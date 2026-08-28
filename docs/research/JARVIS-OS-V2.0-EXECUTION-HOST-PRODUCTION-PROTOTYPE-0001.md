# JARVIS-OS-V2.0-EXECUTION-HOST-PRODUCTION-PROTOTYPE-0001: Execution Host Production 최소 구현 — Evidence

**문서 성격**: `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`
Conditional Accept와 `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md`
의 Scoped 허용을 근거로 진행한 **Production 구현** 완료 보고서다.
이전 5개 Experimental Prototype(`projects/` 격리)과 달리, 이번은
`hqs/development/mvp/`(Development HQ MVP Production 코드)에 실제
파일을 추가했다. 사용자가 `hqs/development/MVP.md` §Out of Scope
("Scheduler / Runtime")와의 충돌을 인지한 상태에서 명시적으로
Production 진행을 승인했다(§0).

**핵심 질문**: `ADC-0015`가 Conditional Accept한 구현 전략(Process
1차, "동일 Target 동시 실행" 조건, Thread 배제)을 실제 Production
코드로 옮겼을 때, 그 코드가 Experimental Prototype이 이미 검증한
결과(정확성·격리)를 그대로 재현하는가?

**핵심 결론**: **재현했다.** 신규 Production 모듈
`hqs/development/mvp/execution_host.py`(단일 함수
`run_isolated()`, Process 전략만)가 (1) 정상 실행 결과 반환, (2)
예외 전파, (3) 실제 pytest 대상 실행, (4) **동일 Target 동시 실행
정확성**(2/2) 네 가지를 전부 첫 시도에 통과했다. 전체 저장소 회귀
355 → **359 passed**(+4, 0 failed) — 회귀 없음.

---

## 0. MVP.md Out of Scope 충돌 — 사용자 승인 기록

`hqs/development/MVP.md`(Approved v1.0 Final) §Out of Scope는
"Scheduler / Runtime"과 "Background Execution / Distributed
Execution"을 명시적으로 배제한다. MVP-0001의 실제 Workflow(`Task 1
(code_review) → Task 2 (test_execution)`, 단일 선형·동기 체인)에는
"동일 Target 동시 실행" 조건이 현재 발생하지 않는다 — 즉 지금
시점에 Execution Host가 실제로 필요한 조건은 MVP-0001 시나리오
자체에는 없다.

이 충돌을 구현 착수 전에 사용자에게 보고했고, 사용자가 **"충돌
인지하고 Production 진행 승인"**을 명시적으로 선택했다(작업 지시,
`dev-hq-vertical-slice` Prototype §1이 남긴 것과 같은 종류의
예외 처리 선례를 따름). 이 문서는 그 예외가 이번 구현에만
적용됨을 기록한다 — MVP.md 자체를 수정하지 않았다(§7).

---

## 1. Experimental Boundary와의 차이 — 이번은 Production이다

이전 5개 Prototype(`runtime-boundary`, `process-runtime-strategy`,
`async-command`, `inprocess-async-command`, `dev-hq-vertical-slice`)
은 전부 `projects/`(Experimental, Governance 승인 불필요) 격리
안에서 진행됐다. 이번은 다르다 — `ADC-0015`/`ADR-0005`가 실제로
Governance 절차(RFC → ADC → ADR)를 완료했고, `hqs/development/
IMPLEMENTATION_RULES.md`가 Execution Host 범위를 Scoped 해제한
뒤에, 그 승인 범위 안에서 Production 코드
(`hqs/development/mvp/execution_host.py`)를 추가했다.

**Scoped 범위 준수 확인**:

- 구현 전략: **Process만**(`ProcessPoolExecutor`) — Thread 미사용,
  Subprocess는 이번에 구현하지 않음(1차 전략만으로 충분,
  `ADC-0015` §Q3가 대안으로 남긴 Subprocess는 필요 시 후속 구현).
- 비동기 lifecycle(PENDING/RUNNING 상태 조회) 미구현 — 동기 블로킹
  호출만 제공한다. `MVP.md` "Background Execution / Distributed
  Execution" Out of Scope를 넘지 않기 위한 의도적 설계 제약이다.
- Scheduler/Task Registry/Multi-Task orchestration 미구현.
- 새 Public Interface/Contract 미정의 — `run_isolated(func, *args,
  **kwargs)` 단일 함수만 노출, Kernel Public Contract(§14) 무관.
- `hqs/development/mvp/cli.py`(실제 code_review→test_execution
  흐름)에는 연결하지 않았다 — MVP-0001 시나리오 자체가 동시 실행을
  만들지 않으므로(§0), 억지로 연결하면 불필요한 결합만 생긴다.

---

## 2. 구성 요소

| 파일 | 책임 | 근거 |
|---|---|---|
| `hqs/development/mvp/execution_host.py` | `run_isolated(func, *args, **kwargs)` — Process Worker에서 격리 실행 후 블로킹 반환 | `BASELINE.md` §16.3, `ADC-0015` |
| `hqs/development/mvp/tests/_pytest_target.py` | 테스트용 pytest 실행 헬퍼(`ProcessPoolExecutor`로 전달되려면 모듈 최상위 함수여야 함) | `projects/runtime-boundary/rtb_runtime.py`의 `_run_pytest`와 동일한 이유로 분리 |
| `hqs/development/mvp/tests/test_execution_host.py` | Production 모듈 검증(4 tests) | 아래 §3 |

`rtb_runtime.py`/`rtb_task.py`의 코드를 그대로 복사하지 않았다 —
Task(identity/lifecycle)는 이번 Scoped 허용 범위 밖이므로
Execution Host(dispatch·격리)만 최소로 옮겼다.

---

## 3. 검증(전부 첫 시도 통과 — 재현 없이 실패한 항목 없음)

```
hqs/development/mvp/tests/test_execution_host.py::test_run_isolated_returns_correct_result PASSED
hqs/development/mvp/tests/test_execution_host.py::test_run_isolated_propagates_exceptions PASSED
hqs/development/mvp/tests/test_execution_host.py::test_run_isolated_executes_real_pytest_target PASSED
hqs/development/mvp/tests/test_execution_host.py::test_run_isolated_is_accurate_on_identical_target_concurrent_execution PASSED
4 passed in 0.44s
```

- **정상 실행/결과 반환**: `run_isolated(_add, 2, 3) == 5`.
- **예외 전파**: `run_isolated(_boom)`이 `ValueError`를 그대로
  전파(`future.result()`가 Worker Process의 예외를 재발생시킴).
- **실제 pytest 대상 실행**: `hqs/investment/tests/
  test_stock_team_integration.py`(2 tests, `runtime-boundary`/
  `process-runtime-strategy`가 동일 Target 오염 재현에 쓴 것과 같은
  대상)를 Worker Process에서 실행, `(passed, failed) == (2, 0)`.
- **동일 Target 동시 실행 정확성**(§16.3 핵심 책임 재확인): 같은
  Target을 `ThreadPoolExecutor`(호출자 측, `execution_host.py`
  내부가 아님)로 2개 동시 호출 → 둘 다 `run_isolated`를 통해 각자
  독립된 Process에서 실행됨 → 2/2 정확(`(2,0)`, `(2,0)`) — 오염
  0건. 이는 `runtime-boundary` §4(5/5 정확)·`process-runtime-
  strategy` §4(3/3 정확)가 Experimental에서 반복 관찰한 것과 동일한
  결과이며, 이번엔 Production 모듈로 재현했다는 것이 새로운 사실
  이다.

---

## 4. 회귀 검증

- 신규 테스트: 4 passed(`pytest hqs/development/mvp/tests/
  test_execution_host.py -q -s`, 0.44초).
- 전체 회귀: `pytest --ignore=archive -q` → **359 passed**(이전
  355 → 359, +4, 0 failed, 220.03초) — `dev-hq-vertical-slice`
  Prototype 이후 베이스라인(355)에서 회귀 없이 정확히 +4.
- `git diff --stat -- core/ dashboard/ hqs/investment/`: 0줄 —
  Execution Host 범위 밖 Production 코드는 무수정.
- `git status`: 신규 3개 파일(§2) 외 변경 없음.

---

## 5. Architecture Findings

- Experimental Prototype이 검증한 정확성·격리 결과는 Production
  코드로 옮겨도 그대로 재현된다 — 새로운 위험이 발견되지 않았다.
- `run_isolated()`를 동기(블로킹)로만 제한한 설계가 실제로
  충분했다 — 4개 테스트 모두 비동기 lifecycle 없이도 검증
  가능했다. `MVP.md`의 "Background Execution" Out of Scope를
  지키면서도 §16.3의 핵심 책임(정확성·격리)은 훼손되지 않았다.
- **MVP-0001 실제 Workflow에는 이 모듈을 호출할 지점이 없다** —
  정직하게 기록한다(`dev-hq-vertical-slice` §8과 동일한 종류의
  솔직한 기록). `execution_host.py`는 검증된 상태로 존재하지만,
  `cli.py`의 실제 code_review→test_execution 흐름에 아직 연결되지
  않았다 — 연결이 필요해지는 시점(동일 대상 동시 요청이 실제로
  발생하는 시점)은 이 문서가 예단하지 않는다.

---

## 6. Kernel Impact

없음. 이 구현은 `ADC-0013`/`ADR-0003`(존재)·`ADC-0014`/`ADR-0004`
(명칭)·`ADC-0015`/`ADR-0005`(구현 전략)가 이미 확정한 책임과 전략을
Production 코드로 옮겼을 뿐, 새 Kernel Responsibility를 발견하지
않았다.

---

## 7. Governance Impact

- RFC/ADC/ADR: **불필요** — `ADC-0015`/`ADR-0005`가 이미 승인한
  Scoped 범위 안에서 진행됐다.
- `MVP.md`는 수정하지 않았다 — §0의 충돌은 사용자 승인으로
  예외 처리됐을 뿐, MVP.md 문서 자체의 Out of Scope 목록은 그대로
  유지된다. 향후 이 충돌을 정식으로 해소하려면(예: MVP.md
  Out of Scope에서 "Runtime"을 Execution Host 범위만큼 좁히는
  개정) 별도 절차가 필요하다 — 이 문서는 그 절차를 열지 않는다.
- `hqs/development/IMPLEMENTATION_RULES.md`: 무수정(`ADR-0005`가
  이미 Scoped 허용을 반영했으므로 추가 변경 불필요).
- Scheduler/Multi-Task/Workflow, §6 넓은 Runtime 구현: 여전히
  금지 상태 그대로.

---

## 8. Next Step

우선순위 미확정 — 사용자 결정 필요.

1. **MVP.md Out of Scope 정식 개정**: §0의 충돌을 예외 승인이
   아니라 문서 자체의 개정으로 해소할지(별도 RFC/승인 절차).
2. **`cli.py` 연결 여부**: MVP-0001 시나리오에 실제 동시 실행
   요청이 생기기 전까지는 연결하지 않는 것을 권고(§5) — 필요가
   생기면 그때 연결.
3. **Subprocess 대안 구현**: `ADC-0015` §Q3가 대안으로 남긴
   Subprocess는 이번에 구현하지 않았다 — 필요 시 별도 추가.
4. **비용 실측**: `ADC-0015` §Risks가 남긴 Gap — Production
   모듈 기준으로도 아직 측정하지 않았다.

---

## 최종 보고

`ADC-0015`/`ADR-0005`가 Scoped 승인한 범위(Process 1차, "동일
Target 동시 실행" 조건, Thread 배제) 그대로 `hqs/development/mvp/
execution_host.py`를 Production에 추가했다. `hqs/development/
MVP.md`의 Out of Scope("Scheduler / Runtime")와 충돌한다는 것을
구현 전에 사용자에게 보고했고, 사용자가 그 충돌을 인지한 채
Production 진행을 명시적으로 승인했다. 신규 테스트 4건이 정확성·
예외 전파·실제 pytest 대상 실행·동일 Target 동시 실행 정확성을
전부 첫 시도에 통과했고, 전체 회귀는 355 → 359(+4, 0 failed)로
회귀 없음을 확인했다. Experimental Prototype이 검증한 결과가
Production 코드로도 그대로 재현된다는 것이 확인됐지만, MVP-0001의
실제 Workflow에는 아직 이 모듈을 호출할 지점이 없다는 것을
정직하게 기록한다 — 억지로 연결하지 않았다. Kernel/§6/Scheduler/
Multi-Task/Workflow 범위는 전혀 건드리지 않았다.

---

Architecture Change: 없음(기존 §16.3/ADC-0015가 이미 Accept·Decide)
Contract Change: 없음
Production Code Change: **있음** — `hqs/development/mvp/execution_host.py`,
`hqs/development/mvp/tests/_pytest_target.py`,
`hqs/development/mvp/tests/test_execution_host.py` 신규 추가.
`core/`, `dashboard/`, `hqs/investment/`, 기존 `hqs/development/mvp/`
파일은 무수정
Tests: 신규 4 passed, 전체 저장소 359 passed(0 failed, 회귀 없음 — 이전 355 대비 +4)
E2E: 해당 없음(단위 테스트만, 실제 Engine/Trade 실행 없음)
RFC: 없음(ADC-0015/ADR-0005가 이미 승인)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Branch: `claude/execution-host-process-prototype`(main에서 분기, ADR-0005 merge 이후)
Next Implementation Candidate: MVP.md Out of Scope 정식 개정, cli.py 연결 여부, Subprocess 대안 구현, 비용 실측 — 우선순위 미확정, 사용자 결정 필요
