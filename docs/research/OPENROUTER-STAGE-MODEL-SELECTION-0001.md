# OpenRouter Stage 01~04 무료 모델 적합성 선별 — Evidence 0001

## Summary

- 이 세션에서 OpenRouter가 실제로 연결·인증됨을 전제로(`OPENROUTER-VALIDATION-0001.md`
  §8), Stage 01~04 각 역할에 실제 Jarvis 프롬프트/Contract를 그대로 사용해
  `:free` 모델 후보를 최소 2개씩 실제 호출·비교했다(`openrouter/free` 자동
  라우팅 미사용, 매 호출마다 고정 모델 slug 지정).
- Stage 04는 실제 대상 함수(`backend_agent_code_review`,
  `hqs/development/mvp/agents/backend.py`)에 대해 실제 Exposure Policy
  프롬프트(전체 파일 반환 + 단일 함수만 수정)를 그대로 사용했고, Stage 05
  실제 검증 함수(`stage_05.py::_check_structural`/`_check_design_scope`/
  `_determine_verdict`)를 **직접 import해 그대로 실행**했다 — 재구현하지
  않았다. 검증용으로 Production 파일을 임시로 덮어썼지만 매 회 즉시
  원본으로 복원했고(`finally` 블록), 최종 `git status`/`git diff`로 무변경을
  확인했다(§4.4).
- 모든 성공 호출은 `cost: 0`, `is_byok: false`로 확인됨(순수 무료 티어,
  §6).
- 일부 후보(`thinkingmachines/inkling(-small):free`)는 "agentic harness
  전용"이라는 OpenRouter 자체 정책으로 403을 반환해 애초에 호출 불가했고,
  일부(`poolside/laguna-*:free`, 일시적으로 `google/gemma-4-31b-it:free`)는
  이 세션의 테스트 기간 동안 upstream provider shared pool이 429로
  소진되어 있었다 — 두 경우 모두 이 문서의 "모델 자체 품질" 평가에서
  제외하고 "가용성 실패"로 별도 기록한다(§7 Not Determined 처리와는
  다른 카테고리).
- **Production 코드/Architecture/Contract/Governance는 변경하지 않았다.**
  변경 범위는 이 문서(신규)뿐이다.

**후보 Model Mapping (최종)**

```
Stage 01 → google/gemma-4-31b-it:free
Stage 02 → nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
Stage 03 → nvidia/nemotron-3-ultra-550b-a55b:free
Stage 04 → nex-agi/nex-n2.5-mini:free
```

---

## 1. 후보 선정 근거 (OpenRouter `:free` 목록, 이 세션 기준 19개)

`GET /api/v1/models`에서 `:free`로 끝나는 id 19개를 확인한 뒤, 각 모델의
공개 설명(`description`)에 나타난 역할 힌트로 Stage별 후보를 1차 분류했다
(추측이 아니라 OpenRouter가 제공한 설명 문자열 기준):

| Stage | 역할 | 선정한 후보 | 선정 근거(설명 문자열 인용) |
|---|---|---|---|
| 01 | Context 이해/정리 | `google/gemma-4-31b-it:free` | 범용 instruction-tuned dense 모델 |
| 01 | | `nvidia/nemotron-3-super-120b-a12b:free` | "open hybrid MoE model" 범용 대형 모델 |
| 02 | Specification/요구사항 명세 | `nex-agi/nex-n2.5-pro:free` | "agentic model built to turn goals into working, verified outcomes" |
| 02 | | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 이름에 명시적 "reasoning" |
| 03 | Architecture Design/Reasoning | `nvidia/nemotron-3-ultra-550b-a55b:free` | "open frontier-reasoning and orchestration model" |
| 03 | | `thinkingmachines/inkling:free`(§2 사유로 대체) → `inclusionai/ling-3.0-flash-vl:free` | 대형 MoE 범용 모델(대체 사유 §2) |
| 04 | 실제 Code Generation | `poolside/laguna-s-2.1:free`(§2 사유로 대체) → `nex-agi/nex-n2.5-mini:free` | (대체 사유 §2); nex는 "goals into working, verified outcomes" — 코드 산출물 지향 |
| 04 | | `cohere/north-mini-code:free`(§2 사유로 실패 기록) / `nex-agi/nex-n2.5-pro:free` | "Cohere's first agentic coding model" 명시 |

## 2. 호출 중 발견한 가용성 문제(모델 품질과 분리해서 기록)

| 모델 | 증상 | 원인(OpenRouter 응답 원문 기반) | 처리 |
|---|---|---|---|
| `thinkingmachines/inkling:free` | HTTP 403 | `"...is only available on agentic harnesses. Try plugging it into a coding agent..."`(OpenRouter 정책) | Stage 03 후보에서 완전히 제외, `inclusionai/ling-3.0-flash-vl:free`로 대체 |
| `thinkingmachines/inkling-small:free` | HTTP 403 | 위와 동일 정책 | 대체 시도하지 않음(같은 정책 재확인 목적으로만 1회 호출) |
| `poolside/laguna-s-2.1:free` | HTTP 429(3회 재시도, 약 10분 간격에도 동일) | `"...is temporarily rate-limited upstream...upstream_provider_shared_pool"`(Poolside 공유 pool 소진) | Stage 04 후보에서 제외(가용성 실패, 품질 미평가) |
| `poolside/laguna-xs-2.1:free` | HTTP 429 | 위와 동일(Poolside 동일 provider) | 위와 동일 |
| `google/gemma-4-31b-it:free` | HTTP 429(1회) | `upstream_provider_shared_pool`(Google AI Studio) | Stage 04 재시도에서만 1회 발생 — Stage 01에서는 정상 성공(§3), 이 모델 자체의 구조적 문제가 아니라 이 세션의 호출 빈도에 따른 일시적 현상으로 판단 |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | HTTP 502(1회, Stage 04 재시도) | `"Upstream error from Nvidia: ResourceExhausted: Worker local total request limit reached (16/16)"` | Stage 04 후보에서 제외(가용성 실패) — Stage 02에서는 정상 성공(§3) |

**해석**: 이 실패들은 OpenRouter 자체의 연결/인증 문제(§1~§8, `OPENROUTER-VALIDATION-0001.md`)가 아니라, 무료 티어가 공유하는 upstream provider capacity가 이 세션의 짧은 시간 동안의 반복 호출로 소진된 것이다 — 무료 모델을 Production에서 쓸 경우 이런 429/502가 정상적으로 발생할 수 있다는 것 자체가 중요한 Evidence다(§7 비용/latency 판단에 반영).

## 3. Stage별 실제 호출 결과

### 3.1 Stage 01 — Context 이해/정리 (Requirement Agent 실제 프롬프트 사용)

`hqs/development/stages/01_context_analysis/reasoning.py::requirement_agent`의
실제 instruction·필수 키(`functional_requirements`/`non_functional_requirements`/
`constraints`/`scope_candidates`/`confidence`)를 그대로 사용했고, 검증도
production 함수 `reasoning.py::parse_structured_output`을 그대로 import해
실행했다(재구현 없음). 입력 issue: "Add input validation to code review
agent"(아래 Stage 02~04와 동일 시나리오로 일관 유지).

| 모델 | HTTP | latency | JSON 파싱 | 필수 키 누락 | 내용 품질 |
|---|---|---|---|---|---|
| `google/gemma-4-31b-it:free` | 200 | 6.01s | PASS | 없음 | functional/non-functional/scope_candidates 명확, `confidence: 0.95` |
| `nvidia/nemotron-3-super-120b-a12b:free` | 200 | 18.72s | PASS | 없음 | 더 풍부(logging, thread-safety 등 non-functional 5개까지 확장) — 다만 Requirement Agent 역할(사실 추출)치고 다소 과확장된 범위 |

### 3.2 Stage 02 — Specification/요구사항 명세 (Task & Dependency Agent 실제 프롬프트 사용)

`hqs/development/stages/02_planning_specification/task_dependency_agent.py::decompose_tasks_and_dependencies`의
실제 `_INSTRUCTION`을 그대로 사용, 동일 production 파서로 검증. 입력
specification: "Implement input validation for backend_agent_code_review:
..."(Stage 01 issue의 자연스러운 후속).

| 모델 | HTTP | latency | JSON 파싱 | tasks/dependencies | 비고 |
|---|---|---|---|---|---|
| `nex-agi/nex-n2.5-pro:free`(1차, `max_tokens=1200`) | 200 | 20.84s | **FAIL(내용 없음)** | - | `reasoning`에만 1587 토큰 소비, `finish_reason: length` — 최종 답을 내지 못하고 예산 소진 |
| `nex-agi/nex-n2.5-pro:free`(2차, `max_tokens=3000`) | 200 | 16.33s | PASS | tasks 3개, dependencies 0개 | "발견되지 않은 의존성은 만들지 않는다"는 지시를 보수적으로 해석해 의존성을 전부 비움 |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`(`max_tokens=1200`) | 200 | 15.44s | PASS(1차 시도로 성공) | tasks 3개, dependencies 2개 | 테스트 Task가 구현 Task에, 문서화 Task가 구현 Task에 의존한다고 **실제로 유의미한 의존 관계**를 식별 — Task & Dependency Agent의 핵심 책임(Dependency 판단)을 더 잘 수행 |

### 3.3 Stage 03 — Architecture Design/Reasoning (Design Agent 실제 프롬프트 + 실제 Stage 03 Skeleton 사용)

`hqs/development/mvp/agents/design.py::design_agent_design`의 실제
instruction과, `stages/03_architecture_design/stage_03.py`의 실제
`_DESIGN_INSTRUCTION`(Architecture Definition/Component Identification/
Responsibility Allocation/Interface·Contract Identification/Data Flow/
Implementation Strategy 6개 항목 요구)을 그대로 포함한 Skeleton을 사용했다.

| 모델 | HTTP | latency | finish_reason | 6개 항목 커버리지 | 비고 |
|---|---|---|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free`(`max_tokens=1800`) | 200 | 65.62s | `stop`(자연 종료) | **6/6** | 표/코드블록/Risks & Mitigations까지 포함한 가장 완결된 설계 — 다만 latency가 가장 느림(전체 후보 중 최대) |
| `inclusionai/ling-3.0-flash-vl:free`(`max_tokens=1800`) | 200 | 12.40s | `length`(예산 소진) | 5/6(Implementation Strategy 직전에 잘림) | 품질은 준수하나 같은 예산에서 완결하지 못함 — `max_tokens`를 늘리면 완결 가능성 높음(별도 재검증 필요, 이 문서는 그 재검증을 수행하지 않음) |

### 3.4 Stage 04 — 실제 Code Generation + Stage 05 Validation 기준 적용

**대상**: `backend_agent_code_review`(`hqs/development/mvp/agents/backend.py`).
**프롬프트**: `workflow_ast_context.py::_EXPOSURE_POLICY_INSTRUCTION`을
그대로 사용 — "대상 함수 하나만 확장하고, 파일 전체 내용을 그대로
반환하라"는 실제 Exposure Policy. `backend_agent_code_generation`의 실제
instruction(`"Based on the following design..."`)도 그대로 사용.

**검증**: `stage_05.py`를 그대로 import해 `_check_structural`/
`_check_design_scope`/`_determine_verdict`를 실행(재구현 없음).
`test_execution`은 실제 대상 파일에 생성 코드를 임시로 적용한 뒤
전체 테스트 스위트(`hqs/development/mvp/tests/`, `pytest -q`)를 실행하고
즉시 원본으로 복원했다(baseline: 324 passed, 6 skipped, §4.3).

| 모델 | HTTP | latency | `structural` | `design_scope`(`changed_names`) | `test_execution` | Stage05 Verdict |
|---|---|---|---|---|---|---|
| `nex-agi/nex-n2.5-mini:free` | 200 | 5.78s | PASS | PASS(`[]`, 대상 함수만 변경) | PASS(`returncode=0`) | **PASS** |
| `nex-agi/nex-n2.5-pro:free` | 200 | 22.94s | PASS | PASS(`[]`, 대상 함수만 변경) | PASS(`returncode=0`) | **PASS** |
| `cohere/north-mini-code:free`(`max_tokens=1800`, 실제 full-file 프롬프트) | 200 | 23.78s | **평가 불가(content 없음)** | - | - | 실행 불가 |
| `cohere/north-mini-code:free`(`max_tokens=4000`, 재시도) | 200 | 49.36s | **평가 불가(content 없음)** | - | - | 실행 불가 — `reasoning` 16,796자 소비, `finish_reason: length`, 4000 토큰 전부 reasoning으로 소진, 최종 코드 미생성 |
| `poolside/laguna-s-2.1:free` / `laguna-xs-2.1:free` | 429 | - | - | - | - | §2 가용성 실패로 평가 불가 |

**두 PASS 후보의 실제 생성 코드 차이**: 사실상 동일(둘 다
`isinstance(code, str) and code.strip()` 검사 + `ValueError` + docstring
갱신, 다른 함수/import/공백 변경 없음) — 품질 차이가 없고 **latency만
4배 차이**(5.78s vs 22.94s)난다.

**`cohere/north-mini-code:free`에 대한 공정성 메모**: 이 모델은 "함수
본문만 반환하라"는 더 단순한 프롬프트(§1 최초 시도, 실제 Exposure
Policy 적용 전)에서는 7.93초 만에 정확한 코드를 냈다(§Appendix). 즉 이
모델 자체가 코드 생성 능력이 없는 것이 아니라, **실제 Stage 04가 쓰는
"전체 파일 반환" 스타일의 긴 프롬프트에서 reasoning 예산을 전부
소진하고 최종 코드를 내지 못하는 것**으로 판단한다 — 이는 실제 운영
조건(Exposure Policy)에서의 실패이므로 그대로 실패로 기록한다.

## 4. Instruction/Contract 준수, Context 처리, Reasoning, Syntax/테스트 통과 — 종합

| 기준 | Stage 01 | Stage 02 | Stage 03 | Stage 04 |
|---|---|---|---|---|
| Instruction/Contract 준수(JSON-only, 필수 키, 코드만 반환 등) | 두 후보 모두 PASS | 1순위 후보 1차 시도로 PASS, 2순위는 예산 증량 후 PASS | 두 후보 모두 형식 준수(표/헤더), 1순위만 6/6 완결 | 두 PASS 후보 모두 "코드만, 대상 함수만 수정" 완전 준수(`changed_names: []`) |
| Context 처리(주어진 issue/spec/skeleton을 실제로 반영) | 두 후보 모두 issue 내용을 정확히 반영 | 두 후보 모두 specification 내용을 정확히 tasks로 분해 | 두 후보 모두 Skeleton(Component/Scope/Constraints/Risks)을 실제로 인용·반영 | 두 후보 모두 대상 파일 전체를 실제로 읽고 그 안에서만 수정 |
| Reasoning(요구되지 않은 추론 필요 항목) | nemotron이 더 깊은 추론(위험 요소 확장)이나 범위 과확장 소지 | nemotron-nano만 실제 의존 관계를 추론(§3.2) — Task & Dependency Agent의 핵심 책임과 가장 부합 | nemotron-ultra가 Risk/Mitigation까지 자발적으로 추가(요구 이상 수행) | 해당 없음(결정적 검사로 대체) |
| Syntax/테스트 통과 | 해당 없음(JSON Contract) | 해당 없음(JSON Contract) | 해당 없음(prose) | 두 PASS 후보 모두 `ast.parse` 유효 + 전체 pytest suite 324 passed 유지 |
| latency | 6.0s / 18.7s | 15.4s(1차 성공) / 16.3s(2차 성공, 1차는 실패) | 12.4s(미완결) / 65.6s(완결) | 5.8s / 22.9s(둘 다 PASS) |
| 무료 사용 여부 | 둘 다 `cost:0`, `is_byok:false` | 둘 다 `cost:0`, `is_byok:false` | 둘 다 `cost:0`, `is_byok:false` | 둘 다 `cost:0`, `is_byok:false` |
| 실패 여부 | 없음 | 1순위 후보가 저예산(1200)에서 1회 실패(재시도로 해결) | 없음(둘 다 응답은 받음, 완결성 차이만 존재) | `cohere/north-mini-code:free` 완전 실패(§3.4), Poolside 두 모델 가용성 실패(§2) |

## 4.3 pytest baseline (test_execution 비교 기준)

```
$ pytest hqs/development/mvp/tests/ -q
324 passed, 6 skipped in 30.56s
```

이 baseline은 원본 `backend.py`(무변경) 기준이며, Stage 04 두 PASS 후보
적용 시에도 동일하게 324 passed(6 skipped 동일, 추가 실패 없음)를 확인했다.

## 4.4 Production 무변경 확인

```
$ git status --short
$ git diff --stat
(출력 없음 — Stage 04 검증 중 임시로 덮어썼던 backend.py가 매 회 원본으로
정확히 복원되었음을 확인)
```

## 5. 최종 비교표

| Stage | 후보 모델 | 결과 | 장점 | 단점 | 추천순위 |
|---|---|---|---|---|---|
| 01 | `google/gemma-4-31b-it:free` | PASS | 빠름(6.0s), 정확, Contract 완전 준수 | 세부 항목이 상대적으로 간결 | **1순위** |
| 01 | `nvidia/nemotron-3-super-120b-a12b:free` | PASS | 더 풍부한 non-functional requirement 도출 | 3배 느림(18.7s), Requirement Agent 범위를 다소 넘는 확장 | 2순위 |
| 02 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | PASS | 저예산(1200)에서 1차 성공, **실제 의존 관계를 정확히 식별**(핵심 책임 부합) | 없음(이번 시나리오 기준) | **1순위** |
| 02 | `nex-agi/nex-n2.5-pro:free` | PASS(2차 시도) | 최종 결과는 정확 | 저예산에서 reasoning 소진으로 1차 실패, 의존성을 과도하게 보수적으로(전부 없음) 판단 | 2순위 |
| 03 | `nvidia/nemotron-3-ultra-550b-a55b:free` | PASS | 요구 6개 항목 전부 자연 완결(`stop`), Risk/Mitigation까지 자발적 포함 | 65.6s로 후보 중 최대 latency | **1순위** |
| 03 | `inclusionai/ling-3.0-flash-vl:free` | PARTIAL | 5배 빠름(12.4s), 품질 자체는 우수 | 동일 예산에서 6번째 항목 직전 잘림(예산 증량 필요, 이 문서는 재검증 안 함) | 2순위 |
| 04 | `nex-agi/nex-n2.5-mini:free` | PASS(Stage05 전체 기준 PASS) | 가장 빠름(5.8s), structural/design_scope/test_execution 전부 PASS, pytest 324 passed 유지 | 없음(이번 시나리오 기준) | **1순위** |
| 04 | `nex-agi/nex-n2.5-pro:free` | PASS(Stage05 전체 기준 PASS) | mini와 동일 품질의 코드 | mini 대비 4배 느림(22.9s), 품질 이득 없음 | 2순위 |
| 04 | `cohere/north-mini-code:free` | FAIL | 단순 요청에서는 빠르고 정확(§3.4 Appendix) | 실제 Exposure Policy(전체 파일) 프롬프트에서 4000 토큰까지도 reasoning만 소비하고 코드 미생성 — 이번 시나리오 기준 사용 불가 | 순위 없음(실패) |
| 04 | `poolside/laguna-s-2.1:free`, `laguna-xs-2.1:free` | 가용성 실패 | "coding agent" 전용 모델로 설계 목적은 적합해 보임 | 이 세션 테스트 기간 동안 upstream 429로 전혀 호출 불가 — 품질 평가 자체가 불가능 | 순위 없음(가용성 실패) |

## 6. 후보 Model Mapping (최종)

```
Stage 01 → google/gemma-4-31b-it:free
Stage 02 → nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
Stage 03 → nvidia/nemotron-3-ultra-550b-a55b:free
Stage 04 → nex-agi/nex-n2.5-mini:free
```

네 Stage 모두 각 1순위 후보에 대해 실제 호출 성공 + 해당 Contract/Validation
기준 PASS Evidence가 존재하므로 `NOT DETERMINED`로 표시할 항목은 없다.
다만 다음은 이 문서의 범위 밖으로 명시적으로 남긴다(과장 방지):

- Stage 03 2순위(`inclusionai/ling-3.0-flash-vl:free`)가 더 큰 `max_tokens`
  에서 6/6 항목을 완결하는지는 **재검증하지 않았다**(Not Determined로
  유지, §3.3).
- 각 Stage 1개 사례만 테스트했다 — 반복 재현(동일 모델 재호출 시 결과
  일관성)은 검증하지 않았다(단일 시도 Evidence, `OPENROUTER-VALIDATION-0001.md`
  §6의 "재현 가능성" 논의와 별개 축).
- `poolside/laguna-*` 두 모델과 `cohere/north-mini-code:free`는 §2/§3.4의
  실패 원인이 실제로는 일시적(재시도 시 해소)인지, 구조적(계속 실패)인지
  추가로 반복 검증하지 않았다.

## 7. Architecture/Governance 경계 재확인

이 문서는 모델 "적합성 선별"만 수행했다 — Production 코드에 이 결과를
반영하는 것(Stage 01~04 Engine 호출부를 OpenRouter로 전환하는 것)은
`OPENROUTER-VALIDATION-0001.md` §7이 이미 정리한 대로 `ADR-0024`의 2-Engine
Stage Mapping·Option C(Central Router 배제) 결정과 충돌하며, RFC 없이
진행할 수 없다 — 이 문서도 그 결론을 바꾸지 않는다. Production 코드,
Architecture/Contract/Governance 문서는 이 작업에서 변경하지 않았다 —
변경 범위는 이 신규 문서 1개로 제한된다.

---

## Appendix — `cohere/north-mini-code:free` 최초(단순) 프롬프트 시도 (공정성 참고용)

실제 Exposure Policy 프롬프트 적용 전, "대상 함수 본문만 반환하라"는
더 단순한 요청(`hqs/development/mvp/ast_context.py::_first_doc_line` 대상)
에서는 다음과 같이 빠르고 정확하게 응답했다(§3.4 실패와의 대조를 위해
그대로 보존):

```
model=cohere/north-mini-code:free status=200 elapsed=7.925s
content:
def _first_doc_line(node) -> str:
    doc = ast.get_docstring(node, clean=True)
    if doc is None:
        return ""
    return doc.strip().split('\n')[0]
```

이 결과는 §5 최종 순위 산정에는 반영하지 않았다(실제 Stage 04 프롬프트
스타일이 아니므로) — 참고 목적으로만 남긴다.
