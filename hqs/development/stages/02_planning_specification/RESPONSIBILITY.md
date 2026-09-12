# Stage 02: Responsibility

**PRD/Specification 생성 책임은 Stage 01에 있다**(RFC-0034/ADC-0037/
ADR-0022) — Stage 01이 Multi-Agent Reasoning + Repository Context를
종합해 `stage_01_context["prd"]`를 이미 만들어 Handover한다. Stage 02는
이를 재생성하지 않고 그대로 통과시키되, PRD를 Task로 구조화하고 Task 간
Dependency를 정리해 실행 순서를 만드는 책임을 진다(RFC-0035/ADC-0038/
ADR-0023).

## 책임진다

- Stage 01이 만든 PRD/Specification(`prd`)의 `skeleton`/`specification`을
  재생성 없이 그대로 전달(`stage_02.py::run_stage_02()`)
- Task & Dependency Agent(Engine 1회 호출)로 PRD를 Task 목록으로
  구조화하고 Task 간 Dependency를 판단
- Deterministic Layer(Schema Validation → Dependency Graph Validation →
  Cycle Detection → Topological Ordering → Implementation Plan Assembly →
  Final Aggregation)로 Task & Dependency Agent 출력을 검증하고 실행
  가능한 순서(`plan`)로 조립 — LLM 판단 없이 코드로만 처리
- `SpecificationResult`(`skeleton`/`specification`/`tasks`/`dependencies`/
  `plan` 5개 키)를 Stage 03(Architecture & Design)이 바로 소비할 수 있는
  고정된 스키마(`SPECIFICATION.md`)로 반환

## 책임지지 않는다

- Repository/파일 탐색, AST 분석, PRD/Specification **생성**(→ Stage 01.
  이 Stage는 Stage 01의 Output을 그대로 Input으로 받을 뿐, Context를
  다시 수집하거나 Specification을 재생성하지 않는다)
- Acceptance Criteria 재생성 — Stage 01 PRD의 기존 값을 그대로 유지하며
  별도 Agent를 두지 않는다(RFC-0035/ADC-0038/ADR-0023 Decision 4)
- Task Decomposition/Dependency Judgment를 별도 Agent로 분리 — 정확히
  1개의 Task & Dependency Agent로만 수행한다(Decision 2)
- Dependency Ordering/Implementation Planning에 LLM 판단을 개입시키는 것
  — 전 구간 Deterministic Code로만 처리한다(Decision 3)
- Architecture/Design 산출(→ Stage 03) — Specification은 "무엇을 만들지"
  까지만 다루고 "어떻게 구현할지"는 다루지 않는다
- 코드 생성/수정(→ Stage 04), 코드 리뷰/테스트 실행(→ Stage 05)

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음. Task & Dependency Agent 도입과 Deterministic Layer 실행 모델
(RFC-0035/ADC-0038/ADR-0023)은 Development HQ 내부 Scoped 결정이며,
`SpecificationResult` Output Contract는 5-key로 확장됐지만(Scoped Public
Contract 변경) 새 Runtime/Scheduler/Workflow Parser/Dynamic Routing을
추가하지 않았고 `ParallelRunner`도 변경하지 않았다(이번 DAG에 병렬 노드
없음).
