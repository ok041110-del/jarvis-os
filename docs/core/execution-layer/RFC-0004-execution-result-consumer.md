# RFC-0004: Execution Result Consumer — 소비 주체와 방식

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Execution Layer 6개 Builder + Pipeline 구현 완료 후속)
**Evidence**: `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`docs/core/execution-layer/RFC-0002~ADR-0002` 전체,
`docs/core/execution-layer/IMPL-STOP-0001-execution-result.md`,
`docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md`,
`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`,
`docs/architecture/core/ADC-0001-core-baseline.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0002-impl-stop.md`,
`docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`

> 본 RFC는 Execution Result Consumer의 해결책(누가/어떻게 소비하는지)을
> 제시하지 않는다. 본 RFC는 기존 Evidence만 근거로 "누가/어떤 방식으로
> Execution Result를 소비하는가"를 Architecture 질문으로 정의한다. 새
> 실험을 하지 않는다. 새 후보를 만들지 않는다. Consumer를 구현하지
> 않는다. Runtime/Memory/Event Bus를 설계하지 않는다.

## 0. 이 RFC가 열린 이유

`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` "Artifact 6:
Execution Result" 절의 `Consumer` 행은 MVP-0006(`ExecutionResultBuilder`)
구현과 Pipeline(`run_execution_layer_pipeline()`) 완료 이후에도 여전히
다음과 같다.

> *"아직 없음(Execution Layer 안에서 Execution Result를 소비하는 일곱
> 번째 Artifact/Builder는 구현되지 않았다. `core/execution_layer/
> pipeline.py`의 `run_execution_layer_pipeline()`은 Execution Result를
> 최종 반환값으로 넘길 뿐, 그 내용을 소비·해석하지 않는다)."*

6개 Builder + Pipeline까지 Execution Layer의 결정된 Contract 범위가
소진된 지금, 이 빈 칸이 Execution Layer에서 유일하게 남은 미결
지점이다. 이 RFC는 그 다음 절차로서, 같은 Evidence를 근거로 정식
Architecture 논의를 연다.

## 1. Problem Statement

Execution Result가 만들어진 뒤, 그것을 누가 이어받아 무엇을 하는지는
Execution Layer 안팎 어떤 문서에도 결정된 바 없다. `Pipeline`은
Execution Result를 호출자에게 반환할 뿐이며(§0 인용), 그 반환값을
받는 쪽이 누구인지는 Pipeline의 Contract 밖이다.

## 2. Evidence Summary

| 문서 | 관찰된 사실 |
|---|---|
| `ARTIFACT-STANDARD-v1.md` "Artifact 6" | `Consumer: 아직 없음` — MVP-0006 구현 이후에도 변하지 않음(§0 인용). |
| Kernel `RFC-0001-jarvis-os-core-baseline.md` 86행("Status: Resolved") | *"Kernel는 Specification, Context, Execution Result, Event 같은 공통 Artifact만 다룬다."* Execution Result가 Kernel이 다루는 공통 Artifact의 예로 이름이 올라 있으나, "다룬다"가 저장인지 전파인지 다른 처리인지는 이 문장이 특정하지 않는다. |
| Kernel `ADC-0001-core-baseline.md` Module 3(Memory) | **Decision: Defer.** 근거: "MVP-0005~0008은 모두 지역 변수/문자열 덧붙이기라는 동일한 단일 경로만 사용했고... 승격을 정당화할 두 번째 경로나 영속화 필요 사례가 관찰된 적이 없다." Memory가 Kernel Module로 아직 Accept되지 않았다. |
| Kernel `ADC-0001-core-baseline.md` Module 4(Execution Layer) | **Decision: Accept(ADR Required).** 그러나 Risks: *"내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model Routing)는 `docs/03_adc/ADC.md`의 ADC-01·ADC-02가 여전히 Open으로 남겨 두었으므로, 이 Accept를 'Execution Layer의 설계가 결정되었다'는 의미로 확장 해석하면 안 된다."* Execution Layer가 Kernel Module로 존재한다는 것만 결정됐고, 그 내부에서 Execution Result를 누가 처리하는지는 다루지 않는다. |
| Kernel `ADC-0001-core-baseline.md` Module 5(Event Bus) | **Decision: Defer.** 근거: *"Event Bus는 이번 5개 Module 중 유일하게 Development HQ에서 단 한 건의 반복 관찰도 없는 Module이다... Phase 1 전체를 통틀어 단 한 번도 실행된 적이 없다."* |
| `RFC-0005-development-hq-execution-boundary.md` §2 결론 | *"Execution Layer는 Implementation Specification을 입력으로 받아... 코드를 실제로 실행·테스트하는 것, 그리고 그 실행을 담당할 Model/Agent를... 선택·호출하는 것까지 포함한다."* Development HQ는 Execution Layer의 **상류**(Implementation Specification 생산자)로만 위치하며, 하류(결과 소비자)로 배치된 적이 없다. |
| `GOVERNANCE-REVIEW-0002-impl-stop.md` §6 A | *"'Execution Result가 필요하다'... 미확정... '자리가 예고되어 있다'와 '필요하다고 결정되었다'는 다르다."* Execution Result 자체의 필요성/존재는 이후 RFC-0002~ADR-0002·MVP-0006으로 Contract·구현이 채워졌다(이 RFC는 그 사실을 재론하지 않는다). 다만 "자리가 채워졌다"와 "그 자리를 누가 소비하는지 결정됐다"는 동일한 구분이 Consumer 질문에도 그대로 적용된다. |

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- `Consumer` 필드는 Execution Result가 Contract·구현으로 채워지기
  전후 모두 동일하게 "아직 없음"이다 — MVP-0006 구현이 이 필드를
  바꾸지 않았다.
- Kernel 수준에서 Execution Result를 소비할 수 있는 잠재적 메커니즘
  으로 이름이 오른 두 Kernel Module 후보(Memory, Event Bus)는 **둘
  다** Kernel Module 확정 단계에서 Defer됐다 — 두 Decision 모두
  같은 종류의 사유("반복 관찰 부재")를 공유한다.
- Execution Layer 자신은 Kernel Module로 Accept됐으나, 그 Accept는
  명시적으로 "내부 구조가 결정되었다"는 뜻이 아니다(Module 4
  Risks 원문).
- Development HQ는 Execution Layer보다 상류로만 위치가 확정되어
  있다(RFC-0005) — 하류(Consumer) 후보로 이름이 오른 적이 없다.
- Execution Result의 "필요성 확정"과 "소비 주체 확정"이 서로 다른
  질문이라는 논리 구조는 `GOVERNANCE-REVIEW-0002`가 이미 한 번
  사용한 구분과 동일하다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Execution Result를 누가, 어떤 방식으로 소비하는가?

Evidence에 이름이 오른 후보만 인용한다 — 이 RFC는 새 후보를 만들지
않는다.

| 후보 | 현재 상태(Evidence 기반) |
|---|---|
| Kernel Memory | Kernel Module 자체가 Defer 상태(§2) — Module이 확정되지 않은 채로 그 역할을 판단할 수 없다. |
| Kernel Event Bus | Kernel Module 자체가 Defer 상태(§2) — 동일한 이유. |
| Execution Layer 자신의 내부 처리 | Kernel Module로는 Accept됐으나 내부 구조가 별도로 Open(ADC-01·ADC-02, §2) — "Execution Layer가 소비한다"고 답하려면 그 내부 구조부터 결정되어야 한다. |

Development HQ는 후보로 포함하지 않는다 — RFC-0005가 이미 상류로만
위치를 확정했다(§2·§3).

이 RFC는 위 후보 중 어느 것이 맞는지, 혹은 셋 다 아직 판단 불가능한지
판단하지 않는다. 이 질문에 대한 판단은 ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Consumer의 실제 구현, 인터페이스, 필드.
- Memory/Event Bus/Execution Layer 내부 구조의 설계.
- Execution Result의 필드 스키마 재논의 — RFC-0002/ADC-0002/ADR-0001,
  RFC-0003/ADC-0003/ADR-0002에서 이미 결정됐다.
- `call_engine()` 실제 Engine 배선(별도 사안, `ENGINE-CONNECT-0001`).
- Execution State의 상태 전이 규칙(별도 사안).
- Kernel Module(Memory/Event Bus) 자체를 Accept/Reject하는 판단 —
  이는 Kernel 수준 ADC(`docs/architecture/core/ADC-0001-core-baseline.md`)
  의 권한이며 이 RFC의 권한이 아니다.
- 새로운 실험.

## Non-goals

- 이 RFC는 Execution Result Consumer를 결정하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — 위에 인용된 기존 문서의 내용만
  사용했다.
- 이 RFC는 후보 3개 외에 새 후보를 추가하지 않는다.
- 이 RFC는 Architecture Baseline이나 Execution Layer Artifact
  Standard v1을 변경하지 않는다.
- 이 RFC는 Execution Layer, Development HQ, Kernel의 어떤 코드도
  수정하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.
- 이 RFC는 Kernel Module(Memory/Event Bus)의 Defer 상태를 재검토하지
  않는다 — 그 재검토는 Kernel 수준 Governance의 권한이다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §4의 3개 후보 중 현재 Evidence로 Execution Result Consumer를
   확정할 수 있는지 — 세 후보 모두 Kernel 수준에서 Defer이거나
   내부 구조가 Open인 상태이므로, 이 판단은 "지금 결정할 수 있는가
   자체"를 먼저 확인해야 할 수 있다.
2. 확정할 수 없다면, 어떤 조건이 충족되어야 재검토 대상이 되는지
   (예: Memory/Event Bus의 Kernel Module Defer가 재평가되는 경우,
   또는 Execution Layer 내부 구조 Open 항목(ADC-01·ADC-02)이
   해소되는 경우) 기존 문서에 이미 기록된 재평가 조건만 인용해
   정리한다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance 절차를
통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ARTIFACT-STANDARD-v1.md`,
  RFC-0002~ADR-0002, IMPL-STOP-0001·0002, Kernel RFC-0001·ADC-0001,
  RFC-0005, GOVERNANCE-REVIEW-0002에 실제로 기록된 내용만 인용했다.
  새 실험은 수행하지 않았다.
- 새 후보를 만들었는가 — **아니오**. Kernel Baseline·ADC-0001이
  이미 이름을 올린 Memory/Event Bus/Execution Layer 내부 처리
  3개만 인용했고, Development HQ는 후보에서 제외한 근거(RFC-0005)
  를 명시했다.
- 해결책을 제안했는가 — **아니오**. Boundary Question은 질문
  형태로만 남겼고, 3개 후보 중 어느 것도 판단하지 않았다.
- Kernel Module(Memory/Event Bus)의 Defer 상태를 재판단했는가 —
  **아니오**. 현재 상태를 인용만 했다.
- Architecture를 변경했는가 — **아니오**.
- Execution Layer/Kernel을 구현했는가 — **아니오**.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(Consumer 구현, Memory/Event Bus/Execution Layer
  내부 설계, 필드 스키마 재논의, Engine 배선, State 전이 규칙,
  Kernel Module Accept/Reject 판단, 새 실험)을 다뤘는가 — **아니오**.
