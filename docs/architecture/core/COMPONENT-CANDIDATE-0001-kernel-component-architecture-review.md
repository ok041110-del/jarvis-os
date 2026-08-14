# COMPONENT-CANDIDATE-0001: Kernel Component Architecture Candidate Review (Phase 7)

**문서 성격**: Evidence/Candidate 문서. **RFC/ADC/ADR이 아니다.**
`docs/02_rfc/RFC_CANDIDATES.md`와 동일한 지위 — "논의됐고 후보로
기록되지만, 아직 정식 절차로 승격되지 않은 것"만 담는다. 이 문서는:

- `docs/03_adc/ADC.md`의 어떤 항목도 상태를 바꾸지 않는다.
- 새 RFC/ADC/ADR을 생성하지 않는다.
- `docs/01_architecture/BASELINE.md`를 수정하지 않는다 — §10은
  여전히 "Kernel Component Architecture"를 Out of Scope로 둔다
  (ADR-0005). 이 문서는 그 경계 **안에서** "만약 설계한다면 무엇이
  후보인가"만 Evidence로 정리한다 — 설계를 확정하지 않는다.
- 코드를 작성하지 않는다.

**선행 문서**: `VALIDATION-0002-kernel-component-boundary-evidence-check.md`
(Phase 6 — 실제 코드/테스트/Evidence가 현재 Baseline 경계를 지키는지
검증)의 결과를 입력으로 삼는다. Phase 6은 "경계가 어디인가"를
확인했고, 이 문서는 "그 경계를 Kernel Component로 표현한다면 어떤
모습이 될 것인가"를 **후보 수준에서만** 정리한다.

**입력 자료**: `BASELINE.md` §6·§7·§10~§16, `VALIDATION-0002`,
`development-hq/BOUNDARY.md`, `core/execution_layer/**`,
`docs/architecture/core/ADC-0009~0011`, `docs/03_adc/ADC.md`
(ADC-01·02·03·09·10·11), `docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`,
`docs/research/INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md`.

---

## 0. 이 문서가 답하는 질문과 답하지 않는 질문

**답하는 것**: 8개 Component 후보 각각에 대해, 현재 Evidence가
"독립 Component로 설계할 근거"를 제공하는지, 아니면 "아직 Responsibility
수준에 머물러야 하는지"를 판정한다.

**답하지 않는 것**:
- Component의 API·클래스 구조·자료형 (§10 Implementation, Out of Scope)
- ADC-01(Model↔Component 대응)의 재조사 — Not Accepted 상태를
  그대로 인용만 한다.
- ADC-02(Runtime 존폐)의 재조사 — 동일.
- ADC-03(Connector 위치)의 재조사 — 동일.
- 어떤 RFC를 지금 열어야 하는가 — §5에서 ADC 채택 기준(두 조건)에
  대조만 하고, 조건 미충족이면 열지 않는다.

---

## 1. Component 후보별 분석

각 후보는 8개 항목(책임/비책임/입력·출력/의존/외부 경계/구현 여부/
Evidence/미확정)으로 정리한다.

### C-1. Kernel Context

| 항목 | 내용 |
|---|---|
| 책임 | Segment 수집·병합·검증·정렬·조립(Assemble)·렌더(Render) — `BASELINE.md` §13.2·§15.1의 6단계 그대로 |
| 비책임 | Source 발견, Content 해석, 영속화, Engine 선택 |
| 입력/출력 | 입력: Segment 집합 + Ordering Policy(HQ가 제공). 출력: Kernel Context(불변 값) → Render 후 표현(Output) |
| 의존 Component | 없음 — 가장 하위의 순수 책임. Renderer(X-1)와 Ordering Policy(X-2)를 **주입받을 뿐** 의존하지 않는다 |
| 외부 경계 | HQ가 Source·Content·Policy를 선언(경계 밖), Kernel이 조립까지 수행(경계 안), Render는 "경계 위"(계약은 안, 구현은 Hidden) — §15.1 표 그대로 |
| 현재 구현 여부 | **미구현.** §13~§15는 책임·계약·배선도를 문서로만 정의했다. 코드(클래스/모듈)는 존재하지 않는다 |
| Evidence | `BASELINE.md` §13(Model)·§14(Contract, PR-1~4/G-1~7)·§15(배선도), ADR-0003~0005 |
| 미확정 | Context Identifier 파생 규칙(H-5, Defer), Context Boundary 확정 형태(Defer), Engine별 Renderer(Defer), R-3(Defer) — §13.6·§14.7이 이미 6건을 Defer로 기록, 이 문서가 새로 추가하지 않는다 |

**판정**: 이미 **Responsibility 수준까지는 확정**되어 있다(§13~15,
ADR-0003~0005로 Governance 절차를 거침). 그러나 이것을 실제
Component(클래스/모듈)로 만드는 것은 §10이 여전히 막고 있다 —
**"설계된 책임, 미구현 Component"**로 남겨야 한다. 이 문서가 새로
할 일은 없다(이미 완료된 상태를 재확인).

### C-2. Task / Workflow

| 항목 | 내용 |
|---|---|
| 책임 | Task 실행 순서(그래프)를 정의하고, 그 순서대로 Task를 실제로 흐르게 한다(§6 Concept Model: "Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다") |
| 비책임 | Task의 도메인 내용(§7: "Workflow의 도메인 내용은 Jarvis OS 책임 아님"), Agent 선택 기준의 세부 로직 |
| 입력/출력 | 입력: Workflow 정의(HQ가 작성) + Task 인스턴스. 출력: Agent에게 배분된 실행 요청, 완료 시 Artifact |
| 의존 Component | Engine 호출 결과(Execution), Agent-Capability 매핑(Registry 후보 영역) |
| 외부 경계 | Workflow **내용**은 HQ 책임(§7), Workflow **실행 메커니즘**(Scheduler)은 Kernel 후보(§11 표: "Task 전달 책임 → Scheduler") |
| 현재 구현 여부 | **미구현.** `development-hq/mvp/workflow*.py`는 Task 순서를 함수 호출로 **하드코딩**한다 — Parser/Scheduler를 명시적으로 만들지 않는다(`IMPLEMENTATION_RULES.md` 금지 항목) |
| Evidence | `VALIDATION-0002` §1(Workflow/Task 판정 "없음 — Stop Trigger 미발동"), `workflow.py`(`run_mvp_0001()` 순차 호출), `HANDOVER.md`: "지금까지 발동 사례 없음" |
| 미확정 | ADC-01(Model↔Component 대응, Open) — Task 전달 책임이 Kernel에 속하는지는 §14.1 표에서 "미결 — 계약 범위 밖"으로 명시. ADC-09(Workflow 그래프의 의미론적 경계, Open·NOW)도 미해소 |

**판정**: **독립 Component로 설계할 Evidence가 아직 없다.** Task
전달 책임의 Kernel 소속 자체가 미결(§14.1)이고, ADC-09(NOW
우선순위)가 "OS가 이해해야 하는 Workflow 스키마가 순수 범용
그래프인지, 도메인 특화 노드 타입을 포함하는지"를 여전히 열어
두고 있다. Stop Trigger가 한 번도 발동하지 않았다는 사실은 "지금
설계가 필요하다"는 압력이 아니라 "지금 설계 없이도 MVP가
동작한다"는 반대 방향의 Evidence다.

### C-3. Agent / Capability Boundary

| 항목 | 내용 |
|---|---|
| 책임 | Agent: 배분된 Task의 실제 수행, Task 실행 중 Context 생성(§7). Capability: HQ가 내용을 정직하게 등록(§7) |
| 비책임 | Agent: Task 배분 메커니즘 자체(§7: HQ가 절대 책임지지 않는 것 — "Task 실행 메커니즘은 Kernel Scheduler 책임"). Capability: 색인·탐색(Registry 책임) |
| 입력/출력 | Agent 입력: 배분된 Task + Context. 출력: Artifact(또는 Fault). Capability는 값(선언 텍스트)이며 실행되지 않는다 |
| 의존 Component | Implementation Engine(`call_engine`)을 통해 실제 연산 수행 |
| 외부 경계 | Agent/Capability 자체는 **HQ 책임**(§7) — Kernel Component가 아니다. Kernel이 관여하는 것은 "탐색"(Registry)뿐 |
| 현재 구현 여부 | **HQ 수준에서 이미 구현됨** — `AGENT_CAPABILITY_MAP`(리터럴 딕셔너리), `agents.py`의 각 Capability 함수 |
| Evidence | `VALIDATION-0002` §Q3("중복·결합 없음 — 물리적으로 분리"), `agents.py`, MVP-0001부터 미확장 |
| 미확정 | RFC_CANDIDATES.md Candidate 1(Capability→Contract 재분류)·2(Agent→"Logical Worker")·5(Capability 다대다) — 전부 Pending, MVP-0001 이후에도 아직 RFC로 승격되지 않음 |

**판정**: Agent/Capability는 **Kernel Component 후보가 아니다** —
이미 §7이 HQ 책임으로 확정했다. 이 문서가 검토할 것은 "Kernel이
Agent/Capability를 어떻게 탐색하는가"(Registry, C-5)뿐이며, Agent/
Capability 자체를 Kernel Component로 승격하는 방향의 Evidence는
없다(오히려 §7이 명시적으로 반대 방향을 확정했다).

### C-4. Execution

| 항목 | 내용 |
|---|---|
| 책임 | Implementation Specification → Execution Result 6단계 결정론적 변환(Collect~Render에 준하는 Execution Request→Prompt Spec→Model Request→Handle→State→Result), Model/Engine 호출까지의 경계(§16.2) |
| 비책임 | 코드의 의미 해석, Task 배분, HQ 도메인 로직, Multi-Model Routing(ADC-01 Open으로 미결) |
| 입력/출력 | 입력: Implementation Specification(`str`, 8개 항목) + caller-supplied 메타데이터(id/시각/state/results). 출력: Execution Result(`str`) |
| 의존 Component | Implementation Engine(`call_engine`, Kernel 경계 밖) — Execution Layer 자신은 이를 직접 호출하지 않는다(`pipeline.py`는 6개 Builder만 호출) |
| 외부 경계 | Development HQ의 Implementation Specification을 입력으로 받는 지점부터가 Execution Layer(§16.2) — 그 이전(Specification 생성)은 Development HQ 책임 |
| 현재 구현 여부 | **이미 구현·Accept됨.** `core/execution_layer/mvp_0001~0006/` + `pipeline.py`, Kernel Module로 Accept(§16.2, ADR-0002 core-to-kernel) |
| Evidence | `VALIDATION-0002` §Q1(Deterministic/Immutable/Lossless 코드+테스트로 확인, 58건 통과) |
| 미확정 | Kernel Context Model과의 연결(R-3, ADR-0005 미해결 4번) — 아래 §2-A에서 별도로 다룬다 |

**판정**: **이미 Component 수준으로 실재하는 유일한 후보.** 다만
Kernel Context Model(§13~15)과는 아직 별개 체계다 — 이 비연결
자체는 §2-A에서 집중 검토한다.

### C-5. Registry / Lifecycle

| 항목 | 내용 |
|---|---|
| 책임 | HQ/Agent의 등록과 발견, HQ의 생명주기 관리 및 상태 전환 통제(§7, Jarvis OS 책임으로 Frozen) |
| 비책임 | Capability 내용의 진실성 검증(ADC-11, Open — "자기 신고인지 OS가 검증하는지 미정") |
| 입력/출력 | 입력: HQ가 등록하는 Capability 선언. 출력: 다른 HQ/Agent가 조회 가능한 색인, HQ Lifecycle State |
| 의존 Component | 없음(현재는 대상이 없다 — 미구현) |
| 외부 경계 | 등록 **내용**은 HQ 책임, 등록 **메커니즘**은 Kernel 책임(§7) |
| 현재 구현 여부 | **완전 미구현.** Development HQ·Investment HQ 둘 다 "비-live"(Registry에 등록된 적 없음) |
| Evidence | `INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md` §2-3(두 HQ가 동일하게 비-live 상태임을 직접 확인), `VALIDATION-0002` §Q4 |
| 미확정 | ADC-06(Lifecycle 전환 권한 경로, Open·NEXT), ADC-11(Capability 신뢰 검증, Open·LATER) |

**판정**: **책임 귀속은 확정(Kernel), 설계 착수 근거는 없다.**
§10 Component Design이 Registry를 명시적으로 나열하며 Out of
Scope로 둔다. 두 HQ가 실제로 동작 중인데도 Registry 부재로 인한
문제가 한 번도 관찰되지 않았다는 사실(`VALIDATION-0002`)은 "지금
당장 필요"라는 압력의 부재를 뒷받침한다.

### C-6. Memory

| 항목 | 내용 |
|---|---|
| 책임 | Context를 HQ 네임스페이스 안에 영속화(§6) |
| 비책임 | Context의 조립(Kernel Context/C-1 책임), 도메인 내용 판단 |
| 입력/출력 | 입력: Kernel Context(값). 출력: 복원된 Context |
| 의존 Component | Kernel Context(C-1) — Memory는 C-1이 만든 값을 영속화할 뿐, 스스로 값을 만들지 않는다(N-4) |
| 외부 경계 | §13.6 각주: "영속화(Memory)는 이 절의 범위가 아니다" — Kernel Context Model과 Memory는 처음부터 분리 설계됐다 |
| 현재 구현 여부 | **완전 미구현.** `IMPLEMENTATION_RULES.md`: "Memory Service(영속화 계층) 구현 금지". `run_mvp_0001()`의 `review` 지역 변수(in-memory)가 유일한 "Context 전달" 사례 |
| Evidence | `VALIDATION-0002` §1("Memory 미구현이 곧 준수"), `BASELINE.md` §14.6 N-4(Non-Goal, "Memory Module이 필요한가"는 Defer) |
| 미확정 | Memory Module 필요 여부 자체가 Defer(§14.6 N-4) — 재검토 조건 없음(트리거 미정) |

**판정**: **독립 Component로 설계할 Evidence가 가장 약한 후보 중
하나다.** in-memory 변수 하나로 지금까지 모든 MVP·Dogfooding이
문제없이 동작했다 — 영속화가 필요해진 사례가 한 번도 관찰되지
않았다.

### C-7. Event / State

| 항목 | 내용 |
|---|---|
| 책임 | Fault의 Event 전파(§6: "Task는 실패 시 Fault를 발생시키고, Fault는 Event로 전파된다"), HQ 경계를 가로지르는 Event Flow |
| 비책임 | Task Flow(순차 실행)와 혼동되지 않는 것 — §6이 Task Flow(수직)와 Event Flow(경계 횡단)를 이미 구분 |
| 입력/출력 | 입력: Fault(Task 실패). 출력: 전파된 Event |
| 의존 Component | Task/Workflow(C-2) — Fault는 Task 실행 중 발생 |
| 외부 경계 | 미정 — ADC-05(Fault 배달 보장 수준)·ADC-08(Task/Event Flow 배달 차등화) 둘 다 Open |
| 현재 구현 여부 | **완전 미구현.** `IMPLEMENTATION_RULES.md`: "Event Bus 구현 금지 — MVP는 단일 선형 Task Flow만 다루며 Event Flow를 쓰지 않는다" |
| Evidence | `workflow.py`의 `try/except`(MVP-0036, Fault를 dict 값으로 반환할 뿐 전파하지 않음) — Event Bus 없이도 단일 HQ 내에서는 예외 처리로 충분했음을 실증 |
| 미확정 | ADC-04(Observability/Audit 소속), ADC-05, ADC-08 전부 Open — Event/State는 8개 후보 중 **미결 ADC가 가장 많이 걸린 영역** |

**판정**: **가장 이른 단계.** Multi-HQ 시나리오가 아직 한 번도
실행된 적이 없어(모든 Dogfooding이 단일 HQ 내부), HQ 경계를
가로지르는 Event Flow 자체가 실증된 적이 없다. 지금 설계하면
Evidence 없이 만드는 것이 된다.

### C-8. External Data / Acquisition Boundary

| 항목 | 내용 |
|---|---|
| 책임 | (후보 단계) 외부 자산 데이터를 project-local Artifact(`raw_data.md`)로 수집·정리 |
| 비책임 | Engine 호출(Execution), Capability 판단, Kernel Context 조립 |
| 입력/출력 | 입력: 외부 데이터(현재는 project 작성자가 수동/도구로 조사). 출력: `raw_data.md`(project-local, `## [TAG]` 섹션 구조) |
| 의존 Component | 없음 — 현재 project-local `runner.py`가 자체적으로 처리, 어떤 Kernel/Execution Layer 코드도 관여하지 않는다 |
| 외부 경계 | **미정의.** `BASELINE.md` §6 Concept Model 10개 분류(Entity/Definition/Process/Event/Service/Interface/Metadata/Policy/State/Resource) 어디에도 "Acquisition"이나 "External Data"가 없다. Meta Architecture(§5)의 "Connector(MCP)"와의 관계도 미정 |
| 현재 구현 여부 | **project-local 관행으로만 존재.** Kernel/Development HQ Platform 어디에도 코드 없음 |
| Evidence | `AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`(재현 4건, "Acquisition — 실제 책임 경계"로 식별), `VALIDATION-0002` §Q5·P-1 |
| 미확정 | ADC-03(Connector 아키텍처 위치, Open·NEXT)과의 관계 — Acquisition이 Connector의 하위 개념인지 별개인지조차 판단된 적 없음 |

**판정**: **Phase 6이 새로 식별한 후보이나, Concept 자체가 없다.**
"책임 경계로 실제 작동했다"는 사실(재현 Evidence)과 "Architecture
Concept으로 존재해야 한다"는 판단은 다른 층위다(`ADC-0011`이 이미
사용한 구분과 동일). 지금 독립 Component로 설계하는 것은 근거가
1개 project 계열(ETF/Dividend Stock)에 그친 Evidence로 새 Concept을
만드는 것이 되어, ADC 채택 기준(두 조건)에 미달한다.

---

## 2. 집중 검토 — Phase 6이 남긴 두 공백

### 2-A. Kernel Context Model ↔ Execution Layer 연결

**현재 상태**: 두 체계가 **의도적으로 분리**되어 있다.

| | Kernel Context (§13~15) | Execution Layer (§16.2) |
|---|---|---|
| 단계 수 | 6단계(Collect~Render) | 6단계(Request~Result) — 이름이 다르다 |
| 입력 | Segment + Ordering Policy | Implementation Specification(`str`) |
| Renderer | X-1 확장 지점, Defer | `prompt_specification_builder.py`(RENDERING_MAP 고정) |
| 관계 판정 | — | §15.3 각주: "Execution Layer의 기존 Builder를 판정하지 않는다 — Kernel Context를 입력으로 받지 않으므로 Kernel Renderer가 아니다" |

**두 체계가 우연히 닮았다는 사실**(둘 다 6단계, 둘 다 결정론적)이
**둘이 같은 Component여야 한다는 근거는 아니다** — `ADC-0009`가
Model 축과 Component 축의 이름이 겹치는 것("Communication",
"Memory")조차 "이름이 같다는 사실과 개념이 같다는 것은 다르다"며
대응을 거부한 것과 동일한 원칙이 여기에도 적용된다.

**판정**: **지금 통합을 시도하지 않는다.** 근거:
1. R-3(Renderer의 순서 재배치 금지)이 아직 미채택 상태이며, 이것이
   해소되지 않고는 `prompt_specification_builder.py`의 `RENDERING_MAP`이
   Kernel Renderer 계약(R-1·R-2·R-4·R-5)을 만족하는지 판단할 수 없다.
2. ADR-0005가 정한 재검토 조건("Execution Layer가 훗날 Kernel
   Context를 사용하도록 정렬되면")이 아직 발생하지 않았다 — Execution
   Layer는 현재 `str` 텍스트 파이프라인으로 완결되어 있고, 이를
   바꿔야 할 필요가 코드에서 관찰된 적이 없다.
3. 통합을 시도하면 §10이 막고 있는 "Kernel Component Architecture
   설계"에 사실상 착수하는 것과 같다 — 이 문서의 권한 밖이다.

**새롭게 확인한 것(이 문서의 기여)**: 두 체계의 단계 이름이
우연히 대응되는 것처럼 보이는 표(위)가 오히려 **오독 위험**이라는
점 — 향후 누군가 이 대응을 "설계 근거"로 오용하지 않도록, 이
비교표 자체를 "닮았지만 별개"라는 결론과 함께 문서화해 둔다.

### 2-B. External Data ↔ Acquisition Boundary

**현재 상태**: C-8에서 정리한 그대로 — Concept 미정의, project-local
관행으로만 존재.

**추가 검토**: 이 경계가 Kernel Component가 되려면 최소 다음이
필요하다(현재 전부 결여):
1. Concept Model(§6)에 분류 위치가 있어야 한다 — 없음.
2. 재현 Evidence가 1개 project 계열을 넘어야 한다 — 현재 ETF/Dividend
   Stock 4건뿐(Stock Team, Investment HQ 밖 domain 사례 없음).
3. ADC-03(Connector 위치)이 먼저 해소되어야, Acquisition이 Connector의
   하위인지 별개인지 판단 가능하다 — ADC-03은 여전히 Open.

**판정**: **RFC 후보로도 아직 이르다.** `docs/02_rfc/RFC_CANDIDATES.md`
수준(Pending, 승격 조건 명시)으로도 등재하지 않는다 — 그 문서의
5개 후보는 전부 "MVP-0001 구현 완료" 조건이 이미 충족된 상태에서
남은 재확인만 기다리는데, Acquisition은 "무엇을 후보로 삼을지" 조차
아직 불확실하다(project-local raw_data.md 작성 관행 자체가 project
마다 조금씩 다를 수 있음 — 아직 표준화 시도가 없었다).

---

## 3. ADC 채택 기준 대조

`ARCHITECTURE_GOVERNANCE.md`의 두 조건을 8개 후보 전부에 대조한다.

| 후보 | (1) 지금 결정 안 하면 진행 불가 | (2) 지연 비용이 매우 큼 | RFC 필요 |
|---|---|---|---|
| C-1 Kernel Context | 아니오 — 이미 §13~15로 Responsibility 확정, 추가 결정 불필요 | 아니오 | **불필요** |
| C-2 Task/Workflow | 아니오 — 하드코딩으로 계속 진행 가능, Stop Trigger 미발동 | 아니오 — ADC-09가 이미 NOW로 등재, 이 문서가 새로 추가할 것 없음 | **불필요(기존 ADC-09가 이미 추적 중)** |
| C-3 Agent/Capability | 아니오 — §7이 이미 HQ 책임으로 확정, Kernel Component 후보 아님 | 아니오 | **불필요** |
| C-4 Execution | 아니오 — 이미 Accept·구현·검증 완료 | 아니오 | **불필요** |
| C-5 Registry/Lifecycle | 아니오 — 두 HQ 모두 비-live로 정상 동작 중 | 아니오 — "되돌릴 상태" 자체가 없음(`INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001` §5-1과 동일 논리) | **불필요** |
| C-6 Memory | 아니오 — in-memory 변수로 계속 충분 | 아니오 | **불필요** |
| C-7 Event/State | 아니오 — Multi-HQ 시나리오 자체가 아직 없음 | 아니오 | **불필요** |
| C-8 External Data/Acquisition | 아니오 — 재현 Evidence 1개 계열, 표준화 시도 없음 | 아니오 — 문제가 실제 피해로 이어진 사례 없음(재현 결과 Execution 결함 아님으로 확정) | **불필요(단, ADC-03 우선순위 상승 시 참고 자료로 인용 권고 — VALIDATION-0002 P-1과 동일)** |

**8개 후보 전부 RFC 채택 기준 미충족.** 이는 "Kernel Component
Architecture를 지금 설계하지 않는 것이 맞다"는 §10의 기존 판단과
일치하며, 이 문서가 그 판단을 뒤집을 새 Evidence를 발견하지
못했다는 뜻이다.

---

## 4. 최종 보고

### 확정된 Component

**없음.** 이 문서는 어떤 Component도 "확정"하지 않는다 — §10이
Kernel Component Architecture를 Out of Scope로 유지하는 한, 확정은
이 문서의 권한 밖이다. 대신 8개 후보의 **현재 Evidence 상태**를
확정했다(위 §1·§3).

### 각 Component 책임 (후보 수준 요약)

| Component | Responsibility 확정 여부 | Component(구현) 확정 여부 |
|---|---|---|
| Kernel Context | **확정**(§13~15, ADR-0003~0005) | 미확정(§10 Out of Scope) |
| Task/Workflow | 부분 확정(Task Flow는 §6) | 미확정(ADC-09 Open) |
| Agent/Capability | **확정**(§7, HQ 책임) | Kernel Component 대상 아님 |
| Execution | **확정**(§16.2, ADR-0002) | **구현됨**(유일한 사례) |
| Registry/Lifecycle | **확정**(§7, Kernel 책임) | 미착수 |
| Memory | Non-Goal로 확정(§14.6 N-4) | 미착수, 필요성도 Defer |
| Event/State | 부분 확정(§6 Event Flow) | 미착수, ADC-04·05·08 Open |
| External Data/Acquisition | **미확정** — Concept 자체 없음 | 미착수 |

### Component 간 Boundary

- Kernel Context(C-1)와 Execution(C-4)은 **닮았지만 별개**(§2-A) —
  통합 시도하지 않는다.
- Agent/Capability(C-3)는 Kernel Component가 아니라 HQ 책임이며,
  Registry(C-5)를 통해서만 Kernel과 접촉한다(탐색 대상으로서).
- Memory(C-6)는 Kernel Context(C-1)가 만든 값을 영속화할 뿐 스스로
  값을 만들지 않는다 — 의존 방향은 C-6 → C-1(단방향).
- Event/State(C-7)는 Task/Workflow(C-2)의 실패(Fault)에서 파생된다
  — 의존 방향은 C-7 → C-2.
- External Data/Acquisition(C-8)은 현재 어떤 Kernel Component와도
  경계가 정의되어 있지 않다 — 고립된 project-local 관행.

### 새롭게 발견된 문제

1. **§2-A 오독 위험**: Kernel Context와 Execution Layer가 둘 다
   6단계라는 표면적 유사성이 향후 "이미 같은 구조이니 통합해도
   된다"는 근거로 오용될 위험이 있다 — 이 문서가 그 위험을
   명시적으로 기록했다(새 Architecture 문제라기보다 **오용 방지를
   위한 기록**).
2. 그 외 새 Boundary Violation이나 새 Architecture 결함은 발견되지
   않았다 — 8개 후보 전부가 기존 ADC/§10/§7의 판단과 일치했다.

### Architecture 변경 필요 여부

**없음.** 8개 후보 전부 ADC 채택 기준(§3) 미충족.

### Governance 필요 여부

**없음.** 새 RFC/ADC/ADR을 열지 않는다. 기존 Open 항목(ADC-01·03·
04·05·06·08·09·11)은 그대로 유지하며, 이 문서는 그중 어느 것도
재조사하지 않았다 — 상태만 인용했다.

### 다음 구현 단계

Kernel Component 구현은 **다음 단계로 넘어가지 않는다** — 8개 후보
모두 지금 설계할 근거가 없다는 것이 이 Phase의 결론이다. 대신:

1. C-2(Task/Workflow): ADC-09가 NOW 우선순위로 이미 추적 중 — 그
   결정이 나면 재검토.
2. C-8(External Data/Acquisition): 재현 표본이 다른 project 계열
   (예: Investment HQ 4번째 Dogfooding, 또는 향후 새 HQ)로 늘어나면
   재검토.
3. C-1↔C-4 연결(§2-A): R-3 채택 또는 Execution Layer가 Kernel
   Context를 실제로 요구하게 되는 시점(ADR-0005 재검토 조건)에
   재검토.
4. C-5(Registry): ADC-01·ADC-02 둘 다 해소되어야 착수 가능(Phase 6
   VALIDATION-0002 §Q4와 동일 결론).

### Tests / Evidence

이 문서는 코드를 작성하거나 실행하지 않았다. 인용한 Evidence는
Phase 6 검증 실행(`58 passed`, `VALIDATION-0002` §0)과 기존 문서
대조뿐이다 — 새 테스트 실행 없음.

### Files

`docs/architecture/core/COMPONENT-CANDIDATE-0001-kernel-component-architecture-review.md`
(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

### Commit / Branch

Branch: `claude/jarvis-os-documentation-drift-9lymtn`. 이 문서만
커밋 대상이다.

---

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**. 8개
  후보 전부 "후보"로만 기록했다.
- Baseline 문서를 변경했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**.
- ADR이 필요한가 — **아니오**.
- 코드를 작성했는가 — **아니오**.

## Self Review

- §10 Out of Scope(Kernel Component Architecture)를 우회했는가 —
  **아니오**. 이 문서는 "설계한다면"의 후보 평가이며, 어떤 항목도
  Accept·확정하지 않았다.
- ADC-01·02·03·09·10·11을 재조사했는가 — **아니오**. 상태만
  인용했다.
- 8개 후보 중 일부라도 억지로 Component로 승격시켰는가 — **아니오**.
  전부 ADC 채택 기준 미충족으로 판정했다.
- 새 RFC/ADC/ADR을 만들었는가 — **아니오**.
