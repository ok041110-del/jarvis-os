# Dev HQ Agent Responsibility Decomposition — Experimental Analysis (Phase F-2 확장)

**분류**: Experimental Implementation의 분석 산출물(`ARCHITECTURE_GOVERNANCE.md`
"Experimental Implementation" 절 — "허용: `projects/` 기반... 실험적
구현"의 분석 문서 형태). **코드 구현이 아니다** — 이 디렉터리는
`README.md` 1개만 담는다.

**Owner**: Claude Code(이 세션).

**전제**: `RFC-0024`~`RFC-0030`, `ADC-0032`, `ADC-0033`(Phase A~F-2)의
Defer/Open 판단을 그대로 유지한다. 이 문서는 Agent Domain/Lifecycle/
State/Message/Event/Agent Manager/Runtime/Event Bus/Scheduler/Registry
중 어느 것도 새로 정의·구현하지 않는다. `hqs/development/` Production
코드는 한 줄도 수정하지 않았다(`git status --porcelain` 확인, §13
Validation).

---

## 1. 조사 대상

| 대상 | 확인 방식 |
|---|---|
| `hqs/development/workflow.py` | 원문 읽음 — Stage 01→05 `try/except` 직접 순차 호출 |
| `hqs/development/mvp/` (`project_intelligence.py`, `ast_context.py`, `workflow_ast_context.py`, `omniroute_engine.py`) | 원문 읽음 |
| `hqs/development/mvp/agents/` (`requirements.py`, `design.py`, `backend.py`, `qa.py`, `__init__.py`) | 원문 읽음 |
| `hqs/development/stages/01~05/stage_0N.py` | 원문 읽음 |
| `hqs/development/stages/contracts.py` | 원문 읽음 |
| `hqs/development/mvp/tests/test_stage_0{1..5}.py`, `test_stage_contracts.py` | 존재 확인(`ls`), Stage별 개별 테스트 확인 |
| `AGENT_CAPABILITY_MAP`, `HELLO_SDLC_CAPABILITY_MAP` | `mvp/agents/__init__.py` 원문 대조 |
| `IMPLEMENTATION_RULES.md` | Policy/Registry/Scheduler/Event Bus 금지 표 원문 대조 |
| `CONSTITUTION.md` | Mission/Core Philosophy/SDLC 원문 대조 |
| `docs/architecture/core/RFC-0024~0030`, `ADC-0032`, `ADC-0033` | Phase A~F-2 결론 인용(재조사 아님) |
| Engine 호출 지점 전수 | `grep -rn "call_engine\|call_engine_via_omniroute" hqs/development/mvp/*.py hqs/development/stages/*/*.py`(정의부 제외) — **5곳**(§3 표) |
| Production 회귀 기준선 | `/root/.local/bin/pytest hqs/development/mvp/tests/ -q` → **186 passed, 6 skipped**(변경 전/후 동일, §13) |

## 2. Stage 01~05 Responsibility Map

| Stage | Deterministic Responsibility | LLM/Agent Responsibility | Input | Output | Side Effect | Downstream Dependency | 현재 담당 Agent |
|---|---|---|---|---|---|---|---|
| **01** | `collect_relevant_context`(정규식 키워드 스코어링), `build_context_bundle`, `build_function_candidate_index`, `build_dependency_closure`(전부 AST/정규식) | **없음** | `issue: dict`, `target: tuple\|None` | `directory_structure`, `context_bundle`, `candidate_index`, `target`, `dependency_closure` | 없음(파일 시스템 읽기만) | Stage 02(`context_bundle`), 03(`candidate_index`), 04(`candidate_index`) | 없음 |
| **02** | `_structure_from_context`/`_skeleton_to_text`/`_enrich_issue_with_skeleton`(문자열 재배치) | `requirements_agent_requirement_analysis` 1회 | `issue`, `stage_01_context` | `skeleton`, `specification` | 없음 | Stage 03(`skeleton`, `specification`) | Requirements Agent |
| **03** | `_structure_from_specification`/`_skeleton_to_text`(문자열 재배치) | `design_agent_design` 1회 | `issue`, `stage_01_context`, `stage_02_output` | `skeleton`, `design` | 없음 | Stage 04(`design`) | Design Agent |
| **04** | `_assemble_build_input`(closure 삽입·Exposure Policy 문구 첨부, 문자열 조립) | **`identify_target` 1회**(§3 재분류) + `backend_agent_code_generation` 1회 | `stage_01_context`, `stage_03_output`, `expose_target: bool` | `target`, `implementation`, `expose_target` | 대상 파일 **읽기만**(쓰기 없음) | Stage 05(`implementation`, `target`, `expose_target`) | Backend Agent(명명) + 미명명 Engine 호출 1건 |
| **05** | 4개 결정적 검사(`structural`/`specification_scope`/`design_scope`/`test_execution`), Verdict 결정(`_determine_verdict`) | `backend_agent_code_review` 1회 (+ `qa_agent_test_execution` 정의만 존재, 미호출) | `stage_02_output`, `stage_04_output`, `required_checks` | `VerificationResult`(checks, verdict, code_review) | **대상 모듈 파일을 임시로 덮어쓰고 `finally`로 원복**(`test_execution` 검사) | 없음(마지막 Stage) | Backend Agent(code_review) |

**Stage 06**: `hqs/development/stages/06_devops_release/`에 `README.md`만
존재, `stage_06.py` 없음. `workflow.py`가 호출하지 않음(`RFC-0029`/
`RFC-0030` 재확인, 이 문서도 동일 확인). 이 문서의 Responsibility Map
대상에서 제외.

## 3. 기존 Agent 책임 Map

| Agent | 실제 담당 업무 | 책임이 너무 넓은가 | 다른 책임과 혼합돼 있는가 | 독립 Agent로 분리 가능한 책임 | 그대로 유지해야 할 책임 |
|---|---|---|---|---|---|
| **Requirements Agent**(`requirements_agent_requirement_analysis`) | Issue + Context 골격 → Specification 생성 | 아니오 — 단일 판단(요구사항 분석) | 아니오 — 골격 조립은 Stage 02가 하고 이 함수는 순수 Engine 호출만 | 없음 | 전체 — 단일 책임이 이미 최소 단위 |
| **Design Agent**(`design_agent_design`) | Specification + 골격 → Architecture/Design 생성 | 아니오 | 아니오(02와 동형) | 없음 | 전체 |
| **Backend Agent**(`backend_agent_code_generation` + `backend_agent_code_review`) | **두 가지 다른 판단**을 한 모듈에 담고 있다 — (a) Design → 코드 생성, (b) 코드 → 리뷰(이슈 서술) | **예 — 함수 두 개가 서로 다른 판단**(생성 vs 검토)을 같은 이름(`backend_agent_*`) 아래 갖고 있어, "Backend Agent"라는 하나의 이름이 실제로는 두 개의 서로 다른 전문 역할을 가리킨다 | 예 — 이름은 하나(Backend Agent)지만 실행되는 시점(Stage 04 vs Stage 05)과 판단 종류가 다르다 | **`code_generation`과 `code_review`는 이미 사실상 독립 함수로 분리돼 있다** — "Backend Agent"라는 공유 이름표만 재검토 대상 | 각 함수 자체의 판단 범위(생성/검토 각각)는 유지 — 함수 내부를 더 쪼갤 근거는 없다 |
| **미명명 Target Identification**(`workflow_ast_context.identify_target`) | Design + 후보 인덱스 → (module, function) 식별 | 아니오 — 단일 판단 | 아니오 — Stage 04 안에서 결정적 조립(§2 Stage 04 열)과 분리돼 있다 | **이미 함수로 분리돼 있으나 `mvp/agents/`에 등록되지 않았고 이름도 없다** | 판단 자체(어디를 고칠지)는 Code Generation(무엇을 쓸지)과 명백히 다른 전문성 |
| **QA Agent**(`qa_agent_test_execution`, 미호출) | 코드 + 리뷰 → 테스트 케이스 제안(설계만, 실행 아님) | 아니오 | 아니오 | 이미 분리돼 있으나 **활성화되지 않음**(§2.1 Stage 05 실제 실행 경로에 없음, `RFC-0029` §3.3 재확인) | 판단 자체는 code_review와 다른 전문성(테스트 설계 vs 코드 결함 지적) |

**판단 기준 적용 결과**: "분리했을 때 독립적 전문 판단/Context
isolation/parallelism/재사용성/검증성 중 하나 이상이 명확히
증가하는가?" — Requirements·Design Agent는 이미 최소 단위라 **더
쪼갤 근거 없음**. Backend Agent는 **이름 재검토**(두 함수를 별도
이름으로 부르는 것이 Context isolation·검증성을 명확히 증가시킴 —
§7)만 해당하고 함수 자체는 이미 분리돼 있어 코드 변경이 필요 없다.
Target Identification·QA Agent는 "쪼개는" 문제가 아니라 **이미 있는데
이름·Capability Map 등록이 없는** 문제다.

## 4. Stage별 Single/Multi-Agent 판단

| Stage | 판단 | 근거 |
|---|---|---|
| **01** | **3. 현재 Agent화 자체가 불필요** | Engine 호출 0건(§2). LLM 판단이 전혀 없다 |
| **02** | **1. Single Agent 적합** | Agent 1개(Requirements), 골격 조립은 결정적 재배치일 뿐 |
| **03** | **1. Single Agent 적합** | Agent 1개(Design), 02와 동형 |
| **04** | **2. Multi-Agent Team 후보** | Target Identification(§3 재분류)과 Code Generation이 서로 다른 판단이며 순차 의존(§5) |
| **05** | **2. Multi-Agent Team 후보(조건부)** | Code Review와 QA(활성화 시)가 독립 병렬 가능(§6). 단, Verdict는 Agent가 아니라 Aggregator(Function)로 유지해야 함(§6 Policy 경계) |

```
Stage 04
├─ Target Identification Agent (신규 명명 후보 — 이미 코드 존재)
├─ Implementation Agent (기존 Backend Agent code_generation)
├─ deterministic component: Build Input 조립(closure 삽입, Exposure Policy 문구 첨부)
└─ Aggregator: 없음(순차 파이프라인, 종합이 아니라 전달)

Stage 05
├─ Review Agent (기존 Backend Agent code_review)
├─ QA Agent (기존 qa_agent_test_execution — 비활성)
├─ deterministic component: structural/specification_scope/design_scope/test_execution 4개 검사
└─ Aggregator: Verdict 결정(_determine_verdict) — Agent 아님, Function 유지(§6)
```

## 5. Stage 04 상세 분석

```
Target Identification         (identify_target — call_engine 1회, §3 §2)
        ↓
Build Input 조립               (deterministic — closure 삽입, Exposure Policy 문구)
        ↓
Implementation / Code Generation  (backend_agent_code_generation — call_engine 1회)
```

**추가 독립 판단 책임이 실제로 존재하는가**: 코드 재확인 결과, Stage
04 안에는 **정확히 2개**의 Engine 호출만 있다(Target Identification,
Code Generation) — Context/Dependency Analysis는 Stage 01이 이미
수행한 `candidate_index`/`dependency_closure`를 그대로 재사용하는
결정적 조립일 뿐 별도 판단이 아니다(§2 Stage 04 Deterministic
Responsibility 열). Implementation Planning이라는 별도 책임도 코드에
없다 — Design(Stage 03 Output)이 이미 그 역할을 하고, Stage 04는
Design을 그대로 Code Generation 프롬프트에 전달할 뿐 재계획하지
않는다. Test Planning도 Stage 04에 없다(Stage 05의 QA Agent 영역,
§6).

**Target Agent → Implementation Agent 구조가 적절한가**: **적절하다.**
근거:
- **C(강한 결합) 판단**: Target Identification의 출력(`target`)이
  Build Input 조립의 입력이고, 그 조립 결과가 Code Generation의
  입력이다 — 순수 순차 의존(F: 이전 결과에 의존 = 예), 병렬화
  불가능(E: 병렬 실행 가능 = 아니오).
- **D(독립 전문 역할)**: "어디를 고칠지"(파일·함수 식별)와 "무엇을
  쓸지"(코드 작성)는 서로 다른 판단 기준(전자는 후보 인덱스와의
  매칭, 후자는 Design 사양 충족)이라 독립 전문 역할로 분리할 가치가
  **있다**.
- **H(별도 Agent Context가 유리한가)**: **유리하다** — 현재 두 Engine
  호출이 각각 다른 프롬프트·다른 판단 기준을 쓰는데도 하나는
  `mvp/agents/`에 등록되고 하나는 `workflow_ast_context.py`에 익명으로
  남아 있어, Capability Map(§3)의 완전성이 깨져 있다. 이름을 주는
  것만으로 Context isolation·검증성(개별 단위 테스트 가능성)이
  증가한다.

**Context/Dependency/Testing 책임을 기존 Agent에 유지할지 별도
Agent로 분리할지**:
- **Context/Dependency Analysis**: **기존대로 Stage 01의 결정적 산출물
  재사용을 유지한다.** 별도 Agent로 분리할 LLM 판단이 코드에 없다 —
  분리하면 "이름만 있고 실제로 하는 일은 없는" Agent가 생긴다(사용자가
  금지한 "이름만 명명" 패턴, `RFC-0030` §1 기준 위반).
- **Testing**: Stage 04에는 Testing 책임이 없다 — Stage 05의 QA Agent
  영역이므로 이 절의 판단 대상이 아니다(§6).

## 6. Stage 05 상세 분석

```
Implementation Result (Stage 04 Output)
       │
 ┌─────┴─────┐
 ▼           ▼
Review      QA
Agent       Agent
(존재,호출됨)  (존재,미호출)
 │           │
 └─────┬─────┘
       ▼
Deterministic Aggregator (4개 검사 + _determine_verdict)
       ▼
Verdict
```

**Code Review**: `backend_agent_code_review` — Stage 04
`implementation`만 입력, 이슈를 prose로 서술. 이미 독립 함수.

**QA/Test Proposal**: `qa_agent_test_execution` — `implementation` +
`review`를 입력으로 테스트 케이스 **제안**(실행 아님). 현재 Stage
05는 이를 호출하지 않는다 — **결정적 `test_execution` 검사(실제
pytest subprocess 실행)와 이름은 같지만 전혀 다른 것**이다. 이
불일치는 `RFC-0029` §3.3·`RFC-0030` §3(Stage 05 ②)이 이미 발견한
것을 이 분석도 재확인한다.

**Deterministic Checks**: `structural`/`specification_scope`/
`design_scope`/`test_execution` — 전부 AST 파싱, dict 키 존재 확인,
pytest 실행 결과(returncode) 비교뿐. **LLM 판단 없음.** Code
Review·QA와 병렬 실행 가능(둘 다 `implementation`만 입력으로 받고
서로 의존하지 않음) — 그러나 이는 Agent Team 관점이 아니라 §16.4
Multi-Task 관점의 관찰이다(`RFC-0030` §4 재확인).

**Verdict**: `_determine_verdict`가 `required_checks`에 포함된 항목만
반영해 PASS/FAIL/PARTIAL을 계산하는 **고정 규칙**(blocking/incomplete
2축 조합)이다. `code_review`의 텍스트 내용이나 QA의 테스트 제안
내용은 Verdict 계산에 **전혀 입력되지 않는다** — `_CHECK_EVALUATORS`가
참조하는 것은 오직 4개 결정적 검사의 raw dict뿐이다(`stage_05.py`
원문 재확인, `structural`/`specification_scope`/`design_scope`/
`test_execution` 키만 사용).

**이 구조가 타당한가 — Verdict가 Policy 판단을 침범하는가**:
`IMPLEMENTATION_RULES.md`("Policy 구현 금지 — MVP는 Policy 판정 호출
자체를 생략한다, 스텁도 만들지 않는다") 기준으로 코드를 재확인한
결과, **현재 Verdict는 Policy를 침범하지 않는다** — Verdict가
참조하는 것은 4개 결정적 검사뿐이고 Code Review·QA의 자연어 판단
내용은 Verdict 계산 경로에 들어오지 않는다(§2 Stage 05 열, 코드
재확인). **그러나 §7 제안대로 Review Agent Team 구조를 실제로
구현하려는 시도가 발생한다면, Verdict가 Review/QA의 텍스트 판단을
반영하도록 확장하고 싶은 유혹이 생길 수 있다 — 그 순간이 바로
Policy 구현 금지 경계를 넘는 지점이다.** 이 문서는 그 지점을
**경계선으로 명시**한다: Aggregator(Verdict)는 앞으로도 **결정적 검사
결과만** 반영해야 하며, Review/QA Agent의 자연어 출력을 Verdict
계산에 직접 대입하는 것은 이 분석이 권장하는 구조 밖이다.

## 7. Agent 재분배 후보 — 재분배 효과 평가 (0~3)

| 항목 | 점수(현재 Single-Agent, Backend Agent 기준) | 근거 |
|---|---|---|
| Responsibility Breadth | 2 | code_generation·code_review 두 판단이 한 모듈(`backend.py`)에 있으나 함수는 이미 분리돼 있어 "넓다"는 이름 층위의 문제일 뿐 |
| Context Breadth | 2 | 두 함수가 서로 다른 입력(design vs code)을 받으면서도 같은 파일·같은 접두어(`backend_agent_*`)를 공유해 호출자가 "Backend Agent가 하는 일"을 한눈에 파악하기 어려움 |
| Decision Diversity | 3 | 생성(무엇을 쓸지)과 검토(무엇이 틀렸는지)는 명백히 다른 판단 기준 |
| Parallelism Opportunity | 0 | code_generation(Stage 04)과 code_review(Stage 05)는 순서상 병렬 불가 — 후자가 전자의 출력을 입력으로 받음 |
| Reusability | 1 | 이미 함수로 분리돼 있어 재사용은 가능하나, 공유 이름(`backend_agent_*`)이 "다른 목적으로 재사용 중"이라는 신호를 흐림 |
| Independent Verification | 1 | 함수 단위 테스트는 이미 가능(`test_stage_04.py`/`test_stage_05.py`가 각각 mock) — 이름 분리는 검증성을 약간만 높임 |
| Failure Isolation | 0 | 이미 별도 함수 호출이라 한쪽 실패가 다른 쪽에 전파되지 않음(Stage 04/05 각자 `try/except`) — 이름을 바꿔도 달라지지 않음 |

**Current Single-Agent("Backend Agent") vs Proposed Agent
Team("Generation Agent" + "Review Agent")**: 점수 분포가 보여주듯,
**개선 여지는 Decision Diversity·Context Breadth 두 항목에 집중돼
있고, Parallelism·Failure Isolation·Reusability는 이미 함수 분리로
확보돼 있어 추가 이득이 없다.** 즉 이 재분배는 "새 Agent를
만드는" 문제가 아니라 **"이미 다른 두 함수에 붙어 있는 공유 이름표를
분리하는" 문제**다 — 코드 재작성이 필요 없고(함수는 이미 분리),
호출부도 이미 각 Stage가 정확한 함수를 개별 import하고 있다
(`stages/04_implementation/stage_04.py`는 `backend_agent_code_generation`만,
`stages/05_validation/stage_05.py`는 `backend_agent_code_review`만
import). **Production 변경이 필요한 부분(모듈 재명명·`__init__.py`
재편)은 이 분석의 범위 밖**이며, 이 문서는 그 필요성만 관찰로
기록한다.

Target Identification·QA Agent(§3, §5, §6)에 대해서는 위 표와 별개로
다음만 재확인한다 — 둘 다 Decision Diversity(3)·Independent
Verification 잠재력(2, 이름이 붙으면 개별 단위 테스트 대상으로
명확해짐)에서 점수가 높고, Parallelism은 Target Identification=0(순차
의존), QA=2(Review와 병렬 가능)로 갈린다.

## 8. Multi-Agent 필요성 판단

**Q1. 현재 구조에서 단순히 Agent 수를 늘리는 것인가?**
아니다. Target Identification·QA Agent는 **이미 코드로 존재하는**
Engine 호출이며, 이 문서가 "새로 만들자"고 제안한 함수가 아니다(§3,
§5, §6). Backend Agent 이름 분리도 새 판단을 추가하는 것이 아니라
기존 두 판단에 정확한 이름을 붙이는 것이다.

**Q2. 아니면 기존 Agent의 책임을 실제로 분리할 필요가 있는가?**
Backend Agent에 한해 **예**(이름 층위, §7). Requirements·Design
Agent는 이미 최소 단위라 **아니오**(§3).

**Q3. 분리했을 때 실제로 병렬 실행이 가능한가?**
Stage 05의 Review ∥ QA만 **예**(§6, 둘 다 `implementation`만 입력).
Stage 04의 Target Identification → Code Generation은 **아니오**
(순차 의존, §5).

**Q4. Agent 간 dependency가 존재하는가?**
Stage 04 내부에 순차 dependency 1건(Target → Build Input → Code
Generation), Stage 05 내부에 병렬 후 종합 dependency 1건(Review·QA
→ Verdict). 그 외(01→02→03→04→05 Stage 간)는 이미 `contracts.py`
HQ-level Public Contract로 형식화된 선형 dependency뿐.

**Q5. dependency 때문에 workflow state가 필요해지는가?**
**아니다.** 두 dependency 모두 caller(Stage 함수)의 지역 변수 전달로
완전히 표현된다 — Phase E(`RFC-0028`) 실험이 이미 증명한 것과 동일한
구조(`caller.py`의 `run_sequential_handoff`)다. Kernel/Runtime이
소유하는 공유 State(Phase B `RFC-0025` §4, 여전히 Defer)는 필요하지
않다.

**Q6. 실패한 Agent만 재실행할 필요가 생기는가?**
현재 코드는 **Stage 단위**로 실패를 처리한다(Stage 전체가 `error`
필드로 즉시 반환) — Agent 단위 개별 재실행은 관찰되지 않았고, 이
문서가 분석한 어떤 후보(Target Identification, Review, QA)도 "이
Agent만 재실행"해야 할 실제 요구를 코드나 테스트에서 보여주지
않았다. **UNVERIFIED**(Evidence 없음, §10 표기 원칙 적용).

**Q7. 이 복잡도가 Plain Python orchestration으로 관리 가능한가?**
**예.** §5·§6이 관찰한 두 종류의 관계(순차 Handoff, 1단계 병렬+종합)는
Phase E가 이미 순수 함수 호출 + `ThreadPoolExecutor`만으로 완전히
재현했다(`projects/multi-agent-handoff-mvp-v1/`, 마찰 없음, IN-1~IN-7
전부 PASS). Stage 04/05 내부 구조는 그 실험 시나리오와 위상적으로
동일하다(2-노드 순차, 2-노드 병렬+1-종합).

**Q8. 어느 지점부터 LangGraph가 실질적인 이점을 제공하는가?**
§10에서 별도로 다룬다 — 이번 분석의 관찰 범위(순차 1건, 병렬+종합
1건, Loop·Conditional Edge 0건) 안에서는 **이점이 관찰되지 않았다.**

## 9. 최소 Experimental Model — 설계만, 구현하지 않음

**선정: Stage 04(Target Agent → Implementation Agent) + Stage
05(Review Agent ∥ QA Agent → deterministic Aggregator) 조합.**

```
Stage 04
Target Agent
    ↓
Implementation Agent

Stage 05
Review Agent ─┐
              ├→ deterministic Aggregator
QA Agent ─────┘
```

### 선정 이유

1. **실제 코드 근거가 가장 강하다** — 이 조합만이 §3 표의 4개 실재
   Engine 호출 지점(Target Identification, Code Generation, Code
   Review, QA)을 전부 포함한다(`RFC-0030` §7과 동일 결론, 이 문서가
   더 세밀한 §5·§6 근거로 재확인).
2. **관찰된 두 관계 유형(순차·병렬+종합)을 정확히 하나씩 담는다** —
   Loop·Conditional Edge가 필요 없어 §16.6 Workflow Adapter A-IN
   전체를 억지로 채우지 않는다(`RFC-0030` §5 재확인).
3. **Phase E 실험(`multi-agent-handoff-mvp-v1`)과 위상적으로
   동일**하여, 그 실험이 이미 마찰 없음을 증명한 패턴(직접 함수 호출
   + `ThreadPoolExecutor`)을 그대로 재사용할 수 있다 — 새 추상화를
   설계할 필요가 없다.

### 다른 책임을 Agent로 분리하지 않은 이유

- **Stage 01 전체**: Engine 호출 0건(§2) — Agent화 근거 자체가 없다.
- **Stage 02·03**: Agent가 1개뿐이라 "Team"이 성립하지 않는다(§4).
- **Stage 04의 Build Input 조립**: 결정적 문자열 조립이며 판단이
  아니다(§5) — Agent로 만들면 "이름만 있고 하는 일은 결정적 로직"인
  패턴(사용자가 금지)이 된다.
- **Stage 05의 4개 결정적 검사**: LLM 판단이 아니다(§6).
- **Stage 05의 Verdict**: Agent가 아니라 Function으로 유지해야
  한다 — Agent화하면 Policy 구현 금지 경계를 넘을 위험이 있다(§6).

## 10. Plain Python 한계 / LangGraph가 필요해지는 조건

| 구분 | 현재 Plain Python으로 충분한 부분 | Graph Runtime이 유리해지는 부분(향후, 조건부) |
|---|---|---|
| 순차 Handoff(Stage 04) | **충분** — Phase E가 실증(§8 Q7) | — |
| 병렬 + 단일 종합(Stage 05) | **충분** — `ThreadPoolExecutor` 직접 사용으로 마찰 없음(§8 Q7) | — |
| Conditional Edge(조건에 따라 다음 Agent가 달라짐) | 관찰된 사례 없음(Stage 04의 Exposure Policy 충돌은 Agent 간 라우팅이 아니라 값 매칭, `RFC-0030` §3 Stage 04 ⑥) | **UNVERIFIED** — 이 저장소에 실제 사례가 나타나면(예: Review 결과에 따라 재생성 Agent를 호출할지 결정) 그 시점에 재평가 필요 |
| Loop(같은 Agent를 조건 만족까지 반복) | 관찰된 사례 없음(`IMPLEMENTATION_RULES.md` "Stage 재진입 금지") | **UNVERIFIED** — Dev HQ가 재진입/재시도를 실제로 요구하게 되면(예: 코드 생성 실패 시 자동 재시도) 재평가 필요, 단 이는 §16.6 Workflow Adapter 트랙(Gate B/C 여전히 미충족)의 소관 |
| Checkpoint/Resume(중간 상태를 저장했다 나중에 이어서) | 관찰된 사례 없음 — 현재 모든 Stage는 단일 프로세스 내에서 끝까지 실행됨 | **UNVERIFIED** — 장시간 실행(예: 대규모 코드베이스 대상 Stage 04)이 실제로 문제가 되는 시점에 재평가 필요 |
| Dynamic Agent Allocation(실행 중 어느 Agent를 쓸지 결정) | 관찰된 사례 없음 — Agent는 전부 Stage 코드에 고정 호출됨(Scheduler/Dynamic Routing 구현 금지, `IMPLEMENTATION_RULES.md`) | **UNVERIFIED** — 이는 애초에 §16.6 범위가 아니라 ADC-02(Runtime 존폐, Open, NOW) 자체의 질문이며, Phase D/E(`RFC-0027`/`RFC-0028`)가 이미 "실제 소비자 없음"으로 판정했다 |

이 분석은 이 5개 항목 중 **어느 것도 LangGraph 채택을 정당화할
Evidence를 발견하지 못했다** — 전부 UNVERIFIED로 남긴다.

## 11. 최소 다음 PoC 제안 (구현하지 않음)

§9의 조합을 실제로 검증하려면(사용자가 별도로 요청하는 경우에만),
Phase E와 동일한 격리 원칙(`projects/`, `hqs/development/` 무단 연결
금지, LangGraph 미사용) 아래 다음을 재현할 수 있다:

1. Target Identification·Code Generation·Code Review·QA 4개 함수를
   **실제 Engine 호출 없이 mock**으로 대체한 순수 함수로 재현(Phase E
   `domain/agents.py`와 동일 패턴).
2. Stage 04 순차 Handoff·Stage 05 병렬+종합을 `caller.py`에서 직접
   함수 호출 + `ThreadPoolExecutor`로 재현.
3. 실패 시나리오(Target Identification 실패 → Code Generation 미호출,
   Review 실패 → Verdict가 그 실패를 값으로 반영하되 QA 결과는
   여전히 종합) 관찰.
4. **이 PoC는 Backend Agent 이름 분리(§7)를 전제하지 않는다** — mock
   함수 이름을 실험 안에서 자유롭게 붙일 수 있으므로, Production의
   `mvp/agents/backend.py` 재편 여부와 무관하게 구조 검증이
   가능하다.

이 문서는 위 4단계를 **제안만** 한다 — 실제 구현은 이번 세션의
범위가 아니다.

## 12. Open Questions

1. Backend Agent의 두 함수(`code_generation`/`code_review`)를 별도
   모듈·이름으로 재편하는 것이 실제로 가치가 있는지 — §7이 관찰만
   했고 Production 변경은 하지 않았다. 재편 여부는 별도 판단 필요.
2. Target Identification에 공식 이름을 부여하고 `mvp/agents/`에
   등록할지 — 등록은 Production 변경이며 이 문서의 범위 밖이다.
3. QA Agent(`qa_agent_test_execution`)를 Stage 05에 실제로 연결할지 —
   연결하면 Verdict 계산 경로에 영향을 주지 않도록 설계해야 한다는
   경계(§6)만 이 문서가 제시했다.
4. §10의 5개 UNVERIFIED 항목 중 어느 것이 실제로 관찰되면 §16.6
   Workflow Adapter 또는 ADC-02 재검토 Trigger에 해당하는지 — 이
   문서는 판정하지 않는다.
5. §9 PoC를 실제로 실행할지 여부 — 사용자 판단 대기.

---

## Validation

- `git status --porcelain` — 이 디렉터리(`README.md` 1개)만 추가.
  `hqs/development/`·`core/`·`dashboard/` Production Code, `BASELINE.md`,
  `GLOSSARY.md`, `IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`
  **전부 무변경**.
- `grep -rn "call_engine\|call_engine_via_omniroute"
  hqs/development/mvp/*.py hqs/development/stages/*/*.py` — §2·§3의
  5개 지점과 정확히 일치(정의부 제외, `RFC-0030` §2와 동일 재확인).
- `hqs/development/stages/04_implementation/stage_04.py`·
  `05_validation/stage_05.py` 원문 재확인 — 각 Stage가 `mvp.agents`에서
  정확히 필요한 함수만 import함(§7 "호출부는 이미 정확한 함수를
  개별 import" 주장의 근거).
- `hqs/development/IMPLEMENTATION_RULES.md` "Policy 구현 금지" 원문
  재확인 — §6 Verdict 분석의 근거.
- `_determine_verdict`/`_CHECK_EVALUATORS` 원문 재확인 — Verdict가
  4개 결정적 검사 dict만 참조하고 `code_review`/QA 텍스트를 참조하지
  않음을 코드로 확인(§6).
- Production 회귀 기준선: `/root/.local/bin/pytest
  hqs/development/mvp/tests/ -q` → **186 passed, 6 skipped** — 이
  문서 작성 전후 동일(코드를 바꾸지 않았으므로 당연한 결과이나,
  사용자 지시대로 실행해 재확인했다). 이 결과를 변경하지 않았다.
- 이 문서 자체의 구조 무결성: 위 12개 섹션 헤더가 요청된 목차(§1~§12
  + Validation)와 1:1 대응하는지 재확인.

## Self Review

- Production 코드(`hqs/development/`)를 수정했는가 — **아니오**(§Validation).
- Agent Manager/Runtime/Event Bus/Scheduler/Registry를 구현했는가 —
  **아니오** — 어디에도 코드가 없다, 이 디렉터리는 `README.md` 1개뿐.
- LangGraph를 사용했는가 — **아니오**(§10, §11).
- 새로운 Message/Event Contract를 정의했는가 — **아니오** — §5·§6의
  dependency는 caller 지역 변수 전달로만 표현되며 Phase B(`RFC-0025`)
  개념을 재정의하지 않았다.
- "이름만 명명"하는 방식으로 Agent 후보를 인정했는가 — **아니오**
  (§3, §4, §9) — Target Identification·QA Agent 모두 실제 `call_engine`
  호출 근거로만 인정했고, Build Input 조립·4개 결정적 검사·Verdict는
  전부 제외했다.
- Verdict의 Policy 침범 여부를 코드로 확인했는가 — **예**(§6) —
  `_CHECK_EVALUATORS`가 참조하는 키를 원문에서 직접 대조했다.
- 기존 RFC-0024~0030/ADC-0032/0033의 판단을 임의로 바꿨는가 —
  **아니오** — 전부 전제로 인용만 했고, UNVERIFIED 항목(§10)은 결정이
  아니라 관찰 부재를 표시한 것이다.
