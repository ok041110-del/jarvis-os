# Evidence — Kernel Candidate Prototype: Parallel Execution(원시 기법)

`PHASE5-KERNEL-CANDIDATE-0001.md`가 확정한 유일한 Kernel Candidate
("`ThreadPoolExecutor.submit()`+`.result()`로 독립 Task를 동시에
`call_engine()` 호출하는 원시 기법", Wave 구조·Checkpointing·도메인
로직 전부 제외)이 **특정 HQ/도메인에 종속되지 않은 공통 실행 기법인지**
하나만 검증한다.

## INPUT

- 검증 대상: Parallel Execution 원시 기법 그 자체(`PHASE4-HQ-CROSS-VALIDATION-0001.md`가
  Dev HQ 자체 연구(`ENGINE-USECASE-0001/0002`, PR #60/#61)와 Investment
  HQ 계보(PR #77/#80)가 독립적으로 도달했다고 확인한 바로 그 기법).
- 도메인: 조수·단풍·발효(자연 현상 설명) — Dev HQ의 code_review/
  test_execution도, Investment HQ의 Stock/ETF/Dividend Stock도 아닌
  제3의 중립 도메인.
- Engine 호출 함수: 이 디렉터리 안의 `engine_caller.py`(`hqs/development/mvp/engine.py`를
  import하지 않은 독립 재구현 — 동일 패턴을 쓴다는 사실 자체가 검증
  대상이므로, `hqs/`/`core/`에 대한 의존을 코드 레벨에서 원천 차단).

## EXECUTION

```
python3 projects/kernel-parallel-execution-prototype/run_prototype.py
```

1. `check_zero_dependency()` — 이 디렉터리의 `.py` 파일 전체를 정적 검사해
   `hqs`/`core` import 여부 확인.
2. `run_sequential()` — 3개 Task를 `call_engine()`으로 순차 호출.
3. `run_parallel()` — 동일 3개 Task를 `ThreadPoolExecutor.submit()`+`.result()`로
   동시 호출.
4. `run_exception_propagation_check()` — 정상 Task 2개 + 반드시 실패하는
   Task 1개(존재하지 않는 바이너리 `claude-binary-that-does-not-exist`
   호출 — 실제 `subprocess` 예외, 코드로 인위 조작한 예외 아님)를 같은
   Pool에 함께 제출.

## OUTPUT

```
ZERO_DEPENDENCY_CHECK: PASS — violations=[]
SEQUENTIAL: 24.4s
PARALLEL: 10.1s
EXCEPTION_PROPAGATION: {"tides": "no_exception", "autumn_leaves": "no_exception",
  "forced_failure": "FileNotFoundError: [Errno 2] No such file or directory:
  'claude-binary-that-does-not-exist'"}
speedup: 2.42x
```

- 3개 Task 결과 전부 실제 정상 수신(515/584/455자, 조수·단풍·발효 각각의
  주제에 정확히 대응하는 내용, 빈 문자열·잘림·교차오염 없음 — `output/parallel.json`
  전문 확인).
- `pytest --ignore=archive`: **187 passed**(기존 그대로, 변화 없음) —
  이 Prototype 파일들은 `test_` 접두어를 쓰지 않아 pytest 수집 대상에도
  포함되지 않음(`--collect-only`로 확인).

## VALIDATION (검증 항목별 결과)

| 항목 | 결과 |
|---|---|
| 1. 최소 Prototype 구현 | 완료(`engine_caller.py` 27줄, `run_prototype.py` 단일 파일) |
| 2. 독립 Task 2~3개 병렬 실행 | 완료(3개: tides/autumn_leaves/bread_rising, 상호 의존 없음) |
| 3. 순차 대비 병렬 동작 확인 | 확인됨 — 순차 24.4s → 병렬 10.1s(2.42배, 실제 동시 실행 없이는 불가능한 단축률) |
| 4. 각 Task 결과 정상 수집 확인 | 확인됨 — 3건 전부 non-empty, 주제 일치, `fut.result()`로 정상 회수 |
| 5. Task 예외 발생 시 호출자에게 정상 전파되는지 확인 | 확인됨 — `forced_failure`의 `FileNotFoundError`가 `.result()` 호출 시 그대로 재발생, 동시에 제출된 나머지 2개 정상 Task는 영향받지 않고 각자 결과를 반환(한 Task의 실패가 같은 Pool의 다른 Task를 오염시키지 않음도 함께 확인) |
| 6. HQ/Investment/Core 기존 코드 의존성 0건 확인 | 확인됨 — 정적 검사(`check_zero_dependency`) PASS, `hqs`/`core` import 0건 |
| 7. pytest 및 기존 187개 테스트 회귀 확인 | 확인됨 — 187 passed, 변화 없음 |
| 8. Prototype EVIDENCE 작성 | 본 문서 |

## ANOMALY

없음. 모든 관찰이 예상과 일치했다 — 병렬 실행이 순차 대비 유의미하게
빨랐고(2.42배), 예외는 발생 지점(`forced_failure`)에서만 발생해 정상
Task로 전파되지 않았으며, 정상 Task의 예외도 호출자(`main()`)까지
정확히 전파됐다.

## CONCLUSION — Kernel Candidate 적합성

**PASS — Domain-independent Kernel Candidate로 확정.**

- 제3의 중립 도메인(자연 현상 설명)에서 `hqs/`·`core/` 어떤 기존
  코드도 참조하지 않고, 이 기법(`ThreadPoolExecutor.submit()`+`.result()`
  로 독립 Task를 동시에 단일 Engine 호출 함수에 넘기는 패턴)을 처음부터
  다시 구현해도 동일하게 동작함을 실측으로 확인했다.
- Dev HQ(`ENGINE-USECASE-0001/0002`)·Investment HQ(프로덕션 6건)에
  이어 **세 번째 독립 맥락**에서도 재현됨 — `PHASE5-KERNEL-CANDIDATE-0001.md`가
  요구한 "반복성"·"재사용성" 기준을 한 단계 더 실증했다.
- 실패 시나리오(예외 전파)도 이 좁은 원시 기법 범위 안에서 안전하게
  동작함을 확인했다 — Checkpointing 같은 별도 계층 없이도 `ThreadPoolExecutor`
  자체의 표준 동작만으로 실패가 삼켜지지 않는다.

**Prototype 결과만으로 `core/` Migration을 결정하지 않는다.** 이 문서는
기법의 도메인 독립성 실증만 다룬다 — `core/execution/`과의 관계 정리,
실제 Kernel 코드 배치, RFC/ADC/ADR 착수 여부는 전부 별도 판단 대상으로
남긴다.

## 관찰되지 않은 것 (명시적으로 기록)

- 4-way 이상 병렬(Investment HQ의 Wave1처럼 5~7개 동시 호출)의 이
  독립 재구현에서의 재현 — 이번엔 3개까지만 검증.
- 장시간(180초 근접) Task에서의 동작 — 이번 Task들은 전부 수 초~수십초
  내 완료됨.
- Checkpointing과의 결합 시 상호작용 — 이번 Prototype은 의도적으로
  Checkpointing을 배제했으므로 다루지 않는다.

---

## Architecture/Contract 변경 여부

**없음.** `hqs/development/`, `hqs/investment/`, `core/`, Structure v1.0,
Architecture Baseline, Development HQ/Investment HQ v1.0 Freeze 어느
것도 수정하지 않았다. Registry/Scheduler/Runtime/Engine Gateway를
만들지 않았다. `core/` Migration을 수행하지 않았다. 새 RFC/ADC/ADR을
작성하지 않았다. 이 Prototype은 `projects/kernel-parallel-execution-prototype/`
안의 신규 파일 4건(`engine_caller.py`, `run_prototype.py`, `output/*.json`,
이 `EVIDENCE.md`)만 추가했다.
