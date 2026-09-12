# ADR-0021: Stage 01 Multi-Agent Reasoning Adoption — Baseline Reflection

**Status**: Accepted
**근거**: `RFC-0033-stage01-multi-agent-reasoning-adoption.md`,
`ADC-0036-stage01-multi-agent-reasoning-resolution.md`

## Decision

ADC-0036의 Decision을 확정하고, 다음을 이 커밋에서 함께 반영한다.

1. `hqs/development/stages/01_context_analysis/RESPONSIBILITY.md`의
   "Engine 호출 없음" 서술을 RFC-0033 §4 재정의안으로 교체한다.
2. `hqs/development/stages/01_context_analysis/CONTEXT.md`에 Multi-Agent
   Reasoning 산출물(Structured Understanding)이 내부 중간 산출물이며,
   `run_stage_01()`/Context Team 진입점이 반환하는 **Public Contract 5개
   키(`directory_structure`/`context_bundle`/`candidate_index`/`target`/
   `dependency_closure`)는 무변경**임을 명시한다.
3. `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`
   상단에 "Superseded by ADC-0036(Stage 01 항목에 한함)" 포인터를
   추가한다 — 본문은 무수정.

## 확인 사항 (Baseline 변경 범위)

- Jarvis OS Architecture Baseline(`docs/architecture/baseline/BASELINE.md`)
  — **무변경**.
- Development HQ Baseline v1.0(`hqs/development/BASELINE.md`) —
  **무변경**(Stage Data Contract 5개 Contract 필수 키 집합 그대로).
- `docs/decisions/adc/ADC.md`(Jarvis OS Open Decision 등록부) — 이 ADR이
  다루는 결정은 Development HQ 내부 Scoped 결정이라 그 등록부에 새
  Open Decision을 추가하지 않는다(ADC-0036이 이미 Accept로 종결).

## Rollback

이 결정이 이후 실제 구현·Dogfooding에서 문제(예: Stage 01의 비결정성이
후속 Stage 회귀를 유발)로 판명되면, Stage 01의 Reasoning 단계만 별도
RFC로 재검토한다 — Code Analysis 4개 Capability(결정적)는 이 ADR과
무관하게 항상 복원 가능하다(Reasoning과 Code Analysis가 §1 순서상
분리되어 있으므로).

## Next Step

Stage 01 Multi-Agent 실제 구현(ParallelRunner, Intent/Goal/Requirement/
Ambiguity Agent, Reasoning Aggregator, GitHub Repository Adapter, Code
Analysis Executor, Context Aggregator)을 진행한다 — 이 구현 자체는 이
ADR 이후 별도 Governance 승인 없이 자유 재량으로 진행한다(ADC-0036
§Out of Scope).
