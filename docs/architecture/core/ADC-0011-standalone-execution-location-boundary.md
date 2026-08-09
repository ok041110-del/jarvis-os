# ADC-0011: Kernel/HQ에 속하지 않는 별도 실행 위치 — 허용 여부 판단 (RFC-0011 후속)

## 목적

`docs/architecture/core/RFC-0011-standalone-execution-location-boundary.md`
가 연 Boundary Question을 판단한다.

**판단 대상**: "Kernel/HQ에 속하지 않는 별도 실행 위치를 Jarvis OS
Architecture의 공식 Concept으로 둘 수 있는가?"

근거는 RFC-0011과 그것이 인용한 Evidence(`ADC-0010-engine-caller-location-boundary.md`,
`RFC-0010-engine-caller-location-boundary.md`,
`ADC-0005-engine-connection-boundary.md`(execution-layer),
`ENGINE-CONNECT-0002~0004`, `BASELINE.md` §6·§7·§10,
`development-hq/CONSTITUTION.md`, `development-hq/BOUNDARY.md`,
`projects/development-hq-devkit/runner.py`·`README.md`)로만 한정한다.
새로운 Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- "별도 실행 위치" Concept의 상세 설계(이름, 필드, 책임 목록) —
  Boundary Question이 Accept되더라도 이 ADC는 설계하지 않는다.
- 소속 Namespace의 실제 선택.
- Engine Adapter와의 관계에 대한 실제 판단.
- ADC-01(Model 축과 Component 축의 대응 관계)·ADC-02(Runtime 존폐)
  — 재조사하지 않는다. 기존 Not Accepted 결론만 인용한다.
- Execution Result Consumer — 재조사하지 않는다.
- 기존 caller 후보 C1~C6(`ADC-0010`) — 재조사하지 않는다. 상태만
  인용한다.
- ADR·Implementation — 이 단계에서 다루지 않는다.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0011의 Boundary Question에
현재 Evidence로 Yes 또는 No를 확정할 수 있는가?**

---

## Evidence 충분성 검토

Yes/No를 억지로 고르지 않기 위해, 먼저 각 방향을 뒷받침할 Evidence가
실제로 존재하는지부터 확인한다.

### "Yes"를 뒷받침하는 Evidence가 있는가?

- `BASELINE.md` §6 Concept Model은 10개 분류의 표를 제시하지만,
  이 표가 확장 가능한지("11번째 분류를 추가할 수 있다") 또는
  고정인지를 명시하는 문장이 어디에도 없다. 표의 존재 자체는
  "확장 가능하다"는 근거가 되지 않는다 — 침묵일 뿐이다.
- `projects/development-hq-devkit/runner.py`가 Kernel도
  `development-hq/`도 아닌 위치에 실제로 존재한다는 사실
  (`RFC-0011` §2, `ENGINE-CONNECT-0004` §Q1)은 "그런 위치에 코드가
  물리적으로 존재할 수 있다"는 것만 보여준다 — 그것이 **Architecture
  공식 Concept으로서** 인정된 적이 있다는 근거는 아니다. 이 스크립트를
  인용하는 Governance 문서(`docs/governance/observations/OBS-0003~0006`)
  어디에도 이 위치를 Concept Model에 등재하자는 제안이나 판단이
  없다(RFC-0011이 이미 인용 범위를 그 문서들까지 넓히지 않았고, 이
  ADC도 새로 끌어오지 않는다).
- 결론: **직접적인 "Yes" 근거 없음.** 있는 것은 물리적 존재 사례
  하나(역할은 다름)와, 표가 닫혀 있다고 말하지 않는 침묵뿐이다.

### "No"를 뒷받침하는 Evidence가 있는가?

- `BASELINE.md` §7 System Boundary는 책임을 "Jarvis OS의 책임"과
  "HQ의 책임" 두 절로만 서술한다. 그러나 이 서술도 "이 두 범주
  외에는 어떤 실행 위치도 존재할 수 없다"고 명시적으로 배제하는
  문장을 포함하지 않는다 — 두 범주의 책임을 나열했을 뿐, 제3
  범주의 가능성을 명시적으로 부정한 적은 없다.
- `BASELINE.md` §10 Out of Scope의 "Component Design"·"Implementation"
  은 **설계·구현 행위**를 Out of Scope로 두는 것이지, "제3의
  실행 위치라는 Concept 자체가 있을 수 없다"고 말하는 것이 아니다
  — Concept의 존재 여부와 그 Concept의 설계는 서로 다른 층위다
  (RFC-0011 §3이 이미 이 구분을 전제로 §3을 "만약 도입한다면"으로
  조건부 서술한 이유).
- 결론: **직접적인 "No" 근거도 없음.** 두 범주만 서술된 것은 지금까지
  결정된 것을 기술한 것이지, 앞으로도 두 범주만 존재해야 한다는
  금지 규범이 아니다.

### 판단

**Evidence가 부족하다.** Yes와 No 어느 쪽도 현재 인용 가능한
문서에서 직접 도출되지 않는다 — 있는 것은 "두 범주만 지금까지
서술되어 있다"는 사실과 "제3 위치에 물리적 코드가 실제로 존재한
적은 있으나 그것이 Concept으로 인정된 적은 없다"는 사실뿐이다.
이 둘로는 Boundary Question에 답할 수 없다.

---

## Decision

**Not Accepted (based on current evidence).**

Boundary Question("Kernel/HQ에 속하지 않는 별도 실행 위치를 공식
Concept으로 둘 수 있는가")에 대해 Yes도 No도 선택하지 않는다. 억지로
결론을 내리지 않는다.

### Reason

`ADC-0008`(Runtime 존폐)·`ADC-0009`(Model↔Component 대응)·`ADC-0010`
(Engine Caller 위치)이 이미 사용한 것과 동일한 판단 방식이다 —
확보된 Evidence가 어느 방향도 뒷받침하지 못하면, 침묵을 근거로
승격시키지 않고 Not Accepted로 남긴다. 이번 판단의 특이점은, Yes와
No 모두 "직접 반박하는 문장이 없다"는 점에서 대칭적으로 약하다는
것이다 — 이는 이 질문이 지금까지 어떤 문서에서도 실제로 다뤄진 적이
없었다는 사실(RFC-0011 §0)을 그대로 반영한다.

## 부족한 Evidence — 무엇이 있어야 재판단 가능한가

새로 만들지 않는다 — 지금 확인된 공백만 기록한다.

1. `BASELINE.md` §6 Concept Model이 확장 가능한 분류 체계인지,
   고정된 10개인지를 명시하는 문장 또는 그에 준하는 Governance
   판단(예: 과거에 Concept이 추가된 선례와 그 절차) — 현재 어디에도
   없다.
2. `projects/development-hq-devkit`와 같은 "Kernel/HQ 밖" 위치가
   Architecture Governance 절차를 통해 공식적으로 검토된 기록 —
   현재는 Dogfooding Testbed로 자기 한정된 상태로만 존재하며,
   Concept 승격을 시도하거나 논의한 기록이 없다.
3. `BASELINE.md` §7 System Boundary가 "Jarvis OS/HQ 두 범주로
   전체 책임을 완전히 소진한다(exhaustive)"는 것을 의도했는지,
   아니면 "지금까지 정의된 두 범주"라는 것만 의도했는지를 확인할
   수 있는 원 저작 의도 기록(Vision/Principles 단계 문서, 이번
   Evidence 범위 밖) — 이번 ADC는 그 문서를 새로 끌어오지 않았다.

## Risks

- Not Accepted는 "그런 위치가 영원히 있을 수 없다"는 뜻이 아니다
  — "지금 이 Evidence로는 있을 수 있는지조차 판단할 재료가 없다"는
  뜻이다(`ADC-0008`·`ADC-0009`·`ADC-0010`과 동일한 구분).
- 이 Decision은 `ADC-0010`의 C1~C6 판단을 바꾸지 않는다 — 특히 C6은
  이 Boundary Question이 Accept되지 않는 한 여전히 근거 없는
  상태로 남는다(`ADC-0010`의 Not Accepted 그대로 유지).
- Yes/No 모두 "직접 반박 문장이 없다"는 대칭적 근거 부족에서
  비롯된 것이므로, 향후 이 질문을 다시 열 때는 두 방향 모두에 대한
  새 Evidence(§부족한 Evidence 1~3)가 필요할 수 있다 — 한쪽만
  보강해서는 재판단이 어려울 수 있다는 관찰이며, 이 자체가 결론은
  아니다.

**재검토 조건**: §부족한 Evidence 1~3 중 하나라도 실제로 충족되면,
이 Decision은 기존 Governance 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**No ADR Required** — "Not Accepted (based on current evidence)"는
Concept을 확정하지도 배제하지도 않으므로 Baseline 변경을 전제하지
않는다.

`ADC-0010`의 C1~C6 판단은 갱신하지 않는다. `docs/03_adc/ADC.md`의
ADC-01·ADC-02 항목, `ADC-0004-execution-result-consumer.md`도
갱신하지 않는다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서를 변경했는가 — **아니오**. 이 ADC는 기존 Baseline과
  RFC-0011의 인용을 그대로 사용했다.
- ADR이 필요한가 — **아니오**. Not Accepted는 Boundary를 이동시키지
  않으므로 Baseline Update를 전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0011과 그것이 인용한 문서
  (`ADC-0010`, `RFC-0010`, `ADC-0005`, `ENGINE-CONNECT-0002~0004`,
  `BASELINE.md`, `development-hq/CONSTITUTION.md`,
  `development-hq/BOUNDARY.md`, `projects/development-hq-devkit/*`)
  만 인용했다. 새 실험은 하지 않았다.
- Yes/No를 억지로 선택했는가 — **아니오**. 양쪽 모두 직접 근거가
  없음을 확인하고 Not Accepted로 남겼다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. 상태만 인용했다.
- Execution Result Consumer를 재조사했는가 — **아니오**.
- C1~C6(기존 caller 후보)를 재조사했는가 — **아니오**. `ADC-0010`의
  판단을 그대로 인용만 했다.
- "별도 실행 위치" Concept을 설계했는가 — **아니오**.
- Namespace를 선택했는가 — **아니오**.
- Engine Adapter와의 관계를 판단했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
