"""`call_engine_via_chatgpt()` 단위 테스트(로컬 test double, 실제
egress 없음). `call_engine_via_omniroute()`(`test_omniroute_engine.py`)와
동일한 외부 계약(`str -> str`, 실패 시 `RuntimeError`)을 지키는지
확인한다 — `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp.chatgpt_engine import call_engine_via_chatgpt

from .fake_omniroute_server import FakeOmniRouteServer


def test_success_returns_message_content(monkeypatch):
    with FakeOmniRouteServer(mode="success") as base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", base_url)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        assert call_engine_via_chatgpt("hello") == "FAKE_OMNIROUTE_OK"


def test_upstream_500_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="error500") as base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", base_url)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_chatgpt("hello")
        assert "500" in str(exc_info.value)


def test_rate_limit_429_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="error429") as base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", base_url)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_chatgpt("hello")
        assert "429" in str(exc_info.value)


def test_malformed_response_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="malformed") as base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", base_url)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        with pytest.raises(RuntimeError):
            call_engine_via_chatgpt("hello")


def test_connection_refused_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("CHATGPT_BASE_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with pytest.raises(RuntimeError) as exc_info:
        call_engine_via_chatgpt("hello")
    assert "connection" in str(exc_info.value).lower()


def test_timeout_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="slow", slow_seconds=2) as base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", base_url)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("CHATGPT_TIMEOUT_SECONDS", "0.3")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_chatgpt("hello")
        assert "timed out" in str(exc_info.value).lower()


def test_default_model_is_gpt_4o(monkeypatch):
    monkeypatch.delenv("CHATGPT_MODEL", raising=False)
    from mvp import chatgpt_engine
    _base_url, _api_key, model, _timeout = chatgpt_engine._resolve_config()
    assert model == "gpt-4o"


def test_uses_http_proxy_env_var(monkeypatch):
    """`http_proxy`/`HTTPS_PROXY`를 실제로 경유하는지 확인한다 —
    Agent Egress Proxy 우회(Root Cause) 재발 방지 회귀 테스트.
    존재하지 않는 upstream(`192.0.2.1`, TEST-NET-1)을 `CHATGPT_BASE_URL`로
    주고, `http_proxy`만 로컬 fake 서버로 돌려 놓는다 — 프록시를 거치지
    않으면 연결이 실패하고, 거치면 fake 서버 응답을 그대로 받는다."""
    with FakeOmniRouteServer(mode="success") as proxy_base_url:
        monkeypatch.setenv("CHATGPT_BASE_URL", "http://192.0.2.1:9")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("http_proxy", proxy_base_url)
        monkeypatch.setenv("HTTP_PROXY", proxy_base_url)
        assert call_engine_via_chatgpt("hello") == "FAKE_OMNIROUTE_OK"


def test_api_key_read_only_from_env_not_hardcoded():
    """소스에 실제 API Key 형태의 리터럴이 없는지 정적으로 확인한다
    (`sk-`로 시작하는 OpenAI Key 접두어 부재)."""
    source = Path(__file__).resolve().parent.parent.joinpath("chatgpt_engine.py").read_text(encoding="utf-8")
    assert "sk-" not in source
    assert 'os.environ.get("OPENAI_API_KEY"' in source
