# OpenRouter Auto Selection v1 — Validation Evidence 0001

## Summary

- **Architecture Decision: B(Auto Selection v1 Evidence PARTIAL).** Stage
  01~04는 15/15 실행 전부 API 성공 + Contract PASS + 재시도 0회로 강한
  Evidence를 확보했다. Stage 05(Review, experimental/advisory)는
  **이 실험의 Fixture 결함**(실제 Stage 04 산출물이 아니라 placeholder
  텍스트가 Review 입력에 들어감, §13/§19)으로 인해 "실제 Implementation을
  올바르게 리뷰했는가"를 이번 데이터로 판단할 수 없다 — 이 하나의 이유로
  전체를 PASS로 올리지 않는다.
- **`model="openrouter/auto"`는 무료 티어에서 지원되지 않는다**(실측
  HTTP 402 "Insufficient credits" — 표준 요금이 부과되는 유료 기능임을
  공식 문서로도 확인, §5). 대신 OpenRouter 공식 `models` 배열
  파라미터(fallback list)를 사용했다 — 단, **이 배열은 4개 이상을
  넣으면 즉시 HTTP 400("`models` array must have 3 items or fewer")을
  반환한다**는 것을 이번 세션이 처음 실측으로 확인했다(공식 문서에는
  Chat Completions 엔드포인트 기준으로 명시돼 있지 않았음, §5).
- Stage Policy는 **모델 이름을 전혀 갖지 않는다** — 무료 모델 목록
  전체(19개 중 실측으로 확인된 2개 제외 17개)를 매 실행마다 조회해
  앞에서 3개만 잘라 `models` 배열로 넘겼다(재정렬/순위화 없음).
- Contract Validation은 **기존 Production parser**(`reasoning.py::
  parse_structured_output`)를 재사용했다(Stage 01/02) — 새 LLM judge를
  추가하지 않았다.
- 15개 실행(Stage01~04 각 3회 + Stage05 Review 3회) 전부 **API 호출
  성공(HTTP 200), 재시도 0회**였다 — OpenRouter의 `models` 배열
  자체가 요청 1회 안에서 가용성 fallback을 처리했다(관찰: 2개의
  서로 다른 모델이 여러 run에 걸쳐 선택됨에도 Jarvis 쪽 retry
  카운터는 항상 0).
- Fixed Model(이전 Evidence)과 latency를 비교한 결과, **Stage
  01~03은 Auto Selection이 명확히 빨랐고, Stage 04는 오히려
  느렸다** — "Auto Selection이 항상 빠르다"는 주장은 하지 않는다
  (§17이 4개 축을 함께 비교).
- API Key/Credential은 탐색·출력하지 않았다. Production Engine
  Routing은 변경하지 않았다(정적 검사 테스트로 고정, §14).

---

## 1. Objective

Stage 01~05에 특정 LLM을 고정하지 않고, OpenRouter의 free model
fallback 메커니즘으로 "Jarvis가 모델을 직접 지정하지 않아도 Stage
Contract를 통과하며 안전하게 다음 Stage로 진행할 수 있는가"를 실제
15회 실행(5 Stage × 3회)으로 검증한다. Production 최종 채택이 목적이
아니다.

## 2. Architecture

```
Stage
  ↓
Stage Policy (모델 이름 없음: free_only / output_contract / token_budget / timeout / retry_policy)
  ↓
OpenRouter `models` 배열(무료 모델 Pool, 상한 3개, 재정렬 없음)
  ↓
LLM (OpenRouter가 Pool 안에서 실제 가용한 모델을 선택 — 응답의 `model` 필드로 확인)
  ↓
Stage Contract Validation (기존 Production parser 재사용)
  ↓
PASS / FAIL
```

사용자가 제시한 목표 Architecture와 동일한 형태로 구현했다(그대로
채택, 수정 없음).

## 3. Governance Boundary

- OpenRouter를 **Central Router로 구현하지 않았다** — `domain/
  auto_selection_client.py`는 단일 HTTP 호출 함수 하나이며,
  Provider/Model 선택 로직·Routing Policy·Cost/Budget Policy를 이
  Harness 코드 자체에 두지 않는다(선택은 전적으로 OpenRouter
  자신의 `models` 배열 fallback 메커니즘에 위임).
- Jarvis 내부에 새 Router/Gateway를 만들지 않았다 — 이 Harness는
  `projects/openrouter-auto-selection-v1/`에만 존재하고,
  `hqs/development/`의 어떤 Engine 모듈도 import하지 않는다(정적
  검사, `test_harness_does_not_import_or_modify_production_engine_
  modules`, §14에서 재확인).
- Production Engine Contract(`str -> str`, 단일 예외)를 임의로
  바꾸지 않았다 — `auto_selection_client.py`도 동일한 형태(예외 대신
  구조화된 실패 분류를 반환하지만, 이는 기존 Contract를 대체하는 것이
  아니라 이 실험 전용 별도 Adapter일 뿐이다).
- 기존 Stage Architecture(`stage_01.py`~`stage_05.py`)를 변경하지
  않았다 — Contract Validation만 그 모듈들의 실제 parser를 읽기
  전용으로 재사용했다.

## 4. Stage Policy

| Stage | free_only | Contract | token_budget(참고 값, 출처) | timeout | retry |
|---|---|---|---|---|---|
| stage01 | True | `reasoning.py::parse_structured_output` + `REQUIREMENT_REQUIRED_KEYS` | 1200(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §3.1) | 90s | 최대 1회 |
| stage02 | True | 동일 parser + `tasks`/`dependencies` 키 존재 | 1200(§3.2, 일부 모델은 3000 필요했던 사례 있음) | 90s | 최대 1회 |
| stage03 | True | 6개 필수 섹션 존재(문자열 검사) | 1800(§3.3) | 120s | 최대 1회 |
| stage04 | True | AST 파싱 가능 + Target 함수 존재 | 2200(§3.4) | 120s | 최대 1회 |
| stage05_review | True | 비어있지 않은 prose(advisory) | 1800(이전 Review Evidence §2, 그 문서 자신이 2/3 실패를 이미 관찰) | 90s | 최대 1회 |

**어떤 Policy도 모델 이름 필드를 갖지 않는다**(`dataclasses.fields`로
정적 확인, §14). token_budget은 전부 "참고 값"으로 명시했다 — 이
Evidence는 이 값들이 최적이라고 주장하지 않는다(사용자 지시).

## 5. Auto Selection Mechanism

### 5.1 `openrouter/auto` — 무료 티어에서 지원되지 않음(실측)

```
$ curl -X POST .../chat/completions -d '{"model":"openrouter/auto",...}'
{"error":{"message":"Insufficient credits. This account never
purchased credits...","code":402}}
```

공식 문서(`docs/features/model-routing`, WebFetch로 확인)도 "표준
요금이 선택된 모델 기준으로 부과되며, Auto Router 자체에 추가 요금은
없다"고 명시한다 — 즉 free 전용 메커니즘이 아니라 **선택된 모델이
무료인지 여부와 무관하게 동작하는 유료 우선 라우터**다. 이 계정은
credit이 없으므로 이 경로는 처음부터 실행 불가능했다.

### 5.2 `models` 배열(공식 fallback 파라미터) — 채택

```json
{"models": ["A:free", "B:free", "C:free"], "messages": [...]}
```

공식 문서(`docs/guides/routing/model-fallbacks.md`, WebFetch로 확인)
원문: "provide an array of model IDs in priority order"(우선순위
순서로 시도), "the actual model used ... returned in the `model`
attribute of the response body." 무료 모델(`:free`)이 명시적으로
지원된다고 문서에 적혀 있지는 않았으나 **실측으로 지원됨을 확인**
했다(`cost: 0, is_byok: false` 응답, §9~§13).

### 5.3 실측으로 처음 확인한 제약 — 배열 상한 3개

```
$ curl ... -d '{"models": [17개 free 모델], ...}'
{"error":{"message":"'models' array must have 3 items or fewer.","code":400}}
```

이 상한은 WebFetch로 조회한 두 문서 어디에도 Chat Completions
엔드포인트 기준으로 명시돼 있지 않았다(Anthropic Messages 호환
엔드포인트 문서에만 "최대 3개"라는 각주가 있었음) — **이번 세션이
Chat Completions에도 이 상한이 적용됨을 실측으로 처음 확인**했다.
`domain/model_pool.py::MAX_MODELS_PER_REQUEST = 3`으로 고정했다
(추정이 아니라 재현 가능한 HTTP 400 응답 기반).

## 6. Contract Validation

| Stage | 재사용한 기존 Parser/Validator | 신규 LLM Judge 추가 여부 |
|---|---|---|
| 01 | `hqs/development/stages/01_context_analysis/reasoning.py::parse_structured_output`(Production 함수, 읽기 전용 import) | 없음 |
| 02 | 동일 parser + 키 존재 확인(`task_dependency_agent.py`가 스키마 세부 검증을 Deterministic Layer 책임으로 남긴 것과 동일 원칙) | 없음 |
| 03 | 문자열 기반 6-섹션 존재 검사(이전 Evidence와 동일 기준 재사용, 새 기준 발명 아님) | 없음 |
| 04 | `ast.parse` + top-level 함수 존재 확인(순수 정적 분석) | 없음 |
| 05(Review) | 비어있음 여부만(Review는 애초에 advisory이므로 최소 Contract만) | 없음 |

## 7. Retry Policy

| 실패 유형 | 재시도 가능 여부 | 근거 |
|---|---|---|
| HTTP 429 | 가능(최대 1회) | 일시적 provider capacity 문제(이전 세션들에서 반복 관찰) |
| HTTP 5xx | 가능(최대 1회) | 동일 |
| Timeout | 가능(최대 1회) | 동일 |
| Malformed output(4xx, 전체 Pool 소진) | 가능(최대 1회) | OpenRouter가 Pool 전체에서 실패했다는 응답 — 같은 요청 반복보다 재시도 자체가 의미 없을 수 있으나, 정책상 1회는 허용 |
| Contract failure | **가능(최대 1회), 단 실패한 모델을 Pool에서 제외 후 재시도** | 사용자 지시 — "Contract failure가 발생했다고 무조건 같은 요청을 반복하지 않는다", "다른 free model이 선택될 가능성을 고려" |
| Empty response(200이지만 content 없음) | 가능(최대 1회), 동일하게 모델 제외 | Contract failure와 같은 성격(내용 없음) |
| Connection error(네트워크 자체 불가) | **재시도하지 않음** | 재시도해도 동일하게 실패할 근거(연결 자체의 문제, Pool/모델과 무관) |

**실제 관찰(§9~§13)**: 15회 전부 재시도가 필요한 상황 자체가
발생하지 않았다(`retry_count: 0` 전부) — Contract failure/malformed
output/HTTP 오류 어느 것도 0건이었다. 따라서 위 표의 재시도 로직은
**실제 실행 경로로는 검증되지 않았다** — Fault Injection 테스트
(§14, `test_retry_count_never_exceeds_policy_max_retries`,
`test_contract_failure_excludes_failed_model_from_retry_pool`)로만
검증했다(솔직하게 구분, §21).

## 8. Experiment Setup

- Fixture: 이전 세션(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`,
  `STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md`)과 동일
  시나리오("Add input validation to code review agent",
  `backend_agent_code_review`) — 새 시나리오를 만들지 않아 비교
  가능성을 유지했다.
- 각 Stage 3회, 총 15회 실행.
- Pool은 매 Stage 실행 시작 시 새로 조회(`fetch_free_model_pool()`)
  했다 — 세션 중 Pool 자체가 바뀔 수 있음을 반영.

## 9. Stage 01 Results

| Run | model | success | Contract | latency |
|---|---|---|---|---|
| 1 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 3,805ms |
| 2 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 3,799ms |
| 3 | `nex-agi/nex-n2.5-mini:free` | True | PASS | 2,990ms |

3/3 성공, 3/3 Contract PASS(필수 키 5개 전부), 재시도 0회. 2개의
서로 다른 모델이 선택됐다.

## 10. Stage 02 Results

| Run | model | success | Contract | latency |
|---|---|---|---|---|
| 1 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 4,918ms |
| 2 | `nex-agi/nex-n2.5-mini:free` | True | PASS | 2,609ms |
| 3 | `nex-agi/nex-n2.5-mini:free` | True | PASS | 3,220ms |

3/3 성공, 3/3 Contract PASS(`tasks`/`dependencies` 키 존재), 재시도
0회.

## 11. Stage 03 Results

| Run | model | success | Contract | latency | response_length |
|---|---|---|---|---|---|
| 1 | `nex-agi/nex-n2.5-mini:free` | True | PASS | 9,757ms | 5,539자 |
| 2 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 13,643ms | 3,650자 |
| 3 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 12,450ms | 5,181자 |

3/3 성공, 3/3 Contract PASS(6개 섹션 전부 존재, `missing_sections: []`),
재시도 0회.

## 12. Stage 04 Results

| Run | model | success | Contract | latency |
|---|---|---|---|---|
| 1 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 15,121ms |
| 2 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 10,283ms |
| 3 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS | 14,837ms |

3/3 성공, 3/3 Contract PASS(유효 Python + `backend_agent_code_review`
top-level 함수로 존재), 재시도 0회. 3회 전부 동일 모델이 선택됐다
(Pool의 첫 번째가 매번 가용했다는 뜻).

## 13. Stage 05 Results — 중요한 제한사항 포함

| Run | model | success | Contract | latency |
|---|---|---|---|---|
| 1 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS(non-empty) | 11,760ms |
| 2 | `inclusionai/ling-3.0-flash-vl:free` | True | PASS(non-empty) | 14,695ms |
| 3 | `nex-agi/nex-n2.5-mini:free` | True | PASS(non-empty) | 8,076ms |

3/3 API 성공, 3/3 Contract PASS(비어있지 않음), 재시도 0회.

**⚠️ 중요한 Fixture 결함(정직하게 기록)**: 이 실험의
`build_stage05_review_prompt()`가 "Stage 04 Implementation" 자리에
**실제 Stage 04 실행 결과가 아니라 placeholder 문자열**(`"(same
implementation validated in the Stage 04 run of this experiment)"`)을
그대로 넣는 버그가 있었다 — 사후에 raw 응답을 읽다가 발견했다. 3회
응답 전부가 (placeholder가 아니라) 함께 제공된 **원본(변경 전)
Immutable Source Snapshot**을 실제로 리뷰한 것으로 보인다(원문에
"missing input validation" 지적이 반복됨 — 원본 파일에는 실제로
검증 로직이 없으므로 사실관계 자체는 맞다). **그러나 이는 "Stage 04가
방금 생성한 Implementation을 올바르게 리뷰했는가"를 검증하려던 이
실험의 원래 의도와 다르다** — Stage 05 결과는 **Contract(비어있지
않음)와 latency/model 선택 관점에서만 유효 Evidence**이고, **응답의
의미적 정확성(실제 Implementation 대비)은 이번 데이터로 판단할 수
없다**(§19 Limitations, §21 NOT DETERMINED).

## 14. Tests

`pytest projects/openrouter-auto-selection-v1/tests/ -q` → **15
passed**:

| 항목(사용자 지시 §14) | 테스트 |
|---|---|
| no fixed model enforcement | `test_stage_policy_has_no_model_field`, `test_auto_selection_client_accepts_a_pool_not_a_single_model` |
| stage policy validation | `test_all_five_stage_policies_exist_with_required_fields` |
| contract validation | `test_stage01_contract_reuses_real_production_parser`, `test_stage01_contract_passes_on_well_formed_json`, `test_stage01_contract_fails_on_missing_keys`, `test_stage03_contract_fails_when_sections_missing` |
| retry bound | `test_retry_count_never_exceeds_policy_max_retries` |
| failure classification | `test_classify_failure_maps_http_statuses_correctly`, `test_contract_failure_excludes_failed_model_from_retry_pool` |
| selected model recording | `test_successful_result_records_the_actually_selected_model` |
| deterministic result ordering | `test_attempts_list_preserves_chronological_order_not_reordered` |
| stage isolation | `test_stage_policies_do_not_share_mutable_pool_state` |
| no production routing mutation | `test_harness_does_not_import_or_modify_production_engine_modules`, `test_model_pool_cap_matches_openrouter_measured_limit` |

**기존 Production 테스트**: `pytest hqs/development/mvp/tests/ -q` →
**324 passed, 6 skipped**(기존 baseline과 동일, 회귀 없음).

## 15. Latency Analysis

| Stage | mean | p50 | min | max | stdev |
|---|---|---|---|---|---|
| 01 | 3,531.5ms | 3,799.2ms | 2,990.1ms | 3,805.3ms | 382.8ms |
| 02 | 3,582.3ms | 3,219.9ms | 2,609.1ms | 4,918.1ms | 976.9ms |
| 03 | 11,950.1ms | 12,450.4ms | 9,757.1ms | 13,642.8ms | 1,625.3ms |
| 04 | 13,413.8ms | 14,837.3ms | 10,282.8ms | 15,121.2ms | 2,217.0ms |
| 05(Review) | 11,510.1ms | 11,759.6ms | 8,075.9ms | 14,694.7ms | 2,707.9ms |

3회씩(사용자 지시 최소 반복 수), 동일 세션(동일 환경)에서 실행했다.

## 16. Reliability Analysis

- **API 성공률**: 15/15(100%).
- **Contract 성공률**: 15/15(100%) — 단 Stage 05는 §13의 제한사항
  때문에 "Contract만 성공, 의미적 정확성은 판정 불가"로 구분한다.
- **Retry 발생**: 0/15(0%) — 재시도 로직은 Fault Injection으로만
  검증됐고 실제 경로로는 트리거되지 않았다.
- **HTTP 오류(429/5xx/timeout)**: 0건.
- **Model Distribution**(사용자 지시 §10):

| Stage | Run1 | Run2 | Run3 |
|---|---|---|---|
| 01 | ling-3.0-flash-vl | ling-3.0-flash-vl | nex-n2.5-mini |
| 02 | ling-3.0-flash-vl | nex-n2.5-mini | nex-n2.5-mini |
| 03 | nex-n2.5-mini | ling-3.0-flash-vl | ling-3.0-flash-vl |
| 04 | ling-3.0-flash-vl | ling-3.0-flash-vl | ling-3.0-flash-vl |
| 05 | ling-3.0-flash-vl | ling-3.0-flash-vl | nex-n2.5-mini |

**관찰**: 15회 중 `nex-agi/nex-n2.5-pro:free`(Pool의 3번째)는 **한
번도 선택되지 않았다** — Pool의 1·2번째(`ling-3.0-flash-vl`,
`nex-n2.5-mini`)만으로 매번 충분했다. 이는 "Auto Selection이 다양한
모델을 골고루 쓴다"는 뜻이 아니라 **"1·2번째가 이 세션 동안 계속
가용했다"**는 뜻이다 — 특정 모델(`ling-3.0-flash-vl`)에 **편중되는
경향**이 관찰된다(15회 중 9회, 60%). 3번째 모델의 실제 fallback
동작(1·2번째가 모두 실패했을 때 3번째로 넘어가는지)은 **이번
실행에서 관찰되지 않았다**(`NOT DETERMINED`, §21).

## 17. Fixed Model Comparison

단순 "더 빠르다"로 판단하지 않고 4개 축을 함께 비교한다.

| Stage | Auto 평균 latency | Fixed 평균 latency(이전 Evidence) | Auto Contract 성공률 | Fixed 성공률(이전 Evidence) | Availability |
|---|---|---|---|---|---|
| 01 | 3,531.5ms | `nvidia/nemotron-3-super-120b-a12b:free` 약 15,502ms(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §9.3, 3/3 성공) 또는 `google/gemma-4-31b-it:free` 약 6,003ms(단 33% 가용성 문제 관찰됨, 같은 문서 §8.1) | 3/3 | Fixed 모델 선택에 따라 3/3(nemotron) 또는 2/6(gemma) | Auto: Pool 안에서 자동 대체, 1개 모델 고정보다 가용성 문제에 덜 취약할 가능성(관찰됐으나 반복 검증 안 됨) |
| 02 | 3,582.3ms | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` 약 17,433ms(3/3) | 3/3 | 3/3 | 둘 다 안정적 |
| 03 | 11,950.1ms | `nvidia/nemotron-3-ultra-550b-a55b:free` 약 52,850ms(3/3) | 3/3 | 3/3 | 둘 다 안정적 |
| 04 | 13,413.8ms | `nex-agi/nex-n2.5-mini:free` 약 8,980ms(3/3, `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §5 최종 순위) | 3/3 | 3/3 | **Fixed가 더 빠름** |
| 05(Review) | 11,510.1ms | 동일 모델(`nex-n2.5-mini`) 평균 10,953ms(`STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md` §8, 단 유효 응답률 33%) | 3/3(Contract만) | 1/3(유효 응답 기준) | Auto가 §13 결함으로 직접 비교 불가하나, 참고 수치는 비슷한 자릿수 |

**단순 결론을 내리지 않는다** — Stage 01~03은 Auto가 명확히
빨랐고(Fixed 대비 4~5배), Stage 04는 Fixed가 더 빨랐다(약 1.5배).
"Auto Selection이 더 빠르다"는 일반화된 주장을 하지 않는다.

## 18. Findings

- `openrouter/auto`는 무료 티어에서 사용할 수 없다(유료 라우터) —
  실제 Evidence로 확정.
- OpenRouter Chat Completions의 `models` 배열은 **3개 상한**이 있다
  — 이번 세션이 처음 실측 확인(문서에 명시 안 됨).
- 무료 모델만으로 구성한 `models` Pool도 정상 동작한다(`cost: 0`).
- Stage 01~04는 Auto Selection으로 100% 성공률·100% Contract
  통과·재시도 0회를 달성했다.
- 모델 선택이 특정 2개 모델(`ling-3.0-flash-vl`, `nex-n2.5-mini`)에
  쏠렸다 — "다양성"이 아니라 "가용성 순서"의 결과다.
- 재시도 로직(HTTP 실패, Contract 실패 시 모델 제외)은 코드/테스트
  수준에서는 검증됐지만, **15회 실제 실행 중 단 한 번도 실제로
  트리거되지 않았다** — "이 재시도 로직이 실전에서 실제로 도움이
  되는지"는 이번 실험이 답하지 못한다.

## 19. Limitations

- Stage 05 Fixture 결함(§13) — Review가 실제 Stage 04 산출물이
  아니라 원본 소스만 참조했다. 재실행하려면 추가 API 호출이
  필요하며 이번 세션은 이를 수행하지 않았다(정직하게 결함으로만
  기록, §21).
- Pool의 3번째 모델(`nex-n2.5-pro`)이 한 번도 선택되지 않아 "3개
  fallback이 실제로 3단계까지 동작하는가"는 검증되지 않았다.
- 15회 모두 같은 세션·같은 시간대에 실행됐다 — 시간대/부하가 다른
  조건에서도 같은 모델 분포가 재현되는지는 확인하지 않았다.
- Fixed Model 비교(§17)는 이전 세션들의 Evidence를 인용한 것이며,
  이번 세션이 Fixed Model을 다시 실행해 직접 비교한 것이 아니다 —
  환경/시점 차이가 있을 수 있다.

## 20. Recommendation

**Production Adoption을 이 Evidence만으로 승인하지 않는다.**
확정 가능한 것과 아닌 것을 구분한다:

- **확정 가능**: Stage 01~04에서 OpenRouter Free `models` 배열
  기반 Auto Selection이 구조적으로 동작하며(모델 이름 미지정,
  Contract 통과, 낮은 latency), 최소 침습적 구현(3개 상한 확인,
  기존 parser 재사용, 새 Router 없음)으로 달성 가능하다는 것.
- **확정 불가**: Stage 05를 포함한 5-Stage 전체에 대한 결론(§13
  결함), 모델 선택의 시간대별 재현성(§19), 3단계 fallback의 실제
  동작(§16).
- 이 Evidence는 "다음에 Stage 05 Fixture를 고쳐 재실행하고, 다른
  시간대에 반복 실행해 모델 분포/재시도 경로를 추가로 확인한 뒤"
  재판단할 것을 제안한다(구현/결정은 이 문서 밖).

## 21. NOT DETERMINED

- Stage 05 Review의 실제 Implementation 대비 의미적 정확성(§13
  Fixture 결함).
- Pool 3번째 모델로의 실제 fallback 동작(15회 중 0회 관찰).
- HTTP 429/5xx/Contract failure 시 재시도 로직의 실전 효과(Fault
  Injection으로만 검증, 실제 경로 미관찰).
- 다른 시간대/부하 조건에서 모델 분포가 재현되는지.
- token_budget 참고 값들이 Auto Selection 맥락에서도 여전히
  적절한지(선택되는 모델이 매번 달라질 수 있으므로, 특정 모델에
  맞춰졌던 이전 budget이 다른 모델에는 부족/과할 수 있음 — 이번
  15회는 전부 Contract를 통과했으므로 이번 표본에서는 문제가
  없었으나 일반화하지 않는다).

---

## Validation — Production 무변경 및 Credential 미출력 확인

```
$ git diff --stat -- hqs/
(출력 없음)
```

- API Key/Credential 값을 어디에도 출력·저장하지 않았다 —
  Authorization 헤더를 설정하지 않았고, 이 세션 Proxy의 자동 인증
  주입에만 의존했다.
- Production Engine Routing(`mvp/chatgpt_engine.py`, `mvp/engine.py`,
  `stages/05_validation/stage_05.py`)은 이 실험의 어떤 코드도
  import하지 않는다(정적 검사 테스트로 고정, §14).
- 기존 RFC/ADC/ADR(`ADR-0024`, `ADR-0025`, `RFC-0039`, `ADC-0042`)은
  이 세션에서 수정하지 않았다 — 전부 조사만 하고 Related로 인용했다.

## Related

- `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md`(Fixed Model 비교 원 출처, §17)
- `docs/research/STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md`(Stage 05 Fixed 비교 원 출처, §17)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`,
  `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`,
  `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`,
  `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`(전부 무수정)
- `projects/openrouter-auto-selection-v1/`(이번 세션 신규 Harness)
