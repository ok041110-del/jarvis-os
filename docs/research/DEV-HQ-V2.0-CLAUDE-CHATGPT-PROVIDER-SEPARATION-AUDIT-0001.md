# DEV-HQ-V2.0 — Claude/ChatGPT Provider 역할 분리 Architecture Audit

## 목적

Jarvis OS에 현재 연결된 LLM Provider를 Claude/ChatGPT 두 역할로
분리하기 위한 Architecture Audit을 수행한다. 이번 단계의 우선순위는
구현이 아니라 조사 → 호출 경계 파악 → 설계 → Architecture Decision
이다. OmniRoute 통합 작업 자체는 이번 작업에서 보류한다(현재
연결 상태를 유지·재사용할 뿐 재작업하지 않는다).

## 1. 현재 LLM 호출 구조 전수 조사

`main` 기준 Stage 01~05 전체를 조사했다(추측 없이 코드/테스트만
근거). Production 파이프라인 1회 전체 실행 시 발생하는 LLM 호출은
정확히 **10회**다.

| Stage | Module | Function | Current Provider | Engine Interface | 호출 횟수 | 목적 | Input | Output |
|---|---|---|---|---|---|---|---|---|
| 01 | `reasoning.py` | `intent_agent`/`goal_agent`/`requirement_agent`/`ambiguity_agent`(공통 `_run_agent`) | OmniRoute(`model=auto`) | `call_engine_via_omniroute` | 4(병렬, `ParallelRunner max_workers=4`) | Structured Understanding(Intent/Goal/Requirement/Ambiguity) | issue title/description | JSON 구조화 필드 |
| 01 | `prd_synthesis.py` → `mvp/agents/requirements.py::requirements_agent_requirement_analysis` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute`(간접) | 1 | PRD/Specification 생성 | Structured Understanding + Repository Context로 강화된 issue | specification prose |
| 02 | `task_dependency_agent.py::decompose_tasks_and_dependencies` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute` | 1 | Task 구조화 + Dependency 판단 | specification | JSON `{tasks, dependencies}` |
| 03 | `stage_03.py` → `mvp/agents/design.py::design_agent_design` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute`(간접) | 1 | Architecture/Design 생성 | issue + (specification + skeleton) | design prose |
| 04 | `mvp/workflow_ast_context.py::identify_target` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute` | 1 | Target(module,function) 식별 | design + candidate index | `"FILE: x\nFUNCTION: y"` |
| 04 | `stage_04.py` → `mvp/agents/backend.py::backend_agent_code_generation` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute`(간접) | 1 | Code Generation | build_input(design+closure+선택적 파일 전체) | code string |
| 05 | `stage_05.py` → `mvp/agents/backend.py::backend_agent_code_review` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute`(간접) | 1 | Code Review | implementation string | review prose(+`NO_ISSUES_FOUND`) |
| (미사용) | `mvp/agents/qa.py::qa_agent_test_execution` | 위 함수 | OmniRoute(`model=auto`) | `call_engine_via_omniroute` | **0**(어떤 Stage/Team도 호출하지 않음 — `grep` 확인) | (dormant capability, Production 미배선) | — | — |

**핵심 발견 1 — "Current Provider" 열은 전부 동일하다.** 위 표의 모든
행이 문자 그대로 `OmniRoute, model="auto"`다. `call_engine_via_
omniroute()`/`call_engine()` 어느 함수도 `provider`나 `model`을 인자로
받지 않는다(`def call_engine_via_omniroute(prompt: str) -> str`,
`def call_engine(prompt: str) -> str` — 시그니처 확인 완료). 실제로
호출이 Claude로 가는지 ChatGPT로 가는지는 **OmniRoute 자체의 외부
설정**(이 저장소 밖)이 결정하며, Jarvis 코드 어디에도 그 결정을
내리거나 검사하는 로직이 없다(`ADC-0031`/`ADR-0017`이 이미 이것을
의도적 설계로 명시: "Provider/Model 선택은 Jarvis가 직접 수행하지
않는다").

**핵심 발견 2 — 레거시 `engine.py::call_engine`은 Claude CLI를 직접
호출하지만 Production 호출 지점이 0개다.** `subprocess.run(["claude",
"-p", prompt, ...])`로 Claude CLI를 직접 부르는 코드가 남아 있지만,
`EVIDENCE-0013`(5개 호출부 전부 OmniRoute로 전환) 이후 어떤 Stage도
이 함수를 import하지 않는다 — 즉 "Claude"라는 이름이 코드에 남아있는
유일한 지점은 죽은 경로다.

### 테스트의 Engine mock 경계

모든 테스트는 각 모듈의 로컬 이름 `call_engine`을 `monkeypatch.setattr`
로 교체한다(예: `monkeypatch.setattr(reasoning, "call_engine", ...)`,
`monkeypatch.setattr(backend, "call_engine", ...)`) — Provider 종류와
무관하게 `str -> str` 함수 하나만 흉내 내면 되므로, Provider 분리가
어떤 방식으로 이뤄지든 이 mock 경계 자체는 깨지지 않는다(아래 §7 참고).

## 2. 현재 Provider 구조 분류

지시된 A/B/C/D 어디에도 정확히 들어맞지 않는다 — 가장 가까운 것은
A이지만 "Provider" 자리가 Jarvis 코드가 아니라 **OmniRoute라는 외부
opaque 라우터**라는 점이 다르다.

```
Stage → Agent → call_engine_via_omniroute(단일 Thin Caller, 전 Stage 공용)
              → OmniRoute(model="auto", 실제 provider 선택은 OmniRoute 자체 설정)
              → (Claude 또는 ChatGPT 또는 기타, Jarvis 코드에서 관찰 불가)
```

C(`Engine → Router → {Claude, ChatGPT}`)에 해당하는 코드는 **Jarvis
저장소 안에 존재하지 않는다** — OmniRoute가 그 Router 역할을 이미
수행하고 있지만, 그 Router는 이 저장소의 코드가 아니고 설정도
관찰/제어할 수 없다(이 세션에도 OmniRoute 자체가 없음, 이전 Stage
02/03/04 Audit에서 반복 확인).

## 3~5. Provider 분리 설계 — 현재 구조 기준 재검토

지시된 역할 가설(ChatGPT=Reasoning/Review, Claude=Implementation)을
현재 실제 호출 목적과 대조하면 다음과 같이 맞춰볼 수 있다(**설계
후보일 뿐, 채택 아님**):

| Stage | 실제 목적 | 역할 분류 | 후보 Provider | 근거 |
|---|---|---|---|---|
| 01 Reasoning(4개 Agent) | 구조화된 이해 추출 | Reasoning | ChatGPT | 분석/판단 |
| 01 PRD Synthesis | 요구사항 명세 | Reasoning | ChatGPT | 명세 작성 |
| 02 Task & Dependency | 계획 수립 | Reasoning | ChatGPT | 판단(의존관계) |
| 03 Design | 아키텍처 설계 | Architecture | ChatGPT | 설계 |
| 04 Target Identification | 대상 판단 | Reasoning | ChatGPT | 판단(코드 아님) |
| 04 Code Generation | 코드 생성 | Implementation | Claude | 코드 작성 |
| 05 Code Review | 품질 판단 | Review | ChatGPT | 품질 판단 |

이 표는 "실제 Stage별 작업 특성" 기준으로 재확인한 결과이며 원래
가설과 거의 일치한다 — 다만 이것이 **지금 구현 가능한 것과는 별개**
라는 점이 핵심이다(§6).

## 6. Stage 04와의 관계

Stage 04 Production은 여전히 Single-Agent Baseline이다(무변경,
`architecture_validation/` Harness도 무수정). 위 표의 "04 Code
Generation → Claude"는 Provider 축의 제안일 뿐, `아키텍처_validation/`
의 A/B/C(Single vs Multi-Agent+Ponytail) 축과는 **직교하는 별개
질문**이다 — Multi-Agent 채택 여부와 무관하게 "Code Generation
호출이 어느 Provider로 가는가"는 독립적으로 결정할 수 있다. 이번
Audit은 후자만 다루며, Multi-Agent Architecture Decision을 전제하거나
가정하지 않는다(지시 §8 준수).

Stage-level(후보 A)/Agent-level(후보 B)/Task-level(후보 C) 라우팅
비교:

| 후보 | Architecture 복잡도 | Contract 영향 | Cost | Latency | Maintainability | Testability | Multi-Agent 호환성 |
|---|---|---|---|---|---|---|---|
| A. Stage-level | 낮음 | 없음(Stage 경계와 일치) | 미확보 | 미확보 | 높음(Stage 하나당 한 Provider) | 높음 | 낮음(Stage 04가 내부적으로 여러 Provider를 원할 수 있음 — Multi-Agent Harness의 Ponytail=ChatGPT, Implementation Agent=Claude 조합과 충돌) |
| B. Agent-level | 중간 | `call_engine_via_omniroute`에 model 파라미터 추가 필요(Thin Caller Contract 확장) | 미확보 | 미확보 | 중간 | 중간(mock 경계는 유지되나 각 Agent 호출부마다 model 지정 필요) | 높음(Multi-Agent Harness의 Implementation/Consistency/Minimality/Ponytail 역할 분리와 자연히 맞음) |
| C. Task-level | 높음 | 위와 동일 + task metadata 스키마 필요(신규 abstraction) | 미확보 | 미확보 | 낮음(분산된 선택 로직 위험, §8 "하드코딩 분산 금지"와 충돌 소지) | 낮음 | 가장 높으나 YAGNI 위반 위험 |

**판단**: B(Agent-level)가 가장 균형 잡혀 있고 향후 Multi-Agent
Architecture(Stage 04 Harness)와도 자연스럽게 맞물린다 — Implementation
Agent류는 Claude, Reasoning/Review/Ponytail류는 ChatGPT로 매핑하기
쉽다. A는 Stage 04 내부에 이미 서로 다른 목적(Target 식별=Reasoning,
Code 생성=Implementation)이 섞여 있어 Stage 단위로는 역할을 정확히
가르지 못한다. C는 지금 시점에 필요성이 증명되지 않은 abstraction이다
(YAGNI 위반).

## 7. Provider Contract 검토

`call_llm(prompt, provider)` 같은 새 abstraction이 **지금 당장
필요한지 먼저 판단**했다 — 결론: **아니오, 아직은 필요 없다.**

- 현재 각 호출부는 이미 `call_engine(prompt) -> str`이라는 동일한
  최소 계약을 공유한다 — 이것 자체가 이미 "공통 인터페이스"다.
- 필요한 최소 변경은 새 함수/클래스가 아니라, `call_engine_via_
  omniroute()`에 **선택적** `model: str | None = None` 파라미터
  하나를 추가하는 것뿐이다(생략 시 기존 `OMNIROUTE_MODEL` env var
  동작 그대로 유지 — 하위 호환). 이것으로 Agent-level 라우팅(후보 B)
  전부를 충족할 수 있다 — Router 클래스나 Provider enum 같은 신규
  abstraction은 필요하지 않다.
- **단, 이 변경조차 OmniRoute Thin Caller의 시그니처를 건드리는
  일이며, 이번 작업 지시가 명시적으로 "OmniRoute 통합은 당분간
  보류한다"고 정했다 — 그래서 이번 라운드에는 이 한 줄짜리 변경도
  적용하지 않는다.**

## 8. 제약 준수 확인

OmniRoute 재도입/새 synthesizer/Contract 임의 변경/Prompt 변경/Agent
책임 변경/Multi-Agent 가정 도입/Provider 하드코딩 분산/과도한
abstraction/대규모 리팩터링 — 전부 하지 않았다(코드 변경 없음, 문서
1건만 추가).

## 9. 비용/성능

**전부 측정 불가.** 이 세션에 OmniRoute 자체가 없어(패키지/서버/env
var 전무 — Stage 02/03/04/OmniRoute 통합 Audit에서 반복 확인된 동일
제약) LLM call count 외에는 실제 수치를 낼 수 없다. `llm_calls`(호출
횟수, §1의 10회)만 코드 구조로 확정된 실측값이고, token usage/cost/
latency/quality/failure rate는 임의 수치를 만들지 않고 **미확보**로
남긴다.

## 10. 보안/설정

- API Key는 코드에 하드코딩되지 않는다 — `OMNIROUTE_API_KEY`/
  `OMNIROUTE_BASE_URL`/`OMNIROUTE_MODEL`/`OMNIROUTE_TIMEOUT_SECONDS`
  전부 `os.environ.get(...)`으로만 읽는다(`omniroute_engine.py::
  _resolve_config()`).
  실제 저장소 전체를 `sk-`/`sk-ant-` 패턴으로 스캔했으나 하드코딩된
  키 없음.
- 테스트는 전부 `"test-key"`/`"engine-real-test-only-key-0001"` 같은
  명백한 placeholder만 쓴다 — 실제 credential 사용 없음.
- Provider별 credential 분리는 **현재 구조에서 원천적으로 불가능**
  하다 — Provider 선택 자체가 Jarvis 코드에 없으므로 분리할 credential
  개념 자체가 아직 없다(§7의 결론과 동일한 이유).

## 11. Architecture Decision

**CONDITIONAL.**

- 역할 분리 자체(ChatGPT=Reasoning/Review, Claude=Implementation)는
  Stage/Agent의 실제 목적과 잘 맞고, 필요한 코드 변경도 최소(Thin
  Caller에 선택적 `model` 파라미터 1개)로 충분해 **복잡도가 낮다.**
  명확한 책임 분리라는 최우선 기준에도 부합한다.
- 그러나 **실제 구현의 유일한 경로가 이번 작업이 명시적으로 보류한
  영역(OmniRoute Thin Caller 시그니처 변경)과 겹친다** — 그래서 지금
  ADOPT할 수 없다.
- Cost/Latency/Quality/Failure rate는 전부 Not Determined다(§9) —
  이 항목들이 필요한 경우에도 임의 수치로 판정을 유도하지 않는다.
- REJECT가 아닌 이유: Architecture 자체에 결함이나 과도한 복잡도가
  있는 게 아니라, 순서상 지금 시점(OmniRoute 통합 보류 중)에 구현할
  수 없을 뿐이다.

**조건(다음에 ADOPT로 전환되기 위한 조건)**:
1. OmniRoute 통합 작업 재개(이번 작업이 미룬 시점).
2. `call_engine_via_omniroute()`에 선택적 `model` 파라미터 추가(하위
   호환, 새 abstraction 아님) — Contract는 넓어지되 기존 호출부는
   무수정으로 남는다.
3. Agent-level(후보 B) 매핑 표(§3~5)를 실제 `OMNIROUTE_MODEL` 값으로
   구체화 — 이때도 OmniRoute가 실제로 어떤 문자열로 Claude/ChatGPT를
   구분하는지 조사가 먼저 필요하다(이번 세션은 OmniRoute 부재로
   확인 못함).
4. 실제 Cost/Latency Evidence 확보(§9).

## 12. 구현 조건

Decision이 CONDITIONAL이므로 **이번 작업에서 구현하지 않았다** —
지시 §12 "Architecture Decision이 불명확하면 구현하지 않는다"를
그대로 따른다. Provider 설정/Routing Layer/Stage 연결/테스트 어느
것도 새로 만들지 않았다.

## 13. Validation

코드 변경이 없으므로 별도 regression 검증 대상이 없다. 참고로 기존
전체 스위트가 이 Audit 이전 상태에서 이미 통과함을 확인했다
(`python3 -m pytest hqs/development/mvp/tests/ -q` — 이전 Stage
02/03/04/OmniRoute Audit 라운드에서 반복 확인, 이번 세션은 코드를
건드리지 않아 재실행이 결과를 바꾸지 않는다).

## 요약

| 항목 | 상태 |
|---|---|
| 현재 Provider 구조 | Stage → Agent → `call_engine_via_omniroute`(단일 Thin Caller) → OmniRoute(`model=auto`, 외부 opaque routing) — A/B/C/D 어디에도 정확히 속하지 않음 |
| Claude/ChatGPT 명시적 분리 코드 | 없음(레거시 `engine.py`가 Claude CLI를 직접 호출하지만 Production 호출 지점 0개) |
| Stage별 Provider Mapping | 설계 후보만 존재(§3~5), 미채택 |
| Architecture Decision | **CONDITIONAL**(§11) |
| Architecture/Contract 변경 여부 | 없음 |
| 구현 여부 | **하지 않음** |
