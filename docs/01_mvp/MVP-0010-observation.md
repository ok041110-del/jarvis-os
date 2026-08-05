# MVP-0010 Observation: Planning Logic을 템플릿 채우기에서 Issue 분석 기반으로 발전시킨다

## 목적

이번 MVP의 대상은 Project Intelligence가 아니라 **Planning Logic**이다.
새 Capability는 추가하지 않는다 — 기존 Planning Capability
(`requirements_agent_requirement_analysis` → `engine.py`
`_analyze_requirement`) 하나의 내부 로직만 바꾼다. MVP-0005~0009까지
Goal은 항상 `'{title}' 기능을 추가한다`는 고정 템플릿이었고, Acceptance
Criteria는 In Scope 문장을 그대로 재서술하는 것에 그쳤으며, Risk나
Open Question을 뽑아내는 절 자체가 없었다. 이번 MVP는 Goal 추출/Scope
추출/Acceptance Criteria 생성/Risk 식별/Open Question 생성 5개를
최소 목표로 구현하고, Planning 결과가 실제로 달라지는지 Dogfooding으로
검증한다. Context Bundle(MVP-0009)은 그대로 사용한다. Architecture
판단은 하지 않는다.

## 변경 파일

- `development-hq/mvp/engine.py` — `_analyze_requirement()` 내부
  로직만 수정.
  - `GOAL_MARKERS`, `RISK_MARKERS`, `QUESTION_MARKERS` 3개 리터럴
    튜플 추가. 여전히 문자열 마커 매칭만 사용하는 규칙 기반 구현이다
    — ML/LLM 호출 없음. 세 마커 집합은 서로 배타적이지 않게 설계했다
    (아래 "관찰 결과"에서 실측으로 확인).
  - `_extract_goal(sentences, title)` 추가 — `GOAL_MARKERS`가 포함된
    첫 문장을 Goal로 쓰고, 없으면 기존 고정 템플릿(`'{title}' 기능을
    추가한다`)으로 되돌아간다.
  - `_extract_marked_sentences(sentences, markers, empty_note)` 추가
    — Risk/Open Question 절 생성에 공통으로 재사용(`RISK_MARKERS`,
    `QUESTION_MARKERS`로 각각 호출).
  - Acceptance Criteria 절이 In Scope 문장 재서술 1줄씩("확인: {s}")
    이었던 것을, "Goal이 실제로 충족됨을 확인한다: {goal}" 1줄 +
    In Scope 항목별 확인 문장으로 바꿨다 — Goal이 바뀌었으므로
    Acceptance Criteria의 첫 줄도 이제 Goal을 반영한다.
  - 반환 텍스트에 `## Risks`, `## Open Questions` 2개 절을
    `## Acceptance Criteria (Draft)`와 `## Reference Context` 사이에
    추가했다.
- 다른 파일은 수정하지 않았다. `agents.py`(Capability 시그니처),
  `project_intelligence.py`(Context Bundle, MVP-0009),
  `design_agent_design`을 포함한 Design/Implementation/Validation
  Capability 로직, 모든 `workflow*.py`는 그대로다. 새 Capability,
  Runtime, Task Dispatcher, Stage Runner, Pipeline Runner는 추가하지
  않았다.

## Dogfooding 방법

같은 두 Issue를 변경 전(`git show HEAD:development-hq/mvp/engine.py`로
로드한 이전 버전)과 변경 후 코드로 각각 `_analyze_requirement()`에
직접 통과시켜 텍스트를 그대로 비교했다 — 이 저장소 자신의 실제 Issue와
기존 MVP들이 써온 무관한 Issue 둘 다로 검증했다.

1. MVP-0008/0009가 사용한 실제 Issue(`workflow_0008.REAL_ISSUE`,
   "Project Intelligence 개선").
2. MVP-0004~0007이 반복 사용한 무관한 toy Issue(`{"title": "reverse
   string", "description": "문자열을 뒤집는 함수를 추가해 달라"}`).

## 관찰 결과 (사실만 기록)

### 실제 Issue("Project Intelligence 개선")

- **Goal이 실제로 달라졌다.** 이전: `'Project Intelligence 개선' 기능을
  추가한다.`(고정 템플릿, title만 사용). 이후:
  `Project Intelligence(collect_relevant_context)가 이 문제를 완화할 수
  있는 방향으로 개선될 수 있는지 검토가 필요하다.`(narrative의 세
  번째 문장, `GOAL_MARKERS`의 "검토가 필요"가 매치되어 추출됨) — Issue
  본문이 실제로 요청한 내용이 Goal에 반영되었다.
- **Risks 절이 2건을 식별했다.** "그 결과 Project Intelligence가
  Planning에서만 수집한 Relevant Context가 Design과 Implementation
  산출물에도 의도치 않게 그대로 나타난다"(`의도치 않게` 매치)와,
  Goal과 동일한 문장(`문제` 매치) — 두 마커 집합이 배타적이지 않다는
  설계가 실제로 한 문장을 Goal이자 Risk로 이중 추출하는 것으로
  확인되었다.
- **Open Questions 절이 1건을 식별했다.** Goal과 동일한 문장(`검토가
  필요` 매치) — 이 Issue에서는 Goal Marker와 Open Question Marker가
  같은 마커("검토가 필요")를 공유해 Goal과 Open Question이 완전히
  동일한 문장으로 나타났다.
- **Acceptance Criteria 줄 수가 3줄에서 4줄로 늘었다.** 이전에는
  In Scope 문장 3개를 "확인: {문장}"으로 재서술한 3줄. 이후에는
  "Goal이 실제로 충족됨을 확인한다: {새 Goal 문장}" 1줄이 앞에
  추가되고, 나머지 3줄은 문구만 "In Scope 항목이 동작함을 확인한다:
  {문장}"으로 바뀐 채 그대로 유지됐다(내용 자체는 In Scope와 동일).
- **In Scope/Out of Scope/Description/Reference Context는 완전히
  동일했다.** 이 4개 절은 `OUT_OF_SCOPE_MARKERS`와 문장 분리 로직을
  그대로 재사용했으므로 변경 전후 텍스트가 문자 단위로 일치한다
  (직접 diff로 확인).
- 전체 길이는 1,222자(변경 전, `[Relevant Context]` 없이 실행한
  경우)에서 새 Risks/Open Questions 절과 늘어난 Goal/Acceptance
  Criteria 텍스트를 포함해 증가했다.

### 무관한 toy Issue("reverse string")

- **Goal이 동일했다.** `GOAL_MARKERS`에 매치되는 문장이 narrative에
  없어(`"문자열을 뒤집는 함수를 추가해 달라"`에는 "필요하다"/"해야
  한다"/"검토가 필요"/"확인이 필요" 중 어느 것도 없음)
  `_extract_goal()`이 기존 고정 템플릿(`'reverse string' 기능을
  추가한다.`)으로 정확히 되돌아갔다 — 변경 전후 Goal 텍스트가
  문자 단위로 일치했다.
- **Risks/Open Questions 모두 "식별된 ... 없음"으로 비었다** — 이
  narrative에 `RISK_MARKERS`/`QUESTION_MARKERS` 중 어느 것도 없기
  때문이다.
- 즉, Goal/Risk/Open Question을 나타내는 명시적 문장이 없는 Issue에
  대해서는 새 로직이 이전과 실질적으로 동일한 Planning 결과(빈 절
  추가 외 차이 없음)를 냈다 — 이번 개선이 모든 Issue에 균등하게
  적용되는 것이 아니라, Issue 문장에 마커가 실제로 있어야만 효과가
  나타난다는 사실을 실측으로 확인했다.

### Design Stage로의 영향

- `design_agent_design`은 수정하지 않았고, `_extract_section()`은
  `"## In Scope\n"`/`"## Out of Scope\n"` 마커만 찾으므로 그 사이에
  새 절(Risks/Open Questions)이 추가되어도 영향을 받지 않는다 —
  실제 Issue로 `run_pipeline()`을 실행해 Design 산출물의
  `## Responsibility`/`## Constraints` 내용이 In/Out Scope 텍스트와
  여전히 정확히 일치함을 확인했다(회귀 없음).

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability, Runtime, Task Dispatcher, Stage Runner, Pipeline
  Runner 추가.
- Design/Implementation/Validation Capability의 내부 로직 수정.
- Context Bundle(MVP-0009, `build_context_bundle()`)의 수정 — 그대로
  재사용했다.
- Goal/Risk/Open Question 추출 마커를 일반화된 NLP나 분류기로
  발전시키는 것. 여전히 리터럴 튜플과 부분 문자열 매칭뿐이다.
- Goal Marker와 Open Question Marker가 겹치는 것("검토가 필요"가 두
  집합 모두에 있음)이 바람직한지 판단. 실제로 한 문장이 Goal이자
  Open Question으로 중복 추출되는 사례를 관찰만 하고 기록했다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음(이 테스트는 `code_review`/`test_execution`만
  다루며 `requirement_analysis`를 호출하지 않는다).
- `_analyze_requirement()`를 변경 전(`git show HEAD:...`) 버전과 변경
  후 버전으로 각각 직접 호출해 실제 Issue 1건 + toy Issue 1건의 출력
  텍스트를 비교하는 방식으로 Dogfooding을 수행했다. 별도 자동화
  테스트는 추가하지 않았다.
