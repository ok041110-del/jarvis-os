# ADC-0036: Stage 01 Multi-Agent Reasoning — Decision

## 목적

`RFC-0033-stage01-multi-agent-reasoning-adoption.md`의 두 판단(Q1: 신규
Agent 4개 도입의 Governance 대상 여부, Q2: Kernel Public Contract/
Development HQ Baseline 변경 여부)을 Decision으로 확정한다.

## Context

Stage 01은 지금까지 Engine을 호출하지 않는 5개 결정적 Capability로만
구성되어 있었다(`RESPONSIBILITY.md`, `ADC-0005` Architecture Impact:
NONE 근거). 사용자가 Stage 01을 Multi-Agent Reasoning(Intent/Goal/
Requirement/Ambiguity Agent) 기반으로 전환하도록 명시적으로 지시했고,
이는 `RFC-0030`(Phase F-2)의 "Stage 01엔 Agent 후보 없음" 결론과
`RESPONSIBILITY.md`의 "Engine 호출 없음" 서술 둘 다와 충돌한다.

## Decision

**Accept — Scoped.**

1. Stage 01에 Intent/Goal/Requirement/Ambiguity 4개 Agent를 신규
   도입한다. 각 Agent는 다른 Stage의 기존 Agent와 동일하게
   `mvp/omniroute_engine.py::call_engine_via_omniroute`만을 통해 Engine을
   호출한다 — 새 Engine Gateway/Routing/Policy를 두지 않는다(ADC-0031
   범위 재사용, 확장 아님).
2. `RFC-0030` §3 Stage 01 항의 "추가 Agent 후보 없음" 결론은 이 ADC로
   **superseded**된다. RFC-0030 본문은 수정하지 않고, 문서 상단에
   "Superseded by ADC-0036" 포인터만 추가한다(역사적 기록 보존,
   CLAUDE.md "Code Documentation" 원칙과 무관 — 이건 문서 Governance
   원칙).
3. Stage 01 RESPONSIBILITY.md의 "Engine 호출 없음" 서술을 RFC-0033 §4
   재정의안으로 교체한다: Stage 01은 Multi-Agent Reasoning을
   orchestrate하지만 Engine 호출의 routing·provider 선택·policy 판정을
   소유하지 않는다 — 그 실행은 기존 Engine Adapter 경계를 그대로
   따른다. 4개 결정적 Code Analysis Capability(Structure/Discovery/AST
   Candidate/Dependency Closure)는 Engine을 호출하지 않는 성격을
   그대로 유지한다.
4. Kernel Public Contract(Jarvis OS Architecture Baseline §14),
   Development HQ Baseline v1.0의 Stage Data Contract(ADR-0009,
   `ContextAnalysisResult` 등 5개 Contract 필수 키 집합)는 **무변경**
   — 이 Accept는 Development HQ 내부(Stage 01 Responsibility + Agent
   구성)로 Scoped된다.
5. ParallelRunner/GitHub Repository Adapter/Code Analysis Executor 등
   Stage 01 **내부** 실행 구조는 이 ADC의 판단 대상이 아니다 — Registry/
   Scheduler/Event Bus/Runtime에 해당하지 않는 한(구현 시점에 매
   결정마다 재확인) 자유 구현 재량이다.

## 판단 근거 요약 (RFC-0033 인용)

- Q1(신규 Agent 4개 → RFC→ADC→ADR 대상인가): **그렇다** — 선례
  (Requirements/Design Agent가 RFC-0008→ADC-0006을 거쳤음), RFC-0030의
  명시적 반대 결론 존재, Stage Data Contract Public Scope 소속 Stage의
  성격 변경.
- Q2(Kernel/Baseline 변경되는가): **아니다** — Kernel Public Contract는
  Stage 내부 Agent 개수를 규정하지 않음, Stage Data Contract는 Stage
  간 Handover 키 집합만 규정, Engine Adapter Contract는 이미 다중 Agent
  재사용을 Accept해 둠(ADC-0031), Registry/Scheduler/Event Bus/Runtime
  도입 없음.

## Out of Scope

- Agent Domain/Lifecycle/State/Message/Event Contract(ADC-0032/0033)
  재정의 — 이 4개 Agent는 이름 붙은 함수 호출 수준으로만 존재.
- ADC-02/09/10 등 Kernel 수준 Open Decision.
- Stage 01 내부 실행 구조 상세 설계(ParallelRunner 등) — 구현 재량.

## Next Step

`ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md`로 Baseline
문서(`RESPONSIBILITY.md`/`CONTEXT.md`) 반영을 확정 선언한다.
