# ENGINE-CONNECT-0005: Development HQ → Implementation Specification → Execution Layer Pipeline → 실제 Engine → ExecutionResult — Runtime Evidence

이 문서는 사용 후기가 아니다. 실제로 수행한 배선 실험 하나의 기록이다.
`ENGINE-CONNECT-0002`(caller → `call_engine()` → 실제 Engine →
`results:list[str]` → `ExecutionResult`, `ExecutionResultBuilder`
1개만 직접 호출)의 후속으로, 이번에는 **6개 Builder를 하나로 묶은
`core/execution_layer/pipeline.py`의 `run_execution_layer_pipeline()`
전체**를 실제 Engine과 함께 실행한다. Execution Result Contract를
새로 설계하지 않는다. Engine Gateway/Adapter를 만들지 않는다.
Baseline을 수정하지 않는다. RFC/ADC/ADR을 작성하지 않는다.
ADC-01·ADC-02·`ADC-0010`(Engine Caller 위치)·`ADC-0011`(별도 실행
위치)을 재조사하지 않는다 — 이 실험은 그 Not Accepted 결론을
바꾸지 않는다. **이 문서 자체가 코드 변경이 아니다** — 실험 코드는
이 세션의 scratchpad에만 존재했고 tracked 브랜치에는 반영되지
않았다(`ENGINE-CONNECT-0002`와 동일한 격리 원칙).

## 왜 이 실험이 필요했는가

- `ENGINE-CONNECT-0002`는 6개 Builder 중 `ExecutionResultBuilder`
  하나만 직접 호출했고, 입력도 `MVP-0006` Dogfooding이 이미 만들어 둔
  고정 fixture(`toy_issue.implementation_specification.md`)를 재사용
  했다. `run_execution_layer_pipeline()`(6개 Builder 전체를 하나로
  묶은 함수)이 실제로 존재하지만, 그 함수 자체를 실제 Engine과
  함께 끝까지 실행해 관찰한 적은 없었다.
- `ADC-0010`은 "caller가 어디 있어야 하는가"(production 위치, 6개
  후보 C1~C6)를 전부 Not Accepted로 남겼다 — 이 실험은 그 질문에
  답하지 않는다. 이 실험의 caller는 scratchpad에만 존재하는 임시
  스크립트이며, 이름·형태·위치 무엇도 tracked 코드베이스에 정의하지
  않는다(C6을 Accept하지 않는다).
- 이 실험은 "Development HQ가 실제로 만든 Implementation
  Specification이 → Execution Layer Pipeline 함수 하나를 통해 →
  실제 Engine 호출까지 → 최종 ExecutionResult로" 끝까지 이어지는지,
  6개 Builder 전체를 한 번에 관찰한 적이 없다는 공백을 메운다.

## Experiment

- **격리**: 실험 스크립트(`experiment_engine_connect_0005.py`)는 이
  세션의 scratchpad 디렉터리에만 존재한다 — tracked 브랜치
  (`claude/engine-connect-0005-full-pipeline-wiring`)에는 이 문서
  하나만 추가된다. `git status --porcelain`이 실험 전후 비어 있음을
  확인했다(아래 "회귀 확인" 참고).
- **Development HQ의 Implementation Specification 생성 방법**:
  `development-hq/mvp/engine.py`의 `_analyze_requirement()` →
  `_design_from_requirement()` → `_generate_code()`를 그대로 순서대로
  호출했다. 이 세 함수는 `ADC-0001`이 확정한 Implementation
  Specification Contract(Target File/Public Interface/Functions/
  Classes/Dependencies/Algorithm Outline/Edge Cases/Validation
  Notes 8개 절)를 만드는, 결정론적이고 AI 호출이 없는 규칙 기반
  함수다 — `call_engine()`이 실제 Engine으로 바뀐 뒤에도(`ENGINE-CONNECT-0001`)
  코드 자체는 그대로 저장소에 남아 있다. `mvp.workflow_0008.run_pipeline()`을
  쓰지 않은 이유는 `core/execution_layer/mvp_0006/dogfooding/run_dogfooding.py`가
  이미 문서화한 것과 같다 — `run_pipeline()`은 내부에서 `call_engine()`을
  5회 호출하므로, 이 실험(Pipeline 배선 관찰)이 요구하지 않는 실제
  비용을 만든다. Issue: "Add clamp helper"
  (`clamp(value, low, high)` — value가 low보다 작으면 low, high보다
  크면 high, 그 외 value 그대로 반환).
- **Execution Layer 쪽 호출**: `build_execution_request()` +
  `build_prompt_specification()`(MVP-0001/0002 Builder, AI 호출
  없음)을 직접 호출해 실제 Engine에 넘길 Prompt Specification을
  얻었다 — Execution Request(머리말만 붙는 그대로의 Implementation
  Specification)가 아니라, Execution Layer가 "AI 모델이 읽기 쉽게
  Rendering"하도록 설계한 실제 Prompt Specification을 Engine 프롬프트로
  썼다(`ENGINE-CONNECT-0002`는 Implementation Specification 원문을
  그대로 프롬프트로 썼다 — 이번 실험은 그보다 한 단계 더 Contract에
  충실한 프롬프트를 썼다).
- **실제 Engine 호출 횟수**: **1회.** `development-hq/mvp/engine.py`의
  실제 `call_engine()`(`claude -p`, `--disallowedTools`로 파일/셸
  도구 차단, cwd 격리 — `MVP-0028` 반영된 상태)을 Prompt Specification
  전체(길이 약 1.9K자)를 prompt로 1회 호출했다.
- **최종 ExecutionResult 생성**: 개별 Builder를 다시 하나씩 부르지
  않고, `run_execution_layer_pipeline(implementation_specification,
  created_at=..., submitted_at=..., state="COMPLETED", changed_at=...,
  produced_at=..., results=[raw_output])` **함수 하나**를 호출해
  6개 Builder 전체를 한 번에 통과시켰다 — Pipeline 자체가 실제로
  검증 대상이 된 것은 이번이 처음이다.

## 실행 결과 (실제 Engine, elapsed 73.9초)

| 확인 항목 | 관찰 결과 |
|---|---|
| Development HQ Implementation Specification 생성 | 성공, 8개 절 모두 포함 (`## Target File` ~ `## Validation Notes` + `## Reference Design`) |
| `build_execution_request()` 호출 | 예외 없음 |
| `build_prompt_specification()` 호출 | 예외 없음, `# Mission`/`# Input`/`# Constraints`/`# Expected Output`/`# Validation Notes` 5개 절 모두 렌더링됨 |
| 실제 Engine 호출(`call_engine()`) | 예외 없음, 반환값 `str`, 길이 2009자 |
| 반환값 → `results: list[str]` 변환 | `[raw_output]` — 새 변환 규칙 불필요, `ENGINE-CONNECT-0002`와 동일 |
| `run_execution_layer_pipeline()` 전체(6개 Builder) 1회 호출 | 예외 없음, 최종 ExecutionResult 길이 5652자 |
| `raw_output`이 ExecutionResult `## Results` 절 안에 verbatim 보존됨 | **True**(Python `in` 연산자로 확인) |

### 실제 Engine 응답 내용

이번 프롬프트(Prompt Specification, "Mission/Input/Constraints/
Expected Output/Validation Notes"로 구조화됨)에 대해, 실제 Engine은
`## Public Interface`/`## Functions`(Design이 만든 `add_clamp_helper`,
`add_clamp_helper_check_1~3`)와 `## Classes`(`AddClampHelper`,
`AddClampHelperValidator`)를 정확히 반영한 실제 Python 코드를
반환했다 — Implementation Specification이 지정한 함수/클래스 이름·
시그니처를 그대로 구현했다(생성된 코드가 명세의 이름을 실제로
따랐는지까지 관찰됐다는 점이 `ENGINE-CONNECT-0002`보다 한 걸음 더
나아간 부분이다). 응답 앞부분에는 파일 쓰기 도구가 없다는 설명이
붙었다("This session doesn't have file-write or shell tools
available...") — `STATELESS_CALL_NOTICE`(`MVP-0025` 이전부터 존재)가
막으려던 것과 같은 종류의 서술이 이번에도 나타났다(코드 자체는
정상적으로 포함됨, 이 서술 자체가 파이프라인을 막지는 않았다 — 관찰만
기록한다).

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| 새 Component/Layer/Service 필요 | 미발동 |
| Engine Gateway/Adapter 필요 | 미발동 — 기존 공개 함수(`_analyze_requirement`/`_design_from_requirement`/`_generate_code`/`build_execution_request`/`build_prompt_specification`/`call_engine`/`run_execution_layer_pipeline`)를 그대로 순서대로 호출 |
| Registry/Scheduler/Runtime 필요 | 미발동 |
| Engine Routing 필요 | 미발동 — 단일 Engine, 단일 호출 지점 |
| `results` 변환 규칙 신설 필요 | 미발동 — `[raw_output]` 그대로 충분(`ENGINE-CONNECT-0002`와 동일 결론 재확인) |
| Execution Layer 내부(Builder/Pipeline) 수정 필요 | 미발동 — 코드 변경 0건 |
| Development HQ(`engine.py`) 수정 필요 | 미발동 — 코드 변경 0건 |
| Baseline 변경 필요 | 미발동 |
| C6(별도 caller)을 Production으로 Accept해야 할 필요 | 미발동 — 이 실험은 그 판단을 하지 않는다, scratchpad 스크립트는 tracked 코드베이스에 존재하지 않는다 |

**하나도 발동하지 않았다.**

## 회귀 확인

- 실행 범위: `python3 -m pytest core/execution_layer development-hq/mvp -q`
- 결과: **58 passed** — `ENGINE-CONNECT-0002`가 관찰한 것과 동일한
  수(58). 이번 실험으로 인한 코드 변경이 없으므로 회귀도 없다.
- `git status --porcelain`: 실험 전후 빈 상태 — 실험 스크립트는 이
  세션의 scratchpad(tracked 브랜치 밖)에만 존재했다.

## 이 문서가 하지 않는 것

- caller의 production 위치를 결정하지 않았다 — `ADC-0010`의 Not
  Accepted 상태(C1~C6 전부)를 바꾸지 않는다. 이 실험의 caller는
  scratchpad에만 존재하며 어떤 tracked 위치로도 승격하지 않는다.
- `ADC-0011`(Kernel/HQ에 속하지 않는 별도 실행 위치)의 Not Accepted
  상태를 바꾸지 않는다 — 이 실험은 별도 실행 위치를 새로 제안하지
  않는다.
- Execution Layer 내부에서 `call_engine()`을 호출하도록 바꾸지
  않았다 — `ADC-0005` Q1(Not Accepted)을 재론하지 않는다. Engine 호출은
  이번에도 Execution Layer 함수 밖(scratchpad 스크립트)에서 일어났다.
- `results: list[str]`로의 변환 규칙을 정식 Contract로 확정하지
  않았다 — `[raw_output]` 1개 항목이 이번에도(2회 연속) 관찰됐을
  뿐이다.
- Execution Result Consumer를 설계하지 않았다.
- Development HQ의 `_generate_code()`가 만드는 Implementation
  Specification과, 실제 `call_engine()`이 만드는 raw 코드 출력
  사이의 형식 차이(전자는 8절 구조 문서, 후자는 자유 서술+코드
  블록)를 통일하는 어떤 변환도 만들지 않았다 — Prompt Specification
  까지는 구조화됐지만, 그 결과로 돌아오는 Engine 응답 자체는 여전히
  비구조화 텍스트다(관찰만 기록).

## Unknowns

- 이번에도 `results` 항목은 1개만 관찰했다 — 2개 이상일 때의 동작은
  여전히 미관찰(`ENGINE-CONNECT-0002`와 동일한 공백).
- Prompt Specification 형식(5개 절로 재배치된 구조)이 항상 이번처럼
  Implementation Specification의 함수/클래스 이름을 정확히 반영한
  코드를 이끌어내는지 — 1회만 관찰했다.
- "파일 쓰기 도구가 없다"는 서술이 매번 응답 앞에 붙는지, 어떤
  조건에서 사라지는지 — 이번 관찰에서는 코드 자체가 온전했으므로
  파이프라인에 영향은 없었지만, 다른 프롬프트/Issue에서 이 서술이
  더 커지거나 코드를 대체할 가능성은 (`MVP-0025` 이전 이력에 비춰)
  배제되지 않는다.

## Conclusion

Development HQ가 규칙 기반 Capability Logic으로 실제로 만든
Implementation Specification이, Execution Layer의 기존 Builder
(`build_execution_request`/`build_prompt_specification`)로 실제
Engine용 Prompt Specification으로 렌더링되고, 실제 Engine
(`call_engine()`, Claude Code CLI) 호출로 실제 코드 산출물을 얻은
뒤, `run_execution_layer_pipeline()`(6개 Builder를 하나로 묶은 기존
함수) 1회 호출로 최종 ExecutionResult까지 이어지는 전체 경로가,
기존 Contract·불변식을 하나도 수정하지 않고 실제로 관찰됐다. 어떤
Stop Trigger도 발동하지 않았다. `raw_output`은 최종 ExecutionResult
안에 verbatim으로 보존됐다(`ENGINE-CONNECT-0002`와 동일 결론, 이번엔
Pipeline 함수 전체를 통해 재확인). 다만 이 결과는 caller의 production
위치(`ADC-0010`/`ADC-0011`), 다중 항목 `results`, 다른 입력에 대한
재현성 등은 다루지 않는다 — 이 문서는 그 판단들을 내리지 않는다.
