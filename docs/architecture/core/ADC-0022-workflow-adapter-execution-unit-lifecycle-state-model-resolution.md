# ADC-0022: Workflow Adapter가 소비하는 실행 단위·Lifecycle·Workflow Execution State — Team/Division 부재 하의 v2 Resolution (RFC-0021 후속, Gate (A) 부분 해소)

**Status**: Decided — ADR Required. Architecture/Governance Review PASS(§9). BASELINE/ADR 미착수, Commit/PR/Merge 대기(사용자 보고 후 진행).
**Author**: Claude Code
**선행 체인**: `RFC-0019` → `ADC-0019` → `ADR-0008` (BASELINE v1.12 §16.6 존재 Accept·Scoped·Conditional) → `RFC-0020` → `ADC-0020` → `ADR-0009` (v1.13 명칭 = **Workflow Adapter** + Adapter Contract (a)(b)(d)) → `ADC-0021` (구현 전략 프레이밍, §8이 미해결 4공백을 Gate (A)로 명명) → `ADR-0010` (v1.14 Gate (C) E4 = "부분 충족")
**RFC pairing**: `RFC-0021-workflow-adapter-execution-unit-lifecycle-state-model-boundary.md` (Proposed) — §6이 B-2·B-5·B-11 Boundary Question을 개설. 이 ADC가 그 세 질문을 판정한다(`ADC-0019`가 `RFC-0019` §8을 판정한 것과 동일 관계).
**대상**: `ADC-0021` §8 Gate **(A)** 중 **Team/Division 부재에서 비롯된 결정 2·5·11** + `ADC-0020`이 결정 11 결합으로 이연한 **(c) reducer 규약의 배치**.

> 이 ADC는 검증된 Resolution만 Architecture Decision으로 공식화한다. **새로운 Kernel Concept·Layer·Component·Public Contract·Port·enum·타입을 추가하지 않는다.** 결정 2·5·11과 (c)만 다룬다 — **결정 9(`IWorkflowEngine` Port)와 §14.1 "Task 전달 책임"은 명시적으로 별도 Track**으로 남긴다(§5 D-9). "실행 단위(Execution Unit)"는 새 Kernel Domain이 **아니라** §16.6 A-IN이 이미 전제하는 입력 경계를 설명하는 용어로만 다룬다(§5 D-0). R11-a의 종료 disposition은 그 **내용·어휘가 HQ Domain 책임**임을 유지한다(§5 D-11). §14 Kernel Public Contract를 승격하지 않고, LangGraph를 채택하지 않으며, 어댑터를 구현하지 않고, `IMPLEMENTATION_RULES.md`를 해제하지 않으며, `BASELINE.md` 문언을 편집하지 않는다. 실제 §16.6 개정은 후속 ADR이 수행한다.

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (셋 + 하나로 한정)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D-0** | "실행 단위(Execution Unit)"를 §16.6 A-IN 입력 경계를 설명하는 용어로 확정 — 새 Kernel Domain 아님 | `RFC-0021` §5·§6, `BASELINE.md` §16.3·§16.4·§16.6("실행 단위" 기존 용법), `ADR-0009` §4(Workflow Adapter 명칭을 §6에 등재하지 않은 선례) |
| **D-2** | **B-2 (결정 2)** — v2 Workflow Adapter가 소비하는 Kernel 소유 실행 단위 Lifecycle의 부재 확정 + §16.6 A-OUT 금지의 긍정형 불변조건 | `RFC-0021` §4.1·§6, `RFC-0019` §5, `ADC-0019` §Q7·조건 5, `BASELINE.md` §5·§6·§7·§16.6 A-OUT |
| **D-5** | **B-5 (결정 5)** — 결정 5가 §16.6 A-IN/A-OUT + §7로 대체됨 확정 + HQ 내부 조직 비의존 잔여 불변조건 1개 | `RFC-0021` §4.2·§6, `BASELINE.md` §5·§7·§16.6, `hqs/development/BOUNDARY.md` |
| **D-11** | **B-11 (결정 11)** — Kernel `WorkflowStatus`/`WorkflowResult` 미도입 확정 + A-IN(a) State가 담는 정보의 서술적 재구성(진행 정보 / 종료 disposition, 후자의 내용 = HQ Domain) | `RFC-0021` §4.3·§6, `RFC-0019` §5, `BASELINE.md` §16.6 A-IN·§14.3 G-6·Adapter Contract (b), `hqs/development/BASELINE.md` §Stage Data Contract |
| **D-11c** | **(c) — D-11의 하위 조건** — 병렬 State disjoint key / reducer 규약의 **배치 = HQ State 스키마**. 독립 Decision 아님 | `ADC-0020` §Q-D·§4.3, `ADR-0009` §3, E4 `projects/workflow-adapter-reversibility-v2/domain/state.py` |
| **D-9** | **결정 9 / §14.1** — 별도 Track으로 명시 분리, Gate (A) 상태를 "부분 해소"로 갱신 | `RFC-0021` §6·§7, `RFC-0019` §5, `ADC-0019` G3, `BASELINE.md` §14.1 |

### 1.2 이 ADC가 판단하지 않는 것 (경계 — 선행 확장 방지)

아래는 이 ADC의 자동 결과가 아니며, 이 판정으로 앞당겨지거나 열리지 않는다. 근거는 §7에 항목별로 재확인한다.

- 결정 9(`IWorkflowEngine` Port) / `WorkflowResult` 반환 타입 / §14.1 "Task 전달 책임"·"Engine 호출 책임"의 계약 편입 — **별도 Track**(D-9)
- §14 Kernel Public Contract 승격 / Public Responsibilities·Guarantees·Extension Points 신설·수정
- Workflow Adapter 입력의 **구체 시그니처** (v1 `IWorkflowEngine.run(team, dispatch)`의 v2 대응) — §14.1 트랙
- (c)의 정식 Adapter Contract 절 승격 / HQ State 설계 구속 강화 — `ADC-0020` §Q-D Defer 유지, D-11c는 배치 질문에만 답
- "실행 단위"를 §6 Concept Model 항목·새 Kernel Domain/Layer/Component로 승격
- Gate **(B)** (`ADC-0019` 재검토 조건 (c) — 다른 계보 또는 v2 프로덕션 관찰), Gate **(C)** 완전 discharge (`ADR-0010` "부분 충족" 유지)
- LangGraph 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 / Implementation Strategy 세부
- `IMPLEMENTATION_RULES.md` line 9/13/14/19 전면·Scoped 해제
- `docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐) / `ADC-0008` 재판단, §16.7 Workflow Kernel Module Defer 재판단
- Rule B 충족 선언 — 이 ADC는 §5 Meta Architecture 정합 판정이지 Evidence 축적이 아니다(`RFC-0021` §8)
- `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`·ADR·CLAUDE.md·Production 코드 문언 편집 — 이 ADC는 지침만 남긴다

### 1.3 새 실험 없음

이 ADC는 `main`에 이미 병합·기록된 Governance 문서(`BASELINE.md` v1.14, `RFC-0019`~`RFC-0021`, `ADC-0019`~`ADC-0021`, `ADR-0008`~`ADR-0010`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`, `GLOSSARY.md`), v1 Evidence(`archive/v1/docs/adr/0007-workflow-execution-model.md`, Accepted), E4(`projects/workflow-adapter-reversibility-v2/`), 그리고 **현재 저장소의 HQ 코드 관찰**(`hqs/investment/`·`hqs/development/`)만 인용한다. 새 PoC·프로토타입·측정을 수행하지 않는다.

### 1.4 판정의 성격 — Rule B 대상 아님

`ADC-0019` §Q2가 §16.6 존재 Accept에 대해 Rule B 형식 미충족을 명시했고, 그 판정은 이 ADC로 바뀌지 않는다. 그러나 결정 2·5·11의 v2 재설계는 **Evidence 축적 문제가 아니라 §5 Meta Architecture와의 정합 문제**다(`RFC-0021` §8·§Non-goals). §5가 Team/Division을 Kernel 밖으로 둔 것이 확정 사실이고, 이 ADC는 그 위에서 "그렇다면 §16.6이 전제하는 입력·Lifecycle·State는 v2에서 어떻게 성립하는가"를 기존 문언·코드 정합으로 판정한다. 따라서 재검토 조건 (c)(Gate (B))는 이 판정의 선행조건이 아니며, 이 ADC 이후에도 다음 단계(§14 승격, LangGraph 채택, Scoped 해제, 구현 착수)의 hard gate로 그대로 존속한다(§6).

---

## 2. Evidence

`RFC-0021` §2가 인용한 자료 + 이 세션의 HQ 코드 관찰. **`RFC-0021`의 §4 "가능한 해소 형태"는 예시이지 결정이 아니며, 이 ADC가 D-2/D-5/D-11로 확정한다.**

| # | Evidence | 이 ADC에서의 용도 |
|---|---|---|
| **V1** | v1 `archive/v1/docs/adr/0007-workflow-execution-model.md` (Accepted) — 결정 2(전이 규칙은 Core, Engine은 조립자·대안 B 기각), 결정 5(Division↔Team, Selection은 개입 이전), 결정 11(`WorkflowStatus` = `TeamState`와 별개 축의 Core Domain State Model, `WorkflowResult`가 포함) | D-2·D-5·D-11의 v1 의도 기준선 |
| **V2** | `BASELINE.md` §5 — 계층 = `Jarvis OS → HQ → Agent → Connector`, "Division과 Team은 HQ 내부에서 선택적으로 … Jarvis OS는 그 존재 여부를 알지 못한다" | D-0·D-2·D-5(Team/Division의 Kernel 밖 배제) |
| **V3** | `BASELINE.md` §6 — State 분류 = `Context, Lifecycle State`; 관계 서술에 "HQ는 Lifecycle State를 가진다"만. §7 — "HQ의 생명주기 관리 및 상태 전환 통제" = Jarvis OS 책임; "HQ 내부 조직 구조 (Division/Team의 존재 여부, 이름, 책임 분담)" = Jarvis OS **비**책임, "내부 조직 구조 결정" = HQ 책임 | D-2(Kernel이 아는 유일한 생명주기 = HQ Lifecycle, 실행 단위 아님), D-5(§7 정합) |
| **V4** | `BASELINE.md` §16.6 A-IN("HQ가 이미 정의한 Workflow 그래프와 이미 구성된 실행 단위를 입력으로 받아", 개입 구간 "HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두 끝나는 시점"), A-OUT("Domain Lifecycle 전이 규칙 — HQ/Agent의 상태 전이 자체 … Adapter가 재구현하지 않는다, v1 `ADR-0007` 결정 2·대안 B 기각과 동일 원칙"), A-IN(a)("공유 실행 상태(State)의 보유"), A-IN(e)/Adapter Contract (a)(caller-owned Checkpoint 값), Adapter Contract (b)(실행 결과의 값 표현 = 어댑터 책임), §14.3 G-6(No Silent Failure) | D-0·D-2·D-5·D-11 전부 — 이미 흡수된 부분의 출처 |
| **V5** | `RFC-0019` §5 — v1 12개 결정의 v2 재해석 표. 결정 2·5·11의 공백 원인 = Team/Division 부재; 결정 9의 공백 원인 = §14.1(별개·상위). `ADC-0019` G3 동일 | D-2/D-5/D-11 ↔ D-9의 2분할 계승 |
| **V6** | `hqs/investment/teams/stock_team.py`·`dividend_stock_team.py`·`etf_team.py` — `run()` 함수 하나, wave 순서 하드코딩("Workflow Parser 아님"), `ThreadPoolExecutor`, 파일 기반 `Checkpointer`. `Team` 클래스·`TeamState` 상태 머신 **부재**. `run()`은 `dict` 반환 | D-2(실행 단위 상태 머신 부재 실측), D-11(Kernel status enum 부재) |
| **V7** | `hqs/investment/run.py` — `TEAMS = {…}` 리터럴 딕셔너리("Registry 아님"), `team.run(...)` 직접 호출, Division/catalog 선택 없음. `hqs/investment/trader.py` `parse_decision()` → `{action, rationale, reassessment_trigger, warnings}`, `action ∈ {BUY, SELL, HOLD}` = HQ 도메인 어휘 | D-5(조직 구조가 Adapter 경로에 없음), D-11(종료 어휘 = HQ 도메인) |
| **V8** | `hqs/investment/checkpoint.py` — "고정 매핑만 다루는 Registry/Scheduler 아님", manifest(`completed_steps`, `call_log`)를 caller(issue_dir)가 보유. `ContentFailureError`는 저장하지 않아 다음 실행 Resume 대상(값 기반 실패 표현) | D-11(진행 정보 = caller 소유 값, §16.6 A-IN(a)·(a) 정합) |
| **V9** | `hqs/development/mvp/workflow.py`·`workflow_0009.py` — Task 직접 함수 호출, `try/except` → 오류 메시지를 **반환 dict의 값으로**(예외 비전파). `hqs/development/mvp/execution_host.py` — "비동기 lifecycle(PENDING/RUNNING 상태 조회)은 … 구현하지 않는다" 명시 | D-2(Dev HQ도 실행 단위 Lifecycle 없음), D-11((b)/G-6 실측) |
| **V10** | `hqs/development/BASELINE.md` §"Stage Data Contract (ADR-0009)" — Stage 01~05의 5개 `*Result` 딕셔너리 = **HQ-level Public Contract**, "Kernel Public Contract(§14)와 별개 … Kernel Baseline을 확장하거나 대체하지 않는다". `VerificationResult.status ∈ {PASS, FAIL, INCONCLUSIVE, SKIPPED}` — 내용은 HQ 소유, 개정 절차만 Jarvis OS Governance | **D-11 결정적 근거** — 종료 disposition의 어휘가 이미 HQ마다 다르고 HQ가 소유. Kernel enum이 있으면 충돌 |
| **V11** | `hqs/development/BOUNDARY.md` 책임 표 — "내부 조직 구조 사용 여부 \| Division/Team 관례를 쓸지 말지 결정" = **HQ 항목**; "Workflow 내용 \| 어떤 업무를, 어떤 순서로 … 정의" = HQ 항목 | **D-5 결정적 근거** — 비의존 불변조건이 HQ 문서에 이미 실재 |
| **V12** | E4 `projects/workflow-adapter-reversibility-v2/domain/state.py` — `REDUCER_KEYS = ("data_flags", "debate_log")`, `SECTION_KEYS`(분석가별 disjoint)를 **도메인 모듈**에 선언. 어댑터(`adapters/sequential.py`·`adapters/langgraph.py`)가 그 선언을 읽어 각자 방식(명시적 `_merge()` / `Annotated[list, operator.add]`)으로 이행. E4 IN-1 = 두 어댑터 최종 State 동치 | **D-11c** — (c) 배치 = HQ 스키마의 실측, 어댑터 의무는 기계적 |
| **V13** | `ADC-0020` §Q-D·§4.3·§12 #1, `ADR-0009` §3 — (c)는 신규 표면이므로 Defer, "reducer 선언 위치(HQ 스키마 vs 어댑터 내부)가 결정 11과 얽힌다", "(i) 계약화 여부 (ii) 배치 (iii) HQ 구속 여부는 결정 11 결합 후속 판정" | D-11c의 위임 근거 — 이 ADC는 (ii) 배치에만 답 |
| **V14** | `BASELINE.md` §14.1 — "Task 전달 책임"·"Engine 호출 책임" = **미결, 계약 범위 밖**. `RFC-0021` §7·§8 Non-goals — 결정 9는 별개·상위 Track | D-9 |
| **V15** | `ADC-0021` §8 Gate (A)/(B)/(C), 진입 순서. `ADR-0010` — Gate (C) E4 "부분 충족", 잔여 한계 (i)~(iii). Gate (A)/(B) 미충족 유지 | D-Gate-A, §6·§7 |
| **V16** | `IMPLEMENTATION_RULES.md` line 9/13/14/19 + "Dynamic Workflow 재검토 Trigger" — Workflow Parser/Scheduler/Dynamic Routing/Runtime/Event Bus 구현 금지 | §6·§7 — 이 ADC가 해제하지 않음 확인 |

---

## 3. Alternatives

### 3.1 이 ADC의 형태

| | 내용 | 판정 |
|---|---|---|
| **F-0** | 결정 2·5·9·11을 한 ADC에서 모두 판정(`ADC-0021` §8 Gate (A) 문면 그대로) | **Reject** — 결정 9의 공백 원인은 Team 부재가 아니라 §14.1(V5·V14). 서로 다른 절차로 해소되며, 결정 9를 이 ADC에 넣으면 §14.1 "Task 전달 책임"을 우회 확장하게 된다(`RFC-0021` §7). |
| **F-1 (채택)** | 결정 2·5·11 + (c) 배치만 판정, 결정 9는 별도 Track으로 명시. 검증된 Resolution(R2-c/R5-b/R11-a)만 공식화하고 새 Kernel 개념 없음 | **Accept (§5)** — `RFC-0021` §5·§6이 이미 수행한 "2·5·11 ↔ 9" 2분할을 계승. Gate (A)를 "부분 해소"로 갱신(D-Gate-A) |
| **F-2** | B-2/B-5/B-11을 지금 판정하지 않고 §14 승격 자체가 먼저여야 한다고 Defer | **Reject** — §14 승격은 결정 2/5/9/11 해소 **이후**에만 가능(`ADC-0019` 조건 5). 순서가 반대다. 결정 2·5·11은 §5 정합만으로 지금 판정 가능하며(§1.4), 이를 미루면 Gate (A)가 영구히 닫히지 않는다 |

### 3.2 "실행 단위" 용어의 지위

| | 내용 | 반대 근거 |
|---|---|---|
| **U-1 (채택)** | §16.6 A-IN 입력 경계를 **설명하는 용어**로만. §6 Concept Model 미등재. 새 Kernel Domain/Layer/Component 아님 | `ADR-0009` §4가 "Workflow Adapter"를 §6에 등재하지 않은 선례. §16.3·§16.4가 이미 "실행 단위"를 정의 없이 쓰고 있으므로 §16.6도 동일 층위의 설명 용어면 충분 |
| **U-2** | "실행 단위"를 §6 Concept Model에 새 항목으로 등재 | 사용자 지시 위반("새 Kernel concept 추가 마라"). §6은 Jarvis OS 전체 수준 어휘 기준선이고 §16.x Module 내부 용어를 넣으면 "Runtime"·"Task"와의 관계를 §6이 스스로 설명해야 하는 부담(`ADR-0009` §4) |
| **U-3** | "실행 단위"를 정의하지 않고 §16.6 A-IN 문언을 그대로 둠 | 결정 2·5·11이 모두 이 미정의 용어로 귀결되므로(§4.1), 최소 1문단 설명 없이는 세 Resolution이 "무엇에 대한" 것인지 문서 수준에서 불명확 |

### 3.3 결정 11 State Model의 형태

| | 내용 | 판정 |
|---|---|---|
| **S-a (채택 = R11-a)** | Kernel은 `WorkflowStatus` enum·`WorkflowResult` 타입 미도입. A-IN(a) State가 담는 정보를 "진행 정보 / 종료 disposition 정보"로 **서술**하되, 종료 disposition의 **내용·어휘 = HQ 도메인**(§7), Kernel은 형식((b)+G-6)만 | **Accept** — V6·V7·V10이 실측한 v2 실태와 정합. Kernel enum 부재, HQ마다 다른 종료 어휘 |
| **S-b (= R11-b)** | Kernel이 내용 없는 최소 "종료 disposition 축"을 A-IN(a) State의 필수 형식으로 **규범 정의** | **Reject** — 새 Kernel 규범 개념. `stock_team.py`는 종료 상태를 명시 필드로조차 두지 않는다(V6) — "항상 명시 축" 규범을 현재 코드가 부분적으로만 뒷받침. 사용자 지시("새 Contract 추가 마라")와 충돌 |
| **S-c (= R11-c)** | 구조적 State Model을 `WorkflowResult`(결정 9)와 함께 §14.1 트랙으로 이연, 지금은 값-표현 부분만 종결 | **부분 채택** — 결정 11의 **결과 반환 타입** 측면은 S-c대로 §14.1 트랙(D-9). 그러나 "State가 무엇을 담는가"의 서술적 답은 S-a가 지금 제공 가능하며, 이연하면 Gate (A)가 결정 11에서 닫히지 않는다 |

---

## 4. Analysis

### 4.1 세 결정은 같은 미정의 용어로 귀결된다 (D-0의 근거)

`RFC-0021` §1이 지적했듯 §16.6 A-IN의 "이미 구성된 실행 단위"는 **무엇인지를 전제로만 두고 정의하지 않는다**. v1에서 그것은 `Team`이었고 결정 2(그 단위의 생명주기)·결정 5(그 단위 구성의 경계)·결정 11(그 단위 실행의 결과·상태)이 `Team`을 축으로 세워졌다. v2는 `Team`을 §5로 배제했으므로 세 결정의 축이 사라졌다.

`grep` 확인: `BASELINE.md`에서 "실행 단위"는 §16.3(Execution Host "단일 실행 단위")·§16.4(Multi-Task "독립 실행 단위")·§16.6("이미 구성된 실행 단위")에서 쓰이나 **정의 문장이 없다**. §16.3은 "Command(불변)에도 Task(identity/lifecycle)에도 속하지 않는 단일 실행 단위"라고 소극적으로만 언급한다.

따라서 D-0은 세 Resolution의 공통 전제를 1문단으로 고정한다 — **새 Domain을 만드는 것이 아니라, 이미 세 절이 쓰고 있는 용어에 §16.6 맥락의 설명을 붙이는 것**이다(U-1). 이 설명이 있어야 D-2가 "그 단위의 생명주기는 v2에 없다", D-5가 "그 단위 구성 경계 = 입력 경계", D-11이 "그 단위 실행이 생산하는 State"를 각각 무엇에 대해 말하는지가 명확해진다.

### 4.2 B-2 — v2에 소비할 Lifecycle이 없다 + HQ Lifecycle과의 2층 분리 (D-2의 근거)

v1 결정 2는 "Workflow Engine은 `Team.activate()`/`complete()`/`terminate()`를 정해진 순서로 호출하는 조립자이지 전이 규칙의 소유자가 아니다"였다. 이 결정이 성립하려면 **소유될 전이 규칙이 존재**해야 한다.

- **구조적 부재**: §5가 `Team`/`TeamState`를 Kernel 밖으로 두었으므로, Adapter가 소비할 Kernel/Core 소유 실행 단위 생명주기의 v2 대응물이 없다(V2·V5).
- **코드 정합**: Investment 3팀 + Dev HQ workflow 전부 실행 단위 상태 머신이 없다(V6·V9). `execution_host.py`는 "비동기 lifecycle … 구현하지 않는다"고 명시한다(V9).
- **§16.6 A-OUT의 금지 절반은 이미 있다**: "Domain Lifecycle 전이 규칙 — HQ/Agent의 상태 전이 자체 … Adapter가 재구현하지 않는다, v1 `ADR-0007` 결정 2·대안 B 기각과 동일 원칙"(V4). 결정 2의 Drift 방지 정신은 v2 문언에 살아 있다.

**남은 gap = 긍정 정의**. A-OUT은 "재구현하지 않는다"만 말하고 "그렇다면 무엇을 소비하는가"의 답이 없다. D-2는 이를 두 층으로 나눠 채운다:

1. **실행 단위 수준**: Adapter 개입 구간에 소비할 Kernel 소유 생명주기 전이가 **없다**. Adapter는 A-IN(a) 그래프 진행 State만 다룬다.
2. **HQ Lifecycle 수준**: §6 "HQ는 Lifecycle State를 가진다" + §7 "HQ 생명주기 관리·상태 전환 통제 = Jarvis OS"는 **변경되지 않는다**. HQ Lifecycle은 Adapter 개입 구간 **밖**(§16.6 개입 구간은 "HQ가 실행 단위를 구성한 이후 ~ 실행 종료")에서 Jarvis OS가 통제하며 Adapter가 전이시키지 않는다.

그리고 A-OUT 금지의 **긍정형**을 조건형으로 명문화한다: "HQ가 구성한 실행 단위가 자체 도메인 전이 로직을 포함하면, Adapter는 그것을 호출만 하고 재구현·재정렬하지 않는다." 현재 이 조건을 트리거하는 실행 단위 전이 로직은 어느 HQ에도 없으므로(V6·V9), 이 조항은 미래 대비로 존속하되 "현재 트리거 없음"을 명시한다.

### 4.3 B-5 — §16.6 A-IN/A-OUT + §7이 결정 5를 대체하며, HQ 문서가 잔여 불변조건을 이미 담는다 (D-5의 근거)

결정 5의 관심사는 "Workflow Engine은 실행 단위 구성·선택 경계를 넘지 않는다"였다. v2에서:

- §16.6 A-IN "이미 구성된 실행 단위를 입력으로 받아" + 개입 구간 한정 = 결정 5의 "Selection은 개입 이전"의 v2 등가물(V4).
- §16.6 A-OUT "HQ Routing/Registry" 제외 + §7 "HQ 내부 조직 구조 (Division/Team의 존재 여부, 이름, 책임 분담) = Jarvis OS 비책임"(V3·V4).
- **코드 정합**: `run.py`가 `TEAMS` 리터럴 딕셔너리 + `team.run()` 직접 호출, Division catalog 선택이 Adapter 경로에 없다(V7). "team"은 함수 모듈일 뿐이다(V6).

**남은 gap = 잔여 불변조건의 명시**. `RFC-0021` §4.2는 "결정 5가 완전 흡수되어 별도 의무가 남지 않는지, 아니면 잔여 불변조건이 필요한지가 판단 대상"으로 열어두었다. D-5는 **1개 잔여 불변조건(확인용 서술)**을 채택한다: "입력('이미 구성된 실행 단위')은 HQ 내부 조직 구조와 독립적으로 성립하며, Adapter는 그것을 관측하지도 의존하지도 않는다."

근거: `hqs/development/BOUNDARY.md`가 "내부 조직 구조 사용 여부 | Division/Team 관례를 쓸지 말지 결정"을 **HQ 책임 표**에 이미 명시한다(V11). 즉 이 불변조건은 새 의무가 아니라 HQ 문서에 실재하는 경계의 Kernel 쪽 확인이다. **적용 방향**: 후속 Adapter Contract 정련이나 Public Port 정의가 HQ 내부 조직 구조를 입력 스키마에 노출하면 이 불변조건 위반이다 — 이것이 이 서술의 실질 효용이다.

입력의 **구체 시그니처**(v1 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 D-5 대상이 아니다 — Investment `team.run(company_label, raw_data_path, issue_dir)`, Dev `run_mvp_0001(code)`처럼 HQ마다 다르며, 계약화는 §14.1 "Task 전달 책임" 트랙(D-9)이다.

### 4.4 B-11 — Kernel enum은 v2에서 불필요하고 HQ 계약과 충돌한다 (D-11의 근거)

v1 결정 11은 `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}`를 `TeamState`와 별개 축의 **Core Domain State Model**로 두고 `WorkflowResult`가 이를 포함하게 했다.

- **Kernel enum 부재 실측**: v2 코드에 `SUCCESS/FAILURE/CANCELLED` Kernel enum·`WorkflowResult` 타입이 0건이다(V6). v1의 `IWorkflowEngine`/`WorkflowResult`는 `archive/v1`에만 있다.
- **종료 disposition은 이미 HQ 도메인이다**: Development HQ가 `VerificationResult.status ∈ {PASS, FAIL, INCONCLUSIVE, SKIPPED}`를 **HQ-level Public Contract**로 보유하며, `hqs/development/BASELINE.md`가 이를 "Kernel Public Contract(§14)와 별개 … Kernel Baseline을 확장하거나 대체하지 않는다"고 명시한다(V10). Investment HQ는 `BUY/SELL/HOLD` + `run()` 완료로 표현한다(V7). **HQ마다 종료 어휘가 다르므로**, Kernel `WorkflowStatus` enum은 불필요할 뿐 아니라 이 HQ 계약들과 어휘·소유권이 충돌한다.
- **이미 흡수된 형식 제약**: "실행 결과는 예외가 아닌 값으로"(§16.6 A-IN)·§14.3 G-6·Adapter Contract (b)(catch-and-encode = 어댑터 책임)가 종료 disposition의 **형식**을 이미 담당한다(V4·V9).

**남은 gap = 구조적 State Model + "별개 축" 재구성**. D-11은 이를 **서술적으로** 채운다(S-a):

- §16.6 A-IN(a) "공유 실행 상태(State)의 보유"가 담는 정보를 두 종류로 **기술**한다 — (1) 진행 정보(어느 Node/무엇을 반복 중, Adapter 생산·caller 소유 값), (2) 종료 disposition 정보(어떻게 끝났는가). 이는 **규범 축 정의가 아니라 서술**이다.
- 종료 disposition 정보가 State 값으로 표현되고 예외로 전파되지 않는 것은 (b)+G-6의 **형식 제약**이며, 그 **내용·어휘**는 §7상 HQ 도메인 책임이다 — Kernel은 규정하지 않는다.
- "별개 축" 재구성: v1의 "`WorkflowStatus` vs `TeamState`"는 v2에서 "진행 정보 vs 종료 정보"로 **약하게** 재기술된다. 둘은 A-IN(a) State가 함께 담을 수 있는 정보이지 Kernel이 강제하는 별도 State 축이 아니다.

**한계 인정(§9.2 리스크와 연결)**: `stock_team.py`는 종료 상태를 명시 필드로조차 두지 않는다(성공 시 `dict` 반환, 실패 시 `ContentFailureError`)(V6·V8). 따라서 D-11은 "Kernel이 종료 disposition 축의 존재를 요구한다"고 말하지 **않는다** — "A-IN(a) State가 담는 정보의 종류를 기술"하는 수준에 한정한다. 이것이 S-a와 S-b(Reject)를 가르는 선이다.

**결과 반환 타입**(`WorkflowResult` 대응)은 D-11 밖 → §14.1 트랙(D-9). 즉 결정 11은 "State가 무엇을 담는가"에서 닫히고, "결과를 호출자에게 어떤 타입으로 돌려주는가"는 결정 9와 함께 열린 채로 남는다.

### 4.5 (c) — R11-a의 하위 조건으로서 배치만 답한다 (D-11c의 근거)

`ADC-0020` §Q-D는 (c)(병렬 fan-out Node가 reducer 선언 없이 동일 State 키에 쓰면 `InvalidUpdateError`/비결정)를 Defer하며 그 이유를 "reducer 선언 위치(HQ 스키마 vs 어댑터 내부)가 결정 11과 얽힌다"고 했다(V13). D-11이 "종료/진행 정보의 내용·State 스키마 = HQ 도메인"(S-a)으로 성립하면, **배치는 그 안에서 따라온다**:

- **선언 위치 = HQ State 스키마**: E4 `domain/state.py`가 `REDUCER_KEYS`·`SECTION_KEYS`를 도메인 모듈에 선언하고, 어댑터가 그것을 읽어 각자 방식으로 이행한다(V12). E4 IN-1이 두 어댑터의 최종 State 동치를 확인했다.
- **어댑터 의무 = 기계적**: HQ 스키마가 "이 키는 브랜치별 disjoint / 이 키는 accumulate"를 선언하면 어댑터는 그 선언을 결정론적으로 이행하고 쓰기를 조용히 누락하거나 비결정적으로 교차시키지 않는다. 이는 A-IN(a) + (b)가 이미 함의하는 범위이며 **새 계약 절이 아니다**.
- **실제 HQ 부담 없음**: `stock_team.py` wave1은 각 job이 별도 키(`wave1_results[n]`)에 쓴다 = 완전 disjoint, 병합은 caller 루프(V6). 공유 키 병렬 쓰기·reducer 필요 사례가 실제 HQ에 **0건**이다.

**규범 효력**: D-11c는 (c)의 **배치 질문((ii))에만** "HQ 스키마"로 답한다. **계약화 여부((i))와 HQ 설계 구속 강화((iii))는 판정하지 않는다** — `ADC-0020` §Q-D Defer와 `ADR-0009` §3의 "후속 판정" 상태를 이 ADC가 약화하지 않는다. (c)는 문서화된 hazard + 배치 원칙으로만 존재하며, R11-a가 성립하는 한 정식 계약 절로의 승격 필요가 관찰되지 않았다. **(c)는 독립 Decision이 아니다** — D-11의 하위 조건이다.

### 4.6 결정 9를 분리하는 근거와 Gate (A) 상태 (D-9·D-Gate-A)

`RFC-0019` §5와 `ADC-0019` G3이 이미 수행한 2분할을 계승한다:

- **결정 2·5·11**: 공백 원인 = Team/Division 부재. §5 정합 판정으로 이 ADC가 해소.
- **결정 9**: 공백 원인 = §14.1이 "Task 전달 책임"·"Engine 호출 책임"을 계약 범위 밖으로 두는 것(V14). Port의 입력 절반(Team)은 결정 2·5와 같은 사유로 막혀 있었으나, `TaskDispatch`/`WorkflowResult` 계약 자체는 §14.1이라는 별개·상위 미결 사유를 갖는다. 이 ADC가 결정 9를 다루면 §14.1을 우회 확장하게 된다(`RFC-0021` §7).

따라서 `ADC-0021` §8 Gate (A)(= 결정 2/5/9/11)의 상태는 이 ADC 이후 **"부분 해소"**로 갱신된다:

> **Gate (A) — 부분 해소**: 결정 2·5·11 = Resolved(`ADC-0022`). 결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처) = §14.1 "Task 전달 책임" 트랙 pending — 별도 RFC → ADC → ADR이 다루며 그 착수 여부·시점은 `ADC-0022`가 정하지 않는다.

§14 Kernel Public Contract 승격은 여전히 결정 9 해소 이후에만 가능하다(`ADC-0019` 조건 5). 즉 Gate (A)의 "부분 해소"는 §14 승격을 열지 않는다 — 결정 9가 그 hard gate로 남는다.

---

## 5. Decision

**A. Accept — Resolution 공식화 (Gate (A) 부분 해소: 결정 2·5·11).** 아래 D-0~D-Gate-A는 검증된 Resolution만 Architecture Decision으로 확정하며, 새 Kernel Concept·Layer·Component·Public Contract·Port·enum·타입을 추가하지 않는다. 실제 `BASELINE.md` 반영은 후속 ADR이 수행한다(§8).

### D-0. "실행 단위(Execution Unit)" — §16.6 A-IN 입력 경계 설명 용어

§16.3·§16.4·§16.6이 이미 쓰는 "실행 단위"를, §16.6 맥락에서 다음으로 **설명**한다:

> **실행 단위(execution unit)** — HQ가 구성한 "무엇을·어떤 순서·병렬성으로·어느 Agent가 수행하는가"의 묶음으로, Workflow Adapter가 **불투명한 입력**으로 받는다. Kernel은 그 내부 구조·생명주기·조직적 출처(Division/Team 유무)를 정의하지 않는다.

**이것이 아닌 것 (명시)**: §6 Concept Model 항목이 아니다. 새 Kernel Domain·Layer·Component가 아니다. §16.7이 Defer한 Workflow Kernel Module이 아니다. `ADR-0009` §4가 "Workflow Adapter" 명칭을 §6에 등재하지 않고 §16.6 본문 용어로 둔 선례와 동일한 층위다.

### D-2. 결정 2 (Core 소유 Lifecycle 소비) — Resolved

1. **실행 단위 Lifecycle 부재**: v2 Workflow Adapter의 개입 구간("HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두 끝나는 시점")에는 **Adapter가 소비할 Kernel/Core 소유 생명주기 전이가 존재하지 않는다.** v1 결정 2가 전제한 `Team`/`TeamState`의 v2 대응물은 §5(Team/Division을 Kernel 밖으로 둠)로 인해 구조적으로 부재하며, Investment/Development HQ 코드에도 실행 단위 상태 머신이 없다(V6·V9).
2. **HQ Lifecycle과의 2층 분리**: §6 "HQ는 Lifecycle State를 가진다"와 §7 "HQ의 생명주기 관리 및 상태 전환 통제 = Jarvis OS"는 이 판정으로 **변경되지 않는다.** HQ Lifecycle State는 Adapter 개입 구간 **밖**에서 Jarvis OS가 통제하며 Adapter가 전이시키지 않는다. 위 (1)의 "생명주기 부재"는 **실행 단위 수준**에 한정된 말이지 HQ Lifecycle을 부정하지 않는다.
3. **긍정형 불변조건 (조건형)**: HQ가 구성한 실행 단위가 자체 도메인 전이 로직을 포함하는 경우, Workflow Adapter는 그 로직을 **호출만** 하고 전이 규칙을 재구현하거나 재정렬하지 않는다. 이는 §16.6 A-OUT "Domain Lifecycle 전이 규칙 재구현 금지"(v1 결정 2·대안 B 기각 인용)의 **긍정형 재기술**이며 새 의무가 아니다. **현재 이 조건을 트리거하는 실행 단위 전이 로직은 어느 HQ에도 없다** — 조항은 미래 대비로 존속한다.

**새 Kernel 개념 없음**: enum·타입·Port·Concept 추가 없음. §16.6 A-OUT 문단 보강 수준(§8).

### D-5. 결정 5 (Team/Division 경계) — Resolved

1. **대체 확정**: v1 결정 5(Division↔Team 경계, Selection은 Adapter 개입 이전)의 관심사는 v2에서 **§16.6 A-IN("이미 구성된 실행 단위" + 개입 구간 한정) + A-OUT("HQ Routing/Registry") + §7("HQ 내부 조직 구조 = HQ 책임")로 대체된다.** Team/Division이라는 이름은 §5가 배제했고, "Adapter는 이미 만들어진 것을 받는다"는 경계는 v2 문언에 살아 있다.
2. **잔여 불변조건 (확인용 서술)**: Workflow Adapter의 입력("이미 구성된 실행 단위")은 HQ 내부 조직 구조(Division/Team의 존재 여부·이름·책임 분담)와 **독립적으로** 성립하며, Adapter는 그 구조를 관측하지도 그에 의존하지도 않는다. 근거: `hqs/development/BOUNDARY.md`가 "Division/Team 관례를 쓸지 말지 결정"을 HQ 책임으로 이미 명시한다(V11).
3. **적용 방향**: 후속 Adapter Contract 정련이나 Public Port 정의가 HQ 내부 조직 구조를 입력 스키마에 노출하면 이 불변조건 위반이다.
4. **범위 밖**: 실행 단위 입력의 **구체 시그니처**(v1 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 이 판정 대상이 아니다 → D-9 / §14.1 트랙.

**새 Kernel 개념 없음**: §16.6 A-IN 프레이밍에 1문장(§8). 이 불변조건은 새 입력 계약 의무가 아니라 §5/§7이 이미 함의한 경계의 확인이다.

### D-11. 결정 11 (Workflow Execution State Model) — Resolved

1. **Kernel enum/타입 미도입**: Kernel은 v1의 `WorkflowStatus{SUCCESS, FAILURE, CANCELLED}` enum이나 `WorkflowResult` 타입을 v2에 도입하지 않는다. 이들은 `archive/v1` `IWorkflowEngine` Port·Team 시대 산물이며, v2 코드에 대응물이 없다(V6).
2. **A-IN(a) State가 담는 정보의 서술 (규범 축 정의 아님)**: §16.6 A-IN(a) "공유 실행 상태(State)의 보유"가 담는 정보는 두 종류로 **기술**된다 —
   - **진행 정보** — 그래프 어느 Node에 있는지, 무엇을 반복 중인지. Adapter가 생산하는 값이며 caller가 보관·반환한다(A-IN(e), Adapter Contract (a)).
   - **종료 disposition 정보** — 실행이 어떻게 끝났는가(성공/실패/취소에 준하는 상태). 이것이 State 값으로 표현되고 예외로 전파되지 않는 것은 §14.3 G-6 · §16.6 A-IN · Adapter Contract (b)가 이미 규정한 **형식 제약**이다. 그 **내용·어휘**(어떤 상태가 있고 무슨 뜻인지)는 §7상 **HQ 도메인 책임**이며 Kernel이 규정하지 않는다.
3. **"별개 축" 재구성**: v1은 `WorkflowStatus`를 `TeamState`와 대비해 정의했다. v2에는 `TeamState`가 없으므로 이 대비는 "진행 정보 vs 종료 정보"로 **약하게** 재기술된다 — 둘은 A-IN(a) State가 함께 담을 수 있는 정보이지 Kernel이 강제하는 별도 State 축이 아니다.
4. **Kernel은 종료 disposition 축의 존재를 요구하지 않는다**: `stock_team.py`는 종료 상태를 명시 필드로조차 두지 않는다(V6). Kernel이 요구하는 것은 (b)+G-6의 형식(경계 밖으로 나가는 결과는 예외가 아닌 값)뿐이다. 이 D-11은 "A-IN(a) State가 담는 정보의 종류를 기술"하는 수준에 한정되며, "Kernel이 disposition 축을 강제한다"로 확장되지 않는다.
5. **근거**: Development HQ가 `VerificationResult.status ∈ {PASS, FAIL, INCONCLUSIVE, SKIPPED}`를 **HQ-level Public Contract**(Kernel §14와 명시적으로 별개, 내용은 HQ 소유)로 보유하고, Investment HQ는 `BUY/SELL/HOLD` + `run()` 완료로 표현한다(V10·V7). HQ마다 종료 어휘가 다르므로 Kernel enum은 불필요하며 이 HQ 계약들과 충돌한다.
6. **결과 반환 타입**(`WorkflowResult` 대응)은 이 판정 밖 → D-9 / §14.1 트랙. 결정 11은 "State가 무엇을 담는가"에서 닫히고, "결과를 호출자에게 어떤 타입으로 돌려주는가"는 결정 9와 함께 열린 채로 남는다.

**새 Kernel 개념 없음**: §16.6 A-IN(a) 서술 문단(§8). enum·타입·규범 축 정의 없음.

### D-11c. (c) reducer 규약 — D-11의 하위 조건 (독립 Decision 아님)

1. **(c)는 독립 Decision으로 만들지 않는다.** D-11 (2)의 "종료/진행 정보의 내용·State 스키마 = HQ 도메인" 안에 포섭되는 **하위 조건**이다.
2. **배치 ((ii)) = HQ State 스키마**: 병렬 fan-out Node의 disjoint-key 분할과 accumulate/merge 의미론의 **선언**은 HQ의 State 스키마 설계 책임이다(§7 도메인 내용 / §13.3류 구조 불변식). 근거: E4 `domain/state.py`가 `REDUCER_KEYS`·`SECTION_KEYS`를 도메인 모듈에 선언하고 어댑터가 그것을 읽어 이행한다(V12).
3. **어댑터 의무 = 기계적**: HQ 스키마가 "이 키는 브랜치별 disjoint / 이 키는 accumulate"를 선언하면 어댑터는 그 선언을 결정론적으로 이행하고(순차 = 명시적 merge, 그래프 라이브러리 = reducer) 쓰기를 조용히 누락하거나 비결정적으로 교차시키지 않는다. 이는 A-IN(a) + Adapter Contract (b)가 이미 함의하는 범위이며 **새 계약 절이 아니다**.
4. **판정하지 않는 것**: (c)의 **계약화 여부 ((i))** 와 **HQ State 설계 구속 강화 ((iii))** 는 이 ADC가 판정하지 않는다 — `ADC-0020` §Q-D Defer와 `ADR-0009` §3의 "후속 판정" 상태를 약화하지 않는다. (c)는 문서화된 hazard + 배치 원칙으로만 존재하며 어떤 규범 효력도 갖지 않는다. 실제 HQ에 공유 키 병렬 쓰기 사례가 0건이므로(V6) 정식 계약 절 승격 필요는 관찰되지 않았다.

### D-9. 결정 9 / §14.1 — 별도 Track (이 ADC가 판정하지 않음)

1. v1 결정 9(`IWorkflowEngine` Port, `run(team, dispatch) -> WorkflowResult`)의 v2 공백은 Team 부재가 아니라 §14.1이 "Task 전달 책임"·"Engine 호출 책임"을 계약 범위 밖으로 두는 데서 온다(V5·V14, `ADC-0019` G3). 이는 이 ADC보다 상위의, 별도로 이미 Open인 Kernel Public Contract 확장 질문이다.
2. **이 ADC는 결정 9를 판정하지 않는다.** Workflow Adapter 입력의 구체 시그니처, 결과 반환 타입(`WorkflowResult` 대응), Public Port 정의는 §14.1 "Task 전달 책임" 트랙(별도 RFC → ADC → ADR)이 다룬다. 그 착수 여부·시점은 이 ADC가 정하지 않는다.

### D-Gate-A. Gate (A) 상태 갱신 — 부분 해소

`ADC-0021` §8 Gate (A)(= v1 `ADR-0007` 결정 2/5/9/11)의 상태는 이 ADC 이후 다음으로 갱신된다:

> **Gate (A) — 부분 해소**: 결정 2·5·11 = **Resolved (`ADC-0022`)**. 결정 9 = **§14.1 "Task 전달 책임" 트랙 pending** (별도 절차).

- §14 Kernel Public Contract 승격은 결정 9 해소 이후에만 가능하다(`ADC-0019` 조건 5) — Gate (A)의 "부분 해소"는 §14 승격을 열지 않는다.
- Gate **(B)**(재검토 조건 (c))와 Gate **(C)**(Reversibility v2 재현 — `ADR-0010` "부분 충족")는 이 ADC로 진전되지 않으며, 다음 단계(LangGraph 채택, Scoped 해제, 구현 착수)의 hard gate로 그대로 존속한다.

### Reason

- **§4.1 (D-0)** — 세 결정이 모두 "실행 단위"라는 미정의 용어로 귀결되므로, 1문단 설명 없이는 Resolution이 무엇에 대한 것인지 불명확하다. U-1(설명 용어) 채택 — §6 등재(U-2)는 사용자 지시 위반이고 `ADR-0009` §4 선례에 어긋난다.
- **§4.2 (D-2)** — §5의 Team/Division 배제 + HQ 코드 관찰(V6·V9)로 실행 단위 Lifecycle의 v2 부재가 확정된다. A-OUT 금지 절반은 이미 있고(V4), D-2는 긍정형(조건형)과 HQ Lifecycle 2층 분리를 더한다. 새 개념 없음.
- **§4.3 (D-5)** — `hqs/development/BOUNDARY.md`가 잔여 불변조건을 HQ 책임으로 이미 담는다(V11). D-5는 그 Kernel 쪽 확인 + 적용 방향(후속 계약이 HQ 내부 구조를 노출하면 위반)이다.
- **§4.4 (D-11)** — Development HQ의 `VerificationResult.status`가 HQ-level Public Contract(§14와 별개)로 이미 존재하고(V10), HQ마다 종료 어휘가 다르다(V7). Kernel enum은 불필요·충돌. S-a(서술) 채택 — S-b(규범 축)는 새 Kernel 개념이고 `stock_team.py`가 부분적으로만 뒷받침한다.
- **§4.5 (D-11c)** — E4가 (c) 배치 = HQ 스키마를 실측했다(V12). D-11c는 배치 질문에만 답하고 계약화·HQ 구속은 `ADC-0020`/`ADR-0009` 상태 그대로 유지한다. 독립 Decision 아님.
- **§4.6 (D-9·D-Gate-A)** — `RFC-0019` §5·`ADC-0019` G3의 2분할을 계승. 결정 9는 §14.1 트랙이므로 이 ADC에 넣으면 §14.1을 우회 확장한다.

### Decision Rationale

이 Decision은 `ADC-0019`/`ADC-0020`/`ADC-0021`/`ADR-0008`/`ADR-0009`/`ADR-0010`이 확정한 것을 **하나도 뒤집지 않는다** — §16.6 존재·A-IN·A-OUT·Reversibility·명칭·Adapter Contract (a)(b)(d)·(c) Defer·Gate (B)/(C)·조건 이월을 전부 전제로만 사용한다(§6). `ADC-0021` §8 Gate (A)의 "결정 2/5/9/11" 문면 중 결정 2·5·11만 해소하고 결정 9는 §14.1 트랙으로 분리하는 것은, `RFC-0019` §5와 `RFC-0021` §5·§7이 이미 수행한 "2·5·11 ↔ 9" 2분할을 계승한 것이지 이 ADC가 새로 판단하는 것이 아니다. `docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐)와 `ADC-0008`(Not Accepted)은 이 Decision으로 갱신·전복되지 않는다 — 이 ADC는 §16.6 A-IN이 전제하는 입력·Lifecycle·State의 v2 형태만 판정했다.

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6 전부 무변경** — 범위(A-IN)·명시적 제외(A-OUT)·§16.3~16.5 불가침·Reversibility 필수·조건 이월·미확정 항목.
2. **`ADC-0020` §6 Conditions 1~8 전부 무변경** — 특히 조건 3(v1 결정 2/5/9/11 미해결 Conditional — 이 ADC는 그중 2/5/11만 해소, 9는 유지), 조건 4(`IMPLEMENTATION_RULES.md` 금지 유지), 조건 5(§14 미승격), 조건 8(Adapter Contract 정식화 범위 = (a)(b)(d), (c) Defer — D-11c는 배치 질문에만 답하고 (c)를 계약 절로 승격하지 않는다).
3. **`ADC-0021` §D1~D4·§6·§7·§8 전부 무변경** — Sequential Reference 기본선·LangGraph 평가 대기·Gate (B)·(C)·Implementation Strategy 세부·Scoped 해제는 전부 별도 hard gate로 존속. §8 진입 순서에서 이 ADC는 "(A) 결정 2/5/9/11 해소" 항목을 **결정 2/5/11에 한해** 진전시키고, 결정 9·(B)·(C)는 그대로 남긴다.
4. **`ADR-0010` "부분 충족" 무변경** — Gate (C) E4의 잔여 한계 (i)~(iii)와 완전 discharge 미선언 상태 유지.
5. **Rule B 미충족 유지** — 이 ADC는 §5 Meta Architecture 정합 판정이지 Evidence 축적이 아니다(§1.4). 재검토 조건 (c)(Gate (B))는 다음 단계의 hard gate로 그대로 유효하다.
6. **§14 Kernel Public Contract 미승격 유지** — Public Port·Surface·Guarantee·Interface 신설 없음. §14.1 "Task 전달 책임"·"Engine 호출 책임" 계약 범위 밖 상태 그대로(D-9). Adapter Contract 부속 명세의 비-§14 지위(`ADC-0020` §Q-C) 계승.
7. **`IMPLEMENTATION_RULES.md` 금지 유지** — line 9(Workflow Parser) / line 13(Scheduler·우선순위·Workflow orchestration·Dynamic Routing·§6 넓은 Runtime) / line 14(Stage 재진입·조건부 Stage) / line 19(Event Bus). 이 ADC는 `ADC-0015`류 Scoped 부분 해제를 **하지 않는다**.
8. **`BASELINE.md`·`GLOSSARY.md`·`ADC.md` 문언 무변경** — §16.6 개정은 후속 ADR. 이 ADC는 §8 지침만 남긴다.
9. **§16.7 Workflow Kernel Module Defer 무변경** — D-0의 "실행 단위" 용어는 §16.6 본문 설명이지 §16.7이 Defer한 Workflow Kernel Module이 아니다.

---

## 7. Out of Scope (이 ADC의 자동 결과가 아닌 것 — 경계 재확인)

| 항목 | 상태 유지 근거 |
|---|---|
| **결정 9 / `IWorkflowEngine` Port / `WorkflowResult` 반환 타입 / 입력 시그니처** | D-9 — §14.1 "Task 전달 책임" 트랙. 별도 RFC → ADC → ADR |
| **§14 Kernel Public Contract 승격 / Public Port·Surface·Guarantee·Interface 정의** | `ADC-0019` §Q7·조건 5, §14.1, `ADC-0020` §Q-C. Gate (A) 부분 해소는 §14 승격을 열지 않음(D-Gate-A) |
| **(c)의 정식 Adapter Contract 절 승격 / HQ State 설계 구속 강화** | `ADC-0020` §Q-D Defer, `ADR-0009` §3. D-11c는 배치 ((ii))에만 답 |
| **"실행 단위"를 §6 Concept Model / 새 Kernel Domain·Layer·Component로 승격** | D-0, U-1. `ADR-0009` §4 선례 |
| **종료 disposition 축을 Kernel 규범으로 정의 (R11-b)** | §3.3 S-b Reject. D-11 (4) — Kernel은 축의 존재를 요구하지 않음 |
| **Gate (B) (`ADC-0019` 재검토 조건 (c)) / Gate (C) 완전 discharge** | `ADC-0021` §8, `ADR-0010`. 이 ADC로 진전 없음 |
| **LangGraph 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 / Implementation Strategy 세부** | `ADC-0019` §Q8, `ADC-0020` §7, `ADC-0021` §D2·§7 |
| **`IMPLEMENTATION_RULES.md` line 9/13/14/19 전면·Scoped 해제** | `ADC-0020` §6 조건 4, `ADR-0009` §6, `ADC-0021` §8 |
| **`docs/decisions/adc/ADC.md` ADC-02 / `ADC-0008` 재판단, §16.7 Defer 재판단** | `ADC-0019` §Q8, §16.6 "Workflow Module Defer와의 구분" |
| **`BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md` 문언 편집** | → 후속 ADR (§8) |
| **Rule B 충족 선언** | §1.4 — §5 정합 판정, Evidence 축적 아님 |
| **Team/Division을 §5 Meta Architecture에 재도입** | §5 배제를 전제로 그 위에서 재정의. D-5는 오히려 비의존을 강화 |
| **Production 코드 변경 (`core/`·`hqs/`·`dashboard/`)** | `IMPLEMENTATION_RULES.md`, `ADC-0019` 조건 5 |

---

## 8. 후속 ADR에서 반영할 사항 (Baseline 지침 — 이 ADC가 직접 반영하지 않음)

후속 ADR(Minor 예상)이 `BASELINE.md` §16.6과 `GLOSSARY.md`에 아래를 반영한다. §5·§6·§7·§14·§16.1~§16.5·§16.7, Adapter Contract (a)(b)(d) 문언, `IMPLEMENTATION_RULES.md`는 무변경(`ADR-0009` §6 선례).

1. **§16.6 본문에 "실행 단위" 설명 용어 1문단** — D-0 문언. "§16.6 A-IN 입력 경계 설명 / §6 Concept Model 미등재 / 새 Kernel Domain·Layer·Component 아님 / §16.7 Workflow Kernel Module 아님" 라벨.
2. **§16.6 A-OUT에 D-2 (3) 긍정형 불변조건 1문단** — 조건형("HQ 실행 단위가 자체 전이 로직을 가지면 Adapter는 호출만"), "현재 이 조건을 트리거하는 실행 단위 전이 로직은 어느 HQ에도 없다 — 미래 대비로 존속" 명시. + D-2 (2) "HQ Lifecycle State(§6)는 Adapter 개입 구간 밖, Jarvis OS 통제, Adapter 무접촉" 1문장.
3. **§16.6 A-IN 프레이밍에 D-5 (2)(3) 불변조건 1문장** — "입력('이미 구성된 실행 단위')은 HQ 내부 조직 구조와 독립적으로 성립하며 Adapter는 그것을 관측·의존하지 않는다. 후속 Adapter Contract·Public Port가 HQ 내부 구조를 입력 스키마에 노출하면 위반." — 확인용 서술이지 새 입력 계약 의무가 아님 명시.
4. **§16.6 A-IN(a)에 D-11 (2)(3) 서술 1문단** — "A-IN(a) State가 담는 정보 = 진행 정보(Adapter 생산·caller 소유 값) + 종료 disposition 정보(형식은 (b)+G-6, **내용·어휘는 HQ 도메인** — Kernel 미규정). Kernel은 종료 disposition 축의 존재를 요구하지 않는다. v1 `WorkflowStatus`/`WorkflowResult`는 v2에 도입하지 않는다." — 규범 축 정의가 아닌 서술임을 명문화.
5. **§16.6 기존 (c) 관련 문단에 D-11c 배치 1문장 추가** — "(c)의 배치 = HQ State 스키마 설계 책임. 어댑터 의무는 선언된 병합 의미론의 기계적·결정론적 이행. 계약화 여부·HQ 구속 강화는 `ADC-0020` §Q-D Defer·`ADR-0009` §3 그대로 — (c)는 hazard + 배치 원칙으로만, 규범 효력 없음." — 기존 "(c)는 이 부속 명세에 포함되지 않는다" 문단을 대체하지 않고 배치 답만 부기.
6. **§16.6 "미해결 상태로 유지되는 v2 공백 (Conditional)" 문단 갱신** — "결정 2·5·11 = Resolved(`ADC-0022`). 결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처) = §14.1 'Task 전달 책임' 트랙 pending. §14 승격은 결정 9 해소 이후에만 가능(`ADC-0019` 조건 5)." + `ADC-0021` §8 Gate (A) = "부분 해소"로 표기.
7. **`GLOSSARY.md` "Workflow Adapter" 절** — "실행 단위" 용어 1줄(§16.6 입력 경계 설명, §6 미등재) + "v1 `ADR-0007` 결정 2/5/11 = `ADC-0022`로 해소, 결정 9는 §14.1 트랙 pending" 1문장.
8. **Version**: v1.14 → v1.15 (Minor 예상), Architecture State = Frozen 유지.
9. **명시적 비변경 재확인**: §5·§6·§7·§14·§16.1~§16.5·§16.7, Adapter Contract (a)(b)(d) 문언, `IMPLEMENTATION_RULES.md` line 9/13/14/19, `docs/decisions/adc/ADC.md` ADC-02, `ADC-0008`, Gate (B)·(C).

---

## 9. Architecture / Governance Review

`RFC-0019`~`RFC-0021`, `ADC-0019`~`ADC-0021`, `ADR-0008`~`ADR-0010`, `BASELINE.md` v1.14, `hqs/investment/`·`hqs/development/` 코드, `IMPLEMENTATION_RULES.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`를 기준으로 이 ADC의 범위·Traceability·정합성을 검증한다.

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 선행 체인(`ADC-0019`/`ADC-0020`/`ADC-0021`/`ADR-0008`/`ADR-0009`/`ADR-0010`)이 확정한 것을 뒤집는가 | **아니오** — §16.6 존재·A-IN·A-OUT·Reversibility·명칭·Adapter Contract (a)(b)(d)·(c) Defer·Gate (B)/(C)·조건 이월을 전부 전제로만 사용(§6 Conditions 1~4·9) |
| `RFC-0021` §6 B-2·B-5·B-11을 판정하는가 | **예** — D-2·D-5·D-11이 각각 대응. `RFC-0021`이 후속 ADC로 위임한 판단을 완료(`RFC-0021` §10 Next Step 2·3·4에 답). `ADC-0019`가 `RFC-0019` §8을 판정한 것과 동일 관계 |
| `RFC-0021` §4 "가능한 해소 형태"를 자동 채택했는가 | **아니오** — §4 예시는 입력. D-2는 R2-c(§3.1 F-1), D-5는 R5-b(§4.3), D-11은 S-a(§3.3, S-b·S-c Reject)로 **독립 판정**. 각 Reason이 Evidence(V1~V16) 기반 |
| `ADC-0021` §8 Gate (A)(= 결정 2/5/9/11) 중 2·5·11만 해소하는 것이 선례에 어긋나는가 | **아니오** — `RFC-0019` §5·`RFC-0021` §5·§7이 이미 수행한 "2·5·11 ↔ 9" 2분할 계승(§4.6). Gate (A)를 "부분 해소"로 갱신(D-Gate-A), 결정 9는 §14.1 트랙 |
| `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준"(① 지금 결정 안 하면 상위 Architecture 진행 불가)을 만족하는가 | **①에 해당** — 결정 2·5·11 미해결이면 §16.6의 §14 승격·구현 착수가 `ADC-0019` 조건 5로 계속 차단된다. 이 판정이 그 차단의 일부(2·5·11)를 해소 |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다" | **준수** — 이 ADC는 §5 정합 판정이며 E4를 (c) 배치의 실측 근거로만 인용(§1.4·§4.5). LangGraph 채택·구현을 발생시키지 않음 |

### 9.2 경계 — Architecture / Contract 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임을 추가했는가 | **아니오** — §16.6 책임은 `ADC-0019`가 Accept 완료. 이 ADC는 그것이 전제하는 입력·Lifecycle·State의 v2 형태만 판정 |
| 새 Layer/Component/Concept을 추가했는가 | **아니오** — "실행 단위"는 §16.6 본문 설명 용어(D-0, U-1). §6 미등재. §16.7 Workflow Kernel Module 아님(§6 조건 9) |
| Contract Change가 있는가 | **없음** — Public Interface·Port·Guarantee 정의 없음. §14 무접촉(§6 조건 6). Adapter Contract (a)(b)(d) 문언 무변경. D-11c는 (c)를 계약 절로 승격하지 않음 |
| 새 Kernel State 축/enum/타입을 정의했는가 | **아니오** — D-11 (1) `WorkflowStatus`/`WorkflowResult` 미도입, D-11 (4) 종료 disposition 축의 존재를 요구하지 않음. S-b Reject |
| §16.6 A-IN/A-OUT 범위를 넓혔거나 좁혔는가 | **아니오** — D-2·D-5·D-11은 기존 A-IN/A-OUT 문언이 이미 전제·함의한 것의 서술적 확정. §8이 반영을 "문단 보강/1문장" 수준으로 한정 |
| 종료 disposition의 내용을 Kernel이 규정했는가 | **아니오** — D-11 (2) "내용·어휘는 §7상 HQ 도메인 책임". V10(Dev HQ `VerificationResult.status`)이 HQ 소유 실측 |
| 이 판정이 §14 승격·구현·Scoped 해제·LangGraph 채택 중 무엇이든 앞당기는가 | **아니오** — D-9(결정 9 pending), D-Gate-A(§14 승격은 결정 9 이후), §6 조건 3·5·7·§7. Gate (B)·(C)는 hard gate로 존속 |
| `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`를 이 ADC가 변경하는가 | **아니오** — §8이 후속 ADR 지침만. 이 ADC 파일 1건만 신규 작성 |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| 검증된 Resolution(R2-c/R5-b/R11-a)만 공식화, 새 Kernel concept/Contract 추가 금지 | **준수** — §5 D-2=R2-c, D-5=R5-b, D-11=R11-a(S-a). §9.2 전 항목 "아니오". S-b(새 규범 축) Reject |
| 결정 2·5·11과 (c)만 다루고, 결정 9/§14.1은 명시적으로 별도 Track | **준수** — D-9, D-Gate-A. §1.2·§7에 결정 9 전 항목 Out of Scope. F-0 Reject |
| "실행 단위"는 새 Kernel Domain이 아니라 §16.6 기존 입력 경계를 설명하는 용어로만 | **준수** — D-0, U-1(U-2 Reject). §8-1 반영 지침에 "§6 미등재 / 새 Domain·Layer·Component 아님 / §16.7 아님" 라벨 |
| R11-a의 disposition도 HQ Domain 책임임을 유지 | **준수** — D-11 (2) "내용·어휘는 §7상 HQ 도메인 책임, Kernel 미규정", D-11 (5) V10 근거. D-11 (4) Kernel은 축의 존재를 요구하지 않음 |
| (c)는 독립 Decision으로 만들지 말고 R11-a의 하위 조건으로만 | **준수** — D-11c (1) "독립 Decision으로 만들지 않는다", 배치 ((ii))에만 답, 계약화 ((i))·HQ 구속 ((iii))은 `ADC-0020`/`ADR-0009` 상태 유지 |
| 작성 후 Architecture/Governance Review만 수행 | **준수** — §9. BASELINE/ADR/코드 수정·commit·PR·merge 없음. 이 ADC 파일 1건만 신규 작성(미커밋) |

### 9.4 판정

**PASS (무조건).** 이 ADC는:

- `ADC-0019` 조건 1~6, `ADC-0020` §6 조건 1~8, `ADC-0021` §D1~D4·§6~§8, `ADR-0010` "부분 충족", Rule B 미충족, `IMPLEMENTATION_RULES.md` line 9/13/14/19 금지, Gate (B)·(C)를 **하나도 약화하지 않는다**(§6).
- 새 Architecture 책임·Layer·Component·Concept·Public Interface·Kernel State 축/enum/타입을 추가하지 않고, §14를 승격하지 않으며, `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`를 변경하지 않는다(§9.2).
- `RFC-0021` §6이 위임한 범위(B-2·B-5·B-11 + (c) 배치)만 판정하고, 결정 9·§14.1은 별도 Track으로 명시 분리한다(D-9).
- 구현·Contract 승격·`IMPLEMENTATION_RULES` Scoped 해제·LangGraph 채택을 선행하지 않으며, 그 전부를 hard gate로 유지한다(§7·D-Gate-A).

**Next Step**: ADR Required — §8 지침으로 §16.6·`GLOSSARY.md`에 D-0~D-Gate-A를 반영(Minor, v1.14 → v1.15, Frozen 유지). Commit/PR/Merge는 사용자 보고 후 별도 진행.

---

## 10. Traceability

| 문서 / 절 | ADC-0022와의 관계 | 정합성 |
|---|---|---|
| `RFC-0021` §6 (B-2·B-5·B-11) | 이 ADC가 판정하는 Boundary Question | D-2·D-5·D-11이 대응. `RFC-0021` §10 Next Step 2·3·4에 답. §4 "가능한 해소 형태"는 입력이지 결정 아님 |
| `RFC-0021` §7·§8 Non-goals (결정 9 제외, (c) 규범 내용 미확정) | 이 ADC도 그대로 유지 | D-9(결정 9 별도 Track), D-11c (4)((c) 규범 효력 없음) |
| `RFC-0019` §5 (v1 12개 결정 재해석, 2·5·11 ↔ 9 2분할) | D-2/D-5/D-11 ↔ D-9 분리의 근거 | 계승 — 이 ADC가 새로 판단하지 않음(§4.6) |
| `ADC-0019` §Q7·§Decision 조건 5·재검토 조건 (c) | 조건 이월의 해소 대상 | 결정 2·5·11 해소로 조건 5의 일부 충족. 결정 9·재검토 조건 (c)(Gate (B))는 유지(§6 조건 3·5) |
| `ADC-0020` §Q-C·§Q-D (c)·§4.3·§12 #1 | D-11·D-11c의 위임 근거 | (c) 배치 ((ii)) = HQ 스키마로 답. 계약화 ((i))·HQ 구속 ((iii))·(c) Defer 상태는 무변경 |
| `ADC-0020` §Q-E-2 (phase 경계 선언 주체 Defer) | 인접 미결 | 이 ADC가 다루지 않음 — D-11은 State 내용 축이지 phase 경계가 아님 |
| `ADR-0009` §3 ((c) Baseline 미반영, 결정 11 결합 후속 판정) | D-11c가 그 "후속 판정"의 배치 부분 수행 | (c)는 §16.6 본문에 배치 1문장만 부기(§8-5), 계약 절 승격 아님 |
| `ADC-0021` §8 Gate (A)/(B)/(C), 진입 순서 | D-Gate-A가 Gate (A)를 "부분 해소"로 갱신 | (A) 결정 2/5/11 Resolved, 결정 9·(B)·(C)는 hard gate 존속. §8 진입 순서 (A) 항목을 부분 진전 |
| `ADR-0010` (Gate (C) "부분 충족") | 무변경 | §6 조건 4 — 잔여 한계 (i)~(iii)·완전 discharge 미선언 유지 |
| `BASELINE.md` §5 (Meta Architecture) | D-0·D-2·D-5의 전제 | 무변경 — Team/Division 배제를 전제로 그 위에서 재정의. 재도입 없음 |
| `BASELINE.md` §6 (Concept Model, "HQ는 Lifecycle State를 가진다") / §7 (System Boundary) | D-2 (2)·D-5 (1)·D-11 (2)의 근거 | 무변경 — "실행 단위" §6 미등재(D-0). HQ Lifecycle·HQ 조직 구조 책임 배치 그대로 |
| `BASELINE.md` §14 / §14.1 | D-9 — 승격 차단, "Task 전달 책임" 계약 범위 밖 | 무변경, §14에 항목 추가 없음(§6 조건 6) |
| `BASELINE.md` §16.6 A-IN/A-OUT/A-IN(a)/Adapter Contract (a)(b)(d) | D-0~D-11c의 반영 대상(후속 ADR) | 문언 무변경 — §8이 "문단 보강/1문장" 지침만 |
| `BASELINE.md` §16.7 (Workflow Kernel Module Defer) | D-0의 "실행 단위"와 혼동 방지 | 무변경(§6 조건 9) — 설명 용어이지 Module 아님 |
| `BASELINE.md` §13.3 (Assembly 불변식) | D-11c의 배치 유비 | 인용만 — (c)를 §13.3류 구조 불변식으로 승격하지 않음(`ADC-0020` §4.3 유지) |
| `hqs/investment/teams/*.py`, `run.py`, `trader.py`, `checkpoint.py` | V6·V7·V8 | 관찰만 — 실행 단위 상태 머신 부재, 종료 어휘 = HQ 도메인, 진행 정보 = caller 소유 값 |
| `hqs/development/mvp/workflow*.py`, `execution_host.py`, `BASELINE.md` §Stage Data Contract, `BOUNDARY.md` | V9·V10·V11 | 관찰만 — Lifecycle 없음, `VerificationResult.status` = HQ-level Public Contract(§14와 별개), Division/Team 사용 여부 = HQ 책임 |
| `projects/workflow-adapter-reversibility-v2/domain/state.py` | V12 | 관찰만 — (c) 배치 = HQ 도메인 스키마 실측 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/19 | §6 조건 7·§7 | 해제 없음 |
| `docs/decisions/adc/ADC.md` ADC-02 / `docs/architecture/core/ADC-0008` | §7 | 갱신·전복 없음(§Decision Rationale) |

---

## 11. Self-Review

- `ADC-0019`/`ADC-0020`/`ADC-0021`이 확정하지 않은 것을 새로 결정했는가 — **결정 2·5·11의 v2 형태 + (c) 배치만**. 결정 9·§14 승격·LangGraph 채택·구현 착수·Scoped 해제·(c) 계약화·Gate (B)/(C)는 §7에 전부 Out of Scope.
- 검증된 Resolution(R2-c/R5-b/R11-a)만 공식화했는가 — **예**(§5 D-2/D-5/D-11). S-b(R11-b, 새 규범 축)는 §3.3에서 Reject.
- 새 Kernel Concept/Contract/Port/enum/타입/Layer/Component를 추가했는가 — **아니오**(§9.2 전 항목). "실행 단위"는 §16.6 본문 설명 용어이지 §6 항목·새 Domain이 아니다(D-0, §8-1).
- 결정 9 / §14.1을 별도 Track으로 명시했는가 — **예**(D-9, D-Gate-A, §1.2, §7). F-0(4개 동시 판정) Reject.
- R11-a의 disposition이 HQ Domain 책임임을 유지했는가 — **예**(D-11 (2)(5), V10). Kernel은 종료 disposition 축의 존재를 요구하지 않음(D-11 (4)).
- (c)를 독립 Decision으로 만들었는가 — **아니오**(D-11c (1)) — D-11의 하위 조건. 배치 ((ii))에만 답하고 (i)·(iii)는 `ADC-0020`/`ADR-0009` 상태 유지.
- `BASELINE.md`·`GLOSSARY.md`·`ADR`·`IMPLEMENTATION_RULES.md`·`ADC.md`·CLAUDE.md·Production 코드를 수정했는가 — **아니오**. 이 ADC 파일 1건만 신규 작성(미커밋).
- 새 실험/PoC를 수행했는가 — **아니오**(§1.3) — `main` 병합 Governance 문서 + v1 Evidence + 현재 HQ 코드 관찰만 인용.
- Rule B 충족을 선언했는가 — **아니오**(§1.4·§6 조건 5) — §5 Meta Architecture 정합 판정. 재검토 조건 (c)(Gate (B))는 다음 단계 hard gate로 존속.
- Architecture/Governance Review를 수행했는가 — **예**(§9), 판정 = PASS(무조건).
- Commit/PR/Merge를 했는가 — **아니오** — PASS 이후에도 사용자 보고를 먼저 한다.
