# ADC-0016: Multi-Task 최소 책임(독립 Task 동시 실행·결과 수집) 존재 여부 판단 (RFC-0016 후속)

## 목적

`docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md`
§8 Boundary Question — **"Jarvis OS는 서로 독립적인(입력 독립·출력
비의존) 복수 Task를 동시에 실행하고 그 결과를 수집하는 책임을,
Execution Host(§16.3)와 별개의 Kernel Concept으로 Accept하는가?"** —
에 대해 판단한다.

근거는 RFC-0016과 그것이 인용한 Evidence(`hqs/development/mvp/workflow_0009.py`
현재 `main`, `docs/architecture/baseline/BASELINE.md` §6·§16.3,
`docs/decisions/adc/ADC.md` ADC-02, `ADC-0013`/`ADR-0003`,
`ADC-0015`/`ADR-0005`, `hqs/development/IMPLEMENTATION_RULES.md`)로만
한정한다. 새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Scheduler, 우선순위, Workflow orchestration 설계.
- `BASELINE.md` §6의 넓은 정의(Workflow 참조, Task를 Agent에게 배분)
  전체의 채택 또는 검증 — 이 ADC는 그 정의의 일부만 판단한다.
- Multi-Task의 명칭 확정.
- 구현 전략(`ThreadPoolExecutor`/`asyncio` 등) 확정.
- §4가 나열한 위험(파일 덮어쓰기, Artifact/Result 충돌, 공유 상태,
  Git 충돌, Retry 충돌)의 구체적 해소 방법 설계 — 최소 안전조건으로
  다룰 뿐, 해법을 설계하지 않는다.
- Execution Host(§16.3)의 존재·명칭·범위(`ADC-0013`/`ADR-0003`,
  `ADC-0014`/`ADR-0004`, `ADC-0015`/`ADR-0005`가 이미 확정) 재론.
- `docs/decisions/adc/ADC.md`의 ADC-02(Open) 항목 자체 수정.
- Production Code(`hqs/`, `core/`, `dashboard/`) 수정.

이 ADC가 판단하는 것은 다섯이다: **(1) RFC-0016 §8이 좁힌 범위 —
독립 Task 동시 실행·결과 수집 책임의 존재 여부, (2) 그 책임과
Execution Host의 경계, (3) Data/Artifact Isolation을 이 책임의 최소
안전조건으로 어떻게 반영할지, (4) Task→Agent 할당이 이 범위에
필요한지, (5) `IMPLEMENTATION_RULES.md`의 금지 범위를 이 시점에
조정할지.**

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가

### Evidence

- `BASELINE.md` §6: Runtime을 `Service`로 등재하며 "Task를 Agent에게
  배분한다"는 정의를 두었으나, 세부 구조는 ADC-02(Open)로 유보했다.
- `BASELINE.md` §16.3: Execution Host Accept가 "Multi-Task를 Agent에게
  배분"으로의 확장 여부를 스스로 결정하지 않는다고 명시했다.

### Q0 결론

Intent는 "실행 조율과 관련된 무언가가 필요할 수 있다"는 신호만 줄 뿐,
그 정체나 범위를 스스로 판단하지 못한다 — `ADC-0013` Q0과 동일한
구조. **Architecture Intent만으로는 지금 판단할 수 없다.**

---

## Q1. 실제 필요성 — MVP-0009가 보여주는 것

### Evidence

`hqs/development/mvp/workflow_0009.py:56-66`의 `run_comparison`은
다음 성질을 실제 Production Code(이미 `main`에 병합)로 보여준다.

1. `flat = run_issue_to_planning(issue)`와
   `bundled = run_issue_to_planning_with_bundle(issue)`는 서로의
   출력에 의존하지 않는다 — 입력 독립·출력 비의존.
2. 각 분기는 `requirements_agent_requirement_analysis` → `call_engine()`
   → `subprocess.run()`(최대 180초)을 포함해, 순차 실행 시 불필요한
   지연이 실제로 발생한다.
3. 병렬화해도 `run_comparison`의 반환 계약이나 의미가 전혀 바뀌지
   않는다 — 오히려 "우열 없이 나란히 비교"라는 함수의 원래 취지에
   더 부합한다(RFC-0016 §1).
4. 이를 표현할 기존 Concept이 없다 — Task는 조율을 표현하지 않고,
   Execution Host는 이미 dispatch가 결정된 **단일** 실행 단위의
   격리만 다룬다(`ADC-0015` §Out of Scope가 Multi-Task 확장을 명시
   배제).

### Q1 결론

이 관찰이 답하는 질문은 RFC-0016 §8이 좁힌 그대로다: **"서로
독립적인 복수 Task를 동시에 실행하고 결과를 수집하는 책임이 실제로
필요한가."** 이 좁은 질문에 한해서는, 실제 Production Code 1건이
필요성을 직접 보여준다.

---

## Q2. 관찰 1건뿐이라는 것이 Accept를 막는가 — Evidence 부족과 필요성의 관계

### 검토

RFC-0016의 근거는 `ADC-0013`의 5개 Prototype 묶음과 달리 실제
관찰이 **1건**(`workflow_0009.py`)뿐이다. 형식적으로는 Governance
v2 Rule B(3건 이상 독립 관찰) 기준에 크게 못 미친다.

이 작업의 작업 지시 §8은 "필요성이 충분하면 Evidence 부족을 이유로
불필요하게 Defer하지 않는다"고 명시한다. `ADC-0013` Q2가 이미 세운
기준을 그대로 적용한다 — **Rule B가 겨냥하는 위험**(범위가 넓고
돌이키기 어려운 결정을, 우연한 관찰만으로 성급히 확정하는 것)이
이 판단 대상에도 실제로 존재하는지를 먼저 확인한다.

- 이 ADC가 판단하는 범위는 RFC-0016 §8이 이미 극도로 좁혀 놓았다 —
  Scheduler, 우선순위, Workflow orchestration, §6의 넓은 정의(Agent
  배분 로직 포함)를 전부 범위 밖으로 제외했다. 남는 것은 "이미
  코드에 고정된, 서로 독립적인 소수 호출을 동시에 시작하고 결과를
  모은다"는 조율 하나뿐이다.
- 이 좁은 범위 안에서, 관찰이 1건이라는 사실 자체는 부정할 수 없다
  — 그러나 그 1건은 **가상 시나리오가 아니라 이미 `main`에 병합된
  실제 Production Code**다(RFC-0016 §1 인용). "우연히 관찰된 것"이
  아니라 "이미 존재하는 것"이라는 점에서, Rule B가 막으려는 "우연한
  관찰에 기반한 성급한 결론"과는 성격이 다르다.
- 반대로, 이 관찰 1건만으로 검증되지 않은 것도 명확히 남아 있다 —
  §4가 나열한 Data/Artifact Isolation 위험은 `workflow_0009.py`
  사례에서 우연히 드러나지 않았을 뿐(파일 쓰기가 없어서), 다른 Task
  조합에서는 실제로 발생할 수 있다(RFC-0016 §4). 이 공백은 "존재
  여부" 판단과는 별개로 반드시 조건으로 남아야 한다(§Q4).

### Q2 결론

**관찰 1건이라는 형식적 부족은, RFC-0016이 스스로 좁힌 범위(이미
존재하는 실제 코드에 대한 조율 책임 하나) 안에서는 Accept 자체를
막을 만큼 결정적이지 않다.** 다만 그 부족은 사라지지 않는다 —
Data/Artifact Isolation처럼 이 1건이 검증하지 못한 위험은 Accept의
**조건**(§Q4, Implementation Boundary)으로 명시적으로 이월한다.
"존재는 Accept하되, 안전조건은 미해결로 남긴다"는 이 구분이 Evidence
부족을 무시하지 않으면서도 불필요한 Defer를 피하는 방법이다.

---

## Q3. Execution Host와 Multi-Task의 책임 경계 확정

### 검토

RFC-0016 §2·§5가 이미 제시한 구분을 이 ADC가 Decision으로 확정한다.

| | Execution Host(§16.3, 기확정) | Multi-Task(이 ADC가 판단) |
|---|---|---|
| 다루는 문제 | **Execution Isolation** — 이미 dispatch된 단일 실행 단위가 동일 Target 동시 실행에서도 상태 오염 없이 정확하게 실행되는가 | **Coordination** — 서로 독립적인 여러 실행 단위를 언제 동시에 시작하고, 언제 전부 끝났다고 판단하며, 결과를 어떻게 모으는가 |
| 대상 개수 | 단일(1개) | 복수(2개 이상, 서로 독립) |
| `workflow_0009.py`와의 대응 | `run_issue_to_planning`/`run_issue_to_planning_with_bundle` 각각의 내부 실행 — 이미 Execution Host 대상 아님(`call_engine()`이 독립 subprocess로 이미 격리) | `run_comparison`이 이 둘을 동시에 시작하고 모으는 지점 |
| 관계 | 서로 배타적이지 않다 — 향후 "동일 Target을 여러 번 동시 실행"하는 Multi-Task 사례가 생기면, Multi-Task가 각 실행을 Execution Host에 위임하는 조합도 가능(이 ADC는 그 조합을 설계하지 않는다) | |

### Q3 결론

**두 책임은 명확히 분리된 채로 확정한다.** Execution Host의 범위
(§16.3, "단일 실행 단위", Multi-Task 제외)는 이 ADC로 전혀 넓어지지
않는다 — 이는 `ADC-0015` §Out of Scope가 이미 명시한 배제를 그대로
유지하는 것이다. Multi-Task는 Execution Host의 확장이 아니라, §6
Runtime 정의 중 "조율" 부분에 해당하는 **별개의, 더 좁은** Concept
후보로 취급한다.

---

## Q4. Data/Artifact Isolation을 최소 안전조건으로 반영

### 검토

RFC-0016 §5가 구분한 두 문제 중, Execution Isolation은 이미 Execution
Host가 다루고(Q3), 이 ADC가 새로 판단하는 것은 **Data/Artifact
Isolation**(동시 실행되는 여러 Task가 파일·Artifact·Git 작업 트리
같은 **결과물**을 서로 덮어쓰지 않는가) 하나다.

`workflow_0009.py` 사례는 이 위험이 우연히 드러나지 않는다(파일
쓰기, 공유 Artifact 이름공간이 없음) — 그러나 "이번 사례에 없었다"는
것이 "이 위험이 이 책임에 없다"는 뜻은 아니다. RFC-0016 §4가 나열한
5개 위험(파일 덮어쓰기, Artifact/Result 충돌, 공유 상태, Git 충돌,
Retry 충돌) 중 상당수는 미래의 다른 Task 조합(예: 코드 생성 결과를
파일로 반영하는 Task)에서 실제로 발생할 수 있다.

**판단**: 이 위험을 지금 전부 해소할 필요는 없다 — RFC-0016도, 이
ADC도 해법을 설계하지 않는다. 그러나 이 책임을 "존재"로 Accept하면서
이 위험을 침묵하면, 후속 구현이 §4의 위험을 검증 없이 지나칠 수
있다. 따라서 **Data/Artifact Isolation을 이 책임의 최소 안전조건으로
명시**한다 — 즉, 향후 이 책임을 실제로 구현·연결하는 어떤 Task
조합이든, "동시 실행되는 각 Task가 서로 다른 파일/Artifact 이름공간에
쓰거나, 아무것도 쓰지 않는다"는 것이 사전에 확인되지 않으면 이
Accept의 범위를 벗어난 것으로 취급한다. `workflow_0009.py`처럼
결과가 메모리 dict로만 결합되는 조합은 이 조건을 이미 충족한다.

### Q4 결론

**Data/Artifact Isolation을 이 책임의 최소 안전조건(Minimum Safety
Precondition)으로 Accept에 포함한다.** 이는 "이번 Accept가 어떤
Task 조합에나 무조건 적용되는 것이 아니라, 이 조건을 만족하는 조합
(§4 위험이 없거나 사전에 회피된 조합)에만 적용된다"는 뜻이며,
해소 방법 설계는 후속 절차(ADR/구현 지침 또는 필요 시 별도 RFC)로
넘긴다.

---

## Q5. Task→Agent 할당 — 기존 Agent 재사용과 동적 할당 분리

### 검토

`run_comparison`의 두 분기는 **같은 Capability**(Requirements Agent)
를 서로 다른 입력으로 두 번 호출할 뿐이다(RFC-0016 §6). 이 범위에서는
"어떤 Task를 어떤 Agent에게 배분할지 결정"하는 로직이 전혀 필요하지
않다 — 호출할 Agent 함수는 이미 코드에 고정돼 있다.

### Q5 결론

**기존 Agent 재사용을 이 책임의 전제로 삼는다 — 새 Agent나 Capability
도입, 동적 Task→Agent 할당 로직은 이 Accept에 포함하지 않는다.** 이
분리는 `IMPLEMENTATION_RULES.md`의 "새 Capability/Agent 추가 금지"
및 "Registry 일반화 금지"와도 일치한다 — Multi-Task 존재를 Accept
한다고 해서 Agent 선택을 동적으로 만들 근거가 생기는 것은 아니다.

---

## Q6. §6 Runtime 전체를 결정하거나 확장하는가

### 검토

`BASELINE.md` §6은 Runtime을 "Workflow를 참조하여 Task를 Agent에게
배분하는" Service로 정의한다. 이 ADC가 Accept하는 범위(§Q1·§Q3)는
그중 "이미 정해진 소수의 독립 Task를 동시에 시작하고 결과를 모은다"
는 조각뿐이다 — "Workflow 참조"(조건·순서 해석)와 "Agent 배분"(Agent
선택, Q5가 이미 배제)은 포함하지 않는다.

### Q6 결론

**§6 Runtime의 넓은 정의를 결정하거나 확장하지 않는다.** `ADC-02`
(Open)는 이 ADC로 전혀 갱신되지 않는다 — 이 ADC는 그 넓은 질문의
아주 작은 부분 집합 하나만 판단했을 뿐이다. `ADC-0008`(넓은 범위
Not Accepted)의 판단도 뒤집지 않는다.

---

## Q7. Scheduler/Workflow orchestration은 계속 Out of Scope인가

### 검토

RFC-0016 §8이 이미 Scheduler(우선순위, 대기열, 리소스 배분)와
Workflow orchestration(조건 분기, Task 그래프 해석)을 명시적으로
제외했다. 이 ADC가 Accept하는 것은 "이미 코드에 고정된 두 호출을
동시에 시작하고 모은다"는 조율뿐이며, 무엇을 실행할지 **결정**하는
로직(우선순위 판단, 조건부 분기)은 전혀 포함하지 않는다.

### Q7 결론

**Scheduler, 우선순위, Workflow orchestration은 계속 Out of Scope로
유지한다.** `IMPLEMENTATION_RULES.md`의 관련 금지 조항은 이 항목에
대해서는 그대로 유효하다(§Q8이 조정 범위를 별도로 판단).

---

## Decision

**A. Accept (Scoped, Conditional on Data/Artifact Isolation)**

RFC-0016 §8의 좁은 Boundary Question — "서로 독립적인 복수 Task를
동시에 실행하고 결과를 수집하는 책임" — 의 **존재**를 Accept한다.
이 Accept는 다음 조건 위에서만 유효하다.

1. **범위**: 이미 코드/설계에 고정된, 서로 입력 독립·출력 비의존인
   소수의 실행 단위를 동시에 시작하고 결과를 모으는 것으로 한정한다
   — 우선순위 판단, 조건부 분기, Workflow 그래프 해석, Agent 동적
   선택은 포함하지 않는다(Q5, Q7).
2. **Execution Host와 분리**: 이 책임은 Execution Host(§16.3)의
   확장이 아니라 별개 Concept이다(Q3) — Execution Host의 범위는
   전혀 넓어지지 않는다.
3. **Data/Artifact Isolation을 최소 안전조건으로 요구**: 이 책임을
   실제로 적용하는 모든 Task 조합은, 동시 실행되는 각 Task가 서로
   다른 파일/Artifact 이름공간에 쓰거나 아무것도 쓰지 않는다는 것이
   사전에 확인된 경우에만 이 Accept의 범위 안에 있다(Q4). 이 조건이
   확인되지 않는 조합(예: 여러 Task가 같은 파일을 쓸 수 있는 경우)은
   이 Accept가 아직 다루지 않은 것으로 취급한다.
4. 이 Accept는 명칭, 구현 전략, §6 넓은 정의로의 확장을 확정하지
   않는다 — RFC-0016이 이미 명시적 Open Question으로 분리했고, 이
   ADC도 그 분리를 그대로 유지한다.

### Reason

- Q0 — Architecture Intent는 단독 근거가 되지 못하지만, 실행 조율과
  관련된 책임이 있을 수 있다는 신호는 일관되게 있어 왔다.
- Q1 — `workflow_0009.py`라는 실제 Production Code가 이 좁은 범위의
  필요성을 직접 보여준다.
- Q2 — 관찰이 1건뿐이라는 형식적 Rule B 미충족은, RFC-0016이 스스로
  좁힌 범위(이미 존재하는 실제 코드에 대한 조율) 안에서는 Accept를
  막지 못한다 — 다만 그 부족은 Data/Artifact Isolation을 조건으로
  이월함으로써 무시되지 않는다(Q4).
- Q3 — Execution Host와의 경계가 명확히 분리되므로, 이 Accept가
  기존 Accept(§16.3)를 흔들 위험이 없다.
- Q4 — Data/Artifact Isolation을 최소 안전조건으로 명시함으로써,
  검증되지 않은 위험을 침묵하지 않고 조건으로 남긴다.
- Q5 — 기존 Agent 재사용만으로 이 범위가 충족되므로, 이 Accept가
  Registry/Capability 확장을 정당화하지 않는다.
- Q6, Q7 — §6 넓은 Runtime과 Scheduler/Workflow orchestration은
  전혀 건드리지 않아, ADC-02(Open)와 기존 금지 조항이 그대로
  유지된다.

### Decision Rationale

이 Decision은 `ADC-02`(Open)를 갱신하지 않는다 — `ADC-02`가 다루는
§6의 넓은 정의(Workflow 참조 + Agent 배분)는 여전히 미결이며, 이
ADC는 그중 "독립 Task 동시 실행·결과 수집"이라는 아주 좁은 조각
하나만 판단했다. `ADC-0013`/`ADR-0003`(Execution Host 존재),
`ADC-0014`/`ADR-0004`(명칭), `ADC-0015`/`ADR-0005`(구현 전략)도
전혀 흔들리지 않는다 — 이 Decision은 그 Accept들의 범위를 넓히지
않고, 오히려 그와 분리된 새 책임 하나를 좁게 Accept했을 뿐이다.

---

## Implementation Boundary (다음 Production 구현을 위한 최소 책임 범위)

이 Accept는 Production 구현을 지금 승인하지 않는다 — 아래는 향후
ADR·Baseline Update가 이 책임을 등재할 때 참고할 **최소 책임 경계**다.

**포함(이번에 존재를 Accept한 것)**:

- 서로 입력 독립·출력 비의존인, 이미 코드에 고정된 소수의 실행
  단위를 동시에 시작하는 책임.
- 모든 실행 단위가 끝났음을 판단하고 결과를 수집·결합하는 책임.
- 한 실행 단위의 실패가 다른 실행 단위의 진행이나 결과에 영향을
  주지 않는다는 것(실패 격리, `workflow_0009.py`가 이미 함수별
  try/except로 실증)을 유지하는 책임.
- Data/Artifact Isolation이 사전에 확인된 조합에서만 적용된다는
  전제(Q4).

**제외(이번 Accept가 결정하지 않는 것 — 후속 절차로 위임)**:

- 명칭(Multi-Task를 그대로 쓸지, 다른 이름을 쓸지).
- 구현 전략(`ThreadPoolExecutor`/`asyncio`/기타).
- Data/Artifact Isolation 위험(§4 5항목)의 구체적 해소 방법(파일
  잠금, Artifact 이름공간 분리 규칙 등) — 최소 안전조건으로만
  요구할 뿐 설계하지 않는다.
- Task→Agent 동적 할당 — 기존 Agent 재사용을 전제로 하며, 동적
  할당이 필요한 사례는 별도 Evidence 없이는 다루지 않는다(Q5).
- Scheduler, 우선순위, Workflow orchestration(Q7).
- `BASELINE.md` §6의 넓은 정의(Workflow 참조 전체) — 이 Accept로
  검증되지 않는다(Q6).

---

## Risks

- 관찰이 1건(`workflow_0009.py`)뿐이라는 사실은 그대로 남는다 — 향후
  이 Decision이 재검토될 경우, 서로 다른 계기의 독립 관찰(다른
  Task 조합, 다른 HQ)이 추가로 쌓이는 것이 이 Decision을 더 견고하게
  만든다.
- "존재는 Accept됐다"는 것이 "Multi-Task 구현을 지금 시작해도
  된다"로 오독될 위험이 있다 — 그런 뜻이 아니다.
  `IMPLEMENTATION_RULES.md`의 금지 조항은 Baseline이 실제로 갱신되기
  전까지, 그리고 §Decision의 조건 3(Data/Artifact Isolation 사전
  확인)이 충족되지 않는 조합에는 계속 유효하다.
- Data/Artifact Isolation을 "최소 안전조건"으로만 요구하고 해소
  방법을 설계하지 않았으므로, 후속 구현이 이 조건을 형식적으로만
  확인하고 실제로는 충분히 검증하지 않을 위험이 있다 — 다음
  ADR/구현 지침이 이 조건의 확인 방법(예: 정적 분석, 코드 리뷰
  체크리스트)을 구체화해야 한다.
- 이 Decision이 §6 Runtime의 넓은 정의로 확장 해석될 위험 —
  Scheduler/Workflow orchestration/Agent 동적 배분은 이 Accept에
  포함되지 않는다는 것을 다음 ADR이 문구에 명확히 남겨야 한다.

**재검토 조건**: 이 Decision 이후 다음 중 하나가 확인되면 재검토
대상이 된다 — (a) `workflow_0009.py` 외 다른 독립 Task 조합에서
Data/Artifact Isolation 위험이 실제로 재현되는 관찰, (b) 이 좁은
책임 경계로는 실제 필요를 충족하지 못한다는 관찰(예: Task→Agent
동적 할당이 실제로 필요해지는 사례).

## Next Step

**ADR Required** — 이 Decision은 Boundary를 이동시킨다(Open →
Accept, 좁은 범위). 따라서 Baseline Update가 필요하다.

1. ADR을 작성해 `BASELINE.md`를 갱신한다 — §16에 새 절(예: §16.5
   Multi-Task 최소 책임)을 추가해 존재를 등재하되, §Implementation
   Boundary의 제외 항목(명칭, 구현 전략, Data/Artifact Isolation
   해소 방법, Task→Agent 동적 할당, §6 넓은 정의)은 계속 Open으로
   명시한다.
2. 같은 ADR 또는 별도 절차로 `hqs/development/IMPLEMENTATION_RULES.md`
   에 이 좁은 범위(Data/Artifact Isolation이 사전 확인된, 독립 Task
   동시 실행·결과 수집)에 한해 금지 조항을 Scoped 해제하는 방향을
   반영한다 — Scheduler/우선순위/Workflow orchestration/§6 넓은
   Runtime 구현은 계속 금지 상태로 유지한다(`ADC-0015` Q4와 동일한
   패턴).
3. `docs/decisions/adc/ADC.md`의 ADC-02 항목은 ADR 승인 이후에만
   이 Decision을 반영해 갱신한다 — 이 ADC 자신은 그 문서를 수정하지
   않는다.
4. Production 구현 착수는 이 ADC와 후속 ADR이 완료된 이후에만
   가능하다 — 착수 시 `workflow_0009.py`의 `run_comparison`을 최소
   범위 후보로 남긴다(우선순위는 사용자 결정). 구현 전, Data/Artifact
   Isolation 조건(Q4)이 이 함수에 실제로 충족되는지 재확인해야 한다.
5. 명칭, 구현 전략, Task→Agent 동적 할당 필요성은 각각 후속 RFC로
   다룬다.

## Governance Chain 검증

`RFC-0016`(Proposed, `workflow_0009.py` 1건 Evidence로 Boundary
Question만 열고 Decision 아님) → 이 ADC(Accept, Scoped·Conditional
— Execution Host와 분리, Data/Artifact Isolation 최소 안전조건,
기존 Agent 재사용 전제, §6/Scheduler/Workflow orchestration 미확장)
→ 후속 ADR(예정 — Baseline·Rules 반영). RFC-0016이 후속 ADC에
위임한 항목(§8 Boundary Question, §4 위험의 Accept 조건 반영 여부,
`IMPLEMENTATION_RULES.md` 해제 범위, 관찰 수량 보강 필요 여부 — RFC-0016
§Next Step 1~4) 중 1~3을 이 ADC가 답했다. 4번(관찰 수량 보강)은 이
Decision이 Accept로 판단했으므로 해당하지 않는다. RFC-0016의 Out of
Scope(Scheduler·우선순위·Workflow orchestration·§6 넓은 정의·명칭·
구현 전략·위험 해소 방법·ADC-02 자체 수정)를 이 ADC도 하나도
건드리지 않았음을 각 Q절에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **좁은 범위에서 그렇다**:
  독립 Task 동시 실행·결과 수집 책임의 "존재"만 Accept했다. 실제
  Baseline 반영은 ADR을 거쳐야 한다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오** —
  Concept의 명칭·위치·Interface는 확정하지 않았다.
- Contract Change — **없음** — 공개 Interface를 정의하지 않았다.
- Baseline 문서(`BASELINE.md`, `docs/decisions/adc/ADC.md`)를
  변경했는가 — **아니오** — 이 ADC 자신은 인용만 했다. 변경은 ADR의
  몫이다.
- Execution Host(§16.3)의 범위를 넓혔는가 — **아니오**(Q3, §Decision
  조건 2).
- ADR이 필요한가 — **예**(§Next Step).

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0016과 그것이 인용한
  `workflow_0009.py`, `BASELINE.md` §6·§16.3, `ADC.md` ADC-02,
  `ADC-0013`/`ADR-0003`, `ADC-0015`/`ADR-0005`,
  `IMPLEMENTATION_RULES.md`만 인용했다. 새 실험은 하지 않았다.
- MVP-0009의 실제 필요성을 핵심 근거로 사용했는가 — **Pass**(Q1).
- 독립 복수 Task의 동시 실행·결과 수집 책임을 판단했는가 —
  **Pass**(§Decision, Accept Scoped).
- Execution Host와 Multi-Task의 책임 경계를 확정했는가 —
  **Pass**(Q3, §Decision 조건 2).
- Data/Artifact Isolation을 최소 안전조건으로 판단했는가 —
  **Pass**(Q4, §Decision 조건 3).
- Task→Agent 동적 할당을 이 범위에 포함했는가 — **아니오**(Q5,
  기존 Agent 재사용을 전제로 명시적으로 분리).
- §6 Runtime 전체를 결정하거나 확장했는가 — **아니오**(Q6).
- Scheduler/Workflow orchestration을 Out of Scope로 유지했는가 —
  **Pass**(Q7).
- Evidence 부족(관찰 1건)을 이유로 불필요하게 Defer했는가 —
  **아니오**(Q2 — 범위 좁힘과 조건부 이월로 Accept까지 나아갔다).
- Production Code를 수정했는가 — **아니오**.
- Baseline·`IMPLEMENTATION_RULES.md`를 직접 수정했는가 —
  **아니오** — 방향만 제시하고 ADR로 위임했다.
- `docs/decisions/adc/ADC.md`(ADC-02)를 재판단했는가 — **아니오**.
