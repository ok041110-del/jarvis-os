# Document Inventory — `docs/` 전체 Markdown 문서 목록 (0001)

**문서 성격**: 이번 단계는 **Inventory 작성만** 수행한다. 통합 원장
(Consolidated Ledger) 4개 생성과 각 문서에 Front Matter를 삽입하는
작업은 이 문서의 범위가 아니며 다음 단계로 명시적으로 보류한다.
이 문서는 `docs/` 하위 어떤 파일도 이동·삭제·내용 수정·번호 변경
하지 않는다 — 순수 READ-ONLY 조사 산출물이다.

## 0. 배경

Issue #206 후속 작업. 지금까지의 세션(PR #207~#211)은 `docs/decisions/`
+ `docs/governance/adc/` + `docs/architecture/core/` +
`docs/core/execution-layer/` 범위의 RFC/ADC/ADR 141개 문서만 전수
조사했다(`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`,
`DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md`,
`MAIN-BRANCH-FULL-VALIDATION-0002.md`). 이번 Inventory는 그 범위를
**`docs/` 전체(449개 Markdown 파일)**로 확장해, RFC/ADC/ADR이 아닌
문서(MVP Observation/Plan, Evidence, Governance Review, Freeze,
Baseline, Research/Investigation, Index/README, Template 등)까지
포함한 완전한 목록을 만든다.

## 1. 방법론

### 1.1 수집 범위

`docs/` 하위 전체 디렉터리를 재귀 스캔했다(`os.walk`). `.md` 확장자
파일만 대상으로 하며, `archive/`(저장소 루트의 별도 Frozen 영역,
`docs/` 하위가 아님)는 애초에 스캔 범위 밖이다.

```
docs/00_governance/  2개
docs/01_mvp/         53개
docs/architecture/   155개
docs/core/           27개
docs/decisions/      33개
docs/governance/     21개
docs/research/       158개
합계                 449개
```

### 1.2 Document ID 추출 규칙

- 파일명이 `RFC-####`, `ADC-####`, `ADR-####`, `RT-####`, `OBS-####`,
  `MVP-####`, `EVIDENCE-####`, `EVIDENCE-INVENTORY-####`,
  `GOVERNANCE-REVIEW-####`, `VALIDATION-####`, `STABILITY-####`,
  `DOC-TRIAGE-####`, `CLOSURE-####`, `COMPONENT-CANDIDATE-####`,
  `IMPLEMENTATION-PRIORITY-####`, `IMPL-ENTRY-####`, `IMPL-STOP-####`,
  `EFFICIENCY-AUDIT-####` 패턴으로 **시작**하면 그 접두사를 Document
  ID로, 대응 유형을 Type으로 채택한다.
- `README.md`, `*-TEMPLATE.md`, `ADC.md`, `BASELINE.md`,
  `STRUCTURE-V1.0-FROZEN.md`, `ARCHITECTURE_GOVERNANCE.md`,
  `GLOSSARY.md`, `DECISION-GROUP-REGISTRY.md`, `RFC_CANDIDATES.md`,
  파일명에 `FREEZE`/`CLOSURE`가 포함된 파일은 별도 규칙으로 분류했다.
- **`docs/research/` 하위 파일은 파일명이 `RFC-0008-...`,
  `ADC-0010-...`, `ADR-0027-...`처럼 다른 문서의 ID로 시작하더라도
  RFC/ADC/ADR로 분류하지 않는다** — 이런 이름은 "그 문서를 검토·재검증
  하는 연구 문서"라는 뜻이며, 실제 RFC/ADC/ADR 본체가 아니다(예:
  `docs/research/RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001.md`는
  RFC-0008 자체가 아니라 RFC-0008/ADC-0006의 준수 여부를 검증한
  이번 세션 자신의 산출물이다). 이 구분을 처음에 놓쳐 39건 중 3건이
  허위 3-way 충돌로 잘못 집계됐다가 스크립트 수정으로 정정했다(§4.2
  참고 — 검증 과정 자체를 투명하게 기록).
- 위 어느 패턴에도 해당하지 않으면 Document ID = 파일명(확장자 제외)
  전체를 그대로 사용한다(이 저장소의 `docs/research/`는 짧은 접두사
  대신 긴 서술형 파일명 자체가 사실상의 ID로 기능하는 컨벤션이다).

### 1.3 Type / Target Domain / Function 분류

- **Type**: 위 ID 추출 규칙과 동일한 근거로 결정(RFC/ADC/ADR/
  MVP-Doc/Evidence/Governance-Review/Validation/Stability-Audit/
  Doc-Triage/Closure/Component-Candidate/Implementation-Priority/
  Impl-Entry/Impl-Stop/Efficiency-Audit/Freeze/Architecture-Baseline/
  Governance-Policy/Registry/Pre-RFC-Candidate-List/Template/Index/
  Open-Decision-Index/Research-Investigation/Other).
- **Target Domain**: 파일 경로의 최상위~2단계 디렉터리로 결정
  (`docs/decisions/rfc` → Development HQ, `docs/architecture/core` →
  Kernel, `docs/core/execution-layer` → Execution Layer,
  `docs/governance/adc` → Development HQ, `docs/research` →
  Cross-cutting(Research) 등). **경로 기반 자동 분류이며 각 문서의
  실제 내용을 읽고 확정한 것이 아니다** — 특히 `docs/decisions/adr/`
  전체를 "Development HQ"로 자동 분류했으나, 이전 세션 조사
  (`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` §4.1)가 이미
  확인했듯 이 디렉터리에는 실제로 Kernel 소속 결정(ADR-0002~0005)이
  물리적으로 섞여 있다 — 그 13건은 Target Domain을 "Development
  HQ(Kernel 일부 혼재)"로 별도 표기했다(§3.2 표 참고).
- **Function**: 문서 최상위 `# ` 제목을 그대로(90자 이내로 축약)
  사용했다. 제목이 없으면 파일명을 사람이 읽기 쉬운 형태로 변환했다.
  **문서 본문 전체를 읽고 요약한 것이 아니다** — 제목만 근거로 한다.

### 1.4 Lifecycle

각 파일 상단 60줄 내에서 `Status` 또는 `상태` 필드를 정규식으로
탐색했다. 찾으면 그 값을, 못 찾으면 `Uncertain`을 기록했다.
**`Uncertain`은 "문서가 미결 상태"라는 뜻이 아니라 "자동 스캔이
명시적 Status 필드를 찾지 못했다"는 뜻이다** — 예를 들어
`BASELINE.md`는 실제로는 Active/현재 유효한 Baseline이지만 "Status:"
형식의 필드를 본문에 갖고 있지 않아 Uncertain으로 기록됐다. 449개
중 138개(31%)에서 명시적 Status 값을 찾았다(§3.1 통계).

### 1.5 Confidence

다음 조건을 만족하는 문서만 `Certain`으로 표기했다 — **이번 세션
또는 선행 세션(PR #207~#211)에서 본문 전체를 실제로 열람하고
Type/Domain/관계를 검증한 문서**(`docs/decisions/{rfc,adc,adr}/`
전체, `docs/governance/adc/ADC-0001~0010`, `docs/governance/
DECISION-GROUP-REGISTRY.md`, `docs/governance/README.md`, 이번
세션이 작성한 7개 `docs/research/*.md`, `docs/architecture/core/
STABILITY-0001`·`DOC-TRIAGE-0001`·`ADC-0023`·`ADC-0032`·`ADC-0033`·
`ADR-0018`·`VALIDATION-0001`, `docs/architecture/baseline/
BASELINE.md`). 나머지 **390개(87%)는 `Uncertain`**이다 — 파일명·
경로·최상위 제목만으로 분류했고 본문 전체를 검증하지 않았다는 뜻을
정직하게 반영한다.

## 2. Governance / Decisions / Research 3개 트리 간 관계

| 트리 | 역할 | 이 Inventory에서의 위치 |
|---|---|---|
| `docs/governance/` | Development HQ 수준의 확정된 Governance 절차·정책 기록(README 헌장, ADC-0001~0010, Observation, RT, **Decision Group Registry**) | §3.6 |
| `docs/decisions/` | Development HQ 수준의 RFC→ADC→ADR 표준 경로 산출물(신규 문서는 이 경로를 Canonical로 사용, `DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md` §7 재확인) | §3.5 |
| `docs/research/` | 위 두 트리의 결정을 사후에 검증·조사·감사하는 **2차 산출물**(Investigation/Review/Verification/Audit/Evidence) — 그 자체가 RFC/ADC/ADR이 아니며 Governance 절차의 어느 단계도 대체하지 않는다 | §3.7 |
| `docs/architecture/`, `docs/core/execution-layer/` | Kernel/Execution Layer 수준의 독립 RFC→ADC→ADR 트리(`docs/decisions/`·`docs/governance/`와 번호 재사용, 내용 중복 아님 — §4.1) | §3.3, §3.4 |
| `docs/00_governance/`, `docs/01_mvp/` | Structure v1 Migration 이전의 레거시 경로. 개별 파일 자체는 여전히 유효하게 참조되나(예: `ARCHITECTURE_GOVERNANCE.md`, `GLOSSARY.md`), 새 RFC/ADC/ADR을 위한 위치는 아니다 | §3.1, §3.2 |

**핵심 관계**: `docs/research/`의 다수 문서(158개 중 상당수)가
`docs/decisions/`·`docs/governance/`의 특정 RFC/ADC/ADR을 근거로
인용하거나 검증한다 — 그러나 이 Inventory는 그 개별 인용 관계
전부를 추적하지 않는다(그 작업은 이미 `docs/governance/
DECISION-GROUP-REGISTRY.md`가 일부 수행 중이며, §3.6에서 그 상태만
재확인한다).

## 3. 전체 인벤토리


### 3.1 `docs/00_governance/` (2개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` | ARCHITECTURE_GOVERNANCE | Governance-Policy | Architecture Governance | Cross-cutting Governance | Uncertain | Uncertain |
| `docs/00_governance/GLOSSARY.md` | GLOSSARY | Governance-Policy | Glossary | Cross-cutting Governance | Uncertain | Uncertain |

### 3.2 `docs/01_mvp/` (53개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/01_mvp/MVP-0002-observation.md` | MVP-0002 | MVP-Doc | MVP-0002 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0002-plan.md` | MVP-0002 | MVP-Doc | MVP-0002 Plan | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0003-plan.md` | MVP-0003 | MVP-Doc | MVP-0003 Plan | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0004-observation.md` | MVP-0004 | MVP-Doc | MVP-0004 Observation: Hello SDLC | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0004-plan.md` | MVP-0004 | MVP-Doc | MVP-0004 Plan: Hello SDLC | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0005-observation.md` | MVP-0005 | MVP-Doc | MVP-0005 Observation: Project Intelligence | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0006-observation.md` | MVP-0006 | MVP-Doc | MVP-0006 Observation: Project Intelligence를 Design Stage까지 전달 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0007-observation.md` | MVP-0007 | MVP-Doc | MVP-0007 Observation: Artifact Flow (Planning -> Design -> Implementation) | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0008-observation.md` | MVP-0008 | MVP-Doc | MVP-0008 Observation: Development HQ가 실제 Issue 하나를 처리한다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0009-observation.md` | MVP-0009 | MVP-Doc | MVP-0009 Observation: Project Intelligence를 Context Bundle로 발전시킨다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0010-observation.md` | MVP-0010 | MVP-Doc | MVP-0010 Observation: Planning Logic을 템플릿 채우기에서 Issue 분석 기반으로 발전시킨다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0011-observation.md` | MVP-0011 | MVP-Doc | MVP-0011 Observation: Design Capability를 Requirement 재서술에서 Architecture Draft 생성으로 발전시킨다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0012-observation.md` | MVP-0012 | MVP-Doc | MVP-0012 Observation: Validation Capability를 Stage-Aware Validation으로 개선한다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0013-observation.md` | MVP-0013 | MVP-Doc | MVP-0013 Observation: Implementation Capability를 Implementation Specification 생성 수준으로 구현한다 | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0014-observation.md` | MVP-0014 | MVP-Doc | MVP-0014 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0015-observation.md` | MVP-0015 | MVP-Doc | MVP-0015 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0016-observation.md` | MVP-0016 | MVP-Doc | MVP-0016 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0017-observation.md` | MVP-0017 | MVP-Doc | MVP-0017 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0018-observation.md` | MVP-0018 | MVP-Doc | MVP-0018 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0019-observation.md` | MVP-0019 | MVP-Doc | MVP-0019 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0020-observation.md` | MVP-0020 | MVP-Doc | MVP-0020 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0021-observation.md` | MVP-0021 | MVP-Doc | MVP-0021 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0022-observation.md` | MVP-0022 | MVP-Doc | MVP-0022 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0023-observation.md` | MVP-0023 | MVP-Doc | MVP-0023 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0024-observation.md` | MVP-0024 | MVP-Doc | MVP-0024 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0025-observation.md` | MVP-0025 | MVP-Doc | MVP-0025 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0026-observation.md` | MVP-0026 | MVP-Doc | MVP-0026 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0027-observation.md` | MVP-0027 | MVP-Doc | MVP-0027 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0028-observation.md` | MVP-0028 | MVP-Doc | MVP-0028 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0029-observation.md` | MVP-0029 | MVP-Doc | MVP-0029 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0030-observation.md` | MVP-0030 | MVP-Doc | MVP-0030 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0031-observation.md` | MVP-0031 | MVP-Doc | MVP-0031 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0032-observation.md` | MVP-0032 | MVP-Doc | MVP-0032 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0033-observation.md` | MVP-0033 | MVP-Doc | MVP-0033 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0034-observation.md` | MVP-0034 | MVP-Doc | MVP-0034 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0035-observation.md` | MVP-0035 | MVP-Doc | MVP-0035 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0036-observation.md` | MVP-0036 | MVP-Doc | MVP-0036 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0037-observation.md` | MVP-0037 | MVP-Doc | MVP-0037 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0038-observation.md` | MVP-0038 | MVP-Doc | MVP-0038 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0039-observation.md` | MVP-0039 | MVP-Doc | MVP-0039 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0040-observation.md` | MVP-0040 | MVP-Doc | MVP-0040 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0041-observation.md` | MVP-0041 | MVP-Doc | MVP-0041 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0042-observation.md` | MVP-0042 | MVP-Doc | MVP-0042 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0043-observation.md` | MVP-0043 | MVP-Doc | MVP-0043 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0044-observation.md` | MVP-0044 | MVP-Doc | MVP-0044 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0045-observation.md` | MVP-0045 | MVP-Doc | MVP-0045 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0046-observation.md` | MVP-0046 | MVP-Doc | MVP-0046 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0047-observation.md` | MVP-0047 | MVP-Doc | MVP-0047 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0048-observation.md` | MVP-0048 | MVP-Doc | MVP-0048 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0049-observation.md` | MVP-0049 | MVP-Doc | MVP-0049 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0050-observation.md` | MVP-0050 | MVP-Doc | MVP-0050 Observation | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0051-observation.md` | MVP-0051 | MVP-Doc | MVP-0051 Observation (Phase 10 Prototype #2) | Development HQ | Uncertain | Uncertain |
| `docs/01_mvp/MVP-0052-observation.md` | MVP-0052 | MVP-Doc | MVP-0052 Observation (Phase 10 Boundary Validation) | Development HQ | Uncertain | Uncertain |

### 3.3 `docs/architecture/` (155개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/architecture/baseline/BASELINE.md` | BASELINE | Architecture-Baseline | Jarvis OS Architecture Baseline v1.8 | Kernel | Uncertain | Certain |
| `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md` | STRUCTURE-V1.0-FROZEN | Architecture-Baseline | Jarvis OS Structure v1.0 — Frozen | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0001-core-baseline.md` | ADC-0001 | ADC | ADC-0001: Kernel Baseline Module 채택 판단 (RFC-0001 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0002-kernel-definition.md` | ADC-0002 | ADC | ADC-0002: Kernel Definition 채택 판단 (RFC-0002 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0003-kernel-context-model.md` | ADC-0003 | ADC | ADC-0003: Kernel Context Model 채택 판단 (RFC-0003 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0004-kernel-public-contract.md` | ADC-0004 | ADC | ADC-0004: Kernel Public Contract 채택 판단 (RFC-0004 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md` | ADC-0005 | ADC | ADC-0005: Kernel Logical Reference Architecture 채택 판단 (RFC-0005 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0006-kernel-context-ownership.md` | ADC-0006 | ADC | ADC-0006: Kernel Context Ownership 채택 판단 (RFC-0006 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0007-kernel-context-identity.md` | ADC-0007 | ADC | ADC-0007: Kernel Context Identity 검토 (RFC-0007 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0008-runtime-existence-boundary.md` | ADC-0008 | ADC | ADC-0008: Runtime 개념의 존폐 판단 (RFC-0008 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0009-model-component-correspondence-boundary.md` | ADC-0009 | ADC | ADC-0009: Model 축과 Component 축의 대응 관계 — Not Accepted (RFC-0009 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md` | ADC-0010 | ADC | ADC-0010: Engine Caller의 위치와 책임 — Not Accepted (RFC-0010 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0011-standalone-execution-location-boundary.md` | ADC-0011 | ADC | ADC-0011: Kernel/HQ에 속하지 않는 별도 실행 위치 — 허용 여부 판단 (RFC-0011 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0012-dispatch-component-boundary.md` | ADC-0012 | ADC | ADC-0012: RFC-0012(Dispatch Component)의 Governance 진행 가능 여부 — DEFER | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md` | ADC-0013 | ADC | ADC-0013: 단일 실행 단위 dispatch·격리 책임 존재 여부 — Scoped Reconsideration (RFC-0013 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0014-execution-responsibility-naming.md` | ADC-0014 | ADC | ADC-0014: 단일 실행 단위 dispatch·격리 책임의 명칭 판단 (RFC-0014 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md` | ADC-0015 | ADC | ADC-0015: Execution Host 구현 전략(Process/Thread/Subprocess) 판단 (RFC-0015 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md` | ADC-0016 | ADC | ADC-0016: Multi-Task 최소 책임(독립 Task 동시 실행·결과 수집) 존재 여부 판단 (RFC-0016 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md` | ADC-0017 | ADC | ADC-0017: Multi-Task Result Store/Checkpointer Integrity Boundary 존재 여부 판단 (RFC-0017 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0018-natural-language-request-multi-hq-task-decomposition.md` | ADC-0018 | ADC | ADC-0018: 자연어 요청 → Multi-HQ Task 분해 공통 책임 존재 여부 판단 (RFC-0018 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md` | ADC-0019 | ADC | ADC-0019: §16.3~16.5 너머 Scoped Workflow Graph Execution Boundary — 존재 판단 (RFC-0019 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0020-workflow-adapter-naming-and-contract-boundary.md` | ADC-0020 | ADC | ADC-0020: Workflow Adapter 명명 + Adapter Contract 부속 명세 정식화 (RFC-0020 후속) | Kernel | Decided — ADR Required | Uncertain |
| `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md` | ADC-0021 | ADC | ADC-0021: Workflow Adapter Implementation Strategy — Sequential Reference와 LangGraph 구현체의… | Kernel | Decided — Strategy Framing Accepted. Architecture/Governance Review PASS (§9). Commit/PR/M | Uncertain |
| `docs/architecture/core/ADC-0022-workflow-adapter-execution-unit-lifecycle-state-model-resolution.md` | ADC-0022 | ADC | ADC-0022: Workflow Adapter가 소비하는 실행 단위·Lifecycle·Workflow Execution State — Team/Division… | Kernel | Decided — ADR Required. Architecture/Governance Review PASS(§9). BASELINE/ADR 미착수, Commit/ | Uncertain |
| `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` | ADC-0023 | ADC | ADC-0023: v1 `ADR-0007` 결정 9의 잔여 계약 표면 — Workflow Adapter 호출 seam·입력 시그니처·결과 반환 타입의 v2 Re… | Kernel | Decided — ADR Required (예상 `ADR-0012`). Architecture/Governance Review PASS(§9, 최종 정합성 재점검 | Certain |
| `docs/architecture/core/ADC-0024-gate-b-independent-observation-threshold-judgment.md` | ADC-0024 | ADC | ADC-0024: Gate (B) — `ADC-0019` 재검토 조건 (c) "독립 관찰 3건" 충족 여부 판정 (E1·E2·E5/L-A) | Kernel | Decided — ADR Required (예상 `ADR-0013`). Architecture/Governance Review PASS(§9, 최종 재검토 포함 | Uncertain |
| `docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md` | ADC-0025 | ADC | ADC-0025: Gate (B) — E6(L-B 재귀 조합자)의 `ADC-0024` §D-B4(i) "2번째 비-LangGraph 독립 계보" 기여도 판정 | Kernel | Decided — ADR Required (예상 `ADR-0014`). Architecture/Governance Review PASS(§9). `BASELINE | Uncertain |
| `docs/architecture/core/ADC-0026-gate-c-real-engine-partial-discharge.md` | ADC-0026 | ADC | ADC-0026: Gate (C) — E7(실제 Engine 호출) 기반 잔여 한계 (i) 판정 | Kernel | Decided — **Partial**. Architecture/Governance Review PASS(§9). `BASELINE.md`·`GLOSSARY.md | Uncertain |
| `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md` | ADC-0027 | ADC | ADC-0027: Model Routing / Engine Adapter — OmniRoute Conditional Adoption Direction (RFC-… | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0028-domain-fallback-chains-precondition-responsibility-redesign.md` | ADC-0028 | ADC | ADC-0028: `domain_fallback_chains` 구현 착수 선행조건 — Responsibility 재설계 채택 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0029-routing-decisions-precondition-responsibility-redesign.md` | ADC-0029 | ADC | ADC-0029: `routing_decisions` 구현 착수 선행조건 — Audit Policy Requirement 재설계 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0030-priority-precondition-responsibility-redesign.md` | ADC-0030 | ADC | ADC-0030: `provider_connections.priority` 구현 착수 선행조건 — Responsibility 재설계 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md` | ADC-0031 | ADC | ADC-0031: OmniRoute Thin Engine Caller Boundary 확정 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0032-agent-domain-and-lifecycle-contract-resolution.md` | ADC-0032 | ADC | ADC-0032: Agent Domain & Lifecycle Contract — Governance Review (RFC-0024 후속) | Kernel | Uncertain | Certain |
| `docs/architecture/core/ADC-0033-agent-state-message-event-contract-resolution.md` | ADC-0033 | ADC | ADC-0033: Agent State / Message / Event Contract — Governance Review (RFC-0025 후속, Phase … | Kernel | Uncertain | Certain |
| `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md` | ADC-0034 | ADC | ADC-0034: LangGraph 승인된 비강제 Implementation Technology 확정 판단 (RFC-0031 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md` | ADC-0035 | ADC | ADC-0035: Graphify 승인된 비강제 Implementation Technology 확정 판단 (RFC-0032 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0036-stage01-multi-agent-reasoning-resolution.md` | ADC-0036 | ADC | ADC-0036: Stage 01 Multi-Agent Reasoning — Decision | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0037-stage01-prd-specification-synthesis-resolution.md` | ADC-0037 | ADC | ADC-0037: Stage 01 PRD/Specification Synthesis — Decision | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0038-stage02-planning-responsibility-and-execution-model-resolution.md` | ADC-0038 | ADC | ADC-0038: Stage 02 Planning Responsibility & Execution Model — Decision | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0039-multi-engine-re-evaluation.md` | ADC-0039 | ADC | ADC-0039: Multi-Engine Architecture 전환 재평가 (RFC-0036 후속, RT-0001 Candidate 2) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md` | ADC-0040 | ADC | ADC-0040: Stage 04 Multi-Agent(Case A/B/C) + Ponytail Supervisor Decision (RFC-0037 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md` | ADC-0041 | ADC | ADC-0041: Stage 05 QA Multi-Agent/Parallel Decision (RFC-0038 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md` | ADC-0042 | ADC | ADC-0042: Stage 05 Parallel Validation DAG — Decision (RFC-0039 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md` | ADC-0043 | ADC | ADC-0043: OpenRouter Free Model Selection — Decision (RFC-0040 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md` | ADC-0044 | ADC | ADC-0044: OpenRouter Production Engine Migration — Decision (RFC-0041 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md` | ADC-0045 | ADC | ADC-0045: Repository-wide Python Audit & Refactoring Governance Decision (RFC-0042 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADC-0046-workflow-execution-history-verification-persistence-ownership-boundary.md` | ADC-0046 | ADC | ADC-0046: Workflow Execution History / Verification Persistence Ownership Boundary 판단 (RF… | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/ADR-0001-governance-module-baseline.md` | ADR-0001 | ADR | ADR-0001: Governance Kernel Module의 Baseline 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | ADR-0002 | ADR | ADR-0002: Execution Layer Kernel Module의 Baseline 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md` | ADR-0003 | ADR | ADR-0003: 단일 실행 단위 Dispatch·격리 책임(Scoped)의 Baseline 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md` | ADR-0004 | ADR | ADR-0004: Execution Host 명칭(ADC-0014)의 Baseline 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md` | ADR-0005 | ADR | ADR-0005: Execution Host 구현 전략(ADC-0015)의 Baseline·Rules 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md` | ADR-0006 | ADR | ADR-0006: Multi-Task 최소 책임(ADC-0016)의 Baseline·Rules 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0007-multi-task-result-store-integrity-baseline.md` | ADR-0007 | ADR | ADR-0007: Multi-Task Result Store 저장 전 검증 게이트(ADC-0017)의 Baseline 반영 | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0008-scoped-workflow-graph-execution-baseline.md` | ADR-0008 | ADR | ADR-0008: Scoped Workflow Graph Execution Boundary(ADC-0019)의 Baseline 반영 | Kernel | Accepted** (2026-09-02) — 이 ADR의 §Decision·§Migration Strategy에 정의된 `BASELINE.md` 변경(§16.6 | Uncertain |
| `docs/architecture/core/ADR-0009-workflow-adapter-naming-and-contract-baseline.md` | ADR-0009 | ADR | ADR-0009: Workflow Adapter 명명 + Adapter Contract 부속 명세((a)(b)(d))의 Baseline 반영 | Kernel | Accepted** — Architecture/Governance Review PASS 이후, §Decision·§Migration Strategy가 정의하는 ` | Uncertain |
| `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md` | ADR-0010 | ADR | ADR-0010: Gate (C) E4 Evidence 반영 — §16.6 Reversibility 통합 테스트 재현 상태를 "부분 충족"으로 Baseline … | Kernel | Accepted** — Architecture/Governance Review PASS(§Review) 이후, §Decision·§Migration Strateg | Uncertain |
| `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md` | ADR-0011 | ADR | ADR-0011: Gate (A) v1 `ADR-0007` 결정 2·5·11 Resolution의 Baseline 반영 (ADC-0022 후속) | Kernel | Accepted** — Architecture/Governance Review PASS 이후, 사용자 승인(2026-09-04)으로 §Migration Strat | Uncertain |
| `docs/architecture/core/ADR-0012-gate-a-decision-9-contract-surface-resolution-baseline.md` | ADR-0012 | ADR | ADR-0012: Gate (A) v1 `ADR-0007` 결정 9 잔여 계약 표면 Resolution의 Baseline 반영 (ADC-0023 후속) | Kernel | Accepted** — Architecture/Governance Review PASS(아래 §Governance Chain 검증·§Self Review) 이후, | Uncertain |
| `docs/architecture/core/ADR-0013-gate-b-partial-relaxation-baseline.md` | ADR-0013 | ADR | ADR-0013: Gate (B) 형식 요건 충족 / 부분 완화의 Baseline 반영 (ADC-0024 후속) | Kernel | Accepted** — Architecture/Governance Review PASS(아래 §Governance Chain 검증·§Self Review). §M | Uncertain |
| `docs/architecture/core/ADR-0014-gate-b-second-lineage-partial-relaxation-baseline.md` | ADR-0014 | ADR | ADR-0014: Gate (B) 2차 부분 완화(E6/L-B)의 Baseline 반영 (ADC-0025 후속) | Kernel | Accepted** — Architecture/Governance Review PASS(아래 §Governance Chain 검증·§Self Review) 이후, | Uncertain |
| `docs/architecture/core/ADR-0015-omniroute-thin-engine-caller-adoption-policy.md` | ADR-0015 | ADR | ADR-0015: OmniRoute Model Routing / Engine Adapter Adoption — Thin Engine Caller 통합 Archi… | Kernel | Accepted (Consolidation Only — Baseline/Rules 문구 미반영)** — 이 ADR은 기존 5개 ADC의 Decision을 재론·확 | Uncertain |
| `docs/architecture/core/ADR-0016-omniroute-thin-caller-freeze-scoped-relaxation.md` | ADR-0016 | ADR | ADR-0016: OmniRoute Thin Engine Caller — Architecture Freeze Scoped 완화 (ADC-0027 §Decisio… | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0017-omniroute-production-adoption-final-review.md` | ADR-0017 | ADR | ADR-0017: OmniRoute Production Adoption — Final Adoption Review, Responsibility Boundary … | Kernel | Accepted — Production Adoption 선언(Scoped: OmniRoute Thin Engine Caller 형태에 한정)** — 판정 근거는 | Uncertain |
| `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md` | ADR-0018 | ADR | ADR-0018: LangGraph Adoption Final Review — Deferred / Not Adopted, Re-evaluation Trigger… | Kernel | Accepted — LangGraph는 Deferred / Not Adopted로 종결한다(§16.6 기존 지위 무변경, 새 Accept 없음)** — 판정 근거 | Certain |
| `docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md` | ADR-0019 | ADR | ADR-0019: LangGraph — 승인된 비강제 Implementation Technology 확정 (Workflow Adapter 구현 전략, `ADR-… | Kernel | Accepted. | Uncertain |
| `docs/architecture/core/ADR-0020-graphify-implementation-technology-adoption.md` | ADR-0020 | ADR | ADR-0020: Graphify — 승인된 비강제 Implementation Technology 확정 (향후 Graph 기반 Memory/Knowledge/R… | Kernel | Accepted. | Uncertain |
| `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md` | ADR-0021 | ADR | ADR-0021: Stage 01 Multi-Agent Reasoning Adoption — Baseline Reflection | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0022-stage01-prd-specification-synthesis-baseline.md` | ADR-0022 | ADR | ADR-0022: Stage 01 PRD/Specification Synthesis — Baseline Reflection | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0023-stage02-planning-responsibility-and-execution-model-baseline.md` | ADR-0023 | ADR | ADR-0023: Stage 02 Planning Responsibility & Execution Model — Baseline Reflection | Kernel | Accepted | Uncertain |
| `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md` | ADR-0024 | ADR | ADR-0024: Multi-Engine Architecture Adoption — ChatGPT/Claude Code 2-Engine 전환 | Kernel | Accepted — Multi-Engine Architecture(2-Engine: ChatGPT/Claude Code) Production Adoption | Uncertain |
| `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md` | ADR-0025 | ADR | ADR-0025: Stage 05 Parallel Validation Architecture — Boundary | Kernel | Accepted — Architecture Independence/Isolation/Aggregation Boundary 확정(Scoped). Parallel P | Uncertain |
| `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md` | ADR-0026 | ADR | ADR-0026: OpenRouter Free Model Selection — Architecture Boundary | Kernel | Accepted (Scoped) — Architecture Independence/Boundary 확정. Concrete API 구현(`openrouter/fre | Uncertain |
| `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md` | ADR-0027 | ADR | ADR-0027: OpenRouter Production Engine Migration — Adoption | Kernel | Accepted (Scoped) — Production Routing Integration(Architecture Adoption) 확정: OpenRouter를 | Uncertain |
| `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md` | ADR-0028 | ADR | ADR-0028: Repository-wide Python Audit & Refactoring — Governance Lifecycle Adoption | Kernel | Accepted (Scoped) — Governance Lifecycle 자체만 확정한다: Inventory → Deterministic Audit → Seman | Uncertain |
| `docs/architecture/core/CLOSURE-0001-architecture-research.md` | CLOSURE-0001 | Closure | CLOSURE-0001: Architecture Research 종료 가능 여부 검토 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/COMPONENT-CANDIDATE-0001-kernel-component-architecture-review.md` | COMPONENT-CANDIDATE-0001 | Component-Candidate | COMPONENT-CANDIDATE-0001: Kernel Component Architecture Candidate Review (Phase 7) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/DEVELOPMENT-HQ-V1.0-FREEZE-0001.md` | DEVELOPMENT-HQ-V1.0-FREEZE-0001 | Freeze | DEVELOPMENT-HQ-V1.0-FREEZE-0001: Development HQ Stable v1.0 Freeze | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` | DEVELOPMENT-HQ-V2.0-FREEZE-0001 | Freeze | DEVELOPMENT-HQ-V2.0-FREEZE-0001: Development HQ v2.0 Stable Freeze | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/DOC-TRIAGE-0001.md` | DOC-TRIAGE-0001 | Doc-Triage | DOC-TRIAGE-0001: Documentation Issue 9건 분류 | Kernel | Uncertain | Certain |
| `docs/architecture/core/EFFICIENCY-AUDIT-0001-token-text-efficiency.md` | EFFICIENCY-AUDIT-0001 | Efficiency-Audit | EFFICIENCY-AUDIT-0001: Token / Text Efficiency Audit (Phase 9) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0001-omniroute-precondition-verification.md` | EVIDENCE-0001 | Evidence | EVIDENCE-0001: OmniRoute 구현 착수 선행조건 검증 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0002-omniroute-domain-budgets-execution-verification.md` | EVIDENCE-0002 | Evidence | EVIDENCE-0002: `domain_budgets` 실제 Blocking Execution 검증 (ADC-0027 후속) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0003-omniroute-zero-config-egress-and-budget-block-static-analysis.md` | EVIDENCE-0003 | Evidence | EVIDENCE-0003: OmniRoute Zero-Config Egress 메커니즘 및 `domain_budgets` 재현 실패 정적 분석 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0004-omniroute-domain-budgets-root-cause-and-real-dispatch-lifecycle.md` | EVIDENCE-0004 | Evidence | EVIDENCE-0004: `domain_budgets` 차단 경로 근본 원인 확정과 실제 Engine Dispatch Lifecycle 검증 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0005-omniroute-open-issue-closure-and-production-adoption-gate-final-check.md` | EVIDENCE-0005 | Evidence | EVIDENCE-0005: OmniRoute Open Issue 전수 종결과 Production Adoption Gate 최종 점검 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0006-omniroute-production-engine-adapter-integration.md` | EVIDENCE-0006 | Evidence | EVIDENCE-0006: OmniRoute Production Engine Adapter Integration — 구현·검증 결과 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0007-omniroute-call-site-conversion-hold.md` | EVIDENCE-0007 | Evidence | EVIDENCE-0007: 기존 5개 `call_engine()` 호출부 OmniRoute 전환 검토 — 전환 보류(HOLD) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0008-test-mvp-0001-real-engine-gate.md` | EVIDENCE-0008 | Evidence | EVIDENCE-0008: `test_mvp_0001.py` 무게이트 실제 Engine 호출 — 재설계·검증·해결 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0009-omniroute-macos-iphone-operational-scope.md` | EVIDENCE-0009 | Evidence | EVIDENCE-0009: OmniRoute 운영 환경 가용성 — macOS + iPhone 범위 확정 검증 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0010-python310-isolated-environment-resolution.md` | EVIDENCE-0010 | Evidence | EVIDENCE-0010: Python 3.9 Collection 문제 해결 — Isolated Python 3.10+ 환경 확보 및 전체 Regression … | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-0011-omniroute-real-operator-instance-safety-check.md` | EVIDENCE-0011 | Evidence | EVIDENCE-0011: 실제 운영 OmniRoute 인스턴스 — 기동·안전조건 구성 상태 검증 | Kernel | 현재 시점 기준 **실행 중이 아니다.** 사용자 | Uncertain |
| `docs/architecture/core/EVIDENCE-0012-omniroute-real-instance-safety-configuration-applied.md` | EVIDENCE-0012 | Evidence | EVIDENCE-0012: 실제 운영 OmniRoute 인스턴스 — `blockedProviders`/`REQUIRE_API_KEY` 안전 설정 적용 | Kernel | `blockedProviders`, `REQUIRE_API_KEY` 둘 다 | Uncertain |
| `docs/architecture/core/EVIDENCE-0013-call-site-conversion-governance-final-review.md` | EVIDENCE-0013 | Evidence | EVIDENCE-0013: OmniRoute Call-Site Conversion — Governance 최종 재확인(READ-ONLY Review) 결과 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/EVIDENCE-INVENTORY-0001-validation-v1.md` | EVIDENCE-INVENTORY-0001 | Evidence-Inventory | EVIDENCE-INVENTORY-0001: V-1을 Observation만으로 재정의한다 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md` | GOVERNANCE-REVIEW-0001 | Governance-Review | Kernel Governance Review 0001 — ADC-0001(Artifact Drift Boundary) Merge 이후 상태 정리 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0002-impl-stop.md` | GOVERNANCE-REVIEW-0002 | Governance-Review | GOVERNANCE-REVIEW-0002: IMPL-STOP-0001 Governance 검토 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0003-adc-0010-reassessment.md` | GOVERNANCE-REVIEW-0003 | Governance-Review | GOVERNANCE-REVIEW-0003: ADC-0010 재평가 (ENGINE-CONNECT-0005 Evidence 반영) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0004-engine-mvp-closure-and-production-entry.md` | GOVERNANCE-REVIEW-0004 | Governance-Review | GOVERNANCE-REVIEW-0004: Engine MVP Validation 종료 판정 및 Production 단계 진입 가능 영역 전수 점검 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0005-c6-rfc-necessity-judgment.md` | GOVERNANCE-REVIEW-0005 | Governance-Review | GOVERNANCE-REVIEW-0005: C6("별도 스크립트/함수") 구체화 RFC의 필요성 판단 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0006-adc-02-09-10-dogfooding-evidence-check.md` | GOVERNANCE-REVIEW-0006 | Governance-Review | GOVERNANCE-REVIEW-0006: ADC-02 · ADC-09 · ADC-10 — Dogfooding/MVP 신규 Evidence 대조 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0007-development-hq-mvp-validation-closure.md` | GOVERNANCE-REVIEW-0007 | Governance-Review | GOVERNANCE-REVIEW-0007: Development HQ MVP Validation 종료 여부 검토 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/GOVERNANCE-REVIEW-0008-adc-0018-reassessment.md` | GOVERNANCE-REVIEW-0008 | Governance-Review | GOVERNANCE-REVIEW-0008: ADC-0018 재검토 — Investment HQ Wave1/2 Multi-Task Dogfooding·Failur… | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/IMPL-ENTRY-0001.md` | IMPL-ENTRY-0001 | Impl-Entry | IMPL-ENTRY-0001: Implementation 진입 가능성 검토 | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/IMPLEMENTATION-PRIORITY-0001-kernel-component-priority.md` | IMPLEMENTATION-PRIORITY-0001 | Implementation-Priority | IMPLEMENTATION-PRIORITY-0001: Kernel Component Implementation Priority (Phase 8) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/INVESTMENT-HQ-V1.0-FREEZE-0001.md` | INVESTMENT-HQ-V1.0-FREEZE-0001 | Freeze | INVESTMENT-HQ-V1.0-FREEZE-0001: Investment HQ Stable v1.0 Freeze | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/REFACTORING-TRACK-CLOSURE-0001.md` | REFACTORING-TRACK-CLOSURE-0001 | Closure | REFACTORING-TRACK-CLOSURE-0001: P2/P3 처리 결과 및 Refactoring Track 종료 판단 (Phase 10) | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` | RFC-0001 | RFC | RFC-0001: Jarvis OS Kernel Baseline | Kernel | Resolved — `ADC-0001-core-baseline.md`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨 | Uncertain |
| `docs/architecture/core/RFC-0002-kernel-definition.md` | RFC-0002 | RFC | RFC-0002: Kernel Definition — Responsibility, Not Component | Kernel | Resolved — `ADC-0002.md` → `ADR-0002`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 | Uncertain |
| `docs/architecture/core/RFC-0003-kernel-context-model.md` | RFC-0003 | RFC | RFC-0003: Kernel Context Model — Context, Builder, Assembly, Prompt Projection | Kernel | Resolved — `ADC-0003.md` → `ADR-0003`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 | Uncertain |
| `docs/architecture/core/RFC-0004-kernel-public-contract.md` | RFC-0004 | RFC | RFC-0004: Kernel Public Contract — 무엇을 보장하고, 무엇을 숨기고, 무엇을 하지 않는가 | Kernel | Resolved — `ADC-0004.md` → `ADR-0004`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 | Uncertain |
| `docs/architecture/core/RFC-0005-kernel-logical-reference-architecture.md` | RFC-0005 | RFC | RFC-0005: Kernel Logical Reference Architecture — 책임의 배선도 | Kernel | Resolved — `ADC-0005.md` → `ADR-0005`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 | Uncertain |
| `docs/architecture/core/RFC-0006-kernel-context-ownership.md` | RFC-0006 | RFC | RFC-0006: Kernel Context Ownership — Kernel은 Kernel Context를 어디까지 소유하는가 | Kernel | Resolved — `ADC-0006.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 | Uncertain |
| `docs/architecture/core/RFC-0007-kernel-context-identity.md` | RFC-0007 | RFC | RFC-0007: Kernel Context Identity — Identity는 Reference의 문제인가, Component의 문제인가 | Kernel | Resolved — `ADC-0007.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 | Uncertain |
| `docs/architecture/core/RFC-0008-runtime-existence-boundary.md` | RFC-0008 | RFC | RFC-0008: Runtime 개념의 존폐 — Boundary (ADC-02 후속) | Kernel | Resolved — `ADC-0008-runtime-existence-boundary.md`로 종결됨(Not Accepted, based on current ev | Uncertain |
| `docs/architecture/core/RFC-0009-model-component-correspondence-boundary.md` | RFC-0009 | RFC | RFC-0009: Model 축과 Component 축의 대응 관계 — Boundary (ADC-01 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0010-engine-caller-location-boundary.md` | RFC-0010 | RFC | RFC-0010: Engine Caller의 위치와 책임 — Boundary (ADC-0005 Q0 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0011-standalone-execution-location-boundary.md` | RFC-0011 | RFC | RFC-0011: Kernel/HQ에 속하지 않는 별도 실행 위치 — Architecture Concept으로서의 Boundary (ADC-0010 C6 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0012-dispatch-component-boundary.md` | RFC-0012 | RFC | RFC-0012: Dispatch Component의 Architecture Boundary (RFC-0010 C1 / RFC-0011 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0013-runtime-existence-scoped-reconsideration.md` | RFC-0013 | RFC | RFC-0013: Runtime Existence — Scoped Reconsideration (ADC-02 후속) | Kernel | Resolved — `ADC-0013-runtime-existence-scoped-reconsideration.md` | Uncertain |
| `docs/architecture/core/RFC-0014-execution-responsibility-naming.md` | RFC-0014 | RFC | RFC-0014: 단일 실행 단위 dispatch·격리 책임의 명칭 (ADR-0003 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0015-execution-host-implementation-strategy.md` | RFC-0015 | RFC | RFC-0015: Execution Host 구현 전략 — Process/Thread/Subprocess 비교 (ADC-0014/ADR-0004 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md` | RFC-0016 | RFC | RFC-0016: Multi-Task 최소 책임 — 독립 Task 동시 실행과 결과 수집 (ADC-02 후속, Execution Host와 분리) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md` | RFC-0017 | RFC | RFC-0017: Multi-Task Result Store/Checkpointer Integrity Boundary (ADC-0016/ADR-0006 후속, … | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0018-natural-language-request-multi-hq-task-decomposition.md` | RFC-0018 | RFC | RFC-0018: Natural-Language Request → Multi-HQ Task Decomposition | Kernel | Uncertain | Uncertain |
| `docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md` | RFC-0019 | RFC | RFC-0019: LangGraph as Scoped Workflow Adapter Candidate — Runtime Existence Boundary (AD… | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md` | RFC-0020 | RFC | RFC-0020: Workflow Adapter Contract와 구현체 경계 (§16.6 Scoped Workflow Graph Execution 후속) | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0021-workflow-adapter-execution-unit-lifecycle-state-model-boundary.md` | RFC-0021 | RFC | RFC-0021: Workflow Adapter가 소비하는 실행 단위·생명주기·State Model — Team/Division 부재 하의 v2 재설계 Boun… | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0022-workflow-engine-port-contract-surface-and-engine-seam-boundary.md` | RFC-0022 | RFC | RFC-0022: v1 `ADR-0007` 결정 9의 잔여 계약 표면 — Workflow Adapter 호출 seam·입력 시그니처·결과 반환 타입과 §14.1… | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0023-model-routing-engine-adapter-freeze-reconsideration-boundary.md` | RFC-0023 | RFC | RFC-0023: Model Routing / Engine Adapter Freeze — Reconsideration Boundary (OmniRoute 실측 … | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0024-agent-domain-and-lifecycle-contract.md` | RFC-0024 | RFC | RFC-0024: Agent Domain & Lifecycle Contract — 최소 범위 Boundary Question (Multi-Agent 운영 대비 … | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0025-agent-state-message-event-contract.md` | RFC-0025 | RFC | RFC-0025: Agent State / Message / Event Contract — 최소 범위 Boundary Question (Multi-Agent 운… | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0026-multi-agent-workflow-contract-candidate-boundary.md` | RFC-0026 | RFC | RFC-0026: Multi-Agent Workflow — Contract Candidate 조사 및 Boundary (Phase C) | Kernel | Proposed (조사·판단 결과 기록, Baseline 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0027-multi-agent-runtime-contract-candidate-boundary.md` | RFC-0027 | RFC | RFC-0027: Multi-Agent Runtime — Contract Candidate 조사 및 Boundary (Phase D) | Kernel | Proposed (조사·판단 결과 기록, Baseline 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0028-minimal-runtime-mvp-necessity-verification.md` | RFC-0028 | RFC | RFC-0028: Minimal Runtime MVP 필요성 검증 (Phase E) | Kernel | Proposed (조사·실험 결과 기록, Baseline 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0029-dev-hq-stage-agent-boundary-analysis.md` | RFC-0029 | RFC | RFC-0029: Dev HQ Stage → Agent Boundary Analysis (Phase F-1) | Kernel | Proposed (분석 결과 기록, Baseline 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md` | RFC-0030 | RFC | RFC-0030: Dev HQ Stage 01~05 Agent Team Boundary Analysis (Phase F-2) | Kernel | Proposed (분석 결과 기록, Baseline 결정 아님). **§3 Stage 01 | Uncertain |
| `docs/architecture/core/RFC-0031-langgraph-implementation-technology-adoption.md` | RFC-0031 | RFC | RFC-0031: Workflow Adapter(§16.6) 구현 전략 — LangGraph를 승인된 비강제 Implementation Technology로 확… | Kernel | Resolved — `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.m | Uncertain |
| `docs/architecture/core/RFC-0032-graphify-implementation-technology-adoption.md` | RFC-0032 | RFC | RFC-0032: Graphify를 승인된 비강제 Implementation Technology 후보로 확정할 것인가 (향후 Graph 기반 Memory/Kno… | Kernel | Resolved — `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md | Uncertain |
| `docs/architecture/core/RFC-0033-stage01-multi-agent-reasoning-adoption.md` | RFC-0033 | RFC | RFC-0033: Stage 01 Multi-Agent Reasoning Adoption | Kernel | Proposed → 이 세션에서 ADC-0036/ADR-0021로 이어 확정 대상 | Uncertain |
| `docs/architecture/core/RFC-0034-stage01-prd-specification-synthesis.md` | RFC-0034 | RFC | RFC-0034: Stage 01 PRD/Specification Synthesis — Stage 01/02 Responsibility Rebalancing | Kernel | Proposed → 이 세션에서 ADC-0037/ADR-0022로 이어 확정 대상 | Uncertain |
| `docs/architecture/core/RFC-0035-stage02-planning-responsibility-and-execution-model.md` | RFC-0035 | RFC | RFC-0035: Stage 02 Planning Responsibility & Execution Model | Kernel | Proposed → 이 세션에서 ADC-0038/ADR-0023으로 이어 확정 대상 | Uncertain |
| `docs/architecture/core/RFC-0036-chatgpt-claude-code-dual-engine-boundary.md` | RFC-0036 | RFC | RFC-0036: ChatGPT Engine / Claude Code Engine 분리 — Freeze 경계 확인 (구현 아님) | Kernel | ~~Proposed~~ → **Resolved** — 이 RFC가 조사한 내용을 근거로 | Uncertain |
| `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md` | RFC-0037 | RFC | RFC-0037: Stage 04 Multi-Agent(Case A/B/C) + Ponytail Supervisor — Freeze 경계 확인 (구현 아님) | Kernel | Proposed (검토 대상, 결정 아님 — §8이 이 RFC의 핵심 결론이다) | Uncertain |
| `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md` | RFC-0038 | RFC | RFC-0038: Stage 05 QA Multi-Agent/Parallel 경계 확인 (구현 아님) | Kernel | Proposed (검토 대상, 결정 아님 — §8이 이 RFC의 핵심 결론이다) | Uncertain |
| `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md` | RFC-0039 | RFC | RFC-0039: Stage 05 Parallel Validation DAG — Architecture Independence Validation | Kernel | Proposed (검토 대상, 결정 아님 — §9가 이 RFC의 핵심 결론이다) | Uncertain |
| `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md` | RFC-0040 | RFC | RFC-0040: OpenRouter Free Model Selection Architecture | Kernel | Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0043`/`ADR-0026`가 담당) | Uncertain |
| `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md` | RFC-0041 | RFC | RFC-0041: OpenRouter Production Engine Migration — Stage 01~05 Free Model Selection Archi… | Kernel | Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0044`/`ADR-0027`가 담당) | Uncertain |
| `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md` | RFC-0042 | RFC | RFC-0042: Repository-wide Python Audit & Refactoring — Governance Boundary (구현 아님) | Kernel | Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0045`/`ADR-0028`가 담당) | Uncertain |
| `docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md` | RFC-0043 | RFC | RFC-0043: Execution History & Evidence Persistence Architecture | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md` | RFC-0044 | RFC | RFC-0044: Narrow Execution History & Verification Persistence Boundary | Kernel | Proposed (검토 대상, 결정 아님) | Uncertain |
| `docs/architecture/core/STABILITY-0001-core-architecture.md` | STABILITY-0001 | Stability-Audit | STABILITY-0001: Core Architecture 안정성 검토 | Kernel | Proposed`를 달고 | Certain |
| `docs/architecture/core/VALIDATION-0001-kernel-reference-architecture.md` | VALIDATION-0001 | Validation | VALIDATION-0001: Kernel Reference Architecture 타당성 검증 | Kernel | Uncertain | Certain |
| `docs/architecture/core/VALIDATION-0002-kernel-component-boundary-evidence-check.md` | VALIDATION-0002 | Validation | VALIDATION-0002: Kernel Component Boundary — 실제 코드·테스트·Evidence 대조 검증 | Kernel | Uncertain | Uncertain |

### 3.4 `docs/core/` (27개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | ADC-0001 | ADC | ADC-0001: Spec-Repository Artifact Drift — Kernel 책임 여부 판단 (RFC-0001 후속) | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | ADC-0002 | ADC | ADC-0002: Execution Result Contract — 3개 후보 판단 (RFC-0002 후속) | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | ADC-0003 | ADC | ADC-0003: Execution Result Item Schema — 항목 타입 판단 (RFC-0003 후속) | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | ADC-0004 | ADC | ADC-0004: Execution Result Consumer — 결정 가능성 판단 (RFC-0004 후속) | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | ADC-0005 | ADC | ADC-0005: Engine 연결 Boundary — 허용 여부 판단 (RFC-0005 후속) | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | ADR-0001 | ADR | ADR-0001: Execution Result Contract의 Artifact Standard 반영 | Execution Layer | Accepted | Uncertain |
| `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | ADR-0002 | ADR | ADR-0002: Execution Result Item Schema의 Artifact Standard 반영 | Execution Layer | Accepted | Uncertain |
| `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` | ARTIFACT-STANDARD-v1 | Other | Execution Layer Artifact Standard v1 | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/IMPL-STOP-0001-execution-result.md` | IMPL-STOP-0001 | Impl-Stop | IMPL-STOP-0001: Execution Result 구현 중단 기록 | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/IMPL-STOP-0002-execution-result-builder.md` | IMPL-STOP-0002 | Impl-Stop | IMPL-STOP-0002: Execution Result Builder 구현 중단 기록 | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0001-artifact-mapping.md` | MVP-0001 | MVP-Doc | Execution Layer MVP-0001 Artifact Mapping | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0001-observation.md` | MVP-0001 | MVP-Doc | Execution Layer MVP-0001 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0001-plan.md` | MVP-0001 | MVP-Doc | Execution Layer MVP-0001 Plan: Implementation Specification → Execution Request | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0002-artifact-mapping.md` | MVP-0002 | MVP-Doc | Execution Layer MVP-0002 Artifact Mapping | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0002-observation.md` | MVP-0002 | MVP-Doc | Execution Layer MVP-0002 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0003-artifact-mapping.md` | MVP-0003 | MVP-Doc | Execution Layer MVP-0003 Artifact Mapping | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0003-observation.md` | MVP-0003 | MVP-Doc | Execution Layer MVP-0003 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0004-artifact-mapping.md` | MVP-0004 | MVP-Doc | Execution Layer MVP-0004 Artifact Mapping | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0004-observation.md` | MVP-0004 | MVP-Doc | Execution Layer MVP-0004 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0005-artifact-mapping.md` | MVP-0005 | MVP-Doc | Execution Layer MVP-0005 Artifact Mapping | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0005-observation.md` | MVP-0005 | MVP-Doc | Execution Layer MVP-0005 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/MVP-0006-observation.md` | MVP-0006 | MVP-Doc | Execution Layer MVP-0006 Observation | Execution Layer | Uncertain | Uncertain |
| `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | RFC-0001 | RFC | RFC-0001: Spec-Repository Artifact Drift — Boundary | Execution Layer | Resolved — `ADC-0001-artifact-drift-boundary.md`로 종결됨(Not Accepted, based on current evide | Uncertain |
| `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | RFC-0002 | RFC | RFC-0002: Execution Result Contract — 산출물을 묶는 방식 | Execution Layer | Resolved — `ADC-0002-execution-result-contract.md` → `ADR-0001-execution-result-contract.m | Uncertain |
| `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | RFC-0003 | RFC | RFC-0003: Execution Result Item Schema — 목록 항목의 형태 | Execution Layer | Resolved — `ADC-0003-execution-result-item-schema.md` → `ADR-0002-execution-result-item-sc | Uncertain |
| `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | RFC-0004 | RFC | RFC-0004: Execution Result Consumer — 소비 주체와 방식 | Execution Layer | Resolved — `ADC-0004-execution-result-consumer.md`로 종결됨(Not Accepted, based on current evi | Uncertain |
| `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | RFC-0005 | RFC | RFC-0005: Engine 연결 Boundary — Execution Result에 실제 산출물을 연결하는 경계 | Execution Layer | Proposed (검토 대상, 결정 아님) | Uncertain |

### 3.5 `docs/decisions/` (33개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/decisions/OPEN-DECISION-REGISTER-TEMPLATE.md` | OPEN-DECISION-REGISTER-TEMPLATE | Other | Open Decision Register | Development HQ | Uncertain | Uncertain |
| `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | ADC-0005 | ADC | ADC-0005: Structure v1.0 Migration — RFC-0006 후속 Decision 4건 | Development HQ/Kernel(Jarvis OS) | Uncertain | Certain |
| `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` | ADC-0006 | ADC | ADC-0006: `docs/01_architecture/BASELINE.md` 재배치 여부 | Development HQ/Kernel(Jarvis OS) | Uncertain | Certain |
| `docs/decisions/adc/ADC-TEMPLATE.md` | ADC-TEMPLATE | Template | ADC-XX — Title | Development HQ/Kernel(Jarvis OS) | Uncertain | Certain |
| `docs/decisions/adc/ADC.md` | ADC | Open-Decision-Index | Architecture Decision Candidate List | Development HQ/Kernel(Jarvis OS) | Open · **우선순위**: NEXT | Certain |
| `docs/decisions/adc/README.md` | README | Index | ADC (Architecture Decision Candidate) | Development HQ/Kernel(Jarvis OS) | Uncertain | Certain |
| `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md` | ADR-0001 | ADR | ADR-0001: Development HQ Baseline에 Stage 기반 구조 반영 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md` | ADR-0002 | ADR | ADR-0002: Core → Kernel 용어 통합 및 Kernel 정의의 Baseline 반영 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md` | ADR-0003 | ADR | ADR-0003: Kernel Context Model의 Architecture Baseline 반영 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md` | ADR-0004 | ADR | ADR-0004: Kernel Public Contract(Context 영역)의 Architecture Baseline 반영 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md` | ADR-0005 | ADR | ADR-0005: Kernel Logical Reference Architecture의 Baseline 반영과 §10 범위 한정 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | ADR-0006 | ADR | ADR-0006: Structure v1.0 Migration Decision 확정 | Development HQ(Kernel 일부 혼재) | Accepted** — Decision만 확정한다. Migration 실행은 이 ADR의 범위가 아니다. | Certain |
| `docs/decisions/adr/ADR-0007-baseline-relocation.md` | ADR-0007 | ADR | ADR-0007: `docs/01_architecture/BASELINE.md` → `docs/architecture/baseline/BASELINE.md` 확정 | Development HQ(Kernel 일부 혼재) | Accepted** — 위치·Reference 정합성만 확정한다. 이 ADR 자체는 이동을 실행하지 않는다. | Certain |
| `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md` | ADR-0008 | ADR | ADR-0008: Stage 폴더의 문서+실행 코드 공존 허용 (ADR-0001 §2/§6 Supersede) | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md` | ADR-0009 | ADR | ADR-0009: Development HQ Stage Data Contract — Public Scope Baseline 반영 | Development HQ(Kernel 일부 혼재) | Accepted | Certain |
| `docs/decisions/adr/ADR-0010-outcome-oriented-governance-model-baseline.md` | ADR-0010 | ADR | ADR-0010: Outcome-Oriented Governance Model — Baseline 반영 결정 | Development HQ(Kernel 일부 혼재) | Accepted.** 사용자 승인 후 §5의 신설 절 텍스트를 `docs/governance/README.md`에 그대로 등재했다(§4 실제 반영 범위 참고). | Certain |
| `docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md` | ADR-0011 | ADR | ADR-0011: "Implementation Freedom" 원칙 — Baseline 반영 결정 | Development HQ(Kernel 일부 혼재) | Accepted.** 사용자 승인 후 §1의 두 원칙을 `docs/governance/README.md`에 그대로 등재했다(§3 실제 반영 범위 참고). | Certain |
| `docs/decisions/adr/ADR-TEMPLATE.md` | ADR-TEMPLATE | Template | ADR-XX — Title | Development HQ(Kernel 일부 혼재) | Uncertain | Certain |
| `docs/decisions/adr/README.md` | README | Index | ADR (Architecture Decision Record) | Development HQ(Kernel 일부 혼재) | Proposed / Accepted / Superseded | Certain |
| `docs/decisions/rfc/README.md` | README | Index | RFC | Development HQ | 후속 ADC | Certain |
| `docs/decisions/rfc/RFC-0001-kernel-boundary.md` | RFC-0001 | RFC | RFC-0001: Kernel Boundary | Development HQ | Resolved — `docs/governance/adc/ADC-0001.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결 | Certain |
| `docs/decisions/rfc/RFC-0002-task-dispatcher-boundary.md` | RFC-0002 | RFC | RFC-0002: Task Dispatcher Boundary (재평가) | Development HQ | Resolved — `docs/governance/adc/ADC-0002.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결 | Certain |
| `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` | RFC-0003 | RFC | RFC-0003: Development HQ를 AI Native SDLC Platform으로 재정의 | Development HQ | Resolved — `docs/governance/adc/ADC-0003.md` → `ADR-0001`(판단 1에 한해)로 종결됨(STABILITY-0001 §1 | Certain |
| `docs/decisions/rfc/RFC-0004-task-dispatcher-runtime-boundary.md` | RFC-0004 | RFC | RFC-0004: Task Dispatcher → Runtime 승격 Boundary (Governance v2, Rule A) | Development HQ | Resolved — `docs/governance/adc/ADC-0004.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결 | Certain |
| `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md` | RFC-0005 | RFC | RFC-0005: Development HQ ↔ Execution Layer Boundary | Development HQ | Proposed (검토 대상, 결정 아님) — 저장소 내 13개 RFC 중 유일하게 후속 ADC가 아직 작성되지 않은 채 Open으로 남아 있다(STABILITY | Certain |
| `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | RFC-0006 | RFC | RFC-0006: Structure v1.0 — hqs/, core/execution/ 재배치 및 docs Taxonomy 정리 | Development HQ | Proposed (검토 대상, 결정 아님) | Certain |
| `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md` | RFC-0007 | RFC | RFC-0007: AST 기반 Context 자동 추출의 Production Build Capability 통합 | Development HQ | Proposed (검토 대상, 결정 아님) | Certain |
| `docs/decisions/rfc/RFC-0008-agents-module-physical-layout-boundary.md` | RFC-0008 | RFC | RFC-0008: AST Context Module Discovery — Dotted Package Path 지원 확장 여부 | Development HQ | Proposed (검토 대상, 결정 아님) | Certain |
| `docs/decisions/rfc/RFC-0009-stage-data-contract.md` | RFC-0009 | RFC | RFC-0009: Development HQ Stage Data Contract 공식화 | Development HQ | Resolved (Decision: 후보 C, Scoped Accept — 후속 `docs/governance/adc/ADC-0007.md` 참고) | Certain |
| `docs/decisions/rfc/RFC-0010-outcome-oriented-governance-model.md` | RFC-0010 | RFC | RFC-0010: Outcome-Oriented Governance Model 도입 여부 | Development HQ | Resolved — `docs/governance/adc/ADC-0008.md`로 종결됨(Scoped | Certain |
| `docs/decisions/rfc/RFC-0011-implementation-freedom-principle.md` | RFC-0011 | RFC | RFC-0011: "Implementation Freedom" 원칙 도입 여부 | Development HQ | Resolved — `docs/governance/adc/ADC-0009.md`로 종결됨(Scoped | Certain |
| `docs/decisions/rfc/RFC-TEMPLATE.md` | RFC-TEMPLATE | Template | RFC-XX — Title | Development HQ | Uncertain | Certain |
| `docs/decisions/rfc/RFC_CANDIDATES.md` | RFC_CANDIDATES | Pre-RFC-Candidate-List | RFC Candidates | Development HQ | Pending RFC · **Adoption Likelihood**: High (post-MVP) | Certain |

### 3.6 `docs/governance/` (21개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/governance/DECISION-GROUP-REGISTRY.md` | DECISION-GROUP-REGISTRY | Registry | Decision Group Registry | Cross-cutting Governance | RFC 수 | Certain |
| `docs/governance/README.md` | README | Index | Governance Charter | Cross-cutting Governance | Uncertain | Certain |
| `docs/governance/adc/ADC-0001.md` | ADC-0001 | ADC | ADC-0001: Kernel Extraction Candidate 승격 판단 (RFC-0001 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0002.md` | ADC-0002 | ADC | ADC-0002: Task Dispatcher 승격 재판단 (RFC-0002 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0003.md` | ADC-0003 | ADC | ADC-0003: Development HQ SDLC Stage 전환 판단 (RFC-0003 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0004.md` | ADC-0004 | ADC | ADC-0004: Task Dispatcher 승격 재판단 (RFC-0004 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0005.md` | ADC-0005 | ADC | ADC-0005: AST 기반 Context 자동 추출 Production 통합 판단 (RFC-0007 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0006.md` | ADC-0006 | ADC | ADC-0006: AST Context Module Discovery — Dotted Package Path 지원 확장 여부 (RFC-0008 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0007.md` | ADC-0007 | ADC | ADC-0007: Development HQ Stage Data Contract 공식화 판단 (RFC-0009 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0008.md` | ADC-0008 | ADC | ADC-0008: Outcome-Oriented Governance Model 도입 여부 판단 (RFC-0010 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0009.md` | ADC-0009 | ADC | ADC-0009: "Implementation Freedom" 원칙 도입 여부 판단 (RFC-0011 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | ADC-0010 | ADC | ADC-0010: RFC·ADC·ADR 통합 식별자 체계 도입 여부 판단 (Issue #206 후속) | Development HQ | Uncertain | Certain |
| `docs/governance/observations/OBS-0001.md` | OBS-0001 | Observation | OBS-0001 | Development HQ | Absorbed into RFC-0004 | Uncertain |
| `docs/governance/observations/OBS-0002.md` | OBS-0002 | Observation | OBS-0002 | Development HQ | Absorbed into RFC-0004 | Uncertain |
| `docs/governance/observations/OBS-0003.md` | OBS-0003 | Observation | OBS-0003 | Development HQ | Open | Uncertain |
| `docs/governance/observations/OBS-0004.md` | OBS-0004 | Observation | OBS-0004 | Development HQ | Open | Uncertain |
| `docs/governance/observations/OBS-0005.md` | OBS-0005 | Observation | OBS-0005 | Development HQ | Open | Uncertain |
| `docs/governance/observations/OBS-0006.md` | OBS-0006 | Observation | OBS-0006 | Development HQ | Open | Uncertain |
| `docs/governance/observations/OBS-TEMPLATE.md` | OBS-TEMPLATE | Template | OBS-XXXX | Development HQ | Open | Uncertain |
| `docs/governance/observations/README.md` | README | Index | Observations (Governance v2) | Development HQ | Baseline (공식 도입) | Uncertain |
| `docs/governance/rt/RT-0001.md` | RT-0001 | RT | RT-0001: Re-evaluation Trigger (ADC-0001 후속) | Development HQ | Uncertain | Uncertain |

### 3.7 `docs/research/` (158개)

| Path | Document ID | Type | Function | Target Domain | Lifecycle | Confidence |
|---|---|---|---|---|---|---|
| `docs/research/ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001.md` | ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001 | Research/Investigation | ADC-0010 후속 구현 순서 준수 여부 검토 (Issue #206 후속) | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/ADR-0027-VALIDATION-GATE-12-RESOLUTION-0001.md` | ADR-0027-VALIDATION-GATE-12-RESOLUTION-0001 | Research/Investigation | ADR-0027 §10 Validation Gate #12 최종 판정 — Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md` | ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001 | Research/Investigation | ADR-0027 §10 Gate #9(Retry) / #10(Failure Classification) 최종 판정 — Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ADR-0027-VALIDATION-GATE-EXECUTION-0001.md` | ADR-0027-VALIDATION-GATE-EXECUTION-0001 | Research/Investigation | ADR-0027 §10 Validation Gate 실측 검증 — Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md` | AGG-DATA-BOUNDARY-REPRODUCTION-0001 | Research/Investigation | AGG Data Boundary Reproduction 0001 — "Engine 데이터 범위 이탈" 재현 검토 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/AI-TOOL-WORKFLOW-AUDIT-0001.md` | AI-TOOL-WORKFLOW-AUDIT-0001 | Research/Investigation | AI Tool & Workflow Audit 0001 — Development HQ Workflow 확장 도구 평가 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ARTIFACT-DASHBOARD-SOURCE-OF-TRUTH-0001.md` | ARTIFACT-DASHBOARD-SOURCE-OF-TRUTH-0001 | Research/Investigation | Artifact Dashboard Source of Truth 0001 — Repository State Audit | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ARTIFACT-DASHBOARD-TRIAL-0001.md` | ARTIFACT-DASHBOARD-TRIAL-0001 | Research/Investigation | Artifact Dashboard Trial 0001 — 현재 사용 방식 기록 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/BASELINE-V1.6-DEV-HQ-V2.0-ALIGNMENT-0001.md` | BASELINE-V1.6-DEV-HQ-V2.0-ALIGNMENT-0001 | Research/Investigation | BASELINE-V1.6-DEV-HQ-V2.0-ALIGNMENT-0001: BASELINE v1.6 ↔ Development HQ v2.0 Architectur… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/BRANCH-AUTO-DELETE-VERIFICATION-0001.md` | BRANCH-AUTO-DELETE-VERIFICATION-0001 | Research/Investigation | BRANCH-AUTO-DELETE-VERIFICATION-0001: GitHub Head Branch Auto-Delete 실측 확인 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DASHBOARD-BACKEND-DATA-INVENTORY-0001.md` | DASHBOARD-BACKEND-DATA-INVENTORY-0001 | Research/Investigation | Dashboard Backend Data Inventory 0001 — Read-Only 조사 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md` | DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001 | Research/Investigation | Decision Group Registry — `docs/decisions/` 전체 커버리지 검증 | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0001.md` | DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0001 | Research/Investigation | Development HQ v2.0 — 01→05 Full Workflow Dogfooding | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0002.md` | DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0002 | Research/Investigation | Development HQ v2.0 — 01→05 Full Workflow Dogfooding (2회차) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-E2E-0001.md` | DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — ADC-0005 Workflow Integration E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` | DEV-HQ-V2.0-AGENT-DEFINITION-0001 | Research/Investigation | DEV-HQ-V2.0 — Agent Definition | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md` | DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001 | Research/Investigation | DEV-HQ-V2.0 — Agent Layer Readiness & Refactoring Audit | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-AGENT-PACKAGE-REFACTORING-E2E-0001.md` | DEV-HQ-V2.0-AGENT-PACKAGE-REFACTORING-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — Agent Package Refactoring real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-AST-CANDIDATE-INDEX-REPRODUCTION-0001.md` | DEV-HQ-V2.0-AST-CANDIDATE-INDEX-REPRODUCTION-0001 | Research/Investigation | DEV-HQ-V2.0 — AST Function Candidate Index 재현성 Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-BUILD-SOURCE-CONTEXT-NEED-0001.md` | DEV-HQ-V2.0-BUILD-SOURCE-CONTEXT-NEED-0001 | Research/Investigation | Build Source Context Need Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CATEGORY-PATHS-BLIND-SPOT-REVIEW-0001.md` | DEV-HQ-V2.0-CATEGORY-PATHS-BLIND-SPOT-REVIEW-0001 | Research/Investigation | CATEGORY_PATHS Blind Spot Review | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CLAUDE-CHATGPT-PROVIDER-SEPARATION-AUDIT-0001.md` | DEV-HQ-V2.0-CLAUDE-CHATGPT-PROVIDER-SEPARATION-AUDIT-0001 | Research/Investigation | DEV-HQ-V2.0 — Claude/ChatGPT Provider 역할 분리 Architecture Audit | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001.md` | DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — CLI Integration real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CONTEXT-AUTO-EXTRACTION-BOUNDARY-0001.md` | DEV-HQ-V2.0-CONTEXT-AUTO-EXTRACTION-BOUNDARY-0001 | Research/Investigation | DEV-HQ-V2.0-T13 — Context 자동 추출 경계조건 Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CONTEXT-EXPOSURE-REPRODUCTION-0001.md` | DEV-HQ-V2.0-CONTEXT-EXPOSURE-REPRODUCTION-0001 | Research/Investigation | DEV-HQ-V2.0-T16 — Context Exposure Reproduction Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-CONTEXT-EXPOSURE-SOURCE-STRATEGY-2X2-0001.md` | DEV-HQ-V2.0-CONTEXT-EXPOSURE-SOURCE-STRATEGY-2X2-0001 | Research/Investigation | DEV-HQ-V2.0-T15 — Context Exposure × Source Strategy 2×2 Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-DESIGN-AST-STARTPOINT-IDENTIFICATION-0001.md` | DEV-HQ-V2.0-DESIGN-AST-STARTPOINT-IDENTIFICATION-0001 | Research/Investigation | DEV-HQ-V2.0 — Design → AST Context Start-Point Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md` | DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001 | Research/Investigation | Governance Tree Investigation — docs/ Governance 문서 트리 병존 조사 | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/DEV-HQ-V2.0-INTEGRATED-WORKFLOW-E2E-0001.md` | DEV-HQ-V2.0-INTEGRATED-WORKFLOW-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — 01→05 Integrated Workflow real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-LITERAL-CODE-EXCERPT-RESEARCH-0001.md` | DEV-HQ-V2.0-LITERAL-CODE-EXCERPT-RESEARCH-0001 | Research/Investigation | Literal Code Excerpt Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-LITERAL-EXCERPT-AUTO-DETECTION-0001.md` | DEV-HQ-V2.0-LITERAL-EXCERPT-AUTO-DETECTION-0001 | Research/Investigation | Literal Excerpt 자동 판별 Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-MULTI-MODULE-AST-DEPENDENCY-RESEARCH-0001.md` | DEV-HQ-V2.0-MULTI-MODULE-AST-DEPENDENCY-RESEARCH-0001 | Research/Investigation | Multi-Module AST Dependency Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001.md` | DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001 | Research/Investigation | Development HQ v2.0 Production Readiness Audit | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-RFC-0007-REVALIDATION-0001.md` | DEV-HQ-V2.0-RFC-0007-REVALIDATION-0001 | Research/Investigation | DEV-HQ-V2.0 — RFC-0007 Revalidation & Decision | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-SCOPE-POLLUTION-3RD-DATAPOINT-0001.md` | DEV-HQ-V2.0-SCOPE-POLLUTION-3RD-DATAPOINT-0001 | Research/Investigation | DEV-HQ-V2.0-T14 — Scope Pollution 3rd Data Point Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-02-E2E-0001.md` | DEV-HQ-V2.0-STAGE-02-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 02 Planning & Specification real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-03-E2E-0001.md` | DEV-HQ-V2.0-STAGE-03-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 03 Architecture / Design real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-04-ARCH-VALIDATION-0001.md` | DEV-HQ-V2.0-STAGE-04-ARCH-VALIDATION-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 04 Implementation Architecture Validation | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-04-E2E-0001.md` | DEV-HQ-V2.0-STAGE-04-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 04 Implementation real Engine E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-05-E2E-0001.md` | DEV-HQ-V2.0-STAGE-05-E2E-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 05 Validation real Engine / real pytest E2E | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0001.md` | DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 01~05 Data Contract 정리(중복 계산 제거 + required_checks 구조화) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0002.md` | DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0002 | Research/Investigation | DEV-HQ-V2.0 — Stage 05 required_checks 인과관계 연결(decorative mirror 해소) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE01-04-CHATGPT-CLAUDE-CODE-CONNECTION-0001.md` | DEV-HQ-V2.0-STAGE01-04-CHATGPT-CLAUDE-CODE-CONNECTION-0001 | Research/Investigation | DEV-HQ-V2.0 — Stage 01~04 실제 ChatGPT / Claude Code Engine 연결 조사 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-STAGE01-04-CHATGPT-CLAUDE-CODE-CONNECTION-0002-REPOSITORY-EXECUTION-PREP.md` | DEV-HQ-V2.0-STAGE01-04-CHATGPT-CLAUDE-CODE-CONNECTION-0002-REPOSITORY-EXECUTION-PREP | Research/Investigation | DEV-HQ-V2.0 — ChatGPT 실제 호출 환경 확보 + Claude Code Repository Execution 준비 조사 (Part 2) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DEV-HQ-V2.0-TARGET-FILE-EXPOSURE-MITIGATION-0001.md` | DEV-HQ-V2.0-TARGET-FILE-EXPOSURE-MITIGATION-0001 | Research/Investigation | DEV-HQ-V2.0 — Target File Exposure 완화 정책 Research | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` | DIVIDEND-STOCK-DOGFOODING-REVIEW-0001 | Research/Investigation | Dividend Stock Dogfooding Review 0001 — Stock 공통성 및 고유 역할 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md` | DIVIDEND-STOCK-DOGFOODING-REVIEW-0002 | Research/Investigation | Dividend Stock Dogfooding Review 0002 — JNJ/KO/PG 3/3 반복성 확정 및 Dividend Stock Team 승격 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md` | DIVIDEND-STOCK-TEAM-DEFINITION-0001 | Research/Investigation | Dividend Stock Team Definition 0001 — 최소 업무 범위 승격 확정 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md` | DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001 | Research/Investigation | Dividend Stock Team Structure Decision 0001 — Promotion 재확인 및 "확장 vs 독립" 구조 권고 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md` | ENGINE-CONNECT-0001-call-engine-real-wiring | Research/Investigation | ENGINE-CONNECT-0001: `call_engine()` 실제 Engine 배선 — Runtime Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0002-execution-layer-results-wiring.md` | ENGINE-CONNECT-0002-execution-layer-results-wiring | Research/Investigation | ENGINE-CONNECT-0002: 외부 caller → `call_engine()` → 실제 Engine → `results:list[str]` → Exec… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0003-production-promotion-blocked.md` | ENGINE-CONNECT-0003-production-promotion-blocked | Research/Investigation | ENGINE-CONNECT-0003: `ENGINE-CONNECT-0002` Production 승격 조사 — Blocked | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0004-adc-0010-c6-investigation.md` | ENGINE-CONNECT-0004-adc-0010-c6-investigation | Research/Investigation | ENGINE-CONNECT-0004: ADC-0010 C6("별도 스크립트/함수") 조사 — Production Caller 후보 승격 가능성 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0005-full-pipeline-real-engine-wiring.md` | ENGINE-CONNECT-0005-full-pipeline-real-engine-wiring | Research/Investigation | ENGINE-CONNECT-0005: Development HQ → Implementation Specification → Execution Layer Pipe… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-CONNECT-0006-multi-item-results.md` | ENGINE-CONNECT-0006-multi-item-results | Research/Investigation | ENGINE-CONNECT-0006: `results: list[str]` 2개 이상 항목 — Runtime Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0001-Claude-Code.md` | ENGINE-INTEGRATION-0001-Claude-Code | Research/Investigation | Engine Integration Research 0001: Claude Code — Execution Protocol Observation | Cross-cutting(Research) | 실험 시작 시점 기준 메인 저장소는 직전 커밋 | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0002-Claude-Code.md` | ENGINE-INTEGRATION-0002-Claude-Code | Research/Investigation | Engine Integration Research 0002: Claude Code — Execution Protocol Observation (기존 파일 수정) | Cross-cutting(Research) | ENGINE-INTEGRATION-0001과 마찬가지로 메인 | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0003-Claude-Code.md` | ENGINE-INTEGRATION-0003-Claude-Code | Research/Investigation | Engine Integration Research 0003: Claude Code — Execution Protocol Observation (다중 파일 수정) | Cross-cutting(Research) | 메인 저장소는 커밋 `77bef0c`(Execution Layer | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0004-Claude-Code.md` | ENGINE-INTEGRATION-0004-Claude-Code | Research/Investigation | Engine Integration Research 0004: Claude Code — Execution Protocol Observation (Model Req… | Cross-cutting(Research) | 메인 저장소는 커밋 `c263c1a` 위에서 변경 없이 | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0005-Claude-Code.md` | ENGINE-INTEGRATION-0005-Claude-Code | Research/Investigation | Engine Integration Research 0005: Claude Code — Execution Protocol Observation (결과 포맷 요구 … | Cross-cutting(Research) | clean, `generated/` 부재 | Uncertain |
| `docs/research/ENGINE-INTEGRATION-0006-Claude-Code.md` | ENGINE-INTEGRATION-0006-Claude-Code | Research/Investigation | Engine Integration Research 0006: Claude Code — Execution Protocol Observation (결합 명시 요구) | Cross-cutting(Research) | clean, `generated/` 부재 | Uncertain |
| `docs/research/ENGINE-USECASE-0001-parallel-independent-tasks.md` | ENGINE-USECASE-0001-parallel-independent-tasks | Research/Investigation | ENGINE-USECASE-0001: 독립적인 두 Task의 병렬 실행 — Runtime Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ENGINE-USECASE-0002-nway-parallel-validation.md` | ENGINE-USECASE-0002-nway-parallel-validation | Research/Investigation | ENGINE-USECASE-0002: N-way Engine 병렬 실행 검증 — Runtime Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ETF-DOGFOODING-REVIEW-0001.md` | ETF-DOGFOODING-REVIEW-0001 | Research/Investigation | ETF Dogfooding Review 0001 — Stock/ETF 공통 요구사항 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ETF-DOGFOODING-REVIEW-0002.md` | ETF-DOGFOODING-REVIEW-0002 | Research/Investigation | ETF Dogfooding Review 0002 — QQQ/SCHD 반복성 종합 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ETF-DOGFOODING-REVIEW-0003.md` | ETF-DOGFOODING-REVIEW-0003 | Research/Investigation | ETF Dogfooding Review 0003 — QQQ/SCHD/AGG 3/3 반복성 확정 및 ETF Team 승격 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/ETF-TEAM-DEFINITION-0001.md` | ETF-TEAM-DEFINITION-0001 | Research/Investigation | ETF Team Definition 0001 — 최소 업무 범위 승격 확정 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/EVIDENCE-REVIEW-0001.md` | EVIDENCE-REVIEW-0001 | Research/Investigation | Evidence Review 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/EVIDENCE-REVIEW-0002-r1-r2-observability.md` | EVIDENCE-REVIEW-0002-r1-r2-observability | Research/Investigation | EVIDENCE-REVIEW-0002: R-1 / R-2 관찰 가능성 검토 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/GOVERNANCE-REASSESSMENT-0001.md` | GOVERNANCE-REASSESSMENT-0001 | Research/Investigation | GOVERNANCE-REASSESSMENT-0001: Phase 7 HOLD / Phase 8 Entry Criteria Reassessment | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/GOVERNANCE-TRIGGER-OBSERVATION-0001.md` | GOVERNANCE-TRIGGER-OBSERVATION-0001 | Research/Investigation | GOVERNANCE-TRIGGER-OBSERVATION-0001: 기존 Governance Trigger Observation 가능성 조사 | Cross-cutting(Research) | 확인 방법 | Uncertain |
| `docs/research/INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001.md` | INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md` | INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001 | Research/Investigation | Investment HQ Minimal Structure Review 0001 — 최소 조직 구조 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-PORTFOLIO-NEED-DOGFOODING-0001.md` | INVESTMENT-HQ-PORTFOLIO-NEED-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-PORTFOLIO-NEED-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-REPOSITORY-POLICY-RISK-PORTFOLIO-REPRODUCTION-0001.md` | INVESTMENT-HQ-REPOSITORY-POLICY-RISK-PORTFOLIO-REPRODUCTION-0001 | Research/Investigation | INVESTMENT-HQ-REPOSITORY-POLICY-RISK-PORTFOLIO-REPRODUCTION-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-RESEARCH-MANAGER-TRADER-BOUNDARY-DOGFOODING-0001.md` | INVESTMENT-HQ-RESEARCH-MANAGER-TRADER-BOUNDARY-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-RESEARCH-MANAGER-TRADER-BOUNDARY-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-RISK-ARCHITECTURE-FREEZE-REVIEW-0001.md` | INVESTMENT-HQ-RISK-ARCHITECTURE-FREEZE-REVIEW-0001 | Research/Investigation | INVESTMENT-HQ-RISK-ARCHITECTURE-FREEZE-REVIEW-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-RISK-CHANGES-PORTFOLIO-REVALIDATION-0001.md` | INVESTMENT-HQ-RISK-CHANGES-PORTFOLIO-REVALIDATION-0001 | Research/Investigation | INVESTMENT-HQ-RISK-CHANGES-PORTFOLIO-REVALIDATION-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-RISK-PORTFOLIO-BOUNDARY-DOGFOODING-0001.md` | INVESTMENT-HQ-RISK-PORTFOLIO-BOUNDARY-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-RISK-PORTFOLIO-BOUNDARY-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-RISK-PORTFOLIO-CHANGE-REPRODUCTION-DOGFOODING-0001.md` | INVESTMENT-HQ-RISK-PORTFOLIO-CHANGE-REPRODUCTION-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-RISK-PORTFOLIO-CHANGE-REPRODUCTION-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-SYNTHESIS-TRADER-EXPANSION-PROTOTYPE-0001.md` | INVESTMENT-HQ-SYNTHESIS-TRADER-EXPANSION-PROTOTYPE-0001 | Research/Investigation | INVESTMENT-HQ-SYNTHESIS-TRADER-EXPANSION-PROTOTYPE-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md` | INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001 | Research/Investigation | Investment HQ Team Validation Closure 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TRADER-ARCHITECTURE-FREEZE-REVIEW-0001.md` | INVESTMENT-HQ-TRADER-ARCHITECTURE-FREEZE-REVIEW-0001 | Research/Investigation | INVESTMENT-HQ-TRADER-ARCHITECTURE-FREEZE-REVIEW-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001.md` | INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TRADER-NEED-DOGFOODING-0001.md` | INVESTMENT-HQ-TRADER-NEED-DOGFOODING-0001 | Research/Investigation | INVESTMENT-HQ-TRADER-NEED-DOGFOODING-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TRADER-NEED-REVALIDATION-0001.md` | INVESTMENT-HQ-TRADER-NEED-REVALIDATION-0001 | Research/Investigation | INVESTMENT-HQ-TRADER-NEED-REVALIDATION-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-TRADER-WORKFLOW-STABILIZATION-0001.md` | INVESTMENT-HQ-TRADER-WORKFLOW-STABILIZATION-0001 | Research/Investigation | INVESTMENT-HQ-TRADER-WORKFLOW-STABILIZATION-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-V2.0-ARCHITECTURE-FREEZE-REVIEW-0001.md` | INVESTMENT-HQ-V2.0-ARCHITECTURE-FREEZE-REVIEW-0001 | Research/Investigation | INVESTMENT-HQ-V2.0-ARCHITECTURE-FREEZE-REVIEW-0001 | Cross-cutting(Research) | `hqs/investment/`는 이미 `INVESTMENT-HQ-V1.0-FREEZE-0001.md`로 | Uncertain |
| `docs/research/INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001.md` | INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001 | Research/Investigation | INVESTMENT-HQ-V2.0-FINAL-FREEZE-REVIEW-0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/INVESTMENT-HQ-V2.0-READINESS-AUDIT-0001.md` | INVESTMENT-HQ-V2.0-READINESS-AUDIT-0001 | Research/Investigation | INVESTMENT-HQ-V2.0-READINESS-AUDIT-0001: Investment HQ v2.0 Current State Audit & Freeze … | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001.md` | JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001 | Research/Investigation | JARVIS-OS-V2.0-ADC-02-RUNTIME-EXISTENCE-RECONSIDERATION-0001: ADC-02 Runtime Existence Bo… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001: Async / Long-running Command Experimental Pr… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001: Command Contract Experimental Prototype —… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-DASHBOARD-OPENROUTER-LLM-PATH-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-DASHBOARD-OPENROUTER-LLM-PATH-PROTOTYPE-0001 | Research/Investigation | Dashboard Chat → OpenRouter LLM 경로 Prototype — 조사·구현·검증 Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001: Development HQ Vertical Slice — Evid… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-EXECUTION-HOST-PRODUCTION-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-EXECUTION-HOST-PRODUCTION-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-EXECUTION-HOST-PRODUCTION-PROTOTYPE-0001: Execution Host Production 최소 구현 … | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-FUTURE-ARCHITECTURE-PROMOTION-POLICY-0001.md` | JARVIS-OS-V2.0-FUTURE-ARCHITECTURE-PROMOTION-POLICY-0001 | Research/Investigation | JARVIS-OS-V2.0-FUTURE-ARCHITECTURE-PROMOTION-POLICY-0001: Future Architecture Promotion P… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001: In-Process Async Command Experimen… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001: Process Runtime Strategy Experime… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001: Runtime Boundary Experimental Prototype —… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001.md` | JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001 | Research/Investigation | JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001: Unified Dashboard / Multi-HQ Orchestr… | Cross-cutting(Research) | Design Notes — Not yet Architecture | Uncertain |
| `docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001.md` | JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001 | Research/Investigation | JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001: Unified Dashboard Experimental Prototype… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` | JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001 | Research/Investigation | JARVIS-OS-V2.0 — Workflow Adapter Reversibility v2 통합 테스트 설계 (0001) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001.md` | KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001 | Research/Investigation | KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001: Development HQ v2.0 이후 Kernel Responsibi… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/MAIN-BRANCH-FULL-VALIDATION-0002.md` | MAIN-BRANCH-FULL-VALIDATION-0002 | Research/Investigation | Main Branch Full Validation — 코드·문서·Governance 무결성 검증 (2차) | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/MAIN-POST-MERGE-REGRESSION-VALIDATION-0001.md` | MAIN-POST-MERGE-REGRESSION-VALIDATION-0001 | Research/Investigation | main 최신 상태 기준 최종 Regression Validation — Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/MD-WRITER-VALIDATION-SKILL-CHECK-0001.md` | MD-WRITER-VALIDATION-SKILL-CHECK-0001 | Research/Investigation | MD-WRITER-VALIDATION-SKILL-CHECK-0001: Evidence 문서 작성에 md-writer/validation Skill 실사용 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` | OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001 | Research/Investigation | OpenRouter Auto Selection v1 — Validation Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` | OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001 | Research/Investigation | OpenRouter Free Model Selection Architecture — Experiment (ADR-0026 후속) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md` | OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001 | Research/Investigation | `identify_target()` OpenRouter Migration 구현 + Gate #4/#11/#12 재검증 — Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md` | OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001 | Research/Investigation | `identify_target()` OpenRouter Migration Scope Gap — Architecture 분석 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` | OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001 | Research/Investigation | OpenRouter `models` 배열 상한(3개) 재검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md` | OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001 | Research/Investigation | OpenRouter Production Engine Migration — Implementation | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md` | OPENROUTER-STAGE-MODEL-SELECTION-0001 | Research/Investigation | OpenRouter Stage 01~04 무료 모델 적합성 선별 — Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` | OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001 | Research/Investigation | OpenRouter Free Model Selection Architecture — Production Migration Evidence | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/OPENROUTER-VALIDATION-0001.md` | OPENROUTER-VALIDATION-0001 | Research/Investigation | OpenRouter Validation 0001 — 현재 세션 실환경 검증 및 Stage 01~05 전환 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE10-CLOSURE-0001.md` | PHASE10-CLOSURE-0001 | Research/Investigation | PHASE10-CLOSURE-0001: Prompt Specification 필요성 검증 — 종료 판정 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md` | PHASE10-PROMPT-SPECIFICATION-AUDIT-0001 | Research/Investigation | PHASE10-PROMPT-SPECIFICATION-AUDIT-0001: Prompt Specification 필요성 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE11-PROMPT-CACHE-AUDIT-0001.md` | PHASE11-PROMPT-CACHE-AUDIT-0001 | Research/Investigation | PHASE11-PROMPT-CACHE-AUDIT-0001: Prompt Cache 필요성 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001.md` | PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001 | Research/Investigation | PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001: Automation Workflow 필요성 재검토 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE12-BRANCH-LIFECYCLE-SKILL-0001.md` | PHASE12-BRANCH-LIFECYCLE-SKILL-0001 | Research/Investigation | PHASE12-BRANCH-LIFECYCLE-SKILL-0001: branch-lifecycle Skill 구현 및 실제 검증 | Cross-cutting(Research) | 분류 | Uncertain |
| `docs/research/PHASE12-BRANCH-LIFECYCLE-SKILL-0002-delete-path.md` | PHASE12-BRANCH-LIFECYCLE-SKILL-0002-delete-path | Research/Investigation | PHASE12-BRANCH-LIFECYCLE-SKILL-0002: 삭제 경로(Step 5~8) 실제 검증 | Cross-cutting(Research) | `git log origin/main -1` | Uncertain |
| `docs/research/PHASE12-RUNTIME-AUTOMATION-AUDIT-0001.md` | PHASE12-RUNTIME-AUTOMATION-AUDIT-0001 | Research/Investigation | PHASE12-RUNTIME-AUTOMATION-AUDIT-0001: Runtime/Automation 필요성 검증 (READ-ONLY) | Cross-cutting(Research) | Open, 우선순위 NOW. | Uncertain |
| `docs/research/PHASE4-HQ-CROSS-VALIDATION-0001.md` | PHASE4-HQ-CROSS-VALIDATION-0001 | Research/Investigation | PHASE4-HQ-CROSS-VALIDATION-0001: Development HQ ↔ Investment HQ 실행 패턴 대조 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE5-KERNEL-CANDIDATE-0001.md` | PHASE5-KERNEL-CANDIDATE-0001 | Research/Investigation | PHASE5-KERNEL-CANDIDATE-0001: Kernel Candidate 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md` | PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001 | Research/Investigation | PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001 | Cross-cutting(Research) | 두 경우 모두 Python 프로세스가 예외로 명확히 종료(`Exception` catch 후 메시지 출력, 스크립트 자체는 `exit 0`로 방어적으로 짜서 확인 | Uncertain |
| `docs/research/PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` | PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001 | Research/Investigation | PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001: Parallel Execution의 Kernel Component 배치 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PHASE7-RESUME-REVIEW-0001.md` | PHASE7-RESUME-REVIEW-0001 | Research/Investigation | PHASE7-RESUME-REVIEW-0001: Development HQ v2.0 완료 이후 Phase 7 재개 가능성 검토 | Cross-cutting(Research) | 🟡 Architecture | Uncertain |
| `docs/research/PHASE9-CLOSURE-0001.md` | PHASE9-CLOSURE-0001 | Research/Investigation | PHASE9-CLOSURE-0001: Engine Adapter 필요성 검증 — 종료 판정 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-AUDIT-WAVE-0-INVENTORY-0001.md` | PYTHON-AUDIT-WAVE-0-INVENTORY-0001 | Research/Investigation | Python Audit Wave 0 — Repository-wide Inventory & Baseline | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001.md` | PYTHON-AUDIT-WAVE-1-COMMENT-DOCSTRING-REFACTOR-0001 | Research/Investigation | Python Audit Wave 1 — Comment/Docstring Refactor | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md` | PYTHON-REFACTOR-WAVE-2-AUDIT-0001 | Research/Investigation | Python Refactor Wave 2 — Repository-wide Audit | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-2-C1-0001.md` | PYTHON-REFACTOR-WAVE-2-C1-0001 | Research/Investigation | Python Refactor Wave 2 — C1 Implementation: `investment/teams/*.py` | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-2-C2-0001.md` | PYTHON-REFACTOR-WAVE-2-C2-0001 | Research/Investigation | Python Refactor Wave 2 — C2 Implementation: `auto_selection_client.py` | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-3-DOCSTRING-FINAL-0001.md` | PYTHON-REFACTOR-WAVE-3-DOCSTRING-FINAL-0001 | Research/Investigation | Python Refactor Wave 3 — Docstring 의미 기반 재분류 완료 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-4-C9-0001.md` | PYTHON-REFACTOR-WAVE-4-C9-0001 | Research/Investigation | Python Refactor Wave 4 — C9(테스트 fixture 공유화) 완료 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/PYTHON-REFACTOR-WAVE-5-DOCSTRING-SEMANTIC-AUDIT-0001.md` | PYTHON-REFACTOR-WAVE-5-DOCSTRING-SEMANTIC-AUDIT-0001 | Research/Investigation | Python Refactor Wave 5 — Docstring Semantic Audit(REMOVE/COMPRESS/KEEP/ADD/NONE) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001.md` | RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001 | Research/Investigation | RFC-0008 → ADC-0006 재검증 및 구현 준수 확인 | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001 | Research/Investigation | RFC/ADC/ADR 식별자 통일 가능성 조사 — Issue #206 | Cross-cutting(Research) | Uncertain | Certain |
| `docs/research/RFC-ROLE-BOUNDARY-REVIEW-0001.md` | RFC-ROLE-BOUNDARY-REVIEW-0001 | Research/Investigation | RFC Role 경계 검토 — `## Decision` 절 사용 실태 (Issue #206 후속) | Cross-cutting(Research) | Proposed (검토 대상, 결정 아님)`(원문 3행). | Certain |
| `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md` | STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001 | Research/Investigation | Stage → Team Migration — Archive/Obsolete File Cleanup Investigation | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md` | STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001 | Research/Investigation | Stage 01~05 → Team 01~05 + OpenRouter Migration — Comprehensive Review | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001.md` | STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001 | Research/Investigation | Stage → Team OpenRouter Real Call Validation | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0002.md` | STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0002 | Research/Investigation | Stage → Team OpenRouter Real Call Validation (2) — 축소형 E2E와 실패 전파 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0003.md` | STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0003 | Research/Investigation | Stage → Team OpenRouter Real Call Validation (3) — T5-A 성공 표본 확보 시도 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0004.md` | STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0004 | Research/Investigation | Stage → Team OpenRouter Real Call Validation (4) — T5-B-1 Contract 구조 검증(코드 근거) | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0005.md` | STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0005 | Research/Investigation | Stage → Team OpenRouter Real Call Validation (5) — Observability 적용 후 T5-C 재실행, 최초 HTTP S… | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` | STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001 | Research/Investigation | Stage 05 Actual Implementation Revalidation | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE05-LATENCY-OPTIMIZATION-EXPERIMENT-0001.md` | STAGE05-LATENCY-OPTIMIZATION-EXPERIMENT-0001 | Research/Investigation | Stage 05 End-to-End Latency Optimization — Experiment Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md` | STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001 | Research/Investigation | Stage 05 Parallel Validation Architecture — Experiment Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md` | STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001 | Research/Investigation | Stage 05 Review Validator LLM — 실제 3회 실행 Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STAGE05-TEST-ISOLATION-VALIDATION-0001.md` | STAGE05-TEST-ISOLATION-VALIDATION-0001 | Research/Investigation | Stage 05 Test Isolation — Existing Test Suite Validation — Evidence 0001 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md` | STOCK-AGENT-SEPARATION-REVIEW-0001 | Research/Investigation | Stock Agent Separation Review 0001 — 역할/Agent 분리 필요성 검증 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STOCK-DOGFOODING-REVIEW-0001.md` | STOCK-DOGFOODING-REVIEW-0001 | Research/Investigation | Stock Dogfooding Review 0001 — Stock Team 승격 판단 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/STOCK-TEAM-DEFINITION-0001.md` | STOCK-TEAM-DEFINITION-0001 | Research/Investigation | Stock Team Definition 0001 — 최소 업무 범위 승격 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/TEAM-ARCHITECTURE-DESIGN-VS-IMPLEMENTATION-GAP-ANALYSIS-0001.md` | TEAM-ARCHITECTURE-DESIGN-VS-IMPLEMENTATION-GAP-ANALYSIS-0001 | Research/Investigation | Team 01~05 — Architecture Design vs Actual Implementation Gap Analysis | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/agg-boundary-repro/agg_perf_risk_repro_1.md` | agg_perf_risk_repro_1 | Research/Investigation | agg_perf_risk_repro_1 | Cross-cutting(Research) | Uncertain | Uncertain |
| `docs/research/agg-boundary-repro/agg_perf_risk_repro_2.md` | agg_perf_risk_repro_2 | Research/Investigation | agg_perf_risk_repro_2 | Cross-cutting(Research) | Uncertain | Uncertain |

## 4. 검증 결과

### 4.1 실제 파일 존재 여부

449개 전부 `os.walk()`로 파일시스템에서 직접 수집했다 — 존재하지 않는 항목을 다룬 적이 없으므로 **누락 검증 대상 자체가 없다**(추정으로 추가한 행이 0건).

### 4.2 Document ID와 파일명 정합성

RFC/ADC/ADR/기타 ID 패턴 파일 270개 전부 파일명 접두사와 Document ID가 100% 일치(추출 규칙 자체가 파일명에서 ID를 뽑으므로 구조적으로 항상 일치 — 별도 불일치 검사가 필요한 것은 "파일명 vs 본문 최상위 제목의 ID" 쪽이며, 그 검사는 이전 세션(`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` §3)이 `docs/decisions/`+`docs/governance/adc/`+`docs/architecture/core/`+`docs/core/execution-layer/`의 141개 RFC/ADC/ADR에 대해 이미 전수 확인해 **불일치 0건**을 확인했다. 이번 Inventory는 그 141개를 포함하는 상위 집합이며 재확인하지 않고 그 결과를 인용한다.

**검증 과정 중 발견·수정한 자체 오류**: 최초 스크립트가 `docs/research/`의 파일명이 다른 문서의 ID로 시작하는 경우(`RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001.md`, `ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001.md`, `ADR-0027-VALIDATION-GATE-*-0001.md` 3건)를 실제 RFC-0008/ADC-0010/ADR-0027 본체로 잘못 집계해 허위 3-way 충돌을 만들었다 — §1.2의 규칙을 추가해 정정했다(§4.3 표는 정정 후 결과).

### 4.3 중복 ID 및 충돌 여부

`docs/` 전체에서 동일 Document ID를 가진 그룹 **39건**을 발견했다. 전수 분류 결과:

| 분류 | 건수 | 설명 |
|---|---:|---|
| RFC/ADC/ADR 트리 간 번호 재사용 | 33 | `docs/decisions/`·`docs/governance/adc/`·`docs/architecture/core/`·`docs/core/execution-layer/` 4개 독립 트리가 각자 RFC/ADC/ADR을 1번부터 채번 — 이미 `RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`가 근거와 함께 확인한 **알려진 현상**(내용 중복 아님) |
| MVP-#### 같은 번호, 다른 산출물 유형 | 6 | `docs/01_mvp/`(Observation/Plan)와 `docs/core/execution-layer/`(Observation/Plan/Artifact-Mapping)가 같은 MVP 번호를 각자 관례대로 재사용 — 같은 MVP 회차의 서로 다른 문서 유형이며 충돌 아님 |
| `README` | 1(5개 파일) | Index 문서 5개가 전부 파일명이 `README.md`라 문자열이 같을 뿐, 애초에 번호가 부여되는 Governance ID가 아니다 — 진짜 ID 충돌이 아니다 |

**신규로 발견된, 이전에 알려지지 않은 실제 충돌: 0건.** 39건 전부 이미 알려진 패턴에 해당하거나(RFC/ADC/ADR 트리 재사용, 이전 세션이 문서화함) 애초에 Governance 번호가 아닌 파일명 우연 일치(README, MVP 문서 유형)다.

### 4.4 기존 문서와 Registry의 참조 정합성

`docs/governance/DECISION-GROUP-REGISTRY.md`(DG-0001, DG-0002)가 인용하는 15개 경로 전부 이번 Inventory의 449개 목록 안에 존재를 재확인했다(DG-0001의 5개 경로: `docs/decisions/rfc/RFC-0006-*`, `docs/decisions/adc/ADC-0005-*`, `docs/decisions/adc/ADC-0006-*`, `docs/decisions/adr/ADR-0006-*`, `docs/decisions/adr/ADR-0007-*` — §3.5에 전부 존재. DG-0002의 10개 경로 중 `docs/architecture/core/` 소속 9개 — §3.3에 전부 존재). Registry 자체는 이번 세션에서 수정하지 않았다.

### 4.5 Markdown 문법 및 표 구조

이 문서 자체의 모든 표(§3의 7개 섹션 포함)를 `|`로 시작/종료하는지 스크립트로 전수 검증 — **오류 0건**. 표 셀 내 백틱·특수문자는 전부 `\|` 이스케이프 규칙을 적용했다.

## 5. 요약 통계

| Type | 건수 |
|---|---:|
| Research/Investigation | 158 |
| MVP-Doc | 65 |
| ADC | 63 |
| RFC | 60 |
| ADR | 41 |
| Evidence | 13 |
| Governance-Review | 8 |
| Observation | 6 |
| Index | 5 |
| Template | 4 |
| Freeze | 3 |
| Governance-Policy | 2 |
| Other | 2 |
| Architecture-Baseline | 2 |
| Closure | 2 |
| Validation | 2 |
| Impl-Stop | 2 |
| Registry | 1 |
| RT | 1 |
| Pre-RFC-Candidate-List | 1 |
| Open-Decision-Index | 1 |
| Component-Candidate | 1 |
| Doc-Triage | 1 |
| Efficiency-Audit | 1 |
| Evidence-Inventory | 1 |
| Impl-Entry | 1 |
| Implementation-Priority | 1 |
| Stability-Audit | 1 |

| Target Domain | 건수 |
|---|---:|
| Cross-cutting(Research) | 158 |
| Kernel | 155 |
| Development HQ | 87 |
| Execution Layer | 27 |
| Development HQ(Kernel 일부 혼재) | 13 |
| Development HQ/Kernel(Jarvis OS) | 5 |
| Cross-cutting Governance | 4 |

| Confidence | 건수 | 비율 |
|---|---:|---:|
| Uncertain | 390 | 86% |
| Certain | 59 | 13% |

Lifecycle(Status) 필드가 명시적으로 발견된 문서: **138/449**건(30%). 나머지는 §1.4가 설명한 의미로 `Uncertain`.

## 6. 이번 단계에서 하지 않은 것 (명시적 보류)

- **통합 원장(Consolidated Ledger) 4개 생성**: 보류. Issue #206이
  최종적으로 요구하는 RFC/ADC/ADR/Open Decision 통합 원장은 이
  Inventory가 만든 원재료(449개 문서의 ID·Type·Domain 분류)를
  입력으로 삼아 별도 후속 작업에서 생성한다.
- **각 문서에 Front Matter 삽입**: 보류. 449개 파일 중 어느 것도
  이번 세션에서 수정하지 않았다 — Front Matter 삽입은 "기존 문서
  내용 수정 금지" 원칙과 정면으로 충돌할 수 있는 작업이라 별도
  승인 후 범위·형식을 먼저 확정해야 한다.
- **`docs/research/` 158개 문서 각각의 개별 내용 검증**: 7개(이번
  세션 및 직전 세션이 작성한 investigation/review 문서)를 제외한
  151개는 제목만으로 분류했다(Confidence: Uncertain). 이 151개를
  깊이 읽고 재분류하는 것은 범위를 크게 넘어서므로 후속 작업으로
  분리한다.
- **`docs/00_governance/`·`docs/01_mvp/` 레거시 경로의 Canonical
  위치 재판단**: `DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md`
  가 이미 "Migration Residue, Architecture 영향 없음"으로 판정한
  사안이며 이번 Inventory는 그 판정을 재론하지 않는다.

## Architecture / Public Contract 영향

- Architecture 변경: **No**
- Public Contract 변경: **No**
- 이번 작업으로 수정된 기존 문서: **0건**(신규 Inventory 문서 1개만
  추가)

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | RFC/ADC/ADR ID 충돌 근거 인용(§4.2, §4.3) |
| Verification | `docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md` | Registry 커버리지 선행 검증 |
| Verification | `docs/research/MAIN-BRANCH-FULL-VALIDATION-0002.md` | 코드/문서 전체 검증 선행 작업 |
| Registry | `docs/governance/DECISION-GROUP-REGISTRY.md` | §4.4 참조 정합성 검증 대상 |
| Issue | #206 | 상위 요청 |

## 별도 상태 표시

- Architecture 변경 여부: No
- Public Contract 변경 여부: No
- 처리한 문서 수: 449(전수)
- 신규 발견 실제 ID 충돌: 0건
- Confidence 분포: Certain 59건(13%) / Uncertain 390건(87%)
- 다음 단계: 통합 원장 4개 생성, Front Matter 삽입 — 사용자 승인
  후 별도 작업으로 진행
