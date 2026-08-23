# DEV-HQ-V2.0 — Agent Definition

**문서 성격**: Audit(READ 중심). 새 RFC/ADC/ADR을 작성하지 않는다.
Architecture/Contract/Runtime/Agent Implementation을 변경하지 않는다.
새 Agent·새 Capability를 도입하지 않는다. `hqs/development/mvp/agents.py`,
`engine.py`, `hqs/development/stages/`의 실제 구현과 기존 Governance/
Evidence(`STRUCTURE.md`, `IMPLEMENTATION_RULES.md`, `HANDOVER.md`,
`DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md`,
`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`)를 기준으로 Agent 종류와
Responsibility를 확정한다.

## 1. 확정된 Agent 목록

현재 실제 구현(`agents.py`)에 존재하는 Agent는 **4개**이며, 후보로
제시된 4개와 정확히 일치한다. 새 Agent를 추가하지 않는다.

| Agent | 근거(코드) |
|---|---|
| Requirements Agent | `requirements_agent_requirement_analysis()` |
| Design Agent | `design_agent_design()` |
| Backend Agent | `backend_agent_code_review()`, `backend_agent_code_generation()` |
| QA Agent | `qa_agent_test_execution()` |

`STRUCTURE.md` "Agent (예시)"에는 이 4개 외에 Frontend Agent/Ops
Agent/Release Agent도 예시로 나열되어 있으나, 이들은 예시일 뿐 실제
구현에 존재하지 않는다 — 이번 확정 대상에서 제외한다(§6).

## 2. Agent Responsibility

### Requirements Agent

| 항목 | 내용 |
|---|---|
| Responsibility | Feature Request/Issue를 분석해 요구사항(목표/범위/위험)을 프로즈로 서술 |
| Capability | `requirement_analysis` |
| Input | `issue: dict`(`title`, `description`) |
| Output | `str`(요구사항 프로즈, 코드 미포함) |
| 담당하지 않는 영역 | 설계(Design Agent), 코드 작성(Backend Agent), 검증(QA Agent) |
| 실제 구현 근거 | `agents.py:57-65` `requirements_agent_requirement_analysis()` — "describe... do not write code" 지시 포함 |

### Design Agent

| 항목 | 내용 |
|---|---|
| Responsibility | Requirement을 입력받아 설계(접근법/책임/위험)를 프로즈로 서술 |
| Capability | `design` |
| Input | `issue: dict`, `requirement: str`(Requirements Agent Output) |
| Output | `str`(설계 프로즈, 코드 미포함) |
| 담당하지 않는 영역 | 요구사항 분석(Requirements Agent), 코드 작성(Backend Agent), 검증(QA Agent) |
| 실제 구현 근거 | `agents.py:68-76` `design_agent_design()` — "describe a design... do not write code yet" 지시 포함 |

### Backend Agent

| 항목 | 내용 |
|---|---|
| Responsibility | (1) 코드를 리뷰해 실이슈를 서술 (2) 설계/입력을 코드로 구현 |
| Capability | `code_review`, `code_generation` |
| Input | `code_review`: `code: str` / `code_generation`: `design: str`(또는 Stage 04 조립 입력) |
| Output | `code_review`: `str`(리뷰 프로즈, 이슈 없으면 `NO_ISSUES_FOUND` 마커) / `code_generation`: `str`(코드만, fence 제거됨) |
| 담당하지 않는 영역 | 요구사항 분석(Requirements Agent), 설계(Design Agent), 테스트 케이스 제안(QA Agent) |
| 실제 구현 근거 | `agents.py:23-44` `backend_agent_code_review()`, `agents.py:88-96` `backend_agent_code_generation()` |

### QA Agent

| 항목 | 내용 |
|---|---|
| Responsibility | 코드와 그 리뷰를 근거로 테스트 케이스를 제안(프로즈) |
| Capability | `test_execution` |
| Input | `code: str`, `review: str`(Backend Agent `code_review` Output) |
| Output | `str`(제안된 테스트 케이스 목록, 프로즈) |
| 담당하지 않는 영역 | 코드 리뷰/작성(Backend Agent), 요구사항/설계(Requirements/Design Agent), 실제 테스트 실행(Stage 05가 별도로 `pytest` subprocess 실행 — §5 참고) |
| 실제 구현 근거 | `agents.py:47-54` `qa_agent_test_execution()` |

## 3. Capability Mapping

현재 실제 구현을 기준으로 후보 매핑을 그대로 확정한다. 변경 근거 없음.

| Capability | Agent | 매핑 근거 |
|---|---|---|
| `requirement_analysis` | Requirements Agent | `HELLO_SDLC_CAPABILITY_MAP["requirement_analysis"] == "Requirements Agent"`, `agents.py:14` |
| `design` | Design Agent | `HELLO_SDLC_CAPABILITY_MAP["design"] == "Design Agent"`, `agents.py:15` |
| `code_review` | Backend Agent | `AGENT_CAPABILITY_MAP["code_review"] == "Backend Agent"`, `agents.py:7` — `test_mvp_0001.py:55-58`가 리터럴 값으로 고정 검증 |
| `code_generation` | Backend Agent | `HELLO_SDLC_CAPABILITY_MAP["code_generation"] == "Backend Agent"`, `agents.py:16` |
| `test_execution` | QA Agent | `AGENT_CAPABILITY_MAP["test_execution"] == "QA Agent"`, `agents.py:8` — `test_mvp_0001.py:55-58`가 리터럴 값으로 고정 검증 |

5개 Capability 모두 정확히 하나의 Agent에 귀속되며, 두 Agent가 같은
Capability를 공유하거나 한 Capability가 여러 Agent에 걸치는 사례는
없다(§8 검증 항목 충족).

`AGENT_CAPABILITY_MAP`(2개 항목, `test_mvp_0001.py`가 리터럴 값으로
고정)과 `HELLO_SDLC_CAPABILITY_MAP`(3개 항목)은 서로 다른 딕셔너리이며
합쳐서 5개 Capability를 이룬다 — 하나로 통합하면
`IMPLEMENTATION_RULES.md`의 "Registry 일반화 금지"에 저촉되므로 현재
분리 상태를 유지한다(`agents.py:11-12` 주석).

## 4. Stage와 Agent 관계

Stage는 Workflow 실행 단계이고 Agent는 그 단계에서 Capability를
수행하는 논리적 역할이다 — 1:1로 강제되지 않는다. 실제 호출 관계
(`hqs/development/workflow.py`, `stages/0N/stage_0N.py` 확인 기준):

| Stage | 호출하는 Agent Capability | 비고 |
|---|---|---|
| Stage 01 (Context Analysis) | 없음 | `project_intelligence.py`/`ast_context.py`의 결정적 함수만 사용, Engine 미호출 — Agent Capability 없음 |
| Stage 02 (Planning & Specification) | Requirements Agent → `requirement_analysis` | Stage 01 Output을 골격으로 재배치 후 기존 Capability 그대로 재사용(신규 Engine 호출 없음) |
| Stage 03 (Architecture & Design) | Design Agent → `design` | Stage 01/02 Output을 골격으로 재배치 후 기존 Capability 그대로 재사용 |
| Stage 04 (Implementation) | Backend Agent → `code_generation` | Design + AST Closure/Exposure 조립 입력을 기존 Capability에 전달 |
| Stage 05 (Validation) | Backend Agent → `code_review`(Evidence 전용, 판정에 미반영) | 판정(PASS/FAIL/PARTIAL) 자체는 Engine 미호출, 결정적 규칙(`_determine_verdict()`)으로만 산출 |

**주의 — 이름은 같지만 다른 것**: Stage 05의 "Capability 4:
Test Execution / Regression Detection"은 `stage_05._run_pytest_with_
applied_implementation()`이 실제 `pytest`를 subprocess로 직접 실행하는
결정적 검사이며, QA Agent의 `test_execution` Capability(Engine을 호출해
테스트 케이스를 프로즈로 제안)와는 별개다. 두 곳 모두 "test_execution"
이라는 이름을 쓰지만 하나는 Agent Capability(Engine 호출, 프로즈
제안), 다른 하나는 Stage 05 고유의 결정적 회귀 검사(Engine 미호출,
실제 실행)다 — 혼동하지 않도록 이 문서에 명시한다. QA Agent의
`test_execution` Capability는 Stage 01~05 Integrated Workflow에서는
호출되지 않으며, `mvp/workflow_hello_sdlc.py`(Hello SDLC)와
`mvp/workflow_0002.py`(MVP-0002)에서만 실제로 호출된다.

## 5. Architecture / Contract 영향

- **Architecture**: 변경 없음. `Agent Role → Capability → call_engine()`
  구조(`STRUCTURE.md`의 `Workflow → Task → Capability → Agent` 모델을
  Runtime 없이 명명 규칙으로 구현한 것)를 그대로 유지했다. Agent
  class/Runtime/Registry/Manager/신규 orchestration layer/신규
  Capability를 도입하지 않았다(§4 지시 준수, `IMPLEMENTATION_RULES.md`
  Stop Trigger 미발동).
- **Contract**: 변경 없음. `AGENT_CAPABILITY_MAP`(2개), `HELLO_SDLC_
  CAPABILITY_MAP`(3개) 값과 각 Agent 함수 시그니처를 그대로 인용만
  했다. `test_mvp_0001.py`의 리터럴 고정 검증과 충돌하지 않는다.
- **Runtime**: 변경 없음. Runtime 자체가 Kernel 범위 Open Decision
  (ADC-02)이며 이 문서는 그 경계를 재확인했을 뿐이다.
- **Agent Implementation**: 변경 없음. `agents.py`/`engine.py`/
  `stages/*.py` 어떤 파일도 수정하지 않았다.
- **기존 Freeze와의 관계**: `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` §1이
  이미 "Agent Layer Readiness Review 완료"를 Freeze 근거로 포함하고
  있으며, 이 문서는 그 결론(Runtime 없는 Capability 함수 명명 규칙이
  Architecture 문서와 일치)을 Agent 단위로 세분화해 재확인한 것이다 —
  Freeze 선언 자체를 재론하거나 변경하지 않는다.

## 6. 추가 Agent 필요 여부

**불필요.** 현재 4개 Agent와 5개 Capability만으로 Stage 01~05 +
Hello SDLC + MVP-0002 전체가 커버된다. `STRUCTURE.md`가 예시로 든
Frontend Agent/Ops Agent/Release Agent(그리고 `deployment`/
`incident_response` Capability)는 실제 구현·실제 Workflow 어디에도
쓰이지 않으므로 이번 확정 대상에 포함하지 않는다. 새 Agent 추가는
다음 조건을 모두 만족할 때만 RFC → ADC → ADR 절차로 검토한다:

1. 실제 Workflow/Stage가 현재 5개 Capability로 커버되지 않는 새
   Capability를 필요로 하는 구체적 사례가 발생했을 때(추측성 확장
   금지).
2. 그 Capability가 기존 4개 Agent 중 어느 하나의 Responsibility로도
   자연스럽게 흡수되지 않을 때.
3. `IMPLEMENTATION_RULES.md`의 "구현 중 새 Capability/Agent 추가 금지"
   원칙에 따라, 추가 여부 자체를 구현 세션이 스스로 결정하지 않고
   Governance 절차로 넘길 때.

## 7. 검증 결과 (§8 대응)

| 검증 항목 | 결과 |
|---|---|
| 모든 현재 Agent Capability가 정확히 하나의 Agent에 귀속되는가 | 예(§3) |
| 중복 Responsibility가 없는가 | 예 — 4개 Agent의 Responsibility가 서로 겹치지 않음(§2). Stage 05 "test_execution"은 이름만 같은 별개 검사이며 QA Agent Responsibility와 겹치지 않음(§4 주의 항목) |
| 현재 구현과 문서가 일치하는가 | 예 — 모든 서술이 실제 코드(`agents.py`, `stages/*.py`, `test_mvp_0001.py`)를 근거로 함 |
| 기존 Freeze/Governance와 충돌하지 않는가 | 예 — `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`, `DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md`, `IMPLEMENTATION_RULES.md`, `STRUCTURE.md`와 모두 일치, 신규 결정 없음 |
| 새로운 Agent를 불필요하게 추가하지 않았는가 | 예 — 4개 그대로 확정, 예시 목록의 미구현 Agent는 제외 |

## 8. 다음 Refactoring 구조 제안

이번 Audit은 Production Code를 변경하지 않았으므로 아래는 제안일 뿐,
이 세션에서 실행하지 않는다.

- Stage 05의 "Test Execution / Regression Detection" 항목과 QA Agent의
  `test_execution` Capability가 이름이 같아 혼동 여지가 있다는 점을
  `stages/05_validation/CAPABILITIES.md`에 상호 참조 각주로 명시하는
  것을 향후 문서 전용 세션에서 고려할 수 있다(§4 주의 항목과 동일
  내용, Contract/코드 변경 없음).
- `STRUCTURE.md`의 Agent 예시 목록(Frontend/Ops/Release Agent)과 실제
  구현 4개 Agent 사이의 간극은 예시와 확정 목록의 성격 차이이므로
  수정이 필요하지 않다 — 다만 향후 새 Agent 추가 논의가 열릴 때
  참고 목록으로 그대로 유지한다.
