# RFC-0018: Natural-Language Request → Multi-HQ Task Decomposition

## Status

Proposed

**Author**: Claude Code (Architecture Governance 세션)
**대상**: `docs/architecture/baseline/BASELINE.md` §6(Concept Model), §16(Kernel Modules) — 이 RFC는 §6/§16을 변경하지 않는다. 후속 ADC/ADR이 필요 시 변경한다.
**Evidence 범위**: `hqs/development/mvp/`(CLI·Workflow·Context Analysis·Agent), `hqs/investment/`(Team·Entry Point) 실제 Repository 구조. 새로운 실행이나 Prototype은 만들지 않는다 — 기존 코드 읽기만으로 얻은 관찰이다.

이 RFC는 Decision을 내리지 않는다. §6이 여는 Boundary Question 하나만 개설하고, Accept/Defer/Reject 판단은 후속 ADC(가칭 ADC-0018)에 위임한다.

---

## 0. 이 RFC가 열린 이유

`docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md` →
`ADC-0017` → `ADR-0007`까지, Kernel Modules는 다음까지 좁혀졌다:

- §16.3 Execution Host — **단일** 실행 단위의 dispatch·격리
- §16.4 Multi-Task — 이미 코드/설계에 **고정된** 복수 독립 실행 단위의 동시 시작·대기·결과 수집
- §16.5 Multi-Task Result Store — 그 결과를 저장하기 전 유효성 판정 게이트

이 세 책임은 모두 "Task가 이미 정의된 뒤"의 실행 계층을 다룬다. 그런데 이번 세션에서
`hqs/development/mvp/cli.py`와 `hqs/investment/run.py`를 직접 읽는 과정에서, "그 Task가
애초에 어떻게 정의되는가"— 특히 사람이 자연어로 요청했을 때 그 요청이 어느 HQ의 어떤
Task로 바뀌는가 — 를 다루는 책임이 지금까지의 Governance Chain 어디에도 명시적으로
다뤄진 적이 없다는 것이 관찰됐다.

이 RFC는 그 관찰을 근거로, "이 변환 자체를 담당하는 공통 책임이 필요한가"를
Boundary Question으로 여는 절차다. **Conversation Layer라는 이름이나 구조를 미리
전제하지 않는다** — 그런 이름·Component가 필요한지 여부 자체가 아직 열려 있지 않은
질문이다.

---

## 1. Problem Statement

지금까지 Accept된 모든 실행 계층 책임(§16.3~§16.5)은 "Task가 이미 있다"를
전제로 시작한다. 그러나 실제 사용자는 Task 단위로 말하지 않는다 — 하나의 자연어
문장 안에 서로 다른 HQ에 속하는 서로 다른 목적의 작업이 섞여 있을 수 있다.

예: "AAPL 투자 분석과 현재 Jarvis OS 개발 상태 분석을 각각 수행해줘."

이 한 문장은 다음을 암묵적으로 요구한다:

1. 이 문장에 두 개의 독립적인 작업이 들어 있다는 것을 식별
2. 각 작업이 Investment HQ / Development HQ 중 어디에 속하는지 식별
3. 각 작업을 그 HQ가 실행할 수 있는 형태(Task)로 변환
4. 변환된 Task를 실제로 실행할 기존 Agent/Team에 연결

이 네 단계 중 어느 것이 현재 코드에 이미 존재하는지, 존재하지 않는다면 그것이
Kernel 책임으로 다뤄져야 하는지는 지금까지 열린 적이 없다. §16.3~§16.5는 모두
4번 이후(Task가 확정된 뒤)만 다룬다.

---

## 2. Existing Architecture

이 RFC가 전제로 삼고 절대 뒤집지 않는 기존 확정 경계:

**Execution Host (§16.3, `RFC-0013`→`ADC-0013`→`ADR-0003`, 명칭 `ADC-0014`→`ADR-0004`,
구현 전략 `ADC-0015`→`ADR-0005`)**
- 이미 identity/lifecycle이 확정된 **단일** Task를 받아 실행을 시작하고 격리를 제공하는 책임.
- Process 1차, Subprocess 대안, "동일 Target 동시 실행" 조건에서 Thread 배제.
- Scheduler/Multi-Task/Workflow orchestration을 결정하지 않는다.

**Multi-Task (§16.4, `RFC-0016`→`ADC-0016`→`ADR-0006`)**
- 서로 입력 독립·출력 비의존인, **이미 코드/설계에 고정된** 소수 실행 단위의 동시
  시작·대기·결과 수집.
- Data/Artifact Isolation이 사전에 확인된 조합에만 적용.
- 기존 Agent 재사용을 전제 — 동적 Task→Agent 할당은 제외.
- Scheduler/우선순위/Workflow orchestration/넓은 Runtime은 제외.

**Result Store / Checkpoint Integrity (§16.5, `RFC-0017`→`ADC-0017`→`ADR-0007`)**
- 저장 전 결과 유효성 판정 및 저장 차단 게이트.
- Investment HQ `Checkpointer`/`run_step`에 한정된 실증 사례.
- Resume 재검증, Retry/Alert/Recovery 정책은 제외.

**ADC-02 (Runtime 개념의 존폐, `docs/decisions/adc/ADC.md`)**
- **여전히 Open**. §6 Concept Model의 "Runtime"(Workflow 참조, Task를 Agent에게 배분,
  Scheduler를 포함하는 넓은 정의)은 §16.3~§16.5의 어느 Accept로도 변경되지 않았다.
- 이 RFC는 ADC-02 자체를 변경하지 않는다.

이 위 세 책임과 ADC-02의 관계에서, 이 RFC가 여는 질문은 그 어떤 것도 다시 열지
않는다 — Task가 **어떻게 만들어지는지**를 다루는, 그 앞 단계의 질문이다.

---

## 3. Observed Multi-HQ Request Scenario

다음 자연어 요청을 대표 Evidence/Scenario로 사용한다(실제로 실행하지 않았다 —
현재 코드가 이런 요청을 애초에 받을 수 있는 입구조차 없기 때문이다):

> "AAPL 투자 분석과 현재 Jarvis OS 개발 상태 분석을 각각 수행해줘."

이 요청은 의도적으로 Task 간 의존성이 없는 독립 Multi-HQ 요청이다. 예상되는 의미
구조는 다음과 같다 — 그러나 이는 **검증을 위한 가설**일 뿐, 이 RFC가 확정하는
Architecture가 아니다.

```
User Request
    │
    ▼
   ???  ← 이 RFC의 Boundary Question이 겨냥하는 지점
    │
    ├──────────────────────┬──────────────────────┐
    ▼                      ▼
Investment HQ          Development HQ
  AAPL 분석            개발 상태 분석
    │                      │
    ▼                      ▼
Investment Task        Development Task
    │                      │
    ▼                      ▼
Existing Team           Existing Agent
    │                      │
    └──────────┬───────────┘
               ▼
           Multi-Task (§16.4)
```

"???" 위치에 무엇이 필요한지 — 하나의 Component인지, 여러 책임의 조합인지, 아니면
현재 구조로 이미 충분한지 — 가 §6의 Boundary Question이다.

---

## 4. Existing Responsibility Mapping

아래 7개 책임을 서로 섞지 않고 각각 조사했다. "존재"는 그 책임을 수행하는 코드가
실제로 존재함을, "미확인"은 조사 범위에서 그런 코드를 찾지 못했음을 뜻한다.

| 책임 | 정의 | 현재 존재 여부 | Evidence |
|---|---|---|---|
| Request Interpretation | 자연어 사용자 요청에서 사용자의 의도/목적을 구조화 | 미확인 | `hqs/development/mvp/cli.py`는 파일/stdin의 원문(code)을 그대로 `run_mvp_0001(code)`에 전달한다 — "무엇을 원하는가"를 해석하는 코드가 없다. `hqs/investment/run.py`는 `team`을 CLI 인자로 **호출자가 이미 알고 지정**해야 받는다(§5.E). |
| HQ Routing | 어떤 HQ가 요청의 일부를 담당하는지 식별 | 미확인 | 두 HQ 모두 호출자가 이미 특정 HQ의 진입점을 직접 호출하는 구조다. HQ 간 선택을 대신 해주는 코드가 없다. |
| Task Decomposition | 하나의 요청을 실행 가능한 Task 단위로 분해 | 미확인 | `run_comparison()`의 두 분기(`run_issue_to_planning`/`run_issue_to_planning_with_bundle`)는 이미 코드에 고정된 두 개의 Task이지, 자연어 요청을 분해해 만들어진 것이 아니다(§5.B). |
| Agent Assignment | Task를 기존 어떤 Agent/Team/Capability가 수행할지 결정 | 부분 존재(정적) | `hqs/investment/run.py`의 `TEAMS` 딕셔너리(§5.E), `hqs/development/mvp/agents/`의 Agent 함수(§5.D)는 모두 **리터럴 매핑**으로 이미 존재한다. 그러나 "어떤 요청이 어떤 Agent/Team으로 가야 하는지"를 자연어에서 자동으로 결정하는 로직은 없다 — 호출자가 이미 알고 지정한다. |
| HQ Context Analysis | 각 HQ가 실제 작업에 필요한 전문 Context를 구성 | 존재 | `hqs/development/mvp/project_intelligence.py`의 `build_context_bundle()`이 Goal/Relevant Documents/Relevant Code/Relevant Observations/Relevant Decisions/Known Constraints/Open Questions를 구성한다(§5.C). 단, 입력은 이미 구조화된 `issue: dict`이지 자연어 원문이 아니다. |
| Multi-Task | 이미 정의된 독립 Task들을 동시에 시작하고 결과를 수집 | 존재(Accept, §16.4) | `hqs/development/mvp/workflow_0009.py`의 `run_comparison()` — `ThreadPoolExecutor`로 두 개의 **이미 고정된** Task를 동시 실행한다. |
| Execution Host | 개별 실행 단위의 격리 | 존재(Accept, §16.3) | `ADC-0013`~`ADR-0005` Governance Chain으로 확정. |

---

## 5. Evidence

### A. Development HQ 진입 구조 — `hqs/development/mvp/cli.py`

```python
def main() -> None:
    ...
    code = f.read()  # 또는 stdin
    result = run_mvp_0001(code)
```

CLI는 입력을 그대로 `run_mvp_0001(code)`에 전달한다. 진입자는 이미 "MVP-0001
Workflow를 실행한다"는 것을 알고 있다 — 어떤 Workflow를 실행할지 자연어에서 판단하는
코드가 없다.

### B. Development HQ Workflow — `workflow.py`, `workflow_0009.py`

`workflow.py`의 `run_mvp_0001()`은 `backend_agent_code_review` → `qa_agent_test_execution`을
순서대로 호출하는, 완전히 하드코딩된 2-Task Workflow다(파일 자체 docstring: "직접
함수 호출로 하드코딩").

`workflow_0009.py`의 `run_comparison(issue: dict)`은 `ThreadPoolExecutor(max_workers=2)`로
`run_issue_to_planning`과 `run_issue_to_planning_with_bundle`을 병렬 실행한다. 이 두
분기는 코드에 이미 정의돼 있고, `issue`는 `workflow_0008.py`의 `REAL_ISSUE`(리터럴
딕셔너리) 또는 그에 준하는 구조화된 값이다 — **자연어 문자열이 아니다**.

→ 이것은 Multi-Task 실행 계층(§16.4)이 존재한다는 Evidence이지, 자연어 요청을
Task로 분해하는 상위 계층이 존재한다는 Evidence가 아니다.

### C. Development HQ Context Analysis — `project_intelligence.py`

`build_context_bundle(issue: dict)`은 다음을 구성한다:

```python
def build_context_bundle(issue: dict) -> dict:
    ...
```

`validate_issue()`, `collect_relevant_context()`를 거쳐 Goal/Relevant Documents/
Relevant Code/Relevant Observations/Relevant Decisions/Known Constraints/Open
Questions를 채운다. 입력은 이미 `{"title": ..., "description": ..., "status": ...}`
형태로 구조화된 `issue`다.

**핵심 구분**: 이 책임은 "이 HQ가 이 작업을 수행하려면 어떤 Context가 필요한가"(HQ-level)를
다룬다. "사용자가 무엇을 원하는가"(Conversation-level)를 자연어에서 읽어내는 책임과는
다르다 — `build_context_bundle()`의 입력 자체가 이미 그 판단이 끝난 `issue`이기 때문이다.
이 RFC는 이 둘을 혼동하지 않는다.

### D. Development Agent — `hqs/development/mvp/agents/`

`backend.py`, `design.py`, `qa.py`, `requirements.py` 각각 명시적인 함수
(`backend_agent_code_review`, `qa_agent_test_execution` 등)를 노출한다. 모두 이미
정해진 입력 형태(코드 문자열, `issue` 딕셔너리 등)를 받아 실행하는 구조다. 자연어
요청을 직접 해석하는 Agent는 없다 — 새 Agent가 필요하다는 결론은 이 Evidence만으로
내리지 않는다.

### E. Investment HQ — `hqs/investment/run.py`, `teams/`

```python
TEAMS = {
    "stock": stock_team,
    "etf": etf_team,
    "dividend_stock": dividend_stock_team,
}

def main():
    team_key, company_label, raw_data_path, issue_dir = sys.argv[1:5]
    ...
    result = team.run(company_label, Path(raw_data_path), issue_dir_path)
```

호출자가 `team`(stock/etf/dividend_stock)을 **CLI 인자로 직접 지정**해야 한다.
"AAPL 투자 분석"이라는 자연어에서 `team_key = "stock"`을 자동으로 판별하는 코드는
없다 — 사람이 이미 그 판단을 내린 뒤 인자로 넘긴다.

`hqs/investment/STRUCTURE.md`의 금지 사항 표에도 "Multi-HQ 지원 코드 작성 금지"에
준하는 원칙은 명시돼 있지 않지만, `hqs/development/IMPLEMENTATION_RULES.md`의
"Multi-HQ 지원 코드 작성 금지 | MVP는 Development HQ 단독 시나리오만 다룬다"(다음
문단 F 참조)가 Dev HQ MVP 범위 안에서는 이미 명시적으로 이 책임을 배제하고 있다.

### F. `hqs/development/IMPLEMENTATION_RULES.md`의 명시적 금지

```
| Multi-HQ 지원 코드 작성 금지 | MVP는 Development HQ 단독 시나리오만 다룬다 |
```

이 금지는 **Development HQ MVP-0001의 자체 범위 선언**이다(파일 자체가 "MVP-0001"에
self-scoped, `CLAUDE.md`·`hqs/development/BASELINE.md` 참조) — Multi-HQ 조율 책임을
Kernel 수준에서 금지하는 것이 아니라, 그 책임이 Dev HQ MVP의 몫이 아니라는 뜻이다.
이 RFC가 여는 질문("공통 책임이 필요한가")은 이 금지와 충돌하지 않는다 — 오히려 이
금지 자체가 "이 책임은 지금 어디에도 없다"는 것을 뒷받침하는 추가 Evidence다.

### G. 정리 — 사실과 추론의 구분

**사실로 기록할 수 있는 것**:
- 현재 CLI(`cli.py`)는 특정 Workflow(`run_mvp_0001`)를 직접 호출한다.
- `run_comparison()`은 이미 정의된 독립 Task 두 개를 병렬 실행한다 — Task 자체를
  만들어내지 않는다.
- Dev HQ Context Analysis(`build_context_bundle`)는 존재하지만 입력은 이미 구조화된
  `issue`다.
- Agent/Capability(Dev HQ `agents/`, Investment HQ `teams/`)는 존재한다.
- 자연어 → Multi-HQ → Task를 담당하는 공통 계층은 조사 범위에서 확인되지 않았다.
- Investment HQ와 Development HQ는 각각 독립적인 실행 구조를 가지며, 서로의 진입점을
  호출하지 않는다.
- Dev HQ `IMPLEMENTATION_RULES.md`는 Multi-HQ 지원 코드를 자체 범위 밖으로
  명시적으로 배제하고 있다.

**아직 Decision이 아닌 것**(이 RFC가 결정하지 않는 것):
- Conversation Layer가 반드시 필요하다.
- HQ Router가 반드시 별도 Component여야 한다.
- Task Planner가 필요하다.
- Agent Assignment를 자동화해야 한다.
- 위 7개 책임 중 무엇을 하나로 묶고 무엇을 분리해야 하는지.

---

## 6. Boundary Question

이 RFC는 단 하나의 질문만 연다:

> **하나의 자연어 사용자 요청에서 복수 HQ와 독립 Task를 식별하고, 이를 실행 가능한
> 구조화 요청으로 변환하는 공통 책임이 필요한가?**

### 이 Boundary Question이 명시적으로 제외하는 것

- "Conversation Layer를 만들 것인가?"라는 질문이 **아니다** — 이름도, Component
  존재도 전제하지 않는다.
- Request Interpretation·HQ Routing·Task Decomposition·Agent Assignment 4개
  책임을 하나로 묶을지 여부를 미리 정하지 않는다(§4의 매핑은 조사 결과일 뿐 결합
  여부의 결론이 아니다).
- 이 책임이 필요하다고 판단되더라도, 그 구현 전략(Rule 기반/Engine 호출/기타)을
  이 RFC는 다루지 않는다.

---

## 7. Relationship to Existing Concepts

**Execution Host (§16.3)**: 이 RFC가 여는 책임은 Task가 확정되기 **이전** 단계를
다룬다. Execution Host는 Task가 이미 확정된 **이후** 단일 실행 단위의 dispatch·격리를
다룬다. 두 책임은 시간축 상 서로 다른 지점이며, 이 RFC는 §16.3의 범위를 전혀
넓히지 않는다.

**Multi-Task (§16.4)**: §16.4는 "이미 코드/설계에 고정된" Task를 전제로 시작한다.
이 RFC의 질문은 "Multi-Task가 필요한가"가 아니라 **"Multi-Task에 전달할 Task를
누가/어떻게 만들어내는가"**다. 관계는 다음과 같다:

```
Request Decomposition (이 RFC가 여는 질문)
        │
        ▼
Independent Tasks
        │
        ▼
Multi-Task (§16.4, 이미 Accept·Production 적용됨)
        │
        ▼
Execution (§16.3)
```

§16.4의 Accept 범위·조건(기존 Agent 재사용, Data/Artifact Isolation, 동적 할당
제외 등)은 이 RFC로 전혀 재검토되지 않는다.

**Dev HQ Context Analysis (`build_context_bundle`)**: §5.C에서 확인했듯, 이 책임은
"이미 결정된 작업에 어떤 Context가 필요한가"(HQ-level)를 다룬다. 이 RFC의 질문인
"사용자가 무엇을 원하는가"(Conversation-level)와는 다른 층위다. 이 RFC는 두 책임을
합칠지 분리할지 결정하지 않는다 — 그 판단은 후속 ADC로 넘긴다.

**§6 Runtime / ADC-02**: `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 개념의 존폐)는
여전히 Open이다. §6의 넓은 Runtime 정의(Workflow 참조, Task를 Agent에게 배분,
Scheduler 포함)와 이번에 논의되는 상위 요청 조율 책임은 개념적으로 일부 겹칠
가능성이 있다는 것을 기록해 둔다. 그러나 다음을 구분한다:

- **이 RFC**: 자연어 요청 → 복수 HQ/독립 Task 구조화라는 최소 Boundary.
- **§6 Runtime**: Workflow 참조, Task 배분, Scheduler 등 더 넓은 개념.

이 RFC는 §6 Runtime 전체의 존폐나 구조를 결정하지 않으며, ADC-02를 대체하거나
종결하지 않는다.

**Agent/Capability**: §5.D·§4에서 확인했듯 기존 Agent/Team은 이미 명시적 입력을
받아 실행하는 구조다. 이 RFC는 새 Agent가 필요하다는 결론을 내리지 않으며, 기존
Agent/Team을 그대로 재사용할 수 있는지는 후속 ADC의 판단 대상이다.

---

## 8. Out of Scope

이 RFC는 다음을 결정하지 않는다:

- Conversation Layer라는 이름 확정
- Conversation Layer Component 확정
- HQ Router Component 확정
- Task Planner Component 확정
- Agent Manager 변경
- 새로운 Public Interface
- 새로운 Agent
- 새로운 Capability
- Scheduler
- 우선순위
- Retry
- Recovery
- Workflow orchestration
- 넓은 Runtime 구현
- Execution Host 확장
- Multi-Task 범위 확장
- Dashboard UI 구현
- "Result Aggregator" 등 결과 결합을 위한 새 Component

특히, "Conversation Layer가 Request Interpretation + HQ Routing + Task
Decomposition + Agent Assignment를 모두 담당한다"고 이 RFC는 결정하지 않는다.
그것은 후속 ADC가 판단해야 한다.

---

## Non-goals

- 이 RFC는 §6의 Boundary Question에 답하지 않는다.
- 이 RFC는 Production Code를 작성·수정하지 않는다.
- 이 RFC는 §3의 Prototype Scenario를 실제로 실행하지 않는다 — 순수하게 현재 코드
  구조를 읽어 만든 가설이다.
- 이 RFC는 결과 결합(여러 HQ의 Task 결과를 하나의 사용자 응답으로 결합하는 책임)이
  이번 Boundary의 일부인지 결론 내리지 않는다 — Evidence가 없으므로 §9의 Open
  Question으로 남긴다.

---

## 9. Open Questions for ADC

후속 ADC(가칭 ADC-0018)가 판단할 항목:

**Q1.** 현재 Jarvis OS는 하나의 자연어 요청에서 복수 HQ를 식별할 수 있는 명시적
공통 책임을 이미 가지고 있는가? — (§4·§5 Evidence: 미확인)

**Q2.** 현재 구조에서 하나의 자연어 요청을 복수 Task로 표현할 수 있는가? — (§5.B
Evidence: `run_comparison()`은 이미 고정된 Task만 병렬 실행하며, 자연어에서 Task를
만들어내지 않는다)

**Q3.** HQ 선택과 Task 분해를 담당하는 기존 Component/Function이 있는가? — (§5.A·E
Evidence: 없음. 호출자가 이미 HQ와 Workflow를 알고 직접 지정한다)

**Q4.** 기존 Agent/Team 구조를 그대로 재사용할 수 있는가? — (§5.D·E Evidence: 기존
Agent/Team은 이미 명시적 입력을 받는 구조이므로 재사용 가능성이 있어 보이나, ADC가
직접 판단해야 한다)

**Q5.** Dev HQ의 `build_context_bundle()` 같은 HQ-specific Context Analysis를
Conversation-level 책임과 분리할 수 있는가? — (§5.C·§7 Evidence: 입력 층위가 이미
다르다는 것은 확인됐으나, 분리 가능성 자체의 최종 판단은 ADC 몫이다)

**Q6.** 독립적인 Multi-HQ Task가 이미 확정된 §16.4 Multi-Task 범위로 전달될 수
있는가?

**Q7.** 현재 구조에서 이 변환을 수행하려면 어떤 책임이 새롭게 필요해지는가?

추가로 다음도 후속 ADC의 판단 대상이다:

- 해당 공통 책임의 필요성 Accept/Defer/Reject
- Request Interpretation / HQ Routing / Task Decomposition의 경계
- 하나의 Component로 묶을지 분리할지
- Agent Assignment를 포함할지
- 결과 결합 책임을 포함할지
- §6 Runtime과의 정확한 관계
- 기존 Agent/Team 재사용 여부
- Public Contract 필요 여부

---

## 10. Next Step

이 RFC는 Decision을 내리지 않는다. §6의 Boundary Question에 대한 판단(Accept/
Defer/Reject)과 §9의 Open Questions는 모두 후속 ADC(가칭 ADC-0018)로 넘긴다. ADC가
Evidence 부족을 이유로 판단을 미루는 것도, Evidence가 이미 충분하다고 판단해
Accept/Reject하는 것도 모두 ADC의 권한이다 — 이 RFC는 그 판단을 선점하지 않는다.

---

## Self Review

- [x] §4의 책임 매핑 7개 항목 모두 실제 파일 근거(§5)로 뒷받침됐다.
- [x] "존재/미확인/부분 존재" 판정은 관찰(코드 읽기)에 기반하며, 추론(Component가
      필요하다는 결론)과 섞이지 않았다.
- [x] Execution Host(§16.3)·Multi-Task(§16.4)·Result Store(§16.5)의 기존 확정
      경계를 다시 열지 않았다 — §7에서 관계만 정리했다.
- [x] ADC-02(Runtime 존폐)는 Open 상태 그대로 인용만 했다 — 변경하지 않았다.
- [x] Conversation Layer/HQ Router/Task Planner 등 어떤 Component 이름도
      Decision으로 확정하지 않았다 — §3·§6·§8에서 반복적으로 "가설"임을 명시했다.
- [x] Production Code를 읽기만 했고 수정하지 않았다(`git status` 확인 예정).
- [x] BASELINE.md·IMPLEMENTATION_RULES.md·ADC.md를 수정하지 않았다.
- [x] §3의 Prototype Scenario는 실제 실행 없이 코드 구조 조사만으로 구성된 가설임을
      명시했다.
