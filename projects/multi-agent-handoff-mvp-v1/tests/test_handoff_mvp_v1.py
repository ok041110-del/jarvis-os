"""Phase E — Minimal Multi-Agent 실행 시나리오 검증 (IN-1 ~ IN-7).

ADC-02(Runtime 개념의 존폐) 판단에 필요한 실행 Evidence 확보용 — 현재 Contract(직접 함수 호출)만으로 최소 Multi-Agent 시나리오가 재현되는지만 관찰하며, Runtime을 채택·구현하지 않는다."""
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
    d = run_drafter("topic-x")
    r = run_reviewer(d)
    assert d["agent"] == "drafter"
    assert r["agent"] == "reviewer"
    assert d["agent"] != r["agent"]


def test_in2_task_handoff_a_to_b_and_result_returns_to_caller():
    result = caller.run_sequential_handoff("topic-x")
    assert result["status"] == "ok"
    assert result["draft"] == "draft(topic-x)"
    assert result["review"] == "reviewed(draft(topic-x))"


def test_in3_failure_at_agent_a_short_circuits_and_returns_as_value():
    result = caller.run_sequential_handoff("topic-x", fail_drafter=True)
    assert result["status"] == "error"
    assert result["failed_at"] == "drafter"


def test_in4_failure_at_agent_b_propagates_as_value():
    result = caller.run_sequential_handoff("topic-x", fail_reviewer=True)
    assert result["status"] == "error"
    assert result["failed_at"] == "reviewer"


def test_in5_independent_parallel_execution_via_stdlib_only():
    results = caller.run_parallel_independent_agents(["a", "b", "c"])
    assert len(results) == 3
    assert {r["draft"] for r in results} == {"draft(a)", "draft(b)", "draft(c)"}
    assert all(r["status"] == "ok" for r in results)


def test_in6_isolation_no_forbidden_dependency():
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
    forbidden_roots = [REPO / "core", REPO / "hqs", REPO / "dashboard"]
    for root in forbidden_roots:
        assert not str(ROOT).startswith(str(root)), f"{ROOT} is inside production path {root}"
