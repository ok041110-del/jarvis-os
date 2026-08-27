"""In-process Long-running Operation — 실제 Architecture와 연결된 작업.

sleep()으로 가짜 지연을 만들지 않는다(작업 지시 §4). subprocess가 아니라
`concurrent.futures.ThreadPoolExecutor`로 프로세스 내부에서 실제 pytest
세션을 실행한다 — 이 방식은 이미 저장소에 존재하는 패턴이다
(`projects/dev-hq-timeout-recovery-prototype/parallel/parallel_runner.py`가
동일한 ThreadPoolExecutor 방식으로 실제 Engine 호출을 병렬 실행한다).
이 Prototype은 그 패턴을 중복 구현하지 않고, "실행 상태를 어디에
보관하는가"라는 다른 질문에 적용한다.

`hqs/development/mvp/tests/test_mvp_0001.py`는 실측 약 69초가 걸리는
실제 MVP 워크플로 테스트다(2026-08-27 측정, 3 passed in 68.84s) —
Dev HQ가 이미 스스로의 Freeze 근거로 인용하는 바로 그 Validation
작업이며, sleep()이 아닌 진짜 장시간 작업이다.

REPO_ROOT/hqs/*를 직접 import하지 않는다 — pytest.main()으로만
호출한다(HQ Business Logic을 이 Prototype이 소유하지 않는다).
"""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_HQ_TEST_PATHS = {
    "development": "hqs/development/mvp/tests/test_mvp_0001.py",
    "investment": "hqs/investment/tests",
}

# 모듈 전역 Executor — 여러 Operation이 동시에(concurrently) 실행될 수
# 있어야 §14 Concurrent Execution 검증이 가능하다.
_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="inprocess-op")


class _ResultCollector:
    """pytest hook으로 결과를 직접 수집한다 — stdout/fd capture를 쓰지
    않는다. 두 pytest.main() 세션이 동시에 실행될 때 `capsys`/`capfd`의
    OS-level fd 리다이렉션(dup2)은 프로세스 전역 자원이라 충돌 위험이
    있기 때문이다(`-s`로 capture 자체를 끈다). Report Hook 수집은 이
    충돌을 피한다."""

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


@dataclass
class OperationStatus:
    status: str  # "RUNNING" | "COMPLETED" | "FAILED"
    elapsed_sec: float
    passed: int = 0
    failed: int = 0
    return_code: int | None = None


@dataclass
class _Execution:
    future: "object"  # concurrent.futures.Future
    started_at: float
    hq: str
    target_path: str
    cached_status: OperationStatus | None = None


_REGISTRY: dict[str, _Execution] = {}


def _run_pytest_inprocess(target_path: str) -> tuple[int, int, int]:
    collector = _ResultCollector()
    absolute_target = str(REPO_ROOT / target_path)
    return_code = pytest.main(["-q", "-s", "-p", "no:cacheprovider", absolute_target], plugins=[collector])
    return int(return_code), collector.passed, collector.failed


def start_operation(hq: str, valid_path: bool = True) -> str:
    """실제 pytest 세션을 Worker Thread에서 시작하고 즉시 반환한다(비동기).

    subprocess와의 결정적 차이: `future.cancel()`은 아직 시작되지 않은
    작업만 취소할 수 있다 — 이미 실행 중인 Thread는 강제 종료할 수 없다
    (Python 표준 threading에 안전한 kill이 없다). `async-command`
    Prototype의 `operation.terminate()`에 대응하는 기능이 in-process
    실행에는 존재하지 않는다 — 이 자체가 §9 Runtime 평가에 대한
    Evidence다."""

    if hq not in _HQ_TEST_PATHS:
        raise ValueError(f"unknown_hq: {hq}")

    target_path = _HQ_TEST_PATHS[hq] if valid_path else f"{_HQ_TEST_PATHS[hq]}_does_not_exist"
    execution_id = str(uuid.uuid4())

    future = _EXECUTOR.submit(_run_pytest_inprocess, target_path)
    _REGISTRY[execution_id] = _Execution(future=future, started_at=time.monotonic(), hq=hq, target_path=target_path)
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
