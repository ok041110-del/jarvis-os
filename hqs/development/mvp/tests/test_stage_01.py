"""Stage 01(Context Analysis) `run_stage_01()` 검증 (ADR-0008,
`stages/01_context_analysis/VALIDATION.md`).

기존 mvp 함수(`build_context_bundle`, `collect_relevant_context`,
`build_function_candidate_index`, `build_dependency_closure`)는
재구현하지 않았으므로 여기서는 재사용 계약만 검증한다.
"""

import importlib.util
import sys
from pathlib import Path

_STAGE_01_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "stage_01.py"
_spec = importlib.util.spec_from_file_location("stage_01", _STAGE_01_PATH)
stage_01 = importlib.util.module_from_spec(_spec)
sys.modules["stage_01"] = stage_01
_spec.loader.exec_module(stage_01)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}


def test_directory_structure_is_populated_with_known_paths():
    result = stage_01.run_stage_01(SAMPLE_ISSUE)
    assert any("mvp" in entry for entry in result["directory_structure"])


def test_context_bundle_keeps_existing_eight_key_contract():
    result = stage_01.run_stage_01(SAMPLE_ISSUE)
    assert set(result["context_bundle"].keys()) == {
        "issue",
        "goal",
        "relevant_documents",
        "relevant_code",
        "relevant_observations",
        "relevant_decisions",
        "known_constraints",
        "open_questions",
    }


def test_candidate_index_contains_known_function():
    result = stage_01.run_stage_01(SAMPLE_ISSUE)
    assert "FUNCTION: def validate_issue(issue: dict) -> None" in result["candidate_index"]


def test_no_target_means_no_dependency_closure():
    result = stage_01.run_stage_01(SAMPLE_ISSUE)
    assert result["target"] is None
    assert result["dependency_closure"] is None


def test_target_given_computes_dependency_closure():
    """`_strip_code_fence`는 Agent Package Refactoring으로 `agents/backend.py`
    (dotted: `agents.backend`)에 있다(ADC-0006 Condition 6)."""
    result = stage_01.run_stage_01(SAMPLE_ISSUE, target=("agents.backend", "_strip_code_fence"))
    assert result["target"] == ("agents.backend", "_strip_code_fence")
    assert "def _strip_code_fence(text: str) -> str:" in result["dependency_closure"]
