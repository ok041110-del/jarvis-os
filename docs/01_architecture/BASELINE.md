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

## 13. Kernel Context Model

> 근거: `docs/architecture/core/RFC-0003-kernel-context-model.md`,
> `docs/architecture/core/ADC-0003-kernel-context-model.md` 판단 1·2·3·5·6a,
> `docs/04_adr/ADR-0003-kernel-context-model-baseline.md`

§11이 Kernel이 **무엇인지**를, §12가 Kernel이 **어떻게 설계되어야
하는지**를 정의했다면, 이 절은 그 원칙이 적용되는 **대상**을 정의한다.

**Kernel Context는 Prompt 이전에 존재한다. Prompt는 그 결과물 중 하나다.**

### 13.1 Kernel Context Model

```
Context
├── Context Identifier          (이 Context를 무엇이라 부르는가)
├── Context Metadata            (이 Context에 대한 서술)
└── Context Segment  [ordered]  (Context를 이루는 최소 단위)
    ├── Context Identifier
    ├── Context Source          (이 Segment가 어디에서 왔는가)
    ├── Content                 (Kernel이 해석하지 않는 불투명한 값)
    ├── Context Metadata
    └── Order Key               (이 Segment가 어디에 놓이는가)
```

| 요소 | 정의 |
|---|---|
| Context | 순서가 정해진 유한한 Context Segment 열과 그 Identifier·Metadata. **값(Value)이며 서비스가 아니다** — 조립된 뒤 변경되지 않는다. |
| Context Segment | Kernel이 독립적으로 식별·정렬·포함/제외할 수 있는 Context의 최소 단위. |
| Context Source | Segment가 어디에서 왔는가를 식별하는 값. Kernel은 이를 **비교**할 뿐 해석하지 않는다. |
| Context Metadata | Segment 또는 Context **에 대한** 서술. 문자열 키-값의 순서 없는 집합. |
| Context Identifier | Context 또는 Segment의 동일성 판정 기준. |

**Model 제약 (4건)**

| ID | 제약 | 근거 |
|---|---|---|
| CM-1 | Segment에 **계층·안정성 분류 필드를 두지 않는다.** | 4-Layer Context Model은 Defer 상태다(§13.6) |
| CM-2 | Model에 **Engine 종속 요소를 두지 않는다**(role, token 수, cache key 등). | KP-5 |
| CM-3 | Kernel은 **Identifier와 시각을 스스로 생성하지 않는다.** 호출자가 주입하거나 결정론적으로 파생한다. | KP-6 |
| CM-4 | Kernel은 **Content와 Source를 해석하지 않는다.** | §7(도메인 내용은 Jarvis OS 책임 아님) |

> **§6 Concept Model과의 관계**: §6의 Context("Task 실행 중에만 유효한
> 임시 State")와 이름이 겹친다. Kernel Context는 §6 Context의
> **구체화(refinement)이며, §6을 재정의하지 않는다** — §6이 "무엇인가"를
> 말했고, 이 절은 "무엇으로 구성되는가"를 말한다. 영속화(Memory)는 이
> 절의 범위가 아니다.

### 13.2 Context Builder 책임

Kernel Context를 만드는 책임은 4개다. 이 절은 **책임을 정의할 뿐 어떤
Component가 구현할지는 정하지 않는다**(KP-1).

| 책임 | 내용 | 하지 않는 것 |
|---|---|---|
| 수집(Collect) | 하나 이상의 Context Source로부터 Segment를 모은다. | Source를 **발견**하지 않는다 — 어떤 Source를 볼지는 호출자가 정한다. |
| 검증(Validate) | **구조 불변식만** 검사한다(Identifier 존재·유일성, Source 존재, Order Key 비교 가능성). | 내용의 사실 여부·관련성·품질·토큰 예산을 검사하지 않는다. 어긋나면 조용히 통과시키지 않는다(No Silent Failure). |
| 병합(Merge) | 복수 Source의 Segment 집합을 합친다. 같은 Identifier + 같은 Content는 중복 제거하고, **같은 Identifier + 다른 Content는 오류**다. | Content를 합치거나 요약하지 않는다. Segment 경계를 무너뜨리지 않는다. |
| 정렬(Order) | Segment 집합에 **전순서**를 부여한다. | — |

**정렬의 핵심 조건**: **Ordering Policy는 Builder의 입력이며, Model에
박힌 분류가 아니다.** 순서 규칙이 Model 안에 들어가면 그것이 곧 계층
분류가 되어 CM-1을 위반한다. 이 외부화 덕분에, 훗날 계층 분류가
확정되더라도 그것은 **하나의 Ordering Policy로** 들어올 뿐 Model은
바뀌지 않는다.

### 13.3 Assembly 불변식

Assembly는 검증되고 정렬된 Segment 열을 하나의 Kernel Context 값으로
확정하는 단계다.

| ID | 불변식 |
|---|---|
| A-1 | Segment Content는 조립 과정에서 한 글자도 바뀌지 않는다. |
| A-2 | Segment가 조용히 추가되거나 사라지지 않는다. |
| A-3 | 입력 Segment는 조립 후에도 변경되지 않는다. 결과는 새 값이다. |
| A-4 | 조립은 시계·난수·외부 I/O를 읽지 않는다. |
| A-5 | 같은 입력 + 같은 Policy → 같은 Context. |

**KP-2의 구체화**: **Assembly의 입력은 (Segment 집합, Ordering Policy)
둘뿐이다.** 호출 시각, 호출 순서, 프로세스 상태, 환경 변수는 결과에
영향을 주지 않는다. 이 진술이 있어야 KP-2를 테스트할 수 있다.

**KP-3의 구체화 — Stable Ordering**

| ID | 요구 |
|---|---|
| O-1 | 순서는 **전순서**여야 한다. 부분 순서는 KP-3을 만족하지 않는다. |
| O-2 | 동률이 남으면 결정론이 깨진다. 유일한 Identifier를 최종 tie-break로 사용한다. |
| O-3 | 순서는 선언된 Order Key에서 나오며, **수집 순서·해시 순회 순서·삽입 순서에서 나오지 않는다.** |
| O-4 | 순서 규칙은 Policy로 명시되며 코드에 암묵적으로 흩어지지 않는다. |

### 13.4 Prompt는 Output Format이다

```
Kernel Context   (Canonical — 정본)
        │
        ├── Renderer A ──▶ Claude Prompt      (표현)
        ├── Renderer B ──▶ GPT Prompt         (표현)
        └── Renderer C ──▶ Gemini Prompt      (표현)
```

- Kernel Context가 정본이고 **Prompt는 파생물이다.** 역방향(Prompt →
  Context)은 정의하지 않는다.
- Claude / GPT / Gemini Prompt는 **동일한 Kernel Context의 서로 다른
  표현**이다.
- 어떤 Engine이 무엇을 요구하든 그것은 Renderer가 흡수한다 — Prompt가
  Model의 형태를 바꾸지 않는다(KP-5).

**Renderer 계약**

| ID | 계약 |
|---|---|
| R-1 | Renderer는 순수하며 결정론적이다. |
| R-2 | Renderer는 Kernel Context를 변경하지 않는다. |
| R-4 | Renderer가 덧붙이는 것은 고정된 구조 틀뿐이며, Context에 없는 내용을 만들어내지 않는다. |
| R-5 | Engine 고유 개념(role, 메시지 배열, 캐시 지시자 등)은 Renderer 안에서만 존재한다. Model에 새지 않는다. |

> **R-3의 부재는 누락이 아니다.** RFC-0003 §5.3이 제안한 R-3
> ("Renderer는 Segment 순서를 재배치하지 않는다")은 기존 Execution
> Layer 구현(MVP-0002 `RENDERING_MAP`)과 충돌하며 코드 재설계를
> 수반하므로, ADC-0003 판단 5가 **Accept 범위에서 의도적으로
> 제외**했다. 채택하려면 별도 RFC가 필요하다.

### 13.5 Kernel과 HQ의 Context 책임 배치

| 주체 | 책임 |
|---|---|
| HQ | **무엇이 Context에 들어가야 하는가**를 정한다. Source를 선언하고 Segment의 Content를 제공한다. |
| Kernel | **그것이 어떻게 식별·검증·병합·정렬·조립·표현되는가**를 담당한다. |

HQ는 Prompt를 만들지 않는다. 이 배치는 새로 만드는 것이 아니라 §7과
`development-hq/BOUNDARY.md`(Frozen)를 Context 영역에 그대로 적용한
것이다.

### 13.6 이 절이 결정하지 않는 것 (Defer)

Freeze 원칙에 따라, 미결 사항을 같은 자리에 명시한다.

| 항목 | 상태 | 근거 |
|---|---|---|
| 4-Layer Context Model (Immutable/Stable/Working/Ephemeral) | **Defer** | ADC-0002 판단 2b |
| Context Identifier 파생 규칙(주입/해시/그 외) | **Defer** | ADC-0003 판단 1b |
| Context Boundary의 확정 형태 | **Defer** (Kernel 책임 후보 지위는 유지) | ADC-0003 판단 4, ADC-0002 판단 2a |
| Engine별 Renderer(Claude/GPT/Gemini) | **Defer** | ADC-0003 판단 5b |
| R-3 (Renderer의 순서 재배치 금지) | **미채택** (Reject 아님) | ADC-0003 판단 5 |
| 활용 사례(Prompt Cache / Conversation Resume / Context Snapshot / Memory Restore) 및 실제 HQ 통합 | **Defer** | ADC-0003 판단 6b |

위 6건 중 3건(Context Boundary, Engine별 Renderer, 활용 사례·실제
통합)의 재검토 조건은 **실제 Engine 호출이 최소 1회 관찰되는 것**으로
동일하다.

**Kernel Architecture와 Component Design은 여전히 §10 Out of Scope다.**
이 절은 Kernel이 무엇을 관리하는지를 정의할 뿐, 그것을 관리할
Component를 설계하지 않는다(KP-1).

## 14. Kernel Public Contract (Context 영역)

> 근거: `docs/architecture/core/RFC-0004-kernel-public-contract.md`,
> `docs/architecture/core/ADC-0004-kernel-public-contract.md` 판단 1~8,
> `docs/04_adr/ADR-0004-kernel-public-contract-baseline.md`

§11이 Kernel이 **무엇인지**, §12가 **어떻게 설계되어야 하는지**, §13이
**무엇을 관리하는지**를 정의했다면, 이 절은 Kernel이 **외부에 무엇을
보장하는지**를 정의한다.

**이 계약은 API가 아니다.** 함수·자료형·프로토콜·직렬화 형식을
정의하지 않는다. API는 이 계약을 구현하는 다음 단계다 — 계약이 위에
있고 API가 아래에 있다(KP-1).

### 14.1 계약의 범위

**이 계약은 Kernel 전체가 아니라 Context 영역에 한정된다.** 계약은
결정된 만큼만 존재한다.

| RFC-0002 §15의 Kernel 책임 후보 | 현재 상태 |
|---|---|
| 1. Task 전달 책임 | **미결** — 이 계약의 범위 밖 |
| 2. Capability 탐색 책임 | **미결** — 이 계약의 범위 밖 |
| 3. Engine 호출 책임 | **미결** — 이 계약의 범위 밖 |
| 4. Context 전달 책임 | 결정됨 (§13) |
| 5. Stable Prefix 책임 | 후보. 형태는 Defer(§13.6) |
| 6. Context Boundary 책임 | 후보. 형태는 Defer(§13.6) |
| 7. Context Assembly 책임 | 결정됨 (§13.3) |
| 8. Context Ordering 책임 | 결정됨 (§13.2·§13.3) |

1~3이 각각 판단되면 그때 이 계약이 확장된다.

**계약의 수신자**: Development HQ(`BOUNDARY.md`), Execution Layer
(Kernel Module로 Accept됨), 그리고 §3 "Composable HQ"·§4 "Reference
Architecture"에 따라 미래의 모든 HQ. 다만 미래 HQ가 아직 존재하지
않으므로, 이 계약이 그들에게도 충분한지는 **검증된 바 없다.**

### 14.2 Public Responsibilities — 외부가 Kernel에 요구할 수 있는 것

| ID | 책임 | 내용 |
|---|---|---|
| PR-1 | **Kernel Context 제공** | 외부가 제공한 Segment와 Ordering Policy로부터 조립된 Kernel Context를 값으로 돌려준다. |
| PR-2 | **Context Assembly** | A-1~A-5 불변식과 O-1~O-4 순서 요구를 만족하는 조립을 수행한다(§13.3). |
| PR-3 | **Context Validation** | 구조 불변식을 검증하고, 위반을 드러낸다(§13.2). |
| PR-4 | **Context Rendering 계약 제공** | Kernel Context를 표현으로 변환하는 **계약(R-1·R-2·R-4·R-5)을 보장한다**(§13.4). |

**PR-1의 "제공"은 "내용을 마련한다"는 뜻이 아니다.** Kernel은 완성된
Context를 **돌려줄** 뿐, 무엇이 Context에 들어가야 하는지는 HQ가
정한다(§13.5, CM-4). 이 구분이 무너지면 §7과
`development-hq/BOUNDARY.md`가 동시에 무너진다.

**PR-4는 Renderer를 제공하지 않는다.** Kernel이 보장하는 것은 Renderer
계약이며, Claude/GPT/Gemini Renderer는 Defer 상태다(§13.6). "계약
제공"과 "Renderer 제공"은 다르다.

**이 4개는 §13.2의 Kernel 책임 4개(수집·검증·병합·정렬)와 다른
목록이며, 그것을 대체하지 않는다.** §13.2는 *Kernel 책임*을 정의하고,
이 표는 *외부가 요청할 수 있는 것*을 정의한다. 수집·병합·정렬은 Kernel
책임이지만 Public Surface가 아니다 — 외부는 그 단계가 아니라 결과
(G-2·G-6)를 관찰한다.

### 14.3 Public Guarantees — 외부가 의존해도 되는 성질

깨지면 계약 위반이다. **확인할 수 없는 보장은 계약이 아니라 선언이므로,
외부의 확인 방법을 함께 적는다.**

| ID | 보장 | 내용 | 외부의 확인 방법 |
|---|---|---|---|
| G-1 | **Deterministic** | 같은 (Segment 집합, Ordering Policy) → 같은 Kernel Context. 호출 시각·호출 순서·프로세스 상태·환경 변수는 결과에 영향을 주지 않는다(KP-2, §13.3). | 같은 입력으로 두 번 호출해 결과를 비교 |
| G-2 | **Stable Ordering** | 순서는 전순서이며 선언된 Order Key에서 나온다. 동률은 Identifier로 해소된다(KP-3, O-1~O-4). | 입력 Segment의 제시 순서를 섞어도 결과 순서가 동일한지 확인 |
| G-3 | **Engine Agnostic** | Kernel Context에는 특정 Engine에만 의미가 있는 요소가 존재하지 않는다(KP-5, CM-2, R-5). | Context에서 role·token 수·cache key 등이 발견되지 않는지 확인 |
| G-4 | **Implementation Agnostic** | Kernel은 호출자의 Runtime·언어·저장소·실행 방식을 강제하지 않는다(KP-1, KP-5). | **관찰로 확인할 수 없다** — 아래 참조 |
| G-5 | **Immutable Inputs** | 외부가 넘긴 Segment는 변경되지 않는다. 반환된 Kernel Context도 변경되지 않는다(A-1, A-3, R-2). | 호출 전후 입력값을 비교 |
| G-6 | **No Silent Failure** | 구조 불변식 위반과 병합 충돌은 조용히 넘어가지 않는다(§13.2). | 규칙을 어긴 입력이 거부되는지 확인 |
| G-7 | **Stateless Boundary** | **Context 경로에 한하여**, Kernel은 호출 간 상태를 갖지 않는다. 시계·난수를 읽지 않으며 Identifier·시각을 생성하지 않는다(CM-3, A-4). | 호출 순서를 바꿔도 각 결과가 동일한지 확인 |

**G-4의 비대칭을 숨기지 않는다.** "강요하지 않는다"는 부정 명제이며
반례가 나타나야 위반이 드러난다. G-4는 검증이 아니라 **검토(Review)로만
지킬 수 있는 보장**이다.

**G-7의 범위가 Context 경로로 한정된 이유**: KP-6의 문언은 *"Kernel은
책임을 정의하지만 특정 구현체의 내부 상태를 강제하지 않는다"*이며,
"Kernel이 상태를 갖지 않는다"와 같은 말이 아니다. 실제로 Kernel
Module로 Accept된 Governance는 문서의 등록과 상태를 다룬다. **G-7을
Kernel 전체에 적용하면 그 결정과 충돌한다.** Context 경로 안에서는
CM-3·A-4가 근거를 제공한다.

### 14.4 Hidden Responsibilities — 외부가 의존해서는 안 되는 것

> **Hidden의 효력**: Hidden에 의존한 코드가 Kernel 변경으로 깨지는 것은
> **계약 위반이 아니다.** 이 문장이 이 목록의 존재 이유다.

| ID | 항목 | 왜 숨기는가 |
|---|---|---|
| H-1 | Ordering Policy의 구현 | 외부가 보장받는 것은 G-2이지 Order Key의 계산 방법이 아니다. |
| H-2 | Builder 내부 구조 | 수집·검증·병합·정렬의 단계 분할과 실행 순서. 외부가 보장받는 것은 PR-1의 결과와 G-1~G-7이다. |
| H-3 | Metadata의 **내부 표현** 방식 | §13.1은 "문자열 키-값의 순서 없는 집합"이라는 성질만 정의했다. 영속화는 Hidden이 아니라 Non-Goal이다(N-4). |
| H-4 | Renderer 내부 구현 | 외부가 보장받는 것은 R-1·R-2·R-4·R-5다. |
| H-5 | Context Identifier 파생 규칙 | **Defer 상태다**(§13.6). 미결을 Public에 두면 외부가 미결에 의존하게 된다. |
| H-6 | Segment의 자료구조·직렬화 형식 | 미결 사항이다. |

**Hidden과 Extension Point에 같은 항목이 나오는 것은 모순이 아니다** —
층이 다르다.

| 층 | 공개 여부 |
|---|---|
| 그 지점이 **교체 가능하다는 사실** | **Public** (§14.5) |
| 그 지점이 **무엇을 지켜야 하는가**(계약) | **Public** (§13.4, §13.2) |
| 그 지점의 **구현 내용** | **Hidden** (H-1, H-4) |

즉 **계약은 공개하고 구현은 숨긴다.**

### 14.5 Extension Points — 교체 가능하다고 선언된 지점

> **이것은 플러그인 메커니즘이 아니다.** 등록·발견·로딩·버전 협상
> 방식은 Component Design이며 §10 Out of Scope다. 이 절이 정의하는
> 것은 **"여기가 교체 지점이다"라는 계약상의 선언**뿐이다.

| ID | 확장 지점 | 무엇을 교체하는가 | 지켜야 할 계약 |
|---|---|---|---|
| X-1 | **Renderer** | Kernel Context를 어떤 표현으로 내보낼 것인가 | R-1·R-2·R-4·R-5 |
| X-2 | **Ordering Policy** | Segment의 Order Key를 어떻게 정할 것인가 | O-1~O-4, G-1 |
| X-3 | **Context Source** | 무엇이 Context에 들어가는가. **플러그인이 아니라 계약의 입력 경계다.** | CM-4 |
| X-4 | **Future Context Model** | Context 구성 요소의 확장. **확장이 들어올 자리의 표시이며, 확장이 일어난다는 예고가 아니다.** | CM-1~CM-4 |

**X-4의 의미**: §13.6이 Defer로 남긴 것들이 훗날 확정될 경우 들어올
자리를 계약 안에 표시해 둔 것이다. 예컨대 4-Layer Context Model이
확정되면 그것은 **하나의 Ordering Policy(X-2)로** 들어오며, Model
(§13.1)도 이 계약의 Public 항목도 바뀌지 않는다. **그 확정 여부 자체는
여전히 미결이다.**

X-1~X-4는 §3 "Everything is Replaceable"(v1.0부터 Frozen)을 Context
영역에 적용한 것이며 새 원칙이 아니다.

**확장의 위험**: 잘못 만든 Renderer나 Ordering Policy는 G-1을 깨뜨릴
수 있다(예: 시각을 읽는 Ordering Policy). 이 계약은 그 위험을
**계약으로만** 다룬다 — 지키지 않은 확장은 Kernel의 보장 밖이다.
**강제·탐지 메커니즘은 Defer다**(§14.7).

### 14.6 Explicit Non-Goals — Kernel이 하지 않는 것

> **Non-Goal은 "이 계약이 그 Component를 제공하지 않는다"는 뜻이지,
> "그 책임이 Kernel에 속하지 않는다"는 뜻이 아니다.** KP-1이 이 구분을
> 요구한다 — Kernel은 책임을 갖고, Component는 그 책임을 구현하는
> 방법이다. 아래는 전부 **Component 수준의 선언**이다.

| ID | Non-Goal | 제공하지 않는 것 | 이것이 닫지 **않는** 질문 |
|---|---|---|---|
| N-1 | Runtime 관리 | Workflow 실행, Task 인스턴스 관리 | "Runtime 개념이 존치하는가"(ADC-02, **Open**) |
| N-2 | Scheduler 구현 | Task 배분·순서 결정 Component | "Task 전달 책임이 Kernel에 속하는가"(RFC-0002 §15-1, **미결**) |
| N-3 | Agent 관리 | Agent의 생성·구성·실행 | 없음 — §7이 이미 HQ 책임으로 확정 |
| N-4 | Memory Service 구현 | Context의 영속화·복원 | "Memory Module이 필요한가"(**Defer**) |
| N-5 | 내용 품질 판단 | Context 내용의 사실성·관련성·품질 평가 | 없음 — §7, §13.2가 이미 확정 |
| N-6 | 도메인 내용 선정 | 무엇이 Context에 들어가야 하는지 결정 | 없음 — §13.5, CM-4가 이미 확정 |

**"닫지 않는 질문" 열은 필수다.** 이 열이 없으면 이 표는 시간이
지나면서 미결 사안을 조용히 닫는 문서가 된다.

### 14.7 계약의 변경 규칙과 미결 항목

| 대상 | 변경 시 필요한 절차 |
|---|---|
| Public — PR-*, G-*, X-*의 존재와 그 계약 | **RFC → ADC → ADR → Baseline**(`ARCHITECTURE_GOVERNANCE.md`) |
| Hidden — H-*의 내용 | 절차 없이 변경 가능. 외부는 여기에 의존하지 않기로 되어 있다(§14.4) |

**이 절이 결정하지 않는 것 (Defer)**

| 항목 | 상태 | 재검토 조건 |
|---|---|---|
| Extension Point의 메커니즘(등록·발견·로딩·검증) | **Defer** | 두 번째 Renderer 또는 두 번째 Ordering Policy가 실제로 필요해지는 시점 |
| Contract Versioning 체계 | **Defer** | 계약이 실제로 변경되어 호환성 문제가 관찰되는 시점 |

**다음 단계**: Kernel API — 이 계약을 어떤 인터페이스로 제공할
것인가. 이 절은 API를 정의하지 않는다.

§13.6의 Defer 6건은 여기서 다시 나열하지 않는다 — §13.6을 참조한다
(Single Source of Truth).

**Kernel Architecture와 Component Design은 여전히 §10 Out of Scope다.**
이 절은 어떤 Component도 정의하지 않는다(KP-1).

## 15. Version

| 항목 | 내용 |
|---|---|
| Version | v1.3 |
| Status | Active |
| Architecture State | Frozen |

**변경 이력**

| Version | 내용 |
|---|---|
| v1.3 | Kernel Public Contract(§14) 추가 — 계약 범위, Public Responsibilities, Public Guarantees, Hidden Responsibilities, Extension Points, Explicit Non-Goals, 변경 규칙. 기존 §14 Version → §15. 근거: ADR-0004 |
| v1.2 | Kernel Context Model(§13) 추가 — Model 5개 요소, Builder 4개 책임, Assembly 불변식, Prompt Output Format, HQ 책임 배치. 기존 §13 Version → §14. 근거: ADR-0003 |
| v1.1 | Kernel 정의(§11)와 Kernel Design Principles(§12) 추가. Core → Kernel 용어 통합. 근거: ADR-0002 |
| v1.0 | 최초 Baseline (Frozen) |
