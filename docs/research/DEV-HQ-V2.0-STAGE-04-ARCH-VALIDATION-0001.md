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
  고른다. 현재 Adapter는 선택만 하고 코드를 절대 수정하지 않는다(0%
  refinement). 이번 세션에 추가한 `ponytail_policy.py`는 지시된
  Ponytail 정책(Target/Design/Contract/Scope 불변, 새 import 금지,
  이미 통과한 후보는 무수정)을 코드로 검증하는 guardrail이다 — 실제
  refinement가 도입되면 이 guardrail이 그 결과를 검사한다. 지금은
  Adapter가 아무것도 수정하지 않으므로 이 정책은 항상 공허하게
  만족된다(`test_verify_policy_passes_for_pure_selection_no_
  mutation`, PASS).

## 4. Controlled Variables

A/B/C 모두 다음을 고정한다: 동일 `build_input`(합성 Design + Context,
Stage 01/02/03을 실제로 실행하지 않고 고정 문자열로 주입), 동일
`target`(Case별로 고정된 `(module, function)` 튜플 — 이번 세션에서
`cases.py`에 명시적 필드로 추가), 동일 `expose_target`(현재 5개 Case
전부 `False`로 고정), 동일 repository state(어떤 실제 파일도 읽거나
쓰지 않음), 동일 Engine configuration(3개 변형 모두 같은 `engine_call`
함수를 주입받음), 동일 Deterministic Gate/Validation 로직, 동일 테스트
환경(이 세션의 컨테이너). Target Identification 자체
(`identify_target()`)는 실행하지 않는다 — Target을 Case 정의에 고정해
주입한다(Target Resolver 최적화는 별도 후속 실험 원칙).

`allowed_function_names`(정의해도 되는 최대 범위)와
`required_function_names`(반드시 정의해야 하는 최소 범위)를
분리했다 — `case_c_helper_reuse`가 요구하는 "기존 helper는 재사용만
하고 재정의하지 않아야 한다"를 표현하려면 이 구분이 필요했다.

**B/C 공정성 재검증**: B와 C가 동일한 `engine_call`을 받으면 완전히
동일한 3개 후보(코드 내용까지)를 생성하는지
`test_variant_b_and_c_generate_identical_candidate_pool_from_same_
engine_call`로 확인했다(PASS) — C는 Ponytail Adapter 실행이라는
차이 하나만 추가하고, Candidate 생성 조건은 B와 완전히 동일하다.

## 5. Test Cases

`cases.py`에 5개 정의(전부 합성 데이터, 실제 repository 파일 미참조):

| Case | 설명 |
|---|---|
| `case_a_simple_function` | 단순 함수(`reverse_text`) |
| `case_b_moderate_modification` | 기존 함수 시그니처 확장(`format_amount`) |
| `case_c_helper_reuse` | 기존 helper 재사용이 중요한 작업(`summarize_lines`/`_truncate`) |
| `case_d_overcompression_risk` | 다중 조건 분기 — 과압축 위험(`classify_score`) |
| `case_e_comment_prone` | 비직관적 제약 포함 — comment 생성 가능성 높음(`retry_with_backoff`) |

**Case Coverage 충분성**: 지시된 5개 검증 목적(단순 함수 / 중간 복잡도
기존 코드 수정 / 기존 helper 재사용 / 과압축 위험 / comment 생성
가능성)과 현재 5개 Case가 정확히 1:1로 대응한다 — 이번 라운드에 새
Case를 추가하지 않았다. 이 5개는 "A/B/C 구조 차이를 관찰하기 위한
최소 대표 세트"로는 충분하다고 판단한다(각 Case가 서로 다른 실패
모드를 겨냥함: scope 위반, helper 재정의, 과도한 압축, comment 정책
위반). **다만 실제 Engine Evidence를 확보한 뒤, 5개 중 어느 Case도
A/B/C 차이를 실제로 드러내지 못하는 것으로 판명되면(예: 전부 동일한
품질로 수렴) 그때 추가 Case의 필요성과 구체적 근거를 다시 판단한다** —
지금은 근거 없이 선제적으로 늘리지 않는다.

## 6. Metrics

`result_schema.py::new_result()`가 정의하는 스키마를 그대로 썼다(§13
Result Schema와 동일 — 새 schema를 만들기 전에 기존 telemetry 구조를
조사했으나 이 저장소에는 cost/latency/quality를 기록하는 기존 구조가
없어 요청된 스키마를 그대로 채택).

### 6.1 Deterministic Metrics (LLM/Runtime 없이 지금 측정 가능)

| 항목 | 구현 | 상태 |
|---|---|---|
| Syntax | `check_syntax` | 실측 가능 |
| AST structural validity | `check_ast_structural_validity` | 실측 가능 |
| Contract | `check_contract`(+ `variants.py`가 Case의 고정 `target`/`expose_target`으로 Stage 04 Contract 모양을 조립해 검사) | 실측 가능 |
| Scope | `check_scope` | 실측 가능 |
| Design Coverage | `check_design_coverage`(이번 라운드 이전 세션에 추가) | 실측 가능 |
| Dependency validity | `check_dependency_validity` | **이번 라운드에 버그 수정 + 테스트 추가**(아래 §6.4) — 실측 가능해짐 |
| Comment/Docstring policy(2줄 제한) | `check_comment_docstring_policy` | 실측 가능 |
| Comment/Docstring 집계(count/docstring_count/over_two_lines) | `find_comments_and_docstrings` | 실측 가능 |
| Explicitness heuristic | `quality_heuristics.explicitness_issue_count` | 실측 가능(구조적 근사, §11 한계 명시) |
| Simplicity heuristic | `quality_heuristics.simplicity_issue_count` | 실측 가능(구조적 근사, §11 한계 명시) |
| Ponytail policy guardrails | `ponytail_policy.verify_policy` | 실측 가능(현재 Adapter가 무수정이라 공허하게 PASS, §3/§14) |

### 6.2 Runtime 필요(OmniRoute 또는 실제 파일 적용 필요 — 현재 BLOCKED)

| 항목 | Blocker |
|---|---|
| pytest 실행 결과 | 합성 Case라 적용할 실제 파일이 없음 — 실제 Engine E2E(backup/apply/pytest/diff/원상복구)에서만 확보 가능 |
| 실제 Engine 성공 여부 | OmniRoute unavailable |
| 실제 LLM output quality(내용 자체) | OmniRoute unavailable |
| 실제 token usage(input/output/total) | OmniRoute unavailable + `call_engine_via_omniroute()`가 `usage`를 버림. `cost_instrumentation.py`로 별도 경로는 준비·검증 완료(§9) |
| 실제 cost | 위와 동일 |
| 실제 wall-clock latency | OmniRoute unavailable — `latency_ms.*`는 계측 코드 자체는 동작하지만 지금 값은 stub 호출 오버헤드일 뿐 Engine latency가 아님 |

### 6.3 Human / LLM-Judge 필요(이 Harness가 대신 판단하지 않음)

| 항목 | 비고 |
|---|---|
| Readability | "함수 목적/변수명이 명확한가" — 사람 또는 LLM-judge 필요 |
| Cognitive Load | "새 개발자가 얼마나 추론해야 하는가" — 사람 또는 LLM-judge 필요 |
| Maintainability | Result Schema에 전용 필드 없음, 임의 확장하지 않음(§11) |
| 최종 품질의 정성적 판단 | Architecture Decision의 최종 근거이지만 이 Harness의 결정적 코드로 대체하지 않음 |

평가 방법론 자체(사람 루브릭 vs LLM-judge)는 **미결정 상태로 유지**한다
— §11에서 A/B/C 선택지를 명시하고 임의로 고르지 않는다.

### 6.4 이번 라운드에 발견/수정한 결함

`check_dependency_validity()`는 이전 세션에 구현됐지만 테스트가
전혀 없었다(§2 재검토 중 발견). 실제로 실행해보니 **실제 결함**이
있었다: `dir(__builtins__)`로 builtin 이름을 모으는 방식이 모듈이
`import`될 때는 `__builtins__`가 dict가 되어(`__main__`으로 실행될
때만 module) `len`/`print` 같은 평범한 builtin 호출까지 "unresolved
call target"으로 오판했다. `import builtins; dir(builtins)`로
수정하고 회귀 테스트를 추가했다
(`test_check_dependency_validity_allows_ordinary_builtin_calls`).
이 결함은 실제 Engine 코드에 아직 적용된 적이 없어(§6.1 표처럼 이번
세션 전에는 어떤 테스트도 이 함수를 호출하지 않았다) 이전 Evidence의
어떤 결과도 오염시키지 않았다.

## 7. Results

**실제 Engine(OmniRoute)을 이 세션에서도 사용할 수 없었다 — 이번 작업의
명시적 지시("OmniRoute는 지금 구축하지 않는다, Stage 05까지 마친 뒤
한 번에 구축한다")에 따라 시도조차 하지 않았다.** A/B/C Architecture
품질을 비교하는 실행은 여전히 수행하지 못했다. 대신
`run_experiment.controlled_stub_engine_call`(LLM을 전혀 호출하지 않는
고정 응답기)로 5개 Case × 3개 Variant = 15건을 재실행해 **Harness
자체의 배선**을 이전보다 더 넓은 범위로 검증했다:

- 15건 모두 정상적으로 Result Schema를 생성했다(`llm_calls`: A=1,
  B=3, C=3 — 전부 정확).
- Deterministic Gate가 각 Case의 `allowed_function_names`/
  `required_function_names`에 대해 syntax/scope/design-coverage를
  정확히 판정했다(이번 세션에 `design_coverage` 체크 추가).
- `correctness.contract`가 이번 세션부터 실제로 채워진다(Case의 고정
  `target`/`expose_target`으로 Stage 04 Contract 모양을 조립해 검사) —
  15건 전부 `true`.
- `quality.explicitness`/`quality.simplicity`가 이번 세션부터 실제로
  채워진다(stub 코드 기준 전부 `0` — 구조가 단순한 stub이므로 당연한
  결과이며, 실제 Engine 코드에 대한 Evidence가 아니다).
- C의 `ponytail` latency만 0보다 큰 값으로 별도 기록됐다(A/B는 0).
- C가 B와 동일한 3개 후보를 재사용하며 Engine을 추가로 호출하지
  않음을 코드/테스트로 확인했다(`test_run_variant_c_reuses_variant_b_
  candidates_without_extra_engine_calls`).

**이 15건은 여전히 Architecture 품질 Evidence가 아니다** — 실제 LLM
판단이 전혀 개입하지 않았으므로 A/B/C의 코드 품질 차이를 보여주지
않는다. 원본 결과 파일: `hqs/development/stages/04_implementation/
architecture_validation/sample_run_results.json`(harness self-test
데이터로 명시, 이번 세션에 재생성).

## 8. Failure Policy

정책: **3/3 → 정상 진행 / 2/3 → 정상 진행 / 1/3 → 제한적 진행(생존한
1개를 최종 후보로 채택) / 0/3 → 실패(`None`)**. 이번 라운드에 4개
등급을 전부 명시적으로 테스트했다(`test_failure_policy_*_of_3_*`,
B/C 양쪽 모두 parametrize):

| 통과 비율 | 기대 동작 | 검증 |
|---|---|---|
| 3/3 | 정상 진행 | `test_failure_policy_3_of_3_proceeds_normally` PASS |
| 2/3 | 정상 진행 | `test_failure_policy_2_of_3_proceeds_normally` PASS |
| 1/3 | 제한적 진행(그 1개를 채택, 실패 아님) | `test_failure_policy_1_of_3_proceeds_with_limited_result` PASS |
| 0/3 | 실패(`None`) | `test_failure_policy_0_of_3_fails` PASS |

Execution completion order가 결과를 좌우하지 않는지도 확인했다 —
`test_deterministic_gate_ordering_is_independent_of_completion_order`
가 고정 ID 순서(`implementation` < `consistency` < `minimality`)로만
최종 후보가 결정됨을 검증한다.

그 외 확인한 실패 처리(전부 controlled fake로 재현):

- 실제 Engine 호출 실패(RuntimeError 등) 자체는 이 Harness 범위에서
  재현하지 않았다 — Production `stage_04.py`의 `_engine_failure_message`
  경로는 기존 `test_stage_04.py`가 이미 검증한다.

## 9. Cost Analysis

**실측은 여전히 불가하지만, 계측 경로 자체의 타당성은 이번 세션에
검증했다.** 이번 작업 지시대로 OmniRoute를 이 세션에서 구축하지
않았으므로 실제 토큰 수는 확보하지 못했다. 대신 §7(Cost instrumentation
조사)을 수행했다:

- `mvp/omniroute_engine.py::call_engine_via_omniroute()`는 Production
  Thin Caller Contract(ADC-0031/ADR-0017, `str -> str`)를 그대로
  유지하기 위해 의도적으로 `usage` 필드를 버린다 — 이 Contract를
  바꾸지 않았다(지시 §7 "Contract를 임의 변경하지 않는다" 준수).
  OmniRoute의 `/api/v1/chat/completions`는 OpenAI-compatible이므로
  표준 `usage.{prompt_tokens, completion_tokens, total_tokens}`을
  이미 응답에 포함하고 있을 가능성이 높다(OmniRoute 자체 소스를 이
  세션에서 열람하지는 못했다 — 패키지 부재).
  `cost_instrumentation.py::call_with_usage()`를 Harness 전용 별도
  경로로 만들어, Production 요청 조립과 동일한 로직으로 호출하되
  `usage`를 버리지 않고 함께 반환하도록 했다.
  실제 OmniRoute 없이도 검증 가능하도록, stdlib `http.server`로 만든
  로컬 loopback double(`test_omniroute_engine_real.py`와 동일
  방법론 — 실제 네트워크/OmniRoute 불필요)에 대해 실제로 호출해
  `usage` 파싱이 정확함을 확인했다(`test_call_with_usage_parses_
  openai_style_usage_field`, PASS).
- 결론: **Cost instrumentation은 구조적으로 가능하고 지금 코드로
  준비돼 있다.** 실제 OmniRoute가 붙으면 `engine_call`을
  `cost_instrumentation.call_with_usage`로 교체해 `usage_to_result_
  fields()`로 Result Schema에 매핑하기만 하면 된다 — 추가 설계가
  필요하지 않다. 다만 **이번 세션에는 실제 OmniRoute가 없어 실제 값은
  여전히 `None`이다**(추정값 사용 안 함, `input_tokens`/
  `output_tokens`/`total_tokens` 전부 `None` 유지).

## 10. Latency Analysis

Harness self-test(controlled stub, LLM 미호출) 기준 상대적 구조만
관찰 가능: B/C(3개 순차 호출)의 `generation` 합계가 A(1개 호출)보다
크고, C는 B에 Ponytail Adapter 실행 시간(수 밀리초 미만, 순수 Python
비교/정렬 연산)만 추가된다. **이 수치는 실제 Engine 호출 지연시간을
반영하지 않는다** — stub 함수 호출 자체의 오버헤드일 뿐이다. 실제
Latency Evidence는 실제 Engine 환경에서 재실행해야 확보된다.

## 11. Code Quality Analysis

**부분적으로 가능해졌다 — 4개 지표 중 2개(Explicitness/Simplicity)는
구조적 근사 신호를 결정적으로 측정할 수 있고, 나머지 2개
(Readability/Cognitive Load)와 지시 §8이 추가로 요구한 Maintainability
는 여전히 측정 불가하다.**

- `quality_heuristics.py`(신규)가 §8 Explicitness 체크리스트("지나친
  one-liner/comprehension", "중첩 conditional expression", "과도한
  chaining", "숨겨진 side effect")를 AST 기반으로 결정적으로 센다:
  ternary 표현식 개수, comprehension 중첩 깊이, method chaining 길이,
  lambda 개수. 이 합계를 `quality.explicitness`에 담는다(낮을수록
  명시적) — LOC는 전혀 쓰지 않는다.
  `quality.simplicity`는 제어 흐름(`if`/`for`/`while`/`try`) 중첩
  깊이를 담는다.
  **주의**: 이 숫자들은 "사람이 실제로 헷갈리는지"를 완전히 대체하지
  않는다 — 코드가 구조적으로 평평해도 변수명이 불명확하면 여전히
  읽기 어려울 수 있다. 이 신호는 §8이 명시한 항목 중 AST로 셀 수 있는
  하위 집합일 뿐이다.
- **Readability**("함수 목적/변수명이 명확한가")와 **Cognitive
  Load**("새 개발자가 얼마나 추론해야 하는가")는 본질적으로 사람 또는
  LLM-judge의 판단을 요구한다 — 이번 세션도 그 판단 Agent를 새로
  도입하지 않았다(§3 "Ponytail Supervisor 실제 구현 금지"와 동일한
  이유로, 새로운 판단 Agent를 얼결에 추가하는 것을 피함). `quality.
  readability`/`quality.cognitive_load`는 여전히 `None`이다.
- 지시 §8이 언급한 **Maintainability**는 Result Schema(§13 원본
  스키마)에 전용 필드가 없다 — 임의로 스키마를 확장하지 않고,
  `quality.simplicity`(중첩 깊이 proxy)로 대신 근사했음을 여기 명시한다.

### Readability/Cognitive Load/Maintainability 평가 방법 — 미결정

이 세 항목을 "단순 AST 점수로 대체하지 않는다"는 원칙을 지킨다. 향후
평가 방식으로 다음 세 가지가 후보이며, **어느 것도 이번 세션에서
선택하지 않는다**(임의의 quality threshold도 만들지 않는다):

| 후보 | 설명 |
|---|---|
| A. Human rubric | 사람이 고정된 체크리스트로 채점 — 재현 가능하지만 느리고 비용이 큼 |
| B. LLM Judge | 별도 LLM 호출로 채점 — 빠르지만 그 자체가 새로운 Engine 호출/Agent이므로 "Ponytail Supervisor를 임의로 만들지 않는다"는 원칙과 동일한 신중함이 필요 |
| C. Human + LLM Judge | 초기 LLM 채점 + 표본 사람 검증(calibration) |

**상태: 미결정.** 실제 Engine Evidence를 확보하고 실제 후보 코드가
생기기 전까지는 이 결정을 내릴 근거가 없다.

## 12. Comment/Docstring Analysis

`deterministic_checks.py::check_comment_docstring_policy()`/
`find_comments_and_docstrings()`는 구현하고 단위 테스트로 검증했다(2줄
초과 comment/docstring을 정확히 탐지). 이번 세션부터 `comments.*`
필드가 `variants.py`에서 실제로 채워진다(count/docstring_count/
over_two_lines/`code_changed_for_comment`). 그러나 실제 Engine이 생성한
코드가 없어 A/B/C 사이의 실제 comment/docstring 발생 빈도 비교는 여전히
수행하지 못했다 — 15건 실행에서 전부 0/False로 남았다(controlled
stub이 comment 없는 코드만 반환하기 때문이며, 이 역시 Evidence가
아니다). `code_changed_for_comment`는 Harness가 comment 압축을 위해
코드를 자동 리라이트하지 않으므로 구조상 항상 `False`다(§9 정책 준수
확인).

## 13. A/B/C Comparison

**실제 품질/비용/지연시간 비교는 여전히 수행하지 못했다.** 이번
세션에 새로 확인한 것: Deterministic 검사 축(syntax/AST/contract/
scope/design-coverage/comment-docstring 5종)과 구조적 Quality 근사
축(explicitness/simplicity)은 실제 Engine 코드가 주어지면 **즉시**
A/B/C를 비교할 준비가 되어 있다 — 추가 설계나 Contract 변경 없이
`engine_call`만 실제 함수로 교체하면 된다. 남은 유일한 공백은 실제
Engine 실행 자체(§7)와 사람/LLM-judge가 필요한 Quality 축(§11)이다.

## 14. Architecture Decision

두 개의 서로 다른 Decision을 분리한다 — 이번 라운드에서 추가로
명확히 한 부분이다.

### 14.1 Harness Architecture Decision — 지금 판단 가능

**Ready.** 이 Validation Harness 자체는 실제 Engine 코드가 주어지면
즉시 A/B/C를 비교할 수 있는 상태다: (1) A/B/C orchestration 및 B/C
공정성(동일 candidate pool) 확인, (2) Deterministic 정확성 검사
5종(syntax/AST/contract/scope/design-coverage) + comment-docstring
정책 + 이번 라운드에 결함을 고친 dependency validity, (3) Quality
구조 근사 2종(explicitness/simplicity), (4) Cost 계측 경로(로컬
double로 검증 완료), (5) Ponytail 정책 guardrail, (6) Failure
Policy(3/3~0/3) 전부 테스트로 고정. 추가 설계나 Contract 변경 없이
`engine_call`만 실제 함수로 교체하면 실제 비교를 시작할 수 있다.

### 14.2 Multi-Agent Production Architecture Decision — 지금 불가능

**NOT DETERMINED — Real Engine Evidence Required.**

ADOPT/CONDITIONAL/REJECT/INVESTIGATE 중 어느 것도 이번 세션에서
근거를 갖추지 못했다. 이번 작업 지시가 명시적으로 "OmniRoute는 지금
구축하지 않는다"고 정했으므로, 실제 Engine 실행은 애초에 이번
세션의 목표가 아니었다 — Decision을 이번에 내리지 못하는 것은
실패가 아니라 계획대로다. 네 판정 모두 최소한 하나의 실제 실행
결과(품질 차이 관찰, 또는 그 부재)를 전제하는데, 이번 세션도 실제
Engine 호출을 단 한 건도 수행하지 않았다. 임의의 사전 threshold로
결과를 유도하지 않기 위해, 근거 없는 판정을 내리지 않는다.

**다음 단계는 지시대로 Stage 05까지 구현/검증을 마친 뒤, OmniRoute를
한 번에 구축해 `run_experiment.run_all(real_engine_call)`(또는 Cost가
필요하면 `cost_instrumentation.call_with_usage`)을 실행해 실제
Evidence를 확보하는 것**이다. 그 전까지는 Multi-Agent/Ponytail의 실제
Production 구현에 착수하지 않는다(지시 §12 — Decision과 Freeze 조건
미충족).

## 15. Remaining Issues

- 실제 Engine 환경에서 A/B/C 전체 실행 필요(가장 중요, 이 문서의 핵심
  미해결 사항) — Stage 05 완료 후 OmniRoute 구축이 선행 조건(이번
  작업의 명시적 순서).
- Quality의 Readability/Cognitive Load(및 지시 §8이 요구한
  Maintainability 전체) 측정 방법론이 여전히 미정 — §11의 A/B/C
  선택지(Human rubric/LLM Judge/Human+LLM) 중 아직 고르지 않았다.
  결정되면 Result Schema에 Maintainability 전용 필드가 필요한지도
  함께 판단해야 한다(현재는 `simplicity`로 근사).
- `ponytail_policy.py`는 아직 "선택만 하는" Adapter에만 적용됐다 — 실제
  refinement가 생기면 그 결과에 대해 이 guardrail이 실제로 FAIL을
  낼 수 있는지(현재는 항상 공허하게 PASS) 별도로 검증해야 한다.
- Ponytail Adapter는 여전히 controlled stand-in이다 — 실제 Ponytail
  Supervisor 구현은 이 문서가 다루지 않는다(§11, 명시적 Non-goal).
- `correctness.pytest`는 합성 Case 구조상 이 Harness에서 측정할 수
  없다 — 실제 Engine E2E(Stage 04 VALIDATION.md의 backup/apply/pytest/
  diff/원상복구 절차)에서만 확보 가능하다.
- Cost/Latency는 현재 `generation` 등 단계 합계로만 기록되고 Agent별
  개별 호출 단위로는 분해되지 않는다(Result Schema에 per-agent 필드가
  없음) — 실제 OmniRoute 연결 시점에 Agent별 세분화가 필요한지는 그때
  판단한다(지금 임의로 스키마를 넓히지 않는다).

## 16. 최종 판단(이번 라운드)

**Case C** — Harness는 Ready, Architecture Decision은 NOT DETERMINED
(Real Engine Evidence Required)다. 이번 라운드에 발견한 실제 결함
(`check_dependency_validity`의 `__builtins__` 오판)을 수정하고,
Deterministic Metrics/Runtime 필요/Human-LLM-Judge 필요 3단 분류,
Failure Policy(3/3~0/3) 전 구간 테스트, B/C 공정성 재검증, Case
Coverage 충분성 근거를 모두 명시적으로 고정했다 — Harness 자체를
더 완성시키기 위해 지금 당장 해야 할 코드 작업은 남아 있지 않다. 남은
유일한 진짜 공백은 실제 OmniRoute 환경에서의 실행이며, 이는 이번
작업 지시 자체가 다음 단계로 명시적으로 미뤄뒀다.
