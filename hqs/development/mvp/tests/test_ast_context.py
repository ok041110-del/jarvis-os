from pathlib import Path

import pytest

from ..ast_context import build_dependency_closure, build_function_candidate_index

_MVP_DIR = Path(__file__).resolve().parents[1]


def test_candidate_index_lists_known_function_signature_and_docstring():
    index = build_function_candidate_index()
    assert "FILE: hqs/development/mvp/project_intelligence.py" in index
    assert "FUNCTION: def validate_issue(issue: dict) -> None" in index
    assert "`title`/`description`만 필수 Issue 필드로 검사한다." in index


def test_candidate_index_has_no_function_body():
    index = build_function_candidate_index()
    # validate_issue의 실제 본문 한 줄(raise 문)이 인덱스에 없어야 한다 —
    # 시그니처+docstring 첫 줄만 담고 본문은 담지 않는다는 계약을 검증한다.
    assert "missing = [" not in index


def test_candidate_index_lists_class_candidates():
    index = build_function_candidate_index()
    assert "CLASS: IssueValidationError" in index


def test_closure_single_module_contains_target_only_dependencies():
    """`_strip_code_fence`는 Agent Package Refactoring으로 `agents/backend.py`
    (dotted: `agents.backend`)에 있다(ADC-0006 Condition 6, 실제 파일 이동에
    직접 필요한 literal 변경)."""
    closure = build_dependency_closure("agents.backend", "_strip_code_fence")
    assert "# module: agents.backend" in closure
    assert "def _strip_code_fence(text: str) -> str:" in closure
    # 다른 모듈을 참조하지 않는 함수이므로 폐쇄는 단일 모듈이어야 한다.
    assert "# module: engine" not in closure


def test_closure_includes_referenced_class_in_same_module():
    closure = build_dependency_closure("project_intelligence", "validate_issue")
    assert "def validate_issue(issue: dict) -> None:" in closure
    assert "class IssueValidationError(ValueError):" in closure


def test_closure_follows_relative_imports_across_modules():
    """Agent Package Refactoring 이후 `requirements_agent_requirement_analysis`/
    `design_agent_design`는 각각 `agents.requirements`/`agents.design`에
    있다 — T18 Evidence 당시의 단일 `agents` 모듈은 이제 2개로 나뉜다
    (ADC-0006 Condition 6)."""
    closure = build_dependency_closure("workflow_project_intelligence", "run_issue_to_design")
    for module in (
        "workflow_project_intelligence",
        "agents.design",
        "agents.requirements",
        "engine",
        "project_intelligence",
        "workflow",
    ):
        assert f"# module: {module}" in closure


def test_closure_is_smaller_than_full_source_for_multi_module_case():
    closure = build_dependency_closure("workflow_project_intelligence", "run_issue_to_design")
    modules = (
        "agents/design.py",
        "agents/requirements.py",
        "engine.py",
        "project_intelligence.py",
        "workflow.py",
        "workflow_project_intelligence.py",
    )
    full_source_total = sum(len((_MVP_DIR / name).read_text(encoding="utf-8")) for name in modules)
    assert len(closure) < full_source_total


def test_closure_raises_for_unknown_target():
    with pytest.raises(ValueError):
        build_dependency_closure("agents", "_does_not_exist")
