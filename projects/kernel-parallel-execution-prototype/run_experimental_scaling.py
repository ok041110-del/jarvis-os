"""Experimental Implementation — Parallel Execution 확장 검증(Governance v2).

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation"
절이 허용하는 격리된 실험이다. `EVIDENCE.md`(Phase 6 Prototype, 3-way까지만
검증)가 "관찰되지 않은 것"으로 명시한 공백 — 4-way 이상 병렬, 장시간 Task,
동일 Task 집합에서의 Sequential/Parallel 직접 비교 — 을 채운다.

이 스크립트는 Formal Kernel Migration이 아니다. Phase 7 HOLD, RFC-0012
Proposed, ADC-0012 DEFER를 해제하지 않는다. `hqs/`·`core/`에 대한 실행
경로 의존은 여전히 0건이다(`engine_caller.py`를 그대로 재사용 — `hqs/`도
`core/`도 import하지 않는다). `core/execution/`과의 결합 실험만 별도
파일(`execution_result_bridge.py`)에서 **읽기 전용 import**로 수행한다.
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

# 6개 독립 Task — Phase 6과 동일한 제3의 중립 도메인(자연 현상)을 유지하되
# 4-way 이상 검증을 위해 3개를 추가했다. 각 프롬프트는 응답 첫 단어로
# 자기 주제 태그를 선언하도록 요구한다 — 이는 "결과 수집이 deterministic한가"
# (어느 Task의 결과가 실제로 그 Task 자신의 것인지)를 텍스트 내용만으로
# 프로그램적으로 검증하기 위한 것이며, LLM 텍스트 자체의 결정론을
# 주장하는 것이 아니다.
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
    """장시간 Task(수백 단어 요구) 1개 + 짧은 Task 2개를 같은 Pool에 동시 제출.

    검증 대상: (1) 장시간 Task가 ENGINE_TIMEOUT_SECONDS(180s) 안에 끝나는가,
    (2) 짧은 Task가 장시간 Task에 의해 지연되지 않고 먼저 완료되는가(완료
    순서로 확인), (3) 세 Task의 결과가 서로 섞이지 않는가.
    """
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
    """정상 Task 2개 + 반드시 실패하는 Task 1개(존재하지 않는 바이너리 호출,
    실제 subprocess 예외 — 인위적으로 코드에서 던지는 예외가 아니다)를 같은
    Pool에 동시 제출."""

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
    """각 배치의 결과가 자기 자신의 Task 태그로 시작하는지 검증한다 —
    Dispatch가 결과를 다른 Task와 교차 배정하지 않았는지에 대한 프로그램적
    증거다(텍스트 내용의 결정론이 아니라 결합/라우팅의 정확성 검증)."""
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
    """이 실험 파일들이 hqs/ 를 import하지 않는지 정적 검사(핵심 Dispatch
    경로만 대상 — core/execution 결합 실험은 execution_result_bridge.py에
    별도로 있으며, 그 파일 자체가 스스로를 core/ 결합 실험이라고 명시한다)."""
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
