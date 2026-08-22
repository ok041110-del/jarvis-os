"""Experimental Implementation — ExecutionResult 결합 실험(읽기 전용).

`core/execution/pipeline.py`와 `core/execution/mvp_0006/execution_result_builder.py`를
**읽기 전용으로 import**해 계약(Contract)을 그대로 사용할 뿐, 수정하지
않는다. 목적은 딱 하나 — Experimental Dispatch(Parallel Execution)가
수집한 결과 문자열들이 `build_execution_result(..., results: list[str])`의
입력 형태로 "결합 가능한가"를 확인하는 것이다.

**중요한 구분**(Governance v2 Experimental Implementation 원칙,
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` 참조): 이 파일이 확인하는
것은 "형식적으로 결합 가능하다"는 사실 하나뿐이다. "Dispatch와 Execution
Layer가 Architecture상 같은 Component다" 또는 "합쳐야 한다"는 것을
결정하지 않는다 — 그 판단은 `RFC-0012`/`ADC-0012`(Proposed/DEFER 유지)의
몫이며, 이 실험은 그 상태를 바꾸지 않는다.

이 파일은 `core/execution/pipeline.py`를 import만 하며 한 줄도 수정하지
않는다. `hqs/`는 어디에서도 import하지 않는다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_ROOT = REPO_ROOT / "core"
sys.path.insert(0, str(CORE_ROOT))

from execution.mvp_0006.execution_result_builder import build_execution_result  # noqa: E402
from execution.pipeline import run_execution_layer_pipeline  # noqa: E402


def _make_reference_execution_state() -> str:
    """`run_execution_layer_pipeline()`을 더미 입력으로 1회 실행해, 그 안에
    포함된 `## Execution State` 절을 그대로 재사용한다 — Builder 체인의
    앞 5단계(Request~State)는 이 실험의 대상이 아니므로 직접 재구현하지
    않고, 이미 존재하는 Kernel Module을 있는 그대로 호출해 얻는다."""
    placeholder_result = run_execution_layer_pipeline(
        "## Task\nplaceholder\n",
        created_at="2026-08-22T00:00:00Z",
        submitted_at="2026-08-22T00:00:01Z",
        state="COMPLETED",
        changed_at="2026-08-22T00:00:02Z",
        produced_at="2026-08-22T00:00:03Z",
        results=["__placeholder__"],
    )
    marker = "## Execution State\n"
    idx = placeholder_result.index(marker)
    return placeholder_result[idx + len(marker):]


def try_combine(dispatch_results: dict[str, str]) -> dict:
    """Experimental Dispatch가 모은 {task_name: result_text} 딕셔너리를
    `results: list[str]`로 변환해 `build_execution_result()`에 그대로
    넣을 수 있는지 시험한다. 성공/실패, 예외 메시지를 있는 그대로 반환한다
    — 실패해도 억지로 성공시키지 않는다."""
    execution_state = _make_reference_execution_state()
    results_list = [f"{name}: {text.strip()}" for name, text in dispatch_results.items()]
    try:
        artifact = build_execution_result(
            execution_state,
            handle_id="experimental-dispatch-bridge",
            produced_at="2026-08-22T00:00:04Z",
            results=results_list,
        )
        return {
            "combinable": True,
            "results_item_count": len(results_list),
            "artifact_contains_results_header": "## Results" in artifact,
            "artifact_length_chars": len(artifact),
            "note": (
                "형식적으로 결합 가능함을 확인했을 뿐, Architecture상 "
                "Dispatch와 Execution Layer가 같은 Component라고 확정하지 않는다."
            ),
        }
    except Exception as e:  # noqa: BLE001 — 실패 자체가 관찰 대상
        return {"combinable": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    import json

    demo = try_combine({"tides": "TIDES. Because of gravity.", "rainbow": "RAINBOW. Because of refraction."})
    print(json.dumps(demo, ensure_ascii=False, indent=2))
