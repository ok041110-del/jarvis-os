# ADC-0031: OmniRoute Thin Engine Caller Boundary 확정 (ADC-0027 후속)

## 목적

`docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
§Decision "구현 착수 선행조건" 4번(`IMPLEMENTATION_RULES.md` Scoped
완화 필요 여부)을 재검토한다. `ADC-0028`(`domain_fallback_chains`)·
`ADC-0029`(`routing_decisions`)·`ADC-0030`(`priority`)이 선행조건
2의 세 항목을 개별 처리했던 것과 동일한 방식으로, 이 ADC는
**선행조건 4 하나에만** 답한다. 이 ADC의 목적은 OmniRoute
integration을 구현하는 것이 **아니라**, 현재 `IMPLEMENTATION_
RULES.md`와 `ADC-0027`의 책임 경계를 근거로 **Jarvis OS가 OmniRoute를
어떤 형태로 호출할 수 있는지 Architecture 수준에서 공식적으로
확정하는 것**이다.

직전 Read-only Review(2026-09-07)가 다음을 확인했다.

- 실제 Jarvis repository에 OmniRoute integration caller는
  **존재하지 않는다**(전수 검색 결과 0건 — `.claude/docs/
  integrations/omniroute.md`와 이번 Adoption 절차 자신의 문서 파일
  외 매치 없음). 이 ADC의 모든 판단은 **향후 caller 설계에 대한
  사전 Architecture 판단**이며, 실제 구현 검증이 아니다.
- Thin Engine Caller(Case A)는 현재 `IMPLEMENTATION_RULES.md`
  15·16·17·21행과 충돌하지 않는다(조건부 — 아래 §Q1).
- Jarvis Routing Layer(Case B)·Multi-Engine Gateway(Case C)는
  각각 16·17행, 15·16·21행과 명확히 충돌한다.
- `BASELINE.md` §16.2(794행)는 Execution Layer(Engine Adapter)의
  책임을 "Model/Engine 선택·호출까지의 경계"로 이미 정의해 뒀고,
  그 선택의 내부 구조(누가 실제로 구현하는지)는 `ADC-01`·`ADC-02`·
  `ADC-0003` 판단4가 여전히 Open으로 남긴 영역이라고 명시한다.

이 ADC는 이 확인을 근거로, Thin Engine Caller Boundary를 "현재
`IMPLEMENTATION_RULES.md` 범위 내에서 허용 가능한 caller 형태"로
공식화할지를 결정한다.

근거는 `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`,
`EVIDENCE-0001-omniroute-precondition-verification.md`,
`EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md`,
`hqs/development/IMPLEMENTATION_RULES.md`, `CONSTITUTION.md`,
`BASELINE.md` §16.2, `ARCHITECTURE_GOVERNANCE.md`, 그리고 직전
Read-only Review로만 한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- **`domain_fallback_chains`/`domain_budgets`/`routing_decisions`/
  `priority`** — 각각 `ADC-0028`/`EVIDENCE-0002`/`ADC-0029`/
  `ADC-0030`이 이미 처리했다. 재론하지 않는다.
- **OmniRoute integration 완료, OmniRoute Adoption 완료** — 이 ADC는
  어떤 구현도 완료시키지 않는다.
- **Engine Adapter Contract(§14) 변경, Architecture Freeze 변경** —
  방향조차 제시하지 않는다.
- **`IMPLEMENTATION_RULES.md` 문구의 실제 수정** — `ADC-0027`
  §Next Step이 이미 명시한 대로, 문구 반영은 후속 ADR의 몫이며 이
  ADC가 직접 수행하지 않는다.
- **실제 caller 구현 허용, OmniRoute production 사용 승인** — 이
  ADC는 어떤 코드 작성도 승인하지 않는다.
- **"실제 구현 검증 완료"라는 확정** — Architecture boundary 확정과
  실제 implementation validation은 다른 층위다(§5).
- **`ADC-0027`·`ADC-0028`·`ADC-0029`·`ADC-0030`·`CONSTITUTION.md`·
  `BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·`EVIDENCE-0001`·
  `EVIDENCE-0002` 파일의 실제 수정** — 하지 않는다.
- **ADR 작성** — 하지 않는다.

---

## Q1. Case A/B/C 재확인

### 검토(직전 Review 재인용)

| Case | Jarvis 코드가 아는 대상 | Provider/Model 선택 주체 | 충돌 조항 |
|---|---|---|---|
| A(Thin Engine Caller) | OmniRoute 1개(단일 endpoint) | OmniRoute 내부 | 없음(조건부) |
| B(Jarvis Routing Layer) | provider/model 인지 | Jarvis 코드 | 16행(Engine Routing), 17행(Policy), 조건에 따라 21행 |
| C(Multi-Engine Gateway) | OmniRoute/Claude Code/Other Engine 다수 | Jarvis 코드 | 15행(Engine Gateway), 16행(Engine Routing), 21행(Multi Engine) |

**Case A의 조건**: Jarvis의 Engine Adapter가 (a) 여러 백엔드를 갈아
끼울 수 있는 일반화된 Port/Adapter 인터페이스가 아니라 **단일 함수**
형태를 유지하고, (b) `ADC-0027`이 Jarvis OS 책임으로 명명한 "Routing
Policy"·"Cost/Budget Policy"·"Audit Policy"·"API Key Scope(정책
결정)"에 해당하는 **판정 로직을 Jarvis 코드 자체에 두지 않을 때**
에만 15·16·17·21행 어느 것과도 충돌하지 않는다. 이 두 조건 중 하나
라도 깨지면(일반화된 추상화를 짓거나, Jarvis 코드에 Policy 판정
로직을 넣으면) Case A는 더 이상 Case A가 아니라 사실상 Case B/C로
전환된다.

### Q1 결론

Thin Engine Caller는 위 두 조건을 지키는 한 현재 `IMPLEMENTATION_
RULES.md`와 충돌하지 않는다. 이 결론은 `BASELINE.md` §16.2가 "Model/
Engine 선택·호출까지"를 이미 Execution Layer 책임으로 정의해 뒀다는
사실, 그리고 `ADC-0027` §Decision Boundary(Reversibility — "OmniRoute
의 내부 구현이 어떻게 바뀌든 Jarvis OS Kernel·HQ 코드는 한 줄도
수정되지 않아야 하며, OmniRoute 고유 문법·설정 형식을 알아서는 안
된다")가 이미 구조적으로 Case A를 요구하고 있다는 사실과 정합적이다
— `IMPLEMENTATION_RULES.md`와 `ADC-0027`의 Reversibility 원칙이
서로 다른 근거에서 같은 방향(Thin Caller)을 가리킨다.

---

## Q2. `IMPLEMENTATION_RULES.md` 판단 재확인

직전 Review가 확인한 15·16·17·21행의 정확한 금지 대상(문맥, keyword
match 아님)을 그대로 인용한다.

- 15행(Engine Gateway): Jarvis가 **여러 Engine을 교체 가능하게 만드는
  추상화(Port/Adapter 패턴) 자체**를 짓는 것을 금지 — 단일 함수로
  하나의 대상을 부르는 것은 이미 허용된 형태다.
- 16행(Engine Routing): Jarvis 자신의 코드가 **"여러 Engine 중 무엇을
  부를지"를 결정하는 로직**을 갖는 것을 금지.
- 17행(Policy): Jarvis 코드 안에 **어떤 형태로든 Policy 판정 로직**이
  존재하는 것을 금지.
- 21행(Multi Engine): Jarvis 코드가 **복수 Engine의 존재를 인지하고
  그에 대응하는 코드**를 갖는 것을 금지.

### Q2 결론

다음 원칙이 위 네 조항과 정합적이다.

> **Jarvis OS는 OmniRoute를 단일 Implementation Engine으로 취급하며,
> Jarvis 코드에는 OmniRoute 선택/라우팅/Provider selection/fallback
> 정책을 구현하지 않는다.**

---

## Decision

**Accept (Scoped, Narrow) — OmniRoute Thin Engine Caller Boundary를
현재 `IMPLEMENTATION_RULES.md` 범위 내에서 허용 가능한 caller 형태로
확정한다.**

### 허용(Thin Engine Caller 범위 안)

- 하나의 OmniRoute endpoint를 호출하는 단일 함수.
- request/response translation(Jarvis 포맷 ↔ OmniRoute의 OpenAI-
  compatible 포맷).
- Engine Adapter 수준의 lifecycle handling(취소, 상태 조회 등
  adapter-level behavior).
- OmniRoute의 OpenAI-compatible interface 호출.
- OmniRoute가 자체적으로 routing하도록 요청을 그대로 전달하는 것.

### 금지(Thin Engine Caller 범위를 벗어남 — Case B/C로 전환)

- Jarvis 내부 provider selection.
- Jarvis 내부 model scoring.
- Jarvis 내부 routing 로직.
- Jarvis 내부 fallback engine.
- Jarvis 내부 multi-provider orchestration.
- Jarvis 내부 multi-engine selection.
- `provider_connections.priority`를 Jarvis 코드에서 직접 적용·재구현.
- OmniRoute가 반환한 후보들을 Jarvis가 직접 평가·재랭킹하는 로직.
- Engine Gateway abstraction(일반화된 Port/Adapter 인터페이스).
- OmniRoute 외 다른 Engine을 위한 일반화된 routing abstraction.

### Responsibility Boundary

- **OmniRoute**: Model Routing, Provider selection, Provider Call,
  Runtime Fallback, Egress Execution — `ADC-0027` §Q5 PDP/PEP 표의
  PEP(정책 실행) 측 그대로 유지한다.
- **Jarvis OS**: 단일 함수 호출 + request/response 변환 + adapter-
  level lifecycle handling. `ADC-0027`이 Jarvis 측 PDP(정책 결정)로
  명명한 "Routing Policy"·"Cost/Budget Policy"·"Audit Policy"·
  "API Key Scope(정책 결정)"가 **Jarvis 코드 자체의 판정 로직으로
  구현돼야 하는지, 아니면 OmniRoute 설정(대시보드 등) 형태로 존재해도
  되는지는 이 ADC가 결정하지 않는다** — 그 결정에 따라 caller가
  Case A로 남을지 Case B로 전환될지가 갈리며, 이는 실제 caller
  설계 시점의 별도 판단 대상이다(§Out of Scope).

### Scope

이 ADC가 확정하는 것은 오직 **"Thin Engine Caller 형태가 현재
`IMPLEMENTATION_RULES.md`와 충돌하지 않는다"는 Architecture 판단**
하나다. 다음은 명시적으로 제외한다.

- `domain_fallback_chains`/`domain_budgets`/`routing_decisions`/
  `priority`(각각 무변경 유지 — 아래 §Gate Impact)
- Engine Adapter Contract(§14)의 실제 확정
- `IMPLEMENTATION_RULES.md`/`CONSTITUTION.md`/`BASELINE.md`/
  `ARCHITECTURE_GOVERNANCE.md` 문구의 실제 수정
- OmniRoute 소스 변경, 실제 caller 구현(OmniRoute client, Engine
  Adapter, API endpoint 연결, 환경변수, provider/routing
  configuration, dashboard 변경, test code 추가 전부 포함)
- ADR 작성

### Evidence

- 사용한 것: 직전 Read-only Review의 Case A/B/C 정의와 조항별 충돌
  분석(§Q1·§Q2), `BASELINE.md` §16.2 원문, `ADC-0027` §Decision
  Boundary(Reversibility) 원문.
- 사용하지 않은 것(과장 배제): 실제 caller 구현이 존재한다고
  서술하지 않았다(§목적에서 전수 검색 결과 0건임을 재확인). "Thin
  Caller가 실제로 검증됐다"고 하지 않고 "현재 규칙 문면과 충돌하지
  않는다는 Architecture 판단"으로만 한정했다.

### Gate Impact

`ADC-0027` Implementation Gate 전체 현황:

| Precondition | Current Status |
|---|---|
| `domain_fallback_chains` | `ADC-0028`로 제외(무변경) |
| `domain_budgets` | `EVIDENCE-0002` PASS(무변경) |
| `routing_decisions` | `ADC-0029`로 제외(무변경) |
| `priority` | `ADC-0030`으로 제외(무변경) |
| `IMPLEMENTATION_RULES.md` | **이 ADC로 Thin Caller Boundary 확정 — Architecture/Governance 관점에서 해소 가능 상태가 되었으나, 규칙 문구 자체의 실제 반영(후속 ADR)은 미착수** |

**중요**: `ADC-0031`만으로 Production Implementation Gate가 열리지
않는다. `ADC-0027` §Decision "구현 착수 선행조건" 4번은 "**후속
ADR이** ... 조항을 ... Scoped 완화하기 전까지는 ... Experimental
Implementation조차 착수할 수 없다"고 명시했다(§Q7) — 이는 ADC가 아닌
**ADR** 수준의 조치를 명시적으로 요구한다. 이 ADC는 그 ADR이 무엇을
근거로 삼을지(Thin Caller Boundary가 현재 규칙과 충돌하지 않는다는
판단)를 확정했을 뿐, 그 ADR 자체를 대신하지 않는다. 따라서:

**Precondition 4는 Architecture/Governance 관점에서 해소 가능
상태가 되었지만, `ADC-0027`의 전체 Production Gate는 별도의 Final
Adoption Review(후속 ADR 및 실제 caller 설계 확인)가 필요하다.**

### Decision Boundary(Reversibility)

`ADC-0027` §Decision Boundary와 동일한 원칙을 재확인한다 — 향후
OmniRoute를 다른 Implementation Engine으로 교체하더라도:

- Jarvis Kernel/HQ architecture를 변경하지 않아야 한다.
- OmniRoute 고유 API/설정 형식을 Jarvis 전체에 노출하지 않는다.
- OmniRoute-specific routing logic을 Jarvis에 복제하지 않는다.

**단, 이것을 현재 Engine Adapter Contract(§14)가 요구하는 범위
이상으로 확대하지 않는다** — 이 ADC는 §14 Kernel Public Contract를
확정하지 않으며, 위 원칙은 방향 재확인일 뿐 새로운 Contract 의무를
만들지 않는다.

### Reason

- Q1 — Thin Engine Caller가 두 조건(단일 함수 유지, Jarvis 코드에
  Policy 판정 로직 미포함)을 지키는 한 15·16·17·21행 어느 것과도
  충돌하지 않음을 확인했고, 이것이 `ADC-0027`의 Reversibility
  원칙과도 정합적임을 확인했다.
- Q2 — `IMPLEMENTATION_RULES.md`의 네 조항이 금지하는 것은 "Jarvis
  코드가 여러 Engine을 인지·선택·추상화하는 것"이지 "단일 외부
  Engine을 호출하는 것" 자체가 아니라는 것을 원문 문맥으로 재확인했다.

### Decision Rationale

이 Decision은 `ADC-0027`의 Decision(Accept, Conditional, Scoped)을
재론하지 않는다 — `ADC-0027`이 연 선행조건 4에 대해, "규칙 완화가
필요한가"라는 질문에 "Thin Caller 형태라면 필요 없다"는 조건부
Architecture 판단을 제공할 뿐이다. `ADC-0027`의 Scope·Responsibility
표·Decision Boundary는 모두 그대로 유지된다. **이 ADC는 `ADC-0027`/
`ADC-0028`/`ADC-0029`/`ADC-0030` 파일 자체를 수정하지 않는다** —
동일 구조(후속 Governance Decision으로 개별 precondition의 판단만
확정)를 유지한다.

---

## Out of Scope

- `domain_fallback_chains`/`domain_budgets`/`routing_decisions`/
  `priority`(각각 무변경).
- Engine Adapter Contract(§14)의 실제 확정.
- `IMPLEMENTATION_RULES.md`/`CONSTITUTION.md`/`BASELINE.md`/
  `ARCHITECTURE_GOVERNANCE.md` 문구의 실제 수정.
- 실제 caller 구현(OmniRoute client, Engine Adapter, API endpoint
  연결, 환경변수 추가, provider/routing configuration, dashboard
  변경, test code 추가).
- "Jarvis OS의 Routing Policy·Cost/Budget Policy·Audit Policy가
  Jarvis 코드로 구현돼야 하는지, OmniRoute 설정으로 존재해도 되는지"
  — 이 질문은 실제 caller 설계 시점의 별도 판단 대상이다.
- ADR 작성.
- `ADC-0027`·`ADC-0028`·`ADC-0029`·`ADC-0030` 파일의 직접 수정.

## Risks

- **"Thin Caller 확정 = 전체 Gate 통과"로 오독될 위험**: §Gate
  Impact에서 "`ADC-0031`만으로 Production Implementation Gate가
  열리지 않는다"를 명시적으로 반복해 이 위험을 낮췄다.
- **Case A→B 전이 위험**: 실제 caller를 구현하는 시점에, "Routing
  Policy"·"Cost/Budget Policy" 등을 Jarvis 코드로 편리하게
  구현하려는 유혹이 Case A의 조건(§Q1)을 조용히 깨고 Case B로
  전이시킬 위험 — 이 ADC는 그 전이 조건을 명시적으로 §Decision
  "금지" 목록에 나열해 재확인 지점을 남겼다.
- **ADR 없이도 구현이 시작될 위험**: `ADC-0027`이 ADR을 명시적으로
  요구했음에도, "Architecture 판단은 끝났다"는 이유로 ADR 없이
  Experimental Implementation이 시작될 위험 — §Gate Impact·§Next
  Step에서 ADR 필요성을 재확인했다.

**재검토 조건**: 실제 caller 설계 시점에 Case A의 두 조건(§Q1)이
지켜지지 않는 것으로 판단되면, 이 ADC의 결론(규칙 미충돌)은 그
설계에 적용되지 않으며 별도 Architecture Decision이 필요하다.

## Next Step

1. `ADC-0027` §Decision 선행조건 1~4가 이제 각각 어떤 상태인지
   정리한다: 1(Evidence 영속화, `EVIDENCE-0001`/`EVIDENCE-0002`로
   충족), 2(`priority`/`domain_fallback_chains`/`routing_decisions`,
   `ADC-0028`/`ADC-0029`/`ADC-0030`으로 개별 처리), 3(`domain_budgets`,
   `EVIDENCE-0002` PASS), 4(`IMPLEMENTATION_RULES.md`, 이 ADC로
   Architecture 판단 확정, ADR 미착수).
2. 후속 ADR가 이 ADC의 Thin Caller Boundary 판단을 근거로
   `IMPLEMENTATION_RULES.md`(및 `ADC-0027` §Baseline/Rules 반영
   범위가 이미 제안한 `CONSTITUTION.md`·`BASELINE.md` §14.1·§16.2
   Scoped 갱신)를 실제로 반영할지 검토한다 — 이 ADC는 그 ADR의
   착수를 승인하지 않는다.
3. 실제 caller 설계가 이뤄지는 시점에, 그 설계가 실제로 Case A(§Q1
   두 조건)를 지키는지 별도로 확인하는 Final Adoption Review가
   필요하다 — 이 ADC는 미래의 특정 설계가 Case A라고 미리 보증하지
   않는다.

## Governance Chain 검증

`RFC-0023`(Proposed) → `ADC-0027`(Accept, Conditional·Scoped) →
`ADC-0028`(Accept, Scoped, Narrow — `domain_fallback_chains`) →
`ADC-0029`(Accept, Scoped, Narrow — `routing_decisions`) →
`EVIDENCE-0002`(Evidence — `domain_budgets` PASS) → `ADC-0030`
(Accept, Scoped, Narrow — `priority`) → 이 ADC(Accept, Scoped,
Narrow — `IMPLEMENTATION_RULES.md` Thin Caller Boundary Architecture
판단) → 후속 ADR(예정, 미착수 — 실제 규칙 문구 반영) → Final Adoption
Review(예정, 미착수 — 실제 caller 설계가 Case A인지 확인). 이 ADC는
`ADC-0027`이 연 선행조건 4에 대한 Architecture 판단만 제공했을 뿐,
`ADC-0027`·`ADC-0028`·`ADC-0029`·`ADC-0030`의 Decision 자체를
재론하지 않았다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. `BASELINE.md`
  §16.2가 이미 정의한 Execution Layer 경계 안에서 caller 형태의
  Architecture 적합성만 판단했다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Contract Change — **없음**. §14 Kernel Public Contract를 확정하지
  않았다.
- `CONSTITUTION.md`·`BASELINE.md`·`ARCHITECTURE_GOVERNANCE.md`·
  `IMPLEMENTATION_RULES.md`·Engine Adapter Contract 문서를 이 ADC가
  수정했는가 — **아니오**.
- Architecture Freeze를 해제했는가 — **아니오**.
- 전체 Production Gate를 근거 없이 PASS 처리했는가 — **아니오**
  (§Gate Impact에서 후속 ADR·Final Adoption Review 필요성을 명시).
- 다른 precondition(`domain_fallback_chains`/`domain_budgets`/
  `routing_decisions`/`priority`)을 임의로 변경했는가 — **아니오**
  (§Gate Impact 표에서 전부 무변경으로 명시).
- 실제 코드를 작성했는가 — **아니오**.
- ADR이 필요한가 — **예**(§Next Step), 이 ADC는 그 ADR을 대신하지
  않는다.

## Self Review

- Thin Caller와 Engine Gateway를 구분했는가 — **Pass**(§Q1·§Decision
  "허용"/"금지" 목록에서 "단일 함수"와 "일반화된 Port/Adapter
  추상화"를 명확히 분리).
- 단일 Engine 호출과 Multi Engine routing을 구분했는가 — **Pass**
  (§Q1 Case A vs Case C).
- OmniRoute 내부 routing과 Jarvis routing을 구분했는가 — **Pass**
  (§Responsibility Boundary).
- Engine Adapter와 Engine Gateway를 혼동했는가 — **아니오**(§Decision
  "허용" 목록의 "Engine Adapter 수준의 lifecycle handling"과 "금지"
  목록의 "Engine Gateway abstraction"을 별도 항목으로 명시).
- `IMPLEMENTATION_RULES.md`의 허용/금지 범위를 과장했는가 — **아니오**
  (§Q2에서 각 조항의 금지 대상을 원문 문맥 그대로 재확인, keyword
  match 아닌 실질 기준 사용).
- 실제 integration이 아직 없다는 사실을 유지했는가 — **Pass**(§목적·
  §Evidence에서 전수 검색 결과 0건임을 반복 명시).
- 실제 implementation validation과 Architecture boundary 결정을
  구분했는가 — **Pass**(§Gate Impact에서 "Architecture/Governance
  관점 해소 가능"과 "Final Adoption Review 별도 필요"를 명시적으로
  분리).
- `ADC-0027`의 다른 조건을 변경했는가 — **아니오**(§Gate Impact,
  §Out of Scope).
- 전체 Production Gate를 근거 없이 PASS 처리했는가 — **아니오**.
- Architecture/Contract/Freeze를 변경했는가 — **아니오**(이 ADC 파일
  외 어떤 파일도 생성·수정하지 않았다).
- 실제 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
