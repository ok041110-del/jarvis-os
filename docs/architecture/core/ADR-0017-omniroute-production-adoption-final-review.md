# ADR-0017: OmniRoute Production Adoption — Final Adoption Review, Responsibility Boundary 확정, Baseline 갱신

## Amendment (후속 세션) — §6.2 "Case A 밖으로의 전환을 승인하지 않는다" 범위 명확화

**이 Amendment는 아래 원본을 삭제·수정하지 않는다.**
`docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`가
ChatGPT/Claude Code 2-Engine Multi-Engine Architecture를 별도의 독립된
RFC → ADC → ADR 절차로 승인했다. 이 Amendment는 그 승인이 아래 §6.2·
§9의 어떤 문장과도 실제로 충돌하지 않음을 명시한다.

- §6.2 "Case A 밖(Case B/C)으로의 전환을 승인하지 않는다"는 **OmniRoute
  Thin Engine Caller 트랙 자신**(이 ADR이 다루는 대상)에 대한 문장이다
  — OmniRoute 호출 방식이 Case A(단일 함수, Jarvis 코드에 Policy
  판정 로직 없음)를 벗어나 Case B/C로 전이하는 것을 이 ADR이 승인하지
  않는다는 뜻이었다. `ADR-0024`는 OmniRoute의 호출 방식을 전혀
  바꾸지 않았다 — `omniroute_engine.py`는 무수정이며 여전히 Case A
  그대로다. 따라서 이 문장은 여전히 유효하고, `ADR-0024`와 충돌하지
  않는다.
- `ADR-0024`가 실제로 발동시킨 것은 이 ADR의 대상이 아니라
  `RT-0001` Candidate 2(Engine Gateway, "Engine 수 ≥ 2")다 — 이는
  §4 표가 "충돌 없음"으로 판정했던 **당시 상태**(Engine 수=1)에 대한
  판정이었지, "Engine 수가 앞으로 영원히 1이어야 한다"는 별도의
  독립적 금지를 이 ADR이 선언한 것이 아니다. `RT-0001` 자신의 문서
  구조(Trigger 충족 시 재검토)가 애초에 그 가능성을 열어 두고 있었다.
- 결론: 이 ADR의 OmniRoute Adoption 결정(§6.1)과 Responsibility
  Boundary 확정(§2)은 **무변경으로 유효**하다. `ADR-0024`는 이 ADR을
  뒤집지 않고, `RT-0001` Candidate 2의 재검토를 별도로 수행했을 뿐이다.

---

## 원본

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0017` |
| 제목 | `ADR-0016` §9·§12가 남긴 "실제 구현을 향해 남은 3단계" 중 3단계(Final Adoption Review)를 수행하고, `ADC-0031` §Out of Scope의 Policy 소재 질문에 답하며, `BASELINE.md` §14.1·§16.2를 최소 범위로 갱신한다 |
| 상태 | **Accepted — Production Adoption 선언(Scoped: OmniRoute Thin Engine Caller 형태에 한정)** — 판정 근거는 §5 Gate 표 참조 |
| Context | `RFC-0023` → `ADC-0027`~`ADC-0031` → `ADR-0015`(Consolidation)→`ADR-0016`(Freeze Scoped 완화)→`EVIDENCE-0001`~`EVIDENCE-0005`(실제 구현·검증, 27/27 PASS) |
| 관련 RFC | `RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` |
| 관련 ADC | `ADC-0027`, `ADC-0028`, `ADC-0029`, `ADC-0030`, `ADC-0031` |
| 관련 ADR | `ADR-0015`, `ADR-0016` |
| 관련 Evidence | `EVIDENCE-0001`~`EVIDENCE-0005` |
| 선행 Decision(참고, 뒤집지 않음) | `docs/governance/adc/ADC-0003.md` 판단4(여전히 Open), `docs/decisions/adc/ADC.md` ADC-01·ADC-02·ADC-07(여전히 Open), `ADC-0010`(Engine Caller 위치, 전부 Not Accepted, 재검토 없음), `RT-0001` Candidate 2(미충족, 재검토 없음) |

이 ADR은 `ADC-0027`~`ADC-0031`이 이미 내린 Decision을 **다시 논의하지
않는다.** §2의 Responsibility Boundary 확정은 새로운 Architecture
Decision이 아니라, `ADC-0031`이 이미 확정한 Case A 정의(§Q1)의 **논리적
필연**을 명시적으로 서술하는 것이다(§2.1에서 그 필연 관계를 증명한다).

---

## 1. Context

작성 전 `hqs/development/CONSTITUTION.md`, `docs/architecture/baseline/
BASELINE.md` §14.1·§16.2, `hqs/development/IMPLEMENTATION_RULES.md`,
`docs/architecture/core/RT-0001`(`docs/governance/rt/RT-0001.md`),
`ADC-0010-engine-caller-location-boundary.md`, `ADC-0027`~`ADC-0031`,
`ADR-0015`~`ADR-0016`, `EVIDENCE-0001`~`EVIDENCE-0005`,
`projects/omniroute-thin-engine-caller-v1/`(코드·테스트 27개)를
재확인했다.

`ADR-0016` §9·§12는 실제 구현을 향한 3단계를 정의했다.

| 단계 | `ADR-0016` 시점 | 이 ADR 시점 |
|---|---|---|
| 1. Thin Engine Caller 실제 구현 | 미착수 | 완료(`EVIDENCE-0004`/`0005`가 확인) |
| 2. 실제 Integration Validation | 미착수 | 완료(`EVIDENCE-0003`/`0004`/`0005`, 27/27) |
| 3. Final Adoption Review | 미착수 | **이 ADR이 수행한다** |

`EVIDENCE-0005` §3은 이 트랙에 남은 항목을 CLOSED/BY-DESIGN/
GOVERNANCE-REQUIRED로 분류했고, GOVERNANCE-REQUIRED 3건(#12 Policy
소재, #13 `BASELINE.md` 실제 갱신, #14 Final Adoption Review 공식
선언)을 "Architecture Decision이 필요해 Evidence 문서가 손대지 않은
항목"으로 명시적으로 남겼다. 이 ADR은 그 3건에 답한다.

---

## 2. Responsibility Boundary 확정 — Routing Policy / Cost·Budget Policy / Audit Policy 소재

### 2.1 이것이 새 Decision이 아니라 기존 Decision의 필연인 이유

`ADC-0031` §Q1은 Case A(Thin Engine Caller)의 조건을 이미 정의했다.

> (a) Jarvis의 Engine Adapter가 일반화된 Port/Adapter 인터페이스가
> 아니라 **단일 함수** 형태를 유지하고, (b) `ADC-0027`이 Jarvis OS
> 책임으로 명명한 "Routing Policy"·"Cost/Budget Policy"·"Audit
> Policy"·"API Key Scope(정책 결정)"에 해당하는 **판정 로직을 Jarvis
> 코드 자체에 두지 않을 때**에만 이 확인이 적용된다.

즉 (b) 조건 자체가 "Jarvis 코드에 이 네 가지 Policy 판정 로직이
있으면 Case A가 아니다"라고 이미 못 박아 뒀다. `ADR-0016`은
`CONSTITUTION.md` Freeze Scoped 예외를 **Case A 형태로 한정**했다
(`ADC-0031` §Q1 두 조건). 따라서:

> **현재의 Freeze Scoped 예외가 적용되는 한(=Jarvis의 구현이 Case A로
> 남아 있는 한), Routing Policy·Cost/Budget Policy·Audit
> Policy·API Key Scope(정책 결정)는 정의상 Jarvis 코드에 존재할 수
> 없다.**

이것은 새로운 선택이 아니라 이미 Accept된 조건(a)·(b)에서 논리적으로
도출되는 결과다 — 이 ADR이 "정책적으로" 고른 것이 아니다.

### 2.2 실증 확인

`projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py`
(8개, 27/27 스위트의 일부, `EVIDENCE-0004`/`0005`가 매 회귀마다
재확인)가 이를 코드 수준에서 실증한다 — `caller.py`에는 provider
선택·model scoring·routing·fallback·multi-provider orchestration·
Policy 판정 로직이 **0줄** 존재한다. 이 실증이 없었다면 아래 결정은
근거 없는 선언이 되었을 것이다.

### 2.3 결정 — 각 Policy의 실제 소재

| Policy | 현재 소재(Case A가 유지되는 한) | 근거 |
|---|---|---|
| **Routing Policy**(우선순위·fallback 규칙) | **OmniRoute 자체 설정**(대시보드/`key_value` 설정 — `blockedProviders`, family selector, `provider_connections.priority` 등) | `ADC-0031` 금지 목록("Jarvis 내부 routing 로직", "`priority`를 Jarvis 코드에서 직접 적용" 금지), `EVIDENCE-0003`§2·§4, `EVIDENCE-0004`§4가 실제로 이 설정 경로만 사용해 검증했다 |
| **Cost/Budget Policy**(예산 한도) | **OmniRoute 자체 설정**(`domain_budgets` 테이블, 운영자가 설정) | Jarvis 코드(`caller.py`)는 예산 값을 읽거나 쓰지 않는다(`EVIDENCE-0002`/`EVIDENCE-0004`§3 — Jarvis는 결과로 오는 HTTP 429만 타입 있는 예외로 옮길 뿐이다) |
| **Audit Policy**(라우팅 결과 감사) | **미실현 — Deferred**(어느 쪽에도 없음) | `ADC-0029`가 이미 확인한 대로 `routing_decisions`는 OmniRoute 쪽에서도 dead code다(score/factors durable 부재). Jarvis 쪽에도 이를 대신하는 감사 로직이 없다 — **이 ADR은 이 공백을 메우지 않는다**(§8 지시 준수, 새 코드 없음). 명시적 Audit 요구사항이 실제로 발생하면 그 시점에 별도 Architecture Decision이 필요하다 |
| **API Key Scope**(정책 결정 측) | **OmniRoute 자체 설정**(`REQUIRE_API_KEY` feature flag 등) | `EVIDENCE-0003`§1과 동일 판단 유지 — Jarvis는 이 값을 설정하거나 판정하지 않는다 |

### 2.4 이 결정의 조건부 성격(Reversibility와 동일 원칙)

이 소재 확정은 **Case A가 유지되는 동안에만** 유효하다. 향후 실제
caller가 이 네 Policy 중 하나라도 Jarvis 코드 안에 판정 로직으로
가져오면, 그 순간 `ADC-0031` §Q1 조건 (b)가 깨져 Case B로 전환되고,
이 결정도 함께 무효화되며 `IMPLEMENTATION_RULES.md`의 금지 표가 그
구현에 다시 전면 적용된다(`ADC-0031` §Decision Rationale, `ADR-0016`
§5 Reversibility와 동일 구조). **이 ADR은 그 전환을 승인하지
않는다** — Case A 밖으로 나가는 것은 별도의 새 Architecture Decision
대상이다.

---

## 3. Final Adoption Review

`ADR-0015` §5·`ADR-0016` §9가 정의한 3단계를 종합한다.

### 3.1 구현·검증 종합

- **구현**: `projects/omniroute-thin-engine-caller-v1/caller.py` —
  단일 파일, 외부 의존성 없음(stdlib만), `call_omniroute()`(동기)·
  `call_omniroute_async()`+`OmniRouteCallHandle`(비동기, 상태 조회·
  취소).
- **Case A 정적 검증**: `test_case_a_boundary.py` 8개 — 단일 파일
  구성, 두 번째 Engine hardcode 없음, provider/routing 선택 로직
  없음, 일반화된 Gateway/Adapter 추상화 없음, `hqs/development/mvp/
  engine.py::call_engine()` 미참조, `hqs/` production path 무연결,
  독립 import 가능. 전부 PASS.
- **단위/lifecycle 검증(로컬 test double)**: `test_caller_unit.py`
  13개, `test_caller_lifecycle.py` 5개 — 요청/응답 변환, 오류 코드
  → 타입 예외 매핑(401/403/429/5xx/4xx/timeout/connection),
  비동기 상태 전이·취소. 전부 PASS.
- **실제(격리) OmniRoute 서버를 통한 검증**(`EVIDENCE-0004`/`0005`):
  - 성공 응답: `caller.call_omniroute()`로 실제 서버(→ 로컬
    `ollama-local` double) 호출, 정확한 응답 파싱 확인.
  - 오류 매핑: 업스트림 HTTP 500 → `OmniRouteProviderError`.
  - Cancellation: `call_omniroute_async()` + `.cancel()` → 상태
    `cancelled`, `OmniRouteCancelledError`.
  - `domain_budgets` pre-dispatch 차단: 실제 HTTP 429(`rate_limit_
    exceeded`), 서버 로그에 dispatch 흔적(`ProxyEgress`/`Auto
    selection:`) 0건. 근본 원인(health-check-repair)까지 확정,
    재현 가능한 자동화 회귀 테스트(`test_real_engine_budget_block.py`)
    로 고정, 2회 독립 재현 PASS.
  - `blockedProviders`: read-only endpoint(`/api/v1/auto-combo/
    auto/candidates`)로 13→0 candidate 확인, egress 위험 없이 검증.
  - 실제 provider 요금/외부 egress: **0건**(모든 dispatch 대상은
    로컬 stdlib 서버).
- **회귀**: `python3 -m pytest projects/omniroute-thin-engine-caller-v1/
  tests/ -v`(이중 게이트 설정) → **27 passed**(`EVIDENCE-0005`§5·§7).

### 3.2 Responsibility가 실제로 지켜지는지 확인

`ADC-0027` §Q5 PDP/PEP 표와 `ADC-0031` §Responsibility Boundary가
정의한 분담이 **실제 코드에서** 지켜지는지가 Final Adoption Review의
핵심 질문이다.

| 분담 | 정의(`ADC-0027`/`ADC-0031`) | 실제 확인 |
|---|---|---|
| Jarvis: 단일 함수 호출 + request/response 변환 + lifecycle | Case A | `caller.py` 전체가 이 범위 안(§3.1, `test_case_a_boundary.py`) |
| Jarvis: Policy 판정 로직 없음 | Case A 조건(b) | 확인됨(§2.2) — 0줄 |
| OmniRoute: Model Routing/Provider selection/Call/Fallback/Egress 실행 | PEP | 실제 서버가 이 전부를 수행하는 것을 `EVIDENCE-0004`§5가 관찰(성공/오류/취소 3종 모두 OmniRoute 내부 dispatch 코드를 통과) |
| OmniRoute: Cost/Budget 판정·차단 | PEP(§2.3) | `EVIDENCE-0004`§3.3 — 429 pre-dispatch 차단 실제 확인 |

**결론**: `ADC-0027`이 목표로 제시했던 PDP/PEP 분담이, 실제 구현된
Thin Caller와 실제(격리) OmniRoute 서버 사이에서 **관찰 가능한 형태로
성립한다.**

---

## 4. 기존 Governance 규칙과의 충돌 최종 검토

| 대상 | 충돌 여부 | 근거 |
|---|---|---|
| `CONSTITUTION.md` Architecture Freeze(9개 항목) | **없음** | Scoped 예외(`ADR-0016`)가 이미 Engine Adapter·Model Routing 두 항목만, Thin Caller 형태에 한정해 해제했다. 나머지 7개 항목·이 두 항목의 Case A 밖 범위는 여전히 동결 — 이번 ADR도 그대로 유지 |
| `IMPLEMENTATION_RULES.md` 15·16·17·21행(금지 표) | **없음** | `ADC-0031`이 이미 확인, `ADR-0016`이 "범위 확인" 절로 반영. 이 ADR은 그 문구를 전혀 수정하지 않는다 |
| Engine Adapter Contract(§14, `BASELINE.md`) | **없음** | §14.1 표의 "Engine 호출 책임" 행만 상태 갱신(§7) — 함수 시그니처·Port 인터페이스·새 Public Responsibility/Guarantee는 추가하지 않는다. §14.2~§14.7 어디도 수정하지 않는다 |
| `RT-0001` Candidate 2(Engine Gateway, "Engine 수 ≥ 2") | **없음** | Trigger는 "`call_engine()` 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로 하게 됨"으로 명시적으로 좁혀져 있다(`RT-0001` 원문). `caller.py`는 `call_engine()`을 import/호출하지 않고 `hqs/development/`에서 참조되지 않는다(`test_case_a_boundary.py`가 이번에도 재확인) — Trigger 미충족 유지. `EVIDENCE-0003`§8·`EVIDENCE-0004`§8의 판단을 재확인했다 |
| `ADC-0010`(Engine Caller 위치, C1~C6 전부 Not Accepted) | **없음** | C1(Kernel Engine Port/Adapter) 재검토 선행조건은 "Kernel Module Defer 3건, ADC-01·02, Engine 수 ≥2"의 **결합**이다(`ADC-0010`§부족한 Evidence 1). `Engine 수 ≥2`가 미충족(위 RT-0001 확인)인 이상 이 결합 자체가 성립하지 않는다 — C1 재검토 문이 열리지 않는다. 이 ADR은 `ADC-0010`을 재론하지 않는다 |
| `ADC-01`(Model↔Component)·`ADC-02`(Runtime 존폐)·`docs/governance/adc/ADC-0003.md` 판단4(Multi-Model) | **없음(무관)** | 이 트랙(`RFC-0023`~)이 시작부터 명시적으로 범위 밖으로 뒀다(`ADC-0027`§목적) — 이 ADR도 재론하지 않는다. 전부 Open 상태 유지 |
| `ADC-0028`/`ADC-0029`/`ADC-0030`(`domain_fallback_chains`/`routing_decisions`/`priority`) | **없음** | 이 ADR은 세 문서의 Decision을 재론하지 않는다. §2.3 Audit Policy "Deferred" 판정은 `ADC-0029`의 기존 판단과 정합적이다(새 결론 아님, 재확인) |

**종합**: 이 ADR의 어떤 결정도 기존 Governance 규칙과 충돌하지
않는다. §2·§7이 확정/갱신하는 내용은 전부 기존 Decision(`ADC-0027`/
`ADC-0031`/`ADR-0016`)의 명시적 위임 또는 논리적 필연이다.

---

## 5. Adoption Gate — 최종 PASS/FAIL/UNVERIFIED 판정

| # | Gate | 판정 | Evidence |
|---|---|---|---|
| 1 | Evidence 영속화 | **PASS** | `EVIDENCE-0001`~`EVIDENCE-0005` |
| 2 | `priority`/`domain_fallback_chains`/`routing_decisions` FAIL 3건 재해소 | **PASS**(Responsibility redesign) | `ADC-0028`·`ADC-0029`·`ADC-0030` |
| 3 | `domain_budgets` 확정(초과 시 실제 차단) | **PASS** | `EVIDENCE-0002`(최초 실행 확인), `EVIDENCE-0004`§3(근본 원인 확정, 재기동-안전 재현), `EVIDENCE-0005`§5(자동화 회귀 테스트로 고정, 2회 재현) |
| 4 | `IMPLEMENTATION_RULES.md` Scoped 완화(문서 반영) | **PASS** | `ADR-0016`§8 |
| 5 | Thin Engine Caller 실제 구현 | **PASS** | `projects/omniroute-thin-engine-caller-v1/caller.py` |
| 6 | Case A 경계 실증(단일 함수, Policy 로직 0줄) | **PASS** | `test_case_a_boundary.py` 8개, 27/27의 일부 |
| 7 | 실제 Engine 성공/오류/cancellation lifecycle | **PASS** | `EVIDENCE-0004`§5, `EVIDENCE-0005`§7(회귀 재확인) |
| 8 | zero-config egress 방어(`blockedProviders`/`REQUIRE_API_KEY`) | **PASS** | `EVIDENCE-0003`§1·§2·§4, `EVIDENCE-0004`§4, `EVIDENCE-0005`§6(read-only 드리프트 없음 재확인) |
| 9 | Responsibility Boundary(Policy 소재) 확정 | **PASS** | 이 ADR §2 |
| 10 | Architecture Freeze/Contract/RT-0001/ADC-0010 충돌 | **PASS**(충돌 없음) | 이 ADR §4 |
| 11 | 실제 Production 배포·`engine.py` 교체 검증 | **UNVERIFIED**(범위 밖) | §6.2에서 명시 — 이 ADR이 판정할 대상이 아니다 |

**11번은 "미충족"이 아니라 "이 Gate 목록에 속하지 않는 별개 단계"다**
— `ADC-0027`~`ADR-0016`이 정의한 Production Adoption Gate(1~10)는
"Architecture/Governance 차원에서 OmniRoute를 Thin Caller 형태로
채택해도 되는가"를 판정하는 것이며, "실제 `hqs/development/mvp/
engine.py`를 교체해 서비스에 배포하는가"는 그 채택 이후의 **별개
구현 작업**이다(§6.2).

**10개 중 10개 PASS. UNVERIFIED 1건은 애초에 이 Gate 목록의 대상이
아니다.**

---

## 6. Decision

### 6.1 Production Adoption 선언

**Accept — OmniRoute를 Jarvis OS의 Model Routing / Engine Adapter
(Execution Layer 내부 구조, `BASELINE.md` §16.2) Implementation
Engine으로 Production Adoption한다. 단, 이 Adoption은 OmniRoute
Thin Engine Caller(Case A, `ADC-0031` §Q1) 형태에 한정된다.**

Gate 10개 전부 PASS(§5)이므로, `ADC-0027` §Decision "구현 착수
선행조건" 4개와 `ADR-0015`/`ADR-0016`이 정의한 "실제 구현을 향한
3단계"가 모두 충족되었다고 판정한다.

### 6.2 이 선언이 하지 않는 것(과장 방지, 반드시 함께 읽을 것)

- **`hqs/development/mvp/engine.py`를 교체하거나 실제 서비스
  트래픽에 OmniRoute를 연결하지 않는다.** 이 ADR은 문서(이 ADR
  자신 + `BASELINE.md` §14.1·§16.2 최소 갱신) 외 어떤 코드·설정도
  변경하지 않는다(§9). 실제 production 배포는 별도의 구현 작업
  (코드 변경, 테스트, PR)이며, 이 ADR은 그 작업이 **Architecture/
  Governance 차원에서 이제 허용된다**는 것만 확정한다.
- Case A 밖(Case B/C)으로의 전환을 승인하지 않는다(§2.4).
- Engine Gateway·Jarvis 자체 Routing/Fallback/Policy 로직을 허용하지
  않는다 — `IMPLEMENTATION_RULES.md` 금지 표는 Case A 범위 밖에서
  그대로 유효하다.
- `ADC-0010`(Engine Caller 위치)·`RT-0001` Candidate 2 재검토를
  촉발하지 않는다(§4에서 확인).
- `ADC-01`·`ADC-02`·`docs/governance/adc/ADC-0003.md` 판단4를
  재판단하지 않는다 — 전부 Open 상태 그대로.
- Audit Policy 공백(§2.3)을 메우지 않는다 — 명시적 요구사항이
  생기면 별도 Architecture Decision 대상이다.
- OmniRoute 외 대체 Implementation Engine 가능성을 닫지 않는다
  (`ADC-0027` §Risks Vendor 특정 위험, Reversibility 원칙 유지).

---

## 7. Baseline 실제 반영

### 7.1 `docs/architecture/baseline/BASELINE.md` §14.1

표의 "3. Engine 호출 책임" 행 상태를 "미결"에서 "부분 진전"으로
갱신한다(§7.3 실제 diff). Kernel Public Contract(§14) 자체 — 함수
시그니처, Port 인터페이스 — 는 여전히 정의하지 않는다. 표의 나머지
7개 행은 무변경.

### 7.2 `docs/architecture/baseline/BASELINE.md` §16.2

"이 Accept가 결정하지 않는 것" 문단에, OmniRoute Thin Engine Caller
Adoption이 부분 진전됐다는 문장을 추가한다(§7.3 실제 diff).
ADC-01·ADC-02·`ADC-0003` 판단4가 여전히 Open이라는 기존 문장은
그대로 유지한다.

### 7.3 실제 diff

*(아래 파일 수정으로 실제 반영했다 — §12 Self Review에서 diff 결과를
대조한다.)*

---

## 8. Reversibility

`ADC-0027`/`ADC-0031`/`ADR-0016`의 Reversibility 원칙을 그대로
유지한다 — OmniRoute의 내부 구현이 바뀌거나 다른 구현체로
교체되더라도 Jarvis OS Kernel·HQ 코드는 한 줄도 수정되지 않아야
하며, OmniRoute 고유 문법·설정 형식을 Kernel·HQ가 알아서는 안 된다.
§2가 확정한 Policy 소재(OmniRoute 설정)도 이 원칙 위에 있다 —
OmniRoute의 설정 스키마가 바뀌어도 Jarvis 코드는 그 스키마를 몰라야
한다(현재 `caller.py`는 실제로 어떤 OmniRoute 설정 테이블도 참조하지
않는다, §2.2).

---

## 9. Governance Constraints / Implementation Boundary

이 ADR이 하지 않는 것.

- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0016`, `EVIDENCE-0001`~
  `EVIDENCE-0005` 파일의 수정 — 전부 무변경.
- `hqs/development/CONSTITUTION.md`·`hqs/development/
  IMPLEMENTATION_RULES.md`·`docs/00_governance/
  ARCHITECTURE_GOVERNANCE.md`의 수정 — **없음**(이미 `ADR-0016`이
  필요한 반영을 완료했다 — 추가 반영 불필요).
- `BASELINE.md` §14.1·§16.2 외 다른 절의 수정 — **없음**(§14.2~
  §14.7, §16.1, §16.3~§16.7 무변경).
- 새 Public Interface/Contract 정의 — **없음**.
- OmniRoute caller 코드, Engine Adapter 코드, API 연결, provider/
  routing configuration, dashboard 변경, `hqs/development/mvp/
  engine.py` 수정, 테스트 코드 추가/수정 — **없음**(이 ADR은 문서만
  변경한다).
- 새로운 Routing/Fallback/Gateway/Policy 판정 로직 — **없음**(§2는
  기존 코드가 이미 로직 0줄임을 확인했을 뿐, 새로 만들지 않았다).

---

## 10. Consequences

- OmniRoute Thin Engine Caller가 Jarvis OS의 Model Routing/Engine
  Adapter Implementation Engine으로 Architecture/Governance
  차원에서 공식 채택된다.
- 향후 실제 `hqs/development/mvp/engine.py` 대체·서비스 연결
  작업이 별도 구현 PR로 진행될 수 있는 근거가 마련된다 — 단 그
  구현은 Case A 조건(단일 함수, Policy 로직 0줄)을 계속 지켜야
  하며, 지키지 못하면 이 Adoption의 적용 대상에서 벗어난다(§2.4,
  §6.2).
- Audit Policy 공백, `ADC-0010`/`RT-0001` 재검토 미충족, ADC-01·
  ADC-02·`ADC-0003` 판단4 Open 상태는 이 ADR 이후에도 변경 없이
  남는다 — 이들은 이 Adoption의 전제조건이 아니었다(§4·§6.2).

---

## 11. Related RFC / ADC / ADR / Evidence

- `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`
- `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
- `docs/architecture/core/ADC-0028-domain-fallback-chains-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0029-routing-decisions-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0030-priority-precondition-responsibility-redesign.md`
- `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md`
- `docs/architecture/core/ADR-0015-omniroute-thin-engine-caller-adoption-policy.md`
- `docs/architecture/core/ADR-0016-omniroute-thin-caller-freeze-scoped-relaxation.md`
- `docs/architecture/core/EVIDENCE-0001-omniroute-precondition-verification.md`
- `docs/architecture/core/EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md`
- `docs/architecture/core/EVIDENCE-0003-omniroute-zero-config-egress-and-budget-block-static-analysis.md`
- `docs/architecture/core/EVIDENCE-0004-omniroute-domain-budgets-root-cause-and-real-dispatch-lifecycle.md`
- `docs/architecture/core/EVIDENCE-0005-omniroute-open-issue-closure-and-production-adoption-gate-final-check.md`
- `docs/governance/rt/RT-0001.md`
- `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`

## 12. Open Conditions (재분류 — 실제 미해결 항목만)

**Adoption Gate(§5)와 직접 관련된 미해결 항목: 0개.** 아래는 이
Adoption의 전제조건이 아니었던, 여전히 Open인(그리고 이 ADR이
건드리지 않는) 별개 항목이다.

1. **실제 Production 배포**(`hqs/development/mvp/engine.py` 교체 또는
   병행) — 별도 구현 작업, 미착수(§6.2).
2. **Audit Policy 공백** — `routing_decisions`의 OmniRoute 측 dead
   code 상태, Jarvis 측 명시적 요구사항 부재. 요구사항이 생기면 별도
   Architecture Decision(§2.3).
3. **`priority` tie-break 실제 dispatch 영향** — UNVERIFIED 그대로
   (`ADC-0030`, Adoption precondition 아님, 무변경).
4. **`domain_budgets` semantics 전체**(warning threshold, 기간 리셋,
   복수 API key, DB-backed key 경로) — 미검증 그대로(`EVIDENCE-0002`
   §9, Adoption precondition 아님, 무변경).
5. **`ADC-0010`(Engine Caller 위치)·`RT-0001` Candidate 2** — 미충족
   상태 유지, 이 ADR로 재검토 촉발되지 않음(§4).
6. **`ADC-01`·`ADC-02`·`docs/governance/adc/ADC-0003.md` 판단4** —
   전부 Open, 이 트랙과 무관, 재론하지 않음.

이 6개는 "이번 Adoption 결정의 미해결 전제조건"이 아니라, 애초에
이 트랙의 Scope 밖이거나(#1, #5, #6) 이미 별도 Decision으로 처리된
사항의 잔여 특성(#2, #3, #4)이다 — Gate 판정(§5)에 영향을 주지
않는다.

---

## Self Review

- `ADC-0027`~`ADC-0031`의 Decision을 뒤집었는가 — **아니오**(§1·§3·
  §4 전부 기존 Decision을 인용·종합했을 뿐이다).
- §2 Responsibility Boundary 확정이 새로운 Architecture Decision인가
  — **아니오**(§2.1 — `ADC-0031` §Q1 조건의 논리적 필연임을 증명
  했고, §2.2 실증으로 뒷받침했다).
- 새로운 Routing/Fallback/Gateway/Policy를 구현했는가 — **아니오**
  (§9 — 코드 변경 없음, `caller.py` 무수정).
- 불필요한 Architecture/Contract 변경을 추가했는가 — **아니오**
  (§9 — `BASELINE.md` §14.1·§16.2 두 곳만, 그것도 상태 서술 갱신뿐
  — 새 Public Responsibility/Guarantee/함수 시그니처 없음).
- Production Adoption 선언이 실제 배포까지 포함한다고 과장했는가 —
  **아니오**(§6.2에서 명시적으로 분리).
- Gate 판정에 근거 Evidence를 명시했는가 — **Pass**(§5 표 전체).
- Architecture Freeze/Contract/RT-0001/ADC-0010과 충돌을 확인했는가 —
  **Pass**(§4, 6개 대상 전부 "없음"으로 판정하고 각각 근거 제시).
- Open Issue를 실제 미해결 항목만 남기도록 재분류했는가 — **Pass**
  (§12 — Gate 관련 미해결 0개, 별개 6개 항목을 명시적으로 분리).
- Gate가 하나라도 미충족이면 Adoption을 선언하지 않기로 했는가 —
  해당 없음(10/10 PASS, §5·§6.1).
- `BASELINE.md` 외 다른 Governance 문서를 수정했는가 — **아니오**
  (§9).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**(별도 지시 대기).
