"""Part 8 — Latency Budget(Baseline vs Optimized Candidate), 3회 반복,
p50/variance 계산. 동일 Workspace 생성 방식을 그대로 재사용한다."""

from __future__ import annotations

import json
import statistics
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
REPEAT_COUNT = 3

_SLOW_DESELECT = [
    "--deselect",
    f"{TESTS_REL}/test_github_adapter_real.py::test_real_structure_and_ast_candidate_analysis_against_jarvis_os",
    "--deselect",
    f"{TESTS_REL}/test_chatgpt_engine.py::test_timeout_raises_runtime_error",
    "--deselect",
    f"{TESTS_REL}/test_omniroute_engine.py::test_timeout_raises_runtime_error",
]


def _run_once(fixture, *, deselect_slow: bool) -> float:
    ws = TestWorkspace(REPO_ROOT)
    ws.create()
    ws.apply_implementation(TARGET_REL, fixture.implementation)
    tests_path = ws.workspace_root / TESTS_REL
    args = [PYTEST_BIN, str(tests_path), "-q", "-p", "no:cacheprovider"]
    if deselect_slow:
        args += _SLOW_DESELECT
    start = time.perf_counter()
    subprocess.run(args, capture_output=True, text=True, cwd=str(ws.workspace_root), timeout=300)
    total_ms = (time.perf_counter() - start) * 1000
    ws.cleanup()
    return total_ms


def compute_stats(values: list) -> dict:
    return {
        "values_ms": values,
        "mean_ms": statistics.mean(values),
        "p50_ms": statistics.median(values),
        "stdev_ms": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "min_ms": min(values),
        "max_ms": max(values),
    }


def main() -> dict:
    fixture = build_fixture(REPO_ROOT)
    baseline_values = [_run_once(fixture, deselect_slow=False) for _ in range(REPEAT_COUNT)]
    optimized_values = [_run_once(fixture, deselect_slow=True) for _ in range(REPEAT_COUNT)]

    baseline_stats = compute_stats(baseline_values)
    optimized_stats = compute_stats(optimized_values)

    absolute_improvement_ms = baseline_stats["mean_ms"] - optimized_stats["mean_ms"]
    relative_improvement_pct = (absolute_improvement_ms / baseline_stats["mean_ms"]) * 100

    return {
        "repeat_count": REPEAT_COUNT,
        "baseline": baseline_stats,
        "optimized_candidate_deselect_3_slow_tests": optimized_stats,
        "absolute_improvement_ms": absolute_improvement_ms,
        "relative_improvement_pct": relative_improvement_pct,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))
