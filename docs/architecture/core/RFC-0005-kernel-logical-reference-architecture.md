# RFC-0005: Kernel Logical Reference Architecture — 책임의 배선도

**Status**: Resolved — `ADC-0005.md` → `ADR-0005`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Version**: Draft
**Author**: Claude Code (Kernel Reference Architecture 요청 → RFC 전환)
**상위 근거**: `docs/01_architecture/BASELINE.md` v1.3 §11·§12·§13·§14
**관련 문서**: `docs/architecture/core/RFC-0002`~`RFC-0004`,
`ADC-0002`~`ADC-0004`, `docs/04_adr/ADR-0002`~`ADR-0004`,
`docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md` §5
(Kernel Readiness Assessment),
`docs/architecture/core/ADC-0001-core-baseline.md`,
`development-hq/BOUNDARY.md`

> 이 RFC는 API를 정의하지 않는다. 함수 시그니처, 클래스 구조, DI,
> Runtime 구현을 정의하지 않는다.
> 이 RFC는 **이미 결정된 책임들이 서로 어떻게 연결되는가**를
> 정의한다 — 논리적 배선도다.

---

## 0. 이 RFC는 Baseline §10과 직접 충돌한다 — 먼저 그것부터 다룬다

**이 절을 첫 번째로 두는 이유**: 이 RFC의 나머지 내용이 아무리
타당해도, 이 충돌이 해소되지 않으면 아무것도 진행할 수 없다.

`docs/01_architecture/BASELINE.md` §10 Out of Scope는 v1.0부터 다음을
포함한다.

```
- Kernel Architecture
- Component Design (Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)
```

**"Kernel Architecture"와 "Component Design"은 서로 다른 항목이다.**
후자가 전자를 설명하는 것이 아니라 별도 항목으로 나열되어 있다.
따라서 "Kernel Architecture"를 좁게 읽어 Component Design만 뜻한다고
주장하는 것은 문언에 없는 해석이다.

그리고 `GOVERNANCE-REVIEW-0001-post-adc-0001.md` §5는 이렇게 기록했다.

> §10은 Kernel Architecture와 Component Design을 v1.0 시점부터
> 명시적으로 Out of Scope로 남겨 두었다 — **이 결정은 아직 뒤집힌 적이
> 없다.**

**즉 이 RFC는 §10이 배제한 영역의 일부를 여는 제안이다. 그 사실을
숨기지 않는다.**

### 0.1 그럼에도 지금 제안하는 근거

`GOVERNANCE-REVIEW-0001` §5가 "Kernel을 설계할 Evidence가 아직 없다"고
판단한 근거는 6개였다. 그 6개가 **무엇에 대한 근거였는지**를 확인한다.

| §5의 근거 | 무엇에 대한 판단인가 | 지금도 유효한가 |
|---|---|---|
| §10이 Out of Scope로 남겨 둠 | 절차 — 뒤집으려면 절차가 필요하다 | **유효.** 그래서 이 RFC가 절차를 밟는다 |
| 5개 Module 중 3개(Workflow/Memory/Event Bus) Defer | **Component 간 통합 구조** | **유효.** 3개 모두 여전히 Defer |
| ADC-02(Runtime 개념의 존폐) Open | **Component 개념의 존폐** | **유효.** 여전히 Open |
| 승격 압력이 관찰된 대상이 없음 | Component 승격 근거 | **유효** |
| Engine Gateway Trigger("Engine 수 ≥ 2") 미충족 | **Component 필요성** | **유효.** Engine은 여전히 0개 호출 |
| Execution Result(6번째 Artifact) 미설계 | Execution Layer 완결성 | **유효** |

**6개 전부 지금도 유효하다.** 그러나 6개 중 5개는 **Component 수준의
판단**이며, 어느 것도 "Context 책임들이 서로 어떻게 연결되는가"에
대한 것이 아니다.

그 사이에 Context 영역에서는 다음이 결정되었다.

| 결정 | 문서 | Baseline |
|---|---|---|
| Kernel Context Model(5개 요소, 제약 4건) | ADC-0003 판단 1 | §13.1 |
| Context Builder 4개 책임 | ADC-0003 판단 2 | §13.2 |
| Assembly 불변식 A-1~A-5, 순서 요구 O-1~O-4 | ADC-0003 판단 3 | §13.3 |
| Prompt = Output Format, Renderer 계약 | ADC-0003 판단 5 | §13.4 |
| HQ/Kernel 책임 배치 | ADC-0003 판단 6a | §13.5 |
| Public Contract(PR/G/H/X/N) | ADC-0004 | §14 |

**즉 부품은 전부 결정되었는데, 그 부품들이 어떤 순서로 어떻게
이어지는지는 어디에도 기록되어 있지 않다.**

### 0.2 이 RFC가 제안하는 §10의 구분

이 RFC는 §10을 **삭제하거나 축소하자고 제안하지 않는다.** 대신 §10이
배제하는 것을 두 가지로 **구분**할 것을 제안한다.

| 구분 | 내용 | 제안 |
|---|---|---|
| **Kernel Component Architecture** | Component(Scheduler, Engine Gateway, Registry, Memory, Runtime, Event Bus)가 무엇이고 어떻게 통합되는가 | **Out of Scope 유지** — §5의 근거 6개가 전부 이것을 가리킨다 |
| **Kernel Logical Reference Architecture** | 이미 결정된 책임들이 어떤 순서로 이어지고 어떤 데이터가 오가는가 | **이 RFC가 여는 것을 제안** |

### 0.3 이 구분이 성립하려면 지켜야 할 조건

위 구분은 말로만 하면 의미가 없다. 이 RFC는 스스로에게 다음 조건을
부과하고, §7에서 그 충족 여부를 자체 점검한다.

| ID | 조건 |
|---|---|
| C-1 | **새 책임을 하나도 만들지 않는다.** 모든 단계는 Baseline v1.3에 이미 있는 책임이어야 한다. |
| C-2 | **새 Model 요소를 하나도 만들지 않는다.** §13.1의 5개 요소가 그대로 유지되어야 한다. |
| C-3 | **어떤 Component도 명명하지 않는다.** Scheduler/Registry/Runtime/Memory/Event Bus/Gateway가 이 문서에 등장하지 않아야 한다(인용 제외). |
| C-4 | **§13.6·§14.7의 Defer를 하나도 해제하지 않는다.** |
| C-5 | **특정 언어·프레임워크·실행 모델을 전제하지 않는다.**(§6) |

**C-1과 C-2가 이 RFC의 성격을 결정한다** — 새 책임도 새 데이터도
만들지 않는다면, 이 문서는 설계가 아니라 **이미 내린 결정들의
배선도**다.

---

## 1. 문제

Baseline v1.3은 다음을 각각 정의했다.

- Kernel이 무엇을 관리하는가(§13.1)
- 어떤 책임이 있는가(§13.2)
- 조립이 무엇을 지켜야 하는가(§13.3)
- Prompt는 무엇인가(§13.4)
- 외부에 무엇을 보장하는가(§14)

그러나 다음은 어디에도 없다.

- 검증은 **언제** 일어나는가? 병합 전인가 후인가?
- Ordering Policy는 **어느 지점에서** 들어오는가?
- Kernel의 경계선은 **어디를 지나는가**? Context Source는 안인가 밖인가?
- Renderer는 Kernel **안**인가 **밖**인가?

이 질문들은 API를 설계할 때 반드시 답해야 하지만, **API에서 답하면
순서가 뒤집힌다** — 배선이 인터페이스의 형태에서 역산된다. KP-1이
금지하는 방향이다.

---

## 2. Responsibility Flow — 책임의 흐름

### 2.1 전체 배선도

```
        ┌─────────────────────── Kernel 경계 밖 (HQ 책임) ───────────────────────┐
        │                                                                        │
        │   Context Source 선언        Segment Content 제공     Policy 선택       │
        │        (X-3)                       (§13.5)            (X-2, X-1)       │
        └───────────┬────────────────────────┬────────────────────┬──────────────┘
                    │                        │                    │
════════════════════▼════════════════════════▼════════════════════▼═══════ Kernel 경계
                    │                        │                    │
              ┌─────┴────────────────────────┴────────┐           │
              │  ① Collect        (§13.2 수집)        │           │
              └──────────────────┬────────────────────┘           │
                                 │                                │
              ┌──────────────────▼────────────────────┐           │
              │  ② Merge          (§13.2 병합)        │           │
              └──────────────────┬────────────────────┘           │
                                 │                                │
              ┌──────────────────▼────────────────────┐           │
              │  ③ Validate       (§13.2 검증)        │◀── G-6    │
              └──────────────────┬────────────────────┘           │
                                 │                                │
              ┌──────────────────▼────────────────────┐           │
              │  ④ Order          (§13.2 정렬)        │◀──────────┘ Ordering Policy
              └──────────────────┬────────────────────┘
                                 │
              ┌──────────────────▼────────────────────┐
              │  ⑤ Assemble       (§13.3)             │◀── A-1~A-5, O-1~O-4
              └──────────────────┬────────────────────┘
                                 │
                        ╔════════▼════════╗
                        ║  Kernel Context ║  ← 정본 (§13.1). 여기서 불변이 된다
                        ╚════════┬════════╝
                                 │
              ┌──────────────────▼────────────────────┐
              │  ⑥ Render         (§13.4)             │◀── Renderer (X-1)
              └──────────────────┬────────────────────┘
                                 │
════════════════════════════════▼═════════════════════════════════════ Kernel 경계
                                 │
                            Output (표현)
```

### 2.2 각 단계의 책임

| 단계 | 책임 | 하지 않는 것 | 근거 |
|---|---|---|---|
| ① Collect | 지정된 Source들로부터 Segment를 모은다 | Source를 **발견**하지 않는다. 내용을 **해석**하지 않는다 | §13.2, CM-4 |
| ② Merge | 복수 Source의 Segment 집합을 하나로 합친다. 같은 Identifier + 같은 Content는 중복 제거 | Content를 합치거나 요약하지 않는다 | §13.2 |
| ③ Validate | 구조 불변식을 검사한다. 위반은 드러낸다 | 내용의 사실성·관련성·품질을 판단하지 않는다 | §13.2, G-6 |
| ④ Order | Ordering Policy에 따라 전순서를 부여한다 | 순서 규칙을 스스로 만들지 않는다 | §13.2, O-1~O-4 |
| ⑤ Assemble | 정렬된 Segment 열을 하나의 불변 값으로 확정한다 | Content를 변경하지 않는다. Segment를 추가·삭제하지 않는다 | §13.3 |
| ⑥ Render | Kernel Context를 표현으로 변환한다 | 정본을 변경하지 않는다. 없는 내용을 만들지 않는다. 순서를 다시 정하지 않는다 | §13.4, R-1·R-2·R-4·R-5 |

**C-1 점검**: 6개 단계 전부 Baseline §13.2·§13.3·§13.4에 이미 있는
책임이다. **새 책임은 하나도 없다.**

### 2.3 Merge와 Validate의 순서 — 이것은 도출된 것이지 선택된 것이 아니다

**근거 성격: 기존 결정으로부터의 도출.**

§13.2는 4개 책임을 나열했을 뿐 **순서를 말하지 않았다.** 그러나
②Merge → ③Validate 순서는 임의로 고른 것이 아니라 기존 결정에서
강제된다.

- §13.2의 병합 규칙: *"같은 Identifier + 다른 Content는 **오류**다."*
- 이 오류는 **두 Source의 Segment를 나란히 놓아 본 뒤에만** 판정할 수
  있다. 즉 병합을 시도하지 않고서는 이 검증이 불가능하다.
- G-6(No Silent Failure)는 이 오류가 드러나야 함을 요구한다.

따라서 **Identifier 충돌 검증은 병합 이후에만 가능하다.** 반대로
"Segment에 Identifier가 있는가" 같은 단일 Segment 검증은 병합 전에도
가능하다.

**이 RFC가 제안하는 최소 진술**: 검증은 **⑤Assemble 이전에 완료되어야
한다.** 그 안에서 몇 번 일어나는지, 어느 검사가 어느 지점에 배치되는지는
**규정하지 않는다** — 그것은 H-2(Builder 내부 구조, Hidden)에 속한다.

위 배선도가 ③을 ② 뒤에 그린 것은 **가능한 배치 하나를 그린 것**이며,
계약이 요구하는 것은 "Assemble 이전 완료" 하나뿐이다. 이 구분을 명시한다.

### 2.4 Kernel 경계선은 어디를 지나는가

**근거 성격: 기존 결정의 도식화.**

| 요소 | 경계 안/밖 | 근거 |
|---|---|---|
| Context Source의 **선언**(무엇을 볼 것인가) | **밖** (HQ) | §13.5, PR-1의 "제공 ≠ 내용 마련" |
| Segment의 **Content** | **밖에서 들어옴** (HQ가 제공) | §13.5, CM-4 |
| Ordering Policy의 **선택** | **밖** | §13.2(Policy는 입력), X-2 |
| Ordering Policy의 **구현** | 밖에서 주입되어 안에서 실행 | X-2 + H-1 |
| ①~⑤ | **안** | §13.2·§13.3 |
| Kernel Context | **안에서 생성, 밖으로 나감** | PR-1 |
| Renderer의 **계약** | **안** (Kernel이 보장) | PR-4 |
| Renderer의 **구현** | 교체 가능(X-1), 내부는 Hidden(H-4) | §14.4·§14.5 |
| Output | **밖** | §13.4(표현) |

**⑥Render의 위치가 미묘하다.** Renderer는 교체 가능(X-1)하면서도 그
계약은 Kernel이 보장한다(PR-4). 이 RFC는 그것을 **"경계 위에 걸친
단계"**로 그린다 — 계약은 안, 구현은 교체 가능. §14.4의 3층 구분
(교체 가능성 = Public / 계약 = Public / 구현 = Hidden)이 그대로 적용된다.

---

## 3. Data Flow — 무엇이 만들어져 무엇으로 넘어가는가

### 3.1 이것은 새 Model 요소가 아니다 (C-2)

**먼저 못박는다.** 아래에 나오는 이름들은 **§13.1의 Model에 추가되는
새 요소가 아니다.** 동일한 Segment 집합이 흐름을 지나며 갖는 **논리적
상태(state)**의 이름일 뿐이다.

§13.1의 Model은 그대로 5개(Context / Segment / Source / Metadata /
Identifier)이며, 이 RFC는 거기에 아무것도 더하지 않는다.

### 3.2 논리적 데이터 흐름

| 지점 | 데이터의 논리적 상태 | 이전 상태와 무엇이 달라졌는가 | 보장 |
|---|---|---|---|
| ①의 출력 | **수집된 Segment들** | Source별로 흩어져 있던 것이 한자리에 모임 | — |
| ②의 출력 | **중복이 제거된 Segment 집합** | 같은 Identifier + 같은 Content가 하나로 합쳐짐 | — |
| ③의 출력 | **검증된 Segment 집합** | 구조 불변식 위반이 없음이 확인됨 | G-6 |
| ④의 출력 | **순서가 부여된 Segment 열** | 집합이 **열**이 됨 (전순서 확정) | G-2 |
| ⑤의 출력 | **Kernel Context** | 열이 **불변 값**이 됨. Identifier·Metadata를 가짐 | G-1, G-5 |
| ⑥의 출력 | **표현(Output)** | Kernel Context의 파생물. 정본은 그대로 남음 | R-2, R-4 |

### 3.3 흐름 전체를 관통하는 두 가지 사실

**(1) Content는 ①에서 ⑥까지 한 글자도 바뀌지 않는다.**

A-1(조립 중 Content 불변), R-4(Renderer는 없는 내용을 만들지 않음),
그리고 §13.2 병합 규칙(Content를 합치거나 요약하지 않음)이 각 구간을
덮는다. **어느 단계도 Content를 쓰지 않는다** — 단계들이 하는 일은
모으기·합치기·검사하기·순서 정하기·굳히기·표현하기다.

이것은 Execution Layer 5개 Builder가 전부 "Wrap, not rewrite"였다는
사실(`ARTIFACT-STANDARD-v1.md`)의 일반화이며, 새 원칙이 아니다.

**(2) 정보는 한 방향으로만 흐른다.**

역방향 경로(Output → Kernel Context, Kernel Context → Segment)는
**정의되지 않는다.** §13.4가 이미 "역방향(Prompt → Context)은 정의하지
않는다"를 확정했고, 이 RFC는 그것을 흐름 전체로 확장한다.

### 3.4 어디에도 저장하지 않는다

이 흐름에는 **영속화 지점이 없다.** 각 상태는 다음 단계로 넘어가는
중간값이며, 어디에도 기록되지 않는다.

- N-4(Memory Service 구현은 Non-Goal)
- G-7(Context 경로에 한하여 Kernel은 호출 간 상태를 갖지 않는다)

"Kernel Context를 보관한다"는 것은 **호출자가** 그 값을 들고 있는
것이지, Kernel이 저장하는 것이 아니다.

---

## 4. Responsibility Relationship — 관계

### 4.1 왜 "Component Relationship"이 아니라 "Responsibility Relationship"인가

요청은 "Component Relationship"이었다. 이 RFC는 그것을
**Responsibility Relationship**으로 바꿔 다룬다. 이유를 명시한다.

- KP-1: *"Kernel은 구현 객체가 아니라 책임 경계다."*
- §11: *"Kernel은 구현으로 정의하지 않는다. 책임으로 정의한다."*
- C-3: 이 RFC는 어떤 Component도 명명하지 않는다.

Builder / Assembly / Validation / Renderer를 **Component로 다루면**,
그것들이 별개의 객체·모듈·서비스여야 한다는 전제가 생긴다. 그 전제는
구현 결정이며 §10이 배제하는 영역이자 C-5(언어·실행 모델 중립)를
깨뜨린다.

**의도한 내용(무엇이 무엇에 어떻게 의존하는가)은 그대로 다룬다.**
바꾸는 것은 그것을 부르는 이름뿐이다.

### 4.2 관계표

| 관계 | 내용 | 성격 |
|---|---|---|
| Collect·Merge·Validate·Order **→** Assemble | 앞의 4개는 Assemble의 **전제 조건**을 만든다. Assemble은 그 조건이 충족된 입력만 받는다 | 순차 의존 |
| Validate **↔** Merge | Validate의 일부(Identifier 충돌)는 Merge 이후에만 판정 가능하다(§2.3) | 부분 순서 |
| Order **←** Ordering Policy | Order는 규칙을 **주입받는다.** 스스로 만들지 않는다 | 입력 의존 |
| Assemble **→** Kernel Context | Assemble은 값을 **생산**한다. 그 값을 소유하지 않는다 | 생산 |
| Render **←** Kernel Context | Render는 값을 **소비**한다. 변경하지 않는다 | 읽기 전용 소비 |
| Render **↛** Collect/Merge/Order | Render는 앞 단계 어디에도 영향을 주지 않는다 | **비의존** |

### 4.3 관계에서 금지되는 것

| ID | 금지 | 근거 |
|---|---|---|
| RR-1 | **역방향 의존 금지** — 뒤 단계가 앞 단계의 동작을 바꿀 수 없다 | §13.4(역방향 미정의), G-1 |
| RR-2 | **단계 건너뛰기 금지** — Assemble은 검증되지 않은 입력을 받지 않는다 | G-6, A-2 |
| RR-3 | **공유 가변 상태 금지** — 단계들이 값을 주고받는 것 외의 경로로 소통하지 않는다 | G-1, G-7 |
| RR-4 | **Render가 정렬에 관여하는 것 금지** — 순서는 ④에서 확정된다 | O-4 |

**RR-4에 대한 주의**: 이것은 ADC-0003 판단 5에서 **Accept 범위에서
제외된 R-3**("Renderer는 Segment 순서를 재배치하지 않는다")과 같은
방향이다. R-3은 Execution Layer MVP-0002 `RENDERING_MAP`과 충돌하기
때문에 제외되었다.

**따라서 RR-4는 이 RFC의 제안 중 유일하게 기존 제외 결정과 겹치는
항목이며, 그 사실을 명시한다.** 다만 RR-4는 R-3과 범위가 다르다 —
R-3은 기존 Execution Layer 코드에 대한 요구였고, RR-4는 **이 Reference
Architecture 안에서의 관계**에 대한 진술이다. 이 구분이 성립하는지는
ADC의 판단에 맡긴다. 성립하지 않는다고 판단되면 RR-4를 빼야 한다.

---

## 5. Extension Flow — 확장 지점이 어디에 위치하는가

§14.5가 4개 확장 지점(X-1~X-4)을 선언했으나, **그것들이 흐름의 어느
지점에 붙는지는 기록되지 않았다.** 이 절이 그 위치만 정한다.

| 확장 지점 | 흐름상의 위치 | 무엇을 바꾸는가 | 무엇을 바꿀 수 없는가 |
|---|---|---|---|
| **X-3 Context Source** | ① Collect의 **입력** (경계 **밖**에서 선언) | 무엇이 들어오는가 | 들어온 것이 어떻게 처리되는가 |
| **X-2 Ordering Policy** | ④ Order의 **입력** | Segment의 상대 순서 | 순서가 전순서라는 사실(O-1), tie-break가 Identifier라는 사실(O-2) |
| **X-1 Renderer** | ⑥ Render의 **자리** | 표현의 형태 | 정본, 순서, 내용(R-2·R-4, RR-4) |
| **X-4 Future Context Model** | §13.1 Model — **흐름 밖** | Model 구성 요소 | CM-1~CM-4 |

### 5.1 확장 지점은 흐름을 바꾸지 않는다

**이 표에서 가장 중요한 사실**: 4개 확장 지점 중 **어느 것도 단계의
개수나 순서를 바꾸지 않는다.** 전부 특정 단계의 **입력**이거나 특정
단계의 **자리**에 꽂힐 뿐이다.

이것이 Reference Architecture가 안정적인 이유다 — Renderer가 10개로
늘어나도, Ordering Policy가 바뀌어도, Source가 추가되어도 배선도는
동일하다.

### 5.2 X-4는 흐름 밖에 있다

X-4(Future Context Model)만 유일하게 단계에 붙지 않는다. Model이
확장되면 **흐르는 데이터의 구조**가 달라지지만 **흐름 자체는 같다.**

예컨대 §13.6이 Defer한 4-Layer Context Model이 훗날 확정된다면, 그것은
**X-2를 통해 하나의 Ordering Policy로** 들어온다(§14.5). 단계는
6개 그대로다.

**다시 확인한다: 4-Layer는 여전히 Defer이며, 이 RFC는 그것이 확정될
것이라고 말하지 않는다**(C-4).

### 5.3 확장 메커니즘은 여전히 Defer다

*어떻게* 꽂는지(등록·발견·로딩·검증)는 ADC-0004 판단 5b에서 Defer되었고
이 RFC는 그것을 열지 않는다. 이 절이 정하는 것은 **위치**뿐이다.

---

## 6. Implementation Neutrality — 구현 중립성

**요구사항**: 이 Reference Architecture는 Python뿐 아니라 다른
구현체에서도 동일하게 적용 가능해야 한다.

### 6.1 중립성 규칙

| ID | 규칙 |
|---|---|
| IN-1 | 단계는 **책임**이며 객체·클래스·모듈·서비스가 아니다. 하나의 단계가 여러 구현 단위에 나뉘거나, 여러 단계가 하나에 합쳐져도 계약은 유지된다. |
| IN-2 | 단계 간 전달은 **논리적 값의 전달**이며, 특정 전달 방식(함수 인자, 메시지, 스트림, 파일)을 전제하지 않는다. |
| IN-3 | 흐름은 **동기/비동기, 순차/병렬 어느 실행 모델도 전제하지 않는다.** 요구되는 것은 순서 의존(§4.2)이지 실행 방식이 아니다. |
| IN-4 | 어떤 타입 시스템·상속·제네릭·DI 방식도 전제하지 않는다. |
| IN-5 | 데이터의 직렬화 형식을 전제하지 않는다(H-6, 미결). |

### 6.2 중립성 자체 시험

이 배선도가 언어·패러다임에 중립적인지 확인하는 방법을 제안한다.
**동일한 배선도가 최소 3개의 서로 다른 실행 형태로 표현될 수 있어야
한다.**

| 형태 | ①~⑥이 무엇이 되는가 | 계약이 유지되는가 |
|---|---|---|
| 순수 함수 파이프라인 | 값을 받아 값을 돌려주는 6개 변환 | G-1·G-5·G-7이 자연스럽게 성립 |
| 메시지 전달(액터 등) | 메시지를 받아 다음으로 보내는 6개 수신자 | 성립. 단 RR-3(공유 가변 상태 금지)이 명시적으로 지켜져야 함 |
| 서비스 체인 | 순서대로 호출되는 6개 처리 단계 | 성립. 단 G-7 때문에 어떤 단계도 호출 간 상태를 남길 수 없음 |

**세 형태 모두에서 G-1~G-7이 유지되어야 한다.** 어느 하나에서만
성립하는 배선은 중립적이지 않다.

이 시험은 **판정 기준이지 구현 계획이 아니다.** 이 RFC는 세 형태 중
어느 것도 채택하지 않는다.

### 6.3 중립성은 이미 Baseline이 요구하고 있다

IN-1~IN-5는 새 요구가 아니다.

- KP-5 Implementation Agnostic: *"특정 모델이나 특정 Runtime에
  종속되지 않는다."*
- G-4: *"Kernel은 호출자의 Runtime·언어·저장소·실행 방식을 강제하지
  않는다."*
- §3 "Everything is Replaceable"(v1.0부터 Frozen)

이 절은 그 요구를 Reference Architecture에 적용했을 때 무엇을
뜻하는지를 구체화한 것이다.

---

## 7. 조건 자체 점검 (§0.3의 C-1 ~ C-5)

| ID | 조건 | 점검 결과 |
|---|---|---|
| C-1 | 새 책임을 만들지 않는다 | **충족.** ①~⑥ 전부 §13.2·§13.3·§13.4의 책임이다. 새로 도입한 것은 **순서 진술 1건**(검증은 Assemble 이전 완료, §2.3)과 **관계 금지 4건**(RR-1~RR-4)이며, 앞의 것은 §13.2 병합 규칙에서 도출되었고 뒤의 것은 G-1·G-6·G-7·O-4에서 도출되었다. |
| C-2 | 새 Model 요소를 만들지 않는다 | **충족.** §3.1이 논리적 상태와 Model 요소를 명시적으로 구분했다. §13.1의 5개 요소는 그대로다. |
| C-3 | Component를 명명하지 않는다 | **충족.** Scheduler/Registry/Runtime/Memory/Event Bus/Gateway는 §0의 §10 인용 외에 등장하지 않는다. §4.1이 "Component Relationship"을 "Responsibility Relationship"으로 바꾼 이유를 기록했다. |
| C-4 | Defer를 해제하지 않는다 | **충족.** §5.2가 4-Layer의 Defer를 재확인했고, §5.3이 확장 메커니즘 Defer를 유지했다. |
| C-5 | 언어·프레임워크 중립 | **충족.** §6이 규칙 5건과 3형태 시험을 제시했다. |

**단 하나의 예외를 기록한다**: RR-4는 ADC-0003 판단 5가 Accept 범위에서
제외한 R-3과 겹치는 영역이 있다(§4.3). 이 RFC는 그것을 숨기지 않고
드러내며, 성립 여부의 판단을 ADC에 맡긴다.

---

## 8. 아직 결정하지 않는 것

- Kernel API — 인터페이스 형태, 함수 시그니처, 자료형(다음 단계).
- 클래스 구조, 모듈 분할, DI 방식, 패키지 구성.
- 실제 Runtime 구현, 동시성 모델, 오류 전달 방식.
- Extension Point의 메커니즘(등록·발견·로딩·검증) — ADC-0004 판단 5b
  Defer 유지.
- 직렬화 형식(H-6).
- Kernel **Component** Architecture — §10 Out of Scope 유지. §5의
  근거 6개가 여전히 유효하다(§0.1).
- RFC-0002 §15의 미결 3개 책임(Task 전달·Capability 탐색·Engine 호출).
- `BASELINE.md` §13.6의 Defer 6건 — 그대로 유지.
- 검증이 흐름 안에서 정확히 몇 번, 어느 지점에서 일어나는가 — H-2
  (Hidden)에 속한다(§2.3).

---

## Out of Scope

- 구현. 이 RFC는 코드를 만들지 않고 어떤 코드도 수정하지 않는다.
- API 설계 — 배선도가 확정된 뒤의 별도 단계다.
- Kernel Component Architecture — Scheduler/Registry/Runtime/Memory/
  Event Bus/Engine Gateway의 존재 여부, 설계, 상호작용.
- Development HQ·Execution Layer의 문서·코드 수정.
- Prompt Engineering, 모델별 캐싱 메커니즘.

## Non-goals

- 이 RFC는 API·함수 시그니처·클래스 구조·DI·Runtime을 정의하지 않는다.
- 이 RFC는 §10 전체를 여는 것을 제안하지 않는다 — Component
  Architecture는 Out of Scope로 유지한다(§0.2).
- 이 RFC는 새 책임·새 Model 요소·새 Component를 만들지 않는다(C-1~C-3).
- 이 RFC는 §13.6·§14.7의 Defer를 해제하지 않는다.
- 이 RFC는 특정 언어·프레임워크·실행 모델을 채택하지 않는다.
- 이 RFC는 Baseline을 변경하지 않는다 — 반영 여부는 후속 ADC·ADR의
  몫이다.

## Self Review

- §10과의 충돌을 숨겼는가 — **아니오**. §0을 문서 첫 절로 두고,
  "Kernel Architecture"와 "Component Design"이 별도 항목이므로 좁게
  읽는 해석은 문언에 없다는 사실까지 기록했다. 이 RFC가 §10의 일부를
  여는 제안임을 명시했다.
- Kernel Readiness 평가를 무시했는가 — **아니오**. §0.1이 §5의 근거
  6개를 하나씩 확인하고 **6개 전부 지금도 유효하다**고 인정했다. 그
  위에서, 6개 중 5개가 Component 수준 판단이라는 사실만을 근거로
  범위를 좁혀 제안했다.
- 새 책임·Model 요소·Component를 만들었는가 — **아니오**. §7이 C-1~C-3을
  개별 점검했다. 새로 도입한 진술 5건(순서 1 + 관계 금지 4)은 전부
  기존 결정에서 도출된 것이며 그 도출 경로를 각각 명시했다.
- 기존 제외 결정과 겹치는 항목이 있는가 — **있다. 드러냈다.** RR-4가
  ADC-0003 판단 5의 R-3 제외와 겹친다(§4.3). 구분이 성립하는지를 ADC에
  맡겼고, 성립하지 않으면 빼야 한다고 명시했다.
- Defer를 해제했는가 — **아니오**. §5.2(4-Layer), §5.3(확장 메커니즘),
  §8이 각각 유지를 확인했다.
- 특정 언어·프레임워크를 전제했는가 — **아니오**. §6이 규칙 5건과
  3형태 시험을 제시했고, 세 형태 중 어느 것도 채택하지 않았다.
- 요청과 다르게 처리한 것이 있는가 — **있다. 기록했다.** "Component
  Relationship"을 "Responsibility Relationship"으로 바꿨다. 이유는
  KP-1과 C-3이며, 다루는 내용은 그대로다(§4.1).
- Development HQ·Execution Layer를 수정했는가 — **아니오**.
- Baseline을 변경했는가 — **아니오**.
