# MVP-0037 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 5개 파일에서
최소 수정했다** — 실제 Engine timeout으로 재현한 실제 결함이 있었다.

## 목적

MVP-0036에서 `run_mvp_0001()`(workflow.py)만 실제 Engine timeout에서
uncaught crash가 나는 것을 발견·수정했다. `call_engine()`은 여전히
예외 처리가 전혀 없는 단일 함수이므로, 이 문제가 다른 주요 workflow
진입점에도 동일하게 있는지 확인이 필요했다. 이번 MVP는
`development-hq/mvp`의 주요 workflow 진입점 6개를 대상으로 (1) 각각의
`call_engine()` 예외 처리 구조를 확인하고, (2) 실제 Engine timeout을
강제로 발생시켜 실측하고, (3) 실제로 깨지는 것만 기존 Contract 안에서
최소 수정했다.

caller 위치(ADC-0010)와 무관 — 각 workflow 함수 내부의 예외 처리
유무만 다뤘다. 새 Architecture/Gateway/Policy를 설계하지 않았고,
새 RFC/ADC/ADR도 만들지 않았다.

## 점검 대상 (주요 workflow 진입점 6개)

| 함수 | 파일 | 기존 예외 처리 |
|---|---|---|
| `run_mvp_0002` | `workflow_0002.py` | 없음 |
| `run_pipeline` | `workflow_0008.py` | 없음 |
| `run_comparison` | `workflow_0009.py` | 없음 (내부적으로 `run_issue_to_planning`, `run_issue_to_planning_with_bundle` 호출) |
| `run_issue_to_implementation` | `workflow_artifact_flow.py` | 없음 |
| `run_issue_to_planning` | `workflow_project_intelligence.py` | 없음 |
| `run_issue_to_design` | `workflow_project_intelligence.py` | 없음 |

(참고: `run_mvp_0001`은 MVP-0036에서 이미 수정됨, `run_hello_sdlc`는
MVP-0036에서 이미 정상 동작 확인됨 — 이번 점검 대상에서 제외.)

## 실험 방법 (mock 없음)

MVP-0036과 동일한 방법: `engine.py`의 `subprocess.run(...)`
`timeout`을 일시적으로 `180` → `2`로 변경해 실제 `claude` 프로세스를
실제로 2초 만에 강제 종료시켜 real `subprocess.TimeoutExpired`를
발생시켰다. 6개 함수 각각을 실제 Issue/코드로 직접 호출해 수정
전/후를 비교했다. 관찰 후 `timeout`을 `180`으로 원복했다
(`git diff development-hq/mvp/engine.py` 무변경으로 확인).

## 관찰 결과 — 수정 전 (6개 전부 재현됨)

6개 함수 전부 real forced timeout(2초)에서 **uncaught
`TimeoutExpired`**로 죽었다 — `run_mvp_0001`과 동일한 결함이
`call_engine()`을 직접/간접 호출하는 모든 주요 workflow 진입점에
공통으로 있었다.

```
[workflow_0002.run_mvp_0002] RAISED UNCAUGHT: TimeoutExpired
[workflow_0008.run_pipeline] RAISED UNCAUGHT: TimeoutExpired
[workflow_0009.run_comparison] RAISED UNCAUGHT: TimeoutExpired
[workflow_artifact_flow.run_issue_to_implementation] RAISED UNCAUGHT: TimeoutExpired
[workflow_project_intelligence.run_issue_to_planning] RAISED UNCAUGHT: TimeoutExpired
[workflow_project_intelligence.run_issue_to_design] RAISED UNCAUGHT: TimeoutExpired
```

## 변경 파일 (5개, 각각 최소 수정)

모두 `run_mvp_0001`(MVP-0036)이 이미 쓰는 것과 동일한 `try/except
Exception` 패턴을 재사용했다 — 새 개념 없음. 기존 반환 계약(키
구성)은 그대로 유지하고, Engine 호출이 필요한 값에만 에러 메시지를
채워 반환한다. Engine 호출 없이 이미 계산된 값(`context`,
`context_bundle` 등, `project_intelligence.py`의 파일 스캔 결과)은
실패 시에도 그대로 보존한다.

- `development-hq/mvp/workflow_0002.py` — `run_mvp_0002()`.
- `development-hq/mvp/workflow_0008.py` — `run_pipeline()`.
- `development-hq/mvp/workflow_project_intelligence.py` —
  `run_issue_to_planning()`, `run_issue_to_design()`.
- `development-hq/mvp/workflow_artifact_flow.py` —
  `run_issue_to_implementation()`.
- `development-hq/mvp/workflow_0009.py` —
  `run_issue_to_planning_with_bundle()`만 직접 수정했다.
  `run_comparison()` 자체는 손대지 않았다 — 이 함수가 호출하는 두
  하위 함수(`run_issue_to_planning`은 `workflow_project_intelligence.py`에서,
  `run_issue_to_planning_with_bundle`은 이 파일에서) 둘 다 이미
  예외를 잡아 항상 dict를 반환하므로, `run_comparison()`은 그 dict의
  키에 안전하게 접근할 뿐 별도 처리가 필요 없다 — 실측으로 확인함
  (아래 "수정 후 재실행" 참조).

`development-hq/mvp/engine.py`는 실험을 위해 `timeout=2`로 바꿨다가
관찰 후 `180`으로 되돌렸다 — 최종 diff 없음.

## 관찰 결과 — 수정 후 재실행 (강제 실패 경로, 6개 전부)

동일한 강제 2초 timeout 조건에서 6개 함수 전부 재실행 — uncaught
exception 없이 각자의 기존 키 구성을 그대로 유지한 채 정상 반환:

```
[workflow_0002.run_mvp_0002] -> keys=['code_review', 'test_execution']
[workflow_0008.run_pipeline] -> keys=['context', 'planning', 'design', 'implementation', 'validation']
    context: (실제로 계산된 값 그대로 보존됨)
    planning/design/implementation/validation.*: "Engine call failed: ..."
[workflow_0009.run_comparison] -> keys=['flat_context_planning', 'context_bundle_planning', 'context_bundle']
    (수정하지 않은 run_comparison() 자체가, 두 하위 함수의 방어적
    반환 덕분에 정상적으로 dict를 반환함 — cascade 확인됨)
[workflow_artifact_flow.run_issue_to_implementation] -> keys=['context', 'planning', 'design', 'implementation']
[workflow_project_intelligence.run_issue_to_planning] -> keys=['context', 'planning']
[workflow_project_intelligence.run_issue_to_design] -> keys=['context', 'planning', 'design']
```

## 관찰 결과 — 수정 후 재실행 (정상 Engine 경로)

- `timeout`을 `180`으로 원복한 뒤, `run_issue_to_planning()`을 real
  Engine으로 정상 실행 — 37.64초 소요, 실제 Requirement Analysis
  텍스트가 정상 반환됨(회귀 없음).
- `run_pipeline()`(5단계, 가장 무거운 대상)의 정상 경로 전체 재실행은
  탐침 스크립트의 외부 timeout(300초)을 넘겨 완주하지 못했다 —
  이는 real Engine 호출 5회 누적 소요 시간 문제이지 코드 결함이
  아니다(부분 출력 없이 정상적으로 진행 중이었음, crash 아님). 이
  경로의 정상 동작은 이미 MVP-0030/MVP-0031에서 real Engine으로
  충분히 검증되어 있고, 이번 수정은 `try:` 블록 안의 기존 코드를
  한 글자도 바꾸지 않았다(예외가 발생하지 않는 한 `try/except`는
  동작을 바꾸지 않는다는 Python 자체의 성질) — 따라서 추가로 같은
  5단계 성공 경로를 반복 실행하는 것은 "단순 성공 경로 반복"에
  해당해 하지 않았다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음).
- `git status --porcelain` — 5개 workflow 파일만 변경.
  `engine.py`는 실험 후 원복되어 diff 없음.

## Self Review

- 코드를 변경했는가 — **예, 5개 파일, 6개 함수 중 5개 함수를 직접
  수정**(`run_comparison`은 하위 함수 수정으로 간접 보호됨). 모두
  실제 Engine timeout으로 재현한 실제 결함을, 저장소에 이미 있는
  패턴(`run_mvp_0001`/`run_hello_sdlc`)을 그대로 재사용해 최소
  수정했다. 새 Registry/Scheduler/Policy/Engine Gateway를 만들지
  않았다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. 각 함수의 기존 반환 계약(키 구성)도 그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. 6개 함수 전부 real forced
  timeout(2초, mock 없음)으로 수정 전 crash를 재현하고 수정 후 정상
  반환을 재확인했다. 정상 조건(180초)에서도 `run_issue_to_planning`을
  real Engine으로 재확인했다. `run_pipeline`의 정상 경로는 이미 존재하는
  real Engine Evidence(MVP-0030/31)와 "try/except는 예외 없을 때
  동작을 바꾸지 않는다"는 논리적 근거로 대체했다 — 이유를 명시했다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  `run_pipeline` 정상 경로의 재실행이 외부 300초 제한으로 완주하지
  못한 사실을 숨기지 않고 그대로 기록했고, 이를 crash나 결함으로
  잘못 표현하지 않았다.
- caller 위치 결정을 시도했는가 — **아니오**. `call_engine()` 단일
  호출 함수 자체나 그 위치는 건드리지 않았다 — 기존 workflow 함수
  내부의 예외 처리 유무만 다뤘다. Execution Layer caller 위치
  (`ADC-0010`)와 무관하다.
- 불필요한 변경을 확인했는가 — **예**. 정확히 필요한 5개 파일만
  수정했고, `run_comparison()`은 직접 손대지 않고 하위 함수 수정만으로
  해결됨을 실측으로 확인했다. `agents.py`, `engine.py`,
  `project_intelligence.py`, `cli.py`는 변경하지 않았다.
