# RFC-0043: Execution History & Evidence Persistence Architecture

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Dev HQ Command Center — Execution Boundary Review 후속)
**대상**: Development HQ Workflow(`hqs/development/workflow.py`) 실행 결과를
Command Center(`projects/dashboard-shell-mvp/devhq-command-center/`)가 조회할 수
있으려면 필요한 **Execution State/History/Evidence Persistence**의 Boundary Question.
`docs/decisions/adc/ADC.md` ADC-02("Runtime 개념의 존폐", Open·NOW)와 그 Scoped
후속 트랙(`ADC-0013`~`ADC-0025`) 전부를 조사 근거로 삼되, 이 RFC 자체는 그중
어느 것도 재론·재개하지 않는다.
**Evidence 범위**: 새 실험/Prototype을 만들지 않았다 — 이 RFC는 기존 저장소
문서·코드의 사실 확인만으로 구성된다.

> 본 RFC는 Runtime/Scheduler/Workflow Engine/Execution History Store/Evidence
> Store 중 어느 것도 설계·구현하지 않는다. ADC-02를 비롯한 어떤 Open/Resolved
> Decision도 재론·재개·확정하지 않는다. Command Center UI/코드도 변경하지
> 않는다. 이 RFC는 문제, 제약, Option, Trade-off, Decision Candidate까지만
> 다룬다 — 최종 Architecture 확정은 후속 ADC → ADR의 책임이다.

---

## 1. Status

Proposed. 후속 ADC가 아직 열리지 않았다.

## 2. Context

`Dev HQ Command Center — Execution Boundary Review`(직전 조사, 코드 변경 없음)가
다음을 실측으로 확인했다:

- `hqs/development/workflow.py::run_workflow()`는 Stage 01→05를 순서대로 호출하는
  **동기 함수**이며, 실행 결과를 dict로 리턴할 뿐 어디에도 저장하지 않는다.
- `hqs/development/cli.py`는 그 결과를 **stdout에 출력**하고 종료한다. 파일/DB
  쓰기가 전혀 없다.
- `serve_dashboard.py`의 POST 경로 3개(`/api/command`, `/api/llm-command`,
  `/api/openrouter-command`) 중 어느 것도 `run_workflow`/`cli.py`를 참조하지
  않는다 — Browser에서 Workflow를 트리거할 기존 경로가 없다.
- `hqs/development/`에는 `hqs/investment/checkpoint.py`(`Checkpointer`/`run_step`)에
  대응하는 어떤 persistence 컴포넌트도 없다(`grep -rl "checkpoints\|manifest.json"
  hqs/development/` → 결과 없음).
- Command Center Mock Task(`#039`~`#042`)와 실제 Workflow 실행 사이에는
  **Task → Workflow Execution mapping이 없다**(Task ID 개념 자체를
  `run_workflow()`가 모른다).

이번 RFC는 이 사실 위에서, Command Center의 Task-centered UX가 요구하는
Execution State/History/Evidence를 실제로 제공하려면 무엇이 필요한지, 그리고
그것이 기존 Architecture(특히 `docs/architecture/baseline/BASELINE.md` §16
Kernel Modules)와 어떻게 맞물리는지를 분석한다.

## 3. Problem Statement

Command Center는 이미 다음을 UI Contract로 요구한다(`data/adapters/adapters.js`,
`data/mock/*.json` 구조):

- Task 단위의 `status`(RUNNING/COMPLETED/FAILED/...), `progress`(overall/workflow/
  tasks/verification, 4개 독립 축), `stages`(5단계, 각 startedAt/completedAt/
  duration/status)
- Task 단위의 `Changes`/`Tests`/`Evidence`(checklist + verification + artifacts)

이 구조가 실제 데이터를 갖추려면 최소한 다음이 실제로 존재해야 한다: (1)
실행을 식별하는 Identity, (2) 그 실행이 지금 어느 Stage에 있는지 조회 가능한
State, (3) 끝난 실행을 나중에 다시 볼 수 있는 History, (4) Stage 05
`VerificationResult`를 실행 종료 후에도 참조할 수 있는 Evidence 저장.

현재 이 네 가지는 **전부 존재하지 않는다**(Q4/Q5, 직전 조사). 이 RFC는 "그것들을
지금 만든다"가 아니라 "그것들을 만들려면 무엇과 충돌하고 무엇을 먼저 결정해야
하는가"를 분석한다.

## 4. Current Architecture (조사 결과)

### 4.1 Development HQ 측

| 문서/코드 | 사실 |
|---|---|
| `hqs/development/BASELINE.md` | "Not Included"에 **Runtime 명시**. "Development HQ는 Architecture Decision을 소유하지 않는다." |
| `hqs/development/HANDOVER.md` | "MVP 범위를 벗어난 기능(Multi-HQ, Multi-Engine, **영속 저장소**, 백그라운드/분산 실행) 추가" 금지 명시 |
| `hqs/development/IMPLEMENTATION_RULES.md` | Workflow Parser/Scheduler/Registry/Runtime/Engine Gateway(추상화)/Policy/Memory Service/Event Bus 구현 금지. Stage 재진입(Retry/Re-entry)·조건부 Stage 실행 구현 금지 |
| `hqs/development/stages/contracts.py` | Stage 간 **필수 키 존재**만 검증(`ContractViolation`). 실행 이력을 저장하지 않음. `KNOWN_CHECK_NAMES`/`required_checks`/`check_results`는 Development HQ Baseline이 **Public Contract**로 못박음(RFC→ADC→ADR 없이 확장 불가) |
| `hqs/development/workflow.py` | Stage 01→05 순차 함수 호출. Execution Host(§16.3)/Multi-Task(§16.4)/Workflow Adapter(§16.6) 중 **어느 것도 쓰지 않는다** — 순수 Python 함수 체인 |

### 4.2 Jarvis OS Kernel 측 — 이미 존재하는 Scoped Accept

`docs/architecture/baseline/BASELINE.md` §16(Kernel Modules)은 겉보기와 달리
이미 상당히 진전돼 있다. 이번 RFC를 위해 처음 확인한 사실이다:

| 절 | 책임 | 상태 | Production 구현 |
|---|---|---|---|
| §16.1 Governance | RFC/ADC/ADR 등록·상태 | Accept | (해당 없음 — 문서 절차) |
| §16.2 Execution Layer | Specification → 코드 생성/실행/테스트, Engine 호출 | Accept | OmniRoute가 Thin Engine Caller(Case A)로 Production Adoption(`ADR-0017`) — 그러나 ADC-01(Model↔Component)·ADC-02(Runtime 존폐)는 이 갱신 이후에도 **Open** |
| §16.3 Execution Host | 단일 실행 단위의 dispatch·격리 | **Accept, Scoped**(`ADC-0013`→`ADR-0003`) | **허용, 단 "동일 Target 동시 실행" 조건 한정, Thread 배제.** Scheduler/Multi-Task/Workflow, §6의 넓은 "Runtime" 구현은 여전히 금지 |
| §16.4 Multi-Task | 독립 Task들의 동시 시작·대기·결과 수집(우선순위/조건분기/Workflow 그래프 해석 불포함) | **Accept, Scoped, Conditional**(`ADC-0016`) | 허용(Data/Artifact Isolation이 사전 확인된 조합에 한함). 실증 사례: `hqs/development/mvp/workflow_0009.py::run_comparison`(main 병합됨) |
| §16.5 Multi-Task Result Store | 저장 전 검증 게이트(Resume 재검증/자동 Retry는 불포함) | **Accept, Scoped, Narrow**(`ADC-0017`) | 실증 사례는 `hqs/investment/checkpoint.py`의 `Checkpointer`/`run_step`/`ContentFailureError` **하나뿐**이며, 이 컴포넌트는 `hqs/development/mvp/`에 존재한 적이 없다. **다른 HQ에 동일 컴포넌트를 새로 만들 것을 요구하지 않는다**(`ADC-0017` §Decision 조건 6) |
| §16.6 Workflow Adapter | HQ가 이미 구성한 Workflow 그래프의 State/Node/Conditional Edge/Loop/값 기반 Checkpoint-Resume 진행 | **Accept, Scoped, Conditional**(`ADC-0019`→`ADC-0022`/`ADC-0023`) | **Production 구현 착수 미승인.** LangGraph는 "승인된 비강제 구현 전략 후보"로만 확정(`ADR-0019`) — 채택 자체가 아직 아님. `IMPLEMENTATION_RULES.md`의 Workflow Parser/Scheduler/Dynamic Routing/Stage 재진입 금지 조항은 **이 Accept로 해제되지 않는다** |
| §16.7 미결 항목 | Workflow/Memory/Event Bus Kernel Module 자체 | **Defer** | 해당 없음 |

**§16.6 Workflow Adapter의 결정적 제약(이 RFC에 직접 영향)**: Adapter Contract
(a)는 "진행 상태는 직렬화 가능한 값으로 표현되고, **어댑터는 그 값을 생산만
하며 영속화·복원을 소유하지 않는다**"고 명시한다. 즉 Workflow Adapter가 설령
Production 승인을 받아 도입되더라도, **Checkpoint 값을 실제로 어디에 저장할지는
Kernel이 아니라 "호출자"(caller-owned)의 책임으로 남는다.** Workflow Adapter는
Execution State의 *표현*만 다루고 *영속화*는 다루지 않는다.

### 4.3 Evidence 개념 자체의 부재

`docs/architecture/baseline/BASELINE.md` 전체(§1~§17)에 "Evidence"라는
**Kernel Concept**은 존재하지 않는다(문서 내 "Evidence" 사용은 전부 "Decision을
뒷받침하는 근거"라는 일반적 의미이지, Stage 05 `VerificationResult`를 저장하는
저장소를 가리키는 Concept이 아니다). §16.5 Multi-Task Result Store도 "결과
저장 게이트"이지 "Evidence"로 명명되지 않았고, 범위가 Investment HQ
`Checkpointer`로 Narrow하다. **Evidence Persistence는 이 저장소 Kernel
Architecture 어디에도 아직 정의된 적이 없는 완전히 새로운 Boundary
Question이다.**

### 4.4 ADC-02와의 관계 요약

`docs/decisions/adc/ADC.md`의 ADC-02("Runtime 개념의 존폐")는 **지금도
Open·NOW**다. 위 §16.3~§16.6의 모든 Scoped Accept는 "ADC-02가 다루는 넓은
'유지 대 대체' 구도를 해소하지 않는다"고 **각 절이 스스로 명시**한다(§16.3:
"ADC-02가 Open으로 남아 있는 한 그대로 유효", §16.6: "`ADC-02`/`ADC-09`는 이
갱신으로 재개설되지 않는다"). 즉 이 저장소는 "Runtime을 유지할지 폐기할지"라는
큰 질문은 열어둔 채, 그 질문의 **좁은 조각들**(단일 실행 격리, 독립 병렬 실행
조율, 저장 전 검증 게이트, 그래프 실행 상태 표현)만 개별적으로 Scoped Accept해
온 것이다.

## 5. Current Limitations

- Execution Identity 없음 (Q2)
- Task ID ↔ Execution ID mapping 없음 (Q5)
- Execution State 조회 불가 (Q6)
- Stage execution history 없음 (Q4)
- Execution persistence 없음 (Q4)
- Evidence persistence 없음 (Q9) — 그리고 Evidence라는 **Kernel Concept 자체가
  아직 정의된 적이 없음**(§4.3, 이번 조사의 새 발견)
- Cancellation 불가 (Q7)
- Retry 불가 (Q7) — `IMPLEMENTATION_RULES.md`가 Stage 재진입을 명시적으로 금지
- Resume 불가 (Q7) — §16.6 Workflow Adapter가 Production 승인되더라도 영속화는
  Kernel이 소유하지 않으므로, Resume을 실제로 쓰려면 별도로 "누가 Checkpoint
  값을 저장/복원하는가"를 결정해야 한다
- Historical execution query 불가 (Q4/Q5 결합)

## 6. Requirements (Command Center가 실제로 요구하는 것 — 확정 아님, 서술)

- Task `#042`처럼 "지금 Stage 04, 72%"를 표시하려면: 실행 중 State를 외부에서
  읽을 수 있는 지점이 필요하다.
- Task `Changes`/`Tests`/`Evidence` 탭이 실제 데이터를 가지려면: 실행이 끝난
  뒤에도 그 결과를 조회할 수 있는 History/Evidence 저장이 필요하다.
- `Progress ≠ Success` 원칙(§13)을 유지하려면: Progress(진행률, %)와
  Verdict(PASS/FAIL/INCONCLUSIVE/SKIPPED)를 **별도 축**으로 저장해야 한다 —
  하나가 다른 하나로부터 계산되면 안 된다.

## 7. Architecture Constraints (반드시 지켜야 하는 경계)

- `hqs/development/IMPLEMENTATION_RULES.md`의 금지 조항(Workflow Parser/
  Scheduler/Registry/Runtime/Engine Gateway/Policy/Memory Service/Event Bus,
  Stage 재진입) — §16.3/§16.4/§16.6의 어떤 Scoped Accept도 이를 해제하지
  않았다.
- `hqs/development/HANDOVER.md`의 "영속 저장소... 추가 금지".
- `docs/decisions/adc/ADC.md` ADC-02(Runtime 존폐, Open) — 이 RFC가 재개·재론
  하지 않는다.
- Development HQ Baseline v1.0의 **Public Contract**(`stages/contracts.py`의
  5개 Stage Contract, `KNOWN_CHECK_NAMES`, `check_results` 스키마, `status`
  집합, `blocking` 규칙) — 확장하려면 RFC→ADC→ADR 필요, 이 RFC가 임의로
  건드리지 않는다.
- §16.6 Workflow Adapter Adapter Contract (a) — Checkpoint 값의 영속화는
  Kernel이 아니라 caller-owned. 이 RFC가 "Kernel이 대신 저장해 준다"고
  가정하면 이미 확정된 Contract와 충돌한다.
- Command Center 자신의 원칙(`README.md`): 새 서버 API를 만들지 않는다,
  Mock을 Real로 위장하지 않는다 — 이 RFC의 Option 평가에도 그대로 적용한다.

## 8. Option A — 현재 on-demand 구조 유지 (Execution 비연결)

Command Center는 계속 Read-only Adapter로만 남고, `run_workflow()`는 지금처럼
사람이 터미널에서 직접 실행하는 채로 둔다. Task별 Changes/Tests/Evidence는
Mock으로 유지(이미 Real Data Adapter v0.1이 이렇게 판단·구현함).

**장점**: 추가 Architecture 영향 0. 기존 금지 조항과 전혀 충돌하지 않는다.
구현 즉시 가능(사실 이미 이 상태).
**단점**: Task history 불가, live progress 불가, Evidence persistence 불가 —
Command Center의 Task-centered UX 절반이 영구히 Mock으로 남는다.

## 9. Option B — Execution Persistence만 추가 (Runtime 없이)

`run_workflow()` 실행을 감싸는 **최소 wrapper**(새 Server API 아님, 예: 사람이
직접 실행하는 CLI 확장 또는 별도 스크립트)가 실행 전후로 Execution
Record(`execution_id`, `task_id`, `started_at`, `completed_at`, `status`)와
Stage Record, `VerificationResult` 원문을 **파일로** 남긴다. Command Center는
이 파일을 Real Data Adapter v0.1과 동일한 패턴(정적 스냅샷 export → fetch)으로
읽는다. 실행 자체는 여전히 동기·사람이 트리거.

**장점**: History/Evidence 조회 가능. Command Center 연동 가능. 기존
export-snapshot 패턴 재사용(새 서버 API 불필요).
**단점**: "영속 저장소" 자체가 HANDOVER.md 금지 조항이므로, **최소한의
파일 하나라도 Governance 승인 없이 만들 수 없다.** Live progress(실행
"중" 조회)는 이 옵션만으로는 안 된다 — 동기 실행이 끝나야 파일이 생기므로.
Cancel/Retry/Resume은 다루지 않는다.

## 10. Option C — Runtime/Scheduler 중심 Execution Architecture

Execution State를 실행 중에도 조회 가능하게 만들고(상시 또는 폴링 가능한
프로세스), Cancel/Retry/Resume까지 지원하는 구조. §16.6 Workflow Adapter를
Production 채택하거나(현재 미승인), 완전히 새로운 Runtime/Scheduler를
설계한다.

**장점**: lifecycle 관리 가능, cancel/retry/resume 가능, Command Center가
요구하는 모든 필드(live progress 포함)를 실제로 채울 수 있다.
**단점**: Architecture 영향이 가장 크다. ADC-02(Open)와 직접 충돌 — 이
Option을 실행하려면 ADC-02 해소가 사실상 선행되어야 한다. §16.6조차
"Production 구현 착수 미승인"이 명시돼 있어, 이 Option은 이미 존재하는
Gate(`ADC-0021` §8 Gate B/C, Reversibility v2 완전 검증)를 통과해야 시작할
수 있다 — 즉 이 RFC 하나로 열 수 있는 범위가 아니다.

## 11. Option D — Structure-only 확장(신규, 이번 조사로 도출)

Execution/Evidence를 저장하지 않은 채로, Command Center가 표시하는 **정적
구조**(Stage 이름/순서, `KNOWN_CHECK_NAMES`, Contract 필드명)만 `real/
export_real_snapshot.py`가 이미 하듯 `contracts.py`/`workflow.py`에서 직접
읽어 노출한다(Real Data Adapter v0.1의 `getWorkflowStatus()`가 이미 부분적으로
이 수준까지 함). Progress/History/Evidence는 Option A와 동일하게 전부 Mock/
unavailable로 유지.

**장점**: 이미 구현·검증된 패턴의 단순 확장. Architecture 영향 0(§16.2
`build_dev_hq_snapshot()`과 동일한 "구조 관찰, 실행 없음" 성격).
**단점**: Option A와 실질적으로 큰 차이가 없다 — "진짜 실행 데이터"에 대한
갈증은 전혀 해소하지 않는다.

## 12. Option Comparison

| 기준 | A (유지) | B (Execution Persistence) | C (Runtime/Scheduler) | D (Structure-only) |
|---|---|---|---|---|
| Architecture 영향 | 없음 | 중간(영속 저장소 금지 조항과 충돌) | 큼(ADC-02와 직접 충돌) | 없음 |
| Governance 선행 필요 | 없음 | RFC→ADC→ADR(영속 저장소 예외 승인) | ADC-02 해소 + `ADC-0021` Gate B/C | 없음 |
| History 조회 | 불가 | 가능(실행 후) | 가능(실행 중+후) | 불가 |
| Live Progress | 불가 | 불가 | 가능 | 불가 |
| Evidence 조회 | 불가(Mock만) | 가능 | 가능 | 불가 |
| Cancel/Retry/Resume | 불가 | 불가 | 가능(단, 별도 설계 필요) | 불가 |
| 즉시 착수 가능 여부 | 예 | 아니오 | 아니오 | 예 |

## 13. Execution Identity (Q1/Q2)

**Q1 비교**: Workflow Run(=`run_workflow()` 1회 호출) / Task(Command Center
UX 개념, 현재 실제 대응 없음) / Stage Run(Stage 01~05 각각의 1회 실행,
`workflow.py` 내부에서 암묵적으로만 존재) / Execution(위 전부를 포괄하는
일반 용어)을 비교하면, 저장소 사실과 가장 가까운 구조는:

```
Workflow Run(= Execution)
      └── Stage Run × 5 (context/planning/architecture/implementation/validation)
```

Task는 **여기 포함되지 않는다** — Task는 Command Center UX 개념이고,
`run_workflow()`는 `issue: dict` 하나만 받을 뿐 Task ID를 모른다(§4.1). 이
RFC는 "Task가 Execution을 소유한다"는 구조를 **확정하지 않는다** — §16
관점에서는 오히려 정반대로, Workflow Adapter A-IN이 "이미 구성된 실행 단위"를
불투명 입력으로 받듯, Task↔Execution 매핑도 **HQ/Command Center 쪽 도메인
책임**일 가능성이 높다(Kernel이 정의하지 않음, `ADC-0023` §D-9 계열 판단과
같은 방향).

**Q2**: Command Center가 "Task #042, RUNNING, Stage 04, 72%"를 표시하려면
**Execution Identity가 필요하다** — 최소한 `execution_id`(1회의 Workflow Run을
식별) 하나는 있어야 State/History를 그 Run에 귀속시킬 수 있다. `task_id`는
Command Center 쪽에서 `execution_id`에 매핑을 얹는 방식이 자연스러워 보이지만,
**그 매핑 자체를 누가 소유하는가(Kernel? Command Center? 별도 계층?)는 이
RFC가 결정하지 않는다** — §16.6이 "Task 전달 책임"을 Kernel Public Contract
밖(§14.1 #1 트랙)으로 명시적으로 유보한 것과 같은 이유다.

## 14. Execution State (Q3)

Q3 후보 A~F 비교:

- **A. Runtime** — ADC-02가 Open인 넓은 개념. 이 RFC 시점에는 선택 불가(선행
  Governance 미해소).
- **B. Scheduler** — `IMPLEMENTATION_RULES.md`가 명시적으로 금지. 선택 불가.
- **C. Workflow 자체(`run_workflow()`가 직접 상태를 들고 있음)** — 현재
  구조와 가장 가깝다. 다만 동기 함수이므로 "실행 중" 상태를 외부가 읽으려면
  별도 프로세스/스레드 경계가 필요해지고, 이는 사실상 Execution Host(§16.3)
  영역이다 — §16.3은 "동일 Target 동시 실행" 조건에서만 Scoped Accept됐으므로,
  Command Center의 단일 실행 조회 요구가 그 조건에 해당하는지부터 별도 검토가
  필요하다.
- **D. Execution Layer** — §16.2가 이미 Accept한 넓은 책임(Specification →
  실행)이지만, "내부 구조(재시도 정책 등)는 ADC-01·ADC-02가 Open으로 남긴
  영역"이라고 스스로 명시한다. 여기에 State 관리를 얹는 것은 사실상 ADC-02를
  건드리는 것과 같다.
- **E. 별도 Execution State Store** — Option B/C의 전제. 영속 저장소
  금지(§7)와 정면으로 부딪힌다.
- **F. §16.6 Workflow Adapter의 caller-owned Checkpoint 값** — 가장 최근에
  Scoped Accept된 개념과 가장 가깝다. 그러나 **Production 구현 자체가 미승인**
  이고, 값을 "누가" 들고 있을지(caller)가 곧 이 RFC가 열려는 질문(Evidence
  Persistence의 주체)과 같다 — 즉 F를 선택해도 "그 caller가 무엇인가"라는
  질문은 그대로 남는다.

**Runtime 유지 vs 폐기가 Command Center에 미치는 영향 비교**(§4 Option A/B
원문 그대로): Runtime을 유지하는 경우 Scheduler→Runtime→Workflow/Execution
경로로 Live State 조회가 Kernel Concept 안에서 설명되지만 ADC-02 해소가
선행돼야 한다. Runtime을 폐기하는 경우 Engine Gateway/Execution mechanism이
그 자리를 대신해야 하는데, 현재 §16.2 Execution Layer Accept는 "내부 구조는
Open"이라고 명시해 이 대안도 미완성이다. **어느 쪽이든 Command Center의
Live Progress 요구를 충족하려면 ADC-02(또는 그 Scoped 후속)의 추가 해소가
필요하다** — 이는 이번 RFC가 만들 수 있는 결론이 아니다.

## 15. Persistence (§5 요구사항 대비)

| 데이터 | 필요성 | 수명 | Source of Truth 후보 | 현재 저장 여부 |
|---|---|---|---|---|
| 최소 Execution Record(`execution_id`/`task_id`/`workflow`/`started_at`/`completed_at`/`status`) | Task 목록/History에 필수 | 영구(History 조회용) | 신규 — 없음 | **저장 안 됨** |
| Stage Record(`stage`/`started_at`/`completed_at`/`status`/`result_reference`) | Stage Timeline 표시에 필수 | 영구 | 신규 — 없음. `contracts.py`는 필드 이름만 정의, 저장은 하지 않음 | **저장 안 됨** |
| Verification Record(`required_checks`/`check_results`/`verdict`) | Evidence/Report 탭에 필수 | 영구 | `stages/contracts.py`의 `VerificationResult`가 **형태**는 이미 Public Contract로 정의 — 저장 위치만 없음 | **저장 안 됨**(`run_workflow()` 리턴값일 뿐) |
| Evidence(execution log/test result/diff/validation result/final report) | Evidence 탭 Artifact 목록에 필요 | 영구, 대용량 가능(diff/log) | 신규 — §16.5 Multi-Task Result Store는 Investment 전용(§4.2), 대응 없음 | **저장 안 됨** |

모든 행이 "신규"이거나 "저장 안 됨"이다 — 이는 §6이 요구하는 데이터 전부가
**현재 Source of Truth 자체를 갖지 못했다**는 뜻이다. 이 RFC는 어떤 저장
위치(파일/DB/기존 컴포넌트 확장)를 쓸지 **결정하지 않는다** — Option
B/C만이 그 결정을 필요로 하며, Option A/D는 이 표를 그대로 둔다.

## 16. Evidence의 의미(§6 요구사항 — Execution History와 구분)

```
Execution History  =  무엇을 언제 실행했는가
Evidence           =  그 실행이 무엇을 근거로 성공/실패/검증되었는가
```

이 구분은 저장소의 실제 사용과도 일치한다: `hqs/investment/checkpoint.py`의
`Checkpointer`(§16.5)는 **Execution History에 더 가깝다** — "저장 전
유효성"을 판정할 뿐 검증 근거(왜 성공/실패로 판단했는지)를 기록하는 것이
목적이 아니다. 반면 Development HQ Stage 05의 `VerificationResult`(`required_
checks`/`check_results`/`verdict`)는 **Evidence 그 자체**다 — `check_results`의
각 항목(`{name, status, blocking, detail}`)이 "무엇을 근거로" 그 Stage가
PASS/FAIL/INCONCLUSIVE로 판정됐는지를 담고 있다.

**중요한 사실**: `check_results`는 이미 Development HQ Baseline의 **Public
Contract**로 확정된 형태다(§4.1). 즉 "Evidence의 *형태*"는 이미 결정돼 있고
RFC-ADC-ADR 절차 없이 바꿀 수 없다 — 이 RFC가 열어야 할 질문은 "Evidence를
어떤 형태로 만들 것인가"가 아니라 **"이미 정해진 형태의 Evidence를 실행이
끝난 뒤에도 어디에 보존할 것인가"**로 좁혀진다. 이는 §16.5가 "저장 전
검증"만 다루고 "저장 자체"·"보존 기간"·"조회 방법"을 다루지 않은 것과
정확히 대칭되는 공백이다.

## 17. Task ↔ Execution Relationship(§7 요구사항)

Command Center UX 모델(Conversation → Task → Plan/Activity/Changes/Tests/
Evidence/Report)을 실제 Architecture로 승격하는 것은 **이 RFC의 범위가
아니다**(지시사항 §7: "Task Runtime을 만들지 않는다"). 이 절은 **Gap만
정의**한다:

- UX 모델은 "1 Task = 1 Execution"을 암묵적으로 가정한다(Task 하나를 열면
  그 Task의 Changes/Tests/Evidence가 전부 같은 실행을 가리킨다).
- 실제로는 "Task"라는 Kernel/HQ Concept이 없다(§13). `run_workflow()`가 아는
  것은 `issue: dict` 하나뿐이다.
- 이 Gap을 메우려면 최소한 "Task ID ↔ Execution ID 매핑을 누가 만들고
  보존하는가"라는 질문에 답해야 하는데, 이는 §13이 이미 지적했듯 Kernel이
  아니라 **HQ 또는 Command Center 쪽 도메인 책임일 가능성이 높다** — 다만
  이것도 이 RFC가 확정하지 않는다.

## 18. Progress / Time(§8 요구사항)

`Workflow Progress`(Stage 5개 중 완료 수 기반, 계산 가능 — 이미 `contracts.py`가
Stage 개수를 고정하므로 분모는 안정적이다), `Task Progress`/`Verification
Progress`(Task라는 Concept이 없으므로 계산 불가 — §17 Gap에 종속), `Overall
Progress`(위 종속 문제 그대로 계승), `Elapsed Time`/`Stage Duration`/`Task
Duration`(§15의 Execution/Stage Record가 `started_at`/`completed_at`을 저장해야
계산 가능 — 현재 저장 안 됨) 전부가 §15 Persistence 공백에 발이 묶여 있다.

**Progress ≠ Success 원칙 유지 방법**: `stages/contracts.py`가 이미 이
분리를 구조적으로 강제한다 — `check_results`의 `status`(PASS/FAIL/
INCONCLUSIVE/SKIPPED)는 Stage 완료 여부(Progress 계산의 분자)와 **별도
필드**다. 즉 Progress는 "Stage가 끝났는가"(bool 계열)로만 계산하고, Success는
`verdict`/`check_results`에서만 읽어야 한다 — 하나의 숫자에서 다른 하나를
역산하지 않는 것이 원칙 유지의 핵심이며, 이는 Real Data Adapter v0.1이 이미
`workflow.json`에서 `verdict` 유사 정보를 Progress와 분리해 다룬 것과 같은
방향이다. ETA는 지시사항대로 이 RFC 범위에서 결정하지 않는다.

## 19. Cancel / Retry / Resume(§9 요구사항)

- **Cancel**: 실행 중인 Workflow를 식별할 Execution Identity(§13)가 선행
  조건이다. 동기 함수 호출(`run_workflow()`)에는 애초에 "중단 지점"이 없다 —
  Cancel을 지원하려면 최소한 Execution Host(§16.3) 수준의 격리된 실행
  단위(별도 프로세스 등)가 필요하고, 이는 §16.3의 Scoped 조건("동일 Target
  동시 실행")과 현재 맞지 않는다.
- **Retry**: `IMPLEMENTATION_RULES.md`가 "Stage 재진입(Retry/Re-entry)·조건부
  Stage 실행 구현 금지"를 명시한다 — **전체 재실행(처음부터 새 Execution으로
  다시 `run_workflow()` 호출)은 이미 가능**(단지 History가 없어 "이전
  시도"라는 개념이 없을 뿐)하지만, **특정 Stage부터 재개하는 Retry는 명시적
  금지 대상**이다.
- **Resume**: §16.6 Workflow Adapter의 값 기반 Checkpoint/Resume이 개념적으로
  가장 가깝지만 (a) Production 미승인, (b) 영속화가 caller-owned(§4.2) —
  즉 Resume을 실제로 쓰려면 §15의 Persistence 공백이 먼저 메워져야 한다.

각 기능이 요구하는 것을 표로 정리하면:

| 기능 | Execution State | Persistence | Checkpoint | Runtime/Scheduler capability |
|---|---|---|---|---|
| Cancel | 필요(식별) | 불필요 | 불필요 | 필요(Execution Host 수준 이상) |
| Retry(전체) | 필요(식별) | 필요(이전 시도 기록) | 불필요 | 불필요(단순 재호출) |
| Retry(부분, Stage부터) | 필요 | 필요 | 필요 | **명시적으로 금지됨** |
| Resume | 필요 | **필요(caller-owned, 주체 미정)** | 필요(§16.6, 미승인) | 필요 |

이번 RFC는 위 네 기능 중 무엇도 구현하지 않는다(지시사항 §9).

## 20. Command Center Boundary(§10 요구사항)

```
Command Center
      ↓
Control Surface        ← 여기까지는 Command Center가 소유 가능(UI/Adapter)
      ↓
Execution mechanism     ← 이 지점부터 Kernel/HQ 소유 — Command Center가 넘으면 안 됨
      ↓
Dev HQ Workflow
      ↓
Evidence
```

**Command Center가 소유하면 안 되는 것**: 실행 요청의 최종 승인/실행 자체
(Execution mechanism), 상태의 Source of Truth(Command Center가 자체적으로
"이 Task는 RUNNING이다"를 판단·기록하면 안 되고, 항상 Kernel/HQ 쪽 State를
그대로 반사(reflect)해야 한다 — Mock을 Real로 위장하지 않는 원칙(§13)의
연장), 취소/재시도의 실제 실행(그 mechanism 자체), Evidence의 내용 해석
(`check_results`의 의미는 HQ 도메인 책임, Command Center는 표시만).

**Command Center가 소유해도 되는 것**: 실행 요청을 "보내는" 지점(Control
Surface — 단, 그 앞단 mechanism이 존재해야 의미 있음), 상태/History/Evidence의
**조회**(Read), UI 상의 Progress/Time 표시(계산 로직이 아니라 원본 데이터의
Rendering).

**Command Center가 Execution Engine이 되면 안 되는 이유**: Command Center는
현재 `serve_dashboard.py`(정적 파일 서버 + 3개 Command 경로)라는 매우 얕은
계층 위에 있다. 여기에 실행 상태 판정/재시도 정책/취소 로직을 직접 넣으면,
`IMPLEMENTATION_RULES.md`가 금지하는 Scheduler/Policy Engine을 Dashboard
Prototype 계층에 **우회 구현**하는 것과 동일한 효과를 낸다 — 금지 조항을
어느 계층에서 어기든 결과는 같다.

## 21. Security / Integrity(§11 요구사항 — Concern만 기록)

- **실행 결과 변조 방지**: Execution/Verification Record가 파일로 남는다면,
  그 파일이 실행 이후 수정 가능한 위치에 있으면 Evidence로서의 신뢰성이
  깨진다 — append-only 또는 서명 여부는 이 RFC가 결정하지 않는다.
- **Evidence 신뢰성**: `check_results`가 실제 실행에서 나온 것인지, 수동
  편집된 것인지 구분할 메커니즘이 없으면 "Mock을 Real로 위장"과 본질적으로
  같은 위험이 된다.
- **Task/Execution ID 위조**: ID를 Command Center(Browser 노출 계층)가 생성한다면
  위조 가능성을 고려해야 한다 — ID 발급 주체를 Kernel/HQ 쪽으로 두는 것이
  안전할 가능성이 높으나 확정하지 않는다.
- **권한**: 누가 실행을 트리거/취소할 수 있는지에 대한 인가(authorization)
  모델이 현재 전혀 없다(Dashboard Shell 자체가 로컬 개발자 도구 성격).
- **민감한 실행 로그**: Stage 04 Implementation 결과 등에 코드/설계 내용이
  포함될 수 있어, Evidence 저장 위치의 접근 범위를 고려해야 한다.
- **API 접근**: 새 Server API가 생긴다면(Option B/C) 그 API의 인증/인가는
  이 RFC 범위 밖이지만 반드시 후속 설계에서 다뤄야 할 항목으로 기록한다.
- **Audit trail**: "누가 이 실행을 시작했는가"를 남길지 여부 — 현재 어떤
  실행 경로도 이를 기록하지 않는다.

이번 RFC는 위 어느 것도 구현하지 않는다(지시사항 §11) — Concern만 기록한다.

## 22. Architecture Principles 기준 평가

| 원칙 | A (유지) | B (Execution Persistence) | C (Runtime/Scheduler) | D (Structure-only) |
|---|---|---|---|---|
| Existing Architecture 우선 | ✅ 완전 부합 | △ 새 저장 위치 필요 | ✗ ADC-02 미해소 상태에서 위반 소지 | ✅ 완전 부합 |
| Simple > Complex | ✅ | △ | ✗ | ✅ |
| Everything is Replaceable | 영향 없음 | §16.6 caller-owned 원칙과 맞으면 유지 가능 | Runtime 선택이 이 원칙과 계속 긴장 관계 | 영향 없음 |
| No Silent Failure | 영향 없음 | Execution 실패도 기록되므로 오히려 개선 | 동일 | 영향 없음 |
| Evidence 기반 검증 | Evidence 자체가 없어 원칙을 실천 못함 | Evidence 실제 보존 가능 — 원칙에 가장 부합 | 동일(부합) | 부합 못함 |
| Domain 내용은 HQ가 소유 | 부합 | 부합(저장 위치만 신규, 내용은 여전히 HQ `check_results`) | 위험 — Runtime이 Domain 해석까지 흡수할 소지 | 부합 |
| OS는 Mechanism을 소유 | 해당 없음 | Execution Record 저장 mechanism만 추가 | Runtime 자체가 큰 Mechanism — ADC-02가 그 정당성을 아직 결정 안 함 | 해당 없음 |
| Command Center는 Execution Engine이 아님 | 자동 충족 | 충족 가능(§20 Boundary 지키면) | 위반 위험 큼(Cancel/Retry UI가 곧 Engine 역할 흡수 유혹) | 자동 충족 |
| Mock을 Real로 위장하지 않음 | 이미 실천 중(Real Data Adapter v0.1) | 실천 가능 | 실천 가능하나 구현 복잡도만큼 위반 여지 커짐 | 이미 실천 중 |
| Progress ≠ Success | 해당 없음(Progress 자체가 Mock) | §18 방법으로 유지 가능 | 유지 가능(더 복잡) | 해당 없음 |

## Recommendation / Decision Candidate

이 RFC는 최종 결정을 내리지 않는다. 다만 위 분석에서 다음이 비교적 명확하게
드러난다:

- **Option C(Runtime/Scheduler)는 이 RFC 하나로 열 수 있는 범위가 아니다** —
  ADC-02(Open·NOW)와 `ADC-0021` §8 Gate B/C(Workflow Adapter Production 구현
  선행조건) 둘 다 미해소이므로, 독립적인 별도 절차가 선행돼야 한다.
- **Option A/D는 이미 사실상 채택돼 있다**(Real Data Adapter v0.1의 Boundary
  판정 D와 동일선상) — 추가 Governance 없이 유지 가능하나, Command Center의
  Task-centered UX 절반을 영구히 Mock으로 남긴다.
- **Option B가 가장 검토 가치가 있는 다음 단계**로 보인다 — Execution Host/
  Multi-Task/Workflow Adapter 같은 무거운 Kernel Concept을 새로 열지 않고도,
  "실행이 끝난 뒤 결과를 어디에 남길 것인가"라는 좁은 질문 하나(§16.5가
  Investment HQ에서 이미 그랬듯)로 범위를 좁힐 수 있다. 단, 이는
  `hqs/development/HANDOVER.md`의 "영속 저장소 추가 금지" 조항의 **예외**를
  요구하므로, 그 예외 승인 자체가 **별도 ADC 대상**이다 — 이 RFC가 그 예외를
  선(先)승인하지 않는다.

**Decision Candidate(확정 아님)**: 다음 단계는 "Execution Record/Stage
Record/Verification Record의 최소 저장(Option B의 좁은 부분집합)"만을 여는
**Boundary Question 하나짜리 후속 RFC**를 여는 것이 가장 리스크가 작아
보인다 — Live Progress/Cancel/Retry/Resume(Option C 영역)은 그 RFC에도
포함하지 않고 명시적으로 제외해야 한다. 이 판단 자체도 후속 ADC가 다시
검토해야 한다.

---

## 23. Risks (§19 요구사항 — 별도 기록)

- Option B를 좁게 연다고 선언해도, 실제 구현 단계에서 "History가 있으니
  Retry도 자연스럽게 필요하다"는 압력이 생겨 Scope Creep으로 Option C 영역을
  침범할 위험 — §16.3~§16.6 전례(Execution Host → Multi-Task → Result Store →
  Workflow Adapter로 점진 확장)가 실제로 이렇게 진행됐음을 상기해야 한다.
- Evidence 저장 위치가 diff/log 등 **대용량·민감 데이터**를 포함하면, "영속
  저장소 금지"의 예외 승인 범위를 벗어나 사실상 Database에 가까워질 위험.
- `check_results`가 Public Contract로 고정돼 있다는 사실이, 향후 이를
  확장(Security/Data-API 등 새 검사 종류 추가, HANDOVER.md가 이미 "대응
  Capability 부재로 여전히 미해결"이라 언급)해야 할 압력과 맞물릴 때, 이
  RFC의 좁은 범위(저장 위치)를 벗어나는 요구로 번질 위험.

## Open Questions

1. Execution Record/Stage Record/Verification Record를 저장하는 것이
   `hqs/development/HANDOVER.md`의 "영속 저장소 금지" 조항의 예외로 인정될
   수 있는가, 아니면 그 조항 자체의 개정이 필요한가?
2. Task ID ↔ Execution ID 매핑은 Kernel 책임인가, HQ 책임인가, Command
   Center(Dashboard Prototype) 책임인가?
3. Execution Host(§16.3)의 "동일 Target 동시 실행" 조건이 Command Center의
   단일 실행 조회 요구에도 적용/확장될 수 있는가, 아니면 완전히 별개
   질문인가?
4. Evidence를 Kernel Concept으로 신설할 것인가(§16.7류 새 Module 후보), 아니면
   HQ Public Contract의 저장 형태 문제로만 좁게 다룰 것인가?

## Required ADC / ADR Follow-up

- 이 RFC가 후속 ADC로 승격된다면, 그 ADC는 **Option B의 좁은 부분집합
  하나만** Boundary Question으로 열어야 한다(§16.3~§16.6이 각각 그렇게 해온
  선례를 따른다) — "Execution/Stage/Verification Record를 파일로 남기는
  책임을 Kernel Concept으로 Accept할 것인가".
- 그 ADC는 ADC-02를 재개하지 않고, §16.3~§16.6의 어떤 Accept도 수정하지
  않아야 한다(Out of Scope 명시 필수 — `ADR-0003`/`ADC-0017`/`ADC-0019`의
  선례 형식을 따른다).
- Live Progress/Cancel/Retry/Resume은 별도의, 더 나중 RFC로 명시적으로
  분리해야 한다 — 이번 RFC의 결론과 동일선상에서, 그 범위는 ADC-02 해소
  이후에나 열 수 있다.

---

Architecture Change: 없음 (이 RFC 자체가 변경이 아니라 분석 문서)
Contract Change: 없음
Implementation: 없음 (지시사항대로 코드/Workflow/CLI/API/Runtime/Scheduler/
Task Store/Execution Store/Evidence Store/Command Center UI 전부 미변경)
RFC: `RFC-0043`(본 문서, Proposed)
ADC: 없음 (열리지 않음 — 후속 ADC는 이 RFC가 결정하지 않는다)
ADR: 없음
PR: 없음
