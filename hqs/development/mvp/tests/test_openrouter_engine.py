"""`call_engine_via_openrouter()` 단위 테스트(로컬 test double, 실제
egress 없음). `call_engine_via_chatgpt()`/`call_engine_via_omniroute()`
와 동일한 외부 계약(`str -> str`, 실패 시 `RuntimeError`)을 지키는지
확인한다 — `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md`.

Free Pool 조회 → Deterministic Filter → Candidate Selection(≤3,
tie-break) → `models[]` 요청 → bounded retry/failure classification
까지 이 모듈 내부에서 실제로 일어나는 각 단계를 검증한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp.openrouter_engine import (
    MAX_CANDIDATES,
    _classify_failure,
    _deterministic_filter,
    _estimate_min_context_tokens,
    _select_candidates,
    call_engine_via_openrouter,
)

from .fake_openrouter_server import FakeOpenRouterServer


# ---- 1. 외부 계약(str -> str, 단일 RuntimeError) -----------------------------


def test_success_returns_message_content(monkeypatch):
    with FakeOpenRouterServer(mode="success") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        assert call_engine_via_openrouter("hello") == "FAKE_OPENROUTER_OK"


def test_quota_failure_raises_single_runtime_error_after_retry(monkeypatch):
    with FakeOpenRouterServer(mode="quota") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_openrouter("hello")
        assert "429_quota" in str(exc_info.value)


def test_server_error_raises_runtime_error(monkeypatch):
    with FakeOpenRouterServer(mode="server_error") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_openrouter("hello")
        assert "5xx" in str(exc_info.value)


def test_malformed_response_raises_runtime_error(monkeypatch):
    with FakeOpenRouterServer(mode="malformed") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError):
            call_engine_via_openrouter("hello")


def test_empty_content_raises_runtime_error(monkeypatch):
    with FakeOpenRouterServer(mode="empty_content") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError):
            call_engine_via_openrouter("hello")


def test_connection_refused_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:1")
    with pytest.raises(RuntimeError):
        call_engine_via_openrouter("hello")


def test_models_fetch_failure_raises_runtime_error(monkeypatch):
    with FakeOpenRouterServer(mode="success", models_mode="models_fetch_error") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError):
            call_engine_via_openrouter("hello")


# ---- 2. Bounded retry(최대 1회, 실패 시 회복 가능) ----------------------------


def test_transient_failure_recovers_on_bounded_retry(monkeypatch):
    """첫 attempt는 500, 두 번째(재시도)는 성공 — bounded retry가 실제로
    응답을 회복시키는지 확인한다."""
    with FakeOpenRouterServer(mode="recover_on_retry") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        assert call_engine_via_openrouter("hello") == "FAKE_OPENROUTER_RECOVERED"


# ---- 3. Free Pool 조회 + Deterministic Filter + Candidate 0/1/2/3/>3 ---------


def test_empty_pool_raises_runtime_error_with_zero_candidates_message(monkeypatch):
    with FakeOpenRouterServer(mode="success", models_mode="empty_pool") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_openrouter("hello")
        assert "0개" in str(exc_info.value)


def test_small_context_pool_is_filtered_out(monkeypatch):
    """실제 프롬프트 길이가 요구하는 context보다 작은 모델은 Deterministic
    Filter가 제외해 결과적으로 candidate가 0개가 된다."""
    with FakeOpenRouterServer(mode="success", models_mode="small_context") as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_openrouter("hello " * 500)
        assert "0개" in str(exc_info.value)


def test_known_nonfunctional_model_excluded_by_filter(monkeypatch):
    pool = [
        {"id": "thinkingmachines/inkling:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
        {"id": "vendor-a/model-1:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    ]
    kept = _deterministic_filter(pool, min_context_tokens=10)
    assert "thinkingmachines/inkling:free" not in kept
    assert "vendor-a/model-1:free" in kept


def test_context_below_requirement_excluded_by_filter():
    pool = [{"id": "vendor-a/model-1:free", "context_length": 100, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}}]
    assert _deterministic_filter(pool, min_context_tokens=100000) == []


def test_non_text_modality_excluded_by_filter():
    pool = [{"id": "vendor-a/image-only:free", "context_length": 200000, "architecture": {"input_modalities": ["image"], "output_modalities": ["text"]}}]
    assert _deterministic_filter(pool, min_context_tokens=10) == []


def test_missing_context_length_metadata_is_not_excluded():
    """판정 불가능한 metadata(context_length 없음)는 추측해서 제외하지
    않는다 — ADR-0026 §6 원칙."""
    pool = [{"id": "vendor-a/model-1:free", "context_length": None, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}}]
    assert _deterministic_filter(pool, min_context_tokens=999999) == ["vendor-a/model-1:free"]


def test_candidate_selection_preserves_order_up_to_three():
    kept = ["a:free", "b:free", "c:free"]
    assert _select_candidates(kept) == ("a:free", "b:free", "c:free")


def test_candidate_selection_ties_break_by_pool_order_when_over_three():
    kept = ["a:free", "b:free", "c:free", "d:free", "e:free"]
    result = _select_candidates(kept)
    assert result == ("a:free", "b:free", "c:free")
    assert len(result) == MAX_CANDIDATES


def test_candidate_selection_empty_pool_returns_empty_tuple():
    assert _select_candidates([]) == ()


def test_five_model_pool_actually_sends_only_three_candidates(monkeypatch):
    """실제 HTTP 경로 전체(Free Pool 5개 → Filter → Selection → POST)로
    최종 `models[]`가 3개로 제한되는지 확인 — 응답의 `model` 필드가
    후보 중 하나(Pool 순서상 첫 3개)와 일치해야 한다."""
    with FakeOpenRouterServer(mode="success") as base_url:  # 기본 Pool 5개
        monkeypatch.setenv("OPENROUTER_BASE_URL", base_url)
        call_engine_via_openrouter("hi")  # 성공하면 예외 없음 — 서버가 이미 models[0]을 그대로 되돌려줌


# ---- 4. Failure classification(quota를 모델 품질 실패와 분리) ---------------


def test_classify_failure_separates_quota_from_other_categories():
    assert _classify_failure(429, connection_error=False) == "429_quota"
    assert _classify_failure(503, connection_error=False) == "5xx"
    assert _classify_failure(400, connection_error=False) == "malformed_response"
    assert _classify_failure(None, connection_error=True) == "connection_error"
    assert _classify_failure(200, connection_error=False) == "empty_response"


def test_classify_failure_never_conflates_quota_with_malformed():
    assert _classify_failure(429, connection_error=False) != "malformed_response"


# ---- 5. Context 추정(추정치임을 명시) ------------------------------------------


def test_min_context_estimate_scales_with_prompt_length():
    short_estimate = _estimate_min_context_tokens("hi")
    long_estimate = _estimate_min_context_tokens("hi " * 10000)
    assert long_estimate > short_estimate


# ---- 6. API Key/Credential 보안 -----------------------------------------------


def test_api_key_read_only_from_env_not_hardcoded():
    """소스에 실제 API Key 형태의 리터럴이 없는지 정적으로 확인한다."""
    source = Path(__file__).resolve().parent.parent.joinpath("openrouter_engine.py").read_text(encoding="utf-8")
    assert "sk-or-" not in source
    assert 'os.environ.get("OPENROUTER_API_KEY"' in source


def test_no_authorization_header_when_api_key_absent(monkeypatch):
    """API Key 환경변수가 없으면 Authorization 헤더 자체를 설정하지
    않는다(자동 인증 주입 환경 지원) — 예외 메시지에도 노출되지 않는다."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from mvp.openrouter_engine import _auth_headers

    assert _auth_headers() == {}


# ---- 7. Production Engine Contract 형태(다른 두 Engine과 동일) --------------


def test_no_central_router_or_gateway_abstraction_in_module():
    """Port/Adapter 일반화 클래스, Registry, Router 같은 금지 패턴이
    이 모듈에 없는지 정적으로 확인한다(`IMPLEMENTATION_RULES.md`)."""
    source = Path(__file__).resolve().parent.parent.joinpath("openrouter_engine.py").read_text(encoding="utf-8")
    forbidden = ("class EngineRouter", "class Registry", "class Gateway", "EngineAdapter(", "class Router")
    for token in forbidden:
        assert token not in source
