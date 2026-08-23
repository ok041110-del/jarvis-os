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
- `agents/` — `AGENT_CAPABILITY_MAP` 리터럴 딕셔너리(`__init__.py`) + Requirements/Design/Backend/QA Agent 함수(각 `requirements.py`/`design.py`/`backend.py`/`qa.py`, Agent Package Refactoring).
- `workflow.py` — Task 1(`code_review`) → Task 2(`test_execution`) 하드코딩 직접 호출.
- `cli.py` — 실행 진입점.

Scheduler, Registry, Workflow Parser, Engine Gateway, Policy, Memory Service,
Event Bus는 `IMPLEMENTATION_RULES.md`에 따라 의도적으로 구현하지 않았다.

## 이 문서의 범위

위 "구조"는 MVP-0001 원 구현 4개 파일만 설명한다. 이후 이 디렉터리에
추가된 MVP-0002~0052 Dogfooding 산출물(`workflow_0002.py` 등 다수),
`project_intelligence.py`, `ast_context.py`, `workflow_ast_context.py`는
각자의 모듈 docstring과 `docs/research/`의 근거 문서를 참고한다.
Stage 01~05(`hqs/development/stages/`)와 이를 연결하는 Integrated
Workflow/CLI(`hqs/development/workflow.py`, `hqs/development/cli.py`)는
이 디렉터리 밖의 별도 v2.0 트랙이며, 각 Stage 폴더의 `README.md`를
참고한다.
