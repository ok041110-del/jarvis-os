# ADR-0003: 단일 실행 단위 Dispatch·격리 책임(Scoped)의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0003` (`docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md`와 다른 문서 — 네임스페이스로 구분) |
| 제목 | `ADC-0013`의 Scoped Accept 결정(단일 실행 단위 dispatch·격리 책임의 존재)을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` — **Decision: A. Accept (Scoped)**, Next Step: ADR Required |
| 관련 RFC | `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md` §4(Boundary Question) |
| 관련 ADC | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` |
| 선행 ADR | `docs/architecture/core/ADR-0001-governance-module-baseline.md`,
`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`(같은 절차로
§16 Kernel Modules에 절을 신설·반영한 선례) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/architecture/core/ADC-0008-runtime-existence-boundary.md`(넓은 범위, Not Accepted — 그대로 유지) |

이 ADR은 `ADC-0013`이 이미 내린 Scoped Accept 결정을 다시 논의하지
않는다. 새로운 철학이나 Architecture를 제안하지 않는다. 그 Accept
결정을 실제 Baseline 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0013`이 Accept 범위에서 명시하지 않은 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| Runtime 명칭 확정(그대로 쓸지, 다른 이름으로 바꿀지) | `ADC-0013` §Implementation Boundary "제외" — RFC-0013 §4가 이미 범위 밖으로 명시 |
| Process/Thread/Subprocess 구현 전략 | `ADC-0013` §Implementation Boundary "제외" — 별도 판단 대상 |
| Scheduler/Engine Gateway 등 대체 구조 설계 | `ADC-0013` §Q2, §Implementation Boundary — 비교 실험이 수행된 적 없음 |
| Multi-Task/Workflow 수준 분배(`BASELINE.md` §6 원래 정의) | `ADC-0013` §Implementation Boundary "제외" — 검증된 적 없음 |
| `BASELINE.md` §6 Concept Model의 "Runtime" 표 항목 자체 수정 | 이름·귀속을 이 ADR이 결정하지 않으므로 표는 손대지 않는다(§Decision 2) |
| `docs/decisions/adc/ADC.md`(Jarvis OS 수준 ADC-01~12 registry) | `ADR-0001` §5, `ADR-0002` §3과 동일한 판단 — 이 문서는 `docs/architecture/core/` 트랙과 독립적으로 추적된다. 이 ADR이 갱신하지 않는다(§5) |
| `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지" 조항 삭제 | 명칭·구현 전략이 여전히 Open이므로 실제 구현 금지는 그대로 유지되어야 한다(§5) |
| Execution Layer 내부 구조, Governance/Workflow/Memory/Event Bus Module 상태 | `ADR-0001`·`ADR-0002`가 이미 반영·기록했다. 이 ADR이 재론하지 않는다 |
| Production Code(`core/`, `hqs/`, `dashboard/`) | 전혀 수정하지 않는다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16에 새 절(16.3)을 신설해 이 책임을 Accept(Scoped)로 기록한다. 기존 §16.3("미결 항목")은 §16.4로 밀린다. §17 Version을 v1.7로 갱신한다 |

그 외 어떤 파일도 변경하지 않는다(§Out of Scope). `docs/decisions/adc/ADC.md`,
`hqs/development/IMPLEMENTATION_RULES.md`는 이번에는 건드리지 않는다 —
이유는 §5에서 별도로 판단한다.

### 2. `BASELINE.md` §16 갱신 내용

`ADC-0013`과 `RFC-0013`이 이미 정리한 것만 옮긴다. 새 문장을 만들지
않는다. 기존 §16.1(Governance)·§16.2(Execution Layer)는 변경하지
않는다.

새로 삽입할 §16.3(기존 §16.3 "미결 항목" 앞에 삽입, 기존 절은
§16.4로 재배치):

```markdown
### 16.3 단일 실행 단위 Dispatch·격리 (Accept, Scoped)

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

**이 Accept가 결정하지 않는 것**: 이 책임의 명칭(§6 Concept Model의
"Runtime" 항목과의 관계 포함), 구현 전략(Process/Thread/Subprocess),
Scheduler/Engine Gateway 등 대체 구조와의 비교, `BASELINE.md` §6의
원래 넓은 정의(Workflow 참조, Multi-Task를 Agent에게 배분)로의 확장
여부는 모두 별도 절차(RFC → ADC → ADR)로 남는다(`ADC-0013`
§Implementation Boundary "제외"). `docs/decisions/adc/ADC.md`
ADC-02가 다루는 "유지 대 대체" 구도와 이름 충돌 문제
(`docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md`)는
이 Accept로 해소되지 않는다.

**Production 구현과의 관계**: 이 Accept는 구현을 승인하지 않는다.
`hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"는
명칭·구현 전략이 확정되지 않은 동안 그대로 유효하다.
```

기존 §16.3("미결 항목")은 내용 변경 없이 §16.4로 재배치한다(Workflow/
Memory/Event Bus Defer 상태 기록 — `ADC-0013`은 이 상태를 재판단하지
않는다).

### 3. `BASELINE.md` §6 Concept Model 각주 처리

**수정하지 않는다.** §6의 Runtime 각주("Runtime은 Concept으로서
Baseline에 유지되나, 그 세부 구조는 Open Decision이다(ADC-02)")는
"Runtime"이라는 **이름**과 그 **넓은 세부 구조**에 대한 진술이다.
이 ADR이 반영하는 것은 그보다 좁은, 이름이 아직 없는 책임의
존재이므로, §6의 이름·표를 이 ADR이 건드리면 "이 책임 = Runtime"이라고
암묵적으로 확정하는 효과를 낳는다 — `ADC-0013`이 명시적으로 배제한
것이다(§Out of Scope). §16.3의 "이 Accept가 결정하지 않는 것"이 이
관계 미정 상태를 명시하는 것으로 충분하다.

### 4. `docs/architecture/baseline/BASELINE.md` 절 번호 영향

- §16 내부만 재배치(16.3 신설 → 기존 16.3이 16.4로 이동)된다.
- §17(Version) 이후 절 번호는 영향받지 않는다 — §16 뒤에 §17 하나만
  있으므로 전체 절 번호 체계(§1~§17)는 그대로 유지된다.

### 5. `docs/decisions/adc/ADC.md`·`IMPLEMENTATION_RULES.md` 갱신 여부

**둘 다 이 ADR에서는 갱신하지 않는다.**

- **`docs/decisions/adc/ADC.md`**(ADC-02 항목, Open·NOW): `ADR-0001`
  §5, `ADR-0002` §3과 동일한 판단 — 이 문서는 Jarvis OS 수준
  ADC-01~12 전용 registry로, `docs/architecture/core/`의 RFC/ADC/ADR
  트랙과 별도로 추적된다. **그러나 이번 Accept로 그 registry의
  ADC-02 항목("충돌 내용": 유지 대 대체, "미결정 시 문제": 이름
  귀속 불명확) 자체는 더 이상 완전한 최신 상태가 아니다** — 존재
  질문의 좁은 부분집합은 이제 Accept됐다. 이 불일치는 새로운 문제가
  아니라 두 트랙(Jarvis OS 수준 ADC.md ↔ Kernel Architecture 수준
  `docs/architecture/core/`)이 애초에 별도로 관리되어 온 데서 오는
  것이며, 이 ADR의 권한 밖이다. **필요 여부**: ADC.md ADC-02 항목에
  "존재(좁은 범위)는 `ADC-0013`/`ADR-0003`으로 Accept됨, 명칭·범위는
  여전히 Open" 한 줄을 덧붙이는 정합성 갱신이 **필요하다** — 단
  별도 절차(ADC.md 자체의 관리 권한을 가진 작업)로 수행되어야 한다.
- **`hqs/development/IMPLEMENTATION_RULES.md`**("Runtime 구현 금지"):
  **지금 당장 갱신이 필요하지 않다.** 이 조항의 실질 효과(Development
  HQ MVP 범위에서 Runtime을 구현하지 않는다)는 이 ADR 이후에도 그대로
  유지되어야 한다 — 명칭도, 구현 전략도 아직 결정되지 않았으므로
  "무엇을 구현 금지하는지"조차 확정할 수 없는 상태다. 다만 그 조항이
  적은 **이유**("Runtime 개념 자체가 Open Decision(ADC-02)이다")는
  이제 부분적으로 부정확하다 — 존재 자체는 더 이상 완전히 Open이
  아니라 좁은 범위에서 Accept됐다. **필요 여부**: 금지 자체는 유지,
  이유 문구의 정밀화는 명칭·구현 전략이 함께 확정되는 시점(§Next Step
  1~2번)에 한 번에 반영하는 것이 더 안정적이다 — 지금 이유 문구만
  먼저 고치면, 그 직후 명칭이 정해질 때 또 고쳐야 하는 이중 수정이
  된다.

### 6. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.6 | **v1.7** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 RFC-0013 → ADC-0013 → 이 ADR 절차를
그대로 거쳤다. `ADR-0001`·`ADR-0002`의 선례와 동일하다.

**Minor 증가(v1.7)를 택한 이유**: §16에 새 절(16.3)을 신설하되, 그
책임의 범위를 의도적으로 좁게 한정했고(§Out of Scope), 다른 어떤
절의 기존 문언도 수정하지 않았다(§6 각주 불변, §3 판단). 선행
`ADR-0001`(신설, v1.5)·`ADR-0002`(내용 채움, v1.6)와 같은 granularity로
Minor 단위로 기록한다.

### 7. Migration Strategy

1. `BASELINE.md` — §16에 16.3 신설(§2), 기존 16.3을 16.4로 재배치,
   변경 이력 한 줄 추가, v1.7 갱신.
2. 검증:
   - `BASELINE.md`의 최상위 절 번호가 §1~§17로 그대로 유지되는지
     확인(§16 내부 subsection만 재배치, 신설 최상위 절 없음).
   - §6 Concept Model 표·각주가 문자 그대로 변경되지 않았는지 확인.
   - `git status`로 `development-hq/`·`core/`(소스), `docs/decisions/adc/ADC.md`,
     `hqs/development/IMPLEMENTATION_RULES.md` 이하에 변경이 없는지
     확인.
3. 커밋 — 이 ADR과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.6 → v1.7이 되고,
  "단일 실행 단위 dispatch·격리" 책임이 Kernel Module 후보 5개
  (Governance/Workflow/Memory/Execution Layer/Event Bus)와는 별도로,
  `ADC-02`(Runtime 존폐) 트랙에서 처음 Baseline에 좁은 범위로
  반영된다.
- `docs/decisions/adc/ADC.md`의 ADC-02 항목은 이 ADR로 직접
  갱신되지 않으나, 그 항목이 이제 부분적으로 최신 상태가 아님을
  이 ADR이 명시적으로 기록했다(§5) — 후속 정합성 갱신이 필요하다는
  사실 자체는 숨기지 않는다.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"는
  실질 효과 그대로 유지된다 — 이 ADR이 구현을 승인한 것으로
  오독되어서는 안 된다(§5).
- `ADC-0008`(넓은 범위, Not Accepted)은 이 ADR로 뒤집히지 않는다 —
  서로 다른 범위의 질문에 대한 것이다.
- Runtime의 명칭, 구현 전략(Process/Thread/Subprocess), Scheduler/
  Engine Gateway 비교, Multi-Task/Workflow 확장은 전부 이 ADR 이후에도
  Open으로 남는다 — 각각 별도 RFC로 다뤄야 한다.
- 이 ADR은 **승인되었으며**, §Decision에 정의된 실제 파일 변경이 이
  승인에 따라 실행된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(Scoped)** — `BASELINE.md` §16에
  새 Kernel Module 후보급 책임이 좁은 범위로 처음 등재된다. 그러나
  Component 설계(§10 Out of Scope)에는 영향을 주지 않는다 — "책임이
  존재한다"는 사실만 기록했을 뿐, 그 책임을 누가/어떻게 구현하는지는
  여전히 미정이다.
- **Contract Impact**: **없음** — 공개 Interface를 정의하지 않았다.
  §16.3은 책임의 존재만 서술하고, Kernel Public Contract(§14)에는
  아무 항목도 추가하지 않는다.
- **Kernel Impact**: **있음(제한적)** — Kernel Concept 목록에 이름
  없는 책임 하나가 추가됐으나, 이것이 Component·Interface로
  구체화되려면 별도 ADR(명칭·구현 전략 확정 이후)이 필요하다.
- **Runtime 구현 가능 범위**: **없음.** 이 ADR은 "Runtime"이라는
  이름의 어떤 구현도 승인하지 않는다. `hqs/development/IMPLEMENTATION_RULES.md`의
  금지가 실질적으로 유지되므로, Development HQ MVP를 포함한 어떤
  Production 범위에서도 이 책임의 구현에 착수할 수 없다 — 착수하려면
  최소한 (a) 명칭 확정 RFC, (b) 구현 전략(Process/Thread/Subprocess)
  확정 RFC/ADC, (c) 그에 따른 별도 ADR이 먼저 완료되어야 한다.

## Governance Chain 검증

`RFC-0013`(질문만 개설, 판단은 후속 절차로 위임 — 개설 당시 Open,
이후 `ADC-0013` → 이 ADR로 Resolved) → `ADC-0013`(Accept,
Scoped — 그 질문에 답함, 명칭·전략·범위는 명시적으로 제외) → 이
ADR(Accepted — Baseline에 반영, 새로운 결정 추가 없음). 세 문서가
각각 인용하는 근거가 상위 문서의 범위를 벗어나지 않는지 확인했다.

- RFC-0013은 답을 제시하지 않고 질문만 열었다(§4) — 위반 없음.
- ADC-0013은 RFC-0013이 연 질문에만 답했고, RFC-0013이 제외한
  항목(명칭·전략·Multi-Task)을 판단하지 않았다(§Implementation
  Boundary) — 위반 없음.
- 이 ADR은 ADC-0013의 Decision을 그대로 옮겼을 뿐, ADC-0013이
  판단하지 않은 것(명칭·전략·Multi-Task, §6 각주, ADC.md, IMPLEMENTATION_RULES.md
  본문)을 새로 결정하지 않았다(§Out of Scope, §Decision 3·5) — 위반
  없음.

## Self Review

- ADC-0013이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(명칭, 구현 전략, 대체 구조, Multi-Task 범위,
  §6 표, ADC.md, IMPLEMENTATION_RULES.md, 다른 Module)은 손대지
  않았다.
- 새 Component/Interface를 설계했는가 — **아니오**.
- `docs/decisions/adc/ADC.md`를 변경했는가 — **아니오**(§5) — 변경
  필요성만 명시했다.
- `hqs/development/IMPLEMENTATION_RULES.md`를 변경했는가 —
  **아니오**(§5) — 실질 금지가 유지됨을 명시했다.
- §6 Concept Model의 "Runtime" 표·각주를 수정했는가 — **아니오**(§3)
  — 이름 귀속을 암묵적으로 확정하지 않기 위해 의도적으로 보존했다.
- 새 최상위 절을 신설했는가 — **아니오**. §16 내부 subsection만
  재배치했다(§4).
- Production Code를 변경했는가 — **아니오**.
- Runtime 구현을 승인했는가 — **아니오**(§Runtime 구현 가능 범위:
  없음).
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  `ADC-0013`이 이미 인지한 것 이상의 새 결정 지점은 나타나지 않았다.
