"""GitHubRepositoryAdapter/RepositorySnapshot 단위 테스트 — 실제 네트워크
호출 없이 `urllib.request.urlopen`을 대체(mock)해 검증한다. 실제 GitHub API
검증은 `test_github_adapter_real.py`(환경변수 `GITHUB_TOKEN` 없으면 skip)."""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp import github_adapter as gh
from mvp.github_adapter import GitHubAdapterError, GitHubRepositoryAdapter


class _FakeResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def _json_response(data) -> _FakeResponse:
    return _FakeResponse(json.dumps(data).encode("utf-8"))


def test_build_snapshot_uses_metadata_then_tree_then_contents(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        url = request.full_url
        calls.append(url)
        if url.endswith("/repos/o/r"):
            return _json_response({"default_branch": "main"})
        if "/git/trees/main" in url:
            return _json_response({
                "sha": "tree-sha-123",
                "tree": [
                    {"path": "a.py", "type": "blob", "size": 10, "sha": "sha-a"},
                    {"path": "docs", "type": "tree", "size": None, "sha": "sha-docs"},
                ],
            })
        if "/contents/a.py" in url:
            content = base64.b64encode(b"print('hi')").decode("ascii")
            return _json_response({"encoding": "base64", "content": content, "size": 12, "sha": "sha-a"})
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)

    adapter = GitHubRepositoryAdapter(token="x")
    snapshot = adapter.build_snapshot("o", "r", ref=None, paths_to_fetch=["a.py"])

    assert snapshot.owner == "o" and snapshot.name == "r" and snapshot.ref == "main"
    assert snapshot.commit_sha == "tree-sha-123"
    assert [e.path for e in snapshot.tree] == ["a.py"]  # tree 타입은 제외
    assert snapshot.file_by_path("a.py").content == "print('hi')"
    assert any(url.endswith("/repos/o/r") for url in calls)
    assert any("/git/trees/main" in url for url in calls)


def test_get_file_content_marks_binary_as_truncated(monkeypatch):
    def fake_urlopen(request, timeout):
        return _json_response({"encoding": "none", "size": 5000, "sha": "binsha"})

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)
    adapter = GitHubRepositoryAdapter(token="x")
    result = adapter.get_file_content("o", "r", "image.png", "main")

    assert result.content is None
    assert result.truncated is True


def test_get_file_content_marks_oversized_file_as_truncated(monkeypatch):
    def fake_urlopen(request, timeout):
        content = base64.b64encode(b"x" * 10).decode("ascii")
        return _json_response({"encoding": "base64", "content": content, "size": 999_999, "sha": "big"})

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)
    adapter = GitHubRepositoryAdapter(token="x")
    result = adapter.get_file_content("o", "r", "huge.bin", "main")

    assert result.content is None
    assert result.truncated is True


def test_get_file_content_rejects_directory_response(monkeypatch):
    def fake_urlopen(request, timeout):
        return _json_response([{"path": "dir/a.py"}])

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)
    adapter = GitHubRepositoryAdapter(token="x")

    with pytest.raises(GitHubAdapterError):
        adapter.get_file_content("o", "r", "dir", "main")


def test_http_error_wrapped_as_github_adapter_error(monkeypatch):
    import urllib.error

    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)
    adapter = GitHubRepositoryAdapter(token="x")

    with pytest.raises(GitHubAdapterError) as exc_info:
        adapter.get_repository_metadata("o", "missing-repo")
    assert "404" in str(exc_info.value)


def test_authorization_header_uses_env_token_by_default(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "env-token-123")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["auth"] = request.get_header("Authorization")
        return _json_response({"default_branch": "main"})

    monkeypatch.setattr(gh.urllib.request, "urlopen", fake_urlopen)
    adapter = GitHubRepositoryAdapter()  # token 인자 없이 env var로만
    adapter.get_repository_metadata("o", "r")

    assert captured["auth"] == "Bearer env-token-123"
