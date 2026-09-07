# ADR-0016: OmniRoute Thin Engine Caller — Architecture Freeze Scoped 완화 (ADC-0027 §Decision 선행조건 4 반영)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0016` |
| 제목 | `ADC-0027` §Decision "구현 착수 선행조건" 4번(`IMPLEMENTATION_RULES.md` Scoped 완화)을 실제 문서 반영으로 옮기는 구현 결정 |
| 상태 | **Accepted** |
| Context | `ADC-0027`(Accept, Conditional·Scoped) §Baseline/Rules 반영 범위, `ADC-0031`(Accept, Scoped, Narrow — Thin Engine Caller Boundary Architecture 판단) §Gate Impact, 직전 Governance Review(2026-09-07, Option C — 부분적으로 필요) |
| 관련 RFC | `RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` |
| 관련 ADC | `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031` |
| 관련 Evidence | `EVIDENCE-0001-omniroute-precondition-verification.md`, `EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md` |
| 선행 ADR | `ADR-0015-omniroute-thin-engine-caller-adoption-policy.md`(Consolidation Only — Baseline/Rules 미반영) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0027`~`ADC-0031`의 모든 Decision, `docs/governance/adc/ADC-0003.md` 판단4(여전히 Open) |

이 ADR은 `ADC-0027`~`ADC-0031`이 이미 내린 Decision을 **다시 논의
하지 않는다.** 새로운 Architecture Decision을 추가하지 않는다.
`ADC-0027` §Decision 선행조건 4번과 §Baseline/Rules 반영 범위가 이미
제시한 방향을, 직전 Governance Review(Option C — 부분적으로 필요)의
판단에 따라 **`CONSTITUTION.md` Architecture Freeze 한 곳에만, 최소
범위로** 실제 문서 반영으로 옮기는 구현 결정만 기록한다.

---

## 1. Context

작성 전 `CONSTITUTION.md`(Architecture Freeze, Observation Policy),
`BASELINE.md` §14.1·§16.2, `ARCHITECTURE_GOVERNANCE.md`(Experimental
Implementation 절), `IMPLEMENTATION_RULES.md`(금지 표 15·16·17·21행),
`ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031`, `ADR-0015`,
직전 Governance Review를 재확인했다.

직전 Governance Review(2026-09-07)가 확정한 핵심 판단:

- `CONSTITUTION.md` Architecture Freeze의 "Engine Adapter"·"Model
  Routing" 문구는 `ADC-0027` 이후에도 **원문 그대로**이며, 이 문구가
  좁혀지지 않는 한 `ARCHITECTURE_GOVERNANCE.md`의 Experimental
  Implementation 금지 목록("Engine Gateway/Routing/Adapter 등 기존
  Frozen 또는 Deferred Boundary를 우회하는 것")에 의해 Thin Caller를
  포함한 **어떤 구현도 착수할 수 없다** — 이것이 실질적으로 유일하게
  반드시 고쳐야 하는 문서다.
- `IMPLEMENTATION_RULES.md` 15·16·17·21행은 `ADC-0031`이 이미 확인한
  대로 Thin Engine Caller(단일 함수, Jarvis 코드에 Policy 판정 로직
  미포함)와 **실질적으로 충돌하지 않는다** — 문구를 완화할 필요는
  없고, 이미 허용된 범위임을 확인하는 절만 추가하면 `ADC-0027`
  선행조건 4의 절차적 요구를 충족한다.
- `BASELINE.md` §14.1·§16.2, `ARCHITECTURE_GOVERNANCE.md`, Engine
  Adapter Contract(§14)는 구현을 막는 조항이 아니며 이번 ADR의
  변경 대상이 아니다.

이 ADR은 위 판단을 그대로 채택한다(**Option C — 부분적으로 필요**).

---

## 2. Decision

**Accept — `CONSTITUTION.md` Architecture Freeze에 OmniRoute Thin
Engine Caller 범위로 한정된 Scoped 예외를 추가하고,
`IMPLEMENTATION_RULES.md`에 그 범위가 기존 금지 표와 충돌하지 않음을
확인하는 절을 추가한다. `BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·
Engine Adapter Contract(§14)는 변경하지 않는다.**

이 Decision은 `ADC-0027`~`ADC-0031`의 Decision을 재론하지 않는다 —
그 문서들이 이미 확정한 Responsibility Boundary·Precondition
처리·Thin Caller 정의를 문서 반영으로 옮길 뿐이다.

### 2.1 변경 대상 파일

| 파일 | 변경 종류 | 근거 |
|---|---|---|
| `hqs/development/CONSTITUTION.md` | Architecture Freeze 절에 Scoped 예외 문단 추가(기존 9개 항목 목록 자체는 무변경) | `ADC-0027` §Baseline/Rules 반영 범위, §Decision Rationale |
| `hqs/development/IMPLEMENTATION_RULES.md` | 금지 표(15·16·17·21행)는 무변경, 그 아래에 "OmniRoute Thin Engine Caller 범위 확인" 절 신설 | `ADC-0031` §Q1·§Q2·§Decision |
| `docs/architecture/baseline/BASELINE.md` | **무변경** | 직전 Review §3 — 구현을 막는 조항이 아니므로 이번 ADR의 필수 대상 아님 |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` | **무변경** | 직전 Review §3 — 이 문서 자체는 Thin Caller와 충돌하지 않음, 문제는 `CONSTITUTION.md` 쪽 |
| Engine Adapter Contract(§14, `BASELINE.md` §14.1) | **무변경** | §14.1 "Engine 호출 책임"은 여전히 미결 상태로 유지 — 이 ADR은 그 상태를 확정하지 않는다 |

---

## 3. Responsibility Boundary

`ADC-0027` §Q5 PDP/PEP 표와 `ADC-0031` §Responsibility Boundary를
그대로 인용한다 — 이 ADR은 새 경계를 만들지 않는다.

- **Jarvis OS**: 단일 OmniRoute endpoint 호출 함수, request/response
  변환, Adapter 수준 lifecycle handling.
- **OmniRoute**: Model Routing, Provider selection, Provider Call,
  Runtime Fallback, Egress Execution.
- **Jarvis 금지**: Provider selection, model scoring, 자체 routing/
  fallback, multi-provider orchestration, multi-engine selection,
  Engine Gateway abstraction, `priority` 직접 적용, OmniRoute 후보
  재평가 로직(`ADC-0031` §Decision "금지" 목록 그대로).

---

## 4. Precondition / Gate Resolution

`ADC-0027` §Decision "구현 착수 선행조건" 4개의 최종 상태:

| 선행조건 | 상태 |
|---|---|
| 1. Evidence 영속화 | `EVIDENCE-0001`/`EVIDENCE-0002`로 충족(무변경) |
| 2. FAIL 3건 재해소 | `ADC-0028`/`ADC-0029`/`ADC-0030`으로 Responsibility redesign 처리(무변경) |
| 3. `domain_budgets` 확정 | `EVIDENCE-0002` PASS(무변경) |
| 4. `IMPLEMENTATION_RULES.md` Scoped 완화 | **이 ADR로 문서 반영 완료** — `CONSTITUTION.md` Freeze Scoped 예외 추가 + `IMPLEMENTATION_RULES.md` 범위 확인 절 추가 |

**과장 방지**: 이 표의 4번이 "완료"로 바뀌었다는 것은 `ADC-0027`
§Decision이 명시한 절차적 전제조건(문서 반영)이 충족됐다는 뜻이지,
Thin Caller가 실제로 구현·검증됐다는 뜻이 아니다(§6).

---

## 5. Reversibility

`ADC-0027` §Decision Boundary·`ADC-0031` §Decision Boundary(Reversibility)
원칙을 그대로 유지한다 — OmniRoute의 내부 구현이 바뀌거나 다른
구현체로 교체되더라도 Jarvis OS Kernel·HQ 코드는 한 줄도 수정되지
않아야 하며, OmniRoute 고유 문법·설정 형식을 Kernel·HQ가 알아서는
안 된다. 이 ADR이 추가하는 `CONSTITUTION.md`·`IMPLEMENTATION_RULES.md`
문구도 이 원칙을 조건으로 명시한다(§8 실제 파일 diff 참조) — 이
Scoped 예외를 새로운 Port/Adapter 추상화나 Multi-Engine Gateway로
확대하지 않는다.

---

## 6. Governance Constraints

이 ADR이 하지 않는 것.

- `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031`,
  `EVIDENCE-0001`, `EVIDENCE-0002`, `ADR-0015` 파일의 수정 — 전부
  무변경.
- 새로운 Architecture Decision 추가 — 없음. `CONSTITUTION.md`/
  `IMPLEMENTATION_RULES.md`에 반영하는 내용은 전부 `ADC-0027`·
  `ADC-0031`이 이미 확정한 방향의 문서화일 뿐이다.
- `BASELINE.md` §14.1 "Engine 호출 책임 = 미결" 상태 확정 — 이 ADR은
  그 상태를 바꾸지 않는다. Engine Adapter Contract(§14)는 여전히
  미확정이다.
- **Production Adoption 완료 선언** — 하지 않는다(§9).
- Architecture Freeze 목록의 나머지 7개 항목(Runtime, Pipeline
  Generalization, Task Dispatcher Generalization, Stage Runner,
  Event Bus, Scheduler, Multi-Agent Runtime) 변경 — 없음.

---

## 7. Consequences

- `CONSTITUTION.md` Architecture Freeze의 "Engine Adapter"·"Model
  Routing" 두 항목에 대해서만, OmniRoute Thin Engine Caller 범위에
  한해 `ARCHITECTURE_GOVERNANCE.md`의 "Frozen Boundary 우회 금지"
  적용이 해제된다 — 그 범위를 벗어나는 구현(Engine Gateway, Jarvis
  자체 Routing/Policy 로직 등)은 계속 동결 상태로 남는다.
- `IMPLEMENTATION_RULES.md` 15·16·17·21행의 금지 대상 자체는 전혀
  좁아지지 않는다 — Thin Caller가 애초에 그 금지 대상 밖에 있었다는
  것을 문서로 확인했을 뿐이다.
- 이 ADR 이후에도 실제 caller 코드는 존재하지 않으며, 그 구현·검증은
  별도 단계로 남는다(§9).

---

## 8. 실제 문서 반영 (Implementation)

### 8.1 `hqs/development/CONSTITUTION.md`

Architecture Freeze 절 하단에 Scoped 예외 문단을 추가한다(기존 9개
항목 목록 자체는 한 글자도 바꾸지 않는다).

### 8.2 `hqs/development/IMPLEMENTATION_RULES.md`

금지 표(1~22행)는 한 글자도 바꾸지 않는다. 그 아래(24행 "Execution
Host 구현 허용 범위" 절 앞)에 "OmniRoute Thin Engine Caller 범위
확인" 절을 신설한다.

*(실제 diff는 §10 Implementation Boundary 직후 파일 수정으로
반영했다 — 아래 Final Review §12에서 diff 결과를 대조한다.)*

---

## 9. Implementation / Validation Boundary — Production Adoption 미완료 확인

**이 ADR이 확정하는 것**: `ADC-0027` §Decision 선행조건 4번(문서
반영)이 충족되었다는 것뿐이다.

**이 ADR이 확정하지 않는 것**:

> ~~"OmniRoute Production Adoption 완료"~~

이런 선언은 하지 않는다. 실제 Production 구현을 향해 남은 단계는
`ADR-0015` §5가 이미 정리한 것과 동일하게 셋이다.

1. **Thin Engine Caller 실제 구현** — 코드 한 줄도 작성되지 않았다
   (전수 검색 0건, `ADC-0031` §목적 재확인 상태 유지).
2. **실제 Integration Validation** — 구현된 caller가 `ADC-0031` §Q1
   두 조건(단일 함수 유지, Policy 판정 로직 미포함)을 실제로 지키는지
   확인.
3. **Final Adoption Review** — 위 1·2 완료 후, `ADC-0027`이 정의한
   Responsibility 분담(PDP/PEP)이 실제로 지켜지는지 확인하는 최종
   검토.

이 ADR은 위 세 단계 중 어느 것도 수행하지 않았고 승인하지 않는다 —
문서 반영(§8)만 수행했다.

---

## 10. Implementation Boundary (코드/OmniRoute 무변경 확인)

- OmniRoute caller 구현 — 없음.
- Engine Adapter 구현 — 없음.
- API 연결, 환경변수, provider/routing configuration — 없음.
- Dashboard 변경 — 없음.
- OmniRoute source 변경 — 없음.
- 테스트 코드 — 없음.
- `core/`, `hqs/development/mvp/`, `hqs/investment/`, `dashboard/`
  Production Code — 무변경.

**문서 반영(§8 CONSTITUTION.md·IMPLEMENTATION_RULES.md) 외 어떤
코드·설정도 변경하지 않았다.**

---

## 11. Related RFC / ADC / ADR / Evidence

- `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`
- `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
- `docs/architecture/core/ADC-0028-domain-fallback-chains-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0029-routing-decisions-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0030-priority-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md`
- `docs/architecture/core/ADR-0015-omniroute-thin-engine-caller-adoption-policy.md`
- `docs/architecture/core/EVIDENCE-0001-omniroute-precondition-verification.md`
- `docs/architecture/core/EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md`

## 12. Open Conditions

1. **Thin Engine Caller 실제 구현** — 미착수.
2. **실제 Integration Validation** — 미착수.
3. **Final Adoption Review** — 미착수.
4. `ADC-0031` §Out of Scope가 남긴 질문 — "Jarvis의 Routing Policy·
   Cost/Budget Policy·Audit Policy가 Jarvis 코드로 구현돼야 하는지,
   OmniRoute 설정으로 존재해도 되는지" — 실제 caller 설계 시점의
   별도 판단 대상으로 유지.
5. `BASELINE.md` §14.1 "Engine 호출 책임 = 미결" — 이 ADR로 확정되지
   않았다. 향후 §14 Kernel Public Contract 확정이 필요하면 별도
   Architecture Decision 대상이다.
6. `ADC-0029`/`ADC-0030`이 남긴 잔여 미검증 항목(`routing_decisions`
   Audit gap, `priority` tie-break 영향 UNVERIFIED) — 무변경 유지.

---

## Self Review

- `ADC-0027`~`ADC-0031`의 Decision을 뒤집었는가 — **아니오**(§2·§3·
  §4 전부 기존 Decision을 그대로 인용·반영했다).
- 새로운 Architecture Decision을 추가했는가 — **아니오**(§2 Decision
  본문 참조 — `ADC-0027`·`ADC-0031`이 이미 확정한 방향의 문서화).
- `CONSTITUTION.md` Freeze 변경 범위가 최소인가 — **Pass**. 9개
  항목 목록 자체는 무변경, Scoped 예외 문단만 추가했고 그 범위도
  Thin Engine Caller로 명시적으로 한정했다(§8.1).
- `IMPLEMENTATION_RULES.md` 15·16·17·21행이 실제로 완화됐는가 —
  **아니오**. 금지 표는 한 글자도 바꾸지 않았고, 범위 확인 절만
  추가했다(§8.2).
- `BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·Engine Adapter
  Contract(§14)를 변경했는가 — **아니오**(§2.1 표, §10).
- Production Adoption 완료를 선언했는가 — **아니오**(§9에서 명시적
  으로 부정하고 남은 3단계 나열).
- Reversibility 원칙을 유지했는가 — **Pass**(§5, §8.1 diff 문구에
  포함).
- 코드/OmniRoute를 변경했는가 — **아니오**(§10).
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
