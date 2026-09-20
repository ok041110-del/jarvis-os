---
document_id: REGISTRATION-CANDIDATES-0001
title: Core Document Ledger Registration — 1차 검증·등록 라운드 기록
type: Research
target_domain: Governance
status: Complete
decision_group: LEDGER
parent_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adc.md
  - docs/decisions/adr.md
  - docs/decisions/open_decision.md
related_documents:
  - docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md
  - docs/core/execution-layer/RFC-0002-execution-result-contract.md
  - docs/core/execution-layer/RFC-0003-execution-result-item-schema.md
  - docs/core/execution-layer/RFC-0004-execution-result-consumer.md
  - docs/core/execution-layer/RFC-0005-engine-connection-boundary.md
  - docs/01_mvp/MVP-0049-observation.md
  - docs/01_mvp/MVP-0050-observation.md
  - docs/01_mvp/MVP-0051-observation.md
  - docs/01_mvp/MVP-0052-observation.md
evidence_references: []
source_path: docs/decisions/REGISTRATION-CANDIDATES-0001.md
last_verified: 2026-09-20
verification_confidence: High
---

# Core Document Ledger Registration — 1차 검증·등록 라운드 기록

## 1. 목적과 범위 축소 사유

PR #213으로 통합 원장 4개(`docs/decisions/{rfc,adc,adr,open_decision}.md`)와
Research Index(`docs/research/README.md`)가 main에 반영된 뒤, 우선순위
높은 기존 문서를 본문 검증 후 원장에 등록하는 첫 라운드다.

지시된 검토 우선순위 1~3(`docs/01_mvp/`, `docs/architecture/`,
`docs/core/execution-layer/`) 중, 실제로 본문 검증까지 완료해 원장에
등록한 대상은 **`docs/core/execution-layer/`** 트리(RFC-0001~0005,
ADC-0001~0005, ADR-0001~0002, 총 12건)로 범위를 축소했다. 사유:

- `docs/architecture/core/`(Kernel 수준)는 RFC 44건, ADC 46건, ADR
  28건 규모로, 이번 라운드에서 전수 본문 대조가 불가능하다. 특히 이
  트리는 기존 `docs/decisions/rfc/README.md`가 이미 지적한 "헤더
  `Status`가 대부분 `Proposed`로 고정되고 실제 상태와 다른" 문제
  (D-9 색인 부채)를 그대로 안고 있어, 건별 본문 대조 없이는 Status를
  확정할 수 없다 — 지시 §5 "본문에서 확인되지 않은 필드는 확정하지
  않는다"에 따라 이번 라운드에서는 제외하고 다음 라운드로 넘긴다.
- `docs/core/execution-layer/`는 RFC/ADC/ADR이 각 5건 이하로 작고,
  각 RFC 헤더에 실제 종결 상태(`Resolved — ADC-000X로 종결됨(...)`)가
  명시되어 있어 본문 대조 부담이 낮고 오류 가능성도 낮다. 유일한
  예외(RFC-0005 헤더가 `Proposed`로 미갱신된 것)는 ADC-0005 본문을
  직접 읽어 실제 Decision(부분 Accept)을 확인했다(§2 참조).

## 2. 확정 등록 — Execution Layer (12건)

아래 문서는 원문을 직접 읽고 Status·Decision·Related Documents를
확인한 뒤 각 원장에 등록했다. 상세 필드는 원장 본체를 참조한다.

| Document ID | Type | Source Path | 등록 원장 |
|---|---|---|---|
| RFC-0001 | RFC | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | `docs/decisions/rfc.md` §6 |
| RFC-0002 | RFC | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | `docs/decisions/rfc.md` §6 |
| RFC-0003 | RFC | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | `docs/decisions/rfc.md` §6 |
| RFC-0004 | RFC | `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | `docs/decisions/rfc.md` §6 |
| RFC-0005 | RFC | `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | `docs/decisions/rfc.md` §6 |
| ADC-0001 | ADC | `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | `docs/decisions/adc.md` §6 |
| ADC-0002 | ADC | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | `docs/decisions/adc.md` §6 |
| ADC-0003 | ADC | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | `docs/decisions/adc.md` §6 |
| ADC-0004 | ADC | `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | `docs/decisions/adc.md` §6 |
| ADC-0005 | ADC | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | `docs/decisions/adc.md` §6 |
| ADR-0001 | ADR | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | `docs/decisions/adr.md` §6 |
| ADR-0002 | ADR | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | `docs/decisions/adr.md` §6 |

**특기 사항 — RFC-0005 헤더 불일치**: RFC-0005 파일 헤더는
`**Status**: Proposed (검토 대상, 결정 아님)`이라고 적혀 있으나,
`ADC-0005-engine-connection-boundary.md`를 직접 읽은 결과 이미
Decision(§Q0 Accept / §Q1 Not Accepted, 양쪽 다 No ADR Required)이
내려져 있음을 확인했다. 원장에는 헤더 라벨이 아니라 이 본문 확인
결과를 Status로 기록했고("Resolved(헤더 라벨은 Proposed로 미갱신…)"),
RFC-0005 파일 자체는 수정하지 않았다(지시 §7 "기존 문서 본문 수정
금지").

Open Decision 원장에는 이번 라운드에서 확정 등록한 항목이 없다 —
Execution Layer 트리의 5개 RFC 모두 ADC까지 진행되어 있어 Open
Decision 단계에 머무른 문서가 없었다.

## 3. 보류 — docs/architecture/core (Kernel, 118건 규모)

RFC-0001~0044, ADC-0001~0046, ADR-0001~0028(및 다수의 EVIDENCE/
GOVERNANCE-REVIEW/CLOSURE 문서)를 이번 라운드에서 열람은 했으나
(§1 참조), 건별 본문 대조·Status 확정까지는 진행하지 않았다. 확정
등록하지 않고 원장에도 올리지 않았다 — 지시 §7 "판단이 불확실하면
범위를 축소"에 따른 결정이다. 다음 라운드에서 이 트리만 대상으로
별도 작업을 진행하는 것을 제안한다.

## 4. MVP 문서 — Evidence Reference 후보 (docs/01_mvp/)

지시에 따라 MVP-0049~0052 4건을 우선 검토했다. 4건 모두 파일 첫
문단에서 스스로 **"문서 성격: 실제 실행 기록(Evidence)"**라고 명시하고
있으며, RFC/ADC/ADR 어느 쪽으로도 스스로를 분류하지 않는다. 본문에서
RFC/ADC/ADR과의 명시적 연결이 확인되지 않으므로, 지시 §6 원칙에 따라
Decision Register(RFC/ADC/ADR/Open Decision)에는 등록하지 않고
**Evidence Reference 후보**로만 아래에 기록한다.

| Document ID | Title | Plan/Observation/Evidence 구분 | Status(본문 판정) | Source Path |
|---|---|---|---|---|
| MVP-0049 | MVP-0049 Observation | Evidence(Observation) | 완료 — Capability 지시문 최소 수정 Prototype, Architecture/Contract 불변 | `docs/01_mvp/MVP-0049-observation.md` |
| MVP-0050 | MVP-0050 Observation (Phase 10 Prototype #1) | Evidence(Observation) | 완료 — Failure로 판정(다음 MVP-0051로 이어짐), Architecture/Contract 불변 | `docs/01_mvp/MVP-0050-observation.md` |
| MVP-0051 | MVP-0051 Observation (Phase 10 Prototype #2) | Evidence(Observation) | 완료 — Success로 판정, Architecture/Contract 불변 | `docs/01_mvp/MVP-0051-observation.md` |
| MVP-0052 | MVP-0052 Observation (Phase 10 Boundary Validation) | Evidence(Observation) | 완료 — Success(경계 검증), 단 "탐지 재현율 편차" 별도 관찰(§5) | `docs/01_mvp/MVP-0052-observation.md` |

이 4건에 대해 MVP → RFC / MVP → ADC / MVP → ADR 관계를 임의로 생성하지
않았다(지시 §6 금지 사항). 4건 모두 원문에 그런 연결을 주장하는
서술이 없다.

## 5. Open Issue 후보 — MVP-0052 탐지 재현율 편차

MVP-0052 본문(§2, L60~83)은 "같은 잠재 결함을 Engine이 매번 알아채는
것은 아니다"라는 **탐지 재현율(detection recall) 편차**를 관찰로
기록했다. 그러나 같은 문서의 §Governance(L99~104)는 이를 스스로
다음과 같이 판정한다:

> "RFC/ADC/ADR 불필요. 탐지 재현율 편차는 '단일 stochastic Engine
> 호출의 본질적 특성'으로 판단한다 — 지금 Specification/Contract를
> 설계할 근거로 쓰지 않는다(NEED-DRIVEN DEFER)."

이 판정은 문서 자신의 결론이며, 이번 등록 작업이 별도로 확정한 것이
아니다. 지시 §6 "MVP-0052의 탐지 재현율 편차는 별도 Open Issue
후보로 검토하되, 본문 근거 없이 확정하지 않는다"에 따라, 이 관찰을
**Open Issue 후보**로만 기록하고 `docs/decisions/open_decision.md`에는
등록하지 않는다(문서 자신이 RFC/ADC/ADR 불필요·DEFER로 판정했으므로,
Open Decision으로 승격할 본문 근거가 없다). 재검토가 필요해지는
조건은 MVP-0052 원문의 판정 그대로다 — 새 Evidence 없이 이 판정을
뒤집지 않는다.

## 6. 검증 방법

- 각 문서를 `Read` 도구로 직접 열람해 헤더의 `**Status**` 라벨과
  본문의 `## Decision`/`### Q0·Q1 결론` 절을 대조했다.
- Related Documents/Parent Documents에 적은 경로는 전부 실제 파일
  존재를 `ls`로 확인했다.
- Evidence References 중 "본문 참조"로 표기한 항목은 해당 ADC/ADR
  본문이 직접 인용한 Evidence 목록을 그대로 옮긴 것이며, 이번 라운드
  에서 그 Evidence 원문(예: `ENGINE-INTEGRATION-0001`)까지 개별
  대조하지는 않았다 — 그래서 RFC-0001의 Verification Confidence는
  Evidence 원문 미대조를 반영해 `High`로 유지하되(본문 자체는 대조),
  이 한계를 이 문서에 기록해 둔다.

## 7. Self Review

- 기존 문서를 수정했는가 — **아니오**(원장 4개 파일의 §6 등록 현황
  표만 갱신, 신규 후보 문서 1건 추가).
- 기존 Document ID/파일명/번호를 변경했는가 — **아니오**.
- RFC/ADC/ADR 관계를 추정으로 생성했는가 — **아니오**(모두 원문에서
  직접 확인).
- MVP → RFC/ADC/ADR 관계를 임의로 만들었는가 — **아니오**.
- Architecture Baseline/Public Contract를 변경했는가 — **아니오**.
- 검증되지 않은 문서를 원장에 확정 등록했는가 — **아니오**(Kernel
  트리는 후보에도 올리지 않고 §3에 보류로만 기록).
