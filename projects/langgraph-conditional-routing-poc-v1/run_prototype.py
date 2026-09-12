"""실행 harness — baseline(`run_mvp_0002`)과 LangGraph 버전을 동일한
실제 입력으로 실행하고 결과를 비교한다. 저장소 코드는 수정하지 않는다
(README "Engine 호출 경로에 대한 unavoidable 차이" 참고).

실행: 저장소 루트에서 `python3 projects/langgraph-conditional-routing-poc-v1/run_prototype.py`
(langgraph가 설치된 환경에서, PYTHONPATH에 저장소 루트 포함)
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import hqs.development.mvp.agents.backend as backend_mod  # noqa: E402
import hqs.development.mvp.agents.qa as qa_mod  # noqa: E402
from hqs.development.mvp.engine import call_engine as real_call_engine  # noqa: E402

# OmniRoute 서버가 이 실행 환경에 없어(README 참고) 프로덕션 경로
# (call_engine_via_omniroute) 대신 이 저장소의 다른 real Engine
# 경로(engine.py::call_engine, Claude CLI 직접 호출)로 일시 교체한다.
# 프로세스 메모리 안에서만 유효하며 파일은 수정하지 않는다.
backend_mod.call_engine = real_call_engine
qa_mod.call_engine = real_call_engine

from hqs.development.mvp.workflow_0002 import run_mvp_0002  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_langgraph import run_via_langgraph  # noqa: E402


CLEAN_CODE = '''def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''

SAMPLE_CODE = """
def add(a, b=[]):
    try:
        return a + b
    except:
        pass
"""

CASES = {"CLEAN_CODE": CLEAN_CODE, "SAMPLE_CODE": SAMPLE_CODE}


def run_case(name: str, code: str) -> dict:
    print(f"=== case: {name} ===", flush=True)

    t0 = time.monotonic()
    baseline = run_mvp_0002(code)
    t1 = time.monotonic()
    baseline_seconds = t1 - t0
    print(f"  baseline(run_mvp_0002) 완료: {baseline_seconds:.1f}s", flush=True)

    t0 = time.monotonic()
    langgraph_result = run_via_langgraph(code)
    t1 = time.monotonic()
    langgraph_seconds = t1 - t0
    print(f"  langgraph 완료: {langgraph_seconds:.1f}s", flush=True)

    baseline_skipped = "생략됨" in baseline["test_execution"]
    langgraph_skipped = "생략됨" in langgraph_result["test_execution"]
    routing_matches = baseline_skipped == langgraph_skipped

    return {
        "case": name,
        "baseline": baseline,
        "baseline_seconds": round(baseline_seconds, 1),
        "baseline_skipped_test_execution": baseline_skipped,
        "langgraph": langgraph_result,
        "langgraph_seconds": round(langgraph_seconds, 1),
        "langgraph_skipped_test_execution": langgraph_skipped,
        "routing_decision_matches": routing_matches,
    }


def main():
    results = [run_case(name, code) for name, code in CASES.items()]
    out_path = Path(__file__).resolve().parent / "run_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n결과 저장: {out_path}")
    for r in results:
        print(
            f"- {r['case']}: routing_decision_matches="
            f"{r['routing_decision_matches']} "
            f"(baseline skip={r['baseline_skipped_test_execution']}, "
            f"langgraph skip={r['langgraph_skipped_test_execution']}) "
            f"baseline={r['baseline_seconds']}s langgraph={r['langgraph_seconds']}s"
        )


if __name__ == "__main__":
    main()
