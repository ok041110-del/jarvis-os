# Jarvis OS Platform — Release Notes v1.0.0

날짜: 2026-08-03
main 기준 commit: `6d957e5`

> **이번 Release는 Platform Release이며, Application Release가 아니다.**
> Development HQ, Investment HQ, Personal HQ, Research HQ 등 실제 업무 조직의
> 비즈니스 로직은 이 Release에 포함되지 않는다. v1.0이 Release/Freeze하는 것은
> **Hexagonal Architecture 기반의 Platform 구조 그 자체**다.

---

## v1.0 목표

Jarvis OS Platform이 다음 하나의 질문에 코드와 테스트로 답하는 것이 v1.0의 유일한
목표였다:

> "Kernel, HQ, Policy, Lifecycle, Connector, Workflow 각각의 실제 구현체(Adapter)를
> 제거하고 다른 구현체로 교체해도, Core는 수정되지 않는가?"

기능의 완성도나 실제 업무 처리 능력은 v1.0의 목표가 아니었다 — Architecture가 주장하는
Adapter Reversibility가 우연이 아니라 구조적으로 보장되는지를 증명하는 것이 목표였다.

## 완료된 Architecture Validation

| Domain | Adapter(실사용) | 대조 Adapter | 검증 결과 |
|---|---|---|---|
| Lifecycle | lifecycle-statemachine | (Core 직접 호출) | 제거 후 즉시 복구 가능 |
| Capability Registry | capability-provider-yaml | — | 새 HQ 코드 수정 없이 추가/제거 가능 |
| Policy | policy-casbin | policy-inmemory | 교체해도 Core/Kernel 무수정 |
| Connector | connector-mcp | connector-mock | 교체 가능 + 새 Connector 무코드 자동 Discovery |
| Workflow | workflow-langgraph | workflow-sequential | 교체해도 Core/Organization Layer 무수정 + Stage 8 Agent-Connector 직접 호출 실증 |

5개 Domain 전부 동일한 방법론(Port 정의 → 최소 2개 Adapter → Reversibility 테스트)으로
검증되었으며, 이는 Jarvis OS의 핵심 Identity Claim이 반복 가능한 구조임을 뜻한다.

## 완료된 Phase

| Phase | 내용 |
|---|---|
| Phase 1 | Lifecycle Adapter (python-statemachine) |
| Phase 2 | Capability YAML Loader |
| Phase 3 | Policy Adapter (Casbin) |
| Phase 4 | Connector Adapter (MCP) |
| Phase 5 | Workflow Adapter (LangGraph) |

각 Phase 종료 보고서는 `docs/poc/phase-*-closing-report.md`에 있다.

## 완료된 ADR

| ADR | 제목 | 상태 |
|---|---|---|
| 0001 | OSS 선정 및 재검증 원칙 | Accepted |
| 0002 | Capability 스키마/YAML 로딩 격차 기록 | Accepted(기록 목적) |
| 0003 | Domain Port Definition & Adapter Reversibility Principles | Accepted |
| 0004 | Capability Registration Model | Accepted |
| 0005 | Policy Decision Model | Accepted |
| 0006 | Connector Execution Model | Accepted |
| 0007 | Workflow Execution Model | Accepted |

## Repository 구조

```
jarvis-os/
├── packages/core, packages/shared     Core Layer (외부 프레임워크 의존성 0)
├── adapters/*                          Adapter Layer (10개 패키지)
├── hqs/development-hq, hqs/investment-hq  HQ Layer (Capability 선언 + 최소 골격)
├── apps/poc-runner                     유일한 Composition Root
└── tests/e2e, tests/integration         47 tests / 143 subtests
```

전체 구조와 각 디렉터리의 역할은 `README.md`의 Repository Structure 섹션을 참고.

## Platform 범위 (이번 Release에 포함된 것)

- Kernel (Intent Recognition → Task Classification → Task Router → HQ Selection)
- Capability Registry (HQ Discovery/Registration)
- Policy Engine (PDP/PEP, Permission Tier)
- Lifecycle (HQ 상태 전이, Team/Agent Ephemeral 생명주기)
- Connector Execution Model (Discovery, Fail-Closed, MCP 실사용 Adapter)
- Workflow Execution Model (LangGraph 기반 Team~Agent 실행 조립)
- Composition Root (`apps/poc-runner`) — 5개 Domain 전부를 조립하는 유일한 지점
- Hexagonal Architecture 원칙(Port/Adapter 분리, Dependency Rule)의 Repository 전체 준수

## 제외된 범위 (이번 Release에 포함되지 않은 것)

- **실제 업무 조직(Application Layer) 비즈니스 로직** — Development HQ/Investment HQ의
  실제 Division 구성, Agent 전문화, Tool 세트는 아직 설계·구현되지 않았다.
- **Agent.required_tools 실채움** — HQProvisioner가 아직 이를 채우지 않으며, Stage 8의
  Agent-Connector 직접 호출은 Fixture Agent로만 검증되었다(§Known Gap 참고).
- **Event Bus 실제 구현** — Port 정의만 존재, 기술 미선정.
- **병렬 실행의 실제 동시성/성능** — LangGraph fan-out/fan-in 구조만 검증, 실제 스케줄링은 없음.
- **Workflow Cancellation 실제 메커니즘** — Domain 개념(`WorkflowStatus.CANCELLED`)만 존재.
- **인증/사용자 신원 모델, 멀티테넌시, Memory Layer, Client(Layer 0)** — Architecture v1.0
  설계 범위 밖으로 이미 명시됨(`docs/architecture/v1.0/` §6).

## Known Gap

1. `Agent.required_tools`가 HQProvisioner에서 실제로 채워지지 않음 (최우선 — v1.1 착수 전 해소 권고)
2. Workflow Cancellation 미구현 (Domain 개념만 존재)
3. 병렬 실행의 실제 동시성 미검증 (구조만 검증됨)
4. Connector Lifecycle State 정의만 되고 전이 로직 없음
5. fetch MCP 레퍼런스 서버 미연결 (SDK 버전 비호환)
6. Event Bus 기술 미선정 + 최소 구현 미착수
7. `tests/unit/` 부재 (integration이 대신 수행 중)
8. Git tag/remote branch 정리 push가 조직 egress 정책으로 403 차단 (반복 재발, 인프라 권한 문제)
9. Division/Agent 최소 관례(1:1, tool 없음)
10. `capability-store-sqlite` 미사용 스켈레톤

전체 근거는 `docs/architecture-review/architecture-review-v1.md` §12, `docs/reports/platform-v1-final-report.md` 참고.

## Technical Debt

- `AgentExecutor.execute()`가 `agent.required_tools[0]`(리스트 첫 항목)만 사용
- `LangGraphWorkflowEngine`이 `run()`마다 그래프를 재컴파일
- `main.py`(Composition Root)의 함수 인자 개수가 Phase가 진행될수록 누적 증가
- `McpConnector`가 호출마다 프로세스를 재기동

## v1.1 방향

`docs/architecture/ARCHITECTURE_FREEZE_v1.0.md`가 규정하는 조건(ADR 승인 또는
Architecture Review 또는 Breaking Change 승인) 하에서만 Architecture 자체를 바꿀 수
있다. v1.1로 예정된 것은 Architecture 재설계가 아니라:

1. `Agent.required_tools` 실채움 메커니즘 (HQProvisioner 확장 또는 Capability 스키마 확장)
2. Event Bus 기술 선정 및 최소 구현
3. 병렬 실행/Workflow Cancellation의 실제 구현 여부 결정
4. `main.py` Context 객체 리팩터링
5. `capability-store-sqlite` 거취 결정 (유지 시 ADR 근거 기록, 아니면 삭제)

이 항목들이 Architecture Layer의 확장인 반면, **실제 Development HQ/Investment HQ 등
업무 조직의 비즈니스 로직 개발은 v1.1과 별개로, Platform이 Frozen된 지금부터 바로
Application Layer 작업으로 시작할 수 있다** — 단, 위 1번(`Agent.required_tools`)이
실제 Agent-Connector 호출 경로를 살아 있게 만드는 선행 조건임을 유의해야 한다.
