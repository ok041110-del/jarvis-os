# ADC-0036 — Stage 01 Multi-Agent Reasoning Decision

> `RFC-0033-stage01-multi-agent-reasoning-adoption.md`의 두 질문(Q1: 신규 Agent
> 4개 도입의 Governance 대상 여부, Q2: Kernel Public Contract/Development HQ
> Baseline 변경 여부)을 Decision으로 확정한다.

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | ADC-0036 |
| Status | Resolved (Accept — Scoped) |
| Owner / Scope | Development HQ Stage 01 내부(Agent 구성) |
| Context | Stage 01은 지금까지 Engine을 호출하지 않는 5개 결정적 Capability로만 구성됐다(RESPONSIBILITY.md, ADC-0005 Architecture Impact: NONE). 사용자가 Stage 01을 Multi-Agent Reasoning(Intent/Goal/Requirement/Ambiguity Agent) 기반으로 전환하도록 지시했고, 이는 RFC-0030(Phase F-2) "Stage 01엔 Agent 후보 없음" 결론 및 RESPONSIBILITY.md "Engine 호출 없음" 서술과 충돌한다 |

## 2. Decision Scope & Context

| Item | Description |
|---|---|
| Decision Scope | Stage 01에 Intent/Goal/Requirement/Ambiguity 4개 Agent 신규 도입 여부, Kernel/Baseline 변경 여부 |
| Constraints | 새 Engine Gateway/Routing/Policy를 두지 않는다(ADC-0031 범위 재사용) |
| Non-Goals | Agent Domain/Lifecycle/State/Message/Event Contract(ADC-0032/0033) 재정의, ADC-02/09/10 등 Kernel 수준 Open Decision, Stage 01 내부 실행 구조 상세 설계(ParallelRunner 등 — 구현 재량) |

## 3. Candidates / Options

| ID | Candidate | Description | Evidence | Advantages | Risks / Trade-offs |
|---|---|---|---|---|---|
| C-1 | Accept — Scoped(채택) | Intent/Goal/Requirement/Ambiguity 4개 Agent를 `mvp/omniroute_engine.py::call_engine_via_omniroute`만으로 호출하도록 도입 | 선례: Requirements/Design Agent가 RFC-0008→ADC-0006을 거침 | 기존 Engine Adapter 경계 재사용, Kernel/Baseline 무변경 | RFC-0030의 기존 결론을 Supersede해야 함(§4) |

## 4. Evaluation

| Criterion | Weight / Priority | C-1 | Notes |
|---|---|---|---|
| Q1 — 신규 Agent 4개가 RFC→ADC→ADR 대상인가 | 필수 | 그렇다 | 선례(RFC-0008→ADC-0006), RFC-0030의 명시적 반대 결론 존재, Stage Data Contract Public Scope 소속 Stage의 성격 변경 |
| Q2 — Kernel/Baseline이 변경되는가 | 필수 | 아니다 | Kernel Public Contract는 Stage 내부 Agent 개수를 규정하지 않음. Stage Data Contract는 Stage 간 Handover 키 집합만 규정. Engine Adapter Contract는 이미 다중 Agent 재사용을 Accept(ADC-0031). Registry/Scheduler/Event Bus/Runtime 도입 없음 |

## 5. Recommendation & Decision Boundary

| Item | Description |
|---|---|
| Recommendation / Decision | Accept — Scoped. Stage 01에 4개 Agent 신규 도입 |
| Decision Boundary | Kernel Public Contract(BASELINE §14), Development HQ Stage Data Contract(ADR-0009, `ContextAnalysisResult` 등 5개 필수 키 집합)는 무변경 — 이 Accept는 Development HQ 내부(Stage 01 Responsibility + Agent 구성)로 Scoped된다 |
| Out of Authority | ParallelRunner/GitHub Repository Adapter/Code Analysis Executor 등 Stage 01 내부 실행 구조는 이 ADC의 판단 대상이 아니다 — Registry/Scheduler/Event Bus/Runtime에 해당하지 않는 한 자유 구현 재량 |
| ADR Requirement | `ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md`가 Baseline 문서(RESPONSIBILITY.md/CONTEXT.md) 반영을 확정 선언한다 |

## 6. Open Questions

이 ADC 단계에서 남는 Open Question은 없다 — Q1/Q2 모두 위 §4에서 확정했다.

## Decision 세부 내용

1. Stage 01에 Intent/Goal/Requirement/Ambiguity 4개 Agent를 신규 도입한다. 각 Agent는 다른 Stage의 기존 Agent와 동일하게 `call_engine_via_omniroute`만을 통해 Engine을 호출한다.
2. RFC-0030 §3 Stage 01 항의 "추가 Agent 후보 없음" 결론은 이 ADC로 **superseded**된다. RFC-0030 본문은 수정하지 않고 상단에 "Superseded by ADC-0036" 포인터만 추가한다(역사적 기록 보존).
3. Stage 01 RESPONSIBILITY.md의 "Engine 호출 없음" 서술을 RFC-0033 §4 재정의안으로 교체한다: Stage 01은 Multi-Agent Reasoning을 orchestrate하지만 Engine 호출의 routing·provider 선택·policy 판정을 소유하지 않는다. 4개 결정적 Code Analysis Capability(Structure/Discovery/AST Candidate/Dependency Closure)는 Engine을 호출하지 않는 성격을 유지한다.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/architecture/core/RFC-0033-stage01-multi-agent-reasoning-adoption.md` | 이 ADC가 판단하는 Q1/Q2의 출처 |
| RFC | `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md` | §3 결론이 이 ADC로 Superseded |
| ADC | `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md` | Engine 호출 경로 재사용 근거 |
| ADR | `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md` | Next Step — Baseline 반영 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | RFC-0033 Q1/Q2 판단 |
