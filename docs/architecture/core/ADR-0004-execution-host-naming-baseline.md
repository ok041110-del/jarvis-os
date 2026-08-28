# ADR-0004: Execution Host 명칭(ADC-0014)의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0004` (`docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md`와 다른 문서 — 네임스페이스로 구분) |
| 제목 | `ADC-0014`의 Accept 결정(단일 실행 단위 dispatch·격리 책임의 명칭 = Execution Host)을 Architecture Baseline·GLOSSARY에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0014-execution-responsibility-naming.md` — **Decision: A. Accept — 명칭: Execution Host**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0014-execution-responsibility-naming.md` §1(Boundary Question), §4(Decision Candidate) |
| 관련 ADC | `docs/architecture/core/ADC-0014-execution-responsibility-naming.md` |
| 선행 ADR | `docs/architecture/core/ADR-0001-governance-module-baseline.md`, `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`, `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`(같은 절차로 §16 Kernel Modules를 갱신한 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/architecture/core/ADC-0008-runtime-existence-boundary.md`(넓은 범위 Runtime 존폐, Not Accepted), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW, 이 ADR이 변경하지 않음) |

이 ADR은 `ADC-0014`가 이미 내린 Accept 결정(명칭 = Execution Host,
§6 "Runtime"과는 별개 Concept)을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. 그 Accept 결정을 실제
Baseline·GLOSSARY 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0014`가 Accept 범위에서 명시하지 않은 것은 **하나도 반영하지
않는다.**

| 항목 | 근거 |
|---|---|
| Process/Thread/Subprocess 구현 전략 | `ADC-0014` §Out of Scope — 별도 RFC 대상 |
| Scheduler/Engine Gateway 등 대체 구조 설계 | `ADC-0014` §Out of Scope |
| Multi-Task/Workflow orchestration | `ADC-0014` §Out of Scope |
| `BASELINE.md` §6 Concept Model의 "Runtime" 항목 재명명·삭제 | `ADC-0014` §Q2가 별개 Concept으로 명시적으로 판정 — 재명명이 아니므로 §6 "Runtime" 행은 손대지 않는다(§Decision 2) |
| `BASELINE.md` §6 Concept Model 표에 "Execution Host" 신규 행 추가 | `ADC-0014` §Next Step 3이 이 ADR에 위임한 판단 — 이 ADR은 **추가하지 않기로** 명시적으로 결정한다(§Decision 3, 이유는 아래) |
| `docs/decisions/adc/ADC.md`의 ADC-02(Jarvis OS 수준 Runtime 존폐) 항목 수정 | `ADC-0014` §Out of Scope, `ADR-0001`·`ADR-0002`·`ADR-0003` 선례와 동일 — 별도 트랙 |
| `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지" 조항 해제 | `ADC-0014` §Out of Scope — 명칭 결정만으로는 해제하지 않는다(§Decision 5) |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.3 절 제목과 본문에 "Execution Host" 명칭 반영. §6은 무변경. §17 Version을 v1.8로 갱신 |
| `docs/00_governance/GLOSSARY.md` | 새 절 "Kernel Modules — Execution Host (Reference)" 신설, §16.3을 참조. "Concept Model 용어" 절(§6 미러링)은 무변경 |

그 외 어떤 파일도 변경하지 않는다(§Out of Scope). `docs/decisions/adc/ADC.md`,
`hqs/development/IMPLEMENTATION_RULES.md`는 이번에도 건드리지 않는다.

### 2. `BASELINE.md` §16.3 갱신 내용

기존 §16.3 절 제목:

```markdown
### 16.3 단일 실행 단위 Dispatch·격리 (Accept, Scoped)
```

교체할 제목:

```markdown
### 16.3 Execution Host — 단일 실행 단위 Dispatch·격리 (Accept, Scoped)
```

"**이 Accept가 결정하지 않는 것**" 문단에서 "이 책임의 명칭(§6
Concept Model의 'Runtime' 항목과의 관계 포함)," 부분을 제거하고
(명칭은 더 이상 Open이 아니므로), 그 앞에 새 문단 "**명칭**"을
추가한다. 나머지 문단(구현 전략·Scheduler·Multi-Task 확장 부분,
"Production 구현과의 관계" 문단)은 문구만 "명칭"을 뺀 형태로
다듬을 뿐 의미는 그대로 유지한다.

교체 후 §16.3 전체 본문(제목 제외):

```markdown
**책임**: 이미 identity/lifecycle이 확정된 단일 Task를 받아 그
실행을 시작하고, Command 불변성을 해치지 않으면서, 동일 대상에 대한
동시 실행에서 상태가 오염되지 않도록 격리를 제공하는 책임.

**근거**: `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md`
§4가 연 좁은 Boundary Question("Command·Task로 환원되지 않는 단일
실행 단위의 dispatch·격리 책임이 필요한가")을,
`docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`가
5개 Prototype·Vertical Slice Evidence(서로 다른 실행 대상·전략에
걸친 반복 관찰, 부재 시 실제 정확성 결함 재현 포함)를 근거로
Accept(Scoped)했다.

**Kernel Module로서 다루는 것**: Command(불변)에도 Task(identity/
lifecycle)에도 속하지 않는, 단일 실행 단위의 dispatch·격리 그
자체(`ADC-0013` §Implementation Boundary "포함").

**명칭**: 이 책임의 공식 명칭은 **Execution Host**다
(`docs/architecture/core/ADC-0014-execution-responsibility-naming.md`).
Execution Host는 §6 Concept Model의 "Runtime" 항목을 재명명한 것이
아니라 그와 별개의, 더 좁은 범위의 Concept이다(`ADC-0014` §Q2) —
§6의 "Runtime" 항목(Service 분류, Workflow 참조·Multi-Task 배분을
포함하는 넓은 정의)은 이 명칭 반영으로 전혀 변경되지 않으며,
`docs/decisions/adc/ADC.md`의 ADC-02("Runtime 개념의 존폐")도 Open
상태 그대로 유지된다.

**이 Accept가 결정하지 않는 것**: 구현 전략(Process/Thread/
Subprocess), Scheduler/Engine Gateway 등 대체 구조와의 비교,
`BASELINE.md` §6의 원래 넓은 정의(Workflow 참조, Multi-Task를
Agent에게 배분)로의 확장 여부는 모두 별도 절차(RFC → ADC → ADR)로
남는다(`ADC-0013` §Implementation Boundary "제외"). `docs/decisions/adc/ADC.md`
ADC-02가 다루는 "유지 대 대체" 구도와 이름 충돌 문제
(`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`)는
이 Accept로 해소되지 않는다.

**Production 구현과의 관계**: 이 Accept(및 명칭 확정)는 구현을
승인하지 않는다. `hqs/development/IMPLEMENTATION_RULES.md`의
"Runtime 구현 금지"는 구현 전략(Process/Thread/Subprocess)이
확정되지 않은 동안 그대로 유효하다 — 명칭이 Execution Host로
정해진 것과 무관하다(`ADC-0014` §Out of Scope).
```

### 3. `BASELINE.md` §6 Concept Model 표 갱신 여부

**추가하지 않는다.** `ADC-0014` §Next Step 3은 "§6 Concept Model
표에 Execution Host를 추가할지는 그 ADR이 명시적으로 판단한다(추가
하지 않기로 결정하는 것도 유효한 결론이다)"라고 이 판단을 이
ADR에 위임했다. 이 ADR은 **추가하지 않기로** 결정한다.

**이유**:
- §6 Concept Model은 Jarvis OS 전체 수준의 넓은 어휘 기준선이다
  (HQ, Agent, Workflow, Task, Runtime 등 10개 분류). Execution
  Host는 그보다 훨씬 좁은, Kernel Module(§16) 하나의 내부 책임이다
  — §16.1(Governance)·§16.2(Execution Layer)도 Accept된 Kernel
  Module이지만 §6 표에 별도 행으로 추가되지 않았다(선례 확인:
  §6에는 "Governance"나 "Execution Layer"라는 행이 없다). Execution
  Host만 예외적으로 §6에 추가하면 이 선례와 어긋난다.
- §6에 추가하면 "Runtime"(넓은 정의)과 "Execution Host"(좁은
  정의)가 같은 표에 나란히 등재되어, 두 Concept의 관계(별개인가
  포함 관계인가)를 §6 스스로 설명해야 하는 부담이 생긴다 — `ADC-0014`
  §Q2가 판정한 "별개, 더 좁은 범위"라는 관계는 §16.3 본문에 이미
  명시했으므로, §6에서 또 설명할 필요가 없다.
- §6은 이 저장소에서 여러 ADR(`ADR-0001`~`ADR-0003`)이 일관되게
  "건드리지 않는다"고 판단해 온 절이다 — 이 판단을 계속 유지한다.

### 4. `docs/00_governance/GLOSSARY.md` 갱신 내용

기존 "Kernel Reference Architecture (Reference)" 절과 "핵심 원칙
(Reference)" 절 사이에 새 절을 삽입한다("Concept Model 용어" 절은
§6을 미러링하므로 무변경).

```markdown
## Kernel Modules — Execution Host (Reference)

상세 정의는 `docs/architecture/baseline/BASELINE.md` §16.3 참조.

| 용어 | 정의 |
|---|---|
| Execution Host | 단일 실행 단위(Task)의 dispatch·격리를 담당하는 책임. Command(불변)·Task(identity/lifecycle) 어느 쪽에도 속하지 않는다. §6 Concept Model의 "Runtime"과는 별개의, 더 좁은 범위의 Concept이다(`docs/architecture/core/ADC-0014-execution-responsibility-naming.md` §Q2) — Runtime 항목을 재명명한 것이 아니다 |

> Execution Host는 §6 Concept Model 표에 등재되지 않는다 — Kernel
> Module(§16) 수준의 좁은 책임이며, Jarvis OS 수준 넓은 Concept
> Model에 반드시 속해야 하는 것은 아니다(`docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`
> §Decision 3). 구현 전략(Process/Thread/Subprocess)은 미확정이며,
> `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"는
> 그대로 유효하다.
```

### 5. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADC-0014` §Out of Scope가 이미 "명칭 결정만
으로는 해제하지 않는다"고 명시했다. 구현 전략(Process/Thread/
Subprocess)이 별도로 확정되기 전까지 "Runtime 구현 금지" 조항의
실질 효과는 그대로 유지되어야 한다. 그 조항의 이유 문구("Runtime
개념 자체가 Open Decision(ADC-02)이다")는 이제 "명칭은 Execution
Host로 정해졌으나 구현 전략은 미정"이라는 더 정확한 상태와 완전히
일치하지는 않지만, `ADR-0003` §5가 이미 판단한 대로 — 구현 전략이
확정되는 시점에 함께 정리하는 것이 이중 수정을 피하는 길이다. 이
ADR도 같은 타이밍 판단을 유지한다.

### 6. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.7 | **v1.8** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0014 → ADC-0014 → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0003`의 선례와 동일하다.

**Minor 증가(v1.8)를 택한 이유**: 새 절을 신설하지 않고, 기존
§16.3의 제목·본문 일부를 명칭 반영을 위해 교체했다(신설 절 없음,
§6 무변경). 선행 `ADR-0002`(내용 채움, v1.6)·`ADR-0003`(신설,
v1.7)과 같은 granularity로 Minor 단위로 기록한다.

### 7. Migration Strategy

1. `BASELINE.md` — §16.3 제목·본문 교체(§2), §6 무변경 확인(§3),
   변경 이력 한 줄 추가, v1.8 갱신.
2. `docs/00_governance/GLOSSARY.md` — 새 절 삽입(§4), 기존
   "Concept Model 용어" 절 무변경 확인.
3. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(신설 최상위 절 없음, §16 내부도 재배치 없음).
   - §6 Concept Model 표·각주, §14(Kernel Public Contract)가 문자
     그대로 변경되지 않았는지 확인.
   - `GLOSSARY.md`의 "Concept Model 용어" 절(Runtime 행 포함)이
     문자 그대로 변경되지 않았는지 확인.
   - `git status`로 `development-hq/`·`core/`(소스), `docs/decisions/adc/ADC.md`,
     `hqs/development/IMPLEMENTATION_RULES.md` 이하에 변경이 없는지
     확인.
4. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.7 → v1.8이 되고,
  §16.3의 책임이 이제 "Execution Host"라는 공식 명칭을 갖는다.
- `docs/00_governance/GLOSSARY.md`에 Execution Host 항목이 추가되어,
  향후 문서 작성 시 이 책임을 가리키는 표준 어휘가 생긴다.
- §6 Concept Model의 "Runtime" 항목, `docs/decisions/adc/ADC.md`의
  ADC-02(Open·NOW)는 이 ADR로 전혀 변경되지 않는다 — 두 Concept은
  계속 별개로 병존한다.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"는
  실질 효과 그대로 유지된다 — 명칭이 정해졌다고 구현이 승인된 것으로
  오독되어서는 안 된다.
- `ADC-0008`(넓은 범위, Not Accepted)·`ADC-0012`(Dispatch Component,
  DEFER)는 이 ADR로 뒤집히거나 재개되지 않는다.
- Process/Thread/Subprocess, Scheduler/Engine Gateway, Multi-Task/
  Workflow는 전부 이 ADR 이후에도 Open으로 남는다 — 각각 별도
  RFC로 다뤄야 한다.
- 이 ADR은 **승인되었으며**, §Decision에 정의된 실제 파일 변경이 이
  승인에 따라 실행된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(명칭 반영뿐)** — §16.3이 가리키는
  책임의 범위는 전혀 바뀌지 않는다. 이름만 확정됐다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경.
- **Kernel Impact**: **없음(추가적)** — `ADR-0003`이 이미 등재한
  책임에 이름을 붙였을 뿐, 새 책임이나 새 Component를 추가하지
  않았다.

## Governance Chain 검증

`RFC-0014`(Proposed, 명칭 후보 비교·권고만) → `ADC-0014`(Accept —
Execution Host, §6과 별개 Concept으로 판정) → 이 ADR(Accepted —
Baseline·GLOSSARY에 반영, 새로운 결정 추가 없음).

- RFC-0014는 권고만 하고 결정하지 않았다(§4 "확정 아님") — 위반
  없음.
- ADC-0014는 RFC-0014가 위임한 두 질문(명칭 Accept 여부, §6과의
  관계)에만 답했다(§Q1, §Q2) — RFC-0014의 Out of Scope(구현
  전략·Scheduler·Multi-Task)를 건드리지 않았다 — 위반 없음.
- 이 ADR은 ADC-0014의 Decision을 그대로 옮겼을 뿐, ADC-0014가
  판단하지 않은 것(구현 전략·Scheduler·Multi-Task·ADC.md·
  IMPLEMENTATION_RULES.md 본문)을 새로 결정하지 않았다(§Out of
  Scope) — 위반 없음. §6 표 추가 여부(ADC-0014가 이 ADR에
  위임한 판단)만 이 ADR이 새로 결정했고, 그 근거를 §Decision 3에
  기록했다 — 이는 위임받은 범위 안의 결정이므로 위반이 아니다.

## Self Review

- ADC-0014가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(구현 전략, Scheduler, Multi-Task, ADC.md,
  IMPLEMENTATION_RULES.md, 다른 Module)은 손대지 않았다. §6 표
  추가 여부만 ADC-0014가 이 ADR에 명시적으로 위임한 판단이었다.
- §6 "Runtime" 항목을 재명명·수정했는가 — **아니오**(§3) — `ADC-0014`
  §Q2의 "별개 Concept" 판정을 그대로 반영해 §6을 건드리지 않았다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**(§1
  표, §5 대상 아님).
- `hqs/development/IMPLEMENTATION_RULES.md`를 변경했는가 —
  **아니오**(§5).
- 새 최상위 절 또는 §16 내부 재배치를 했는가 — **아니오**. 기존
  §16.3의 제목·본문만 교체했다(§2).
- Production Code를 변경했는가 — **아니오**.
- 구현 전략(Process/Thread/Subprocess)을 결정했는가 — **아니오**.
- Scheduler/Multi-Task를 다뤘는가 — **아니오**.
- Contract를 변경했는가 — **아니오**(§14 무변경).
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  `ADC-0014`가 이미 인지한 것 이상의 새 결정 지점은 나타나지
  않았다.
