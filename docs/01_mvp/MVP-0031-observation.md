# MVP-0031 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** —
5단계 전부 정상 동작해 수정할 문제가 없었다.

## 목적

MVP-0030은 `workflow_0008.run_pipeline()`을 investigation형
`REAL_ISSUE`(MVP-0008 fixture)로 실행해, Design 이후 단계가 무의미한
산출물을 냈다는 것을 확인했다 — 원인은 Engine의 결함이 아니라 그
Issue 자체가 애초에 코드 생성을 요구하지 않는 investigation형
Issue였기 때문이라고 결론지었다. 이번 MVP는 그 결론을 검증하기 위해,
**명확한 코드성 Issue**로 같은 `run_pipeline()`을 실제 Engine으로
실행해 5단계 전체가 정상 동작하는지 확인한다.

## 실행 (실제 Engine, 84.3초)

`CODE_ISSUE`(신규, 이 실행 전용 — 저장소에 커밋된 fixture는 아니다):
"Add divide() input validation" — `divide(a, b)`가 `b == 0`일 때
`ValueError`를 던지도록 구현해 달라는, 명확히 코드 작성을 요구하는
Issue.

| Stage | 길이(문자) | 내용 |
|---|---|---|
| planning | 2466 | Goal/Scope/Risks — `divide()` 입력 검증 요구사항을 정확히 서술 |
| design | 2722 | Guard clause 접근법을 구체적으로 설계 |
| implementation | 131 | **실제 동작하는 코드**: `if b == 0: raise ValueError(...); return a / b` |
| code_review | 1560 | 실제 리뷰 4건 — 예외 타입 불일치(`ZeroDivisionError`→`ValueError`), NaN이 조용히 통과하는 엣지 케이스, 타입 힌트/docstring 부재, 중복 검사 |
| test_execution | 1905 | 22개 구체적 테스트 케이스 — 기본 동작, 예외 발생, code_review가 지적한 NaN/무한대 엣지 케이스, 타입 처리, 정밀도까지 review 내용을 실제로 반영 |

## 관찰 결과

### 5단계 모두 정상 동작했는가?

**예.** MVP-0030에서 관찰된 "Design이 스스로 구현을 범위 밖으로
선언 → Implementation이 코드 작성을 거부 → Review/Test가 산문을
리뷰하는" 연쇄가 이번에는 전혀 나타나지 않았다. `implementation`은
즉시 실제 동작 코드를 반환했고, `code_review`는 그 코드의 실제
결함(예외 타입, NaN 처리)을 지적했으며, `test_execution`은 review에서
지적된 엣지 케이스(NaN, 무한대, `-0.0`)를 실제로 테스트 케이스에
반영했다 — Task 1(review)의 출력이 Task 2(test)의 입력 컨텍스트로
전달된다는 MVP.md Exit Criteria가 이 5단계 파이프라인에서도 그대로
관찰됐다.

### Project Intelligence(Planning 전용 Context)는 어떻게 동작했는가?

`context`(`collect_relevant_context`)는 이번 Issue 키워드와 겹치는
파일들(`engine.py`/`agents.py`/`workflow_hello_sdlc.py`, MVP-0013/
0014/0025 관찰 문서 등)을 정상적으로 수집했다. `planning`이 이
Context를 반영했는지는 이번 관찰 범위에서 별도로 대조하지 않았다 —
MVP-0030과 달리 이번 목적은 "5단계가 코드성 Issue에서 정상 동작하는가"
확인이었다.

### MVP-0030 결론의 재확인

MVP-0030이 "Engine 자체는 정직하게 동작했고, 문제는 investigation형
fixture와 항상 코드를 요구하는 파이프라인의 불일치였다"고 내린
결론이, 코드성 Issue에서 파이프라인이 정상 동작함을 실제로 확인함
으로써 뒷받침됐다 — `run_pipeline()`/`agents.py`/`engine.py` 자체에
결함이 있었다면 이번 코드성 Issue에서도 유사한 문제가 재현됐어야
하지만, 그러지 않았다.

## 왜 수정하지 않았는가

5단계 모두 의미 있는 산출물을 냈고, Exit Criteria(Task 1 출력이 Task
2 입력으로 전달됨)도 실제로 관찰됐다 — 고칠 문제가 없었다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `run_pipeline(CODE_ISSUE)`
  전체(5단계)를 실제 `claude -p` 호출로 1회 실행(mock 없음).
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  5단계 모두 실제로 정상 동작했고, 그 사실을 그대로 기록했다.
- MVP-0030 결론을 재확인했는가 — **예**, 같은 파이프라인·같은
  Engine 설정으로 코드성 Issue를 실행해 대조군을 확보했다.
