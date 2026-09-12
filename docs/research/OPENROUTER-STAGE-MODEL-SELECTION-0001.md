# OpenRouter Stage 01~04 무료 모델 적합성 선별 — Evidence 0001

## Summary

- **[Session 3 갱신] Stage 01 대체 후보(`nvidia/nemotron-3-super-120b-a12b:free`)
  검증 결과(§9) — 3/3 반복 성공(100%), Contract 3/3 PASS, upstream
  오류 0건. `google/gemma-4-31b-it:free`(§8.1, 성공률 33%)와 비교해
  가용성이 압도적으로 우수해 **Stage 01 최종 Production 후보로
  `nvidia/nemotron-3-super-120b-a12b:free`를 선정**한다(§9.5). 상세는
  §9 참조.**
- **[Session 2 갱신] 반복 재현성 Validation 결과(§8) — Stage 02/03/04는
  3/3 반복 성공 + 매번 동일한 Contract/Validation PASS로 재현성 확인
  (PASS). Stage 01(`google/gemma-4-31b-it:free`)은 응답 품질 자체는
  2/2 성공 시도 모두 동일하게 PASS했지만, 6회 시도 중 4회가 upstream
  provider(Google AI Studio) shared pool 429로 실패해 **호출
  가용성이 33%(2/6)에 불과했다** — 품질 재현성은 확인됐으나 가용성
  재현성이 불충분해 **PARTIAL**로 판정한다(NOT DETERMINED는 아님 —
  성공한 2회의 데이터 자체는 존재하고 일관됨). 최종 Model Mapping은
  §8.6 참조.**
- (이하는 §8 이전, 최초 선별 세션의 원래 Summary — 그대로 보존)
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

---

## 8. Session 2 — 반복 재현성 Validation

**목적**: §1~§7(Session 1)이 각 Stage 1회 시도만으로 내린 1순위 판단이
우연이 아니었는지, 선정된 4개 모델(Stage 01~04 각 1순위)을 동일 조건으로
**최소 3회** 반복 호출해 확인한다. §1~§7의 판단을 뒤집을 근거가 나오면
그대로 반영한다.

**대상**(Session 1 §6 최종 1순위 그대로):

```
Stage 01 → google/gemma-4-31b-it:free
Stage 02 → nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
Stage 03 → nvidia/nemotron-3-ultra-550b-a55b:free
Stage 04 → nex-agi/nex-n2.5-mini:free
```

**방법**: Session 1과 완전히 동일한 프롬프트 파일(`stage01_prompt.txt`~
`stage04_prompt.txt`, `call_or.py`, `stage04_harness.py`)을 그대로
재사용했다 — 입력·Contract·검증 로직을 Session 1과 다르게 만들지 않았다.
매 시도의 `cost`/`is_byok`를 확인해 무료 호출임을 재확인했다(§8.5).

### 8.1 Stage 01 — `google/gemma-4-31b-it:free` (3회 시도 목표, 실제 6회 시도)

| 시도 | 결과 | HTTP | latency | Contract(`parse_structured_output` 실제 함수로 검증) | 원인 구분 |
|---|---|---|---|---|---|
| 1 | 성공 | 200 | 6.19s | PASS(필수 키 5개 전부 존재) | - |
| 2(최초) | 실패 | 429 | 0.24s | - | `upstream_provider_shared_pool`(Google AI Studio) — rate limit, 모델 결함 아님 |
| 2(재시도 1, +20s 대기) | 실패 | 429 | 1.41s | - | 위와 동일 |
| 2(재시도 2, +30s 대기) | 실패 | 429 | 0.58s | - | 위와 동일 |
| 2(재시도 3, +45s 대기) | 실패 | 429 | 0.73s | - | 위와 동일 |
| 2(재시도 4, +90s 대기) | 실패 | 429 | 0.60s | - | 위와 동일(누적 대기 약 3분, 계속 동일 원인) |
| 3 | 성공 | 200 | 5.82s | PASS(필수 키 5개 전부 존재) | - |

**요약**: 실제로 응답을 받은 2회(원래 1·3번째 시도)는 **둘 다 Contract를
완전히 준수**했고 내용도 Session 1과 동일한 수준이었다(functional/
non-functional/scope_candidates 명확). 그러나 같은 5분 남짓한 시간
동안 같은 모델에 대한 **호출 자체의 성공률이 2/6 = 33%**였다 — 이는
Session 1 §2가 이미 관찰한 "google/gemma-4-31b-it:free 1회 429" 패턴이
우연한 1회성이 아니라 **이 모델(Google AI Studio 무료 공유 pool)의
반복되는 특성**임을 이번 재검증이 확정했다는 뜻이다. `raw` 메시지가
매번 정확히 "temporarily rate-limited upstream ... upstream_provider_shared_pool"
로 동일해 **rate limit이지 모델 자체 결함(품질 저하, 응답 변질)이
아님**을 명확히 구분할 수 있었다.

### 8.2 Stage 02 — `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` (3/3 성공, 1회 재시도 포함)

| 시도 | 결과 | HTTP | latency | Contract | tasks/dependencies |
|---|---|---|---|---|---|
| 1(최초) | 실패 | 502 | 0.36s | - | `Upstream error from Nvidia: ResourceExhausted: Worker local total request limit reached (16/16)` — provider capacity, 모델 결함 아님 |
| 1(재시도, +10s) | 성공 | 200 | 20.90s | PASS | tasks=3, dependencies=2 |
| 2 | 성공 | 200 | 17.56s | PASS | tasks=3, dependencies=2 |
| 3 | 성공 | 200 | 13.83s | PASS | tasks=3, dependencies=2 |

**요약**: 성공한 3회 전부 **tasks 3개·dependencies 2개로 완전히 동일한
구조**를 산출했다 — Session 1의 "테스트/문서화 Task가 구현 Task에
의존한다"는 판단이 우연이 아니라 **일관된 reasoning 패턴**임을
확인했다. 1회의 502는 Stage 04 Session 1에서도 관찰된 것과 동일한
Nvidia provider capacity 문제로, 10초 재시도로 즉시 해소됐다(Google
AI Studio 사례와 달리 지속되지 않음).

### 8.3 Stage 03 — `nvidia/nemotron-3-ultra-550b-a55b:free` (3/3 성공, 1차 시도로 전부 성공)

| 시도 | 결과 | HTTP | latency | finish_reason | 6개 항목 커버리지 |
|---|---|---|---|---|---|
| 1 | 성공 | 200 | 33.90s | `stop` | 6/6 |
| 2 | 성공 | 200 | 52.93s | `stop` | 6/6 |
| 3 | 성공 | 200 | 71.70s | `stop` | 6/6 |

**요약**: 3회 전부 자연 종료(`stop`)로 6개 필수 항목을 전부 포함했다 —
Session 1의 "완결성" 결과가 재현됐다. 다만 **latency가 33.9s → 52.9s →
71.7s로 시도마다 뚜렷이 증가**했다 — 이 세션 내에서 시간이 지날수록
느려지는 추세가 관찰됐다(원인은 이 문서가 규명하지 않음 — provider
부하 증가 추정, 반복 관찰 필요). Session 1의 65.6s 단일 관측치가
"이 모델 특유의 높은 latency"라는 판단 자체는 재확인됐고, 오히려
변동폭이 더 크다는 사실이 추가로 드러났다.

### 8.4 Stage 04 — `nex-agi/nex-n2.5-mini:free` (3/3 성공, Stage 05 실제 검증 3회 전부 PASS)

동일한 실제 대상(`backend_agent_code_review`)·동일한 Exposure Policy
프롬프트·동일한 `stage_05.py` 실제 검증 함수(재구현 없음, import 그대로
실행)를 사용했다. 매 회 검증 후 `backend.py`를 즉시 원본으로 복원했다.

| 시도 | 결과 | HTTP | latency | `structural` | `design_scope` | `test_execution`(pytest) | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 성공 | 200 | 7.61s | PASS | PASS(`changed_names: []`) | PASS(`returncode=0`) | **PASS** |
| 2 | 성공 | 200 | 10.67s | PASS | PASS(`changed_names: []`) | PASS(`returncode=0`) | **PASS** |
| 3 | 성공 | 200 | 8.65s | PASS | PASS(`changed_names: []`) | PASS(`returncode=0`) | **PASS** |

**요약**: 3회 전부 Session 1과 동일하게 **대상 함수만 정확히 수정**했고,
매번 전체 pytest suite가 그대로 통과했다(324 passed, 6 skipped 유지,
추가 실패 없음). Session 1의 PASS가 우연이 아니라 **일관된 정확한
동작**임을 확인했다 — 4개 Stage 중 가장 확실하게 재현된 결과다.

### 8.5 무료 호출 확인 (전체 재검증 대상)

성공한 모든 호출(Stage 01 2건, Stage 02 3건 + 재시도 1건, Stage 03 3건,
Stage 04 3건)에서 `usage.cost`를 확인한 결과 전부 `0`, `usage.is_byok`
전부 `false`였다 — 이번 반복 검증도 예외 없이 순수 무료 티어 호출이었다.

### 8.6 종합 — Stage별 재현성 판단

| Stage | 모델 | 반복 성공률(응답 성공/시도) | 평균/범위 latency(성공한 호출만) | Validation 통과율(성공한 호출 중) | 재현성 판단 |
|---|---|---|---|---|---|
| 01 | `google/gemma-4-31b-it:free` | 2/6 = 33%(동일 원인의 429 반복) | 평균 6.00s, 범위 5.82~6.19s | 2/2 = 100% | **PARTIAL** — 응답 품질은 완전히 재현되나 호출 가용성 자체가 낮고 반복적으로 실패 |
| 02 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 3/4 = 75%(1회 502는 provider 일시 문제, 즉시 재시도로 해소) | 평균 17.43s, 범위 13.83~20.90s | 3/3 = 100% | **PASS** — 성공 시 결과 구조(tasks=3, deps=2)까지 완전히 동일 |
| 03 | `nvidia/nemotron-3-ultra-550b-a55b:free` | 3/3 = 100% | 평균 52.85s, 범위 33.90~71.70s(변동폭 큼) | 3/3 = 100% | **PASS** — 내용 재현성은 확실하나 latency 변동성은 운영 시 고려 필요 |
| 04 | `nex-agi/nex-n2.5-mini:free` | 3/3 = 100% | 평균 8.98s, 범위 7.61~10.67s | 3/3 = 100%(Stage05 Verdict 전부 PASS) | **PASS** — 가장 안정적, latency도 가장 짧고 변동 적음 |

### 8.7 Session 1과의 충돌 여부 분석

- Stage 02/03/04는 Session 1의 1회 PASS 결과와 **충돌 없음** — 오히려
  반복으로 더 강하게 뒷받침됐다.
- Stage 01만 잠재적 충돌 소지가 있다 — Session 1은 1회 성공만 관찰해
  "빠르고 정확"으로 1순위 판정했지만(§Stage별 실제 호출 결과 §3.1),
  이번 §8.1이 **같은 모델의 반복 가용성 문제**를 추가로 드러냈다. 이는
  Session 1의 판단이 "틀렸다"는 뜻이 아니라(성공했을 때의 품질 판단은
  그대로 유효), **Session 1이 관찰하지 못했던 새로운 차원(가용성)의
  Evidence가 이번에 추가된 것**이다 — 정직하게 원인을 분석하면 Google AI
  Studio 무료 공유 pool 자체의 용량 문제이지, `google/gemma-4-31b-it`
  모델의 추론 품질 문제가 아니다.

### 8.8 최종 Model Mapping (Session 2, 재현성 검증 반영)

```
Stage 01 → google/gemma-4-31b-it:free   (PARTIAL — 응답 시 품질은 재현되나 가용성 33%, §8.1 참조)
Stage 02 → nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free   (PASS)
Stage 03 → nvidia/nemotron-3-ultra-550b-a55b:free   (PASS, latency 변동성 큼)
Stage 04 → nex-agi/nex-n2.5-mini:free   (PASS, 가장 안정적)
```

Stage 01은 `NOT DETERMINED`로 표시하지 않는다 — 성공한 2회의 실제
Evidence가 존재하고 서로 완전히 일치하기 때문이다. 다만 **PARTIAL**로
명확히 구분해, Production 전환을 실제로 검토하는 단계(RFC 이후)에서는
Stage 01에 한해 ① 같은 모델을 유지하되 재시도/대체 provider 전략을
같이 설계하거나, ② 대체 후보(Session 1 §5의 2순위
`nvidia/nemotron-3-super-120b-a12b:free`)의 반복 재현성도 별도로
검증할 것을 권고한다 — 이 권고 자체는 Governance 판단이 아니라 다음
검증 세션을 위한 메모이며, 이 문서가 RFC를 대신하지 않는다(§7 경계
재확인, 무변경).

### 8.9 Production/Architecture/Governance 영향 및 변경 범위

- Stage 04 검증 3회 동안 `hqs/development/mvp/agents/backend.py`를 임시로
  덮어썼으나 매 회 즉시 원본으로 복원했고, 이 섹션 작성 시점 기준
  `git status --short`/`git diff --stat` 모두 출력 없음(무변경)을
  확인했다.
- API Key/Credential 값은 이번 재검증에서도 어디에도 출력·저장하지
  않았다(§8.5는 `cost`/`is_byok` boolean만 기록).
- Production 코드, Architecture/Contract/Governance 문서는 이 재검증에서
  변경하지 않았다. 변경 범위는 이 문서(기존 파일 수정, §8 추가)로
  제한된다.
- §7(Architecture/Governance 경계, ADR-0024와의 충돌·RFC 필요성)의
  결론은 이 §8로 번복되지 않는다.

---

## 9. Session 3 — Stage 01 대체 후보 검증 및 최종 선정(`nvidia/nemotron-3-super-120b-a12b:free`)

**목적**: §8.1이 확인한 `google/gemma-4-31b-it:free`의 낮은 가용성
(2/6 = 33%)을 근거로, Session 1 §5의 Stage 01 2순위 후보
`nvidia/nemotron-3-super-120b-a12b:free`를 **동일 prompt/입력/Contract**로
3회 반복 검증해 Stage 01 Production 후보를 최종 선정한다.

**방법**: §1~§8과 완전히 동일한 `stage01_prompt.txt`(Requirement Agent
실제 instruction, issue: "Add input validation to code review agent")와
production 검증 함수(`reasoning.py::parse_structured_output`,
`REQUIREMENT_REQUIRED_KEYS`)를 그대로 재사용했다 — 새 입력이나 새 검증
로직을 만들지 않았다.

### 9.1 3회 시도 결과

| 시도 | 결과 | HTTP | latency | Contract | FR/NFR 개수 | confidence | upstream 오류 |
|---|---|---|---|---|---|---|---|
| 1 | 성공 | 200 | 28.73s | PASS(필수 키 5개 전부) | FR 4 / NFR 4 | 0.92 | 없음 |
| 2 | 성공 | 200 | 10.08s | PASS(필수 키 5개 전부) | FR 4 / NFR 5 | 0.92 | 없음 |
| 3 | 성공 | 200 | 7.69s | PASS(필수 키 5개 전부) | FR 5 / NFR 5 | 0.92 | 없음 |

3회 모두 **1차 시도로 즉시 성공**했다 — 재시도가 필요했던 경우가 한
번도 없었고, 429/502 등 upstream capacity 오류도 전혀 관찰되지
않았다(§9.4에서 Gemma의 반복적 429와 명시적으로 대조).

### 9.2 성공률

**3/3 = 100%**(3회 호출, 3회 전부 응답 성공). §8.1의
`google/gemma-4-31b-it:free` 2/6 = 33%(같은 5분 내외 시간대, 동일 재시도
전략)와 직접 대조된다.

### 9.3 평균/범위 latency

- 평균: **15.50s**((28.73+10.08+7.69)/3)
- 범위: **7.69s ~ 28.73s**
- 1차 시도가 가장 느리고(28.73s) 이후 점점 빨라지는 경향(10.08s →
  7.69s)이 관찰됐다 — Session 1의 단일 관측치(18.72s)도 이 범위 안에
  있다. Gemma(평균 6.00s, 범위 5.82~6.19s)보다 **평균 약 2.6배 느리고
  변동폭도 크다** — 순수 latency만 보면 Gemma가 우수하다.

### 9.4 품질/Contract 결과

- 3회 전부 `reasoning.py::parse_structured_output`(재구현 없이 실제
  production 함수 그대로 사용) 검증을 통과했고, 필수 키
  (`functional_requirements`/`non_functional_requirements`/
  `constraints`/`scope_candidates`/`confidence`) 5개가 매번 전부
  존재했다 — **Contract 준수율 3/3 = 100%**.
- `confidence`가 3회 모두 정확히 `0.92`로 동일 — 응답의 안정성을
  보여주는 부가 신호.
- 내용 품질은 Session 1 §3.1 관찰과 일치 — functional/non-functional
  requirement를 상세히 도출하지만, "latency ≤10ms", "localization",
  "high test coverage" 등 원 issue 설명에 명시되지 않은 항목까지
  추가로 만들어내는 **확장 경향(과확장 소지)** 이 3회 모두
  재확인됐다. 이는 Contract 위반은 아니며(요구된 키 구조를 준수하는
  한 내용의 상세도는 Agent 자유도 범위), 오히려 Requirement Agent가
  더 폭넓게 위험/비기능 요구를 짚어내는 것으로 볼 수도 있다 — 이
  문서는 "장점"과 "단점" 어느 한쪽으로 단정하지 않고 있는 그대로
  기록한다(§9.6 표에도 반영).

### 9.5 upstream 오류 여부

**없음.** 3회 전부 HTTP 200으로 즉시 응답했고, `429`(rate limit)나
`502`(provider capacity) 등 upstream 오류가 한 번도 발생하지 않았다.
이는 §8.1에서 Google AI Studio가 같은 세션 시간대에 반복적으로 429를
반환한 것과 명확히 대조된다 — Nvidia 계열 provider(이 모델의 upstream)
가 이번 검증 시간대에는 더 넉넉한 여유 capacity를 갖고 있었던 것으로
판단한다(다른 시간대에도 동일한지는 이 문서가 보장하지 않는다, §9.7).

### 9.6 Gemma 4 31B 대비 비교

| 기준 | `google/gemma-4-31b-it:free`(§8.1) | `nvidia/nemotron-3-super-120b-a12b:free`(§9.1~9.5) |
|---|---|---|
| 성공률(응답 성공/시도) | 2/6 = 33% | **3/3 = 100%** |
| 평균 latency(성공 호출만) | **6.00s**(빠름) | 15.50s(약 2.6배 느림) |
| latency 범위 | 5.82~6.19s(안정적) | 7.69~28.73s(변동폭 큼) |
| Contract 준수(성공 호출 중) | 2/2 = 100% | 3/3 = 100% |
| upstream 오류 | 429 4회(같은 시간대 반복, 최대 3분 대기에도 지속) | 0회 |
| 무료 사용 여부 | `cost:0`/`is_byok:false`(성공 2건 확인) | `cost:0`/`is_byok:false`(3건 전부 확인) |
| 응답 내용 특성 | 간결, 요구된 범위에 근접 | 더 상세하나 과확장 소지(§9.4) |

**핵심 Trade-off**: Gemma는 "성공하면" 더 빠르고 간결하지만 **3번 중 2번은
아예 응답을 받지 못했다**. Nemotron Super는 매번 응답은 받지만 느리고
변동폭이 크다. Stage 01은 Stage 02~05로 이어지는 파이프라인의 첫
단계이므로, **호출 자체가 실패하면 이후 Stage 전체가 진행되지 못한다**
— 이 파이프라인 특성상 "빠르지만 3번에 2번 막히는 모델"보다 "느리지만
매번 응답하는 모델"이 구조적으로 더 안전하다.

### 9.7 Stage 01 최종 추천

**`nvidia/nemotron-3-super-120b-a12b:free`를 Stage 01 Production 후보로
최종 추천한다.** 근거:

1. 이번 3회 전부 100% 성공, upstream 오류 0건 — §9.1~9.5의 직접 Evidence.
2. Session 1(§3.1, 1회 성공)까지 합산하면 이 모델은 **이 대화 전체에서
   4/4 = 100% 성공**, upstream 오류 관측 0건이다.
3. Gemma는 이 대화 전체에서 **3/7 ≈ 43% 성공**(Session 1 1/1, Session 2
   §8.1 2/6)이며, 실패 원인이 매번 동일(`upstream_provider_shared_pool`)
   해 **일회성이 아니라 반복되는 패턴**으로 판단된다(§8.7에서 이미
   지적).
4. Contract 준수는 두 모델 모두 응답이 성공했을 때는 100%로 동일 —
   즉 품질 차이가 아니라 **가용성 차이**가 결정적 구분 기준이다.

**NOT DETERMINED로 판단하지 않는 이유**: Nemotron Super는 3/3 100%
성공 + upstream 오류 0건이라는 충분한 Evidence를 확보했다 — 가용성이
불충분한 쪽은 오히려 Gemma다. 두 모델을 직접 비교할 근거가 이미
확보되어 있으므로 "판단 불가" 상태가 아니다.

**남기는 한계**: 이번 검증도 특정 시간대(이 세션의 실행 시점) 1회
관측이며, §8.1의 Gemma 실패도 같은 시간대 관측이다 — 두 모델의
가용성이 항상 이 비율로 유지된다고 일반화하지 않는다. 다만 Gemma는
Session 1과 Session 2 두 개의 서로 다른 시점에서 모두 실패 패턴이
나타났고, Nemotron Super는 Session 1과 Session 3 두 시점 모두
100% 성공했다는 점에서 **단일 관측보다는 근거가 두텁다**.

### 9.8 Production 전환 여부

**Stage 01 모델 선정 자체는 이 문서로 확정하지만, 이것이 Stage 01의
실제 Engine 호출부를 OpenRouter로 전환해도 된다는 뜻은 아니다.**
`OPENROUTER-VALIDATION-0001.md` §7 및 이 문서 §7이 이미 정리한 대로:

- `ADR-0024`의 2-Engine(ChatGPT/Claude Code) Stage Mapping과 Option
  C(Central Router 배제) 결정은 이 검증으로 바뀌지 않는다.
- OpenRouter를 Stage 01(또는 다른 Stage)의 실제 Engine 호출 경로로
  쓰려면 여전히 RFC → ADC → ADR 절차가 필요하다.
- 이 문서(§1~§9 전체)는 "OpenRouter 무료 모델 중 Stage 01에 가장 적합한
  것은 무엇인가"라는 **후보 선정 질문에만** 답한다 — "Stage 01을
  OpenRouter로 전환해도 되는가"라는 Governance 질문에는 답하지 않는다.

**Production 코드/Architecture/Contract/Governance는 이번 검증에서도
변경하지 않았다.** 변경 범위는 이 문서(기존 파일 수정, §9 추가) 1건으로
제한된다 — `git status --short`/`git diff --stat` 확인 결과 코드 변경
없음(이번 검증은 API 호출·응답 검증만 수행해 대상 코드 적용 자체가
없었음).

### 9.9 최종 Model Mapping (Session 3 반영)

```
Stage 01 → nvidia/nemotron-3-super-120b-a12b:free   (PASS, 3/3 성공, Gemma 대비 가용성 우수 — Session 2의 PARTIAL을 대체)
Stage 02 → nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free   (§8, PASS)
Stage 03 → nvidia/nemotron-3-ultra-550b-a55b:free   (§8, PASS, latency 변동성 큼)
Stage 04 → nex-agi/nex-n2.5-mini:free   (§8, PASS, 가장 안정적)
```
