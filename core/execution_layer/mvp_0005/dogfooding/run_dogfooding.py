"""Execution Layer MVP-0005 Dogfooding.

Development HQ MVP-0013(`_generate_code()`)이 실제로 생성하는
Implementation Specification부터, Execution Layer MVP-0001~0005를 그대로
통과시켜 전체 Artifact Chain(Implementation Specification → Execution
Request → Prompt Specification → Model Request → Execution Handle →
Execution State)을 검증한다.

Development HQ, MVP-0001~0004 코드는 읽기(호출)만 한다. 어떤 파일도
수정하지 않는다. 이전 MVP와 동일하게 실제 Issue
(`workflow_0008.REAL_ISSUE`)와 토이 Issue("reverse string")를 모두
사용한다.

`state`/`changed_at`/`handle_id`는 ExecutionStateBuilder가 스스로
생성하지 않는 값이므로(Runtime/Scheduler 책임 영역,
`execution_state_builder.py` 참조), 이 스크립트가 호출자로서 값을
주입한다. `handle_id`는 방금 만든 Execution Handle 자신의 handle_id를
그대로 재사용한다(같은 Execution Handle을 가리키는 Execution State이므로
당연히 같아야 하며, 이 스크립트가 그 일관성을 직접 보장한다).
`changed_at`은 이전 MVP의 `created_at`/`submitted_at`과 동일하게 고정
placeholder 문자열을 사용하고, `state`는 이번 MVP가 다루는 5개 값 중
`"PENDING"`(Execution Handle이 만들어진 직후의 최초 상태)을 사용한다.
"""

import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "core"))
sys.path.insert(0, str(REPO_ROOT / "development-hq"))

from mvp.workflow_0008 import REAL_ISSUE, run_pipeline  # noqa: E402

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

TOY_ISSUE = {
    "title": "reverse string",
    "description": "문자열을 뒤집는 함수를 작성해야 한다.",
    "status": "Open",
}

CREATED_AT_PLACEHOLDER = "unresolved"
SUBMITTED_AT_PLACEHOLDER = "unresolved"
CHANGED_AT_PLACEHOLDER = "unresolved"
INITIAL_STATE = "PENDING"

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


def _run_case(name: str, issue: dict) -> None:
    result = run_pipeline(issue)
    implementation_specification = result["implementation"]
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
    # handle_id는 방금 만든 Execution Handle 자신의 값을 그대로
    # 재사용한다 — 새로 유도하지 않는다.
    handle_id_from_handle = _extract_handle_id(execution_handle)
    execution_state = build_execution_state(
        execution_handle,
        handle_id=handle_id_from_handle,
        state=INITIAL_STATE,
        changed_at=CHANGED_AT_PLACEHOLDER,
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

    print(f"--- {name} ---")
    print(f"Implementation Specification length: {len(implementation_specification)}")
    print(f"Execution Request length: {len(execution_request)}")
    print(f"Prompt Specification length: {len(prompt_specification)}")
    print(f"Model Request length: {len(model_request)}")
    print(f"Execution Handle length: {len(execution_handle)}")
    print(f"Execution State length: {len(execution_state)}")
    print(f"request_id (derived): {request_id}")
    print(f"handle_id (derived): {handle_id}")
    print(f"handle_id (from execution_handle): {handle_id_from_handle}")
    print(
        "execution_handle in execution_state: "
        f"{execution_handle in execution_state}"
    )
    print()


def main() -> None:
    _run_case("real_issue", REAL_ISSUE)
    _run_case("toy_issue", TOY_ISSUE)


if __name__ == "__main__":
    main()
