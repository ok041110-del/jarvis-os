# ADC-0009: Model 축과 Component 축의 대응 관계 — Not Accepted (RFC-0009 후속)

## 목적

`docs/architecture/core/RFC-0009-model-component-correspondence-boundary.md`
가 제기한 Boundary Question — "Model 축 3개(Execution/Communication/
Memory)와 Component 축 6개(Scheduler/Engine Gateway/Registry/
Communication/Memory/Policy)는 어떻게 대응하는가?" — 에 대해, 이
ADC는 먼저 **그 질문 자체를 지금 결정할 수 있는가**부터 판단한다
(Q0). 결정 가능한 범위가 있다면 그 범위만 판단하고, 아니면 후보를
억지로 만들지 않고 Not Accepted와 부족한 Evidence를 기록한다.

근거는 RFC-0009와 그것이 인용한 Evidence(`docs/03_adc/ADC.md`
ADC-01, `docs/01_architecture/BASELINE.md` §10,
`docs/02_rfc/RFC-0001-kernel-boundary.md`,
`docs/core/execution-layer/ADC-0004-execution-result-consumer.md`,
`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`,
`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`)로만
한정한다. 새로운 Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- ADC-02(Runtime 존폐) 자체 — `RFC-0008`·`ADC-0008`의 Not Accepted
  결론을 기존 결정으로만 인용하고 재조사하지 않는다.
- "Model 축"이라는 분류 자체를 재정의하는 것.
- Kernel Component Architecture의 실제 설계.
- "Execution"(Model 축)과 Kernel Module "Execution Layer"의
  동일성 — RFC-0009 §Out of Scope가 이미 판단 범위 밖에 뒀고, 이
  ADC도 새 판단을 추가하지 않는다.
- Execution Result Consumer의 재판단.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0009의 Boundary Question을
현재 확보된 Evidence로 지금(전부 또는 일부) 결정할 수 있는가?**

---

## Q0. 현재 확보된 Evidence로 전체 대응 관계를 결정할 수 있는가?

### Evidence

RFC-0009 §2 Evidence Summary를 그대로 인용한다.

| 축 | 상태 |
|---|---|
| Component 축 6개 | `BASELINE.md` §10 Out of Scope에 원문 실재, 5개 이상 문서가 반복 인용 — **실재** |
| Model 축 3개 | `docs/03_adc/ADC.md` ADC-01의 한 줄 진술이 유일한 출처. 전수 검색으로도 정의·근거 부연 문서 없음 — **원문 부재** |

### Q0 결론(Evidence 기반)

대응 관계를 판단하려면 최소한 **두 축 각각이 무엇을 분류 기준으로
삼는지**가 있어야 한다. Component 축은 `BASELINE.md` §10이 "Component
Design"(구현 방법 후보)이라는 분류 기준을 명시하지만, Model 축은
그 분류 기준 자체가 저장소 어디에도 정의돼 있지 않다 — "Execution/
Communication/Memory"가 왜 3개인지, 무엇을 축으로 삼아 나눈 것인지
설명하는 문서가 없다. **분류 기준을 모르는 축과 아는 축 사이의
대응 관계는 지금 결정할 수 없다.**

---

## Q1. 이름이 겹치는 두 항목("Communication", "Memory")만이라도 대응으로 확정할 수 있는가?

### Evidence

- RFC-0009 §4가 이미 관찰했다: *"'Communication'과 'Memory'는 두 축
  모두에 동일한 이름으로 등장한다... 대응이 1:1일 가능성을 시사하나,
  확정 근거는 아니다."*
- 같은 절: *"이름이 같다는 사실과 개념이 같다는 것은 다르다."*
- `BASELINE.md` §10에서 Component 축의 "Memory"는 "Component
  Design"(구현 방법) 후보로 정의된다. Model 축의 "Memory"가 같은
  층위(구현 방법)의 개념인지, 아니면 다른 층위(예: 책임, 데이터
  흐름)의 개념인지는 Model 축 자체의 정의가 없어 확인할 방법이
  없다.

### Q1 결론(Evidence 기반)

이름이 겹친다는 관찰은 사실이지만, 그 관찰만으로 두 항목이 같은
개념을 가리킨다고 결정하면, 정의되지 않은 축(Model 축)에 정의된
축(Component 축)의 의미를 무단으로 이식하는 것과 같다 — 이는 "임의의
대응 관계 추가"에 해당한다. **부분 대응도 확정할 수 없다.**

---

## Q2. Blocking Evidence(ADC-0004 Q3)가 대응 관계 판단을 대신 정당화하는가?

### Evidence

- `ADC-0004-execution-result-consumer.md` Q3: Execution Result
  Consumer Candidate C가 "ADC-01·ADC-02가 여전히 Open"에 막혀 있다고
  확인했다 — 이는 ADC-01이 **다른 판단을 막고 있다는 사실**이지,
  ADC-01 **자체의 답을 알려주는 사실이 아니다.**

### Q2 결론(Evidence 기반)

무언가를 막고 있다는 사실(Blocking)은 이 RFC를 여는 근거(ADC 채택
기준 1번, RFC-0009 §0)는 될 수 있어도, 그 내용을 무엇으로 채울지의
근거는 아니다. `ADC-0008`이 ADC-02에서 같은 구분을 이미 썼다(Q2:
"한쪽 주장의 근거 부재가 반대쪽 주장의 참을 증명하지 않는다"). 이
ADC도 동일한 원칙을 적용한다 — **Blocking 사실은 판단을 대신하지
않는다.**

---

## Decision

**Not Accepted (based on current evidence)**

Model 축과 Component 축의 대응 관계를 전부든 일부든 확정하지 않는다.
억지로 결론을 내리지 않는다.

### Reason

Model 축 3개(Execution/Communication/Memory)의 분류 기준 자체가
저장소 어디에도 정의돼 있지 않아(Q0), Component 축과의 대응을 판단할
근거가 없다. 이름이 겹치는 항목(Communication, Memory)만 부분
확정하는 것도, 정의되지 않은 축에 정의된 축의 의미를 무단으로
이식하는 것이므로 배제한다(Q1). ADC-01이 다른 판단(Execution Result
Consumer)을 막고 있다는 사실은 이 RFC가 열린 이유일 뿐, ADC-01
자체의 답을 정당화하지 않는다(Q2).

## Decision Rationale

Q0·Q1·Q2는 각각 독립적인 이유로 전체·부분·간접 판단 전부를
배제했다 — 이는 `ADC-0008-runtime-existence-boundary.md`가 ADC-02에
적용한 것과 동일한 판단 방식이다: 확보된 Evidence가 어느 후보도
뒷받침하지 못하면, 후보를 억지로 만들지 않고 Not Accepted로 남긴다.

## 부족한 Evidence — 무엇이 있어야 재판단 가능한가

새로 만들지 않는다 — 지금 확인된 공백만 기록한다.

1. **"Model 축"의 원래 정의 또는 그에 준하는 재구성 가능한 기록.**
   "Execution/Communication/Memory"가 무엇을 분류 기준으로 삼아
   선택된 3개인지(예: 책임의 종류인지, 데이터 흐름인지, 다른
   무엇인지)가 없이는 Component 축과의 대응을 판단할 방법이 없다.
   이는 `ADC-0008`이 ADC-02에서 확인한 "Core Component 검토 원문
   부재"와 같은 종류의 공백이다.
2. **"Execution"(Model 축)과 Kernel Module "Execution Layer"
   (`ADC-0001-core-baseline.md` Module 4, Accept)의 관계를 확인할
   근거.** 이름이 같다는 사실 외에 이 둘이 같은 개념인지 확인할
   문서가 없다(RFC-0009 §Out of Scope가 이미 이 판단을 보류했다).
3. 위 둘 중 하나가 채워지기 전까지, 이 질문은 "결정을 미루는 것"이
   아니라 "결정할 재료가 없는 것"이다 — `ADC-0008`이 ADC-02에서
   확인한 것과 같은 Freeze 원칙의 적용이다.

## Risks

- 이 Decision은 ADC-01을 처음으로 Boundary Question 형태로
  대조했으나, 여전히 Open으로 남긴다. `docs/03_adc/ADC.md`의 ADC-01
  항목 상태(Open, 우선순위 NEXT)는 이 ADC로 변경되지 않는다.
- `ADC-0004-execution-result-consumer.md`가 남긴 Blocking Evidence는
  이 Decision 이후에도 해소되지 않는다 — Execution Result Consumer는
  여전히 Not Accepted 상태로 남으며, 이는 새로운 문제가 아니라
  §부족한 Evidence가 채워지기 전까지 이미 예상된 상태의 지속이다.
- ADC-01과 ADC-02가 같은 Execution Result Consumer 판단을 공동으로
  막고 있었는데(`ADC-0004` Q3), 이제 둘 다 Not Accepted로 종결됐다
  — Execution Result Consumer의 재검토 조건은 둘 중 하나가 아니라
  **둘 다** 해소되어야 할 가능성이 있다. 이 ADC는 그 관계를
  판단하지 않는다 — 사실만 기록한다.

**재검토 조건**: §부족한 Evidence 1번("Model 축" 원문 확보) 또는
2번("Execution" 동일성 확인 근거)이 실제로 충족되면, 이 Decision은
기존 Governance 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다 — 이
문서를 직접 고쳐 뒤집는 것이 아니라, 새 RFC가 새 Evidence를 근거로
열리는 절차를 따른다.

## Next Step

**No ADR Required** — "Not Accepted (based on current evidence)"는
대응 관계를 확정하지 않으므로 Baseline 변경을 전제하지 않는다.

`docs/03_adc/ADC.md`의 ADC-01 항목은 갱신하지 않는다 — Open·NEXT
상태 그대로 유지된다. 이 판단이 그 등재 상태를 바꿀 근거를 제공하지
않는다(§부족한 Evidence).

`ADC-0004-execution-result-consumer.md`도 갱신하지 않는다 — 그 Not
Accepted 상태와 재검토 조건은 그대로 유효하다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서(`BASELINE.md`, `docs/03_adc/ADC.md`)를 변경했는가 —
  **아니오**. 이 ADC는 기존 Baseline과 ADC.md를 인용만 했다.
- ADR이 필요한가 — **아니오**. Not Accepted는 Boundary를 이동시키지
  않으므로 Baseline Update를 전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0009와 그것이 인용한
  `ADC.md` ADC-01, `BASELINE.md` §10, `RFC-0001-kernel-boundary.md`,
  `ADC-0004`(execution-layer), `RFC-0008`·`ADC-0008`만 인용했다. 새
  실험은 하지 않았다.
- ADC-02를 재조사했는가 — **아니오**. `RFC-0008`·`ADC-0008`의 Not
  Accepted 결론을 기존 결정으로만 인용했다(§목적, Q2).
- Model 축과 Component 축의 대응 관계를 임의로 결정했는가 —
  **아니오**. Q1에서 이름이 겹치는 항목조차 확정하지 않았다.
- 억지로 결론을 내렸는가 — **아니오**. Not Accepted로 남겼다.
- `docs/03_adc/ADC.md`를 수정했는가 — **아니오**(§Next Step).
- `ADC-0004-execution-result-consumer.md`를 수정했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q0~Q2에서 다룬
  공백은 RFC-0009가 이미 인지한 것이며, 이 ADC가 새로 발견한 문제가
  아니다.
