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

## 핵심 원칙 (Reference)

| 용어 | 정의 |
|---|---|
| Reference Architecture | 다른 HQ를 만들기 위한 기준 Architecture |
| Task Flow | HQ 계층을 따라 수직으로 흐르는 작업 흐름 |
| Event Flow | HQ 경계를 가로질러 수평으로 흐르는 통지 흐름 |
| No Silent Failure | 실패는 반드시 관측 가능하게 드러나야 한다는 원칙 |
