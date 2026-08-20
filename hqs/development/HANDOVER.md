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
| Development HQ MVP | MVP-0001 완료(원 구현) + MVP-0002~MVP-0052 Dogfooding/결함 수정/Capability Prototype 완료 (Evidence 기반, `docs/01_mvp/`) |
| Kernel | Responsibility·Public Contract·Logical Reference Architecture는 BASELINE.md §11 이하에 정의됨(ADR-0002~0005). Component Architecture(Scheduler/Registry 등 실제 구현)는 여전히 Out of Scope — "설계 안 함"이 아니라 "책임은 정의됨, 구현은 의도적으로 미착수" |
| Engine MVP | 종료 대상으로 판정됨 (`GOVERNANCE-REVIEW-0004`) — success/실패 경로 모두 real-Engine Evidence로 검증 완료 |
| Development HQ MVP Validation | **종료 확정 — Stable v1.0 Freeze** (`GOVERNANCE-REVIEW-0007` 권고 → `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`로 승인·확정). Production 진입 Blocking과는 별개(그쪽은 계속 Open) |
| Phase 9~12 (Engine Adapter/Prompt Specification/Prompt Cache/Runtime·Automation) | 전부 종료, NEED-DRIVEN DEFER — `PHASE9-CLOSURE-0001.md`, `PHASE10-CLOSURE-0001.md`, `PHASE11-PROMPT-CACHE-AUDIT-0001.md`, `PHASE12-RUNTIME-AUTOMATION-AUDIT-0001.md`/`PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001.md`. 재개 조건은 각 원문서 참조 |
| Stock Team (Investment 영역) | Promoted (최소 업무 범위 한정, Agent/Architecture 미확정) — `docs/research/STOCK-TEAM-DEFINITION-0001.md` |
| ETF Team (Investment 영역) | Promoted (최소 업무 범위 한정, Agent/Architecture 미확정) — `docs/research/ETF-TEAM-DEFINITION-0001.md` |
| Dividend Stock Team (Investment 영역) | **Promoted** (독립 명명 + Stock Team 확장으로 문서화, Agent/Architecture 미확정) — `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md` (JNJ/KO/PG 3/3 Evidence 기반) |
| Investment HQ 자체 | 최소 구조(Investment HQ → Investment Division → Stock/ETF/Dividend Stock Team)를 문서 수준에서 확인함 — `docs/research/INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md`. Registry 미등록·Lifecycle 없음(Kernel 기능 자체가 미구현 — Development HQ와 동일한 비-live 상태). 전체 Architecture 설계(Mission/Boundary/Capability 등록)는 RFC 대상이며 아직 열리지 않음(ADC 채택 기준 미충족) |

## Frozen Architecture

다음은 더 이상 변경하지 않는다.

- Vision, Core Principles
- Meta Architecture: `Jarvis OS → HQ → Agent → Connector(MCP)` (Division/Team은 HQ 내부 선택 구조)
- Concept Model (`docs/architecture/baseline/BASELINE.md` 6장)
- System Boundary — Jarvis OS/HQ/Agent 책임 분류 (`docs/architecture/baseline/BASELINE.md` 7장)

## Approved Baselines

- `docs/architecture/baseline/BASELINE.md` — Jarvis OS Architecture Baseline (현재 v1.6, RFC → ADC → ADR 경로로만 갱신)
- `hqs/development/BASELINE.md` — Development HQ Baseline v1.0

두 문서 모두 이 Starter Kit의 최우선 참조 문서다. 이 문서들과 충돌하는 어떤 판단도 우선하지 않는다.

## MVP Scope

`hqs/development/MVP.md` 참조. 요약:

- User Scenario: 코드 리뷰 + 테스트 케이스 제안
- Workflow: `Task 1 (code_review) → Task 2 (test_execution)`, 단일 선형 체인
- Agent: Backend Agent, QA Agent (2개)
- Capability: `code_review`, `test_execution` (기존 예시 재사용, 신규 추가 없음)
- 저장소·Policy·Multi-Engine·Multi-HQ 모두 Out of Scope

## MVP Exit Criteria

입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환된다. 이 과정에서 Registry/Scheduler/Policy에 해당하는 범용 서비스 코드가 생성되지 않았다면 MVP는 성공이다.

## Implementation Rules

`hqs/development/IMPLEMENTATION_RULES.md`를 전문 그대로 따른다. 요약:

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
RFC (docs/decisions/rfc)
↓
ADC (docs/decisions/adc/ADC.md — Single Source of Truth)
↓
ADR (docs/decisions/adr)
↓
Architecture Baseline Update
↓
Development HQ Baseline Update
↓
Implementation
```

새로운 ADC는 다음 중 하나를 만족해야 채택된다: (1) 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다, (2) 결정이 늦어질수록 되돌리는 비용이 매우 커진다.

현재 Open Decision 12개는 `docs/decisions/adc/ADC.md`에 전부 기록되어 있으며, 이 중 ADC-02·ADC-09·ADC-10이 NOW 우선순위다. MVP 구현은 이 Open Decision들과 무관하게 진행 가능하다 (Kernel 범위이거나, System Boundary 원칙의 세부 사항이기 때문).

별도로 `docs/decisions/rfc/RFC_CANDIDATES.md`에 이미 논의되었으나 아직 정식 RFC로 승격되지 않은 Architecture 후보(Capability/Agent/Engine 관계 정밀화 등)가 기록되어 있다. **이 문서는 참고용이며, MVP-0001 구현에는 어떤 내용도 반영하지 않는다.**

## What Claude Code Can Do

- `hqs/development/MVP.md`에 정의된 범위 내에서 코드 작성
- Task 1(code_review) → Task 2(test_execution) 흐름을 스크립트/함수 호출로 직접 구현
- 단일 Engine을 호출하는 함수 하나 작성
- Agent-Capability 매핑을 리터럴 딕셔너리로 작성
- MVP 구현 중 Architecture 문제를 발견하면, `docs/decisions/rfc`에 문제를 기록 (해결은 하지 않음)

## What Claude Code Must Never Do

- Architecture Baseline 또는 Development HQ Baseline을 직접 수정
- 새로운 Component, Layer, Concept를 코드나 문서에 도입
- Scheduler, Registry, Policy Engine, Engine Gateway(추상화 계층), Memory Service, Event Bus를 구현
- MVP 범위를 벗어난 기능(Multi-HQ, Multi-Engine, 영속 저장소, 백그라운드/분산 실행) 추가
- Implementation Stop Trigger 발생 시 스스로 해결하려 시도

## Kernel Extraction Rule

Kernel은 만드는 것이 아니라 발견(Extraction)하는 것이다. MVP 구현 중 공통 기능의 필요성이 드러나면, 그 필요성을 코드 주석 또는 `docs/decisions/adc/ADC.md`에 후보로 기록하고, 실제 Kernel 구현은 이후 별도의 RFC → ADC → ADR 절차를 거쳐 진행한다. Development HQ MVP 단계에서 Kernel을 미리 구현하지 않는다.

## Next Step

MVP-0001의 최소 스크립트 작성은 이미 완료되었고
(`hqs/development/mvp/`, `docs/01_mvp/MVP-0001~0052`), **Development HQ
MVP Validation은 종료 확정되어 Stable v1.0으로 Freeze됐다**
(`docs/architecture/core/DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`).
Stock/ETF/Dividend Stock Team 3개 트랙 모두 3회 이상 반복으로 Promoted
됐다(`STOCK-TEAM-DEFINITION-0001.md`, `ETF-TEAM-DEFINITION-0001.md`,
`DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`). Phase 9~12(Engine Adapter/
Prompt Specification/Prompt Cache/Runtime·Automation)도 전부 종료됐다
— 각 재개 조건은 해당 Phase 원문서 참조. 이는 "앞으로 아무 것도 하지
않는다"는 뜻이 아니라 — 새로운 결함이 실제로 발견되면 MVP 번호를 이어서
계속 기록하고, 각 Phase 재개 조건이 실제로 충족되면 그 Phase를 다시
연다 — 새 MVP나 Phase를 선제적으로 만들어 검증 범위를 확장하지는
않는다는 뜻이다.

**다음 단계는 새 기능 개발이 아니라 Kernel Validation이다.**

1. **Kernel Boundary/Component 책임 검증**을 우선한다 —
   `docs/architecture/baseline/BASELINE.md` §11(Kernel Responsibility)과
   §10(Out of Scope, Component Architecture)의 경계가 실제 Evidence
   (Development HQ + Investment Dogfooding 누적 14건: MVP 10건 +
   Stock/ETF/Dividend Stock)와 계속 일치하는지 확인하는 것이 다음
   작업이다. 새 Kernel Component를 미리 설계하지 않는다 — Extraction
   Candidate가 실제로 나타났을 때만 다룬다.
2. `docs/decisions/adc/ADC.md`의 NOW 우선순위 Open Decision(ADC-02,
   ADC-09, ADC-10)은 **구현 근거가 생길 때까지 계속 Open으로 유지한다**
   (`GOVERNANCE-REVIEW-0006`) — 지금 억지로 결정하지 않는다.
3. Production 진입 Blocking(Engine caller 위치, `ADC-0010`/`ADC-0011`
   Not Accepted)은 별도 트랙으로 계속 열려 있다 — Kernel Validation과
   순서상 무관하게 진행 가능.
4. AGG Data Boundary 관찰은 4회 재현 시도(AGG 재실행 2회 + JNJ + KO +
   PG) 전부 미재현 — Execution 문제로 확정하지 않는다
   (`docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`).
5. Implementation Stop Trigger·Kernel Extraction Candidate 발생 여부는
   신규 작업마다 계속 점검한다 (지금까지 발동 사례 없음).
