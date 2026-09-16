"""Vercel Python Function — public preview에서 `/api/command`를 안전하게 차단한다.

로컬 `serve_dashboard.py`의 `/api/command`는 `execute_workflow`+`development`일
때 실제 `run_workflow()`를 호출할 수 있다. 이 Function은 그 로직을 재구현하지
않고, 이 Preview 단계(상시 접속 Dashboard UI만 공개, Workflow 실행 공개는
별도 검토 대상)에서 누구나 호출 가능한 public endpoint가 실제 Workflow를
트리거하지 못하도록 항상 차단 응답만 반환한다. 응답 스키마는 기존
`serve_dashboard.py`의 `/api/command` 응답 필드와 동일하게 맞춰 Command
Center Terminal UI(`data/adapters/adapters.js::executeCommand`)가 그대로
동작하게 한다(reason이 오류 줄로 표시됨, UI 변경 없음).
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        raw_input = None
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            candidate = body.get("raw_input")
            if isinstance(candidate, str):
                raw_input = candidate
        except (ValueError, TypeError):
            raw_input = None

        payload = {
            "raw_input": raw_input,
            "intent": None,
            "target_hq": None,
            "status": "blocked",
            "reason": "public_preview_command_execution_disabled",
            "hq_identity": None,
            "detail": [
                "Public Preview에서는 실제 Workflow 실행이 비활성화되어 있습니다 "
                "(Dashboard UI/정적 데이터 열람만 공개됨)."
            ],
        }
        response_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
