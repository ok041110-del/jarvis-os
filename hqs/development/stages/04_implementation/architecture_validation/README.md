# Stage 04 Architecture Validation Harness

## 목적

이 폴더는 Stage 04 Implementation의 **Candidate Architecture**(Multi-Agent
+ Ponytail)가 현재 Single-Agent Baseline보다 실제로 나은지 Evidence
기반으로 판정하기 위한 Validation Harness다. Multi-Agent Architecture를
Production에 도입하는 코드가 아니다.

```
Architecture Candidate → Validation → Evidence → Architecture Decision → Freeze
```

지금 상태는 "Validation" 단계다. 이 폴더의 어떤 파일도 `run_stage_04()`
(Production 경로, `../stage_04.py`)에서 import되지 않는다 — Stage 04
Public Contract(`{target, implementation, expose_target}`)는 이 Harness와
무관하게 그대로다.

## 구성

| 파일 | 역할 |
|---|---|
| `result_schema.py` | 실행 1건의 측정값 스키마(`new_result`) |
| `deterministic_checks.py` | syntax/AST/contract/scope/design-coverage/comment-docstring 2줄 정책 — LLM 미호출 |
| `quality_heuristics.py` | Explicitness/Simplicity의 **구조적 근사 신호**(중첩 ternary/comprehension/chaining/lambda, 제어 흐름 중첩 깊이) — Readability/Cognitive Load/전체 Maintainability는 포함하지 않는다(사람·LLM-judge 필요, 아래 참고) |
| `ponytail_adapter.py` | **실제 Ponytail Supervisor가 아닌** controlled adapter — Deterministic Gate를 통과한 후보 중 고정 ID 순서로 하나를 고름(현재 0% refinement, 순수 선택만) |
| `ponytail_policy.py` | Ponytail 정책 guardrail(Target 불변/새 import 금지/Scope 불변/Gate 통과 후보 무변경) — 실제 refinement가 생기면 그 결과를 검증하는 역할 |
| `cost_instrumentation.py` | OmniRoute 응답의 `usage` 필드를 노출하는 **Harness 전용** 계측 경로(Production Thin Caller Contract 무변경) |
| `variants.py` | A(Single-Agent)/B(Multi-Agent)/C(Multi-Agent+Ponytail) 세 실험군의 orchestration. 셋 다 동일한 `build_input`/`target`/`expose_target`을 입력받는다 |
| `cases.py` | 5개 대표 Test Case(합성 데이터, 실제 repository 파일 미사용), 고정 `target`/`expose_target`/`required_function_names` 포함 |
| `run_experiment.py` | Case × Variant 전체 실행, 결과를 JSON으로 저장 |

## 실제 Engine 없이 실행하기

`run_experiment.controlled_stub_engine_call`은 LLM을 호출하지 않는 고정
응답기다 — Harness의 배선(순서 독립성, latency 계측, Gate/Ponytail 연결)
만 검증하며, **Architecture 품질 비교의 Evidence로 쓸 수 없다**. 실제
비교를 하려면 `engine_call`에 실제 Engine 호출 함수(`backend_agent_
code_generation`과 동일한 `str -> str` 시그니처)를 주입해 `run_experiment
.run_all(real_engine_call)`을 실행한다.

## Cost 측정 — 조사 결과

`mvp/omniroute_engine.py::call_engine_via_omniroute()`는 텍스트만
반환하고 토큰 사용량(`usage`)을 노출하지 않는다(의도된 Thin Caller
Contract, ADC-0031/ADR-0017 — 이 Harness는 그 Contract를 바꾸지
않는다). `cost_instrumentation.py::call_with_usage()`가 Production과
완전히 별도인 Harness 전용 경로로 OpenAI-compatible `usage` 필드를
파싱하는 것을 로컬 loopback double(실제 OmniRoute/네트워크 불필요,
`test_omniroute_engine_real.py`와 동일 방법론)로 검증했다 — **OmniRoute
가 실제로 가용해지면 `engine_call` 대신 이 함수를 써서 실제 Cost를
측정할 수 있다.** 이번 세션에는 실제 OmniRoute가 없어 실제 토큰 수는
여전히 측정하지 못했다 — `input_tokens`/`output_tokens`/`total_tokens`
는 실측 전까지 `None`으로 남는다(추정값 사용 안 함).

## Ponytail Adapter는 실제 Ponytail이 아니다

`ponytail_adapter.select_final_candidate()`는 Deterministic Gate를
통과한 후보 중 고정 ID 순서(`implementation` < `consistency` <
`minimality`)로 하나를 고르는 결정적 tie-break일 뿐, LLM 기반 품질
판단을 전혀 수행하지 않는다(0% refinement — 선택된 코드를 절대 수정하지
않는다). 실제 Ponytail Supervisor의 LLM 비용/품질을 검증하려면 이
adapter를 실제 Supervisor 호출로 교체하는 별도 experimental path가
필요하다(§11) — 이번 작업은 그 교체를 하지 않는다. 실제 refinement가
도입되면 `ponytail_policy.verify_policy()`로 "Design/Contract/Scope
불변, Target 불변, 새 import 없음, 이미 통과한 후보는 무수정" 정책을
검증한다.

## Quality 측정의 한계

`quality_heuristics.py`는 §8 Explicitness 체크리스트 중 코드로 결정적
으로 셀 수 있는 부분(중첩 ternary/comprehension/chaining/lambda 개수,
제어 흐름 중첩 깊이)만 다룬다. **Readability**("함수 목적이 명확한가"),
**Cognitive Load**("새 개발자가 얼마나 추론해야 하는가"), 전체
**Maintainability**는 사람 또는 LLM-judge의 판단이 필요해 이 Harness가
결정적으로 대신 측정하지 않는다 — `quality.readability`/
`quality.cognitive_load`는 항상 `None`으로 남는다. LOC는 어떤 지표에도
쓰지 않는다("Short code is not automatically simple code").
