---
name: task-planner
description: Turns a bounded task (from task-intake) with its loaded context (from context-loader) into an executable step-by-step plan. Use before starting implementation on any non-trivial task in this repository, to define Steps, affected Files/Components, a Validation Plan, and Completion Criteria up front.
---

# task-planner

## 책임

확정된 Task를 실행 가능한 계획으로 만든다.

## 출력

- **Objective**
- **Preconditions**
- **Steps**
- **Files / Components**
- **Validation Plan**
- **Risks**
- **Completion Criteria**

## 규칙

- 하나의 bounded task를 계획한다.
- 구현과 검증을 함께 계획한다.
- 불필요한 파일을 포함하지 않는다.
- Architecture 변경은 Governance proposal로 전환한다 (`docs/02_rfc/` → `docs/03_adc/` → `docs/04_adr/`).

## Pre-Flight

각 Step이 Scope 안에 있고, 각 Step에 검증 방법이 존재하는지 확인한다.
