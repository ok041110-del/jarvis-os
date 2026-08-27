# JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001: In-Process Async Command Experimental Prototype — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, 기존 Runtime/Engine/
Workflow, `BASELINE.md`를 수정하지 않는다.

**핵심 질문**: "in-process 비동기 실행에서 immutable Command와 실행
lifecycle을 분리하기 위해 Task가 실제로 필요한가? 그 Task를 실행하기
위해 별도의 Runtime Architecture가 실제로 필요한가?"

**핵심 결론**: **Task 필요성은 이전 Prototype과 동일하게 재확인됐다**
(결과 A — Task = CANDIDATE 유지, Command 불변성 보호가 이유). 그러나
**Runtime 질문의 답은 subprocess 버전과 달라졌다.** in-process 실행은
"서로 다른 실제 작업"을 동시 실행할 때는 안전했지만, **동일한 대상을
동시 실행하면 실제로 결과가 오염됐다** — 단순 카운트 오류가 아니라
`monkeypatch`로 설정한 fake 상태가 스레드 간에 실제로 섞여 진짜 테스트
실패(`assert 2 == 1` 등)가 재현됐다. subprocess는 OS 프로세스 경계로
이 문제를 공짜로 피했지만, in-process 실행에는 그 경계가 없다. 이는
Runtime을 CANDIDATE로 격상시킬 근거이지만, 이번 Prototype의 Command/
Task 설계 자체가 이 문제를 일으키거나 해결하지 못한다는 것도 함께
확인했다(§12 참조) — **결과 C(Task=CANDIDATE, Runtime=CANDIDATE, 두
책임의 Boundary 검토 필요)**에 해당한다.

---

## 1. Objective

`JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`(subprocess 기반)가
"Runtime = NOT REQUIRED(subprocess-delegatable 범위에 한정, in-process
비동기 Engine 호출은 미검증 Gap)"로 명시적으로 남긴 Gap을 검증한다.
Task/Runtime을 미리 Architecture로 확정하지 않고, Case A(Command만)로
먼저 시작해 실제로 막히는 지점을 관찰한 뒤에만 필요한 만큼 Case B를
만들었다(작업 지시 §25 순서 준수).

---

## 2. Existing Evidence

작업 지시 §1이 요구한 목록을 저장소 전체에서 검색했다.

- `asyncio`/`threading`/`concurrent.futures` 사용처 12개 파일 발견.
  그중 `projects/dev-hq-timeout-recovery-prototype/parallel/parallel_runner.py`
  가 이미 `ThreadPoolExecutor`로 실제 Engine 호출(`agents.py`)을
  병렬 실행하는 패턴을 갖고 있다 — 이 Prototype은 그 패턴을
  중복 구현하지 않고 그대로 재사용했다(`inproc_operation.py`).
  `hqs/investment/teams/*.py`, `hqs/investment/checkpoint.py`도
  동일한 `ThreadPoolExecutor` Wave 병렬 패턴을 이미 쓰고 있다(Bull/
  Bear, 7개 분석 Wave) — **in-process 병렬 실행 자체는 저장소에
  이미 존재하는 검증된 패턴**이며, 이번 Prototype이 새로 발명한
  개념이 아니다.
- `docs/architecture/core/STRUCTURE.md`: 존재하지 않는다 —
  `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`가 Source of
  Truth(이전 두 Prototype과 동일 결론).
- Task/Runtime/Context Production 구현: 저장소 전체에 없음(이전
  Prototype들과 동일 결론 재확인).
- Dashboard Snapshot: `projects/unified-dashboard/snapshot.py`를
  Command Contract Prototype 경유로 이미 재사용 중 — 이번 Prototype도
  `inproc_case_b.py` → `resolver._detect_hq`를 통해 간접 재사용한다
  (직접 import하지 않음, Boundary 유지).

---

## 3. Experimental Boundary

- 위치: `projects/in-process-async-command/`(격리).
- `hqs/`, `core/`, Production `dashboard/`, 기존 Runtime/Engine/
  Workflow: **무수정**(`git diff main -- hqs/ core/ dashboard/` 결과
  0줄, §17 검증 참조).
- `hqs/*`, `core/*`, `mvp*` 직접 import 금지: AST 기반
  `test_no_direct_hq_or_kernel_import`로 4개 모듈 파일 전부 자동
  검증(테스트 통과).
- `projects/command-contract/`의 `resolver._detect_hq`만 재사용,
  HQ 판별 로직을 중복 구현하지 않았다.
- `core/task/`, `core/runtime/`, `core/context/`, `core/command/`:
  생성하지 않았다.

---

## 4. Execution Target

우선순위(작업 지시 §4)에 따라 **1순위: 기존 Dev HQ read-only
Workflow**이자 **2순위: 기존 Validation 작업**에 해당하는 실제
pytest 스위트를 선택했다.

- Development HQ: `hqs/development/mvp/tests/test_mvp_0001.py`
  (실측 68.84~69.07초, 3 passed, 2026-08-27 sequential baseline
  측정) — 저장소 안에서 가장 오래 걸리는 실제 MVP 워크플로 테스트.
  `async-command` Prototype이 subprocess로 실행한 것과 동일한
  종류의 실제 작업을 **in-process**(`pytest.main()`을 Worker
  Thread에서 직접 호출)로 실행했다.
- Investment HQ: `hqs/investment/tests`(실측 0.05~0.19초, 16
  passed) — 빠른 lifecycle 관찰/Failure/Retry 검증용.
- 실제 주문·Trade Execution·Production 데이터 변경: 없음(read-only
  Validation만 실행, 작업 지시 §4 준수).
- `sleep()`: 사용하지 않았다.

---

## 5. Case A — Command Only

`inproc_case_a.py`: `AsyncCommand`(mutable dataclass — `raw_input`,
`target_hq`, `execution_id`, `status`, `passed`, `failed`, `error`).
`start()`가 `inproc_operation.start_operation()`을 호출해 즉시
반환하고, `refresh()`가 non-blocking poll로 상태를 갱신한다.

**Q1 답(즉시 반환?)**: 예 — `start()` 호출 직후 `status`는 항상
`"RUNNING"`이었다(Executor에 제출만 하고 반환).

---

## 6. Case B — Command + Task

Case A에서 실제 문제(§5의 mutable Command, Command 불변성 상실)가
확인된 뒤 `inproc_case_b.py`를 만들었다. `Command`는
`frozen=True`(raw_input, target_hq), `Task`는 최소 필드만
(task_id, command, execution_id, status, result, error) 사용했다.
`retry()`는 실패한 Task의 `command`를 그대로 재사용해 새 Task를
만든다(작업 지시 §7 최소 필드 원칙 준수, `context`/`priority` 등
불필요한 필드는 추가하지 않았다).

---

## 7. Async Lifecycle

실제로 관찰된 상태 전이만 기록한다(작업 지시 §12 PENDING 원칙 준수).

- `RUNNING → COMPLETED`: 실제 관찰(Investment HQ, Development HQ
  모두).
- `RUNNING → FAILED`: 실제 관찰(잘못된 대상 경로, §9).
- `FAILED → RETRY → RUNNING → COMPLETED`: 실제 관찰
  (`test_retry_reuses_command_and_produces_new_task`).
- `PENDING`: 이번에도 선언은 했지만(`Task.status` 기본값)
  **실제로 관찰되지 않았다** — `start()`가 Operation을 즉시 제출해
  `status`가 생성 직후 바로 `"RUNNING"`으로 바뀌기 때문이다. 이전
  Prototype과 동일한 결론이며, 두 번째 Prototype에서도 재확인됐다는
  것은 이 조건에서 PENDING이 구조적으로 불필요함을 시사한다.

---

## 8. Concurrent Execution

**서로 다른 실제 대상(Dev HQ + Investment HQ)을 동시 실행 — 정상.**

`demo.py` 실행(2026-08-27) 결과:

```
started dev=96f2647a investment=6825fb7a
+  0.0s  development=RUNNING     investment=RUNNING
+  2.0s  development=RUNNING     investment=COMPLETED
...
+ 54.0s  development=COMPLETED   investment=COMPLETED
Development: status=COMPLETED result=(3, 0) error=None
Investment:  status=COMPLETED result=(16, 0) error=None
```

- 서로 독립적인 lifecycle을 가졌다: Investment가 2초 내 완료된
  뒤에도 Development는 계속 RUNNING을 유지했다(하나의 완료가
  다른 것에 영향을 주지 않음, `test_dev_and_investment_run_
  concurrently_with_independent_lifecycles`로 자동 검증).
- 결과값도 정확했다: `(3, 0)`, `(16, 0)` 모두 순차 실행 baseline과
  일치.
- Task identity 필요성: 확인됨 — Dashboard가 두 Task를
  `task_id`로 구분해 동시에 관찰했다(`list_running_tasks()`가
  실행 중 2개를 반환).

**동일한 실제 대상을 동시 실행 — 결과가 오염됐다.**

이 Prototype이 원래 요구받은 검증(§14 Concurrent Execution)을
넘어, "in-process 병렬 실행 자체의 안전성"을 별도로 탐색했다
(§2에서 확인한 기존 `ThreadPoolExecutor` 패턴이 서로 다른 데이터를
병렬 처리하는 것과, **동일한 테스트 대상을 동시 실행하는 것**은
다른 위험을 가질 수 있다고 판단했기 때문). `demo.py` Part 2에서
동일 대상(`hqs/investment/tests`)을 두 Thread에서 동시에 3회
반복 실행한 결과(baseline: 순차 실행 시 16 passed):

| 시도 | Thread 1 | Thread 2 | 합계 passed | 기대값(32) 대비 |
|---|---|---|---|---|
| 1 | rc=0, 16 passed | rc=1, 15 passed, 1 failed | 31 | 오염 |
| 2 | rc=1, 15 passed, 1 failed | rc=1, 15 passed, 1 failed | 30 | 오염 |
| 3 | rc=1, 15 passed, 1 failed | rc=1, 15 passed, 1 failed | 30 | 오염 |

단순 카운트 오차가 아니었다. 실패 로그를 읽어보면 실제로
**`hqs/investment/tests/test_stock_team_integration.py`의
`monkeypatch.setattr(stock_team, "call_engine", ...)`가 스레드
간에 서로 섞였다** — 한 Thread의 테스트가 설정한 fake
`call_engine`(또는 그 호출 카운터)을 다른 Thread의 테스트가
관찰해 `assert calls["trader"] == 1`이 `assert 2 == 1`,
`assert 0 == 1`로 실패했다. 두 pytest 세션이 **동일한
`stock_team` 모듈 객체**(Python `sys.modules` 캐시)를 공유하기
때문이다 — subprocess였다면 각 세션이 독립된 프로세스 메모리를
가져 이 문제가 원천적으로 없었을 것이다(`async-command`
Prototype에서는 이 현상이 나타나지 않았다).

이 탐색은 자동 테스트 스위트에는 포함하지 않았다(재현 결과가
매번 오염 방식이 달라 결정론적 assertion을 만들기 어렵고, 목적이
"고쳐야 할 버그"가 아니라 "실제로 존재하는 위험을 관찰하는 것"이기
때문 — Refactoring Audit §16 참조). `demo.py` 실행으로 재현
가능하다.

---

## 9. Failure / Retry

`inproc_case_b.start(..., valid_path=False)`로 존재하지 않는 대상
경로를 pytest에 전달해 실제 실패(pytest exit code 4, "file or
directory not found")를 재현했다.

- Task가 FAILED로 전환되는가: 예.
- error가 보존되는가: 예(`error="return_code=4"`).
- Command는 변경되지 않는가: 예(frozen, `retry()`가 같은 Command
  객체를 그대로 참조).
- Retry 시 새로운 실행 단위가 생성되는가: 예(`task_id` 다름,
  `execution_id` 다름).
- 이전 Task와 새 Task를 구분할 수 있는가: 예(`task_id`로 구분,
  `test_retry_reuses_command_and_produces_new_task`로 자동 검증).

---

## 10. Command Immutability

Case A와 Case B를 나란히 비교했다(`test_case_a_command_cannot_
stay_frozen`, `test_case_b_command_stays_frozen`).

- Case A: `AsyncCommand`는 `frozen=True`로 선언할 수 없다 — 실행
  상태(`status`, `passed`, `failed`, `error`)를 Command 자신에게
  담아야 하므로, 외부에서도 `command.status = "MANUALLY_TAMPERED"`
  처럼 자유롭게 mutate할 수 있었다(실제로 재현).
- Case B: `Command(frozen=True)`는 실제로 `task.command.raw_input
  = "tampered"`가 `FrozenInstanceError`를 던졌다 — 불변성이 실제로
  보호됐다.

subprocess 버전과 완전히 동일한 결론이다: **Command 불변성을
지키려는 요구가 Task 필요성의 실제 원인**이며, 이는 "장시간
실행"이라는 조건과 별개로 in-process에서도 동일하게 재현됐다.

---

## 11. Dashboard Observation

`inproc_dashboard_view.py`(read-only)가 `inproc_case_b._TASK_
REGISTRY`만 읽는다. `test_dashboard_view_does_not_start_or_
control_execution`(AST 기반, `start`/`refresh`/`retry` 호출 여부
검사)과 `test_dashboard_can_observe_running_tasks_via_registry_
only`(RUNNING → 완료 후 목록에서 제외됨)로 자동 검증했다. 실제
`demo.py` 실행에서도 Dashboard가 두 HQ의 동시 RUNNING 상태를
정확히 관찰했다(§8).

---

## 12. Runtime Evaluation

**표준 Python primitive(`concurrent.futures.ThreadPoolExecutor`)로
시작했다** — 별도 Runtime을 먼저 만들지 않았다(작업 지시 §9).

이 primitive만으로 충분했는가는 대상에 따라 답이 갈렸다:

- **서로 다른 실제 대상을 동시 실행하는 경우**: 충분했다. 즉시
  반환, 정확한 결과, 독립적 lifecycle을 모두 실제로 확인했다
  (§8). → 이 범위에서는 Runtime = **NOT REQUIRED**.
- **동일한 실제 대상(또는 같은 모듈을 import/monkeypatch하는 여러
  대상)을 동시 실행하는 경우**: 충분하지 않았다. `ThreadPoolExecutor`
  자체는 정상 동작했지만, **실행되는 코드(pytest + monkeypatch)가
  공유 프로세스 메모리를 전제하지 않고 작성됐기 때문에 실제 오염이
  발생했다**(§8). subprocess였다면 이 문제가 없었을 것이다 —
  즉 in-process 실행은 "동시성을 얻는 대신 격리를 잃는다"는
  실제 trade-off가 이번에 처음으로 관찰됐다.

**Task와 Runtime의 경계(작업 지시 §10)**: 이번 Prototype에서
Task는 "무엇이 실행 중이며 그 lifecycle이 무엇인가"만 다뤘고
(§6), 실행을 실제로 어떻게 dispatch할지(어느 Thread에, 언제,
서로 격리해서)는 전부 `inproc_operation.py`(사실상 Runtime 역할을
암묵적으로 하고 있는 모듈)가 담당했다. 이번에 발견된 오염 문제는
**Task 설계를 아무리 정교하게 해도 해결되지 않는다** — Task는
실행 결과를 올바르게 "기록"할 뿐, 실행 자체가 서로를 오염시키는
것을 막을 책임(격리, 스케줄링 순서 제어)을 지지 않기 때문이다.
이는 Runtime이 Task와 **다른** 책임이라는 것을 실제로 보여주는
최초의 구체적 증거다(이전 subprocess Prototype에서는 이 구분이
관찰될 기회 자체가 없었다 — 프로세스 격리가 이미 문제를 없앴으므로).

**in-process 실행의 취소 불가능성**: `future.cancel()`은 아직
시작되지 않은 작업만 취소한다. 실행 중인 Thread를 강제 종료하는
표준 방법이 없다 — 실제로 자동 테스트에서 Dev HQ Task를 시작만
하고 함수는 즉시 반환했지만(1.31초), 프로세스 자체는 백그라운드
Thread가 끝날 때까지 종료되지 않아 실제 종료까지 59초가 걸렸다
(`time` 측정, §17). `async-command`의 `operation.terminate()`에
대응하는 기능이 in-process에는 존재하지 않는다 — 이 역시 subprocess
대비 in-process 실행의 실제 제약이다.

**판정**: Runtime = **CANDIDATE**(결과 C) — "동일 대상 동시 실행"
같은 조건에서는 표준 primitive만으로 부족하다는 것이 실제로
확인됐지만, 이번 Prototype은 그 문제를 해결하는 구조(격리 전략,
스케줄링 정책)를 설계하지 않았다(작업 지시 범위 밖 — "Task/Runtime을
만드는 작업이 아니다"). Task와의 Boundary를 별도로 검토할 필요가
있다(§18 Next Step).

---

## 13. Context Evaluation

Command/Task 외부에 지속적으로 보존해야 하는 상태가 실제로
필요해진 경우는 없었다. §8/§12에서 발견된 오염 문제도 Context
부재 때문이 아니라 **실행 대상 코드(테스트, monkeypatch)가 프로세스
전역 상태를 공유하기 때문**이었다 — Context를 추가한다고 해결되는
문제가 아니다(Context는 Command/Task가 몰라도 되는 실행 도구 내부
문제). **Context = NOT REQUIRED**(이전 Prototype과 동일 결론
유지).

---

## 14. Evidence Generated

| 요소 | 판정 | 근거 |
|---|---|---|
| Command | EXPERIMENTAL | Case A/B 비교로 불변성 요구 재확인(§10) |
| Task | **CANDIDATE**(유지) | 불변 Command 보호를 위한 실행 상태 분리 필요성 in-process에서도 재현(§6, §10) |
| Result | NOT REQUIRED | Task.result 필드로 충분, 별도 타입 불필요 |
| Dashboard | EXPERIMENTAL | Registry 조회만으로 관찰 가능, Production 승격 판단은 별도(§11) |
| Runtime | **CANDIDATE**(변경 — 이전 NOT REQUIRED에서 격상) | 동일 대상 동시 실행 시 실제 결과 오염 재현(§8, §12) |
| Context | NOT REQUIRED | 오염 문제는 Context 부재가 원인이 아님(§13) |

---

## 15. Architecture Findings

- **결과 C에 해당한다**(작업 지시 §19): Task = CANDIDATE, Runtime =
  CANDIDATE. 두 책임의 Boundary를 검토할 필요가 있다는 것이 이번
  Prototype의 핵심 발견이다.
- Task와 Runtime은 실제로 다른 문제를 다룬다: Task는 "무엇이
  실행 중인가(상태 기록)", Runtime은 "실행이 서로를 오염시키지
  않게 하는 것(격리/스케줄링)" — 이번 Prototype 이전에는 이 구분이
  가설이었지만, §8의 재현된 오염으로 실제 근거가 생겼다.
- 이 발견은 "장시간 실행"이 아니라 **"동시에 같은 것을 실행할
  가능성"**에서 나왔다 — 원래 핵심 질문(장시간 → Task 필요성)과는
  다른 축의 질문이며, 작업 지시가 이미 §8/§14에서 요구한 Concurrent
  Execution 검증 범위 안에 있다.

---

## 16. Kernel Impact

없음. Cross-HQ 공통 Responsibility가 안정적인 Boundary와 함께
확인된 것이 아니라, 오히려 "각 HQ의 테스트 코드가 프로세스 전역
상태(모듈 attribute)를 전제로 작성돼 있다"는 **HQ 내부 구현
디테일**이 원인이었다 — Kernel Candidate 기준(Cross-HQ 공통성)에
해당하지 않는다.

---

## 17. Governance Impact

없음. RFC/ADC/ADR 생성하지 않음. `core/task/`, `core/runtime/`,
`core/context/`, `core/command/` 생성하지 않음. Production Task/
Runtime 생성하지 않음.

**검증**:
- `git diff main -- hqs/ core/ dashboard/`: 0줄(Production 무수정).
- `git status`: `projects/in-process-async-command/`,
  `docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`
  외 변경 없음.
- 신규 테스트: 13 passed(`pytest projects/in-process-async-command/tests/ -q`).
- 전체 회귀: `pytest --ignore=archive -q` → **325 passed**(이전
  312 → 325, +13, 0 failed). 처음 실행 시 async-command Prototype과
  모듈 이름이 겹쳐(`operation.py` 등) 전체 회귀에서만 재현되는
  `sys.modules` 충돌이 실제로 발견됐고(README 참조), `inproc_`
  접두어로 분리해 해결한 뒤 재검증했다.

---

## 18. Next Step

두 후보 모두 우선순위 미확정 — 사용자 결정 필요.

1. **Runtime Boundary Prototype**: 이번에 발견된 "동일 대상 동시
   실행 오염" 문제를 실제로 해결하는 최소 격리/스케줄링 전략을
   설계 없이 실험(예: 동일 대상 요청은 직렬화, 서로 다른 대상만
   병렬 허용)해 Runtime 책임의 실제 경계를 좁힌다.
2. **Trading HQ 등장 시 3-HQ 재검증**: 이전 Prototype과 동일하게
   보류.

---

## 최종 보고

1. **무엇을 실행했는가**: `hqs/development/mvp/tests/test_mvp_0001.py`
   (실측 ~69초)와 `hqs/investment/tests`(실측 <1초)를
   `pytest.main()`으로 in-process(ThreadPoolExecutor Worker Thread)
   실행 — subprocess 대신 프로세스 내부에서 직접 호출.
2. **왜 이 실행을 선택했는가**: 저장소가 이미 Validation 목적으로
   반복 실행하는 실제 작업이고(async-command Prototype과 동일
   근거), `ThreadPoolExecutor` 병렬 실행 패턴 자체가 저장소에
   이미 존재해(§2) 중복 구현을 피할 수 있었다.
3. **Command-only 결과**: 동작은 했지만 실행 상태를 담기 위해
   Command를 mutable로 만들어야 했다(§5, §10).
4. **Command 불변성 결과**: subprocess 버전과 동일 — frozen=True는
   Case B(Task 분리)에서만 유지됐다(§10).
5. **Async 결과**: 서로 다른 실제 대상에 대해서는 실제로 즉시
   반환 + 독립적 동시 실행이 확인됐다(§8). 동일 대상에 대해서는
   결과가 실제로 오염됐다(§8) — 예상하지 못한 핵심 발견.
6. **Task 필요성**: 예, CANDIDATE 유지 — Command 불변성 보호
   때문(§6, §10, §14).
7. **Task lifecycle**: RUNNING→COMPLETED, RUNNING→FAILED,
   FAILED→RETRY→RUNNING→COMPLETED 모두 실제 관찰. PENDING은
   이번에도 관찰되지 않았다(§7).
8. **Failure/Retry**: 둘 다 실제로 검증됨 — 불변 Command 재사용,
   새 Task 생성(§9).
9. **Concurrent execution**: 서로 다른 대상은 정상, 동일 대상은
   오염(모듈 공유로 인한 `monkeypatch` 간섭까지 실제 재현) — §8
   참조.
10. **Dashboard 관찰**: 예, Registry 조회만으로 두 HQ의 동시 RUNNING
    상태를 정확히 관찰했다(§11).
11. **Runtime 필요성**: **조건부로 발생함(변경)** — 서로 다른
    대상 병렬 실행에는 불필요했지만, 동일 대상 동시 실행에서는
    표준 primitive만으로 부족함이 실제로 확인됐다(§12). Task
    설계로는 이 문제를 해결할 수 없다는 것도 함께 확인했다.
12. **Context 필요성**: 없음, 이전과 동일(§13).
13. **생성된 Evidence**: §14 표 참조 — Task/Runtime 모두
    CANDIDATE.
14. **Architecture Candidate**: Task, Runtime(Boundary 분리 필요,
    §15).
15. **Kernel Impact**: 없음(§16).
16. **Governance Impact**: 없음(§17).
17. **Production 승격 가능 여부**: **아니오** — Runtime Boundary가
    이번에 처음 CANDIDATE로 격상됐고 아직 설계되지 않았다. Task
    Contract도 Command/Task/Runtime 세 책임이 어떻게 나뉘는지
    확정되기 전까지는 안정적이라 보기 어렵다.
18. **다음 Implementation**: Runtime Boundary Prototype(우선) 또는
    Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정
    필요.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 신규 13 passed, 전체 저장소 325 passed(0 failed, 회귀 없음 — async-command와의 모듈 이름 충돌을 `inproc_` 접두어로 해결한 뒤 재검증)
E2E: 해당 없음(read-only, 실제 Engine/Trade 실행 없음)
RFC: 없음
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (커밋 예정)
Branch: `claude/inprocess-async-command-prototype`(계보: `claude/async-command-prototype` → `claude/command-contract-prototype` → `claude/unified-dashboard-prototype`, 전부 아직 main 미merge)
Next Implementation Candidate: Runtime Boundary Prototype(동일 대상 동시 실행 오염 문제의 최소 격리 전략 검증) 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정 필요
