# Architecture Decision Candidate List

이 문서는 Jarvis OS의 모든 Open Decision에 대한 Single Source of Truth다. 구현 진행 여부와 무관하게, 여기 기록된 항목은 상태가 갱신될 때까지 Open으로 유지된다.

이 문서는 Jarvis OS(Kernel) 수준 Open Decision(ADC-01~12)만 다룬다. Development HQ 수준 ADC는 `docs/governance/adc/`, Kernel Architecture RFC 후속 ADC는 `docs/architecture/core/`, Execution Layer 수준 ADC는 `docs/core/execution-layer/`에 각각 별도로 등록되어 있다(`DOC-TRIAGE-0001` D-7).

**Experimental Implementation과의 관계**(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" 참조): Experimental 단계에서 얻은 Evidence는 Observation으로 기록될 수 있으나, 그 존재만으로 이 문서의 Open Decision이나 다른 트랙(위 문단 참조)의 Deferred Decision이 자동으로 재개되지 않는다. 각 Decision의 기존 재개 Trigger는 그대로 유지되며, Formal Architecture 승격을 시도하는 경우에만 RFC → ADC → ADR 절차를 따른다. Experimental은 이 문서가 정의하는 Governance를 우회하기 위한 예외가 아니다.

---

## ADC-01. Model 축과 Component 축의 대응 관계

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: Execution/Communication/Memory 3개 Model 축 제안과, Scheduler/Engine Gateway/Registry/Communication/Memory/Policy 6개 Component 축 제안 사이의 정확한 대응 관계가 정의되지 않음.

**결정 필요 이유**: Kernel Boundary 설계의 용어·구조적 전제가 됨.

**미결정 시 문제**: Registry/Communication 간 책임 경계가 반복적으로 재해석됨.

---

## ADC-02. Runtime 개념의 존폐

**상태**: Open · **우선순위**: NOW

**충돌 내용**: Concept Model은 Runtime을 Service로 유지하나, Core Component 검토에서는 Runtime을 폐기하고 Scheduler + Engine Gateway로 대체할 것을 권고함.

**결정 필요 이유**: Concept Model은 모든 후속 문서의 용어 기준선임.

**미결정 시 문제**: "Runtime 버그"라는 보고가 어느 Component를 가리키는지 구분 불가.

---

## ADC-03. Connector(MCP)의 아키텍처 상 위치

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: Connector가 Engine과 동일한 Port/Adapter 패턴을 공유하는지 정의되지 않음.

**결정 필요 이유**: Engine Independent/Everything is Replaceable 원칙이 Connector에도 적용되는지 결정 필요.

**미결정 시 문제**: Connector마다 임시방편 통합 방식이 생기고 추후 소급 재작업 필요.

---

## ADC-04. Observability/Audit 소속 Component

**상태**: Open · **우선순위**: LATER

**충돌 내용**: OS 책임(인프라 로깅)과 HQ 책임(도메인 해석)의 구분은 System Boundary에서 확인되었으나, OS 내부 어느 Component가 담당하는지 미정.

**결정 필요 이유**: No Silent Failure 원칙의 실질적 집행 주체가 필요.

**미결정 시 문제**: 각 Component가 제각각 로깅하여 통합 관측 경로 부재.

---

## ADC-05. Fault Event 배달 보장 수준

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: Fault가 Task Flow 수준(at-least-once)으로 배달되는지, Event Flow 수준(best-effort)으로 배달되는지 미정.

**결정 필요 이유**: No Silent Failure와 직결되는 계약 수준 결정.

**미결정 시 문제**: Fault가 일반 Event와 동일 취급되어 부하 상황에서 유실 가능.

---

## ADC-06. Lifecycle State 전환 권한 경로

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: HQ 상태 전환(특히 Disabled 해제)이 Policy 승인을 반드시 거쳐야 하는지 미정.

**결정 필요 이유**: "Disabled는 사람만 재활성화 가능"이라는 원칙의 강제 주체 필요.

**미결정 시 문제**: Registry 쓰기 권한이 있는 임의 프로세스가 Disabled를 우회 가능.

---

## ADC-07. Resource(Token 예산)의 이중 소속

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: Token 예산이 Scheduler 책임인지 Policy 책임인지, 혹은 분담 방식이 미정.

**결정 필요 이유**: God Component 방지, Simple > Complex 원칙 준수.

**미결정 시 문제**: 예산 정책 변경 시마다 Scheduler 코드 수정 필요.

---

## ADC-08. Task/Event Flow 배달 보장 차등화

**상태**: Open · **우선순위**: NEXT

**충돌 내용**: Task Flow(순서·무유실)와 Event Flow(도달 범위)가 실제로 다른 배달 보장 수준으로 구현되는지 미정.

**결정 필요 이유**: Task/Event Flow 분리가 실질적 계약 차이로 이어져야 함.

**미결정 시 문제**: Task Flow에 필요한 신뢰성이 보장되지 않을 수 있음.

---

## ADC-09. Workflow 그래프의 의미론적 경계

**상태**: Open · **우선순위**: NOW

**충돌 내용**: OS가 이해해야 하는 Workflow 스키마가 순수 범용 그래프인지, 도메인 특화 노드 타입을 포함하는지 미정.

**결정 필요 이유**: System Boundary("OS는 도메인 내용을 모른다")가 실제로 성립하는지 좌우함.

**미결정 시 문제**: OS Scheduler가 다시 도메인 지식(예: SDLC)을 흡수할 위험.

**참고 자료**: Development HQ MVP의 Workflow 스키마(`{task_type, capability_required, inputs/outputs}`)가 이 결정에 실증 사례로 활용 가능.

---

## ADC-10. Policy 규칙의 출처 분리

**상태**: Open · **우선순위**: NOW

**충돌 내용**: Policy Engine이 OS 전역 규칙만 평가하는지, HQ 도메인 규칙까지 평가 대상으로 삼는지 미정.

**결정 필요 이유**: "메커니즘은 OS, 내용은 HQ"라는 System Boundary 원칙의 성립 여부가 걸림.

**미결정 시 문제**: OS가 HQ의 비즈니스 규칙 내용을 알아야 하는 구조가 되어 System Boundary를 넘음.

---

## ADC-11. Capability 선언의 신뢰 검증 책임

**상태**: Open · **우선순위**: LATER

**충돌 내용**: Registry에 등록된 Capability가 자기 신고인지, OS가 검증하는지 미정.

**결정 필요 이유**: 잘못된 Capability 등록이 다른 HQ에게 그대로 추천되는 것을 방지.

**미결정 시 문제**: "할 수 있다고 등록했지만 실제로는 안 되는" HQ가 걸러지지 않음.

---

## ADC-12. Connector 자격증명 관리 책임

**상태**: Open · **우선순위**: LATER

**충돌 내용**: Connector의 인증정보·접근권한 관리 주체가 OS/HQ/외부 제공자 중 무엇인지 미정. ADC-03(위치) 결정 이후에 의미가 있는 질문.

**결정 필요 이유**: 자격증명 관리 소홀은 보안 사고로 직결.

**미결정 시 문제**: Connector별 임시 자격증명 관리 방식이 난립.

---

## 요약

| ID | 제목 | 상태 | 우선순위 |
|---|---|---|---|
| ADC-01 | Model ↔ Component 대응 관계 | Open | NEXT |
| ADC-02 | Runtime 개념의 존폐 | Open | NOW |
| ADC-03 | Connector(MCP) 아키텍처 위치 | Open | NEXT |
| ADC-04 | Observability/Audit 소속 Component | Open | LATER |
| ADC-05 | Fault Event 배달 보장 수준 | Open | NEXT |
| ADC-06 | Lifecycle State 전환 권한 경로 | Open | NEXT |
| ADC-07 | Resource(Token 예산) 이중 소속 | Open | NEXT |
| ADC-08 | Task/Event Flow 배달 보장 차등화 | Open | NEXT |
| ADC-09 | Workflow 그래프의 의미론적 경계 | Open | NOW |
| ADC-10 | Policy 규칙의 출처 분리 | Open | NOW |
| ADC-11 | Capability 선언의 신뢰 검증 책임 | Open | LATER |
| ADC-12 | Connector 자격증명 관리 책임 | Open | LATER |
