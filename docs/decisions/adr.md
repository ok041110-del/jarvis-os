---
document_id: LEDGER-ADR
title: ADR 통합 원장
type: Ledger
target_domain: Governance
status: Active
decision_group: LEDGER
parent_documents:
  - docs/decisions/adc.md
related_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adc.md
  - docs/decisions/open_decision.md
  - docs/decisions/adr/README.md
evidence_references: []
source_path: docs/decisions/adr.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# ADR 통합 원장

## 1. 작성 목적

ADR(Architecture Decision Record)은 ADC 중 실제로 결정된 사항을 기록하고
Architecture Baseline 반영으로 이어지는 문서다. 저장소에는 도메인별로
독립 채번된 ADR이 이미 존재한다(`docs/decisions/adr/`,
`docs/architecture/core/`, `docs/core/execution-layer/`). 이 원장은
그 문서들을 대체하지 않고, ADR이 어떤 ADC를 종결시켰고 Baseline 어디에
반영됐는지를 한 표에서 확인할 수 있게 한다.

## 2. 필드 설명

| 필드 | 설명 | 필수 |
|---|---|---|
| Document ID | 트리 내부 고유 ID(예: `ADR-0006`) | Y |
| Title | 문서 제목 | Y |
| Type | 이 원장에서는 항상 `ADR` | Y |
| Target Domain | `Kernel` / `Development HQ` / `Execution Layer` / `Investment HQ` / `Governance` | Y |
| Status | `Proposed` / `Accepted` / `Superseded` — `docs/decisions/adr/README.md` 정의를 그대로 따름 | Y |
| Decision Group | 종결시킨 ADC, 근거 RFC와 그룹 ID 공유 | Y |
| Parent Documents | 이 ADR이 종결시킨 ADC Document ID + 경로(필수 — ADR은 ADC 없이 존재하지 않는 것이 원칙, 예외는 아래 작성 규칙 참조) | N(있으면 필수) |
| Related Documents | 이 ADR이 갱신한 Baseline 문서, 또는 이 ADR을 Supersede한 후속 ADR | N |
| Evidence References | 판단 근거 Research/MVP 문서 | N |
| Source Path | 실제 ADR 파일의 저장소 상대 경로 | Y |
| Last Verified | 마지막 검증 날짜 | Y |
| Verification Confidence | `High` / `Medium` / `Low` | Y |

## 3. 작성 규칙

- ADR은 원칙적으로 ADC를 경유해 발생한다. 예외적으로 Architecture Owner
  직접 지시로 ADC 없이 작성된 ADR(예: 기존 `ADR-0008`)은 Parent
  Documents를 `없음(직접 지시)`로 명시한다 — 빈 칸으로 두거나 추론해서
  채우지 않는다.
- Status가 `Accepted`인 ADR은 반드시 Related Documents에 실제 Baseline
  반영 위치(예: `docs/architecture/baseline/BASELINE.md` 절 이름 또는
  `docs/governance/README.md` 절 이름)를 적는다. 반영 여부를 확인하지
  못했다면 Status를 `Accepted`로 적지 않고 `Undetermined`로 남긴다.
- 한 ADR이 다른 ADR을 Supersede하면 두 행 모두 유지하고, Superseded된
  행의 Status만 갱신한다. 행을 삭제하지 않는다.

## 4. 문서 템플릿

```markdown
| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR-XXXX | | ADR | | Proposed | DG-XXX-XXXX | | | | | YYYY-MM-DD | |
```

## 5. 작성 예시

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR-0006 | Structure v1.0 Migration 확정 | ADR | Development HQ | Accepted | DG-DEVHQ-0006 | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | `docs/architecture/baseline/BASELINE.md` | 본문 참조 | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | 2026-09-20 | High |

## 6. 등록 현황

> 이 원장 도입 이후 신규 작성되는 ADR과, 우선순위 검증을 거쳐 소급
> 등록된 ADR을 함께 관리한다. 기존 ADR 전체 목록은 여전히 도메인별
> 원본 문서(`docs/decisions/adr/README.md`, `docs/architecture/core/`,
> `docs/core/execution-layer/`)가 Source of Truth다.
> `docs/architecture/core/`(Kernel 수준 ADR-0001~0028)는 이번 라운드에서
> 검증 대상에서 제외했다 — 근거는
> `docs/decisions/REGISTRATION-CANDIDATES-0001.md` §3.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR-0001 | Execution Result Contract(여섯 번째 Artifact)의 Contract 형태(목록형)를 Artifact Standard에 반영 | ADR | Execution Layer | Accepted | DG-EXECLAYER-0002 | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` §Artifact 6(반영 확인) | 본문 참조 | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | 2026-09-20 | High |
| ADR-0002 | Execution Result 목록 항목의 타입(`list[str]`)을 Artifact Standard에 반영 | ADR | Execution Layer | Accepted | DG-EXECLAYER-0003 | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` §Artifact 6(반영 확인) | 본문 참조 | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | 2026-09-20 | High |

## 7. 검증 기준

- [ ] Document ID + Target Domain 조합이 전역적으로 유일한가
- [ ] Parent Documents(종결 ADC 또는 직접 지시 사유)가 명시됐는가
- [ ] Status가 Accepted라면 실제 Baseline 반영 위치가 Related Documents에 있는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Last Verified가 갱신됐는가
