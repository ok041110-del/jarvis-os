# RFC-0033: Stage 01 Multi-Agent Reasoning Adoption

**Status**: Proposed → 이 세션에서 ADC-0036/ADR-0021로 이어 확정 대상
**Author**: Claude Code (사용자 명시적 요청에 따른 구현 착수 전 Governance)
**대상**: `hqs/development/stages/01_context_analysis/RESPONSIBILITY.md`·
`CONTEXT.md`, `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`
§3(Stage 01 항)의 결론, `docs/governance/adc/ADC-0003.md` 계열 Stage 01
Capability 근거(ADC-0005).

## 0. 이 RFC가 열린 이유

사용자가 "(구)Stage 01 Context Analysis를 Multi-Agent 기반으로 실제
구현"을 지시했다. 구현 착수 전 기존 문서를 검토한 결과 두 가지 기존
확정 사실과 정면으로 충돌한다.

1. `hqs/development/stages/01_context_analysis/RESPONSIBILITY.md`가
   "Engine 호출 — 5개 Capability 전부 순수 정적 분석/파일 탐색이며
   Engine을 호출하지 않는다(**결정적 Input→Output의 근거**)"를
   Stage 01의 책임 경계로 명시하고, 이를 "Kernel Architecture/Baseline
   변경 없음(**ADC-0005 Architecture Impact: NONE**)"의 근거로 삼는다.
2. `RFC-0030`(Phase F-2, Proposed) §3 Stage 01 항이 코드를 직접 재조사해
   "추가 Agent 후보: **없음**"이라고 명시적으로 결론 냈다.

사용자는 이 충돌을 인지한 상태에서 다음과 같이 처리 방향을 지시했다
(원문 요지): RFC-0030의 결론은 이후 확정된 Multi-Agent Development HQ
도입 결정과 이번 Stage 01 Multi-Agent 설계로 **superseded** 처리한다.
Stage 01의 "Engine 호출 없음" 서술은 단순 삭제/유지가 아니라, **Stage
01의 orchestration 책임**과 **Agent의 Engine 실행 책임**을 분리해
재정의한다 — Stage 01은 Multi-Agent Reasoning을 조정(orchestrate)할 수
있지만 Engine 자체의 호출·라우팅·정책을 소유하지 않으며, 실제 Agent의
LLM 실행은 기존 Engine/Engine Adapter 경계(`mvp/omniroute_engine.py`)를
그대로 따른다. Architecture/Public Contract가 실제로 바뀌는 부분에
한해서만 이 RFC→ADC→ADR을 적용하고, 그 외 Stage 01 내부 실행 구조
변경(ParallelRunner, GitHub Adapter, Code Analysis Executor 등)은 별도
Governance Gateway로 확대하지 않는다.

## 1. 판단 범위 (Scoped)

이 RFC가 다루는 것은 정확히 다음 두 가지뿐이다.

1. Stage 01에 Intent/Goal/Requirement/Ambiguity 4개 Agent(Engine 호출)를
   신규 도입하는 것이 기존 IMPLEMENTATION_RULES.md의 "구현 중 새
   Capability/Agent 추가 금지"(RFC→ADC→ADR 전환 조건: "기존 Capability로
   해결할 수 없는 작업이 반복적으로 관찰")에 해당하는가.
2. Stage 01 RESPONSIBILITY.md의 "Engine 호출 없음" 서술을 "Stage 01은
   Engine 호출·라우팅·정책을 소유하지 않는다(Agent 실행은 기존 Engine
   Adapter 경계를 따른다)"로 재정의했을 때, 이것이 Kernel Public
   Contract(Jarvis OS Architecture Baseline §14)나 Development HQ
   Baseline v1.0("Stage Data Contract")을 변경하는가.

**이 RFC가 다루지 않는 것**: ParallelRunner/GitHub Repository
Adapter/Code Analysis Executor 등 Stage 01 **내부** 실행 구조 선택.
이들은 Agent Domain/Lifecycle/State/Message/Event Contract를 새로
확정하지 않고, Registry/Scheduler/Runtime/Event Bus에 해당하지 않는
한(§4에서 확인) 내부 구현 자유 재량이다(HANDOVER.md "What Claude Code
Can Do").

## 2. Q1 — 새 Agent 4개 도입이 RFC→ADC→ADR을 요구하는가

**그렇다.** 근거:

- 선례: Requirements/Design Agent 도입은 실제로
  `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` → RFC-0008 → ADC-0006 절차를
  거쳤다(HANDOVER.md "Development HQ v2.0" 행). "새 Agent 도입"은 이
  프로젝트에서 반복적으로 RFC→ADC→ADR을 거쳐온 결정 범주다.
- `RFC-0030` §3이 Stage 01에 대해 "추가 Agent 후보 없음"을 **코드
  재조사 기반**으로 명시 확정했다 — 이를 뒤집으려면 새로운 결정
  근거(사용자의 Multi-Agent Development HQ 도입 방향)를 governance
  기록에 남겨야 그 다음 세션/감사가 "왜 RFC-0030과 다른가"를 추적할 수
  있다.
- Stage 01은 Development HQ Baseline v1.0의 Stage Data Contract(ADR-0009)
  Public Scope에 포함된 Stage다 — 그 내부에 Engine 호출 지점을 추가하는
  것은 Stage의 "성격"(결정적 Capability인지 Agent 포함 Capability인지)을
  바꾸는 것이며, ADC-0005/ADR-0008이 원래 승인한 Stage 01 형태와
  달라진다.

**결론**: 4개 Agent 도입 자체는 RFC→ADC→ADR 대상이다. 이 RFC가 그
역할을 한다(사용자가 이미 Multi-Agent Development HQ 방향을 확정했으므로
Decision Candidate가 아니라 그 방향을 Stage 01에 적용하는 **후속
확정**으로 처리한다 — HANDOVER.md ADC 채택 기준 (1) "지금 결정하지 않으면
상위 작업(Stage 01 Multi-Agent 구현)을 진행할 수 없다"를 충족).

## 3. Q2 — Kernel Public Contract / Development HQ Baseline이 변경되는가

**변경되지 않는다(Scoped).** 근거:

- Kernel Public Contract(Jarvis OS Architecture Baseline §14)는 HQ/
  Agent/Connector 수준 개념을 정의하며, "어느 Stage가 내부적으로 몇 개의
  Agent를 호출하는가"는 그 Contract가 규정하는 대상이 아니다 — Stage
  02~05가 이미 각자 1개 이상의 Agent를 호출하면서도 그때마다 Kernel
  Public Contract를 건드리지 않은 것과 동일 선례(`stages/02_.../
  RESPONSIBILITY.md` "Kernel Architecture/Baseline 변경 없음, 새
  Interface/Contract 미추가").
- Development HQ Baseline v1.0의 "Stage Data Contract(ADR-0009)"는 Stage
  **간** Handover의 5개 Contract(`ContextAnalysisResult` 등)의 필수
  키 집합만 규정한다 — Stage **내부**에서 몇 단계·몇 Agent를 거쳐 그
  키들을 채우는지는 이 Contract의 범위 밖이다(BASELINE.md "이 Contract는
  Stage 간 '무엇을 주고받는가'만 정의한다").
- Engine Adapter Contract(OmniRoute Thin Engine Caller, ADC-0031)는
  이미 "여러 Agent가 동일한 단일 함수(`call_engine_via_omniroute`)를
  통해서만 Engine을 호출한다"를 Accept 범위로 확인해 뒀다 — Stage 01의
  4개 신규 Agent도 정확히 이 동일 Adapter를 재사용하므로 Engine
  Gateway/Routing/Policy를 Jarvis 코드에 새로 두지 않는다(ADC-0031
  §Decision 그대로 적용, 확장 아님).
- Registry/Scheduler/Event Bus/Runtime — 4개 Agent를 순차 Reasoning
  단계에서 하드코딩된 함수 호출(ParallelRunner를 통한 명시적 Task
  목록)로 실행하며, Agent 동적 등록·탐색·조건부 라우팅을 도입하지
  않는다(§4에서 별도 확인).

**결론**: Kernel Public Contract·Development HQ Baseline v1.0(Stage Data
Contract 포함)·Engine Adapter Contract 어느 것도 변경되지 않는다. 이번
결정은 Development HQ **내부** 범위(Stage 01의 Responsibility 재정의 +
Agent 4개 추가)로 Scoped Accept한다.

## 4. Stage 01 신규 Responsibility 경계 (재정의안)

기존(삭제 대상 서술): "Engine 호출 — 5개 Capability 전부 순수 정적
분석/파일 탐색이며 Engine을 호출하지 않는다(결정적 Input→Output의
근거)."

신규(대체 서술): "Stage 01은 Multi-Agent Reasoning(Intent/Goal/
Requirement/Ambiguity Agent)을 orchestrate하지만, Engine 호출 자체의
routing·provider 선택·policy 판정을 소유하지 않는다 — 각 Agent의 실제
LLM 실행은 기존 Engine Adapter 경계(`mvp/omniroute_engine.py::
call_engine_via_omniroute`)를 그대로 따른다(다른 Stage의 Agent와 동일
호출 경로, ADC-0031 범위 재사용). Repository Structure/Relevant
Discovery/AST Candidate Index/Dependency Closure 4개 Code Analysis
Capability는 계속 Engine을 호출하지 않는 결정적 분석으로 유지한다 —
바뀌는 것은 Reasoning 단계 하나가 추가된 것이지, 기존 결정적
Capability의 성격이 아니다."

## 5. Non-goals

- Agent Domain/Lifecycle/State/Message/Event Contract(Phase A/B,
  ADC-0032/0033 Defer/Open)를 재정의하지 않는다 — 이 RFC의 4개 Agent는
  다른 Stage의 기존 Agent(Requirements/Design/Backend/QA)와 동일한
  "이름 붙은 함수 호출" 수준으로만 존재한다.
- Runtime/Scheduler/Event Bus/Agent Manager를 도입하지 않는다.
- GitHub Repository Adapter, ParallelRunner, Code Analysis Executor
  구조는 이 RFC의 Governance 판단 대상이 아니다(§1) — 구현 세부는
  RFC/ADC/ADR 없이 진행한다.
- ADC-02/09/10 등 Kernel 수준 Open Decision을 재론하지 않는다.

## 6. Governance Chain / Next Step

| 단계 | 내용 |
|---|---|
| 이 RFC(RFC-0033) | Q1(신규 Agent 도입 RFC 대상 여부)·Q2(Public Contract 변경 여부) 판단, Stage 01 Responsibility 재정의안 제시 |
| ADC-0036 | 이 RFC의 판단을 Decision으로 등록(Accept, Scoped) |
| ADR-0021 | Baseline 문서(Stage 01 RESPONSIBILITY.md/CONTEXT.md) 반영 확정 선언 |
| 이후 | Stage 01 Multi-Agent 실제 구현(ParallelRunner/Agent/Aggregator/GitHub Adapter/Code Analysis Executor) — 이 RFC의 Governance 판단과 별개로 자유 구현 |

## 7. Self Review

- Kernel Public Contract를 변경했는가 — **아니오**(§3).
- Development HQ Baseline v1.0(Stage Data Contract)을 변경했는가 —
  **아니오**(§3) — 5개 Stage Contract의 필수 키 집합은 무변경.
- RFC-0030의 결론을 근거 없이 뒤집었는가 — **아니오**(§0, §2) — 사용자의
  명시적 Multi-Agent Development HQ 도입 결정을 새 근거로 기록했다.
- Agent Domain/Lifecycle/State/Message/Event Contract를 새로
  확정했는가 — **아니오**(§5).
- Registry/Scheduler/Event Bus/Runtime을 도입하는 판단을 내렸는가 —
  **아니오**(§3, §5).
- 문서(RFC-0030 등) 역사적 기록을 다시 썼는가 — **아니오** — RFC-0030
  본문은 무수정, 상단에 "Superseded by RFC-0033" 포인터만 추가한다
  (ADR-0021에서 실행).
