# PROJECT CONTEXT

## Current Status
Architecture v1.0
Status: Frozen
Current Phase: Implementation Phase — Walking Skeleton (Repository Handoff 준비 완료)

## Completed
- Vision
- Organization Layer
- Kernel
- Capability Registry
- Policy Engine (PDP/PEP)
- Lifecycle
- Communication Model
- Repository Architecture (Monorepo, Ports & Adapters)
- PoC Backlog
- Walking Skeleton (In-Memory adapter로 전체 배선 검증 완료 — Must 11개 항목 대응 테스트 10개 통과)
- ADR Process (Re-evaluation Principle 포함, 구현 중 발견한 구조적 사실 기록 포함 — ADR-0002)
- Repository 최종 정리 (GitHub 업로드 준비 완료)

## Current Goal
Architecture Validation. 기능 구현이 아니라 Architecture가 실제 구현에서도 유지되는지 검증한다.

## PoC Scope

### Validate
- Kernel
- Capability Registry
- Policy Engine
- Development HQ
- Investment HQ
- HQ Routing
- Lifecycle
- MCP Connector

### Not Included
- Voice
- Learning
- Memory Optimization
- Token Optimization
- Trading Performance
- Code Generation Quality

## Technology Decisions (ADR로 확정됨 — docs/adr/ 참고)

| 영역 | Walking Skeleton (현재 실제 wiring) | Phase Target | Future |
|---|---|---|---|
| Lifecycle | python-statemachine (Phase 1 완료) | — | — |
| Policy | Casbin (`adapters/policy-casbin`, Phase 3 완료, ADR-0005) | — | OPA (ADR-0001의 ADR-003) |
| Connector | `adapters/connector-mock` (임시, 외부 의존성 없음) | **Phase 4**: MCP 공식 filesystem/fetch 서버 | — |
| Workflow | `apps/poc-runner`의 순차 함수 호출 | **Phase 5**: LangGraph Core (langgraph-api는 사용하지 않음) | — |
| Capability Registry | Core 직접 구현 | 동일 (오픈소스 없음, 의도적 결정) | 동일 |

## Current Development Order (Architecture 검증 강도 순)

```
Phase 1  Lifecycle   → python-statemachine
Phase 2  Capability  → YAML Loader
Phase 3  Policy      → Casbin
Phase 4  Connector   → MCP
Phase 5  Workflow    → LangGraph Core
```

**⚠️ Phase 착수 전 필수 확인**: 개발 환경에 네트워크가 없으면 어떤 Phase도 시작할 수 없습니다
(각 Phase의 대상 라이브러리를 `uv sync`로 설치해야 함). Phase 진행 전 이 문서의
"Phase 실행 로그" 섹션에 pip/uv 접근 가능 여부를 먼저 기록하세요.

## Definition of Done (Phase 공통)
1. Core를 수정하지 않았는가?
2. Interface(Port)를 변경하지 않았는가?
3. Adapter만 교체하여 동일한 테스트(tests/e2e)가 통과하는가?
4. Architecture v1.0의 책임 분리가 그대로 유지되는가?
5. 새로운 구조적 문제가 발견되었다면 ADR로 기록했는가?

5가지 모두 "예"일 때만 해당 Phase를 완료로 간주한다.

## Phase 실행 로그
(각 Phase 시작 시 Claude Code가 이 섹션에 추가)

- [x] Phase 1 — Lifecycle (python-statemachine): **완료**. `uv sync` 네트워크 접근 가능 확인됨.
  `packages/core/src/jarvis_core/ports/i_lifecycle_runtime.py`에 `LifecycleRuntime` Domain
  Interface 최초 정의(ADR-0003), `adapters/lifecycle-statemachine`가 이를 구현. Guard 판정은
  전부 `jarvis_core.lifecycle.hq_state`에 위임(재구현 없음). `apps/poc-runner/main.py`에서
  Composition Root 레벨로만 wiring. 기존 e2e 테스트(10개) 전부 무수정 통과 + 신규 integration
  테스트(`tests/integration/test_lifecycle_statemachine.py`, 8-state 전이표 전수 검증 포함)
  전부 통과. Core(`packages/core`) 외 파일 수정 없음.
- [x] Phase 2 — Capability YAML Loader (ADR-0002 해소, ADR-0004 Accepted): **완료**.
  `packages/core/src/jarvis_core/ports/i_capability_provider.py`에 `ICapabilityProvider`
  Domain Interface 신규 정의. `packages/core/src/jarvis_core/application/hq_provisioner.py`에
  `HQProvisioner` Application Service 신규 정의 — Composition Root는 이를 조립만 하고
  Provisioning 절차 자체는 이 서비스가 담당(사용자 요청 반영). `adapters/capability-provider-yaml`이
  Python Entry Point(`jarvis.hq_capability_source`)로 `hqs/*`를 자동 발견해 `capabilities.yaml`을
  파싱. `apps/poc-runner/main.py`의 `build_world()`가 HQ 이름을 하드코딩하지 않는 제네릭
  루프로 교체됨. 실제로 `hqs/legal-hq`를 저장소에 추가/제거하며 `uv sync`를 실행하는 통합
  테스트로 "Core/Kernel/Registry/main.py 무수정 + 자동 Discovery(3개 HQ 동시) + 자동
  Routing + HQ 제거 후 정상 동작"을 실증(Phase 2 Architecture Validation 목표 달성).
  기존 e2e(10개) + Phase 1 integration(6개) 전부 무수정 통과. Kernel/Capability Registry/
  Lifecycle/Organization 파일 수정 없음(git diff로 확인).
- [x] Phase 3 — Policy (Casbin, ADR-0005 Accepted): **완료**. `adapters/policy-casbin`의
  빈 스켈레톤을 실제 구현(`CasbinPolicyEngine`)으로 채움 — Casbin RBAC 모델(`model.conf`,
  이 Adapter 안에서만 존재하는 문법)로 Permission Tier(Tier 1)를 평가. `packages/core`는
  `ports/i_policy_engine.py`의 docstring에 Fail-Closed 계약(ADR-0005 결정 4)만 추가했고
  (Port 계약 명시는 ADR-0003 결정 1과 동일하게 "예정된 확장"으로 취급, 로직/스키마 변경
  없음), `kernel/hq_selection.py`와 `policy/models.py`는 무수정. `apps/poc-runner/main.py`는
  import 한 줄(`InMemoryPolicyEngine` → `CasbinPolicyEngine`)만 교체. `policy-inmemory`
  Adapter는 삭제하지 않고 Adapter Reversibility 증명용으로 계속 보존.
  신규 `tests/integration/test_policy_adapter_reversibility.py`(4 tests)로 (1) Casbin과
  InMemory가 `hq_selection.py`를 통해 항상 동일한 결정을 낸다는 Parity, (2) Casbin을
  제거하고 InMemory로 되돌려도 Core 무수정으로 즉시 동일하게 동작한다는 Adapter
  Reversibility, (3) 내부 오류가 나도 예외를 던지지 않고 Deny로 귀결된다는 Fail-Closed
  계약을 증명. 기존 e2e(10개) + Phase 1/2 integration 전부 무수정 통과(총 28 tests /
  131 subtests). `apps/poc-runner`의 실제 실행(`python -m jarvis_poc_runner.main`)으로
  4개 시나리오(Wake-up+ALLOW, Disabled 거부, 재활성화+ALLOW, Permission DENY) 전부
  Casbin 경유로 기존과 동일한 결과 확인.
- [ ] Phase 4 — Connector (MCP): 대기 중
- [ ] Phase 5 — Workflow (LangGraph Core): 대기 중

## 알려진 격차 (Known Gaps — ADR-0002)
- `hqs/*/capabilities.yaml`이 런타임에 실제로 로드되지 않고, `apps/poc-runner/main.py`에
  동일한 값이 하드코딩되어 있다. Phase 2("Capability YAML Loader")에서 해소 예정.
  자세한 내용은 docs/adr/0002-capability-schema-and-yaml-loading-gap.md와 docs/roadmap/ROADMAP.md 참고.

## Repository Principle
Monorepo. `packages/` (core, shared) / `adapters/` / `hqs/` / `apps/` / `tests/` / `docs/`.
Composition Root는 `apps/poc-runner` 하나만 존재한다.

## ADR Rule
Architecture 변경은 반드시 ADR 승인 이후에만 가능하다.
구현 중 발견한 구조적 문제는 ADR로 기록한다 (설계 문서가 아니라 발견한 사실의 기록).
Core를 임의 변경하지 않는다.
Re-evaluation Principle(docs/adr/0001-...)에 따라 기각된 후보도 조건 충족 시 재평가 가능하다.

## 다음 계획
Phase별 상세 계획과 v1.1 후보 목록은 docs/roadmap/ROADMAP.md 참고.
