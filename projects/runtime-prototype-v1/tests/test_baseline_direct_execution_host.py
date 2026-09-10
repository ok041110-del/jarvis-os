"""Baseline 시나리오 — Runtime 계층 없이 Caller가 Execution Host를
직접 호출한다(작업 지시 "비교 실험" Baseline: Caller → Execution
Host → Engine).

이 파일이 Q1~Q4 비교의 기준선이다. Runtime Prototype 쪽
(`test_runtime_prototype.py`)과 동일한 실제 Engine 실행 대상
(`rp_target.run_pytest_target`)을 사용한다.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import rp_execution_host as execution_host  # noqa: E402
import rp_target as target  # noqa: E402

STOCK_TARGET = "hqs/investment/tests/test_stock_team_integration.py"
ETF_TARGET = "hqs/investment/tests/test_etf_team_integration.py"
DIVIDEND_TARGET = "hqs/investment/tests/test_dividend_stock_team_integration.py"


def test_single_execution_unit_direct_call():
    """단일 실행: Caller가 Execution Host를 직접 블로킹 호출한다 —
    Runtime 계층 없이도 단일 Execution Unit은 이미 충분하다(Q5의
    baseline)."""
    return_code, passed, failed = execution_host.run_isolated(
        target.run_pytest_target, STOCK_TARGET
    )
    assert (return_code, passed, failed) == (0, 2, 0)


def test_multi_execution_unit_requires_caller_written_concurrency():
    """복수 실행: Runtime이 없으면 Caller가 직접 동시성 코드를
    작성해야 한다 — 이것이 Q3(재사용성)·Q4(확장성) 비교의 핵심
    관찰 지점이다. Execution Host 자체는 lifecycle을 추적하지
    않으므로(PENDING/RUNNING 상태 없음), Caller가 List[Future] +
    수동 결과 취합을 직접 만든다."""
    targets = [STOCK_TARGET, ETF_TARGET, DIVIDEND_TARGET]

    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=len(targets)) as pool:
        futures = [
            pool.submit(execution_host.run_isolated, target.run_pytest_target, t)
            for t in targets
        ]
        results = [f.result() for f in futures]
    elapsed = time.monotonic() - start

    assert results == [(0, 2, 0), (0, 1, 0), (0, 1, 0)]
    # Runtime 없이도 동시 실행 자체는 가능하다 — Caller가 매번 이
    # ThreadPoolExecutor 조합을 직접 작성해야 한다는 것이 관찰 대상.
    assert elapsed < 30


def test_baseline_has_no_lifecycle_query_api():
    """Baseline에는 "지금 몇 번이 끝났는가"를 물어볼 API가 없다 —
    Caller가 Future 리스트를 직접 들고 `future.done()`을 스스로
    확인해야 한다(Q1 비교 대상)."""
    targets = [STOCK_TARGET, ETF_TARGET]
    with ThreadPoolExecutor(max_workers=2) as pool:
        # Execution Host/Baseline 어디에도 "status(unit_id)" 같은 조회
        # API가 없다 — Caller가 raw `Future`를 직접 들고 `.done()`을
        # 호출해야 상태를 알 수 있다(Q1 비교: Runtime 쪽은 `status()`
        # 문자열 API를 제공).
        futures = [
            pool.submit(execution_host.run_isolated, target.run_pytest_target, t)
            for t in targets
        ]
        assert all(hasattr(f, "done") for f in futures)  # Future API 그대로 노출됨
        results = [f.result() for f in futures]

    assert results == [(0, 2, 0), (0, 1, 0)]
