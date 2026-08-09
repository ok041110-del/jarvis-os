# RFC-0005: Engine 연결 Boundary — Execution Result에 실제 산출물을 연결하는 경계

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (E2E Architecture 조사 후속)
**대상**: Execution Layer의 `results`(Execution Result 목록 항목)를
실제 Engine 산출물과 연결하는 경계 — 전용 RFC가 한 번도 작성된 적
없는 항목
**Evidence**: `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`core/execution_layer/mvp_0001~0006/*.py`(6개 Builder 소스),
`core/execution_layer/pipeline.py`,
`docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md`,
`development-hq/mvp/engine.py`,
`docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`,
`docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`

> 본 RFC는 Engine 연결 방식을 결정하지 않는다. 새 Architecture를
> 설계하지 않는다. Engine Gateway/Adapter를 만들지 않는다. 새
> 실험을 하지 않는다. 이 RFC는 "Execution Layer의 `results`를 실제
> Engine 산출물과 어떻게 연결하는가"를 Boundary Question으로
> 정의하고, 이미 저장소에 기록된 Evidence만 정리한다. 해결책 선택은
> 후속 ADC로 넘긴다. ADC-01·ADC-02·Execution Result Consumer는
> 재조사하지 않는다 — 기존 결정(Not Accepted)만 인용한다.

## 0. 이 RFC가 열린 이유

Execution Layer 6개 Builder + Pipeline은 완성되어 테스트됐다
(`core/execution_layer/mvp_0001~0006`, `pipeline.py`, 55 tests). 그러나
`ExecutionResultBuilder`(`build_execution_result`)와
`run_execution_layer_pipeline()` 모두 `results: list[str]`을
**caller가 주입**해야 하며, 어떤 Builder도 Engine을 호출해 그 값을
스스로 만들지 않는다(`ARTIFACT-STANDARD-v1.md` "공통 패턴": *"AI
호출 없음, Runtime 없음. 6개 MVP 전체에서 `call_engine`... 문자열이
소스 코드에 없음을 각 MVP의 테스트로 확인했다"*).

동시에, Development HQ 쪽의 `call_engine()`
(`development-hq/mvp/engine.py`)은 더 이상 규칙 기반이 아니라 실제
Engine(Claude Code CLI)을 호출한다 — 이 파일 자신의 docstring이
명시한다: *"ENGINE-CONNECT-0001(worktree 실험)에서 이 함수를 실제
Claude Code Engine 호출로 교체해도 Stop Trigger가 발동하지 않음을
확인했다... 그 실험 결과를 그대로 tracked branch에 반영한다."*

즉 Engine을 실제로 호출하는 단일 함수는 이미 존재하고 검증됐지만,
Execution Layer의 Artifact Chain 어디에도 그 함수를 호출하는 지점이
없다 — 이것이 사용자 Task 입력에서 Execution Result 반환까지의
E2E 흐름이 실제로 끊기는 첫 지점이다. 이 RFC는 그 다음 절차로서,
같은 Evidence를 근거로 정식 Architecture 논의를 연다.

## 1. Problem Statement

Execution Result의 `results` 항목이 실제 Engine 산출물을 담으려면,
Execution Layer의 어느 지점에서(Model Request 생성 시? Execution
Handle 생성 시? 별도 단계?) `call_engine()`을 호출할지, 그 호출
결과를 어떻게 `results: list[str]`로 변환할지가 결정되어야 한다.
이 결정은 지금까지 어떤 RFC/ADC/ADR에서도 다뤄진 적이 없다.

## 2. Evidence Summary

| 문서/소스 | 관찰된 사실 |
|---|---|
| `ARTIFACT-STANDARD-v1.md` "공통 패턴" | 6개 MVP(Builder) 전체가 `call_engine`, `openai`, `anthropic`, `subprocess` 등의 문자열을 소스 코드에 포함하지 않는다는 것이 각 MVP의 테스트로 확인됐다 — Execution Layer의 **불변식**이다. |
| `core/execution_layer/mvp_0001~0006/tests/*.py`, `core/execution_layer/tests/test_pipeline.py` | `test_no_ai_or_runtime_symbols_present_in_module`이 6개 Builder + Pipeline 전부에서 반복되며, 이 불변식을 실제로 강제한다(55개 테스트 중 다수가 이 검증을 포함). |
| `core/execution_layer/mvp_0006/execution_result_builder.py` | `build_execution_result(execution_state, *, handle_id, produced_at, results: list[str])` — `results`는 함수 매개변수로 caller가 제공한다. 함수 본문 어디에도 Engine을 호출하는 코드가 없다(`IMPL-STOP-0002` §2 E-3·E-4가 이미 이 사실을 근거로 항목 타입만 결정하고 값의 출처는 범위 밖에 뒀다). |
| `core/execution_layer/pipeline.py` | `run_execution_layer_pipeline(...)`도 `results: list[str]`을 그대로 caller로부터 받아 마지막 Builder에 전달할 뿐이다 — 중간에 Engine을 호출하는 단계가 없다. |
| `development-hq/mvp/engine.py` | `call_engine(prompt: str) -> str`이 실제로 존재하며, 현재 `subprocess.run(["claude", "-p", prompt, ...])`를 호출한다(모듈 docstring: "그 실험 결과를 그대로 tracked branch에 반영한다"). Engine Routing 없음, 단일 함수. |
| `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md` | `call_engine()`을 규칙 기반에서 실제 Engine 호출로 교체하는 실험이 실제로 수행됐고, "어떤 Stop Trigger도 발동하지 않았다"고 기록됐다. 단, 이 실험은 `development-hq/mvp/`의 `call_engine()` 자체를 대상으로 했을 뿐, **Execution Layer의 어느 Builder도 이 실험에 관여하지 않았다.** |
| `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | Kernel 수준에서 Execution Layer Module이 Accept됐고 그 책임에 "Model/Engine 선택·호출까지의 경계"가 포함된다고 명시했으나, 같은 문서가 스스로 한정한다: *"내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model Routing)는... ADC-01·ADC-02가 여전히 Open으로 남긴 영역이다."* |
| `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md` §2 | Execution Layer의 책임에 "그 실행을 담당할 Model/Agent를... 선택·호출하는 것까지 포함한다"고 이미 확인했으나, **어떻게**(Prompt 구성, 호출 시점, 결과 파싱)는 그 RFC의 범위 밖으로 명시했다. |

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- Execution Layer 6개 Builder + Pipeline은 예외 없이 "AI 호출 없음"을
  테스트로 강제한다 — 이는 우연이 아니라 반복 설계된 불변식이다.
- Engine을 실제로 호출하는 단일 함수(`call_engine()`)는 이미
  존재하고, 최소 1회 검증됐다(ENGINE-CONNECT-0001) — 그러나 그
  검증은 Development HQ 범위 안에서만 이뤄졌다.
- "Execution Layer가 Model/Engine을 선택·호출하는 책임을 가진다"는
  것은 이미 Kernel Module 수준에서 확정됐다(`ADR-0002-execution-layer-module-baseline.md`).
  그러나 "그 내부 구조(언제·어떻게 호출하는가)"는 같은 문서가 명시적으로
  ADC-01·ADC-02(둘 다 Not Accepted, 재조사하지 않음)에 걸린 채 열어
  두었다.
- Execution Result의 항목 타입(`str`, 개별 항목의 의미 미정)은 이미
  결정됐으나(RFC-0002~0004, ADC-0002~0004, ADR-0001·0002 execution-layer),
  그 값을 **어디서 가져오는가**는 그 결정 범위 밖에 있었다
  (`IMPL-STOP-0002` §2 E-4).

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Execution Layer의 `results`(Execution Result 목록 항목)를 실제 Engine
산출물과 연결하는 경계는 어디이며, 어떤 형태인가?

이 질문은 세부적으로 최소 두 개의 하위 질문을 포함하나, 이 RFC는
어느 것도 판단하지 않는다.

| 하위 질문 | 관련 Evidence |
|---|---|
| Execution Layer의 어느 Builder(또는 그 사이의 어느 지점)가 `call_engine()`을 호출하는가 | 현재 6개 Builder 중 어느 것도 호출하지 않는다(§2) — 새 지점이 필요한지, 기존 Builder를 수정하는지는 결정된 바 없다 |
| `call_engine()`의 반환값(`str`, 자유 서술형 산문 — `ENGINE-CONNECT-0001`의 실제 관찰)을 `results: list[str]`로 어떻게 변환하는가 | `ENGINE-CONNECT-0001`은 Development HQ 맥락에서 반환값이 "자유 서술형 산문 + 코드 블록"이라고 관찰했으나, 이를 Execution Layer의 opaque 문자열 목록으로 변환하는 규칙은 어디에도 없다 |

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Engine 연결 방식의 실제 선택(어느 Builder가 호출하는지, 변환
  규칙이 무엇인지).
- Engine Gateway, Adapter, Multi-Model Routing의 설계 —
  `IMPLEMENTATION_RULES.md`("Engine Gateway 구현 금지")와
  `docs/governance/adc/ADC-0003.md` 판단 4(Multi-Model, Out of
  Authority)가 이미 금지·분리해 둔 영역이다.
- ADC-01(Model 축과 Component 축의 대응 관계), ADC-02(Runtime 존폐)
  재조사 — `RFC-0008/ADC-0008`, `RFC-0009/ADC-0009`의 Not Accepted
  결론을 기존 결정으로만 인용한다.
- Execution Result Consumer의 재판단 — `ADC-0004-execution-result-consumer.md`
  의 Not Accepted 상태는 이 RFC의 결과가 나오기 전까지 그대로
  유지된다.
- Execution State의 상태 전이 규칙(별도 사안).
- `results` 항목의 개수 제한, 의미론적 종류 구분(파일/로그/텍스트
  보고) — `ADC-0003-execution-result-item-schema.md` Q0에서 이미
  Not Accepted로 배제됐다.
- Development HQ, Kernel, Execution Layer의 어떤 코드도 수정하지
  않는다.
- 새로운 실험.

## Non-goals

- 이 RFC는 Engine 연결 방식을 결정하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `ARTIFACT-STANDARD-v1.md`,
  6개 Builder + Pipeline 소스, `IMPL-STOP-0002`, `engine.py`,
  `ENGINE-CONNECT-0001`, `ADR-0002-execution-layer-module-baseline.md`,
  `RFC-0005-development-hq-execution-boundary.md`에 이미 기록된
  내용만 인용했다.
- 이 RFC는 Architecture Baseline이나 Execution Layer Artifact
  Standard v1을 변경하지 않는다.
- 이 RFC는 Engine Gateway/Adapter를 설계·구현하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.
- 이 RFC는 ADC-01·ADC-02·Execution Result Consumer를 재조사하지
  않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §4의 두 하위 질문(호출 지점, 변환 규칙) 중 현재 Evidence로 결정
   가능한 것이 있는지 — 없다면 억지로 결정하지 않고 Not Accepted와
   부족한 Evidence만 기록한다(`ADC-0008`·`ADC-0009`의 선례와 동일한
   방식).
2. 결정 가능한 범위가 있다면, "AI 호출 없음" 불변식(§2)을 어떻게
   개정할지 — 이 불변식 자체를 깨는 것은 Execution Layer 5년(6개
   MVP) 전체의 반복 검증된 패턴을 바꾸는 것이므로, 그 개정이
   정당화되는지도 함께 판단 대상이다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ARTIFACT-STANDARD-v1.md`, 6개
  Builder + Pipeline 소스, `IMPL-STOP-0002`, `engine.py`,
  `ENGINE-CONNECT-0001`, `ADR-0002-execution-layer-module-baseline.md`,
  `RFC-0005-development-hq-execution-boundary.md`에 실제로 기록된
  내용만 인용했다. 새 실험은 하지 않았다.
- Engine 연결 방식을 결정했는가 — **아니오**. §4는 질문 형태로만
  남겼고, 하위 질문 어느 것도 판단하지 않았다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. `RFC-0008/ADC-0008`,
  `RFC-0009/ADC-0009`의 Not Accepted 결론을 기존 결정으로만
  인용했다(§Out of Scope).
- Execution Result Consumer를 재판단했는가 — **아니오**.
- 새 Architecture(Engine Gateway 등)를 설계했는가 — **아니오**.
- Architecture를 변경했는가 — **아니오**.
- Execution Layer, Development HQ, Kernel을 구현했는가 — **아니오**.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(연결 방식 선택, Engine Gateway 설계, ADC-01/02
  재조사, Consumer 재판단, State 전이 규칙, 항목 개수/의미 재논의,
  코드 수정, 새 실험)을 다뤘는가 — **아니오**.
