"""OpenRouter Auto Selection v1 Harness 테스트(사용자 지시 §14). 실제
네트워크 호출 없이 검증 가능한 것은 전부 Mock/Fault Injection으로
수행한다(§11 원칙 — 외부 서비스를 실제로 공격/rate-limit 유발하지
않는다)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from domain.auto_selection_client import (  # noqa: E402
    call_with_auto_selection,
    classify_failure,
)
from domain.contracts import ContractResult, stage01_contract, stage03_contract  # noqa: E402
from domain.model_pool import MAX_MODELS_PER_REQUEST, fetch_free_model_pool  # noqa: E402
from domain.stage_policy import STAGE_POLICIES  # noqa: E402


# ---- 1. No fixed model enforcement ----------------------------------------


def test_stage_policy_has_no_model_field():
    """StagePolicy 필드 목록 어디에도 모델 이름을 담는 필드가 없다(사용자
    지시 §4 — "Stage Policy에는 모델 이름을 넣지 않는다")."""
    import dataclasses

    from domain.stage_policy import StagePolicy

    field_names = {f.name for f in dataclasses.fields(StagePolicy)}
    forbidden = {"model", "model_name", "model_id", "fixed_model"}
    assert not (field_names & forbidden), f"StagePolicy에 모델 이름 필드가 있다: {field_names & forbidden}"


def test_auto_selection_client_accepts_a_pool_not_a_single_model():
    import inspect

    params = list(inspect.signature(call_with_auto_selection).parameters)
    assert "models_pool" in params
    assert "model" not in params  # 단일 고정 모델 인자가 없다


# ---- 2. Stage policy validation ---------------------------------------------


def test_all_five_stage_policies_exist_with_required_fields():
    expected_stages = {"stage01", "stage02", "stage03", "stage04", "stage05_review"}
    assert set(STAGE_POLICIES.keys()) == expected_stages
    for stage, policy in STAGE_POLICIES.items():
        assert policy.free_only is True
        assert policy.token_budget > 0
        assert policy.timeout_seconds > 0
        assert callable(policy.output_contract)
        assert policy.token_budget_source  # 출처 문자열이 비어있지 않음(추정 아님을 항상 기록)


# ---- 3. Contract validation(기존 production parser 재사용 확인) -----------


def test_stage01_contract_reuses_real_production_parser():
    from domain.contracts import parse_structured_output

    import inspect

    # production reasoning.py 파일 경로에서 그대로 로드됐는지 소스 파일 확인.
    source_file = inspect.getsourcefile(parse_structured_output)
    assert "stages/01_context_analysis/reasoning.py" in source_file.replace("\\", "/")


def test_stage01_contract_passes_on_well_formed_json():
    good = '{"functional_requirements": ["a"], "non_functional_requirements": [], "constraints": [], "scope_candidates": [], "confidence": 0.9}'
    result = stage01_contract(good)
    assert result.passed is True


def test_stage01_contract_fails_on_missing_keys():
    bad = '{"functional_requirements": ["a"]}'
    result = stage01_contract(bad)
    assert result.passed is False
    assert "confidence" in result.detail["missing_keys"]


def test_stage03_contract_fails_when_sections_missing():
    result = stage03_contract("Architecture Definition: ...\nComponent Identification: ...")
    assert result.passed is False
    assert "Data Flow" in result.detail["missing_sections"]


# ---- 4. Retry bound ---------------------------------------------------------


def test_retry_count_never_exceeds_policy_max_retries(monkeypatch):
    """모든 attempt가 실패하도록 fault injection — retry_count가
    `max_retries`를 절대 넘지 않는지 확인한다."""
    import domain.auto_selection_client as client_module

    def _always_fail(*args, **kwargs):
        return {"http_status": 500, "elapsed_ms": 1.0, "error": None, "parsed": {"error": {"message": "boom"}}}

    monkeypatch.setattr(client_module, "_single_call", _always_fail)

    result = call_with_auto_selection(
        "stage01", "prompt", ("a:free", "b:free", "c:free"),
        output_contract=stage01_contract, max_tokens=100, timeout=5, max_retries=1,
    )
    assert result.success is False
    assert result.retry_count <= 1
    assert len(result.attempts) == 2  # 최초 1회 + 재시도 1회


# ---- 5. Failure classification ----------------------------------------------


def test_classify_failure_maps_http_statuses_correctly():
    assert classify_failure({"http_status": 429, "error": None}) == "http_429"
    assert classify_failure({"http_status": 502, "error": None}) == "http_5xx"
    assert classify_failure({"http_status": 400, "error": None}) == "malformed_output"
    assert classify_failure({"http_status": 200, "error": None}) is None
    assert classify_failure({"http_status": None, "error": "conn refused"}) == "connection_error"


def test_contract_failure_excludes_failed_model_from_retry_pool(monkeypatch):
    """Contract 실패 시, 재시도에서 같은 모델이 다시 응답 모델로 오더라도
    Pool에서는 제외된 상태로 다음 호출이 나가는지 확인(사용자 지시 §6 —
    "retry 시 다른 free model이 선택될 가능성을 고려한다")."""
    import domain.auto_selection_client as client_module

    call_log = []

    def _fake_call(models_offered, prompt, *, max_tokens, timeout):
        call_log.append(tuple(models_offered))
        return {
            "http_status": 200,
            "elapsed_ms": 1.0,
            "error": None,
            "parsed": {
                "model": models_offered[0],
                "usage": {},
                "choices": [{"message": {"content": "not valid json"}, "finish_reason": "stop"}],
            },
        }

    monkeypatch.setattr(client_module, "_single_call", _fake_call)

    def _always_fail_contract(content):
        return ContractResult(False, {"reason": "always fails for this test"})

    result = call_with_auto_selection(
        "stage01", "prompt", ("a:free", "b:free", "c:free"),
        output_contract=_always_fail_contract, max_tokens=100, timeout=5, max_retries=1,
    )
    assert result.success is False
    assert len(call_log) == 2
    assert call_log[0] == ("a:free", "b:free", "c:free")
    assert "a:free" not in call_log[1]  # 실패한 모델이 재시도 Pool에서 빠짐


# ---- 6. Selected model recording -------------------------------------------


def test_successful_result_records_the_actually_selected_model(monkeypatch):
    import domain.auto_selection_client as client_module

    def _fake_call(models_offered, prompt, *, max_tokens, timeout):
        return {
            "http_status": 200,
            "elapsed_ms": 5.0,
            "error": None,
            "parsed": {
                "model": "b:free",  # Pool의 2번째가 실제로 선택된 상황을 흉내
                "usage": {"total_tokens": 10},
                "choices": [{"message": {"content": '{"functional_requirements": [], "non_functional_requirements": [], "constraints": [], "scope_candidates": [], "confidence": 0.5}'}, "finish_reason": "stop"}],
            },
        }

    monkeypatch.setattr(client_module, "_single_call", _fake_call)
    result = call_with_auto_selection(
        "stage01", "prompt", ("a:free", "b:free", "c:free"),
        output_contract=stage01_contract, max_tokens=100, timeout=5,
    )
    assert result.success is True
    assert result.final_selected_model == "b:free"


# ---- 7. Deterministic result ordering ---------------------------------------


def test_attempts_list_preserves_chronological_order_not_reordered(monkeypatch):
    import domain.auto_selection_client as client_module

    responses = iter(
        [
            {"http_status": 429, "elapsed_ms": 1.0, "error": None, "parsed": {"error": {"message": "rate limited"}}},
            {
                "http_status": 200,
                "elapsed_ms": 2.0,
                "error": None,
                "parsed": {
                    "model": "b:free",
                    "usage": {},
                    "choices": [{"message": {"content": '{"functional_requirements": [], "non_functional_requirements": [], "constraints": [], "scope_candidates": [], "confidence": 0.5}'}, "finish_reason": "stop"}],
                },
            },
        ]
    )

    def _fake_call(*args, **kwargs):
        return next(responses)

    monkeypatch.setattr(client_module, "_single_call", _fake_call)
    result = call_with_auto_selection(
        "stage01", "prompt", ("a:free", "b:free", "c:free"),
        output_contract=stage01_contract, max_tokens=100, timeout=5, max_retries=1,
    )
    assert [a.attempt_number for a in result.attempts] == [1, 2]
    assert result.attempts[0].failure_class == "http_429"
    assert result.attempts[1].failure_class is None


# ---- 8. Stage isolation ------------------------------------------------------


def test_stage_policies_do_not_share_mutable_pool_state():
    """Stage마다 별도의 `StagePolicy` 인스턴스이며, 한 Stage의 정책 객체를
    변경해도 다른 Stage에 영향이 없다(단순 dict/dataclass 격리 확인)."""
    s1 = STAGE_POLICIES["stage01"]
    s2 = STAGE_POLICIES["stage02"]
    assert s1 is not s2
    assert s1.output_contract is not s2.output_contract


# ---- 9. No production routing mutation --------------------------------------


def test_harness_does_not_import_or_modify_production_engine_modules():
    """`mvp/chatgpt_engine.py`/`mvp/engine.py`/`stages/05_validation/
    stage_05.py`의 실제 Engine 선택 로직을 이 Harness가 import하거나
    패치하지 않는지 소스 코드 수준으로 확인한다(정적 검사)."""
    harness_files = list(HARNESS_ROOT.rglob("*.py"))
    forbidden_imports = ("chatgpt_engine", "mvp.engine", "omniroute_engine")
    for path in harness_files:
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            assert forbidden not in text, f"{path}가 Production Engine 모듈({forbidden})을 참조한다"


def test_model_pool_cap_matches_openrouter_measured_limit():
    """OpenRouter `models` 배열의 실측 상한(3개, 이 세션이 HTTP 400으로
    확인)과 이 Harness의 기본 `limit`이 일치하는지 고정한다 — 회귀 방지."""
    assert MAX_MODELS_PER_REQUEST == 3
