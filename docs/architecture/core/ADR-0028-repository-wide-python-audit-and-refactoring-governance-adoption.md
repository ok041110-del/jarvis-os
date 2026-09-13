# ADR-0028: Repository-wide Python Audit & Refactoring — Governance Lifecycle Adoption

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0028` |
| 상태 | **Accepted (Scoped) — Governance Lifecycle 자체만 확정한다: Inventory → Deterministic Audit → Semantic/Ponytail Review → Candidate Classification → Refactoring Wave → Validation → Evidence 절차, Ponytail 권한 경계, 7종 Candidate Classification, Wave 정책, Validation 정책을 Repository-wide Python Audit & Refactoring의 공식 절차로 승인한다. 실제 Inventory/Audit 실행, 실제 `*.py` 수정(Implementation)은 이 ADR이 승인하지 않는다 — Wave 단위 별도 사용자 승인을 통해서만 착수한다(NOT YET AUTHORIZED, §6).** |
| Context | `RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` → `ADC-0045-repository-wide-python-audit-and-refactoring-decision.md` → 이 ADR |
| 관련 RFC | `RFC-0042`(Lifecycle/권한 경계/분류 체계 설계), `RFC-0037`(Ponytail 원 정의, 재론하지 않음) |
| 관련 ADC | `ADC-0045`(Governance 절차 채택 확정, Implementation 별도 승인 조건부), `ADC-0040`(Stage 04 Multi-Agent, 여전히 NOT DETERMINED — Open, 이 ADR이 대신 결정하지 않음) |
| 관련 ADR | 없음(Ponytail을 Production Architecture 구성요소로 승격하는 ADR은 아직 없다 — `ADC-0040`이 Open이므로) |
| 관련 Evidence | `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`, `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`(파일 보존 판단 선례로 §4 Historical Evidence 보호 조건에 인용) |
| Governance Status 확인 | 이 저장소의 모든 ADR Status는 "Accepted"(Scoped 등 수식어 동반) 계열뿐이다(`ADR-0025`~`ADR-0027`이 이미 재확인). 이 ADR도 동일 어휘를 재사용한다. 단, 이 ADR은 Architecture/Contract를 승인하는 것이 아니라 **Governance 절차(Process)**를 승인한다는 점에서 `ADR-0024`~`ADR-0027`(Engine/Architecture Adoption)과 성격이 다르다 — 이 구분을 §1/§5에서 명시한다. |

---

## 1. Context

사용자가 Repository 전체 `*.py`를 Ponytail 원칙 + Senior Developer
수준 기준으로 감사·리팩토링할 수 있는 Governance를 먼저 확립하라고
요청했다. `RFC-0042`가 기존 Governance 체계(번호 체계, 문서 위치,
Status 어휘, `ADC-0040`의 Ponytail 원 정의)를 조사하고 그 위에서
새 Lifecycle을 설계했으며, `ADC-0045`가 이를 ADOPT로 판정했다.
이 ADR은 그 Decision을 Baseline 절차로 기록한다 — Architecture나
Public Contract를 변경하는 것이 아니라, **Python 코드 품질을
다루는 새로운 하위 Governance 절차의 존재**를 공식화한다.

## 2. Decision 본문

### 2.1 승인된 것

- `RFC-0042` §3의 Lifecycle 7단계(Inventory → Deterministic
  Audit → Semantic/Ponytail Review → Candidate Classification →
  Refactoring Wave → Validation → Evidence).
- `RFC-0042` §5의 Ponytail 권한 경계(Local simplification/
  Readability/Unnecessary abstraction 제거/Comment·docstring
  cleanup/Obvious duplication 축소/Naming·control-flow 개선은
  Governance 불필요; Architecture/Stage·Team responsibility/Public
  Contract/Output schema/Dependency boundary/신규 capability/
  Cross-HQ 변경은 별도 RFC → ADC → ADR 필요).
- `RFC-0042` §6의 7종 Candidate Classification(KEEP/COMMENT·
  DOCSTRING CLEANUP/SIMPLIFY/REFACTOR/POSSIBLE BUG/ARCHITECTURE·
  CONTRACT RISK/GOVERNANCE REQUIRED).
- `RFC-0042` §7의 Wave 정책(Audit → Candidate selection →
  Implementation → Focused validation → Full regression →
  Evidence → 다음 Wave, 매 Wave 범위 사전 선언 원칙).
- `RFC-0042` §8의 Validation 정책(기존 도구/기존 테스트 스위트
  우선 재사용, 신규 Validator는 필요성만 인정하고 작성은 유보).

### 2.2 승인되지 않은 것

- 실제 Inventory 실행.
- 실제 Deterministic Audit/Semantic Review 실행.
- 어떤 `*.py` 파일의 실제 수정/삭제/이동.
- `RFC-0042` §8이 "필요성만 인정"한 신규 경량 Validator 스크립트의
  실제 작성.
- `ADC-0040`(Stage 04 Multi-Agent Ponytail) 관련 어떤 Decision
  변경도 아니다 — 그 ADC는 이 ADR과 무관하게 계속 NOT DETERMINED로
  Open 상태다.

### 2.3 향후 별도 Governance가 필요한 것

`RFC-0042` §5의 "별도 Governance 필요" 목록(Architecture 변경,
Stage/Team responsibility 변경, Public Contract 변경, Output
schema 변경, dependency boundary 변경, 신규 capability 추가,
Cross-HQ architectural change)에 해당하는 발견 사항은, 이 Governance
Lifecycle 진행 중 언제 나타나든 즉시 별도 RFC 개설 대상으로
분류한다(`GOVERNANCE REQUIRED`). 이 ADR은 그런 개별 RFC를 미리
승인하지 않는다 — 각각 발생 시점에 개별적으로 판단한다.

## 3. Audit-only 단계 vs Refactoring 실행 단계

이 ADR은 두 단계를 명확히 분리해서 기록한다:

- **Audit-only 단계(이 ADR이 승인)**: Inventory, Deterministic
  Audit, Semantic/Ponytail Review, Candidate Classification까지.
  이 단계는 코드를 읽기만 하며 어떤 파일도 수정하지 않는다. 이
  단계의 산출물은 분류 결과와 Evidence 문서뿐이다.
- **Refactoring 실행 단계(이 ADR이 승인하지 않음, Wave별 별도
  승인 필요)**: `SIMPLIFY`/`REFACTOR`/`COMMENT·DOCSTRING CLEANUP`로
  분류된 항목에 대한 실제 코드 수정(§2.1의 Wave 정책을 따름). 이
  단계는 매 Wave 착수 시점에 그 Wave의 범위를 사용자에게 명시
  보고하고 승인을 받은 뒤에만 시작한다.

## 4. Historical Evidence / Architecture Governance 보호

`docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`,
`docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`가 이미 KEEP으로
확정한 파일(`archive/v1/`, `docs/decisions/{rfc,adc,adr}/`이
인용하는 대상, RFC/ADC/ADR/Freeze 문서가 실제로 인용하는
`projects/*` 코드, `stages/04_implementation/architecture_validation/`)은
이 Lifecycle의 Candidate Classification에서 `SIMPLIFY`/`REFACTOR`
대상이 될 수 없다 — 최대 `GOVERNANCE REQUIRED` 또는 `KEEP`으로만
분류 가능하다. 이는 §2.1의 Ponytail 권한 경계가 이미 함의하는
결론을 이 ADR 수준에서 다시 한번 명시적으로 고정한다.

## 5. Rollback 기준

다음 중 하나라도 발생하면 이 Governance Lifecycle의 적용을
즉시 중단하고 재검토(새 RFC)로 전환한다:

- 어떤 Wave에서든 Ponytail 권한 범위(§2.1)를 벗어난 변경이 실제
  커밋에 포함된 사실이 Validation(§2.1 Validation 정책, Scope
  compliance 항목)에서 발견된 경우.
- Full regression에서 이전 Wave까지는 없던 실패가 발생하고, 그
  원인이 이번 Wave의 변경으로 확인된 경우 — 해당 Wave의 커밋을
  되돌리고 그 Candidate를 다시 Audit 단계로 되돌린다.
- 어떤 분류 판단이 실제로는 Architecture/Contract에 영향을 준
  것으로 사후에 밝혀진 경우 — 해당 변경을 되돌리고 `GOVERNANCE
  REQUIRED`로 재분류, 별도 RFC를 연다.
- 사용자가 임의 시점에 Lifecycle 자체의 중단을 지시한 경우.

Rollback은 Wave 단위로 수행한다(Repository 전체를 한 번에 되돌리는
상황이 발생하지 않도록 하는 것이 §2.1 Wave 정책의 목적 그 자체다).

## 6. 이 ADR이 확정하는 것 / 확정하지 않는 것(요약)

- **확정**: Repository-wide Python Audit & Refactoring을 위한
  Governance Lifecycle, Ponytail 권한 경계, Candidate Classification
  7종, Wave/Validation 정책, Rollback 기준.
- **확정하지 않음(NOT YET AUTHORIZED)**: 실제 Wave 착수, 실제
  코드 수정, `ADC-0040`의 Stage 04 Multi-Agent Decision.
- **Architecture 변경**: 없음.
- **Contract 변경**: 없음.
- **Governance 변경**: 신규 하위 절차(Python Audit Lifecycle)를
  기존 RFC → ADC → ADR 체계 안에서 추가했을 뿐, 상위 Governance
  단계 정의(`docs/governance/README.md`)는 무변경.

## Self Review

- Architecture를 재설계했는가 — **아니오**, 절차만 정의(§6).
- Ponytail의 Stage 04 채택 여부를 대신 결정했는가 — **아니오**,
  `ADC-0040`은 그대로 Open(§2.2).
- 코드를 수정했는가 — **아니오**.
- 이 ADR 자체가 실제 Refactoring을 허가하는가 — **아니오**,
  §3/§6에서 명시적으로 구분.

## Related

- `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md`
- `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`
- `hqs/development/IMPLEMENTATION_RULES.md`
- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`,
  `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`
