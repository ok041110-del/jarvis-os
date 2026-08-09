# MVP-0026 Observation

**문서 성격**: 재현 시도 기록(Evidence). **코드를 변경하지 않았다.**

## 목적

MVP-0025 Observation "범위 밖으로 남겨둔 추가 관찰"에 기록된 현상 —
`run_hello_sdlc()`를 "Add input validation to divide()" Issue로 실행했을
때, `implementation`(`backend_agent_code_generation`)이 실제 코드 대신
"design을 받지 못해 구현할 수 없다"는 취지의 placeholder를 반환하고, 그
결과가 `code_review`/`test_execution`까지 그대로 전파된 1회 관찰 —
이 현상이 실제로 반복 재현되는지, 재현된다면 발생 조건이 무엇인지를
실제 Engine 반복 실행으로 확인한다.

## 실행 방법

동일한 Issue("Add input validation to divide()")로 `run_hello_sdlc()`를
**4회 연속 실제 실행**했다(mock 없음, 매 회 새 `claude -p` 프로세스 호출).
Issue/코드는 MVP-0025에서 문제를 재현했던 것과 동일하게 고정했다 —
Issue 내용을 바꾸면 재현 여부 판단이 흐려지기 때문이다.

## 실행 결과 (4회 전수)

| Run | 소요 시간(초) | status | implementation 길이(문자) | Placeholder 여부 |
|---|---|---|---|---|
| 0 | 152.9 | Complete | 141 | 아니오 — 실제 `divide()` 코드 |
| 1 | 92.1 | Complete | 132 | 아니오 — 실제 `divide()` 코드 |
| 2 | 171.3 | Complete | 145 | 아니오 — 실제 `divide()` 코드 |
| 3 | 116.6 | Complete | 193 | 아니오 — 실제 `divide()` 코드 (docstring 포함) |

4회 모두 `implementation`이 `def divide(a, b): ... raise ValueError(...)`
형태의 실제 동작 코드를 반환했고, 그 결과 `test_execution`도 4회 모두
`divide()`에 대한 구체적인 테스트 케이스 목록(Core behavior/Edge case
등)을 정상적으로 반환했다. MVP-0025에서 관찰했던 "design을 받지 못해
구현할 수 없다"는 취지의 placeholder는 **4회 중 0회** 재현됐다.

## 판단

**재현되지 않았다.** MVP-0025가 기록한 1회의 관찰은, 4회 반복 재현
시도에서 재현 비율 0/4으로 확인된 산발적 현상이다. 발생 조건(무엇이
그 1회를 유발했는지)은 이번 실행으로도 특정하지 못했다 — 재현 자체가
안 되므로 조건을 비교할 대조군이 없다.

## 후속 처리 (지시에 따름)

"재현되지 않으면 수정하지 말고 Evidence만 기록한다"는 지시에 따라,
`agents.py`/`engine.py`/`workflow*.py` 어디에도 코드 변경을 하지
않았다. `git status`가 클린 상태임을 확인했다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. 4회 모두 실제 `claude -p`
  호출(mock 없음).
- 재현되지 않은 사실을 재현된 것처럼 표현했는가 — **아니오**. 4회
  중 0회 재현을 그대로 기록했다.
- 추측했는가 — **아니오**. 발생 조건을 알아내지 못했다는 사실도
  그대로 기록했다 — 원인을 지어내지 않았다.
