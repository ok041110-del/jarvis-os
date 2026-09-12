# ADC-0039: Multi-Engine Architecture 전환 재평가 (RFC-0036 후속, RT-0001 Candidate 2)

## Amendment (후속 세션) — Decision: RE-EVALUATE → TRANSITION

**이 Amendment는 아래 원본 문서를 삭제·수정하지 않는다.** 원본이 무엇을
근거로 RE-EVALUATE를 판정했는지는 그대로 역사적 기록으로 남기고, 이
Amendment는 그 이후 실제로 바뀐 사실 관계만 추가한다.

**바뀐 사실**: 사용자가 "현재 환경에서는 OmniRoute 운영 대안(원격
호스팅)을 사용할 수 없다는 제약이 확정되었다"고 명시했다. 이는 원본
§Validation Requirements 1번("운영 대안 배제 확인")이 요구한 조건이
충족되었다는 뜻이다.

**충족되지 않은 조건**: 원본 §Validation Requirements 2번("반복
관찰")은 이 시점에도 별도의 반복 관찰 Evidence로 채워지지 않았다.
이 Amendment는 그 사실을 숨기지 않는다 — TRANSITION 판정은 1번
조건만으로 내려진다.

**왜 1번 조건만으로 TRANSITION이 정당화되는가**: 원본 §Trade-offs가
이미 보인 대로, Multi-Engine 전환이 실제로 값어치를 갖는 유일한 경로는
"휴대폰(또는 유사 제약 환경)에서 Jarvis가 동작해야 한다"는 요구다 —
2번 조건("목적별 품질 차이")은 그 값어치와 별개로, Engine 선택
**방식**(Agent-level 정적 선택)이 온당한지를 뒷받침하는 조건이었지
Multi-Engine **채택 여부** 자체의 전제조건은 아니었다. 운영 대안이
배제된 이상, Single Engine 유지(Option 1)는 더 이상 실행 가능한
대안이 아니다 — Jarvis가 그 환경에서 아예 동작하지 않기 때문이다.
따라서 §Decision 판정 근거 1번(휴대폰 제약 단독으로는 부족)의 전제
자체가 무효화된다 — "운영 변경으로 해결 가능하다"는 대안이 이제
실제로 배제되었으므로, 남은 §Decision 판정 근거 2번(반복 관찰 부재)
만으로는 Single Engine 유지를 정당화할 수 없다(Single Engine 유지가
곧 "동작 불가"를 뜻하게 되었기 때문).

**Case B 전환이 승인되는 이유(요약)**:
1. Option 1(Single Engine 유지 + 운영 변경)의 실행 가능성이
   사라졌다 — 유일한 대안이 이제 배제됨.
2. Contract 변경은 이미 불필요함이 확정되어 있었다(원본
   §Engine Contract 재검토) — 전환 비용이 낮다는 원본의 판단이
   그대로 유효하다.
3. Option 4(Central Router)는 여전히 배제한다(15행 위반 확정적,
   원본 판정 근거 4 유지) — TRANSITION은 Option 2/3 혼합 범위로만
   승인된다.

**Decision (Amended): TRANSITION.** 실행 형태(Stage Mapping, Engine
모듈 경계, 구현)는 `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`가
확정한다. 아래 원본 §Decision·§Validation Requirements·§Open
Questions는 삭제하지 않고 그대로 유지하되, 이 Amendment가 우선한다.

**ADR 여부(갱신)**: TRANSITION이므로 사용자 지시 §11에 따라 후속 ADR이
필요하다 — `ADR-0024`가 그 ADR이다(원본 §ADR 여부의 "RE-EVALUATE라서
작성하지 않는다"는 더 이상 적용되지 않는다).

---

## 원본 (RE-EVALUATE 판정 당시 그대로 보존)

## 목적

`RFC-0036-chatgpt-claude-code-dual-engine-boundary.md`가 조사만 하고 멈춘
지점("ChatGPT Engine/Claude Code Engine 분리를 Jarvis 코드가 목적별로
선택하게 하자"는 요청)을 이어받아, `docs/governance/rt/RT-0001.md`
Candidate 2(Engine Gateway)의 Re-evaluation Trigger를 실제로 충족시키는지,
충족시킨다면 `IMPLEMENTATION_RULES.md` 16·21행과 `ADR-0017`이 승인하지
않은 Case A→B 전환을 지금 승인할지를 판정한다. 이 ADC는 코드를 작성하지
않는다(§12 구현 금지, 사용자 지시).

**전제(main `50db4c6` 기준 재확인)**: RFC-0036 §1이 이미 확정한 사실
관계(Engine Contract `str -> str`, Production 호출 지점 7곳 전부
`omniroute_engine.py` 단일 대상, `engine.py`는 Production 호출 0건이지만
개념적으로 이미 "텍스트 전용 Claude Code Engine")를 이 ADC는 다시 조사하지
않고 그대로 인용한다 — `hqs/development/mvp/engine.py`,
`hqs/development/mvp/omniroute_engine.py`를 이번 세션에서도 직접 열어
동일함을 재확인했다(코드 0줄 변경, 함수 시그니처·호출부 동일).

---

## Context

- 사용자의 실제 실행 환경(휴대폰)에서 OmniRoute 서버 구동에 제약이 있다.
- 현재 Engine Routing은 전부 OmniRoute `model="auto"`에 위임되어 있고,
  Jarvis 코드는 Claude/ChatGPT 중 무엇이 실제로 응답하는지 선택하지도
  관찰하지도 않는다(`ADR-0017` §2.3, §6.2).
- 향후 Stage/Agent 목적(Reasoning vs Implementation vs Review)에 따라
  서로 다른 Engine을 쓰고 싶다는 요구가 있다.
- `RFC-0036`이 이미 다음을 Evidence로 확정했다(재조사 없이 인용):
  - Engine Contract 변경 불필요(§1.5) — 기존과 동일한 `str -> str`
    모듈을 하나 더 추가하고 Agent import 한 줄만 바꾸면 됨.
  - `agents/backend.py`가 `CODE_REVIEW`/`CODE_GENERATION` 두 목적을
    같은 module-level `call_engine` 이름 하나로 공유 — Agent-level
    routing을 그대로 쓰면 이 파일을 함수 단위로 쪼개야 함.
  - 지금 코드에 "Repository Execution Engine"(LLM이 파일을 직접
    읽고 쓰는 모드)은 존재하지 않는다 — `engine.py`도 이미 도구 접근이
    전부 차단된 순수 텍스트 함수다.

## Problem

"두 가지 서로 다른 문제"가 하나의 요청 안에 섞여 있다.

1. **운영 제약**: 휴대폰에서 OmniRoute 서버를 직접 구동하기 어렵다.
2. **Architecture 요구(주장)**: Jarvis가 작업 목적에 따라 Engine을
   직접 선택해야 한다.

1번은 "OmniRoute를 어디서/어떻게 호스팅하는가"의 운영 문제이지,
Jarvis 코드가 여러 Engine을 인지·선택해야 하는가의 Architecture
문제가 아니다 — OmniRoute를 원격 서버(휴대폰이 아닌 곳)에 그대로 계속
띄워두고 휴대폰은 네트워크로 그 endpoint를 호출하기만 하면, 코드 한
줄도 바꾸지 않고 1번이 해결된다. 이 대안이 실제로 시도·배제되었다는
Evidence가 이번 요청 어디에도 없다.

2번은 별개의, 훨씬 더 근본적인 주장이다 — "Jarvis가 Engine을 선택할
능력을 가져야 한다"는 것은 운영 제약과 무관하게 그 자체로 참일 수도,
아닐 수도 있다. 이 ADC는 이 둘을 동일한 문제로 취급하지 않는다(사용자
지시 §3 그대로).

## Trigger

`RT-0001` Candidate 2:

> Re-evaluation Trigger: Engine 수 ≥ 2 (두 번째 Engine이 실제로
> 추가되어 `call_engine()` 호출 지점이 둘 이상의 서로 다른 Engine을
> 대상으로 하게 됨)

**정확한 상태**: 이 Trigger는 아직 실제로 발동하지 않았다 — 현재
Production 호출 지점 7곳은 전부 `omniroute_engine.py` 하나만
대상으로 하고(RFC-0036 §1.4 표, 이번 세션 재확인), `chatgpt_engine.py`
같은 코드는 저장소 어디에도 없다. RFC-0036 §2가 확인한 것은 "이번에
**요청받은 Architecture를 실제로 구현하면** 이 Trigger를 정의 그대로
충족시킨다"는 조건부 사실이지, Trigger가 이미 충족되어 있다는 사실이
아니다. 이 구분이 이 ADC의 핵심 판정 기준이다(§Decision).

## Current Architecture — 무엇이 Frozen이고 무엇이 구현 세부사항인가

```
Stage / Agent
      ↓
call_engine() 계열 함수 (Agent 파일 import 시점에 고정)
      ↓
Single Engine (production: OmniRoute 1개)
```

| 요소 | Frozen 여부 | 근거 |
|---|---|---|
| Engine 개수 = 1(Production) | **Frozen** | `RT-0001` Candidate 2, `IMPLEMENTATION_RULES.md` 21행, `ADR-0017` §6.2("Case B 밖으로의 전환을 승인하지 않는다") |
| Engine 선택 방식(Jarvis 코드가 선택하지 않음, OmniRoute 내부에 위임) | **Frozen** | `ADC-0031` §Q1 조건(b), `ADR-0017` §2("Routing Policy는 Jarvis 코드에 존재할 수 없다") |
| Provider abstraction 부재(Port/Adapter 없음) | **Frozen** | `IMPLEMENTATION_RULES.md` 15행, `ADC-0031` §Decision "금지"("Engine Gateway abstraction") |
| OmniRoute 사용 자체 | **Frozen(Scoped Accept)** | `ADR-0017` §6.1 |
| Agent → Engine 호출 관계(파일 import 한 줄로 정적 고정) | **구현 세부사항** | Contract가 아니라 현재 코드가 우연히 택한 형태 — `call_engine`이라는 module-level 이름만 mocking boundary로 작동(`test_mvp_0001.py`), 이 이름 자체는 Governance 문서 어디서도 Public Contract로 지정되지 않았다 |
| `str -> str` Engine Contract 형태 | **구현 세부사항이자 사실상 안정적 관행** | `BASELINE.md` §14 Kernel Public Contract가 함수 시그니처 자체를 아직 확정하지 않았다(`ADR-0017` §6.2 "Engine Adapter Contract(§14) 변경 없음") — 그러나 두 독립 구현체(`engine.py`/`omniroute_engine.py`)가 이미 이 모양을 따르고 있어 사실상의 안정 관행이다 |

**결론**: Engine **개수**와 **선택 주체**(Jarvis 코드 vs 외부)가
Frozen의 본질이다. 호출부가 파일 import로 고정되는 방식이나
`str -> str` 시그니처는 아직 공식 Contract로 못박히지 않은 구현
세부사항이다 — 즉 "몇 개의 Engine을 어떻게 부를 수 있는가"가 아니라
"Jarvis 코드가 그 선택 로직을 갖는가"가 Freeze의 실체다.

## Constraints

- `IMPLEMENTATION_RULES.md` 16행: 여러 Engine 중 무엇을 선택할지
  결정하는 로직 금지(런타임 `if/else`든 컴파일타임 import 선택이든
  동일하게 해당 — RFC-0036 §2가 이미 이 점을 명시).
- `IMPLEMENTATION_RULES.md` 21행: Multi Engine 지원 코드 작성 금지.
- `ADR-0017` §6.2: "Case A 밖(Case B/C)으로의 전환을 승인하지 않는다"
  — 명시적 재승인 없이는 어떤 구현도 이 경계를 넘을 수 없다.
- `RT-0001` 자체의 절차 규범(다른 3개 Candidate와 동일 기준): Trigger는
  "실제로 추가됨/구현됨/발생함" 형태의 **관찰된 사건**이어야 하고,
  `IMPLEMENTATION_RULES.md`의 "Dynamic Workflow 재검토 Trigger" 절이
  보여주는 것과 같이 이 저장소의 Governance 관행은 **1회 관찰은 Evidence로
  인정하지 않는다**(반복 관찰 요구).
- CLAUDE.md Frozen Architecture: Architecture 변경은 RFC → ADC → ADR
  순서로만 — 이 ADC는 그 두 번째 단계다.

## Options

### Option 1 — Single Engine 유지 + 현재 구조 확장

```
All Agents
   ↓
Single Engine (OmniRoute)
```

휴대폰 제약은 OmniRoute를 원격 서버로 계속 운용하는 **운영 변경**으로
해결한다. Jarvis 코드는 무변경.

### Option 2 — Agent-level Engine Selection

```
Agent
 ↓
Engine Selection (파일 import 고정)
 ├─ ChatGPT
 └─ Claude Code
```

RFC-0036 §1.4가 이미 지적: `agents/backend.py`(Review+Generation 혼재)
1개 파일을 함수 단위로 쪼개야 깨끗하게 맞는다.

### Option 3 — Function/Capability-level Selection

```
Capability
 ↓
Engine
```

예: Architecture → ChatGPT, Implementation → Claude Code, Review →
ChatGPT. Agent 파일 경계와 무관하게 목적(Capability) 단위로 고정.
`identify_target`(Stage 04)·`qa_agent_test_execution`처럼 목적이
모호한 두 지점(RFC-0036 §3 표)에 대해서는 여전히 판단이 필요하다.

### Option 4 — Central Engine Router

```
Agent
 ↓
Engine Router
 ├─ ChatGPT
 └─ Claude Code
```

`IMPLEMENTATION_RULES.md` 15행이 금지하는 "Engine Gateway(Port/Adapter
추상화)"에 가장 가깝다 — 런타임 판정 로직을 한 곳에 모으는 순간 그 자체가
Policy 판정 로직(16·17행 금지 대상)이 된다.

## Trade-offs

| 기준 | Option 1(Keep) | Option 2(Agent-level) | Option 3(Capability-level) | Option 4(Router) |
|---|---|---|---|---|
| Architecture complexity | 없음 | 낮음(정적 import) | 중간(`backend.py` 분리 필요) | 높음(추상화 계층 신설) |
| Governance impact | 없음(Freeze 유지) | RT-0001 Trigger 충족 → ADR 필요 | RT-0001 Trigger 충족 → ADR 필요 | RT-0001 Trigger 충족 + 15행(Gateway) 위반 → ADR로도 못 덮음(별도 Freeze 해제 필요) |
| Implementation complexity | 없음(운영 변경만) | 낮음(import 한 줄 + `backend.py` 함수 분리) | 중간(모호 지점 2곳 판단 필요) | 높음 |
| Contract impact | 없음 | 없음(RFC-0036 §1.5 확정) | 없음(동일 근거) | 잠재적 있음(Router가 `EngineRequest`류 객체를 요구할 위험, YAGNI 위반) |
| Testing complexity | 없음(기존 251 passed 유지) | 낮음(기존 mocking boundary 그대로, RFC-0036 §1.6) | 중간(Capability↔Engine 매핑 테스트 추가) | 높음(Router 자체 단위 테스트 + 기존 mocking boundary 재설계) |
| Cost | 무변경 | ChatGPT API 비용 신규 발생(Not Determined, 실측 없음) | 동일 | 동일 + Router 유지비용 |
| Latency | 무변경 | Engine당 상이(Not Determined) | 동일 | Router 오버헤드 추가 |
| Reliability | OmniRoute의 기존 Fallback 그대로 유지 | Fallback 없음(단일 함수 고정, RFC-0036 §1.2) — Engine별 장애 시 Jarvis 코드가 아무 대응도 하지 않음 | 동일 | Router가 Fallback을 가지려는 유혹 → 17행(Policy) 위반 위험 |
| Maintainability | 최고(단일 대상) | 중간(`backend.py` 분리로 파일 수 증가) | 중간 | 낮음(추상화 계층 자체가 유지 대상) |
| 휴대폰 환경 적합성 | **운영 변경으로 이미 해결 가능**(원격 호스팅) — Architecture 변경 불필요 | 무관(휴대폰 제약을 해결하지 않음 — ChatGPT도 여전히 외부 서버) | 무관 | 무관 |
| 향후 Multi-Agent 확장성 | 낮음(Agent 수 늘어도 대응 없음) | 중간 | 높음(목적 단위라 Agent 신설에 독립적) | 높음(그러나 15행 위반 비용이 더 큼) |

**핵심 관찰**: 휴대폰 적합성 행에서 Option 2/3/4 어느 것도 Option 1보다
낫지 않다 — ChatGPT Engine이든 Claude Code Engine이든 똑같이 "휴대폰이
아닌 어딘가"에서 실행되는 외부 호출이다. 즉 **이번 요청이 실제로 해결
하려는 운영 문제에 대해서는 Multi-Engine 전환이 우위를 전혀 제공하지
않는다.** Multi-Engine이 실제로 값어치를 갖는 것은 오직 "목적별로 다른
LLM 품질/특성이 필요하다"는 두 번째(별개) 요구뿐이며, 이는 아직 반복
관찰된 Evidence가 없다(§Problem, §Governance Impact).

## 중요한 판단 — Provider vs Execution Environment

ChatGPT는 LLM/Reasoning Provider이고, Claude Code는 LLM +
Repository Execution Environment(filesystem/shell/git/test 실행)라는
사용자의 구분은 **개념적으로는 맞지만 현재 코드에는 대응물이 없다**.
`engine.py::call_engine()`은 `--disallowedTools`로 Write/Edit/Bash/
Read/Glob/Grep/NotebookEdit/WebFetch/WebSearch를 전부 차단하고
`cwd`를 저장소 밖으로 고정한다(RFC-0036 §3.1 재확인, 이번 세션에서
`engine.py` 원문으로 직접 재검증). 즉 지금 "Claude Code Engine" 후보는
이미 순수 텍스트 생성 함수이지 Repository Agent가 아니다.

**결론**: `provider="claude"` / `provider="chatgpt"`를 동일한
Contract로 취급하는 것은 **지금 시점에는 문제가 없다** — 왜냐하면 둘 다
현재는 Text/Reasoning Execution Mode 하나뿐이기 때문이다. "Claude
Code = Repository Execution Engine"이라는 더 큰 구도는 LLM에게 실제
도구 접근권(filesystem/shell/git)을 주는 것이고, 이는 이번 ADC보다
훨씬 크고 별도인 Architecture Decision 대상이다 — 이 ADC는 그 구도를
전제하지 않는다(RFC-0036 §3.1과 동일 결론, 재확인).

## Engine Contract 재검토

1. **ChatGPT reasoning은 `str -> str`로 충분한가?** — 그렇다. 순수
   텍스트 요청/응답이며 별도 상태나 도구 결과를 주고받지 않는다.
2. **Claude Code repository execution은 `str -> str`로 충분한가?** —
   질문 자체가 현재 코드에 적용되지 않는다. 지금의 "Claude Code
   Engine"(`engine.py`)은 repository execution을 하지 않는 순수 텍스트
   함수이므로 `str -> str`로 이미 충분하다. Repository execution을
   실제로 도입하면 그 시점에 별도로 재검토해야 하지만, 그것은 이 ADC의
   범위(Provider 두 가지의 목적별 정적 선택)를 벗어난다.
3. **두 Engine을 하나의 Contract로 묶는 것이 abstraction leakage를
   일으키는가?** — 현재 범위(둘 다 Text/Reasoning Mode)에서는
   아니다. 둘 중 하나가 도구 접근권을 갖게 되는 순간부터는 leakage가
   발생한다(에러 모델·타임아웃·중간 진행 상태가 서로 달라짐) — 그러나
   그것은 지금 요청 범위 밖이다.
4. **별도의 Execution Contract가 필요한가?** — 지금은 불필요.
   Repository Execution Engine이 실제로 도입될 때 별도 RFC 대상.
5. **지금 새 Request/Result abstraction을 만드는 것이 YAGNI 위배인가?**
   — 그렇다. RFC-0036 §1.5·§3.2가 이미 확인한 대로, 기존과 동일한
   `str -> str` 모듈을 하나 더 추가하는 것으로 충분하며
   `EngineRequest`/`EngineResult`/`engine=` 매개변수/Router 클래스는
   전부 지금 시점에는 불필요하다.

## Governance Impact

| 문서 | 이 ADC와의 관계 |
|---|---|
| `RT-0001` Candidate 2 | Trigger는 "실제 구현 시" 조건부로 충족되나(§Trigger), 아직 발동하지 않았다. 이 ADC는 RT-0001 자체를 수정하지 않는다. |
| `IMPLEMENTATION_RULES.md` 16·21행 | 이 ADC는 문구를 수정하지 않는다(Scoped 예외 여부는 §Decision에서 판정하되, 실제 문구 반영은 후속 ADR 대상 — `ADC-0031`이 15·16·17·21행에 대해 밟은 것과 동일한 2단계 구조). |
| `ADR-0017` | §6.2("Case A 밖으로의 전환을 승인하지 않는다")를 뒤집지 않는다 — 이 ADC가 그 전환을 승인하지 않는 한 `ADR-0017`의 범위는 그대로 유효하다. |
| `RFC-0036` | §4·§6 결론(INVESTIGATE, Contract 변경 불필요, Architecture 변경 없음)을 재론하지 않고 그대로 이어받는다. 이 ADC는 RFC-0036이 열어 둔 "ADC 단계"를 수행한다. |

**"Engine 수 ≥ 2" 조건이 현재 요구사항에 해당하는가?** — 조건부로만
해당한다. 지금 이 순간에는 해당하지 않는다(Engine 수 = 1, Production
기준). 이 요청을 실제로 구현하면 정의상 해당하게 된다. 이 ADC는 "지금
구현해도 되는가"를 판정하는 것이지 "이미 Trigger가 발동했다"고 선언하는
것이 아니다.

## Contract Impact

**없음.** `str -> str` Engine Contract는 이 ADC로 변경되지 않으며,
변경할 필요도 없다는 것까지 확정한다(§Engine Contract 재검토 5번).
`BASELINE.md` §14 Kernel Public Contract 자체도 이 ADC로 손대지 않는다.

## Architecture 변경 여부

**없음.** 이 ADC는 코드·Contract·Baseline 문서 어느 것도 수정하지
않는다. Frozen 상태는 그대로 유지된다.

---

## Decision

**RE-EVALUATE — 추가 Evidence 필요. KEEP도 TRANSITION도 아니다.**

### 판정 근거

1. **휴대폰 제약 하나만으로는 Multi-Engine 전환을 정당화하지 않는다**
   (사용자 지시 §10 명시, 그리고 §Trade-offs 표가 실증: Option 2/3/4
   중 어느 것도 휴대폰 적합성에서 Option 1보다 낫지 않다 — ChatGPT도
   Claude Code Engine도 똑같이 "휴대폰 밖"에서 실행되는 외부 Provider
   이기 때문이다). 이 제약은 OmniRoute 원격 호스팅이라는 **운영
   변경**으로 먼저 해소를 시도해야 하며, 그 시도·배제 여부에 대한
   Evidence가 이번 요청에 없다.
2. **"목적별 Engine 선택이 필요하다"는 두 번째 요구는 아직 반복 관찰된
   Evidence가 없다** — `RT-0001`의 다른 3개 Candidate와
   `IMPLEMENTATION_RULES.md`의 "Dynamic Workflow 재검토 Trigger" 절이
   보여주는 이 저장소의 일관된 기준은 "1회 관찰/1회 요청은 Evidence로
   인정하지 않는다"이다. 지금 이 요구는 실제 Dogfooding 중 반복 관찰된
   사례가 아니라 사용자의 단일 요청(가설)이다.
3. **다만 Contract 차원의 장벽은 없다** — Engine Contract 변경 불필요
   (§Engine Contract 재검토), YAGNI 위반 없이 기존 패턴 확장만으로
   구현 가능(RFC-0036 §1.5). 즉 향후 Evidence가 쌓이면 **전환 비용은
   낮다** — 이것이 KEEP을 영구 확정하지 않고 RE-EVALUATE로 열어 두는
   이유다.
4. Option 4(Central Router)는 Evidence 유무와 무관하게 15행(Engine
   Gateway) 위반이 확정적이므로 이 ADC 시점에 이미 배제한다 — 향후
   TRANSITION이 실제로 승인되더라도 Option 2 또는 3(정적 import 선택)
   범위 안에서만 검토되어야 한다.

### 이 Decision이 KEEP과 다른 점

RT-0001의 다른 Candidate처럼 "무기한 Keep"이 아니라, 아래 Evidence
Requirement가 충족되면 즉시 재소집 가능한 상태로 열어 둔다.

## Validation Requirements — TRANSITION으로 전환하기 위해 필요한 Evidence

다음 중 최소 조건을 만족해야 후속 ADC/ADR이 TRANSITION을 검토할 수
있다(이 ADC 자신은 이 조건 충족 여부를 판정하지 않는다 — 향후 별도
세션의 몫).

1. **운영 대안 배제 확인**: OmniRoute를 원격(휴대폰이 아닌 상시 가동
   서버)에 호스팅하는 방식을 실제로 시도했고, 그 방식이 실패하거나
   불충분했다는 구체적 관찰(지연시간, 가용성, 비용 등 실측치).
2. **반복 관찰**(1회 아님): 실제 Development HQ Dogfooding에서, 동일
   Engine(OmniRoute `model="auto"`)으로 처리했을 때 품질/실패율 문제가
   Stage/Agent 목적별로 반복 관찰되고, 다른 Engine이었다면 해결됐을
   것이라는 근거(사후 비교 실험 등).
3. **`backend.py` 분리 범위 확정**: Option 2를 택한다면
   `backend_agent_code_review`/`backend_agent_code_generation` 함수
   분리가 다른 회귀를 일으키지 않는다는 사전 확인.
4. **모호 지점 판정**: `identify_target`(Stage 04)·
   `qa_agent_test_execution`이 Reasoning/Implementation/Review 중
   어디에 속하는지에 대한 명시적 근거(추측 배제).

## Open Questions

- OmniRoute 원격 호스팅이 실제로 휴대폰 제약을 해소하는지는 이
  저장소 범위 밖(운영/인프라) 질문이라 이 ADC가 답하지 않는다 — 사용자
  환경에 대한 실제 시도가 선행되어야 한다.
- Repository Execution Engine(LLM에게 도구 접근권을 주는 것)은 이
  ADC 범위 밖이며, 도입 여부는 완전히 별도의 RFC 대상이다(§Provider
  vs Execution Environment).
- Audit/Cost 관측(Engine별 실제 품질·비용 차이)을 위한 계측이 현재
  코드에 없다 — Validation Requirement 2를 충족하려면 이 계측이 먼저
  필요할 수 있으나, 이 계측 자체를 지금 구현하는 것도 이 ADC의 범위
  밖이다(§12 구현 금지).

---

## ADR 여부

**이번 세션에서 ADR을 작성하지 않는다.** Decision이 TRANSITION이 아니라
RE-EVALUATE이므로, 사용자 지시 §11("ADC가 RE-EVALUATE라면 ADR을 선행
작성하지 않는다")을 그대로 따른다. `RT-0001` Candidate 2, `ADR-0017`,
`IMPLEMENTATION_RULES.md` 16·21행은 전부 무변경으로 유지된다.

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: `engine.py` 변경, `omniroute_engine.py`
변경, `chatgpt_engine.py`/`claude_code_engine.py` 생성, Router 구현,
Stage Mapping 구현, Agent 수정. 문서 1건만 추가했다.

## Self Review

- 새로운 Architecture를 추가했는가 — **아니오**. 기존 Frozen 상태를
  판정했을 뿐이다.
- Contract를 변경했는가 — **아니오**(§Contract Impact).
- 휴대폰 제약 하나만으로 Multi-Engine을 정당화했는가 — **아니오**
  (§Decision 판정 근거 1, §Trade-offs 표에서 실증).
- Jarvis의 목적별 Engine 선택 요구를 무시했는가 — **아니오**(별개
  질문으로 명시적으로 분리하고, TRANSITION에 필요한 구체적 Evidence
  Requirement를 남겼다).
- `RT-0001`/`ADR-0017`/`IMPLEMENTATION_RULES.md`를 직접 수정했는가 —
  **아니오**.
- RFC-0036의 결론을 뒤집었는가 — **아니오**(그 결론을 이어받아 ADC
  단계를 완료했을 뿐이다).
- ADR을 선행 작성했는가 — **아니오**(Decision이 RE-EVALUATE이므로
  사용자 지시에 따라 작성하지 않았다).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다.

## Related

- `docs/architecture/core/RFC-0036-chatgpt-claude-code-dual-engine-boundary.md`
- `docs/research/DEV-HQ-V2.0-CLAUDE-CHATGPT-PROVIDER-SEPARATION-AUDIT-0001.md`
- `docs/governance/rt/RT-0001.md`
- `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md`
- `docs/architecture/core/ADR-0017-omniroute-production-adoption-final-review.md`
- `hqs/development/IMPLEMENTATION_RULES.md`
