"""Backend Agent — code_review/code_generation Capability(Agent Package
Refactoring, `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2)."""

from ..engine import call_engine

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
