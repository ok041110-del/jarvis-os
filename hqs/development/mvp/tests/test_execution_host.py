"""Execution Host(Production, `execution_host.py`) 최소 검증.

`ADC-0015` Conditional Accept 범위(Process 1차, "동일 Target 동시
실행" 조건에서 Thread 배제)를 Production 모듈에서 재확인한다 —
새 실험이 아니라 `runtime-boundary`/`process-runtime-strategy`
Experimental Prototype이 이미 검증한 방법론을 Production 모듈
대상으로 재사용한다.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from ..execution_host import run_isolated
from ._pytest_target import run_pytest_target

# `hqs/investment/tests/test_stock_team_integration.py`: 2 tests,
# `monkeypatch.setattr(stock_team, "call_engine", ...)` 사용 —
# `runtime-boundary`/`process-runtime-strategy` Prototype이 동일
# Target 오염 재현에 쓴 것과 같은 최소 대상.
CONTAMINATION_TARGET = "hqs/investment/tests/test_stock_team_integration.py"


def _add(a: int, b: int) -> int:
    return a + b


def _boom() -> None:
    raise ValueError("boom")


def test_run_isolated_returns_correct_result():
    assert run_isolated(_add, 2, 3) == 5


def test_run_isolated_propagates_exceptions():
    with pytest.raises(ValueError):
        run_isolated(_boom)


def test_run_isolated_executes_real_pytest_target():
    return_code, passed, failed = run_isolated(run_pytest_target, CONTAMINATION_TARGET)
    assert return_code == 0
    assert (passed, failed) == (2, 0)


def test_run_isolated_is_accurate_on_identical_target_concurrent_execution():
    """동일 Target을 두 호출자가 동시에 요청해도(Process 격리로)
    결과가 오염되지 않는다 — `runtime-boundary` §4, `process-runtime-
    strategy` §4가 반복 관찰한 조건을 Production 모듈로 재현."""

    def _call():
        return run_isolated(run_pytest_target, CONTAMINATION_TARGET)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_call) for _ in range(2)]
        results = [f.result() for f in futures]

    for return_code, passed, failed in results:
        assert return_code == 0
        assert (passed, failed) == (2, 0)
