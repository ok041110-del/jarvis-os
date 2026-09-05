"""Dashboard Shell MVP — 로컬 실행 스크립트.

Dashboard는 `js/data.js`가 `fetch("data/development-snapshot.json")`을
호출하므로 `file://`로 직접 열면 CORS로 막힌다(README 참조) — 반드시
HTTP 서버가 필요하다. 이 스크립트는 그 서버를 표준 라이브러리
(`http.server`)만으로 띄우고, 접속 URL을 곧바로 출력한다.

이 파일은 실행 편의용이며 Dashboard 코드(`index.html`/`css`/`js`/
`generate_*_snapshot.py`)를 전혀 건드리지 않는다.

`POST /api/command`만 예외다 — Dashboard Chat이 raw_input을 보내면
`projects/command-contract/resolver.py`의 `parse_command()`/
`resolve()`를 그대로 호출한다(같은 로직을 여기 복제하지 않는다).
이 서버는 `hqs/`·`core/`를 직접 호출하지 않는다 — resolver 자체가
이미 그 Boundary를 지킨다(Command Resolution 책임만 이 서버가
중계한다).
"""

from __future__ import annotations

import http.server
import json
import socket
import sys
from functools import partial
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
COMMAND_CONTRACT_DIR = DASHBOARD_DIR.parent / "command-contract"
sys.path.insert(0, str(COMMAND_CONTRACT_DIR))

from resolver import parse_command, resolve  # noqa: E402

DEFAULT_PORT = 8765
MAX_PORT_ATTEMPTS = 20


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """정적 파일 서빙(기존과 동일) + `/api/command` 한 경로만 추가."""

    def do_POST(self):
        if self.path != "/api/command":
            self._send_json(http.HTTPStatus.NOT_FOUND, {"error": "알 수 없는 경로: " + self.path})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            raw_input = body["raw_input"]
            if not isinstance(raw_input, str):
                raise TypeError("raw_input은 문자열이어야 함")
        except (ValueError, KeyError, TypeError) as exc:
            self._send_json(
                http.HTTPStatus.BAD_REQUEST,
                {"error": "잘못된 요청 본문 — raw_input(string) 필드가 필요함: " + str(exc)},
            )
            return

        command = parse_command(raw_input)
        result = resolve(command)
        self._send_json(
            http.HTTPStatus.OK,
            {
                "raw_input": command.raw_input,
                "intent": command.intent,
                "target_hq": command.target_hq,
                "status": result.status,
                "reason": result.reason,
                "hq_identity": result.hq_identity,
                "detail": result.detail,
            },
        )

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _find_free_port(start_port: int) -> int:
    for port in range(start_port, start_port + MAX_PORT_ATTEMPTS):
        if _port_is_free(port):
            return port
    raise RuntimeError(
        f"{start_port}~{start_port + MAX_PORT_ATTEMPTS - 1} 범위에서 사용 가능한 포트를 찾지 못함"
    )


def main() -> None:
    requested_port = DEFAULT_PORT
    if len(sys.argv) > 1:
        requested_port = int(sys.argv[1])

    port = requested_port
    if not _port_is_free(port):
        port = _find_free_port(requested_port)
        print(f"포트 {requested_port}번이 이미 사용 중 — {port}번으로 대신 실행")

    url = f"http://localhost:{port}/index.html"

    # 출력이 파일/파이프로 리다이렉트되면 기본 버퍼링 때문에 이 배너가
    # serve_forever() 동안 화면에 안 보일 수 있어 매 print에 flush를 강제한다.
    print("=" * 60, flush=True)
    print(f"Dashboard URL: {url}", flush=True)
    print("=" * 60, flush=True)
    print("브라우저에서 위 주소를 열면 Dashboard Shell MVP가 표시됩니다.", flush=True)
    print("종료하려면 Ctrl+C를 누르세요.", flush=True)

    handler = partial(DashboardRequestHandler, directory=str(DASHBOARD_DIR))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard 서버를 종료합니다.")


if __name__ == "__main__":
    main()
