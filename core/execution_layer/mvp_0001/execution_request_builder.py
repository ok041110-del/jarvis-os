"""Execution Layer MVP-0001: ExecutionRequestBuilder.

Implementation Specification(Development HQ의 산출물, MVP-0013)을
Execution Request(Execution Layer 내부 전용 중간 Artifact)로 변환한다.

Contract (docs/core/execution-layer/MVP-0001-plan.md):
- Input: Implementation Specification (`str`, 8개 항목: Target File /
  Public Interface / Functions / Classes / Dependencies / Algorithm
  Outline / Edge Cases / Validation Notes — `development-hq/mvp/engine.py`
  `_generate_code()`가 실제로 생성하는 형태 그대로).
- Output: Execution Request (`str`).
- 이 모듈은 Transformation만 수행한다. Interpretation(의미 해석, 요약,
  재구성)은 수행하지 않는다 — 입력 텍스트를 한 글자도 바꾸지 않고,
  Execution Request임을 나타내는 머리말 하나만 앞에 붙인다.
- AI/LLM/Model 호출 없음. Prompt 생성 없음. Session/Runtime 없음.
"""

EXECUTION_REQUEST_HEADER = "# Execution Request\n\n"

KNOWN_SECTIONS = (
    "Target File",
    "Public Interface",
    "Functions",
    "Classes",
    "Dependencies",
    "Algorithm Outline",
    "Edge Cases",
    "Validation Notes",
)


def build_execution_request(implementation_specification: str) -> str:
    """Implementation Specification을 Execution Request로 변환한다.

    입력 텍스트의 내용을 변경하지 않는다(해석·요약·재구성 없음). 머리말
    하나만 앞에 붙이는 것으로 변환이 끝난다. 동일한 입력은 항상 동일한
    출력을 만든다(Deterministic Transformation).
    """
    return f"{EXECUTION_REQUEST_HEADER}{implementation_specification}"


def find_known_sections(text: str) -> dict:
    """텍스트 안에서 `## {Section}` 마커로 시작하는 8개 알려진 절의 존재
    여부만 확인한다.

    이 함수는 `_generate_code()`(development-hq/mvp/engine.py)가 실제로
    사용하는 마커 형식(`## {Section}\\n`)을 그대로 검색할 뿐, 각 절의
    내용을 해석하지 않는다. Artifact Mapping 검증(손실 여부 확인)을 위한
    보조 함수이며, `build_execution_request()`의 변환 경로에는 관여하지
    않는다 — 변환 자체는 이 함수 없이도 동일하게 동작한다.
    """
    return {section: f"## {section}\n" in text for section in KNOWN_SECTIONS}
