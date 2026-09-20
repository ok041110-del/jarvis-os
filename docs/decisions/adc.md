---
document_id: LEDGER-ADC
title: ADC 통합 원장
type: Ledger
target_domain: Governance
status: Active
decision_group: LEDGER
parent_documents:
  - docs/decisions/rfc.md
related_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adr.md
  - docs/decisions/open_decision.md
  - docs/decisions/adc/ADC.md
evidence_references: []
source_path: docs/decisions/adc.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# ADC 통합 원장

## 1. 작성 목적

ADC(Architecture Decision Candidate)는 RFC에서 제기된 논의 중 실제로
결정이 필요하다고 판단된 항목이다. 저장소에는 이미 도메인별 ADC 목록이
개별적으로 존재한다(`docs/decisions/adc/ADC.md`(Kernel 수준 ADC-01~12),
`docs/governance/adc/ADC-000X.md`, `docs/architecture/core/ADC-000X-*.md`,
`docs/core/execution-layer/ADC-000X-*.md`). 이 원장은 그 목록들을
대체하지 않고, 도메인을 가로질러 조회 가능한 색인 한 장을 추가로
제공한다.

**주의**: `docs/decisions/adc/ADC.md`(대문자, `adc/` 디렉터리 내부)는
Kernel 수준 Open Decision 12건을 다루는 기존 문서이며, 이 원장
(`docs/decisions/adc.md`, 소문자, `decisions/` 바로 아래)과 이름이
비슷하지만 별개의 문서다. 기존 `ADC.md`는 수정하지 않는다.

## 2. 필드 설명

| 필드 | 설명 | 필수 |
|---|---|---|
| Document ID | 트리 내부 고유 ID(예: `ADC-0005`, `ADC-01`). 트리마다 채번 규칙이 다를 수 있어 Target Domain과 조합해야만 전역적으로 유일하다 | Y |
| Title | 문서 제목 | Y |
| Type | 이 원장에서는 항상 `ADC` | Y |
| Target Domain | `Kernel` / `Development HQ` / `Execution Layer` / `Investment HQ` / `Governance` | Y |
| Status | `Open` / `Resolved` — `docs/decisions/adc/README.md`의 정의를 그대로 따름. Resolved 시에도 항목은 삭제하지 않고 상태만 갱신 | Y |
| Decision Group | 이 ADC를 낳은 RFC, 종결시키는 ADR과 같은 그룹 ID를 공유(예: `DG-DEVHQ-0007`) | Y |
| Parent Documents | 이 ADC의 근거가 된 RFC Document ID + 경로 | N(있으면 필수) |
| Related Documents | 이 ADC를 종결시킨 ADR, 또는 병렬 Open Decision 경로 | N |
| Evidence References | 판단 근거가 된 `docs/research/`·`docs/01_mvp/` 문서 | N |
| Source Path | 실제 ADC 파일의 저장소 상대 경로 | Y |
| Last Verified | 마지막 검증 날짜 | Y |
| Verification Confidence | `High` / `Medium` / `Low` | Y |

## 3. 작성 규칙

- 신규 ADC는 채택 기준(`docs/decisions/adc/README.md` §채택 기준)을
  통과한 경우에만 이 원장에 등록한다.
- Parent Documents에는 반드시 근거 RFC를 적는다. RFC 없이 발생한 ADC
  (Architecture Owner 직접 지시 등)는 Parent Documents를 `없음(직접 지시)`로
  명시하고 추론해서 채우지 않는다.
- 우선순위(NOW/NEXT/LATER)는 이 원장의 필드가 아니다 — 기존
  `docs/decisions/adc/ADC.md`가 우선순위를 계속 관리하며, 이 원장은
  Status/Decision Group/Relationship 조회에 집중한다.
- Status를 Resolved로 바꿀 때는 반드시 Related Documents에 종결 ADR을
  함께 채운다. ADR 없이 Resolved로 표기하지 않는다.

## 4. 문서 템플릿

```markdown
| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADC-XXXX | | ADC | | Open | DG-XXX-XXXX | | | | | YYYY-MM-DD | |
```

## 5. 작성 예시

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADC-0005 | Structure v1.0 Migration Decisions | ADC | Development HQ | Resolved | DG-DEVHQ-0006 | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | 본문 참조 | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | 2026-09-20 | High |

## 6. 등록 현황

> 이 원장 도입 이후 신규 작성되는 ADC와, 우선순위 검증을 거쳐 소급
> 등록된 ADC를 함께 관리한다. 기존 ADC 전체 목록은 여전히 도메인별
> 원본 문서(`docs/decisions/adc/ADC.md`, `docs/governance/adc/`,
> `docs/architecture/core/`, `docs/core/execution-layer/`)가 Source of
> Truth다. `docs/architecture/core/`(Kernel 수준 ADC-0001~0046)는 이번
> 라운드에서 검증 대상에서 제외했다 — 근거는
> `docs/decisions/REGISTRATION-CANDIDATES-0001.md` §3.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADC-0001 | Spec-Repository Artifact Drift — Kernel 책임 여부 판단 | ADC | Execution Layer | Resolved(Not Accepted, No ADR Required) | DG-EXECLAYER-0001 | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | 없음(ADR 불필요) | 본문 참조(RFC-0001 인용 Evidence 동일) | `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | 2026-09-20 | High |
| ADC-0002 | Execution Result Contract — 3개 후보 판단 | ADC | Execution Layer | Resolved(Accepted: Candidate 2 — 산출물 목록) | DG-EXECLAYER-0002 | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | 본문 참조 | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | 2026-09-20 | High |
| ADC-0003 | Execution Result Item Schema — 항목 타입 판단 | ADC | Execution Layer | Resolved(Accepted: `list[str]`) | DG-EXECLAYER-0003 | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | 본문 참조 | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | 2026-09-20 | High |
| ADC-0004 | Execution Result Consumer — 결정 가능성 판단 | ADC | Execution Layer | Resolved(Not Accepted, No ADR Required) | DG-EXECLAYER-0004 | `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | 없음(ADR 불필요) | 본문 참조(Kernel `ADC-0001-core-baseline.md` Module 4 인용) | `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | 2026-09-20 | High |
| ADC-0005 | Engine 연결 Boundary — 허용 여부 판단 | ADC | Execution Layer | Resolved(부분 Accept: caller 수준 연결 Q0 Accept / Execution Layer 내부 호출 Q1 Not Accepted, 양쪽 다 No ADR Required) | DG-EXECLAYER-0005 | `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | 없음(ADR 불필요) | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`, `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md` | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | 2026-09-20 | High |

## 7. 검증 기준

- [ ] Document ID + Target Domain 조합이 전역적으로 유일한가
- [ ] Parent Documents(근거 RFC)가 실제로 존재하고 경로가 정확한가
- [ ] Status가 Resolved라면 Related Documents에 종결 ADR이 채워졌는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Last Verified가 갱신됐는가
