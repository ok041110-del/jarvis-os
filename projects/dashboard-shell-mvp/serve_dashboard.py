"""Dashboard Shell MVP — 로컬 실행 스크립트.

정적 파일 서빙 외 `/api/command`·`/api/llm-command`·`/api/openrouter-command` 세 경로만 추가한다. `/api/command`는 raw_input을 command-contract의 `parse_command()`에 그대로 전달한다(로직 복제 없음). intent가 `execute_workflow`이고 target_hq가 `development`일 때만 `_resolve_or_execute()`가 기존 `hqs/development/workflow.py::run_workflow()`를 직접 호출하고, 그 외 intent는 `resolver.resolve()`(무수정)로 그대로 넘긴다 — `resolver.py`는 여전히 Engine/HQ 코드를 import하지 않는다는 자신의 Boundary를 유지한다. `/api/llm-command`는 그 앞단에 실제 Claude 호출을 한 번 더 거치고, `/api/openrouter-command`는 같은 앞단을 기존 `hqs/development/mvp/openrouter_engine.py`의 `call_engine_via_openrouter()`(Thin Engine Caller, ADR-0026/0027)로 수행한다 — Dashboard 전용 LLM client를 새로 만들지 않고 기존 Engine 호출 경로를 재사용한다."""

from __future__ import annotations

import http.server
import json
import re
import socket
import subprocess
import sys
from functools import partial
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
COMMAND_CONTRACT_DIR = DASHBOARD_DIR.parent / "command-contract"
DEV_HQ_DIR = DASHBOARD_DIR.parents[1] / "hqs" / "development"
sys.path.insert(0, str(COMMAND_CONTRACT_DIR))

from command import Command, CommandResult  # noqa: E402
from resolver import parse_command, resolve  # noqa: E402

# OpenRouter 경로는 Dashboard 전용 client를 만들지 않고 Dev HQ MVP가 이미
# 쓰는 `mvp/openrouter_engine.py`(단일 함수, str -> str, 단일 RuntimeError)
# 를 그대로 재사용한다 — `IMPLEMENTATION_RULES.md`의 Engine Gateway/Routing
# 금지와 동일한 이유다. `hqs/` production path 어디도 수정하지 않는다.
# `DEV_HQ_DIR`(= hqs/development)은 `_run_development_workflow()`가 이미
# 쓰는 경로와 같다 — 별도 MVP_DIR을 새로 만들지 않는다.
if str(DEV_HQ_DIR) not in sys.path:
    sys.path.insert(0, str(DEV_HQ_DIR))
from mvp.openrouter_engine import call_engine_via_openrouter  # noqa: E402

DEFAULT_PORT = 8765
MAX_PORT_ATTEMPTS = 20


class WorkflowExecutionError(Exception):
    """`run_workflow()` 호출 자체(Import/실행)가 실패했을 때 — Stage 실패(`failed_at`)와는 다르다."""


def _run_development_workflow(raw_input: str) -> dict:
    """`hqs/development/workflow.py::run_workflow()`를 그대로 호출한다(재구현 없음).

    Command Center raw_input을 최소한의 Issue({"title", "description"})로만
    감싼다 — 새 Task/Issue Contract를 만들지 않는다.
    """
    if str(DEV_HQ_DIR) not in sys.path:
        sys.path.insert(0, str(DEV_HQ_DIR))
    try:
        from workflow import run_workflow  # noqa: E402
    except Exception as exc:  # noqa: BLE001 — import 실패 원인을 그대로 전달
        raise WorkflowExecutionError(f"run_workflow import 실패: {exc}") from exc

    issue = {"title": raw_input[:80], "description": raw_input}
    try:
        return run_workflow(issue)
    except Exception as exc:  # noqa: BLE001 — run_workflow() 자체의 미처리 예외
        raise WorkflowExecutionError(f"run_workflow 실행 실패: {exc}") from exc


def _resolve_or_execute(command: Command) -> CommandResult:
    """`execute_workflow`(Development HQ)만 `run_workflow()`로 라우팅하고, 그 외는 `resolver.resolve()`(무수정) 그대로 사용한다."""
    if command.intent == "execute_workflow" and command.target_hq == "development":
        try:
            result = _run_development_workflow(command.raw_input)
        except WorkflowExecutionError as exc:
            return CommandResult(status="invalid", reason=str(exc))
        reason = None if result["failed_at"] is None else f"workflow_failed_at_{result['failed_at']}"
        return CommandResult(
            status="ok",
            reason=reason,
            hq_identity="Development HQ",
            detail=[json.dumps(result, ensure_ascii=False)],
        )
    return resolve(command)

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

# OpenRouter 분류 프롬프트 — 스키마 필드(intent/target_hq)는 Claude 경로와
# 정확히 같다. 모델 자유 선택(free pool)을 전제로 하므로 영문·JSON-only 지시로
# 쓴다 — 특정 모델의 말투에 맞춘 프롬프트를 만들지 않는다(모델 독립성 경계).
_OPENROUTER_CLASSIFIER_PROMPT_TEMPLATE = (
    'User message: "{raw_input}"\n\n'
    "You are a classifier that converts a natural language message into a "
    "JSON object with exactly this schema and no other keys:\n\n"
    '{{"response": {{"intent": "show_status" | null, '
    '"target_hq": "development" | "investment" | "trading" | null}}}}\n\n'
    "Rules:\n"
    '- For a status-lookup request, set intent="show_status"\n'
    "- For anything else, set intent=null\n"
    "- If the message does not point at any HQ, set target_hq=null\n"
    "- Output exactly one JSON object and nothing else. No markdown, no explanations."
)

# 테스트가 이 함수 객체를 교체해 mock한다 — 새 env var/설정 체계를 만들지 않고
# `test_omniroute_engine.py`가 쓰는 것과 같은 "엔진 자리를 바꿔 끼우는" 방식이다.
_openrouter_engine_call = call_engine_via_openrouter


class LLMInterpretError(Exception):
    """LLM 호출/네트워크 실패 — 호출부가 Mock으로 대체하지 않고 그대로 드러내야 함."""


class LLMResponseFormatError(LLMInterpretError):
    """LLM이 응답했으나 그 텍스트가 {intent, target_hq} JSON 스키마를 지키지 않음 — provider 실패(502)와 구분해 422로 드러낸다."""


def _interpret_with_claude(raw_input: str) -> tuple[str | None, str | None]:
    """raw_input을 Command 스키마(intent/target_hq)로 분류한다.

`--tools ""`로 Bash/Read 등 모든 Tool(Agent 포함)을 비활성화해 Claude가 파일을 직접 읽거나 행동을 취하지 못하게 막는다 — 순수 텍스트 분류 1회 호출이다. `--restricted`로 이 저장소의 CLAUDE.md/ project 설정도 불러오지 않는다(분류와 무관한 컨텍스트 배제).
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


def _classify_with_openrouter(raw_input: str) -> dict:
    """`call_engine_via_openrouter()`(기존 Engine 호출 경로, 무수정) 1회로 raw_input을 분류해 구조화한다.

이 함수가 파싱 책임을 전부 진다 — Engine 모듈은 str -> str 계약 그대로 둔다. 자유모델 응답의 실측 편차(markdown fence, 필드 앞 라벨, 모델 별도 텍스트)를 순서대로 벗긴다:

    1. ```json fence 제거
    2. "intent:" 라벨 형태의 답변은 라벨을 벗겨 정상 JSON으로 복구
    3. 정상 JSON이면 그대로 사용

모든 단계가 실패하면 `LLMResponseFormatError` — Mock으로 대체하지 않고 호출부가 그대로 드러낸다. 상태 코드(502 provider/timeout vs 422 format)는 호출부가 구분해 응답한다.
    """
    prompt = _OPENROUTER_CLASSIFIER_PROMPT_TEMPLATE.format(raw_input=raw_input)
    try:
        engine_output = _openrouter_engine_call(prompt)
    except RuntimeError as exc:
        # Engine 계약 단일 예외를 그대로 호출부 오류로 옮긴다 — 예외 메시지에
        # API Key/헤더 값은 포함되지 않는다(openrouter_engine 계약).
        raise LLMInterpretError(str(exc)) from exc

    stripped = engine_output.strip()

    # 1) markdown fence 제거 — free 모델이 "JSON만 출력" 지시를 무시하고
    #    감싸는 실측 편차(정확히 감싸진 형태만 벗긴다).
    lines = stripped.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        stripped = "\n".join(lines[1:-1]).strip()

    # 2) 라벨형 답변 복구 — 필드 하나당 한 줄을 차지하는 형태만 처리한다.
    #    (fence 안쪽 필드 줄의 trailing comma는 조립 시 제거한다)
    if not stripped.startswith("{"):
        field_lines = [
            line.strip().rstrip(",")
            for line in stripped.splitlines()
            if re.match(r'^\s*"(intent|target_hq)"\s*:', line)
        ]
        if len(field_lines) == 2:
            stripped = "{" + ", ".join(field_lines) + "}"

    # 3) 정상 JSON 파싱 — 실패해도 여기서 끝내지 않고 format error로 옮긴다.
    try:
        parsed = json.loads(stripped)
        if not isinstance(parsed, dict):
            raise TypeError("응답이 JSON 객체가 아님")
        intent = parsed.get("intent")
        target_hq = parsed.get("target_hq")
        if intent is not None and not isinstance(intent, str):
            raise TypeError("intent는 string 또는 null이어야 함")
        if target_hq is not None and not isinstance(target_hq, str):
            raise TypeError("target_hq는 string 또는 null이어야 함")
    except (ValueError, TypeError) as exc:
        raise LLMResponseFormatError("OpenRouter 응답 파싱 실패: " + str(exc)) from exc

    return {"intent": intent, "target_hq": target_hq}


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """정적 파일 서빙(기존과 동일) + `/api/command`·`/api/llm-command`·`/api/openrouter-command` 세 경로만 추가."""

    def do_POST(self):
        if self.path == "/api/command":
            self._handle_command()
        elif self.path == "/api/llm-command":
            self._handle_llm_command()
        elif self.path == "/api/openrouter-command":
            self._handle_openrouter_command()
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
        result = _resolve_or_execute(command)
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
        result = _resolve_or_execute(command)
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

    def _handle_openrouter_command(self):
        try:
            raw_input = self._read_raw_input()
        except (ValueError, KeyError, TypeError) as exc:
            self._send_json(
                http.HTTPStatus.BAD_REQUEST,
                {"error": "잘못된 요청 본문 — raw_input(string) 필드가 필요함: " + str(exc)},
            )
            return

        try:
            classification = _classify_with_openrouter(raw_input)
        except LLMResponseFormatError as exc:
            # Provider/네트워크 실패(502)와 응답 형식 실패(422)를 구분해 드러낸다
            # — 어느 쪽도 Mock으로 대체하지 않는다.
            self._send_json(http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error": str(exc)})
            return
        except LLMInterpretError as exc:
            self._send_json(http.HTTPStatus.BAD_GATEWAY, {"error": str(exc)})
            return

        # 기존 `/api/llm-command`와 정확히 같은 후반부 — Command/CommandResult
        # Contract와 `_resolve_or_execute()`는 무수정이다. resolver가 지원하지
        # 않는 분류(예: trading)도 그대로 넘겨 resolver가 거부하게 둔다 —
        # LLM 분류가 실행 Boundary를 우회하지 않음을 보여주는 지점이다.
        command = Command(
            raw_input=raw_input,
            intent=classification["intent"],
            target_hq=classification["target_hq"],
        )
        result = _resolve_or_execute(command)
        self._send_json(
            http.HTTPStatus.OK,
            {
                "raw_input": raw_input,
                "llm": classification,
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
