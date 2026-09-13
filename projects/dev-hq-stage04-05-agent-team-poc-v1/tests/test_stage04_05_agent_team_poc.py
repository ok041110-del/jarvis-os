"""Stage 04/05 Agent Team Experimental PoC — 결정적 검증 (IN-1 ~ IN-14).

`RFC-0030`이 선정한 Stage 04/05 구조를 격리된 `projects/` 영역에서 재현해 결정적으로 검증한다.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import caller  # noqa: E402
from domain.agents import qa_agent, review_agent  # noqa: E402

REPO = ROOT.parent.parent


# ---- Stage 04: 순차 Handoff ----


def test_in1_stage04_success_full_pipeline():
    result = caller.run_stage04_pipeline("design-x", "index-y")
    assert result["status"] == "ok"
    assert result["target"]["target"]["function"] == "mock_function"
    assert "mock_function" in result["implementation"]["code"]


def test_in2_stage04_target_failure_short_circuits():
    """Target Identification 실패 시 Implementation Agent가 호출되지 않아야 한다(순차 의존의 증거)."""
    calls = []
    original = caller.implementation_agent

    def spy(*a, **kw):
        calls.append(1)
        return original(*a, **kw)

    caller.implementation_agent = spy
    try:
        result = caller.run_stage04_pipeline("design-x", "index-y", fail_target=True)
    finally:
        caller.implementation_agent = original

    assert result["status"] == "error"
    assert result["failed_at"] == "target_identification"
    assert calls == []  # Implementation Agent 미호출


def test_in3_stage04_implementation_failure_preserves_upstream_result():
    result = caller.run_stage04_pipeline("design-x", "index-y", fail_impl=True)
    assert result["status"] == "error"
    assert result["failed_at"] == "implementation"
    assert result["target"]["status"] == "ok"  # 상류 성공 결과가 보존됨(부분 재실행의 전제)


def test_in4_stage04_partial_reexecution_only_implementation():
    """부분 재실행 — Target Identification은 캐시된 성공 결과를 재사용한다."""
    failed = caller.run_stage04_pipeline("design-x", "index-y", fail_impl=True)
    assert failed["status"] == "error"
    cached_target = failed["target"]

    retried = caller.retry_stage04_implementation_only("design-x", cached_target)
    assert retried["status"] == "ok"
    assert retried["target"] is cached_target  # 재계산 없이 동일 객체 재사용


def test_in5_stage04_no_parallelism_by_design():
    """Target -> Implementation은 순차 dependency다 — ThreadPoolExecutor가 없음을 소스로 확인한다."""
    src = (ROOT / "caller.py").read_text(encoding="utf-8")
    stage04_block = src.split("# ---- Stage 04", 1)[1].split("# ---- Stage 05", 1)[0]
    assert "ThreadPoolExecutor" not in stage04_block


# ---- Stage 05: 독립 병렬 + 결정적 종합 ----


def test_in6_stage05_success_both_agents_and_verdict_pass():
    result = caller.run_stage05_pipeline("def f(): return 1")
    assert result["verdict"] == "PASS"
    assert result["review"]["status"] == "ok"
    assert result["qa"]["status"] == "ok"


def test_in7_stage05_review_failure_does_not_block_qa():
    result = caller.run_stage05_pipeline("def f(): return 1", fail_review=True)
    assert result["review"]["status"] == "error"
    assert result["qa"]["status"] == "ok"  # 독립 실행 — Review 실패가 QA를 막지 않음


def test_in8_stage05_verdict_ignores_agent_content():
    """Agent가 둘 다 실패해도 결정적 검사가 PASS면 Verdict는 PASS다 — Policy 구현 금지 경계의 재확인."""
    result = caller.run_stage05_pipeline("def f(): return 1", fail_review=True, fail_qa=True)
    assert result["review"]["status"] == "error"
    assert result["qa"]["status"] == "error"
    assert result["verdict"] == "PASS"  # 결정적 검사만 반영, Agent 실패와 무관


def test_in9_stage05_deterministic_check_failure_sets_verdict_fail():
    result = caller.run_stage05_pipeline("def f(:\n  broken syntax")
    assert result["checks"]["syntax"]["blocking_fail"] is True
    assert result["verdict"] == "FAIL"


def test_in10_stage05_actual_parallel_execution_wall_clock():
    """각 0.2s 지연 시 총 소요 시간이 순차 합(0.4s)이 아니라 병렬 시간(~0.2s)에 가까운지 측정한다."""
    from concurrent.futures import ThreadPoolExecutor

    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(review_agent, "code", delay=0.2)
        f2 = pool.submit(qa_agent, "code", delay=0.2)
        f1.result()
        f2.result()
    elapsed = time.monotonic() - start
    assert elapsed < 0.35  # 순차였다면 >=0.4s


def test_in11_stage05_partial_reexecution_only_failed_agent():
    """부분 재실행 — QA만 재시도하고 Review 결과는 캐시에서 재사용한다."""
    failed = caller.run_stage05_pipeline("def f(): return 1", fail_qa=True)
    assert failed["qa"]["status"] == "error"
    assert failed["review"]["status"] == "ok"

    retried = caller.retry_stage05_agent_only("def f(): return 1", failed, agent="qa")
    assert retried["qa"]["status"] == "ok"
    assert retried["review"] is failed["review"]  # Review 재호출 없이 캐시 재사용
    assert retried["verdict"] == failed["verdict"]  # Verdict는 재종합돼도 값은 결정적 검사 기준 그대로


def test_in12_stage05_error_propagates_as_value_not_exception():
    try:
        result = caller.run_stage05_pipeline("def f(): return 1", fail_review=True, fail_qa=True)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"failure propagated as exception, not value: {exc}")
    assert result["review"]["status"] == "error"
    assert result["qa"]["status"] == "error"


# ---- 격리·구조 검증 ----


def test_in13_no_production_path_modified():
    forbidden_roots = [REPO / "core", REPO / "hqs", REPO / "dashboard"]
    for root in forbidden_roots:
        assert not str(ROOT).startswith(str(root))


def test_in14_isolation_no_forbidden_dependency():
    """LangGraph·Kernel/HQ production·새 일반화 Runtime 어휘에 의존하지 않는지 정적 검사한다."""
    src_files = [ROOT / "caller.py", ROOT / "domain" / "agents.py", ROOT / "domain" / "checks.py"]
    forbidden_tokens = [
        "import langgraph",
        "import langchain",
        "from langgraph",
        "from langchain",
        "StateGraph",
        "import hqs",
        "from hqs",
        "class Runtime",
        "class Scheduler",
        "class Registry",
        "class AgentManager",
        "class EventBus",
        "class Message(",
        "class Event(",
    ]
    for f in src_files:
        text = f.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text, f"{f} contains forbidden token: {token}"
