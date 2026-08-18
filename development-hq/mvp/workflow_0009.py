"""collect_relevant_context()의 결과를 build_context_bundle() 수준의
구조화된 Context Bundle로 감싸, Planning이 그 Context Bundle만 입력으로
사용했을 때의 결과를 관찰한다.

새 Runtime/Task Dispatcher/Stage Runner/Pipeline Runner/Capability를
추가하지 않는다. Planning Capability
(`requirements_agent_requirement_analysis`)의 내부 로직은 수정하지
않는다 — 이 파일은 `description`에 `[Relevant Context]` 마커와 그
뒤에 오는 내용을 이어붙여 전달할 뿐이다. 그 마커를 해석하는 별도
코드는 없다 — `call_engine()`이 호출하는 실제 Engine이 프롬프트
텍스트를 그대로 읽고 자연어로 이해한다.

같은 Issue에 대해 기존 방식(`run_issue_to_planning`, flat Context)과
새 방식(Context Bundle)으로 각각 Planning을 실행해 두 결과를 나란히
반환하는 `run_comparison()`만 추가한다 — Context 품질 차이가 Planning
결과에 어떤 영향을 주는지 관찰하기 위함이며, 어느 쪽이 더 나은지는
이 코드가 판단하지 않는다.
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
    """Issue를 받아 `build_context_bundle()`로 구조화된 Context Bundle을
    만들고, Planning에는 그 Bundle을 렌더링한 내용만 전달한다 —
    Planning이 실제로 보는 것은 Context Bundle(과 그것이 감싼 원본
    Issue)뿐이다.

    MVP-0037: `run_mvp_0001`(MVP-0036)과 동일한 이유로 Engine 호출
    실패(예: timeout)를 잡아 기존 반환 계약(2개 키)을 유지한 채
    반환한다. `bundle`은 Engine 호출 없이 이미 계산된 값이므로 실패
    시에도 그대로 유지한다. `run_comparison()`은 이 함수와
    `run_issue_to_planning()`(둘 다 개별적으로 예외를 처리함)만
    호출하므로 별도 처리가 필요 없다."""
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
    """같은 Issue로 MVP-0005 방식(flat Context)과 MVP-0009 방식(Context
    Bundle)의 Planning 결과를 각각 실행해 나란히 반환한다. 두 결과를
    비교 판단하지 않는다 — Observation이 사실만 기록한다."""
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
