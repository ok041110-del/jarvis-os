"""Stage 01 Multi-Agent 진입점 E2E 검증(`stages/01_context_analysis/
stage_01_multi_agent.py`) — mock 기반: Request -> Multi-Agent Reasoning ->
Aggregation -> GitHub Snapshot -> Parallel Code Analysis -> Context
Aggregation -> Stage 01 Output 전체 흐름과, LLM Reasoning/Code Analysis가
병렬화되지 않고 순차(Reasoning 전체 완료 후 Code Analysis 시작)로 실행되는지
확인한다. 실제 네트워크/Engine 호출은 하지 않는다."""

import importlib.util
import sys
import time
from pathlib import Path

_STAGE_DIR = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, _STAGE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reasoning = _load("reasoning", "reasoning.py")
code_analysis = _load("code_analysis", "code_analysis.py")
prd_synthesis = _load("prd_synthesis", "prd_synthesis.py")
stage_01_multi_agent = _load("stage_01_multi_agent", "stage_01_multi_agent.py")

from mvp.github_adapter import RepositoryEntry, RepositoryFile, RepositorySnapshot  # noqa: E402

SAMPLE_ISSUE = {"title": "Add caching", "description": "Cache expensive lookups."}


def _patch_prd_synthesis_engine_call(monkeypatch, response="PRD SPEC TEXT"):
    """PRD Synthesis도 Engine을 1회 호출하므로(RFC-0034), 실제 네트워크
    호출 없이 검증하려면 이 함수도 별도로 mock해야 한다."""
    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", lambda issue: response)


class _FakeAdapter:
    def __init__(self, event_log):
        self._event_log = event_log
        self._snapshot = RepositorySnapshot(
            owner="o", name="r", ref="main", commit_sha="sha",
            tree=[RepositoryEntry(path="hqs/development/mvp/engine.py", type="blob", size=10, sha="s")],
            files=[],
        )

    def build_snapshot(self, owner, repo, ref, paths_to_fetch):
        self._event_log.append(("snapshot", time.monotonic()))
        return self._snapshot

    def get_file_content(self, owner, repo, path, ref):
        return RepositoryFile(path=path, content="def call_engine(prompt): pass", size=10, sha="s")


def _fake_agent(task_id, event_log, delay=0.05):
    def _run(issue):
        event_log.append((f"agent:{task_id}:start", time.monotonic()))
        time.sleep(delay)
        event_log.append((f"agent:{task_id}:end", time.monotonic()))
        return {
            "intent": {"action": "add", "target": "cache", "domain": "perf", "explicit_intent": "x", "confidence": 0.9},
            "goal": {"desired_outcome": "x", "success_direction": "x", "underlying_goal": "x", "confidence": 0.9},
            "requirement": {
                "functional_requirements": [], "non_functional_requirements": [],
                "constraints": [], "scope_candidates": [], "confidence": 0.9,
            },
            "ambiguity": {
                "ambiguous_points": [], "missing_information": [], "conflicting_interpretations": [],
                "unresolved_questions": [], "confidence": 0.9,
            },
        }[task_id]
    return _run


def _patch_agents(monkeypatch, event_log, delay=0.05):
    """`stage_01_multi_agent._run_reasoning_phase()`는 `reasoning.AGENT_FUNCTIONS`
    dict를 순회해 호출하므로, 그 dict의 값 자체를 교체해야 실제로 반영된다."""
    for task_id in reasoning.AGENT_TASK_IDS:
        monkeypatch.setitem(reasoning.AGENT_FUNCTIONS, task_id, _fake_agent(task_id, event_log, delay))


def test_full_flow_returns_existing_stage_01_contract_shape(monkeypatch):
    event_log = []
    _patch_agents(monkeypatch, event_log, delay=0.01)
    _patch_prd_synthesis_engine_call(monkeypatch)
    adapter = _FakeAdapter(event_log)

    result = stage_01_multi_agent.run_stage_01_multi_agent(SAMPLE_ISSUE, adapter=adapter)

    assert set(result.keys()) == {
        "directory_structure", "context_bundle", "candidate_index", "target", "dependency_closure", "prd",
    }
    assert result["target"] is None
    assert result["dependency_closure"] is None
    assert "hqs/development/mvp/engine.py" in result["directory_structure"]
    assert result["prd"]["specification"] == "PRD SPEC TEXT"
    assert set(result["prd"]["skeleton"].keys()) == {
        "problem_definition", "constraints", "risks", "scope_candidates",
    }


def test_reasoning_fully_completes_before_code_analysis_starts(monkeypatch):
    """LLM Reasoning과 Code Analysis를 병렬화하지 않는다는 요구사항(§ 중요)을
    검증한다 — 4개 Agent가 전부 끝난 시각이 GitHub Snapshot 생성 시작 시각보다
    앞서야 한다."""
    event_log = []
    _patch_agents(monkeypatch, event_log, delay=0.05)
    _patch_prd_synthesis_engine_call(monkeypatch)
    adapter = _FakeAdapter(event_log)

    stage_01_multi_agent.run_stage_01_multi_agent(SAMPLE_ISSUE, adapter=adapter)

    agent_end_times = [t for name, t in event_log if name.endswith(":end")]
    snapshot_time = next(t for name, t in event_log if name == "snapshot")

    assert max(agent_end_times) <= snapshot_time


def test_target_given_computes_dependency_closure_conditionally(monkeypatch):
    event_log = []
    _patch_agents(monkeypatch, event_log, delay=0.0)
    _patch_prd_synthesis_engine_call(monkeypatch)
    adapter = _FakeAdapter(event_log)

    result = stage_01_multi_agent.run_stage_01_multi_agent(
        SAMPLE_ISSUE, target=("agents.backend", "_strip_code_fence"), adapter=adapter,
    )

    assert result["target"] == ("agents.backend", "_strip_code_fence")
    assert "def _strip_code_fence(text: str) -> str:" in result["dependency_closure"]


def test_all_agents_timeout_still_produces_output_not_a_crash(monkeypatch):
    """Partial/전체 Reasoning 실패라도 Runner가 실행을 죽이지 않고 Aggregator가
    INSUFFICIENT로 판단해 흐름을 계속 진행한다(§5 Partial Failure)."""
    def timeout_forever(issue):
        time.sleep(0.3)  # timeout(0.05s)보다 길지만 테스트를 느리게 만들지 않을 만큼 짧게

    for task_id in reasoning.AGENT_TASK_IDS:
        monkeypatch.setitem(reasoning.AGENT_FUNCTIONS, task_id, timeout_forever)

    event_log = []
    adapter = _FakeAdapter(event_log)
    _patch_prd_synthesis_engine_call(monkeypatch)
    monkeypatch.setattr(stage_01_multi_agent, "_AGENT_TIMEOUT_SECONDS", 0.05)

    result = stage_01_multi_agent.run_stage_01_multi_agent(SAMPLE_ISSUE, adapter=adapter)

    # Reasoning이 전부 INSUFFICIENT여도 Code Analysis/PRD Synthesis는 계속
    # 진행되어 기존 Contract 6-key(`prd` 포함)를 채운 dict를 반환한다
    # (크래시하지 않음).
    assert set(result.keys()) == {
        "directory_structure", "context_bundle", "candidate_index", "target", "dependency_closure", "prd",
    }
