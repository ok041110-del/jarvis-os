# MVP-0011 Observation: Design Capability를 Requirement 재서술에서 Architecture Draft 생성으로 발전시킨다

## 목적

이번 MVP의 범위는 **Design Capability 하나**뿐이다. 새 Architecture,
새 Capability, 새 Runtime/Pipeline/Task Dispatcher/Stage Runner를
만들지 않는다. `development-hq/mvp/engine.py`의 `_design_from_requirement`
(Design Logic) 내부만 수정한다. `Development HQ Constitution v1.0`의
Capability Engineering Process(Baseline 저장 → Logic Improvement →
Dogfooding → Before/After 비교 → Regression 확인 → Observation 작성)를
그대로 따랐다.

MVP-0005~0010까지 Design은 Requirement의 In/Out of Scope 문장을
"책임: {문장}" / "제약: {문장}" 형태로 재서술하고, Requirement 전체를
`## Reference Requirement` 절에 그대로 이어붙이는 수준이었다. Open
Questions는 Requirement 내용과 무관하게 항상 동일한 고정 문장이었다.
이번 MVP는 Design의 출력을 Component/Responsibility/Interfaces/
Constraints/Open Questions 5개 항목을 갖춘 Architecture Draft로
발전시킨다.

## 변경 파일

- `development-hq/mvp/engine.py` — `_design_from_requirement()`와 그
  내부에서만 쓰이는 헬퍼(`_bullets_to_restated_lines`,
  `_extract_section` 재사용, 신규 `_section_bullets`,
  `_acceptance_to_interface_lines`)만 수정. 다음은 수정하지 않았다:
  Planning Logic(`_analyze_requirement`, `_extract_goal`,
  `_extract_marked_sentences`, MVP-0010에서 만든 `GOAL_MARKERS`/
  `RISK_MARKERS`/`QUESTION_MARKERS`), Validation Logic(`_review_code`,
  `_review_design`, `_suggest_tests`, `_suggest_design_checks`,
  `DESIGN_REQUIRED_SECTIONS`), `project_intelligence.py`(Context
  Bundle, MVP-0009), 모든 `workflow*.py`, `agents.py`(Capability
  시그니처). `## Component`/`## Responsibility`/`## Constraints`
  헤더 문자열은 `DESIGN_REQUIRED_SECTIONS`(Validation Logic)가 그대로
  검사하므로 정확히 유지했다 — 새 헤더(`## Interfaces`)만 추가했다.
- 다른 파일은 변경하지 않았다.

## 개선 내용

1. **Component**: 이전에는 `` `{slug}(*args, **kwargs)`를 이 Issue의
   기능을 구현할 단일 Component로 제안한다 ``로 Goal 내용과 무관한
   고정 문구였다. 이제 Requirement의 `## Goal` 절(MVP-0010에서 Issue
   문장 기반으로 개선된 값)을 그대로 인용해, 이 Component가 무엇을
   구현해야 하는지 Goal 텍스트로 명시한다.
2. **Interfaces(신규 절)**: Requirement의 `## Acceptance Criteria
   (Draft)` 각 항목을 `` `{slug}_check_N() -> bool`: {항목} ``
   형태의 검증 함수 시그니처로 1:1 대응시킨다. 새 정보를 추정하지
   않고 Requirement에 이미 있는 문장만 재사용한다.
3. **Constraints**: 이전에는 Out of Scope 문장만 "제약: {문장}"으로
   재서술했다. 이제 Requirement의 `## Risks` 절(MVP-0010 신규)도
   "회피: {문장}" 형태로 추가해, Risk를 Implementation이 지켜야 할
   제약으로 재분류한다.
4. **Open Questions**: 이전에는 Requirement 내용과 무관하게 항상
   동일한 고정 문장 1개였다. 이제 Requirement의 `## Open Questions`
   절(MVP-0010 신규)에 실제 항목이 있으면 그것을 먼저 옮기고, 기존
   고정 문장을 그 뒤에 이어 붙인다.
5. Requirement의 두 placeholder 표기 관례(In/Out of Scope: `- (감지된
   ... 없음)`, Risks/Open Questions: `- 식별된 ... 없음`, 둘 다
   Planning Logic이 만드는 그대로이며 이번 MVP에서 수정하지 않음)를
   모두 "내용 없음"으로 인식하도록 `_section_bullets()`를 만들었다.
   최초 구현에서 괄호 없는 관례(Risks/Open Questions)를 실제 내용으로
   잘못 인식해 toy Issue의 Constraints에 "회피: 식별된 Risk
   없음"처럼 이중으로 어색한 문장이 생기는 것을 Dogfooding 중 실측으로
   발견하고, 두 관례를 모두 거르도록 수정했다(아래 "Dogfooding 결과"
   참고).

## Dogfooding 결과

`development-hq/mvp/workflow_0008.REAL_ISSUE`("Project Intelligence
개선", 이 저장소 자신의 실제 Issue)와, MVP-0004~0010이 반복 사용한
무관한 toy Issue(`"reverse string"`) 둘 다로 `run_pipeline()`을 실행해
Before/After Design 출력을 직접 비교했다.

- toy Issue의 Constraints에서 실제 오류를 하나 발견하고 수정했다:
  최초 구현은 Risks 절의 placeholder("- 식별된 Risk 없음")를
  실제 항목으로 오인해 Constraints에 "회피: 식별된 Risk 없음"이라는
  문장을 만들어냈다. `_section_bullets()`에 "없음으로 끝나는 줄도
  제외" 규칙을 추가한 뒤 재실행하자, toy Issue의 Constraints는
  "Requirement에서 감지된 Out of Scope 항목 없음" / "Requirement에서
  식별된 Risk 없음" 2줄로 정상화되었다.

### Before/After 비교 (실제 Issue, `REAL_ISSUE`)

| 항목 | Before | After |
|---|---|---|
| Component | "이 Issue의 기능을 구현할 단일 Component로 제안한다"(고정 문구) | "다음 Goal을 구현할 단일 Component로 제안한다: {실제 Goal 문장}" |
| Responsibility | 3줄("책임: {In Scope 문장}") | 3줄, 동일(변경 없음) |
| Interfaces | 없음(절 자체가 없었음) | 4줄 신규 — `project_intelligence_check_1..4() -> bool`, 각각 Acceptance Criteria 문장과 1:1 대응 |
| Constraints | 1줄("Requirement에서 감지된 Out of Scope 항목 없음") | 3줄 — 기존 1줄 + Risks에서 뽑은 "회피: {문장}" 2줄 |
| Open Questions | 고정 문장 1개 | 2줄 — Requirement의 실제 Open Question 1개 + 기존 고정 문장 |
| Reference Requirement | Requirement 전체 verbatim | 동일(변경 없음, 여전히 verbatim) |

### Before/After 비교 (toy Issue, `"reverse string"`)

| 항목 | Before | After |
|---|---|---|
| Component | 고정 문구 | "다음 Goal을 구현할 단일 Component로 제안한다: 'reverse string' 기능을 추가한다." |
| Responsibility | 1줄 | 1줄, 동일 |
| Interfaces | 없음 | 2줄 신규(`reverse_string_check_1`, `_check_2`) |
| Constraints | 1줄 | 2줄(Out of Scope 없음 + Risk 없음) |
| Open Questions | 고정 문장 1개 | 고정 문장 1개(이 Issue는 Requirement에 실제 Open Question이 없어 Before와 최종적으로 동일한 1줄) |

- **Implementation이 활용 가능한 정보가 실제로 늘었는가?** 두 Issue
  모두에서 Interfaces 절이 신규로 생겼다 — Before에는 Implementation이
  참고할 수 있는 함수 시그니처가 Component 하나(`{slug}(*args,
  **kwargs)`)뿐이었지만, After에는 Acceptance Criteria당 하나씩
  구체적인 검증 함수 시그니처(`{slug}_check_N() -> bool`)가 추가로
  생겼다. 실제 Issue에서는 Constraints/Open Questions도 Out of
  Scope/고정 문장 외의 실제 Requirement 내용(Risk 2건, Open Question
  1건)을 추가로 반영했다.

## Regression 확인

- **Planning 출력**: `run_pipeline(REAL_ISSUE)`의 `planning` 값을
  변경 전/후로 각각 저장해 `diff`했다 — **완전히 동일**(바이트 단위
  일치). Design Logic만 바꿨고 Planning Logic은 건드리지 않았으므로
  예상된 결과다.
- **Validation**: `code_review`의 finding 종류(TODO 주석 1건, N번째
  줄 100자 초과 다수)는 변경 전후 동일했다. 초과 줄의 **줄 번호와
  개수는 달라졌다**(16건 → 21건) — Design 출력이 길어져 `implementation`
  docstring에 더 많은 100자 초과 줄이 포함되었기 때문이다(MVP-0008에서
  이미 관찰된 "Context/Artifact 텍스트가 길어질수록 line-length
  finding이 늘어난다"는 현상의 재현). `test_execution` 출력(함수 이름
  기반 테스트 케이스 2건)은 변경 전후 완전히 동일했다.
  - `# 수정 금지` 대상인 Validation Logic 코드 자체(`_review_code`,
    `_suggest_tests` 등)는 수정하지 않았다 — 위 차이는 Validation이
    받는 입력(`implementation` 텍스트)이 길어진 결과이지 Validation
    로직 변경의 결과가 아니다.
- **Artifact Flow**: `requirement in design`과 `design in
  implementation`을 실제 실행으로 재확인 — 둘 다 여전히 `True`다.
  MVP-0007/0008이 관찰한 verbatim 이어붙이기 동작(`## Reference
  Requirement` 절에 Requirement 전체를 그대로 포함)이 이번 변경
  이후에도 유지된다.
- **기존 테스트**: `development-hq/mvp/tests/test_mvp_0001.py` 3건
  모두 통과 — 회귀 없음.
- RFC/ADC/ADR/RT는 생성하거나 수정하지 않았다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability, Runtime, Task Dispatcher, Stage Runner, Pipeline
  Runner, Engine, LLM/ML 추가.
- Planning Logic, Validation Logic, Project Intelligence, Context
  Bundle, Workflow, Capability Catalog, Engine Interface 수정.
- Design이 여러 Component로 분해하는 것(Component는 여전히 Issue당
  1개). Interfaces가 실제로 컴파일 가능한 코드인지 검증하는 것(여전히
  텍스트 형태의 함수 시그니처 제안일 뿐이다).
- `## Reference Requirement` 절(Requirement 전체 verbatim 포함,
  MVP-0005~0010부터 이어진 동작)을 요약하거나 제거하는 것 — 이번
  MVP는 Component/Responsibility/Interfaces/Constraints/Open
  Questions 5개 항목의 내용 개선만 다뤘다.
- Validation의 line-length finding이 늘어나는 현상(MVP-0008에서 이미
  관찰됨)을 완화하는 것 — 이번 MVP 범위 밖이며 Architecture 판단이
  필요한 사안이다.
