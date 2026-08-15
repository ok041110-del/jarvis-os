"""Agent-Capability 매핑과 Agent 함수.

IMPLEMENTATION_RULES.md: "Registry 구현 금지 — Agent-Capability 매핑은
리터럴 딕셔너리 이상으로 발전시키지 않는다." AGENT_CAPABILITY_MAP은 그 리터럴
딕셔너리이며, 조회 함수/클래스로 감싸지 않는다.

Stop Trigger 감시 지점: 이 딕셔너리가 동적 등록 API나 클래스로 바뀌려는 순간
Registry 일반화이므로 즉시 중단하고 RFC로 넘긴다 (HANDOVER.md 참조).
"""

from .engine import call_engine

AGENT_CAPABILITY_MAP = {
    "code_review": "Backend Agent",
    "test_execution": "QA Agent",
}

# MVP-0004(Hello SDLC)가 추가하는 Capability만 담는 별도 리터럴 딕셔너리.
# AGENT_CAPABILITY_MAP(MVP-0001)을 확장하지 않는다 — 그 딕셔너리를 정확히
# 2개 항목으로 고정해 검증하는 기존 테스트(test_mvp_0001.py)를 그대로
# 유지하기 위함이다. 이 분리 자체가 Registry 중복 관리(RT-0001 Trigger)로
# 이어지는지는 MVP-0004-observation.md에서 관찰만 하고 판단하지 않는다.
HELLO_SDLC_CAPABILITY_MAP = {
    "requirement_analysis": "Requirements Agent",
    "design": "Design Agent",
    "code_generation": "Backend Agent",
}


NO_ISSUES_MARKER = "NO_ISSUES_FOUND"


def backend_agent_code_review(code: str) -> str:
    """Backend Agent가 code_review Capability를 수행한다.

    MVP-0025: 실제 Engine 실행(run_mvp_0001)에서, 이 함수와
    `qa_agent_test_execution`만 지시 문장 없이 `CODE_REVIEW:`/
    `TEST_EXECUTION:` 리터럴 마커만 붙여 호출하고 있었다 — 나머지 3개
    Agent 함수(requirement_analysis/design/code_generation)는 이미
    "리터럴 마커 단독으로는 Engine이 의도를 놓친다"는 이유로 지시
    문장이 붙어 있었다(위 각 함수 docstring 참고). 실제로 동일한
    문제가 test_execution에서 재현됐다(MVP-0025 Observation): Engine이
    테스트 케이스 대신 코드를 다시 리뷰하거나, 입력을 명확화 요청으로
    오인했다. 두 함수 모두 같은 패턴(지시 문장 추가)으로 맞웠다.

    MVP-0027: `workflow_0002.py`(RT-0001 관찰용 1개 분기)는 code_review
    결과에 이슈가 없으면 test_execution을 건너뛴다는 계약을 갖고 있다.
    그 판단은 원래 rule-based Engine이 항상 반환하던 고정 문자열
    ("뚜렷한 이슈가 발견되지 않았습니다.")로 이뤄졌는데, ENGINE-CONNECT-0001
    이후 `call_engine()`이 실제 Engine을 호출하면서 그 고정 문자열은
    더 이상 나오지 않는다 — 실제 실행으로 확인한 결과 분기가 항상
    test_execution을 실행하는 쪽으로만 동작했다(MVP-0027 Observation).
    이를 고치기 위해, 이슈가 없을 때만 끝에 `NO_ISSUES_MARKER`를
    그대로 적으라는 지시를 추가한다 — 특정 응답 구조(섹션/헤더)를
    요구하는 것이 아니라, MVP-0002가 이미 필요로 하던 단일 신호
    하나만 명시적으로 요청하는 것이다.

    MVP-0047: `code_review` Capability의 입력은 파일 하나의 텍스트뿐이라
    (`agents.py`/`engine.py` 어디에도 다른 프로젝트 파일을 함께 보여주는
    경로가 없다 — `call_engine()`의 `--disallowedTools`가 Read/Bash 등을
    전부 막아 Engine이 스스로 다른 파일을 열어볼 수도 없다), 상대 import가
    가리키는 파일이 실제로 존재하는지·실제로 그 이름을 정의하는지는
    이 Capability의 계약 안에서 원천적으로 검증 불가능하다. 실제
    프로젝트 Dogfooding(MVP-0046, `projects/notekeeper/issues/0002-store`)
    에서 `from .note import Note`(실재하지 않는 모듈)가 real Review에서
    아무 언급 없이 통과하는 것을 직접 재현해 확인했다. 이 함수의
    반환값(`str`)과 호출 형태(`call_engine()` 한 번)는 그대로 두고,
    지시 문장에 한 문장만 추가해 실제로 이 결함을 재현·검증했다
    (MVP-0047 Evidence): 상대 import를 발견하면 그 대상을 검증할 수
    없다는 사실 자체를 리뷰에 명시적으로 적으라고 요청한다. 새 입력
    Context(다른 파일 내용)를 넘기지 않는다 — 그러면 이 함수의 시그니처
    (`code: str`)를 넘어서는 Contract 변경이 된다. 대신 이미 참인
    사실(자신이 볼 수 있는 범위의 한계)을 명시적으로 말하게 할 뿐이다.
    실제 실행으로 확인한 결과, 존재하지 않는 모듈을 가리키는 import는
    "unverified"로 정확히 지목했고, 존재하는 모듈을 가리키는 import에는
    "틀렸다"고 오탐하지 않았다(둘 다 "검증 불가"라고만 말한다 — 그것이
    사실이므로).

    MVP-0050: `PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md`가 실제 Engine
    3회 반복 실행으로 `NO_ISSUES_MARKER`가 "실이슈 없음" 입력에서도 3회
    중 1회만 등장하는 것을 확인했다. "minor/style-level observation도
    이슈로 취급하라"는 한 문장을 지시문에 추가해 실제로 재검증했으나
    (`MVP-0050-observation.md`), 결과가 3회 중 0회로 오히려 악화됐다 —
    Engine이 그 문장을 받고 사소한 관찰까지 더 적극적으로 "issue"로
    적어, 마커가 더 나오지 않게 됐다. Failure로 판정하고 이 변경은
    되돌렸다(git 이력에 시도가 남아 있다) — 아래 instruction은 MVP-0047
    이전 원문과 동일하다."""
    instruction = (
        "Review the following code and describe issues in prose "
        "(bugs, risks, style) — do not rewrite or restate the code as your answer. "
        "You are shown only this single file, not the rest of the project. "
        "For every `from .module import Name`-style relative import, you cannot "
        "verify that `module` actually exists as a sibling file or that `Name` is "
        "actually defined there — explicitly call out each such import as an "
        "unverified assumption that must be checked against the real project "
        "files, and say so even if the import looks syntactically fine. "
        "Respond entirely in English, regardless of the language used in the "
        "code's comments or identifiers. "
        f"If and only if you find no real issues, end your response with the "
        f"exact line: {NO_ISSUES_MARKER}"
    )
    return call_engine(f"CODE_REVIEW:{instruction}\n\n{code}")


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent가 test_execution Capability(테스트 케이스 제안)를 수행한다.
    지시 문장을 추가한 이유는 `backend_agent_code_review` docstring 참고
    (MVP-0025)."""
    instruction = (
        "Based on the following code and its review, propose a list of "
        "test cases to add — do not review the code again."
    )
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{instruction}\n\n{payload}")


def requirements_agent_requirement_analysis(issue: dict) -> str:
    """Requirements Agent가 requirement_analysis Capability를 수행한다.

    프롬프트 앞에 한 문장짜리 자연어 지시를 붙인다 — 실제 Engine으로
    실행했을 때(2026-08-08) 리터럴 마커(`REQUIREMENT_ANALYSIS:`) 단독으로는
    Engine이 코드를 바로 작성해 버리는 등 Capability 의도를 놓치는 사례가
    관찰됐다. 이 문장은 무엇을 요구하는지만 밝힐 뿐, 출력 구조(필드·헤더)를
    지정하지 않는다 — Output Contract가 아니라 입력 프롬프트 보강이다.
    """
    instruction = (
        "Analyze the following feature request and describe the "
        "requirement in prose (goal, scope, risks) — do not write code."
    )
    payload = f"{issue['title']}|||{issue['description']}"
    return call_engine(f"REQUIREMENT_ANALYSIS:{instruction}\n\n{payload}")


def design_agent_design(issue: dict, requirement: str) -> str:
    """Design Agent가 design Capability를 수행한다. 지시 문장의 목적은
    `requirements_agent_requirement_analysis`와 같다."""
    instruction = (
        "Based on the following requirement, describe a design in prose "
        "(approach, responsibilities, risks) — do not write code yet."
    )
    payload = f"{issue['title']}\n---REQUIREMENT---\n{requirement}"
    return call_engine(f"DESIGN:{instruction}\n\n{payload}")


def _strip_code_fence(text: str) -> str:
    """실제 Engine 3회 독립 호출(Python/JavaScript 각각, 서로 다른
    Issue)로 직접 확인함: `backend_agent_code_generation`이 "Return
    only the code, with no surrounding commentary"라고 명시적으로
    요청해도, 실제 Engine은 매번 ```{lang}\\n...\\n``` 마크다운 fence로
    감싸서 반환했다 — 지시가 요구한 Contract("코드만")를 텍스트
    형태(fence 포함)가 어긴다. 이 결과는 `backend_agent_code_review`/
    `qa_agent_test_execution`의 `code` 입력으로 그대로 전달되므로,
    fence를 벗겨 실제로 코드만 남기는 것이 지시된 Contract와 일치한다.
    감싸진 형태(첫 줄이 ```로 시작하고 마지막 줄이 정확히 ```인 경우)만
    벗긴다 — 그 형태가 아니면(Engine이 fence 없이 코드만 반환한 경우
    등) 원문을 그대로 반환한다. 새 Capability/파싱 로직이 아니라, 이미
    존재하는 단일 Capability(code_generation)의 출력을 그 Capability
    자신의 지시문 Contract에 맞게 정리하는 후처리다."""
    lines = text.strip().splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1])
    return text


def backend_agent_code_generation(design: str) -> str:
    """Backend Agent가 code_generation Capability를 수행한다. 지시 문장의
    목적은 위와 같다 — 이번에는 반대로 코드**만** 요구한다(다음 Task인
    code_review/test_execution이 코드를 직접 입력으로 받기 때문).

    `_strip_code_fence` 적용 이유는 그 함수 docstring 참고 — 실제
    Engine이 지시를 어기고 마크다운 fence로 감싸는 것을 직접 확인해
    벗긴다."""
    instruction = (
        "Based on the following design, write the implementation code. "
        "Return only the code, with no surrounding commentary."
    )
    code = call_engine(f"CODE_GENERATION:{instruction}\n\n{design}")
    return _strip_code_fence(code)
