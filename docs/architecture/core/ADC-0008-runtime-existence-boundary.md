# ADC-0008: Runtime 개념의 존폐 판단 (RFC-0008 후속)

## 목적

`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`가
제기한 Boundary Question — "Runtime을 Kernel Concept으로 유지할
것인가, Scheduler + Engine Gateway로 대체할 것인가?" — 에 대해
판단한다.

근거는 RFC-0008과 그것이 인용한 Evidence(`BASELINE.md` §6,
`docs/03_adc/ADC.md` ADC-02, `GLOSSARY.md`,
`ADR-0002-core-to-kernel-terminology-unification.md`,
`RFC-0004-task-dispatcher-runtime-boundary.md`(Dev HQ),
`ADC-0004-execution-result-consumer.md`(execution-layer))로만
한정한다. 새로운 Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Scheduler/Engine Gateway의 실제 설계.
- "Core Component 검토"의 원문을 추정·재구성하는 것 — 부재 사실을
  그대로 취급한다.
- Execution Result Consumer의 재판단 —
  `ADC-0004-execution-result-consumer.md`의 Not Accepted 상태는 이
  ADC의 결과와 무관하게 유지된다.
- ADC-01(Model 축과 Component 축의 대응 관계) — RFC-0008이 이미
  범위에서 제외했다.

---

## Q0. Candidate "유지"(Runtime을 Kernel Concept으로 유지)는 지금 확정할 수 있는가?

### Evidence

- `BASELINE.md` §6: *"Runtime은 Workflow를 참조하여 Task를 Agent에게
  배분한다."* 원문이 실재하며, Runtime을 `Service` 분류로 등재하고
  있다(RFC-0008 §2.1).
- 그러나 같은 절이 스스로 이 상태를 확정으로 표시하지 않는다: *"Runtime은
  Concept으로서 Baseline에 유지되나, 그 세부 구조는 Open Decision이다
  (ADC-02)."* — 즉 "유지"는 **결정된 사실이 아니라, ADC-02가 아직
  Open이기 때문에 남아 있는 현상 유지(default) 상태**임을 Baseline
  자신이 명시한다.
- `docs/03_adc/ADC.md`에 ADC-02가 애초에 등재되어 있다는 사실 자체가,
  "유지"가 이미 내려진 결론이 아니라 여전히 대조 대상임을 보여준다.

### Q0 결론(Evidence 기반)

"유지" 후보는 원문이 실재한다는 점에서 "대체" 후보보다 인용 가능한
근거는 많다. 그러나 그 원문 자체가 "세부 구조는 Open Decision"이라고
명시적으로 유보를 걸어 두었으므로, 이 원문은 "유지가 옳다"는 적극적
근거가 아니라 "아직 아무것도 바뀌지 않았다"는 현상 유지 기술일 뿐이다.
현상 유지를 뒷받침하는 것과 그것이 옳다고 확정하는 것은 다르다.
**이 Evidence만으로 "유지"를 Accept할 근거는 부족하다.**

---

## Q1. Candidate "대체"(Scheduler + Engine Gateway)는 지금 확정할 수 있는가?

### Evidence

- `docs/03_adc/ADC.md` ADC-02의 유일한 실질 근거: *"Core Component
  검토에서는 Runtime을 폐기하고 Scheduler + Engine Gateway로
  대체할 것을 권고함."*
- `GLOSSARY.md`와 `ADR-0002`가 "Core Component 검토"를 "과거에 실제로
  수행된 검토 단계의 고유 명칭"이라고 확인하지만, 그 검토의 원문·
  판단 근거·비교 기준은 어디에도 인용되지 않는다(RFC-0008 §2.2가
  전수 검색으로 확인).

### Q1 결론(Evidence 기반)

"대체" 후보의 근거는 결론 문구 하나("...대체할 것을 권고함")만
남아 있고, 그 권고에 이른 추론 과정·비교 기준·관찰 사실은 저장소
어디에도 존재하지 않는다. 결론만 있고 추론이 없는 근거로 Architecture
를 결정하는 것은 이 저장소의 Freeze 원칙("미결정 사항이 정직하게
드러나 추적되는 것이 목표")과 정면으로 배치된다. **이 Evidence만으로
"대체"를 Accept할 근거는 없다.**

---

## Q2. 어느 한쪽이 다른 쪽에 대한 근거 부족을 이유로 채택될 수 있는가?

### 검토

Q0·Q1은 서로 다른 이유로 각각 Accept를 보류했다. 이 비대칭
(유지=원문 실재하나 유보 명시, 대체=원문 부재)을 근거로 "대체의
근거가 없으니 유지가 맞다"고 결론짓는 것은, 한쪽 주장의 근거
부재가 반대쪽 주장의 참을 증명하지 않는다는 원칙(무지에 호소하는
오류를 피하는 것)에 어긋난다. `RFC-0008`도 "이 RFC는... 그 근거가
지금 판단을 가능하게 하는지만 질문한다"고 스스로 한정했다 — 비대칭
자체를 판단 근거로 쓰라고 요청한 적이 없다.

### Q2 결론(Evidence 기반)

"유지"가 "대체"보다 인용 가능한 원문이 많다는 사실은 있지만, 그
원문이 스스로 미결정임을 선언하고 있으므로, 이 비대칭은 "유지"를
선택할 근거가 될 수 없다. **두 후보 모두 Accept할 수 없다.**

---

## Decision

**Not Accepted (based on current evidence)**

"유지"와 "대체" 중 어느 것도 채택하지 않는다. 억지로 결론을 내리지
않는다.

### Reason

"유지" 근거(BASELINE.md §6)는 원문이 실재하나 스스로 미결정임을
명시하므로 확정 근거가 될 수 없다(Q0). "대체" 근거("Core Component
검토")는 결론만 남고 추론 과정이 저장소 어디에도 없어 채택할 수
없다(Q1). 한쪽 근거의 부재가 다른 쪽의 채택 근거가 되지 않는다(Q2).

## Decision Rationale

Q0·Q1·Q2는 각각 독립적인 이유로 두 후보 모두를 배제했다 — 이는
`ADC-0001-artifact-drift-boundary.md`(execution-layer)와
`ADC-0004-execution-result-consumer.md`(execution-layer)가 이미 쓴
것과 동일한 판단 방식이다: 확보된 Evidence가 어느 쪽도 뒷받침하지
못하면, 후보를 억지로 좁히지 않고 Not Accepted로 남긴다.

## 부족한 Evidence — 무엇이 있어야 재판단 가능한가

새로 만들지 않는다 — 지금 확인된 공백만 기록한다.

1. **"Core Component 검토"의 원문 또는 그에 준하는 재구성 가능한
   기록.** 그 검토가 Runtime 폐기를 권고한 실제 이유(무엇을
   비교했는지, 어떤 관찰에 근거했는지)가 없이는 "대체"를 판단할
   방법이 없다. 이 문서를 찾거나 재작성하는 것은 이 ADC의 권한이
   아니다.
2. **Runtime의 "세부 구조"가 실제로 문제를 일으켰다는 반복 관찰.**
   `ADC-0004-execution-result-consumer.md`(Q3)가 남긴 것은 "Runtime
   개념이 결정되지 않아 다른 판단이 막혔다"는 사실 하나뿐이다
   (관찰 1건). "유지" 또는 "대체" 중 하나를 정당화할 만큼의 반복
   관찰(Governance v2 Rule B의 정신과 같은 종류)은 아직 없다.
3. 위 둘 중 하나가 채워지기 전까지, 이 질문은 "결정을 미루는 것"이
   아니라 "결정할 재료가 없는 것"이다 — Freeze 원칙이 요구하는
   구분이다.

## Risks

- 이 Decision은 ADC-02를 v1.0 이후 처음으로 Boundary Question 형태로
  대조했으나, 여전히 Open으로 남긴다. `docs/03_adc/ADC.md`의 ADC-02
  항목 상태(Open, 우선순위 NOW)는 이 ADC로 변경되지 않는다 — 이
  ADC는 그 문서를 수정하지 않는다.
- `ADC-0004-execution-result-consumer.md`가 남긴 Blocking Evidence는
  이 Decision 이후에도 해소되지 않는다. Execution Result Consumer는
  여전히 Not Accepted 상태로 남으며, 이는 새로운 문제가 아니라
  §부족한 Evidence 2번이 채워지기 전까지 이미 예상된 상태의 지속이다.
- "결정할 재료가 없다"는 이 Decision이 "Runtime 논의를 다시 열지
  말라"는 뜻으로 오독될 위험이 있다 — 그런 뜻이 아니다. §부족한
  Evidence 중 하나라도 채워지면 재판단 대상이 된다.

**재검토 조건**: §부족한 Evidence 1번(Core Component 검토 원문 확보)
또는 2번(Runtime 미결정으로 인한 반복 관찰 축적)이 실제로 충족되면,
이 Decision은 기존 Governance 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다 — 이
문서를 직접 고쳐 뒤집는 것이 아니라, 새 RFC가 새 Evidence를 근거로
열리는 절차를 따른다.

## Next Step

**No ADR Required** — "Not Accepted (based on current evidence)"는
Runtime의 존폐를 확정하지 않으므로 Baseline 변경을 전제하지 않는다.

`docs/03_adc/ADC.md`의 ADC-02 항목은 갱신하지 않는다 — Open·NOW
상태 그대로 유지된다. 이 판단이 그 등재 상태를 바꿀 근거를 제공하지
않는다(§부족한 Evidence).

`ADC-0004-execution-result-consumer.md`도 갱신하지 않는다 — 그
Not Accepted 상태와 재검토 조건은 그대로 유효하다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서(`BASELINE.md`, `docs/03_adc/ADC.md`)를 변경했는가 —
  **아니오**. 이 ADC는 기존 Baseline과 ADC.md를 인용만 했다.
- ADR이 필요한가 — **아니오**. Not Accepted는 Boundary를 이동시키지
  않으므로 Baseline Update를 전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0008과 그것이 인용한
  `BASELINE.md` §6, `ADC.md` ADC-02, `GLOSSARY.md`, `ADR-0002`,
  `RFC-0004`(Dev HQ), `ADC-0004`(execution-layer)만 인용했다. 새
  실험은 하지 않았다.
- "Core Component 검토"의 원문을 추정으로 보완했는가 — **아니오**.
  부재 사실만 그대로 기록했다(§Q1, §부족한 Evidence 1번).
- 비대칭성을 근거로 한쪽을 암묵적으로 선택했는가 — **아니오**(§Q2)
  — 명시적으로 그 오류를 피했다.
- 억지로 결론을 내렸는가 — **아니오**. Not Accepted로 남겼다.
- `docs/03_adc/ADC.md`를 수정했는가 — **아니오**(§Next Step).
- `ADC-0004-execution-result-consumer.md`를 수정했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q0~Q2에서 다룬
  비대칭·공백은 RFC-0008이 이미 정리한 것이며, 이 ADC가 새로 발견한
  문제가 아니다.
