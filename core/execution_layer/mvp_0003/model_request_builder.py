"""Execution Layer MVP-0003: ModelRequestBuilder.

Prompt Specification(Execution Layer MVP-0002의 Artifact)을 Model
Request(Execution Layer의 세 번째 공식 Artifact)로 변환한다.

Contract (요청 원문 기준):
- Input: Prompt Specification (`str`, MVP-0002 `build_prompt_specification()`
  이 생성하는 형태).
- Output: Model Request (`str`).
- Model Request는 Prompt Specification의 정보를 손실 없이 보존한다.
  추가되는 정보는 Execution Layer 내부 메타데이터뿐이다(request_id,
  artifact_version, created_at, target_engine — placeholder).
- Model Request는 특정 모델을 호출하는 코드가 아니다. Execution Engine이
  사용할 표준 요청 객체(텍스트 형태)일 뿐이다.
- 실제 모델명(Claude/GPT/Codex 등)은 절대 넣지 않는다 — Execution Layer는
  Model Independent를 유지한다. `TARGET_ENGINE_PLACEHOLDER`는 항상
  고정 문자열이며, 이 모듈은 이를 결정하거나 조회하지 않는다.
- AI/LLM/Model 호출 없음. HTTP 요청 없음. Runtime/Session/Retry/Scheduler
  없음.

## request_id / created_at을 이 모듈이 생성하지 않는 이유

request_id를 무작위로 발급하거나 created_at을 시스템 시계에서 읽는
행위는 이 MVP가 명시적으로 금지한 Session/Runtime의 책임 영역과
겹친다("무엇을 언제 요청했는가"를 추적하는 것은 실행 세션의 역할이다).
그래서 `build_model_request()`는 두 값을 내부에서 생성하지 않고 호출자가
주입한 값을 그대로 담기만 한다. 이 설계 덕분에 이 함수는 순수 함수로
남고, 동일한 세 인자(Prompt Specification, request_id, created_at)가
주어지면 항상 동일한 Model Request를 만든다(Deterministic
Transformation) — 시스템 시계나 난수에 의존하지 않는다.
"""

# Model Request 안에서 고정되는 Execution Layer 메타데이터. 입력에 따라
# 달라지지 않으므로 모듈 상수로 둔다 — 호출자가 바꿀 수 없다.
ARTIFACT_VERSION = "execution-layer-mvp-0003"
TARGET_ENGINE_PLACEHOLDER = "unresolved"

MODEL_REQUEST_HEADER = "# Model Request\n\n"


def build_model_request(prompt_specification: str, *, request_id: str, created_at: str) -> str:
    """Prompt Specification을 Model Request로 변환한다.

    Prompt Specification의 텍스트를 한 글자도 바꾸지 않고, 그 앞에
    Execution Layer 메타데이터 절(``## Metadata``)만 추가한다.
    ``request_id``와 ``created_at``은 호출자가 제공해야 한다(이 함수는
    둘 다 생성하지 않는다). ``artifact_version``과 ``target_engine``은
    모듈 상수로 고정되어 있으며, 항상 동일한 값이 채워진다.
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
