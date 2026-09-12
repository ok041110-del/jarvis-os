"""GitHubRepositoryAdapter — GitHub REST API를 호출해 분석에 필요한 데이터를
RepositorySnapshot으로 변환한다(§6/§7). Architecture상 Repository 접근 방법은
GitHub REST API로 한정한다 — GraphQL/Search/Issues/PR/Actions/Commit History
API는 이번 구현 범위 밖이다. 인증은 환경변수(`GITHUB_TOKEN`)로만 받는다 —
코드/테스트 fixture에 하드코드하지 않고, Architecture/Public Contract에도
포함하지 않는다."""

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

GITHUB_API_BASE_URL = "https://api.github.com"
DEFAULT_TIMEOUT_SECONDS = 30.0
# 과도하게 큰 파일은 일반 text file처럼 content를 채우지 않는다(§7).
MAX_FILE_BYTES = 200_000


class GitHubAdapterError(RuntimeError):
    """GitHub REST API 호출 실패 또는 예상치 못한 응답 형태."""


@dataclass
class RepositoryEntry:
    path: str
    type: str  # "blob" | "tree"
    size: Optional[int]
    sha: str


@dataclass
class RepositoryFile:
    path: str
    content: Optional[str]
    size: int
    sha: str
    truncated: bool = False


@dataclass
class RepositorySnapshot:
    owner: str
    name: str
    ref: str
    commit_sha: str
    tree: list = field(default_factory=list)
    files: list = field(default_factory=list)

    def file_by_path(self, path: str) -> Optional[RepositoryFile]:
        return next((f for f in self.files if f.path == path), None)


class GitHubRepositoryAdapter:
    """최소 API 범위(§6): 저장소 Metadata, 재귀 Tree, 개별 파일 Contents."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = GITHUB_API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self._token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _request(self, path: str) -> dict:
        url = f"{self._base_url}{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "jarvis-os-development-hq-context-analysis",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read()[:200]
            raise GitHubAdapterError(f"GitHub API error {exc.code} for {path}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAdapterError(f"GitHub API request failed for {path}: {exc}") from exc

    def get_repository_metadata(self, owner: str, repo: str) -> dict:
        return self._request(f"/repos/{owner}/{repo}")

    def get_tree(self, owner: str, repo: str, tree_sha_or_ref: str) -> tuple:
        """`(commit_sha_or_ref, RepositoryEntry[])`를 반환한다. `truncated`
        응답은 안전하게 인식만 하고(전체 트리로 오인하지 않음) 받은 항목만
        사용한다 — 이 저장소 규모에서는 실제로 truncated되지 않는다."""
        data = self._request(f"/repos/{owner}/{repo}/git/trees/{tree_sha_or_ref}?recursive=1")
        entries = [
            RepositoryEntry(path=entry["path"], type=entry["type"], size=entry.get("size"), sha=entry["sha"])
            for entry in data.get("tree", [])
            if entry["type"] == "blob"
        ]
        return data.get("sha", tree_sha_or_ref), entries

    def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> RepositoryFile:
        data = self._request(f"/repos/{owner}/{repo}/contents/{path}?ref={ref}")
        if isinstance(data, list):
            raise GitHubAdapterError(f"{path} is a directory, not a file")
        size = data.get("size", 0)
        sha = data.get("sha", "")
        if data.get("encoding") != "base64" or size > MAX_FILE_BYTES:
            return RepositoryFile(path=path, content=None, size=size, sha=sha, truncated=True)
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            # binary 파일은 일반 text file처럼 처리하지 않는다(§7).
            return RepositoryFile(path=path, content=None, size=size, sha=sha, truncated=True)
        return RepositoryFile(path=path, content=content, size=size, sha=sha, truncated=False)

    def build_snapshot(self, owner: str, repo: str, ref: Optional[str], paths_to_fetch: list) -> RepositorySnapshot:
        """§7 순서: Repository Metadata → Repository Tree → (호출자가 결정한)
        Relevant Paths → Required File Contents. Repository 전체 파일을
        무조건 preload하지 않는다 — `paths_to_fetch`에 있는 파일만 fetch."""
        metadata = self.get_repository_metadata(owner, repo)
        resolved_ref = ref or metadata.get("default_branch", "main")
        commit_sha, tree = self.get_tree(owner, repo, resolved_ref)
        files = [self.get_file_content(owner, repo, path, resolved_ref) for path in paths_to_fetch]
        return RepositorySnapshot(
            owner=owner, name=repo, ref=resolved_ref, commit_sha=commit_sha,
            tree=tree, files=files,
        )
