# ADC-0030: `provider_connections.priority` 구현 착수 선행조건 — Responsibility 재설계 (ADC-0027 후속)

## 목적

`docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
§Decision "구현 착수 선행조건" 2번(FAIL 3건 재해소 중 `priority`
항목)을 재검토한다. `ADC-0028`이 `domain_fallback_chains`를,
`ADC-0029`가 `routing_decisions`를 각각 좁게 처리했던 것과 동일한
방식으로, 이 ADC는 **`priority` 항목 하나에만** 답한다. 이것은
`priority` 구현 작업이 아니라, `ADC-0027`이 OmniRoute 도입 선행조건으로
요구한 `priority`의 의미와 필요성을 재검토·공식 결정하는 Governance
작업이다.

직전 Read-only Verification(2026-09-06)이 다음을 확인했다.

1. `priority`는 DB retrieval ordering에 사용된다(`providers.ts::
   getRawProviderConnections()` "`ORDER BY priority ASC, updated_at
   DESC`").
2. priority를 바꾸면 read-only candidate listing(`/api/v1/auto-combo/
   auto/candidates`, 격리 환경에서 실제 A/B 테스트로 확인) 결과의
   connection 순서가 실제로 바뀐다.
3. `virtualFactory.ts::computeSnapshotWeights()`의 7개 scoring factor
   (`taskFit`/`stability`/`tierPriority`/`costInv`/`latencyInv`/
   `health`/`quota`)에는 DB `priority`가 없다.
4. 실제 dispatch-time 최종 랭킹 함수 `autoStrategy.ts::
   scoreAutoTargets()`가 사용하는 `ProviderCandidate` 인터페이스에도
   DB `priority`에 해당하는 field가 없다.
5. 따라서 `priority`가 scoring factor라는 근거는 없다.
6. score가 동일한 경우 JS stable sort와 기존 배열 순서 때문에
   간접적으로 영향을 줄 가능성은 있으나, 실제 최종 dispatch selection
   까지는 검증하지 않았다(안전 경계상 실제 provider 호출 진입 직전에서
   멈췄다).
7. 따라서 최종 selection 영향은 **UNVERIFIED**로 남는다.
8. 현재 `priority`를 "routing priority" 또는 "정책적 우선순위"라고
   표현하는 것은 근거가 부족하다.

이 ADC는 이 확인을 근거로, `ADC-0027`이 자신이 만든 `priority`
precondition을 계속 유지할 필요가 있는지를 공식적으로 결정한다.

근거는 `ADC-0027`, `ADC-0028`, `ADC-0029`, `EVIDENCE-0001-omniroute-
precondition-verification.md`, `EVIDENCE-0002-omniroute-domain-budgets-
execution-verification.md`, `RFC-0023`, `CONSTITUTION.md`,
`BASELINE.md`, `ARCHITECTURE_GOVERNANCE.md`, `docs/governance/adc/
ADC-0003.md`, 그리고 직전 Read-only Verification이 확인한 OmniRoute
소스 경로(아래 §Q1·§Q2)로만 한정한다. 새로운 실험·Evidence를 만들지
않는다.

### 이 ADC가 답하지 않는 것

- **`domain_fallback_chains`** — `ADC-0028`이 이미 처리했다. 재론하지
  않는다.
- **`domain_budgets`** — `EVIDENCE-0002`가 PASS로 확인했다. 재론하지
  않는다.
- **`routing_decisions`** — `ADC-0029`가 이미 처리했다. 재론하지
  않는다.
- **`IMPLEMENTATION_RULES.md` Scoped 완화** — 판단보류 그대로 유지,
  이 ADC는 다루지 않는다.
- **`priority` 구현, scoring code 변경, candidate selection code
  변경** — 이 ADC는 어떤 코드 구현·수정도 승인하지 않는다.
- **`provider_connections` schema 변경** — `priority` column을
  삭제하거나 의미를 재정의하지 않는다.
- **OmniRoute Integration 착수 승인** — `ADC-0027`의 Production 구현
  차단은 유지된다.
- **Jarvis OS가 별도 provider-priority engine을 구현하기로 선언하는
  것** — 아래 §Decision Boundary가 명시하듯, 이 ADC는 그런 선언을
  하지 않는다.
- **"priority 개념 자체가 영구적으로 불필요하다"는 확정** — 이
  Decision은 "현재 execution scope에서 추가 구현/보장이 필요 없다"는
  판단이지, 미래에도 provider selection policy가 필요할 수 없다는
  뜻이 아니다(§Decision Boundary·§Reversibility).
- **`ADC-0027`·`ADC-0028`·`ADC-0029`·`CONSTITUTION.md`·`BASELINE.md`·
  `ARCHITECTURE_GOVERNANCE.md`·Engine Adapter Contract 파일의 실제
  수정** — 방향만 제시하고 실행은 하지 않는다.
- **ADR 작성** — 하지 않는다.

---

## Q1. Jarvis Governance가 provider priority를 요구하는가

### 검토

상위 Governance 문서 4개를 `priority`·`routing priority`·
`provider priority`·`candidate`·`selection`·`scoring`·`tier`·
`policy`·`routing policy`·`fallback`·`provider` 키워드로 재확인했다.

| 문서 | 확인 결과 |
|---|---|
| `hqs/development/CONSTITUTION.md` | "Model Routing"이 Architecture Freeze 목록의 항목명으로만 존재(220~236행). `priority`/`provider`/`candidate`/`scoring`/`tier` 등 세부 구현 개념에 대한 서술 없음. |
| `docs/architecture/baseline/BASELINE.md` | "Routing" 언급은 전부 HQ Routing/Registry·Dynamic Routing(Multi-HQ 작업 분해, Workflow 조건부 분기) 개념 — OmniRoute의 provider/connection 우선순위와 무관. `priority`/`provider priority`/`tier` 매치 없음. |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` | Engine Gateway/Routing/Adapter 관련 유일한 언급은 "Frozen/Deferred Boundary 우회 금지" 조항. `priority`/`provider`/`scoring`/`tier` 매치 없음. |
| `docs/governance/adc/ADC-0003.md` | 매치 없음. |

### Q1 결론

- **Explicit requirement**: 없음.
- **Implicit requirement**: 없음 — "Model Routing"이 Freeze 목록에
  존재한다는 사실은 "무엇을 라우팅 기준으로 삼을지"에 대한 어떤
  서술도 포함하지 않는다. Freeze 항목명 하나로부터 `provider_
  connections.priority`라는 특정 컬럼·메커니즘의 필요성을 추론할
  근거는 없다.
- **Not Defined**로 판정한다.

`priority`에 대한 요구(FAIL 판정, "Routing Policy" 축과의 연결)는
`RFC-0023`(§3.3, §6)·`ADC-0027`(§Q4, §Decision Responsibility 표,
선행조건 2)이 스스로 도입한 것이며, 상위 Governance 문서 어디에도
그 상위 근거가 없다 — `ADC-0029`가 `routing_decisions`에 대해 내린
것과 동일한 구조의 결론이다.

---

## Q2. `ADC-0027`이 요구한 `priority`는 정확히 무엇인가

### 검토

`ADC-0027` 원문의 `priority` 관련 문장을 전수 재대조했다.

- §Q4 표(148~150행): `priority`(FAIL) | 성격: **"라우팅 정책 실행"**
  | "근거로 쓰지 않는다 — 오히려 §Q5·§Decision의 선행조건을 발생시키는
  반대 방향 Evidence로 사용".
- §Q4 핵심 관찰(155~163행): "**Routing Policy**"(Jarvis OS가
  우선순위·fallback 체인을 정책으로 결정)는 Om니Route의 `priority`·
  `domain_fallback_chains` **실행**이 전제돼야 의미가 있고..."
- §Decision 선행조건 2(369~372행): "`priority`, `domain_fallback_
  chains`, `routing_decisions`가 재검증에서 PASS로 확인되거나, PASS로
  확인될 수 없다면 Responsibility 분담(Routing Policy·Audit Policy
  축)이 그 실패를 전제로 재설계돼야 한다."

이를 §3 분류(A~E)에 대조한다.

- **A(column 존재)**: `ADC-0027` 작성 시점에도 이미 충족돼 있었다
  (`EVIDENCE-0001` §3.2가 이후 확인). 원문이 이것을 FAIL로 지목한
  것이 아니다 — column 존재 자체는 애초에 쟁점이 아니었다.
- **B(DB retrieval ordering 사용)**: 마찬가지로 이미 코드에 존재했다
  (`ORDER BY priority ASC`). 원문의 FAIL 판정 시점에 이 사실이
  이미 관찰 가능했음에도 FAIL로 분류됐다는 것은, 원 평가자가 B만으로는
  충족되지 않는 **더 높은 수준의 무언가**를 기준으로 삼았다는 것을
  시사한다.
- **C(candidate selection 영향)/D(scoring factor)/E(정책적 provider
  선택 우선순위 보장)**: §Q4가 `priority`를 "**라우팅 정책 실행**"
  으로 명명하고 "**Routing Policy**"(Jarvis가 정책으로 결정한 우선
  순위·fallback을 OmniRoute가 실제로 실행하는 것) 축에 직접 연결한
  것은, C~E 중 하나(또는 그 이상)를 의도했음을 강하게 시사한다.
  그러나 원문은 "실행"이 정확히 candidate selection에 직접 반영되는
  것을 의미하는지(C), scoring 산식에 편입되는 것을 의미하는지(D),
  아니면 "낮은 priority 값을 가진 connection이 항상 우선 시도된다"는
  절대적 보장을 의미하는지(E)를 **구체적으로 특정하지 않았다**.

### Q2 결론

**정의 불충분(Under-specified).** `ADC-0027`의 `priority` 요구는
A/B 수준(이미 충족돼 있었음에도 FAIL 처리됐다는 사실 자체가 이를
방증한다)을 넘어서는 C~E 어딘가를 의도했으나, 그중 정확히 무엇을
요구하는지 원문 자체에서 확정할 수 없다. 이는 `ADC-0027`의 결함이라기
보다, `RFC-0023`의 원본 5라운드 검증이 "priority가 실제로 후보 선정에
영향을 주는지"를 differentiated 데이터로 실증하지 못한 채(당시 모든
connection이 priority=1로 무차별) FAIL을 내린 것에서 비롯된 모호성
이다(`EVIDENCE-0001` §3.2).

---

## 중요한 구분(명제별 독립 판정)

| 명제 | 현재 상태 |
|---|---|
| `priority` column 존재 | **확인** |
| DB `ORDER BY`에 `priority` 사용 | **확인** |
| candidate listing order 영향 | **실행 확인**(격리 환경 A/B 테스트, 우선순위 역전 시 순서 정확히 반전) |
| scoring factor | **사용되지 않음**(`computeSnapshotWeights()`·`scoreAutoTargets()`가 사용하는 `ProviderCandidate` 양쪽 다 확인) |
| tie-break 영향 | **UNVERIFIED**(JS stable sort 구조상 가능성은 있으나 실제 dispatch 진입 없이는 미실증) |
| 최종 selected candidate 영향 | **UNVERIFIED** |
| 정책적 routing priority 보장 | **확인되지 않음** |

이 표를 근거로 "`priority`가 구현됐다/안 됐다"는 단순 이분법적
결론을 내리지 않는다 — 각 명제는 서로 다른 수준의 사실이며 독립적으로
참·거짓·미확정이다.

---

## Decision

**Accept (Scoped, Narrow) — 현재 execution scope에서
`provider_connections.priority`를 OmniRoute Model Routing / Execution
Layer(`ADC-0027` Scope) 구현 착수의 필수 선행조건에서 제외한다.**

### Reason

1. 상위 Jarvis Governance(§Q1)에는 provider priority에 대한 명시적
   또는 묵시적 요구가 없다(Not Defined).
2. OmniRoute에서 `priority`가 실제 DB retrieval ordering 및 그로부터
   파생되는 candidate listing 순서에 사용되는 것은 실행으로 확인됐다
   (위 표 1~3행).
3. 그러나 실제 Auto-Combo scoring factor로는 사용되지 않는다(위 표
   4행, 두 개의 독립된 scoring 구현 모두에서 확인).
4. 최종 selection(tie-break 포함)에 대한 영향은 아직 UNVERIFIED다
   (위 표 5~6행) — 이는 "없다"가 아니라 "확정할 수 없다"는 뜻이며,
   이 Decision은 이 불확실성을 인정한 채로 내려진다.
5. `ADC-0027`이 §Q2에서 확인한 대로 "정책적 provider priority 실행"
   (C~E 어딘가)을 정확히 요구했는지 자체가 원문상 특정되지 않는다
   (정의 불충분) — 특정되지 않은 요구를 근거로 구현 착수를 계속
   차단할 Architecture상의 근거가 부족하다.

이 다섯 가지를 종합하면, "현재 execution scope에서 `priority`를
추가로 구현·보장할 필요가 없다"는 결론이 소스·Governance 문서 양쪽과
정합적이다.

### Decision Boundary

이 Decision이 의미하는 것과 의미하지 않는 것을 명확히 구분한다.

**의미하는 것**: **"현재 도입을 위해 `priority`를 추가로 구현/보장할
필요가 없다."**

**의미하지 않는 것**: "`priority`라는 개념 자체가 영구적으로
불필요하다."

구체적으로:

- `provider_connections.priority` column을 삭제하지 않는다.
- 현재 DB retrieval ordering 구현(`ORDER BY priority ASC`)을
  제거하지 않는다.
- OmniRoute 소스를 수정하지 않는다.
- `priority`의 의미를 새롭게 "routing policy"로 재정의하지 않는다 —
  §Q2가 확인한 "정의 불충분" 상태를 이 ADC가 임의로 확정하지 않는다.
- Jarvis OS가 별도 provider-priority engine을 구현한다고 선언하지
  않는다 — "만들지 않는다"는 소극적 결정이지 "대신 무엇을 만든다"는
  적극적 결정이 아니다.
- 향후 다음 중 하나라도 실제로 관찰되면 이 Decision을 재검토
  대상으로 등록한다(§Reversibility).

### Responsibility Boundary

- **OmniRoute의 실제 실행**: `priority` 기반 DB 조회 정렬 및
  candidate listing 순서 반영은 이미 실제로 동작한다(`ADC-0028`이
  `domain_fallback_chains`에 대해, `ADC-0029`가 `routing_decisions`에
  대해 그랬듯, 이 ADC도 새로운 코드를 만들거나 승인하지 않는다).
- **Jarvis OS의 Governance**: 어떤 provider 선택 정책을 요구할지
  결정하는 상위 정책 책임(`ADC-0027` §Q5 "Routing Policy" 축)은
  유지된다 — 다만 그 정책이 `priority`라는 특정 메커니즘을 통해
  "보장된 실행"으로 구현돼야 한다는 전제만 제거한다. Jarvis OS가
  실제로 무엇을 provider 선택 기준으로 요구하는지는 이 ADC가
  판단하지 않는다(§Out of Scope) — 실제 요구사항이 생기면 별도
  Architecture Decision 대상이다.
- **`priority`(정책적 보장) 자체**: 현재 OmniRoute 통합을 위해
  Jarvis OS가 별도로 구현하지 않는다.

### Scope

이 ADC가 변경하는 판단은 오직 다음으로 한정한다.

- `priority` requirement의 재검토(A~E 분류, Q1/Q2)
- `ADC-0027` 선행조건 2 중 `priority` 항목의 재설계

다음은 명시적으로 제외한다.

- `priority` 구현, scoring code 변경, candidate selection code 변경
- `provider_connections` schema 변경
- OmniRoute 소스 변경
- `routing_decisions`(`ADC-0029` 상태 유지), `domain_budgets`
  (`EVIDENCE-0002` 상태 유지), `domain_fallback_chains`(`ADC-0028`
  상태 유지)
- `IMPLEMENTATION_RULES.md` 변경
- Architecture Contract 변경, Architecture Freeze 변경
- OmniRoute Integration 착수
- ADR 작성

### Evidence

- 사용한 것: 직전 Read-only Verification의 source-level 전수 추적
  (§목적 1~8), 격리 환경 A/B 실행 결과(candidate listing 순서
  반전 확인), §Q1의 4개 Governance 문서 전수 검색(0건), §Q2의
  `ADC-0027` 원문 재대조(A~E 분류).
- 사용하지 않은 것(과장 배제): tie-break·최종 selection 영향(위 표
  5~6행)은 UNVERIFIED 그대로 두고, 이를 "영향 없음"으로 확정하지
  않았다 — 확정할 근거가 없기 때문이다. "priority가 routing priority
  또는 정책적 우선순위를 보장한다"는 표현도 사용하지 않았다.

### Gate Impact

`ADC-0027` Implementation Gate 전체 현황:

| 조건 | 상태 |
|---|---|
| `domain_fallback_chains` | `ADC-0028`로 해소(Responsibility redesign accepted) |
| `domain_budgets` | `EVIDENCE-0002`로 PASS(실제 blocking 확인) |
| `routing_decisions` | `ADC-0029`로 선행조건 제외(Responsibility redesign accepted) |
| `priority` | **이 ADC로 선행조건 제외**(Responsibility redesign accepted) |
| `IMPLEMENTATION_RULES.md` | 판단보류(무변경) |

**`priority`를 선행조건에서 제외한다고 해서 전체 OmniRoute
Integration Gate가 자동으로 PASS 되는 것은 아니다.** `IMPLEMENTATION_
RULES.md` Scoped 완화가 판단보류로 남아 있는 한 `ADC-0027`의
"Production 구현 착수는 선행조건이 모두 충족되기 전까지 차단된다"는
문언은 계속 유효하다. 선행조건 2(`priority`/`domain_fallback_chains`/
`routing_decisions`)는 이 ADC로 3건 모두 처리됐지만, 선행조건 1
(Evidence 영속화, `EVIDENCE-0001`/`EVIDENCE-0002`로 충족)과 3
(`domain_budgets`, `EVIDENCE-0002`로 PASS)이 이미 해소된 것과 별개로,
**선행조건 4(`IMPLEMENTATION_RULES.md` Scoped 완화)는 여전히 미해소
상태**로 남아 실제 구현 착수를 계속 차단한다.

### Reason

- Q1 — 4개 상위 Governance 문서 전수 검색 결과 provider priority를
  요구하는 문장이 없음을 확인했다.
- Q2 — `ADC-0027`의 `priority` 요구가 A/B 수준을 넘어서는 것을
  의도했으나 정확히 무엇(C/D/E)인지 원문상 특정되지 않는다는 것을
  확인했다.
- 위 §4 표의 7개 명제를 개별로 판정한 결과, "정책적 provider priority
  보장"이 확인되지 않았고, 그 미확인 상태를 근거로 구현 착수를 계속
  차단할 Architecture상의 근거가 부족하다.

### Decision Rationale

이 Decision은 `ADC-0027`의 Decision(Accept, Conditional, Scoped)을
재론하지 않는다 — `ADC-0027`이 연 선행조건 2의 마지막 잔여 항목
하나(`priority`)를 재설계할 뿐이다. `ADC-0027`의 Scope·Responsibility
표·Decision Boundary(Reversibility)는 모두 그대로 유지된다. **이 ADC는
`ADC-0027`/`ADC-0028`/`ADC-0029` 파일 자체를 수정하지 않는다** — 동일
구조(후속 Governance Decision으로 개별 precondition의 책임/필요성만
재설계)를 유지한다.

---

## Out of Scope

- `priority` 구현, scoring code 변경, candidate selection code 변경.
- `provider_connections` schema 변경(column 삭제·의미 재정의 포함).
- OmniRoute 소스 변경, OmniRoute Integration 착수.
- `routing_decisions`(무변경), `domain_budgets`(무변경),
  `domain_fallback_chains`(무변경).
- `IMPLEMENTATION_RULES.md` 실제 수정 또는 그 필요성의 최종 확정.
- Engine Adapter Contract(§14)의 실제 확정.
- `CONSTITUTION.md`·`BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md` 문구의
  실제 수정.
- ADR 작성.
- `ADC-0027`·`ADC-0028`·`ADC-0029` 파일의 직접 수정.

## Risks

- **"priority 개념 전면 폐기"로 오독될 위험**: 이 Decision이
  "`priority` 컬럼/메커니즘 자체가 불필요하다"로 확대 해석될 위험 —
  §Decision Boundary에서 "column 삭제 안 함, 구현 제거 안 함, 개념
  영구 폐기 아님"을 명시적으로 반복했다.
- **정의 불충분(§Q2) 상태의 잔존**: `ADC-0027`이 정확히 무엇을
  요구했는지 이 ADC도 완전히 해소하지 못했다 — "정의 불충분"이라는
  판정 자체가 남은 모호성이며, 향후 Jarvis가 구체적 provider selection
  policy를 정의하면 그 모호성이 실제 요구로 구체화될 수 있다
  (§Reversibility).
- **tie-break UNVERIFIED 상태의 오독 위험**: "확정할 수 없다"가
  "영향이 없다"로 읽힐 위험 — §4 표와 §Evidence에서 반복적으로
  구분했다.
- **`ADC-0027` 선행조건 2 잔여 항목과의 혼동 위험**: `ADC-0028`
  (`domain_fallback_chains`)·`ADC-0029`(`routing_decisions`)·이 ADC
  (`priority`)로 선행조건 2의 3개 항목이 모두 개별 처리됐다 — 이것이
  "선행조건 2 전체 PASS"로 뭉뚱그려 읽히지 않도록 §Gate Impact 표에서
  개별로 나열했다.

**재검토 조건**: `ADC-0027` §Risks의 "FAIL 항목이 구조적 결함일
가능성" 절과 동일한 원칙을 적용한다.

## Reversibility

향후 다음 요구가 생기면 별도 Architecture Decision으로 재검토할 수
있다.

- Jarvis가 provider selection policy를 명시적으로 정의하는 경우.
- 특정 provider/account에 대한 우선순위 정책이 실제 제품 요구사항이
  되는 경우.
- deterministic provider selection이 Kernel/Execution Contract의
  요구사항이 되는 경우.
- scoring/tie-break policy가 Governance requirement가 되는 경우.

이 ADC가 향후 provider priority policy 자체를 영구적으로 금지하는
것으로 해석되지 않는다.

## Next Step

1. `IMPLEMENTATION_RULES.md` Scoped 완화는 별도 Observation/
   Architecture Decision 대상으로 그대로 남는다 — 이 ADC는 그 작업을
   앞당기지 않는다.
2. `ADC-0027` 선행조건 1~4가 전부(각자의 방식으로) 해소되면, `ADC-0027`
   §Next Step이 예정한 후속 ADR이 `CONSTITUTION.md`·`BASELINE.md`·
   `IMPLEMENTATION_RULES.md`의 실제 Scoped 반영을 수행한다.
3. Jarvis 쪽에 명시적 provider selection policy가 관찰되면 이 ADC를
   재검토 대상으로 등록한다(§Risks·§Reversibility).

## Governance Chain 검증

`RFC-0023`(Proposed) → `ADC-0027`(Accept, Conditional·Scoped) →
`ADC-0028`(Accept, Scoped, Narrow — `domain_fallback_chains`) →
`ADC-0029`(Accept, Scoped, Narrow — `routing_decisions`) →
`EVIDENCE-0002`(Evidence — `domain_budgets` PASS) → 이 ADC(Accept,
Scoped, Narrow — `priority`) → 후속 ADR(예정, 선행조건 4 해소 후
Baseline·Rules 반영). 이 ADC는 `ADC-0027`이 열어 둔 선행조건 2의
마지막 잔여 항목을 재설계했을 뿐, `ADC-0027`·`ADC-0028`·`ADC-0029`의
Decision 자체를 재론하지 않았다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**. Jarvis
  OS가 새 provider-priority engine을 구현한다고 선언하지 않았다.
- Contract Change — **없음**.
- `CONSTITUTION.md`·`BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·Engine
  Adapter Contract 문서를 이 ADC가 수정했는가 — **아니오**.
- Architecture Freeze를 해제했는가 — **아니오**.
- OmniRoute Integration을 허용하는 문구가 들어갔는가 — **아니오**
  (§Gate Impact에서 "전체 Gate 자동 PASS 아님", 선행조건 4 잔존을
  명시).
- 다른 precondition(`domain_fallback_chains`/`domain_budgets`/
  `routing_decisions`/`IMPLEMENTATION_RULES.md`)을 임의로 변경했는가 —
  **아니오**(§Gate Impact 표에서 각각 무변경으로 명시).
- `provider_connections.priority` column을 삭제·재정의했는가 —
  **아니오**(§Decision Boundary).
- ADR이 필요한가 — 이 ADC 자체는 아니오. 선행조건 4가 완료된 뒤
  `ADC-0027`이 이미 예정한 후속 ADR이 별도로 필요하다.

## Self Review

- 상위 Governance와 `ADC-0027` requirement를 분리했는가 — **Pass**
  (§Q1: Not Defined, §Q2: `ADC-0027` 자체 요구는 정의 불충분으로
  각각 독립 판정).
- `ORDER BY priority`를 routing priority implementation으로
  과장했는가 — **아니오**(§4 표에서 "DB ordering 확인"과 "정책적
  routing priority 보장 확인되지 않음"을 별도 행으로 분리).
- scoring 미사용과 최종 selection 미검증을 구분했는가 — **Pass**
  (§4 표 4행 vs 5~6행, §Evidence에서 재확인).
- tie-break 가능성을 확정 사실로 만들었는가 — **아니오**(UNVERIFIED로
  일관 유지, §Risks에서 오독 위험까지 명시).
- `priority`를 영구적으로 폐기한다고 선언했는가 — **아니오**
  (§Decision Boundary·§Reversibility에서 명시적으로 부정).
- 다른 precondition을 변경했는가 — **아니오**(§Gate Impact, §Out of
  Scope).
- 전체 Integration Gate를 자동 PASS 처리했는가 — **아니오**(§Gate
  Impact에서 선행조건 4 잔존을 명시).
- Architecture/Contract/Freeze를 변경했는가 — **아니오**(이 ADC 파일
  외 어떤 파일도 생성·수정하지 않았다).
- OmniRoute Integration을 허용했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**.
- `ADC-0027`/`ADC-0028`/`ADC-0029` 파일을 직접 수정했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
