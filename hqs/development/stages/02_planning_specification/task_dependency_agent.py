"""Stage 02 Task & Dependency Agent — PRD를 Task로 구조화하고 Task 간
Dependency를 판단하는 단일 Engine 호출(RFC-0035/ADC-0038/ADR-0023 Decision 2).
Task Decomposition과 Dependency Judgment를 별도 Agent로 쪼개지 않는다. 이
모듈은 Engine 호출과 JSON 추출만 담당하고, tasks/dependencies의 스키마·구조
검증은 `planning_pipeline.py`(Deterministic Layer)가 별도로 수행한다.
Multi-Engine Architecture(`ADR-0024`) 이후 이 Reasoning 목적 호출은
ChatGPT Engine을 사용한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.chatgpt_engine import call_engine_via_chatgpt as call_engine  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "01_context_analysis"))

from reasoning import AgentOutputError, parse_structured_output  # noqa: E402

__all__ = ["AgentOutputError", "decompose_tasks_and_dependencies"]

_INSTRUCTION = (
    "You are the Task & Dependency Agent in a software development planning "
    "pipeline. Given a PRD/specification below, decompose it into concrete "
    "implementation tasks and judge the dependency relationships between "
    "them. Do not invent dependencies that are not implied by the "
    "specification — leave a task independent unless another task's output "
    "is clearly required first.\n\n"
    "Respond with a single JSON object only (no prose, no markdown fences) "
    "with exactly these two keys:\n"
    '- "tasks": a list of objects, each with "id" (short unique string), '
    '"title", and "description".\n'
    '- "dependencies": a list of objects, each with "task" (id of the '
    'dependent task) and "depends_on" (id of the task it depends on).\n\n'
    "Specification:\n{specification}"
)


def decompose_tasks_and_dependencies(specification: str) -> dict:
    """Task & Dependency Agent를 1회 호출해 원시 JSON(dict)을 반환한다.
    JSON으로 파싱 불가능한 응답만 `AgentOutputError`로 처리하고,
    tasks/dependencies의 키·타입 검증은 하지 않는다(Deterministic Layer 책임)."""
    prompt = _INSTRUCTION.format(specification=specification)
    raw = call_engine(prompt)
    return parse_structured_output(raw)
