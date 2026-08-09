# MVP-0030 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** — 이유는
아래 "왜 수정하지 않았는가" 참고.

## 목적

`workflow_0008.py`의 `run_pipeline()`(Planning(PI 포함) → Design →
Implementation → Validation, 5단계 전부)을 MVP-0028의 cwd 수정 이후
처음으로 실제 Engine으로 전체 실행했다. 이전 MVP들은 `run_comparison`
(MVP-0009, Planning까지만)이나 `run_hello_sdlc`(MVP-0004, `divide()`
같은 범용 코드 이슈)만 실제 실행했을 뿐, MVP-0008이 정의한 실제
`REAL_ISSUE`("Project Intelligence 개선")로 5단계 전체를 실제 Engine
으로 실행한 적은 없었다.

## 실행 (실제 Engine, 209.2초)

`run_pipeline(REAL_ISSUE)`를 1회 실행했다. 5개 Stage 모두 `Complete`
상태로 비지 않은 값을 반환했다.

| Stage | 길이(문자) | 내용 |
|---|---|---|
| planning | 2448 | Goal/범위/위험 — 정상적인 prose Requirement 분석 |
| design | 3798 | 3단계 진단 절차 + "책임 분리 원칙" — 정상적인 prose Design |
| implementation | 1885 | **코드 없음** — 코드 작성을 명시적으로 거부 |
| code_review | 2364 | `implementation`을 "코드가 아니라 산문"으로 정확히 인식하고, 그 산문의 커뮤니케이션 품질(중복 서술, 모순된 표현 등)을 리뷰 |
| test_execution | 3288 | 실제 코드 테스트 케이스 대신 "산문 리뷰 결과를 검증하는 체크리스트"(TC1~TC10)를 생성 |

## 관찰 결과 — 왜 이런 출력이 나왔는가 (실제 텍스트 근거)

`design`은 스스로 이렇게 명시했다: "이번 작업은 코드 수정이 아니라
**원인 소재 판정(diagnosis)**이 목표", "코드 수준 세부 설계는 범위
밖이므로 개념만 제시", "실제 코드 수정 ... 범위 밖으로 남겨두며".

`implementation`(`backend_agent_code_generation`)은 그 지시("Based on
the following design, write the implementation code")를 받고도, 위
Design이 스스로 코드 작성을 범위 밖으로 명시했다는 점과, Design이
요구한 "1단계 사실 확인"(실제 소스 파일 열람)이 이 호출에서는
불가능하다는 점(도구 차단, `DISALLOWED_TOOLS`)을 근거로 **가상의
함수 시그니처를 지어내는 대신 코드 작성을 거부**했다 — "Writing
'implementation code' now would mean inventing fictional function
bodies ... exactly the risk the design itself warns against."

`code_review`/`test_execution`은 그 거부 응답을 그대로 `code`
파라미터로 받아, "코드가 아니라 산문"임을 정확히 인식한 뒤 그
산문 자체의 품질(리드 문장 위치, 중복, 언어 혼용 등)을 리뷰/테스트
대상으로 삼았다 — 코드 리뷰나 테스트 케이스로서는 의미가 없지만,
입력이 실제로 코드가 아니라는 사실 자체는 두 Stage 모두 정확히
인지했다.

## 이것이 "문제"인가?

**Engine 호출 자체는 정직하게 동작했다** — 존재하지 않는 코드베이스
구조나 함수 시그니처를 지어내는 대신("오진단 위험"을 스스로
경계하며) 정직하게 거부했다. 이는 hallucination이 아니라 그 반대다.

**진짜 원인은 `REAL_ISSUE`(MVP-0008이 만든 고정 Issue)의 성격에
있다.** `REAL_ISSUE`의 description은 "...개선될 수 있는지 **검토가
필요하다**"로 끝난다 — 애초에 "코드를 작성해 달라"가 아니라
"조사·검토해 달라"는 investigation형 요청이다. 그런데
`run_pipeline()`은 Issue의 종류를 구분하지 않고 항상 Planning →
Design → **Implementation(코드 생성)** → Validation을 그대로
호출한다(`backend_agent_code_generation`의 지시 문장은 "write the
implementation code"로 고정되어 있다, MVP-0025). rule-based Engine
시절에는 Capability Logic이 입력 형태와 무관하게 항상 어떤 텍스트를
반환했으므로 이 불일치가 드러나지 않았지만, 실제 Engine은 Design이
스스로 규정한 범위를 존중해 코드 작성을 거부할 만큼 "정직하게"
동작하기 때문에, investigation형 Issue를 코드 생성 파이프라인에
그대로 태우면 이런 결과가 나온다는 것이 이번 실행으로 처음 실측
확인됐다.

## 왜 수정하지 않았는가

이 현상을 "고치려면" 다음 중 하나가 필요하다:

1. `backend_agent_code_generation`/`backend_agent_code_review`/
   `qa_agent_test_execution`이 입력이 실제 코드인지 investigation
   산문인지 구분해 다르게 동작하도록 만드는 것 — 이는 입력 내용에
   따른 조건 분기를 Capability Logic에 추가하는 것이며, MVP-0002의
   RT-0001 관찰 대상("Task 호출이 조건문/파서로 일반화되려는 순간")과
   같은 종류의 변화다. `workflow_0008.py`는 스스로 "새 Capability를
   추가하지 않는다 — 기존 5개 함수만 순서대로 호출한다"고 명시했고,
   분기 도입은 별도 MVP(MVP-0002)의 관찰 대상으로 이미 분리되어
   있다 — 여기서 조용히 끼워 넣는 것은 그 분리를 흐린다.
2. `REAL_ISSUE`(MVP-0008이 만든 고정 fixture)를 코드 생성이 가능한
   내용으로 바꾸는 것 — 그러나 `REAL_ISSUE`는 이 저장소 자신의 실제
   Issue를 그대로 쓴다는 MVP-0008의 명시적 취지("Development HQ가
   Development HQ의 실제 Issue 하나를 처리한다")이며, 그 실제 Issue가
   investigation형이라는 사실 자체가 이번 관찰의 핵심이다 — fixture를
   바꾸면 관찰 대상이 사라진다.

두 방향 모두 "기존 Contract 안에서의 최소 수정"의 범위를 벗어난다 —
전자는 새로운 조건 분기(Stage-aware Capability Logic) 설계이고,
후자는 관찰 대상 자체를 지우는 것이다. 따라서 이번 실행은 새로운
Blocking으로 보지 않고, 지시대로 실제 Engine 호출 자체는 정상
동작했다는 사실과 함께 원인을 Evidence로만 기록한다.

## Regression 확인

- 이번 실행은 관찰 목적의 단발 스크립트 실행이며, `agents.py`/
  `engine.py`/`workflow*.py` 어디에도 코드 변경이 없다. `git status`
  클린 상태를 확인했다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `run_pipeline(REAL_ISSUE)`
  전체(5단계)를 실제 `claude -p` 호출로 1회 실행(mock 없음).
- "문제"를 억지로 만들어 수정을 시도했는가 — **아니오**. 원인을
  MVP-0008 fixture의 investigation 성격과 Engine의 정직한 거부
  동작으로 정확히 특정했고, 그 결론에 따라 수정하지 않기로 판단한
  근거를 그대로 기록했다.
- 실패를 성공으로 표현했는가 — **아니오**. Stage 3~5의 산출물이
  의미 있는 코드 리뷰/테스트가 아니라는 사실을 숨기지 않았다.
