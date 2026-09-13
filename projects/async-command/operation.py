"""Long-running Operation — 실제 Architecture와 연결된 작업.

sleep()으로 가짜 지연을 만들지 않는다 — 실제 저장소 테스트 스위트를 subprocess로 실행한다(Dev HQ 기준 실측 69.99초, 2026-08-26, 120 passed).
"""

from __future__ import annotations

import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_HQ_TEST_PATHS = {
    "development": "hqs/development/mvp/tests",
    "investment": "hqs/investment/tests",
}


@dataclass
class _Execution:
    process: subprocess.Popen
    started_at: float
    hq: str
    target_path: str
    cached_status: "OperationStatus | None" = None


# In-memory Registry — Prototype 범위(영속화하지 않음, 프로세스 종료 시 소실).
_REGISTRY: dict[str, _Execution] = {}


def start_operation(hq: str, valid_path: bool = True) -> str:
    if hq not in _HQ_TEST_PATHS:
        raise ValueError(f"unknown_hq: {hq}")

    target_path = _HQ_TEST_PATHS[hq] if valid_path else f"{_HQ_TEST_PATHS[hq]}/test_does_not_exist.py"
    execution_id = str(uuid.uuid4())

    process = subprocess.Popen(
        [sys.executable, "-m", "pytest", target_path, "-q"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    _REGISTRY[execution_id] = _Execution(process=process, started_at=time.monotonic(), hq=hq, target_path=target_path)
    return execution_id


@dataclass
class OperationStatus:
    status: str  # "RUNNING" | "COMPLETED" | "FAILED"
    elapsed_sec: float
    output_tail: str = ""
    return_code: int | None = None


def poll(execution_id: str) -> OperationStatus:
    """`stdout.read()`는 스트림을 소모하므로, 완료 시점 결과를 `cached_status`에 캐싱해 재조회 시 빈 문자열이 반환되는 문제를 막는다."""

    execution = _REGISTRY.get(execution_id)
    if execution is None:
        raise KeyError(f"unknown_execution_id: {execution_id}")

    if execution.cached_status is not None:
        return execution.cached_status

    elapsed = time.monotonic() - execution.started_at
    return_code = execution.process.poll()

    if return_code is None:
        return OperationStatus(status="RUNNING", elapsed_sec=elapsed)

    output = execution.process.stdout.read() if execution.process.stdout else ""
    tail = "\n".join(output.strip().splitlines()[-5:])
    status = "COMPLETED" if return_code == 0 else "FAILED"
    result = OperationStatus(status=status, elapsed_sec=elapsed, output_tail=tail, return_code=return_code)
    execution.cached_status = result
    return result


def wait(execution_id: str, timeout: float | None = None) -> OperationStatus:
    """테스트/데모 편의용 — Prototype 자체 흐름(Q1~Q6)은 poll()만 쓴다."""

    execution = _REGISTRY[execution_id]
    execution.process.wait(timeout=timeout)
    return poll(execution_id)


def terminate(execution_id: str) -> None:
    """테스트 정리용 — RUNNING 확인만 필요한 테스트에서 완료까지 대기하는 낭비를 피한다. Production 취소 기능이 아니다."""

    execution = _REGISTRY.get(execution_id)
    if execution and execution.process.poll() is None:
        execution.process.terminate()
