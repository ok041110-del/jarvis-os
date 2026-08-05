# MVP-0003 Plan

## 목적

Development HQ가 하나의 개발 Task를 끝까지 관리할 수 있는지 검증한다.
새로운 Architecture를 만드는 것이 목적이 아니라, Task Lifecycle
(Created → Running → Completed/Failed)을 실제 코드에서 관찰하는 것이
목적이다.

이 문서는 계획 문서다. 이번 작업에서는 구현하지 않는다.

## 현재 상태 (변경하지 않음)

- MVP-0001, MVP-0002(plan/observation), RFC-0001, RFC-0002, ADC-0001,
  ADC-0002, RT-0001, Governance README는 확정되어 있다.
- 이 문서는 위 문서 중 어떤 것도 수정하지 않는다.

## 검증할 시나리오

Task 하나를 생성해 다음 상태 전이를 관찰한다.

```
Created
  ↓
Running
  ↓
Completed 또는 Failed
```

- 대상 Task는 기존에 이미 존재하는 Capability(`test_execution`, QA Agent)
  를 그대로 재사용한다. 새 Capability를 추가하지 않는다.
- 성공 경로: `test_execution`이 정상 종료 → Task 상태가 `Completed`로
  전이한다.
- 실패 경로: `test_execution` 호출 중 예외가 발생 → Task 상태가 `Failed`로
  전이한다.
- 두 경로 모두 관찰 대상이다. Task 하나에 대해 두 실행(성공 1회, 실패
  1회)을 각각 수행해 상태 전이를 확인한다.

## 목표 (Observation)

관찰하고 싶은 것은 다음 세 가지뿐이다.

1. Task가 상태(Created/Running/Completed/Failed)를 가지는가?
2. 그 상태가 실행 중 실제로 변경되는가?
3. Workflow(기존 `run_mvp_0001`/`run_mvp_0002` 호출 경로)가 이 상태를
   이용하는가, 아니면 무시하고 지나가는가?

## 최소 구현 범위 (Minimum Observation Product) — 계획만, 구현하지 않음

- 기존 `development-hq/mvp/agents.py`의 `qa_agent_test_execution()` 호출을
  감싸는 최소한의 Task 표현을 만든다. 예: `status` 필드 하나를 가진 간단한
  자료구조(dict 또는 dataclass 1개)로 `id`, `capability`, `status`만
  담는다.
- 상태 전이는 코드 안에서 순서대로 직접 대입한다: 생성 시 `Created`,
  `qa_agent_test_execution()` 호출 직전 `Running`, 호출이 예외 없이
  끝나면 `Completed`, 예외가 발생하면 `Failed`.
- 상태 전이 로직은 하드코딩된 대입문(`task["status"] = "Running"` 등)으로만
  표현한다. 상태 머신 클래스, 전이 규칙 테이블, 이벤트 발행은 두지 않는다.
- 새 파일을 추가하더라도 기존 `development-hq/mvp/` 디렉토리 구조 안에서
  1개 파일 이내로 한정한다. MVP-0001/0002의 기존 파일은 수정하지 않는다.

## Non-goals

- Scheduler, Queue, Runtime, Event Bus, Registry, Memory, Persistence를
  만들지 않는다.
- 병렬 실행, Retry, Priority, Worker를 구현하지 않는다.
- 새로운 Capability나 Agent를 추가하지 않는다.
- Task 상태를 영속화하지 않는다(in-memory로만 존재하고 프로세스 종료 시
  사라진다).
- 여러 Task를 동시에 또는 순서대로 관리하는 구조(Task 목록, Task 큐)를
  만들지 않는다. 이번 MVP는 Task 하나의 생애주기만 관찰한다.
- RFC-0001, RFC-0002, ADC-0001, ADC-0002, RT-0001, Governance README를
  수정하지 않는다.
- 이번 작업에서는 구현하지 않는다. 계획만 작성한다.

## Self Review

- Architecture Drift가 없는가 → **Pass**. Scheduler/Queue/Runtime/
  EventBus/Registry/Memory/Persistence를 계획에 포함하지 않았다.
- Observation 확보가 목표인가 → **Pass**. 목표 문구 자체가 "관찰"이며
  Task 관리 기능의 실사용 확장이 아니다.
- Task Lifecycle이 실제로 관찰 가능한가 → **Pass(계획 수준)**. 성공 경로와
  실패 경로 각각에서 `Created→Running→Completed`와
  `Created→Running→Failed` 전이를 관찰할 수 있도록 시나리오와 최소 구현
  범위를 구체적으로 정의했다.
