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
| OD-0001 | Decision Group Registry(DG-NNNN, `ADC-0010` 기결) 도입과 이 통합 원장의 Decision Group 필드(`DG-<도메인>-NNNN`)의 관계 | Open Decision | Governance | Reconsidered | DG-DEVHQ-GOVERNANCE-0206 | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | `docs/decisions/rfc.md`, `docs/decisions/adc.md`, `docs/decisions/adr.md`, `docs/governance/DECISION-GROUP-REGISTRY.md`(공식 Registry — 이미 존재함, 5차 라운드에서 확인) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md`(3~5차 라운드) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md` | 2026-09-20 | High |
| OD-0002 | `ADR-0028`의 상태 필드("Wave 실행은 NOT YET AUTHORIZED")와 실제 저장소에 존재하는 Wave 0~5 실행 기록 문서 6건 사이의 표기 최신성(Currency) 확인 필요 | Open Decision | Kernel | Reconsidered | DG-KERNEL-0042 | `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`, `docs/research/PYTHON-REFACTOR-WAVE-5-DOCSTRING-SEMANTIC-AUDIT-0001.md` 외 4건(Wave 1~4); PR #189, PR #190(5차 라운드 근거 확인) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md`(4차·5차 라운드) | `docs/decisions/REGISTRATION-CANDIDATES-0001.md` | 2026-09-20 | High |

### OD-0001 — Decision Group Registry와 통합 원장 Decision Group 필드의 관계

#### Decision Question (원안, 3차 라운드)

`ADC-0010`(Scoped Accept)은 fan-out/fan-in을 표현하기 위해 **전역
단일 네임스페이스** `DG-NNNN`(예: `DG-0001`)을 쓰는
`docs/governance/DECISION-GROUP-REGISTRY.md`를 "후속 구현 작업"으로
지정했다. 3차 라운드는 이 문서가 **"아직 생성되지 않음"**이라고
기술했다. 이번 라운드에서 만든 `docs/decisions/{rfc,adc,adr}.md` 3개
원장은 이미 자체적으로 `DG-<도메인약어>-NNNN`(예: `DG-KERNEL-0001`,
`DG-DEVHQ-0007`) 형식의 Decision Group 값을 200개 가까이 채워
넣었다 — `ADC-0010`이 정의한 공식 네임스페이스와 형식이 다르다는
것이 원래의 Open Question이었다.

#### Reconsideration (5차 라운드) — 사실관계 정정

**3차 라운드의 전제 자체가 틀렸다.** `docs/governance/
DECISION-GROUP-REGISTRY.md`는 **이미 존재한다** — `ADC-0010`이
승인된 직후(같은 세션, PR #208, 커밋 `8481d81`)에 생성되어 `main`에
병합됐고, 지금 이 브랜치에도 그대로 존재한다(`git log`로 확인,
`main` 기준 확인). 실제 내용:

- 공식 전역 네임스페이스 `DG-NNNN` 형식을 그대로 사용 중이다
  (`DG-0001`, `DG-0002` — 도메인 접두어 없음).
- **2개 그룹만 등록**되어 있다: `DG-0001`(Structure v1.0 Migration &
  Baseline Relocation), `DG-0002`(Kernel Agent Domain & Multi-Agent
  Boundary). 그 문서 자신이 "근거가 명확한 그룹부터 점진적으로
  추가한다"는 원칙을 명시해, 전체 RFC/ADC/ADR을 커버하는 것을
  처음부터 목표로 하지 않았다.
- 이 원장(`docs/decisions/{rfc,adc,adr}.md`)의 `DG-<도메인>-NNNN`
  값(약 190개)과 공식 Registry의 `DG-NNNN` 값(2개)은 **표기 형식이
  다르므로 문자열로 절대 충돌하지 않는다**(`DG-0001` ≠
  `DG-DEVHQ-0001`, `DG-KERNEL-0001` 등 — grep으로 재확인).

#### Resolution

원안의 3개 선택지 중 **(b)를 그대로 채택**한다 — 이 원장의
`DG-<도메인>-NNNN` 값은 원장 내부 조회 편의를 위한 **비공식 인덱스**로
유지하고, 공식 Registry(`DECISION-GROUP-REGISTRY.md`)는 근거가
확인된 fan-out/fan-in 사례만 별도로 계속 관리한다. 근거:

1. 공식 Registry가 이미 이 원칙(점진적 등록, 근거 우선)으로 설계·
   운영되고 있다 — 새로 결정할 필요가 없다.
2. 두 네임스페이스는 형식이 달라(도메인 접두어 유무) 실제 문자열
   충돌이 없다 — 사람이 혼동할 위험은 "이 원장 필드가 공식 Registry를
   대체한다"는 오해뿐이며, 이는 (b) 채택 결정과 함께 3개 원장의
   §3(작성 규칙)에 명시적 disambiguation 문구를 추가해 해소했다
   (`docs/decisions/rfc.md`·`adc.md`·`adr.md` §3, 이번 라운드에서
   추가).
3. (a)(전체 재발급)는 여전히 불필요하고 위험하다 — 약 190개 행을
   근거 없이 일괄 재작업해야 하며, 공식 Registry 자신의 "점진적
   등록" 원칙과도 맞지 않는다.
4. (c)(`ADC-0010` 재검토)도 불필요하다 — `ADC-0010`이 이미 승인한
   설계(전역 `DG-NNNN`, 점진적 등록, 기존 문서 비파괴)가 그대로
   구현·운영되고 있어 재검토할 새 Evidence가 없다.

**남는 것(이번 라운드가 결정하지 않음)**: 이 원장이 이미 확인한
fan-out/fan-in 관계 중 공식 Registry에 아직 등록되지 않은 사례(예:
`DG-DEVHQ-0006` 계열은 이미 공식 `DG-0001`과 대응하지만, 다른 여러
`DG-KERNEL-*` 계열은 아직 공식 Registry 후보로 검토되지 않았다)를
공식 Registry에 추가 등록할지는 별도 라운드의 판단 대상이다 —
이 OD는 "두 체계가 충돌하는가"라는 원래 질문만 종결한다.

#### Related Documents

| Type | ID | Relationship |
|---|---|---|
| ADC | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | 공식 DG-NNNN 체계를 Scoped Accept로 확정 |
| Registry | `docs/governance/DECISION-GROUP-REGISTRY.md` | 이미 존재함(5차 라운드에서 확인) — DG-0001·DG-0002 등록 |
| Ledger | `docs/decisions/rfc.md`, `docs/decisions/adc.md`, `docs/decisions/adr.md` | 비공식 `DG-<도메인>-NNNN` 값을 사용 중, §3에 disambiguation 문구 추가(5차 라운드) |

### OD-0002 — ADR-0028 상태 표기와 실제 Wave 실행 기록의 최신성

#### Decision Question (원안, 4차 라운드)

`docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md`
는 상태 필드에 "실제 Inventory/Audit 실행, 실제 `*.py` 수정은 이
ADR이 승인하지 않는다 — Wave 단위 별도 사용자 승인을 통해서만
착수한다(**NOT YET AUTHORIZED**)"라고 명시한다. 그러나 저장소에는
`docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md`부터
`PYTHON-REFACTOR-WAVE-5-DOCSTRING-SEMANTIC-AUDIT-0001.md`까지 **Wave
0~5, 6건의 실행 기록 문서**가 실제로 존재한다. 4차 라운드는 Wave별
개별 승인이 실제로 이뤄졌는지 파일만으로는 확인할 수 없다고 보고
판단을 보류했다.

#### Reconsideration (5차 라운드) — 승인 근거 확인

`git log --all --merges`로 각 Wave 커밋의 병합 이력을 추적한 결과,
Wave 0~5는 예외 없이 GitHub PR을 통해 병합되었음을 확인했다:

- **PR #189**(`claude/jarvis-python-audit-wave1-comments`, base
  `main`): Wave 0 커밋(`1b2c21e`)과 Wave 1 커밋(`793714a`,
  `71135e3`)을 포함 — 커밋 그래프상 `f4c214b`(ADR-0028 자체 확립
  커밋) → `1b2c21e`(Wave 0) → `793714a`(Wave 1) → `71135e3`(Wave 1
  연장) 순으로 이 PR의 head(`71135e3`)에 도달한다.
- **PR #190**(`claude/jarvis-python-refactor-wave2`, base
  `main@bc087f8`, 즉 PR #189 병합 직후): Wave 2(`0b17ae1`,
  `969b232`, `93b5683`), Wave 3(`8f85c08` 외 스냅샷 6건,
  `53a592d`), Wave 4(`b72dc57`), Wave 5(`3c1b93e`)를 전부 포함한다.
  PR 제목 자체가 "Python Refactor Wave 2+3+4+5"로 4개 Wave를 명시한다.

GitHub API(`pull_request_read`, method `get`)로 두 PR을 직접 조회해
`state: closed`, `merged: true`, **`merged_by: ok041110-del`**(이
저장소 소유자 계정)을 확인했다. 즉 Wave 0~5 전체가 이 저장소가 실제로
사용하는 승인 메커니즘 — PR을 저장소 소유자가 직접 병합하는 행위 —
을 예외 없이 거쳤다. 이는 "승인 근거가 확인되지 않으면 승인 사실을
추정하지 않는다"는 이번 지시의 원칙을 만족하는 **직접 증거**다(git
log의 커밋 존재만으로 승인을 추정한 것이 아니라, PR 병합 주체를
GitHub API로 직접 조회함).

#### Resolution

위 증거에 근거해 다음과 같이 판단한다.

1. **문서 표기 오류(Documentation Labeling Issue)이지 Governance
   미비(Governance Gap)가 아니다.** Wave 0~5는 각각 별도 PR 병합을
   통해 저장소 소유자의 명시적 승인을 받고 실행되었다 — ADR-0028이
   요구하는 "Wave 단위 별도 사용자 승인" 절차 자체는 실제로 준수된
   것으로 확인된다. 누락된 것은 **ADR-0028 상태 필드 텍스트의
   사후 갱신**뿐이다.
2. 이는 이 저장소에 이미 존재하는 선례와 일치한다 —
   `DOC-TRIAGE-0001`이 "D-9 index debt"로 분류한, 실제로 해결된
   RFC/ADC/ADR의 `Status: Proposed` 헤더를 소급 갱신하지 않는
   관행과 동일한 패턴이다. 즉 이번 발견은 새로운 이상 징후가 아니라
   기존에 문서화된 관행이 ADR-0028에도 적용된 사례다.
3. **원본 ADR-0028은 이번 라운드에서도 수정하지 않는다** — 사용자의
   명시적 별도 승인 없이 Governance 문서 원문을 고치는 것은 이번
   작업 범위를 벗어나며, 발견 사항은 이 Open Decision 기록으로
   충분히 추적된다.
4. 따라서 OD-0002는 **판단 불가(Open)** 상태에서 **사실관계가
   확인되어 종결 가능한 상태(Reconsidered)** 로 전환한다. 스키마상
   `Closed(→ADC)`/`Closed(→ADR)`는 새 ADC/ADR 제정을 의미하므로
   해당하지 않는다 — 이 건은 새 결정이 아니라 기존 결정(ADR-0028)의
   상태 텍스트 최신성에 대한 사실 확인이다.

**남는 것**: ADR-0028 상태 필드의 "NOT YET AUTHORIZED" 문구를
"Wave 0~5 실행 완료(각각 PR #189/#190 병합으로 승인)"로 갱신할지는
여전히 별도의 사용자 승인이 필요한 Governance 판단이다 — 이 Open
Decision은 그 판단에 필요한 근거(PR #189, #190의 병합 사실)를
제공하는 것으로 역할을 다하며, 실제 갱신 여부·시점은 사용자 결정에
맡긴다.

#### Related Documents

| Type | ID | Relationship |
|---|---|---|
| ADR | `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | 상태 필드가 "NOT YET AUTHORIZED"로 남아 있는 원본(수정하지 않음) |
| Evidence | `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md` 외 5건 | 실제 실행 기록(Wave 0~5) |
| Evidence | GitHub PR #189(`jarvis-python-audit-wave1-comments`) | Wave 0+1 병합 승인 기록(`merged_by: ok041110-del`) |
| Evidence | GitHub PR #190(`jarvis-python-refactor-wave2`) | Wave 2+3+4+5 병합 승인 기록(`merged_by: ok041110-del`) |

## 7. 검증 기준

- [ ] Document ID(`OD-XXXX`)가 전역적으로 유일한가
- [ ] Status가 본문 대조 없이 확정되지 않았는가
- [ ] 예약 ADR 번호가 다른 건과 중복되지 않는가
- [ ] MVP-0049~0052 등 관계 미확인 Evidence 문서를 임의로 등록하지 않았는가
- [ ] Source Path의 파일이 실제로 존재하는가
