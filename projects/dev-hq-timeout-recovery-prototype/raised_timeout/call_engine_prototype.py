"""Timeout 상향 Prototype — `development-hq/mvp/engine.py`의 `call_engine()`을
그대로 복제하되 `ENGINE_TIMEOUT_SECONDS`만 인자로 받는 project-local
실험용 함수. `development-hq/` 어떤 파일도 import하지 않고 수정하지도
않는다 — Dev HQ v1.0 Freeze를 그대로 유지한 채, "타임아웃을 올리면
실패율이 실제로 줄어드는가"만 격리된 환경에서 검증하기 위한 Prototype이다.

Architecture 반영 여부는 이 실험과 별개다 — 이 함수가 검증에서 유효하다고
나오더라도, `engine.py`의 `ENGINE_TIMEOUT_SECONDS`를 실제로 바꾸려면
RFC → ADC → ADR 절차를 거쳐야 한다(PR #75 EVIDENCE.md 참조).
"""

import subprocess
import tempfile

ENGINE_CLI = "claude"

DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"

STATELESS_CALL_NOTICE = (
    "You are being invoked as a stateless text-in/text-out function call, "
    "not an interactive coding session. You have no filesystem or shell "
    "tools available on this call, and that is expected and permanent — "
    "do not report it, apologize for it, or ask for permissions. Respond "
    "only with the requested content as plain text."
)


def call_engine_with_timeout(prompt: str, timeout_seconds: int) -> str:
    """`call_engine()`과 동일한 CLI 인자로 동일한 Engine을 호출하되,
    `ENGINE_TIMEOUT_SECONDS`(180) 대신 실험 대상 timeout_seconds를 쓴다.
    """
    result = subprocess.run(
        [
            ENGINE_CLI, "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", DISALLOWED_TOOLS,
            "--append-system-prompt", STATELESS_CALL_NOTICE,
        ],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=tempfile.gettempdir(),
    )
    return result.stdout
