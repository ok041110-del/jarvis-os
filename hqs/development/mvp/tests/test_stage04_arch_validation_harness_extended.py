"""Stage 04 Architecture Validation Harness 확장 검증(RFC 요청 — Stage 04
Architecture Validation을 계속 진행: Design coverage, Quality 구조 신호,
Ponytail Policy Guardrail, Cost Instrumentation). 전부 결정적 코드
검사이거나(§4 OmniRoute 없이 가능한 검증), 로컬 loopback double로 재현
가능한 것만 다룬다 — 실제 OmniRoute를 호출하지 않는다."""

import importlib.util
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

_HARNESS_DIR = (
    Path(__file__).resolve().parents[2] / "stages" / "04_implementation" / "architecture_validation"
)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


deterministic_checks = _load("arch_val_deterministic_checks_ext", _HARNESS_DIR / "deterministic_checks.py")
quality_heuristics = _load("arch_val_quality_heuristics", _HARNESS_DIR / "quality_heuristics.py")
ponytail_policy = _load("arch_val_ponytail_policy", _HARNESS_DIR / "ponytail_policy.py")
cost_instrumentation = _load("arch_val_cost_instrumentation", _HARNESS_DIR / "cost_instrumentation.py")
variants = _load("arch_val_variants_ext", _HARNESS_DIR / "variants.py")


# --- check_dependency_validity -------------------------------------------


def test_check_dependency_validity_allows_ordinary_builtin_calls():
    """회귀 테스트: `dir(__builtins__)`가 모듈로 import된 상태에서는 dict가
    되어 `len`/`print` 같은 평범한 builtin 호출까지 "unresolved call
    target"으로 오판했던 결함(`import builtins`로 수정)."""
    code = "def f(xs):\n    return len(xs)\n"
    result = deterministic_checks.check_dependency_validity(code, ())
    assert bool(result) is True


def test_check_dependency_validity_allows_known_names():
    code = "def f(text):\n    return _truncate(text, 80)\n"
    result = deterministic_checks.check_dependency_validity(code, ("_truncate",))
    assert bool(result) is True


def test_check_dependency_validity_flags_unknown_call_targets():
    code = "def f(text):\n    return _mystery_helper(text)\n"
    result = deterministic_checks.check_dependency_validity(code, ("_truncate",))
    assert bool(result) is False
    assert "_mystery_helper" in result.detail


def test_check_dependency_validity_flags_syntax_error():
    result = deterministic_checks.check_dependency_validity("def f(:\n", ())
    assert bool(result) is False


# --- check_design_coverage / run_deterministic_gate extension ----------


def test_check_design_coverage_passes_when_all_required_defined():
    code = "def a():\n    pass\n\ndef b():\n    pass\n"
    assert bool(deterministic_checks.check_design_coverage(code, ("a", "b"))) is True


def test_check_design_coverage_fails_when_required_missing():
    code = "def a():\n    pass\n"
    result = deterministic_checks.check_design_coverage(code, ("a", "b"))
    assert bool(result) is False
    assert "b" in result.detail


def test_run_deterministic_gate_defaults_required_to_allowed_for_backward_compat():
    gate = deterministic_checks.run_deterministic_gate(
        "def f():\n    pass\n", required_keys=(), allowed_function_names=("f",)
    )
    assert gate["passed"] is True
    assert "design_coverage" in gate["checks"]


def test_run_deterministic_gate_distinguishes_allowed_from_required():
    """case_c_helper_reuse류 시나리오: `_truncate`는 허용되지만 필수는
    아니다 — 정의하지 않아도 통과해야 한다."""
    code = "def summarize_lines(lines):\n    return lines\n"
    gate = deterministic_checks.run_deterministic_gate(
        code,
        required_keys=(),
        allowed_function_names=("summarize_lines", "_truncate"),
        required_function_names=("summarize_lines",),
    )
    assert gate["passed"] is True


# --- quality_heuristics.py -----------------------------------------------


def test_count_ternary_expressions():
    code = "def f(x):\n    return 1 if x else 2\n"
    assert quality_heuristics.count_ternary_expressions(code) == 1


def test_max_comprehension_nesting():
    flat = "def f(xs):\n    return [x for x in xs]\n"
    nested = "def f(xs):\n    return [[y for y in x] for x in xs]\n"
    assert quality_heuristics.max_comprehension_nesting(flat) == 1
    assert quality_heuristics.max_comprehension_nesting(nested) == 2


def test_max_chained_calls():
    code = "def f(x):\n    return x.a().b().c()\n"
    assert quality_heuristics.max_chained_calls(code) == 3


def test_count_lambda():
    code = "def f():\n    g = lambda x: x + 1\n    return g\n"
    assert quality_heuristics.count_lambda(code) == 1


def test_max_control_flow_nesting():
    code = "def f(x):\n    if x:\n        for i in range(x):\n            while i:\n                i -= 1\n"
    assert quality_heuristics.max_control_flow_nesting(code) == 3


def test_explicitness_issue_count_is_zero_for_plain_code():
    plain = "def f(x):\n    if x:\n        return 1\n    return 2\n"
    assert quality_heuristics.explicitness_issue_count(plain) == 0


def test_explicitness_issue_count_returns_negative_one_on_syntax_error():
    assert quality_heuristics.explicitness_issue_count("def f(:\n") == -1


def test_simplicity_issue_count_increases_with_nesting():
    flat = "def f(x):\n    return x\n"
    nested = "def f(x):\n    if x:\n        for i in range(x):\n            return i\n"
    assert quality_heuristics.simplicity_issue_count(nested) > quality_heuristics.simplicity_issue_count(flat)


# --- ponytail_policy.py --------------------------------------------------


def test_check_target_unchanged_detects_drift():
    assert bool(ponytail_policy.check_target_unchanged(("m", "f"), ("m", "f"))) is True
    assert bool(ponytail_policy.check_target_unchanged(("m", "f"), ("m", "g"))) is False


def test_check_no_new_imports_flags_added_dependency():
    before = "def f():\n    pass\n"
    after = "import os\n\ndef f():\n    return os.getcwd()\n"
    assert bool(ponytail_policy.check_no_new_imports(before, after)) is False


def test_check_no_new_imports_allows_identical_imports():
    code = "import os\n\ndef f():\n    return os.getcwd()\n"
    assert bool(ponytail_policy.check_no_new_imports(code, code)) is True


def test_check_scope_unchanged_flags_new_function():
    before = "def f():\n    pass\n"
    after = "def f():\n    pass\n\ndef g():\n    pass\n"
    assert bool(ponytail_policy.check_scope_unchanged(before, after)) is False


def test_check_no_op_when_gate_passed_flags_unnecessary_modification():
    before = "def f():\n    return 1\n"
    after = "def f():\n    return 2\n"
    assert bool(ponytail_policy.check_no_op_when_gate_passed(before, after, gate_passed_before=True)) is False
    assert bool(ponytail_policy.check_no_op_when_gate_passed(before, after, gate_passed_before=False)) is True


def test_verify_policy_passes_for_pure_selection_no_mutation():
    """현재 ponytail_adapter는 순수 선택만 하고 코드를 수정하지 않는다 —
    이 경우 정책 7개 중 코드 검사 가능한 항목이 전부 공허하게 만족돼야
    한다(README의 "0% refinement" 설명과 일치)."""
    code = "def f():\n    return 1\n"
    result = ponytail_policy.verify_policy(
        target_before=("m", "f"), target_after=("m", "f"),
        code_before=code, code_after=code, gate_passed_before=True,
    )
    assert result["passed"] is True


# --- cost_instrumentation.py (local loopback double, no real OmniRoute) -


class _UsageDoubleHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length) if length else b""
        payload = json.dumps({
            "choices": [{"message": {"content": "HARNESS_COST_TEST_OK"}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@pytest.fixture
def usage_double_server():
    server = HTTPServer(("127.0.0.1", 0), _UsageDoubleHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_call_with_usage_parses_openai_style_usage_field(usage_double_server, monkeypatch):
    monkeypatch.setenv("OMNIROUTE_BASE_URL", usage_double_server)
    monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
    monkeypatch.setenv("OMNIROUTE_MODEL", "test-model")

    text, usage = cost_instrumentation.call_with_usage("hello")

    assert text == "HARNESS_COST_TEST_OK"
    assert usage == {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}


def test_usage_to_result_fields_maps_openai_keys():
    fields = cost_instrumentation.usage_to_result_fields(
        {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}
    )
    assert fields == {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18}


def test_usage_to_result_fields_stays_none_when_usage_missing():
    fields = cost_instrumentation.usage_to_result_fields(None)
    assert fields == {"input_tokens": None, "output_tokens": None, "total_tokens": None}


# --- Failure Policy: 3/3, 2/3, 1/3, 0/3 (variants.py) ---------------------


def _engine_call_with_pass_count(pass_count: int):
    """`implementation`/`consistency`/`minimality` 중 앞에서부터 정확히
    `pass_count`개만 통과시키고 나머지는 SyntaxError 코드를 반환한다."""
    passing_ids = set(("implementation", "consistency", "minimality")[:pass_count])

    def _call(prompt):
        for agent_id in ("implementation", "consistency", "minimality"):
            if f"[{agent_id}]" in prompt:
                if agent_id in passing_ids:
                    return "def target():\n    return 1\n"
                return "def target(:\n"  # SyntaxError — FAIL
        raise AssertionError("unknown agent id in prompt")

    return _call


@pytest.mark.parametrize("runner", [variants.run_variant_b, variants.run_variant_c])
def test_failure_policy_3_of_3_proceeds_normally(runner):
    result, code = runner("case_x", "Design", _engine_call_with_pass_count(3), ("target",))
    assert code is not None


@pytest.mark.parametrize("runner", [variants.run_variant_b, variants.run_variant_c])
def test_failure_policy_2_of_3_proceeds_normally(runner):
    result, code = runner("case_x", "Design", _engine_call_with_pass_count(2), ("target",))
    assert code is not None


@pytest.mark.parametrize("runner", [variants.run_variant_b, variants.run_variant_c])
def test_failure_policy_1_of_3_proceeds_with_limited_result(runner):
    """1/3만 통과해도 "제한적 진행"으로 그 1개를 최종 후보로 채택한다 —
    실패로 취급해 `None`을 반환하지 않는다."""
    result, code = runner("case_x", "Design", _engine_call_with_pass_count(1), ("target",))
    assert code is not None


@pytest.mark.parametrize("runner", [variants.run_variant_b, variants.run_variant_c])
def test_failure_policy_0_of_3_fails(runner):
    result, code = runner("case_x", "Design", _engine_call_with_pass_count(0), ("target",))
    assert code is None


def test_variant_b_and_c_generate_identical_candidate_pool_from_same_engine_call():
    """A/B/C 공정성 재검증 — B와 C는 동일한 engine_call이 주어지면
    정확히 동일한 3개 후보(코드 내용까지)를 만들어야 한다. C가 Ponytail
    Adapter를 추가하는 것 외에 다른 변수를 바꾸지 않는지 확인한다."""
    def deterministic_engine_call(prompt):
        for agent_id in ("implementation", "consistency", "minimality"):
            if f"[{agent_id}]" in prompt:
                return f"def target():\n    return '{agent_id}'\n"
        raise AssertionError("unknown agent id")

    candidates_b, _, _ = variants._generate_and_gate_candidates(
        "Design", deterministic_engine_call, ("target",), ("target",)
    )
    candidates_c, _, _ = variants._generate_and_gate_candidates(
        "Design", deterministic_engine_call, ("target",), ("target",)
    )
    assert [c["code"] for c in candidates_b] == [c["code"] for c in candidates_c]
    assert [c["id"] for c in candidates_b] == [c["id"] for c in candidates_c]
