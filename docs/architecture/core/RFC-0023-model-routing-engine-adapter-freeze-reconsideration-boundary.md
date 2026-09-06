# RFC-0023: Model Routing / Engine Adapter Freeze — Reconsideration Boundary (OmniRoute 실측 Evidence 기반)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `hqs/development/CONSTITUTION.md` Architecture Freeze 목록 중
**Engine Adapter**·**Model Routing** 두 항목(Multi-Agent Runtime 등
목록의 다른 항목은 대상이 아니다 — §5). `docs/architecture/baseline/BASELINE.md`
§14.1 Kernel Public Contract 표 3번("Engine 호출 책임" = 미결, 계약
범위 밖)·§16.2 Execution Layer Accept("내부 구조 — Prompt 구성, Model
선택, 재시도 정책, Multi-Model Routing — 는 Open"). `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`
C4(Development HQ, Not Accepted — "Freeze 목록 자체를 재론하지 않는 한
재검토 근거가 생기지 않는다")가 열어 둔 재검토 경로. `docs/governance/adc/ADC-0003.md`
판단 4(Execution Layer Multi-Model 지원, **Out of Authority/Escalate**
— "별도 Jarvis OS 수준 RFC 상정 여부는 이 ADC의 결정 범위 밖"). `docs/governance/rt/RT-0001.md`
Candidate 2(Engine Gateway, Re-evaluation Trigger = "Engine 수 ≥ 2").

**Evidence**: OmniRoute 5라운드 실측 검증 결과(이번 세션에서 사용자가
보고 — §3 "Evidence 출처 상태" 참조), `.claude/docs/integrations/omniroute.md`,
`.claude/docs/SMOKE_TEST-2026-08-08.md` §3(2026-08-08, CLI 설치·기동
확인만), `hqs/development/CONSTITUTION.md` Architecture Freeze·Evidence
Review 원칙, `hqs/development/IMPLEMENTATION_RULES.md` 금지 표("Engine
Gateway 구현 금지", "Engine Routing 구현 금지", "Multi Engine 지원 코드
작성 금지"), `docs/architecture/baseline/BASELINE.md` §14.1·§16.2,
`docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`,
`docs/governance/adc/ADC-0003.md` 판단 4, `docs/governance/rt/RT-0001.md`
Candidate 2, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`(Architecture
Need 진입 흐름, ADC 채택 기준). 새로운 실험은 수행하지 않는다 — 이미
보고된 검증 결과와 기존 Governance 문서만 인용한다.

> 본 RFC는 Architecture Freeze를 해제하지 않는다. OmniRoute를 Jarvis
> OS의 Governance Layer로 채택하지 않으며, Routing Engine/Execution
> Layer 내부 구현 **후보**로만 다룬다(§5). Model Routing/Engine
> Adapter의 Contract를 확정하지 않는다. 검증되지 않은 OmniRoute
> 기능(`priority`, `domain_fallback_chains`, `routing_decisions`,
> `domain_budgets`)을 Contract 후보에 포함하지 않는다. 기존 Multi-Agent
> Runtime Freeze 항목을 재론하지 않는다. 기존 RFC → ADC → ADR 절차를
> 우회하지 않는다. 이 RFC가 여는 것은 좁은 질문 하나다: **"`CONSTITUTION.md`
> Architecture Freeze 목록의 Engine Adapter·Model Routing 두 항목이,
> OmniRoute 5라운드 실측 Evidence를 근거로 지금 재검토(Freeze 유지 /
> 부분 해제 / 재검토 보류 중 판단) 대상이 될 수 있는가?"**

## 0. 이 RFC가 열린 이유

`ADC-0010`은 Engine Caller 위치 후보 6개를 전수 검토하며 C4(Development
HQ)를 다음 이유로 Not Accepted로 남겼다 — *"Development HQ는 후보
검토 대상이 아니라 명시적으로 배제된 대상이다... Freeze 목록 자체를
재론하지 않는 한 재검토 근거가 생기지 않는다 — Phase 1 종료 후 불변
원칙과 충돌한다."* `GOVERNANCE-REVIEW-0003`은 C4를 동일한 사유("Freeze 목록 자체를
재론해야 함 — Phase 1 종료 후 불변 원칙과 충돌")로 재확인했고,
`GOVERNANCE-REVIEW-0004`는 이를 "사실상 Governance 경로가 막혀
있다"고 서술한다 — 다만 두 문서 모두 이 서술을 C4(Development HQ가
caller가 되는 경로) 판단의 맥락 안에서만 남겼을 뿐, "Architecture Governance 절차(RFC → ADC → ADR)로
Freeze 목록 자체를 직접 재검토하는 경로"까지 막혀 있다고 명시적으로
말한 적은 없다. **이 RFC의 해석으로는**, 이 문장의 "충돌"은
**Development HQ RFC-0005 문서 자체를 다시 여는 경로**가 Phase 1
종료 후 불변 원칙과 부딪힌다는 뜻이며, `CONSTITUTION.md`의 Architecture
Freeze 목록 자체가 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
Architecture Governance 절차로 재검토되는 것까지 막는다고 확정적으로
읽을 근거는 원문에 없다 — 그러나 이 해석 자체가 기존 문서에 명시된
사실은 아니며, 이 RFC가 스스로 내린 절차적 판단이다. 이 해석의
타당성 자체를 §9 Required Decision 항목으로 남긴다.

별도로, `docs/governance/adc/ADC-0003.md` 판단 4는 Execution Layer의
Multi-Model 지원을 Development HQ ADC의 권한 밖(Out of Authority)으로
Escalate하며 *"Multi-Model 실행 요구가 실제로 발생해도 이를 판단할
절차가 지금 당장은 지정되어 있지 않다"*는 공백을 그대로 남겼다. 이
RFC는 그 Escalate 이후 처음으로, Jarvis OS 수준에서 이 공백을 정식
Boundary Question으로 여는 시도다.

## 1. Problem / Context

`CONSTITUTION.md`는 Engine Adapter와 Model Routing을 "충분한 Evidence가
나올 때까지 동결"하는 항목으로 명시하고, *"반복된 실전 Evidence
없이는 개발하지 않는다"*는 원칙을 Core Philosophy 최상위(Architecture
< Capability < Dogfooding < Observation < Evidence)에 둔다. 이 Freeze는
지금까지 두 갈래로 확인돼 왔다 — (1) `IMPLEMENTATION_RULES.md`가
Engine Gateway·Engine Routing·Multi Engine 지원 코드 작성을 명시적으로
금지하는 구현 차원, (2) `BASELINE.md` §14.1이 "Engine 호출 책임"을
Kernel Public Contract 범위 밖 미결로 두는 설계 차원. 두 차원 모두
**Evidence 부재**를 이유로 미결 상태를 유지해 왔다.

이번 세션에서 사용자가 OmniRoute(290+ Provider/500+ Model을 단일
엔드포인트로 라우팅하는 AI Gateway, `.claude/docs/integrations/omniroute.md`)에
대해 실제 계정으로 5라운드 검증을 수행하고 그 결과를 보고했다. 이
RFC의 목적은 그 결과가 Freeze 해제를 정당화한다고 결론짓는 것이
**아니라**, Freeze를 재검토 대상으로 올릴 만큼 Evidence가 구체적인지를
Architecture Governance 절차 위에서 공식적으로 묻는 것이다.

## 2. Current Freeze — 지금 무엇이 동결되어 있는가

| 근거 문서 | 동결 내용 | 현재 상태 |
|---|---|---|
| `CONSTITUTION.md` "Architecture Freeze" | Engine Adapter, Model Routing (Multi-Agent Runtime 등 7개 항목과 함께 — Runtime, Pipeline Generalization, Task Dispatcher Generalization, Stage Runner, Event Bus, Scheduler, Multi-Agent Runtime) | 동결 유지 — 이 RFC 시점까지 변경 없음 |
| `IMPLEMENTATION_RULES.md` 금지 표 | Engine Gateway(Port/Adapter 추상화) 구현 금지, Engine Routing 구현 금지, Multi Engine 지원 코드 작성 금지 | 동결 유지 |
| `BASELINE.md` §14.1 | Kernel 책임 후보 3번 "Engine 호출 책임" = 미결, 계약 범위 밖 | 미결 유지 |
| `BASELINE.md` §16.2 | Execution Layer는 Accept됐으나 내부 구조(Model 선택, Multi-Model Routing)는 Open — ADC-01(Model↔Component 대응)·ADC-02(Runtime 존폐)·`ADC-0003` 판단 4가 각각 미해소 | Open 유지 |
| `ADC-0010` | Engine Caller 위치 6개 후보 전부 Not Accepted | 유지 — 이 RFC로 재론되지 않음(§5) |
| `RT-0001` Candidate 2 | Engine Gateway Re-evaluation Trigger = "Engine 수 ≥ 2" | **미충족** — `call_engine()`이 실제로 2개 이상의 서로 다른 Engine을 대상으로 호출된 적은 이번 Evidence에도 없다(§4) |

**정리**: Freeze는 다층 구조다 — Constitution 차원의 선언, 구현 차원의
금지, 설계 차원의 미결, 그리고 사전에 정의된 정량 Trigger(RT-0001)까지
넷이 서로 다른 층에서 동일한 결론(동결 유지)을 뒷받침해 왔다. 이 RFC가
묻는 것은 이 중 어느 층도 아직 자동으로 해제되지 않았다는 전제 위에서,
새 Evidence가 **재검토를 시작할 근거**가 되는지다.

## 3. Evidence

### 3.1 이번 세션 보고 — OmniRoute 5라운드 실측 검증

| 검증 항목 | 결과 |
|---|---|
| Provider Exclusion | **PASS** |
| API Key Scope | **PASS** |
| Egress Audit | **PASS** |
| Auto-Routing/내부 fallback 실행 | **PASS** |
| `priority` | **FAIL** |
| `domain_fallback_chains` | **FAIL** |
| `routing_decisions` | **FAIL** |
| `domain_budgets` | **UNVERIFIED** |

### 3.2 Evidence 출처 상태 — 반드시 함께 기록해야 하는 공백

`IMPLEMENTATION_RULES.md` "Dynamic Workflow 재검토 Trigger" 절의
"[Evidence 출처 상태]" 선례를 그대로 따른다 — **위 8개 항목은 이번
세션에서 사용자가 보고한 내용이며, 이 저장소 안에 그 결과를 재현
가능한 형태로 기록한 원본 로그·스크립트·출력 파일은 이 RFC 작성
시점 기준으로 존재하지 않는다**(저장소 전수 탐색 결과 미발견 —
`.claude/docs/integrations/omniroute.md`은 2026-08-08 시점 CLI 설치·
`omniroute doctor` 기동 확인만 기록했고, PASS/FAIL 세부 항목·5라운드
구성은 다루지 않는다). 이는 보고 내용이 사실이 아니라는 뜻이 아니라,
`CONSTITUTION.md` Observation Policy("Observation은 사실만 기록한다")와
Evidence Review 원칙이 요구하는 **재현 가능한 원본 Evidence**가 아직
저장소에 영속화되지 않았다는 뜻이다. 이 공백 자체를 §7 Risks·§8
Recommendation·§9 Required Decision의 선행조건으로 다룬다.

또한, `omniroute.md`가 이미 명시한 대로 OmniRoute는 **사용자 로컬
머신에서 상시 기동돼야 의미가 있는 게이트웨이**이며, 이 저장소 작업
세션(일시적 컨테이너)은 실제 연결·상시 검증을 수행할 수 없다 —
5라운드 검증이 사실이라면 그것은 이 세션 밖, 사용자의 로컬 환경에서
수행됐다는 뜻이며, 이 RFC는 그 실행 환경의 재현성·감사 가능성을
검증하지 않았다.

### 3.3 결과 해석 — PASS/FAIL/UNVERIFIED가 각각 뒷받침하는 것과 뒷받침하지 않는 것

- **PASS 4건은 성격이 서로 다르며, 뭉뚱그려 하나의 근거로 다루지
  않는다.**
  - **접근 통제·감사 3건(Provider Exclusion, API Key Scope, Egress
    Audit)**이 보고대로라면, OmniRoute가 (a) 지정된 Provider를 실제로
    배제할 수 있고, (b) API Key의 사용 범위를 스코프대로 제한하며,
    (c) 외부로 나가는 트래픽이 감사 가능하다는 것을 시사한다 — 이
    3건은 OmniRoute의 **거버넌스적 통제 속성**을 보여줄 뿐, 실제로
    2개 이상의 서로 다른 Engine이 호출됐다는 근거는 아니다.
  - **라우팅 실행 1건(Auto-Routing/내부 fallback 실행)**만이 여러
    Provider/Model 사이의 자동 선택·내부 fallback이 실제로 동작함을
    시사한다 — 이 1건이 §2 표의 "Engine 수 ≥ 2" Trigger가 기술적으로
    충족 **가능하다는 정황**과 닿아 있는 유일한 항목이다(그러나 이
    Evidence 자체가 `call_engine()` 호출 지점을 실제로 2개 Engine
    대상으로 바꾼 것은 아니다 — Trigger는 여전히 미충족, §2).
  - 즉 "PASS 4건"을 한 덩어리로 "Engine 수 ≥ 2 정황"의 근거로 인용하는
    것은 부정확하다 — 그 정황은 라우팅 실행 1건에서만 나온다.
- **FAIL 3건(`priority`, `domain_fallback_chains`, `routing_decisions`)**은
  OmniRoute가 **문서화·설정한 대로 동작하지 않는 영역이 실제로
  존재함**을 보여준다 — 이는 OmniRoute를 그대로 신뢰할 수 있는
  Governance/Routing 계층으로 다룰 근거가 **아직 없다**는 뜻이다.
- **UNVERIFIED 1건(`domain_budgets`)**은 검증되지 않았다는 사실 자체를
  Evidence로 취급한다 — Accept도 Reject도 아닌 공백으로 남긴다.

## 4. Why Reconsider Now

- `ADC-0003` 판단 4가 Escalate한 이후, Jarvis OS 수준에서 Multi-Model/
  Engine Routing 질문이 정식 RFC로 열린 적이 없다 — 이 RFC는 그
  공백을 처음으로 정식 절차 위에 올린다.
- `CONSTITUTION.md`의 재검토 조건("반복된 실전 Evidence")과 `RT-0001`의
  정량 Trigger("Engine 수 ≥ 2") 둘 다 아직 충족되지 않았다(§2) — 그러나
  `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 Architecture Need
  원칙은 *"사전에 정의된 특정 Trigger가 충족되지 않았더라도, 실제
  Architecture Need가 관찰되면 재검토를 시작할 권한을 부여한다"*고
  명시한다 — 이 RFC는 정량 Trigger 충족을 주장하지 않고, 이 원칙에
  근거해 **검토 시작**만 요청한다.
- 실제 계정을 사용한 실측 검증(§3.1)은 이 저장소가 지금까지 가진
  OmniRoute 관련 Evidence(`.claude/docs/SMOKE_TEST-2026-08-08.md`의
  CLI 설치 확인 수준) 대비 한 단계 더 나아간 종류의 관찰이다 —
  PASS/FAIL이 항목별로 갈렸다는 사실 자체가 "전부 성공"도 "전부
  실패"도 아닌, 실제 동작을 관찰한 결과라는 신호다.
- 동시에 §3.2가 기록한 대로 이 Evidence는 아직 저장소에 영속화되지
  않았다 — "지금 재검토를 시작해도 되는가"와 "지금 결정을 내려도
  되는가"는 다른 질문이며, 이 RFC는 전자만 연다(§9).

## 5. Scope / Non-Scope

### Scope

- `CONSTITUTION.md` Architecture Freeze 목록의 **Engine Adapter**·
  **Model Routing** 두 항목이 재검토 대상이 될 수 있는지 여부.
- OmniRoute를 **Routing Engine/Execution Layer 구현 후보**로만
  한정해 다룬다 — §16.2 Execution Layer("Model/Engine 선택·호출까지의
  경계")의 내부 구조 후보 하나로만 위치시킨다.

### Out of Scope

- **Jarvis OS Governance 확정** — OmniRoute를 Governance Layer,
  Policy 엔진, 또는 그에 준하는 Kernel Concept으로 다루지 않는다.
  OmniRoute가 제공하는 Provider Exclusion/API Key Scope/Egress
  Audit이 "Governance스럽게" 보이더라도, 이 RFC는 그것을 §16.1
  Governance(Accept)의 대체·확장 후보로 제안하지 않는다.
- **Multi-Agent Runtime** — `CONSTITUTION.md` Freeze 목록의 별도
  항목이며, 이 RFC의 Evidence(OmniRoute Provider/Model 라우팅
  검증)는 Multi-Agent Runtime의 존폐·구조에 대해 아무것도 말하지
  않는다. 재론하지 않는다.
- **Engine Caller 위치**(`ADC-0010`) — 이 RFC는 그 6개 후보 판단을
  다시 열지 않는다. Freeze 목록 자체의 재검토 가능 여부만 묻는다
  (§0에서 구분한 것과 동일한 원칙).
- **Contract 확정** — Model Routing/Engine Adapter의 Public
  Contract(입력·출력 시그니처, Port/Adapter 형태)를 규정하지 않는다.
  OmniRoute의 검증되지 않은 기능(`priority`, `domain_fallback_chains`,
  `routing_decisions`, `domain_budgets`)은 물론, PASS로 확인된
  기능(Provider Exclusion 등)조차 Contract 후보로 명명하지 않는다 —
  Accept되더라도 그 작업은 후속 ADC/ADR의 몫이다(§10).
- **구현 착수** — `IMPLEMENTATION_RULES.md`의 Engine Gateway/Engine
  Routing/Multi Engine 금지는 이 RFC로 해제되지 않는다.
- **Workflow Adapter 관련 트랙(`ADC-0019`~`ADC-0023`, `ADR-0009`)과의
  혼동 방지** — 그 트랙은 §16.6 Workflow 그래프 실행(State/Node/
  Conditional Edge/Loop/Checkpoint) 책임을 다루며, 이 RFC가 다루는
  §16.2 Engine Adapter(Model/LLM Provider 호출)와는 `GLOSSARY.md`가
  이미 명시한 대로 별개의 seam이다. 이 RFC는 Workflow Adapter
  Contract·Gate (A)/(B)/(C) 진행 상태에 어떤 영향도 주지 않는다.

### Non-goals

- OmniRoute 채택을 전제하지 않는다 — Accept되더라도 후속 ADC는
  OmniRoute 대신 다른 구현체(또는 현행 단일 Engine 직접 호출 유지)를
  선택할 자유가 있다.
- "Freeze 해제가 필요하다"를 전제하지 않는다 — §6이 Freeze 유지를
  포함한 세 선택지를 동등하게 비교한다.
- Governance v2 Rule B(3건 이상 독립 관찰) 충족을 주장하지 않는다 —
  Evidence는 이번 세션 보고 1건이며, 그마저 §3.2가 기록한 영속화
  공백을 안고 있다.

## 6. Options

| 옵션 | 내용 | 근거가 되는 조건 | 이 RFC의 판단 |
|---|---|---|---|
| **A. Freeze 유지** | Engine Adapter·Model Routing을 계속 동결한다. OmniRoute Evidence를 참고 기록으로만 남긴다 | §3.2 영속화 공백 미해소, `RT-0001` Trigger("Engine 수 ≥ 2") 미충족, FAIL 3건이 신뢰 가능한 Routing 계층의 근거로는 부족 | 가장 보수적이며 현재 Evidence 상태와 가장 정합적인 선택지 |
| **B. 부분 해제(Scoped)** | Freeze 전체가 아니라, PASS로 확인된 좁은 부분집합(예: 단일 실제 계정에서의 Provider Exclusion/API Key Scope 관찰)에 한해 **Experimental Implementation**(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`, `projects/` 격리 환경 한정, HQ production path 무단 연결 금지) 범위에서 추가 관찰을 허용한다 | PASS 4건이 반복 관찰을 쌓을 실험적 가치가 있다고 판단될 경우 | Formal Architecture 변경이 아니라 **관찰 축적 경로**로서만 검토 가능 — 이 RFC는 그 판단을 후속 ADC에 위임한다(§9) |
| **C. 재검토 보류** | 이 RFC를 Not Accepted로 남기고, `RT-0001` Trigger 또는 반복 관찰이 실제로 쌓일 때까지 대기한다 | §3.2 영속화 공백이 그 자체로 재검토 착수 자격을 충족하지 못한다고 판단될 경우 | `ADC-0008`·`ADC-0010`이 반복해 온 "Not Accepted (based on current evidence)" 패턴과 동일한 절차적 선례 |

이 RFC는 A/B/C 중 하나를 선택하지 않는다 — 세 선택지의 판단 기준을
비교 가능한 형태로 제시할 뿐이며, 실제 선택은 §9 Required Decision이
후속 ADC로 위임한다.

## 7. Risks

- **실계정 보호**: OmniRoute 검증이 사용자의 실제 API Key/계정으로
  수행됐다면, 그 자격 증명이 이 저장소나 세션 기록에 노출되지
  않았는지 확인이 필요하다 — 이 RFC는 그 확인을 수행하지 않았다
  (저장소 전수 탐색에서 자격 증명 관련 문자열은 발견되지 않았으나,
  이는 부재 증명이 아니라 이번 탐색 범위 내 미발견일 뿐이다).
- **`REQUIRE_API_KEY=true`와의 관계**: 이 설정이 존재하는 실행
  경로가 있다면, OmniRoute 같은 외부 Gateway로의 우회가 그 보호를
  약화시키지 않는지 후속 검토가 필요하다 — 이 RFC는 이 설정의
  현재 적용 범위를 조사하지 않았다(범위 밖).
- **Provider Exclusion의 신뢰 경계**: PASS로 보고됐으나, FAIL
  3건(특히 `domain_fallback_chains`, `routing_decisions`)이 존재한다는
  사실은 OmniRoute의 설정과 실제 라우팅 동작 사이에 **불일치가
  실제로 있다**는 것을 뜻한다 — Provider Exclusion 자체가 다른
  실행 경로(예: fallback 체인 경유)에서도 항상 성립하는지는 이번
  Evidence만으로 보장되지 않는다.
- **OmniRoute 설정-실동작 불일치**: `priority`·`domain_fallback_chains`·
  `routing_decisions` FAIL은 OmniRoute의 선언적 설정(무엇을
  우선하고, 무엇으로 fallback하고, 무엇을 결정했는지 기록하는 것)이
  실제 동작과 어긋난다는 것을 보여준다 — 이런 계층을 Routing Engine
  후보로라도 다루려면, 이 불일치의 원인(OmniRoute 자체 버그인지,
  이 세션의 설정 오류인지)이 후속 검토에서 먼저 구분돼야 한다.
- **Audit 영속성**: §3.2가 기록한 대로, 이번 검증의 원본 로그·출력이
  저장소에 남아 있지 않다 — Egress Audit이 PASS라 하더라도, 그
  Audit 결과 자체가 재현 가능한 형태로 보존되지 않으면 향후 동일한
  결론을 재확인할 방법이 없다. 이는 이 RFC가 Rule B(반복 관찰)를
  충족한다고 주장하지 않는 가장 직접적인 이유이기도 하다.
- **Freeze 우회 선례화**: 이 RFC가 열리는 것 자체를 "Freeze는
  세션 보고만으로 재검토된다"는 선례로 오독하면, `CONSTITUTION.md`
  Evidence Review 원칙("Evidence 없이 Architecture를 변경하지
  않는다")이 형해화될 위험이 있다 — §9는 이 위험을 명시적으로
  차단한다.

## 8. Recommendation

현재 Evidence 상태(§3)를 근거로, 이 RFC는 **옵션 A(Freeze 유지)를
현재 시점의 기본선으로, 옵션 B(부분 해제/Scoped Experimental)를
후속 ADC가 검토할 조건부 후보로** 제시한다. 근거:

- FAIL 3건과 UNVERIFIED 1건은 OmniRoute를 즉시 신뢰 가능한 Routing
  계층으로 다룰 근거를 약화시킨다 — PASS 4건만으로 Freeze 전체를
  재검토하는 것은 균형 잡힌 판단이 아니다.
- §3.2의 영속화 공백은 `CONSTITUTION.md` Evidence Review 원칙과
  직접 충돌한다 — "사실만 기록"돼야 할 Observation이 아직 재현
  가능한 형태로 존재하지 않는다.
- 그럼에도 PASS 4건(특히 Provider Exclusion·API Key Scope·Egress
  Audit)은 완전히 무시하기에는 구체적이다 — Freeze를 즉시 해제하지
  않으면서도 이 Evidence를 버리지 않는 유일한 경로는, Architecture
  Governance(RFC → ADC → ADR)가 아니라 **Experimental Implementation**
  경로(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`)로 반복 관찰을
  먼저 쌓는 것이다.

이 Recommendation은 결정이 아니다 — §9가 이를 공식 판단 형태로
넘긴다.

## 9. Required Decision

후속 ADC(신설 예정, 이 RFC의 후속)가 다음을 판단하도록 제안한다.

1. **재검토 착수 여부**: 이 RFC가 제기한 Boundary Question("Engine
   Adapter·Model Routing Freeze가 지금 재검토 대상이 될 수 있는가")을
   Accept(재검토 착수)할지, Not Accepted(based on current evidence,
   §6 옵션 C)로 남길지.
2. **Accept된다면** — §6 옵션 A/B 중 무엇을 선택할지, 그리고 옵션
   B를 선택한다면 그 Experimental Implementation의 범위(어떤
   `projects/` 격리 환경에서, 어떤 owner가, 어떤 성공/폐기 기준으로)를
   별도로 정의할지.
3. **선행조건으로서 §3.2 영속화 공백**: 어떤 옵션을 선택하든, 이번
   5라운드 검증의 원본 로그·설정·출력을 저장소에 재현 가능한 형태로
   기록하는 것이 후속 판단의 전제조건이 되는지.
4. **Escalate 응답**: `ADC-0003` 판단 4가 남긴 공백("Multi-Model 실행
   요구를 판단할 절차가 지정되지 않음")에 대해, 이 RFC를 그 절차의
   시작으로 인정할지, 아니면 별도 Jarvis OS 수준 RFC가 다시 필요하다고
   볼지.
5. **절차적 해석의 타당성**: §0이 제시한 해석 — "`ADC-0010`의
   'Phase 1 종료 후 불변 원칙과 충돌한다'는 판단과 `GOVERNANCE-REVIEW-0004`의
   '사실상 Governance 경로가 막혀 있다'는 서술은 모두 C4(Development
   HQ) 판단 맥락에 한정되며, Architecture Governance 절차로 Freeze
   목록을 직접 재검토하는 이 RFC의 경로 자체를 막지 않는다" — 가
   타당한지, 아니면 이 RFC가 이미 절차적으로 열려서는 안 될 것을 연
   것인지.

이 RFC 자체는 그 판단을 내리지 않는다.

## 10. Next Step: RFC → ADC/ADR → Implementation

```
이 RFC (Proposed)
  ↓
후속 ADC (신설 예정)
  — §9의 4개 질문 판단
  — Accept(Scoped)라면: 책임 경계(Governance Layer가 아님을 재확인)와
    Integration Architecture(OmniRoute가 어디에 어떻게 붙는지)를 검토
  ↓ (Accept(Scoped)인 경우에만)
ADR
  — Baseline(§14.1, §16.2) 갱신 여부와 범위 확정
  — `IMPLEMENTATION_RULES.md` 금지 표 중 어떤 항목이, 어떤 범위로
    완화되는지(전면 해제가 아닌 Scoped 완화 원칙 — `ADC-0013`→`ADR-0003`,
    `ADC-0016`→`ADR-0006` 선례와 동일)
  ↓
Implementation
  — ADR이 확정한 범위 안에서만, Experimental Implementation 절차를
    거쳐 착수
```

Accept되지 않는 경우(§6 옵션 C), `CONSTITUTION.md` Architecture
Freeze와 `IMPLEMENTATION_RULES.md` 금지 표는 변경 없이 그대로
유지되며, §3.2 영속화 공백이 해소되고 반복 관찰이 축적될 때 재론한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. 이번 세션 보고(§3.1)와 기존
  Governance 문서(`CONSTITUTION.md`, `BASELINE.md`, `ADC-0010`,
  `ADC-0003`, `RT-0001`, `ARCHITECTURE_GOVERNANCE.md`)만 인용했다.
  새 실험은 수행하지 않았다.
- Evidence의 한계를 숨겼는가 — **아니오**. §3.2에서 영속화 공백을
  명시적으로 기록했고, §7 Risks에 별도 항목으로 반복했다.
- Freeze 해제를 전제했는가 — **아니오**. §6은 Freeze 유지를 포함한
  세 옵션을 동등하게 비교했고, §8 Recommendation도 현재 시점 기본선을
  Freeze 유지로 제시했다.
- OmniRoute를 Governance Layer로 다뤘는가 — **아니오**. §5 Out of
  Scope에서 명시적으로 배제했다 — Routing Engine/Execution Layer
  구현 후보로만 한정했다.
- 검증되지 않은 OmniRoute 기능을 Contract에 포함했는가 — **아니오**.
  §5·§9 어디에서도 `priority`/`domain_fallback_chains`/`routing_decisions`/
  `domain_budgets`를 Contract 후보로 명명하지 않았다.
- Multi-Agent Runtime을 재론했는가 — **아니오**. §5 Out of Scope에서
  별도 항목임을 명시하고 배제했다.
- Engine Caller 위치(`ADC-0010`)를 재조사했는가 — **아니오**. §5에서
  명시적으로 배제했다.
- 기존 Governance 절차를 우회했는가 — **아니오**. RFC → ADC → ADR
  절차 자체를 이 문서가 대체하지 않으며, §10이 그 절차를 그대로
  따른다.
- Architecture/Contract를 확정했는가 — **아니오**. §9는 모든 확정을
  후속 ADC/ADR로 위임했다.
- 코드/Baseline을 수정했는가 — **아니오**. 이 RFC 파일 외 어떤 파일도
  수정하지 않았다.
