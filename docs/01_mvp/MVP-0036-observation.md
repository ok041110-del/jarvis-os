# MVP-0036 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1곳 최소 수정했다** —
실제 Engine으로 재현한 실제 결함이 있었다.

## 목적

지금까지의 MVP-0001~0035는 모두 real Engine 호출의 **성공** 경로만
관찰했다 — Engine이 정상적으로 텍스트를 반환하는 경우다.
`development-hq/mvp/engine.py`의 `call_engine()`은 Engine 호출 실패를
전혀 처리하지 않고(try/except 없음, `result.returncode` 확인도 없음)
`subprocess.run(..., timeout=180)`을 그대로 노출하는데, 이 실패
전파 경로(Engine이 timeout 등으로 실패했을 때 각 workflow가 어떻게
반응하는가)는 어떤 MVP에서도 real Engine으로 검증된 적이 없었다 —
core 동작(Engine 실패 처리)이지만 여태 항상 "성공"만 관찰됐다는 점에서
`__main__` 진입점 검증(MVP-0034/0035)보다 의미 있는 경계다.

caller 위치(ADC-0010)와 무관 — 이 관찰은 기존 `call_engine()` 단일
호출 함수와 기존 workflow 함수들의 예외 처리 유무만 다룬다. 새
Architecture/Gateway/Policy를 설계하지 않았다.

## 실험 방법 (mock 없음 — 실제 Engine 프로세스를 실제로 timeout시킴)

1. 사전 측정: 실제 `claude -p "Say the single word: ok"` 1회 호출이
   약 7.3초 걸림을 확인(정상 latency 파악용).
2. `engine.py`의 `subprocess.run(...)` `timeout` 값을 일시적으로
   `180` → `2`로 변경 — Mock이 아니라 **진짜 `claude` 프로세스를
   진짜로 실행하고 진짜로 2초 만에 강제 종료**시켜 real
   `subprocess.TimeoutExpired`를 발생시키는 방법.
3. 이 상태에서 `workflow_hello_sdlc.run_hello_sdlc()`와
   `workflow.run_mvp_0001()`을 각각 실제 Issue/코드로 직접 호출.
4. 관찰 후 `timeout` 값을 `180`으로 원복(`git diff`로 무변경 확인).

## 관찰 결과 — 최초 실행 (수정 전)

- **`run_hello_sdlc()`**: real timeout 발생 시 이미 있는
  `try/except Exception`이 정상적으로 잡아 `{"status": "Failed",
  "error": "Command [...] timed out after 2 seconds", "planning":
  None, "design": None, ...}`를 반환. 크래시 없음 — 기존 코드가
  이미 올바르게 동작함을 처음으로 실측 확인(수정 불필요).
- **`run_mvp_0001()`** (MVP-0001의 실제 workflow, `cli.py`가 호출하는
  함수): `try/except`가 전혀 없어 `subprocess.TimeoutExpired`가
  **잡히지 않고 그대로 호출자까지 전파**됨을 실측 확인 — 함수가
  `dict`를 반환하지 않고 uncaught exception으로 죽었다. `cli.py`를
  통해 실행됐다면 raw Python traceback으로 종료됐을 것이다. 이는
  MVP.md Exit Criteria("입력 코드가 주어지면, 수동 개입 없이 ...
  순서대로 반환된다")를 Engine 실패 상황에서 위반하는 실제 결함이다.

## 변경 파일

- `development-hq/mvp/workflow.py`
  - `run_mvp_0001()` 본문을 `try/except Exception`으로 감쌌다.
    `workflow_hello_sdlc.run_hello_sdlc()`가 이미 쓰고 있는 것과
    동일한 패턴을 그대로 재사용했다(새 개념 도입 없음). 실패 시에도
    기존 반환 계약(`{"code_review": ..., "test_execution": ...}`,
    정확히 이 2개 키)을 그대로 유지하고, 값에 에러 메시지를 담아
    반환한다 — `cli.py`가 수정 없이 그대로 두 섹션을 출력할 수
    있도록.
  - `development-hq/mvp/engine.py`는 실험을 위해 `timeout=2`로
    바꿨다가 관찰 후 `180`으로 되돌렸다 — 최종 diff 없음
    (`git diff development-hq/mvp/engine.py` 확인, 아래 회귀 확인
    참조).

## 관찰 결과 — 수정 후 재실행

- 동일한 강제 2초 timeout 조건에서 `run_mvp_0001()`을 재실행 —
  uncaught exception 없이 정상적으로 `dict` 반환:
  `{"code_review": "Engine call failed: Command [...] timed out
  after 2 seconds", "test_execution": "Engine call failed: Command
  [...] timed out after 2 seconds"}`. 두 키 모두 유지됨.
- `timeout`을 `180`으로 원복한 뒤, 정상 조건(강제 timeout 없음)에서
  다시 `run_mvp_0001()`을 real Engine으로 실행 — 29.6초 소요,
  mutable default argument 등 실제 리뷰 4건과 테스트 케이스 16건이
  정상적으로 순서대로 반환됨(회귀 없음, happy path 그대로 동작).

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음).
- `git status --porcelain` — `development-hq/mvp/workflow.py` 1개
  파일만 변경. `engine.py`는 실험 후 원복되어 diff 없음.
- `git diff development-hq/mvp/workflow.py` — 위 "변경 파일" 절의
  내용과 일치, 그 외 변경 없음.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`workflow.py`) 1개 함수만**.
  실제 Engine 실행으로 재현한 실제 결함(uncaught timeout crash)을
  기존 저장소에 이미 있는 패턴(`run_hello_sdlc`의 try/except)을
  그대로 재사용해 최소 수정했다. 새 Registry/Scheduler/Policy/
  Engine Gateway를 만들지 않았다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. 기존 `run_mvp_0001()`의 반환 계약(2-key dict)도 그대로
  유지했다.
- 실제 Engine으로 확인했는가 — **예**. 진짜 `claude` 프로세스를 진짜
  timeout(2초)으로 실제로 죽여 real `subprocess.TimeoutExpired`를
  발생시켰고(mock 없음), 수정 전/후 각각 실제로 재실행해 비교했다.
  수정 후에는 정상 조건(180초)에서도 real Engine으로 happy path를
  재확인했다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  `run_hello_sdlc()`는 이미 정상 동작했음을 있는 그대로 기록했고,
  `run_mvp_0001()`의 실제 결함과 그 최소 수정만 별도로 구분해
  기록했다.
- caller 위치 결정을 시도했는가 — **아니오**. `call_engine()` 단일
  호출 함수 자체나 그 위치는 건드리지 않았다 — 이미 존재하는
  workflow 함수 내부의 예외 처리 유무만 다뤘다. Execution Layer
  caller 위치(`ADC-0010`)와 무관하다.
- 불필요한 변경을 확인했는가 — **예**. `workflow_0002.py`,
  `workflow_0008.py`, `workflow_0009.py`,
  `workflow_artifact_flow.py`, `workflow_project_intelligence.py`도
  동일하게 try/except가 없어 같은 패턴의 결함을 가질 가능성이
  있지만, 이번 MVP는 그 사실만 기록하고 수정하지 않았다(MVP 범위
  최소화 — 각 파일의 수정은 별도 MVP로 관찰·검증되어야 한다).
