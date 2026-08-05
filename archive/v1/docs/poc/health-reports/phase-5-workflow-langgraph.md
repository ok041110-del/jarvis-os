# Repository Health Report — Phase 5 (Workflow Adapter, LangGraph)

날짜: 2026-08-03
범위: `packages/core`에 Workflow Domain Model(`workflow/models.py` —
`WorkflowResult`/`WorkflowStatus`) 신규 추가, `ports/i_workflow_engine.py`를
빈 docstring에서 `IWorkflowEngine.run(team, dispatch) -> WorkflowResult`로
채움, `application/agent_executor.py`(Application Service, Domain Service
아님) 신규 추가. `adapters/workflow-langgraph`를 실제 LangGraph `StateGraph`
구현으로 채움(Agent별 Node로 fan-out/fan-in하는 병렬 실행 가능 구조),
`adapters/workflow-sequential` 신규(Adapter Reversibility 증명 전용).
`apps/poc-runner/main.py` Stage 8을 "Composition Root가 Connector 대행 호출"
에서 "Agent가 AgentExecutor를 통해 Connector를 직접 호출"하는 구조로 이동,
Stage 6(Division Selection)·Kernel(Stage 1~5)은 무수정. 신규 통합 테스트
2개 파일(Adapter Reversibility + Contract Parity, Stage 8 Agent-Connector
직접 호출). ADR-0007 신규(Accepted, 사용자 피드백 3건 반영: Workflow
Registry 미도입, Agent Lifecycle 범위 제외, Stage 8 최소 변경 원칙).

| 항목 | 점수 | 근거 |
|---|---|---|
| Architecture | 94 | ADR-0007의 12개 결정이 대부분 코드로 검증됨: Workflow Engine은 무엇을 실행할지 결정하지 않고 Team~Agent 실행 순서만 조립(결정 1), Team의 생명주기 전이 규칙(`assert` 강제)은 `organization/entities.py`에 그대로 남아 Workflow Engine은 `activate()`/`complete()`/`terminate()`를 호출만 함(결정 2, git diff로 무수정 확인), LangGraph의 `StateGraph`/Node/`START`/`END` 문법이 `adapters/workflow-langgraph` 내부에만 존재(결정 4), Workflow Registry/Discovery/Capability를 도입하지 않고 `build_world()`가 직접 구성(결정 12, 사용자 피드백 1 반영), Agent 전용 State Machine을 추가하지 않고 "Agent = Workflow 실행 단위"까지만 정의(결정 3, 사용자 피드백 2 반영), Stage 8 이동이 "Connector 호출 주체 이동" 하나로 한정되고 Kernel/HQ/Division은 git diff로 무수정 확인(결정 3 최소 변경 원칙, 사용자 피드백 3 반영), Fail-Closed 계약이 `IWorkflowEngine.run()`에 그대로 적용되어 내부 오류/Connector 부재 시에도 예외 없이 `WorkflowResult(FAILURE)` 반환(결정 6/9). 6점 감점 사유: (1) 병렬 실행(결정 7)은 "구조"만 구현되었을 뿐(LangGraph의 fan-out/fan-in Node) 실제 동시성 제어나 성능은 검증하지 않음(사용자가 이번 Phase 범위에서 명시적으로 제외), (2) Workflow Cancellation(결정 10)은 Domain 개념(`WorkflowStatus.CANCELLED`)만 존재하고 실제 취소 메커니즘은 구현하지 않음(ADR이 이미 예고). |
| Documentation | 93 | ADR-0007이 배경·12개 결정·근거·6개 기각 대안(Workflow Registry 도입 포함)·영향 범위·DoD를 모두 포함하며, 사용자 피드백 3건(Workflow Registry 미도입, Agent Lifecycle 제외, Stage 8 최소 변경) 반영 후 Accepted로 승격된 이력이 커밋 메시지와 ADR 본문에 남아 있음. `agent_executor.py`의 docstring이 "Application Service이지 Domain Service가 아니다"라는 경계를 명시적으로 설명하고, 담당하는 것/담당하지 않는 것을 목록으로 구분. 7점 감점 사유: LangGraph의 fan-out/fan-in을 통한 "병렬 실행 가능한 구조"라는 설명이 코드 주석에만 있고, 이 구조가 실제 동시 실행을 보장하지는 않는다는 점(LangGraph의 실행 스케줄링 세부사항)이 별도로 강조되지 않음 — 향후 실제 병렬 스케줄링 Phase에서 오해의 소지가 될 수 있음. |
| Implementation | 90 | `LangGraphWorkflowEngine`이 실제 `langgraph`(1.2.10) `StateGraph`로 Team 활성화 → Agent별 Node(fan-out) → Team 종료(fan-in) 그래프를 구성해 실행. `SequentialWorkflowEngine`이 동일 계약을 순차 함수 호출로 재현. `AgentExecutor`가 Agent.required_tools → ConnectorRegistry.find_by_capability() → ToolRequest/ToolResponse라는 ADR-0006 경로를 그대로 재사용. 실제 `python -m jarvis_poc_runner.main` 실행으로 4개 시나리오 전부 기존과 동일한 결과 확인(회귀 없음), Phase 4 데모(실제 MCP filesystem 서버 호출)도 무수정으로 동작. 10점 감점 사유: (1) `LangGraphWorkflowEngine._build_graph()`가 `run()`마다 그래프를 새로 컴파일함(Team마다 Agent 수가 달라질 수 있어 그래프를 캐시하지 않음) — PoC 규모에서는 문제없으나 반복 호출 시 컴파일 오버헤드가 누적됨, (2) Agent.required_tools 미채움 Known Gap(Phase 2/4부터 이월, 이번 Phase도 의도적으로 미해결)으로 인해 `main.py`의 실제 데모 실행에서는 Stage 8의 Agent→Connector 직접 호출 경로가 실전 데이터로는 발동하지 않음 — 통합 테스트의 Fixture Agent로만 이 경로가 검증됨. |
| Tests | 92 | 신규 `test_workflow_adapter_reversibility.py`(7 tests: Contract Parity 3건 — 성공/실패/빈 Team, Adapter Reversibility 1건, Fail-Closed 3건)와 `test_stage8_agent_calls_connector.py`(2 tests: Agent가 Connector를 직접 호출하는 경로가 LangGraph/Sequential 양쪽에서 동작함을 실제 Kernel Stage 1~5 + HQ Division Selection을 거쳐 증명, Kernel/HQ/Capability Registry/Lifecycle 소스에 "workflow" 문자열이 전혀 없음을 정적으로 확인). 기존 e2e(10개) + Phase 1~4 integration 전부 무수정 통과(총 47 tests/143 subtests, 회귀 없음). 8점 감점 사유: LangGraph의 병렬 fan-out 구조가 실제로 동시에 실행되는지(스레드/비동기 수준)를 검증하는 테스트가 없다 — Contract 동일성만 확인했을 뿐 "구조가 병렬을 지원하는가"의 실행 수준 증거는 아직 없음(사용자가 이번 Phase에서 명시적으로 범위 제외한 부분과 일치). |
| Technical Debt | 87 | 새로 추가된 부채: (1) `LangGraphWorkflowEngine`이 `run()`마다 그래프를 재컴파일하는 설계(Implementation 항목에서 이미 지적), (2) `workflow-sequential`이 entry point를 선언하지 않고 프로덕션 배선에도 쓰이지 않아 "왜 존재하는가"가 패키지 docstring에만 있고 이번에 `PROJECT_CONTEXT.md`에도 함께 반영 필요, (3) `AgentExecutor`가 여전히 `agent.required_tools[0]`(리스트의 첫 항목)만 사용함 — 한 Agent가 여러 Capability를 요구하는 시나리오는 아직 다루지 않음(Phase 4부터 동일하게 이어진 단순화, 이번 Phase에서 확대하지 않음). |
| Known Gap | 90 | 이번 Phase가 새로 만든 Known Gap: 병렬 실행의 실제 동시성 미검증(ADR-0007 결정 7이 이미 "구조만" 검증하기로 범위를 좁혀 둠, Architecture 리스크 없음), Workflow Cancellation 미구현(결정 10이 이미 예고), LangGraph 그래프 재컴파일 오버헤드(Health 감점 사유이지 Architecture 문제 아님). 기존 Known Gap 중 `Agent.required_tools` 미채움(Phase 2/4)은 사용자 지시로 이번 Phase에서도 명시적으로 이월(Fixture Agent로 우회 검증), 나머지(main.py 함수 인자 개수, `tests/unit/` 부재, git tag push 403)도 그대로 이월됨. |
| Repository Readiness | 93 | `uv sync`/`uv run pytest` 전체 통과(47 tests/143 subtests). `packages/core`는 `ports/i_workflow_engine.py` 시그니처 채움 + `workflow/`, `application/agent_executor.py` 신규 추가만 있고 `kernel/`, `policy/`, `lifecycle/`, `organization/`, `capability_registry/`, `connector_registry/`, `connector/`는 git diff로 무수정 확인됨(`git diff origin/main --stat -- packages/core/src/jarvis_core/kernel packages/core/src/jarvis_core/policy packages/core/src/jarvis_core/lifecycle packages/core/src/jarvis_core/organization packages/core/src/jarvis_core/capability_registry packages/core/src/jarvis_core/connector_registry packages/core/src/jarvis_core/connector`가 빈 결과를 반환). 실제 `python -m jarvis_poc_runner.main` 실행으로 4개 시나리오 전부 LangGraph 경유로 기존과 동일한 결과 확인. 7점 감점 사유: `workflow-sequential`이 워크스페이스에는 설치되지만 어떤 프로덕션 패키지도 의존하지 않아 "미사용 코드처럼 보일 위험"이 있음(문서화로 완화했으나 Phase 4의 `connector-mock`과 동일한 구조적 특징이며 새로운 리스크는 아님). |

**총평**: Phase 5는 ADR-0007이 규정한 결정 사항(Workflow Engine 책임 한정, Team 생명주기 Core 소유 유지, Agent 실행 모델, LangGraph Adapter 분리, Team/Division 경계, Failure/Fail-Closed, Event Bus 분리, IWorkflowEngine Port, Cancellation Domain 개념, Workflow State Model, Workflow Registry 미도입, Stage 8 최소 변경 원칙)을 대부분 코드와 실제 LangGraph 실행으로 검증했습니다. 이번 Phase의 최종 Architecture Validation 목표 두 가지 — "LangGraph를 제거하고 Sequential Workflow Adapter로 교체해도 Core와 Organization Layer를 수정하지 않는다"와 "Stage 8에서 Agent가 Connector를 직접 호출하는 구조가 Core 수정 없이 동작함을 증명한다" — 는 각각 `test_workflow_adapter_reversibility.py`와 `test_stage8_agent_calls_connector.py`로 실증되었습니다. 병렬 실행의 실제 동시성 검증, Workflow Cancellation의 실제 구현, `Agent.required_tools` Known Gap 해소는 모두 사용자 지시로 명시적으로 범위 밖에 두었으며 은폐된 감점 요인은 없습니다.

## 다음 단계 권고 (사용자 계획과 일치)
Phase 5 병합 완료 후 사용자가 예고한 Repository 전체 관점의 Architecture Review(전체 ADR 일관성, Layer Dependency, Package Structure, Known Gap 정리, Technical Debt, Jarvis OS v1.0 Readiness)에서 함께 다룰 것을 제안하는 항목:
1. `Agent.required_tools`를 실제로 채우는 방법(HQProvisioner 확장 또는 Capability 스키마 확장) — Phase 2/4/5에 걸쳐 세 번 이월된 Known Gap.
2. `LangGraphWorkflowEngine`의 그래프 캐싱 여부 — 실제 병렬 스케줄링이 도입되는 시점에 함께 재검토.
3. `main.py`의 함수 인자 개수 문제(Context 객체 리팩터링) — Phase 1부터 다섯 번째로 이월.
4. Workflow Cancellation/병렬 실행의 실제 구현 — 별도 Phase로 분리할지, 이번 Review에서 Phase 6 계획으로 확정할지.
