# RFC-0026: Multi-Agent Workflow — Contract Candidate 조사 및 Boundary (Phase C)

**Status**: Proposed (조사·판단 결과 기록, Baseline 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §6(Concept Model:
Workflow/Task/Runtime)·§16.3~16.7(Execution Host/Multi-Task/Multi-Task
Result Store/**Workflow Adapter**/Workflow Module Defer),
`hqs/development/IMPLEMENTATION_RULES.md`(Workflow Parser/Scheduler/
Dynamic Routing 금지 표), `docs/architecture/core/RFC-0019~0021`·
`ADC-0019~0025`·`ADR-0008,0009,0011~0014`(Workflow Adapter Governance
Chain), `docs/architecture/core/RFC-0024/ADC-0032`·`RFC-0025/ADC-0033`
(Phase A/B — Agent Domain/Lifecycle/State/Message/Event **Defer/Open**).

**Evidence**: 위 문서 전체, `hqs/development/workflow.py`(Stage 01→05
실제 구현), `hqs/investment/teams/stock_team.py`(`ThreadPoolExecutor`),
`projects/workflow-adapter-*/`(Experimental Implementation 4건),
`docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐, Open). **새로운 실험·
프로토타입·측정은 수행하지 않는다.**

> 이 RFC는 Phase A(`RFC-0024`/`ADC-0032`)와 Phase B(`RFC-0025`/`ADC-0033`)의
> 결과를 **전제**로 삼는다 — Agent Domain·Lifecycle·State·Message/Event
> 어느 것도 Accept되지 않았다(전부 Not Accept/Defer 또는 Open). 이 RFC는
> 그 Defer/Open을 우회해 "Multi-Agent Workflow"라는 이름으로 새 확정
> Contract를 만들지 않는다.

---

## 0. 이 RFC가 열린 이유

사용자가 지정한 Phase C는 Workflow의 최소 구성 개념(Node/Step, Transition/
Edge, Condition, Sequence, Parallelism, Loop, Failure/Termination)이
Multi-Agent 맥락에서 실제로 필요한지 조사·판단하라는 것이다. 조사 결과,
이 저장소는 이미 `BASELINE.md` §16.6 **Workflow Adapter**라는 이름으로
정확히 이 구성 개념들(State/Node/Conditional Edge/Loop/Checkpoint-Resume)을
**Accept(Scoped, Conditional)**해 둔 상태다 — RFC-0019 → ADC-0019 →
ADR-0008/0009 → ADC-0020~0025 → ADR-0011~0014로 이어지는, 이 저장소에서
가장 길고 촘촘한 Governance Chain 중 하나다. 따라서 이 RFC의 실질적
임무는 "새 개념을 정의하는 것"이 아니라 **"이미 있는 것과 아직 없는 것을
정확히 가르는 것"**이다 — 이미 Decided된 것을 다시 여는 것은 중복
Governance이며, 아직 없는 것(Multi-Agent 차원)을 이 김에 확정하는 것은
Phase A/B의 Defer를 우회하는 것이다.

## 1. Problem Statement

"Multi-Agent Workflow"라는 한 단어가 실제로는 두 개의 다른 층위를
가리킬 수 있다.

- **(층위 1) Task 그래프 실행** — 이미 정해진 Node들(각 Node는 이미
  어느 Agent가 수행할지 HQ가 정한 상태)을 조건부 분기·반복·병렬로
  진행시키는 것. 이는 §16.6이 이미 다루는 영역이다.
- **(층위 2) Agent 간 동적 상호작용** — 어느 Agent가 이 단계를 수행할지
  실행 중에 결정되거나(동적 배분), Agent끼리 직접 통신하거나
  (Message/Event), Agent의 생애 상태가 Workflow 진행에 따라 전이되는
  것. 이는 Scheduler·Dynamic Routing·Registry(전부 구현 금지)와 Agent
  Domain/Lifecycle/State/Message/Event(Phase A/B, 전부 Defer/Open)의
  영역이다.

이 두 층위를 구분하지 않으면 "Workflow Candidate가 필요한가"라는
질문에 뭉뚱그려 답하게 되고, 이미 Accept된 §16.6을 다시 여는 오류나
Defer된 Phase A/B를 우회하는 오류 중 하나에 빠지기 쉽다. 이 RFC는 그
구분을 §2~§4에서 명시적으로 수행한다.

## 2. Evidence Summary — 층위 1: 이미 결정된 것

### 2.1 §16.6 Workflow Adapter — Accept(Scoped, Conditional)

| Candidate(사용자 지정 항목) | §16.6 대응 | 상태 |
|---|---|---|
| Node/Step | A-IN(b) "단일 실행 단계(Node)의 진행" | **Accept(Scoped, Conditional)** |
| Transition/Edge(무조건) | A-IN 암묵 — Node 간 순차 진행 | **Accept(Scoped, Conditional)**(Node 진행의 일부) |
| Condition | A-IN(c) "조건부 분기(Conditional Edge)" | **Accept(Scoped, Conditional)** |
| Sequence | Development HQ `workflow.py`(Stage 01→05 직접 함수 호출) — Kernel 결정 불필요, 이미 무제한 허용 | **이미 자유롭게 허용**(Scheduler 아님) |
| Parallelism | §16.4 Multi-Task(`ADC-0016`, Scoped·Conditional) + §16.6 Reversibility 테스트의 "5-way 병렬 fan-out" 시나리오 | **Accept(Scoped, Conditional)**(두 트랙 모두) |
| Loop | A-IN(d) "조건 만족까지의 반복(Loop)" | **Accept(Scoped, Conditional)** |
| Failure/Termination | A-IN(a)(ii) 종료 disposition, §14.3 G-6(예외 아닌 값으로 표현) | **Accept(Scoped, Conditional)**(형식만; 내용·어휘는 HQ 도메인) |

**결론**: 사용자가 나열한 7개 Candidate 전부가 이미 §16.6에서 **Kernel
Module 후보로 Accept(Scoped, Conditional)**되어 있다. 이 RFC가 이들을
새로 "정의"하면 §16.6의 기존 Governance Chain(RFC-0019~0021, ADC-0019~0025,
ADR-0008/0009/0011~0014)을 중복·재판정하는 것이 되어 Governance 절차
위반이다. 이 RFC는 **이들을 재정의하지 않는다.**

### 2.2 §16.6이 Production 개시를 아직 막고 있는 이유(중복 확인)

Accept(Scoped, Conditional)의 "Conditional"은 여전히 유효하다 —
`ADC-0019` 재검토 조건 (c)의 견고성 요건(비결정적 실제 엔진 관찰, v2
프로덕션 맥락 관찰)이 미충족이고(`ADC-0024`·`ADC-0025`의 "부분/2차 부분
완화"), Reversibility v2 검증도 "부분 충족(E4)"에 그친다(잔여 한계
(i)~(iii)). `IMPLEMENTATION_RULES.md`의 Workflow Parser/Scheduler 금지도
전혀 해제되지 않았다. **Production 구현은 여전히 차단**되어 있으며 이
RFC는 이 차단을 해제하지 않는다.

### 2.3 §16.6의 A-OUT — 층위 2로 넘어가지 않는 명시적 경계

§16.6 A-OUT은 "HQ Routing/Registry, Policy 판정, Capability/Connector
Discovery, **Domain Lifecycle 전이 규칙**, **Event Bus 구독·라우팅**,
Multi-HQ 분해"를 명시적으로 제외한다. 즉 §16.6이 다루는 "Agent"는 **이미
고정된 실행 단위의 불투명한 일부**일 뿐, Workflow 진행 중 동적으로
바뀌거나 서로 통신하는 주체가 아니다. §16.6의 Node가 "어느 Agent가
수행하는가"는 HQ가 실행 단위를 구성하는 시점에 이미 정해지며, Workflow
Adapter는 이를 관측·해석하지 않는다(§16.6 "실행 단위" 문단, `ADC-0022`
§D-0). **이것이 층위 1과 층위 2를 가르는 원문상의 정확한 경계선이다.**

## 3. Evidence Summary — 층위 2: 실제 Multi-Agent Workflow 소비자 존재 여부

### 3.1 코드 조사

| 대상 | 확인 결과 |
|---|---|
| `hqs/development/workflow.py` | Stage 01→05를 `try/except`로 직접 순차 호출하는 **고정 선형 단일 패스**. 그래프·조건부 분기·Loop 없음. `IMPLEMENTATION_RULES.md` "Stage 재진입 금지"로 명시적으로 금지됨. |
| `hqs/investment/teams/stock_team.py` | `ThreadPoolExecutor` 블록(line 164, 190) — 짧은 수명 병렬 실행. `Multi-Task`(§16.4, `ADC-0016` Scoped) 범위. Agent 간 통신·동적 배분 없음. |
| `projects/workflow-adapter-*/` (4개 디렉터리) | §16.6의 **Experimental Implementation**(`ARCHITECTURE_GOVERNANCE.md`의 격리 영역) — `graph_spec`/`StateGraph`/`langgraph` 사용은 이 안에만 존재하며 `hqs/`·`core/`·`dashboard/` Production 경로에 연결되지 않았다(격리 원칙 준수, `ADC-0021`~`ADC-0026` 확인). |
| Production 경로(`hqs/`, `core/`, `dashboard/`) | `graph_spec`/`StateGraph`/`langgraph` 참조 **0건**(grep 확인). |

### 3.2 결론 — 실제 소비자 없음

**Multi-Agent Workflow(층위 1이든 층위 2든)의 실제 Production 소비자는
현재 존재하지 않는다.** 층위 1(§16.6)은 Experimental 단계에서 4건의
Evidence로 검증 중이나 Production 착수가 명시적으로 차단되어 있고,
층위 2(Agent 간 동적 상호작용)는 이를 가능케 할 전제 조건
(Scheduler/Registry/Event Bus 해제, Agent Domain/Lifecycle/State/Message/
Event Accept)이 전부 금지 또는 Defer/Open 상태라 **소비자가 존재할 수
있는 조건 자체가 아직 없다.**

## 4. Gap Analysis

| 항목 | 현재 상태 | 이 RFC가 새로 열 것이 있는가 |
|---|---|---|
| Node/Edge/Condition/Sequence/Parallelism/Loop/Failure(층위 1) | §16.6 Accept(Scoped, Conditional), Governance Chain 완결 | **없음** — 재정의는 중복 Governance |
| §16.6의 Production 개시 조건 | `ADC-0019` 재검토 조건 (c), Reversibility 완전 검증 미충족 | **없음** — 이 RFC의 판단 대상 아님(§16.6 트랙 소관) |
| Agent가 Workflow Node에 동적으로 배분되는가(층위 2) | Scheduler/Dynamic Routing 구현 금지(`IMPLEMENTATION_RULES.md`), Runtime 존폐 Open(ADC-02) | **없음** — Phase A/B Defer를 우회하지 않고는 열 수 없음 |
| Conditional Edge의 조건이 Agent State/Message를 참조할 수 있는가 | §16.6 A-IN(a)는 "공유 실행 상태(State)"만 언급 — 이것이 Phase B의 "Agent State"(§4, Defer)와 같은 것인지 미답 | **Boundary Question으로만 개설**(§5) — 결정하지 않음 |
| Workflow Node 간 Agent↔Agent 통신이 §16.6 그래프의 일부인가 | §16.6 A-OUT은 Event Bus 구독·라우팅을 제외 — Node 진행 자체와 Node 간 "통신"의 관계 미답 | **Boundary Question으로만 개설**(§5) — 결정하지 않음 |
| §16.7 Workflow Kernel Module(전체 Module 존재 여부, `ADC-0001` Module 2) | Defer, 무변경 | **없음** — 이 RFC와 별개 축(§16.6 본문이 이미 재확인한 구분) |

## 5. Candidate — 유일하게 남는 것: 층위 1과 Phase A/B의 접점 Boundary Question

> 이 절은 새 Contract를 제안하지 않는다. §16.6과 Phase A/B가 미래에
> 만날 수 있는 **접점 두 곳**만 명시적으로 기록하고, 지금 답하지
> 않는다.

| 접점 | 질문 | 이 RFC의 입장 |
|---|---|---|
| §16.6 A-IN(a) State ↔ RFC-0025 §4 Agent State | §16.6의 "공유 실행 상태"는 Workflow 그래프 진행 정보(HQ 도메인 State)다. RFC-0025 §4의 "Agent State"는 Agent 인스턴스 단위의 불투명 값이다. 둘은 이름은 다르나 "Workflow가 실행 중 Agent의 상태를 읽어야 하는 순간"이 오면 접점이 생길 수 있다 | **접점 존재만 기록. 통합·구분 여부는 결정하지 않는다** — 둘 다 아직 각자 Defer 상태(§16.6은 Production 미개시, RFC-0025 §4는 Not Accept)이므로 지금 관계를 정할 근거가 없다 |
| §16.6 Node 진행 ↔ RFC-0025 §6 Message/Event | Workflow Node가 여러 Agent에 걸쳐 있다면 Node 간 이동이 §6의 (a)/(b)/(c) 중 어느 Flow에 해당하는지 물을 수 있다 | **§6의 미선택 상태를 그대로 유지한다** — §16.6의 A-OUT("Event Bus 구독·라우팅 제외")과 정합적으로, 이 RFC도 Node 간 이동을 Event/Message로 분류하지 않는다 |

**이 Candidate가 하지 않는 것**: 두 접점 중 어느 쪽도 Kernel Concept
Model·§14 Public Contract·§16.6 A-IN/A-OUT을 확장하지 않는다. 접점이
"있다"는 관찰만 기록해, 향후 Phase A/B의 재검토 Trigger가 충족되거나
§16.6의 Production 개시 조건이 충족될 때 이 RFC를 참조점으로 삼을 수
있게 한다.

## 6. LangGraph의 취급 — 설계 기준이 아닌 매핑 대상

`ADC-0019`~`ADC-0026`의 축적된 판단(Gate (B) 부분/2차 부분 완화, Gate
(C) 부분 충족)을 그대로 따른다 — LangGraph는 §16.6 A-IN 다섯 항목을
구현할 수 있는 **후보 구현체 중 하나**(Reversibility 불변조건 하에
교체 가능)로만 남아 있으며, 이 RFC는 그 지위를 바꾸지 않는다. 이 RFC의
어떤 절도 LangGraph의 API·그래프 모델을 §16.6 A-IN 개념 정의의 기준으로
쓰지 않았다 — §2.1 표는 §16.6 원문 문구만 인용했다.

## 7. Out of Scope

- §16.6 A-IN 다섯 항목(State/Node/Conditional Edge/Loop/Checkpoint-Resume)의
  **재정의·재판정** — 이미 Accept(Scoped, Conditional), 별도 Governance
  Chain(RFC-0019~0021/ADC-0019~0026/ADR-0008 등) 소관.
- §16.6 Production 개시 조건(Gate (B)/(C))의 해소 — 그 트랙 소관.
- Scheduler, Registry, Event Bus, Agent Manager, Runtime Engine의 설계·구현.
- LangGraph 평가·채택·구현.
- Agent Domain/Lifecycle(Phase A)·Agent State/Message/Event(Phase B)의
  재정의 — 여전히 Defer/Open, 이 RFC는 이를 그대로 인용만 한다.
- §16.7 Workflow Kernel Module(전체) Defer 상태의 재판단.
- `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md` 문언
  수정. Production Code 변경.

## 8. Non-goals

- 이 RFC는 "Multi-Agent Workflow Contract가 필요하다"고 주장하지
  않는다 — 조사 결과 오히려 그 이름이 가리키는 대부분(층위 1)이 이미
  Contract화되어 있고, 나머지(층위 2)는 아직 그것을 요구할 실제 사례가
  없다.
- 이 RFC는 §16.6의 기존 Accept를 강화·약화하지 않는다.
- 이 RFC는 §5의 두 접점을 "곧 결정해야 한다"고 주장하지 않는다 — 접점의
  기록 자체가 이 RFC의 전부다.

## 9. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase C)** | 층위 1(§16.6)이 이미 Decided임을 확인 + 층위 2(Multi-Agent 동적 상호작용)에 실제 소비자가 없음을 확인 + 두 층위의 접점을 Boundary Question으로만 기록(§5). **새 Candidate를 Accept 대상으로 제안하지 않는다.** |
| **후속 Governance Review(신설 예정, 필요 시)** | 사용자가 별도로 요청하는 경우, 이 RFC의 §5 접점 관찰이 ADC 채택 기준을 충족하는지(현재 판단으로는 미충족) 재확인하는 문서. 다만 이 RFC 자체가 이미 "결정 없음"을 결론으로 명시했으므로, 새로 Accept/Reject할 대상이 없다면 별도 ADC가 필수는 아니다. |
| **§16.6 자체 트랙** | Production 개시 조건(Gate (B)/(C)) 해소는 이 RFC와 무관하게 그 트랙에서 계속 진행. |
| **Phase A/B 트랙** | 재검토 Trigger(`ADC-0032` §Conditions, `ADC-0033` §Conditions) 충족 여부는 이 RFC와 무관하게 그대로 유지. |

## 10. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건 추가만 존재. `BASELINE.md`·
  `GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  Production Code(`core/`, `hqs/`, `dashboard/`) **무변경**.
- §2.1 표의 각 인용이 `BASELINE.md` §16.6 원문(A-IN 다섯 항목, "책임"
  문단)과 문자 그대로 일치하는지 재대조 — 일치 확인.
- §2.3 A-OUT 인용이 §16.6 원문("HQ Routing/Registry, Policy 판정...
  Domain Lifecycle 전이 규칙, Event Bus 구독·라우팅...")과 일치하는지
  재대조 — 일치 확인.
- `grep -n "graph_spec\|StateGraph\|langgraph" -r hqs/ core/ dashboard/` —
  0건 확인(§3.1 "Production 경로 참조 0건"의 근거).
- `hqs/development/workflow.py` 원문 확인 — `try/except` 직접 순차 호출
  구조, 그래프·조건부 분기·Loop 없음(§3.1 인용과 일치).
- `hqs/investment/teams/stock_team.py:164,190` `ThreadPoolExecutor`
  재확인(`ADC-0032` §Q3에서 이미 확인한 것과 동일 위치).
- §5가 Phase A/B의 Defer/Open 상태를 재확정하거나 우회하지 않았는지
  확인 — "접점 존재만 기록, 관계는 결정하지 않는다"는 문장이 §5 두
  행 모두에 명시됨.
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다. `pytest`
  모듈은 이번 세션 환경에 없으며(Phase A/B에서 이미 확인), 코드 diff
  0줄이므로 재실행 결과가 달라질 여지가 없다.

## 11. Self Review

- §16.6의 기존 Accept(Scoped, Conditional)를 재정의·재판정했는가 —
  **아니오**(§2.1, §7) — 원문을 인용해 "이미 Decided"임을 확인했을
  뿐이다.
- §16.6의 Production 차단을 해제하는 근거로 이 RFC를 썼는가 —
  **아니오**(§2.2, §7) — 차단 사유(Gate (B)/(C) 미충족)를 그대로
  인용했다.
- Agent Domain/Lifecycle/State/Message/Event를 재정의하거나 Phase A/B의
  Defer/Open을 우회했는가 — **아니오**(§5, §8) — 두 접점 모두 "관계를
  결정하지 않는다"고 명시했다.
- Scheduler/Registry/Event Bus/Agent Manager/Runtime Engine/LangGraph를
  구현·설계했는가 — **아니오**(§6, §7) — LangGraph는 기존 지위(후보
  구현체)를 재확인만 했다.
- 실제 소비자 존재 여부를 코드로 검증했는가 — **예**(§3.1) — grep과
  파일 원문 확인.
- 새 Kernel Concept·Public Contract 항목을 추가했는가 — **아니오**
  (§7, §10 `git status` 0 diff).
- Production Code를 변경했는가 — **아니오**(§10).
- 새로운 실험·프로토타입·측정을 수행했는가 — **아니오** — 기존 문서·
  코드 관찰만 인용했다.
