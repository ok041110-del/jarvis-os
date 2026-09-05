"""Dashboard Shell MVP — 로컬 실행 스크립트.

Dashboard는 `js/data.js`가 `fetch("data/development-snapshot.json")`을
호출하므로 `file://`로 직접 열면 CORS로 막힌다(README 참조) — 반드시
HTTP 서버가 필요하다. 이 스크립트는 그 서버를 표준 라이브러리
(`http.server`)만으로 띄우고, 접속 URL을 곧바로 출력한다.

이 파일은 실행 편의용이며 Dashboard 코드(`index.html`/`css`/`js`/
`generate_development_snapshot.py`)를 전혀 건드리지 않는다.
"""

from __future__ import annotations

import http.server
import socket
import sys
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
MAX_PORT_ATTEMPTS = 20


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

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *args, directory=str(DASHBOARD_DIR), **kwargs
    )
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard 서버를 종료합니다.")


if __name__ == "__main__":
    main()
