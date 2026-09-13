# Stage 05 Review Validator LLM — 실제 3회 실행 Evidence 0001

## Summary

- **Objective 재확인**: LLM Review를 Production에 채택하려는 것이
  아니라 "Stage 05에 LLM Review를 추가할 실질적 가치가 있는가"를
  실제 3회 실행으로 판단하기 위한 Evidence다.
- **3회 전부 API 호출은 성공(200 OK)했지만, 실제로 분석 내용을 담은
  응답은 3회 중 1회(33%)뿐이었다** — 나머지 2회는 `finish_reason:
  length`로 지정한 `max_tokens`(1,800) 전부를 내부 reasoning에
  소모하고 최종 답변(`content`)이 빈 문자열이었다(실측 확인,
  `usage.reasoning_tokens: 2,244` > `max_tokens: 1,800`인 경우까지
  관찰). 이는 latency 문제가 아니라 **Reliability 문제**다.
- **latency는 3회 모두 비슷했다**(10,740~11,215ms) — 응답 내용의
  유무와 무관하게 토큰 생성 시간 자체가 지배적이었다.
- **실제로 얻은 1개의 유효한 응답은 "No real issues found"** —
  deterministic Review(findings 0건)와 **완전히 일치**했다. 이번
  fixture에서는 LLM이 deterministic이 놓친 결함을 추가로 찾지
  못했다(추가 발견 0건).
- **Verdict는 3회 모두 영향받지 않았다** — Review가 성공/실패/빈
  응답 어느 경우든 Aggregator의 deterministic Verdict는 PASS로
  고정됐다(설계대로 동작 확인).
- **Latency Budget**: Review LLM(평균 10,953ms)을 최적화된 Test
  baseline(9,549ms)과 병렬 실행하면 총 latency ≈ **10,953ms(+14.7%)**,
  순차 실행하면 ≈ **20,502ms(+114.7%)**다.
- **API Key/Credential은 탐색하거나 출력하지 않았다** — 이 세션의
  Egress Proxy가 자동으로 인증을 주입하는 기존 메커니즘만 그대로
  재사용했다. Production Engine Routing은 변경하지 않았다(신규
  `domain/openrouter_experimental_adapter.py`는 Harness 내부에만
  존재).
- 결론은 이 문서의 §Production Recommendation에서 Evidence에 근거해서만
  내린다 — "LLM Review가 필요/불필요하다"는 임의로 주장하지 않는다.

---

## 1. Experimental Setup

- **대상**: 이전 세션들이 이미 반복 사용한 동일 Fixture —
  `backend_agent_code_review`(`hqs/development/mvp/agents/backend.py`)에
  입력 검증을 추가하는 Implementation(원본 파일을 읽어 문자열
  치환으로 구성, 하드코딩 사본 없음, `domain/fixtures.py`).
- **선행 조사(수정 없이 참고만)**: `ADR-0025`, `RFC-0039`, `ADC-0042`,
  `STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`,
  `STAGE05-LATENCY-OPTIMIZATION-EXPERIMENT-0001.md` — 전부 이번
  세션에서 재조사만 했고 수정하지 않았다.
- **격리 확인**: 실행 전 `git status --short`/`git diff --stat --
  hqs/`가 무출력임을 확인했고, 실험 종료 후에도 동일하게 무출력임을
  재확인했다(§Validation).

## 2. Model

- **`nex-agi/nex-n2.5-mini:free`**(OpenRouter, 무료 티어) — 이전
  세션(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`)이 Stage 04 Code
  Generation 후보로 이미 실측 검증(3/3 성공, Stage 05 실제 검증
  기준 PASS)했던 것과 같은 모델을 재사용했다 — 새로 모델을 고르는
  실험이 아니라 Review Input 경계와 실질적 가치를 검증하는 것이
  목적이기 때문이다.
- 모델은 **고정 지정**했다 — `openrouter/free` 자동 라우팅을 쓰지
  않았다(`domain/openrouter_experimental_adapter.py::
  make_openrouter_engine_call(model=...)`).
- `max_tokens=1,800`(3회 공식 실행 전부 동일 설정 — 사용자 지시의
  "동일한 Stage 04 Implementation을 사용하여 ... 정확히 3회
  실행한다"를 "동일 설정으로 3회"로 해석해 파라미터를 실행 중간에
  바꾸지 않았다).

## 3. Input Boundary

Review Input을 다음 5가지로 명시적으로 제한했다(`domain/review.py::
_build_llm_review_prompt`):

1. Stage 03 Design(`ctx.design_context`, 고정 텍스트 — 이 Fixture가
   흉내 내는 "입력 검증 추가" 요구사항, `domain/fixtures.py::
   FIXED_DESIGN_CONTEXT`)
2. Stage 04 Implementation(`ctx.implementation`)
3. Contract(함수 시그니처가 `str -> str`을 유지해야 한다는 설명 —
   프롬프트 내 고정 문자열)
4. Scope Context(`ctx.scope_candidates` — Result가 아니라 정의, RFC-0039
   §9의 구분을 그대로 유지)
5. Immutable Source Snapshot(`ctx.original_source_snapshot` — 변경 전
   원본 파일 전체)

**Structure/Scope/AST/Dependency/Test의 `ValidatorResult`는 어떤
형태로도 프롬프트에 들어가지 않는다** — `_build_llm_review_prompt(ctx)`
의 시그니처 자체가 `ValidationContext` 하나만 받으므로 애초에 결과
객체를 받을 수 없다. 이는 코드 수준 강제이며, `tests/test_harness.py`
의 `test_llm_review_prompt_contains_only_the_allowed_input_boundary`/
`test_llm_review_prompt_never_contains_other_validator_result_fields`/
`test_llm_review_prompt_builder_signature_only_accepts_context` 3개
테스트가 실제로 확인한다(전부 PASS, §13).

## 4. Run 1

| 항목 | 값 |
|---|---|
| model | `nex-agi/nex-n2.5-mini:free` |
| success(API 호출) | **True**(HTTP 200) |
| total latency | **11,215.22ms** |
| API latency | 11,215.21ms(전체 latency와 사실상 동일 — 프롬프트 조립 비용은 무시할 수준) |
| finding count | **응답 내용 없음(0, 하지만 "0건 발견"이 아니라 "발견 못함")** |
| finding 요약 | **`content`가 빈 문자열** — 진단 결과 `finish_reason: "length"`, `usage.reasoning_tokens: 2,244` (`max_tokens: 1,800`보다 큼 — reasoning 자체가 잘림, §9 참고) |
| 실제 semantic defect 여부 | 판정 불가(응답 없음) |
| deterministic과 중복 여부 | 판정 불가 |
| false positive | 판정 불가(응답 없음이므로 존재할 수 없음) |
| final deterministic verdict | **PASS**(Review 상태와 무관) |
| Review advisory result | `ValidatorResult("review", status="PASS", ...)` — LLM raw 응답을 자동으로 PASS/FAIL 판정하지 않는 설계이므로 "API 호출 성공"이 곧 status(Policy 구현 금지 원칙 유지) |

## 5. Run 2

| 항목 | 값 |
|---|---|
| model | `nex-agi/nex-n2.5-mini:free` |
| success(API 호출) | **True**(HTTP 200) |
| total latency | **10,903.47ms** |
| API latency | 10,903.44ms |
| finding count(자동 카운트) | 정규식 기반 목록 카운트는 `-1`(번호/불릿 목록 형식이 아닌 산문 — 사람이 직접 판독, §6) |
| finding 요약(원문) | *"No real issues found. The validation is correctly placed, raises a single clear `ValueError`, preserves the existing instruction and engine delegation, and does not alter other functions or add prohibited access."* |
| 실제 semantic defect 여부 | **없음(모델 스스로 명시)** |
| deterministic과 중복 여부 | **완전 일치** — deterministic Review(§6)도 findings 0건 |
| false positive | 관찰되지 않음(정상적인 코드에 대해 실제로 "문제 없음"을 정확히 판단) |
| final deterministic verdict | **PASS** |
| Review advisory result | `ValidatorResult("review", status="PASS", ...)` |

## 6. Run 3

| 항목 | 값 |
|---|---|
| model | `nex-agi/nex-n2.5-mini:free` |
| success(API 호출) | **True**(HTTP 200) |
| total latency | **10,740.57ms** |
| API latency | 10,740.55ms |
| finding count | Run 1과 동일하게 **응답 내용 없음** |
| finding 요약 | `content` 빈 문자열(Run 1과 동일 패턴 — `max_tokens` 소진) |
| 실제 semantic defect 여부 | 판정 불가 |
| deterministic과 중복 여부 | 판정 불가 |
| false positive | 판정 불가 |
| final deterministic verdict | **PASS** |
| Review advisory result | `ValidatorResult("review", status="PASS", ...)` |

## 7. Quality Analysis

- **3회 중 1회(33%)만 실제로 분석 가능한 응답을 얻었다.** 나머지
  2회는 API 호출 자체는 성공했지만 유효한 finding이 존재하지
  않는다 — "0건 발견"과 "응답 자체가 없음"을 구분해서 기록한다
  (혼동하지 않음, 사용자 지시).
- 유일하게 얻은 응답(Run 2)은 deterministic Review와 **정확히 일치**
  했다(둘 다 0 findings, "문제 없음").
- **Quality Consistency 판정: 판단 불가(`NOT DETERMINED`)** — 표본이
  1개뿐이라 "LLM Review의 품질이 일관적인가"를 3개 표본으로 평가할
  수 없다. 이는 회피가 아니라 실제 이 실험이 마주친 제약이다.
- **Finding Consistency 판정: 판단 불가**(같은 이유).
- **참고(공식 3회에는 포함하지 않음, §9)**: `max_tokens`를 4,000으로
  올려 추가로 1회 호출한 결과, **latency 16,898.74ms**에 **363자
  응답**을 얻었다 — 내용은 Run 2와 실질적으로 동일("No real issues
  found" + 근거 3가지). 이는 "이 모델의 Review 판단 자체는 일관되게
  '문제 없음'이지만, 그 판단을 실제로 받으려면 더 큰 `max_tokens`(그리고
  더 긴 latency)가 필요할 수 있다"는 **가설**을 뒷받침하는 참고
  데이터이지, 공식 3회 실행 결과를 대체하지 않는다.

## 8. Latency Analysis

| 통계 | 값 |
|---|---|
| Run 값(ms) | 11,215.22 / 10,903.47 / 10,740.57 |
| 평균(mean) | **10,953.09ms** |
| p50(median) | **10,903.47ms** |
| stdev(population) | **196.9ms** |
| min / max | 10,740.57 / 11,215.22ms |

**latency는 응답 내용의 유무와 무관하게 일정했다** — `max_tokens`
전부를 소진하는 데 걸리는 시간이 지배적이며, 그 결과 reasoning이
제때 끝나 최종 답을 냈는지(Run 2) 아닌지(Run 1, 3)는 latency 차이로
드러나지 않는다.

### Latency Budget 비교(사용자 지시 Part 10)

| 시나리오 | 계산 | 값 |
|---|---|---|
| 현재 Stage 05 optimized baseline(Test만) | `STAGE05-LATENCY-OPTIMIZATION-EXPERIMENT-0001.md` §1/§8 인용 | **9,549ms** |
| **Parallel**(Review를 Test와 동시 실행) | `max(T_test, T_review_llm)` = `max(9,549, 10,953)` | **10,953ms(+1,404ms, +14.7%)** |
| **Sequential**(Review를 Test 이후 실행) | `T_test + T_review_llm` = `9,549 + 10,953` | **20,502ms(+10,953ms, +114.7%)** |

**11초보다 느린 것을 이유로 "실패"로 결론 내지 않는다**(사용자
지시) — 병렬로 배치하면 전체 latency 증가는 14.7%에 그친다는 것이
실측 사실이다. Trade-off는 §11에서 품질 근거와 함께 다룬다.

## 9. Reliability Analysis

- **API 호출 성공률**: 3/3(100%) — HTTP 오류, timeout, upstream
  429/502 전부 0건(재시도 발생 0회, `attempts: 1` 전부).
- **유효 응답 생성률**: 1/3(33%) — 나머지 2/3은 `finish_reason:
  "length"`로 `max_tokens`(1,800)를 reasoning에 전부 소모하고 `content`
  가 `null`(빈 문자열로 정규화)이었다. 진단 호출(§Appendix)로 확인:
  `usage.reasoning_tokens: 2,244`, `usage.completion_tokens: 1,800`
  (상한에 정확히 도달) — 모델이 이 프롬프트 크기(8,006자, 2,145
  prompt tokens)에서 reasoning에 필요한 토큰이 설정된 예산을 종종
  초과한다는 것을 보여준다.
- **Failure/Retry**: 이번 3회 공식 실행에서는 재시도가 필요한 상황
  (429/502/timeout) 자체가 발생하지 않았다 — 관찰된 문제는 "호출
  실패"가 아니라 "성공했지만 쓸모 있는 내용이 없음"이라는 다른 종류의
  신뢰성 문제였다.
- **결론**: 이 모델+설정(`max_tokens=1,800`)의 Review 용도 Reliability는
  **낮다(3회 중 1회만 유효)** — 이는 latency 문제가 아니라 설정
  (token budget) 문제로 보인다(§7 참고 데이터가 이 가설을 뒷받침하나,
  공식적으로 검증하려면 별도의 반복 실험이 필요하다, §14).

## 10. Deterministic Overlap

- Deterministic Review(`domain/review.py::_deterministic_findings`,
  bare-except/TODO/no-docstring 검사)의 이번 fixture 결과: **findings
  0건**.
- 유일하게 얻은 LLM 응답(Run 2)도 **findings 0건**("No real issues
  found").
- **중복 여부**: 둘 다 0건이므로 "겹치는 finding"은 존재하지 않는다 —
  단, 이는 "LLM이 deterministic과 동일한 결론에 도달했다"는 긍정적
  신호로도, "이 fixture 자체가 애초에 결함이 없어서 두 방식 모두
  검출할 게 없었다"는 재현성 낮은 신호로도 해석 가능하다 — 이 문서는
  둘 중 하나로 단정하지 않는다.

## 11. Additional Findings

- **LLM이 deterministic이 놓친 새로운 결함을 발견했는가**: **아니오,
  0건.** 이번 3회(및 §7 참고 1회) 중 어느 응답도 deterministic Review가
  검출하지 못한 새로운 semantic defect를 제시하지 않았다.
- **False Positive**: 관찰되지 않음(0건) — 정상 코드에 대해 잘못된
  결함을 보고한 사례 없음.
- **False Negative**: `NOT DETERMINED` — 이 fixture 자체가 실제로
  결함이 없는(이미 검증된) 코드였으므로, "LLM이 실제로 존재하는
  결함을 놓쳤는가"를 판정할 known-bad 샘플이 이 실험에 없었다.
- **Trade-off(latency 증가 vs 품질 개선, 사용자 지시 Part 11)**: 이번
  실험 범위에서는 **품질 개선이 관찰되지 않았다**(추가 발견 0건) —
  따라서 관찰된 latency 증가(병렬 +14.7% / 순차 +114.7%)를 상쇄할
  만한 품질 이득의 Evidence가 이번 fixture에서는 없다. **단, 이것이
  "모든 상황에서 LLM Review가 무가치하다"는 뜻은 아니다** — 이번
  fixture는 이미 여러 세션에 걸쳐 검증된 "깨끗한" Implementation
  1건일 뿐이며, 실제 결함이 있는 Implementation에 대한 반복 실험은
  이번 세션 범위 밖이다(`NOT DETERMINED`, §14).

## 12. Production Recommendation

**Evidence에 근거해서만 판단한다 — 임의로 "필요/불필요"를 주장하지
않는다(사용자 지시).**

- 이번 3회 실행 + 1회 참고 실행에서 확보한 Evidence는:
  1. Review LLM(이 모델+설정)의 **Reliability가 낮다**(3회 중 1회만
     유효 응답, §9).
  2. 유효했던 1회는 deterministic Review와 **완전히 일치**했다
     (§10) — 이번 fixture에서 **추가 가치를 보여주지 못했다**.
  3. latency 증가는 병렬 배치 시 **관리 가능한 수준**(+14.7%)이지만,
     순차 배치는 **상당하다**(+114.7%, §8).
- **이 Evidence만으로는 "LLM Review를 Stage 05에 채택해야 한다"는
  결론도, "채택하지 말아야 한다"는 결론도 내릴 수 없다** — 표본이
  1개 fixture, 1개 모델, 1개 설정에 국한되고, Reliability 문제
  (33% 유효 응답률)가 이 모델/설정에 국한된 문제인지 근본적인
  문제인지 추가 실험 없이는 구분할 수 없기 때문이다.
- **명확히 확정 가능한 것**: 이번 세션의 Harness 구현(`domain/
  review.py`, `domain/openrouter_experimental_adapter.py`)이 Review
  Input 경계(§3)와 Aggregator 비반영 정책(§4~§6의 "final deterministic
  verdict" 열, 전부 PASS 불변)을 **실제로** 지킨다는 것은 코드+테스트로
  확정됐다(§13) — 이는 "LLM Review를 도입해도 Architecture 원칙이
  깨지지 않는다"는 것이지, "도입해야 한다"는 것이 아니다.
- 특정 모델(`nex-agi/nex-n2.5-mini:free`)을 Production에 확정하지
  않는다 — 이번 실험은 모델 선정 실험이 아니었다(§2).

## 13. Tests

`pytest projects/stage05-parallel-validation-harness-v1/tests/ -q -m
"not slow"` → **26 passed**(기존 21개 + 이번에 추가한 5개):

| 신규 테스트 | 확인하는 것 |
|---|---|
| `test_llm_review_prompt_contains_only_the_allowed_input_boundary` | 프롬프트에 5가지 허용 입력이 전부 포함됨 |
| `test_llm_review_prompt_never_contains_other_validator_result_fields` | `validator_id`/`blocking`/`verdict`/`PASS` 등 다른 Validator 결과 관련 문구가 프롬프트에 없음 |
| `test_llm_review_prompt_builder_signature_only_accepts_context` | 프롬프트 생성 함수가 `ctx` 하나만 받음(독립성의 구조적 강제) |
| `test_openrouter_adapter_wraps_connection_failure_as_single_exception_type` | 연결 실패가 단일 예외(`OpenRouterCallError`)로만 노출됨(기존 Engine Adapter Contract와 동일 패턴) |
| `test_review_llm_result_never_participates_in_deterministic_verdict_even_when_error` | Review가 ERROR여도 나머지 5개가 PASS면 Verdict는 PASS 유지 |

**기존 Production 테스트**: `pytest hqs/development/mvp/tests/ -q` →
**324 passed, 6 skipped**(기존 baseline과 동일, 회귀 없음).

## 14. NOT DETERMINED

- Quality Consistency / Finding Consistency across 3 runs(§7 — 유효
  표본이 1개뿐이라 판정 불가).
- 이 모델의 Reliability 문제(33% 유효 응답률)가 `max_tokens`를
  충분히 크게 잡으면 해소되는지(§7 참고 데이터가 힌트만 제공, 공식
  검증 아님).
- False Negative 여부(§11 — known-bad 샘플 없음).
- 다른 모델/다른 fixture(특히 실제 결함이 있는 Implementation)에서도
  같은 결론(추가 발견 0건)이 재현되는지.
- Sequential/Parallel 배치를 실제로 Production에 구현했을 때의 실제
  Isolation/Failure 동작(이번 실험은 latency만 산술적으로 조합했을
  뿐, 실제 동시 실행 코드를 짜서 측정하지 않았다).
- LLM Review를 Production에 채택할지 여부 자체(§12 — Evidence 부족으로
  판단 보류).

---

## Appendix — 진단 호출 원문(§9 근거, 공식 3회와 별개)

```json
{
  "finish_reason": "length",
  "usage": {
    "prompt_tokens": 2145,
    "completion_tokens": 1800,
    "reasoning_tokens": 2244,
    "cost": 0,
    "is_byok": false
  },
  "content_is_none": true
}
```

`max_tokens=4000`으로 재시도한 참고 호출(latency 16,898.74ms)의 응답
원문:

> No real issues found.
>
> - The validation is placed before the Engine call and matches the
>   stated design: non-empty string after whitespace stripping, with a
>   clear `ValueError`.
> - The review instruction and Engine delegation remain unchanged.
> - No filesystem/network access is added, `call_engine_review`'s
>   signature is untouched, and no other function is modified.

---

## Validation — Production 무변경 및 Credential 미출력 확인

```
$ git diff --stat -- hqs/
(출력 없음)
```

- 이 문서, 관련 스크립트(`domain/openrouter_experimental_adapter.py`,
  `review_llm_real_execution_experiment.py`) 어디에도 API Key/
  Credential 값을 출력하거나 저장하지 않았다 — Authorization 헤더를
  설정하지 않았고(이 세션 Proxy의 자동 주입에 의존), `env` 조회 자체를
  하지 않았다.
- `ADR-0025`/`RFC-0039`/`ADC-0042`는 이 실험에서 수정하지 않았다.
- Production Stage Engine Routing(`mvp/chatgpt_engine.py`,
  `mvp/engine.py`, `stages/05_validation/stage_05.py`)은 전혀
  건드리지 않았다 — `domain/openrouter_experimental_adapter.py`는
  Harness 내부에만 존재하는 별도 Adapter다.

## Related

- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`(무수정, §10 LLM Review Decision Status가 이 Evidence를 인용할 수 있음)
- `docs/research/STAGE05-LATENCY-OPTIMIZATION-EXPERIMENT-0001.md`(baseline 9,549ms 원 출처)
- `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`
- `projects/stage05-parallel-validation-harness-v1/`(`domain/review.py`,
  `domain/openrouter_experimental_adapter.py`,
  `review_llm_real_execution_experiment.py`)
