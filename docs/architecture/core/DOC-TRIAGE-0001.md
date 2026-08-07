# DOC-TRIAGE-0001: Documentation Issue 9건 분류

**문서 성격**: Documentation Review. **Architecture 문서가 아니다.**
**대상**: `STABILITY-0001` §2.B가 분류한 Documentation Issue 9건
**목적**: 9건을 **수정하지 않고 분류만** 한다.

이 문서는 어떤 파일도 수정하지 않는다. Architecture Baseline을
수정하지 않는다. RFC·ADC·ADR·Governance Rule·Phase·Roadmap을 만들지
않는다. **문서 문제를 Architecture 문제로 승격시키지 않는다.**

## 분류 유형

| 유형 | 기준 |
|---|---|
| **T1 Factual Error** | 저장소의 사실과 문서 내용이 **명백히 불일치**. 수정 권장 |
| **T2 Index / Traceability** | 실제 산출물과 **색인·목록·추적 정보**가 불일치. 수정 권장 |
| **T3 Editorial / Cosmetic** | 표현·문체·중복. **Architecture 의미에 영향 없음.** 후순위 |

### 분류 체계의 한계를 먼저 기록한다

D-1·D-2·D-4는 **셋 중 어디에도 정확히 맞지 않는다.** 거짓 진술이
아니므로 T1이 아니고, 색인 불일치가 아니므로 T2가 아니다. 성격상
**"문서 내부의 미해소 상태"**이며, 그것을 담을 유형이 이 체계에 없다.

T3의 **조작적 기준**("Architecture 의미에 영향을 주지 않음")은
만족하므로 T3으로 분류하되, **"Cosmetic"이라는 이름이 이 항목들의
성격을 정확히 반영하지 않는다는 점을 명시한다.** 표현 문제와 같은
급으로 취급하지 않기 위해 T3 안에서 별도 표기한다.

---

# 1. 개별 분류

## D-1 — Context 수준 Identifier·Metadata가 어떤 규칙에도 소비되지 않음

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-1 (= VALIDATION-0001 **V-1**) |
| **파일** | `docs/01_architecture/BASELINE.md` §13.1, §15.1 |
| **현재 문구** | §13.1 구조도: `Context ├── Context Identifier ├── Context Metadata └── Context Segment [ordered]` |
| **실제 저장소 사실** | §13~§15(207~760행) 전수 검색 결과 "Identifier" 12개 지점 중 **Context 수준을 읽거나 요구하는 규칙 0건**. 나머지는 구조 선언 3 / 금지·미결 3 / Segment 수준 6 (`EVIDENCE-INVENTORY-0001` D-4) |
| **분류** | **T3** (미해소 상태 — Cosmetic 아님) |
| **Architecture 영향** | **없음** — 소비자가 없으므로 어떤 규칙도 이에 의존하지 않는다 |
| **Implementation 차단** | **없음** — 차단 주장(R-3·R-4)이 Interpretation임이 확인됨(`EVIDENCE-INVENTORY-0001` §2.2) |
| **수정 필요** | **지금은 아니다** — 해소하려면 N-1/N-2/N-3 중 하나의 관찰이 필요하다 |
| **최소 수정 범위** | 해당 없음. **단 N-3(§15.1 경계표의 범위가 전수인지 예시인지 진술)은 지금 확인 가능하며, 그것이 최소 범위 후보다** |

## D-2 — Merge의 순서 무관성이 진술되지 않음

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-2 (= **V-2**) |
| **파일** | `BASELINE.md` §13.2 (병합 규칙), §15.5 (IN-3) |
| **현재 문구** | §13.2: *"같은 Identifier + 같은 Content는 중복 제거하고, 같은 Identifier + 다른 Content는 오류다"* / IN-3: *"동기/비동기, 순차/병렬 어느 실행 모델도 전제하지 않는다"* |
| **실제 저장소 사실** | 두 규칙 모두 실제로 **순서 무관**하다(어느 쪽을 남겨도 동일 / 어느 순서로 만나도 오류). **성질은 성립하나 진술되어 있지 않다** |
| **분류** | **T3** (미해소 상태 — Cosmetic 아님) |
| **Architecture 영향** | **없음** — 성질이 이미 만족되므로 규칙 변경이 필요 없다 |
| **Implementation 차단** | **없음** |
| **수정 필요** | **권장하나 시급하지 않음** |
| **최소 수정 범위** | §13.2 병합 행에 한 문장 추가 — 다만 **Baseline 수정이므로 절차 판단이 선행되어야 한다**(이 문서는 판단하지 않는다) |

## D-3 — 명사형/동사형 어휘 이원화

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-3 (= **V-3**) |
| **파일** | `BASELINE.md` §13.2(255행), §13.2(267행), §14.4(458행), §15(614행), "Renderer" 24회 |
| **현재 문구** | `### 13.2 Context Builder 책임` / *"Ordering Policy는 **Builder의 입력**"* / `H-2 Builder 내부 구조` ↔ §15는 동사형(Collect/Merge/Validate/Order/Assemble/Render) |
| **실제 저장소 사실** | 두 표기 체계가 공존한다 |
| **분류** | **T3** (진짜 Editorial) |
| **Architecture 영향** | **없음** — §13.2 제목이 "책임"임을 명시하고 §14.4 H-2가 Hidden으로 두어 구현을 규정하지 않는다 |
| **Implementation 차단** | **없음** |
| **수정 필요** | **아니다** — 용어 변경은 Baseline 전면 수정을 수반하며 비용이 효용을 넘는다 |
| **최소 수정 범위** | 권장하지 않음 |

## D-4 — 배선도 번호가 이산 단위를 암시

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-4 (= **V-4**) |
| **파일** | `BASELINE.md` §15.1 배선도 |
| **현재 문구** | 박스와 `① ~ ⑥` 번호 |
| **실제 저장소 사실** | 같은 절 본문이 *"위 배선도의 ②Merge → ③Validate 배치는 가능한 배치 하나의 예시다"*, IN-1이 *"단계는 책임이며 객체·클래스·모듈·서비스가 아니다"*로 이미 방어한다 |
| **분류** | **T3** (미해소 상태 — 그림과 문장의 강도 차이) |
| **Architecture 영향** | **없음** — 본문 진술이 우선한다 |
| **Implementation 차단** | **없음** |
| **수정 필요** | **아니다** |
| **최소 수정 범위** | 권장하지 않음 |

## D-5 — ADR README가 "작성된 ADR 없음"으로 남아 있음

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-5 (= **V-7a**) |
| **파일** | `docs/04_adr/README.md` "현재 상태" 절 |
| **현재 문구** | *"**작성된 ADR 없음.** Development HQ MVP 구현 중 `docs/03_adc/ADC.md`의 NOW 항목(ADC-02, ADC-09, ADC-10)에 대한 실증 자료가 축적되면, 이를 근거로 **첫 ADR 작성을 고려한다**."* |
| **실제 저장소 사실** | **ADR-0001 ~ ADR-0005, 5건이 존재하며 전부 Accepted다.** 그중 4건(ADR-0002~0005)이 Baseline을 v1.1→v1.4로 갱신했다 |
| **분류** | **T1 Factual Error** |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **예 — 즉시** |
| **최소 수정 범위** | "현재 상태" 절 **한 문단 교체.** ADR 5건 목록과 각각이 종결시킨 ADC를 기재. 다른 절(목적·최소 구성)은 그대로 |

## D-6 — RFC README의 등록 표와 현재 상태 진술

**두 개의 서로 다른 사실이 한 파일에 있다. 분류가 다르므로 나눈다.**

### D-6a — 등록된 RFC 표

| 항목 | 내용 |
|---|---|
| **파일** | `docs/02_rfc/README.md` "등록된 RFC" 절 |
| **현재 문구** | 표에 `RFC-0001 \| Kernel Boundary \| Proposed` **1건만** |
| **실제 저장소 사실** | RFC **13건** 존재 — `docs/02_rfc/` 5건, `docs/architecture/core/` 7건, `docs/core/execution-layer/` 1건. 그중 12건이 후속 ADC로 종결 |
| **분류** | **T2 Index / Traceability** |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **예 — 권장** |
| **최소 수정 범위** | 표에 나머지 12건 추가 + 각 행에 후속 ADC 기재. **네임스페이스가 셋이므로 표에 위치 열 추가 필요** |

### D-6b — "현재 상태" 절의 버전 진술

| 항목 | 내용 |
|---|---|
| **파일** | `docs/02_rfc/README.md:17` |
| **현재 문구** | *"Jarvis OS Architecture Baseline **v1.0**과 Development HQ Baseline v1.0은 Frozen이다."* |
| **실제 저장소 사실** | Architecture Baseline은 **v1.4**(§16 Version). Development HQ Baseline은 **v1.0이 맞다**(`development-hq/BASELINE.md` Version = 1.0.0) |
| **분류** | **T1 Factual Error** (앞부분만. 뒷부분은 정확) |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **예 — 즉시** |
| **최소 수정 범위** | `v1.0` → `v1.4` **한 단어.** Development HQ 쪽은 **건드리지 않는다** |

## D-7 — ADC 네임스페이스 3개와 Single Source of Truth 진술

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-7 (= **V-8**) |
| **파일** | `docs/03_adc/ADC.md` 서두, `docs/03_adc/README.md` |
| **현재 문구** | *"이 문서는 Jarvis OS의 **모든 Open Decision에 대한 Single Source of Truth**다."* |
| **실제 저장소 사실** | ADC가 **3개 네임스페이스**에 존재하며 번호가 중복된다 — `docs/03_adc/ADC.md`(12건 Open), `docs/governance/adc/`(Dev HQ ADC-0001~0004), `docs/architecture/core/`(Kernel ADC-0001~0007). 후자 두 곳의 Defer 항목 15건 이상이 `ADC.md`에 집계되어 있지 않다 |
| **분류** | **T2 Index / Traceability** (단 "모든"이라는 문언은 T1 요소를 포함한다) |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **권장** |
| **최소 수정 범위** | `ADC.md` 서두에 **범위 한정 문장 1개** — 이 문서가 다루는 것이 Jarvis OS 수준 Open Decision임을, 그리고 Dev HQ·Kernel 네임스페이스가 별도로 존재함을 기재. **12개 항목은 건드리지 않는다** |

## D-8 — Kernel ADC-0001의 미작성 ADR 2건

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-8 (= **V-9**) |
| **파일** | `docs/architecture/core/ADC-0001-core-baseline.md` 종합 표 |
| **현재 문구** | `\| Governance \| **Accept** \| ... \| ADR Required \|`, `\| Execution Layer \| **Accept** \| ... \| ADR Required \|` |
| **실제 저장소 사실** | 두 ADR 모두 **미작성.** `GOVERNANCE-REVIEW-0001` §1이 지적한 이후 ADR-0002·0003·0004·0005가 전부 *"이 ADR이 해소하지 않는다"*로만 기록했다 |
| **분류** | **T2 Index / Traceability** |
| **Architecture 영향** | **없음** — 두 Module은 이미 Accept되었고 Baseline이 그것에 의존하지 않는다 |
| **Implementation 차단** | **없음** |
| **수정 필요** | **권장하나, 수정 방법이 문서 편집이 아니다** — 해소하려면 ADR 2건을 실제로 작성해야 하며 그것은 절차 작업이다 |
| **최소 수정 범위** | **문서 편집으로는 해소 불가.** 이번 분류 범위 밖 |

## D-9 — RFC 상태 라벨 13건 미갱신

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-9 |
| **파일** | RFC 13건 전부의 헤더 |
| **현재 문구** | `**Status**: Proposed (검토 대상, 결정 아님)` — **13건 전부 동일** |
| **실제 저장소 사실** | 13건 중 **12건이 후속 ADC로 종결**되었고 4건은 ADR·Baseline 반영까지 완료되었다. 실제 Open은 `docs/02_rfc/RFC-0005` 1건뿐 |
| **분류** | **T2 Index / Traceability** |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **권장.** 단 D-6a와 **중복 해소 가능** — 표 하나로 상태를 관리하면 13개 파일을 건드릴 필요가 없다 |
| **최소 수정 범위** | **두 선택지.** (a) D-6a의 표에 상태 열을 두고 각 RFC 파일은 그대로 — 편집 1파일. (b) 13개 헤더 개별 수정 — 편집 13파일. **(a)가 최소다** |

## D-10 — VALIDATION-0001 findings가 어느 집계 지점에도 없음

| 항목 | 내용 |
|---|---|
| **Issue ID** | D-10 |
| **파일** | `docs/architecture/core/VALIDATION-0001-*.md` (findings 원본), 집계 지점 부재 |
| **현재 문구** | V-1~V-9가 VALIDATION-0001 본문에만 존재 |
| **실제 저장소 사실** | V-1·V-7을 언급하는 문서는 8건이나 **전부 서술 인용이며 상태를 추적하는 집계표가 아니다.** `BASELINE.md` §13.6·§14.7·§15.6은 Kernel Defer만 집계하고 VALIDATION findings는 포함하지 않는다 |
| **분류** | **T2 Index / Traceability** |
| **Architecture 영향** | **없음** |
| **Implementation 차단** | **없음** |
| **수정 필요** | **판단 보류** — 집계 지점을 새로 만드는 것은 **추적 장치 신설**에 해당할 수 있다. `STABILITY-0001` §5.3이 같은 이유로 만들지 않았다 |
| **최소 수정 범위** | **이번 분류 범위 밖.** 기존 문서에 추가할지 새 집계를 만들지는 별도 판단 |

---

# 2. 검증 중 발견한 추가 사실 오류 3건

**9건에 포함되지 않지만 같은 유형(T1)이며, 더 중대하다.**

## A-1 — Baseline 문서 제목이 자신의 Version 절과 모순

| 항목 | 내용 |
|---|---|
| **파일** | `docs/01_architecture/BASELINE.md` **1행** |
| **현재 문구** | `# Jarvis OS Architecture Baseline **v1.0**` |
| **실제 저장소 사실** | 같은 문서 **§16 Version = v1.4** |
| **분류** | **T1 Factual Error** — **이번 검토에서 발견한 것 중 가장 중대하다** |
| **Architecture 영향** | **없음** — 제목은 Architecture 진술이 아니다 |
| **Implementation 차단** | **없음** |
| **수정 필요** | **예** |
| **최소 수정 범위** | 1행의 `v1.0` → `v1.4` **한 단어** |

> **절차 판단이 필요하다**: 이 수정은 `BASELINE.md` 파일을 건드린다.
> 내용상 Architecture 변경이 아니라 **버전 표기 정정**이므로
> `ARCHITECTURE_GOVERNANCE.md`의 `RFC → ADC → ADR` 절차 대상인지가
> 명확하지 않다. **이 문서는 그것을 판단하지 않는다** — 사용자
> 결정 사항이며, 이번 작업의 제약("Architecture Baseline을 수정하지
> 마십시오")에 따라 수정하지 않았다.

## A-2 — 루트 README의 상태 표

| 항목 | 내용 |
|---|---|
| **파일** | `README.md` "상태" 표 |
| **현재 문구** | `\| Jarvis OS Architecture Baseline \| **v1.0**, Frozen \|` |
| **실제 저장소 사실** | v1.4, Frozen. (같은 표의 Development HQ Baseline v1.0은 **정확**) |
| **분류** | **T1 Factual Error** |
| **Architecture / Implementation 영향** | 없음 / 없음 |
| **최소 수정 범위** | 표의 **한 셀** |

## A-3 — 루트 README의 도입 문장

| 항목 | 내용 |
|---|---|
| **파일** | `README.md:5` |
| **현재 문구** | *"Architecture Baseline **v1.0**과 Development HQ Baseline v1.0을 기반으로, Claude Code가 Development HQ **MVP-0001 구현에 바로 착수**할 수 있도록 구성된 문서 패키지다."* |
| **실제 저장소 사실** | Baseline은 v1.4. MVP-0001은 완료되었고 MVP-0013까지 진행되었다 |
| **분류** | **T1 Factual Error** (버전) + 맥락 낡음 |
| **Architecture / Implementation 영향** | 없음 / 없음 |
| **최소 수정 범위** | **버전 한 단어**만 정정하면 T1은 해소된다. 맥락 문장 갱신은 선택 |

> **주의 — 고치면 안 되는 것**: `Development HQ Baseline v1.0` 표기는
> **정확하다**(`development-hq/BASELINE.md` Version = 1.0.0).
> 일괄 치환으로 함께 바꾸면 새 사실 오류가 생긴다.

---

# 3. 보고

## 3.1 즉시 수정해야 하는 Documentation Issue (T1 — 명백한 사실 불일치)

| ID | 파일 | 수정 범위 |
|---|---|---|
| **A-1** | `docs/01_architecture/BASELINE.md:1` | 제목 `v1.0` → `v1.4` (한 단어) — **절차 판단 선행 필요** |
| **D-5** | `docs/04_adr/README.md` | "현재 상태" 한 문단 교체 |
| **D-6b** | `docs/02_rfc/README.md:17` | `v1.0` → `v1.4` (한 단어) |
| **A-2** | `README.md` 상태 표 | 한 셀 |
| **A-3** | `README.md:5` | 버전 한 단어 |

**5건 중 4건이 "한 단어 또는 한 셀" 수정이다.** D-5만 한 문단이다.

## 3.2 수정 권장하나 Implementation을 막지 않는 Issue (T2 — 색인/추적)

| ID | 내용 | 비고 |
|---|---|---|
| **D-6a** | RFC 등록 표 1건 → 13건 | D-9와 함께 처리하면 편집 1파일 |
| **D-9** | RFC 상태 라벨 13건 | **D-6a의 표에 상태 열을 두는 것이 최소** |
| **D-7** | ADC.md의 "모든 Open Decision" 범위 한정 | 서두 문장 1개 |
| **D-8** | 미작성 ADR 2건 | **문서 편집으로 해소 불가** — 절차 작업 |
| **D-10** | VALIDATION findings 미집계 | **판단 보류** — 집계 지점 신설 여부는 별도 결정 |

## 3.3 후순위로 보류 가능한 Issue (T3)

| ID | 내용 | 성격 |
|---|---|---|
| **D-1** | Context 수준 요소 미소비 | 미해소 상태 (Cosmetic 아님). 해소에 관찰 필요 |
| **D-2** | Merge 순서 무관성 미진술 | 미해소 상태. 성질은 이미 성립 |
| **D-4** | 배선도 번호 | 미해소 상태. 본문이 이미 방어 |
| **D-3** | 명사형/동사형 이원화 | 진짜 Editorial. **수정 권장하지 않음** |

---

# 4. 최종 판단 — 9건이 Kernel Component Architecture 또는 Implementation 착수를 차단하는가

## **차단하지 않는다.**

### 근거 1 — 차단 요인은 이미 별도로 특정되어 있다

`CLOSURE-0001` §4가 확인한 대로, Kernel Component Architecture를
막고 있는 것은 `BASELINE.md` §10과 `GOVERNANCE-REVIEW-0001` §5의
**6개 근거**다.

**그 6개 중 Documentation Issue에 해당하는 것은 0건이다.**

| §5의 6개 근거 | Documentation Issue인가 |
|---|---|
| §10 Out of Scope 유지 | 아니다 — 절차 |
| Kernel Module 3개 Defer | 아니다 — 관찰 부족 |
| ADC-02 Open | 아니다 — Architecture 결정 |
| 승격 대상 없음 | 아니다 — 관찰 부족 |
| Engine 수 ≥ 2 미충족 | 아니다 — 관찰 부족 |
| Execution Result 미설계 | 아니다 — 관찰·구현 |

### 근거 2 — 유일하게 차단으로 주장되었던 항목은 근거를 잃었다

D-1(V-1)이 유일하게 *"Component RFC 착수 불가"*의 근거로 제시된
항목이었으나, `EVIDENCE-INVENTORY-0001` §2.2가 그 주장(R-3·R-4)의
전제가 **하나도 관찰되지 않음**을 확인했다.

### 근거 3 — 9건 전부 Architecture 영향 0건

§1의 개별 분류에서 **9건 + 추가 3건, 총 12건 모두 "Architecture 영향
없음 / Implementation 차단 없음"**으로 판정되었다.

### 판정을 한정한다

> 9건은 **차단 요인이 아니다.** 다만 T1 5건은 **저장소를 처음 읽는
> 사람에게 잘못된 사실을 전달한다** — 특히 A-1(Baseline 제목이 자신의
> Version과 모순)과 D-5(*"작성된 ADR 없음"*)는 프로젝트의 현재 위치를
> 정반대로 알려준다.
>
> **차단하지 않는 것과 방치해도 되는 것은 다르다.**

---

## Self Review

- 파일을 수정했는가 — **아니오**. 이 문서는 분류만 한다.
- Architecture Baseline을 수정했는가 — **아니오**. A-1은 발견·보고만
  했고, 절차 판단이 필요하다는 사실을 명시했다.
- RFC·ADC·ADR·Governance Rule·Phase·Roadmap을 만들었는가 —
  **아니오**. D-10에서 집계 지점 신설을 **보류**했다.
- 문서 문제를 Architecture 문제로 승격시켰는가 — **아니오**. 12건
  전부 "Architecture 영향 없음"으로 판정했고, §4가 차단하지 않음을
  결론으로 명시했다.
- 사실 오류와 표현 문제를 동일하게 취급했는가 — **아니오**. T1 5건과
  T3 4건을 분리했고, T3 안에서도 "미해소 상태"(D-1·D-2·D-4)와 "진짜
  Editorial"(D-3)을 구분했다.
- 분류 체계에 억지로 끼워 맞췄는가 — **아니오**. §0에서 D-1·D-2·D-4가
  세 유형 중 어디에도 정확히 맞지 않는다는 사실을 먼저 기록했다.
- 9건 밖의 발견을 9건에 섞었는가 — **아니오**. §2로 분리하고 "추가
  발견"으로 표기했다.
- 사실 확인을 했는가 — **Pass**. 12건 전부 원문을 직접 읽어 현재
  문구를 인용했고, 저장소 사실은 전수 검색·파일 확인으로 대조했다.
