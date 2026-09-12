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
| `deterministic_checks.py` | syntax/AST/contract/scope/comment-docstring 2줄 정책 — LLM 미호출 |
| `ponytail_adapter.py` | **실제 Ponytail Supervisor가 아닌** controlled adapter — Deterministic Gate를 통과한 후보 중 고정 ID 순서로 하나를 고름 |
| `variants.py` | A(Single-Agent)/B(Multi-Agent)/C(Multi-Agent+Ponytail) 세 실험군의 orchestration. 셋 다 동일한 `build_input`을 입력받는다 |
| `cases.py` | 5개 대표 Test Case(합성 데이터, 실제 repository 파일 미사용) |
| `run_experiment.py` | Case × Variant 전체 실행, 결과를 JSON으로 저장 |

## 실제 Engine 없이 실행하기

`run_experiment.controlled_stub_engine_call`은 LLM을 호출하지 않는 고정
응답기다 — Harness의 배선(순서 독립성, latency 계측, Gate/Ponytail 연결)
만 검증하며, **Architecture 품질 비교의 Evidence로 쓸 수 없다**. 실제
비교를 하려면 `engine_call`에 실제 Engine 호출 함수(`backend_agent_
code_generation`과 동일한 `str -> str` 시그니처)를 주입해 `run_experiment
.run_all(real_engine_call)`을 실행한다.

## Cost 측정의 한계

`mvp/omniroute_engine.py::call_engine_via_omniroute()`는 텍스트만
반환하고 토큰 사용량(`usage`)을 노출하지 않는다. 이 Harness는 실제
토큰 수를 추정하지 않는다(§6 "추정값을 Evidence로 사용하지 않는다") —
`input_tokens`/`output_tokens`/`total_tokens`는 실측 불가 시 `None`으로
남는다. 실제 Cost Evidence가 필요하면 OmniRoute 응답의 `usage` 필드를
노출하는 별도 계측 경로가 먼저 필요하다(이번 작업 범위 밖).

## Ponytail Adapter는 실제 Ponytail이 아니다

`ponytail_adapter.select_final_candidate()`는 Deterministic Gate를
통과한 후보 중 고정 ID 순서(`implementation` < `consistency` <
`minimality`)로 하나를 고르는 결정적 tie-break일 뿐, LLM 기반 품질
판단을 전혀 수행하지 않는다. 실제 Ponytail Supervisor의 LLM 비용/품질을
검증하려면 이 adapter를 실제 Supervisor 호출로 교체하는 별도
experimental path가 필요하다(§11) — 이번 작업은 그 교체를 하지 않는다.
