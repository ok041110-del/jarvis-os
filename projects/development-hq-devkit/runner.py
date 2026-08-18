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
    context = collect_relevant_context(issue)
    # Design intentionally gets the raw `issue`, not `enriched_issue` — only
    # Planning uses collected context (MVP-0007/0008 pattern).
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
