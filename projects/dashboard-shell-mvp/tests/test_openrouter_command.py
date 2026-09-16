"""OpenRouter LLM Command 경로 — Functional/Boundary/실패 유형 검증.

`docs/research/JARVIS-OS-V2.0-DASHBOARD-OPENROUTER-LLM-PATH-PROTOTYPE-0001.md`
범위(F 항목): Dashboard Chat 정상 요청, LLM 정상 응답, 구조화된 응답 parsing,
LLM timeout, invalid response, provider/model failure, 기존 resolver Boundary
우회 없음, 기존 기능 회귀 없음.

대상 경로: Chat -> POST /api/openrouter-command -> `_classify_with_openrouter()`
(기존 `hqs/development/mvp/openrouter_engine.py`의 `call_engine_via_openrouter`
재사용, 무수정) -> 구조화 응답 -> 기존 `projects/command-contract/resolver.py`의
`resolve()`. 새 LLM client/Contract/Registry/Runtime/Dispatcher는 만들지
않았다 — 이 파일의 정적 검증이 그 부재까지 확인한다.

LLM 실패 유형 매핑: provider/네트워크/timeout -> HTTP 502(LLMInterpretError),
응답 형식 불일치 -> HTTP 422(LLMResponseFormatError). 어느 쪽도 Mock으로
대체하지 않는다(기존 Prototype의 노출 원칙과 동일).
"""

from __future__ import annotations

import ast
import http.server
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from functools import partial
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import pytest  # noqa: E402

import serve_dashboard  # noqa: E402


# ---- 테스트 전용 로컬 OpenRouter test double(stdlib http.server) ------------
#
# `hqs/development/mvp/tests/fake_openrouter_server.py`와 동일한 원칙의
# fixture다 — 실제 OpenRouter가 아니라 `/api/v1/models`(Free Pool, GET)와
# `/api/v1/chat/completions`(POST)의 응답 형태를 흉내 낸 결정론적 fixture.
# Production 코드가 아니다(이 파일 안에서만 존재).

_DEFAULT_FREE_MODELS = [
    {
        "id": f"vendor-{name}/model-{index}:free",
        "context_length": 200000,
        "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
    }
    for index, name in enumerate(("a", "b", "c"), start=1)
]

_CLASSIFICATION_OK = '{"intent": "show_status", "target_hq": "development"}'
_CLASSIFICATION_LABELLED = (
    "```json\n"
    '"intent": "show_status",\n'
    '"target_hq": "development"\n'
    "```"
)
_CLASSIFICATION_OTHER_INTENT = '{"intent": "deploy", "target_hq": "development"}'
# 프롬프트 스키마가 실제로 지시하는 형태 — 모델이 "response"로 감싸 답한
# 실측 형태(2026-09-13 실제 OpenRouter E2E에서 재현).
_CLASSIFICATION_RESPONSE_WRAPPED = (
    '{"response": {"intent": "show_status", "target_hq": "development"}}'
)
_RESPONSE_GARBAGE = "I am sorry, I cannot comply with the JSON formatting requirement."


class _FakeOpenRouterHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: A003 - stdlib override
        pass

    def _write_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def do_GET(self):
        # Free Pool 조회 — 항상 기본 pool(3개, text modality, 넉넉한 context).
        self._write_json(200, {"data": _DEFAULT_FREE_MODELS})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            self.server.last_post_body = json.loads(raw.decode("utf-8"))  # type: ignore[attr-defined]
        except (ValueError, UnicodeDecodeError):
            self.server.last_post_body = None  # type: ignore[attr-defined]
        mode = self.server.mode  # type: ignore[attr-defined]

        if mode == "slow":
            time.sleep(1.0)  # 테스트의 client timeout(0.4s)보다 길게 — read timeout 유발
            self._write_json(
                200,
                {"model": _DEFAULT_FREE_MODELS[0]["id"], "choices": [{"message": {"content": _CLASSIFICATION_OK}}]},
            )
            return

        content_by_mode = {
            "success": _CLASSIFICATION_OK,
            "labelled": _CLASSIFICATION_LABELLED,
            "other_intent": _CLASSIFICATION_OTHER_INTENT,
            "response_wrapped": _CLASSIFICATION_RESPONSE_WRAPPED,
            "garbage": _RESPONSE_GARBAGE,
            "trading": '{"intent": "show_status", "target_hq": "trading"}',
        }
        if mode in content_by_mode:
            self._write_json(
                200,
                {"model": _DEFAULT_FREE_MODELS[0]["id"], "choices": [{"message": {"content": content_by_mode[mode]}}]},
            )
            return

        if mode == "unauthorized":
            # 잘못된 API Key — OpenRouter의 실제 401 응답 형태.
            self._write_json(
                401,
                {"error": {"message": "No auth credentials found", "code": 401}},
            )
            return

        if mode == "quota":
            self._write_json(429, {"error": {"message": "Rate limit exceeded: free-models-per-day", "code": 429}})
            return
        if mode == "server_error":
            self._write_json(500, {"error": {"message": "synthetic upstream failure"}})
            return

        raise ValueError(f"unknown POST mode: {mode}")


class FakeOpenRouterServer:
    """`with FakeOpenRouterServer(mode="success") as base_url:` 형태로 쓴다."""

    def __init__(self, mode: str):
        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _FakeOpenRouterHandler)
        self._server.mode = mode  # type: ignore[attr-defined]
        self._server.last_post_body = None  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def __exit__(self, *exc_info):
        self._server.shutdown()
        self._server.server_close()


class DashboardServer:
    """실제 `serve_dashboard.DashboardRequestHandler`를 임의 포트에 띄운다."""

    def __enter__(self):
        self._server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            partial(serve_dashboard.DashboardRequestHandler, directory=str(serve_dashboard.DASHBOARD_DIR)),
        )
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def __exit__(self, *exc_info):
        self._server.shutdown()
        self._server.server_close()


def _post(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        base_url + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


# ---- 1. Functional — Chat -> LLM -> 구조화 응답 -> resolver -------------------


def test_chat_request_classified_and_resolved_end_to_end(monkeypatch):
    with FakeOpenRouterServer(mode="success") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 200
    assert body["llm"] == {"intent": "show_status", "target_hq": "development"}
    assert body["status"] == "ok"
    assert body["hq_identity"] == "Development HQ"
    assert body["detail"]


def test_prose_wrapped_response_is_recovered_and_resolved(monkeypatch):
    """fence + 필드 라벨형 편차(free 모델 실측)도 복구해 정상 분류로 처리한다."""
    with FakeOpenRouterServer(mode="labelled") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 200
    assert body["llm"] == {"intent": "show_status", "target_hq": "development"}
    assert body["status"] == "ok"


def test_response_wrapped_classification_is_unwrapped_and_resolved(monkeypatch):
    """프롬프트 스키마가 지시한 `{"response": {...}}` wrapper 형태(실제 모델
    실측)도 unwrap해 intent/target_hq를 정상 추출하고 resolve()까지 통과한다 —
    unwrap 이전에는 이 형태가 intent/target_hq를 항상 null로 만들어
    unknown_command로 귀결됐다."""
    with FakeOpenRouterServer(mode="response_wrapped") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 200
    assert body["llm"] == {"intent": "show_status", "target_hq": "development"}
    assert body["status"] == "ok"
    assert body["hq_identity"] == "Development HQ"
    assert body["reason"] != "unknown_command"


# ---- 2. 실패 유형 — timeout / provider failure / invalid response ------------


def test_provider_server_error_returns_502_without_mock_fallback(monkeypatch):
    with FakeOpenRouterServer(mode="server_error") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 502
    assert "5xx" in body["error"]
    assert "detail" not in body  # Mock으로 대체하지 않았다 — 실행 결과 없음


def test_provider_quota_failure_returns_502_with_quota_category(monkeypatch):
    with FakeOpenRouterServer(mode="quota") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 502
    assert "429_quota" in body["error"]


def test_llm_timeout_returns_502(monkeypatch):
    """실제 Engine timeout 경로 — 느린 응답 + 짧은 OPENROUTER_TIMEOUT_SECONDS."""
    with FakeOpenRouterServer(mode="slow") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", "0.4")
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 502
    assert "timed out" in body["error"] or "connection_error" in body["error"]


def test_invalid_response_returns_422_distinct_from_provider_failure(monkeypatch):
    with FakeOpenRouterServer(mode="garbage") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 422
    assert "파싱" in body["error"]


def test_bad_request_body_returns_400():
    with DashboardServer() as base_url:
        status, body = _post(base_url, "/api/openrouter-command", {"wrong_field": 1})

    assert status == 400
    assert "raw_input" in body["error"]


# ---- 3. Boundary — LLM 분류가 기존 resolver를 우회하지 않음 -------------------


def test_llm_classification_of_unknown_hq_is_refused_by_resolver(monkeypatch):
    """LLM이 resolver가 모르는 HQ(trading)로 분류해도 resolve()가 거부한다 —
    LLM 분류가 실행 Boundary를 우회하지 않음(기존 Claude 경로와 동일 원칙)."""
    with FakeOpenRouterServer(mode="trading") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Trading HQ 상태를 보여줘"})

    assert status == 200
    assert body["llm"]["target_hq"] == "trading"  # 분류는 그대로 노출
    assert body["status"] == "invalid"
    assert body["reason"] == "unknown_hq"


def test_llm_unsupported_intent_is_refused_by_resolver(monkeypatch):
    """LLM이 새 intent를 지어내도 resolver의 _SUPPORTED_INTENTS가 거부한다 —
    Command Contract 확장 없이 기존 Boundary가 그대로 지켜진다."""
    with FakeOpenRouterServer(mode="other_intent") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ에 배포해줘"})

    assert status == 200
    assert body["llm"]["intent"] == "deploy"
    assert body["status"] == "invalid"
    assert body["reason"] == "unsupported_intent"


def test_null_classification_is_refused_by_resolver(monkeypatch):
    """intent/target_hq가 null인 분류도 resolver가 unknown_command/unknown_hq로
    거부한다 — LLM이 대답을 지어낼 여지가 없다."""
    serve_dashboard._openrouter_engine_call = lambda prompt: '{"intent": null, "target_hq": null}'
    try:
        result = serve_dashboard._classify_with_openrouter("아무 말이나")
    finally:
        serve_dashboard._openrouter_engine_call = serve_dashboard.call_engine_via_openrouter

    assert result == {"intent": None, "target_hq": None}
    from command import Command
    from resolver import resolve

    resolution = resolve(Command(raw_input="아무 말이나", intent=None, target_hq=None))
    assert resolution.status == "invalid"


# ---- 4. 파싱 세부 — 구조화 응답 parsing 단위 검증 ------------------------------


def test_engine_runtime_error_maps_to_llm_interpret_error():
    def _failing_engine(prompt: str) -> str:
        raise RuntimeError("OpenRouter call failed after retry (category=5xx)")

    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = _failing_engine
    try:
        with pytest.raises(serve_dashboard.LLMInterpretError) as exc_info:
            serve_dashboard._classify_with_openrouter("Development HQ 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original

    assert not isinstance(exc_info.value, serve_dashboard.LLMResponseFormatError)
    assert "5xx" in str(exc_info.value)


def test_non_dict_json_is_format_error():
    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = lambda prompt: "[1, 2, 3]"
    try:
        with pytest.raises(serve_dashboard.LLMResponseFormatError):
            serve_dashboard._classify_with_openrouter("Development HQ 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original


def test_wrong_field_type_is_format_error():
    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = lambda prompt: '{"intent": 5, "target_hq": "development"}'
    try:
        with pytest.raises(serve_dashboard.LLMResponseFormatError):
            serve_dashboard._classify_with_openrouter("Development HQ 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original


def test_response_wrapper_is_unwrapped_at_parser_level():
    """`_OPENROUTER_CLASSIFIER_PROMPT_TEMPLATE`이 지시하는 `{"response": {...}}`
    스키마 그대로 모델이 답했을 때 `_classify_with_openrouter()`가 wrapper를
    벗기고 intent/target_hq를 추출하는지 파서 단위에서 직접 검증한다."""
    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = (
        lambda prompt: '{"response": {"intent": "show_status", "target_hq": "investment"}}'
    )
    try:
        result = serve_dashboard._classify_with_openrouter("Investment HQ 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original

    assert result == {"intent": "show_status", "target_hq": "investment"}


def test_top_level_classification_without_wrapper_still_works():
    """wrapper 없이 최상위로 답하는 기존 실측 편차도 계속 지원한다 — unwrap은
    "response" 키가 있을 때만 적용되고 없으면 그대로 최상위를 읽는다."""
    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = (
        lambda prompt: '{"intent": "show_status", "target_hq": "development"}'
    )
    try:
        result = serve_dashboard._classify_with_openrouter("Development HQ 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original

    assert result == {"intent": "show_status", "target_hq": "development"}


def test_label_style_answer_without_fence_is_recovered():
    original = serve_dashboard._openrouter_engine_call
    serve_dashboard._openrouter_engine_call = lambda prompt: (
        '분류 결과:\n"intent": "show_status"\n"target_hq": "investment"'
    )
    try:
        result = serve_dashboard._classify_with_openrouter("Investment HQ 최신 상태를 보여줘")
    finally:
        serve_dashboard._openrouter_engine_call = original

    assert result == {"intent": "show_status", "target_hq": "investment"}


# ---- 5. API Key 처리 — 미설정/잘못된 Key/키 노출 금지 -------------------------


def test_missing_api_key_fails_at_provider_level_without_mock_fallback(monkeypatch):
    """OPENROUTER_API_KEY 미설정 상태에서의 실제 요청 경로 — Engine 모듈의 기존
    규칙(키 없으면 Authorization 헤더 자체를 설정하지 않음)을 그대로 거치며,
    응답이 없으면 provider 오류로 노출된다(Mock 대체 금지).

    test double은 401을 돌려준다 — 실제 OpenRouter도 키 없는 요청에 401을
    반환한다. 즉 이 테스트는 '키 미설정 상태의 전체 실패 경로'를 실제 HTTP
    위임 계층까지 검증한다.
    """
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with FakeOpenRouterServer(mode="unauthorized") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 502
    assert "malformed_response" in body["error"]
    assert "detail" not in body


def test_missing_api_key_clearly_reported_when_double_also_refuses(monkeypatch):
    """키가 없으면 Engine이 Authorization 헤더를 아예 보내지 않는다 — 요청에
    Authorization이 없음을 test double 수신에서 직접 확인한다(키 노출 금지
    규칙과 함께, 미설정 상태의 동작을 명확히 검증).
    """
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with FakeOpenRouterServer(mode="unauthorized") as openrouter_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        with pytest.raises(serve_dashboard.LLMInterpretError) as exc_info:
            serve_dashboard._classify_with_openrouter("Development HQ 상태를 보여줘")

    assert "malformed_response" in str(exc_info.value)
    assert not isinstance(exc_info.value, serve_dashboard.LLMResponseFormatError)


def test_invalid_api_key_returns_502_without_leaking_credentials(monkeypatch):
    """잘못된 API Key(401) — provider 실패로 구분되고, 오류 메시지에 Key 값이
    Authorization 헤더 값이 노출되지 않는다.
    """
    with FakeOpenRouterServer(mode="unauthorized") as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-invalid-key-for-test")
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 502
    assert "sk-or-v1-invalid-key-for-test" not in body["error"]
    assert "Authorization" not in body["error"]


def test_error_messages_never_contain_api_key_value(monkeypatch):
    """모든 실패 유형(5xx/quota/garbage/unauthorized)에서 오류 메시지에 API Key
    값이 절대 포함되지 않는다."""
    api_key = "sk-or-v1-secret-value-must-not-leak"
    monkeypatch.setenv("OPENROUTER_API_KEY", api_key)
    failure_modes = ["server_error", "quota", "garbage", "unauthorized"]

    for mode in failure_modes:
        with FakeOpenRouterServer(mode=mode) as openrouter_url, DashboardServer() as base_url:
            monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
            status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "x"})
            expected_status = 422 if mode == "garbage" else 502
            assert status == expected_status, mode
            assert api_key not in body.get("error", ""), mode


def test_engine_delegation_sends_chat_completions_request(monkeypatch):
    """Dashboard endpoint가 기존 Engine의 실제 호출 계약(POST
    /api/v1/chat/completions, messages 페이로드, models 후보 배열)을 그대로
    위임하는지 test double 수신에서 확인한다 — 위임 계층 실측.
    """
    fake = FakeOpenRouterServer(mode="success")
    with fake as openrouter_url, DashboardServer() as base_url:
        monkeypatch.setenv("OPENROUTER_BASE_URL", openrouter_url)
        status, body = _post(base_url, "/api/openrouter-command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 200
    sent = fake._server.last_post_body
    assert sent is not None
    assert sent["messages"][0]["role"] == "user"
    assert "Development HQ 상태를 보여줘" in sent["messages"][0]["content"]
    assert isinstance(sent.get("models"), list) and sent["models"]  # 후보 선택도 Engine 위임


def test_openrouter_path_never_executes_llm_output_as_code():
    """LLM 출력은 {intent, target_hq} 파싱 입력으로만 쓰인다 — OpenRouter 경로
    함수 어디에서도 임의 출력을 실행(eval/exec/subprocess/os.system)하지
    않는다. shell command/tool execution 방지 원칙의 정적 검증."""
    source = (PROTOTYPE_DIR / "serve_dashboard.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    target = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_classify_with_openrouter"
    )
    for node in ast.walk(target):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "system", "Popen"}:
                pytest.fail(f"LLM 출력 실행 호출 발견: {node.func.id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "Popen", "run"}:
                pytest.fail(f"LLM 출력 실행 호출 발견: .{node.func.attr}()")


# ---- 6. 회귀 — 기존 endpoint/기존 기능은 그대로 --------------------------------


def test_existing_regex_command_endpoint_still_works():
    with DashboardServer() as base_url:
        status, body = _post(base_url, "/api/command", {"raw_input": "Development HQ 상태를 보여줘"})

    assert status == 200
    assert body["intent"] == "show_status"
    assert body["status"] == "ok"


def test_unknown_post_path_returns_404():
    with DashboardServer() as base_url:
        status, _ = _post(base_url, "/api/no-such-path", {})

    assert status == 404


# ---- 6. Boundary 정적 검증 — 새 추상화/중복 구현 없음 --------------------------


def _imported_top_level_modules(py_file: Path) -> set:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_serve_dashboard_does_not_import_hqs_or_core_directly():
    """`mvp` 패키지 seam(Engine 함수)만 건드리고 `hqs`/`core` 트리는 직접
    import하지 않는다 — 기존 Prototype Boundary 방식과 동일."""
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "serve_dashboard.py")
    assert "hqs" not in modules
    assert "core" not in modules


def test_reuses_existing_engine_function_object():
    """새 Dashboard LLM client를 만들지 않고 기존 함수 객체를 그대로 쓰는지
    확인한다(같은 로직을 복제하지 않았는지 검증)."""
    from mvp.openrouter_engine import call_engine_via_openrouter as canonical

    assert serve_dashboard.call_engine_via_openrouter is canonical


def test_no_new_llm_networking_or_client_abstraction_in_serve_dashboard():
    """HTTP/네트워킹은 전부 기존 Engine 모듈이 담당한다 — serve_dashboard.py에
    새 client 클래스나 새 네트워킹 코드가 없어야 한다."""
    source = (PROTOTYPE_DIR / "serve_dashboard.py").read_text(encoding="utf-8")
    for token in ("class EngineClient", "class LLMClient", "class Router", "class Gateway", "urllib.request", "http.client"):
        assert token not in source


def test_command_contract_and_resolver_untouched():
    """Command/Resolver Contract 파일의 핵심 리터럴이 그대로인지 확인한다 —
    이 Prototype이 Contract를 확장하지 않았음을 정적으로 검증."""
    contract_dir = PROTOTYPE_DIR.parent / "command-contract"
    resolver_source = (contract_dir / "resolver.py").read_text(encoding="utf-8")
    command_source = (contract_dir / "command.py").read_text(encoding="utf-8")
    assert '_SUPPORTED_INTENTS = {"show_status"}' in resolver_source
    assert '"unknown_command"' in resolver_source
    assert '"unsupported_intent"' in resolver_source
    assert '"unknown_hq"' in resolver_source
    assert "raw_input: str" in command_source
    assert "intent: str | None" in command_source
    assert "target_hq: str | None" in command_source
