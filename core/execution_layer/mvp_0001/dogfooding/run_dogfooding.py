"""Execution Layer MVP-0001 Dogfooding.

Development HQ가 실제로 생성하는 Implementation Specification을 입력으로
ExecutionRequestBuilder를 실행하고 결과를 `output/`에 저장한다.
Development HQ 코드는 읽기(호출)만 한다.
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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / f"{name}.implementation_specification.md").write_text(
        implementation_specification, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.execution_request.md").write_text(
        execution_request, encoding="utf-8"
    )

    sections_before = find_known_sections(implementation_specification)
    sections_after = find_known_sections(execution_request)

    print(f"--- {name} ---")
    print(f"Implementation Specification length: {len(implementation_specification)}")
    print(f"Execution Request length: {len(execution_request)}")
    print(f"8 sections present before: {sections_before}")
    print(f"8 sections present after:  {sections_after}")
    print(f"before == after: {sections_before == sections_after}")
    print(
        "implementation_specification in execution_request: "
        f"{implementation_specification in execution_request}"
    )
    print()


def main() -> None:
    _run_case("real_issue", REAL_ISSUE)
    _run_case("toy_issue", TOY_ISSUE)


if __name__ == "__main__":
    main()
