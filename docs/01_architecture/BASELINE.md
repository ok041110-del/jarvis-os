# Jarvis OS Architecture Baseline v1.0

## 1. Purpose

Jarvis OS는 AI Organization Operating System이다. Jarvis OS는 단일 AI Agent가 아니라, 여러 HQ(업무 영역)를 실행하고 관리하는 운영체제를 제공한다. 이 문서는 Jarvis OS와 그 위에서 동작할 모든 HQ가 공통으로 따라야 할 Architecture 기준선을 정의한다.

## 2. Vision

기존 소프트웨어는 사람을 위한 운영체제를 제공한다. Jarvis OS는 AI 조직을 위한 운영체제를 제공한다.

사람이 애플리케이션을 실행하듯, Jarvis OS는 HQ를 실행한다. 각 HQ는 독립적으로 업무를 수행하면서도, 공통된 철학과 시스템 위에서 협업한다.

Jarvis OS는 사람 조직을 흉내 내는 프로젝트가 아니다. AI Organization을 위한 Operating System이다.

## 3. Core Principles

- AI Native First — 모든 설계는 AI를 중심으로 한다.
- Workflow First — 조직 구조보다 Workflow가 우선한다.
- Engine Independent — 특정 AI 모델에 종속되지 않는다.
- Scalability — 1000개 이상의 Agent까지 확장 가능해야 한다.
- Composable HQ — 새로운 HQ는 기존 Architecture를 재사용하여 생성할 수 있어야 한다.
- Everything is Replaceable — 모든 Engine, Agent, Workflow는 교체 가능해야 한다.
- Long-term Memory — 모든 HQ는 장기 기억을 공유할 수 있어야 한다.
- Automation by Default — 사람의 개입보다 자동화를 우선한다.
- Simple > Complex — 복잡한 설계보다 단순한 설계를 우선한다.
- Abstraction over Implementation — 구현보다 추상화를 먼저 설계한다.

## 4. Architecture Philosophy

- **AI Native**: Jarvis OS의 모든 구성요소는 AI Agent의 실행을 전제로 설계된다.
- **Multi-HQ**: Jarvis OS는 하나의 조직이 아니라 여러 독립적 HQ를 동시에 운영하는 것을 전제로 한다.
- **Engine Independent**: 어떤 AI Engine에도 종속되지 않는다. Engine은 교체 가능한 Port/Adapter로 다뤄진다.
- **Long-term Scalability**: 단기 구현 편의보다 장기 확장성을 우선한다.
- **Build < Integrate**: 직접 구현보다 기존 오픈소스 통합을 우선한다.
- **Reference Architecture**: 첫 번째 HQ(Development HQ)는 향후 모든 HQ가 따를 참조 구조가 되어야 하며, 특정 도메인에 종속된 설계를 포함하지 않는다.
- **Good Architecture Principle**: 좋은 Architecture는 모든 것을 미리 설계한 Architecture가 아니라, 필요한 것만 적절한 시점에 결정한 Architecture다.

## 5. Meta Architecture

```
Jarvis OS
↓
HQ
↓
Agent
↓
Connector (MCP)
```

Division과 Team은 이 계층에 포함되지 않는다. Division과 Team은 HQ 내부에서 선택적으로 사용할 수 있는 구조이며, Jarvis OS는 그 존재 여부를 알지 못한다.

## 6. Concept Model

| 분류 | Concept |
|---|---|
| Entity | HQ, Agent, Principal |
| Definition | Workflow |
| Process | Task |
| Event | Event, Fault |
| Service | Runtime, Memory, Registry |
| Interface | Engine Port, Adapter, Message |
| Metadata | Capability, Artifact |
| Policy | Policy |
| State | Context, Lifecycle State |
| Resource | Resource |

**Concept 간 관계**

```
Principal는 Task를 요청한다.
HQ는 Capability를 Registry에 등록한다.
Agent는 HQ에 소속되며 Capability를 가진다.
Workflow는 Task들의 실행 순서(그래프)를 정의한다.
Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다.
Task는 Engine Port를 통해 실제 연산을 수행하고, 완료 시 Artifact를 생성한다.
Task는 실패 시 Fault를 발생시키고, Fault는 Event로 전파된다.
Event는 HQ 경계를 가로질러(Event Flow) 전파된다.
Task는 HQ 계층을 따라(Task Flow) 수직으로 흐른다.
Policy는 모든 Task/Event에 대해 PDP/PEP로 평가한다.
Memory는 Context를 HQ 네임스페이스 안에 영속화한다.
Context는 Task 실행 중에만 유효한 State다.
Registry는 HQ의 Capability를 통해 다른 HQ를 발견하게 한다.
HQ는 Lifecycle State를 가진다.
```

> Runtime은 Concept으로서 Baseline에 유지되나, 그 세부 구조는 Open Decision이다 (ADC-02). → `docs/03_adc/ADC.md` 참조.

## 7. System Boundary

**Jarvis OS의 책임**

- HQ/Agent의 등록과 발견(Registry)
- HQ의 생명주기 관리 및 상태 전환 통제
- Task/Event의 전달
- Engine 호출의 표준 인터페이스 제공 (Port/Adapter)
- Context/Artifact 저장을 위한 인프라 제공
- 모든 요청에 대한 승인/거부 판정(Policy) 메커니즘 제공
- 물리 자원 및 실행 예산의 배분
- 실패의 관측 가능성 보장

**Jarvis OS가 책임지지 않는 것**

- Workflow의 도메인 내용
- Agent가 수행하는 업무의 Prompt 및 로직 내용
- HQ 내부 조직 구조 (Division/Team의 존재 여부, 이름, 책임 분담)
- 도메인 특화 비즈니스 규칙
- Capability의 내부 구현 방식
- 개별 작업 결과의 품질 및 정확성

**HQ의 책임**

- Workflow의 정의(내용)
- 내부 조직 구조 결정
- Agent 구성 및 역할 결정
- 도메인 특화 비즈니스 규칙 적용
- Capability 내용 작성 및 정직한 등록

**Agent의 책임**

- 배분된 Task의 실제 수행
- Task 실행 중 Context 생성

## 8. Architecture Governance

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` 참조.

## 9. Open Decisions

Open Decision의 상세 내용은 본 문서에 기록하지 않는다. 전체 목록과 상태는 `docs/03_adc/ADC.md`를 참조한다.

## 10. Out of Scope

- Kernel Architecture
- Component Design (Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)
- Workflow Runtime 내부 구조
- Development HQ 내부 설계
- Implementation

## 11. Kernel

> 근거: `docs/architecture/core/RFC-0002-kernel-definition.md` §8·§9·§10,
> `docs/architecture/core/ADC-0002-kernel-definition.md` 판단 4,
> `docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md`

**Kernel은 모든 HQ가 공통으로 필요로 하지만 어느 HQ에도 속하지 않는 책임(Common Responsibility)을 담당하는 계층이다.**

Kernel은 다음이 아니다.

- Kernel은 Component가 아니다.
- Kernel은 Framework가 아니다.
- Kernel은 Runtime이 아니다.
- Kernel은 Scheduler가 아니다.
- Kernel은 Registry가 아니다.
- Kernel은 Event Bus가 아니다.

**Kernel과 Component의 관계**: Kernel은 책임을 가진다. Component는 그 책임을 구현하는 방법이다.

| Kernel 책임 | 구현 후보 |
|---|---|
| Task 전달 책임 | Scheduler |
| Capability 탐색 책임 | Registry |
| Engine 호출 책임 | Engine Gateway |
| Context 전달 책임 | Memory |

> 위 표의 Component는 **예시이며, 채택 여부는 결정되지 않았다.** 각 책임이 실제로 Kernel에 속하는지는 개별 RFC로 판단한다.

**핵심 원칙**: Kernel은 구현으로 정의하지 않는다. 책임으로 정의한다.

**Kernel Architecture와 Component Design(Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)은 여전히 §10 Out of Scope다.** 이 절은 Kernel이 무엇인지를 정의할 뿐, Kernel을 설계하지 않는다.

> 용어: "Core"는 Kernel의 이전 명칭이며 동일한 것을 가리킨다. 공식 용어는 Kernel이다 (ADR-0002).

## 12. Kernel Design Principles

> 근거: `docs/architecture/core/RFC-0002-kernel-definition.md` §11,
> `docs/architecture/core/ADC-0002-kernel-definition.md` 판단 1

이 원칙들은 Development HQ, Runtime, Memory, Agent 등 **모든 하위 설계가 공통으로 참조하는 최상위 설계 원칙**이다.

| ID | 원칙 | 내용 |
|---|---|---|
| KP-1 | Responsibility over Component | Kernel은 구현 객체가 아니라 책임 경계(Responsibility Boundary)다. |
| KP-2 | Deterministic Context Assembly | 동일한 입력은 항상 동일한 Context를 구성해야 한다. |
| KP-3 | Stable Context Ordering | Context는 항상 동일한 순서로 조립되어야 한다. |
| KP-4 | Stable Context by Design | Kernel은 결정론적이고 안정적이며 재사용 가능한 Context 구조를 만들어내도록 설계된다. Prompt Caching과 같은 최적화는 그 설계의 **결과이지 목적이 아니다.** |
| KP-5 | Implementation Agnostic | Kernel은 특정 모델(Claude, GPT, Gemini 등)이나 특정 Runtime에 종속되지 않는다. |
| KP-6 | Stateless Responsibility Boundary | Kernel은 책임을 정의하지만, 특정 구현체의 내부 상태를 강제하지 않는다. |

KP-4의 인과 방향은 한쪽으로만 성립한다: 안정적인 Context 구조를 설계한다(목적) → 그 결과로 Prompt Cache 등 최적화가 가능해진다(결과). 역방향은 성립하지 않는다.

## 13. Version

| 항목 | 내용 |
|---|---|
| Version | v1.1 |
| Status | Active |
| Architecture State | Frozen |

**변경 이력**

| Version | 내용 |
|---|---|
| v1.1 | Kernel 정의(§11)와 Kernel Design Principles(§12) 추가. Core → Kernel 용어 통합. 근거: ADR-0002 |
| v1.0 | 최초 Baseline (Frozen) |
