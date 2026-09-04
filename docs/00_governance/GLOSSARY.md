# Glossary

## 조직 계층

| 용어 | 정의 |
|---|---|
| Jarvis OS | AI Organization Operating System |
| Kernel | 모든 HQ가 공통으로 필요로 하지만 어느 HQ에도 속하지 않는 책임을 담당하는 계층. Component가 아니라 책임 경계다. *(정의: `docs/01_architecture/BASELINE.md` §11)* |
| HQ | 업무 영역. Jarvis OS가 실행하는 최상위 조직 단위 |
| Division | HQ 내부의 선택적 책임 단위. Jarvis OS 필수 계층 아님 |
| Team | HQ 내부의 선택적 전문 분야 단위. Jarvis OS 필수 계층 아님 |
| Agent | 실제 업무를 수행하는 단위 |
| Connector (MCP) | Agent가 외부 서비스와 연동하는 계층 |

## Concept Model 용어

| 분류 | Concept | 정의 |
|---|---|---|
| Entity | HQ | Registry에 등록되는 자율 단위 |
| Entity | Agent | Task를 실행하는 단위, HQ에 소속 |
| Entity | Principal | Task를 요청하는 주체 (사람/Agent/HQ) |
| Definition | Workflow | Task들의 실행 순서(그래프)를 정의하는 선언적 정의. 그 자체는 실행되지 않음 |
| Process | Task | Workflow에 따라 생성되는 작업 인스턴스 |
| Event | Event | HQ 경계를 가로질러 전파되는 통지 |
| Event | Fault | Task 실패 시 발생하는 특수 Event |
| Service | Runtime | Workflow를 참조하여 Task를 Agent에 배분하는 서비스 *(세부 구조는 ADC-02, Open)* |
| Service | Memory | Context를 HQ 네임스페이스 안에 영속화하는 서비스 |
| Service | Registry | HQ의 Capability를 색인하고 탐색하게 하는 서비스 |
| Interface | Engine Port | Engine 호출의 표준 인터페이스 |
| Interface | Adapter | 특정 Engine에 대한 구체 구현체 |
| Interface | Message | Task/Event가 공유하는 전달 형식 |
| Metadata | Capability | HQ/Agent가 선언하는 "무엇을 할 수 있는가" |
| Metadata | Artifact | Task 수행의 결과물에 대한 참조 |
| Policy | Policy | 모든 요청에 대해 PDP/PEP로 평가되는 규칙 |
| State | Context | Task 실행 중에만 유효한 임시 State |
| State | Lifecycle State | HQ의 생명주기 상태 |
| Resource | Resource | Runtime이 Task 실행에 배분하는 용량 (CPU/GPU/Token 등) |

## 용어 변경 이력

| 이전 명칭 | 현재 명칭 | 비고 |
|---|---|---|
| Core | Kernel | 동일한 것을 가리킨다. 공식 용어는 **Kernel**이다(ADR-0002). 과거 커밋 이력과 `archive/v1/`에는 "Core" 표기가 그대로 남아 있으며, 그 경우에도 Kernel과 같은 것을 뜻한다. 단, "Core Principles"·"Core Philosophy"·"Core Component 검토"처럼 **"핵심"이라는 일반적 의미로 쓰인 "Core"는 Kernel과 무관하며 변경되지 않았다.** |

## Kernel Design Principles (Reference)

상세 정의는 `docs/01_architecture/BASELINE.md` §12 참조.

| ID | 원칙 |
|---|---|
| KP-1 | Responsibility over Component |
| KP-2 | Deterministic Context Assembly |
| KP-3 | Stable Context Ordering |
| KP-4 | Stable Context by Design |
| KP-5 | Implementation Agnostic |
| KP-6 | Stateless Responsibility Boundary |

## Kernel Context Model (Reference)

상세 정의는 `docs/01_architecture/BASELINE.md` §13 참조.

| 용어 | 정의 |
|---|---|
| Kernel Context | 순서가 정해진 유한한 Context Segment 열과 그 Identifier·Metadata. 값(Value)이며 서비스가 아니다 |
| Context Segment | Kernel이 독립적으로 식별·정렬·포함/제외할 수 있는 Kernel Context의 최소 단위 |
| Context Source | Segment가 어디에서 왔는가를 식별하는 값. Kernel은 비교만 하고 해석하지 않는다 |
| Context Metadata | Segment 또는 Context **에 대한** 서술. 계층 분류나 Engine 종속 키를 담지 않는다 |
| Context Identifier | Context 또는 Segment의 동일성 판정 기준. Kernel이 스스로 생성하지 않는다 |
| Ordering Policy | Segment의 순서를 정하는 규칙. Model에 박힌 분류가 아니라 Context Builder의 **입력**이다 |

> 위 Concept Model 표의 `State | Context`("Task 실행 중에만 유효한 임시
> State")와 이름이 겹친다. Kernel Context는 그 Concept의
> **구체화이며 재정의가 아니다** — `BASELINE.md` §13.1 참조.
>
> **Prompt는 Kernel Context의 Output Format이다.** Claude/GPT/Gemini
> Prompt는 동일한 Kernel Context의 서로 다른 표현이며, Kernel Context가
> 정본이다(`BASELINE.md` §13.4).

## Kernel Public Contract (Reference)

상세 정의는 `docs/01_architecture/BASELINE.md` §14 참조. 이 계약은
Kernel 전체가 아니라 **Context 영역에 한정**된다.

| 용어 | 정의 |
|---|---|
| Kernel Public Contract | Kernel이 외부(HQ, Execution Layer)에 보장하는 공식 약속. API가 아니며, API는 이 계약을 구현하는 다음 단계다 |
| Public Responsibility | 외부가 Kernel에 요구할 수 있고 Kernel이 응답할 의무가 있는 것 (PR-1~PR-4) |
| Public Guarantee | 외부가 의존해도 되는 성질. 깨지면 계약 위반이다 (G-1~G-7) |
| Hidden Responsibility | Kernel이 수행하지만 **외부가 의존해서는 안 되는** 것. 여기에 의존한 코드가 깨지는 것은 계약 위반이 아니다 (H-1~H-6) |
| Extension Point | 교체 가능하다고 **계약상 선언된 지점**. 플러그인 메커니즘이 아니다 (X-1~X-4) |

> **계약은 공개하고 구현은 숨긴다.** 어떤 지점이 교체 가능하다는
> 사실과 그 지점이 지켜야 할 계약은 Public이고, 그 지점의 구현
> 내용은 Hidden이다(`BASELINE.md` §14.4).
>
> **Non-Goal은 "그 책임이 Kernel에 속하지 않는다"는 뜻이 아니다** —
> Component 수준의 선언일 뿐이다(`BASELINE.md` §14.6).

## Kernel Reference Architecture (Reference)

상세 정의는 `docs/01_architecture/BASELINE.md` §15 참조. **논리적
배선도이며 API가 아니다.**

| 용어 | 정의 |
|---|---|
| Responsibility Flow | Kernel 내부에서 책임이 이어지는 순서 — Collect → Merge → Validate → Order → Assemble → Render (6단계) |
| Data Flow | 각 단계에서 데이터가 갖는 논리적 상태. **§13.1의 Model 요소를 확장하지 않는다** |
| Responsibility Relationship | 단계 간 의존 관계와 금지 사항(RR-1~RR-4). "Component 관계"가 아니다(KP-1) |
| Extension Flow | 확장 지점(X-1~X-4)이 흐름의 어느 지점에 붙는가. **확장은 단계의 개수나 순서를 바꾸지 않는다** |
| Implementation Neutrality | 특정 언어·프레임워크·실행 모델에 종속되지 않기 위한 규칙(IN-1~IN-5)과 3형태 판정 기준 |

> **이 절에 "Component"라는 표현을 쓰지 않는 것은 의도적이다.** Kernel은
> 책임으로 정의되고 구현으로 정의되지 않는다(KP-1, `BASELINE.md` §11).
> **Kernel Component Architecture는 §10 Out of Scope다.**

## Kernel Modules — Execution Host (Reference)

상세 정의는 `docs/architecture/baseline/BASELINE.md` §16.3 참조.

| 용어 | 정의 |
|---|---|
| Execution Host | 단일 실행 단위(Task)의 dispatch·격리를 담당하는 책임. Command(불변)·Task(identity/lifecycle) 어느 쪽에도 속하지 않는다. §6 Concept Model의 "Runtime"과는 별개의, 더 좁은 범위의 Concept이다(`docs/architecture/core/ADC-0014-execution-responsibility-naming.md` §Q2) — Runtime 항목을 재명명한 것이 아니다 |

> Execution Host는 §6 Concept Model 표에 등재되지 않는다 — Kernel
> Module(§16) 수준의 좁은 책임이며, Jarvis OS 수준 넓은 Concept
> Model에 반드시 속해야 하는 것은 아니다(`docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`
> §Decision 3). 구현 전략(Process/Thread/Subprocess)은 미확정이며,
> `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"는
> 그대로 유효하다.

## Kernel Modules — Workflow Adapter (Reference)

상세 정의는 `docs/architecture/baseline/BASELINE.md` §16.6 참조.

| 용어 | 정의 |
|---|---|
| Workflow Adapter | HQ가 정의한 고정 Workflow 그래프의 실행 진행(State 보유·Node 진행·조건부 분기·Loop·값 기반 Checkpoint/Resume — §16.6 A-IN 5항목)을 담당하는 책임의 공식 명칭. §16.2 **Engine Adapter**(Model/LLM Provider 호출)와는 별개의 책임이며 그것을 재명명·흡수한 것이 아니다(`docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` §Q-B). v1 `archive/v1` `ADR-0007`의 `IWorkflowEngine` Port("Engine" 계보)를 계승하지 않는다 — "Engine" 프레이밍이 함의하던 Core 소유 Lifecycle 소비를 v2가 폐기했기 때문이다(`ADC-0019` G2) |
| Adapter Contract | Workflow Adapter 구현체가 지켜야 할 **내부 의무**를 §16.6 A-IN의 부속 명세로 정련한 것 — (a) caller-owned Checkpoint 값 소유, (b) 실행 결과의 값 표현 = 어댑터 책임, (d) Reversibility 재확인. Public Surface가 아니고 §14 Kernel Public Contract가 아니며 그 선행물도 아니다 — §14 자동 승격 경로 없음(`ADC-0020` §Q-C). 병렬 State 동시 쓰기 규약("(c)")은 이 명세에서 Defer됨(`ADC-0020` §Q-D) |
| 실행 단위 (Execution Unit) | `BASELINE.md` §16.6 A-IN이 입력으로 받는 "이미 구성된 실행 단위" — HQ가 구성한 "무엇을·어떤 순서·병렬성으로·어느 Agent가 수행하는가"의 묶음. Kernel은 그 내부 구조·생명주기·조직적 출처(Division/Team 유무)를 정의하지 않는다(`docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` §D-0). §16.3·§16.4·§16.6이 공유하는 용어이며 §6 Concept Model에 등재되지 않는다 |

> Workflow Adapter는 §6 Concept Model 표에 등재되지 않는다 — Execution
> Host(§16.3)와 같은 Kernel Module(§16) 수준의 좁은 책임이다
> (`docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md`
> §Decision 4). Reversibility는 이 책임의 필수 Architecture 불변조건이며,
> 어떤 구현체(LangGraph 포함)를 제거·교체해도 Kernel·HQ 코드는 수정되지
> 않는다. 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 9(및 `ADC-0021` §8 Gate (B)·(C))가 미해결인 동안 §14
> 승격·Production 구현 착수는 불가하다 — v1 `ADR-0007` 결정 2·5·11은
> `ADC-0022`로 해소됐다. `hqs/development/IMPLEMENTATION_RULES.md`의 Workflow/
> Scheduler/Runtime/Event Bus 구현 금지는 그대로 유효하다.
> Reversibility 불변조건은 `ADC-0021` §8 Gate (C)의 in-repo 통합
> 테스트(E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`,
> IN-1~IN-5 22 PASS)로 v2 맥락에서 **부분 충족**으로 재현됐다 —
> 결정론적 stub·LangGraph 단일 계보·실엔진 미검증이라는 잔여 한계가
> 있어 완전 discharge는 아니며, `ADC-0019` 재검토 조건 (c)와 v1
> `ADR-0007` 결정 9는 그대로 미충족이다(결정 2·5·11은 `ADC-0022`로
> 해소; `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).

## 핵심 원칙 (Reference)

| 용어 | 정의 |
|---|---|
| Reference Architecture | 다른 HQ를 만들기 위한 기준 Architecture |
| Task Flow | HQ 계층을 따라 수직으로 흐르는 작업 흐름 |
| Event Flow | HQ 경계를 가로질러 수평으로 흐르는 통지 흐름 |
| No Silent Failure | 실패는 반드시 관측 가능하게 드러나야 한다는 원칙 |
