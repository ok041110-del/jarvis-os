# OpenRouter Free Model Selection Architecture — Production Migration Evidence

## Summary

- 목표: `ADR-0026`이 확정한 8단계 경로를 Stage 01~05 **Production
  코드**에 실제로 Migration한다(사용자 지시).
- Migration 대상(Stage 01~05의 실제 LLM 호출 지점) 조사는 완료했다
  (§1) — 읽기 전용, Production 코드 무변경.
- **Migration 자체는 수행하지 않고 STOP했다.** 이유: OpenRouter를
  Stage 실행 내부의 LLM Engine으로 실제 편입시키는 것은 현재
  `hqs/development/IMPLEMENTATION_RULES.md`가 명시한 "3번째 Engine
  추가는 별도 RFC → ADC → ADR 대상"이라는 규칙에 해당하며, `ADR-0026`
  §10 자신이 "Production Routing Integration Decision Status:
  **NOT YET DETERMINED**"라고 명시한 바로 그 결정이 아직 내려지지
  않았다(§4).
- 이 작업의 지시(`RFC-0040`/`ADC-0043`/`ADR-0026` 수정 금지 + Production
  Migration 수행)는 서로 충돌한다 — 이 세 문서를 건드리지 않고서는
  "Production Routing Integration"을 NOT YET DETERMINED에서 실제
  채택으로 바꿀 방법이 Governance 상 존재하지 않는다. 이 문서는 이
  충돌을 사용자 지시 10번("Architecture 변경이 필요하다고 판단되는
  경우 임의 수정하지 말고 STOP + Evidence로 보고한다")에 따라 그대로
  보고한다.
- **최종 판정: D. Architecture change required**(코드 변경이 아니라
  Governance 결정 변경이 필요 — 새 RFC → ADC → ADR로 "Production
  Routing Integration"을 NOT YET DETERMINED에서 명시적으로 재판정
  해야 함).
- Production `hqs/` 코드는 이 작업 전체에서 **한 바이트도 변경되지
  않았다**(§15 `git diff` 확인).

---

## 1. Migration 대상 조사(읽기 전용)

### 공통 — Multi-Engine 모듈(ADR-0024)

- `hqs/development/mvp/engine.py::call_engine(prompt: str) -> str` —
  "Claude Code Engine"(Implementation/Execution). `subprocess.run
  ([ENGINE_CLI, "-p", prompt, ...])`, 실패 시 단일 `RuntimeError`.
- `hqs/development/mvp/chatgpt_engine.py::call_engine_via_chatgpt
  (prompt: str) -> str` — "ChatGPT Engine"(Reasoning/Review).
  `CHATGPT_DEFAULT_MODEL = "gpt-4o"`(env `CHATGPT_MODEL`로 override
  가능), 실패 시 단일 `RuntimeError`.
- `hqs/development/mvp/omniroute_engine.py::call_engine_via_omniroute`
  — 존재하나 **어떤 Stage/Agent 호출부도 import하지 않음**(독립
  모듈, 미사용 확인).

### Stage 01 — Context Analysis

- LLM 호출: `stages/01_context_analysis/reasoning.py:15`
  (`from mvp.chatgpt_engine import call_engine_via_chatgpt as
  call_engine`), 호출: `reasoning.py:62`.
- 모델 선택: 정적 import(하드코딩된 특정 모델명은 없음 — Engine
  모듈이 자체적으로 `gpt-4o`를 기본값으로 가짐, Stage 코드는 모델명을
  모른다).
- Requirement: 4개 독립 reasoning agent(intent/goal/requirement/
  ambiguity), 각각 지정된 키를 가진 JSON 응답 요구.
- Input/Output Contract: `parse_structured_output()`(정규식 JSON
  추출 + `json.loads`) + 필수 키 존재 검사(`reasoning.py:64-66`).
- 기존 parser: `parse_structured_output`(이미 실험 harness
  `contracts.py`가 읽기 전용 재사용 중).
- Retry/failure: `AgentOutputError(ValueError)` — 명시적으로 "재시도
  대상 아님" 주석. 재시도 판단은 `mvp/parallel_runner.py`(상위
  레이어)에서.
- 기존 테스트: `mvp/tests/test_stage01_reasoning.py` 외 5개 파일.

### Stage 02 — Planning/Specification

- LLM 호출: `stages/02_planning_specification/task_dependency_agent.py:14`,
  호출: 44행.
- 모델 선택: Stage 01과 동일 패턴(정적 ChatGPT Engine import).
- Requirement: PRD/spec → `tasks` + `dependencies` JSON 분해.
- Contract: 동일 `parse_structured_output` 재사용, 세부 스키마
  검증은 `planning_pipeline.py`(Deterministic Layer)로 위임.
- Retry/failure: `AgentOutputError`만, 로컬 재시도 없음.
- 기존 테스트: `mvp/tests/test_task_dependency_agent.py` 등 3개.

### Stage 03 — Architecture Design

- LLM 호출: `stage_03.py`는 직접 Engine을 import하지 않고
  `mvp.agents.design_agent_design`(`mvp/agents/design.py:4,15`,
  ChatGPT Engine 정적 import)을 호출.
- Requirement: Architecture Definition/Component Identification/
  Responsibility Allocation/Interface Contract/Data Flow/
  Implementation Strategy를 포함하는 prose(`stage_03.py:12-20`).
- Contract: 구조적 파서 없음 — free prose. 실패만
  `_engine_failure_message`/`is_engine_failure`(`mvp/workflow.py`)로
  감지.
- Retry/failure: `try/except Exception` → 실패 시 sentinel 문자열로
  치환, re-raise 없음. 재시도 없음.
- 기존 테스트: `mvp/tests/test_stage_03.py`.

### Stage 04 — Implementation

- LLM 호출: `stage_04.py`는 직접 Engine 미import,
  `mvp.agents.backend_agent_code_generation`(`mvp/agents/backend.py:16,61`,
  **Claude Code Engine** 정적 import — Stage 01~03/05와 다른
  Engine)을 호출.
- Requirement: AST-closure/exposure-policy 기반 build input →
  "코드만 반환" 지시, `_strip_code_fence`로 fence 제거.
- Contract: JSON 스키마 없음 — raw code text. `EXPOSURE_POLICY_
  CONFLICT: <reason>` sentinel 라인만 구조적으로 확인(Stage 05가
  파싱).
- Retry/failure: `try/except` → `_engine_failure_message`로 치환,
  재시도 없음.
- 기존 테스트: `mvp/tests/test_stage_04.py`(9개) 외.

### Stage 05 — Validation

- LLM 호출: `stage_05.py`는 직접 Engine 미import,
  `mvp.agents.backend_agent_code_review`(`mvp/agents/backend.py:15,42`,
  **ChatGPT Engine** 정적 import)를 호출.
- (QA capability `qa_agent_test_execution`은 `mvp/agents/qa.py`에
  존재하나 Production Stage 05는 이를 호출하지 않음 — 대신 결정적
  `pytest` subprocess 실행을 씀.)
- Requirement: prose code review, `NO_ISSUES_FOUND` 정확 일치 marker.
- Contract: 구조적 파싱 없음(자유 텍스트) — Stage 05의 실제 Output
  Contract 집행은 `contracts.py`(`validate_verification_requirement`,
  `KNOWN_CHECK_NAMES`)가 담당, Review 자체는 pass-through.
- Retry/failure: `is_engine_failure(implementation)` 게이트(Stage 04
  결과가 이미 실패 sentinel이면 Review 자체를 건너뜀) + `try/except`
  → sentinel 치환. 재시도 없음.
- 기존 테스트: `mvp/tests/test_stage_05.py`(37개 함수).

### OpenRouter 참조 현황

`grep -rniE "openrouter" hqs/development/`(전체, `__pycache__` 제외)
— **0건**. Production 코드/문서/테스트 어디에도 OpenRouter 참조가
없다(이번 작업 이전부터 계속).

## 2. Before Architecture(현재 Production)

```
Stage 01/02 ─┐
Stage 03/05 ─┼─(정적 import)─→ chatgpt_engine.call_engine_via_chatgpt ─→ str
Stage 04    ─┘─(정적 import)─→ engine.call_engine(Claude Code)       ─→ str
```

`ADR-0024` Option C(2-Engine, 파일 단위 정적 import, 런타임 분기
없음)가 그대로 Production에서 동작 중이다. 어느 Stage도 모델명을
알지 못한다 — Engine 모듈이 각자 모델을 내부적으로 고정한다.

## 3. After Architecture(사용자 지시가 요구한 것)

```
Stage 01~05 ─→ 공통 Model Selection Layer(Free Pool → Filter → ≤3 → models[]) ─→ OpenRouter(실제 선택/failover) ─→ str
```

이는 각 Stage(또는 그 Agent 함수)가 지금처럼 **정확히 하나의 Engine
모듈을 정적으로 import**하는 대신, **런타임에 후보 목록을 만들고
OpenRouter가 그중 하나를 실제로 고르는 형태**로 호출 경로 자체를
바꾸는 것을 의미한다.

## 4. Architecture Deviation — STOP 사유

`hqs/development/IMPLEMENTATION_RULES.md`(Frozen, CLAUDE.md가 직접
참조하는 문서)의 "Multi-Engine 허용 범위 확인(Scoped, ADR-0024)"
절이 명시한 조건과 이번 요청을 대조한다:

| 조건(`IMPLEMENTATION_RULES.md` 원문) | 이번 요청과의 관계 |
|---|---|
| "허용(Multi-Engine 허용 범위 안): 호출부 파일이 정확히 하나의 Engine 모듈을 import 시점에 정적으로 선택하는 것" | 이번 요청은 "OpenRouter models[] → 실제 selection/failover"를 요구한다 — 이는 import 시점 정적 선택이 아니라 **런타임에 여러 후보 중 하나가 선택**되는 구조다 |
| "금지: ... 3번째 이상의 Engine 추가(이 절은 정확히 2개까지만 확인한다 — **3번째 Engine은 별도 RFC → ADC → ADR 대상**)" | OpenRouter를 "Stage 내부의 LLM 실행 Engine으로 취급"(사용자 지시 원칙 9)하는 것은 정확히 **3번째 Engine 추가**에 해당한다 |
| "금지: 두 Engine 중 하나가 실패했을 때 다른 Engine으로 자동 전환하는 Fallback 로직" | OpenRouter의 "실제 selection/failover"는 이 금지 항목이 묘사하는 것과 구조적으로 동일한 성격(여러 후보 중 실행 시점 자동 전환)이다 |

`ADR-0026` 자신도 이를 이미 예견하고 명시적으로 유보했다:

> §10 Production Routing Integration Decision Status: **NOT YET
> DETERMINED**. "OpenRouter는 지금까지 Production Stage Engine
> Routing에 편입된 적이 없고, '실험적 검증 endpoint'로만 다뤄져
> 왔다... 이 ADR은 이 구분을 바꾸지 않는다."
>
> §12 Non-Goals: "Stage 01~05 Production 코드/routing을 변경하는
> 것 — 하지 않음."

**결론**: 이번 작업이 요구하는 "Production Migration"은 `ADR-0026`
자신이 아직 채택하지 않겠다고 명시한 바로 그 결정(Production Routing
Integration)을 전제로 한다. 이 결정을 실제로 채택하려면
`IMPLEMENTATION_RULES.md`가 요구하는 대로 **별도 RFC → ADC → ADR**
(3번째 Engine 추가 절차)가 필요하다.

이번 작업 지시는 동시에 "`RFC-0040`/`ADC-0043`/`ADR-0026` 수정 금지"
를 요구한다. 이 세 문서를 건드리지 않고 새 RFC/ADC/ADR도 만들지
않은 채로 코드만 바꾸는 것은, `hqs/development/IMPLEMENTATION_
RULES.md` "Architecture 문제 발견 시 절차" 1번("직접 수정하지
않는다")과 CLAUDE.md의 Frozen Architecture 원칙을 정면으로 위반한다.

**따라서 이 작업은 코드 Migration을 수행하지 않고 STOP한다**
(사용자 지시 원칙 10을 그대로 따름).

## 5. Stage별 변경점

**없음 — Migration을 수행하지 않았다.**

## 6. Contract 보존 여부

해당 없음(코드 변경 없음) — 기존 Contract(§1에 조사된 그대로)는
전부 그대로 유지되고 있다.

## 7. 기존 Agent/Capability 보존 여부

**보존됨** — `mvp/agents/design.py`, `backend.py`, `requirements.py`,
`qa.py` 전부 무변경. 재작성 없음.

## 8. hardcoded model 제거 여부

**해당 없음 — 애초에 제거할 hardcoded model이 없었다.** §1 조사가
확인한 대로, 어느 Stage/Agent 코드도 특정 모델명(`gpt-4o` 등)을
직접 참조하지 않는다 — 모델명은 각 Engine 모듈(`chatgpt_engine.py`
의 `CHATGPT_DEFAULT_MODEL`) 내부에만 있다. "Stage별 특정 모델명을
고정하지 않는다"(원칙 3)는 조건은 **Migration 이전부터 이미 충족되어
있었다** — 이 사실 자체가 이번 조사의 중요한 발견이다.

## 9. deterministic filtering / candidate ≤3 적용 여부

**미적용 — Migration을 수행하지 않았으므로 Production 코드에는
적용되지 않았다.** 해당 로직은 `projects/openrouter-free-model-
selection-architecture-experiment-v1/`에 실험 코드로만 존재한다
(§Related).

## 10. Test 결과

- 기존 Production 테스트 스위트 재실행(변경 없는 baseline 확인
  목적, 읽기 전용): `hqs/development/mvp/tests/` — **324 passed, 6
  skipped**(회귀 없음, §1 조사가 인용한 각 Stage 테스트 파일 전부
  포함).
- 이번 작업에서 추가/수정된 Production 테스트는 없다(코드 변경이
  없었으므로).

## 11. Production Regression

**없음.** `git diff --stat -- hqs/`가 빈 결과를 반환한다(§15에서
재확인) — 애초에 아무것도 바뀌지 않았으므로 회귀 가능성 자체가
없다.

## 12. OpenRouter 실제 실행 결과

**해당 없음 — 이번 작업은 실제 OpenRouter 호출을 수행하지 않았다.**
Migration 자체가 STOP됐으므로 Stage 01~05를 통한 실제 OpenRouter
실행도 발생하지 않았다. (참고: OpenRouter의 실제 실행 가능성 자체는
`OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`가 별도
Experiment로 이미 다뤘다 — 이 문서가 그 실험들을 대체하거나
반복하지 않는다.)

## 13. quota/network limitation

**해당 없음.** Migration이 코드 변경 이전 단계(Governance 검토)에서
멈췄으므로 quota/network 상태는 이번 판정에 영향을 주지 않았다.

## 14. Architecture Deviation(종합, §4 상세 참조)

OpenRouter를 Stage 01~05 실행 경로에 "Stage 내부의 LLM 실행 Engine"
으로 편입하는 것은 `ADR-0024`의 2-Engine Scoped 예외 범위를 벗어나는
**3번째 Engine 추가**이며, `IMPLEMENTATION_RULES.md`는 이를 명시적으로
"별도 RFC → ADC → ADR 대상"으로 지정해 두었다. `ADR-0026`도 이 결정을
자신의 범위 밖(NOT YET DETERMINED)으로 명시적으로 유보했다. 이
Migration을 진행하려면:

1. 새 RFC(예: RFC-0041 후보 번호, 이 세션은 만들지 않음)로 "OpenRouter를
   Stage 01~05의 3번째 Engine으로 Production에 편입한다"는 제안을
   공식화하고,
2. 그 RFC가 `ADR-0024`의 2-Engine 구조·`IMPLEMENTATION_RULES.md`의
   Engine Routing/Gateway 금지 조항과의 관계를 다루며,
3. ADC → ADR 단계에서 "Production Routing Integration"을 NOT YET
   DETERMINED에서 실제로 Accept(또는 재차 Reject)해야 한다.

이 세 단계 중 어느 것도 이번 작업에서 수행하지 않았다 — 사용자 지시가
`RFC-0040`/`ADC-0043`/`ADR-0026` 수정을 금지했고, 새 RFC 작성은 이번
작업 범위 밖(사용자가 명시적으로 요청하지 않음)이기 때문이다.

## 최종 판정: D. Architecture change required

코드 결함이 아니라 **Governance 결정 자체가 아직 존재하지 않는다**는
의미의 D다. `ADR-0026`은 정확히 이 상황을 대비해 §10을 NOT YET
DETERMINED로 남겨뒀고, `IMPLEMENTATION_RULES.md`는 3번째 Engine
추가에 별도 RFC → ADC → ADR을 요구한다 — 이번 작업은 그 요구를
우회하지 않았다.

## NOT DETERMINED 종합

- OpenRouter를 3번째 Engine으로 편입하는 것이 실제로 승인될지 —
  Governance 판단 필요, 이 문서는 판단하지 않는다.
- 승인된다면 그 형태가 "OpenRouter가 ChatGPT/Claude Code를 대체"인지
  "셋 중 Stage별로 선택"인지 "OpenRouter가 두 Engine의 fallback"인지
  — 전부 미정.
- 승인되더라도 `IMPLEMENTATION_RULES.md`의 Engine Gateway/Routing
  금지 조항을 어떤 형태의 Scoped 예외로 통과시킬지 — 미정(참고:
  `ADC-0031` OmniRoute Thin Caller, `ADR-0024` 2-Engine이 선례이나
  둘 다 이번 사례에 직접 적용되지 않는다).

## Governance / Production 영향

- `RFC-0040`/`ADC-0043`/`ADR-0026` 무수정.
- `ADR-0024`, `IMPLEMENTATION_RULES.md` 무수정.
- Production `hqs/` 코드 **1바이트도 변경 없음**(§15 확인).
- 새 RFC/ADC/ADR을 이 세션이 임의로 만들지 않았다(사용자 지시 원칙
  10 — "임의 수정하지 말고 STOP + Evidence로 보고").
- API Key/Authorization 값은 이 문서 어디에도 포함되지 않았다(이번
  작업은 실제 API 호출을 하지 않았다).

## 15. git diff 확인(최종)

```
$ git status --short
(이 Evidence 문서 추가 전 기준: 완전히 clean)

$ git diff --stat -- hqs/
(빈 결과)
```

## Related

- `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`
  (§10 Production Routing Integration = NOT YET DETERMINED — 이
  Evidence의 핵심 근거)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
  (2-Engine Option C, 3번째 Engine 배제)
- `hqs/development/IMPLEMENTATION_RULES.md`("Multi-Engine 허용 범위
  확인" 절, "Architecture 문제 발견 시 절차" 절)
- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`,
  `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
- `docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
  `docs/research/STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`
  (Experiment 범위, Production 미편입 상태에서 수행된 선행 작업)
