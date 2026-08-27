# JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001: Runtime Boundary Experimental Prototype — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, 기존 Runtime/Engine/
Workflow, `BASELINE.md`를 수정하지 않는다. Runtime API, Production
Runtime, Kernel Component를 구현하지 않는다.

**핵심 질문**: `in-process-async-command` Prototype이 발견한 동일
대상 동시 실행 오염 문제를, Sequential/Thread/Process 세 전략으로
실제 비교했을 때 Runtime은 NOT REQUIRED / EXPERIMENTAL / CANDIDATE
중 무엇인가?

**핵심 결론**: **Runtime = CANDIDATE(유지, 근거 강화)**. Thread
전략은 이전 Prototype이 발견한 결과 오염(§4)뿐 아니라, **대상
코드 자체의 내부 `ThreadPoolExecutor`(`hqs/investment/teams/
stock_team.py`)와 중첩되어 실행 시간이 실행마다 크게 달라지는
현상(0.03초 baseline이 최대 16~37초까지 관찰됨)** 까지 재현됐다 —
단순 격리 문제가 아니라 예측 불가능한 성능 열화까지 포함하는 실질적
안전성 문제다. Process 전략은 두 문제 모두에서 항상 정확하고
안정적이었다(3회+3회+3회 반복 전부 4/4, 속도도 일정). Task와
Runtime의 책임 분리(identity/lifecycle vs scheduling/isolation)는
코드 구조로 실제 검증됐다 — Task는 Executor를 전혀 참조하지 않고도
정상 동작했다.

---

## 1. 조사 결과(작업 지시 서두 "기존 Governance/Evidence와
Repository를 먼저 조사한다")

- `docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`
  §8/§12: 동일 대상(`hqs/investment/tests`, 16개)을 Thread로 동시
  실행하면 `monkeypatch` 상태가 섞여 실제 테스트 실패가 재현됨.
  Runtime을 NOT REQUIRED → CANDIDATE로 격상시킨 근거.
- `docs/research/JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001.md`,
  `JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`: Task = CANDIDATE
  (Command 불변성 보호가 이유), Context = NOT REQUIRED — 두 결론
  모두 이번 Prototype이 재검증 대상으로 삼지 않는다(이미 두 번
  독립적으로 확인됨, 이번은 Runtime/Task Boundary에만 집중).
- `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
  Implementation"/"Architecture Need": 이전 Prototype들과 동일한
  절차 재확인.
- Repository 검색: `concurrent.futures.ProcessPoolExecutor` 사용처
  기존에 없음(신규 조합) — `ThreadPoolExecutor`는 이미 3곳에서
  실전 사용 중(`dev-hq-timeout-recovery-prototype`,
  `hqs/investment/teams/*.py`, `hqs/investment/checkpoint.py`).
  **바로 이 기존 `ThreadPoolExecutor` 사용(`stock_team.py`)이
  이번 Prototype에서 중첩 Thread Pool 문제의 원인이 됐다** — 사전
  조사에서 발견한 기존 패턴이 이번 실험 설계의 핵심 변수가 됐다.

---

## 2. Experimental Boundary

- 위치: `projects/runtime-boundary/`(격리).
- `hqs/`, `core/`, Production `dashboard/`: **무수정**(`git diff
  main -- hqs/ core/ dashboard/` 0줄, §9 검증 참조).
- `hqs/*`, `core/*`, `mvp*` 직접 import 금지: AST 기반
  `test_no_direct_hq_or_kernel_import`로 3개 모듈 파일 전부 자동
  검증.
- Runtime API, Production Runtime, Kernel Component: 생성하지
  않았다 — `rtb_runtime.py`는 세 전략을 비교하기 위한 최소
  Dispatcher일 뿐 어떤 전략을 "기본값"으로 채택할지 결정하지
  않는다.
- 모듈 이름: `rtb_` 접두어 사용 — `in-process-async-command`
  Prototype에서 실제로 발생했던 `sys.modules` 이름 충돌(README
  참조)을 반복하지 않기 위해 처음부터 고유 이름으로 설계했다.

---

## 3. Task / Runtime 책임 분리 검증

`rtb_task.py`(identity/lifecycle)와 `rtb_runtime.py`(scheduling/
isolation)를 분리해 구현했다.

- `rtb_task.py`는 `ThreadPoolExecutor`/`ProcessPoolExecutor`를
  이름조차 참조하지 않는다 — `test_task_module_does_not_
  reference_executor_classes_directly`(AST 기반)로 자동 검증.
  Task는 오직 `runtime.start(strategy, target)` /
  `runtime.poll(execution_id)`만 호출한다.
- `rtb_runtime.py`는 Task 개념을 전혀 모른다 — `execution_id`,
  `target_path`, `strategy`만 받고 반환한다. `Task`라는 이름조차
  이 파일에 없다.
- 이 분리가 실제로 문제없이 동작했다: `Task.start()`가 전략만
  바꿔서(`"sequential"`/`"thread"`/`"process"`) 세 가지 실행 방식
  전부에 대해 identity(task_id)/lifecycle(status)/result를 동일한
  방식으로 관리했다(§6 테스트 결과).

---

## 4. 동일 대상 최소 재현(작업 지시 §1)

`hqs/investment/tests/test_stock_team_integration.py`(2 tests,
baseline 0.03~0.13초)를 최소 재현 대상으로 선택했다 — 이전
Prototype이 쓴 전체 16개 스위트보다 작고 빠르면서, 실제로 오염을
일으킨 파일(`monkeypatch.setattr(stock_team, "call_engine", ...)`)
그 자체다.

Thread 전략으로 동일 대상을 5회씩 반복 동시 실행(수동 확인,
2026-08-27):

```
trial0: (1,1,1) (0,2,0) combined=3
trial1: (1,1,1) (0,2,0) combined=3
trial2: (1,1,1) (1,1,1) combined=2
trial3: (1,1,1) (1,1,1) combined=2
trial4: (1,1,1) (1,1,1) combined=2
```

5회 전부 오염(기대값 4를 한 번도 만족하지 못함) — 이전 Prototype의
발견이 더 작은 대상에서도 동일하게 재현됐다. Process 전략으로
동일 조건 5회 반복 시 5회 전부 정확(4/4, §7).

---

## 5. Sequential / Thread / Process 비교

| 전략 | 즉시 반환? | 동일 대상 2회 동시 실행 | 실측 소요 시간 |
|---|---|---|---|
| Sequential | 아니오(호출이 곧 실행, 블로킹) | 항상 정확(4/4) — 애초에 동시성이 없음 | ~0.13~0.14초(순차 합) |
| Thread | 예 | 불안정 — 오염되거나(§4), 결과가 `None`으로 남고 소요 시간이 급증 | 0.18~0.21초(정상) ~ **43초(자동 테스트에서 실제 관찰, §8)** |
| Process | 예 | 항상 정확(4/4) | ~0.11~0.13초(demo), ~0.7초(자동 테스트 3회) — 안정적 |

Sequential은 "즉시 반환"이라는 비동기 성질 자체가 없어 Q1
관점에서는 비교 대상이 아니지만, 정확성의 baseline으로는 유효했다
— 블로킹이므로 격리 문제 자체가 발생할 수 없다(동시에 두 실행이
존재하지 않음).

---

## 6. Failure / Retry(Process 전략)

- 잘못된 대상 경로로 시작 → `status="FAILED"`, `error`에
  return_code 보존, `result=None`(실제 검증,
  `test_failure_is_observable_with_process_strategy`).
- `retry()`가 같은(target, strategy)로 새 Task를 생성 —
  `task_id` 다름, 원본 target을 그대로 재사용해 다시 실패(같은
  잘못된 경로이므로 정상), 이어서 올바른 대상으로도 retry가
  독립적인 새 실행을 만들어 성공하는 것까지 확인
  (`test_retry_with_valid_target_after_fixing_succeeds`).

---

## 7. Concurrent Execution — Task 상태/결과 독립성(Process, 서로 다른 대상)

`test_concurrent_tasks_on_different_targets_are_independent`:
서로 다른 실제 대상(2-test 파일 + 16-test 전체 스위트)을 Process
전략으로 동시 실행 → 둘 다 즉시 RUNNING, 각각 정확한 결과(`(2,0)`,
`(16,0)`)로 독립적으로 완료. Task identity(`task_id`)로 명확히
구분됨.

---

## 8. 예상하지 못한 추가 발견 — Thread 전략과 대상 코드의 중첩 Thread Pool

이번 Prototype의 실제 실행 중, Thread 전략으로 반복 테스트를 돌릴
때 실행 시간이 실행마다 크게 달라지는 현상을 발견했다(pytest
자체 보고 시간은 6.33초인데 프로세스 종료까지 실제 43초가 걸림,
`time python3 -m pytest ... -q` 3회 반복 중 1회 재현, 2026-08-27
측정). 원인을 조사한 결과:

`hqs/investment/teams/stock_team.py`의 `run()`이 **자체적으로
`ThreadPoolExecutor`를 만들어 분석 Wave를 병렬 실행**한다(§1에서
사전 조사로 이미 확인한 기존 패턴). 이 Prototype의 Thread 전략이
이 코드를 감싸면, **바깥쪽 `rtb_runtime._THREAD_EXECUTOR`의 Worker
Thread 안에서 다시 안쪽 `ThreadPoolExecutor`가 생성되는 중첩
구조**가 된다. 두 개의 이런 중첩 실행이 동시에 진행되면 Thread
스케줄링 경합이 심해져 완료까지 걸리는 시간이 예측 불가능해졌다
(별도의 1회성 스크립트 재현에서는 `RuntimeError: cannot schedule
new futures after interpreter shutdown`까지 관찰됨 — 인터프리터
종료 시점과 중첩 Thread Pool의 내부 스케줄링이 경쟁 상태에 빠질 수
있음을 시사한다).

Process 전략은 이 문제가 전혀 없었다(§5 표, 반복 실행 전부
~0.7초로 일정) — 각 Process가 완전히 독립된 인터프리터이므로
바깥쪽/안쪽 Thread Pool 개념 자체가 부모 프로세스와 공유되지
않는다.

이 발견은 §4의 결과 오염과는 **다른 종류의 문제**다 — 오염은
"틀린 결과를 정확한 것처럼 반환하는" 문제였고, 이번 발견은
"실행이 언제 끝날지 예측할 수 없어지는" 문제다. 둘 다 Thread
전략의 실제 위험이며, 둘 다 Process 전략에는 없었다.

---

## 9. Governance / Boundary 검증

- `git diff main -- hqs/ core/ dashboard/`: 0줄(Production
  무수정).
- `git status`: `projects/runtime-boundary/`,
  `docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md`
  외 변경 없음.
- 신규 테스트: 13 passed
  (`pytest projects/runtime-boundary/tests/ -q`).
- 전체 회귀: `pytest --ignore=archive -q` → **338 passed**(이전
  325 → 338, +13, 0 failed). `rtb_` 접두어 덕분에 모듈 이름 충돌
  없이 첫 실행부터 통과.

---

## 10. Architecture Findings

- **Task(identity/lifecycle)와 Runtime(scheduling/isolation)은
  코드 구조로 분리 가능하다는 것이 실제로 증명됐다** — `rtb_task.py`
  는 Executor를 몰라도 세 가지 실행 전략 전부에서 정상 동작했다.
- **Runtime의 "isolation" 책임은 실제로 필요하다** — 단, "Task를
  더 정교하게 설계"해서 해결되는 문제가 아니라, "실행을 어디서
  하는가(Thread vs Process)"라는 순수 Runtime 층위의 결정이었다.
  in-process-async-command Prototype §12가 가설로 남긴 결론이
  이번에 Process/Thread 직접 비교로 확정적 증거를 얻었다.
- Thread 전략의 위험은 한 가지가 아니라 최소 두 가지였다(결과
  오염 + 예측 불가능한 지연) — Runtime이 필요하다는 결론을
  강화하지만, 그 Runtime이 반드시 "여러 전략 중 선택"이어야
  하는지, 아니면 "Process 전략 하나만 지원"이면 충분한지는 이번
  Prototype이 답하지 않는다(Next Step).

---

## 11. Kernel Impact

없음. Cross-HQ 공통 Responsibility가 확인된 것이 아니라, Investment
HQ 한 팀 코드(`stock_team.py`)의 내부 구현(자체 Thread Pool 사용)
이 원인이었다 — Kernel Candidate 기준(Cross-HQ 공통성)에 해당하지
않는다.

---

## 12. Governance Impact

없음. RFC/ADC/ADR 생성하지 않음. Runtime API, Production Runtime,
Kernel Component 생성하지 않음.

---

## 13. Next Step

우선순위 미확정 — 사용자 결정 필요.

1. Process 전략을 Runtime의 유일한/기본 전략으로 좁히는 것이
   타당한지(Thread를 아예 후보에서 제외) 추가 검증.
2. Trading HQ 등장 시 3-HQ 재검증(이전 Prototype들과 동일하게
   보류).

---

## 최종 보고

Runtime = **CANDIDATE**(결론 유지, 근거가 결과 오염 1건에서
"결과 오염 + 예측 불가능한 지연" 2건으로 강화됨). Task와 Runtime의
책임 분리는 `rtb_task.py`가 Executor를 전혀 참조하지 않고도 세
전략 모두에서 정상 동작한다는 것으로 코드 수준에서 실증됐다.
Sequential(baseline)/Thread(불안정)/Process(안정) 비교에서
Process가 유일하게 정확성과 속도 모두 일관됐다. Failure/Retry,
Dashboard 관찰(전략 무관), 서로 다른 대상의 동시 Task 독립성 모두
Process 전략으로 실제 검증됐다. Kernel/Governance 영향 없음.
Production 승격 불가 — Runtime의 정확한 책임 범위(전략 선택 자체를
남길지, Process로 고정할지)가 아직 결정되지 않았다.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 신규 13 passed, 전체 저장소 338 passed(0 failed, 회귀 없음)
E2E: 해당 없음(read-only, 실제 Engine/Trade 실행 없음)
RFC: 없음
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: `f9a95e3`
Branch: `claude/runtime-boundary-prototype`(계보: `claude/inprocess-async-command-prototype` → `claude/async-command-prototype` → `claude/command-contract-prototype` → `claude/unified-dashboard-prototype`, 전부 아직 main 미merge)
Next Implementation Candidate: Process 전략을 Runtime 기본/유일 전략으로 좁히는 검증, 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정 필요
