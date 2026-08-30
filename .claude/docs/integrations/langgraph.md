# LangGraph 도입 검증

검증일: 2026-08-30

## Summary

- LangGraph(1.2.11, LangChain 팀)는 State/Node/Conditional Edge/Loop/Checkpoint를 갖춘 Agent Workflow Runtime이다. 별도 임시 venv에서 실제 설치·실행해 핵심 기능(Loop 종료, Checkpoint 중단/재개, Persistence)을 전부 실제 로그로 검증했다(PASS).
- Jarvis OS v2 Architecture BASELINE은 AgentManager/WorkflowEngine/EventBus/Engine Adapter를 아직 **결정하지 않은 Kernel 책임 후보**로만 다룬다(§11, §10 Out of Scope) — LangGraph를 지금 배선할 대상 자체가 v2에는 없다.
- 이 저장소의 `archive/v1`이 이미 LangGraph를 `IWorkflowEngine` Adapter로 실사용 검증했고(ADR-0007, Phase 5), Sequential Adapter로 교체해도 Core 무수정임을 증명한 바 있다 — 이번 검증은 그 결론이 여전히 유효함을 최신 버전(1.2.11)으로 재확인했다.
- Claude-Mem/Task Observer/OmniRoute/Graphify/Context7 중 "Agent Workflow 실행 상태를 그래프로 관리하고 checkpoint하는" 기능을 가진 도구는 없다 — 역할 중복 없음.
- LangGraph는 `langchain-core`에만 의존하며 전체 `langchain` 패키지는 요구하지 않는다(설치 로그로 확인).
- **판정: 보류(조건부 채택 후보).** 도구 자체는 적합하지만, 현재 Development HQ MVP 단계는 Workflow/Runtime/Event Bus 구현을 명시적으로 금지한다(`IMPLEMENTATION_RULES.md`) — 도입은 v1 Phase 5와 동일하게, Kernel Runtime 존폐가 결정(ADC-02)되고 실제 구현 근거가 생긴 이후 별도 RFC로 판단한다.

## 1. 조사 — LangGraph 정체와 핵심 기능

- 공식 저장소: https://github.com/langchain-ai/langgraph (LangChain 팀)
- 최신 버전: **1.2.11** (`pip index versions langgraph`로 확인, 2026-05 출시된 1.2 계열의 최신 패치)
- 핵심 개념: `StateGraph`(TypedDict 기반 공유 State) → `Node`(Python 함수) → `Edge`/`Conditional Edge`(라우팅 규칙) → `graph.compile()`로 실행 가능한 그래프 생성.
- Checkpoint: `MemorySaver`(개발용) / `PostgresSaver`(운영용) 등 pluggable Checkpointer가 매 super-step마다 State를 저장 — pause/resume, time-travel debugging, human-in-the-loop 중단점의 기반.
- Human-in-the-loop: `interrupt_before`/`interrupt_after`로 특정 Node 실행 전후에 멈추고, `graph.update_state()` + `graph.invoke(None, config)`로 정확히 그 지점부터 재개.

Sources:
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [Human-in-the-loop - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)

## 2. PoC — 실제 실행 Evidence

별도 임시 디렉터리(`scratchpad/langgraph-poc`, 이 저장소 밖)에 독립 venv를 만들어 `langgraph==1.2.11`을 설치하고 실행했다. Kernel/Architecture/MVP 코드는 변경하지 않았다(`git status --short` 클린 확인).

```bash
python3 -m venv venv && source venv/bin/activate
pip install langgraph==1.2.11
```

### 2.1 State → Node → Conditional Edge → Loop → 종료

시나리오: "목표값(10) 이상이 될 때까지 3씩 더하는 Loop" — `increment` Node가 조건부 Edge(`should_continue`)로 자기 자신에게 돌아가거나 `finalize`로 빠져나간다.

실제 실행 결과:

```
=== 1) State -> Node -> Conditional Edge -> Loop -> 종료 (checkpoint 없음) ===
  attempt 1: value -> 3
  attempt 2: value -> 6
  attempt 3: value -> 9
  attempt 4: value -> 12
  finalized at value=12 after 4 attempts
최종 state: {'value': 12, 'target': 10, 'attempts': 4}
PASS: loop이 조건을 만족할 때까지 반복 후 종료함
```

### 2.2 Checkpoint/Persistence (핵심 장점 추가 검증)

`MemorySaver`로 컴파일하고 `interrupt_before=["increment"]`를 지정해 매 Node 실행 전 중단시킨 뒤, 동일 `thread_id`로 `invoke(None, config)`를 반복 호출해 checkpoint에서 이어서 실행되는지 확인했다.

```
=== 2) Checkpoint/Persistence 검증 (MemorySaver, 중단 후 재개) ===
  최초 invoke: interrupt 직후 상태 -> value=0, attempts=0
  재개 1: value=3, attempts=1, next=('increment',)
  재개 2: value=6, attempts=2, next=('increment',)
  재개 3: value=9, attempts=3, next=()
PASS: 중간에 멈춘 뒤(checkpoint) 동일 thread_id로 재개하여 끝까지 실행 완료함

checkpoint 히스토리 개수: 6 (매 super-step마다 하나씩 저장됨)
PASS: MemorySaver가 super-step마다 checkpoint를 실제로 저장함
```

전체 스크립트(`poc.py`)와 원본 실행 로그(`poc_output.txt`)는 세션 종료와 함께 사라지는 임시 디렉터리에만 있다 — 이 문서의 로그 인용이 재현 결과의 기록이다. 재현 절차: 위 설치 명령 + 본 절의 시나리오를 동일하게 구현하면 동일 결과가 나온다.

### 2.3 LangChain 의존성 범위 확인

```
$ pip show langgraph
Requires: langchain-core, langgraph-checkpoint, langgraph-prebuilt, langgraph-sdk, pydantic, xxhash
```

`langgraph`는 **`langchain-core`(타입/메시지/Runnable 인터페이스)에만 의존하고, 전체 `langchain` 패키지(LLM Provider 통합, Chain, Agent 프리셋)는 요구하지 않는다** — 설치된 패키지 목록에 `langchain`(non-core) 자체는 없다. LangGraph 단독 사용이 가능함을 확인했다.

## 3. Architecture 적합성 — Jarvis OS BASELINE과의 경계 비교

과제가 지정한 "AgentManager, WorkflowEngine, EventBus, Engine Adapter"는 v2 BASELINE에 **그 이름 그대로 존재하지 않는다.** 대신 BASELINE §11 Kernel 책임 후보 표가 이렇게 대응한다:

| 과제가 지정한 개념 | v2 BASELINE 대응 | 현재 상태 |
|---|---|---|
| WorkflowEngine | Task 전달 책임 → Scheduler(구현 후보) | **미결**(§14.1 "Task 전달 책임 — 이 계약의 범위 밖") |
| AgentManager | §7 "Agent 구성 및 역할 결정"은 HQ 책임으로 이미 확정 | Kernel이 아니라 HQ 책임(N-3, 이미 확정) |
| EventBus | §6 "Event는 HQ 경계를 가로질러 전파된다"(Concept만 존재) | 구현 자체가 MVP 단계에서 명시적으로 금지(`IMPLEMENTATION_RULES.md`: "Event Bus 구현 금지") |
| Engine Adapter | Engine 호출 책임 → Engine Gateway(구현 후보) | **미결**, 현재는 "단일 함수로 Engine 호출"만 허용 |

즉 LangGraph가 대체하거나 통합될 자리(Runtime/Workflow/Scheduler) 자체가 v2에서는 **ADC-02(Runtime 존폐)가 여전히 Open**이라 아직 만들어지지 않았다. Kernel은 "무엇이 Kernel 책임인지"만 정의했을 뿐(§11~§15), Component 구현은 §10 Out of Scope다.

### 3.1 v1(archive)의 선행 검증 — 이미 답한 질문

이 저장소의 `archive/v1`에서 LangGraph는 이미 `IWorkflowEngine` Port의 구현체(`LangGraphWorkflowEngine`)로 **실사용 검증**되었다(ADR-0007, Phase 5, 2026-08-03):

- LangGraph의 `StateGraph`/Node/`START`/`END` 문법이 `adapters/workflow-langgraph` 내부에만 존재 — Core(`packages/core`)는 5개 Phase 전체에 걸쳐 LangGraph를 알지 못한 채 유지됨(git diff로 반복 검증).
- **Adapter Reversibility 증명**: LangGraph를 제거하고 `SequentialWorkflowEngine`(순수 함수 호출)으로 교체해도 Core/Organization Layer 무수정 — `test_workflow_adapter_reversibility.py` (Contract Parity 3건 + Reversibility 1건 + Fail-Closed 3건).
- Team 생명주기 전이(`activate()`/`complete()`/`terminate()`) 규칙은 `organization/entities.py`에 그대로 남고, LangGraph는 그 호출 순서만 조립 — Workflow Engine이 "무엇을 실행할지"를 결정하지 않는다는 Kernel 원칙(§7 System Boundary, "Jarvis OS가 책임지지 않는 것: Workflow의 도메인 내용")과 일치.
- Known Gap으로 남은 것: 그래프 재컴파일 오버헤드(`run()`마다 재컴파일), 병렬 fan-out의 실제 동시성 미검증(구조만 검증), Workflow Cancellation 미구현.

이번 세션의 PoC는 이 v1 결론(경계 준수 가능)이 **최신 LangGraph 버전(0.2.x대 → 1.2.11)에서도 API 수준에서 여전히 성립**함을 별도 확인한 것이다 — `StateGraph`/`add_conditional_edges`/`compile()` 핵심 API는 하위 호환을 유지하고 있었다.

### 3.2 Kernel Design Principle과의 정합성

- **KP-1(Responsibility over Component)**: LangGraph를 Kernel 자체로 채택하는 것이 아니라, 미결 상태인 "Workflow Engine 책임"의 구현 후보(Adapter) 하나로 다루는 것만 원칙과 합치한다 — v1이 실증한 방식.
- **KP-5(Implementation Agnostic)**: LangGraph의 `StateGraph`/`TypedDict` 문법이 Domain Model(Team/Agent 등)에 새지 않고 Adapter 내부에만 머물러야 한다 — v1의 `_WorkflowState` 변환 경계가 그 실례.
- **§7 System Boundary**: "Workflow의 도메인 내용"은 Jarvis OS(Kernel) 책임이 아니다 — LangGraph의 Node/Edge 내용(무엇을 실행하는가)은 HQ가 정의해야 하며, Kernel/Adapter가 대신 정의하면 경계 위반이다.

## 4. 해결/확인된 사항

1. LangGraph 최신 버전(1.2.11)의 State/Node/Conditional Edge/Loop/종료 구조를 실제로 구성·실행해 정상 동작을 확인했다(2.1).
2. Checkpoint/Persistence(중단 후 재개, `MemorySaver`)를 실제로 검증했다(2.2) — Human-in-the-loop의 기반 메커니즘이 실제로 동작함을 확인.
3. LangGraph는 `langchain-core`에만 의존하고 전체 `langchain`은 요구하지 않는다 — 무거운 의존성 없이 단독 사용 가능(2.3).
4. Claude-Mem(세션 간 대화 요약)/Task Observer(skill 관찰)/OmniRoute(Provider 라우팅)/Graphify(코드 구조 그래프)/Context7(라이브러리 문서 조회) 중 "Agent Workflow 실행 상태 관리+checkpoint" 기능을 가진 도구는 없음을 확인했다 — 역할 중복 없음.
5. `archive/v1`이 이미 LangGraph를 Kernel 경계를 지키며(Adapter Reversibility 포함) 실사용 검증한 선례가 있고, 이번 PoC로 그 결론이 최신 버전에서도 유효함을 확인했다.

## 5. 남은 사항

- v2 BASELINE에는 LangGraph가 채워질 자리(WorkflowEngine/Scheduler/Engine Gateway) 자체가 아직 없다 — ADC-02(Runtime 개념 존치 여부)가 Open인 한 이 자리는 열리지 않는다.
- v1의 Known Gap(그래프 재컴파일 오버헤드, 병렬 fan-out의 실제 동시성 미검증, Cancellation 미구현)은 이번 세션에서 재검증하지 않았다 — 실제 도입 시점에 다시 확인이 필요하다.
- 이번 PoC는 단일 Node Loop 수준이며, v1이 이미 검증한 "Agent별 Node로 fan-out/fan-in하는 병렬 구조"까지는 재현하지 않았다 — 이미 v1 Evidence가 있으므로 중복 검증하지 않았다.
- `PostgresSaver` 등 운영급 Checkpointer, 실제 human-in-the-loop UI 연동은 검증 범위 밖이다(`MemorySaver` in-memory만 검증).

## 6. 도입 판단: **보류 (조건부 채택 후보)**

- **채택하지 않는 이유**: Development HQ 현재 MVP 단계는 Workflow Parser/Scheduler/Runtime orchestration/Event Bus 구현을 `IMPLEMENTATION_RULES.md`가 명시적으로 금지한다. LangGraph를 지금 배선하면 그 금지를 우회하는 것이 된다 — 도구가 아무리 적합해도 현재 Governance 상태에서는 채택 대상이 아니다.
- **제외하지 않는 이유**: 도구 자체의 기능(State/Node/Conditional Edge/Loop/Checkpoint)과 Architecture 정합성(Kernel 경계를 지키는 Adapter로 배선 가능)은 실제 실행 Evidence와 v1 선례로 이미 검증되었다. 역할 중복도 없다.
- **재검토 조건**: (1) ADC-02(Runtime 존폐)가 Accept로 판정되고, (2) 실제 Multi-Task/Workflow orchestration 구현 근거(Implementation Stop Trigger 또는 Kernel Extraction Candidate)가 발생하면, 그때 RFC → ADC → ADR 절차로 LangGraph를 Workflow Engine 구현 후보 중 하나로 정식 평가한다 — v1 ADR-0007과 이 문서가 그 시작점이 된다.
- 이번 세션은 Kernel/Architecture/MVP 코드를 변경하지 않았다(`git status --short` 클린 확인) — PoC는 저장소 밖 임시 디렉터리에서만 수행했다.
