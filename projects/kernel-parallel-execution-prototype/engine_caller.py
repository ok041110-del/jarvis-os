"""이 Prototype만을 위한 독립 Engine 호출 함수.

`hqs/development/mvp/engine.py`의 `call_engine()`을 import하지 않는다 —
Kernel Candidate가 "특정 HQ 코드에 실제로 의존하지 않는" 원시 기법인지
검증하는 것이 목적이므로, 이 파일 자체가 그 코드로부터 완전히 독립된
별도 구현이어야 검증이 성립한다. 로직은 의도적으로 최소화했다(단일
함수, Registry/Gateway 없음) — `hqs/development/mvp/engine.py`와
"같은 패턴을 쓴다"는 사실 자체가 이 패턴이 특정 코드가 아니라 일반
기법임을 보여준다.
"""

import subprocess
import tempfile

ENGINE_CLI = "claude"
ENGINE_TIMEOUT_SECONDS = 180


def call_engine(prompt: str) -> str:
    """단일 Engine 호출 함수. 텍스트를 받아 텍스트를 반환한다."""
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
