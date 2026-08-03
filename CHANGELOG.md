# Changelog

이 문서는 Jarvis OS Platform의 버전별 변경 사항을 기록한다. 형식은
[Keep a Changelog](https://keepachangelog.com/)를 참고하되, 이 저장소의 성격(Architecture
Validation 중심 PoC)에 맞게 `Added`/`Changed`/`Validated`/`Known Gap` 4개 섹션을 쓴다.

## [1.0.0] — 2026-08-03

Jarvis OS **Platform** v1.0 Release (Architecture Frozen). Application Release가 아니다 —
자세한 범위는 `RELEASE_NOTES_v1.0.md` 참고.

### Added

- `packages/core`: Kernel(Intent Recognition/Task Classification/Task Router/HQ
  Selection), Capability Registry, Policy 모델, Lifecycle(HQ 상태 전이), Connector
  Domain Model + Connector Registry, Workflow Domain Model(`WorkflowResult`/
  `WorkflowStatus`), Organization 엔티티(HQ/Division/Team/Agent), Application
  Services(`HQProvisioner`, `AgentExecutor`), 7개 Core Port.
- `adapters/`: lifecycle-statemachine, capability-provider-yaml,
  capability-store-sqlite(미사용), policy-casbin, policy-inmemory,
  connector-mcp, connector-mock, connector-discovery-entrypoint,
  workflow-langgraph, workflow-sequential — 10개 Adapter 패키지.
- `hqs/development-hq`, `hqs/investment-hq` — Capability 선언 + 최소 Division/Agent 골격.
- `apps/poc-runner` — 유일한 Composition Root.
- `tests/e2e`(10 tests), `tests/integration`(9 files) — 총 47 tests/143 subtests.
- `docs/adr/0001`~`0007` — 전부 Accepted.
- `docs/architecture-review/architecture-review-v1.md` — Repository 전체 Architecture Review.
- `docs/architecture/ARCHITECTURE_FREEZE_v1.0.md` — Freeze 선언 및 조건.
- `docs/reports/platform-v1-final-report.md` — Platform v1.0 최종 보고서.
- `RELEASE_NOTES_v1.0.md`, `VERSION`, `CHANGELOG.md`(이 문서).

### Changed

- 모든 workspace 패키지(`packages/*`, `adapters/*`, `hqs/*`, `apps/poc-runner`)의
  버전을 `0.1.0` → `1.0.0`으로 통일.
- `README.md`를 Platform 기준으로 전면 갱신(Vision/Core Principles/Architecture/
  Repository Structure/Architecture Validation/Current Status/Roadmap/Repository
  Map/Getting Started 구성, 상단에 Platform/Architecture/Version 배지 추가).
- Walking Skeleton(In-Memory/Mock adapter)을 Phase 1~5에 걸쳐 실제 오픈소스
  Adapter(python-statemachine, Casbin, MCP, LangGraph)로 순차 교체.
- `apps/poc-runner/main.py` Stage 8을 "Composition Root가 Connector 대행 호출"에서
  "Agent가 AgentExecutor를 통해 Connector를 직접 호출"하는 구조로 이동(Phase 5).

### Validated

- **Adapter Reversibility** — 5개 Domain(Lifecycle/Capability/Policy/Connector/
  Workflow) 전부에서 "구현체를 제거하고 다른 구현체로 교체해도 Core 무수정"을 증명.
- **Capability 기반 자동 Discovery** — 새 HQ, 새 Connector를 코드 수정 없이 추가/제거해도
  자동 Discovery + Registration이 유지됨.
- **Fail-Closed 계약** — `IPolicyEngine.evaluate()`, `IConnector.call_tool()`,
  `IWorkflowEngine.run()` 모두 예외 대신 실패를 명시적 반환값으로 표현.
- **Stage 8 Agent-Connector 직접 호출** — Kernel/HQ/Division 무수정으로 동작함을 실제
  Kernel Stage 1~6 경로 + 정적 소스 검사로 증명.
- **Layer Dependency / Dependency Rule / Core 순수성** — Repository Architecture
  Review에서 위반 사례 0건 확인.
- 전체 테스트: 47 tests / 143 subtests, 전부 통과.

### Known Gap

- `Agent.required_tools`가 `HQProvisioner`에서 실제로 채워지지 않음 (최우선, v1.1 이전 해소 권고).
- Workflow Cancellation 실제 메커니즘 미구현(Domain 개념만 존재).
- 병렬 실행의 실제 동시성/성능 미검증(구조만 검증됨).
- Connector Lifecycle State 정의만 되고 전이 로직 없음.
- fetch MCP 레퍼런스 서버 미연결(SDK 버전 비호환).
- Event Bus 기술 미선정 + 최소 구현 미착수(Port docstring이 아직 이행되지 않은 약속을 담고 있음).
- `tests/unit/` 부재(integration이 대신 수행 중).
- Git tag(`phase-4-complete`, `phase-5-complete`, `v1.0.0`, `Architecture-Freeze-v1.0`)와
  일부 원격 branch 정리 push가 조직 egress 정책으로 403 차단(반복 재발, 로컬에는 존재).
- Division/Agent 최소 관례(1:1, tool 없음) 재설계 안 됨.
- `capability-store-sqlite` 미사용 스켈레톤, 거취 미정.
