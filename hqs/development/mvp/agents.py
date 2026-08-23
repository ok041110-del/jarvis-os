"""Agent-Capability 매핑과 Agent 함수.
AGENT_CAPABILITY_MAP은 리터럴 딕셔너리로 고정 — Registry로 일반화하지 않는다(IMPLEMENTATION_RULES.md, HANDOVER.md Stop Trigger)."""

from .engine import call_engine

AGENT_CAPABILITY_MAP = {
    "code_review": "Backend Agent",
    "test_execution": "QA Agent",
}

# Hello SDLC 전용 별도 딕셔너리 — AGENT_CAPABILITY_MAP을 2개 항목으로
# 고정 검증하는 test_mvp_0001.py를 깨지 않기 위해 확장하지 않는다.
HELLO_SDLC_CAPABILITY_MAP = {
    "requirement_analysis": "Requirements Agent",
    "design": "Design Agent",
    "code_generation": "Backend Agent",
}


NO_ISSUES_MARKER = "NO_ISSUES_FOUND"


def backend_agent_code_review(code: str) -> str:
    """`NO_ISSUES_MARKER`는 `workflow_0002.py`의 분기 판단 신호로 쓰인다 —
    실이슈가 없을 때만 응답 끝에 정확히 적도록 지시한다."""
    instruction = (
        "Review the following code and describe issues in prose "
        "(bugs, risks, style) — do not rewrite or restate the code as your answer. "
        "You are shown only this single file, not the rest of the project. "
        "For every `from .module import Name`-style relative import, you cannot "
        "verify that `module` actually exists as a sibling file or that `Name` is "
        "actually defined there — explicitly call out each such import as an "
        "unverified assumption that must be checked against the real project "
        "files, and say so even if the import looks syntactically fine. "
        "Respond entirely in English, regardless of the language used in the "
        "code's comments or identifiers. "
        "A real issue is a concrete defect that would cause wrong output, a "
        "crash, or a violation of the function's own stated behavior — "
        "improvement ideas (add validation, add tests, add docs, style "
        "preferences) are not real issues by themselves. "
        f"If and only if you find no real issues by that definition, end "
        f"your response with the exact line: {NO_ISSUES_MARKER}"
    )
    return call_engine(f"CODE_REVIEW:{instruction}\n\n{code}")


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent의 test_execution Capability(테스트 케이스 제안, MVP-0025)."""
    instruction = (
        "Based on the following code and its review, propose a list of "
        "test cases to add — do not review the code again."
    )
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{instruction}\n\n{payload}")


def requirements_agent_requirement_analysis(issue: dict) -> str:
    """리터럴 마커만으로는 Engine이 의도를 놓치고 코드를 바로 작성하는 등의
    사례가 있어 한 문장짜리 지시를 앞에 붙인다."""
    instruction = (
        "Analyze the following feature request and describe the "
        "requirement in prose (goal, scope, risks) — do not write code."
    )
    payload = f"{issue['title']}|||{issue['description']}"
    return call_engine(f"REQUIREMENT_ANALYSIS:{instruction}\n\n{payload}")


def design_agent_design(issue: dict, requirement: str) -> str:
    """Design Agent가 design Capability를 수행한다. 지시 문장의 목적은
    `requirements_agent_requirement_analysis`와 같다."""
    instruction = (
        "Based on the following requirement, describe a design in prose "
        "(approach, responsibilities, risks) — do not write code yet."
    )
    payload = f"{issue['title']}\n---REQUIREMENT---\n{requirement}"
    return call_engine(f"DESIGN:{instruction}\n\n{payload}")


def _strip_code_fence(text: str) -> str:
    """Engine이 "코드만 반환" 지시에도 마크다운 fence로 감쌀 수 있어 벗긴다
    — 정확히 감싸진 형태만 벗기고 그 외엔 원문을 유지한다."""
    lines = text.strip().splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1])
    return text


def backend_agent_code_generation(design: str) -> str:
    """Backend Agent의 code_generation Capability — 코드만 반환하도록 지시하고
    `_strip_code_fence`로 마크다운 fence를 벗긴다."""
    instruction = (
        "Based on the following design, write the implementation code. "
        "Return only the code, with no surrounding commentary."
    )
    code = call_engine(f"CODE_GENERATION:{instruction}\n\n{design}")
    return _strip_code_fence(code)
