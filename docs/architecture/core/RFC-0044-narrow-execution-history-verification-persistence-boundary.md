# RFC-0044: Narrow Execution History & Verification Persistence Boundary

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (RFC-0043 Architecture Review 후속)
**대상**: `RFC-0043-execution-history-evidence-persistence-architecture.md`의
Decision Candidate("Option B의 좁은 부분집합 하나만 여는 후속 RFC")를 이어받아,
Development HQ Workflow(`hqs/development/workflow.py`)의 Execution/Stage/
Verification 결과를 Command Center가 **사후 조회**할 수 있게 하는 **최소
Persistence Boundary** 하나만 Architecture 수준에서 정의한다.

> 본 RFC는 Runtime/Scheduler/Workflow Parser/Workflow Orchestration/Dynamic
> Routing/Retry/Resume/Cancellation/Background 실행/Distributed 실행/새
> Engine Gateway/Memory Service/Event Bus/새 Agent·Capability/실시간 Execution
> Control 중 어느 것도 설계·구현하지 않는다. ADC-02를 비롯한 어떤 Open/
> Resolved Decision도 재론·재개·확정하지 않는다. 코드/테스트/Dashboard/
> Persistence 컴포넌트는 만들지 않는다. "Persistence가 필요하다"는 사실과
> "Persistence Architecture를 지금 확정한다"는 것은 분리한다 — 이 RFC는
> Decision Candidate까지만 다룬다.

---

## 1. Identity & Status

| Field | Value |
|---|---|
| Document ID | RFC-0044 |
| Title | Narrow Execution History & Verification Persistence Boundary |
| Type | RFC |
| Target Domain | Kernel Architecture / Development HQ — Execution/Stage/Verification 결과 사후 조회를 위한 최소 Persistence Boundary(Option B Decision Candidate) |
| Status | Proposed (검토 대상, 결정 아님) |
| Decision Group | RFC-0043 Option B Decision Candidate 후속 — 아직 ADC 미개설(§1) |
| Parent Documents | docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md |
| Related Documents | 아래 「Related Documents」 참조 |
| Evidence References | docs/architecture/baseline/BASELINE.md §16, docs/decisions/adc/ADC.md ADC-02 |
| Source Path | docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md |
| Last Verified | 정보 없음 — 원문에 정의되지 않음 |
| Verification Confidence | 정보 없음 — 원문에 정의되지 않음 |

## 2. Context & Problem

### 1. Status

Proposed. 후속 ADC가 아직 열리지 않았다.

### 2. Context — RFC-0043 재확인

RFC-0043은 다음을 실측·분석으로 확정했고, 이 RFC는 그 결론을 전제로 시작한다
(재론하지 않음):

- `run_workflow()`는 동기 함수이며 실행 결과를 dict로 리턴할 뿐 어디에도
  저장하지 않는다. Execution Identity/Task↔Execution mapping/Stage History/
  Evidence persistence가 전부 없다.
- `docs/architecture/baseline/BASELINE.md` §16 Kernel Modules는 이미
  §16.3(Execution Host)~§16.6(Workflow Adapter)까지 Scoped Accept가 진행돼
  있으나, **어느 것도 persistence를 소유하지 않는다** — §16.6 Workflow
  Adapter Contract (a)는 "어댑터는 진행 상태 값을 생산만 하며 영속화·복원을
  소유하지 않는다"(caller-owned)를 명시한다.
- `docs/decisions/adc/ADC.md` ADC-02("Runtime 개념의 존폐")는 지금도
  **Open·NOW**다. §16.3~§16.6의 모든 Scoped Accept는 이 구도를 해소하지
  않는다고 각 절이 스스로 명시한다.
- Evidence는 Kernel Concept으로 정의된 적이 없다 — Development HQ Stage 05
  `VerificationResult`(`required_checks`/`check_results`/`verdict`)가
  Evidence 그 자체이지만, 그 저장 위치는 어디에도 없다.
- RFC-0043의 Option 비교(A 현행 유지 / B Execution Persistence만 추가 / C
  Runtime·Scheduler 중심 / D Structure-only)에서, **Option C는 ADC-02(Open)와
  `ADC-0021` §8 Gate B/C(Workflow Adapter Production 구현 선행조건) 둘 다
  미해소이므로 이 RFC 하나로 열 수 있는 범위가 아니다**. Option A/D는 이미
  사실상 채택돼 있다(Real Data Adapter v0.1). **Option B가 다음 단계로 검토
  가치가 있다**고 판단했다.

본 RFC는 이 Decision Candidate를 이어받아, **Option B의 좁은 부분집합**만을
단독 Boundary Question으로 좁혀 다룬다.

#### 2.1 재확인한 현재 문서 상태(작업 착수 전 재조사)

이 RFC 작성 직전 다음을 다시 읽고 RFC-0043 이후 변경이 없음을 확인했다:

| 문서 | 확인 결과 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` §16 | RFC-0043 인용 내용과 동일(§16.1~§16.7 Accept/Scoped 상태 무변경) |
| `docs/decisions/adc/ADC.md` | ADC-01~12 전부 Open, ADC-02 여전히 NOW 우선순위, 변경 없음 |
| `hqs/development/BASELINE.md` | "Not Included"에 Runtime 명시 무변경. Stage Data Contract(§Public/Hidden) 무변경 |
| `hqs/development/HANDOVER.md` | "영속 저장소... 추가 금지" 문구 무변경(§What Claude Code Must Never Do) |
| `hqs/development/IMPLEMENTATION_RULES.md` | 금지 표 무변경. Execution Host(§16.3)/Multi-Task(§16.4)/Multi-Task Result Store(ADC-0017) Scoped 허용 범위 무변경 — ADC-0017 절이 "Development HQ에는 적용 대상 자체가 없다"고 명시한 것도 그대로 |
| Workflow Adapter 관련 문서(`ADC-0019`/`ADC-0022`/`ADC-0023`) | caller-owned persistence 원칙 무변경, Production 구현 여전히 미승인 |
| Execution Layer 트랙(`docs/core/execution-layer/`) | 무관 트랙 재확인 — 이 트랙은 **단일 Engine 호출 1회의 산출물을 어떻게 묶는가**(`ADC-0002` Execution Result Contract)를 다루며, Workflow 실행 이력·Stage 이력과는 별개 질문이다(`ADC-0002` "이 ADC가 답하지 않는 것": "Execution State의 상태 전이 규칙(별도 사안)"으로 명시적으로 제외) |

RFC-0043 이후 이 저장소의 관련 Architecture 상태에 실질적 변화는 없다.

### 3. Problem (A)

- `run_workflow()`의 결과는 **stdout/in-memory 수준**에서 끝난다 — 호출이
  끝나면 그 실행이 존재했다는 사실 자체가 사라진다.
- **Execution Identity가 없다** — 여러 번의 실행을 서로 구분할 식별자가
  코드 어디에도 없다.
- **Task ↔ Execution mapping이 없다** — Command Center의 Task(`#039`~`#042`류
  UX 개념)와 실제 `run_workflow()` 호출 사이에 대응 관계를 코드가 모른다.
- **Stage History가 없다** — Stage 01~05 각각이 언제 시작·종료했는지,
  어떤 순서로 어떤 결과를 냈는지 실행 종료 후에는 알 수 없다.
- **Verification/Evidence를 사후 조회할 수 없다** — Stage 05
  `VerificationResult`(`required_checks`/`check_results`/`verdict`)는 이미
  Development HQ Baseline의 **Public Contract**로 그 형태가 확정돼 있음에도
  (`hqs/development/BASELINE.md` "Stage Data Contract"), 그 값을 실행이 끝난
  뒤 다시 볼 방법이 전혀 없다.

### 4. Scope (B)

이 RFC가 **저장 대상으로 검토**하는 기록은 다음 6종으로 한정한다. 더 넓히지
않는다.

1. **Execution Identity** — 1회의 `run_workflow()` 호출을 식별하는 값
   (`execution_id`).
2. **Execution metadata** — `started_at`/`completed_at`/최종 `status`
   (`COMPLETED`/`FAILED`류, 실행 자체의 종료 상태).
3. **Stage execution result** — Stage 01~05 각각이 리턴한 Contract 값
   (`ContextAnalysisResult`/`SpecificationResult`/`DesignResult`/
   `ImplementationResult`/`VerificationResult`, `hqs/development/BASELINE.md`가
   이미 형태를 확정한 것과 동일한 Public Contract를 그대로 참조).
4. **Stage timestamps/status** — 각 Stage의 시작/종료 시각과 완료 여부(Progress
   계산의 분자 — RFC-0043 §18이 이미 구분한 "Progress ≠ Success" 원칙을
   유지하는 축).
5. **Stage 05 `VerificationResult`** — `required_checks`/`check_results`/
   `verdict`. Evidence 그 자체(RFC-0043 §16의 구분: Execution History는
   "무엇을 언제 실행했는가", Evidence는 "그것이 무엇을 근거로 판정됐는가").
6. **Evidence/artifact reference** — 값 자체가 아니라 **참조**(예: 생성된
   diff/log/report가 파일로 존재한다면 그 경로). 대용량 원문을 이 RFC의
   저장 대상에 포함하지 않는다(§9 Risks 참조).
7. **Final execution status** — 위 1~6을 종합한, 실행 1회의 최종 결론
   (`verdict`와는 별도 축 — 실행 자체가 끝까지 갔는지 vs. 그 결과가
   PASS/FAIL인지를 혼동하지 않는다).

## 3. Analysis & Decision

### 5. Explicit Non-Goals (C)

다음은 이번 RFC 범위에서 **명시적으로 제외**한다. Scope(§4)에 포함되지
않으며, 후속 RFC라도 이 RFC의 결론을 근거로 자동 확장되지 않는다.

- Runtime 구현
- Scheduler
- Workflow Parser
- Workflow orchestration
- Dynamic routing
- Retry(부분 재진입 포함 — `IMPLEMENTATION_RULES.md`가 이미 명시적으로 금지)
- Resume(§16.6 Workflow Adapter Checkpoint/Resume 포함)
- Cancellation
- Background 실행
- Distributed 실행
- 새로운 Engine Gateway
- Memory Service
- Event Bus
- 새로운 Agent/Capability
- 실시간 execution control(Live Progress 조회 포함 — 동기 실행이 끝나야
  기록이 생기는 구조를 전제로 하므로, "실행 중" 상태 조회는 이 RFC의
  Scope 밖이다)

#### Live Execution State Boundary

- 본 RFC의 Persistence 대상은 실행 종료 후 사후 조회 가능한 기록이다.
- 현재 Development HQ Workflow는 동기 실행이며 실행 중 외부 State 조회
  경로가 없다.
- 따라서 Live Progress / Live Execution State는 본 RFC의 Persistence
  Decision에 포함하지 않는다.
- Background Execution, Live State Streaming, Cancellation, Retry, Resume
  등의 기능도 본 RFC의 결정으로 허용되지 않는다.
- 향후 Command Center가 실행 중 State/Progress를 실제로 표시해야 하는
  경우 별도의 Architecture Question으로 취급한다.
- 해당 문제는 Runtime/Execution Architecture와 직접적인 관계가 있을 수
  있으므로 ADC-02와의 정합성을 별도로 검토해야 한다.
- RFC-0044의 Persistence Decision을 Live Execution Architecture의 근거로
  자동 확장하지 않는다.

### 6. Ownership Boundary (D)

#### 6.1 Development HQ Workflow가 생산하는 결과

`run_workflow()`는 Stage 01→05를 호출하며 각 Stage가 리턴하는 dict를
그대로 합성해 최종 dict 하나를 리턴한다. 이 값들의 **형태**(Public Contract)는
이미 `hqs/development/BASELINE.md`가 소유하고 있다 — 이 RFC가 그 형태를
바꾸지 않는다. Development HQ가 소유하는 것은 "무엇이 생산되는가"(Contract)
이지 "그것이 어디에 남는가"(Persistence)가 아니다 — 이 둘은 서로 다른
질문이다.

#### 6.2 Persistence를 누가 소유할 수 있는가

세 후보를 검토한다:

- **Kernel(§16 Kernel Modules)** — §16.5 Multi-Task Result Store가 가장
  가까운 선례이나, 그 Accept는 명시적으로 **Narrow**하고(`ADC-0017`),
  "Development HQ에는 적용 대상 자체가 없다"고 스스로 못박는다
  (`IMPLEMENTATION_RULES.md` "Multi-Task Result Store 관련 확인" 절). §16.6
  Workflow Adapter는 한발 더 나아가 persistence 소유를 **명시적으로
  거부한다**(caller-owned). 즉 Kernel이 이 기록의 persistence를 소유한다고
  가정하는 것은 현재 어떤 Accept로도 지지되지 않는다.
- **Development HQ(`hqs/development/`)** — `hqs/development/BASELINE.md`
  "Not Included"에 Runtime이 명시돼 있고, `HANDOVER.md`가 "영속 저장소...
  추가 금지"를 Frozen 규칙으로 못박는다. Development HQ가 스스로
  persistence를 소유하는 것도 현재 Baseline과 정면으로 충돌한다.
- **Command Center(`projects/dashboard-shell-mvp/devhq-command-center/`)** —
  아래 6.4에서 별도로 검토.

**중간 결론(확정 아님)**: 현재 저장소의 어떤 기존 Accept도 "누가 이
persistence를 소유하는가"라는 질문에 답을 갖고 있지 않다. 이는 §16.5/§16.6이
의도적으로 좁게 Accept됐기 때문이지, 우연한 공백이 아니다. 이 질문에 답하는
것 자체가 **새로운 Boundary Question**이며, 그것이 이 RFC가 후속 ADC로
넘기려는 것이다(§10).

#### 6.3 Workflow Adapter의 caller-owned 원칙과의 정합성

§16.6 Workflow Adapter Contract (a)는 "어댑터는 진행 상태 값을 생산만 하며
영속화·복원을 소유하지 않는다"고 명시한다. 이 원칙은 **이 RFC의 Scope(§4)와
충돌하지 않는다** — 오히려 방향이 같다:

- Workflow Adapter가 다루는 것은 **실행 중** Checkpoint 값의 표현이다
  (Production 미승인 상태이며, 이 RFC의 Scope 밖).
- 이 RFC가 다루는 것은 **실행이 끝난 뒤** 남는 결과 기록이다(§4).
- 두 질문 모두 "값을 누가 저장하는가"에서 Kernel이 아니라 **caller**(호출한
  쪽)를 가리킨다는 점에서 일관된다. 즉 이 RFC가 "caller-owned"의 caller가
  구체적으로 누구인지(HQ? Command Center? 제3의 계층?)를 확정하지 않더라도,
  "Kernel이 대신 저장해 주지 않는다"는 전제 자체는 §16.6과 이미 정합적이다.

#### 6.4 Command Center가 persistence owner가 되면 안 되는지

RFC-0043 §20(Command Center Boundary)이 이미 정리한 원칙을 그대로 계승한다:
Command Center가 소유해도 되는 것은 **조회(Read)**뿐이며, 상태의 **Source of
Truth**를 자체적으로 판단·기록하면 안 된다(Mock을 Real로 위장하지 않는
원칙의 연장). Persistence owner가 된다는 것은 "이 실행이 COMPLETED다"를
Command Center 자신이 **판정**한다는 뜻이 되므로, 현재 원칙과 정면으로
충돌한다. **Command Center는 이 기록의 소비자(Reader)로만 남아야 하며,
생산자(Writer)가 되어서는 안 된다** — 이는 이 RFC가 Option 비교(§7)에서
지키는 고정 제약이다.

#### 6.5 Kernel에 Evidence Concept을 신설할 필요성

RFC-0043 §4.3이 이미 확인했듯, "Evidence"는 `BASELINE.md` 어디에도 Kernel
Concept으로 정의된 적이 없다. 이 RFC는 그 신설이 **필요한가**를 열린 질문으로
남긴다(§10 Open Questions) — 신설 자체를 이 RFC가 결정하지 않는다. 다만
관찰: §16.5(Result Store)도 "Evidence"라는 이름을 쓰지 않았고 범위가 Narrow
했다는 사실은, Evidence를 Kernel Module로 신설하는 것보다 **HQ Public
Contract의 저장 형태 문제로 좁게 다루는 쪽**이 기존 저장소의 선례(Narrow
Accept 경향)와 더 일치할 가능성을 시사한다 — 그러나 이 판단도 후속 ADC의
몫이다.

### 7. Persistence Model (E) — Architecture Option 비교

파일 기반 persistence를 구현안으로 확정하지 않는다. 4개 Option을 비교한다.

#### Option A — No Persistence(현행 유지)

`run_workflow()`를 그대로 둔다. Execution/Stage/Verification 기록을 저장하지
않는다.

- **Boundary impact**: 없음.
- **Governance impact**: 없음 — 어떤 절차도 필요 없다.
- **Complexity**: 0.
- **Future migration impact**: 나중에 Option B/C로 전환 시 "과거 실행
  이력"은 소급 생성 불가(그 시점부터 새로 쌓인다).
- **ADC-02 의존**: 없음.

#### Option B — Narrow File-based Execution Records

`run_workflow()` 실행을 감싸는 최소 wrapper(새 Server API 아님 — 기존
`export_real_snapshot.py` 패턴처럼 **호출자 쪽 스크립트/CLI 확장**)가 §4
Scope의 6개 기록을 실행 종료 시점에 파일로 남긴다. 저장 위치의 소유자는
**caller**(§6.2가 답하지 못한 질문 — 후속 ADC 대상)이며, 이 Option 자체는
"파일"이라는 저장 형태만 고정한다.

- **Boundary impact**: 중간. `hqs/development/HANDOVER.md`의 "영속 저장소...
  추가 금지" 조항과 문언상 충돌한다 — **예외 승인이 필요**하다(§10).
  §16 Kernel Module 어느 것도 건드리지 않는다(§16.5/§16.6 caller-owned
  원칙과 정합적, §6.3).
- **Governance impact**: RFC → ADC → ADR(영속 저장소 금지 조항의 **Scoped
  예외** 승인) 필요.
- **Complexity**: 낮음 — 기존 `export_real_snapshot.py`류 정적 스냅샷 패턴을
  재사용 가능(신규 서버 경로 불필요).
- **Future migration impact**: 파일 → 다른 저장 형태(예: 후속 Option C의
  일부)로 전환 시, 기록의 **형태**(§4 Scope 6종)는 이미 Public Contract에
  가깝게 고정돼 있어 이관 비용이 상대적으로 낮다.
- **ADC-02 의존**: 없음 — Runtime 존폐와 무관하게, "실행이 끝난 뒤 결과를
  파일로 남긴다"는 이 Option은 Runtime 개념을 전제하지 않는다.

#### Option C — Dedicated Persistence Service/Store

Execution Record를 전담하는 별도 서비스/저장소(DB, 전용 API 등)를 신설한다.

- **Boundary impact**: 큼. `IMPLEMENTATION_RULES.md`의 Memory Service/
  Registry 금지 조항과 직접 충돌한다.
- **Governance impact**: RFC → ADC → ADR 전체 절차, 게다가 새 Kernel
  Component 후보이므로 §16.7류 신규 Module 승격 절차에 준하는 검토가
  필요하다.
- **Complexity**: 높음 — 서비스 lifecycle, 접근 제어, 마이그레이션까지
  다뤄야 한다.
- **Future migration impact**: 가장 유연하지만, 지금 결정하면 이후 되돌리기
  비용이 크다(서비스가 한 번 존재하면 의존이 누적된다).
- **ADC-02 의존**: 간접적으로 있다 — "전담 서비스"는 Runtime의 한 형태로
  해석될 여지가 있어, ADC-02가 Open인 채로 이 Option을 채택하면 사실상
  ADC-02의 한쪽(Runtime 유지) 방향으로 선판단하는 효과를 낼 위험이 있다.

#### Option D — Runtime/Scheduler 중심 Persistence

Runtime 또는 Scheduler가 실행을 직접 관리하면서 그 부산물로 persistence를
갖는다(RFC-0043 Option C와 동일 계열).

- **Boundary impact**: 가장 큼. ADC-02(Open)와 정면 충돌.
- **Governance impact**: ADC-02 해소가 선행돼야 시작 가능 — 이 RFC/후속 ADC
  하나로 열 수 있는 범위가 아니다(RFC-0043 §12/§Recommendation과 동일
  결론).
- **Complexity**: 가장 높음.
- **Future migration impact**: 해당 없음(착수 자체가 이 RFC 범위 밖).
- **ADC-02 의존**: 직접적·선행적.

#### Option Comparison

| 기준 | A (No Persistence) | B (Narrow File-based) | C (Dedicated Store) | D (Runtime/Scheduler) |
|---|---|---|---|---|
| Boundary impact | 없음 | 중간(영속 저장소 금지 조항 예외 필요) | 큼(Memory Service/Registry 금지와 충돌) | 가장 큼(ADC-02 직접 충돌) |
| Governance 선행 필요 | 없음 | RFC→ADC→ADR(Scoped 예외) | RFC→ADC→ADR + 신규 Kernel Component 검토 | ADC-02 해소 선행 |
| Complexity | 0 | 낮음 | 높음 | 가장 높음 |
| Future migration impact | 이력 소급 불가 | 낮음(형태가 이미 Contract에 가까움) | 큼(되돌리기 비용) | 해당 없음(착수 불가) |
| ADC-02 의존 | 없음 | 없음 | 간접적 | 직접적·선행적 |
| 즉시 착수 가능 여부(별도 예외 승인 후) | 예(이미 현재 상태) | 예외 승인 후 가능 | 아니오 | 아니오 |

### 12. Recommendation / Decision Candidate

이 RFC는 최종 결정을 내리지 않는다. 다만 위 분석에서 다음이 비교적 명확하게
드러난다:

- **Option D(Runtime/Scheduler 중심)는 ADC-02 해소 없이 열 수 없다** — RFC-0043의
  동일 결론을 재확인한다.
- **Option C(전담 서비스)는 이 RFC 하나로 열기에는 Governance 비용이 너무
  크다** — 신규 Kernel Component 후보에 준하는 검토가 필요하다.
- **Option A(No Persistence)는 언제든 선택 가능한 기본값**이다 — 아무 것도
  하지 않아도 되는 선택지로 항상 남아 있다.
- **Option B(Narrow File-based)가 이 RFC가 열려는 Boundary Question의
  실질적 후보**로 보인다 — 기존 `export_real_snapshot.py` 패턴을 재사용할
  수 있고, ADC-02와 독립적이며(§9), §16.6 caller-owned 원칙과 정합적이다
  (§6.3). 단, **caller가 구체적으로 누구인지(§6.2가 답하지 못한 질문)와
  "영속 저장소 금지" 조항의 예외 범위**는 후속 ADC가 결정해야 한다.

**Decision Candidate(확정 아님)**: 후속 ADC를 연다면, 그 ADC는 다음 하나의
질문만 Boundary Question으로 열어야 한다 — **"Option B(Scope §4의 6개
기록을 파일로 남기는 것)를 `hqs/development/HANDOVER.md`의 영속 저장소
금지 조항의 Scoped 예외로 Accept할 것인가, 그리고 그 caller는 누구인가."**
Live Progress/Cancel/Retry/Resume(Option C/D 영역)은 그 ADC에도 포함하지
않고 명시적으로 제외해야 한다.

---

## 4. Evidence & Validation

### 8. Data Integrity (F)

다음 원칙을 이 RFC가 검토하되, 확정된 구현 규칙으로 제시하지 않는다 — 후속
ADC/ADR이 실제 규칙으로 못박아야 한다.

- **실제 실행에서 생성된 값만 저장** — Execution Record는 `run_workflow()`가
  실제로 리턴한 값의 파생물이어야 하며, 수동 생성·편집된 값이 섞이면 안
  된다(RFC-0043 §21 "Evidence 신뢰성" Concern과 동일 축).
- **Progress와 Verdict 분리** — `hqs/development/BASELINE.md`의 Stage
  Contract가 이미 `check_results`의 `status`를 Stage 완료 여부와 별도
  필드로 구조화하고 있다(RFC-0043 §18). 이 RFC의 Scope(§4)도 Stage
  timestamps/status(항목 4, Progress 계산용)와 `VerificationResult`(항목 5,
  Verdict)를 별개 항목으로 분리해 이 원칙을 그대로 계승한다.
- **실행 결과와 Evidence를 임의로 생성하지 않음** — 저장 대상이 없는
  Stage/필드에 대해 빈 값 대신 추정치를 채워 넣지 않는다(Real Data Adapter
  v0.1이 이미 실천한 "Mock을 Real로 위장하지 않는다" 원칙과 동일 방향).
- **immutable execution record와 mutable live state 구분** — 실행이 끝난
  뒤 남는 기록(§4 Scope)은 이후 수정되지 않는 값으로 다뤄야 한다("실행 중"
  상태는 이 RFC의 Scope 밖이므로 mutable live state 자체를 이 RFC가 설계하지
  않는다 — 구분의 **필요성**만 기록한다).
- **persistence failure가 execution success를 자동으로 의미 변경하지
  않도록 경계 정의** — "기록이 저장되지 못했다"는 사실과 "실행이
  실패했다"는 사실은 서로 다른 축이어야 한다. 저장 실패 시 실행 결과
  자체를 FAILED로 재해석하는 로직은 이 RFC의 원칙과 충돌한다. 구체적
  실패 처리 방식은 확정하지 않는다.
- **partial/incomplete records 처리 방식** — Architecture Question으로
  남긴다(§10 Open Questions). 예: Stage 03에서 실행이 중단됐을 때 Stage
  01/02 기록만 저장할지, 전체를 버릴지는 이 RFC가 결정하지 않는다.

### 9. ADC-02 관계 (G)

ADC-02(Runtime 개념의 존폐)는 이 RFC가 변경하거나 재개하지 않는다. 다음
세 질문을 분석한다:

- **Runtime 유지안과 충돌하는가**: 충돌하지 않는다. Option B(§7)는 "실행이
  끝난 뒤 파일로 남긴다"는 wrapper 수준의 좁은 동작이며, Runtime이 유지되든
  아니든 그 wrapper는 `run_workflow()` 호출 지점을 감싸는 것만으로 성립한다
  — Runtime의 존재를 전제하지도, 배제하지도 않는다.
- **Runtime 제거안과 충돌하는가**: 충돌하지 않는다. 같은 이유로, Runtime이
  최종적으로 폐기되더라도 "실행 함수 호출을 감싸 결과를 기록한다"는 패턴
  자체는 무엇이 그 실행 함수를 호출하든(사람이 직접, 또는 향후 다른
  mechanism이) 유지 가능하다.
- **ADC-02 결정 이후에도 유지 가능한 Boundary인가**: 유지 가능해 보인다 —
  이 RFC의 Scope(§4)는 "무엇을 기록하는가"(Execution/Stage/Verification의
  형태)만 다루고 "누가/무엇이 실행을 관리하는가"(Runtime의 본질적 질문)는
  다루지 않는다. 다만 이 판단은 ADC-02가 실제로 어느 방향으로 결정되는지에
  따라 후속 ADC에서 재확인이 필요할 수 있다 — 이 RFC가 그 재확인을
  대신하지 않는다.

**결론(확정 아님)**: Option B는 ADC-02의 두 방향(유지/폐기) 어느 쪽과도
설계상 독립적으로 보인다. 그러나 이는 이 RFC의 분석이지, ADC-02를 해소하는
근거로 사용될 수 없다 — ADC-02는 계속 Open·NOW로 남는다.

## 5. Consequences & Risks

### 10. Governance (H)

이 RFC가 새로운 Architecture Boundary(영속 저장소 금지 조항의 Scoped 예외)를
제안하는 만큼, 최종 결론은 **RFC → ADC → ADR** 절차를 그대로 따라야 한다.
이 RFC 자체는 그 절차의 첫 단계(RFC)이며, 어떤 결정도 확정하지 않는다.

### 11. Architecture Constraints (재확인 — 변경 없음)

- `hqs/development/IMPLEMENTATION_RULES.md`의 금지 조항 — 이 RFC의 어떤
  Option도 이를 직접 해제하지 않는다. Option B조차 **예외 승인**을
  요구할 뿐, 금지 조항 자체를 고치지 않는다.
- `hqs/development/HANDOVER.md` "영속 저장소... 추가 금지" — Option B의
  선행조건.
- `docs/decisions/adc/ADC.md` ADC-02(Open) — §9에서 분석, 재개하지 않음.
- Development HQ Baseline v1.0의 **Public Contract**(`stages/contracts.py`의
  5개 Stage Contract, `KNOWN_CHECK_NAMES`, `check_results` 스키마, `status`
  집합, `blocking` 규칙) — 이 RFC는 그 **형태**를 그대로 참조만 할 뿐
  변경하지 않는다. `KNOWN_CHECK_NAMES` 확장·`check_results` 스키마 변경은
  이 RFC의 범위가 전혀 아니다.
- Command Center UX Contract(`data/adapters/adapters.js`의 11-function
  Adapter Contract) — 이 RFC는 UI/Adapter 코드를 변경하지 않으므로 이
  Contract에 손대지 않는다.
- §16.6 Workflow Adapter Contract (a) caller-owned 원칙 — §6.3에서 확인한 대로
  이 RFC의 방향과 정합적이며, 이 RFC가 그 원칙을 뒤집지 않는다.

### 13. Risks

- Option B를 좁게 연다고 선언해도, "History가 있으니 다음은 Live Progress도
  필요하다"는 Scope Creep 압력이 생길 위험 — RFC-0043 §23이 이미 지적한
  §16.3~§16.6의 점진 확장 전례(Execution Host → Multi-Task → Result Store →
  Workflow Adapter)가 반복될 수 있다.
- Evidence artifact reference(§4 항목 6)가 diff/log 원문까지 포함하도록
  확장되면, "파일 하나"가 사실상 Database에 준하는 대용량 저장소로
  변질될 위험 — 이 RFC는 **참조만** 저장 대상으로 제안하고 원문 보존은
  Scope 밖으로 남긴다.
- `check_results`가 Public Contract로 고정돼 있다는 사실이, 이 RFC의 좁은
  범위(저장 위치)를 넘어 그 스키마 자체의 확장(Security/Data-API 등)
  요구와 뒤섞일 위험 — 이 RFC는 스키마 변경을 전혀 다루지 않는다(§11).
- caller-owned persistence의 "caller"를 정하지 않은 채 구현이 먼저
  진행되면, 사실상 그 구현을 처음 만드는 쪽(Development HQ든 Command
  Center든)이 암묵적으로 owner가 되어 §6.4(Command Center는 Writer가 될 수
  없음) 원칙이 사후적으로 침해될 위험.

## 6. Open Questions & Change History

### 14. Open Questions

1. `hqs/development/HANDOVER.md`의 "영속 저장소 금지" 조항에 대한 Scoped
   예외를 Option B 범위(§4)로 한정해 승인할 수 있는가?
2. Persistence의 caller(저장 동작을 실제로 트리거·소유하는 주체)는
   Development HQ 쪽 CLI 확장인가, 별도의 독립 스크립트인가, 아니면 제3의
   계층인가?
3. Evidence를 Kernel Concept으로 신설할 것인가(§6.5), 아니면 HQ Public
   Contract의 저장 형태 문제로만 좁게 다룰 것인가?
4. partial/incomplete execution(Stage 중간에 중단된 실행)의 기록 처리
   방식은 무엇인가(§8 마지막 항목)?
5. Evidence artifact reference(§4 항목 6)가 가리키는 파일의 보존 기간·접근
   범위는 누가 정하는가?

### 15. Required ADC / ADR Follow-up

- 이 RFC가 후속 ADC로 승격된다면, 그 ADC는 §12의 Decision Candidate 문구
  그대로 **단일 Boundary Question**만 열어야 한다(§16.3~§16.6이 각각 그렇게
  해 온 선례를 따른다).
- 그 ADC는 ADC-02를 재개하지 않고, §16.3~§16.6의 어떤 Accept도 수정하지
  않아야 한다(Out of Scope 명시 필수 — `ADR-0003`/`ADC-0017`/`ADC-0019`의
  선례 형식을 따른다).
- Live Progress/Cancel/Retry/Resume은 §5 Non-Goals 그대로 그 ADC에도 포함하지
  않는다 — 별도의, 더 나중 RFC로 명시적으로 분리한다.
- `check_results`/`KNOWN_CHECK_NAMES` 등 Public Contract 변경은 이 트랙과
  완전히 별개 절차로 남긴다(§11).

---

Architecture Change: 없음 (이 RFC 자체가 변경이 아니라 분석 문서)
Contract Change: 없음
Implementation: 없음 (지시사항대로 코드/테스트/Dashboard/Persistence
컴포넌트 전부 미변경)
RFC: `RFC-0044`(본 문서, Proposed)
ADC: 없음 (열리지 않음 — 후속 ADC는 이 RFC가 결정하지 않는다)
ADR: 없음
PR: 없음

### Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md` | 이 RFC가 이어받는 Decision Candidate(§2) |
| ADR | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` | Out of Scope 명시 형식 선례(§15) |
| ADC | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` | Narrow Accept 선례(§6.2), Out of Scope 형식 선례(§15) |
| ADC | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` | Workflow Adapter caller-owned 원칙 선례(§0 대상, §15) |
| ADC | `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md` | Gate B/C 선행조건 인용(§2) |
| ADC | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` | Workflow Adapter 관련 문서 재확인 대상(§2.1) |
| ADC | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` | Workflow Adapter 관련 문서 재확인 대상(§2.1) |
| ADC | `docs/architecture/core/ADC-0002-kernel-definition.md`(원문은 `ADC-02`로 인용 — Kernel 트리, Runtime 개념의 존폐) | ADC-02(Open·NOW) 재확인 대상(§2, §9, §11) |
| ADC | `docs/core/execution-layer/ADC-0002-execution-result-contract.md`(원문은 `ADC-0002` Execution Result Contract로 인용 — Execution Layer 트리, ID 충돌 주의) | 무관 트랙 재확인(§2.1) |
| Reference | `docs/decisions/adc/ADC.md` | ADC-01~12 전체 Open 상태 재확인 대상(§2.1, §11) |
| Reference | `docs/architecture/baseline/BASELINE.md` | §16 Kernel Modules 재확인 대상 |
| Reference | `hqs/development/BASELINE.md` | Stage Data Contract, "Not Included" Runtime 재확인 대상 |
| Reference | `hqs/development/HANDOVER.md` | "영속 저장소... 추가 금지" 조항(§7 Option B 예외 대상, §11) |
| Reference | `hqs/development/IMPLEMENTATION_RULES.md` | 금지 표 재확인 대상 |
| Reference | `projects/dashboard-shell-mvp/devhq-command-center/data/real/export_real_snapshot.py`(원문은 `export_real_snapshot.py`로 인용) | Option B 재사용 대상 패턴(§7) |

### Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | RFC-0043 Option B(Narrow File-based Execution Records)를 좁은 Boundary Question으로 좁혀 Decision Candidate 제시(확정 아님) |
