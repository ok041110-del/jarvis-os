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
| Document ID | 트리 내부 고유 ID(예: `ADC-0005`, `ADC-01`). 트리마다 채번 규칙이 다를 수 있어 Target Domain과 조합해도 유일하지 않을 수 있다 — 저장소에 물리적으로 다른 4개 디렉터리(`docs/decisions/adc/`, `docs/governance/adc/`, `docs/architecture/core/`, `docs/core/execution-layer/`)가 각자 `ADC-0001`부터 독립 채번하며, 같은 Target Domain(`Development HQ`) 안에서도 서로 다른 두 파일이 같은 번호를 쓰는 사례가 실제로 확인됐다(`docs/governance/adc/ADC-0005.md` vs `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md`). **전역 유일성은 Document ID + Target Domain + Source Path 조합으로만 보장된다** — Source Path가 실질적 유일 키다 | Y |
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
- **Decision Group 필드는 `docs/governance/DECISION-GROUP-REGISTRY.md`
  (공식 전역 `DG-NNNN`)를 대체하지 않는다** — 별개 네임스페이스다
  (`docs/decisions/rfc.md` §3, `OD-0001` Resolution 참조).

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
> Truth다. `docs/architecture/core/`(Kernel 수준, ADC-0001·ADC-0008~
> ADC-0046 중 40건)는 원문 대조 후 아래에 등록했다. ADC-0002~0007은
> 후속 ADR이 다른 트리(`docs/decisions/adr/`)에 물리적으로 위치하는
> 교차 참조 이슈가 있어 이번 라운드에서 보류했다 — 근거는
> `docs/decisions/REGISTRATION-CANDIDATES-0001.md` §3·§4.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADC-0001 | Spec-Repository Artifact Drift — Kernel 책임 여부 판단 | ADC | Execution Layer | Resolved(Not Accepted, No ADR Required) | DG-EXECLAYER-0001 | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | 없음(ADR 불필요) | 본문 참조(RFC-0001 인용 Evidence 동일) | `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | 2026-09-20 | High |
| ADC-0002 | Execution Result Contract — 3개 후보 판단 | ADC | Execution Layer | Resolved(Accepted: Candidate 2 — 산출물 목록) | DG-EXECLAYER-0002 | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | 본문 참조 | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | 2026-09-20 | High |
| ADC-0003 | Execution Result Item Schema — 항목 타입 판단 | ADC | Execution Layer | Resolved(Accepted: `list[str]`) | DG-EXECLAYER-0003 | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | 본문 참조 | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | 2026-09-20 | High |
| ADC-0004 | Execution Result Consumer — 결정 가능성 판단 | ADC | Execution Layer | Resolved(Not Accepted, No ADR Required) | DG-EXECLAYER-0004 | `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | 없음(ADR 불필요) | 본문 참조(Kernel `ADC-0001-core-baseline.md` Module 4 인용) | `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | 2026-09-20 | High |
| ADC-0005 | Engine 연결 Boundary — 허용 여부 판단 | ADC | Execution Layer | Resolved(부분 Accept: caller 수준 연결 Q0 Accept / Execution Layer 내부 호출 Q1 Not Accepted, 양쪽 다 No ADR Required) | DG-EXECLAYER-0005 | `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | 없음(ADR 불필요) | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`, `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md` | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | 2026-09-20 | High |
| ADC-0001 | Kernel Baseline Module 채택 판단(5개 Module 개별 판단) | ADC | Kernel | Resolved(Multi-Module: Governance Accept/ADR Required, Workflow Defer, Memory Defer, Execution Layer Accept/ADR Required, Event Bus Defer — 세부는 원문 §종합 참조) | DG-KERNEL-0001 | `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` | `docs/architecture/core/ADR-0001-governance-module-baseline.md`, `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0001-core-baseline.md` | 2026-09-20 | High |
| ADC-0008 | Runtime 개념의 존폐 | ADC | Kernel | Resolved(Not Accepted, No ADR Required) | DG-KERNEL-0008 | `docs/architecture/core/RFC-0008-runtime-existence-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/architecture/core/ADC-0008-runtime-existence-boundary.md` | 2026-09-20 | High |
| ADC-0009 | Model 축과 Component 축의 대응 관계 | ADC | Kernel | Resolved(Not Accepted, No ADR Required) | DG-KERNEL-0009 | `docs/architecture/core/RFC-0009-model-component-correspondence-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/architecture/core/ADC-0009-model-component-correspondence-boundary.md` | 2026-09-20 | High |
| ADC-0010 | Engine Caller의 위치와 책임(6개 후보) | ADC | Kernel | Resolved(Not Accepted 전부, No ADR Required) | DG-KERNEL-0010 | `docs/architecture/core/RFC-0010-engine-caller-location-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md` | 2026-09-20 | High |
| ADC-0011 | Kernel/HQ에 속하지 않는 별도 실행 위치 | ADC | Kernel | Resolved(Not Accepted, No ADR Required) | DG-KERNEL-0011 | `docs/architecture/core/RFC-0011-standalone-execution-location-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/architecture/core/ADC-0011-standalone-execution-location-boundary.md` | 2026-09-20 | High |
| ADC-0012 | Dispatch Component의 Architecture Boundary | ADC | Kernel | Resolved(B. Defer) | DG-KERNEL-0012 | `docs/architecture/core/RFC-0012-dispatch-component-boundary.md` | 없음(Defer, ADR 없음) | 본문 참조 | `docs/architecture/core/ADC-0012-dispatch-component-boundary.md` | 2026-09-20 | High |
| ADC-0013 | Runtime 존폐 — Scoped Reconsideration | ADC | Kernel | Resolved(A. Accept Scoped) | DG-KERNEL-0013 | `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md` | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` | 2026-09-20 | High |
| ADC-0014 | Execution 책임의 명칭 | ADC | Kernel | Resolved(A. Accept — 명칭: Execution Host) | DG-KERNEL-0014 | `docs/architecture/core/RFC-0014-execution-responsibility-naming.md` | `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0014-execution-responsibility-naming.md` | 2026-09-20 | High |
| ADC-0015 | Execution Host 구현 전략 | ADC | Kernel | Resolved(A. Conditional Accept — Process 1차, Thread 배제, Subprocess 대안) | DG-KERNEL-0015 | `docs/architecture/core/RFC-0015-execution-host-implementation-strategy.md` | `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md` | 2026-09-20 | High |
| ADC-0016 | Multi-Task 최소 책임 | ADC | Kernel | Resolved(A. Accept, Scoped/Conditional on Data·Artifact Isolation) | DG-KERNEL-0016 | `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md` | `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md` | 2026-09-20 | High |
| ADC-0017 | Multi-Task Result Store Integrity Boundary | ADC | Kernel | Resolved(A. Accept, Scoped/Narrow — 저장 전 검증 게이트로 한정) | DG-KERNEL-0017 | `docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md` | `docs/architecture/core/ADR-0007-multi-task-result-store-integrity-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` | 2026-09-20 | High |
| ADC-0018 | Natural-Language Request → Multi-HQ Task Decomposition | ADC | Kernel | Resolved(C. Defer, Scoped — 실 필요 관찰 전까지 보류) | DG-KERNEL-0018 | `docs/architecture/core/RFC-0018-natural-language-request-multi-hq-task-decomposition.md` | 없음(Defer, ADR 없음) | 본문 참조 | `docs/architecture/core/ADC-0018-natural-language-request-multi-hq-task-decomposition.md` | 2026-09-20 | High |
| ADC-0019 | Scoped Workflow Graph Execution Boundary | ADC | Kernel | Resolved(A. Accept, Scoped/Conditional) | DG-KERNEL-0019 | `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md` | `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` | 2026-09-20 | High |
| ADC-0020 | Workflow Adapter Naming and Contract Boundary(Q-A~Q-F 다중 판단) | ADC | Kernel | Resolved(Accept — 세부는 원문 §5 Q-A~Q-F 참조) | DG-KERNEL-0020 | `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md` | `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` | 2026-09-20 | High |
| ADC-0021 | Workflow Adapter Implementation Strategy(D1~D4) | ADC | Kernel | Resolved(A. Accept — Strategy Framing Only) | DG-KERNEL-0019-GATE | 없음(선행 `docs/architecture/core/ADC-0019`·`docs/architecture/core/ADC-0020`의 후속 판단 — 전용 RFC 없음) | `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`(§8 Gate C 지정자) | 본문 참조 | `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md` | 2026-09-20 | Medium |
| ADC-0022 | Workflow Adapter Execution Unit Lifecycle State Model Resolution | ADC | Kernel | Resolved(A. Accept — Gate (A) 부분 해소: 결정 2·5·11) | DG-KERNEL-0021 | `docs/architecture/core/RFC-0021-workflow-adapter-execution-unit-lifecycle-state-model-boundary.md` | `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` | 2026-09-20 | Medium |
| ADC-0023 | Workflow Engine Port Contract Surface and Engine Seam Resolution | ADC | Kernel | Resolved(A. Accept — 결정 9 Gate (A) 완전 해소) | DG-KERNEL-0022 | `docs/architecture/core/RFC-0022-workflow-engine-port-contract-surface-and-engine-seam-boundary.md` | `docs/architecture/core/ADR-0012-gate-a-decision-9-contract-surface-resolution-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` | 2026-09-20 | Medium |
| ADC-0024 | Gate (B) Independent Observation Threshold Judgment | ADC | Kernel | Resolved(A. Accept — Gate (B) 형식 요건 충족/Conditional 부분 완화) | DG-KERNEL-0019-GATE | 없음(선행 `docs/architecture/core/ADC-0019`의 재검토 조건에 따른 후속 판단 — 전용 RFC 없음) | `docs/architecture/core/ADR-0013-gate-b-partial-relaxation-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0024-gate-b-independent-observation-threshold-judgment.md` | 2026-09-20 | Medium |
| ADC-0025 | Gate (B) Second Lineage Partial Relaxation | ADC | Kernel | Resolved(판정: Partial) | DG-KERNEL-0019-GATE | 없음(선행 `docs/architecture/core/ADC-0024`의 후속 판단 — 전용 RFC 없음) | `docs/architecture/core/ADR-0014-gate-b-second-lineage-partial-relaxation-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md` | 2026-09-20 | Medium |
| ADC-0026 | Gate (C) Real Engine Partial Discharge | ADC | Kernel | Resolved(판정: Decided — Partial) | DG-KERNEL-0019-GATE | 없음(선행 `docs/architecture/core/ADC-0019`의 재검토 조건에 따른 후속 판단 — 전용 RFC 없음) | 전용 ADR 없음 — `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md`가 종합 인용 | 본문 참조 | `docs/architecture/core/ADC-0026-gate-c-real-engine-partial-discharge.md` | 2026-09-20 | Medium |
| ADC-0027 | OmniRoute Model Routing/Engine Adapter Conditional Adoption | ADC | Kernel | Resolved(Accept, Conditional/Scoped) | DG-KERNEL-0023 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` | `docs/architecture/core/ADR-0015~0017`(3건, Consolidation) | 본문 참조 | `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md` | 2026-09-20 | High |
| ADC-0028 | Domain Fallback Chains Precondition Responsibility Redesign | ADC | Kernel | Resolved(Accept, Scoped/Narrow) | DG-KERNEL-0023 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`(`ADC-0027` Scope 산하) | `docs/architecture/core/ADR-0015~0017`(3건, Consolidation) | 본문 참조 | `docs/architecture/core/ADC-0028-domain-fallback-chains-precondition-responsibility-redesign.md` | 2026-09-20 | High |
| ADC-0029 | Routing Decisions Precondition Responsibility Redesign | ADC | Kernel | Resolved(Accept, Scoped/Narrow) | DG-KERNEL-0023 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`(`ADC-0027` Scope 산하) | `docs/architecture/core/ADR-0015~0017`(3건, Consolidation) | 본문 참조 | `docs/architecture/core/ADC-0029-routing-decisions-precondition-responsibility-redesign.md` | 2026-09-20 | High |
| ADC-0030 | Priority Precondition Responsibility Redesign | ADC | Kernel | Resolved(Accept, Scoped/Narrow) | DG-KERNEL-0023 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md`(`ADC-0027` Scope 산하) | `docs/architecture/core/ADR-0015~0017`(3건, Consolidation) | 본문 참조 | `docs/architecture/core/ADC-0030-priority-precondition-responsibility-redesign.md` | 2026-09-20 | High |
| ADC-0031 | OmniRoute Thin Engine Caller Boundary | ADC | Kernel | Resolved(Accept, Scoped/Narrow) | DG-KERNEL-0023 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` | `docs/architecture/core/ADR-0015~0017`(3건, Consolidation), `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`(재인용) | 본문 참조 | `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md` | 2026-09-20 | High |
| ADC-0032 | Agent Domain and Lifecycle Contract Resolution | ADC | Kernel | Resolved(Q1 — Reject) | DG-KERNEL-0024 | `docs/architecture/core/RFC-0024-agent-domain-and-lifecycle-contract.md` | 전용 ADR 없음 — `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md`가 종합 인용 | 본문 참조 | `docs/architecture/core/ADC-0032-agent-domain-and-lifecycle-contract-resolution.md` | 2026-09-20 | Medium |
| ADC-0033 | Agent State Message Event Contract Resolution | ADC | Kernel | Resolved(Q1·Q2 — Not Accept, Defer) | DG-KERNEL-0025 | `docs/architecture/core/RFC-0025-agent-state-message-event-contract.md` | 전용 ADR 없음 — `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md`가 종합 인용 | 본문 참조 | `docs/architecture/core/ADC-0033-agent-state-message-event-contract-resolution.md` | 2026-09-20 | Medium |
| ADC-0034 | LangGraph Implementation Technology Adoption | ADC | Kernel | Resolved(Accept(a), Conditional/Non-Mandatory) | DG-KERNEL-0031 | `docs/architecture/core/RFC-0031-langgraph-implementation-technology-adoption.md` | `docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md` | 2026-09-20 | High |
| ADC-0035 | Graphify Implementation Technology Adoption | ADC | Kernel | Resolved(Accept(a), Conditional/Non-Mandatory, Architecture 무연동) | DG-KERNEL-0032 | `docs/architecture/core/RFC-0032-graphify-implementation-technology-adoption.md` | `docs/architecture/core/ADR-0020-graphify-implementation-technology-adoption.md` | 본문 참조 | `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md` | 2026-09-20 | High |
| ADC-0036 | Stage01 Multi-Agent Reasoning Resolution | ADC | Kernel | Resolved(Accept — Scoped) | DG-KERNEL-0033 | `docs/architecture/core/RFC-0033-stage01-multi-agent-reasoning-adoption.md` | `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0036-stage01-multi-agent-reasoning-resolution.md` | 2026-09-20 | High |
| ADC-0037 | Stage01 PRD Specification Synthesis Resolution | ADC | Kernel | Resolved(Accept — Scoped) | DG-KERNEL-0034 | `docs/architecture/core/RFC-0034-stage01-prd-specification-synthesis.md` | `docs/architecture/core/ADR-0022-stage01-prd-specification-synthesis-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0037-stage01-prd-specification-synthesis-resolution.md` | 2026-09-20 | High |
| ADC-0038 | Stage02 Planning Responsibility and Execution Model Resolution(다중 판단) | ADC | Kernel | Resolved(Accept — 세부는 원문 §Decision 참조) | DG-KERNEL-0035 | `docs/architecture/core/RFC-0035-stage02-planning-responsibility-and-execution-model.md` | `docs/architecture/core/ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md` | 본문 참조 | `docs/architecture/core/ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md` | 2026-09-20 | High |
| ADC-0039 | Multi-Engine Re-Evaluation | ADC | Kernel | Resolved(RE-EVALUATE — KEEP도 TRANSITION도 아님, 추가 Evidence 필요) | DG-KERNEL-0036 | `docs/architecture/core/RFC-0036-chatgpt-claude-code-dual-engine-boundary.md` | `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`(Amendment 포함) | 본문 참조 | `docs/architecture/core/ADC-0039-multi-engine-re-evaluation.md` | 2026-09-20 | High |
| ADC-0040 | Stage04 Multi-Agent Ponytail Decision | ADC | Kernel | Open(NOT DETERMINED — Real Engine Evidence Required) | DG-KERNEL-0037 | `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md` | 없음(미결정, ADR 없음) | 본문 참조 | `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md` | 2026-09-20 | High |
| ADC-0041 | Stage05 QA Multi-Agent Decision | ADC | Kernel | Open(NOT DETERMINED — Real Engine Evidence Required) | DG-KERNEL-0038 | `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md` | 없음(미결정, ADR 없음) | 본문 참조 | `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md` | 2026-09-20 | High |
| ADC-0042 | Stage05 Parallel Validation DAG Decision | ADC | Kernel | Resolved(Partial — Independence Confirmed, Production Adoption Not Determined) | DG-KERNEL-0039 | `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md` | `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md` | 본문 참조 | `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md` | 2026-09-20 | High |
| ADC-0043 | OpenRouter Free Model Selection Decision | ADC | Kernel | Resolved(Partial — Architecture Boundary Confirmed, Concrete API Adoption Not Yet Determined) | DG-KERNEL-0040 | `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md` | `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`, `docs/architecture/core/ADR-0027`(재인용) | 본문 참조 | `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md` | 2026-09-20 | High |
| ADC-0044 | OpenRouter Production Engine Migration Decision | ADC | Kernel | Resolved(Partial — Architecture Production Adoption Accepted, Operational Reliability 별도 유지) | DG-KERNEL-0041 | `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md` | `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md` | 본문 참조 | `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md` | 2026-09-20 | High |
| ADC-0045 | Repository-Wide Python Audit and Refactoring Decision | ADC | Kernel | Resolved(ADOPT — Governance Lifecycle Accepted, Implementation 별도 승인 필요) | DG-KERNEL-0042 | `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` | `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | 본문 참조 | `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md` | 2026-09-20 | High |
| ADC-0046 | Workflow Execution History Verification Persistence Ownership Boundary | ADC | Kernel | Resolved(Not Accepted, No ADR Required — Boundary Question Open으로 남음) | DG-KERNEL-0043 | `docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md`(및 `RFC-0043`) | 없음(ADR 불필요) | 본문 참조 | `docs/architecture/core/ADC-0046-workflow-execution-history-verification-persistence-ownership-boundary.md` | 2026-09-20 | High |
| ADC-0001 | Kernel Extraction Candidate 승격 판단(4개 후보) | ADC | Development HQ | Resolved(Keep in MVP — 전부 미승격) | DG-DEVHQ-0001 | `docs/decisions/rfc/RFC-0001-kernel-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/governance/adc/ADC-0001.md` | 2026-09-20 | High |
| ADC-0002 | Task Dispatcher 승격 재판단 | ADC | Development HQ | Resolved(Keep in MVP) | DG-DEVHQ-0002 | `docs/decisions/rfc/RFC-0002-task-dispatcher-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/governance/adc/ADC-0002.md` | 2026-09-20 | High |
| ADC-0003 | Development HQ SDLC Platform 재정의 판단 | ADC | Development HQ | Resolved(Accept) | DG-DEVHQ-0003 | `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` | `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md`(판단 1), `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`(교차 인용) | 본문 참조 | `docs/governance/adc/ADC-0003.md` | 2026-09-20 | High |
| ADC-0004 | Task Dispatcher → Runtime 승격 판단 | ADC | Development HQ | Resolved(Keep in MVP) | DG-DEVHQ-0004 | `docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md` | 없음(ADR 불필요) | 본문 참조 | `docs/governance/adc/ADC-0004.md` | 2026-09-20 | High |
| ADC-0005 | AST Context 자동 추출 Production 통합 판단(4개 판단) | ADC | Development HQ | Resolved(4개 판단 전부 Accept, 전부 No ADR Required) | DG-DEVHQ-0007 | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md`, `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md`(인용) | `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md`, `docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md`(교차 인용) | 본문 참조 | `docs/governance/adc/ADC-0005.md` | 2026-09-20 | Medium |
| ADC-0006 | AST Context Module Discovery Dotted Path 확장 판단 | ADC | Development HQ | Resolved(Decision B, Conditional Accept) | DG-DEVHQ-0008 | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md`, `docs/decisions/rfc/RFC-0008-agents-module-physical-layout-boundary.md` | `docs/decisions/adr/ADR-0007-baseline-relocation.md`(교차 인용) | 본문 참조 | `docs/governance/adc/ADC-0006.md` | 2026-09-20 | Medium |
| ADC-0007 | Stage Data Contract 판단 | ADC | Development HQ | Resolved(Scoped Accept) | DG-DEVHQ-0009 | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md`, `docs/decisions/rfc/RFC-0009-stage-data-contract.md` | `docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md` | 본문 참조 | `docs/governance/adc/ADC-0007.md` | 2026-09-20 | High |
| ADC-0008 | Outcome-Oriented Governance Model 도입 판단(Q-1/Q-2/Q-3) | ADC | Development HQ | Resolved(Scoped Accept — Q-1 Accept(b)/Q-2 Scoped/Q-3 Scoped, 소급 미적용) | DG-DEVHQ-0010 | `docs/decisions/rfc/RFC-0010-outcome-oriented-governance-model.md`, `docs/decisions/rfc/RFC-0004~0005,0007~0009`(인용) | `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md` | 본문 참조 | `docs/governance/adc/ADC-0008.md` | 2026-09-20 | High |
| ADC-0009 | "Implementation Freedom" 원칙 도입 판단(Q-1/Q-2) | ADC | Development HQ | Resolved(Scoped Accept, 개정 없음) | DG-DEVHQ-0011 | `docs/decisions/rfc/RFC-0011-implementation-freedom-principle.md`, `docs/decisions/rfc/RFC-0005,0011`(인용) | `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md` | 본문 참조 | `docs/governance/adc/ADC-0009.md` | 2026-09-20 | High |
| ADC-0010 | RFC·ADC·ADR 통합 식별자 체계 도입 판단(Issue #206 후속) | ADC | Development HQ | Resolved(Scoped Accept — 후보 C의 '논리적 그룹' 개념만 채택, 파일명 소급 반영/전면 재번호화는 Reject) | DG-DEVHQ-GOVERNANCE-0206 | 없음(선행 RFC 없음 — Issue #206 직접 요청, ADR-0008 직접 지시 선례와 동일 성격) | 없음(ADR 미생성 — Registry 신설은 Baseline 변경이 아니라고 판단) | 본문 참조 | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | 2026-09-20 | High |
| ADC-0002 | Kernel Definition — Responsibility, Not Component(5개 판단) | ADC | Kernel | Resolved(4개 Accept, 1개 Defer — 세부 원문 §종합 참조) | DG-KERNEL-0002 | `docs/architecture/core/RFC-0002-kernel-definition.md` | `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md`(교차 트리 — 판단 1·3·4) | 본문 참조 | `docs/architecture/core/ADC-0002-kernel-definition.md` | 2026-09-20 | High |
| ADC-0003 | Kernel Context Model(10개 판단) | ADC | Kernel | Resolved(6개 Accept, 4개 Defer — 세부 원문 §종합 참조) | DG-KERNEL-0003 | `docs/architecture/core/RFC-0003-kernel-context-model.md` | `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md`(교차 트리 — 판단 1·2·3·5·6a) | 본문 참조 | `docs/architecture/core/ADC-0003-kernel-context-model.md` | 2026-09-20 | High |
| ADC-0004 | Kernel Public Contract(9개 판단) | ADC | Kernel | Resolved(6개 Accept 전부 조건부, 1개 부분Accept/부분Defer, 2개 Defer) | DG-KERNEL-0004 | `docs/architecture/core/RFC-0004-kernel-public-contract.md` | `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md`(교차 트리 — 판단 1~8) | 본문 참조 | `docs/architecture/core/ADC-0004-kernel-public-contract.md` | 2026-09-20 | High |
| ADC-0005 | Kernel Logical Reference Architecture(10개 판단) | ADC | Kernel | Resolved(10개 전부 Accept, 5개 조건부) | DG-KERNEL-0005 | `docs/architecture/core/RFC-0005-kernel-logical-reference-architecture.md` | `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md`(교차 트리 — 판단 1~8) | 본문 참조 | `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md` | 2026-09-20 | High |
| ADC-0006 | Kernel Context Ownership(7개 판단) | ADC | Kernel | Resolved(Accept 5, Defer 2, Reject 1 — ADR 불필요) | DG-KERNEL-0006 | `docs/architecture/core/RFC-0006-kernel-context-ownership.md` | 없음(ADR 불필요 — 판정) | 본문 참조 | `docs/architecture/core/ADC-0006-kernel-context-ownership.md` | 2026-09-20 | High |
| ADC-0007 | Kernel Context Identity | ADC | Kernel | Resolved(핵심 주장 Reject — V-1을 닫는 잘못된 경로 제거, ADR 불필요) | DG-KERNEL-0007 | `docs/architecture/core/RFC-0007-kernel-context-identity.md` | 없음(ADR 불필요 — 판정) | 본문 참조 | `docs/architecture/core/ADC-0007-kernel-context-identity.md` | 2026-09-20 | High |

## 7. 검증 기준

- [ ] Document ID + Target Domain + Source Path 조합이 전역적으로 유일한가(Document ID + Target Domain만으로는 유일하지 않을 수 있음에 주의)
- [ ] Parent Documents(근거 RFC)가 실제로 존재하고 경로가 정확한가
- [ ] Status가 Resolved라면 Related Documents에 종결 ADR이 채워졌는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Last Verified가 갱신됐는가
