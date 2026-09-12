"""Stage 01 PRD/Specification Synthesis — RFC-0034/ADC-0037/ADR-0022.

Structured Understanding(Reasoning Aggregator 결과, 재추론 없이 직렬화)과
Repository Context(Code Analysis 결과: `context_bundle`/`candidate_index`/
`directory_structure`)를 종합해 기존 `requirements_agent_requirement_
analysis()`를 정확히 1회 호출한다 — 새 Agent/Capability를 추가하지 않는다
(기존 Stage 02 Capability 2를 그대로 재사용, 호출 위치만 이동).

이 Capability는 이전에 Stage 02가 담당했다(`stage_02.py`, ADR-0022로 책임
이동) — Stage 02는 이제 이 결과를 그대로 전달(passthrough)할 뿐 재생성하지
않는다."""

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
    """Stage 02의 기존 `_structure_from_context()`와 동일한 결정적
    재배치(Engine 미호출) — Stage 01→02 의존 방향을 지키기 위해 이 골격
    조립 로직만 이 Stage에도 둔다. Stage 02는 이제 이 골격을 다시 계산하지
    않고 `prd["skeleton"]`을 그대로 전달한다."""
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
    """Structured Understanding을 재추론 없이 텍스트로 직렬화한다 —
    Synthesis일 뿐 Agent를 다시 호출하지 않는다."""
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
    """PRD/Specification Synthesis — Structured Understanding과 Repository
    Context를 종합해 Engine을 정확히 1회 호출한다. Engine 실패 시에도
    `specification`은 기존 오류 포맷(`_engine_failure_message`)으로
    채워진다(Stage 02의 기존 동작과 동일)."""
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
