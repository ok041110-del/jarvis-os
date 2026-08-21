# CLAUDE.md

Claude Code가 이 저장소에서 항상 알아야 하는 최소 persistent instruction.

## Project Identity

Jarvis OS v2 Starter Kit. Development HQ MVP-0001 구현을 시작점으로, Development HQ MVP Dogfooding, Kernel Architecture 연구(RFC/ADC/ADR), Investment HQ(Stock/ETF/Dividend Stock) Dogfooding까지 확장된 문서/실행환경 패키지다.

## Core Rules

### Frozen Architecture

Architecture / Baseline은 직접 수정하지 않는다. Architecture 변경이 필요하면:

RFC → ADC → ADR

순서로 제안한다. (`docs/decisions/rfc/` → `docs/decisions/adc/` → `docs/decisions/adr/`)

### Scope Boundary

Development HQ는 Kernel/Architecture 경계를 우회하지 않는다. 금지 사항은 `hqs/development/IMPLEMENTATION_RULES.md`를 따른다.

### Branch Strategy

- `main` = Stable Source of Truth. `claude/*` = Claude Code 작업 단위 브랜치. `develop`/`release`/`hotfix`는 사용하지 않는다.
- 작업 시작 전 `git fetch --all`로 기존 `claude/*` 브랜치 중복 여부를 확인한다. 동일 작업에 여러 브랜치를 만들지 않는다 — 하나의 작업 단위에는 하나의 작업 브랜치만 사용한다.
- 작업 완료 후 main 반영 여부를 확인한다. main에 반영된 완료 브랜치는 원격에서 정리하고, 미완료/후속 작업/Evidence 보존이 필요한 브랜치는 삭제하지 않는다(orphaned branch 방지, 장기 존속하는 `claude/*` 브랜치를 만들지 않는다).
- Branch Strategy는 Architecture/Governance 절차를 대체하지 않는다 — Architecture/Governance 변경은 이 규칙과 무관하게 항상 RFC → ADC → ADR 절차(Frozen Architecture 항목)를 그대로 따른다.

**PR Creation Criteria**

- PR 필수: 실제 코드/Capability 변경, main에 반영할 실제 산출물이 있는 작업.
- PR 권장: Governance 판단, Freeze/중요 문서 변경, 리뷰 가치가 있는 문서 변경.
- PR 불필요: READ-ONLY Audit, 폐기된 실험, main에 반영할 diff가 없는 브랜치.
- 예외: (1) 사용자가 세션 중 명시적으로 직접 반영을 승인한 경우 PR을 생략할 수 있다. (2) RFC → ADC → ADR은 PR과 별개이며, PR이 Governance 승인을 대체하지 않는다. (3) Merge·브랜치 삭제는 기존 승인 절차를 그대로 유지한다.

**표준 흐름**: 작업 → PR 필요성 판단 → PR → 사용자 승인 → Merge → GitHub 자동 브랜치 삭제 → `fetch --prune`.

### Completion Standard

작업 완료를 주장하기 전에:

- 실제 변경 범위를 확인
- 관련 검증 수행
- 실제 evidence 확인
- 실패한 검증을 성공으로 표현하지 않음
- 불필요한 변경 확인

### Code Documentation

Docstring/주석은 기본 한글로 작성한다(외부 API·프로토콜·표준 명칭 등 고유 기술 용어는 원문 유지 가능).

- **Docstring**: 실질적 설명 가치가 있을 때만, 최대 2줄. 코드만으로 의도가 명확하면 생략. 구현 과정을 설명하는 장문 금지.
- **Comment**: 코드만으로 의도가 명확하면 생략. 필요할 때만, 보통 4~5단어로 간결하게. "무엇을 하는지"보다 "왜 필요한지"를 우선한다. 코드와 같은 내용을 반복하는 주석 금지. TODO/FIXME는 실제 후속 작업이 있을 때만 사용.
- **Code Clarity**: 주석으로 복잡한 코드를 설명하기보다 코드 자체를 단순하게 만든다. 변수·함수명으로 의도를 표현한다. 주석이 필요한 복잡한 로직은 가능하면 구조를 개선한다.
- **Review**: PR/Code Review에서 불필요한 docstring·주석을 제거한다. 기존 코드 수정 시 해당 영역의 과도한 문서화도 함께 정리한다. 기능 변경 없는 docstring/주석 정리는 실제 동작 변경으로 간주하지 않는다.

## Context Loading

작업에 필요한 문서만 선택적으로 읽는다.

- 프로젝트 개요 → `README.md`
- 현재 작업 상태 → `hqs/development/HANDOVER.md`
- Architecture → `docs/architecture/baseline/BASELINE.md`
- Development HQ 규칙 → `hqs/development/IMPLEMENTATION_RULES.md`
- Development HQ 구조 → `hqs/development/BASELINE.md`
- MVP → `hqs/development/MVP.md`
- Governance → `docs/decisions/rfc/`, `docs/decisions/adc/`, `docs/decisions/adr/`, `docs/governance/`
- Kernel Architecture 연구 → `docs/architecture/core/`
- Execution Layer → `docs/core/execution-layer/`
- Investment HQ → `hqs/investment/`
- 세션 기억 → Claude-Mem

전체 문서를 작업마다 일괄 로드하지 않는다.

## Development HQ

작업 지향 세션에서 task-observer를 활성화한다.

## Execution Environment

- Task Observer — 작업 세션 관찰
- Claude-Mem — 세션 간 영속 메모리
- OmniRoute — Provider/Model routing

설치/검증 상세: `.claude/docs/integrations/`

## Skills

- `task-observer`
- `task-intake`
- `context-loader`
- `task-planner`
- `validation`
- `md-writer`
- `handover`
- `branch-lifecycle`

각 Skill의 상세 동작은 해당 SKILL.md에서 관리한다.

## Maintenance

CLAUDE.md 변경 시:

- 프로젝트 핵심 규칙이 실제 상태와 일치하는지 확인
- 불필요한 상세 내용을 추가하지 않음
- 변경된 실행환경/Skill 목록을 반영
- Architecture 문서를 직접 수정하지 않음
