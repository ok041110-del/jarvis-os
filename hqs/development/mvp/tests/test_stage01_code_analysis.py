"""Stage 01 Code Analysis Executors 검증(`stages/01_context_analysis/
code_analysis.py`) — Structure/Relevant Discovery/AST Candidate 3종을
가짜 RepositorySnapshot + fetch_content로 검증한다(실제 GitHub API 호출
없음). Dependency Analysis(target 조건부)와 Context Aggregator도 확인."""

import importlib.util
import sys
from pathlib import Path

_CODE_ANALYSIS_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "code_analysis.py"
_spec = importlib.util.spec_from_file_location("code_analysis", _CODE_ANALYSIS_PATH)
code_analysis = importlib.util.module_from_spec(_spec)
sys.modules["code_analysis"] = code_analysis
_spec.loader.exec_module(code_analysis)

from mvp.github_adapter import RepositoryEntry, RepositorySnapshot  # noqa: E402

ROOT = code_analysis.ROOT
SAMPLE_ISSUE = {"title": "validate_issue behavior", "description": "Check validate_issue handling."}


def _rel(path) -> str:
    return str(path.relative_to(ROOT))


def _make_snapshot() -> RepositorySnapshot:
    mvp_dir = ROOT / "hqs" / "development" / "mvp"
    tree = [
        RepositoryEntry(path=_rel(mvp_dir / "project_intelligence.py"), type="blob", size=100, sha="s1"),
        RepositoryEntry(path=_rel(mvp_dir / "engine.py"), type="blob", size=50, sha="s2"),
        RepositoryEntry(path="docs/01_mvp/MVP-0001.md", type="blob", size=10, sha="s3"),
        RepositoryEntry(path="docs/01_mvp", type="tree", size=None, sha="s4"),
    ]
    return RepositorySnapshot(owner="o", name="r", ref="main", commit_sha="sha", tree=tree, files=[])


def test_structure_analysis_lists_tree_paths_sorted():
    snapshot = _make_snapshot()

    result = code_analysis.structure_analysis(snapshot)

    assert result == sorted(entry.path for entry in snapshot.tree)


def test_relevant_discovery_keeps_eight_key_contract():
    snapshot = _make_snapshot()

    def fetch_content(path):
        return "def validate_issue(issue): pass"

    result = code_analysis.relevant_discovery(snapshot, fetch_content, SAMPLE_ISSUE, {"keywords": [], "scope_candidates": []})

    assert set(result.keys()) == {
        "issue", "goal", "relevant_documents", "relevant_code",
        "relevant_observations", "relevant_decisions", "known_constraints", "open_questions",
    }
    assert result["issue"] == SAMPLE_ISSUE


def test_relevant_discovery_scores_by_keyword_match_in_content():
    snapshot = _make_snapshot()
    project_intel_path = _rel(ROOT / "hqs" / "development" / "mvp" / "project_intelligence.py")
    engine_path = _rel(ROOT / "hqs" / "development" / "mvp" / "engine.py")

    def fetch_content(path):
        if path == project_intel_path:
            return "def validate_issue(issue): pass"
        if path == engine_path:
            return "def call_engine(prompt): pass"
        return None

    result = code_analysis.relevant_discovery(snapshot, fetch_content, SAMPLE_ISSUE, {"keywords": [], "scope_candidates": []})

    assert project_intel_path in result["relevant_code"]
    assert engine_path not in result["relevant_code"]


def test_relevant_discovery_never_fetches_files_outside_matched_categories():
    snapshot = _make_snapshot()
    fetched = []

    def fetch_content(path):
        fetched.append(path)
        return None

    code_analysis.relevant_discovery(snapshot, fetch_content, SAMPLE_ISSUE, {"keywords": [], "scope_candidates": []})

    assert "docs/01_mvp" not in fetched  # tree 타입(디렉토리)은 fetch 대상이 아니다


def test_ast_candidate_analysis_reuses_existing_ast_context_logic():
    snapshot = _make_snapshot()
    path = _rel(ROOT / "hqs" / "development" / "mvp" / "project_intelligence.py")

    def fetch_content(fetch_path):
        if fetch_path == path:
            return "def validate_issue(issue: dict) -> None:\n    \"\"\"docstring line.\"\"\"\n    pass\n"
        return None

    result = code_analysis.ast_candidate_analysis(snapshot, fetch_content)

    assert f"FILE: {path}" in result
    assert "FUNCTION: def validate_issue(issue: dict) -> None" in result
    assert "docstring line." in result


def test_ast_candidate_analysis_skips_files_with_no_content():
    snapshot = _make_snapshot()

    result = code_analysis.ast_candidate_analysis(snapshot, lambda path: None)

    assert result == ""


def test_dependency_analysis_reuses_local_build_dependency_closure():
    result = code_analysis.dependency_analysis(("agents.backend", "_strip_code_fence"))

    assert "def _strip_code_fence(text: str) -> str:" in result


def test_aggregate_context_produces_contract_shape_unchanged():
    result = code_analysis.aggregate_context(
        directory_structure=["a"], context_bundle={"issue": {}}, candidate_index="IDX",
        target=None, dependency_closure=None,
    )

    assert result == {
        "directory_structure": ["a"], "context_bundle": {"issue": {}}, "candidate_index": "IDX",
        "target": None, "dependency_closure": None,
    }
