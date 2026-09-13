import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import design_agent_design
from mvp.workflow import _engine_failure_message

_DESIGN_INSTRUCTION = (
    "아래는 이 작업의 Design 골격입니다(Component Candidates/"
    "Implementation Scope Candidates/Constraints/Risks). 이 골격의 "
    "내용을 반영하면서, Architecture Definition(전체 구조), Component "
    "Identification(구성 요소), Responsibility Allocation(책임 배분), "
    "Interface/Contract Identification(경계와 계약), Data Flow(데이터 "
    "흐름), Implementation Strategy(구현 순서/방식)를 추가로 포함해 "
    "Architecture/Design을 작성해 주십시오."
)


def _structure_from_specification(stage_01_context: dict, stage_02_output: dict) -> dict:
    skeleton_02 = stage_02_output["skeleton"]
    return {
        "component_candidates": stage_01_context["candidate_index"],
        "scope_candidates": skeleton_02["scope_candidates"],
        "constraints": skeleton_02["constraints"],
        "risks": skeleton_02["risks"],
    }


def _skeleton_to_text(skeleton: dict) -> str:
    lines = [
        f"[Component Candidates]\n{skeleton['component_candidates']}",
        f"[Implementation Scope Candidates]\n{', '.join(skeleton['scope_candidates']) or '(없음)'}",
        f"[Constraints]\n{', '.join(skeleton['constraints']) or '(없음)'}",
        f"[Risks]\n{', '.join(skeleton['risks']) or '(없음)'}",
    ]
    return "\n\n".join(lines)


def _enrich_requirement_with_skeleton(specification: str, skeleton_text: str) -> str:
    return f"{specification}\n\n[Architecture Design Skeleton]\n{_DESIGN_INSTRUCTION}\n\n{skeleton_text}"


def run_stage_03(issue: dict, stage_01_context: dict, stage_02_output: dict) -> dict:
    skeleton = _structure_from_specification(stage_01_context, stage_02_output)
    skeleton_text = _skeleton_to_text(skeleton)
    enriched_requirement = _enrich_requirement_with_skeleton(
        stage_02_output["specification"], skeleton_text
    )

    try:
        design = design_agent_design(issue, enriched_requirement)
    except Exception as exc:
        design = _engine_failure_message(exc)

    return {
        "skeleton": skeleton,
        "design": design,
    }
