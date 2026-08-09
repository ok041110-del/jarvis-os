# RFC-0002: Execution Result Contract — 산출물을 묶는 방식

**Status**: Resolved — `ADC-0002-execution-result-contract.md` → `ADR-0001-execution-result-contract.md`로 종결됨. RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (Execution Layer Governance Priority Review 후속)
**Evidence**: `docs/core/execution-layer/IMPL-STOP-0001-execution-result.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`docs/research/ENGINE-INTEGRATION-0001-Claude-Code.md`,
`docs/research/ENGINE-INTEGRATION-0002-Claude-Code.md`,
`docs/research/ENGINE-INTEGRATION-0003-Claude-Code.md`

> 본 RFC는 Execution Result의 해결책(3개 후보 중 선택)을 제시하지
> 않는다. 본 RFC는 기존 Evidence(`IMPL-STOP-0001`, `ARTIFACT-STANDARD-v1`,
> `ENGINE-INTEGRATION-0001~0003`)만 근거로 질문과 후보를 정리한다. 새
> 실험을 하지 않는다. 새 후보를 만들지 않는다. Architecture를
> 변경하지 않는다. Execution Layer를 구현하지 않는다.

## 0. 이 RFC가 열린 이유

`docs/core/execution-layer/IMPL-STOP-0001-execution-result.md`는
Execution Layer의 여섯 번째 Artifact(Execution Result)를 구현하려던
작업이 착수 전 단계에서 Stop Trigger 2("기존 Artifact Standard만으로
Contract를 결정할 수 없는 경우")를 발동시키며 중단됐음을 기록했다.
그 중단은 세 가지 Evidence로 뒷받침된다.

- 기존 5개 Builder의 metadata 필드 13개를 전수 분류한 결과, 예외 없이
  identity/time/모듈 상수/상류 canonical 재사용/소형 enum 다섯 종류
  중 하나였고 **content 필드는 0건**이었다(`IMPL-STOP-0001` §2 E-1).
- `ARTIFACT-STANDARD-v1.md`는 Execution Result 설계를 명시적으로
  거부했다 — "이 문서는 그 자리를 예고만 할 뿐 설계하지 않는다"(8·149행,
  `IMPL-STOP-0001` §2 E-2).
- `ENGINE-INTEGRATION-0001~0003` 세 실험 모두 동일한 질문을 각각
  "Unknown"으로 기록했다 — "여러 개별 산출물을 하나의 단일 Execution
  Result Artifact로 묶는 방식"(`IMPL-STOP-0001` §2 E-3).

`IMPL-STOP-0001`은 구현 중단 기록(Observation)이며 Architecture 문서가
아니다. 그 문서는 스스로 "이 문서는 그 다음에 무엇을 해야 하는지
판단하지 않는다"(§9)고 명시했다. 이 RFC는 그 다음 절차로서, 같은
Evidence를 근거로 정식 Architecture 논의를 연다.

## 1. Problem Statement

Execution Layer의 Artifact Chain(`ARTIFACT-STANDARD-v1.md`)은 5개
Builder(Execution Request → Prompt Specification → Model Request →
Execution Handle → Execution State)까지 Baseline으로 고정돼 있다.
Execution State의 Consumer 칸은 비어 있다 — 여섯 번째 Artifact인
Execution Result를 소비할 지점이 아직 없다
(`ARTIFACT-STANDARD-v1.md` Artifact 5 "Consumer: 아직 없음").

Execution Result는 이름과 체인 위치상 "실행이 만들어 낸 것"을 담아야
하는 자리이며, 이는 기존 5개 Builder의 패턴(Wrap, not rewrite — 입력
Artifact를 verbatim으로 감싸고 메타데이터만 추가)이 처음으로 적용되지
않는 자리다. 기존 패턴에는 "만들어진 내용(content)"을 담는 사례가 없기
때문이다(`IMPL-STOP-0001` §2 E-1).

**Observation Count = 3**

`ENGINE-INTEGRATION-0001~0003` 세 실험 모두 Execution Layer 5개
Builder 밖에서, Engine(Claude Code)이 실제로 만들어내는 산출물의 형태를
관찰했다. 세 실험 모두 "여러 개별 산출물을 하나의 Execution Result로
묶는 방식"에 답하지 못한 채 Unknown으로 남겼다는 사실이 반복됐다.

## 2. Evidence Summary

| 실험/문서 | 관찰된 산출물 | Execution Result로의 결합 여부 |
|---|---|---|
| `ENGINE-INTEGRATION-0001` | 신규 파일, 로그, 텍스트 보고 등 "여러 개별 산출물" | 관찰되지 않음 — "Observed Claude Output → Candidate Execution Result: Unknown"(157~160행) |
| `ENGINE-INTEGRATION-0002` | 파일 수정, diff, 진단 로그, 텍스트 보고 | 여전히 Unknown(213~215행) |
| `ENGINE-INTEGRATION-0003` | (동일 계열 산출물) | 여전히 Unknown(244~245행) |
| `ARTIFACT-STANDARD-v1.md` | 5개 Builder의 metadata 필드 13개 전수 | content 필드 0건 — Execution Result가 참조할 기존 패턴이 없음(`IMPL-STOP-0001` §2 E-1) |

## 3. Pattern

세 실험과 두 Standard/Stop 문서에서 반복된 사실만 정리한다. 새 사실을
추가하지 않는다.

- Engine이 실제로 만들어내는 산출물은 단일 텍스트가 아니라 "여러 개별
  산출물"(신규/수정 파일, diff, 로그, 텍스트 보고)로 관찰됐다(세 실험
  공통).
- 그 여러 산출물을 하나의 Execution Result Artifact로 묶는 방식은 세
  번의 독립된 관찰에서 한 번도 답이 나오지 않았다 — 부재가 아니라
  반복 기록된 Unknown이다(`IMPL-STOP-0001` §2 E-3).
- 기존 5개 Builder의 Contract 패턴(identity/time/모듈 상수/상류
  canonical 재사용/소형 enum)은 이 질문에 적용할 선례를 제공하지
  않는다(`IMPL-STOP-0001` §2 E-1).
- `ARTIFACT-STANDARD-v1.md`는 이 질문에 답하는 것을 자신의 범위 밖으로
  이미 명시해 두었다(`IMPL-STOP-0001` §2 E-2).

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

여러 Engine 산출물을 하나의 Execution Result로 어떻게 묶는가?

`IMPL-STOP-0001` §2 E-4가 이미 나열한 3개 후보를 그대로 인용한다 —
이 RFC는 새 후보를 만들지 않는다.

| 후보 | 무엇을 결정하게 되는가(`IMPL-STOP-0001` §2 E-4 인용) |
|---|---|
| 단일 불투명 문자열 | 산출물이 하나의 텍스트로 환원 가능하다는 결정 |
| 산출물 목록 | Artifact가 복수 항목을 담는 첫 사례 — 5개 Builder의 단일 텍스트 구조를 벗어난다 |
| 참조만 담고 내용은 밖 | 저장 위치가 필요해진다 → Memory 영역(Defer) |

이 RFC는 이 중 어느 것이 맞는지 판단하지 않는다. 이 질문에 대한 판단은
ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Execution Result의 실제 Contract(필드, 구조) 확정.
- 3개 후보 중 선택.
- Execution Result Builder의 구현.
- `call_engine()`의 실제 Engine 배선 여부(`docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`의 판단 사항 — 이 RFC와 별개 사안).
- Execution State의 상태 전이 규칙(`ARTIFACT-STANDARD-v1.md` Artifact 5,
  전이 규칙 미검증 — 이 RFC와 별개 사안).
- Memory 영역, Runtime, Storage 설계.
- 새로운 실험(Engine 산출물을 직접 재관찰하는 것 포함).

## Non-goals

- 이 RFC는 Execution Result Contract를 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `IMPL-STOP-0001`,
  `ARTIFACT-STANDARD-v1.md`, `ENGINE-INTEGRATION-0001~0003`에서 이미
  관찰된 사실만 인용했다.
- 이 RFC는 3개 후보 외에 새 후보를 추가하지 않는다.
- 이 RFC는 Architecture Baseline이나 Execution Layer Artifact Standard
  v1을 변경하지 않는다.
- 이 RFC는 Execution Layer, Development HQ의 어떤 코드도 수정하지
  않는다.
- 이 RFC는 ADC, ADR, MVP 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음 하나만 판단하도록 제안한다.

1. §4의 3개 후보(단일 불투명 문자열 / 산출물 목록 / 참조만 담고 내용은
   밖) 중 Execution Result Contract로 채택할 것.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance 절차를
통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `IMPL-STOP-0001`,
  `ARTIFACT-STANDARD-v1.md`, `ENGINE-INTEGRATION-0001~0003`에 실제로
  기록된 내용만 인용했다. 새 실험은 수행하지 않았다.
- 새 후보를 만들었는가 — **아니오**. `IMPL-STOP-0001` §2 E-4의 3개
  후보를 그대로 인용했다.
- 해결책을 제안했는가 — **아니오**. Boundary Question은 질문 형태로만
  남겼고, 3개 후보 중 어느 것도 판단하지 않았다.
- Architecture를 변경했는가 — **아니오**.
- Execution Layer를 구현했는가 — **아니오**.
- ADC/ADR/MVP를 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(Contract 확정, 후보 선택, Builder 구현,
  call_engine 배선, Execution State 전이 규칙, Memory/Runtime/Storage
  설계, 새 실험)을 다뤘는가 — **아니오**.
