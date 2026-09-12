# ADR-0022: Stage 01 PRD/Specification Synthesis — Baseline Reflection

**Status**: Accepted
**근거**: `RFC-0034-stage01-prd-specification-synthesis.md`,
`ADC-0037-stage01-prd-specification-synthesis-resolution.md`

## Decision

ADC-0037의 Decision을 확정하고, 다음을 이 커밋에서 함께 반영한다.

1. `hqs/development/BASELINE.md`의 "Stage Data Contract(ADR-0009)" 절 —
   `ContextAnalysisResult`의 Public 필수 키 집합에 `prd`를 추가해 6개로
   갱신한다.
2. `hqs/development/stages/01_context_analysis/CONTEXT.md` — `prd` 키를
   Stage 01 Output 표에 추가하고, PRD/Specification 생성이 Stage 01의
   책임으로 이동했음을 명시한다.
3. `hqs/development/stages/01_context_analysis/RESPONSIBILITY.md` —
   "책임진다" 목록에 "PRD/Specification 생성(Requirement & Specification
   Capability 재사용)"을 추가한다.
4. `hqs/development/stages/02_planning_specification/RESPONSIBILITY.md`/
   `SPECIFICATION.md`/`CAPABILITIES.md` — PRD/Specification 생성 책임이
   Stage 01로 이동했고, Stage 02는 이제 Stage 01의 `prd`를 그대로
   전달(passthrough)함을 명시한다. Task Decomposition/Dependency/
   Acceptance/Implementation Planning으로의 책임 확장은 이 ADR이
   결정하지 않는다(별도 후속 작업).

## 확인 사항 (Baseline 변경 범위)

- Jarvis OS Architecture Baseline(`docs/architecture/baseline/BASELINE.md`)
  — **무변경**.
- Development HQ Baseline v1.0(`hqs/development/BASELINE.md`) — Stage
  Data Contract 절의 `ContextAnalysisResult` 필수 키 집합만 갱신(5→6개,
  `prd` 추가). `SpecificationResult`는 **무변경**.
- `docs/decisions/adc/ADC.md`(Jarvis OS Open Decision 등록부) — 이 결정은
  Development HQ 내부 Scoped 결정이라 새 Open Decision을 추가하지
  않는다(ADC-0037이 이미 Accept로 종결).

## Rollback

Stage 01의 PRD Synthesis가 이후 실제 Dogfooding에서 문제(예: Stage 01이
지나치게 무거워지거나 실패율이 올라감)로 판명되면, `prd` 키와 그 생성
로직만 별도 RFC로 되돌릴 수 있다 — Stage 02의 passthrough 로직은 원래의
직접 생성 로직으로 되돌리는 것으로 복원 가능하며(git 이력 보존), Stage
03/05의 소비 코드는 이 Rollback으로 영향받지 않는다(`SpecificationResult`
Output Contract가 그대로이므로).

## Next Step

Stage 01 PRD Synthesis 실제 구현(`stage_01_multi_agent.py` 확장) 및
Stage 02 passthrough 전환을 진행한다 — 이 ADR 이후 별도 Governance
승인 없이 자유 재량으로 진행한다(ADC-0037 §Out of Scope).
