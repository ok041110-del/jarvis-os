# DEV-HQ-V2.0 — Stage 04 Implementation Architecture Validation

## 1. Objective

Stage 04 Implementation의 현재 Single-Agent Baseline과, 제안된
Multi-Agent(+ Ponytail) Candidate Architecture의 실제 품질/비용/지연시간을
동일 조건에서 비교해 Stage 04 Architecture를 Freeze할 수 있는 Evidence를
만든다. 이 작업의 목적은 Multi-Agent를 성공시키는 것이 아니라, 그 가치를
증명하거나 반증하는 것이다.

## 2. Baseline (A)

현재 Production 구현 그대로: `stage_04.py::run_stage_04()`가 Stage 03
`design` → `identify_target()` → `_assemble_build_input()`(Deterministic)
→ `backend_agent_code_generation()`(Engine 1회) → `{target, implementation,
expose_target}`을 반환한다. 이 Harness의 Variant A(`variants.py::
run_variant_a`)는 이와 동일한 "Deterministic Preparation → Existing
Backend Agent ×1" 구조를, Target을 이미 고정한 상태로 재현한다.

## 3. Candidate Architectures

- **B — Multi-Agent**: `implementation`/`consistency`/`minimality` 3개
  고정 ID Agent를 동일 `build_input`에 대해 각각 1회 호출하고,
  Deterministic Gate(syntax/AST/scope/comment-docstring)를 통과한 후보
  중 고정 ID 순서로 Best Candidate를 고른다.
- **C — Multi-Agent + Ponytail**: B와 동일한 생성/Gate 이후, Ponytail
  Adapter(controlled, §11 — 실제 Supervisor 아님)로 Final Candidate를
  고른다.

## 4. Controlled Variables

A/B/C 모두 다음을 고정한다: 동일 `build_input`(합성 Design + Context,
Stage 01/02/03을 실제로 실행하지 않고 고정 문자열로 주입), 동일 Target(
Case별 `allowed_function_names`로 명시), 동일 Exposure(이번 실험은
`expose_target` 개념을 쓰지 않는 순수 코드 생성 비교), 동일 repository
state(어떤 실제 파일도 읽거나 쓰지 않음), 동일 Engine configuration(3개
변형 모두 같은 `engine_call` 함수를 주입받음), 동일 Deterministic Gate/
Validation 로직, 동일 테스트 환경(이 세션의 컨테이너). Target
Identification 자체(`identify_target()`)는 실행하지 않는다 — Target을
Case 정의에 고정해 주입한다(§5의 "Target Resolver 최적화는 후속 실험"
원칙).

## 5. Test Cases

`cases.py`에 5개 정의(전부 합성 데이터, 실제 repository 파일 미참조):

| Case | 설명 |
|---|---|
| `case_a_simple_function` | 단순 함수(`reverse_text`) |
| `case_b_moderate_modification` | 기존 함수 시그니처 확장(`format_amount`) |
| `case_c_helper_reuse` | 기존 helper 재사용이 중요한 작업(`summarize_lines`/`_truncate`) |
| `case_d_overcompression_risk` | 다중 조건 분기 — 과압축 위험(`classify_score`) |
| `case_e_comment_prone` | 비직관적 제약 포함 — comment 생성 가능성 높음(`retry_with_backoff`) |

## 6. Metrics

`result_schema.py::new_result()`가 정의하는 스키마를 그대로 썼다(§13
Result Schema와 동일 — 새 schema를 만들기 전에 기존 telemetry 구조를
조사했으나 이 저장소에는 cost/latency/quality를 기록하는 기존 구조가
없어 요청된 스키마를 그대로 채택). `llm_calls`는 실제 호출 횟수를
정확히 센다. `latency_ms`는 각 실행에서 `time.perf_counter()`로 실측한
값이다(단계별: `generation`/`validation`/`ponytail`/`total`).
`input_tokens`/`output_tokens`/`total_tokens`는 **측정하지 않았다** —
아래 §9 참고.

## 7. Results

**실제 Engine(OmniRoute)을 이 세션 환경에서 사용할 수 없어(§9), A/B/C
Architecture 품질을 비교하는 실행은 수행하지 못했다.** 대신
`run_experiment.controlled_stub_engine_call`(LLM을 전혀 호출하지 않는
고정 응답기)로 5개 Case × 3개 Variant = 15건을 실행해 **Harness
자체의 배선**만 검증했다:

- 15건 모두 정상적으로 Result Schema를 생성했다(`llm_calls`: A=1,
  B=3, C=3 — 전부 정확).
- Deterministic Gate가 각 Case의 `allowed_function_names`에 대해
  scope/syntax를 정확히 판정했다.
- C의 `ponytail` latency만 0보다 큰 값으로 별도 기록됐다(A/B는 0).
- C가 B와 동일한 3개 후보를 재사용하며 Engine을 추가로 호출하지
  않음을 코드/테스트로 확인했다(`test_run_variant_c_reuses_variant_b_
  candidates_without_extra_engine_calls`).

**이 15건은 Architecture 품질 Evidence가 아니다** — 실제 LLM 판단이
전혀 개입하지 않았으므로 A/B/C의 코드 품질 차이를 보여주지 않는다.
원본 결과 파일: `hqs/development/stages/04_implementation/
architecture_validation/sample_run_results.json`(harness self-test
데이터로 명시).

## 8. Failure Cases

Harness 자체 테스트에서 확인한 실패 처리(전부 controlled fake로 재현,
`test_stage04_arch_validation_harness.py`):

- 모든 후보가 Deterministic Gate에서 FAIL하면 B/C 모두 `None`을
  반환한다(Ponytail에 아무것도 전달하지 않음, §10 준수).
- 3개 후보 중 일부만 FAIL해도(예: `consistency`가 SyntaxError) 나머지
  PASS 후보 중 고정 ID 순서로 정상 선택된다.
- 실제 Engine 호출 실패(RuntimeError 등) 자체는 이 Harness 범위에서
  재현하지 않았다 — Production `stage_04.py`의 `_engine_failure_message`
  경로는 기존 `test_stage_04.py`가 이미 검증한다.

## 9. Cost Analysis

**측정 불가.** 이 세션 환경에는 OmniRoute 패키지/서버/환경변수가 전혀
없다(`find / -iname "*omniroute*"` 결과 없음, `OMNIROUTE_*` env var
없음 — Stage 02/03 검증 작업에서도 동일하게 확인된 제약). 또한 현재
`mvp/omniroute_engine.py::call_engine_via_omniroute()`는 응답 텍스트만
반환하고 `usage`(토큰) 필드를 노출하지 않는다 — 설령 OmniRoute가
가용했더라도 실제 토큰 수를 얻으려면 별도 계측 경로가 먼저 필요했을
것이다. 추정값을 Evidence로 기록하지 않았다(`input_tokens`/
`output_tokens`/`total_tokens`는 전부 `None`).

## 10. Latency Analysis

Harness self-test(controlled stub, LLM 미호출) 기준 상대적 구조만
관찰 가능: B/C(3개 순차 호출)의 `generation` 합계가 A(1개 호출)보다
크고, C는 B에 Ponytail Adapter 실행 시간(수 밀리초 미만, 순수 Python
비교/정렬 연산)만 추가된다. **이 수치는 실제 Engine 호출 지연시간을
반영하지 않는다** — stub 함수 호출 자체의 오버헤드일 뿐이다. 실제
Latency Evidence는 실제 Engine 환경에서 재실행해야 확보된다.

## 11. Code Quality Analysis

**측정 불가.** `quality.readability`/`explicitness`/`cognitive_load`/
`simplicity` 4개 지표는 사람 또는 LLM-judge의 판단을 필요로 하는데,
이번 세션은 (a) 실제 Engine이 없어 후보 코드 자체가 생성되지 않았고,
(b) LLM-judge를 이 Harness에 새로 도입하는 것은 이번 작업 범위(§3
"Ponytail Supervisor 실제 구현 금지"와 동일한 이유로, 새로운 판단
Agent를 얼결에 추가하는 것을 피함)를 벗어난다. Result Schema의 해당
필드는 전부 `None`으로 남았다.

## 12. Comment/Docstring Analysis

`deterministic_checks.py::check_comment_docstring_policy()`/
`find_comments_and_docstrings()`는 구현하고 단위 테스트로 검증했다(2줄
초과 comment/docstring을 정확히 탐지). 그러나 실제 Engine이 생성한
코드가 없어 A/B/C 사이의 실제 comment/docstring 발생 빈도 비교는
수행하지 못했다 — `comments.*` 필드는 실제 실행에서 전부 0/False로
남았다(controlled stub이 comment 없는 코드만 반환하기 때문이며, 이 역시
Evidence가 아니다).

## 13. A/B/C Comparison

**실제 품질/비용/지연시간 비교는 수행하지 못했다.** 확인한 것은
"Harness가 A/B/C를 구조적으로 다르게, 그리고 올바르게 실행한다"는
점뿐이다 — llm_calls(1/3/3), Deterministic Gate가 각 후보를 독립적으로
검사한다는 점, Ponytail Adapter가 B의 결과를 재사용해 추가 Engine 호출
없이 동작한다는 점. Architecture의 실제 가치 비교는 이 Harness를 실제
Engine과 연결해 재실행해야 한다.

## 14. Architecture Decision

**보류(Not Determined)** — ADOPT/CONDITIONAL/REJECT/INVESTIGATE 중
어느 것도 이번 세션에서 근거를 갖추지 못했다. 네 판정 모두 최소한
하나의 실제 실행 결과(품질 차이 관찰, 또는 그 부재)를 전제하는데, 이번
세션은 실제 Engine 호출을 단 한 건도 수행하지 못했다. 임의의 사전
threshold로 결과를 유도하지 않기 위해, 근거 없는 판정을 내리지 않는다.
Harness는 실행 가능한 상태로 완성됐으므로, **다음 단계는 OmniRoute
사용 가능 환경에서 `run_experiment.run_all(real_engine_call)`을
실행해 실제 Evidence를 확보하는 것**이다.

## 15. Remaining Issues

- 실제 Engine 환경에서 A/B/C 전체 재실행 필요(가장 중요, 이 문서의
  핵심 미해결 사항).
- Cost 측정을 위해 `call_engine_via_omniroute()`가 반환하지 않는
  `usage` 필드를 노출하는 별도 계측 경로 필요(Production
  `omniroute_engine.py` 수정 여부는 별도 판단 — 이번 작업 범위 밖).
- Quality(`readability`/`explicitness`/`cognitive_load`/`simplicity`)
  측정 방법 자체가 미정 — 사람 평가 루브릭인지 LLM-judge인지 결정 필요
  (이번 작업은 그 결정을 내리지 않았다).
- `check_dependency_validity()`(deterministic_checks.py)는 구현했으나
  이번 Case들에서는 사용하지 않았다 — 실제 closure 기반 `known_names`가
  필요한 Case가 생기면 연결한다.
- Ponytail Adapter는 여전히 controlled stand-in이다 — 실제 Ponytail
  Supervisor 구현은 이 문서가 다루지 않는다(§11, 명시적 Non-goal).
