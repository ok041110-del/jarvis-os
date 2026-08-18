"""MVP-0009: build_context_bundle()의 결과를 Planning에 전달한다.

새 Runtime/Dispatcher/Capability는 추가하지 않는다. `[Relevant Context]`
마커를 해석하는 별도 코드는 없다 — Engine이 프롬프트 텍스트를 그대로
자연어로 읽는다. `run_comparison()`은 flat Context와 Context Bundle의
Planning 결과를 나란히 반환할 뿐 우열을 판단하지 않는다.
"""

from .agents import requirements_agent_requirement_analysis
from .project_intelligence import build_context_bundle
from .workflow import _engine_failure_message
from .workflow_0008 import REAL_ISSUE
from .workflow_project_intelligence import run_issue_to_planning


def _render_context_bundle(bundle: dict) -> str:
    def _list_or_none(files: list) -> str:
        return "\n".join(f"- {f}" for f in files) if files else "- (없음)"

    issue = bundle["issue"]
    return (
        f"## Issue\n- title: {issue['title']}\n- status: {issue.get('status', '(미지정)')}\n\n"
        f"## Goal\n{bundle['goal']}\n\n"
        f"## Relevant Documents\n{_list_or_none(bundle['relevant_documents'])}\n\n"
        f"## Relevant Code\n{_list_or_none(bundle['relevant_code'])}\n\n"
        f"## Relevant Observations\n{_list_or_none(bundle['relevant_observations'])}\n\n"
        f"## Relevant Decisions\n{_list_or_none(bundle['relevant_decisions'])}\n\n"
        f"## Known Constraints\n{_list_or_none(bundle['known_constraints'])}\n\n"
        f"## Open Questions\n{_list_or_none(bundle['open_questions'])}"
    )


def _enrich_issue_with_bundle(issue: dict, bundle: dict) -> dict:
    enriched_issue = dict(issue)
    enriched_issue["description"] = (
        f"{issue['description']}\n\n[Relevant Context]\n{_render_context_bundle(bundle)}"
    )
    return enriched_issue


def run_issue_to_planning_with_bundle(issue: dict) -> dict:
    """Planning에는 Context Bundle을 렌더링한 내용만 전달한다. `bundle`은
    Engine 호출 없이 이미 계산된 값이므로 실패 시에도 그대로 유지한다."""
    bundle = build_context_bundle(issue)
    enriched_issue = _enrich_issue_with_bundle(issue, bundle)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
    except Exception as exc:
        return {
            "context_bundle": bundle,
            "planning": _engine_failure_message(exc),
        }

    return {
        "context_bundle": bundle,
        "planning": requirement,
    }


def run_comparison(issue: dict) -> dict:
    """flat Context와 Context Bundle의 Planning 결과를 나란히 반환할 뿐,
    우열은 판단하지 않는다."""
    flat = run_issue_to_planning(issue)
    bundled = run_issue_to_planning_with_bundle(issue)

    return {
        "flat_context_planning": flat["planning"],
        "context_bundle_planning": bundled["planning"],
        "context_bundle": bundled["context_bundle"],
    }


if __name__ == "__main__":
    result = run_comparison(REAL_ISSUE)
    print("=== Flat Context Planning ===")
    print(result["flat_context_planning"])
    print("\n=== Context Bundle Planning ===")
    print(result["context_bundle_planning"])
