# STABILITY-0001: Core Architecture 안정성 검토

**문서 성격**: Custodian 검토 문서. **Governance 문서가 아니다.**
**대상**: Architecture Baseline v1.4 및 Kernel 영역 전체
**목적**: Core Architecture를 **Stable 상태로 선언할 수 있는지** 검토한다.

이 문서는 **새로운 결정을 내리지 않는다.** RFC·ADC·ADR을 작성하지
않는다. 새 Concept·Layer·Component·Boundary·Governance Rule을 만들지
않는다. **현재까지의 Evidence로 안정화 여부만 판단한다.**

---

# 1. Open RFC가 있는가

## 1.1 먼저 확인한 사실 — RFC 상태 라벨은 판정 근거가 되지 못한다

저장소의 RFC **13건 전부**가 헤더에 `**Status**: Proposed`를 달고
있다(전수 확인). ADC와 ADR이 완료된 RFC도 마찬가지다.

> **RFC 상태 라벨은 절차 진행을 반영하도록 갱신된 적이 없다.**

이는 `VALIDATION-0001` V-7(ADR README가 *"작성된 ADR 없음"*으로 남아
있음, RFC README 등록 표가 1건만 기재)과 **같은 종류의 색인 부채**다.

따라서 Open 여부는 라벨이 아니라 **후속 ADC의 존재로 판정**했다.

## 1.2 RFC → ADC 대응 전수 확인

| 네임스페이스 | RFC | 후속 ADC | 상태 |
|---|---|---|---|
| `docs/architecture/core/` | RFC-0001 | ADC-0001-core-baseline | 종결 |
| | RFC-0002 | ADC-0002 → ADR-0002 | 종결 |
| | RFC-0003 | ADC-0003 → ADR-0003 | 종결 |
| | RFC-0004 | ADC-0004 → ADR-0004 | 종결 |
| | RFC-0005 | ADC-0005 → ADR-0005 | 종결 |
| | RFC-0006 | ADC-0006 (ADR 불필요) | 종결 |
| | RFC-0007 | ADC-0007 (ADR 불필요) | 종결 |
| `docs/core/execution-layer/` | RFC-0001 | ADC-0001-artifact-drift-boundary | 종결 |
| `docs/02_rfc/` (Dev HQ) | RFC-0001 | `governance/adc/ADC-0001` | 종결 |
| | RFC-0002 | ADC-0002 | 종결 |
| | RFC-0003 | ADC-0003 | 종결 |
| | RFC-0004 | ADC-0004 | 종결 |
| | **RFC-0005** | **없음** | **Open** |

## 1.3 판정

> **Open RFC는 1건이다** — `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`.
> `ADC-0001-core-baseline.md`가 이를 *"후속 ADC 대기 중"*으로 이미
> 기록했고, 그 상태가 지금까지 유지되었다.

**이것이 Architecture를 계속 변경해야 하는 필수 사안인가**:

| 확인 | 결과 |
|---|---|
| Kernel 영역을 막고 있는가 | **아니다.** Development HQ 수준의 Execution Boundary 문제이며, Kernel Context 영역의 어떤 결정도 이 RFC에 의존하지 않았다 |
| Development HQ를 막고 있는가 | **아니다.** Development HQ Phase 1은 종료되었고(ADR-0001·0002·0003·0004·0005가 반복 확인), 이후 코드·문서가 변경되지 않았다 |

> **Architecture를 계속 변경해야 하는 필수 사안은 남아 있지 않다.**

---

# 2. Open Issue 재분류

현재 열려 있는 항목을 **Architecture / Documentation / Implementation
관찰 대기** 세 범주로 다시 분류한다.

## 2.A Architecture — 실제로 Architecture 결정이 남은 것

| 항목 | 출처 | 비고 |
|---|---|---|
| ADC-02 Runtime 개념의 존폐 | `ADC.md`, NOW | v1.0부터 Open. Kernel Context 영역과 무관 |
| ADC-09 Workflow 그래프의 의미론적 경계 | `ADC.md`, NOW | 동일 |
| ADC-10 Policy 규칙의 출처 분리 | `ADC.md`, NOW | 동일 |
| ADC-01·03~08·11·12 (9건) | `ADC.md`, NEXT/LATER | 우선순위상 지금 대상 아님 |
| Kernel Module Defer 3건 (Workflow / Memory / Event Bus) | Kernel ADC-0001 | 전부 "관찰 부족"이 사유 |
| Dev HQ RFC-0005 | §1.3 | 후속 ADC 미작성 |

**소계: 16건.** 이 중 **NOW 3건은 전부 Architecture Baseline v1.0
시점부터 Open이며, Kernel 영역 작업(RFC-0002~0007)이 그중 어느
것도 건드리지 않았다.**

## 2.B Documentation — 문서 내부의 미해소 상태

| 항목 | 출처 | 즉시 처리 가능한가 |
|---|---|---|
| **V-1** Context 수준 Identifier·Metadata가 어떤 규칙에도 소비되지 않음 | VALIDATION-0001 → EVIDENCE-INVENTORY-0001 §7이 **Documentation으로 재분류** | 판단 필요 |
| **V-2** Merge의 순서 무관성 미진술 | VALIDATION-0001 | 판단 필요 |
| **V-3** 명사형/동사형 어휘 이원화 | VALIDATION-0001 | 판단 필요 |
| **V-4** 배선도 번호가 이산 단위를 암시 | VALIDATION-0001 | 판단 필요 |
| **V-7** ADR README *"작성된 ADR 없음"*, RFC README 등록 표 1건 | VALIDATION-0001 | **예 — Architecture 결정이 아님** |
| **V-8** ADC 네임스페이스 3개, 번호 중복 | VALIDATION-0001 | 판단 필요 |
| **V-9** Kernel ADC-0001의 미작성 ADR 2건(Governance·Execution Layer Module) | VALIDATION-0001, 원문 재확인 | 절차 필요 |
| **RFC 상태 라벨 미갱신 13건** | 본 문서 §1.1 | **예 — Architecture 결정이 아님** |
| VALIDATION-0001 findings가 어디에도 집계되지 않음 | 본 문서 §5.2 | 판단 필요 |

**소계: 9건.** 이 범주가 **가장 크다.**

## 2.C Implementation 관찰 대기 — 지금 결정할 수 없는 것

| 항목 | 재검토 조건 | 출처 |
|---|---|---|
| V-5 실패 시 흐름 의미론 | Kernel 구현·사용 | VALIDATION-0001 |
| V-6 빈 Context의 유효성 | 동일 | VALIDATION-0001 |
| Context Boundary 형태 | **실제 Engine 호출 1회** | ADC-0003 판단 4 |
| Engine별 Renderer | **실제 Engine 호출 1회** | ADC-0003 판단 5b |
| 활용 사례·실제 HQ 통합 | **실제 Engine 호출 1회** | ADC-0003 판단 6b |
| Identifier 파생 규칙 | Context 재사용·비교 사례 | ADC-0003 판단 1b |
| 확장 메커니즘 | 두 번째 Renderer 또는 Ordering Policy | ADC-0004 판단 5b |
| Contract Versioning | 계약 변경으로 호환성 문제 발생 | ADC-0004 판단 7 |
| Ownership 어휘 / 3층 명명 | 두 번째 문서에서 필요해질 때 | ADC-0006 판단 5·6b |
| Identity 구분 / Boundary 판정 / 어휘 승격 | 이중성으로 인한 **실제 오류 1회** | ADC-0007 판단 2·3·4 |
| 4-Layer Context Model | 관찰된 적 없음 | ADC-0002 판단 2b |

**소계: 11건 이상.** **전부 재검토 조건이 명시되어 있으며, 그 조건은
예외 없이 "관찰"이다.**

## 2.4 재분류 결과

| 범주 | 건수 | 성격 |
|---|---|---|
| **A. Architecture** | 16 | 대부분 v1.0부터 Open이며 Kernel 영역과 독립 |
| **B. Documentation** | 9 | **가장 큼.** Architecture 결정이 아님 |
| **C. Implementation 관찰 대기** | 11+ | 전부 재검토 조건이 명시된 상태 |

> **현재 열려 있는 것 중 "Kernel Architecture를 지금 바꿔야 하는 것"은
> 하나도 없다.**

---

# 3. Architecture 자체는 Stable한가

## 3.1 Evidence

| ID | Observation | 확인 방법 |
|---|---|---|
| **S-1** | `BASELINE.md`의 마지막 변경은 `09e5289`(v1.4, ADR-0005)이다 | `git log -- docs/01_architecture/BASELINE.md` |
| **S-2** | 그 이후 **6개 커밋**(VALIDATION-0001, RFC-0006, ADC-0006, RFC-0007, ADC-0007, EVIDENCE-INVENTORY-0001)이 **Baseline을 한 글자도 바꾸지 않았다** | `git log 09e5289..HEAD` + 각 문서의 "Baseline 영향 없음" 판정 |
| **S-3** | 그 사이 **RFC → ADC 사이클이 2회** 완주했고, **두 번 모두 Baseline 변경 없이 종결**되었다 | ADC-0006 "Baseline 영향 없음", ADC-0007 "Baseline 영향 없음" |
| **S-4** | 두 사이클의 핵심 주장이 각각 **정정(ADC-0006 판단 4)**과 **Reject(ADC-0007 판단 1)**되었다 | 두 ADC 원문 |
| **S-5** | 두 사이클 모두 **Frozen 문언 변경 요구를 Reject**했다(ADC-0006 판단 7 §11, ADC-0007 판단 7 §13.1) | 두 ADC 원문 |
| **S-6** | Kernel 영역 RFC 7건 전부 후속 ADC로 종결되었다 | §1.2 |

## 3.2 판정

> ## **Stable하다.**

근거는 "더 이상 바꿀 것이 없다"가 아니라 **"바꾸려는 시도가 Evidence
부족으로 두 번 연속 실패했다"**(S-3·S-4)는 관찰이다.

이 프로젝트의 안정성 기준은 `ARCHITECTURE_GOVERNANCE.md`의 Good
Architecture Principle이다 — *"좋은 Architecture는 모든 것을 미리
설계한 Architecture가 아니라, 필요한 것만 적절한 시점에 결정한
Architecture다."*

**S-4가 그 기준의 충족을 보여준다**: 두 번의 시도가 실패한 이유가
"설계가 틀려서"가 아니라 **"지금 결정할 근거가 없어서"**였다. 그것은
**Evidence 없이 진행할 수 없는 지점에 도달했다**는 뜻이며, 안정화의
정의에 해당한다.

## 3.3 반대 근거도 기록한다

| 반대 근거 | 무게 |
|---|---|
| Kernel 구현 코드가 **존재하지 않는다** — Architecture가 실행으로 검증된 적이 없다 | **크다.** Stable은 "문서 수준의 안정"이며 "검증된 안정"이 아니다 |
| 실제 Engine 호출 **0회** | 크다. 위와 같은 성질 |
| Documentation 범주 9건이 미해소 | 보통. Architecture 결정이 아니나 문서 신뢰도에 영향 |

> **따라서 "Stable"은 다음으로 한정된다: Architecture Baseline이
> 현재 Evidence로 더 변경될 필요가 없는 상태. 실행으로 검증된 상태가
> 아니다.**

---

# 4. Kernel Component 설계를 시작할 수 있는가

## 4.1 차단하는 것은 V-1이 아니다

`VALIDATION-0001` 항목 8은 *"V-1 해소 전 Component RFC 착수 불가"*로
판정했으나, `EVIDENCE-INVENTORY-0001` §2.2가 그 근거(R-3·R-4)가
**Interpretation임**을 확인했다.

**이 문서는 그 판정을 재조정하지 않는다**(새 결정 금지). 다만 V-1과
무관하게 **더 강한 차단 요인이 별도로 존재한다**는 사실을 기록한다.

## 4.2 실제 차단 요인 — §10과 GOVERNANCE-REVIEW-0001 §5

`BASELINE.md` §10은 v1.4 기준으로 **"Kernel Component Architecture
(Component의 존재·설계·상호작용 구조)"**를 Out of Scope로 유지하고
있다.

`ADC-0005` 판단 1이 그 항목을 열지 않기로 한 근거는
`GOVERNANCE-REVIEW-0001` §5의 **6개 근거**였고, 같은 ADC가 그 6개가
**전부 지금도 유효함**을 확인했다.

| §5의 근거 | 현재 상태 |
|---|---|
| §10이 Out of Scope로 유지 | 유효 |
| Kernel Module 3개 Defer (Workflow/Memory/Event Bus) | 유효 |
| ADC-02(Runtime 존폐) Open | 유효 — `ADC.md`에서 확인 |
| Kernel 방향 승격 대상 없음 | 유효 |
| Engine Gateway Trigger("Engine 수 ≥ 2") 미충족 | 유효 — Engine 호출 0회 |
| Execution Result(6번째 Artifact) 미설계 | 유효 |

## 4.3 순환 구조를 기록한다

`EVIDENCE-INVENTORY-0001` §6이 확인한 사실과 §4.2를 겹치면 다음이
드러난다.

```
Component 설계를 열려면  →  §5의 6개 근거가 해소되어야 한다
6개 중 최소 2개(Engine 수 ≥ 2, Execution Result)  →  Runtime/구현 관찰이 필요
Runtime 관찰이 생기려면  →  무언가가 실제로 구현·실행되어야 한다
```

**즉 문서 작업만으로는 이 조건이 해소되지 않는다.** 두 번의 RFC
사이클이 실패한 것도 같은 이유다 — **부족한 것이 문서가 아니라
관찰이기 때문이다.**

## 4.4 판정

> ## **보류한다. Runtime Observation이 생길 때까지.**

**차단 근거는 V-1이 아니라 §10 + GOVERNANCE-REVIEW-0001 §5의 6개
근거다.** 이 근거는 V-1의 상태와 무관하게 성립하며, ADC-0005 판단 1이
이미 확인했다.

**이 판정은 새 결정이 아니다** — §10(Frozen)과 ADC-0005 판단 1이
이미 내린 결정을 현재 상태에서 확인한 것이다.

---

# 5. Baseline은 Freeze 가능한 상태인가

## 5.1 Freeze의 정의를 먼저 확인한다

`ARCHITECTURE_GOVERNANCE.md`:

> *"Architecture Baseline은 '모든 문제가 해결된 상태'가 아니라 **'지금
> 결정할 것과 나중에 결정할 것이 명확히 구분되고 추적되는 상태'**를
> 의미한다. 미결정 사항이 없는 것이 목표가 아니라, 미결정 사항이
> **정직하게 드러나 추적되는 것**이 목표다."*

**Baseline은 이미 v1.0부터 `Architecture State = Frozen`이다.**
따라서 질문은 "Freeze로 전환 가능한가"가 아니라 **"현재 상태가 Freeze
조건을 만족하는가"**다.

## 5.2 조건 대조 — 미결 항목이 추적되는가

| 미결 항목군 | 추적 위치 | 판정 |
|---|---|---|
| Kernel Context Model Defer 6건 | `BASELINE.md` §13.6 | **추적됨** |
| Public Contract Defer 2건 | §14.7 | **추적됨** |
| Reference Architecture 미결 6건 | §15.6 | **추적됨** |
| Jarvis OS Open Decision 12건 | `ADC.md` | **추적됨** |
| Kernel Module Defer 3건 | Kernel ADC-0001 | 추적됨 (집계는 없음) |
| RT-0001 재평가 Trigger 4건 | `docs/governance/rt/RT-0001.md` | **추적됨** |
| ADC-0006·0007의 Defer 5건 | 각 ADC | 추적됨 (집계는 없음) |
| **VALIDATION-0001 findings V-1~V-9** | **VALIDATION-0001 문서 내부만** | **집계 없음** |
| **미작성 ADR 2건** | 각 ADR의 Consequences 각주 | **집계 없음** |
| **Dev HQ RFC-0005 Open** | `ADC-0001-core-baseline.md` 한 줄 | **집계 없음** |

## 5.3 판정

> ## **Freeze 상태를 유지할 수 있다. 단 조건 충족은 부분적이다.**

- **"구분되어 있는가"** — 충족. 결정된 것과 Defer된 것이 각 절에
  명시적으로 분리되어 있다.
- **"추적되는가"** — **부분 충족.** 상위 3개 항목군은 Baseline 본문에
  집계되어 있으나, **VALIDATION findings 9건 / 미작성 ADR 2건 /
  Open RFC 1건은 어느 집계 지점에도 없다.**

이 결함의 원인은 §2.B가 분류한 **Documentation 범주**이며, 특히
V-7(색인 낡음)과 같은 성질이다. **Architecture의 결함이 아니라 추적
장치의 결함이다.**

> **이 문서는 그 추적 장치를 만들지 않는다** — 새 Governance Rule
> 금지에 해당한다. 사실로만 기록한다.

---

# 6. Architecture를 다시 열 수 있는 Trigger

**새 Trigger를 만들지 않는다.** 기존 Rule A / Rule B와 각 ADC가 이미
기록한 재검토 조건을 **정리만** 한다.

## 6.1 기존 규칙 (원문)

`docs/governance/README.md`:

- **Rule A**: RT Trigger 충족 → RFC
- **Rule B**: 동일 Tag Observation 3회 → RFC

## 6.2 Rule A — RT-0001의 4개 Trigger 현재 상태

| Candidate | Trigger (원문) | 현재 |
|---|---|---|
| 1. Task Dispatcher | Workflow Branch 발생, 또는 하드코딩된 Task 호출 체인 수 ≥ 2 | **ADC-0004에서 이미 재판단(Keep in MVP).** EVIDENCE-REVIEW-0001이 추가 체인을 관찰했으나 재발동 여부는 판단하지 않음 |
| 2. Engine Gateway | **Engine 수 ≥ 2** | **미충족** — Engine 호출 0회 |
| 3. Agent Registry | **HQ 수 ≥ 2**, 또는 Registry 중복 관리 발생 | **미충족** — HQ 1개 |
| 4. Context 전달 메커니즘 | **Context 전달 경로 ≥ 2** | **미충족** — EVIDENCE-REVIEW-0001 기준 단일 경로 |

## 6.3 Rule B — 동일 Tag Observation 3회

현재 Observation 축적은 **Development HQ MVP-0001~0013**과 **Execution
Layer MVP-0001~0005**에서 멈춰 있으며, 그 이후 새 MVP Observation이
추가되지 않았다. **3회 축적 중인 Tag는 없다.**

## 6.4 각 ADC가 기록한 재검토 조건 (정리)

**이것들은 새 Trigger가 아니라 이미 각 ADC 본문에 있는 조건이다.**

| 조건 | 열리는 항목 | 출처 |
|---|---|---|
| **실제 Engine 호출 1회 관찰** | Context Boundary / Engine별 Renderer / 활용 사례·HQ 통합 | ADC-0003 판단 4·5b·6b |
| **두 번째 Renderer 또는 Ordering Policy 필요** | 확장 메커니즘 | ADC-0004 판단 5b |
| **계약 변경으로 호환성 문제 발생** | Contract Versioning | ADC-0004 판단 7 |
| **Ownership 어휘가 두 번째 문서에서 필요해짐** | Ownership 어휘·3층 명명 | ADC-0006 판단 5·6b |
| **Identifier 이중성으로 실제 오류 1회 발생** | Identity 구분·Boundary 판정·어휘 승격 | ADC-0007 판단 2·3·4 |
| **Context 재사용·비교 사례 발생** | Identifier 파생 규칙 | ADC-0003 판단 1b |
| **§5의 6개 근거 해소** | Kernel Component Architecture(§10) | ADC-0005 판단 1 |

## 6.5 정리 — 공통 성질

> **위 조건 전부가 "관찰"이다. 문서 작업으로 충족되는 조건은 하나도
> 없다.**

예외는 하나뿐이다 — `EVIDENCE-INVENTORY-0001` §6의 **N-3**(§15.1
경계표의 범위 진술 존재 여부)은 지금 확인 가능하며, 그것은
Architecture Trigger가 아니라 Documentation 범주에 속한다(§2.B).

---

# 7. 산출물 요약

## 7.1 Architecture Stability Report

> **Core Architecture는 Stable하다** — 단, "문서 수준의 안정"이며
> "실행으로 검증된 안정"이 아니다(§3.3).

결정적 Evidence: Baseline 마지막 변경(v1.4) 이후 **6개 커밋, 2회의
완주한 RFC→ADC 사이클이 Baseline을 한 글자도 바꾸지 않았다.** 두
사이클 모두 Evidence 부족으로 정정·Reject되었고, Frozen 문언 변경
요구도 두 번 다 Reject되었다.

## 7.2 Open Issue 재분류

| 범주 | 건수 | 판정 |
|---|---|---|
| Architecture | 16 | 대부분 v1.0부터 Open, Kernel 영역과 독립 |
| **Documentation** | **9** | **가장 큼. Architecture 결정이 아님** |
| Implementation 관찰 대기 | 11+ | 전부 재검토 조건 명시됨 |

**Kernel Architecture를 지금 바꿔야 하는 항목: 0건.**

## 7.3 Freeze 가능 여부

> **유지 가능. 조건 충족은 부분적.**
> "구분" 충족 / "추적" 부분 충족 — VALIDATION findings 9건, 미작성
> ADR 2건, Open RFC 1건이 어느 집계 지점에도 없다(§5.2).

## 7.4 Kernel Component 착수 가능 여부

> **보류.** 차단 근거는 V-1이 아니라 §10 + GOVERNANCE-REVIEW-0001 §5의
> 6개 근거이며, 그 6개는 전부 유효하다. **최소 2개는 Runtime 관찰
> 없이는 해소되지 않는다**(§4.3).

## 7.5 Architecture를 다시 열 조건

Rule A(RT Trigger 4건 — 3건 미충족, 1건 재판단 완료) / Rule B(축적
중인 Tag 없음) / 각 ADC의 재검토 조건 7종.

> **전부 "관찰"이 조건이다. 문서 작업으로 열리는 것은 없다.**

---

## Self Review

- 새 결정을 내렸는가 — **아니오**. §4.4의 "보류"는 §10과 ADC-0005
  판단 1이 이미 내린 결정의 확인이고, §5.3의 "Freeze 유지 가능"은
  현재 상태가 기존 정의를 만족하는지의 대조다.
- 새 RFC·ADC·ADR을 작성했는가 — **아니오**.
- 새 Concept·Layer·Component·Boundary·Governance Rule을 만들었는가 —
  **아니오**. §5.3과 §6.5에서 추적 장치·Trigger를 만들지 않는다고
  명시했다.
- V-1의 심각도를 재조정했는가 — **아니오**. §4.1이 재조정하지 않음을
  명시하고, 대신 V-1과 무관한 별도 차단 요인을 근거로 삼았다.
- Evidence만 사용했는가 — **Pass**. S-1·S-2는 `git log`로, RFC→ADC
  대응은 전수 확인으로, RT Trigger·Rule A/B·ADC.md 12건은 원문에서
  직접 확인했다.
- 안정성을 낙관적으로 판정했는가 — **아니오**. §3.3에 반대 근거 3건을
  기록하고 "Stable"의 범위를 문서 수준으로 한정했다.
- Documentation 부채를 이 문서가 해소했는가 — **아니오**. 분류하고
  기록만 했다. 해소는 별도 작업이며 이 문서의 권한 밖이다.
