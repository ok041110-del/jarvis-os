"""Stage 01~05 공통 Fixture — 이전 세션(`OPENROUTER-STAGE-MODEL-
SELECTION-0001.md`)이 이미 실측에 쓴 것과 동일한 시나리오("Add input
validation to code review agent")를 그대로 재사용한다(새 시나리오
발명 없음, 비교 가능성 유지). Production 파일은 읽기만 한다."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TARGET_RELATIVE_PATH = "hqs/development/mvp/agents/backend.py"
TARGET_FUNCTION_NAME = "backend_agent_code_review"

STAGE01_PROMPT = """You are the Requirement Agent. Extract functional requirements, non-functional requirements, constraints, and scope candidates (as general topic/keyword strings, NOT repository file paths) from the request below.

Respond with a single JSON object only (no prose, no markdown fences) containing exactly these keys: ['functional_requirements', 'non_functional_requirements', 'constraints', 'scope_candidates', 'confidence']. "confidence" must be a number between 0 and 1.

Title: Add input validation to code review agent
Description: Users can call backend_agent_code_review with an empty string or a non-code text blob. Currently this produces a confusing engine response instead of a clear validation error. We need requirements for detecting invalid input before calling the Engine.
"""

STAGE02_PROMPT = """You are the Task & Dependency Agent in a software development planning pipeline. Given a PRD/specification below, decompose it into concrete implementation tasks and judge the dependency relationships between them. Do not invent dependencies that are not implied by the specification — leave a task independent unless another task's output is clearly required first.

Respond with a single JSON object only (no prose, no markdown fences) with exactly these two keys:
- "tasks": a list of objects, each with "id" (short unique string), "title", and "description".
- "dependencies": a list of objects, each with "task" (id of the dependent task) and "depends_on" (id of the task it depends on).

Specification:
Implement input validation for backend_agent_code_review: reject empty or non-string code input with a clear ValueError before calling the Engine. Add a corresponding unit test that exercises both the empty-string case and the non-string case. Update the function's docstring to document the new validation behavior.
"""

STAGE03_PROMPT = """DESIGN:Based on the following requirement, describe a design in prose (approach, responsibilities, risks) — do not write code yet.

Add input validation to code review agent
---REQUIREMENT---
Implement input validation for backend_agent_code_review: reject empty or non-string code input with a clear ValueError before calling the Engine. Add a corresponding unit test that exercises both the empty-string case and the non-string case. Update the function's docstring to document the new validation behavior.

[Architecture Design Skeleton]
Below is this task's Design skeleton (Component Candidates/Implementation Scope Candidates/Constraints/Risks). Reflect this skeleton's content while also including Architecture Definition, Component Identification, Responsibility Allocation, Interface/Contract Identification, Data Flow, and Implementation Strategy in the Architecture/Design you write.

[Component Candidates]
backend_agent_code_review (hqs/development/mvp/agents/backend.py)

[Implementation Scope Candidates]
hqs/development/mvp/agents/backend.py

[Constraints]
Must not change the function's external contract (str -> str), must not add filesystem/network access, must not modify call_engine_review's signature

[Risks]
Overly strict validation could reject valid code containing only whitespace/comments; ValueError message wording could leak internal details
"""

_EXPOSURE_POLICY_INSTRUCTION = (
    "You are extending exactly one existing function, `backend_agent_code_review`, "
    "in the file below. Add code only inside that function's existing body — do "
    "not create a new function, and do not change any other function, import, or "
    "whitespace in this file for any reason. Return the complete file content "
    "with only that one change applied."
)

_STAGE04_DESIGN_TEXT = (
    "Add input validation to backend_agent_code_review: if `code` is not a "
    "non-empty string (after stripping whitespace), raise `ValueError` with a "
    "clear message before calling the Engine. Keep the existing review "
    "instruction and function behavior otherwise unchanged. Update the "
    "function's docstring to mention the new validation."
)


def build_stage04_prompt(repo_root: Path = REPO_ROOT) -> str:
    """Production 파일을 읽기만 해서(쓰지 않음) 실제 Exposure Policy
    프롬프트를 구성한다 — 하드코딩 사본을 두지 않아 원본과 드리프트하지
    않는다."""
    target_source = (repo_root / TARGET_RELATIVE_PATH).read_text(encoding="utf-8")
    build_input = (
        f"{_STAGE04_DESIGN_TEXT}\n\n---TARGET FILE (agents/backend.py, full content)---\n"
        f"{target_source}\n\n---INSTRUCTION---\n{_EXPOSURE_POLICY_INSTRUCTION}"
    )
    instruction = "Based on the following design, write the implementation code. Return only the code, with no surrounding commentary."
    return f"CODE_GENERATION:{instruction}\n\n{build_input}"


def build_stage05_review_prompt(repo_root: Path = REPO_ROOT) -> str:
    """Stage 05 Review(advisory, experimental) 프롬프트 — 이전 세션
    (`STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md`)의 Input
    경계(Design/Implementation/Contract/Scope/Immutable Source
    Snapshot)를 그대로 재사용한다."""
    original_source = (repo_root / TARGET_RELATIVE_PATH).read_text(encoding="utf-8")
    instruction = (
        "You are the Review capability of a validation pipeline. Review the "
        "following code and describe issues in prose (bugs, risks, style) — "
        "do not rewrite or restate the code as your answer. A real issue is "
        "a concrete defect that would cause wrong output, a crash, or a "
        "violation of the function's own stated behavior."
    )
    contract_description = (
        "External Contract: the reviewed function must remain `str -> str`, "
        "with failures surfaced as a single exception type."
    )
    scope_description = f"Scope Context (files this change is allowed to touch): {TARGET_RELATIVE_PATH}"
    return (
        f"{instruction}\n\n---STAGE 03 DESIGN---\n{_STAGE04_DESIGN_TEXT}\n\n"
        f"---CONTRACT---\n{contract_description}\n\n---SCOPE CONTEXT---\n{scope_description}\n\n"
        f"---IMMUTABLE SOURCE SNAPSHOT---\n{original_source}\n\n"
        f"---STAGE 04 IMPLEMENTATION (already validated separately)---\n"
        f"(same implementation validated in the Stage 04 run of this experiment)"
    )
