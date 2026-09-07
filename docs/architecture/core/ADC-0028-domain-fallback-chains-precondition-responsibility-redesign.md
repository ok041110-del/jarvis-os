# ADC-0028: `domain_fallback_chains` 구현 착수 선행조건 — Responsibility 재설계 채택 (ADC-0027 후속)

## 목적

`docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
§Decision "구현 착수 선행조건" 2번("FAIL 3건 재해소: `priority`,
`domain_fallback_chains`, `routing_decisions`가 재검증에서 PASS로
확인되거나, PASS로 확인될 수 없다면 Responsibility 분담(Routing
Policy·Audit Policy 축)이 그 실패를 전제로 재설계돼야 한다(§Q4의
비대칭 해소)")을, **`domain_fallback_chains` 항목 하나에 한해** 두
경로 중 어느 쪽으로 해소할지 결정한다.

`ADC-0027` 자신은 이 선택을 미리 하지 않고 후속 Observation/Decision에
위임했다(§Next Step 1: "선행조건 1~3(Evidence 영속화, FAIL 3건 재해소
또는 Responsibility 재설계, `domain_budgets` 확정)이 실제로 충족되는지
먼저 확인한다 — 이 확인 자체는 새 Observation/Evidence Review
대상이며 이 ADC의 범위 밖이다"). 이후 두 차례의 Observation(2026-09-06, "Implementation
Gate Blocking 조건 해소를 위한 Observation/Validation", "Gate 재정의를
위한 Governance Review")이 `domain_fallback_chains`가 재검증 PASS
경로로는 해소될 수 없는 orphaned legacy임을 확인했다 — 이 ADC는 그
결과에 대해 "②Responsibility 재설계" 경로를 공식 채택할지만 결정한다.

근거는 `ADC-0027`, `EVIDENCE-0001-omniroute-precondition-verification.md`,
`RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`,
`hqs/development/CONSTITUTION.md`(Architecture Freeze·Observation
Policy·Evidence Review 원칙), `docs/architecture/baseline/BASELINE.md`
§14.1·§16.2, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`, 그리고
위 두 Observation 세션이 확인한 OmniRoute 소스 경로(아래 §Q1)로만
한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- **`routing_decisions` durable audit 방식** — `ADC-0027` §Decision
  선행조건 2 중 이 항목은 그대로 미해결 상태로 남긴다(§Scope).
- **`domain_budgets` 검증 결과** — 선행조건 3, 그대로 미해결.
- **`priority` 차등 selection 실증** — 선행조건 2의 다른 축, 그대로
  미해결.
- **`IMPLEMENTATION_RULES.md` Scoped 완화**(선행조건 4) — 그대로
  미해결. 이 ADC의 Accept는 이 완화를 앞당기지 않는다.
- **Engine Adapter Contract의 실제 확정, Architecture Freeze 문구의
  실제 수정** — `ADC-0027`과 동일하게 방향조차 이 ADC가 직접
  수행하지 않는다(§Gate Impact 참조, 실행은 후속 ADR 몫).
- **OmniRoute 통합 구현 착수 승인** — 이 ADC는 어떤 코드 구현도
  승인하지 않는다. `ADC-0027`의 Production 구현 차단은 유지된다
  (§Decision, §Gate Impact).
- **Jarvis OS가 새 fallback engine을 구현하기로 선언하는 것** —
  아래 §Responsibility Boundary가 명시하듯, 이 ADC는 그런 선언을
  하지 않는다.
- **`domain_fallback_chains`를 향후 영구적으로 배제하는 것** — 이
  Decision은 "현재 OmniRoute execution scope에서 불필요"라는 판단이지,
  미래에 실제 요구사항이 생겨도 재검토할 수 없다는 뜻이 아니다
  (§Decision Boundary).

---

## Q1. Evidence 재확인 — orphaned legacy 판단이 충분한가

### 검토

두 차례 Observation이 각각 독립적으로 확인한 사실을 다시 대조한다.

1. **실제 라이브 Auto-Combo 실행 경로에 참조 없음**: OmniRoute의 실제
   Auto-Routing 후보 생성/스코어링 코드
   (`open-sse/services/autoCombo/virtualFactory.ts`, 995줄)를
   `priority|domain_fallback_chains|fallbackPolicy|routing_decisions|
   logRoutingDecision` 패턴으로 전수 검색한 결과 0건. 이 파일은
   실제 운영 로그(`[AUTO] ... matched no connected models`)의
   발생지로 확인된 파일이다 — 즉 "검사가 부족해서 못 찾은 것"이
   아니라 "실제 라이브 경로 자체에 이 기능에 대한 참조가 없다"는
   전수 확인이다.
2. **실제 fallback은 완전히 별도 시스템이 담당**: `open-sse/services/
   accountFallback.ts`(`isAccountUnavailable`/`isModelLocked`,
   `rateLimitedUntil`/`testStatus` 기반)와 `open-sse/services/combo/
   decisionTrace.ts`의 `ComboSkipReason`(`circuit_open`/
   `provider_cooldown`/`model_lockout`/`quota_cutoff`/`availability`/
   `credential_gate`/`concurrency_cap`/`admission_lane`/
   `predictive_ttft`)이 실제 dispatch 루프(`combo.ts`, 실제 HTTP
   상태 200/504/503 분기 지점)에서 호출된다. 이 두 파일 어디에도
   `domain_fallback_chains`/`fallbackPolicy`/`registerFallback`/
   `resolveFallbackChain` 참조가 없다.
3. **`registerFallback`/`resolveFallbackChain` external caller
   0건**: 정의 파일(`src/domain/fallbackPolicy.ts`) 자기 자신을
   제외하면 저장소 전체에서 호출하는 코드가 없다(전수 검색,
   `EVIDENCE-0001` §3.3 OB-16 및 후속 Observation이 재확인).
4. **유일한 소비 경로 자체가 dead code**: `src/domain/
   policyEngine.ts::evaluateRequest()`가 `resolveFallbackChain`을
   호출하지만, 이 함수를 실제로 resolve해서 쓰는 코드가 `src/lib/
   container.ts`의 DI 등록(`container.register("policyEngine", ...)`)
   외에는 존재하지 않는다(`EVIDENCE-0001` §3.3 OB-15).

### Q1 결론

**충분하다.** 위 네 가지는 "관찰 부재"가 아니라 "부재의 전수 확인"이며,
서로 다른 세 개의 독립 경로(라이브 실행 경로 자체, 호출자 검색,
DI resolve 검색)가 같은 결론(미사용·미연결·미소비)을 가리킨다.
`CONSTITUTION.md` Observation Policy("사실만 기록한다")와 Evidence
Review 원칙이 요구하는 재현 가능한 근거 수준을 충족한다.

---

## Q2. ADC-0027 선행조건 2의 어느 경로를 채택하는가

### 검토

`ADC-0027` §Decision 선행조건 2는 두 경로를 열어뒀다.

- **① 재검증 PASS**: `domain_fallback_chains`가 재검증에서 실제로
  동작하는 것으로 확인되는 경로. — §Q1의 네 가지 사실은 이 경로를
  **닫는다**. 저장 계층(`domainState.ts`)과 1차 소비자
  (`fallbackPolicy.ts`)는 코드로서 존재하지만, 그 값을 실제 요청
  처리에 반영할 경로 자체가 dead code이므로 "재검증"을 반복해도
  같은 결과(0 rows, 0 caller)가 나올 수밖에 없는 구조다.
- **② Responsibility 재설계**: PASS로 확인될 수 없다면, Jarvis OS
  쪽 "Routing Policy" 책임이 `domain_fallback_chains` 실행을 전제로
  하지 않도록 재설계하는 경로. — §Q1이 확인한 대체 메커니즘
  (`accountFallback.ts`/`decisionTrace.ts`)의 존재는, 이 재설계가
  "공백을 방치하는 것"이 아니라 "이미 실제로 동작 중인 다른 메커니즘을
  인정하는 것"임을 뒷받침한다.

두 경로 중 하나를 반드시 택해야 하는 것이지, 새로운 세 번째 선택지를
만드는 것이 아니다 — ①이 구조적으로 닫혀 있으므로 ②가 유일하게 남은
경로다.

### Q2 결론

**② Responsibility 재설계를 채택한다.** 아래 §Decision·§Responsibility
Boundary에서 그 재설계의 정확한 경계를 규정한다.

---

## Decision

**Accept (Scoped, Narrow) — `domain_fallback_chains`를 OmniRoute
Model Routing / Execution Layer(`ADC-0027` Scope) 구현 착수의
선행조건에서 제외한다.**

- `domain_fallback_chains`(및 그 1차 소비자 `src/domain/
  fallbackPolicy.ts`, 2차 소비자 `src/domain/policyEngine.ts`)는
  현재 OmniRoute의 실제 Auto-Combo execution에서 사용되지 않는
  **orphaned legacy**로 분류한다(§Q1).
- `ADC-0027` §Decision 선행조건 2의 **②Responsibility 재설계** 경로를
  `domain_fallback_chains`에 한해 채택한다 — Jarvis OS의 "Routing
  Policy"(`ADC-0027` §Q5 PDP/PEP 표) 책임은, OmniRoute가
  `domain_fallback_chains`를 통해 Jarvis가 지정하는 도메인별 커스텀
  fallback 체인을 실행해 줄 것이라는 전제를 갖지 않는다.
- 이 제외는 **`domain_fallback_chains` 항목 하나에만** 적용된다.
  `priority`·`routing_decisions`·`domain_budgets`·
  `IMPLEMENTATION_RULES.md` Scoped 완화는 `ADC-0027`이 규정한 상태
  그대로 유지되며, 이 ADC는 그중 어느 것도 해소하지 않는다(§Scope).

### Responsibility Boundary

- **OmniRoute의 실제 fallback execution**: `accountFallback.ts`
  (계정 가용성·모델 lockout 판단)와 `open-sse/services/combo/
  decisionTrace.ts` 계열(`ComboSkipReason` 기반 스킵·재시도 판단)이
  담당한다 — 이는 이미 실제로 동작 중인 기존 메커니즘이며, 이 ADC가
  새로 만들거나 승인하는 것이 아니다.
- **Jarvis OS의 Governance**: 어떤 routing/fallback 정책을 요구할지
  결정하는 상위 정책 책임(`ADC-0027` §Q5 "Routing Policy" 축)은
  그대로 유지된다 — 다만 그 정책을 `domain_fallback_chains`라는
  특정 메커니즘을 통해 실행시킬 수 있다는 전제만 제거한다. Jarvis
  OS가 실제로 필요로 하는 fallback 정책이 무엇인지, 그것을
  `accountFallback.ts`류의 기존 메커니즘으로 충분히 표현할 수
  있는지는 이 ADC가 판단하지 않는다(§Out of Scope) — 실제 요구사항이
  생기면 별도 Architecture Decision 대상이다.
- **`domain_fallback_chains` 자체**: 현재 OmniRoute 통합을 위해
  Jarvis OS가 별도로 구현하지 않는다. **Jarvis OS가 새로운 fallback
  engine을 구현하겠다고 선언하는 것이 아니다** — 이 Decision은
  "만들지 않는다"는 소극적 결정이지 "대신 무엇을 만든다"는 적극적
  결정이 아니다.

### Scope

이 ADC가 변경하는 판단은 오직 **`domain_fallback_chains` 선행조건의
재설계 경로 채택** 하나로 한정한다. 다음은 명시적으로 결정하지
않으며, `ADC-0027`이 규정한 상태 그대로 유지한다.

- `routing_decisions` durable audit 방식(대체 채널 활용 여부 포함)
- `domain_budgets` 검증 결과(UNVERIFIED 유지)
- `priority` 차등 selection 실증(UNVERIFIED 유지)
- `IMPLEMENTATION_RULES.md` Scoped 완화(미결 유지)
- Engine Adapter Contract(§14 Kernel Public Contract)의 실제 확정
- Architecture Freeze(`CONSTITUTION.md`) 문구의 실제 수정
- OmniRoute 통합 구현 착수

### Evidence

- 사용한 것: 두 차례 Observation(2026-09-06)이 확인한 §Q1의 네 가지
  사실 — `virtualFactory.ts` 전수 검색 0건, `accountFallback.ts`/
  `decisionTrace.ts` 대체 메커니즘 존재, `registerFallback`/
  `resolveFallbackChain` external caller 0건, `policyEngine.
  evaluateRequest` DI-등록-후-미resolve 확인. `EVIDENCE-0001` §3.3의
  기존 인용(OB-10~OB-16)과 일치하며 뒤집지 않는다.
- 사용하지 않은 것(과장 배제): "구현 불필요"는 **현재 OmniRoute
  execution scope에 대한 판단**일 뿐이다. 이것이 향후 Jarvis
  Governance 요구사항까지 영구적으로 금지한다는 뜻은 아니다 — 실제
  요구사항이 관찰되면 이 Decision과 무관하게 별도 Architecture
  Decision으로 재검토할 수 있다(§Decision Boundary).
- 새로 만든 Evidence 없음 — 기존 두 Observation 세션의 결과만
  재구조화했다.

### Gate Impact

`ADC-0027` Implementation Gate에서:

| 조건 | 변경 전(`ADC-0027`/`EVIDENCE-0001`) | 변경 후(이 ADC) |
|---|---|---|
| `domain_fallback_chains` | FAIL / BLOCKING | **Responsibility redesign accepted — 이 항목의 구현 착수 선행조건 해소** |
| `priority` | PASS(코드) / UNVERIFIED(차등 selection) | 무변경 |
| `routing_decisions` | FAIL / BLOCKING | 무변경 |
| `domain_budgets` | UNVERIFIED / BLOCKING | 무변경 |
| `IMPLEMENTATION_RULES.md` Scoped 완화 | UNVERIFIED/판단보류 | 무변경 |

**전체 Implementation Gate는 자동으로 PASS가 되지 않는다.**
`routing_decisions`·`domain_budgets`·`IMPLEMENTATION_RULES.md`
선행조건이 그대로 남아 있는 한, `ADC-0027`의 "Production 구현 착수는
선행조건이 모두 충족되기 전까지 차단된다"는 문언은 계속 유효하다.
이 ADC는 4개 선행조건 중 1개(그중에서도 3개 항목으로 묶인 선행조건
2의 1/3)만 해소한다.

### Decision Boundary

- 이 Decision은 **가역적**이다 — OmniRoute 업스트림이
  `domain_fallback_chains`/`fallbackPolicy.ts`를 실제 실행 경로에
  연결하는 변경을 하거나, Jarvis OS 쪽에 도메인별 커스텀 fallback
  체인이라는 실제 요구사항이 관찰되면, 이 Decision은 재검토 대상이다
  (`ADC-0027` §Risks의 "FAIL 항목이 구조적 결함일 가능성" 절과 동일한
  원칙).
- 이 Decision은 OmniRoute의 전체 Governance 책임을 면제하지 않는다
  — `accountFallback.ts`/`decisionTrace.ts`가 담당하는 실제 fallback
  execution은 여전히 `ADC-0027` §Q5 PDP/PEP 경계(Jarvis가 정책을
  결정하고 OmniRoute가 실행) 안에 있으며, 이 ADC는 그 경계를
  넓히거나 좁히지 않는다.

### Reason

- Q1 — 두 차례 Observation이 서로 다른 세 경로(라이브 실행 경로,
  호출자 검색, DI resolve 검색)에서 동일하게 미사용을 확인했으므로
  orphaned legacy 판단은 충분한 Evidence를 갖췄다.
- Q2 — `ADC-0027` 선행조건 2의 ①(재검증 PASS)이 구조적으로 닫혀
  있으므로, 남은 유일한 경로 ②(Responsibility 재설계)를 채택하는
  것이 Evidence와 정합적이다.

### Decision Rationale

이 Decision은 `ADC-0027`의 Decision(Accept, Conditional, Scoped —
OmniRoute를 목표 구현 후보로 지정)을 재론하지 않는다 — `ADC-0027`이
연 4개 선행조건 중 정확히 1개 항목(`domain_fallback_chains`)의
해소 경로만 확정할 뿐이다. `ADC-0027`의 Scope(Model Routing/Engine
Adapter 한정, Multi-Agent Runtime 등 나머지 7개 Freeze 항목 무변경),
Responsibility 표(PDP/PEP), Decision Boundary(Reversibility 원칙)는
모두 그대로 유지된다.

---

## Out of Scope

- `routing_decisions` durable audit 방식(대체 채널 활용 여부 포함).
- `domain_budgets` 검증 결과 확정.
- `priority` 차등 selection 실증.
- `IMPLEMENTATION_RULES.md` 실제 수정 또는 그 필요성의 최종 확정.
- Engine Adapter Contract(§14)의 실제 확정.
- `CONSTITUTION.md` Architecture Freeze 문구의 실제 수정(Engine
  Adapter·Model Routing 항목 포함) — `ADC-0027`과 마찬가지로 방향도
  이 ADC가 제시하지 않는다. 이 항목은 `domain_fallback_chains` 단독
  판단이 아니라 선행조건 1~4 전체가 충족된 뒤 `ADC-0027`이 이미
  예정한 후속 ADR의 몫이다.
- Multi-Agent Runtime 및 `CONSTITUTION.md` Freeze 목록의 나머지 7개
  항목.
- OmniRoute의 실제 설치·연결·설정·통합 구현.
- Jarvis OS 자체 fallback engine의 신규 구현 또는 그 구현 선언.

## Risks

- **과대 해석 위험**: "선행조건 하나 해소"가 "Gate 전체 통과"로
  오독될 위험 — §Gate Impact에서 나머지 3개 조건이 무변경임을
  명시했다.
- **OmniRoute 업스트림 변경에 따른 재검토 필요성**: 이 Decision의
  근거(orphaned legacy)는 검증 시점(2026-09-06, 소스 버전 3.8.50)의
  코드 상태에 기반한다 — OmniRoute가 향후 `domain_fallback_chains`를
  실제 실행 경로에 연결하는 업데이트를 배포하면, 이 ADC의 전제
  자체가 달라진다(§Decision Boundary에서 재검토 대상으로 이미 명시).
- **Jarvis 요구사항 발생 시 재검토 필요성**: Jarvis OS 쪽에서 도메인별
  커스텀 fallback 체인이 실제로 필요하다는 요구가 나중에 관찰되면,
  이 Decision과 무관하게 그 요구를 별도 Architecture Decision으로
  다뤄야 한다 — 이 ADC가 "영구 배제"를 의미하지 않는다는 것을
  재확인한다.

## Next Step

1. `routing_decisions`·`domain_budgets`·`IMPLEMENTATION_RULES.md`
   나머지 선행조건은 별도 Observation/Architecture Decision 대상으로
   그대로 남는다 — 이 ADC는 그 작업을 앞당기지 않는다.
2. 선행조건 1~4가 전부(각자의 방식으로) 해소되면, `ADC-0027` §Next
   Step이 예정한 후속 ADR이 `CONSTITUTION.md`·`BASELINE.md`·
   `IMPLEMENTATION_RULES.md`의 실제 Scoped 반영을 수행한다 — 그 ADR은
   이 ADC 하나만으로 착수되지 않는다.
3. OmniRoute가 `domain_fallback_chains`를 실제 실행 경로에 연결하는
   변경을 배포하거나, Jarvis 쪽에 도메인별 fallback 요구사항이
   관찰되면 이 ADC를 재검토 대상으로 등록한다(§Risks).

## Governance Chain 검증

`RFC-0023`(Proposed) → `ADC-0027`(Accept, Conditional·Scoped —
OmniRoute를 목표 후보로 지정, 선행조건 1~4 규정) → 이 ADC(Accept,
Scoped, Narrow — 선행조건 2 중 `domain_fallback_chains` 항목만
Responsibility 재설계 경로로 해소) → 후속 ADR(예정, 선행조건 1~4
전체 충족 후 Baseline·Rules 반영). 이 ADC는 `ADC-0027`이 열어 둔
선행조건 2의 두 경로(①/②) 중 하나를 택했을 뿐, `ADC-0027`의 Decision
자체를 재론하지 않았다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. 기존 `ADC-0027`
  Scope(§16.2 Execution Layer) 안에서 선행조건 하나의 해소 경로만
  확정했다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**. Jarvis
  OS가 새 fallback engine을 구현한다고 선언하지 않았다
  (§Responsibility Boundary).
- Contract Change — **없음**. §14 Kernel Public Contract를 확정하지
  않았다.
- `CONSTITUTION.md`·`BASELINE.md`·`IMPLEMENTATION_RULES.md`·Engine
  Adapter Contract 문서를 이 ADC가 수정했는가 — **아니오**.
- Architecture Freeze를 해제했는가 — **아니오**. Freeze 목록 9개
  항목 문구는 무변경이며, `ADC-0027`이 이미 규정한 Conditional 상태도
  바뀌지 않았다.
- OmniRoute 실제 구현·통합을 승인했는가 — **아니오**. `ADC-0027`의
  "Production 구현 착수 차단"은 그대로 유지된다(§Gate Impact).
- `routing_decisions`를 임의로 구현/확정했는가 — **아니오**(§Scope,
  §Out of Scope에서 명시적으로 배제).
- 다른 Blocking 조건(`routing_decisions`·`domain_budgets`·
  `IMPLEMENTATION_RULES.md`)을 임의로 해소했는가 — **아니오**
  (§Gate Impact 표에서 "무변경"으로 명시).
- Multi-Agent Runtime Freeze를 침범했는가 — **아니오**(§Out of
  Scope).
- ADR이 필요한가 — 이 ADC 자체는 아니오(문서 수정을 하지 않음).
  나머지 선행조건이 모두 충족된 뒤 `ADC-0027`이 이미 예정한 후속
  ADR이 별도로 필요하다.

## Self Review

- `ADC-0027`의 기존 Decision과 논리적으로 충돌하는가 — **아니오**.
  `ADC-0027`이 미리 열어 둔 선행조건 2의 두 경로 중 하나(②)를
  택했을 뿐이며, `ADC-0027`의 Accept(Conditional, Scoped) 자체나
  Scope·Responsibility·Decision Boundary를 변경하지 않았다.
- `EVIDENCE-0001`과 직전 Observation을 정확히 반영하는가 — **Pass**.
  §Q1의 네 가지 사실은 `EVIDENCE-0001` §3.3(OB-10~OB-16)과 직전 두
  Observation 세션이 확인한 내용을 그대로 인용했으며, 어떤 FAIL
  판정도 PASS로 뒤집지 않았다.
- `domain_fallback_chains` 하나의 범위를 넘어 Decision을 확대했는가 —
  **아니오**. §Scope·§Gate Impact 표에서 다른 3개 조건이 무변경임을
  명시했다.
- OmniRoute 구현 착수를 잘못 허용했는가 — **아니오**. §Gate Impact가
  "전체 Gate는 자동으로 PASS가 되지 않는다"를 명시했고, `ADC-0027`의
  Production 차단은 유지된다.
- 다른 Blocking 조건을 임의로 해소했는가 — **아니오**(§Scope,
  §Out of Scope).
- Jarvis OS가 새 fallback engine을 구현한다고 선언했는가 — **아니오**
  (§Responsibility Boundary에서 명시적으로 부정).
- "구현 불필요"를 영구적 배제로 과장했는가 — **아니오**(§Evidence,
  §Decision Boundary에서 재검토 가능성을 명시).
- 기존 Architecture/Contract/`CONSTITUTION.md`/`BASELINE.md`/
  `IMPLEMENTATION_RULES.md` 문서를 수정했는가 — **아니오**. 이 ADC
  파일 외 어떤 파일도 생성·수정하지 않았다.
- Freeze를 변경했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
