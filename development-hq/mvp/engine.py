"""단일 Engine 호출 함수.

IMPLEMENTATION_RULES.md: "Engine Gateway(Port/Adapter 추상화) 구현 금지 —
단일 함수로 Engine을 호출하는 것으로 충분하다." 이 파일은 그 단일 함수만 가진다.
여러 Engine 중 선택하는 로직(Engine Routing)은 두지 않는다.

ENGINE-CONNECT-0001(worktree 실험)에서 이 함수를 실제 Claude Code Engine
호출로 교체해도 Stop Trigger가 발동하지 않음을 확인했다 — 단일 함수 구조를
유지한 채 본문만 실제 호출로 바꿨다. 그 실험 결과를 그대로 tracked
branch에 반영한다.

Kernel Extraction Candidate: Task 종류에 따라 다른 Engine을 골라야 하는
필요가 생기면 그것이 Engine Gateway(Port/Adapter) 추출 신호다. RFC 없이
여기서 분기를 늘리지 않는다.
"""

import re
import subprocess


DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"


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
    같은 단일 함수의 호출 인자일 뿐이다."""
    result = subprocess.run(
        [
            "claude", "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", DISALLOWED_TOOLS,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return result.stdout


def _rule_based_response(prompt: str) -> str:
    if prompt.startswith("CODE_REVIEW:"):
        return _review_code(prompt[len("CODE_REVIEW:"):])
    if prompt.startswith("TEST_EXECUTION:"):
        return _suggest_tests(prompt[len("TEST_EXECUTION:"):])
    if prompt.startswith("REQUIREMENT_ANALYSIS:"):
        return _analyze_requirement(prompt[len("REQUIREMENT_ANALYSIS:"):])
    if prompt.startswith("DESIGN:"):
        return _design_from_requirement(prompt[len("DESIGN:"):])
    if prompt.startswith("CODE_GENERATION:"):
        return _generate_code(prompt[len("CODE_GENERATION:"):])
    return ""


# MVP-0012: Validation이 입력 Artifact의 종류(Requirement/Architecture
# Draft/Source Code)를 구분하지 못하고, 코드가 아니면 전부 Design으로
# 취급하던 2-way 분류(코드 vs "코드가 아니면 Design")를 3-way로
# 넓힌다. Requirement Specification도 코드가 아니므로 예전에는
# `_review_design`으로 잘못 라우팅되어 "'## Component' 섹션이
# 없습니다" 같은 False Positive를 냈다(MVP-0012 Baseline으로 실측
# 확인). Validation Logic만 수정한다 — Planning/Design이 만드는 실제
# 산출물 텍스트(헤더 이름)는 그대로 읽기만 한다.
DESIGN_REQUIRED_SECTIONS = (
    "## Component",
    "## Responsibility",
    "## Interfaces",
    "## Constraints",
    "## Open Questions",
    "## Reference Requirement",
)
REQUIREMENT_REQUIRED_SECTIONS = (
    "## Goal",
    "## In Scope",
    "## Out of Scope",
    "## Acceptance Criteria (Draft)",
    "## Risks",
    "## Open Questions",
)


def _looks_like_code(text: str) -> bool:
    return bool(re.search(r"^\s*(def |class |import |from )", text, re.MULTILINE))


def _looks_like_design(text: str) -> bool:
    """Architecture Draft(Design 산출물, MVP-0011)만 갖는 마커로
    판단한다. `## Interfaces`와 `## Reference Requirement`는 Design만
    만드는 절이다 — Requirement에는 없다(Requirement은 Design 산출물
    안에 `## Reference Requirement` 절로 통째로 인용되어 나타나지만,
    이 함수는 코드 판정 다음 순서로만 호출되므로 그 안에 중첩된
    Requirement 텍스트가 먼저 Design으로 오판되는 것이 옳다 — 실제로
    Design 산출물 자체이기 때문이다)."""
    return "## Interfaces" in text or "## Reference Requirement" in text


def _looks_like_requirement(text: str) -> bool:
    """Requirement Specification(MVP-0005/0010)만 갖는 마커로
    판단한다. `_looks_like_design`이 먼저 걸러지므로, 이 함수에
    도달했다면 `## Interfaces`/`## Reference Requirement`가 없는
    텍스트다."""
    return "## Goal" in text and "## In Scope" in text


def _detect_artifact_stage(text: str) -> str:
    """입력 Artifact가 Requirement/Design(Architecture Draft)/Code 중
    무엇인지 규칙 기반으로 판단한다. 순서가 결과를 좌우한다 — 코드
    판정을 가장 먼저 하는 이유는, Implementation 산출물(코드)의
    docstring 안에는 Design 텍스트가, 그 안에는 다시 Requirement
    텍스트가 verbatim으로 중첩되어 있기 때문이다(MVP-0007/0008에서
    관찰된 Artifact 누적 이어붙이기). 코드 판정을 먼저 해야 실제
    Python 코드가 Design/Requirement로 오판되지 않는다."""
    if _looks_like_code(text):
        return "code"
    if _looks_like_design(text):
        return "design"
    if _looks_like_requirement(text):
        return "requirement"
    return "unknown"


def _review_requirement(requirement_text: str) -> str:
    """Requirement Specification(`_analyze_requirement`, MVP-0005/0010)의
    필수 섹션(Goal/In Scope/Out of Scope/Acceptance Criteria (Draft)/
    Risks/Open Questions) 존재 여부만 규칙 기반으로 확인한다. Design
    전용 규칙(Component/Interfaces 등)이나 Python 코드 전용 규칙(bare
    except 등)은 적용하지 않는다 — Requirement에는 의미가 없기
    때문이다.
    """
    findings = [
        f"'{section}' 섹션이 없습니다. Requirement Specification에 포함되어야 합니다."
        for section in REQUIREMENT_REQUIRED_SECTIONS
        if section not in requirement_text
    ]
    if not findings:
        findings.append("Requirement Specification에 필수 섹션(Goal/In Scope/Out of Scope/Acceptance Criteria/Risks/Open Questions)이 모두 포함되어 있습니다.")
    return "\n".join(f"- {f}" for f in findings)


def _review_design(design_text: str) -> str:
    """Design 산출물(Architecture Draft, MVP-0011)을 코드가 아닌 문서로
    인식하고, 필수 섹션(Component/Responsibility/Interfaces/
    Constraints/Open Questions/Reference Requirement) 존재 여부만
    규칙 기반으로 확인한다. `_review_python_code`의 Python 코드 전용
    규칙(bare except, docstring, mutable default 등)은 적용하지 않는다
    — 그 규칙들은 Design 문서에 의미가 없기 때문이다.
    """
    findings = [
        f"'{section}' 섹션이 없습니다. Architecture Draft에 포함되어야 합니다."
        for section in DESIGN_REQUIRED_SECTIONS
        if section not in design_text
    ]
    if not findings:
        findings.append("Architecture Draft에 필수 섹션(Component/Responsibility/Interfaces/Constraints/Open Questions/Reference Requirement)이 모두 포함되어 있습니다.")
    return "\n".join(f"- {f}" for f in findings)


def _suggest_requirement_checks(requirement_text: str) -> str:
    """Requirement Specification에 대해, Python 코드 전용 테스트
    케이스나 Design 전용 검증 항목 대신 Requirement 구조에서 실제로
    도출 가능한 검증 항목만 규칙 기반으로 제시한다."""
    cases = []
    if "## Acceptance Criteria (Draft)" in requirement_text:
        cases.append("Acceptance Criteria(Draft)에 나열된 각 항목이 실제로 검증 가능한 조건인지 확인")
    if "## Risks" in requirement_text:
        cases.append("Risks에 나열된 각 항목이 Design/Implementation 단계에서 실제로 완화되는지 확인")
    if not cases:
        cases.append("Requirement Specification에서 검증 가능한 섹션(Acceptance Criteria/Risks)을 찾지 못해 기본 검증 항목을 생성할 수 없음")
    return "\n".join(f"- {c}" for c in cases)


def _suggest_design_checks(design_text: str) -> str:
    """Design 산출물에 대해 Python 코드 전용 테스트 케이스(함수 단위
    정상/경계값 검증) 대신, Design 문서 구조에서 실제로 도출 가능한
    검증 항목만 규칙 기반으로 제시한다."""
    cases = []
    if "## Responsibility" in design_text:
        cases.append("Responsibility에 나열된 각 항목이 Requirement의 In Scope와 실제로 일치하는지 확인")
    if "## Interfaces" in design_text:
        cases.append("Interfaces에 나열된 각 검증 함수가 Implementation에서 실제로 정의되는지 확인")
    if "## Constraints" in design_text:
        cases.append("Constraints에 나열된 각 항목이 Implementation 단계에서 실제로 지켜지는지 확인")
    if not cases:
        cases.append("Architecture Draft에서 검증 가능한 섹션(Responsibility/Interfaces/Constraints)을 찾지 못해 기본 검증 항목을 생성할 수 없음")
    return "\n".join(f"- {c}" for c in cases)


def _review_python_code(code: str) -> str:
    """MVP-0005~0011까지 써온 Python 코드 전용 규칙(bare except, TODO
    주석, docstring, line length, mutable default)을 그대로 유지한다
    — Success Criteria("Code 입력은 기존 Python Rule을 유지한다")에
    따라 로직을 바꾸지 않았다."""
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


def _review_code(code: str) -> str:
    """Validation(code_review) Capability의 진입점. 입력이 Requirement/
    Design/Code 중 무엇인지 `_detect_artifact_stage()`로 판단해 해당
    Stage 전용 규칙만 적용한다(Stage-Aware Validation, MVP-0012).
    Stage를 판단할 수 없는 입력(`unknown`)은 MVP-0005~0011까지의
    기존 fallback 동작(Design 규칙 적용)을 그대로 유지한다 — 이전
    동작과의 호환을 위해서다.
    """
    stage = _detect_artifact_stage(code)
    if stage == "code":
        return _review_python_code(code)
    if stage == "requirement":
        return _review_requirement(code)
    return _review_design(code)


def _suggest_tests(payload: str) -> str:
    code, _, review = payload.partition("\n---REVIEW---\n")

    stage = _detect_artifact_stage(code)
    if stage == "requirement":
        return _suggest_requirement_checks(code)
    if stage != "code":
        return _suggest_design_checks(code)

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


OUT_OF_SCOPE_MARKERS = ("않는다", "제외", "범위 밖", "아니다")

# MVP-0010: 템플릿 채우기(Goal은 항상 "'{title}' 기능을 추가한다" 고정 문자열)
# 수준이던 Planning을 Issue 문장 분석 기반으로 발전시키기 위한 마커.
# 여전히 문자열 마커 매칭만 사용하는 규칙 기반 구현이다 — ML/LLM 호출 없음.
# 세 마커 집합은 서로 배타적이지 않다 — 한 문장이 Goal이면서 동시에
# Risk·Open Question으로도 뽑힐 수 있다(예: "...문제를 완화할 수 있는
# 방향으로 개선될 수 있는지 검토가 필요하다"는 개선 요청(Goal)이자
# 미해결 판단(Open Question)이다). 이 중복은 의도적으로 허용한다 —
# 각 절은 서로 다른 질문("무엇을 해야 하는가" vs "아직 무엇이
# 불확실한가")에 답하므로 같은 문장이 두 질문 모두에 답할 수 있다.
GOAL_MARKERS = ("필요하다", "해야 한다", "검토가 필요", "확인이 필요")
RISK_MARKERS = ("문제", "실패", "오류", "위험", "왜곡", "결함", "누락", "의도치 않게")
QUESTION_MARKERS = ("검토가 필요", "확인이 필요", "판단이 필요", "?")


def _split_sentences(text: str) -> list:
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", text)]
    return [s for s in sentences if s]


def _extract_goal(sentences: list, title: str) -> str:
    """Goal 마커가 있는 첫 문장을 Goal로 사용한다. 없으면 기존
    MVP-0005~0009의 고정 템플릿으로 되돌아간다 — Goal을 표현하는
    문장이 전혀 없는 Issue(예: 순수 사실 나열)에서도 Planning이 빈
    Goal을 반환하지 않도록 하기 위함이다."""
    for sentence in sentences:
        if any(marker in sentence for marker in GOAL_MARKERS):
            return sentence
    return f"'{title}' 기능을 추가한다."


def _extract_marked_sentences(sentences: list, markers: tuple, empty_note: str) -> str:
    matched = [s for s in sentences if any(marker in s for marker in markers)]
    if not matched:
        return f"- {empty_note}"
    return "\n".join(f"- {s}" for s in matched)


def _analyze_requirement(payload: str) -> str:
    """Issue(title|||description)를 Requirement Specification(Goal /
    Description / In Scope / Out of Scope / Acceptance Criteria (Draft) /
    Risks / Open Questions / Reference Context)으로 정제한다. 문장 분리와
    마커 매칭만 사용하는 규칙 기반 구현이다 — ML/LLM 호출 없음.

    MVP-0005~0009까지는 Goal이 `'{title}' 기능을 추가한다` 고정
    템플릿이었고, Acceptance Criteria는 In Scope 문장을 그대로
    재서술하는 것에 그쳤으며, Risks/Open Questions 절 자체가 없었다.
    MVP-0010은 Goal/Acceptance Criteria를 Issue 문장에서 추출하고,
    Risk/Open Question 절을 새로 추가한다 — 여전히 새 Capability는
    아니다. 기존 `requirement_analysis` Capability 하나의 내부
    로직만 바뀐다.

    Project Intelligence(`_enrich_issue`)가 덧붙인 `[Relevant Context]`
    블록은 문맥 문장으로 잘못 분류되지 않도록 별도 절(Reference Context)로
    분리한다 — 그 블록을 In/Out of Scope/Risk/Open Question 분류
    대상에서 제외한다.
    """
    title, _, description = payload.partition("|||")
    narrative, _, context_block = description.partition("[Relevant Context]")
    narrative = narrative.strip()
    context_block = context_block.strip()

    sentences = _split_sentences(narrative)
    in_scope = [s for s in sentences if not any(m in s for m in OUT_OF_SCOPE_MARKERS)]
    out_of_scope = [s for s in sentences if any(m in s for m in OUT_OF_SCOPE_MARKERS)]

    goal = _extract_goal(sentences, title)

    in_scope_lines = "\n".join(f"- {s}" for s in in_scope) if in_scope else "- (감지된 In Scope 문장 없음)"
    out_of_scope_lines = "\n".join(f"- {s}" for s in out_of_scope) if out_of_scope else "- (감지된 Out of Scope 문장 없음)"
    acceptance_lines = (
        "\n".join([f"- Goal이 실제로 충족됨을 확인한다: {goal}"] + [f"- In Scope 항목이 동작함을 확인한다: {s}" for s in in_scope])
        if in_scope
        else f"- Goal이 실제로 충족됨을 확인한다: {goal}"
    )
    risk_lines = _extract_marked_sentences(sentences, RISK_MARKERS, "식별된 Risk 없음")
    open_question_lines = _extract_marked_sentences(sentences, QUESTION_MARKERS, "식별된 Open Question 없음")
    reference_context = context_block if context_block else "(없음)"

    return (
        f"## Goal\n{goal}\n\n"
        f"## Description\n{narrative}\n\n"
        f"## In Scope\n{in_scope_lines}\n\n"
        f"## Out of Scope\n{out_of_scope_lines}\n\n"
        f"## Acceptance Criteria (Draft)\n{acceptance_lines}\n\n"
        f"## Risks\n{risk_lines}\n\n"
        f"## Open Questions\n{open_question_lines}\n\n"
        f"## Reference Context\n{reference_context}"
    )


def _slugify(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    if not words:
        return "generated_function"
    return "_".join(w.lower() for w in words)[:40]


def _extract_section(requirement: str, section: str) -> str:
    marker = f"## {section}\n"
    if marker not in requirement:
        return ""
    start = requirement.index(marker) + len(marker)
    end = requirement.find("\n\n## ", start)
    body = requirement[start:end if end != -1 else len(requirement)]
    return body.strip()


def _section_bullets(section_body: str) -> list:
    """섹션 본문에서 실제 내용이 있는 불릿 줄만 뽑아 문자열 리스트로
    반환한다. Requirement(`_analyze_requirement`, MVP-0005/0010)가 쓰는
    두 가지 placeholder 표기 관례를 모두 제외한다 — In/Out of
    Scope처럼 괄호로 감싼 것("- (감지된 ... 없음)")과, Risks/Open
    Questions처럼 괄호 없이 "없음"으로 끝나는 것("- 식별된 Risk
    없음")."""
    lines = [ln.strip() for ln in section_body.splitlines() if ln.strip().startswith("- ")]
    return [
        ln[2:].strip()
        for ln in lines
        if not ln.strip().startswith("- (") and not ln.strip().endswith("없음")
    ]


def _bullets_to_restated_lines(section_body: str, prefix: str, empty_note: str) -> str:
    real_lines = _section_bullets(section_body)
    if not real_lines:
        return f"- {empty_note}"
    return "\n".join(f"- {prefix}: {s}" for s in real_lines)


def _acceptance_to_interface_lines(acceptance_body: str, slug: str) -> str:
    """Requirement의 Acceptance Criteria(Draft) 각 항목을, Implementation이
    실제로 만들 수 있는 검증 Interface(함수 시그니처 하나씩)로 변환한다.
    Acceptance Criteria는 이미 "확인 가능한 조건" 형태의 문장이므로,
    그 문장 하나당 검증 함수 시그니처 하나를 규칙 기반으로 대응시킨다
    — 새 정보를 추정하지 않고 Requirement에 있는 문장만 재사용한다."""
    items = _section_bullets(acceptance_body)
    if not items:
        return "- (Acceptance Criteria가 없어 Interface를 도출할 수 없음)"
    return "\n".join(
        f"- `{slug}_check_{i}() -> bool`: {item}" for i, item in enumerate(items, start=1)
    )


def _design_from_requirement(payload: str) -> str:
    """Requirement Specification을 Architecture Draft(Component /
    Responsibility / Interfaces / Constraints / Open Questions /
    Reference Requirement)로 변환한다. Requirement 절(Goal/In Scope/
    Out of Scope/Acceptance Criteria/Risks/Open Questions)에서 실제
    내용을 뽑아 재구성하는 규칙 기반 구현이다 — ML/LLM 호출 없음.

    MVP-0005~0010까지 Design은 Requirement를 그대로 이어붙이거나
    (Reference Requirement 절), In/Out of Scope 문장만 재서술하는
    수준이었다("책임: {문장}", "제약: {문장}"). Open Questions는
    Requirement 내용과 무관하게 항상 동일한 고정 문장이었다.

    MVP-0011은 다음을 바꾼다:
    - Component: Requirement의 Goal(MVP-0010에서 Issue 문장 기반으로
      개선됨)을 그대로 인용해 이 Component가 구현해야 할 목표를
      명시한다 — 이전에는 "이 Issue의 기능을 구현할 단일 Component"
      처럼 Goal 내용과 무관한 고정 문구였다.
    - Interfaces(신규 절): Acceptance Criteria(Draft)의 각 문장을
      `{slug}_check_N() -> bool` 형태의 검증 함수 시그니처로
      대응시킨다 — Implementation이 실제로 구현할 수 있는 단위를
      제공한다.
    - Constraints: 기존 Out of Scope 기반 제약에, Requirement의
      Risks 절에서 뽑은 항목을 "회피" 제약으로 추가한다 — Risk도
      Implementation이 지켜야 할 제약이라는 관점에서 재분류한다.
    - Open Questions: Requirement의 Open Questions 절에 실제 항목이
      있으면 그것을 그대로 옮기고, 기존 고정 문장(Acceptance Criteria
      충족 여부 확인 필요)은 그 뒤에 계속 덧붙인다 — Requirement에
      Open Question이 없을 때만 고정 문장 하나만 남는다.
    """
    title, _, requirement = payload.partition("\n---REQUIREMENT---\n")
    slug = _slugify(title)

    goal_body = _extract_section(requirement, "Goal")
    in_scope_body = _extract_section(requirement, "In Scope")
    out_of_scope_body = _extract_section(requirement, "Out of Scope")
    acceptance_body = _extract_section(requirement, "Acceptance Criteria (Draft)")
    risks_body = _extract_section(requirement, "Risks")
    open_questions_body = _extract_section(requirement, "Open Questions")

    goal_text = goal_body if goal_body else f"'{title}' 기능을 추가한다."

    responsibility_lines = _bullets_to_restated_lines(
        in_scope_body, "책임", "Requirement에서 감지된 In Scope 항목이 없어 Responsibility를 도출할 수 없음"
    )
    interface_lines = _acceptance_to_interface_lines(acceptance_body, slug)
    out_of_scope_constraint_lines = _bullets_to_restated_lines(
        out_of_scope_body, "제약", "Requirement에서 감지된 Out of Scope 항목 없음"
    )
    risk_constraint_lines = _bullets_to_restated_lines(
        risks_body, "회피", "Requirement에서 식별된 Risk 없음"
    )
    constraint_lines = f"{out_of_scope_constraint_lines}\n{risk_constraint_lines}"

    requirement_open_questions = _section_bullets(open_questions_body)
    open_question_lines = "\n".join(f"- {q}" for q in requirement_open_questions)
    fixed_open_question = "- Acceptance Criteria 충족 여부는 Implementation/Validation Stage에서 별도로 확인이 필요하다."
    open_question_lines = f"{open_question_lines}\n{fixed_open_question}" if open_question_lines else fixed_open_question

    return (
        f"## Component\n`{slug}(*args, **kwargs)`를 다음 Goal을 구현할 "
        f"단일 Component로 제안한다: {goal_text}\n\n"
        f"## Responsibility\n{responsibility_lines}\n\n"
        f"## Interfaces\n{interface_lines}\n\n"
        f"## Constraints\n{constraint_lines}\n\n"
        f"## Open Questions\n{open_question_lines}\n\n"
        f"## Reference Requirement\n{requirement}"
    )


def _extract_slug(design_text: str) -> str:
    if "`" not in design_text:
        return "generated_function"
    start = design_text.index("`") + 1
    end = design_text.index("(", start)
    return design_text[start:end]


def _parse_interface_lines(interfaces_body: str) -> list:
    """Design의 `## Interfaces` 절(MVP-0011, "- `{sig}`: {설명}" 형태의
    불릿)을 (signature, description) 튜플 리스트로 분리한다. placeholder
    줄("- (Acceptance Criteria가 없어...)")은 backtick으로 시작하지
    않으므로 자연히 걸러진다."""
    entries = []
    for raw_line in interfaces_body.splitlines():
        line = raw_line.strip()
        if not line.startswith("- `"):
            continue
        content = line[2:]
        sig_part, sep, desc = content.partition(": ")
        if not sep:
            continue
        entries.append((sig_part.strip("`"), desc.strip()))
    return entries


def _extract_trailing_section(text: str, section: str) -> str:
    """`_extract_section`(Design/Planning Logic이 공유하는 헬퍼)과
    달리, 섹션 본문 자체가 중첩된 `## ...` 헤더를 포함할 수 있는
    경우에 쓴다 — `## Reference Requirement`(Design)와 `## Reference
    Context`(Requirement)는 각각 하위 문서 전체를 verbatim으로 품고
    있어, 그 하위 문서 자신의 첫 `## ` 경계에서 `_extract_section`이
    잘못 잘라낸다(실측으로 확인: Dependencies가 항상 비어 나왔다).
    이 두 절이 항상 자신을 담은 문서의 **마지막 절**이라는 관례
    (MVP-0005~0011)에 기대어, 마커 이후 끝까지를 그대로 반환한다.
    Implementation Logic 전용 헬퍼이며 `_extract_section`은 그대로
    둔다 — Design/Planning Logic이 그 함수를 계속 쓰기 때문이다."""
    marker = f"## {section}\n"
    if marker not in text:
        return ""
    return text[text.index(marker) + len(marker):].strip()


def _extract_dependencies(reference_context_body: str) -> list:
    """Requirement의 `## Reference Context` 절(Project Intelligence,
    MVP-0005)에서 `source_code`/`existing_workflow` 카테고리의 파일
    목록만 골라 Dependencies 후보로 쓴다 — 이 Issue를 다루면서 Project
    Intelligence가 이미 관련 있다고 규칙 기반으로 찾아낸 기존 코드
    파일들이므로, Implementation이 참고/의존할 가능성이 있는 대상이다.
    """
    deps = []
    for line in reference_context_body.splitlines():
        line = line.strip()
        if not (line.startswith("source_code:") or line.startswith("existing_workflow:")):
            continue
        _, _, files = line.partition(":")
        for f in files.split(","):
            f = f.strip()
            if f and f not in deps:
                deps.append(f)
    return deps


def _generate_code(design_text: str) -> str:
    """Architecture Draft(Design 산출물, MVP-0011)를 입력받아 코드를
    작성하지 않고 Implementation Specification(Target File / Public
    Interface / Functions / Classes / Dependencies / Algorithm Outline
    / Edge Cases / Validation Notes)을 생성한다. Design의 각 절과,
    Design이 `## Reference Requirement`로 그대로 품고 있는 Requirement
    (MVP-0011)의 각 절에서 실제 문장만 재사용하는 규칙 기반 구현이다
    — ML/LLM 호출 없음. Code Generation Engine이 실제 코드를 만들 때
    쓸 명세이며, 이 함수 자신은 실행 가능한 코드를 만들지 않는다.

    MVP-0005~0012까지 Implementation은 design_text 전체를 TODO
    docstring에 그대로 넣은 `raise NotImplementedError` 스텁 함수
    (사실상 Capability 부재)였다. MVP-0013은 이를 대체해 다음을
    생성한다:
    - Target File: slug 기반 파일 경로 제안.
    - Public Interface: Design Component의 함수 시그니처.
    - Functions: Public Interface 1개 + Design Interfaces 절의 각
      검증 함수(MVP-0011의 `{slug}_check_N`) — 모두 구현 대상으로
      나열한다.
    - Classes: 이 Design은 항상 단일 함수형 Component만 제안하므로
      (MVP-0011), 고정적으로 "필요 없음"을 명시한다.
    - Dependencies: Requirement의 Reference Context(Project
      Intelligence)에서 찾은 관련 기존 코드 파일.
    - Algorithm Outline: Design Responsibility 절의 각 항목을 순서
      있는 단계로 나열.
    - Edge Cases: Design Constraints 절(Out of Scope + Risk 회피,
      MVP-0011)의 각 항목.
    - Validation Notes: Design Open Questions 절(Requirement의 실제
      Open Question + 고정 확인 문구, MVP-0011)을 그대로 옮긴다.
    - Reference Design: Design 전체를 verbatim으로 마지막에 포함한다
      — MVP-0005부터 이어진 "Reference X" 관례(각 Stage가 자신의
      입력 전체를 참고용으로 보존)를 그대로 따른다.
    """
    slug = _extract_slug(design_text)

    component_body = _extract_section(design_text, "Component")
    responsibility_body = _extract_section(design_text, "Responsibility")
    interfaces_body = _extract_section(design_text, "Interfaces")
    constraints_body = _extract_section(design_text, "Constraints")
    open_questions_body = _extract_section(design_text, "Open Questions")
    reference_requirement = _extract_trailing_section(design_text, "Reference Requirement")
    reference_context_body = (
        _extract_trailing_section(reference_requirement, "Reference Context") if reference_requirement else ""
    )

    target_file = f"development-hq/mvp/generated/{slug}.py"
    public_interface = f"`def {slug}(*args, **kwargs)`"

    function_lines = [f"- `def {slug}(*args, **kwargs)` (Public Interface): {component_body if component_body else '(Component 설명 없음)'}"]
    for sig, desc in _parse_interface_lines(interfaces_body):
        function_lines.append(f"- `def {sig}`: {desc}")
    functions_lines = "\n".join(function_lines)

    classes_lines = "- (필요 없음: Design이 단일 함수형 Component만 제안했다)"

    dependencies = _extract_dependencies(reference_context_body)
    dependencies_lines = (
        "\n".join(f"- {d}" for d in dependencies)
        if dependencies
        else "- (Reference Context에서 식별된 의존 대상 없음)"
    )

    responsibility_items = _section_bullets(responsibility_body)
    algorithm_lines = (
        "\n".join(f"{i}. {item}" for i, item in enumerate(responsibility_items, start=1))
        if responsibility_items
        else "1. (Responsibility 항목이 없어 Algorithm Outline을 도출할 수 없음)"
    )

    constraint_items = _section_bullets(constraints_body)
    edge_case_lines = (
        "\n".join(f"- {item}" for item in constraint_items)
        if constraint_items
        else "- (Constraints에서 식별된 Edge Case 없음)"
    )

    open_question_items = _section_bullets(open_questions_body)
    validation_notes = (
        "\n".join(f"- {item}" for item in open_question_items)
        if open_question_items
        else "- (Open Questions 없음)"
    )

    return (
        f"## Target File\n{target_file}\n\n"
        f"## Public Interface\n{public_interface}\n\n"
        f"## Functions\n{functions_lines}\n\n"
        f"## Classes\n{classes_lines}\n\n"
        f"## Dependencies\n{dependencies_lines}\n\n"
        f"## Algorithm Outline\n{algorithm_lines}\n\n"
        f"## Edge Cases\n{edge_case_lines}\n\n"
        f"## Validation Notes\n{validation_notes}\n\n"
        f"## Reference Design\n{design_text}"
    )
