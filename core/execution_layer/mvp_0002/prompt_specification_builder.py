"""Execution Layer MVP-0002: PromptSpecificationBuilder.

Execution Request(Execution Layer MVP-0001의 Canonical Artifact)를
Prompt Specification(AI 모델이 읽기 쉬운 구조로 Rendering된 두 번째
공식 Artifact)으로 변환한다.

Contract (요청 원문 기준):
- Input: Execution Request (`str`, MVP-0001 `build_execution_request()`가
  생성하는 형태: `"# Execution Request\n\n"` 머리말 + Implementation
  Specification의 8개 항목 + Reference Design).
- Output: Prompt Specification (`str`).
- Execution Request는 Canonical Artifact다. 이 모듈은 그 정보를 재배치
  (Rendering)할 뿐, Execution Request를 대체하거나 변경하지 않는다.
- Interpretation(의미 해석)을 수행하지 않는다. Transformation은
  "어느 절을 어느 절 아래로 옮길지"를 정하는 고정된 배치표
  (`RENDERING_MAP`) 하나로 최소화한다 — 각 절의 본문 텍스트는 한 글자도
  바꾸지 않는다.
- AI/LLM/Model 호출 없음. Prompt 실행 없음. Session/Runtime/Model
  Connector/Retry/Cost 관리 없음.
"""

import re

# Execution Request(및 원본 Implementation Specification)가 실제로 갖는
# 절 이름과 순서. `development-hq/mvp/engine.py` `_generate_code()`와
# `core/execution_layer/mvp_0001/execution_request_builder.py`가 만드는
# 형태를 그대로 따른다 — 이 모듈은 그 두 코드를 수정하지 않는다.
SOURCE_SECTIONS_IN_ORDER = (
    "Target File",
    "Public Interface",
    "Functions",
    "Classes",
    "Dependencies",
    "Algorithm Outline",
    "Edge Cases",
    "Validation Notes",
    "Reference Design",
)

# Prompt Structure — 요청에 명시된 5개 절, 이 순서 그대로.
PROMPT_SECTIONS_IN_ORDER = (
    "Mission",
    "Input",
    "Constraints",
    "Expected Output",
    "Validation Notes",
)

# Rendering Map: Execution Request의 9개 절(8개 항목 + Reference Design)을
# Prompt Structure의 5개 절에 정확히 1:1로 배정한다. 이 맵이 유일한 배치
# 규칙이다 — 절 이름 배정 외에 어떤 내용도 새로 만들지 않는다.
#
#   Mission          <- Target File, Public Interface
#     (무엇을, 어디에 만들 것인지 — Execution Request가 이미 명시한 대상)
#   Input            <- Dependencies, Reference Design
#     (참고해야 할 기존 코드와, 이 요청이 근거한 원본 Design/Requirement/
#      Context 전체)
#   Constraints      <- Classes, Edge Cases
#     (Execution Request가 이미 명시한 제약: 클래스 분해 필요 여부, 처리해야
#      할 경계 조건)
#   Expected Output  <- Functions, Algorithm Outline
#     (구현해야 할 함수 목록과 그 구현 순서)
#   Validation Notes <- Validation Notes
#     (구현 완료 후 확인해야 할 항목 — 이름 그대로 1:1 대응)
RENDERING_MAP = {
    "Target File": "Mission",
    "Public Interface": "Mission",
    "Dependencies": "Input",
    "Reference Design": "Input",
    "Classes": "Constraints",
    "Edge Cases": "Constraints",
    "Functions": "Expected Output",
    "Algorithm Outline": "Expected Output",
    "Validation Notes": "Validation Notes",
}

PROMPT_SPECIFICATION_HEADER = "# Prompt Specification\n\n"


def _extract_section_body(text: str, section: str) -> str:
    """`## {section}\\n` 마커로 시작하는 절의 본문을 그대로 추출한다.

    다음 `## ` 마커(같은 레벨) 전까지를 본문으로 본다. `Reference Design`은
    관례상(MVP-0001 Observation, MVP-0013 Observation) 텍스트 끝까지
    중첩된 하위 문서 전체를 품고 있으므로, 다음 `\\n## ` 경계에서 자르지
    않고 텍스트 끝까지를 본문으로 취급한다. 마커가 없으면 빈 문자열을
    반환한다.
    """
    marker = f"## {section}\n"
    start_idx = text.find(marker)
    if start_idx == -1:
        return ""
    start = start_idx + len(marker)
    if section == "Reference Design":
        return text[start:].rstrip("\n")
    end = text.find("\n## ", start)
    body = text[start:end] if end != -1 else text[start:]
    return body.rstrip("\n")


def build_prompt_specification(execution_request: str) -> str:
    """Execution Request를 Prompt Specification으로 Rendering한다.

    `RENDERING_MAP`에 따라 원본 9개 절(8개 항목 + Reference Design)의
    본문을 5개 Prompt Structure 절 아래로 재배치한다. 각 본문은 원본
    절 이름을 소제목(`## {원본 절 이름}`)으로 유지한 채 그대로 옮겨진다
    — 요약·재해석·새 문장 생성 없음. 동일한 입력은 항상 동일한 출력을
    만든다(Deterministic Rendering).
    """
    grouped: dict[str, list[str]] = {name: [] for name in PROMPT_SECTIONS_IN_ORDER}

    for source_section in SOURCE_SECTIONS_IN_ORDER:
        body = _extract_section_body(execution_request, source_section)
        target_section = RENDERING_MAP[source_section]
        grouped[target_section].append(f"## {source_section}\n{body}")

    rendered_sections = [
        f"# {name}\n\n" + "\n\n".join(grouped[name])
        for name in PROMPT_SECTIONS_IN_ORDER
    ]

    return PROMPT_SPECIFICATION_HEADER + "\n\n".join(rendered_sections)


def find_prompt_sections(text: str) -> dict:
    """텍스트 안에서 `# {Section}` 마커(Prompt Structure 최상위 절)로
    시작하는 5개 알려진 절의 존재 여부만 확인한다.

    "Validation Notes"처럼 최상위 절(`# Validation Notes`)과 원본 소제목
    (`## Validation Notes`)이 같은 이름을 쓰는 경우가 있으므로, 단순
    부분 문자열 검사(`in`)는 `##` 줄도 오탐지한다. 그래서 줄 시작이
    정확히 `# ` 하나로 시작하는 경우만 최상위 절로 인정한다(`^#{1}\\s`
    — `##`은 제외).

    Artifact Mapping 검증을 위한 보조 함수이며,
    `build_prompt_specification()`의 변환 경로에는 관여하지 않는다.
    """
    return {
        section: bool(re.search(rf"(?m)^# {re.escape(section)}\n", text))
        for section in PROMPT_SECTIONS_IN_ORDER
    }
