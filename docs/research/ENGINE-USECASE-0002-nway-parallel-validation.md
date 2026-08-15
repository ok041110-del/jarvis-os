# ENGINE-USECASE-0002: N-way Engine 병렬 실행 검증 — Runtime Evidence

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 기록이다.
`ENGINE-USECASE-0001`(2-way 병렬)의 후속으로, 독립 Task 개수를 3개·4개로
늘렸을 때 현재 `call_engine()` 구조만으로 어디까지 실제로 되는지 검증한다.
Adapter를 만들기 위한 실험이 아니다 — `call_engine()`은 전혀 수정하지
않았고, 실험 스크립트는 이 세션의 scratchpad에만 존재했다(`git status
--porcelain`이 실험 전후 비어 있음을 확인). 비용 관측은 이번 실험
범위에서 제외했다(`ENGINE-USECASE-0001`이 이미 구조적 한계로 기록함).

## Use Case

서로 완전히 독립적인(공유 상태 없음, 서로의 출력을 입력으로 쓰지 않음)
실제 Task를 3개, 4개로 늘려 순차/병렬(스레드) 실행시간과 성공/실패/
timeout을 비교한다. 모두 기존 Capability 함수와 기존 fixture를 그대로
재사용했다(신규 입력 생성 안 함, `qa_agent_test_execution`의 `review`
인자는 실제 체이닝 대신 고정 placeholder 문자열을 줘 독립 Task로 취급).

- Task A: `backend_agent_code_review(SAMPLE_CODE)` — `test_mvp_0001.py` 재사용
- Task B: `call_engine(prompt_specification)` — `mvp_0006` fixture 재사용
  (`ENGINE-USECASE-0001`과 동일 입력)
- Task C: `requirements_agent_requirement_analysis(SAMPLE_ISSUE)` —
  `test_workflow_hello_sdlc.py`의 `SAMPLE_ISSUE` 재사용
- Task D: `qa_agent_test_execution(SAMPLE_CODE, "No issues found.")` —
  고정 placeholder review로 독립 호출

## Execution

2-way는 `ENGINE-USECASE-0001`의 기존 실측치를 Baseline으로 그대로
재사용했다(재실행 안 함): 순차 32.19s / 병렬 20.11s.

| N-way | 순차 | 병렬(스레드) | 성공/실패 |
|---|---|---|---|
| 2 (Baseline, 재사용) | 32.19s | 20.11s | 성공 2/2 |
| 3 (A, B, C) | 35.65s | 15.27s | 성공 3/3, 오류 없음 |
| 4 (A, B, C, D) | 61.57s | 53.60s | 성공 4/4, 오류 없음 |
| 4 (재실행) | — | 17.20s | 성공 4/4, 오류 없음 |

실제 Engine 호출 총 16회(3-way 순차 3 + 3-way 병렬 3 + 4-way 순차 4 +
4-way 병렬 4 + 4-way 병렬 재실행 4), 전부 real `claude -p`, timeout
(`ENGINE_TIMEOUT_SECONDS=180`) 도달 사례 없음, 예외 발생 사례 없음.

## 관찰 결과

1. **3-way, 4-way 모두 코드 변경 없이 성공했다.** `call_engine()`을
   스레드에서 동시에 여러 번 불러도 실패·예외·빈 응답이 한 번도
   없었다(N=16 전부 성공).
2. **교차오염 없음(실측).** 4-way 병렬 재실행에서 A/B/C/D 각 결과의
   앞부분을 직접 확인 — A는 mutable default, B는 reverse_string, C는
   "the thing" 요구사항 분석, D는 `add()` 테스트 케이스로 각각 자신의
   Task 주제와 정확히 일치했고 서로 섞이지 않았다.
3. **병렬 단축률이 N이 늘수록 줄어들고, 실행마다 편차가 크다.** 2-way
   ~37%, 3-way ~57% 단축이었지만 4-way는 첫 실행에서 겨우 ~13%
   단축(61.57s→53.60s)이었다 — 반면 동일한 4-way 병렬을 곧바로
   재실행하니 17.20s로 3배 이상 차이가 났다. 이는 병렬 자체의 실패가
   아니라, 동시 실행 개수가 늘수록 공유 자원(CPU/네트워크/Engine
   백엔드 처리)에서의 편차가 커진다는 신호로 관찰된다 — 이번 실험(n=1
   반복 수준)은 원인(로컬 CPU contention인지 Engine 쪽 처리 편차인지)을
   분리 검증하지 않았다.
4. **새로운 구조적 제약은 관찰되지 않았다.** Rate limit, 인증 충돌,
   프로세스 실패, 응답 잘림/누락 등 4-way까지는 발생하지 않았다. "몇
   way부터 실제로 깨지는가"는 여전히 미관찰이다(4-way까지만 검증).

## 현재 구조로 충분한가

4-way까지는 **충분하다** — `call_engine()` 수정, Adapter, Gateway,
Registry, Scheduler 없이 호출부의 단순 스레드 병렬화만으로 성공적으로
동작했다. 병목은 "구조적으로 막혀서"가 아니라 "동시 실행 시간이 편차 있게
늘어난다"는 성능 특성으로 관찰됐다 — 이는 기능적 실패가 아니다.

## Adapter Need

없음. 4-way까지 관찰한 결과 Adapter/Gateway가 필요하다는 신호(실패,
상태 충돌, 호출 계약 불일치 등)는 나타나지 않았다.

## Governance / Architecture

Architecture/Contract 변경 없음. 이번 실험에서 발견된 것은 구현 필요
항목이 아니라 관찰 사실(N이 늘수록 병렬 단축률 편차 증가)뿐이다 — 별도
판단이 필요한 새 결정 사항은 없다.

## Evidence

- 실험 스크립트: 세션 scratchpad(`experiment_engine_nway_0001.py`,
  tracked 브랜치 미포함).
- 실제 실행 로그(요약): 위 표, 4-way 병렬 재실행 결과 스니펫(A/B/C/D
  주제 일치, 교차오염 없음).

## Next

- 5-way 이상에서 실제로 실패/timeout이 나타나는 지점은 미관찰 — 필요
  시 후속 실험 대상.
- 4-way 실행시간 편차(53.60s vs 17.20s)의 원인 분리(로컬 자원 vs
  Engine 쪽)는 미관찰 — 반복 횟수를 늘린 후속 실험이 필요하면 별도
  기록한다.
