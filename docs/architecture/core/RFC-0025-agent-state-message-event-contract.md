# RFC-0025: Agent State / Message / Event Contract — 최소 범위 Boundary Question (Multi-Agent 운영 대비 Phase B)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §6(Concept Model: State/Event/Interface),
§11(Kernel은 Event Bus가 아니다), §14.1(Kernel 책임 후보 표 — Event/Message
전달 책임이 아예 후보로도 등재되지 않음), `docs/decisions/adc/ADC.md`
ADC-05(Fault Event 배달 보장 수준, Open)·ADC-08(Task/Event Flow 배달
보장 차등화, Open), `hqs/development/IMPLEMENTATION_RULES.md`(Event Bus
구현 금지), `docs/architecture/core/RFC-0024-agent-domain-and-lifecycle-contract.md`·
`docs/architecture/core/ADC-0032-agent-domain-and-lifecycle-contract-resolution.md`
(Phase A — Agent Domain/Lifecycle **Not Accept, Defer**).

**Evidence**: 위 문서 전체, `docs/00_governance/GLOSSARY.md`(Message/Event/
Fault/Runtime 행), `docs/architecture/core/RFC-0018-*`(Conversation
Layer Boundary Question의 절차 관행 — 이름·Component를 전제하지 않고
질문만 여는 방식), `docs/architecture/baseline/BASELINE.md` §13.1
Kernel Context Model(Context Identifier/Context Source 개념 — 이 RFC가
"Correlation"·"Identity" 후보를 설계할 때 참고하는 기존 패턴). **새로운
실험·프로토타입·측정은 수행하지 않는다.**

> 이 RFC는 Phase A(`RFC-0024`/`ADC-0032`)의 결과를 **전제**로 삼는다 —
> Agent Domain Model과 Agent Lifecycle State Model은 **채택되지
>않았다(Not Accept, Defer)**. 이 RFC는 그 Defer를 우회하거나, Agent
> State Contract를 근거로 Domain/Lifecycle을 사실상 재확정하지 않는다.
> Agent State는 Lifecycle State(`RFC-0024` §5의 REGISTERED→ASSIGNED→…)와
> **다른 개념**으로 다룬다(§4 참조) — 후자는 여전히 Deferred다.
>
> **이 RFC는 Baseline/Contract를 변경하지 않는다.** Runtime, Event
> Bus, Scheduler, Registry, LangGraph, Workflow Engine — 어느 것도
> 구현하지 않는다. State/Message/Event의 **의미적 경계**만 Candidate로
> 제안하고, 채택 여부·Baseline 반영 여부는 후속 ADC로 위임한다.

---

## 0. 이 RFC가 열린 이유

`ADC-0032`는 Agent Domain·Lifecycle을 Defer하면서 재검토 Trigger 4건을
남겼다(§Conditions 1~4). 그중 어느 것도 지금 충족되지 않았다 — 이 RFC는
그 Trigger를 충족시키려는 시도가 아니다. 대신, 사용자가 이번 세션에서
지정한 **Phase B**는 Agent Domain/Lifecycle과는 **독립적으로** 성립할
수 있는 다른 질문을 연다 — "Multi-Agent Runtime이 언젠가 존재하게 될
때, 그 Runtime이 Agent의 State를 읽고 Agent 사이의 통신을 전달하려면
최소한 어떤 의미적 어휘가 필요한가?" 이는 Agent 자신이 무엇으로
구성되는지(Domain, Phase A)의 질문이 아니라, **여러 Agent 사이에 무엇이
오가는지**(State 조회, Message/Event 전달)의 질문이며, `IMPLEMENTATION_RULES.md`가
이미 Event Bus·Runtime 구현을 금지하고 있으므로 여기서도 **구현이 아닌
경계 서술**만 다룬다.

## 1. Problem Statement

`BASELINE.md` §6 Concept Model은 이미 세 조각의 어휘를 갖고 있다.

- **State** 분류: "Context, Lifecycle State" — Agent에 대응하는 State는
  없다(Phase A로 확정).
- **Event** 엔티티: "Event는 HQ 경계를 가로질러(Event Flow) 전파된다."
- **Interface**: "Message" — `GLOSSARY.md`: "Task/Event가 공유하는 전달
  형식."

그러나 이 세 조각은 서로 다른 정밀도로 존재한다. Event/Message는
**이름과 한 문장의 관계**(Event는 Message로 전파된다, Task Flow는
수직·Event Flow는 수평)만 있을 뿐, **무엇을 담는지**(Envelope 형태),
**누가 보내고 받는지**(Agent 간 통신이 이 Flow에 포함되는지), **배달이
보장되는 수준**(ADC-05, ADC-08이 이미 수 년째 Open)이 전부 미정이다.
State는 아예 Agent 수준 대응물이 없다.

Multi-Agent Runtime(아직 존재하지 않음, ADC-02 Open)이 미래에 등장한다면,
그것이 "Agent가 지금 무엇을 하고 있는지"를 조회하고 "Agent A의 결과를
Agent B에게 전달"하려는 순간 이 공백과 충돌한다. 이 RFC는 그 미래
충돌을 예방하기 위해 지금 무엇을 정할 수 있고 무엇을 정할 수 없는지를
가른다.

## 2. Evidence Summary — 이미 기록된 것만 인용

### 2.1 이미 확정된 것 (Concept 존재, 세부는 미정)

| 근거 | 내용 |
|---|---|
| §6 Concept Model | State 분류에 "Context, Lifecycle State"만 등재. Event(Entity), Message(Interface) 별도 존재. |
| §6 관계 서술 | "Event는 HQ 경계를 가로질러(Event Flow) 전파된다." "Task는 HQ 계층을 따라(Task Flow) 수직으로 흐른다." |
| `GLOSSARY.md` | Message = "Task/Event가 공유하는 전달 형식." Event/Fault 행 존재, Envelope/Correlation/Identity/Payload/Time 행은 **없음**. |
| §11 | "Kernel은 Event Bus가 아니다." |
| `IMPLEMENTATION_RULES.md` | "Event Bus 구현 금지 — MVP는 단일 선형 Task Flow만 다루며 Event Flow를 쓰지 않는다." 무변경. |
| `ADC.md` ADC-05(Open, 우선순위 NEXT) | "Fault가 Task Flow 수준(at-least-once)으로 배달되는지, Event Flow 수준(best-effort)으로 배달되는지 미정." |
| `ADC.md` ADC-08(Open, 우선순위 NEXT) | "Task Flow(순서·무유실)와 Event Flow(도달 범위)가 실제로 다른 배달 보장 수준으로 구현되는지 미정." |
| `RFC-0024`/`ADC-0032` | Agent Domain Model·Agent Lifecycle State(REGISTERED→…) **Not Accept, Defer**. Agent Manager의 현재 허용 책임 범위 = **없음**. |

### 2.2 §14 Kernel Public Contract와의 관계 — 결정적 공백

`BASELINE.md` §14.1의 8개 Kernel 책임 후보 표(§14.1 계약의 범위)에는
"Task 전달 책임"·"Capability 탐색 책임"·"Engine 호출 책임"·"Context 전달
책임"·"Stable Prefix 책임"·"Context Boundary 책임"·"Context Assembly
책임"·"Context Ordering 책임" **8개만** 있다. **"Event 전달 책임"·"Message
전달 책임"은 이 표에 후보로조차 올라 있지 않다.** §6이 Event/Message를
Concept으로 이미 선언했음에도, §14 Public Contract 트랙에는 진입한 적이
없다는 뜻이다 — 즉 Event/Message는 §6에서는 "이미 있는 어휘"처럼
보이지만 §14 관점에서는 **완전한 백지 상태**다.

## 3. Gap Analysis

| 항목 | 현재 상태 | Gap |
|---|---|---|
| Agent State(의미적 값) | 없음(Phase A Defer) | Runtime이 조회할 대상 자체가 정의되지 않음 |
| State 소유권 | 없음 | 누가 쓰고 누가 읽는지 미정 |
| Event 존재 | §6 Concept("HQ 경계를 가로질러 전파") | **Agent 간** 전파인지 **HQ 간** 전파인지 구분 없음 — 원문은 HQ 경계만 명시 |
| Message 형식 | §6/GLOSSARY "Task/Event가 공유하는 전달 형식"(한 문장) | Envelope 필드(Identity/Type/Payload/Correlation/Time) 전무 |
| Message ↔ Event 구분 | Message는 "전달 형식", Event는 "내용물 중 하나" — 계층은 다르나 그 관계가 §14 Public Contract로 정련된 적 없음 | Agent↔Agent 통신이 Message인지 Event인지, 혹은 제3의 것인지 미정 |
| 배달 보장 수준 | ADC-05·ADC-08 **수 년째 Open** | 이 RFC로도 해소되지 않음(§7) |
| §14 Public Contract 편입 여부 | 후보로도 없음(§2.2) | Context처럼 결정된 적이 없는 완전 백지 |

## 4. Candidate — Agent State (최소 의미적 값, Lifecycle State와 구분)

> **Lifecycle State(`RFC-0024` §5)와의 구분**: Lifecycle State는 "Agent
> 인스턴스의 생애 단계"(REGISTERED→ASSIGNED→…)이며 **여전히 Defer
> 상태다.** 이 절이 다루는 "Agent State"는 **그보다 좁고 다른 것** —
> "지금 이 순간 Runtime(존재한다면)이 조회할 수 있는 불투명한 값 하나가
> 있다"는 존재 여부 자체의 질문이다. Lifecycle이 Accept되지 않았다고
> 이 존재 여부 질문 자체가 봉쇄되는 것은 아니다 — Kernel Context가
> "Content를 해석하지 않는" 것처럼(CM-4), 이 State도 **내용을
> 규정하지 않는 불투명 값** 후보로만 다룬다.

| Candidate | 정의(최소) |
|---|---|
| Agent State의 존재 | Agent 인스턴스마다 외부(Runtime 등)가 조회 가능한 불투명 값이 **있을 수 있다**는 자리(placeholder) — 그 값이 무엇을 담는지는 이 RFC가 정의하지 않는다(§13.1 Kernel Context의 Content를 다루지 않는 것과 동일한 절제). |
| State가 Lifecycle을 함의하는가 | **아니다.** Lifecycle Enum이 Defer이므로, State는 "Lifecycle 값 중 하나"로 정의될 수 없다 — 정의되면 Lifecycle을 사실상 재확정하는 우회가 된다(§9 명시 금지). |

**이 Candidate가 하지 않는 것**: State의 자료구조, 저장 위치, 조회
API를 정의하지 않는다. State가 실제로 존재해야 한다고 주장하지 않는다
— "존재한다면 이런 성질을 가져야 한다"는 조건부 서술이다.

## 5. Candidate — State 소유권과 변경 책임

> 사용자 지시대로, **현재 Governance에서 허용되지 않는 책임은 추가하지
> 않는다.** 아래 표는 새 권한을 부여하는 것이 아니라, 이미 확정/금지된
> 것을 State라는 새 대상에 그대로 적용한 결과다.

| 주체 | State를 소유(자기 값을 스스로 바꿈)할 수 있는가 | 근거 |
|---|---|---|
| **Agent** | **예 — 유일한 소유자 후보** | `BASELINE.md` §7 "배분된 Task의 실제 수행"·"Task 실행 중 Context 생성" — 자기 실행에 대한 사실상의 유일한 관찰자. v1 결정 2·`ADR-0011` A-OUT("전이 규칙을 재구현하지 않는다")과 동형 원칙 — 자기 상태는 자기가 소유한다. |
| **Agent Manager** | **아니오** | `ADC-0032` §Q4가 이미 확정: "현재 허용 범위는 없다(전무)." State를 대신 바꾸는 것은 Registry/Scheduler 금지 범위를 넘어서는 새 권한이 되므로 이 RFC가 부여할 수 없다. |
| **Runtime** | **아니오(현재는)** | Runtime의 세부 구조는 ADC-02(Open)이며, `IMPLEMENTATION_RULES.md`가 "넓은 Runtime(Workflow 참조, Agent 동적 배분) 구현 금지"를 유지한다. Runtime이 State를 **읽을 수 있는지**(조회)는 §4가 열어 두지만, **쓸 수 있는지**(변경)는 Agent 소유권 원칙과 충돌하므로 이 RFC는 Read-only 조회만 후보로 남긴다. |
| **Event Bus** | **아니오** | §11 "Kernel은 Event Bus가 아니다" + 구현 금지(`IMPLEMENTATION_RULES.md`). Event Bus 자체가 존재하지 않으므로 소유권 질문이 성립하지 않는다. |

**핵심 원칙(Candidate)**: **State는 Agent 자신만 변경하고, 그 외
주체(Agent Manager/Runtime/Event Bus)는 읽기만 가능하거나 아예 접근할
수 없다.** 이는 새 권한 창설이 아니라, Phase A의 "전이 규칙 재구현
금지" 원칙을 State 개념에도 일관 적용한 것이다.

## 6. Candidate — Agent↔Agent Message와 Event를 구분해야 하는가

### Boundary Question

§6 원문은 Event를 "**HQ** 경계를 가로질러 전파"되는 것으로만 서술한다
— **Agent 경계**를 가로지르는 통신(Agent A → Agent B, 같은 HQ 내부일
수도 있음)이 이 정의에 포함되는지는 원문이 답하지 않는다. 이는 이 RFC가
**결정하지 않는** 채로 여는 진짜 Boundary Question이다.

| 후보 | 설명 | 이 RFC의 입장 |
|---|---|---|
| (a) Agent↔Agent 통신 = 기존 Event Flow의 부분집합 | HQ 경계를 가로지르지 않는 Agent 간 통신도 "Event"로 취급 | Candidate — §6 "HQ 경계를 가로질러"라는 한정어와 문언상 충돌 가능성 있음 |
| (b) Agent↔Agent 통신 = 기존 Task Flow의 일부(HQ가 Task로 배분) | Agent가 직접 통신하지 않고, HQ/Runtime이 Task 배분으로 간접 연결 | Candidate — §7 "Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다"와 정합적이나, Runtime 자체가 ADC-02 Open이라 실체가 없음 |
| (c) 제3의 새 Flow(Agent Flow) | 기존 Task/Event Flow 어디에도 속하지 않는 새 개념 | Candidate — 가장 무겁다. §6 Concept Model에 새 관계 문장을 추가해야 하므로 Architecture Impact가 가장 큼 |

**이 RFC는 (a)/(b)/(c) 중 하나를 선택하지 않는다.** 셋 다 §6의 기존
문언을 다른 방식으로 확장해야 하며, 그 확장이 필요할 만큼의 실제
Agent 간 통신 사례가 아직 관찰되지 않았다(§7).

### Message vs Event 자체의 구분(선택과 무관하게 성립하는 관찰)

GLOSSARY 정의(Message = Task/Event가 공유하는 **전달 형식**)를 따르면
Message는 **봉투(Envelope)**, Event(또는 Task)는 **내용물의 한
종류**다. 이 관계는 (a)/(b)/(c) 중 무엇이 채택되든 깨지지 않는다 — Agent
간에 오가는 것이 무엇으로 분류되든, 그것은 Message라는 전달 형식에
담겨 옮겨진다는 최소 구조는 유지된다. 따라서 **"Message"와 "Event"는
같은 층위의 개념이 아니며 서로 대체하지 않는다** — 이는 이 RFC가 새로
만드는 구분이 아니라 기존 GLOSSARY 문언을 정확히 읽은 결과다.

## 7. Candidate — 최소 Envelope 개념(형식만, 스키마 아님)

> §13.1 Kernel Context Model(Context Identifier/Context Source/Content/
> Context Metadata/Order Key)의 절제된 서술 방식을 참고하되, Context와
> 동일한 개념으로 취급하지 않는다 — Context는 "Prompt 이전에 존재하는
> 값"(§13)이고 Message/Event는 그것과 다른 전달 경로다. 아래는 **개념적
> 존재 여부**만 후보로 올리며, 자료구조·직렬화 형식(Hidden 후보)은
> 정의하지 않는다.

| Candidate 필드 | 역할(최소) | 참고 선례 |
|---|---|---|
| Identity | 이 Message/Event 인스턴스를 다른 것과 구분하는 값 | §13.1 Context Identifier와 동일 층위 원칙(발급 방식은 Defer) |
| Type | 이 전달물이 Task/Event/Fault 중 무엇을 담는지 표시 | §6이 이미 구분한 Task/Event/Fault 분류를 재사용할 뿐, 새 분류를 만들지 않음 |
| Payload | 실제 내용물 — Kernel/Runtime이 해석하지 않는 불투명 값 | CM-4("Kernel은 Content를 해석하지 않는다")와 동형 |
| Correlation | 이 전달물이 어느 상위 흐름(예: 어느 Task, 어느 실행 단위)에 속하는지 | §16.6 "실행 단위(Execution Unit)"의 "불투명한 입력" 원칙과 동형 — Correlation 값 자체도 발신자가 정하고 Kernel은 비교만 한다(§13.1 Context Source의 "비교할 뿐 해석하지 않는다"와 동일 원칙 후보) |
| Time | 발생·발송 시각 | §13.3 A-4("조립은 시계를 읽지 않는다")와 상충하지 않도록 **호출자가 주입**하는 값으로만 후보를 남긴다 — Kernel/Runtime이 스스로 시계를 읽어 생성하지 않는다 |

**이 Envelope 후보가 결정하는 것 — 없음.** 다섯 필드의 **존재 여부만**
후보로 제안했다. 자료형, 필수/선택 여부, 직렬화 포맷, 발급 규칙은
전부 미정이며 이 RFC 다음 단계(후속 ADC, 그 이후로도 Hidden 유지될
가능성 큼)의 판단 대상이다.

## 8. Event Bus와의 경계 — 구현하지 않는다

이 RFC의 §4~§7 어디에도 다음이 없다: Event를 발행·구독하는 코드, 메시지
큐, Pub/Sub 패턴, 비동기 전달 보장 구현. §11("Kernel은 Event Bus가
아니다")과 `IMPLEMENTATION_RULES.md`("Event Bus 구현 금지")는 이 RFC로
전혀 완화되지 않는다. §6·§7의 Candidate는 **Event Bus가 언젠가
존재하게 될 경우 그것이 지켜야 할 최소 어휘**를 미리 논의할 뿐,
Event Bus의 존재 자체를 요구하지 않는다 — ADC-05·ADC-08이 여전히
Open인 이유(배달 보장 수준조차 미정)가 이를 뒷받침한다.

## 9. Phase A(`ADC-0032`)와의 관계 — 우회 금지 확인

- 이 RFC는 Agent Lifecycle State(`RFC-0024` §5)를 Accept된 것처럼
  전제하지 않는다 — §4가 "Agent State"를 Lifecycle과 명시적으로
  분리했다.
- 이 RFC는 Agent Domain Model(`RFC-0024` §4)의 필드(Identity/Role/
  Capabilities/Input/Output/Result)를 재정의하거나 확장하지 않는다 —
  §7 Envelope의 "Identity"는 **Message/Event 인스턴스의 식별자**이지
  **Agent의 Identity**(Phase A §4, 여전히 Defer)가 아니다. 이름이
  같다고 같은 개념이 아니다 — 혼동 방지를 위해 이 문장을 명시한다.
- 이 RFC는 Agent Manager의 허용 책임 범위를 넓히지 않는다(§5 — `ADC-0032`
  §Q4의 "전무" 판정을 그대로 계승).

## 10. 이 Contract가 어디에 귀속되어야 하는가 (Open Question, 이 RFC가 결정하지 않음)

`RFC-0024` §8은 Agent Domain의 귀속처(Kernel vs HQ)를 Open으로 남겼고
`ADC-0032` Q5도 확정하지 않았다. Message/Event Contract는 **다른
비대칭**을 보인다 — Agent Domain의 내용(Role이 무엇을 의미하는지)은
§7·CM-4에 따라 명백히 HQ 도메인이지만, **Event/Message 자체는 이미
§6에서 Kernel Concept Model 항목(Entity: Event, Interface: Message)으로
등재되어 있다.** 즉 "Event/Message가 있다는 사실"은 이미 Kernel
수준이고, 이 RFC가 여는 것은 "그 안에 무엇이 들어가는가(Envelope)"와
"배달을 어떻게 보장하는가(ADC-05·08)"뿐이다. 이는 §4의 두 후보와
다르게, **Kernel-level 정련일 가능성이 더 높은 방향**이라는 점만
관찰로 기록한다 — 그러나 이 관찰이 자동으로 Accept를 뜻하지 않는다.
`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준(①·②) 충족 여부는 후속
ADC가 별도로 판단해야 한다.

## 11. Out of Scope

- Agent State/Message/Event의 **구현**(자료구조, 저장소, 전송 코드,
  직렬화 형식).
- Event Bus, Pub/Sub, 비동기 전달 메커니즘의 설계·구현.
- Runtime의 세부 구조(ADC-02, Open), Scheduler, Registry.
- LangGraph, Workflow Engine과의 연동.
- ADC-05(Fault 배달 보장 수준)·ADC-08(Task/Event Flow 배달 보장 차등화)의
  **해소** — 이 RFC는 그 미결 상태를 인용할 뿐 판정하지 않는다.
- §6 Boundary Question(§6 표 (a)/(b)/(c)) 중 하나를 선택하는 것.
- Agent Domain Model·Agent Lifecycle State의 재정의(Phase A 소관,
  `ADC-0032` Not Accept 상태 유지).
- `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`
  문언 수정. Production Code 변경.

## 12. Non-goals

- 이 RFC는 Agent State/Message/Event Contract가 **필요하다**고
  주장하지 않는다 — Multi-Agent Runtime 자체가 아직 존재하지 않으므로
  (ADC-02 Open), 이 Contract의 실제 소비자가 없다. 미래 대비로 경계만
  미리 서술할 뿐이다.
- 이 RFC는 §10의 "Kernel-level 정련일 가능성이 더 높다"는 관찰을
  Accept 근거로 주장하지 않는다 — 관찰과 결정은 다르다.
- 이 RFC는 ADC-05·ADC-08의 오랜 Open 상태를 이 김에 해소하려 하지
  않는다 — 별개 절차다.

## 13. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase B)** | Agent State 존재 여부·소유권 경계(§4~§5), Message/Event 구분과 Envelope 개념(§6~§7)을 Candidate로 제안 + Event Bus 경계 재확인(§8) + Phase A 우회 여부 명시적 확인(§9) + 귀속처 Open Question(§10). **결정하지 않는다.** |
| **후속 ADC(신설 예정, 필요 시)** | §4~§7 각 Candidate의 Accept/Reject/조건부 Accept, §6 (a)/(b)/(c) 중 선택 여부, §10 귀속처 결정, ADC 채택 기준 충족 여부 판단. |
| **후속 ADR** | ADC 판단을 Baseline에 반영(Accept된 부분에 한해). |
| **후속 별도 절차** | ADC-05·ADC-08 배달 보장 수준 해소, Event Bus 구현, Runtime 존폐(ADC-02). |

이 RFC 자체는 위 판단을 내리지 않는다.

## 14. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건 추가만 존재. `BASELINE.md`·
  `GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  Production Code(`core/`, `hqs/`, `dashboard/`) **무변경**.
- §5 표의 각 행이 실제로 기존 확정/금지 문언과 모순 없이 인용됐는지
  재확인: `ADC-0032` §Q4("현재 허용 범위는 없다") — 원문 인용 일치.
  `IMPLEMENTATION_RULES.md` "Event Bus 구현 금지" — 원문 인용 일치.
  §11 "Kernel은 Event Bus가 아니다" — 원문 인용 일치.
- §9가 Phase A 우회 여부를 스스로 점검하는 절로 존재하는지 확인(있음) —
  Agent Domain/Lifecycle을 재정의·확장하지 않았음을 문장으로 명시.
- §7 Envelope 후보 중 "Time" 필드가 §13.3 A-4(조립은 시계를 읽지
  않는다)와 충돌하지 않도록 "호출자 주입"으로 한정했는지 확인(§7 표
  마지막 행) — Kernel Context Model의 결정론 원칙과 정합.
- ADC-05·ADC-08이 이 RFC로 인해 상태가 바뀌지 않았는지 `docs/decisions/adc/ADC.md`
  재확인 — 두 항목 모두 "Open"으로 그대로 존재(§11 Out of Scope 명시와
  일치).
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다(Phase A와
  동일 판단 — `pytest` 모듈은 이번 세션 환경에 없으며, 코드 diff 0줄이므로
  재실행 결과가 달라질 여지가 없다).

## 15. Self Review

- Baseline/Contract를 변경했는가 — **아니오**(§14).
- Agent State를 Lifecycle State와 혼동해 사실상 Phase A를
  재확정했는가 — **아니오**(§4, §9) — 명시적으로 분리하고 우회 여부를
  자체 점검했다.
- Agent Manager·Runtime·Event Bus에 새 권한을 부여했는가 —
  **아니오**(§5) — 전부 기존 확정·금지를 그대로 인용해 State에 적용했을
  뿐이다.
- Event Bus를 구현했는가 — **아니오**(§8, §11) — 코드·메커니즘 없음.
- Message ↔ Event 구분을 임의로 확정했는가 — **아니오**(§6) — (a)/(b)/(c)
  세 후보를 나열하고 선택하지 않았다.
- Envelope의 자료구조·스키마를 확정했는가 — **아니오**(§7) — 필드
  존재 여부만 후보로 올렸다.
- §10 귀속처를 확정했는가 — **아니오** — "가능성이 더 높다"는 관찰과
  결정을 명시적으로 분리했다(§10, §12).
- ADC-05/ADC-08을 이 김에 해소했는가 — **아니오**(§11, §14).
- Production Code를 변경했는가 — **아니오**(§14).
- 새로운 실험·프로토타입·측정을 수행했는가 — **아니오** — 기존 문서
  관찰만 인용했다.
