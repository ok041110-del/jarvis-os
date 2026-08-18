"""Execution Layer MVP-0003: ModelRequestBuilder.

Prompt Specification을 Model Request로 변환한다. 정보를 손실 없이
보존하고 Execution Layer 메타데이터만 추가한다. 실제 모델명(Claude/GPT
등)은 절대 넣지 않는다 — Execution Layer는 Model Independent를
유지한다.

`request_id`/`created_at`은 Session/Runtime의 책임 영역이므로 이 모듈이
생성하지 않는다 — 호출자가 주입한 값을 그대로 담아 순수 함수로 남는다.
"""

ARTIFACT_VERSION = "execution-layer-mvp-0003"
TARGET_ENGINE_PLACEHOLDER = "unresolved"

MODEL_REQUEST_HEADER = "# Model Request\n\n"


def build_model_request(prompt_specification: str, *, request_id: str, created_at: str) -> str:
    """Prompt Specification을 Model Request로 변환한다.

    텍스트는 그대로 두고 앞에 메타데이터 절(``## Metadata``)만 추가한다.
    ``request_id``/``created_at``은 호출자가 제공해야 한다.
    """
    metadata_lines = "\n".join(
        [
            f"- request_id: {request_id}",
            f"- artifact_version: {ARTIFACT_VERSION}",
            f"- created_at: {created_at}",
            f"- target_engine: {TARGET_ENGINE_PLACEHOLDER}",
        ]
    )

    return (
        f"{MODEL_REQUEST_HEADER}"
        f"## Metadata\n{metadata_lines}\n\n"
        f"## Prompt Specification\n{prompt_specification}"
    )
