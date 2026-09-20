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
| Document ID | 트리 내부 고유 ID. 기존 파일명 규칙(`RFC-XXXX`)을 그대로 쓴다. Document ID + Target Domain만으로는 전역 유일성이 보장되지 않을 수 있다(`docs/decisions/adr.md`가 확인한 ADR-0002~0005 교차 트리 충돌과 같은 패턴이 RFC/ADC에도 이론상 가능) — 전역 유일 키는 Document ID + Target Domain + Source Path다 | Y |
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

> 신규 RFC 등록 창구. 아래 표는 이 원장 도입 이후 신규 작성되는 RFC와,
> 우선순위 검증을 거쳐 소급 등록된 RFC를 함께 관리한다. 과거 RFC 전체
> 목록은 여전히 `docs/decisions/rfc/README.md`가 Source of Truth다 —
> 이 표가 그 문서를 대체하지 않는다. 소급 등록 근거와 검증 범위는
> `docs/decisions/REGISTRATION-CANDIDATES-0001.md`를 참조한다.

| Document ID | Title | Type | Target Domain | Status | Decision Group | Parent Documents | Related Documents | Evidence References | Source Path | Last Verified | Verification Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RFC-0001 | Spec-Repository Artifact Drift — Boundary | RFC | Execution Layer | Resolved(Not Accepted, ADR 불필요) | DG-EXECLAYER-0001 | 없음(논의 시작점) | `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | `docs/research/ENGINE-INTEGRATION-0001-Claude-Code.md`(원문 인용) | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | 2026-09-20 | High |
| RFC-0002 | Execution Result Contract — 산출물을 묶는 방식 | RFC | Execution Layer | Resolved | DG-EXECLAYER-0002 | 없음(논의 시작점) | `docs/core/execution-layer/ADC-0002-execution-result-contract.md`, `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | `docs/core/execution-layer/IMPL-STOP-0001-execution-result.md`, `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | 2026-09-20 | High |
| RFC-0003 | Execution Result Item Schema — 목록 항목의 형태 | RFC | Execution Layer | Resolved | DG-EXECLAYER-0003 | 없음(논의 시작점) | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md`, `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | `docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md`, `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | 2026-09-20 | High |
| RFC-0004 | Execution Result Consumer — 소비 주체와 방식 | RFC | Execution Layer | Resolved(Not Accepted, ADR 불필요) | DG-EXECLAYER-0004 | 없음(논의 시작점) | `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`, RFC-0002~ADR-0002 전체(원문 인용) | `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | 2026-09-20 | High |
| RFC-0005 | Engine 연결 Boundary — Execution Result에 실제 산출물을 연결하는 경계 | RFC | Execution Layer | Resolved(헤더 라벨은 `Proposed`로 미갱신 — 본문 대조로 ADC-0005 실제 존재·Decision 확인, D-9류 색인 부채) | DG-EXECLAYER-0005 | 없음(논의 시작점) | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`, `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`, `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | 2026-09-20 | High |
| RFC-0001 | Jarvis OS Kernel Baseline | RFC | Kernel | Resolved | DG-KERNEL-0001 | 없음(논의 시작점) | `docs/architecture/core/ADC-0001-core-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` | 2026-09-20 | High |
| RFC-0008 | Runtime 개념의 존폐 — Boundary | RFC | Kernel | Resolved(Not Accepted, ADR 불필요) | DG-KERNEL-0008 | 없음(논의 시작점) | `docs/architecture/core/ADC-0008-runtime-existence-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0008-runtime-existence-boundary.md` | 2026-09-20 | High |
| RFC-0009 | Model 축과 Component 축의 대응 관계 — Boundary | RFC | Kernel | Resolved(Not Accepted, ADR 불필요; 헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0009 | 없음(논의 시작점) | `docs/architecture/core/ADC-0009-model-component-correspondence-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0009-model-component-correspondence-boundary.md` | 2026-09-20 | High |
| RFC-0010 | Engine Caller의 위치와 책임 — Boundary | RFC | Kernel | Resolved(Not Accepted, ADR 불필요; 헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0010 | 없음(논의 시작점) | `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0010-engine-caller-location-boundary.md` | 2026-09-20 | High |
| RFC-0011 | Kernel/HQ에 속하지 않는 별도 실행 위치 — Boundary | RFC | Kernel | Resolved(Not Accepted, ADR 불필요; 헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0011 | 없음(논의 시작점) | `docs/architecture/core/ADC-0011-standalone-execution-location-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0011-standalone-execution-location-boundary.md` | 2026-09-20 | High |
| RFC-0012 | Dispatch Component의 Architecture Boundary | RFC | Kernel | Resolved(Defer, ADR 불필요; 헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0012 | 없음(논의 시작점) | `docs/architecture/core/ADC-0012-dispatch-component-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0012-dispatch-component-boundary.md` | 2026-09-20 | High |
| RFC-0013 | Runtime 존폐 — Boundary Scoped Reconsideration | RFC | Kernel | Resolved | DG-KERNEL-0013 | 없음(논의 시작점) | `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`, `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md` | 2026-09-20 | High |
| RFC-0014 | Execution 책임의 명칭 | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9, ADR-0004 관련 RFC 필드로 확인) | DG-KERNEL-0014 | 없음(논의 시작점) | `docs/architecture/core/ADC-0014-execution-responsibility-naming.md`, `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0014-execution-responsibility-naming.md` | 2026-09-20 | High |
| RFC-0015 | Execution Host 구현 전략 | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0015 | 없음(논의 시작점) | `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`, `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0015-execution-host-implementation-strategy.md` | 2026-09-20 | High |
| RFC-0016 | Multi-Task 최소 책임 | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0016 | 없음(논의 시작점) | `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`, `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md` | 2026-09-20 | High |
| RFC-0017 | Multi-Task Checkpointer Integrity Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9; 후속 ADC/ADR은 "result-store-integrity" 명칭으로 진행 — 동일 Decision Group, 명칭 변경만) | DG-KERNEL-0017 | 없음(논의 시작점) | `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md`, `docs/architecture/core/ADR-0007-multi-task-result-store-integrity-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md` | 2026-09-20 | Medium |
| RFC-0018 | Natural-Language Request → Multi-HQ Task Decomposition | RFC | Kernel | Open(Defer — ADC-0018 Decision: Defer Scoped, ADR 없음) | DG-KERNEL-0018 | 없음(논의 시작점) | `docs/architecture/core/ADC-0018-natural-language-request-multi-hq-task-decomposition.md` | 본문 참조 | `docs/architecture/core/RFC-0018-natural-language-request-multi-hq-task-decomposition.md` | 2026-09-20 | High |
| RFC-0019 | LangGraph-Scoped Workflow Adapter Runtime Existence Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0019 | 없음(논의 시작점) | `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`, `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md` | 2026-09-20 | High |
| RFC-0020 | Workflow Adapter Contract and Implementation Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0020 | 없음(논의 시작점) | `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md`, `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md` | 2026-09-20 | High |
| RFC-0021 | Workflow Adapter Execution Unit Lifecycle State Model Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9; 실제 종결 ADC는 번호가 다른 ADC-0022 — ADR-0011 관련 RFC/ADC 필드로 확인, RFC 원문 번호와 어긋남) | DG-KERNEL-0021 | 없음(논의 시작점) | `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md`, `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0021-workflow-adapter-execution-unit-lifecycle-state-model-boundary.md` | 2026-09-20 | Medium |
| RFC-0022 | Workflow Engine Port Contract Surface and Engine Seam Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9; 실제 종결 ADC는 번호가 다른 ADC-0023 — ADR-0012 관련 RFC/ADC 필드로 확인) | DG-KERNEL-0022 | 없음(논의 시작점) | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md`, `docs/architecture/core/ADR-0012-gate-a-decision-9-contract-surface-resolution-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0022-workflow-engine-port-contract-surface-and-engine-seam-boundary.md` | 2026-09-20 | Medium |
| RFC-0023 | Model Routing Engine Adapter Freeze Reconsideration Boundary | RFC | Kernel | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-KERNEL-0023 | 없음(논의 시작점) | `docs/architecture/core/ADC-0027~0031`(5건), `docs/architecture/core/ADR-0015~0017`(3건) | 본문 참조 | `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` | 2026-09-20 | High |
| RFC-0024 | Agent Domain and Lifecycle Contract | RFC | Kernel | Resolved(Reject — ADC-0032 Q1) | DG-KERNEL-0024 | 없음(논의 시작점) | `docs/architecture/core/ADC-0032-agent-domain-and-lifecycle-contract-resolution.md` | 본문 참조 | `docs/architecture/core/RFC-0024-agent-domain-and-lifecycle-contract.md` | 2026-09-20 | Medium |
| RFC-0025 | Agent State Message Event Contract | RFC | Kernel | Resolved(Not Accept, Defer — ADC-0033 Q1·Q2) | DG-KERNEL-0025 | 없음(논의 시작점) | `docs/architecture/core/ADC-0033-agent-state-message-event-contract-resolution.md` | 본문 참조 | `docs/architecture/core/RFC-0025-agent-state-message-event-contract.md` | 2026-09-20 | Medium |
| RFC-0026 | Multi-Agent Workflow Contract Candidate Boundary | RFC | Kernel | Open(조사·분석 기록 — 문서 자신이 "Baseline 결정 아님"으로 명시, 후속 ADC 없음) | DG-KERNEL-0026 | 없음(논의 시작점) | 없음(후속 ADC 미작성) | 본문 참조 | `docs/architecture/core/RFC-0026-multi-agent-workflow-contract-candidate-boundary.md` | 2026-09-20 | Low |
| RFC-0027 | Multi-Agent Runtime Contract Candidate Boundary | RFC | Kernel | Open(조사·분석 기록 — 문서 자신이 "Baseline 결정 아님"으로 명시, 후속 ADC 없음) | DG-KERNEL-0027 | 없음(논의 시작점) | 없음(후속 ADC 미작성) | 본문 참조 | `docs/architecture/core/RFC-0027-multi-agent-runtime-contract-candidate-boundary.md` | 2026-09-20 | Low |
| RFC-0028 | Minimal Runtime MVP Necessity Verification | RFC | Kernel | Open(조사·분석 기록 — 문서 자신이 "Baseline 결정 아님"으로 명시, 후속 ADC 없음) | DG-KERNEL-0028 | 없음(논의 시작점) | 없음(후속 ADC 미작성) | 본문 참조 | `docs/architecture/core/RFC-0028-minimal-runtime-mvp-necessity-verification.md` | 2026-09-20 | Low |
| RFC-0029 | Dev HQ Stage Agent Boundary Analysis | RFC | Kernel | Open(조사·분석 기록 — 문서 자신이 "Baseline 결정 아님"으로 명시, 후속 ADC 없음) | DG-KERNEL-0029 | 없음(논의 시작점) | 없음(후속 ADC 미작성) | 본문 참조 | `docs/architecture/core/RFC-0029-dev-hq-stage-agent-boundary-analysis.md` | 2026-09-20 | Low |
| RFC-0030 | Dev HQ Stage Agent Team Boundary Analysis | RFC | Kernel | Open(조사·분석 기록 — 문서 자신이 "Baseline 결정 아님"으로 명시, 후속 ADC 없음) | DG-KERNEL-0030 | 없음(논의 시작점) | 없음(후속 ADC 미작성) | 본문 참조 | `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md` | 2026-09-20 | Low |
| RFC-0031 | LangGraph Implementation Technology Adoption | RFC | Kernel | Resolved | DG-KERNEL-0031 | 없음(논의 시작점) | `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md`, `docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0031-langgraph-implementation-technology-adoption.md` | 2026-09-20 | High |
| RFC-0032 | Graphify Implementation Technology Adoption | RFC | Kernel | Resolved | DG-KERNEL-0032 | 없음(논의 시작점) | `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md`, `docs/architecture/core/ADR-0020-graphify-implementation-technology-adoption.md` | 본문 참조 | `docs/architecture/core/RFC-0032-graphify-implementation-technology-adoption.md` | 2026-09-20 | High |
| RFC-0033 | Stage01 Multi-Agent Reasoning Adoption | RFC | Kernel | Resolved | DG-KERNEL-0033 | 없음(논의 시작점) | `docs/architecture/core/ADC-0036-stage01-multi-agent-reasoning-resolution.md`, `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0033-stage01-multi-agent-reasoning-adoption.md` | 2026-09-20 | High |
| RFC-0034 | Stage01 PRD Specification Synthesis | RFC | Kernel | Resolved | DG-KERNEL-0034 | 없음(논의 시작점) | `docs/architecture/core/ADC-0037-stage01-prd-specification-synthesis-resolution.md`, `docs/architecture/core/ADR-0022-stage01-prd-specification-synthesis-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0034-stage01-prd-specification-synthesis.md` | 2026-09-20 | High |
| RFC-0035 | Stage02 Planning Responsibility and Execution Model | RFC | Kernel | Resolved | DG-KERNEL-0035 | 없음(논의 시작점) | `docs/architecture/core/ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md`, `docs/architecture/core/ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md` | 본문 참조 | `docs/architecture/core/RFC-0035-stage02-planning-responsibility-and-execution-model.md` | 2026-09-20 | High |
| RFC-0036 | ChatGPT/Claude Code Dual-Engine Boundary | RFC | Kernel | Resolved | DG-KERNEL-0036 | 없음(논의 시작점) | `docs/architecture/core/ADC-0039-multi-engine-re-evaluation.md`(RE-EVALUATE), `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md` | 본문 참조 | `docs/architecture/core/RFC-0036-chatgpt-claude-code-dual-engine-boundary.md` | 2026-09-20 | High |
| RFC-0037 | Stage04 Multi-Agent Ponytail Boundary | RFC | Kernel | Open(ADC-0040: NOT DETERMINED — Real Engine Evidence Required) | DG-KERNEL-0037 | 없음(논의 시작점) | `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md` | 본문 참조 | `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md` | 2026-09-20 | High |
| RFC-0038 | Stage05 QA Multi-Agent Boundary | RFC | Kernel | Open(ADC-0041: NOT DETERMINED — Real Engine Evidence Required) | DG-KERNEL-0038 | 없음(논의 시작점) | `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md` | 본문 참조 | `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md` | 2026-09-20 | High |
| RFC-0039 | Stage05 Parallel Validation DAG | RFC | Kernel | Resolved(Partial — Independence Confirmed, Production Adoption Not Determined) | DG-KERNEL-0039 | 없음(논의 시작점) | `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`, `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md` | 2026-09-20 | High |
| RFC-0040 | OpenRouter Free Model Selection Architecture | RFC | Kernel | Resolved(Partial — Boundary Confirmed, Concrete API Adoption Not Determined) | DG-KERNEL-0040 | 없음(논의 시작점) | `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`, `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md` | 2026-09-20 | High |
| RFC-0041 | OpenRouter Production Engine Migration | RFC | Kernel | Resolved(Partial — Architecture Adoption Accepted, Operational Reliability 별도 유보) | DG-KERNEL-0041 | 없음(논의 시작점) | `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md`, `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md` | 본문 참조 | `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md` | 2026-09-20 | High |
| RFC-0042 | Repository-Wide Python Audit and Refactoring Governance | RFC | Kernel | Resolved(Scoped — Governance Lifecycle Accepted, Implementation 별도 승인 필요) | DG-KERNEL-0042 | 없음(논의 시작점) | `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`, `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | 본문 참조 | `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` | 2026-09-20 | High |
| RFC-0043 | Execution History Evidence Persistence Architecture | RFC | Kernel | Open(후속 RFC-0044로 범위가 좁혀짐 — 자체 ADC 없음) | DG-KERNEL-0043 | 없음(논의 시작점) | 없음(RFC-0044가 범위를 좁혀 승계) | 본문 참조 | `docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md` | 2026-09-20 | Medium |
| RFC-0044 | Narrow Execution History Verification Persistence Boundary | RFC | Kernel | Resolved(Not Accepted, ADR 불필요 — Boundary Question은 Open으로 남음) | DG-KERNEL-0043 | 없음(논의 시작점) | `docs/architecture/core/ADC-0046-workflow-execution-history-verification-persistence-ownership-boundary.md` | 본문 참조 | `docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md` | 2026-09-20 | High |
| RFC-0001 | Kernel Boundary | RFC | Development HQ | Resolved(ADR 불필요) | DG-DEVHQ-0001 | 없음(논의 시작점) | `docs/governance/adc/ADC-0001.md` | 본문 참조 | `docs/decisions/rfc/RFC-0001-kernel-boundary.md` | 2026-09-20 | High |
| RFC-0002 | Task Dispatcher Boundary (재평가) | RFC | Development HQ | Resolved(ADR 불필요) | DG-DEVHQ-0002 | 없음(논의 시작점) | `docs/governance/adc/ADC-0002.md` | 본문 참조 | `docs/decisions/rfc/RFC-0002-task-dispatcher-boundary.md` | 2026-09-20 | High |
| RFC-0003 | Development HQ를 AI Native SDLC Platform으로 재정의 | RFC | Development HQ | Resolved | DG-DEVHQ-0003 | 없음(논의 시작점) | `docs/governance/adc/ADC-0003.md`, `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md`(판단 1에 한해) | 본문 참조 | `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` | 2026-09-20 | High |
| RFC-0004 | Task Dispatcher → Runtime 승격 Boundary(Governance v2 Rule A) | RFC | Development HQ | Resolved(ADR 불필요) | DG-DEVHQ-0004 | 없음(논의 시작점) | `docs/governance/adc/ADC-0004.md` | 본문 참조 | `docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md` | 2026-09-20 | High |
| RFC-0005 | Development HQ ↔ Execution Layer Boundary | RFC | Development HQ | Open(후속 ADC 미작성 — 저장소 내 유일한 순수 Open RFC) | DG-DEVHQ-0005 | 없음(논의 시작점) | 없음(미작성) | 본문 참조 | `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md` | 2026-09-20 | High |
| RFC-0006 | Structure v1.0 — hqs/, core/execution/ 재배치 및 docs Taxonomy 정리 | RFC | Development HQ | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-DEVHQ-0006 | 없음(논의 시작점) | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md`, `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md`, `docs/decisions/adr/ADR-0006-structure-v1-migration.md`, `docs/decisions/adr/ADR-0007-baseline-relocation.md` | 본문 참조 | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | 2026-09-20 | High |
| RFC-0007 | AST 기반 Context 자동 추출의 Production Build Capability 통합 | RFC | Development HQ | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-DEVHQ-0007 | 없음(논의 시작점) | `docs/governance/adc/ADC-0005.md`(4개 판단 전부 Accept, 전부 No ADR Required) | 본문 참조 | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md` | 2026-09-20 | High |
| RFC-0008 | AST Context Module Discovery — Dotted Package Path 지원 확장 여부 | RFC | Development HQ | Resolved(헤더 `Proposed` 미갱신 — D-9) | DG-DEVHQ-0008 | 없음(논의 시작점) | `docs/governance/adc/ADC-0006.md`(Decision B, Conditional Accept) | 본문 참조 | `docs/decisions/rfc/RFC-0008-agents-module-physical-layout-boundary.md` | 2026-09-20 | Medium |
| RFC-0009 | Stage Data Contract — 후보 C, Scoped Accept | RFC | Development HQ | Resolved | DG-DEVHQ-0009 | 없음(논의 시작점) | `docs/governance/adc/ADC-0007.md` | 본문 참조 | `docs/decisions/rfc/RFC-0009-stage-data-contract.md` | 2026-09-20 | High |
| RFC-0010 | Outcome-Oriented Governance Model 도입 여부 | RFC | Development HQ | Resolved(Scoped Accept) | DG-DEVHQ-0010 | 없음(논의 시작점) | `docs/governance/adc/ADC-0008.md`, `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md` | 본문 참조 | `docs/decisions/rfc/RFC-0010-outcome-oriented-governance-model.md` | 2026-09-20 | High |
| RFC-0011 | "Implementation Freedom" 원칙 도입 여부 | RFC | Development HQ | Resolved(Scoped Accept) | DG-DEVHQ-0011 | 없음(논의 시작점) | `docs/governance/adc/ADC-0009.md`, `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md` | 본문 참조 | `docs/decisions/rfc/RFC-0011-implementation-freedom-principle.md` | 2026-09-20 | High |
| RFC-0002 | Kernel Definition — Responsibility, Not Component | RFC | Kernel | Resolved(종결 ADR이 물리적으로 `docs/decisions/adr/`에 위치 — §Note 참조) | DG-KERNEL-0002 | 없음(논의 시작점) | `docs/architecture/core/ADC-0002-kernel-definition.md`, `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md`(교차 트리) | 본문 참조 | `docs/architecture/core/RFC-0002-kernel-definition.md` | 2026-09-20 | Medium |
| RFC-0003 | Kernel Context Model — Context, Builder, Assembly, Prompt Projection | RFC | Kernel | Resolved(종결 ADR 교차 트리) | DG-KERNEL-0003 | 없음(논의 시작점) | `docs/architecture/core/ADC-0003-kernel-context-model.md`, `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md`(교차 트리) | 본문 참조 | `docs/architecture/core/RFC-0003-kernel-context-model.md` | 2026-09-20 | Medium |
| RFC-0004 | Kernel Public Contract | RFC | Kernel | Resolved(종결 ADR 교차 트리) | DG-KERNEL-0004 | 없음(논의 시작점) | `docs/architecture/core/ADC-0004-kernel-public-contract.md`, `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md`(교차 트리) | 본문 참조 | `docs/architecture/core/RFC-0004-kernel-public-contract.md` | 2026-09-20 | Medium |
| RFC-0005 | Kernel Logical Reference Architecture — 책임의 배선도 | RFC | Kernel | Resolved(종결 ADR 교차 트리) | DG-KERNEL-0005 | 없음(논의 시작점) | `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md`, `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md`(교차 트리) | 본문 참조 | `docs/architecture/core/RFC-0005-kernel-logical-reference-architecture.md` | 2026-09-20 | Medium |
| RFC-0006 | Kernel Context Ownership | RFC | Kernel | Resolved(ADR 불필요) | DG-KERNEL-0006 | 없음(논의 시작점) | `docs/architecture/core/ADC-0006-kernel-context-ownership.md` | 본문 참조 | `docs/architecture/core/RFC-0006-kernel-context-ownership.md` | 2026-09-20 | High |
| RFC-0007 | Kernel Context Identity | RFC | Kernel | Resolved(ADR 불필요) | DG-KERNEL-0007 | 없음(논의 시작점) | `docs/architecture/core/ADC-0007-kernel-context-identity.md` | 본문 참조 | `docs/architecture/core/RFC-0007-kernel-context-identity.md` | 2026-09-20 | High |

## 7. 검증 기준

새 행을 추가하기 전에 다음을 확인한다.

- [ ] Document ID가 대상 Target Domain 트리 내에서 중복되지 않는가
- [ ] Source Path의 파일이 실제로 존재하는가
- [ ] Status가 원문 헤더가 아니라 후속 ADC/ADR 존재 여부로 판단됐는가
- [ ] Related Documents에 적힌 경로가 실제로 존재하는가(존재하지 않으면 `Undetermined`)
- [ ] Last Verified가 오늘 날짜로 갱신됐는가
