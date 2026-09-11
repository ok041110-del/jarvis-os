# RFC-0034: Stage 01 PRD/Specification Synthesis — Stage 01/02 Responsibility Rebalancing

**Status**: Proposed → 이 세션에서 ADC-0037/ADR-0022로 이어 확정 대상
**Author**: Claude Code (사용자 명시적 요청에 따른 구현 착수 전 Governance)
**대상**: `hqs/development/stages/contracts.py`(`ContextAnalysisResult`),
`hqs/development/BASELINE.md`("Stage Data Contract"), `stages/01_context_analysis/
stage_01_multi_agent.py`, `stages/02_planning_specification/stage_02.py`.

## 0. 이 RFC가 열린 이유

사용자가 Stage 01/02의 책임 경계를 다음과 같이 재정의하도록 요청했다.

```
현재: Stage 01 = Context Analysis         Stage 02 = PRD → Task/Planning
목표: Stage 01 = Context Understanding    Stage 02 = PRD → Task Decomposition
      + Repository Context                       + Dependency + Acceptance
      + PRD/Specification                         + Implementation Planning
```

기존 코드를 조사한 결과, "PRD/Specification 생성"에 해당하는 실제
Capability는 이미 존재한다 — Stage 02 Capability 2("Requirement &
Specification 생성", `stage_02.py::run_stage_02()`가
`mvp/agents/requirements.py::requirements_agent_requirement_analysis()`를
호출)가 그것이다. 이 Capability를 옮기는 것이지, 새로 만드는 것이
아니다.

## 1. 현재 구조 조사 결과

- **Stage 01 → Stage 02 Handoff Contract**(`stages/contracts.py::
  ContextAnalysisResult`)는 5개 키(`directory_structure`/`context_bundle`/
  `candidate_index`/`target`/`dependency_closure`)로 고정돼 있다
  (`hqs/development/BASELINE.md` "Stage Data Contract", **Public**).
- **Stage 02 Output Contract**(`SpecificationResult`)는 2개 키
  (`skeleton`/`specification`)이며, 이 역시 **Public**이다.
- Stage 02의 실제 구현(`stage_02.py`)은 두 Capability로 구성된다: (1)
  `_structure_from_context()` — Stage 01의 `context_bundle`에서 결정적으로
  골격(problem_definition/constraints/risks/scope_candidates)을 추출하는
  순수 함수, (2) 골격을 텍스트로 직렬화해 Issue에 붙이고
  `requirements_agent_requirement_analysis()`(Engine 1회 호출)로
  Specification 프로즈를 생성.
- Stage 03(`stage_03.py`)과 Stage 05(`stage_05.py`)는
  `stage_02_output["specification"]`을 불투명한 문자열로, `stage_02_output
  ["skeleton"]["scope_candidates"]`를 대상 판정 입력으로만 소비한다 —
  Specification이 **어떻게** 생성됐는지에는 의존하지 않는다.
- PR #176(병합 완료)으로 Stage 01은 이미 Multi-Agent Reasoning
  (Intent/Goal/Requirement/Ambiguity Agent → Structured Understanding)과
  GitHub Repository 기반 Code Analysis를 갖추고 있다 — Stage 02보다
  **더 풍부한** Context(Structured Understanding + Repository Snapshot
  기반 Discovery)를 이미 갖고 있다.

## 2. 결론 — 무엇을 옮기고 무엇을 그대로 두는가

**옮긴다**: Capability 2(Requirement & Specification 생성, Engine 1회
호출)를 Stage 01로 이동한다. 새 Agent를 만들지 않고 기존
`requirements_agent_requirement_analysis()`를 그대로 재사용한다 — 호출
위치와 입력 조립만 바뀐다(사용자 지시 #9·#10 충족: Agent 수 증가 없음).

**Synthesis로 설계한다(재추론 아님)**: PRD 생성 입력은 Stage 01이 이미
만든 Structured Understanding(Intent/Goal/Requirement/Ambiguity Agent
결과, 재추론하지 않고 그대로 직렬화)과 Repository Context(`context_bundle`/
`candidate_index`/`directory_structure`, 이미 Code Analysis가 만든 결과)를
텍스트로 합쳐 **한 번만** Engine을 호출한다 — Stage 02가 기존에 하던
골격 조립(`_structure_from_context`)과 동일한 성격의 결정적 조립 +
Engine 1회 호출 패턴을 그대로 유지한다.

**그대로 둔다**: Stage 02의 Output Contract(`SpecificationResult`, 2키)
형태는 무변경. Stage 02는 이제 자체 Engine 호출 없이 Stage 01이 생성한
PRD(`stage_01_context["prd"]`)를 그대로 `{skeleton, specification}`으로
반환한다(passthrough) — Stage 03/05는 아무 변경 없이 계속 동작한다.
Task Decomposition/Dependency/Acceptance/Implementation Planning(Stage
02의 목표 책임)은 **이번 범위에 포함하지 않는다** — 사용자 지시 §중요
"Stage 02 전체를 지금 구현하지 않는다"를 그대로 따른다. Stage 02는 PRD
생성 책임만 제거되고, 나머지는 이후 별도 작업이다.

**Dependency Analysis는 손대지 않는다** — 사용자 지시 §중요, 기존
Known Limitation(PR #176) 그대로 유지.

## 3. Public Contract 변경 여부 (사용자 지시 #11/#12)

**변경된다 — 정확히 한 곳, Scoped.**

- `ContextAnalysisResult`에 6번째 키 `prd`를 추가한다. 값 형태는
  `SpecificationResult`와 동일한 `{"skeleton": dict, "specification": str}`
  — 새 자료구조를 발명하지 않고 이미 검증된 기존 형태를 재사용한다.
- `hqs/development/BASELINE.md`의 "Stage Data Contract(ADR-0009)" 절이
  "5개 Stage Contract(...)의 필수 키 집합"을 **Public**(RFC→ADC→ADR
  필요)이라고 명시적으로 규정하므로, 이 추가는 예외 없이 이 절차
  대상이다 — 판단의 여지가 없는 명확한 경우다.
- `SpecificationResult`(Stage 02 Output)는 **변경되지 않는다** — 키
  집합·타입 모두 그대로.
- Kernel Public Contract(Jarvis OS Architecture Baseline §14)는
  영향받지 않는다 — 이 변경은 Development HQ 내부 Stage 간 Handover
  구조에 한정된다.
- Engine Adapter Contract(ADC-0031)도 영향받지 않는다 — 여전히
  `requirements_agent_requirement_analysis()` 1개 함수, 1개 Engine
  Adapter(`call_engine_via_omniroute`)만 사용한다.

## 4. Legacy 결정적 `stage_01.py`와의 관계

기존 결정적 `stage_01.py`(ADR-0021로 이미 "Multi-Agent 도입 전 형태로
보존, `mvp/tests/test_stage_01.py`가 직접 검증"으로 명시)는 **이 RFC로
변경하지 않는다** — 여전히 5키만 반환한다. Production 경로
(`teams/context/team.py::run_context_team()` → `stage_01_multi_agent.py`)만
6키(`prd` 포함)를 반환한다. `validate_context_analysis_result()`가
6키를 요구하게 되면 legacy `stage_01.py`의 출력은 그 검증기를 통과하지
못하지만, legacy 경로는 애초에 `workflow.py`에서 호출되지 않으므로(Team
경유만 Production 경로) 실제 파이프라인에 영향이 없다 — ADR-0021이 이미
legacy 경로를 "역사적 보존, Production 비경로"로 규정한 것과 일관된다.

## 5. Non-goals

- Stage 02의 Task Decomposition/Dependency/Acceptance/Implementation
  Planning 책임을 실제로 구현하지 않는다.
- Dependency Analysis(Stage 01 Code Analysis)를 재구현하지 않는다.
- LangGraph/Graphify를 도입하지 않는다.
- 새 Agent/Capability를 추가하지 않는다 — 기존
  `requirements_agent_requirement_analysis()`만 재사용한다.
- Agent Domain/Lifecycle/State/Message/Event Contract를 재정의하지
  않는다.

## 6. Governance Chain / Next Step

| 단계 | 내용 |
|---|---|
| 이 RFC(RFC-0034) | 현재 구조 조사, PRD Synthesis 설계, Contract 변경 범위 확정(`ContextAnalysisResult`에 `prd` 키 1개 추가만) |
| ADC-0037 | Decision 등록(Accept, Scoped) |
| ADR-0022 | Baseline 문서(`hqs/development/BASELINE.md`, Stage 01/02 RESPONSIBILITY/CONTEXT/SPECIFICATION.md) 반영 확정 |
| 이후 | 실제 구현 — Governance 판단과 별개로 자유 재량 |

## 7. Self Review

- Kernel Public Contract를 변경했는가 — **아니오**(§3).
- `SpecificationResult`(Stage 02 Output)를 변경했는가 — **아니오**(§2, §3).
- 새 Agent/Capability를 추가했는가 — **아니오**(§2) — 기존
  `requirements_agent_requirement_analysis()` 재사용만.
- Stage 02 전체를 구현했는가 — **아니오**(§2, §5) — PRD 생성 책임만
  제거, Task/Dependency/Acceptance/Planning은 미착수.
- Dependency Analysis를 재구현했는가 — **아니오**(§2, §5).
- LangGraph/Graphify를 도입했는가 — **아니오**(§5).
- Agent 수를 조사 전에 임의로 확정했는가 — **아니오**(§2) — 조사 결과
  기존 Agent 재사용만으로 충분함을 확인했다.
