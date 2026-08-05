# MVP-0008 Observation: Development HQ가 실제 Issue 하나를 처리한다

## 목적

Development HQ가 Development HQ 자신의 실제 Issue 하나를
Planning → Design → Implementation → Validation까지 처리하는 것을
실행하고, Artifact Flow와 Information Flow를 사실로만 기록한다.
Architecture 판단은 하지 않는다.

## 사용한 실제 Issue

토이 예시가 아니라, 이 저장소에서 실제로 발생한 Issue를 그대로
사용했다 — MVP-0007 Observation(`docs/01_mvp/MVP-0007-observation.md`)
이 실측으로 발견한 문제를 다루는 "Project Intelligence 개선" Issue다.

```
title: "Project Intelligence 개선"
description: "MVP-0007 Observation에서 실측으로 확인됨: design_agent_design과
  backend_agent_code_generation은 상위 Stage의 Artifact(Requirement, Design)
  전체를 요약 없이 그대로 이어붙인다. 그 결과 Project Intelligence가
  Planning에서만 수집한 Relevant Context가 Design과 Implementation
  산출물에도 의도치 않게 그대로 나타난다. Project
  Intelligence(collect_relevant_context)가 이 문제를 완화할 수 있는
  방향으로 개선될 수 있는지 검토가 필요하다."
```

이 예시는 MVP-0008 지시문이 든 예시(Task Dispatcher 일반화 / Project
Intelligence 개선 / Artifact Flow 검증) 중 하나이며, 실제로 이번
저장소의 MVP-0007 실행 결과에서 나온 사실이다.

## 변경 파일

- `development-hq/mvp/workflow_0008.py` (신규) — 실제 Issue
  상수(`REAL_ISSUE`)와 `run_pipeline(issue) -> dict`. MVP-0004
  `workflow_hello_sdlc.py`와 동일하게 Planning → Design →
  Implementation → Validation(code_review → test_execution) 4단계를
  유지하는 하드코딩된 순차 호출이다. Project Intelligence는
  `requirements_agent_requirement_analysis` 호출 직전에서만 사용했다
  — `design_agent_design`에는 Context가 섞이지 않은 원본 Issue를
  그대로 넘겼다(MVP-0007과 동일한 방식). `_enrich_issue`(MVP-0006)를
  재사용해 중복 구현을 피했다.
- 기존 파일(`agents.py`, `engine.py`, `project_intelligence.py`,
  `workflow.py`, `workflow_0002.py`, `workflow_hello_sdlc.py`,
  `workflow_project_intelligence.py`, `workflow_artifact_flow.py`)은
  **수정하지 않았다**. 새 Capability를 추가하지 않았다. Task
  Dispatcher, Runtime, Stage Runner, Pipeline Runner는 구현하지
  않았다.

## Artifact Flow 관찰 (사실만 기록)

위 Issue로 `run_pipeline()`을 실제 실행한 결과:

- **Planning → Design**: `requirement`(1,383자) 전체가 `design`
  (1,443자) 텍스트에 부분 문자열로 그대로 포함됨을 확인했다
  (`requirement in design` == True). MVP-0007과 동일한 verbatim
  이어붙이기가 재현되었다.
- **Design → Implementation**: `design`(1,443자) 전체가
  `implementation`(1,533자)의 docstring에 그대로 포함됨을 확인했다
  (`design in implementation` == True).
- **Implementation → Validation(code_review)**: `backend_agent_code_review(code)`
  는 `code` 전체 문자열을 줄 단위로 스캔한다. `implementation`에
  `[Relevant Context]` 절이 그대로 들어있었기 때문에, `code_review`가
  실제로 반환한 findings 중 7건이 "N번째 줄이 100자를 초과합니다"였다
  — 전부 docstring 안에 이어붙은 Context 목록 줄(카테고리별 파일
  목록)이 100자를 넘긴 것이었다. 이 findings 중 `NotImplementedError`
  스텁이라는 사실 자체를 지적한 것은 "TODO 주석이 남아있습니다" 1건
  뿐이었고, 나머지는 실제 로직이 아니라 이어붙은 Artifact 텍스트의
  길이 때문에 발생했다.
- **Validation(code_review) → Validation(test_execution)**:
  `qa_agent_test_execution(code, review)`는 `code`에서 함수 이름
  (`project_intelligence`)만 추출해 2건의 테스트 케이스 문구를
  만들었다. `code_review`의 findings 텍스트에서 "bare except"나
  "mutable default argument" 문자열이 없었으므로, 그 findings에
  조건부로 추가되는 추가 테스트 케이스(예: 예외 처리 검증)는 이번
  실행에서 추가되지 않았다.

## Information Flow 관찰 (사실만 기록)

- Project Intelligence(`collect_relevant_context`)가 반환한 8개
  카테고리 중 7개(`source_code`, `existing_workflow`,
  `mvp_documents`, `obs_documents`, `rfc_documents`, `adc_documents`,
  `adr_documents`, `rt_documents` — `directory_structure` 제외)
  모두에서 실제로 파일이 검색되었다. 이 Issue가 이 저장소 자신의
  실제 작업(MVP-0005~0007, RFC-0002/0003/0004, ADC-0001/0003/0004,
  ADR-0001, RT-0001)을 언급하고 있었기 때문이다.
- Design(`design_agent_design`)은 Issue의 `title`만 구조적으로
  사용해 함수 이름(`project_intelligence`)을 만들었고, `requirement`
  전체는 파싱 없이 텍스트로만 이어붙였다. 즉 Design 함수가 실제로
  "읽은" 것은 제목 한 줄뿐이었다.
- Implementation(`backend_agent_code_generation`)은 Design 텍스트에서
  백틱 사이 함수 이름만 추출했고, 나머지 Design 텍스트 전체(Context
  포함)는 다시 파싱 없이 docstring으로 이어붙였다.
- Validation 두 함수(`backend_agent_code_review`,
  `qa_agent_test_execution`)는 Issue 원문이나 `context` dict를 인자로
  전혀 받지 않는다 — 이 시점부터 Information Flow의 유일한 경로는
  `implementation`(코드+누적된 Context 텍스트) 문자열 자체였다.
  Validation은 원본 Issue 제목/설명이나 Requirement/Design 산출물에
  직접 접근하지 못했고, Implementation 문자열에 남아있는 흔적을 통해
  간접적으로만 정보를 전달받았다.
- 요약하면, Context 및 상위 Artifact 텍스트는 Stage를 거칠 때마다
  누적되며 커졌다(1,383 → 1,443 → 1,533자, Validation 입력인 `code`
  기준). 반면 각 Stage 함수가 구조적으로 실제 사용한 정보는
  Stage마다 한두 개 필드(제목 → slug, 함수 이름)로 매우 좁았다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability 추가. `run_pipeline`은 기존 5개 Agent 함수만 그대로
  호출했다.
- Task Dispatcher, Runtime, Stage Runner, Pipeline Runner 구현.
- MVP-0007에서 발견되고 이번 실행에서 재확인된 verbatim 이어붙이기
  동작이나 Project Intelligence의 개선(요약, 필터링 등) — Issue
  본문이 요청하는 개선 자체를 구현하지 않았다. 이번 MVP의 범위는
  "Issue를 Pipeline에 통과시키고 관찰하는 것"이지 그 Issue가 요청한
  변경을 수행하는 것이 아니다.
- Architecture 판단. Artifact가 verbatim으로 누적되는 것이
  바람직한지, Project Intelligence를 어떻게 개선해야 하는지는 이
  문서가 판단하지 않는다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음.
- `run_pipeline(REAL_ISSUE)`를 수동 실행해 Planning → Design →
  Implementation → Validation 4단계가 예외 없이 끝까지 진행되고, 각
  단계 반환값이 위에 기록한 내용과 일치함을 확인했다. 별도 자동화
  테스트는 추가하지 않았다.
