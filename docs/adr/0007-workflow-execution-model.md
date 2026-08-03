# ADR-0007: Workflow Execution Model

- 날짜: 2026-08-03
- 상태: **Accepted**

---

## 배경 (Context)

Phase 5(Workflow — LangGraph Core)에 착수하기 전, 현재 코드를 조사했다.

1. `apps/poc-runner/src/jarvis_poc_runner/main.py`의 `run_organization_layer()`가
   Stage 6(Division Selection) ~ Stage 9(Result Integration)까지를 **순차 함수
   호출**로 직접 구현하고 있다: `hq.select_division()` → `Team(...)` 생성 →
   `team.activate()` → Agent 반복문(Connector 호출) → `team.complete()` →
   `team.terminate()`. 분기, 병렬 실행, 재시도, 취소 중 어떤 것도 없다 — "Kernel이
   선택한 HQ 이후의 흐름이 실제로 발생하는가"만 검증하는 Walking Skeleton이다.
2. `packages/core/src/jarvis_core/organization/entities.py`의 `Team`은 이미
   `TeamState`(FORMING → ACTIVE → COMPLETING → TERMINATED) Enum과 그 전이를
   강제하는 메서드(`activate()`/`complete()`/`terminate()`, `assert`로 순서 위반을
   막음)를 갖고 있다 — Ephemeral(HQ와 달리 Idle 상태를 두지 않음)이라는 것도 이미
   확정되어 있다(Core Design Principles v1 §3).
3. `packages/core/src/jarvis_core/ports/i_workflow_engine.py`는 파일만 존재하고
   내용이 비어 있다(docstring 두 줄뿐, Interface 정의 없음).
4. `adapters/workflow-langgraph/.../langgraph_engine.py`도 마찬가지로 docstring만
   있고 구현이 없다 — Phase 5가 채워야 할 대상.
5. `docs/architecture/v1.0/01-reference-architecture.md` §3~4가 이미 두 가지를
   확정해 두었다:
   - Task 흐름(수직, 계층 준수: Jarvis OS → HQ → Division → Team → Agent)과
     Event 흐름(수평/전역, 계층 무관: 어느 계층이든 발행/구독 가능)은 **서로 다른
     골격**이다.
   - "이전 블루프린트에서는 LangGraph를 오케스트레이션 코어 전체로 표현했지만,
     더 정확히는 **HQ~Team 사이의 실행 엔진**이다. Jarvis OS 계층(전역 라우팅·
     정책·HQ 레지스트리)은 LangGraph가 대신해주지 않는다" — 즉 LangGraph의
     Architecture상 위치는 이미 한 번 정정된 바 있다.
6. Event Bus 자체(Redis Streams/Kafka/NATS 등)는 여전히 미조사·미구현 상태다
   (`ROADMAP.md` v1.1 후보, 01-reference-architecture.md §6). 이 ADR은 Event Bus의
   기술 선정을 다루지 않는다 — Workflow Engine과 Event Bus 사이의 **책임 경계**만
   확정한다.

이 ADR은 Workflow라는 Domain 개념 자체(Workflow Engine의 책임, Team 생명주기,
Agent 실행 모델, Team/Division 경계, Failure/Parallel/Cancellation 정책, Workflow와
Event의 관계, Workflow State Model)를 확정한다. LangGraph는 그 Domain을 만족시키는
구현체 중 하나일 뿐이며, LangGraph의 Graph/Node/Edge/State 표현 방식, Checkpointer,
Command API 같은 SDK 세부 사항은 이 ADR에 포함하지 않는다 — 그건
`adapters/workflow-langgraph` 내부의 구현 디테일이다.

## 결정 (Decision)

### 결정 1 — Workflow Engine의 책임: HQ~Team~Agent 사이의 실행 순서를 조립하고 진행시킨다

Workflow Engine은:

- **무엇을 실행할지 결정하지 않는다.** 어떤 HQ가 선택되는지(Kernel의 Stage
  1~5), 어떤 Division이 선택되는지(HQ 자신의 책임, `HQ.select_division()`), 어떤
  Capability가 필요한지는 이미 Workflow Engine이 개입하기 전에 결정되어 있다.
  Workflow Engine은 이 결정들의 **결과(Dispatch)를 입력받아 Team~Agent 실행
  순서를 조립하고 진행시키는 것**만 담당한다.
- **Division/HQ를 대신하지 않는다.** Division Selection은 여전히 HQ의 책임이고
  (기존 `HQ.select_division()` 무수정), Workflow Engine은 그 결과를 소비할 뿐
  Division 로직을 흡수하지 않는다.
- **Team의 생명주기 전이를 스스로 재구현하지 않는다.** `Team.activate()`/
  `complete()`/`terminate()`는 이미 Core의 Domain 로직이다(결정 2). Workflow
  Engine은 이 메서드들을 정해진 순서로 호출하는 조립자(orchestrator)이지, 전이
  규칙 자체의 소유자가 아니다 — Guard 로직을 Adapter에 재구현하지 않는다는
  ADR-0003 결정 3의 원칙을 그대로 따른다.
- **Policy 판단을 하지 않는다.** "이 Agent가 이 Capability를 써도 되는가"는
  여전히 Policy Engine(PDP, ADR-0005)의 몫이다. Workflow Engine은 Policy 판단이
  이미 끝난 지점 이후의 실행 순서만 다룬다.

### 결정 2 — Team의 생명주기: Core Domain 로직, Workflow Engine은 이를 소비만 한다

`Team`/`TeamState`(`packages/core/.../organization/entities.py`)는 이미 존재하는
Core Domain 개념이며, 이 ADR은 이를 재정의하지 않는다.

- Team은 여전히 **Ephemeral**이다: `FORMING → ACTIVE → COMPLETING → TERMINATED`
  외의 상태를 갖지 않으며, Idle 상태를 의도적으로 두지 않는다(Core Design
  Principles v1 §3, 기존 확정 사항 재확인).
- 전이 순서 강제(`assert`로 위반 시 예외)는 Core에 남는다. Workflow Engine
  Adapter가 무엇이든(LangGraph든 다른 엔진이든) 이 전이 규칙을 우회하거나
  재구현할 수 없다.
- Workflow Engine의 역할은 "언제 `activate()`를 호출하고, 언제 `complete()`를
  호출할지"의 **타이밍과 순서**를 그래프/노드로 표현하는 것이다 — 상태값 자체를
  새로 만들거나 전이 조건을 바꾸는 것이 아니다.

### 결정 3 — Agent 실행 모델: Agent는 Workflow의 실행 단위(Node)이지, Workflow를 소유하지 않는다

- Agent(`packages/core/.../organization/entities.py`의 `Agent` dataclass)는
  Workflow Engine이 실행하는 **작업 단위**다. Agent 자신은 자신이 언제 실행될지,
  다른 Agent와 어떤 순서/병렬 관계에 있는지 알지 못한다 — 이 지식은 Workflow
  Engine(구체적으로는 Team 구성 시점에 조립되는 Graph)에 있다.
- Agent의 실행 내용(어떤 Capability를 수행하고 어떤 Connector를 호출하는가)은
  ADR-0006이 이미 확정한 Connector Execution Model을 그대로 따른다 — 이 ADR은
  Agent-Connector 관계(ADR-0006 결정 1, 10)를 변경하지 않는다. Workflow Engine은
  "언제 Agent가 Connector를 호출하는 단계에 도달하는가"만 결정하고, 호출 자체의
  의미·허용 여부·실패 처리는 여전히 Agent(및 그 뒤의 Connector/Policy Engine)의
  몫이다.
- **Stage 8 재구성(사용자 지시, ADR-0006 결정 12 관련 논의에서 이미 범위 밖으로
  확정됨)**: "Agent가 Connector를 호출한다"는 구조로의 실제 이동은 이 Phase에서
  다룬다 — Workflow Engine이 Agent를 실행 단위로 취급하는 순간, Composition
  Root(`main.py`)가 Connector 호출을 대행하던 기존 방식(ADR-0006 결정 12가 이미
  지적한 임시 구조)이 자연스럽게 "Team이 조립한 순서대로 Agent가 실행되고, 그
  실행 안에서 Agent가 Connector를 호출한다"는 형태로 바뀐다. 이 ADR은 그 목표
  구조를 확정하고, 실제 배선(Implementation Plan에서 상세화)은 Phase 5 구현에서
  수행한다.
- **최소 변경 원칙(사용자 지시)**: 이번 Phase가 허용하는 변경은 "Connector
  호출의 주체가 Composition Root에서 Agent로 이동한다"는 것 **하나뿐**이다.
  Kernel(Stage 1~5), HQ의 Division Selection(Stage 6, `HQ.select_division()`),
  Division 자체의 책임(Agent Catalog 보유)은 이 이동과 함께 재설계하지 않는다.
  이번 Phase의 Architecture Validation 목표는 "Workflow Adapter를 교체할 수
  있는가"와 "Agent가 Connector를 직접 호출하는 구조가 Core 수정 없이 동작하는가"
  이지, Organization Layer(Kernel/HQ/Division 포함) 전체의 재설계가 아니다.
- **Agent Lifecycle은 이번 ADR/Phase의 범위가 아니다.** 이번 Phase가 정의하는
  것은 "Agent = Workflow의 실행 단위"라는 역할뿐이며, Agent 자신의 상태 전이
  모델(HQ의 8-state Lifecycle이나 결정 13의 Connector Lifecycle State처럼 Agent
  전용 State Machine)은 정의하지 않는다. Agent에게 독자적인 Lifecycle이
  필요해지는 것은 여러 Agent가 장시간·비동기로 협업하는 Multi-Agent 운영
  단계이며, 그 시점에 별도 ADR로 다룬다 — 지금 Agent Lifecycle까지 정의하면
  아직 존재하지 않는 요구를 위해 설계하는 것이 되어 ADR-0004/0005가 반복해 온
  "필요가 드러나지 않은 확장은 미룬다"는 원칙에 어긋난다.

### 결정 4 — LangGraph의 위치: Workflow Adapter이지 Architecture가 아니다

- LangGraph는 `IWorkflowEngine`(결정 9)의 구현체 중 하나다. Team 생명주기/Agent
  실행 모델/Failure/Parallel/Cancellation에 대한 이 ADR의 결정들이 Architecture이고,
  LangGraph는 그 Architecture를 만족시키는 PoC 단계의 선택(`PROJECT_CONTEXT.md`
  Technology Decisions, "LangGraph Core만 사용, langgraph-api는 사용하지 않음")일
  뿐이다.
- 01-reference-architecture.md §3이 이미 정정한 대로, LangGraph의 Architecture상
  위치는 **"HQ~Team 사이의 실행 엔진"**이다. Jarvis OS 계층 전체(전역 Kernel
  Routing, HQ Registry, Policy Engine)를 LangGraph가 대신하지 않는다 — LangGraph는
  Division Selection 이후, 정확히는 Team Formation~Agent 실행~Team 종료 구간의
  실행을 담당하는 Adapter다.
- **Adapter Reversibility 조건**(ADR-0003 결정 5, ADR-0005 결정 6, ADR-0006 결정
  11과 동일한 패턴): LangGraph Adapter를 제거하고 다른 Workflow Engine(또는 현재의
  순차 함수 호출 방식)으로 교체해도 `packages/core`와 Organization Layer를
  구현하는 코드는 단 한 줄도 수정하지 않는다. 교체는 Composition Root의 import
  한 줄과 `pyproject.toml` 의존성 한 줄로 끝나야 한다.
- LangGraph의 Graph/Node/Edge/`StateGraph`/Checkpointer 같은 SDK 문법은 Adapter
  내부에서만 사용하는 언어다. Team/Agent(Core Domain Model)를 LangGraph의
  State/Node로 변환하는 지점이 LangGraph 문법과 Domain Language의 유일한 경계다.

### 결정 5 — Team과 Division의 경계

기존 계층 책임(01-reference-architecture.md, Core Design Principles v1)을
재확인하고, Workflow Engine이 이 경계를 넘지 않도록 명시한다.

| | Division | Team (Workflow Engine이 조립) |
|---|---|---|
| 생명주기 | 반영구(프로젝트 단위, Archived 가능) | Ephemeral(작업당 1회, 종료 시 소멸) |
| 책임 | Agent Catalog 보유, Division Selection에는 관여하지 않음(Selection은 HQ 책임) | 필요한 Agent를 모아 실행 순서를 조립·진행 |
| Workflow Engine과의 관계 | Workflow Engine은 Division을 생성/소멸시키지 않는다 | Workflow Engine이 Team의 FORMING→TERMINATED 전이를 조립·트리거한다 |

- Division Selection(`HQ.select_division()`)은 Workflow Engine이 개입하기 **이전**
  단계다. Workflow Engine은 Division이 이미 선택된 뒤, 그 Division의
  `agent_catalog`를 바탕으로 Team을 조립하는 지점부터 시작한다.
- Division 자체의 생명주기(반영구, Archived 가능 여부는 `ROADMAP.md` v1.1 후보로
  남아있는 미정 사항)는 이 ADR의 범위가 아니다.

### 결정 6 — Workflow Failure 처리

- Workflow 실행 중 발생하는 실패는 두 층위로 구분한다:
  1. **Agent/Connector 층위 실패** — 이미 ADR-0006이 `ToolResponse(status=FAILURE
     |TIMEOUT)`으로 Fail-Closed 계약을 확정했다. Workflow Engine은 이 실패를
     삼키지 않고 그대로 관측 가능해야 한다(No Silent Failure) — 하지만 이 실패의
     "의미"(재시도할지, 포기할지)를 Workflow Engine이 스스로 정책으로 판단하지
     않는다. 이는 여전히 Policy Engine(Retry Policy, ADR-0005/0006이 이미 Tier
     3/결정 8로 범위를 좁혀 둔 영역)의 몫이다.
  2. **Workflow 자체 층위 실패** — Team 전이 규칙 위반(예: `TransitionDenied`류),
     Workflow Engine 내부 오류(그래프 구성 실패 등)는 Workflow Engine이 예외를
     삼키지 않고 호출자(Composition Root)에게 명시적 실패로 전달해야 한다 — Fail-
     Closed 계약을 Connector(ADR-0006 결정 9)에 이어 Workflow Engine에도 동일하게
     적용한다.
- Workflow Engine은 실패 시 자동으로 재시도하지 않는다 — ADR-0006 결정 8("Connector는
  재시도하지 않는다, 재시도는 Policy 소관이다")과 동일한 논리를 Workflow 층위에도
  적용한다. Workflow 전체를 재시도할지는 향후 Retry Policy가 결정할 사항이며,
  이번 ADR/Phase 범위가 아니다.

### 결정 7 — Parallel Execution 원칙

- 한 Team 안에서 여러 Agent를 **병렬로 실행하는 것은 Workflow Engine의 권리이자
  능력**이다(LangGraph가 여러 Node를 병렬 분기로 표현할 수 있다는 것이 이 Phase를
  Phase 5로 배치한 이유 중 하나 — 순차 함수 호출로는 표현할 수 없었던 것).
- 단, 병렬 실행이 허용되려면 다음을 만족해야 한다:
  - Agent 간 병렬 실행 여부는 **Domain 지식**(어떤 Agent가 서로 독립적인가)에
    달려 있다 — 이 판단은 Division/Team 구성 시점의 Domain 설계(Agent Catalog
    설계) 문제이지, Workflow Engine이 임의로 결정할 대상이 아니다. 이번 ADR은
    "병렬 실행이 가능해야 한다"는 요구만 확정하고, "어떤 Agent들이 병렬 가능한지
    판단하는 스키마"는 Implementation Plan에서 범위를 정한다.
  - 병렬로 실행된 Agent 중 일부가 실패해도 Team 전체가 Silent하게 성공 처리되지
    않는다(결정 6의 No Silent Failure 원칙을 병렬 실행에도 동일 적용).
  - 병렬 실행은 Team의 Ephemeral 생명주기(결정 2)를 바꾸지 않는다 — 병렬로
    실행되는 여러 Agent는 여전히 하나의 `ACTIVE` Team 상태 안에 속한다. "Agent별
    하위 상태"를 Team의 State Model에 추가하지 않는다(결정 10).

### 결정 8 — Event Bus와 Workflow의 책임 분리

01-reference-architecture.md §3~4이 이미 확정한 "Task 흐름(수직) vs Event 흐름
(수평)"의 구분을 Workflow Engine에도 명시적으로 적용한다.

- **Workflow Engine의 흐름은 Task 흐름이다.** HQ → Division → Team → Agent라는
  계층을 그대로 준수하며, Kernel이 만든 Dispatch 하나에 대응하는 하나의 실행
  경로를 조립·진행시킨다.
- **Event Bus의 흐름은 별개다.** 어느 계층에서든 발행 가능하고, 계층을 건너뛸 수
  있으며(예: 말단 Agent의 이상 감지 이벤트가 곧바로 상위 모니터링에 도달), 특정
  Workflow 실행과 1:1로 묶이지 않는다.
- **경계**: Workflow Engine이 실행 중 Event를 발행할 수는 있다(예: "Team이
  Completing으로 전이했다"는 이벤트) — 하지만 Workflow Engine이 Event Bus의
  구독/라우팅 로직을 흡수하지 않는다. 반대로 Event Bus가 Workflow의 다음 단계
  진행을 대신 결정하지도 않는다 — Event를 구독해서 새로운 Dispatch를 만드는
  것(예: HQ가 자기 Division의 이벤트를 구독했다가 새 Task를 스스로 생성하는
  것)은 이미 01-reference-architecture.md가 설명한 시나리오이며, 이 경우도 "새
  Dispatch가 만들어지면 그 이후는 다시 정상적인 Task 흐름(Workflow Engine의
  영역)"이라는 원칙은 변하지 않는다.
- Event Bus의 기술 선정(Redis Streams/Kafka/NATS)은 여전히 이 ADR의 범위 밖이다
  (`ROADMAP.md` v1.1 후보로 남는다). 이 ADR은 "Workflow Engine과 Event Bus는
  서로 다른 책임이며 서로의 로직을 흡수하지 않는다"는 경계만 확정한다.

### 결정 9 — IWorkflowEngine Port (Domain Interface, Core 소속)

```python
class IWorkflowEngine(ABC):
    def run(self, team: Team, dispatch: KernelDispatch) -> WorkflowResult:
        """Team을 구성하는 Agent들의 실행 순서를 조립하고 진행시킨 뒤,
        Team이 TERMINATED에 도달하면 WorkflowResult를 반환한다.
        예외를 던지지 않는다 — 실패는 WorkflowResult.status로 표현한다(결정 6).
        """
        ...
```

- `Team`/`KernelDispatch`는 이미 존재하는 Core Domain Model이다. `IWorkflowEngine`은
  이들을 입력받아 `WorkflowResult`(신규 Domain Model, 최소한 `status`/`error`
  필드를 가져 ADR-0005/0006과 동일한 Fail-Closed 패턴을 표현)를 반환한다.
- 정확한 필드 구성과 Cancellation(결정 10)을 위한 API 형태는 Architecture
  결정이 아니라 구현 세부사항이다 — Implementation Plan에서 확정한다. 이 ADR은
  "Port가 존재해야 하고, Team/Dispatch를 받아 WorkflowResult를 예외 없이
  반환해야 한다"는 계약만 확정한다.
- **Team은 이 Port(또는 이 Port를 사용하는 Application Service)만 의존한다.**
  Team이나 Agent를 구현하는 Core 코드는 LangGraph의 존재를 알지 못한다 —
  ADR-0003 결정 4("Core는 Adapter를 추론하거나 분기하지 않는다")를 Workflow에도
  동일하게 적용한 것이다.

### 결정 10 — Workflow Cancellation

ADR-0006 결정 6(Connector Cancellation)과 동일한 논리를 Workflow 층위로 확장한다.

- Cancellation은 **호출자(Composition Root, 향후 User 요청)가 진행 중인 Workflow를
  더 이상 진행시키지 않기로 결정하는 것**으로 정의한다.
- Domain이 요구하는 것: 취소 요청 시 Workflow Engine은 최대한 빠르게 안전한
  지점(예: 현재 Agent 실행이 끝나는 시점)에서 멈추고, Team을 강제로
  `TERMINATED`로 전이시켜야 한다 — Team이 `ACTIVE`나 `COMPLETING` 상태로
  방치되지 않는다(Ephemeral 원칙, 결정 2 위반 방지).
- Domain이 요구하지 않는 것: 이미 실행 중인 Agent/Connector 호출이 물리적으로
  즉시 중단되는 것까지는 보장하지 않는다 — ADR-0006 결정 6과 동일하게, 이는
  각 Connector Adapter의 능력에 달려 있다.
- **Phase 5 범위**: LangGraph는 비동기 실행과 Checkpoint 기반 재개를 지원하므로
  Cancellation을 실제로 구현할 능력이 Phase 4(완전 동기 구조)보다 커진다. 다만
  이번 ADR은 "Workflow Cancellation이라는 Domain 개념(상태값, `IWorkflowEngine`의
  취소 신호 계약)이 존재해야 한다"는 요구까지만 확정하고, 실제 구현 범위(어느
  수준까지 취소를 지원할지)는 Phase 5 Implementation Plan에서 정한다 — 은폐가
  아니라 명시적 범위 조정이다(ADR-0006이 Cancellation에 대해 취한 것과 동일한
  절차).

### 결정 11 — Workflow State Model

Team의 기존 State(`TeamState`, 결정 2)에 더해, Workflow 실행 자체의 결과를
표현하는 최소 State를 Domain Model로 정의한다 — Connector의 `ToolCallStatus`
(ADR-0006 결정 4)와 동일한 패턴이다.

```python
class WorkflowStatus(str, Enum):
    SUCCESS = "success"     # Team이 정상적으로 TERMINATED에 도달함
    FAILURE = "failure"     # Team 내부에서 복구 불가능한 실패 발생(예: 모든 Agent 실패)
    CANCELLED = "cancelled" # 결정 10에 의해 중도 종료됨
```

- 이 State는 `TeamState`(Ephemeral 생명주기, 결정 2)를 대체하지 않는다 —
  `WorkflowStatus`는 "그 생명주기가 어떻게 끝났는가"를 나타내고, `TeamState`는
  "지금 어느 단계에 있는가"를 나타낸다. 두 개념은 서로 다른 축이다.
- `WorkflowResult`(결정 9)는 반드시 `WorkflowStatus`를 포함하며, `SUCCESS`가
  아닐 때는 `error`가 채워진다(No Silent Failure, ADR-0004/0005/0006과 동일한
  원칙의 반복 적용).
- 이 State Model 역시 HQ Lifecycle(ADR-0003)과 Connector Lifecycle(ADR-0006
  결정 13)처럼 **Core의 Domain 개념**이며, 특정 Adapter(LangGraph)의 내부
  상태(LangGraph의 `StateGraph` 내부 State와는 다른 개념)가 아니다.

### 결정 12 — Workflow는 Plugin이 아니다: Workflow Registry/Discovery/Capability를 도입하지 않는다

HQ(ADR-0004)와 Connector(ADR-0006 결정 12)는 모두 "이름이 아니라 Capability로
발견되는 Plugin"이라는 동일한 패턴을 따른다. **Workflow Engine은 이 패턴을
따르지 않는다** — 사용자 지시로 이번 ADR에서 명시적으로 확정한다.

- Workflow Engine은 여러 구현체 중 런타임에 선택되는 대상이 아니다. Composition
  Root가 조립 시점에 **하나의 실행 엔진**(현재는 LangGraph Adapter)을 선택해
  Team에 주입할 뿐이다 — HQ나 Connector처럼 "여러 개가 동시에 존재하고 그중
  하나를 Capability로 골라 쓰는" 구조가 아니다.
- 따라서 이번 Phase(및 이 ADR)는 다음을 **도입하지 않는다**: Workflow Registry,
  Workflow Discovery(entry point 기반이든 다른 방식이든), Workflow Capability
  선언. `IWorkflowEngine`(결정 9)는 Connector Discovery(ADR-0006 결정 12)와
  달리 Composition Root가 직접 구성(direct construction)하는 단일 인스턴스로
  충분하다.
- Adapter Reversibility(결정 4, 이번 Phase의 최종 Architecture Validation
  목표)는 Discovery 메커니즘이 아니라 **Composition Root의 import 한 줄 교체**
  만으로 증명한다 — ADR-0003 결정 5(Lifecycle Adapter), ADR-0005 결정
  6(Policy Adapter)이 이미 증명한 것과 동일한 방식이며, ADR-0006이 Connector에
  대해서만 추가로 도입한 Discovery/Registry 계층을 Workflow에는 확장하지 않는다.
- 이 결정은 "Workflow Engine이 하나의 실행 엔진이며 Team이 이를 사용하는
  구조"라는 원칙을 Registry 계층 없이 유지하기 위한 것이다 — 향후 여러 Workflow
  Engine을 동시에 운용해야 하는 요구가 실제로 발생하면(예: HQ별로 다른 Workflow
  Engine을 쓰는 시나리오), 그때 별도 ADR로 재검토한다(Re-evaluation Principle,
  ADR-0001).

## 근거 (Rationale)

ADR-0003(Domain Port / Adapter Reversibility)과 ADR-0005/0006(Fail-Closed 계약,
정책은 코드가 아니라 Policy Engine 소관)의 원칙을 Workflow Engine에 동일하게
적용했다. Workflow Engine이 실패 시 스스로 재시도하지 않는다는 결정(결정 6)은
ADR-0006 결정 8("Connector는 재시도하지 않는다")의 직접적 연장이다 — 재시도
정책을 Workflow Engine에 하드코딩하면 같은 실수(정책의 계층 간 중복 분산)를
반복하게 된다.

LangGraph의 위치(결정 4)는 01-reference-architecture.md §3이 이미 한 번
정정해 둔 내용("LangGraph는 오케스트레이션 코어 전체가 아니라 HQ~Team 사이의
실행 엔진")을 ADR로 공식화한 것이다. Event Bus와의 책임 분리(결정 8)도 같은
문서 §3~4가 이미 확립한 "Task 흐름(수직) vs Event 흐름(수평)" 구분을 그대로
가져온 것 — 이 ADR은 새로운 원칙을 발명하지 않고, 이미 Architecture v1.0에
있던 구분을 Workflow Engine이라는 구체적 컴포넌트에 적용했을 뿐이다.

Workflow State Model(결정 11)은 ADR-0006 결정 4(`ToolCallStatus`)와 동일한
이유로 존재한다 — SUCCESS/FAILURE/CANCELLED를 명시적으로 구분해야 호출자가
각기 다른 대응을 할 수 있고, Fail-Closed 계약을 표현할 자리가 생긴다.

Workflow Registry를 도입하지 않는다는 결정(결정 12)은 ADR-0004/0006이 HQ와
Connector에 각각 적용한 "Capability 기반 Plugin" 패턴을 **모든 확장 지점에
기계적으로 반복 적용하지 않는다**는 판단이다 — HQ와 Connector는 실제로 여러
구현체가 동시에 존재하고 런타임에 선택되어야 하는 대상이지만, Workflow Engine은
Composition Root가 조립 시점에 하나만 선택하는 대상이다. 사용자가 지적한 대로
"Workflow는 Plugin이 아니다"라는 구분을 그대로 ADR에 반영했다 — 패턴의 일관성보다
Domain의 실제 성격을 우선한 것이다.

## 기각된 대안 (Rejected Alternatives)

- **대안 A**: LangGraph를 Jarvis OS 전체의 오케스트레이션 코어로 취급하고,
  Kernel Routing/Policy Engine/HQ Registry까지 LangGraph 그래프 안에 흡수한다.
  기각 — 01-reference-architecture.md §3이 이미 이 표현을 "정정 대상"으로
  지적했다. Kernel/Policy/Capability Registry는 이미 각자의 ADR(0004/0005)로
  확정된 별도 Domain이며, 이를 LangGraph 그래프에 흡수하면 Core가 LangGraph를
  알게 되어(ADR-0003 결정 4 위반) Adapter Reversibility가 깨진다.
- **대안 B**: Workflow Engine이 Team의 상태 전이 규칙을 자체적으로 재구현한다
  (예: LangGraph의 State로 FORMING/ACTIVE/COMPLETING/TERMINATED를 다시 표현).
  기각 — ADR-0003 결정 3(Guard 로직을 Adapter에 재구현하지 않는다)과 동일한
  이유로, 상태 전이 규칙이 Core(`Team` dataclass)와 Adapter(LangGraph State) 두
  곳에 분산되면 Drift 위험이 생긴다. Workflow Engine은 `Team.activate()`/
  `complete()`/`terminate()`를 호출하는 조립자일 뿐, 전이 규칙의 소유자가 아니다.
- **대안 C**: Event Bus를 Workflow Engine의 일부로 구현한다(예: LangGraph의
  Pub/Sub 확장을 Event Bus로 겸용). 기각 — 결정 8이 명시한 대로 Task 흐름과
  Event 흐름은 서로 다른 골격이다. Event는 계층을 건너뛸 수 있어야 하는데
  (말단 Agent → 전역 모니터링), Workflow Engine은 계층을 준수하는 Task 흐름
  전용이므로 이 요구를 만족시킬 수 없다. 두 책임을 섞으면 향후 Event Bus 기술을
  선정할 때(v1.1 후보) Workflow Engine 교체와 억지로 묶이게 된다.
- **대안 D**: 병렬 실행 가능 여부를 Workflow Engine이 런타임에 자동으로
  판단한다(예: 인자를 공유하지 않는 Agent는 자동으로 병렬 처리). 기각 — 이는
  Domain 지식(Agent 간 실제 독립성)을 Workflow Engine이라는 Adapter 계층에서
  추론하려는 시도이며, ADR-0003 결정 4("Core/Adapter는 서로를 추론하거나
  분기하지 않는다")의 정신에 어긋난다. 병렬 가능 여부는 Division/Agent Catalog
  설계 시점의 명시적 선언이어야 한다(결정 7).
- **대안 E**: Workflow Cancellation을 이번 ADR에서 완전히 범위 밖으로 제외하고
  언급조차 하지 않는다. 기각 — ADR-0006이 Connector Cancellation에 대해 이미
  보여준 절차(Domain 개념은 먼저 정의하고 실제 구현만 이연)를 따르지 않으면,
  Phase 6 이후 Cancellation이 필요해질 때 State Model을 다시 설계해야 한다.
  Domain 개념을 지금 정의해 두는 비용이 재설계 비용보다 훨씬 낮다.
- **대안 F**: Connector(ADR-0006)와 동일하게 Workflow Engine에도 Workflow
  Registry/Discovery/Capability 선언 구조를 도입한다(예: `jarvis.workflow`
  entry point group으로 여러 Workflow Engine을 자동 발견). 기각(사용자 지시,
  결정 12) — Workflow Engine은 HQ/Connector와 달리 여러 구현체가 동시에
  존재하며 런타임에 Capability로 선택되는 대상이 아니다. Composition Root가
  조립 시점에 하나만 선택하는 실행 엔진이므로, Registry 계층을 추가하면 실제로
  존재하지 않는 "여러 Workflow가 동시에 발견·경쟁한다"는 상황을 가정하게 되어
  불필요한 복잡도만 늘어난다. Adapter Reversibility는 Discovery 없이도 직접
  구성(direct construction) 교체만으로 충분히 증명된다(ADR-0003/0005가 이미
  보여준 방식).

## 영향 범위 (Impact)

- 수정(Core): `packages/core/.../ports/i_workflow_engine.py`에 `IWorkflowEngine`
  Interface 최초 정의(`run(team, dispatch) -> WorkflowResult`, 결정 9) — 현재
  빈 docstring 파일을 채우는 것이므로 신규 Port 추가와 동일하게 취급.
- 신규(Core): `WorkflowResult`, `WorkflowStatus`(결정 11) Domain Model.
- 신규 없음(의도적, 결정 12): Workflow Registry, Workflow Discovery, Workflow
  Capability 선언 — 이번 Phase는 이 세 가지 중 어느 것도 추가하지 않는다.
- 신규 없음(의도적, 결정 3): Agent Lifecycle State Machine — 이번 Phase는
  "Agent = Workflow 실행 단위"라는 역할 정의까지만 하고, Agent 전용 State
  Machine은 추가하지 않는다.
- 무수정: `packages/core/.../organization/entities.py`의 `Team`/`TeamState`
  전이 규칙 자체(결정 2 — Workflow Engine은 이를 소비만 함), `kernel/`,
  `policy/`, `lifecycle/`(HQ), `capability_registry/`, `connector_registry/`
  (ADR-0006, 이번 Phase에서 건드리지 않음). `HQ.select_division()`도
  무수정(결정 5, 최소 변경 원칙).
- 수정 범위 한정(Phase 5, 결정 3 최소 변경 원칙): `apps/poc-runner/main.py`
  Stage 8에서 Connector 호출 주체가 Composition Root → Agent로 이동하지만,
  이 이동에 필요한 만큼만 `connector/`(ADR-0006 Domain Model)를 Agent 실행
  경로에서 참조하도록 배선한다 — Connector Domain Model/Registry 자체(ADR-0006
  결정 12)의 구조는 변경하지 않는다.
- 구현 예정(Phase 5): `adapters/workflow-langgraph`(신규 구현 — 현재 docstring
  뿐인 스켈레톤을 채움).
- 수정 예정(Phase 5): `apps/poc-runner/main.py`의 `run_organization_layer()`가
  Stage 7~9를 직접 순차 호출하던 것을 `IWorkflowEngine.run()` 호출로 교체 —
  이 과정에서 Stage 8("Agent가 Connector를 호출한다"는 구조로의 이동, 결정 3)이
  자연스럽게 함께 정리된다. 정확한 배선 방식은 Implementation Plan에서
  확정한다.
- Architecture 변경 없음: Event Bus 자체의 기술 선정/구현은 이번 ADR/Phase의
  범위가 아니다(결정 8은 책임 경계만 확정, 구현은 v1.1 후보로 유지).

## Definition of Done

ADR-0003/0005/0006 공통 DoD에 더해 다음을 모두 만족해야 한다(Phase 5 승인 시).

- LangGraph Adapter가 기존 Kernel~Organization Layer 시나리오(기존 e2e 10개 +
  Phase 1~4 integration)를 동일하게 통과한다.
- **[최종 Architecture Validation 목표 1]** LangGraph를 제거하고 다른 Workflow
  Engine으로 교체해도 `packages/core`(Core)와 Organization Layer를 구현하는
  코드를 수정하지 않고 즉시 복구 가능함을 통합 테스트로 증명한다(Adapter
  Reversibility, 결정 4/12).
- **[최종 Architecture Validation 목표 2]** Stage 8에서 Agent가 Connector를
  직접 호출하는 구조(결정 3)가 Core(Kernel/HQ/Division 포함)를 수정하지 않고
  동작함을 통합 테스트로 증명한다 — 이때 Kernel의 Stage 1~5, HQ의 Division
  Selection(Stage 6), Division의 Agent Catalog 책임이 이 변경 전후로 동일하게
  유지되는지도 함께 확인한다(결정 3의 최소 변경 원칙).
- Team이 병렬로 구성된 Agent 중 일부가 실패해도 그 실패가 삼켜지지 않고
  `WorkflowResult`에 명시적으로 나타남을 계약 테스트로 증명한다(결정 6, No
  Silent Failure).
- Workflow 실행 중 예외가 발생해도 `IWorkflowEngine.run()`이 예외를 던지지
  않고 `WorkflowResult(status=FAILURE, ...)`를 반환함을 계약 테스트로 증명한다
  (Fail-Closed 계약의 Workflow 버전).
- Team의 Ephemeral 생명주기(FORMING→ACTIVE→COMPLETING→TERMINATED)가 LangGraph
  Adapter를 거쳐도 Core의 전이 규칙과 정확히 일치함을 증명한다(결정 2 — 전이
  규칙이 두 곳에서 분기하지 않음).
- Workflow Registry/Discovery/Capability 선언이 코드 어디에도 추가되지
  않았음을 git diff로 확인한다(결정 12).
- Agent 전용 State Machine(Agent Lifecycle)이 추가되지 않았음을 git diff로
  확인한다(결정 3의 Agent Lifecycle 범위 제외).

## 향후 적용

본 ADR은 Jarvis OS의 Workflow Execution Model(Workflow Engine의 책임, Team
생명주기 소비 방식, Agent 실행 모델, Team/Division 경계, Failure/Parallel/
Cancellation 정책, Workflow와 Event Bus의 책임 분리, Workflow State Model)의
기준 문서다. 향후 다른 Workflow Engine(LangGraph 외의 대안)이나 실제 Event Bus
기술이 선정될 때 모두 본 ADR을 상위 원칙으로 인용한다. Workflow Cancellation의
실제 구현 범위(결정 10에서 범위를 열어 둔 부분)와 병렬 실행 가능 여부 판단
스키마(결정 7)는 Phase 5 Implementation Plan에서 구체화하고, 필요시 후속
ADR/Roadmap 항목으로 이월한다.
