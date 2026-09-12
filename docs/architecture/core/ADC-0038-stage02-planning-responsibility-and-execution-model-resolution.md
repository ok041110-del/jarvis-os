# ADC-0038: Stage 02 Planning Responsibility & Execution Model — Decision

## 목적

`RFC-0035-stage02-planning-responsibility-and-execution-model.md`의
4개 Decision(Task & Dependency Agent 도입, Deterministic Layer 범위,
Acceptance Criteria 현행 유지, Output Contract 확장)을 공식 Decision으로
등록한다.

## Context

두 차례 문서 조사(Stage 02 Planning 문서 설계 확정, Stage 02 LLM 호출
필요성/영향력 조사)를 거쳐, Stage 02의 목표 재정의("PRD → Task
Decomposition + Dependency + Acceptance + Implementation Planning")를
실제로 어떤 Agent/Deterministic 조합으로 만족시킬지가 좁혀졌다. 이
ADC는 그 결과를 4개의 독립된 Boundary Decision으로 확정한다.

## Decision 1 — Stage 02 Planning Boundary

**Accept.** Stage 02의 책임은 다음으로 확정한다.

- PRD/Specification 생성 **없음**(Stage 01 소관, `RFC-0034` 이미 확정).
- Task Decomposition + Dependency Judgment: **1개 신규 Agent**(Decision 2).
- Dependency Ordering + Implementation Planning: **Deterministic
  Code**(Decision 3).
- Acceptance Criteria: Stage 01 PRD의 기존 값을 그대로 통과시킴, Stage
  02가 재생성하지 않음(Decision 4는 아래 별도 항).
- Stage 03 Architecture/Design 산출, Stage 04 코드 생성, Stage 05
  검증/리뷰는 여전히 Stage 02 책임 밖(기존 경계 무변경).

## Decision 2 — Task & Dependency Agent

**Accept.** 정확히 1개의 신규 Agent를 도입한다 — Task Decomposition과
Dependency Judgment를 하나의 Engine 호출로 함께 수행하며, 별도 Task
Agent/Dependency Agent로 분리하지 않는다(RFC-0035 §1). 입력은 Stage
01의 `prd`(specification prose + skeleton)만이며, Structured
Understanding/Repository Context를 재종합하지 않는다.

## Decision 3 — Deterministic Ordering/Planning

**Accept.** Task & Dependency Agent 호출 이후 전 구간(Schema
Validation → Dependency Graph Validation → Cycle Detection →
Topological Ordering → Implementation Plan Assembly → Final
Aggregation)은 LLM 판단 없이 코드로만 처리한다(RFC-0035 §2). Cycle
Detection은 구조적 무결성만 보장하며 의미적 오판을 걸러내지 않는다는
한계를 명시적으로 인정한다(§6 재평가 조건으로 이관).

## Decision 4 — Acceptance Criteria 현행 유지

**Accept.** Acceptance Criteria에 대한 신규 Agent를 도입하지 않는다.
Stage 01 PRD Synthesis가 이미 생성한 값을 Stage 02가 그대로 유지한다
(RFC-0035 §3). 소비자가 관찰되기 전까지 구조화하지 않는다.

## Decision 5 — Output Contract

**Accept — Scoped Public Contract 변경.** `stages/contracts.py::
SpecificationResult`에 `tasks`/`dependencies`/`plan` 3개 키를
추가한다(정확한 타입은 RFC-0035 §4). `SPECIFICATION_REQUIRED_KEYS`는
5개로 갱신된다. 이는 `hqs/development/BASELINE.md` "Stage Data
Contract(ADR-0009)" 절의 "5개 Stage Contract 필수 키 집합" 변경에
해당하며, 이 ADC가 그 변경을 Accept로 확정한다 — 실제 코드 반영은
후속 작업(Non-goal, RFC-0035 §9).

## 판단 근거 요약

- 새 Agent가 몇 개 필요한가 — **1개**(Task & Dependency Agent). Agent
  수를 먼저 정하지 않고 "독립적 판단 책임 존재 여부" 기준으로 조사한
  결과 이 개수로 수렴했다(LLM 영향력 조사 §3).
- Kernel/Engine Adapter Contract가 바뀌는가 — **아니다**. 여전히 단일
  `call_engine_via_omniroute` 경로만 쓰고, 신규 Engine Gateway/Routing/
  Policy가 없다.
- Runtime/Scheduler/Workflow Parser/Dynamic Routing이 필요한가 —
  **아니다**. Task & Dependency Agent → Deterministic 체인은 하드코딩된
  순차 함수 호출로 충분하다(`IMPLEMENTATION_RULES.md` 금지 표 미해당).
- ParallelRunner 변경이 필요한가 — **아니다**. 이번 DAG에는 병렬 노드가
  없다(단일 Agent + 순차 Deterministic 체인).

## Out of Scope

- Task & Dependency Agent, Deterministic Layer의 실제 코드 구현.
- Stage 02 `RESPONSIBILITY.md`/`CAPABILITIES.md`/`SPECIFICATION.md`의
  실제 문서 반영(모순 여부 확인만 별도 수행, 반영은 후속 작업).
- Agent Domain/Lifecycle/State/Message/Event Contract 재정의.
- ADC-02/09/10 등 Kernel 수준 Open Decision.

## Next Step

`ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md`로
Baseline 문서 반영 대상, 대안·Trade-off, 재평가 조건을 최종 확정
선언한다.
