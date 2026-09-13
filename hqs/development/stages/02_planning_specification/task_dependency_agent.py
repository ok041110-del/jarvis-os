"""Stage 02 Task & Dependency Agent(RFC-0035/ADC-0038/ADR-0023 Decision 2) — Task Decomposition과 Dependency Judgment를 별도 Agent로 쪼개지 않는다. 스키마 검증은 `planning_pipeline.py`(Deterministic Layer) 책임이다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.openrouter_engine import call_engine_via_openrouter as call_engine  # noqa: E402

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
    """JSON 파싱 불가능한 응답만 `AgentOutputError`로 처리한다 — 키·타입
    검증은 하지 않는다(Deterministic Layer 책임)."""
    prompt = _INSTRUCTION.format(specification=specification)
    raw = call_engine(prompt)
    return parse_structured_output(raw)
