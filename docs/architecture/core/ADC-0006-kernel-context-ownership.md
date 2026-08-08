# ADC-0006: Kernel Context Ownership 채택 판단 (RFC-0006 후속)

## 목적

`docs/architecture/core/RFC-0006-kernel-context-ownership.md`를 검토해
**7개 항목을 개별 판단**한다. 일괄 승인하지 않는다.

이 ADC는 Ownership을 **어떻게 구현할지** 결정하지 않는다. Ownership을
**Architecture Vocabulary와 Reference Boundary로 채택할지**만
판단한다.

Identifier 생성 방식 / Metadata 출처 / Memory / Scheduler / Registry /
Execution Layer / Kernel API / Component Design / Implementation은 이
ADC의 범위가 아니다.

근거는 RFC-0006, 그리고 그것이 인용한 기존 문서·코드
(`docs/01_architecture/BASELINE.md` v1.4,
`docs/architecture/core/VALIDATION-0001-kernel-reference-architecture.md`,
`RFC-0002`~`RFC-0005`, `ADC-0001`~`ADC-0005`, `ADR-0002`~`ADR-0005`,
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`)에 실제로 기록된
사실로만 한정한다.

**이 ADC가 매 판단마다 확인하는 기준선**

| 기준선 | 내용 |
|---|---|
| B-1 | 새 Component·Layer·Runtime·Service를 도입하지 않는다. |
| B-2 | `BASELINE.md` §13.6·§14.7의 Defer(특히 H-5 Identifier 파생 규칙)와 Kernel ADC-0001의 Memory Defer를 해제하지 않는다. |
| B-3 | Frozen 문언 변경은 **충분한 Evidence가 있을 때만** 허용한다. |

---

## 판단 1. Ownership과 Responsibility를 서로 다른 개념으로 채택할 것인가

### Evidence

**두 개념이 실제로 갈라지는 사례가 이 저장소에 실물로 존재한다.**

| Evidence | 내용 | 출처 |
|---|---|---|
| caller-supplied identity | Execution Layer 5개 Builder는 Artifact를 **만들 책임**을 지지만 `request_id`·`created_at`·`handle_id`·`submitted_at`·`state`·`changed_at`을 **전부 호출자로부터 주입받는다.** 5개 MVP 전체에서 반복된 설계 결정 | `ARTIFACT-STANDARD-v1.md` "caller-supplied identity/time fields" |
| 시계·난수 부재 | 5개 MVP 전체에서 `uuid.uuid4`/`datetime.now`/`time.time` 부재가 테스트로 확인됨 | 동일 문서 |
| CM-3 | Kernel은 조립할 **책임**을 지면서 Identifier를 **생성하지 않는다** | `BASELINE.md` §13.1 |
| §13.5 | HQ는 무엇이 들어갈지 정하고, Kernel은 어떻게 처리되는지 담당 — **권한의 분할**을 책임 어휘로 서술 | §13.5 |
| §14.4 Hidden 효력 | *"Hidden에 의존한 코드가 Kernel 변경으로 깨지는 것은 계약 위반이 아니다"* — 이는 의무가 아니라 **변경 권한**에 대한 진술 | §14.4 |

**"만드는 쪽"과 "정하는 쪽"이 다른 상황이 9개 MVP에 걸쳐 반복
관찰되었다.** 두 개념이 동일하다면 이 분리는 나타날 수 없다.

### 검토한 반론 (기록)

- **"이 프로젝트의 어휘는 전부 책임 기반이다(KP-1: Kernel은 책임
  경계다). 두 번째 축을 들이면 KP-1이 희석되지 않는가"** — 희석
  위험은 실재한다. 다만 판단 1이 Accept하는 것은 **개념이 구분된다는
  사실**이지 **그 어휘를 Baseline에 들이는 것**이 아니다. 후자는
  판단 5에서 별도로 판단한다. 이 분리가 없으면 판단 1이 판단 5를
  자동 통과시키게 된다.
- **"Ownership 없이도 §13.5가 이미 같은 것을 말하고 있지 않은가"** —
  말하고 있다. 그래서 판단 1은 "새 개념의 도입"이 아니라 "이미
  갈라져 있던 두 개념이 서로 다르다는 사실의 확인"이다.

### Decision

**Accept** — 단 **개념적 구분의 확인**에 한정한다.

Accept되는 것: **Responsibility(수행 의무, 시간 구간을 가짐)와
Ownership(최종 결정권, 영역)은 서로 다른 개념이며, 이 저장소의 기존
설계는 이미 그 구분 위에서 동작해 왔다.**

Accept되지 **않는** 것: 그 구분을 Baseline 어휘로 등재하는 것
(판단 5), 3층 구조의 명명(판단 6).

### Decision Rationale

두 개념이 동일하다는 가설은 Evidence와 충돌한다 — 9개 MVP에 걸쳐
"만들되 정하지 않는" 패턴이 반복되었고, CM-3이 그것을 원칙으로
고정했다. 구분의 확인은 새 commitment를 만들지 않으므로 채택 비용이
없다.

### Next Step

**No ADR Required** — 이 Accept는 Baseline을 변경하지 않는다.

---

## 판단 2. RFC-0006이 새 Component·Layer·Runtime·Service를 도입하는가

### Evidence (전수 확인)

| 검사 대상 | 확인 결과 |
|---|---|
| 새 Component | **없음.** RFC-0006은 Assembler·Renderer·Memory·Registry·Runtime·Scheduler 어느 것도 설계하지 않았다 |
| Memory 언급 | §4.1·§4.2에서 **미결 영역의 이름으로만** 인용(§11 대응표 인용). 설계 없음. RFC-0006 §7이 이 경계 사례를 스스로 기록했다 |
| 새 Layer | **없음** — 아래 명명 위험 참조 |
| 새 Runtime 암시 | **없음.** §5.3이 오히려 *"Kernel Context에는 Kernel이 관리하는 생명주기가 없다"*로 Runtime적 관리를 배제했다 |
| 새 Service 암시 | **없음.** §3의 답이 "Kernel은 인스턴스를 소유하지 않는다"이며, 이는 Service화의 반대 방향이다(G-7·N-4와 동일 방향) |
| "호출자"는 새 행위자인가 | **아니오.** §14.1이 이미 계약의 수신자로 Development HQ·Execution Layer·미래 HQ를 등재했다 |

### 발견 — 명명 위험 1건 (기록)

RFC-0006은 Ownership을 **"3층"**(O-1 내용 / O-2 형식 / O-3 인스턴스)
으로 부른다. **이 "층"은 Architecture Layer가 아니라 소유 대상의
분류다.**

그러나 `BASELINE.md` §5 Meta Architecture가 Jarvis OS → HQ → Agent →
Connector를 계층으로 정의하고 있고, 이 프로젝트는 "새 Layer를 만들지
않는다"를 반복 확인해 왔다. **같은 단어가 두 가지를 가리키게 되면
V-3(VALIDATION-0001이 기록한 명사형/동사형 이원화)과 같은 종류의
용어 부채가 된다.**

→ 이 명명은 판단 6에서 함께 다룬다.

### Decision

**Accept** — RFC-0006은 새 Component·Layer·Runtime·Service를 도입하지
않는다. **따라서 Reference Layer 개념으로만 판단한다.**

**조건**: "층(Layer)"이라는 명명은 채택하지 않는다(판단 6 참조).

### Next Step

**No ADR Required**

---

## 판단 3. Ownership은 Boundary를 명확하게 하는가, 불필요한 복잡성인가

### Evidence — 명확화된 것 2건 (실측)

| # | 무엇이 명확해졌는가 | 그 전 상태 |
|---|---|---|
| 1 | **Kernel Context의 인스턴스는 호출자의 것이다** | §15.2에 문장으로 존재했으나, §13.1(Context는 Identifier를 갖는다)과 CM-3(Kernel은 생성하지 않는다)을 잇는 근거로 사용된 적이 없었다 |
| 2 | **"전달"이 두 뜻으로 쓰이고 있다** — §11 대응표의 "Context 전달 책임 → Memory"(운반·영속)와 §14.2 PR-1의 "값으로 돌려준다"(반환) | 이 저장소에서 지적된 적이 없다. RFC-0006 §4.1이 처음 드러냈다 |

**#2는 Ownership 논의 과정에서 발견된 것이다.** Ownership을 묻지
않았다면 "전달"의 두 뜻은 계속 섞여 있었을 것이다 — 개념이 실제로
Boundary 검사 도구로 기능했다는 증거다.

### Evidence — 추가되는 비용

- 이 저장소는 **이미 어휘 이원화 부채를 갖고 있다.** VALIDATION-0001
  V-3이 §15의 동사형(Collect/Merge/…)과 §13.2·§14.4의 명사형
  (Builder/Renderer)의 공존을 Minor로 기록했다.
- Ownership을 어휘로 들이면 **세 번째 축**(책임 / 명명 형태 / 소유)이
  생긴다. 이후 모든 문서가 "이것을 책임으로 쓸 것인가 소유로 쓸
  것인가"를 매번 판단해야 한다.

### Decision

**Accept** — Ownership은 Boundary를 **명확하게 한다.**

단, **비용을 함께 기록한다**: 어휘 축이 늘어나는 비용은 실재하며,
그 비용이 승격(판단 5)의 문턱을 높인다.

### Decision Rationale

효용이 추상적 주장이 아니라 **실측 2건**으로 확인되었다. 특히 #2는
Ownership 없이는 발견되지 않았을 모호성이다.

다만 "명확하게 한다"는 것과 "Baseline 어휘가 되어야 한다"는 것은
다른 판단이며, 후자는 판단 5에서 비용과 함께 저울질된다.

### Next Step

**No ADR Required**

---

## 판단 4. Ownership 없이도 Kernel Reference가 충분히 설명 가능한가 (V-1 기준)

**이 판단이 이번 ADC에서 가장 중요하며, RFC-0006의 주장 하나를
정정한다.**

### Evidence

V-1이 요구한 것은 정확히 다음이다.

> `BASELINE.md` §15.1 경계표에 Kernel Context의 Identifier·Metadata
> **입력 경로가 나타날 것**.

**이 요구는 Ownership 개념 없이도 충족될 수 있다.** 경계표에 한 행을
추가하면 된다 — 예컨대 "Kernel Context의 Identifier: 밖에서 들어옴".
그 행은 기존 어휘(경계 / 입력)만으로 작성 가능하다.

**따라서 "Ownership 없이 Kernel Reference를 설명할 수 있는가"의 답은
'설명은 가능하다'이다.**

Ownership이 추가하는 것은 **설명이 아니라 정당화**다.

| | Ownership 없이 | Ownership과 함께 |
|---|---|---|
| 경계표에 행을 넣을 수 있는가 | **예** | 예 |
| 왜 그 행이 그 방향이어야 하는지 설명할 수 있는가 | **아니오** — 임의 결정이 된다 | 예 — 값의 소유자가 정체성을 정한다는 귀결 |
| CM-3(Kernel은 Identifier를 생성하지 않는다)의 **이유**를 말할 수 있는가 | 아니오 — 규칙으로만 존재 | 예 — 남의 것에 이름을 붙일 권한이 없다 |

### RFC-0006의 주장에 대한 정정

RFC-0006 §10은 ADC 채택 기준 1(*"지금 결정하지 않으면 상위
Architecture를 진행할 수 없다"*)이 만족된다고 주장했다.

**이 주장은 부정확하다.** 정확히는 다음과 같이 나뉜다.

| 대상 | 기준 1 만족 여부 |
|---|---|
| **V-1의 해소** | **만족.** VALIDATION-0001 항목 8이 "V-1 해소 전 Component RFC 착수 불가"로 판정했다 |
| **Ownership 개념의 채택** | **불만족.** V-1은 Ownership 없이도 닫을 수 있다 |

이 정정은 판단 5·6의 근거가 된다 — Ownership 승격은 "진행 불가"를
근거로 삼을 수 없다.

### 검토한 반론 (기록)

- **"정당화 없는 결정을 이 프로젝트가 허용해 왔는가"** — 허용하지
  않았다. 모든 ADC가 Evidence 기반 Rationale을 요구한다. 따라서
  Ownership이 제공하는 정당화는 **무가치하지 않다.** 다만 그것이
  "없으면 진행 불가"와 같은 급의 근거는 아니다.
- **"그렇다면 이 RFC는 불필요했는가"** — 아니다. 판단 3의 실측 2건이
  효용을 보였고, 특히 "전달"의 두 뜻은 이 RFC 없이는 드러나지
  않았다.

### Decision

**Accept** — Ownership 없이도 Kernel Reference의 **설명은 가능하다.**
Ownership이 더하는 것은 **정당화**이며, 그것은 채택의 근거가 되되
"진행 불가"의 근거는 되지 못한다.

### Next Step

**No ADR Required**

---

## 판단 5. Ownership을 Baseline Vocabulary로 승격할 것인가

### Evidence

**승격을 지지하는 것**

- 개념 구분이 실재한다(판단 1, Evidence 5건).
- Boundary 명확화 효용이 실측되었다(판단 3, 2건).

**승격을 지지하지 않는 것**

- **사용 횟수 1회.** Ownership이라는 어휘가 사용된 문서는 RFC-0006
  하나이며, 그 RFC는 아직 어떤 후속 문서에도 적용된 적이 없다.
- **"진행 불가" 근거가 성립하지 않는다**(판단 4).
- **어휘 축이 늘어난다**(판단 3의 비용). 저장소는 이미 V-3(명사형/
  동사형 이원화) 부채를 갖고 있다.
- `ARCHITECTURE_GOVERNANCE.md` ADC 채택 기준 2개 중 **어느 것도
  만족하지 않는다** — 기준 1은 판단 4에서 불만족으로 확인되었고,
  기준 2("결정이 늦어질수록 되돌리는 비용이 매우 커진다")는 어휘
  하나를 나중에 도입하는 비용이 크다는 근거가 없다.
- **선례**: ADC-0002 판단 2b가 4-Layer Context Model을 Defer한 근거는
  *"이 프로젝트에서 단 한 번도 관찰된 적이 없는 구조를 확정하는
  것"*이었다. Ownership 어휘도 아직 한 문서에서만 사용되었다.

### 검토한 반론 (기록)

- **"어휘를 등재하지 않으면 다음 문서들이 제각기 다른 의미로
  Ownership을 쓰게 되지 않는가"** — 실재하는 위험이나, 그것은 **어휘가
  실제로 반복 사용될 때** 발생한다. 지금은 사용 1회다. 두 번째 사용이
  나타나면 그 시점이 재검토 조건이 된다.
- **"판단 1에서 개념 구분을 Accept했는데 어휘를 등재하지 않는 것이
  모순인가"** — 모순이 아니다. **결론은 기존 어휘(책임 / 값 / 경계 /
  호출자)로 전부 표현 가능하다** — RFC-0006 §0.3이 8개 근거로 이를
  보였다. 개념이 참인 것과 그 이름을 Baseline에 새기는 것은 다른
  판단이다.

### Decision

**Defer**

Ownership은 **RFC 단계에 남긴다.** Baseline 어휘로 등재하지 않는다.

**재검토 조건**: Ownership이라는 어휘가 **두 번째 문서에서 실제로
필요해질 때** — 즉 기존 어휘(책임/값/경계)로 표현하려다 실패하는
사례가 한 번 더 관찰될 때.

### Decision Rationale

ADC 채택 기준 2개 중 어느 것도 만족하지 않는다. 사용 1회 시점에
어휘를 확정하는 것은 ADC-0002 판단 2b가 4-Layer를 Defer한 상황과
같으며, 같은 판단이 적용되어야 한다.

**Defer해도 잃는 것이 없다**: RFC-0006의 결론은 기존 어휘로 전부
표현되므로, V-1을 닫는 후속 작업이 이 Defer 때문에 막히지 않는다.

### Next Step

**No ADR Required**

---

## 판단 6. Ownership 3층(내용/형식/인스턴스)은 이번 ADC의 판단 대상인가

성격이 다른 두 가지를 분리한다.

- **6a**: 3층이 **말하는 결론** — 내용은 HQ, 형식은 Kernel, 인스턴스는
  호출자
- **6b**: 3층이라는 **명명과 구조화** — O-1/O-2/O-3 라벨, "층"이라는 틀

### 6a. 결론

#### Evidence — 결론은 전부 기존 결정의 재진술이다

| 결론 | 이미 있는 곳 |
|---|---|
| 내용은 HQ의 것 | §13.5, CM-4, §14.2 PR-1의 "제공 ≠ 내용 마련" |
| 형식은 Kernel의 것 | §13.2(검증·병합·정렬), §13.3(A-1~A-5, O-1~O-4), §14.3(G-1~G-7) — **다만 "Kernel이 형식을 결정한다"는 한 문장으로 모인 적은 없다** |
| 인스턴스는 호출자의 것 | §15.2 *"Kernel Context를 보관한다는 것은 호출자가 그 값을 들고 있는 것"*, G-7, N-4, §13.1(값) |

3개 중 2개는 문장으로 이미 존재하고, 1개(형식)는 여러 절에 분산되어
있으나 새 내용이 아니다.

#### Decision

**Accept** — 단 **기존 결정의 재진술로서만** Accept한다.

이 Accept는 **새 결정을 만들지 않으며**, Baseline에 새 문장을
추가할 것을 요구하지 않는다(판단 8 참조).

#### Decision Rationale

결론이 재진술이므로 채택 비용이 없다. 동시에 재진술이므로 **Baseline에
중복 기록할 이유도 없다** — `ARCHITECTURE_GOVERNANCE.md`의 Single
Source of Truth 원칙에 따른다.

### 6b. 명명과 구조화

#### Evidence

- 판단 2에서 기록한 **명명 위험**: "층(Layer)"이 `BASELINE.md` §5
  Meta Architecture의 계층과 같은 단어를 쓴다.
- 판단 5에서 Ownership 어휘 자체가 Defer되었다. 어휘가 Defer된 상태에서
  그 어휘의 하위 구조(O-1/O-2/O-3)를 확정하는 것은 순서가 맞지
  않는다.
- 3층 분류가 **다른 대상에도 적용되는지 관찰된 바 없다.** RFC-0006은
  Kernel Context 하나에만 적용했다. 분류 체계로 승격하려면 최소 2회
  적용이 필요하다는 것이 이 저장소의 반복된 기준이다(RT-0001의
  Trigger 형식, ADC-0002 판단 2b).

#### Decision

**Defer** — **후속 RFC로 미룬다.**

**재검토 조건**: (a) 판단 5의 Ownership 어휘 Defer가 해제되고,
(b) 3층 분류가 Kernel Context 외의 대상에도 적용되는 사례가 관찰될
때.

#### Decision Rationale

사용자가 제시한 원칙(*"Ownership 3층 구조는 이번 ADC에서 채택하지
않아도 된다. 필요하면 별도 RFC로 남긴다"*)과, 이 저장소의 기존 판단
기준(관찰 2회 미만이면 분류 체계를 확정하지 않는다)이 같은 방향을
가리킨다.

**"층"이라는 명명 자체도 후속 RFC에서 재검토되어야 한다** —
Architecture Layer와의 혼동 위험이 있다.

#### Next Step

No ADR Required

---

## 판단 7. §11 문언 변경이 필요한가

### Evidence

**§11 대응표의 실제 문언을 확인했다** (연구자가 원문에서 직접 확인).

```
| Kernel 책임 | 구현 후보 |
| Context 전달 책임 | Memory |

> 위 표의 Component는 예시이며, 채택 여부는 결정되지 않았다.
> 각 책임이 실제로 Kernel에 속하는지는 개별 RFC로 판단한다.
```

**결정적 사실**: §11의 표에는 **"예시이며 채택 여부는 결정되지
않았다"**는 단서가 이미 붙어 있다. 즉 §11은 *"Context 전달 = 운반·
영속"*이라고 **주장하지 않는다** — 미결 책임 하나와 구현 후보 하나를
짝지어 놓았을 뿐이다.

따라서 RFC-0006 §4.1이 지적한 모호성은 **§11의 결함이 아니라, §11의
미결 상태가 §14.2 PR-1의 확정 상태와 나란히 놓였을 때 생기는
읽기상의 혼동**이다.

**Frozen 변경의 정당성 기준** (B-3, 그리고 ADR-0005 선례):

- ADR-0005가 §10을 변경할 때의 근거는 *"그 문언을 유지하면 다음
  단계를 진행할 수 없다"*였다 — 배선도가 §10의 문언에 정면으로
  해당했기 때문이다.
- **§11의 경우 그런 차단이 없다.** §11을 그대로 두어도 V-1 해소,
  Ownership 논의, Component RFC 어느 것도 막히지 않는다.
- VALIDATION-0001은 §10 변경에 대해 *"경계 조정의 선례가 생겼다"*를
  Drift 위험으로 기록했고, ADC-0005 판단 1 조건 3이 *"이번 Accept를
  다음 단계의 선례로 삼지 않는다"*를 명시했다.

### 검토한 반론 (기록)

- **"모호성이 실재하는데 방치하는가"** — 방치하지 않는다. 모호성은
  RFC-0006 §4.1과 이 ADC에 **기록**되었다. 기록과 문언 변경은 다른
  조치이며, 기록만으로 충분한지는 그 모호성이 실제 오독을 일으켰는지에
  달렸다 — **오독 사례는 관찰된 적이 없다.**
- **"나중에 §11을 고쳐야 한다면 지금 고치는 것이 싸지 않은가"** —
  §11의 해당 행은 "Context 전달 책임"이 Kernel에 속하는지 자체가
  미결이다(RFC-0002 §15-4는 결정되었으나 §11 표의 구현 후보는 미결).
  그 미결이 풀릴 때 표 전체가 다시 다뤄질 가능성이 높으므로, 지금
  부분 수정하는 것이 더 싸다는 근거가 없다.

### Decision

**Reject** — §11 문언 변경은 **필요하지 않다.**

근거: (a) §11은 모호한 주장을 하고 있지 않다 — "예시이며 미결"이라는
단서가 이미 붙어 있다, (b) §11을 유지해도 어떤 후속 작업도 막히지
않는다, (c) 따라서 **Frozen 변경의 정당성이 충분하지 않다**(B-3).

**대신 기록으로 남긴다**: "전달"이 두 뜻으로 읽힐 수 있다는 사실은
RFC-0006 §4.1과 이 ADC 판단 7에 기록되었다. 실제 오독이 관찰되면 그때
재검토한다.

### Decision Rationale

Frozen 문언 변경은 이 저장소에서 **한 번만** 일어났고(ADR-0005 §10),
그때의 근거는 "유지하면 진행 불가"였다. §11에는 그 근거가 없다.
근거 없이 두 번째 변경을 허용하면 VALIDATION-0001이 기록한 "경계
조정의 선례" 위험이 현실화된다.

### Next Step

No ADR Required

---

## 판단 8 (부수). 이 ADC는 Baseline을 변경하는가

판단 1~7의 결과를 모으면 다음과 같다.

| 판단 | 결과 | Baseline 변경을 요구하는가 |
|---|---|---|
| 1. 개념 구분 | Accept | **아니오** — 개념 확인이며 어휘 등재 아님 |
| 2. Component 미도입 | Accept | 아니오 |
| 3. Boundary 명확화 | Accept | 아니오 |
| 4. 설명 가능성 | Accept(정정 포함) | 아니오 |
| 5. 어휘 승격 | **Defer** | 아니오 |
| 6a. 3층의 결론 | Accept(재진술) | **아니오** — 재진술이므로 중복 기록하지 않는다(Single Source of Truth) |
| 6b. 3층의 명명·구조 | **Defer** | 아니오 |
| 7. §11 문언 변경 | **Reject** | 아니오 |

### Decision

**이 ADC는 Baseline을 변경하지 않는다. 따라서 ADR이 필요하지 않다.**

### 이것이 뜻하는 것 — 정직하게 기록한다

**V-1은 이 ADC로 닫히지 않는다.**

- V-1이 요구한 것은 §15.1 경계표에 입력 경로가 나타나는 것이다.
- 그 행을 쓰려면 OQ-1(Identifier가 호출자 주입인가 형식으로부터의
  파생인가)에 답해야 하는데, **그것은 이 ADC의 범위가 아니며 H-5
  (Defer)와 맞물려 있다**(B-2).
- 따라서 `VALIDATION-0001` 항목 8의 판정("V-1 해소 전 Component RFC
  착수 불가")은 **여전히 유효하다.**

이 ADC가 한 일은 **V-1을 닫은 것이 아니라, V-1을 닫을 때 그 결정이
무엇에서 도출되어야 하는지를 정한 것**이다.

---

# 판단 결과 요약

| # | 판단 | Decision |
|---|---|---|
| 1 | Ownership과 Responsibility를 다른 개념으로 채택 | **Accept** (개념 구분에 한정) |
| 2 | 새 Component·Layer·Runtime·Service 도입 여부 | **Accept** (도입 없음, Reference Layer 개념으로만 판단) |
| 3 | Boundary 명확화 vs 불필요한 복잡성 | **Accept** (명확화한다, 비용 기록) |
| 4 | Ownership 없이 설명 가능한가 | **Accept** (설명 가능. 더하는 것은 정당화) |
| 5 | Baseline Vocabulary 승격 | **Defer** (RFC 단계에 남김) |
| 6a | Ownership 3층의 **결론** | **Accept** (기존 결정의 재진술로서만) |
| 6b | Ownership 3층의 **명명·구조화** | **Defer** (후속 RFC) |
| 7 | §11 문언 변경 | **Reject** (Frozen 변경 정당성 불충분) |

**Accept 5 / Defer 2 / Reject 1.**

이 ADC에서 **Reject가 나온 것은 처음이다**(ADC-0002~0005는 전부
Accept 또는 Defer였다). §11 문언 변경 요구가 Frozen 변경 기준(B-3)을
통과하지 못했다.

**RFC-0006의 주장 1건을 정정했다**: §10의 "ADC 채택 기준 1 만족"
주장은 V-1 해소에 대해서는 성립하나 Ownership 채택에 대해서는
성립하지 않는다(판단 4).

---

# Evidence Summary

| ID | Evidence | 출처 | 어느 판단에 쓰였는가 |
|---|---|---|---|
| E-1 | 5개 Builder가 Artifact를 만들되 식별자·시각을 전부 호출자로부터 주입받음 (9개 MVP 반복) | `ARTIFACT-STANDARD-v1.md` | 판단 1 |
| E-2 | 5개 MVP 전체에서 시계·난수 부재가 테스트로 확인됨 | 동일 | 판단 1 |
| E-3 | CM-3 — Kernel은 Identifier를 생성하지 않는다 | `BASELINE.md` §13.1 | 판단 1, 4 |
| E-4 | §13.5 — HQ가 무엇을, Kernel이 어떻게 | §13.5 | 판단 1, 6a |
| E-5 | §14.4 Hidden 효력 — 변경 권한에 대한 진술 | §14.4 | 판단 1 |
| E-6 | §15.2 — *"호출자가 그 값을 들고 있는 것"* | §15.2 | 판단 3, 6a |
| E-7 | §11 대응표에 *"예시이며 채택 여부는 결정되지 않았다"* 단서가 이미 존재 | §11 | **판단 7 (Reject의 결정적 근거)** |
| E-8 | ADR-0005의 §10 변경 근거는 "유지하면 진행 불가"였음 | ADR-0005 | 판단 7 |
| E-9 | VALIDATION-0001 항목 8 — "V-1 해소 전 Component RFC 착수 불가" | VALIDATION-0001 | 판단 4, 8 |
| E-10 | VALIDATION-0001 V-3 — 명사형/동사형 어휘 이원화 부채가 이미 존재 | VALIDATION-0001 | 판단 3, 5 |
| E-11 | ADC-0002 판단 2b — 관찰되지 않은 taxonomy는 확정하지 않는다 | ADC-0002 | 판단 5, 6b |
| E-12 | ADC 채택 기준 2개 | `ARCHITECTURE_GOVERNANCE.md` | 판단 5 |

**새로 만든 Evidence는 없다.** 모든 항목이 기존 문서·소스에 이미
기록되어 있던 사실이다.

---

# Baseline 영향 여부

## **영향 없음.**

- `docs/01_architecture/BASELINE.md` — **변경 없음.** §11(판단 7
  Reject), 어휘 등재 없음(판단 5 Defer), 재진술 중복 기록 없음(판단
  6a).
- `docs/00_governance/GLOSSARY.md` — **변경 없음**(판단 5 Defer).
- `development-hq/**`, `core/execution_layer/**` — **영향 없음.**

RFC-0006 §8이 나열한 "영향받을 수 있는 문서 7건"은 **이번 ADC의
판단 결과로 전부 영향 없음이 되었다.**

---

# ADR 필요 여부

## **필요하지 않다.**

`docs/04_adr/README.md`가 정의한 대로 ADR은 *"ADC 중 NOW로 분류되어
실제로 결정된 사항을 기록하는 문서"*이며, 그 결과는 Baseline에
반영된다. 이 ADC는 Baseline을 변경하지 않으므로 반영할 것이 없다.

Accept된 5건은 **개념의 확인·정정·재진술**이며 새 Baseline 문장을
만들지 않는다. Defer 2건과 Reject 1건도 마찬가지다.

---

# Open Questions

RFC-0006이 남긴 6건의 상태를 갱신하고, 이 ADC가 추가한 것을 더한다.

| ID | 질문 | 이 ADC 이후 상태 |
|---|---|---|
| OQ-1 | Kernel Context의 Identifier는 호출자 주입인가, 형식으로부터의 파생인가 | **열림. 가장 시급하다** — V-1 해소의 전제이며 Component RFC를 막고 있다. H-5(Defer)와 맞물린다 |
| OQ-2 | Context Metadata의 출처는 Identifier와 같아야 하는가 | 열림. OQ-1과 함께 다루는 것이 자연스럽다 |
| OQ-3 | §11의 "Context 전달 책임" 두 뜻을 구분할 것인가 | **판단 7에서 Reject로 답했다.** 실제 오독이 관찰되면 재검토 |
| OQ-4 | 운반·영속 전달은 Kernel의 책임인가 | 열림. Memory Module Defer(Kernel ADC-0001)와 직결 |
| OQ-5 | Ownership을 Baseline 어휘로 등재할 것인가 | **판단 5에서 Defer로 답했다.** 재검토 조건: 두 번째 문서에서 실제로 필요해질 때 |
| OQ-6 | 오래 보관된 Kernel Context를 나중에 쓰는 것이 유효한가 | 열림. Artifact Drift(`docs/core/execution-layer/RFC-0001`)와 같은 종류 |
| **OQ-7** | **"층(Layer)"이라는 명명을 Ownership 분류에 쓸 수 있는가** | **신규.** `BASELINE.md` §5 Meta Architecture의 계층과 같은 단어다. 판단 6b의 후속 RFC에서 함께 다뤄야 한다 |
| **OQ-8** | **V-1을 닫는 최소 변경은 무엇인가** | **신규.** 판단 4가 "Ownership 없이도 경계표 행 추가로 가능"함을 확인했다. 그 행이 OQ-1의 답 없이 작성 가능한지(예: 두 후보를 모두 허용하는 형태)가 다음 RFC의 첫 질문이 된다 |

---

## Self Review

- Evidence만 사용했는가 — **Pass**. 12개 Evidence 전부 기존 문서·
  소스에 기록되어 있던 사실이며, 특히 판단 7의 결정적 근거(E-7,
  §11의 "예시이며 미결" 단서)는 원문에서 직접 확인했다. 새 실험을
  하지 않았다.
- 일괄 승인했는가 — **아니오**. 7개 판단(8개 항목)으로 분리했고
  Accept 5 / Defer 2 / Reject 1이다.
- RFC를 무비판적으로 통과시켰는가 — **아니오**. 판단 4가 RFC-0006
  §10의 "ADC 채택 기준 1 만족" 주장을 **정정**했고, 판단 7이 RFC가
  제기한 §11 변경 가능성을 **Reject**했으며, 판단 2가 "층" 명명
  위험을 새로 발견했다.
- Ownership을 구현했는가 — **아니오**.
- Identifier·Metadata 출처를 결정했는가 — **아니오**. OQ-1·OQ-2로
  열어 두었다(B-2 유지).
- Memory·Scheduler·Registry·Execution Layer·API·Component를
  설계했는가 — **아니오**. Memory는 판단 7·OQ-4에서 **미결 영역의
  이름으로만** 인용했다.
- Frozen 문언을 변경했는가 — **아니오**. 판단 7이 정당성 불충분으로
  Reject했다.
- Defer를 해제했는가 — **아니오**. H-5, Memory Module, §13.6·§14.7
  전부 그대로다.
- 새 Component·Layer·Concept를 만들었는가 — **아니오**. 판단 2에서
  전수 확인했고, 판단 5·6b가 어휘와 구조를 Defer해 새 Concept 등재를
  막았다.
- V-1을 닫았다고 주장하는가 — **아니오**. 판단 8이 닫히지 않았음과
  그 이유를 명시했다.
- ADR을 작성했는가 — **아니오**. ADR이 필요하지 않다고 판정했다.
