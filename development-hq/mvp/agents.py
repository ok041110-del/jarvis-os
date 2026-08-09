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
    하나만 명시적으로 요청하는 것이다."""
    instruction = (
        "Review the following code and describe issues in prose "
        "(bugs, risks, style) — do not rewrite or restate the code as your answer. "
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


def backend_agent_code_generation(design: str) -> str:
    """Backend Agent가 code_generation Capability를 수행한다. 지시 문장의
    목적은 위와 같다 — 이번에는 반대로 코드**만** 요구한다(다음 Task인
    code_review/test_execution이 코드를 직접 입력으로 받기 때문)."""
    instruction = (
        "Based on the following design, write the implementation code. "
        "Return only the code, with no surrounding commentary."
    )
    return call_engine(f"CODE_GENERATION:{instruction}\n\n{design}")
