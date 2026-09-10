# EVIDENCE — Runtime Prototype v1

## 목적

`docs/decisions/adc/ADC.md` ADC-02(Runtime 개념의 존폐, Open, NOW)의
최종 Decision을 내리기 전에, Runtime 추상화가 실제 Jarvis OS 실행
구조에서 유용한지 실행 Evidence로 검증한다. **Runtime을 채택·구현하지
않는다** — Baseline(Execution Host 직접 호출)과 Runtime Prototype
경로를 동일한 실제 Engine 실행 대상으로 비교 관찰할 뿐이다.

## Scope

- Execution Unit 생성/등록·실행 요청·상태 조회·종료/정리·결과
  수집(작업 지시 "Prototype 범위" 1~5).
- Baseline(Caller → Execution Host → Engine)과 Runtime Prototype
  (Caller → Runtime → Execution Host → Engine)을 **동일한 실제
  Engine 실행 대상**으로 비교.
- **명시적으로 만들지 않은 것**: Scheduler, Workflow Engine/Parser,
  Policy Engine, Agent Manager, Event Bus, Model Routing, Engine
  Gateway, Multi-Agent orchestration, 새 Public Contract, 새 Kernel
  Module, Production Runtime Architecture 확정.

## Owner

Claude Code(이 세션).

## 격리 확인 (`ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation")

- `projects/runtime-prototype-v1/`에만 존재.
- `rp_execution_host.py`/`rp_runtime.py`/`rp_target.py` 세 모듈 모두
  `hqs`/`core`/`mvp`/`dashboard`를 import하지 않음(AST 정적 검증,
  `test_no_direct_hq_or_kernel_import`) — Production Execution Host의
  Contract를 **재구현**했을 뿐 Production 모듈을 연결하지 않았다.
- `git diff --stat origin/main -- hqs/ core/` 빈 문자열 확인
  (`test_production_paths_unmodified`) — Production 무수정.
- `rp_runtime.py`가 `ProcessPoolExecutor`를 직접 참조하지 않음
  (`test_task_style_unit_module_does_not_reference_executor_classes_directly`)
  — 실제 dispatch·격리는 항상 `rp_execution_host.run_isolated()` 호출로
  위임한다(Execution Host 대체 아님).
- "실제 Engine 실행"의 의미: 실제 LLM API 호출이 아니라, 저장소의
  실제 pytest 스위트를 격리된 Worker Process에서 실행하는 것 —
  Production Execution Host 자체의 테스트(`hqs/development/mvp/tests/test_execution_host.py`),
  `runtime-boundary`/`process-runtime-strategy` Prototype이 이미
  사용해 온 것과 동일한 방법론을 그대로 재사용했다. LLM 호출(`call_engine`)을
  대상으로 삼지 않은 이유: (1) 반복 실행되는 자동화 테스트에서 비용·
  지연·네트워크 의존을 만들지 않기 위해, (2) 이 Prototype이 검증하는
  대상은 "Runtime이 실행 lifecycle을 조정하는 방식"이지 "Engine 호출
  자체"가 아니기 때문 — 어떤 함수를 실행하든 Runtime의 책임(§16.3
  Execution Host를 감싸는 lifecycle 조정)은 동일하다.

## 실행 결과

`/root/.local/bin/pytest projects/runtime-prototype-v1/tests/ -v` →
**11 passed** (0.83초).

| 파일 | 테스트 | 결과 |
|---|---|---|
| `test_baseline_direct_execution_host.py` | 단일 실행 직접 호출 | PASS — `(0, 2, 0)` |
| | 복수 실행(Caller가 직접 `ThreadPoolExecutor` 작성) | PASS — 3개 서로 다른 실제 대상 동시 실행, 결과 정확 |
| | lifecycle 조회 API 부재 확인 | PASS — raw `Future` 노출 |
| `test_runtime_prototype.py` | 단일 Execution Unit 전체 lifecycle(1~5) | PASS |
| | 실패 관찰(FAILED 상태 + 예외) | PASS |
| | 이중 start() 거부 | PASS |
| | 복수 Execution Unit 재사용(동일 API 반복) | PASS — 3개 서로 다른 실제 대상, 결과 정확 |
| | 논블로킹 상태 조회 | PASS |
| `test_isolation_guardrails.py` | HQ/Kernel import 금지 | PASS |
| | Production 무수정 | PASS |
| | Execution Host 대체 아님(Executor 미직접참조) | PASS |

Development HQ Production 회귀 기준선 재확인:
`/root/.local/bin/pytest hqs/development/mvp/tests/ -q` → **186
passed, 6 skipped**(무변경) — 이 Prototype이 Production 경로에 전혀
영향을 주지 않았음을 재확인.

전체 저장소 회귀(`pytest --ignore=archive --continue-on-collection-errors -q`):
**486 passed, 9 failed, 6 errors, 7 skipped**(71초). 9 failed·6
errors는 이 Prototype과 무관한 **기존(pre-existing) 문제**다 —
`langgraph` 모듈 미설치로 인한 6개 collection error(`workflow-adapter-*`,
`multi-agent-handoff-mvp-v1`, `omniroute-thin-engine-caller-v1`)와,
`in-process-async-command`/`omniroute-thin-engine-caller-v1`/
`process-runtime-strategy`의 기존 Experimental Prototype 안에서 발생한
타이밍 의존 테스트 실패다 — 이 목록에 `runtime-prototype-v1`은 없다
(신규 실패 0건, 이번 작업으로 인한 회귀 없음).

## Baseline vs Runtime Prototype 구조 비교

| 항목 | Baseline(Caller → Execution Host) | Runtime Prototype(Caller → Runtime → Execution Host) |
|---|---|---|
| 실행 코드 규모(모듈) | `rp_execution_host.py` 32줄(Production과 동일 Contract) | `rp_runtime.py` 114줄(신규 추가) |
| 단일 실행 호출 | `run_isolated(func, *args)` 1줄, 블로킹 | `create_unit()` → `start()` → `result()` 3단계 |
| 상태 조회 | 없음 — Caller가 raw `Future.done()`을 직접 확인해야 함 | `status(unit_id)` → `PENDING`/`RUNNING`/`DONE`/`FAILED` 문자열 |
| 복수 실행 | Caller가 매번 `ThreadPoolExecutor` + list comprehension을 직접 작성 | `create_unit`/`start`/`result`를 반복 호출 — 동시성 코드는 Runtime 내부에 이미 있음 |
| 실패 처리 | Execution Host가 예외를 그대로 raise — Caller가 매번 `try/except` | Runtime이 예외를 `FAILED` 상태 + `error` 필드로 흡수, `result()` 호출 시점에만 재발생 |
| 중복 실행 방지 | 없음(같은 Future를 두 번 기다리는 것은 안전하지만 "같은 작업을 두 번 시작"을 막는 장치 없음) | `start()` 이중 호출을 `ValueError`로 명시적 차단 |
| 자원 정리 | Execution Host의 전역 `ProcessPoolExecutor`가 프로세스 종료까지 유지(Caller가 정리할 것이 없음) | `Runtime` 인스턴스 자체를 `shutdown()`해야 함 — 새로운 자원 관리 책임 |
| 실측 소요 시간(3개 실제 대상 동시 실행) | 0.11~0.12초 | 0.08~0.12초(동등 — 둘 다 실제로는 동일한 `run_isolated` 위에서 동작) |

## Q1~Q5 평가

### Q1. 책임 분리 — Runtime을 사용하면 lifecycle 관리가 명확해지는가

**예, 명확해진다.** Baseline은 "지금 실행 중인가/끝났는가"를 raw
`Future` 객체를 직접 들고 확인해야 하고, 실패는 예외로만 드러난다.
Runtime은 이를 4가지 명시적 상태(`PENDING`/`RUNNING`/`DONE`/`FAILED`)
와 `error` 필드로 통일했고, 같은 Execution Unit을 두 번 시작하는
것을 `ValueError`로 명시적으로 막는다(`test_double_start_is_rejected`)
— Baseline에는 이 보호가 없다.

### Q2. 복잡성 — Runtime 계층을 추가함으로써 불필요하게 복잡해지는가

**실제 비용이 있다.** Runtime은 신규 코드 114줄(Execution Host
stand-in 32줄의 3.5배)을 추가했고, `ExecutionUnit` dataclass·4가지
상태·`Runtime` 인스턴스 자체의 lifecycle(`shutdown()`)이라는 새로운
개념을 도입한다. 단일 실행 시나리오(`test_single_execution_unit_direct_call`
1줄 vs `test_single_execution_unit_lifecycle` 3단계)에서는 Runtime
쪽이 오히려 더 많은 호출을 요구한다 — 단순 사용 사례에서는 Baseline이
더 간결하다.

### Q3. 재사용성 — 복수 Execution Unit 시나리오에서 중복 코드를 줄이는가

**제한적으로 그렇다.** `test_multi_execution_unit_lifecycle_reused_across_units`는
`create_unit`/`start`/`result` 세 호출만 반복하면 되지만,
`test_multi_execution_unit_requires_caller_written_concurrency`(Baseline)
도 표준 라이브러리 `ThreadPoolExecutor` + list comprehension 5줄이면
동일한 결과를 얻는다 — 이번 Prototype 규모(3개 Execution Unit)에서는
차이가 크지 않았다. Runtime의 이점은 "동시성 코드를 매 호출부마다
새로 작성하지 않아도 된다"는 것이지만, Python 표준 라이브러리
자체가 이미 그 반복을 짧게 만들어 주므로 감소 폭이 크지 않다.

### Q4. 확장성 — 향후 여러 Execution Unit을 조정할 자연스러운 확장 지점을 제공하는가

**이 Prototype의 실제 범위 안에서는 강하게 뒷받침되지 않는다.**
작업 지시가 명시한 대로 "실제로 구현하지 않은 미래 기능을 근거로
평가하지 않는다" — 이 실험이 실제로 실행한 것은 "N개 Execution
Unit을 만들고 반복문으로 start/result를 부르는 것"뿐이며, 이는
Baseline도 list comprehension으로 동일하게 표현 가능했다(Q3).
Runtime 객체가 구조적으로 향후 기능(우선순위, 취소, 배달 보장
차등화 등)을 얹기 더 쉬워 보이는 것은 사실이지만, 이번 Evidence가
**실제로 검증한 것은 아니다** — 그런 미검증 가능성을 Q4의 근거로
쓰지 않는다.

### Q5. 실제 Jarvis 적합성 — 현재 존재하는 MVP/실행 흐름에 적용했을 때 실제 문제가 해결되는가

**해결되는 실제 문제가 관찰되지 않았다.** `hqs/development/workflow.py`는
Stage를 순차 직접 함수 호출로 진행하고(`GOVERNANCE-REVIEW-0006`
9건의 Dogfooding이 반복 확인), `hqs/investment/teams/stock_team.py`는
이미 팀 코드 내부에서 `ThreadPoolExecutor`로 병렬 Wave를 직접
처리한다. 둘 다 Runtime의 "여러 Execution Unit의 lifecycle을 통합
조회"할 필요를 만들지 않는다 — Production `run_isolated`(Execution
Host)조차 현재 어떤 Production 호출부에서도 사용되지 않는다(`grep -rln
run_isolated hqs/ core/` → 자기 자신의 테스트 파일 외 0건, 이번
조사로 확인). Runtime을 그 위에 얹어도 대체할 대상 자체가 없다 —
`RFC-0028`(Phase E, Multi-Agent Handoff)이 이미 관찰한 "마찰 없음"과
같은 결론이 이번에도 반복됐다.

## 최종 평가

**NEUTRAL**

```
NEUTRAL
  Runtime abstraction works, but current Jarvis workload does not
  justify the additional abstraction.
```

Runtime Prototype은 실제로 동작했고(11/11 PASS, 실제 pytest 스위트를
Execution Host를 통해 정확히 실행·격리·결과 수집·정리), Q1(책임
분리)에서는 Baseline 대비 실질적 이점(명시적 상태, 이중 실행 방지)을
보였다. 그러나 그 이점은 지금 Jarvis OS 어디에도 아직 필요하지
않다(Q5) — Production `run_isolated`조차 호출부가 없고, 실제 동시
실행이 필요한 유일한 사례(Investment Team)는 이미 팀 코드 내부
`ThreadPoolExecutor`로 해결되어 있다. Runtime을 추가하면 코드
114줄과 새로운 인스턴스 lifecycle(`shutdown()`)이라는 실제 비용
(Q2)이 발생하지만, 그 비용을 상쇄할 실제 소비자는 이번에도 관찰되지
않았다.

이 결과는 `docs/architecture/core/GOVERNANCE-REVIEW-0009-adc-02-runtime-existence-evidence-review.md`
(C: Runtime을 상위 개념으로 유지하되 독립 구현 Component로 확정하지
않음)·`RFC-0028`(Phase E, Multi-Agent Handoff — Runtime Candidate
미발생)과 **같은 방향**이다 — 이번 Prototype이 그 결론을 실행
수준에서 다시 한번 재확인했다.

## 성공/실패/폐기 기준

- **성공 기준**(이 실험 자체에 대해): Runtime Prototype이 실제로
  실행되고 Execution Host와 정상 연결됨, 실제 Engine 실행 Evidence
  확보, Baseline 비교 완료, 테스트 통과 — **충족**(11/11 PASS).
- **Architecture 승격 기준**: ADC 채택 기준(①지금 결정 안 하면 상위
  진행 불가, ②지연 시 되돌리는 비용 급증) 중 어느 것도 충족되지
  않는다 — **미충족**. ADC-02는 이 Prototype 이후에도 Open 상태로
  유지한다(작업 지시 "Governance 제약").
- **폐기 기준**: 이 Experimental Component는 반복적 가치가 추가로
  확인되지 않는 한 RFC 없이 즉시 제거 가능하다.
