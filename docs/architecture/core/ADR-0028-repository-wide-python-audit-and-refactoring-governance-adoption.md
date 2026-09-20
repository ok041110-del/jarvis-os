# ADR-0028 — Repository-wide Python Audit & Refactoring: Governance Lifecycle Adoption

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | `docs/architecture/core/ADR-0028` |
| Status | **Accepted (Scoped) — Governance Lifecycle 자체만 확정한다: Inventory → Deterministic Audit → Semantic/Ponytail Review → Candidate Classification → Refactoring Wave → Validation → Evidence 절차, Ponytail 권한 경계, 7종 Candidate Classification, Wave 정책, Validation 정책을 Repository-wide Python Audit & Refactoring의 공식 절차로 승인한다. 실제 Inventory/Audit 실행, 실제 `*.py` 수정(Implementation)은 이 ADR이 승인하지 않는다 — Wave 단위 별도 사용자 승인을 통해서만 착수한다(NOT YET AUTHORIZED, §6).** |
| Owner / Scope | Repository 전체 Python 코드 품질 Governance 절차(Architecture/Contract 아님) |
| Context | `RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` → `ADC-0045-repository-wide-python-audit-and-refactoring-decision.md` → 이 ADR |

> 이 ADR은 Architecture/Contract를 승인하는 것이 아니라 **Governance
> 절차(Process)**를 승인한다는 점에서 `ADR-0024`~`ADR-0027`(Engine/
> Architecture Adoption)과 성격이 다르다. 이 저장소의 모든 ADR Status는
> "Accepted"(Scoped 등 수식어 동반) 계열뿐이며(`ADR-0025`~`ADR-0027`이
> 이미 재확인), 이 ADR도 동일 어휘를 재사용한다.

## 2. Context & Decision Drivers

| Item | Description |
|---|---|
| Context | 사용자가 Repository 전체 `*.py`를 Ponytail 원칙 + Senior Developer 수준 기준으로 감사·리팩토링할 수 있는 Governance를 먼저 확립하라고 요청. `RFC-0042`가 기존 Governance 체계(번호 체계, 문서 위치, Status 어휘, `ADC-0040`의 Ponytail 원 정의)를 조사하고 새 Lifecycle을 설계했으며, `ADC-0045`가 ADOPT로 판정 |
| Problem | Python 코드 품질을 다루는 새로운 하위 Governance 절차의 부재 |
| Decision Drivers | `RFC-0042` §3(Lifecycle 7단계), §5(Ponytail 권한 경계), §6(7종 Candidate Classification), §7(Wave 정책), §8(Validation 정책) |
| Constraints | `ADC-0040`(Stage 04 Multi-Agent, NOT DETERMINED — Open)의 Decision을 이 ADR이 대신 결정하지 않는다 |

## 3. Decision

### 3.1 승인된 것

- Lifecycle 7단계: Inventory → Deterministic Audit → Semantic/Ponytail Review → Candidate Classification → Refactoring Wave → Validation → Evidence.
- Ponytail 권한 경계: Local simplification/Readability/Unnecessary abstraction 제거/Comment·docstring cleanup/Obvious duplication 축소/Naming·control-flow 개선은 Governance 불필요; Architecture/Stage·Team responsibility/Public Contract/Output schema/Dependency boundary/신규 capability/Cross-HQ 변경은 별도 RFC → ADC → ADR 필요.
- 7종 Candidate Classification: KEEP / COMMENT·DOCSTRING CLEANUP / SIMPLIFY / REFACTOR / POSSIBLE BUG / ARCHITECTURE·CONTRACT RISK / GOVERNANCE REQUIRED.
- Wave 정책: Audit → Candidate selection → Implementation → Focused validation → Full regression → Evidence → 다음 Wave, 매 Wave 범위 사전 선언 원칙.
- Validation 정책: 기존 도구/기존 테스트 스위트 우선 재사용, 신규 Validator는 필요성만 인정하고 작성은 유보.

### 3.2 승인되지 않은 것 — Audit-only 단계 vs Refactoring 실행 단계

이 ADR은 두 단계를 명확히 분리한다.

- **Audit-only 단계(승인)**: Inventory, Deterministic Audit, Semantic/Ponytail Review, Candidate Classification까지 — 코드를 읽기만 하며 어떤 파일도 수정하지 않는다.
- **Refactoring 실행 단계(미승인, Wave별 별도 승인 필요)**: `SIMPLIFY`/`REFACTOR`/`COMMENT·DOCSTRING CLEANUP` 분류 항목의 실제 코드 수정. 매 Wave 착수 시점에 범위를 사용자에게 명시 보고하고 승인받은 뒤에만 시작한다.

승인되지 않은 항목: 실제 Inventory/Audit/Semantic Review 실행, 어떤 `*.py` 파일의 실제 수정/삭제/이동, 신규 경량 Validator 스크립트의 실제 작성, `ADC-0040` 관련 Decision 변경(그 ADC는 이 ADR과 무관하게 계속 NOT DETERMINED로 Open).

### 3.3 향후 별도 Governance가 필요한 것

`RFC-0042` §5의 "별도 Governance 필요" 목록(Architecture 변경, Stage/Team responsibility 변경, Public Contract 변경, Output schema 변경, dependency boundary 변경, 신규 capability 추가, Cross-HQ architectural change)에 해당하는 발견 사항은 Lifecycle 진행 중 언제 나타나든 즉시 별도 RFC 개설 대상(`GOVERNANCE REQUIRED`)으로 분류한다. 이 ADR은 그런 개별 RFC를 미리 승인하지 않는다.

### 3.4 Historical Evidence / Architecture Governance 보호

`STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`, `ARCHIVE-CLEANUP-REVALIDATION-0001.md`가 이미 KEEP으로 확정한 파일(`archive/v1/`, `docs/decisions/{rfc,adc,adr}/`이 인용하는 대상, RFC/ADC/ADR/Freeze 문서가 실제로 인용하는 `projects/*` 코드, `stages/04_implementation/architecture_validation/`)은 이 Lifecycle의 Candidate Classification에서 `SIMPLIFY`/`REFACTOR` 대상이 될 수 없다 — 최대 `GOVERNANCE REQUIRED` 또는 `KEEP`으로만 분류 가능하다.

### 3.5 Rollback 기준

다음 중 하나라도 발생하면 이 Lifecycle 적용을 즉시 중단하고 새 RFC로 재검토한다: (1) Ponytail 권한 범위를 벗어난 변경이 실제 커밋에 포함된 사실이 Validation에서 발견, (2) Full regression에서 이전 Wave까지 없던 실패가 발생하고 원인이 이번 Wave로 확인 — 해당 Wave 커밋 되돌리고 Audit 단계로 재분류, (3) 어떤 분류 판단이 사후에 Architecture/Contract에 영향을 준 것으로 밝혀짐 — 변경을 되돌리고 `GOVERNANCE REQUIRED`로 재분류, 별도 RFC 개설, (4) 사용자가 임의 시점에 Lifecycle 중단을 지시. Rollback은 Wave 단위로 수행한다.

## 4. Rationale & Alternatives

### Rationale

| Reason | Explanation | Evidence |
|---|---|---|
| Audit과 Implementation을 분리 승인 | Governance 절차 확립과 실제 코드 변경 착수를 같은 문서에서 동시에 승인하면 Wave별 사용자 통제가 무력화됨 | `RFC-0042` §7 Wave 정책 |
| Historical Evidence 보호를 ADR 수준에서 재확인 | Ponytail 권한 경계(§2.1)가 이미 함의하는 결론을 명시적으로 고정해 반복 재해석을 방지 | §4 Historical Evidence |

### Rejected Alternatives

| Alternative | Reason for Rejection | Evidence |
|---|---|---|
| Governance 승인과 동시에 Wave 1 착수 승인 | Wave 단위 사전 범위 선언·개별 승인 원칙(§7 Wave 정책)과 상충 | `RFC-0042` §7 |

## 5. Consequences & Impact

| Category | Impact |
|---|---|
| Positive Consequences | Repository-wide Python Audit & Refactoring을 위한 Governance Lifecycle, Ponytail 권한 경계, Candidate Classification 7종, Wave/Validation 정책, Rollback 기준이 확정된다 |
| Negative Consequences / Trade-offs | 없음 |
| Risks | 없음(Wave별 별도 승인 게이트가 리스크를 통제) |
| Operational Impact | 실제 Wave 착수, 실제 코드 수정, `ADC-0040`의 Stage 04 Multi-Agent Decision은 확정하지 않음(NOT YET AUTHORIZED) |

## 6. Architecture Baseline & Implementation

| Item | Description |
|---|---|
| Architecture Baseline Impact | 없음 |
| Public Contract Impact | 없음 |
| Implementation Scope | 신규 하위 절차(Python Audit Lifecycle)를 기존 RFC → ADC → ADR 체계 안에 추가했을 뿐, 상위 Governance 단계 정의(`docs/governance/README.md`)는 무변경 |
| Follow-up Work | Wave 단위 별도 사용자 승인을 통한 실제 착수(§3.2) |

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` | Lifecycle/권한 경계/분류 체계 설계 |
| RFC | `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md` | Ponytail 원 정의(재론하지 않음) |
| ADC | `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md` | Governance 절차 채택 확정, Implementation 별도 승인 조건부 |
| ADC | `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md` | 여전히 NOT DETERMINED — Open, 이 ADR이 대신 결정하지 않음 |
| ADR | — | 없음(Ponytail을 Production Architecture 구성요소로 승격하는 ADR은 아직 없음 — ADC-0040이 Open) |
| Evidence | `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`, `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md` | 파일 보존 판단 선례(§3.4 Historical Evidence 보호 조건에 인용) |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | RFC-0042 → ADC-0045 Governance Lifecycle 채택 |
