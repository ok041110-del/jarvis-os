"""Kernel Candidate Prototype — Parallel Execution(원시 기법)이 특정 HQ/도메인에
종속되지 않은 공통 실행 기법인지 검증한다.

검증 대상은 오직 하나: "서로 독립적인 Task를 `ThreadPoolExecutor.submit()`+
`.result()`로 동시에 `call_engine()` 호출할 수 있는가" — Wave 구조, Checkpointing,
Team/Workflow, Investment/Dev HQ 도메인 로직은 전부 배제한다.

도메인: 자연 현상에 대한 일반 상식 설명(조수·단풍·발효) — code_review/
test_execution(Dev HQ)도 Stock/ETF/Dividend Stock(Investment HQ)도 아닌
제3의 중립 도메인이다. `hqs/development/`, `hqs/investment/`, `core/`
어디에서도 import하지 않는다(이 디렉터리 안의 `engine_caller.py`만 사용).

사용법: python3 run_prototype.py
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine_caller import call_engine  # noqa: E402

PROTO_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROTO_ROOT / "output"

# 서로 완전히 독립적인 3개 Task — 공유 상태 없음, 서로의 출력을 입력으로 쓰지 않음.
# Dev HQ(code_review/test_execution)도 Investment HQ(Stock/ETF/Dividend Stock)도
# 아닌 일반 상식 도메인.
TASKS = {
    "tides": "In 2-3 sentences, explain in plain prose why ocean tides happen.",
    "autumn_leaves": "In 2-3 sentences, explain in plain prose why leaves change color in autumn.",
    "bread_rising": "In 2-3 sentences, explain in plain prose why bread dough rises when yeast is added.",
}


def run_sequential() -> dict:
    results = {}
    t0 = time.monotonic()
    for name, prompt in TASKS.items():
        results[name] = call_engine(prompt)
    elapsed = time.monotonic() - t0
    return {"mode": "sequential", "elapsed_sec": round(elapsed, 1), "results": results}


def run_parallel() -> dict:
    results = {}
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=len(TASKS)) as pool:
        futures = {name: pool.submit(call_engine, prompt) for name, prompt in TASKS.items()}
        for name, fut in futures.items():
            results[name] = fut.result()
    elapsed = time.monotonic() - t0
    return {"mode": "parallel", "elapsed_sec": round(elapsed, 1), "results": results}


def run_exception_propagation_check() -> dict:
    """정상 Task 2개 + 반드시 실패하는 Task 1개(존재하지 않는 Engine 바이너리
    호출 — 실제 subprocess 예외, 인위적으로 예외를 던지는 코드가 아니다)를
    같은 ThreadPoolExecutor에 함께 제출해, 실패가 호출자에게 정상 전파되는지
    확인한다."""

    def _call_nonexistent_engine(prompt: str) -> str:
        import subprocess
        result = subprocess.run(
            ["claude-binary-that-does-not-exist", "-p", prompt],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout

    jobs = {
        "tides": (call_engine, TASKS["tides"]),
        "autumn_leaves": (call_engine, TASKS["autumn_leaves"]),
        "forced_failure": (_call_nonexistent_engine, "unused"),
    }

    propagated = {}
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {name: pool.submit(fn, arg) for name, (fn, arg) in jobs.items()}
        for name, fut in futures.items():
            try:
                fut.result()
                propagated[name] = "no_exception"
            except Exception as e:
                propagated[name] = f"{type(e).__name__}: {e}"

    return propagated


def check_zero_dependency() -> list[str]:
    """이 Prototype 디렉터리의 .py 파일들이 hqs/ 또는 core/를 import하지
    않는지 소스 레벨로 확인한다(런타임 sys.modules 검사가 아니라 정적 검사)."""
    violations = []
    for py_file in PROTO_ROOT.glob("*.py"):
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

    seq = run_sequential()
    print(f"SEQUENTIAL: {seq['elapsed_sec']}s")
    (OUTPUT_DIR / "sequential.json").write_text(
        json.dumps(seq, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    par = run_parallel()
    print(f"PARALLEL: {par['elapsed_sec']}s")
    (OUTPUT_DIR / "parallel.json").write_text(
        json.dumps(par, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    exc = run_exception_propagation_check()
    print(f"EXCEPTION_PROPAGATION: {json.dumps(exc, ensure_ascii=False)}")
    (OUTPUT_DIR / "exception_propagation.json").write_text(
        json.dumps(exc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    summary = {
        "zero_dependency_violations": violations,
        "sequential_elapsed_sec": seq["elapsed_sec"],
        "parallel_elapsed_sec": par["elapsed_sec"],
        "speedup": round(seq["elapsed_sec"] / par["elapsed_sec"], 2) if par["elapsed_sec"] > 0 else None,
        "task_count": len(TASKS),
        "results_collected": {name: len(v) for name, v in seq["results"].items()},
        "exception_propagation": exc,
    }
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
