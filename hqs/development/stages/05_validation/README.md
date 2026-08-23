# Stage 05: Validation

## 요약

Stage 04(Implementation)의 Output을 입력으로 받아, 실제 변경이
Stage 02 Specification/Stage 03 Design에 부합하는지 검증하고 구조화된
Evidence와 명확한 판정(PASS/FAIL/PARTIAL)을 생성한다. **문제를 수정하지
않는다** — 발견된 문제는 Evidence와 Open Issue로만 반환한다.

진입점: [`stage_05.py`](./stage_05.py)의 `run_stage_05()`. 신규
Agent/Capability 없음. `IMPLEMENTATION_RULES.md`의 "Policy 구현 금지"
원칙에 따라 PASS/FAIL/PARTIAL 판정은 전부 **결정적 규칙**(Engine
미호출)으로 계산한다 — Engine은 `agents.backend_agent_code_review()`
(기존 Capability, MVP-0001) 재사용으로 보조 Evidence만 만들고, 판정에
직접 반영하지 않는다.

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 6개 Capability의
  Input → Validation → Output → Evidence
- [`VALIDATION.md`](./VALIDATION.md) — `run_stage_05()`이 반환하는
  Validation Output Schema(고정)와 검증 방법(mock 기반 + real Engine/
  실제 pytest E2E)

## 근거 문서

- `hqs/development/stages/02_planning_specification/`(Stage 02 —
  `skeleton.scope_candidates` 재사용)
- `hqs/development/stages/03_architecture_design/`(Stage 03 — Design
  자체는 이번 Stage에서 직접 소비하지 않음, `RESPONSIBILITY.md` 참고)
- `hqs/development/stages/04_implementation/`(Stage 04 — 이 Stage의
  주 Input Schema 출처)
- `hqs/development/mvp/agents.py`(`backend_agent_code_review` — 재사용
  하는 기존 Capability)
- `docs/research/DEV-HQ-V2.0-STAGE-04-E2E-0001.md`(백업/적용/pytest/
  diff/원상복구 방법론 — 이 Stage의 Test Execution Capability가 코드로
  formalize한 절차)
- `hqs/development/IMPLEMENTATION_RULES.md`("Policy 구현 금지" — 이
  Stage가 판정을 결정적 규칙으로 유지한 이유)
