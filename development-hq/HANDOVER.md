# HANDOVER.md

## Project Summary

Jarvis OS는 AI Organization Operating System이다. 여러 HQ(업무 영역)를 실행하고 관리하는 운영체제를 목표로 하며, Development HQ는 그 첫 번째 HQ이자 향후 모든 HQ의 Reference Architecture다.

지금까지의 Architecture 설계 단계(Vision → Principles → Meta Architecture → Concept Model → System Boundary → Core Component 검토 → Baseline Freeze → Development HQ Reference Architecture → MVP 정의)가 완료되었고, Development HQ MVP-0001 구현과 그 이후 MVP-0002~MVP-0048 Dogfooding·결함 수정, Kernel Architecture 연구(RFC/ADC/ADR), Investment 영역(Stock/ETF/Dividend Stock) Dogfooding까지 실제로 진행된 상태다. 아래 "Current Status"가 현재 실제 진행 상태이며, "Next Step"은 그 다음에 남은 작업이다.

## Core Principles (필독)

1. **Architecture를 변경하지 않는다.** Jarvis OS Architecture Baseline과 Development HQ Baseline은 구현 편의를 이유로 수정되지 않는다.
2. **이 Starter Kit은 Frozen이다.** 여기 포함된 모든 문서는 v1.0 Final이며, 구현 중 임의로 고쳐 쓰지 않는다.
3. **HANDOVER.md를 기준으로 구현을 시작한다.** 다른 문서와 판단이 갈릴 경우, 본 문서의 "Next Step"과 "Implementation Stop Triggers"를 우선한다.
4. **Architecture 변경이 필요하면 RFC → ADC → ADR 절차를 따른다.** 직접 해결하지 않는다.

## Current Status

| 항목 | 상태 |
|---|---|
| Jarvis OS Architecture Baseline | v1.6 (RFC → ADC → ADR 경로로만 갱신, 직접 수정은 여전히 금지) |
| Development HQ Baseline | v1.0, Frozen (미변경) |
| Development HQ MVP | MVP-0001 완료(원 구현) + MVP-0002~MVP-0048 Dogfooding/결함 수정 완료 (Evidence 기반, `docs/01_mvp/`) |
| Kernel | Responsibility·Public Contract·Logical Reference Architecture는 BASELINE.md §11 이하에 정의됨(ADR-0002~0005). Component Architecture(Scheduler/Registry 등 실제 구현)는 여전히 Out of Scope — "설계 안 함"이 아니라 "책임은 정의됨, 구현은 의도적으로 미착수" |
| Engine MVP | 종료 대상으로 판정됨 (`GOVERNANCE-REVIEW-0004`) — success/실패 경로 모두 real-Engine Evidence로 검증 완료 |
| Stock Team (Investment 영역) | Promoted (최소 업무 범위 한정, Agent/Architecture 미확정) — `docs/research/STOCK-TEAM-DEFINITION-0001.md` |
| ETF Team (Investment 영역) | Promoted (최소 업무 범위 한정, Agent/Architecture 미확정) — `docs/research/ETF-TEAM-DEFINITION-0001.md` |
| Dividend Stock Team (Investment 영역) | Dogfooding 1회(JNJ) 진행, 승격 여부 미결정 — 최소 2회 이상 추가 실행 필요 (`docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md`) |
| Investment HQ 자체 | 아직 이 저장소에 인스턴스화되어 있지 않음 (Stock/ETF/Dividend Stock은 모두 project-local Dogfooding, Development HQ Registry 등록 없음) |

## Frozen Architecture

다음은 더 이상 변경하지 않는다.

- Vision, Core Principles
- Meta Architecture: `Jarvis OS → HQ → Agent → Connector(MCP)` (Division/Team은 HQ 내부 선택 구조)
- Concept Model (`docs/01_architecture/BASELINE.md` 6장)
- System Boundary — Jarvis OS/HQ/Agent 책임 분류 (`docs/01_architecture/BASELINE.md` 7장)

## Approved Baselines

- `docs/01_architecture/BASELINE.md` — Jarvis OS Architecture Baseline (현재 v1.6, RFC → ADC → ADR 경로로만 갱신)
- `development-hq/BASELINE.md` — Development HQ Baseline v1.0

두 문서 모두 이 Starter Kit의 최우선 참조 문서다. 이 문서들과 충돌하는 어떤 판단도 우선하지 않는다.

## MVP Scope

`development-hq/MVP.md` 참조. 요약:

- User Scenario: 코드 리뷰 + 테스트 케이스 제안
- Workflow: `Task 1 (code_review) → Task 2 (test_execution)`, 단일 선형 체인
- Agent: Backend Agent, QA Agent (2개)
- Capability: `code_review`, `test_execution` (기존 예시 재사용, 신규 추가 없음)
- 저장소·Policy·Multi-Engine·Multi-HQ 모두 Out of Scope

## MVP Exit Criteria

입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환된다. 이 과정에서 Registry/Scheduler/Policy에 해당하는 범용 서비스 코드가 생성되지 않았다면 MVP는 성공이다.

## Implementation Rules

`development-hq/IMPLEMENTATION_RULES.md`를 전문 그대로 따른다. 요약:

- Workflow Parser, Scheduler, Registry, Runtime, Engine Gateway(추상화), Policy, Memory Service, Event Bus — 모두 구현 금지
- 신규 Capability/Agent 추가 금지
- Task 순서는 직접 함수 호출로 하드코딩

## Implementation Stop Triggers

다음 중 하나라도 실제 코드에서 발생하면 **즉시 구현을 중단**하고 Architecture Governance 절차로 넘긴다. 직접 해결하지 않는다.

1. Agent-Capability 매핑이 Registry처럼 일반화되려는 경우 (딕셔너리 → 클래스/서비스)
2. Task 호출이 Workflow Parser 또는 Scheduler 형태로 일반화되려는 경우 (직접 호출 → 조건문/설정 파일/파서)

이는 Kernel Extraction Candidate가 예상보다 빨리 필요해졌다는 신호다.

## Architecture Governance

```
RFC (docs/02_rfc)
↓
ADC (docs/03_adc/ADC.md — Single Source of Truth)
↓
ADR (docs/04_adr)
↓
Architecture Baseline Update
↓
Development HQ Baseline Update
↓
Implementation
```

새로운 ADC는 다음 중 하나를 만족해야 채택된다: (1) 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다, (2) 결정이 늦어질수록 되돌리는 비용이 매우 커진다.

현재 Open Decision 12개는 `docs/03_adc/ADC.md`에 전부 기록되어 있으며, 이 중 ADC-02·ADC-09·ADC-10이 NOW 우선순위다. MVP 구현은 이 Open Decision들과 무관하게 진행 가능하다 (Kernel 범위이거나, System Boundary 원칙의 세부 사항이기 때문).

별도로 `docs/02_rfc/RFC_CANDIDATES.md`에 이미 논의되었으나 아직 정식 RFC로 승격되지 않은 Architecture 후보(Capability/Agent/Engine 관계 정밀화 등)가 기록되어 있다. **이 문서는 참고용이며, MVP-0001 구현에는 어떤 내용도 반영하지 않는다.**

## What Claude Code Can Do

- `development-hq/MVP.md`에 정의된 범위 내에서 코드 작성
- Task 1(code_review) → Task 2(test_execution) 흐름을 스크립트/함수 호출로 직접 구현
- 단일 Engine을 호출하는 함수 하나 작성
- Agent-Capability 매핑을 리터럴 딕셔너리로 작성
- MVP 구현 중 Architecture 문제를 발견하면, `docs/02_rfc`에 문제를 기록 (해결은 하지 않음)

## What Claude Code Must Never Do

- Architecture Baseline 또는 Development HQ Baseline을 직접 수정
- 새로운 Component, Layer, Concept를 코드나 문서에 도입
- Scheduler, Registry, Policy Engine, Engine Gateway(추상화 계층), Memory Service, Event Bus를 구현
- MVP 범위를 벗어난 기능(Multi-HQ, Multi-Engine, 영속 저장소, 백그라운드/분산 실행) 추가
- Implementation Stop Trigger 발생 시 스스로 해결하려 시도

## Kernel Extraction Rule

Kernel은 만드는 것이 아니라 발견(Extraction)하는 것이다. MVP 구현 중 공통 기능의 필요성이 드러나면, 그 필요성을 코드 주석 또는 `docs/03_adc/ADC.md`에 후보로 기록하고, 실제 Kernel 구현은 이후 별도의 RFC → ADC → ADR 절차를 거쳐 진행한다. Development HQ MVP 단계에서 Kernel을 미리 구현하지 않는다.

## Next Step

MVP-0001의 최소 스크립트 작성(위 1~4단계에 해당하는 작업)은 이미 완료되었다
(`development-hq/mvp/`, `docs/01_mvp/MVP-0001~0048`). 현재 실제로 열려 있는
작업은 다음과 같다.

1. Dividend Stock Team: 추가 Dogfooding 1~2회 실행(예: KO, PG 등 다른 산업의
   배당주) — Dividend Quality/Valuation 역할의 반복성과 "Stock Team 확장 vs
   독립 Team" 판단 근거 확보 (`docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` §7)
2. AGG 실행에서 1회 관찰된 "Engine의 데이터 범위 이탈"의 재현 여부 계속 관찰
   (JNJ에서는 미재현, 현재 1/2)
3. `docs/03_adc/ADC.md`의 NOW 우선순위 Open Decision(ADC-02, ADC-09, ADC-10)은
   여전히 Open — MVP/Dogfooding 진행과 무관하게 별도 트랙으로 존재
4. Implementation Stop Trigger·Kernel Extraction Candidate 발생 여부는 신규
   MVP/Dogfooding마다 계속 점검한다 (지금까지 발동 사례 없음)
