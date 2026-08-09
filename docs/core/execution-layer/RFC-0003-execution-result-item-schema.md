# RFC-0003: Execution Result Item Schema — 목록 항목의 형태

**Status**: Resolved — `ADC-0003-execution-result-item-schema.md` → `ADR-0002-execution-result-item-schema.md`로 종결됨. RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (Execution Result Builder 구현 시도 후속)
**Evidence**: `docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md`,
`docs/core/execution-layer/ADC-0002-execution-result-contract.md`,
`docs/core/execution-layer/ADR-0001-execution-result-contract.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`core/execution_layer/mvp_0001~0005/*.py`(기존 5개 Builder 소스)

> 본 RFC는 Execution Result 목록 항목의 해결책(어떤 타입을 채택할지)을
> 제시하지 않는다. 본 RFC는 `IMPL-STOP-0002`가 이미 기록한 Evidence만
> 근거로 질문과 후보를 정리한다. 새 실험을 하지 않는다. 새 후보를
> 만들지 않는다. Architecture를 변경하지 않는다. Execution Layer를
> 구현하지 않는다.

## 0. 이 RFC가 열린 이유

`docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md`
는 Execution Result Builder(`core/execution_layer/mvp_0006`, 미생성)
구현 시도가 Builder 함수 시그니처 정의 단계, 정확히는 첫 매개변수
(`results`, 산출물 목록)의 항목 타입을 결정해야 하는 지점에서
Stop Trigger 2를 재발동시키며 중단됐음을 기록했다.

`ADC-0002`가 "형태(shape)" — Execution Result는 산출물 목록(list)을
담는다 — 를 이미 결정했고 `ADR-0001`이 그 형태를
`ARTIFACT-STANDARD-v1.md`에 반영했지만, **목록의 각 항목이 무엇인지**
는 두 문서 모두 명시적으로 판단 범위 밖으로 남겨두었다
(`IMPL-STOP-0002` §2 E-1·E-2). 이 RFC는 그 다음 절차로서, 같은
Evidence를 근거로 정식 Architecture 논의를 연다.

## 1. Problem Statement

`ADC-0002`·`ADR-0001`이 결정한 것은 Execution Result가 "목록"이라는
**컨테이너 형태**뿐이다. Builder를 실제로 구현하려면 그 목록의
**항목 하나하나가 어떤 타입인지**를 추가로 결정해야 한다. 이 결정
없이는 `build_execution_result()`의 `results` 매개변수 타입을 쓸 수
없다(`IMPL-STOP-0002` §1).

## 2. Evidence Summary

| 문서 | 관찰된 사실 |
|---|---|
| `ADC-0002-execution-result-contract.md` §목적 | "이 ADC가 답하지 않는 것"에 "채택된 후보의 실제 필드 구성(이름, 타입, 개수)", "산출물 항목의 타입 스키마(파일/로그/텍스트 보고를 어떻게 구분하는지)"를 명시적으로 포함시켰다. |
| `ADR-0001-execution-result-contract.md` §Out of Scope | "목록 항목의 실제 필드 스키마(타입, 이름, 개수 제한)"를 "ADC-0002 '이 ADC가 답하지 않는 것' — Contract 상세는 후속 구현/추가 ADR 대상"으로 명시했다. |
| `ARTIFACT-STANDARD-v1.md` "Artifact 6: Execution Result" | `Canonical Fields \| 미정(ADC-0002 범위 밖) — 목록 항목의 타입 스키마는 후속 결정 대상.` |
| `IMPL-STOP-0002` §2 E-3 | `results` 타입 후보를 전수 검토했다 — 두 후보(`list[str]`, `list[dict]`) 모두 새 Contract 결정이 필요함을 확인했고, 별도로 "빈 목록 허용 여부/최소·최대 개수"라는 세 번째 종류의(항목 타입과는 다른) 검증 규칙 질문도 식별했다. |
| `core/execution_layer/mvp_0001~0005/*.py`(전수 확인) | 5개 Builder의 함수 시그니처를 전수 확인한 결과, 입력·출력·모든 keyword 메타데이터 인자가 예외 없이 `str`이다 — `build_execution_request(implementation_specification: str) -> str`, `build_prompt_specification(execution_request: str) -> str`, `build_model_request(prompt_specification: str, *, request_id: str, created_at: str) -> str`, `build_execution_handle(model_request: str, *, handle_id: str, submitted_at: str) -> str`, `build_execution_state(execution_handle: str, *, handle_id: str, state: str, changed_at: str) -> str`. 구조화(dict/list/객체) 타입의 필드는 5개 Builder 전체에서 한 건도 없다. |

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- `ADC-0002`·`ADR-0001` 두 문서 모두, 독립적으로, "항목의 실제
  타입/필드 스키마"를 명시적으로 자신의 판단 범위 밖에 두었다 —
  우연이 아니라 두 문서가 같은 경계를 일관되게 지켰다는 사실이다.
- 기존 5개 Builder의 모든 필드는 예외 없이 `str`이다(§2 표,
  전수 확인) — 구조화 타입(dict 등)이 Baseline 어디에도 선례가
  없다.
- `IMPL-STOP-0002`가 식별한 항목 타입 후보는 정확히 둘이다:
  `list[str]`(opaque 문자열)과 `list[dict]`(구조화 레코드). 이
  둘은 서로 다른 종류의 결정을 요구한다 — 전자는 "항목이
  문자열이라는 사실 하나", 후자는 "항목의 필드 이름·타입·그
  필드들이 구분하는 산출물 종류(파일/로그/텍스트 보고 등)"라는
  복수의 사실.
- "빈 목록 허용 여부/개수 제한"은 항목 **타입**과는 다른 종류의
  질문으로 `IMPL-STOP-0002`가 별도로 식별했다 — 이 RFC는 이를
  같은 질문으로 섞지 않는다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Execution Result 목록의 각 항목은 어떤 타입인가?

`IMPL-STOP-0002` §2 E-3이 이미 식별한 2개 후보를 그대로 인용한다 —
이 RFC는 새 후보를 만들지 않는다.

| 후보 | 무엇을 결정하게 되는가(`IMPL-STOP-0002` §2 E-3 인용) |
|---|---|
| `list[str]`(opaque, caller가 이미 직렬화한 문자열) | "항목은 문자열이다"라는 최소 스키마 결정 |
| `list[dict]`(type/source/content 등 구조화 레코드) | 명백한 새 스키마 결정 — "파일/로그/텍스트 보고를 어떻게 구분하는지" 그 자체 |

이 RFC는 이 중 어느 것이 맞는지 판단하지 않는다. 이 질문에 대한
판단은 ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- 항목 타입의 실제 선택(`list[str]` 대 `list[dict]` 판단).
- 목록의 빈 목록 허용 여부, 최소/최대 개수 — `IMPL-STOP-0002` §2
  E-3이 항목 타입과 별개 질문으로 식별했으며, 이 RFC의 Boundary
  Question이 아니다.
- `list[dict]`를 채택했을 때의 실제 필드 이름·타입(`type`,
  `source`, `content` 등의 구체적 스키마).
- Execution Result Builder의 구현.
- Candidate 3(Reference, `ADC-0002` Q1에서 이미 Not Accepted)의
  재논의.
- `call_engine()`의 실제 Engine 배선, Execution State의 상태 전이
  규칙(별도 사안).
- 새로운 실험(Engine 산출물의 실제 타입을 직접 재관찰하는 것 포함).

## Non-goals

- 이 RFC는 Execution Result Item Schema를 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `IMPL-STOP-0002`,
  `ADC-0002`, `ADR-0001`, `ARTIFACT-STANDARD-v1.md`, 5개 Builder
  소스에서 이미 확인된 사실만 인용했다.
- 이 RFC는 2개 후보 외에 새 후보를 추가하지 않는다.
- 이 RFC는 Architecture Baseline이나 Execution Layer Artifact
  Standard v1을 변경하지 않는다.
- 이 RFC는 Execution Layer, Development HQ의 어떤 코드도 수정하지
  않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음 하나만 판단하도록 제안한다.

1. §4의 2개 후보(`list[str]` / `list[dict]`) 중 Execution Result
   목록 항목의 타입으로 채택할 것.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance 절차를
통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `IMPL-STOP-0002`, `ADC-0002`,
  `ADR-0001`, `ARTIFACT-STANDARD-v1.md`, 5개 Builder 소스에 실제로
  기록된 내용만 인용했다. 새 실험은 수행하지 않았다.
- 새 후보를 만들었는가 — **아니오**. `IMPL-STOP-0002` §2 E-3의 2개
  후보를 그대로 인용했다.
- 해결책을 제안했는가 — **아니오**. Boundary Question은 질문
  형태로만 남겼고, 2개 후보 중 어느 것도 판단하지 않았다.
- Architecture를 변경했는가 — **아니오**.
- Execution Layer를 구현했는가 — **아니오**.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(항목 타입 선택, 개수 검증 규칙, `list[dict]`
  세부 필드, Builder 구현, Candidate 3 재논의, call_engine 배선,
  Execution State 전이 규칙, 새 실험)을 다뤘는가 — **아니오**.
