"""Stage 04 Architecture Validation — Experiment Runner. `cases.py`의 각
Case에 A/B/C 세 변형을 모두 실행하고 `Result Schema` 목록을 만든다.

`engine_call`을 주입받는다 — 실제 Engine(`backend_agent_code_generation`
과 동일한 `str -> str` 시그니처)이 있으면 그대로 넘길 수 있고, 없으면
`controlled_stub_engine_call`(이 파일 하단)로 harness 자체의 배선만
검증한다. **`controlled_stub_engine_call`로 만든 결과는 Architecture
품질 Evidence가 아니다** — LLM을 전혀 호출하지 않는 고정 응답이다."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cases import CASES  # noqa: E402
from variants import run_variant_a, run_variant_b, run_variant_c  # noqa: E402

_VARIANT_RUNNERS = {
    "single": run_variant_a,
    "multi": run_variant_b,
    "multi_ponytail": run_variant_c,
}

_FUNCTION_NAME_RE = re.compile(r"`(\w+)\(")


def controlled_stub_engine_call(prompt: str) -> str:
    """LLM을 호출하지 않는 고정 응답 — harness 배선(순서 독립성, latency
    계측, Gate/Ponytail 연결)만 검증할 때 쓴다. `build_input`에 적힌 첫
    함수명으로 최소 정의를 만들어 scope check를 통과시키되, 실제 LLM을
    호출하지 않으므로 Architecture 품질 비교에는 쓸 수 없다."""
    match = _FUNCTION_NAME_RE.search(prompt)
    function_name = match.group(1) if match else "stub_result"
    return f"def {function_name}(*args, **kwargs):\n    return None\n"


def run_all(engine_call, cases: list = CASES) -> list:
    """모든 Case x 모든 Variant를 실행해 Result Schema 목록을 반환한다.
    반환 순서는 `cases` 순서 x (`single`, `multi`, `multi_ponytail`)
    고정 순서이며, 각 실행의 내부 완료 순서와 무관하다(§10)."""
    results = []
    for case in cases:
        for variant_name, runner in _VARIANT_RUNNERS.items():
            result, _code = runner(
                case["case_id"], case["build_input"], engine_call, case["allowed_function_names"]
            )
            results.append(result)
    return results


def write_results(results: list, out_path: Path) -> None:
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    results = run_all(controlled_stub_engine_call)
    out_path = Path(__file__).resolve().parent / "sample_run_results.json"
    write_results(results, out_path)
    print(f"wrote {len(results)} results (controlled stub, not Architecture Evidence) to {out_path}")
