# ADC-0010: Engine Caller의 위치와 책임 — Not Accepted (RFC-0010 후속)

## 목적

`docs/architecture/core/RFC-0010-engine-caller-location-boundary.md`가
제기한 Boundary Question — "`call_engine()`을 호출하고 그 결과를
Execution Layer의 `results`에 주입하는 caller는 어디에 위치하며,
누구의 책임인가?" — 에 대해, RFC-0010이 전수 확인한 6개 후보를
각각 판단한다.

근거는 RFC-0010과 그것이 인용한 Evidence(`ADC-0005-engine-connection-boundary.md`,
`docs/01_architecture/BASELINE.md` §6·§7·§10,
`development-hq/BOUNDARY.md`,
`docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`,
`docs/architecture/core/ADC-0001-core-baseline.md`,
`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`,
6개 Dogfooding 스크립트, `ARTIFACT-STANDARD-v1.md`)로만 한정한다.
새로운 Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- ADC-01(Model 축과 Component 축의 대응 관계), ADC-02(Runtime 존폐)
  — 재조사하지 않는다. 기존 Not Accepted 결론만 인용한다.
- Execution Result Consumer — 재조사하지 않는다.
- Kernel Engine Gateway/Adapter의 설계·구현.
- Engine 연결의 변환 규칙(반환값→`results` 매핑).

이 ADC가 판단하는 것은 오직 하나다: **RFC-0010이 전수 확인한 6개
caller 후보 중 현재 Evidence로 Accept 가능한 것이 있는가?**

---

## 후보별 판단

### C1. Kernel Engine Port/Adapter

**Evidence**: `BASELINE.md` §7 "Engine 호출의 표준 인터페이스 제공
(Port/Adapter)"이 Jarvis OS 책임으로 Frozen — **책임의 귀속**은
확정되어 있다. 그러나 `BASELINE.md` §10 Out of Scope: *"Component
Design (Scheduler, Engine Gateway, Registry, Communication, Memory,
Policy 등)"* — **설계·구현 자체가 명시적으로 범위 밖**이다.

**판단**: 책임이 귀속되어 있다는 사실과 그 책임을 수행할 실체가
존재한다는 사실은 다르다. 지금 이 후보를 caller로 Accept하면, §10이
Out of Scope로 명시한 Component(Engine Gateway)의 설계에 착수하는
것과 같은 효과를 가진다 — 이는 이 ADC의 권한 밖이며 새 Architecture
설계 금지 원칙에 위배된다. **Not Accepted (based on current
evidence)** — 실체가 없어 지금 caller 역할을 할 수 없다.

### C2. Runtime

**Evidence**: `BASELINE.md` §6 "Runtime은 Concept으로서 Baseline에
유지되나, 그 세부 구조는 Open Decision이다 (ADC-02)." ADC-02는
`ADC-0008-runtime-existence-boundary.md`로 이미 Not Accepted 종결됐다
(재조사하지 않고 상태만 인용).

**판단**: Runtime의 존재 자체가 미결인 상태에서, 그것을 caller로
지정하는 것은 미결정 위에 새 결정을 얹는 것과 같다. **Not Accepted
(based on current evidence)**.

### C3. Session

**Evidence**: `ARTIFACT-STANDARD-v1.md`가 "Session/Runtime의 책임
영역"을 언급하지만, `BASELINE.md` §6 Concept Model의 10개 분류
(Entity/Definition/Process/Event/Service/Interface/Metadata/Policy/
State/Resource) 어디에도 "Session"이 등재된 적이 없다.

**판단**: 정의되지 않은 개념을 caller로 지정하는 것은 새 Concept을
만드는 것과 같다 — 이 ADC의 권한 밖이다. **Not Accepted (based on
current evidence)**.

### C4. Development HQ

**Evidence**: `RFC-0005-development-hq-execution-boundary.md`
§Out of Scope: *"Runtime, Multi-Agent, Model Routing, Engine Adapter
구현... 을 다루지 않는다."* §4: *"Development HQ Constitution v1.0의
Architecture Freeze 목록에 Engine Adapter, Model Routing이 이미
포함되어 있다."*

**판단**: Development HQ는 후보 검토 대상이 아니라 **명시적으로
배제된 대상**이다. **Not Accepted** — 이 판단은 새 결정이 아니라
기존 Freeze 목록의 재확인이다.

### C5. Dogfooding 스크립트(6개)

**Evidence**: `core/execution_layer/mvp_0001~0006/dogfooding/run_dogfooding.py`
각 docstring이 스스로를 검증 목적으로 한정한다(*"이 스크립트가
호출자로서 값을 주입한다"* — 매 MVP의 Contract 검증 맥락에서만).

**판단**: 이 스크립트들이 6번 caller 역할을 수행했다는 사실은
Contract가 caller-supplied 값으로 실제 작동한다는 것을 증명했을
뿐, 그 caller가 **production 위치**여야 한다는 근거는 아니다 — 문서
스스로 그렇게 주장한 적이 없다. **Not Accepted (based on current
evidence)**.

### C6. 별도 스크립트/함수(Dev HQ↔Execution Layer를 잇는, 이름 없음)

**Evidence**: `ADC-0005-engine-connection-boundary.md` Next Step의
예시 문구 *"caller(예: Development HQ ↔ Execution Layer를 잇는 별도
스크립트나 함수)"*뿐이며, 같은 문서가 *"이 ADC는 그 선택을 하지
않는다"*고 명시했다.

**판단**: 이름·형태·위치 무엇도 정의된 적 없는 후보를 지금 Accept
하는 것은, 이 ADC가 새로 Architecture(새 Component의 존재)를
발명하는 것과 같다. **Not Accepted (based on current evidence)**
— Evidence 자체가 예시 수준에 그친다.

---

## Decision

**Not Accepted (based on current evidence) — 6개 후보 전부.**

어느 후보도 caller 위치로 선택하지 않는다. 억지로 결론을 내리지
않는다.

### Reason

6개 후보 각각이 서로 다른 이유로 Accept될 수 없었다: C1은 책임은
있으나 실체가 없고(설계 자체가 Out of Scope), C2는 그 존재 자체가
Open(ADC-02, 재조사하지 않음)이며, C3은 정의된 적 없는 개념이고,
C4는 명시적으로 배제됐으며, C5는 검증 목적으로만 문서화됐고, C6은
예시 수준의 언급 외에 근거가 없다. 여섯 판단 모두 새 Evidence를
만들지 않고 RFC-0010이 이미 정리한 인용만 사용했다.

## Decision Rationale

이 결과는 `ADC-0008`(Runtime 존폐)·`ADC-0009`(Model↔Component
대응)가 이미 사용한 것과 동일한 판단 방식이다 — 확보된 Evidence가
어느 후보도 뒷받침하지 못하면, 후보를 억지로 좁히지 않고 Not
Accepted로 남긴다. 특히 C1(Kernel Engine Port/Adapter)의 경우처럼
"책임의 귀속"과 "실체의 존재"를 구분한 것은 RFC-0010 §3 Pattern이
이미 명시한 구분을 그대로 적용한 것이며, 이 ADC가 새로 만든 기준이
아니다.

## 부족한 Evidence — 무엇이 있어야 재판단 가능한가

새로 만들지 않는다 — 지금 확인된 공백만 후보별로 기록한다.

1. **C1(Kernel Engine Port/Adapter)**: Kernel Component Architecture
   설계 착수(현재 §10 Out of Scope) — 이 자체가 여러 선행 조건
   (Kernel Module Defer 3건, ADC-01·02, Engine 수 ≥2 등)에 걸려
   있다.
2. **C2(Runtime)**: ADC-02의 재검토 조건(`ADC-0008` §부족한
   Evidence — "Core Component 검토" 원문 또는 반복 관찰)이 먼저
   충족되어야 한다.
3. **C3(Session)**: Session을 Kernel Concept Model에 등재하는 것
   자체가 새 RFC 대상이며, 이 ADC의 범위가 아니다.
4. **C4(Development HQ)**: Freeze 목록 자체를 재론하지 않는 한
   재검토 근거가 생기지 않는다 — Phase 1 종료 후 불변 원칙과
   충돌한다.
5. **C5(Dogfooding)**: 검증 스크립트를 production 위치로 승격하려는
   시도가 실제로 관찰되거나 명시적으로 제안되어야 한다.
6. **C6(별도 스크립트/함수)**: 이 후보 자체를 구체화하는 새 RFC가
   필요하다 — 이름·형태·소속 네임스페이스(Dev HQ? Execution Layer?
   독립?) 무엇도 없다.

## Risks

- 6개 후보 전부 Not Accepted라는 결과는 "caller 위치가 영원히
  없다"는 뜻이 아니라, "지금 이 Evidence로는 결정할 재료가 없다"는
  뜻이다(`ADC-0008`·`ADC-0009`와 동일한 구분).
- `ADC-0005-engine-connection-boundary.md` Q0가 Accept한 "caller
  수준 연결 자체는 허용된다"는 결론은 이 ADC로 바뀌지 않는다 — 다만
  그 caller가 실제로 어디 있어야 하는지는 여전히 공백으로 남는다.
- C6이 가장 약한 형태의 후보(예시 수준)였다는 사실은, 향후 이
  질문을 다시 열 때 새 후보를 원점에서 정의해야 할 수도 있음을
  시사한다 — 이 ADC는 그 시사점을 결론으로 삼지 않는다(추정이며
  Evidence가 아니다).

**재검토 조건**: §부족한 Evidence 1~6 중 하나라도 실제로 충족되면,
이 Decision은 기존 Governance 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**No ADR Required** — "Not Accepted (based on current evidence)"는
caller 위치를 확정하지 않으므로 Baseline 변경을 전제하지 않는다.

`docs/core/execution-layer/ADC-0005-engine-connection-boundary.md`의
Q0 Accept 결론은 그대로 유지된다 — 이 ADC는 그것을 재론하지 않았다.
`docs/03_adc/ADC.md`의 ADC-01·ADC-02 항목, `ADC-0004-execution-result-consumer.md`
는 갱신하지 않는다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서를 변경했는가 — **아니오**. 이 ADC는 기존 Baseline과
  RFC-0010의 인용을 그대로 사용했다.
- ADR이 필요한가 — **아니오**. Not Accepted는 Boundary를 이동시키지
  않으므로 Baseline Update를 전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0010과 그것이 인용한
  6개 문서/소스만 인용했다. 새 실험은 하지 않았다.
- caller 위치를 임의로 선택했는가 — **아니오**. 6개 후보 전부 Not
  Accepted로 남겼다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. 상태만 인용했다(C1·C2).
- Execution Result Consumer를 재조사했는가 — **아니오**.
- 새 Architecture(Engine Gateway, Session Concept 등)를 설계했는가 —
  **아니오**.
- 억지로 결론을 내렸는가 — **아니오**. 6개 후보 전부 Not Accepted로
  남겼다.
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 후보별 공백은
  RFC-0010이 이미 인지한 것이며, 이 ADC가 새로 발견한 문제가
  아니다.
