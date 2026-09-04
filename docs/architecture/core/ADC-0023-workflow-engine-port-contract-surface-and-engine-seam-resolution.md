# ADC-0023: v1 `ADR-0007` 결정 9의 잔여 계약 표면 — Workflow Adapter 호출 seam·입력 시그니처·결과 반환 타입의 v2 Resolution (RFC-0022 후속, Gate (A) 완전 해소)

**Status**: Decided — ADR Required (예상 `ADR-0012`). Architecture/Governance Review PASS(§9, 최종 정합성 재점검 포함 — `RFC-0022`·`ADC-0022`·`ADR-0011`·`ADC-0019`·`ADC-0021` 대조 결과 신규·변경 Architecture 결정 없음). `BASELINE.md`·`GLOSSARY.md`·ADR 미착수. feature branch commit + PR 생성 — main 직접 커밋·Merge 금지, Merge는 사용자 승인 대기.
**Author**: Claude Code
**선행 체인**: `RFC-0019`→`ADC-0019`→`ADR-0008`(v1.12 §16.6 존재 Accept·Scoped·Conditional) → `RFC-0020`→`ADC-0020`→`ADR-0009`(v1.13 명칭 = **Workflow Adapter** + Adapter Contract (a)(b)(d)) → `ADC-0021`(구현 전략 프레이밍, §8이 미해결 4공백을 Gate (A)로 명명) → `ADR-0010`(v1.14 Gate (C) E4 "부분 충족") → `RFC-0021`→`ADC-0022`→`ADR-0011`(v1.15 결정 **2·5·11** Resolved, Gate (A) "부분 해소")
**RFC pairing**: `RFC-0022-workflow-engine-port-contract-surface-and-engine-seam-boundary.md` (Proposed) — §6이 F-9a~F-9f Boundary Question을 개설. 이 ADC가 그 여섯 facet을 판정한다(`ADC-0022`가 `RFC-0021` §6 B-2·B-5·B-11을 판정한 것과 동일 관계).
**대상**: `ADC-0021` §8 Gate **(A)** 중 `ADC-0022` §D-9가 "별도 Track"으로 남긴 **v1 `ADR-0007` 결정 9**(`IWorkflowEngine` Port 존재 / 입력 시그니처 / `WorkflowResult` 반환 타입)의 잔여 계약 표면.

> 이 ADC는 **새로운 Kernel Concept·Layer·Component·Public Contract·Port·enum·타입을 추가하지 않는다.** 결정 9의 잔여 계약 표면 세 조각(Port 존재·입력 시그니처·결과 반환 타입)을 F-9a~F-9f로 판정하되, 각 판정은 **BASELINE v1.15 문언과 현재 `main` 코드 Evidence의 서술적 확정**이며 새 요구사항을 만들지 않는다. §14 Kernel Public Contract를 승격하지 않고(그것은 §14 scope의 Context→Execution 확장이라는 상위 절차이며 이 ADC 밖), Gate (B)·(C)를 진전시키지 않으며, LangGraph를 채택하지 않고, 어댑터를 구현하지 않으며, `IMPLEMENTATION_RULES.md`를 해제하지 않고, `BASELINE.md`/`GLOSSARY.md` 문언을 편집하지 않는다. 실제 §16.6/`GLOSSARY.md` 반영은 후속 ADR이 수행한다(§8). §14에 항목을 추가해야 한다고 판정되더라도, 이 ADC는 **결정만 기록**하고 문안·BASELINE 변경은 별도 ADR로 분리한다.

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (F-9b 우선, 그다음 F-9a·c·d·e·f)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D-9b** | **F-9b (우선)** — v1 `IWorkflowEngine`의 "Engine"(Workflow 그래프 실행 조립·진행)과 v2 §16.2 "Engine Adapter"(Model/LLM Provider 호출)가 **동일 seam인지 별도 seam인지** 결정. 결정 9가 하나의 질문인지 둘로 쪼개지는지 | `RFC-0022` §2.3·§3·§4.1, `BASELINE.md` §16.2·§16.6 명칭 문단, `RFC-0019` §3, `ADC-0019` G2, `ADC-0020` §Q-B, `hqs/` 코드 |
| **D-9a** | **F-9a** — §16.6 Reversibility가 요구하는 "구현체 교체 시 Kernel·HQ 무수정" seam의 **§14 지위** (승격 / 비-§14 존속 / HQ 위임) | `RFC-0022` §4.1, `BASELINE.md` §14.1·§14.5·§16.6 Adapter Contract·Reversibility, `ADC-0020` §Q-C, `ADR-0009` §Decision 4 |
| **D-9c** | **F-9c** — 실행 메커니즘 호출의 **입력 시그니처**가 Kernel 표준 형태인지 영구 HQ별인지. §14.1 #1 "Task 전달 책임"의 처리 | `RFC-0022` §4.2, `ADC-0022` §D-5, `BASELINE.md` §14.1·§14.6 N-2, `RFC-0002` §15-1, `hqs/` 진입 시그니처 |
| **D-9d** | **F-9d** — 실행 **결과 반환 타입** (Kernel envelope / caller-owned Checkpoint 값 / HQ 타입) | `RFC-0022` §4.3, `ADC-0022` §D-11, `BASELINE.md` §16.6 A-IN(a)·Adapter Contract (a)(b)·§14.3 G-6, `hqs/development/stages/contracts.py` |
| **D-9e** | **F-9e** — §7 "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)" ↔ §14.1 "Engine 호출 책임 = 계약 범위 밖"의 **층위 정합성**. `ADC-0010` Not Accepted 제약 | `RFC-0022` §4.4, `BASELINE.md` §7·§11·§14·§14.1, `ADC-0010` |
| **D-9f** | **F-9f** — 결정 9 "해소"의 **최소 조건**과 이 ADC가 그것을 충족하는지 | `RFC-0022` §4.4, `ADC-0019` §Decision 조건 5, `ADC-0021` §8, `ADC-0022` §D-Gate-A |
| **D-Gate-A** | Gate (A) 상태를 "부분 해소" → **"해소"**로 갱신 (결정 2·5·11·9 전부 Resolved), 단 §14 승격·Gate (B)·(C)·구현은 열지 않음 | `ADC-0021` §8, `ADC-0022` §D-Gate-A |

### 1.2 이 ADC가 판단하지 않는 것 (경계 — 선행 확장 방지)

아래는 이 ADC의 자동 결과가 아니며, 이 판정으로 앞당겨지거나 열리지 않는다. 근거는 §7에 항목별로 재확인한다.

- **§14 Kernel Public Contract 승격** / Public Responsibilities·Guarantees·Extension Points 신설·수정 / §14 scope의 Context→Execution 확장 — 상위 별도 절차(별도 RFC → ADC → ADR). D-9a는 "지위"만 판정하고 §14 항목을 추가하지 않는다.
- **§14.1 #1 "Task 전달 책임"·#3 "Engine 호출 책임"의 Kernel 귀속 여부** — `BASELINE.md` §14.1·§14.6 N-2가 "미결"로 둔 상태 그대로. D-9c·D-9e는 이를 닫지 않는다.
- **§16.2 Engine Adapter(Model/LLM Provider 호출) seam의 내부 구조·Port·위치** — `ADC-0010` Not Accepted 상태 유지. D-9b가 "결정 9와 별개 seam"임을 확정할 뿐 그 seam을 설계하지 않는다.
- **Scheduler / Engine Gateway / Task Dispatcher Component의 존재·위치·책임·Interface** — `BASELINE.md` §10 Out of Scope, `ADC-0012` Defer 유지.
- **Gate (B)** (`ADC-0019` 재검토 조건 (c) — 다른 계보 또는 v2 프로덕션 관찰), **Gate (C)** 완전 discharge (`ADR-0010` "부분 충족" 유지).
- **LangGraph 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 / Implementation Strategy 세부**.
- **`IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 전면·Scoped 해제** — 결정 9 해소가 이를 해제하지 않는다.
- **Production 구현 착수** — Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md`로 계속 차단(`ADC-0021` §8).
- **결정 2·5·11의 재론·재설계** — `ADC-0022`/`ADR-0011`로 Resolved, 전제로만 사용.
- **Cancellation API 형태** (v1 `ADR-0007` 결정 10) — §16.6 A-OUT Domain Lifecycle 밖 + 구현 세부. 이 ADC 밖.
- **`docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐) / `ADC-0008` 재판단**.
- **`BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`·ADR·CLAUDE.md·Production 코드 문언 편집** — 이 ADC는 §8 지침만 남긴다.

### 1.3 새 실험 없음

이 ADC는 `main`(`3e36e63`)에 이미 병합·기록된 Governance 문서(`BASELINE.md` v1.15, `RFC-0019`~`RFC-0022`, `ADC-0019`~`ADC-0022`, `ADR-0008`~`ADR-0011`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`, `GLOSSARY.md`), v1 Evidence(`archive/v1/docs/adr/0007-workflow-execution-model.md` Accepted, `archive/v1/packages/core/src/jarvis_core/ports/i_workflow_engine.py`), 그리고 **현재 저장소의 HQ 코드 관찰**(`hqs/development/`·`hqs/investment/`)만 인용한다. 새 PoC·프로토타입·측정을 수행하지 않는다.

### 1.4 판정의 성격 — Rule B 대상 아님, §14 승격 아님

결정 9의 잔여 계약 표면은 Evidence 축적 문제가 아니라 **§14.1·§7·§16.6 사이의 정합 문제**다(`RFC-0022` §8). §14.1이 "이 계약은 Context 영역에 한정된다 / 결정된 만큼만 존재한다"고 정한 상태, §16.6이 "§14 승격은 결정 9 해소 이후에만 가능하다"고 전제한 상태, §7이 "Engine 호출의 표준 인터페이스 제공"을 Jarvis OS 책임으로 등재한 상태 — 이 셋의 관계를 기존 문언·코드 정합으로 판정한다. 따라서 재검토 조건 (c)(Gate (B))는 이 판정의 선행조건이 아니며, 이 ADC 이후에도 다음 단계(§14 scope 확장, LangGraph 채택, Scoped 해제, 구현 착수)의 hard gate로 그대로 존속한다(§6). **이 ADC는 §14에 어떤 항목도 추가하지 않는다** — F-9a가 "seam의 지위"를 판정하되, §14 항목 신설은 §14 scope 확장이라는 상위 ADR의 몫이다(§7).

---

## 2. Evidence

`RFC-0022` §2가 인용한 자료 + `main` 코드 관찰. **`RFC-0022` §4의 "가능한 갈래"는 입력이지 결정이 아니며, 이 ADC가 D-9a~D-9f로 확정한다.**

| # | Evidence | 이 ADC에서의 용도 |
|---|---|---|
| **V1** | v1 `archive/v1/docs/adr/0007-workflow-execution-model.md` (Accepted) 결정 9 + `i_workflow_engine.py` — `class IWorkflowEngine(ABC): def run(self, team: Team, dispatch: TaskDispatch) -> WorkflowResult`, "예외를 던지지 않는다", 결정 12(Workflow ≠ Plugin, Composition Root가 direct construction) | 결정 9의 v1 원문 기준선 — 계약 3조각(Port 존재·입력·반환) |
| **V2** | `RFC-0019` §5 표 + G3 — 결정 9의 v2 공백 원인 = Team 부재가 **아니라** §14.1이 "Task 전달 책임"을 계약 범위 밖으로 두는 것. "이 RFC/ADC 범위보다 상위의, 별도로 이미 Open인 Kernel Public Contract 확장 질문" | D-9b·D-9c·D-9f의 2분할 계승 근거 |
| **V3** | `ADC-0019` §Q7 · §Decision 조건 5 · §Next Step 5 — 4공백을 "Accept의 미해결 조건"으로 이월. "네 공백이 후속 Architecture 절차(ADR 또는 별도 RFC)로 **다뤄지기 전에는** §14 승격·구현 착수 불가" | D-9f("해소" = "Architecture 절차로 다뤄짐"), D-Gate-A |
| **V4** | `ADC-0022` §D-9 · §4.6 · §D-11 (6) — "이 ADC는 결정 9를 판정하지 않는다. 입력 시그니처·결과 반환 타입(`WorkflowResult` 대응)·Public Port 정의는 §14.1 'Task 전달 책임' 트랙(별도 RFC → ADC → ADR)이 다룬다. 착수 여부·시점은 이 ADC가 정하지 않는다." "결과를 호출자에게 어떤 타입으로 돌려주는가는 결정 9와 함께 열린 채로 남는다." Gate (A) = "부분 해소" | 이 ADC가 이어받는 정확한 범위 — D-9c·D-9d |
| **V5** | `ADR-0011` / `BASELINE.md` v1.15 §16.6 "v2 공백의 현재 상태" 문단 — "결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처)는 미해결로 남는다 — 공백 원인이 §14.1이 'Task 전달 책임'·'Engine 호출 책임'을 계약 범위 밖으로 두는 것 … 이 책임을 Kernel Public Contract(§14)로 승격하는 것은 결정 9 해소 이후에만 가능하다" | D-9a·D-9e·D-9f — 반영 시 갱신 대상(§8) |
| **V6** | `BASELINE.md` §14.1 표 — "1. Task 전달 책임" · "3. Engine 호출 책임" = **미결, 이 계약의 범위 밖**. "1~3이 각각 판단되면 그때 이 계약이 확장된다." §14.6 N-2 닫지 않는 질문: "Task 전달 책임이 Kernel에 속하는가(RFC-0002 §15-1, 미결)" | D-9c(§14.1 #1 미결 유지), D-9e |
| **V7** | `BASELINE.md` §14 전문 + §14.1("이 계약은 Kernel 전체가 아니라 **Context 영역에 한정**된다") + §14.5 X-1~X-4(Renderer / Ordering Policy / Context Source / Future Context Model — 전부 Context 영역) | D-9a — §14 Extension Point는 현재 Context 영역 한정; Execution seam은 §14 밖 |
| **V8** | `BASELINE.md` §7 System Boundary — Jarvis OS 책임에 "Task/Event의 전달" · "**Engine 호출의 표준 인터페이스 제공 (Port/Adapter)**". §11 표 — Engine 호출 책임 → *Engine Gateway*(구현 후보, "채택 여부는 결정되지 않았다") | D-9e — §7 = 책임 소재, §14 = Public Guarantee 결정 여부. 다른 층위 |
| **V9** | `BASELINE.md` §16.2 / §16.6 "명칭" 문단 — §16.2 = "Model/LLM Provider 호출 책임" = **Engine Adapter**. "Workflow Adapter는 §16.2 Engine Adapter를 재명명하거나 흡수한 것이 아니라 그와 **별개의 책임**이다." "이 명칭은 'Engine' 프레이밍을 의도적으로 계승하지 않는다(`ADC-0019` G2, `ADC-0020` §Q-B)." `RFC-0019` §3이 "Workflow Adapter" / "Engine Adapter"로 이미 구분 | **D-9b 결정적 근거** — 별개 seam |
| **V10** | `BASELINE.md` §16.6 Adapter Contract 서두 + (a)(b)(d) + "Reversibility — 필수 Architecture 불변조건" 문단 — "§16.6 A-IN 부속 명세이며 그 위의 새 계층이 아니다", "Public Surface가 아니고", "'Port' / 'Public' / 'Guarantee' / 'Interface' 어휘를 쓰지 않으며, §14에는 어떤 항목도 추가되지 않는다"(`ADC-0020` §Q-C, `ADR-0009` §Decision 4). (a) = "진행 상태(중간·최종)는 직렬화 가능한 값 … 어댑터는 그 값을 **생산**만". (d) = "Reversibility 재확인 — 신규 계약 아님" | **D-9a·D-9d 결정적 근거** — seam은 비-§14 개념 수준; adapter 산출물 = caller-owned 값 |
| **V11** | `ADC-0010` — "Engine Caller의 위치와 책임" 6개 후보 전수 검토 → **Not Accepted**(현재 Evidence로 Accept 가능한 것 없음) | D-9e — §7 "표준 인터페이스 제공"은 아직 어떤 Component/위치로도 구현 확정 안 됨 |
| **V12** | `hqs/development/mvp/engine.py` — `call_engine(prompt: str) -> str`, `subprocess`로 `claude` CLI 호출. `IMPLEMENTATION_RULES.md` line 15("Engine Gateway(Port/Adapter 추상화) 구현 금지") · line 16("Engine Routing 구현 금지") | D-9b(§16.2 Engine Adapter seam = `str->str` 함수, Workflow 그래프 실행과 별개), D-9e |
| **V13** | `hqs/development/mvp/workflow.py` — `run_mvp_0001(code: str) -> dict`({`code_review`, `test_execution`}), Task 1→2 직접 함수 호출 하드코딩. `try/except` → 오류를 **반환 dict의 값으로**(예외 비전파) | D-9c(HQ별 진입 시그니처), D-9d((b)/G-6 실측) |
| **V14** | `hqs/development/stages/contracts.py` — `VerificationResult`(TypedDict), `status ∈ {PASS, FAIL, INCONCLUSIVE, SKIPPED}`. "새 Architecture Concept이 아니라 … Input/Output을 코드로 명시". `hqs/development/BASELINE.md` §Stage Data Contract — 5개 `*Result` = **HQ-level Public Contract**, "Kernel Public Contract(§14)와 별개 … Kernel Baseline을 확장하거나 대체하지 않는다" | **D-9d 결정적 근거** — 결과 소비 타입은 이미 HQ 소유·HQ마다 다름 |
| **V15** | `hqs/investment/engine_client.py`(Dev HQ `call_engine` 물리적 재수출) + `teams/stock_team.py`(`_run()` → `call_engine`; wave orchestration = `ThreadPoolExecutor` + `run_step` + `Checkpointer` — 별개 계층) + `run.py`(`team.run(company_label, raw_data_path: Path, issue_dir: Path) -> dict`, `TEAMS` 리터럴 딕셔너리) | D-9b(코드에서 두 seam 물리 분리), D-9c(HQ·팀별 시그니처), D-9d(`dict` 반환) |
| **V16** | `ADC-0022` §D-11 (1)(6) — Kernel `WorkflowStatus{SUCCESS,FAILURE,CANCELLED}` enum·`WorkflowResult` 타입 v2 미도입. 값-표현·예외 비전파 = §14.3 G-6 + Adapter Contract (b). 종료 disposition 내용·어휘 = §7상 HQ 도메인 | D-9d(Kernel envelope Reject 근거) |
| **V17** | `ADC-0021` §8 — Gate (A)/(B)/(C), 진입 순서. "(A) = v1 `ADR-0007` 결정 2/5/9/11 v2 공백 해소". "현재 2·3·4·5 중 충족된 것은 없다" | D-9f·D-Gate-A — (A) 완료가 여는 것/열지 않는 것 |
| **V18** | `RFC-0022` §6(F-9a~F-9f + 제외 목록) · §9(Governance Chain: RFC-0022 → **ADC-0023**) · §10(Next Step을 ADC-0023 앞으로 작성) | 이 ADC의 판정 대상·번호 |

---

## 3. Alternatives

### 3.1 이 ADC의 형태

| | 내용 | 판정 |
|---|---|---|
| **G-0** | 결정 9를 §14 항목(Execution 영역 Extension Point) 신설로 지금 해소 | **Reject** — §14.1이 "계약은 Context 영역에 한정 / 결정된 만큼만 존재"라 정한다(V7). Execution seam을 §14에 넣으려면 §14 scope 확장이 선행하며 그건 상위 별도 절차다. 사용자 지시("§14 추가해야 해도 ADC는 결정만, 문안·BASELINE은 후속 ADR")와도 충돌 |
| **G-1 (채택)** | F-9a~F-9f를 각각 판정하되 **결정만 기록**, §14 문안·BASELINE 반영은 후속 ADR. 각 판정 = BASELINE v1.15 + 코드 Evidence의 서술적 확정 | **Accept (§5)** — `ADC-0022`가 `RFC-0021` B-2·B-5·B-11을 판정한 것과 동일 granularity. Gate (A)를 "해소"로 갱신(D-Gate-A) |
| **G-2** | 결정 9를 계속 pending으로 두고 "§14 승격 ADR이 먼저"라고 Defer | **Reject** — §14 승격은 결정 9 해소 **이후**에만 가능(`ADC-0019` 조건 5, V3·V5). 순서가 반대다. `RFC-0022`가 이미 §14.1 트랙 RFC로 개설됐고(V18), 이를 미루면 Gate (A)가 영구히 닫히지 않는다 |

### 3.2 F-9b — seam 정체 (우선 판정)

| | 내용 | 판정 |
|---|---|---|
| **SB-1 (채택)** | **별개 seam.** v1 `IWorkflowEngine`의 "Engine" = Workflow 그래프 실행 조립·진행(§16.6 Workflow Adapter). v2 §16.2 "Engine Adapter" / §14.1 #3 "Engine 호출 책임" / §11 "Engine Gateway" = Model/LLM Provider 호출(`call_engine` 계보). 결정 9 = Workflow Adapter 호출 seam **하나**의 질문, §14.1 **#1 "Task 전달 책임"** 트랙에만 걸림 | **Accept** — §16.6 명칭 문단·`RFC-0019` §3·`ADC-0019` G2·`ADC-0020` §Q-B가 "별개 책임" 확정(V9). 코드에서 물리 분리(`stock_team.py` wave orchestration ↔ `_run()`의 `call_engine`, V15) |
| **SB-2** | **동일 seam.** v1 "Engine"과 v2 "Engine Adapter"는 같은 것 | **Reject** — V9가 명시적으로 "재명명·흡수가 아니라 별개 책임", "'Engine' 프레이밍 미계승". `call_engine`은 `str->str` Model 호출이고(V12), Workflow 그래프 진행은 그 위/밖의 조율 계층 |
| **SB-3** | 결정 9를 **두 개의 분리된 질문**(Workflow Adapter seam / §16.2 Engine Adapter seam)으로 쪼갬 | **Reject** — 결정 9의 대상은 Workflow Adapter 호출 seam **하나**다. §16.2 Engine Adapter seam은 그 자체로 미결(§14.1 #3, `ADC-0010` Not Accepted)이나 결정 9와 **무관**하며, 이 ADC가 그것을 판정하지 않는다(§1.2) |

### 3.3 F-9a — Reversibility seam의 §14 지위

| | 내용 | 판정 |
|---|---|---|
| **PA-1 (채택)** | seam은 현재 **비-§14**(§16.6 Adapter Contract 부속 명세, "개념 수준"). 결정 9 해소가 이 지위를 바꾸지 않는다. §14 승격은 §14 scope의 Context→Execution 확장이라는 **상위 별도 절차**이며 결정 9/이 ADC의 범위가 아니다 | **Accept** — V7(§14 = Context 한정), V10(Adapter Contract = 비-§14, "'Port'/'Public'/'Guarantee'/'Interface' 어휘 미사용, §14 무추가"), `ADC-0020` §Q-C, `ADR-0009` §Decision 4 |
| **PA-2** | 지금 §14 Extension Point로 신설 | **Reject** — G-0과 동일. §14.1 Context 한정, scope 확장 선행, 사용자 지시 위반 |
| **PA-3** | seam을 §7 도메인 내용으로서 **HQ 관례에 위임**(HQ마다 다른 seam 계약) | **Reject** — Reversibility("구현체 교체 시 Kernel·HQ 코드 한 줄도 수정 안 됨")는 §3 "Everything is Replaceable"(Frozen)의 Kernel-HQ **불변조건**이다(V10). HQ가 opt-out할 수 있는 관례가 아니다 |

### 3.4 F-9d — 결과 반환 타입

| | 내용 | 판정 |
|---|---|---|
| **RT-1 (채택)** | Kernel은 결과 반환 타입을 정의하지 않는다. adapter 경계 산출물 = **caller-owned 최종 State 값**(§16.6 Adapter Contract (a) "중간·최종", (b), §14.3 G-6). 그 값에서 HQ가 도출하는 종료 disposition·요약의 **타입** = HQ 도메인(`VerificationResult` 등 HQ Public Contract, Investment `dict`) | **Accept** — V10·V14·V16. `ADC-0022` §D-11 (1)(6) 계승 |
| **RT-2** | Kernel `WorkflowResult` 대응 타입 신설 | **Reject** — `ADC-0022` §D-11 (1)과 충돌(Kernel enum/타입 미도입), v2 코드에 0건(V16). HQ 종료 어휘가 이미 제각각(V14: `{PASS,FAIL,INCONCLUSIVE,SKIPPED}`; V15: `{BUY,SELL,HOLD}`) |
| **RT-3** | 반환 타입도 계속 §14.1 트랙으로 이연 | **Reject** — `ADC-0022` §D-11 (6)이 이미 "결정 9와 함께" 이 트랙으로 넘겼고 `RFC-0022`가 그 트랙이다. 여기서 닫지 않으면 결정 9가 영구 미결 — Gate (A)가 닫히지 않는다 |

---

## 4. Analysis

### 4.1 F-9b 우선 — v1 "Engine"과 v2 §16.2 "Engine Adapter"는 별개 seam이다 (D-9b의 근거)

`RFC-0022` §2.3이 지적한 용어 위험: v1 `IWorkflowEngine`에서 "Engine"은 **workflow 실행 엔진**(그래프 진행·병렬 조립)을 뜻했다. v2에서 "Engine 호출 책임"(§14.1 #3) · "Engine Gateway"(§11) · §16.2 "Engine Adapter"는 모두 **Model/LLM Provider 호출**(`call_engine` 계보)을 뜻한다.

- **문서 확정**: §16.6 명칭 문단이 "Workflow Adapter는 §16.2 Engine Adapter를 재명명하거나 흡수한 것이 아니라 그와 별개의 책임이다", "이 명칭은 'Engine' 프레이밍을 의도적으로 계승하지 않는다"고 명시한다(`ADC-0019` G2, `ADC-0020` §Q-B, V9). `RFC-0019` §3이 이미 "Workflow Adapter" / "Engine Adapter"로 구분해 왔다.
- **코드 확정**: `hqs/investment/teams/stock_team.py`에서 `_run(capability_marker, instruction, data)`가 `call_engine(prompt)`(§16.2 Engine Adapter seam — `str->str` Model 호출)를 호출하고, 그 **바깥**의 wave orchestration(`ThreadPoolExecutor` + `run_step` + `Checkpointer`)이 §16.6 Workflow Adapter가 다룰 그래프 진행 계층이다(V12·V15). 두 seam이 물리적으로 분리돼 있다.

**따라서 D-9b**: 결정 9의 잔여 계약 표면은 **Workflow Adapter 호출 seam 하나**의 질문이며, §14.1 **#1 "Task 전달 책임"** 트랙에만 걸린다. §14.1 **#3 "Engine 호출 책임"** 및 §16.2 Engine Adapter seam은 결정 9와 **무관**하다(별도 미결로 존속하되 이 ADC가 판정하지 않음). 결정 9는 **두 질문으로 쪼개지지 않는다**(SB-3 Reject).

**후속 ADR 정정 지침**: §16.6 "v2 공백의 현재 상태" 문단이 결정 9 공백 원인에 "'Task 전달 책임'·'**Engine 호출 책임**'"을 병기한 것은 D-9b에 비추어 **부정확한 확대**다 — 후속 ADR이 이를 "'Task 전달 책임'"으로 좁혀 정정한다(문안 변경은 ADR, §8-1).

### 4.2 F-9a — seam은 비-§14로 유지되며, §14 승격은 상위 별도 절차다 (D-9a의 근거)

v1 결정 9는 `IWorkflowEngine`을 **Core 소속 Domain Interface**로 두었다. v2에서 그 seam은:

- **개념적으로 이미 존재**: §16.6 "Reversibility — 필수 Architecture 불변조건"이 "어떤 구현체를 제거하고 다른 구현체(최소한 순차 함수 호출)로 교체해도, Kernel과 HQ가 정의하는 코드는 한 줄도 수정되지 않아야 한다"를 요구한다(V10).
- **그러나 지위는 비-§14**: §16.6 Adapter Contract는 그 seam을 "§16.6 A-IN 부속 명세이며 그 위의 새 계층이 아니다", "Public Surface가 아니고", "'Port' / 'Public' / 'Guarantee' / 'Interface' 어휘를 쓰지 않으며, **§14에는 어떤 항목도 추가되지 않는다**"로 못박았다(`ADC-0020` §Q-C, `ADR-0009` §Decision 4, V10).
- **§14의 현재 scope는 Context 영역**: §14.1이 "이 계약은 Kernel 전체가 아니라 Context 영역에 한정된다"고 명시하고, §14.5 Extension Points X-1~X-4는 전부 Context 영역(Renderer / Ordering Policy / Context Source / Future Context Model)이다(V7). Execution Layer의 Workflow Adapter seam을 §14 Extension Point로 만들려면 §14가 먼저 scope를 Context→Execution으로 넓혀야 한다.

**따라서 D-9a**: Workflow Adapter 교체 가능 seam의 §14 지위 = **비-§14 (§16.6 Adapter Contract 부속 명세, "개념 수준")로 유지**된다. 결정 9 해소가 이 지위를 바꾸지 않는다.

- (a) §14 Extension Point **승격**은 §14 scope의 Context→Execution 확장이라는 **상위 별도 절차**(별도 RFC → ADC → ADR)의 몫이며 결정 9/이 ADC의 범위가 아니다. §16.6이 "§14 승격은 결정 9 해소 이후에만 가능하다"고 서술한 것은 그 승격의 **선행조건 하나**(결정 9)를 기술한 것이지, 결정 9 해소가 곧 §14 승격이라는 뜻이 아니다.
- (c) **HQ 관례 위임**은 Reject — Reversibility는 §3 "Everything is Replaceable"(Frozen)의 Kernel-HQ 불변조건이며 HQ opt-out 대상이 아니다(PA-3).

**이 ADC는 §14에 어떤 항목도 추가하지 않는다.** D-9a는 "seam의 지위 = 현재 비-§14, 승격은 상위 절차"라는 **판정만 기록**한다.

### 4.3 F-9c — Kernel은 입력 시그니처를 규정하지 않는다 (D-9c의 근거)

v1 결정 9의 입력은 `(team: Team, dispatch: TaskDispatch)`였다.

- **실행 단위 절반**: `ADC-0022` §D-5가 이미 Resolved했다 — 어댑터는 "이미 구성된 실행 단위"를 **불투명한 HQ 입력**으로 받고 Kernel은 그 형태를 타입하지 않는다.
- **`dispatch` 절반**: v1에서 `TaskDispatch`는 Kernel Stage 1~5(HQ/Division selection)의 산물이었다. v2 코드에는 대응물이 없다 — Dev HQ `run_mvp_0001(code: str)`, Investment `team.run(company_label, raw_data_path, issue_dir)`처럼 **HQ·팀별 진입 시그니처**이며 Kernel 객체가 관통하지 않는다(V13·V15).
- **§14.1 #1 "Task 전달 책임"** 은 "미결, 계약 범위 밖"이고, §14.6 N-2는 "Task 전달 책임이 Kernel에 속하는가"를 "닫지 않는 질문"으로 명시한다(V6).

**따라서 D-9c**: 결정 9의 입력 시그니처 facet = **"Kernel은 실행 메커니즘 호출의 입력 시그니처를 규정하지 않는다"**로 Resolved된다.

- 실행 단위 절반 = 불투명 HQ 입력(`ADC-0022` §D-5 확인).
- 나머지 = HQ별 진입 시그니처. v2에 Kernel 표준 `Dispatch` 타입은 **부재**하며, 이 ADC는 그것을 만들지 않는다.
- **"Task 전달 책임을 Kernel 책임으로 승격할지"** 는 §14.1 #1 / N-2 트랙 — 이 ADC보다 상위의 별개 미결이며, 이 ADC는 그것을 닫지 않는다. 결정 9의 입력 facet은 그 상위 질문에 **의존하지 않고** "Kernel 미규정, HQ 소유"로 종결된다 — Kernel이 입력을 규정하지 않는 것이 곧 이 facet의 답이다.

### 4.4 F-9e·F-9f — §7 ↔ §14.1은 다른 층위이고, "해소"의 최소 조건은 충족된다 (D-9e·D-9f의 근거)

**F-9e**: §7 System Boundary는 "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)"을 Jarvis OS 책임으로 등재한다(V8). §14.1은 "Engine 호출 책임 = 미결, 계약 범위 밖"이라 한다(V6). 이는 **모순이 아니라 층위 차이**다:

- §7 = **책임 소재**의 선언("이 책임은 Jarvis OS의 것이지 HQ의 것이 아니다"). §11이 이를 뒷받침한다("Kernel은 책임을 가진다. Component는 그 책임을 구현하는 방법이다" — Engine Gateway는 "채택 여부 결정 안 됨").
- §14 = **외부가 의존해도 되는 Public Guarantee**의 정의, 그리고 §14.1이 "결정된 만큼만 존재한다"고 한 상태. §14.1 표가 "Engine 호출 책임 = 미결, 계약 범위 밖"이라 적은 것이 바로 이 상태의 정확한 기술이다.
- **`ADC-0010` 제약**: Engine Caller(=`call_engine` 호출부)의 위치·책임이 Not Accepted이므로(V11), §7의 "표준 인터페이스 제공"은 아직 **어떤 Component/위치로도 구현이 확정되지 않았다**. §7의 등재는 방향만 고정하고, `IMPLEMENTATION_RULES.md` line 15·16이 그 구현을 현재 막는다(V12).
- **결정 9와의 관계**: D-9b에 의해 이 "Engine 호출"(§7 / §14.1 #3 / §16.2)은 Workflow Adapter(결정 9) seam과 **별개**다. 따라서 §7 ↔ §14.1 #3 정합성은 결정 9 해소의 선행조건이 **아니다** — 결정 9는 §14.1 #1 트랙에만 걸린다(D-9c).

**F-9f**: `ADC-0019` §Decision 조건 5의 문언은 "네 공백이 후속 Architecture 절차로 **다뤄지기 전에는** §14 승격·구현 착수 불가"다(V3) — "다뤄지다"는 "Architecture 절차로 명시적으로 판정됨"이지 "새 계약으로 채워짐"이 아니다.

- 결정 9의 세 조각이 이 ADC로 판정된다: Port 존재(D-9a: 비-§14 유지, 승격은 상위 절차) / 입력 시그니처(D-9c: Kernel 미규정, HQ 소유) / 결과 반환 타입(D-9d: Kernel envelope 미도입, caller-owned 값 + HQ 타입). **세 조각 모두 "Kernel이 규정하지 않는다"는 판정으로 종결 가능**하며, 그 판정 자체가 `ADC-0019` 조건 5의 "다뤄짐"을 충족한다.
- **따라서 결정 9의 "해소" 최소 조건 = 잔여 세 조각 각각이 Architecture 절차로 명시적 disposition을 받는 것**이며, 그 disposition이 "§14 확장"이든 "Kernel 미규정"이든 무방하다(F-9f (a)/(b) 둘 다 유효, (c) "좁은 비-§14 seam 계약 신설"은 불필요 — 기존 §16.6 Adapter Contract로 충분). 이 ADC(+ 후속 ADR의 BASELINE 반영)가 이 최소 조건을 충족한다.

### 4.5 Gate (A) 상태 — "부분 해소" → "해소", 단 여는 것은 제한적 (D-Gate-A의 근거)

`ADC-0021` §8 Gate (A)(= v1 `ADR-0007` 결정 2/5/9/11)의 상태:

- 결정 2·5·11 = Resolved(`ADC-0022` → `ADR-0011`, BASELINE v1.15).
- 결정 9 = Resolved(`ADC-0023` + 후속 ADR) — 잔여 세 조각 전부 판정(D-9a·D-9c·D-9d).
- → **Gate (A) = 해소 (전체)**.

**Gate (A) 해소가 여는 것**: `ADC-0021` §8 진입 순서의 "(A)" 항목 완료.

**Gate (A) 해소가 열지 않는 것**(§6·§7에서 재확인):

- **§14 Kernel Public Contract 승격** — §14 scope의 Context→Execution 확장이라는 상위 ADR이 선행(D-9a). 결정 9 해소는 그 선행조건 하나를 충족할 뿐이다.
- **Gate (B)** (`ADC-0019` 재검토 조건 (c)) · **Gate (C)** (Reversibility v2 완전 검증, `ADR-0010` "부분 충족") — 이 ADC로 진전 없음.
- **Production 구현 착수** — Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19로 계속 차단(`ADC-0021` §8, §16.6). 결정 9 해소가 이 중 어느 것도 해제하지 않는다.
- **LangGraph 채택 / Implementation Strategy 세부 ADC / Scoped 해제 ADR** — 전부 별도 hard gate로 존속.

---

## 5. Decision

**A. Accept — 결정 9 잔여 계약 표면 Resolution (Gate (A) 완전 해소).** 아래 D-9b~D-Gate-A는 BASELINE v1.15 문언과 `main` 코드 Evidence의 서술적 확정이며, 새 Kernel Concept·Layer·Component·Public Contract·Port·enum·타입을 추가하지 않는다. 실제 `BASELINE.md`/`GLOSSARY.md` 반영은 후속 ADR이 수행한다(§8).

### D-9b. F-9b — v1 "Engine"과 v2 §16.2 "Engine Adapter"는 별개 seam

1. v1 `IWorkflowEngine`의 "Engine" = **Workflow 그래프 실행 조립·진행 책임**(= §16.6 Workflow Adapter). v2 §16.2 "Engine Adapter" / §14.1 #3 "Engine 호출 책임" / §11 "Engine Gateway" = **Model/LLM Provider 호출 책임**(`call_engine` 계보). 이 둘은 §16.6 명칭 문단 · `RFC-0019` §3 · `ADC-0019` G2 · `ADC-0020` §Q-B가 "별개 책임"으로 이미 확정했고, `hqs/` 코드에서 물리적으로 분리돼 있다(wave orchestration ↔ `_run()`의 `call_engine`).
2. **결정 9는 Workflow Adapter 호출 seam 하나의 질문**이며, §14.1 **#1 "Task 전달 책임"** 트랙에만 걸린다. §14.1 #3 "Engine 호출 책임" · §16.2 Engine Adapter seam · `ADC-0010`(Engine Caller 위치 Not Accepted)은 결정 9와 **무관**하며 이 ADC가 판정하지 않는다 — 별도 미결로 존속.
3. 결정 9는 두 질문으로 쪼개지지 않는다.

**후속 ADR 정정**: §16.6 "v2 공백의 현재 상태" 문단의 결정 9 공백 원인 병기 "'Task 전달 책임'·'Engine 호출 책임'" → "'Task 전달 책임'"으로 좁힘(§8-1).

### D-9a. F-9a — Reversibility seam의 §14 지위 = 비-§14 유지

1. Workflow Adapter 교체 가능 seam(§16.6 Reversibility 필수 불변조건이 요구)의 §14 지위는 **비-§14**다 — §16.6 Adapter Contract 부속 명세, "개념 수준"(`RFC-0019` §7 지위 계승), "'Port' / 'Public' / 'Guarantee' / 'Interface' 어휘 미사용, §14 무추가"(`ADC-0020` §Q-C, `ADR-0009` §Decision 4). **결정 9 해소가 이 지위를 바꾸지 않는다.**
2. **(a) §14 Extension Point 승격**은 §14 scope의 Context→Execution 확장이라는 **상위 별도 절차**(별도 RFC → ADC → ADR)의 몫이다. §14.5 X-1~X-4가 전부 Context 영역인 현재 §14에 Execution seam을 넣을 자리가 없다. §16.6의 "§14 승격은 결정 9 해소 이후에만 가능하다"는 서술은 그 승격의 **선행조건 하나**(결정 9)를 기술한 것이지 결정 9 해소 = §14 승격이 아니다.
3. **(c) HQ 관례 위임 Reject** — Reversibility는 §3 "Everything is Replaceable"(Frozen)의 Kernel-HQ 불변조건이며 HQ opt-out 대상이 아니다.
4. **이 ADC는 §14에 어떤 항목도 추가하지 않는다.** D-9a는 지위 판정만 기록한다.

### D-9c. F-9c — Kernel은 입력 시그니처를 규정하지 않는다

1. 실행 메커니즘 호출의 **입력 시그니처를 Kernel이 규정하지 않는다.**
2. 실행 단위 절반 = 불투명 HQ 입력(`ADC-0022` §D-5 확인 — Kernel이 형태를 타입하지 않음).
3. 나머지 절반(v1 `dispatch: TaskDispatch` 대응) = HQ·팀별 진입 시그니처(`run_mvp_0001(code)`, `team.run(company_label, raw_data_path, issue_dir)`). v2에 Kernel 표준 `Dispatch` 타입은 **부재**하며 이 ADC가 만들지 않는다.
4. **"Task 전달 책임을 Kernel 책임으로 승격할지"** (§14.1 #1 / §14.6 N-2)는 이 ADC보다 상위의 별개 미결이며, 이 ADC는 그것을 닫지 않는다. 결정 9의 입력 facet은 그 상위 질문에 의존하지 않고 **"Kernel 미규정, HQ 소유"** 로 종결된다.

### D-9d. F-9d — Kernel은 결과 반환 타입을 정의하지 않는다

1. Kernel은 실행 **결과 반환 타입을 정의하지 않는다.** v1 `WorkflowResult` 대응 Kernel 타입을 v2에 도입하지 않는다(`ADC-0022` §D-11 (1) 계승 — v2 코드에 0건).
2. adapter 경계를 벗어나는 산출물 = **caller-owned 최종 State 값**(§16.6 Adapter Contract (a) "중간·최종", (b), §14.3 G-6). 별도의 Kernel 반환 타입 계층이 없다.
3. 그 값에서 HQ가 도출하는 종료 disposition·요약의 **타입** = HQ 도메인 — Development HQ `VerificationResult`(HQ-level Public Contract, §14와 별개), Investment `wave_summary` / `{action, rationale, ...}` `dict`(V14·V15).
4. F-9d 세 갈래 중 **(ii) caller-owned 값 + (iii) HQ 타입의 조합**이며, (i) Kernel-typed envelope는 Reject(RT-2). 이는 §16.6 Adapter Contract (a)(b) + `ADC-0022` §D-11이 이미 함의한 것의 서술적 확정이며 새 계약이 아니다.

### D-9e. F-9e — §7 ↔ §14.1은 다른 층위 (모순 아님)

1. §7 System Boundary "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)" = **책임 소재**의 선언(누구 책임인가). §14 Kernel Public Contract = **외부가 의존해도 되는 Public Guarantee**의 정의이며, §14.1이 "결정된 만큼만 존재한다"고 한 상태. §14.1 표의 "Engine 호출 책임 = 미결, 계약 범위 밖"이 이 상태의 정확한 기술이다 — 두 절은 층위가 다르지 모순이 아니다.
2. **`ADC-0010` 제약**: Engine Caller 위치·책임이 Not Accepted이므로 §7의 "표준 인터페이스 제공"은 아직 어떤 Component/위치로도 구현이 확정되지 않았고, `IMPLEMENTATION_RULES.md` line 15·16이 그 구현을 현재 막는다.
3. **결정 9와의 관계**: D-9b에 의해 이 "Engine 호출"(§7 / §14.1 #3 / §16.2)은 Workflow Adapter(결정 9) seam과 별개다. §7 ↔ §14.1 #3 정합성은 결정 9 해소의 선행조건이 아니다.
4. **이 ADC는 §7 목록도 §14.1 표도 편집하지 않는다** — D-9e는 두 절의 관계에 대한 해석 확정이다. 후속 ADR은 §16.6 문단에 이 해석 1문장만 부기한다(§8-5).

### D-9f. F-9f — 결정 9 "해소"의 최소 조건과 충족

1. **결정 9 "해소"의 최소 조건** = 잔여 계약 표면 세 조각(Port 존재·입력 시그니처·결과 반환 타입) 각각이 Architecture 절차로 **명시적 disposition을 받는 것**이며, 그 disposition이 "§14 확장"이든 "Kernel이 규정하지 않음"이든 무방하다(`ADC-0019` §Decision 조건 5의 "후속 Architecture 절차로 다뤄지기" 문언 — "새 계약으로 채워짐"이 아님).
2. **이 ADC(+ 후속 ADR의 BASELINE 반영)가 그 최소 조건을 충족한다**: D-9a(Port 존재 = 비-§14 유지) · D-9c(입력 = Kernel 미규정) · D-9d(반환 타입 = Kernel 미정의). 세 조각 모두 판정 완료.
3. F-9f 갈래 중 (a) §14 확장·(b) 명시적 부정("Kernel 미규정") **둘 다 유효**하며, (c) "좁은 비-§14 seam 계약 신설"은 불필요하다 — 기존 §16.6 Adapter Contract로 충분(새 계약 절 없음).

### D-Gate-A. Gate (A) 상태 갱신 — 해소

`ADC-0021` §8 Gate (A)(= v1 `ADR-0007` 결정 2/5/9/11)의 상태는 이 ADC + 후속 ADR 이후:

> **Gate (A) — 해소**: 결정 2·5·11 = Resolved(`ADC-0022` / `ADR-0011`, BASELINE v1.15). 결정 9 = Resolved(`ADC-0023` + 후속 ADR) — Port 존재 지위·입력 시그니처·결과 반환 타입 세 조각 전부 "Kernel이 §16.6 밖 별도 계약으로 규정하지 않음"으로 판정.

**Gate (A) 해소가 열지 않는 것**:

- **§14 Kernel Public Contract 승격** — §14 scope의 Context→Execution 확장 상위 ADR이 선행(D-9a). 결정 9 해소는 그 선행조건 하나를 충족할 뿐이다.
- **Gate (B)** (`ADC-0019` 재검토 조건 (c)) · **Gate (C)** (Reversibility v2 완전 검증, `ADR-0010` "부분 충족") — 이 ADC로 진전 없음, 다음 단계의 hard gate로 존속.
- **Production 구현 착수** — Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19로 계속 차단(`ADC-0021` §8, §16.6). 결정 9 해소가 이 중 어느 것도 해제하지 않는다.
- **LangGraph 채택 / Implementation Strategy 세부 ADC / Scoped 해제 ADR**.

### Reason

- **§4.1 (D-9b)** — §16.6 명칭 문단·`RFC-0019` §3·`ADC-0019` G2·`ADC-0020` §Q-B가 "별개 책임"을 이미 확정했고(V9), 코드에서 두 seam이 물리 분리돼 있다(V12·V15). SB-2(동일 seam)·SB-3(두 질문으로 분할) Reject.
- **§4.2 (D-9a)** — §14가 Context 영역 한정(V7)이고 §16.6 Adapter Contract가 "비-§14, §14 무추가"로 못박았다(V10). PA-1 채택 — PA-2(지금 §14 신설)는 §14.1·사용자 지시 위반, PA-3(HQ 위임)은 Reversibility 불변조건 위반.
- **§4.3 (D-9c)** — `ADC-0022` §D-5가 실행 단위 절반을 이미 Resolved했고, 코드에 Kernel `Dispatch` 타입이 0건이다(V13·V15). §14.1 #1 / N-2의 "미결"은 이 ADC보다 상위이므로 닫지 않고, 결정 9 입력 facet은 "Kernel 미규정"으로 종결.
- **§4.4 (D-9d)** — `ADC-0022` §D-11 (1)(6) 계승. Development HQ `VerificationResult.status`가 HQ-level Public Contract로 이미 존재하고 HQ마다 종료 어휘가 다르다(V14·V15). RT-2(Kernel 타입 신설)·RT-3(계속 이연) Reject.
- **§4.4 (D-9e·D-9f)** — §7 = 책임 소재, §14 = Public Guarantee 결정 여부. `ADC-0010`이 Engine Caller를 Not Accepted로 남겼다(V11). "해소" = "Architecture 절차로 다뤄짐"(`ADC-0019` 조건 5 문언, V3) — 세 조각 판정으로 충족.
- **§4.5 (D-Gate-A)** — 결정 2·5·11(`ADC-0022`) + 결정 9(이 ADC)로 Gate (A) 전체 해소. §14 승격·Gate (B)·(C)·구현은 `ADC-0021` §8·`ADC-0019` 조건 5로 별도 hard gate 존속.

### Decision Rationale

이 Decision은 `ADC-0019`/`ADC-0020`/`ADC-0021`/`ADC-0022`/`ADR-0008`~`ADR-0011`이 확정한 것을 **하나도 뒤집지 않는다** — §16.6 존재·A-IN·A-OUT·Reversibility·명칭·Adapter Contract (a)(b)(c)(d)·(c) Defer·Gate (B)/(C)·조건 이월·결정 2·5·11 Resolution을 전부 전제로만 사용한다(§6). `RFC-0022`가 개설한 F-9a~F-9f를 판정하되, 모든 판정이 "Kernel은 결정 9의 잔여 계약 표면을 §16.6 밖 별도 계약으로 규정하지 않는다"로 수렴하며 새 Kernel 표면을 만들지 않는다. §14 승격·§14.1 #1·#3의 Kernel 귀속·§16.2 Engine Adapter seam 설계·Gate (B)/(C)·LangGraph·구현·`IMPLEMENTATION_RULES.md` 해제는 전부 이 ADC 밖의 별도 절차로 남는다(§7).

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6 전부 무변경** — 범위(A-IN)·명시적 제외(A-OUT)·§16.3~16.5 불가침·Reversibility 필수·조건 이월·미확정 항목. 조건 5의 "§14 승격·구현 착수 불가"는 결정 9 해소로 **§14 승격 부분만 선행조건 하나가 충족**되며, Gate (B)·(C)·§14 scope 확장은 그대로 남는다.
2. **`ADC-0020` §6 Conditions 1~8 전부 무변경** — 특히 조건 3(v1 결정 2/5/9/11 Conditional — 이제 전부 해소), 조건 4(`IMPLEMENTATION_RULES.md` 금지 유지), 조건 5(§14 미승격 — 이 ADC도 §14 항목 미추가), 조건 8(Adapter Contract 정식화 범위 = (a)(b)(d), (c) Defer — D-9a·D-9d는 (a)(b)(d)를 재기술만).
3. **`ADC-0021` §D1~D4·§6·§7·§8 전부 무변경** — Sequential Reference 기본선·LangGraph 평가 대기·Gate (B)·(C)·Implementation Strategy 세부·Scoped 해제는 전부 별도 hard gate로 존속. §8 진입 순서에서 이 ADC는 "(A)" 항목을 **완료**시키고, (B)·(C) 및 그 이후는 그대로 남긴다.
4. **`ADC-0022` §D-0~§D-11c 무변경** — 결정 2·5·11 Resolution, "실행 단위" 설명 용어 지위, (c) 배치 = HQ 스키마를 전제로만 사용. D-9d는 `ADC-0022` §D-11 (6)이 넘긴 "결과 반환 타입"을 이어받아 종결한다.
5. **`ADR-0010` "부분 충족" 무변경** — Gate (C) E4 잔여 한계 (i)~(iii)·완전 discharge 미선언 유지.
6. **Rule B 미충족 유지** — 이 ADC는 §14.1·§7·§16.6 정합 판정이지 Evidence 축적이 아니다(§1.4). 재검토 조건 (c)(Gate (B))는 다음 단계의 hard gate로 그대로 유효하다.
7. **§14 Kernel Public Contract 미승격 유지** — Public Port·Surface·Guarantee·Interface 신설 없음. §14.1 표의 행 상태(#1·#3 = 미결) 무변경. §14 scope = Context 영역 유지. Adapter Contract 부속 명세의 비-§14 지위(`ADC-0020` §Q-C) 계승.
8. **`IMPLEMENTATION_RULES.md` 금지 유지** — line 9(Workflow Parser) / line 13(Scheduler·orchestration·Dynamic Routing·§6 넓은 Runtime) / line 14(Stage 재진입·조건부 Stage) / line 15(Engine Gateway Port/Adapter) / line 16(Engine Routing) / line 19(Event Bus). 이 ADC는 Scoped 부분 해제를 하지 않는다.
9. **`BASELINE.md`·`GLOSSARY.md`·`ADC.md`·§7 목록·§14.1 표 문언 무변경** — §16.6/`GLOSSARY.md` 반영은 후속 ADR. 이 ADC는 §8 지침만 남긴다.
10. **§16.2 Engine Adapter / `ADC-0010` / §16.7 무변경** — D-9b는 §16.2 seam을 "별개"로 확정만 하고 설계하지 않는다. §16.7 Workflow Kernel Module Defer도 재판단하지 않는다.

---

## 7. Out of Scope (이 ADC의 자동 결과가 아닌 것 — 경계 재확인)

| 항목 | 상태 유지 근거 |
|---|---|
| **§14 Kernel Public Contract 승격 / §14 scope의 Context→Execution 확장 / Public Responsibilities·Guarantees·Extension Points 신설** | `ADC-0019` §Q7·조건 5, §14.1(Context 한정), `ADC-0020` §Q-C. D-9a는 "지위"만 판정, §14 항목 미추가. 별도 RFC → ADC → ADR |
| **§14.1 #1 "Task 전달 책임" / #3 "Engine 호출 책임"의 Kernel 귀속 여부** | §14.1·§14.6 N-2 "미결" 유지. D-9c·D-9e는 결정 9 facet만 종결하고 이 상위 질문을 닫지 않음 |
| **§16.2 Engine Adapter(Model/LLM Provider 호출) seam의 내부 구조·Port·위치** | `ADC-0010` Not Accepted 유지. D-9b는 "별개 seam" 확정만, 설계 아님 |
| **Scheduler / Engine Gateway / Task Dispatcher Component 설계** | §10 Out of Scope, `ADC-0012` Defer |
| **Cancellation API 형태 (v1 `ADR-0007` 결정 10)** | §16.6 A-OUT Domain Lifecycle 밖 + 구현 세부 |
| **Gate (B) (`ADC-0019` 재검토 조건 (c)) / Gate (C) 완전 discharge** | `ADC-0021` §8, `ADR-0010`. 이 ADC로 진전 없음 |
| **LangGraph 채택 / 어댑터 래핑 / Checkpointer 백엔드 / Implementation Strategy 세부** | `ADC-0019` §Q8, `ADC-0021` §D2·§7 |
| **`IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 전면·Scoped 해제** | `ADC-0020` §6 조건 4, `ADC-0021` §8. 결정 9 해소가 해제하지 않음 |
| **Production 구현 착수 (`core/`·`hqs/`·`dashboard/`)** | Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md` |
| **결정 2·5·11 재론·재설계** | `ADC-0022` / `ADR-0011` Resolved. 전제로만 |
| **`docs/decisions/adc/ADC.md` ADC-02 / `ADC-0008` 재판단, §16.7 Defer 재판단** | `ADC-0019` §Q8, §16.6 "Workflow Module Defer와의 구분" |
| **`BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`·ADR·CLAUDE.md 문언 편집** | → 후속 ADR (§8) |
| **Rule B 충족 선언** | §1.4 — §14.1·§7·§16.6 정합 판정, Evidence 축적 아님 |

---

## 8. 후속 ADR에서 반영할 사항 (Baseline 지침 — 이 ADC가 직접 반영하지 않음)

후속 ADR(Minor 예상)이 `BASELINE.md` §16.6과 `GLOSSARY.md`에 아래를 반영한다. §5·§6·§7 목록·§11·§14·§14.1 표·§16.1~§16.5·§16.7, Adapter Contract (a)(b)(c)(d) 문언, `IMPLEMENTATION_RULES.md`는 무변경(`ADR-0009` §6, `ADR-0011` 선례).

1. **§16.6 "v2 공백의 현재 상태" 문단 갱신** —
   - "결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처)는 미해결로 남는다" → "**결정 9는 `ADC-0023`으로 Resolved**다 — Kernel은 (i) Workflow Adapter 교체 가능 seam을 §16.6 Adapter Contract(비-§14)로 두고, (ii) 실행 메커니즘 호출의 입력 시그니처를 규정하지 않으며, (iii) 결과 반환 타입을 정의하지 않는다(caller-owned 최종 State 값 + HQ 도메인 타입)."
   - 공백 원인 병기 "'Task 전달 책임'·'Engine 호출 책임'" → "'**Task 전달 책임**'"으로 좁힘(D-9b — §16.2 Engine Adapter seam은 결정 9와 별개).
   - "이 책임을 Kernel Public Contract(§14)로 승격하는 것은 결정 9 해소 이후에만 가능하다" → 유지하되 "**§14 승격은 §14 scope의 Context→Execution 확장이라는 별도 절차이며, 결정 9 해소는 그 선행조건 하나를 충족한 것**"을 1문장 부기(D-9a).
   - `ADC-0021` §8 Gate (A) = "부분 해소" → "**해소** (결정 2·5·11·9 전부 Resolved)". "Gate (B)·(C)·§14 승격·`IMPLEMENTATION_RULES.md` 차단은 유지 — 결정 9 해소가 이 중 어느 것도 해제하지 않는다"를 명시.
2. **§16.6 Adapter Contract 인접에 D-9a 1문장** — "이 seam의 §14 지위 = 비-§14(위 부속 명세). §14 Extension Point 승격은 §14 scope 확장 별도 ADR의 몫이며 이 반영은 §14 항목을 추가하지 않는다(`ADC-0023` §D-9a)."
3. **§16.6 A-IN 프레이밍에 D-9c 1문장** — "실행 메커니즘 호출의 **입력 시그니처**는 Kernel이 규정하지 않는다 — 실행 단위 절반 = 불투명 HQ 입력(`ADC-0022` §D-5), 나머지 = HQ별 진입 시그니처(`run_mvp_0001(code)`, `team.run(...)`). Kernel 표준 `Dispatch` 타입 부재. 'Task 전달 책임'의 Kernel 귀속 여부는 §14.1 #1 트랙 — 이 반영이 닫지 않는다(`ADC-0023` §D-9c)."
4. **§16.6 A-IN(a) / "v2 공백" 문단에 D-9d 1문장** — "**결과 반환 타입** = Kernel 미정의. adapter 경계 산출물 = caller-owned 최종 State 값(Adapter Contract (a)(b), §14.3 G-6); 그 값에서 HQ가 도출하는 disposition·요약 타입 = HQ 도메인(`VerificationResult` 등). Kernel-typed envelope(`WorkflowResult` 대응) 미도입 — `ADC-0022` §D-11 계승(`ADC-0023` §D-9d)."
5. **§16.6 명칭 문단 인접에 D-9e 1문장** — "§7 'Engine 호출의 표준 인터페이스 제공'(책임 소재) ↔ §14.1 'Engine 호출 책임 = 계약 범위 밖'(Public Guarantee 결정 여부)은 층위 차이이지 모순이 아니다. 이 'Engine 호출'(§16.2 Engine Adapter, Model/LLM)은 Workflow Adapter(결정 9) seam과 별개다(`ADC-0023` §D-9b·§D-9e). `ADC-0010`(Engine Caller 위치 Not Accepted) 유지."
6. **§16.6 "Production 구현과의 관계" 문단** — "v1 `ADR-0007` 결정 9 공백 해소(결정 2·5·11은 `ADC-0022`로 해소됨)" → "**결정 2·5·9·11 전부 Resolved(`ADC-0022`·`ADC-0023`)**". 차단 조건 = Gate (B) + Gate (C) + `IMPLEMENTATION_RULES.md` 유지 명시(결정 9 해소가 이를 해제하지 않음).
7. **`GLOSSARY.md` "Workflow Adapter (Reference)" 절** — "v1 `ADR-0007` 결정 9는 §14.1 트랙 pending" → "v1 `ADR-0007` 결정 9 = `ADC-0023`으로 **Resolved** (Kernel은 Port 존재 지위·입력 시그니처·결과 반환 타입을 §16.6 밖 별도 계약으로 규정하지 않음; §14 승격은 §14 scope 확장 이후)". `ADC-0021` §8 Gate (A) = "해소".
8. **Version**: v1.15 → v1.16 (Minor 예상), Architecture State = Frozen 유지.
9. **명시적 비변경 재확인**: §5·§6·§7 목록·§11 표·§14 항목·§14.1 표·§16.1~§16.5·§16.7, §16.2 Engine Adapter 문언, Adapter Contract (a)(b)(c)(d) 문언, Reversibility 필수 불변조건 문단, `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19, `docs/decisions/adc/ADC.md` ADC-02, `ADC-0008`, `ADC-0010`, Gate (B)·(C).

---

## 9. Architecture / Governance Review

`RFC-0019`~`RFC-0022`, `ADC-0019`~`ADC-0022`, `ADR-0008`~`ADR-0011`, `BASELINE.md` v1.15, `hqs/development/`·`hqs/investment/` 코드, `IMPLEMENTATION_RULES.md`, `ADC-0010`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`를 기준으로 이 ADC의 범위·Traceability·정합성을 검증한다.

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 선행 체인(`ADC-0019`~`ADC-0022`, `ADR-0008`~`ADR-0011`)이 확정한 것을 뒤집는가 | **아니오** — §16.6 존재·A-IN·A-OUT·Reversibility·명칭·Adapter Contract·(c) Defer·Gate (B)/(C)·조건 이월·결정 2·5·11 Resolution을 전부 전제로만 사용(§6 Conditions 1~5·10) |
| `RFC-0022` §6 F-9a~F-9f를 판정하는가 | **예** — D-9b·D-9a·D-9c·D-9d·D-9e·D-9f가 각각 대응. `RFC-0022` §10 Next Step에 답. `ADC-0022`가 `RFC-0021` §6을 판정한 것과 동일 관계 |
| `RFC-0022` §4 "가능한 갈래"를 자동 채택했는가 | **아니오** — §4 갈래는 입력. §3 Alternatives에서 SB-1(F-9b), PA-1(F-9a), RT-1(F-9d)을 **독립 판정**하고 SB-2/SB-3·PA-2/PA-3·RT-2/RT-3를 Reject. 각 Reason이 Evidence(V1~V18) 기반 |
| F-9b를 먼저 판정했는가 | **예** — §3.2·§4.1·D-9b가 §3.3 이후·D-9a 이후보다 앞. F-9b 결과가 F-9c·F-9e 범위를 좁힘(§14.1 #1만, #3 무관) |
| 결정 2·5·11을 재론했는가 | **아니오** — `ADC-0022`/`ADR-0011` Resolved를 전제로만(§6 조건 4, §7) |
| `ADC-0021` §8 Gate (A) 중 결정 9를 해소하는 것이 §14.1을 우회 확장하는가 | **아니오** — `RFC-0022`가 §14.1 트랙 RFC로 정식 개설됐고(V18), D-9c는 오히려 "Kernel은 입력을 규정하지 않는다 / Task 전달 책임 Kernel 귀속은 닫지 않는다"로 **확장을 거부**한다. §14 항목 0건 추가 |
| `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준"(① 지금 결정 안 하면 상위 Architecture 진행 불가) | **①에 해당** — 결정 9 미해결이면 Gate (A)가 닫히지 않아 `ADC-0021` §8 진입 순서가 (A)에서 정지. 이 판정이 그것을 해소 |

### 9.2 경계 — Architecture / Contract 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임·Layer·Component·Concept을 추가했는가 | **아니오** — D-9b는 §16.2/§16.6 seam 구분을 확정만, D-9a는 지위 판정만, D-9c·D-9d는 "Kernel 미규정/미정의"의 서술 |
| Contract Change가 있는가 (Public Interface·Port·Guarantee·Type·enum) | **없음** — §14 무접촉(§6 조건 7). Adapter Contract (a)(b)(c)(d) 문언 무변경. Kernel `WorkflowResult`/`Dispatch` 타입 미도입(D-9c·D-9d). "'Port'/'Public'/'Guarantee'/'Interface' 어휘 미사용" 준수 |
| §14에 항목을 추가했는가 | **아니오** — D-9a가 "지위 = 비-§14, 승격은 상위 절차"로 명시. §14 scope = Context 유지 |
| §7 목록 / §14.1 표를 편집했는가 | **아니오** — D-9e는 두 절의 관계 해석 확정. 후속 ADR이 §16.6에 1문장 부기(§8-5), §7·§14.1 원문 무변경 |
| §16.2 Engine Adapter seam을 설계했는가 | **아니오** — D-9b는 "결정 9와 별개"만 확정. `ADC-0010` Not Accepted 유지(§6 조건 10) |
| 이 판정이 §14 승격·구현·Scoped 해제·LangGraph·Gate (B)/(C) 중 무엇이든 앞당기는가 | **아니오** — D-9a(§14 승격 = 상위 절차), D-9f·D-Gate-A(Gate (A) 해소가 여는 것 = `ADC-0021` §8 "(A)" 항목뿐), §6·§7 |
| `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`를 이 ADC가 변경하는가 | **아니오** — §8이 후속 ADR 지침만. 이 ADC 파일 1건만 신규 작성(미커밋) |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| F-9a~F-9f를 각각 독립 Decision 대상으로 판정, 결정 2·5·11은 Resolved 전제 | **준수** — §5 D-9a~D-9f 6개 독립 Decision. §6 조건 4·§7에 결정 2·5·11 전제 명시 |
| F-9b를 먼저 검토, v1 Workflow 실행 Engine ↔ v2 §16.2 Model/LLM Engine 동일/별도 seam 결정 | **준수** — §3.2·§4.1·D-9b (우선). SB-1(별개 seam) Accept, SB-2·SB-3 Reject |
| F-9a=Reversibility seam §14 지위, F-9c=입력 시그니처, F-9d=결과 반환 타입, F-9e=§7↔§14.1 정합, F-9f=Gate A 해소 최소 조건 | **준수** — D-9a/D-9c/D-9d/D-9e/D-9f 각각 대응 |
| 각 Decision은 BASELINE v1.15 + 현재 코드 Evidence 기준, 새 요구사항 임의 생성 금지 | **준수** — 모든 D가 V1~V18 인용. D-9a·D-9c·D-9d = "Kernel이 규정하지 않는다"의 서술적 확정. 새 Kernel 표면 0건(§9.2) |
| Gate B/C, LangGraph, Production 구현, `IMPLEMENTATION_RULES` 해제는 판정하지 않음 | **준수** — §1.2·§7에 전부 Out of Scope. §6 조건 3·5·6·8. D-Gate-A가 "열지 않는 것"으로 재확인 |
| §14 Public Contract를 추가해야 해도 ADC는 결정만, 문안/BASELINE은 후속 ADR | **준수** — D-9a가 §14 항목 미추가, §8이 후속 ADR 지침. G-0 Reject |
| `RFC-0022` Boundary Question + 선행 ADC/ADR Governance Chain 추적 | **준수** — §10 Traceability, §1 근거 위임 표 |
| Draft 작성 후 Architecture/Governance Review 수행 | **준수** — §9. BASELINE/GLOSSARY/ADR/코드 수정·commit·PR·merge 없음. 이 ADC 파일 1건만 신규 작성(미커밋) |

### 9.4 판정

**PASS.** 이 ADC는:

- `ADC-0019` 조건 1~6, `ADC-0020` §6 조건 1~8, `ADC-0021` §D1~D4·§6~§8, `ADC-0022` §D-0~§D-11c, `ADR-0010` "부분 충족", Rule B 미충족, `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 금지, Gate (B)·(C), `ADC-0010` Not Accepted를 **하나도 약화하지 않는다**(§6).
- 새 Architecture 책임·Layer·Component·Concept·Public Interface·Port·Kernel State 축/enum/타입을 추가하지 않고, §14를 승격하지 않으며(§14 항목 0건), §7 목록·§14.1 표·`BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·`ADC.md`를 변경하지 않는다(§9.2).
- `RFC-0022` §6이 개설한 F-9a~F-9f를 F-9b 우선으로 판정하고, 모든 판정이 "Kernel은 결정 9의 잔여 계약 표면을 §16.6 밖 별도 계약으로 규정하지 않는다"로 수렴한다.
- Gate (A)를 "부분 해소" → "해소"로 갱신하되(D-Gate-A), §14 승격·Gate (B)·(C)·LangGraph·구현·`IMPLEMENTATION_RULES.md` 해제를 hard gate로 유지한다(§7·§4.5).

**Next Step**: ADR Required — §8 지침으로 §16.6·`GLOSSARY.md`에 D-9a~D-Gate-A를 반영(Minor, v1.15 → v1.16, Frozen 유지). Commit/PR/Merge는 사용자 보고 후 별도 진행.

---

## 10. Traceability

| 문서 / 절 | ADC-0023과의 관계 | 정합성 |
|---|---|---|
| `RFC-0022` §6 (F-9a~F-9f) | 이 ADC가 판정하는 Boundary Question | D-9b·D-9a·D-9c·D-9d·D-9e·D-9f가 대응. §4 "가능한 갈래"는 입력이지 결정 아님 |
| `RFC-0022` §6 제외 목록·§7·§8 Non-goals | 이 ADC도 그대로 유지 | 결정 2·5·11·Gate (B)/(C)·LangGraph·Production·`IMPLEMENTATION_RULES` 해제 = §1.2·§7 Out of Scope |
| `RFC-0022` §9 (RFC-0022 → ADC-0023 번호) | 이 ADC의 번호 근거 | `ADC-0022`(결정 2·5·11)와 별개 주제. `RFC-0021`→`ADC-0022` 선례 계승 |
| `RFC-0019` §5 · G3 | 결정 9 공백 원인 = §14.1(별개·상위)의 2분할 | D-9b·D-9c가 계승 — 이 ADC가 새로 판단하지 않음 |
| `ADC-0019` §Q7 · §Decision 조건 5 · §Next Step 5 | 조건 이월의 해소 대상(결정 9) | 결정 9 해소로 조건 5의 "4공백" 부분 완료. 재검토 조건 (c)(Gate (B))·§14 scope 확장은 유지(§6 조건 1·6) |
| `ADC-0022` §D-9 · §D-11 (6) · §D-Gate-A | 이 ADC가 이어받는 정확한 범위 | D-9c·D-9d가 "입력 시그니처·결과 반환 타입"을 종결. D-Gate-A가 "부분 해소" → "해소" |
| `ADC-0020` §Q-B · §Q-C | D-9b·D-9a의 근거 | "Workflow Adapter ≠ Engine Adapter"(§Q-B), Adapter Contract 비-§14(§Q-C) 계승 |
| `ADC-0021` §8 Gate (A)/(B)/(C) · 진입 순서 | D-Gate-A가 Gate (A)를 "해소"로 갱신 | (A) 완료, (B)·(C)·Implementation Strategy·Scoped 해제는 hard gate 존속. §8 진입 순서 "(A)" 항목 완결 |
| `ADR-0010` (Gate (C) "부분 충족") | 무변경 | §6 조건 5 — 잔여 한계 (i)~(iii)·완전 discharge 미선언 유지 |
| `ADR-0011` / `BASELINE.md` v1.15 §16.6 "v2 공백의 현재 상태"·"Production 구현과의 관계" | D-9a~D-9f의 반영 대상(후속 ADR) | 문언은 §8이 "문단 갱신/1문장" 지침만. "결정 9 미해결" → "Resolved", 공백 원인 병기 정정, Gate (A) "부분 해소" → "해소" |
| `BASELINE.md` §7 System Boundary ("Engine 호출의 표준 인터페이스 제공") | D-9e의 한 축 | 무변경 — §7 = 책임 소재. 후속 ADR이 §16.6에 해석 1문장만 부기 |
| `BASELINE.md` §11 (Kernel 책임 ↔ 구현 후보) | D-9e | 무변경 — "Engine Gateway 채택 미결" 유지 |
| `BASELINE.md` §14 / §14.1 / §14.5 / §14.6 N-2 | D-9a·D-9c·D-9e·D-9f | 무변경 — §14 = Context 한정, #1·#3 = 미결. §14 항목 0건 추가(§6 조건 7) |
| `BASELINE.md` §16.2 Engine Adapter | D-9b — "결정 9와 별개 seam" | 무변경 — 설계 아님(§6 조건 10) |
| `BASELINE.md` §16.6 A-IN / A-IN(a) / A-OUT / Adapter Contract (a)(b)(d) / Reversibility 필수 불변조건 / 명칭 문단 | D-9a~D-9f의 반영 대상(후속 ADR) | 문언 무변경 — §8이 "1문장 부기" 지침만. (a)(b)(d)·Reversibility 문단 verbatim 유지 |
| `BASELINE.md` §16.7 (Workflow Kernel Module Defer) | 혼동 방지 | 무변경(§6 조건 10) |
| `ADC-0010` (Engine Caller 위치 Not Accepted) | D-9e의 제약 인용 | 전복·재개 없음 |
| `RFC-0002` §15-1 / §15-3 (Kernel 책임 후보 Task 전달 / Engine 호출) | D-9c·D-9e | 인용만 — "미결" 상태 유지 |
| `hqs/development/mvp/engine.py` · `workflow.py` | V12·V13 | 관찰만 — `call_engine(str)->str`, `run_mvp_0001(code)->dict`, 예외 비전파 |
| `hqs/development/stages/contracts.py` · `hqs/development/BASELINE.md` §Stage Data Contract | V14 | 관찰만 — `VerificationResult` = HQ-level Public Contract(§14와 별개) |
| `hqs/investment/engine_client.py` · `teams/stock_team.py` · `run.py` | V15 | 관찰만 — `call_engine` 재수출, wave orchestration ↔ `_run()` 물리 분리, `team.run(...)->dict` HQ별 시그니처 |
| `archive/v1/.../i_workflow_engine.py` · `docs/adr/0007-workflow-execution-model.md` 결정 9 | V1 | v1 원문 기준선 인용만 |
| `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 | §6 조건 8·§7 | 해제 없음 |
| `docs/decisions/adc/ADC.md` ADC-02 / `docs/architecture/core/ADC-0008` | §7 | 갱신·전복 없음(§Decision Rationale) |

---

## 11. Self-Review

- `ADC-0019`~`ADC-0022`가 확정하지 않은 것을 새로 결정했는가 — **결정 9의 잔여 계약 표면 세 조각의 disposition만**(D-9a·D-9c·D-9d) + F-9b seam 구분(D-9b) + F-9e 층위 정합(D-9e) + F-9f 최소 조건(D-9f). §14 승격·§14.1 #1·#3 Kernel 귀속·§16.2 seam 설계·Gate (B)/(C)·LangGraph·구현·`IMPLEMENTATION_RULES` 해제는 §7에 전부 Out of Scope.
- F-9b를 먼저 판정했는가 — **예**(§3.2·§4.1·D-9b가 §3.3·D-9a보다 앞). 결과: **별개 seam**(SB-1), 결정 9는 §14.1 #1 트랙만.
- v1 Workflow 실행 Engine ↔ v2 §16.2 Model/LLM Engine seam 구분을 유지했는가 — **예**(D-9b, §4.1, V9·V12·V15).
- 각 Decision이 BASELINE v1.15 + 코드 Evidence 기준인가 — **예**(V1~V18 인용). 새 요구사항 임의 생성 없음 — D-9a·D-9c·D-9d는 "Kernel이 규정하지 않는다"의 서술적 확정.
- 새 Kernel Concept/Contract/Port/enum/타입/Layer/Component를 추가했는가 — **아니오**(§9.2 전 항목). §14 항목 0건.
- 결정 2·5·11을 Resolved로 전제했는가 — **예**(§6 조건 4, §7, `ADC-0022`/`ADR-0011` 인용).
- Gate B/C·LangGraph·Production 구현·`IMPLEMENTATION_RULES` 해제를 판정했는가 — **아니오**(§1.2·§7·§6 조건 3·5·6·8, D-Gate-A "열지 않는 것").
- §14에 항목을 추가하거나 문안을 편집했는가 — **아니오**. D-9a는 "지위 = 비-§14, 승격은 상위 절차"만 기록. §8이 후속 ADR로 분리.
- `RFC-0022` Boundary Question + 선행 Governance Chain을 추적했는가 — **예**(§1 근거 위임 표, §10 Traceability).
- `BASELINE.md`·`GLOSSARY.md`·`ADR`·`IMPLEMENTATION_RULES.md`·`ADC.md`·CLAUDE.md·Production 코드를 수정했는가 — **아니오**. 이 ADC 파일 1건만 신규 작성(미커밋).
- 새 실험/PoC를 수행했는가 — **아니오**(§1.3) — `main` 병합 Governance 문서 + v1 Evidence + 현재 HQ 코드 관찰만.
- Architecture/Governance Review를 수행했는가 — **예**(§9), 판정 = PASS.
- Commit/PR/Merge를 했는가 — **아니오** — PASS 이후에도 사용자 보고를 먼저 한다.
