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


def test_api_key_read_only_from_env_not_hardcoded():
    """소스에 실제 API Key 형태의 리터럴이 없는지 정적으로 확인한다
    (`sk-`로 시작하는 OpenAI Key 접두어 부재)."""
    source = Path(__file__).resolve().parent.parent.joinpath("chatgpt_engine.py").read_text(encoding="utf-8")
    assert "sk-" not in source
    assert 'os.environ.get("OPENAI_API_KEY"' in source
