# OpenRouter Free Model Selection Architecture Experiment (ADR-0026 후속)

## 목적

`ADR-0026`이 확정한 8단계 경로(Free Pool → Deterministic Filter →
Candidate Selection(≤3) → `models[]` → OpenRouter 실제 선택 →
Contract Validation)를 Stage 01~05 실제 Requirement로 실측 검증한다.
Production 최종 채택이 목적이 아니다. 상세 Evidence:
`docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`.

## Scope / 격리 확인

- `projects/openrouter-free-model-selection-architecture-experiment-v1/`
  에만 존재한다. `hqs/development/`의 Engine 모듈(`chatgpt_engine.py`/
  `engine.py`/`omniroute_engine.py`)을 import하지 않는다(정적 검사,
  `tests/test_architecture_experiment.py`).
- `projects/openrouter-auto-selection-v1/domain/`(contracts/fixtures/
  stage_policy/model_pool/auto_selection_client)을 **읽기 전용**으로
  재사용한다 — `domain/_sibling_import.py`가 패키지 이름 충돌(양쪽
  다 최상위 `domain`)을 별칭 로드로 회피한다. sibling 프로젝트의 어떤
  파일도 수정하지 않는다.
- 최대 3개 제한(`domain/candidate_selection.py::MAX_CANDIDATES`)은
  `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` §6의 API-level
  limit 판정을 그대로 승계한다.

## 구성

- `domain/free_pool.py` — Free Pool 조회(§1, metadata 포함).
- `domain/stage_requirements.py` — Stage 01~05 실제 Requirement(모델명
  없음, sibling 프로젝트의 `STAGE_POLICIES`/`fixtures` 재사용).
- `domain/deterministic_filter.py` — ADR-0026 §6 Hard Filter(free/
  capability/context/modality/contract_compatibility, 판정 불가
  항목은 `NOT_DETERMINED`로만 기록 — 제외 사유로 쓰지 않음).
- `domain/candidate_selection.py` — Case 판정(0/1/2/3/>3) + tie-break
  (Pool 응답 순서 보존, 재정렬 없음).
- `run_experiment.py` — Stage 01~05 x 3회, 전체 경로 실행.
- `boundary_case_experiment.py` — 실제 Pool 데이터로 5개 Case
  전부(0/1/2/3/>3)를 재현하는 경계 조건 실험(OpenRouter 호출 없음,
  quota 미소모).
- `tests/test_architecture_experiment.py` — offline 테스트 14개.

## 실행

```
python3 run_experiment.py           # Stage 01~05 x 3회, 실제 OpenRouter 호출 포함(quota 소모)
python3 boundary_case_experiment.py # 5개 Case 재현, OpenRouter 호출 없음(quota 미소모)
pytest tests/ -q
```

## 알려진 제한(Evidence 문서 §7/§10/최종 판정 참조)

이번 세션 실행 시점에는 OpenRouter 무료 일일 요청 한도(50/day)가
이 실험 이전에 이미 소진돼 있었다 — 15/15 실행(Stage 01~05 x 3회)
전부 HTTP 429로 실패했다. Free Pool/Deterministic Filter/Candidate
Selection 구간은 실측으로 확정됐으나, OpenRouter 실제 선택/Contract
Validation/Retry 회복 효과는 **NOT DETERMINED**로 남았다(최종 판정
D — Evidence 부족, 후반부 한정). quota 재설정(기록된 리셋 시각:
2026-09-13T00:00:00 UTC) 이후 `run_experiment.py`를 재실행하면 이
공백을 메울 수 있다.

## Non-goals

- Production Stage 01~05 routing 변경 — 하지 않는다.
- 새 Gateway/Router — 만들지 않는다.
- 특정 모델을 Production에 확정 — 하지 않는다.
- `RFC-0040`/`ADC-0043`/`ADR-0026` 변경 — 하지 않는다.
