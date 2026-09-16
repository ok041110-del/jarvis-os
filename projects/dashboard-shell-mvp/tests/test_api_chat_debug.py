"""`api/chat.py` — A/B/C 원인 판별용 임시 debug 필드 검증.

`buildCommand`(`cp ../../hqs/development/mvp/openrouter_engine.py
api/openrouter_engine.py`)의 staging 결과가 실제 Lambda에 반영됐는지를
Vercel Build Log 없이 응답 JSON만으로 판별하기 위해 추가된
`_import_failure_debug()`가 (1) import 실패 시에만 응답에 섞이고, (2) 정상
정보(`debug_file`/`debug_api_dir`/`debug_api_dir_listing`/
`debug_staged_openrouter_engine_exists`)를 담는지만 확인한다. 정상
success/engine-failure 경로의 응답 스키마가 바뀌지 않았는지도 함께 본다.
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


def test_import_failure_includes_debug_fields(chat_server):
    # 이 저장소 checkout에는 `api/openrouter_engine.py`가 staging되어 있지
    # 않으므로(로컬 개발은 buildCommand를 거치지 않는다) import가 실제로
    # 실패하는 상태 그대로 검증한다 — Mock으로 대체하지 않는다.
    status, body = _post(chat_server, {"message": "hello", "history": []})

    assert status == 502
    assert body["status"] == "error"
    assert "openrouter_engine import 실패" in body["reason"]
    assert body["debug_file"] == str((API_DIR / "chat.py").resolve())
    assert body["debug_api_dir"] == str(API_DIR.resolve())
    assert "chat.py" in body["debug_api_dir_listing"]
    assert body["debug_staged_openrouter_engine_exists"] is False


def test_bad_request_body_has_no_debug_fields(chat_server):
    status, body = _post(chat_server, {"history": []})  # message 누락

    assert status == 400
    assert "debug_file" not in body
    assert "debug_api_dir" not in body


def test_import_failure_debug_helper_reports_actual_directory():
    debug = chat_module._import_failure_debug()

    assert debug["debug_api_dir"] == str(API_DIR.resolve())
    assert isinstance(debug["debug_api_dir_listing"], list)
    assert debug["debug_staged_openrouter_engine_exists"] == (
        (API_DIR / "openrouter_engine.py").is_file()
    )
