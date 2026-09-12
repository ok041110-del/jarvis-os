# RFC-0036: ChatGPT Engine / Claude Code Engine 분리 — Freeze 경계 확인 (구현 아님)

**Status**: Proposed (검토 대상, 결정 아님 — 아래 §6이 이 RFC의 핵심 결론이다)
**Author**: Claude Code (사용자 요청에 따른 Architecture Audit 결과)
**대상**: `hqs/development/mvp/engine.py`, `hqs/development/mvp/omniroute_engine.py`,
`hqs/development/mvp/agents/*.py`, `hqs/development/stages/01_context_analysis/reasoning.py`,
`hqs/development/stages/02_planning_specification/task_dependency_agent.py`,
`hqs/development/mvp/workflow_ast_context.py`, `hqs/development/IMPLEMENTATION_RULES.md`
금지 표(15·16·21행), `docs/governance/rt/RT-0001.md` Candidate 2, `docs/architecture/core/ADC-0031`,
`docs/architecture/core/ADR-0015`·`ADR-0017`.

**요청 배경**: 사용자의 실제 실행 환경(휴대폰)에서 OmniRoute 서버를
직접 구동하기 어렵다는 제약을 근거로, Jarvis OS의 LLM Engine 실행
대상을 ChatGPT Engine / Claude Code Engine 두 가지로 분리하고, Stage/
Agent가 작업 목적에 따라 이 중 하나를 명시적으로 선택하도록 하는
Architecture를 요청받았다. OmniRoute는 이 작업 범위에서 제외한다.

**이 RFC가 확정하지 않는 것**: Contract 변경, Engine 코드 추가/수정,
Stage/Agent의 실제 Provider 배정. 이 RFC는 "그 Architecture가 지금
바로 구현 가능한가"를 조사한 결과, **구현 불가 — 기존 Freeze와
직접 충돌**이라는 결론에 도달했다(§6). 그래서 코드 변경 없이 이
RFC만 제출한다.

---

## 1. 현재 구조 조사 (실제 코드 근거)

main(`50db4c6`) 기준 `hqs/development/mvp/`, `hqs/development/stages/`
전수 조사.

### 1.1 Engine Contract

```python
def call_engine(prompt: str) -> str: ...
```

`prompt: str` 하나만 받고 `str`을 반환한다. 실패는 예외 하나
(`RuntimeError`)로만 표현한다. `provider`/`model`/`engine` 같은 선택
파라미터는 코드 어디에도 없다. 이 Contract는 문서(주석)로만 존재하고
`Protocol`/ABC로 강제되지 않는다 — 두 구현체가 우연이 아니라
`ADC-0031`/`ADR-0017`이 의도적으로 강제한 "단일 함수" 모양을 따른다.

이 Contract를 독립적으로 구현하는 모듈이 이미 2개 존재한다.

| 모듈 | 함수 | 실제 백엔드 | Production 호출 지점 수 |
|---|---|---|---|
| `mvp/engine.py` | `call_engine` | `claude` CLI subprocess(`--disallowedTools`로 전 도구 차단, `cwd`를 저장소 밖으로 고정) | **0**(모든 호출부가 아래 omniroute로 전환 완료, `EVIDENCE-0013`) |
| `mvp/omniroute_engine.py` | `call_engine_via_omniroute` | OmniRoute OpenAI-compatible HTTP endpoint | **7** |

두 모듈은 서로를 import하지 않는다(`omniroute_engine.py` 자체 docstring이
이를 명시). `engine.py`는 이미 사실상 **"Claude Code CLI를 텍스트 전용
함수로 감싼 Engine"** 이다 — 이번 요청의 "Claude Code Engine" 후보와
개념적으로 동일한 것이 이미 코드에 있다(§4).

### 1.2 `call_engine()`의 책임

프롬프트 1개를 완성된 텍스트 응답 1개로 바꾸는 것 하나뿐이다.
Retry/Fallback/재시도 정책/Provider 선택/Model 선택 로직이 전혀 없다
— 이는 우연이 아니라 `IMPLEMENTATION_RULES.md` 15·16·17·21행이
명시적으로 금지한 항목이다(§1.4).

### 1.3 OmniRoute Thin Caller는 Contract에 포함되는가, Adapter인가

Adapter다. Contract(`str -> str`, 단일 예외)는 두 구현체 이전부터
암묵적으로 존재했고, `omniroute_engine.py`는 그 Contract를 만족하는
**두 번째 독립 구현체**로 추가됐다 — Contract 자체를 확장하거나
변경하지 않았다(`ADR-0017` §2.1: "새 Architecture Decision이 아니라
`ADC-0031`이 이미 확정한 Case A 정의의 논리적 필연").

### 1.4 Stage/Agent가 Engine 구현을 얼마나 아는가

Stage 코드(`stage_01.py`~`stage_05.py`)는 Engine을 전혀 모른다 —
Agent 함수만 호출한다. Engine을 아는 것은 Agent 모듈 7곳뿐이고, 각
모듈은 파일 최상단 import 한 줄로 정확히 하나의 Engine 구현에
고정된다.

```python
from ..omniroute_engine import call_engine_via_omniroute as call_engine
```

호출부 전수(7곳, 기존 5곳 + `EVIDENCE-0013` 이후 확인된 2곳):

| 파일 | 함수 | 목적(프롬프트 접두) |
|---|---|---|
| `agents/requirements.py` | `requirements_agent_requirement_analysis` | `REQUIREMENT_ANALYSIS` |
| `agents/design.py` | `design_agent_design` | `DESIGN` |
| `agents/backend.py` | `backend_agent_code_review` | `CODE_REVIEW` |
| `agents/backend.py` | `backend_agent_code_generation` | `CODE_GENERATION` |
| `agents/qa.py` | `qa_agent_test_execution` | `TEST_EXECUTION` |
| `workflow_ast_context.py` | `identify_target` | (Stage 04 대상 식별 — AST 후보 색인에서 target 선택) |
| `stages/01_context_analysis/reasoning.py` | Stage 01 Reasoning Agent | Context 이해/구조화 |
| `stages/02_planning_specification/task_dependency_agent.py` | Task & Dependency Agent | Task 분해 + 의존 관계 판단 |

**중요한 발견**: `agents/backend.py` 한 파일 안에 목적이 다른 두 호출
(`CODE_REVIEW`, `CODE_GENERATION`)이 **같은 module-level `call_engine`
이름 하나**를 공유한다. Agent 파일 단위로 Engine을 선택하는 구조를
그대로 쓰면 이 파일만 두 개의 Engine 바인딩(`call_engine_review`,
`call_engine_generation`)으로 쪼개야 한다 — "Agent-level routing"이
매끄럽지 않은 유일한 지점이다.

### 1.5 ChatGPT/Claude Code 추가 시 Contract 변경 필요 여부

**불필요.** 기존 두 모듈과 동일한 모양(`str -> str`, 단일
`RuntimeError`)의 새 모듈을 추가하고, Agent 파일의 import 한 줄만
바꾸면 된다 — `engine.py↔omniroute_engine.py` 전환 때 이미 증명된
패턴 그대로다. `EngineRequest`/`EngineResult` 같은 새 객체, `engine=`
매개변수, Router 클래스는 전부 불필요(YAGNI) — 만들 이유가 없다.

### 1.6 기존 테스트의 mocking boundary

Agent 모듈 로컬 이름을 patch한다(`monkeypatch.setattr(backend,
"call_engine", fake)`, `monkeypatch.setattr(reasoning, "call_engine",
fake)` 등, `test_mvp_0001.py`가 이 경계를 "각 Agent 모듈이 자신만의
`call_engine` local reference를 갖는다"고 명시). 어떤 모듈에서
import했든 이름만 일치하면 되므로, 새 Engine 모듈을 추가해도 기존
mocking boundary는 깨지지 않는다.

---

## 2. 핵심 발견 — 이 요청은 "구현"이 아니라 "Freeze 재검토" 대상이다

`hqs/development/IMPLEMENTATION_RULES.md` 금지 표:

| 행 | 금지 항목 | 원문 |
|---|---|---|
| 15 | Engine Gateway 구현 금지 | 단일 함수로 Engine을 호출하는 것으로 충분하다 |
| 16 | Engine Routing 구현 금지 | **여러 Agent 또는 여러 Engine 중 무엇을 선택할지 결정하는 로직을 만들지 않는다.** MVP는 Engine을 호출하는 함수 하나만 가진다 |
| 21 | Multi Engine 지원 코드 작성 금지 | 단일 Engine 호출로 충분하다 |

그리고 `docs/governance/rt/RT-0001.md` Candidate 2(Engine Gateway):

> **Re-evaluation Trigger**: Engine 수 ≥ 2 (두 번째 Engine이 실제로
> 추가되어 `call_engine()` 호출 지점이 둘 이상의 서로 다른 Engine을
> 대상으로 하게 됨)

`ADR-0017` §2.4는 `omniroute_engine.py` 도입이 이 Trigger를 유발하지
**않는** 이유를 명시했다 — 5개(현재 7개) 호출부 **전부**가 동기화되어
하나의 Engine(OmniRoute)만 대상으로 하기 때문이다(부분 전환 금지,
`EVIDENCE-0013` §5.2, `test_omniroute_engine_boundary.py`의
`test_all_five_existing_call_sites_import_omniroute_engine`이 이를
회귀 검증). 그리고 같은 §2.4는 다음을 명시적으로 못박았다.

> 향후 실제 caller가 [Routing Policy 등] 하나라도 Jarvis 코드 안에
> 판정 로직으로 가져오면, 그 순간 ... Case B로 전환되고, 이 결정도
> 함께 무효화되며 `IMPLEMENTATION_RULES.md`의 금지 표가 그 구현에
> 다시 전면 적용된다 ... **이 ADR은 그 전환을 승인하지 않는다.**

이번에 요청받은 Architecture — Stage/Agent가 ChatGPT Engine과 Claude
Code Engine 중 **작업 목적에 따라 선택**하는 구조 — 는 정의상:

1. 두 번째 Engine이 실제로 추가되고,
2. 호출 지점(7곳)이 하나로 동기화되지 않고 **목적별로 서로 다른
   Engine을 대상으로 하게 되며**,
3. "어떤 Agent가 어떤 Engine을 쓸지"는 **Jarvis 코드(Agent 파일의
   import 선택)가 직접 판정**한다.

이는 RT-0001 Candidate 2의 Trigger 문구("두 번째 Engine이 실제로
추가되어 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로 하게
됨")를 정확히 충족하고, `IMPLEMENTATION_RULES.md` 16행("여러 Engine
중 무엇을 선택할지 결정하는 로직을 만들지 않는다")과 21행("Multi
Engine 지원 코드 작성 금지")을 문자 그대로 위반한다. Import 한 줄
선택이 "Gateway 추상화"가 아니라는 점은 사실이지만, 16행이 금지하는
것은 추상화의 유무가 아니라 **"무엇을 선택할지 결정하는 로직" 자체의
존재**다 — 그 로직이 런타임 `if/else`든 컴파일타임 import 선택이든
동일하게 해당한다.

**결론**: 이것은 CLAUDE.md의 "Frozen Architecture" 규칙 대상이다.

> Architecture / Baseline은 직접 수정하지 않는다. Architecture
> 변경이 필요하면 RFC → ADC → ADR 순서로 제안한다.

그래서 이 문서는 구현이 아니라 그 RFC 단계 자체다. 코드 변경은
Governance 검토 없이 이번 세션에서 진행하지 않는다.

---

## 3. ChatGPT Engine / Claude Code Engine 역할 후보 (참고용 분석, 미확정)

Freeze 재검토가 이뤄질 경우를 대비해 실제 Agent 책임 기준으로만
분석한다(추측 금지 원칙에 따라, "ChatGPT가 더 낫다"는 가정 없이).

| Agent/호출 | 실제 작업 성격(코드 근거) | Reasoning/Review 편향 후보 |
|---|---|---|
| `requirements.py` | 자연어 요구사항 → prose 분석 | Reasoning |
| `reasoning.py`(Stage 01) | Context 이해/구조화(JSON) | Reasoning |
| `task_dependency_agent.py` | Task 분해 + 의존 판단(JSON) | Reasoning |
| `design.py` | 설계 prose 작성 | Reasoning/Architecture |
| `identify_target`(Stage 04) | Design 텍스트에서 대상 함수 식별 | 경계 모호 — 코드 후보 색인을 읽는 작업이라 Reasoning/Implementation 어느 쪽으로도 정당화 가능 |
| `backend_agent_code_generation` | 실제 코드 텍스트 생성 | Implementation |
| `backend_agent_code_review` | 코드 리뷰 prose(같은 파일, 다른 목적) | Review |
| `qa_agent_test_execution` | 테스트 케이스 제안 prose | 경계 모호 — Review와 Implementation 사이 |

이 표가 보여주는 것: 사용자가 제시한 초기 가설("ChatGPT=Reasoning,
Claude=Implementation")은 대체로 코드 근거와 맞지만, **Agent 파일
단위 라우팅으로는 `backend.py`(Review+Generation 혼재)와
`identify_target`/`qa`(경계 모호) 두 지점이 깨끗하게 맞아떨어지지
않는다** — Agent-level routing을 실제로 채택하려면 최소
`backend.py`를 함수 단위로 쪼개는 추가 변경이 필요하다(Contract는
안 바뀌지만 파일 내부 구조는 바뀐다).

### 3.1 Provider vs Execution Mode

현재 코드에 "Repository Execution Engine"(LLM이 파일을 직접 읽고
쓰는 모드)은 **존재하지 않는다**. `engine.py`는 `claude` CLI를
호출하지만 `--disallowedTools`로 Write/Edit/Bash/Read/Glob/Grep/
NotebookEdit/WebFetch/WebSearch를 전부 차단하고 `cwd`를 저장소 밖
(`tempfile.gettempdir()`)으로 고정한다 — 즉 지금의 "Claude Code
Engine" 후보는 이미 순수 텍스트 생성 함수이지 Repository Agent가
아니다. `backend_agent_code_generation`이 만든 코드도 LLM이 직접
파일에 쓰는 게 아니라 텍스트로 반환되어 이후 별도 경로로 소비된다.

**결론**: 지금 채택 가능한 범위는 Provider 두 가지(ChatGPT/Claude)
모두 **Text/Reasoning Execution Mode 하나**뿐이다. "Claude Code →
Repository Execution Engine"이라는 §6(사용자 원 요청) 구도는 현재
코드에 대응물이 없는, 훨씬 더 큰 별도의 Architecture 결정(LLM에게
도구 접근권을 주는 것)이라서 이 RFC 범위 밖으로 명시적으로 뺀다.

### 3.2 Engine Contract 후보

`EngineRequest`/`EngineResult` 같은 객체는 만들 필요가 없다(§1.5).
Freeze가 재검토되어 실제로 채택된다면, 기존과 동일한 `str -> str`
모듈을 하나 더 추가하고 Agent import를 바꾸는 것으로 충분하다.

---

## 4. Architecture Decision

**Decision: 이 시점에는 ADOPT/CONDITIONAL/REJECT 중 어느 것도 아니다
— `INVESTIGATE`(추가 Governance 필요, 실제 코드/Contract 변경
없음).**

- Contract 변경 필요 여부는 **명확히 결정됨: 불필요**(§1.5) — 이
  부분은 Evidence 기반으로 지금 확정 가능하다.
- 반면 "Jarvis 코드가 여러 Engine 중 하나를 선택하는 로직을 가져도
  되는가"는 이번 RFC 혼자 결정할 수 없다 — `IMPLEMENTATION_RULES.md`
  16·21행과 `RT-0001` Candidate 2를 정면으로 재검토하는 것이기
  때문이다. `ADC-0031`이 OmniRoute 도입 때 밟은 것과 같은 절차
  (RFC → ADC → ADR)가 이번에도 필요하다 — 이번엔 "Case A(단일
  Engine 유지)"가 아니라 **"Case B 이상(목적별 정적 Multi-Engine
  선택)"을 새로 정의하고 그 범위를 확정하는 ADC**가 되어야 한다.
- 우선순위(사용자 지시대로 명확한 책임 분리 > 낮은 복잡도 > 낮은
  비용 > 낮은 latency > 확장성)는 이 RFC가 실제 Evidence 없이 임의
  가중치를 매기지 않는다 — ADC 단계에서 다룰 사안이다.

---

## 5. 향후 절차 제안 (실행하지 않음, 제안만)

1. **ADC**: `IMPLEMENTATION_RULES.md` 16·21행에 "목적별 정적
   Multi-Engine 선택(런타임 Provider 재선택/Fallback 없음, Agent
   파일 import 시점에 고정)"을 위한 Scoped 예외를 둘지 판정. `ADC-0031`
   Case A 정의를 확장하거나 새 Case를 정의해야 한다.
2. **ADR**: ADC가 예외를 승인하면, `backend.py` 함수 단위 분리 여부
   포함 실제 Stage/Agent Mapping을 Adoption Review로 확정.
3. 그 이후에만 `chatgpt_engine.py`(신규, `omniroute_engine.py`와
   동일한 형태 — stdlib `http.client`만 사용, OpenAI-compatible
   Chat Completions 형식, 로컬 test double로 검증) 같은 실제 코드
   추가를 진행한다. `engine.py`는 이미 "Claude Code Engine" 역할을
   하므로 새로 만들 필요가 없다(문서상 역할만 명확히 하면 된다).

---

## 6. 이 RFC의 결론 (요약)

- **조사 완료**: 현재 Engine Contract, 책임 경계, mocking boundary,
  Contract 변경 필요 여부(불필요) — 전부 실제 코드 근거로 확인했다.
- **구현하지 않음**: ChatGPT/Claude Code Engine 분리는 `RT-0001`
  Candidate 2 Trigger를 충족시키고 `IMPLEMENTATION_RULES.md` 16·21행과
  정면 충돌한다 — CLAUDE.md Frozen Architecture 규칙에 따라 RFC 단계
  (이 문서)에서 멈추고 ADC/ADR 없이 코드를 바꾸지 않았다.
- **Contract 변경**: 없음(필요하다면 없어도 된다는 것까지만 확정).
- **Architecture 변경**: 없음(제안만, Freeze 그대로 유지).
