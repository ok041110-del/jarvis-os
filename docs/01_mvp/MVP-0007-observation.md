# MVP-0007 Observation: Artifact Flow (Planning -> Design -> Implementation)

## 목적

이번 MVP의 관찰 대상은 Project Intelligence가 아니라 **Artifact 전달
경로**다. Project Intelligence는 Planning에서만 사용하고, Planning
산출물(Requirement)이 Design으로, Design 산출물(Architecture)이
Implementation으로 어떻게 전달되는지를 관찰한다. 판단은 하지 않는다.

## 변경 파일

- `development-hq/mvp/workflow_artifact_flow.py` (신규) —
  `run_issue_to_implementation(issue) -> dict`. Issue를
  Planning(`requirements_agent_requirement_analysis`, PI 포함) ->
  Design(`design_agent_design`) -> Implementation
  (`backend_agent_code_generation`) 순서로 통과시키는 세 줄짜리
  하드코딩된 순차 호출이다. Project Intelligence(`collect_relevant_context`,
  MVP-0005/0006)는 Planning 호출 직전에 한 번만 사용했다 — Design에는
  Context가 섞이지 않은 **원본 Issue**를 그대로 넘겼다(MVP-0006에서
  Design에 넘겼던 `enriched_issue`가 아니라 `issue`를 그대로 사용).
  기존 `_enrich_issue()`(MVP-0006, `workflow_project_intelligence.py`)를
  재사용해 중복 구현을 피했다.
- 기존 파일(`agents.py`, `engine.py`, `project_intelligence.py`,
  `workflow.py`, `workflow_0002.py`, `workflow_hello_sdlc.py`,
  `workflow_project_intelligence.py`)은 **수정하지 않았다**. 새
  Capability를 추가하지 않았고, Task Dispatcher/Runtime/Pipeline/
  Stage Runner는 구현하지 않았다.

## 관찰 결과

### Requirement(Planning 산출물)가 Design으로 어떻게 전달되는가?

**전체 텍스트가 그대로 전달된다.** `design_agent_design(issue, requirement)`
(`agents.py:47-50`)는 `requirement` 문자열 전체를 `f"...요구사항: {requirement}"`
형태로 자신의 반환 텍스트에 이어붙인다(`engine.py:94-97`
`_design_from_requirement`). 두 Issue(Task Dispatcher 관련, 무관한
reverse string)로 실제 실행해 `requirement_text in design_text`가
**True**임을 확인했다 — Design 산출물은 Requirement 산출물을
부분집합으로 그대로 포함한다.

다만 Design이 Requirement에서 구조적으로 실제 사용하는 부분은 `title`
뿐이다 — `title`을 slug로 변환해 함수 이름(`` `reverse_string(...)` ``
등)을 만드는 데만 쓰고, `requirement` 문자열 자체는 파싱하지 않고
텍스트로만 이어붙인다.

### Architecture(Design 산출물)가 Implementation으로 어떻게 전달되는가?

**마찬가지로 전체 텍스트가 그대로 전달된다.** `backend_agent_code_generation(design)`
은 Design 텍스트에서 백틱(`` ` ``) 사이의 함수 이름만 추출해 함수
시그니처를 만들고(`engine.py:100-105` `_extract_slug`), Design 텍스트
전체를 그대로 docstring(`"""TODO: {design_text}"""`)에 밀어넣는다
(`engine.py:108-114` `_generate_code`). 실제 실행 결과
`design_text in implementation_text`가 **True**였다 — Implementation
산출물은 Design 산출물을 그대로 포함한다.

### "Project Intelligence는 Planning에서만 사용한다"는 실제로 지켜지는가?

**워크플로우 호출 인자 수준에서는 지켜졌지만, Artifact 텍스트 수준에서는
지켜지지 않았다.** `design_agent_design()`에는 Context가 없는 원본
`issue`를 넘겼음에도(호출부만 보면 Design은 PI를 모른다), 실행 결과
`design` 텍스트와 `implementation` 텍스트 양쪽 모두에 `[Relevant
Context]` 절이 그대로 나타났다.

원인은 위 두 관찰과 같다: Design은 `issue`가 아니라 `requirement`
전체를 그대로 이어붙이는데, 그 `requirement`는 이미 Planning
단계에서 Context가 섞인 `enriched_issue`로부터 만들어졌기 때문이다.
같은 방식으로 Implementation은 `design` 전체를 그대로 docstring에
밀어넣기 때문에, Design 텍스트에 들어있던 Context도 함께 넘어간다.
즉 "PI를 어느 Stage 함수의 인자로 넘기는가"와 "PI 내용이 실제로 그
Stage의 산출물에 도달하는가"는 이번 Engine 구현에서는 서로 다른
질문이었다 — 후자는 인자 전달이 아니라 각 Stage가 상위 Artifact를
얼마나 그대로(verbatim) 이어붙이는가에 의해 결정되었다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability 추가. `run_issue_to_implementation`은 기존 4개 Agent
  함수(requirement_analysis, design, code_generation — PI는 Capability
  아님)만 호출했다.
- Task Dispatcher, Runtime, Pipeline, Stage Runner 구현.
- `engine.py`의 verbatim 이어붙이기 동작을 바꾸는 것(예: Design이
  Requirement를 요약해서만 반영하도록 수정). 이는 Architecture
  판단이므로 이번 범위에서 하지 않았다.
- Validation Stage(code_review, test_execution)로의 Artifact 전달 관찰.
  이번 범위는 Planning -> Design -> Implementation까지다.
- "Artifact가 verbatim으로 전달되는 현재 구조가 바람직한지"에 대한
  판단. 이 문서는 관찰한 사실만 기록한다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음.
- `run_issue_to_implementation()`을 서로 다른 2개 Issue(Task Dispatcher
  관련, 무관한 reverse string)에 대해 수동 실행해 `requirement in
  design`, `design in implementation`이 두 Issue 모두에서 True임을
  확인했다. 동시에 Design에 원본(Context 없는) `issue`를 넘겼음에도
  `[Relevant Context]`가 `design`, `implementation` 양쪽 텍스트에
  나타남을 확인했다. 별도 자동화 테스트는 추가하지 않았다.
