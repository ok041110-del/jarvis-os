# RFC-0007: Kernel Context Identity — Identity는 Reference의 문제인가, Component의 문제인가

**Status**: Resolved — `ADC-0007.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Version**: Draft
**Author**: Claude Code (VALIDATION-0001 V-1 / ADC-0006 OQ-1·OQ-8 후속)
**상위 근거**: `docs/01_architecture/BASELINE.md` v1.4 §13·§14·§15
**직접 계기**: `ADC-0006` 판단 8 — *"V-1은 이 ADC로 닫히지 않는다.
OQ-1(Identifier 출처)이 전제이며 H-5 Defer와 맞물린다"*

> **이 RFC는 Identifier를 정의하지 않는다.**
> 생성 방식·알고리즘·UUID·Hash·Composite Key·Metadata 구조를
> 정의하지 않는다.
>
> **이 RFC는 Identity도 정의하지 않는다.**
>
> 이 RFC의 목적은 하나다 — **Identity가 Reference Layer에서 논의되어야
> 하는 문제인지, Component Layer의 문제인지 Boundary를 확인하는 것.**

---

## 0. 범위와 제약

### 0.1 이 RFC가 다시 결정하지 않는 것

| 항목 | 이미 결정된 곳 |
|---|---|
| Ownership과 Responsibility의 구분 | ADC-0006 판단 1 (**Accept**) |
| Ownership 어휘의 Baseline 등재 | ADC-0006 판단 5 (**Defer**) — **이 RFC는 그 Defer를 존중한다**(§0.2) |
| Ownership 3층의 명명·구조화 | ADC-0006 판단 6b (**Defer**) |
| §11 문언 변경 | ADC-0006 판단 7 (**Reject**) |

### 0.2 ADC-0006 판단 5의 Defer를 어떻게 존중하는가

ADC-0006은 "Ownership"을 **Baseline 어휘로 등재하지 않기로**
Defer했다. 따라서 이 RFC는 **Ownership을 어휘로 사용하지 않는다.**

대신 ADC-0006 판단 **6a**가 *"기존 결정의 재진술로서"* Accept한
결론만, **기존 어휘(책임 / 값 / 형식 / 경계 / 호출자)로** 인용한다.

| ADC-0006 판단 6a가 Accept한 결론 | 이 RFC가 쓰는 표현 |
|---|---|
| 내용은 HQ의 것 | 무엇이 Context에 들어가는지는 HQ가 정한다(§13.5) |
| 형식은 Kernel의 것 | **무엇이 유효한 Kernel Context인지는 Kernel이 판정한다**(§13.2·§13.3) |
| 인스턴스는 호출자의 것 | 만들어진 값은 호출자가 들고 있다(§15.2) |

### 0.3 다루지 않는 것

Identifier 생성 방식 / UUID / Hash / Composite Key / Metadata 구조 /
Memory / Registry / Scheduler / Execution Layer / API / Component
Design / Implementation.

### 0.4 새 Concept를 도입하는가 — 먼저 답한다

**도입하지 않는다.** "Identity"가 가리키는 것은 `BASELINE.md`에 이미
문언으로 존재한다.

> `BASELINE.md` §13.1: *"Context Identifier | Context 또는 Segment의
> **동일성 판정 기준**."*

"동일성 판정 기준"이 곧 Identity다. 이 RFC는 그 이름을 부를 뿐,
없던 것을 만들지 않는다. **다만 그 이름을 Baseline 어휘로 등재할지는
이 RFC가 제안하지 않는다** — ADC-0006 판단 5가 같은 종류의 승격을
Defer한 선례가 있으므로, 어휘 등재 여부는 후속 ADC의 판단 대상이다.

---

## 1. Q2를 먼저 답해야 한다 — Identity와 Identifier는 같은 개념인가

**Q1~Q6 중 Q2를 첫 번째로 다룬다.** 나머지 질문이 전부 이 구분 위에서
갈리기 때문이다.

### 1.1 구분

| | Identity (동일성) | Identifier (식별자) |
|---|---|---|
| 무엇인가 | **두 것이 같은 것인지 판정하는 기준** | 그 판정을 위해 붙는 **값·표기** |
| 형태 | 관계(relation) | 값(value) |
| 개수 | 하나의 대상에 하나 | 하나의 Identity를 여러 표기로 나타낼 수 있다 |
| 없을 수 있는가 | 없으면 "같다"를 말할 수 없다 | **없어도 Identity는 성립할 수 있다** — 구조적 동등성(같은 Segment 열이면 같은 Context)만으로도 판정 가능하다 |

**핵심**: Identifier는 Identity를 **표현하는 수단**이지 Identity
**자체**가 아니다.

### 1.2 Baseline은 이 둘을 한 이름으로 묶고 있다 — 이것이 V-1의 뿌리다

`BASELINE.md`가 "Context Identifier"에 대해 말하는 두 문장을 나란히
놓으면 성격이 다르다.

| 문언 | 무엇에 대한 진술인가 |
|---|---|
| §13.1: *"Context 또는 Segment의 **동일성 판정 기준**"* | **Identity** — 관계 |
| CM-3: *"Kernel은 Identifier를 스스로 **생성하지 않는다.** 호출자가 주입하거나 결정론적으로 파생한다"* | **Identifier** — 값 |

**정의는 Identity로 쓰여 있고, 제약은 Identifier에 걸려 있다.**

이것이 V-1이 닫히지 않은 이유를 설명한다. V-1은 *"Identifier가 어디서
오는가"*를 물었는데, 그 값이 어디서 와야 하는지는 **"무엇이 같은
것인가"를 정하지 않고서는 답할 수 없다.**

- 동일성이 **구조적**이라면(같은 내용 = 같은 것) → Identifier는
  형식으로부터 파생될 수 있다.
- 동일성이 **지명적**이라면(누가 같다고 부르면 같은 것) → Identifier는
  주입되어야 한다.

**즉 ADC-0006 OQ-1의 두 후보는 Identifier의 선택지가 아니라 Identity의
선택지였다.** 값의 출처를 고르는 문제로 보였던 것이 실은 판정 기준을
고르는 문제였다.

### 1.3 제안하는 답 (Q2)

> **Identity와 Identifier는 다른 개념이다.** Identity는 판정 기준이고,
> Identifier는 그 기준을 표현하는 값이다.

이 RFC는 이 구분을 **제안**할 뿐 확정하지 않는다.

---

## 2. Q5 — 현재 Baseline은 Identity를 암묵적으로 가정하고 있는가

**Evidence를 수집한다. 새 Evidence를 만들지 않는다.**

### 2.1 Baseline 안의 암묵적 가정 (전수)

| # | 문언 | 무엇을 가정하는가 |
|---|---|---|
| E-1 | §13.2 병합: *"같은 Identifier + 같은 Content는 중복 제거"* | Identifier의 **동등 관계** + Content의 **동등 관계** |
| E-2 | §13.2 병합: *"같은 Identifier + 다른 Content는 **오류**"* | 위와 동일. "다른"은 "같은"의 부정이므로 같은 기준에 의존 |
| E-3 | §13.2 검증: *"Identifier 존재·**유일성**"* | 유일성은 **동등 관계 위에서만** 정의된다 |
| E-4 | O-2: *"유일한 Identifier를 최종 **tie-break**로 사용한다"* | 동등을 넘어 **전순서(비교 가능성)**까지 가정한다 |
| E-5 | G-1: *"**같은** (Segment 집합, Ordering Policy) → **같은** Kernel Context"* | 입력의 동일성과 출력의 동일성 **양쪽**을 가정한다 |
| E-6 | G-5: *"외부가 넘긴 Segment는 **변경되지 않는다**"* | 변경 여부 판정 = 동일성 판정 |
| E-7 | A-5 / A-3 | E-5·E-6과 동일한 가정 |
| E-8 | G-2 확인 방법: *"입력 Segment의 제시 순서를 섞어도 결과 순서가 **동일한지** 확인"* | 결과의 동일성 판정 |

**8개 지점에서 동일성 판정이 전제되고 있으며, 그 기준은 어디에도
정의되어 있지 않다.**

특히 **E-1·E-2는 Identifier뿐 아니라 Content의 동일성까지 요구한다** —
"같은 Content"가 바이트 동일인지, 정규화 후 동일인지, 그 외인지가
Baseline에 없다.

### 2.2 코드에 이미 존재하는 동일성 판정

| Evidence | 내용 | 출처 |
|---|---|---|
| E-9 | `request_id`가 MVP-0003 → 0004 → 0005 세 단계에 걸쳐 **동일한 값으로 유지**됨이 Dogfooding에서 실측 확인됨 | `ARTIFACT-STANDARD-v1.md` "Canonical field 재사용, 재생성 아님" |
| E-10 | MVP-0009 `build_context_bundle()`이 `[p for p in existing_workflow if p not in relevant_code]`로 중복을 제거 — **문자열 동등성**을 동일성 기준으로 사용 | `development-hq/mvp/project_intelligence.py:143-144` |
| E-11 | 정본 불변 테스트 4건이 전부 **문자열 동일성 비교**로 구현됨 | `core/execution_layer/*/tests/` |

**즉 동일성 판정은 이미 실물로 쓰이고 있으며, 그 기준은 우연히
"문자열 동일"이었다.** 선택된 것이 아니라 기본값이었다.

### 2.3 Q5의 답

> **가정하고 있다.** Baseline 8개 지점과 코드 3개 지점이 동일성 판정
> 위에서 동작하며, 그 기준은 명시된 적이 없다.

**이것은 결함의 발견이지 새 요구의 도입이 아니다.** Identity는 이미
Baseline 안에서 작동 중이며, 다만 이름과 정의가 없을 뿐이다.

---

## 3. Q1 — Identity는 본질적 속성인가, 외부에서 부여되는가

### 3.1 질문을 정확히 나눈다

§1의 구분을 적용하면 이 질문은 하나가 아니라 둘이다.

| 질문 | 대상 |
|---|---|
| Q1-a | **판정 기준**은 어디에 속하는가 |
| Q1-b | **표기 값**은 어디서 오는가 |

### 3.2 제안 — 둘은 서로 다른 곳에 속한다

**Q1-a (판정 기준)**: ADC-0006 판단 6a가 *"무엇이 유효한 Kernel
Context인지는 Kernel이 판정한다"*를 재진술로 Accept했다. 동일성 판정은
바로 그 판정의 일부다 — §13.2의 검증(유일성)과 병합(중복·충돌)이
동일성 없이는 수행될 수 없다(E-1~E-3).

> **판정 기준은 Kernel에 속한다.**

**Q1-b (표기 값)**: CM-3이 이미 답했다 — Kernel은 생성하지 않는다.
ADC-0006 판단 6a의 *"만들어진 값은 호출자가 들고 있다"*와 같은
방향이다.

> **표기 값은 Kernel이 만들지 않는다.**

### 3.3 두 답은 모순되지 않는다

**기준을 정하는 것과 값을 만드는 것은 다른 일이다.** 이 구분은 이
저장소에 실물로 존재한다.

> Execution Layer의 5개 Builder는 `state`가 허용된 5개 값 중
> 하나인지 **판정**하되(`test_all_five_allowed_states_are_accepted`,
> `test_unknown_state_is_rejected`), 그 값을 **만들지는 않는다** —
> `state`는 호출자 주입이다(`ARTIFACT-STANDARD-v1.md`).

같은 형태다. 기준은 안에, 값은 밖에.

### 3.4 Q1의 답 (제안)

> Identity의 **판정 기준**은 Kernel에 속하는 본질적 속성이고,
> Identifier의 **표기 값**은 외부에서 온다.

**이 RFC는 이 답을 확정하지 않는다.** 제안이며, ADC의 판단 대상이다.

---

## 4. Q6 — Identity가 새 Layer·Component·Runtime·API·Service를 암시하는가

### 4.1 판정 기준으로서의 Identity — 암시하지 않는다

동등 관계는 **Model의 성질**이지 실행되는 무엇이 아니다. §13.2의
검증·병합이 이미 그것을 사용하고 있으므로, 명시한다고 해서 새로
수행되는 일이 생기지 않는다.

| 검사 | 결과 |
|---|---|
| 새 Layer | 없음 — 동등 관계는 계층이 아니다 |
| 새 Component | 없음 — §13.2의 기존 책임이 이미 사용 중 |
| 새 Runtime | 없음 — 판정은 상태를 남기지 않는다(G-7과 정합) |
| 새 Service | 없음 |
| 새 API | 없음 |

### 4.2 그러나 한 방향은 Component를 암시한다 — 이것을 드러낸다

**§3.2의 Q1-b를 반대로 택하면**, 즉 *"Kernel이 Identifier 값을
부여한다"*는 방향을 택하면 다음이 따라온다.

- 값을 **발급**해야 한다 → 발급 주체가 필요하다.
- 발급된 값이 충돌하지 않아야 한다 → **발급 이력**을 알아야 한다.
- 이력을 안다 → **호출 간 상태**가 생긴다.

**이는 G-7(Context 경로에서 호출 간 상태 없음)을 직접 깨뜨리고,
Registry·Runtime 형태의 Component를 암시한다.**

CM-3이 *"Kernel은 Identifier를 생성하지 않는다"*로 이미 이 방향을
막아 두었다. **이 RFC의 발견은 CM-3이 왜 그렇게 규정되었는지를
Identity 관점에서 설명할 수 있다는 것**이며, 새 제약을 만들지
않는다.

### 4.3 Q6의 답

> **판정 기준으로서의 Identity는 아무것도 암시하지 않는다.**
> 다만 "Kernel이 값을 부여한다"는 방향은 Registry·Runtime을
> 암시하며, 그 방향은 CM-3·G-7이 이미 배제하고 있다.

---

## 5. Q3 — Identity는 Reference Layer에서 정의 가능한가

### 5.1 두 부분으로 갈린다

| 대상 | 어느 Layer의 문제인가 | 근거 |
|---|---|---|
| **동일성 판정 기준**(무엇이 같은 것인가) | **Reference** | §13.2 검증·병합이 이미 이것에 의존한다(E-1~E-3). Reference가 답하지 않으면 그 두 책임이 정의되지 않은 채 남는다 |
| **표기 값의 생성 방식**(UUID·Hash·Composite 등) | **Component / Implementation** | H-5가 이미 Hidden으로 두었고, ADC-0003 판단 1b가 **Defer**했다 |

### 5.2 판별 기준

이 저장소가 반복해 사용한 기준을 그대로 적용한다 — **"외부가 의존해도
되는가"**(§14.4).

- 외부(HQ, Execution Layer)는 **"이 두 Context가 같은가"에 의존한다.**
  Conversation Resume, Context Snapshot 같은 사례가 성립하려면 반드시
  필요하다(§13.6에 활용 사례로 기록됨 — 단 전부 Defer 상태).
- 외부는 **"그 값이 UUID인가 Hash인가"에는 의존하지 않는다.** 의존하면
  H-5(Hidden)를 침범한다.

**따라서 경계는 정확히 §14.4의 Public/Hidden 경계와 일치한다** —
기준은 Public(Reference), 생성 방식은 Hidden(Component 이하).

### 5.3 Q3의 답 (제안)

> **동일성 판정 기준은 Reference Layer의 문제다.**
> **표기 값의 생성 방식은 Reference Layer의 문제가 아니다.**

---

## 6. Q4 — Identity를 Reference에서 정의하지 않으면 V-1은 닫히는가

**"닫힌다"의 기준에 따라 답이 갈린다. 두 기준을 모두 검토한다.**

### 6.1 기준 A — "경계표에 행이 생기는가"

**닫힌다.** ADC-0006 판단 4가 확인한 대로, 경계표에 행 하나를
추가하면 형식 요건은 충족된다. 예컨대 *"Kernel Context의 Identifier:
Kernel이 생성하지 않는다(CM-3). 주입 또는 파생"*이라고 쓸 수 있다.

### 6.2 기준 B — "Assemble 책임의 입력이 정의되는가"

**닫히지 않는다.**

VALIDATION-0001 항목 8이 V-1을 Component RFC의 차단 요인으로 판정한
근거는 다음이었다.

> *"Assemble 책임의 입력이 정의되지 않으면 그 책임을 구현할 후보를
> 논할 수 없다."*

§6.1의 행은 **선언(disjunction)이지 입력 정의가 아니다.** "주입
또는 파생"은 두 개의 서로 다른 입력을 뜻한다.

- **주입**이면 Assemble의 입력에 값이 하나 더 있다.
- **파생**이면 Assemble의 입력에 값이 추가되지 않고, 대신 **파생
  규칙**이 있어야 한다.

**두 경우의 입력 개수가 다르다.** 따라서 선택하지 않으면 입력이
정의되지 않는다.

그리고 §1.2에서 보였듯 **그 선택은 Identity 없이는 할 수 없다** —
동일성이 구조적이면 파생이 성립하고, 지명적이면 주입이 필요하다.

### 6.3 Q4의 답

> **기준 B에서 닫히지 않는다.** 그리고 VALIDATION-0001이 V-1을
> 차단 요인으로 판정한 근거가 기준 B이므로, **실질적으로는 닫히지
> 않는다.**

### 6.4 ADC-0006 판단 4와 모순되지 않는다

ADC-0006 판단 4는 *"V-1은 Ownership 없이도 닫을 수 있다"*고 했고,
이 RFC는 *"Identity 없이는 닫히지 않는다"*고 한다. 겉보기에 반대로
보이므로 구분을 명시한다.

| | 무엇을 제공하는가 | V-1과의 관계 |
|---|---|---|
| Ownership (RFC-0006) | 그 행이 왜 그 방향인지에 대한 **정당화** | 없어도 행을 쓸 수 있다 |
| Identity (본 RFC) | 두 후보 중 하나를 고르기 위한 **판정 기준** | **없으면 고를 수 없다** |

**역할이 다르다.** 정당화는 결정을 설명하고, 기준은 결정을 가능하게
한다.

---

## 7. 이 RFC가 결정하지 않는 것

- Identity의 **내용** — 무엇이 동일성 기준이 되어야 하는지(구조적/
  지명적/그 외)를 정하지 않는다. **경계만 확인한다.**
- Identifier의 **생성 방식** — UUID·Hash·Composite Key 어느 것도
  다루지 않는다.
- Content의 동일성 기준(§2.1 E-1·E-2가 드러낸 공백) — 존재를 지적할
  뿐 정하지 않는다.
- H-5(Identifier 파생 규칙, **Defer**)를 해제하지 않는다.
- "Identity"를 Baseline 어휘로 등재할지 — ADC의 판단 대상이다(§0.4).
- V-1을 닫는 실제 문언 — 후속 단계다.

---

## 8. Evidence Summary

**새로 만든 Evidence는 없다.** 전부 기존 문서·소스에 기록되어 있던
사실이다.

| ID | Evidence | 출처 | 쓰인 곳 |
|---|---|---|---|
| E-1 | 병합 규칙이 Identifier와 Content **양쪽의 동등 관계**를 요구 | `BASELINE.md` §13.2 | Q5, Q3 |
| E-2 | 병합 충돌 규칙이 같은 기준에 의존 | §13.2 | Q5 |
| E-3 | 검증이 Identifier **유일성**을 요구 — 동등 관계 없이는 정의 불가 | §13.2 | Q5, Q3 |
| E-4 | O-2가 Identifier의 **전순서**까지 가정 | §13.3 | Q5 |
| E-5 | G-1이 입력·출력 **양쪽의 동일성**을 가정 | §14.3 | Q5 |
| E-6 | G-5(불변)가 변경 여부 판정에 의존 | §14.3 | Q5 |
| E-7 | A-3·A-5가 동일한 가정 | §13.3 | Q5 |
| E-8 | G-2 확인 방법이 결과 동일성 판정에 의존 | §14.3 | Q5 |
| E-9 | `request_id`가 3개 MVP에 걸쳐 동일 값으로 유지됨이 실측 확인 | `ARTIFACT-STANDARD-v1.md` | Q5 |
| E-10 | `build_context_bundle()`이 **문자열 동등성**으로 중복 제거 | `project_intelligence.py:143-144` | Q5 |
| E-11 | 정본 불변 테스트 4건이 문자열 동일성 비교로 구현됨 | `core/execution_layer/*/tests/` | Q5 |
| E-12 | §13.1이 Identifier를 *"동일성 판정 기준"*으로 정의 — **Identity 문언** | §13.1 | Q2, §0.4 |
| E-13 | CM-3이 Identifier를 **값**으로 제약 | §13.1 | Q2, Q1-b |
| E-14 | 5개 Builder가 `state`를 **판정하되 만들지 않음** | `ARTIFACT-STANDARD-v1.md` | Q1 |
| E-15 | H-5(파생 규칙)가 Hidden·Defer 상태 | §14.4, ADC-0003 판단 1b | Q3 |
| E-16 | VALIDATION-0001 항목 8의 차단 근거 = *"Assemble 책임의 입력"* | VALIDATION-0001 | Q4 |

**가장 중요한 것은 E-12와 E-13이다** — 같은 이름("Context
Identifier") 아래 Identity 문언과 Identifier 제약이 함께 놓여 있다.

---

## 9. Open Questions

| ID | 질문 | 성격 |
|---|---|---|
| **OQ-1'** | 동일성 판정 기준은 **구조적**인가(같은 내용 = 같은 것) **지명적**인가(같다고 부르면 같은 것) | ADC-0006 OQ-1의 **재정식화.** 원래 질문(주입인가 파생인가)은 이 질문의 **귀결**이다 |
| **OQ-9** | **"같은 Content"란 무엇인가** — 바이트 동일인가, 정규화 후 동일인가 | **신규.** §2.1 E-1·E-2가 드러낸 공백. 현재 코드는 문자열 동일을 기본값으로 쓰고 있으나 선택된 적이 없다(E-10, E-11) |
| **OQ-10** | Identifier의 **전순서**(O-2 tie-break)는 어떤 기준인가 — 동등 관계보다 강한 가정이 필요하다 | **신규.** E-4 |
| **OQ-11** | "Identity"를 Baseline 어휘로 등재할 것인가 | ADC-0006 판단 5(Ownership 어휘 Defer)와 같은 종류의 판단 |
| OQ-2 | Context Metadata의 출처 | ADC-0006에서 이월 |
| OQ-6 | 오래 보관된 Kernel Context의 유효성 | ADC-0006에서 이월. **OQ-1'과 직결된다** — 동일성이 구조적이면 시점과 무관하다 |
| OQ-8 | V-1을 닫는 최소 변경 | **§6이 부분적으로 답했다** — 기준 B에서는 Identity 확정 없이 닫을 수 없다 |

---

## 10. 영향받는 문서 — **수정하지 않는다**

이 RFC는 어떤 문서도 수정하지 않는다. 아래는 **후속 ADC/ADR이
승인될 경우** 영향을 받을 문서다.

| 문서 | 예상 영향 | 성격 |
|---|---|---|
| `BASELINE.md` §13.1 | "Context Identifier" 정의가 Identity와 Identifier로 나뉠 수 있다 | **기존 문언 영향 가능** |
| `BASELINE.md` §13.2 | 병합·검증이 의존하는 동일성 기준이 명시될 수 있다 | 보강 |
| `BASELINE.md` §15.1 (경계표) | V-1 해소 행이 추가될 수 있다 | 추가 |
| `BASELINE.md` §14.4 H-5 | 파생 규칙의 Hidden 범위가 조정될 수 있다 | 보강 |
| `GLOSSARY.md` | Identity 항목이 추가될 수 있다(OQ-11 판단에 따름) | 추가 |
| `VALIDATION-0001` V-1 | 해소 상태가 갱신될 수 있다 | 상태 |

**주의가 필요한 것은 §13.1 한 건이다.** 이는 v1.2에서 추가된 문언이며
Frozen 상태다. ADC-0006 판단 7이 §11 변경을 Reject한 기준(*"유지해도
어떤 후속 작업도 막히지 않는다"*)을 §13.1에도 적용해야 한다 —
**§13.1을 유지한 채 §13.2 쪽에 기준을 명시하는 것으로 충분한지**가
ADC의 판단 대상이 된다.

**영향받지 않는 문서**: `development-hq/**`, `core/execution_layer/**`,
`archive/v1/**`.

---

## 11. ADC가 필요한가

### **필요하다.**

`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준 **1을 만족한다.**

> *"지금 결정하지 않으면 상위 Architecture를 진행할 수 없다."*

근거 사슬:

1. VALIDATION-0001 항목 8: V-1 해소 전 Component RFC 착수 불가.
2. ADC-0006 판단 8: V-1은 그 ADC로 닫히지 않았다.
3. 본 RFC §6.2: V-1은 **Identity 없이 닫히지 않는다**(기준 B).

**ADC-0006 판단 4와의 차이를 명시한다**: 그 판단은 Ownership이
"진행 불가"의 근거가 되지 못한다고 정정했다. 본 RFC는 Identity에
대해 반대로 주장하며, 그 근거는 §6.4의 역할 구분(정당화 vs 판정
기준)이다. **이 주장이 성립하는지 자체가 ADC의 첫 판단 대상이
되어야 한다.**

### ADC가 판단해야 할 것 (제안)

| # | 판단 대상 |
|---|---|
| 1 | **Identity가 V-1의 차단 요인이라는 §6의 주장이 성립하는가** (Gating) |
| 2 | Identity와 Identifier를 다른 개념으로 구분할 것인가(Q2) |
| 3 | 동일성 판정 기준은 Reference Layer의 문제인가(Q3) |
| 4 | 판정 기준은 Kernel에, 표기 값은 외부에 속한다는 §3.4의 답을 채택할 것인가 |
| 5 | Baseline이 Identity를 암묵적으로 가정한다는 §2의 Evidence를 인정할 것인가 |
| 6 | "Identity"를 Baseline 어휘로 등재할 것인가(OQ-11) — **ADC-0006 판단 5의 선례 적용 대상** |
| 7 | §13.1 문언 변경이 필요한가 — **Frozen 변경 여부**(§10) |
| 8 | Baseline 반영 범위 |

---

## Out of Scope

- Identifier 생성 방식 — UUID·Hash·Composite Key·그 외.
- Metadata 구조.
- Memory / Registry / Scheduler / Runtime / Event Bus / Engine Gateway.
- Execution Layer, Kernel API, Component Design, Implementation.
- Identity의 **내용** — 구조적인지 지명적인지(OQ-1').
- Content 동일성 기준의 **내용**(OQ-9).
- VALIDATION-0001의 V-2 및 나머지 발견 사항.

## Non-goals

- 이 RFC는 Identifier를 정의하지 않는다.
- 이 RFC는 Identity를 정의하지 않는다 — **Boundary만 확인한다.**
- 이 RFC는 Ownership·Responsibility를 다시 결정하지 않는다.
- 이 RFC는 ADC-0006이 Defer한 Ownership 어휘를 사용하지 않는다(§0.2).
- 이 RFC는 새 Concept·Layer·Component·Service를 도입하지 않는다.
- 이 RFC는 H-5를 비롯한 어떤 Defer도 해제하지 않는다.
- 이 RFC는 어떤 문서도 수정하지 않는다.
- 이 RFC는 V-1을 닫지 않는다.

## Self Review

- Identifier를 정의했는가 — **아니오**. 생성 방식·알고리즘을 다루지
  않았고, §7이 이를 명시했다.
- Identity를 정의했는가 — **아니오**. §1은 Identity와 Identifier의
  **구분**을 제안했을 뿐, 무엇이 동일성 기준인지는 OQ-1'로 열어
  두었다.
- 새 Concept를 도입했는가 — **아니오**. §0.4가 §13.1의 *"동일성 판정
  기준"* 문언을 근거로 제시했고, 어휘 등재는 OQ-11로 남겼다.
- 새 Component·Layer·Runtime·Service를 암시했는가 — **아니오**.
  §4.1에서 전수 확인했고, §4.2에서 **암시하게 되는 방향**(Kernel이 값을
  부여)을 드러내되 그것이 CM-3·G-7으로 이미 배제되어 있음을 기록했다.
- ADC-0006의 Defer를 존중했는가 — **예**. §0.2가 Ownership 어휘를
  쓰지 않고 판단 6a의 결론만 기존 어휘로 인용하는 방식을 명시했다.
- 기존 Evidence만 사용했는가 — **예**. 16건 전부 기존 문서·소스에
  있던 사실이며, §8에 출처를 개별 표기했다.
- ADC-0006 판단 4와 모순되는가 — **아니오**. §6.4가 역할 구분(정당화
  vs 판정 기준)으로 두 주장이 양립함을 보였고, 그 주장 자체를 ADC
  판단 1(Gating)의 대상으로 넘겼다.
- Frozen 문언 변경을 요구했는가 — **아니오**. §10이 §13.1을 유일한
  주의 대상으로 표시하고, ADC-0006 판단 7의 Reject 기준을 적용해야
  한다고 기록했다.
- V-1을 닫았는가 — **아니오**. §6.3이 닫히지 않았음을 명시했다.
- 문서를 수정했는가 — **아니오**.
