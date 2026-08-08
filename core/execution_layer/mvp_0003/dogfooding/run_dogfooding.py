"""Execution Layer MVP-0003 Dogfooding.

Development HQ MVP-0013(`_generate_code()`)이 실제로 생성하는
Implementation Specification부터, Execution Layer MVP-0001
(`build_execution_request`), MVP-0002(`build_prompt_specification`),
MVP-0003(`build_model_request`)을 그대로 통과시켜 전체 Artifact Chain
(Implementation Specification → Execution Request → Prompt
Specification → Model Request)을 검증한다.

Development HQ, MVP-0001, MVP-0002 코드는 읽기(호출)만 한다. 어떤
파일도 수정하지 않는다. 이전 MVP와 동일하게 실제 Issue
(`workflow_0008.REAL_ISSUE`)와 토이 Issue("reverse string")를 모두
사용한다.

`request_id`/`created_at`은 ModelRequestBuilder가 스스로 생성하지 않는
값이므로(Session/Runtime 책임 영역, `model_request_builder.py` 참조),
이 스크립트가 호출자로서 값을 주입한다. `request_id`는 Prompt
Specification 내용의 SHA-256 해시로 결정론적으로 유도한다(무작위 발급
아님 — 동일한 Prompt Specification은 항상 동일한 request_id를 만든다).
`created_at`은 이 MVP가 실제 시계를 읽지 않는다는 사실을 그대로 반영해
고정 placeholder 문자열을 사용한다.
"""

import hashlib
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

TOY_ISSUE = {
    "title": "reverse string",
    "description": "문자열을 뒤집는 함수를 작성해야 한다.",
    "status": "Open",
}

CREATED_AT_PLACEHOLDER = "unresolved"

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def _derive_request_id(prompt_specification: str) -> str:
    """Prompt Specification 내용으로부터 결정론적 request_id를 만든다.

    무작위 발급(uuid4 등)이 아니라 내용 해시이므로, 동일한 Prompt
    Specification은 항상 동일한 request_id를 만든다.
    """
    return hashlib.sha256(prompt_specification.encode("utf-8")).hexdigest()[:16]


def _run_case(name: str, issue: dict) -> None:
    result = run_pipeline(issue)
    implementation_specification = result["implementation"]
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)
    request_id = _derive_request_id(prompt_specification)
    model_request = build_model_request(
        prompt_specification,
        request_id=request_id,
        created_at=CREATED_AT_PLACEHOLDER,
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

    print(f"--- {name} ---")
    print(f"Implementation Specification length: {len(implementation_specification)}")
    print(f"Execution Request length: {len(execution_request)}")
    print(f"Prompt Specification length: {len(prompt_specification)}")
    print(f"Model Request length: {len(model_request)}")
    print(f"request_id (derived): {request_id}")
    print(
        "prompt_specification in model_request: "
        f"{prompt_specification in model_request}"
    )
    print()


def main() -> None:
    _run_case("real_issue", REAL_ISSUE)
    _run_case("toy_issue", TOY_ISSUE)


if __name__ == "__main__":
    main()
