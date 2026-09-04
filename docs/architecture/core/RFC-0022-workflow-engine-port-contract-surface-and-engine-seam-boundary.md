# RFC-0022: v1 `ADR-0007` 결정 9의 잔여 계약 표면 — Workflow Adapter 호출 seam·입력 시그니처·결과 반환 타입과 §14.1의 경계 (ADC-0019 G3 / ADC-0022 D-9 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
G3 · §Decision 조건 5 · §Next Step 5, 그리고
`docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md`
§D-9가 "별도 Track"으로 명시 분리한 v1 `ADR-0007` 결정 **9**(`IWorkflowEngine`
Port / 입력 시그니처 / `WorkflowResult` 반환 타입). `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md`
§8이 이를 **Gate (A)**의 일부로 명명하고 "§14 승격·Production 구현 착수의
hard gate"로 유지 중이다. 결정 2·5·11은 `ADC-0022`로 Resolved됐으므로
(`ADR-0011`, BASELINE v1.15), 이 RFC는 Gate (A)에 남은 **결정 9의 잔여
계약 표면**만 정식 Boundary Question으로 연다.

**Evidence**: `archive/v1/docs/adr/0007-workflow-execution-model.md`(Accepted,
결정 9·11·12 원문), `archive/v1/packages/core/src/jarvis_core/ports/i_workflow_engine.py`
(v1 Port 실제 코드 — `run(team, dispatch) -> WorkflowResult`),
`docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md`
§5(v1 12개 결정의 v2 재해석 표) · G3, `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
§Q7 · G3 · §Decision 조건 5 · §Next Step 5,
`docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md`
§Q-B(명칭) · §Q-C(Adapter Contract의 비-§14 지위),
`docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md`
§3 · §Decision 4, `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md`
§8(Gate (A)/(B)/(C), 진입 순서), `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md`
§D-9 · §D-11 · §4.6(결정 9 분리 근거, Gate (A) "부분 해소"),
`docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md`,
`docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`(Engine
Caller 위치·책임 6개 후보 전수 검토 → Not Accepted),
`docs/architecture/core/RFC-0002-kernel-definition.md` §15(Kernel 책임 후보
1 "Task 전달 책임" · 3 "Engine 호출 책임"), `docs/architecture/baseline/BASELINE.md`
§7 · §11 · §14.1 · §14.6 N-2 · §16.2 · §16.6(v1.15),
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`hqs/development/mvp/engine.py`(`call_engine(prompt: str) -> str` — 단일
함수, Port/Adapter 아님) · `hqs/development/mvp/workflow.py`(`run_mvp_0001(code: str) -> dict`) ·
`hqs/development/stages/contracts.py`(`VerificationResult` = HQ 수준 Public
Contract, §14와 분리) · `hqs/development/IMPLEMENTATION_RULES.md` line
15·16(Engine Gateway / Engine Routing 구현 금지),
`hqs/investment/engine_client.py`(Dev HQ `call_engine` 물리적 재수출) ·
`hqs/investment/teams/stock_team.py` · `hqs/investment/run.py`(`team.run(company_label, raw_data_path, issue_dir) -> dict`
— HQ·팀별 시그니처). **새로운 실험·프로토타입·측정은 수행하지 않는다** —
이미 병합·기록된 v1 Evidence, v2 Governance 문서, 현재 `main` 코드 관찰만
인용한다.

> 본 RFC는 v1 결정 9의 v2 대안을 **설계하지 않는다**. `IWorkflowEngine`
> 대응 Port·Interface·Type·Contract를 정의하지 않고, §14 Public
> Responsibilities/Guarantees/Extension Points를 신설·수정하지 않는다.
> Scheduler / Engine Gateway Component를 설계하지 않는다. 결정 2·5·11을
> 재론하지 않는다(전제로만 사용). Gate (B)(`ADC-0019` 재검토 조건 (c)) ·
> Gate (C)(Reversibility v2 완전 검증) · LangGraph 채택 · Production 구현
> 착수 · `IMPLEMENTATION_RULES.md` 해제를 다루지 않는다. 코드·Baseline·
> ADC·ADR·CLAUDE.md를 수정하지 않는다. 이 RFC가 여는 것은 하나의 질문이다:
> **"결정 2·5·11이 실행 단위 입력·Lifecycle·State를 Resolved한 뒤 v1 결정
> 9에 남은 잔여 계약 표면(Port 존재·입력 시그니처·결과 반환 타입)은,
> §14.1이 '계약 범위 밖'으로 둔 'Task 전달 책임'·'Engine 호출 책임'과
> 어떤 관계이며, 어떤 형태로 닫혀야 `ADC-0019` 조건 5·`ADC-0021` §8
> Gate (A)를 여는가?"**

---

## 0. 이 RFC가 열린 이유

`RFC-0019` §5는 v1 `ADR-0007`의 12개 결정 중 4개(2·5·9·11)를 "v2 재설계가
필요한 진짜 공백"으로 식별하고, 그 공백 원인이 하나로 묶이지 않음을 명시했다.

- **결정 2·5·11**의 공백 원인은 **Team/Division 부재**다. → `RFC-0021` →
  `ADC-0022` → `ADR-0011`(BASELINE v1.15)로 **Resolved**됐다.
- **결정 9**(`IWorkflowEngine` Port)의 공백 원인은 Team 부재가 **아니다** —
  §14.1이 "Task 전달 책임"·"Engine 호출 책임"을 계약 범위 밖으로 두는
  데서 온다. `ADC-0019` G3은 이것을 "이 RFC/ADC 범위보다 상위의, 별도로
  이미 Open인 Kernel Public Contract 확장 질문"으로 규정했다.

`ADC-0019` §Next Step 5는 "v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계는 후속
ADR 또는 별도 RFC로 순서를 정해 다룬다 — 완료 전 Public Contract 승격·
구현 착수 불가"라고 지시했다. `RFC-0021` §6·§7·§8은 결정 9를 그 Boundary
Question에서 **의도적으로 제외**하며 "§14.1 트랙의 별개 RFC(또는 Kernel
Public Contract 확장 절차)가 다룰 사안"이라고 기록했다. `ADC-0022` §D-9는
"이 ADC는 결정 9를 판정하지 않는다. 입력 시그니처·결과 반환 타입·Public
Port 정의는 §14.1 'Task 전달 책임' 트랙(별도 RFC → ADC → ADR)이 다룬다.
그 착수 여부·시점은 이 ADC가 정하지 않는다"고 명시했다.

이 RFC는 그 지시를 따라 **결정 9의 잔여 계약 표면만** 정식 절차에 올린다.
"결정 2·5·11 ↔ 결정 9"의 2분할은 이 RFC가 새로 판단하는 것이 아니라
`RFC-0019` §5 · `ADC-0019` §Q7 · `RFC-0021` §5·§7 · `ADC-0022` §4.6이 이미
수행한 것을 그대로 계승한다.

## 1. Problem Statement

### 1.1 v1 결정 9가 확정한 것 (`archive/v1/docs/adr/0007-workflow-execution-model.md`)

결정 9 = **`IWorkflowEngine` Port (Domain Interface, Core 소속)**:

```python
class IWorkflowEngine(ABC):
    def run(self, team: Team, dispatch: TaskDispatch) -> WorkflowResult: ...
```

명문화된 계약은 세 조각뿐이다.

1. **Port 존재** — Core 소속 Domain Interface가 존재해야 한다. 결정 12가
   보강: Workflow는 Plugin이 아니므로 Registry/Discovery/Capability 없이
   Composition Root가 **direct construction**으로 하나만 주입한다. Core는
   구현체(LangGraph 등)를 알지 못한다(ADR-0003 결정 4 적용).
2. **입력 시그니처** — `Team`(실행 단위) + `TaskDispatch`(Kernel이 만든
   Task 전달 산물), 둘 다 기존 Core Domain Model.
3. **결과 반환 타입** — `WorkflowResult`(신규 Domain Model, 최소
   `status`/`error`, **예외를 던지지 않음** = Fail-Closed).

정확한 필드 구성·Cancellation API 형태는 "구현 세부, Implementation Plan"으로
명시 이연됐다.

### 1.2 결정 2·5·11 해소로 이미 v2에 닫힌 부분 (재론하지 않음)

| 결정 9 요소 | v2 처리 (전제) |
|---|---|
| 입력의 "`Team`(실행 단위)" 절반 | `ADC-0022` §D-2·§D-5 — 실행 단위 = **불투명 HQ 입력**, Division/Team 비의존, 소비할 Kernel 소유 Lifecycle 전이 부재 → Resolved |
| "예외를 던지지 않는다"(Fail-Closed) | §14.3 G-6 + §16.6 Adapter Contract **(b)** "실행 결과는 예외가 아닌 State 값" → 흡수됨 |
| Core가 구현체를 모름 | §16.6 Reversibility 필수 불변조건 + A-OUT → 흡수됨 |
| Workflow ≠ Plugin (결정 12) | §16.6 A-OUT "Registry/Discovery 일반화 미포함" + 실측 `TEAMS` 리터럴 딕셔너리 → 흡수됨 |
| `WorkflowStatus{SUCCESS,FAILURE,CANCELLED}` enum / State가 담는 정보 | `ADC-0022` §D-11 — Kernel enum·타입 미도입, State 내용·어휘 = HQ 도메인 → Resolved(서술 종결) |

### 1.3 결정 9에 **남은** 잔여 계약 표면

결정 2·5·11이 "실행 단위" 절반·Fail-Closed·Core-구현체 격리·non-Plugin을
닫은 뒤, 결정 9에 남은 것은 **계약 표면(§14) 질문 세 조각**이다.

- **Port 존재**: §16.6 Reversibility가 이미 "구현체 교체 시 Kernel·HQ 코드
  한 줄도 수정 안 됨" seam을 **요구**한다. 그러나 §16.6은 그 seam을
  "부속 명세(sub-specification)", "개념 수준"(`RFC-0019` §7 지위 계승),
  **비-§14**, "'Port'/'Public'/'Guarantee'/'Interface' 어휘를 쓰지
  않는다"로 못박았다(`ADC-0020` §Q-C, `ADR-0009` §Decision 4). v1의
  "Port가 존재해야 한다"가 v2에서 어떤 지위로 성립하는지가 미결이다.
- **입력 시그니처**: `Team` 절반은 Resolved. `dispatch: TaskDispatch`
  절반은 §14.1 #1("Task 전달 책임", 미결)에 묶여 있고, 실측은 HQ별
  (`run_mvp_0001(code)`, `team.run(company_label, path, dir)`).
- **결과 반환 타입**: `ADC-0022` §D-11이 "State가 담는 정보"는 서술로
  닫았으나, "실행 결과를 **호출자에게 돌려주는 반환 타입**(`WorkflowResult`
  대응)"은 §16.6이 명시적으로 "§14.1 트랙에 남는다"로 이연했다.

### 1.4 공백을 방치할 때의 위험

세 조각을 규정하지 않은 채 §16.6을 §14로 승격하거나 Production 구현에
착수하면, 어댑터를 "어떻게 호출하고 무엇을 돌려받는지"가 계약에 없는 상태로
seam이 고정된다. 반대로 이 조각들을 서둘러 §14 Public 항목으로 신설하면,
§14.1이 "1~3이 각각 판단되면 그때 이 계약이 확장된다"고 정한 절차와 §10
Out of Scope(Component Design)를 우회하게 된다. 이 RFC는 그 사이에서
**어느 형태의 해소가 절차상 정당한지**를 질문으로만 연다.

## 2. Evidence Summary — 이미 기록된 것만 인용

### 2.1 Governance 문서가 결정 9에 대해 확정해 둔 것

| 위치 | 문언(요지) |
|---|---|
| `BASELINE.md` §14.1 표 | "1. Task 전달 책임" = **미결, 계약 범위 밖** · "3. Engine 호출 책임" = **미결, 계약 범위 밖**. "1~3이 각각 판단되면 그때 이 계약이 확장된다" |
| `BASELINE.md` §11 표 | Task 전달 책임 → *Scheduler* / Engine 호출 책임 → *Engine Gateway* (구현 후보, **채택 미결**, "각 책임이 실제로 Kernel에 속하는지는 개별 RFC로 판단") |
| `BASELINE.md` §7 System Boundary | Jarvis OS 책임에 "Task/Event의 전달" · "**Engine 호출의 표준 인터페이스 제공 (Port/Adapter)**" 이미 등재 |
| `BASELINE.md` §14.6 N-2 | Scheduler 구현 = Non-Goal. 닫지 않는 질문: "Task 전달 책임이 Kernel에 속하는가 (RFC-0002 §15-1, **미결**)" |
| `BASELINE.md` §16.2 / §16.6 명칭 문단 | §16.2 = "Model/LLM Provider 호출 책임" = **Engine Adapter**. §16.6 Workflow Adapter는 "§16.2 Engine Adapter를 재명명하거나 흡수한 것이 아니라 그와 별개의 책임"이며 "'Engine' 프레이밍을 의도적으로 계승하지 않는다"(`ADC-0019` G2, `ADC-0020` §Q-B) |
| `BASELINE.md` §16.6 | "입력의 **구체 시그니처**(v1 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 이 Accept가 정하지 않는다 — §14.1 'Task 전달 책임' 트랙" / "반환 타입(`WorkflowResult` 대응)은 이 Accept 밖이며 §14.1 'Task 전달 책임' 트랙" / "결정 9는 미해결로 남는다 — 공백 원인이 Team 부재가 아니라 §14.1이 'Task 전달 책임'·'Engine 호출 책임'을 계약 범위 밖으로 두는 것 … 이 책임을 Kernel Public Contract(§14)로 승격하는 것은 결정 9 해소 이후에만 가능하다" |
| `ADC-0019` G3 | "결정 9의 v2 공백은 Team 부재가 아니라 §14.1이 'Task 전달 책임'을 계약 범위 밖으로 두는 데서 온다 — 별도로 이미 Open인 상위 질문" |
| `ADC-0022` §D-9 · §4.6 | "이 ADC는 결정 9를 판정하지 않는다. Port의 입력 절반(Team)은 결정 2·5와 같은 사유로 막혀 있었으나, `TaskDispatch`/`WorkflowResult` 계약 자체는 §14.1이라는 별개·상위 미결 사유를 갖는다." Gate (A) = "부분 해소(결정 2·5·11 Resolved / 결정 9 pending)" |
| `ADC-0021` §8 | 진입 순서: (A) 결정 2/5/9/11 해소 → (B) 재검토 조건 (c) → (C) Reversibility v2 재현 → Implementation Strategy 세부 ADC → Scoped 해제 ADR → 구현. "현재 2·3·4·5 중 충족된 것은 없다" |
| `ADC-0010` | "Engine Caller의 위치와 책임" — `call_engine()`을 호출하고 결과를 주입하는 caller의 위치·책임 6개 후보 전수 검토 → **Not Accepted**(현재 Evidence로 Accept 가능한 것 없음) |

### 2.2 현재 `main`(`3e36e63`) 코드가 보이는 것 — 관찰만

**"Engine 호출"은 Port/Adapter가 아니다**:
- `hqs/development/mvp/engine.py`: 단일 함수 `call_engine(prompt: str) -> str`,
  `subprocess`로 `claude` CLI 호출. `IMPLEMENTATION_RULES.md` line 15
  "Engine Gateway(Port/Adapter 추상화) 구현 금지" · line 16 "Engine
  Routing 구현 금지"가 명시적으로 막는다.
- `hqs/investment/engine_client.py`: `sys.path` 주입으로 Dev HQ의
  `call_engine`을 **물리적 재수출**. "새 Gateway/Adapter를 만들지 않는다."

**"Task 전달"은 Kernel 경계를 넘는 `dispatch` 객체가 없다**:
- Dev HQ: `run_mvp_0001(code: str) -> dict`(Task 1→2 직접 함수 호출
  하드코딩), Stage 01→05 고정 선형 단일 패스. `IMPLEMENTATION_RULES.md`
  line 9/10/13/14가 Workflow Parser/Scheduler/orchestration/Stage 재진입
  금지.
- Investment HQ: `team.run(company_label, raw_data_path: Path, issue_dir: Path) -> dict`
  — **HQ·팀별 시그니처**. `run.py`의 `TEAMS` = 리터럴 딕셔너리.
- 유일하게 계약처럼 보이는 것은 Dev HQ `VerificationResult.status ∈
  {PASS,FAIL,INCONCLUSIVE,SKIPPED}`(`hqs/development/stages/contracts.py`) —
  그러나 이는 **HQ 수준 Public Contract**로 §14와 명시적으로 분리돼 있다.

이 관찰은 이 RFC가 판정 재료로 인용할 뿐, 코드를 변경 대상으로 삼지
않는다(§7).

### 2.3 용어 위험 — v1 "Engine" ≠ v2 "Engine"

v1 결정 9의 `IWorkflowEngine`에서 "Engine"은 **workflow 실행 엔진**(그래프
진행·병렬 조립)을 뜻했다. v2에서 "Engine 호출 책임"(§14.1 #3) · "Engine
Gateway"(§11) · §16.2 "Engine Adapter"는 모두 **Model/LLM Provider
호출**(`call_engine()` 계보)을 뜻한다. §16.6은 이 프레이밍 충돌을 인지하고
"'Engine' 프레이밍을 의도적으로 계승하지 않는다"고 적었으나, "v2 공백의
현재 상태" 문단은 결정 9의 공백 원인을 "'Task 전달 책임'·'**Engine 호출
책임**'을 계약 범위 밖으로 두는 것"이라 하여 §14.1 두 행 모두에 연결한다.
결정 9가 실제로 **하나의 seam 질문인지, 두 개(Workflow Adapter seam /
§16.2 Engine Adapter seam)로 쪼개지는지**가 정리되지 않았다.

## 3. v1 개념과 v2의 불일치 정리

| v1 개념 | v1에서의 지위 | v2에서의 상태 | 이 RFC와의 관계 |
|---|---|---|---|
| **`IWorkflowEngine`** | Core 소속 Domain Interface, direct construction | §16.6 Reversibility seam은 존재하나 "부속 명세 / 개념 수준", **비-§14**. Public Port 정의 = "이 Accept 밖" | seam을 §14 항목으로 승격할지 / 비-§14로 존속시킬지 / HQ별 관례로 둘지(F-9a) |
| **`IWorkflowEngine`의 "Engine"** | workflow 실행 엔진 | v2 "Engine 호출 책임"·"Engine Adapter"(§16.2)는 Model/LLM 호출을 지칭 — 다른 seam | 결정 9가 하나의 질문인지 두 개로 쪼개지는지(F-9b) |
| **입력 `team`** | Core Domain Model | `ADC-0022` §D-2·§D-5 → 불투명 HQ 입력으로 **Resolved** | 재론 안 함(§7) |
| **입력 `dispatch: TaskDispatch`** | Kernel의 Task 전달 산물 | §14.1 #1 "Task 전달 책임" = 미결. 실측 HQ별 시그니처 | Kernel 표준 입력 형태가 있는가 / 영구 HQ별인가(F-9c) |
| **반환 `WorkflowResult`** | `WorkflowStatus` 포함 Domain Model, 예외 없음 | 값-표현·예외 비전파 = §14.3 G-6 + Adapter Contract (b)로 흡수. **반환 타입 자체**는 §14.1 트랙 | 반환 타입이 Kernel envelope / caller-owned Checkpoint 값 / HQ 타입 중 무엇인가(F-9d) |
| **§7 "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)"** | — (v2 문서) | §14.1은 "Engine 호출 책임 = 미결, 계약 범위 밖". `ADC-0010`은 Engine Caller 위치를 Not Accepted | "책임 소재"(§7)와 "계약 표면"(§14.1)의 층위 관계(F-9e) |
| **Gate (A)의 결정 9 절반** | — | `ADC-0021` §8 · `ADC-0019` 조건 5가 "결정 9 해소 이후에만 §14 승격·구현" | "해소"의 최소 조건이 무엇인가(F-9f) |

## 4. 계약 표면별 v2 공백 분석

### 4.1 Port 존재 — seam의 지위와 정체

**v1이 확정한 것**: Core 소속 `ABC`, direct construction, Core는 구현체를
모름.

**v2 상태 — seam은 있으나 지위가 비-§14**: §16.6 Reversibility 필수
불변조건이 "어떤 구현체를 제거하고 다른 구현체(최소한 순차 함수 호출)로
교체해도 Kernel·HQ 코드 한 줄도 수정되지 않아야 한다"를 요구하므로, 교체
가능한 seam은 **개념적으로 이미 존재**한다. 그러나 §16.6 Adapter Contract는
그 seam을 "§16.6 A-IN 부속 명세이며 그 위의 새 계층이 아니다", "Public
Surface가 아니고", "'Port'/'Public'/'Guarantee'/'Interface' 어휘를 쓰지
않으며, §14에는 어떤 항목도 추가되지 않는다"로 못박았다(`ADC-0020` §Q-C,
`ADR-0009` §Decision 4).

**잔여 공백**: v1 결정 9의 "Port가 존재해야 한다"는 계약이 v2에서 (a) §14
Extension Point(X-*)로 **승격**되는지, (b) §16.6 비-§14 개념 수준 부속
명세로 **영구 존속**하는지, (c) HQ별 관례(§7 도메인 내용)로 **위임**되는지가
미결이다. §16.6·`ADC-0019` 조건 5·`ADC-0021` §8이 "§14 승격은 결정 9 해소
이후"라고 전제하므로, 이 세 갈래 중 어느 것이 "해소"에 해당하는지도 함께
미결이다.

### 4.2 입력 시그니처

**v1이 확정한 것**: `run(team, dispatch: TaskDispatch)`.

**v2 상태**: `team`(실행 단위) 절반은 `ADC-0022`로 Resolved — 어댑터는
불투명한 HQ 입력을 받고 Kernel은 그 형태를 타입하지 않는다. `dispatch`
절반은 v1에서 "Kernel의 Task 전달 책임 산물"이었고, §14.1 #1이 "Task 전달
책임"을 계약 범위 밖으로 둔다. 실측은 HQ마다 다르다(`run_mvp_0001(code)`,
`team.run(company_label, path, dir)`).

**잔여 공백**: 실행 메커니즘 호출의 입력이 (i) Kernel이 규정하는 표준
형태를 갖는지, (ii) 실측대로 **영구히 HQ별**인지가 미결이다. (ii)가
결론이라면 "§14.1 #1 'Task 전달 책임'은 Kernel 책임이 아니다"라는 **명시적
부정**으로 §14.1 표의 해당 행이 닫히는지, 아니면 미결로 남되 결정 9와는
분리되는지도 함께 판단 대상이다.

### 4.3 결과 반환 타입

**v1이 확정한 것**: `-> WorkflowResult`(≥ `status`/`error`, 예외 없음).

**v2 상태 — 형식은 흡수, 타입은 공백**: 실행 결과를 "예외가 아닌 값으로"
표현하는 **형식 제약**은 §14.3 G-6 + §16.6 Adapter Contract (b)가 담는다.
그 값의 **내용·어휘**는 `ADC-0022` §D-11이 "HQ 도메인 책임, Kernel이
규정하지 않음"으로 종결했다. 그러나 "실행 결과를 호출자에게 **어떤 타입의
무엇으로 돌려주는가**"는 §16.6이 명시적으로 "§14.1 트랙에 남는다"로
이연했다.

**잔여 공백**: 반환 타입이 (i) Kernel-typed envelope(v1 `WorkflowResult`의
Kernel 수준 대응), (ii) caller-owned Checkpoint 값(Adapter Contract (a))에
흡수되어 별도 반환 타입이 없음, (iii) HQ 정의 타입(`VerificationResult`
선례처럼 HQ Public Contract) 중 무엇인지가 미결이다.

### 4.4 세 조각에 공통으로 걸린 정합성·gate 문제

- **§7 ↔ §14.1**: §7이 "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)"을
  Jarvis OS 책임으로 이미 등재하는데 §14.1은 "미결, 계약 범위 밖"이다.
  §7의 서술이 §14.1보다 앞서가 있는 것인지, 아니면 §7은 "책임 소재",
  §14.1은 "계약 표면"이라는 서로 다른 층위인지, `ADC-0010`(Engine Caller
  위치 Not Accepted)이 이 관계에 어떤 제약을 주는지가 미결이다.
- **gate 개방 조건**: §16.6·`ADC-0019` 조건 5·`ADC-0021` §8이 "결정 9
  해소 이후에만 §14 승격·Production 구현 착수 가능"이라 한다. 결정 9의
  "해소"가 §14 확장 / 명시적 부정 결론 / Workflow Adapter에 한정한 좁은
  비-§14 seam 계약 중 무엇으로도 성립하는지 — 즉 gate를 여는 **최소
  조건**이 무엇인지가 미결이다.

## 5. §16.6·§14가 이미 부분적으로 메운 것 — 이 RFC가 새로 만들지 않는 것

| 계약 표면 | §16.6/§14가 이미 담은 것 | 이 RFC가 여는 것 |
|---|---|---|
| Port 존재 | Reversibility 필수 불변조건 + Adapter Contract (비-§14, 개념 수준) | 그 seam의 §14 승격 / 비-§14 존속 / HQ 위임 중 무엇인지 |
| 입력 시그니처 | `team` 절반 = 불투명 HQ 입력(`ADC-0022` §D-2·§D-5) | `dispatch` 절반 = Kernel 표준 형태인지 영구 HQ별인지, §14.1 #1의 처리 |
| 결과 반환 타입 | 값-표현·예외 비전파 = §14.3 G-6 + Adapter Contract (b); 내용·어휘 = HQ 도메인(`ADC-0022` §D-11) | 호출자가 결과를 돌려받는 **타입**(Kernel envelope / Checkpoint 값 / HQ 타입) |

이 표는 이 RFC의 범위를 **좁힌다**: 세 조각 모두 "완전 공백"이 아니라
"부분 흡수 + 명시되지 않은 잔여"이며, 이 RFC는 그 잔여만 Boundary
Question으로 올린다. 어떤 조각에 대해서도 해소 형태를 **선택하지 않는다**.

## 6. Boundary Question

**v1 `ADR-0007` 결정 9(`IWorkflowEngine` Port / 입력 시그니처 /
`WorkflowResult` 반환 타입)의 v2 잔여 계약 표면 — 결정 2·5·11이 실행 단위
입력·Lifecycle·State를 Resolved한 뒤 남은 것 — 은, §14.1이 "계약 범위
밖"으로 둔 "Task 전달 책임"·"Engine 호출 책임" 및 §7이 "Jarvis OS
책임"으로 등재한 "Engine 호출의 표준 인터페이스 제공 (Port/Adapter)"와
어떤 관계이며, Port 존재·입력 시그니처·결과 반환 타입 각각이 어떤 형태로
닫혀야 `ADC-0019` §Decision 조건 5·`ADC-0021` §8 Gate (A)를 여는가?**

세 계약 표면으로 나뉘고, 여섯 하위 facet으로 세분된다(후속 ADC가 각각
판정하며, **이 RFC는 어떤 facet에 대해서도 해결책을 선결정하지 않는다**).

### 표면 1 — Port 존재

- **F-9a — seam의 §14 지위**: §16.6 Reversibility가 이미 요구하는 "구현체
  교체 시 Kernel·HQ 무수정" seam은 (a) §14 Kernel Public Contract의
  Extension Point(X-*)로 승격되어야 하는가, (b) §16.6 부속 명세의 비-§14
  개념 수준 지위(`ADC-0020` §Q-C, `ADR-0009` §Decision 4)로 영구 존속하는가,
  (c) §7 도메인 내용으로서 HQ별 관례에 위임되는가? v1 결정 9의 "Port가
  존재해야 한다"는 계약은 이 셋 중 무엇으로 v2에서 성립하는가?
- **F-9b — "Engine" seam의 정체**: v1 `IWorkflowEngine`이 하나로 묶었던
  "workflow 그래프 실행 호출"과, v2 §14.1 #3 "Engine 호출 책임" · §11
  "Engine Gateway" · §16.2 "Engine Adapter"(Model/LLM Provider 호출)는
  **같은 seam인가 다른 seam인가?** §16.6 명칭 문단이 "별개 책임"이라
  했다면, 결정 9는 실제로 **두 개의 분리된 질문**(Workflow Adapter 호출
  seam / §16.2 Engine Adapter seam)으로 나뉘는가, 아니면 하나의 seam
  질문인가?

### 표면 2 — 입력 시그니처

- **F-9c — 입력의 소유**: 실행 메커니즘 호출의 입력은 Kernel이 규정하는
  **표준 형태**를 갖는가(v1 `TaskDispatch`의 v2 대응물이 필요한가), 아니면
  실측(`run_mvp_0001(code)`, `team.run(company_label, path, dir)`)대로
  **영구히 HQ별**인가? 후자라면 §14.1 #1 "Task 전달 책임"은 "Kernel 책임
  아님"으로 명시적으로 닫히는가, 미결로 남되 결정 9와 분리되는가?
  (`team`(실행 단위) 절반은 `ADC-0022`로 Resolved됐으므로 재론 대상 아님 —
  이 facet은 `dispatch` 절반만 다룬다.)

### 표면 3 — 결과 반환 타입

- **F-9d — 반환 타입의 소재**: 실행 결과가 호출자에게 돌아가는 타입은
  (i) Kernel-typed envelope(v1 `WorkflowResult`의 Kernel 수준 대응),
  (ii) caller-owned Checkpoint 값(§16.6 Adapter Contract (a))에 흡수되어
  별도 반환 타입이 없음, (iii) HQ 정의 타입(`hqs/development/stages/contracts.py`
  `VerificationResult`가 보인 HQ Public Contract 선례) 중 무엇인가?
  `ADC-0022` §D-11이 "State가 담는 정보"를 서술로 닫은 것과 이 반환 타입
  질문은 어떻게 분리되는가?

### 표면 전반 — 정합성과 gate

- **F-9e — §7 ↔ §14.1 층위**: §7이 "Engine 호출의 표준 인터페이스 제공
  (Port/Adapter)"을 Jarvis OS 책임으로 이미 명시하는데 §14.1이 "Engine
  호출 책임 = 미결, 계약 범위 밖"인 것을 어떻게 정합적으로 읽는가? §7은
  "책임 소재"만, §14.1은 "계약 표면"만 말하는 다른 층위인가, 아니면 §7의
  서술이 §14.1보다 앞서간 것으로 조정이 필요한가? `ADC-0010`(Engine
  Caller 위치·책임 6개 후보 Not Accepted)은 이 관계에 어떤 제약을 주는가?
- **F-9f — "해소"의 최소 조건**: §16.6 · `ADC-0019` 조건 5 · `ADC-0021`
  §8이 "결정 9 해소 이후에만 §14 승격·Production 구현 착수 가능"이라
  한다. 결정 9의 "해소"란 (a) §14 확장(Task 전달/Engine 호출 책임을
  계약에 편입), (b) "이 책임들은 Kernel 계약이 아니다"라는 명시적 부정
  결론, (c) Workflow Adapter에 한정한 좁은 비-§14 seam 계약만 — 중
  무엇으로도 성립하는가? gate를 여는 최소 조건은 무엇인가?

### 이 Boundary Question이 명시적으로 제외하는 것

- **v1 결정 2·5·11** — `ADC-0022` → `ADR-0011`(BASELINE v1.15)로 Resolved.
  이 RFC는 전제로만 사용하고 재론하지 않는다.
- **§14 Public Responsibilities/Guarantees/Extension Points의 실제
  신설·문안** — 이 RFC는 질문만 연다. 신설은 후속 ADC → ADR의 몫이며,
  §14.7 변경 규칙(RFC → ADC → ADR → Baseline)을 그대로 따른다.
- **Scheduler / Engine Gateway Component 설계** — §10 Out of Scope 유지.
  §11 표의 "구현 후보"는 예시이며 채택 여부는 이 RFC가 정하지 않는다.
- **Gate (B)**(`ADC-0019` 재검토 조건 (c) — 다른 계보 또는 v2 프로덕션
  관찰), **Gate (C)**(Reversibility 필수 불변조건의 v2 완전 검증),
  **LangGraph 채택 여부·구현 전략·Checkpointer 백엔드** — 별개 hard
  gate이며 이 트랙의 입력이 아니다.
- **Production 구현 착수** · **`IMPLEMENTATION_RULES.md` line
  9/13/14/15/16/19의 전면·Scoped 해제** — 결정 9 해소가 gate의 일부일
  뿐, 이 RFC가 해제를 제안하지 않는다.
- **§16.6 A-IN/A-OUT 범위 변경, Adapter Contract (a)(b)(c)(d) 재정의** —
  이 RFC는 §16.6 문언을 수정 대상으로 삼지 않는다.

## 7. Out of Scope

- v1 결정 9의 v2 대안 **설계**(구체 Port·Interface·Type·필드·시그니처·
  다이어그램). 이 RFC는 Boundary Question만 연다.
- 결정 2·5·11의 재론·재설계(`ADC-0022`로 Resolved — 전제로만 사용).
- §14 Public Responsibilities/Guarantees/Extension Points 신설·수정,
  §14.1 표의 행 상태 변경, §7·§11·§16.2·§16.6 문언 수정.
- Scheduler / Engine Gateway / Task Dispatcher 등 Component의 존재·위치·
  책임·Interface 판정(§10 Out of Scope, `ADC-0010`·`ADC-0012` 상태 인용만).
- `ADC-0019` §Decision 조건 1~6, 재검토 조건 (c)(= Gate (B)), Reversibility
  필수 불변조건(= Gate (C) 트랙)의 재판단.
- `ADC-0021` §8 진입 순서 (B)·(C)·Implementation Strategy 세부 ADC·
  Scoped 해제 ADR의 재정의.
- LangGraph 채택 여부·구현 전략·Checkpointer 백엔드.
- (c) reducer 규약의 규범화·배치·HQ 구속 판정(`ADC-0022` §D-11c로 "배치 =
  HQ 스키마"만 확정, 나머지는 `ADC-0020` §Q-D Defer 그대로).
- `docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐, Open) · `ADC-0008`
  (Not Accepted)의 재판단·전복.
- Production 코드 변경(`core/`, `hqs/`, `dashboard/`), `IMPLEMENTATION_RULES.md`
  해제, 이 RFC 파일 자체를 제외한 `docs/architecture/`·`docs/decisions/`
  파일.
- Multi-HQ, 자연어 요청 분해(`ADC-0018`, Defer) 범위로의 확장.

## 8. Non-goals

- 이 RFC는 Port 존재·입력 시그니처·결과 반환 타입 중 어느 것도 "v2에서
  필요/불필요"라고 **미리 결론짓지 않는다** — F-9a·F-9c·F-9d가 "§14
  승격", "명시적 부정", "HQ 위임" 등 서로 다른 결말로 종결될 가능성을
  모두 열어두며, 그 판정은 후속 ADC(`ADC-0023`)의 몫이다.
- 이 RFC는 Governance v2 Rule B 충족을 주장하지 않는다 — 결정 9의 잔여
  계약 표면은 Evidence 축적 문제가 아니라 §14.1·§7·§16.6 사이의 정합
  문제이므로 Rule B와 직접 관계가 없다. Gate (B)는 별개로 유지된다.
- 이 RFC는 §14 승격 gate를 여는 것이 **아니다** — `ADC-0019` 조건 5가
  "결정 9 해소 전 §14 승격 불가"로 유지하며, 이 RFC는 결정 9를 절차에
  올려 **해소를 시작**할 뿐이다. F-9f의 "최소 조건" 판정 자체도 후속
  ADC의 몫이다.
- 이 RFC는 `ADC-0010`(Engine Caller 위치 Not Accepted)을 전복하거나
  재개하지 않는다 — F-9e에서 그 결론이 §7 ↔ §14.1 관계에 주는 제약을
  **인용**할 뿐이다.
- 이 RFC는 결정 9 해소의 착수 시점·우선순위를 정하지 않는다 — Gate (A)의
  나머지 절반이라는 사실만 기록하며, (B)·(C)와의 착수 순서는 `ADC-0021`
  §8이 "이 ADC가 정하지 않는다"고 한 그대로 열려 있다.

## 9. Governance Chain / 번호 관계

- **선행**: `RFC-0019`→`ADC-0019`→`ADR-0008`(§16.6 존재 Accept, 조건 5로
  결정 2/5/9/11 이월) · `RFC-0020`→`ADC-0020`→`ADR-0009`(명칭 + Adapter
  Contract (a)(b)(d)의 비-§14 지위) · `ADC-0021`(구현 전략 프레이밍, §8이
  결정 2/5/9/11을 Gate (A)로 명명) · `RFC-0021`→`ADC-0022`→`ADR-0011`
  (결정 **2·5·11** Resolved, BASELINE v1.15, Gate (A) "부분 해소").
- **이 RFC**: Gate (A) 중 `ADC-0022`가 "별도 Track"으로 남긴 **결정 9의
  잔여 계약 표면**(Port 존재·입력 시그니처·결과 반환 타입)만 정식 Boundary
  Question으로 개설. "결정 2·5·11 ↔ 결정 9"의 2분할은 `RFC-0019` §5 ·
  `ADC-0019` §Q7 · `RFC-0021` §5·§7 · `ADC-0022` §4.6이 이미 수행한 것을
  계승한다.
- **번호 관계 주의**: 이 저장소 core 체인의 RFC-N ↔ ADC-N 1:1 짝은
  `ADC-0021`(`RFC-0020` §8.2를 RFC pairing으로 삼음, `ADC-0021` §1.4)과
  `RFC-0021`→`ADC-0022`(`ADC-0021`과 주제가 다른 별개 문서)에서 이미
  어긋났다. 따라서 **`RFC-0022`(이 문서)의 후속 ADC는 `ADC-0023`**이다 —
  `ADC-0022`(결정 2·5·11 Resolution)와는 주제가 다른 별개 문서이며,
  혼동을 막기 위해 파일명·제목에 주제를 명시했다.
- **후속**: 이 RFC가 Accept(개설 타당) 판정되면 → `ADC-0023`(신설)이
  F-9a~F-9f를 판정 → 필요 시 ADR(예상 `ADR-0012`) → `BASELINE.md`
  §14/§14.1(및 필요 시 §7·§11·§16.2·§16.6) Update. 이 RFC 자체는 그
  판단을 내리지 않는다.

## 10. Next Step

후속 ADC(신설 예정, **`ADC-0023`**)에서 다음을 판단하도록 제안한다.

1. §6 Boundary Question(결정 9의 잔여 계약 표면)을 지금 정식 절차로 여는
   것이 타당한지, 아니면 더 상위의 결정(예: §14.1 #1·#3 "Task 전달
   책임"·"Engine 호출 책임"의 Kernel 귀속 여부 자체)이 먼저여야 하는지.
2. 타당하다면 — **F-9a**: §16.6 Reversibility seam의 §14 지위(승격 / 비-§14
   존속 / HQ 위임)를 확정. **F-9b**: 그 seam이 §16.2 Engine Adapter와
   같은지 다른지, 결정 9가 하나의 질문인지 둘로 쪼개지는지 확정.
3. **F-9c**: 입력의 `dispatch` 절반이 Kernel 표준 형태인지 영구 HQ별인지,
   §14.1 #1의 처리(계약 편입 / "Kernel 아님"으로 닫기 / 미결 유지·분리)를
   확정.
4. **F-9d**: 결과 반환 타입이 Kernel envelope / caller-owned Checkpoint
   값 흡수 / HQ 타입 중 무엇인지 확정.
5. **F-9e**: §7 "표준 인터페이스 제공" ↔ §14.1 "계약 범위 밖"의 층위
   관계를 `ADC-0010` 제약과 함께 정리. **F-9f**: gate를 여는 "결정 9
   해소"의 최소 조건을 정의.
6. 각 facet의 판정이 `BASELINE.md` 어느 절(§14 / §14.1 / §7 / §11 /
   §16.2 / §16.6)에 어떤 granularity(§14.1 표의 행 상태 변경 / Minor
   문단 추가 / 별도 항목)로 반영되는지, ADR이 필요한지를 정한다.
7. 결정 2·5·11(Resolved)·Gate (B)·Gate (C)·LangGraph·Production 구현은
   이 ADC가 다루지 않음을 재확인한다.

이 RFC 자체는 위 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 진행한다.

## 11. Self Review

- Evidence만 사용했는가 — **Pass**. v1 `ADR-0007`(Accepted 그대로 인용) ·
  `i_workflow_engine.py`(v1 코드) · `RFC-0019` §5 · `ADC-0019`/`ADC-0020`/
  `ADC-0021`/`ADC-0022`/`ADR-0009`/`ADR-0011`/`ADC-0010` · `RFC-0002` §15 ·
  `BASELINE.md`(v1.15) · `ARCHITECTURE_GOVERNANCE.md` · `hqs/` 코드 관찰만
  인용했다. 새 실험·프로토타입·측정은 없다.
- 결정 9의 v2 대안을 설계했는가 — **아니오**(§7). §4는 공백을 기술하고
  §6은 질문만 연다. §4.1~§4.3의 "가능한 갈래"는 열거이지 선택이 아니다.
- 잔여 계약 표면을 Port 존재·입력 시그니처·결과 반환 타입으로 분리했는가 —
  **예**(§1.3, §4, §6 표면 1·2·3).
- F-9a~F-9f를 하위 facet으로 포함하되 해결책을 선결정하지 않았는가 —
  **예**(§6). 각 facet은 (a)/(b)/(c) 갈래를 병렬로 두고 판정을 `ADC-0023`에
  위임한다.
- v1 "Engine"과 v2 §16.2 "Engine Adapter"의 seam 동일성을 별도 질문으로
  다뤘는가 — **예**(§2.3, §3 표, F-9b).
- 결정 2·5·11 / Gate (B)/(C) / LangGraph / Production 구현을 Out of Scope로
  명시했는가 — **예**(§6 제외 목록, §7, §8).
- §7 "표준 인터페이스 제공" ↔ §14.1 "계약 범위 밖" 관계를 Boundary
  Question에 포함했는가 — **예**(§4.4, F-9e).
- 새 Port·Interface·Type·Contract를 만들었는가 — **아니오**. §14 항목을
  추가·수정하지 않았고, seam을 명명하지 않았다.
- Production 코드·Baseline·ADC·ADR·CLAUDE.md를 수정했는가 — **아니오**.
  이 RFC 파일 하나만 신규 작성했다.
- `ADC-0019` 조건 5·Gate (A)를 약화했는가 — **아니오**(§8) — 결정 9를
  절차에 올려 해소를 **시작**할 뿐, §14 승격 gate는 그대로다.
- 번호 관계(RFC-0022 ↔ ADC-0023, ADC-0022와 별개 주제)를 명시했는가 —
  **예**(§9).
- RFC-0021과 동일한 granularity·Governance 형식(Status/Author/대상 →
  Evidence → 범위 blockquote → §0~§11)을 따랐는가 — **예**.
