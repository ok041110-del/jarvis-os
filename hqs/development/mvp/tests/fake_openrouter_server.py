"""테스트 전용 로컬 OpenRouter test double(stdlib `http.server`).

실제 OpenRouter가 아니라 `/api/v1/models`(Free Pool 조회, GET)와
`/api/v1/chat/completions`(POST)의 실제 응답 형태를 흉내 낸 결정론적
fixture다. `fake_omniroute_server.py`는 POST만 지원해 Free Pool GET
경로를 검증할 수 없으므로, Production 테스트 전용으로 독립적으로
둔다(`fake_omniroute_server.py` 자신의 docstring과 동일한 원칙 —
Experimental 경로를 참조하지 않는다)."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 3개 초과 후보로 Candidate Selection(tie-break)을 실제로 검증할 수
# 있도록 5개를 둔다 — 순서가 곧 tie-break 근거(Pool 응답 순서 보존).
_DEFAULT_FREE_MODELS = [
    {"id": "vendor-a/model-1:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    {"id": "vendor-b/model-2:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    {"id": "vendor-c/model-3:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    {"id": "vendor-d/model-4:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    {"id": "vendor-e/model-5:free", "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
    # 이 두 모델도 모델 이름만으로 Deterministic Filter의 실측 exclusion
    # 목록에 걸려야 KEPT에서 빠진다(테스트가 실제로 이 필터를 검증하려면
    # 이름이 그 상수와 일치해야 하므로, 별도 mode에서만 pool에 섞는다).
]

_NONFUNCTIONAL_MODEL_IDS = ["thinkingmachines/inkling:free", "thinkingmachines/inkling-small:free"]


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: A003 - stdlib override
        pass

    def _write_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _write_raw(self, status: int, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def do_GET(self):
        mode = self.server.mode  # type: ignore[attr-defined] # GET 전용(Free Pool 조회)
        if self.path != "/api/v1/models":
            self._write_json(404, {"error": "not found"})
            return

        if mode == "models_fetch_error":
            self._write_raw(500, b"upstream failure")
            return
        if mode == "empty_pool":
            self._write_json(200, {"data": []})
            return
        if mode == "with_nonfunctional":
            data = _DEFAULT_FREE_MODELS[:2] + [
                {"id": mid, "context_length": 200000, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}}
                for mid in _NONFUNCTIONAL_MODEL_IDS
            ]
            self._write_json(200, {"data": data})
            return
        if mode == "small_context":
            data = [{"id": "vendor-a/model-1:free", "context_length": 1, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}}]
            self._write_json(200, {"data": data})
            return

        self._write_json(200, {"data": _DEFAULT_FREE_MODELS})

    def do_POST(self):
        mode = getattr(self.server, "post_mode", self.server.mode)  # type: ignore[attr-defined] # POST 전용(Chat Completions)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            request_body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            request_body = {}

        if mode == "success":
            self._write_json(
                200,
                {
                    "model": (request_body.get("models") or ["unknown"])[0],
                    "choices": [{"message": {"content": "FAKE_OPENROUTER_OK"}}],
                },
            )
            return

        if mode == "quota":
            self._write_json(429, {"error": {"message": "Rate limit exceeded: free-models-per-day", "code": 429}})
            return

        if mode == "server_error":
            self._write_json(500, {"error": {"message": "synthetic upstream failure"}})
            return

        if mode == "malformed":
            self._write_raw(200, b"not json")
            return

        if mode == "empty_content":
            self._write_json(200, {"model": (request_body.get("models") or ["unknown"])[0], "choices": [{"message": {"content": ""}}]})
            return

        if mode == "recover_on_retry":
            self.server.call_count += 1  # type: ignore[attr-defined]
            if self.server.call_count == 1:  # type: ignore[attr-defined]
                self._write_json(500, {"error": {"message": "transient upstream failure"}})
            else:
                self._write_json(
                    200,
                    {
                        "model": (request_body.get("models") or ["unknown"])[0],
                        "choices": [{"message": {"content": "FAKE_OPENROUTER_RECOVERED"}}],
                    },
                )
            return

        raise ValueError(f"unknown POST mode: {mode}")


class FakeOpenRouterServer:
    """`with FakeOpenRouterServer(mode="success") as base_url:` 형태로
    사용한다. GET(`/api/v1/models`)과 POST(`/api/v1/chat/completions`)
    모드를 독립적으로 지정할 수 있다(`models_mode`가 없으면 POST
    `mode`와 동일하게 GET도 기본 Pool을 반환한다)."""

    def __init__(self, mode="success", models_mode=None):
        self._server = HTTPServer(("127.0.0.1", 0), _Handler)
        self._server.mode = models_mode if models_mode else mode
        self._server.call_count = 0
        self._post_mode = mode
        self._models_mode = models_mode
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        port = self._server.server_address[1]
        # GET/POST가 서로 다른 mode를 써야 하는 테스트를 위해, 핸들러가
        # do_GET에서는 `_models_mode`(없으면 기본 Pool), do_POST에서는
        # `_post_mode`를 보도록 서버 객체에 둘 다 실어 둔다.
        self._server.mode = self._models_mode or "default_pool"
        self._server.post_mode = self._post_mode
        return f"http://127.0.0.1:{port}"

    def __exit__(self, *exc_info):
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)
