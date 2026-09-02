# ADR-0008: Scoped Workflow Graph Execution Boundary(ADC-0019)의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0008` |
| 제목 | `ADC-0019`의 Accept 결정(Scoped Workflow Graph Execution Boundary의 **존재**, Scoped, Conditional)을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** (2026-09-02) — 이 ADR의 §Decision·§Migration Strategy에 정의된 `BASELINE.md` 변경(§16.6 Scoped Workflow Graph Execution 신설, 기존 §16.6 미결 항목 → §16.7 재배치, §17 Version v1.11 → v1.12)이 반영되었다. `IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·`ADC-0008`·§6·§16.1~§16.5는 무변경 |
| Context | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` — **Decision: A. Accept (Scoped, Conditional)**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md` §8(Boundary Question) |
| 관련 ADC | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` |
| 선행 ADR | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`(§16.3 신설 — 책임의 **존재만** 등재하고 `IMPLEMENTATION_RULES.md`는 건드리지 않은 선례, v1.7), `docs/architecture/core/ADR-0006`/`ADR-0007`(§16.4/§16.5 신설 — 같은 절차로 §16 Kernel Modules를 갱신하고 "미결 항목" 절을 한 칸 밀어낸 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0013`~`ADC-0017`/`ADR-0003`~`ADR-0007`(Execution Host 존재·명칭·구현 전략, Multi-Task, Result Store 게이트), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW), `docs/architecture/core/ADC-0008`(Runtime 존폐, Not Accepted) — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 `ADC-0019`가 이미 내린 Accept(Scoped, Conditional) 결정을 다시
논의하지 않는다. 새로운 철학이나 Architecture를 제안하지 않는다. 그
Accept 결정을 실제 Baseline 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다.

이 ADR의 핵심은 "LangGraph를 도입한다"가 **아니라** "Scoped Workflow
Graph Execution이라는 Architecture Boundary를 Baseline에 공식 등재한다"
이다. 구분:

| 단계 | 다루는 것 |
|---|---|
| `RFC-0019` | Boundary Question 개설 |
| `ADC-0019` | Boundary의 **존재** Accept (Scoped, Conditional) |
| **이 ADR** | 그 Accept의 **Baseline Governance 반영** — §16에 등재 |
| 후속 별도 결정 | LangGraph 채택 여부 / Workflow Adapter 명칭 / Public Port / 구현 전략 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0019`가 Accept 범위에서 명시하지 않은 것은 **하나도 반영하지
않는다.**

| 항목 | 근거 |
|---|---|
| 구현체 선택 — LangGraph 채택 여부, v1처럼 순차 함수 호출 유지 여부 | `ADC-0019` §Q8·§Decision 조건 6 — 별도 ADC |
| 이 책임의 명칭(Workflow Adapter / Workflow Engine 등) | `ADC-0019` §Q8·§Decision 조건 6 — Execution Host `ADC-0014` 선례를 따르는 별도 명명 절차 |
| Public Port / Interface 정의 | `ADC-0019` §Q7·§Decision 조건 5 — §14.1이 "Task 전달 책임"을 계약 범위 밖으로 두는 한 근거 없음 |
| 구현 전략(Adapter 래핑 방식, Checkpointer 백엔드 선택 등) | `ADC-0019` §Q8·§Decision 조건 6 — 별도 ADC |
| v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계 | `ADC-0019` §Q7·§Decision 조건 5 — 미해결로 유지, 후속 Architecture/ADR 조건 |
| `IMPLEMENTATION_RULES.md`의 Workflow/Scheduler/Runtime/Event Bus 금지 조항 전면 해제 | `ADC-0019` §Decision 조건 5·§Next Step 2 — 이 ADR은 해제하지 않는다(§4) |
| Execution Host(§16.3)·Multi-Task(§16.4)·Multi-Task Result Store(§16.5)의 범위·명칭·구현 전략·Accept 조건 변경 | `ADC-0019` §Q5·§Decision 조건 3 — 세 절 모두 문자 그대로 유지 |
| `hqs/investment/checkpoint.py`(§16.5 실증 사례)의 저장 전 검증 게이트 책임 재판단·대체 | `ADC-0019` §Q5 — 값 기반 Checkpoint/Resume과 계층이 다름, 동일 개념으로 취급하지 않음 |
| Model/LLM Provider 호출을 다루는 Engine Adapter(§16.2)의 내부 구조 | `ADC-0019` §Q5 — 별개 계층 |
| Multi-HQ, 자연어 요청 분해(`ADC-0018`, Defer) 범위로의 확장 | `ADC-0019` §Q4 — 단일 HQ 안의 Workflow 그래프 실행만 |
| `BASELINE.md` §6 Concept Model("Runtime")의 넓은 정의 채택·수정 | 선행 `ADR-0004` §3·`ADR-0006` §3·`ADR-0007` §3과 동일 판단 — §6 표·정의를 건드리지 않는다(§3) |
| `docs/decisions/adc/ADC.md` ADC-02 항목 수정, `docs/architecture/core/ADC-0008` Not Accepted 전복 | `ADC-0019` §Q8, 선행 `ADR-0003` §5·`ADR-0007` §Out of Scope와 동일 판단 — 별도 트랙, 별도 절차 |
| §16.7 미결 항목이 Defer로 기록한 Workflow **Kernel Module**(`ADC-0001` Module 2)의 재판단 | `ADC-0019` §Q8 — Module 존재 여부의 축은 ADC-02 축과 다르다. 이 ADR은 그 Defer를 재판단하지 않는다 |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16에 새 절 **16.6**을 신설해 Scoped Workflow Graph Execution Boundary를 Accept(Scoped, Conditional)로 기록한다. 기존 §16.6("미결 항목")은 내용 변경 없이 **§16.7**로 밀린다. §17 Version을 **v1.12**로 갱신하고 변경 이력 한 줄을 추가한다 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, Kernel Public Contract(§14),
Production Code는 이 ADR로 건드리지 않는다(§3·§4 참조).

### 2. `BASELINE.md` §16 갱신 내용

`ADC-0019`와 `RFC-0019`가 이미 정리한 것만 옮긴다. 새 판단을 만들지
않는다. 기존 §16.1(Governance)·§16.2(Execution Layer)·§16.3(Execution
Host)·§16.4(Multi-Task)·§16.5(Multi-Task Result Store)는 변경하지
않는다 — 본문 문자열도 그대로 유지한다(세 Accept의 범위는 이 ADR로
전혀 넓어지지 않는다, `ADC-0019` §Q5).

새로 삽입할 §16.6(기존 §16.6 "미결 항목" 앞에 삽입, 기존 절은 §16.7로
재배치):

```markdown
### 16.6 Scoped Workflow Graph Execution — 조건부 분기·Loop·값 기반 Checkpoint/Resume (Accept, Scoped, Conditional)

**책임**: HQ가 이미 정의한 Workflow 그래프와 이미 구성된 실행 단위를
입력으로 받아, 그 그래프가 기술하는 (a) 공유 실행 상태(State)의 보유,
(b) 단일 실행 단계(Node)의 진행, (c) 실행 중 상태에 따른 조건부
분기(Conditional Edge), (d) 조건 만족까지의 반복(Loop), (e) 진행 상태를
값으로 표현하고 호출자가 그 값을 보관했다 반환하면 이어서 진행하는 것
(값 기반 Checkpoint/Resume) — 이 다섯을 진행시키는 책임. 이 책임은
영속화 계층을 소유하지 않는다 — Checkpoint 값을 생산할 뿐, 그 값의
저장·복원은 호출자의 몫이다(§15.2 "호출자가 그 값을 들고 있는 것"
패턴과 동일). 실행 결과(성공/실패/취소에 준하는 상태)는 예외가 아닌
값으로 표현한다(§14.3 G-6).

**근거**: `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md`
§8이 연 좁은 Boundary Question("§16.3~16.5가 Accept한 범위를 넘어서는
Workflow 그래프 해석·실행 책임(조건부 분기·Loop·Checkpoint/Resume 포함)이
재검토 대상이 될 수 있는가")을,
`docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
가 v1 `ADR-0007`(`archive/v1`, Accepted — `LangGraphWorkflowEngine`
실사용 검증 + `test_workflow_adapter_reversibility.py`)와 이번 세션
PoC(`langgraph` 1.2.11 API 재확인) 2건의 Evidence를 근거로
Accept(Scoped, Conditional)했다. Evidence 2건은 동일 계보이고 Governance
v2 Rule B(3건 이상 독립 관찰)를 형식적으로 충족하지 않으나, 범위를
아래 A-IN으로 극소화하고 검증되지 않은 v2 공백을 조건으로 이월하며
Reversibility를 필수 불변조건으로 요구하는 것을 전제로 Accept됐다
(`ADC-0019` §Q2).

**A-IN (Kernel Module로서 다루는 것)**: State, Node, Conditional Edge,
Loop, 값 기반 Checkpoint/Resume — 위 "책임" 문단의 다섯 항목, 그리고
그 진행이 개입하는 구간("HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두
끝나는 시점")으로 한정된다(`ADC-0019` §Q3·§Decision 조건 1).

**A-OUT (이 Accept가 다루지 않는 것)**: HQ Routing/Registry, Policy
판정(PDP/PEP), Capability/Connector Discovery, Domain Lifecycle 전이
규칙, Event Bus 구독·라우팅, §16.5 Multi-Task Result Store 저장 전 검증
게이트, Multi-HQ 및 자연어 요청 분해(`ADC-0018` 범위), Registry/Discovery
일반화는 이 책임에 포함되지 않으며, 이 책임의 어떤 구현체도 이를
소유·재구현·대체하지 않는다(`ADC-0019` §Q4·§Decision 조건 2). "무엇을
실행할지"(Workflow 도메인 내용)는 §7 System Boundary대로 HQ가 채운다.

**§16.3~16.5와의 경계**: 이 책임은 Execution Host(§16.3)·Multi-Task(§16.4)·
Multi-Task Result Store(§16.5)의 확장이 아니라 별개 Concept이다
(`ADC-0019` §Q5). Execution Host는 이미 dispatch가 결정된 단일 실행
단위의 Execution Isolation을, Multi-Task는 이미 고정된 소수 독립 실행
단위의 Coordination을 다룬다 — 이 책임은 그 "고정" 자체가 실행 중 조건에
따라 달라지거나(Conditional Edge) 같은 단계가 반복되는(Loop) 경우, 즉
§16.4가 명시적으로 제외한 영역을 다룬다. §16.3~16.5의 범위·명칭·구현
전략·Accept 조건은 이 Accept로 전혀 변경되지 않는다.

**Checkpoint 용어 구분**: `hqs/investment/checkpoint.py`(§16.5 실증
사례)의 저장 전 검증 게이트와 이 책임의 값 기반 Checkpoint/Resume은
동일 개념이 아니다(`ADC-0019` §Q5) — 전자는 Result **저장** 시점의
유효성 게이트, 후자는 그래프 **실행** 상태의 pause/resume 메커니즘으로
계층이 다르며, 하나가 다른 하나를 함의하지 않는다. Investment HQ가
향후 이 책임을 실제로 쓰게 되더라도 `checkpoint.py`의 저장 전 검증
책임은 §16.5 그대로 유지되고 자동으로 대체되지 않는다.

**Reversibility — 필수 Architecture 불변조건**: 이 책임의 어떤 구현체를
제거하고 다른 구현체(최소한으로는 순차 함수 호출)로 교체해도, Kernel과
HQ가 정의하는 코드는 한 줄도 수정되지 않아야 한다. 구현체 고유
문법(`StateGraph`/`START`/`END`/Checkpointer API 등)은 이 책임의 경계
안에서만 쓰인다. 이 조건은 v1 `test_workflow_adapter_reversibility.py`가
실증한 선례를 근거로 하며, 이 책임을 실제로 구현하려는 후속 절차는
v2 맥락의 통합 테스트로 이 불변조건을 재현 검증해야 한다(`ADC-0019`
§Q6·§Decision 조건 4).

**미해결 상태로 유지되는 v2 공백 (Conditional)**: v1 `ADR-0007` 결정
2(Core 소유 Lifecycle 소비)·5(Team/Division 경계)·9(`IWorkflowEngine`
Port)·11(State Model)의 v2 대응 부재는 이 Accept로 해소되지 않는다
(`ADC-0019` §Q7·§Decision 조건 5). 이 네 공백이 후속 Architecture
절차(ADR 또는 별도 RFC)로 다뤄지기 전에는, 이 책임을 Kernel Public
Contract(§14)로 승격하거나 Production 구현에 착수할 수 없다. 결정 9의
공백 원인은 §14.1이 "Task 전달 책임"을 계약 범위 밖으로 두는 것이며,
이는 이 책임보다 상위의, 별도로 이미 Open인 질문이다.

**Workflow Module Defer(§16.7)와의 구분**: 이 절의 "Scoped Workflow
Graph Execution"은 §16.7 미결 항목이 Defer 상태로 기록한 **Workflow
Kernel Module**(`ADC-0001` Module 2 — Module 존재 여부의 축)과 다른
것이다. 이 절은 §6 "Runtime" 정의(ADC-02의 축) 중 조건부 분기·Loop
조율이라는 좁은 책임의 존재만 Accept하며, Workflow Module의 Defer
상태를 재판단하지 않는다.

**이 Accept가 결정하지 않는 것**: 구현체 선택(LangGraph 채택 여부 포함),
이 책임의 명칭(Workflow Adapter / Workflow Engine 등), Public Port 정의,
구현 전략은 모두 별도 절차(RFC → ADC → ADR)로 남는다 — Execution
Host가 존재(`ADC-0013`) → 명명(`ADC-0014`) → 구현 전략(`ADC-0015`)
3단계로 분리한 선례를 그대로 따른다. `docs/decisions/adc/ADC.md`
ADC-02(Runtime 존폐, Open·NOW)와 `docs/architecture/core/ADC-0008`(넓은
"유지 대 대체", Not Accepted)은 이 Accept로 갱신·전복되지 않는다 —
이 책임은 §6 "Runtime" 정의 중 "조건부·반복 조율" 조각 하나일 뿐이다
(`ADC-0019` §Q8).

**Production 구현과의 관계**: 이 Accept는 위 A-IN 범위의 **존재**만
등재하며, Production 구현 착수를 승인하지 않는다.
`hqs/development/IMPLEMENTATION_RULES.md`의 Workflow Parser 구현 금지,
Scheduler/우선순위/Workflow orchestration/Dynamic Routing(조건부 목적지
선택·Agent 동적 배분) 및 §6 넓은 Runtime 구현 금지, Stage 재진입
(Retry/Re-entry)·조건부 Stage 실행 구현 금지, Event Bus 구현 금지
조항은 이 Accept로 해제되지 않는다. v1 `ADR-0007` 결정 2/5/9/11 공백
해소와 Reversibility의 v2 재현 검증 이후, 별도 ADR이 A-IN 범위에 한해
그 금지의 Scoped 해제 여부를 판단한다(`ADC-0019` §Next Step 2·5).
```

기존 §16.6("미결 항목")는 내용 변경 없이 §16.7로 재배치한다
(Workflow/Memory/Event Bus Defer 상태 기록 — `ADC-0019`는 이 상태를
재판단하지 않는다).

### 3. `BASELINE.md` §6 Concept Model 표 갱신 여부

**변경하지 않는다.** `ADR-0004` §3·`ADR-0006` §3·`ADR-0007` §3이 이미
"§6에 Execution Host/Multi-Task/Result Store 게이트를 추가하지 않기로"
결정했고, 그 근거(이름 귀속을 암묵적으로 확정하는 효과를 피한다,
`BASELINE.md` §6의 "Runtime" 넓은 정의는 ADC-02가 Open으로 두고 있다)는
이 Scoped Workflow Graph Execution 책임에도 그대로 적용된다 — 이 책임은
§6의 "Runtime" 항목을 재명명·구체화한 것이 아니라 그 넓은 정의 중
조건부·반복 조율이라는 좁은 조각 하나다(`ADC-0019` §Q8). §6은 이번에도
무변경.

### 4. `hqs/development/IMPLEMENTATION_RULES.md` 변경 필요성 검토

`ADC-0015`/`ADR-0005`(Execution Host)와 `ADC-0016`/`ADR-0006`(Multi-Task)는
각각 `IMPLEMENTATION_RULES.md`의 금지 표를 Scoped 해제하고 "구현 허용
범위" 절을 신설했다 — 두 경우 모두 **그 Accept가 Production 구현 착수를
허용했고**, 그 착수를 금지 표가 막고 있던 상황이었다.

**이 ADR은 그 선례를 따르지 않는다** — `ADC-0019`는 구조가 다르다.

- `ADC-0019`는 A-IN 범위의 **존재**만 Accept했고, **Production 구현
  착수를 명시적으로 금지**한다(`ADC-0019` §Decision 조건 5): v1 `ADR-0007`
  결정 2/5/9/11의 v2 공백이 후속 Architecture 절차로 해소되고
  Reversibility가 v2 통합 테스트로 재현 검증되기 전까지 Public Contract
  승격도 구현 착수도 불가하다. 따라서 지금 Scoped 해제할 대상이 없다 —
  해제하면 `ADC-0019`가 금지한 것을 이 ADR이 허용하는 모순이 된다.
- 이 상황은 `ADR-0003`(v1.7)과 같다 — `ADR-0003`은 Execution Host의
  **존재만** §16.3에 등재하고 `IMPLEMENTATION_RULES.md`는 건드리지
  않았으며, Scoped 해제는 구현 전략이 확정된 뒤 `ADR-0005`(v1.9)가 별도로
  수행했다. 이 ADR은 그 2단계 선례를 따른다: 이번에는 등재만, Scoped
  해제는 후속 ADR.
- `IMPLEMENTATION_RULES.md`의 관련 금지 조항 — Workflow Parser 구현 금지
  (line 9), "Scheduler/우선순위/Workflow orchestration/Dynamic Routing
  (조건부 목적지 선택·Agent 동적 배분) 및 §6 넓은 Runtime 구현 금지"
  (line 13), "Stage 재진입(Retry/Re-entry)·조건부 Stage 실행 구현 금지"
  (line 14), Event Bus 구현 금지(line 19) — 은 `ADC-0019` A-IN의 실제
  구현(조건부 분기·Loop·그래프 진행)을 직접 덮는다. 이 조항들은 그대로
  **유지**되어야 하며, 이 ADR은 이를 해제하지 않는다.

**결론(검토 결과)**: **이 ADR은 `IMPLEMENTATION_RULES.md`를 변경하지
않는다.** 금지 조항은 전면 유지된다. §16.6 등재(책임 경계의 존재)와
`IMPLEMENTATION_RULES.md`의 구현 금지는 공존한다 — `ADR-0003`이 §16.3을
등재하면서도 구현 금지를 유지했던 것과 같다.

**향후 Scoped exception의 정확한 조건과 범위**(이 ADR이 허용하는 것이
아니라, 후속 ADR이 판단할 때 충족해야 하는 조건):

1. v1 `ADR-0007` 결정 2·5·11(Team/Division 부재로 인한 Lifecycle 소비·
   경계·State Model 공백)이 후속 Architecture 절차(ADR 또는 별도 RFC)로
   해소됨.
2. v1 `ADR-0007` 결정 9(`IWorkflowEngine` Port) 공백의 상위 원인인
   §14.1 "Task 전달 책임"의 계약 범위 문제가 별도로 정리됨.
3. Reversibility 필수 불변조건이 v2 맥락의 통합 테스트로 재현 검증됨.
4. 위 1~3 충족 이후, 별도 ADR이 **A-IN 범위(State/Node/Conditional
   Edge/Loop/값 기반 Checkpoint·Resume, HQ가 정의한 고정 Workflow
   그래프의 실행 진행)에 한해** `IMPLEMENTATION_RULES.md` line 9/13/14를
   Scoped 해제한다. 이때에도 Scheduler/우선순위/Dynamic Routing(Agent
   동적 배분)/§6 넓은 Runtime(Workflow 참조 전체)/Event Bus는 계속 금지
   상태로 유지한다(A-OUT).

이 조건 서술은 후속 절차의 참고 기준이며, 이 ADR이 그 exception을 미리
허가하지 않는다.

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.11 | **v1.12** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 `RFC-0019` → `ADC-0019` → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0007`의 선례와 동일하다.

**Minor 증가(v1.12)를 택한 이유**: §16에 새 절(16.6)을 신설하되 그
책임의 범위를 의도적으로 좁게 한정했고(A-IN), 다른 어떤 절의 기존
문언도 수정하지 않았다(§16.1~§16.5 무변경, §6 무변경). `IMPLEMENTATION_RULES.md`도
변경하지 않았다(§4). 선행 `ADR-0006`(신설, v1.10)·`ADR-0007`(신설,
v1.11)과 같은 granularity로 Minor 단위로 기록한다.

**H1 제목줄 관련 참고(이 ADR이 수정하지 않음)**: `BASELINE.md` 1행의
제목은 현재 `# Jarvis OS Architecture Baseline v1.8`로, §17 Version
표(v1.11)와 값이 다르다 — v1.9~v1.11 갱신 시 제목줄이 함께 갱신되지
않은 기존 불일치다. 선행 `ADR-0003`~`ADR-0007`은 모두 §17 표만 갱신하고
제목줄은 손대지 않았다. 이 ADR도 같은 관행을 따라 §17 표만 v1.12로
갱신하며, 제목줄 불일치의 정정은 이 ADR의 범위 밖이다(별도로 다뤄야
하는 사항으로 남긴다).

### 6. Migration Strategy

1. `BASELINE.md`:
   - §16.5(Multi-Task Result Store)와 기존 §16.6("미결 항목") 사이에
     새 §16.6(Scoped Workflow Graph Execution)을 §2의 블록 그대로
     삽입한다.
   - 기존 §16.6("미결 항목")을 §16.7로 재배치한다(본문 문자열 무변경).
   - §17 Version 표의 `Version` 값을 v1.11 → v1.12로 바꾸고, 변경 이력
     맨 위에 다음 한 줄을 추가한다:

     > `| v1.12 | §16에 §16.6 Scoped Workflow Graph Execution(조건부 분기·Loop·값 기반 Checkpoint/Resume) 신설 — Accept(Scoped, Conditional). §16.3~16.5 무변경(Execution Host/Multi-Task/Result Store 게이트 범위·명칭·구현 전략 불변). Reversibility를 필수 Architecture 불변조건으로 등재. A-OUT(Routing/Registry·Policy·Discovery·Domain Lifecycle·Event Bus·§16.5 저장 게이트·Multi-HQ decomposition·Registry 일반화) 명시 제외. v1 ADR-0007 결정 2/5/9/11의 v2 공백은 미해결로 유지 — 해소 전 Public Contract 승격·Production 구현 착수 불가. 구현체 선택(LangGraph 포함)·명칭·Public Port·구현 전략은 별도 결정. 기존 §16.6(미결 항목)은 §16.7로 재배치. §6 Concept Model 표·§16.1~§16.5는 변경하지 않음. IMPLEMENTATION_RULES.md는 금지 조항 유지(무변경). 근거: docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md |`

2. `hqs/development/IMPLEMENTATION_RULES.md` — 변경하지 않는다(§4).
3. `docs/decisions/adc/ADC.md`(ADC-02), `docs/architecture/core/ADC-0008` —
   변경하지 않는다.
4. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(신설 최상위 절 없음, §16 내부만 재배치).
   - §6 Concept Model 표·각주, §14(Kernel Public Contract), §15.2,
     §16.1~§16.5가 문자 그대로 변경되지 않았는지 확인.
   - 새 §16.6 본문이 §16.3~16.5의 어떤 문장도 인용·수정으로 변형하지
     않는지 확인(경계 서술은 참조만).
   - `IMPLEMENTATION_RULES.md`가 문자 그대로 무변경인지 확인(`git diff`
     0줄).
   - `git status`로 `core/`·`dashboard/`(Production 소스),
     `hqs/`(Production 구현), `docs/decisions/`가 무변경인지 확인.
5. 커밋 — 이 ADR과 위 `BASELINE.md` 변경을 함께 커밋한다(승인·반영
   완료, 커밋만 남음).

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.11 → v1.12가 되고, §16.6이
  Scoped Workflow Graph Execution(조건부 분기·Loop·값 기반 Checkpoint/
  Resume, A-IN 다섯 항목)의 **존재**를 Accept(Scoped, Conditional)로
  등재한다. 기존 §16.6(미결 항목)은 §16.7로 재배치된다.
- Reversibility가 이 책임의 **필수 Architecture 불변조건**으로 Baseline에
  기록된다 — 후속 구현 절차는 v2 통합 테스트로 이를 재현 검증해야 한다.
- `hqs/development/IMPLEMENTATION_RULES.md`는 **무변경**이다 — `ADC-0019`가
  구현 착수를 금지하므로 Scoped 해제할 대상이 없다(§4). Workflow Parser/
  Scheduler/Workflow orchestration/조건부 목적지 선택/Stage 재진입·조건부
  Stage 실행/Event Bus 구현 금지는 전면 유지된다.
- §6 Concept Model의 "Runtime" 항목, `docs/decisions/adc/ADC.md`의
  ADC-02(Open·NOW), `docs/architecture/core/ADC-0008`(Not Accepted)은 이
  ADR로 전혀 변경되지 않는다.
- Execution Host(§16.3)·Multi-Task(§16.4)·Multi-Task Result Store(§16.5)의
  범위·명칭·구현 전략·Accept 조건은 이 ADR로 전혀 바뀌지 않는다.
- `hqs/investment/checkpoint.py`의 저장 전 검증 게이트 책임은 §16.5 그대로
  유지되며, 이 책임의 값 기반 Checkpoint/Resume과 동일 개념으로 취급되지
  않는다.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface를 정의하지
  않았다. §14.1의 "Task 전달 책임" 미결 상태도 그대로다.
- v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계, 구현체 선택(LangGraph 포함),
  명칭, Public Port, 구현 전략은 모두 이 ADR 이후에도 별도 절차(후속
  RFC/ADC/ADR)를 거쳐야 한다.
- 이 Accept는 영구 고정이 아니다 — `ADC-0019` §Risks·재검토 조건(다른
  계보/ v2 프로덕션 관찰로 독립 3건 도달 시 Conditional 완화 재판단 등)이
  이 ADR 이후에도 그대로 유효하다.
- 이 ADR은 **Accepted** 상태이며, §Decision·§Migration Strategy의
  `BASELINE.md` 변경(§16.6 신설, §16.6 미결 항목 → §16.7, §17 v1.12)이
  반영되었다. 커밋은 별도로 진행한다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(Scoped, Conditional)** — `BASELINE.md`
  §16에 조건부 분기·Loop·값 기반 Checkpoint/Resume 실행 진행이라는 새
  책임 경계가 좁은 범위로 처음 등재된다. Component 설계(§10 Out of
  Scope)에는 영향을 주지 않는다 — 책임의 존재와 A-IN/A-OUT 경계,
  Reversibility 불변조건만 기록했을 뿐, 명칭·Interface·구현 전략은 여전히
  미정이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경. §14.1의 "Task 전달 책임" 미결
  상태가 이 책임의 Public Contract 승격을 계속 막는다(조건 이월).
- **Kernel Impact**: **있음(제한적, 조건부)** — Kernel Concept 목록에
  이름 없는 책임 하나가 추가되나(Execution Host·Multi-Task·Result Store
  게이트와 별개, A-IN 다섯 항목에 한정), 이것이 Public Contract나
  Component로 구체화되려면 v1 결정 2/5/9/11 공백 해소와 Reversibility v2
  재현 검증을 거친 별도 ADR이 필요하다.

## Governance Chain 검증

`RFC-0019`(Boundary Question만 개설, 판단은 후속 절차로 위임 — 개설 당시
Proposed, 이후 `ADC-0019` → 이 ADR로 이어짐) → `ADC-0019`(Accept, Scoped·
Conditional — 그 질문에 답함, 구현체·명칭·Public Port·구현 전략·v1 결정
2/5/9/11 재설계는 명시적으로 제외) → 이 ADR(Accepted — `ADC-0019`의
Decision을 `BASELINE.md` §16.6으로 반영, 새로운 결정 추가 없음). 세
문서가 각각 인용하는 근거가 상위 문서의 범위를 벗어나지 않는지
확인했다.

- `RFC-0019`는 답을 제시하지 않고 질문만 열었다(§8) — 위반 없음.
- `ADC-0019`는 `RFC-0019`가 연 질문에만 답했고, `RFC-0019`가 제외한
  항목(구현체 선택, 명칭, Public Port, 구현 전략, v1 결정 2/5/9/11
  재설계, §16.3~16.5 재론, ADC-02/ADC-0008)을 새로 확정하지 않았다
  (`ADC-0019` §Decision 조건 6·§Q8) — 위반 없음.
- 이 ADR은 `ADC-0019`의 Decision(A-IN, A-OUT, 조건 3~6)을 그대로
  옮겼을 뿐, `ADC-0019`가 판단하지 않은 것(구현체·명칭·Port·구현 전략,
  v1 결정 재설계, §16.3~16.5 확장, §6 넓은 정의, ADC.md, ADC-0008,
  Contract 신설, `IMPLEMENTATION_RULES.md` 해제)을 새로 결정하지 않았다
  (§Out of Scope, §3, §4) — 위반 없음.
- §16.6 신설 블록(§2)이 §16.3~16.5의 문장을 인용은 하되 수정·재정의하지
  않음을 확인했다(§6 Migration Strategy 검증 절차 3).
- `IMPLEMENTATION_RULES.md` line 9/13/14/19의 금지가 `ADC-0019` A-IN의
  구현을 덮으며, 이 ADR이 그 금지를 유지한다는 것이 `ADC-0019` §Decision
  조건 5(구현 착수 불가)와 일치함을 확인했다(§4) — 충돌 없음.

## Self Review

- `ADC-0019`가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(구현체 선택, 명칭, Public Port, 구현 전략, v1
  결정 2/5/9/11 재설계, `IMPLEMENTATION_RULES.md` 전면 해제, §16.3~16.5
  확장, §6 넓은 정의, ADC.md, ADC-0008, Production Code)은 손대지
  않았다.
- Scoped Workflow Graph Execution Boundary의 **존재**만 Baseline에
  반영했는가 — **Pass**(§2 §16.6 블록) — 새 판단을 추가하지 않고
  `ADC-0019`의 A-IN/A-OUT·조건을 그대로 옮겼다.
- A-IN을 State/Node/Conditional Edge/Loop/값 기반 Checkpoint·Resume
  다섯으로 한정했는가 — **Pass**(§2 "A-IN" 문단).
- A-OUT(Routing/Registry, Policy(PDP/PEP), Discovery, Domain Lifecycle,
  Event Bus, §16.5 Result Store 게이트, Multi-HQ decomposition, Registry
  일반화)을 명시 제외했는가 — **Pass**(§2 "A-OUT" 문단).
- §16.3~16.5 기존 결정을 변경했는가 — **아니오**(§2 서두, §Governance
  Chain 검증) — 본문 문자열을 문자 그대로 유지한다.
- Investment `checkpoint.py`와 값 기반 Checkpoint/Resume을 동일 개념으로
  취급했는가 — **아니오**(§2 "Checkpoint 용어 구분" 문단).
- Reversibility를 필수 Architecture 불변조건으로 유지했는가 —
  **Pass**(§2 "Reversibility" 문단, §Consequences).
- v1 `ADR-0007` 결정 2/5/9/11의 v2 gap을 미해결 상태로 유지했는가 —
  **Pass**(§2 "미해결 상태로 유지되는 v2 공백" 문단, §Out of Scope).
- 그 gap 해소 전 Public Contract 승격·Production 구현을 허용했는가 —
  **아니오**(§2 동일 문단, §4, §Architecture/Contract/Kernel 영향).
- `IMPLEMENTATION_RULES.md`의 Workflow/Scheduler/Runtime/Event Bus 금지를
  전면 해제했는가 — **아니오**(§4) — 무변경, 금지 전면 유지. 향후 Scoped
  exception의 조건과 범위만 참고로 서술했다.
- ADC-02·ADC-0008을 이 ADR에서 해결했는가 — **아니오**(§Out of Scope,
  §3, §Governance Chain 검증).
- LangGraph 채택 여부/명칭/Public Port/구현 전략을 확정했는가 —
  **아니오**(§Out of Scope, §2 "이 Accept가 결정하지 않는 것" 문단).
- §6 "Runtime" 항목을 재명명·수정했는가 — **아니오**(§3).
- 새 최상위 절 또는 §16 내부 재배치 외의 변경을 계획했는가 — **아니오**
  (§1, §6) — 기존 §16.6을 §16.7로 재배치하고 §17 표를 갱신하는 것
  외에는 없다.
- `BASELINE.md`를 실제로 수정했는가 — **예(승인 반영)** — §2의 §16.6
  블록을 §16.5와 기존 §16.6 사이에 삽입하고, 기존 §16.6(미결 항목)을
  §16.7로 재배치하고, §17 Version을 v1.12로 갱신하고 변경 이력 한 줄을
  추가했다. §6·§14·§15.2·§16.1~§16.5·`IMPLEMENTATION_RULES.md`·`ADC.md`·
  `ADC-0008`은 무변경이다. 커밋은 별도.
