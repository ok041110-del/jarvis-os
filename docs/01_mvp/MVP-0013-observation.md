# MVP-0013 Observation: Implementation Capability를 Implementation Specification 생성 수준으로 구현한다

## 목적

이번 MVP의 범위는 **Implementation Capability 하나**뿐이다. 코드를
생성하는 것이 목표가 아니다. `development-hq/mvp/engine.py`의
Implementation Logic(`_generate_code`와 그 전용 헬퍼)만 수정한다.
`Development HQ Constitution v1.0`의 Capability Engineering
Process(Baseline 저장 → Logic Improvement → Dogfooding → Before/After
비교 → Regression 확인 → Observation 작성)를 그대로 따랐다.

MVP-0005~0012까지 Implementation Capability(`backend_agent_code_generation`)는
사실상 존재하지 않았다 — Design 전체를 TODO docstring에 그대로 넣고
`raise NotImplementedError`만 반환하는 스텁 함수를 만들 뿐이었다. 이번
MVP는 코드 대신 Code Generation Engine이 실제로 쓸 수 있는
Implementation Specification(Target File / Public Interface /
Functions / Classes / Dependencies / Algorithm Outline / Edge Cases /
Validation Notes)을 생성하도록 구현한다.

## 변경 파일

- `development-hq/mvp/engine.py` — Implementation Logic만 수정.
  - `_generate_code(design_text)` 전면 재작성. 더 이상
    `def {slug}(*args, **kwargs): raise NotImplementedError` 코드를
    반환하지 않는다. Design의 각 절(Component/Responsibility/
    Interfaces/Constraints/Open Questions/Reference Requirement,
    MVP-0011)과, Design이 품고 있는 Requirement(Reference Requirement)의
    Reference Context(Project Intelligence, MVP-0005) 절에서 실제
    문장만 뽑아 8개 항목의 Implementation Specification을 만든다.
  - `_parse_interface_lines(interfaces_body)`(신규) — Design의
    `## Interfaces` 절 각 불릿("- `{sig}`: {설명}")을 (signature,
    description) 튜플로 분리한다.
  - `_extract_dependencies(reference_context_body)`(신규) —
    Reference Context의 `source_code`/`existing_workflow` 카테고리
    파일 목록을 Dependencies 후보로 추출한다.
  - `_extract_trailing_section(text, section)`(신규, Implementation
    Logic 전용) — `## Reference Requirement`/`## Reference Context`처럼
    "하위 문서 전체를 verbatim으로 품은 절"을 추출하기 위한 헬퍼.
    기존 `_extract_section`(Design/Planning Logic이 계속 쓰는 공유
    헬퍼, 수정하지 않음)은 섹션 본문 안에 `\n\n## `가 나오면 거기서
    잘라버리므로, 중첩 문서를 통째로 품은 절에는 쓸 수 없다(아래
    "Dogfooding 결과"에서 실측으로 발견).
  - `_extract_slug(design_text)`는 그대로 재사용(수정 없음).
- 다른 파일은 수정하지 않았다. Planning Logic, Design Logic,
  Validation Logic, Project Intelligence, Context Bundle, 모든
  `workflow*.py`, `agents.py`(Capability 시그니처), Engine의
  `CODE_GENERATION:` prefix 라우팅은 그대로다.

## Implementation Logic 변경 내용

| 항목 | Before | After |
|---|---|---|
| 반환 형태 | 실행 가능한 Python 함수 문자열(`def ...: raise NotImplementedError`) | 8개 섹션의 Implementation Specification 문서 |
| Target File | 없음 | slug 기반 파일 경로 제안(`development-hq/mvp/generated/{slug}.py`) |
| Public Interface | Component 문구 안에 암묵적으로만 존재 | 별도 절로 명시 |
| Functions | 없음(스텁 함수 1개뿐) | Public Interface 1개 + Design Interfaces 절의 검증 함수 N개 |
| Classes | 없음 | 고정 값("필요 없음") — Design이 항상 단일 함수형 Component만 제안하므로 |
| Dependencies | 없음 | Reference Context의 source_code/existing_workflow 파일 목록 |
| Algorithm Outline | 없음 | Design Responsibility 절 항목을 순서 있는 단계로 나열 |
| Edge Cases | 없음 | Design Constraints 절(Out of Scope + Risk 회피) 항목 |
| Validation Notes | 없음 | Design Open Questions 절(Requirement 실제 Open Question + 고정 확인 문구) |
| Reference Design | Design 전체가 TODO docstring 안에 있었음(형태만 다름, 내용은 verbatim) | 별도 절로 Design 전체를 verbatim 포함(관례 유지) |

## Dogfooding 결과

`development-hq/mvp/workflow_0008.REAL_ISSUE`(이 저장소 자신의 실제
Issue)와 MVP-0004부터 반복 사용한 무관한 toy Issue(`"reverse
string"`)로 `run_pipeline()`을 실제 실행했다.

- **구현 중 실제 버그를 발견하고 수정했다.** 최초 구현은 Dependencies가
  실제 Issue에서도 항상 "(Reference Context에서 식별된 의존 대상
  없음)"으로 비어 나왔다. 원인을 추적한 결과, 공유 헬퍼
  `_extract_section()`은 섹션 본문 안에 `\n\n## `가 나타나면 그
  지점에서 잘라내도록 설계되어 있는데(Design/Planning의 flat 섹션에는
  맞는 동작), `## Reference Requirement`의 본문은 그 자체로 `## Goal`
  로 시작하는 중첩 문서 전체이므로, `_extract_section`이 중첩 문서의
  첫 `\n\n## Description` 경계에서 멈춰 `## Goal` 한 줄만 반환했다 —
  그 결과 안에 있는 `## Reference Context`는 애초에 추출되지 않았다.
  기존 `_extract_section`(Design/Planning Logic이 쓰는 공유 함수)은
  건드리지 않고, Implementation Logic 전용의 `_extract_trailing_section`을
  새로 만들어(마커 이후 끝까지 반환) 해결했다. 수정 후 재실행하자
  Dependencies에 실제 Issue의 Reference Context 파일 목록
  (`workflow_0008.py`, `engine.py`, `workflow_artifact_flow.py`,
  `workflow_project_intelligence.py`)이 정확히 나타났다.
- **실제 Issue의 Implementation Specification**: Target File
  `development-hq/mvp/generated/project_intelligence.py`, Functions
  5개(Public Interface 1 + Interface 검증 함수 4개, Design의
  `project_intelligence_check_1~4`와 정확히 대응), Algorithm Outline
  3단계(Responsibility 3개 항목), Edge Cases 2건(Risk 회피 항목),
  Validation Notes 2건(Requirement의 실제 Open Question + 고정 확인
  문구), Dependencies 4건.
- **toy Issue("reverse string")**: Functions 3개(Public Interface 1 +
  검증 함수 2개), Algorithm Outline 1단계, Edge Cases는
  "(Constraints에서 식별된 Edge Case 없음)"(이 Issue는 Out of
  Scope/Risk가 모두 없었으므로 예상된 결과), Dependencies 2건
  (`engine.py`, `project_intelligence.py`).
- **Artifact Flow**: `design in implementation`이 실제 실행으로
  여전히 `True` — Reference Design 절에 Design 전체를 verbatim
  포함하는 관례(MVP-0005부터 이어진 Reference X 관례)를 유지했다.

## Regression 확인

- **Planning 유지**: `run_pipeline(REAL_ISSUE)`의 `planning` 값이
  변경 전/후 완전히 동일(`diff` 일치).
- **Design 유지**: 같은 방식으로 `design` 값도 완전히 동일.
- **Validation Logic 유지**: `git diff`로 이번 변경이 `_extract_slug`
  이후(Implementation Logic 영역)에만 있음을 확인했다 — Validation
  함수(`_review_code`, `_review_design`, `_review_requirement`,
  `_review_python_code`, `_suggest_tests` 등, MVP-0012)는 한 줄도
  건드리지 않았다.
- **Validation 결과는 실제로 달라졌다 — 이는 예상된 결과다.**
  Implementation이 더 이상 코드를 생성하지 않으므로, 파이프라인이
  `code_review`/`test_execution`에 넘기는 `implementation` 값의
  성격 자체가 바뀌었다. 새 Implementation Specification 텍스트는
  `def `가 줄 시작에 오지 않아(`- \`def ...\`` 형태로 불릿 안에만
  등장) `_looks_like_code()`가 False를 반환하고, Reference Design
  절에 Design 전체가 중첩되어 있어 `## Interfaces`/`## Reference
  Requirement` 마커가 존재해 `_detect_artifact_stage()`(MVP-0012)가
  "design"으로 분류한다. 그 결과 실제 실행에서 `code_review`는 이제
  "Architecture Draft에 필수 섹션이 모두 포함되어 있습니다"를,
  `test_execution`은 Design 검증 항목 3건을 반환한다(이전에는 TODO
  주석 1건 + line-length 22건 + 코드 함수 기반 테스트 2건). 이 변화는
  Validation Logic이 바뀌어서가 아니라 입력 Artifact의 종류가
  근본적으로 바뀌었기 때문이다 — Validation Logic 자체(코드)는
  MVP-0012 그대로다.
- **기존 테스트**: `development-hq/mvp/tests/test_mvp_0001.py` 3건
  모두 통과 — 회귀 없음(이 테스트는 원시 코드 문자열을 직접
  `run_mvp_0001()`에 넣으며 `backend_agent_code_generation`을 거치지
  않는다).
- RFC/ADC/ADR/RT는 생성하거나 수정하지 않았다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability, Engine, Architecture, Code Generation Engine(실제
  코드를 생성하는 별도 엔진) 추가. Planning/Design/Validation/Project
  Intelligence/Context Bundle/Workflow/Runtime/Pipeline/Task
  Dispatcher/Stage Runner/Capability Catalog 수정.
- Workflow가 Implementation Specification을 Validation에 맞는
  방식으로 다르게 라우팅하도록 바꾸는 것 — `workflow_0008.py` 등은
  여전히 `implementation`을 그대로 `code_review`/`test_execution`에
  전달하며, 그 결과 이번 MVP가 만든 Implementation Specification이
  Validation에서 "design"으로 분류되는 것을 그대로 관찰만 했다(위
  "Regression 확인" 참고).
- Implementation Specification으로부터 실제 실행 가능한 코드를
  생성하는 별도 단계 — 이번 MVP는 "코드를 작성하지 않는다"는 요구를
  그대로 따랐다.
- Classes 절을 실제로 여러 Class로 분해하는 로직 — Design이 항상
  단일 함수형 Component만 제안하므로(MVP-0011), 이번 MVP에서는 고정
  문구로만 처리했다.
