"""`api/chat.py` — staged `openrouter_engine.py` sibling import 경로 보정 검증.

Runtime Evidence(Preview Deployment 실측)로 원인이 확정됐다: `buildCommand`가
`api/openrouter_engine.py`를 실제로 staging하는 데는 성공하지만(파일이
물리적으로 존재), Vercel Python Function이 `chat.py`를 로드하는 방식이 자신의
디렉터리를 `sys.path`에 자동으로 넣어주지 않아 평범한
`from openrouter_engine import ...`가 `ModuleNotFoundError`로 실패했다.
수정은 import 직전 `chat.py` 자신의 디렉터리를 명시적으로 `sys.path`에
추가하는 것뿐이다 — `openrouter_engine.py`/Command Contract는 무수정.

여기서는 실제 네트워크(OpenRouter)를 타지 않도록, staged 파일 자리에 최소
stub(`call_engine_via_openrouter`만 정의)을 임시로 놓고 import 경로 보정
자체만 검증한다.
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
STUB_SOURCE = (
    'def call_engine_via_openrouter(prompt: str) -> str:\n'
    '    return "stub-reply:" + prompt\n'
)


@pytest.fixture()
def staged_engine_stub():
    """buildCommand가 만드는 `api/openrouter_engine.py`를 최소 stub으로 재현한다."""
    STAGED_PATH.write_text(STUB_SOURCE, encoding="utf-8")
    sys.modules.pop("openrouter_engine", None)
    try:
        yield
    finally:
        STAGED_PATH.unlink(missing_ok=True)
        sys.modules.pop("openrouter_engine", None)


@pytest.fixture()
def no_staged_engine():
    """로컬 checkout처럼 staged 파일이 없는 상태(회귀 확인용)."""
    assert not STAGED_PATH.exists(), "테스트 시작 전 staged 파일이 이미 있으면 안 됨"
    sys.modules.pop("openrouter_engine", None)
    yield
    sys.modules.pop("openrouter_engine", None)


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


def test_sibling_import_succeeds_when_staged_file_present(chat_server, staged_engine_stub):
    status, body = _post(chat_server, {"message": "1+1은?", "history": []})

    assert status == 200
    assert body == {"status": "ok", "reply": "stub-reply:User: 1+1은?\nAssistant:"}


def test_import_failure_without_staged_file_has_no_debug_fields(chat_server, no_staged_engine):
    # 로컬 checkout(=buildCommand 미실행)에서는 여전히 실패해야 하고, 이전
    # 진단용 debug_* 필드는 이제 응답에 없어야 한다(정상 스키마로 복귀).
    status, body = _post(chat_server, {"message": "hello", "history": []})

    assert status == 502
    assert body == {
        "status": "error",
        "reason": "openrouter_engine import 실패: No module named 'openrouter_engine'",
    }


def test_bad_request_body_unaffected(chat_server, no_staged_engine):
    status, body = _post(chat_server, {"history": []})  # message 누락

    assert status == 400
    assert body == {"status": "error", "reason": "message(비어있지 않은 string) 필드가 필요함"}
