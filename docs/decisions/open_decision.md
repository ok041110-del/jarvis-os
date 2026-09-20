---
document_id: LEDGER-OPEN-DECISION
title: Open Decision 통합 원장
type: Ledger
target_domain: Governance
status: Active
decision_group: LEDGER
parent_documents:
  - docs/decisions/rfc.md
related_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adc.md
  - docs/decisions/adr.md
  - docs/decisions/OPEN-DECISION-REGISTER-TEMPLATE.md
evidence_references: []
source_path: docs/decisions/open_decision.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# Open Decision 통합 원장

## 1. 작성 목적

Open Decision은 최종 결정을 내리지 않고 추적만 하는 문서다
(`docs/decisions/OPEN-DECISION-REGISTER-TEMPLATE.md` 참조). RFC에서
제기됐지만 아직 ADC로 확정할 근거가 부족하거나, ADR 번호만 예약해 둔
채 보류된 항목이 여기 속한다. 이 원장은 도메인을 가로질러 흩어질 수
있는 Open Decision을 한 표에서 조회 가능하게 한다.

## 2. 필드 설명

| 필드 | 설명 | 필수 |
|---|---|---|
| Document ID | `OD-XXXX` 형식의 고유 ID | Y |
| Title | Decision Question 요약 | Y |
| Type | 이 원장에서는 항상 `Open Decision` | Y |
| Target Domain | `Kernel` / `Development HQ` / `Execution Layer` / `Investment HQ` / `Governance` | Y |
| Status | `Open` / `Reconsidered` / `Closed(→ADC)` / `Closed(→ADR)` — 최종 결정이 나면 Status만 갱신하고 행은 유지 | Y |
| Decision Group | 관련 RFC/ADC/ADR과 그룹 ID 공유 | Y |
| Parent Documents | 이 Open Decision을 제기한 RFC | N(있으면 필수) |
| Related Documents | 예약된 ADR 번호, 이 Open Decision을 다루는 상세 문서(Register 파일 등) | N |
| Evidence References | Required Evidence로 지정된 `docs/research/` 문서(작성 시점에 존재하지 않아도 됨 — 필요 Evidence 목록으로 기록) | N |
| Source Path | 이 Open Decision이 상세히 기록된 실제 파일 경로 | Y |
| Last Verified | 마지막 검증 날짜 | Y |
| Verification Confidence | `High` / `Medium` / `Low` | Y |

## 3. 작성 규칙

- Open Decision은 최종 결정을 내리지 않는다. 이 원장에 Status를
  `Closed`로 적더라도 실제 결정 내용은 이 원장이 아니라 해당 ADC/ADR
  문서에 기록한다 — 이 원장은 상태 추적 색인일 뿐이다.
- ADR 번호를 예약한 경우, 그 번호는 다른 의사결정 건에 재사용하지 않는다
  (`OPEN-DECISION-REGISTER-TEMPLATE.md` 작성 제한과 동일).
- MVP-0049~0052(`docs/01_mvp/MVP-00{49,50,51,52}-observation.md`)와 같이
  아직 RFC/ADC/ADR 관계가 확인되지 않은 Evidence 문서는 이 원장에
  Open Decision으로 등록하지 않는다 — Evidence Reference 후보로만
  취급하고, 관계가 실제로 확인된 뒤에만 등록한다.
- 본문 대조 없이 Status를 확정하지 않는다. 확인되지 않으면
  `Undetermined`로 남긴다.

## 4. 문서 템플릿

```markdown
| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OD-XXXX | | Open Decision | | Open | DG-XXX-XXXX | | | | | YYYY-MM-DD | |
```

## 5. 작성 예시

다음은 가상의 예시다(실제 등록 항목이 아님 — §6 참조).

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OD-EX01 | (예시) Connector 자격증명 관리 주체 | Open Decision | Kernel | Open | DG-KERNEL-EX | `docs/decisions/rfc/RFC-EXAMPLE.md` | ADR 번호 예약 없음 | 없음(향후 지정) | `docs/decisions/OPEN-DECISION-REGISTER-TEMPLATE.md` | 2026-09-20 | Low |

## 6. 등록 현황

> 이 원장 도입 이후 신규로 열리는 Open Decision부터 등록한다. 기존
> Kernel 수준 Open Decision(ADC-01~12)은 이미
> `docs/decisions/adc/ADC.md`에서 관리되고 있으며, 이 원장이 그 문서를
> 대체하지 않는다 — 소급 등록 전 원문 대조가 필요하다.
>
> 2026-09-20 검증 라운드(`docs/decisions/REGISTRATION-CANDIDATES-0001.md`)
> 에서는 `docs/01_mvp/`·`docs/core/execution-layer/` 우선 검토 범위 내에
> Open Decision으로 확정 등록할 문서가 없었다 — MVP-0052가 관찰한
> "탐지 재현율 편차"는 그 문서 자신이 "RFC/ADC/ADR 불필요·NEED-DRIVEN
> DEFER"로 명시했으므로 Open Decision으로 승격하지 않고 후보로만
> 남겼다(위 후보 문서 §2 참조).

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OD-0001 | Decision Group Registry(DG-NNNN, `ADC-0010` 기결) 도입과 이 통합 원장의 Decision Group 필드(`DG-<도메인>-NNNN`)의 관계 | Open Decision | Governance | Open | DG-DEVHQ-GOVERNANCE-0206 | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | `docs/decisions/rfc.md`, `docs/decisions/adc.md`, `docs/decisions/adr.md`(이 3개 원장이 사용 중인 Decision Group 값 전체) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md`(3차 라운드) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md` | 2026-09-20 | Medium |

### OD-0001 — Decision Group Registry와 통합 원장 Decision Group 필드의 관계

#### Decision Question

`ADC-0010`(Scoped Accept)은 fan-out/fan-in을 표현하기 위해 **전역
단일 네임스페이스** `DG-NNNN`(예: `DG-0001`)을 쓰는
`docs/governance/DECISION-GROUP-REGISTRY.md`를 "후속 구현 작업"으로
지정했다(아직 생성되지 않음). 이번 라운드에서 만든
`docs/decisions/{rfc,adc,adr}.md` 3개 원장은 이미 자체적으로
`DG-<도메인약어>-NNNN`(예: `DG-KERNEL-0001`, `DG-DEVHQ-0007`) 형식의
Decision Group 값을 200개 가까이 채워 넣었다 — `ADC-0010`이 정의한
공식 네임스페이스와 형식이 다르다. 두 체계를 어떻게 정리할지가
Open Question이다: (a) 이 원장의 값을 공식 `DG-NNNN`으로 재발급하는가,
(b) 이 원장의 값은 비공식 "그룹 힌트"로 유지하고 공식 Registry는
별도로 신설하는가, (c) `ADC-0010`을 재검토해 도메인 접두어 형식을
공식화하는가.

#### Why Open

이 질문은 `ADC-0010` 재검토 없이 이번 작업(단순 문서 검증·등록) 범위
안에서 임의로 답할 수 없다 — 어느 쪽이든 기존 Governance 절차
(RFC→ADC→ADR 또는 최소 ADC 재확인)를 거쳐야 한다. 특히 (a)는 이번
라운드에서 등록한 약 190개 행의 Decision Group 값을 전부 재발급해야
해서 "일괄 재작업" 금지 원칙과 충돌할 수 있다.

#### Required Evidence

- `docs/governance/DECISION-GROUP-REGISTRY.md`가 실제로 생성될 때
  그 설계가 도메인 접두어 형식을 허용/금지하는지.
- 이 원장의 Decision Group 값을 실제로 참조하는 코드나 문서가
  생기는지(현재는 순수 색인 필드).

#### Reconsideration Trigger

`docs/governance/DECISION-GROUP-REGISTRY.md`가 실제로 생성되는 시점,
또는 두 체계 간 참조 충돌이 실제로 관찰되는 시점.

#### Next Action

다음 라운드에서 `ADC-0010`의 "후속 구현 작업 목록" 1~2번(Registry
신설 + 이미 확인된 2개 그룹 최초 등록)을 먼저 진행할지, 이 통합
원장의 Decision Group 형식을 그대로 유지할지 사용자 판단을 받는다.

#### Related Documents

| Type | ID | Relationship |
|---|---|---|
| ADC | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | 공식 DG-NNNN 체계를 Scoped Accept로 확정, Registry 신설은 미실행 |
| Ledger | `docs/decisions/rfc.md`, `docs/decisions/adc.md`, `docs/decisions/adr.md` | 비공식 `DG-<도메인>-NNNN` 값을 이미 사용 중 |

## 7. 검증 기준

- [ ] Document ID(`OD-XXXX`)가 전역적으로 유일한가
- [ ] Status가 본문 대조 없이 확정되지 않았는가
- [ ] 예약 ADR 번호가 다른 건과 중복되지 않는가
- [ ] MVP-0049~0052 등 관계 미확인 Evidence 문서를 임의로 등록하지 않았는가
- [ ] Source Path의 파일이 실제로 존재하는가
