"""TextKit runner: Issue -> Planning -> Design -> Implementation ->
src/textkit/<module>.py -> Validation. Verification script, not a
production entry point; does not modify development-hq/mvp.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.agents import (  # noqa: E402
    backend_agent_code_generation,
    design_agent_design,
    requirements_agent_requirement_analysis,
)
from mvp.workflow_0002 import run_mvp_0002  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent
ISSUES_DIR = PROJECT_ROOT / "issues"
SRC_DIR = PROJECT_ROOT / "src" / "textkit"


def _enrich_with_existing_code(issue: dict, existing_files: list) -> dict:
    """Appends existing files' verbatim source to the issue description
    as [Existing Code] context."""
    if not existing_files:
        return dict(issue)
    blocks = []
    for path in existing_files:
        content = path.read_text(encoding="utf-8")
        blocks.append(f"### {path.relative_to(PROJECT_ROOT)}\n```python\n{content}\n```")
    enriched = dict(issue)
    enriched["description"] = (
        f"{issue['description']}\n\n[Existing Code]\n" + "\n\n".join(blocks)
    )
    return enriched


def run_issue(issue_id: str, issue: dict, module_name: str, existing_files: list) -> dict:
    enriched_issue = _enrich_with_existing_code(issue, existing_files)

    requirement = requirements_agent_requirement_analysis(enriched_issue)
    design = design_agent_design(enriched_issue, requirement)
    code = backend_agent_code_generation(design)

    SRC_DIR.mkdir(parents=True, exist_ok=True)
    module_path = SRC_DIR / f"{module_name}.py"
    module_path.write_text(code.rstrip() + "\n", encoding="utf-8")

    validation = run_mvp_0002(code)

    out_dir = ISSUES_DIR / issue_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "planning.md").write_text(
        f"# Planning: {issue['title']}\n\n{requirement}\n", encoding="utf-8"
    )
    (out_dir / "design.md").write_text(
        f"# Design: {issue['title']}\n\n{design}\n", encoding="utf-8"
    )
    (out_dir / "implementation.md").write_text(
        f"# Implementation: {issue['title']}\n\n"
        f"실제 저장 위치: `src/textkit/{module_name}.py`\n\n"
        f"```python\n{code}\n```\n",
        encoding="utf-8",
    )
    (out_dir / "validation.md").write_text(
        f"# Validation: {issue['title']}\n\n"
        f"## Code Review\n\n{validation['code_review']}\n\n"
        f"## Test Execution\n\n{validation['test_execution']}\n",
        encoding="utf-8",
    )

    return {
        "issue": issue,
        "planning": requirement,
        "design": design,
        "implementation": code,
        "validation": validation,
        "module_path": module_path,
    }
