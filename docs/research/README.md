---
document_id: RESEARCH-INDEX
title: Research Index
type: Index
target_domain: Governance
status: Active
decision_group: LEDGER
parent_documents: []
related_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adc.md
  - docs/decisions/adr.md
  - docs/decisions/open_decision.md
evidence_references: []
source_path: docs/research/README.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# Research Index

## 1. 작성 목적

`docs/research/`에는 155건 이상의 조사·검증·재현 기록이 쌓여 있다.
이 문서는 그 문서들을 관리하기 위한 색인이며, Decision Register
(`docs/decisions/rfc.md`/`adc.md`/`adr.md`/`open_decision.md`)와는
성격이 다르다.

## 2. Research와 Decision Register의 관계

**Research 문서는 결정 문서가 아니다.** Research는 RFC/ADC/ADR/Open
Decision이 판단할 때 참조하는 **Evidence Reference**다. 즉:

```
Research → Evidence Reference (RFC/ADC/ADR/Open Decision의 근거로 인용됨)
```

Research 문서 자체는 Architecture나 Baseline을 변경하지 않는다.
Research가 Architecture 변경으로 이어지려면 반드시 RFC → ADC → ADR
절차(CLAUDE.md "Frozen Architecture")를 거쳐야 한다.

## 3. 기존 문서에 대한 원칙

- 기존 155건의 Research 문서를 이 Index 도입을 이유로 일괄 수정하거나
  Front Matter를 소급 삽입하지 않는다.
- 기존 문서의 제목이나 내용을 근거로 RFC/ADC/ADR과의 관계를 자동
  추론해서 이 Index나 Decision Register에 추가하지 않는다. 관계는
  해당 RFC/ADC/ADR 원문에서 명시적으로 인용된 경우에만 등록한다.
- 기존 문서는 필요할 때(예: 다른 작업에서 실제로 읽고 확인했을 때)
  점진적으로 아래 §5 등록 현황에 추가한다. 이 Index 생성 자체가 전수
  등록을 의미하지 않는다.

## 4. 신규 Research 문서 작성 기준

신규로 작성하는 Research 문서부터 다음을 적용한다.

1. Front Matter를 포함한다(§6 참조).
2. 이 문서 §5 "등록 현황"에 한 행을 추가한다.
3. 그 Research가 어떤 결정(RFC/ADC/ADR/Open Decision)의 근거로
   쓰였다면 Related Decision 열에 명시한다. 아직 어떤 결정에도 인용되지
   않았다면 `없음(미인용)`으로 둔다 — 추측해서 채우지 않는다.

`docs/01_mvp/MVP-0049~0052-observation.md`와 같이 `docs/research/`
바깥에 있는 Evidence 문서는 이 Index의 등록 대상이 아니다. 이들은
Decision Register 쪽에서 "Evidence Reference 후보"로만 취급되며
(`docs/decisions/open_decision.md` §3 참조), RFC/ADC/ADR 관계를 임의로
부여받지 않는다.

## 5. 등록 현황

> 이 Index 도입 이후 작성되는 신규 Research 문서부터 등록한다.

| Document ID | Title | Source Path | Related Decision | Last Verified |
|---|---|---|---|---|
| (없음) | | | | |

## 6. Front Matter 필드(신규 Research 문서용)

| 필드 | 설명 | 허용값 |
|---|---|---|
| document_id | 파일명 기반 ID(예: `MD-WRITER-VALIDATION-SKILL-CHECK-0001`) | 자유 형식, 파일명과 일치 |
| title | 문서 제목 | 자유 텍스트 |
| type | 항상 `Research` | `Research` |
| target_domain | 조사 대상 도메인 | `Kernel` / `Development HQ` / `Execution Layer` / `Investment HQ` / `Governance` |
| status | 조사 진행 상태 | `Draft` / `Complete` / `Superseded` |
| related_decision | 이 Research를 인용한 RFC/ADC/ADR/Open Decision Document ID | Document ID 또는 `없음(미인용)` |
| source_path | 파일의 저장소 상대 경로 | 실제 경로 |
| last_verified | 마지막 검증 날짜 | `YYYY-MM-DD` |

## 7. 검증 기준

- [ ] 신규 Research 문서에 Front Matter가 포함됐는가
- [ ] related_decision이 실제로 그 RFC/ADC/ADR 원문에서 인용을 확인한 값인가(추론 아님)
- [ ] 기존 문서를 이 Index 도입을 이유로 일괄 수정하지 않았는가
- [ ] `docs/01_mvp/` Evidence 문서를 이 Index에 잘못 등록하지 않았는가
