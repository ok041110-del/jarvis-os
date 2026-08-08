---
name: handover
description: Produces a minimal-context handover document so the next session or agent can pick up current work without re-deriving it. Use at the end of a work session or task in this repository, or when the user asks for a handover/summary of where things stand. Never copies existing documents at length and never introduces new Architecture decisions.
---

# handover

## 책임

현재 작업을 다음 세션/Agent가 최소 Context로 이어받게 한다.

## 구조

```markdown
# Handover

## Task

## Completed

## Current State

## Decisions

## Changed Files

## Validation

## Open Issues

## Next Step

## Important Context
```

## 규칙

- 기존 문서를 장황하게 복사하지 않는다.
- 다음 작업에 필요한 정보만 남긴다.
- Open Issues와 Next Step은 명확히 한다.
- Architecture의 source of truth를 대체하지 않는다.
- 새로운 Architecture 결정을 만들지 않는다.

## Pre-Flight

Handover만 읽어도 다음 세션이 현재 상태와 Next Step을 이해할 수 있는지 확인한다.
