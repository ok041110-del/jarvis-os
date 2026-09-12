"""실제 GitHub Repository 검증(§13) — `ok041110-del/jarvis-os`를 대상으로
최소 한 번 실제 RepositorySnapshot 생성과 Code Analysis 실행을 확인한다.
`GITHUB_TOKEN`이 환경변수에 없으면(이 저장소/CI 밖에서 실행하는 경우) skip
한다 — Mock 기반 검증(`test_github_adapter.py`)과 명확히 구분한다. 인증
정보는 이 파일에 하드코드하지 않고 환경변수만 읽는다."""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.github_adapter import GitHubRepositoryAdapter  # noqa: E402

_CODE_ANALYSIS_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "code_analysis.py"
_spec = importlib.util.spec_from_file_location("code_analysis", _CODE_ANALYSIS_PATH)
code_analysis = importlib.util.module_from_spec(_spec)
sys.modules["code_analysis"] = code_analysis
_spec.loader.exec_module(code_analysis)

pytestmark = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not set — real GitHub API validation skipped (see test_github_adapter.py for mock coverage)",
)

OWNER = "ok041110-del"
REPO = "jarvis-os"


def test_real_snapshot_metadata_and_tree_against_jarvis_os():
    adapter = GitHubRepositoryAdapter()
    snapshot = adapter.build_snapshot(OWNER, REPO, ref=None, paths_to_fetch=[])

    assert snapshot.owner == OWNER
    assert snapshot.name == REPO
    assert snapshot.commit_sha
    assert any(entry.path == "hqs/development/mvp/engine.py" for entry in snapshot.tree)


def test_real_structure_and_ast_candidate_analysis_against_jarvis_os():
    adapter = GitHubRepositoryAdapter()
    snapshot = adapter.build_snapshot(OWNER, REPO, ref=None, paths_to_fetch=[])

    structure = code_analysis.structure_analysis(snapshot)
    assert any("hqs/development/mvp" in path for path in structure)

    fetch_cache = {}

    def fetch_content(path):
        if path not in fetch_cache:
            fetch_cache[path] = adapter.get_file_content(OWNER, REPO, path, snapshot.ref).content
        return fetch_cache[path]

    candidate_index = code_analysis.ast_candidate_analysis(snapshot, fetch_content)
    assert "FUNCTION:" in candidate_index
