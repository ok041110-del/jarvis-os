Platform: **v1.0 Ready** · Architecture: **Frozen** · Version: **1.0.0**

# Jarvis OS

> AI Organization Operating System — Platform Layer (Architecture Frozen, v1.0.0)

## Claude Code를 위한 컨텍스트 파일 (읽는 순서)
1. **`Instructions.md`** — 개발 프로세스, Architecture Rules, Coding Rules
2. **`Vision.md`** — 프로젝트 목적과 철학
3. **`PROJECT_CONTEXT.md`** — Phase 실행 로그, 현재 상태
4. **`docs/architecture/ARCHITECTURE_FREEZE_v1.0.md`** — 무엇을 바꿀 수 있고 무엇을
   바꿀 수 없는지 (Application Layer 개발 시작 전 필독)

세 핵심 파일(Instructions/Vision/PROJECT_CONTEXT)은 이 저장소의 코드(`packages/`,
`adapters/`, `hqs/`, `apps/`)와 같은 루트에 있어야 Claude Code가 설계 의도와 실제
코드를 함께 참조할 수 있습니다.

---

## Vision

Jarvis OS는 하나의 AI Agent를 만드는 프로젝트가 아니다. 여러 전문 AI 조직(HQ)을 하나의
운영체제처럼 관리하고 협업시키는 **AI Organization Operating System**이다.

사람이 회사의 대표에게 업무를 지시하면 각 부서가 협업해 결과를 만드는 것처럼, Jarvis OS는
사용자의 요청을 적절한 조직(HQ)에 전달하고 필요하면 여러 조직을 협업시켜 하나의 결과를
만들어낸다.

- **Mission**: AI Assistant가 아니라 AI Organization을 만든다.
- **Goal**: 하나의 AI가 모든 일을 하는 게 아니라, 여러 전문 조직(Development HQ, Investment
  HQ, Personal HQ, Finance HQ, Research HQ 등)이 협업하는 구조를 만든다.

자세한 내용은 [`Vision.md`](./Vision.md) 참고.

## Core Principles

1. **Build Thin, Replace Easily** (Ports & Adapters / Hexagonal Architecture) — Core는
   어떤 외부 오픈소스도 직접 import하지 않는다.
2. **Dependency Rule** — 항상 `Adapter → Port(Interface) → Core` 방향으로만 의존한다.
   `apps/poc-runner`(Composition Root)만 모든 구현체를 안다.
3. **Organization First** — 기능보다 조직 구조(HQ → Division → Team → Agent)가 먼저다.
4. **Architecture before Feature** — 구현보다 Architecture Validation을 우선한다.
5. **Validate before Optimize** — 성능보다 구조가 옳은지 먼저 증명한다.
6. **No Silent Failure** — 모든 실패는 명시적인 이유(reason)를 가져야 한다.
7. **Adapter Reversibility** — 어떤 Adapter든 제거하고 다른 구현체로 교체해도 Core는
   수정되지 않아야 한다 (Phase 1~5에서 5개 Domain 전부 실증됨).
8. **Re-evaluation Principle** — 기각된 후보는 영구 기각이 아니다. Architecture 변경,
   PoC 실패, 라이선스 변경 시 재평가한다.

## Architecture

Architecture v1.0은 **Frozen** 상태다. 원본 설계 문서는 [`docs/architecture/v1.0/`](./docs/architecture/v1.0/)에,
Freeze 범위와 조건은 [`docs/architecture/ARCHITECTURE_FREEZE_v1.0.md`](./docs/architecture/ARCHITECTURE_FREEZE_v1.0.md)에 있다.

핵심 계층 구조:

```
User → Kernel → HQ → Division → Team → Agent → Connector(Tool) → External Services
                              └─ Workflow Engine이 Team~Agent 실행을 조립
```

- **Kernel**: Intent Recognition → Task Classification(Capability Registry 조회) →
  Task Router → HQ Selection. Division 이하의 결정에는 관여하지 않는다.
- **Capability Registry**: Kernel이 HQ 이름이 아니라 능력(Capability)으로 HQ를 찾는
  구조. 새 HQ 추가는 Capability 등록만으로 이루어지며 Kernel 코드는 바뀌지 않는다.
- **Policy Engine**: PDP/PEP 모델. Permission(Tier 1) → Budget/Wake-up/Isolation(Tier 2)
  → Priority/Retry(Tier 3) → Audit(상시 기록).
- **Lifecycle**: HQ는 Provisioning/Running/Idle/Sleeping/Disabled/Updating/Error/
  Decommissioned 상태를 가진다. Team/Agent는 Task 단위로 생성-소멸하는 Ephemeral 존재다.
- **Connector**: Agent가 외부 도구(MCP 등)를 호출하는 창구. HQ Capability Registry와
  완전히 분리된 별도의 Discovery/Registry를 가진다(Connector도 Plugin이다).
- **Workflow Engine**: Team 활성화부터 Agent 실행, Team 종료까지의 실행 순서를 조립한다.
  HQ/Connector와 달리 Plugin이 아니다 — Composition Root가 직접 하나만 선택해 주입한다.
- **No Silent Failure**: 모든 실패는 명시적인 이유를 가져야 한다.

전체 설계 근거는 `docs/architecture/v1.0/`(Reference Architecture → Core Design
Principles → Request Processing Kernel → Policy Engine → Capability Registry 순),
그리고 각 Phase의 결정 사항은 `docs/adr/0001`~`0007`을 참고.

## Repository Structure

```
jarvis-os/
├── VERSION                      # 1.0.0
├── RELEASE_NOTES_v1.0.md        # Platform Release 노트 (Application Release 아님)
├── CHANGELOG.md
├── Instructions.md              # Claude Code 개발 프로세스/규칙
├── Vision.md                    # 프로젝트 철학
├── PROJECT_CONTEXT.md           # Phase 실행 로그, 현재 상태
├── README.md                    # 이 문서
├── pyproject.toml                # uv workspace root (virtual)
│
├── packages/                     # ── Core Layer ── 외부 프레임워크 의존성 0
│   ├── core/                     #    Kernel, Capability Registry, Connector/Connector
│   │                             #    Registry, Policy, Lifecycle, Workflow Domain Model,
│   │                             #    Organization, Application Services, Ports
│   └── shared/                    #    프레임워크 독립적인 순수 유틸
│
├── adapters/                      # ── Adapter Layer ── Core의 Port를 구현
│   ├── lifecycle-statemachine/    #    실사용 (python-statemachine)
│   ├── capability-provider-yaml/  #    실사용 (YAML 기반 Capability 선언)
│   ├── capability-store-sqlite/   #    미사용 스켈레톤 (v1.1 정리 후보)
│   ├── policy-casbin/             #    실사용
│   ├── policy-inmemory/           #    Adapter Reversibility 증명 전용
│   ├── connector-mcp/             #    실사용 (MCP filesystem 서버)
│   ├── connector-mock/            #    Adapter Reversibility 증명 전용
│   ├── connector-discovery-entrypoint/ # entry point 기반 Connector 자동 Discovery
│   ├── workflow-langgraph/        #    실사용 (LangGraph StateGraph)
│   └── workflow-sequential/       #    Adapter Reversibility 증명 전용
│
├── hqs/                            # ── HQ Layer ── Core에만 의존, Adapter는 모름
│   ├── development-hq/
│   └── investment-hq/
│
├── apps/
│   └── poc-runner/                 # ── 유일한 Composition Root ──
│
├── tests/
│   ├── unit/           # 비어 있음 — Known Gap (integration이 대신 수행 중)
│   ├── integration/    # Phase별 Adapter/Architecture Validation (9개 파일)
│   └── e2e/            # PoC Must 11개 항목 대응 (10 tests)
│
├── scripts/
│   ├── run_walking_skeleton.sh
│   └── run_tests.sh
│
└── docs/
    ├── architecture/v1.0/            # Frozen 설계 원본 5개 문서
    ├── architecture/ARCHITECTURE_FREEZE_v1.0.md
    ├── architecture-review/          # Repository 전체 Architecture Review
    ├── adr/                          # ADR-0001~0007, 전부 Accepted
    ├── poc/health-reports/           # Phase별 Repository Health Report
    ├── poc/phase-*-closing-report.md # Phase별 종료 보고서
    ├── reports/platform-v1-final-report.md
    ├── roadmap/ROADMAP.md
    └── research/
```

## Architecture Validation

5개 Phase에 걸쳐 Jarvis OS의 핵심 Architecture Claim — **"Adapter는 언제든 교체
가능하고, Core는 구체 기술을 모른다"** — 를 코드와 테스트로 반복 실증했다.

| Phase | Domain | 검증 결과 |
|---|---|---|
| 1 | Lifecycle | python-statemachine Adapter 제거 후 Core 직접 호출로 즉시 복구 가능 |
| 2 | Capability Registry | 새 HQ를 코드 수정 없이 추가/제거해도 자동 Discovery + Routing 유지 |
| 3 | Policy | Casbin Adapter 제거 후 다른 구현체로 교체해도 Core/Kernel 무수정 |
| 4 | Connector | MCP Adapter 제거 후 교체 가능 + 새 Connector 무코드 추가 자동 Discovery |
| 5 | Workflow | LangGraph Adapter 제거 후 Sequential로 교체해도 Core/Organization Layer 무수정 + Stage 8에서 Agent가 Connector를 직접 호출하는 구조가 Core 수정 없이 동작 |

전체 테스트: **47 tests / 143 subtests, 전부 통과**. 상세 근거는
[`docs/architecture-review/architecture-review-v1.md`](./docs/architecture-review/architecture-review-v1.md)와
[`docs/reports/platform-v1-final-report.md`](./docs/reports/platform-v1-final-report.md) 참고.

## Current Status

> **Jarvis OS Platform v1.0 Ready**
> **Architecture Frozen**
> **Application Development Not Started**

Platform(Kernel/HQ/Policy/Lifecycle/Connector/Workflow의 Hexagonal Architecture)은
Architecture Review를 통과해 v1.0으로 Release 및 Freeze되었다. Development HQ,
Investment HQ, Personal HQ, Research HQ 등 실제 업무 조직(Application Layer)의
비즈니스 로직 개발은 **아직 시작되지 않았다** — 지금 존재하는 `hqs/development-hq`,
`hqs/investment-hq`는 Capability 선언과 최소 Division/Agent 골격만 가진 PoC 조직이다.

Architecture 변경이 필요하면 언제든 `ADR 작성 → Architecture Review → 승인` 절차를
거쳐야 한다(자세한 조건은 `docs/architecture/ARCHITECTURE_FREEZE_v1.0.md` 참고).

## Roadmap

v1.1 이전에 반드시 다뤄야 할 항목과 장기 로드맵은 [`docs/roadmap/ROADMAP.md`](./docs/roadmap/ROADMAP.md)에
정리되어 있다. 가장 우선순위가 높은 것은 **`Agent.required_tools` 실채움 메커니즘**이다
— 이것이 해소되지 않으면 실제 HQ의 Agent가 Connector를 호출하는 경로가 실전 데이터로는
발동하지 않는다.

## Repository Map

| 무엇을 찾고 있는가 | 어디를 보면 되는가 |
|---|---|
| Architecture 설계 근거 | `docs/architecture/v1.0/` |
| 각 Phase의 결정 사항 | `docs/adr/0001`~`0007` |
| Freeze 범위/조건 | `docs/architecture/ARCHITECTURE_FREEZE_v1.0.md` |
| Repository 전체 평가 | `docs/architecture-review/architecture-review-v1.md` |
| Phase별 상세 진행 | `PROJECT_CONTEXT.md`의 "Phase 실행 로그" |
| 남은 작업/이월 항목 | `docs/roadmap/ROADMAP.md` |
| v1.0 최종 결과 | `docs/reports/platform-v1-final-report.md` |
| 실행 가능한 코드 | `packages/core`, `adapters/*`, `hqs/*`, `apps/poc-runner` |

## Getting Started

```bash
# 1. 저장소 클론 후 컨텍스트 파일부터 읽기
cat Instructions.md Vision.md PROJECT_CONTEXT.md docs/architecture/ARCHITECTURE_FREEZE_v1.0.md

# 2. 워크스페이스 동기화
uv sync

# 3. 전체 배선이 지금도 동작하는지 확인
./scripts/run_walking_skeleton.sh
./scripts/run_tests.sh
# 또는: uv run pytest -q

# 4. Application Layer(Development HQ 등) 개발을 시작하기 전에
#    docs/architecture/ARCHITECTURE_FREEZE_v1.0.md의 "변경 가능한 영역"을 먼저 확인할 것
```

Architecture와 충돌하는 상황을 만나면 구현을 멈추고 먼저 보고한다. Core 변경이
필요하다고 판단되면 ADR 초안을 먼저 작성하고 사용자 승인 후에만 진행한다.
