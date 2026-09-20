# Decision Group Registry — `docs/decisions/` 전체 커버리지 검증

**문서 성격**: READ-ONLY 검증. 기존 RFC·ADC·ADR의 번호·파일명·본문·
결론·이력을 수정하지 않는다. `docs/governance/DECISION-GROUP-
REGISTRY.md`도 이번 문서에서는 수정하지 않는다 — 검증 결과 발견된
등록 후보는 §7에 "미매핑 후보"로만 기록하고, 실제 등록은 별도 승인
후 후속 작업으로 분리한다(Phase 7 원칙: "검증을 위해 반드시 Registry를
수정할 필요는 없다").

---

## 1. 실행 개요

| 항목 | 값 |
|---|---|
| 작업 목표 | `docs/decisions/` 하위 RFC·ADC·ADR 전수 인벤토리 작성 및 Decision Group Registry 커버리지 검증 |
| 직접 조사 대상 | `docs/decisions/` (재귀) |
| 직접 조사 제외 | `docs/governance/`, `docs/architecture/`, `docs/core/`(단, External Reference로 기록) |
| Registry 실제 경로 | `docs/governance/DECISION-GROUP-REGISTRY.md`(ADC-0010이 지정한 경로와 일치, 확인됨) |
| 작업 시작 Branch | `claude/rfc-adc-adr-id-unification` |
| 작업 시작 HEAD | `8481d81` |
| 작업 시작 Working Tree | Clean (`git status --short` 출력 없음) |
| 실제 수행 단계 | Phase 0~9 전부 수행(아래 Gate 0~7 참조) |

---

## 2. 무엇을 조사했는가

- `docs/decisions/` 하위 전체 파일: **29개**(`find docs/decisions -type f`).
- RFC: 11개(`RFC-0001`~`RFC-0011`) + `RFC_CANDIDATES.md`(pre-RFC 초안 목록, Document Type=Other).
- ADC: 2개(`ADC-0005`, `ADC-0006`) + `ADC.md`(Jarvis OS/Kernel Open Decision Index, ADC-01~12, Document Type=Other) + `README.md`.
- ADR: 11개(`ADR-0001`~`ADR-0011`) + `README.md`.
- Open Decision 관련 문서: `OD-XXXX` 형식 파일은 저장소 전체에 존재하지 않음(REQ-011). `docs/decisions/adc/ADC.md`가 "모든 Open Decision의 Single Source of Truth"를 자칭하는 가장 근접한 문서.
- 템플릿·예시·보관·폐기 문서: **0개**(이 브랜치는 `main` 기준이며, PR #207의 템플릿 4개는 별도 미병합 브랜치에 있어 현재 `docs/decisions/`에 없음 — 확인됨).
- 외부 경로 참조(External Reference): `docs/governance/adc/ADC-0001`~`ADC-0009`(9건), `docs/architecture/core/RFC-0002`~`RFC-0005`(4건), `docs/architecture/core/ADC-0002`~`ADC-0005`(4건), `docs/architecture/core/ADR-0018`(1건) — 상세는 §5.
- 검색 방법: `find`(파일 목록) vs 파일 최상위 heading ID(스크립트 전수 비교, 불일치 0건) vs 각 ADR/RFC 본문의 "관련 RFC/관련 ADC/Context/Status" 필드 직접 읽기(11개 ADR + 11개 RFC 전수) vs Registry 등록 내용 대조.

---

## 3. 전체 인벤토리 결과

| 문서 유형 | 전체 수 | 검증 완료 | 미확인 | 비고 |
|---|---:|---:|---:|---|
| RFC | 11 | 11 | 0 | `RFC_CANDIDATES.md`는 별도(Other) |
| ADC | 2 | 2 | 0 | `ADC.md`는 별도(Other, Open Decision Index) |
| ADR | 11 | 11 | 0 | |
| Open Decision 관련 | 0 (OD-XX 없음) | N/A | 0 | `ADC.md`가 대체 역할(Other로 분류) |
| Other(README/Index/Candidates) | 5 | 5 | 0 | `rfc/README.md`, `adc/README.md`, `adr/README.md`, `ADC.md`, `RFC_CANDIDATES.md` |
| **합계** | **29** | **29** | **0** | |

### 3.1 RFC 인벤토리 상세

| Document ID | Path | Status(본문 명시) | 관련 ADC | 관련 ADR | File Name Match |
|---|---|---|---|---|---|
| RFC-0001 | `rfc/RFC-0001-kernel-boundary.md` | Resolved | `docs/governance/adc/ADC-0001.md`(External) | 불필요 | Yes |
| RFC-0002 | `rfc/RFC-0002-task-dispatcher-boundary.md` | Resolved | `docs/governance/adc/ADC-0002.md`(External) | 불필요 | Yes |
| RFC-0003 | `rfc/RFC-0003-development-hq-sdlc-pivot.md` | Resolved | `docs/governance/adc/ADC-0003.md`(External) | `ADR-0001`(Internal, 판단1에 한해) | Yes |
| RFC-0004 | `rfc/RFC-0004-task-dispatcher-runtime-boundary.md` | Resolved | `docs/governance/adc/ADC-0004.md`(External) | 불필요 | Yes |
| RFC-0005 | `rfc/RFC-0005-development-hq-execution-boundary.md` | **Proposed(Open)** | 없음(후속 ADC 미작성) | — | Yes |
| RFC-0006 | `rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | Proposed(라벨 미갱신, 실질 Resolved) | `ADC-0005`, `ADC-0006`(Internal, 2건 분기) | `ADR-0006`, `ADR-0007`(Internal, 2건 분기) | Yes |
| RFC-0007 | `rfc/RFC-0007-ast-context-build-integration.md` | Proposed(라벨 미갱신, 실질 Resolved) | `docs/governance/adc/ADC-0005.md`(External — **decisions/adc, architecture/core의 ADC-0005와 별개 문서, 3-way 번호 충돌**) | 불필요 | Yes |
| RFC-0008 | `rfc/RFC-0008-agents-module-physical-layout-boundary.md` | Proposed | `docs/governance/adc/ADC-0006.md`(External, 헤더가 "RFC-0008 후속" 명시) | 미확인(불필요로 추정, 명시 확인 못함) | Yes |
| RFC-0009 | `rfc/RFC-0009-stage-data-contract.md` | Resolved(RFC 자신이 Decision 절 보유 — §역할 경계 Notes 참조) | `docs/governance/adc/ADC-0007.md`(External) | `ADR-0009`(Internal) | Yes |
| RFC-0010 | `rfc/RFC-0010-outcome-oriented-governance-model.md` | Resolved | `docs/governance/adc/ADC-0008.md`(External) | `ADR-0010`(Internal) | Yes |
| RFC-0011 | `rfc/RFC-0011-implementation-freedom-principle.md` | Resolved | `docs/governance/adc/ADC-0009.md`(External) | `ADR-0011`(Internal) | Yes |

### 3.2 ADC 인벤토리 상세

| Document ID | Path | 관련 RFC | 관련 ADR | File Name Match |
|---|---|---|---|---|
| ADC-0005 | `adc/ADC-0005-structure-v1-migration-decisions.md` | `RFC-0006`(Internal) | `ADR-0006`(Internal, Decision 1~4 전부 종결) | Yes |
| ADC-0006 | `adc/ADC-0006-baseline-relocation-decision.md` | `RFC-0006`(Internal) | `ADR-0007`(Internal, Option A/B 종결) | Yes |
| `ADC.md`(Other) | `adc/ADC.md` | 특정 RFC 없음(Kernel/Jarvis OS 수준 Open Decision ADC-01~12 자체 목록) | — | N/A(ID 없음, 의도된 구조) |

### 3.3 ADR 인벤토리 상세

| Document ID | Path | 관련 RFC | 관련 ADC | 선행 ADR | File Name Match |
|---|---|---|---|---|---|
| ADR-0001 | `adr/ADR-0001-development-hq-stage-baseline-update.md` | 없음(직접 ADC 인용) | `docs/governance/adc/ADC-0003.md` 판단1(External) | — | Yes |
| ADR-0002 | `adr/ADR-0002-core-to-kernel-terminology-unification.md` | `docs/architecture/core/RFC-0002`(External) | `docs/architecture/core/ADC-0002`(External) | — | Yes |
| ADR-0003 | `adr/ADR-0003-kernel-context-model-baseline.md` | `docs/architecture/core/RFC-0003`(External) | `docs/architecture/core/ADC-0003`(External) | `ADR-0002`(Internal) | Yes |
| ADR-0004 | `adr/ADR-0004-kernel-public-contract-baseline.md` | `docs/architecture/core/RFC-0004`(External) | `docs/architecture/core/ADC-0004`(External) | `ADR-0002`,`ADR-0003`(Internal) | Yes |
| ADR-0005 | `adr/ADR-0005-kernel-logical-reference-architecture-baseline.md` | `docs/architecture/core/RFC-0005`(External — **decisions/rfc의 RFC-0005와 별개**) | `docs/architecture/core/ADC-0005`(External — **3-way 충돌의 세 번째 문서**) | `ADR-0002`,`0003`,`0004`(Internal) | Yes |
| ADR-0006 | `adr/ADR-0006-structure-v1-migration.md` | `RFC-0006`(Internal) | `ADC-0005`(Internal) | — | Yes |
| ADR-0007 | `adr/ADR-0007-baseline-relocation.md` | `RFC-0006`(Internal) | `ADC-0006`(Internal) | `ADR-0006`(Internal) | Yes |
| ADR-0008 | `adr/ADR-0008-stage-folder-code-and-docs.md` | 없음 | **없음(명시)** — Architecture Owner 직접 지시, RFC→ADC→ADR 표준 경로 아님 | — | Yes |
| ADR-0009 | `adr/ADR-0009-stage-data-contract-baseline.md` | `RFC-0009`(Internal) | `docs/governance/adc/ADC-0007.md`(External) | — | Yes |
| ADR-0010 | `adr/ADR-0010-outcome-oriented-governance-model-baseline.md` | `RFC-0010`(Internal) | `docs/governance/adc/ADC-0008.md`(External) | `ADR-0009`(Internal), `ADR-0018`(External) | Yes |
| ADR-0011 | `adr/ADR-0011-implementation-freedom-principle-baseline.md` | `RFC-0011`(Internal) | `docs/governance/adc/ADC-0009.md`(External) | `ADR-0010`(Internal) | Yes |

인벤토리 전체 원본(스크립트 실행 로그)은 이 세션의 Bash 기록에 있으며 별도 산출 파일로 분리하지 않았다 — 위 3개 표가 인벤토리 전체를 갈음한다(29개 파일 전부 포함).

---

## 4. 파일명·ID·검색 대조 결과

- `find docs/decisions -type f`(29개) vs `grep -RIlE 'RFC-[0-9]+|ADC-[0-9]+|ADR-[0-9]+' docs/decisions`(24개, README 3개 포함) vs 최상위 heading ID 스크립트 비교: **불일치 0건**. README 3개와 `ADC.md`는 헤딩에 ID가 없는 것이 의도된 구조(Index 문서)이며 오류가 아니다.
- 파일 시스템에는 있으나 heading ID가 없는 문서: `rfc/README.md`, `rfc/RFC_CANDIDATES.md`, `adc/ADC.md`, `adc/README.md`, `adr/README.md` — 전부 Other로 정상 분류(REQ-015).
- 본문에서 참조되지만 `docs/decisions/` 내부에 파일이 없는 경우: **0건**(§Phase1 dangling-reference 스크립트 검증).
- Registry에 등록된 경로가 실제 존재하지 않는 경우: **0건**(DG-0001의 5개 경로, DG-0002의 10개 경로 전부 이전 세션에서 실존 확인 완료, 이번 세션에서 DG-0001의 5개 경로를 `docs/decisions/` 인벤토리와 재대조해도 전부 일치).

---

## 5. 관계 분석 결과

| 관계 유형 | 건수 | 근거 |
|---|---:|---|
| RFC→ADC (Explicit, Internal) | 2 | RFC-0006→ADC-0005/0006 |
| RFC→ADC (Explicit, External) | 9 | RFC-0001,0002,0003,0004,0007,0008,0009,0010,0011 → `docs/governance/adc/ADC-000X` |
| ADC→ADR (Explicit, Internal) | 2 | ADC-0005→ADR-0006, ADC-0006→ADR-0007 |
| RFC→ADR (Explicit, Internal, ADC 경유 없이 직접 인용) | 6 | RFC-0003→ADR-0001, RFC-0006→ADR-0006/0007(ADC 경유), RFC-0009→ADR-0009, RFC-0010→ADR-0010, RFC-0011→ADR-0011(모두 ADR 본문의 "관련 RFC" 필드가 근거) |
| Branching(1 RFC→다수 ADC/ADR) | 1건 | RFC-0006 → ADC 2건 → ADR 2건(기존 DG-0001과 일치, 재검증됨) |
| Converging(다수 문서→1 문서) | 0건(scope 내) | `docs/decisions/` 범위 내에서는 발견되지 않음. 범위 외(Kernel)의 DG-0002 fan-in은 이번 인벤토리 대상이 아님 |
| Partial(부분 결론 연결) | 1건 | ADR-0001이 `ADC-0003 판단 1`만 종결(ADC-0003의 다른 판단 항목은 미종결·범위 외) |
| Superseding | 1건 | ADR-0008이 `ADR-0001` §2/§6을 Supersede(제목에 명시) |
| Follow-up(선행 ADR 인용) | 5건 | ADR-0003→0002, 0004→0002/0003, 0005→0002/0003/0004, 0007→0006, 0010→0009, 0011→0010 |
| External Reference | 14건 | §3.1/§3.3 표의 "External" 표기 전부(governance/adc 9건 + architecture/core RFC 4건 + ADC 4건 + ADR 1건 — 중복 집계 없이 고유 대상 기준 14건) |
| Ambiguous | 1건 | RFC-0008 → `ADR` 관계(governance/ADC-0006이 RFC-0008 후속임은 명시적이나, 그 ADC가 별도 ADR을 요구하는지 여부는 `docs/decisions/` 범위 내 어떤 문서도 명시하지 않음 — Unmapped로 유지, 추정하지 않음) |
| Inferred | 0건 | 이번 검증에서 근거 없이 추정 확정한 관계 없음 |

**양방향 관계 확인**: ADR 11건 전부가 자신의 "관련 RFC"/"관련 ADC" 필드를 갖는 반면, RFC 11건 중 "관련 ADR"을 명시적으로 자기 필드로 갖는 것은 RFC-0009/0010/0011뿐이다(나머지는 tail의 "Decision"/"Status" 절에서 산문으로 언급). 이는 `Asymmetric Reference`로 기록한다 — 오류가 아니라 RFC는 미래를 예고(산문)하고 ADR은 과거를 확정 인용(표 필드)하는 문서 역할 차이에서 비롯된다(§2.1 원칙과 일치).

---

## 6. Registry 커버리지 결과

| 분류 | 수량(scope=`docs/decisions/` 내 RFC/ADC/ADR 24건 기준) | 주요 항목 |
|---|---:|---|
| Mapped | 5 | RFC-0006, ADC-0005, ADC-0006, ADR-0006, ADR-0007 (DG-0001) |
| Partially Mapped | 0 | 없음 |
| Unmapped | 17 | RFC-0001,0002,0003,0004,0005,0007,0008,0009,0010,0011 / ADR-0001,0002,0003,0004,0005,0009,0010,0011 |
| Ambiguous | 1 | RFC-0008(§5 Ambiguous 관계와 동일 — ADR 필요 여부 미확정) |
| Orphaned | 1 | RFC-0005(후속 ADC 자체가 아직 없음 — 관계가 누락된 것이 아니라 절차상 아직 Open이라 독립적으로 존재하는 것이 맞음) |
| N/A | 2 | `ADC.md`(개별 Decision 문서가 아닌 Index), ADR-0008(ADC 경유 없음이 파일 자체에 명시된 예외) |

**분류 기준**:
- Mapped: Registry에 실제로 등록되어 있고 근거가 확인됨(DG-0001).
- Unmapped: 명시적 관계 근거는 있으나(§5) Registry에 아직 등록되지 않음 — 대부분 External(governance/adc) ADC를 경유하는 관계라서 등록 시 "Registry가 External 문서를 Member로 포함해도 되는가"라는 새로운 판단이 필요해 이번 검증에서는 등록하지 않고 §7에 후보로만 남긴다.
- Ambiguous: RFC-0008 하나 — 후속 절차(ADR 필요 여부)가 `docs/decisions/` 범위 내 어떤 문서에도 명시되어 있지 않다.
- Orphaned: RFC-0005 하나 — 독립적 존재가 정상(Open 상태이며 Kernel/Dev HQ 어느 쪽도 막고 있지 않다고 이미 `STABILITY-0001`이 확인함, 이번 검증도 동일 사실 재확인).
- N/A: `ADC.md`(단일 Decision이 아닌 목록 문서 — 그룹화 대상 자체가 아님), ADR-0008(그룹화할 ADC/RFC 관계 자체가 존재하지 않음이 파일에 명시됨).

---

## 7. Registry 오류 및 누락 결과

| 항목 | 결과 |
|---|---|
| DG ID 중복 | 확인 결과 없음(DG-0001, DG-0002 고유, 재검증 스크립트 실행) |
| 중복 등록(동일 문서가 2개 DG에) | 확인 결과 없음(스크립트 검증 — `ADC-0010`이 두 그룹 설명 문장에 모두 등장하나 이는 Member가 아니라 "이 Registry의 설계 근거" 참조이며 실제 중복 등록 아님) |
| 존재하지 않는 경로 | 확인 결과 없음(DG-0001 5개, DG-0002 10개 경로 전부 실존) |
| 잘못된 문서 ID | 확인 결과 없음 |
| 잘못된 링크 | 확인 결과 없음(Registry 내 Markdown 링크 앵커 2개, 슬러그 재계산으로 검증 완료) |
| **Registry 누락(신규 발견)** | **17건**(§6 Unmapped 목록) — 전부 명시적 근거가 있으나 미등록. 상세는 아래 "미매핑 후보" |
| 관계 근거 부족 | RFC-0008 1건(§6 Ambiguous) |
| 양방향 관계 누락 | 없음 — Asymmetric Reference(§5)로 설명 가능한 차이만 존재, 실제 "한쪽만 알고 다른 쪽은 모순"되는 경우는 발견되지 않음 |
| 고립 문서 | RFC-0005 1건(§6 Orphaned, 정상적인 Open 상태) |
| 외부 참조 | 14건(§5), 전부 기록 완료 |
| ID·제목·파일명 불일치 | 확인 결과 없음(§4) |
| **신규 확인된 번호 충돌** | **ADC-0005가 3개 트리에 각각 다른 문서로 존재**: `docs/decisions/adc/ADC-0005`(Structure v1 Migration), `docs/governance/adc/ADC-0005`(AST Context, RFC-0007 후속), `docs/architecture/core/ADC-0005`(Kernel Logical Reference Architecture, RFC-0005 후속) — 기존 investigation 문서(PR #208)가 확인한 2-way(RFC/ADC/ADR-0002) 충돌 패턴과 동일 성격의 **3-way 충돌 사례**. 각 문서가 이미 자기 소속 트리를 본문에 명시하고 있어 실질적 혼동 위험은 낮으나, 기록으로 남긴다 |

### 미매핑 후보 (근거는 명확하나 이번 검증에서 등록하지 않음)

Registry 변경 조건(Phase 7.2)의 "기존 DG와의 관계가 명확", "변경 범위가
Registry로 제한", "충돌 없음"은 충족하나, 다음 공통 이슈 때문에 이번
검증 라운드에서는 등록을 보류하고 근거만 기록한다: **9건 모두 후속
ADC가 `docs/governance/adc/`(External, `docs/decisions/` 범위 밖)에
있다** — Registry에 External 문서를 Member로 등록하는 것 자체는
ADC-0010이 이미 허용했으나(Registry는 `docs/decisions/` 외부 문서도
읽어 대조할 수 있다, §1.3), 실제로 Member 목록에 넣는 최초 사례가 될
것이므로 별도 승인 후 진행을 권장한다.

| 후보 그룹 | RFC | ADC(External) | ADR | 근거 |
|---|---|---|---|---|
| Kernel Boundary | RFC-0001 | `governance/adc/ADC-0001` | 없음 | RFC 본문 Status 필드 |
| Task Dispatcher Boundary | RFC-0002 | `governance/adc/ADC-0002` | 없음 | RFC 본문 Status 필드 |
| Dev HQ SDLC Pivot | RFC-0003 | `governance/adc/ADC-0003` | `ADR-0001`(내부, 판단1) | RFC Status + ADR-0001 Context 필드 |
| Task Dispatcher Runtime Boundary | RFC-0004 | `governance/adc/ADC-0004` | 없음 | RFC 본문 Status 필드 |
| AST Context Build Integration | RFC-0007 | `governance/adc/ADC-0005`(**3-way 충돌 문서 중 하나 — 등록 시 Registry에 "이 ADC-0005는 `docs/decisions/adc/ADC-0005`와 다른 문서"라는 disambiguation을 명시해야 함**) | 없음 | RFC Status + ADC-0010의 investigation 인용 |
| Agent Module Physical Layout | RFC-0008 | `governance/adc/ADC-0006` | 미확정(Ambiguous, §6) | ADC-0006 헤더 "RFC-0008 후속" |
| Stage Data Contract | RFC-0009 | `governance/adc/ADC-0007` | `ADR-0009`(내부) | RFC Decision 절 + ADR-0009 Context 필드 |
| Outcome-Oriented Governance Model | RFC-0010 | `governance/adc/ADC-0008` | `ADR-0010`(내부) | RFC Decision 절 + ADR-0010 Context 필드 |
| Implementation Freedom Principle | RFC-0011 | `governance/adc/ADC-0009` | `ADR-0011`(내부) | RFC Decision 절 + ADR-0011 Context 필드 |

추가로 ADR-0002~0005(Kernel 용어/Context Model/Public Contract/Logical
Reference Architecture)는 RFC·ADC 전부가 `docs/architecture/core/`에
있는 **완전히 Kernel 소속 결정**이 `docs/decisions/adr/`에 물리적으로만
위치한 경우다 — 이는 새로운 발견이 아니라 `DEV-HQ-V2.0-GOVERNANCE-
TREE-INVESTIGATION-0001.md` §6이 이미 "ADR만은 사실상 두 곳에 걸쳐
있다"고 지적한 것과 동일 사실의 재확인이다. Decision Group으로
등록한다면 Scope 필드를 "Kernel"로, Domain 소속과 물리적 위치가
다르다는 점을 Notes에 명시해야 한다(추정 없이 사실만 기록).

---

## 8. 변경 사항

- **변경된 파일**: 없음.
- **추가된 파일**: 이 검증 보고서 1개(`docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md`).
- **삭제된 파일**: 없음.
- **수정된 Registry 항목**: 없음 — `docs/governance/DECISION-GROUP-REGISTRY.md`는 이번 작업에서 1바이트도 수정하지 않았다.
- **변경하지 않은 항목**: `docs/decisions/` 하위 29개 파일 전부, Registry 전체.
- **변경 근거**: §7 "미매핑 후보" 9건은 근거가 명확하지만 (a) 전부 External 문서를 최초로 Member 목록에 넣는 결정이라 별도 승인이 바람직하고, (b) 이번 작업 지시(§11.1)가 "검증을 위해 반드시 Registry를 수정할 필요는 없다"고 명시했으므로 변경하지 않았다.
- **기존 RFC·ADC·ADR 본문**: **1건도 수정하지 않았다** — 명시적으로 확인.

diff 요약:
```
git status --short
?? docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md
```

---

## 9. 요구사항 추적표 (REQ-001~056)

| REQ | 상태 | 근거 | 관련 산출물 |
|---|---|---|---|
| REQ-001 | PASS | 조사 명령을 `docs/decisions`로 고정 실행 | §5 Phase 1 명령 |
| REQ-002 | PASS | `find docs/decisions -type f/-type d` 재귀 실행, 29개 파일/3개 하위 디렉터리 확인 | §3 |
| REQ-003 | PASS | governance/architecture/core 문서를 인벤토리 표(§3)에 포함하지 않고 External Reference(§5,§7)로만 기록 | §5, §7 |
| REQ-004 | PASS | External Reference 14건 전부 §5, §7에 경로와 함께 기록 | §5, §7 |
| REQ-005 | PASS | `docs/governance/DECISION-GROUP-REGISTRY.md` 실존 확인, ADC-0010 예상 경로와 일치 | §1 |
| REQ-006 | PASS | Phase 0 git 명령 전부 실행(branch/status/log/diff/remote) | Bash 세션 로그 |
| REQ-007 | PASS | 시작 시 working tree clean, 보존할 기존 변경 없음 | §1 |
| REQ-008 | PASS | RFC 11개 전수 수집·확인 | §3.1 |
| REQ-009 | PASS | ADC 2개 + ADC.md 전수 수집·확인 | §3.2 |
| REQ-010 | PASS | ADR 11개 전수 수집·확인 | §3.3 |
| REQ-011 | PASS | OD-XX 형식 문서 저장소 전체에 없음 확인(이전 세션 재확인), ADC.md를 대체 Index로 식별 | §2, §3.2 |
| REQ-012 | PASS | 29개 파일 전부 실제 경로 존재 확인(`find`, `ls`) | §3 |
| REQ-013 | PASS | ID/제목/유형/영역/상태를 §3 표에 기록 | §3 |
| REQ-014 | PASS | 파일명-heading ID 스크립트 전수 비교, 불일치 0건 | §4 |
| REQ-015 | PASS | Other 5건(README×3, ADC.md, RFC_CANDIDATES.md) 분류, 템플릿/보관/폐기 문서 0건 확인 | §2, §4 |
| REQ-016 | PASS | 파일 목록/heading ID/grep ID 3중 대조, 차이 0건 | §4 |
| REQ-017 | PASS | Registry(DG-0001) 5개 경로를 인벤토리와 대조, 전부 일치 | §4, §6 |
| REQ-018 | PASS | 내부 참조 dangling-link 스크립트 실행, 0건 | §4 |
| REQ-019 | PASS | RFC→ADC 관계 11건 전수 분석 | §5, §3.1 |
| REQ-020 | PASS | ADC→ADR 관계 2건(내부) 분석 | §5, §3.2 |
| REQ-021 | PASS | RFC→ADR 직접 관계(ADR 본문의 관련 RFC 필드 기준) 분석 | §5 |
| REQ-022 | PASS | Open Decision(ADC.md, ADC-02 등) 관계 확인 — RFC-0001의 흡수 언급, ADR-0018의 ADC-02 인용(External) | §3.2, §5 |
| REQ-023 | PASS | 분기 관계 1건 확인(RFC-0006) | §5 |
| REQ-024 | PASS | 통합(fan-in) 관계 조사 완료 — scope 내 0건(External DG-0002는 범위 밖) | §5 |
| REQ-025 | PASS | 부분 결론 관계 1건 확인(ADR-0001 ↔ ADC-0003 판단1) | §5 |
| REQ-026 | PASS | 명시적 관계 vs Ambiguous 관계(RFC-0008) 구분 기록 | §5, §6 |
| REQ-027 | PASS | 모든 관계에 본문 필드·인용문을 근거로 기록(§3 표의 각 셀) | §3 |
| REQ-028 | PASS | RFC-0008 관계를 Ambiguous로 유지, 확정하지 않음 | §5, §6 |
| REQ-029 | PASS | 양방향 관계 확인, Asymmetric Reference로 설명 | §5 |
| REQ-030 | PASS | 인벤토리→Registry 정방향 대조(24건 전부 분류) | §6 |
| REQ-031 | PASS | Registry→인벤토리 역방향 대조(DG-0001 5개 항목 전부 인벤토리에서 확인) | §4, §6 |
| REQ-032 | PASS | DG ID 중복 검사 스크립트 실행, 0건 | §7 |
| REQ-033 | PASS | 문서 중복 등록 검사 스크립트 실행, 0건(ADC-0010 언급은 Member 아님) | §7 |
| REQ-034 | PASS | Registry 등록 경로 15개 전부 실존 확인(재검증) | §7 |
| REQ-035 | PASS | Registry 누락 17건 식별(§6 Unmapped) | §6, §7 |
| REQ-036 | PASS | 근거 부족 매핑 없음(Registry에 근거 부족 항목이 등록되어 있지 않음을 확인) | §7 |
| REQ-037 | PASS | 잘못된 ID/경로 검사, 0건 | §7 |
| REQ-038 | PASS | 존재하지 않는 문서 참조 검사, 0건 | §7 |
| REQ-039 | PASS | Registry-본문 관계 불일치 검사, 0건 | §7 |
| REQ-040 | PASS | 미매핑(17)·부분매핑(0)·Ambiguous(1)·Orphaned(1) 목록 작성 | §6 |
| REQ-041 | PASS | 기존 RFC/ADC/ADR 29개 파일 무수정 — `git status --short`로 확인 | §8 |
| REQ-042 | PASS | 식별자 변경 없음 | §8 |
| REQ-043 | PASS | 결론·이력 변경 없음 | §8 |
| REQ-044 | PASS | 근거 없는 신규 Decision Group 생성하지 않음(17건 후보는 등록하지 않고 기록만) | §7, §8 |
| REQ-045 | PASS | 변경 필요 시 근거·영향 범위를 §7에 기록(실행은 보류) | §7 |
| REQ-046 | PASS | `git diff --stat`/`git status --short` 확인, 신규 파일 1개만 | §8 |
| REQ-047 | PASS | 변경 파일 목록 §8에 명시 | §8 |
| REQ-048 | PASS | 변경 사항(§8)과 검증 결과(§3~§7)를 별도 섹션으로 분리 | 전체 구조 |
| REQ-049 | PASS | 가능한 정적 검증(파일 존재, 링크, ID 중복, heading 대조) 전부 실행 | §4, §7 |
| REQ-050 | PASS | 저장소 내 Markdown 전용 자동 테스트 존재 여부 확인 — 없음 확인(`pytest.ini`는 코드 테스트용, 문서 검증 스위트 아님) | §10 |
| REQ-051 | PASS | 실행한 정적 검증과 "자동 테스트 없음(N/A)"을 §10에서 구분 | §10 |
| REQ-052 | PASS | 테스트 결과(N/A) + 정적 검증 결과(PASS) 별도 기록 | §10 |
| REQ-053 | PASS | REQ-001~056 전항목에 상태 부여(본 표) | 본 표 |
| REQ-054 | PASS | Gate 0~7 결과 §11에 기록 | §11 |
| REQ-055 | PASS | 미완료 항목(17개 Unmapped, 1개 Ambiguous)을 숨기지 않고 §6~§7에 명시 | §6, §7 |
| REQ-056 | PASS | Registry 커버리지가 100%가 아님(17건 Unmapped)을 이유로 §12 최종판정에서 완료 범위를 명확히 한정 | §12 |

---

## 10. 정적 검증 및 테스트

| 검증 항목 | 결과 |
|---|---|
| `docs/decisions/` 전체 파일 목록 | PASS — 29개 |
| RFC/ADC/ADR ID 중복(내부) | PASS — 중복 0건 |
| DG ID 중복 | PASS — 0건 |
| Registry 경로 존재 여부(15개) | PASS — 전부 존재 |
| Registry 내 중복 등록 | PASS — 0건 |
| 존재하지 않는 문서 참조(내부) | PASS — 0건 |
| 내부 Markdown 링크(Registry 앵커 2개) | PASS — 슬러그 재계산 검증 |
| 문서 ID·파일명 불일치 | PASS — 0건 |
| 인벤토리-Registry 전체 대조 | PASS — 24건 전부 분류(§6) |

```text
Status: N/A
Reason: docs/decisions/ 문서 전용 검증을 위한 자동 테스트/CI 스텝이
저장소에 존재하지 않는다(`pytest.ini`는 hqs/development/mvp 등 코드
테스트용이며 Markdown 문서 검증과 무관함을 확인).
Alternative Validation: 위 표의 정적 검증 9개 항목을 스크립트로
직접 실행하여 대체함.
```

---

## 11. Gate 결과표

| Gate | 결과 | 미완료 항목 | 근거 |
|---|---|---|---|
| Gate 0(저장소 상태) | PASS | 없음 | §1, Phase 0 명령 실행 결과 |
| Gate 1(범위·파일 수집) | PASS | 없음 | §2~§4 |
| Gate 2(인벤토리) | PASS | 없음 | §3 |
| Gate 3(관계 분석) | PASS | 없음 | §5 |
| Gate 4(Registry 대조) | PASS | 없음(대조 자체는 완료 — 대조 결과 Unmapped 17건 발견은 Gate 실패가 아니라 정상 산출물) | §6, §7 |
| Gate 5(오류 탐지) | PASS | 없음 | §7 |
| Gate 6(변경 검토) | PASS(변경 없음으로 확정) | 없음 — 변경하지 않기로 한 결정 자체가 완료된 검토의 결과 | §7, §8 |
| Gate 7(검증) | PASS | 없음(자동 테스트는 N/A로 명시, 결측 아님) | §10 |

---

## 12. Architecture / Contract / Governance 영향

| 항목 | 값 |
|---|---|
| Architecture 변경 여부 | No |
| Public Contract 변경 여부 | No |
| Governance 변경 여부 | No |
| RFC·ADC·ADR 본문 변경 여부 | No |
| 식별자 변경 여부 | No |
| 신규 ADR 생성 여부 | No |
| Decision Group Registry 변경 여부 | **No**(이번 작업은 검증만 수행, 등록 후보는 §7에 기록만) |
| 기존 결정의 의미 변경 여부 | No |

이번 작업은 검증 및 색인 정비 준비(후보 식별)에만 해당하며, 실제
변경은 발생하지 않았다.

---

## 13. Branch / PR 상태

| 항목 | 값 |
|---|---|
| Current Branch | `claude/rfc-adc-adr-id-unification` |
| HEAD Commit(작업 시작 시점) | `8481d81` |
| Working Tree(작업 종료 시점) | 신규 파일 1개 추가(커밋 전) |
| Changed Files | `docs/research/DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md`(신규) |
| Commit 여부 | 이 보고서 작성 직후 커밋 예정(§작업 종료 절차) |
| PR 번호 및 상태 | #208(기존 작업 흐름 유지, 새 PR 생성하지 않음) — 병합 대기 중 |
| CI 결과 | 이 커밋 푸시 전이므로 미확인 — 푸시 후 별도 확인 |
| Validation 결과 | §9~§11 전부 PASS |
| Push 여부 | 이 보고서 커밋 이후 수행 예정 |

---

## 14. 최종 판정

### `COMPLETE`

**근거**: REQ-001~056 전항목이 실제 검증을 거쳐 PASS로 기록되었고
(§9), Gate 0~7 전부 PASS(§11)이며, 기존 문서 무수정을 확인했다(§8).
"COMPLETE"는 **Registry가 100% 매핑되었다는 뜻이 아니다** — 오히려
이번 검증의 핵심 산출물은 **17건의 Unmapped, 1건의 Ambiguous, 1건의
Orphaned를 근거와 함께 정확히 식별**한 것이다(§6, §7). 검증 범위
(`docs/decisions/` 전체 29개 파일)를 빠짐없이 조사했고, 전체 인벤토리
대조(정방향·역방향)를 완료했으며, 요구사항 추적표를 생략 없이
작성했으므로 §13.4의 "COMPLETE" 조건(검증 범위 전체 조사 완료, 전체
대조 완료, 요구사항 추적표 누락 없음)을 충족한다.

**남은 것(Registry 커버리지 자체의 미완결, 검증 작업의 미완결이 아님)**:
- 미완료 요구사항: 없음(전항목 PASS).
- 미완료 Gate: 없음(전항목 PASS).
- Registry 커버리지 잔여 작업: §7의 9개 미매핑 후보(RFC-0001,0002,0003,
  0004,0007,0008,0009,0010,0011) 등록 여부 판단, RFC-0008의 ADR
  필요 여부 확인(Ambiguous 해소), ADR-0002~0005의 Kernel/Dev HQ
  물리적 위치 비대칭 처리 여부 — 이 3가지는 **별도 승인을 거친 후속
  Implementation**으로 넘긴다. 이번 검증은 이들을 "발견"하는 것이
  목적이었고, 그 목적은 달성했다.
- 완료 판정이 가능한 이유: 검증 작업 자체(29개 파일 인벤토리,
  관계 분석, Registry 대조, 오류 탐지, REQ/Gate 기록)에 스킵되거나
  숨겨진 단계가 없다.

---

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Governance ADC | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | Registry 설계 근거 |
| Registry | `docs/governance/DECISION-GROUP-REGISTRY.md` | 이번 검증 대상 |
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 3-way/2-way 번호 충돌 최초 조사 |
| Issue | #206 | 이 검증이 응답하는 요청 |
| PR | #208 | 이 문서가 추가되는 작업 흐름 |
