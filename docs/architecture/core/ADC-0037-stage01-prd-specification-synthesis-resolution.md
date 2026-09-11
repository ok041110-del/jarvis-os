# ADC-0037: Stage 01 PRD/Specification Synthesis — Decision

## 목적

`RFC-0034-stage01-prd-specification-synthesis.md`의 판단(Stage 01/02
책임 재분배, `ContextAnalysisResult`에 `prd` 키 추가)을 Decision으로
확정한다.

## Context

Stage 02가 담당하던 Requirement & Specification 생성 Capability(Engine
1회 호출, `requirements_agent_requirement_analysis()` 재사용)를 Stage
01로 이동해 "Stage 01 = Context Understanding + Repository Context +
PRD/Specification, Stage 02 = PRD → Task Decomposition + Dependency +
Acceptance + Implementation Planning"으로 재정의한다. RFC-0034가 확인한
대로 이 이동은 `ContextAnalysisResult`(Stage 01 Public Contract)에
1개 키를 추가하는 것 외에는 Kernel Public Contract·Engine Adapter
Contract·`SpecificationResult`(Stage 02 Output) 어느 것도 바꾸지
않는다.

## Decision

**Accept — Scoped.**

1. `stages/contracts.py::ContextAnalysisResult`에 6번째 키 `prd`를
   추가한다. 값 형태는 기존 `SpecificationResult`와 동일하게
   `{"skeleton": {problem_definition, constraints, risks,
   scope_candidates}, "specification": str}`로 고정한다 — 새 자료구조를
   발명하지 않는다.
2. `CONTEXT_ANALYSIS_REQUIRED_KEYS`에 `"prd"`를 추가하고
   `validate_context_analysis_result()`가 이를 검증하게 한다.
3. `stage_01_multi_agent.py`에 PRD Synthesis 단계를 추가한다 — Structured
   Understanding(Reasoning Aggregator 결과, 재추론 없이 직렬화)과
   Repository Context(Code Analysis 결과인 `context_bundle`/
   `candidate_index`/`directory_structure`)를 결합해 기존
   `requirements_agent_requirement_analysis()`를 **정확히 1회** 호출한다
   — 새 Agent를 만들지 않는다.
4. `stage_02.py::run_stage_02()`는 자체 Engine 호출과 골격 재계산을
   제거하고, `stage_01_context["prd"]`를 그대로 `{skeleton,
   specification}`으로 반환한다(passthrough). `SpecificationResult`의
   키/타입은 무변경 — Stage 03/05 소비 코드는 무수정.
5. Legacy 결정적 `stage_01.py`(ADR-0021 보존 대상)는 무변경 — 계속 5키만
   반환하며, Production 경로(`teams/context/team.py`)에서 호출되지
   않으므로 6키 요구 Contract 검증과 무관하다.
6. Kernel Public Contract(Jarvis OS Architecture Baseline §14), Engine
   Adapter Contract(ADC-0031)는 **무변경**.
7. Stage 02의 Task Decomposition/Dependency/Acceptance/Implementation
   Planning 책임은 이 ADC의 판단 대상이 아니다 — 이번 반복에서
   구현하지 않는다.

## 판단 근거 요약 (RFC-0034 인용)

- 새 Capability/Agent가 필요한가 — **아니다**, 기존
  `requirements_agent_requirement_analysis()`를 호출 위치만 옮겨
  재사용한다.
- Kernel/Engine Adapter Contract가 바뀌는가 — **아니다**, Development HQ
  내부 Stage Handover 구조에 한정된 변경이다.
- `SpecificationResult`가 바뀌는가 — **아니다**, Stage 02는 passthrough로
  동일 Output Contract를 유지한다.

## Out of Scope

- Stage 02 Task/Dependency/Acceptance/Planning 실제 구현.
- Stage 01 Dependency Analysis 재구현.
- LangGraph/Graphify 도입.
- Agent Domain/Lifecycle/State/Message/Event Contract 재정의.

## Next Step

`ADR-0022-stage01-prd-specification-synthesis-baseline.md`로 Baseline
문서(`hqs/development/BASELINE.md`, Stage 01/02 RESPONSIBILITY/CONTEXT/
SPECIFICATION.md) 반영을 확정 선언한다.
