# VALIDATION-0001: Kernel Reference Architecture 타당성 검증

**문서 성격**: Review 문서. **Governance 문서가 아니다.**
**검토 대상**: `docs/01_architecture/BASELINE.md` v1.4 §15 (및 그 전제인
§10·§11·§12·§13·§14)
**근거 문서**: `RFC-0005`·`ADC-0005`·`ADR-0005`,
`GOVERNANCE-REVIEW-0001-post-adc-0001.md`,
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`docs/03_adc/ADC.md`, `docs/02_rfc/README.md`, `docs/04_adr/README.md`,
`core/execution_layer/**`, `development-hq/mvp/project_intelligence.py`

이 문서는 Architecture Decision을 포함하지 않는다. Baseline을 변경하지
않는다. 새 Architecture·Component·Layer를 설계하지 않는다. Scheduler·
Registry·Runtime·Execution Layer·API를 설계하지 않는다. **발견 사항을
기록하고 판정만 한다.**

## 이 검증의 한계 (먼저 밝힌다)

검증 대상 문서(RFC-0005·ADC-0005·ADR-0005 및 §15)를 작성한 것과 이
검증을 수행하는 것이 **동일 주체**다. 자기 검토는 독립 검토를 대체하지
못한다. 이 보고서는 **문서 간 정합성과 사실 대조로 확인 가능한
것**에 한정하며, 설계 판단의 타당성 자체에 대해서는 독립성이 없다.

그 한계를 보완하기 위해, 아래 모든 발견 사항은 **문서의 특정 문장 또는
소스의 특정 위치를 근거로** 제시한다.

---

# 1. 검토 항목별 판정

| # | 항목 | 판정 |
|---|---|---|
| 1 | Kernel 정의 (Responsibility로 일관되는가) | **조건부 Pass** (V-3) |
| 2 | Boundary (Reference → Component → Implementation) | **조건부 Pass** (V-4) |
| 3 | Responsibility (신규 추가 없음) | **Pass** |
| 4 | Model (신규 요소 없음) | **Pass** — 단 접합부 결손 (V-1) |
| 5 | Relationship (Component 미암시) | **조건부 Pass** (V-3, V-4) |
| 6 | Implementation Neutrality (3형태) | **조건부 Pass** (V-2) |
| 7 | Architecture Drift | **Pass — Drift 없음** |
| 8 | Reference Completeness | **조건부 충분** (V-1 해소 필요) |
| 9 | Governance | **절차 Pass / 산출물 색인 Fail** (V-7, V-8) |

---

## 항목 1. Kernel 정의 — Responsibility로 일관되는가

### 확인한 것

§15의 6단계는 전부 **동사형**(Collect / Merge / Validate / Order /
Assemble / Render)으로 기술되었다. §15.3은 명칭을 "Component
Relationship"이 아니라 "Responsibility Relationship"으로 두고 그 이유
(KP-1, §11)를 본문에 기록했다. §15.5 IN-1이 *"단계는 책임이며 객체·
클래스·모듈·서비스가 아니다"*를 명시했다.

### 발견 — V-3 (Minor): 명사형 표기가 앞선 절들에 남아 있다

§15는 동사형으로 일관되나, **그 전제가 되는 절들은 명사형을 쓴다.**

| 위치 | 표현 |
|---|---|
| `BASELINE.md:255` | `### 13.2 Context Builder 책임` |
| `BASELINE.md:267` | "Ordering Policy는 **Builder의 입력**이며" |
| `BASELINE.md:458` | `| H-2 | Builder 내부 구조 |` |
| `BASELINE.md` 전체 | "Renderer" 24회 |

"Builder"와 "Renderer"는 **행위자 형태의 명사**다. §15가 §13.2를
참조할 때(`BASELINE.md:614`, "H-2(Builder 내부 구조, Hidden)에
속한다") 동사형 체계와 명사형 체계가 한 문장 안에서 만난다.

**판정에 미치는 영향**: 이것이 Kernel을 Component로 정의한다는 뜻은
아니다 — §13.2는 명확히 "책임"이라는 단어를 제목에 달고 있고, §14.4
H-2는 그것을 Hidden으로 두어 구현을 규정하지 않는다. 그러나 **표기
체계가 두 개**라는 사실은 향후 Component RFC에서 "Builder는
Component인가 책임인가"라는 불필요한 논쟁을 만들 수 있다.

**이 문서는 그 해소 방법을 제안하지 않는다** — 용어 변경은 Baseline
변경이며 RFC 절차의 대상이다.

### 판정: 조건부 Pass

§15 자체는 일관된다. 저장소 전체 수준에서는 표기 체계가 이원화되어
있다.

---

## 항목 2. Boundary — Reference가 Component를 암시하지 않는가

### 확인한 것

- §15 서두: *"이 절은 새 책임·새 Model 요소·새 Component를 만들지
  않는다"*, *"이 절은 API가 아니다"*.
- §10에 "Kernel Component Architecture"가 그대로 남아 있고, §15
  서두와 §15.6 말미가 각각 이를 재확인한다.
- §15 본문에서 Scheduler·Registry·Event Bus·Engine Gateway·Memory는
  **한 번도 등장하지 않는다**(전문 검색으로 확인). "Runtime"은 2회
  등장하나 둘 다 *"정의하지 않는다"* 문맥이다(`BASELINE.md:557`,
  `:747`).

### 발견 — V-4 (Minor): 배선도의 번호가 이산 단위를 암시한다

§15.1의 배선도는 단계에 **①~⑥ 번호와 박스**를 부여한다. 이는 다음과
긴장 관계에 있다.

- IN-1: *"하나의 단계가 여러 구현 단위에 나뉘거나 여러 단계가 하나에
  합쳐져도 계약은 유지된다."*
- ADC-0005 판단 2b: 배선도의 ②→③ 배치는 *"가능한 배치 하나의
  예시"*다.

번호가 붙은 6개의 박스는 시각적으로 **"6개의 순차 단위"**를 읽게
만든다. §15.1 본문이 이를 문장으로 방어하고 있으나(*"검증은 ⑤Assemble
이전에 완료되어야 한다"* 하나만 요구), **그림과 문장이 서로 다른
강도를 갖는다.**

### 발견 — Extension Point는 "교체 단위"의 존재를 함의한다 (판정 유지)

X-1(Renderer 교체), X-2(Ordering Policy 교체)는 **무언가 식별 가능한
교체 단위가 존재함**을 논리적으로 함의한다. 교체할 수 없는 것은
Extension Point가 아니기 때문이다.

다만 이는 Drift로 보지 않는다. 근거:

- §14.5가 *"플러그인 메커니즘이 아니다. 등록·발견·로딩·버전 협상
  방식은 Component Design이며 §10 Out of Scope다"*로 이미 방어한다.
- 그 단위가 **무엇인지**(객체·함수·모듈·프로세스)는 IN-1·IN-2·IN-4가
  전부 열어 두었다.
- `BASELINE.md` §3 "Everything is Replaceable"은 v1.0부터 Frozen이며,
  교체 가능성 선언 자체는 새 개념이 아니다.

**즉 "교체 지점이 있다"는 함의는 존재하고, "그것이 Component다"라는
함의는 존재하지 않는다.**

### 판정: 조건부 Pass

Reference → Component → Implementation 경계는 유지된다. 배선도의
시각적 표현이 문장보다 강한 것이 유일한 약점이다.

---

## 항목 3. Responsibility — 신규 추가가 없는가

### 확인한 것 (전수 대조)

| §15의 단계 | Baseline 상의 출처 | 신규? |
|---|---|---|
| ① Collect | §13.2 수집 | 아니오 |
| ② Merge | §13.2 병합 | 아니오 |
| ③ Validate | §13.2 검증 | 아니오 |
| ④ Order | §13.2 정렬 | 아니오 |
| ⑤ Assemble | §13.3 | 아니오 |
| ⑥ Render | §13.4 | 아니오 |

§15가 추가한 진술은 **5건**이며, 전부 도출 경로가 명시되어 있다.

| 진술 | 도출 근거 | 검증 결과 |
|---|---|---|
| "검증은 Assemble 이전 완료" | §13.2 병합 규칙(같은 Identifier + 다른 Content = 오류는 병합 시도 후에만 판정 가능) + G-6 + A-2 | **도출 성립** |
| RR-1 역방향 의존 금지 | §13.4(역방향 미정의) + G-1 | **도출 성립** |
| RR-2 단계 건너뛰기 금지 | G-6 + A-2 | **도출 성립** |
| RR-3 공유 가변 상태 금지 | G-1 + G-7 | **도출 성립** |
| RR-4 Render의 정렬 관여 금지 | O-4 | **도출 성립** |

RR-4는 ADC-0003 판단 5가 제외한 R-3과 겹치는 영역이 있으나,
`core/execution_layer/mvp_0002/prompt_specification_builder.py`가
Kernel Context가 아니라 Execution Request를 입력으로 받는다는 사실을
소스에서 직접 확인했다 — **Kernel Renderer가 아니므로 RR-4의 적용
대상이 아니며**, §15.3의 인용 블록이 이를 명시한다.

### 판정: Pass

새 책임은 없다. 추가된 5개 진술은 전부 기존 결정에서 도출된다.

---

## 항목 4. Model — 신규 요소가 추가되지 않았는가

### 확인한 것

§15.2의 인용 블록이 *"아래 이름들은 §13.1의 Model에 추가되는 새 요소가
아니다"*를 표 앞에 명시하고, *"6개 중 실제 Model 요소는 Kernel Context
하나뿐"*임을 기록한다. §13.1의 5개 요소는 그대로다.

### 발견 — V-1 (**Major**): Kernel Context의 Identifier·Metadata 입력 경로가 배선도에 없다

**이것이 이번 검증에서 발견한 가장 중요한 결함이다.**

사실 관계는 다음과 같다.

1. **§13.1**: Context는 `Context Identifier` + `Context Metadata` +
   `Context Segment [ordered]`로 구성된다.
2. **CM-3**: *"Kernel은 Identifier와 시각을 스스로 생성하지 않는다.
   호출자가 주입하거나 결정론적으로 파생한다."*
3. **H-5**: Identifier 파생 규칙은 **Defer**이며 Hidden이다
   (ADC-0003 판단 1b).
4. **§15.1 경계 배치표**: Kernel 경계 밖에서 들어오는 것은 **3개**다 —
   Context Source의 선언, Segment의 Content, Ordering Policy의 선택.
5. **§15.2**: ⑤Assemble의 출력이 "Kernel Context"라고만 기록한다.

**§15 전체에서 "Identifier"가 등장하는 5곳은 전부 Segment 수준이다**
(전문 검색으로 확인: 병합 규칙 2회, tie-break 2회, 충돌 판정 1회).
**Context 수준의 Identifier와 Metadata가 어디서 오는지는 §15
어디에도 없다.**

즉 배선도는 다음 질문에 답하지 못한다.

> ⑤Assemble이 Kernel Context를 만들 때, 그 Context의 Identifier와
> Metadata는 어디서 오는가?

가능한 답은 셋이며, **어느 것도 Baseline에 기록되어 있지 않다.**

| 후보 | 문제 |
|---|---|
| 호출자가 주입 | §15.1 경계표의 외부 입력 3개에 없다 — 표가 불완전해진다 |
| Segment들로부터 파생 | H-5(파생 규칙)가 Defer이므로 지금은 규정 불가 |
| Kernel이 생성 | **CM-3 위반** |

**이것은 §15의 오류라기보다 §13.1과 §15.1의 접합부 결손이다.** §13.1이
Context에 Identifier를 부여했고, §15.1이 경계를 그렸는데, 두 결정이
만나는 지점이 비어 있다.

**영향**: Component RFC는 시작하자마자 이 질문에 부딪힌다 — "Assemble
책임을 구현하는 것은 Context Identifier를 어디서 받는가"에 답하지
않고는 그 책임의 입력을 정의할 수 없다.

### 판정: Pass (신규 요소 없음) — 단 V-1로 인해 항목 8이 제약된다

Model 요소는 5개 그대로이며 §15가 확장하지 않았다. 이 판정은 유지된다.
**결손은 "추가"가 아니라 "누락"이며, 항목 8(Completeness)에서 다룬다.**

---

## 항목 5. Relationship — Relationship만 정의했는가

### 확인한 것

§15.3의 관계표 6행은 전부 **단계 간 의존 성격**(순차 의존 / 부분 순서
/ 입력 의존 / 생산 / 읽기 전용 / 비의존)만 기술한다. 어떤 행도 "무엇이
무엇을 소유한다", "무엇이 무엇을 호출한다"를 말하지 않는다.

RR-1~RR-4는 전부 **금지 형태**이며, 구현 방법을 규정하지 않고 결과만
금지한다.

### 발견

V-3(명사형 표기)과 V-4(번호 부여)가 이 항목에도 동일하게 적용된다.
추가 발견 없음.

### 판정: 조건부 Pass

---

## 항목 6. Implementation Neutrality — 3형태에서 성립하는가

**이 항목은 판정을 위해 실제 대조가 필요하므로, 세 형태를 개별
점검했다.**

### Function Pipeline

| 보장 | 성립 여부 |
|---|---|
| G-1 Deterministic | 성립. 순수 함수 합성은 정의상 결정론적 |
| G-5 Immutable Inputs | 성립 |
| G-7 Stateless | 성립 |
| RR-3 공유 가변 상태 금지 | 자연 성립 |

**결과: 성립.**

### Service Chain

| 보장 | 성립 여부 |
|---|---|
| G-1 | 각 단계가 호출 간 상태를 남기지 않는 한 성립 |
| G-7 | **명시적으로 지켜야 함** — 서비스는 상태를 갖기 쉽다 |
| RR-3 | 명시적으로 지켜야 함 |

**결과: 성립. 단 G-7·RR-3이 자동으로 보장되지 않는다** — §15.5가 이를
이미 기록했다.

### Message Passing — 여기서 V-2를 발견했다

| 보장 | 성립 여부 |
|---|---|
| G-2 Stable Ordering | 성립. O-3이 "순서는 Order Key에서 나오며 수집 순서·삽입 순서에서 나오지 않는다"를 이미 요구 |
| G-1 Deterministic | **조건부 성립** — 아래 참조 |

### 발견 — V-2 (**Major**): Merge의 순서 무관성이 진술되지 않았다

IN-3은 *"동기/비동기, 순차/병렬 어느 실행 모델도 전제하지 않는다"*고
명시한다. 병렬 수집·병렬 병합이 허용된다는 뜻이다.

그런데 **병렬 실행에서 G-1(같은 입력 → 같은 결과)이 성립하려면
②Merge가 순서와 무관해야 한다** — 즉 어떤 순서로 합치든 같은 결과가
나와야 한다(교환·결합 법칙).

§13.2의 병합 규칙을 대조하면 이 성질은 **실제로 만족된다.**

| 규칙 | 순서 의존성 |
|---|---|
| 같은 Identifier + 같은 Content → 중복 제거 | 어느 쪽을 남겨도 동일 → **순서 무관** |
| 같은 Identifier + 다른 Content → 오류 | 어느 순서로 만나도 오류 → **순서 무관** |

**즉 성질은 성립한다. 그러나 그 성질이 Baseline 어디에도 진술되어 있지
않다.** G-1과 IN-3의 양립은 이 미진술 성질에 **의존**하고 있다.

또한 §14.3이 G-2의 확인 방법으로 제시한 *"입력 Segment의 제시 순서를
섞어도 결과 순서가 동일한지 확인"*은 **이 성질을 전제로 해야만
의미가 있다** — 제시 순서를 섞었을 때 Merge 결과가 달라지면 그
확인은 G-2가 아니라 Merge를 시험하는 것이 된다.

**영향**: 구현자가 순서 의존적인 Merge를 만들어도 현재 Baseline
문언만으로는 위반을 지적할 근거가 약하다.

### 판정: 조건부 Pass

3형태 전부에서 성립한다. **단 Message Passing에서의 성립은 미진술
성질(Merge의 순서 무관성)에 의존한다.**

---

## 항목 7. Architecture Drift

### 전수 확인 결과

| 검사 대상 | 결과 |
|---|---|
| 새 Layer | **없음** |
| 새 Component | **없음** — Scheduler·Registry·Event Bus·Engine Gateway·Memory는 §15에 0회 등장 |
| 새 Concept | **없음** — §15.2의 6개 이름은 논리적 상태이며 Model 요소가 아님을 표 앞에서 명시 |
| Runtime 암시 | **없음** — "Runtime" 2회 등장, 둘 다 "정의하지 않는다" 문맥 |
| Scheduler 암시 | **없음** — 단계 간 순서는 데이터 의존이며 스케줄링이 아님 |
| Registry 암시 | **없음** — §15.4가 "확장 메커니즘(등록·발견·로딩)은 Defer"를 명시 |
| 새 책임 | **없음** (항목 3에서 전수 대조) |
| 새 Model 요소 | **없음** (항목 4) |
| Defer 해제 | **없음** — §15.4가 4-Layer Defer 유지를 명시 |

**§10 범위 한정은 Drift가 아니다** — RFC → ADC → ADR 절차를 거친
명시적 결정이며, `BASELINE.md` §10과 §Version 절 양쪽에 변경 사실과
근거가 기록되어 있다. Drift는 절차 없이 경계가 이동하는 것을 뜻하며,
이 경우는 그 반대다.

### 판정: **Architecture Drift 없음**

---

## 항목 8. Reference Completeness

### 판정 기준

"Kernel Reference만으로 Component RFC를 시작할 수 있는가" =
**Component RFC가 다룰 대상(책임), 그 책임의 입력·출력, 지켜야 할
제약이 전부 정의되어 있는가.**

### 충분한 것

| 필요 정보 | 위치 |
|---|---|
| 무엇을 관리하는가 | §13.1 |
| 어떤 책임이 있는가 | §13.2·§13.3·§13.4, §15.1 |
| 책임 간 순서·의존 | §15.1·§15.3 |
| 외부 계약 | §14.2·§14.3 |
| 숨겨야 할 것 | §14.4 |
| 확장 지점의 위치 | §15.4 |
| 구현 중립성 판정 기준 | §15.5 |
| 무엇이 미결인가 | §13.6·§14.7·§15.6 |

**Component RFC의 출발점으로서 이 정도면 대부분 충분하다.**

### 부족한 것

| ID | 결손 | 심각도 | 왜 Component RFC를 막는가 |
|---|---|---|---|
| **V-1** | Kernel Context의 Identifier·Metadata 입력 경로 | **Major** | Assemble 책임의 **입력 정의가 불완전**하다. 첫 Component RFC가 즉시 부딪힌다 |
| **V-2** | Merge의 순서 무관성 미진술 | **Major** | 병렬 구현의 적합성을 판정할 근거가 약하다 |
| **V-5** | 실패 시 흐름 의미론 | Minor | 검증 실패 시 흐름이 어디서 멈추고 부분 결과를 어떻게 하는지 미정의. G-6은 "드러난다"고만 함 |
| **V-6** | 빈 Context(Segment 0개)의 유효성 | Minor | §13.1은 "유한한 열"이라 했고 0도 유한하나, 허용 여부가 §13.2 검증 규칙에 없음 |

V-5·V-6은 Component RFC 진행 중에 병행 해소해도 무방하다. **V-1은
그렇지 않다** — 책임의 입력이 정의되지 않으면 그 책임을 구현할 후보를
논할 수 없다.

### 판정: **조건부 충분**

---

## 항목 9. Governance

### 절차 준수 — Pass

`ARCHITECTURE_GOVERNANCE.md`의 `RFC → ADC → ADR → Baseline Update`
순서가 지켜졌음을 확인했다.

| 단계 | 산출물 | 확인 |
|---|---|---|
| RFC | `RFC-0005` | §0에서 §10 충돌을 **문서 첫 절**에 제기 |
| ADC | `ADC-0005` | 판단 1을 Gating Judgment로 분리, 10개 개별 판단 |
| ADR | `ADR-0005` | 조건 14건의 반영 위치 지정, 변경 범위 한정 |
| Baseline | v1.4 | §10·§15·§Version 절에 변경 사실과 근거 기록 |

**§10 변경 처리 방식이 특히 적절했다.** ADC-0005 판단 1이 *"이것은
해석이 아니라 범위 변경"*임을 명시하고 ADR을 통한 문언 변경으로
처리했다 — 해석으로 우회했다면 절차 위반이었을 것이다.

`GOVERNANCE-REVIEW-0001` §5의 근거 6개가 **전부 유효함을 인정한 위에서**
범위를 좁힌 점, 그리고 *"이번 Accept를 다음 단계의 선례로 삼지
않는다"*를 §10 본문에 남긴 점도 확인했다.

### 발견 — V-7 (**Major, Governance**): 절차 산출물의 색인이 낡았다

절차는 지켜졌으나, **그 절차가 만든 산출물을 추적하는 색인이 갱신되지
않았다.**

| 파일 | 기록된 내용 | 실제 |
|---|---|---|
| `docs/04_adr/README.md` | *"**작성된 ADR 없음.** … 첫 ADR 작성을 고려한다"* | **ADR-0001 ~ ADR-0005, 5건 존재** |
| `docs/02_rfc/README.md` | 등록된 RFC 표에 **RFC-0001 1건**만 | `docs/02_rfc/`에 5건 + `docs/architecture/core/`에 5건 = **10건 존재** |

`ARCHITECTURE_GOVERNANCE.md`의 Single Source of Truth 원칙에 비추어,
**색인이 실제를 반영하지 않는 상태**는 절차 자체의 신뢰성을 떨어뜨린다.
특히 `04_adr/README.md`의 "작성된 ADR 없음"은 **명백한 사실 오류**다.

### 발견 — V-8 (Minor, Governance): ADC 네임스페이스가 3개다

| 위치 | 내용 |
|---|---|
| `docs/03_adc/ADC.md` | Jarvis OS 수준 Open Decision 12건. *"모든 Open Decision의 Single Source of Truth"*라고 선언 |
| `docs/governance/adc/` | Development HQ 수준 ADC-0001~0004 |
| `docs/architecture/core/` | Kernel 수준 ADC-0001~0005 |

세 곳이 같은 "ADC" 이름과 번호 체계를 쓴다(예: "ADC-0001"이 세
의미를 가진다). ADR-0003 §5·ADR-0004 §6·ADR-0005 §7이 각각 "ADC.md를
갱신하지 않는다"고 판단했고 그 판단 자체는 타당하나, **결과적으로
`ADC.md`의 "모든 Open Decision"이라는 선언과 실제 상태가 어긋난다.**

### 발견 — V-9 (기록): 미작성 ADR 2건이 5개 ADR을 지나며 누적되었다

Kernel ADC-0001이 "ADR Required"로 판정한 2건(Governance Module,
Execution Layer Module)의 ADR이 여전히 없다.
`GOVERNANCE-REVIEW-0001` §1이 이를 지적한 이후 ADR-0002·0003·0004·0005가
전부 *"이 ADR이 해소하지 않는다"*로만 기록했다.

**이 검증도 그것을 해소하지 않는다** — 사실로만 기록한다.

### 판정: 절차 **Pass** / 산출물 색인 **Fail**

---

# 2. Architecture Drift 여부

## **Drift 없음.**

새 Layer·Component·Concept·Runtime·Scheduler·Registry 어느 것도
도입되지 않았음을 전수 확인했다(항목 7).

§10의 범위 한정은 절차를 거친 명시적 결정이며, 변경 사실·근거·한계가
`BASELINE.md` §10 본문, §15 서두, §Version 절 세 곳에 기록되어 있다.
**절차 없이 경계가 이동한 사례는 발견되지 않았다.**

다만 **경계 조정의 선례가 생겼다는 사실**은 Drift 위험으로 계속
추적되어야 한다. ADC-0005 판단 1 조건 3(*"다음 단계의 선례로 삼지
않는다"*)이 유일한 방어 장치이며, 이는 문서 관행으로만 유지된다.

---

# 3. Reference Completeness 평가

## **조건부 충분 — Major 결손 2건**

| ID | 결손 | 심각도 | 조치 |
|---|---|---|---|
| **V-1** | Kernel Context의 Identifier·Metadata 입력 경로 미정의 | **Major** | **Component RFC 이전에 해소 필요** |
| **V-2** | Merge의 순서 무관성 미진술 | **Major** | Component RFC와 병행 가능하나 함께 처리 권장 |
| V-5 | 실패 시 흐름 의미론 미정의 | Minor | 병행 가능 |
| V-6 | 빈 Context의 유효성 미정의 | Minor | 병행 가능 |
| V-3 | 명사형/동사형 표기 이원화 | Minor | 병행 가능 |
| V-4 | 배선도 번호가 이산 단위를 암시 | Minor | 병행 가능 |
| V-7 | 절차 산출물 색인 낡음 | **Major (Governance)** | **즉시 처리 가능** — Architecture 결정이 아님 |
| V-8 | ADC 네임스페이스 3개 | Minor (Governance) | 별도 판단 필요 |

---

# 4. Component RFC 착수 준비 여부

## **조건부 준비됨.**

**착수 가능한 근거**

- 다룰 책임이 전부 정의되어 있다(§13.2·§13.3·§13.4).
- 책임 간 순서·의존·금지가 정의되어 있다(§15.1·§15.3).
- 지켜야 할 계약이 정의되어 있다(§14.2·§14.3).
- 무엇을 노출하면 안 되는지 정의되어 있다(§14.4).
- 판정 기준이 있다 — 어떤 Component 제안이든 PR-1~PR-4를 제공하는가,
  G-1~G-7을 지키는가, H-1~H-6을 노출하지 않는가, IN-1~IN-5와 3형태
  시험을 통과하는가로 검토할 수 있다.

**착수 전 해소해야 할 것**

- **V-1 (Major)**: Kernel Context의 Identifier·Metadata가 어디서
  오는지. 이것이 정의되지 않으면 **Assemble 책임의 입력을 정의할 수
  없고**, 따라서 그 책임을 구현할 Component 후보를 논할 수 없다.

**해소 방법은 이 문서가 제안하지 않는다.** 후보가 셋이고(호출자 주입 /
Segment로부터 파생 / 그 외) 그중 하나는 H-5(Defer)와 맞물려 있으므로,
**별도 RFC의 판단 대상**이다.

**함께 다루기를 권고하는 것**

- **V-2 (Major)**: 같은 RFC에서 함께 다루면 비용이 낮다. 둘 다
  §13(Model·Builder·Assembly) 영역의 미진술 사항이다.

---

# 5. 추가 RFC가 필요한 Open Question

이 문서는 RFC를 만들지 않는다. **질문만 나열한다.**

## Q-1 (Major). Kernel Context의 Identifier와 Metadata는 어디서 오는가

- §13.1은 Context가 Identifier와 Metadata를 갖는다고 정의했다.
- CM-3은 Kernel이 Identifier를 스스로 생성하지 않는다고 제약했다.
- §15.1의 경계표에는 그 입력 경로가 없다.
- H-5(파생 규칙)는 Defer 상태다.

**이 질문은 H-5의 Defer를 해제하지 않고도 답할 수 있는가?** — 즉
"어디서 오는가"(경로)와 "어떻게 만들어지는가"(규칙)를 분리할 수
있는가가 이 RFC의 첫 판단이 될 것이다.

## Q-2 (Major). Merge는 순서와 무관한가 — 그 성질을 진술해야 하는가

- IN-3이 병렬 실행을 허용한다.
- 병렬에서 G-1이 성립하려면 Merge가 순서 무관이어야 한다.
- §13.2의 병합 규칙 2개는 실제로 순서 무관이다.
- **그러나 그 성질이 어디에도 진술되어 있지 않다.**

## Q-3 (Minor). 검증 실패 시 흐름은 어떻게 되는가

G-6은 "드러난다"고만 한다. 흐름이 어디서 멈추는지, 부분 결과가
어떻게 되는지, 여러 위반이 동시에 발견되면 전부 보고되는지 하나만
보고되는지가 정의되지 않았다. **오류의 전달 방식(예외·결과값·이벤트)은
구현이지만, "흐름이 어디서 멈추는가"는 Reference 수준 질문이다.**

## Q-4 (Minor). 빈 Kernel Context는 유효한가

§13.1은 "유한한 Segment 열"이라 했고 0개도 유한하다. §13.2의 검증
규칙에 최소 개수 요구가 없다. 허용된다면 ⑥Render는 무엇을
출력하는가.

## Q-5 (Minor). ①Collect와 X-3(입력 경계)의 경계는 어디인가

- §15.1: Context Source의 **선언**은 경계 **밖**, Segment의 **Content**도
  **밖에서 들어온다**.
- 그렇다면 경계 **안**의 ①Collect가 수행하는 일은 무엇인가 — "받는
  것"과 어떻게 구분되는가?

§13.2가 Collect를 Kernel 책임으로 정의했으므로 이 구분은 Component
RFC가 반드시 답해야 한다.

## Q-6 (Minor). ⑥Render는 Kernel이 소유하는가, 호출자가 제공하는가

§15.1이 Render를 **"경계 위"**로 배치했다 — 계약은 안(PR-4), 구현은
교체 가능(X-1)·내부는 Hidden(H-4). Component RFC는 이 배치를 유지한
채 진행할 수 있는가, 아니면 소유권을 확정해야 하는가.

## Q-7 (Governance). 절차 산출물의 색인을 어떻게 유지할 것인가

V-7이 드러낸 것은 단일 오류가 아니라 **색인 갱신이 절차에 포함되어
있지 않다**는 구조적 사실이다. `ARCHITECTURE_GOVERNANCE.md`의 절차
(`RFC → ADC → ADR → Baseline Update`)에 색인 갱신 단계가 없다.

**이것은 Architecture 결정이 아니라 문서 관리 문제이므로 RFC 없이
처리 가능하다.** 다만 절차 자체에 단계를 추가하는 것은 Governance
변경이다.

## Q-8 (Governance). ADC 네임스페이스 3개를 어떻게 정리할 것인가

`ADC.md`의 "모든 Open Decision의 Single Source of Truth" 선언과
실제(3개 네임스페이스, 번호 중복)가 어긋난다.

---

# Review Self Check

- 새 Architecture를 설계했는가 — **아니오**. 발견 사항의 해소 방법을
  제안하지 않았다(V-1·V-2 모두 "이 문서가 제안하지 않는다"로 명시).
- 새 Component·Layer·Concept를 만들었는가 — **아니오**.
- Scheduler·Registry·Runtime·Execution Layer·API를 설계했는가 —
  **아니오**. Execution Layer는 RR-4 적용 대상 여부 확인을 위해
  **사실 조회**만 했다.
- Baseline을 변경했는가 — **아니오**. 이 문서는 Review이며 Decision을
  포함하지 않는다.
- Defer를 해제했는가 — **아니오**. Q-1이 H-5의 Defer와 맞물린다는
  사실을 지적했을 뿐, 해제하지 않았다.
- 판정에 근거를 붙였는가 — **Pass**. 모든 발견 사항에 문서의 특정
  절·행 번호 또는 소스 위치를 제시했다.
- 자기 검토의 한계를 밝혔는가 — **Pass**. 문서 서두에 명시했다.
- 통과시키기 위해 기준을 낮췄는가 — **아니오**. 9개 항목 중 5개가
  조건부 Pass이고 1개(Governance 산출물 색인)는 **Fail**이며, Major
  결손 3건(V-1·V-2·V-7)을 기록했다.
