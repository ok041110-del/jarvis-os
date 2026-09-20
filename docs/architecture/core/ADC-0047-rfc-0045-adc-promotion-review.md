# ADC-0047: RFC-0045(Context Segment Identifier·Metadata Contract) ADC 승격 검토

**Status**: Decided — **Defer** (ADC로 승격하지 않는다, RFC-0045는 Proposed로 유지)
**Author**: Claude Code
**선행 체인**: `RFC-0045-context-segment-identifier-metadata-contract.md`
(Proposed) — `ADC-0003` 판단 1b(H-5 Defer) / `ADC-0006` 판단 5·8(Ownership
Defer, V-1 미종결) / `ADC-0007` 판단 1·4(Identity Reject/Defer)의
직접 후속.
**대상**: RFC-0045를 지금 ADC로 승격할지, H-5/H-6 설계를 확정할지,
단일/분리 ADC로 열지, ADR 시점을 언제로 할지 — **5개 질문에 대한
Owner-level 판정**(`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준을
그대로 적용).

> 이 ADC는 H-5/H-6의 **내용을 확정하지 않는다.** Kernel Context
> Builder·Renderer를 구현하지 않는다. Stable Prefix가 관찰됐다고
> 주장하지 않는다. A 조건 충족을 B 조건 충족으로 취급하지 않는다.
> `BASELINE.md`·`ADC-0003`·`ADC-0006`·`ADC-0007` 원문은 수정하지
> 않는다.

---

## 0. 이 ADC가 판정하는 5개 질문 (사용자 Owner Decision Scope 그대로)

1. RFC-0045를 ADC로 승격해야 하는가
2. H-5/H-6을 하나의 ADC로 묶을지, 분리할지
3. 현재 Evidence가 설계 선택에 충분한가
4. OQ-1·OQ-4가 추가 조사를 필요로 하는가
5. ADR이 지금 필요한가, 설계 확정 이후에만 필요한가

---

## 판단 1. RFC-0045를 ADC로 승격해야 하는가

### Evidence

`ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준": 다음 중 **하나**를
반드시 만족해야 채택된다.

1. 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다.
2. 결정이 늦어질수록 되돌리는 비용이 매우 커진다.

RFC-0045 자신의 Evidence 섹션이 이 두 기준에 대해 이미 답하고 있다.

| 기준 | RFC-0045의 근거 | 충족 여부 |
|---|---|---|
| 1. 진행 불가 | §6: "H-5/H-6을 확정해도 기존 책임 배치(§13.5)와 Engine 호출 경계(4개 Adapter 함수의 `str` 계약)는 바뀌지 않는다." §1: H-5/H-6 미결 상태 자체는 "지금까지 문제가 되지 않았다 — Kernel Context Builder가 구현된 적이 없으므로 소비자가 없었다"(GAP-1). B(Stable Prefix)만 막혀 있으나, `ADC-0003` 판단 4 Decision Rationale이 이미 "Defer해도 상위 설계가 막히지 않는다 — 판단 1과 판단 3은 Boundary 없이 성립한다"고 확정해 두었다. | **불충족** |
| 2. 비용 증가 | §3.4: "8개 패턴이 존재한다는 사실 자체는... 어느 것도 자동으로 충족시키지 않는다", "실제 장애·운영 실패 사례는 관찰되지 않았다(0건)". §8: H-5/H-6 확정에 필요한 Evidence(비교·재사용 사례, 실제 필요 관찰) 둘 다 "현재 0건". | **불충족** |

### Decision

## **Defer**

RFC-0045를 ADC로 승격하지 않는다. **RFC 단계(Proposed)에 남긴다.**

### Decision Rationale

두 기준 모두 불충족이므로 `ARCHITECTURE_GOVERNANCE.md`의 "두 조건을
만족하지 않으면 해당 사안은 현재 단계에서 다루지 않는다"가 그대로
적용된다. 이것은 RFC-0045의 품질이나 방향이 잘못됐다는 뜻이 아니다
— RFC-0045 자신이 §3.4·§8에서 정직하게 "Evidence 0건"을 기록해 둔
덕분에 이 판정이 추측 없이 가능했다. `ADC-0003` 판단 1b(H-5
Defer)와 `ADC-0007` 판단 4(Identity 어휘 승격 Defer)가 정확히 같은
논리로 같은 결론에 도달한 전례와 일치한다.

**재검토 조건**(`ADC-0003` 판단 1b, `ADC-0007` 판단 4와 동일 형식으로
명시):

- Context를 실제로 **비교·재사용하는 사례**가 1회 이상 관찰되거나,
- 8개 ad hoc 패턴 중 하나가 순서 불일치·Identifier 부재/충돌로 인한
  **실제 운영 실패**를 1회 이상 일으키거나,
- 여러 실제 Engine 호출에 걸쳐 동일 Segment가 재사용돼야 하는 실제
  필요가 관찰될 때.

### Next Step

No ADR Required (ADC 자체가 Baseline을 바꾸지 않으므로).

---

## 판단 2. H-5/H-6을 하나의 ADC로 묶을지, 분리할지

### Evidence

RFC-0045 §5.1이 이미 의존관계를 분석해 두었다 — H5-A(주입)는 H-6과
독립, H6-B(델리미터)는 H-5와 독립이나, H5-B(해시 파생)와 H6-A/C(구조체)는
"무엇을 해시할 것인가"를 공유해서 결정해야 하는 관계다. 즉 **완전
독립도, 완전 결합도 아니다** — 채택되는 옵션 조합에 따라 결합도가
달라진다.

### Decision

## **판정하지 않는다 (판단 1의 결과로 인해 이 질문 자체가 아직 발생하지 않음)**

### Decision Rationale

판단 1이 Defer이므로 ADC 자체가 열리지 않는다 — "하나로 묶을지
분리할지"는 ADC를 여는 시점에만 의미를 갖는 질문이다. 지금 이
질문에 미리 답하면, 아직 Evidence가 없는 상태에서 미래의 ADC
구조를 선결정하게 되어 §채택 기준을 우회하는 효과를 낳는다. 이
질문은 재검토 조건(판단 1)이 충족되어 실제로 ADC를 여는 시점에,
그때의 Evidence(어떤 옵션 조합이 실제로 관찰되었는지)를 근거로
다시 판단해야 한다.

### Next Step

No ADR Required.

---

## 판단 3. 현재 Evidence가 설계 선택에 충분한가

### Evidence

| 필요 Evidence | RFC-0045 근거 | 현재 값 |
|---|---|---|
| H-5 확정에 필요(비교·재사용 사례) | §8 | **0건** |
| H-6 확정에 필요(Segment 요구 상황 부딪힌 사례, 재사용 필요) | §8 | **0건** |
| 8개 ad hoc 패턴으로 인한 실제 장애 | §3.4 | **0건** |
| `ADC-0026`/`ENGINE-CONNECT-000x`의 Segment 유사 구조 언급 | §3.3 | **0건**(전수 grep) |

### Decision

## **불충분하다**

### Decision Rationale

네 항목 모두 0건이다. 이것은 "증거가 약하다"가 아니라 "증거가
전혀 없다"는 뜻이며, `ARCHITECTURE_GOVERNANCE.md`의 Experimental
Evidence 원칙("Experimental Evidence는 그 존재만으로 Formal
Architecture Decision이나 ADC Accept를 발생시키지 않는다")보다도
더 이른 단계다 — Experimental Evidence조차 아직 없다.

### Next Step

No ADR Required.

---

## 판단 4. OQ-1·OQ-4가 추가 조사를 필요로 하는가

### Evidence — OQ-1

OQ-1: "H-5는 지금 확정돼야 하는가, 계속 Defer해도 상위 설계가 막히지
않는가?" `ADC-0003` 판단 1b의 원 논리: "두 후보(주입/해시) 중 하나를
지금 고르면, 근거 없이 한쪽을 고정하는 것이 된다. 반면 고르지
않아도 상위 설계가 막히지 않는다." 판단 1(위)이 이미 이 논리가
**지금도 그대로 유효함**을 확인했다(진행 불가 기준 불충족).

### Evidence — OQ-4

OQ-4: "`ADC-0007` 판단 4의 재검토 조건(이중성으로 인한 실제 문제
1회 이상, **또는** 두 번째 문서에서 기존 어휘로 표현하려다 실패하는
사례)이 8개 ad hoc 패턴으로 충족됐다고 볼 수 있는가?" 8개 패턴을
직접 검토하면, 그중 어느 것도 "Identity"나 "Ownership" 어휘를
**시도했다가 실패한** 사례가 아니다 — 이들은 Kernel Context Model
자체를 전혀 인지하지 못한 채 독립적으로 작성된 HQ 코드다(`RFC-0045`
§3.3). "어휘를 쓰려다 실패했다"와 "그 어휘를 애초에 쓴 적이 없다"는
다른 사실이다.

### Decision

## **둘 다 추가 조사가 필요 없다 — 현재 Evidence만으로 답할 수 있다**

- **OQ-1**: **아니오, 지금 확정할 필요가 없다.** `ADC-0003` 판단
  1b의 Defer 논리가 그대로 유효하다(판단 1 재확인).
- **OQ-4**: **아니오, 재검토 조건은 충족되지 않았다.** 8개 패턴은
  "어휘를 시도하다 실패한 사례"가 아니라 "어휘 자체를 접한 적이
  없는 독립 코드"다 — `ADC-0007` 판단 4의 재검토 조건 후半과
  문언상 다르다.

### Decision Rationale

두 질문 모두 새로운 조사가 아니라 **기존 문서(ADC-0003, ADC-0007)의
문언과 RFC-0045 자신의 Evidence를 정확히 대조하는 것만으로** 답이
나온다. 이것이 새로운 해석을 추가하는 것이 아님을 분명히 한다 —
`ADC-0007` 판단 4가 "재검토 조건"으로 명시한 두 문구를 그대로
가져와 8개 패턴에 기계적으로 대조했을 뿐이다.

### Next Step

No ADR Required.

---

## 판단 5. ADR이 지금 필요한가, 설계 확정 이후에만 필요한가

### Evidence

`ARCHITECTURE_GOVERNANCE.md`: "이 절차를 우회한 변경은 Baseline에
반영되지 않는다"(RFC→ADC→ADR→Baseline Update). 판단 1이 ADC 자체를
열지 않기로 했으므로, ADR의 전제(ADC의 Decision)가 존재하지 않는다.

RFC-0045 OQ-5는 별도 질문을 남겼다: 훗날 H-5/H-6이 실제로 확정될
때, `BASELINE.md` §14.4의 H-5/H-6 문언("Defer 상태다" / "미결
사항이다")을 "Accept(선택된 옵션)"로 바꾸는 것이 Baseline 개정(ADR
필요)인지, Hidden 항목이므로 ADC만으로 충분한지는 이 ADC의 판단
대상이 아니다 — §14.4 자체가 "Hidden Responsibilities" 절이며,
H-1~H-4의 선례(Ordering Policy 구현, Builder 내부 구조 등)는 모두
구현 세부사항으로서 Baseline 문언 자체를 건드리지 않고 처리되어
왔다는 점만 참고 사실로 기록한다 — **이것이 H-5/H-6에도 동일하게
적용되는지는 그 시점의 ADC가 직접 판단해야 한다.**

### Decision

## **지금은 불필요 — ADC가 열리고 실제로 Baseline 문언 변경이
필요한 것으로 그 ADC가 판단할 때만 필요하다**

### Decision Rationale

ADR은 Baseline을 실제로 바꾸는 단계다(`ARCHITECTURE_GOVERNANCE.md`
변경 절차). 지금은 ADC조차 열리지 않았으므로 ADR을 논할 단계가
아니다. 이 ADC는 미래의 그 판단을 대신하지 않는다 — H-1~H-4가
Baseline 문언 변경 없이 처리된 선례가 있다는 사실만 참고로 남긴다.

### Next Step

No ADR Required.

---

## 종합

| 판단 | Decision |
|---|---|
| 1. RFC-0045 ADC 승격 여부 | **Defer** — 두 채택 기준 모두 불충족 |
| 2. 단일/분리 ADC | **판정하지 않음** — 판단 1 결과로 질문 자체가 아직 발생하지 않음 |
| 3. Evidence 충분성 | **불충분** — 4개 필요 Evidence 항목 전부 0건 |
| 4. OQ-1·OQ-4 추가 조사 필요성 | **불필요** — 기존 문서 대조만으로 답변 가능(둘 다 "아니오") |
| 5. ADR 시점 | **지금 불필요** — ADC가 열리고 Baseline 문언 변경이 실제로 필요하다고 그 ADC가 판단할 때만 |

**이 ADC가 하지 않는 것**: H-5/H-6의 내용을 결정하지 않는다.
Kernel Context Builder/Renderer를 구현하지 않는다. `BASELINE.md`·
`ADC-0003`·`ADC-0006`·`ADC-0007`을 수정하지 않는다. Stable Prefix가
관찰됐다고 주장하지 않는다. A 조건 충족(이미 확정됨, 별도 Amendment
참고)을 B 조건 충족으로 취급하지 않는다 — 이 ADC의 어떤 판단도 B와
무관하다.

---

## Self Review

- H-5/H-6의 설계를 선호에 따라 선택했는가 — **아니오**. 이 ADC는
  RFC-0045의 옵션 목록에 손대지 않았다 — 승격 여부·Evidence
  충분성·재검토 조건만 판정했다.
- Stable Prefix가 관찰됐다고 주장했는가 — **아니오**.
- A 조건 충족을 B 조건 충족으로 취급했는가 — **아니오** — 이 ADC는
  B를 언급하되 판정하지 않았다.
- 8개 ad hoc 패턴을 Architecture 실패의 증거로 취급했는가 —
  **아니오**(판단 3) — 오히려 "0건"이라는 사실을 근거로 승격을
  Defer했다.
- `BASELINE.md`·기존 ADC 문서를 수정했는가 — **아니오**. 이 ADC
  파일 1건과 `RFC-0045` 상단 상태 노트(추가만, 본문 미변경) 외
  변경 없음.
- 기존 Defer 결정(ADC-0003 1b, ADC-0006 5, ADC-0007 4)을 뒤집었는가
  — **아니오** — 오히려 그 논리가 지금도 유효함을 재확인했을 뿐이다.
- Owner 권한을 참칭했는가 — **아니오** — 이 ADC는
  `ARCHITECTURE_GOVERNANCE.md`가 이미 정의한 객관적 2-기준 테스트를
  RFC-0045 자신의 Evidence에 기계적으로 적용했을 뿐이며, 이는
  `ADC-0003`/`ADC-0006`/`ADC-0007`을 Claude Code가 동일한 방식으로
  작성해 온 것과 같은 절차다. 새로운 Governance 해석을 추가하지
  않았다.
- 새 Layer·Component·Runtime·Concept를 도입했는가 — **아니오**.
- Kernel Context Builder/Renderer를 구현했는가 — **아니오**.

---

## Architecture / Governance Review

| 점검 | 결과 |
|---|---|
| `ARCHITECTURE_GOVERNANCE.md` ADC 채택 기준을 정확히 적용했는가 | **예** — 두 조건을 RFC-0045 §3.4·§8의 실측치에 직접 대조 |
| `ADC-0003`·`ADC-0006`·`ADC-0007`의 기존 Decision을 뒤집는가 | **아니오** — 오히려 그 논리의 현재 유효성만 재확인 |
| Baseline을 수정하는가 | **아니오** |
| 새 Architecture 책임·Component를 추가하는가 | **아니오** |
| H-5/H-6 내용을 확정하는가 | **아니오** |
| Stable Prefix 관찰을 주장하는가 | **아니오** |
| 이 ADC 자체가 Baseline 변경을 요구하는가 | **아니오 — ADR 불필요** |

**판정**: PASS.

---

## Traceability

| 문서/절 | 관계 |
|---|---|
| `RFC-0045-context-segment-identifier-metadata-contract.md` §3.4, §8, §11 | 이 ADC의 직접 Evidence 근거 |
| `ADC-0003-kernel-context-model.md` 판단 1b | H-5 Defer 논리의 원 출처, 판단 1·4의 재확인 대상 |
| `ADC-0006-kernel-context-ownership.md` 판단 5·8 | Ownership Defer 선례, V-1 미종결 확인 |
| `ADC-0007-kernel-context-identity.md` 판단 1·4 | Identity Reject/Defer 선례, 재검토 조건의 원 출처(판단 4) |
| `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준", "Experimental Implementation" | 이 ADC의 판정 기준 |
