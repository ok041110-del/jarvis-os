---
name: task-intake
description: Structures a user request into a bounded task before any implementation starts. Use at the start of any non-trivial request in this repository — before reading code, before writing files — to pin down Scope, Non-goals, and Acceptance Criteria. Also use when a request seems to imply an Architecture change, so it can be redirected to the RFC → ADC → ADR path instead of direct implementation.
---

# task-intake

## 책임

사용자 요청을 bounded task로 구조화한다. 구현하지 않는다.

## 출력

- **Task** — 한 줄 요약
- **Type** — 아래 Type 중 하나
- **Scope** — 이번 작업이 다루는 범위
- **Non-goals** — 이번 작업이 다루지 않는 것
- **Acceptance Criteria** — 완료로 인정되는 조건
- **Required Context** — 다음 단계(context-loader)가 확인해야 할 문서/영역
- **Boundary / Risk** — Kernel/Architecture 경계 관련 위험 여부
- **Next Skill** — 이어질 Skill (보통 `context-loader`)

## Type

- `implementation`
- `investigation`
- `validation`
- `documentation`
- `architecture-change proposal`

## 규칙

- 파일을 수정하지 않는다.
- 요구사항을 임의로 추가하지 않는다.
- 구현 방법을 미리 결정하지 않는다.
- Architecture 변경이면 구현을 멈추고 RFC → ADC → ADR로 전환한다 (`docs/02_rfc/` → `docs/03_adc/` → `docs/04_adr/`).

## Pre-Flight

Scope / Non-goals / Acceptance Criteria가 사용자의 실제 요청과 일치하는지 확인한다.
