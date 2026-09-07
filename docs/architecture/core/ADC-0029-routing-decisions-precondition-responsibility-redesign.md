# ADC-0029: `routing_decisions` 구현 착수 선행조건 — Audit Policy Requirement 재설계 (ADC-0027 후속)

## 목적

`docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
§Decision "구현 착수 선행조건" 2번(FAIL 3건 재해소 중 `routing_decisions`
항목)과, 그 근거가 된 §Q4의 "Audit Policy"(Jarvis OS가 라우팅 결과를
감사) 요구를 재검토한다. `ADC-0028`이 같은 선행조건 2의
`domain_fallback_chains` 항목 하나만 좁게 처리했던 것과 동일한 방식으로,
이 ADC는 **`routing_decisions` 항목 하나에만** 답한다.

직전 Read-only Architecture/Governance Review(2026-09-06)가 다음을
확인했다 — `hqs/development/CONSTITUTION.md`, `docs/architecture/
baseline/BASELINE.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`docs/governance/adc/ADC-0003.md` 4개 문서를 `audit`·`routing_decisions`·
`call_logs`·`trace`·`observability`·`persistence` 키워드로 전수
검색한 결과 **0건**이었다. "Audit Policy"·`routing_decisions` 요구는
`RFC-0023`→`ADC-0027`이 스스로 도입한 개념이며, 그 상위에 이를
요구하는 Governance 문서가 없다. 이 ADC는 그 확인을 근거로,
`ADC-0027`이 자신이 만든 이 precondition을 계속 유지할 필요가
있는지를 공식적으로 결정한다.

근거는 `ADC-0027`, `ADC-0028`, `EVIDENCE-0001-omniroute-precondition-
verification.md`, `EVIDENCE-0002-omniroute-domain-budgets-execution-
verification.md`, `RFC-0023`, `CONSTITUTION.md`, `BASELINE.md`,
`ARCHITECTURE_GOVERNANCE.md`, `docs/governance/adc/ADC-0003.md`, 그리고
직전 Read-only Review가 확인한 OmniRoute 소스 경로(아래 §Q2·§Q3)로만
한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- **`domain_fallback_chains`** — `ADC-0028`이 이미 처리했다. 재론하지
  않는다.
- **`domain_budgets`** — `EVIDENCE-0002`가 PASS로 확인했다. 재론하지
  않는다.
- **`priority` 차등 selection 실증** — UNVERIFIED 그대로 유지, 이
  ADC는 다루지 않는다.
- **`IMPLEMENTATION_RULES.md` Scoped 완화** — 판단보류 그대로 유지,
  이 ADC는 다루지 않는다.
- **`routing_decisions` 구현, 새 audit system 구현** — 이 ADC는
  어떤 코드 구현도 승인하지 않는다.
- **`call_logs`/`ComboTrace`/`RoutingEvent` 코드 변경** — 이 ADC는
  이 세 메커니즘의 **역할을 정리**할 뿐, 그중 어느 것도 수정·확장하지
  않는다.
- **OmniRoute Integration 착수 승인** — `ADC-0027`의 Production 구현
  차단은 유지된다.
- **Jarvis OS가 새로운 routing audit engine을 구현하기로 선언하는 것** —
  아래 §Responsibility Boundary가 명시하듯, 이 ADC는 그런 선언을
  하지 않는다.
- **"Audit requirement가 영구적으로 불필요하다"는 확정** — 이 Decision은
  "현재 정의된 Governance 요구가 없다"는 사실 판단이지, 미래에도
  Audit 요구가 생길 수 없다는 뜻이 아니다(§Decision Boundary).
- **`ADC-0027`·`CONSTITUTION.md`·`BASELINE.md`·
  `ARCHITECTURE_GOVERNANCE.md`·Engine Adapter Contract 파일의 실제
  수정** — 방향만 제시하고 실행은 하지 않는다(`ADC-0027`·`ADC-0028`과
  동일한 원칙).
- **ADR 작성** — 하지 않는다.

---

## Q1. Jarvis Governance가 `routing_decisions`를 요구하는가

### 검토

직전 Read-only Review가 4개 상위 Governance 문서를 전수 검색한 결과를
그대로 재확인한다.

| 문서 | `audit`/`routing_decisions`/`call_logs`/`trace`/`observability`/`persistence` 매치 |
|---|---|
| `hqs/development/CONSTITUTION.md` | 0건("Model Routing"은 Architecture Freeze 목록의 항목명일 뿐, 감사 요구 서술 없음) |
| `docs/architecture/baseline/BASELINE.md` | 0건("Routing" 언급은 전부 HQ Routing/Registry·Dynamic Routing — Multi-HQ 작업 분해·Workflow 조건부 분기 개념이며 OmniRoute/라우팅 감사와 무관) |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` | 0건(Engine Gateway/Routing/Adapter 관련 유일한 언급은 "Frozen/Deferred Boundary 우회 금지" 조항이며 Audit schema와 무관) |
| `docs/governance/adc/ADC-0003.md` | 0건 |

반면 "Audit Policy"·`routing_decisions` 요구는 `RFC-0023`(§3.3, §6,
§7 "Audit 영속성")과 `ADC-0027`(§Q4, §Decision Responsibility 표,
선행조건 2)에서만 등장한다 — 두 문서 모두 이 Adoption 절차 자신이
작성한 것이다.

### Q1 결론

- **Explicit requirement**: 없음.
- **Specific schema requirement**: 없음.
- **Audit persistence requirement**: 없음.
- **상위 Governance requirement**와 **`ADC-0027` 자체 requirement**는
  서로 다른 층위다 — 전자는 **Not Defined**, 후자는 `ADC-0027`이
  스스로 만들어 여전히 유효한 상태로 존재한다. 이 ADC는 후자를
  재설계하는 것이지, 존재하지도 않는 전자를 "해제"하는 것이 아니다.

**판단 제한(§3 원칙 적용)**: "`routing_decisions`가 없다"(사실, A)와
"`routing_decisions`가 없기 때문에 Jarvis Governance를 위반한다"(주장,
B)는 다른 명제다 — A는 참이고, B는 현재 근거가 없다. 또한 "`call_logs`
+ `ComboTrace` + `RoutingEvent`가 Jarvis Audit requirement를 완전히
충족한다"는 명제도 자동으로 확정하지 않는다 — 상위 Governance에
Audit requirement 자체가 정의돼 있지 않으므로, "충족한다/못한다"를
판단할 기준 자체가 없기 때문이다. 이 ADC의 Decision은 **"기존
Evidence가 충분하다"가 아니라 "`routing_decisions`를 요구할 상위
Governance requirement가 정의돼 있지 않으며, `ADC-0027`이 추가한 해당
precondition을 계속 유지할 Architecture상의 필요성도 확인되지
않는다"**는 판단에 근거한다.

---

## Q2. OmniRoute의 `routing_decisions` 구현이 실제로 필요한가

### 검토

직전 두 차례 Observation(`EVIDENCE-0001` §3.4, 후속 Read-only Review)이
확인한 사실을 재확인한다.

- **Schema는 존재한다**: `routing_decisions(id, request_id, task_type,
  combo_id, provider_selected, model_selected, score, factors_json,
  fallbacks_triggered, success, latency_ms, cost, source, created_at)`
  — 4개 인덱스를 갖춘, 완성도 높은 설계다.
- **실제 INSERT path는 없다**: `src/lib/a2a/routingLogger.ts`의
  `logRoutingDecision()`(46행)은 `decisions.push(decision)`만 수행하며
  (55행), 파일 전체에 `db.prepare(...INSERT...)` 호출이 없다. 파일
  헤더 주석(1~7행, "Records every routing decision to the
  `routing_decisions` SQLite table")과 코드 내부 주석(38행, "In-memory
  log (production would use SQLite via routing_decisions table)")이
  서로 모순된다.
- **`logRoutingDecision()` external caller가 없다**: 저장소 전체
  전수 검색 결과 정의 파일 자기 자신 외에 호출하는 코드가 없다.
- **실제 Auto-Combo execution path와 연결되지 않는다**: 실제 라이브
  라우팅 실행부(`open-sse/services/autoCombo/virtualFactory.ts`)를
  `routing_decisions`/`logRoutingDecision` 패턴으로 전수 검색한 결과
  0건이다.

### Q2 결론

`routing_decisions`는 OmniRoute 자신의 **기존 구현 안에서도** 실질적인
routing execution evidence mechanism으로 사용되지 않는다 — 이것은
Jarvis 쪽의 요구 유무와 무관하게, OmniRoute 내부 기준으로도 이미
미사용 상태라는 사실이다. `ADC-0028`이 `domain_fallback_chains`에
대해 확인한 것과 같은 성격의 orphaned 상태이나, **`routing_decisions`는
`domain_fallback_chains`와 달리 "대체 가능한 다른 실행 메커니즘이
Jarvis Audit 요구 전체를 무리 없이 흡수하는가"가 아직 불확실하다**
(§Q3) — 그래서 이 ADC는 `ADC-0028`과 달리 "완전한 orphaned legacy"로
단정하지 않고, 책임 소재만 재설계한다.

---

## Q3. 기존 Evidence mechanism으로 어떤 정보를 얻을 수 있는가

직전 Read-only Review의 Evidence 수준 비교를 그대로 인용한다 — 네
메커니즘의 역할을 섞지 않는다.

- **`call_logs`**: durable SQLite, 실제 request execution path
  (`chat.ts`/`chatCore.ts`, 실제 78+ rows), `provider`/`model`/
  `requested_model`/`status`/`duration`/`tokens_in`/`tokens_out`/
  `combo_name`/`combo_step_id`/`combo_execution_key` 등 보유. **제공하지
  않는 것**: 후보 배제 사유, score/factors.
- **ComboTrace**(`open-sse/services/combo/decisionTrace.ts`): 실제
  Combo dispatch path(`combo.ts`)에서 `dispatched`/
  `skipped_before_dispatch`/`not_reached` 3종 decision과 provider/model,
  `COMBO_SKIP_REASONS`(`circuit_open`/`provider_cooldown`/
  `model_lockout`/`quota_cutoff`/`availability`/`credential_gate`/
  `concurrency_cap`/`admission_lane`/`predictive_ttft`/
  `request_exhaustion`) 10종을 기록. **bounded in-memory**(TTL 30분+
  LRU 2000cap) — durable하지 않다.
- **RoutingEvent**(`open-sse/services/routing/events.ts`/`index.ts`):
  실제 routing execution path(`chatCore.ts`)에서 provider/model,
  outcome(success/error/malformed/timeout/rate_limited/
  stream_interrupted/guardrail_blocked/cancelled), latency/tokens/cost를
  기록. 기본 sink는 in-memory ring buffer(500)+quality tracker, 선택적
  외부 OTel export(로컬 SQLite 아님, env var 필요).
- **`accountFallback.ts`**: 실제 fallback/candidate filtering
  execution(`resilienceCandidateFilter.ts` 경유), rate-limit/model-lock
  등 상태 기반 필터링을 수행하지만 **그 자체가 audit record는 아니다**
  — boolean 필터 결과만 남긴다.

### Q3 결론

이 네 메커니즘을 합쳐도 `routing_decisions` schema가 원래 설계한
`score`/`factors_json`이 **durable하게** 남는 경로는 없다. 이 gap이
"문제"인지 아닌지는 §Q1이 확인한 대로 그 판단 기준(Jarvis Audit
requirement)이 아직 정의돼 있지 않아 **이 ADC가 확정할 수 없다** —
Decision은 이 불확실성을 인정한 채로 내려진다(§Decision, §Decision
Boundary).

---

## Decision

**Accept (Scoped, Narrow) — `routing_decisions`를 OmniRoute Model
Routing / Execution Layer(`ADC-0027` Scope) 구현 착수의 필수
선행조건에서 제외한다.**

- `routing_decisions` 구현을 요구하지 않는다.
- Jarvis OS가 별도 routing audit engine을 구현한다고 선언하지 않는다.
- 기존 `call_logs`·ComboTrace·RoutingEvent의 존재를 "완전한 Audit
  System"이라고 재정의하지 않는다 — §Q3이 확인한 gap(특히 score/
  factors의 비영속성)은 그대로 gap으로 남긴다.
- 현재 execution scope에서는 특정 `routing_decisions` schema를
  강제하지 않는다.
- 향후 Jarvis OS가 명시적인 Audit requirement를 정의하면, 이 Decision과
  무관하게 별도 Architecture Decision으로 재검토한다(§Decision
  Boundary).

### Responsibility Boundary

- **OmniRoute의 실제 routing execution evidence**: `call_logs`(요청
  단위 durable 결과), `ComboTrace`(dispatch 단계별 skip/decision,
  비영속), `RoutingEvent`(outcome 분류, 비영속)가 각자의 역할대로
  이미 실제 실행 경로에서 동작한다 — 이 ADC가 새로 만들거나 승인하는
  것이 아니다.
- **Jarvis OS의 Governance**: 어떤 Audit 정보를 요구할지 결정하는
  상위 정책 책임(`ADC-0027` §Q5 "Audit Policy" 축)은 유지된다 — 다만
  그 정책이 `routing_decisions`라는 특정 OmniRoute 내부 SQLite
  테이블을 통해 실행돼야 한다는 전제만 제거한다. Jarvis OS가 실제로
  무엇을 감사 대상으로 요구하는지, 그것을 `call_logs` 등 기존
  메커니즘으로 충분히 표현할 수 있는지는 이 ADC가 판단하지 않는다
  (§Out of Scope) — 실제 요구사항이 생기면 별도 Architecture Decision
  대상이다.
- **`routing_decisions` 자체**: 현재 OmniRoute 통합을 위해 Jarvis OS가
  별도로 구현하지 않는다. **Jarvis OS가 새로운 routing audit engine을
  구현하겠다고 선언하는 것이 아니다** — "만들지 않는다"는 소극적
  결정이지 "대신 무엇을 만든다"는 적극적 결정이 아니다.

### Scope

이 ADC가 변경하는 판단은 오직 다음으로 한정한다.

- `routing_decisions` requirement의 재검토
- "Audit Policy" requirement의 책임/정의 여부 정리
- `ADC-0027` 선행조건 2 중 `routing_decisions` 항목의 재설계
- 현재 Evidence mechanism(`call_logs`/ComboTrace/RoutingEvent/
  `accountFallback.ts`)의 역할 정리(§Q3)

다음은 명시적으로 제외한다.

- `routing_decisions` 구현, 새 audit system 구현
- `call_logs`/`ComboTrace`/`RoutingEvent` 코드 변경
- OmniRoute 소스 변경
- `priority` 검증, `domain_budgets` 변경, `domain_fallback_chains`
  변경(각각 무변경 유지 — 아래 §Gate Impact)
- `IMPLEMENTATION_RULES.md` 변경
- Architecture Contract 변경, Architecture Freeze 변경
- OmniRoute Integration 착수
- ADR 작성

### Evidence

- 사용한 것: §Q1의 4개 Governance 문서 전수 검색 결과(0건), §Q2의
  `routing_decisions` 미사용 확인(schema 존재·INSERT 부재·caller
  0건·라이브 경로 미참조), §Q3의 4개 대체 메커니즘 역할 비교.
  `EVIDENCE-0001` §3.4, `EVIDENCE-0002`, `ADC-0027` §Q4의 기존 인용과
  일치하며 뒤집지 않는다.
- 사용하지 않은 것(과장 배제): "Audit requirement 없음"을 "모든
  Audit이 불필요함"으로 확대하지 않는다 — 이는 **현재 정의된 상위
  Governance 문서 기준**의 판단일 뿐이다. `call_logs`/ComboTrace/
  RoutingEvent가 "Jarvis Audit requirement를 완전히 충족한다"고도
  확정하지 않는다 — 그 requirement 자체가 아직 없기 때문에 "충족
  여부"를 판단할 근거가 없다(§Q1 판단 제한).
- 새로 만든 Evidence 없음 — 기존 Observation·Review 결과만
  재구조화했다.

### Gate Impact

`ADC-0027` Implementation Gate 전체 현황:

| 조건 | 현재 상태 |
|---|---|
| `domain_fallback_chains` | `ADC-0028`로 해소(Responsibility redesign accepted) |
| `domain_budgets` | `EVIDENCE-0002`로 PASS(실제 blocking 확인) |
| `routing_decisions` | **이 ADC로 선행조건에서 제외**(Responsibility redesign accepted) |
| `priority` differential selection | UNVERIFIED(무변경) |
| `IMPLEMENTATION_RULES.md` | 판단보류(무변경) |

**`routing_decisions`가 선행조건에서 제외된다고 해서 전체 OmniRoute
Integration Gate가 자동으로 PASS 되는 것은 아니다.** `priority` 실제
차등 selection이 UNVERIFIED로 남아 있고, `IMPLEMENTATION_RULES.md`
Scoped 완화도 판단보류 상태다 — `ADC-0027`의 "Production 구현 착수는
선행조건이 모두 충족되기 전까지 차단된다"는 문언은 이 두 조건이
남아 있는 한 계속 유효하다.

### Decision Boundary(Reversibility)

- 이 Decision은 **가역적**이다. 다음 중 하나라도 실제로 관찰되면
  재검토 대상이다.
  - Jarvis가 명시적인 routing audit requirement를 정의하는 경우.
  - 규제/감사 목적의 durable routing decision evidence가 실제
    요구사항이 되는 경우.
  - score/factors/fallback history의 영구 보존이 실제 제품
    요구사항이 되는 경우.
  - OmniRoute 업스트림이 `routing_decisions`를 실제 실행 경로에
    연결하는 변경을 배포하는 경우.
- 이 ADC는 향후 audit architecture 자체를 영구적으로 금지하는 것으로
  해석되지 않는다 — "현재 정의된 요구가 없다"는 사실 판단일 뿐,
  미래의 Architecture Decision을 막지 않는다.

### Reason

- Q1 — 4개 상위 Governance 문서 전수 검색 결과 `routing_decisions`/
  Audit persistence를 요구하는 문장이 없음을 확인했고, 그 요구가
  `ADC-0027` 자신이 도입한 것임을 재확인했다.
- Q2 — `routing_decisions`가 OmniRoute 자신의 기존 구현 안에서도
  실질적으로 사용되지 않는다는 것을 소스 수준에서 재확인했다.
- Q3 — 기존 4개 메커니즘이 부분적으로만 정보를 제공하며, 그 부분성
  자체는 "문제"로 확정하지 않았다 — 판단 기준이 아직 없기 때문이다.

### Decision Rationale

이 Decision은 `ADC-0027`의 Decision(Accept, Conditional, Scoped —
OmniRoute를 목표 구현 후보로 지정)을 재론하지 않는다 — `ADC-0027`이
연 선행조건 2의 3개 항목 중 `domain_fallback_chains`(`ADC-0028`에
이어) `routing_decisions` 하나를 추가로 재설계할 뿐이다. `ADC-0027`의
Scope·Responsibility 표·Decision Boundary(Reversibility)는 모두
그대로 유지된다. **이 ADC는 `ADC-0027` 파일 자체를 수정하지 않는다** —
`ADC-0028`이 확립한 것과 동일한 구조(후속 Governance Decision으로
개별 precondition의 책임/필요성만 재설계)를 유지한다.

---

## Out of Scope

- `routing_decisions` 구현, 새 audit system 구현.
- `call_logs`/`ComboTrace`/`RoutingEvent` 코드 변경.
- OmniRoute 소스 변경, OmniRoute Integration 착수.
- `priority` 검증(UNVERIFIED 무변경), `domain_budgets` 변경(PASS
  무변경), `domain_fallback_chains` 변경(`ADC-0028` 상태 무변경).
- `IMPLEMENTATION_RULES.md` 실제 수정 또는 그 필요성의 최종 확정.
- Engine Adapter Contract(§14)의 실제 확정.
- `CONSTITUTION.md`·`BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md` 문구의
  실제 수정 — 방향도 이 ADC가 제시하지 않는다.
- ADR 작성.
- `ADC-0027`·`ADC-0028` 파일의 직접 수정.

## Risks

- **"Audit 전면 불필요"로 오독될 위험**: 이 Decision이 "OmniRoute
  통합에는 어떤 Audit도 필요 없다"로 확대 해석될 위험 — §Decision
  Boundary·§Decision Rationale에서 "현재 정의된 상위 Governance
  requirement가 없다"는 좁은 사실 판단임을 명시했다.
- **`call_logs`/ComboTrace/RoutingEvent 과대평가 위험**: 이 세 메커니즘의
  존재가 "완전한 Audit System이 이미 있다"로 읽힐 위험 — §Q3·
  §Decision에서 score/factors의 durable 부재를 gap으로 명시적으로
  남겼다.
- **`ADC-0027` 선행조건 2 잔여 항목과의 혼동 위험**: 선행조건 2는
  원래 `priority`·`domain_fallback_chains`·`routing_decisions` 3건
  묶음이었다 — `priority`는 §Q4에서 이미 PASS(코드 수준)였고,
  `domain_fallback_chains`는 `ADC-0028`, `routing_decisions`는 이
  ADC로 각각 처리됐다. 이 세 항목이 "선행조건 2 전체 해소"로
  뭉뚱그려 읽히지 않도록 §Gate Impact 표에서 개별로 나열했다.

**재검토 조건**: `ADC-0027` §Risks의 "FAIL 항목이 구조적 결함일
가능성" 절과 동일한 원칙을 적용한다 — Jarvis 쪽에 실제 Audit
requirement가 관찰되거나 OmniRoute 업스트림이 `routing_decisions`를
실제 실행 경로에 연결하면, 이 Decision을 재검토 대상으로 등록한다.

## Next Step

1. `priority` 실제 차등 selection, `IMPLEMENTATION_RULES.md` Scoped
   완화는 별도 Observation/Architecture Decision 대상으로 그대로
   남는다 — 이 ADC는 그 작업을 앞당기지 않는다.
2. `ADC-0027` 선행조건 1~4가 전부(각자의 방식으로) 해소되면, `ADC-0027`
   §Next Step이 예정한 후속 ADR이 `CONSTITUTION.md`·`BASELINE.md`·
   `IMPLEMENTATION_RULES.md`의 실제 Scoped 반영을 수행한다.
3. Jarvis 쪽에 명시적 routing audit requirement가 관찰되거나 OmniRoute
   업스트림 변경이 있으면 이 ADC를 재검토 대상으로 등록한다(§Risks).

## Governance Chain 검증

`RFC-0023`(Proposed) → `ADC-0027`(Accept, Conditional·Scoped) →
`ADC-0028`(Accept, Scoped, Narrow — `domain_fallback_chains` 선행조건
제외) → `EVIDENCE-0002`(Evidence — `domain_budgets` PASS) → 이
ADC(Accept, Scoped, Narrow — `routing_decisions` 선행조건 제외) →
후속 ADR(예정, 선행조건 1~4 전체 충족 후 Baseline·Rules 반영). 이 ADC는
`ADC-0027`이 열어 둔 선행조건 2의 잔여 항목 하나를 재설계했을 뿐,
`ADC-0027`의 Decision 자체나 `ADC-0028`의 Decision을 재론하지 않았다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. 기존 `ADC-0027`
  Scope 안에서 선행조건 하나의 해소 경로만 확정했다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**. Jarvis
  OS가 새 routing audit engine을 구현한다고 선언하지 않았다
  (§Responsibility Boundary).
- Contract Change — **없음**.
- `CONSTITUTION.md`·`BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·Engine
  Adapter Contract 문서를 이 ADC가 수정했는가 — **아니오**.
- Architecture Freeze를 해제했는가 — **아니오**.
- OmniRoute Integration을 허용하는 문구가 들어갔는가 — **아니오**
  (§Gate Impact에서 "전체 Gate 자동 PASS 아님"을 명시).
- `call_logs`/`ComboTrace`/`RoutingEvent`를 임의로 변경/과장했는가 —
  **아니오**(§Q3·§Decision에서 각자의 역할과 한계를 그대로 유지).
- 다른 precondition(`priority`/`domain_budgets`/`domain_fallback_chains`/
  `IMPLEMENTATION_RULES.md`)을 임의로 변경했는가 — **아니오**
  (§Gate Impact 표에서 "무변경"으로 명시).
- ADR이 필요한가 — 이 ADC 자체는 아니오. 선행조건 1~4가 모두
  충족된 뒤 `ADC-0027`이 이미 예정한 후속 ADR이 별도로 필요하다.

## Self Review

- 상위 Governance requirement와 `ADC-0027` requirement를 구분했는가 —
  **Pass**(§Q1에서 Explicit/Specific schema/Audit persistence
  requirement 각각 "없음"으로 명시하되, `ADC-0027` 자체 precondition은
  별개로 유효함을 명시).
- `routing_decisions` schema 존재를 requirement로 오해했는가 —
  **아니오**(§Q2에서 schema 존재는 "설계"로만 기록, 실행 부재를
  근거로 사용).
- dead code와 실제 execution path를 구분했는가 — **Pass**(§Q2
  `routing_decisions`=dead code vs §Q3 `call_logs`/ComboTrace/
  RoutingEvent=실제 execution path로 명확히 분리).
- `call_logs`/ComboTrace/RoutingEvent의 역할을 과장했는가 — **아니오**
  (§Q3·§Decision에서 각자의 persistence 특성과 한계를 그대로 기록,
  "완전한 Audit System"이라 부르지 않음을 명시).
- "Audit requirement 없음"을 "모든 Audit이 불필요함"으로 확대했는가 —
  **아니오**(§Decision·§Decision Boundary·§Risks에서 반복적으로
  경계를 명시).
- `ADC-0027`의 다른 precondition을 임의로 변경했는가 — **아니오**
  (§Gate Impact, §Out of Scope).
- OmniRoute Integration을 허용하는 문구가 들어갔는가 — **아니오**.
- Architecture/Contract/Freeze를 변경했는가 — **아니오**(이 ADC 파일
  외 어떤 파일도 생성·수정하지 않았다).
- 별도 ADR을 작성했는가 — **아니오**.
- `ADC-0027`/`ADC-0028` 파일을 직접 수정했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
