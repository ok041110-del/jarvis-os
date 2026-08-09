# RFC-0008: Runtime 개념의 존폐 — Boundary (ADC-02 후속)

**Status**: Resolved — `ADC-0008-runtime-existence-boundary.md`로 종결됨(Not Accepted, based on current evidence; ADR 불필요). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (Execution Result Consumer Governance 후속)
**대상**: `docs/03_adc/ADC.md` ADC-02("Runtime 개념의 존폐") — Kernel
Baseline v1.0부터 Open(우선순위 NOW)으로 남아 있던 항목
**Evidence**: `docs/01_architecture/BASELINE.md` §6,
`docs/03_adc/ADC.md` ADC-02 항목, `docs/00_governance/GLOSSARY.md`,
`docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md`,
`docs/02_rfc/RFC-0004-task-dispatcher-runtime-boundary.md`,
`docs/core/execution-layer/ADC-0004-execution-result-consumer.md`

> 본 RFC는 Runtime 개념의 존폐를 결정하지 않는다. 본 RFC는 Runtime을
> 설계하거나 대체 구조(Scheduler/Engine Gateway)를 설계하지 않는다.
> 새 실험을 하지 않는다. 이 RFC는 ADC-02가 지금까지 저장소 안에서
> 실제로 판단된 적이 있는지 확인하고, 판단에 필요한 양측 근거를
> 있는 그대로 정리하며, 그 근거가 지금 판단을 가능하게 하는지만
> 질문한다.

## 0. 이 RFC가 열린 이유

ADC-02(Runtime 개념의 존폐)는 Architecture Baseline v1.0부터 Open
상태로 `docs/03_adc/ADC.md`에 등재되어 있었다. 저장소 안에서 이
항목을 인용한 문서는 최소 10건 이상이지만(`docs/architecture/core/`
전수 검색 결과), 그 전부가 "ADC-02는 Open 상태 그대로 둔다" /
"이번 작업과 무관하다"는 확인만 반복했을 뿐, ADC-02 자체를
Boundary Question으로 열어 양측 근거를 대조한 문서는 하나도 없었다.

그러던 중, `docs/core/execution-layer/ADC-0004-execution-result-consumer.md`
Q3(Candidate C: Execution Layer 자신의 내부 처리)가 **처음으로**
ADC-02 Open 상태가 실제로 다른 작업(Execution Result Consumer 판단)
을 막고 있다는 관찰 가능한 사실을 남겼다. 이는
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준
1번("지금 결정하지 않으면 상위 Architecture를 진행할 수 없다")이
처음으로 충족된 지점이다. 이 RFC는 그 관찰을 근거로, ADC-02를 정식
Boundary Question으로 여는 첫 시도다.

## 1. Problem Statement

Runtime이 Kernel Concept으로서 존속해야 하는지, 아니면 다른 구조
(Scheduler + Engine Gateway)로 대체되어야 하는지가 결정된 바 없다.
`docs/01_architecture/BASELINE.md` §6은 Runtime을 Concept으로
유지하면서도 스스로 "그 세부 구조는 Open Decision(ADC-02)"이라고
명시했다. 이 RFC는 그 미결 상태의 양측 근거를 정리한다.

## 2. Evidence Summary — 저장소 안에서 실제로 확인한 것만

### 2.1 Runtime 유지 근거 — 원문이 실재한다

`docs/01_architecture/BASELINE.md` §6 Concept Model:

> *"Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다."*

같은 절 표에서 Runtime은 `Service` 분류(Memory, Registry와 함께)로
등재되어 있고, 절 말미에 다음과 같이 스스로 미결 상태를 표시했다.

> *"Runtime은 Concept으로서 Baseline에 유지되나, 그 세부 구조는 Open
> Decision이다 (ADC-02). → `docs/03_adc/ADC.md` 참조."*

이 근거는 Frozen Baseline 문서에 원문 그대로 존재하며, 지금도
인용 가능하다.

### 2.2 Runtime 폐기 근거 — 원문이 부재한다

`docs/03_adc/ADC.md` ADC-02 항목의 유일한 실질 내용:

> *"Concept Model은 Runtime을 Service로 유지하나, **Core Component
> 검토**에서는 Runtime을 폐기하고 Scheduler + Engine Gateway로
> 대체할 것을 권고함."*

"Core Component 검토"는 다음 두 문서가 그 성격을 확인한다.

- `docs/00_governance/GLOSSARY.md`: *"'Core Principles'·'Core
  Philosophy'·'Core Component 검토'처럼 '핵심'이라는 일반적 의미로
  쓰인 'Core'는 Kernel과 무관하며 변경되지 않았다."*
- `docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md`:
  *"`docs/03_adc/ADC.md` ADC-02 | 'Core Component 검토' | 과거에
  실제로 수행된 **검토 단계의 고유 명칭**이다. 역사적 사건 이름이므로
  바꾸면 기록이 훼손된다."*

두 문서 모두 "Core Component 검토"가 **과거에 실제로 수행된 사건의
이름**이라는 것만 확인할 뿐, 그 검토의 원문·상세 근거는 인용하지
않는다. 저장소 전수 검색 결과("Core Component 검토" 문자열, `find`
로 관련 파일명 검색 포함) 그 검토 자체를 기록한 문서는 발견되지
않았다. **Runtime 폐기 쪽 근거는 결론(권고 문구) 하나만 남아 있고,
그 결론을 뒷받침하는 원문은 저장소 안에 없다.**

### 2.3 기존 시도된 권한 위임 — Development HQ는 이 질문에 답할 권한이 없다

`docs/02_rfc/RFC-0004-task-dispatcher-runtime-boundary.md`(Development
HQ 수준, Resolved)는 저장소에서 "Runtime"을 정면으로 다룬 유일한
RFC였다. 그러나 이 RFC는 명시적으로 권한을 넘겼다.

> §4: *"Development HQ ADC는 ADC-02를 해결할 권한이 없다(Jarvis OS
> Architecture Baseline은 Frozen이며, ADC-02는 Jarvis OS
> `docs/03_adc/ADC.md` 소관이다)."*
> Non-goals: *"이 RFC는 ADC-02(Jarvis OS 수준 Runtime 개념 존폐)를
> 해결하지 않는다."*

그 후속 `docs/governance/adc/ADC-0004.md`(Development HQ 수준)도
동일하게 "Jarvis OS 경계로 남겨둔 부분(ADC-02, Runtime 명칭)은
그대로 두었다"고 확인했다. **Development HQ 수준에서 이 질문에 답할
수 없다는 것은 이미 확정된 사실이며, 이 RFC는 그것을 재론하지
않는다** — 이 RFC 자체가 Kernel 수준에서 처음 열리는 이유다.

### 2.4 최초의 실제 Blocking Evidence

`docs/core/execution-layer/ADC-0004-execution-result-consumer.md`
Q3(Candidate C: Execution Layer 자신의 내부 처리):

> *"Kernel Module 4는... Execution Layer가 Kernel Module로서
> 존재해야 한다는 것 자체는 결정되어 있다. 그러나... '내부 구조...
> `docs/03_adc/ADC.md`의 ADC-01·ADC-02가 여전히 Open'... 'Execution
> Layer가 소비한다'고 답하려면 그 소비가 Execution Layer 내부의
> 무엇에 해당하는지 특정해야 하는데, 그 특정에 필요한 내부 구조
> 자체가 아직 없다."*
>
> Decision: *"Not Accepted (based on current evidence)... 세 후보
> 모두 이 ADC의 권한 밖에 있는 Kernel 수준 선행 결정(Kernel Module
> Accept 또는 Kernel Open Decision 해소)에 의존하며..."*

이는 저장소 안에서 ADC-02 Open 상태가 실제로 다른 판단을 막았다고
관찰 가능한 형태로 기록한 **첫 사례**다. 이전의 모든 교차검토
(`GOVERNANCE-REVIEW-0001`, Kernel `ADC-0002/0004/0005`,
`CLOSURE-0001`, `STABILITY-0001`)는 예외 없이 "ADC-02와 무관"이라고
확인했을 뿐이다.

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- Runtime 유지 근거(§2.1)는 원문이 실재하고 지금도 인용 가능하다.
- Runtime 폐기 근거(§2.2)는 결론 문구만 남아 있고, 그 결론을
  뒷받침하는 원문은 저장소 안에 없다.
- Development HQ 수준에서 이 질문을 해결하려는 시도(§2.3)가 있었고,
  그 시도는 스스로 권한이 없다고 확인하며 종결됐다.
- ADC-02가 실제로 다른 Governance 판단을 막은 사례는 이번이
  처음이다(§2.4) — 그 전까지는 전부 "무관" 확인이었다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Runtime은 Kernel Concept으로서 존속하는가, 아니면 다른 구조
(Scheduler + Engine Gateway)로 대체되는가?

| 입장 | 근거 문서 | 근거의 실재 여부 |
|---|---|---|
| 유지 | `BASELINE.md` §6 Concept Model | 원문 실재(§2.1) |
| 대체(Scheduler + Engine Gateway) | `ADC.md` ADC-02가 인용한 "Core Component 검토" | 결론만 남고 원문 부재(§2.2) |

이 RFC는 이 중 어느 것이 맞는지 판단하지 않는다. 이 질문에 대한
판단은 ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Runtime 존폐의 실제 판단.
- Scheduler/Engine Gateway 등 대체 구조의 설계.
- "Core Component 검토"의 원문을 재구성하거나 추정하는 것 — 부재
  사실만 기록한다.
- Execution Result Consumer의 재판단 — `ADC-0004-execution-result-consumer.md`
  는 그대로 유지되며, 이 RFC의 결과가 나오기 전까지 그 Not Accepted
  상태도 유지된다.
- ADC-01(Model 축과 Component 축의 대응 관계) — `ADC-0004-execution-result-consumer.md`
  Q3이 ADC-01·ADC-02를 함께 인용했으나, 이 RFC는 우선순위(ADC-02:
  NOW, ADC-01: NEXT)와 Blocking Evidence(§2.4)가 ADC-02에 한정된
  점을 근거로 ADC-02만 다룬다.
- Development HQ, Execution Layer, Kernel의 어떤 코드도 수정하지
  않는다.
- 새로운 실험.

## Non-goals

- 이 RFC는 Runtime 개념의 존폐를 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `BASELINE.md`, `ADC.md`,
  `GLOSSARY.md`, `ADR-0002`, `RFC-0004`(Dev HQ),
  `ADC-0004`(execution-layer)에 이미 기록된 내용만 인용했다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 Runtime이나 대체 구조를 설계·구현하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §2.1·§2.2의 비대칭(유지 근거는 원문 실재, 폐기 근거는 원문
   부재)을 근거로 지금 판단이 가능한지, 아니면 "Core Component
   검토"의 재구성 없이는 판단할 수 없는지.
2. 판단이 가능하다면 §4의 Boundary Question(유지/대체) 중 무엇을
   채택할지.
3. 판단이 불가능하다면, §2.4의 Blocking Evidence(Execution Result
   Consumer)를 근거로 이 ADC가 다시 Defer될 경우, 그 Defer가
   Execution Result Consumer 판단에 어떤 영향을 주는지(추가 판단
   없이 상태만 기록).

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `BASELINE.md` §6, `ADC.md`
  ADC-02, `GLOSSARY.md`, `ADR-0002`, `RFC-0004`(Dev HQ),
  `ADC-0004`(execution-layer)에 실제로 기록된 내용만 인용했다. 새
  실험은 수행하지 않았다.
- Runtime 존폐를 결정했는가 — **아니오**. §4는 질문 형태로만
  남겼고, 두 입장 중 어느 것도 판단하지 않았다.
- 새 Architecture(Scheduler/Engine Gateway 등)를 설계했는가 —
  **아니오**. §2.2는 기존 ADC.md 문구를 인용만 했다.
- "Core Component 검토"의 원문을 추정·재구성했는가 — **아니오**.
  부재 사실만 기록했다(§2.2).
- Development HQ 수준 RFC-0004의 권한 위임을 재론했는가 — **아니오**.
  기록만 인용했다(§2.3).
- ADC-0004(execution-layer)의 Not Accepted 결정을 뒤집었는가 —
  **아니오**. 그대로 유지된다고 명시했다(§Out of Scope).
- ADC, ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(Runtime 판단, 대체 구조 설계, 원문 재구성,
  Consumer 재판단, ADC-01, 코드 수정, 새 실험)을 다뤘는가 —
  **아니오**.
