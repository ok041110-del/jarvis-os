"""로컬 HTTP test double — 실제 OmniRoute가 아니라, OmniRoute의
OpenAI-compatible 응답 형태를 흉내 낸 stdlib 서버다.

정상 응답·오류 코드·지연 응답(cancellation 테스트용)을 결정론적으로
재현하기 위해서만 쓴다 — "OmniRoute가 실제로 이렇게 동작한다"는
주장의 근거가 아니다(Caller의 request 구성·response 파싱·lifecycle
로직만 검증한다).
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - stdlib 시그니처
        pass  # 테스트 출력 소음 억제

    def do_POST(self):
        server = self.server
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length else b""
        with server.lock:
            server.received_requests.append(
                {
                    "path": self.path,
                    "headers": dict(self.headers.items()),
                    "body": json.loads(raw_body) if raw_body else None,
                }
            )
            delay = server.delay_seconds
            status = server.response_status
            body = server.response_body

        if delay:
            time.sleep(delay)

        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # cancellation 테스트에서 클라이언트가 먼저 끊는 경우


def success_body(content="Hello from fake OmniRoute"):
    return {
        "id": "router-fake0001",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "fake/model",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


class FakeOmniRouteServer:
    """`with FakeOmniRouteServer(status=200, body=...) as server:` 형태로
    사용한다. `server.base_url`을 caller의 `base_url`로 넘긴다."""

    def __init__(self, *, status=200, body=None, delay_seconds=0.0):
        self.response_status = status
        self.response_body = body if body is not None else success_body()
        self.delay_seconds = delay_seconds
        self.received_requests = []
        self.lock = threading.Lock()
        self._httpd = None
        self._thread = None

    def __enter__(self):
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self._httpd.lock = self.lock
        self._httpd.received_requests = self.received_requests
        self._httpd.response_status = self.response_status
        self._httpd.response_body = self.response_body
        self._httpd.delay_seconds = self.delay_seconds
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=5)

    @property
    def base_url(self):
        host, port = self._httpd.server_address
        return f"http://{host}:{port}"

    def set_response(self, *, status=None, body=None, delay_seconds=None):
        with self.lock:
            if status is not None:
                self._httpd.response_status = status
                self.response_status = status
            if body is not None:
                self._httpd.response_body = body
                self.response_body = body
            if delay_seconds is not None:
                self._httpd.delay_seconds = delay_seconds
                self.delay_seconds = delay_seconds
