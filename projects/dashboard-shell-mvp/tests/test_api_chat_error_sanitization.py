"""`api/chat.py` — OpenRouter 호출 실패 시 원본 예외 메시지 비노출 검증.

`call_engine_via_openrouter()` 실패의 `str(exc)`에는 API Key, Authorization
Header, 환경변수 값 등 Secret이 포함될 수 있다. 이 테스트는 그런 원본
메시지가 HTTP 응답(및 캡처된 stderr)에 그대로 노출되지 않는지, 안전한
고정 문구로만 응답하는지를 검증한다. 실제 Secret은 사용하지 않고
가상의 문자열만 사용한다.
"""

from __future__ import annotations

import http.server
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "api"
sys.path.insert(0, str(API_DIR))

import pytest  # noqa: E402

import chat as chat_module  # noqa: E402

STAGED_PATH = API_DIR / "openrouter_engine.py"

FAKE_API_KEY = "sk-or-v1-FAKE0000000000000000000000000000000000000000000000"
FAKE_AUTH_HEADER = "Authorization: Bearer " + FAKE_API_KEY


def _stub_source(reply_or_raise: str) -> str:
    return (
        "def call_engine_via_openrouter(prompt: str) -> str:\n"
        f"    raise RuntimeError({reply_or_raise!r})\n"
    )


@pytest.fixture()
def chat_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), chat_module.handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        thread.join(timeout=2)


def _post(port: int, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _with_staged_stub(message: str):
    STAGED_PATH.write_text(_stub_source(message), encoding="utf-8")
    sys.modules.pop("openrouter_engine", None)


def _cleanup_stub():
    STAGED_PATH.unlink(missing_ok=True)
    sys.modules.pop("openrouter_engine", None)


@pytest.fixture()
def engine_raises_plain_message():
    _with_staged_stub("internal engine failure")
    try:
        yield
    finally:
        _cleanup_stub()


@pytest.fixture()
def engine_raises_with_api_key():
    _with_staged_stub(f"upstream rejected key {FAKE_API_KEY}")
    try:
        yield
    finally:
        _cleanup_stub()


@pytest.fixture()
def engine_raises_with_newlines_and_auth_header():
    _with_staged_stub(f"request failed\n{FAKE_AUTH_HEADER}\nretry later")
    try:
        yield
    finally:
        _cleanup_stub()


def test_generic_exception_message_not_exposed(chat_server, engine_raises_plain_message):
    status, body = _post(chat_server, {"message": "1+1은?", "history": []})

    assert status == 502
    assert body == {"status": "error", "reason": "OpenRouter request failed"}
    assert "internal engine failure" not in json.dumps(body)


def test_api_key_in_exception_not_exposed(chat_server, engine_raises_with_api_key):
    status, body = _post(chat_server, {"message": "1+1은?", "history": []})

    assert status == 502
    response_text = json.dumps(body)
    assert FAKE_API_KEY not in response_text
    assert body == {"status": "error", "reason": "OpenRouter request failed"}


def test_multiline_exception_with_auth_header_not_exposed(
    chat_server, engine_raises_with_newlines_and_auth_header
):
    status, body = _post(chat_server, {"message": "1+1은?", "history": []})

    assert status == 502
    response_text = json.dumps(body)
    assert FAKE_AUTH_HEADER not in response_text
    assert FAKE_API_KEY not in response_text
    assert "\n" not in body["reason"]
    assert body == {"status": "error", "reason": "OpenRouter request failed"}


def test_stderr_log_does_not_contain_secret(capfd, chat_server, engine_raises_with_api_key):
    _post(chat_server, {"message": "1+1은?", "history": []})

    captured = capfd.readouterr()
    assert FAKE_API_KEY not in captured.err
    assert FAKE_API_KEY not in captured.out


def test_success_response_unaffected(chat_server):
    STAGED_PATH.write_text(
        "def call_engine_via_openrouter(prompt: str) -> str:\n"
        "    return 'stub-reply:' + prompt\n",
        encoding="utf-8",
    )
    sys.modules.pop("openrouter_engine", None)
    try:
        status, body = _post(chat_server, {"message": "1+1은?", "history": []})
        assert status == 200
        assert body == {"status": "ok", "reply": "stub-reply:User: 1+1은?\nAssistant:"}
    finally:
        _cleanup_stub()
