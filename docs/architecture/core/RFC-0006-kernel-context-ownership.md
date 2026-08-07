# RFC-0006: Kernel Context Ownership — Kernel은 Kernel Context를 어디까지 소유하는가

**Status**: Proposed (검토 대상, 결정 아님)
**Version**: Draft
**Author**: Claude Code (VALIDATION-0001 Major Finding V-1 후속)
**상위 근거**: `docs/01_architecture/BASELINE.md` v1.4 §13·§14·§15
**직접 계기**: `docs/architecture/core/VALIDATION-0001-kernel-reference-architecture.md`
V-1 (Major) — *"Kernel Context의 Identifier·Metadata 입력 경로가
배선도에 없다"*

> 이 RFC는 **하나의 질문에만** 답한다.
> **Kernel은 Kernel Context를 어디까지 소유하는가?**
>
> Identifier 생성 방법, Metadata 생성 방법, 저장 방식, Component,
> API, Implementation은 이 RFC의 범위가 아니다.

---

## 0. 이 RFC의 범위

### 0.1 다루는 것

VALIDATION-0001의 Major Finding 중 **V-1 하나만** 다룬다. V-2(Merge의
순서 무관성)를 포함한 나머지 발견 사항은 이 RFC의 범위가 아니다.

### 0.2 다루지 않는 것

Identifier 생성 방법 / Metadata 생성 방법 / Assembler 구현 / Renderer
구현 / Runtime / Scheduler / Registry / Memory / Event Bus / API /
Execution Layer / Context 저장 방식 / Component Design /
Implementation.

### 0.3 "Ownership"은 새 Concept인가 — 먼저 답한다

이 RFC는 새 Concept를 만들지 않는다. 그 근거를 문서 첫머리에 밝힌다.

`BASELINE.md`에 "Ownership"이라는 용어는 존재하지 않는다. 그러나
**Ownership이 묻는 질문에는 이미 여러 절이 부분적으로 답하고 있다.**

| 이미 결정된 것 | 위치 |
|---|---|
| Context는 **값(Value)이며 서비스가 아니다** | §13.1 |
| Kernel은 조립된 Context를 **값으로 돌려준다** | §14.2 PR-1 |
| Kernel은 Context 경로에서 **호출 간 상태를 갖지 않는다** | G-7 |
| 흐름에 **영속화 지점이 없다** | §15.2 |
| *"Kernel Context를 보관한다는 것은 **호출자가** 그 값을 들고 있는 것이지 Kernel이 저장하는 것이 아니다"* | §15.2 |
| Kernel은 Identifier·시각을 **생성하지 않는다** | CM-3 |
| Kernel은 Content와 Source를 **해석하지 않는다** | CM-4 |
| 무엇이 Context에 들어갈지는 **HQ가 정한다** | §13.5 |

**즉 답은 이미 문서 곳곳에 흩어져 있고, 어디에도 한 문장으로
모여 있지 않다.** 이 RFC가 하는 일은 그것을 모으는 것이다.

따라서 이 RFC는 **"Ownership"을 Baseline의 새 Concept로 등재할 것을
제안하지 않는다.** Ownership은 기존 결정들이 이미 답하고 있던 질문을
부르는 이름이며, 답 자체는 기존 어휘(책임 / 값 / 경계)로 전부
표현된다. 등재 여부는 이 RFC가 아니라 후속 ADC의 판단 대상이다.

---

## 1. 문제 — V-1이 실제로 무엇을 드러냈는가

VALIDATION-0001 V-1은 표면적으로 "배선도에 화살표 하나가 빠졌다"는
지적이었다. 그러나 그 빠진 화살표를 그리려면 먼저 답해야 하는 질문이
있다.

- §13.1은 Kernel Context가 **Identifier와 Metadata를 갖는다**고 했다.
- CM-3은 Kernel이 그것을 **생성하지 않는다**고 했다.
- §15.1의 경계표에는 그 **입력 경로가 없다**.

세 진술이 동시에 참이면, Identifier는 **경계 밖에서 오거나, 형식으로부터
파생되거나, 아예 존재하지 않아야** 한다. 어느 쪽인지를 정하려면
"그 값이 누구의 것인가"를 먼저 알아야 한다.

**속성(Identifier)을 먼저 정하면 소유가 그 속성에서 역산된다.** 이
프로젝트는 같은 방향 오류를 세 번 피했다 — Prompt Cache가 Kernel의
목적이 아니라 결과라는 것(RFC-0002 §12.1), 계약이 API 위에 있다는 것
(RFC-0004 §0), 배선이 인터페이스 위에 있다는 것(RFC-0005 §0). **네
번째 적용이 이 RFC다.**

---

## 2. Ownership과 Responsibility는 다르다 (검토 사항 4)

**이 구분이 이 RFC의 나머지 전부를 결정하므로 먼저 정의한다.**

| | Responsibility (책임) | Ownership (소유) |
|---|---|---|
| 묻는 것 | **무엇을 해야 하는가** | **무엇에 대해 최종 결정권을 갖는가** |
| 형태 | 수행 의무 | 권한·귀속 |
| 시간 | **구간을 가진다** — 시작하고 끝난다 | 구간이 아니라 **영역**이다 |
| 위반의 모습 | 해야 할 일을 하지 않음 | 남의 것을 결정함 |

**핵심**: 무언가를 **만들 책임**이 있다는 것과 그것을 **소유한다**는
것은 다르다.

이 구분은 이 저장소에 이미 실물로 존재한다.

> Execution Layer의 5개 Builder는 Artifact를 **만들 책임**을 지지만,
> `request_id`·`created_at`·`handle_id`·`submitted_at`·`state`·
> `changed_at`을 **전부 호출자로부터 주입받는다**
> (`ARTIFACT-STANDARD-v1.md` "caller-supplied identity/time fields",
> 5개 MVP 전체에서 반복). 만드는 쪽과 정하는 쪽이 다르다.

**즉 "Kernel이 Kernel Context를 만든다"는 사실만으로는 "Kernel이
Kernel Context를 소유한다"가 따라 나오지 않는다.** V-1이 드러낸 공백은
정확히 이 지점이다.

---

## 3. Ownership을 세 층으로 나눈다 (검토 사항 1)

"Kernel은 Context를 소유하는가, 전달만 하는가"는 **이분법으로는 답할
수 없다.** 무엇에 대한 소유인지가 셋으로 갈리기 때문이다.

| 층 | 무엇에 대한 소유인가 | 누구의 것인가 | 근거 |
|---|---|---|---|
| **O-1 내용(Content)** | 무엇이 Context에 들어가는가 | **HQ** | §13.5, CM-4, §14.2 PR-1의 "제공 ≠ 내용 마련" |
| **O-2 형식(Form)** | 무엇이 유효한 Kernel Context인가 — 구조·정합성·순서·불변식 | **Kernel** | §13.1 Model, §13.2 검증·병합·정렬, §13.3 A-1~A-5·O-1~O-4, §14.3 G-1~G-7 |
| **O-3 인스턴스(Instance)** | 만들어진 그 값을 누가 들고 있고 언제 버리는가 | **호출자** | §13.1(값), §14.2 PR-1(돌려준다), G-7, §15.2(영속화 지점 없음), N-4 |

### 3.1 이 세 층으로 답하면 원래 질문이 해소된다

> **Kernel은 Context 자체를 소유하는가, 전달만 하는가?**
>
> **Kernel은 형식(O-2)을 소유하고, 인스턴스(O-3)를 소유하지 않는다.**
> 내용(O-1)은 애초에 Kernel의 것이 아니다.

"전달만 한다"도 정확하지 않다 — Kernel은 단순 통과 지점이 아니라
**무엇이 유효한 Kernel Context인지를 결정하는 유일한 주체**다. 그것이
O-2 소유의 의미다.

### 3.2 O-2 소유가 실제로 뜻하는 것

Kernel이 형식을 소유한다는 것은 다음을 뜻한다.

- 어떤 Segment 집합이 Kernel Context가 될 수 있는지 **Kernel이
  판정한다**(§13.2 검증).
- 조립된 값이 어떤 순서를 갖는지 **Kernel이 확정한다**(§13.3).
- 그 판정과 확정을 **호출자가 무를 수 없다** — 호출자가 "이 검증은
  건너뛰라"고 요구할 수 없다(G-6, RR-2).

**반대로 Kernel이 할 수 없는 것**: 만들어진 값을 붙잡아 두기, 나중에
바꾸기, 폐기 시점 정하기. 그것은 O-3이며 호출자의 것이다.

### 3.3 왜 O-3이 호출자의 것인가 — 이것은 이 RFC의 발명이 아니다

§15.2가 이미 문장으로 기록했다.

> *"Kernel Context를 보관한다"는 것은 **호출자가** 그 값을 들고 있는
> 것이지, Kernel이 저장하는 것이 아니다.*

G-7(Context 경로에서 호출 간 상태 없음)과 N-4(Memory Service는
Non-Goal)가 같은 방향을 가리킨다. Kernel이 인스턴스를 소유하려면 그것을
어딘가에 들고 있어야 하고, 그러면 G-7이 즉시 깨진다.

---

## 4. Boundary — 생성 / 유지 / 전달 중 어디까지인가 (검토 사항 2)

### 4.1 세 단어를 먼저 구분해야 한다

**"전달"이라는 단어가 이 저장소에서 두 가지를 뜻하고 있다.** 그 사실을
먼저 드러낸다.

| 용례 | 위치 | 뜻 |
|---|---|---|
| "Context 전달 책임 → **Memory**" | `BASELINE.md` §11 대응표 | 운반·영속 — **어딘가에 두었다가 나중에 꺼내는 것** |
| "Kernel Context를 **값으로 돌려준다**" | §14.2 PR-1 | 반환 — **호출자에게 결과를 넘기는 것** |

**이 둘은 다른 일이다.** §11의 대응표는 "Context 전달 책임"의 구현
후보로 Memory를 적었고, Memory Module은 Kernel ADC-0001에서
**Defer**되었다.

### 4.2 답

| 책임 | Kernel의 것인가 | 근거 |
|---|---|---|
| **생성(Construction)** — 유효한 Kernel Context를 만들어내는 것 | **예** | §13.2·§13.3, §15.1 ①~⑤ |
| **유지(Retention)** — 만들어진 값을 계속 들고 있는 것 | **아니오** | G-7, §15.2, N-4 |
| **반환(Return)** — 호출자에게 값을 넘기는 것 | **예** | §14.2 PR-1 |
| **운반·영속 전달(Delivery/Persistence)** — 값을 다른 곳에 두었다가 꺼내는 것 | **미결** | §11 대응표(Memory), Kernel ADC-0001 Memory **Defer** |

**즉 Kernel의 책임은 생성과 반환까지다.** 유지는 Kernel의 것이 아니고,
운반·영속은 아직 결정되지 않았다.

이 RFC는 마지막 행(운반·영속)에 답하지 않는다 — 그것은 Memory Module의
Defer와 직결되며, 여는 순간 이 RFC의 범위를 벗어난다.

---

## 5. Lifecycle (검토 사항 3)

**정의만 한다. 구현하지 않는다.**

### 5.1 두 개의 구간을 구분해야 한다

```
      호출자                          Kernel                         호출자
        │                               │                              │
        │  Segment Content              │                              │
        │  Source 선언                  │                              │
        │  Ordering Policy 선택         │                              │
        ├──────────────────────────────▶│                              │
        │                          ┌────┴────┐                         │
   ①    │                          │ ① ~ ⑤  │  ← Kernel 책임 구간      │
        │                          └────┬────┘                         │
        │                               │  Kernel Context              │
        │                               ├─────────────────────────────▶│
        │                               │                          ②   │
        │                            (끝)                              │
        │                                                        값은 계속
        │                                                        존재한다
```

| 구간 | 시작 | 끝 |
|---|---|---|
| **Kernel의 책임 구간** | 입력이 Kernel 경계를 넘어온 시점(①의 입력) | Kernel Context가 경계를 넘어 반환된 시점 |
| **Kernel Context의 존재 구간** | ⑤Assemble이 값을 확정한 시점 | **Kernel이 알지 못한다** — 호출자가 그 값을 버릴 때 |

### 5.2 값은 책임보다 오래 산다

**이것이 Lifecycle의 핵심이며, §13.1이 Context를 "값"으로 정한 결과다.**

값이 불변이면(§13.1, A-1, A-3) 그 값은 만든 쪽의 관리 없이도 계속
유효하다. 따라서 Kernel의 책임이 끝난 뒤에도 그 값은 온전하며, 이는
결함이 아니라 값 의미론의 정상 동작이다.

이 성질은 이 저장소에 이미 실물로 있다 — Execution Layer의 5개
Artifact는 전부 생성 후 하류에서 변경되지 않으며, 그 사실이 4건의
테스트로 고정되어 있다(`ARTIFACT-STANDARD-v1.md`).

### 5.3 Lifecycle은 값 단위가 아니라 호출 단위다

G-7(Context 경로에서 호출 간 상태 없음)의 직접적 귀결이다.

- 호출자가 나중에 그 Kernel Context로 ⑥Render를 요청하면, 그것은
  **같은 Lifecycle의 연장이 아니라 새 책임 구간의 시작**이다.
- Kernel은 "이 Context를 전에 만들었다"는 사실을 기억하지 않는다 —
  기억하면 G-7이 깨진다.

**따라서 Kernel Context에는 "Kernel이 관리하는 생명주기"가 없다.**
생성 시점만 Kernel이 관여하고, 그 이후는 값의 문제다.

### 5.4 폐기(Disposal)

Kernel은 폐기하지 않는다. 폐기할 대상을 들고 있지 않기 때문이다
(§5.1, G-7). 폐기는 O-3(인스턴스 소유)에 속하며 호출자의 것이다.

---

## 6. 이 답이 V-1에 미치는 영향

### 6.1 Identifier 후보가 좁혀진다 — 그러나 결정되지 않는다

VALIDATION-0001은 Identifier의 출처 후보를 셋으로 정리했다. Ownership이
정해지면 그중 하나가 **제거되고**, 남은 둘의 성격이 달라진다.

| 후보 | Ownership 관점의 귀결 |
|---|---|
| Kernel이 생성 | **제거됨.** CM-3이 이미 금지했고, O-3이 Kernel의 것이 아니라는 사실이 그 금지의 이유를 설명한다 — 남의 것에 이름을 붙일 권한이 없다 |
| 호출자가 주입 | **성립.** O-3 소유자가 인스턴스의 정체성을 정한다 |
| 형식으로부터 파생(내용 기반) | **성립.** O-2 소유자가 형식의 함수로 정체성을 정한다 |

**이 RFC는 남은 둘 중 하나를 고르지 않는다.** 둘 다 Ownership 모델과
정합적이며, 어느 쪽인지는 파생 규칙(H-5, **Defer**)과 맞물린 별도
판단이다.

Context Metadata도 동일하다 — Context 수준 Metadata는 인스턴스에 대한
서술이므로 같은 두 후보를 갖는다.

### 6.2 V-1은 이 RFC만으로 완전히 닫히지 않는다 — 정직하게 기록한다

V-1이 요구한 것은 **§15.1 경계표에 입력 경로가 나타나는 것**이었다.
이 RFC는 "그 경로가 어느 쪽일 수 있는가"를 두 후보로 좁혔을 뿐,
배선표를 채우지 않는다.

**남는 작업**: 두 후보 중 하나를 택하거나, 둘 다 허용하되 어느
쪽인지를 호출자가 선언하도록 하거나. 그 판단은 이 RFC의 범위가 아니다.

**그럼에도 이 RFC가 선행되어야 하는 이유**: Ownership을 정하지 않고
경로만 그리면, 그 경로가 왜 그래야 하는지 설명할 근거가 없다. 속성이
소유를 결정하는 역방향이 된다(§1).

---

## 7. Reference 적합성 자체 점검 (검토 사항 5)

| 확인 | 결과 |
|---|---|
| Component를 설계했는가 | **아니오.** Assembler·Renderer·Memory·Registry·Runtime·Scheduler 어느 것도 설계하지 않았다 |
| Component를 명명했는가 | Memory는 §4.1·§4.2에서 **미결 사항의 이름으로만** 인용했다(§11 대응표 인용). 설계하지 않았다 |
| API·시그니처를 정의했는가 | **아니오** |
| Identifier·Metadata 생성 방법을 정했는가 | **아니오.** §6.1이 후보를 좁혔을 뿐 선택하지 않았다 |
| 저장 방식을 정했는가 | **아니오.** §5.4가 Kernel에 폐기 개념이 없다고만 했다 |
| 새 Layer·Concept를 만들었는가 | **아니오.** §0.3이 Ownership이 새 Concept가 아님을 근거와 함께 밝혔다 |
| 기존 어휘만 사용했는가 | **예.** 책임 / 값 / 경계 / 호출자 / HQ — 전부 Baseline v1.4의 어휘다 |
| Reference Layer에서 논의 가능한가 | **예.** 이 RFC의 모든 진술은 "누가 무엇을 결정하는가"이며, "무엇이 어떻게 구현되는가"가 아니다 |

**한 가지 경계 사례를 기록한다**: §4.2가 "운반·영속 전달"을 **미결**로
분류하면서 Memory Module의 Defer를 인용했다. 이는 Memory를 설계하는
것이 아니라, **이 RFC가 답하지 않는 영역의 이름을 정확히 부르기 위한
인용**이다. 이름을 부르지 않으면 "전달"의 두 뜻이 계속 섞인다(§4.1).

---

## 8. 영향받는 문서 (검토 사항 6) — **수정하지 않는다**

이 RFC는 어떤 문서도 수정하지 않는다. 아래는 **후속 ADC/ADR이
승인될 경우** 영향을 받을 문서 목록이다.

| 문서 | 예상되는 영향 | 성격 |
|---|---|---|
| `docs/01_architecture/BASELINE.md` §13.5 | Kernel/HQ 책임 배치에 **Ownership 3층 구분**이 추가될 수 있다 | 추가 |
| `BASELINE.md` §15.1 (경계표) | Kernel Context의 Identifier·Metadata 입력 경로 행이 추가될 수 있다(V-1 해소) | 추가 |
| `BASELINE.md` §15 (Lifecycle) | 책임 구간과 값 존재 구간의 구분이 기록될 수 있다 | 추가 |
| `BASELINE.md` §11 (대응표) | "Context 전달 책임"의 두 뜻(반환 / 운반·영속)이 구분될 수 있다 | **기존 문언 영향 가능** |
| `BASELINE.md` §14.2 PR-1 | "제공"의 의미가 Ownership 어휘로 보강될 수 있다 | 보강 |
| `docs/00_governance/GLOSSARY.md` | Ownership 관련 항목이 추가될 수 있다 | 추가 |
| `VALIDATION-0001` V-1 | 해소 상태가 갱신될 수 있다 | 상태 |

**주의가 필요한 것은 §11 대응표 한 건뿐이다.** 나머지는 전부 추가이며
기존 문언을 건드리지 않는다. §11은 v1.0부터 유지된 표이고 ADR-0005가
이미 §10에서 Frozen 문언을 한 번 변경했으므로, **또 한 번의 기존
문언 변경이 필요한지**는 신중히 판단되어야 한다.

**영향받지 않는 문서**: `development-hq/**`, `core/execution_layer/**`,
`archive/v1/**`. 이 RFC는 코드에 영향을 주지 않는다.

---

## 9. Open Questions

이 RFC가 답하지 않는 질문을 나열만 한다.

### OQ-1. Kernel Context의 Identifier는 호출자 주입인가, 형식으로부터의 파생인가

§6.1이 후보를 둘로 좁혔다. 선택은 H-5(파생 규칙, **Defer**)와
맞물린다. **Ownership만으로는 결정되지 않는다** — 둘 다 정합적이다.

### OQ-2. Context 수준 Metadata의 출처는 Identifier와 같아야 하는가

둘 다 인스턴스에 대한 서술이므로 같은 후보를 갖지만, 반드시 같은
선택이어야 하는지는 별개다.

### OQ-3. "Context 전달 책임"(§11 대응표)의 두 뜻을 문서에서 구분해야 하는가

§4.1이 반환과 운반·영속이라는 두 뜻을 드러냈다. 구분을 §11에 반영할
것인지, 아니면 이 RFC의 기록으로 충분한지.

### OQ-4. 운반·영속 전달은 Kernel의 책임인가

§4.2가 **미결**로 남긴 행이다. Memory Module의 Defer(Kernel ADC-0001)와
직결되며, 그 Defer의 재검토 조건이 충족되어야 열린다.

### OQ-5. Ownership을 Baseline의 어휘로 등재할 것인가

§0.3은 Ownership이 새 Concept가 아니라 기존 결정들에 붙인 이름이라고
밝혔다. 그렇더라도 Baseline에 **어휘로 등재할지**는 별개의 판단이다.
등재하지 않고 기존 어휘(책임/값/경계)만으로 §13.5를 보강하는 선택지도
있다.

### OQ-6. 호출자가 Kernel Context를 오래 보관한 뒤 사용하는 경우의 유효성

§5.2가 "값은 책임보다 오래 산다"고 했다. 그렇다면 오래된 Kernel
Context를 나중에 ⑥Render에 넣는 것이 항상 유효한가 — 그 값이 참조하는
내용이 그사이 낡았다면? **이 질문은 `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md`
가 다룬 Artifact Drift와 같은 종류다.** 이 RFC는 연결만 지적하고 답하지
않는다.

---

## 10. ADC가 필요한가

### **필요하다.**

`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준 2개 중 **기준 1을
만족한다.**

> **"지금 결정하지 않으면 상위 Architecture를 진행할 수 없다."**

근거: `VALIDATION-0001` 항목 8이 *"V-1 해소 전에는 Component RFC 착수
불가"*로 판정했다. 그 근거는 **"Assemble 책임의 입력이 정의되지 않으면
그 책임을 구현할 후보를 논할 수 없다"**였다.

기준 2("결정이 늦어질수록 되돌리는 비용이 커진다")도 부분적으로
해당한다 — Ownership을 정하지 않은 채 Component RFC가 진행되면, 각
Component 제안이 서로 다른 Ownership을 암묵적으로 가정하게 되고 그
차이는 나중에야 드러난다.

### ADC가 판단해야 할 것 (제안)

이 RFC는 ADC의 판단 항목을 **제안만** 한다.

| # | 판단 대상 |
|---|---|
| 1 | Ownership 3층 구분(O-1 내용 / O-2 형식 / O-3 인스턴스)을 채택할 것인가 |
| 2 | "Kernel은 형식을 소유하고 인스턴스를 소유하지 않는다"는 답을 확정할 것인가 |
| 3 | Boundary 4행(생성 예 / 유지 아니오 / 반환 예 / 운반·영속 미결)을 확정할 것인가 |
| 4 | Lifecycle 진술(책임 구간과 값 존재 구간의 분리, 호출 단위 Lifecycle)을 확정할 것인가 |
| 5 | Ownership을 Baseline 어휘로 등재할 것인가(OQ-5) |
| 6 | §11 대응표의 "Context 전달 책임"을 구분할 것인가(OQ-3) — **기존 Frozen 문언 변경 여부** |
| 7 | Baseline 반영 범위 |

**판단 6은 특히 신중해야 한다.** ADR-0005가 §10에서 Frozen 문언을
변경한 첫 사례를 만들었고, VALIDATION-0001은 그것을 *"경계 조정의
선례가 생겼다"*는 위험으로 기록했다. 같은 일이 §11에서 반복되는 것이
타당한지는 별도 근거가 필요하다.

---

## Out of Scope

- Identifier·Metadata의 생성·파생 알고리즘.
- Context 저장 방식, Memory Service, 영속화.
- Assembler·Renderer의 구현, Component Design.
- Registry / Runtime / Scheduler / Engine Gateway / Event Bus.
- API, 함수 시그니처, 자료형.
- Execution Layer의 문서·코드.
- VALIDATION-0001의 V-2 및 나머지 발견 사항.

## Non-goals

- 이 RFC는 V-1을 완전히 닫지 않는다 — 후보를 둘로 좁힐 뿐이다(§6.2).
- 이 RFC는 OQ-1~OQ-6에 답하지 않는다.
- 이 RFC는 새 Concept·Layer·Component를 만들지 않는다.
- 이 RFC는 §13.6·§14.7의 Defer를 해제하지 않는다 — 특히 H-5(Identifier
  파생 규칙)와 Memory Module의 Defer를 그대로 둔다.
- 이 RFC는 어떤 문서도 수정하지 않는다(§8).
- 이 RFC는 Baseline을 변경하지 않는다.

## Self Review

- 질문 하나만 답했는가 — **예.** Ownership 외의 V-1 후속 작업(배선표
  갱신)은 §6.2에서 범위 밖으로 명시했다.
- Identifier 생성 방법을 설계했는가 — **아니오.** §6.1이 후보 셋 중
  하나를 **기존 제약(CM-3)으로 제거**하고 둘을 남겼을 뿐, 선택하지도
  알고리즘을 제시하지도 않았다.
- 새 Concept를 만들었는가 — **아니오.** §0.3이 Ownership이 기존
  결정들에 붙인 이름임을 8개 근거와 함께 밝혔고, 등재 여부를 OQ-5로
  남겼다.
- Component를 설계·명명했는가 — **아니오.** Memory는 §4에서 **미결
  영역의 이름으로만** 인용했고, 그 인용이 필요한 이유("전달"의 두 뜻
  구분)를 §7에 기록했다.
- Ownership과 Responsibility를 구분했는가 — **예.** §2가 표로
  구분하고, Execution Layer의 caller-supplied identity 관행을 실물
  근거로 제시했다.
- Reference Layer를 벗어났는가 — **아니오.** §7이 8개 항목으로 자체
  점검했고, 경계 사례 1건(Memory 인용)을 기록했다.
- 기존 결정과 충돌하는가 — **없음.** §3의 답은 §13.1·§14.2·G-7·
  §15.2·CM-3·CM-4·§13.5와 전부 같은 방향이며, 새 제약을 만들지
  않는다.
- V-1을 완전히 닫았다고 주장하는가 — **아니오.** §6.2가 닫히지 않는
  부분을 명시했다.
- 문서를 수정했는가 — **아니오.** §8은 영향 예상 목록이며 수정이
  아니다.
