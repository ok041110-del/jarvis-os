# Stage 05 Parallel Validation Architecture — Harness (Experimental)

## 목적

`ADR-0025-stage05-parallel-validation-architecture-boundary.md`가
정리한 Stage 05 Parallel Validation Architecture의 Independence/
Isolation/Aggregation 판단을 **실측**으로 뒷받침하기 위한 격리된
실험 Harness다. `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`
(Evidence 문서)가 이 Harness의 실행 결과를 기록한다.

## Scope / 격리 확인

- `projects/stage05-parallel-validation-harness-v1/`에만 존재한다.
  `hqs/development/stages/05_validation/stage_05.py`를 import하거나
  수정하지 않는다 — Production Stage 05는 이 Harness와 완전히
  독립이다(`domain/`이 자체적으로 6개 Validator를 재정의).
- `hqs/development/mvp/agents/backend.py`(실제 대상)를 **읽기만**
  한다(`domain/fixtures.py::build_fixture`) — 절대 쓰지 않는다. 실제
  파일 mutation은 전부 `domain/workspace.py::TestWorkspace`가 만드는
  임시 디렉터리(repository 밖) 안에서만 일어난다.
- 새로운 Gateway/Router/Provider Architecture를 만들지 않는다 —
  `domain/review.py`의 LLM Mode는 `engine_call: Callable[[str], str]`
  하나만 주입받는 Adapter이며, 어떤 Provider도 스스로 선택하지 않는다.
  기본 실행에서는 `engine_call`을 주입하지 않으므로 실제 Engine을
  호출하지 않는다.

## 구성

- `domain/results.py` — 공통 `ValidatorResult` 스키마 + 고정 ID 순서.
- `domain/validators.py` — Structure/Scope/AST/Dependency(4개 결정적
  Validator, Engine 미호출).
- `domain/review.py` — Review(disabled/deterministic/llm 3-Mode).
- `domain/workspace.py` — Test Workspace(`.git` 제외 전체 복사).
- `domain/test_node.py` — Test Validator(Workspace 생성 → Implementation
  적용 → pytest 실행 → cleanup, 4단계 실패를 각각 구분).
- `domain/runner.py` — `run_single()`/`run_parallel()`.
- `domain/aggregator.py` — 결과 수집 + deterministic blocking 정책.
- `domain/fixtures.py` — 실제 `backend_agent_code_review` 대상 fixture
  (원본을 읽어 검증 로직을 문자열 치환으로 추가, 하드코딩 사본 없음).
- `experiment_a.py` — Single vs Parallel(3회 반복).
- `experiment_b.py` — Review Case A/B/C.
- `failure_isolation_experiment.py` — 6/6 success ~ all failure 시나리오.
- `tests/test_harness.py` — Harness 자체 테스트(Part 7).

## 실행

```
python3 experiment_a.py
python3 experiment_b.py
python3 failure_isolation_experiment.py
pytest tests/ -q -m "not slow"   # 빠른 테스트(약 2초)
pytest tests/ -q -m "slow"       # 실제 backend.py 대상 E2E(약 1분)
```

## Non-goals

- Parallel Production Adoption을 전제하지 않는다.
- Review LLM Adoption을 전제하지 않는다.
- Production `stage_05.py`를 이 Harness의 구조로 바꾸지 않는다(별도
  RFC → ADC → ADR 대상, `ADR-0025` §14 Non-Goals 참조).
