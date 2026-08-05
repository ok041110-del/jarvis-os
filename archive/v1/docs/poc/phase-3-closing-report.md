# Phase 3 종료 보고서 — Policy Adapter (Casbin)

날짜: 2026-08-03
main 기준 commit: `b236a43`

## 완료된 Phase

| Phase | 내용 | 상태 |
|---|---|---|
| Phase 1 | Lifecycle Adapter (python-statemachine) | 완료 |
| Phase 2 | Capability YAML Loader | 완료 |
| Phase 3 | Policy Adapter (Casbin) | **완료 (이번 보고서 대상)** |
| Phase 4 | Connector (MCP) | 대기 — ADR-0006 착수 예정 |
| Phase 5 | Workflow (LangGraph Core) | 대기 |

## 완료된 ADR

| ADR | 제목 | 상태 |
|---|---|---|
| ADR-0001 (구 ADR v1) | OSS 선정 및 재검증 원칙 | Accepted |
| ADR-0002 | Capability 스키마/YAML 로딩 격차 기록 | Accepted (기록 목적) |
| ADR-0003 | Domain Port Definition & Adapter Reversibility Principles | Accepted |
| ADR-0004 | Capability Registration Model | Accepted |
| **ADR-0005** | **Policy Decision Model** | **Accepted** |

## 현재 Repository 구조

```
jarvis-os/
├── adapters/
│   ├── capability-provider-yaml/   (Phase 2, 실사용)
│   ├── capability-store-sqlite/    (미사용 스켈레톤)
│   ├── connector-mcp/              (Phase 4 대상, 미구현)
│   ├── connector-mock/             (실사용, 임시)
│   ├── lifecycle-statemachine/     (Phase 1, 실사용)
│   ├── policy-casbin/              (Phase 3, 실사용 — 이번 Phase에서 구현 완료)
│   ├── policy-inmemory/            (실사용 아님 — Adapter Reversibility 증명용으로 보존)
│   └── workflow-langgraph/         (Phase 5 대상, 미구현)
├── apps/
│   └── poc-runner/                 (유일한 Composition Root)
├── docs/
│   ├── adr/                        (ADR-0000~0005)
│   ├── architecture/v1.0/          (Frozen 설계 문서)
│   ├── poc/health-reports/         (Phase별 Repository Health Report)
│   ├── research/, roadmap/
├── hqs/
│   ├── development-hq/, investment-hq/
├── packages/
│   ├── core/                       (Hexagonal Architecture의 Core — Kernel, Policy, Lifecycle,
│   │                                 Capability Registry, Organization, Ports, Application Services)
│   └── shared/
└── tests/
    ├── e2e/          (10 tests — Must #1~11 대응)
    ├── integration/  (Phase별 Adapter 검증 — Lifecycle 6, Capability 7, Policy 4)
    └── unit/         (비어 있음 — 알려진 격차, 이월)
```

## 현재 Architecture Validation 완료 항목

- **Phase 1**: Lifecycle Adapter(python-statemachine)를 제거하고 Core 직접 호출로 되돌려도 Core 무수정으로 즉시 복구 가능함(`test_lifecycle_statemachine.py::TestAdapterReversibility`).
- **Phase 2**: 새 HQ를 코드 수정 없이 추가/제거해도 자동 Discovery + 자동 Registration + 정상 Routing이 유지됨(`test_hq_zero_code_addition.py`, 실제로 `hqs/legal-hq`를 추가/제거하며 실증).
- **Phase 3**: **Policy Engine 구현체(Casbin)를 제거하고 다른 구현체(InMemory)로 교체해도 Core와 Kernel을 수정하지 않는다** — `test_policy_adapter_reversibility.py::TestAdapterReversibility`, `TestCasbinInMemoryParity`로 실증. 추가로 Fail-Closed 계약(내부 오류 시 예외 대신 Deny 반환)을 `TestFailClosedContract`로 검증.

## 현재 Repository Health (최근 3개 Phase 요약)

| Phase | Architecture | Documentation | Implementation | Tests | Technical Debt | Known Gap | Repository Readiness |
|---|---|---|---|---|---|---|---|
| 1 — Lifecycle | 92 | 88 | 90 | 85 | 78 | 95 | 90 |
| 2 — Capability YAML | 93 | 90 | 91 | 88 | 80 | 92 | 91 |
| 3 — Policy (Casbin) | 94 | 91 | 92 | 90 | 82 | 90 | 93 |

세부 근거는 `docs/poc/health-reports/phase-3-policy-casbin.md` 참고. 전체 테스트: **28 tests / 131 subtests, 전부 통과** (main 기준 재확인 완료).

**병합 전 발견 및 해소한 이슈**: Feature branch가 이전 세션에서 `origin/main`과 분기되어 있었다(동일 내용의 Phase 2 커밋이 서로 다른 해시로 양쪽에 존재). `git diff`로 두 트리가 완전히 동일함을 확인한 뒤, Phase 3 커밋만 `origin/main` 위로 rebase하여 히스토리를 선형으로 정리했다(코드 손실 없음). `main`은 현재 `origin/main`과 fast-forward로 병합되어 있고, feature branch도 동일 커밋(`b236a43`)을 가리키도록 정리했다.

## 남아있는 Known Gap

1. **`PolicyRequest`에 tier 구분 필드 없음** (ADR-0005 결정 5) — Tier 2/3(Budget/Wake-up/Priority 등) 정책이 추가되는 시점에 스키마 확장 필요. 지금은 Permission Policy 하나뿐이라 문제 없음.
2. **Permission 레벨 매핑 중복** — Casbin(`_ROLE_BY_LEVEL`)과 InMemory(`_LEVELS`) 양쪽에 "standard/restricted" 레벨 이름이 각각 정의됨. 세 번째 레벨이 생기기 전까지는 허용 가능한 수준.
3. **`main.py`의 함수 인자 개수 문제** — Phase 1부터 이월된 권고(Context 객체 리팩터링 미적용). Phase 4에서 `connectors`에 이어 실제 MCP 관련 인자가 추가되기 전에 검토 필요.
4. **Division/Agent 최소 관례(1:1, tool 없음)** — Phase 2에서 의도적으로 미룬 것, 아직 재설계 안 됨.
5. **`tests/unit/`이 비어 있음** — Phase 1부터 이월된 격차. Integration 테스트가 그 역할을 대신하고 있음.
6. **Git tag push 실패** — `phase-3-policy-casbin` 태그를 로컬에는 생성했으나 원격(origin) push가 조직 egress 정책으로 403 차단됨. 로컬 태그는 존재하나 GitHub에는 아직 반영되지 않음(사용자 확인/직접 push 필요).

## 다음 Phase 목표

**Phase 4 — Connector (MCP)**. ADR-0006(Connector Execution Model) 작성 및 승인이 선행 조건이며, 승인 전에는 구현에 착수하지 않는다. 이번 Phase의 최종 Architecture Validation 목표:

> Connector 구현체(MCP)를 제거하고 다른 Connector 구현체로 교체해도 Core와 Agent를 수정하지 않는다.
