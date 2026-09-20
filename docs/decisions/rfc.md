---
document_id: LEDGER-RFC
title: RFC 통합 원장
type: Ledger
target_domain: Governance
status: Active
decision_group: LEDGER
parent_documents: []
related_documents:
  - docs/decisions/adc.md
  - docs/decisions/adr.md
  - docs/decisions/open_decision.md
  - docs/decisions/rfc/README.md
evidence_references: []
source_path: docs/decisions/rfc.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# RFC 통합 원장

## 1. 작성 목적

이 문서는 저장소 전체에 흩어진 RFC(Request For Comments) 문서를 하나의
표에서 조회할 수 있게 하는 원장(Ledger)이다. 기존 RFC 파일을 대체하거나
이동시키지 않는다 — 각 RFC의 원문은 기존 위치(`docs/decisions/rfc/`,
`docs/architecture/core/`, `docs/core/execution-layer/` 등)에 그대로 남는다.

이 원장이 존재하는 이유는 두 가지다.

1. 저장소에 RFC 번호가 트리마다 독립적으로 채번되어(`RFC-0001`이 세 곳에
   존재) 번호만으로는 문서를 특정할 수 없다는 문제(`RFC/README.md`가 이미
   지적함)를 Document ID + Target Domain 조합으로 해소한다.
2. 신규 RFC부터는 이 원장에 등록하는 것을 표준 절차로 만들어, 앞으로는
   같은 문제가 반복되지 않게 한다.

**기존 RFC 문서는 이 원장 생성으로 인해 일괄 등록되지 않는다.** 아래
"3. 등록 현황"은 신규 RFC 등록 창구이며, 과거 RFC는 필요할 때 개별
확인 후 점진적으로 추가한다(§4 작성 규칙 참조).

## 2. 필드 설명

| 필드 | 설명 | 필수 |
|---|---|---|
| Document ID | 트리 내부 고유 ID. 기존 파일명 규칙(`RFC-XXXX`)을 그대로 쓴다 | Y |
| Title | 문서 제목. 기존 파일 제목과 동일하게 유지 | Y |
| Type | 이 원장에서는 항상 `RFC` | Y |
| Target Domain | `Kernel` / `Development HQ` / `Execution Layer` / `Investment HQ` / `Governance` 중 하나 — 트리 구분자 역할 | Y |
| Status | `Proposed` / `Open` / `Resolved` / `Withdrawn` 중 하나. 문서 헤더 라벨이 아니라 후속 ADC/ADR 존재 여부로 판단한 **실제 상태** | Y |
| Decision Group | 같은 논의 흐름(RFC→ADC→ADR 또는 RFC→Open Decision)에 속한 문서를 묶는 임의 식별자. 형식: `DG-<도메인약어>-<일련번호>` (예: `DG-DEVHQ-0007`) | Y |
| Parent Documents | 이 RFC가 참조/승계하는 상위 문서(대개 없음 — RFC는 논의의 시작점) | N |
| Related Documents | 이 RFC로부터 파생된 ADC/ADR 또는 Open Decision 경로 | N |
| Evidence References | 이 RFC의 판단 근거가 된 `docs/research/` 또는 `docs/01_mvp/` 문서 경로 | N |
| Source Path | 실제 RFC 파일의 저장소 상대 경로 | Y |
| Last Verified | 이 원장 항목을 마지막으로 검증(파일 존재·상태 일치 확인)한 날짜 | Y |
| Verification Confidence | `High`(원문 직접 대조) / `Medium`(연관 문서로 간접 확인) / `Low`(미확인·추정) | Y |

## 3. 작성 규칙

- 신규 RFC를 작성하면 그 즉시 이 원장에 한 행을 추가한다. 기존 RFC를 이
  원장에 소급 등록하려면, 원문을 직접 열어 Status/Related Documents를
  확인한 뒤에만 추가한다 — 확인 없이 일괄 추가하지 않는다.
- Document ID·파일명·번호는 기존 트리의 채번 규칙을 그대로 따른다.
  이 원장이 새로운 번호 체계를 만들지 않는다.
- Status는 파일 헤더의 `**Status**` 라벨을 그대로 옮기지 않는다.
  후속 ADC/ADR 존재 여부로 실제 상태를 판단해 기록하고, 헤더 라벨과
  다르면 비고에 그 사실을 남긴다.
- Related Documents/Parent Documents는 확인되지 않은 관계를 추론해서
  채우지 않는다. 확인되지 않으면 `Undetermined`로 남긴다.
- 원장 항목을 삭제하지 않는다. 철회(Withdrawn)된 RFC도 상태만 갱신하고
  행은 유지한다.

## 4. 문서 템플릿

```markdown
| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RFC-XXXX | | RFC | | | DG-XXX-XXXX | | | | | YYYY-MM-DD | |
```

## 5. 작성 예시

다음은 이미 존재하는 RFC-0007(Development HQ 트리)을 이 원장 형식으로
표현한 예시다(원문 대조 후 작성).

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RFC-0007 | AST 기반 Context 자동 추출의 Production Build Capability 통합 | RFC | Development HQ | Resolved | DG-DEVHQ-0007 | 없음 | `docs/governance/adc/ADC-0005.md` | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md` 본문 참조 | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md` | 2026-09-20 | High |

## 6. 등록 현황

> 신규 RFC 등록 창구. 아래 표는 이 원장 도입 이후 신규 작성되는 RFC부터
> 채운다. 과거 RFC 전체 목록은 여전히 `docs/decisions/rfc/README.md`가
> Source of Truth다 — 이 표가 그 문서를 대체하지 않는다.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| (없음) | | | | | | | | | | | |

## 7. 검증 기준

새 행을 추가하기 전에 다음을 확인한다.

- [ ] Document ID가 대상 Target Domain 트리 내에서 중복되지 않는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Status가 원문 헤더가 아니라 후속 ADC/ADR 존재 여부로 판단됐는가
- [ ] Related Documents에 적힌 경로가 실제로 존재하는가(존재하지 않으면 `Undetermined`)
- [ ] Last Verified가 오늘 날짜로 갱신됐는가
