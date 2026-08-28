"""Runtime — Scheduling/Isolation 책임만 담당한다(Task의 lifecycle/identity와 분리).

`in-process-async-command` Prototype이 발견한 문제(동일 실제 대상을
Thread에서 동시 실행하면 `monkeypatch` 상태가 섞여 결과가 오염됨,
`docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`
§8/§12)를 세 가지 실행 전략으로 실제 비교한다.

이 모듈은 "무엇이 실행 중인가"를 모른다 — Task 개념을 전혀 참조하지
않는다. 오직 "주어진 대상을 어떤 전략으로 실행할 것인가"만 안다.
Production Runtime API가 아니다 — 세 전략을 비교하기 위한 최소
Dispatcher.
"""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_STRATEGIES = ("sequential", "thread", "process")

_THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="rtb-thread")
_PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=4)


class _ResultCollector:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when != "call":
            return
        if report.outcome == "passed":
            self.passed += 1
        elif report.outcome == "failed":
            self.failed += 1


def _run_pytest(target_path: str) -> tuple[int, int, int]:
    """Thread/Process 양쪽에서 동일하게 호출 가능해야 한다 — Process
    Worker는 별도 인터프리터이므로 REPO_ROOT를 매번 절대경로로
    전달한다(부모 프로세스의 sys.path에 의존하지 않는다)."""

    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    collector = _ResultCollector()
    absolute_target = str(REPO_ROOT / target_path)
    return_code = pytest.main(["-q", "-s", "-p", "no:cacheprovider", absolute_target], plugins=[collector])
    return int(return_code), collector.passed, collector.failed


@dataclass
class OperationStatus:
    status: str  # "RUNNING" | "COMPLETED" | "FAILED"
    elapsed_sec: float
    passed: int = 0
    failed: int = 0
    return_code: int | None = None


@dataclass
class _Execution:
    strategy: str
    started_at: float
    future: "object | None" = None  # sequential은 future 없이 즉시 완료
    cached_status: OperationStatus | None = None


_REGISTRY: dict[str, _Execution] = {}


def start(strategy: str, target_path: str) -> str:
    """실행을 시작하고 execution_id를 반환한다. `sequential`은 호출
    스레드를 블로킹하고 즉시 완료 상태로 등록한다(비동기가 아님 —
    비교 baseline). `thread`/`process`는 각각의 Executor에 제출하고
    즉시 반환한다."""

    if strategy not in _STRATEGIES:
        raise ValueError(f"unknown_strategy: {strategy}")

    execution_id = str(uuid.uuid4())
    started_at = time.monotonic()

    if strategy == "sequential":
        return_code, passed, failed = _run_pytest(target_path)
        status = "COMPLETED" if return_code == 0 else "FAILED"
        result = OperationStatus(
            status=status, elapsed_sec=time.monotonic() - started_at,
            passed=passed, failed=failed, return_code=return_code,
        )
        _REGISTRY[execution_id] = _Execution(strategy=strategy, started_at=started_at, cached_status=result)
        return execution_id

    executor = _THREAD_EXECUTOR if strategy == "thread" else _PROCESS_EXECUTOR
    future = executor.submit(_run_pytest, target_path)
    _REGISTRY[execution_id] = _Execution(strategy=strategy, started_at=started_at, future=future)
    return execution_id


def poll(execution_id: str) -> OperationStatus:
    execution = _REGISTRY.get(execution_id)
    if execution is None:
        raise KeyError(f"unknown_execution_id: {execution_id}")

    if execution.cached_status is not None:
        return execution.cached_status

    elapsed = time.monotonic() - execution.started_at
    if not execution.future.done():
        return OperationStatus(status="RUNNING", elapsed_sec=elapsed)

    return_code, passed, failed = execution.future.result()
    status = "COMPLETED" if return_code == 0 else "FAILED"
    result = OperationStatus(status=status, elapsed_sec=elapsed, passed=passed, failed=failed, return_code=return_code)
    execution.cached_status = result
    return result
