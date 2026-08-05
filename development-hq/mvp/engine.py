"""단일 Engine 호출 함수.

IMPLEMENTATION_RULES.md: "Engine Gateway(Port/Adapter 추상화) 구현 금지 —
단일 함수로 Engine을 호출하는 것으로 충분하다." 이 파일은 그 단일 함수만 가진다.
여러 Engine 중 선택하는 로직(Engine Routing)은 두지 않는다.

Kernel Extraction Candidate: 이 함수가 실제 LLM Engine 호출로 교체되거나,
Task 종류에 따라 다른 Engine을 골라야 하는 필요가 생기면 그것이
Engine Gateway(Port/Adapter) 추출 신호다. RFC 없이 여기서 분기를 늘리지 않는다.
"""


def call_engine(prompt: str) -> str:
    """단일 Engine 호출 지점. 지금은 규칙 기반 응답을 반환한다."""
    return _rule_based_response(prompt)


def _rule_based_response(prompt: str) -> str:
    if prompt.startswith("CODE_REVIEW:"):
        return _review_code(prompt[len("CODE_REVIEW:"):])
    if prompt.startswith("TEST_EXECUTION:"):
        return _suggest_tests(prompt[len("TEST_EXECUTION:"):])
    return ""


def _review_code(code: str) -> str:
    findings = []
    lines = code.splitlines()

    if "except:" in code or "except :" in code:
        findings.append("bare except 절이 있습니다. 구체적인 예외 타입을 지정하세요.")
    if "def " in code and "TODO" in code:
        findings.append("TODO 주석이 남아있습니다. 구현을 완료하거나 이슈로 분리하세요.")
    if '"""' not in code and "'''" not in code:
        findings.append("함수/모듈에 docstring이 없습니다. 목적과 입출력을 문서화하세요.")
    for i, line in enumerate(lines, start=1):
        if len(line) > 100:
            findings.append(f"{i}번째 줄이 100자를 초과합니다. 가독성을 위해 줄바꿈하세요.")
    if "def " in code and "=[]" in code.replace(" ", ""):
        findings.append("mutable default argument(빈 리스트)가 있습니다. None 기본값 후 내부에서 초기화하세요.")

    if not findings:
        findings.append("뚜렷한 이슈가 발견되지 않았습니다. 전체적으로 양호합니다.")

    return "\n".join(f"- {f}" for f in findings)


def _suggest_tests(payload: str) -> str:
    code, _, review = payload.partition("\n---REVIEW---\n")

    func_names = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            name = stripped[len("def "):].split("(", 1)[0].strip()
            func_names.append(name)

    cases = []
    if func_names:
        for name in func_names:
            cases.append(f"{name}() 정상 입력에 대한 기본 동작 검증")
            cases.append(f"{name}() 빈 입력/None 입력에 대한 경계값 검증")
    else:
        cases.append("스크립트 최상위 로직에 대한 실행 결과 검증")

    if "bare except" in review:
        cases.append("의도적으로 예외를 발생시켜 예외 처리 동작을 검증하는 테스트")
    if "mutable default argument" in review:
        cases.append("기본 인자를 사용하는 연속 호출 간 상태 공유가 없는지 검증하는 테스트")

    return "\n".join(f"- {c}" for c in cases)
