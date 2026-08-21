# Jarvis OS Structure v1.0 — Frozen

**문서 성격**: 사용자가 첨부한 `Jarvis OS_Structure_v1.0__frozen.pdf`의 전문(全文) 전사(transcription)다. 이 PDF는 `RFC-0006`(`docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md`) → `ADC-0005`/`ADC-0006` → `ADR-0006`(`docs/decisions/adr/ADR-0006-structure-v1-migration.md`) → `ADR-0007`(`docs/decisions/adr/ADR-0007-baseline-relocation.md`) 절차를 거쳐 이미 승인·실행된 Target Architecture 문서이며, `roadmap.md`가 명시하는 Source of Truth 중 하나다. 이 파일은 그 승인된 내용을 저장소 안에서 직접 인용·참조할 수 있도록 옮겨 적은 것일 뿐 — **새 Architecture 결정을 추가하지 않는다.** 원본 PDF와 내용이 다르면 원본 PDF가 우선한다.

---

## Status

**Structure v1.0 — Frozen**

### Freeze 판단

현재 구조는 **Architecture Target Structure로 Freeze 가능**하다.

Freeze의 대상은 Repository의 논리적 경계와 책임 분리이며, 모든 디렉터리를 즉시 구현하거나 생성한다는 의미는 아니다.

현재까지의 논의에서 핵심 Boundary가 일관되게 정리되었다.

- `hqs/development/`를 Development HQ의 정식 위치로 사용
- 기존 `development-hq/`는 장기 구조에서 제거하고 Migration 대상으로 취급
- Development HQ의 Workflow는 `workflows/software-development/` 아래에서 관리
- 기존 01~06은 Workflow를 구성하는 Stage로 유지
- `projects/`는 Development HQ가 주관하는 Project 영역으로 유지
- Development HQ가 `scripts/`, `tests/`, `config/`를 관리
- Root `scripts/`, `tests/`, `config/`는 별도로 두지 않음
- Jarvis OS Runtime과 Kernel은 `core/`에서 담당
- Dashboard는 외부 관리 Interface로 분리
- 외부 서비스 연결은 `integrations/`에서 담당
- 공식 Architecture·Decision·Specification·Validation·Research는 `docs/`에서 관리
- 과거 Frozen/Deprecated Artifact는 `archive/`에서 보존

---

## Structure v1.0

```
jarvis-os/
│
├── .claude/                    # Claude Code를 이용해 Repository를 개발·운영하기 위한 환경
├── .github/                    # GitHub 기반 CI/CD와 Repository Governance를 관리
├── .gitignore                  # Git에 포함하지 않을 파일과 Secret을 지정
├── .env.example                # 필요한 환경변수의 이름과 형식을 보여주는 예시
│
├── README.md                   # Jarvis OS의 목적·구조·사용 방법을 설명하는 프로젝트 진입점
├── CLAUDE.md                   # Claude Code가 Repository에서 작업할 때 따라야 하는 규칙
├── AGENTS.md                   # 전체 AI Agent가 공통적으로 따라야 하는 규칙
├── LICENSE                     # Jarvis OS의 사용·수정·배포 조건을 정의
│
├── core/                       # Jarvis OS의 핵심 실행 영역인 Kernel
│   ├── registry/                # Agent·Workflow·Capability·Tool 등의 구성요소를 등록·조회
│   ├── runtime/                 # 시스템과 Agent의 실행 환경과 Lifecycle을 관리
│   ├── scheduler/                # 예약·반복·Trigger 기반 실행을 관리
│   ├── policy/                  # Permission·Policy·Guardrail 등 실행 제약을 관리
│   ├── communication/            # Kernel 내부와 외부 구성요소 사이의 통신을 관리
│   ├── execution/                # Capability를 실제로 실행하는 Execution Layer
│   ├── events/                   # Event와 Event Bus를 통해 상태 변화를 전달
│   ├── context/                  # Agent와 Workflow에 필요한 Context를 구성·전달
│   ├── memory/                   # Memory의 저장·검색·Lifecycle을 관리
│   └── observability/            # Log·Metric·Trace·Audit을 통해 실행 상태를 관찰
│
├── hqs/                         # Jarvis OS에서 여러 업무 영역을 HQ 단위로 운영
│   ├── development/              # Development HQ — Jarvis OS 전체의 개발·검증·개선을 담당
│   │   ├── README.md              # Development HQ의 목적과 운영 구조를 설명
│   │   ├── workflows/             # Development HQ가 사용하는 개발 Workflow
│   │   │   └── software-development/  # 표준 Software Development Workflow
│   │   │       ├── 01_repository_intelligence/
│   │   │       ├── 02_planning_specification/
│   │   │       ├── 03_architecture_design/
│   │   │       ├── 04_implementation/
│   │   │       ├── 05_validation/
│   │   │       └── 06_devops_release/
│   │   ├── agents/                # Development HQ 전용 Agent
│   │   ├── runtime/                # Development HQ의 실행 환경과 상태
│   │   ├── scripts/                # Development HQ가 사용하는 개발·검증·운영 자동화 Script
│   │   ├── tests/                  # Development HQ가 관리하는 Jarvis OS 전체 테스트
│   │   ├── config/                 # Development HQ가 관리하는 Jarvis OS 환경 설정
│   │   └── artifacts/              # Development HQ가 생성·관리하는 산출물
│   │
│   ├── investment/                # Investment HQ — 투자 관련 업무를 담당
│   │   ├── workflows/              # Investment 업무 Workflow
│   │   ├── agents/                 # Investment 전용 Agent
│   │   ├── projects/               # Investment 업무 Project
│   │   ├── tasks/                  # Investment 업무 Task
│   │   ├── runtime/                 # Investment HQ 실행 환경
│   │   └── config/                  # Investment HQ 설정
│   │
│   └── shared/                    # 여러 HQ에서 공통으로 사용하는 Domain 정의
│
├── projects/                    # Development HQ가 주관하는 Project를 관리
│   ├── active/                   # 현재 진행 중인 Project
│   ├── archived/                 # 종료·보관된 Project
│   └── templates/                # 새로운 Project를 생성하기 위한 Template
│
├── dashboard/                   # 사용자가 Jarvis OS와 HQ를 관리하는 외부 인터페이스
│   ├── web/                      # Web Dashboard UI
│   ├── api/                      # Dashboard와 Kernel을 연결하는 API
│   ├── events/                   # 실시간 상태 변화와 Notification을 전달
│   ├── components/               # Dashboard에서 사용하는 UI Component
│   ├── views/                    # HQ·Project·Workflow·Task·Agent View
│   └── auth/                     # Dashboard 인증과 접근 권한을 관리
│
├── integrations/                # Jarvis OS와 외부 서비스·도구를 연결
│   ├── mcp/                      # MCP 기반 외부 Tool·Service Integration
│   ├── github/                   # GitHub Integration
│   ├── notion/                   # Notion Integration
│   └── providers/                # AI Model·Execution Provider Integration
│
├── docs/                        # Architecture·Decision·Specification·Evidence·Research를 공식 기록
│   ├── architecture/             # Jarvis OS Architecture의 Source of Truth
│   │   ├── baseline/              # Frozen Architecture Baseline
│   │   ├── kernel/                # Kernel Architecture
│   │   ├── hq/                    # Multi-HQ Architecture
│   │   ├── dashboard/             # Dashboard Architecture
│   │   └── integration/           # Integration Architecture
│   ├── decisions/                # Architecture와 주요 기술적 의사결정을 관리
│   │   ├── rfc/                   # Architecture 변경 제안
│   │   ├── adc/                   # 검토 중인 Architecture Decision
│   │   └── adr/                   # 승인된 Architecture Decision
│   ├── specifications/           # 시스템과 구성요소의 요구사항·계약을 정의
│   │   ├── system/
│   │   ├── kernel/
│   │   ├── hq/
│   │   ├── dashboard/
│   │   └── features/
│   ├── validation/                # 구현과 Architecture를 검증한 Evidence를 보관
│   │   ├── mvp/
│   │   ├── dogfooding/
│   │   ├── architecture/
│   │   └── reports/
│   └── research/                  # 아직 공식 Architecture로 확정하지 않은 연구 내용을 보관
│       ├── ai/
│       ├── architecture/
│       └── infrastructure/
│
├── archive/                     # 과거 Version과 Frozen/Deprecated Artifact를 보존
│   ├── architecture/
│   ├── development-hq/
│   ├── validation/
│   └── deprecated/
│
├── examples/                    # Architecture·Agent·Workflow 사용 예제
├── pyproject.toml               # Python Project·Dependency·개발 도구 설정
└── pytest.ini                   # Pytest 실행과 테스트 관련 설정
```

---

## Core Domain Model

```
User
 ↓
Dashboard
 ↓ API / Events
Jarvis Kernel
 ↓
HQ
 ↓
Project
 ↓
Workflow
 ↓
Stage
 ↓
Task
 ↓
Agent
 ↓
Capability
 ↓
Execution
 ↓
Provider / Tool / MCP
```

---

## Development HQ Workflow

```
Software Development Workflow
│
├── Stage 01 — Repository Intelligence
├── Stage 02 — Planning & Specification
├── Stage 03 — Architecture Design
├── Stage 04 — Implementation
├── Stage 05 — Validation
└── Stage 06 — DevOps & Release
```

---

## Responsibility Model

| 영역 | 책임 |
|---|---|
| `core/` | Jarvis OS의 Kernel과 Runtime을 실행 |
| `hqs/development/` | Jarvis OS 전체의 개발·검증·개선을 관리 |
| `hqs/investment/` | 투자 관련 업무를 수행 |
| `projects/` | Development HQ가 주관하는 Project를 관리 |
| `dashboard/` | 사용자가 Jarvis OS와 HQ를 외부에서 관리 |
| `integrations/` | 외부 서비스와 Tool을 연결 |
| `docs/` | Architecture와 개발 지식을 공식적으로 기록 |
| `archive/` | 과거 구조와 Frozen Artifact를 보존 |

---

## Deferred Decisions

다음 항목은 Structure v1.0의 Freeze를 막지 않는 **후속 Architecture Decision 대상**으로 명시적으로 보류한다.

- `projects/`를 HQ별로 물리적으로 분류할지 여부
- `capabilities/`를 `core/` 내부에 둘지 별도 최상위 영역으로 분리할지 여부
- `hqs/shared/`의 실제 도입 시점과 구체적인 범위
- Dashboard의 실제 구현 구조
- Kernel의 세부 Module 및 Interface 구조
- Production Secret Manager 도입 방식
- `docs/guides/`를 별도 영역으로 만들 필요성
- License의 구체적인 종류 선택

---

## Freeze Rule

Structure v1.0 이후 Repository 구조를 변경할 때는 단순한 편의에 따른 이동을 허용하지 않는다.

Architecture Boundary에 영향을 주는 구조 변경은 **RFC → Decision → ADR → Migration → Validation**의 절차를 거친다.

단순한 구현 세부사항 변경은 Structure v1.0의 변경으로 간주하지 않는다.

---

## Relationship to Development HQ v1.0

기존 Development HQ v1.0 Workflow는 이미 Notion에서 Frozen 상태로 관리되고 있으며, Core Pipeline은 `01 Define → 02 Plan → 03 Design → 04 Build → 05 Prove → 06 Release`로 정의되어 있다. Structure v1.0에서는 이 Workflow를 `hqs/development/workflows/software-development/` 아래의 표준 Workflow로 배치한다.

---

## Current Implementation Rule

이 문서는 **Target Structure Archive**다. 문서에 존재하는 모든 디렉터리를 현재 Repository에 즉시 생성하지 않는다.

현재 구현과 Target Architecture 사이의 차이는 별도의 Migration 계획으로 관리한다.

---

## Governance Chain (전사자 주석 — 원본 PDF에는 없음)

이 절은 원본 PDF의 내용이 아니라, 이 문서를 저장소에 반입한 Governance 절차를 추적하기 위해 전사 시점에 추가한 참조 정보다.

| 단계 | 문서 |
|---|---|
| RFC | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` |
| ADC | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md`, `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` |
| ADR | `docs/decisions/adr/ADR-0006-structure-v1-migration.md`, `docs/decisions/adr/ADR-0007-baseline-relocation.md` |
| Migration 실행 | PR #87(`refactor: Structure v1.0 Migration — hqs/, core/execution/, docs/decisions 재배치`) |

Structure v1.0은 이미 승인·실행 완료된 상태이며, 이 문서는 그 승인 내용을 저장소 내부에서 직접 인용 가능하도록 옮긴 것일 뿐 새로운 승인 절차를 개시하지 않는다.
