# CLAUDE.md

Claude Code가 이 저장소에서 항상 알아야 하는 최소 persistent instruction.

## Project Identity

Jarvis OS v2 Starter Kit. 이 저장소는 Development HQ MVP-0001 구현을 위한 문서/실행환경 패키지다.

## Core Rules

### Frozen Architecture

Architecture / Baseline은 직접 수정하지 않는다. Architecture 변경이 필요하면:

RFC → ADC → ADR

순서로 제안한다. (`docs/02_rfc/` → `docs/03_adc/` → `docs/04_adr/`)

### Scope Boundary

Development HQ는 Kernel/Architecture 경계를 우회하지 않는다. 금지 사항은 `development-hq/IMPLEMENTATION_RULES.md`를 따른다.

### Branch Strategy

- `main` = Stable Source of Truth. `claude/*` = Claude Code 작업 단위 브랜치. `develop`/`release`/`hotfix`는 사용하지 않는다.
- 작업 시작 전 `git fetch --all`로 기존 `claude/*` 브랜치 중복 여부를 확인한다. 동일 작업에 여러 브랜치를 만들지 않는다 — 하나의 작업 단위에는 하나의 작업 브랜치만 사용한다.
- 작업 완료 후 main 반영 여부를 확인한다. main에 반영된 완료 브랜치는 원격에서 정리하고, 미완료/후속 작업/Evidence 보존이 필요한 브랜치는 삭제하지 않는다(orphaned branch 방지, 장기 존속하는 `claude/*` 브랜치를 만들지 않는다).
- Branch Strategy는 Architecture/Governance 절차를 대체하지 않는다 — Architecture/Governance 변경은 이 규칙과 무관하게 항상 RFC → ADC → ADR 절차(Frozen Architecture 항목)를 그대로 따른다.

### Completion Standard

작업 완료를 주장하기 전에:

- 실제 변경 범위를 확인
- 관련 검증 수행
- 실제 evidence 확인
- 실패한 검증을 성공으로 표현하지 않음
- 불필요한 변경 확인

## Context Loading

작업에 필요한 문서만 선택적으로 읽는다.

- 프로젝트 개요 → `README.md`
- 현재 작업 상태 → `development-hq/HANDOVER.md`
- Architecture → `docs/01_architecture/BASELINE.md`
- Development HQ 규칙 → `development-hq/IMPLEMENTATION_RULES.md`
- Development HQ 구조 → `development-hq/BASELINE.md`
- MVP → `development-hq/MVP.md`
- Governance → `docs/02_rfc/`, `docs/03_adc/`, `docs/04_adr/`
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

각 Skill의 상세 동작은 해당 SKILL.md에서 관리한다.

## Maintenance

CLAUDE.md 변경 시:

- 프로젝트 핵심 규칙이 실제 상태와 일치하는지 확인
- 불필요한 상세 내용을 추가하지 않음
- 변경된 실행환경/Skill 목록을 반영
- Architecture 문서를 직접 수정하지 않음
