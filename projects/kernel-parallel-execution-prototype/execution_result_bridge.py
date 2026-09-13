"""Experimental Implementation — ExecutionResult 결합 실험(읽기 전용).

이 파일은 "형식적으로 결합 가능하다"는 사실만 확인한다 — Dispatch와 Execution Layer가 같은 Component라고 결정하지 않는다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_ROOT = REPO_ROOT / "core"
sys.path.insert(0, str(CORE_ROOT))

from execution.mvp_0006.execution_result_builder import build_execution_result  # noqa: E402
from execution.pipeline import run_execution_layer_pipeline  # noqa: E402


def _make_reference_execution_state() -> str:
    """Builder 체인의 앞 5단계는 실험 대상이 아니므로 직접 재구현하지 않고 기존 Kernel Module을 호출해 얻는다."""
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
    """Dispatch 결과를 `build_execution_result()`에 그대로 넣을 수 있는지 시험한다 — 실패해도 억지로 성공시키지 않는다."""
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
