"""Stage 04 Architecture Validation — A/B/C 실험군 orchestration(RFC 요청
§4). 세 실험군 모두 동일한 `build_input`/`target`/`expose_target`(§5)을
입력받는다 — Target Identification 자체의 변동성은 이 Harness의 비교
대상이 아니다.

`engine_call: Callable[[str], str]`을 주입받는다 — production
`backend_agent_code_generation`을 그대로 넘길 수도, 이 Harness의 controlled
fake를 넘길 수도 있다(§11: 실제 Ponytail 미구현 상태에서 Architecture를
이미 채택한 것처럼 만들지 않기 위한 DI 구조). 이 모듈은 어떤 Production
경로도 새로 만들지 않는다 — 파일을 쓰지 않고 문자열만 다룬다."""

import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from deterministic_checks import check_contract, find_comments_and_docstrings, run_deterministic_gate  # noqa: E402
from ponytail_adapter import select_final_candidate  # noqa: E402
from quality_heuristics import explicitness_issue_count, simplicity_issue_count  # noqa: E402
from result_schema import new_result  # noqa: E402

STAGE_04_CONTRACT_KEYS = ("target", "implementation", "expose_target")

_SUB_AGENT_IDS = ("implementation", "consistency", "minimality")

_SUB_AGENT_INSTRUCTIONS = {
    "implementation": "Write the implementation for the following design.",
    "consistency": "Write an implementation consistent with existing code style for the following design.",
    "minimality": "Write the minimal implementation (no extra abstraction) for the following design.",
}


def _timed(fn, *args):
    start = perf_counter()
    value = fn(*args)
    elapsed_ms = (perf_counter() - start) * 1000
    return value, elapsed_ms


def _gate(code: str, allowed_function_names: tuple, required_function_names: tuple) -> dict:
    return run_deterministic_gate(
        code,
        required_keys=STAGE_04_CONTRACT_KEYS,
        allowed_function_names=allowed_function_names,
        required_function_names=required_function_names,
    )


def _annotate_result(result: dict, code, target, expose_target: bool) -> None:
    """Gate 판정 이후 공통 후처리 — Stage 04 Contract 판정(§7), Quality
    구조 신호(§8), Comment/Docstring 집계(§9)를 채운다. `code`가 `None`
    이면(모든 후보가 Gate에서 FAIL) 기본값(None/0)을 그대로 둔다."""
    if code is None:
        return

    if target is not None:
        wrapped = {"target": target, "implementation": code, "expose_target": expose_target}
        result["correctness"]["contract"] = bool(check_contract(wrapped, STAGE_04_CONTRACT_KEYS))

    result["quality"]["explicitness"] = explicitness_issue_count(code)
    result["quality"]["simplicity"] = simplicity_issue_count(code)

    entries = find_comments_and_docstrings(code)
    result["comments"]["count"] = sum(1 for e in entries if e["kind"] == "comment")
    result["comments"]["docstring_count"] = sum(1 for e in entries if e["kind"] == "docstring")
    result["comments"]["over_two_lines"] = sum(1 for e in entries if e["line_count"] > 2)
    # 이 Harness는 comment 압축을 위해 코드를 자동 리라이트하지 않는다(§9) —
    # 항상 False다.
    result["comments"]["code_changed_for_comment"] = False


def run_variant_a(
    case_id: str, build_input: str, engine_call, allowed_function_names: tuple,
    *, required_function_names: tuple = None, target=None, expose_target: bool = False,
) -> tuple:
    """A — Baseline. 기존 Single-Agent(`backend_agent_code_generation`과
    동일한 시그니처)를 정확히 1회 호출한다."""
    result = new_result(case_id, "single")

    code, generation_ms = _timed(engine_call, build_input)
    result["llm_calls"] = 1
    result["latency_ms"]["generation"] = generation_ms

    gate_result, validation_ms = _timed(_gate, code, allowed_function_names, required_function_names)
    result["latency_ms"]["validation"] = validation_ms
    result["correctness"]["syntax"] = bool(gate_result["checks"]["syntax"])
    result["correctness"]["scope"] = bool(gate_result["checks"]["scope"])

    result["latency_ms"]["total"] = generation_ms + validation_ms
    final_code = code if gate_result["passed"] else None
    _annotate_result(result, final_code, target, expose_target)
    return result, final_code


def _generate_and_gate_candidates(
    build_input: str, engine_call, allowed_function_names: tuple, required_function_names: tuple
) -> tuple:
    """3개 고정 ID Agent 호출 + Deterministic Gate. B/C가 공유한다 — C가
    같은 후보를 재사용하도록 해 Engine 호출이 중복되지 않게 한다."""
    candidates = []
    generation_ms_total = 0.0
    for agent_id in _SUB_AGENT_IDS:
        prompt = f"[{agent_id}]\n{_SUB_AGENT_INSTRUCTIONS[agent_id]}\n\n{build_input}"
        code, generation_ms = _timed(engine_call, prompt)
        generation_ms_total += generation_ms
        candidates.append({"id": agent_id, "code": code})

    def _gate_all():
        for candidate in candidates:
            candidate["gate"] = _gate(candidate["code"], allowed_function_names, required_function_names)
        return candidates

    _, validation_ms = _timed(_gate_all)
    return candidates, generation_ms_total, validation_ms


def run_variant_b(
    case_id: str, build_input: str, engine_call, allowed_function_names: tuple,
    *, required_function_names: tuple = None, target=None, expose_target: bool = False,
) -> tuple:
    """B — Multi-Agent. `implementation`/`consistency`/`minimality` 3개
    고정 ID Agent를 호출하고, Deterministic Gate를 통과한 후보 중 고정
    ID 순서로 Best Candidate를 고른다(§10 — 실행 완료 순서 무관)."""
    result = new_result(case_id, "multi")

    candidates, generation_ms_total, validation_ms = _generate_and_gate_candidates(
        build_input, engine_call, allowed_function_names, required_function_names
    )
    result["llm_calls"] = len(_SUB_AGENT_IDS)
    result["latency_ms"]["generation"] = generation_ms_total
    result["latency_ms"]["validation"] = validation_ms

    best = select_final_candidate(candidates)
    result["correctness"]["syntax"] = best is not None
    result["correctness"]["scope"] = best is not None

    result["latency_ms"]["total"] = generation_ms_total + validation_ms
    final_code = best["code"] if best else None
    _annotate_result(result, final_code, target, expose_target)
    return result, final_code


def run_variant_c(
    case_id: str, build_input: str, engine_call, allowed_function_names: tuple,
    *, required_function_names: tuple = None, target=None, expose_target: bool = False,
) -> tuple:
    """C — Multi-Agent + Ponytail. B와 동일한 3개 고정 ID Agent 호출을
    재사용하고(중복 호출 없음), Ponytail Adapter(controlled, §11)로 Final
    Candidate를 고른다. 실제 Ponytail LLM 판단은 포함하지 않는다 —
    `ponytail` latency는 이 adapter 실행 시간만 측정한다."""
    result = new_result(case_id, "multi_ponytail")

    candidates, generation_ms_total, validation_ms = _generate_and_gate_candidates(
        build_input, engine_call, allowed_function_names, required_function_names
    )
    result["llm_calls"] = len(_SUB_AGENT_IDS)
    result["latency_ms"]["generation"] = generation_ms_total
    result["latency_ms"]["validation"] = validation_ms

    final, ponytail_ms = _timed(select_final_candidate, candidates)
    result["latency_ms"]["ponytail"] = ponytail_ms
    result["correctness"]["syntax"] = final is not None
    result["correctness"]["scope"] = final is not None
    result["latency_ms"]["total"] = generation_ms_total + validation_ms + ponytail_ms

    final_code = final["code"] if final else None
    _annotate_result(result, final_code, target, expose_target)
    return result, final_code
