# MVP-0006 Observation: Project Intelligence를 Design Stage까지 전달

## 목적

MVP-0005가 만든 Project Intelligence(`collect_relevant_context`)를 새
Capability로 만들지 않고, Planning Stage뿐 아니라 Design Stage까지
전달했을 때 실제로 재사용되는지만 관찰한다. 판단은 하지 않는다.

## 변경 파일

- `development-hq/mvp/workflow_project_intelligence.py` (수정) —
  기존 `run_issue_to_planning(issue)`는 그대로 두고,
  `run_issue_to_design(issue) -> dict`를 추가했다.
  `collect_relevant_context(issue)`를 **한 번만** 호출해 얻은 Context를
  `_enrich_issue()`로 Issue에 덧붙인 뒤, 그 동일한 Context가 담긴
  Issue/requirement를 Planning(`requirements_agent_requirement_analysis`)
  과 Design(`design_agent_design`) 양쪽에 순서대로 전달한다.
- `development-hq/mvp/project_intelligence.py`, `agents.py`,
  `engine.py`, `workflow.py`, `workflow_0002.py`,
  `workflow_hello_sdlc.py`는 **수정하지 않았다**. `collect_relevant_context`
  는 여전히 일반 함수이며, 어떤 Capability-Agent 매핑에도 등록하지
  않았다. Task Dispatcher, Runtime, Pipeline, Stage Runner는 구현하지
  않았다.

## 관찰 결과

### Project Intelligence가 Planning과 Design 모두에서 실제로 재사용되는가?

**예, 단 경로가 예상과 달랐다.** `{"title": "Task Dispatcher", ...}` Issue로
`run_issue_to_design()`을 실행해 확인했다.

- `collect_relevant_context()`는 정확히 1회만 호출되고, 그 반환값(`context`)
  이 Planning 호출과 Design 호출에 동일하게 재사용된다 (`context` 객체
  자체를 두 번 만들지 않음).
- 하지만 `design_agent_design(issue, requirement)`은 인자로 받은
  `issue`의 `title`만 사용하고 `description`은 전혀 읽지 않는다
  (`development-hq/mvp/agents.py:47-50`). 따라서 Context를 덧붙인
  `enriched_issue`를 Design에 그대로 넘겨도, Context가 Design 출력에
  도달하는 유일한 경로는 **Design 함수 인자가 아니라, 이미 Context가
  섞여 들어간 `requirement` 문자열을 통해서**였다.
- 직접 검증: 동일한 `requirement`(Context 포함)를 고정한 채
  `design_agent_design(enriched_issue, requirement)`과
  `design_agent_design(issue, requirement)`(원본 Issue)를 각각 호출해
  비교한 결과, 두 출력이 **완전히 동일**했다. 즉 이번 구현에서
  `enriched_issue`를 Design에 넘긴 부분은 현재 `design_agent_design`
  구현상 아무 영향이 없었고, 재사용이 실제로 관찰된 지점은
  "Planning 결과(`requirement`)에 스며든 Context가 Design 입력으로
  다시 흘러들어가는 것"이었다.

### 두 Stage에서 같은 Context가 확인되는가?

**예.** 출력 텍스트를 직접 확인했다 — `run_issue_to_design()`이 반환한
`planning`과 `design` 문자열 양쪽 모두에 동일한
`[Relevant Context]` 절(source_code, existing_workflow, mvp_documents,
obs_documents, rfc_documents, adc_documents, adr_documents, rt_documents
8개 카테고리 목록)이 그대로 나타났다. `design` 쪽 텍스트는
`design_agent_design`이 `requirement` 문자열 전체를 그대로 에코하는
현재 `engine.py` 구현 방식 때문에 포함된 것이다.

무관한 Issue(`"reverse string"`)로도 동일하게 실행해, 두 Issue가 서로
다른 Context 목록을 Planning/Design 양쪽에서 일관되게 유지한 채
반환하는 것을 확인했다 (MVP-0005에서 관찰한 카테고리별 차이가 Design
출력까지 그대로 이어짐).

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability 추가. `run_issue_to_design`은 `AGENT_CAPABILITY_MAP`,
  `HELLO_SDLC_CAPABILITY_MAP` 어디에도 항목을 추가하지 않았다.
- `design_agent_design`의 시그니처나 `issue['description']`을 읽도록
  하는 수정. 관찰 중 발견한 사실(Design이 Issue의 description을 읽지
  않는다는 것)은 기록만 하고 고치지 않았다 — 이는 MVP-0004에서 만든
  기존 코드의 동작이며, 이번 MVP 범위(Context 전달 관찰)를 벗어난다.
- Task Dispatcher, Runtime, Pipeline, Stage Runner 구현.
- Implementation/Validation Stage로의 Context 전달. 이번 범위는
  Planning과 Design까지다.
- Capability 승격 여부 판단. Context가 Design까지 도달한다는 사실이
  `collect_relevant_context`를 Capability로 등록해야 하는 근거가
  되는지는 이 문서가 판단하지 않는다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음.
- `run_issue_to_design()`을 서로 다른 2개 Issue(Task Dispatcher 관련,
  무관한 reverse string)에 대해 수동 실행해 `context`가 1회만
  수집되고 Planning/Design 양쪽 출력에 동일하게 나타남을 확인했다.
  또한 `enriched_issue`를 Design에 넘긴 경우와 원본 `issue`를 넘긴
  경우의 Design 출력이 동일함을 별도로 확인했다(위 관찰 결과 참조).
  별도 자동화 테스트는 추가하지 않았다.
