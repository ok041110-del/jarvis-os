# Team 01~05 — Architecture Design vs Actual Implementation Gap Analysis

## Summary

- **핵심 발견(이 문서 전체를 지배하는 사실)**: Team 01~05 각각을 그
  Team의 **실제 governing RFC/ADC/ADR**과 대조한 결과, **5개 Team
  전부 현재 코드가 "그 Team에 대해 실제로 Accepted된 Architecture"와
  일치한다.** 겉보기 "Gap"(Team02/03/04가 단일 Agent, Team05가 순차
  실행)은 구현 미비가 아니라 **Governance가 애초에 더 많은 것을
  요구하지 않았거나(Team02/03), 더 많은 것을 명시적으로 거부했거나
  (Team02 2-Agent 분리), 더 많은 것을 아직 NOT DETERMINED로
  유보했기 때문(Team04/05)**이다.
- 따라서 이번 조사의 결론은 "Architecture대로 만들려면 얼마나 더
  구현해야 하는가"가 아니라 **"지금 이미 구현된 것이 Architecture와
  정확히 일치하며, 그 이상(Team04 3-Agent Ponytail, Team05 6-way
  Parallel DAG)은 구현 대상이 아니라 별도 Governance 결정 대상"**
  이라는 것이다.
- Team01만 예외적으로 **Accepted 최소 요구치(4-Agent + Engine 호출
  정합성, L2 상당)를 실제로는 초과 달성**했다(실제 ThreadPoolExecutor
  병렬 + 실제 Aggregator, L3) — 이는 RFC-0033/ADC-0036이 스케줄링/
  집계 로직을 "자유 구현 재량"으로 명시적으로 위임했기 때문에 가능한,
  **허용된 초과 달성**이지 Architecture 위반이나 우연이 아니다.
- OpenRouter Migration은 5개 Team 전부 동일한 단일 Adapter
  (`openrouter_engine.py`)를 통과하므로 Team별 차이가 구조적으로
  없다 — Migration Gap은 전체적으로 작다(이미 완료, 남은 것은
  `ADR-0027` §9 Validation Gate 실측뿐이며 이는 이번 조사 범위 밖).
- **Production 코드/RFC/ADC/ADR 어느 것도 이 조사에서 수정하지
  않았다.** Validation Gate를 실행하거나 판정하지 않았다. 실제
  OpenRouter API 호출을 하지 않았다.

---

## 1. 현재 구조 조사(코드 기준, 이전 리뷰 재확인 + 이번 조사로 보강)

| 항목 | Team 01 | Team 02 | Team 03 | Team 04 | Team 05 |
|---|---|---|---|---|---|
| Entrypoint | `teams/context/team.py::run_context_team()` | `teams/planning/team.py::run_planning_team()` | `teams/architecture/team.py::run_architecture_team()` | `teams/implementation/team.py::run_implementation_team()` | `teams/validation/team.py::run_validation_team()` |
| Orchestration | importlib 동적 로드 → `stage_01_multi_agent.run_stage_01_multi_agent()` | importlib → `stage_02.run_stage_02()` | importlib → `stage_03.run_stage_03()` | importlib → `stage_04.run_stage_04()` | importlib → `stage_05.run_stage_05()` |
| Agent | intent/goal/requirement/ambiguity(reasoning.py) + PRD synthesis(requirements.py 재사용) | Task & Dependency Agent 1개(`task_dependency_agent.py`) | Design Agent 1개(`design.py`) | Backend Agent code_generation 1개(`backend.py`) | Backend Agent code_review 1개(`backend.py`) + 4개 결정적 검사 |
| Capability | reasoning 4종 + requirement_analysis | task_decomposition_and_dependency | design | code_generation | code_review |
| Engine | OpenRouter(전부 3번째 Engine으로 Migration 완료) | OpenRouter | OpenRouter | OpenRouter | OpenRouter |
| OpenRouter | `openrouter_engine.py` 경유 확인(§8) | 〃 | 〃 | 〃 | 〃 |
| Dependency | Stage 01 자체 완결 | Stage01 Output 의존 | Stage01+02 Output 의존 | Stage01+03 Output 의존 | Stage02+04 Output 의존 |
| Output | `ContextAnalysisResult`(6키, PRD 포함) | `tasks`/`dependencies`/`plan` | Design prose(6섹션) | Implementation code + Exposure sentinel | Verdict + check_results + code_review(advisory) |
| Validation | Aggregator 내부(`aggregate_reasoning`/`aggregate_context`) | `planning_pipeline.py`(스키마/사이클/위상정렬) | 없음(단일 생산자) | 없음(Stage05가 사후 검증) | `_build_check_results`/`_determine_verdict`(4개 결정적 검사만) |
| Tests | `test_stage01_reasoning.py` 등 6개 | `test_task_dependency_agent.py`/`test_planning_pipeline.py`/`test_stage_02.py` | `test_stage_03.py` | `test_stage_04.py`(9개) | `test_stage_05.py`(37개 함수) |
| Parallel execution | **실제**(ThreadPoolExecutor via `ParallelRunner`) | 없음 | 없음 | 없음(실험 harness만 존재, 미배선) | 없음(실험 harness만 존재, 미배선) |
| Aggregation | 실제(충돌 탐지/중복 제거/신뢰도 평균) | 결정적 파이프라인(Agent 집계 아님) | 없음 | 없음 | 단순(4개 결정적 검사만 병합, Review는 advisory) |

## 2. Architecture Expected State(governing 문서에서 추출, 문서 원문 근거)

### Team 01 — RFC-0033/ADC-0036/ADR-0021(Accepted) + RFC-0034/ADC-0037/ADR-0022(Accepted)

- **확정된 것**: Intent/Goal/Requirement/Ambiguity 4개 Agent 신규 도입,
  각각 기존 Engine Adapter로만 호출(ADC-0036 §Decision). PRD Synthesis는
  기존 `requirements_agent_requirement_analysis`를 새 Agent 없이
  재사용(ADC-0037 §Decision 3).
- **명시적으로 "자유 재량"으로 남긴 것**: "ParallelRunner"와 "Reasoning
  Aggregator"는 **이름만 지정**됐을 뿐, 실제 병렬 실행 여부·충돌/중복
  처리 로직은 ADR-0021 Next Step이 "이 ADR 이후 별도 Governance
  승인 없이 자유 재량으로 진행한다"고 명시 — 즉 **L2(4-Agent, 순차
  라도 무방)가 최소 승인 요구치이고, L3(실제 병렬+실제 Aggregator)는
  구현자가 재량으로 선택한 초과 달성**이다.

### Team 02 — RFC-0035/ADC-0038/ADR-0023(Accepted)

- **확정된 것(원문)**: "Stage 02에 **정확히 1개**의 신규 Agent(Task &
  Dependency Agent)를 도입한다... **호출 횟수: 정확히 1회**... 별도
  Task Agent와 별도 Dependency Agent로 분리하지 **않는다**."
- **명시적으로 거부(Rejected)된 것**: 2-Agent 분리안 — "이미 기각했다"
  (Multi-Engine 호출 회피, 재추론 위험 회피가 사유).
  ParallelRunner 변경 불필요 — "이번 DAG에는 병렬 노드가 없다(단일
  Task 실행이므로)."
- **결론**: Team02의 Architecture Target은 **L1(단일 Agent + 결정적
  파이프라인)이며, 현재 구현이 정확히 그 Target이다.** Multi-Agent화는
  Architecture 위반이 된다(명시적 Rejected 대안을 재도입하는 것).

### Team 03 — 전용 RFC/ADC/ADR 없음

- `docs/architecture/core/`에 "stage03"/"stage_03" 전용 문서 0건.
  유일하게 존재하는 `RFC-0030`(Dev HQ Stage-Agent-Team Boundary
  Analysis)은 **Status: Proposed(분석 결과 기록, Baseline 결정
  아님)**이며, 그 §3 Stage 03 항목은 "추가 Agent 후보 | 없음",
  §7은 "Stage 02·03은 각각 Agent가 1개뿐이라 'Multi-'라는 전제
  자체가 성립하지 않는다"고 명시한다. 이 결론은 이후 어떤 문서로도
  뒤집히거나 재론되지 않았다(Team01/05는 후속 RFC로 재론됐지만
  Team03은 아님).
- **결론**: Team03의 Architecture Target은 **단일 Design Agent이며,
  현재 구현이 정확히 그 Target이다.** 사용자 지시가 나열한 "Design
  Skeleton/Architecture Definition/.../Implementation Strategy"는
  **별도 Agent들이 아니라, 그 단일 Design Agent가 생성하는 prose
  응답 안의 6개 내용 섹션**이며(`stage_03.py::_DESIGN_INSTRUCTION`
  이 그대로 지시), 이미 충족되어 있다(`test_stage_03.py`가 검증).

### Team 04 — RFC-0037/ADC-0040(Accepted 아님, NOT DETERMINED). **ADR 없음.**

- 제안된 3-Agent(고정 ID `implementation`/`consistency`/`minimality`)
  + "Ponytail"(현재 실험 구현은 "실제 LLM 판단이 전혀 없는 고정 ID
  순서 선택기"이며, RFC-0037 자신이 "이것은 실제 Ponytail Supervisor가
  아니다"라고 명시) + Deterministic Gate(`deterministic_checks.py`,
  syntax/AST/contract/scope/design-coverage/dependency-validity/
  comment-docstring 7종 검사) — 전부 `stages/04_implementation/
  architecture_validation/`(실험 harness)에만 존재, `stage_04.py`/
  `team.py`는 이를 import하지 않음(재확인).
- 실행 방식: RFC-0037 자신이 "`_generate_and_gate_candidates`가
  순차 for-loop로 실행 — 실제 병렬 실행은 구현되어 있지 않다"고
  명시. 병렬화 자체는 "구조적으로 가능"하나 미구현이며, 시도하려면
  `ADC-0015`(Execution Host: Process 1차, Thread 금지) 범위를 따라야
  한다.
- **ADC-0040 Decision(원문)**: "**NOT DETERMINED — Real Engine
  Evidence Required.** `ADOPT`/`KEEP`/`REJECT` 어느 것도 이번 세션에서
  근거를 갖추지 못했다." **ADR 자체가 작성되지 않았다** — 이 저장소의
  Governance 관례상(모든 기존 ADR은 Accepted 계열뿐, Proposed/NOT
  DETERMINED ADR 선례 없음) ADR 부재는 **Production 권한 없음**을
  뜻한다.
- **결론**: Team04의 **유일하게 승인된 Production 상태는 Case A
  (현재 단일 Agent)다.** 3-Agent + Ponytail 구조는 Architecture가
  "아직 요구하지 않는" 정도가 아니라 **명시적으로 NOT DETERMINED —
  지금 구현하면 Governance를 앞지르는 것**이다.

### Team 05 — RFC-0038/ADC-0041(NOT DETERMINED) + RFC-0039/ADC-0042(PARTIAL)/ADR-0025(Accepted, Scoped)

- **ADR-0025가 실제로 Accept한 것**(재론 없이 인용 가능): 6개
  책임(Structure/Scope/AST/Dependency/Test/Review)의 독립성 표
  (Structure/Scope/Dependency=A, AST/Review=A*[Context 선-스냅샷
  조건부], Test=B[Isolation 필요]), Test Isolation 메커니즘(`.git`
  제외 전체 working-tree 복사, Worktree/Container 불필요로 이미
  실측 기각), Aggregator의 5단계 경계, Failure Isolation Policy,
  Review의 **advisory 경계**("Review는 항상 advisory다 — Aggregator의
  Verdict 계산에 참여하지 않는다").
- **ADR-0025가 명시적으로 유보한 것**: §11 Parallel Production
  Adoption — **NOT YET DETERMINED**(실측 결과 오히려 "Parallel이
  Single보다 명확히 빠르다는 근거는 나타나지 않았다"). §10 LLM Review
  Adoption — **NOT YET DETERMINED**(LLM을 실제로 호출한 적 없음).
  §13 Consequences가 직접 경고: "이 ADR을 'Stage 05가 병렬로
  전환됐다'는 근거로 인용해서는 안 된다."
- RFC-0038/ADC-0041(QA Agent를 Stage05에 활성화하는 별개 축)도 **NOT
  DETERMINED** — 현재 `qa_agent_test_execution(code, review)` 시그니처
  자체가 Code Review 출력에 순차 의존적이라, Stage04 3-Agent처럼
  독립적이지 않다는 점까지 이미 문서화됨.
- **결론**: Team05의 **유일하게 승인된 Production 상태는 현재
  순차 구조(4개 결정적 검사 + Code Review, Verdict는 Review 결과에
  영향받지 않음)다.** 6-way Parallel DAG, Test Workspace 실제 배선,
  LLM Review 실제 배선 — 전부 **NOT YET DETERMINED, Governance
  Blocked**다.

---

## 3. TEAM-BY-TEAM GAP MATRIX

| Team | Architecture Requirement | Current Implementation | Gap | Priority | Estimated Work |
|---|---|---|---|---|---|
| 01 | 4-Agent(intent/goal/requirement/ambiguity) + PRD 재사용, 호출 정합성만 확정(스케줄링/집계는 자유 재량) | 4-Agent 전부 구현 + 실제 ThreadPoolExecutor 병렬 + 실제 Aggregator(초과 달성) | **Already Implemented**(요구치 충족, 초과분은 허용된 재량) | N/A | 없음 |
| 02 | 정확히 1-Agent + 결정적 파이프라인, 2-Agent 분리 명시적 Rejected, 병렬 노드 없음이 확정 | 1-Agent + `planning_pipeline.py`(스키마/사이클/위상정렬) | **Already Implemented** | N/A | 없음 |
| 03 | 전용 문서 없음, 유일한 분석(RFC-0030, Proposed)이 "추가 Agent 후보 없음"으로 결론, 단일 Agent가 6개 내용 섹션을 prose로 생성 | 단일 Design Agent, 6개 섹션 전부 프롬프트에 포함(`_DESIGN_INSTRUCTION`), Contract 테스트로 검증됨 | **Already Implemented** | N/A | 없음 |
| 04 | (제안만 존재, NOT DETERMINED) 3-Agent(implementation/consistency/minimality) + Deterministic Gate + Ponytail(고정 ID tie-break) — **ADR 부재로 Production 미승인** | 단일 Agent(code_generation), 실험 harness는 별도 존재하나 미배선 | **N/A(구현 대상 아님)** — Governance가 아직 승인하지 않음 | **N/A** | 해당 없음(승인 시까지) |
| 05 | (일부만 Accepted) 독립성 표/Isolation 메커니즘/Aggregator 5단계/Failure Isolation/Review advisory 경계는 Accepted, **6-way Parallel 실배선·LLM Review 실배선은 NOT YET DETERMINED** | 4개 결정적 검사 + 1 LLM Review, 순차 실행, 원본 파일 mutate+restore(Isolation 없음) | Structural facts: **Already Implemented(문서화 수준)**. Production 배선: **N/A(구현 대상 아님)** | Structural facts=N/A(이미 문서화 완료). 배선=**N/A**(Governance 미승인) | 해당 없음(승인 시까지) |

**Missing/Partial/Incorrect/Already Implemented 판정**: 5개 Team 모두
"Already Implemented"(현재 승인된 Architecture 기준) 또는 "N/A"(아직
승인되지 않아 구현 대상 자체가 아님) 중 하나이며, **"Missing"·
"Partial"·"Incorrect"로 분류되는 항목은 이번 조사에서 발견되지
않았다.**

## 4. MVP vs FINAL ARCHITECTURE — Current vs Target Level

```
Team 01
Current: L3
Target(최소 승인 요구치): L2   Target(허용된 재량 상한): L3
Gap: 없음 — 오히려 최소 요구치를 초과 달성(허용된 재량 범위 안)

Team 02
Current: L1
Target: L1(2-Agent 분리는 명시적으로 Rejected)
Gap: 없음

Team 03
Current: L0/L1(단일 Agent, Team 래퍼)
Target: L0/L1(전용 문서 없음, RFC-0030이 "Multi- 전제 성립 안 함"으로 결론)
Gap: 없음

Team 04
Current: L0
Target: 공식적으로는 L0(Case A만 승인) — L2/L3 상당의 3-Agent+Ponytail은 **NOT DETERMINED**(ADR 없음)
Gap: "구현 격차"가 아니라 "Governance 미결정" — 구현 대상 아님

Team 05
Current: L2
Target: 공식적으로는 L2(현재 순차 구조만 승인) — L3 상당의 6-way Parallel DAG는 **NOT YET DETERMINED**(ADR-0025 §11/§13)
Gap: "구현 격차"가 아니라 "Governance 미결정" — 구현 대상 아님
```

**중요**: 사용자 지시("Architecture 문서가 실제로 요구하지 않는
Multi-Agent화를 임의로 추가하지 않는다")를 그대로 지켜, Team02/03을
Multi-Agent로 "끌어올려야 할 대상"으로 취급하지 않았다. Team04/05도
"미완성"이 아니라 "아직 승인되지 않음"으로 정확히 구분했다.

## 5. PARALLELIZATION GAP

| Team | 병렬화 가능한 작업 | 현재 실행 방식 | 목표 실행 방식(승인 기준) | dependency로 병렬 불가한 작업 | 병렬화 필요 이유 | 병렬화 효과 | 불필요한 병렬화인가 |
|---|---|---|---|---|---|---|---|
| 01 | 4개 reasoning agent, 3개 code-analysis 유닛 | **이미 실제 병렬**(ThreadPoolExecutor) | 동일(이미 목표 달성) | Reasoning 완료 후 Code Analysis 시작(phase 간 순차는 의도된 것, `test_reasoning_fully_completes_before_code_analysis_starts`로 확정) | 이미 구현됨 — 해당 없음 | 이미 실측 가능(단, 이번 조사는 재실측하지 않음) | 아니오(승인된 재량 범위) |
| 02 | 없음(Agent 1개뿐) | 순차 | 순차(승인된 최종 상태) | Task/Dependency가 원래 한 판단이라 분리 자체가 Rejected | 해당 없음 | 해당 없음 | **그 자체로 불필요**(RFC-0035가 이미 이렇게 결론) |
| 03 | 없음(Agent 1개뿐) | 순차 | 순차 | 단일 Design 판단을 여러 Agent로 쪼갤 근거가 문서에 없음 | 해당 없음 | 해당 없음 | **불필요** |
| 04 | 3개 Code Agent(implementation/consistency/minimality) — **구조적으로 독립**(RFC-0037 §2 Q1) | 순차(실험 harness 기준), Production은 1개뿐 | **미결정**(ADC-0040이 판정 보류) | 없음(3개는 서로 데이터 의존 없음) | 병렬화하면 latency 절감 **가능성**(미실측) | **미실측**(ADC-0040 §Validation Requirements가 실측 요구) | 판단 불가 — 실측 전에는 "필요/불필요" 자체를 결정할 근거가 없음 |
| 05 | Structure/Scope/AST/Dependency/Review(5개, A 등급) | 순차 | **미결정**(ADR-0025 §11), 실측 결과는 오히려 회의적(§11 인용: "Parallel이 Single보다 명확히 빠르다는 근거는 나타나지 않았다") | Test(B 등급, 파일 mutation) — 반드시 Isolation 필요 | latency 단축 가설이었으나 실측이 이를 뒷받침하지 않음 | ADR-0025 §11이 이미 "이득 없음"을 실측으로 확인 | **이미 한 번 실측했고 이득이 안 보임** — 추가 근거 없이 병렬화를 강행하는 것은 불필요한 작업일 위험이 있다 |

**특히 강조**: "Agent를 여러 개 만드는 것"(Team04의 3-Agent 존재)과
"실제 Parallel DAG를 만드는 것"(동시 실행 + Aggregator)은 이미 이
저장소의 Governance 문서들 자신이 구분해서 다루고 있다 — Team04/05
모두 전자(Agent/책임 분리)는 문서·실험 코드 수준에서 확인됐지만,
후자(실제 병렬 배선)는 Production에 없고 승인되지도 않았다.

## 6. AGENT / CAPABILITY GAP

| Team | Architecture가 요구하는 Agent | Current Agent | Missing Agent | 중복 Agent | 잘못된 책임을 가진 Agent |
|---|---|---|---|---|---|
| 01 | Intent/Goal/Requirement/Ambiguity(4) + Requirement(PRD 재사용) | 동일 | 없음 | 없음 | 없음 |
| 02 | Task & Dependency Agent(1, 명시적으로 이거 하나여야 함) | 동일 | 없음(2-Agent는 Rejected이므로 "missing"이 아님) | 없음 | 없음 |
| 03 | Design Agent(1, 문서상 유일 후보) | 동일 | 없음 | 없음 | 없음 |
| 04 | (제안만) Implementation/Consistency/Minimality(3) — **미승인** | Backend Agent code_generation(1) | 승인되지 않았으므로 "missing"으로 세지 않음(N/A) | 없음 | 없음 |
| 05 | (제안만) Review는 유지, 6개 책임 중 Review만 Agent(LLM), 나머지 5개는 결정적 검사 — **6-way Parallel 배선만 미승인, 개별 검사 자체는 이미 존재** | Backend Agent code_review(1) + 4개 결정적 함수 | 없음(6개 책임이 전부 코드로는 이미 존재 — Structure/Scope-spec/Scope-design(AST 대응)/Test/Review, Dependency만 명시적으로 별도 함수가 없고 AST 검사에 준하는 로직에 흡수돼 있음) | 없음 | 없음 |

Agent/Capability 경계는 5개 Team 전부 Architecture와 일치한다 — 각
Agent 함수(`*_agent_*`)는 정확히 하나의 Capability만 수행하고,
`call_engine`류 함수는 Provider-specific 이름을 노출하지 않는다
(이전 종합 리뷰가 이미 정적 검사로 확인, 이번 조사가 문서 대조로
재확인).

## 7. DAG / ORCHESTRATION GAP

실제 function-level call graph(코드에서 직접 추출):

```
workflow.py::run_workflow()
 ├─ context_team.run_context_team(issue)
 │    └─ stage_01_multi_agent.run_stage_01_multi_agent(issue)
 │         ├─ [parallel] intent/goal/requirement/ambiguity agents (reasoning.py, ThreadPoolExecutor)
 │         ├─ aggregate_reasoning(...)
 │         ├─ [parallel] structure/relevant/ast code-analysis (code_analysis.py, ThreadPoolExecutor)
 │         ├─ aggregate_context(...)
 │         └─ prd_synthesis.synthesize_prd(...) → requirements_agent_requirement_analysis(...)
 ├─ planning_team.run_planning_team(issue, stage_01)
 │    └─ stage_02.run_stage_02(...)
 │         ├─ task_dependency_agent.decompose_tasks_and_dependencies(...)  [단일 Agent]
 │         └─ planning_pipeline.build_plan(...)  [결정적]
 ├─ architecture_team.run_architecture_team(issue, stage_01, stage_02)
 │    └─ stage_03.run_stage_03(...)
 │         └─ design_agent_design(...)  [단일 Agent]
 ├─ implementation_team.run_implementation_team(stage_01, stage_03, expose_target)
 │    └─ stage_04.run_stage_04(...)
 │         └─ backend_agent_code_generation(...)  [단일 Agent]
 └─ validation_team.run_validation_team(stage_02, stage_04)
      └─ stage_05.run_stage_05(...)
           ├─ _check_structural(...)          [결정적, 순차]
           ├─ _check_specification_scope(...) [결정적, 순차]
           ├─ _check_design_scope(...)        [결정적/AST, 순차]
           ├─ _run_pytest_with_applied_implementation(...) [결정적, 순차, 원본 파일 mutate+restore]
           └─ backend_agent_code_review(...)  [단일 Agent, advisory, 순차]
```

- **missing branch**: 없음(Architecture가 요구하는 branch는 전부
  존재).
- **unnecessary sequential dependency**: Team05의 4개 결정적 검사 +
  Review 사이에는 Architecture(RFC-0039 §2)가 "독립적(A 등급)"이라고
  판정한 것이 다수 있으나, 이들을 순차로 묶어 실행하는 것 자체가
  "불필요한 순차 의존"은 아니다 — Production Adoption이 아직 미승인
  이므로 현재 순차 실행이 **Architecture 위반이 아니라 유일하게
  승인된 상태**다.
- **missing parallel branch**: Team04(3-Agent), Team05(6-way DAG) —
  단, 둘 다 §2/§4에서 확인한 대로 **의도적으로 미승인** 상태이므로
  "빠뜨린 것"이 아니라 "아직 만들면 안 되는 것"이다.
- **missing aggregator**: 없음(Team02/03/04는 단일 생산자라 Aggregator
  자체가 Architecture상 불필요, Team05는 이미 단순 Aggregator 보유).
- **circular dependency**: 0건(이전 종합 리뷰의 import 실행 검증
  재확인, `stages/` → `teams/` 역방향 참조 없음, `openrouter_engine.py`
  는 leaf 모듈).
- **hidden dependency**: 0건(각 Team의 입력 파라미터가 실제 호출부
  (`workflow.py`)와 정확히 일치, 암묵적 전역 상태 공유 없음).
- **unnecessary LLM call**: 0건(각 Team의 LLM 호출 수는 Architecture가
  정한 수와 정확히 일치 — Team01=5회(4 reasoning+1 PRD), Team02~05=
  각 1회).

## 8. OPENROUTER MIGRATION GAP(Team별 call path만 재확인, API 호출 없음)

| Team | Agent | LLM call | OpenRouter Adapter | Free Pool | Deterministic Filter | ≤3 | `models[]` |
|---|---|---|---|---|---|---|---|
| 01 | reasoning.py(4) + requirements.py(1) | `call_engine`(각각) | `openrouter_engine.call_engine_via_openrouter` | ✅ | ✅ | ✅ | ✅ |
| 02 | task_dependency_agent.py | `call_engine` | 동일 | ✅ | ✅ | ✅ | ✅ |
| 03 | design.py | `call_engine` | 동일 | ✅ | ✅ | ✅ | ✅ |
| 04 | backend.py(code_generation) | `call_engine_generation` | 동일 | ✅ | ✅ | ✅ | ✅ |
| 05 | backend.py(code_review) | `call_engine_review` | 동일 | ✅ | ✅ | ✅ | ✅ |

5개 Team 전부 **동일한 단일 Adapter**(`hqs/development/mvp/
openrouter_engine.py`)를 거치므로, Team별 Migration 차이가 구조적으로
존재하지 않는다 — 하나의 Adapter를 검증하면 5개 Team 전부를 검증한
것과 같다(이전 종합 리뷰가 이미 `python3 -c` 직접 import로 5개 call
site의 `__module__`이 전부 `mvp.openrouter_engine`임을 확인). 이번
조사는 실제 API 호출을 하지 않고 이 사실을 재확인만 했다. **누락
없음.**

## 9. CONTRACT GAP

| 비교 대상 | Architecture 요구 | 현재 구현 | Gap |
|---|---|---|---|
| Team input | 각 Team 함수 시그니처(issue/stage_0N_output 등)는 `workflow.py` 호출부와 governing RFC/ADR의 데이터 흐름과 일치 | 일치 | 없음 |
| Team output | `ContextAnalysisResult`(6키)/`tasks,dependencies,plan`/Design prose/Implementation+sentinel/Verdict+checks | 일치(Migration 커밋이 이 파일들을 건드리지 않음, 이전 리뷰 §5 확인) | 없음 |
| Agent input/output | `str -> str`(모든 Agent 함수) | 일치 | 없음 |
| Engine boundary | `str -> str`, 단일 `RuntimeError` — 3개 Engine 전부 동일 | 일치(`openrouter_engine.py` 확인) | 없음 |
| OpenRouter response isolation | Stage/Agent 코드가 OpenRouter의 원본 JSON(model 필드, usage, reasoning_tokens 등)을 보면 안 되고 `content` 문자열만 받아야 함 | `_parse_chat_response()`가 `choices[0].message.content`만 반환, 나머지 메타데이터는 Adapter 내부에 머무름(코드 확인, `openrouter_engine.py:164-184`) | 없음 |
| error semantics | 어떤 Engine이 실패해도 `except Exception` → `Engine call failed: {exc}`로 동일하게 처리 | 일치(`workflow.py::_engine_failure_message`가 Engine 종류를 구분하지 않음) | 없음 |
| validation semantics | Contract Validation은 어떤 Engine이 선택됐는지 몰라도 동작해야 함(`ADR-0026` §Contract Boundary) | 일치(`contracts.py`/각 Stage의 검증 함수는 Engine 관련 코드를 import하지 않음, 이전 세션에 확인) | 없음 |

**Contract 변경이 필요한 Gap은 발견되지 않았다.** 따라서 Governance
영향 표시 대상도 없다(만약 Team04/05의 Parallel DAG가 향후 승인되면
`VerificationResult`를 6-Node 구조로 재설계해야 하며, 이는 `ADR-0025`
§12 Validation Required 4번이 이미 "별도 RFC → ADC → ADR 대상"으로
명시해 둔 사항이다 — 이번 조사가 새로 발견한 것이 아니라 기존 기록의
재확인이다).

## 10. TEST GAP

| 항목 | 분류 | 근거 |
|---|---|---|
| Team 01 실제 병렬 실행(ParallelRunner 레벨) | **existing sufficient** | `test_parallel_runner.py::test_tasks_run_concurrently_not_sequentially`가 elapsed-time 비교로 실제 동시성을 증명(< 0.6s vs 순차 시 1.0s+) |
| Team 01 실제 병렬 실행(Stage01 통합 레벨) | **existing but insufficient** | `test_stage_01_multi_agent.py`는 phase 순서(`test_reasoning_fully_completes_before_code_analysis_starts`)만 확인 — 4개 reasoning agent 자신이 서로 겹쳐 실행되는지의 timing 증명은 통합 테스트 레벨에 없음(ParallelRunner 단위 테스트로만 간접 커버) |
| Agent independence(Team01 Aggregator) | **existing sufficient** | `reasoning.py`의 `aggregate_reasoning` 단위 테스트가 충돌/중복 케이스를 검증(`test_stage01_reasoning.py`) |
| Deterministic aggregation(Team02 파이프라인) | **existing sufficient** | `test_planning_pipeline.py`가 사이클 탐지/위상정렬을 개별 검증 |
| Failure policy(3개 Engine 공통) | **existing sufficient** | `test_engine_boundary.py` + `test_openrouter_engine.py`(24개)가 429/5xx/malformed/connection_error/empty_response를 개별 검증 |
| Test Workspace isolation(Team05, Production) | **missing**(Production에 해당 메커니즘 자체가 없으므로 테스트 대상도 없음 — 실험 harness `projects/stage05-parallel-validation-harness-v1/`에는 이미 존재) | `stage_05.py`가 여전히 원본 파일 mutate+restore 방식이라 "Isolation이 작동하는지"를 테스트할 대상 코드가 Production에 없음 |
| OpenRouter adapter import(5개 Team) | **existing sufficient** | `test_engine_boundary.py::test_openrouter_routed_files_import_openrouter_engine_only`/`test_backend_py_uses_openrouter_engine_for_both_capabilities` |
| Stage/Team call path | **existing but could be stronger** | 개별 `test_stage_0N.py`가 각 Stage를 직접 검증하지만, `teams/*/team.py`가 실제로 그 Stage를 올바르게 호출하는지의 통합 테스트는 `test_workflow_integrated.py`/`test_cli_integrated.py`에 있음(이전 리뷰가 이미 확인) — 다만 Team 계층 자체를 겨냥한 전용 단위 테스트(`test_teams_*.py` 류)는 없음 |
| Contract preservation(Migration 전후) | **existing sufficient** | 전체 352 passed가 이를 실질적으로 증명(Contract를 검증하는 기존 테스트가 전부 그대로 통과) |
| Circular import(OpenRouter Adapter) | **missing** | 수동으로(이 조사와 이전 리뷰에서) `python3 -c`로 확인했으나, 이를 codify한 회귀 테스트는 없음 |

## 11. IMPLEMENTATION WORK ESTIMATE

**전제**: §3/§4가 확인한 대로, 승인된 Architecture 기준으로는 5개
Team 모두 추가 구현이 필요 없다. 아래는 (a) 승인된 범위 안에서의
**작은 보강 작업**(Should Implement, §14)과 (b) **참고용으로만** 제시하는
Team04/05의 "만약 향후 승인된다면" 규모 추정이다 — (b)는 이번
Governance 상태에서는 **착수 대상이 아니다.**

### (a) 승인된 범위 안 — Should Implement 후보

| 작업 | 파일 수 | 신규/수정 | 예상 규모 | 테스트 추가 | Governance 영향 | 의존 작업 |
|---|---|---|---|---|---|---|
| Team01 통합 레벨 실제 동시성 증명 테스트 추가 | 1 | 수정(`test_stage_01_multi_agent.py`) | **Small**(수십 LOC) | 1~2개 | 없음(테스트만) | 없음 |
| OpenRouter Adapter 순환 import 회귀 테스트 codify | 1 | 신규 또는 `test_engine_boundary.py`에 추가 | **Small**(10~30 LOC) | 1개 | 없음 | 없음 |
| `workflow.py` Stage/Team 명명 일관성 정리(dict key를 "team_XX"로 통일하거나, 최소한 주석으로 의도 명시) | 1 | 수정(`workflow.py`) + 하위 호환 필요 시 테스트 수정 | **Small~Medium**(명명 변경 범위에 따라 다름, 하위 호환 깨지면 여러 테스트 파일 연쇄 수정 필요) | 기존 테스트 회귀 확인 필수 | **주의**: 이것도 Contract는 아니지만 다수 테스트가 `stage_01` 등 속성명에 의존(`test_workflow_integrated.py`) — 이름을 바꾸면 그 테스트들도 함께 수정해야 함 | 없음(단, 범위가 생각보다 넓을 수 있어 우선순위 재검토 권장) |
| Team rename 자체를 사후 추인하는 경량 Governance 기록(선택) | 1 | 신규 RFC 또는 Evidence(이번 조사가 스스로 만들지 않음) | **Small**(문서만) | N/A | 사용자 판단 필요 — 이번 조사는 "필요성"만 기록 | 없음 |

### (b) 참고용 — Team04/05 향후 승인 시 규모(현재 착수 금지)

이 추정은 **오늘 구현하라는 뜻이 아니다** — `ADC-0040`/`ADR-0025`의
NOT DETERMINED가 먼저 해소돼야 한다. 참고 목적으로만 남긴다:

| Team | 향후 작업(가정) | 신규 파일 | 수정 파일 | 예상 규모 | 의존 작업 |
|---|---|---|---|---|---|
| 04 | 3-Agent Production 배선 + 병렬 executor 연결 + Ponytail 실제 판단 로직 + fail/escalate 경로 | 2~4(Agent 분리, Ponytail 판단 로직) | `stage_04.py`, `team.py`, 관련 테스트 | **Medium~Large**(Ponytail의 "실제 LLM 판단" 요구사항 자체가 RFC-0037에서도 미정의라 설계 작업이 선행돼야 함) | 새 RFC(3-Agent Production 배선 승인) → ADC → ADR, 15회 이상 Real Engine 실측(ADC-0040 요구) |
| 05 | 6-Node 분리 + Aggregator 확장 + Test Workspace 실제 배선(이미 실험 harness에 구현된 것을 Production에 이식) + `VerificationResult` 6-Node Contract 재설계 | 3~6(Node 분리, Workspace 배선) | `stage_05.py`, `contracts.py`(Contract 변경!), `team.py`, 다수 테스트 | **Medium~Large**(Contract 변경이 포함되므로 상위 Workflow 영향 분석 필요) | 새 RFC(Contract 재설계) → ADC → ADR, `ADC-0016` Multi-Task Isolation 재확인, 실제 latency 재실측(이전 실측이 이득 없음을 보였으므로 재실측 근거부터 필요) |

**공통 참고**: Team01이 이미 사용 중인 `mvp/parallel_runner.py`는
**"Stage 01 전용 코드가 아닌 재사용 가능한 내부 병렬 실행 인프라"**로
설계돼 있다(`parallel_runner.py` 모듈 docstring, `RFC-0033/ADC-0036
§Out of Scope`). 따라서 Team04/05가 향후 승인되어 병렬화를 구현하게
되더라도 **새 병렬 실행 엔진을 처음부터 만들 필요는 없다** — 다만
`ADC-0015`가 "동일 Target 동시 실행"류 케이스에 Thread를 금지하고
Process를 요구하므로, `ParallelRunner`(Thread 기반)를 그대로 재사용할
수 있는지, 아니면 Process 기반의 별도 실행기가 필요한지는 승인 시점에
다시 판단해야 한다(Team01의 4개 reasoning agent는 파일 mutation이
없어 Thread로 충분했지만, Team05의 Test는 파일을 mutate하므로 다른
격리 축이 필요하다는 점은 `ADR-0025` §6이 이미 확인해 둔 사실이다).

## 12. IMPLEMENTATION ORDER(승인된 범위 (a)에 한정)

1. OpenRouter Adapter 순환 import 회귀 테스트 추가(독립적, 의존성 없음)
2. Team01 통합 레벨 동시성 증명 테스트 추가(독립적)
3. `workflow.py` 명명 일관성 검토 — 범위를 먼저 확정(다수 테스트
   연쇄 수정 가능성 때문에 가장 나중, 그리고 별도 승인/합의 후 진행 권장)
4. (선택) Team rename 사후 Governance 기록 — 사용자 판단 필요, 위
   1~3과 독립적으로 아무 때나 진행 가능

Team04/05의 (b) 항목은 이 순서에 포함하지 않는다 — Governance 결정이
선행돼야 순서를 논할 수 있다.

## 13. GOVERNANCE IMPACT

| Gap/작업 | 기존 Architecture 내 구현 가능 | RFC 필요 | ADC 필요 | ADR 필요 | Contract 변경 필요 | Governance 변경 불필요 |
|---|---|---|---|---|---|---|
| Team01/02/03 관련 모든 항목 | ✅ | | | | | ✅(이미 승인된 범위) |
| Team01 통합 동시성 테스트 | ✅ | | | | | ✅ |
| 순환 import 회귀 테스트 | ✅ | | | | | ✅ |
| `workflow.py` 명명 정리 | ✅(코드 스타일 문제일 뿐) | | | | 아니오 | ✅ |
| Team04 3-Agent+Ponytail Production 배선 | ❌ | **필요**(3-Agent Production 배선 승인) | **필요** | **필요**(현재 ADR 없음) | 아니오(Engine Contract는 무관) | ❌ |
| Team05 6-way Parallel DAG Production 배선 | ❌ | **필요**(이미 ADR-0025가 예고: `VerificationResult` 재설계는 "별도 RFC → ADC → ADR 대상") | **필요** | **필요**(ADR-0025 자체가 Production Adoption을 미승인) | **필요**(`VerificationResult` 6-Node 구조 재설계) | ❌ |
| Team05 LLM Review Production 배선 | ❌ | **필요** | **필요** | **필요**(ADR-0025 §10 NOT YET DETERMINED) | 아니오(Review는 advisory라 Verdict Contract 불변) | ❌ |

`ADR-0027`이 승인한 범위(OpenRouter Free Model Selection Architecture
Production 편입)를 넘는 변경 — 즉 Team04/05의 Multi-Agent/Parallel
구조 확장 — 은 전부 위 표에서 **별도 Governance 대상으로 분리**됐다.

## 14. FINAL IMPLEMENTATION SCOPE

### Must Implement

**없음.** 5개 Team 모두 현재 승인된 Architecture를 이미 만족한다.
"Architecture를 만족시키기 위해 반드시 필요한 것"은 이번 조사에서
발견되지 않았다.

### Should Implement

- OpenRouter Adapter 순환 import 회귀 테스트(Small).
- Team01 통합 레벨 실제 동시성 증명 테스트(Small).
- `workflow.py`의 Stage/Team 명명 불일치 정리 — 단, 영향 범위(여러
  테스트 파일의 monkeypatch 대상)를 먼저 확인 후 착수 권장(Small~Medium).
- (선택) Stage→Team rename에 대한 경량 사후 Governance 기록 — 이번
  조사가 발견한 사실을 남기는 것으로, 필수는 아니나 향후 감사
  대응에 유용(Small, 문서만).

### Do Not Implement

- Team04 3-Agent(Implementation/Consistency/Minimality) + Ponytail의
  Production 배선 — `ADC-0040`이 NOT DETERMINED, ADR 부재.
- Team05 6-way Parallel Validation DAG의 Production 배선(Test
  Workspace 격리 포함) — `ADR-0025` §11 NOT YET DETERMINED, 게다가
  이미 한 번 실측해 이득이 확인되지 않음.
- Team05 LLM Review의 Production 배선 — `ADR-0025` §10 NOT YET
  DETERMINED.
- Team02/03에 임의로 Multi-Agent 구조 추가 — 각각 RFC-0035(2-Agent
  분리 명시적 Rejected)와 RFC-0030(추가 Agent 후보 없음)에 반한다.

### 전체 규모 요약

- 총 신규 파일: **0~2개**(Should Implement 항목 중 회귀 테스트 신규
  파일 여부에 따라, 기존 파일에 추가하는 것으로도 충분할 수 있음)
- 총 수정 파일: **1~4개**(`test_stage_01_multi_agent.py`,
  `test_engine_boundary.py`, `workflow.py`(+연쇄되는 테스트 파일들))
- 대략적 LOC 범위: **Small**(수십~150줄 내외, `workflow.py` 명명
  정리의 파급 범위에 따라 변동)
- 테스트 추가 규모: **Small**(2~5개 테스트)
- 예상 작업 단위 수: **3~4개**(§12 순서 참조)
- **가장 큰 Risk**: Team04/05를 "Team이니까 당연히 Multi-Agent/
  Parallel이어야 한다"는 선입견으로 임의 구현하는 것 — 이는 이미
  NOT DETERMINED로 유보된 Governance 결정을 코드로 우회하는 것이며,
  `hqs/development/IMPLEMENTATION_RULES.md`의 "Architecture 변경은
  구현으로 해결하지 않는다" 원칙을 정면으로 위반한다. 두 번째로 큰
  Risk는 `workflow.py` 명명 정리 시도가 예상보다 넓은 테스트 연쇄
  수정을 유발해 "Small 정리"가 "Medium 리팩터링"으로 번지는 것이다.

## 15. FINAL VERDICT

**Architecture Implementation Gap: Small**
(승인된 Architecture 기준으로는 사실상 Gap이 없다 — "Small"은 §14
Should Implement의 사소한 보강 항목만을 반영한 것이며, 엄밀히는
"거의 0에 가까운 Small"이다.)

**Migration Gap: Small**
(OpenRouter Migration 자체는 코드 레벨에서 완전하다 — 남은 것은
`ADR-0027` §9 Validation Gate의 실제 실측뿐이며, 이는 코드 작업이
아니라 실행/검증 작업이고 이번 조사 범위 밖이다.)

**Team Architecture Completion: Governance Blocked**
(Team01~03은 사실상 "Ready/Complete"이지만, 전체 5개 Team 중 Team04/
05가 목표로 하는 더 정교한 구조(3-Agent+Ponytail, 6-way Parallel DAG)
는 명시적으로 Governance가 막아둔 상태다 — "Needs Architecture
Clarification"이 아닌 이유는 문서가 불명확해서가 아니라, 문서 스스로
"NOT DETERMINED"라고 **명확하게** 결론 내렸기 때문이다.)

### "지금 바로 구현해도 되는 범위"

- §14 Should Implement 3~4개 항목(회귀 테스트 2종, `workflow.py`
  명명 정리 — 영향 범위 확인 후, 선택적 Governance 기록 문서).

### "추가 Architecture/Governance 결정이 필요한 범위"

- Team04: 3-Agent + Ponytail Production 배선 전체(RFC → ADC → ADR
  전 과정 재개 필요, Real Engine Evidence 15건 이상 실측 필요).
- Team05: 6-way Parallel DAG Production 배선 전체 + `VerificationResult`
  Contract 재설계(RFC → ADC → ADR 전 과정 필요) + LLM Review Production
  배선(별도 결정 필요).

---

## 최종 보고

1. **Architecture와 실제 구현의 핵심 차이**: 사실상 차이가 없다.
   겉보기 차이(Team02/03/04가 단일 Agent, Team05가 순차)는 전부
   Governance 문서 자신이 의도했거나(Team02/03), 아직 승인하지
   않은 것(Team04/05)이다.
2. **Team 01~05별 Gap**: §3 Matrix 참조 — 전부 "Already Implemented"
   또는 "N/A(미승인)".
3. **Multi-Agent/Parallelization Gap**: Team01만 실제 병렬 완비(초과
   달성, 허용됨). Team02/03은 애초에 대상 아님. Team04/05는 설계·
   실험은 있으나 Production 배선은 Governance가 보류.
4. **OpenRouter Migration Gap**: 없음(구조적으로 완전) — 남은 것은
   실측 Validation Gate뿐(범위 밖).
5. **Stage→Team Rename Gap**: 기능적으로는 완전(실제 진입점 교체,
   재구현 없음) — 전용 Governance 문서 부재, `workflow.py` 명명
   불일치 2건의 비파괴적 finding.
6. **Must/Should/Do Not Implement**: §14 참조.
7. **예상 구현 규모**: Small(§14 요약).
8. **구현 순서**: §12 참조(승인된 범위 한정, 4단계 이내).
9. **Governance 영향**: §13 참조 — Team04/05 확장은 전부 새 RFC→ADC→
   ADR 필요, `ADR-0027` 범위 밖으로 명확히 분리.
10. **최종 판단**: Architecture Implementation Gap = Small, Migration
    Gap = Small, Team Architecture Completion = Governance Blocked
    (Team04/05의 고도화만 해당, Team01~03은 이미 Complete).

---

### 별도 확인 항목

- **Architecture**: 변경 없음(이번 조사는 읽기 전용).
- **Contract**: 변경 없음(§9 확인, Gap 없음).
- **Governance**: `RFC-0040`/`ADC-0043`/`ADR-0026`/`RFC-0041`/
  `ADC-0044`/`ADR-0027`/`RFC-0033`~`RFC-0039`/`ADC-0036`~`ADC-0042`/
  `ADR-0021`~`ADR-0025` — 전부 무수정. 새 RFC/ADC/ADR 미생성.
- **Production Code**: 이 조사 세션에서 전혀 수정하지 않음.
- **Validation Gate**: `ADR-0027` §9 — OPEN 유지, 실행/판정하지 않음.
- **Branch**: `claude/jarvis-openrouter-validation-bin9aj`
- **Commit**: 이 Evidence 문서 추가가 새 commit(코드 변경 없음).
- **PR**: 없음(생성하지 않음).

## Related

- `docs/architecture/core/RFC-0033-stage01-multi-agent-reasoning-adoption.md`,
  `ADC-0036-stage01-multi-agent-reasoning-resolution.md`,
  `ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md`
- `docs/architecture/core/RFC-0034-stage01-prd-specification-synthesis.md`,
  `ADC-0037-stage01-prd-specification-synthesis-resolution.md`,
  `ADR-0022-stage01-prd-specification-synthesis-baseline.md`
- `docs/architecture/core/RFC-0035-stage02-planning-responsibility-and-execution-model.md`,
  `ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md`,
  `ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md`
- `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`(Team03 유일 참고, Proposed)
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `ADC-0040-stage04-multi-agent-ponytail-decision.md`(ADR 없음)
- `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md`,
  `ADC-0041-stage05-qa-multi-agent-decision.md`
- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`,
  `ADC-0042-stage05-parallel-validation-dag-decision.md`,
  `ADR-0025-stage05-parallel-validation-architecture-boundary.md`
- `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md`,
  `ADC-0044-openrouter-production-engine-migration-decision.md`,
  `ADR-0027-openrouter-production-engine-migration-adoption.md`
- `docs/research/STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md`
  (이 문서의 직접 선행 리뷰, 코드 현황 조사)
- `docs/research/OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`
- `hqs/development/IMPLEMENTATION_RULES.md`("Architecture 변경은 구현으로 해결하지 않는다")
- `hqs/development/HANDOVER.md`

---

**Architecture Implementation Gap: Small**
**Migration Gap: Small**
**Team Architecture Completion: Governance Blocked**
