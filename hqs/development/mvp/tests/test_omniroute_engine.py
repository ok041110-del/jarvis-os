"""`call_engine_via_omniroute()` 단위 테스트(로컬 test double, 실제
egress 없음). `call_engine()`(기존, `test_engine.py`)과 동일한 외부
계약(`str -> str`, 실패 시 `RuntimeError`)을 지키는지 확인한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp.omniroute_engine import call_engine_via_omniroute

from .fake_omniroute_server import FakeOmniRouteServer


def test_success_returns_message_content(monkeypatch):
    with FakeOmniRouteServer(mode="success") as base_url:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        assert call_engine_via_omniroute("hello") == "FAKE_OMNIROUTE_OK"


def test_upstream_500_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="error500") as base_url:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_omniroute("hello")
        assert "500" in str(exc_info.value)


def test_budget_exceeded_429_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="error429") as base_url:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_omniroute("hello")
        assert "429" in str(exc_info.value)


def test_malformed_response_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="malformed") as base_url:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        with pytest.raises(RuntimeError):
            call_engine_via_omniroute("hello")


def test_connection_refused_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
    with pytest.raises(RuntimeError) as exc_info:
        call_engine_via_omniroute("hello")
    assert "connection" in str(exc_info.value).lower()


def test_timeout_raises_runtime_error(monkeypatch):
    with FakeOmniRouteServer(mode="slow", slow_seconds=2) as base_url:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        monkeypatch.setenv("OMNIROUTE_TIMEOUT_SECONDS", "0.3")
        with pytest.raises(RuntimeError) as exc_info:
            call_engine_via_omniroute("hello")
        assert "timed out" in str(exc_info.value).lower()


def test_default_model_is_auto(monkeypatch):
    monkeypatch.delenv("OMNIROUTE_MODEL", raising=False)
    from mvp import omniroute_engine
    _base_url, _api_key, model, _timeout = omniroute_engine._resolve_config()
    assert model == "auto"
