# MVP-0005 Observation: Project Intelligence

## 목적

Issue → Project Intelligence → Relevant Context → Planning으로 이어지는
최소 구현을 실행하고, 그 결과를 관찰한다. 판단은 하지 않는다.

## 변경 파일

- `development-hq/mvp/project_intelligence.py` (신규) —
  `collect_relevant_context(issue) -> dict`. Project 내 8개 카테고리
  (source_code, existing_workflow, mvp_documents, obs_documents,
  rfc_documents, adc_documents, adr_documents, rt_documents)와
  directory_structure 1개를 규칙 기반(키워드 겹침)으로 수집한다.
  Task Dispatcher, Runtime, Stage Runner, Pipeline Runner에 해당하는
  구조는 포함하지 않았다.
- `development-hq/mvp/workflow_project_intelligence.py` (신규) —
  `run_issue_to_planning(issue) -> dict`. Project Intelligence를 호출한
  뒤, 그 결과를 Issue의 `description`에 덧붙여 기존 Planning
  Capability(`requirements_agent_requirement_analysis`, MVP-0004)에
  그대로 전달하는 두 줄짜리 하드코딩된 순차 호출이다.
- 기존 파일(`agents.py`, `engine.py`, `workflow.py`, `workflow_0002.py`,
  `workflow_hello_sdlc.py`)은 **수정하지 않았다**. `agents.py`의
  `requirements_agent_requirement_analysis` 시그니처도 그대로다 — Context는
  기존 `issue["description"]` 필드에 문자열로 덧붙여 전달했다.

## 관찰 결과

### Issue → Project Intelligence → Relevant Context → Planning이 실제로 연결되는가?

**예.** `{"title": "Task Dispatcher", "description": "Task Dispatcher를
Runtime으로 승격해야 하는지 재검토하는 기능을 추가해 달라", "status":
"Open"}` 입력에 대해 `collect_relevant_context()`가 8개 카테고리 중
6개에서 실제로 파일을 찾아냈고, 그 결과가 `requirements_agent_requirement_analysis()`
가 반환한 Planning 텍스트의 `[Relevant Context]` 절에 그대로 포함된
것을 확인했다.

### 관련성 수집이 실제로 구분되는가?

**예.** 위 Task Dispatcher 관련 Issue와, 무관한 Issue(`"reverse
string"`, "문자열을 뒤집는 함수를 추가해 달라")를 각각 실행해 비교했다.

| 카테고리 | Task Dispatcher Issue | reverse string Issue |
|---|---|---|
| rfc_documents | RFC-0001, RFC-0002, RFC-0004 | RFC-0003, RFC-0004 |
| existing_workflow | 3건 | 0건 |
| obs_documents | 3건(OBS-0001, OBS-0002, OBS-TEMPLATE) | 0건 |
| adr_documents | ADR-0001 | 0건 |
| rt_documents | RT-0001 | 0건 |

두 Issue가 서로 다른 파일 집합을 반환했다 — 무관한 Issue에서는 여러
카테고리가 빈 리스트를 반환했다.

### 구현 중 실제로 발견하고 수정한 버그 (사실 기록)

최초 구현에서 키워드 추출을 `\w+` 정규식 하나로 처리했더니, "Task
Dispatcher를"처럼 한글 조사가 영문 단어에 그대로 붙어 `dispatcher를`
같은 하나의 토큰으로 추출되었다. 이 토큰은 조사 없이 쓰인 원문
(`RFC-0004-task-dispatcher-runtime-boundary.md` 등)과 매칭되지 않아,
가장 관련성이 높아야 할 RFC-0004가 처음에는 관련 문서 상위 3건에
포함되지 못했다. 라틴 문자 토큰과 한글 음절 토큰을 별도 정규식
(`[A-Za-z0-9_]+`, `[가-힣]+`)으로 분리 추출하도록 수정한 뒤, 동일 Issue
입력에서 RFC-0004가 관련 문서 목록에 포함되는 것을 확인했다. 이는
Architecture Decision이 아니라 이번에 새로 작성한 코드 자체의 결함
수정이었다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- Task Dispatcher, Runtime, Stage Runner, Pipeline Runner 구현
- 새로운 Capability 등록(예: `repository_analysis`를 `AGENT_CAPABILITY_MAP`
  이나 `HELLO_SDLC_CAPABILITY_MAP` 같은 리터럴 딕셔너리에 공식 추가하는
  것). `collect_relevant_context()`는 어떤 Capability-Agent 매핑에도
  등록되지 않은 일반 함수로만 구현했다.
- ML/임베딩/벡터 검색. 키워드 겹침 카운트만 사용했다.
- Jarvis OS 공통 계층으로의 일반화. 이 구현은
  `development-hq/mvp/` 안에서만 존재한다.
- `existing_workflow` 등 다른 카테고리와 매칭되는 Planning 이후
  Stage(Design/Implementation/Validation)로의 Context 전달. 이번
  범위는 Planning까지다.

## 관찰만 기록 — 판단하지 않음

`collect_relevant_context()`가 수행하는 일(Project 전체에서 Issue와
관련된 자료를 찾는 것)은 `development-hq/STRUCTURE.md`의 기존 7개
Capability(`code_generation`, `code_review`, `deployment`, `design`,
`incident_response`, `requirement_analysis`, `test_execution`) 중
어느 것과도 정확히 대응되지 않았다. 이 함수는 어떤 Capability로도
등록하지 않고 구현했다. 이 사실이 ADC-0003 판단 2(Capability Catalog
확장, Defer)를 재검토할 근거가 되는지는 이 문서가 판단하지 않는다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음.
- `run_issue_to_planning()`을 서로 다른 2개 Issue(Task Dispatcher 관련,
  무관한 reverse string)에 대해 수동 실행해 관련 자료 목록이 실제로
  달라짐을 확인했다. 별도 자동화 테스트는 추가하지 않았다.
