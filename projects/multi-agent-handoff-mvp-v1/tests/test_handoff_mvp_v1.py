"""Phase E — Minimal Multi-Agent 실행 시나리오 검증 (IN-1 ~ IN-6).

목적: `docs/decisions/adc/ADC.md` ADC-02(Runtime 개념의 존폐, Open, NOW)
판단에 필요한 실제 실행 Evidence를 확보한다. 이 테스트는 Runtime을
채택·구현하지 않는다 — 현재 Contract(직접 함수 호출, §16.3 Execution
Host/§16.4 Multi-Task 패턴)만으로 최소 Multi-Agent 시나리오(2개 독립
Agent 역할, Task 전달, 결과 반환, 실패 종료, 병렬 실행)를 재현할 수
있는지만 관찰한다. LangGraph·새 일반화된 Runtime API·Agent Manager·
Scheduler·Registry·Event Bus는 이 디렉터리 어디에도 없다(IN-6이 정적
검증).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import caller  # noqa: E402
from domain.agents import run_drafter, run_reviewer  # noqa: E402

REPO = ROOT.parent.parent


def test_in1_two_independent_agent_roles_exist():
    """IN-1: 최소 2개의 독립적인 Agent 역할이 존재하는가."""
    d = run_drafter("topic-x")
    r = run_reviewer(d)
    assert d["agent"] == "drafter"
    assert r["agent"] == "reviewer"
    assert d["agent"] != r["agent"]


def test_in2_task_handoff_a_to_b_and_result_returns_to_caller():
    """IN-2: Agent A의 결과가 Agent B의 입력으로 전달되고, 최종 결과가
    상위 흐름(caller)으로 반환되는가 — 실제 소비 사례."""
    result = caller.run_sequential_handoff("topic-x")
    assert result["status"] == "ok"
    assert result["draft"] == "draft(topic-x)"
    assert result["review"] == "reviewed(draft(topic-x))"


def test_in3_failure_at_agent_a_short_circuits_and_returns_as_value():
    """IN-3: Agent A 실패 시 Agent B가 호출되지 않고, 실패가 예외가 아닌
    값으로 상위 흐름에 반환되는가."""
    result = caller.run_sequential_handoff("topic-x", fail_drafter=True)
    assert result["status"] == "error"
    assert result["failed_at"] == "drafter"


def test_in4_failure_at_agent_b_propagates_as_value():
    """IN-4: Agent A 성공, Agent B 실패 시 실패가 값으로 전파되는가."""
    result = caller.run_sequential_handoff("topic-x", fail_reviewer=True)
    assert result["status"] == "error"
    assert result["failed_at"] == "reviewer"


def test_in5_independent_parallel_execution_via_stdlib_only():
    """IN-5: 독립적인 Agent 인스턴스 여러 개를 동시 실행할 수 있는가 —
    새 동시성 추상화 없이 표준 라이브러리(`ThreadPoolExecutor`)만으로."""
    results = caller.run_parallel_independent_agents(["a", "b", "c"])
    assert len(results) == 3
    assert {r["draft"] for r in results} == {"draft(a)", "draft(b)", "draft(c)"}
    assert all(r["status"] == "ok" for r in results)


def test_in6_isolation_no_forbidden_dependency():
    """IN-6: 이 실험이 LangGraph·Kernel/HQ production 경로·새 일반화된
    Runtime/Scheduler/Registry/Event Bus/Agent Manager 어휘에 의존하지
    않는가 — 정적 소스 검사."""
    src_files = [
        ROOT / "caller.py",
        ROOT / "domain" / "agents.py",
    ]
    forbidden_import_tokens = [
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
    ]
    for f in src_files:
        text = f.read_text(encoding="utf-8")
        for token in forbidden_import_tokens:
            assert token not in text, f"{f} contains forbidden token: {token}"


def test_in7_no_production_path_modified():
    """IN-7: 이 실험이 Production 경로(core/, hqs/, dashboard/)를 전혀
    건드리지 않았는가 — 이 실험 디렉터리가 그 경로들 밖에 있는지 확인."""
    forbidden_roots = [REPO / "core", REPO / "hqs", REPO / "dashboard"]
    for root in forbidden_roots:
        assert not str(ROOT).startswith(str(root)), f"{ROOT} is inside production path {root}"
