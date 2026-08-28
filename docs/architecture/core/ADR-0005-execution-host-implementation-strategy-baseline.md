# ADR-0005: Execution Host 구현 전략(ADC-0015)의 Baseline·Rules 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0005` |
| 제목 | `ADC-0015`의 Conditional Accept 결정(Execution Host 구현 전략 = Process 1차/Subprocess 대안, Thread 배제)을 Architecture Baseline·Development HQ Rules에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md` — **Decision: A. Conditional Accept**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0015-execution-host-implementation-strategy.md` §1(Boundary Question)·§4(Decision Candidate) |
| 관련 ADC | `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md` |
| 선행 ADR | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`(§16.3 신설), `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`(§16.3 명칭 반영, 같은 절차로 §16 Kernel Modules를 갱신한 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`(존재, Accept Scoped), `docs/architecture/core/ADC-0014-execution-responsibility-naming.md`(명칭, Accept), `docs/architecture/core/ADC-0008-runtime-existence-boundary.md`(넓은 범위 Runtime 존폐, Not Accepted), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW, 이 ADR이 변경하지 않음) |

이 ADR은 `ADC-0015`가 이미 내린 Conditional Accept 결정(구현 전략
= Process 1차·Subprocess 대안, Thread 배제, "동일 Target 동시 실행"
조건 한정, 비용/운영 Evidence에 따라 재검토 가능)을 **다시 논의하지
않는다.** 새로운 Decision을 추가하지 않는다. 그 Conditional Accept
결정을 실제 `BASELINE.md`·`IMPLEMENTATION_RULES.md` 문서 변경으로
옮기기 위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0015`가 Accept 범위에서 명시하지 않은 것은 **하나도 반영하지
않는다.**

| 항목 | 근거 |
|---|---|
| Scheduler/Engine Gateway 등 대체 구조 설계 | `ADC-0015` §Out of Scope |
| Multi-Task/Workflow orchestration | `ADC-0015` §Out of Scope — Scheduler/Multi-Task/Workflow 구현 금지는 계속 유지 |
| `BASELINE.md` §6 Concept Model "Runtime" 항목의 구현 허용 여부 | `ADC-0015` §Out of Scope, `ADC-0014` §Q2가 이미 별개 Concept으로 판정 — §6 "Runtime"(넓은 정의) 구현을 허용하는 결정이 아니다 |
| `docs/decisions/adc/ADC.md`의 ADC-02(Jarvis OS 수준 Runtime 존폐) 항목 수정 | `ADC-0015` §Out of Scope, `ADR-0001`~`ADR-0004` 선례와 동일 — 별도 트랙 |
| "동일 Target" 자동 판별 메커니즘 설계 | `ADC-0015` §Out of Scope — 판별은 구현자 재량/후속 검증 대상으로 남긴다 |
| 구현 전략의 비용(Worker 기동, 직렬화 오버헤드) 실측 | `ADC-0015` §Out of Scope |
| Contract/Public Interface 신규 정의 | `ADC-0015`가 정의하지 않았다 — Kernel Public Contract(§14)는 무변경 |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.3에 "구현 전략" 문단 신설(Process 1차·Subprocess 대안·Thread 배제, Conditional Accept). "이 Accept가 결정하지 않는 것"·"Production 구현과의 관계" 문단을 그 반영에 맞춰 갱신. §17 Version을 v1.9로 갱신 |
| `hqs/development/IMPLEMENTATION_RULES.md` | "Runtime 구현 금지" 행을 "Scheduler/Multi-Task/Workflow 및 §6 넓은 Runtime 구현 금지"로 좁히고, Execution Host의 Scoped 허용 조건을 명시하는 새 절 추가 |

그 외 어떤 파일도 변경하지 않는다(§Out of Scope). `docs/decisions/adc/ADC.md`,
Kernel Public Contract(§14), Production Code는 이번에도 건드리지
않는다.

### 2. `BASELINE.md` §16.3 갱신 내용

기존 "**명칭**" 문단 다음, "**이 Accept가 결정하지 않는 것**" 문단
앞에 새 문단 "**구현 전략**"을 삽입한다.

```markdown
**구현 전략**: 이 책임을 실현하는 구현 전략은 **Process를 1차,
Subprocess를 대안으로 Conditional Accept**했다(`docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`).
적용 조건은 "동일 Target(프로세스 전역 상태를 공유하는 대상)을
동시 실행할 가능성이 있는 경로"로 한정되며, 이 조건에서 **Thread는
명시적으로 배제**한다. 이 조건 밖(서로 다른 Target만 실행하는
경로)까지 Process를 강제하지 않는다. 이 Accept는 **Conditional**
이다 — 비용(Worker 기동·직렬화 오버헤드) 또는 운영 중 새로 관찰되는
Evidence에 따라 재검토 대상이다(`ADC-0015` §Risks·재검토 조건).
```

기존 "**이 Accept가 결정하지 않는 것**" 문단에서 "구현 전략
(Process/Thread/Subprocess)," 부분을 제거한다(더 이상 전면 Open이
아니므로 — Process/Subprocess/Thread에 대한 판단은 위 "구현 전략"
문단으로 옮겨졌다). 나머지("Scheduler/Engine Gateway 등 대체
구조와의 비교", "§6의 원래 넓은 정의로의 확장 여부")는 그대로
유지한다 — `ADC-0015`가 다루지 않은 영역이다.

교체 후 문단:

```markdown
**이 Accept가 결정하지 않는 것**: Scheduler/Engine Gateway 등 대체
구조와의 비교, `BASELINE.md` §6의 원래 넓은 정의(Workflow 참조,
Multi-Task를 Agent에게 배분)로의 확장 여부, "동일 Target" 자동
판별 메커니즘, 구현 전략의 비용 실측은 모두 별도 절차(RFC → ADC →
ADR 또는 후속 검증)로 남는다(`ADC-0015` §Out of Scope).
`docs/decisions/adc/ADC.md` ADC-02가 다루는 "유지 대 대체" 구도와
이름 충돌 문제(`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`)는
이 Accept로 해소되지 않는다.
```

"**Production 구현과의 관계**" 문단을 다음으로 교체한다.

```markdown
**Production 구현과의 관계**: 이 Accept(명칭·구현 전략 확정
포함)는 Execution Host 범위(Process 1차·Subprocess 대안, "동일
Target 동시 실행" 조건, Thread 배제)에 한해 구현 착수를 허용한다
(`hqs/development/IMPLEMENTATION_RULES.md`, `ADC-0015` §Q4).
Scheduler/Multi-Task/Workflow, `BASELINE.md` §6의 넓은 "Runtime"
구현은 여전히 금지 상태다 — `docs/decisions/adc/ADC.md`의
ADC-02(Runtime 존폐)가 Open으로 남아 있는 한 그대로 유효하다.
```

### 3. `BASELINE.md` §6 Concept Model 표 갱신 여부

**변경하지 않는다.** `ADR-0004` §3이 이미 "§6에 Execution Host를
추가하지 않기로" 결정했고, 그 판단은 명칭 확정에 대한 것이었다.
이번 구현 전략 Conditional Accept도 §16.3 범위를 벗어나지 않으므로
`ADR-0004` §3의 판단을 재론할 근거가 없다 — §6은 이번에도 무변경.

### 4. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 내용

기존 "금지 사항" 표의 다음 행을 교체한다.

```markdown
| Runtime 구현 금지 | Runtime 개념 자체가 Open Decision(ADC-02)이다 |
```

교체 후:

```markdown
| Scheduler/Multi-Task/Workflow 및 §6 넓은 Runtime 구현 금지 | Multi-Task orchestration과 Workflow 참조·배분은 `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 존폐)가 여전히 Open이다. Execution Host(§16.3)의 Scoped 허용 범위는 아래 "Execution Host 구현 허용 범위" 절 참조 |
```

"금지 사항" 표 바로 다음에 새 절을 신설한다.

```markdown
## Execution Host 구현 허용 범위 (Scoped, ADC-0015)

`docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`
가 Conditional Accept한 범위에 한해, 아래 조건을 모두 지키는 경우
Execution Host 구현을 허용한다.

- 적용 대상: "동일 Target(프로세스 전역 상태를 공유하는 대상)을
  동시 실행할 가능성이 있는 경로"에서 격리를 제공하는 최소 구현만
  허용한다.
- 구현 전략: Process를 1차로, Subprocess를 대안으로 사용한다.
  **Thread는 이 경로에서 사용하지 않는다**(`ADC-0015` §Q0·§Q1).
- 이 허용은 Scheduler, Multi-Task/Workflow orchestration,
  `BASELINE.md` §6의 넓은 "Runtime"(Workflow 참조, Multi-Task를
  Agent에게 배분) 구현을 포함하지 않는다 — 이들은 여전히 금지
  상태다(위 표).
- 이 허용은 **Conditional**이다 — 비용 또는 운영 중 새로 관찰되는
  Evidence에 따라 `ADC-0015`의 재검토 대상이며, 재검토 결과에 따라
  이 절도 함께 갱신되어야 한다.
- 새 Public Interface/Contract를 정의하지 않는다 — Kernel Public
  Contract(§14)는 이 허용과 무관하게 무변경이다.
```

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.8 | **v1.9** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0015 → ADC-0015 → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0004`의 선례와 동일하다.

**Minor 증가(v1.9)를 택한 이유**: 새 최상위 절을 신설하지 않고,
기존 §16.3에 문단 하나를 추가하고 기존 두 문단을 갱신했다(신설
절 없음, §6 무변경). 선행 `ADR-0004`(기존 §16.3 제목·본문 일부
교체, v1.8)와 같은 granularity로 Minor 단위로 기록한다.

### 6. Migration Strategy

1. `BASELINE.md` — §16.3에 "구현 전략" 문단 삽입, "이 Accept가
   결정하지 않는 것"·"Production 구현과의 관계" 문단 교체(§2), §6
   무변경 확인(§3), 변경 이력 한 줄 추가, v1.9 갱신.
2. `hqs/development/IMPLEMENTATION_RULES.md` — "Runtime 구현 금지"
   행 교체, "Execution Host 구현 허용 범위" 절 신설(§4).
3. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(신설 최상위 절 없음, §16 내부도 재배치 없음).
   - §6 Concept Model 표·각주, §14(Kernel Public Contract)가 문자
     그대로 변경되지 않았는지 확인.
   - `IMPLEMENTATION_RULES.md`의 나머지 금지 항목(Workflow Parser,
     Scheduler, Registry, Engine Gateway/Routing, Policy, Memory
     Service, Event Bus, Multi-HQ/Multi Engine, Baseline 수정
     금지)이 문자 그대로 유지되는지 확인.
   - `git status`로 `core/`·`dashboard/`(Production 소스),
     `hqs/development/mvp/`(Production 구현), `docs/decisions/adc/ADC.md`
     이하에 변경이 없는지 확인.
   - `git diff -- hqs/ core/ dashboard/`가 `IMPLEMENTATION_RULES.md`
     외에는 0줄인지 확인.
4. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.8 → v1.9가 되고,
  §16.3이 이제 구현 전략(Process 1차·Subprocess 대안, Thread 배제,
  Conditional)까지 명시한다.
- `hqs/development/IMPLEMENTATION_RULES.md`가 Execution Host
  범위(Process/Subprocess, "동일 Target 동시 실행" 조건)에 한해
  구현을 허용하고, Scheduler/Multi-Task/Workflow 및 §6 넓은
  Runtime 구현은 계속 금지한다.
- §6 Concept Model의 "Runtime" 항목, `docs/decisions/adc/ADC.md`의
  ADC-02(Open·NOW)는 이 ADR로 전혀 변경되지 않는다.
- `ADC-0008`(Not Accepted)·`ADC-0012`(DEFER)는 이 ADR로 뒤집히거나
  재개되지 않는다.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface를
  정의하지 않았다.
- 실제 구현 착수는 이 ADR 이후 가능해지지만, 이 ADR 자체가 구현을
  수행하지는 않는다 — Production Code(`core/`, `hqs/`, `dashboard/`)
  는 전혀 수정하지 않는다.
- 이 Conditional Accept는 영구 고정이 아니다 — 비용/운영 Evidence에
  따라 `ADC-0015`가 재검토 대상으로 명시한 조건이 이 ADR 이후에도
  그대로 유효하다.
- 이 ADR은 **승인되었으며**, §Decision에 정의된 실제 문서 변경이 이
  승인에 따라 실행된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(구현 전략 반영뿐)** — §16.3이
  가리키는 책임의 범위는 전혀 바뀌지 않는다. 그 책임을 어떻게
  실현할지에 대한 지침이 추가됐을 뿐이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경.
- **Kernel Impact**: **없음(추가적)** — `ADR-0003`/`ADR-0004`가
  이미 등재한 책임과 명칭에 구현 전략 지침을 붙였을 뿐, 새 책임이나
  새 Component를 추가하지 않았다.

## Governance Chain 검증

`RFC-0015`(Proposed, 5개 Prototype Evidence 비교·권고만 — Decision
아님) → `ADC-0015`(Conditional Accept — Process 1차·Subprocess
대안·Thread 배제, `IMPLEMENTATION_RULES.md` Scoped 해제 결정) → 이
ADR(Accepted — Baseline·Rules에 반영, 새로운 결정 추가 없음).

- RFC-0015는 비교·권고만 하고 확정하지 않았다(§4 "확정 아님") —
  위반 없음.
- ADC-0015는 RFC-0015가 후속 ADC에 위임한 세 질문(최종 채택 방향,
  Thread 배제 근거 처리, 구현 금지 해제 여부 — RFC-0015 §Next Step
  1·2·3)에만 답했다(§Q0~§Q4) — RFC-0015의 Out of Scope(Scheduler·
  Multi-Task/Workflow·§6 Runtime 관계·ADC-02·ADC-0012 재론·비용
  실측·자동 판별 설계)를 건드리지 않았다 — 위반 없음.
- 이 ADR은 ADC-0015의 Decision을 그대로 옮겼을 뿐, ADC-0015가
  판단하지 않은 것(Scheduler·Multi-Task/Workflow·§6 넓은 Runtime·
  ADC.md·자동 판별·비용 실측·Contract 신설)을 새로 결정하지
  않았다(§Out of Scope) — 위반 없음. `diff` 검증 결과도 §6
  Concept Model 표·§14 Kernel Public Contract·`ADC.md`·Production
  Code 어디에도 변경이 없음을 확인했다(§6 Migration Strategy).

## Self Review

- ADC-0015가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(Scheduler, Multi-Task/Workflow, §6 넓은
  Runtime, ADC.md, 자동 판별, 비용 실측, Contract 신설, Production
  Code)은 손대지 않았다.
- ADC-0015의 Conditional Accept를 그대로 반영하고 새로운 Decision을
  추가했는가 — **아니오, 그대로 반영만 했다**(§2·§4) — Process
  1차/Subprocess 대안/Thread 배제/조건("동일 Target 동시 실행")/
  Conditional(재검토 가능)을 문구 그대로 옮겼을 뿐, 새 판단 기준을
  추가하지 않았다.
- Execution Host의 1차 구현 전략(Process)·대안(Subprocess)·배제
  (Thread)를 명시했는가 — **Pass**(§2 "구현 전략" 문단, §4
  "Execution Host 구현 허용 범위" 절).
- Conditional Accept이므로 재검토 가능함을 명시했는가 — **Pass**
  (§2 "구현 전략" 문단 마지막 문장, §4 절 마지막 항목, §Consequences
  마지막 항목).
- `BASELINE.md` §16.3에 구현 전략 범위를 반영했는가 — **Pass**
  (§2).
- `IMPLEMENTATION_RULES.md`의 Runtime 구현 금지를 Execution Host
  범위에 한해 Scoped 해제했는가 — **Pass**(§4) — Scheduler/Multi-
  Task/Workflow 및 §6 넓은 Runtime 구현 금지는 그대로 유지했다.
- Scheduler/Multi-Task/Workflow 및 §6 Runtime 구현 허용을
  결정했는가 — **아니오** — 오히려 그 반대(금지 유지)를 명시적으로
  재확인했다(§4 교체 행, §Out of Scope).
- Contract/Public Interface를 새로 정의했는가 — **아니오**(§14
  무변경, §Architecture/Contract/Kernel 영향).
- Production Code를 변경했는가 — **아니오**.
- §6 "Runtime" 항목을 재명명·수정했는가 — **아니오**(§3) — `ADR-0004`
  §3의 판단을 그대로 유지했다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- 새 최상위 절 또는 §16 내부 재배치를 했는가 — **아니오**. 기존
  §16.3에 문단 삽입·교체만 했다(§2).
- RFC-0015 → ADC-0015 → 이 ADR chain과 diff를 검증했는가 —
  **Pass**(§Governance Chain 검증, §6 Migration Strategy 검증
  절차).
