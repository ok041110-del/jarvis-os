# JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001: Async / Long-running Command Experimental Prototype — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, 기존 Runtime/Engine/
Workflow, `BASELINE.md`를 수정하지 않는다.

**핵심 질문**: "실행이 즉시 끝나지 않는 순간, Command만으로는 무엇을
표현할 수 없게 되는가?"

**핵심 결론**: **Task는 이 조건(장시간·비동기)에서 실제로 독립적인
책임을 가졌다** — 단, 그 이유는 "실행 시간이 길어서"가 아니라
**"Command를 불변 요청 기록으로 유지하려면 변하는 실행 상태를 담을
별도 장소가 필요하기 때문"**이었다. Case A(Command만)는 실제로
동작했지만, 그 대가로 Command Contract Prototype이 확립한
"Command는 불변"이라는 설계 원칙을 깨야 했다. Context와 Runtime은
이번 조건에서도 여전히 **NOT REQUIRED**였다.

---

## 1. Objective

`JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001.md`가 남긴 핵심
Gap("비동기/장시간 Command가 등장하면 Task 필요성 결론이 달라질
가능성이 높다")을 실제 장시간 작업으로 검증한다. Task Architecture를
미리 설계하지 않고, Case A(Command만)를 먼저 구현해 막히는 지점을
관찰한 뒤에만 Case B(Task)를 만들었다(작업 지시 §25 순서 그대로
준수).

---

## 2. Existing Evidence

- Command/Task/Context/Conversation/Runtime 관련 기존 코드: 저장소
  전체에 **없음**(작업 지시 §2 검색 완료, 이전 Command Contract
  Prototype Evidence §2와 동일 결론 재확인).
- `docs/architecture/core/STRUCTURE.md`는 존재하지 않는다 —
  `STRUCTURE-V1.0-FROZEN.md`가 실제 Source of Truth(이전 Prototype과
  동일하게 재확인).
- 기존 subprocess/CLI 실행 방식: `hqs/development/mvp/cli.py`(실제
  Engine 호출), `hqs/investment/run.py`(실제 Engine 호출) — 둘 다
  실제 투자/코드 생성 부작용이 있어 이번 Prototype의 Long-running
  Operation으로 **직접 쓰지 않았다**(작업 지시 §14 "실제 Production
  데이터나 투자 주문을 사용하지 않는다" 준수). 대신 저장소가 이미
  Validation 목적으로 반복 실행하는 `pytest`를 선택했다(§5).
- checkpoint/result 구조: `hqs/investment/checkpoint.py`의
  `Checkpointer`(파일 기반 완료 단계 추적)가 이미 유사한 lifecycle
  개념(단계 완료 여부)을 갖고 있음을 확인했으나, 이 Prototype은
  그 코드를 import하지 않고(Boundary) 독립적으로 재구현했다 — 다만
  "완료된 것은 재실행하지 않는다"는 원칙은 참고했다(Retry 설계,
  §9).

---

## 3. Experimental Boundary

- 위치: `projects/async-command/`(격리).
- `hqs/`, `core/`, Production `dashboard/`, 기존 Runtime/Engine/
  Workflow: **무수정**(`git diff` 확인).
- 신규 dependency: **0개**(stdlib: `subprocess`, `uuid`, `time`,
  `dataclasses`).
- 의존: `projects/command-contract/resolver._detect_hq`(재사용,
  중복 구현 금지) — 이 Prototype은 `claude/command-contract-
  prototype` 브랜치(→ `claude/unified-dashboard-prototype`) 위에서
  작업했다.
- 실제 투자 주문/Trade Execution 없음, 실제 Dev HQ Workflow(코드
  생성) 실행 없음 — Long-running Operation은 **읽기 전용 검증
  작업**(pytest)뿐이다.

---

## 4. Long-running Operation

**선택**: `pytest hqs/development/mvp/tests -q`(Dev HQ), `pytest
hqs/investment/tests -q`(Investment HQ) — 작업 지시 §5 우선순위
4("기존 테스트에서 실행 시간이 충분한 Workflow")에 해당.

**실측**:

| HQ | 소요 시간 | 결과 |
|---|---|---|
| Development(단독 실행) | 69.99초 | 120 passed |
| Development(Investment와 동시 실행, `demo.py`) | 88초 | 120 passed(동시 실행으로 인한 CPU 경합으로 단독 대비 +18초 — 실제로 관찰된 부작용, 조작하지 않음) |
| Investment(단독) | 0.10초 | 16 passed |

Dev HQ 우선(70초+)이 Async 검증에, Investment HQ(<1초)가 전체
lifecycle(시작→완료) 반복 검증에 각각 쓰였다 — 작업 지시 §16이
허용한 "실제로 안전하게 제공 가능한 HQ 선택"을 그대로 적용했다.
Investment HQ의 실제 거래 실행은 어디에도 없다(§3).

---

## 5. Case A — Command Only

`case_a_command_only.py`의 `AsyncCommand`가 `raw_input`과 함께
`execution_id`/`status`/`started_at`/`result`/`error`를 직접
보유한다.

**실측(자동 테스트 `test_dev_hq_operation_does_not_return_immediately_
with_result`)**: `start()` 호출 직후 `status == "RUNNING"`, 그 직후
`refresh()`를 한 번 더 호출해도 여전히 `RUNNING`(120개 테스트가 그
사이 끝날 수 없음) — Command가 **즉시 결과를 반환하지 않는다**는
전제가 실증됐다(Q1 조건 성립).

**Q1 판정**: Command 단독으로 실행 상태를 표현하는 것 자체는
**가능했다** — `AsyncCommand`가 동작했고 완료까지 이어졌다
(`test_case_a_full_lifecycle_completes`). 그러나 §12에서 확인하듯
이 방식은 실제 대가를 요구했다.

---

## 6. Case B — Command + Task

`case_b_command_task.py`는 `Command`를 `frozen=True`로 되돌리고,
`Task`가 `task_id`/`execution_id`/`status`/`result`/`error`를
소유한다. `_TASK_REGISTRY`가 `task_id`만으로 조회 가능하게 한다.

**Case A/B 실측 비교(동일 Investment HQ 입력)**:

| 기준 | Case A | Case B |
|---|---|---|
| 실행 식별 | `execution_id`(Command 내부 필드) | `task_id`(Registry key) |
| 실행 상태 | Command가 직접 보유 | Task가 보유 |
| 결과 추적 | Command.result | Task.result |
| 실패 표현 | Command.error | Task.error(Command와 분리, §8) |
| 재실행 | 원본 raw_input을 Command에서 다시 읽어야 함(mutate된 상태일 수 있어 신뢰 불확실) | 원본 `Command`가 불변이므로 그대로 재사용(`retry()`가 `old_task.command`를 그대로 넘김) |
| Dashboard 표시 | **불가능**(§11) | **가능**(Registry 조회) |
| Command 재사용 | Command 자체가 실행 상태로 오염돼 "순수 요청"으로 재사용 불가 | Command는 항상 순수 요청 그대로 유지 |
| 구조 복잡도 | 낮음(파일 1개, 클래스 1개) | 약간 높음(클래스 2개 + Registry) |

---

## 7. Async Execution

`operation.start_operation()`은 `subprocess.Popen`을 호출한 뒤
**대기하지 않고 즉시 반환**한다 — Python stdlib의 `subprocess`
모듈이 이미 이 비동기성을 제공하므로, 별도의 Thread/asyncio/Runtime
구현이 전혀 필요하지 않았다. `demo.py` 실행에서 Investment(0.1초)와
Development(70초+) 두 Operation이 **동시에** RUNNING 상태였음을
직접 관찰했다(§4의 88초 결과, 두 프로세스가 실제로 병렬 실행됨).

**Synchronous 대비 새로 발생한 책임**(§10 비교): "즉시 반환됨"
자체가 동기 방식에는 없던 새 사실이며, 이로 인해 **폴링(polling)**
이라는 별도 호출 패턴이 필요해졌다 — `resolve()`(Command Contract
Prototype, 동기)는 한 번 호출하면 끝이었지만, 이번엔 `start()` +
반복 `refresh()`(또는 `poll()`) 두 종류의 호출이 필요했다. 이
자체는 Task를 요구하지 않는다(Case A도 폴링이 가능했다) — 폴링은
비동기의 결과이지 Task의 존재 이유가 아니다.

---

## 8. Lifecycle / Result

관찰된 상태: `RUNNING → COMPLETED` 또는 `RUNNING → FAILED`.
**`PENDING`은 실제로 한 번도 관찰되지 않았다** — `start()`가
`subprocess.Popen()` 호출 직후 곧바로 `RUNNING`으로 설정하기
때문에, "시작 대기 중"이라는 상태가 이 Prototype 조건(로컬
subprocess, 즉시 스폰)에서는 발생하지 않았다. `Task.status`의
기본값으로 `PENDING`을 선언해뒀지만 **미사용 상태로 확인됐다** —
Refactoring Audit(§13)에서 이 사실을 그대로 기록한다(대기열/동시
실행 수 제한이 있는 환경에서는 다시 필요해질 수 있으나, 이번
Prototype Evidence로는 정당화되지 않는다).

`Result`(성공 시 `task.result`)와 `Failure`(실패 시 `task.error`)는
**서로 다른 필드로 명확히 분리**됐다 — 같은 실행이 결과와 실패를
동시에 가질 수 없음을 `test_failure_is_observable_and_
distinguishable_from_result`로 확인(`result is None`일 때만
`error`가 채워짐, 반대도 마찬가지). Result를 Task와 별도 Entity로
분리할 필요는 **발견되지 않았다** — `task.result`/`task.error`
필드만으로 충분했다(NOT REQUIRED).

**버그 수정 기록(투명성)**: 최초 구현은 완료 후 두 번째
`poll()` 호출 시 `subprocess.stdout.read()`를 다시 실행해 빈
문자열을 반환하는 버그가 있었다(실제 `demo.py` 실행에서 Investment
HQ의 `result`가 `''`로 관찰되어 발견) — `_Execution.cached_status`로
완료 상태를 캐싱해 해결했다. 수정 후 idempotent 재조회를 직접
검증했다(§ 수동 재현: 4회 연속 poll, 2회차부터 동일 `result`
반환).

---

## 9. Failure / Retry

**Failure**: Investment HQ 대상으로 존재하지 않는 테스트 파일
경로를 사용해 실제 pytest 실패(exit code 4, "file or directory not
found")를 재현했다 — `sleep()`이나 인위적 예외가 아니라 실제 CLI
오류다. `Command`(불변)는 실패해도 그대로 살아 있고, `Task.status
== "FAILED"`, `Task.error`에 원인이 보존됐다(`test_failure_is_
observable_and_distinguishable_from_result`).

**Retry**: `case_b.retry(task_id)`가 실패한 Task의 **불변
Command**를 그대로 재사용해 새 `Task`(새 `task_id`)를 만들고 올바른
경로로 재시작 — 재시도가 성공적으로 COMPLETED에 도달함을 확인
(`test_retry_reuses_command_and_produces_new_task`). Command가
불변이었기 때문에 "원래 무엇을 요청했는지"를 재조립할 필요가
없었다 — 이것이 Case A 대비 Case B의 실질적 이점이었다(§12).

복잡한 Retry Engine(자동 재시도 횟수 제한, 지수 백오프 등)은
구현하지 않았다 — 이번 Evidence는 "1회 수동 retry가 성립하는가"만
확인했고, 그 이상의 정책 필요성은 관찰되지 않았다(작업 지시 §13
원칙 준수).

---

## 10. Dashboard Observation

`dashboard_view.list_running_tasks()`는 `case_b_command_task.
_TASK_REGISTRY`를 읽기만 한다 — `start`/`refresh`/`retry`를 호출하지
않음을 AST 기반 테스트로 강제했다(`test_dashboard_view_does_not_
start_or_control_execution`).

**Q5 판정**: **Case B에서만 가능했다.** `demo.py` 실행에서 Dashboard
가 진행 중인 Investment/Development 2개 Task를 Registry로 나열했고,
완료 후 다시 관찰했을 때 목록에서 자동으로 빠졌다(§4 실측 로그
참조). **Case A에는 이 관찰이 원천적으로 불가능하다** —
`AsyncCommand`를 위한 전역 Registry가 없으므로, Command 객체
참조를 누군가 계속 들고 있지 않으면 실행 중인 작업 목록 자체를
얻을 방법이 없다(`test_case_a_has_no_equivalent_registry`로 확인).
이것이 이번 Prototype에서 Task의 존재 이유를 가장 명확하게
보여주는 지점이다.

---

## 11. Context Evaluation

이번 조건(장시간·비동기·Failure/Retry 포함)에서도 Context가
필요해지는 지점을 찾지 못했다:

- Retry는 Task의 `command` 참조(불변)만으로 충분했다 — Command
  외부의 "이전 상태/정보"를 별도로 보존할 필요가 없었다.
- Multi-HQ 동시 실행(Investment + Development)도 각 Task가
  독립적으로 자신의 `execution_id`만 들고 있으면 됐다 — HQ 간
  공유해야 할 상태가 없었다.
- Dashboard Observation도 Task Registry만으로 충분했다 — 별도
  Context 계층이 필요하지 않았다.

**판정: NOT REQUIRED**(이번 Prototype 범위) — 작업 지시 §15 원칙
그대로 적용, Candidate로도 기록하지 않는다.

---

## 12. Evidence Generated

| 요소 | 판정 | 근거 |
|---|---|---|
| Command(장시간 조건에서도 독립 Model 유지 가치) | **EXPERIMENTAL** | Case A/B 둘 다에서 "요청 파싱" 책임은 유지됨. 다만 장시간 조건이 Command에 추가한 것은 없음 — Command Contract Prototype의 결론을 그대로 계승 |
| Task(별도 Execution Entity 필요성) | **CANDIDATE** | §6·§10에서 실측 — Registry 조회(Dashboard Observation)와 Command 불변성 보존(Retry) 둘 다 Task가 있을 때만 성립했다. 반복 관찰(Command Contract Prototype에서도 "read-only 범위에선 불필요"였다가, 이번 "장시간+Multi 관찰+Retry" 범위에서 "필요"로 전환된 것 자체가 **조건에 따라 달라지는 책임**이라는 명확한 Evidence) |
| Result(Task와 별도 관리 필요성) | **NOT REQUIRED** | §8 — `task.result`/`task.error` 필드로 충분 |
| Context(별도 필요성) | **NOT REQUIRED** | §11 |
| Dashboard(공통 Snapshot 확장 필요성) | **EXPERIMENTAL** | `dashboard_view.py`가 기존 `unified-dashboard`의 `HQSnapshot`과는 별도로 "실행 중인 Task 목록"이라는 새 View를 필요로 했다 — `HQSnapshot`(정적 상태)과 Task 목록(동적 실행)은 서로 다른 질문에 답한다는 것이 실측됨. Contract 확정은 아직 이르다 |
| Runtime(비동기 실행을 위한 별도 Component 필요성) | **NOT REQUIRED** | §7 — Python stdlib `subprocess`가 이미 비동기성을 제공했다. Thread Pool/Scheduler/core/runtime/ 어느 것도 필요하지 않았다. **단, 이 결론은 "subprocess로 위임 가능한 작업" 범위에 한정된다** — 프로세스 내부(in-process) 비동기 작업(예: 실제 async Engine 호출)에는 재검증이 필요할 수 있다(§16) |

---

## 13. Architecture Findings

- **Task의 필요성은 "장시간"이 아니라 "Command 불변성을 지키려는
  요구"에서 나왔다.** 이는 작업 지시가 예상한 인과관계("장시간 →
  Task 필요")를 그대로 확인한 것이 아니라, 더 정밀한 인과관계
  ("Command를 Value Object로 유지하려는 설계 원칙 → 변경 가능한
  실행 상태를 위한 별도 place 필요 → Task")를 실측으로 발견한
  것이다.
- **Command Contract Prototype과 이번 Prototype의 판정 차이 자체가
  Evidence다.** 이전 Prototype(read-only, 동기)은 Task를 NOT
  REQUIRED로 판정했고, 이번(비동기, Failure/Retry, Multi-HQ 관찰)은
  CANDIDATE로 판정했다 — 이는 "Task는 무조건 필요/불필요"가 아니라
  **"Command가 감당할 수 있는 책임의 경계"가 실행 조건에 따라
  달라진다**는 것을 보여준다.
- `PENDING` 상태가 이번 조건에서 미사용으로 확인된 것(§8)은
  "언젠가 필요할 것 같아서" 만든 상태값이 실제로는 검증되지 않을
  수 있다는 구체적 사례다 — Refactoring Audit(§14)에서 유지 여부를
  판단한다.
- Dashboard가 `HQSnapshot`(정적)과 별도로 Task 목록(동적)을
  필요로 한 것(§10)은 향후 공식 Dashboard Contract가 두 종류의
  View를 모두 지원해야 할 수 있다는 최초 Evidence다 — 지금 Contract
  를 확정하지 않는다.

---

## 14. Refactoring Audit

- **Command/Task 책임 중복**: Case A와 Case B가 같은 로직(HQ 파싱,
  Operation 시작/폴링)을 두 번 구현한 것처럼 보이지만, 이는 의도된
  **비교 실험**이다(작업 지시 §8) — 최종 채택은 Case B이며, Case A는
  "왜 Case B가 필요한지"를 보여주는 대조군으로 남겨둔다(삭제하지
  않음, Evidence 보존).
- **불필요한 ID**: `command_id`는 추가하지 않았다(Command는 여전히
  값으로 비교됨, identity 불필요) — `task_id`만 필요했다.
- **과도한 lifecycle state**: `PENDING`이 미사용으로 확인됨(§8) —
  다음 세션에서 실제로 대기열이 필요해지기 전까지 이 상태값을
  Production Contract에 넣지 않는다는 점을 명시적으로 기록한다
  (지금 코드에서 제거하지는 않는다 — Case A/B 비교의 완결성을 위해
  Prototype 코드 자체는 보존).
- **Task를 만들기 위해 Task를 만들었는가**: 아니오 — §6·§10·§12가
  보여주듯 Task는 구체적 질문(Dashboard Observation, Command
  불변성)에 답하기 위해 만들어졌고 실제로 답했다.
- **Prototype 외부 dependency**: `command-contract`의
  `_detect_hq` 재사용 1건, 신규 stdlib 외 dependency 0건.
- **Production Code 침범**: 없음(`git diff` 확인).
- **HQ 내부 Logic 유출**: 없음(AST 테스트로 강제).
- **Dashboard가 execution을 관리하는지**: 아니오(AST 테스트로 강제).

---

## 15. Kernel Impact

**없음.** `core/` 어디에도 의존하지 않았다. Task Scheduler/
Dependency Resolver/Worker Manager/Event Bus/Runtime/Memory Engine/
Agent Manager/Kernel Component 중 어느 것도 만들지 않았다(작업
지시 §23 금지 목록 준수). Investment HQ와 Development HQ 양쪽에서
동일한 Task 구조가 반복 사용된 것은 관찰됐지만(§9의 Multi-HQ
실행), 이는 **이 Prototype 내부의 재사용**이지 저장소 전체에서
반복 관찰된 Cross-HQ 공통 Responsibility(BASELINE §11 Kernel 정의
기준)에는 아직 못 미친다 — **KERNEL CANDIDATE는 임의로 생성하지
않는다**(작업 지시 §18 원칙). Phase 7은 이 Prototype으로 재개되지
않는다.

---

## 16. Governance Impact

- RFC/ADC/ADR: **불필요** — Experimental Implementation 절의 허용
  범위 안에서 진행됐다.
- 이번 Prototype의 Evidence(§12)는 그 존재만으로 Formal Architecture
  Decision이나 Kernel 승격을 발생시키지 않는다.
- `BASELINE.md`, Structure v1.0, Dev HQ/Investment HQ Freeze 문서:
  **무수정**.
- 기존 Governance상 반드시 필요한 새 문서는 발견되지 않았다 — Task가
  CANDIDATE로 판정됐지만(§12), 이는 "다음에 검토할 대상"이지
  "지금 RFC를 열어야 한다"는 뜻이 아니다(Command Need 원칙,
  `ARCHITECTURE_GOVERNANCE.md` "Architecture Need" 절 — "Need 발생
  ≠ 승인").

---

## 17. Next Step

**Production Command/Task API로 승격하지 않는다**(작업 지시 §24).
`core/task/`, `core/runtime/`, `core/context/`, `core/command/`를
만들지 않았다.

**남은 Gap**(§16 참조):

- 이번 결론(Runtime NOT REQUIRED)은 **subprocess로 위임 가능한
  작업**에 한정된다 — 실제 in-process 비동기 Engine 호출(예:
  `call_engine()`을 비동기로 여러 개 동시 호출)이 Command 대상이
  되면 Runtime 필요성이 다시 검증 대상이 될 수 있다.
- `Task`가 CANDIDATE로 승격했지만, 지금 시점에 Contract를
  Freeze하기엔 표본이 여전히 작다(2개 HQ, 1개 intent, 1회
  Failure/Retry 사이클). Cross-HQ 반복(3번째 HQ 등장 등)이 있어야
  Kernel 질문(BASELINE §11)을 다시 검토할 수 있다.
- `dashboard_view.py`가 드러낸 "정적 Snapshot vs 동적 Task 목록"
  구분이 `HQDashboardSnapshot`(Dashboard Architecture Review
  Contract Candidate) 설계에 반영돼야 하는지는 아직 판단하지
  않는다.

**후보(우선순위 미확정)**: 실제 in-process 비동기 Command
Prototype(Runtime 재검증) 또는 Trading HQ 등장 시 3-HQ 재검증(기존
두 Prototype과 동일 트리거).

---

## Self Review

- Production Command/Task/Context Engine을 구현했는가 — **아니오**.
- Global Orchestrator/Scheduler/Dependency Resolver/Worker Manager/
  Event Bus/Runtime/Memory Engine/Agent Manager/Kernel Component를
  만들었는가 — **아니오**.
- 실제 Trade Execution/Investment Order/Dev HQ Workflow(코드
  생성/수정)를 실행했는가 — **아니오**(read-only 테스트 실행뿐).
- Production Dashboard를 변경했는가 — **아니오**.
- Task를 미리 설계하고 Case A를 형식적으로만 거쳤는가 — **아니오**
  (§5에서 Case A를 실제로 완주시켜 완료까지 확인한 뒤, §6에서 그
  한계를 §10·§12 Evidence로 뒷받침해 Case B를 만들었다).
- `sleep()`으로 가짜 장시간 작업을 만들었는가 — **아니오**(실제
  `pytest` subprocess, 실측 시간 §4).
- Runtime 필요성이 나타나자마자 `core/runtime/`을 만들었는가 —
  **아니오**(오히려 NOT REQUIRED로 판정, §7·§12).
- Kernel Candidate를 임의로 만들었는가 — **아니오**(§15).
- 전체 회귀 테스트를 실제로 실행했는가 — **예**(312 passed, §Validation).

---

## 최종 보고

1. **무엇을 실행했는가**: `pytest hqs/development/mvp/tests -q`
   (실측 ~70~90초, 120 passed)와 `pytest hqs/investment/tests -q`
   (실측 <1초, 16 passed)를 subprocess로 비동기 실행.
2. **왜 이 작업을 Long-running Case로 선택했는가**: 저장소가 이미
   Validation 목적으로 반복 실행하는 실제 작업이고(Dashboard
   Prototype의 "Latest Validation"과 동일 근거), 실제 투자/코드
   변경 부작용이 없어 안전했다(작업 지시 §5·§14).
3. **Command-only 구조의 결과**: 동작은 했으나(§5), Command를
   `frozen=True`로 유지할 수 없게 만들어 이전 Prototype이 확립한
   설계 원칙과 충돌했다(§12).
4. **Async가 실제로 필요했는가**: 예 — `subprocess.Popen`이 이미
   제공하는 비동기성을 그대로 썼고, 두 HQ가 실제로 동시 RUNNING
   상태였다(§4·§7).
5. **Task가 필요했는가**: **예, 조건부로** — Dashboard Observation
   (Registry 조회)과 Command 불변성 보존(Retry) 두 가지 구체적
   책임에서 Case A가 할 수 없는 것을 Case B가 해냈다(§10·§12,
   **CANDIDATE** 판정).
6. **어떤 lifecycle이 발생했는가**: `RUNNING → COMPLETED`/`FAILED`
   만 실제로 관찰됨, `PENDING`은 미사용으로 확인(§8).
7. **Failure/Retry가 필요했는가**: 예 — 실제 pytest 실패(잘못된
   경로)와 그 재시도를 둘 다 실측 검증했다(§9).
8. **Dashboard에서 실행 상태를 관찰할 필요가 있었는가**: 예 — Case
   B에서만 가능했고, `demo.py`로 2개 HQ의 동시 RUNNING 상태를 실제
   관찰했다(§10).
9. **Context가 필요했는가**: **아니오**(§11, NOT REQUIRED).
10. **Runtime 필요성이 발생했는가**: **아니오**(§7·§12) — 단
    subprocess 기반 작업에 한정된 결론(§17 Gap).
11. **생성된 Evidence**: §12 표 6개 요소 전체 판정 + Case A/B 실측
    비교표(§6).
12. **Architecture Candidate**: `Task`(CANDIDATE, §12), Dashboard
    의 동적 View 필요성(EXPERIMENTAL, §12) — 둘 다 RFC 승격 근거로
    삼기엔 표본 부족.
13. **Kernel Impact**: 없음(§15).
14. **Governance Impact**: 없음(§16, Experimental Implementation
    범위 안에서 진행).
15. **Production 승격 가능 여부**: **아니오** — in-process 비동기
    Command라는 핵심 Gap이 미검증(§17).
16. **다음 Implementation**: in-process 비동기 Command Prototype
    (Runtime 재검증) 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위
    미확정.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음(`projects/async-command/`만 신규 추가, `hqs/`·`core/`·`dashboard/` 무수정)
Tests: `projects/async-command/tests/` 14 passed(신규), 전체 저장소 312 passed(기존 298 + 신규 14, 0 failed, 회귀 없음)
E2E: 해당 없음(read-only pytest subprocess 기반, 실제 Engine/Trade 실행 없음)
RFC: 없음(Experimental Implementation 범위 — 불필요)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 작업 커밋 예정)
Branch: `claude/async-command-prototype`(`claude/command-contract-prototype` → `claude/unified-dashboard-prototype` 위에서 작업 — 세 Prototype 브랜치가 계보로 연결됨, 전부 아직 main 미merge)
Next Implementation Candidate: in-process 비동기 Command Prototype(Runtime 재검증) 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정 필요
