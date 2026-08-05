"""Development HQ DevKit runner.

Issue -> Project Intelligence -> Planning -> Design -> Validation.

이 파일은 Development HQ(`development-hq/mvp`)를 수정하지 않는다. 그
안의 기존 함수(`collect_relevant_context`,
`requirements_agent_requirement_analysis`, `design_agent_design`,
`backend_agent_code_review`, `qa_agent_test_execution`)를 그대로
import해서 순서대로 호출하고, 결과를 Markdown 파일 3개로 저장하는
하드코딩된 순차 호출 하나만 담는다. 새 Capability/Dispatcher/Runtime/
Stage Runner/Pipeline Runner는 만들지 않는다.

Project Intelligence(`collect_relevant_context`)는 Planning 호출
직전에서만 사용한다 — Design에는 Context가 섞이지 않은 원본 Issue를
그대로 넘긴다(MVP-0007/0008과 동일한 방식).

Implementation(Code Generation)은 이번 단계 범위 밖이다. 실제 코드가
없으므로, Validation Capability(`code_review`, `test_execution`)에는
Design 산출물 텍스트를 그대로 입력한다 — 이 두 Capability가 원래
코드용으로 만들어졌다는 사실을 바꾸지 않고, 코드가 아닌 입력에 대해
그대로 실행했을 때 무엇을 반환하는지를 관찰하기 위함이다.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.agents import (  # noqa: E402
    backend_agent_code_review,
    design_agent_design,
    qa_agent_test_execution,
    requirements_agent_requirement_analysis,
)
from mvp.project_intelligence import collect_relevant_context  # noqa: E402
from mvp.workflow_project_intelligence import _enrich_issue  # noqa: E402

ISSUES_DIR = Path(__file__).resolve().parent / "issues"


def run_issue(issue_id: str, issue: dict) -> dict:
    """Issue 하나를 Project Intelligence -> Planning -> Design ->
    Validation까지 통과시키고, 결과를 issues/<issue_id>/ 아래 Markdown
    3개 파일로 저장한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    requirement = requirements_agent_requirement_analysis(enriched_issue)
    design = design_agent_design(issue, requirement)
    review = backend_agent_code_review(design)
    test_cases = qa_agent_test_execution(design, review)

    result = {
        "issue": issue,
        "context": context,
        "planning": requirement,
        "design": design,
        "validation": {"code_review": review, "test_execution": test_cases},
    }

    out_dir = ISSUES_DIR / issue_id
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "planning.md").write_text(
        f"# Planning: {issue['title']}\n\n{requirement}\n", encoding="utf-8"
    )
    (out_dir / "design.md").write_text(
        f"# Design: {issue['title']}\n\n{design}\n", encoding="utf-8"
    )
    (out_dir / "validation.md").write_text(
        f"# Validation: {issue['title']}\n\n"
        f"## Code Review\n\n{review}\n\n"
        f"## Test Execution\n\n{test_cases}\n",
        encoding="utf-8",
    )

    return result


DEVKIT_ISSUE_0001 = {
    "title": "Development HQ DevKit 최소 기능",
    "description": (
        "Development HQ DevKit 프로젝트의 첫 기능: 실제 Issue 하나를 "
        "입력받아 Development HQ의 기존 Capability(Project Intelligence, "
        "Planning, Design, Validation)를 순서대로 실행하고, 그 결과를 "
        "planning.md, design.md, validation.md 세 개의 Markdown 파일로 "
        "저장한다. Implementation(Code Generation)은 이번 기능에 포함하지 "
        "않는다."
    ),
    "status": "Open",
}


if __name__ == "__main__":
    run_issue("0001-devkit-minimal-feature", DEVKIT_ISSUE_0001)
