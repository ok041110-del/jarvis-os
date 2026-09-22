# GOVERNANCE-HOLD-RATIFICATION-AND-POLICY-DECISION-0001

## 0. 목적 및 근거

이 문서는 `REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001.md`
§9-2("Governance Hold 17건의 최종 처리 방침")가 미결정으로 남긴 질문에
대한 사용자의 명시적 결정, 그리고 그 결정을 이미 편집된 4개 문서
(`docs/governance/adc/ADC-0001.md`/`ADC-0002.md`/`ADC-0004.md`/
`ADC-0005.md`)에 적용하는 사후 추인을 기록한다.

**승인 근거**: 저장소 소유자(user)가 세션 대화에서 다음 두 가지를
직접 지시했다 — "ADC-0001/2/4/5는 사후 추인으로 진행하고, Governance
Hold는 경량 절차로 확정해줘." 이는 `ADR-0008-stage-folder-code-and-docs.md`
("Architecture Owner 직접 지시, ADC 경유 없음")와 `ADC-0010`이 인용한
동일 선례와 같은 성격의 Governance 절차 결정이며, Architecture Decision이
아니므로 RFC → ADC → ADR 절차 대상이 아니다(문서 Governance 절차 자체에
대한 결정이지 Kernel/Baseline 구조 변경이 아니기 때문).

이 문서가 다루는 두 결정은 서로 다른 범위를 가지므로 분리해 기록한다.

---

## 1. Decision A — Governance Hold 정책: 경량 절차 공식 채택

### 1.1 배경(§9-2 원문 인용)

`REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001.md`(커밋
`80cffb4`) §9-2는 다음을 미결정 질문으로 남겼다.

> "Governance Hold 17건의 최종 처리 방침: 영구 보류인지, 별도 경량
> 절차(예: Front Matter나 라벨 변경 없이 문서 최상단에 'Identity &
> Status 요약 표'만 추가하는 초저위험 변형)를 정의해 재검토할지
> 결정이 필요하다."

### 1.2 Decision

**경량 절차를 공식 채택한다.** Governance Hold로 분류된 문서에 대해
다음 조건을 **모두** 충족하는 편집은, 개별 문서 단위의 별도 사전
승인 없이 진행할 수 있는 "경량 절차(Lightweight Restructuring)"로
확정한다.

| 조건 | 내용 |
|---|---|
| 허용되는 변경 | 문서 최상단에 "Identity & Status" 요약 표 추가, 기존 `##`/`###` 헤딩 레벨 조정(강등), "Self Review" 등 템플릿 미대응 섹션을 "부록: " 접두 섹션으로 재배치 |
| 금지되는 변경 | Front Matter 추가, Document ID·파일명 변경, Decision/Status/Rationale/Evidence Reference/Label의 문구·값 변경, 표·코드 블록·Q-번호·후보 라벨의 내용 삭제 또는 재서술(재배치는 허용, 재서술은 금지) |
| 사전 검증 | 편집 대상 문서를 인용하는 문서 목록을 grep으로 재수집(§9-5·§9-6 절차) |
| 사후 검증 | 원문 대비 "매칭되지 않는 삭제 줄 0건"을 라인 단위로 확인(`comm -23` 방식 등), Decision/Status 값 라인의 완전 일치 확인 |

### 1.3 이 결정이 적용되는 범위

- **즉시 적용**: 이미 이 경량 절차 방식으로 편집된 4개 문서
  (§2 Decision B 참조)에 대한 사후 추인의 정책적 근거가 된다.
- **향후 적용 가능**: 나머지 Governance Hold 13건(§3 목록)에 대해
  **같은 경량 절차를 적용하는 것이 정책적으로는 허용**된다. 단, 이
  결정 자체는 그 13건을 지금 편집하라는 지시가 아니다 — 개별 편집은
  별도 작업으로 착수하며, 착수 시에도 §1.2의 사전/사후 검증 조건을
  각 문서마다 다시 수행해야 한다.
- **적용되지 않는 것**: ADC-0019는 이 정책의 적용 대상이 아니다 —
  ADC-0019는 `BASELINE.md`(Frozen)가 Q-번호를 8곳에서 직접 인용하는
  것이 별도로 확인된 문서로, 이 정책과 무관하게 별도의 명시적 사용자
  승인이 있을 때까지 어떤 편집도 하지 않는다(기존 결정 유지).

---

## 2. Decision B — ADC-0001/0002/0004/0005 사후 추인

### 2.1 대상 및 원 편집

| 파일 | 편집 커밋 | 편집 시점 |
|---|---|---|
| `docs/governance/adc/ADC-0001.md` | `9cec37d` | PR #214 branch, `80cffb4`(계획 수립) 8커밋 이후 |
| `docs/governance/adc/ADC-0002.md` | `9cec37d` | 상동 |
| `docs/governance/adc/ADC-0004.md` | `9cec37d` | 상동 |
| `docs/governance/adc/ADC-0005.md` | `9cec37d` | 상동 |

### 2.2 추인의 근거(이미 완료된 독립 검증 재인용)

- **원시 diff 분석**: 4개 파일 전부 삭제 줄이 다른 위치에 재등장하는
  구조 재배치이며, 순수 신규 삭제(재등장 없는 삭제)는 0건(`comm -23`
  기준 라인 비교로 확인).
- **Bold Decision 라인 완전 일치**: `**Keep in MVP**`, `**Accept**` 등
  Decision을 나타내는 볼드 라인이 편집 전후 byte 단위로 완전히 일치.
- **"Self Review" 섹션**: "## Self Review(Checklist)" → "## 부록: Self
  Review(Checklist)"로 제목만 이동, 체크리스트 8~13개 항목 전부
  verbatim 보존.
- **Identity & Status 표 추가**: 4개 파일 모두 상단에 ID/Status/Owner
  요약 표만 신규 추가, Front Matter 미추가.
- **Ledger 영향**: `docs/decisions/adc.md`의 해당 등록 행(Source Path,
  Status)은 이 편집으로 변경되지 않았다(별도 커밋에서 확인, `9cec37d`가
  Ledger 파일을 건드리지 않음).

이상은 §1.2의 경량 절차 조건(허용되는 변경만 발생, 금지되는 변경
없음)을 사후적으로 충족한다.

### 2.3 Decision

**사후 추인(Ratified).** `9cec37d`가 4개 문서에 가한 편집을 §1의
경량 절차에 따른 정당한 편집으로 추인한다. 4개 문서의 Decision Group
표기·Document ID·Status·Ledger 등록은 **변경하지 않는다**(변경할
필요가 없음 — 애초에 그 값들이 편집 전후 동일함이 §2.2에서 확인됨).

### 2.4 이 추인이 하지 않는 것

- 4개 파일을 추가로 편집하지 않는다(이미 있는 상태 그대로 유효화할 뿐).
- 나머지 13개 Governance Hold 문서를 자동으로 추인하거나 편집하지
  않는다.
- ADC-0019에는 어떤 영향도 주지 않는다.
- Architecture Baseline·Kernel Public Contract·Decision Ledger를
  변경하지 않는다.

---

## 3. Governance Hold 13건 — 이 결정 이후의 상태

다음 13건은 이 결정으로 인해 **편집되지 않았으며**, §1.3에 따라 향후
동일한 경량 절차 적용이 정책적으로는 가능하나 개별 착수는 별도
작업이다.

| 트리 | ID | 경로 |
|---|---|---|
| DevHQ-RFC | RFC-0004 | `docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md` |
| DevHQ-RFC | RFC-0005 | `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md` |
| DevHQ-ADR | ADR-0002 | `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md` |
| Kernel-RFC | RFC-0001 | `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` |
| Kernel-RFC | RFC-0013 | `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md` |
| Kernel-ADC | ADC-0001 | `docs/architecture/core/ADC-0001-core-baseline.md` |
| Kernel-ADC | ADC-0002 | `docs/architecture/core/ADC-0002-kernel-definition.md` |
| Kernel-ADC | ADC-0008 | `docs/architecture/core/ADC-0008-runtime-existence-boundary.md` |
| Kernel-ADC | ADC-0013 | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` |
| Kernel-ADR | ADR-0002 | `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` |
| Kernel-ADR | ADR-0003 | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` |
| GovAdc | ADC-0003 | `docs/governance/adc/ADC-0003.md` |
| GovAdc | ADC-0008 | `docs/governance/adc/ADC-0008.md` |

이 13건에 경량 절차를 실제로 적용하려면, 각 문서마다 §1.2의 사전/사후
검증(인용 재수집, 라인 단위 무손실 확인)을 개별적으로 수행하는 별도
작업 단위가 필요하다 — 이 문서는 그 실행을 승인하지 않는다.

---

## 4. Architecture / Public Contract / Protected Document 영향

- Architecture Baseline, Development HQ Baseline, Kernel Public
  Contract: 변경 없음(이 결정 자체가 문서 편집을 수반하지 않음 — 4개
  파일은 이미 편집되어 있던 상태를 추인할 뿐).
- ADC-0019: 영향 없음, 무변경.
- Decision Ledger(`docs/decisions/{rfc,adc,adr,open_decision}.md`):
  변경 없음.

## 5. Related Documents

| Type | ID | Relationship |
|---|---|---|
| Plan | `docs/research/REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001.md` | §9-2 미결정 질문을 이 문서가 해소 |
| Governance Review | `docs/research/OPEN-ISSUES-RESOLUTION-EVIDENCE-PRESERVATION-0001.md` | 4개 문서 무손실 검증의 최초 기록 |
| Governance Review | (이전 세션의 Batch 5/Batch 6 재검증 보고, 본 대화 기록) | ADC-0001/2/4/5 diff 재확인·§9-2 원문 확인 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | 사용자 명시 승인에 따른 §9-2 정책 확정 및 ADC-0001/2/4/5 사후 추인 기록 |
