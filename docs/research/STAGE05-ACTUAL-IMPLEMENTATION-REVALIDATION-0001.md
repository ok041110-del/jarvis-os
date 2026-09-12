# Stage 05 Actual Implementation Revalidation

## Summary

- 목적: `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`
  §5~§7이 남긴 공백(OpenRouter 실제 선택/Contract/Retry)을 메우기 전에,
  더 이전부터 있었던 **더 근본적인 결함**(Stage 05 Review에 placeholder
  텍스트가 전달됐던 문제, `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-
  0001.md` §13/§19)을 먼저 제거하고, Stage 05만 다시 검증한다.
- Stage 01~04는 이번 작업에서 **재실행하지 않았다** — 이 세션이 이전에
  실제로 실행해 성공시킨 Stage 04 결과(`OPENROUTER-AUTO-SELECTION-V1-
  VALIDATION-0001.md` stage04 run 1, 실제 OpenRouter 응답, HTTP 200,
  Contract PASS)를 원본 JSON에서 바이트 단위로 그대로 복사해 동결
  재사용했다(§1).
- **핵심 수정은 확인됐다(구조적으로 확정)**: Review Prompt에 실제
  Stage 04 Implementation이 실제로 포함됨을 pre-check로 확인했고,
  이전 placeholder 문구가 프롬프트 어디에도 없음을 확인했다(§2).
- **OpenRouter 실제 선택/Contract/Review 결과는 이번에도 확인하지
  못했다** — 3회 실행(+각 1회 재시도, 총 6회 호출) 전부 HTTP 429(일일
  quota 소진, `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`/
  `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`가
  이미 확인한 것과 동일한 quota 상태가 이번 실행 시점에도 그대로
  유지되고 있었다, §5).
- **최종 판정: D(quota/network 때문에 Evidence 부족)** — 단, "이전
  실험의 placeholder 결함이 이번 실험에서 제거됐는가"는 **예**로 별도
  확정한다(§7). 이 두 판단을 뭉뚱그리지 않는다.

---

## 0. 이전 Evidence와의 관계

이 문서는 기존 Evidence를 삭제·수정하지 않는다. 아래 두 문서를 그대로
Reference로 유지하며, 이 문서는 그 둘의 **후속(Stage 05 한정
재검증)**이다:

- `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` — Stage 05 Review에
  placeholder가 전달된 원래 결함이 처음 보고된 문서(§13/§19). 이
  문서의 stage04 run 1 실제 출력을 이번 재검증의 Implementation
  Fixture로 그대로 재사용한다(§1).
- `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` —
  ADR-0026 8단계 경로를 Stage 01~05 전체로 검증했고, OpenRouter 위임
  구간이 quota 소진으로 NOT DETERMINED에 그쳤던 문서. 이 문서는 그
  NOT DETERMINED를 Stage 05에 한해 다시 시도한 것이며, 같은 quota
  상태(전체 소진)가 이번에도 그대로였다(§5).

## 1. Stage 04 Implementation — 존재 여부 / 길이 / 대상

검증 시작 전 pre-check 출력(사용자 지시, 실제 코드 전체는 출력하지
않음):

```
Stage 04 implementation 존재 여부: True
implementation 길이: 3341 chars
대상 module: hqs/development/mvp/agents/backend.py
대상 function: backend_agent_code_review
```

- 출처(provenance): `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`
  stage04 run 1 — `selected_model=inclusionai/ling-3.0-flash-vl:free`,
  `http_status=200`, `contract_passed=True`, `content_length=3341`.
  이 세션이 그 실행 당시 저장한 원본 JSON(`/tmp/auto_selection_full_
  output.json`)에서 **손으로 재입력하지 않고 바이트 단위로 복사**해
  `projects/openrouter-free-model-selection-architecture-experiment-v1/
  domain/fixtures_data/stage04_actual_implementation.txt`에 고정했다
  — 전사 오류를 배제하기 위해 `ACTUAL_STAGE04_IMPLEMENTATION == 원본
  JSON의 final_raw_content` 정확 일치를 실행 시점에 직접 확인했다
  (`True`).
- placeholder/dummy/원본 source 어느 것도 아니다 — 실제 LLM이 실제로
  생성한 Implementation 문자열 그 자체다(내용: `backend_agent_code_
  review`에 `if not isinstance(code, str) or not code.strip(): raise
  ValueError(...)` 검증을 실제로 추가한 코드, 유효한 Python으로
  파싱됨을 확인).

## 2. Review Prompt에 실제 Implementation 포함 여부

Pre-check 출력:

```
Review prompt에 실제 implementation 포함 여부: True
Review prompt에 이전 placeholder 문구 포함 여부(있으면 결함 재발): False
prompt 총 길이: 7429 chars (실제 코드 본문은 출력하지 않음)
```

- `ACTUAL_STAGE04_IMPLEMENTATION in prompt` 문자열 포함 검사로 확인
  (실제 코드 전체를 로그로 출력하지 않고, 포함 여부만 boolean으로
  확인 — 사용자 지시 그대로).
- 이전 결함의 흔적 문구(`"same implementation validated in the Stage
  04 run of this experiment"`)가 새 prompt 어디에도 없음을 직접
  검사했다.
- Input 경계 구조(ADR-0025/RFC-0039 §9: Design/Contract/Scope/Immutable
  Source Snapshot + Implementation)는 그대로 유지했다 — 새 섹션을
  추가하거나 기존 섹션을 제거하지 않았다(`tests/
  test_stage05_revalidation.py::test_review_prompt_preserves_input_
  boundary_sections`로 offline 확인).
- 이 검사가 실패했다면(포함 안 됨 또는 placeholder 잔존) 스크립트
  자체가 `RuntimeError`로 즉시 중단하도록 만들었다 — 결함이 있는
  상태로 실행을 진행시키지 않는다.

## 3. Routing — Stage 05만

```
Free Model Pool → Deterministic Filter → 최대 3개 candidate → models[] → OpenRouter → 실제 selected model → Stage 05 Review
```

- Stage 01~04는 이 실행 경로에 포함되지 않았다(재실행 없음, §1).
- 고정 Stage 05 모델명을 쓰지 않았다 — `domain/stage_requirements.py`
  (기존 `openrouter-auto-selection-v1`의 `STAGE_POLICIES["stage05_
  review"]`를 읽기 전용 재사용, 모델명 필드 없음)를 그대로 썼다.
- Free Pool은 매 회 다시 조회했다(19개 `:free` 모델, 이전 실험과 동일
  구성 — Pool 구성 자체는 짧은 시간 안정적이었다).

## 4. 실행 결과 — 3회

| rep | candidate models(≤3) | selected model | HTTP status | latency | response 존재 | Contract | retry | error category |
|---|---|---|---|---|---|---|---|---|
| 1 | ling-3.0-flash-vl / nex-n2.5-mini / nex-n2.5-pro | None | 429 | (attempt별 상세는 원본 JSON) | False | None | True(1회) | 429_quota(양쪽 attempt 모두) |
| 2 | 동일 3개(Pool 순서 안정적) | None | 429 | 〃 | False | None | True(1회) | 429_quota(양쪽) |
| 3 | 동일 3개 | None | 429 | 〃 | False | None | True(1회) | 429_quota(양쪽) |

- 3회 전부 Candidate Selection은 정상적으로 `>3_candidates` Case에서
  tie-break를 거쳐 동일한 3개 최종 후보를 냈다(`OPENROUTER-FREE-
  MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` §4의 관찰과 일치
  — Pool 순서가 이번에도 안정적이었다).
- 매 회 bounded retry(최대 1회)가 실제로 수행됐다(`retry_performed:
  true`, `retry_count: 1`) — 1차·2차 attempt 모두 HTTP 429였다.
- 원본 오류 메시지(6회 attempt 전부 동일):
  `"Rate limit exceeded: free-models-per-day. Add 10 credits to unlock
  1000 free model requests per day"`, `X-RateLimit-Remaining: 0`.
- 전체 원본 데이터: `/tmp/stage05_actual_implementation_revalidation_
  output.json`(세션 임시 디렉터리, 이 문서가 요약을 반영).

## 5. Retry — 실패 분류

사용자 지시대로 429/5xx/timeout/malformed/Contract failure를 별도
분류하는 사후 분류기(`run_stage05_revalidation.py::
_classify_error_detail`)를 이 harness 전용으로 추가했다(기존
`auto_selection_client.classify_failure()`는 수정하지 않음 —
timeout/connection을 함께 묶는 기존 동작 그대로 두고, 그 위에 문자열
매칭으로 한 단계 더 세분화).

- 6회 attempt(3 run × 2 attempt) **전부 `429_quota`로 분류됐다** — 다른
  카테고리(5xx/timeout/malformed_response/connection_error)는 이번
  실행에서 0건.
- **quota failure를 모델 품질 실패로 판정하지 않았다** — `run_record`
  어디에도 "Review 품질이 나쁘다"는 판단을 기록하지 않았고, 대신
  `openrouter_call_skipped`가 아니라 `response_present: false`로만
  기록해 "호출은 실제로 갔으나 응답 content가 없었다"는 사실만
  남겼다(offline 테스트
  `test_quota_failure_is_never_classified_as_malformed_or_contract`로
  회귀 방지).

## 6. Review 품질 — 기존 Deterministic Validation과 비교

Pre-check 출력(§본문):

```
Deterministic 기준선 — AST: PASS {'scope_ok': True, 'changed_names': []}, Dependency: PASS {'dependency_ok': True, 'added_imports': []}
```

- `stage05-parallel-validation-harness-v1/domain/validators.py`의
  `ast_validator`/`dependency_validator`(RFC-0039 §2.3/§2.4 구현,
  순수 함수, 읽기 전용 재사용, 수정 없음)를 실제 Implementation에
  대해 실행했다.
- 결과: Target 함수(`backend_agent_code_review`) 외 다른 top-level
  정의는 변경되지 않았고(AST PASS), 새 import도 추가되지 않았다
  (Dependency PASS) — 이는 이 Implementation이 Stage 04 Ponytail
  정책(다른 함수/구조 미변경)을 실제로 지켰다는 **결정적** 확인이다.
- **LLM Review 결과 자체(§4)는 이번 세션에서 얻지 못했으므로, "LLM
  Review가 이 Deterministic 기준선과 일치/불일치하는지"는 비교할
  수 없다** — 비교 대상 한쪽(Deterministic)만 확보됐다는 사실을
  그대로 남긴다.
- **"단순히 PASS 문자열이 나왔다는 이유만으로 Review 품질이 검증됐다고
  주장하지 않는다"**: 이번 실행에서는 LLM Review의 "PASS" 문자열
  자체가 아예 없었다(HTTP 429로 응답 content 부재) — 애초에 그런
  주장을 할 재료가 없다. Deterministic 기준선(AST/Dependency PASS)은
  LLM Review와 **다른 방법론**의 결과이며, 이 문서는 이를 "LLM Review
  가 검증됐다"는 근거로 대체하지 않는다.

## 7. 이전 실험과 비교 — placeholder 결함이 제거됐는가

| 항목 | 이전(`OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`) | 이번(이 문서) |
|---|---|---|
| Review 대상 | placeholder 문자열(`"(same implementation validated in the Stage 04 run of this experiment)"`, 실제 코드 아님) | 실제 Stage 04 Implementation(3341 chars, 실제 OpenRouter 응답, 원본 JSON에서 바이트 단위 복사) |
| 검증 시점 확인 | 사후에(실행 뒤 raw response를 읽다가) 발견 | **사전에**(실행 시작 전 pre-check로 확인, 불일치 시 `RuntimeError`로 즉시 중단하도록 설계) |
| 결과 | Review가 "원본 코드에는 검증이 없다"는, 사실이지만 의도한 대상이 아닌 것에 대한 관찰을 했다 | 이번 세션은 실제 Review 결과 자체를 얻지 못함(quota, §4) — placeholder 문제와는 무관하게 별도 원인으로 막힘 |

**결론: 이전 실험의 placeholder 결함은 이번 실험에서 확정적으로
제거됐다(§1, §2 — 구조적 근거, 실행 성공 여부와 무관하게 확인
가능).** 다만 그 수정이 "실제로 더 나은 Review 결과를 낳는지"는
OpenRouter 응답 자체가 없어 이번에도 확인하지 못했다 — 결함 제거와
품질 개선 확인은 서로 다른 질문이며, 전자만 이 세션이 답했다.

## 최종 판정

**D. quota/network 때문에 Evidence 부족** — Review 결과/Contract/
Deterministic-LLM 비교(§4, §6)에 한정된 판정이다.

이와 별개로, 다음은 이 판정과 뭉뚱그리지 않고 명시적으로 분리 확정한다:

- **Routing 구성 자체(Free Pool → Filter → ≤3 → `models[]` 요청 구성)**:
  `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`가
  이미 A로 확정한 것을 이번 Stage 05 단독 실행도 동일하게 재확인했다
  (§3, §4 — Filter/Selection/tie-break 정상 동작).
- **Placeholder 결함 제거**: **확정(Yes)** — §1, §2, §7이 근거. 이는
  quota와 무관하게 이번 세션이 확인 가능했던 사실이다.
- **LLM Review가 실제로 유의미한 결과를 내는지**: 여전히 NOT
  DETERMINED — 이번에도 실제 응답을 얻지 못했다.

이 세 가지를 하나의 A/B/C/D로 합쳐서 보고하지 않는다 — 사용자 지시가
요구한 "반드시 구분한다"를 그대로 따른다.

## NOT DETERMINED 종합

- 실제 OpenRouter 선택 모델(Stage 05, 이번 3회) — 전부 미확인.
- 실제 Stage 05 Review 결과 content — 전부 미확인.
- Contract Validation 결과(Stage 05 Review Contract, non-empty 검사) —
  전부 미확인.
- LLM Review와 Deterministic(AST/Dependency) 기준선의 실제 일치/불일치
  — 비교 불가(한쪽 데이터 없음).
- Retry가 실제로 다른 candidate로 회복시키는지 — 이번에도 관찰되지
  않음(quota가 계정 단위라 후보를 바꿔도 결과가 같음, 이전 Evidence와
  일관).

## Governance / Production 영향

- `RFC-0040`/`ADC-0043`/`ADR-0026` 무수정.
- 기존 Stage 05 Architecture(Production `stage_05.py`) 무변경.
- Production `hqs/` 코드 무변경(`git diff --stat -- hqs/` 빈 결과로
  확인, 이 문서 작성 시점 재확인).
- 기존 Experiment Harness(`openrouter-free-model-selection-architecture-
  experiment-v1/`의 기존 파일)는 수정하지 않고, 이번 재검증에 필요한
  파일만 새로 추가했다(§재현 방법).
- `projects/openrouter-auto-selection-v1/`,
  `projects/stage05-parallel-validation-harness-v1/`의 기존 파일도
  전부 무수정(읽기 전용 재사용만, 별칭 로더로 충돌 회피).
- API Key/Authorization 값은 이 실험의 어떤 산출물에도 포함되지
  않았다.

## 재현 방법 / 산출물(신규 파일만, 기존 파일 무수정)

- `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/stage05_actual_implementation_fixture.py`
  — 실제 Stage04 Implementation 동결(§1).
- `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/fixtures_data/stage04_actual_implementation.txt`
  — 원본 바이트 그대로 저장.
- `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/stage05_deterministic_comparison.py`
  — AST/Dependency 기준선(§6, `stage05-parallel-validation-harness-v1`
  읽기 전용 재사용).
- `projects/openrouter-free-model-selection-architecture-experiment-v1/domain/_sibling_import_stage05_harness.py`
  — 별칭 로더(패키지명 충돌 회피, sibling 파일 무수정).
- `projects/openrouter-free-model-selection-architecture-experiment-v1/run_stage05_revalidation.py`
  — 이번 재검증 실행 스크립트(§2~§5).
- `projects/openrouter-free-model-selection-architecture-experiment-v1/tests/test_stage05_revalidation.py`
  — offline 테스트 10개(placeholder 미포함/실제 코드 포함/Deterministic
  기준선/실패 분류, 전부 PASS).
- 원본 실행 결과: `/tmp/stage05_actual_implementation_revalidation_output.json`.

## Related

- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`(원래
  placeholder 결함이 보고된 문서, §13/§19)
- `docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`
  (Stage 01~05 전체 ADR-0026 경로 검증, 이 문서의 직접 선행 문서)
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
  (`models[]` 3개 상한 API-level limit 근거, 이번에도 동일하게 적용)
- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`
- `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
- `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`
- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`(Review
  Input 경계 원 출처, §9)
- `projects/openrouter-auto-selection-v1/`, `projects/stage05-parallel-validation-harness-v1/`
  (읽기 전용 재사용 대상)
