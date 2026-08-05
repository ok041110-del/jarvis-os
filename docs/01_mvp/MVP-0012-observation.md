# MVP-0012 Observation: Validation Capability를 Stage-Aware Validation으로 개선한다

## 목적

이번 MVP의 범위는 **Validation Capability 하나**뿐이다. 새
Capability/Engine/Architecture를 만들지 않는다.
`development-hq/mvp/engine.py`의 Validation Logic
(`_review_code`/`_suggest_tests`와 그 내부 헬퍼)만 수정한다.
`Development HQ Constitution v1.0`의 Capability Engineering
Process(Baseline 저장 → Logic Improvement → Dogfooding → Before/After
비교 → Regression 확인 → Observation 작성)를 그대로 따랐다.

MVP-0005~0011까지 Validation은 입력을 "코드처럼 보이는가"(`_looks_like_code`,
`def `/`class `/`import `/`from ` 라인 존재 여부)로만 2-way 분류했다 —
코드가 아니면 전부 Design(Architecture Draft)으로 취급했다. Requirement
Specification도 코드가 아니므로 이 2-way 분류에서는 Design으로
오분류되어, "'## Component' 섹션이 없습니다" 같은 실제로는 틀린
지적(False Positive)을 냈다. 이번 MVP는 Requirement/Design(Architecture
Draft)/Code 3-way로 판단을 넓혀 각 Stage에 맞는 규칙만 적용한다.

## 변경 파일

- `development-hq/mvp/engine.py` — Validation Logic만 수정.
  - `_detect_artifact_stage(text) -> "code"|"design"|"requirement"|"unknown"`
    (신규) — 코드 판정(`_looks_like_code`, 기존 로직 그대로 재사용)을
    가장 먼저 하고, 그다음 Design 전용 마커(`_looks_like_design`:
    `## Interfaces` 또는 `## Reference Requirement` 존재), 그다음
    Requirement 전용 마커(`_looks_like_requirement`: `## Goal`과
    `## In Scope` 동시 존재)로 판단한다. 코드 판정을 가장 먼저 하는
    이유는 Implementation 산출물(진짜 Python 코드)의 docstring 안에
    Design 텍스트가, 그 안에 다시 Requirement 텍스트가 verbatim으로
    중첩되어 있기 때문이다(MVP-0007/0008에서 관찰된 Artifact 누적).
  - `_review_requirement(text)` / `_suggest_requirement_checks(text)`
    (신규) — Requirement 전용 섹션 존재 검사(`REQUIREMENT_REQUIRED_SECTIONS`
    = Goal/In Scope/Out of Scope/Acceptance Criteria (Draft)/Risks/
    Open Questions 6개)와 Requirement 구조 기반 검증 항목 제안.
  - `_review_design`/`_suggest_design_checks`(기존 함수, 로직 구조는
    유지) — `DESIGN_REQUIRED_SECTIONS`에 MVP-0011이 추가한 헤더
    (`## Interfaces`, `## Open Questions`, `## Reference Requirement`)를
    반영해 6개로 확장했고, `_suggest_design_checks`에 Interfaces 관련
    검증 항목 1건을 추가했다.
  - `_review_python_code(code)`(신규 이름, 로직은 기존 `_review_code`의
    Python 규칙 그대로) — bare except/TODO/docstring/line length/
    mutable default 5개 규칙을 **한 글자도 바꾸지 않고** 그대로
    옮겼다.
  - `_review_code(code)`/`_suggest_tests(payload)` — 이제 각각
    `_detect_artifact_stage()`로 판단한 뒤 해당 Stage 전용 함수로
    위임하는 dispatcher가 되었다. Stage를 판단할 수 없는 경우
    (`unknown`)는 MVP-0005~0011까지의 기존 fallback(Design 규칙 적용)을
    그대로 유지해 이전 동작과의 호환을 보존했다.
- 다른 파일은 수정하지 않았다. `agents.py`(Capability 시그니처와
  `CODE_REVIEW:`/`TEST_EXECUTION:` prefix 라우팅), Planning
  Logic(`_analyze_requirement`), Design Logic(`_design_from_requirement`),
  Project Intelligence, Context Bundle, 모든 `workflow*.py`는 그대로다.

## Validation Logic 변경 내용

| 구분 | Before | After |
|---|---|---|
| 판단 방식 | 코드 vs "코드가 아니면 Design" (2-way) | 코드 → Design → Requirement → unknown (3-way + fallback) |
| Requirement 입력 | Design 규칙 적용(오분류) | Requirement 전용 규칙 적용 |
| Design 입력 | Design 규칙 적용 | Design 규칙 적용(헤더 목록만 6개로 확장) |
| Code 입력 | Python 규칙 적용 | Python 규칙 적용(로직 무변경) |

## Dogfooding 결과

`development-hq/mvp/workflow_0008.REAL_ISSUE`(이 저장소 자신의 실제
Issue)로 `run_pipeline()`을 실행해 얻은 세 실제 Artifact —
Requirement(`planning`), Architecture Draft(`design`),
Implementation(`implementation`, 실제 Python 코드) — 각각에
`backend_agent_code_review()`/`qa_agent_test_execution()`을 직접
호출해 Before(변경 전 engine.py)/After(변경 후)를 비교했다. Workflow는
수정 대상이 아니므로 파이프라인 자체가 아니라, 파이프라인이 생성한
세 실제 Artifact를 Validation 함수에 개별적으로 통과시키는 방식으로
검증했다. 무관한 toy Issue(`"reverse string"`)로도 동일하게
Requirement/Design 재현을 확인했다.

### Before/After 비교

**Requirement 입력 (`planning`)**

- Before(`code_review`): `- '## Component' 섹션이 없습니다...` /
  `- '## Responsibility' 섹션이 없습니다...` / `- '## Constraints'
  섹션이 없습니다...` — **3건 모두 False Positive**(Requirement에는
  애초에 그 섹션들이 있을 이유가 없다).
- After(`code_review`): `- Requirement Specification에 필수
  섹션(Goal/In Scope/Out of Scope/Acceptance Criteria/Risks/Open
  Questions)이 모두 포함되어 있습니다.` — **False Positive 3건 → 0건**.
- Before(`test_execution`): `- Architecture 초안에서 검증 가능한
  섹션(Responsibility/Constraints)을 찾지 못해 기본 검증 항목을 생성할
  수 없음` — Requirement에 실제로 있는 Acceptance Criteria/Risks를
  전혀 활용하지 못한 기본 fallback 문구.
- After(`test_execution`): `- Acceptance Criteria(Draft)에 나열된 각
  항목이 실제로 검증 가능한 조건인지 확인` / `- Risks에 나열된 각
  항목이 Design/Implementation 단계에서 실제로 완화되는지 확인` —
  Requirement에 실제 있는 내용을 반영한 검증 항목 2건 생성.

**Design 입력 (`design`)**

- Before(`code_review`): `- Architecture 초안에 필수 섹션
  (Component/Responsibility/Constraints)이 모두 포함되어 있습니다.`
  (당시 3개 섹션 기준으로는 정상 판정 — MVP-0011로 Interfaces/Open
  Questions/Reference Requirement가 추가됐지만 Validation은 여전히
  옛 3개 섹션만 확인하고 있었다.)
- After(`code_review`): `- Architecture Draft에 필수 섹션
  (Component/Responsibility/Interfaces/Constraints/Open
  Questions/Reference Requirement)이 모두 포함되어 있습니다.` — 여전히
  모두 포함된 정상 판정이지만, 이제 MVP-0011이 실제로 추가한 6개
  섹션을 다 확인한다.
- Before/After(`test_execution`): 기존 2건(Responsibility/Constraints)에
  Interfaces 관련 검증 항목 1건이 추가되어 3건이 되었다.

**Code 입력 (`implementation`)**

- Before/After `code_review`, `test_execution` 모두 **완전히 동일**
  (`diff` 결과 바이트 단위 일치) — Python 규칙은 로직을 한 글자도
  바꾸지 않았고, 이 payload는 `_looks_like_code()`가 가장 먼저
  "code"로 판정하므로 Stage 판단 순서 변경의 영향을 받지 않는다.

## Regression 확인

- **Planning 유지**: `run_pipeline(REAL_ISSUE)`의 `planning` 값이
  변경 전/후 완전히 동일(`diff` 일치) — Planning Logic을 건드리지
  않았으므로 예상된 결과다.
- **Design 유지**: 같은 방식으로 `design` 값도 완전히 동일.
- **Artifact Flow 유지**: `requirement in design`, `design in
  implementation` 모두 여전히 `True` — MVP-0007부터 이어진 verbatim
  이어붙이기 동작은 이번 MVP의 대상이 아니며 그대로 유지된다.
- **파이프라인의 실제 Validation 결과 유지**: `run_pipeline()`이 항상
  호출해 온 `implementation`(Code) 대상 `code_review`/`test_execution`
  결과가 변경 전/후 완전히 동일 — 기존 워크플로우가 실제로 겪던
  결과에는 회귀가 없다. (MVP-0012는 Workflow가 아직 Requirement/
  Design을 Validation에 직접 통과시키지 않으므로, False Positive
  개선은 이번 Dogfooding처럼 Validation 함수를 직접 호출했을 때
  드러난다 — "범위 밖" 참고.)
- **기존 테스트**: `development-hq/mvp/tests/test_mvp_0001.py` 3건
  모두 통과 — 회귀 없음.
- RFC/ADC/ADR/RT는 생성하거나 수정하지 않았다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability, Engine, Architecture 추가. Planning/Design/Project
  Intelligence/Context Bundle/Workflow/Runtime/Pipeline/Task
  Dispatcher/Stage Runner/Capability Catalog 수정.
- Workflow가 Requirement나 Design을 Validation에 직접 통과시키도록
  바꾸는 것 — 현재 모든 `workflow*.py`의 `run_pipeline`류 함수는
  여전히 `implementation`(Code)만 `code_review`/`test_execution`에
  전달한다. 이번 MVP는 Validation 함수 자체가 Requirement/Design을
  받았을 때 올바르게 판단하는지만 개선했다.
- Implementation 산출물의 docstring에 누적된 Context/Artifact
  텍스트로 인한 line-length finding 증가 현상(MVP-0008/0011에서 이미
  관찰) 완화 — 이번 MVP 범위 밖이며, Code로 판정된 입력에는 여전히
  기존 Python 규칙이 그대로 적용된다.
- `_detect_artifact_stage`가 `unknown`으로 판단하는 경우(Goal/In
  Scope도 없고 Interfaces/Reference Requirement도 없는 임의 텍스트)에
  대한 별도 처리 — 기존 fallback(Design 규칙)을 그대로 유지했다.
