"""Stage 02: Planning & Specification 실행 진입점 (Architecture Owner
승인, ADR-0008 §4).

Stage 01의 Output Schema(`run_stage_01()` 반환 dict)를 그대로 Input으로
받는다 — Stage 01을 다시 호출하지 않는다. 새 Agent/Capability를
추가하지 않고 기존 `agents.requirements_agent_requirement_analysis()`를
재사용한다(`CAPABILITIES.md` Capability 2).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import requirements_agent_requirement_analysis
from mvp.workflow import _engine_failure_message

_SPECIFICATION_INSTRUCTION = (
    "아래는 이 작업의 Specification 골격입니다(Problem Definition/"
    "Constraints/Risks/Implementation Scope Candidates). 이 골격의 "
    "내용을 반영하면서, Task Decomposition(구현 단계를 나눈 목록)과 "
    "Acceptance Criteria(완료 판단 기준 목록)를 추가로 포함해 "
    "Specification을 작성해 주십시오."
)


def _structure_from_context(issue: dict, stage_01_context: dict) -> dict:
    """Stage 01 Context에서 결정적으로(Engine 호출 없이) Specification
    골격을 뽑는다 — 새 파일 탐색/AST 분석을 하지 않고 Stage 01 결과만
    재배치한다."""
    context_bundle = stage_01_context["context_bundle"]
    return {
        "problem_definition": f"{issue['title']}: {issue['description']}",
        "constraints": context_bundle["known_constraints"],
        "risks": context_bundle["open_questions"],
        "scope_candidates": context_bundle["relevant_code"],
    }


def _skeleton_to_text(skeleton: dict) -> str:
    lines = [
        f"[Problem Definition]\n{skeleton['problem_definition']}",
        f"[Constraints]\n{', '.join(skeleton['constraints']) or '(없음)'}",
        f"[Risks]\n{', '.join(skeleton['risks']) or '(없음)'}",
        f"[Implementation Scope Candidates]\n{', '.join(skeleton['scope_candidates']) or '(없음)'}",
    ]
    return "\n\n".join(lines)


def _enrich_issue_with_skeleton(issue: dict, skeleton_text: str) -> dict:
    enriched_issue = dict(issue)
    enriched_issue["description"] = (
        f"{issue['description']}\n\n[Specification Skeleton]\n"
        f"{_SPECIFICATION_INSTRUCTION}\n\n{skeleton_text}"
    )
    return enriched_issue


def run_stage_02(issue: dict, stage_01_context: dict) -> dict:
    """Skeleton 추출 -> Requirement Analysis Capability 재사용 -> Specification.

    Engine 호출 실패 시에도 `specification`은 채워진다(기존
    `_engine_failure_message()` 포맷) — `skeleton`은 Engine과 무관하게
    항상 채워진다(SPECIFICATION.md 참고)."""
    skeleton = _structure_from_context(issue, stage_01_context)
    skeleton_text = _skeleton_to_text(skeleton)
    enriched_issue = _enrich_issue_with_skeleton(issue, skeleton_text)

    try:
        specification = requirements_agent_requirement_analysis(enriched_issue)
    except Exception as exc:
        specification = _engine_failure_message(exc)

    return {
        "skeleton": skeleton,
        "specification": specification,
    }
