"""Thin Caller의 request 변환·response 파싱·오류 매핑 단위 테스트.

로컬 test double(`fake_server.py`)만 사용한다 — 실제 OmniRoute 서버는
쓰지 않는다(비용/egress 없음). "정상 응답" 테스트는 Caller가 OmniRoute
OpenAI-compatible 응답 형태를 올바르게 파싱한다는 것만 증명한다 —
실제 OmniRoute의 동작을 증명하지 않는다.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import caller as omniroute_caller  # noqa: E402
from fake_server import FakeOmniRouteServer, success_body  # noqa: E402


def test_success_returns_message_content():
    with FakeOmniRouteServer(status=200, body=success_body("정상 응답 텍스트")) as server:
        result = omniroute_caller.call_omniroute(
            "hello", base_url=server.base_url, api_key="test-key",
        )
    assert result == "정상 응답 텍스트"


def test_request_is_openai_compatible_shape():
    with FakeOmniRouteServer(status=200) as server:
        omniroute_caller.call_omniroute(
            "번역해줘: hello", base_url=server.base_url, api_key="secret-abc",
            model="auto",
        )
    assert len(server.received_requests) == 1
    req = server.received_requests[0]
    assert req["path"] == "/api/v1/chat/completions"
    assert req["headers"]["Authorization"] == "Bearer secret-abc"
    assert req["body"] == {
        "model": "auto",
        "messages": [{"role": "user", "content": "번역해줘: hello"}],
    }


def test_default_model_is_auto_when_unspecified():
    with FakeOmniRouteServer(status=200) as server:
        omniroute_caller.call_omniroute("hi", base_url=server.base_url, api_key="k")
    assert server.received_requests[0]["body"]["model"] == "auto"


@pytest.mark.parametrize(
    "status,expected_exc",
    [
        (401, omniroute_caller.OmniRouteAuthError),
        (403, omniroute_caller.OmniRouteAuthError),
        (429, omniroute_caller.OmniRouteBudgetExceededError),
        (500, omniroute_caller.OmniRouteProviderError),
        (503, omniroute_caller.OmniRouteProviderError),
        (400, omniroute_caller.OmniRouteCallError),
    ],
)
def test_error_status_codes_map_to_typed_exceptions(status, expected_exc):
    with FakeOmniRouteServer(status=status, body={"error": "synthetic"}) as server:
        with pytest.raises(expected_exc):
            omniroute_caller.call_omniroute(
                "hello", base_url=server.base_url, api_key="k",
            )


def test_malformed_response_shape_raises_call_error():
    with FakeOmniRouteServer(status=200, body={"unexpected": "shape"}) as server:
        with pytest.raises(omniroute_caller.OmniRouteCallError):
            omniroute_caller.call_omniroute(
                "hello", base_url=server.base_url, api_key="k",
            )


def test_connection_refused_raises_connection_error():
    # 어떤 서버도 듣지 않는 포트 — 실제 네트워크 호출 없이 즉시 실패.
    with pytest.raises(omniroute_caller.OmniRouteConnectionError):
        omniroute_caller.call_omniroute(
            "hello", base_url="http://127.0.0.1:1", api_key="k", timeout=2,
        )


def test_timeout_raises_timeout_error():
    with FakeOmniRouteServer(status=200, delay_seconds=2.0) as server:
        with pytest.raises(omniroute_caller.OmniRouteTimeoutError):
            omniroute_caller.call_omniroute(
                "hello", base_url=server.base_url, api_key="k", timeout=0.2,
            )


def test_env_vars_used_when_kwargs_omitted(monkeypatch):
    with FakeOmniRouteServer(status=200) as server:
        monkeypatch.setenv("OMNIROUTE_BASE_URL", server.base_url)
        monkeypatch.setenv("OMNIROUTE_API_KEY", "env-key-value")
        omniroute_caller.call_omniroute("hello")
    assert server.received_requests[0]["headers"]["Authorization"] == "Bearer env-key-value"
