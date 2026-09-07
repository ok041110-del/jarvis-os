"""테스트 전용 로컬 OmniRoute test double(stdlib `http.server`).

실제 OmniRoute가 아니라 OpenAI-compatible 응답 형태를 흉내 낸
결정론적 fixture다 — Experimental Thin Caller 프로토타입(`projects/`
아래)의 동명 fixture와 같은 목적이지만, production 테스트가
Experimental 경로를 참조하지 않도록 이 위치에 독립적으로 둔다."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: A003 - stdlib override
        pass

    def do_POST(self):
        mode = self.server.mode  # type: ignore[attr-defined]
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length) if length else b""

        if mode == "slow":
            import time
            time.sleep(self.server.slow_seconds)  # type: ignore[attr-defined]

        if mode == "success":
            payload = json.dumps({
                "choices": [{"message": {"content": "FAKE_OMNIROUTE_OK"}}],
            }).encode()
            self.send_response(200)
        elif mode == "error500":
            payload = json.dumps({"error": {"message": "synthetic upstream failure"}}).encode()
            self.send_response(500)
        elif mode == "error429":
            payload = json.dumps({"error": {"message": "Daily budget exceeded"}}).encode()
            self.send_response(429)
        elif mode == "malformed":
            payload = b"not json"
            self.send_response(200)
        else:
            raise ValueError(f"unknown mode: {mode}")

        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except Exception:
            pass


class FakeOmniRouteServer:
    """`with FakeOmniRouteServer(mode="success") as base_url:` 형태로 사용."""

    def __init__(self, mode="success", slow_seconds=0):
        self._server = HTTPServer(("127.0.0.1", 0), _Handler)
        self._server.mode = mode
        self._server.slow_seconds = slow_seconds
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        port = self._server.server_address[1]
        return f"http://127.0.0.1:{port}"

    def __exit__(self, *exc_info):
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)
