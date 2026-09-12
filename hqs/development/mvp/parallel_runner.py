"""ParallelRunner — 재사용 가능한 내부 병렬 실행 인프라(Stage 01 전용 코드가
아니다, RFC-0033/ADC-0036 §Out of Scope). 책임은 task scheduling·concurrent
실행·timeout·retry·결과 정규화·batch 결과 수집으로 한정한다. Agent 선택,
Repository 판단, LLM 선택, GitHub API, semantic correctness, conflict
resolution, workflow semantics는 이 모듈이 판단하지 않는다 — 호출자(Reasoning
Aggregator/Context Aggregator)의 책임이다."""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    INVALID_OUTPUT = "INVALID_OUTPUT"


@dataclass
class RetryPolicy:
    """`retry_on`에 해당하는 예외만 재시도한다 — 일시적 API/network 오류
    한정(§5). 무조건적인 반복 retry는 하지 않는다(`max_attempts` 상한)."""

    max_attempts: int = 1
    retry_on: tuple = (Exception,)


@dataclass
class ParallelTask:
    task_id: str
    executor: Callable[[Any], Any]
    input: Any = None
    timeout: Optional[float] = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    # 스키마 검증 실패처럼 재시도 대상이 아닌 예외 — 즉시 INVALID_OUTPUT.
    invalid_output_errors: tuple = ()


@dataclass
class ParallelTaskResult:
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    attempts: int = 0


@dataclass
class ParallelBatchResult:
    results: list
    started_at: float
    completed_at: float
    total_duration: float
    summary: dict

    def by_id(self, task_id: str) -> Optional[ParallelTaskResult]:
        return next((r for r in self.results if r.task_id == task_id), None)


def _run_single(task: ParallelTask) -> ParallelTaskResult:
    start = time.monotonic()
    max_attempts = max(1, task.retry_policy.max_attempts)
    attempts = 0
    last_error: Optional[BaseException] = None

    while attempts < max_attempts:
        attempts += 1
        try:
            output = task.executor(task.input)
        except task.invalid_output_errors as exc:
            return ParallelTaskResult(
                task_id=task.task_id, status=TaskStatus.INVALID_OUTPUT,
                error=str(exc), duration=time.monotonic() - start, attempts=attempts,
            )
        except Exception as exc:  # noqa: BLE001 — 재시도 여부는 retry_on이 결정
            last_error = exc
            if isinstance(exc, task.retry_policy.retry_on) and attempts < max_attempts:
                continue
            return ParallelTaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED,
                error=str(exc), duration=time.monotonic() - start, attempts=attempts,
            )
        return ParallelTaskResult(
            task_id=task.task_id, status=TaskStatus.SUCCESS,
            output=output, duration=time.monotonic() - start, attempts=attempts,
        )

    return ParallelTaskResult(
        task_id=task.task_id, status=TaskStatus.FAILED,
        error=str(last_error), duration=time.monotonic() - start, attempts=attempts,
    )


class ParallelRunner:
    """`tasks`를 동시에 실행하고 `ParallelBatchResult`로 결과를 모은다.
    Task 하나의 실패/timeout이 다른 Task 실행을 막지 않는다(concurrent task
    isolation) — 최종 진행 가능 여부 판단은 이 클래스가 아니라 호출자
    (Aggregator)의 책임이다(Partial Failure 원칙)."""

    def __init__(self, max_workers: int = 8):
        self._max_workers = max_workers

    def run(self, tasks: list) -> ParallelBatchResult:
        # `with ThreadPoolExecutor(...)`는 종료 시 `shutdown(wait=True)`를
        # 호출해 모든 스레드가 끝날 때까지 블로킹한다 — timeout이 걸린 Task의
        # 스레드가 계속 실행 중이면 그 Task의 timeout이 사실상 무의미해진다
        # (Python 스레드는 강제 종료가 불가능하므로 `wait=False`로 반환하고
        # 지연된 스레드는 백그라운드에서 자연 종료되게 둔다).
        started_at = time.time()
        results = []
        pool = ThreadPoolExecutor(max_workers=self._max_workers)
        try:
            future_to_task = {pool.submit(_run_single, task): task for task in tasks}
            for future, task in future_to_task.items():
                try:
                    result = future.result(timeout=task.timeout)
                except FutureTimeoutError:
                    result = ParallelTaskResult(
                        task_id=task.task_id, status=TaskStatus.TIMEOUT,
                        error=f"timed out after {task.timeout}s",
                        duration=task.timeout or 0.0, attempts=0,
                    )
                results.append(result)
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        completed_at = time.time()
        summary = {status.value: 0 for status in TaskStatus}
        for result in results:
            summary[result.status.value] += 1
        return ParallelBatchResult(
            results=results, started_at=started_at, completed_at=completed_at,
            total_duration=completed_at - started_at, summary=summary,
        )
