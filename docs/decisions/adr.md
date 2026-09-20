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
| Document ID | 트리 내부 고유 ID(예: `ADR-0006`). **Document ID + Target Domain만으로는 전역 유일성이 보장되지 않는다** — 예: `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`와 `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md`는 물리적으로 다른 두 파일이지만 둘 다 Document ID `ADR-0002`, 둘 다 내용상 Target Domain `Kernel`이다(ADR-0002~0005 4건 전부 이 패턴). 전역 유일 키는 Document ID + Target Domain + Source Path다 | Y |
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
> `docs/architecture/core/`(Kernel 수준 ADR-0001~0028) 28건 전부를 원문
> 대조 후 아래에 등록했다 — 근거는
> `docs/decisions/REGISTRATION-CANDIDATES-0001.md` §3.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR-0001 | Execution Result Contract(여섯 번째 Artifact)의 Contract 형태(목록형)를 Artifact Standard에 반영 | ADR | Execution Layer | Accepted | DG-EXECLAYER-0002 | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` §Artifact 6(반영 확인) | 본문 참조 | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | 2026-09-20 | High |
| ADR-0002 | Execution Result 목록 항목의 타입(`list[str]`)을 Artifact Standard에 반영 | ADR | Execution Layer | Accepted | DG-EXECLAYER-0003 | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` §Artifact 6(반영 확인) | 본문 참조 | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | 2026-09-20 | High |
| ADR-0001 | Governance Kernel Module의 Baseline 반영(§16 신설) | ADR | Kernel | Accepted | DG-KERNEL-0001 | `docs/architecture/core/ADC-0001-core-baseline.md` Module 1(Governance) | `docs/architecture/baseline/BASELINE.md` §16(반영 확인됨 — v1.5) | 본문 참조 | `docs/architecture/core/ADR-0001-governance-module-baseline.md` | 2026-09-20 | High |
| ADR-0002 | Execution Layer Kernel Module의 Baseline 반영(§16 신설) | ADR | Kernel | Accepted | DG-KERNEL-0001 | `docs/architecture/core/ADC-0001-core-baseline.md` Module 4(Execution Layer) | `docs/architecture/baseline/BASELINE.md` §16.2(반영 확인됨 — v1.6) | 본문 참조 | `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | 2026-09-20 | High |
| ADR-0003 | Single Execution Unit Dispatch Isolation Baseline | ADR | Kernel | Accepted | DG-KERNEL-0013 | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` | `docs/architecture/baseline/BASELINE.md` §16.3(반영 확인됨 — v1.7) | 본문 참조 | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` | 2026-09-20 | High |
| ADR-0004 | Execution Host Naming Baseline | ADR | Kernel | Accepted | DG-KERNEL-0014 | `docs/architecture/core/ADC-0014-execution-responsibility-naming.md` | `docs/architecture/baseline/BASELINE.md` §16.3(반영 확인됨 — v1.8) | 본문 참조 | `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md` | 2026-09-20 | High |
| ADR-0005 | Execution Host Implementation Strategy Baseline | ADR | Kernel | Accepted | DG-KERNEL-0015 | `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md` | `docs/architecture/baseline/BASELINE.md` §16.3(반영 확인됨 — v1.9) | 본문 참조 | `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md` | 2026-09-20 | High |
| ADR-0006 | Multi-Task Minimal Responsibility Baseline | ADR | Kernel | Accepted | DG-KERNEL-0016 | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md` | `docs/architecture/baseline/BASELINE.md` §16.4(반영 확인됨 — v1.10) | 본문 참조 | `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md` | 2026-09-20 | High |
| ADR-0007 | Multi-Task Result Store Integrity Baseline | ADR | Kernel | Accepted | DG-KERNEL-0017 | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` | `docs/architecture/baseline/BASELINE.md` §16.5(반영 확인됨 — v1.11) | 본문 참조 | `docs/architecture/core/ADR-0007-multi-task-result-store-integrity-baseline.md` | 2026-09-20 | High |
| ADR-0008 | Scoped Workflow Graph Execution Baseline(§16.6 신설, v1.11→v1.12) | ADR | Kernel | Accepted(2026-09-02) | DG-KERNEL-0019 | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` | `docs/architecture/baseline/BASELINE.md` §16.6·§17(버전 이력 기재) | 본문 참조 | `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md` | 2026-09-20 | High |
| ADR-0009 | Workflow Adapter Naming and Contract Baseline(§16.6, v1.12→v1.13) | ADR | Kernel | Accepted | DG-KERNEL-0020 | `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` | `docs/architecture/baseline/BASELINE.md` §16.6·§17, `GLOSSARY.md` | 본문 참조 | `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md` | 2026-09-20 | High |
| ADR-0010 | Gate (C) E4 Reversibility 부분 충족(§16.6, v1.13→v1.14) | ADR | Kernel | Accepted | DG-KERNEL-0019-GATE | `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md` §8 Gate (C) | `docs/architecture/baseline/BASELINE.md` §16.6·§17, `GLOSSARY.md` | 본문 참조 | `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md` | 2026-09-20 | High |
| ADR-0011 | Gate (A) 결정 2·5·11 Resolution Baseline(v1.14→v1.15) | ADR | Kernel | Accepted(사용자 승인 2026-09-04) | DG-KERNEL-0021 | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` | `docs/architecture/baseline/BASELINE.md` §16.6·§17, `GLOSSARY.md` | 본문 참조 | `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md` | 2026-09-20 | High |
| ADR-0012 | Gate (A) 결정 9 Contract Surface Resolution Baseline(v1.15→v1.16) | ADR | Kernel | Accepted(사용자 승인 2026-09-04) | DG-KERNEL-0022 | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` | `docs/architecture/baseline/BASELINE.md` §14·§16.6·§17, `GLOSSARY.md` — feature branch `claude/adr-0012-decision-9-baseline-v1.16`에 반영, main 직접 Merge 없음 | 본문 참조 | `docs/architecture/core/ADR-0012-gate-a-decision-9-contract-surface-resolution-baseline.md` | 2026-09-20 | High |
| ADR-0013 | Gate (B) Partial Relaxation Baseline(v1.16→v1.17) | ADR | Kernel | Accepted | DG-KERNEL-0019-GATE | `docs/architecture/core/ADC-0024-gate-b-independent-observation-threshold-judgment.md` | `docs/architecture/baseline/BASELINE.md` §16.6·§17, `GLOSSARY.md` | 본문 참조 | `docs/architecture/core/ADR-0013-gate-b-partial-relaxation-baseline.md` | 2026-09-20 | High |
| ADR-0014 | Gate (B) Second Lineage Partial Relaxation Baseline(v1.17→v1.18) | ADR | Kernel | Accepted | DG-KERNEL-0019-GATE | `docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md` | `docs/architecture/baseline/BASELINE.md` §16.6·§17, `GLOSSARY.md` | 본문 참조 | `docs/architecture/core/ADR-0014-gate-b-second-lineage-partial-relaxation-baseline.md` | 2026-09-20 | High |
| ADR-0015 | OmniRoute Thin Engine Caller Adoption Policy(Consolidation Only) | ADR | Kernel | Accepted(Consolidation Only — Baseline/Rules 문구 미반영, 후속 ADR 대상) | DG-KERNEL-0023 | `docs/architecture/core/ADC-0027~0031`(5건) | 없음(문구 반영은 후속 ADR로 명시적 이월 — §13 Open Conditions) | 본문 참조 | `docs/architecture/core/ADR-0015-omniroute-thin-engine-caller-adoption-policy.md` | 2026-09-20 | High |
| ADR-0016 | OmniRoute Thin Caller Freeze Scoped Relaxation | ADR | Kernel | Accepted | DG-KERNEL-0023 | `docs/architecture/core/ADC-0027~0031`(5건) | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0016-omniroute-thin-caller-freeze-scoped-relaxation.md` | 2026-09-20 | High |
| ADR-0017 | OmniRoute Production Adoption Final Review(Scoped) | ADR | Kernel | Accepted(Production Adoption 선언, Scoped: OmniRoute Thin Engine Caller 형태 한정) | DG-KERNEL-0023 | `docs/architecture/core/ADC-0027~0031`(5건) | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0017-omniroute-production-adoption-final-review.md` | 2026-09-20 | High |
| ADR-0018 | LangGraph Adoption Final Review(Consolidation, 10 RFC/10 ADC 종합) | ADR | Kernel | Accepted(LangGraph는 Deferred/Not Adopted로 종결 — 2026-09-08 `ADR-0019`가 이 판정을 부분 Supersede) | DG-KERNEL-0019-GATE | `docs/architecture/core/RFC-0019~0022,0024~0030`(다수) | `docs/architecture/core/ADC-0019~0026,0032,0033`(다수) — Superseded by `docs/architecture/core/ADR-0019` (부분) | 본문 참조 | `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md` | 2026-09-20 | Medium |
| ADR-0019 | LangGraph Implementation Technology Adoption Baseline | ADR | Kernel | Accepted | DG-KERNEL-0031 | `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md` | `docs/architecture/core/ADR-0018`(부분 Supersede — LangGraph를 승인된 비강제 구현 후보로 사전 확정) | 본문 참조 | `docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md` | 2026-09-20 | High |
| ADR-0020 | Graphify Implementation Technology Adoption | ADR | Kernel | Accepted | DG-KERNEL-0032 | `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md` | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0020-graphify-implementation-technology-adoption.md` | 2026-09-20 | High |
| ADR-0021 | Stage01 Multi-Agent Reasoning Adoption Baseline | ADR | Kernel | Accepted | DG-KERNEL-0033 | `docs/architecture/core/ADC-0036-stage01-multi-agent-reasoning-resolution.md` | `hqs/development/stages/01_context_analysis/RESPONSIBILITY.md`·`CONTEXT.md`(반영 확인됨 — ADR-0021 인용 확인) | 본문 참조 | `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md` | 2026-09-20 | High |
| ADR-0022 | Stage01 PRD Specification Synthesis Baseline | ADR | Kernel | Accepted | DG-KERNEL-0034 | `docs/architecture/core/ADC-0037-stage01-prd-specification-synthesis-resolution.md` | `hqs/development/stages/01_context_analysis/CONTEXT.md`·`RESPONSIBILITY.md`(반영 확인됨 — ADR-0022 인용 확인) | 본문 참조 | `docs/architecture/core/ADR-0022-stage01-prd-specification-synthesis-baseline.md` | 2026-09-20 | High |
| ADR-0023 | Stage02 Planning Responsibility and Execution Model Baseline | ADR | Kernel | Accepted | DG-KERNEL-0035 | `docs/architecture/core/ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md` | `hqs/development/stages/02_planning_specification/CAPABILITIES.md`·`README.md`(반영 확인됨 — ADR-0023 인용 확인) | 본문 참조 | `docs/architecture/core/ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md` | 2026-09-20 | High |
| ADR-0024 | Multi-Engine Architecture Adoption(2-Engine: ChatGPT/Claude Code) | ADR | Kernel | Accepted | DG-KERNEL-0036 | `docs/architecture/core/ADC-0039-multi-engine-re-evaluation.md`(Amendment), `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md` | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md` | 2026-09-20 | High |
| ADR-0025 | Stage05 Parallel Validation Architecture Boundary(Scoped) | ADR | Kernel | Accepted(Scoped — Independence/Isolation/Aggregation Boundary만 확정, Production Adoption·Validator LLM Adoption은 NOT YET DETERMINED) | DG-KERNEL-0039 | `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md` | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md` | 2026-09-20 | High |
| ADR-0026 | OpenRouter Free Model Selection Architecture Boundary(Scoped) | ADR | Kernel | Accepted(Scoped — Architecture Boundary만 확정, Concrete API 구현·Production Routing 실통합은 NOT YET DETERMINED) | DG-KERNEL-0040 | `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md` | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md` | 2026-09-20 | High |
| ADR-0027 | OpenRouter Production Engine Migration Adoption(Scoped) | ADR | Kernel | Accepted(Scoped — Production Routing Integration/3번째 Engine 승인, §9 Operational Validation은 NOT YET DETERMINED) | DG-KERNEL-0041 | `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md`, `docs/architecture/core/ADC-0043`(재인용) | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md` | 2026-09-20 | High |
| ADR-0028 | Repository-Wide Python Audit and Refactoring Governance Adoption(Scoped) | ADR | Kernel | Accepted(Scoped — Governance Lifecycle만 확정, 실제 Wave 실행은 NOT YET AUTHORIZED) | DG-KERNEL-0042 | `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`, `docs/architecture/core/ADC-0040`(재인용, 여전히 Open) | 본문 참조 | 본문 참조 | `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | 2026-09-20 | High |
| ADR-0001 | Development HQ Baseline에 Stage 기반 구조 반영(ADC-0003 판단 1) | ADR | Development HQ | Accepted(§2/§6은 ADR-0008이 Supersede — 문서 자체는 수정 안 함) | DG-DEVHQ-0003 | `docs/governance/adc/ADC-0003.md` 판단 1 | Dev HQ 자체 Baseline 문서(확인 필요 — 이번 라운드 미대조) | 본문 참조 | `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md` | 2026-09-20 | High |
| ADR-0006 | hqs/, core/execution/ 재배치 및 docs/ Taxonomy 정리 Migration Decision 확정 | ADR | Development HQ | Accepted(Decision만 확정, Migration 실행은 범위 밖) | DG-DEVHQ-0006 | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | 확인 필요 — 이번 라운드 미대조 | 본문 참조 | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | 2026-09-20 | High |
| ADR-0007 | Architecture Baseline 문서의 Structure v1.0 위치 확정 | ADR | Development HQ | Accepted(위치·Reference 정합성만 확정, 이동 미실행) | DG-DEVHQ-0006 | `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` | 확인 필요 — 이번 라운드 미대조 | 본문 참조 | `docs/decisions/adr/ADR-0007-baseline-relocation.md` | 2026-09-20 | High |
| ADR-0008 | Stage 폴더의 문서+실행 코드 공존 허용(Architecture Owner 직접 지시) | ADR | Development HQ | Accepted | DG-DEVHQ-0003 | 없음(직접 지시 — ADC 경유 없음) | 확인 필요 — 이번 라운드 미대조 | 본문 참조 | `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md` | 2026-09-20 | High |
| ADR-0009 | Stage Data Contract Baseline 반영 | ADR | Development HQ | Accepted | DG-DEVHQ-0009 | `docs/governance/adc/ADC-0007.md` | 확인 필요 — 이번 라운드 미대조 | 본문 참조 | `docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md` | 2026-09-20 | High |
| ADR-0010 | Outcome-Oriented Governance Model 명칭·역할·원칙의 Baseline 반영 | ADR | Development HQ | Accepted | DG-DEVHQ-0010 | `docs/governance/adc/ADC-0008.md` | `docs/governance/README.md` §"Outcome-Oriented Governance Model"(반영 확인됨) | 본문 참조 | `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md` | 2026-09-20 | High |
| ADR-0011 | "Implementation Freedom" 원칙의 Baseline 반영 | ADR | Development HQ | Accepted | DG-DEVHQ-0011 | `docs/governance/adc/ADC-0009.md` | `docs/governance/README.md` §"Implementation Freedom"(반영 확인됨) | 본문 참조 | `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md` | 2026-09-20 | High |
| ADR-0002 | Core → Kernel 용어 통합 및 Kernel 정의의 Baseline 반영 | ADR | Kernel | Accepted(교차 트리 — 물리 경로는 docs/decisions/adr/, 내용은 Kernel §11·§12. 동일 ID `ADR-0002`가 Kernel Target Domain에 이미 등록된 `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`와 별개 문서 — Source Path로만 구분됨. §Note 참조) | DG-KERNEL-0002 | `docs/architecture/core/ADC-0002-kernel-definition.md` 판단 1·3·4 | `docs/architecture/baseline/BASELINE.md` §11·§12(v1.1, 반영 확인됨) | 본문 참조 | `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md` | 2026-09-20 | High |
| ADR-0003 | Kernel Context Model의 Baseline 반영 | ADR | Kernel | Accepted(교차 트리 — Kernel Target Domain ADR-0003(`single-execution-unit-dispatch-isolation`, architecture/core)과 Document ID 동일, Source Path로만 구분) | DG-KERNEL-0003 | `docs/architecture/core/ADC-0003-kernel-context-model.md` 판단 1·2·3·5·6a | `docs/architecture/baseline/BASELINE.md` §13(v1.2, 반영 확인됨) | 본문 참조 | `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md` | 2026-09-20 | High |
| ADR-0004 | Kernel Public Contract의 Baseline 반영 | ADR | Kernel | Accepted(교차 트리 — Kernel Target Domain ADR-0004(`execution-host-naming`, architecture/core)과 Document ID 동일, Source Path로만 구분) | DG-KERNEL-0004 | `docs/architecture/core/ADC-0004-kernel-public-contract.md` 판단 1~8 | `docs/architecture/baseline/BASELINE.md` §14(v1.3, 반영 확인됨) | 본문 참조 | `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md` | 2026-09-20 | High |
| ADR-0005 | Kernel Logical Reference Architecture의 Baseline 반영과 §10 범위 한정 | ADR | Kernel | Accepted(교차 트리 — Kernel Target Domain ADR-0005(`execution-host-implementation-strategy`, architecture/core)과 Document ID 동일, Source Path로만 구분) | DG-KERNEL-0005 | `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md` 판단 1~8 | `docs/architecture/baseline/BASELINE.md` §15(v1.4, 반영 확인됨) — §10 첫 항목 문언 한정 포함 | 본문 참조 | `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md` | 2026-09-20 | High |

## 7. 검증 기준

- [ ] Document ID + Target Domain + Source Path 조합이 전역적으로 유일한가(Document ID + Target Domain만으로는 유일하지 않을 수 있음에 주의 — ADR-0002~0005 교차 트리 사례 참조)
- [ ] Parent Documents(종결 ADC 또는 직접 지시 사유)가 명시됐는가
- [ ] Status가 Accepted라면 실제 Baseline 반영 위치가 Related Documents에 있는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Last Verified가 갱신됐는가
