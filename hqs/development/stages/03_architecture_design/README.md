# Stage 03: Architecture / Design

## 요약

Stage 01(Context Analysis)의 Context와 Stage 02(Planning & Specification)의
Specification을 입력으로 받아, Stage 04(Implementation)가 바로 소비할 수
있는 **Architecture / Design Specification**을 생성한다. Architecture
Definition / Component Identification / Responsibility Allocation /
Interface·Contract Identification / Data Flow / Dependency·Boundary
Definition / Implementation Strategy / Design Constraints / Design Risks
9개 관점을 하나의 Design 텍스트로 구조화한다.

실행 진입점은 [`stage_03.py`](./stage_03.py)의 `run_stage_03()`이다.
새 Agent/Capability를 추가하지 않고, 기존 `agents.design_agent_design()`
(MVP-0004부터 존재하는 Design Capability)을 그대로 재사용한다 —
Component Candidates(Stage 01 `candidate_index`)와 Implementation Scope/
Constraints/Risks(Stage 02 `skeleton`)를 결정적으로(Engine 호출 없이)
재배치해 골격을 만들고, 그 골격을 Stage 02 Specification에 덧붙여 같은
Engine 호출 한 번으로 나머지 관점(Architecture Definition/Component
Identification/Responsibility Allocation/Interface·Contract
Identification/Data Flow/Implementation Strategy)까지 포함한 Design을
만든다(자세한 근거는 `CAPABILITIES.md`).

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 2개 Capability의
  Input → Analysis → Output → Validation
- [`DESIGN.md`](./DESIGN.md) — `run_stage_03()`이 반환하는 Design 스키마와
  9개 관점이 어디서 채워지는지
- [`VALIDATION.md`](./VALIDATION.md) — 검증 방법(mock 기반 + real Engine
  E2E 1건)과 현재 커버리지

## 근거 문서

- `hqs/development/stages/01_context_analysis/`(Stage 01 — Component
  Candidates 출처)
- `hqs/development/stages/02_planning_specification/`(Stage 02 — 이
  Stage의 주 Input Schema 출처)
- `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`(Stage 폴더
  구조, 신규 Capability 판단 기준 §4)
- `hqs/development/mvp/workflow_ast_context.py`(`identify_target` —
  Design 텍스트에서 AST 시작점을 식별하는 기존 구현. Stage 03은 이
  식별을 스스로 수행하지 않는다, `RESPONSIBILITY.md` 참고)
