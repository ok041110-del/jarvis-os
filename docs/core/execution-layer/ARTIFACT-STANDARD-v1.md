# Execution Layer Artifact Standard v1

Execution Layer MVP-0001~0005에서 실제로 구현되고 Dogfooding으로
검증된 5개 Artifact의 Contract를 Baseline으로 고정한다. 이 문서는
구현이 아니라, 이미 검증된 사실을 정리한 Standard다.

새 Architecture를 만들지 않는다. 새 Builder를 만들지 않는다.
Runtime, Claude Code, Prompt Engineering은 논의하지 않는다.
MVP-0001~0005에서 이미 검증된 내용만 일반화한다.

Execution Result(여섯 번째 Artifact)의 **형태(shape)** 는
`ADC-0002-execution-result-contract.md`가 결정했다 — 산출물
목록(list)이다. 이 문서는 그 형태만 반영하며, 목록 항목의 필드
스키마는 여전히 설계하지 않는다.

## Artifact Chain (전체 개요)

```
Implementation Specification   (Development HQ MVP-0013, Execution Layer 밖)
            │
            ▼  ExecutionRequestBuilder      (MVP-0001)
Execution Request
            │
            ▼  PromptSpecificationBuilder   (MVP-0002)
Prompt Specification
            │
            ▼  ModelRequestBuilder          (MVP-0003)
Model Request
            │
            ▼  ExecutionHandleBuilder       (MVP-0004)
Execution Handle
            │
            ▼  ExecutionStateBuilder        (MVP-0005)
Execution State
            │
            ▼  (미구현 Builder — ADC-0002: 형태는 산출물 목록)
Execution Result
```

각 화살표는 "Transformation" 하나이며, 모든 Builder는 입력 Artifact의
텍스트를 한 글자도 바꾸지 않고, 그 앞(또는 위)에 고정된 메타데이터
절만 추가한다. 이 패턴은 5개 MVP 전체에서 예외 없이 반복되었다
(`docs/core/execution-layer/MVP-0001~0005-artifact-mapping.md`에 각각
실측 기록됨).

## Artifact 1: Execution Request

| 항목 | 내용 |
|---|---|
| Mission | Development HQ의 Implementation Specification을 Execution Layer 내부에서 다룰 수 있는 첫 공식 Artifact로 재포장한다. |
| Input | Implementation Specification(`str`, Development HQ MVP-0013 `_generate_code()`가 생성하는 8개 항목 형식: Target File / Public Interface / Functions / Classes / Dependencies / Algorithm Outline / Edge Cases / Validation Notes + Reference Design). |
| Output | Execution Request(`str`) — Implementation Specification 전체 앞에 머리말 `"# Execution Request\n\n"`(21 글자)만 추가한 것. |
| Canonical Fields | 별도 메타데이터 필드 없음. Canonical Content는 입력의 8개 항목 + Reference Design, verbatim 그대로. |
| Version | 코드 안에 `artifact_version` 필드가 존재하지 않는다(MVP-0001 시점에는 버전 필드가 도입되지 않았다) — 이 문서에서는 "MVP-0001이 생성한 형태"로만 식별한다. |
| Producer | `ExecutionRequestBuilder`(`core/execution_layer/mvp_0001/execution_request_builder.py`, `build_execution_request()`). |
| Consumer | `PromptSpecificationBuilder`(MVP-0002). |
| Deterministic 여부 | Yes — 동일한 Implementation Specification 입력에 항상 동일한 Execution Request를 만든다(MVP-0001 `test_transformation_is_deterministic`로 확인). |
| Immutable 여부 | Yes — Execution Request가 만들어진 뒤 어떤 하류 Builder도 그 내용을 바꾸지 않는다(MVP-0002 `test_execution_request_itself_is_unchanged_by_rendering`로 확인). |

## Artifact 2: Prompt Specification

| 항목 | 내용 |
|---|---|
| Mission | Execution Request의 정보를 AI 모델이 읽기 쉬운 5개 절 구조로 Rendering한다. Execution Request는 Canonical Artifact로 남고, Prompt Specification은 그 재배치 결과다. |
| Input | Execution Request(`str`). |
| Output | Prompt Specification(`str`) — 머리말 `"# Prompt Specification\n\n"` + 5개 최상위 절(`# Mission`, `# Input`, `# Constraints`, `# Expected Output`, `# Validation Notes`). |
| Canonical Fields | Execution Request의 9개 절(8개 Implementation Specification 항목 + Reference Design)이 고정 배치표(`RENDERING_MAP`)에 따라 5개 절로 재배치된 것: Mission ← Target File·Public Interface / Input ← Dependencies·Reference Design / Constraints ← Classes·Edge Cases / Expected Output ← Functions·Algorithm Outline / Validation Notes ← Validation Notes. |
| Version | 코드 안에 `artifact_version` 필드가 존재하지 않는다(MVP-0001과 동일하게 MVP-0002 시점에도 버전 필드가 없다) — "MVP-0002가 생성한 형태"로만 식별한다. |
| Producer | `PromptSpecificationBuilder`(`core/execution_layer/mvp_0002/prompt_specification_builder.py`, `build_prompt_specification()`). |
| Consumer | `ModelRequestBuilder`(MVP-0003). |
| Deterministic 여부 | Yes — 동일한 Execution Request 입력에 항상 동일한 Prompt Specification을 만든다(MVP-0002 `test_rendering_is_deterministic`로 확인). |
| Immutable 여부 | Yes — Prompt Specification이 만들어진 뒤 어떤 하류 Builder도 그 내용을 바꾸지 않는다(MVP-0003 `test_prompt_specification_itself_is_unchanged_by_wrapping`로 확인). |

## Artifact 3: Model Request

| 항목 | 내용 |
|---|---|
| Mission | Prompt Specification에 Execution Layer 내부 메타데이터(누가 언제 무엇을 요청했는지 식별하는 정보)만 덧붙여, Execution Engine이 사용할 표준 요청 객체를 만든다. 특정 모델을 호출하는 코드가 아니다. |
| Input | Prompt Specification(`str`). |
| Output | Model Request(`str`) — 머리말 `"# Model Request\n\n"` + `## Metadata` 절(4개 필드) + `## Prompt Specification`(원문 verbatim). |
| Canonical Fields | `request_id`(호출자 제공), `artifact_version`(모듈 상수, 항상 `"execution-layer-mvp-0003"`), `created_at`(호출자 제공), `target_engine`(모듈 상수 placeholder, 항상 `"unresolved"` — 실제 모델명 아님, Model Independent 유지). |
| Version | `"execution-layer-mvp-0003"`(모듈 상수 `ARTIFACT_VERSION`, 입력과 무관하게 항상 동일). |
| Producer | `ModelRequestBuilder`(`core/execution_layer/mvp_0003/model_request_builder.py`, `build_model_request()`). |
| Consumer | `ExecutionHandleBuilder`(MVP-0004). |
| Deterministic 여부 | Yes, 단 `request_id`/`created_at`을 포함한 3개 인자가 모두 같을 때만 — 이 두 값은 Builder가 생성하지 않고 호출자가 주입한다(시계·난수 미사용). 동일한 3개 인자 → 항상 동일한 Model Request(MVP-0003 `test_transformation_is_deterministic`로 확인). |
| Immutable 여부 | Yes — Model Request가 만들어진 뒤 어떤 하류 Builder도 그 내용을 바꾸지 않는다(MVP-0004 `test_model_request_itself_is_unchanged_by_wrapping`로 확인). |

## Artifact 4: Execution Handle

| 항목 | 내용 |
|---|---|
| Mission | Model Request를 그대로 참조하면서, 실행을 추적하기 위한 최소 상태(제출되었다는 사실과 그 식별자)를 부여한다. 실행 결과가 아니라 실행을 추적하기 위한 상태 Artifact다. |
| Input | Model Request(`str`). |
| Output | Execution Handle(`str`) — 머리말 `"# Execution Handle\n\n"` + `## Handle` 절(5개 필드) + `## Model Request`(원문 verbatim). |
| Canonical Fields | `handle_id`(호출자 제공), `request_id`(Model Request의 `## Metadata` 절에서 그대로 읽음 — 새로 주입받지 않음), `status`(고정값 `"PENDING"` 하나만 사용, MVP-0004 범위), `submitted_at`(호출자 제공), `artifact_version`(모듈 상수, 항상 `"execution-layer-mvp-0004"`). |
| Version | `"execution-layer-mvp-0004"`(모듈 상수 `ARTIFACT_VERSION`). |
| Producer | `ExecutionHandleBuilder`(`core/execution_layer/mvp_0004/execution_handle_builder.py`, `build_execution_handle()`). |
| Consumer | `ExecutionStateBuilder`(MVP-0005). |
| Deterministic 여부 | Yes, `handle_id`/`submitted_at`을 포함한 3개 인자가 모두 같을 때 — 이 두 값도 호출자 주입이며 Builder는 시계·난수를 쓰지 않는다(MVP-0004 `test_transformation_is_deterministic`로 확인). |
| Immutable 여부 | Yes — Execution Handle이 만들어진 뒤 Execution State 생성 과정에서도 그 내용이 바뀌지 않는다(MVP-0005 `test_execution_handle_itself_is_unchanged_by_state_creation`로 확인). |

## Artifact 5: Execution State

| 항목 | 내용 |
|---|---|
| Mission | Execution Handle의 실행 상태를 표현하는 독립 Artifact를 만든다. Execution Handle을 수정하지 않고, 그 상태 스냅샷만 별도로 기록한다. |
| Input | Execution Handle(`str`). |
| Output | Execution State(`str`) — 머리말 `"# Execution State\n\n"` + `## State` 절(5개 필드) + `## Execution Handle`(원문 verbatim). Execution Handle 자체는 수정되지 않고, 새 Artifact가 별도로 생성된다. |
| Canonical Fields | `handle_id`(호출자 제공, Execution Handle 자신의 값을 재사용하는 것이 관례 — Dogfooding에서 실측), `request_id`(Execution Handle의 `## Handle` 절에서 그대로 읽음 — 새로 주입받지 않음), `state`(호출자 제공, 5개 허용값 PENDING/RUNNING/COMPLETED/FAILED/CANCELLED 중 하나인지만 검증, 전이 규칙 미검증), `changed_at`(호출자 제공), `artifact_version`(모듈 상수, 항상 `"execution-layer-mvp-0005"`). |
| Version | `"execution-layer-mvp-0005"`(모듈 상수 `ARTIFACT_VERSION`). |
| Producer | `ExecutionStateBuilder`(`core/execution_layer/mvp_0005/execution_state_builder.py`, `build_execution_state()`). |
| Consumer | 아직 없음(Execution Layer 안에서 Execution State를 소비하는 여섯 번째 Artifact/Builder는 이번 MVP 범위까지 구현되지 않았다). |
| Deterministic 여부 | Yes, `handle_id`/`state`/`changed_at`을 포함한 4개 인자가 모두 같을 때 — 세 값 모두 호출자 주입이며 Builder는 시계·난수·상태 결정 로직을 쓰지 않는다(MVP-0005 `test_transformation_is_deterministic`로 확인). |
| Immutable 여부 | Yes(생성 시점 기준) — Execution State는 그 자체가 특정 시점의 스냅샷이며, 이 Standard 범위 안에서 그것을 다시 수정하는 Builder는 존재하지 않는다. |

## Artifact 6: Execution Result

| 항목 | 내용 |
|---|---|
| Mission | Engine이 실제로 만들어낸 산출물을 Execution Layer 내부에서 다룰 수 있는 여섯 번째 Artifact로 담는다. |
| Input | Execution State(`str`). |
| Output | Execution Result — **형태: 산출물 목록(list)**(ADC-0002 Decision). 구체적 직렬화 형식(`str` 내 목록 표현인지, 다른 타입인지)은 미정(ADC-0002 범위 밖). |
| Canonical Fields | 미정(ADC-0002 범위 밖) — 목록 항목의 타입 스키마는 후속 결정 대상. |
| Version | 미정. |
| Producer | 미구현. |
| Consumer | 아직 없음. |
| Deterministic 여부 | 미정 — Builder가 구현되지 않아 확인 불가. |
| Immutable 여부 | 미정 — Builder가 구현되지 않아 확인 불가. |

이 절은 `ADC-0002-execution-result-contract.md`가 결정한 형태(산출물
목록)만 반영한다. 5개 Builder(Artifact 1~5)와 달리, 이 Artifact는
Deterministic/Immutable 여부를 실측(테스트)으로 확인한 적이 없다 —
Builder 자체가 아직 구현되지 않았기 때문이다. "미정" 표시는 누락이
아니라 의도적 표기다(Freeze 원칙).

## 공통 패턴 (5개 Artifact에 걸쳐 반복 확인된 사실)

- **Wrap, not rewrite.** 5개 Builder 모두 입력 Artifact의 텍스트를
  한 글자도 바꾸지 않고, 고정된 메타데이터/구조 절만 추가한다
  (Transformation, Interpretation 아님). Execution Result(Artifact
  6)는 이 패턴을 따르지 않는 첫 사례로 결정됐다(ADC-0002) — 단일
  텍스트 Wrap이 아니라 목록을 담는다.
- **Fixed structural overhead.** 각 변환 단계의 길이 증가분은 입력
  내용과 무관하게 항상 동일했다(MVP-0002: 77자, MVP-0003: 183자,
  MVP-0004: 199자, MVP-0005: 197자 — 각 Artifact Mapping 문서에서
  실제 Issue/토이 Issue 두 Case로 확인).
- **Canonical field 재사용, 재생성 아님.** `request_id`는 Model
  Request에서 만들어진 뒤(MVP-0003) Execution Handle(MVP-0004),
  Execution State(MVP-0005)까지 그대로 전달되며 한 번도 값이
  바뀌지 않았다(Dogfooding에서 세 MVP에 걸쳐 동일한 해시 값으로 실측
  확인). `handle_id`도 동일한 방식으로 MVP-0004→0005에서 재사용된다.
- **caller-supplied identity/time fields.** `request_id`/`created_at`
  (MVP-0003), `handle_id`/`submitted_at`(MVP-0004),
  `handle_id`/`state`/`changed_at`(MVP-0005) — 식별자 발급과 시각
  기록은 각 Builder 내부에서 생성되지 않고 항상 호출자가 주입한다.
  이는 다섯 MVP 모두에서 반복된 설계 결정이며(각 모듈 docstring에
  근거 기록), Session/Runtime의 책임 영역을 Execution Layer Builder가
  침범하지 않기 위함이다.
- **artifact_version은 MVP-0003부터 도입되었다.** Execution Request
  (MVP-0001), Prompt Specification(MVP-0002)에는 `artifact_version`
  필드가 없다. Model Request(MVP-0003)부터 Execution State
  (MVP-0005)까지는 각 Builder 모듈에 고정 상수로 존재한다. 이 불일치는
  이번 Standard가 "정리"하는 것이지 "해소"하는 것이 아니다 — 필드를
  소급 추가하지 않는다.
- **AI 호출 없음, Runtime 없음.** 5개 MVP 전체에서 `call_engine`,
  `openai`, `anthropic`, `requests.`, `subprocess`, `urllib`,
  `http.client`, `datetime.now`, `uuid.uuid4`, `time.time` 문자열이
  소스 코드에 없음을 각 MVP의 테스트로 확인했다.

## Boundary (이 문서가 하지 않는 것)

- 새 Architecture, 새 Layer, 새 Component를 만들지 않는다.
- 새 Builder를 만들지 않는다 — 5개 Builder(MVP-0001~0005)는 이미
  구현된 것을 그대로 인용했을 뿐이다.
- Execution Result의 **필드 스키마**는 설계하지 않는다 — ADC-0002가
  결정한 것은 형태(목록)뿐이다. Builder 구현, 목록 항목의 타입
  분류는 여전히 이 문서의 범위 밖이다.
- Runtime, Scheduler, Retry, Session의 내부 구조를 논의하지 않는다.
- Claude Code, GPT, Codex 등 실제 모델 호출을 논의하지 않는다.
- Prompt Engineering(어떤 문구가 효과적인지)을 논의하지 않는다.
- MVP-0001~0005에서 실제로 구현·테스트·Dogfooding으로 검증된 사실
  외의 내용은 포함하지 않는다.

## 근거

- `core/execution_layer/mvp_0001/execution_request_builder.py`
- `core/execution_layer/mvp_0002/prompt_specification_builder.py`
- `core/execution_layer/mvp_0003/model_request_builder.py`
- `core/execution_layer/mvp_0004/execution_handle_builder.py`
- `core/execution_layer/mvp_0005/execution_state_builder.py`
- `docs/core/execution-layer/MVP-0001-plan.md`,
  `MVP-0001-observation.md`, `MVP-0001-artifact-mapping.md`
- `docs/core/execution-layer/MVP-0002-observation.md`,
  `MVP-0002-artifact-mapping.md`
- `docs/core/execution-layer/MVP-0003-observation.md`,
  `MVP-0003-artifact-mapping.md`
- `docs/core/execution-layer/MVP-0004-observation.md`,
  `MVP-0004-artifact-mapping.md`
- `docs/core/execution-layer/MVP-0005-observation.md`,
  `MVP-0005-artifact-mapping.md`
- `docs/core/execution-layer/RFC-0002-execution-result-contract.md`
- `docs/core/execution-layer/ADC-0002-execution-result-contract.md`
- `docs/core/execution-layer/ADR-0001-execution-result-contract.md`
