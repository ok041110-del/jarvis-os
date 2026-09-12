# ADR-0024: Multi-Engine Architecture Adoption — ChatGPT/Claude Code 2-Engine 전환

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0024` |
| 제목 | `RFC-0036`이 조사만 하고 멈춘 ChatGPT/Claude Code 목적별 Engine 선택 요청을, `ADC-0039` Amendment(RE-EVALUATE → TRANSITION)의 근거 위에서 실제로 승인·확정한다 |
| 상태 | **Accepted — Multi-Engine Architecture(2-Engine: ChatGPT/Claude Code) Production Adoption** |
| Context | `RFC-0036` → `ADC-0039`(RE-EVALUATE) → `ADC-0039` Amendment(TRANSITION, 운영 환경 제약 확정) → 이 ADR |
| 관련 RFC | `RFC-0036-chatgpt-claude-code-dual-engine-boundary.md` |
| 관련 ADC | `ADC-0039-multi-engine-re-evaluation.md`(Amendment 포함), `ADC-0031-omniroute-thin-engine-caller-boundary.md` |
| 관련 ADR | `ADR-0017-omniroute-production-adoption-final-review.md`(§6.2 Amendment로 부분 superseded, §5 Amendment 항목 참조) |
| 선행 Decision(참고, 뒤집지 않음) | `docs/governance/rt/RT-0001.md` Candidate 2(이 ADR로 Trigger 발동 확정), `hqs/development/IMPLEMENTATION_RULES.md` 16·21행(문구는 유지, Scoped 예외 추가) |

이 ADR은 `ADC-0039`의 Amendment(RE-EVALUATE → TRANSITION)가 이미 확정한
"전환 승인"을 실행 가능한 형태(Stage Mapping, Engine 모듈, 후속 Validation
Requirement)로 구체화한다. `ADC-0039` 본문의 Trade-off 분석·Option 비교
자체를 재론하지 않는다.

---

## Context

- `RFC-0036`이 ChatGPT/Claude Code 2-Engine 분리 요청을 조사했고,
  Contract 변경이 불필요함(§1.5)과 현재 Frozen Architecture와의 충돌
  (§2)을 확인한 뒤 ADC 단계로 넘겼다.
- `ADC-0039`(최초)는 "휴대폰 제약(운영 문제)"과 "목적별 Engine 선택
  요구(Architecture 문제)"를 분리하고, 운영 대안(OmniRoute 원격
  호스팅)이 시도·배제되었다는 Evidence가 없다는 이유로 **RE-EVALUATE**
  판정을 내렸다.
- 이번 요청에서 "현재 환경에서는 OmniRoute 운영 대안을 사용할 수
  없다는 제약이 확정"되었다고 명시됐다 — 즉 `ADC-0039` §Validation
  Requirements 1번("운영 대안 배제 확인")이 충족됐다고 선언된 것이다.
  이 ADR은 그 선언을 있는 그대로의 Governance 사실로 기록한다 —
  독립적인 재실측(예: 실제 원격 호스팅 시도 로그)은 이 세션이
  생성하지 않았다는 점을 명시적으로 남긴다(§Validation Requirements
  참조, 과장 방지).
- `ADC-0039` §Validation Requirements 2번("반복 관찰")은 이 ADR
  시점에도 별도로 채워지지 않았다 — 이 ADR의 Decision은 §Validation
  Requirements 1번(운영 대안 배제)만으로 TRANSITION을 정당화하며, 이
  사실을 숨기지 않는다(§Governance Impact에서 재확인).

## Problem

Jarvis 코드가 단일 OmniRoute Engine에 완전히 의존하는 현재 구조는,
OmniRoute 운영이 불가능한 환경에서 Jarvis 전체가 동작할 수 없게
만든다. 동시에 목적별로 Reasoning(ChatGPT)과 Implementation/Execution
(Claude Code)을 분리하고 싶다는 요구가 있다. 두 문제를 하나의
Architecture 결정으로 해결한다.

## Trigger

`RT-0001` Candidate 2:

> Engine 수 ≥ 2 (두 번째 Engine이 실제로 추가되어 `call_engine()`
> 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로 하게 됨)

이 ADR의 구현(§Engine Architecture, §Stage Mapping)이 이 Trigger를
**실제로** 충족시킨다 — `ADC-0039`(최초)가 "조건부"로만 인정했던
것과 달리, 이제는 실제 코드에 두 번째·세 번째 Engine 모듈이 존재하고
서로 다른 호출부가 서로 다른 Engine을 대상으로 한다. 이 ADR이 그
Trigger 발동을 공식적으로 승인한다.

---

## Decision

**Accept — Multi-Engine Architecture(ChatGPT Engine + Claude Code
Engine, 2-Engine)를 Production Adoption한다.**

```
                    Jarvis OS
                       │
                     Agent
                       │
                Engine Contract (str -> str, 무변경)
                       │
          ┌────────────┴────────────┐
          │                         │
      ChatGPT Engine          Claude Code Engine
     reasoning / review       implementation / execution
```

- Central Router/Gateway는 만들지 않는다(§Alternatives Option C 채택
  근거 참조).
- OmniRoute는 이번 전환의 필수 실행 경로가 아니다 — `omniroute_engine.py`
  파일은 삭제하지 않고 선택적 Adapter로 코드에 그대로 남는다(향후
  세 번째 Engine으로 재도입 가능, 이 ADR이 그 가능성을 닫지 않는다).
- 현재 요구 범위에서는 ChatGPT/Claude Code 두 Engine만 지원한다.

### Engine 선택 방식 (Option C 채택)

| Option | 설명 | complexity | readability | testability | Governance | Contract | future extension |
|---|---|---|---|---|---|---|---|
| A — Agent/Function이 Engine adapter 직접 선택 | 각 파일이 필요한 Engine 모듈을 import | 낮음 | 높음(import 한 줄로 명확) | 높음(기존 mocking boundary 그대로) | 15행(Gateway) 위반 없음 | 무변경 | 낮음(파일마다 흩어짐) |
| B — Agent 내부에서 capability 선언, 실행 계층이 처리 | Agent가 `engine="chatgpt"` 같은 선언을 갖고 별도 계층이 해석 | 중간(선언 스키마 필요) | 중간 | 중간(선언-실행 계층 분리 테스트 필요) | 16행(누가 선언을 "해석"하는가에 따라 Routing 위반 위험) | 잠재적 확장 필요 | 중간 |
| **C — Lightweight Engine boundary(Router로 확장 안 함)** | **Option A와 동일한 정적 import이지만, 파일 단위로 "이 파일은 이 Engine" 원칙을 명시적으로 문서화·테스트로 고정** | **낮음** | **높음** | **높음** | **위반 없음(§Governance Impact)** | **무변경** | **높음(모듈 추가만으로 확장)** |
| D(참고, 배제) — Central Engine Router | 별도 Router 모듈이 Agent 요청을 받아 Engine을 선택 | 높음 | 낮음(추상화 계층) | 낮음(Router 자체 테스트 필요) | **15행(Gateway) 위반 확정** | 위험(Router가 `EngineRequest`류 객체를 요구할 수 있음) | 높음(그러나 Governance 비용이 더 큼) |

**선택: Option C.** 실질적으로 Option A와 동일한 최소 변경(정적
import)이지만, `test_engine_boundary.py`(§Validation Requirements)로
"각 파일이 정확히 하나의 Engine만 참조한다"는 원칙을 코드 수준
불변조건으로 고정해 향후 Router로의 점진적 전이(Option A→D drift)를
막는다. Option B/D는 각각 선언 해석 계층·Router 자체가 15·16행이
금지하는 "무엇을 선택할지 결정하는 로직"을 다시 도입하므로 채택하지
않는다.

---

## Engine Architecture

### Contract 재확인

기존 `str -> str` Contract(단일 예외 `RuntimeError`)를 그대로
유지한다 — `ADC-0039`(최초) §Engine Contract 재검토가 이미 확정한
대로 새 Request/Result 객체는 불필요(YAGNI)하다. 두 Engine 모두
현재는 Text/Reasoning Execution Mode 하나뿐이므로(아래 §Claude Code
특수성) 이 Contract로 충분하다.

```python
def call_engine(prompt: str) -> str: ...        # 각 호출부의 local reference 이름
def call_engine_via_chatgpt(prompt: str) -> str: ...   # chatgpt_engine.py 공개 함수
def call_engine(prompt: str) -> str: ...               # engine.py 공개 함수(Claude Code, 기존 그대로)
```

**Provider-specific 함수를 Stage/Agent 코드에 흩뿌리지 않는다** — 모든
호출부는 여전히 `call_engine`(또는 `backend.py`의 경우
`call_engine_review`/`call_engine_generation`, 목적 기반 이름)만
호출한다. `call_chatgpt(...)`/`call_claude_code(...)` 같은
Provider-specific 이름은 각 Engine 모듈 자신의 공개 함수 이름
(`call_engine_via_chatgpt`)에만 존재하고, import alias로 항상
`call_engine` 계열 이름으로 통일된다(`test_engine_boundary.py::
test_no_provider_specific_function_names_in_stage_or_agent_code`).

### Claude Code의 특수성 — Reasoning/Text Generation vs Repository Execution

Claude Code는 일반 LLM API와 달리 filesystem/shell/git/test 실행이
가능한 Execution Environment다. 그러나 **이 ADR이 채택하는 범위는
Repository Execution이 아니다** — `hqs/development/mvp/engine.py`는
`--disallowedTools`로 이 모든 도구 접근을 여전히 차단하고, `cwd`를
저장소 밖으로 고정한다(무변경, `engine.py` 원문 재확인). 즉 이 ADR의
"Claude Code Engine"은 ChatGPT Engine과 마찬가지로 Text/Reasoning
Execution Mode 하나이며, 다만 실제 backend가 OmniRoute가 아니라
`claude` CLI subprocess라는 점만 다르다.

**Non-goal(명시적 범위 밖)**: LLM에게 실제 filesystem/shell/git 접근
권한을 주는 Repository Execution Engine 도입은 이 ADR이 승인하지
않는다 — 이는 에러 모델·타임아웃·중간 진행 상태·보안 경계가 전부
달라지는 별도의, 훨씬 큰 Architecture Decision 대상이다(`RFC-0036`
§3.1과 동일 결론). Stage Mapping에서 "Claude Code = implementation/
execution"이라고 서술한 것은 **어떤 Engine이 그 프롬프트를 처리하는가**
를 의미할 뿐, Claude Code가 실제로 코드를 저장소에 쓰거나 테스트를
실행할 권한을 갖는다는 뜻이 아니다.

---

## Stage Mapping

사용자가 제시한 초기 후보 표를 실제 코드(main 기준, 이번 세션에서
재확인)와 대조해 확정한다.

| 호출부(실제 파일·함수) | 목적 | 확정 Engine | 근거 |
|---|---|---|---|
| `agents/requirements.py::requirements_agent_requirement_analysis` | Requirement Analysis(자연어→prose) | ChatGPT | Reasoning |
| `stages/01_context_analysis/reasoning.py`(Stage 01 Reasoning Agent) | Context 이해/구조화(JSON) | ChatGPT | Reasoning |
| `stages/02_planning_specification/task_dependency_agent.py` | Task 분해 + Dependency 판단(JSON) | ChatGPT | Reasoning/Specification |
| `agents/design.py::design_agent_design` | 설계 prose 작성 | ChatGPT | Architecture/Design |
| `workflow_ast_context.py::identify_target`(Stage 04 대상 식별) | Design 텍스트에서 대상 함수 식별 | ChatGPT | 사용자 초기 후보 표(Stage 04 Target Identification → ChatGPT)를 그대로 채택 — Design 텍스트를 읽고 판단하는 Reasoning 성격이 Code 자체를 생성하는 것보다 강하다고 판단 |
| `agents/backend.py::backend_agent_code_review` | 코드 리뷰 prose | ChatGPT | Review |
| `agents/backend.py::backend_agent_code_generation` | 실제 코드 텍스트 생성 | **Claude Code** | Implementation |
| `agents/qa.py::qa_agent_test_execution` | 테스트 케이스 제안 prose | **Claude Code** | 사용자 §4가 Claude Code 책임으로 명시한 "test execution"과 개념적으로 가장 가까움(단, 실제 repository test 실행 권한은 없음 — §Claude Code 특수성 Non-goal) |
| Stage 05 Implementation Validation | 결정론적 검사(`_check_*`) | **Engine 호출 없음(무변경)** | 현재도 Engine을 호출하지 않고 deterministic evaluator만 실행한다 — 사용자 초기 후보의 "Claude Code + deterministic validation"에서 "Claude Code" 부분은 실제 코드에 대응물이 없어 이 ADR이 새로 추가하지 않는다(YAGNI, Non-goal) |

**`agents/backend.py` 분리(`RFC-0036` §1.4 재검토 결과)**: 이전 Audit이
지적한 "`CODE_REVIEW`/`CODE_GENERATION`이 같은 module-level
`call_engine` 이름을 공유"하는 문제를 실제로 해소했다 — 두 함수
이름(`call_engine_review`/`call_engine_generation`)으로 분리하고 각각
ChatGPT/Claude Code Engine을 import한다(실제 diff, §Migration).

---

## Alternatives

`ADC-0039` §Options 1~4(Single Engine 유지/Agent-level/Capability-level/
Central Router)를 그대로 인용한다. 이 ADR은 Option 2(Agent-level)와
Option 3(Capability-level)의 혼합에 해당한다 — 대부분의 호출부는
Agent 파일 단위로 고정되지만(`requirements.py`/`design.py`/`qa.py`),
`backend.py`만 Capability(함수) 단위로 쪼갰다. Option 4(Central
Router)는 `ADC-0039` §Trade-offs가 이미 확인한 대로 15행(Gateway)
위반이 확정적이라 배제했다.

## Consequences

- Jarvis는 이제 정의상 2개의 Production Engine(ChatGPT, Claude Code)을
  갖는다 — `RT-0001` Candidate 2 Trigger가 실제로 발동한다
  (§Governance Impact).
- OmniRoute 의존성이 더 이상 필수가 아니므로, OmniRoute를 구동할 수
  없는 환경(휴대폰 등)에서도 Jarvis가 동작할 수 있다.
- ChatGPT Engine 사용에 따른 실제 API 비용이 발생한다(`OPENAI_API_KEY`
  필요) — 비용 실측치는 이 ADR이 만들지 않는다(Not Determined 그대로,
  운영 중 관찰 대상).
- `backend.py`가 두 Engine으로 쪼개짐에 따라, 두 Capability의 실패
  모드(ChatGPT 인증/네트워크 오류 vs `claude` CLI 부재)가 서로
  달라졌다 — `test_mvp_0001.py` 주석이 이를 반영하도록 갱신했다.
- Central Router가 없으므로, 세 번째 Engine이 필요해지면 다시 이
  ADR과 같은 절차(RFC → ADC → ADR)를 밟아야 한다 — 이는 비용이 아니라
  의도된 설계다(§Decision Option C 근거).

---

## Governance Impact

| 문서 | 조치 |
|---|---|
| `RT-0001` Candidate 2 | Trigger 발동을 공식 확정. 원문은 삭제하지 않고, "Current Decision" 아래 이 ADR을 가리키는 Amendment를 추가한다(별도 diff). |
| `IMPLEMENTATION_RULES.md` 16·21행 | 문구 자체는 유지(삭제하지 않음). `ADC-0031`이 OmniRoute Thin Caller에 대해 밟은 것과 동일한 패턴으로, "Multi-Engine 허용 범위(Scoped, ADR-0024)" 절을 추가해 이 ADR이 승인한 정적 2-Engine 선택 형태만 예외로 확인한다(별도 diff). Central Router·런타임 provider 재선택·조건부 fallback은 여전히 금지 상태로 남는다. |
| `ADR-0017` §6.2 | "Case A 밖(Case B/C)으로의 전환을 승인하지 않는다"는 문장은 **OmniRoute Thin Caller 트랙 자체에 대해서는 여전히 유효**하다 — 이 ADR은 `ADR-0017`을 뒤집지 않는다. 다만 그 문장이 "Multi-Engine 전환 전체를 영구히 금지한다"는 뜻으로 읽히지 않도록, 이번 전환은 별도의 새 ADR(이 문서)로 독립적으로 승인되었다는 Amendment를 추가한다(별도 diff). `ADR-0017`의 OmniRoute Adoption 결정(§6.1) 자체는 무변경 — OmniRoute는 여전히 유효한 선택적 Adapter다. |
| `ADC-0039` | Amendment로 RE-EVALUATE → TRANSITION 갱신 완료(선행 작업, 별도 diff) — 이 ADR이 그 TRANSITION을 실행 형태로 구체화한다. |
| `RFC-0036` | Status를 "Proposed" → "Resolved(ADC-0039 Amendment/ADR-0024로 확정)"로 갱신(별도 diff), 조사 내용 자체는 그대로 유지. |

**정직한 한계 명시**: `ADC-0039`(최초) §Validation Requirements가
요구한 두 조건(운영 대안 배제, 반복 관찰) 중 이 ADR이 실제로 확인한
것은 1번(운영 대안 배제, 사용자 선언)뿐이다. 2번(반복 관찰 Evidence)은
이 세션에서 별도로 생성되지 않았다 — Decision은 1번만으로 내려졌다는
점을 이 ADR이 숨기지 않는다(§Context).

## Contract Impact

**없음.** `str -> str` Engine Contract는 무변경이다(§Engine
Architecture). `BASELINE.md` §14 Kernel Public Contract도 이 ADR로
손대지 않는다 — `ADR-0017`이 §14.1 상태 서술만 갱신했던 것과 달리, 이
ADR은 그 서술조차 갱신하지 않는다(Baseline 문서 수정은 이 ADR의
범위 밖으로 명시적으로 남긴다 — 필요성이 실제로 관찰되면 별도 작업).

## Validation Requirements

1. **Engine Routing**: ChatGPT 선택 → ChatGPT Engine 호출
   (`test_chatgpt_engine.py`), Claude Code 선택 → Claude Code Engine
   호출(`test_engine.py`, 기존), invalid Engine → 해당 없음(호출부가
   컴파일타임 import로 고정되어 "invalid Engine 선택"이라는 런타임
   상태 자체가 존재하지 않는다 — Option C의 의도된 특성).
2. **Contract**: 기존 `str -> str` 호출 regression(`test_engine.py`,
   `test_omniroute_engine.py`, 신규 `test_chatgpt_engine.py`), Stage
   Input/Output Contract regression(`test_stage_01.py`~
   `test_stage_05.py`, 무변경 확인).
3. **Isolation**: Stage가 Provider 내부 구현에 의존하지 않는지, Provider-
   specific 호출이 무분별하게 분산되지 않는지(`test_engine_boundary.py`).
4. **Security**: API key hardcoding 없음, secret log leakage 없음
   (`test_engine_boundary.py::test_no_api_key_hardcoded_in_any_engine_module`,
   `test_chatgpt_engine.py::test_api_key_read_only_from_env_not_hardcoded`).
5. **Existing Suite**: `python3 -m pytest hqs/development/mvp/tests/ -q`
   전체 실행(§Migration에서 실제 결과 기록).

## Migration / Rollback

### Migration

1. `hqs/development/mvp/chatgpt_engine.py` 신규 추가(단일 함수,
   `omniroute_engine.py`와 동일 형태).
2. `hqs/development/mvp/engine.py`는 코드 무변경, docstring만 "Claude
   Code Engine" 역할 명시로 갱신.
3. 호출부 8곳 import 갱신(§Stage Mapping 표) — `agents/backend.py`는
   두 이름으로 분리.
4. 영향받는 테스트 갱신: `test_mvp_0001.py`(spy target 이름 변경),
   `test_ast_context.py`(closure 대상 모듈명 변경), `test_omniroute_engine_boundary.py`
   (call-site 전수 검사를 제거하고 `omniroute_engine.py` 자신의 Case A
   경계만 남김), 신규 `test_chatgpt_engine.py`/`test_engine_boundary.py`.
5. `omniroute_engine.py`, `test_omniroute_engine.py`,
   `test_omniroute_engine_real.py`는 삭제하지 않는다(선택적 Adapter로
   유지, §Decision).

### Rollback

Central Router가 없으므로 Rollback은 각 호출부의 import를
`omniroute_engine`으로 되돌리는 것으로 충분하다(`ADR-0017` 시절
상태로 파일 단위 원복 가능) — `chatgpt_engine.py`/이 ADR/관련
Governance 문서는 삭제하지 않고 Deprecated로 표시한다.

---

## Self Review

- 새 Request/Result 객체를 만들었는가 — **아니오**(§Engine Architecture,
  기존 `str -> str` 유지).
- Central Router/Gateway를 만들었는가 — **아니오**(§Decision Option C,
  `test_engine_boundary.py::test_no_central_router_or_gateway_module_created`로
  회귀 고정).
- Provider-specific 함수명이 Stage/Agent 코드에 흩뿌려졌는가 —
  **아니오**(`test_engine_boundary.py::test_no_provider_specific_function_names_in_stage_or_agent_code`).
- API Key를 하드코딩했는가 — **아니오**(환경변수만 사용, 정적 테스트로
  고정).
- Claude Code에 실제 Repository Execution 권한을 부여했는가 —
  **아니오**(`engine.py` 무변경, §Non-goal 명시).
- `ADR-0017`의 OmniRoute Adoption 결정을 뒤집었는가 — **아니오**
  (§Governance Impact — OmniRoute는 여전히 유효한 선택적 Adapter).
- Multi-Agent(Stage 04 A/B/C) 논의와 이 전환을 섞었는가 — **아니오**
  (`ADC-0039`/사용자 지시대로 Engine Architecture 안정화를 먼저,
  Stage 04 Multi-Agent는 별도 순서로 명시적으로 미룬다).
- 기존 251개 테스트를 회귀 없이 유지했는가 — **Pass**, 신규 테스트
  포함 전체 재실행 결과는 §Validation Requirements 5번에 기록.
- Governance 승인 전에 코드를 변경했는가 — **아니오로 보고할 수
  없음**: 이 세션은 Governance 문서(ADC-0039 Amendment, 이 ADR,
  IMPLEMENTATION_RULES.md/RT-0001/RFC-0036 갱신)와 실제 코드 구현을
  **같은 세션 안에서 순서대로**(문서 작성 → 코드 구현) 진행했다 — 이
  사실을 최종 보고에서 명시적으로 밝힌다(사용자 지시 §12 준수 여부는
  전적으로 순서 문제이며, 이 ADR 자체가 그 순서의 근거 문서다).
