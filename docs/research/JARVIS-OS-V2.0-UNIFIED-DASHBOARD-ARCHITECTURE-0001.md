# JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001: Unified Dashboard / Multi-HQ Orchestration External Architecture Review

**문서 성격**: Architecture Review(Governance 판단 문서). **Dashboard를
구현하는 작업이 아니다.** Production Code·API·UI·Command
Contract·Orchestrator·Scheduler·Event Bus·Runtime·Conversation
Engine·Memory Engine·Kernel Component를 생성하지 않는다.
`BASELINE.md`·Dev HQ/Invest HQ Freeze 문서·Kernel Architecture·
Historical Evidence를 수정하지 않는다.

**핵심 질문**: Notion "🖥️ Jarvis OS — Unified Dashboard & Multi-HQ
Orchestration Notes"(Status: *Design Notes — Not yet Architecture
Freeze*)의 설계 방향이 현재 Repository 실제 상태(BASELINE v1.6,
Structure v1.0 Frozen, Dev HQ v2.0 Freeze, Investment HQ v2.0
Freeze, Kernel Boundary Observation, Phase 7 BLOCKED)와 어디까지
정합하는가.

---

## 1. Source / Design Context

**Design Source**: 사용자 첨부 PDF `Jarvis_OS__Unified_Dashboard__
MultiHQ_Orchestration_Notes.pdf`(Notion 문서 전사, 18절 + Reference
Principle). 문서 자신이 **"Design Notes — Not yet Architecture
Freeze"**, **"현재 공식 Architecture의 변경을 의미하지 않는다"**고
명시한다 — 이 Review는 그 구분(결정된 UX 방향 / 설계 후보 / 후보
Contract / 향후 검토 대상)을 그대로 유지하며, 문서의 어떤 항목도
읽는 시점에 자동으로 확정된 것으로 취급하지 않는다.

**Repository Evidence**: `docs/architecture/baseline/BASELINE.md`
(v1.6), `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`
(RFC-0006→ADC-0005/0006→ADR-0006→ADR-0007로 이미 승인된 Target
Architecture), `docs/architecture/core/DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`,
`docs/research/INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001.md`,
`docs/research/KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001.md`,
`docs/research/PHASE7-RESUME-REVIEW-0001.md`, `roadmap.md`,
`docs/decisions/rfc/RFC_CANDIDATES.md`, `docs/decisions/adc/ADC.md`.
실제 파일 시스템(`hqs/`, 저장소 루트) 직접 확인.

---

## 2. Existing Architecture

이번 Review에서 **이미 존재함을 실제로 확인한 것**만 기록한다
(추측 없음).

| 항목 | 상태 | 근거 |
|---|---|---|
| `dashboard/`(저장소 최상위, 사용자 외부 관리 Interface) | **Frozen**(RFC-0006 chain 승인) | `STRUCTURE-V1.0-FROZEN.md` L27, L94-100, L201 |
| Core Domain Model: `User → Dashboard → API/Events → Jarvis Kernel → HQ → ... → Provider/Tool/MCP` | **Frozen** | 동일 문서 L148-174 |
| `hqs/shared/`(여러 HQ 공통 Domain 정의) | **Frozen**(Target, 미구현) | 동일 문서 L87 |
| `core/{registry,runtime,scheduler,policy,communication,execution,events,context,memory,observability}/` | **Frozen as Target Boundary**, 실제 구현은 `execution/`(Accept)뿐 | `STRUCTURE-V1.0-FROZEN.md` L49-59, `BASELINE.md` §16 |
| Dashboard가 Core Logic을 실행하지 않고 API/Events로 Kernel과 연결 | **Frozen 원칙과 일치** | Core Domain Model, `BASELINE.md` §7 System Boundary |
| `hqs/development/`, `hqs/investment/` 물리 존재 | **실제 코드 존재** | `hqs/` 디렉터리 직접 확인 |
| `hqs/trading/`(Quant Trading HQ) | **존재하지 않음** | `hqs/` 디렉터리에 `development/`, `investment/` 2개만 존재 |
| Investment HQ Freeze 범위 | Team→Analysis→Bull/Bear→Trader→Final Report만 FREEZE, Portfolio/Risk/Execution DEFER | `INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001.md` §4·§5(main 반영 완료) |
| Command Contract(별도 API 형태) | **존재하지 않음** | `grep -rl "Command Contract"` 저장소 전체 0건 |
| `docs/architecture/{kernel,hq,dashboard}/`, `docs/specifications/{system,kernel,hq,dashboard,features}/` | **Frozen as Target**, 실제 디렉터리 미생성 | `STRUCTURE-V1.0-FROZEN.md` L108-134 |
| Dashboard/Orchestrator 관련 기존 RFC Candidate | **없음** | `RFC_CANDIDATES.md`, `ADC.md` grep 0건 |

---

## 3. Unified Dashboard UX

**"1안: 통합 Dashboard + 공통 Jarvis Chat"과 "Dashboard = Observe /
Jarvis Chat = Command / HQ = Execute / Evidence = Verify"** 원칙은
BASELINE §7 System Boundary("Jarvis OS 책임: Task/Event 전달, Engine
호출 표준 인터페이스, Context/Artifact 저장 인프라" vs "HQ 책임:
Workflow 정의, 내부 조직 구조, 도메인 규칙")와 **충돌하지 않는다** —
오히려 Structure v1.0의 Core Domain Model(`User → Dashboard → API/
Events → Kernel → HQ`)이 이미 같은 방향(Dashboard는 관찰/명령 계층,
HQ는 실행 계층)을 전제하고 있다.

**판정**: 이 UX 방향 자체는 **비교·재검토 대상이 아니며**(작업 지시
§3), Architecture 관점에서 **EXISTING 원칙과 정합**한다. 단, 이는
"이미 구현됐다"는 뜻이 아니라 "기존 승인된 Frozen 원칙과 방향이
어긋나지 않는다"는 뜻이다 — `dashboard/` 코드 자체는 아직 존재하지
않는다(§2).

---

## 4. Global Dashboard Responsibility

| Notion 제안 | Structure v1.0 Frozen 대조 | 판정 |
|---|---|---|
| `dashboard/`가 최상위 디렉터리, Global UI/Shell 담당 | 정확히 일치(`STRUCTURE-V1.0-FROZEN.md` L94) | **EXISTING** |
| `dashboard/`가 HQ 내부 DB/Core Logic에 직접 접근하지 않고 Contract로 상태 소비 | Core Domain Model과 §7 System Boundary에 이미 내포 | **EXISTING(원칙)** |
| `dashboard/{layout,navigation,command-center,overview,tasks,events,alerts,usage}/`(Notion 제안 하위 구조) | Frozen 하위 구조는 `{web,api,events,components,views,auth}/`로 **다르다** | **CANDIDATE** — 두 구조가 불일치하므로 어느 쪽도 자동으로 맞다고 볼 수 없다. `STRUCTURE-V1.0-FROZEN.md` §Deferred Decisions가 "Dashboard의 실제 구현 구조"를 이미 명시적으로 후속 결정 대상으로 남겨뒀다(L215) — Notion 제안은 그 후속 결정의 **입력 후보**로는 유효하나, 이 Review가 두 구조 중 하나를 채택하지 않는다 |
| Global Dashboard = "어떻게 보여줄 것인가"(Shell 조합) | Structure v1.0 Frozen 원칙과 일치 | **EXISTING(원칙)** |

---

## 5. HQ Dashboard Responsibility

| Notion 제안 | Repository 대조 | 판정 |
|---|---|---|
| `hqs/{development,investment,trading}/dashboard/` 하위 디렉터리 | `STRUCTURE-V1.0-FROZEN.md`의 `hqs/development/`(L62-77)·`hqs/investment/`(L79-85) 목록에 `dashboard/` 항목 **없음** | **CANDIDATE** — Frozen Structure에 없는 새 하위 디렉터리 유형이므로, "이미 확정된 구조"로 표현하면 안 된다. 단, Structure v1.0 §Freeze Rule("단순한 구현 세부사항 변경은 Structure v1.0의 변경으로 간주하지 않는다")과 이미 Deferred로 남겨둔 "Dashboard의 실제 구현 구조"(§4) 범위 안에 있어 **Boundary 충돌은 아니다** — RFC 필요성은 §11에서 판단 |
| HQ Dashboard = "무엇을 보여줄 것인가"(Domain View) | §7 HQ 책임("Workflow 정의, 도메인 특화 비즈니스 규칙")과 정합 | **EXISTING(원칙)** |
| Dev HQ 표시 정보(Status/Phase/Current Task/Progress/Agent 상태/Latest Event) | Dev HQ v2.0 Freeze 범위(Stage 01~05, Agent Definition 4개, Checkpoint 유사 메커니즘)와 데이터 원천이 **개념적으로 존재** | **CANDIDATE**(표시 UI는 없음, 그러나 근거가 될 Production 상태 자체는 존재) |
| Invest HQ 표시 정보(Total Portfolio/Daily P&L/Daily Return/Market Index) | **Portfolio 자체가 DEFER**(`INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001.md` §5) — Production 코드에 Portfolio 개념이 없음 | **NOT YET JUSTIFIED** — Freeze 범위(Team→Trader→Final Report)에 없는 데이터를 표시 대상으로 적으면 존재하지 않는 기능을 Production처럼 표현하는 것(작업 지시 §4 "Portfolio/Execution을 Production 기능처럼 표현하지 않는다"에 정확히 해당) |
| Trading HQ 표시 정보(Engine Status/Strategy/Risk/Positions) | Trading HQ 자체가 **미착수**(§2) | **FUTURE / NOT YET JUSTIFIED** |

---

## 6. Dashboard Contract

`HQDashboardSnapshot`(identity/status/tasks/alerts/latest_event/
metrics/updated_at) 필드별 판정:

| 필드 | 근거 데이터 존재 여부 | 판정 |
|---|---|---|
| `identity`, `status`, `updated_at` | HQ 자체의 존재·실행 여부는 이미 관찰 가능(Freeze 문서들이 각 HQ 상태를 텍스트로 기록) | **CONTRACT CANDIDATE** |
| `tasks`, `alerts`, `latest_event` | 현재 Checkpoint(Investment)·Stage 진행(Dev)에서 유사 정보가 파일로 존재하나, 이를 외부에 노출하는 Contract/API는 없음 | **CONTRACT CANDIDATE** |
| `metrics`(Dev: phase/current_task/progress/active_agents/validation_status) | Dev HQ v2.0 Production 상태와 대응 가능 | **CONTRACT CANDIDATE** |
| `metrics`(Invest: total_portfolio/daily_pnl/allocation) | Portfolio 개념 자체가 DEFER(§5) | **NOT YET JUSTIFIED** |
| `metrics`(Trading: strategy/engine_status/positions/risk_status) | Trading HQ 미착수 | **NOT YET JUSTIFIED** |
| Schema 전체를 공식 Contract로 Freeze | Notion 문서 자신이 "아직 공식 Schema로 Freeze하지 않았다"고 명시 | **CONTRACT CANDIDATE(Notion 원문과 동일 판정 유지)** — 이 Review가 승격하지 않는다 |

**결과**: `HQDashboardSnapshot`은 전체가 하나의 판정으로 묶이지
않는다 — **공통 骨格(identity/status/tasks/alerts/latest_event/
updated_at)은 CONTRACT CANDIDATE, HQ별 `metrics`는 그 HQ의 실제
Freeze 범위 안에 있는 필드만 CANDIDATE, 범위 밖(Portfolio/Trading
전체)은 NOT YET JUSTIFIED**로 분리 판정한다.

---

## 7. Command Contract

Notion §12의 "Dashboard Contract(상태 조회) ↔ Command Contract(작업
요청)" 분리 원칙은 BASELINE §7("Jarvis OS: Task/Event의 전달")과
개념적으로 정합하지만, **현재 Repository에 Command Contract에
해당하는 API/스펙이 전혀 없다**(§2 확인) — Dev HQ는 `cli.py`를 통한
직접 스크립트 실행, Investment HQ는 `run.py`를 통한 argv 기반 직접
실행이며, 이 둘 다 "Command Contract"라는 별도 계층을 거치지 않는다.

**판정**: **CANDIDATE**. 원칙(분리해야 한다는 것)은 §7과 충돌하지
않으나, 구현 형태(어떤 필드/프로토콜)는 전혀 정의된 바 없다 —
"이미 있다"고 표현하면 안 된다.

---

## 8. Multi-HQ Conversation / Task Model

| Notion 제안 | Repository 대조 | 판정 |
|---|---|---|
| Global Conversation → Orchestrator → Dev/Invest/Trading Task → Context | **존재하지 않음** — 현재 각 HQ는 독립 CLI/스크립트 실행이며, 하나의 대화에서 여러 HQ에 동시 지시하는 경로가 없다 | **FUTURE** |
| `Conversation ID → Task ID → {HQ ID, Agent ID, Context ID}` 개념 모델 | 대응 코드 없음. Dev HQ의 `workflow.py`(Stage 1→5 하드코딩)와 Investment HQ의 `run.py`(Team 1개 단발)는 각각 자기 HQ 안에서만 순차 실행하며, Task ID/Context ID를 명시적 객체로 다루지 않는다 | **FUTURE** |
| HQ별 Context/Memory/Tool/Permission 격리 | BASELINE §7·`hqs/development/BOUNDARY.md`가 이미 "HQ 내부 조직 구조는 Jarvis OS가 모른다"는 격리 원칙을 확정 — **원칙은 EXISTING**, 그러나 이를 강제하는 Kernel Component(Context Isolation)는 없음 | **원칙 EXISTING / 구현 FUTURE** |
| Task Scheduler / Dependency Resolver / Worker Manager / Context Isolation / Result Aggregator | `core/{scheduler,context}/`가 Structure v1.0 Target Boundary로 이미 이름만 예약돼 있음(§2) — 실제 설계는 §10 Out of Scope, Kernel Module Defer 상태(Workflow Defer) | **FUTURE(Boundary만 Frozen, Component 미설계)** |
| Event Bus / Runtime / Conversation Engine / Memory Engine | Runtime은 ADC-02로 Open(존폐 미결), Event Bus/Memory는 Kernel Module Defer(`BASELINE.md` §16.3), Conversation Engine은 저장소 어디에도 개념조차 없음 | **FUTURE** |
| 병렬 실행(독립 Task 병렬, 의존 Task 순차, 혼합 Workflow) | Dev HQ(Wave 병렬)·Investment HQ(Wave 병렬) 양쪽 모두 **HQ 내부**에서 이미 `ThreadPoolExecutor` 기반 병렬 실행을 실증(Phase 5/6 Kernel Candidate, `KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001.md`가 재확인) — 그러나 이는 **HQ 내부 Wave 병렬화**이지 Notion이 제안하는 **Multi-HQ 간 병렬화**(Task A→Dev, Task B→Invest 동시 실행)와 범위가 다르다 | HQ 내부 병렬화: **EXISTING**(단, Phase 7 DEFER로 Kernel 승격은 안 됨). Multi-HQ 간 병렬화: **FUTURE**, 실제 사례 0건 |

---

## 9. Architecture Boundary Matrix

| Boundary | 책임 | 현재 상태 |
|---|---|---|
| `dashboard/` ↔ HQ | Global UI ↔ HQ View | **CANDIDATE** — 최상위 `dashboard/` 위치는 EXISTING(Frozen), 내부 세부 구조·HQ와의 실제 연결 방식은 미정 |
| `<hq>/dashboard/` ↔ HQ Core | Domain UI ↔ Domain Logic | **CANDIDATE** — Frozen Structure에 없는 신규 하위 디렉터리(§5) |
| `dashboard/command-center` ↔ Kernel | User Command ↔ Orchestration | **FUTURE** — Command Contract도 Orchestrator도 모두 존재하지 않음(§7·§8) |
| Kernel ↔ HQ | Task Execution ↔ Domain Capability | **EXISTING(원칙, BASELINE §7)** / **FUTURE(구현)** — 원칙은 Frozen, `core/` 대부분 미구현 |
| `shared/ui` ↔ HQ Dashboard | Common UI ↔ Domain UI | **CANDIDATE with naming conflict** — Notion은 저장소 **최상위** `shared/{ui,types,contracts}`를 제안하나, Structure v1.0은 이미 `hqs/shared/`(HQ 공통 **Domain** 정의, UI 아님)를 Frozen으로 예약해뒀다(§2). 같은 "shared"라는 이름이 서로 다른 두 위치·목적을 가리킬 위험이 있다 — 이번 Review는 어느 쪽도 확정하지 않고 **Open Issue**로 기록한다(§13) |
| Usage(Claude Budget) ↔ Task/Agent | Cost Tracking ↔ Execution | **FUTURE** — 저장소에 Usage/Budget 추적 코드가 전혀 없음(확인, grep 0건) |

핵심 원칙("Dashboard가 Core Logic을 실행하지 않는다")은 현재
어디서도 위반되지 않는다 — 애초에 Dashboard 코드 자체가 없기 때문에
검증 대상이 존재하지 않는다.

---

## 10. Kernel Boundary Impact

**질문**: "Unified Dashboard/Global Command/Multi-HQ Task 구조가
현재 Kernel Boundary 밖에서 정의 가능한가?"

- Notion이 "향후 검토"로 명시한 Orchestrator/Task Scheduler/
  Dependency Resolver/Worker Manager/Event Bus/Runtime/Conversation
  Engine/Memory Engine은 전부 `core/`의 기존 Target Boundary(§2)
  안에 있는 이름들이다 — 즉 **이 구조들은 Kernel Boundary "밖"에서
  정의될 수 없다**. Structure v1.0이 이미 이들의 자리를 `core/`
  안에 예약해뒀기 때문에, Dashboard가 이 책임을 자체적으로
  구현하면 그 자체로 Kernel Boundary를 침범하게 된다.
- 그러나 **지금 이 구조들을 설계·구현할 근거(Evidence)는 없다** —
  `KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001.md`(직전 세션)가
  Dev HQ v2.0 + Investment HQ 실제 코드를 전수 대조해 **NO NEW
  KERNEL RESPONSIBILITY**를 확정했고, 이번 Notion 설계 노트는 그
  이후에 나온 **Design Note일 뿐 Production Evidence가 아니다**
  (실제 실행 0건, Dogfooding 0건) — Kernel Extraction 5개 기준
  (§Extraction Candidate 판정 기준 1: "실제 Production/Validation
  Evidence가 존재한다")을 충족하지 못한다.
- **Phase 7은 이번 Review로 재개되지 않는다** — `PHASE7-RESUME-REVIEW-0001.md`가
  확정한 6개 재개 근거(Engine 수 ≥2 등) 중 어느 것도 이 설계 노트로
  충족되지 않는다.
- Task Scheduler/Dependency Resolver/Worker Manager/Event Bus/
  Runtime/Memory Engine/Kernel Dispatch Component는 이번 작업에서
  **생성하지 않는다**(작업 지시 §11 그대로 준수).

**결론**: Multi-HQ Orchestration은 개념적으로 Kernel 책임 후보
자리에 이미 예약돼 있지만(Structure v1.0), 실제 설계 착수는 Phase 7
HOLD와 무관하게 **Evidence 부족으로 시기상조**다.

---

## 11. Governance Impact

| Notion 항목 | 판정 |
|---|---|
| Unified Dashboard + Global Jarvis Chat UX 방향 | **A. EXISTING ARCHITECTURE** — Structure v1.0 Core Domain Model 해석 범위, Governance 변경 불필요 |
| 최상위 `dashboard/` 디렉터리 존재 | **A. EXISTING ARCHITECTURE** — 이미 Frozen |
| `dashboard/` 내부 세부 구조(Notion 제안 vs Frozen 제안 불일치) | **A. EXISTING ARCHITECTURE의 해석 범위** — Structure v1.0이 "Dashboard의 실제 구현 구조"를 이미 명시적 후속 결정 대상으로 Defer해뒀으므로, 이 안에서 조정하는 것은 새 Governance Decision이 필요한 영역이 아니다(신규 Layer/Concept 추가 아님) |
| `hqs/<hq>/dashboard/` 신규 하위 디렉터리 | **B. ARCHITECTURE EXTENSION CANDIDATE**(약함) — Frozen 목록에 없는 항목을 각 HQ에 추가하는 것이므로, RFC Candidate로만 기록(§12). 실제 구현 착수 시점에 정식 판단 |
| `shared/`(root) vs `hqs/shared/` 명칭 충돌 | **C. ARCHITECTURE CONFLICT 후보** — 직접 수정하지 않고 Governance Review 대상으로만 기록. RFC 작성은 하지 않는다(실제 구현 시도가 없어 충돌이 아직 발생하지 않았음) |
| Command Contract 도입 | **B. ARCHITECTURE EXTENSION CANDIDATE** — 새 Contract이므로 RFC Candidate로 기록 |
| `HQDashboardSnapshot`(공통 骨格) | **B. ARCHITECTURE EXTENSION CANDIDATE** — RFC Candidate로 기록. HQ별 `metrics`는 각 HQ Freeze 범위 안에서만 후속 판단(§6) |
| Orchestrator/Task Scheduler/Event Bus/Runtime/Memory Engine | **A. EXISTING(Boundary만)**, 설계는 **여전히 §10 Out of Scope** — Governance 변경 불필요(이미 Frozen 상태 그대로), 새 RFC 불필요(Evidence 없음, §10) |
| Quant Trading HQ 신규 HQ 추가 | **A. EXISTING ARCHITECTURE** — `roadmap.md` Phase 13이 이미 "신규 HQ 추가 자체는 RFC 대상이 아니다"(Investment HQ 선례)로 확정. 단 실제 착수 시점은 별도 판단 |
| Claude Usage/Budget을 Global Resource로 취급 | **B. ARCHITECTURE EXTENSION CANDIDATE**(약함) — 현재 Usage 추적 시스템 자체가 없어(§9) Contract Candidate 이전 단계, RFC Candidate로만 기록 |

**필요성이 명확하지 않으면 새 RFC/ADC/ADR을 만들지 않는다는 원칙에
따라, 이번 Review는 RFC Candidate로만 기록하고 실제 RFC 문서를
작성하지 않는다**(§12).

---

## 12. Implementation Boundary

**Evidence 기준 최소 구현 가능 범위**: 이번 Review에서 확인한
Evidence(설계 노트 1건, 실제 실행 0건)만으로는 **Phase 1(Global
Dashboard Shell)조차 착수 근거가 부족하다.** Notion 원문 §18 "다음
작업 후보"가 이미 Dashboard 세부 구현이 아니라 다음을 우선순위로
제시했고, 이 Review는 그 순서를 뒤집을 근거를 찾지 못했다:

1. Quant Trading HQ의 Freqtrade/LEAN Reverse Engineering
2. Global Command → Task → HQ Context → Agent/Engine Architecture 검증
3. Parallel Execution/Multi-Agent Orchestration Architecture 검증
4. HQ Context/Memory/Tool Isolation 검증
5. Dashboard Contract를 공식 Architecture로 승격할지 결정

작업 지시 §16이 제안한 Phase 1~5 순서(Global Dashboard Shell →
HQ Navigation → Snapshot 소비 → Global Chat → Command/Task
Integration)는 **자동으로 채택하지 않는다** — Notion 원문 §17
("Dashboard 자체의 추가 논의는 일단 중단, 실제 책임 경계 검증이
우선")과 이번 Review의 Evidence Gap(§6·§7·§8 대부분 FUTURE/
CANDIDATE)이 같은 결론을 가리킨다: **지금은 Dashboard 코드가 아니라
그 밑에서 Dashboard가 소비할 실제 HQ 상태·Command 경로 자체가
없다.**

**RFC Candidate로만 기록**(§11의 B 항목 재정리, RFC 작성 안 함):

1. `hqs/<hq>/dashboard/` 하위 디렉터리를 Structure v1.0에 추가 확장할지
2. Command Contract의 형태(필드/프로토콜)
3. `HQDashboardSnapshot` 공통 骨格 Schema
4. `shared/`(root) vs `hqs/shared/`의 관계 정리(Conflict 후보 해소)
5. Claude Usage/Budget Global Resource 구조

---

## 13. Final Recommendation

**Dashboard/Orchestrator를 지금 구현하지 않는다.** Notion 설계
노트는 기존 Frozen Architecture(Structure v1.0의 최상위 `dashboard/`,
Core Domain Model, System Boundary)와 **충돌하지 않으며**, UX
방향(Unified Dashboard + Global Jarvis Chat, Dashboard=Observe/
Chat=Command/HQ=Execute/Evidence=Verify)도 그대로 유효하다. 그러나
문서 자신이 인정하듯 핵심 Contract·Component(`HQDashboardSnapshot`,
Command Contract, Orchestrator, Context Isolation)는 **전부
미확정**이고, 이를 뒷받침할 Repository Evidence(실제 실행, Dogfooding)
는 이번 Review 시점에 **0건**이다.

**Open Issue만 기록하고 구현으로 넘어가지 않는다**:
- `shared/`(root) vs `hqs/shared/`
- `hqs/<hq>/dashboard/`가 Structure v1.0 확장 대상인지
- Invest HQ/Trading HQ Dashboard Metrics 대부분이 아직 근거
  데이터(Portfolio, Trading HQ 자체)가 없음

**남은 의도적 미구현 영역**: Dashboard UI/API 전체, Command
Contract, Orchestrator/Scheduler/Event Bus/Runtime/Memory Engine,
Quant Trading HQ 전체, Investment HQ의 Portfolio/Risk/Execution
(기존 Freeze 결정 그대로 유지).

---

## Self Review

- Production Code/UI/API를 구현했는가 — **아니오**.
- Orchestrator/Scheduler/Event Bus/Runtime/Conversation Engine/
  Memory Engine/Kernel Component를 생성했는가 — **아니오**.
- `BASELINE.md`/Dev HQ·Invest HQ Freeze 문서/Kernel Architecture를
  수정했는가 — **아니오**.
- 신규 RFC/ADC/ADR을 작성했는가 — **아니오**(RFC Candidate만 기록).
- Notion의 결정된 UX 방향을 재비교·변경했는가 — **아니오**(§3에서
  그대로 유지, Architecture 충돌 여부만 확인).
- 아직 존재하지 않는 Portfolio/Trading HQ 기능을 Production처럼
  서술했는가 — **아니오**(§5·§6에서 NOT YET JUSTIFIED로 명시 분리).
- Phase 7을 재개했는가 — **아니오**(§10).
- Historical Evidence를 소급 수정했는가 — **아니오**.

---

## 최종 보고

1. **Notion 설계 노트 핵심 방향**: Unified Dashboard + Global Jarvis
   Chat(1안 확정), Dashboard=Observe/Chat=Command/HQ=Execute/
   Evidence=Verify, HQ별 Execution Context 격리, Quant Trading HQ를
   독립 HQ로 신설(자동매매 중심, Freqtrade/LEAN Reference).
2. **Repository에서 실제로 확인된 내용**: 최상위 `dashboard/`와 Core
   Domain Model은 이미 Structure v1.0으로 Frozen. `hqs/`에는
   development/investment 2개만 존재(trading 없음). Command
   Contract·Orchestrator·`HQDashboardSnapshot`은 저장소 어디에도
   없음(grep 0건).
3. **Global Dashboard 책임**: 최상위 위치는 EXISTING(Frozen), 내부
   세부 구조는 CANDIDATE(Notion 제안이 Frozen 하위 구조와 불일치).
4. **HQ Dashboard 책임**: 원칙(Domain View 소유)은 EXISTING, 실제
   `<hq>/dashboard/` 디렉터리는 CANDIDATE. Invest/Trading HQ
   Metrics 상당수는 근거 데이터 자체가 없어 NOT YET JUSTIFIED.
5. **Dashboard Contract 상태**: `HQDashboardSnapshot` 공통 骨格은
   CONTRACT CANDIDATE, HQ별 metrics는 각 HQ Freeze 범위 안에서만
   부분 CANDIDATE.
6. **Command Contract 상태**: CANDIDATE — 원칙은 정합하나 구현 0건.
7. **Multi-HQ Orchestration 상태**: 전부 FUTURE — Global
   Conversation/Task/Context 모델, Orchestrator, 병렬 실행(Multi-HQ
   간)은 실제 코드 0건. HQ 내부 Wave 병렬화는 이미 EXISTING이지만
   범위가 다름.
8. **Kernel 영향**: Notion이 제안한 Component들은 이미 `core/`
   Target Boundary 안에 예약돼 있어 Boundary 밖 정의는 불가능하지만,
   설계 착수 Evidence가 없어 Phase 7 HOLD를 재개시키지 않는다 —
   NO NEW KERNEL RESPONSIBILITY 판정 유지.
9. **Governance 영향**: 신규 RFC/ADC/ADR 없음. RFC Candidate 5건만
   기록(§12).
10. **실제 구현 가능한 최소 범위**: 없음(현재 Evidence 기준) —
    Notion 원문 §18의 우선순위(Quant Trading HQ Reverse Engineering,
    Command→Task→Context Architecture 검증, HQ Isolation 검증)가
    Dashboard 구현보다 선행돼야 한다는 결론이 이 Review로 재확인됨.
11. **최종 Recommendation**: Dashboard/Orchestrator 구현 시작 금지,
    설계 노트를 Architecture Candidate 저장소(RFC Candidate 5건)로만
    보존.
12. **남은 Open Issues**: `shared/`(root) vs `hqs/shared/` 명칭 충돌,
    `hqs/<hq>/dashboard/` Structure v1.0 확장 여부, Command
    Contract·`HQDashboardSnapshot` 형태 미정.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 미실행(코드 변경 없어 불필요)
E2E: 미실행
RFC: 없음(신규 작성 안 함, RFC Candidate 5건만 문서에 기록 — §12)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 문서 커밋 예정)
Branch: `claude/unified-dashboard-architecture-review`
Next Implementation Candidate: 없음 — Notion §18 우선순위(Quant
Trading HQ Reference 조사, Global Command→Task→Context Architecture
검증, HQ Context/Memory/Tool Isolation 검증)가 Dashboard 구현보다
선행 필요
