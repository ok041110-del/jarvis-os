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


def _augment_design_with_target_source(design: str, module_path: Path) -> str:
    """이슈 0005a(`NoteStore.update()` 추가)를 실제로 실행해 재현한 실제
    결함: `code_generation()`이 받는 `design` 텍스트는 Design
    Capability의 산문(prose) 출력일 뿐, 기존 파일의 실제 소스를
    verbatim으로 담고 있지 않다(Design 지시문 자체가 "describe a design
    in prose ... do not write code yet"). 기존 파일에 메서드 하나를
    "추가"하라는 Design을 그대로 `code_generation`에 넘기면, 실제
    Engine이 새로 추가되는 부분만 반환하고(파일 전체가 아니라) 기존
    메서드 전체가 사라지는 것을 직접 재현해 확인했다 — `module_path`가
    이미 존재하는 파일을 덮어쓰는 이 함수의 계약(아래 `write_text`)과
    결합하면 실제로 파일이 손상된다.

    수정: `code_generation()`(development-hq/mvp/agents.py, 변경 없음)의
    Contract(`design: str -> code: str`)는 그대로 두고, 이 파일(호출
    쪽)이 실제 대상 파일이 이미 존재할 때만 그 파일의 실제 내용을
    verbatim으로 Design 텍스트 뒤에 덧붙여 넘긴다 — Design이 손실 없이
    전달하지 못하는 정보(기존 파일의 정확한 바이트)를 호출자가 직접
    보강하는 것이다. `_enrich_with_existing_code()`가 이미 쓰는 것과
    같은 기법(프롬프트에 실제 파일 내용을 문자열로 덧붙임)을 Design ->
    Implementation 경계에도 적용했을 뿐, 새 Capability나 새 함수
    시그니처를 만들지 않았다. 실제 Engine으로 재확인함: 이 보강을 거친
    출력은 기존 메서드 전부(byte 단위로 동일한 `add()` 포함)를 보존한
    채 새 메서드를 추가했다(대상 파일이 없을 때, 즉 신규 파일을 만드는
    Issue 1~4에서는 이 함수가 아무것도 하지 않는다 — 기존 동작을 그대로
    유지)."""
    if not module_path.exists():
        return design
    existing_source = module_path.read_text(encoding="utf-8")
    return (
        f"{design}\n\n"
        f"## Existing file to extend (verbatim — {module_path.relative_to(PROJECT_ROOT)})\n"
        "This is the ACTUAL, CURRENT, COMPLETE content of the file you are "
        "extending. Preserve every line below byte-for-byte except for the "
        "change described above. Return the COMPLETE resulting file (this "
        "content plus the change), never a diff or fragment.\n\n"
        f"```python\n{existing_source}\n```\n"
    )


def run_issue(issue_id: str, issue: dict, module_name: str, existing_files: list) -> dict:
    """Issue 하나를 Planning -> Design -> Implementation -> Validation까지
    통과시키고, 실제 생성된 코드를 `src/notekeeper/<module_name>.py`에 쓴
    뒤, 결과를 `issues/<issue_id>/` 아래 Markdown 4개로 저장한다."""
    enriched_issue = _enrich_with_existing_code(issue, existing_files)

    requirement = requirements_agent_requirement_analysis(enriched_issue)
    design = design_agent_design(enriched_issue, requirement)
    module_path = SRC_DIR / f"{module_name}.py"
    design_for_generation = _augment_design_with_target_source(design, module_path)
    code = backend_agent_code_generation(design_for_generation)

    SRC_DIR.mkdir(parents=True, exist_ok=True)
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
