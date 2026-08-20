# Development HQ MVP-0001

**Status: Approved — v1.0 Final**

## Mission

이 MVP의 목적은 완전한 개발 플랫폼을 만드는 것이 아니라, Development HQ Architecture가 실제로 동작하는지 검증하는 것이다. 가장 작은 범위로 가장 큰 검증을 수행한다.

## User Scenario

사용자가 짧은 코드 스니펫을 제출하며 "이 코드를 리뷰하고, 필요한 테스트 케이스를 제안해 달라"고 요청한다.

## Expected Result

- 코드 리뷰 코멘트 (개선 제안 포함)
- 위 리뷰를 반영한 테스트 케이스 제안 목록

## Exit Criteria

입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환된다. 이 조건을 만족하면 MVP는 성공으로 본다.

이 과정에서 Registry/Scheduler/Policy에 해당하는 범용 서비스 코드가 생성되지 않았어야 한다.

## Workflow (가장 짧은 형태)

```
Task 1 (code_review) → Task 2 (test_execution)
```

Task 1의 출력(리뷰 코멘트)이 Task 2의 입력 컨텍스트로 전달된다. 2단계, 단일 선형 체인. 분기·재시도·병렬 실행 없음.

## Required Capability (예시 수준, STRUCTURE.md 재사용)

- `code_review`
- `test_execution`

## Required Agents (최소 수, STRUCTURE.md 재사용)

- **Backend Agent** — `code_review` 수행
- **QA Agent** — `test_execution`(테스트 케이스 제안) 수행

## Out of Scope

- Scheduler / Runtime
- Multi-HQ
- Memory Persistence
- Background Execution / Distributed Execution
- Multi Engine
- Connector Auto Discovery
- Policy 판정 (PDP/PEP 호출 자체를 생략)
- Registry의 동적 등록/탐색
- Lifecycle State, Fault 전파 인프라, Event Bus

## Kernel Extraction Candidate (구현하지 않고 기록만)

| 후보 | MVP에서 임시로 어떻게 처리되는가 |
|---|---|
| Task Dispatcher | Task 1→Task 2 순서를 스크립트에 직접 함수 호출로 하드코딩 |
| Engine Gateway | 특정 Engine API를 호출하는 함수 하나만 작성 |
| Registry | Agent-Capability 매핑을 리터럴 딕셔너리로 고정 |
| Context 전달 메커니즘 | Task 간 데이터 전달을 단순 in-memory 변수로 처리 |

이 4개는 구현되지 않는다. 코드 안에 필요성이 드러나는 지점만 주석으로 남긴다.

## Implementation Complexity

**Low.** 2개 Task, 2개 Agent, 단일 Engine 호출, 저장소 없음, 분기 없음.

## Reference Architecture Validation

다른 HQ에서도 동일한 방식으로 구현 가능. 이 MVP의 구조(2-Task 선형 Workflow, 2-Agent 체인, 정적 Capability-Agent 매핑, 하드코딩된 단일 Engine 호출)는 도메인에 무관하다.

## 구현 중단 트리거 (필독 — IMPLEMENTATION_RULES.md와 연동)

다음 두 현상 중 하나라도 발생하면 구현을 즉시 중단하고 RFC → ADC → ADR 절차로 넘긴다.

- Agent-Capability 매핑이 Registry처럼 일반화되려는 경우
- Task 호출이 Workflow Parser 또는 Scheduler 형태로 일반화되려는 경우

이는 Kernel Extraction Candidate가 예상보다 빨리 필요해졌다는 신호이며, 직접 구현으로 해소하지 않는다.
