# Stage 02: Planning & Specification

## 요약

Stage 01(Context Analysis)이 만든 PRD(`skeleton`/`specification`)를
입력으로 받아, Task & Dependency Agent(Engine 1회 호출)로 Task를
구조화하고 Task 간 Dependency를 판단한 뒤, Deterministic Layer로
검증·정렬·조립해 Stage 03(Architecture & Design)이 바로 쓸 수 있는
**Specification**(`SpecificationResult`, 5-key)을 만든다(RFC-0035/
ADC-0038/ADR-0023).

진입점: [`stage_02.py`](./stage_02.py)의 `run_stage_02()`.
`skeleton`/`specification`은 Stage 01의 `prd`를 재생성 없이 그대로
전달하고(ADR-0022 유지), `tasks`/`dependencies`/`plan`은
[`task_dependency_agent.py`](./task_dependency_agent.py)(Engine 1회
호출) + [`planning_pipeline.py`](./planning_pipeline.py)(Schema
Validation → Dependency Graph Validation → Cycle Detection →
Topological Ordering → Implementation Plan Assembly, LLM 호출 없음)로
새로 산출한다(근거: `CAPABILITIES.md`).

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 3개 Capability(PRD
  Passthrough, Task & Dependency Agent, Deterministic Layer)의
  Input → Analysis → Output → Validation
- [`SPECIFICATION.md`](./SPECIFICATION.md) — `run_stage_02()`이 반환하는
  `SpecificationResult`(5-key) 스키마와 7개 관점이 어디서 채워지는지
- [`VALIDATION.md`](./VALIDATION.md) — 검증 방법(단위 테스트 + mock 기반
  통합 테스트)과 현재 커버리지

## 근거 문서

- `hqs/development/stages/01_context_analysis/`(Stage 01 — 이 Stage의
  Input Schema 출처)
- `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`(Stage 폴더
  구조, 신규 Capability 판단 기준 §4)
- `hqs/development/IMPLEMENTATION_RULES.md`(신규 Capability/Agent 추가
  금지 원칙 — 이 Stage가 신규 Capability를 만들지 않은 이유)
