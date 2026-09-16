"""Dev HQ Command Center — Real Data Snapshot Exporter.

`unified-dashboard/export_snapshot_json.py`와 동일한 패턴이다 — 새 서버
API/Runtime을 추가하지 않고, 이 스크립트를 수동으로 실행해 실제 저장소
상태(File Tree/Git/Dev HQ Workflow 구조/기존 테스트 결과)를 정적 JSON으로
`data/real/`에 내보낸다. Command Center의 `adapters.js`는 이 JSON을
fetch만 한다 — Dashboard 서버(`serve_dashboard.py`)는 무수정이다.

Task별 실행 기록(Changes/Tests/Evidence per task)은 내보내지 않는다 —
`hqs/development/workflow.py`가 영속 저장소 없이 on-demand로만 실행되어
Task ID(#039~042 등, Command Center Mock Task)에 대응하는 실제 실행
기록이 존재하지 않기 때문이다(Real Data Adapter v0.1 조사 결과). 그
탭들은 계속 `data/mock/*.json`을 그대로 쓴다.

재사용(재구현 없음):
- `hqs/development/workflow.py`의 Stage 이름/순서는 새로 읽지 않는다 —
  Mock Task의 stage key(`context/planning/architecture/implementation/
  validation`)가 이미 그 이름과 1:1로 일치함을 조사로 확인했다.
- `projects/unified-dashboard/snapshot.py::build_dev_hq_snapshot()`을
  그대로 import해 호출한다(Freeze 문서/Agent 파일 존재만 관찰, Stage/
  Agent 코드 미import 원칙 그대로 유지).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = Path(__file__).resolve().parent
CONTENT_DIR = OUT_DIR / "content"
DASHBOARD_DIR = REPO_ROOT / "projects" / "dashboard-shell-mvp"

sys.path.insert(0, str(REPO_ROOT / "projects" / "unified-dashboard"))
from snapshot import build_dev_hq_snapshot  # noqa: E402

_EXCLUDE_NAMES = {".git", "__pycache__", "node_modules", ".pytest_cache", ".venv", "venv"}

# Real File Tree 대상 root — Mock `files.json`이 보여주던 영역(hqs/development,
# projects/dashboard-shell-mvp, docs/architecture, docs/decisions)과 동일한
# 범위를 실제 디렉터리로 치환한다. 전체 저장소를 덤프하지 않는다(Scope 최소화).
_TREE_ROOTS = [
    ("hqs/development", 2),
    ("projects/dashboard-shell-mvp", 3),
    ("docs/architecture", 2),
    ("docs/decisions", 2),
]

_MAX_CONTENT_BYTES = 50_000


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return result.stdout.strip()


# ---- File Tree ----


def _build_tree_node(path: Path, depth: int, max_depth: int) -> dict | None:
    """`path`(전체 repo-relative 경로)를 모든 노드(dir/file)에 남긴다 — UI가
    Explorer 클릭 시 이름만으로 fuzzy 매칭하지 않고 정확한 경로로
    `getFileContent()`를 호출할 수 있게 한다."""
    if path.name in _EXCLUDE_NAMES:
        return None
    relpath = str(path.relative_to(REPO_ROOT))
    if path.is_dir():
        if depth >= max_depth:
            return {"name": path.name, "type": "dir", "path": relpath, "children": []}
        children = []
        for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name)):
            node = _build_tree_node(child, depth + 1, max_depth)
            if node is not None:
                children.append(node)
        return {"name": path.name, "type": "dir", "path": relpath, "children": children}
    return {"name": path.name, "type": "file", "path": relpath}


def _mark_changed(node: dict, changed_paths: set) -> dict:
    if node["type"] == "dir":
        node["children"] = [_mark_changed(c, changed_paths) for c in node["children"]]
        return node
    if node["path"] in changed_paths:
        node["changed"] = True
    return node


def build_files_document(changed_paths: set) -> dict:
    tree = []
    for rel, max_depth in _TREE_ROOTS:
        root_path = REPO_ROOT / rel
        if not root_path.is_dir():
            continue
        node = _build_tree_node(root_path, 0, max_depth)
        if node is not None:
            tree.append(_mark_changed(node, changed_paths))
    return {
        "source": "real",
        "generated_at": _now_iso(),
        "note": "실제 저장소 File Tree 스냅샷 — export_real_snapshot.py 실행 시점 기준, 실시간 아님",
        "tree": tree,
    }


# ---- Git status/diff ----


def build_git_document() -> tuple[dict, set]:
    branch = _run(["git", "branch", "--show-current"])
    status_lines = _run(["git", "status", "--porcelain=v1", "--untracked-files=all"]).splitlines()

    changes = []
    changed_paths = set()
    for line in status_lines:
        if not line:
            continue
        code = line[:2].strip()
        path = line[3:]
        status = {"M": "M", "A": "A", "D": "D", "R": "R", "??": "A"}.get(code, code[:1] or "M")
        changes.append({"status": status, "path": path})
        changed_paths.add(path)

    diffs = {}
    for change in changes:
        path = change["path"]
        diff_text = _run(["git", "diff", "--", path])
        if not diff_text:
            diff_text = _run(["git", "diff", "--cached", "--", path])
        if diff_text:
            diffs[path] = diff_text[:20_000]

    doc = {
        "source": "real",
        "generated_at": _now_iso(),
        "branch": branch or None,
        "summary": f"{len(changes)} files changed" if changes else "0 files changed",
        "changes": changes,
        "diffs": diffs,
    }
    return doc, changed_paths


# ---- Dev HQ Workflow snapshot(기존 Read Adapter 재사용) ----


def build_workflow_document() -> dict:
    snapshot = build_dev_hq_snapshot()
    return {
        "source": "real",
        "generated_at": _now_iso(),
        "identity": snapshot.identity,
        "status": snapshot.status,
        "detail": snapshot.detail,
        "source_files": snapshot.source_files,
    }


# ---- 기존 테스트 실행 결과(Dashboard Shell + Dev HQ MVP 회귀 기준선) ----

_TEST_TARGETS = ["projects/dashboard-shell-mvp/tests", "hqs/development/mvp/tests"]
_SUMMARY_RE = __import__("re").compile(
    r"(?:(\d+) passed)?(?:, )?(?:(\d+) skipped)?(?:, )?(?:(\d+) failed)?.* in ([\d.]+)s"
)


def build_tests_document() -> dict:
    started = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *_TEST_TARGETS, "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    duration = time.time() - started
    tail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    match = _SUMMARY_RE.search(tail)
    passed = int(match.group(1)) if match and match.group(1) else 0
    skipped = int(match.group(2)) if match and match.group(2) else 0
    failed = int(match.group(3)) if match and match.group(3) else 0

    return {
        "source": "real",
        "generated_at": _now_iso(),
        "pass": passed,
        "skipped": skipped,
        "failed": failed,
        "lastRun": _now_iso(),
        "duration": f"{duration:.1f}s",
        "targets": _TEST_TARGETS,
        "raw_summary": tail,
    }


# ---- 파일 내용(정적 서버 root 밖의 파일만 — projects/dashboard-shell-mvp/*는
#      기존 정적 서버가 이미 서빙하므로 별도로 내보내지 않는다) ----


def export_file_contents() -> int:
    """`files.json`의 tree는 `_mark_changed()`에서 relpath를 이미 지웠으므로,
    내보낼 파일 목록은 root별로 실제 파일시스템을 다시 걷는다(파일 필터
    조건 — depth/exclude/size — 은 tree 생성 시와 동일하게 재적용)."""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    exported = 0
    for rel, max_depth in _TREE_ROOTS:
        if rel.startswith("projects/dashboard-shell-mvp"):
            continue
        root_path = REPO_ROOT / rel
        if not root_path.is_dir():
            continue
        for path in root_path.rglob("*"):
            if path.is_dir() or any(part in _EXCLUDE_NAMES for part in path.parts):
                continue
            try:
                relpath = path.relative_to(REPO_ROOT)
            except ValueError:
                continue
            if len(str(relpath).split("/")) - len(rel.split("/")) > max_depth:
                continue
            if path.stat().st_size > _MAX_CONTENT_BYTES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            safe_name = str(relpath).replace("/", "__") + ".json"
            (CONTENT_DIR / safe_name).write_text(
                json.dumps({"source": "real", "path": str(relpath), "content": text}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            exported += 1
    return exported


def _write(name: str, document: dict) -> None:
    path = OUT_DIR / name
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{name} written to {path}")


def main() -> None:
    git_doc, changed_paths = build_git_document()
    files_doc = build_files_document(changed_paths)

    _write("git.json", git_doc)
    _write("files.json", files_doc)
    _write("workflow.json", build_workflow_document())
    _write("tests.json", build_tests_document())

    exported = export_file_contents()
    print(f"{exported} file content snapshot(s) written to {CONTENT_DIR}")


if __name__ == "__main__":
    main()
