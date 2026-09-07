# ADC-0027: Model Routing / Engine Adapter — OmniRoute Conditional Adoption Direction (RFC-0023 후속)

## 목적

`docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`
§9 Required Decision 5개 항목에 대해 판단한다. RFC-0023은 스스로
"Freeze 해제가 필요하다"를 전제하지 않고 Freeze 유지/부분 해제(Scoped
Experimental)/재검토 보류 세 선택지를 비교한 뒤 실제 선택을 이 ADC로
위임했다(§6·§9). 이 ADC는 그 위임에 답한다.

근거는 RFC-0023과 그것이 인용한 Evidence(`hqs/development/CONSTITUTION.md`
Architecture Freeze·Evidence Review 원칙, `hqs/development/IMPLEMENTATION_RULES.md`
금지 표, `docs/architecture/baseline/BASELINE.md` §14.1·§16.2,
`docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0003-adc-0010-reassessment.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0004-engine-mvp-closure-and-production-entry.md`,
`docs/governance/adc/ADC-0003.md` 판단 4, `docs/governance/rt/RT-0001.md`
Candidate 2, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`,
`.claude/docs/integrations/omniroute.md`, `.claude/docs/SMOKE_TEST-2026-08-08.md`)로만
한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- **Multi-Agent Runtime과 `CONSTITUTION.md` Freeze 목록의 나머지
  항목**(Runtime, Pipeline Generalization, Task Dispatcher
  Generalization, Stage Runner, Event Bus, Scheduler) — RFC-0023 §5가
  이미 Out of Scope로 배제했고, 이 ADC도 재론하지 않는다.
- **Engine Caller 위치**(`ADC-0010`의 C1~C6 판단) — 재조사하지 않는다.
  다만 §Q6에서 이 Decision이 실행될 경우 `ADC-0010` C1(Kernel Engine
  Port/Adapter)의 선행조건 중 하나에 미치는 파급만 기록한다(재판단은
  아니다).
- **ADC-01**(Model↔Component 대응)·**ADC-02**(Runtime 존폐,
  `docs/decisions/adc/ADC.md`) — Open 상태 그대로 유지, 재론하지 않는다.
- **ADC-07**(Resource/Token 예산 이중 소속, `docs/decisions/adc/ADC.md`,
  Open/NEXT) — 아래 Responsibility에서 "Cost/Budget Policy"를 다루지만,
  이는 OmniRoute Provider 비용에 한정된 서술이며 ADC-07이 다투는
  "Token 예산이 Scheduler 책임인지 Policy 책임인지"라는 더 넓은 질문을
  해소하지 않는다.
- **Workflow Adapter 트랙**(`ADC-0019`~`ADC-0026`, `ADR-0009`) —
  §16.6 Workflow 그래프 실행 책임과는 별개 seam(`GLOSSARY.md`)이며
  이 ADC는 그 Gate 진행 상태에 영향을 주지 않는다.
- **§14 Kernel Public Contract의 실제 확정**(함수 시그니처, Port
  인터페이스 코드) — 아래 Responsibility는 개념 수준 방향 제시이며
  `RFC-0019` §7 Pseudo-Contract와 동일한 지위(실행 가능한 코드 아님)를
  유지한다.
- **`BASELINE.md`·`CONSTITUTION.md`·`IMPLEMENTATION_RULES.md` 파일의
  실제 수정** — 방향만 제시하고 실행은 후속 ADR에 위임한다(`ADC-0015`
  선례와 동일한 원칙).
- **Production 구현 착수 승인** — 이 ADC는 어떤 코드 구현도 승인하지
  않는다(§Next Step).
- **OmniRoute를 §16.1 Governance(Accept) Kernel Module로 만드는 것** —
  아래 "Provider Governance"라는 책임 명칭은 §16.1과 무관한, Provider
  선택 정책을 가리키는 서술적 이름일 뿐 새 Kernel Module이 아니다.

이 ADC가 판단하는 것은 RFC-0023 §9의 5개 질문과, 그 답이 Accept
방향이라면 함께 확정해야 하는 Scope·Responsibility·Decision Boundary
방향이다.

---

## Q1. RFC-0023 §0의 절차적 해석은 타당한가 (§9 항목 5)

### 검토

RFC-0023 §0은 `ADC-0010`의 "Phase 1 종료 후 불변 원칙과 충돌한다"는
판단과 `GOVERNANCE-REVIEW-0004`의 "사실상 Governance 경로가 막혀
있다"는 서술이 모두 **C4(Development HQ가 Engine Caller가 되는 경로)**
판단 맥락에 한정된다고 해석했다 — `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md`
(Development HQ 트랙, Phase 1 종료 후 불변)를 다시 여는 경로만
막혔을 뿐, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
Architecture Governance 절차(RFC → ADC → ADR)로 `CONSTITUTION.md`
Freeze 목록을 직접 재검토하는 경로까지 막는다고 읽을 근거는 원문에
없다는 것이다.

이 ADC가 원본을 다시 대조한 결과도 동일하다 — `ADC-0010` §C4, §부족한
Evidence 4, `GOVERNANCE-REVIEW-0003` §C4, `GOVERNANCE-REVIEW-0004` ④
네 곳 모두 서술 대상이 "C4(Development HQ) 후보"로 명시적으로 한정돼
있으며, "Architecture Governance 절차 자체가 Freeze 목록에 접근할 수
없다"는 문장은 어디에도 없다. 오히려 `ADC-0010` §Risks는 *"재검토
조건: §부족한 Evidence 1~6 중 하나라도 실제로 충족되면, 이 Decision은
기존 Governance 절차... RFC → ADC → ADR → Baseline Update를 통해
재검토 대상이 된다"*고 명시해, Architecture Governance 절차 자체는
항상 열려 있다는 것을 오히려 확인해 준다.

### Q1 결론

**타당하다.** RFC-0023 §0의 해석을 Accept한다 — C4 경로(Development
HQ)가 막혀 있다는 것과 Architecture Governance 절차(RFC → ADC → ADR)
자체가 막혀 있다는 것은 서로 다른 명제이며, 원본 문서 어디에도 후자를
주장한 곳이 없다. 이 ADC 자신이 Architecture Governance 트랙
(`docs/architecture/core/`)에서 작성되고 있다는 사실 자체가 이 결론을
실증한다.

---

## Q2. 재검토 착수 여부 (§9 항목 1)

### 검토

RFC-0023 §4가 정리한 대로, `CONSTITUTION.md`의 정성적 재검토 조건
("반복된 실전 Evidence")과 `RT-0001`의 정량 Trigger("Engine 수 ≥ 2")는
둘 다 미충족이다. 그러나 `ARCHITECTURE_GOVERNANCE.md`의 Architecture
Need 원칙은 사전에 정의된 Trigger 미충족 상태에서도 실제 Architecture
Need가 관찰되면 재검토를 시작할 권한을 명시적으로 부여한다. 실제
계정을 사용한 5라운드 검증에서 PASS/FAIL이 항목별로 갈렸다는 사실은
"Evidence가 전혀 없다"·"완전히 실패했다" 어느 쪽도 아닌, 판단 재료가
될 만큼 구체적인 관찰이라는 신호다(RFC-0023 §4).

### Q2 결론

**Accept — 재검토 착수.** Architecture Need 원칙에 근거해 착수하되,
이것이 곧 §Q5의 Option 선택이나 Freeze 해제를 의미하지 않는다 — 착수
여부와 실제 판단 내용은 분리된 질문이다.

---

## Q3. Escalate 응답 (§9 항목 4)

### 검토

`docs/governance/adc/ADC-0003.md` 판단 4는 Execution Layer의
Multi-Model 지원을 Development HQ ADC의 권한 밖으로 Escalate하며
*"별도 Jarvis OS 수준 RFC 상정 여부는 이 ADC의 결정 범위 밖"*이라고
남겼다. RFC-0023이 그 Escalate 이후 최초의 Jarvis OS 수준 RFC이고,
이 ADC가 그 RFC의 후속이다 — 계보가 끊기지 않았다.

### Q3 결론

**이 RFC-0023 → ADC-0027 계보를 그 Escalate에 대한 공식 응답으로
인정한다.** `docs/governance/adc/ADC-0003.md` 판단 4 자체의 재판단은
아니다(그 문서는 수정하지 않는다) — 다만 그 문서가 열어 둔 공백을
메우는 절차가 지금 이 ADC로 실제 진행되고 있음을 확인한다.

---

## Q4. Evidence 특성화 — 무엇을 판단 근거로 쓸 수 있는가

### 검토

RFC-0023 §3.3이 이미 PASS 4건을 성격별로 분리했다 — 이 ADC는 그
분리를 그대로 받아들이고, Decision 근거로 사용할 수 있는 것과 없는
것을 명확히 가른다.

| Evidence | 성격 | 이 ADC가 근거로 쓰는 방식 |
|---|---|---|
| Provider Exclusion (PASS) | 접근 통제 | OmniRoute가 지정된 Provider를 실제로 배제할 수 있다는 근거로 사용 |
| API Key Scope (PASS) | 접근 통제 | OmniRoute가 Key 사용 범위를 스코프대로 제한할 수 있다는 근거로 사용 |
| Egress Audit (PASS) | 감사 | OmniRoute가 외부 트래픽을 감사 가능하게 만들 수 있다는 근거로 사용 |
| Auto-Routing/내부 fallback (PASS) | 라우팅 실행 | OmniRoute가 여러 Provider/Model 사이의 자동 선택·fallback을 실제로 실행할 수 있다는 근거로 사용 |
| `priority` (FAIL) | 라우팅 정책 실행 | **근거로 쓰지 않는다** — 오히려 §Q5·§Decision의 선행조건을 발생시키는 반대 방향 Evidence로 사용 |
| `domain_fallback_chains` (FAIL) | 라우팅 정책 실행 | 위와 동일 |
| `routing_decisions` (FAIL) | 감사 기록 | 위와 동일 |
| `domain_budgets` (UNVERIFIED) | 비용 정책 | Accept도 Reject도 아닌 공백 — 근거로 쓰지 않는다 |

**핵심 관찰**: FAIL 3건(`priority`, `domain_fallback_chains`,
`routing_decisions`)은 우연히 흩어진 결함이 아니라, 아래 §Q5가
설계하는 Responsibility 분담의 정확히 두 지점을 직접 겨냥한다 —
"Routing Policy"(Jarvis OS가 우선순위·fallback 체인을 정책으로
결정)는 OmniRoute의 `priority`·`domain_fallback_chains` **실행**이
전제돼야 의미가 있고, "Audit Policy"(Jarvis OS가 라우팅 결과를
감사)는 OmniRoute의 `routing_decisions` **기록**이 전제돼야 의미가
있다. 이 셋이 모두 FAIL이라는 것은 곧 **Responsibility 분담의
실현 가능성 자체에 대한 직접적 반대 증거**다.

### Q4 결론

PASS 4건은 "OmniRoute가 실행 계층(Provider Connection/Call, Egress
Execution, Model Routing Execution)을 담당할 수 있다"는 후보 자격을
뒷받침한다. FAIL 3건은 "Jarvis OS가 그 실행을 신뢰하고 정책·감사를
얹을 수 있는가"라는, Responsibility 분담이 실제로 작동하기 위한
전제조건이 **아직 충족되지 않았다**는 것을 보여준다. 이 비대칭이
§Decision을 Conditional로 만드는 핵심 근거다.

---

## Q5. Option 선택과 Responsibility 설계 방향 (§9 항목 2)

### 검토

RFC-0023 §6은 Freeze 유지(A)/부분 해제·Scoped Experimental(B)/재검토
보류(C) 세 선택지를 제시했다. 이 ADC는 그중 하나를 그대로 고르지
않는다 — RFC-0023도 "실제 선택은 §9 Required Decision이 후속 ADC로
위임한다"고 했을 뿐 ADC가 A/B/C 중 하나에 묶인다고 하지 않았다.

- **A(Freeze 유지)를 그대로 택하면**: PASS 4건(§Q4)이 보여주는 구체적
  진전을 아무 결론 없이 방치하게 된다 — RFC-0023 §8도 이를 "완전히
  무시하기에는 구체적"이라고 이미 지적했다.
- **B(Scoped Experimental)만 택하면**: 관찰 축적 경로일 뿐 "무엇을
  향해" 관찰을 쌓는지 목적지가 없다 — Responsibility 분담이라는
  설계 방향 없이 관찰만 반복하면 다음 판단 시점에도 같은 논의를
  반복하게 된다.
- 따라서 이 ADC는 **A와 B 사이의 세 번째 지점**을 택한다 — "OmniRoute를
  Model Routing/Engine Adapter의 **목표 구현 후보(target
  implementation candidate)**로 지정하고, 그 아래에서 어떤 조건이
  충족되면 실제 구현(Experimental Implementation부터)에 착수할 수
  있는지를 구체적으로 규정"하는 것이다. 이것이 사용자가 지시한
  Decision("OmniRoute를 Jarvis OS의 Model Routing / Execution Layer
  구현체로 채택한다")의 형태이며, §Q4의 비대칭(PASS는 후보 자격을
  주지만 FAIL은 실행을 아직 허가하지 않음)과 정합하도록 **Conditional**
  로 좁힌다.

### Responsibility 설계 — PDP/PEP 원칙 적용

`RFC-0019` §4가 이미 이 저장소에서 쓴 Policy 판정 원칙(PDP/PEP —
Policy Decision Point와 Policy Enforcement Point의 분리)을 그대로
적용한다. Jarvis OS는 **무엇을 허용할지 결정**하고(PDP), OmniRoute는
**그 결정을 기계적으로 실행**한다(PEP) — 어느 쪽도 다른 쪽의 책임을
흡수하지 않는다.

| 축 | Jarvis OS (PDP — 정책 결정) | OmniRoute (PEP — 정책 실행) |
|---|---|---|
| Provider | Provider Governance(어떤 Provider를 허용/배제할지 결정) | Provider Connection(실제 연결 수립) |
| Routing | Routing Policy(우선순위·fallback 규칙을 정책으로 결정) | Model Routing Execution, Runtime Fallback(그 규칙을 실제로 실행) |
| 인증 | API Key Scope(Key 사용 범위를 정책으로 결정) | Provider Call(그 범위 안에서 실제 호출 수행) |
| 비용 | Cost/Budget Policy(예산 규칙을 정책으로 결정 — ADC-07과 무관, §목적 참조) | (해당 없음 — OmniRoute 책임 목록에 비용 실행 항목 없음, `domain_budgets` UNVERIFIED이므로 이 축은 §Decision에서 전면 보류) |
| 감사 | Audit Policy(무엇을 감사할지, 위반을 어떻게 처리할지 결정) | Egress Execution(실제 외부 트래픽 발생), 라우팅 결과 기록 제공 |

**이 표는 §14 Kernel Public Contract가 아니다.** 함수 시그니처, Port
인터페이스, 클래스 이름 어느 것도 정의하지 않는다 — "어느 쪽이
무엇을 결정하고 무엇을 실행하는가"라는 책임 소재만 방향으로
제시한다(`RFC-0019` §7과 동일한 지위). "Provider Governance"·"Routing
Policy"·"Cost/Budget Policy"·"Audit Policy"라는 이름이 §6 Concept
Model에 새 Entry로 즉시 등재되는 것도 아니다 — 그 분류(예: Policy로
분류할지)는 후속 ADR이 Baseline 반영 시점에 판단한다.

### Q5 결론

**A/B/C 중 하나가 아니라, "목표 후보 지정 + Responsibility 방향
제시 + Conditional 게이트"를 Decision으로 택한다(아래 §Decision).**
이는 RFC-0023 §6의 세 선택지보다 구체적이지만, §Q4가 확인한 FAIL
3건·UNVERIFIED 1건 때문에 즉시 구현을 허가하는 것과는 다르다.

---

## Q6. 선행조건 — Evidence 영속화 (§9 항목 3)

### 검토

RFC-0023 §3.2는 5라운드 검증 결과가 저장소에 재현 가능한 형태로
영속화되지 않았다는 공백을 기록했다. `CONSTITUTION.md` Observation
Policy("사실만 기록한다")와 Evidence Review 원칙은 재현 가능한
원본을 요구한다 — 이 공백이 해소되지 않은 채로 실제 구현(Experimental
Implementation 포함)에 착수하면, 향후 그 구현의 정당성을 재확인할
방법이 없다(`IMPLEMENTATION_RULES.md` "[Evidence 출처 상태]" 선례가
이미 보여준 문제와 동일한 종류).

### Q6 결론

**선행조건이다.** 아래 §Decision의 조건 목록에 포함한다 — 영속화가
없으면 §Q5의 목표 후보 지정과 무관하게 어떤 구현 단계(Experimental
포함)도 시작할 수 없다.

---

## Q7. Freeze/`IMPLEMENTATION_RULES.md`/Reversibility 경계

### 검토

`ARCHITECTURE_GOVERNANCE.md`의 Experimental Implementation 절은 허용
범위를 열거하면서도 **금지** 항목에 "Engine Gateway/Routing/Adapter
등 기존 Frozen 또는 Deferred Boundary를 우회하는 것"을 명시한다.
`IMPLEMENTATION_RULES.md`의 "Engine Gateway 구현 금지", "Engine
Routing 구현 금지", "Multi Engine 지원 코드 작성 금지"는 지금 이
ADC로 해제되지 않는다 — 이 ADC는 방향만 정하고 문서 자체를 수정하지
않는다(§목적 "이 ADC가 답하지 않는 것").

**따라서 이 ADC의 Accept는 그 자체로 어떤 구현(Experimental 포함)도
열지 않는다.** Scoped 완화는 `ADC-0013`→`ADR-0003`,
`ADC-0016`→`ADR-0006`, `ADC-0015`(후속 ADR 예정) 선례와 동일하게
**후속 ADR**의 몫이며, 그 ADR조차 §Q6 선행조건과 아래 §Decision의
FAIL 항목 재해소 조건이 충족된 뒤에만 착수 대상이 된다.

**Decision Boundary(Reversibility)**: `RFC-0019` §7 Reversibility
조건("이 Adapter를 제거하고 다른 구현체로 교체해도 Kernel과 HQ가
정의하는 코드는 한 줄도 수정되지 않아야 한다")과 동일한 원칙을
OmniRoute에 적용한다 — OmniRoute의 내부 구현(설정 스키마, 라우팅
알고리즘, 신규 기능 추가/제거)이 변경되거나 OmniRoute 자체가 다른
구현체로 교체되더라도, Jarvis OS Kernel·HQ 코드는 §Q5 표가 정의한
PDP측 인터페이스(정책을 넘겨주고 결과를 값으로 돌려받는 것)만
알아야 하며 OmniRoute 고유 문법·설정 형식을 알아서는 안 된다. 이
경계가 무너지면 Engine Adapter라는 이름 자체("교체 가능한 seam")가
무의미해진다.

### Q7 결론

이 ADC의 Accept는 **문서·구현 어느 것도 지금 바꾸지 않는다** — 방향과
조건만 확정한다. Reversibility는 §Decision의 불변조건으로 포함한다.

---

## Decision

**Accept (Conditional, Scoped) — OmniRoute를 Model Routing / Engine
Adapter(§16.2 Execution Layer 내부 구조)의 목표 구현 후보로 지정한다.
Production 구현 착수는 아래 조건이 모두 충족되기 전까지 차단된다.**

### Scope

- Model Routing / Engine Adapter 영역(`CONSTITUTION.md` Architecture
  Freeze 목록의 해당 두 항목, `BASELINE.md` §14.1 Kernel 책임 후보
  3번, §16.2 Execution Layer 내부 구조)에 한정한다.
- Multi-Agent Runtime, Runtime, Pipeline Generalization, Task
  Dispatcher Generalization, Stage Runner, Event Bus, Scheduler —
  `CONSTITUTION.md` Freeze 목록의 나머지 7개 항목은 변경하지 않는다.
- Conversation Layer(사용자 지시가 언급한 별도 영역)는 이 ADC의 어떤
  Evidence·논증도 다루지 않았다 — 명시적으로 범위 밖이다.
- Engine Caller 위치(`ADC-0010`), Workflow Adapter 트랙(`ADC-0019`~
  `ADC-0026`)도 범위 밖이다(§목적).

### Responsibility

§Q5의 PDP/PEP 표를 목표 방향으로 채택한다.

- **Jarvis OS(정책 결정, PDP)**: Provider Governance, Routing Policy,
  API Key Scope(정책 결정 측), Cost/Budget Policy, Audit Policy.
- **OmniRoute(정책 실행, PEP)**: Provider Connection, Model Routing
  Execution, Provider Call, Runtime Fallback, Egress Execution.

이 분담은 §14 Kernel Public Contract가 아니며, 실제 Interface·함수
시그니처는 후속 ADR/Implementation Plan이 별도로 정의한다.

**주의**: 이 표는 목표 방향이지 검증된 현재 능력이 아니다 — 특히
Jarvis OS의 "Routing Policy"·"Audit Policy"가 OmniRoute의 "Model
Routing Execution"·"Runtime Fallback"에 정책을 넘겨 실행시키려면
OmniRoute의 `priority`·`domain_fallback_chains`·`routing_decisions`
메커니즘이 동작해야 하는데, 이 셋은 모두 FAIL이다(§Q4·아래 Evidence).
"Auto-Routing/내부 fallback 실행"이 PASS라는 것은 OmniRoute가 기본
자동 fallback을 실행할 수 있다는 근거일 뿐, Jarvis OS가 지정한
**커스텀 정책**(우선순위, 도메인별 fallback 체인)을 그대로 실행한다는
근거가 아니다 — 이 둘을 혼동하지 않는다.

### Evidence

- 채택 근거로 사용한 것: Provider Exclusion·API Key Scope·Egress
  Audit·Auto-Routing/내부 fallback(PASS 4건, §Q4) — OmniRoute가 PEP
  실행 후보 자격을 갖췄다는 근거로만 사용한다.
- 채택 근거로 사용하지 않은 것(오히려 조건을 발생시킨 것): `priority`,
  `domain_fallback_chains`, `routing_decisions`(FAIL 3건),
  `domain_budgets`(UNVERIFIED 1건) — 어떤 Contract 요구사항으로도
  승격하지 않는다(§Q4).
- Evidence 영속화 조건(§Q6): 5라운드 검증(또는 그 재현)의 원본 로그·
  설정·출력을 저장소에 재현 가능한 형태로 기록하는 것을, 아래
  "구현 착수 선행조건" 1번으로 명시한다.

### Architecture

- 기존 Engine Adapter 경계(§16.2 — "Model/Engine 선택·호출까지의
  경계")를 그대로 유지한다 — 이 Decision은 그 경계를 확장하거나
  재정의하지 않는다. OmniRoute는 그 경계 **안**의 구현 후보일 뿐이다.
- OmniRoute 자체를 §16.1 Governance(Accept) Kernel Module이나 새로운
  Kernel Public Contract(§14)로 만들지 않는다 — "Provider Governance"는
  §16.1과 무관한 정책 결정 책임의 서술적 이름이다.
- Freeze 변경 범위를 최소화한다 — `CONSTITUTION.md` Architecture
  Freeze 목록에서 Engine Adapter·Model Routing 두 항목만 대상으로
  하며, 그 문구 자체의 실제 수정도 이 ADC가 아니라 후속 ADR이 수행한다.

### Decision Boundary

`RFC-0019` §7과 동일한 Reversibility 원칙을 적용한다 — OmniRoute의
내부 구현이 어떻게 바뀌든(설정 스키마 변경, 기능 추가/제거, 다른
Gateway로 교체) Jarvis OS Kernel·HQ 코드는 한 줄도 수정되지 않아야
한다. OmniRoute 고유 문법·설정 형식은 Engine Adapter 구현 내부에만
존재해야 하며 Kernel·HQ가 그것을 알게 되는 순간 이 경계는 깨진다.

### 구현 착수 선행조건 (모두 충족돼야 후속 ADR·Experimental Implementation 검토 가능)

1. **Evidence 영속화**: 5라운드 검증(또는 재검증)의 원본 로그·설정·
   출력을 저장소에 재현 가능한 형태로 기록한다(§Q6).
2. **FAIL 3건 재해소**: `priority`, `domain_fallback_chains`,
   `routing_decisions`가 재검증에서 PASS로 확인되거나, PASS로 확인될
   수 없다면 Responsibility 분담(Routing Policy·Audit Policy 축)이
   그 실패를 전제로 재설계돼야 한다(§Q4의 비대칭 해소).
3. **`domain_budgets` 검증**: UNVERIFIED 상태를 PASS/FAIL 중 하나로
   확정한다 — 확정 전까지 Cost/Budget Policy 축의 실행 가능성은
   공백으로 남는다.
4. **`IMPLEMENTATION_RULES.md` Scoped 완화**: 후속 ADR이 "Engine
   Gateway/Engine Routing/Multi Engine 지원 코드 작성 금지" 조항을
   이 Scope(§Scope)에 한해 좁혀 완화하기 전까지는, 위 1~3이 전부
   충족되더라도 Experimental Implementation조차 착수할 수 없다
   (`ARCHITECTURE_GOVERNANCE.md`가 Frozen Boundary 우회를 Experimental
   에서도 명시적으로 금지, §Q7).

### Reason

- Q1 — RFC-0023의 절차적 해석이 원본과 대조해 타당함을 확인했다.
- Q2 — Architecture Need 원칙에 근거해 재검토 착수를 Accept했다.
- Q3 — `ADC-0003` 판단 4의 Escalate에 대한 공식 응답 계보로 인정했다.
- Q4 — PASS 4건과 FAIL 3건·UNVERIFIED 1건의 비대칭을 근거로, 후보
  자격은 Accept하되 실행 허가는 Condition으로 분리했다.
- Q5 — RFC-0023의 A/B/C 어느 것도 그대로 택하지 않고, PDP/PEP 원칙
  (`RFC-0019` §4 선례)으로 Responsibility 방향을 제시하는 세 번째
  지점을 택했다.
- Q6 — Evidence 영속화 공백을 구현 착수의 선행조건으로 명시했다.
- Q7 — Freeze 문서·`IMPLEMENTATION_RULES.md`는 이 ADC로 변경되지
  않으며, Reversibility를 불변조건으로 남겼다.

### Decision Rationale

이 Decision은 `ADC-0010`(Engine Caller 위치 6개 후보 전부 Not
Accepted), `docs/decisions/adc/ADC.md`의 ADC-01·ADC-02·ADC-07(전부
Open), `ADC-0019`~`ADC-0026`(Workflow Adapter 트랙)을 전혀 재론하지
않는다 — 이 Decision이 판단한 것은 "Model Routing/Engine Adapter의
목표 구현 후보를 지정할 수 있는가"라는 좁은 질문 하나이며, 그 답이
"예, 그러나 조건부"라는 것뿐이다. `CONSTITUTION.md` Architecture
Freeze 목록도 아직 문면 그대로다 — 이 Decision은 그 문면을 바꿀
방향을 제시했을 뿐 바꾸지 않았다.

---

## Baseline / IMPLEMENTATION_RULES.md 반영 범위 (다음 ADR을 위한 지침, 이 ADC가 직접 반영하지 않음)

### `hqs/development/CONSTITUTION.md` Architecture Freeze 반영 범위

"Engine Adapter", "Model Routing" 두 항목의 문구를, 완전 삭제가
아니라 "OmniRoute를 목표 후보로 하는 Conditional Accept 상태 —
`ADC-0027` 참조, 구현 착수 선행조건 미충족으로 Production 구현은
여전히 동결"과 같은 방향으로 좁히는 것을 제안한다(최종 문구는 ADR이
확정). 나머지 7개 Freeze 항목 문구는 무변경.

### `BASELINE.md` §14.1·§16.2 반영 범위

§14.1 표의 "Engine 호출 책임 = 미결" 행은, "부분 진전(`ADC-0027`,
Conditional) — 실행 후보 지정, Contract 미확정"과 같은 방향으로
갱신을 제안한다. §16.2 "이 Accept가 결정하지 않는 것" 문단(Multi-Model
Routing 등)은, 그 Open 상태가 `ADC-0027`로 부분적으로(방향만) 진전됐음을
반영하되 ADC-01·ADC-02·`ADC-0003` 판단 4가 여전히 Open이라는 문장은
유지하는 것을 제안한다.

### `hqs/development/IMPLEMENTATION_RULES.md` 반영 범위

"Engine Gateway 구현 금지", "Engine Routing 구현 금지", "Multi Engine
지원 코드 작성 금지" 세 항목을, §Decision "구현 착수 선행조건" 1~4가
전부 충족된 뒤에 한해 §Scope 범위(OmniRoute를 통한 Model Routing/
Engine Adapter, PDP/PEP 경계 준수) 안에서만 Scoped 완화하는 방향을
제안한다 — 전면 해제가 아니라 `ADC-0013`→`ADR-0003` 선례처럼 조건이
명시된 좁은 문구로 교체하는 것을 다음 ADR에 제안한다.

이 반영은 이 ADC가 직접 수행하지 않는다 — 다음 ADR의 몫이며, 그 ADR
착수 자체도 §Decision의 선행조건 1~3이 먼저 충족돼야 한다.

---

## Out of Scope

- Multi-Agent Runtime 및 `CONSTITUTION.md` Freeze 목록의 나머지 7개
  항목.
- Conversation Layer(근거 문서 어디에도 정의되지 않은 개념 — 새로
  정의하지 않는다).
- Engine Caller 위치(`ADC-0010`), ADC-01·ADC-02·ADC-07(`docs/decisions/adc/ADC.md`,
  전부 Open 유지).
- Workflow Adapter 트랙(`ADC-0019`~`ADC-0026`).
- §14 Kernel Public Contract의 실제 확정(함수 시그니처, Port 코드).
- `CONSTITUTION.md`·`BASELINE.md`·`IMPLEMENTATION_RULES.md` 파일의
  실제 수정 — 방향만 제시했다(§Baseline/Rules 반영 범위).
- Production Code(`core/`, `hqs/`, `dashboard/`, `projects/`) 수정 —
  Experimental Implementation조차 이 ADC로 열리지 않는다(§Q7,
  §Decision "구현 착수 선행조건" 4).
- OmniRoute의 실제 설치·연결·설정.

## Risks

- **Vendor 특정 위험**: OmniRoute를 "목표 구현 후보"로 명명하는 것
  자체가, 다른 후보를 충분히 비교하지 않은 채 사실상 유일한 방향으로
  굳어질 위험이 있다 — §Decision Boundary(Reversibility)가 이 위험을
  완화하지만 완전히 제거하지는 않는다. 후속 ADR/구현 단계는 대체
  구현체 가능성을 계속 열어 둬야 한다.
- **선행조건 미충족 상태에서의 사실상 착수 압력**: "목표 후보 지정"이
  라는 표현이 실무에서 "이미 채택이 끝났다"는 신호로 오독되어,
  §Decision의 선행조건 1~4를 건너뛰고 구현이 시작될 위험이 있다 —
  이 Risk는 §Q7·§Decision에서 명시적으로 차단했지만, 문서 밖에서
  일어나는 실무 판단까지 강제할 수는 없다.
- **FAIL 항목이 구조적 결함일 가능성**: `priority`·`domain_fallback_chains`·
  `routing_decisions` FAIL이 이 세션의 설정 오류가 아니라 OmniRoute
  자체의 구조적 한계라면, 선행조건 2번("재해소")이 영구히 충족되지
  않을 수 있다 — 이 경우 §Decision은 사실상 무기한 보류 상태로
  남는다. 이는 결함이 아니라 의도된 설계다(Evidence 없이 강제로
  진행하지 않는다).
- **RT-0001 연쇄 파급**: 이 Decision이 실제 구현(선행조건 충족 이후)
  으로 이어지면, 그 구현 자체가 `RT-0001` Candidate 2("Engine 수
  ≥ 2")를 충족시키는 사건이 된다 — 이는 `ADC-0010` C1(Kernel Engine
  Port/Adapter)이 나열한 선행조건 중 하나("Engine 수 ≥2")를 충족시켜
  C1 재판단의 문을 열 수 있다는 뜻이다. 이 ADC는 그 재판단을 수행하지
  않지만, 후속 ADR·구현 단계는 이 연쇄를 인지하고 별도로 다뤄야 한다.
- **ADC-07과의 경계 흐림**: "Cost/Budget Policy"를 Jarvis OS 책임으로
  명명한 것이, ADC-07(Token 예산 이중 소속, Open)이 이미 답을 찾은
  것처럼 오독될 위험이 있다 — §목적·§Q5에서 명시적으로 구분했으나,
  후속 ADR은 이 이름이 ADC-07의 Scheduler/Policy 논쟁을 대신
  해결하지 않는다는 것을 다시 한번 명시해야 한다.
- **실계정 보호·Audit 영속성**(RFC-0023 §7에서 이미 식별): 이 ADC로
  달라지지 않는다 — 선행조건 1(Evidence 영속화)이 충족되는 시점에
  함께 확인돼야 한다.

**재검토 조건**: 선행조건 1~4 중 하나라도 충족되지 않는 상태가
장기화되면, 이 Decision은 `ADC-0008`·`ADC-0010`이 반복해 온 대로
"Not Accepted (based on current evidence)"로 재분류하는 것을
검토한다 — Conditional Accept가 사실상 영구 보류라면 그 상태를
정직하게 재명명하는 것이 `CONSTITUTION.md` Evidence Review 원칙에
더 부합한다.

## Next Step

**ADR Required — 그러나 즉시 착수 대상은 아니다.**

1. §Decision "구현 착수 선행조건" 1~3(Evidence 영속화, FAIL 3건
   재해소 또는 Responsibility 재설계, `domain_budgets` 확정)이 실제로
   충족되는지 먼저 확인한다 — 이 확인 자체는 새 Observation/Evidence
   Review 대상이며 이 ADC의 범위 밖이다.
2. 충족되면, ADR을 작성해 §Baseline/Rules 반영 범위에 제시한 방향으로
   `CONSTITUTION.md`·`BASELINE.md` §14.1·§16.2·`IMPLEMENTATION_RULES.md`
   를 Scoped 갱신한다.
3. 선행조건 4(`IMPLEMENTATION_RULES.md` Scoped 완화)가 그 ADR로
   완료된 뒤에만 Experimental Implementation(`projects/` 격리 환경,
   `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` 조건)을 검토할 수
   있다 — 이 ADC·그 ADR 어느 것도 Production 구현을 직접 승인하지
   않는다.
4. Vendor 특정 위험(§Risks)을 완화하기 위해, 후속 ADR/구현 계획은
   OmniRoute 외 대체 구현체 가능성을 명시적으로 열어 두는 문구를
   포함하는 것을 권고한다.
5. RT-0001 연쇄(§Risks)를 후속 ADR/구현 지침에 명시적으로 기록한다.

## Governance Chain 검증

`RFC-0023`(Proposed — Freeze 유지/부분 해제/재검토 보류 비교, Decision
아님) → 이 ADC(Accept, Conditional·Scoped — OmniRoute를 목표 후보로
지정, Responsibility 방향 제시, Production은 선행조건까지 차단) →
후속 ADR(예정 — 선행조건 충족 확인 후 Baseline·Rules 반영). RFC-0023
§9가 위임한 5개 질문(재검토 착수 여부, Option 선택, 영속화 선행조건,
Escalate 응답, 절차적 해석의 타당성) 전부를 이 ADC가 §Q1~§Q6에서
답했다. RFC-0023의 Out of Scope(Multi-Agent Runtime, Engine Caller
위치, Contract 확정, 구현 착수, Workflow Adapter 트랙)를 이 ADC도
하나도 건드리지 않았음을 §Out of Scope에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. §16.2 Execution
  Layer의 기존 경계 안에서 구현 후보를 지정했을 뿐, 새 Layer·책임을
  추가하지 않았다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
  "Provider Governance"·"Routing Policy" 등은 §6 Concept Model에
  즉시 등재되지 않았다 — 방향 제시일 뿐이며 분류는 후속 ADR의 몫이다.
- Contract Change — **없음**. §14 Kernel Public Contract를 확정하지
  않았다(§목적, §Q5).
- Baseline·`CONSTITUTION.md`·`IMPLEMENTATION_RULES.md` 문서를 이
  ADC가 변경했는가 — **아니오**. 방향·제안만 했다(§Baseline/Rules
  반영 범위).
- `docs/decisions/adc/ADC.md`(ADC-01·ADC-02·ADC-07)를 변경했는가 —
  **아니오**.
- Multi-Agent Runtime Freeze를 침범했는가 — **아니오**(§Scope,
  §Out of Scope에서 명시적으로 배제).
- Production 구현을 승인했는가 — **아니오**. Experimental
  Implementation조차 이 ADC로 열리지 않는다(§Q7, §Decision 선행조건
  4).
- 검증되지 않은 OmniRoute 기능을 과장했는가 — **아니오**. FAIL
  3건·UNVERIFIED 1건 어느 것도 채택 근거로 쓰지 않았고(§Q4), 오히려
  구현 착수를 막는 조건으로 전환했다(§Decision).
- ADR이 필요한가 — **예**(§Next Step), 단 즉시 착수 대상은 아니다.

## Self Review

- RFC-0023의 Required Decision과 일치하는가 — **Pass**. §9의 5개
  항목 전부를 §Q1~§Q6에서 각각 답했다(대응: 항목5=Q1, 항목1=Q2,
  항목4=Q3, 항목2=Q5, 항목3=Q6).
- 기존 `CONSTITUTION.md`/`BASELINE.md`/Governance 규칙을
  위반했는가 — **아니오**. Evidence Review 원칙(FAIL/UNVERIFIED를
  근거로 쓰지 않음), Frozen Boundary 우회 금지(Experimental조차
  차단), RFC → ADC → ADR 절차(문서 수정을 ADR로 위임) 모두 준수했다.
- OmniRoute의 검증되지 않은 기능을 과장했는가 — **아니오**. §Q4·
  §Decision Evidence에서 FAIL 3건·UNVERIFIED 1건을 채택 근거에서
  명시적으로 제외했고, 오히려 선행조건으로 전환했다.
- Architecture/Contract 변경 범위가 최소한인가 — **Pass**. Model
  Routing/Engine Adapter 두 항목에 한정했고, §14 Contract는 확정하지
  않았으며, 실제 파일 수정은 전혀 하지 않았다(방향만 제시).
- Multi-Agent Runtime Freeze를 침범했는가 — **아니오**(§Scope에서
  명시적으로 배제, Freeze 목록 나머지 7개 항목 무변경).
- "채택"을 무조건적으로 확정했는가 — **아니오**. Decision 표제 자체가
  "Conditional, Scoped"이며, 구현 착수 선행조건 4개가 전부 충족되기
  전까지 어떤 구현도 승인하지 않는다.
- Evidence만 사용했는가 — **Pass**. RFC-0023과 그것이 인용한 문서만
  대조했다. 새 실험은 수행하지 않았다.
- 코드/Baseline/Freeze 문서를 직접 수정했는가 — **아니오**. 이 ADC
  파일 외 어떤 파일도 생성·수정하지 않았다.
