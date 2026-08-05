# MVP-0002 Plan

## 목적

MVP-0002의 목적은 새로운 기능을 만드는 것이 아니다. ADC-0001에서 "Keep in
MVP"로 판단된 4개 Candidate 중, RT-0001이 정의한 Re-evaluation Trigger
하나를 실제로 발생시켜 Observation을 확보하는 것이다.

이 문서는 계획 문서다. 이번 작업에서는 구현하지 않는다.

## 현재 상태 (변경하지 않음)

- MVP-0001, RFC-0001, ADC-0001, RT-0001, Governance README는 Governance
  Baseline v1으로 확정되어 있다.
- 이 문서는 위 5개 문서 중 어떤 것도 수정하지 않는다.

## 목표

RT-0001에서 정의된 Trigger 중 정확히 하나를 실제로 발생시켜, ADC-0001의
Decision Rationale이 의존했던 전제("MVP-0001에서 관찰된 유일한 사례")가
더 이상 성립하지 않는 순간을 직접 관찰한다.

## 발생시킬 Trigger

- **Candidate**: Task Dispatcher
- **Trigger**(RT-0001 원문): Workflow Branch 발생 — "Task 흐름에 조건
  분기·재시도·병렬 실행이 실제로 구현됨"
- 이번 MVP-0002는 이 중 **조건 분기(Branch) 1개**만 발생시킨다. 재시도,
  병렬 실행은 다루지 않는다.

## 왜 이 Trigger를 선택했는가

- 4개 후보 중 Task Dispatcher의 Workflow Branch Trigger만 MVP-0001의 기존
  코드(`development-hq/mvp/workflow.py`)를 그대로 확장하는 것만으로 관찰이
  가능하다. 새 Engine 함수, 새 HQ 디렉토리, 새 전달 경로 같은 부가 산출물이
  필요 없다.
- Engine 수 ≥ 2 Trigger(Engine Gateway)와 HQ 수 ≥ 2 Trigger(Agent Registry)는
  각각 두 번째 Engine 함수 또는 두 번째 HQ(Mission/Boundary 등 문서 포함)를
  동반해야 하므로, "최소 구현" 원칙 대비 산출물이 상대적으로 무겁다.
- Context 전달 경로 ≥ 2 Trigger는 "두 번째 전달 경로"를 만드는 행위 자체가
  파일 저장 등 영속화 메커니즘으로 보이기 쉬워, Memory Service를 설계하는
  것으로 오인될 위험(Kernel Leak 위험)이 상대적으로 크다.
- Workflow Branch는 기존 두 줄의 순차 호출에 조건 하나만 추가하면 되므로,
  새 Layer/Component 없이 가장 작은 코드 변경으로 Trigger를 발생시킬 수
  있다.

## 최소 구현 범위 (Minimum Observation Product)

- `development-hq/mvp/workflow.py`의 Task 1→Task 2 호출부에 조건 분기
  **1개**를 추가한다. 예: `code_review` 결과에 따라 `test_execution`으로
  이어지는 경로와 그렇지 않은 경로를 하드코딩된 `if`/`else`로 표현한다.
- 분기는 정확히 1개만 추가한다. 중첩 분기, 재시도, 병렬 실행은 포함하지
  않는다.
- 분기 로직은 `if`/`else` 형태 그대로 유지한다. 설정 파일, 파서, Workflow
  스키마로 일반화하지 않는다.
- 관찰 대상: 이 분기가 추가된 뒤에도 하드코딩된 직접 호출 방식이 그대로
  유지 가능한지, 아니면 Implementation Stop Trigger("조건문이
  파서/설정 파일로 대체되려는 순간")가 실제로 발생하는지.
- 코드 변경 범위는 기존 MVP-0001 파일 수정, 또는 이를 복제한 별도 스크립트
  1개를 넘지 않는다.

## Non-goals

- Kernel, Runtime, Registry, Scheduler, Memory, Engine Gateway를 만들지
  않는다.
- Workflow Parser, Policy, Event Bus를 만들지 않는다.
- 분기 조건을 둘 이상 만들지 않는다(다중 분기·재시도·병렬 실행 제외).
- 새로운 Capability나 Agent를 추가하지 않는다(기존 `code_review`,
  `test_execution`, Backend Agent, QA Agent만 사용).
- Engine 추가, HQ 추가, Context 전달 경로 추가는 이번 MVP-0002에서 다루지
  않는다. 이는 RT-0001의 다른 Trigger에 해당하며, 별도 후속 MVP 후보로
  남긴다.
- 새로운 Framework를 도입하지 않는다.
- RFC-0001, ADC-0001, RT-0001, Governance README를 수정하지 않는다.
- 이번 작업에서는 구현하지 않는다. 계획만 작성한다.

## Self Review

- Trigger가 RT-0001과 일치하는가 → **Pass**. Task Dispatcher의 "Workflow
  Branch 발생" 문구를 그대로 사용했다.
- Trigger가 하나뿐인가 → **Pass**. Engine 수, HQ 수, Context 전달 경로
  Trigger는 다루지 않았다.
- Architecture Drift가 없는가 → **Pass**. 새 Layer/Component/Service/Module
  없음.
- Governance를 수정하지 않았는가 → **Pass**. RFC-0001/ADC-0001/RT-0001/
  Governance README 미수정.
- Observation 확보가 목표인가 → **Pass**. 목표 자체가 "관찰"이며 기능
  확장이 아니다.
