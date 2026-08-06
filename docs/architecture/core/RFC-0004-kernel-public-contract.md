# RFC-0004: Kernel Public Contract — 무엇을 보장하고, 무엇을 숨기고, 무엇을 하지 않는가

**Status**: Proposed (검토 대상, 결정 아님)
**Version**: Draft
**Author**: Claude Code (Kernel Public Contract 요청 → RFC 전환)
**상위 근거**: `docs/01_architecture/BASELINE.md` v1.2 §11(Kernel 정의)·
§12(KP-1~KP-6)·§13(Kernel Context Model)
**관련 문서**: `docs/architecture/core/RFC-0002`·`ADC-0002`(Kernel Definition),
`docs/architecture/core/RFC-0003`·`ADC-0003`(Kernel Context Model),
`docs/architecture/core/ADC-0001-core-baseline.md`(Kernel Module 5건 판단),
`docs/04_adr/ADR-0002`·`ADR-0003`,
`development-hq/BOUNDARY.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`

> 이 RFC는 API를 정의하지 않는다. 함수 시그니처, 자료형, 프로토콜,
> 직렬화 형식을 정의하지 않는다.
> 이 RFC는 **Kernel이 외부에 무엇을 보장하는가**를 정의한다.
> API 설계는 이 계약이 확정된 뒤의 별도 단계다.

---

## 0. 이 RFC의 위치

이 프로젝트는 일관되게 **책임 → 계약 → 구현** 순서를 따라 왔다.

| 단계 | 문서 | 결과 |
|---|---|---|
| Kernel이란 무엇인가(책임) | RFC-0002 / ADC-0002 / ADR-0002 | Baseline §11·§12 (v1.1) |
| Kernel은 무엇을 관리하는가(대상) | RFC-0003 / ADC-0003 / ADR-0003 | Baseline §13 (v1.2) |
| **Kernel은 외부에 무엇을 보장하는가(계약)** | **본 RFC** | — |
| 그 보장을 어떤 API로 제공하는가(구현) | (다음 단계) | — |

API를 먼저 정의하면 계약이 API의 형태에서 역산된다. 그것은 KP-1
("Kernel은 구현 객체가 아니라 책임 경계다")의 인과 방향을 뒤집는다.
RFC-0002 §12.1이 Prompt Cache에 대해 고정한 것과 같은 방향 규칙이
여기에도 적용된다 — **계약이 위에 있고 API가 아래에 있다.**

### 0.1 이 RFC가 지켜야 하는 제약

| 제약 | 출처 |
|---|---|
| Kernel Architecture·Component Design을 하지 않는다 | `BASELINE.md` §10 Out of Scope (v1.2에서 유지) |
| 책임으로 정의하고 구현으로 정의하지 않는다 | KP-1 |
| ADC-0003이 Defer한 6건을 확정하지 않는다 | `BASELINE.md` §13.6 |
| RFC-0002 §15의 미결 8개 책임을 닫지 않는다 | RFC-0002 §15 |
| Kernel ADC-0001이 Defer한 3개 Module(Workflow/Memory/Event Bus)의 판단을 뒤집지 않는다 | `ADC-0001-core-baseline.md` |
| Development HQ·Execution Layer의 문서·코드를 수정하지 않는다 | ADR-0001·ADR-0002·ADR-0003 선례 |

---

## 1. 계약의 범위 — 지금 무엇에 대한 계약을 쓸 수 있는가

**이 RFC가 정의하는 것은 Kernel 전체의 계약이 아니라, 지금까지 결정된
영역(Kernel Context)에 대한 계약이다.**

이유는 다음과 같다. RFC-0002 §15는 8개 책임이 Kernel에 속하는지를
**하나씩 판단**하기로 했고, 그중 결정된 것은 Context 관련 4개뿐이다.

| RFC-0002 §15의 책임 | 현재 상태 |
|---|---|
| 1. Task 전달 책임 | **미결** |
| 2. Capability 탐색 책임 | **미결** |
| 3. Engine 호출 책임 | **미결** |
| 4. Context 전달 책임 | Kernel ADC-0001에서 Execution Layer Module Accept, Baseline §13에서 Model 확정 |
| 5. Stable Prefix 책임 | 후보(ADC-0002 판단 2a), 형태는 Defer(ADC-0003 판단 4) |
| 6. Context Boundary 책임 | 후보, 형태는 Defer(ADC-0003 판단 4) |
| 7. Context Assembly 책임 | Baseline §13.3에서 확정 |
| 8. Context Ordering 책임 | Baseline §13.2·§13.3에서 확정 |

1~3이 미결인 상태에서 "Kernel 전체의 Public Contract"를 쓰면, 그
계약은 미결 사안에 답하거나(권한 밖) 침묵하거나(불완전한 계약) 둘 중
하나가 된다.

따라서 이 RFC는 **Kernel Public Contract (Context 영역)** 를 제안한다.
Task 전달·Capability 탐색·Engine 호출 책임이 각각 판단되면, 그때 이
계약이 확장된다. 계약은 **결정된 만큼만** 존재한다.

### 1.1 계약의 수신자

이 계약은 다음을 대상으로 한다.

| 수신자 | 근거 |
|---|---|
| Development HQ | `BOUNDARY.md`(Frozen)가 Context/Engine 호출을 Kernel 책임으로 이미 명시 |
| Execution Layer | Kernel ADC-0001에서 **Kernel Module로 Accept**됨 |
| 미래의 HQ (Personal HQ, Research HQ 등) | `BASELINE.md` §3 "Composable HQ", §4 "Reference Architecture" |

**미래 HQ에 대한 주의**: `BASELINE.md` §4가 요구하는 Reference
Architecture 성질 때문에 이 계약은 Development HQ 전용이어서는 안
된다. 그러나 그런 HQ는 아직 존재하지 않으므로, 이 계약이 그들에게도
충분한지는 **검증된 바 없다**(RFC-0002 §5가 같은 한계를 이미
기록했다).

---

## 2. Public Responsibilities — Kernel이 외부에 제공하는 책임

**Public Responsibility의 정의**: 외부가 Kernel에 요구할 수 있고,
Kernel이 응답할 의무가 있는 것.

| ID | 책임 | 내용 | 근거 |
|---|---|---|---|
| PR-1 | **Kernel Context 제공** | 외부가 제공한 Segment와 Ordering Policy로부터 조립된 **Kernel Context를 값으로 돌려준다.** | Baseline §13.1 |
| PR-2 | **Context Assembly** | A-1~A-5 불변식과 O-1~O-4 순서 요구를 만족하는 조립을 수행한다. | Baseline §13.3 |
| PR-3 | **Context Validation** | 구조 불변식을 검증하고, 위반을 **드러낸다.** | Baseline §13.2 |
| PR-4 | **Context Rendering 계약 제공** | Kernel Context를 표현으로 변환하는 **계약(R-1·R-2·R-4·R-5)을 보장한다.** | Baseline §13.4 |

### 2.1 PR-1의 "제공"이 뜻하지 않는 것 — 반드시 구분해야 한다

"Context 제공"은 **"Kernel이 완성된 Context를 돌려준다"**는 뜻이지,
**"Kernel이 Context의 내용을 마련한다"**는 뜻이 아니다.

Baseline §13.5가 이미 고정했다 — 무엇이 Context에 들어가야 하는지는
HQ가 정한다. CM-4는 Kernel이 Content와 Source를 해석하지 않는다고
명시한다. 이 구분이 무너지면 §7("Jarvis OS는 Workflow의 도메인 내용을
책임지지 않는다")과 `BOUNDARY.md`가 동시에 무너진다.

```
HQ ──── Segment(내용) + Source 선언 + Ordering Policy 선택 ───▶ Kernel
                                                                  │
HQ ◀─────────────── Kernel Context (조립된 값) ───────────────────┘
```

### 2.2 PR-4의 "계약 제공"이 뜻하지 않는 것

Kernel은 **Renderer 계약을 보장**하지만, **특정 Engine용 Renderer를
제공하지 않는다.** Claude/GPT/Gemini Renderer는 ADC-0003 판단 5b에서
Defer되었다. 이 둘의 차이가 이 RFC의 핵심 중 하나다.

| 구분 | 누구의 것인가 |
|---|---|
| "Renderer는 순수하고 결정론적이며 Context를 변경하지 않는다"(R-1·R-2·R-4·R-5) | **Kernel의 보장** — Public |
| "Claude에게는 이런 형태로 보낸다" | **Renderer의 구현** — Extension Point(X-1), Hidden(H-4) |

### 2.3 병합·정렬은 왜 Public Responsibility 목록에 없는가

Baseline §13.2는 Kernel 책임을 4개(수집·검증·병합·정렬)로 정의했다.
그중 병합과 정렬이 이 목록에 별도 항목으로 없는 것은 누락이 아니다.

**외부는 병합과 정렬을 요청하지 않는다.** 외부는 Context를 요청하고
(PR-1), 병합·정렬은 그 요청을 만족시키는 **내부 단계**다. 외부가
관찰하는 것은 그 단계 자체가 아니라 **결과에 대한 보장**이다 —
G-2(Stable Ordering)와 G-6(No Silent Failure, 병합 충돌 시 오류).

즉 병합·정렬은 **Kernel 책임이지만 Public Surface가 아니다.** 이
구분이 §4(Hidden Responsibilities)의 근거가 된다.

수집(Collect)도 같은 이유로 PR-1에 흡수된다 — 다만 수집은 "어떤
Source를 볼지 호출자가 정한다"(Baseline §13.2)는 제약 때문에 외부와
맞닿아 있으며, 그 접점이 X-3(Context Source)이다.

---

## 3. Public Guarantees — Kernel이 항상 보장하는 성질

**Guarantee의 정의**: 외부가 **의존해도 되는** 성질. Kernel의 내부가
어떻게 바뀌더라도 유지되어야 하며, 깨지면 계약 위반이다.

각 보장에는 **외부가 그것을 어떻게 확인할 수 있는지**를 함께 적는다 —
확인할 수 없는 보장은 계약이 아니라 선언에 불과하다.

| ID | 보장 | 내용 | 근거 | 외부의 확인 방법 |
|---|---|---|---|---|
| G-1 | **Deterministic** | 같은 (Segment 집합, Ordering Policy) → 같은 Kernel Context. 호출 시각·호출 순서·프로세스 상태·환경 변수는 결과에 영향을 주지 않는다. | KP-2, Baseline §13.3 | 같은 입력으로 두 번 호출해 결과를 비교 |
| G-2 | **Stable Ordering** | 순서는 전순서이며, 선언된 Order Key에서 나온다. 동률은 Identifier로 해소된다. | KP-3, O-1~O-4 | 입력 Segment의 제시 순서를 섞어도 결과 순서가 동일한지 확인 |
| G-3 | **Engine Agnostic** | Kernel Context에는 특정 Engine에만 의미가 있는 요소가 존재하지 않는다. | KP-5, CM-2, R-5 | Kernel Context에서 role·token 수·cache key 등이 발견되지 않는지 확인 |
| G-4 | **Implementation Agnostic** | Kernel은 호출자의 Runtime·언어·저장소·실행 방식을 강제하지 않는다. | KP-1, KP-5 | — (구조적 보장. §7 참조) |
| G-5 | **Immutable Inputs** | 외부가 넘긴 Segment는 변경되지 않는다. 반환된 Kernel Context도 변경되지 않는다. | A-1, A-3, R-2 | 호출 전후 입력값을 비교 |
| G-6 | **No Silent Failure** | 구조 불변식 위반과 병합 충돌은 조용히 넘어가지 않는다. | Baseline §13.2, `GLOSSARY.md` | 규칙을 어긴 입력이 거부되는지 확인 |
| G-7 | **Stateless Boundary** | **Context 경로에 한하여**, Kernel은 호출 간 상태를 갖지 않는다. 시계·난수를 읽지 않으며 Identifier·시각을 생성하지 않는다. | CM-3, A-4, KP-6 | 호출 순서를 바꿔도 각 결과가 동일한지 확인 |

### 3.1 G-3과 G-4는 새 약속이 아니다

두 항목은 KP-5("특정 모델이나 특정 Runtime에 종속되지 않는다") 하나를
**외부에서 관찰 가능한 두 방향으로 나눈 것**이다.

- G-3은 **Kernel이 내보내는 것**에 대한 제약 — Context 안에 Engine
  개념이 없다.
- G-4는 **Kernel이 요구하는 것**에 대한 제약 — 호출자에게 특정
  구현을 강요하지 않는다.

`BASELINE.md` §3의 "Engine Independent"와 "Everything is Replaceable"은
v1.0부터 Frozen이며, 두 보장은 그 재진술이다.

### 3.2 G-4의 확인 방법이 비어 있는 것에 대하여

G-1·G-2·G-3·G-5·G-6·G-7은 외부에서 관찰로 확인할 수 있다. **G-4는
그렇지 않다** — "강요하지 않는다"는 부정 명제이며, 반례가 나타나야
위반이 드러난다.

이 비대칭을 숨기지 않고 기록한다. G-4는 다른 6개와 성격이 다르며,
검증이 아니라 **검토(Review)로만 지킬 수 있는 보장**이다.

### 3.3 G-7은 KP-6보다 강하다 — 그래서 범위를 한정한다

KP-6의 문언은 *"Kernel은 책임을 정의하지만, 특정 구현체의 내부 상태를
강제하지 않는다"*이다. 이것은 **"Kernel이 상태를 갖지 않는다"와 같은
말이 아니다.**

실제로 Kernel ADC-0001은 **Governance Module을 Accept**했고, 그 Module은
RFC/ADC/ADR 문서의 등록과 상태를 다룬다(같은 문서 Risks: "그 실행
주체가 문서의 등록과 상태를 물리적으로 관리하는가는 여전히 미정"). 만약
G-7을 Kernel 전체에 적용하면 이미 Accept된 Module과 충돌한다.

따라서 **G-7은 §1이 정한 계약 범위(Context 경로)에만 적용된다.** 그
범위 안에서는 근거가 명확하다 — CM-3(Kernel은 Identifier·시각을 생성하지
않는다), A-4(조립은 시계·난수·외부 I/O를 읽지 않는다), 그리고
Execution Layer 5개 Builder 전부에서 확인된 caller-supplied identity
관행이다.

### 3.4 이 보장들은 아직 실제 Engine 호출 없이 선언된다

G-1·G-2·G-5·G-7은 Execution Layer 42개 테스트 안에 이미 같은 형태로
존재한다(결정론 5건, 정본 불변 4건, 시계·난수 부재 5건 —
`ARTIFACT-STANDARD-v1.md`). G-3은 MVP-0003의
`test_target_engine_is_a_placeholder_not_a_real_model_name`이 같은
성질을 검증한다. G-6은 MVP-0005의 `test_unknown_state_is_rejected`가
같은 형태다.

**그러나 그 테스트들은 Kernel의 것이 아니라 Execution Layer
Builder들의 것이다.** 같은 성질이 Kernel 수준에서도 유지될 수 있는지는
아직 관찰되지 않았다. 이 RFC는 그 사실을 근거로 삼지 않고, **선례로만**
인용한다.

---

## 4. Hidden Responsibilities — Kernel 내부에 남아야 하는 것

**Hidden의 정의**: Kernel이 수행하지만 **외부가 의존해서는 안 되는**
것. Hidden에 의존한 코드가 Kernel 변경으로 깨지는 것은 **계약 위반이
아니다.** 이것이 Hidden 목록의 실질적 효력이다.

| ID | 항목 | 왜 숨기는가 |
|---|---|---|
| H-1 | **Ordering Policy의 구현** | 어떤 Policy가 어떤 Order Key를 만드는지는 Policy의 내부다. 외부가 보장받는 것은 G-2(순서가 안정적이라는 사실)이지 그 계산 방법이 아니다. |
| H-2 | **Builder 내부 구조** | 수집·검증·병합·정렬이 몇 개 단계로 나뉘고 어떤 순서로 실행되는지. 외부가 보장받는 것은 PR-1의 결과와 G-1~G-7이다(§2.3). |
| H-3 | **Metadata의 내부 표현 방식** | Metadata를 어떤 자료구조로 들고 있는지. Baseline §13.1은 "문자열 키-값의 순서 없는 집합"이라는 성질만 정의했고 표현을 정하지 않았다. |
| H-4 | **Renderer 내부 구현** | 각 Renderer가 어떤 틀로 표현을 만드는지. 외부가 보장받는 것은 R-1·R-2·R-4·R-5다(PR-4). |
| H-5 | **Context Identifier 파생 규칙** | ADC-0003 판단 1b에서 **Defer**되었다. 미결 사항을 Public에 두면 외부가 미결에 의존하게 된다. |
| H-6 | **Segment의 자료구조·직렬화 형식** | RFC-0003 §7에서 미결로 남았다. |

### 4.1 H-3은 "저장"이 아니라 "표현"이다

Metadata를 **영속화**하는 것은 Hidden이 아니라 **Non-Goal**이다
(N-4). Memory Module은 Kernel ADC-0001에서 Defer되었고, Kernel은
호출 간 상태를 갖지 않는다(G-7). H-3이 가리키는 것은 **한 번의 조립
안에서의 내부 표현**뿐이다.

### 4.2 Hidden과 Extension Point는 모순되지 않는다

Ordering Policy와 Renderer는 §4(Hidden)와 §5(Extension Point) 양쪽에
나온다. 모순이 아니라 **층이 다르다.**

| 층 | 공개 여부 | 예 |
|---|---|---|
| 그 지점이 **교체 가능하다**는 사실과 교체 지점의 존재 | **Public** (X-1, X-2) | "Renderer는 교체할 수 있다" |
| 그 지점이 **무엇을 지켜야 하는가**(계약) | **Public** (R-1·R-2·R-4·R-5) | "Renderer는 결정론적이어야 한다" |
| 그 지점의 **구현 내용** | **Hidden** (H-1, H-4) | "기본 Renderer가 절을 어떻게 배치하는가" |

즉 **계약은 공개하고 구현은 숨긴다.** 이것은 이 저장소에 이미 있는
패턴이다 — `ARTIFACT-STANDARD-v1.md`는 5개 Artifact의 **Contract**를
고정하면서 각 Builder의 내부 구현은 고정하지 않았다.

---

## 5. Extension Points — 외부에서 교체하거나 확장 가능한 지점

**Extension Point의 정의**: Kernel이 **교체 가능하다고 선언한 지점**.

> **이것은 플러그인 메커니즘이 아니다.** 등록·발견·로딩·버전 협상
> 방식은 Component Design이며 `BASELINE.md` §10 Out of Scope다. 이
> RFC가 정의하는 것은 **"여기가 교체 지점이다"라는 계약상의 선언**
> 뿐이며, 그것을 어떻게 꽂는지는 정의하지 않는다.

| ID | 확장 지점 | 무엇을 교체하는가 | 지켜야 할 계약 | 근거 |
|---|---|---|---|---|
| X-1 | **Renderer** | Kernel Context를 어떤 표현으로 내보낼 것인가(Claude/GPT/Gemini/그 외) | R-1·R-2·R-4·R-5 | Baseline §13.4 |
| X-2 | **Ordering Policy** | Segment의 Order Key를 어떻게 정할 것인가 | O-1~O-4, G-1 | Baseline §13.2 |
| X-3 | **Context Source** | 무엇이 Context에 들어가는가 | CM-4(Kernel은 해석하지 않는다) | Baseline §13.1·§13.5 |
| X-4 | **Future Context Model** | Context 구성 요소의 확장 | CM-1~CM-4 | Baseline §13.6 |

### 5.1 X-4가 이 계약의 핵심 장치다

`BASELINE.md` §13.6은 6건을 Defer 상태로 남겼고, 그중 가장 큰 것이
4-Layer Context Model이다. X-4는 **그 Defer들이 나중에 들어올 자리를
계약 안에 미리 표시해 둔 것**이다.

4-Layer가 훗날 확정되면 그것은 **하나의 Ordering Policy(X-2)** 로
들어온다 — Model(§13.1)도, 이 계약의 Public 항목도 바뀌지 않는다.
이것이 ADC-0003 판단 2가 Ordering Policy를 Model 밖으로 꺼낸 이유의
귀결이다.

### 5.2 Extension Point는 "Everything is Replaceable"의 구체화다

`BASELINE.md` §3은 v1.0부터 "Everything is Replaceable — 모든 Engine,
Agent, Workflow는 교체 가능해야 한다"를 Frozen으로 갖고 있다. X-1~X-4는
그 원칙을 Context 영역에 적용한 것이며, 새 원칙이 아니다.

### 5.3 확장이 계약을 깨뜨릴 수 있는 지점 (정직하게 기록한다)

Extension Point는 위험을 동반한다. **잘못 만든 Renderer나 Ordering
Policy는 G-1(Deterministic)을 깨뜨릴 수 있다** — 예를 들어 시각을 읽는
Ordering Policy는 같은 입력에 다른 순서를 만든다.

이 RFC는 그 위험을 **계약으로만** 다룬다: 확장은 표에 명시된 계약을
지켜야 하며, 지키지 않은 확장은 Kernel의 보장 밖이다. **그것을
강제하는 메커니즘(검증기, 샌드박스 등)은 설계하지 않는다** — 그것이
필요한지는 관찰된 바 없다.

---

## 6. Explicit Non-Goals — Kernel이 하지 않는 것

**중요한 구분을 먼저 명시한다.**

> Non-Goal은 **"Kernel Public Contract가 그 Component를 제공하지
> 않는다"**는 뜻이지, **"그 책임이 Kernel에 속하지 않는다"**는 뜻이
> 아니다.
>
> KP-1이 정확히 이 구분을 요구한다 — Kernel은 책임을 갖고, Component는
> 그 책임을 구현하는 방법이다. 따라서 아래 목록은 **Component 수준의
> 선언**이며, RFC-0002 §15가 미결로 남긴 책임 질문에 답하지 않는다.

| ID | Non-Goal | Kernel이 제공하지 않는 것 | 이것이 닫지 **않는** 질문 | 근거 |
|---|---|---|---|---|
| N-1 | **Runtime 관리** | Workflow 실행, Task 인스턴스 관리 | "Runtime 개념이 존치하는가"(ADC-02, Open) | `BASELINE.md` §10, ADC-02 |
| N-2 | **Scheduler 구현** | Task 배분·순서 결정 Component | "Task 전달 책임이 Kernel에 속하는가"(RFC-0002 §15-1, 미결) | RFC-0002 §13, Kernel ADC-0001 Workflow Defer |
| N-3 | **Agent 관리** | Agent의 생성·구성·실행 | 없음 — Agent 구성은 `BASELINE.md` §7·`BOUNDARY.md`가 이미 **HQ 책임**으로 확정했다 | `BASELINE.md` §7 |
| N-4 | **Memory Service 구현** | Context의 영속화·복원 | "Memory Module이 필요한가"(Kernel ADC-0001, **Defer**) | Kernel ADC-0001 |
| N-5 | **내용 품질 판단** | Context 내용의 사실성·관련성·품질 평가 | 없음 — `BASELINE.md` §7이 이미 확정 | `BASELINE.md` §7, §13.2 |
| N-6 | **도메인 내용 선정** | 무엇이 Context에 들어가야 하는지 결정 | 없음 — Baseline §13.5가 이미 HQ 책임으로 확정 | Baseline §13.5, CM-4 |

### 6.1 N-1·N-2·N-4가 특히 조심스러운 이유

이 세 항목은 **아직 미결이거나 Defer된 사안과 맞닿아 있다.** 만약 이
RFC가 "Kernel은 Task 전달을 하지 않는다"라고 썼다면, 그것은 RFC-0002
§15가 하나씩 판단하기로 한 질문에 미리 답하는 것이 된다 — 권한 밖이다.

그래서 위 표는 전부 **Component 수준**으로만 서술되어 있다.
"Scheduler라는 Component를 제공하지 않는다"와 "Task 전달 책임이
Kernel에 없다"는 서로 다른 진술이며, 이 RFC는 앞의 것만 말한다.

### 6.2 N-3·N-5·N-6은 이미 확정된 경계의 재진술이다

세 항목은 `BASELINE.md` §7과 `BOUNDARY.md`(둘 다 Frozen)가 이미
고정한 경계이며, 새 결정이 아니다. Contract에 다시 적는 이유는 계약
문서 하나만 읽는 사람이 이 경계를 놓치지 않게 하기 위함이다.

---

## 7. 계약의 변경 규칙

계약은 **무엇이 바뀌면 외부가 깨지는가**를 말할 수 있어야 의미가
있다.

| 대상 | 변경 시 필요한 절차 |
|---|---|
| Public Responsibility(PR-*), Guarantee(G-*), Extension Point의 존재(X-*)와 그 계약 | **RFC → ADC → ADR → Baseline** (`ARCHITECTURE_GOVERNANCE.md`) |
| Hidden(H-*)의 내용 | 절차 없이 변경 가능. 외부는 여기에 의존하지 않기로 되어 있다(§4). |

**Contract Versioning 체계(번호 규칙, 호환성 표기, Deprecation 기간
등)는 이 RFC가 정하지 않는다.** 계약이 실제로 한 번이라도 변경된 적이
없으므로, 지금 버전 체계를 만드는 것은 관찰되지 않은 필요에 대한
설계다. 현재는 `BASELINE.md`의 문서 Version(v1.x)이 유일한 추적
수단이다.

---

## 8. 아직 결정하지 않는 것

- Kernel API — 함수·자료형·프로토콜·직렬화 형식(다음 단계).
- Task 전달 / Capability 탐색 / Engine 호출 책임이 Kernel에 속하는지
  (RFC-0002 §15, 미결 유지).
- Extension Point의 **메커니즘**(등록·발견·로딩·검증).
- Contract Versioning 체계.
- 계약 위반을 강제·탐지하는 방법(§5.3).
- `BASELINE.md` §13.6의 Defer 6건 — 그대로 유지한다.
- 이 계약이 미래 HQ에도 충분한지(§1.1, 검증 불가).

---

## Out of Scope

- 구현. 이 RFC는 코드를 만들지 않고 어떤 코드도 수정하지 않는다.
- API 설계 — 계약이 확정된 뒤의 별도 단계다.
- Kernel Architecture 및 Component Design — `BASELINE.md` §10 그대로.
- Development HQ·Execution Layer의 문서·코드 수정.
- Scheduler / Runtime / Registry / Memory / Event Bus / Prompt
  Assembly Engine의 설계 또는 필요 여부 판단.
- Prompt Engineering, 모델별 캐싱 메커니즘.

## Non-goals

- 이 RFC는 API를 정의하지 않는다.
- 이 RFC는 Kernel 전체의 계약을 정의하지 않는다 — Context 영역에
  한정한다(§1).
- 이 RFC는 RFC-0002 §15의 미결 8개 책임에 답하지 않는다.
- 이 RFC는 `BASELINE.md` §13.6의 Defer 6건을 해제하지 않는다.
- 이 RFC는 Kernel ADC-0001의 Module 판단(2 Accept / 3 Defer)을
  뒤집지 않는다.
- 이 RFC는 Baseline을 변경하지 않는다 — 반영 여부는 후속 ADC·ADR의
  몫이다.

## Self Review

- API를 정의했는가 — **아니오**. 함수·자료형·프로토콜·직렬화 형식이
  이 문서에 없다. §8이 그것을 다음 단계로 명시했다.
- 미결 사안에 답했는가 — **아니오**. §6이 Non-Goal을 전부 Component
  수준으로 서술하고, "이것이 닫지 않는 질문" 열을 두어 RFC-0002 §15의
  미결 3건과 ADC-02·Kernel ADC-0001의 Defer를 명시적으로 열어 두었다.
- Defer된 것을 확정했는가 — **아니오**. §5.1이 4-Layer의 자리를
  X-4/X-2로 표시했을 뿐 확정하지 않았고, H-5가 Identifier 파생 규칙을
  Defer 상태 그대로 Hidden에 두었다.
- Component를 만들었는가 — **아니오**. §5 서두가 Extension Point를
  "계약상의 선언이며 플러그인 메커니즘이 아님"으로 명시했고, §8이
  메커니즘을 미결로 남겼다.
- 계약이 검증 가능한가 — **부분적으로만. 기록했다.** G-1~G-3·G-5~G-7은
  확인 방법을 표에 적었고, G-4는 관찰로 확인할 수 없다는 사실을
  §3.2에 정직하게 기록했다.
- Evidence를 과장했는가 — **아니오**. §3.4가 "42개 테스트는 Kernel의
  것이 아니라 Execution Layer Builder들의 것이며, 선례로만 인용한다"고
  명시했다.
- 기존 결정과 충돌하는가 — **한 건 있었고 해소했다.** G-7을 Kernel
  전체에 적용하면 Kernel ADC-0001이 Accept한 Governance Module(문서
  상태를 다룬다)과 충돌한다. §3.3에서 이를 확인하고 G-7의 적용 범위를
  Context 경로로 한정했다.
- Hidden과 Extension Point가 모순되는가 — **아니오**. §4.2가 층
  구분(교체 가능성·계약은 공개, 구현은 비공개)으로 해소했다.
- 확장의 위험을 숨겼는가 — **아니오**. §5.3이 잘못된 확장이 G-1을
  깨뜨릴 수 있음을 기록하고, 그 강제 메커니즘은 설계하지 않는다고
  명시했다.
- Development HQ·Execution Layer를 수정했는가 — **아니오**.
- Baseline을 변경했는가 — **아니오**.
