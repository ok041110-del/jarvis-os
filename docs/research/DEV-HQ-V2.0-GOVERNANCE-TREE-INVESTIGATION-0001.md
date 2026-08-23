# Governance Tree Investigation — docs/ Governance 문서 트리 병존 조사

**문서 성격**: READ-ONLY 조사. 문서 이동/삭제/이름 변경, Governance 규칙
변경, Architecture/Contract/코드 변경을 하지 않는다. 필요한 정리는
Recommendation으로만 남긴다.

## 1. 목적

`DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001.md`(T01) §15/§19가 남긴
Open Issue — "두 Governance 문서 트리(`docs/decisions/` vs
`docs/governance/`+`docs/architecture/core/`)의 번호 중복" — 를
Evidence 기반으로 조사한다. 실제로는 조사 결과 트리가 2개가 아니라
**4~5개**임이 드러났다(§4 참조). 구조를 고치기 전에 그 구조가 왜
존재하는지를 먼저 증명한다.

## 2. Audit Scope

- `docs/00_governance/`, `docs/decisions/{rfc,adc,adr}/`,
  `docs/governance/{adc,observations,rt}/`, `docs/architecture/{baseline,core}/`,
  `docs/core/execution-layer/`
- 위 트리들의 RFC/ADC/ADR 상호 참조, 생성 시점(Git History), Migration
  관련 RFC-0006/ADC-0005/ADC-0006/ADR-0006/ADR-0007
- `docs/architecture/core/DOC-TRIAGE-0001.md`, `STABILITY-0001-core-
  architecture.md` — 이 정확히 같은 질문을 이미 다룬 선행 문서

## 3. 현재 구조 (실측)

```
docs/
├── 00_governance/         ARCHITECTURE_GOVERNANCE.md, GLOSSARY.md (RFC/ADC/ADR 아님 — 절차 정의 문서)
├── 01_mvp/                MVP-0002~0052 Observation/Plan (53개)
├── architecture/
│   ├── baseline/          BASELINE.md, STRUCTURE-V1.0-FROZEN.md
│   └── core/              Kernel 수준 RFC-0001~0012, ADC-0001~0012, ADR-0001~0002,
│                          GOVERNANCE-REVIEW-0001~0007, Freeze/Closure/Audit 문서 다수
├── core/
│   └── execution-layer/   Execution Layer 수준 RFC-0001~0005, ADC-0001~0005,
│                          ADR-0001~0002, MVP-0001~0006 artifact-mapping/observation
├── decisions/
│   ├── rfc/               Development HQ 수준 RFC-0001~0006 + RFC_CANDIDATES.md
│   ├── adc/               ADC.md(Jarvis OS/Kernel Open Decision 12건 SSOT) + ADC-0005/0006
│   └── adr/                Development HQ 수준 ADR-0001 + Kernel 수준 ADR-0002~0007
├── governance/
│   ├── adc/               Development HQ 수준 ADC-0001~0004(Stage 채택 등)
│   ├── observations/       OBS-0001~0006 (Governance v2 계층)
│   └── rt/                 RT-0001(Re-evaluation Trigger)
└── research/               Audit/Investigation 산출물(본 문서 포함)
```

RFC/ADC/ADR을 보유한 트리는 **4개**다: `docs/decisions/`,
`docs/governance/`, `docs/architecture/core/`, `docs/core/execution-
layer/`. `docs/00_governance/`는 RFC/ADC/ADR을 갖지 않는 별개 성격의
트리(정책 문서 2건)다.

## 4. History (Git + 문서 내부 사료)

### 4.1 이 구조를 만든 결정 체인

```
RFC-0006(hqs/, core/execution/, docs Taxonomy 정리)
  ↓
ADC-0005(Structure v1 Migration Decision 4건)
  ↓
ADR-0006(Structure v1 Migration Decision 확정) — 실행 커밋 71d4fa7
```

- **RFC-0006 §6.1**(원안, `docs/decisions/rfc/RFC-0006-...md:88-101`)은
  `docs/architecture/core/*` → `docs/architecture/kernel/`을 "명확(1:1)"
  으로 초안에 넣었으나, **후속 ADC-0005/ADR-0006의 최종 "명확 16개"
  목록에는 이 항목이 없다**(§5.2 참조 — 미해결 사실로 기록, 추측하지
  않음).
- **ADC-0005 Decision 2**(`docs/decisions/adc/ADC-0005-...md:74-103`)는
  Migration을 "명확 16개 우선 이동" / "불명확 140개는 후속 ADC로 이연"
  으로 나눴다. **불명확 140개 목록에 `docs/governance/*`(14개),
  `docs/core/execution-layer/*`(27개), `docs/00_governance/*`(2개),
  `docs/01_mvp/*`(53개), `docs/research/*`(44개)가 명시적으로 포함된다.**
- **ADR-0006 §2**(`docs/decisions/adr/ADR-0006-...md:57-59, 94`)이 이
  결정을 확정: "후속 ADC 예고: §2가 이연한 '불명확 140개' 문서
  taxonomy는 Phase 1·2 완료 후 별도 ADC(가칭 'docs taxonomy Phase 2
  매핑')를 새로 연다. 이 ADR은 그 ADC의 번호나 시점을 지금 확정하지
  않는다."
- 실제 실행은 커밋 `71d4fa7`(Structure v1.0 Migration)이 담당했고,
  `git show 71d4fa7 --stat`으로 확인한 실제 diff는 정확히 "명확 16개"
  범위만 이동했다(`development-hq/` → `hqs/development/`,
  `docs/{01_architecture,02_rfc,03_adc,04_adr}/` → `docs/{architecture/
  baseline, decisions/{rfc,adc,adr}}`). `docs/governance/`, `docs/
  architecture/core/`, `docs/core/execution-layer/`, `docs/00_
  governance/`는 이 커밋에서 손대지 않았다 — 경로가 지금도 그대로다
  (직접 `ls`로 확인, §3).
- **"docs taxonomy Phase 2 매핑" ADC는 지금까지 생성되지 않았다** —
  `docs/decisions/adc/`에 ADC-0005/0006 다음 번호(ADC-0007 이상)가
  없음을 직접 확인(`ls docs/decisions/adc/`). 즉 ADR-0006이 예고한
  후속 정리는 **아직 착수되지 않은 상태**다.

### 4.2 그 사이 이 문제를 이미 다룬 선행 조사 2건

이 병존 문제는 이번 조사가 처음 발견한 것이 아니다 — 저장소 자체가
이미 두 차례 조사했다.

- **`STABILITY-0001-core-architecture.md`**(§2.B, `V-8`): "ADC
  네임스페이스 3개, 번호 중복"을 "Documentation — 문서 내부의 미해소
  상태"로 분류하고 "판단 필요"로 남겼다. 같은 문서 §1.2는 RFC→ADC 대응을
  전수 확인해 **"Open RFC는 1건뿐"**(`docs/decisions/rfc/RFC-0005`, 후속
  ADC 미작성)이라고 판정했다 — 즉 이 시점 기준으로 다른 12개 RFC는
  트리와 무관하게 이미 종결 상태였다.
- **`DOC-TRIAGE-0001.md`**(`docs/architecture/core/`)이 V-8을 이어받아
  **D-7**로 재분류: 분류 **T2(Index/Traceability)**, "Architecture 영향
  없음", 최소 수정 = "`ADC.md` 서두에 범위 한정 문장 1개". **D-6a**(RFC
  네임스페이스 3개, 13건 중 1건만 표에 등록)도 동일 분류, 최소 수정 =
  "표에 위치(네임스페이스) 열 추가 + 나머지 12건 기재".
- **이 두 권고 중 D-7은 이미 실행됐다**: `docs/decisions/adc/ADC.md:5`
  에 정확히 "이 문서는 Jarvis OS(Kernel) 수준 Open Decision(ADC-01~12)만
  다룬다. Development HQ 수준 ADC는 `docs/governance/adc/`, Kernel
  Architecture RFC 후속 ADC는 `docs/architecture/core/`, Execution
  Layer 수준 ADC는 `docs/core/execution-layer/`에 각각 별도로 등록되어
  있다(`DOC-TRIAGE-0001` D-7)."라는 문장이 존재한다(직접 확인).
  `docs/decisions/rfc/README.md`도 동일하게 "Kernel 수준 RFC는
  `docs/architecture/core/`, Execution Layer 수준 RFC는 `docs/core/
  execution-layer/`에 별도로 등록되어 있다"는 범위 한정 문장을 갖고
  있다.
- **D-6a("13건 전부를 표 하나에, 위치 열과 함께 등록")는 실행되지
  않았다**: `docs/decisions/rfc/README.md`의 "등록된 RFC" 표는 지금도
  Development HQ 수준 RFC-0001~0005(5건)만 나열하며, Kernel 7건·
  Execution Layer 1건은 표에 없고 위 범위 한정 문장으로만 언급된다
  (직접 확인).

## 5. Reference (누가 이 트리들을 참조하는가)

- `CLAUDE.md`(프로젝트 최상위 지시)는 "Governance → `docs/decisions/
  rfc/`, `docs/decisions/adc/`, `docs/decisions/adr/`,
  `docs/governance/`"로 **두 경로를 나란히** 명시한다 — `docs/
  architecture/core/`, `docs/core/execution-layer/`는 CLAUDE.md의
  Context Loading 목록에 없다(별도 항목 "Kernel Architecture 연구 →
  `docs/architecture/core/`"로 분리 언급).
- `HANDOVER.md`는 Kernel Responsibility 근거로 `docs/architecture/
  baseline/BASELINE.md` §11(ADR-0002~0005 인용)을 참조 — ADR-0002~0005는
  `docs/architecture/core/`에 있다.
- `hqs/development/mvp/project_intelligence.py::CATEGORY_PATHS`(T02에서
  경로 정정)는 `obs_documents`/`rt_documents`를 `docs/governance/
  observations`, `docs/governance/rt`로, `adc_documents`를 `docs/
  governance/adc`로 참조한다 — 즉 **Development HQ의 실행 코드 자체가
  `docs/governance/`를 canonical 위치로 실제 소비한다**(T02에서 정정한
  `rfc_documents`/`adr_documents`만 `docs/decisions/`를 가리킨다).
- `docs/decisions/rfc/README.md`·`docs/decisions/adc/README.md`·
  `docs/decisions/adr/README.md` 모두 "이 표는 Development HQ 수준만
  다룬다"는 문장으로 자신의 범위를 스스로 한정하고, 다른 3개 트리의
  존재를 명시적으로 인정한다(§4.2에서 인용).

## 6. 중복 분석

| 대상 | 트리 | 번호 체계 | 실제 중복인가 |
|---|---|---|---|
| RFC | `docs/decisions/rfc/`(Dev HQ, 6건) / `docs/architecture/core/`(Kernel, 12건) / `docs/core/execution-layer/`(Execution Layer, 5건) | 3개 트리 모두 **독립적으로 RFC-0001부터 재시작** | **번호는 중복(동명이인)이나, 각 RFC의 대상 도메인은 겹치지 않는다** — 동일 결정을 두 번 내린 사례는 발견되지 않음 |
| ADC | `docs/decisions/adc/ADC.md`(Jarvis OS/Kernel Open Decision 12건) / `docs/governance/adc/`(Dev HQ, 4건) / `docs/architecture/core/`(Kernel, 12건) | 3개 네임스페이스, 번호 독립 | 동일(도메인별 분리, 내용 중복 아님) |
| ADR | `docs/decisions/adr/`(Dev HQ 1건 + Kernel 6건 혼재) / `docs/architecture/core/`(Kernel 2건) | 부분 혼재 | `docs/decisions/adr/`가 Dev HQ·Kernel을 이미 한 디렉터리에 섞어 담고 있다(ADR-0001은 Dev HQ, ADR-0002~0007은 Kernel) — 이는 RFC/ADC와 다른 패턴이다. `docs/architecture/core/`에도 별도 ADR-0001/0002(Governance/Execution Layer Module Baseline)가 존재해, ADR만은 사실상 **두 곳에 걸쳐 있다** |
| 내용 실질 중복 | — | — | **발견되지 않음.** 어느 RFC/ADC/ADR도 다른 트리의 결정과 상충하거나 같은 질문에 두 번 답한 사례가 없다 — DOC-TRIAGE-0001·STABILITY-0001도 동일하게 결론 |

**핵심 관찰**: "중복"은 **번호 재사용**(각 트리가 1부터 독립 채번)일
뿐, **결정 내용의 중복이나 충돌**이 아니다. 이는 `docs/governance/
README.md`가 이미 명시한 원칙("번호는 문서 종류별로 독립적으로
증가한다")과 일치하며, 다만 그 문서가 예상한 것은 "RFC/ADC/RT/ADR"
간의 종류별 독립 채번이었고, **"같은 종류(RFC)가 여러 도메인 트리에서
각각 독립 채번되는 것"까지는 명시적으로 예고하지 않았다** — 이 부분이
실제 혼동의 근원이다.

## 7. Canonical 위치 판단 (Evidence 있는 것만)

| 도메인 | Canonical 위치 | 근거 |
|---|---|---|
| Development HQ 수준 RFC/ADR(신규, Structure v1 이후) | `docs/decisions/{rfc,adr}/` | RFC-0006/ADC-0005/ADR-0006이 명시적으로 이곳을 Target으로 결정·실행(커밋 `71d4fa7`) |
| Development HQ 수준 ADC(신규, Jarvis OS/Kernel Open Decision) | `docs/decisions/adc/ADC.md` | 동일 근거 + `docs/decisions/adc/README.md`가 SSOT로 자기 선언 |
| Development HQ 수준 ADC(구, Stage 채택 등 ADC-0001~0004) | `docs/governance/adc/` | ADR-0006이 "불명확"으로 분류해 **이연**했다 — 이동하지 않기로 확정한 것이 아니라 **아직 판단하지 않은 상태**. 다만 `project_intelligence.py`(실행 코드)와 `docs/decisions/adc/ADC.md:5`(문서)가 모두 이 경로를 실제 참조 대상으로 인정하고 있어, **사실상(de facto) canonical**이지만 **공식(de jure) canonical로 ADR이 확정한 적은 없다** |
| Kernel 수준 RFC/ADC/ADR | `docs/architecture/core/` | RFC-0006 §6.1 원안은 `docs/architecture/kernel/`로 이동을 "명확"이라 봤으나, ADC-0005/ADR-0006 최종본에는 이 항목이 없다 — 즉 **이동 결정 자체가 내려진 적이 없다.** 현재 위치가 Canonical이라는 근거는 "아무도 다른 곳으로 옮기기로 결정한 적이 없다"는 소극적 사실뿐이다 |
| Execution Layer 수준 RFC/ADC/ADR | `docs/core/execution-layer/` | 동일 — ADC-0005 "불명확 140개"에 포함되어 이연됐을 뿐, 별도 이동 결정은 없다 |
| 정책/용어 문서(RFC/ADC/ADR 아님) | `docs/00_governance/` | ADR-0006이 "Target에 대응 위치가 아예 없음"으로 명시 — Canonical 위치가 **아직 존재하지 않는다** |

**결론**: 4개 RFC/ADC/ADR 트리 중 **`docs/decisions/`만 명시적 ADR로
확정된 Canonical 위치**다. 나머지 3개(`docs/governance/`, `docs/
architecture/core/`, `docs/core/execution-layer/`)는 "아직 다른 곳으로
옮기기로 결정되지 않았다"는 소극적 근거로만 현재 위치에 남아 있다 —
이는 §8 판정에서 B(Migration Residue)의 핵심 근거다.

## 8. 최종 판정

### B. Migration Residue (주 판정) + 부분적으로 A로 완화됨(DOC-TRIAGE-0001에 의해)

- **1차 원인(B)**: Structure v1 Migration(RFC-0006 → ADC-0005 →
  ADR-0006)이 명시적으로 "명확 16개만 우선 이동, 나머지 140개는 후속
  ADC로 이연"이라고 결정했고, 그 후속 ADC("docs taxonomy Phase 2
  매핑")는 지금까지 생성되지 않았다. `docs/governance/`, `docs/
  architecture/core/`, `docs/core/execution-layer/`, `docs/00_
  governance/`가 여전히 옛 위치에 남아 있는 것은 **의도적으로 완결된
  설계가 아니라, 스스로 예고했던 후속 절차가 아직 실행되지 않은
  상태**다.
- **완화 요인**: 그렇다고 이 잔존이 방치된 것은 아니다.
  `STABILITY-0001`(V-8)과 `DOC-TRIAGE-0001`(D-6a, D-7)이 이미 이 정확한
  문제를 조사해 "Architecture 영향 없음, Index/Traceability 문제"로
  판정했고, 그 최소 권고(범위 한정 문장 추가)의 **일부(D-7)는 이미
  실행**되어 현재 `docs/decisions/adc/ADC.md`, `docs/decisions/rfc/
  README.md`가 스스로 다른 트리의 존재를 밝히고 있다. 즉 순수한 방치
  (C: Duplicate/Ambiguous로 격하되는 상태)는 아니고, **"물리적 이동은
  미완료이나 문서적 상호 참조로 이미 부분 정리된 Migration Residue"**
  라는 중간 상태다.
- **A(Intentional Multi-Tree)로 완전히 분류하지 않는 이유**: RFC-0006이
  원래 Kernel 트리(`docs/architecture/core/` → `docs/architecture/
  kernel/`)를 "명확" 이동 대상으로 제안했었다는 사실(§4.1) 자체가, 이
  구조가 "처음부터 의도된 최종 설계"가 아니라 "이동이 논의되다 결정
  없이 멈춘 상태"임을 보여준다. 완전한 Intentional Design이라면 애초에
  그런 이동 제안이 나오지 않았거나, 나왔다면 명시적으로 Reject됐어야
  한다 — 그런 Reject 결정은 어디에도 없다.

**요약**: B가 근본 원인이고, DOC-TRIAGE-0001의 사후 조치가 그 위에
A에 가까운 안정 상태(도메인별 분리가 실제로는 합리적이고, 상호 참조로
이미 부분 문서화됨)를 만들어 놓았다. C(순수 모호/중복)와 D(원인
불명)는 근거로 배제한다 — 원인 체인(RFC-0006 → ADC-0005 → ADR-0006 →
미착수 후속 ADC → STABILITY-0001/DOC-TRIAGE-0001의 사후 진단)이 Git
History와 문서 내용만으로 명확히 추적됐다.

## 9. Open Issues

1. `docs/architecture/core/*` → `docs/architecture/kernel/` 이동이
   RFC-0006 원안(§6.1)에서 "명확"으로 제안됐다가 ADC-0005/ADR-0006
   최종본에서 아무 설명 없이 빠진 이유 — **D. Undetermined**(왜
   빠졌는지 설명하는 문서를 찾지 못함, 추측하지 않는다).
2. ADR-0006이 예고한 "docs taxonomy Phase 2 매핑" ADC — 아직 생성되지
   않음. 이 ADC가 열릴 조건은 ADR-0006 §2가 이미 정의했다("Phase 1·2
   완료 + `pytest --ignore=archive` 전체 통과 안정 상태"), 그 조건 충족
   여부는 이번 조사 범위 밖.
3. `docs/decisions/adr/`가 Development HQ·Kernel ADR을 한 디렉터리에
   혼재시키는 것과 달리 `docs/architecture/core/`도 별도 ADR 2건을
   갖는 비대칭 — DOC-TRIAGE-0001 D-8이 이미 지적("Governance·Execution
   Layer Module의 ADR 2건 미작성")했으나 근본 구조 비대칭 자체는 별도
   판단 대상으로 남아 있다.
4. `docs/decisions/rfc/README.md`의 "등록된 RFC" 표가 DOC-TRIAGE-0001
   D-6a 권고(13건 전부 + 위치 열)를 아직 반영하지 않음 — 실행 가능한
   최소 수정이나, 이번 조사는 문서를 고치지 않는다(범위 밖).

## 10. Recommendations

(구현 아님 — 기록만)

1. ADR-0006이 예고한 "docs taxonomy Phase 2 매핑" ADC를, 그 ADR이
   정의한 착수 조건(Phase 1·2 완료 + 전체 테스트 통과 안정 상태) 충족
   여부부터 확인한 뒤 여는 것을 검토.
2. `docs/decisions/rfc/README.md`의 RFC 등록 표에 DOC-TRIAGE-0001
   D-6a가 권고한 "위치(네임스페이스)" 열을 추가하고 13건 전부를
   등록하는 것을 검토(최소 편집 1파일).
3. `docs/architecture/core/*` → `docs/architecture/kernel/` 이동이
   ADC-0005/ADR-0006에서 왜 빠졌는지, 남아 있는 세션 기록(있다면)을
   확인해 명시적 Reject였는지 단순 누락이었는지 규명할지 판단.
4. 4개 RFC/ADC/ADR 트리 각각의 "도메인 소유자"(Dev HQ / Kernel /
   Execution Layer / Jarvis OS 전체)를 명시하는 상위 인덱스 문서 1개가
   필요한지 검토 — 현재는 이 정보가 여러 README에 분산되어 있다.

## 11. v2.0에서의 의미

Development HQ v2.0 Productionization 관점에서 이 트리 병존은
**Architecture나 Contract를 막지 않는다** — STABILITY-0001·DOC-
TRIAGE-0001·본 조사 모두 동일하게 "Architecture 영향 없음"으로
판정했다. 다만 신규 기여자(또는 v2.0 구현 세션)가 "새 RFC를 어디에
써야 하는가"를 판단할 때 참조할 단일 진입점이 아직 없다는 점은 실무
효율의 문제로 남는다.

---

## 최종 보고

1. **무엇을 조사했는가** — `docs/00_governance/`, `docs/decisions/`,
   `docs/governance/`, `docs/architecture/{baseline,core}/`, `docs/
   core/execution-layer/` 5개 트리의 생성 목적·시점·현재 사용 여부·
   Migration 이력·상호 참조·Canonical 근거를 실제 파일과 Git History
   (RFC-0006/ADC-0005/ADR-0006, 커밋 `71d4fa7`), 그리고 이 문제를
   이미 다룬 두 선행 문서(STABILITY-0001, DOC-TRIAGE-0001)로 대조했다.
2. **왜 여러 트리가 존재하는가** — Structure v1 Migration이 "명확
   16개"만 우선 이동하고 나머지(`docs/governance/`,
   `docs/architecture/core/`, `docs/core/execution-layer/`,
   `docs/00_governance/`)는 "불명확"으로 분류해 후속 ADC로 미뤘는데,
   그 후속 ADC가 아직 열리지 않았기 때문이다(Migration Residue). 다만
   그 사이 두 선행 문서가 이 상태를 조사해 "Architecture 영향 없음"
   으로 확인하고 최소 상호 참조 문구를 일부 추가해 실무적 혼란을
   줄여 놓았다.
3. **Canonical 위치는 무엇인가** — `docs/decisions/{rfc,adc,adr}/`만
   ADR로 명시적으로 확정된 Canonical이다. 나머지 3개 RFC/ADC/ADR
   트리는 "아직 옮기기로 결정되지 않아 남아 있는" 상태이며, 실행
   코드(`project_intelligence.py`)와 여러 README가 사실상 그 위치를
   계속 참조하고 있어 사실상(de facto)의 위치로는 안정적이다.
4. **정리가 필요한가** — Architecture/Contract 차원에서는 불필요(모든
   선행 조사가 동일 결론). 실무 색인 차원에서는 §10의 정리(RFC 등록
   표 확장, Phase 2 ADC 착수 조건 확인)가 권장되나 이번 조사는 실행하지
   않는다.
5. **무엇이 불확실한가** — `docs/architecture/core/*`의 Kernel 이동
   제안이 ADC-0005/ADR-0006에서 왜 소리 없이 빠졌는지는 Evidence로
   확정하지 못했다(D. Undetermined, §9-1).
6. **v2.0에서의 의미** — 이 병존은 v2.0 Productionization의 차단
   요인이 아니다. 다만 다음 RFC를 쓸 때 "어디에 쓸 것인가"를 스스로
   판단해야 하는 실무 비용이 남아 있다.

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NONE
Documentation Change: NO (본 조사 결과 문서 1건 신규 생성 외 기존 문서 수정 없음)
Tests: N/A
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: §10-2 — `docs/decisions/rfc/README.md`의
RFC 등록 표에 DOC-TRIAGE-0001 D-6a가 권고한 "위치" 열을 추가하고 13건
전부를 등록. 근거: 이미 다른 두 문서(STABILITY-0001, DOC-TRIAGE-0001)가
이 정확한 수정을 권고했고 편집 범위가 파일 1개·표 1개로 가장 작다.
