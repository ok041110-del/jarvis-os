# ADC-0004: Kernel Public Contract 채택 판단 (RFC-0004 후속)

## 목적

`docs/architecture/core/RFC-0004-kernel-public-contract.md`가 제안한
Public Contract를 **항목군별로 개별 판단**한다. 일괄 승인하지 않는다.

근거는 RFC-0004, 그리고 그 RFC가 인용한 기존 문서·코드
(`docs/01_architecture/BASELINE.md` v1.2,
`docs/architecture/core/RFC-0002`·`ADC-0002`,
`docs/architecture/core/RFC-0003`·`ADC-0003`,
`docs/architecture/core/ADC-0001-core-baseline.md`,
`docs/04_adr/ADR-0002`·`ADR-0003`,
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`·`GLOSSARY.md`,
`docs/03_adc/ADC.md`,
`development-hq/BOUNDARY.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`core/execution_layer/mvp_0001~0005/**`)에 실제로 기록된 사실로만
한정한다. 새 Evidence를 만들지 않는다.

각 판단의 Decision은 **Accept / Defer / Reject / Out of Authority**
중 하나다.

**이 ADC가 매 판단마다 확인해야 하는 3개 기준선**

| 기준선 | 내용 |
|---|---|
| B-1 | RFC-0002 §15의 미결 8개 책임(특히 1·2·3)에 답하지 않는다. |
| B-2 | `BASELINE.md` §13.6의 Defer 6건(4-Layer 포함)을 해제하지 않는다. |
| B-3 | Kernel ADC-0001의 Module 판단(Governance·Execution Layer Accept / Workflow·Memory·Event Bus Defer)을 뒤집지 않는다. |

---

## 판단 1. 계약의 범위 — Kernel 전체가 아니라 Context 영역에 한정하는가

### Evidence

- RFC-0002 §15는 8개 책임을 **하나씩 판단**하기로 명시했고, 그중
  1(Task 전달)·2(Capability 탐색)·3(Engine 호출)은 지금까지 어떤 ADC도
  판단하지 않았다.
- Context 관련 책임만 결정되었다 — Kernel ADC-0001(Execution Layer
  Accept), ADC-0002 판단 2a(Context 4개 책임을 후보로 Accept),
  ADC-0003(Model·Builder·Assembly·Output Format Accept).
- `ARCHITECTURE_GOVERNANCE.md` Freeze 원칙: Baseline은 "모든 문제가
  해결된 상태"가 아니라 "지금 결정할 것과 나중에 결정할 것이 명확히
  구분되고 추적되는 상태"다.

### 검토한 반론 (기록)

- **"범위가 한정된 계약은 계약으로서 불완전하지 않은가"** — 불완전한
  것이 맞고, 그것이 정직한 상태다. 대안은 두 가지뿐이다: (a) 미결
  책임에 답하며 전체 계약을 쓴다 → B-1 위반이자 권한 밖, (b) 미결
  영역에 침묵한 채 "Kernel 전체 계약"이라 이름 붙인다 → 읽는 사람이
  침묵을 "해당 없음"으로 오독한다. 범위를 명시적으로 좁히는 것이
  Freeze 원칙에 부합한다.
- **"Context 영역만으로 계약이 쓸모가 있는가"** — 있다. 계약의
  수신자로 지목된 둘 중 Execution Layer는 이미 Kernel Module로
  Accept되었고(Kernel ADC-0001), Development HQ는 `BOUNDARY.md`에서
  Context/Engine 호출을 Kernel 책임으로 이미 넘겨 두었다. 두 수신자
  모두 지금 Context 계약을 필요로 한다.

### Decision

**Accept**

계약의 공식 명칭에 범위를 포함한다 — **Kernel Public Contract
(Context 영역)**. Task 전달·Capability 탐색·Engine 호출 책임이 각각
판단되면 그때 계약이 확장된다.

### Decision Rationale

계약은 **결정된 만큼만** 존재할 수 있다. 미결 사안을 포함한 계약은
계약이 아니라 추측이다. 범위 한정은 RFC-0002 §15의 설계(하나씩
판단)를 그대로 따르는 것이며, B-1을 위반하지 않는 유일한 방법이다.

### Risks

계약이 조각으로 나뉘어 존재하게 된다. 향후 다른 책임이 Accept될 때마다
계약이 증분 확장되며, 그 조각들이 서로 모순되지 않는지 확인하는 비용이
누적된다. 이 ADC는 그 비용을 해소하지 않고 기록한다.

### Next Step

**ADR Required**

---

## 판단 2. Public Responsibilities (PR-1 ~ PR-4)

### Evidence (항목별)

| ID | 근거 확인 결과 |
|---|---|
| PR-1 Kernel Context 제공 | **기존 결정의 외부 관점 재진술.** Baseline §13.1이 Kernel Context를 값으로 정의했고 §13.5가 HQ/Kernel 책임을 배치했다. PR-1은 그 배치를 "외부가 무엇을 받는가"의 관점에서 다시 쓴 것이다. |
| PR-2 Context Assembly | **기존 결정의 재진술.** Baseline §13.3(A-1~A-5, O-1~O-4)이 이미 확정되어 있다. |
| PR-3 Context Validation | **기존 결정의 재진술.** Baseline §13.2가 구조 불변식만 검증하고 어긋나면 거부한다고 이미 확정했다. |
| PR-4 Context Rendering 계약 제공 | **기존 결정의 재진술 + 경계 명확화.** Baseline §13.4가 R-1·R-2·R-4·R-5를 확정했고, ADC-0003 판단 5b가 Engine별 Renderer를 Defer했다. PR-4는 그 둘의 경계("계약은 제공하되 Renderer는 제공하지 않는다")를 명시한 것이다. |

### 검토한 반론 (기록)

- **PR-1의 "제공"이 CM-4·Baseline §13.5와 충돌하는가** — 충돌하지
  않는다. RFC-0004 §2.1이 "완성된 Context를 돌려준다"와 "Context의
  내용을 마련한다"를 명시적으로 분리했고, 후자는 HQ 책임으로 남겼다.
  이 구분이 문서에 없으면 §7("Jarvis OS는 Workflow의 도메인 내용을
  책임지지 않는다")과 `BOUNDARY.md`가 동시에 위태로워지므로, 구분
  문장은 Baseline 반영 시에도 반드시 함께 가야 한다.
- **수집·병합·정렬이 Public 목록에 없는 것이 Baseline §13.2와
  모순되는가** — 모순되지 않는다. §13.2는 그 4개를 **Kernel 책임**으로
  정의했고, PR 목록은 **외부가 요청할 수 있는 것**을 정의한다. 두
  목록의 기준이 다르다. RFC-0004 §2.3이 이 구분을 기록했고, 외부가
  관찰하는 것은 그 단계가 아니라 결과(G-2·G-6)라고 명시했다. 다만
  **이 구분은 이 계약이 처음 도입하는 것**이므로 신규로 표시한다.
- **PR-4를 "Rendering"이라 부르면 Kernel이 Renderer를 제공한다고
  읽히지 않는가** — 읽힐 수 있다. 그래서 항목명을 "Context Rendering"이
  아니라 **"Context Rendering 계약 제공"**으로 고정한다.

### Decision

**Accept** (PR-1 ~ PR-4 전부. 아래 조건을 붙인다.)

1. PR-1에는 **"제공 ≠ 내용 마련"** 구분 문장을 반드시 동반한다.
2. PR-4의 명칭은 **"Context Rendering 계약 제공"**으로 고정한다 —
   "Rendering 제공"으로 축약하지 않는다.
3. Public Surface(4개)와 Kernel 책임(§13.2의 4개)은 **서로 다른
   목록**임을 명시한다. Public 목록이 Baseline §13.2를 대체하지
   않는다.

### Decision Rationale

4개 항목 중 어느 것도 새 책임을 만들지 않는다 — 전부 Baseline v1.2에
이미 확정된 것을 **외부 관점으로 다시 진술**한 것이다. 새로운 것은
"무엇이 Public Surface인가"라는 구분 하나이며, 그 구분이 §4(Hidden)와
§5(Extension Point)를 성립시킨다.

### Risks

Public Surface와 Kernel 책임이 두 개의 목록으로 존재하게 되어, 읽는
사람이 둘을 혼동하거나 한쪽만 보고 다른 쪽을 놓칠 수 있다. 조건 3이
이 위험을 문서로 막을 뿐, 구조적으로 해소하지는 않는다.

### Next Step

**ADR Required**

---

## 판단 3. Public Guarantees (G-1 ~ G-7)

### Evidence (항목별)

| ID | 근거 확인 결과 | 성격 |
|---|---|---|
| G-1 Deterministic | Baseline §13.3이 "Assembly의 입력은 (Segment 집합, Ordering Policy) 둘뿐"으로 이미 확정. 선례로 결정론 테스트 5건 통과(`test_transformation_is_deterministic` 4건, `test_rendering_is_deterministic` 1건). | 재진술 |
| G-2 Stable Ordering | Baseline §13.3 O-1~O-4가 이미 확정. | 재진술 |
| G-3 Engine Agnostic | KP-5 + CM-2 + R-5의 재진술. 선례: `test_target_engine_is_a_placeholder_not_a_real_model_name`(통과). | 재진술 |
| G-4 Implementation Agnostic | KP-1·KP-5의 재진술. `BASELINE.md` §3 "Engine Independent"·"Everything is Replaceable"은 v1.0부터 Frozen. | 재진술 |
| G-5 Immutable Inputs | Baseline §13.3 A-1·A-3 + §13.4 R-2의 재진술. 선례: 정본 불변 테스트 4건 통과. | 재진술 |
| G-6 No Silent Failure | Baseline §13.2(검증 실패·병합 충돌) + `GLOSSARY.md` 등재 원칙의 재진술. 선례: `test_unknown_state_is_rejected`(통과). | 재진술 |
| G-7 Stateless Boundary | CM-3·A-4의 재진술. **단 범위 한정이 필요하다** — 아래 반론 참조. | 재진술(범위 한정 후) |

**신규인 것은 보장의 내용이 아니라 "외부의 확인 방법"을 함께 적었다는
점이다.** RFC-0004는 G-1·G-2·G-3·G-5·G-6·G-7에 확인 방법을 명시했고,
G-4는 확인할 수 없다는 사실을 §3.2에 기록했다.

### 검토한 반론 (기록)

- **G-7이 Kernel ADC-0001의 Governance Module Accept와 충돌한다** —
  실제로 충돌할 뻔했고, RFC-0004 §3.3이 이를 발견해 해소했다. KP-6의
  문언은 *"특정 구현체의 내부 상태를 강제하지 않는다"*이며 "Kernel이
  상태를 갖지 않는다"가 아니다. 반면 Governance Module은 RFC/ADC/ADR
  문서의 등록과 상태를 다룬다(Kernel ADC-0001 Module 1의 Risks가
  "문서의 등록과 상태를 물리적으로 관리하는가는 미정"이라고 기록).
  **G-7을 Kernel 전체에 적용하면 B-3을 위반한다.** 따라서 G-7은
  판단 1이 정한 계약 범위(Context 경로)에만 적용되어야 하며, 이
  한정은 Accept의 필수 조건이다.
- **G-4는 확인할 수 없는데 보장이라 할 수 있는가** — 약한 보장이다.
  다만 KP-1·KP-5가 이미 Baseline에 Frozen으로 존재하므로, G-4를
  빼는 것이 오히려 계약과 Baseline의 불일치를 만든다. 확인 불가라는
  사실을 명시하는 조건으로 유지한다.
- **7개는 너무 많지 않은가** — 7개 전부가 기존 Baseline 진술의
  재진술이므로 새 commitment가 발생하지 않는다. 개수가 아니라
  commitment의 총량이 판단 기준이다.

### Decision

**Accept** (G-1 ~ G-7. 아래 두 조건은 필수다.)

1. **G-7의 적용 범위는 "Context 경로"로 한정한다.** Kernel 전체가
   Stateless라고 서술해서는 안 된다(B-3).
2. **G-4는 "관찰로 확인할 수 없는 보장"임을 함께 기록한다.**

### Decision Rationale

7개 보장 전부가 Baseline v1.1·v1.2에 이미 있는 진술을 외부 관점에서
재진술한 것이며, 새 commitment를 만들지 않는다. 계약으로서 새로운
가치는 **확인 방법을 함께 명시했다는 점**에 있다 — 확인할 수 없는
보장은 계약이 아니라 선언이라는 구분을 문서가 스스로 지켰고, G-4에
대해 그것을 정직하게 인정했다.

### Risks

이 보장들은 **실제 Engine 호출 없이** 선언된다. 인용된 테스트 선례는
전부 Execution Layer Builder의 것이며 Kernel의 것이 아니다(RFC-0004
§3.4가 이를 명시). 실제 Kernel 구현이 시작된 뒤 어떤 보장이 유지
불가능하다는 관찰이 나오면 재검토 대상이다.

### Next Step

**ADR Required**

---

## 판단 4. Hidden Responsibilities (H-1 ~ H-6)

### Evidence

- H-1(Ordering Policy 구현)·H-2(Builder 내부 구조)·H-4(Renderer 내부
  구현): Baseline §13.2·§13.4는 **책임과 계약만** 정의했고 구현을
  정의하지 않았다. KP-1이 그 이유를 이미 고정했다.
- H-3(Metadata 내부 표현): Baseline §13.1은 "문자열 키-값의 순서 없는
  집합"이라는 성질만 정의하고 표현 방식을 정하지 않았다.
- H-5(Identifier 파생 규칙): **ADC-0003 판단 1b에서 Defer**되었다.
- H-6(자료구조·직렬화 형식): RFC-0003 §7, Baseline §13.6 계열의 미결
  사항이다.
- 선례: `ARTIFACT-STANDARD-v1.md`는 5개 Artifact의 **Contract**를
  Baseline으로 고정하면서 각 Builder의 내부 구현은 고정하지 않았다 —
  "계약은 공개하고 구현은 숨긴다"는 패턴이 이미 실물로 존재한다.

### 검토한 반론 (기록)

- **Hidden 목록을 문서화하는 것 자체가 Component Design 아닌가** —
  아니다. Hidden 목록은 "이것들이 어떻게 생겼는지"를 기술하지 않는다.
  오직 **"외부가 여기에 의존하면 안 된다"**만 선언한다. 어떤 구조도
  설계하지 않으므로 `BASELINE.md` §10을 침범하지 않는다.
- **H-5를 Hidden에 두는 것이 Defer를 우회하는가** — 오히려 반대다.
  미결 사항을 Public에 두면 외부가 미결에 의존하게 되고, 나중에 그
  규칙이 정해질 때 계약이 깨진다. Hidden에 두는 것이 Defer 상태를
  안전하게 유지하는 방법이다(B-2 유지).
- **Hidden과 Extension Point에 같은 항목(Ordering Policy, Renderer)이
  중복 등장하는 것이 모순인가** — 모순이 아니다. RFC-0004 §4.2가
  3층 구분(교체 가능성 = Public / 계약 = Public / 구현 = Hidden)으로
  해소했다. 이 구분은 이 계약이 처음 명시하는 것이므로 신규로
  표시한다.

### Decision

**Accept** (H-1 ~ H-6)

Hidden의 **효력**을 명시적으로 함께 기록한다: *"Hidden에 의존한 코드가
Kernel 변경으로 깨지는 것은 계약 위반이 아니다."* 이 문장이 없으면
Hidden 목록은 아무것도 하지 않는 목록이 된다.

### Decision Rationale

Hidden 목록은 새 구조를 만들지 않고, 이미 미정이거나 Defer된 것들을
"외부가 의존하면 안 되는 영역"으로 묶는다. 이것은 오히려 Defer를
**보호하는** 장치다 — H-5가 그 대표적인 예다.

### Risks

Hidden/Public 경계가 처음 그어지는 것이므로, 실제 구현이 시작되면
"이건 어느 쪽인가"를 판단해야 하는 항목이 추가로 나타날 수 있다. 그
판단 기준(무엇을 Public으로 올릴 것인가)은 이 ADC가 정하지 않는다.

### Next Step

**ADR Required**

---

## 판단 5. Extension Points

성격이 다른 두 내용을 분리해 판단한다.

- **5a**: 4개 확장 지점의 **존재와 계약**(X-1 ~ X-4)
- **5b**: 확장의 **메커니즘**(등록·발견·로딩·검증)

### 5a. 확장 지점의 존재와 계약

#### Evidence

- `BASELINE.md` §3 "Everything is Replaceable"은 v1.0부터 **Frozen**
  이다. X-1~X-4는 그 원칙을 Context 영역에 적용한 것이다.
- X-1(Renderer): Baseline §13.4가 Renderer 계약을 확정했고, ADC-0003
  판단 5가 "Claude/GPT/Gemini는 동일한 Kernel Context의 서로 다른
  표현"임을 Accept했다.
- X-2(Ordering Policy): Baseline §13.2가 "Ordering Policy는 Builder의
  입력이며 Model에 박힌 분류가 아니다"를 이미 확정했다.
- X-3(Context Source): Baseline §13.1·§13.5가 Source 선언을 HQ
  책임으로 확정했다.
- X-4(Future Context Model): Baseline §13.6이 Defer 6건을 명시적으로
  기록했다.

#### 검토한 반론 (기록)

- **X-4가 "Model이 확장될 것"이라는 예고가 되어 B-2를 침식하는가** —
  침식할 수 있는 표현이다. 따라서 X-4의 의미를 **"확장이 일어날 경우
  그것이 들어올 자리"**로 한정하고, **"확장이 일어난다는 예고가
  아니다"**를 함께 기록하는 것을 Accept 조건으로 삼는다. 4-Layer는
  여전히 Defer이며, 확정될지 여부 자체가 미결이다.
- **X-3은 확장 지점이 아니라 그냥 입력 아닌가** — 그렇다. X-3은
  플러그인이 아니라 **계약의 입력 경계**다. 다른 셋과 성격이 다르다는
  점을 표에 함께 기록한다.

#### Decision

**Accept** (X-1 ~ X-4. 두 조건을 붙인다.)

1. X-4는 **"확장이 들어올 자리의 표시"**이며 확장의 예고가 아님을
   명시한다(B-2 유지).
2. X-3은 플러그인이 아니라 **입력 경계**임을 명시한다.

#### Decision Rationale

4개 전부 Baseline v1.2에 이미 있는 결정의 재배치다. 특히 X-2는
ADC-0003 판단 2가 Ordering Policy를 Model 밖으로 꺼낸 결정의 직접적
귀결이며, X-4는 그 설계가 왜 그렇게 되었는지를 계약에 드러낸다.

### 5b. 확장의 메커니즘

#### Evidence

- 이 저장소에서 확장·교체가 실제로 일어난 적이 **한 번도 없다.**
  Renderer는 0개이고(ADC-0003 판단 5b Defer), Ordering Policy도 아직
  존재하지 않으며, Context Source는 Development HQ 하나뿐이다.
- 등록·발견·로딩 메커니즘은 Component Design이며 `BASELINE.md` §10
  Out of Scope다.
- RFC-0004 §5.3은 잘못된 확장이 G-1을 깨뜨릴 수 있음을 기록하면서도,
  그것을 강제하는 메커니즘은 설계하지 않는다고 명시했다.

#### Decision

**Defer**

#### Decision Rationale

확장이 한 번도 일어나지 않은 시점에 확장 메커니즘을 설계하는 것은,
Kernel ADC-0001이 Memory Module을 Defer하고 ADC-0002가 4-Layer를
Defer한 것과 같은 상황이다. 5a(확장 지점의 존재와 계약)는 메커니즘
없이도 성립한다.

**재검토 조건**: 두 번째 Renderer 또는 두 번째 Ordering Policy가 실제로
필요해진 시점.

#### Next Step

No ADR Required

---

## 판단 6. Explicit Non-Goals (N-1 ~ N-6)

### Evidence (항목별)

| ID | 근거 확인 결과 | 미결 사안을 닫는가 |
|---|---|---|
| N-1 Runtime 관리 | `BASELINE.md` §10 Out of Scope, ADC-02(Runtime 개념의 존폐)가 Open 상태로 `docs/03_adc/ADC.md`에 등재. | **닫지 않는다** — Component 제공 여부만 말한다. |
| N-2 Scheduler 구현 | RFC-0002 §13이 "Scheduler가 필요한가"를 미결로 남김. Kernel ADC-0001 Workflow **Defer**. | **닫지 않는다** — RFC-0002 §15-1(Task 전달 책임)은 미결 유지. |
| N-3 Agent 관리 | `BASELINE.md` §7이 "Agent 구성 및 역할 결정"을 **HQ 책임**으로 이미 확정. `BOUNDARY.md`도 동일. | 닫을 미결 사안이 없다(이미 확정된 경계의 재진술). |
| N-4 Memory Service 구현 | Kernel ADC-0001 Memory Module **Defer**. G-7(Context 경로 Stateless)과 정합. | **닫지 않는다** — "Memory Module이 필요한가"는 Defer 유지. |
| N-5 내용 품질 판단 | `BASELINE.md` §7("개별 작업 결과의 품질 및 정확성"은 Jarvis OS 책임 아님), Baseline §13.2(검증은 구조만). | 닫을 미결 사안이 없다. |
| N-6 도메인 내용 선정 | Baseline §13.5, CM-4, `BOUNDARY.md`. | 닫을 미결 사안이 없다. |

### 검토한 반론 (기록)

- **Non-Goal을 선언하는 것이 B-1을 위반하는가** — RFC-0004 §6이 이
  위험을 인지하고 **전부 Component 수준으로만** 서술했다. "Scheduler라는
  Component를 제공하지 않는다"와 "Task 전달 책임이 Kernel에 속하지
  않는다"는 서로 다른 진술이며, 전자만 말한다. 이 구분은 KP-1이
  요구하는 것과 정확히 같다. 6개 항목을 개별 확인한 결과 **책임
  수준의 진술은 하나도 없었다.**
- **N-4가 Memory Defer와 충돌하는가** — 충돌하지 않는다. Defer는
  "지금 만들지 않는다"이고, N-4는 "이 계약이 그것을 제공하지
  않는다"이다. 같은 방향이다.
- **Non-Goal 목록이 나중에 Kernel이 그 책임을 갖게 될 때 걸림돌이
  되는가** — 될 수 있다. 그래서 각 항목에 "이것이 닫지 않는 질문"을
  함께 기록하는 것을 Accept 조건으로 삼는다. 그 열이 없으면 이 표는
  시간이 지나면서 "Kernel은 Task 전달을 하지 않기로 했다"로
  오독된다.

### Decision

**Accept** (N-1 ~ N-6. 아래 조건은 필수다.)

- **6개 전부를 Component 수준으로만 서술한다.**
- **"이것이 닫지 않는 질문" 열을 Baseline 반영 시에도 유지한다.**
  이 열이 B-1·B-3을 보호하는 유일한 장치다.

### Decision Rationale

Non-Goal 목록의 가치는 계약을 읽는 사람이 "Kernel에 이것을 요구하면
안 된다"를 한자리에서 알 수 있다는 데 있다. 6개 중 3개(N-3·N-5·N-6)는
이미 Frozen된 경계의 재진술이고, 나머지 3개(N-1·N-2·N-4)는 미결·Defer
사안과 맞닿아 있으나 Component 수준 서술과 "닫지 않는 질문" 열로
그 미결성을 보존한다.

### Risks

시간이 지나 조건(Component 수준 서술, "닫지 않는 질문" 열)이 편집
과정에서 소실되면, 이 표는 미결 사안을 조용히 닫는 문서가 된다. 이
위험은 문서 관행으로만 막을 수 있으며 구조적으로 해소되지 않는다.

### Next Step

**ADR Required**

---

## 판단 7. 계약의 변경 규칙 (RFC-0004 §7)

### Evidence

- `ARCHITECTURE_GOVERNANCE.md`: "이 절차(RFC → ADC → ADR → Baseline
  Update)를 우회한 변경은 Baseline에 반영되지 않는다." 이 원칙은
  설계·문서화 단계에도 동일하게 적용된다고 같은 문서가 명시했다.
- 계약의 Public 항목이 Baseline에 들어가면, 그 변경은 자동으로 위
  절차의 적용을 받는다 — 새 규칙이 아니라 기존 규칙의 귀결이다.
- Hidden 항목은 Baseline에 내용이 기록되지 않으므로 절차 대상이
  아니다.
- Contract Versioning: 계약이 아직 한 번도 변경된 적이 없다.

### Decision

- **변경 규칙(Public = 절차 필요 / Hidden = 자유)**: **Accept**
- **Contract Versioning 체계**: **Defer**

### Decision Rationale

변경 규칙은 `ARCHITECTURE_GOVERNANCE.md`를 이 계약에 적용한 결과일
뿐 새 규칙이 아니며, Hidden 목록(판단 4)의 효력을 완성시킨다.

Versioning 체계는 다르다 — 계약이 변경된 적이 없으므로 어떤 호환성
문제가 실제로 발생하는지 관찰된 바가 없다. `ARCHITECTURE_GOVERNANCE.md`
의 ADC 채택 기준 2개 중 어느 것도 만족하지 않는다. 현재는
`BASELINE.md`의 문서 Version이 유일한 추적 수단이며 그것으로 충분하다.

### Next Step

**ADR Required** (변경 규칙 부분만)

---

## 판단 8. Baseline 반영 범위

### Evidence

- `docs/01_architecture/BASELINE.md` §Version: v1.2, Status Active,
  Architecture State **Frozen**.
- §10 Out of Scope: Kernel Architecture, Component Design. v1.1·v1.2가
  각각 이를 유지한다고 다시 명시했다.
- RFC-0004는 Kernel Architecture를 설계하지 않는다 — Extension Point의
  메커니즘(판단 5b Defer), API(§8 미결), 자료구조·직렬화(H-6)를 전부
  미결로 남겼고, 어떤 Component도 정의하지 않았다.
- ADR-0002·ADR-0003 선례: Frozen 상태의 Baseline을 절차를 거쳐
  v1.0 → v1.1 → v1.2로 갱신했다.

### Decision

**Accept** (반영 범위를 한정하는 조건부)

Baseline에 반영할 것:

1. 계약의 범위 한정(판단 1) — Context 영역에 한정된 계약임을 명시
2. Public Responsibilities PR-1 ~ PR-4(판단 2, 조건 3건 포함)
3. Public Guarantees G-1 ~ G-7(판단 3, 조건 2건 포함)
4. Hidden Responsibilities H-1 ~ H-6과 그 효력(판단 4)
5. Extension Points X-1 ~ X-4(판단 5a, 조건 2건 포함)
6. Explicit Non-Goals N-1 ~ N-6과 "닫지 않는 질문" 열(판단 6)
7. 계약 변경 규칙(판단 7 전반부)

Baseline에 반영하지 **않을** 것:

- Extension Point의 메커니즘 — 판단 5b Defer
- Contract Versioning 체계 — 판단 7 Defer
- Kernel API — RFC-0004 §8, 다음 단계
- RFC-0002 §15의 미결 3개 책임에 대한 어떤 판단도 — B-1
- `BASELINE.md` §13.6의 Defer 6건 — B-2, 그대로 유지
- Kernel Architecture 및 Component Design — §10 Out of Scope 유지

### Decision Rationale

이 계약이 Baseline에 추가하는 것은 "Kernel이 외부에 무엇을
보장하는가"이며, "Kernel이 어떻게 생겼는가"가 아니다. §10이 막는 것은
후자다.

계약을 Baseline에 두는 것에는 별도의 이유가 있다 — **Public 항목의
변경이 절차를 거치도록 만드는 것이 계약의 실질적 효력**이며(판단 7),
Baseline 밖에 있는 계약은 그 효력을 갖지 못한다.

### Risks

- Baseline 버전 갱신(v1.2 → v1.3)이 필요하다. 절 번호 정책은 ADR에
  위임한다.
- 이번 판단이 다시 6건의 "ADR Required"를 발생시킨다. ADC-0002·
  ADC-0003이 기록한 절차 부채는 이 ADC가 해소하지 않는다.
- 계약이 Baseline에 들어가지만 그것을 구현하는 Kernel은 아직 존재하지
  않는다. "보장은 있으나 보장하는 주체가 없는" 상태가 API 설계 단계까지
  지속된다.

### Next Step

**ADR Required**

---

## 종합

| 판단 항목 | Decision | Next Step |
|---|---|---|
| 1. 계약 범위(Context 영역 한정) | **Accept** | ADR Required |
| 2. Public Responsibilities PR-1~PR-4 | **Accept** (조건 3건) | ADR Required |
| 3. Public Guarantees G-1~G-7 | **Accept** (조건 2건) | ADR Required |
| 4. Hidden Responsibilities H-1~H-6 | **Accept** (효력 문장 필수) | ADR Required |
| 5a. Extension Points X-1~X-4 | **Accept** (조건 2건) | ADR Required |
| 5b. 확장 메커니즘 | **Defer** | No ADR Required |
| 6. Explicit Non-Goals N-1~N-6 | **Accept** (조건 2건) | ADR Required |
| 7. 계약 변경 규칙 / Contract Versioning | **Accept** / **Defer** | ADR Required (전반부) |
| 8. Baseline 반영 범위 | **Accept** (범위 한정) | ADR Required |

9개 판단 중 6개 Accept(전부 조건부), 1개 부분 Accept·부분 Defer,
2개 Defer다. 일괄 승인하지 않았다.

Reject나 Out of Authority로 분류된 항목은 없다. 다만 **판단 3에서
G-7의 적용 범위를 축소**했고(Kernel 전체 → Context 경로), **판단 5a에서
X-4의 의미를 축소**했다(확장의 예고 → 확장이 들어올 자리의 표시).
두 축소는 각각 B-3과 B-2를 보호하기 위한 것이다.

### 기준선 3건 최종 확인

| 기준선 | 확인 결과 |
|---|---|
| B-1 (RFC-0002 §15 미결 8개 책임을 닫지 않는다) | **Pass.** 판단 1이 계약 범위를 Context로 한정했고, 판단 6이 Non-Goal 6건을 개별 확인해 책임 수준 진술이 하나도 없음을 확인했다. |
| B-2 (`BASELINE.md` §13.6 Defer 6건을 해제하지 않는다) | **Pass.** 판단 4가 H-5(Identifier 파생 규칙)를 Defer 상태로 Hidden에 두었고, 판단 5a가 X-4의 의미를 "자리 표시"로 축소했다. |
| B-3 (Kernel ADC-0001 Module 판단을 뒤집지 않는다) | **Pass.** 판단 3이 G-7의 범위를 한정해 Governance Module Accept와의 충돌을 제거했고, 판단 6이 N-4와 Memory Defer가 같은 방향임을 확인했다. |

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0004와 그것이 인용한 기존
  문서·소스에 기록된 사실만 사용했다. Kernel ADC-0001 Module 1의
  Risks 문장과 KP-6의 문언은 원문에서 직접 확인했다. 새 실험을 하지
  않았다.
- 일괄 승인했는가 — **아니오**. 9개 판단으로 분리했고 2개가 Defer,
  Accept 6개는 전부 조건부다.
- 미결 사안에 답했는가 — **아니오**. 기준선 3건(B-1·B-2·B-3)을 각
  판단에서 개별 확인하고 종합에서 다시 확인했다.
- 기존 결정과의 충돌을 발견했는가 — **1건 발견하고 해소했다.**
  G-7 vs Kernel ADC-0001 Governance Module Accept. 판단 3에서 적용
  범위 한정을 Accept 조건으로 삼았다.
- "필요할 것 같다"는 이유로 Accept했는가 — **아니오**. 판단 5b(확장
  메커니즘)와 판단 7 후반부(Versioning)가 바로 그 이유로 Defer되었다.
- 반론을 검토했는가 — **Pass**. 판단 1에 2건, 2에 3건, 3에 3건, 4에
  3건, 5a에 2건, 6에 3건을 기록했다. 그중 2건이 실제로 Accept 범위
  축소로 이어졌다(G-7, X-4).
- Architecture Drift가 없는가 — **없음**. 새 Layer/Component를 만들지
  않았다. 판단 8이 §10 Out of Scope를 그대로 유지하도록 범위를
  한정했다.
- Kernel Leak가 없는가 — **없음**. Scheduler/Registry/Runtime/Memory/
  Event Bus 어느 것도 설계하지 않았고, 판단 6이 그것들을 Component
  수준 Non-Goal로만 다뤘다.
- API를 설계했는가 — **아니오**. 판단 8이 API를 반영 대상에서
  명시적으로 제외했다.
- Development HQ·Execution Layer를 수정 대상으로 삼았는가 —
  **아니오**.
- ADR을 작성했는가 — **아니오**. 이 ADC는 ADR이 필요하다는 판정만
  내렸다.
