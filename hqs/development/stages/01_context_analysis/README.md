# Stage 01: Context Analysis

## 요약

Repository·문서·코드 구조·AST·Dependency를 분석해 후속 Stage(02 이하)가
쓸 Context를 생성한다. 구 명칭 "Repository Intelligence"(ADR-0001 §4)를
AST Context 추가에 맞춰 ADR-0008이 개명했다.

진입점: [`stage_01.py`](./stage_01.py)의 `run_stage_01()` — 신규
구현 없이 기존 `mvp/project_intelligence.py`, `mvp/ast_context.py`
함수만 호출한다.

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
