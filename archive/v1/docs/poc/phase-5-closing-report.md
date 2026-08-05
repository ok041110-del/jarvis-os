# Phase 5 종료 보고서 — Workflow Adapter (LangGraph)

날짜: 2026-08-03
main 기준 commit: `fbded84`

## 완료된 Phase

| Phase | 내용 | 상태 |
|---|---|---|
| Phase 1 | Lifecycle Adapter (python-statemachine) | 완료 |
| Phase 2 | Capability YAML Loader | 완료 |
| Phase 3 | Policy Adapter (Casbin) | 완료 |
| Phase 4 | Connector (MCP) | 완료 |
| Phase 5 | Workflow (LangGraph Core) | **완료 (이번 보고서 대상)** |

## 완료된 ADR

| ADR | 제목 | 상태 |
|---|---|---|
| ADR-0001 (구 ADR v1) | OSS 선정 및 재검증 원칙 | Accepted |
| ADR-0002 | Capability 스키마/YAML 로딩 격차 기록 | Accepted (기록 목적) |
| ADR-0003 | Domain Port Definition & Adapter Reversibility Principles | Accepted |
| ADR-0004 | Capability Registration Model | Accepted |
| ADR-0005 | Policy Decision Model | Accepted |
| ADR-0006 | Connector Execution Model | Accepted |
| **ADR-0007** | **Workflow Execution Model** | **Accepted** |

## 현재 Repository 구조

```
jarvis-os/
├── adapters/
│   ├── capability-provider-yaml/         (Phase 2, 실사용)
│   ├── capability-store-sqlite/          (미사용 스켈레톤)
│   ├── connector-discovery-entrypoint/   (Phase 4, 실사용 — entry point 기반 Discovery)
│   ├── connector-mcp/                    (Phase 4, 실사용 — 실제 MCP filesystem 서버 연동)
│   ├── connector-mock/                   (Adapter Reversibility 증명 전용, Discovery 미참여)
│   ├── lifecycle-statemachine/           (Phase 1, 실사용)
│   ├── policy-casbin/                    (Phase 3, 실사용)
│   ├── policy-inmemory/                  (Adapter Reversibility 증명 전용)
│   ├── workflow-langgraph/               (Phase 5, 실사용 — LangGraph StateGraph)
│   └── workflow-sequential/              (Adapter Reversibility 증명 전용, Discovery 없음)
├── apps/
│   └── poc-runner/                       (유일한 Composition Root)
├── docs/
│   ├── adr/                              (ADR-0000~0007)
│   ├── architecture/v1.0/                (Frozen 설계 문서)
│   ├── poc/health-reports/               (Phase별 Repository Health Report)
│   ├── research/, roadmap/
├── hqs/
│   ├── development-hq/, investment-hq/
├── packages/
│   ├── core/                             (Hexagonal Architecture의 Core — Kernel, Policy, Lifecycle,
│   │                                       Capability Registry, Connector/Connector Registry, Workflow
│   │                                       Domain Model, Organization, Ports, Application Services
│   │                                       [HQProvisioner, AgentExecutor])
│   └── shared/
└── tests/
    ├── e2e/          (10 tests — Must #1~11 대응)
    ├── integration/  (Phase별 Adapter 검증 — Lifecycle 6, Capability 7, Policy 4, Connector 11, Workflow 9)
    └── unit/         (비어 있음 — 알려진 격차, 이월)
```

`packages/core`에 이번 Phase에서 신설된 것은 `workflow/`(Domain Model:
`WorkflowResult`/`WorkflowStatus`)와 `application/agent_executor.py`(Application
Service) 두 개뿐이며, `ports/i_workflow_engine.py`는 기존 빈 파일에 시그니처만
채워졌다. `kernel/`, `policy/`, `lifecycle/`, `organization/`,
`capability_registry/`, `connector_registry/`, `connector/`는 git diff로
무수정 확인됨.

## 현재 Architecture Validation 완료 항목

- **Phase 1**: Lifecycle Adapter(python-statemachine)를 제거하고 Core 직접 호출로 되돌려도 Core 무수정으로 즉시 복구 가능함.
- **Phase 2**: 새 HQ를 코드 수정 없이 추가/제거해도 자동 Discovery + 자동 Registration + 정상 Routing이 유지됨.
- **Phase 3**: Policy Engine 구현체(Casbin)를 제거하고 다른 구현체(InMemory)로 교체해도 Core와 Kernel을 수정하지 않는다.
- **Phase 4**: Connector 구현체(MCP)를 제거하고 다른 구현체(Mock)로 교체해도 Core와 Agent를 수정하지 않으며, 새 Connector를 코드 수정 없이 추가해도 자동 Discovery/선택이 가능하다.
- **Phase 5**:
  1. **Workflow Adapter Reversibility** — LangGraph를 제거하고 Sequential Workflow Adapter로
     교체해도 Core와 Organization Layer를 수정하지 않는다(`test_workflow_adapter_reversibility.py`,
     Contract Parity 3건 + Reversibility 1건 + Fail-Closed 3건).
  2. **Stage 8 Agent-Connector 직접 호출** — Agent가 Composition Root를 거치지 않고
     AgentExecutor(Application Service)를 통해 Connector를 직접 호출하는 구조가 Core 수정
     없이 동작함을 실제 Kernel Stage 1~6 경로 + 정적 소스 검사(Kernel/HQ/Lifecycle/Capability
     Registry가 "workflow"를 참조하지 않음)로 증명(`test_stage8_agent_calls_connector.py`).

## 현재 Repository Health (5개 Phase 요약)

| Phase | Architecture | Documentation | Implementation | Tests | Technical Debt | Known Gap | Repository Readiness |
|---|---|---|---|---|---|---|---|
| 1 — Lifecycle | 92 | 88 | 90 | 85 | 78 | 95 | 90 |
| 2 — Capability YAML | 93 | 90 | 91 | 88 | 80 | 92 | 91 |
| 3 — Policy (Casbin) | 94 | 91 | 92 | 90 | 82 | 90 | 93 |
| 4 — Connector (MCP) | 93 | 92 | 90 | 91 | 85 | 91 | 94 |
| 5 — Workflow (LangGraph) | 94 | 93 | 90 | 92 | 87 | 90 | 93 |

세부 근거는 `docs/poc/health-reports/phase-5-workflow-langgraph.md` 참고.
전체 테스트: **47 tests / 143 subtests, 전부 통과** (main 기준 재확인 완료).

**병합 전 최종 검토**: 전체 테스트(47 tests/143 subtests) 재실행 통과, `git diff
origin/main --stat`로 Core 변경 범위가 `workflow/`, `application/agent_executor.py`,
`ports/i_workflow_engine.py`뿐임을 확인, ADR-0007 상태가 Accepted임을 확인.
Feature branch와 `origin/main`이 이미 동일 선형 히스토리(분기 없음)였으므로
fast-forward로 병합(`053c8ba..fbded84`).

## 남아있는 Known Gap

1. **`Agent.required_tools`가 `HQProvisioner`에서 실제로 채워지지 않음** — Phase 2부터
   이월, Phase 4·5에서도 사용자 지시로 명시적으로 미해결. 통합 테스트는 Fixture Agent로
   우회 검증. `main.py`의 실제 데모 실행에서는 Stage 8 경로가 실전 데이터로는 발동하지 않음.
2. **`LangGraphWorkflowEngine`이 `run()`마다 그래프를 재컴파일** — PoC 규모에서는 무해하나
   반복 호출 시 컴파일 오버헤드 누적. 실제 병렬 스케줄링 도입 시 캐싱 여부 재검토 권고.
3. **Workflow Cancellation 미구현** — Domain 개념(`WorkflowStatus.CANCELLED`)만 존재,
   실제 취소 메커니즘은 ADR-0007이 이미 향후로 이연.
4. **병렬 실행의 실제 동시성 미검증** — LangGraph fan-out/fan-in 구조만 구현·검증되었고,
   실제 동시 실행/스레드 안전성/성능은 사용자 지시로 이번 Phase 범위에서 명시적으로 제외.
5. **`workflow-sequential`이 프로덕션 배선에 쓰이지 않음** — Adapter Reversibility 증명
   전용 패키지(`connector-mock`, `policy-inmemory`와 동일한 구조적 특징), entry point 없음.
6. **fetch MCP 레퍼런스 서버 미연결** — Phase 4부터 이월, SDK 버전 비호환.
7. **Connector Lifecycle State 정의만 되고 전이 로직 없음** — ADR-0006 결정 13이 이미 예고.
8. **`main.py`의 함수 인자 개수 문제** — Phase 1부터 이월, Stage 8 재구성으로 한 번 더 누적.
   Context 객체 리팩터링 권고가 Phase 4에 이어 다시 이월됨.
9. **`McpConnector`의 호출마다 프로세스 재기동 설계** — Phase 4부터 이월.
10. **Division/Agent 최소 관례(1:1, tool 없음)** — Phase 2부터 이월, 재설계 안 됨.
11. **`tests/unit/`이 비어 있음** — Phase 1부터 이월, Integration 테스트가 대신함.
12. **Git tag/remote branch delete push 실패** — `phase-5-complete` 태그 및 feature
    branch(`claude/jarvis-os-architecture-analysis-vjrthp`) 삭제가 조직 egress 정책으로
    403 차단됨(Phase 3/4와 동일 현상, 재발). main 병합 자체는 정상 완료(`fbded84`).
    로컬 태그는 존재하나 GitHub에는 아직 반영되지 않음, 원격 feature branch도 아직 남아있음
    (사용자 직접 정리 또는 권한 확인 필요).

## Technical Debt 요약 (Phase 5 신규분)

- `AgentExecutor.execute()`가 `agent.required_tools[0]`(리스트 첫 항목)만 사용 — 한
  Agent가 여러 Capability를 요구하는 시나리오 미지원(Phase 4부터 동일 단순화 유지).
- `LangGraphWorkflowEngine._build_graph()` 재컴파일 (위 Known Gap 2와 동일 항목).

## Jarvis OS Platform v1.0 완료 선언

Phase 1~5를 통해 Jarvis OS Platform Architecture v1.0이 규정한 5개 핵심 축
(Lifecycle, Capability Registry, Policy, Connector, Workflow) 각각에 대해
**Adapter Reversibility**(구현체 교체 시 Core 무수정)와 각 Domain 고유의 두 번째
Validation 목표(HQ 자동 Discovery, Connector 자동 Discovery, Stage 8 Agent-Connector
직접 호출 등)가 실제 코드와 테스트로 증명되었다. ADR-0001~0007이 모두 Accepted 상태이며,
Core(`packages/core`)는 5개 Phase 전체에 걸쳐 각 Adapter의 구체 기술(python-statemachine,
Casbin, MCP, LangGraph)을 알지 못한 채로 유지되었다(각 Phase의 git diff로 반복 검증됨).

이로써 **Jarvis OS Platform v1.0의 핵심 Architecture Validation 단계가 완료**되었다고
판단한다 — 이는 "완제품으로서 출시 준비 완료"를 의미하지 않으며, 사용자가 다음으로
예고한 Repository 전체 관점의 Architecture Review(ADR 일관성, Layer Dependency,
Hexagonal Architecture 준수, Dependency Rule, Composition Root, Package 구조, Core
순수성, Adapter Reversibility 종합, Architecture Drift, Technical Debt, Known Gap,
v1.0 Readiness)를 통해 최종적으로 "v1.0 Ready" 여부가 판정될 예정이다.

## 다음 단계

Phase 6(신규 기능 구현)은 시작하지 않는다. 사용자 지시에 따라 다음으로 **Repository
전체 Architecture Review**를 수행하고, `Architecture Review Report` 문서로 "Jarvis OS
Platform v1.0 Ready" 또는 "Not Ready"를 명확히 판정한다. 이 판정 전까지 Development HQ,
Investment HQ, Personal HQ 등 실제 업무 조직 개발은 착수하지 않는다.
