"""단일 Engine 호출 함수 — Gateway 추상화·Engine Routing 없음(IMPLEMENTATION_RULES.md)."""

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
    """단일 Engine 호출 지점(ENGINE-CONNECT-0001). `disallowedTools`로 텍스트
    전용 계약을 강제하고, `cwd`를 저장소 밖으로 고정해 CLAUDE.md 오염을 막는다."""
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
