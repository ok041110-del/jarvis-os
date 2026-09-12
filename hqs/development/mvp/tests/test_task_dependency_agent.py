"""Stage 02 Task & Dependency Agent(`task_dependency_agent.py`) 검증(RFC-0035/
ADC-0038/ADR-0023 Decision 2) — Engine 호출 자체는 mock하고, JSON 추출/파싱
동작만 확인한다(스키마 검증은 `planning_pipeline.py` 책임이라 여기서는
검사하지 않는다)."""

import importlib.util
import sys
from pathlib import Path

import pytest

_STAGE_DIR = Path(__file__).resolve().parents[2] / "stages"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reasoning = _load("reasoning", _STAGE_DIR / "01_context_analysis" / "reasoning.py")
task_dependency_agent = _load(
    "task_dependency_agent", _STAGE_DIR / "02_planning_specification" / "task_dependency_agent.py"
)


def test_decompose_tasks_and_dependencies_parses_json_response(monkeypatch):
    raw = '{"tasks": [{"id": "a", "title": "A", "description": "do a"}], "dependencies": []}'
    monkeypatch.setattr(task_dependency_agent, "call_engine", lambda prompt: raw)

    result = task_dependency_agent.decompose_tasks_and_dependencies("SPEC TEXT")

    assert result == {"tasks": [{"id": "a", "title": "A", "description": "do a"}], "dependencies": []}


def test_decompose_tasks_and_dependencies_strips_markdown_fence(monkeypatch):
    raw = '```json\n{"tasks": [], "dependencies": []}\n```'
    monkeypatch.setattr(task_dependency_agent, "call_engine", lambda prompt: raw)

    result = task_dependency_agent.decompose_tasks_and_dependencies("SPEC TEXT")

    assert result == {"tasks": [], "dependencies": []}


def test_decompose_tasks_and_dependencies_raises_on_non_json_response(monkeypatch):
    monkeypatch.setattr(task_dependency_agent, "call_engine", lambda prompt: "not json at all")

    with pytest.raises(task_dependency_agent.AgentOutputError):
        task_dependency_agent.decompose_tasks_and_dependencies("SPEC TEXT")


def test_decompose_tasks_and_dependencies_passes_specification_into_prompt(monkeypatch):
    captured = {}

    def _fake_call_engine(prompt):
        captured["prompt"] = prompt
        return '{"tasks": [], "dependencies": []}'

    monkeypatch.setattr(task_dependency_agent, "call_engine", _fake_call_engine)

    task_dependency_agent.decompose_tasks_and_dependencies("UNIQUE SPEC MARKER")

    assert "UNIQUE SPEC MARKER" in captured["prompt"]
