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
    전용 계약을 강제하고, `cwd`를 저장소 밖으로 고정해 CLAUDE.md 오염을 막는다.

    subprocess가 실패(non-zero returncode)하면 stdout 대신 returncode/stderr를
    담은 RuntimeError를 raise한다 — 호출부(workflow.py 등)가 이미
    `except Exception`으로 잡아 `Engine call failed: {exc}`로 구조화하므로,
    여기서 실패를 삼키면 그 구조화가 발동하지 않고 빈/부분 stdout이 성공
    결과로 오인된다."""
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
    if result.returncode != 0:
        raise RuntimeError(
            f"exit code {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout
