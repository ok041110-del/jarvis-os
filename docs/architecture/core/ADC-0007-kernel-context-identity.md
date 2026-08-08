# ADC-0007: Kernel Context Identity 검토 (RFC-0007 후속)

## 목적

**이 ADC는 Identity를 채택하는 문서가 아니다.**

`docs/architecture/core/RFC-0007-kernel-context-identity.md`의 **핵심
주장이 현재 Evidence로 정당화되는지**를 판단한다.

> RFC-0007의 핵심 주장: **"Identity가 V-1을 설명하는 핵심 개념이다.
> Identity 없이는 V-1이 닫히지 않는다."** (RFC-0007 §6.2·§6.3)

**RFC는 주장이고 ADC는 그 주장을 Evidence로 검증하는 단계다. 이 ADC는
RFC-0007의 결론을 사실로 가정하지 않는다.**

### 이 ADC가 지키는 검증 형식

```
Observation  (문서·소스에 실제로 기록된 사실)
    ↓
Interpretation  (그 사실로부터의 추론)
    ↓
Conclusion  (주장)
```

**Observation이 Conclusion을 직접 증명하지 않으면 Accept하지 않는다.**
추론을 사실로 승격하지 않는다.

### 금지 사항 준수

Identity를 정의하지 않는다. Identifier 생성 방식을 결정하지 않는다.
UUID·Hash·Composite Key·Metadata·Memory·Runtime·Execution Layer·
Component·API·Implementation을 논의하지 않는다.

---

## 판단 1 (가장 중요). Identity는 V-1의 원인인가, 가능한 해석 중 하나인가

### 1.1 RFC-0007의 주장 사슬을 분해한다

| 단계 | 내용 | 성격 |
|---|---|---|
| **O-1** | `BASELINE.md` §13.1이 Context Identifier를 *"Context 또는 Segment의 **동일성 판정 기준**"*으로 정의한다 | **Observation** (원문 확인) |
| **O-2** | CM-3이 같은 대상에 대해 *"Kernel은 스스로 **생성하지 않는다.** 호출자가 주입하거나 결정론적으로 파생한다"*고 제약한다 | **Observation** (원문 확인) |
| **I-1** | O-1은 관계(판정 기준)에 대한 진술이고 O-2는 값에 대한 진술이므로, 한 이름 아래 두 개념이 놓여 있다 | **Interpretation** |
| **I-2** | 따라서 ADC-0006 OQ-1의 두 후보(주입/파생)는 값의 선택지가 아니라 판정 기준의 선택지다 | **Interpretation** |
| **C-1** | 그러므로 **Identity를 정하지 않으면 두 후보 중 하나를 고를 수 없고, V-1은 닫히지 않는다** | **Conclusion** |

**O-1과 O-2는 사실이다.** I-1도 문언 대조로 뒷받침된다.

**문제는 I-2 → C-1이다.** 이 단계는 관찰이 아니라 추론이며, 이 ADC는
그것이 직접 증명되는지를 검증해야 한다.

### 1.2 반증 시도 1 — 두 후보를 Identity 없이 고를 수 있는가

C-1이 성립하려면 **"두 후보가 Evidence상 대등해서 이론적 기준 없이는
고를 수 없다"**는 전제가 필요하다.

**이 전제는 Evidence와 충돌한다.**

| Observation | 출처 |
|---|---|
| 호출자 주입 사례: `request_id`·`created_at`(MVP-0003), `handle_id`·`submitted_at`(MVP-0004), `handle_id`·`state`·`changed_at`(MVP-0005) — **9개 MVP에 걸쳐 반복** | `ARTIFACT-STANDARD-v1.md` |
| 5개 MVP 전체에서 `uuid.uuid4`/`datetime.now`/`time.time` 부재가 **테스트로 확인됨** | 동일 문서 |
| **파생 사례: 0건.** *"내용 해시로 식별자를 만든 사례는 이 저장소에 존재하지 않는다"* | `ADC-0003` 판단 1b, 원문 확인 |

**관찰 9 대 0이다.** 두 후보는 대등하지 않다.

따라서 **"어느 쪽인지 고를 수 없다"가 아니라 "한쪽만 관찰되었다"**가
현재 상태이며, 선택이 필요하다면 **선례를 근거로** 할 수 있다 —
Identity 이론 없이도 가능하다.

### 1.3 반증 시도 2 — 선행 ADC가 이미 반대로 판단했다

**결정적 Observation이다.**

`ADC-0003` 판단 1b는 파생 규칙을 Defer하면서 그 이유를 이렇게
기록했다(원문 확인).

> *"고르지 않아도 **상위 설계가 막히지 않는다** — 판단 1의 Model은
> Identifier를 '값 하나'로만 규정하므로 어느 규칙이든 나중에 들어올
> 수 있다."*

**RFC-0007의 C-1은 이 판단과 정면으로 반대된다.** 그런데 RFC-0007은
그 사이에 새로 관찰된 사실을 제시하지 않았다 — O-1·O-2는 둘 다
v1.2 시점부터 존재하던 문언이며, ADC-0003 판단 1b 당시에도 있었다.

**선행 판단을 뒤집으려면 그 이후의 새 Observation이 필요하다. 없다.**

### 1.4 반증 시도 3 — V-1의 원래 요구를 다시 읽는다

`VALIDATION-0001` V-1이 요구한 것은 다음이다(원문 확인).

> §15.1 경계표에 Kernel Context의 Identifier·Metadata **입력 경로가
> 나타날 것.**

그리고 차단 근거는 *"Assemble 책임의 입력이 정의되지 않으면 그 책임을
구현할 후보를 논할 수 없다"*였다.

**"입력 경로를 적는 것"과 "판정 기준을 정하는 것"은 다른 일이다.**
전자는 경계표의 한 행이고, 후자는 개념 정의다. RFC-0007 §6.2는
전자를 후자에 의존시켰으나, **그 의존이 필연이라는 Observation은
없다** — 9 대 0의 선례를 근거로 행을 쓰는 경로가 존재하기 때문이다
(§1.2).

### 1.5 그렇다면 RFC-0007의 O-1·I-1은 무가치한가

**아니다.** 이 ADC는 다음을 구분한다.

| 주장 | 판정 |
|---|---|
| §13.1이 Identity 문언으로 쓰여 있고 CM-3이 Identifier에 걸려 있다(O-1·O-2·I-1) | **사실이다** — 아래 판단 2에서 다룬다 |
| 그 사실이 **V-1의 원인**이다(C-1) | **입증되지 않았다** |

**RFC-0007이 발견한 것은 실재하는 문언상의 이중성이지, V-1의
인과가 아니다.**

### Decision

## **Reject**

Reject되는 것: **"Identity가 V-1의 원인이며, Identity 없이는 V-1이
닫히지 않는다"**는 주장(C-1).

Reject되지 **않는** 것: O-1·O-2·I-1 — 문언상의 이중성은 실재하며,
이 ADC는 그것을 사실로 인정한다(판단 2 참조).

### Decision Rationale

세 가지 이유가 각각 독립적으로 C-1을 무너뜨린다.

1. **두 후보가 대등하지 않다** — 관찰 9 대 0(§1.2). "고를 수 없다"는
   전제가 성립하지 않는다.
2. **선행 ADC가 반대로 판단했고, 그 이후 새 Observation이 없다**
   (§1.3). ADC-0003 판단 1b는 *"고르지 않아도 상위 설계가 막히지
   않는다"*고 명시했다.
3. **V-1의 요구는 경계표의 행이지 개념 정의가 아니다**(§1.4).

**Identity는 V-1을 설명하는 가능한 해석 중 하나이며, 유일한 해석도
필연적 원인도 아니다.**

이는 ADC-0006 판단 4가 Ownership에 대해 내린 것과 **같은 구조의
판정**이다 — 그때는 RFC의 주장을 "정정"했고, 이번에는 주장이 선행
판단과 정면 충돌하므로 Reject한다.

### Risks

이 Reject가 틀렸을 가능성: 만약 향후 Context를 **비교·재사용하는
사례**가 실제로 나타나면(ADC-0003 판단 1b가 제시한 바로 그 조건),
값의 동일성만으로는 부족하다는 관찰이 생길 수 있다. 그때 C-1은 새
Evidence를 얻는다. **이 Reject는 "Identity가 무의미하다"가 아니라
"지금 그것을 V-1의 원인으로 삼을 근거가 없다"이다.**

### Next Step

No ADR Required

---

## 판단 2. Identity와 Identifier를 Architecture에서 구분해야 하는가

### Evidence

| ID | Observation | 출처 |
|---|---|---|
| O-1 | §13.1: *"동일성 판정 기준"* — 관계에 대한 문언 | 원문 |
| O-2 | CM-3: *"생성하지 않는다"* — 값에 대한 제약 | 원문 |
| O-3 | §13.2 병합·검증이 Identifier와 Content **양쪽의 동등 관계**를 요구 | 원문 |
| O-4 | O-2(O-2 tie-break)가 Identifier의 **전순서**까지 요구 | 원문 |
| O-5 | 현재 코드의 동일성 판정은 전부 **문자열 동일**이며, 그것이 선택된 기록은 없다 | `project_intelligence.py:143-144`, `core/execution_layer/*/tests/` |
| O-6 | **이 이중성 때문에 실제로 오류가 발생한 사례: 0건** | 전 저장소 검색 |

### Interpretation과 Evidence의 구분

| 진술 | 성격 |
|---|---|
| "한 이름 아래 두 성격의 문언이 있다" | **Observation**(O-1+O-2 대조) |
| "그 이중성이 혼동을 일으킬 수 있다" | **Interpretation** — 가능성이지 관찰이 아니다 |
| "따라서 Architecture에서 구분해야 한다" | **Conclusion** — O-6(오류 0건)이 이를 뒷받침하지 않는다 |

### 검토한 반론 (기록)

- **"오류가 없었다고 구분이 불필요한가"** — 불필요하다고 판정하지
  않는다. **아직 필요성이 입증되지 않았다**고 판정한다. 이 저장소는
  같은 기준을 반복 적용해 왔다 — ADC-0002 판단 2b(관찰되지 않은
  taxonomy 확정 안 함), ADC-0003 판단 1b(관찰 없는 규칙 확정 안 함),
  ADC-0006 판단 5(사용 1회 어휘 승격 안 함).
- **"O-3·O-4는 실제 공백 아닌가"** — **맞다. 그것은 사실이다.**
  다만 그 공백이 드러내는 것은 *"동일성 기준이 명시된 적 없다"*이지
  *"Identity와 Identifier를 개념적으로 분리해야 한다"*가 아니다. 두
  진술은 다르다 — 전자는 기준 하나를 적으면 해소되고, 후자는 어휘
  체계를 하나 더 만든다.

### Decision

## **Defer**

- **Accept되는 사실**: §13.1과 CM-3 사이에 문언상 이중성이 실재한다
  (O-1·O-2). 그리고 §13.2·O-2가 의존하는 동일성 기준이 명시된 적이
  없다(O-3·O-4·O-5).
- **Defer되는 것**: 그 사실을 근거로 Identity와 Identifier를
  **Architecture 차원에서 구분 장치로 채택**하는 것.

**재검토 조건**: 이 이중성 때문에 **실제 오독·오구현·판단 오류가 1회
이상 관찰될 때**, 또는 문자열 동일이 아닌 동일성 기준이 필요한 사례가
관찰될 때.

### Decision Rationale

O-6(오류 0건)이 결정적이다. 구분의 **실질적 가치**는 그것이 막아 준
문제로만 입증되는데, 막아야 할 문제가 아직 관찰되지 않았다.

### Next Step

No ADR Required

---

## 판단 3. Identity는 Reference Layer의 개념인가, Component Layer의 개념인가

### Evidence

**이미 결정된 절반**

| Observation | 출처 |
|---|---|
| 표기 값의 **생성 방식**은 Reference의 문제가 아니다 — H-5가 Hidden으로 두었고 ADC-0003 판단 1b가 Defer했다 | `BASELINE.md` §14.4, ADC-0003 |

이 절반은 이미 결정되어 있으므로 새 판단 대상이 아니다.

**미결인 절반**

| 진술 | 성격 |
|---|---|
| "§13.2의 검증·병합이 동일성 기준에 의존한다" | **Observation**(O-3) |
| "따라서 그 기준은 Reference Layer에서 정의되어야 한다" | **Interpretation** — 의존한다는 사실이 *어느 Layer에서 정의되어야 하는가*를 직접 증명하지 않는다 |

**반례가 존재한다**: §13.2는 동일성에 의존하면서도 **지금까지 Reference
수준의 정의 없이 동작해 왔다**(O-5: 문자열 동일이 기본값으로 사용됨,
오류 0건). 즉 "의존한다 → Reference에서 정의되어야 한다"는 함의가
관찰로 뒷받침되지 않는다.

### Decision

## **Defer**

Boundary 판정(Reference인가 Component인가)을 지금 내리지 않는다.

### Decision Rationale

판단 1이 Reject되고 판단 2가 Defer된 상태에서, Boundary 판정은
**선행 근거를 잃는다.** 무엇을 어느 Layer에 둘지는 그것이 무엇인지가
합의된 뒤의 질문이다.

또한 이 판정을 내리려면 `ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준
2개 중 하나를 만족해야 하는데, **둘 다 만족하지 않는다** — 판단 1에서
"진행 불가"가 성립하지 않음이 확인되었고, 되돌리는 비용이 커진다는
근거도 없다.

### Next Step

No ADR Required

---

## 판단 4. Identity를 Architecture Vocabulary로 승격할 Evidence가 있는가

### Evidence

| Observation | 값 |
|---|---|
| "Identity"라는 어휘가 사용된 문서 수 | **1건**(RFC-0007) |
| 그 어휘가 적용된 후속 문서 수 | **0건** |
| 이중성으로 인한 실제 오류 | **0건**(O-6) |
| ADC 채택 기준 1(진행 불가) 만족 | **불만족**(판단 1) |
| ADC 채택 기준 2(되돌리는 비용) 만족 | **불만족** — 어휘를 나중에 도입하는 비용이 크다는 근거 없음 |

**선례**: ADC-0006 판단 5가 "Ownership" 어휘를 **정확히 같은 상태**
(사용 1회, 기준 2개 불만족)에서 Defer했다.

### Decision

## **Defer**

Identity를 Architecture Vocabulary로 승격하지 않는다. **RFC 단계에
남긴다.**

**재검토 조건**: 판단 2의 재검토 조건과 동일 — 이중성으로 인한 실제
문제가 1회 이상 관찰되거나, 두 번째 문서에서 기존 어휘로 표현하려다
실패하는 사례가 나타날 때.

### Decision Rationale

승격 근거가 ADC-0006 판단 5 당시의 Ownership보다 **약하다** —
Ownership은 최소한 Boundary 명확화 효용 2건이 실측되었으나(ADC-0006
판단 3), Identity는 판단 1에서 그 효용 주장(V-1 설명)이 Reject되었다.

### Next Step

No ADR Required

---

## 판단 5. RFC가 새 Layer·Component·Runtime·Service·Memory·Registry·Scheduler·API를 암시하는가

### Evidence (전수 확인)

| 검사 대상 | RFC-0007에서의 등장 | 판정 |
|---|---|---|
| Layer | "Reference Layer"·"Component Layer"는 기존 구분의 인용 | 새 Layer 없음 |
| Component | 설계·명명 없음 | 없음 |
| Runtime | §4.2에서 **배제 논증의 대상**으로만 등장 | 없음 |
| Registry | §4.2에서 **배제 논증의 대상**으로만 등장 | 없음 |
| Scheduler | 등장하지 않음 | 없음 |
| Memory | Out of Scope 목록에만 등장 | 없음 |
| Service | 등장하지 않음 | 없음 |
| API | Out of Scope 목록에만 등장 | 없음 |

**§4.2의 성격을 확인했다.** RFC-0007 §4.2는 *"Kernel이 값을 부여한다"*는
방향이 발급 이력 → 호출 간 상태 → Registry·Runtime을 암시하게 됨을
지적하고, **그 방향이 CM-3·G-7으로 이미 배제되어 있음**을 기록했다.
이는 Component를 설계하는 것이 아니라 **배제된 방향을 설명하는
논증**이다.

### Decision

## **Accept** — 암시하지 않는다.

### Next Step

No ADR Required

---

## 판단 6. RFC가 Reference를 Implementation으로 끌어내렸는가

### Evidence (전수 확인)

| 검사 대상 | 결과 |
|---|---|
| UUID·Hash·Composite Key | **전부 배제 문장에서만** 등장(6회, 모두 "다루지 않는다"·"의존하지 않는다" 문맥) |
| 알고리즘·의사코드·자료구조 | **없음** |
| 함수·시그니처·타입 | **없음** |
| Metadata 구조 | 없음 |

RFC-0007 §7이 결정하지 않는 것을 6개 항목으로 명시했고, Identity의
**내용**(구조적인지 지명적인지)조차 OQ-1'로 열어 두었다.

### Decision

## **Accept** — 끌어내리지 않았다.

### Next Step

No ADR Required

---

## 판단 7. Baseline을 수정하지 않고도 RFC의 문제 제기를 설명할 수 있는가

### Evidence

RFC-0007 §10이 지목한 Frozen 변경 후보는 **`BASELINE.md` §13.1
하나**다.

| 검사 | 결과 |
|---|---|
| §13.1의 문언이 **틀렸는가** | **아니다.** *"동일성 판정 기준"*은 Context Identifier가 하는 일을 정확히 서술한다 |
| §13.1을 유지하면 **막히는 후속 작업이 있는가** | **없다.** 판단 1이 V-1 차단 주장을 Reject했으므로, 막히는 것으로 지목된 유일한 작업이 사라졌다 |
| 문제 제기를 **기록만으로 보존할 수 있는가** | **가능하다.** 이중성(O-1·O-2)과 미명시 공백(O-3·O-4·O-5)은 RFC-0007과 이 ADC에 기록되었다 |

**적용 기준**: ADC-0006 판단 7이 §11 변경을 Reject할 때 사용한 기준을
그대로 적용한다 — *"유지해도 어떤 후속 작업도 막히지 않는다"*, *"실제
오독 사례가 관찰된 적이 없다"*.

**두 기준 모두 §13.1에 그대로 해당한다.**

### Decision

## **Reject**

`BASELINE.md` §13.1을 포함한 어떤 Frozen 문언도 변경하지 않는다.

### Decision Rationale

ADR-0005가 §10을 변경할 때의 근거는 *"유지하면 진행 불가"*였다.
§13.1에는 그 근거가 없으며, 판단 1의 Reject로 그 근거의 유일한 후보
(V-1 차단)마저 사라졌다.

`VALIDATION-0001`이 기록한 "경계 조정의 선례" 위험을 고려하면,
근거 없는 두 번째·세 번째 Frozen 변경은 허용되어서는 안 된다.

### Next Step

No ADR Required

---

# 판단 결과 요약

| # | 판단 | Decision |
|---|---|---|
| **1** | **Identity가 V-1의 원인인가** | **Reject** — 가능한 해석 중 하나이며, 원인임이 입증되지 않았다 |
| 2 | Identity와 Identifier를 Architecture에서 구분할 것인가 | **Defer** — 이중성은 사실로 인정, 구분 채택은 보류 |
| 3 | Identity는 Reference의 개념인가 | **Defer** — 선행 근거 상실 |
| 4 | Architecture Vocabulary 승격 | **Defer** — 사용 1회, 채택 기준 2개 불만족 |
| 5 | 새 Layer·Component·Runtime·Service·Memory·Registry·Scheduler·API 암시 | **Accept** — 암시하지 않는다 |
| 6 | Reference를 Implementation으로 끌어내렸는가 | **Accept** — 끌어내리지 않았다 |
| 7 | Frozen 문언 변경 | **Reject** — 수정 없이 설명 가능하다 |

**Accept 2 / Defer 3 / Reject 2.**

**RFC-0007의 핵심 주장은 Accept되지 않았다.** 다만 그 RFC가 수집한
Observation(§13.1과 CM-3의 이중성, 8개 지점의 미명시 동일성 가정)은
**사실로 인정되어 기록된다.**

---

# Evidence Summary

| ID | Observation | 출처 | 쓰인 판단 |
|---|---|---|---|
| O-1 | §13.1이 Context Identifier를 *"동일성 판정 기준"*으로 정의 | `BASELINE.md` §13.1 | 1, 2, 7 |
| O-2 | CM-3이 같은 대상을 *"생성하지 않는다"*로 제약 | §13.1 | 1, 2 |
| O-3 | §13.2 병합·검증이 Identifier와 Content 양쪽의 동등 관계를 요구 | §13.2 | 2, 3 |
| O-4 | O-2(tie-break)가 Identifier의 전순서까지 요구 | §13.3 | 2 |
| O-5 | 현재 동일성 판정은 전부 문자열 동일이며 선택된 기록이 없다 | `project_intelligence.py:143-144`, 테스트 4건 | 2, 3 |
| **O-6** | **이중성으로 인한 실제 오류: 0건** | 전 저장소 | **2, 4, 7** |
| **O-7** | **호출자 주입 관찰 9건 vs 파생 관찰 0건** | `ARTIFACT-STANDARD-v1.md`, ADC-0003 판단 1b | **1** |
| **O-8** | **ADC-0003 판단 1b: *"고르지 않아도 상위 설계가 막히지 않는다"*** | ADC-0003 원문 | **1** |
| O-9 | V-1의 요구는 *"경계표에 입력 경로가 나타날 것"* | VALIDATION-0001 | 1 |
| O-10 | ADC-0006 판단 5가 사용 1회 어휘를 Defer한 선례 | ADC-0006 | 4 |
| O-11 | ADC-0006 판단 7의 Frozen 변경 Reject 기준 | ADC-0006 | 7 |
| O-12 | UUID·Hash·Composite가 RFC-0007에서 전부 배제 문장에만 등장 | RFC-0007 전수 검색 | 6 |

**O-7과 O-8이 판단 1의 Reject를 결정했다.** 새로 만든 Evidence는
없다.

---

# Evidence와 Interpretation 구분표

**이 표가 이번 ADC의 핵심 산출물이다.**

| # | 진술 | 분류 | 직접 증명되는가 | 처리 |
|---|---|---|---|---|
| 1 | §13.1이 "동일성 판정 기준"으로 쓰여 있다 | **Observation** | — | 사실 인정 |
| 2 | CM-3이 값에 제약을 건다 | **Observation** | — | 사실 인정 |
| 3 | 한 이름 아래 두 성격의 문언이 있다 | **Observation**(1+2 대조) | 예 | 사실 인정 |
| 4 | §13.2·O-2가 동일성 기준에 의존하는데 그 기준이 명시된 적 없다 | **Observation** | 예 | 사실 인정 |
| 5 | 그 이중성이 혼동을 **일으킬 수 있다** | **Interpretation** | 아니오 — O-6(오류 0건) | 판단 2 Defer |
| 6 | ADC-0006 OQ-1의 두 후보는 판정 기준의 선택지다 | **Interpretation** | 아니오 | 판단 1의 검증 대상 |
| 7 | **Identity 없이는 두 후보를 고를 수 없다** | **Interpretation** | **아니오 — O-7(9 대 0)이 반증** | **판단 1 Reject** |
| 8 | **따라서 Identity 없이는 V-1이 닫히지 않는다** | **Conclusion** | **아니오 — O-8이 정면 반증** | **판단 1 Reject** |
| 9 | 판정 기준은 Reference Layer에 속한다 | **Interpretation** | 아니오 — O-5가 반례 | 판단 3 Defer |
| 10 | 표기 값의 생성 방식은 Reference의 문제가 아니다 | **기존 결정의 재진술** | — | 이미 결정됨(H-5) |
| 11 | RFC가 Component를 암시하지 않는다 | **Observation**(전수 검색) | 예 | 판단 5 Accept |
| 12 | RFC가 Implementation으로 내려가지 않았다 | **Observation**(전수 검색) | 예 | 판단 6 Accept |

**Accept된 것은 전부 Observation이거나 전수 검색으로 확인된 사실이다.
Interpretation은 하나도 Accept되지 않았다.**

---

# Baseline 영향 여부

## **영향 없음.**

- `docs/01_architecture/BASELINE.md` — **변경 없음.** §13.1 포함
  어떤 절도 수정하지 않는다(판단 7 Reject).
- `docs/00_governance/GLOSSARY.md` — **변경 없음**(판단 4 Defer).
- `development-hq/**`, `core/execution_layer/**` — **영향 없음.**

RFC-0007 §10이 나열한 "영향받을 수 있는 문서 6건"은 이번 판단으로
**전부 영향 없음**이 되었다.

---

# ADR 필요 여부

## **필요하지 않다.**

ADR은 Baseline에 반영될 결정을 기록하는 문서이며, 이 ADC는 Baseline을
변경하지 않는다.

Accept 2건은 **검증 결과의 확인**(암시 없음 / 끌어내리지 않음)이고,
Reject 2건과 Defer 3건은 어느 것도 Baseline 문장을 만들지 않는다.

---

# Open Questions

| ID | 질문 | 이 ADC 이후 상태 |
|---|---|---|
| **OQ-12** | **V-1을 닫는 근거로 무엇을 쓸 것인가** | **신규이자 가장 시급.** 판단 1이 Identity 경로를 Reject했으므로 다른 근거가 필요하다. §1.2가 기록한 **관찰 9 대 0의 비대칭**이 후보 근거이나, **이 ADC는 그것을 결정하지 않는다**(금지 사항) |
| OQ-1' | 동일성 기준은 구조적인가 지명적인가 | **판단 2·3 Defer로 보류.** 재검토 조건: 이중성으로 인한 실제 문제 관찰 |
| OQ-9 | "같은 Content"란 무엇인가 | **열림.** O-3이 드러낸 실제 공백이며, 이 ADC가 사실로 인정했다. 다만 오류 0건이므로 지금 결정 대상은 아니다 |
| OQ-10 | Identifier의 전순서 기준 | **열림.** O-4. 위와 동일 |
| OQ-11 | "Identity" 어휘 등재 | **판단 4에서 Defer로 답했다** |
| OQ-2 | Context Metadata의 출처 | 이월 |
| OQ-6 | 오래 보관된 Kernel Context의 유효성 | 이월 |
| OQ-8 | V-1을 닫는 최소 변경 | **OQ-12로 흡수** |

**OQ-12가 다음 단계다.** V-1은 여전히 열려 있고, `VALIDATION-0001`
항목 8의 "Component RFC 착수 불가" 판정도 여전히 유효하다. 이 ADC가
한 일은 **V-1을 닫는 잘못된 경로 하나를 제거한 것**이다.

---

## Self Review

- RFC의 결론을 사실로 가정했는가 — **아니오**. 핵심 주장(C-1)을
  세 갈래로 반증 시도했고 Reject했다.
- Observation과 Interpretation을 구분했는가 — **Pass**. 12행 구분표를
  산출물로 제시했고, **Accept된 것은 전부 Observation이다.**
- Interpretation을 Accept했는가 — **아니오**. 12행 중 Interpretation
  4건(5·6·7·9)은 전부 Defer 또는 Reject로 처리했다.
- 선행 판단과의 정합성을 확인했는가 — **Pass**. O-8(ADC-0003 판단
  1b)이 RFC-0007의 주장과 정면 충돌함을 발견했고, 그 사이 새
  Observation이 없음을 확인했다.
- Identity를 정의했는가 — **아니오**.
- Identifier 생성 방식을 결정했는가 — **아니오**. OQ-12에서 관찰
  비대칭을 **사실로 기록**했을 뿐 결정하지 않았다.
- UUID·Hash·Composite·Metadata·Memory·Runtime·Execution Layer·
  Component·API·Implementation을 논의했는가 — **아니오**. 판단 5·6의
  **전수 검사 대상으로만** 언급했다.
- Frozen 문언을 변경했는가 — **아니오**. 판단 7에서 Reject했다.
- Reject가 과한가 — 판단 1은 O-7·O-8 두 개의 독립적 반증에 근거하며,
  §1.5에서 RFC의 Observation은 사실로 인정하고 Risks에서 이 Reject가
  틀릴 조건을 명시했다.
- ADR을 작성했는가 — **아니오**. 필요하지 않다고 판정했다.
