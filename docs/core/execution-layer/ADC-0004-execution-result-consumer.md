# ADC-0004: Execution Result Consumer — 결정 가능성 판단 (RFC-0004 후속)

## 목적

`docs/core/execution-layer/RFC-0004-execution-result-consumer.md`가
제기한 Boundary Question — "Execution Result를 누가, 어떤 방식으로
소비하는가?" — 에 대해, 이 ADC는 먼저 **그 질문 자체를 지금 결정할
수 있는가**부터 판단한다. 결정 가능하면 RFC-0004가 인용한 3개 후보
(Kernel Memory / Kernel Event Bus / Execution Layer 자신의 내부
처리) 중 하나를 선택한다. 결정 불가능하면 후보를 억지로 고르지
않고, 어떤 기존 Architecture 결정이 선행되어야 하는지만 기록한다.

근거는 RFC-0004와 그것이 인용한 Evidence(`ARTIFACT-STANDARD-v1.md`,
Kernel `RFC-0001-jarvis-os-core-baseline.md`, Kernel
`ADC-0001-core-baseline.md`, `RFC-0005-development-hq-execution-boundary.md`,
`GOVERNANCE-REVIEW-0002-impl-stop.md`)로만 한정한다. 새로운 Evidence를
만들지 않는다.

### 이 ADC가 답하지 않는 것

이 ADC는 다음을 판단하지 않는다.

- Kernel Module(Memory/Event Bus)을 Accept/Reject할지 — 이는 Kernel
  수준 ADC(`docs/architecture/core/ADC-0001-core-baseline.md`)의
  권한이며 이 ADC의 권한이 아니다(RFC-0004 §Out of Scope와 동일한
  제약).
- `docs/03_adc/ADC.md`의 ADC-01(Model↔Component 대응 관계)·ADC-02
  (Runtime 개념의 존폐) 자체를 판단할지 — 동일하게 Kernel 수준
  권한이다.
- Consumer의 실제 구현, 인터페이스, 필드.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0004의 Boundary Question을
현재 확보된 Evidence로 지금 결정할 수 있는가, 있다면 어느 후보인가?**

---

## Q0. 현재 확보된 Evidence로 이 질문을 결정할 수 있는가?

### Evidence

RFC-0004 §2 Evidence Summary가 이미 정리한 3개 후보의 현재 상태를
그대로 인용한다.

| 후보 | RFC-0004가 인용한 현재 상태 |
|---|---|
| Kernel Memory | Kernel `ADC-0001-core-baseline.md` Module 3 — **Decision: Defer.** "승격을 정당화할 두 번째 경로나 영속화 필요 사례가 관찰된 적이 없다." |
| Kernel Event Bus | Kernel `ADC-0001-core-baseline.md` Module 5 — **Decision: Defer.** "Phase 1 전체를 통틀어 단 한 번도 실행된 적이 없다." |
| Execution Layer 자신의 내부 처리 | Kernel `ADC-0001-core-baseline.md` Module 4 — **Decision: Accept(ADR Required)**, 그러나 Risks: "내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model Routing)는 `docs/03_adc/ADC.md`의 ADC-01·ADC-02가 여전히 Open... 이 Accept를 'Execution Layer의 설계가 결정되었다'는 의미로 확장 해석하면 안 된다." |

### Q0 결론(Evidence 기반)

세 후보 모두, 그 후보를 채택하기 위한 **선행 조건**이 아직 충족되지
않았다.

- Memory·Event Bus를 선택하려면 그 Kernel Module 자체가 먼저
  Accept돼야 하는데, 둘 다 Defer 상태다.
- Execution Layer 내부 처리를 선택하려면 그 내부 구조가 먼저
  결정돼야 하는데, ADC-01·ADC-02가 Open 상태이며 이는 Kernel Module
  4 Decision 자체가 "설계 결정으로 확장 해석하면 안 된다"고 명시한
  바로 그 지점이다.

**현재 확보된 Evidence로는 이 질문을 결정할 수 없다.**

---

## Q1. Candidate A(Kernel Memory)는 그럼에도 채택 가능한가?

### Evidence

Q0과 동일 — Kernel Module 3이 Defer다. RFC-0004 §Out of Scope는 이미
"Kernel Module(Memory/Event Bus) 자체를 Accept/Reject하는 판단...
이 RFC의 권한이 아니다"라고 명시했고, 이 ADC도 같은 제약을 상속한다
(§목적).

### Q1 결론(Evidence 기반)

이 ADC가 Kernel Module의 Defer 상태를 스스로 뒤집을 권한이 없는 한,
Memory를 Consumer로 선택하는 것은 아직 Accept되지 않은 Kernel
Module의 존재를 전제하는 것과 같다. **Not Accepted.**

---

## Q2. Candidate B(Kernel Event Bus)는 그럼에도 채택 가능한가?

### Evidence

Q0과 동일 — Kernel Module 5가 Defer다. 근거는 "Phase 1 전체를 통틀어
단 한 번도 실행된 적이 없다"는, Memory보다도 약한(반복 관찰 0회)
Evidence다.

### Q2 결론(Evidence 기반)

Q1과 동일한 이유로 **Not Accepted.**

---

## Q3. Candidate C(Execution Layer 자신의 내부 처리)는 그럼에도 채택 가능한가?

### Evidence

Kernel Module 4는 세 후보 중 유일하게 **Accept**됐다 — Execution
Layer가 Kernel Module로서 존재해야 한다는 것 자체는 결정되어 있다.
그러나 같은 Decision의 Risks 절이 그 Accept의 범위를 스스로
한정한다: "내부 구조... `docs/03_adc/ADC.md`의 ADC-01·ADC-02가
여전히 Open." "Execution Layer가 소비한다"고 답하려면 그 소비가
Execution Layer 내부의 **무엇**(Prompt 구성 계층? Model 선택 계층?
재시도 정책?)에 해당하는지 특정해야 하는데, 그 특정에 필요한 내부
구조 자체가 아직 없다.

### Q3 결론(Evidence 기반)

Kernel Module로서의 Accept는 "Execution Layer가 존재한다"만
확정했을 뿐 "Execution Layer 안에서 Execution Result를 누가/어떻게
처리하는가"에는 답하지 않는다. 세 후보 중 유일하게 부분적으로
근접했으나(Module 자체는 Accept), 여전히 **Not Accepted** — 내부
구조 미결이 그대로 Consumer 미결로 이어진다.

---

## Decision

**Not Accepted (based on current evidence)**

3개 후보(Kernel Memory / Kernel Event Bus / Execution Layer 내부
처리) 중 어느 것도 선택하지 않는다. 억지로 하나를 고르지 않는다.

### Reason

세 후보 모두 이 ADC의 권한 밖에 있는 Kernel 수준 선행 결정(Kernel
Module Accept 또는 Kernel Open Decision 해소)에 의존하며, 그 선행
결정은 지금 확보된 Evidence 안에서 아직 내려지지 않았다.

## Decision Rationale

Q0은 세 후보 모두 채택을 위한 선행 조건이 충족되지 않았음을
확인했다. Q1·Q2는 Memory·Event Bus가 Kernel Module 자체의 Defer로
막혀 있음을, Q3은 Execution Layer 내부 처리가 Module Accept에도
불구하고 내부 구조 Open으로 여전히 막혀 있음을 확인했다. 세 판단
모두 RFC-0004가 이미 정리한 Evidence를 그대로 적용했을 뿐, 새로운
사실을 추가하지 않았다.

## 선행되어야 하는 기존 Architecture 결정

새로 만들지 않는다 — 이미 저장소에 기록된 Open Decision만 나열한다.

1. Kernel `docs/architecture/core/ADC-0001-core-baseline.md` Module 3
   (Memory)의 **Defer 재평가** — Kernel Governance 권한. 재평가
   조건은 그 Decision 자체가 명시하지 않았으나, Risks 절이 "Memory
   부재로 인한 실패(실행 실패 후 재시도, Context 유실)가 실제로
   발생"하는 관찰을 전제로 언급한다.
2. Kernel `ADC-0001-core-baseline.md` Module 5(Event Bus)의 **Defer
   재평가** — Kernel Governance 권한. 같은 문서가 명시한 재평가
   조건: "Fault/Event 전파가 실제로 필요한 상황... 이 실제로 발생하기
   전까지."
3. `docs/03_adc/ADC.md`의 **ADC-01**(Model↔Component 대응 관계,
   우선순위 NEXT)과 **ADC-02**(Runtime 개념의 존폐, 우선순위 NOW)의
   해소 — 이 둘이 풀려야 Execution Layer의 내부 구조가 생기고,
   Candidate C(Execution Layer 자신의 내부 처리)를 판단할 근거가
   마련된다.

이 셋 중 무엇이 먼저 해소되어야 하는지, 혹은 셋 다 동시에 필요한지는
이 ADC가 판단하지 않는다 — 그 우선순위는 Kernel 수준 Governance의
권한이다.

## Risks

- 이 Decision은 "지금은 결정할 수 없다"는 판단이며, "Consumer가
  영원히 필요 없다"는 뜻이 아니다. Execution Result의 필요성 자체는
  이미 RFC-0002~ADR-0002·MVP-0006으로 확정됐으므로(RFC-0004 §2 인용),
  Consumer 없이 Execution Result만 계속 만들어지는 상태가 무기한
  지속될 수 있다 — 이는 새로운 문제가 아니라 §선행 조건이 해소될
  때까지 이 저장소가 이미 감수해 온 것과 같은 종류의 유예다(Kernel
  Module 4 Risks 절이 이미 동일한 유예를 인정했다).
- 세 후보의 선행 조건이 전부 Kernel 수준이라는 사실 자체가, Execution
  Layer 수준에서는 이 질문에 답할 방법이 근본적으로 없다는 것을
  시사할 수 있다 — 그러나 이는 추정이며, 이 ADC는 이를 결론으로
  삼지 않는다(Evidence가 그렇게 말하지 않았다).

**재검토 조건**: §선행되어야 하는 기존 Architecture 결정 3건 중
하나라도 Kernel 수준 Governance 절차로 실제 해소되면, 이 Decision은
기존 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`: RFC → ADC
→ ADR → Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**No ADR Required** — "Not Accepted (based on current evidence)"는
Consumer를 확정하지 않으므로 Baseline 변경을 전제하지 않는다.

RFC-0004의 원래 Boundary Question은 이 ADC가 완전히 답하지 않았다.
이 ADC는 "지금 결정할 수 있는가"만 판단했고, 답은 "아니오"였다. 위에
나열한 3개 선행 조건 중 하나가 Kernel 수준에서 해소되기 전까지, 이
질문은 Execution Layer 수준에서 다시 열 근거가 없다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer가 추가되었는가 — **아니오**.
- 새로운 Component가 추가되었는가 — **아니오**.
- 새로운 Concept이 추가되었는가 — **아니오**.
- Baseline 문서(`ARTIFACT-STANDARD-v1.md`, Kernel Baseline)를
  변경했는가 — **아니오**. 이 ADC는 기존 Baseline을 그대로 인용만
  했다.
- ADR이 필요한가 — **아니오**. "Not Accepted"는 Boundary를 이동시키지
  않으므로 Baseline Update를 전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0004와 그것이 인용한 Kernel
  RFC-0001·ADC-0001, RFC-0005, GOVERNANCE-REVIEW-0002에 실제로
  기록된 내용만 인용했다. 새 실험은 하지 않았다.
- 새 후보를 만들었는가 — **아니오**. RFC-0004의 3개 후보만
  비교했다.
- "결정 가능한가"를 먼저 판단했는가 — **Pass**. Q0에서 먼저 판단한
  뒤, Q1~Q3에서 개별 후보를 대조했다.
- 억지로 후보를 선택했는가 — **아니오**. Not Accepted로 남겼다.
- 선행 Architecture 결정을 새로 만들었는가 — **아니오**. 이미
  `docs/03_adc/ADC.md`와 Kernel `ADC-0001-core-baseline.md`에 기록된
  Open Decision 3건만 나열했다.
- Kernel Module Accept/Reject을 판단했는가 — **아니오**(§목적).
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q0~Q3에서 다룬
  선행 조건은 RFC-0004가 이미 인지한 것이며, 이 ADC가 새로 발견한
  문제가 아니다.
