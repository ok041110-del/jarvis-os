"""단일 Engine 호출 함수.

IMPLEMENTATION_RULES.md: "Engine Gateway(Port/Adapter 추상화) 구현 금지 —
단일 함수로 Engine을 호출하는 것으로 충분하다." 여러 Engine 중 선택하는
로직(Engine Routing)은 두지 않는다 — 그런 필요가 생기면 Gateway 추출
신호이므로 RFC 없이 여기서 분기를 늘리지 않는다.
"""

import subprocess
import tempfile


ENGINE_CLI = "claude"
ENGINE_TIMEOUT_SECONDS = 180

DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"

# 도구 부재를 Engine이 응답 본문에 서술하면 그 서술이 다음 Task의
# 입력으로 전파되므로, 매번 새로 보고할 대상이 아님을 미리 알린다.
STATELESS_CALL_NOTICE = (
    "You are being invoked as a stateless text-in/text-out function call, "
    "not an interactive coding session. You have no filesystem or shell "
    "tools available on this call, and that is expected and permanent — "
    "do not report it, apologize for it, or ask for permissions. Respond "
    "only with the requested content as plain text."
)


def call_engine(prompt: str) -> str:
    """단일 Engine 호출 지점(ENGINE-CONNECT-0001) — Routing/Gateway 없음.
    `--disallowedTools`는 "텍스트를 받아 텍스트를 반환한다"는 이 함수의
    계약을 실제 Engine 위에서 유지하기 위한 호출 인자다(도구가 있으면
    Engine이 파일 쓰기 권한을 요청하는 등 계약을 벗어난다).

    `cwd`를 저장소 밖으로 고정한다 — 저장소 안이면 이 저장소의
    `CLAUDE.md`/Skill을 읽는 대화형 세션처럼 오염될 수 있다."""
    result = subprocess.run(
        [
            ENGINE_CLI, "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", DISALLOWED_TOOLS,
            "--append-system-prompt", STATELESS_CALL_NOTICE,
        ],
        capture_output=True,
        text=True,
        timeout=ENGINE_TIMEOUT_SECONDS,
        cwd=tempfile.gettempdir(),
    )
    return result.stdout
