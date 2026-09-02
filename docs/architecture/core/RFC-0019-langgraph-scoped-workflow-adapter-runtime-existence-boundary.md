# RFC-0019: LangGraph as Scoped Workflow Adapter Candidate — Runtime Existence Boundary (ADC-02/ADC-0008 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/decisions/adc/ADC.md` ADC-02("Runtime 개념의 존폐") — Open·NOW.
`docs/architecture/baseline/BASELINE.md` §6이 정의한 넓은 Runtime 책임
("Workflow를 참조하여 Task를 Agent에게 배분") 중, §16.3(Execution
Host)·§16.4(Multi-Task)·§16.5(Multi-Task Result Store)가 이미 좁혀
Accept한 부분을 **제외한 나머지** — 조건부 분기(Conditional Edge)와
Loop을 포함하는 Workflow 그래프 해석·실행 — 를 이 RFC가 연다.
**Evidence**: `archive/v1/docs/adr/0007-workflow-execution-model.md`
(Accepted, `LangGraphWorkflowEngine` 실사용 검증 완료),
`archive/v1/adapters/workflow-langgraph/src/jarvis_adapter_workflow_langgraph/langgraph_engine.py`,
`archive/v1/docs/poc/health-reports/phase-5-workflow-langgraph.md`,
`.claude/docs/integrations/langgraph.md`(이번 세션 PoC — State/Node/
Conditional Edge/Loop/Checkpoint 실행 Evidence, langgraph 1.2.11),
`docs/architecture/baseline/BASELINE.md` §6·§7·§16.1~16.6,
`docs/decisions/adc/ADC.md` ADC-02,
`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`,
`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`,
`docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md`,
`docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`,
`docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md`,
`docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md`,
`hqs/investment/checkpoint.py`,
`docs/core/execution-layer/MVP-0001-plan.md`(Engine Adapter 용어
확인), `hqs/development/IMPLEMENTATION_RULES.md`. 새로운 실험은
수행하지 않는다 — 이미 병합/기록된 v1 Evidence와 이번 세션에서
저장소 밖 임시 디렉터리에서 실행하고 기록만 남긴 PoC만 인용한다.

> 본 RFC는 ADC-02(Runtime 개념의 존폐)를 대신 판정하지 않는다.
> LangGraph 도입을 승인하지 않는다. Scheduler/Engine Gateway 등
> 대체 구조를 설계하지 않는다. Workflow Adapter의 명칭을 확정하지
> 않는다(Execution Host가 `ADC-0014`로 별도 명명 절차를 거친 것과
> 같은 절차가 필요하면 후속 ADC가 담당한다). `hqs/investment/checkpoint.py`의
> 교체를 제안하지 않는다. 코드·Baseline·ADC·ADR·CLAUDE.md를 수정하지
> 않는다. 이 RFC가 여는 것은 좁은 질문 하나다: **"§16.3~16.5가 이미
> Accept한 범위를 넘어서는 Workflow 그래프 해석·실행 책임(조건부
> 분기·Loop 포함)이, LangGraph라는 구체적으로 검증된 Adapter Evidence를
> 근거로 지금 재검토 대상이 될 수 있는가?"**

## 0. 이 RFC가 열린 이유

`ADC-0008`은 ADC-02의 넓은 질문("유지" 대 "대체")을 Not Accepted로
남기면서 재검토 조건 두 가지를 제시했다 — (1) "Core Component 검토"
원문 확보, (2) Runtime 미결정으로 인한 반복 관찰 축적. `ADC-0013`은
조건 (2)를 근거로 그 질문을 "단일 실행 단위의 dispatch·격리"로
좁혀 Accept했고(§16.3, Execution Host), `ADC-0016`·`ADC-0017`이 각각
"독립 Task 동시 실행·결과 수집"(§16.4)과 "저장 전 검증 게이트"(§16.5)로
추가로 좁혀 Accept했다. 세 Accept 모두 스스로 "§6의 넓은 정의(Workflow
그래프 해석, Multi-Task를 Agent에게 배분)로의 확장 여부는 결정하지
않는다"고 명시적으로 한정했다 — 그 확장, 특히 **조건부 분기와 Loop**은
지금도 미검토 상태다.

한편 이 저장소의 `archive/v1`은 이미 이 미검토 영역에 해당하는 실행을
LangGraph로 실사용 검증한 이력이 있다(`ADR-0007`, Phase 5, Accepted).
이번 세션은 그 검증이 v2 시점(langgraph 1.2.11)에도 API 수준에서
유효함을 별도 PoC로 재확인했다(`.claude/docs/integrations/langgraph.md`).
이 RFC는 이 두 Evidence(v1의 실전 검증 + 이번 세션의 최신 버전 재확인)를
근거로, ADC-02의 넓은 질문 전체가 아니라 그 안의 좁은 부분
집합 하나("조건부 분기·Loop을 포함하는 Workflow 그래프 실행 책임을
LangGraph Adapter로 담당할 수 있는가")만 정식 Boundary Question으로
연다 — `RFC-0013`/`RFC-0016`/`RFC-0017`이 반복해 온 것과 동일한
절차적 선례(넓게 묻지 않고 좁게 묻는다)를 따른다.

## 1. Problem Statement

§16.3~16.5의 세 차례 Accept로 Runtime의 일부(단일 실행 단위 격리,
독립 Task 동시 실행, 저장 게이트)는 v2에 안착했다. 그러나 이 셋을
합쳐도 **"이미 고정된 소수의 독립 실행 단위를 동시에 시작하고 결과를
모으는 것"**까지만 가능하다 — 어떤 다음 단계로 갈지 실행 중 상태에
따라 갈라지는 것(Conditional Edge), 조건을 만족할 때까지 같은 단계를
반복하는 것(Loop), 그 중간 상태를 저장했다가 이어서 실행하는 것
(Checkpoint/Resume)은 세 Accept 모두가 "제외"로 명시한 영역이다
(§16.4: "우선순위 판단, 조건부 분기, Workflow 그래프 해석, Agent
동적 선택은 포함하지 않는다").

Jarvis OS가 §3 Core Principles에서 "Build < Integrate"(직접 구현보다
기존 오픈소스 통합을 우선한다)를 명시하고 있고, 이 저장소 안에
이미 이 정확한 문제(조건부 분기·Loop이 있는 Workflow 실행)를 실전
검증한 오픈소스 Adapter(LangGraph, v1 `ADR-0007`)와 그 검증이 최신
버전에서도 유효하다는 재확인(이번 세션 PoC)이 존재한다. 이 RFC는
"이 두 Evidence가 §16.3~16.5 너머의 좁은 부분집합 하나를 재검토할
만큼 구체적인가"를 묻는다 — LangGraph를 채택하자는 제안이 아니라,
**그 질문을 지금 열 근거가 있는지**를 검토 대상으로 올리는 것이다.

## 2. Evidence Summary — 이미 기록된 것만 인용

### 2.1 Architecture Intent — BASELINE이 이미 표시한 설계 의도

- §6 Concept Model: *"Workflow는 Task들의 실행 순서(그래프)를
  정의한다"*(Definition으로 분류), *"Runtime은 Workflow를 참조하여
  Task를 Agent에게 배분한다"*(Service로 분류). Workflow라는 개념
  자체는 Concept Model에 이미 있다 — Runtime이라는 Service가 그것을
  "어떻게" 참조·배분하는지가 미결일 뿐이다.
- §7 System Boundary: *"Jarvis OS가 책임지지 않는 것 — Workflow의
  도메인 내용."* Workflow의 **내용**(무엇을 실행하는가)은 처음부터
  Kernel 책임이 아니라고 확정돼 있다 — 이 RFC가 다루는 것은 내용이
  아니라 **그 내용을 실행하는 그래프 해석·조립 책임의 소재**다.
- §16.6: Workflow는 Kernel Module 후보로 검토됐으나 Defer됐다
  (`ADC-0001` Module 2). 이는 ADC-02와 별개의 축(Module 존재 여부)
  이지만 같은 결론(아직 결정할 재료가 없다)을 가리킨다.

### 2.2 실제 필요성 — v1의 실전 검증 + 이번 세션의 재확인

- **v1 `ADR-0007`(Accepted)**: LangGraph를 `IWorkflowEngine` Port의
  구현체로 실사용 검증했다 — Team 생명주기 전이 규칙은 Core에 남기고
  (결정 2), LangGraph는 그 호출 순서만 조립하며(결정 1), 병렬
  fan-out/fan-in 구조를 실제로 구성했고(결정 7), **Adapter
  Reversibility**를 통합 테스트로 증명했다(결정 4 — LangGraph를
  제거하고 `SequentialWorkflowEngine`으로 교체해도 Core/Organization
  Layer 무수정, `test_workflow_adapter_reversibility.py`).
- **이번 세션 PoC**(`.claude/docs/integrations/langgraph.md`): 별도
  임시 디렉터리에서 langgraph 1.2.11을 설치해 State→Node→Conditional
  Edge→Loop→종료를 실제로 실행했고(4회 반복 후 정상 종료),
  `MemorySaver` Checkpointer로 중단 후 동일 `thread_id` 재개가
  실제로 동작함을 확인했다(checkpoint 히스토리 6건). `langgraph`는
  `langchain-core`에만 의존하고 전체 `langchain` 패키지는 요구하지
  않는다는 것도 확인했다 — v1 PoC 시점(0.2.x대)과 API 표면
  (`StateGraph`/`add_conditional_edges`/`compile()`)이 하위 호환을
  유지하고 있음을 별도로 재확인한 것이다.
- 두 Evidence를 합치면: "조건부 분기·Loop이 있는 Workflow 실행"이라는
  §16.4가 제외한 영역에서, 실제로 동작하는 구체적 구현체가 **Core를
  전혀 수정하지 않고** 그 영역을 채울 수 있다는 것이 한 번(v1)
  실증되었고, 최신 버전에서도 그 능력이 유지된다는 것이 한 번(이번
  세션) 더 확인되었다.

### 2.3 남아 있는 공백 — 이 RFC가 채우지 않는 것

- **Governance v2 Rule B(3건 이상 독립 관찰)를 채우지 않는다.**
  Evidence는 사실상 2건(v1 Phase 5 + 이번 세션)이며, 둘 다 같은
  계보(LangGraph)이고 프로덕션 트래픽이 아닌 PoC/Phase 검증이다.
  `ADC-0016`이 1건으로도 Accept했던 것은 "범위를 극도로 좁혔기
  때문"(§16.4의 "포함" 목록 참고)이었지 Rule B를 면제받은 것이
  아니다 — 이 RFC도 동일한 전제 위에서만 좁게 열 수 있다.
- **v1과 v2는 같은 Architecture가 아니다.** v1은 Team/Division을
  Core Domain Model로 가졌으나(`packages/core/organization/entities.py`),
  v2 Meta Architecture(§5)는 *"Division과 Team은 HQ 내부에서
  선택적으로 사용할 수 있는 구조이며, Jarvis OS는 그 존재 여부를
  알지 못한다"*고 명시한다 — v1 `ADR-0007`의 Team 중심 결정들은
  v2에 그대로 이식할 수 없다(§5에서 재해석).
- **Investment HQ의 기존 `checkpoint.py`와의 관계가 아직 정리되지
  않았다.** 같은 "Checkpoint"라는 단어를 쓰지만 책임 범위가 다르다
  (§6에서 정리).
- Multi-HQ, 자연어 요청 분해(`ADC-0018`, Defer) 범위는 다루지 않는다
  — 이 RFC는 단일 HQ 안에서의 Workflow 그래프 실행만 연다.

## 3. 용어 충돌 정리 — Workflow Adapter(LangGraph)와 Engine Adapter(Model/LLM)

이 RFC가 다루는 대상을 정확히 하기 위해, v2 저장소에 이미 존재하는
"Engine Adapter"라는 용어와 명시적으로 구분한다.

| 용어 | v2에서의 실제 의미 | 근거 | 이 RFC와의 관계 |
|---|---|---|---|
| **Engine Adapter** (v2 기존 용법) | Model/LLM Provider 호출 어댑터 — "코드 생성·실행·테스트, Model/Engine 선택·호출"(§16.2 Execution Layer의 일부) | `docs/core/execution-layer/MVP-0001-plan.md` Out of Scope("Model Routing / Engine Adapter 구현"), `BASELINE.md` §16.2 | **이 RFC의 대상이 아니다.** §16.2는 이미 Accept됐고 이 RFC는 그 내부(Model 선택·재시도 정책)를 건드리지 않는다 |
| **Workflow Adapter** (이 RFC가 다루는 대상, v1 용어 계승) | HQ가 정의한 Task 그래프(Conditional Edge·Loop 포함)의 실행 순서를 조립·진행시키는 어댑터 — v1 `IWorkflowEngine`의 v2 대응 개념 | v1 `ADR-0007` 결정 9, `BASELINE.md` §6 Runtime/Workflow 정의 | **이 RFC가 다루는 대상.** LangGraph는 이 역할의 후보 구현체이지, Model 호출 자체를 담당하지 않는다 |

두 Adapter는 계층이 다르다 — Workflow Adapter가 "어떤 Agent를 어떤
순서로 실행할지"를 조립하면, 그 Agent 실행 **내부**에서 필요하면
Engine Adapter(§16.2)가 별도로 Model을 호출한다. Workflow Adapter는
Engine Adapter를 대체하거나 흡수하지 않는다 — 이 구분은 v1 `ADR-0007`
결정 3("Agent의 실행 내용은 Connector Execution Model을 따른다")이
Workflow Engine과 Connector 호출을 분리한 것과 같은 원칙이다.

## 4. LangGraph 담당 범위 vs Core 고유 책임

| LangGraph(Workflow Adapter)가 담당할 수 있는 범위 | Core가 계속 소유해야 하는 책임 (LangGraph가 소유·대체하지 않음) |
|---|---|
| State(공유 실행 상태) 표현 | HQ Routing/Registry — 어떤 HQ가 선택되는가. **v2에 "Kernel Stage"라는 확정된 구조는 없다** — 이 표현은 v1(`archive/v1` `ADR-0007` 배경)에서 온 것이고, `BASELINE.md` §10은 Kernel Component Architecture(Stage 구성 포함)를 여전히 Out of Scope로 둔다. 이 RFC는 v2에 몇 개의 Stage가 있는지, 그런 구조 자체가 있는지조차 전제하지 않는다 — "HQ가 선택된다"는 §7 System Boundary("HQ/Agent의 등록과 발견")가 이미 확정한 사실만 인용한다 |
| Node(단일 실행 단계) | Capability 탐색·Capability/Connector Registry — 어떤 Agent가 어떤 Capability로 발견되는가 |
| Conditional Edge(조건부 분기) | Policy 판정 — Agent가 이 Capability를 써도 되는지(PDP/PEP) |
| Loop(조건 만족까지 반복) | Domain Lifecycle 전이 규칙 — HQ/Agent의 상태 전이 자체(HQ가 소유하는 Domain 로직을 Adapter가 재구현하지 않는다, v1 `ADR-0007` 결정 2·대안 B 기각과 동일 원칙) |
| Workflow 그래프 실행(조립·진행) | Event Bus — §16.6 Defer 상태, 이 RFC와 무관하게 별개 |
| Checkpoint/Resume(그래프 실행 상태의 pause·재개) | Investment HQ Result Store 저장 게이트(§16.5) — **이 표의 좌우는 1:1 대응도, 대체 관계도 아니다**(두 "Checkpoint"는 계층이 다르다, §6에서 별도로 정리) |

이 표는 v1 `ADR-0007` 결정 1("무엇을 실행할지 결정하지 않는다"),
결정 4("HQ~Agent 사이의 실행 엔진일 뿐, Kernel 전체를 대신하지
않는다")의 v2 버전이다 — v1이 Kernel Routing/Policy/HQ Registry로
표현한 것을 v2 Kernel Public Contract(§14)·System Boundary(§7) 용어로
재진술했다.

## 5. v1 ADR-0007의 v2 재해석

v1의 12개 결정을 그대로 옮기지 않는다 — v1과 v2는 Concept Model이
다르다(§2.3). 아래는 각 결정이 v2에서 여전히 성립하는지, 성립한다면
어떤 용어로 다시 말해야 하는지를 정리한 것이며, 이 RFC가 그중 어느
것도 확정하지 않는다(모두 후속 절차 대상).

| v1 결정 | v1의 전제 | v2 재해석 | v2에서 달라지는 점 |
|---|---|---|---|
| 결정 1(무엇을 실행할지 결정 안 함) | Division Selection(HQ 책임) 이후부터 개입 | 그대로 성립 — §7이 이미 "Workflow 도메인 내용은 HQ 책임"으로 확정 | 없음 |
| 결정 2(생명주기는 Core 소유, Adapter는 소비만) | `Team.activate()`/`complete()`/`terminate()`가 Core Domain 메서드 | v2는 Team을 Kernel이 모른다(§5) — Adapter가 소비할 대상은 **HQ 내부에서 정의한 Agent/Task 단위의 전이**이지, Kernel이 정의한 Team 상태 머신이 아니다 | v2 Kernel에는 이 "소비할 생명주기"가 아직 없다 — HQ마다 다를 수 있음. 이 자체가 후속 Open Question |
| 결정 3(Agent = 실행 단위, Agent 전용 State Machine 없음) | Agent dataclass가 Core Domain Model | v2도 Agent는 §6 Entity로 존재 — 원칙은 유지 가능 | 없음 |
| 결정 4(Adapter Reversibility) | LangGraph 제거해도 Core 무수정 | v2 KP-1(Responsibility over Component)·Adapter Reversibility 원칙과 그대로 정합 | 없음 — 오히려 v2가 이 원칙을 더 명시적으로 요구(§14.4 Hidden, §14.5 Extension Point) |
| 결정 5(Team/Division 경계) | Team↔Division 두 계층 구분 | **v2에 대응 개념 없음** — §5가 Division/Team을 Kernel이 알지 못하는 HQ 내부 구조로 명시 | 이 결정 자체를 v2로 이식할 수 없다. Workflow Adapter는 HQ가 이미 만든 실행 단위(내부에 Team/Division이 있든 없든)만 받는다는 형태로 재정의해야 함 — 후속 절차 대상 |
| 결정 6(Failure 2층 구분, No Silent Failure) | Fail-Closed 계약(ADR-0006) | v2도 §14.3 G-6(No Silent Failure)와 동일 원칙 존재 | 용어만 Kernel Public Contract 쪽으로 정렬 필요 |
| 결정 7(Parallel Execution 원칙) | 병렬 가능 여부는 Domain 설계 시점의 명시적 선언 | §16.4(Multi-Task)의 "이미 고정된 소수 실행 단위"·"기존 Agent 재사용" 조건과 원칙적으로 합치 | §16.4는 이미 Accept된 반면 Conditional Edge/Loop을 곁들인 병렬은 여전히 §16.4 밖 — 이 RFC가 여는 질문과 직결 |
| 결정 8(Event Bus 분리) | Task 흐름(수직) vs Event 흐름(수평) 구분 | v2 §6도 동일 구분(Task Flow vs Event Flow)을 이미 갖고 있음 | 없음 — Event Bus는 §16.6 Defer로 별개 |
| 결정 9(`IWorkflowEngine` Port) | Team/`TaskDispatch` 입력, `WorkflowResult` 반환 | v2는 이 Port 자체가 아직 없다(§14.1: Task 전달·Engine 호출 책임은 "미결 — 계약 범위 밖") | **새 Public Contract를 만들 근거가 아직 없다** — 이 RFC는 §7 Pseudo-Contract를 "제안 수준"으로만 다룬다 |
| 결정 10(Cancellation) | Domain 개념만 정의, 구현은 이연 | v2도 동일하게 다룰 수 있음(개념 정의와 구현 분리는 v2 원칙과도 합치) | 없음 |
| 결정 11(WorkflowStatus 등 State Model) | `TeamState`와 별개 축 | v2에 `TeamState` 대응 없음(위 결정 5와 동일 사유) | Team 대신 무엇의 상태를 나타낼지 후속 절차 대상 |
| 결정 12(Workflow는 Plugin이 아님, Registry 없음) | Composition Root가 직접 구성 | v2도 §10 Out of Scope(Registry 구현 금지)·`IMPLEMENTATION_RULES.md`(Registry 일반화 금지)와 정합 | 없음 — 오히려 v2가 더 엄격하게 금지 |

**재해석의 결론**: v1의 원칙 대부분(1, 3, 4, 6, 8, 10, 12)은 v2로
그대로 옮길 수 있다. 그러나 4개 결정(2, 5, 9, 11)은 **재설계가
필요한 진짜 공백**이며, 그 원인은 하나로 묶이지 않는다.

- **결정 2·5·11**의 공백 원인은 **Team/Division 부재**다 — v2
  Concept Model(§5 Meta Architecture)에 Team/Division 대응물이
  없어, Core가 소비할 생명주기(결정 2)·경계(결정 5)·State Model
  (결정 11)을 그대로 옮길 수 없다.
- **결정 9**(`IWorkflowEngine` Port)의 공백 원인은 Team 부재가
  **아니다** — v2 Kernel Public Contract §14.1이 "Task 전달 책임"을
  여전히 "미결 — 계약 범위 밖"으로 두고 있기 때문이다. Port의
  입력 절반(Team)은 결정 2·5와 같은 사유로 막혀 있지만, 나머지
  절반(`TaskDispatch`/`WorkflowResult` 계약 자체)은 §14.1이라는
  별개의, 더 상위의 미결 사유를 갖는다.

두 원인은 서로 다른 절차로 해소된다 — Team/Division 공백은 이
Boundary Question(§8)이 Accept될 경우 그 후속 ADC/ADR이 다루지만,
§14.1의 Task 전달 책임 자체는 이 RFC의 범위보다 상위의, 별도로 이미
Open인 Kernel Public Contract 확장 질문이다(§14.1 표 참조 — 이 RFC로
해소되지 않는다).

## 6. §16.3~16.5 기존 Accept와의 관계

- **Execution Host(§16.3)와 겹치지 않는다.** Execution Host는 "이미
  dispatch가 결정된 단일 실행 단위"의 실행 격리만 다룬다(§16.3
  "이 Accept가 결정하지 않는 것" 참조). Workflow Adapter는 그 반대편
  질문 — "무엇을, 어떤 순서로, 어떤 조건으로" dispatch할지 — 을
  다룬다. `ADC-0016` §Q3의 구도(Execution Host=Isolation,
  Multi-Task=Coordination)를 그대로 연장하면, Workflow Adapter는
  **Coordination의 조건부·반복 확장**이다.
- **Multi-Task(§16.4)를 넓히지 않는다.** §16.4는 "이미 고정된 소수의
  독립 실행 단위"만 다룬다. Workflow Adapter가 다루는 것은 그
  "고정" 자체가 실행 중 조건에 따라 달라지는 경우(Conditional Edge)와
  같은 단계가 반복되는 경우(Loop)다 — §16.4가 명시적으로 제외한
  바로 그 영역이며, 이 RFC는 §16.4의 범위를 수정하자는 것이 아니라
  그 옆의 빈 자리를 여는 것이다.
- **Investment HQ Result Store(§16.5)를 대체하지 않는다.** 이름이
  겹치는 "Checkpoint"를 명확히 구분해야 한다.

  | | §16.5 Multi-Task Result Store | LangGraph Checkpointer(이 RFC 대상) |
  |---|---|---|
  | 책임 | 저장 **직전** 결과의 유효성 검증 게이트 | 그래프 실행 **전체 상태**의 pause/resume |
  | 실증 사례 | `hqs/investment/checkpoint.py`(Production, 4회 재현 Evidence) | v1 `LangGraphWorkflowEngine` + 이번 세션 PoC(`MemorySaver`) |
  | 대상 | Investment HQ에 한정(§16.5 "Investment HQ 관찰에 한정") | HQ 무관, Adapter 자체의 실행 메커니즘 |
  | 이 RFC의 입장 | **건드리지 않는다** — §16.5 책임은 그대로 유지, 대체 제안 없음 | 이 RFC가 여는 Boundary Question의 대상(§8) |

  두 "Checkpoint"는 계층이 다르다 — §16.5는 Result **저장** 시점의
  검증 게이트이고, LangGraph Checkpointer는 그래프 **실행** 시점의
  중단·재개 메커니즘이다. 하나가 다른 하나를 함의하지 않는다.
  Investment HQ가 향후 Workflow Adapter를 실제로 쓰게 되더라도,
  `checkpoint.py`의 저장 전 검증 책임은 §16.5 그대로 유지되고 별도
  절차 없이 자동으로 대체되지 않는다.

## 7. Pseudo-Contract — Workflow Adapter Port (제안 수준, 실행 가능한 코드 아님)

아래는 §4 재해석·§9 결정 9가 남긴 공백을 메우기 위한 **개념적
계약**이다. 함수 시그니처, 클래스, import 가능한 파일이 아니다 —
Kernel Design Principle KP-1("Kernel은 구현으로 정의하지 않는다")과
v1 `ADR-0007`이 스스로 "API를 정의하지 않는다"고 한 것과 같은 수준을
유지한다. 이 절은 실제 코드를 만들지 않으며, Accept되더라도 실제
Interface 정의는 별도 ADR/Implementation Plan의 몫이다.

**책임(Responsibility)**

- HQ가 이미 정의한 Workflow(Task 그래프, §6 Definition)와 이미
  구성된 Task 실행 단위(누가 언제 무엇을 하는지, HQ가 결정) 를
  입력으로 받아, 그 그래프가 기술하는 순서·분기·반복을 실제로
  진행시킨다.
- 진행 중 상태(어느 Node에 있는지, 무엇을 반복 중인지)를 값으로
  들고, 필요하면 그 값을 외부(호출자)가 들고 있다가 다시 넘겨받아
  이어서 진행할 수 있게 한다(Checkpoint/Resume) — Adapter 스스로
  영속화 계층을 소유하지 않는다(N-4, Memory Service Non-Goal과
  동일 원칙). 이는 새로 만드는 규칙이 아니라 `BASELINE.md` §15.2가
  Kernel Context Assembly에 이미 적용한 것과 같은 패턴이다 — §15.2는
  "이 흐름에는 영속화 지점이 없다... 'Kernel Context를 보관한다'는
  것은 호출자가 그 값을 들고 있는 것이지 Kernel이 저장하는 것이
  아니다"라고 명시한다. Workflow Adapter의 Checkpoint 값도 동일하게,
  Adapter가 값을 **생산**할 뿐 그 값의 영속화·복원은 호출자(및 실제
  Checkpointer 백엔드 선택)의 몫으로 남는다.

**불변조건(Invariants)**

- **무엇을 실행할지 결정하지 않는다** — Workflow의 도메인 내용
  (Node가 무엇을 하는가)은 HQ가 채운다(§7 System Boundary 준수).
- **Domain Lifecycle 전이 규칙을 재구현하지 않는다** — Agent/HQ의
  상태 전이가 이미 다른 곳에 정의돼 있다면 그것을 호출만 한다(v1
  대안 B 기각과 동일 원칙).
- **Policy 판정을 하지 않는다** — "이 Agent가 이 Capability를 써도
  되는가"는 Adapter가 개입하기 전에 이미 끝나 있어야 한다.
- **Registry/Discovery를 도입하지 않는다** — 여러 Workflow Adapter
  구현체가 동시에 존재하고 런타임에 선택되는 구조를 만들지 않는다
  (v1 결정 12, `IMPLEMENTATION_RULES.md` "Registry 일반화 금지"와
  합치).
- **Event Bus 로직을 흡수하지 않는다** — Event 발행은 할 수 있으나
  구독·라우팅은 소유하지 않는다(v1 결정 8).
- **Result Store 저장 게이트를 대체하지 않는다** — §16.5가 이미
  다루는 책임과 겹치는 저장 검증 로직을 새로 만들지 않는다.

**경계(Boundary)**

- 입력: HQ가 만든 Workflow 정의 + 이미 확정된 Task/Agent 실행 단위.
- 출력: 실행 결과(성공/실패/취소에 준하는 상태) — 예외를 던지지
  않고 값으로 표현한다(No Silent Failure, G-6과 동일 원칙).
- 이 Adapter가 개입하는 구간은 "HQ가 실행 단위를 이미 구성한
  이후 ~ 그 실행이 모두 끝나는 시점까지"로 한정된다. Kernel Stage
  (HQ Routing), Policy 판정, Capability/Connector 탐색은 이 구간
  **이전에** 끝나 있어야 한다.

**Reversibility 조건**

- 이 Adapter(어떤 구현체든, LangGraph 포함)를 제거하고 다른
  구현체(가장 단순하게는 순차 함수 호출)로 교체해도, Kernel과
  HQ가 정의하는 코드는 한 줄도 수정되지 않아야 한다 — v1
  `test_workflow_adapter_reversibility.py`가 이미 이 조건을 실제
  테스트로 증명한 선례가 있다(같은 검증 패턴을 v2에서도 요구할
  근거로 인용 가능).
- LangGraph 고유 문법(`StateGraph`/`Node`/`START`/`END`/
  Checkpointer API)은 이 Adapter 내부에서만 쓰여야 한다 — HQ나
  Kernel이 이 문법을 알게 되면 Reversibility가 깨진다.

## 8. Boundary Question

**§16.3~16.5가 이미 Accept한 범위를 넘어서는 Workflow 그래프
해석·실행 책임(조건부 분기·Loop·Checkpoint/Resume 포함)이,
LangGraph라는 구체적으로 검증된 Adapter Evidence(v1 `ADR-0007`
Accepted + 이번 세션 최신 버전 재확인)를 근거로, 지금 재검토
대상이 될 수 있는가?**

### 이 Boundary Question이 명시적으로 제외하는 것

- ADC-02의 넓은 질문("유지" 대 "대체") 자체를 다시 열지 않는다 —
  이 질문은 그 안의 좁은 부분집합 하나만 연다.
- LangGraph의 채택 여부를 확정하지 않는다 — "재검토 대상이 될 수
  있는가"까지만 묻는다. Accept되더라도 그것은 "이 질문을 정식으로
  열어도 될 만큼 Evidence가 구체적이다"라는 뜻이지 "LangGraph를
  쓴다"는 뜻이 아니다.
- §5가 남긴 공백(v1 Team/Division 의존 결정의 v2 재설계, 특히 결정
  2/5/9/11)을 채우지 않는다 — Accept되더라도 후속 ADC/ADR이 처음부터
  다뤄야 한다.
- 명칭(Workflow Adapter/Workflow Engine 등 무엇으로 부를지)을
  확정하지 않는다 — Execution Host가 별도 명명 ADC(`ADC-0014`)를
  거친 선례를 그대로 따른다.
- `hqs/investment/checkpoint.py`의 책임(§16.5)을 재판단하지 않는다.
- Model/LLM Provider 호출을 다루는 Engine Adapter(§16.2)의 내부
  구조를 변경하지 않는다(§3).
- 구현 착수를 승인하지 않는다 — `IMPLEMENTATION_RULES.md`의
  "Workflow Parser/Scheduler/Runtime orchestration/Event Bus 구현
  금지"는 이 RFC로 해제되지 않는다(§16.3이 Execution Host 범위에서만
  해제됐던 것과 동일한 원칙 — 이 RFC의 범위는 아직 Accept조차
  받지 않았다).

## Out of Scope

- Scheduler, Engine Gateway 등 대체 구조 설계.
- Workflow Registry/Discovery/Capability 선언 도입.
- Agent 전용 State Machine(Agent Lifecycle) 설계.
- 실제 Interface/Port 코드, 클래스, 함수 파일 작성 — §7은 개념적
  계약이며 구현이 아니다.
- Production 코드 변경(`hqs/`, `docs/architecture/`, `docs/decisions/`
  중 이 RFC 파일 자체를 제외한 어떤 파일도 포함).
- Investment HQ `checkpoint.py`의 수정 또는 대체 제안.
- Multi-HQ, 자연어 요청 분해(`ADC-0018`) 범위로의 확장.

## Non-goals

- 이 RFC는 LangGraph를 "정답"으로 전제하지 않는다 — Boundary
  Question이 Accept되더라도, 후속 ADC는 LangGraph 대신 다른 구현체
  (또는 v1처럼 순차 함수 호출 유지)를 선택할 자유가 있다. 이 RFC가
  제공하는 것은 "LangGraph로 이 영역이 실제로 채워질 수 있음을
  보여주는 Evidence"이지 "LangGraph여야 한다"는 결론이 아니다.
- 이 RFC는 Governance v2 Rule B(3건 이상 독립 관찰) 충족을 주장하지
  않는다 — §2.3에서 명시했듯 Evidence는 2건, 같은 계보다. 후속 ADC가
  `ADC-0016`과 동일한 논리(범위를 좁혀 Rule B 형식 미충족을 극복)를
  적용할지는 그 ADC의 판단이지 이 RFC가 대신 정하지 않는다.
- 이 RFC는 v2 Kernel Public Contract(§14)를 확장하지 않는다 — §14.1이
  "Task 전달 책임"을 여전히 계약 범위 밖으로 두고 있다는 사실을
  그대로 유지한다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §8 Boundary Question(§16.3~16.5 너머의 조건부 분기·Loop 실행
   책임 재검토 여부)을 지금 Evidence(v1 `ADR-0007` + 이번 세션 PoC)로
   Accept(Scoped)할 수 있는지, 아니면 Rule B 미충족·Evidence 2건뿐이라는
   이유로 Not Accepted로 남길지.
2. Accept된다면(Scoped) — §5가 정리한 재해석 공백(v1 결정 2/5/9/11,
   Team/Division 의존)을 후속 ADR이 어떤 순서로 다룰지, §7 Pseudo-Contract를
   실제 Public Contract 후보로 승격할지.
3. Accept된다면 — 명칭 확정(Execution Host의 `ADC-0014` 선례를
   따를지)과 구현 전략(LangGraph 그대로 채택할지, v1처럼 Adapter로만
   감쌀지)은 각각 별도 ADC로 분리해 판단하도록 제안한다(Execution
   Host가 존재 Accept(`ADC-0013`) → 명명(`ADC-0014`) → 구현 전략
   (`ADC-0015`) 3단계로 나눠 진행한 선례를 그대로 따른다).
4. Accept되지 않는다면 — `ADC-0008`이 남긴 재검토 조건 1번("Core
   Component 검토" 원문 확보)이 여전히 유일한 남은 경로임을
   재확인한다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. v1 `ADR-0007`(Accepted 상태
  그대로 인용), 이번 세션 PoC 기록(`.claude/docs/integrations/langgraph.md`,
  이미 커밋됨), `BASELINE.md`·`ADC.md`·기존 RFC/ADC 체인만 인용했다.
  새 실험은 수행하지 않았다.
- ADC-02를 대신 판정했는가 — **아니오**. §8은 질문 형태로만 남겼고,
  §Next Step이 판정을 후속 ADC로 명시적으로 위임했다.
- LangGraph 도입을 승인했는가 — **아니오**. Non-goals에서 "LangGraph가
  정답이라고 전제하지 않는다"고 명시했다.
- v1의 12개 결정을 그대로 복사했는가 — **아니오**. §5에서 Team/Division
  의존 여부에 따라 재해석 가능한 것(1,3,4,6,8,10,12)과 v2에
  대응물이 없어 재설계가 필요한 것(2,5,9,11)을 구분했다.
- 실행 가능한 코드나 Interface를 작성했는가 — **아니오**. §7은
  책임·불변조건·경계·Reversibility 조건만 서술했고, 함수 시그니처나
  클래스를 포함하지 않는다.
- §16.3~16.5의 기존 Accept를 침범했는가 — **아니오**(§6). Execution
  Host·Multi-Task·Result Store 어느 것도 범위를 넓히거나 좁히지
  않았다.
- Engine Adapter(§16.2, Model/LLM)와 혼동했는가 — **아니오**(§3).
  용어 충돌을 표로 명시적으로 분리했다.
- `hqs/investment/checkpoint.py`를 대체하자고 제안했는가 —
  **아니오**(§6, Out of Scope). "건드리지 않는다"고 명시했다.
- 명칭을 확정했는가 — **아니오**. §8 제외 목록과 §Next Step에서
  Execution Host의 3단계 선례(존재→명명→구현 전략)를 따르도록
  후속 절차로 넘겼다.
- Production 코드, Baseline, ADC, ADR, CLAUDE.md를 수정했는가 —
  **아니오**. 이 RFC 파일 하나만 신규 작성했다.
- Governance v2 Rule B 충족을 주장했는가 — **아니오**(§2.3,
  Non-goals). Evidence 2건뿐임을 명시하고 판단은 후속 ADC로
  위임했다.
