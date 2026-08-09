"""단일 Engine 호출 함수.

IMPLEMENTATION_RULES.md: "Engine Gateway(Port/Adapter 추상화) 구현 금지 —
단일 함수로 Engine을 호출하는 것으로 충분하다." 이 파일은 그 단일 함수만 가진다.
여러 Engine 중 선택하는 로직(Engine Routing)은 두지 않는다.

ENGINE-CONNECT-0001(worktree 실험)에서 이 함수를 실제 Claude Code Engine
호출로 교체해도 Stop Trigger가 발동하지 않음을 확인했다 — 단일 함수 구조를
유지한 채 본문만 실제 호출로 바꿨다. 그 실험 결과를 그대로 tracked
branch에 반영한다.

MVP-0043: 실제 Engine 배선(ENGINE-CONNECT-0001) 이전에 이 파일이 쓰던
rule-based 응답 로직(`_rule_based_response`와 그 하위 함수 전체, 약 790줄)을
삭제했다. `call_engine()`은 그 배선 이후 한 번도 그 경로를 호출한 적이
없고(`_rule_based_response` 자체가 미사용), 저장소 안 다른 어떤 파일도 그
함수들을 참조하지 않는다는 것을 실제 grep으로 확인했다 — 죽은 코드였다.
이 파일은 이제 실제로 호출되는 유일한 함수(`call_engine`)만 가진다.

Kernel Extraction Candidate: Task 종류에 따라 다른 Engine을 골라야 하는
필요가 생기면 그것이 Engine Gateway(Port/Adapter) 추출 신호다. RFC 없이
여기서 분기를 늘리지 않는다.
"""

import subprocess
import tempfile


DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"

# 도구 차단 이후 관찰된 두 번째 문제(2026-08-08): 도구가 없다는 사실
# 자체를 응답 내용으로 서술("I don't have filesystem access...")해,
# 그 서술이 다음 Task의 입력으로 전파됐다. 이 함수의 계약(텍스트를 받아
# 텍스트를 반환한다)에는 원래부터 도구가 없었으므로, 그 부재를 매번
# 새로 보고할 대상이 아니라는 사실만 알린다. 특정 출력 구조(섹션 헤더
# 등)는 요구하지 않는다 — 그런 요구가 필요한 근거가 없음을 확인했다
# (`docs/`, `MVP.md`, `STRUCTURE.md` 어디에도 출력 형식을 요구하는
# 문서화된 Contract가 없다).
STATELESS_CALL_NOTICE = (
    "You are being invoked as a stateless text-in/text-out function call, "
    "not an interactive coding session. You have no filesystem or shell "
    "tools available on this call, and that is expected and permanent — "
    "do not report it, apologize for it, or ask for permissions. Respond "
    "only with the requested content as plain text."
)


def call_engine(prompt: str) -> str:
    """단일 Engine 호출 지점. 실제 Engine(Claude Code CLI, `claude -p`)을
    호출하고 Raw Output(stdout)을 그대로 반환한다. Engine Routing/Gateway
    없음 — 이 함수 하나가 유일한 호출 지점이다(ENGINE-CONNECT-0001).

    `--disallowedTools`로 파일/셸 도구를 막는다 — hello_sdlc Pipeline을
    실제 Engine으로 실행했을 때(2026-08-08 관찰), 도구가 허용된 상태의
    Engine이 텍스트 응답 대신 실제 파일 쓰기 권한을 요청해 그 요청 문구
    자체가 다음 Task의 입력으로 전파되는 것이 관찰됐다. 이 함수의 계약은
    "텍스트를 받아 텍스트를 반환한다"이며, 도구 차단은 그 계약을 실제
    Engine 위에서 유지하기 위한 것이다 — 새 Gateway/Adapter가 아니라
    같은 단일 함수의 호출 인자일 뿐이다. `STATELESS_CALL_NOTICE`도 같은
    계약을 유지하기 위한 것이다 — 새 출력 형식을 요구하지 않는다.

    MVP-0028: 이 함수는 `cwd`를 지정하지 않아 호출한 Python 프로세스의
    작업 디렉터리(이 저장소 안)를 그대로 물려받았다. `claude -p`는 실행
    디렉터리의 `CLAUDE.md`/Skill을 자동으로 읽으므로, Engine으로 호출된
    것이 실제로는 이 저장소의 project-level 지시(task-intake/
    context-loader 같은 Skill, "Architecture 경계" 절 등)를 그대로 읽고
    따르는 또 다른 대화형 Claude Code 세션처럼 동작했다 — 실제 실행으로
    확인된 사례(MVP-0009 Observation): REQUIREMENT_ANALYSIS 호출인데도
    "다음 Skill: context-loader"를 제안하거나 하위 조사 에이전트를
    언급하는 등, `STATELESS_CALL_NOTICE`가 요구하는 "텍스트를 받아
    텍스트만 반환하는 상태 없는 호출"과 다르게 동작했다. `cwd`를 이
    저장소 밖의 중립 디렉터리(`tempfile.gettempdir()`)로 고정하면 이
    문제가 사라짐을 같은 prompt로 직접 확인했다 — 새 Gateway/Adapter가
    아니라 기존 단일 함수 호출의 인자(`subprocess.run`의 `cwd`) 하나일
    뿐이다."""
    result = subprocess.run(
        [
            "claude", "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", DISALLOWED_TOOLS,
            "--append-system-prompt", STATELESS_CALL_NOTICE,
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=tempfile.gettempdir(),
    )
    return result.stdout
