# ADC-0005: Engine 연결 Boundary — 허용 여부 판단 (RFC-0005 후속)

## 목적

`docs/core/execution-layer/RFC-0005-engine-connection-boundary.md`가
연 질문을 좁혀서 판단한다. RFC-0005 §4는 "어느 지점에서 호출하는가"
"반환값을 어떻게 변환하는가" 두 하위 질문을 미결로 남겼다. 이 ADC는
그 두 질문에 답하지 않는다 — 대신 그보다 먼저 물어야 하는 질문 하나만
판단한다.

**판단 대상**: "Execution Layer의 `results`에 실제 Engine 산출물을
연결하는 것이 현재 Architecture에서 허용되는가?"

근거는 RFC-0005와 그것이 인용한 Evidence(`ARTIFACT-STANDARD-v1.md`,
`core/execution_layer/mvp_0001~0006/*.py`, `core/execution_layer/pipeline.py`,
`development-hq/mvp/engine.py`, `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`,
`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`)
로만 한정한다. `docs/research/ENGINE-INTEGRATION-0001~0006-Claude-Code.md`
는 RFC-0005가 직접 인용하지 않았으므로 이 ADC도 새로 끌어오지 않는다
— RFC-0005의 인용 범위를 벗어나지 않는다. 새로운 Evidence·실험·
Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Engine 연결의 실제 방식(어느 Builder가 호출하는지, 반환값을
  `results: list[str]`로 어떻게 변환하는지) — RFC-0005 §4의 두 하위
  질문은 그대로 미결로 남긴다.
- ADC-01(Model 축과 Component 축의 대응 관계), ADC-02(Runtime 존폐)
  — 재조사하지 않는다. 이 ADC의 판단은 그 둘의 Not Accepted 여부와
  무관하게 성립한다(§Q0·Q1 참고).
- Execution Result Consumer — `ADC-0004-execution-result-consumer.md`
  의 범위(Execution Result가 만들어진 **뒤** 누가 소비하는가)와 이
  ADC의 범위(Execution Result가 만들어지기 **전** 그 content가 어디서
  오는가)는 서로 다른 질문이다. 이 ADC는 Consumer 쪽으로 확장하지
  않는다.
- Engine Gateway/Adapter 설계, ADR, 코드 구현.

---

## Q0. Caller가 Execution Layer 밖에서 Engine을 호출하고, 그 결과를 caller-supplied `results`로 주입하는 것은 허용되는가?

### Evidence

- `core/execution_layer/mvp_0006/execution_result_builder.py`:
  `build_execution_result(execution_state, *, handle_id, produced_at,
  results: list[str])` — `results`는 함수 **매개변수**이며, 이미
  `ADC-0002-execution-result-contract.md`(형태=목록)·
  `ADC-0003-execution-result-item-schema.md`(항목 타입=`str`)로
  Contract가 확정됐다. 이 Contract는 값의 **출처**를 제한하지
  않는다 — Builder는 caller가 넘긴 문자열을 그대로 담을 뿐이다
  (`IMPL-STOP-0002` §2 E-3·E-4가 이미 확인한 사실: Builder는 항목의
  의미를 해석하지 않는다).
- `ARTIFACT-STANDARD-v1.md` "공통 패턴": *"AI 호출 없음, Runtime
  없음. 6개 MVP 전체에서 `call_engine`... 문자열이 **소스 코드에
  없음**을 각 MVP의 테스트로 확인했다."* 이 불변식은 텍스트 그대로
  **모듈 소스 코드의 범위**로 한정된다.
- 그 불변식을 강제하는 실제 테스트
  (`test_no_ai_or_runtime_symbols_present_in_module`, 6개 Builder +
  Pipeline 전부에 반복)는 `inspect.getsource(module)`로 **해당
  모듈 자신의 소스**만 검사한다 — caller가 Builder를 호출하기 전에
  무엇을 하는지는 이 테스트의 검사 대상이 아니다.
- `development-hq/mvp/engine.py`의 `call_engine()`은 이미 존재하고
  실제 Engine을 호출한다(모듈 자체 docstring: "그 실험 결과를 그대로
  tracked branch에 반영한다"). `ENGINE-CONNECT-0001`은 이 함수를
  실제 호출로 교체해도 "어떤 Stop Trigger도 발동하지 않았다"고
  기록했다 — 이는 Development HQ 범위의 관찰이지만, `call_engine()`
  자체가 안전하게 호출 가능한 단일 함수라는 사실은 그대로 전이된다
  (함수 자체의 성질이지 호출 위치에 종속된 성질이 아니다).

### Q0 결론(Evidence 기반)

caller가 Execution Layer의 Builder/Pipeline **밖**에서 `call_engine()`
을 호출하고, 그 반환값을 이미 결정된 caller-supplied `results`
매개변수에 그대로 전달하는 것은, 기존의 어떤 Contract·불변식도
위반하지 않는다 — `results`의 Contract(§ADC-0002·0003)는 이미
caller-supplied로 확정되어 있고, "AI 호출 없음" 불변식은 Builder
자신의 소스 코드 범위로 명시적으로 한정되어 있다. **Accept.**

이 Accept는 새 Architecture나 Contract를 만드는 것이 아니다 — 이미
확정된 `results: list[str]`의 caller-supplied 성질을 그대로 사용하는
것일 뿐이다.

---

## Q1. Execution Layer 자신(Builder 또는 Pipeline)이 내부에서 `call_engine()`을 호출하는 것은 허용되는가?

### Evidence

- 위 Q0와 동일한 테스트(`test_no_ai_or_runtime_symbols_present_in_module`)
  가 6개 Builder + `pipeline.py` 전부에서 `call_engine` 문자열의
  부재를 **직접** 검증한다 — 어느 모듈이든 내부에서 `call_engine()`을
  호출하는 코드를 추가하면 이 테스트가 실패한다.
- `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`:
  *"내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model
  Routing)는... ADC-01·ADC-02가 여전히 Open으로 남긴 영역이다."*
  Execution Layer가 Engine을 선택·호출하는 책임 자체는 Kernel Module
  수준에서 Accept됐으나, 그 내부 **방식**은 명시적으로 미결이다.

### Q1 결론(Evidence 기반)

Execution Layer 내부(Builder 또는 Pipeline)가 `call_engine()`을
직접 호출하려면, 6개 MVP + Pipeline 전체에 걸쳐 반복 검증된 "AI
호출 없음" 불변식을 실제로 깨야 한다. 이는 기존 테스트가 명시적으로
막고 있는 변경이며, 이 불변식을 개정하려면 Baseline 수준의 Governance
(RFC-0005의 §Next Step 판단 2가 이미 예견한 것)가 선행되어야 한다.
**Not Accepted (based on current evidence)** — 이번 ADC의 범위에서는
결정하지 않는다.

---

## Decision

**부분 Accept**: caller 수준의 연결(Q0)은 **Accept**된다 — 이미
확정된 Contract를 그대로 사용하는 것이므로 새 결정이 필요 없다.
Execution Layer 내부에서의 직접 호출(Q1)은 **Not Accepted (based on
current evidence)**로 남는다 — 기존 불변식을 깨는 것이므로 별도
Governance 없이는 진행할 수 없다.

### Reason

두 질문은 서로 다른 Evidence에 근거해 서로 다른 결론에 도달한다.
Q0는 이미 확정된 Contract(caller-supplied `results`)와 명시적으로
범위가 한정된 불변식("소스 코드에 없음")을 그대로 적용한 결과다 —
새 판단이 아니라 기존 결정의 재확인이다. Q1은 그 불변식을 정면으로
깨야 하므로, 이 ADC의 권한(RFC-0005의 근거만 사용)으로는 Accept할
수 없다.

## Decision Rationale

RFC-0005가 미결로 남긴 두 하위 질문("어느 지점에서 호출하는가",
"반환값을 어떻게 변환하는가")은 **Execution Layer 내부** 호출을
전제로 한 질문이었다(Q1 영역). 이 ADC는 그 질문들에 답하기 전에,
애초에 "내부 호출이 필요한가, 아니면 caller 수준에서 이미 가능한
연결이 있는가"부터 구분했다. 그 결과 caller 수준 연결(Q0)은 이미
허용되어 있었다는 사실을 확인했을 뿐, 그것을 새로 결정하지 않았다.

## Risks

- Q0의 Accept는 "Engine 연결이 완전히 해결됐다"는 뜻이 아니다. caller
  가 `call_engine()`을 언제·어떻게·어떤 prompt로 호출하는지, 그
  반환값(자유 서술형 산문, `ENGINE-CONNECT-0001` 관찰)을 `results:
  list[str]`의 몇 개 항목으로 어떻게 나눌지는 여전히 결정된 바 없다
  — RFC-0005 §4의 "변환 규칙" 질문은 그대로 미결이다.
- Q0와 Q1의 경계(caller 수준 vs Builder 내부)는 `inspect.getsource`
  기반 테스트의 검사 범위에서 직접 도출한 것이지만, 이 경계 자체가
  Execution Layer의 "책임"을 어디까지로 볼 것인가라는 더 큰 질문
  (ADC-01, 재조사하지 않음)과 맞닿아 있다 — 이 ADC는 그 더 큰 질문을
  판단하지 않는다.
- Q1의 Not Accepted는 "영원히 금지"가 아니라 "지금 이 Evidence로는
  결정할 수 없다"는 뜻이다.

**재검토 조건**: Q1은 "AI 호출 없음" 불변식의 개정이 실제로 필요하다는
새 Evidence(예: caller 수준 연결만으로는 부족한 구체적 실패 사례)가
관찰되거나, ADC-01·ADC-02 중 하나가 재검토되어 Execution Layer 내부
구조에 대한 근거가 생기면, 기존 Governance 절차(RFC → ADC → ADR →
Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**Q0에 대해 No ADR Required** — 이미 확정된 Contract(caller-supplied
`results`)를 재확인했을 뿐, Baseline이나 `ARTIFACT-STANDARD-v1.md`를
변경할 내용이 없다.

**Q1에 대해서도 No ADR Required** — Not Accepted는 Boundary를
이동시키지 않으므로 Baseline Update를 전제하지 않는다.

RFC-0005 §4의 두 하위 질문(호출 지점, 변환 규칙)은 여전히 미결이다.
다만 그 질문들은 이제 "Execution Layer 내부에서 호출해야 하는가"
(Q1, Not Accepted)를 전제로 다시 검토되어야 한다 — caller 수준
연결(Q0, Accept)을 택한다면 그 두 질문은 Execution Layer의 Contract
문제가 아니라 caller(예: Development HQ ↔ Execution Layer를 잇는
별도 스크립트나 함수)의 구현 문제가 된다. 이 ADC는 그 선택을 하지
않는다 — 다음 절차가 판단할 사항이다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서(`ARTIFACT-STANDARD-v1.md`, Kernel Baseline)를
  변경했는가 — **아니오**. 이 ADC는 기존 Contract와 테스트 범위를
  인용만 했다.
- ADR이 필요한가 — **아니오**(Q0·Q1 모두).

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0005와 그것이 인용한
  `ARTIFACT-STANDARD-v1.md`, 6개 Builder + Pipeline 소스,
  `engine.py`, `ENGINE-CONNECT-0001`,
  `ADR-0002-execution-layer-module-baseline.md`만 인용했다.
  `ENGINE-INTEGRATION-0001~0006`은 RFC-0005가 인용하지 않았으므로
  새로 끌어오지 않았다.
- Engine 연결 방식을 선택했는가 — **아니오**. Q0·Q1은 "허용되는가"
  라는 경계 질문에만 답했다 — 어느 Builder가 언제 어떻게 호출할지는
  결정하지 않았다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. 두 질문 모두 인용
  없이 판단됐다(§목적).
- Execution Result Consumer로 범위를 확장했는가 — **아니오**(§목적
  에서 명시적으로 구분).
- 억지로 결론을 내렸는가 — **아니오**. Q1은 Not Accepted로 남겼다.
- ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q0·Q1에서 다룬
  경계는 RFC-0005·기존 테스트 범위가 이미 담고 있던 사실이며, 이
  ADC가 새로 발견한 문제가 아니다.
