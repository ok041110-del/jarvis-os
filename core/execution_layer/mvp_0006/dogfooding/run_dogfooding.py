"""Execution Layer MVP-0006 Dogfooding.

Execution Layer MVP-0001~0006을 그대로 통과시켜 전체 Artifact Chain을
검증한다. 읽기(호출)만 하며 어떤 파일도 수정하지 않는다.

`development-hq/mvp/workflow_0008.run_pipeline()`을 호출하지 않는다 —
ExecutionResultBuilder는 Execution State(문자열)만 입력받으므로 상위
Artifact 생성 경로와 무관하다. 대신 고정 샘플에서 시작한다.

`handle_id`/`produced_at`/`results`는 Builder가 생성하지 않으므로
(Runtime/Scheduler/Engine 책임 영역) 이 스크립트가 주입한다. `results`는
opaque placeholder 문자열 목록이다.
"""

import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "core"))

from execution_layer.mvp_0001.execution_request_builder import (  # noqa: E402
    build_execution_request,
)
from execution_layer.mvp_0002.prompt_specification_builder import (  # noqa: E402
    build_prompt_specification,
)
from execution_layer.mvp_0003.model_request_builder import (  # noqa: E402
    build_model_request,
)
from execution_layer.mvp_0004.execution_handle_builder import (  # noqa: E402
    build_execution_handle,
)
from execution_layer.mvp_0005.execution_state_builder import (  # noqa: E402
    build_execution_state,
)
from execution_layer.mvp_0006.execution_result_builder import (  # noqa: E402
    build_execution_result,
)

SAMPLE_IMPLEMENTATION_SPECIFICATION = (
    "## Target File\n"
    "development-hq/mvp/generated/reverse_string.py\n\n"
    "## Public Interface\n"
    "`def reverse_string(*args, **kwargs)`\n\n"
    "## Functions\n"
    "- `def reverse_string(*args, **kwargs)` (Public Interface): 문자열을 뒤집는다\n\n"
    "## Classes\n"
    "- (필요 없음: Design이 단일 함수형 Component만 제안했다)\n\n"
    "## Dependencies\n"
    "- (Reference Context에서 식별된 의존 대상 없음)\n\n"
    "## Algorithm Outline\n"
    "1. 입력 문자열을 받는다\n"
    "2. 문자열을 뒤집는다\n\n"
    "## Edge Cases\n"
    "- (Constraints에서 식별된 Edge Case 없음)\n\n"
    "## Validation Notes\n"
    "- (Open Questions 없음)\n\n"
    "## Reference Design\n"
    "## Component\n문자열을 뒤집는 함수\n"
)

CREATED_AT_PLACEHOLDER = "unresolved"
SUBMITTED_AT_PLACEHOLDER = "unresolved"
CHANGED_AT_PLACEHOLDER = "unresolved"
PRODUCED_AT_PLACEHOLDER = "unresolved"
INITIAL_STATE = "COMPLETED"

PLACEHOLDER_RESULTS = [
    "placeholder: diff not produced (call_engine not invoked, see run_dogfooding.py docstring)",
    "placeholder: log not produced (call_engine not invoked, see run_dogfooding.py docstring)",
]

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

_HANDLE_ID_LINE_PATTERN = re.compile(r"^- handle_id: (?P<value>.+)$", re.MULTILINE)


def _derive_id(content: str) -> str:
    """내용 기반 결정론적 ID(SHA-256 해시 앞 16자). 무작위 발급이 아니다."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _extract_handle_id(execution_handle: str) -> str:
    match = _HANDLE_ID_LINE_PATTERN.search(execution_handle)
    if not match:
        raise ValueError("execution_handle에서 handle_id를 찾을 수 없다")
    return match.group("value")


def _run_case(name: str, implementation_specification: str) -> None:
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)
    request_id = _derive_id(prompt_specification)
    model_request = build_model_request(
        prompt_specification,
        request_id=request_id,
        created_at=CREATED_AT_PLACEHOLDER,
    )
    handle_id = _derive_id(model_request)
    execution_handle = build_execution_handle(
        model_request,
        handle_id=handle_id,
        submitted_at=SUBMITTED_AT_PLACEHOLDER,
    )
    handle_id_from_handle = _extract_handle_id(execution_handle)
    execution_state = build_execution_state(
        execution_handle,
        handle_id=handle_id_from_handle,
        state=INITIAL_STATE,
        changed_at=CHANGED_AT_PLACEHOLDER,
    )
    execution_result = build_execution_result(
        execution_state,
        handle_id=handle_id_from_handle,
        produced_at=PRODUCED_AT_PLACEHOLDER,
        results=PLACEHOLDER_RESULTS,
    )

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
    (OUTPUT_DIR / f"{name}.model_request.md").write_text(
        model_request, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.execution_handle.md").write_text(
        execution_handle, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.execution_state.md").write_text(
        execution_state, encoding="utf-8"
    )
    (OUTPUT_DIR / f"{name}.execution_result.md").write_text(
        execution_result, encoding="utf-8"
    )

    print(f"--- {name} ---")
    print(f"Implementation Specification length: {len(implementation_specification)}")
    print(f"Execution Request length: {len(execution_request)}")
    print(f"Prompt Specification length: {len(prompt_specification)}")
    print(f"Model Request length: {len(model_request)}")
    print(f"Execution Handle length: {len(execution_handle)}")
    print(f"Execution State length: {len(execution_state)}")
    print(f"Execution Result length: {len(execution_result)}")
    print(f"request_id (derived): {request_id}")
    print(f"handle_id (derived): {handle_id}")
    print(f"handle_id (from execution_handle): {handle_id_from_handle}")
    print(
        "execution_state in execution_result: "
        f"{execution_state in execution_result}"
    )
    print()


def main() -> None:
    _run_case("toy_issue", SAMPLE_IMPLEMENTATION_SPECIFICATION)


if __name__ == "__main__":
    main()
