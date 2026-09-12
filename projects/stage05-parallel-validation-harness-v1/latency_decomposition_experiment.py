"""Part 2 — Test Validator Latency Decomposition + Part 3 Case 1~7(사용자
지시). 각 단계를 개별적으로 실측한다 — 추정하지 않는다."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.fixtures import build_fixture  # noqa: E402
from domain.workspace import TestWorkspace  # noqa: E402

PYTEST_BIN = "/root/.local/bin/pytest"
TESTS_REL = "hqs/development/mvp/tests"
TARGET_REL = "hqs/development/mvp/agents/backend.py"


def _timed(fn):
    start = time.perf_counter()
    value = fn()
    return value, (time.perf_counter() - start) * 1000


def case_5_workspace_copy_only() -> dict:
    ws = TestWorkspace(REPO_ROOT)
    _, ms = _timed(ws.create)
    cleanup = ws.cleanup()
    return {"case": 5, "name": "workspace_copy_only", "latency_ms": ms, "cleanup_succeeded": cleanup.succeeded}


def case_6_copy_plus_apply(fixture) -> dict:
    ws2 = TestWorkspace(REPO_ROOT)
    _, copy_ms = _timed(ws2.create)
    _, apply_ms = _timed(lambda: ws2.apply_implementation(TARGET_REL, fixture.implementation))
    cleanup = ws2.cleanup()
    return {
        "case": 6,
        "name": "workspace_copy_plus_apply",
        "copy_latency_ms": copy_ms,
        "apply_latency_ms": apply_ms,
        "total_ms": copy_ms + apply_ms,
        "cleanup_succeeded": cleanup.succeeded,
    }


def case_7_workspace_plus_pytest_startup(fixture) -> dict:
    """Workspace + pytest startup(= collection만, 실제 test 실행 없음)."""
    ws = TestWorkspace(REPO_ROOT)
    _, copy_ms = _timed(ws.create)
    ws.apply_implementation(TARGET_REL, fixture.implementation)
    tests_path = ws.workspace_root / TESTS_REL

    start = time.perf_counter()
    proc = subprocess.run(
        [PYTEST_BIN, str(tests_path), "-q", "-p", "no:cacheprovider", "--collect-only"],
        capture_output=True, text=True, cwd=str(ws.workspace_root), timeout=120,
    )
    collect_ms = (time.perf_counter() - start) * 1000
    cleanup = ws.cleanup()
    return {
        "case": 7,
        "name": "workspace_plus_pytest_startup_collection_only",
        "workspace_copy_ms": copy_ms,
        "pytest_startup_plus_collection_ms": collect_ms,
        "total_ms": copy_ms + collect_ms,
        "returncode": proc.returncode,
        "collected_line": [l for l in proc.stdout.splitlines() if "collected" in l][-1:],
        "cleanup_succeeded": cleanup.succeeded,
    }


def case_1_full_pytest_in_workspace(fixture, *, unset_github_token: bool) -> dict:
    ws = TestWorkspace(REPO_ROOT)
    _, copy_ms = _timed(ws.create)
    ws.apply_implementation(TARGET_REL, fixture.implementation)
    tests_path = ws.workspace_root / TESTS_REL

    import os
    env = dict(os.environ)
    if unset_github_token:
        env.pop("GITHUB_TOKEN", None)

    start = time.perf_counter()
    proc = subprocess.run(
        [PYTEST_BIN, str(tests_path), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(ws.workspace_root), timeout=300, env=env,
    )
    exec_ms = (time.perf_counter() - start) * 1000
    cleanup = ws.cleanup()
    tail_lines = proc.stdout.strip().splitlines()[-3:]
    return {
        "case": 1,
        "name": f"full_pytest_in_workspace(github_token={'unset' if unset_github_token else 'inherited'})",
        "workspace_copy_ms": copy_ms,
        "pytest_full_run_ms": exec_ms,
        "total_ms": copy_ms + exec_ms,
        "returncode": proc.returncode,
        "summary_tail": tail_lines,
        "cleanup_succeeded": cleanup.succeeded,
    }


def main() -> dict:
    fixture = build_fixture(REPO_ROOT)
    results = {
        "case_5": case_5_workspace_copy_only(),
        "case_6": case_6_copy_plus_apply(fixture),
        "case_7": case_7_workspace_plus_pytest_startup(fixture),
        "case_1_with_github_token": case_1_full_pytest_in_workspace(fixture, unset_github_token=False),
        "case_1_without_github_token": case_1_full_pytest_in_workspace(fixture, unset_github_token=True),
    }
    return results


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))
