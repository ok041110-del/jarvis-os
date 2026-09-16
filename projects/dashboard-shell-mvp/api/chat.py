"""Vercel Python Function — Command Center Chat을 실제 OpenRouter Engine에 연결한다.

`hqs/development/mvp/openrouter_engine.py::call_engine_via_openrouter()`를
Vercel build step에서 Function root(`api/`)로 stage한 뒤 그대로 import해서
호출한다(Engine 구현 자체는 수정하지 않는다). 새 Engine Gateway/Provider
abstraction을 만들지 않고, Command Contract/Resolver(`command.py`/`resolver.py`)도
거치지 않으며, Workflow(`run_workflow()`)도 호출하지 않는다 — 순수 stateless
대화 중계 1개 endpoint다. 대화 history는 요청 본문으로만 받아 prompt 구성에
쓰고 서버에 저장하지 않는다(브라우저 state가 유일한 history 저장소,
`ADR`/`RFC` 없이 새 Persistence를 만들지 않는다).

`OPENROUTER_API_KEY`는 staged `openrouter_engine.py`가 내부적으로 환경변수에서만
읽는다 — 이 Function은 API key를 직접 다루거나 client에 노출하지 않는다.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

MAX_HISTORY_MESSAGES = 20


def _build_prompt(history: list, message: str) -> str:
    """history + 새 message를 단일 prompt 문자열로 합성한다.

    `call_engine_via_openrouter(prompt: str)`은 단일 문자열만 받으므로,
    multi-turn 여부와 무관하게 여기서 하나로 합친다 — Engine 쪽 Contract는
    바꾸지 않는다.
    """
    lines = []
    for turn in history[-MAX_HISTORY_MESSAGES:]:
        role = turn.get("role") if isinstance(turn, dict) else None
        text = turn.get("text") if isinstance(turn, dict) else None
        if role not in ("user", "agent") or not isinstance(text, str):
            continue
        speaker = "User" if role == "user" else "Assistant"
        lines.append(f"{speaker}: {text}")
    lines.append(f"User: {message}")
    lines.append("Assistant:")
    return "\n".join(lines)


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, TypeError) as exc:
            self._send_json(400, {"status": "error", "reason": "잘못된 요청 본문(JSON 아님): " + str(exc)})
            return

        message = body.get("message")
        history = body.get("history")
        if not isinstance(message, str) or not message.strip():
            self._send_json(
                400,
                {"status": "error", "reason": "message(비어있지 않은 string) 필드가 필요함"},
            )
            return
        if not isinstance(history, list):
            history = []

        try:
            from openrouter_engine import call_engine_via_openrouter  # noqa: E402
        except Exception as exc:  # noqa: BLE001 — import 실패 원인을 그대로 전달
            self._send_json(502, {"status": "error", "reason": "openrouter_engine import 실패: " + str(exc)})
            return

        prompt = _build_prompt(history, message)
        try:
            reply = call_engine_via_openrouter(prompt)
        except Exception as exc:  # noqa: BLE001 — Engine 실패(API key 미설정 포함)를 그대로 드러냄
            self._send_json(502, {"status": "error", "reason": str(exc)})
            return

        self._send_json(200, {"status": "ok", "reply": reply})

    def _send_json(self, status: int, payload: dict) -> None:
        response_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
