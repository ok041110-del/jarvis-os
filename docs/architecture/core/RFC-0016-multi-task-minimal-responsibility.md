# RFC-0016: Multi-Task 최소 책임 — 독립 Task 동시 실행과 결과 수집 (ADC-02 후속, Execution Host와 분리)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/decisions/adc/ADC.md` ADC-02("Runtime 개념의 존폐") — Open·NOW.
`docs/architecture/baseline/BASELINE.md` §6이 정의한 넓은 Runtime 책임
("Workflow를 참조하여 Task를 Agent에게 배분") 중, 이 RFC는 그 전체가
아니라 **서로 독립적인 복수 Task를 동시에 실행하고 결과를 수집하는
최소 부분 집합**만 연다.
**Evidence**: `hqs/development/mvp/workflow_0009.py`(`run_comparison`,
현재 `main`), `docs/architecture/baseline/BASELINE.md` §6·§16.3,
`docs/decisions/adc/ADC.md` ADC-02, `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`,
`docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`,
`hqs/development/IMPLEMENTATION_RULES.md`. 새로운 실험을 만들지
않는다 — 이미 `main`에 병합된 실제 Production Code(`workflow_0009.py`)
1건을 유일한 실증 근거로 삼는다.

> 본 RFC는 Multi-Task 책임의 존재 여부를 확정하지 않는다. Scheduler,
> 우선순위, Workflow orchestration, `BASELINE.md` §6의 넓은 Runtime
> 정의로의 확장은 다루지 않는다. Execution Host(§16.3)의 범위를
> 넓히지 않는다 — 오히려 그 범위를 그대로 유지한 채 Multi-Task를
> 별개 책임으로 분리한다. Production Code(`hqs/`, `core/`,
> `dashboard/`)는 수정하지 않는다.

## 0. 이 RFC가 열린 이유

`ADC-0013`/`ADR-0003`은 ADC-02의 넓은 질문("Runtime 존폐")을
"Command·Task로 환원되지 않는 단일 실행 단위의 dispatch·격리
책임"으로 좁혀 Accept(Scoped)했다. `BASELINE.md` §16.3은 이 Accept가
"§6의 넓은 정의(Workflow 참조, Multi-Task를 Agent에게 배분)로의
확장 여부"를 명시적으로 결정하지 않는다고 스스로 한정했고, ADC-02는
그 넓은 정의 그대로 여전히 Open이다.

이후 `main`에 병합된 `hqs/development/mvp/workflow_0009.py`의
`run_comparison(issue)`가 실제로 이 미결 영역에 해당하는 코드를
이미 담고 있다는 것이 관찰됐다. 이 RFC는 그 관찰을 근거로, ADC-02의
넓은 질문 전체가 아니라 그 안의 좁은 부분 집합 하나("독립 Task
동시 실행과 결과 수집")만 정식 Boundary Question으로 연다 — 이는
`RFC-0013`이 ADC-02를 "단일 실행 단위 dispatch·격리"로 좁힌 것과
같은 절차적 선례를 따른다.

## 1. Problem Statement

`hqs/development/mvp/workflow_0009.py:56-66`의 `run_comparison`은
다음과 같이 되어 있다.

```python
def run_comparison(issue: dict) -> dict:
    flat = run_issue_to_planning(issue)
    bundled = run_issue_to_planning_with_bundle(issue)
    return {
        "flat_context_planning": flat["planning"],
        "context_bundle_planning": bundled["planning"],
        "context_bundle": bundled["context_bundle"],
    }
```

`flat`과 `bundled`는 서로 다른 함수이며, 서로의 출력에 의존하지
않는다(둘 다 동일한 `issue`만 입력으로 받는다). 각각 내부에서
`requirements_agent_requirement_analysis` → `call_engine()` →
`subprocess.run()`(최대 180초, `hqs/development/mvp/engine.py`)을
호출한다. 현재 구현은 이 둘을 **순차** 실행한다 — 병렬화해도
`run_comparison`의 반환 형태나 두 결과의 내용은 전혀 달라지지
않으며, 오직 총 소요 시간만 줄어든다.

이 상황은 다음 세 가지를 동시에 만족하는 첫 실제 사례다.

1. 서로 독립적인 두 개의 실행 단위가 실제 Production Code에 존재한다.
2. 그 실행 단위들을 동시에 실행하는 것이 Workflow의 의미를 바꾸지
   않는다(오히려 `run_comparison`의 원래 취지 — "우열 없이 나란히
   비교" — 에 더 부합한다).
3. 이를 표현할 기존 Concept이 없다 — Task는 "실행을 수행"할 뿐
   "여러 Task를 동시에 시작하고 모은다"는 조율을 표현하지 않고,
   Execution Host(§16.3)는 이미 dispatch가 결정된 **단일** 실행
   단위의 격리만 다룬다(`ADC-0015` §Out of Scope가 Multi-Task로의
   확장을 명시적으로 배제).

이 RFC는 이 세 조건이 가리키는 좁은 질문만 연다: **서로 독립적인
복수 Task를 동시에 실행하고 그 결과를 수집하는 책임이 Kernel
Concept으로 필요한가?**

## 2. Multi-Task와 Execution Host의 책임 분리

두 책임은 다루는 질문 자체가 다르다.

| | Execution Host(§16.3, Accept·Scoped) | Multi-Task(이 RFC가 여는 질문) |
|---|---|---|
| 질문 | 이미 dispatch가 결정된 **하나**의 실행 단위를, 동일 Target 동시 실행에서도 정확하게 격리해 실행하려면? | **여러** 독립 실행 단위를 언제·동시에 시작하고, 언제 전부 끝났다고 판단하며, 결과를 어떻게 모을 것인가? |
| 입력 | 단일 `func(*args, **kwargs)` | 복수의 독립 실행 단위(예: `[flat_call, bundled_call]`) |
| 책임 | 격리(Isolation) | 조율(Coordination) — 시작·대기·수집 |
| `workflow_0009.py`와의 관계 | `run_issue_to_planning`/`run_issue_to_planning_with_bundle` 각각의 **내부**(각자 자기 실행 자체)는 이미 Execution Host 대상이 아니다 — `call_engine()`이 이미 독립 OS subprocess로 격리되어 있어 동일 Target 오염 조건 자체가 없음(선행 조사 결론) | `run_comparison`이 이 둘을 **동시에 시작하고 모으는** 지점이 이 RFC의 대상 |
| 결정 상태 | 이미 Accept(Scoped) — 이 RFC가 재론하지 않음 | Open(ADC-02의 부분 집합) — 이 RFC가 처음 좁혀서 연다 |

두 책임은 배타적이지 않다 — 향후 "동일 Target을 동시에 여러 번
실행"해야 하는 Multi-Task 사례가 생기면 Multi-Task가 각 실행 단위를
Execution Host에 위임하는 조합도 가능하다. 그러나 그 조합 여부는
이 RFC의 범위 밖이다(§Out of Scope). 이 RFC가 필요로 하는 것은
"Multi-Task가 존재한다면 Execution Host와 겹치지 않는다"는 것의
확인뿐이다.

## 3. 최소 범위 검토 — Task Identity/Lifecycle, 동시 실행, 결과 수집

`workflow_0009.run_comparison` 수준의 최소 사례를 기준으로 세 요소만
검토한다(그 이상은 §Out of Scope).

- **Task Identity/Lifecycle**: `flat`/`bundled` 각각은 이미
  독립적으로 식별 가능한 호출이다(서로 다른 함수, 서로 다른 인자
  가공). 새로운 identity 개념을 만들 필요는 없어 보인다 — 다만
  "동시에 시작된 두 실행을 하나의 논리적 단위로 묶어 부를 이름"이
  필요한지는 미결이다(§7).
- **동시 실행**: `flat`과 `bundled`를 시작하는 시점과, 두 결과가
  모두 준비됐다고 판단하는 시점(join)이 필요하다. 이 자체가 새
  Concept("무엇을 언제 동시에 실행할지 결정")이며, `BASELINE.md`
  §6이 "Runtime"에 부여한 정의("Task를 Agent에게 배분")의 가장
  축소된 형태다.
- **결과 수집**: `run_comparison`은 이미 두 결과를 단순 dict
  결합으로 모은다 — 이 결합 자체는 새 책임이 필요 없다. 다만 한쪽만
  실패했을 때(§4) 무엇을 반환할지는 현재 코드가 이미 각 함수 내부
  try/except로 흡수하고 있어(`workflow.py`의 `_engine_failure_message`
  패턴), Multi-Task 계층이 별도로 처리할 필요가 있는지는 열린
  질문이다.

## 4. 위험 항목

Multi-Task 책임이 실제로 필요하다고 판단될 경우, 다음 5개 위험은
"동시 실행 자체의 정확성"과 별개로 반드시 검토돼야 한다 — 이
RFC는 위험을 **나열**할 뿐 해소하지 않는다.

1. **파일 덮어쓰기**: 동시 실행되는 두 Task가 같은 파일 경로에
   쓰기를 시도하면 경쟁 상태가 발생한다. `workflow_0009.py` 사례
   자체는 파일 쓰기가 없어(Engine 응답을 메모리 dict로만 다룸)
   이 위험을 노출하지 않지만, 다른 Task 조합(예: Artifact를 파일로
   저장하는 Task)에서는 실제 위험이다.
2. **Artifact/Result 충돌**: 두 Task가 같은 Artifact 이름이나
   Result 키를 생성하면 한쪽이 다른 쪽을 덮어쓸 수 있다.
   `run_comparison`은 두 결과를 서로 다른 키(`flat_context_planning`
   / `context_bundle_planning`)로 이미 분리해 이 위험을 우연히
   피하고 있으나, 이는 현재 코드의 우연이지 Multi-Task 계층이
   보장하는 성질이 아니다.
3. **공유 상태**: `project_intelligence.py`의 `collect_relevant_context`/
   `build_context_bundle`은 파일시스템을 읽기만 하고 프로세스
   전역 변수를 쓰지 않는다(선행 조사 확인) — 그러나 향후 캐시나
   메모이제이션이 추가되면 공유 상태 위험이 새로 생길 수 있다.
4. **Git 충돌**: 현재 MVP Workflow는 Git에 쓰기 작업을 하지 않는다
   — 그러나 Multi-Task가 향후 "코드 생성 → 파일 반영" 같은 Task로
   확장되면, 동시 실행되는 두 Task가 같은 작업 트리를 건드릴 때
   Git 수준 충돌이 발생할 수 있다.
5. **Retry 충돌**: 두 Task 중 하나만 실패해 재시도할 때, 이미 성공한
   다른 Task의 결과를 보존하면서 실패한 Task만 재실행하는 것이
   필요하다 — 현재 `run_comparison`은 Task 단위 재시도 개념이 없고
   전체 함수를 다시 호출해야 하므로, 이 위험은 실제 코드로는 아직
   검증되지 않았다(Evidence 없음).

## 5. Execution Isolation과 Data/Artifact Isolation의 구분

이 둘은 서로 다른 문제이며, 이 RFC는 섞어서 다루지 않는다.

- **Execution Isolation**(Execution Host의 문제, §16.3): 동일 Target을
  동시 실행할 때 **실행 자체의 상태**(프로세스 전역 변수, monkeypatch
  된 참조 등)가 오염되는가. `call_engine()`이 이미 독립 subprocess로
  실행되므로 `workflow_0009.py` 사례에서는 이 문제가 원천적으로
  발생하지 않는다(선행 조사 결론, 재확인만 함).
- **Data/Artifact Isolation**(§4가 나열한 위험, Multi-Task의 문제):
  동시 실행되는 여러 Task가 **결과물(파일, dict 키, Git 작업 트리)**
  을 서로 덮어쓰는가. 이는 실행 격리가 완벽해도 별도로 발생할 수
  있는 문제다 — 두 Task가 각자 완벽히 격리된 프로세스에서 실행되어도,
  둘 다 같은 파일 경로에 쓰기를 시도하면 Data/Artifact 충돌은
  그대로 발생한다.

`workflow_0009.py` 사례는 Execution Isolation 문제가 없고
Data/Artifact Isolation 위험도 우연히 회피되어 있어(§4-2), 이 구분이
실제 위험으로 드러나지 않는다 — 그러나 이 구분 자체가 없으면 향후
사례에서 두 문제를 뭉뚱그려 "Execution Host를 확장하면 된다"는
잘못된 해법으로 이어질 위험이 있다. 이 RFC가 Execution Host와
Multi-Task를 분리하는 이유(§2)가 여기서도 재확인된다 — Execution
Host의 격리 보장은 Data/Artifact Isolation을 전혀 보장하지 않는다.

## 6. Task→Agent 할당 필요성과 기존 Agent 재사용

`run_comparison`의 두 분기(`flat`, `bundled`)는 **같은 Capability**
(`requirements_agent_requirement_analysis`, Requirements Agent)를
서로 다른 입력으로 두 번 호출하는 것이다 — 새로운 Agent나 새로운
Capability가 필요하지 않다. 즉:

- 기존 `AGENT_CAPABILITY_MAP`/`HELLO_SDLC_CAPABILITY_MAP`(리터럴
  딕셔너리) 확장 없이 기존 Agent 함수를 그대로 재사용할 수 있다.
- "Task를 어떤 Agent에게 배분할지 결정"하는 문제(§6 Runtime 정의의
  일부)는 이 최소 사례에서는 발생하지 않는다 — 호출할 Agent 함수는
  이미 코드에 고정되어 있고, Multi-Task가 결정해야 하는 것은
  "언제 동시에 시작하고 언제 모을지"뿐이다.
- 따라서 이 RFC가 여는 최소 범위에서는 **Task→Agent 동적 할당**이
  필요하다는 근거가 없다 — 이는 `BASELINE.md` §6의 "Task를 Agent에게
  배분"이라는 넓은 정의 중, Agent 선택 로직까지는 이 RFC의 Evidence가
  다루지 않는다는 것을 의미한다.

## 7. §6 "Runtime"과의 관계

`BASELINE.md` §6 Concept Model은 Runtime을 "Workflow를 참조하여
Task를 Agent에게 배분하는" Service로 정의한다. 이 RFC가 여는
Multi-Task 책임은 그 정의의 **부분 집합**이다 — "Workflow 참조"(어떤
Task들이 순서/조건에 따라 실행돼야 하는지 해석하는 것)와 "Agent에게
배분"(어떤 Agent가 각 Task를 수행할지 선택하는 것)은 포함하지
않는다(§6이 확인). 이 RFC가 다루는 것은 그중 "이미 정해진 소수의
독립 Task를 동시에 시작하고 결과를 모은다"는, `RFC-0013`이
Execution Host를 위해 좁혔던 것과 같은 방식의 최소 조각이다.

`ADC-0015` §Out of Scope는 Execution Host의 허용 범위가 "Multi-Task를
Agent에게 배분"으로의 확장을 포함하지 않는다고 이미 명시했다 — 이
RFC는 그 배제를 재확인하며, Multi-Task를 Execution Host의 확장이
아니라 **§6 Runtime 정의의 또 다른 부분 집합**으로 위치시킨다.
`ADC-02`(Runtime 존폐, Open) 자체는 이 RFC로 해소되지 않는다 — 이
RFC는 그 넓은 질문 중 이 좁은 조각 하나만 정식 Boundary Question으로
연다.

## 8. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 좁은 질문만 제기한다.

**Jarvis OS는 서로 독립적인(입력 독립·출력 비의존) 복수 Task를
동시에 실행하고 그 결과를 수집하는 책임을, Execution Host(§16.3)와
별개의 Kernel Concept으로 Accept하는가?**

| 후보 | 근거 | 근거 성격 |
|---|---|---|
| Accept(최소 범위) | §1 `workflow_0009.py` 실제 사례 1건 — 지연 단축의 실질적 가치, 기존 Workflow 의미 불변(§1-2) | 실제 Production Code 근거, 그러나 관찰 1건뿐 |
| Not Accepted(현행 유지) | 관찰 1건은 Governance v2 Rule B의 "3건 이상 독립 관찰" 기준에 크게 못 미침. §4의 위험(Data/Artifact Isolation 등)이 전혀 검증되지 않음 | 수량·검증 부족 |

이 RFC는 이 중 어느 쪽이 맞는지 판단하지 않는다. 판단은 후속 ADC로
위임한다.

### 이 Boundary Question이 명시적으로 제외하는 것

- **Scheduler**: Task 우선순위, 대기열, 리소스 배분은 다루지 않는다.
- **우선순위**: 여러 Task 후보 중 무엇을 먼저 실행할지 결정하는
  로직은 다루지 않는다.
- **Workflow orchestration**: 조건 분기, Task 그래프 해석은 다루지
  않는다 — `run_comparison`처럼 이미 코드에 고정된 두 호출만 대상.
- **넓은 Runtime 확장**: §6의 "Workflow 참조", "Agent 배분" 부분은
  다루지 않는다(§7).
- **명칭**: Multi-Task라는 임시 명칭을 그대로 쓸지, Execution Host
  선례(`ADC-0014`)처럼 별도 명칭 절차를 거칠지는 후속 판단으로
  남긴다.
- **구현 전략**: `ThreadPoolExecutor`/`asyncio`/기타 무엇을 쓸지는
  다루지 않는다 — Execution Host 선례(`RFC-0015`)와 동일하게 존재
  판단과 구현 전략을 분리한다.
- **§4 위험의 해소 방법**: 위험을 나열했을 뿐, 해소책(파일 잠금,
  Artifact 이름 공간 분리 등)은 설계하지 않는다.

## Out of Scope

- Multi-Task 존재 여부의 실제 판단(§8에 위임).
- Scheduler, 우선순위, Workflow orchestration 설계.
- `BASELINE.md` §6 "Runtime"의 넓은 정의(Workflow 참조, Agent 배분)
  전체 검증 또는 수정.
- Multi-Task의 명칭 결정.
- 구현 전략(ThreadPoolExecutor 등) 결정.
- §4가 나열한 위험(파일 덮어쓰기, Artifact/Result 충돌, 공유 상태,
  Git 충돌, Retry 충돌)의 해소 방법 설계.
- Execution Host(§16.3)의 범위 확장 — 오히려 그 범위를 그대로
  유지한다(§2).
- `docs/decisions/adc/ADC.md`의 ADC-02 항목 자체 수정.
- Production Code(`hqs/`, `core/`, `dashboard/`) 수정 — 전혀 하지
  않는다.
- 새로운 실험 — `workflow_0009.py`라는 이미 병합된 Production
  Code만 근거로 삼는다.

## Non-goals

- 이 RFC는 Multi-Task 책임의 존재를 확정하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 Scheduler, 우선순위, Workflow orchestration을 설계하지
  않는다.
- 이 RFC는 Execution Host의 범위를 넓히지 않는다.
- 이 RFC는 구현 전략이나 명칭을 확정하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 §8의 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §8 Boundary Question(독립 Task 동시 실행·결과 수집 책임의 존재
   여부)을 지금 Evidence(`workflow_0009.py` 1건)로 Accept할 수
   있는지, 아니면 Governance v2 Rule B의 관찰 수량 기준 미충족을
   이유로 Not Accepted로 남길지.
2. Accept된다면, §4의 위험(특히 Data/Artifact Isolation)에 대한
   Evidence를 요구하는 후속 Prototype을 선행 조건으로 둘지, 아니면
   구현 단계로 넘길지.
3. Accept된다면, `hqs/development/IMPLEMENTATION_RULES.md`의
   "Scheduler/Multi-Task/Workflow 구현 금지" 조항 중 정확히 어느
   부분(이 RFC가 좁힌 최소 범위)만 해제 대상인지 — Scheduler·
   우선순위·Workflow orchestration은 그대로 금지 상태를 유지해야
   함을 명시하도록 제안한다.
4. Not Accepted라면, 관찰 수량(현재 1건)을 늘릴 별도 실측(예:
   `workflow_0009.py` 외 다른 독립 Task 조합 탐색)을 별도 절차로
   요구할지, 아니면 이 좁은 질문 자체를 보류할지.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `workflow_0009.py`(현재 `main`),
  `BASELINE.md` §6·§16.3, `ADC-02`, `RFC-0013`/`ADC-0013`/`ADR-0003`,
  `ADC-0015`, `IMPLEMENTATION_RULES.md`만 인용했다. 새 실험은
  수행하지 않았다.
- Multi-Task 존재를 결정했는가 — **아니오**. §8은 질문 형태로만
  남겼다.
- Execution Host의 범위를 넓혔는가 — **아니오**. §2·§5·§7이 명시적으로
  분리·유지했다.
- Scheduler/우선순위/Workflow orchestration을 설계했는가 —
  **아니오**(§Out of Scope).
- §4의 위험을 해소했다고 주장했는가 — **아니오** — 나열만 하고
  해소책은 다루지 않았다고 명시했다.
- Execution Isolation과 Data/Artifact Isolation을 구분했는가 —
  **Pass**(§5).
- Task→Agent 동적 할당이 필요하다고 주장했는가 — **아니오**(§6,
  이 최소 범위에서는 근거가 없다고 명시).
- §6 "Runtime"과의 관계를 명시했는가 — **Pass**(§7, 부분 집합으로
  위치시킴).
- `ADC-02`를 재판단했는가 — **아니오**, 그 넓은 질문의 부분 집합만
  열었다.
- Production Code를 수정했는가 — **아니오**.
- ADC, ADR 문서를 작성했는가 — **아니오**. RFC 문서 하나만
  작성했다.
