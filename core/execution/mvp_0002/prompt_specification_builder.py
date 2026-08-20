"""Execution Layer MVP-0002: PromptSpecificationBuilder.

Execution Request를 Prompt Specification(AI 모델이 읽기 쉬운 5개 절
구조)으로 Rendering한다. `RENDERING_MAP`이 유일한 배치 규칙이며, 각
절 본문 텍스트는 한 글자도 바꾸지 않는다(Interpretation 없음).
"""

import re

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

PROMPT_SECTIONS_IN_ORDER = (
    "Mission",
    "Input",
    "Constraints",
    "Expected Output",
    "Validation Notes",
)

# Execution Request의 9개 절을 Prompt Structure의 5개 절로 배정하는
# 유일한 배치 규칙 — 이 맵 외에 어떤 내용도 새로 만들지 않는다.
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

    다음 `## ` 마커 전까지를 본문으로 본다. `Reference Design`은 중첩된
    하위 문서를 포함하므로 예외적으로 텍스트 끝까지를 본문으로 취급한다.
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

    `RENDERING_MAP`에 따라 재배치할 뿐 본문 텍스트는 그대로 옮긴다
    (Deterministic).
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
    """`# {Section}` 마커(최상위 절)로 시작하는 5개 절의 존재 여부를 확인한다.

    `## Validation Notes` 같은 하위 소제목과 구분하기 위해 줄 시작이
    정확히 `# ` 하나인 경우만 인정한다. Artifact Mapping 검증용 보조
    함수이며 `build_prompt_specification()`의 변환 경로에는 관여하지
    않는다.
    """
    return {
        section: bool(re.search(rf"(?m)^# {re.escape(section)}\n", text))
        for section in PROMPT_SECTIONS_IN_ORDER
    }
