# Stage 02: Responsibility

**PRD/Specification 생성 책임은 Stage 01로 이동했다**(RFC-0034/ADC-0037/
ADR-0022) — Stage 01이 Multi-Agent Reasoning + Repository Context를
종합해 `stage_01_context["prd"]`를 이미 만들어 Handover한다. Stage 02는
이제 이를 재생성 없이 그대로 전달(passthrough)한다.

## 책임진다

- Stage 01이 만든 PRD/Specification(`prd`)을 `SpecificationResult`
  (`skeleton`/`specification`) 형태로 그대로 전달 — 재생성하지 않는다
  (`stage_02.py::run_stage_02()`)
- Specification을 Stage 03(Architecture & Design)이 바로 소비할 수 있는
  고정된 스키마(`SPECIFICATION.md`)로 반환

## 향후 확장 대상(이번 범위 아님)

- Task Decomposition(구현 단계 목록), Dependency Ordering, Acceptance
  Criteria 정교화, Implementation Planning — 목표 정의상 Stage 02의
  최종 책임이지만, 이번 PRD Synthesis 이동 작업에서는 구현하지 않는다
  (RFC-0034 §5 Non-goals, 별도 후속 작업).

## 책임지지 않는다

- Repository/파일 탐색, AST 분석, PRD/Specification **생성**(→ Stage 01.
  이 Stage는 Stage 01의 Output을 그대로 Input으로 받을 뿐, Context를
  다시 수집하거나 Specification을 재생성하지 않는다)
- Architecture/Design 산출(→ Stage 03) — Specification은 "무엇을 만들지"
  까지만 다루고 "어떻게 구현할지"는 다루지 않는다
- 코드 생성/수정(→ Stage 04), 코드 리뷰/테스트 실행(→ Stage 05)
- Engine 호출 — Requirement & Specification 생성(Engine 1회 호출)이
  Stage 01로 이동했으므로, 현재 `run_stage_02()`는 Engine을 호출하지
  않는다(순수 passthrough)

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음. PRD/Specification 생성 책임 이동(RFC-0034/ADC-0037/ADR-0022)은
Development HQ 내부 Scoped 결정이며, `SpecificationResult` Output
Contract(키/타입)는 무변경 — Stage 03/05는 수정 없이 그대로 동작한다.
