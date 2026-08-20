"""Characterization tests for `mvp.workflow_0008.run_pipeline` (P1-2).

Production code(`workflow_0008.py`)는 수정하지 않았다. 모든 외부
의존성(Project Intelligence, Agent 호출)은 mock/stub해 결정적으로
테스트한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_0008

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_CONTEXT = {"relevant_documents": ["doc.md"]}
SAMPLE_ENRICHED_ISSUE = {**SAMPLE_ISSUE, "description": "Do the thing.\n\n[Relevant Context]\ndoc.md"}


def _patch_pre_try_deps(monkeypatch):
    monkeypatch.setattr(workflow_0008, "collect_relevant_context", lambda issue: SAMPLE_CONTEXT)
    monkeypatch.setattr(workflow_0008, "_enrich_issue", lambda issue, context: SAMPLE_ENRICHED_ISSUE)


def test_happy_path_returns_all_five_keys_in_order(monkeypatch):
    _patch_pre_try_deps(monkeypatch)
    monkeypatch.setattr(workflow_0008, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")
    monkeypatch.setattr(workflow_0008, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_0008, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_0008, "backend_agent_code_review", lambda code: "REVIEW")
    monkeypatch.setattr(workflow_0008, "qa_agent_test_execution", lambda code, review: "TESTS")

    result = workflow_0008.run_pipeline(SAMPLE_ISSUE)

    assert list(result.keys()) == ["context", "planning", "design", "implementation", "validation"]
    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "REQUIREMENT",
        "design": "DESIGN",
        "implementation": "CODE",
        "validation": {"code_review": "REVIEW", "test_execution": "TESTS"},
    }


def test_requirement_analysis_receives_enriched_issue_design_receives_original(monkeypatch):
    """Docstring이 명시한 계약: Planning은 enriched_issue를, Design은
    원본 issue를 받는다."""
    _patch_pre_try_deps(monkeypatch)
    seen = {}

    def fake_requirement(issue):
        seen["requirement_input"] = issue
        return "REQUIREMENT"

    def fake_design(issue, req):
        seen["design_input"] = issue
        return "DESIGN"

    monkeypatch.setattr(workflow_0008, "requirements_agent_requirement_analysis", fake_requirement)
    monkeypatch.setattr(workflow_0008, "design_agent_design", fake_design)
    monkeypatch.setattr(workflow_0008, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_0008, "backend_agent_code_review", lambda code: "REVIEW")
    monkeypatch.setattr(workflow_0008, "qa_agent_test_execution", lambda code, review: "TESTS")

    workflow_0008.run_pipeline(SAMPLE_ISSUE)

    assert seen["requirement_input"] == SAMPLE_ENRICHED_ISSUE
    assert seen["design_input"] == SAMPLE_ISSUE


def test_engine_failure_preserves_precomputed_context_and_fills_error_everywhere(monkeypatch):
    _patch_pre_try_deps(monkeypatch)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_0008, "requirements_agent_requirement_analysis", raising_requirement)

    result = workflow_0008.run_pipeline(SAMPLE_ISSUE)

    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "Engine call failed: boom",
        "design": "Engine call failed: boom",
        "implementation": "Engine call failed: boom",
        "validation": {
            "code_review": "Engine call failed: boom",
            "test_execution": "Engine call failed: boom",
        },
    }


def test_engine_failure_later_in_chain_still_produces_full_error_shape(monkeypatch):
    """실패 지점이 마지막 단계(test_execution)여도 반환 계약(5개 키,
    validation은 2개 키)은 동일하게 유지된다."""
    _patch_pre_try_deps(monkeypatch)
    monkeypatch.setattr(workflow_0008, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")
    monkeypatch.setattr(workflow_0008, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_0008, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_0008, "backend_agent_code_review", lambda code: "REVIEW")

    def raising_test_execution(code, review):
        raise TimeoutError("timed out")

    monkeypatch.setattr(workflow_0008, "qa_agent_test_execution", raising_test_execution)

    result = workflow_0008.run_pipeline(SAMPLE_ISSUE)

    assert list(result.keys()) == ["context", "planning", "design", "implementation", "validation"]
    assert result["context"] == SAMPLE_CONTEXT
    assert result["planning"] == "Engine call failed: timed out"
    assert result["validation"] == {
        "code_review": "Engine call failed: timed out",
        "test_execution": "Engine call failed: timed out",
    }
