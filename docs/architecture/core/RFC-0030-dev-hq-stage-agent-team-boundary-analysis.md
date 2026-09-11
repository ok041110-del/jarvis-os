# RFC-0030: Dev HQ Stage 01~05 Agent Team Boundary Analysis (Phase F-2)

**Status**: Proposed (분석 결과 기록, Baseline 결정 아님). **§3 Stage 01
항의 "추가 Agent 후보 없음" 결론은 `ADC-0036`으로 superseded됨** — Stage
01 Multi-Agent Reasoning 도입 결정은 `RFC-0033`/`ADC-0036`/`ADR-0021`
참조. 이 문서 본문은 원 분석 기록 보존을 위해 무수정.
**Author**: Claude Code
**대상**: `hqs/development/CONSTITUTION.md`·`BASELINE.md`·`IMPLEMENTATION_RULES.md`,
`hqs/development/workflow.py`, `hqs/development/stages/01~05/stage_0N.py`,
`hqs/development/mvp/agents/*.py`, `hqs/development/mvp/project_intelligence.py`,
`hqs/development/mvp/workflow_ast_context.py`, `docs/architecture/core/RFC-0024~0029`·
`ADC-0032`·`ADC-0033`(Phase A~F-1 — 전부 Defer/Open 또는 "이미 Decided,
재정의 불필요").

**Evidence**: 위 코드 전체 직접 읽음, `grep`으로 Engine 호출 지점 전수
조사. **Production Code는 변경하지 않았다** — 이 RFC는 분석 문서다.

> 이 RFC는 `RFC-0029`(Phase F-1)의 결과를 **전제**로 삼는다 — Stage
> 전체를 Agent로 승격할 근거는 없다는 결론이 이미 확정됐다. 이 RFC는
> 그 결론을 뒤집지 않고, **Stage 내부**의 개별 작업 단위로 분석
> 수준을 좁힌다. Agent Domain/Lifecycle/State/Message/Event/Agent
> Manager/Runtime Contract 어느 것도 이 RFC로 새로 확정되지 않는다.

---

## 0. 이 RFC가 열린 이유

`RFC-0029`(Phase F-1)는 "Stage를 통째로 Agent로 볼 수 있는가"에
**아니오**로 답했다 — Agent에 해당하는 부분(Engine 호출)은 이미
`mvp/agents/`로 분리되어 있고, Stage 자신은 골격 조립·Contract 검증·
흐름 제어라는 별개 책임을 가진 Workflow Step이었다. Phase F-2는 그
분석을 한 단계 더 파고든다 — "각 Stage **내부에** 아직 이름 붙지 않은
Agent 후보(LLM 판단이 필요한 작업)가 더 있는가?"라는 질문이다. 이
질문은 문서 재검토가 아니라 **코드를 다시 읽어야만 답할 수 있다** —
아래 §2가 그 결과다.

## 1. 판단 기준 — 엄격한 Agent 인정 조건

사용자 지시대로, **"함수/검사 하나를 Agent라고 명명하는 것"은
후보에서 제외**한다. Agent 후보로 인정하는 조건은 둘 중 하나다.

1. **LLM 기반 판단이 실제로 필요하다** — 결정적 규칙(AST 매칭, 정규식,
   키워드 스코어링, subprocess 실행 결과 비교)으로 대체 불가능한
   판단을 코드가 실제로 Engine 호출로 수행하고 있다.
2. **독립적인 전문 역할**이 이미 분리되어 있다 — 다른 역할과 책임이
   겹치지 않고, 별도 Capability로 재사용 가능하다.

## 2. 코드 전수 조사 — Engine 호출 지점 전체

`grep -rn "call_engine\|call_engine_via_omniroute"
hqs/development/mvp/*.py hqs/development/stages/*/*.py`(정의부 제외)
결과, 이 저장소에 존재하는 **모든** LLM 판단 지점은 다음 5곳뿐이다.

| # | 위치 | 함수 | 현재 "Agent" 이름 존재? |
|---|---|---|---|
| 1 | `mvp/agents/requirements.py` | `requirements_agent_requirement_analysis` | 예 — Requirements Agent |
| 2 | `mvp/agents/design.py` | `design_agent_design` | 예 — Design Agent |
| 3 | `mvp/agents/backend.py` | `backend_agent_code_generation` | 예 — Backend Agent(code_generation) |
| 4 | `mvp/agents/backend.py` | `backend_agent_code_review` | 예 — Backend Agent(code_review) |
| 5 | **`mvp/workflow_ast_context.py::identify_target`** | (이름 없음) | **아니오** — Stage 04가 직접 호출, `mvp/agents/`에 없음 |

**핵심 발견(#5)**: Stage 04의 Target 식별(`identify_target`)은
`Phase F-1`(RFC-0029)이 "결정적"으로 분류했으나, 코드를 다시 읽은
결과 **실제로는 Engine을 호출하는 LLM 판단**이다 — Design 텍스트와
후보 함수 인덱스를 프롬프트로 구성해 `call_engine()`을 호출하고,
응답에서 정규식으로 FILE/FUNCTION 라인만 파싱한다(파싱은 결정적이나
**판단 자체는 LLM이 한다**). 이는 이 저장소에서 **유일하게 존재하는,
아직 이름 붙지 않은 실제 Agent 후보**다. Phase F-1의 재분류: Target
식별은 "결정적"이 아니라 "Engine 호출 + 결정적 파싱"이며, 이 RFC가
정정한다.

이 5곳 외에는 어떤 Engine 호출도 없다 — Stage 01(`project_intelligence.py`)은
정규식·키워드 스코어링만 쓰는 **규칙 기반**(코드 주석 자기 선언: "규칙
기반 Context 수집")이고, Stage 05의 4개 결정적 검사(structural/
specification_scope/design_scope/test_execution)도 AST 파싱과 pytest
subprocess 결과 비교일 뿐 Engine을 호출하지 않는다.

## 3. Stage별 분석

### Stage 01 — Context Analysis

| 항목 | 내용 |
|---|---|
| ① 현재 Agent | **없음** |
| ② 추가 Agent 후보 | **없음** — `collect_relevant_context`/`build_context_bundle`/`build_function_candidate_index`/`build_dependency_closure` 전부 정규식·AST 기반 규칙(§2). "관련성 판단"이 의미상 LLM 판단처럼 보일 수 있으나, 코드는 명시적으로 규칙 기반이며 그 자체가 Development HQ 내부용으로 의도적으로 설계된 것(`project_intelligence.py` 헤더 주석)이다 |
| ③ 병렬 후보 | 해당 없음(Agent가 없으므로) — 단, 5개 결정적 함수 자체는 서로 입력 독립(`issue`, 정적 파일 시스템)이라 **함수 수준 병렬화는 기술적으로 가능**하나 이는 Agent Team 질문이 아니라 §16.4 Multi-Task 범위의 별개 관찰이다 |
| ④ 의존 관계 | 없음(첫 Stage) |
| ⑤ 결과 종합 지점 | 해당 없음 |
| ⑥ Agent화 근거 부족 영역 | 전체 — LLM 판단이 전혀 없다 |

### Stage 02 — Planning/Specification

| 항목 | 내용 |
|---|---|
| ① 현재 Agent | Requirements Agent(`requirements_agent_requirement_analysis`) 1개 |
| ② 추가 Agent 후보 | **없음** — `_structure_from_context`/`_skeleton_to_text`/`_enrich_issue_with_skeleton`은 Stage 01 Output을 재배치하는 순수 문자열 조립이며 Engine을 호출하지 않는다(§2 표에 없음) |
| ③ 병렬 후보 | 없음 — Agent가 1개뿐 |
| ④ 의존 관계 | Stage 01 Output(`context_bundle`)에 골격 조립이 의존 |
| ⑤ 결과 종합 지점 | 해당 없음(단일 Agent 결과가 곧 Stage 출력) |
| ⑥ Agent화 근거 부족 영역 | 골격 조립 로직(Constraints/Risks/Scope Candidates 재배치) — 결정적 재배치이며 판단이 아니다 |

### Stage 03 — Architecture/Design

| 항목 | 내용 |
|---|---|
| ① 현재 Agent | Design Agent(`design_agent_design`) 1개 |
| ② 추가 Agent 후보 | **없음** — Stage 02와 동형 구조, 골격 조립(`_structure_from_specification`)이 결정적 재배치뿐 |
| ③ 병렬 후보 | 없음 |
| ④ 의존 관계 | Stage 01(`candidate_index`)·Stage 02(`skeleton`, `specification`) Output에 의존 |
| ⑤ 결과 종합 지점 | 해당 없음 |
| ⑥ Agent화 근거 부족 영역 | 골격 조립 로직 |

### Stage 04 — Implementation (가장 복잡한 내부 구조)

| 항목 | 내용 |
|---|---|
| ① 현재 Agent | Backend Agent(`backend_agent_code_generation`) 1개(명명됨) |
| ② 추가 Agent 후보 | **Target Identification**(`identify_target`, §2 #5) — **LLM 판단 기준(§1-1) 충족, 독립 전문 역할 기준(§1-2)도 충족**(어느 파일·함수를 고칠지 결정하는 것은 "무엇을 작성할지" 결정하는 Code Generation과 명백히 다른 판단). 이 RFC는 이를 실질적인 **미명명 Agent 후보**로 인정한다 |
| ③ 병렬 후보 | **없음** — Target Identification의 출력(`target`)이 Build Input 조립·Code Generation의 입력이므로 순차적이다. 병렬화 불가능한 진짜 순차 의존(Sequential dependency) |
| ④ 의존 관계 | Target Identification → Build Input 조립(결정적) → Code Generation — **2-Agent 순차 Handoff**(Phase E `RFC-0028`의 실험 시나리오와 정확히 동형 구조가 이미 Production 코드에 존재) |
| ⑤ 결과 종합 지점 | 없음(단일 순차 파이프라인, 종합이 아니라 전달) |
| ⑥ Agent화 근거 부족 영역 | Build Input 조립(`_assemble_build_input`) — closure 삽입·Exposure Policy 문구 첨부는 결정적 문자열 조립이며 Exposure Policy 충돌 판단도 Engine 응답의 **정해진 접두어(`EXPOSURE_POLICY_CONFLICT:`) 매칭**이라는 결정적 파싱이다(Engine이 그 신호를 만들지만, Stage 04는 그것을 판단하지 않고 문자열 매칭만 한다) |

### Stage 05 — Validation

| 항목 | 내용 |
|---|---|
| ① 현재 Agent | Backend Agent(`backend_agent_code_review`, code_review) 1개(명명·호출됨) |
| ② 추가 Agent 후보 | **QA Agent**(`qa_agent_test_execution`) — `RFC-0029` §3.3이 이미 발견한 "정의만 되고 미호출"인 함수. **LLM 판단 기준 충족**(테스트 케이스 제안은 code_review와 다른 판단), **독립 전문 역할 기준도 충족**(review와 test proposal은 서로 다른 전문성). 단, 현재 미호출이므로 "실제 코드 근거"가 정의부에만 있고 **실행 경로 근거는 없다** — 이 RFC는 이를 "코드로 이미 준비돼 있으나 활성화되지 않은 후보"로 구분해 기록한다 |
| ③ 병렬 후보 | code_review(Backend Agent)와 test proposal(QA Agent, 활성화된다면)은 **둘 다 `implementation`(Stage 04 Output)만 입력으로 받고 서로의 출력에 의존하지 않는다** — 병렬 실행 가능한 진짜 Fan-out 후보 |
| ④ 의존 관계 | 둘 다 Stage 04 `implementation`에 의존, 서로 독립. 4개 결정적 검사(structural/specification_scope/design_scope/test_execution)는 Agent가 아니라 Function/Tool로 유지(`RFC-0029` §4 재확인) |
| ⑤ 결과 종합 지점 | **Verdict 결정**(`_determine_verdict`) — code_review·(활성화 시) test proposal·4개 결정적 검사 결과를 **모아서** 최종 판정하는 지점. 이 종합 로직 자체를 Agent화하는 것은 `RFC-0029` §3.2가 이미 경고한 Policy 구현 금지 위험을 그대로 안고 있으므로 **이 RFC도 Agent 후보에서 제외**한다 |
| ⑥ Agent화 근거 부족 영역 | 4개 결정적 검사 전부, Verdict 결정 로직 |

### Stage 06 — devops_release (코드 없음, 향후 후보만 기록)

`README.md`만 존재하고 `stage_06.py`가 없다(`RFC-0029` §1 재확인 — 이
RFC로도 무변경). **현재 Production 코드가 없으므로 Agent Team 분석
대상이 아니다.** 다만 이름("devops_release")이 시사하는 책임(배포
전 검토, 릴리스 노트 작성 등)은 일반적으로 LLM 판단이 필요한 영역과
결정적 영역(CI 트리거, 버전 태깅)이 섞일 가능성이 높다는 점만
**향후 후보 가능성으로 기록**한다 — 이 RFC는 그 이상을 설계하지
않는다(코드가 없는 것을 설계하는 것은 Architecture Need 없이 미래를
앞서 설계하는 것이다).

## 4. Agent 간 Dependency Graph가 실제로 필요한 수준인가

Stage 02~05 전체를 통틀어 관찰된 Agent 간 관계는 두 종류뿐이다.

- **순차 Handoff**(Stage 04 내부, Target Identification → Code
  Generation) — 선형 체인, 분기·Loop 없음.
  Stage 간(02→03→04)도 마찬가지로 선형.
- **독립 병렬 + 단일 종합**(Stage 05 내부, code_review ∥ test
  proposal → Verdict) — Fan-out/Fan-in 1단계, Loop 없음.

**이 둘을 표현하는 데 일반화된 Dependency Graph 엔진은 필요하지
않다.** §16.6 Workflow Adapter가 이미 Kernel Module 후보로 Accept한
어휘(Node/Conditional Edge/Loop) 중 **Conditional Edge와 Loop는
이 저장소의 실제 Agent 관계 어디에도 관찰되지 않았다** — Stage 04의
"Exposure Policy 충돌" 분기는 Agent 간 조건부 라우팅이 아니라 값
매칭(§3 Stage 04 ⑥)이고, 어떤 Stage에도 반복(Loop)이 없다. 관찰된
것은 순차(Sequence)와 1단계 병렬(Parallelism)뿐이며, 이는 §16.4
Multi-Task(Accept, Scoped, Conditional)의 "독립 Task 동시 실행" 범위
안에 있다 — **새 그래프 엔진이나 Runtime을 요구하지 않는다.**

## 5. Workflow Adapter(§16.6) 어휘와의 관계 — 관찰만, Contract 확정 아님

| §16.6 어휘 | 이 분석에서 관찰된 대응 | 새 Contract 필요한가 |
|---|---|---|
| Node | Stage 04의 Target Identification, Code Generation 각각을 Node로 볼 여지 | **아니오** — §16.6은 이미 Accept(Scoped, Conditional)됐고, Production 개시는 별도 Gate(B)/(C) 소관(`RFC-0026` §2.2 재확인) |
| Conditional Edge | 관찰되지 않음(§4) | 해당 없음 |
| Loop | 관찰되지 않음(§4) | 해당 없음 |
| Parallelism | Stage 05의 code_review ∥ test proposal | §16.4 Multi-Task로 이미 충분(§4) |
| State(A-IN(a)) | 각 Agent 호출의 입출력이 caller(Stage 함수)가 들고 있는 지역 변수일 뿐, Kernel/Runtime이 보유하는 공유 State가 아님 | 해당 없음 — Phase B(`RFC-0025` §4 Agent State)와도 다른 층위, 접점 관찰만(§6) |

## 6. Phase A~E Defer/Open과의 접점 재확인 — 우회 아님

- Target Identification·QA Agent를 "Agent 후보"로 인정한 것(§3)은
  **Agent Domain(Phase A, `RFC-0024`/`ADC-0032`, Defer)을 Accept로
  전환하는 것이 아니다** — 이 RFC는 이 두 후보에 Identity/Role/
  Capabilities/State 등 Domain 필드를 부여하지 않았다. "LLM 판단
  지점이 코드에 실재한다"는 사실 관찰과 "Agent Domain Contract를
  Accept한다"는 결정은 다르다.
- Stage 05의 병렬 Fan-out 관찰(§3)은 Agent State/Message/Event(Phase
  B, `RFC-0025`/`ADC-0033`, Defer/Open)를 재정의하지 않는다 — 두
  Agent가 "통신"하는 것이 아니라 caller가 각각 독립 호출하고 결과를
  모을 뿐이다(§16.4 범위 그대로).
- §5의 Workflow Adapter 대응 관찰은 `RFC-0026`(Phase C)의 결론(§16.6은
  이미 Decided, 재정의 불필요)을 그대로 따른다.
- Dependency Graph 불필요 판단(§4)은 `RFC-0027`/`RFC-0028`(Phase D/E)의
  "실제 소비자 없음, 현재 Contract로 충분" 결론과 정합적이다 — 오히려
  이번 코드 재조사가 그 결론을 Dev HQ 내부에서 더 구체적으로 재확인한
  것이다.

## 7. 최적 Stage/Stage 조합 — Multi-Agent Workflow·LangGraph Mapping 검증용

**선정: Stage 04 + Stage 05 조합.**

### 근거

1. **이미 존재하는 실제 코드 근거** — 이 조합만이 §2에서 발견한 5개
   Engine 호출 지점 중 4개(Target Identification, Code Generation,
   Code Review, QA — 활성화 시)를 전부 포함한다. 다른 Stage(01~03)는
   Agent가 0~1개뿐이라 "Multi-Agent"라 부를 근거가 약하다.
2. **두 가지 관계 유형을 모두 포함** — Stage 04는 순차 Handoff(Target
   Identification → Code Generation), Stage 05는 독립 병렬 + 단일
   종합(code_review ∥ test proposal → Verdict). 이는 §16.6이 이미
   Accept한 어휘 중 Node·Parallelism 두 가지를 실제 코드 근거로
   검증할 수 있는 유일한 조합이다.
3. **Loop·Conditional Edge가 필요 없어 범위가 최소로 유지된다** — §4가
   확인했듯 이 조합 어디에도 반복·조건부 라우팅이 없으므로, 검증
   시나리오가 §16.6 A-IN 전체(다섯 항목)를 억지로 채우려 하지 않고
   실제 관찰된 두 항목만 다루면 된다 — Phase E(`RFC-0028`)가 지킨
   "필요한 것만" 원칙과 일치한다.
4. **Stage 04→05 경계 자체가 이미 HQ-level Public Contract**
   (`ImplementationResult`→`VerificationResult`, `ADR-0009`)로
   형식화돼 있어, 실험이 그 Contract를 재해석할 필요 없이 그대로
   재사용할 수 있다.

**제외 사유(01~03)**: Stage 01은 Agent가 0개라 Multi-Agent 검증
대상이 될 수 없다. Stage 02·03은 각각 Agent가 1개뿐이라 "Multi-"라는
전제 자체가 성립하지 않는다.

## 8. Out of Scope

- Target Identification·QA Agent를 실제로 `mvp/agents/`에 명명·등록
  하는 것 — 이 RFC는 코드를 변경하지 않는다.
- §7이 선정한 Stage 04+05 조합의 **Experimental PoC 구현** — 제안된
  적 없다(이번 Phase는 분석만 요청받았다; 구현은 후속 세션 판단).
- Agent Domain/Lifecycle/State/Message/Event/Agent Manager/Runtime
  Contract의 재정의(§6).
- §16.6 Workflow Adapter의 재정의(§5).
- Stage 06의 실제 설계·구현.
- `hqs/development/*.md`·`docs/architecture/baseline/BASELINE.md` 문언
  수정. Production Code 변경.

## 9. Non-goals

- 이 RFC는 Target Identification·QA Agent가 "지금 당장 Agent로
  명명·등록되어야 한다"고 주장하지 않는다 — 후보로 인정하는 것과
  Production에 반영하는 것은 다르다(Architecture Need·ADC 채택 기준
  미검증).
- 이 RFC는 Stage 04+05 조합이 유일하게 유효한 검증 대상이라고
  주장하지 않는다 — 다만 현재 코드 근거로는 가장 강하다.
- 이 RFC는 §16.6 Workflow Adapter의 Production 개시를 앞당기자고
  주장하지 않는다 — Gate (B)/(C)는 이 RFC와 무관하게 그대로다.

## 10. Governance Chain / Next Step

| 단계 | 다루는 것 |
|---|---|
| **이 RFC(Phase F-2)** | Stage 내부 작업 단위를 Agent Team 관점에서 분석, 미명명 Agent 후보 2건 발견(§3), Dependency Graph 불필요 판단(§4), §16.6 대응 관찰(§5), 최적 검증 대상 Stage 04+05 선정(§7). |
| **후속(필요 시)** | Stage 04+05 조합을 대상으로 한 격리 Experimental Implementation(Phase E `RFC-0028`과 동일 규칙) — 사용자가 별도로 요청하는 경우에만. |

## 11. Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건만 추가. `hqs/development/`·
  `core/`·`dashboard/` Production Code **무변경**.
- `grep -rn "call_engine\|call_engine_via_omniroute"
  hqs/development/mvp/*.py hqs/development/stages/*/*.py` — §2 표의
  5개 지점과 정확히 일치(정의부 제외 재확인).
- `hqs/development/mvp/workflow_ast_context.py::identify_target` 원문
  재확인 — `call_engine(prompt)` 호출 존재, 정규식 파싱은 응답 이후
  단계임을 재확인(§2 핵심 발견 근거).
- `hqs/development/mvp/agents/__init__.py` 재확인 — `qa_agent_test_execution`이
  `__all__`·`AGENT_CAPABILITY_MAP`에는 있으나 `stages/`·`workflow.py`
  호출 경로에는 없음(`RFC-0029` §3.3 재인용, 이 RFC가 다시 독립
  확인).
- `hqs/development/mvp/project_intelligence.py` 헤더 주석("규칙 기반
  Context 수집") 재확인 — Stage 01 Agent 후보 없음 판단의 근거.
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다. Phase
  E·F-1에서 이미 확인된 `hqs/development/mvp/tests/` 186 passed, 6
  skipped 기준선은 이 RFC로 변경되지 않는다.

## 12. Self Review

- Stage 전체를 Agent로 승격하는 판단을 다시 열었는가 — **아니오**
  (§0) — `RFC-0029`의 결론을 전제로 삼고 내부 단위로만 좁혔다.
- 함수/검사 하나를 이름만으로 Agent라고 인정했는가 — **아니오**(§1,
  §3) — Target Identification·QA Agent 둘 다 실제 Engine 호출 또는
  독립 전문 역할 근거로만 인정했고, 4개 결정적 검사·골격 조립·Verdict는
  전부 제외했다.
- Stage 01·05를 분석에서 제외했는가 — **아니오**(§3) — 동일한 6개
  기준으로 평가했다.
- Stage 06을 실제로 설계했는가 — **아니오**(§3 Stage 06) — 향후
  가능성만 한 문단으로 기록했다.
- Agent Domain/Lifecycle/State/Message/Event/Agent Manager/Runtime
  Contract를 새로 확정했는가 — **아니오**(§6, §8).
- §16.6 Workflow Adapter를 재정의했는가 — **아니오**(§5) — 대응
  관찰만 기록했다.
- LangGraph를 사용했는가 — **아니오** — 이 RFC는 코드를 실행하지
  않았다(분석 문서).
- Production Code(`hqs/development/`)를 변경했는가 — **아니오**(§11).
- Dependency Graph 필요성을 근거 없이 주장/부정했는가 — **아니오**
  (§4) — 관찰된 관계 유형(순차·1단계 병렬)을 근거로 불필요를
  판단했다.
