# RFC-0035: Stage 02 Planning Responsibility & Execution Model

**Status**: Proposed → 이 세션에서 ADC-0038/ADR-0023으로 이어 확정 대상
**Author**: Claude Code (사용자 요청에 따른 문서 조사 2건을 근거로 작성)
**Governance 원칙**: Outcome-Oriented(`RFC-0010`/`ADC-0008`/`ADR-0010`) —
이 RFC는 구현 허가 절차가 아니라, 이미 두 차례 문서 조사로 도출된
Architecture/Contract Decision을 기록한다. 새로운 실험이나 Open
Question 제기가 아니라, 조사 결과를 Decision으로 굳히는 것이 목적이다.

**대상**: `hqs/development/stages/contracts.py`(`SpecificationResult`),
`hqs/development/BASELINE.md`("Stage Data Contract"),
`hqs/development/stages/02_planning_specification/*.md`,
`hqs/development/stages/01_context_analysis/prd_synthesis.py`(책임
경계 확인 대상, 수정 대상 아님).

**Evidence 범위**: 이 세션에서 먼저 수행한 두 건의 문서 조사 —
(1) "Stage 02 Planning & Specification 문서 설계 확정"(Open Issue
A/B/C, Capability 정의, DAG 초안), (2) "Stage 02 LLM 호출 필요성 및
영향력 조사"(Capability별 LLM 필요성 재검증, Task Decomposition/
Acceptance Criteria가 이미 Stage 01 PRD Synthesis에서 처리되고 있다는
발견, Task&Dependency 통합 Agent 권고). 이 RFC는 그 결과를 다시
도출하지 않고 인용·확정한다.

## 0. 이 RFC가 여는 것

두 조사의 핵심 결론은 다음과 같이 수렴했다.

1. Task Decomposition과 Acceptance Criteria는 **이미** Stage 01의
   `prd_synthesis.py`(단일 Engine 호출) 안에서 생성되고 있다 — Stage
   02가 이를 다시 판단하면 재추론(RFC-0034가 금지한 패턴)이 된다.
2. Stage 02에 실제로 **존재하지 않는, 중복 없는 유일한 신규 판단**은
   Task 간 의존관계 판단(Dependency Judgment)이다.
3. Task Decomposition(구조화)과 Dependency Judgment(판단)를 별도
   Agent 2개로 쪼갤 이유가 없다 — Stage 01의 Requirement Agent가 이미
   증명한 "1회 호출·다중 구조화 필드 출력" 패턴을 그대로 따르면, **1개
   Agent가 PRD를 구조화된 Task 목록 + 의존 관계로 함께 출력**할 수 있다.
4. Dependency Ordering(위상 정렬)과 Implementation Planning(조립)은
   판단이 아니라 알고리즘/조립이므로 Deterministic Code다.
5. 이 구조화된 산출물(Task/Dependency/Plan)을 Stage 03이 나중에
   구조적으로 소비하려면 `SpecificationResult`(Public Contract,
   `ADR-0009`)에 새 키가 필요하다.

이 RFC는 이 5가지를 Architecture/Contract Decision으로 공식화한다.

## 1. Decision — Task & Dependency Agent 도입

**Accept.** Stage 02에 정확히 1개의 신규 Agent(가칭 "Task & Dependency
Agent")를 도입한다.

- **입력**: Stage 01의 `prd`(`specification` prose, `skeleton`).
  Structured Understanding이나 Repository Context를 다시 참조하지
  않는다 — PRD 자체가 이미 그것들을 종합한 결과이기 때문이다(재종합
  금지, RFC-0034 §"Synthesis 원칙"과 동일 정신).
- **출력**: 구조화된 Task 목록과 Task 간 의존 관계(그래프)를 **하나의
  JSON**으로 함께 산출한다.
- **판단 내용**: (a) PRD를 구현 가능한 Task 단위로 나누는 것(경계·개수·
  설명), (b) 어떤 Task가 어떤 Task의 완료를 전제로 하는지(pairwise
  의존).
- **호출 횟수**: 정확히 1회 — 이 Agent만으로 Task Decomposition과
  Dependency Judgment 두 판단을 모두 커버한다. **별도 Task Agent와
  별도 Dependency Agent로 분리하지 않는다.**
- **재사용 관계**: Stage 01의 기존 4개 Agent(Intent/Goal/Requirement/
  Ambiguity)나 Requirements Agent(`requirements_agent_requirement_
  analysis`)를 중복 생성하지 않는다 — 이 Agent는 그것들과 다른 신규
  판단(Task 간 의존)을 담당하는, 완전히 별개의 새 함수다.

**Rejected 대안**: "Task Decomposition Agent"와 "Dependency Judgment
Agent"를 별도 2개로 분리하는 안 — 이전 조사(LLM 영향력 조사 §3)가
Stage 01의 기존 패턴(1회 호출·다중 구조화 필드)과의 일관성, Multi-Engine
호출 회피(`RESPONSIBILITY.md` 반복 원칙), 재추론 회피를 근거로 이미
기각했다. 이 RFC는 그 판단을 뒤집지 않는다.

## 2. Decision — Deterministic Layer

**Accept.** Task & Dependency Agent 호출 **이후**는 전부 코드 기반
결정적 처리로 한다. 새 판단을 추가하지 않는다.

| 단계 | 책임 | LLM 여부 |
|---|---|---|
| Schema Validation | Agent 출력이 필요한 키(Task id/제목/설명, 의존 edge)를 갖췄는지 확인 | 없음 |
| Dependency Graph Validation | 의존 edge가 참조하는 Task id가 실제로 Task 목록에 존재하는지 확인(참조 무결성) | 없음 |
| Cycle Detection | 의존 그래프에 순환이 있으면 실행 불가능한 계획이므로 명시적으로 거부(`ContractViolation`류) | 없음 |
| Topological Ordering | 순환 없는 그래프를 실행 가능한 순서로 정렬(Kahn's algorithm 등 표준 알고리즘) | 없음 |
| Implementation Plan Assembly | Task 목록 + 정렬된 순서를 하나의 실행 계획 구조로 조립 | 없음 |
| Final Aggregation | 위 결과를 `SpecificationResult` 확장 키(§4)로 조립 | 없음 |

Cycle Detection은 **구조적 무결성만** 보장한다 — Task & Dependency
Agent가 "의미적으로 틀린" 의존관계를 판단했더라도(예: 실제로는 독립인
두 Task를 서로 의존한다고 오판), 그것이 순환을 만들지 않는 한 이 레이어는
잡아내지 못한다. 이는 §6(향후 재평가 조건)에서 명시적으로 기록한다 —
지금 추가 LLM 검증 단계를 두지 않는다(불필요한 Agent 확장 금지).

## 3. Decision — Acceptance Criteria는 그대로 둔다

**Accept.** Stage 01 PRD Synthesis(`prd_synthesis.py`)가 이미 생성한
Acceptance Criteria(현재 `specification` prose 내부)를 그대로 유지한다.
Stage 02는 이를 재추론하지 않고, 별도 Agent도 도입하지 않는다.

근거(LLM 영향력 조사 재확인): Acceptance Criteria는 Stage 02의 다른 어떤
신규 Capability(Task&Dependency Agent, Ordering, Planning)의 입력으로도
쓰이지 않는다 — 소비자가 없는 상태에서 구조화 비용을 들일 근거가
없다. 향후 Stage 03/05가 AC를 구조적으로 소비할 필요가 실제로
관찰되면, 그때 별도 RFC로 재론한다(지금 선제적으로 만들지 않는다).

## 4. Decision — Output Contract 확장

**Accept — Public Contract 변경.** `stages/contracts.py::
SpecificationResult`를 다음 3개 키로 확장한다(기존 `skeleton`/
`specification` 무변경 — 순수 추가).

```python
class TaskItem(TypedDict):
    id: str
    title: str
    description: str

class DependencyEdge(TypedDict):
    task: str          # 의존하는 쪽(후행 Task)의 id
    depends_on: str     # 선행되어야 하는 Task의 id


class ImplementationPlan(TypedDict):
    execution_order: list   # list[str] — Task id를 실행 가능한 순서로 나열


class SpecificationResult(TypedDict):
    skeleton: dict
    specification: str
    tasks: list          # list[TaskItem] — Task & Dependency Agent 출력(구조화 부분)
    dependencies: list    # list[DependencyEdge] — Task & Dependency Agent 출력(의존 판단 부분), Cycle Detection 통과 후
    plan: ImplementationPlan  # Deterministic Ordering + Assembly 결과
```

**필드명 결정 근거**:
- `tasks`/`dependencies`/`plan`은 사용자가 제시한 개념 이름을 그대로
  채택한다(추가 재해석 없음).
- `DependencyEdge`가 `from`/`to` 대신 `task`/`depends_on`을 쓰는 이유:
  `from`은 Python 예약어라 TypedDict 클래스 구문에 쓸 수 없고, 무엇보다
  "X가 Y에 의존한다"는 의미를 코드만 보고 오독할 위험을 줄이기 위해
  `task`(의존하는 쪽)/`depends_on`(선행 조건)으로 명시적으로 이름
  붙인다.
- `plan.execution_order`는 Task id의 목록만 담는다 — Task 상세는 이미
  `tasks`에 있으므로 중복 저장하지 않는다(단일 진실 원천 원칙).

**필수 키 집합 갱신**: `SPECIFICATION_REQUIRED_KEYS`는 기존
`("skeleton", "specification")`에서 `("skeleton", "specification",
"tasks", "dependencies", "plan")` 5개로 늘어난다. 이는 `ADR-0009`가
"Public(변경 시 RFC → ADC → ADR 필요)"으로 명시한 "5개 Stage Contract의
필수 키 집합"에 정확히 해당하는 변경이다 — Stage 01의 `prd` 키 추가
(`RFC-0034`)와 동일한 절차 대상.

**`ContextAnalysisResult`/`DesignResult`/`ImplementationResult`/
`VerificationResult`는 무변경.**

## 5. 유지되는 경계 (사용자 지시 "반드시 유지" 그대로 확인)

- Stage 01 PRD Synthesis의 책임(Structured Understanding + Repository
  Context 종합 → PRD)은 이 RFC로 변경되지 않는다.
- Stage 01의 기존 5개 Agent(Intent/Goal/Requirement/Ambiguity +
  Requirements Agent 재사용)를 중복 생성하지 않는다 — Task & Dependency
  Agent는 이들과 무관한 새 함수다.
- Acceptance Criteria 별도 Agent 금지(§3).
- Dependency Ordering은 LLM이 아니라 Deterministic Code(§2).
- Implementation Planning은 Deterministic Assembly(§2) — 추가 판단을
  넣지 않는다.
- Runtime/Scheduler/Workflow Parser/Dynamic Routing 등 Kernel 책임으로
  확장하지 않는다 — Task & Dependency Agent와 Deterministic Layer는
  Stage 02 내부의 하드코딩된 순차 호출로 구현되며(향후 실제 구현 시),
  `IMPLEMENTATION_RULES.md`의 Registry/Scheduler 금지 표를 넘지 않는다.
- ParallelRunner를 변경하지 않는다 — 이번 DAG에는 병렬 노드가 없다
  (Task&Dependency Agent 1개 → Deterministic 체인 1개, 병렬화 대상
  없음). Stage 01의 `ParallelRunner`를 그대로 재사용할 필요조차
  없다(단일 Task 실행이므로).

## 6. 향후 재평가 조건

다음이 실제로 관찰되면 이 Decision을 재검토한다(RT 성격 기록, 새 RFC
개설 조건).

1. Cycle Detection이 잡지 못하는 **의미적으로 틀린 의존 판단**이
   반복적으로(1회 관찰은 불충분) 발견되는 경우 — Dependency Judgment
   결과에 대한 추가 검증 단계(예: 별도 확인 Agent) 도입 여부를 재론.
2. Acceptance Criteria를 Stage 03/05가 구조적으로 소비할 필요가 실제
   구현 과정에서 관찰되는 경우 — 별도 구조화/Agent 여부를 재론.
3. Task 목록이 매우 커서(예: 수십 개) 단일 Engine 호출의 컨텍스트
   한계에 반복적으로 부딪히는 경우 — 분할 호출 전략을 재론(지금은
   가정하지 않는다).

## 7. Architecture Impact

**없음.** Kernel Public Contract(Jarvis OS Architecture Baseline §14),
Jarvis OS Architecture Baseline 자체는 무변경. Development HQ 내부
Scoped 결정이다(RFC-0033/RFC-0034와 동일 성격).

## 8. Contract Impact

**있음, Scoped.** `SpecificationResult`(Stage 02 Output, `ADR-0009`
Public Scope)에 3개 키 추가(§4). 나머지 4개 Stage Contract는 무변경.
Engine Adapter Contract(`ADC-0031`)도 무변경 — 여전히 단일
`call_engine_via_omniroute` 경로만 재사용.

## 9. Non-goals

- Task & Dependency Agent, Deterministic Layer의 실제 코드 구현 —
  이 RFC/ADC/ADR은 Decision만 기록한다.
- Stage 02 문서(`RESPONSIBILITY.md`/`CAPABILITIES.md`/
  `SPECIFICATION.md`)의 실제 수정 — 모순 여부만 확인하고 반영은 후속
  작업으로 남긴다.
- ParallelRunner 변경, 신규 병렬 인프라 도입.
- Agent Domain/Lifecycle/State/Message/Event Contract 재정의.
- ADC-02/09/10 등 Kernel 수준 Open Decision.

## 10. Governance Chain / Next Step

| 단계 | 내용 |
|---|---|
| 이 RFC(RFC-0035) | Task & Dependency Agent 도입, Deterministic Layer 범위, AC 유지, Contract 확장 형태(§1~§4)를 Decision으로 기록 |
| ADC-0038 | 이 RFC의 4개 Decision을 각각 Accept로 등록, Boundary(Stage 02 Planning Boundary/Task & Dependency Agent/Deterministic Ordering·Planning/Output Contract) 명시 |
| ADR-0023 | Baseline 문서 반영 대상 확정(`BASELINE.md` Stage Data Contract 절), 대안/Trade-off/재평가 조건 최종 기록 |
| 이후(별도 작업) | 실제 코드 구현, Stage 02 문서(`RESPONSIBILITY.md` 등) 갱신 — 이 RFC/ADC/ADR과 무관하게 자유 재량 |

## 11. Self Review

- 새로운 실험/측정을 수행했는가 — **아니오** — 기존 두 조사 결과만
  인용·확정.
- Task Decomposition/Dependency Judgment를 별도 Agent 2개로 분리했는가
  — **아니오**(§1).
- Acceptance Criteria에 새 Agent를 추가했는가 — **아니오**(§3).
- Dependency Ordering/Implementation Planning에 LLM 판단을 넣었는가 —
  **아니오**(§2).
- Kernel Public Contract를 변경했는가 — **아니오**(§7).
- Runtime/Scheduler/Workflow Parser/Dynamic Routing을 도입했는가 —
  **아니오**(§5).
- ParallelRunner를 변경했는가 — **아니오**(§5).
- Stage 01의 기존 Agent를 중복 생성했는가 — **아니오**(§1, §5).
