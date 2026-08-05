# Phase 4 종료 보고서 — Connector Adapter (MCP)

날짜: 2026-08-03
main 기준 commit: `756519c`

## 완료된 Phase

| Phase | 내용 | 상태 |
|---|---|---|
| Phase 1 | Lifecycle Adapter (python-statemachine) | 완료 |
| Phase 2 | Capability YAML Loader | 완료 |
| Phase 3 | Policy Adapter (Casbin) | 완료 |
| Phase 4 | Connector (MCP) | **완료 (이번 보고서 대상)** |
| Phase 5 | Workflow (LangGraph Core) | 대기 — ADR-0007 착수 예정 |

## 완료된 ADR

| ADR | 제목 | 상태 |
|---|---|---|
| ADR-0001 (구 ADR v1) | OSS 선정 및 재검증 원칙 | Accepted |
| ADR-0002 | Capability 스키마/YAML 로딩 격차 기록 | Accepted (기록 목적) |
| ADR-0003 | Domain Port Definition & Adapter Reversibility Principles | Accepted |
| ADR-0004 | Capability Registration Model | Accepted |
| ADR-0005 | Policy Decision Model | Accepted |
| **ADR-0006** | **Connector Execution Model** | **Accepted** |

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
│   └── workflow-langgraph/               (Phase 5 대상, 미구현)
├── apps/
│   └── poc-runner/                       (유일한 Composition Root)
├── docs/
│   ├── adr/                              (ADR-0000~0006)
│   ├── architecture/v1.0/                (Frozen 설계 문서)
│   ├── poc/health-reports/               (Phase별 Repository Health Report)
│   ├── research/, roadmap/
├── hqs/
│   ├── development-hq/, investment-hq/
├── packages/
│   ├── core/                             (Hexagonal Architecture의 Core — Kernel, Policy, Lifecycle,
│   │                                       Capability Registry, Connector/Connector Registry, Organization,
│   │                                       Ports, Application Services)
│   └── shared/
└── tests/
    ├── e2e/          (10 tests — Must #1~11 대응, Must #9 시그니처 갱신)
    ├── integration/  (Phase별 Adapter 검증 — Lifecycle 6, Capability 7, Policy 4, Connector 11)
    └── unit/         (비어 있음 — 알려진 격차, 이월)
```

`packages/core`에 이번 Phase에서 신설된 것은 `connector/`(Domain Model)와
`connector_registry/`(HQ `capability_registry`와 완전히 분리된 별도 모듈) 두 개뿐이며,
`kernel/`, `policy/`, `lifecycle/`, `capability_registry/`는 git diff로 무수정 확인됨.

## 현재 Architecture Validation 완료 항목

- **Phase 1**: Lifecycle Adapter(python-statemachine)를 제거하고 Core 직접 호출로 되돌려도 Core 무수정으로 즉시 복구 가능함.
- **Phase 2**: 새 HQ를 코드 수정 없이 추가/제거해도 자동 Discovery + 자동 Registration + 정상 Routing이 유지됨.
- **Phase 3**: Policy Engine 구현체(Casbin)를 제거하고 다른 구현체(InMemory)로 교체해도 Core와 Kernel을 수정하지 않는다.
- **Phase 4**:
  1. **Connector Adapter Reversibility** — Connector 구현체(MCP)를 제거하고 다른 Connector 구현체(Mock)로
     교체해도 Core와 Agent를 수정하지 않는다(`test_connector_adapter_reversibility.py`). Fail-Closed
     계약(내부 오류/Timeout 시 예외 대신 `ToolResponse`)도 실제 MCP 서버 대상으로 실증.
  2. **Connector 자동 Discovery/선택** — 새 Connector(`connector-http-stub`)를 코드 수정 없이 추가하면
     자동으로 Discovery되고 Capability로 선택 가능하며, 제거해도 기존 Connector는 무수정으로 계속
     동작한다(`test_connector_discovery_zero_code_addition.py`, Phase 2 legal-hq 테스트와 동일 방법론).

## 현재 Repository Health (최근 4개 Phase 요약)

| Phase | Architecture | Documentation | Implementation | Tests | Technical Debt | Known Gap | Repository Readiness |
|---|---|---|---|---|---|---|---|
| 1 — Lifecycle | 92 | 88 | 90 | 85 | 78 | 95 | 90 |
| 2 — Capability YAML | 93 | 90 | 91 | 88 | 80 | 92 | 91 |
| 3 — Policy (Casbin) | 94 | 91 | 92 | 90 | 82 | 90 | 93 |
| 4 — Connector (MCP) | 93 | 92 | 90 | 91 | 85 | 91 | 94 |

세부 근거는 `docs/poc/health-reports/phase-4-connector-mcp.md` 참고. 전체 테스트: **38 tests / 131 subtests, 전부 통과** (main 기준 재확인 완료).

**병합 전 최종 검토**: 전체 테스트(38 tests/131 subtests) 재실행 통과, `git diff origin/main...HEAD --stat -- packages/core`로 Core 변경 범위가 `connector/`, `connector_registry/`, `ports/i_connector.py`, `ports/i_connector_discovery.py`뿐임을 확인, ADR-0006 상태가 Accepted임을 확인. Feature branch와 `origin/main`이 이미 동일 선형 히스토리(분기 없음)였으므로 fast-forward로 병합(`ee4798a..756519c`).

## 남아있는 Known Gap

1. **fetch MCP 레퍼런스 서버 미연결** — `mcp-server-fetch`가 이 환경의 `mcp` SDK 버전과 호환되지 않음(`McpError` import 실패). MCP 구현 세부사항 문제로 Architecture 리스크는 없음(ADR-0006 결정 2). `create_fetch_mock()`으로 대체 유지.
2. **Cancellation/Idempotency/Retry 미구현** — Domain 개념(Enum 값, `idempotency_key` 필드)만 존재. ADR-0006이 이미 Phase 5(비동기 실행) 및 향후로 명시적으로 이연.
3. **Connector Lifecycle State 정의만 되고 전이 로직 없음** — ADR-0006 결정 13이 이미 예고, Health Check/Failover/Auto Recovery의 향후 기반.
4. **`Agent.required_tools`가 `HQProvisioner`에서 실제로 채워지지 않음** — Phase 2부터 이월된 사전 존재 격차. Stage 8의 Connector 호출 루프가 실제 데모 실행에서 발동하지 않아, `main.py`에 별도의 명시적 데모 블록을 추가해 Discovery→Registry→실제 MCP 호출 경로를 증명함. `hq_provisioner.py`/Capability 스키마를 건드리지 않기 위해 Phase 4 범위에서는 의도적으로 미해결.
5. **`main.py`의 함수 인자 개수 문제** — Phase 1부터 이월. Connector 인자가 dict에서 Registry로 바뀌며 시그니처가 한 번 더 복잡해짐. Phase 5(Workflow/LangGraph)에서 Stage 8 재구성과 함께 Context 객체 리팩터링 검토 권고.
6. **`McpConnector`의 호출마다 프로세스 재기동 설계** — PoC 규모에서는 문제없으나, Phase 5에서 비동기 실행 도입 시 세션 재사용(ClientSession 유지) 방향 재검토 권고.
7. **Division/Agent 최소 관례(1:1, tool 없음)** — Phase 2에서 의도적으로 미룬 것, 아직 재설계 안 됨.
8. **`tests/unit/`이 비어 있음** — Phase 1부터 이월된 격차. Integration 테스트가 그 역할을 대신하고 있음.
9. **Git tag push 실패** — `phase-4-connector-mcp` 태그를 로컬에는 생성했으나 원격(origin) push가 조직 egress 정책으로 403 차단됨(Phase 3와 동일 현상, 재발). 로컬 태그는 존재하나 GitHub에는 아직 반영되지 않음(사용자 확인/직접 push 필요).

## 다음 Phase 목표

**Phase 5 — Workflow (LangGraph Core)**. ADR-0007(Workflow Execution Model) 작성 및 승인이 선행 조건이며,
승인 전에는 구현에 착수하지 않는다. 이번 Phase의 최종 Architecture Validation 목표:

> Workflow 구현체(LangGraph)를 제거하고 다른 Workflow Engine으로 교체해도 Core와 Organization Layer를 수정하지 않는다.
