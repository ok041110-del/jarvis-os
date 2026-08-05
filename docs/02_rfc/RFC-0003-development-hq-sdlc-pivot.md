# RFC-0003: Development HQ를 AI Native SDLC Platform으로 재정의

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (사용자 요청에 따른 방향 전환 제안 정리)
**범위**: Development HQ 내부 구조(Workflow 내용, 내부 조직 구조, Agent 구성,
Capability 목록) — Jarvis OS Architecture Baseline, Meta Architecture,
Concept Model, System Boundary는 변경 대상이 아니다.

> 이 RFC는 Jarvis OS Kernel을 설계하지 않는다.
> 이 RFC는 Development HQ의 내부 구조(Workflow/조직/Agent/Capability)에
> 대한 제안이며, Development HQ Baseline v1.0을 지금 대체하지 않는다.
> Baseline 변경은 ADC → ADR → Baseline Update를 거쳐야만 성립한다.

---

## 0. 이 문서를 읽기 전에 — 이 RFC가 하는 일과 하지 않는 일

이 RFC는 사용자가 제시한 "AI Native SDLC Platform" 방향 전환 요청을
정리한 제안서다. 요청은 10개 산출물(Architecture, Directory Structure,
Domain Model, Interface, Stage Definition, Responsibility Catalog,
Capability Catalog, MVP 재구성 계획, 재사용 코드, 제거 코드)을 요구했고,
이 RFC는 그 10개를 아래 §2~§11에서 각각 다룬다.

다만 이 RFC는 다음을 **결정하지 않는다**.

- Development HQ Baseline v1.0(`development-hq/BASELINE.md`,
  `MISSION.md`, `BOUNDARY.md`, `RESPONSIBILITY.md`, `STRUCTURE.md`)을
  지금 수정하지 않는다. 이 문서들은 여전히 Frozen이다.
- Jarvis OS Architecture Baseline(`docs/01_architecture/BASELINE.md`)을
  수정하지 않는다.
- 아래에서 제안하는 내용 중 Jarvis OS Kernel의 책임 영역(Engine 호출,
  Multi-Engine 지원)과 겹치는 부분은 **이 RFC의 결정 범위 밖**이라고
  명시적으로 표시했다(§4, §12 참조). Development HQ는 그 영역을 스스로
  결정할 권한이 없다(`development-hq/BOUNDARY.md`: "Engine 호출 | Kernel
  Engine Port/Adapter의 책임").

이 RFC가 통과되더라도 다음 절차(ADC → ADR → Baseline Update)를 거치기
전까지는 Development HQ의 실제 코드나 문서가 바뀌지 않는다.

---

## 1. Background

Development HQ MVP-0001~MVP-0003 및 Governance(RFC-0001/0002,
ADC-0001/0002, RT-0001)를 진행하는 과정에서, 다음 오픈소스/플랫폼을
조사했다: OpenHands, Aider, LangGraph, CrewAI, OpenAI Agents SDK, AWS AI
Native SDLC, Anthropic Claude Code Workflow. 그 결과, "Agent를
오케스트레이션하는 Multi-Agent 시스템"보다 "SDLC 전체를 AI 중심으로
오케스트레이션하는 플랫폼"이 Development HQ의 목표(Mission.md: "Jarvis OS
Architecture Baseline v1.0이 실제 도메인에서 성립하는지 검증")에 더
부합한다는 판단이 제기되었다.

## 2. New Philosophy (요청 그대로 인용)

> Development HQ는 AI Agent Platform이 아니다.
> Development HQ는 AI Native Development Platform이다.

Agent를 오케스트레이션하는 것이 목적이 아니라, SDLC 전체(Planning →
Design → Implementation → Validation → Release)를 AI 중심으로
오케스트레이션하는 것이 목적이다. AI(Agent/Model)는 각 단계를 수행하는
실행자(Execution)일 뿐, 설계의 중심이 아니다.

## 3. 기존 Baseline과의 정합성 검토 (중요 발견)

이 제안을 검토하면서, **이 방향 전환의 상당 부분이 실제로는 Architecture
Drift가 아니라는 사실**을 확인했다. 그 근거는 다음과 같다.

- Jarvis OS Architecture Baseline §7 System Boundary는 "Workflow의 도메인
  내용", "HQ 내부 조직 구조", "Agent 구성 및 역할 결정"을 **HQ의 책임**으로
  이미 명시하고 있다. Jarvis OS는 그 내용에 관여하지 않는다.
- `development-hq/STRUCTURE.md`는 이미 "Division과 Team은 Development HQ
  내부의 선택적 관례이며, Jarvis OS Meta Architecture의 필수 계층이
  아니다"라고 선언했다.

즉, "Stage(Repository Intelligence → Planning & Specification →
Architecture & Design → Implementation → Validation → DevOps & Release)"는
**새로운 Jarvis OS Concept이 아니라, Division/Team을 대신하는 Development
HQ 내부의 선택적 조직 구조**로 표현할 수 있다. 이 부분은 Jarvis OS
Architecture Baseline을 전혀 건드리지 않고도 Development HQ Baseline
갱신만으로 반영 가능하다.

반면, **"Model(Claude Code/GPT/Codex/Qwen)은 Execution Layer에서
교체 가능해야 한다"는 부분은 Development HQ의 권한 밖**이다. Engine 호출과
그 표준 인터페이스(Port/Adapter)는 Jarvis OS Kernel의 책임이며
(`development-hq/BOUNDARY.md`), Multi-Engine 지원은 MVP-0001부터 지금까지
명시적으로 Out of Scope였다. 이 부분은 §4와 §12에서 별도로 다룬다.

## 4. 새로운 Architecture (요청 산출물 1)

### 4.1 Development HQ 내부 구조 (HQ의 권한 범위 — 이 RFC가 제안 가능)

```
Development HQ
  ↓ (기존 Division/Team 자리를 대신하는 선택적 내부 구조)
Stage
  ↓
Responsibility
  ↓
Capability
  ↓
Agent (Execution Layer 구현체 중 하나)
```

기존 STRUCTURE.md의 `Workflow → Task → Capability → Agent` 관계는 그대로
유지된다. Stage는 그 위에 놓이는 조직화 계층일 뿐, Task가 Capability를
거쳐 Agent에게 배분되는 관계 자체(Kernel의 Task 배분 책임)는 바뀌지 않는다.

```
Stage
  ↓
Workflow (해당 Stage에 속하는 Task들의 순서)
  ↓
Task
  ↓
Capability
  ↓
Agent (Execution Layer 구현체: Claude Code / Codex / 규칙 기반 함수 등)
```

### 4.2 Execution Layer (HQ의 권한 밖 — Jarvis OS 수준 논의 필요)

"Model은 교체 가능해야 한다"는 요구는 Engine Port/Adapter, 즉 Jarvis OS
Kernel의 책임 영역이다. 이 RFC는 이 부분의 최종 구조를 제안하지 않는다.
대신 현재 상태만 기록한다.

- ADC-0001은 Engine Gateway를 "Keep in MVP"로 판단했다: 단일 함수
  (`call_engine()`)로 충분했고, 승격을 정당화할 관찰(복수 Engine 실사용)이
  없었다.
- RT-0001은 이 Candidate의 재평가 Trigger를 "Engine 수 ≥ 2"로 정의했다.
- 이번 요청("Claude Code/GPT/Codex/Qwen 교체 가능")은 그 Trigger를
  발생시키자는 제안과 사실상 같다. 이는 Development HQ가 혼자 결정할 수
  있는 사안이 아니라, RT-0001이 이미 지정한 재평가 절차(→ 새 RFC
  Observation → ADC)를 따라야 한다.

**결론**: Execution Layer의 Multi-Model 지원 여부는 이 RFC의 §7(MVP 재구성
계획)에서 "관찰을 얻기 위한 별도 MVP"로만 다루고, 이 RFC 자체는 그 구조를
결정하거나 설계하지 않는다.

## 5. Directory Structure (요청 산출물 2)

기존 디렉토리를 삭제하지 않고, Stage 조직화를 얹는 최소 변경안이다. 이는
제안일 뿐이며, ADC 승인 전에는 적용하지 않는다.

```
development-hq/
├── MISSION.md              (기존 유지, 필요 시 ADR 이후 갱신)
├── BOUNDARY.md             (기존 유지)
├── RESPONSIBILITY.md       (기존 유지)
├── STRUCTURE.md            (기존 유지 — Stage를 Division/Team 대체
│                            선택지로 추가하는 형태의 갱신 후보)
├── BASELINE.md             (기존 유지)
├── stages/                 (신규 제안 — 각 Stage의 Responsibility/
│   │                        Capability 문서만 둔다. 실행 코드는 두지
│   │                        않는다)
│   ├── 01_repository_intelligence/
│   ├── 02_planning_specification/
│   ├── 03_architecture_design/
│   ├── 04_implementation/
│   ├── 05_validation/
│   └── 06_devops_release/
└── mvp/                    (기존 유지 — MVP-0001~0003 코드/테스트는
                              삭제하지 않는다. §9 참조)
```

`stages/`는 이번 RFC에서 실제로 생성하지 않는다. ADC가 이 방향을 승인하고
후속 MVP가 계획된 뒤에 만든다.

## 6. Domain Model (요청 산출물 3)

| 개념 | 정의 | 기존 Concept Model과의 관계 |
|---|---|---|
| Stage | SDLC 상의 한 국면(예: Implementation) | 새 Jarvis OS Concept 아님. Development HQ 내부의 선택적 조직 구조(Division/Team과 동일한 지위) |
| Responsibility | 한 Stage 안에서 수행되어야 하는 책임 항목(예: "Unit Test") | 새 Concept 아님. 기존 Task(Process)가 요구하는 내용을 서술하는 방식일 뿐 |
| Capability | Responsibility를 실제로 수행할 수 있는 능력 | 기존 Concept Model의 Capability(Metadata)를 그대로 사용 |
| Execution | Capability를 실제로 실행하는 구현체(Agent, 나아가 Model) | 기존 Concept Model의 Agent(Entity)/Engine Port(Interface)를 그대로 사용. 새 Concept 아님 |

새로 추가되는 Jarvis OS 수준 Concept은 없다. Stage/Responsibility는 Task와
Capability를 조직화하는 명명법일 뿐이며, 이는 이미 Development HQ가
자유롭게 정의할 수 있는 영역(Workflow 내용, 내부 조직 구조)이다.

## 7. Interface (요청 산출물 4)

Development HQ 수준에서 새 Interface를 정의하지 않는다. 기존 MVP-0001의
`call_engine(prompt) -> str` 형태(단일 함수 호출)를 Stage별 Capability
실행에도 그대로 재사용할 것을 제안한다. 즉, 각 Stage의 각 Capability는
"입력을 받아 출력을 반환하는 함수 하나"로 표현되며, 이는 지금 `engine.py`
구조와 동일하다.

Model을 교체 가능한 형태로 만드는 Interface(예: 여러 Model 중 선택하는
표준 인터페이스)는 §4.2에서 설명한 대로 Jarvis OS Kernel의 Engine
Port/Adapter 영역이며, 이 RFC는 그 Interface를 설계하지 않는다.

## 8. Stage Definition (요청 산출물 5)

요청된 6개 Stage를 그대로 채택한다. 각 Stage는 Development HQ 내부의
선택적 조직 구조(Division/Team 대체)로 취급한다.

| Stage | 목적 | Reference |
|---|---|---|
| Repository Intelligence | 프로젝트를 이해한다 | Aider Repository Map |
| Planning & Specification | Intent를 실행 가능한 명세로 변환한다 | AWS AI Native SDLC, Kiro, Claude Code |
| Architecture & Design | 구현 전에 구조를 설계한다 | LangGraph, CrewAI |
| Implementation | 명세를 코드로 구현한다 | Claude Code, OpenHands |
| Validation | 구현 결과를 검증한다 | OpenHands, Claude Code |
| DevOps & Release | 배포와 운영을 자동화한다 | AWS AI Native SDLC |

## 9. Responsibility Catalog (요청 산출물 6)

| Stage | Responsibility |
|---|---|
| Repository Intelligence | Repository 분석, 관련 파일 탐색, Symbol 검색, Dependency 분석, Context 최적화 |
| Planning & Specification | Requirement 분석, User Story 작성, Functional Spec 작성, Non-Functional Spec 작성, Task 분해 |
| Architecture & Design | Architecture 설계, Module 설계, Interface 설계, Workflow 설계, Prototype |
| Implementation | Coding, Refactoring, Git 작업, Documentation |
| Validation | Unit Test, Integration Test, Review, Lint, Security, Performance |
| DevOps & Release | CI, CD, Release, Monitoring |

## 10. Capability Catalog (요청 산출물 7)

`development-hq/STRUCTURE.md`의 기존 Capability 목록은 "예시일 뿐이며
확정 목록이 아니다"라고 이미 명시되어 있다. 아래는 위 Responsibility를
근거로 한 **제안**이며, 기존 목록(`code_generation`, `code_review`,
`deployment`, `design`, `incident_response`, `requirement_analysis`,
`test_execution`)을 대체하지 않고 확장하는 형태다.

| Responsibility | 대응 Capability | 비고 |
|---|---|---|
| Repository 분석 | `repository_analysis` | 신규 제안 |
| 관련 파일 탐색 | `file_discovery` | 신규 제안 |
| Symbol 검색 | `symbol_search` | 신규 제안 |
| Dependency 분석 | `dependency_analysis` | 신규 제안 |
| Context 최적화 | `context_optimization` | 신규 제안 |
| Requirement 분석 | `requirement_analysis` | **기존 목록에 이미 존재** |
| User Story 작성 | `user_story_authoring` | 신규 제안 |
| Functional/NFR Spec | `spec_authoring` | 신규 제안 |
| Task 분해 | `task_decomposition` | 신규 제안 |
| Architecture 설계 | `design` | **기존 목록에 이미 존재** |
| Module/Interface/Workflow 설계 | `design` (세분화 시 `module_design`, `interface_design`) | 기존 `design`으로 우선 흡수 가능 |
| Prototype | `prototyping` | 신규 제안 |
| Coding | `code_generation` | **기존 목록에 이미 존재** |
| Refactoring | `code_generation` (세분화 시 `refactoring`) | 기존 `code_generation`으로 우선 흡수 가능 |
| Git 작업 | `git_operations` | 신규 제안 |
| Documentation | `documentation` | 신규 제안 |
| Unit/Integration Test | `test_execution` | **기존 목록에 이미 존재** |
| Review | `code_review` | **기존 목록에 이미 존재** |
| Lint/Security/Performance | `lint`, `security_review`, `performance_review` | 신규 제안(세분화) 또는 `code_review`로 우선 흡수 |
| CI/CD | `deployment` (세분화 시 `ci_pipeline`, `cd_pipeline`) | 기존 `deployment`로 우선 흡수 가능 |
| Release | `deployment` | **기존 목록에 이미 존재** |
| Monitoring | `incident_response` (세분화 시 `monitoring`) | 기존 `incident_response`와 인접 |

**관찰**: 기존 7개 Capability 중 6개(`code_generation`, `code_review`,
`deployment`, `design`, `incident_response`, `requirement_analysis`,
`test_execution`)가 이미 6개 Stage 전부에 최소 1개씩 대응된다. 즉 기존
Capability 목록은 이미 SDLC 전 단계를 성글게나마 커버하고 있었다 —
"세분화가 필요한가"는 이 RFC가 결정하지 않고, ADC 대상으로 남긴다.

## 11. MVP 재구성 계획 (요청 산출물 8)

새 Architecture를 한 번에 구현하지 않는다. 기존 Governance 흐름(MVP →
RFC → ADC → RT)을 그대로 재사용해, Stage 하나씩 순차적으로 검증한다.

| 다음 MVP 후보 | 검증할 Stage | 재사용 대상 |
|---|---|---|
| MVP-0004(후보) | Implementation | 기존 `mvp/agents.py`의 `backend_agent_code_review`를 "Implementation Stage의 Coding Responsibility" 예시로 재해석 |
| MVP-0005(후보) | Validation | 기존 `mvp/agents.py`의 `qa_agent_test_execution`, MVP-0003의 Task Lifecycle 관찰 결과를 그대로 재사용 |
| MVP-0006(후보) | Repository Intelligence | 신규 Capability(`repository_analysis` 등) 필요 — 이 RFC가 승인된 뒤 별도 ADC 대상 |

각 MVP는 지금까지와 동일한 규율을 따른다: 최소 구현, Architecture Drift
금지, Observation 우선, Stop Trigger 발생 시 RFC로 에스컬레이션.

## 12. 기존 MVP에서 재사용 가능한 코드 (요청 산출물 9)

| 기존 코드 | 재사용 방식 |
|---|---|
| `development-hq/mvp/agents.py`의 `AGENT_CAPABILITY_MAP` | 그대로 유지. Stage 조직화가 추가되어도 Capability→Agent 매핑 자체는 바뀌지 않는다 |
| `development-hq/mvp/agents.py`의 `backend_agent_code_review`, `qa_agent_test_execution` | 각각 Implementation/Validation Stage의 Responsibility 구현 예시로 그대로 재사용 |
| `development-hq/mvp/engine.py`의 `call_engine()` | Execution Layer의 "기본(규칙 기반) 실행자" 자리로 그대로 재사용. Multi-Model 지원이 결정되기 전까지 유일한 Execution 구현체로 유지 |
| `development-hq/mvp/workflow.py`, `workflow_0002.py` | Implementation → Validation 두 Stage에 걸친 Workflow 예시로 그대로 재사용 |
| `development-hq/mvp/tests/test_mvp_0001.py` | Validation Stage 자체 검증(회귀 테스트)으로 그대로 재사용 |
| RFC-0001/0002, ADC-0001/0002, RT-0001 | Governance 흐름 자체를 그대로 재사용. 새 Governance 문서 종류를 만들지 않는다 |

## 13. 제거해야 하는 코드 (요청 산출물 10)

**없음.** MVP-0001~0003의 코드는 모두 리터럴 딕셔너리, 단일 함수 호출,
하드코딩된 조건 분기 수준이며, 이는 "Multi-Agent 오케스트레이션 프레임워크"
성격을 띠지 않는다. Stage 기반 재조직은 기존 코드를 삭제할 이유를 만들지
않는다. 필요하다면 파일 위치 이동(예: `mvp/agents.py`의 일부 함수를
`stages/04_implementation/`, `stages/05_validation/` 문서가 참조하는
형태)만 있을 뿐, 삭제 대상은 없다.

## 14. Boundary Risk (Architecture 문제 기록 — 직접 해결하지 않음)

- **Execution Layer의 Multi-Model 지원**은 Jarvis OS Kernel의 Engine
  Port/Adapter 책임과 겹친다. Development HQ Governance만으로는 결정할
  수 없으며, Jarvis OS 수준의 ADC(ADC-01, ADC-03)와 `RFC_CANDIDATES.md`
  Candidate 3(Engine의 재정의)·Candidate 4(Engine 다대다 공유)의 정식 RFC
  승격이 선행되어야 한다.
- 이 사실은 여기 기록만 하며, 이 RFC는 그 경계 문제를 해결하지 않는다.

## Non-goals

- 이 RFC는 Development HQ Baseline이나 Jarvis OS Architecture Baseline을
  지금 변경하지 않는다.
- 이 RFC는 Execution Layer(Multi-Model 실행)의 최종 구조를 설계하지
  않는다.
- 이 RFC는 `stages/` 디렉토리나 신규 Capability를 지금 생성/구현하지
  않는다.
- 이 RFC는 RFC-0001/0002, ADC-0001/0002, RT-0001을 수정하지 않는다.

## 다음 절차

이 RFC는 ADC-0003에서 다음을 개별적으로 판단할 것을 제안한다.

1. Stage 기반 내부 조직화(§4.1, §5, §6, §8)를 Development HQ Baseline
   갱신 대상으로 채택할지
2. Capability Catalog 확장(§10)을 채택할지, 기존 7개로 유지할지
3. MVP-0004 이후 계획(§11)을 승인할지
4. Execution Layer의 Multi-Model 지원(§4.2, §14)은 Development HQ ADC의
   범위가 아니라 Jarvis OS 수준 RFC로 별도 상정할지

이 RFC 자체는 위 4개 중 어느 것도 결정하지 않는다.
