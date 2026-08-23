# Stage 02: Planning & Specification

## 요약

Stage 01(Context Analysis)이 만든 Context와 원본 Issue를 입력으로 받아,
Stage 03(Architecture & Design)이 바로 쓸 수 있는 **Specification**을
생성한다. Problem Definition / Requirement Analysis / Task Decomposition /
Constraints / Risk / Acceptance Criteria / Implementation Scope 7개
관점을 하나의 Specification 텍스트에 구조화한다.

실행 진입점은 [`stage_02.py`](./stage_02.py)의 `run_stage_02()`이다.
새 Agent/Capability를 추가하지 않고, 기존
`agents.requirements_agent_requirement_analysis()`(MVP-0004부터 존재하는
Requirement Analysis Capability)를 그대로 재사용한다 — 7개 관점 중
Problem Definition/Constraints/Risk/Implementation Scope 후보는
Stage 01 Context에서 결정적으로(Engine 호출 없이) 뽑고, 그 골격을
Issue에 덧붙여 같은 Engine 호출 한 번으로 Task Decomposition/Acceptance
Criteria까지 포함한 Specification을 만든다(자세한 근거는
`CAPABILITIES.md`).

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 2개 Capability의
  Input → Analysis → Output → Validation
- [`SPECIFICATION.md`](./SPECIFICATION.md) — `run_stage_02()`이 반환하는
  Specification 스키마와 7개 관점이 어디서 채워지는지
- [`VALIDATION.md`](./VALIDATION.md) — 검증 방법(mock 기반 + real Engine
  E2E 1건)과 현재 커버리지

## 근거 문서

- `hqs/development/stages/01_context_analysis/`(Stage 01 — 이 Stage의
  Input Schema 출처)
- `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`(Stage 폴더
  구조, 신규 Capability 판단 기준 §4)
- `hqs/development/IMPLEMENTATION_RULES.md`(신규 Capability/Agent 추가
  금지 원칙 — 이 Stage가 신규 Capability를 만들지 않은 이유)
