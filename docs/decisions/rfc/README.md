# RFC

## 목적

RFC(Request For Comments)는 Architecture에 대한 새로운 논의를 제기하는 문서다. RFC는 결정이 아니라 검토 대상이다.

## 절차 상 위치

```
RFC → ADC → ADR → Architecture Baseline Update
```

RFC에서 논의된 내용 중 결정이 필요한 항목은 `docs/decisions/adc/ADC.md`에 Decision Candidate로 등록된다. RFC 자체는 Baseline을 변경하지 않는다.

## 현재 상태

Jarvis OS Architecture Baseline v1.6과 Development HQ Baseline v1.0은 Frozen이다. 새로운 RFC는 Baseline 변경이 불가피하다고 판단될 때만 작성한다.

과거 RFC(Meta Architecture, Concept Model, Core Component 등 논의)의 결과는 `docs/01_architecture/BASELINE.md`와 `docs/decisions/adc/ADC.md`에 이미 반영되어 있다.

## RFC 승격 대기 항목

`RFC_CANDIDATES.md`에는 이미 논의가 이루어졌고 MVP 검증 이후 정식 RFC로 승격될 가능성이 높은 Architecture 후보가 기록되어 있다. 이는 막연한 아이디어 목록이 아니라, Baseline 반영 가능성이 높다고 판단된 항목이다. 단, 정식 RFC로 승격되기 전까지는 Baseline에도, 구현에도 반영되지 않는다.

## 등록된 RFC

저장소 전체의 RFC는 3개 트리(Location)에 독립적으로 채번되어 있다 —
`docs/decisions/rfc/`(Development HQ 수준), `docs/architecture/core/`
(Kernel 수준), `docs/core/execution-layer/`(Execution Layer 수준). 각
트리는 RFC-0001부터 별도로 시작하므로 번호만으로는 구분되지 않는다 —
`DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md`(§6)가 이미 확인한
대로 이는 **번호 재사용**일 뿐 **결정 내용의 중복은 아니다**.

실제 파일 수는 24건이다(과거 `STABILITY-0001` §1.2 집계 13건 이후
Kernel 트리에 RFC-0008~0012, Execution Layer 트리에 RFC-0002~0005,
Development HQ 트리에 RFC-0006이 추가됨 — 이번 확인으로 갱신. RFC-0007
(Development HQ 트리, AST Context Build Integration)은 DEV-HQ-V2.0
Context Research(T06~T16) 종료 후 추가됨).

각 RFC 파일 헤더의 `**Status**` 라벨은 실제 절차 진행과 무관하게 대부분
`Proposed`로 고정되어 있다(`DOC-TRIAGE-0001` D-9가 이미 지적한 색인
부채) — 아래 "상태" 열은 헤더 라벨이 아니라 **후속 ADC/ADR 문서의
실제 존재 여부로 확인한 상태**다. 개별 RFC 파일 헤더는 이 표 작성으로
수정하지 않는다.

| ID | Location | 제목 | 상태 | 후속 ADC | 후속 ADR |
|---|---|---|---|---|---|
| RFC-0001 | `docs/decisions/rfc/` | Kernel Boundary | Resolved | `docs/governance/adc/ADC-0001.md` | 없음(불필요) |
| RFC-0002 | `docs/decisions/rfc/` | Task Dispatcher Boundary (재평가) | Resolved | `docs/governance/adc/ADC-0002.md` | 없음(불필요) |
| RFC-0003 | `docs/decisions/rfc/` | Development HQ를 AI Native SDLC Platform으로 재정의 | Resolved | `docs/governance/adc/ADC-0003.md` | `ADR-0001`(판단 1에 한해) |
| RFC-0004 | `docs/decisions/rfc/` | Task Dispatcher → Runtime 승격 Boundary (Governance v2, Rule A) | Resolved | `docs/governance/adc/ADC-0004.md` | 없음(불필요) |
| RFC-0005 | `docs/decisions/rfc/` | Development HQ ↔ Execution Layer Boundary | **Open** | 없음(미작성) | — |
| RFC-0006 | `docs/decisions/rfc/` | Structure v1.0 — hqs/, core/execution/ 재배치 및 docs Taxonomy 정리 | Resolved(헤더는 `Proposed`로 미갱신 — D-9) | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | `ADR-0006-structure-v1-migration.md` |
| RFC-0007 | `docs/decisions/rfc/` | AST 기반 Context 자동 추출의 Production Build Capability 통합 | Resolved(Decision: A. INTEGRATION JUSTIFIED, 조건부 범위로 한정 — 선행조건 2건 모두 Evidence로 해소, `DEV-HQ-V2.0-RFC-0007-REVALIDATION-0001.md` 참고) | `docs/governance/adc/ADC-0005.md`(4개 판단 전부 Accept, 전부 No ADR Required) | 없음(불필요) |
| RFC-0008 | `docs/decisions/rfc/` | AST Context Module Discovery — Dotted Package Path 지원 확장 여부 | Resolved(Decision: B, Conditional Accept) | `docs/governance/adc/ADC-0006.md` | 없음(불필요 — 확장 자체는 MVP Implementation 범위, Conditions 이행은 후속 구현 Task) |
| RFC-0001 | `docs/architecture/core/` | Jarvis OS Kernel Baseline | Resolved | `ADC-0001-core-baseline.md` | 없음(불필요) |
| RFC-0002 | `docs/architecture/core/` | Kernel Definition — Responsibility, Not Component | Resolved | `ADC-0002-kernel-definition.md` | `ADR-0002`(RFC 헤더 원문 인용 — 저장소에 동일 번호 ADR-0002가 두 곳 존재해 대상 특정 불가, `Undetermined` — 아래 §Open Issues) |
| RFC-0003 | `docs/architecture/core/` | Kernel Context Model — Context, Builder, Assembly, Prompt Projection | Resolved | `ADC-0003-kernel-context-model.md` | `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md` |
| RFC-0004 | `docs/architecture/core/` | Kernel Public Contract | Resolved | `ADC-0004-kernel-public-contract.md` | `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md` |
| RFC-0005 | `docs/architecture/core/` | Kernel Logical Reference Architecture — 책임의 배선도 | Resolved | `ADC-0005-kernel-logical-reference-architecture.md` | `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md` |
| RFC-0006 | `docs/architecture/core/` | Kernel Context Ownership | Resolved | `ADC-0006-kernel-context-ownership.md` | 없음(불필요) |
| RFC-0007 | `docs/architecture/core/` | Kernel Context Identity | Resolved | `ADC-0007-kernel-context-identity.md` | 없음(불필요) |
| RFC-0008 | `docs/architecture/core/` | Runtime 개념의 존폐 — Boundary (ADC-02 후속) | Resolved(Not Accepted, based on current evidence; 헤더는 `Proposed`로 미갱신 — D-9) | `ADC-0008-runtime-existence-boundary.md` | 없음(불필요) |
| RFC-0009 | `docs/architecture/core/` | Model 축과 Component 축의 대응 관계 — Boundary | Resolved(Not Accepted; 헤더는 `Proposed`로 미갱신 — D-9) | `ADC-0009-model-component-correspondence-boundary.md` | 없음(불필요) |
| RFC-0010 | `docs/architecture/core/` | Engine Caller의 위치와 책임 — Boundary | Resolved(Not Accepted; 헤더는 `Proposed`로 미갱신 — D-9) | `ADC-0010-engine-caller-location-boundary.md` | 없음(불필요) |
| RFC-0011 | `docs/architecture/core/` | Kernel/HQ에 속하지 않는 별도 실행 위치 — Boundary | Resolved(Not Accepted; 헤더는 `Proposed`로 미갱신 — D-9) | `ADC-0011-standalone-execution-location-boundary.md` | 없음(불필요) |
| RFC-0012 | `docs/architecture/core/` | Dispatch Component의 Architecture Boundary | Resolved(Not Accepted/DEFER; 헤더는 `Proposed`로 미갱신 — D-9) | `ADC-0012-dispatch-component-boundary.md` | 없음(불필요) |
| RFC-0001 | `docs/core/execution-layer/` | Spec-Repository Artifact Drift — Boundary | Resolved(Not Accepted, based on current evidence) | `ADC-0001-artifact-drift-boundary.md` | 없음(불필요) |
| RFC-0002 | `docs/core/execution-layer/` | Execution Result Contract — 산출물을 묶는 방식 | Resolved | `ADC-0002-execution-result-contract.md` | `ADR-0001-execution-result-contract.md` |
| RFC-0003 | `docs/core/execution-layer/` | Execution Result Item Schema — 목록 항목의 형태 | Resolved | `ADC-0003-execution-result-item-schema.md` | `ADR-0002-execution-result-item-schema.md` |
| RFC-0004 | `docs/core/execution-layer/` | Execution Result Consumer — 소비 주체와 방식 | Resolved(Not Accepted, based on current evidence) | `ADC-0004-execution-result-consumer.md` | 없음(불필요) |
| RFC-0005 | `docs/core/execution-layer/` | Engine 연결 Boundary | **Open**(헤더 `Proposed`가 실제 상태와 일치하는 유일한 사례) | 없음(미작성, `Undetermined` — 후속 착수 여부를 밝힌 문서를 찾지 못함) | — |

(출처: 각 RFC 파일 자체의 `**Status**` 헤더 원문 인용 + `docs/decisions/
adc/ADC.md`·`docs/governance/adc/`·`docs/architecture/core/ADC-*.md`·
`docs/core/execution-layer/ADC-*.md` 실제 파일 존재 확인.
`STABILITY-0001-core-architecture.md` §1.2는 참고했으나, 그 시점 이후
추가된 RFC/ADC(위 Kernel RFC-0008~0012, Execution Layer RFC-0002~0005,
Dev HQ RFC-0006)는 이번 확인으로 갱신했다. ID는 각 Location 내부에서만
고유하다 — 트리를 가로질러서는 번호가 재사용된다.)

RFC-0001(Development HQ 수준)은 Development HQ MVP-0001 구현 중 관찰된
Kernel Extraction Candidate(Task Dispatcher, Engine Gateway, Registry,
Context 전달 메커니즘)를 근거로 Kernel Boundary 논의가 필요한 시점인지를
제기한다. 답은 제시하지 않는다. → `RFC-0001-kernel-boundary.md`

**실제 Open RFC는 2건**이다 — Development HQ 수준 RFC-0005(후속 ADC
미작성), Execution Layer 수준 RFC-0005(후속 ADC 미작성, 여부 자체가
Undetermined). Development HQ 수준 RFC-0007은 후속 ADC(`ADC-0005`,
4개 판단 전부 Accept, 전부 No ADR Required)가 작성되어 Resolved로
전환됐다. Development HQ 수준 RFC-0008(Agent Package Refactoring
작업 중 발견)도 후속 ADC(`ADC-0006`, Decision B Conditional Accept)가
작성되어 Resolved로 전환됐다. Kernel 영역도 Development HQ Phase
1(종료됨)도 이 RFC들에 의존하지 않는다(`STABILITY-0001` §1.3,
Development HQ RFC-0005에 한해 확인됨 — Execution Layer RFC-0005의
동일 여부는 이번 확인 범위 밖).

## Open Issues (이번 확인으로 발견, 해결하지 않음)

- Kernel RFC-0002의 "후속 ADR" 참조가 RFC 파일 원문에 `ADR-0002`로만
  적혀 있으나, 저장소에는 같은 번호의 ADR-0002가 **두 곳**
  (`docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md`,
  `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`)
  존재해 어느 쪽을 가리키는지 파일 원문만으로 확정할 수 없다 —
  `Undetermined`로 남긴다.
- Execution Layer RFC-0005는 후속 ADC 존재 여부 자체가 확인되지 않아
  `Undetermined`로 남긴다(`docs/core/execution-layer/`에 ADC-0006 이상
  파일 없음 — 미작성으로 잠정 판단하되, 다른 트리에 등록됐을 가능성은
  배제하지 않는다).
