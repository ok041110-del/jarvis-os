# OpenRouter Auto Selection v1 (Experimental)

## 목적

Stage 01~05에 특정 LLM 모델을 Jarvis가 고정하지 않고, OpenRouter의
무료 모델 fallback(`models` 배열, 공식 파라미터)으로 다음 Stage로
안전하게 진행할 수 있는지 실측한다. Production 최종 채택이 목적이
아니다. 상세 Evidence: `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`.

## Scope / 격리 확인

- `projects/openrouter-auto-selection-v1/`에만 존재한다. `hqs/development/`
  의 Engine 모듈(`chatgpt_engine.py`/`engine.py`/`omniroute_engine.py`)을
  import하지 않는다(정적 검사, `tests/test_auto_selection_harness.py`).
- Contract Validation은 `hqs/development/stages/01_context_analysis/
  reasoning.py::parse_structured_output`을 **읽기 전용**으로 재사용한다
  — 수정하지 않는다.
- `model="openrouter/auto"`는 사용하지 않는다(무료 티어 미지원, 실측
  HTTP 402 확인). OpenRouter 공식 `models` 배열 파라미터만 사용한다.

## 구성

- `domain/model_pool.py` — `:free` 모델 목록 조회, 실측 상한(3개)으로
  자르기, 알려진 비기능 모델(agentic-harness-only) 제외.
- `domain/stage_policy.py` — Stage별 정책(모델 이름 없음).
- `domain/contracts.py` — Stage별 Contract(기존 Production parser 재사용).
- `domain/auto_selection_client.py` — `models` 배열 기반 호출 + 실패
  분류 + bounded retry(최대 1회, 실패 모델 Pool 제외).
- `domain/fixtures.py` — Stage 01~05 공통 프롬프트(이전 세션과 동일
  시나리오 재사용).
- `run_experiment.py` — Stage 01~05 × 3회 실행.
- `tests/test_auto_selection_harness.py` — Harness 자체 테스트 15개.

## 실행

```
python3 run_experiment.py
pytest tests/ -q
```

## 알려진 제한(Evidence 문서 §13/§19 참조)

`domain/fixtures.py::build_stage05_review_prompt()`는 이번 실행에서
실제 Stage 04 산출물 대신 placeholder 텍스트를 사용했다 — Stage 05
Review 결과의 의미적 정확성은 이 Harness의 이번 실행 결과로 판단할 수
없다(Contract/latency/model 선택 관점에서만 유효).

## Non-goals

- Production Stage 01~05 routing 변경 — 하지 않는다.
- 새 Gateway/Router — 만들지 않는다.
- 특정 모델을 Production에 확정 — 하지 않는다.
