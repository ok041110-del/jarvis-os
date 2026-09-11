"""Stage 02(Planning & Specification) `run_stage_02()` 검증 (ADR-0008,
`stages/02_planning_specification/VALIDATION.md`).

PRD/Specification 생성 책임은 Stage 01로 이동했다(RFC-0034/ADC-0037/
ADR-0022) — 여기서는 Stage 02가 Stage 01의 `prd`를 재생성 없이 그대로
전달(passthrough)하는지만 검증한다. Synthesis 자체의 검증은
`test_stage01_prd_synthesis.py` 참조.
"""

import importlib.util
import sys
from pathlib import Path

_STAGE_02_PATH = (
    Path(__file__).resolve().parents[2] / "stages" / "02_planning_specification" / "stage_02.py"
)
_spec = importlib.util.spec_from_file_location("stage_02", _STAGE_02_PATH)
stage_02 = importlib.util.module_from_spec(_spec)
sys.modules["stage_02"] = stage_02
_spec.loader.exec_module(stage_02)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

SAMPLE_PRD = {
    "skeleton": {
        "problem_definition": "Sample Issue: Do the thing.",
        "constraints": ["docs/governance/rt/RT-0001.md"],
        "risks": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
        "scope_candidates": ["hqs/development/mvp/agents.py"],
    },
    "specification": "SPECIFICATION TEXT",
}

SAMPLE_STAGE_01_CONTEXT = {
    "directory_structure": ["hqs/development/mvp/"],
    "context_bundle": {
        "issue": SAMPLE_ISSUE,
        "goal": "Sample Issue",
        "relevant_documents": ["docs/01_mvp/MVP.md"],
        "relevant_code": ["hqs/development/mvp/agents.py"],
        "relevant_observations": [],
        "relevant_decisions": ["docs/governance/adc/ADC-0005.md"],
        "known_constraints": ["docs/governance/rt/RT-0001.md"],
        "open_questions": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
    },
    "candidate_index": "FILE: hqs/development/mvp/agents.py\nFUNCTION: ...",
    "target": None,
    "dependency_closure": None,
    "prd": SAMPLE_PRD,
}


def test_run_stage_02_passes_through_stage_01_prd_unchanged():
    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result == SAMPLE_PRD


def test_run_stage_02_does_not_mutate_input_prd():
    original = dict(SAMPLE_PRD)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)
    result["specification"] = "MUTATED"

    assert SAMPLE_STAGE_01_CONTEXT["prd"] == original


def test_run_stage_02_output_keeps_specification_result_contract_shape():
    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert set(result.keys()) == {"skeleton", "specification"}
    assert set(result["skeleton"].keys()) == {
        "problem_definition", "constraints", "risks", "scope_candidates",
    }
