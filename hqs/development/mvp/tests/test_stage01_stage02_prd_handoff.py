"""Stage 01 → Stage 02 PRD Handoff E2E(RFC-0034/ADC-0037/ADR-0022) — Stage 01
Multi-Agent가 만든 `prd`가 Stage 02를 거쳐 재생성 없이 그대로
`SpecificationResult`(`skeleton`/`specification`)로 나오는지, 그리고 그
결과가 `stages/contracts.py`의 두 Contract를 모두 통과하는지 확인한다.
실제 네트워크/Engine 호출 없이 mock으로 전체 흐름을 검증한다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_DIR = Path(__file__).resolve().parents[2] / "stages"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reasoning = _load("reasoning", _STAGE_DIR / "01_context_analysis" / "reasoning.py")
code_analysis = _load("code_analysis", _STAGE_DIR / "01_context_analysis" / "code_analysis.py")
prd_synthesis = _load("prd_synthesis", _STAGE_DIR / "01_context_analysis" / "prd_synthesis.py")
stage_01_multi_agent = _load("stage_01_multi_agent", _STAGE_DIR / "01_context_analysis" / "stage_01_multi_agent.py")
stage_02 = _load("stage_02", _STAGE_DIR / "02_planning_specification" / "stage_02.py")
contracts = _load("contracts", _STAGE_DIR / "contracts.py")

from mvp.github_adapter import RepositoryEntry, RepositoryFile, RepositorySnapshot  # noqa: E402

SAMPLE_ISSUE = {"title": "Add caching", "description": "Cache expensive lookups."}


class _FakeAdapter:
    def __init__(self):
        self._snapshot = RepositorySnapshot(
            owner="o", name="r", ref="main", commit_sha="sha",
            tree=[RepositoryEntry(path="hqs/development/mvp/engine.py", type="blob", size=10, sha="s")],
            files=[],
        )

    def build_snapshot(self, owner, repo, ref, paths_to_fetch):
        return self._snapshot

    def get_file_content(self, owner, repo, path, ref):
        return RepositoryFile(path=path, content="def call_engine(prompt): pass", size=10, sha="s")


def _fake_agent(task_id):
    def _run(issue):
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


def test_stage_01_prd_flows_unchanged_through_stage_02_into_contract_shape(monkeypatch):
    for task_id in reasoning.AGENT_TASK_IDS:
        monkeypatch.setitem(reasoning.AGENT_FUNCTIONS, task_id, _fake_agent(task_id))
    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", lambda issue: "REAL PRD PROSE")

    stage_01_output = stage_01_multi_agent.run_stage_01_multi_agent(SAMPLE_ISSUE, adapter=_FakeAdapter())
    contracts.validate_context_analysis_result(stage_01_output)  # Stage 01 Contract(6-key) 통과

    stage_02_output = stage_02.run_stage_02(SAMPLE_ISSUE, stage_01_output)
    contracts.validate_specification_result(stage_02_output)  # Stage 02 Contract(2-key) 통과

    # 핵심 주장: Stage 02는 Stage 01의 PRD를 재생성하지 않고 그대로 전달한다.
    assert stage_02_output == stage_01_output["prd"]
    assert stage_02_output["specification"] == "REAL PRD PROSE"
