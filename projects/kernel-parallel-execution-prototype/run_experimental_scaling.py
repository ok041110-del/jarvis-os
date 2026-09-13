"""Experimental Implementation — Parallel Execution 확장 검증(Governance v2).

Formal Kernel Migration이 아니다 — Phase 7 HOLD/RFC-0012/ADC-0012를 해제하지 않으며, `hqs/`·`core/` 실행 경로 의존은 0건이다.
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine_caller import call_engine  # noqa: E402

PROTO_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROTO_ROOT / "output" / "experimental-scaling"

# 6개 독립 Task — Phase 6과 동일한 중립 도메인 유지, 4-way 이상 검증 위해 3개
# 추가. 응답 첫 단어의 주제 태그로 결과 귀속을 프로그램적으로 검증한다(텍스트 결정론 주장 아님).
TASK_POOL = {
    "tides": "Start your answer with the exact word 'TIDES.' then a space. In 1-2 sentences, explain in plain prose why ocean tides happen.",
    "autumn_leaves": "Start your answer with the exact word 'LEAVES.' then a space. In 1-2 sentences, explain in plain prose why leaves change color in autumn.",
    "bread_rising": "Start your answer with the exact word 'BREAD.' then a space. In 1-2 sentences, explain in plain prose why bread dough rises when yeast is added.",
    "rainbow": "Start your answer with the exact word 'RAINBOW.' then a space. In 1-2 sentences, explain in plain prose why rainbows form after rain.",
    "ice_floats": "Start your answer with the exact word 'ICE.' then a space. In 1-2 sentences, explain in plain prose why ice floats on liquid water.",
    "thunder_delay": "Start your answer with the exact word 'THUNDER.' then a space. In 1-2 sentences, explain in plain prose why thunder is heard after lightning is seen.",
}

EXPECTED_TAG = {
    "tides": "TIDES.",
    "autumn_leaves": "LEAVES.",
    "bread_rising": "BREAD.",
    "rainbow": "RAINBOW.",
    "ice_floats": "ICE.",
    "thunder_delay": "THUNDER.",
}

LONG_TASK_PROMPT = (
    "Start your answer with the exact word 'LONGFORM.' then a space. "
    "Write a detailed, well-structured explanation (roughly 400-600 words, "
    "multiple paragraphs) of how the water cycle (evaporation, condensation, "
    "precipitation, collection) works and why it matters for climate."
)


def _run_named_pool(names: list[str], *, label: str) -> dict:
    """지정된 이름의 Task만 동시에 실행하고, 완료 순서·개별 소요시간을 기록한다."""
    t0 = time.monotonic()
    completion_order = []
    results = {}
    per_task_elapsed = {}
    task_start = {n: time.monotonic() for n in names}
    with ThreadPoolExecutor(max_workers=len(names)) as pool:
        futures = {pool.submit(call_engine, TASK_POOL[n]): n for n in names}
        for fut in as_completed(futures):
            n = futures[fut]
            results[n] = fut.result()
            per_task_elapsed[n] = round(time.monotonic() - task_start[n], 1)
            completion_order.append(n)
    elapsed = time.monotonic() - t0
    return {
        "label": label,
        "mode": "parallel",
        "task_count": len(names),
        "elapsed_sec": round(elapsed, 1),
        "per_task_elapsed_sec": per_task_elapsed,
        "completion_order": completion_order,
        "results": results,
    }


def run_sequential_full() -> dict:
    """전체 6개 Task를 순차 실행 — Parallel 6-way와 동일 Task 집합으로 직접 비교."""
    t0 = time.monotonic()
    results = {}
    per_task_elapsed = {}
    for name, prompt in TASK_POOL.items():
        s = time.monotonic()
        results[name] = call_engine(prompt)
        per_task_elapsed[name] = round(time.monotonic() - s, 1)
    elapsed = time.monotonic() - t0
    return {
        "label": "sequential_all6",
        "mode": "sequential",
        "task_count": len(TASK_POOL),
        "elapsed_sec": round(elapsed, 1),
        "per_task_elapsed_sec": per_task_elapsed,
        "results": results,
    }


def run_parallel_2way() -> dict:
    return _run_named_pool(["tides", "autumn_leaves"], label="parallel_2way")


def run_parallel_3way() -> dict:
    return _run_named_pool(["tides", "autumn_leaves", "bread_rising"], label="parallel_3way")


def run_parallel_4way() -> dict:
    return _run_named_pool(
        ["tides", "autumn_leaves", "bread_rising", "rainbow"], label="parallel_4way"
    )


def run_parallel_6way() -> dict:
    return _run_named_pool(list(TASK_POOL.keys()), label="parallel_6way")


def run_long_task_scenario() -> dict:
    """장시간 Task 1개 + 짧은 Task 2개를 같은 Pool에 제출 — 짧은 Task가 지연 없이 먼저 완료되는지 확인한다."""
    jobs = {
        "long_water_cycle": LONG_TASK_PROMPT,
        "tides": TASK_POOL["tides"],
        "ice_floats": TASK_POOL["ice_floats"],
    }
    t0 = time.monotonic()
    completion_order = []
    results = {}
    per_task_elapsed = {}
    task_start = {n: time.monotonic() for n in jobs}
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {pool.submit(call_engine, prompt): name for name, prompt in jobs.items()}
        for fut in as_completed(futures):
            name = futures[fut]
            results[name] = fut.result()
            per_task_elapsed[name] = round(time.monotonic() - task_start[name], 1)
            completion_order.append(name)
    elapsed = time.monotonic() - t0
    return {
        "label": "long_task_scenario",
        "elapsed_sec": round(elapsed, 1),
        "per_task_elapsed_sec": per_task_elapsed,
        "completion_order": completion_order,
        "long_task_finished_last": completion_order[-1] == "long_water_cycle",
        "results": results,
    }


def run_exception_in_pool() -> dict:
    """정상 Task 2개 + 실패하는 Task 1개(존재하지 않는 바이너리 호출 — 실제 subprocess 예외)를 같은 Pool에 제출한다."""

    def _call_nonexistent_engine(prompt: str) -> str:
        import subprocess

        result = subprocess.run(
            ["claude-binary-that-does-not-exist", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout

    jobs = {
        "rainbow": (call_engine, TASK_POOL["rainbow"]),
        "thunder_delay": (call_engine, TASK_POOL["thunder_delay"]),
        "forced_failure": (_call_nonexistent_engine, "unused"),
    }
    propagated = {}
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {pool.submit(fn, arg): name for name, (fn, arg) in jobs.items()}
        for fut in futures:
            name = futures[fut]
            try:
                propagated[name] = {"status": "ok", "value_len": len(fut.result())}
            except Exception as e:  # noqa: BLE001 — 예외 타입 자체가 관찰 대상
                propagated[name] = {"status": "exception", "detail": f"{type(e).__name__}: {e}"}
    return propagated


def check_deterministic_collection(*batches: dict) -> dict:
    """각 배치의 결과가 자기 자신의 Task 태그로 시작하는지 검증한다 — Dispatch의 교차 배정 여부를 확인한다."""
    mismatches = []
    checked = 0
    for batch in batches:
        for name, text in batch.get("results", {}).items():
            if name not in EXPECTED_TAG:
                continue
            checked += 1
            if not text.strip().startswith(EXPECTED_TAG[name]):
                mismatches.append({"task": name, "expected_prefix": EXPECTED_TAG[name], "got_head": text[:40]})
    return {"checked": checked, "mismatches": mismatches, "deterministic": not mismatches}


def check_zero_dependency() -> list[str]:
    """핵심 Dispatch 경로가 hqs/를 import하지 않는지 정적 검사한다(core/execution 결합은 execution_result_bridge.py에서 별도 검증)."""
    violations = []
    for py_file in [PROTO_ROOT / "engine_caller.py", PROTO_ROOT / "run_experimental_scaling.py"]:
        text = py_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("import hqs") or stripped.startswith("from hqs"):
                violations.append(f"{py_file.name}: {stripped}")
            if stripped.startswith("import core") or stripped.startswith("from core"):
                violations.append(f"{py_file.name}: {stripped}")
    return violations


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    violations = check_zero_dependency()
    print(f"ZERO_DEPENDENCY_CHECK: {'PASS' if not violations else 'FAIL'} — violations={violations}")

    seq = run_sequential_full()
    print(f"SEQUENTIAL_ALL6: {seq['elapsed_sec']}s")

    p2 = run_parallel_2way()
    print(f"PARALLEL_2WAY: {p2['elapsed_sec']}s")
    p3 = run_parallel_3way()
    print(f"PARALLEL_3WAY: {p3['elapsed_sec']}s")
    p4 = run_parallel_4way()
    print(f"PARALLEL_4WAY: {p4['elapsed_sec']}s")
    p6 = run_parallel_6way()
    print(f"PARALLEL_6WAY: {p6['elapsed_sec']}s")

    long_scn = run_long_task_scenario()
    print(f"LONG_TASK_SCENARIO: {long_scn['elapsed_sec']}s, order={long_scn['completion_order']}")

    exc = run_exception_in_pool()
    print(f"EXCEPTION_IN_POOL: {json.dumps(exc, ensure_ascii=False)}")

    det = check_deterministic_collection(seq, p2, p3, p4, p6, long_scn)
    print(f"DETERMINISTIC_COLLECTION: {json.dumps(det, ensure_ascii=False)}")

    for name, payload in [
        ("sequential_all6", seq),
        ("parallel_2way", p2),
        ("parallel_3way", p3),
        ("parallel_4way", p4),
        ("parallel_6way", p6),
        ("long_task_scenario", long_scn),
        ("exception_in_pool", exc),
        ("deterministic_collection", det),
    ]:
        (OUTPUT_DIR / f"{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    summary = {
        "zero_dependency_violations": violations,
        "sequential_all6_elapsed_sec": seq["elapsed_sec"],
        "parallel_2way_elapsed_sec": p2["elapsed_sec"],
        "parallel_3way_elapsed_sec": p3["elapsed_sec"],
        "parallel_4way_elapsed_sec": p4["elapsed_sec"],
        "parallel_6way_elapsed_sec": p6["elapsed_sec"],
        "speedup_6way_vs_sequential": round(seq["elapsed_sec"] / p6["elapsed_sec"], 2)
        if p6["elapsed_sec"] > 0
        else None,
        "long_task_scenario_elapsed_sec": long_scn["elapsed_sec"],
        "long_task_completion_order": long_scn["completion_order"],
        "exception_propagation": exc,
        "deterministic_collection": det,
    }
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
