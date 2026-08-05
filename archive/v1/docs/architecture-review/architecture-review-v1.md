# Jarvis OS Platform — Architecture Review Report (v1.0 Readiness)

날짜: 2026-08-03
검토 대상: main 기준 commit `a309c40` (Phase 1~5 완료, ADR-0001~0007)
검토자: Claude (요청에 따른 Repository 전체 관점 Architecture Review)

이 문서는 새 기능을 계획하는 문서가 아니다. Phase 1~5에서 실제로 만들어진 코드,
ADR, 테스트, git 이력을 근거로 15개 항목을 평가하고, 최종적으로 "Jarvis OS
Platform v1.0 Ready" 또는 "Not Ready"를 판정한다.

---

## 1. ADR 전체 일관성

| ADR | 제목 | 상태 | 다른 ADR과의 충돌 |
|---|---|---|---|
| 0001 | OSS 선정 및 재검증 원칙 | Accepted | 없음 — 이후 ADR들이 선정 결과(LangGraph/Casbin/MCP/python-statemachine)를 그대로 계승 |
| 0002 | Capability 스키마/YAML 로딩 격차 기록 | Accepted(기록 목적) | ADR-0004가 이 격차를 실제로 해소(Capability Registration Model) |
| 0003 | Domain Port Definition & Adapter Reversibility | Accepted | 이후 모든 ADR(0004~0007)이 이 원칙(Port 정의 후 구현, Adapter Reversibility 테스트)을 그대로 따름 |
| 0004 | Capability Registration Model | Accepted | ADR-0006이 "Connector Registry는 이 Registry와 별도"라고 명시적으로 대비, 충돌 없음 |
| 0005 | Policy Decision Model | Accepted | ADR-0006/0007이 Policy 판단을 각자 명시적으로 "포함하지 않는다"고 선언 — 책임 경계 일관 |
| 0006 | Connector Execution Model | Accepted | ADR-0007이 AgentExecutor를 통해 이 ADR의 실행 경로(ToolRequest/ToolResponse)를 그대로 재사용 |
| 0007 | Workflow Execution Model | Accepted | Workflow Registry를 의도적으로 두지 않아 ADR-0004/0006의 "Plugin=Registry" 패턴과 다른데, 근거(Decision 12)가 명시되어 있어 불일치가 아니라 의도된 분기 |

**결론**: 7개 ADR 모두 Accepted, 상호 모순 없음. ADR-0007의 "Workflow는 Plugin이
아니다"라는 결정은 ADR-0004/0006과 표면적으로 다른 패턴을 취하지만, Rationale에서
그 이유(Domain 본질의 차이 — 다중 구현체 동시 존재 여부)를 명시했으므로 이는
**의도적 분기(Architecture Drift 아님)** 로 판단한다.

---

## 2. Layer Dependency 검증

`pyproject.toml` 의존성 그래프를 전수 확인한 결과:

```
jarvis-shared  (외부 의존성 없음)
      ↑
jarvis-core  (jarvis-shared에만 의존, 외부 프레임워크 의존성 없음)
      ↑                              ↑
hqs/*-hq              adapters/*  (jarvis-core + 각자의 구체 기술에만 의존)
      ↑                              ↑
             apps/poc-runner  (jarvis-core + hqs/* + adapters/* 전체를 조립)
```

- `packages/core/pyproject.toml`의 `dependencies`는 `jarvis-shared` 단 하나 — casbin, mcp,
  langgraph, python-statemachine, pyyaml 등 어떤 외부 패키지도 Core에 선언되지 않음.
- `grep -rn "^import \|^from "` 결과 Core 소스 어디에도 프레임워크 import가 없음(직접 확인).
- 10개 adapter 패키지 전부 `jarvis-core`(+자기 자신의 기술 의존성)에만 의존 — adapter가
  다른 adapter를 참조하는 사례 없음(`grep -rln "from jarvis_adapter"` 결과 0건).
- `apps/poc-runner`만 모든 adapter를 동시에 의존성으로 선언 — Composition Root 역할이 실제
  패키지 구조로도 강제되어 있음(다른 어떤 패키지도 두 개 이상의 adapter를 동시에 의존하지 않음).

**결론**: Layer Dependency 위반 없음. 의존 방향이 항상 `adapters/apps → core → shared`
한 방향으로만 흐른다.

---

## 3. Hexagonal Architecture 준수 여부

- Port(추상 인터페이스)는 전부 `packages/core/src/jarvis_core/ports/`에 위치:
  `i_lifecycle_runtime.py`, `i_capability_provider.py`, `i_capability_store.py`,
  `i_policy_engine.py`, `i_connector.py`, `i_connector_discovery.py`, `i_workflow_engine.py`.
- 각 Port마다 최소 1개의 실사용 Adapter + 최소 1개의 Reversibility 증명용 Adapter 쌍이 존재:
  - Lifecycle: `lifecycle-statemachine`(실사용) — Reversibility 대조군 없음(Phase 1은 "Core
    직접 호출로 되돌리기"로 증명, 별도 Adapter 불필요).
  - Capability Provider: `capability-provider-yaml`(실사용), `capability-store-sqlite`(미사용
    스켈레톤, ADR 근거 없이 방치됨 — §11 Technical Debt에서 다룸).
  - Policy: `policy-casbin`(실사용) / `policy-inmemory`(Reversibility 전용).
  - Connector: `connector-mcp`(실사용) / `connector-mock`(Reversibility 전용).
  - Workflow: `workflow-langgraph`(실사용) / `workflow-sequential`(Reversibility 전용).
- Application Service(`hq_provisioner.py`, `agent_executor.py`)가 Core 안에 있지만 Domain
  Logic이 아니라 절차 조립만 담당 — Port를 소비하는 위치이지 Port를 우회하는 위치가 아님.

**결론**: Hexagonal Architecture(Port/Adapter 분리, Composition Root 단일화)가 5개 Phase에
걸쳐 일관되게 적용됨.

---

## 4. Dependency Rule 위반 여부

Dependency Rule(안쪽 Layer가 바깥쪽을 몰라야 한다)을 Core 내부 모듈 단위로도 확인했다.

- `kernel/hq_selection.py`가 `capability_registry`, `organization`, `lifecycle`, `policy`를
  import — 이는 위반이 아니라 Kernel이 여러 Domain을 **오케스트레이션**하는 설계상 역할이며,
  Reference Architecture v1에서 이미 규정된 책임(모두 Core 내부, 바깥 Layer 의존 아님).
- `organization/entities.py`가 `lifecycle.hq_state`를 import — `Team`/`HQ`가 자신의 상태
  전이 규칙을 lifecycle 모듈에 위임하는 것으로, 이 역시 Core 내부 Domain 간 참조.
- Core의 어떤 모듈도 `ports/` 밖의 구체 구현체(예: `jarvis_adapter_*`)를 import하지 않음
  (전수 grep 결과 0건).
- `apps/poc-runner/main.py`만 Port 타입과 구체 Adapter 생성자를 동시에 import — Composition
  Root의 정의상 정상.

**결론**: Dependency Rule 위반 사례 없음. Core 내부의 모듈 간 참조는 모두 "같은 원 안에서의
Domain 간 협력"이지 "안쪽이 바깥쪽에 의존"하는 위반이 아니다.

---

## 5. Composition Root 검토

`apps/poc-runner`가 유일한 Composition Root라는 원칙이 5개 Phase 내내 유지됨:

- `build_world()`가 Capability Provisioning, Connector Discovery, Workflow Engine 구성을
  전부 여기서 수행하고, 이 함수 밖에서는 어떤 코드도 구체 Adapter를 직접 생성하지 않는다
  (테스트 코드 제외 — 테스트는 Adapter Reversibility를 증명하기 위해 의도적으로 직접 구성).
- `main.py` docstring에 Phase 1~5 각각의 "무엇이 바뀌었고 무엇이 안 바뀌었는지"가 순서대로
  기록되어 있어, Composition Root 자체가 Architecture 변경 이력의 살아있는 문서 역할을 함.
- 다만 `handle_request()`/`run_organization_layer()`의 인자 개수가 Phase가 진행될수록
  누적 증가함(현재 6~7개) — 이는 §11 Technical Debt에서 다룬다.

**결론**: Composition Root 원칙 자체는 위반 없이 유지됨. 다만 함수 인자 누적은 리팩터링
후보로 이미 4개 Phase 연속 이월된 상태.

---

## 6. Repository Structure 검토

```
jarvis-os/
├── adapters/        10개 패키지, Port 1개당 실사용 1~2개 + Reversibility용 1개 원칙 준수
├── apps/poc-runner/  유일한 Composition Root
├── docs/             adr/, architecture/v1.0/(Frozen), poc/health-reports/, research/, roadmap/
├── hqs/               development-hq, investment-hq — Capability 선언 + Division/Agent 정의
├── packages/          core(Hexagonal Core), shared(횡단 유틸리티)
└── tests/             e2e/, integration/, unit/(비어 있음)
```

- 최상위 구조가 Vision/Architecture 문서의 Layer 구분과 그대로 대응됨(HQ Layer=`hqs/`,
  Core=`packages/core`, Adapter=`adapters/`, Composition Root=`apps/`).
- `docs/architecture/v1.0/`이 "Frozen"으로 명명되어 있고 실제로 이번 Review 기간 동안
  수정된 적이 없음(git log 확인) — 문서 관리 원칙이 지켜짐.

**결론**: Repository Structure는 Architecture 문서와 1:1로 대응되며 구조적 문제 없음.

---

## 7. Package 구조 검토

- 모든 패키지가 `pyproject.toml` + `src/<package_name>/` 레이아웃(PEP 621 + src-layout)으로
  통일됨 — 10개 adapter + 2개 hq + 1개 app + 2개 core/shared, 예외 없음.
- 패키지 명명 규칙이 일관됨: `jarvis-adapter-<domain>-<impl>`, `jarvis-hq-<name>`,
  `jarvis-core`, `jarvis-shared`, `jarvis-poc-runner`.
- entry point 그룹(`jarvis.hq_capability_source`, `jarvis.connector`)이 명확히 구분되어
  있고, Workflow는 의도적으로 entry point 그룹이 없음(ADR-0007 결정 12와 일치).
- `capability-store-sqlite`는 entry point도 없고 어디에도 의존성으로 선언되지 않은 완전한
  미사용 스켈레톤 — 패키지는 존재하지만 실체가 없는 유일한 사례(§11에서 처리 권고).

**결론**: Package 구조는 일관되고 명명 규칙도 잘 지켜짐. 유일한 흠은 `capability-store-sqlite`의
존재 목적이 코드베이스만 봐서는 불분명하다는 점.

---

## 8. Core의 순수성 검토

- `packages/core/src/jarvis_core` 전체에 대해 외부 프레임워크 import를 grep한 결과 **0건**.
- `pyproject.toml`의 `dependencies`가 `jarvis-shared` 단 하나뿐이라는 선언과 실제 코드가
  일치함(선언과 실제가 어긋나는 사례 없음).
- 유일한 예외적 관찰: `packages/core/src/jarvis_core/events/event_bus_port.py`가 "PoC에서는
  최소 구현(in-memory pub/sub)으로 Task Flow/Event Flow 분리만 시연한다"는 docstring을
  갖고 있지만, 실제로는 어떤 in-memory 구현도 없고 이 모듈을 import하는 코드가 전무함
  (`grep -rln "event_bus\|EventBus"` 결과 이 파일 자체 외 0건). Core 순수성 자체는 침해되지
  않았으나(빈 Port), **문서가 약속한 것을 코드가 이행하지 않은 유일한 사례**다.

**결론**: Core는 프레임워크 의존성이 전혀 없는 순수 상태를 5개 Phase 내내 유지했다. Event
Bus Port의 docstring-구현 불일치는 §10 Architecture Drift 항목에서 정식으로 다룬다.

---

## 9. Adapter Reversibility 종합 검토

| Domain | 실사용 Adapter | Reversibility 대조군 | 증명 테스트 |
|---|---|---|---|
| Lifecycle | lifecycle-statemachine | (Core 직접 호출로 복귀) | Phase 1 — `test_lifecycle_statemachine.py` |
| Capability Provider | capability-provider-yaml | — | Phase 2 — `test_hq_zero_code_addition.py` |
| Policy | policy-casbin | policy-inmemory | Phase 3 — `test_policy_adapter_reversibility.py` |
| Connector | connector-mcp | connector-mock | Phase 4 — `test_connector_adapter_reversibility.py`, `test_connector_discovery_zero_code_addition.py` |
| Workflow | workflow-langgraph | workflow-sequential | Phase 5 — `test_workflow_adapter_reversibility.py` |

5개 Domain 전부 "구현체를 제거하고 다른 구현체로 교체해도 Core를 수정하지 않는다"는 동일한
형태의 Architecture Validation을 코드와 테스트로 실증했다. 방법론도 일관됨 — 직접 구성
(direct construction)으로 교체하고, Contract(반환 타입/상태)가 동일함을 확인.

**결론**: Adapter Reversibility는 이번 Repository의 핵심 Architecture Claim이며, 5개
Domain 전부에서 반복 검증되어 우연이 아니라 구조적으로 보장된 성질임을 확인했다.

---

## 10. Architecture Drift 존재 여부

Architecture Drift(설계 문서와 실제 구현이 시간이 지나며 벌어지는 현상)를 다음 기준으로
점검했다: (a) ADR의 결정과 실제 코드 불일치, (b) 문서가 약속했지만 구현되지 않은 것, (c)
Phase가 진행되며 이전 원칙이 조용히 깨진 사례.

- **(a) ADR-코드 불일치**: 발견되지 않음. ADR-0003~0007의 모든 Port 시그니처, Registry
  분리 원칙, Fail-Closed 계약이 실제 코드와 대응됨(각 Phase 종료 보고서의 git diff 검증
  기록으로 이미 확인됨).
- **(b) 문서상 약속·미구현**: **Event Bus Port** 하나 발견(§8 참고). Reference Architecture
  v1 §4가 Event Bus의 책임을 정의했고 ADR-0007 Decision 8이 이를 재확인했지만, 실제
  in-memory 구현체는 어느 Phase에서도 작성되지 않았다. 이는 Architecture 자체의 결함이
  아니라 "PoC에서는 최소 구현으로 시연한다"는 문구가 실제 이행되지 않은 **문서 정확성
  문제**로 분류한다 — Task Flow(Kernel→Organization→Workflow)만으로 지금까지의 모든 PoC
  시나리오가 검증 가능했기 때문에 실제로 필요하지 않았을 뿐이다.
- **(c) 원칙의 조용한 훼손**: 발견되지 않음. 오히려 각 Phase가 시작될 때마다 사용자가
  "최소 변경 원칙"을 반복 요구했고, 실제로 Kernel/HQ/Division 코드는 5개 Phase에 걸쳐
  git diff로 무수정이 반복 확인됐다.

**결론**: 유의미한 Architecture Drift는 없다. 유일하게 짚어야 할 것은 Event Bus Port의
문서-구현 간극이며, 이는 "설계가 잘못 흘러간 것"이 아니라 "아직 쓰이지 않은 약속"이다 —
v1.1에서 실제로 Event Bus 기술을 선정하기 전까지는 docstring을 "구현 예정, 현재 정의만
존재"로 정정하는 것을 권고한다.

---

## 11. Technical Debt 정리

Phase별 Health Report에 흩어져 있던 Technical Debt를 domain별로 통합했다.

| 항목 | 최초 발생 Phase | 현재 상태 |
|---|---|---|
| `main.py`의 함수 인자 개수 누적(`handle_request`, `run_organization_layer`) | Phase 1 | Phase 5까지 5회 연속 이월, 인자 6~7개로 증가. Context 객체로 묶는 리팩터링 권고. |
| `Agent.required_tools`가 `HQProvisioner`에서 채워지지 않음 | Phase 2 | Phase 4/5에서도 사용자 지시로 의도적 이월. **실제 업무 조직(Development/Investment HQ) 개발 이전에는 반드시 해소 필요**(§15). |
| `capability-store-sqlite`가 미사용 스켈레톤으로 방치 | Phase 2 이전(스캐폴딩 시점) | 어떤 ADR도 이 패키지의 존속 이유를 설명하지 않음. 삭제 또는 ADR로 존재 이유 기록 권고. |
| `McpConnector`가 호출마다 프로세스 재기동 | Phase 4 | 비동기/반복 실행 도입 시 세션 재사용 재검토 필요. |
| `LangGraphWorkflowEngine`이 `run()`마다 그래프 재컴파일 | Phase 5 | 실제 병렬 스케줄링 도입 전에 캐싱 여부 결정 필요. |
| Event Bus Port 문서-구현 불일치 | Phase 0(스캐폴딩) | §10 참고, 문서 정정 또는 최소 구현 필요. |
| `tests/unit/`이 비어 있음 | Phase 1 | Integration 테스트가 대신하고 있으나, Core만 겨냥한 순수 단위 테스트 부재는 Adapter 없이 Core 로직만 빠르게 검증하는 능력의 공백. |

**결론**: 신규로 발견된 위험한 부채는 없다. 대부분 각 Phase에서 이미 스스로 인지하고
기록한 항목이며, 은폐된 부채는 발견되지 않았다.

---

## 12. Known Gap 정리 (Phase 1~5 통합)

1. `Agent.required_tools` 미채움 — **가장 우선순위 높은 Gap**(§15에서 v1.1 필수 항목으로 재확인).
2. Workflow Cancellation 실제 미구현(Domain 개념만 존재).
3. 병렬 실행의 실제 동시성/성능 미검증(구조만 검증됨, ADR-0007이 이미 범위 제한).
4. Connector Lifecycle State 정의만 되고 전이 로직 없음(ADR-0006 결정 13 예고).
5. fetch MCP 레퍼런스 서버 미연결(SDK 버전 비호환, Mock으로 대체).
6. Event Bus 기술 미선정 + 최소 구현 미착수(§10).
7. `tests/unit/` 부재.
8. Git tag/remote branch 정리 push가 조직 egress 정책으로 403 차단(Phase 3~5 반복 재발,
   로컬에는 존재하나 GitHub 미반영 — 인프라 권한 문제이지 Architecture 문제 아님).
9. Division/Agent 최소 관례(1:1, tool 없음)가 실제 조직 다양성을 아직 반영하지 않음.
10. `capability-store-sqlite` 미사용 스켈레톤(§11).

이 중 **1번만이 실제 업무 조직 개발(Development HQ 등)의 진짜 착수 조건**이고, 나머지는
전부 "다음 Phase/버전에서 다뤄도 되는" 성격이다.

---

## 13. Architecture Validation 결과 종합

Phase 1~5가 각각 증명한 것을 한 문장씩으로 정리한다.

1. **Lifecycle**: Adapter(python-statemachine)를 제거해도 Core 무수정으로 즉시 복구 가능.
2. **Capability Registry**: 새 HQ를 코드 수정 없이 추가/제거해도 자동 Discovery + Routing 유지.
3. **Policy**: Adapter(Casbin)를 제거하고 다른 구현체로 교체해도 Core/Kernel 무수정.
4. **Connector**: Adapter(MCP)를 제거해도 Core/Agent 무수정 + 새 Connector 무코드 추가 Discovery.
5. **Workflow**: Adapter(LangGraph)를 제거해도 Core/Organization Layer 무수정 + Stage 8에서
   Agent가 Connector를 직접 호출하는 구조가 Core 수정 없이 동작.

다섯 개의 검증이 전부 동일한 형태("구현체 교체 시 Core 무수정")를 취하고, 전부 실제
테스트(총 47 tests/143 subtests)로 뒷받침된다. 이는 Jarvis OS Platform의 핵심 Identity
Claim("Adapter는 언제든 교체 가능하고, Core는 구체 기술을 모른다")이 우연이 아니라
반복 가능한 방법론(Port 정의 → 최소 2개 Adapter → Reversibility 테스트)으로 실현되고
있음을 뜻한다.

---

## 14. Jarvis OS Platform v1.0 Readiness 평가

**평가 기준**: v1.0의 목표는 "완제품 출시"가 아니라 "Hexagonal Architecture 기반의 5개
핵심 축(Lifecycle/Capability/Policy/Connector/Workflow)에서 Adapter Reversibility가
구조적으로 보장됨을 증명하는 것"이었다(각 Phase Implementation Plan에서 반복 확인된 목표).

- ADR 일관성: 충족 (§1)
- Layer Dependency: 위반 없음 (§2)
- Hexagonal Architecture 준수: 충족 (§3)
- Dependency Rule: 위반 없음 (§4)
- Composition Root 단일화: 유지됨 (§5)
- Repository/Package 구조: 일관됨 (§6, §7)
- Core 순수성: 유지됨(Event Bus 문서 불일치 제외, §8)
- Adapter Reversibility: 5개 Domain 전부 실증 (§9)
- Architecture Drift: 유의미한 것 없음 (§10)
- Technical Debt/Known Gap: 전부 문서화됨, 은폐된 것 없음 (§11, §12)

**판정: Jarvis OS Platform v1.0 Ready**

이 판정은 "Architecture 검증 단계"에 한정된다. Development HQ/Investment HQ/Personal HQ
등 실제 업무 조직의 **비즈니스 로직 개발**에 대한 준비 상태를 의미하지 않는다 — 그 판단은
§15의 조건이 충족된 이후에 별도로 내려야 한다.

---

## 15. v1.1 이전 반드시 해결해야 하는 항목

Architecture 자체의 결함이 아니라, **실제 업무 조직 개발을 시작하는 순간 즉시 문제가
드러나는 선행 조건**들이다.

1. **`Agent.required_tools` 실채움 메커니즘** (최우선) — `HQProvisioner` 확장 또는
   Capability YAML 스키마 확장 중 택일. 이것이 해소되지 않으면 Development HQ의 실제
   Agent가 Stage 8에서 Connector를 호출하는 경로 자체가 데모 블록으로만 우회되는 현재
   상태(§12-1)가 실제 조직에서도 반복된다 — Phase 5가 증명한 "Agent가 Connector를 직접
   호출한다"는 구조가 실제 데이터로는 아직 한 번도 발동한 적이 없다는 뜻이기 때문이다.
2. **Division/Agent 최소 관례(1:1) 재검토** — 실제 업무 조직은 Division당 여러 Agent,
   Agent당 여러 required_tools를 가질 가능성이 높다. `AgentExecutor.execute()`가 현재
   `required_tools[0]`만 쓰는 단순화(§11)도 이와 함께 재검토해야 한다.
3. **Event Bus 기술 선정 및 최소 구현, 또는 최소한 docstring 정정** — 실제 조직 간
   비동기 알림/감사가 필요해지는 시점에 Domain 설계 없이 시작하지 않도록.
4. **`main.py` Context 객체 리팩터링** — 실제 조직이 늘어나면 Composition Root의 배선
   로직도 함께 복잡해질 것이므로, 함수 인자 누적 문제를 먼저 해소하는 것이 유지보수 측면에서
   유리하다(Architecture 위반은 아니나 v1.1 착수 전 정리 권고).
5. **`capability-store-sqlite`의 거취 결정** — 유지한다면 ADR로 존재 이유를 남기고,
   불필요하다면 삭제한다.

이 5개 항목 중 1번만이 **"실제 업무 조직 개발을 막는 진짜 조건"** 이고, 나머지 4개는
"먼저 하면 더 편해지는" 권고 사항이다.

---

## 최종 판정

> **Jarvis OS Platform v1.0 Ready** — Architecture Validation 단계 기준으로.
>
> Development HQ/Investment HQ/Personal HQ 등 실제 업무 조직 개발에 착수하기
> 위해서는, 그전에 §15-1 (`Agent.required_tools` 실채움) 을 최소한 하나의 별도
> Phase/ADR로 해소할 것을 권고한다. 그 외 항목은 병행하거나 이후로 미뤄도
> Architecture 자체의 무결성에는 영향이 없다.
