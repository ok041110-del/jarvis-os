"""TextKit runner.

Issue -> Project Intelligence(선행 Issue의 실제 코드를 [Existing Code]
Context로 포함) -> Planning -> Design -> Implementation(code_generation) ->
src/textkit/<module>.py 저장 -> Validation(workflow_0002.run_mvp_0002를
그대로 재사용).

이 파일은 Development HQ(`development-hq/mvp`)를 수정하지 않는다. 그
안의 기존 함수(`requirements_agent_requirement_analysis`,
`design_agent_design`, `backend_agent_code_generation`,
`run_mvp_0002`)를 그대로 import해서 순서대로 호출하고, 결과를
Markdown 3개 + 실제 소스 파일 1개로 저장하는 하드코딩된 순차 호출만
담는다. 새 Capability/Dispatcher/Runtime/Stage Runner/Pipeline Runner는
만들지 않는다.

`projects/development-hq-devkit/runner.py`와 같은 성격의 검증 스크립트다
— production 위치 후보가 아니다(README.md 참고).
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
    """`workflow_project_intelligence._enrich_issue`(MVP-0005/0006)가
    쓰는 것과 같은 패턴 — Issue description 끝에 텍스트 블록을
    덧붙인다. 새 Project Intelligence 메커니즘이 아니다. `existing_files`는
    이미 실제로 diskeh에 존재하는(선행 Issue가 실제로 만든) 소스 파일
    경로 목록이며, 그 파일의 실제 내용을 그대로 인용한다 — 요약하거나
    가공하지 않는다."""
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
    통과시키고, 실제 생성된 코드를 `src/textkit/<module_name>.py`에 쓴 뒤,
    결과를 `issues/<issue_id>/` 아래 Markdown 3개로 저장한다."""
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
