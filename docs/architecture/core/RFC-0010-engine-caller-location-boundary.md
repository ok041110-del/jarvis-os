# RFC-0010: Engine Caller의 위치와 책임 — Boundary (ADC-0005 Q0 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Engine 연결 Boundary 조사 후속)
**대상**: `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md`
Q0가 Accept한 "외부 caller가 `call_engine()`을 호출하고 그 결과를
caller-supplied `results`로 주입하는 것" — 그 **caller가 물리적으로
어디에 있어야 하는가**는 아직 어느 문서도 결정한 적이 없다
**Evidence**: `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md`,
`docs/01_architecture/BASELINE.md` §6·§7·§10,
`development-hq/BOUNDARY.md`,
`docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`,
`docs/architecture/core/ADC-0001-core-baseline.md`,
`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`,
`core/execution_layer/mvp_0001~0006/dogfooding/run_dogfooding.py`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`

> 본 RFC는 caller의 위치를 결정하지 않는다. 새 Architecture를
> 설계하지 않는다. Engine Gateway/Adapter를 만들지 않는다. 새
> 실험을 하지 않는다. 이 RFC는 이미 저장소에 기록된 caller 후보를
> 전수 정리하고, 각 후보의 근거를 있는 그대로 대조한다. 최종 선택은
> 후속 ADC로 넘긴다. ADC-01·ADC-02·Execution Result Consumer는
> 재조사하지 않는다 — 기존 결정으로만 인용한다.

## 0. 이 RFC가 열린 이유

`ADC-0005-engine-connection-boundary.md` Q0는 "caller가 Execution
Layer 밖에서 `call_engine()`을 호출하고 그 결과를 caller-supplied
`results`에 주입하는 것"을 Accept했다. 그러나 같은 문서의 Next Step은
그 caller가 무엇인지 "예"로만 들었을 뿐 결정하지 않았다: *"caller
(예: Development HQ ↔ Execution Layer를 잇는 별도 스크립트나 함수)의
구현 문제가 된다... 이 ADC는 그 선택을 하지 않는다 — 다음 절차가
판단할 사항이다."* 이 RFC는 그 다음 절차다.

## 1. Problem Statement

Execution Layer의 Builder/Pipeline은 `results: list[str]`을
caller-supplied로만 받는다(이미 결정된 Contract). 그 값을 실제로
채우려면 누군가 `call_engine()`을 호출해야 하는데, 그 "누군가"가
Development HQ인지, (설계되지 않은) Kernel Engine Gateway인지,
아직 이름 없는 별도 위치인지가 결정된 바 없다.

## 2. Evidence Summary — 이미 존재하는 caller 후보 전수 확인

| 후보 | 근거(원문 인용) | 상태 |
|---|---|---|
| **Kernel Engine Port/Adapter** | `BASELINE.md` §7: *"Engine 호출의 표준 인터페이스 제공 (Port/Adapter)"*(Jarvis OS 책임, v1.0부터 Frozen). `development-hq/BOUNDARY.md`: *"Engine 호출 \| Kernel Engine Port/Adapter의 책임"*. `BASELINE.md` §11 표: *"Engine 호출 책임 \| Engine Gateway"*(구현 후보, 채택 여부 미정) | **책임은 Frozen, 설계·구현은 §10 Out of Scope**(`BASELINE.md` §10: *"Component Design (Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)"*) — 실체가 존재하지 않는다 |
| **Runtime** | `BASELINE.md` §6: *"Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다."* 같은 절: *"그 세부 구조는 Open Decision이다 (ADC-02)."* | **ADC-02 Open — 재조사하지 않고 상태만 인용.** caller로 명명된 적 없다 |
| **Session** | `ARTIFACT-STANDARD-v1.md`: *"Session/Runtime의 책임 영역을 Execution Layer Builder가 침범하지 않기 위함이다"* | `BASELINE.md` §6 Concept Model 10개 분류(Entity/Definition/Process/Event/Service/Interface/Metadata/Policy/State/Resource) 어디에도 없음 — **정의된 개념이 아니라 제외 라벨로만 사용됨** |
| **Development HQ** | `RFC-0005-development-hq-execution-boundary.md` §Out of Scope: *"Runtime, Multi-Agent, Model Routing, Engine Adapter 구현... 을 다루지 않는다."* §4: *"Development HQ Constitution v1.0의 Architecture Freeze 목록에 Engine Adapter, Model Routing이 이미 포함되어 있다."* | **명시적으로 배제됨** — Dev HQ 자신의 `call_engine()`은 Dev HQ 내부 목적(code_review 등)에 한정된다 |
| **Dogfooding 스크립트**(6개) | `core/execution_layer/mvp_0001~0006/dogfooding/run_dogfooding.py` 각 docstring: *"이 스크립트가 호출자로서 값을 주입한다"* | **검증 전용으로만 명시됨** — 어떤 문서도 이를 production caller로 지정한 적 없다 |
| **별도 스크립트/함수**(Dev HQ↔Execution Layer를 잇는) | `ADC-0005-engine-connection-boundary.md` Next Step의 예시 문구뿐 | **결정된 바 없음 — 이 ADC 자신이 "선택하지 않는다"고 명시** |

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- 6개 후보 중 유일하게 Baseline 수준에서 "Engine 호출 책임"의
  공식 소유자로 지정된 것은 Kernel Engine Port/Adapter다. 그러나
  그 지정은 **책임의 귀속**일 뿐, **실체의 존재**를 뜻하지 않는다 —
  설계·구현은 명시적으로 Out of Scope다.
- Runtime과 Session은 둘 다 "책임 영역"으로 언급되지만, Runtime은
  Concept으로 존재하되 세부 구조가 Open(ADC-02)이고, Session은
  Concept Model에 아예 등재된 적이 없다 — 둘 다 caller로 지정된
  적은 없다.
- Development HQ는 caller 후보로 검토된 적이 없는 정도가 아니라,
  Engine Adapter/Model Routing 관련 책임에서 **명시적으로 제외**됐다.
- Dogfooding 스크립트는 실제로 caller 역할을 6번 수행했지만, 매번
  "검증"이라는 목적으로 한정됐다 — 이는 Contract가 caller-supplied
  값으로 실제 작동한다는 것을 증명했을 뿐, 그 caller가 누구여야
  하는지는 증명하지 않는다.
- ADC-0005 자신이 "별도 스크립트/함수"를 예시로만 들고 선택하지
  않았다는 사실은, 이 질문이 그 ADC의 판단 범위 밖에 있었다는
  것을 스스로 인정한 것이다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

`call_engine()`을 호출하고 그 결과를 Execution Layer의 `results`에
주입하는 caller는 어디에 위치하며, 누구의 책임인가?

| 후보 | 이 질문에 대해 지금 알 수 있는 것 |
|---|---|
| Kernel Engine Port/Adapter | 책임은 이미 귀속되어 있으나(Frozen), 실체가 없어 **지금 당장** caller 역할을 할 수 없다 — Kernel Component Architecture 설계가 선행되어야 한다 |
| Runtime | ADC-02가 Not Accepted로 남아 있는 한, Runtime을 caller로 지정할 근거가 없다 |
| Development HQ | 명시적으로 배제되어 있어 후보가 아니다 |
| Session | 정의된 개념이 아니므로 caller의 자리로 지정할 수 없다 |
| Dogfooding 스크립트 | 검증 목적을 넘어선 지정 근거가 없다 |
| 별도 스크립트/함수 | 이름조차 없는 자리 — 존재 근거 자체가 없다 |

이 RFC는 위 후보 중 어느 것이 맞는지 판단하지 않는다. 이 질문에
대한 판단은 ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- caller 위치의 실제 선택.
- Kernel Engine Gateway/Adapter의 설계·구현.
- ADC-01(Model 축과 Component 축의 대응 관계), ADC-02(Runtime 존폐)
  재조사 — 기존 Not Accepted 결론만 인용한다.
- Execution Result Consumer의 재판단 —
  `ADC-0004-execution-result-consumer.md`(execution-layer)의 Not
  Accepted 상태는 그대로 유지된다.
- Engine 연결의 변환 규칙(반환값→`results` 매핑) —
  `RFC-0005-engine-connection-boundary.md`(execution-layer) §4가
  이미 미결로 남긴 것이며, 이 RFC는 그것도 다루지 않는다.
- Kernel Component Architecture의 나머지 부분(Scheduler, Registry,
  Memory, Policy 등) — `BASELINE.md` §10 Out of Scope 그대로.
- Development HQ, Kernel, Execution Layer의 어떤 코드도 수정하지
  않는다.
- 새로운 실험.

## Non-goals

- 이 RFC는 caller의 위치를 결정하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `ADC-0005-engine-connection-boundary.md`,
  `BASELINE.md`, `development-hq/BOUNDARY.md`,
  `RFC-0005-development-hq-execution-boundary.md`,
  `ADC-0001-core-baseline.md`,
  `ADR-0002-execution-layer-module-baseline.md`, 6개 Dogfooding
  스크립트, `ARTIFACT-STANDARD-v1.md`에 이미 기록된 내용만 인용했다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 Engine Gateway/Adapter를 설계·구현하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.
- 이 RFC는 ADC-01·ADC-02·Execution Result Consumer를 재조사하지
  않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §2·§4의 6개 후보 중 현재 Evidence로 결정 가능한 것이 있는지 —
   `ADC-0008`·`ADC-0009`가 적용한 것과 같은 방식(Not Accepted 시
   억지로 선택하지 않음)으로 판단한다.
2. 결정 가능한 후보가 없다면, 어떤 선행 조건(예: Kernel Engine
   Gateway 설계 착수, ADC-02 재검토)이 채워져야 재판단 가능한지만
   기록한다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0005-engine-connection-boundary.md`,
  `BASELINE.md`, `development-hq/BOUNDARY.md`,
  `RFC-0005-development-hq-execution-boundary.md`,
  `ADC-0001-core-baseline.md`,
  `ADR-0002-execution-layer-module-baseline.md`, Dogfooding
  스크립트, `ARTIFACT-STANDARD-v1.md`에 실제로 기록된 내용만
  인용했다. 새 실험은 하지 않았다.
- caller 위치를 임의로 선택했는가 — **아니오**. §4는 6개 후보의
  현재 상태만 나열했고 어느 것도 채택하지 않았다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. 상태만 인용했다(§2).
- Execution Result Consumer를 재조사했는가 — **아니오**.
- 새 Architecture(Engine Gateway 등)를 설계했는가 — **아니오**.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(위치 선택, Gateway 설계, ADC-01/02 재조사,
  Consumer 재판단, 변환 규칙, Kernel Component Architecture 나머지,
  코드 수정, 새 실험)을 다뤘는가 — **아니오**.
