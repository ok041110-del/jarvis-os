# Stage 01: Context Analysis

## 요약

Repository, 문서, 코드 구조, AST, Dependency를 분석해 후속 Stage(02
Planning & Specification 이하)가 사용할 수 있는 Context를 생성한다.
이전 이름은 "Repository Intelligence"였다(ADR-0001 §4) — Responsibility가
AST 기반 Context 생성까지 넓어지며 ADR-0008이 이름을 갱신했다.

실행 진입점은 [`stage_01.py`](./stage_01.py)의 `run_stage_01()`이다.
새 구현이 아니라 기존 `hqs/development/mvp/project_intelligence.py`,
`mvp/ast_context.py`의 함수를 그대로 호출한다.

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 5개 Capability의
  Input → Analysis → Output → Validation
- [`CONTEXT.md`](./CONTEXT.md) — `run_stage_01()`이 반환하는 Context
  스키마
- [`VALIDATION.md`](./VALIDATION.md) — 검증 방법과 현재 커버리지

## 근거 문서

- `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md`
- `docs/governance/adc/ADC-0005.md`
- `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md`,
  `ADR-0008-stage-folder-code-and-docs.md`
