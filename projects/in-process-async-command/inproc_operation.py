"""In-process Long-running Operation — 실제 Architecture와 연결된 작업.

sleep()으로 가짜 지연을 만들지 않는다 — subprocess 대신 ThreadPoolExecutor로 프로세스 내부에서 실제 pytest 세션을 실행한다.
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
    """pytest hook으로 결과를 직접 수집한다 — capsys/capfd의 OS-level fd 리다이렉션은 두 세션 동시 실행 시 충돌하므로 쓰지 않는다."""

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

    subprocess와 달리 future.cancel()은 시작 전 작업만 취소 가능하다 — 이미 실행 중인 Thread는 강제 종료할 수 없다(operation.terminate() 대응 기능 없음).
    """

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
