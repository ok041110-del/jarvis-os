"""NoteKeeper runner.

Issue -> Project Intelligence(선행 Issue의 실제 코드를 [Existing Code]
Context로 포함) -> Planning -> Design -> Implementation(code_generation) ->
src/notekeeper/<module>.py 저장 -> Validation(workflow_0002.run_mvp_0002를
그대로 재사용).

`projects/textkit/runner.py`와 정확히 같은 구조·같은 성격(검증 목적
스크립트, production 위치 후보 아님)이다. 이 파일은 Development HQ
(`development-hq/mvp`)를 수정하지 않는다.
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
SRC_DIR = PROJECT_ROOT / "src" / "notekeeper"


def _enrich_with_existing_code(issue: dict, existing_files: list) -> dict:
    """`projects/textkit/runner.py`의 `_enrich_with_existing_code`와
    동일한 패턴 — Issue description 끝에 선행 Issue의 실제 코드를
    그대로 인용한 텍스트 블록을 덧붙인다. 새 Project Intelligence
    메커니즘이 아니다."""
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
    """Issue 하나를 Planning -> Design -> Implementation -> Validation까지
    통과시키고, 실제 생성된 코드를 `src/notekeeper/<module_name>.py`에 쓴
    뒤, 결과를 `issues/<issue_id>/` 아래 Markdown 4개로 저장한다."""
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
        f"실제 저장 위치: `src/notekeeper/{module_name}.py`\n\n"
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
