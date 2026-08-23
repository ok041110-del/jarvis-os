# Stage 04: Implementation

## 요약

Stage 03(Architecture / Design)의 Design을 입력으로 받아, 실제
Production Code 변경(Stage 05가 검증할 수 있는 형태)을 만든다.
Target Identification / Implementation Planning / Code Generation /
Target File Exposure Policy / Scope Control / Existing Code
Preservation 6개 관점을 다룬다.

실행 진입점은 [`stage_04.py`](./stage_04.py)의 `run_stage_04()`이다.
새 Agent/Capability를 추가하지 않는다 — ADC-0005 §8에서 이미 배선하고
real Engine E2E로 검증한(`DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-
E2E-0001.md`, Scope 준수 3/3 누적) `workflow_ast_context.py`의
`identify_target()`/`build_dependency_closure()`/`module_source_path()`/
`_EXPOSURE_POLICY_INSTRUCTION`과, `agents.backend_agent_code_generation()`
을 그대로 재사용한다. Stage 04는 이 기존 조각들을 **Stage 03 Design**
에 연결하는 새 진입점일 뿐이다 — `workflow_ast_context.run_pipeline_
with_ast_context()`처럼 Planning/Design을 다시 만들지 않는다(Stage
02/03이 이미 만들었으므로).

## 문서 구성

- [`RESPONSIBILITY.md`](./RESPONSIBILITY.md) — 이 Stage가 책임지는 것과
  책임지지 않는 것
- [`CAPABILITIES.md`](./CAPABILITIES.md) — 3개 Capability의
  Input → Analysis → Output → Validation
- [`IMPLEMENTATION.md`](./IMPLEMENTATION.md) — `run_stage_04()`이
  반환하는 Output 스키마와 Implementation Contract
- [`VALIDATION.md`](./VALIDATION.md) — 검증 방법(mock 기반 + real
  Engine E2E, 실제 파일 적용/복원 절차 포함)과 현재 커버리지

## 근거 문서

- `hqs/development/stages/03_architecture_design/`(Stage 03 — 이
  Stage의 Input Schema 출처, `design: str`)
- `hqs/development/mvp/workflow_ast_context.py`(재사용하는 기존 구현 —
  ADC-0005 §7/§8, RFC-0007)
- `docs/research/DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-E2E-0001.md`
  (재사용 함수들의 기존 검증 Evidence)
- `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`(Stage 폴더
  구조, 신규 Capability 판단 기준 §4)
