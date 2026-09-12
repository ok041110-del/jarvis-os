# RFC-0029: Dev HQ Stage → Agent Boundary Analysis (Phase F-1)

**Status**: Proposed (분석 결과 기록, Baseline 결정 아님)
**Author**: Claude Code
**대상**: `hqs/development/CONSTITUTION.md`·`BASELINE.md`·`IMPLEMENTATION_RULES.md`,
`hqs/development/workflow.py`, `hqs/development/stages/01~05/stage_0N.py`,
`hqs/development/stages/contracts.py`, `hqs/development/mvp/agents/*.py`,
`docs/research/DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`·
`DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md`,
`docs/architecture/core/RFC-0024~0028`·`ADC-0032`·`ADC-0033`(Phase A~E —
전부 Defer/Open 또는 "이미 Decided, 재정의 불필요").

**Evidence**: 위 코드·문서 전체(코드 원문 직접 읽음, grep으로 실제
호출 관계 대조). **Production Code는 변경하지 않았다** — 이 RFC는
분석 문서다.

> 이 RFC는 Phase A~E의 결과를 **전제**로 삼는다. Agent Domain/Lifecycle/
> State/Message/Event/Runtime 어느 것도 이 RFC로 새로 확정되지 않는다.
> 이 RFC는 Dev HQ의 **기존 코드가 실제로 어떻게 동작하는지**만
> 분석하고, 그 분석을 근거로 향후 Governance 절차(RFC→ADC→ADR)가 참고할
> Candidate 구분만 남긴다.

---

## 0. 이 RFC가 열린 이유

Phase A(`RFC-0024`)는 Agent Domain을 문서·Governance 수준에서
다뤘지만, "Dev HQ의 실제 코드가 Agent 경계에 얼마나 가까운가"는 검증한
적이 없다. Phase F-1은 그 공백을 코드 읽기로 메운다 — Stage가
존재한다는 사실만으로 Agent 적합성을 인정하지 않고, 각 Stage의 실제
책임·입출력·실행 독립성을 코드 기준으로 추출한다.

## 1. Stage별 책임/입출력/도구/상태/검증 — 코드 기준 추출

| Stage | 책임 | 입력 | 출력 | 도구(Engine 호출 여부) | 상태 | 검증 |
|---|---|---|---|---|---|---|
| **01 Context Analysis** | 디렉터리 구조·context bundle·후보 인덱스·(선택) dependency closure 수집 | `issue: dict`, `target: tuple\|None` | `directory_structure`, `context_bundle`, `candidate_index`, `target`, `dependency_closure` | **Engine 호출 없음** — `mvp.ast_context`/`mvp.project_intelligence`의 순수 결정적 함수만 호출 | Stateless(순수 함수) | Stage 05가 아닌 각 Stage 자체 단위 테스트(`VALIDATION.md`)로 검증 |
| **02 Planning/Specification** | Stage 01 Context에서 결정적으로 골격 조립(`_structure_from_context`) + **Requirements Agent** 호출(`requirements_agent_requirement_analysis`) | `issue`, `stage_01_context` | `skeleton`, `specification` | **Engine 호출 있음**(1회, Requirements Agent) | Stateless, 단 Engine 실패 시 값으로 오류 반환(예외 미전파) | `contracts.validate_specification_result` |
| **03 Architecture/Design** | Stage 01/02 Output에서 결정적으로 골격 조립 + **Design Agent** 호출(`design_agent_design`) | `issue`, `stage_01_context`, `stage_02_output` | `skeleton`, `design` | **Engine 호출 있음**(1회, Design Agent) | Stateless, 값 기반 오류 반환 | `contracts.validate_design_result` |
| **04 Implementation** | Target 식별(결정적, Stage 01 `candidate_index` 재사용) + Build Input 조립(결정적) + **Backend Agent** 호출(`backend_agent_code_generation`) | `stage_01_context`, `stage_03_output`, `expose_target: bool` | `target`, `implementation`, `expose_target` | **Engine 호출 있음**(1회, Backend Agent, code_generation) | Stateless, 단 대상 파일을 임시로 읽기만 함(부작용 없음) | `contracts.validate_implementation_result` |
| **05 Validation** | 4개 결정적 검증(structural/specification_scope/design_scope/test_execution — 후자는 **실제 파일을 덮어쓰고 pytest subprocess 실행 후 원복**) + **Backend Agent** 호출(`backend_agent_code_review`, code_review) + Verdict 결정(결정적 규칙, Policy 아님) | `stage_02_output`, `stage_04_output`, `required_checks` | `VerificationResult`(checks, verdict, code_review) | **Engine 호출 있음**(1회, Backend Agent, code_review — QA Agent 아님, §2.1 참조) | **부작용 있음** — 대상 모듈 파일을 임시로 덮어쓰고(`path.write_text`) `finally`로 원복 | `contracts.validate_verification_result` |

**06 devops_release**: `hqs/development/stages/06_devops_release/`에
`README.md`만 존재하고 `stage_06.py` 자체가 없다 — `workflow.py`도
이를 호출하지 않는다(grep 확인). **코드로 존재하지 않는 Stage**이므로
이 분석 대상에서 제외한다.

### 1.1 Workflow 자체의 실행 형태 — 단일 선형, 동적 협업 아님

`hqs/development/workflow.py`의 `run_workflow()`는 Stage 01→05를
`try/except`로 **직접 순차 호출**하며, 중간 Stage 예외 시 `failed_at`/
`error`만 채워 즉시 반환한다. 조건부 분기·Loop·재진입 없음
(`IMPLEMENTATION_RULES.md` "Stage 재진입 금지"). **Agent 간 동적
협업(누가 다음에 실행될지 실행 중 결정, Agent끼리 직접 통신)은 이
Workflow 어디에도 없다** — Stage 순서는 소스 코드에 고정되어 있고,
그 안에서 호출되는 4개 Agent 함수(Requirements/Design/Backend×2)는
서로를 모르며 직접 통신하지 않는다. 이는 `RFC-0026` §3.1이 이미 확인한
것과 동일한 구조다.

## 2. Agent 적합성 판단 — 기준별 평가

> 기준: 책임 독립성, 입력/출력 경계, 실행 독립성, 다른 Stage와의
> 의존성, 재실행 가능성, 조건부 분기 가능성. "Stage가 존재한다"는
> 사실 자체는 근거로 쓰지 않는다.

### 2.1 핵심 관찰 — Agent 경계는 이미 Stage 경계와 다른 곳에 있다

`mvp/agents/*.py`(Requirements/Design/Backend/QA)는 **이미 Stage와
분리된 독립 모듈**로 존재한다 — 각 함수는 하나의 좁은 Capability(예:
`backend_agent_code_generation(design: str) -> str`)만 가지며, 자신을
호출하는 Stage의 골격 조립 로직을 전혀 모른다. 즉 "Stage를 Agent로
분리해야 하는가"라는 질문은 이미 **절반은 답이 나와 있다** — Agent에
해당하는 부분(Engine 호출)은 이미 분리되어 있고, 남은 것은 "Stage
자신(골격 조립 + Contract 검증 + 흐름 제어)도 Agent로 볼 것인가"라는
좁은 질문이다.

한 가지 불일치도 발견됐다: `mvp/agents/__init__.py`의
`AGENT_CAPABILITY_MAP`은 `"test_execution": "QA Agent"`로 선언하지만,
Stage 05의 실제 `test_execution` 검사(`_run_pytest_with_applied_implementation`)는
**pytest subprocess 실행이며 `qa_agent_test_execution`(QA Agent 함수)을
전혀 호출하지 않는다** — `qa_agent_test_execution`은 grep 결과
`stages/`·`workflow.py`·`cli.py` 어디에서도 호출되지 않는 **정의만
되고 미사용인 함수**다. 이는 `DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md`가
이미 지적한 "Runtime 없는 명명 규칙 수준"이 코드 레벨에서도 그대로
확인된 것이다 — Capability Map의 이름과 실제 실행 경로가 어긋나 있다.

### 2.2 Stage별 평가표

| Stage | 책임 독립성 | I/O 경계 | 실행 독립성 | 다른 Stage 의존성 | 재실행 가능성 | 조건부 분기 가능성 | 종합 |
|---|---|---|---|---|---|---|---|
| **01** | 높음(순수 조회) | 명확(issue→context) | 높음(Stage 02~05 없이 단독 실행 가능) | 없음(첫 Stage) | 높음(부작용 없는 순수 함수, 멱등) | 낮음(분기 로직 없음, 있을 이유도 없음) | **Agent화 근거 부족** — Engine 호출이 아예 없어 이 저장소가 지금까지 써 온 "Agent = Capability를 Engine으로 수행하는 단위" 관행과 맞지 않음(§2.3) |
| **02** | 중간(골격 조립 + Agent 호출 이중 책임) | 명확하나 골격 조립 로직이 Agent 호출과 섞여 있음 | 낮음(Stage 01 Context 없이 실행 불가) | Stage 01에 강하게 의존 | 높음(순수 함수, 부작용 없음) | 낮음 | **조건부 후보** — Agent 부분(Requirements Agent)은 이미 분리되어 있으나, Stage 자체를 Agent로 승격하려면 골격 조립 책임을 별도로 떼어내야 함 |
| **03** | 02와 동형 | 02와 동형 | 낮음(Stage 01/02 없이 실행 불가) | Stage 01·02 모두에 의존 | 높음 | 낮음 | **조건부 후보** — 02와 동일 논거 |
| **04** | 중간(Target 식별 + Build Input 조립 + Agent 호출) | 명확 | 낮음(Stage 01/03 없이 실행 불가) | Stage 01·03에 의존 | 높음(파일을 읽기만 함, 쓰지 않음) | 낮음~중간(Exposure Policy 충돌 시 결정적 신호 반환 — 이미 값 기반 분기) | **조건부 후보** — Target 식별 로직(결정적)과 Agent 호출(Backend)이 분리 가능해 보이나, `identify_target`이 Stage 01 산출물에 강하게 결합 |
| **05** | **낮음** — 4개 결정적 검사 + Agent 호출(code_review) + Verdict 결정(Policy에 가까운 결정 로직)이 한 함수에 응집 | 넓음(Stage 02·04 Output 모두 필요) | **매우 낮음** — Stage 02·04 없이 무의미, 게다가 **부작용 있음**(대상 파일 임시 덮어쓰기) | Stage 02·04 모두에 강하게 의존 | **낮음** — 파일 쓰기/복원이 동시 실행과 충돌 위험(§3.4) | 있음(required_checks에 따라 실행 집합이 달라짐 — 그러나 이는 Policy가 아닌 고정 규칙) | **Agent화 근거 가장 부족** — 책임이 응집돼 있고, Verdict 결정 로직을 Agent로 옮기면 `IMPLEMENTATION_RULES.md` "Policy 구현 금지"를 사실상 우회할 위험(§3.2) |

## 3. Agent 경계에서 발생할 핵심 문제

### 3.1 Stage의 이중 책임 — "골격 조립"과 "Agent 호출"이 분리되지 않음

Stage 02~04는 전부 "이전 Stage Output에서 결정적으로 골격을 조립하는
로직"과 "그 골격을 Agent에게 넘겨 호출하는 로직"을 한 함수에서
수행한다. 이 둘을 그대로 "Agent"로 승격하면, Agent의 Capability(Phase
A `RFC-0024` §4, Defer)에 "골격 조립"이라는 **Kernel/HQ 결정적 로직**과
"Engine 호출"이라는 **Agent 본연의 책임**이 섞여 들어가게 된다. 이는
`BASELINE.md` §16.6 A-OUT이 Workflow Adapter에 대해 이미 경계 지은
것("무엇을 실행할지는 HQ가 채운다")과 같은 종류의 혼동을 Agent
경계에서도 반복할 위험이다.

### 3.2 Stage 05 Verdict 로직과 Policy 구현 금지의 경계

Stage 05의 `_determine_verdict`/`_CHECK_EVALUATORS`는 `required_checks`에
따라 실행 집합과 판정을 결정하는 **규칙 기반 로직**이며, 코드 주석이
스스로 "Policy 구현 금지"를 명시적으로 인용한다. 이 로직을 "QA Agent"
같은 이름으로 Agent화하면, 규칙이 Engine 호출 뒤에 숨어 사실상 Policy
Decision Point(PDP)처럼 보이게 될 위험이 있다 — `IMPLEMENTATION_RULES.md`
Policy 구현 금지를 문언은 지키면서 실질은 우회하는 경로가 될 수
있다. 이 RFC는 이 위험을 **경고로만 기록**하며, Stage 05를 Agent화
후보에서 배제하는 판단(§4)의 핵심 근거로 삼는다.

### 3.3 Capability Map과 실제 실행 경로의 불일치(QA Agent)

§2.1이 발견한 `AGENT_CAPABILITY_MAP["test_execution"] = "QA Agent"` vs
실제 미호출은, Agent Domain(Phase A, Defer)이 아직 확정되지 않은
상태에서 "이름"과 "실행"이 이미 갈라질 수 있음을 보여준다. Agent
Domain이 실제로 Accept되는 시점에는 이런 불일치를 검출할 Contract적
근거(예: Capability 선언과 실제 호출의 일치 검증)가 필요할 수 있으나,
이 RFC는 그 Contract를 새로 만들지 않는다 — 관찰만 기록한다.

### 3.4 Stage 05의 파일 쓰기 부작용과 동시 실행

Stage 05의 `test_execution` 검사는 대상 모듈 파일을 **임시로
덮어쓰고 원복**한다(`_run_pytest_with_applied_implementation`). 이
Stage(혹은 그 Agent화 후보)를 §16.4 Multi-Task(Accept, Scoped,
Conditional **on Data/Artifact Isolation**) 범위에서 동시 실행하면,
동일 대상 파일에 대한 쓰기 충돌이 발생할 수 있다 — 이는 새로운
문제가 아니라 §16.3 Execution Host의 기존 조건("동일 Target 동시
실행" 시 Process 격리 필요)이 이미 예견한 것과 같은 종류의 위험이며,
이 RFC는 그 기존 경계를 재확인할 뿐 새 Contract를 만들지 않는다.

### 3.5 §14.1 "Task 전달 책임"·Phase B 접점 재확인(우회 아님)

Stage 간 데이터는 `contracts.py`의 HQ-level Public Contract(`ADR-0009`)로
이미 형식화되어 있다 — Kernel Public Contract(§14)가 아니다
(`hqs/development/BASELINE.md` "Stage Data Contract" 절이 이미 이
경계를 확정). 이를 Agent Domain(Phase A)의 Input/Output 필드나
Message/Event(Phase B)로 재해석하고 싶은 유혹이 있을 수 있으나, 이
RFC는 그렇게 하지 않는다 — `RFC-0025` §5의 접점 관찰과 동일하게,
"접점이 있다"는 사실만 기록하고 관계를 결정하지 않는다.

## 4. 분류 — Agent로 분리할 가치가 높은 Stage / 조건부 후보 / 근거 부족

| 분류 | Stage | 근거 |
|---|---|---|
| **Agent로 분리할 가치가 높음** | **없음** | 어떤 Stage도 §2.2 기준을 압도적으로 충족하지 못했다 — Agent에 해당하는 부분(Engine 호출)은 이미 `mvp/agents/`로 분리되어 있어, Stage 자체를 통째로 Agent로 승격할 실익이 없다 |
| **조건부 후보**(Agent 부분과 골격 조립 부분을 먼저 분리해야 판단 가능) | 02, 03, 04 | 이미 분리된 Agent 함수(Requirements/Design/Backend)가 각각 Capability 경계를 갖고 있으나, Stage 자체의 골격 조립 로직(§3.1)을 분리하지 않고는 Stage 전체를 Agent 경계와 동일시할 수 없다 |
| **Agent화할 근거가 부족함(Workflow Step/Function으로 유지가 더 적절)** | **01, 05** | 01은 Engine 호출이 아예 없어 이 저장소의 기존 Agent 관행(Capability=Engine 수행)과 불일치. 05는 책임이 응집돼 있고 부작용(파일 쓰기)과 Policy 인접 로직(Verdict) 때문에 Agent화가 오히려 위험(§3.2, §3.4) |

## 5. Experimental PoC 제안 — 구현하지 않음, 설계만

Agentized Dev Workflow를 실제로 검증하려면, Phase E(`RFC-0028`)와
동일한 격리 원칙(`projects/`, `hqs/development/` 무단 연결 금지,
LangGraph 미사용, 새 일반화 Runtime API 금지)을 지키는 최소 시나리오가
필요하다. **이 RFC는 다음을 제안만 하며 구현하지 않는다**:

1. **골격 조립과 Agent 호출의 분리 관찰**: Stage 02~04 각각에서
   "골격 조립 함수"와 "기존 Agent 함수 호출"을 격리된 `projects/`
   디렉터리 안에서 두 개의 독립 함수로 재현(원본 코드 수정 없음,
   구조만 재현)하고, 그 둘을 caller가 순차 호출했을 때 Phase E와
   동일하게 마찰 없이 재현되는지 관찰한다.
2. **Stage 05 분리 실험(선택)**: 4개 결정적 검사와 Verdict 결정
   로직을 그대로 유지한 채 `code_review` 호출만 별도 "Agent 경계"로
   격리했을 때, Verdict 로직이 Policy 구현 금지 경계를 넘는 신호가
   나타나는지(예: Verdict가 Engine 응답 내용에 의존하게 되는지)
   관찰한다 — 넘는다면 이는 Stage 05를 Agent화 후보에서 배제할
   추가 근거가 된다.
3. **QA Agent 실사용 재현(선택)**: `qa_agent_test_execution`을 실제로
   호출하는 대안 경로를 격리된 실험에서만 구성해, 그 출력(테스트
   케이스 제안)이 Stage 05의 결정적 `test_execution` 검사와 병존
   가능한지(대체가 아니라 **추가** 정보로서) 관찰한다 — 이는 §3.3의
   불일치를 실행 수준에서 이해하기 위한 것이지, 즉시 Production에
   연결하자는 제안이 아니다.

이 세 시나리오 모두 Agent Domain/Lifecycle/State/Message/Event/Agent
Manager/Runtime Contract를 새로 확정하는 것을 전제하지 않는다 — 순수
관찰 목적이며, 필요하다고 판단되면 별도 세션에서 Phase E와 동일한
Experimental Implementation 규칙 아래 구현될 수 있다.

## 6. Out of Scope

- `mvp/agents/*.py`·`stages/*.py`·`workflow.py`·`contracts.py`의
  **재정의·재구현** — 이 RFC는 코드를 한 줄도 바꾸지 않았다.
- Agent Domain/Lifecycle(Phase A)·Agent State/Message/Event(Phase B)·
  Multi-Agent Workflow(Phase C)·Runtime Contract(Phase D)·Minimal
  Runtime MVP(Phase E)의 재정의.
- §5가 제안한 3개 시나리오의 실제 구현.
- `hqs/development/BASELINE.md`·`CONSTITUTION.md`·`IMPLEMENTATION_RULES.md`·
  `docs/architecture/baseline/BASELINE.md`의 문언 수정.
- QA Agent 미사용 불일치(§3.3)의 **수정** — 이 RFC는 관찰만 기록한다.

## 7. Non-goals

- 이 RFC는 "Dev HQ Stage를 Agent로 전환해야 한다"고 주장하지 않는다 —
  §4가 확인했듯 압도적으로 적합한 Stage가 없다.
- 이 RFC는 QA Agent 불일치(§3.3)를 즉시 고쳐야 할 결함으로 판정하지
  않는다 — Agent Domain이 아직 Defer 상태이므로 "선언과 실행의 일치"를
  요구할 Contract 근거 자체가 없다.
- 이 RFC는 §5의 Experimental PoC가 반드시 필요하다고 주장하지 않는다 —
  후속 세션에서 실제 필요가 관찰되면 그때 판단한다.

## 8. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase F-1)** | Dev HQ Stage 01~05의 실제 책임·입출력을 코드로 추출하고, Agent 적합성을 기준별로 평가해 분류(§4) + 핵심 문제 기록(§3) + 미구현 PoC 제안(§5). |
| **후속(필요 시)** | §5 시나리오 중 하나를 격리된 Experimental Implementation으로 실행하거나(Phase E와 동일 규칙), Phase A(Agent Domain)의 재검토 Trigger가 충족되면 이 RFC를 참고 자료로 재상정. |

## 9. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건만 추가. `hqs/development/`·
  `core/`·`dashboard/` Production Code **무변경**.
- Stage 01~05 코드 원문을 직접 읽고 §1 표를 작성 — 인용이 실제 함수
  시그니처·본문과 일치.
- `grep -rn "qa_agent_test_execution" hqs/development/stages/
  hqs/development/workflow.py hqs/development/cli.py` — 0건, §2.1·§3.3
  주장의 근거.
- `hqs/development/stages/06_devops_release/` 디렉터리 확인 —
  `README.md`만 존재, `stage_06.py` 없음, `workflow.py`가 호출하지
  않음(§1 "06 devops_release" 문단).
- `hqs/development/workflow.py` 원문 재확인 — `try/except` 직접 순차
  호출(§1.1 인용과 일치, `RFC-0026` §3.1과 동일 관찰 재확인).
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다. 참고로
  `/root/.local/bin/pytest hqs/development/mvp/tests/ -q`가 이번 세션
  Phase E에서 이미 186 passed, 6 skipped로 확인된 바 있으며, 이 RFC는
  그 이후 어떤 코드도 바꾸지 않았으므로 재실행 결과가 달라질 여지가
  없다.

## 10. Self Review

- Production Code(`hqs/development/`)를 변경했는가 — **아니오**(§9).
- Agent Domain/Lifecycle/State/Message/Event/Agent Manager/Runtime
  Contract를 새로 확정했는가 — **아니오**(§6, §7) — §3.5·§5 모두
  접점·제안만 기록했다.
- "Stage가 존재한다"는 이유만으로 Agent 적합성을 인정했는가 —
  **아니오**(§2.2) — 6개 기준 전부에 대해 코드 근거를 표로 제시했다.
- Workflow의 Stage 순서를 Agent 간 동적 협업과 동일시했는가 —
  **아니오**(§1.1) — 단일 선형 실행임을 명시적으로 확인했다.
- LangGraph를 사용했는가 — **아니오** — 이 RFC는 코드를 실행하지
  않았고(분석 문서), §5 제안도 명시적으로 LangGraph를 배제한다.
- Phase A~E의 Defer/Open 결론을 우회했는가 — **아니오**(§0, §3.5,
  §6) — 전부 그대로 인용했다.
- QA Agent 불일치를 발견하고 그대로 기록했는가 — **예**(§2.1, §3.3) —
  grep으로 재현 가능하게 근거를 남겼다.
- 새로운 실험·프로토타입·측정을 수행했는가 — **아니오** — §5는
  제안만 하고 구현하지 않았다.
