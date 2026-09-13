# OpenRouter Free Model Selection Architecture — Experiment (ADR-0026 후속)

## Summary

- `ADR-0026`이 확정한 8단계 경로(Free Pool → Deterministic Filter →
  Candidate Selection(≤3) → `models[]` → OpenRouter 실제 선택 →
  Contract Validation)를 Stage 01~05 각 3회, 총 15회 실행으로 검증했다.
- **Free Pool 조회 → Deterministic Filter → Candidate Selection(tie-break
  포함)까지는 실측으로 확정적으로 동작을 확인했다** — 5개 Case(0/1/2/3/>3
  candidates) 전부 실제 Pool 메타데이터로 재현했다.
- **OpenRouter 실제 선택(`models[]` 호출) 이후 단계는 이번 세션에서
  검증하지 못했다** — 15회 전부, 그리고 각 회의 bounded retry(1회)도
  전부 HTTP 429(`free-models-per-day` 일일 한도 소진)로 실패했다. 이는
  이 Architecture나 이 실험 코드의 결함이 아니라, 이 세션(그리고 오늘
  하루 누적된 이전 세션들)이 OpenRouter 무료 일일 요청 한도(50/day)를
  이미 소진한 상태에서 실행됐기 때문이다(사실을 숨기지 않는다).
- **최종 판정: D(Evidence 부족)** — Free Pool/Filter/Candidate Selection
  구간은 A 수준 근거가 있지만, OpenRouter 위임·Contract Validation·
  retry 회복 구간은 이번 세션 Evidence로 A/B/C 어느 것도 판정할 근거가
  되지 못한다. 두 구간을 뭉뚱그려 하나의 판정으로 표현하지 않는다.

---

## 1. Free Pool 조회 결과

- 조회 시각 기준 OpenRouter `:free` 모델 **19개** 확인
  (`https://openrouter.ai/api/v1/models`, `data[].id`가 `:free`로
  끝나는 항목만).
- 기록한 metadata: `id`, `context_length`, `architecture.input_modalities`,
  `architecture.output_modalities`, `supported_parameters`(원본 JSON
  전체는 `FreeModelMetadata.raw`에 보존).
- 실측 목록(context_length, input/output modalities):

| model id | context_length | input modalities | output modalities |
|---|---|---|---|
| inclusionai/ling-3.0-flash-vl:free | 262144 | text, image, video | text |
| nex-agi/nex-n2.5-mini:free | 262144 | text, image | text |
| nex-agi/nex-n2.5-pro:free | 262144 | text, image | text |
| inclusionai/ling-3.0-flash-sante:free | 262144 | text | text |
| inclusionai/ling-3.0-flash-fin:free | 262144 | text | text |
| dots-studio/dots-3-note-preview:free | 512000 | text, image | text |
| liquid/lfm-2.5-2.6b:free | 65536 | text | text |
| nvidia/nemotron-3.5-lightning:free | 1000000 | text | text |
| thinkingmachines/inkling-small:free | 1048576 | text, image, audio | text |
| poolside/laguna-s-2.1:free | 262144 | text | text |
| thinkingmachines/inkling:free | 1048576 | text, image, audio | text |
| poolside/laguna-xs-2.1:free | 262144 | text | text |
| cohere/north-mini-code:free | 256000 | text | text |
| nvidia/nemotron-3.5-content-safety:free | 128000 | text, image | text |
| nvidia/nemotron-3-ultra-550b-a55b:free | 1000000 | text | text |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | 256000 | text, audio, image, video | text |
| google/gemma-4-26b-a4b-it:free | 262144 | image, text, video | text |
| google/gemma-4-31b-it:free | 262144 | image, text, video | text |
| nvidia/nemotron-3-super-120b-a12b:free | 262144 | text | text |

- 어떤 모델도 output modality에 `audio`를 포함하지 않았다(§4 "0
  candidates" 경계 조건 설계의 근거).

## 2. Filter 결과

`domain/deterministic_filter.py`가 5개 체크(free/required_capability/
context/modality/contract_compatibility)를 각 모델에 적용했다.

- Stage 01~05 각각의 실제 Requirement(`domain/stage_requirements.py`
  — 기존 `STAGE_POLICIES.token_budget` + 실제 프롬프트 길이 추정치
  `len(prompt)//4` + 20% 안전 여유로 산출한 `min_context_tokens`)로
  필터링한 결과, **19개 중 17개가 KEPT**(2개는 `required_capability`
  FAIL — `thinkingmachines/inkling:free`, `inkling-small:free`, 기존
  실측 Evidence의 "plain chat completion 비기능" 판정을 그대로
  승계·재확인).
- `context_length`가 모든 모델에서 metadata로 존재해(§1 표),
  이번 실행에서는 `context` 체크가 `NOT_DETERMINED`로 떨어진 사례가
  없었다 — `NOT_DETERMINED` 처리 로직 자체는 별도 offline 테스트
  (`tests/test_architecture_experiment.py::test_missing_context_length_is_not_determined_not_excluded`)
  로 검증했다(§9).
- `contract_compatibility` 체크는 설계대로 **19개 전부 NOT_DETERMINED**
  였다 — 사전 메타데이터로 판정하지 않는다는 원칙(ADR-0026 §6)이
  실제로 지켜졌음을 확인.

## 3. Candidate 수 — 5개 Case 전부 실측 확인

Stage 01~05의 실제 Requirement로는 **매번 `>3_candidates`**(17개 KEPT)
로 귀결됐다 — 모든 Stage의 `min_context_tokens` 추정치(수백~수천
토큰)가 Free Pool 대부분의 `context_length`(최소 65536)보다 훨씬
작기 때문이다. 나머지 4개 Case(0/1/2/3)는 실제 Stage Requirement로는
자연 발생하지 않아, **동일한 실측 Pool에 합성 Requirement**(경계
조건을 역산해 설계, `boundary_case_experiment.py`)를 적용해 Filter/
Selection 로직 자체가 5개 Case 모두에서 올바르게 동작하는지 별도
확인했다:

| Case | 적용한 조건(실측 Pool 기반 역산) | 결과 |
|---|---|---|
| 0 candidates | output modality = `audio` 요구(실측 Pool 어떤 모델도 미충족) | kept=0 |
| 1 candidate | input modality = `text+video+audio` 동시 요구 | kept=1(`nemotron-3-nano-omni-30b-a3b-reasoning`만 유일 충족) |
| 2 candidates | min_context=600000 | kept=2(`nemotron-3.5-lightning`, `nemotron-3-ultra-550b`, 둘 다 1,000,000) |
| 3 candidates | min_context=500000 | kept=3(위 2개 + `dots-studio`(512000)) |
| >3 candidates | Stage 01~05 실제 Requirement(전부) | kept=17(2개 known-nonfunctional만 제외) |

이 경계 조건들은 실제 조회한 Pool 메타데이터를 보고 역산한 것이며,
Pool 자체를 조작하지 않았다(§9 재현 방법 참조).

## 4. 최종 3개 후보 — Tie-break 확인

`>3_candidates` Case(Stage 01~05 실제 실행, 15회 전부)에서 **최종
`models[]`는 항상 정확히 3개**였고, 매번 다음과 같았다:

```
['inclusionai/ling-3.0-flash-vl:free', 'nex-agi/nex-n2.5-mini:free', 'nex-agi/nex-n2.5-pro:free']
```

이는 `RFC-0040`/`ADR-0026`이 정의한 tie-break(OpenRouter `/models`
응답 순서 그대로, 재정렬 없이 앞에서부터 3개)가 그대로 적용된
결과다 — 17개 KEPT 중 Pool 응답 순서상 처음 3개가 그대로 뽑혔다(§1
표의 순서와 일치). 15회 모두 동일한 3개였다는 것은 **이 세션 동안
Free Pool의 응답 순서 자체가 반복 조회에도 안정적이었다**는
부수적 관찰이다(반복마다 재조회했음에도 순서 변화 없음, §8).

## 5. 실제 선택 모델

**NOT DETERMINED — 이번 세션에서 확인하지 못했다.**

15회 전부(Stage 01~05 각 3회) OpenRouter가 실제로 어떤 모델을
선택했는지 확인할 수 없었다 — 모든 요청이 HTTP 429로 거부돼 OpenRouter
가 후보 선택 로직 자체에 도달하지 못했다(§7).

## 6. Contract 결과

**NOT DETERMINED — 이번 세션에서 확인하지 못했다.** Contract
Validation은 실제 모델 응답(content)이 있어야 실행되는데, 15회 전부
HTTP 429로 응답 content 자체가 없었다(`contract_passed: null`, 원본
JSON `/tmp/free_model_selection_architecture_experiment_output.json`
확인 가능).

## 7. Latency / HTTP Status / Error

| Stage | rep | HTTP status(attempt 1 / 2) | total_latency_ms |
|---|---|---|---|
| stage01 | 1 | 429 / 429 | 396.7 |
| stage01 | 2 | 429 / 429 | 313.8 |
| stage01 | 3 | 429 / 429 | 344.8 |
| stage02 | 1~3 | 429 / 429(전부 동일) | 313~366 |
| stage03 | 1~3 | 429 / 429(전부 동일) | 308~466 |
| stage04 | 1~3 | 429 / 429(전부 동일) | 315~322 |
| stage05_review | 1~3 | 429 / 429(전부 동일) | 316~422 |

- 원문 오류 메시지(15회 전부 동일): `"Rate limit exceeded:
  free-models-per-day. Add 10 credits to unlock 1000 free model
  requests per day"`, `X-RateLimit-Limit: 50`, `X-RateLimit-Remaining: 0`,
  `X-RateLimit-Reset: 1789257600000`(= 2026-09-13T00:00:00 UTC, 이
  실험 실행 시각 기준 약 13시간 후).
- **원인**: 이 세션(및 오늘 같은 계정으로 실행된 이전 세션들 —
  `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`의 15회,
  `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`의 5회 등)이
  이미 오늘 하루의 무료 요청 한도(50/day)를 이 실험 이전에 소진했다
  — 이 실험 자체의 코드 결함이 아니다.
- **참고(불일치 기록)**: `/api/v1/key` 엔드포인트는 `usage_daily: 0`을
  반환했으나 실제로는 `free-models-per-day` 한도가 소진된 상태였다 —
  이 두 필드가 서로 다른 카운터임을 이번 세션이 실측으로 확인했다
  (`usage_daily`는 과금 사용량, `free-models-per-day`는 별도의 무료
  티어 요청 횟수 한도로 추정된다 — 이는 **추정**이며 OpenRouter가
  공식적으로 이 관계를 문서화한 것을 이번 세션이 확인하지는 않았다,
  NOT DETERMINED로 남긴다).

## 8. Retry

- `RetryPolicy(max_retries=1, exclude_failed_model_from_retry_pool=True)`
  가 15회 전부에서 **정확히 1회 재시도를 수행했다**(`retry_count: 1`,
  `attempts` 배열 길이 2 — 정상 동작 확인).
- 재시도 시 후보 목록이 동일하게 유지됐다 — `classify_failure()`가
  `http_429`를 반환할 때 `exclude_failed_model_from_retry_pool` 로직은
  "실패한 모델"이 아니라 "빈 응답/Contract 실패로 지목된 모델"만
  제외하도록 설계돼 있어(§7 attempts 상세 확인), HTTP 429처럼 후보
  전체가 거부된 경우 같은 3개 후보로 재시도하는 것이 기존 구현의
  의도된 동작이다(`domain/auto_selection_client.py::classify_failure`
  — `http_429`는 `_RETRYABLE_FAILURE_CLASSES`에 있으나 특정 모델을
  지목하지 않으므로 Pool에서 제외할 대상이 없음).
- **재시도가 실제로 다른 candidate로 fallback했는가**: 아니오, 이번
  15회에서는 관찰되지 않았다 — quota 소진이 candidate 전체에 균일하게
  적용되는 계정 단위 제약이라 어떤 모델로 바꿔도 결과가 같았다(§7
  원인 분석과 일관).
- **Contract가 회복됐는가**: NOT DETERMINED — 애초에 HTTP 200 응답
  자체가 없어 Contract 판정이 실행되지 않았다.

## 9. Failure Cases

- 15/15 실행이 동일한 failure class(`http_429`)로 실패했다 — 단일
  실패 유형만 관찰됐고, 다른 실패 유형(malformed_output/timeout/
  connection_error/empty_response)은 이번 세션에서 재현되지 않았다
  (`OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`가 이미
  `empty_response`를, `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-
  0001.md`가 `malformed`류를 각각 다른 세션에서 관찰한 바 있다 — 이
  실험이 그 발견들을 뒤집지 않는다).
- Filter 단계의 경계 조건 실패는 없었다 — `apply_deterministic_filter`/
  `select_candidates`는 15회 + 4개 boundary 시나리오 전부에서 예외
  없이 정상 반환했다.

## 10. Architecture 적합성

| 단계 | 이번 세션 근거 수준 |
|---|---|
| Free Pool | **A(실측 확정)** — 19개 모델, 전체 metadata 실제 조회 |
| Deterministic Filter | **A(실측 확정)** — 5개 체크 전부 실제 동작, `NOT_DETERMINED` 원칙(추측 금지) 실제로 준수됨 |
| Candidate Selection(≤3) | **A(실측 확정)** — 5개 Case(0/1/2/3/>3) 전부 실측 Pool 데이터로 재현, tie-break 규칙(Pool 순서 보존) 실제 동작 확인 |
| OpenRouter `models[]` 호출 자체 | **A(실측 확정, 구조만)** — 요청이 올바른 형태(최대 3개, `models` 필드)로 실제 전송됨을 확인(HTTP 429 응답 자체가 요청이 서버에 도달했다는 증거) |
| OpenRouter 실제 선택 / Fallback | **NOT DETERMINED** — 이번 세션 0회 관찰 |
| Contract Validation | **NOT DETERMINED** — 이번 세션 0회 관찰 |
| Retry 메커니즘 자체(재시도 수행 여부) | **A(실측 확정)** — 15/15 정상 1회 재시도 수행 |
| Retry의 실제 회복 효과 | **NOT DETERMINED** — 이번 세션 0회 관찰 |

---

## 최종 판정: **D. Evidence 부족**

**"ADR-0026에서 확정한 Free Pool → deterministic filter → ≤3 →
models[] 구조가 실제 OpenRouter Free Model 환경에서 성립하는가?"**

**부분적으로 성립한다 — 그러나 전체 경로를 이번 세션이 끝까지
확인하지는 못했다.**

- **Free Pool → Deterministic Filter → Candidate Selection(≤3) →
  `models[]` 요청 구성까지는 성립을 실측으로 확정할 수 있다.** 19개
  실제 모델에 대해 5개 체크가 의도대로 동작했고, 5개 Candidate 수
  Case 전부가 실제 데이터로 재현됐으며, tie-break 규칙도 15회 모두
  일관되게 적용됐다.
- **그러나 "OpenRouter가 이 구조 위에서 실제로 free 모델을 선택하고,
  그 결과가 Contract를 통과하는가"라는 핵심 질문은 이번 세션이
  답하지 못했다.** 15/15 실행이 계정 단위 일일 quota 소진(이 실험
  이전에 이미 소진된 상태)으로 막혔다 — 이는 Architecture의 결함이
  아니라 **이번 세션의 실행 조건(quota 상태) 문제**이지만, "Evidence가
  있는가"라는 질문에는 정직하게 "없다"고 답해야 한다.
- 판정 A(그대로 Production 구현 가능)를 내리기에는 후반부(§5~§7)
  Evidence가 전무하다. 판정 B/C(Filter/Selection 수정 필요)를 내리기
  에는 오히려 전반부(§1~§4) Evidence가 수정이 불필요함을 뒷받침한다
  — 즉 B/C를 정당화할 근거도 없다. 따라서 **D가 유일하게 정직한
  판정**이다.
- **"Auto Selection이 실제로 동작한다"/"동작하지 않는다"를 이 문서는
  주장하지 않는다** — quota 재설정(§7, 2026-09-13T00:00:00 UTC) 이후
  동일 Harness(`projects/openrouter-free-model-selection-architecture-
  experiment-v1/`)를 재실행하면 §5~§7을 메울 수 있다(다음 Experiment
  로 남긴다).

## NOT DETERMINED 종합

- 실제 OpenRouter 선택 모델 분포(§5)
- Contract Validation 결과(§6)
- Retry의 실제 회복 효과(§8)
- `usage_daily`와 `free-models-per-day` 카운터의 정확한 관계(§7)
- `context`/`modality` 체크가 실제로 `NOT_DETERMINED`로 떨어지는
  모델이 Free Pool에 존재하는지(이번 조회 시점 19개 전부 metadata
  완비 — 향후 조회 시 달라질 수 있음)

## Governance / Production 영향

- `RFC-0040`/`ADC-0043`/`ADR-0026` 무수정 — 이 문서는 Reference로만
  인용된다.
- Production `hqs/` 코드 무변경(`git diff --stat -- hqs/` 빈 결과로
  확인).
- Stage 01~05 Production routing 무변경.
- API Key/Authorization 값은 이 실험의 어떤 산출물에도 포함되지
  않았다(원문 오류 메시지에도 Key 값 없음, §7 인용문 확인).

## 재현 방법 / 산출물

- `projects/openrouter-free-model-selection-architecture-experiment-v1/`
  — `domain/free_pool.py`(§1), `domain/deterministic_filter.py`(§2),
  `domain/candidate_selection.py`(§3, §4), `run_experiment.py`(Stage
  01~05 x 3회, §5~§9), `boundary_case_experiment.py`(§3 경계 Case
  4종).
- `tests/test_architecture_experiment.py` — 14개 offline 테스트,
  네트워크 호출 없이 Filter/Selection 로직·`NOT_DETERMINED` 처리·
  Stage Requirement에 모델명이 없음·Production Engine 모듈 미참조를
  검증(전부 PASS).
- 원본 실행 결과: `/tmp/free_model_selection_architecture_experiment_output.json`
  (15회 전체), `/tmp/boundary_case_experiment_output.json`(경계 Case
  4종) — 세션 임시 디렉터리, 이 Evidence 문서가 그 내용을 요약해
  이미 반영했다.

## Related

- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`
- `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
- `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`(최대
  3개 제한의 API-level limit 근거, 이 실험의 `MAX_CANDIDATES=3` 그대로 승계)
- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`(재사용한
  `auto_selection_client.py`/`contracts.py`/`stage_policy.py`/`fixtures.py`의 원 출처)
- `projects/openrouter-auto-selection-v1/`(이 실험이 읽기 전용으로 재사용한 domain 모듈)
