# MVP-0001 Implementation

`hqs/development/MVP.md`의 User Scenario(코드 리뷰 + 테스트 케이스 제안)를 구현한다.

## 실행

```
python3 hqs/development/mvp/cli.py <파일 경로>
# 또는
cat some_code.py | python3 hqs/development/mvp/cli.py
```

## 테스트

```
python3 -m pytest hqs/development/mvp/tests/
```

## 구조

- `engine.py` — 단일 Engine 호출 함수 (`call_engine`). Engine Gateway 추상화 없음.
- `agents.py` — `AGENT_CAPABILITY_MAP` 리터럴 딕셔너리 + Backend/QA Agent 함수.
- `workflow.py` — Task 1(`code_review`) → Task 2(`test_execution`) 하드코딩 직접 호출.
- `cli.py` — 실행 진입점.

Scheduler, Registry, Workflow Parser, Engine Gateway, Policy, Memory Service,
Event Bus는 `IMPLEMENTATION_RULES.md`에 따라 의도적으로 구현하지 않았다.
