"""단일 Engine 호출 함수.

IMPLEMENTATION_RULES.md: "Engine Gateway(Port/Adapter 추상화) 구현 금지 —
단일 함수로 Engine을 호출하는 것으로 충분하다." 이 파일은 그 단일 함수만 가진다.
여러 Engine 중 선택하는 로직(Engine Routing)은 두지 않는다.

Kernel Extraction Candidate: 이 함수가 실제 LLM Engine 호출로 교체되거나,
Task 종류에 따라 다른 Engine을 골라야 하는 필요가 생기면 그것이
Engine Gateway(Port/Adapter) 추출 신호다. RFC 없이 여기서 분기를 늘리지 않는다.
"""

import re


def call_engine(prompt: str) -> str:
    """단일 Engine 호출 지점. 지금은 규칙 기반 응답을 반환한다."""
    return _rule_based_response(prompt)


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


DESIGN_REQUIRED_SECTIONS = ("## Component", "## Responsibility", "## Constraints")


def _looks_like_code(text: str) -> bool:
    return bool(re.search(r"^\s*(def |class |import |from )", text, re.MULTILINE))


def _review_design(design_text: str) -> str:
    """Design 산출물(Architecture 초안)을 코드가 아닌 문서로 인식하고,
    필수 섹션(Component/Responsibility/Constraints) 존재 여부만 규칙
    기반으로 확인한다. `_review_code`의 Python 코드 전용 규칙(bare
    except, docstring, mutable default 등)은 적용하지 않는다 — 그
    규칙들은 Design 문서에 의미가 없기 때문이다.
    """
    findings = [
        f"'{section}' 섹션이 없습니다. Architecture 초안에 포함되어야 합니다."
        for section in DESIGN_REQUIRED_SECTIONS
        if section not in design_text
    ]
    if not findings:
        findings.append("Architecture 초안에 필수 섹션(Component/Responsibility/Constraints)이 모두 포함되어 있습니다.")
    return "\n".join(f"- {f}" for f in findings)


def _suggest_design_checks(design_text: str) -> str:
    """Design 산출물에 대해 Python 코드 전용 테스트 케이스(함수 단위
    정상/경계값 검증) 대신, Design 문서 구조에서 실제로 도출 가능한
    검증 항목만 규칙 기반으로 제시한다."""
    cases = []
    if "## Responsibility" in design_text:
        cases.append("Responsibility에 나열된 각 항목이 Requirement의 In Scope와 실제로 일치하는지 확인")
    if "## Constraints" in design_text:
        cases.append("Constraints에 나열된 각 항목이 Implementation 단계에서 실제로 지켜지는지 확인")
    if not cases:
        cases.append("Architecture 초안에서 검증 가능한 섹션(Responsibility/Constraints)을 찾지 못해 기본 검증 항목을 생성할 수 없음")
    return "\n".join(f"- {c}" for c in cases)


def _review_code(code: str) -> str:
    if not _looks_like_code(code):
        return _review_design(code)

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

    if not _looks_like_code(code):
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


def _split_sentences(text: str) -> list:
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", text)]
    return [s for s in sentences if s]


def _analyze_requirement(payload: str) -> str:
    """Issue(title|||description)를 Requirement Specification(Goal /
    Description / In Scope / Out of Scope / Acceptance Criteria (Draft) /
    Reference Context)으로 정제한다. 문장 분리와 부정 표현(마커) 매칭만
    사용하는 규칙 기반 구현이다 — ML/LLM 호출 없음.

    Project Intelligence(`_enrich_issue`)가 덧붙인 `[Relevant Context]`
    블록은 문맥 문장으로 잘못 분류되지 않도록 별도 절(Reference Context)로
    분리한다 — 그 블록을 In/Out of Scope 분류 대상에서 제외한다.
    """
    title, _, description = payload.partition("|||")
    narrative, _, context_block = description.partition("[Relevant Context]")
    narrative = narrative.strip()
    context_block = context_block.strip()

    sentences = _split_sentences(narrative)
    in_scope = [s for s in sentences if not any(m in s for m in OUT_OF_SCOPE_MARKERS)]
    out_of_scope = [s for s in sentences if any(m in s for m in OUT_OF_SCOPE_MARKERS)]

    in_scope_lines = "\n".join(f"- {s}" for s in in_scope) if in_scope else "- (감지된 In Scope 문장 없음)"
    out_of_scope_lines = "\n".join(f"- {s}" for s in out_of_scope) if out_of_scope else "- (감지된 Out of Scope 문장 없음)"
    acceptance_lines = (
        "\n".join(f"- 확인: {s}" for s in in_scope)
        if in_scope
        else "- (In Scope 문장이 없어 Acceptance Criteria를 도출할 수 없음)"
    )
    reference_context = context_block if context_block else "(없음)"

    return (
        f"## Goal\n'{title}' 기능을 추가한다.\n\n"
        f"## Description\n{narrative}\n\n"
        f"## In Scope\n{in_scope_lines}\n\n"
        f"## Out of Scope\n{out_of_scope_lines}\n\n"
        f"## Acceptance Criteria (Draft)\n{acceptance_lines}\n\n"
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


def _bullets_to_restated_lines(section_body: str, prefix: str, empty_note: str) -> str:
    lines = [ln for ln in section_body.splitlines() if ln.strip().startswith("- ")]
    real_lines = [ln[2:].strip() for ln in lines if not ln.strip().startswith("- (")]
    if not real_lines:
        return f"- {empty_note}"
    return "\n".join(f"- {prefix}: {s}" for s in real_lines)


def _design_from_requirement(payload: str) -> str:
    """Requirement Specification을 Architecture 초안(Component /
    Responsibility / Constraints / Open Questions / Reference
    Requirement)으로 변환한다. Requirement의 In Scope/Out of Scope
    절을 그대로 재서술하는 규칙 기반 구현이다 — ML/LLM 호출 없음.
    """
    title, _, requirement = payload.partition("\n---REQUIREMENT---\n")
    slug = _slugify(title)

    in_scope_body = _extract_section(requirement, "In Scope")
    out_of_scope_body = _extract_section(requirement, "Out of Scope")

    responsibility_lines = _bullets_to_restated_lines(
        in_scope_body, "책임", "Requirement에서 감지된 In Scope 항목이 없어 Responsibility를 도출할 수 없음"
    )
    constraint_lines = _bullets_to_restated_lines(
        out_of_scope_body, "제약", "Requirement에서 감지된 Out of Scope 항목 없음"
    )

    return (
        f"## Component\n`{slug}(*args, **kwargs)`를 이 Issue의 기능을 구현할 "
        f"단일 Component로 제안한다.\n\n"
        f"## Responsibility\n{responsibility_lines}\n\n"
        f"## Constraints\n{constraint_lines}\n\n"
        f"## Open Questions\nAcceptance Criteria 충족 여부는 Implementation/"
        f"Validation Stage에서 별도로 확인이 필요하다.\n\n"
        f"## Reference Requirement\n{requirement}"
    )


def _extract_slug(design_text: str) -> str:
    if "`" not in design_text:
        return "generated_function"
    start = design_text.index("`") + 1
    end = design_text.index("(", start)
    return design_text[start:end]


def _generate_code(design_text: str) -> str:
    slug = _extract_slug(design_text)
    return (
        f'def {slug}(*args, **kwargs):\n'
        f'    """TODO: {design_text}"""\n'
        f'    raise NotImplementedError\n'
    )
