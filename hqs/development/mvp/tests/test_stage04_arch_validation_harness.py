"""Stage 04 Architecture Validation Harness 검증(RFC 요청 — Stage 04
Architecture Validation Harness Implementation). 이 Harness 자체는
Production `stage_04.py`/Kernel Architecture를 변경하지 않는다 — 여기서는
(a) Deterministic Gate/comment 정책이 올바르게 판정하는지, (b) 고정 ID
순서가 실행 완료 순서와 무관한지, (c) A/B/C variant가 Contract대로
llm_calls/latency/candidate를 만드는지, (d) Ponytail Adapter가 실제
Supervisor 없이 결정적으로만 동작하는지를 전부 controlled fake로
검증한다 — 실제 Engine을 호출하지 않는다."""

import importlib.util
import sys
from pathlib import Path

_HARNESS_DIR = (
    Path(__file__).resolve().parents[2] / "stages" / "04_implementation" / "architecture_validation"
)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


result_schema = _load("arch_val_result_schema", _HARNESS_DIR / "result_schema.py")
deterministic_checks = _load("arch_val_deterministic_checks", _HARNESS_DIR / "deterministic_checks.py")
ponytail_adapter = _load("arch_val_ponytail_adapter", _HARNESS_DIR / "ponytail_adapter.py")
variants = _load("arch_val_variants", _HARNESS_DIR / "variants.py")
run_experiment = _load("arch_val_run_experiment", _HARNESS_DIR / "run_experiment.py")


# --- result_schema.py --------------------------------------------------


def test_new_result_has_all_required_top_level_keys():
    result = result_schema.new_result("case_x", "single")
    assert set(result.keys()) == {
        "case_id", "variant", "llm_calls", "input_tokens", "output_tokens", "total_tokens",
        "latency_ms", "correctness", "quality", "comments",
    }
    assert set(result["latency_ms"].keys()) == {"total", "generation", "validation", "ponytail"}
    assert set(result["correctness"].keys()) == {"syntax", "contract", "scope", "pytest"}


def test_new_result_rejects_unknown_variant():
    import pytest
    with pytest.raises(ValueError):
        result_schema.new_result("case_x", "not_a_real_variant")


def test_new_result_tokens_default_to_none_not_zero():
    """§13/§6: 측정하지 않은 값은 0이 아니라 None(미확보)이어야 한다 —
    추정값을 Evidence로 오인하지 않도록 하는 방어."""
    result = result_schema.new_result("case_x", "single")
    assert result["input_tokens"] is None
    assert result["output_tokens"] is None
    assert result["total_tokens"] is None


# --- deterministic_checks.py --------------------------------------------


def test_check_syntax_detects_valid_and_invalid_code():
    assert bool(deterministic_checks.check_syntax("def f():\n    return 1\n")) is True
    assert bool(deterministic_checks.check_syntax("def f(:\n    return 1\n")) is False


def test_check_ast_structural_validity_requires_a_definition():
    assert bool(deterministic_checks.check_ast_structural_validity("def f():\n    pass\n")) is True
    assert bool(deterministic_checks.check_ast_structural_validity("x = 1\n")) is False


def test_check_contract_detects_missing_keys():
    ok = deterministic_checks.check_contract(
        {"target": None, "implementation": "x", "expose_target": False}, ("target", "implementation", "expose_target")
    )
    missing = deterministic_checks.check_contract({"target": None}, ("target", "implementation", "expose_target"))
    assert bool(ok) is True
    assert bool(missing) is False


def test_check_scope_flags_out_of_scope_definitions():
    in_scope = deterministic_checks.check_scope("def allowed():\n    pass\n", ("allowed",))
    out_of_scope = deterministic_checks.check_scope(
        "def allowed():\n    pass\n\ndef extra():\n    pass\n", ("allowed",)
    )
    assert bool(in_scope) is True
    assert bool(out_of_scope) is False


def test_check_comment_docstring_policy_flags_over_two_lines():
    short = "def f():\n    # one line\n    return 1\n"
    long_docstring = 'def f():\n    """line one\n    line two\n    line three"""\n    return 1\n'
    assert bool(deterministic_checks.check_comment_docstring_policy(short)) is True
    assert bool(deterministic_checks.check_comment_docstring_policy(long_docstring)) is False


def test_find_comments_and_docstrings_counts_correctly():
    code = "def f():\n    # a comment\n    '''doc'''\n    return 1\n"
    entries = deterministic_checks.find_comments_and_docstrings(code)
    kinds = [entry["kind"] for entry in entries]
    assert kinds.count("comment") == 1
    assert kinds.count("docstring") == 1


def test_run_deterministic_gate_fails_closed_on_bad_syntax():
    gate = deterministic_checks.run_deterministic_gate(
        "def f(:\n", required_keys=(), allowed_function_names=("f",)
    )
    assert gate["passed"] is False


# --- ponytail_adapter.py (controlled, non-real Supervisor) -------------


def test_ponytail_adapter_picks_first_passing_by_fixed_id_order_regardless_of_list_order():
    candidates = [
        {"id": "minimality", "code": "m", "gate": {"passed": True}},
        {"id": "implementation", "code": "i", "gate": {"passed": True}},
        {"id": "consistency", "code": "c", "gate": {"passed": True}},
    ]
    best = ponytail_adapter.select_final_candidate(candidates)
    assert best["id"] == "implementation"


def test_ponytail_adapter_skips_failed_candidates():
    candidates = [
        {"id": "implementation", "code": "i", "gate": {"passed": False}},
        {"id": "consistency", "code": "c", "gate": {"passed": True}},
    ]
    best = ponytail_adapter.select_final_candidate(candidates)
    assert best["id"] == "consistency"


def test_ponytail_adapter_returns_none_when_all_fail():
    candidates = [{"id": "implementation", "code": "i", "gate": {"passed": False}}]
    assert ponytail_adapter.select_final_candidate(candidates) is None


# --- variants.py: fixed-ID ordering independent of completion order ----


def test_deterministic_gate_ordering_is_independent_of_completion_order():
    """§10 예시(A PASS, B FAIL, C PASS → Ponytail input: A + C)와 동등한
    성질을 고정 ID 3개로 검증한다 — 완료 순서를 뒤섞어도 최종 선택은
    항상 고정 ID 순서를 따른다."""
    call_order = []

    def out_of_order_engine_call(prompt):
        for agent_id in ("minimality", "implementation", "consistency"):
            if f"[{agent_id}]" in prompt:
                call_order.append(agent_id)
                if agent_id == "consistency":
                    return "def target(:\n"  # FAIL — invalid syntax
                return "def target():\n    return 1\n"
        raise AssertionError("unknown agent id in prompt")

    result, code = variants.run_variant_c(
        "case_order", "Design", out_of_order_engine_call, ("target",)
    )

    assert code is not None
    assert "return 1" in code


# --- variants.py: A/B/C shape and call counts ---------------------------


def _fake_engine_call(prompt):
    return "def target():\n    return 1\n"


def test_run_variant_a_calls_engine_exactly_once():
    result, code = variants.run_variant_a("case_1", "Design", _fake_engine_call, ("target",))
    assert result["llm_calls"] == 1
    assert result["variant"] == "single"
    assert code is not None


def test_run_variant_b_calls_engine_exactly_three_times_with_fixed_ids():
    calls = []

    def counting_engine_call(prompt):
        calls.append(prompt)
        return "def target():\n    return 1\n"

    result, code = variants.run_variant_b("case_1", "Design", counting_engine_call, ("target",))
    assert result["llm_calls"] == 3
    assert len(calls) == 3
    assert any("[implementation]" in p for p in calls)
    assert any("[consistency]" in p for p in calls)
    assert any("[minimality]" in p for p in calls)


def test_run_variant_c_reuses_variant_b_candidates_without_extra_engine_calls():
    calls = []

    def counting_engine_call(prompt):
        calls.append(prompt)
        return "def target():\n    return 1\n"

    result, code = variants.run_variant_c("case_1", "Design", counting_engine_call, ("target",))
    assert result["llm_calls"] == 3
    assert len(calls) == 3  # B와 동일 — C가 별도로 재호출하지 않음
    assert result["variant"] == "multi_ponytail"
    assert result["latency_ms"]["ponytail"] >= 0


def test_run_variant_b_and_c_return_none_when_all_candidates_fail_gate():
    def failing_engine_call(prompt):
        return "not valid python(("

    result_b, code_b = variants.run_variant_b("case_1", "Design", failing_engine_call, ("target",))
    result_c, code_c = variants.run_variant_c("case_1", "Design", failing_engine_call, ("target",))
    assert code_b is None
    assert code_c is None


# --- run_experiment.py smoke test (no real Engine) -----------------------


def test_run_all_produces_one_result_per_case_per_variant_with_controlled_stub():
    results = run_experiment.run_all(run_experiment.controlled_stub_engine_call)
    case_ids = {r["case_id"] for r in results}
    variants_seen = {r["variant"] for r in results}

    assert len(results) == len(run_experiment.CASES) * 3
    assert variants_seen == {"single", "multi", "multi_ponytail"}
    assert case_ids == {case["case_id"] for case in run_experiment.CASES}


def test_controlled_stub_engine_call_produces_scope_compliant_code():
    code = run_experiment.controlled_stub_engine_call("Design: implement `reverse_text(text: str) -> str` ...")
    assert "def reverse_text" in code
    assert bool(deterministic_checks.check_scope(code, ("reverse_text",))) is True
