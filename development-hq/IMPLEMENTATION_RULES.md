# Implementation Rules

이 문서는 Claude Code가 Development HQ MVP-0001을 구현할 때 반드시 지켜야 하는 규칙만 정리한다. 모두 이미 승인된 내용이며, 새로운 규칙을 추가하지 않는다.

## 금지 사항

| 금지 항목 | 이유 |
|---|---|
| Workflow Parser 구현 금지 | Task 1→Task 2는 직접 함수 호출로 충분. 파서는 Scheduler를 미리 만드는 것과 동일 |
| Scheduler 구현 금지 | MVP는 Task 순서를 스크립트에 하드코딩한다 |
| Registry 구현 금지 | Agent-Capability 매핑은 리터럴 딕셔너리 이상으로 발전시키지 않는다 |
| Registry 일반화 금지 | 정적 딕셔너리를 조회 함수, 클래스, 동적 등록 API 등 어떤 형태로도 일반화하지 않는다 |
| Runtime 구현 금지 | Runtime 개념 자체가 Open Decision(ADC-02)이다 |
| Engine Gateway(Port/Adapter 추상화) 구현 금지 | 단일 함수로 Engine을 호출하는 것으로 충분하다 |
| Engine Routing 구현 금지 | 여러 Agent 또는 여러 Engine 중 무엇을 선택할지 결정하는 로직을 만들지 않는다. MVP는 Engine을 호출하는 함수 하나만 가진다 |
| Policy 구현 금지 | MVP는 Policy 판정 호출 자체를 생략한다 (스텁도 만들지 않는다) |
| Memory Service(영속화 계층) 구현 금지 | Context는 in-memory 변수로만 다룬다 |
| Event Bus 구현 금지 | MVP는 단일 선형 Task Flow만 다루며 Event Flow를 쓰지 않는다 |
| Multi-HQ 지원 코드 작성 금지 | MVP는 Development HQ 단독 시나리오만 다룬다 |
| Multi Engine 지원 코드 작성 금지 | 단일 Engine 호출로 충분하다 |
| Architecture Baseline 및 Development HQ Baseline 수정 금지 | 두 Baseline은 Frozen 상태다 |

## 구현 중 새 Capability/Agent 추가 금지

MVP는 `STRUCTURE.md`에 이미 예시로 등재된 Capability(`code_review`, `test_execution`)와 Agent(Backend Agent, QA Agent)만 사용한다. 구현 편의를 위해 새 Capability나 Agent를 추가하지 않는다.

## 구현 중단 트리거

다음 두 현상 중 하나라도 실제 코드에서 나타나면, 구현을 즉시 중단하고 `docs/02_rfc` → `docs/03_adc` → `docs/04_adr` 절차로 넘긴다. 직접 고치지 않는다.

1. Agent-Capability 매핑이 리터럴 딕셔너리를 넘어서는 클래스/서비스로 발전하려는 순간
2. Task 1→Task 2 호출이 조건문·설정 파일·파서로 대체되려는 순간

이는 새로운 Architecture, Component, Layer, Concept를 만드는 것이 아니라, Kernel Extraction이 예상보다 이르게 필요해졌다는 관찰을 ADC 후보로 기록하기 위한 절차다.

## Architecture 문제 발견 시 절차

**Architecture 변경은 구현으로 해결하지 않는다.** 구현 중 Architecture 결함이 발견되었다고 해서 그 결함을 코드로 메우거나 우회하지 않는다.

Development HQ 구현 중 Architecture 수준의 문제(Concept 누락, Boundary 모순 등)를 발견하면:

1. 직접 수정하지 않는다.
2. `docs/02_rfc`에 문제를 기록한다.
3. `docs/03_adc/ADC.md`에 Decision Candidate로 등록한다.
4. NOW로 분류되지 않는 한, 구현은 현재 MVP 범위 내에서 계속 진행한다.

## Exit Criteria 재확인

구현 완료 판단 기준은 `MVP.md`의 Exit Criteria를 그대로 따른다: 입력 코드가 주어지면 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환되고, 이 과정에서 Registry/Scheduler/Policy에 해당하는 범용 서비스 코드가 생성되지 않아야 한다.
