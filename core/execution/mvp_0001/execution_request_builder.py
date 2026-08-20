"""Execution Layer MVP-0001: ExecutionRequestBuilder.

Implementation Specification(Development HQ 산출물)을 Execution
Request로 변환한다. Transformation만 수행하고 Interpretation(해석·
요약·재구성)은 하지 않는다 — 입력을 한 글자도 바꾸지 않고 머리말만
붙인다. Contract 상세: docs/core/execution-layer/MVP-0001-plan.md
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

    입력 텍스트를 변경하지 않고 머리말만 붙인다(Deterministic).
    """
    return f"{EXECUTION_REQUEST_HEADER}{implementation_specification}"


def find_known_sections(text: str) -> dict:
    """`## {Section}` 마커로 시작하는 8개 알려진 절의 존재 여부만 확인한다.

    Artifact Mapping 검증용 보조 함수이며 `build_execution_request()`의
    변환 경로에는 관여하지 않는다.
    """
    return {section: f"## {section}\n" in text for section in KNOWN_SECTIONS}
