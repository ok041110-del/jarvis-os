---
name: validation
description: Checks whether completed work in this repository actually satisfies its Acceptance Criteria and project rules before it is reported as done. Use after implementation, before claiming a task complete — checks scope, Architecture/Governance compliance, tests, syntax/formatting, related-doc consistency, and unintended changes. Judges strictly from actual diff and actual verification output, never from assumption.
---

# validation

## 책임

작업 결과가 요구사항과 프로젝트 규칙을 만족하는지 검증한다.

## 순서

1. Acceptance Criteria
2. 변경 범위
3. Architecture / Governance
4. Tests
5. 코드/Markdown 문법
6. formatting / 줄바꿈
7. 관련 문서 정합성
8. unintended change

## 결과

- `PASS`
- `PASS WITH NOTES`
- `FAIL`

## 특히 확인

- 문법이 올바른가?
- 더 적절한 문법/구현 방식이 있는가?
- 줄바꿈과 formatting이 정상인가?
- 불필요한 변경이 없는가?
- 기존 계약을 깨지 않았는가?

## Pre-Flight

실제 diff와 실제 검증 결과를 기준으로 판정한다.
