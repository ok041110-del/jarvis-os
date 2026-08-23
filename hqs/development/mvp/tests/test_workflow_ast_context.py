"""Characterization tests for `mvp.workflow_ast_context` (ADC-0005 §8).

Production code(`workflow_ast_context.py`)는 수정하지 않았다. 모든 외부
의존성(Project Intelligence, Agent 호출, Engine 호출)은 mock/stub해
결정적으로 테스트한다 — `test_workflow_0008.py`와 동일한 패턴.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_ast_context

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_CONTEXT = {"relevant_documents": ["doc.md"]}
SAMPLE_ENRICHED_ISSUE = {**SAMPLE_ISSUE, "description": "Do the thing.\n\n[Relevant Context]\ndoc.md"}


def _patch_pre_try_deps(monkeypatch):
    monkeypatch.setattr(workflow_ast_context, "collect_relevant_context", lambda issue: SAMPLE_CONTEXT)
    monkeypatch.setattr(workflow_ast_context, "_enrich_issue", lambda issue, context: SAMPLE_ENRICHED_ISSUE)


def _patch_pipeline_deps(monkeypatch, build_input_sink=None):
    _patch_pre_try_deps(monkeypatch)
    monkeypatch.setattr(workflow_ast_context, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")
    monkeypatch.setattr(workflow_ast_context, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_ast_context, "identify_target", lambda design: ("agents", "_strip_code_fence"))
    monkeypatch.setattr(workflow_ast_context, "build_dependency_closure", lambda module, function: "CLOSURE")

    def fake_build(build_input):
        if build_input_sink is not None:
            build_input_sink["value"] = build_input
        return "CODE"

    monkeypatch.setattr(workflow_ast_context, "backend_agent_code_generation", fake_build)


def test_happy_path_returns_all_five_keys_including_target(monkeypatch):
    _patch_pipeline_deps(monkeypatch)

    result = workflow_ast_context.run_pipeline_with_ast_context(SAMPLE_ISSUE)

    assert list(result.keys()) == ["context", "planning", "design", "target", "implementation"]
    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "REQUIREMENT",
        "design": "DESIGN",
        "target": ("agents", "_strip_code_fence"),
        "implementation": "CODE",
    }


def test_build_input_concatenates_design_and_closure_without_exposure(monkeypatch):
    sink = {}
    _patch_pipeline_deps(monkeypatch, build_input_sink=sink)

    workflow_ast_context.run_pipeline_with_ast_context(SAMPLE_ISSUE, expose_target=False)

    assert "DESIGN" in sink["value"]
    assert "CLOSURE" in sink["value"]
    assert "TARGET FILE" not in sink["value"]


def test_expose_target_includes_full_file_and_policy_instruction(monkeypatch, tmp_path):
    sink = {}
    _patch_pipeline_deps(monkeypatch, build_input_sink=sink)
    fake_source = "def _strip_code_fence(text):\n    return text\n"
    monkeypatch.setattr(workflow_ast_context, "module_source_path", lambda module: _write_tmp_module(tmp_path, fake_source))

    workflow_ast_context.run_pipeline_with_ast_context(SAMPLE_ISSUE, expose_target=True)

    build_input = sink["value"]
    assert fake_source in build_input
    assert "_strip_code_fence" in build_input
    assert "do not change any other function" in build_input.lower()


def _write_tmp_module(tmp_path, content):
    path = tmp_path / "agents.py"
    path.write_text(content, encoding="utf-8")
    return path


def test_no_target_identified_falls_back_to_design_only(monkeypatch):
    sink = {}
    _patch_pipeline_deps(monkeypatch, build_input_sink=sink)
    monkeypatch.setattr(workflow_ast_context, "identify_target", lambda design: None)

    result = workflow_ast_context.run_pipeline_with_ast_context(SAMPLE_ISSUE)

    assert result["target"] is None
    assert sink["value"] == "DESIGN"


def test_engine_failure_preserves_precomputed_context_and_fills_error_everywhere(monkeypatch):
    _patch_pre_try_deps(monkeypatch)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_ast_context, "requirements_agent_requirement_analysis", raising_requirement)

    result = workflow_ast_context.run_pipeline_with_ast_context(SAMPLE_ISSUE)

    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "Engine call failed: boom",
        "design": "Engine call failed: boom",
        "target": None,
        "implementation": "Engine call failed: boom",
    }


def test_identify_target_parses_file_and_function_lines(monkeypatch):
    monkeypatch.setattr(workflow_ast_context, "build_function_candidate_index", lambda: "INDEX")
    monkeypatch.setattr(workflow_ast_context, "call_engine", lambda prompt: "FILE: agents.py\nFUNCTION: _strip_code_fence")

    assert workflow_ast_context.identify_target("some design") == ("agents", "_strip_code_fence")


def test_identify_target_strips_directory_prefix_from_file_line(monkeypatch):
    """후보 인덱스가 FILE을 저장소 상대 경로로 표기하므로(예:
    hqs/development/mvp/x.py), Engine이 그 경로를 그대로 돌려줘도
    module 이름은 basename만 남아야 한다."""
    monkeypatch.setattr(workflow_ast_context, "build_function_candidate_index", lambda: "INDEX")
    monkeypatch.setattr(
        workflow_ast_context,
        "call_engine",
        lambda prompt: "FILE: hqs/development/mvp/workflow_project_intelligence.py\nFUNCTION: _summarize_context",
    )

    assert workflow_ast_context.identify_target("some design") == ("workflow_project_intelligence", "_summarize_context")


def test_identify_target_returns_none_for_unknown(monkeypatch):
    monkeypatch.setattr(workflow_ast_context, "build_function_candidate_index", lambda: "INDEX")
    monkeypatch.setattr(workflow_ast_context, "call_engine", lambda prompt: "FILE: UNKNOWN\nFUNCTION: UNKNOWN")

    assert workflow_ast_context.identify_target("some design") is None
