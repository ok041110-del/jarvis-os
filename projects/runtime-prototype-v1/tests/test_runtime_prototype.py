"""Runtime Prototype 시나리오 — Caller → Runtime → Execution Host →
Engine(작업 지시 "비교 실험" Runtime Prototype 경로).

`test_baseline_direct_execution_host.py`와 동일한 실제 Engine 실행
대상(`rp_target.run_pytest_target`, 실제 HQ pytest 스위트)을 사용해
직접 비교 가능하게 한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import rp_runtime as runtime  # noqa: E402
import rp_target as target  # noqa: E402

STOCK_TARGET = "hqs/investment/tests/test_stock_team_integration.py"
ETF_TARGET = "hqs/investment/tests/test_etf_team_integration.py"
DIVIDEND_TARGET = "hqs/investment/tests/test_dividend_stock_team_integration.py"


def test_single_execution_unit_lifecycle():
    """생성 → 실행 요청 → 상태 조회 → 결과 수집 → 정리, 5개 책임
    전부를 단일 Execution Unit으로 확인한다(Prototype 범위 1~5)."""
    rt = runtime.Runtime()
    try:
        unit_id = rt.create_unit(target.run_pytest_target, STOCK_TARGET)
        assert rt.status(unit_id) == runtime.STATUS_PENDING

        rt.start(unit_id)
        assert rt.status(unit_id) in (runtime.STATUS_RUNNING, runtime.STATUS_DONE)

        result = rt.result(unit_id)
        assert result == (0, 2, 0)
        assert rt.status(unit_id) == runtime.STATUS_DONE

        rt.cleanup(unit_id)
        with pytest.raises(runtime.UnknownExecutionUnitError):
            rt.status(unit_id)
    finally:
        rt.shutdown()


def _boom() -> None:
    raise ValueError("boom")


def test_execution_unit_failure_is_observable():
    """실패하는 Execution Unit은 상태가 FAILED로 관찰되고, result()가
    예외를 발생시킨다(Q1: lifecycle 명확성 비교 대상) — Execution
    Host의 예외 전파(`run_isolated`가 예외를 그대로 raise) 계약을
    Runtime이 상태값으로도 관찰 가능하게 만든다는 차이를 보여준다."""
    rt = runtime.Runtime()
    try:
        unit_id = rt.create_unit(_boom)
        rt.start(unit_id)
        with pytest.raises(RuntimeError):
            rt.result(unit_id)
        assert rt.status(unit_id) == runtime.STATUS_FAILED
    finally:
        rt.shutdown()


def test_double_start_is_rejected():
    """같은 Execution Unit을 두 번 start()하면 명시적으로 거부된다 —
    Baseline(raw Future)에는 이런 identity 보호가 없다(Q1)."""
    rt = runtime.Runtime()
    try:
        unit_id = rt.create_unit(target.run_pytest_target, STOCK_TARGET)
        rt.start(unit_id)
        with pytest.raises(ValueError):
            rt.start(unit_id)
        rt.result(unit_id)
    finally:
        rt.shutdown()


def test_multi_execution_unit_lifecycle_reused_across_units():
    """복수 Execution Unit: `create_unit`/`start`/`result` 세 호출만
    반복하면 된다 — Baseline의
    `test_multi_execution_unit_requires_caller_written_concurrency`가
    매번 직접 작성해야 했던 `ThreadPoolExecutor` 조합을 Runtime이
    대신 제공한다(Q3 재사용성 비교 대상)."""
    rt = runtime.Runtime()
    try:
        targets = [STOCK_TARGET, ETF_TARGET, DIVIDEND_TARGET]
        unit_ids = [rt.create_unit(target.run_pytest_target, t) for t in targets]
        for unit_id in unit_ids:
            rt.start(unit_id)

        results = [rt.result(unit_id) for unit_id in unit_ids]
        assert results == [(0, 2, 0), (0, 1, 0), (0, 1, 0)]
        assert all(rt.status(unit_id) == runtime.STATUS_DONE for unit_id in unit_ids)
    finally:
        rt.shutdown()


def test_status_query_without_blocking():
    """Runtime은 결과를 기다리지 않고도 상태를 조회할 수 있다 —
    `status()`는 `result()`와 달리 블로킹하지 않는다(Q1: Baseline은
    이 조회 지점 자체가 없음)."""
    rt = runtime.Runtime()
    try:
        unit_id = rt.create_unit(target.run_pytest_target, STOCK_TARGET)
        rt.start(unit_id)
        # status()는 즉시 반환 — PENDING/RUNNING/DONE/FAILED 중 하나
        immediate_status = rt.status(unit_id)
        assert immediate_status in (
            runtime.STATUS_PENDING,
            runtime.STATUS_RUNNING,
            runtime.STATUS_DONE,
        )
        rt.result(unit_id)  # 최종 완료까지 대기
        assert rt.status(unit_id) == runtime.STATUS_DONE
    finally:
        rt.shutdown()
