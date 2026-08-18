"""Execution Layer MVP-0002 Dogfooding.

Development HQ가 생성하는 Implementation Specification부터 MVP-0001/0002
Builder를 통과시켜 Artifact Flow를 검증한다. 읽기(호출)만 하며 어떤
파일도 수정하지 않는다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "core"))
sys.path.insert(0, str(REPO_ROOT / "development-hq"))

from mvp.workflow_0008 import REAL_ISSUE, run_pipeline  # noqa: E402

from execution_layer.mvp_0001.execution_request_builder import (  # noqa: E402
    build_execution_request,
    find_known_sections,
)
from execution_layer.mvp_0002.prompt_specification_builder import (  # noqa: E402
    SOURCE_SECTIONS_IN_ORDER,
    _extract_section_body,
    build_prompt_specification,
    find_prompt_sections,
)

TOY_ISSUE = {
    "title": "reverse string",
    "description": "문자열을 뒤집는 함수를 작성해야 한다.",
    "status": "Open",
}

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def _run_case(name: str, issue: dict) -> None:
    result = run_pipeline(issue)
    implementation_specification = result["implementation"]
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / f"{name}.implementation_specification.md").write_text(
        implementation_specification, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.execution_request.md").write_text(
        execution_request, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.prompt_specification.md").write_text(
        prompt_specification, encoding="utf-8"
    )

    all_bodies_present = all(
        _extract_section_body(execution_request, section) in prompt_specification
        for section in SOURCE_SECTIONS_IN_ORDER
    )

    print(f"--- {name} ---")
    print(f"Implementation Specification length: {len(implementation_specification)}")
    print(f"Execution Request length: {len(execution_request)}")
    print(f"Prompt Specification length: {len(prompt_specification)}")
    print(f"8 ER sections present: {find_known_sections(execution_request)}")
    print(f"5 Prompt sections present: {find_prompt_sections(prompt_specification)}")
    print(f"all 9 source section bodies verbatim in prompt spec: {all_bodies_present}")
    print()


def main() -> None:
    _run_case("real_issue", REAL_ISSUE)
    _run_case("toy_issue", TOY_ISSUE)


if __name__ == "__main__":
    main()
