# JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001: Process Runtime Strategy Experimental Validation — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, 기존 Runtime/Engine/
Workflow, `BASELINE.md`를 수정하지 않는다. Context, Production
Runtime, Runtime API, Kernel Component를 구현하지 않는다.

**핵심 질문**: Process가 Runtime의 기본 전략인가, 아니면 특정
조건에서만 필요한가?

**핵심 결론**: **특정 조건에서만 필요하다 — "동일 Target을 동시
실행할 가능성"이 그 조건이다.** 서로 다른 실제 Dev HQ Validation
3종(실행 시간대 0.1초/0.6초/~69초로 다양)에 Process를 반복 적용한
결과 정확성 100%(9/9 반복)였다. 하지만 Dev HQ 내부의 서로 다른 두
실제 파일(둘 다 `monkeypatch` 미사용)을 **Thread**로 동시 실행해도
3회 반복 전부 정확했다 — Process가 필요 없는 조건도 실제로
확인됐다. 즉 **Process는 "동시 실행 자체"의 기본 요구사항이
아니라, "동일 Target 동시 실행"이라는 좁은 조건에서만 필요하다는
것이 이번 실증으로 구체화됐다.**

---

## 1. 조사 결과

- `docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md`:
  Runtime = CANDIDATE, 근거는 (a) 동일 대상 Thread 동시 실행 시
  결과 오염, (b) 대상 코드의 내부 `ThreadPoolExecutor`와 중첩되어
  실행 시간이 예측 불가능해짐. 이번 Prototype이 재검증 대상으로
  삼은 두 가지.
- `docs/research/JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`
  (subprocess): 동일/다른 대상 여부와 무관하게 항상 안전했다 — OS
  프로세스 경계가 애초에 공유 메모리 문제를 만들지 않기 때문. 단,
  `subprocess.Popen`은 매번 완전히 새 Python 인터프리터를 기동하는
  비용이 있다(이번 Prototype이 실측하지는 않았으나 일반적으로
  `ProcessPoolExecutor`의 재사용 가능한 Worker Process보다 기동
  비용이 크다 — Next Step에서 실측 후보로 남김).
- 저장소 내 `monkeypatch` 사용 파일 분포 확인:
  `hqs/investment/tests/test_stock_team_integration.py`,
  `hqs/development/mvp/tests/test_cli_integrated.py`,
  `test_mvp_0001.py`, `test_stage_02~05.py` 등 다수 — 이번
  Prototype이 "다른 Target 동시 실행이 항상 안전하다"고 일반화하지
  않기 위해, monkeypatch를 **쓰지 않는** 두 파일(`test_ast_
  context.py`, `test_stage_01.py`)을 의도적으로 골라 비교했다(§4).

---

## 2. Experimental Boundary

- 위치: `projects/process-runtime-strategy/`(격리).
- `hqs/`, `core/`, Production `dashboard/`: **무수정**(`git diff
  main -- hqs/ core/ dashboard/` 0줄).
- `rtb_runtime.py`/`rtb_task.py`(`runtime-boundary` Prototype)를
  그대로 재사용 — 중복 구현하지 않았다.
- Process ID, worker pool 크기, scheduling 정책, cancellation:
  추가하지 않았다 — `rtb_runtime.py`의 기존 `ProcessPoolExecutor`
  (max_workers=4)로 모든 검증이 충분했고, 이 이상의 기능이
  필요하다는 실제 신호는 없었다(작업 지시 §6).
- Context, Production Runtime, Runtime API, Kernel Component:
  생성하지 않았다.

---

## 3. 서로 다른 실제 Dev HQ Validation 3종 — Process 반복 검증

| 대상 | 테스트 수 | Sequential Baseline | Process 반복(3회) 결과 |
|---|---|---|---|
| `test_ast_context.py` | 8 | ~0.1초 | 3/3 정확(8,0) |
| `test_stage_01.py` | 5 | ~0.6초 | 3/3 정확(5,0) |
| `test_mvp_0001.py` | 3 | ~69초 | 1/1 정확(3,0), 즉시 반환 확인(호출 직후 RUNNING) |

세 대상 모두 실행 시간대가 다르지만(0.1초~69초) Process 전략의
정확성은 100%였다 — Investment HQ 한 파일에서만 확인했던
`runtime-boundary` Evidence를 Dev HQ의 다양한 실제 작업으로
일반화했다(`test_process_strategy_accurate_across_repeated_
different_dev_hq_targets`, `test_process_strategy_handles_long_
running_dev_hq_validation`).

---

## 4. 동일 Target vs 다른 Target 동시 실행 — Process가 실제로 필요한 조건

**동일 Target(Investment, `monkeypatch` 사용) 동시 실행**:

- Thread: 5회 반복 중 재현(오염) — `runtime-boundary` Evidence
  재확인(`test_thread_can_still_be_contaminated_on_identical_
  target`).
- Process: 3회 반복 전부 정확(4/4) — 재확인
  (`test_process_is_accurate_on_identical_target_concurrent_
  execution`).

**다른 Target(Dev HQ 내부, `monkeypatch` 미사용) 동시 실행**:

- Thread: **3회 반복 전부 정확** — `test_ast_context.py`(8개)와
  `test_stage_01.py`(5개)를 동시 실행해도 결과가 서로 섞이지
  않았다(`test_different_dev_hq_targets_are_safe_under_thread_
  concurrency`). Cross-HQ(Dev+Investment, 이전 Prototype)뿐 아니라
  **같은 HQ 내부의 서로 다른 파일**에서도 재확인됐다.
  - Process: 정확했다(`test_different_dev_hq_targets_also_
    correct_under_process`) — 기대한 결과이며 추가 정보는 없음
    (Process는 필요하지 않은 조건에서도 안전하지만, 그렇다고
    "항상 Process를 써야 한다"는 결론이 강화되지는 않는다).

**결론**: "동시 실행"이 아니라 **"모듈 attribute를 공유하는 동일
Target(또는 그런 Target을 포함하는 조합)의 동시 실행"** 이 실제
위험 조건이다. `monkeypatch`가 있는 파일이 관련되지 않는 한, Thread
로도 실제 문제가 없었다.

---

## 5. Sequential Baseline과 Process 결과 일치

`test_sequential_and_process_results_match`: 동일 대상
(`test_ast_context.py`)을 Sequential/Process 양쪽으로 실행해
결과가 완전히 일치함을 확인(`(8, 0)` == `(8, 0)`) — Process가
정확성을 희생하지 않는다는 것을 baseline과 직접 비교로 재확인.

---

## 6. Failure / Retry, Dashboard Observe — Process 전략에서도 유지

- Failure/Retry: 잘못된 Dev HQ 대상 경로로 Process 실행 →
  `status=FAILED`, `error` 보존, Retry가 새 `task_id`로 같은
  대상을 재사용해 다시 실패(정상) —
  `test_failure_and_retry_still_work_under_process_strategy`.
- Dashboard Observe: `rtb_dashboard_view`(읽기 전용)가 Process
  Task도 동일하게 관찰 — RUNNING 목록에 나타났다가 완료 후 사라짐
  — `test_dashboard_observes_process_tasks_same_as_before`. Task/
  Runtime 분리가 이 Prototype에서도 그대로 성립했다(`rtb_task`를
  재사용했으므로 당연한 결과이지만, 새로운 대상 조합에서 깨지지
  않는지 실제로 재확인했다).

---

## 7. Governance / Boundary 검증

- `git diff main -- hqs/ core/ dashboard/`: 0줄(Production
  무수정).
- `git status`: `projects/process-runtime-strategy/`,
  `docs/research/JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001.md`
  외 변경 없음.
- 신규 테스트: 10 passed
  (`pytest projects/process-runtime-strategy/tests/ -q`, 66.10초 —
  `test_mvp_0001.py`(~69초) 1회 포함).
- 전체 회귀: `pytest --ignore=archive -q` → **348 passed**(이전
  338 → 348, +10, 0 failed, 146.85초 — `test_mvp_0001.py`가 이번
  Prototype과 `in-process-async-command` Prototype 양쪽에서 각각
  1회씩 실행되어 이전 회귀보다 소요 시간이 늘었다). `rtb_`/`prs_`
  이름 분리 덕분에 모듈 충돌 없이 첫 실행부터 통과.

---

## 8. Architecture Findings

- Runtime의 "언제 필요한가"는 실행 시간(장시간 여부)이나 대상
  HQ(Cross-HQ 여부)가 아니라 **"동일 Target을 동시 실행할 가능성이
  있는가"**로 좁혀진다 — 이는 `in-process-async-command`/
  `runtime-boundary` Prototype이 이미 시사했지만, 이번에 Dev HQ
  내부의 서로 다른 실제 파일로 "Process가 필요 없는 조건"까지
  직접 실증하면서 조건이 더 명확해졌다.
- Process를 Runtime의 **기본값**으로 삼을 근거는 아직 약하다 —
  "다른 Target"에서는 Thread로도 실제 문제가 없었고, Process가
  더 안전하다는 것 이상의 실질적 이점(정확성 향상)은 관찰되지
  않았다. Process 고유의 비용(Worker Process 기동, 직렬화)은
  이번 Prototype이 정량적으로 측정하지 않았다 — Next Step.
- **subprocess(async-command)와 in-process Process(runtime-
  boundary/이번 Prototype)의 근본 차이는 아직 명확히 구분되지
  않았다** — 둘 다 OS 프로세스 경계로 격리를 얻지만, 전자는 매
  실행마다 새 인터프리터를, 후자는 재사용 가능한 Worker Pool을
  쓴다는 점에서 비용 구조가 다를 것으로 예상되나 이번 Prototype은
  이를 실측하지 않았다.

---

## 9. Kernel Impact

없음. 확인된 현상은 여전히 "특정 대상 파일이 monkeypatch로
모듈 attribute를 공유하는가"라는 실행 코드 내부 디테일이며,
Cross-HQ 공통 Responsibility가 아니다.

---

## 10. Governance Impact

없음. RFC/ADC/ADR 생성하지 않음. Context/Production Runtime/
Runtime API/Kernel Component 생성하지 않음.

---

## 11. Next Step

우선순위 미확정 — 사용자 결정 필요.

1. **Process vs Thread vs Subprocess 비용 실측**: Worker 기동
   비용, 직렬화 오버헤드를 정량 비교해 "Process를 언제 선택해야
   하는가"의 실질적 판단 기준을 만든다.
2. **"동일 Target" 판별 방법**: 실행 전에 두 요청이 "동일 Target"
   인지(따라서 Process가 필요한지) 판별하는 방법이 있는지 —
   이번 Prototype은 사람이 미리 알고 전략을 선택했을 뿐, 자동
   판별은 검증하지 않았다.
3. Trading HQ 등장 시 3-HQ 재검증(이전 Prototype들과 동일하게
   보류).

---

## 최종 보고

Process는 Runtime의 기본 전략이 아니라 **"동일 Target 동시
실행"이라는 특정 조건에서만 필요**하다는 것이 이번 실증으로
구체화됐다. 서로 다른 실제 Dev HQ Validation 3종(0.1초~69초)에
Process를 반복 적용해 정확성 100%를 확인했고, Dev HQ 내부의 서로
다른 두 실제 파일을 Thread로 동시 실행해도 3회 반복 전부 정확해
"다른 Target"에서는 Process가 불필요하다는 것도 함께 확인했다.
Task(identity/lifecycle)와 Runtime(scheduling/isolation) 분리는
`rtb_task`/`rtb_runtime` 재사용만으로 새로운 대상 조합에서도
그대로 유지됐다. Failure/Retry, Dashboard Observe 모두 Process
전략에서 재확인됐다. Kernel/Governance 영향 없음. Production
승격 판단에는 아직 이르다 — "동일 Target" 자동 판별 방법과 Process/
Thread/Subprocess 비용 비교가 없다.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 신규 10 passed, 전체 저장소 348 passed(0 failed, 회귀 없음)
E2E: 해당 없음(read-only, 실제 Engine/Trade 실행 없음)
RFC: 없음
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (커밋 예정)
Branch: `claude/process-runtime-strategy-prototype`(계보: `claude/runtime-boundary-prototype` → `claude/inprocess-async-command-prototype` → `claude/async-command-prototype` → `claude/command-contract-prototype` → `claude/unified-dashboard-prototype`, 전부 아직 main 미merge)
Next Implementation Candidate: Process/Thread/Subprocess 비용 실측, "동일 Target" 자동 판별 방법 검증, 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정 필요
