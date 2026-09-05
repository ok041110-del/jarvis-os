"""Dashboard Shell MVP — 로컬 실행 스크립트.

Dashboard는 `js/data.js`가 `fetch("data/development-snapshot.json")`을
호출하므로 `file://`로 직접 열면 CORS로 막힌다(README 참조) — 반드시
HTTP 서버가 필요하다. 이 스크립트는 그 서버를 표준 라이브러리
(`http.server`)만으로 띄우고, 접속 URL을 곧바로 출력한다.

이 파일은 실행 편의용이며 Dashboard 코드(`index.html`/`css`/`js`/
`generate_*_snapshot.py`)를 전혀 건드리지 않는다.

`POST /api/command`/`POST /api/llm-command` 두 경로만 예외다.
`/api/command`는 Dashboard Chat의 raw_input을 `projects/command-
contract/resolver.py`의 `parse_command()`/`resolve()`에 그대로
전달한다(같은 로직을 여기 복제하지 않는다). `/api/llm-command`는
그 앞단에 실제 Claude 호출(이미 로그인된 `claude` CLI, `--tools ""`로
Tool을 전부 비활성화한 순수 분류 1회 호출)을 끼워 넣어 raw_input을
intent/target_hq로 해석한 뒤 같은 `resolve()`를 그대로 호출한다 —
Claude는 분류만 하고, 실제 HQ 상태 조회는 여전히 기존 resolve()/
Snapshot Builder가 전담한다. 이 서버는 `hqs/`·`core/`를 직접
호출하지 않는다 — resolver 자체가 이미 그 Boundary를 지킨다.

Claude API Key/OAuth Credential은 이 파일 어디에도 등장하지 않는다 —
`claude` CLI가 이미 이 머신에 로그인된 기존 인증(Claude Code 자신의
Credential Mechanism)을 그대로 쓸 뿐이며, 이 코드는 그 값을 읽거나
로그에 남기지 않는다.
"""

from __future__ import annotations

import http.server
import json
import socket
import subprocess
import sys
from functools import partial
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
COMMAND_CONTRACT_DIR = DASHBOARD_DIR.parent / "command-contract"
sys.path.insert(0, str(COMMAND_CONTRACT_DIR))

from command import Command  # noqa: E402
from resolver import parse_command, resolve  # noqa: E402

DEFAULT_PORT = 8765
MAX_PORT_ATTEMPTS = 20

# Claude를 raw_input -> {intent, target_hq} 분류기로만 쓴다. 이 스키마는
# command.py의 Command 필드와 정확히 같다 — 새 Contract를 만들지 않는다.
_LLM_CLASSIFIER_PROMPT_TEMPLATE = (
    '사용자 메시지: "{raw_input}"\n\n'
    "당신은 자연어 메시지를 아래 스키마의 JSON으로만 분류하는 분류기다. "
    "절대 다른 텍스트나 설명을 출력하지 마라.\n\n"
    '스키마: {{"intent": "show_status" | null, '
    '"target_hq": "development" | "investment" | "trading" | null}}\n\n'
    "규칙:\n"
    '- 상태 조회 요청이면 intent="show_status"\n'
    "- 어떤 HQ를 가리키는지 알 수 없으면 target_hq=null\n"
    "- JSON 객체 하나만 출력한다."
)
_LLM_TIMEOUT_SEC = 45


class LLMInterpretError(Exception):
    """Claude 호출/파싱 실패 — 호출부가 Mock으로 대체하지 않고 그대로 드러내야 함."""


def _interpret_with_claude(raw_input: str) -> tuple[str | None, str | None]:
    """raw_input을 Command 스키마(intent/target_hq)로 분류한다.

    `--tools ""`로 Bash/Read 등 모든 Tool(Agent 포함)을 비활성화해
    Claude가 파일을 직접 읽거나 행동을 취하지 못하게 막는다 — 순수
    텍스트 분류 1회 호출이다. `--restricted`로 이 저장소의 CLAUDE.md/
    project 설정도 불러오지 않는다(분류와 무관한 컨텍스트 배제).
    """

    prompt = _LLM_CLASSIFIER_PROMPT_TEMPLATE.format(raw_input=raw_input)
    try:
        proc = subprocess.run(
            [
                "claude", "-p", prompt,
                "--tools", "",
                "--restricted",
                "--output-format", "json",
                "--permission-mode", "dontAsk",
            ],
            capture_output=True,
            text=True,
            timeout=_LLM_TIMEOUT_SEC,
        )
    except FileNotFoundError as exc:
        raise LLMInterpretError("claude CLI를 찾을 수 없음: " + str(exc)) from exc
    except subprocess.TimeoutExpired as exc:
        raise LLMInterpretError(f"Claude 호출 타임아웃({_LLM_TIMEOUT_SEC}초 초과)") from exc

    if proc.returncode != 0:
        raise LLMInterpretError(
            "Claude 호출 실패(exit " + str(proc.returncode) + "): " + proc.stderr.strip()[:500]
        )

    try:
        outer = json.loads(proc.stdout)
        parsed = json.loads(outer["result"])
        intent = parsed["intent"]
        target_hq = parsed["target_hq"]
        if intent is not None and not isinstance(intent, str):
            raise TypeError("intent는 string 또는 null이어야 함")
        if target_hq is not None and not isinstance(target_hq, str):
            raise TypeError("target_hq는 string 또는 null이어야 함")
    except (ValueError, KeyError, TypeError) as exc:
        raise LLMInterpretError("Claude 응답 파싱 실패: " + str(exc)) from exc

    return intent, target_hq


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """정적 파일 서빙(기존과 동일) + `/api/command`·`/api/llm-command` 두 경로만 추가."""

    def do_POST(self):
        if self.path == "/api/command":
            self._handle_command()
        elif self.path == "/api/llm-command":
            self._handle_llm_command()
        else:
            self._send_json(http.HTTPStatus.NOT_FOUND, {"error": "알 수 없는 경로: " + self.path})

    def _read_raw_input(self) -> str:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        raw_input = body["raw_input"]
        if not isinstance(raw_input, str):
            raise TypeError("raw_input은 문자열이어야 함")
        return raw_input

    def _handle_command(self):
        try:
            raw_input = self._read_raw_input()
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

    def _handle_llm_command(self):
        try:
            raw_input = self._read_raw_input()
        except (ValueError, KeyError, TypeError) as exc:
            self._send_json(
                http.HTTPStatus.BAD_REQUEST,
                {"error": "잘못된 요청 본문 — raw_input(string) 필드가 필요함: " + str(exc)},
            )
            return

        try:
            intent, target_hq = _interpret_with_claude(raw_input)
        except LLMInterpretError as exc:
            self._send_json(http.HTTPStatus.BAD_GATEWAY, {"error": str(exc)})
            return

        # parse_command()의 정규식 분류 대신 Claude의 분류 결과로 Command를
        # 만든다 — Command/CommandResult Contract와 resolve()는 그대로다.
        command = Command(raw_input=raw_input, intent=intent, target_hq=target_hq)
        result = resolve(command)
        self._send_json(
            http.HTTPStatus.OK,
            {
                "raw_input": raw_input,
                "llm_intent": intent,
                "llm_target_hq": target_hq,
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
