"""이 Prototype만을 위한 독립 Engine 호출 함수.

`hqs/development/mvp/engine.py`의 `call_engine()`을 import하지 않는다 — 특정 HQ 코드에 의존하지 않는 원시 기법인지 검증하려면 완전히 독립된 구현이어야 한다.
"""

import subprocess
import tempfile

ENGINE_CLI = "claude"
ENGINE_TIMEOUT_SECONDS = 180


def call_engine(prompt: str) -> str:
    result = subprocess.run(
        [
            ENGINE_CLI, "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch",
        ],
        capture_output=True,
        text=True,
        timeout=ENGINE_TIMEOUT_SECONDS,
        cwd=tempfile.gettempdir(),
    )
    return result.stdout
