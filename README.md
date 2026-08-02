# Jarvis OS

> AI Organization Operating System

## Claude Code를 위한 컨텍스트 파일 (읽는 순서)
1. **`Instructions.md`** — 개발 프로세스, Architecture Rules, Coding Rules
2. **`Vision.md`** — 프로젝트 목적과 철학
3. **`PROJECT_CONTEXT.md`** — 현재 상태, PoC 범위, Phase 진행 순서, Definition of Done

세 파일은 이 저장소의 코드(`packages/`, `adapters/`, `hqs/`, `apps/`)와 같은 루트에 있어야
Claude Code가 설계 의도와 실제 코드를 함께 참조할 수 있습니다.

---

## 프로젝트 소개

Jarvis OS는 하나의 AI Agent를 만드는 프로젝트가 아닙니다. 여러 전문 AI 조직(HQ)을
하나의 운영체제처럼 관리하고 협업시키는 **AI Organization Operating System**입니다.

사람이 회사의 대표에게 업무를 지시하면 각 부서가 협업해 결과를 만드는 것처럼, Jarvis OS는
사용자의 요청을 적절한 조직(HQ)에 전달하고 필요하면 여러 조직을 협업시켜 하나의 결과를
만들어냅니다.

## Vision

- **Mission**: AI Assistant가 아니라 AI Organization을 만든다.
- **Goal**: 하나의 AI가 모든 일을 하는 게 아니라, 여러 전문 조직(Development HQ, Investment
  HQ, Personal HQ, Finance HQ, Research HQ 등)이 협업하는 구조를 만든다.
- **Philosophy**: Build Thin, Replace Easily / Organization First / Architecture before
  Feature / Validate before Optimize / No Silent Failure

자세한 내용은 [`Vision.md`](./Vision.md) 참고.

## Architecture

Architecture v1.0은 **동결(Frozen)** 상태입니다. 원본 문서는 [`docs/architecture/v1.0/`](./docs/architecture/v1.0/)에 있습니다.

핵심 계층 구조:

```
User → Kernel → HQ → Division → Team → Agent → MCP/External Services
```

- **Kernel**: Intent Recognition → Task Classification(Capability Registry 조회) →
  Task Router → HQ Selection. Division 이하의 결정에는 관여하지 않는다.
- **Capability Registry**: Kernel이 HQ 이름이 아니라 능력(Capability)으로 HQ를 찾는
  구조. 새 HQ 추가는 Capability 등록만으로 이루어지며 Kernel 코드는 바뀌지 않는다.
- **Policy Engine**: PDP/PEP 모델. 파이프라인의 한 단계가 아니라 모든 계층이 결정
  순간마다 호출하는 공유 서비스. Permission/Security(Tier 1) → Budget/Wake-up/
  Isolation(Tier 2) → Priority/Retry(Tier 3) → Audit(상시 기록 채널).
- **Lifecycle**: HQ는 Provisioning/Running/Idle/Sleeping/Disabled/Updating/Error/
  Decommissioned 상태를 가진다. Sleeping(자동 wake 가능)과 Disabled(사람만 wake 가능)를
  엄격히 구분한다. Team/Agent는 Task 단위로 생성-소멸하는 Ephemeral 존재다.
- **No Silent Failure**: 모든 실패는 명시적인 이유(reason)를 가져야 한다.

전체 설계 근거와 대안 비교는 `docs/architecture/v1.0/`의 5개 문서를 참고하세요
(Reference Architecture → Core Design Principles → Request Processing Kernel →
Policy Engine → Capability Registry 순으로 읽으면 설계가 쌓인 순서와 같습니다).

## Repository Structure

```
jarvis-os/
├── Instructions.md          # Claude Code 개발 프로세스/규칙
├── Vision.md                # 프로젝트 철학
├── PROJECT_CONTEXT.md        # 현재 상태, Phase 순서, DoD
├── README.md                 # 이 문서
├── pyproject.toml            # uv workspace root (virtual — 자체 의존성 없음)
│
├── packages/                 # ── Core Layer ── 외부 프레임워크 의존성 0
│   ├── core/                 #    Kernel, Capability Registry, Policy 모델,
│   │                         #    Lifecycle, Organization 엔티티, Port(Interface)
│   └── shared/                #    프레임워크 독립적인 순수 유틸
│
├── adapters/                 # ── Adapter Layer ── Core의 Port를 구현, 외부 라이브러리 의존
│   ├── policy-inmemory/       #    (Walking Skeleton, 현재 실제 사용 중)
│   ├── connector-mock/        #    (Walking Skeleton, 현재 실제 사용 중)
│   ├── lifecycle-statemachine/#    Phase 1 target (python-statemachine)
│   ├── policy-casbin/         #    Phase 2 target (Casbin)
│   ├── connector-mcp/         #    Phase 3 target (MCP)
│   ├── workflow-langgraph/    #    Phase 4 target (LangGraph Core)
│   └── capability-store-sqlite/
│
├── hqs/                       # ── HQ Layer ── Core에만 의존, Adapter는 모름
│   ├── development-hq/
│   └── investment-hq/
│
├── apps/                      # ── Composition Root ── 유일하게 모든 걸 아는 곳
│   └── poc-runner/
│
├── tests/
│   ├── unit/          # Core만, Fake Port로 테스트
│   ├── integration/   # 개별 Adapter 테스트
│   └── e2e/           # PoC Must 11개 항목과 1:1 대응 (현재 10개 통과)
│
├── scripts/
│   ├── run_walking_skeleton.sh   # 네트워크 없이도 즉시 실행 가능
│   └── run_tests.sh
│
└── docs/
    ├── architecture/v1.0/   # 동결된 Architecture 원본 5개 문서
    ├── adr/                  # Architecture Decision Record
    ├── poc/                   # Backlog, Walking Skeleton 상태
    ├── roadmap/               # 모든 문서의 "다음 단계"를 모은 ROADMAP.md
    └── research/              # 향후 오픈소스 후보 원본 조사 기록용
```

## 개발 원칙

1. **Build Thin, Replace Easily** (Ports & Adapters / Hexagonal Architecture) — Core는
   어떤 외부 오픈소스도 직접 import하지 않는다. 모든 외부 의존성은 `packages/core/*/ports/`의
   Interface를 `adapters/`가 구현하는 형태로만 연결된다.
2. **Dependency Rule** — 항상 `Adapter → Interface(Port) → Core` 방향으로만 의존한다.
   `apps/poc-runner`(Composition Root)만 모든 구현체를 안다.
3. **Walking Skeleton** — 기능보다 Architecture Validation을 우선한다. 가장 단순한
   기술로 전체 배선을 먼저 검증하고, 이후 실제 오픈소스로 하나씩 교체한다.
4. **Vertical Slice** — 컴포넌트를 개별로 완성하지 않고, 하나의 요청이 User부터 Result까지
   전 계층을 관통하는 것을 우선한다.
5. **No Silent Failure** — 모든 실패는 명시적인 이유를 가져야 한다.
6. **Integrate First** — 검증된 오픈소스를 우선 채택하고, 직접 구현은 마지막 선택이다.
   기술 선정은 GitHub 원본 데이터(Star, License, 유지보수 상태)로 검증한 뒤 ADR로 기록한다.
7. **Re-evaluation Principle** — 기각된 후보는 영구 기각이 아니다. Architecture 변경,
   PoC 실패, 성능 문제, 라이선스 변경, 프로젝트 성숙도 변화 시 재평가한다.

## 구현 순서 (Architecture 검증 강도 순)

Walking Skeleton은 이미 완료되어 있습니다(In-Memory/Mock adapter로 전 계층 배선 검증,
PoC Must 11개 항목 대응 테스트 10개 통과). 다음은 실제 오픈소스 Adapter로 하나씩
교체하는 단계입니다 — 구현 난이도가 아니라 **Architecture를 가장 많이 검증하는 순서**로
정했습니다.

| Phase | 교체 대상 | 검증 목표 |
|---|---|---|
| 1 | Lifecycle → python-statemachine | HQ 공통 기반인 Lifecycle이 실제 라이브러리에서도 설계와 동일하게 유지되는가 |
| 2 | Policy → Casbin | Policy Engine(PDP/PEP), Permission Tier, Interface 분리가 실제 코드에서도 유지되는가 |
| 3 | Connector → MCP | Connector Interface, Adapter 구조, External Integration이 깨지지 않는가 |
| 4 | Workflow → LangGraph Core | Core가 LangGraph를 직접 의존하지 않는다는 원칙이 끝까지 유지되는가 |

각 Phase는 Definition of Done(`PROJECT_CONTEXT.md` 참고) 5개 항목을 모두 만족해야
완료로 간주합니다. 완료 여부와 무관하게 발견한 구조적 사실은 ADR로 남깁니다.

## Claude Code 시작 방법

```bash
# 1. 저장소 클론 후 컨텍스트 파일부터 읽기
cat Instructions.md Vision.md PROJECT_CONTEXT.md

# 2. Walking Skeleton이 지금도 동작하는지 먼저 확인 (네트워크 불필요)
./scripts/run_walking_skeleton.sh
./scripts/run_tests.sh

# 3. 네트워크가 있는 환경이라면 워크스페이스 동기화
uv sync

# 4. PROJECT_CONTEXT.md의 "Phase 실행 로그"를 확인하고 Phase 1부터 진행
#    (Instructions.md의 Development Process 9단계를 반드시 따를 것 — 승인 전 코드 수정 금지)
```

Architecture와 충돌하는 상황을 만나면 구현을 멈추고 먼저 보고합니다. Core 변경이
필요하다고 판단되면 ADR 초안을 먼저 작성하고 사용자 승인 후에만 진행합니다.
