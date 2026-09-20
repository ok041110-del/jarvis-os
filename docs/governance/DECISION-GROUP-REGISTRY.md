# Decision Group Registry

## 목적

`docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`가
Scoped Accept한 Decision Group 개념의 실제 구현체다. RFC·ADC·ADR이
여러 문서로 분기(fan-out)·집약(fan-in)되거나 하나의 문서 안에서 부분
종결되는 경우, 그 관계를 **기존 문서를 전혀 수정하지 않고** 별도로
기록한다.

## 운영 규칙 (ADC-0010 요약, 상세 근거는 원문 참조)

- 이 Registry에 등록한다고 기존 RFC/ADC/ADR 파일의 번호·제목·본문·
  링크가 바뀌지 않는다. 등록/미등록 여부가 문서의 유효성에 영향을
  주지 않는다.
- 문서 본문에 명시된 교차 참조("관련 RFC", "관련 ADC", "Context",
  "RFC-000X 후속" 등)만 근거로 채택한다. 제목·주제 유사성만으로는
  등록하지 않는다.
- 근거가 확인되지 않은 관계는 등록하지 않는다 — 임의 추정 금지.
- 전체 문서를 한 번에 매핑하지 않는다. 근거가 명확한 그룹부터
  점진적으로 추가한다.
- Open Decision(`OD-XX`)은 독자 번호 체계를 유지한다 — 이 Registry는
  관련 있는 경우에만 참조로 연결하며, OD 자체를 재번호하지 않는다.
- `Decision Group ID`(`DG-NNNN`)는 RFC/ADC/ADR/OD 어느 번호와도
  공유하지 않는 완전히 독립된 전역 순차 번호다.

## Decision Groups

| DG ID | Title | Scope | Status | RFC 수 | ADC 수 | ADR 수 |
|---|---|---|---|---|---|---|
| [DG-0001](#dg-0001--structure-v10-migration--baseline-relocation) | Structure v1.0 Migration & Baseline Relocation | Development HQ (Docs Taxonomy) | Resolved | 1 | 2 | 2 |
| [DG-0002](#dg-0002--kernel-agent-domain--multi-agent-boundary-phase-af) | Kernel Agent Domain & Multi-Agent Boundary (Phase A~F) | Kernel | Resolved (Not Adopted — LangGraph) | 7 | 2 | 1 |

미등록 문서는 "그룹 없음" 상태로 남으며, 이는 오류가 아니라 이번
1차 등록 범위(§선정 근거 참조)에 포함되지 않았음을 의미한다.

---

## DG-0001 — Structure v1.0 Migration & Baseline Relocation

| Field | Value |
|---|---|
| Decision Group ID | DG-0001 |
| Title | Structure v1.0 Migration & Baseline Relocation |
| Scope | Development HQ — `docs/`, `hqs/`, `core/execution/` 물리적 재배치 |
| RFC Documents | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` |
| ADC Documents | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md`(Decision 1~4), `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md`(Option A/B) |
| ADR Documents | `docs/decisions/adr/ADR-0006-structure-v1-migration.md`(ADC-0005 Decision 1~4 전부 종결), `docs/decisions/adr/ADR-0007-baseline-relocation.md`(ADC-0006 Option A/B 종결) |
| Open Decisions | 없음 |
| Relationship Evidence | `ADC-0005` 제목 본문: `"# ADC-0005: Structure v1.0 Migration — RFC-0006 후속 Decision 4건"`. `ADC-0006` 본문: `"근거는 docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md ..."`. `ADR-0006` 필드: `"관련 RFC | RFC-0006-...md"`, `"관련 ADC | ADC-0005-...md (Decision 1~4 전부 종결)"`. `ADR-0007` 필드: `"Context | docs/decisions/adc/ADC-0006-baseline-relocation-decision.md"`, `"관련 ADC | ADC-0006-...md (Option A/B 판단 종결)"` |
| Status | Resolved |
| Notes | 1 RFC → ADC 2건 → ADR 2건으로 분기(fan-out)하는 사례 — RFC=ADC=ADR 단일 번호 통일이 구조적으로 불가능함을 보여준 근거 사례(`ADC-0010` §4.3). ADR-0006이 예고한 "docs taxonomy Phase 2 매핑" 후속 ADC는 아직 생성되지 않았다(`DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md` §9-2) — 생성되면 이 그룹에 추가 등록을 검토한다. |

## DG-0002 — Kernel Agent Domain & Multi-Agent Boundary (Phase A~F)

| Field | Value |
|---|---|
| Decision Group ID | DG-0002 |
| Title | Kernel Agent Domain & Multi-Agent Boundary (Phase A~F) |
| Scope | Kernel — Agent Domain/Lifecycle/State/Message/Event Contract, Multi-Agent Runtime 필요성 |
| RFC Documents | `RFC-0024`(Phase A, Agent Domain/Lifecycle), `RFC-0025`(Phase B, State/Message/Event), `RFC-0026`(Phase C, Multi-Agent Workflow Contract), `RFC-0027`(Phase D, Multi-Agent Runtime Contract), `RFC-0028`(Phase E, Minimal Runtime MVP 필요성), `RFC-0029`(Phase F-1, Dev HQ Stage→Agent Boundary), `RFC-0030`(Phase F-2, Stage 01~05 Agent Team Boundary) — 전부 `docs/architecture/core/` |
| ADC Documents | `docs/architecture/core/ADC-0032-agent-domain-and-lifecycle-contract-resolution.md`(RFC-0024 후속), `docs/architecture/core/ADC-0033-agent-state-message-event-contract-resolution.md`(RFC-0025 후속, Phase B). RFC-0026~0030(Phase C~F)은 개별 ADC 없이 Evidence/PoC를 거쳐 아래 ADR로 직접 종합됨 |
| ADR Documents | `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md`(Phase A~F 종합 — "LangGraph를 지금 Production에 도입할 근거가 있는가" 최종 판정) |
| Open Decisions | `docs/decisions/adc/ADC.md`의 `ADC-02`(Runtime 존폐, Open) — ADR-0018이 "선행 Decision(참고, 뒤집지 않음)"으로만 인용, 이 그룹이 결정하지 않음 |
| Relationship Evidence | `ADR-0018` 필드 원문: `"Context | ... RFC-0024~RFC-0030 → ADC-0032~ADC-0033(Agent Domain/Lifecycle/Multi-Agent 트랙, Phase A~F)"`, `"관련 RFC | RFC-0024, RFC-0025, RFC-0026, RFC-0027, RFC-0028, RFC-0029, RFC-0030"`(문서 원문은 RFC-0019~0022도 함께 나열하나 이는 별도 트랙 — 아래 Notes 참조), `"관련 ADC | ..., ADC-0032, ADC-0033"`. `ADC-0032`/`ADC-0033` 각자의 제목이 "(RFC-0024 후속)"/"(RFC-0025 후속, Phase B)"로 명시 |
| Status | Resolved (Not Adopted — LangGraph는 Deferred/Not Adopted로 종결) |
| Notes | **불확실성 기록**: `ADR-0018`은 자신의 Context/관련 RFC·ADC 필드에 이 그룹(Phase A~F, Agent Domain/Multi-Agent 트랙)과 **별도의 다른 트랙**(`RFC-0019`~`RFC-0022` → `ADC-0019`~`ADC-0026` → `ADR-0008`~`ADR-0014`, Workflow Adapter Gate A/B/C 트랙)을 함께 나열한다 — 문서 본문이 명시적으로 "서로 다른 두 트랙이 시간순으로 이어진 것"이라고 구분하므로, 이 DG-0002는 Agent Domain/Multi-Agent 트랙(Phase A~F)만 포함하고 Workflow Adapter Gate 트랙은 **별도 미등록 그룹 후보**로 남긴다(추정으로 합치지 않음). 또한 `ADR-0018`의 LangGraph 관련 일부 판정은 2026-09-08 `ADR-0019`(구현 기술 채택, 별도 스코프)가 부분 Supersede했다 — `ADR-0018` 원문이 "새 Accept 없음, 이 문서의 판정·근거·Gate 표는 재작성되지 않는다"고 명시하므로 이 그룹의 Status/Evidence는 변경하지 않는다. `ADR-0019`를 이 그룹에 포함할지는 별도 근거 검토 후 판단(현재 미매핑). |

---

## 미매핑 후보 (근거는 있으나 이번 1차 등록에서 제외)

다음은 명시적 교차 참조가 확인되었으나, 범위 확정에 추가 검토가
필요해 이번 1차 등록에 포함하지 않았다 — 임의 추정으로 합치지 않고
공란으로 남긴다.

- **Workflow Adapter Gate A/B/C 트랙**: `RFC-0019`~`RFC-0022` →
  `ADC-0019`~`ADC-0026` → `ADR-0008`~`ADR-0014`(`docs/architecture/
  core/`). `ADR-0018`이 이 트랙을 DG-0002와 나란히 인용하지만, 이
  트랙 자체의 내부 RFC:ADC:ADR 대응이 1:1이 아니므로(§ADC-0010 §4.1)
  정확한 그룹 경계를 별도로 확인한 뒤 등록할 후보로 남긴다.
- **Development HQ 초기 트랙**: `docs/decisions/rfc/RFC-0001`~
  `RFC-0004` ↔ `docs/governance/adc/ADC-0001`~`ADC-0004` — 번호는
  일치하나 후속 ADR 유무·번호가 문서마다 달라(예: `ADR-0001`은
  `ADC-0003` 판단 1만 종결) 그룹 경계 확정에 추가 검토 필요.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Governance ADC | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | 이 Registry의 설계 근거이자 승인 문서 |
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 원 조사 문서 |
| Issue | #206 | 이 구현이 응답하는 요청 |
| PR | #208 | 이 Registry가 추가되는 작업 흐름 |

## Change History

| Date | Change | Reason |
|---|---|---|
| 2026-09-20 | DG-0001, DG-0002 최초 등록 | ADC-0010 후속 구현 작업 1·2번 실행 |
