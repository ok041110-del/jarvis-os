# ADR-0015: OmniRoute Model Routing / Engine Adapter Adoption — Thin Engine Caller 통합 Architecture 정책 (ADC-0027~0031 정리)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0015` |
| 제목 | `ADC-0027`~`ADC-0031`이 각각 내린 Decision을 하나의 최종 Architecture 정책으로 통합 정리 |
| 상태 | **Accepted (Consolidation Only — Baseline/Rules 문구 미반영)** — 이 ADR은 기존 5개 ADC의 Decision을 재론·확장하지 않고 그대로 정리한다. 이 저장소의 기존 ADR 관례(`ADR-0001`~`ADR-0014`)는 ADR 자신이 `BASELINE.md`/`IMPLEMENTATION_RULES.md` 문구를 실제로 갱신했으나, **이 ADR은 그 관례를 따르지 않는다** — 사용자 지시에 따라 문서 정리만 수행하고 실제 문구 반영은 별도 후속 ADR 대상으로 명시적으로 남긴다(§13 Open Conditions). |
| Context | `RFC-0023` → `ADC-0027`(Accept, Conditional·Scoped) → `ADC-0028`/`ADC-0029`/`ADC-0030`(선행조건 2의 세 항목 개별 재설계) → `EVIDENCE-0002`(선행조건 3 PASS) → `ADC-0031`(선행조건 4 Architecture 판단) |
| 관련 RFC | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` |
| 관련 ADC | `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031` |
| 관련 Evidence | `EVIDENCE-0001-omniroute-precondition-verification.md`, `EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md` |
| 선행 Decision(참고, 뒤집지 않음) | `docs/governance/adc/ADC-0003.md` 판단4(Multi-Model, Out of Authority — 여전히 Open), `docs/decisions/adc/ADC.md` ADC-01·ADC-02·ADC-07(여전히 Open) |

이 ADR은 `ADC-0027`~`ADC-0031`이 이미 내린 Decision을 **다시 논의하지
않는다.** 새로운 Architecture Decision을 추가하지 않는다. 다섯 개
ADC에 흩어진 Decision을 하나의 정합적인 정책 서술로 정리하는 것만
수행한다.

---

## 1. Context

사전 검토를 위해 `hqs/development/CONSTITUTION.md`, `docs/architecture/
baseline/BASELINE.md`(§16.2), `docs/00_governance/
ARCHITECTURE_GOVERNANCE.md`, `hqs/development/IMPLEMENTATION_RULES.md`,
`docs/governance/adc/ADC-0003.md`, `RFC-0023`, `ADC-0027`~`ADC-0031`,
`EVIDENCE-0001`/`EVIDENCE-0002`를 재확인했다. 상호 정합성 확인 결과,
다섯 ADC의 Decision은 서로 충돌하지 않으며 각자 독립된 선행조건
하나씩을 다뤘다(아래 §6).

| 문서 | 내린 Decision |
|---|---|
| `ADC-0027` | Accept(Conditional, Scoped) — OmniRoute를 Model Routing/Engine Adapter의 목표 구현 후보로 지정, 구현 착수 선행조건 4개(Evidence 영속화·FAIL 3건 재해소·`domain_budgets` 확정·`IMPLEMENTATION_RULES.md` Scoped 완화) 규정 |
| `ADC-0028` | Accept(Scoped, Narrow) — `domain_fallback_chains`를 선행조건에서 제외(Responsibility redesign) |
| `ADC-0029` | Accept(Scoped, Narrow) — `routing_decisions`를 선행조건에서 제외(Responsibility redesign) |
| `ADC-0030` | Accept(Scoped, Narrow) — `priority`를 선행조건에서 제외(Responsibility redesign) |
| `ADC-0031` | Accept(Scoped, Narrow) — OmniRoute Thin Engine Caller Boundary를 현재 `IMPLEMENTATION_RULES.md` 범위 내 허용 형태로 확정(Architecture 판단, ADR 미착수) |

---

## 2. Decision

**OmniRoute의 위치**: OmniRoute는 Jarvis OS의 **Model Routing /
Engine Adapter / Execution Layer(`BASELINE.md` §16.2) 내부
Implementation Engine 후보**로 취급한다.

다음 영역에는 포함하지 않는다.

- **Governance Layer**(§16.1) — `ADC-0027` §목적이 명시한 대로,
  "Provider Governance"라는 책임 명칭은 §16.1과 무관한 정책 결정
  책임의 서술적 이름일 뿐 새 Kernel Module이 아니다.
- **Kernel Public Contract**(§14) — `ADC-0027`·`ADC-0031` 모두 §14를
  확정하지 않았다.
- **Jarvis 자체 Routing Policy(코드로 구현된 것)** — `ADC-0031`이
  확정한 Thin Caller Boundary는 Jarvis 코드가 아닌 OmniRoute가
  Routing을 수행하는 구조를 전제한다.
- **Multi-Engine Gateway** — `ADC-0031` Case C(Multi-Engine Gateway)는
  `IMPLEMENTATION_RULES.md` 15·16·21행과 명확히 충돌하는 것으로
  판정됐다.

---

## 3. Responsibility Boundary

`ADC-0027` §Q5 PDP/PEP 구조와 `ADC-0031`의 Thin Caller Boundary를
그대로 통합한다.

### Jarvis가 담당(Thin Engine Caller, `ADC-0031` 확정)

- OmniRoute를 호출하는 단일 endpoint/function invocation.
- request/response transformation(Jarvis 포맷 ↔ OmniRoute OpenAI-
  compatible 포맷).
- 필요한 경우 adapter-level lifecycle/error mapping(취소, 상태
  조회 등).

### OmniRoute가 담당(PEP, `ADC-0027` §Decision)

- Model Routing Execution.
- Provider selection.
- Provider Call.
- Runtime Fallback.
- Egress Execution.

### Jarvis에서 금지(`ADC-0031` §Decision "금지" 목록)

- Provider selection.
- Model selection/scoring.
- 자체 Routing 로직.
- 자체 Runtime fallback engine.
- Multi-provider orchestration.
- Multi-engine selection.
- Engine Gateway(일반화된 Port/Adapter 추상화).
- `provider_connections.priority`를 이용한 Jarvis 자체 선택 정책.
- OmniRoute가 반환한 후보를 Jarvis가 직접 재평가하는 로직.
- Policy 판정 로직 그 자체(Jarvis 코드 내부에 두는 것).

**Thin Caller의 정확한 범위는 `ADC-0031`의 결정을 그대로 따르며,
이 ADR은 그 범위를 확장하지 않는다.**

---

## 4. Precondition / Gate Resolution

| 항목 | 최종 처리 | 과장 방지 명시 |
|---|---|---|
| `domain_fallback_chains` | `ADC-0028`에 따라 OmniRoute Adoption precondition에서 제외 | **이 제외는 새로운 fallback engine을 Jarvis가 구현했다는 뜻이 아니다.** 실제 fallback execution은 `accountFallback.ts`/`decisionTrace.ts` 계열이 이미 담당하며, `domain_fallback_chains` 자체는 orphaned legacy로 분류됐을 뿐이다. |
| `domain_budgets` | `EVIDENCE-0002`를 통해 execution enforcement PASS | **이 PASS는 "누적 spend가 한도를 초과했을 때 provider 호출 이전 차단"이라는 좁은 범위만 실제 실행으로 확인된 것이다.** `additionalCost`를 반영한 사전 계산형 차단, warning threshold 로직, 복수 API key 동시 시나리오 등 budget semantics 전체가 검증된 것이 아니다(`EVIDENCE-0002` §5·§9). |
| `routing_decisions` | `ADC-0029`에 따라 Adoption precondition에서 제외 | **이 제외는 Audit 기능이 완전히 해결됐다는 뜻이 아니다.** `routing_decisions` 테이블 자체는 여전히 미구현(dead code)이며, `call_logs`/ComboTrace/RoutingEvent가 부분적으로만 정보를 제공한다는 gap(특히 score/factors의 durable 부재)은 그대로 남아 있다 — Jarvis Audit requirement 자체가 상위 Governance에 정의돼 있지 않다는 사실에 근거한 제외일 뿐이다. |
| `priority` | `ADC-0030`에 따라 Adoption precondition에서 제외 | **이 제외는 priority 기반 routing selection이 검증됐다는 뜻이 아니다.** `priority`는 DB 조회 정렬·candidate listing 순서에는 실행으로 확인된 영향을 주지만, 실제 Auto-Combo scoring factor로는 사용되지 않으며 최종 dispatch selection·tie-break에 대한 영향은 UNVERIFIED로 남아 있다(`ADC-0030` §4 표). |
| `IMPLEMENTATION_RULES.md` | `ADC-0031`에 따라 Thin Caller 범위에서는 별도 완화 불필요 | **이것은 실제 caller 구현이 검증됐다는 뜻이 아니다.** 실제 Jarvis repository에 OmniRoute integration caller는 존재하지 않으며(`ADC-0031` §목적, 전수 검색 재확인), 이 판단은 향후 caller 설계에 대한 사전 Architecture 판단이다. |

---

## 5. Production Adoption Gate

**현재 확정 가능한 것**: OmniRoute를 특정 책임 경계(§3) 안에서
구현 후보로 채택할 Architecture 방향이 확정되었다.

**현재 확정할 수 없는 것(근거 없이 선언하지 않는다)**:

> ~~"OmniRoute Production Adoption 완료"~~

이런 선언은 하지 않는다. `ADC-0027` §Decision 선행조건 1~4가 아래
표와 같이 처리됐더라도, 이는 **Architecture Decision 수준의 해소**
이지 **Production 구현 착수 승인**이 아니다.

| 선행조건 | 상태 |
|---|---|
| 1. Evidence 영속화 | `EVIDENCE-0001`/`EVIDENCE-0002`로 충족 |
| 2. FAIL 3건 재해소(`priority`/`domain_fallback_chains`/`routing_decisions`) | `ADC-0030`/`ADC-0028`/`ADC-0029`로 각각 Responsibility redesign 경로 처리 |
| 3. `domain_budgets` 확정 | `EVIDENCE-0002` PASS |
| 4. `IMPLEMENTATION_RULES.md` Scoped 완화 | `ADC-0031`이 "Thin Caller라면 완화 불필요"라는 조건부 Architecture 판단 확정 — **`ADC-0027`이 명시적으로 요구한 후속 ADR(규칙 문구 자체 반영)은 여전히 미착수** |

실제 구현을 향해 남은 절차는 다음 세 단계다.

1. **Thin Engine Caller 구현** — 아직 코드 한 줄도 작성되지 않았다.
2. **실제 integration validation** — 구현된 caller가 실제로
   `ADC-0031`의 Thin Caller 조건(단일 함수 유지, Policy 판정 로직
   미포함)을 지키는지 확인.
3. **Final Adoption Review** — 위 1·2가 완료된 뒤, `ADC-0027`이
   요구한 후속 ADR(`CONSTITUTION.md`·`BASELINE.md` §14.1·§16.2·
   `IMPLEMENTATION_RULES.md`의 실제 Scoped 갱신)과 함께 수행되는
   최종 검토.

**이 ADR은 위 세 단계 중 어느 것도 수행하지 않는다.** 이 ADR이
확정하는 것은 §2~§3의 Architecture 방향 하나뿐이다.

---

## 6. Reversibility

`ADC-0027` §Decision Boundary·`ADC-0031` §Decision Boundary의
Reversibility 원칙을 그대로 유지한다.

- OmniRoute-specific routing logic을 Jarvis에 복제하지 않는다.
- OmniRoute 내부 API/configuration을 Kernel/HQ 전체에 노출하지
  않는다.
- Jarvis Kernel/HQ가 OmniRoute의 Provider 구조를 직접 인식하지
  않도록 한다.

**이를 새로운 Port/Adapter abstraction이나 Multi-Engine Gateway로
확대하지 않는다** — Reversibility를 지키기 위한 수단이 그 자체로
`IMPLEMENTATION_RULES.md` 15행(Engine Gateway 금지)이 금지하는
추상화가 되어서는 안 된다. 이 경계는 `ADC-0031` §Q1이 이미 확인한
Case A(허용)와 Case C(금지)의 구분과 동일하다.

---

## 7. Governance Constraints

이 ADR 작성 자체로 다음을 변경하지 않는다.

- `hqs/development/CONSTITUTION.md`
- `docs/architecture/baseline/BASELINE.md`
- `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`
- `hqs/development/IMPLEMENTATION_RULES.md`
- Engine Adapter Contract(§14)
- Architecture Freeze(`CONSTITUTION.md` 9개 항목 목록)
- `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031`
- `EVIDENCE-0001`, `EVIDENCE-0002`

문구 변경이 필요하다고 판단되는 지점(`ADC-0027` §Baseline/Rules
반영 범위가 이미 제안한 `CONSTITUTION.md` Architecture Freeze
문구·`BASELINE.md` §14.1·§16.2·`IMPLEMENTATION_RULES.md` 조항)이
있더라도, 이번 작업에서 임의로 수정하지 않는다 — 별도 Architecture
Decision(후속 ADR) 대상으로 남긴다(§13).

---

## 8. Consequences

- **긍정적 결과**: 다섯 개 ADC에 흩어져 있던 Decision이 하나의
  일관된 정책 서술로 정리되어, 향후 실제 caller를 설계할 때 참조할
  단일 기준점이 생겼다.
- **위험**: 이 통합 정리가 "OmniRoute Adoption이 실질적으로
  끝났다"로 오독될 위험이 있다 — §5에서 Production Adoption Gate가
  여전히 열리지 않았음을 반복 명시해 이 위험을 낮췄다.
- **후속 의무**: `ADC-0027`이 요구한 후속 ADR(실제 Baseline/Rules
  텍스트 반영)과 실제 caller 구현·검증이 이 ADR 이후에도 별도로
  필요하다(§13).

---

## 9. Implementation Boundary

이 ADR은 실제 구현을 승인하지 않는다. 다음은 이 ADR 작성 과정에서
수행하지 않았고, 이 ADR도 승인하지 않는다.

- OmniRoute caller 구현
- Engine Adapter 구현
- API 연결
- Provider configuration 변경
- Dashboard 변경
- OmniRoute source 변경
- 테스트 코드 추가

**문서 작성 및 검증만 수행했다.**

---

## 10. Validation Boundary

실제 caller가 §3의 Responsibility Boundary와 `ADC-0031`의 Thin
Caller 조건을 지키는지 검증하는 것은 이 ADR의 범위가 아니다 — 그
검증은 §5가 명시한 "실제 integration validation" 및 "Final Adoption
Review" 단계에서, 실제 caller 코드가 존재하게 된 시점에 별도로
수행돼야 한다. 이 ADR은 검증 기준(§3·§4·`ADC-0031` §Q1의 두 조건)만
정리했을 뿐, 어떤 검증도 수행하지 않았다.

---

## 11. Related RFC / ADC / Evidence

- `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`
- `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
- `docs/architecture/core/ADC-0028-domain-fallback-chains-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0029-routing-decisions-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0030-priority-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md`
- `docs/architecture/core/EVIDENCE-0001-omniroute-precondition-verification.md`
- `docs/architecture/core/EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md`
- `docs/governance/adc/ADC-0003.md` 판단4(Multi-Model, Out of Authority — 여전히 Open, 이 ADR이 재판단하지 않음)

---

## 12. Open Conditions

이 ADR 이후에도 남아 있는, 별도 절차가 필요한 사항.

1. **후속 ADR(실제 Baseline/Rules 텍스트 반영)** — `ADC-0027` §Next
   Step·§Baseline/Rules 반영 범위가 이미 제안한 `CONSTITUTION.md`
   Architecture Freeze 문구·`BASELINE.md` §14.1·§16.2·
   `IMPLEMENTATION_RULES.md` "Engine Gateway/Engine Routing/Multi
   Engine 지원 코드 작성 금지" 조항의 Scoped 완화는 여전히 미착수다.
2. **실제 Thin Engine Caller 구현** — 코드 한 줄도 작성되지 않았다.
3. **Final Adoption Review** — 실제 구현된 caller가 `ADC-0031` §Q1의
   두 조건(단일 함수 유지, Policy 판정 로직 미포함)을 지키는지
   확인하는 절차가 구현 시점에 별도로 필요하다.
4. **Jarvis의 "Routing Policy"·"Cost/Budget Policy"·"Audit Policy"가
   Jarvis 코드로 구현돼야 하는지, OmniRoute 설정(대시보드 등)으로
   존재해도 되는지** — `ADC-0031` §Out of Scope가 이미 명시한 대로
   미결이며, 이 선택에 따라 실제 caller가 Case A로 남을지 Case B로
   전이될지가 갈린다.
5. **`routing_decisions` Audit gap** — score/factors의 durable 부재는
   해소되지 않았다(`ADC-0029` §Q3). Jarvis 쪽에 명시적 Audit
   requirement가 생기면 별도 Architecture Decision 대상이다.
6. **`priority` tie-break 영향** — 실제 dispatch-time 최종 selection에
   대한 영향은 UNVERIFIED로 남아 있다(`ADC-0030` §4 표).
7. **`domain_budgets` semantics 전체 검증** — warning threshold, 기간
   리셋(`resetInterval`/`resetTime`), 복수 API key 동시 사용 시나리오,
   실제 사용자 생성(DB-backed) API key 경로는 검증되지 않았다
   (`EVIDENCE-0002` §9).
8. **`docs/governance/adc/ADC-0003.md` 판단4, `docs/decisions/adc/ADC.md` ADC-01·ADC-02·ADC-07** — 전부 Open 상태 그대로이며 이 ADR이 재판단하지 않는다.

---

## Self Review

- `ADC-0027`~`ADC-0031`의 결정이 모두 반영됐는가 — **Pass**(§1·§4·§5
  표에서 5개 ADC 전부 인용).
- 새로운 Architecture 결정을 몰래 추가했는가 — **아니오**(§2·§3
  어느 항목도 기존 ADC 원문에 없는 새 책임·경계를 만들지 않았다).
- Thin Caller와 Engine Gateway가 명확히 구분됐는가 — **Pass**(§3
  "담당"/"금지" 목록에서 명시).
- Jarvis Routing과 OmniRoute Routing이 구분됐는가 — **Pass**(§3).
- `domain_fallback_chains`를 새로운 fallback 시스템으로 오해했는가 —
  **아니오**(§4 표 "과장 방지 명시" 열에서 명시적으로 부정).
- `routing_decisions` 제외를 Audit 완료로 과장했는가 — **아니오**
  (§4 표, §13 항목5).
- `priority`가 routing selection으로 검증됐다고 표현했는가 —
  **아니오**(§4 표, §13 항목6).
- `domain_budgets` Evidence 범위를 과장했는가 — **아니오**(§4 표,
  §13 항목7).
- 실제 caller 구현이 아직 없다는 사실이 유지됐는가 — **Pass**(§4
  마지막 행, §5, §9).
- Production Adoption 완료라고 선언했는가 — **아니오**(§5에서
  명시적으로 부정하고 남은 3단계를 나열).
- Architecture/Contract/Freeze가 변경되었는가 — **아니오**(§7).
- 기존 ADC 문서가 수정되었는가 — **아니오**(이 ADR 파일 외 어떤
  파일도 생성·수정하지 않았다).
- 코드 변경이 있는가 — **아니오**(§9).
