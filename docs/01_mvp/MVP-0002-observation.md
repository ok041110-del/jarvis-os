# MVP-0002 Observation

## 목적

`docs/01_mvp/MVP-0002-plan.md`에 따라, RT-0001의 Task Dispatcher Trigger
("Workflow Branch 발생")를 실제 코드에서 발생시키고 그 결과를 관찰한다.

## 변경 파일

- `development-hq/mvp/workflow_0002.py` (신규) — `run_mvp_0002(code)`: 기존
  `agents.py`의 `backend_agent_code_review`, `qa_agent_test_execution`을
  그대로 재사용하되, code_review 결과에 조건 분기 1개를 추가했다.
  - 이슈 발견 시 → `test_execution` 그대로 호출 (기존 MVP-0001과 동일 경로)
  - 이슈 없음 시 → `test_execution` 호출을 건너뛰고 생략 메시지 반환
- `development-hq/mvp/workflow.py`(MVP-0001)는 수정하지 않았다. MVP-0001의
  Exit Criteria와 기존 테스트가 "분기 없음"을 그대로 검증하고 있으므로,
  Trigger는 별도 파일에서 발생시켰다.

## 관찰 결과

### Workflow에 Branch가 실제 존재하는가?

**예.** `run_mvp_0002()` 안에 `if NO_ISSUE_MARKER in review: ... else: ...`
형태의 조건 분기가 1개 존재하며, 실제 실행으로 두 경로 모두 확인했다.

- 이슈가 있는 코드 입력 → `test_execution`이 정상 실행되어 4개 테스트
  케이스 제안 반환 (분기 A)
- 이슈가 없는 코드 입력 → `test_execution` 호출이 건너뛰어지고 생략
  메시지만 반환 (분기 B)

두 경로 모두 실제로 트리거되는 것을 수동 실행으로 확인했다.

### RT-0001 Trigger가 충족되었는가?

**예.** RT-0001 · Candidate: Task Dispatcher의 Trigger 문구는 "Workflow
Branch 발생 (Task 흐름에 조건 분기·재시도·병렬 실행이 실제로 구현됨)"이다.
이번 구현으로 조건 분기가 실제로 구현되었으므로, 이 Trigger는 충족되었다.

재시도·병렬 실행은 이번 구현에 포함되지 않았으며, Trigger 문구의 "조건
분기" 부분만 충족한다.

Trigger 충족 자체가 관찰의 목적이었으며, 이 관찰이 ADC-0001의 Task
Dispatcher Decision("Keep in MVP")을 재검토할지 여부는 이 문서가 판단하지
않는다. 그 판단은 다음 RFC의 몫이다.

### 분기 추가 후 하드코딩된 직접 호출 방식은 그대로 유지되었는가?

**예, 이번 규모(분기 1개)에서는 유지되었다.** `if`/`else` 조건문 하나만
추가했고, Implementation Stop Trigger("조건문이 파서/설정 파일로
대체되려는 순간")는 발생하지 않았다. 조건 판단 기준(`NO_ISSUE_MARKER`
문자열 포함 여부)도 하드코딩된 상수 비교이며, 별도 설정이나 파서를
도입하지 않았다.

이 관찰은 "분기 1개"라는 최소 규모에 한정된다. 분기가 늘어나거나 중첩될
때도 동일하게 유지되는지는 이번 구현으로 확인되지 않았다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 재시도, 병렬 실행 (RT-0001 Trigger 문구의 나머지 부분)
- 두 번째 Engine 추가, 두 번째 HQ 추가, Context 전달 경로 추가 (RT-0001의
  다른 Candidate Trigger)
- Workflow Parser, Scheduler, Registry, Engine Gateway, Policy, Memory
  Service, Event Bus 구현
- 새로운 Capability, Agent 추가
- MVP-0001(`workflow.py`)의 수정 또는 리팩터링
- RFC-0002, ADC-0002 작성, RT-0001 수정, ADR 작성

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건 모두
  통과 — MVP-0002 구현이 MVP-0001 동작에 영향을 주지 않았음을 확인.
- `run_mvp_0002()`를 이슈 있는 코드/이슈 없는 코드 각각에 대해 수동 실행하여
  두 분기가 모두 실제로 트리거됨을 확인. 별도 자동화 테스트는 추가하지
  않았다(계획서 6항: "새 테스트가 꼭 필요하지 않다면 추가하지 않는다").
