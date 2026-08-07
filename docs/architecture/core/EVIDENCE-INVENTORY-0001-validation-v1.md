# EVIDENCE-INVENTORY-0001: V-1을 Observation만으로 재정의한다

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.**
**대상**: `VALIDATION-0001` Major Finding **V-1**
**목적**: V-1이 **현재 어떤 Observation만으로 정의되는 문제인지**
확인한다. Interpretation을 제거한다.

이 문서는 RFC·ADC·ADR을 작성하지 않는다. Baseline·Concept·Layer·
Component·Implementation을 제안하지 않는다. **새 Observation을 만들지
않는다** — 저장소에 이미 있는 것만 수집한다.

## 분류 규칙

| 분류 | 기준 |
|---|---|
| **Observation (OB)** | 문서의 문언 또는 소스의 내용을 **직접 읽어 확인**할 수 있는 것. 부재도 유한한 범위에서 전수 검색으로 확인되면 Observation이다 |
| **Interpretation (IN)** | 그 사실로부터의 추론·평가·예측 |

---

# 1. V-1에 사용된 Observation 목록

**전부 원문·소스에서 직접 확인했다. 추론을 섞지 않았다.**

## 1.1 §13.1 Model에 관한 것

| ID | Observation | 확인 위치 |
|---|---|---|
| **OB-1** | §13.1의 Model 구조도가 `Context` 아래에 `Context Identifier`와 `Context Metadata`를 **Segment와 나란히** 배치한다 | `BASELINE.md` §13.1 구조도 |
| **OB-2** | §13.1 표: *"Context \| 순서가 정해진 유한한 Context Segment 열과 **그 Identifier·Metadata**"* | 동일 |
| **OB-3** | §13.1 표: *"Context Identifier \| Context 또는 Segment의 **동일성 판정 기준**"* | 동일 |
| **OB-4** | CM-3: *"Kernel은 **Identifier와 시각을 스스로 생성하지 않는다.** 호출자가 주입하거나 결정론적으로 파생한다"* | 동일 |

## 1.2 §13.1 요소의 **사용처**에 관한 것 — 전수 검색 결과

`BASELINE.md` §13 ~ §15(207~760행) 전 구간에서 "Identifier"가 등장하는
**12개 지점을 전수 확인**했다.

| ID | Observation |
|---|---|
| **OB-5** | 12개 중 **구조 선언**은 3건이다 — §13.1 구조도 2행, §13.1 정의 표 2행(OB-1~OB-3) |
| **OB-6** | 12개 중 **금지·미결 기록**은 3건이다 — CM-3, G-7(*"Identifier·시각을 생성하지 않는다"*), H-5·§13.6(*"파생 규칙 Defer"*) |
| **OB-7** | 나머지 6건은 **전부 Segment 수준**이다 — §13.2 검증(*"Identifier 존재·유일성"*), §13.2 병합(*"같은 Identifier + 같은 Content"*), O-2 tie-break, G-2, §15.2 ②의 출력, §15.3 ③↔② |
| **OB-8** | **Context 수준의 Identifier를 읽거나 요구하는 규칙은 §13.2·§13.3·§14·§15 어디에도 없다** |
| **OB-9** | **Context 수준의 Metadata를 읽거나 요구하는 규칙도 없다** — "Metadata"의 조작 규칙은 §13.1 정의와 H-3(내부 표현은 Hidden) 외에 존재하지 않는다 |

**OB-8·OB-9는 유한 범위(§13~§15) 전수 검색으로 확인된 부재이므로
Observation이다.**

## 1.3 §15.1 경계표에 관한 것

| ID | Observation |
|---|---|
| **OB-10** | §15.1 "Kernel 경계선의 배치" 표는 **7행**이다 — Context Source 선언 / Segment의 Content / Ordering Policy 선택 / ①~⑤ / Kernel Context / ⑥Render / Output |
| **OB-11** | 그 7행에 **Context 수준 Identifier·Metadata 행은 없다** |
| **OB-12** | **그 표가 전수 목록이라는 진술은 없다.** 표 앞뒤 어디에도 "이것이 경계를 넘는 전부다"라는 문장이 없다 |
| **OB-13** | §15.2 Data Flow 표의 ⑤ 행은 *"⑤의 출력 \| **Kernel Context** \| 열이 **불변 값**이 됨 \| G-1, G-5"*이며, Identifier를 언급하지 않는다 |

## 1.4 소비 사례에 관한 것

| ID | Observation |
|---|---|
| **OB-14** | Context 수준 Identifier를 사용할 만한 사례(Prompt Cache / Conversation Resume / Context Snapshot / Memory Restore)는 §13.6에 **Defer**로 등재되어 있다 |
| **OB-15** | 그 4개 사례는 이 저장소에서 **관찰된 적이 0회**다(ADC-0003 판단 6b Evidence) |
| **OB-16** | Kernel Renderer는 **0개**다(ADC-0004 판단 5b) |
| **OB-17** | 이 저장소에 **Kernel 구현 코드는 존재하지 않는다.** `core/execution_layer/`(Execution Layer)와 `development-hq/mvp/`만 있다 |

## 1.5 Identifier 값의 출처에 관한 것

| ID | Observation |
|---|---|
| **OB-18** | 호출자 주입 관찰: `request_id`·`created_at`(MVP-0003), `handle_id`·`submitted_at`(MVP-0004), `handle_id`·`state`·`changed_at`(MVP-0005). **9건** |
| **OB-19** | 5개 MVP 전체에서 `uuid.uuid4`/`datetime.now`/`time.time` 부재가 테스트로 확인됨 |
| **OB-20** | 파생(내용 해시) 관찰: **0건.** ADC-0003 판단 1b 원문 — *"내용 해시로 식별자를 만든 사례는 이 저장소에 존재하지 않는다"* |

## 1.6 선행 판단에 관한 것

| ID | Observation |
|---|---|
| **OB-21** | ADC-0003 판단 1b 원문: *"고르지 않아도 **상위 설계가 막히지 않는다**"* |
| **OB-22** | VALIDATION-0001 371행: V-1의 심각도가 **Major**로 기재되어 있고, 사유 칸은 *"Assemble 책임의 **입력 정의가 불완전**하다. 첫 Component RFC가 즉시 부딪힌다"*이다 |
| **OB-23** | VALIDATION-0001 377행: *"책임의 입력이 정의되지 않으면 그 책임을 구현할 후보를 논할 수 없다"* |
| **OB-24** | ADC-0006 판단 4가 Ownership 경로를 정정했고, ADC-0007 판단 1이 Identity 경로를 Reject했다 |
| **OB-25** | V-1과 관련해 **실제 오류·오독·오구현이 관찰된 사례: 0건** |

---

# 2. Observation에서 직접 증명되는 것 / 추론이 필요한 것

## 2.1 직접 증명되는 것

| # | 진술 | 근거 | 증명 |
|---|---|---|---|
| D-1 | §13.1은 Context 수준 Identifier·Metadata를 **구조로 선언한다** | OB-1·OB-2 | 문언 |
| D-2 | §13.1은 Context Identifier를 **"동일성 판정 기준"**으로 정의한다 | OB-3 | 문언 |
| D-3 | CM-3은 Kernel의 **생성을 금지**한다 | OB-4 | 문언 |
| D-4 | **§13.2·§13.3·§14·§15의 어떤 규칙도 Context 수준 Identifier·Metadata를 읽거나 요구하지 않는다** | OB-5~OB-9 | 전수 검색 |
| D-5 | §15.1 경계표에 해당 행이 **없다** | OB-11 | 전수 |
| D-6 | 그 표가 **전수 목록이라는 진술도 없다** | OB-12 | 전수 |
| D-7 | Context 수준 Identifier를 소비할 사례는 **전부 Defer이며 관찰 0회**다 | OB-14·OB-15 | 문언·기록 |
| D-8 | Kernel 구현 코드도 Kernel Renderer도 **존재하지 않는다** | OB-16·OB-17 | 저장소 |
| D-9 | 값의 출처 관찰은 **주입 9 : 파생 0**이다 | OB-18·OB-20 | 기록 |
| D-10 | 선행 ADC가 *"고르지 않아도 상위 설계가 막히지 않는다"*고 기록했다 | OB-21 | 문언 |
| D-11 | V-1과 관련해 **관찰된 실제 오류는 0건**이다 | OB-25 | 전수 |

## 2.2 추론이 필요한 것

| # | 진술 | 필요한 추가 전제 | 그 전제가 관찰되는가 |
|---|---|---|---|
| **R-1** | "경계표에 행이 없다 **= 결손이다**" | 경계표가 **전수 목록**이어야 한다 | **아니오** — D-6이 반대를 보인다 |
| **R-2** | "Context Identifier는 **Assemble의 입력이다**" | 어떤 규칙이 그것을 요구해야 한다 | **아니오** — D-4가 반대를 보인다 |
| **R-3** | "따라서 Assemble 책임의 **입력 정의가 불완전하다**"(OB-22) | R-1 또는 R-2 | **아니오** |
| **R-4** | "따라서 **Component RFC 착수가 불가하다**"(OB-23) | R-3 + 미래 예측 | **아니오** — D-8상 착수 대상 코드가 아직 없다 |
| **R-5** | "V-1의 심각도는 **Major**다"(OB-22) | R-3·R-4 | **아니오** |
| **R-6** | "Ownership이 V-1을 설명한다" | — | **ADC-0006에서 정정됨** |
| **R-7** | "Identity가 V-1의 원인이다" | — | **ADC-0007에서 Reject됨** |

**R-1 ~ R-5는 전부 추론이며, 그 전제 중 어느 것도 관찰되지 않는다.**

---

# 3. Ownership 재분류

| 대상 | 분류 | 근거 |
|---|---|---|
| "만드는 쪽과 정하는 쪽이 다른 사례가 9개 MVP에 걸쳐 반복되었다" | **Observation** | OB-18·OB-19 |
| §13.5·§15.2·CM-3·CM-4의 각 문언 | **Observation** | 문언 |
| **"Ownership"이라는 개념** | **Interpretation** | 저장소 어디에도 관찰된 적 없다. 위 Observation들을 묶어 설명하기 위해 RFC-0006이 도입한 **설명 틀**이다 |
| "Ownership이 V-1을 설명한다" | **Interpretation** | ADC-0006 판단 4가 *"V-1은 Ownership 없이도 닫을 수 있다"*로 정정 |

> **재분류 결과: Ownership은 Interpretation이다.** 그것이 묶어 설명한
> 개별 사실들은 Observation이지만, 개념 자체는 관찰이 아니다.
> ADC-0006이 판단 1에서 Accept한 것도 *"개념적 구분의 확인"*이었고
> 어휘 등재는 Defer했다 — 이 재분류와 일치한다.

---

# 4. Identity 재분류

| 대상 | 분류 | 근거 |
|---|---|---|
| §13.1이 Identifier를 *"동일성 판정 기준"*으로 정의한다 | **Observation** | OB-3 |
| CM-3이 값에 제약을 건다 | **Observation** | OB-4 |
| §13.2·O-2·G-1 등이 동등 관계에 의존한다 | **Observation** | OB-7 |
| 현재 동일성 판정이 전부 문자열 동일이다 | **Observation** | ADC-0007 O-5 |
| **"Identity"라는 개념(Identifier와 구분되는)** | **Interpretation** | 저장소에 그 구분이 명시된 적 없다. RFC-0007이 도입한 **설명 틀** |
| "Identity가 V-1의 원인이다" | **Interpretation** | ADC-0007 판단 1에서 **Reject** |

> **재분류 결과: Identity는 Interpretation이다.** Ownership과 정확히
> 같은 구조다 — 개별 문언은 관찰이고, 그것을 묶는 개념은 관찰이
> 아니다.

## 4.1 두 번의 Reject가 공유하는 구조

| | RFC-0006 (Ownership) | RFC-0007 (Identity) |
|---|---|---|
| 출발한 Observation | 만드는 쪽 ≠ 정하는 쪽 (9건) | §13.1 문언과 CM-3 제약의 이중성 |
| 도입한 설명 틀 | Ownership | Identity |
| 주장 | V-1을 설명한다 | V-1의 원인이다 |
| 결과 | **정정**(ADC-0006 판단 4) | **Reject**(ADC-0007 판단 1) |

**두 RFC 모두 Observation에서 출발했으나, V-1과의 연결이 Interpretation
이었다.** 이것이 V-1이 두 번의 시도로 닫히지 않은 구조적 이유다.

---

# 5. Evidence Gap

**V-1을 Observation만으로 다시 쓰면 다음이 남는다.**

> §13.1이 Context 수준 Identifier와 Metadata를 구조로 선언하지만
> (D-1), §13.2·§13.3·§14·§15의 **어떤 규칙도 그것을 읽거나 요구하지
> 않으며**(D-4), §15.1 경계표에도 해당 행이 없다(D-5). 그 표가 전수
> 목록이라는 진술은 없다(D-6).

**여기까지가 Observation이다. 그 이상은 전부 추론이다.**

## 5.1 부재하는 Observation (Gap)

| ID | 없는 것 | 왜 필요한가 |
|---|---|---|
| **GAP-1** | Context 수준 Identifier·Metadata를 **읽는 규칙·책임·계약** | 소비자가 없으면 "입력 경로 누락"은 결과를 갖지 않는다 |
| **GAP-2** | 그것의 부재로 **실제 실패가 발생한 사례** | D-11: 0건 |
| **GAP-3** | §15.1 경계표가 **전수 목록이라는 진술** | 이것이 없으면 "행이 없다"가 "누락"이 되지 않는다 |
| **GAP-4** | Context 수준 Identifier가 **필수인지 선택인지에 대한 진술** | §13.2 검증 규칙은 Segment 수준만 요구한다(OB-7) |

**4개 Gap 중 어느 것도 지금 저장소에서 관찰되지 않는다.**

---

# 6. V-1을 닫기 위해 필요한 Observation

**새 Observation을 만들지 않는다. 어떤 종류의 Observation이 필요한지만
정의한다.**

V-1이 **결정 가능한 문제가 되려면** 다음 중 **최소 하나**가 관찰되어야
한다.

| ID | 필요한 Observation | 관찰되면 무엇이 달라지는가 |
|---|---|---|
| **N-1** | Context 수준 Identifier 또는 Metadata를 **실제로 읽는 규칙·책임·계약이 존재한다**는 사실 | GAP-1 해소. 소비자가 확정되면 입력 경로가 무엇이어야 하는지가 **소비 방식에서 도출**된다 |
| **N-2** | 그것의 부재로 **실제 실패가 1회 이상 발생했다**는 사실 | GAP-2 해소. 심각도(R-5)가 추론이 아니라 관찰이 된다 |
| **N-3** | §15.1 경계표의 **범위(전수인가 예시인가)에 대한 진술이 존재한다**는 사실 | GAP-3 해소. R-1이 추론에서 사실로 바뀌거나, 반대로 V-1 자체가 성립하지 않게 된다 |

**세 가지는 성격이 다르다.**

- **N-1·N-2는 Kernel이 실제로 구현되거나 사용될 때만 관찰될 수 있다.**
  현재 Kernel 구현 코드는 존재하지 않는다(D-8).
- **N-3은 지금 확인 가능하다** — 문서에 진술이 있는지 없는지의 문제이며,
  현재는 **없다**(OB-12). 이것은 새 Observation을 만드는 것이 아니라
  **이미 없는 것을 확인한 결과**다.

---

# 7. 현재 부족한 것은 무엇인가

## 판정: **Architecture도 Evidence도 아니다. Documentation이다** (부차적으로 Boundary)

| 후보 | 판정 | 근거 |
|---|---|---|
| **Architecture** | **아니다** | 어떤 규칙도 Context 수준 Identifier를 필요로 하지 않는다(D-4). 필요로 하는 구조가 없으므로 빠진 구조도 없다 |
| **Evidence** | **아니다** — 정확히는 "지금 얻을 수 없다" | N-1·N-2는 Kernel 구현·사용 시점에만 관찰 가능하다(D-8). 지금 실험을 늘려서 얻을 수 있는 종류가 아니다 |
| **Documentation** | **그렇다** | §13.1이 **소비자 없는 요소를 선언**하고 있다(D-1 + D-4). 이것은 설계 결손이 아니라 **문서 내부의 미해소 상태**다 |
| **Boundary** | **부분적으로 그렇다** | §15.1 경계표의 **범위가 진술되지 않았다**(D-6). 전수인지 예시인지가 없어 "행이 없다"의 의미가 확정되지 않는다 |

## 7.1 이 판정이 뜻하는 것

**V-1은 "Kernel이 잘못 설계되었다"는 발견이 아니다.** Observation만으로
보면 V-1은 다음이다.

> **§13.1이 선언한 두 요소가 어떤 규칙에도 소비되지 않는 상태이며,
> 그 사실이 §15.1의 표 범위 미진술과 겹쳐 "누락처럼" 보이는 것.**

**심각도 Major(OB-22)와 "Component RFC 착수 불가"(OB-23)는 Observation이
아니라 Interpretation(R-4·R-5)이다.** 이 문서는 그 판정을 바꾸지
않는다 — **분류만 한다.** 심각도 재조정은 Governance 절차의 몫이며 이
문서의 권한 밖이다.

---

# 8. 현재 단계에서 RFC를 열 수 있는가

## 판정: **열 수 있다. 단, 열 수 있는 주제가 달라진다.**

**이 문서는 RFC를 열지 않는다.** 아래는 Observation 기준의 판정이다.

| 주제 | 열 수 있는가 | 근거 |
|---|---|---|
| Identifier의 **출처를 정하는** RFC | **근거가 약하다** | D-4상 소비자가 없다. D-9(주입 9:파생 0)는 있으나, 소비자 없는 요소의 출처를 정하는 것은 결과를 갖지 않는다 |
| Ownership / Identity 등 **설명 틀을 도입하는** RFC | **닫혀 있다** | ADC-0006 정정, ADC-0007 Reject. 같은 구조의 세 번째 시도가 될 근거가 없다 |
| **§15.1 경계표의 범위를 진술하는** 문제 | **열 수 있다** | N-3은 지금 확인 가능하며(§6), 필요한 것은 새 개념이 아니라 **이미 없는 진술의 존재 여부 확인**이다 |
| **§13.1의 두 요소가 소비자를 갖지 않는다는 사실**을 다루는 문제 | **열 수 있다** | D-1 + D-4 전부 Observation이다. 새 해석이 필요 없다 |

**핵심**: 지금 Observation만으로 열 수 있는 것은 **개념을 도입하는
RFC가 아니라, 문서 내부의 미해소 상태를 다루는 것**이다.

---

# 9. 산출물 요약

| 산출물 | 내용 |
|---|---|
| **V-1 Evidence Inventory** | Observation 25건(OB-1~OB-25), 전부 원문·소스 직접 확인 |
| **Observation 목록** | §1 — Model 4건 / 사용처 5건 / 경계표 4건 / 소비 사례 4건 / 값 출처 3건 / 선행 판단 5건 |
| **Interpretation 목록** | R-1~R-7 (7건). **전제 중 관찰되는 것은 하나도 없다** |
| **Evidence Gap** | GAP-1~GAP-4 (4건). 전부 현재 미관찰 |
| **필요한 Observation** | N-1·N-2(Kernel 구현·사용 시점에만 가능) / N-3(지금 확인 가능) |
| **RFC 개설 가능 여부** | 가능. 단 개념 도입이 아니라 문서 내부 미해소 상태를 다루는 것 |

---

## Self Review

- 새 RFC·ADC·ADR을 작성했는가 — **아니오**. 이 문서는 Evidence 정리
  문서이며 Decision을 포함하지 않는다.
- 새 Concept·Layer·Component·Architecture를 제안했는가 — **아니오**.
- Implementation을 제안했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 새 Observation을 만들었는가 — **아니오**. OB-1~OB-25는 전부 기존
  문서·소스를 읽어 확인한 것이며, 전수 검색으로 확인한 부재(OB-8·
  OB-9·OB-12·OB-25)도 새 사실 생성이 아니다.
- Observation과 Interpretation을 섞었는가 — **아니오**. §1은
  Observation만, §2.2·§3·§4는 Interpretation만 다뤘고 각 항목에 분류를
  표기했다.
- 추론을 사실로 승격했는가 — **아니오**. R-1~R-5의 전제가 관찰되지
  않음을 §2.2에 표로 명시했다.
- V-1의 심각도를 바꿨는가 — **아니오**. Major가 Interpretation임을
  **분류**했을 뿐, 재조정은 Governance 절차의 몫으로 남겼다(§7.1).
- V-1을 닫았는가 — **아니오**. 닫으려면 어떤 Observation이 필요한지만
  정의했다(§6).
- 결론을 미리 정해 놓고 Evidence를 골랐는가 — **아니오**. §1.2의 전수
  검색(12개 지점 분류)이 D-4를 만들었고, D-4가 §7 판정을 결정했다.
  순서가 반대가 아니다.
