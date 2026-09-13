"""Stage 01 PRD/Specification Synthesis(RFC-0034/ADC-0037/ADR-0022) — 이전에는
Stage 02가 담당했으나 이관됐고, Stage 02는 이 결과를 재생성 없이 전달만 한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import requirements_agent_requirement_analysis  # noqa: E402
from mvp.workflow import _engine_failure_message  # noqa: E402

_PRD_INSTRUCTION = (
    "아래는 이 작업의 PRD 골격입니다(Problem Definition/Constraints/Risks/"
    "Implementation Scope Candidates, Multi-Agent Reasoning 결과와 "
    "Repository Context 포함). 이 골격의 내용을 반영하면서, Task "
    "Decomposition(구현 단계를 나눈 목록)과 Acceptance Criteria(완료 판단 "
    "기준 목록)를 추가로 포함해 PRD/Specification을 작성해 주십시오."
)


def _skeleton_from_context_bundle(issue: dict, context_bundle: dict) -> dict:
    """Stage 01→02 의존 방향을 지키기 위해 골격 조립 로직을 이 Stage에도 둔다 —
    Stage 02는 이 값을 다시 계산하지 않고 그대로 전달한다."""
    return {
        "problem_definition": f"{issue['title']}: {issue['description']}",
        "constraints": context_bundle.get("known_constraints", []),
        "risks": context_bundle.get("open_questions", []),
        "scope_candidates": context_bundle.get("relevant_code", []),
    }


def _skeleton_to_text(skeleton: dict) -> str:
    return "\n\n".join([
        f"[Problem Definition]\n{skeleton['problem_definition']}",
        f"[Constraints]\n{', '.join(skeleton['constraints']) or '(없음)'}",
        f"[Risks]\n{', '.join(skeleton['risks']) or '(없음)'}",
        f"[Implementation Scope Candidates]\n{', '.join(skeleton['scope_candidates']) or '(없음)'}",
    ])


def _structured_understanding_to_text(structured_understanding: dict) -> str:
    intent = structured_understanding.get("intent") or {}
    goal = structured_understanding.get("goal") or {}
    requirement = structured_understanding.get("requirement") or {}
    ambiguity = structured_understanding.get("ambiguity") or {}

    return "\n".join([
        "[Structured Understanding]",
        f"Intent: action={intent.get('action', '(unknown)')}, "
        f"domain={intent.get('domain', '(unknown)')}, "
        f"explicit_intent={intent.get('explicit_intent', '(unknown)')}",
        f"Goal: desired_outcome={goal.get('desired_outcome', '(unknown)')}, "
        f"underlying_goal={goal.get('underlying_goal', '(unknown)')}",
        "Functional Requirements: " + (", ".join(requirement.get("functional_requirements") or []) or "(없음)"),
        "Non-Functional Requirements: " + (", ".join(requirement.get("non_functional_requirements") or []) or "(없음)"),
        "Unresolved Questions: " + (", ".join(ambiguity.get("unresolved_questions") or []) or "(없음)"),
        f"Reasoning Status: {structured_understanding.get('status', 'UNKNOWN')}",
    ])


def _repository_context_to_text(directory_structure: list, candidate_index: str) -> str:
    top_paths = ", ".join(directory_structure[:10]) if directory_structure else "(없음)"
    return (
        f"[Repository Structure(일부, 최대 10개)]\n{top_paths}\n\n"
        f"[AST Candidate Index(일부, 최대 2000자)]\n{(candidate_index or '')[:2000]}"
    )


def synthesize_prd(
    issue: dict,
    structured_understanding: dict,
    context_bundle: dict,
    directory_structure: list,
    candidate_index: str,
) -> dict:
    """Engine을 정확히 1회 호출한다 — 실패 시에도 기존 오류 포맷으로
    `specification`을 채운다(Stage 02의 기존 동작과 동일)."""
    skeleton = _skeleton_from_context_bundle(issue, context_bundle)
    synthesis_text = "\n\n".join([
        _skeleton_to_text(skeleton),
        _structured_understanding_to_text(structured_understanding),
        _repository_context_to_text(directory_structure, candidate_index),
    ])

    enriched_issue = dict(issue)
    enriched_issue["description"] = (
        f"{issue['description']}\n\n[PRD Synthesis Input]\n{_PRD_INSTRUCTION}\n\n{synthesis_text}"
    )

    try:
        specification = requirements_agent_requirement_analysis(enriched_issue)
    except Exception as exc:
        specification = _engine_failure_message(exc)

    return {"skeleton": skeleton, "specification": specification}
