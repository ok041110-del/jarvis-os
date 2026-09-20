# RFC/ADC/ADR 식별자 통일 가능성 조사 — Issue #206

**문서 성격**: READ-ONLY 조사. 문서 이동/삭제/파일명 변경, ADR Decision
내용 수정, Open Decision 상태 변경을 하지 않는다. 조사 결과 근거가
부족한 통합은 실행하지 않고 Unresolved로 남긴다.

## 1. 배경 및 목적

Issue #206은 "동일한 의사결정 건이 RFC → ADC → ADR로 이어질 때 동일한
숫자를 쓰도록 정비"할 것을 요청한다(예시 형식: `RFC-02 → ADC-02 →
ADR-02`). 본 문서는 이 통합이 실제로 근거를 가지고 안전하게 수행 가능한지
Evidence 기반으로 조사한 결과를 기록한다.

이 질문은 처음이 아니다 — `docs/architecture/core/STABILITY-0001-core-
architecture.md`(V-8), `docs/architecture/core/DOC-TRIAGE-0001.md`
(D-6a/D-7), `docs/research/DEV-HQ-V2.0-GOVERNANCE-TREE-
INVESTIGATION-0001.md`(§6~§10)가 이미 "RFC/ADC/ADR 트리 간 번호
재사용" 문제를 조사했다. 선행 조사들의 결론은 **"번호는 중복(동명이인)
이나 결정 내용의 중복은 아니며, Architecture 영향이 없는 Index/
Traceability 문제"**(B. Migration Residue)였고, 권고 사항은 renumbering이
아니라 README에 범위 한정·위치(namespace) 정보를 추가하는 것이었다.
본 조사는 이 선행 결론을 재확인하고, "RFC=ADC=ADR 동일 번호" 요청이
이 결론과 구체적으로 어떻게 충돌하는지 새로 검증한다.

## 2. 조사 범위

| 트리 | 경로 | 문서 수(RFC/ADC/ADR) |
|---|---|---|
| Development HQ | `docs/decisions/rfc/`, `docs/decisions/adc/`, `docs/governance/adc/`, `docs/decisions/adr/` | RFC 6 / ADC 2+9(governance) / ADR 11 |
| Kernel | `docs/architecture/core/` | RFC 44 / ADC 46 / ADR 28 |
| Execution Layer | `docs/core/execution-layer/` | RFC 5 / ADC 5 / ADR 2 |

추가로 `docs/decisions/adc/ADC.md`(Jarvis OS/Kernel Open Decision
Register, OD 형식은 아니고 ADC-01~12 자체 등록부), Open Decision 관련
파일(`OD-` prefix)을 검색했으나 저장소 어디에도 `OD-XXXX` 형식 문서는
아직 존재하지 않는다(신규 Open Decision Register 템플릿은 PR #207,
아직 미병합).

## 3. 제목·파일명 일치 검증 (조사 범위 4.1-1~3)

6개 경로의 모든 `RFC-*.md` / `ADC-*.md` / `ADR-*.md` 파일에 대해
"파일명의 ID"와 "파일 최상위 `#` 제목의 ID"를 스크립트로 전수 비교했다.

```
docs/decisions/{rfc,adc,adr}/, docs/governance/adc/ → 불일치 0건
docs/architecture/core/, docs/core/execution-layer/ → 불일치 0건
```

**결론**: 문서 내부 제목과 파일명 간 불일치는 발견되지 않았다. 이번
조사 대상 전체(약 141개 RFC/ADC/ADR 파일)에서 제목 수정이 필요한
사례는 없다.

## 4. RFC → ADC → ADR 연결 관계 조사 (조사 범위 4.1-2, 4.1-5)

각 파일의 명시적 교차 참조 필드("관련 RFC", "관련 ADC", "Context",
"RFC-000X 후속" 등, 파일명 유사도가 아닌 본문 내 명시 문구만 근거로
채택)를 확인했다.

### 4.1 Kernel 트리 (`docs/architecture/core/`)

- RFC-0001~0020 구간은 ADC 번호와 대체로 일치한다(예: `ADC-0002: Kernel
  Definition 채택 판단 (RFC-0002 후속)`).
- RFC-0021 이후 번호가 어긋난다 — `ADR-0011`은 `관련 RFC: RFC-0021 |
  관련 ADC: ADC-0022`, `ADR-0019`는 `관련 RFC: RFC-0031 | 관련 ADC:
  ADC-0034`로 명시한다. 오프셋이 문서가 늘어날수록 커진다.
- **ADR 번호는 RFC/ADC와 독립된 별도의 순차 채번**이다. 예:
  `ADR-0002`(Execution Layer Module Baseline)는 `ADC-0001 Module 4`의
  결과이며, `ADR-0003`(Kernel Context Model)은 `ADC-0013`/`RFC-0013`의
  결과다. 즉 "ADR-000X"라는 번호 자체가 "RFC/ADC-000X"와 같은 결정을
  의미하지 않는다 — 파일이 스스로 이 사실을 다음과 같이 명시한다:
  `ID | docs/architecture/core/ADR-0002 (docs/04_adr/ADR-0002 core-to-
  kernel-terminology-unification과 다른 문서 — 네임스페이스로 구분)`.

### 4.2 Execution Layer 트리 (`docs/core/execution-layer/`)

- RFC-0001~0005 ↔ ADC-0001~0005는 1:1로 일치(`ADC-0003: Execution
  Result Item Schema (RFC-0003 후속)` 등, 명시적 헤더로 확인).
- ADR은 별도 순차 채번: `RFC-0002/ADC-0002 → ADR-0001`
  (`"ADC-0002-execution-result-contract.md → ADR-0001-execution-
  result-contract.md로 종결됨"`), `RFC-0003/ADC-0003 → ADR-0002`.
  5개 ADC 중 2개만 ADR로 이어졌고, 이어진 ADR 번호는 RFC/ADC 번호와
  다르다(오프셋 -1/-2).

### 4.3 Development HQ 트리 (3개 하위 네임스페이스)

- `docs/decisions/rfc/` RFC-0001~0004 ↔ `docs/governance/adc/`
  ADC-0001~0004는 일치(`ADC-0002: Task Dispatcher 승격 재판단
  (RFC-0002 후속)`).
- 이후 어긋난다 — `docs/governance/adc/ADC-0005`는 **RFC-0007**의
  후속(`"# ADC-0005: AST 기반 Context 자동 추출 Production 통합 판단
  (RFC-0007 후속)"`), ADC-0006→RFC-0008, ADC-0007→RFC-0009,
  ADC-0008→RFC-0010, ADC-0009→RFC-0011.
- `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md`는
  **RFC-0006**의 후속(`"# ADC-0005: Structure v1.0 Migration —
  RFC-0006 후속 Decision 4건"`, 번호 오프셋 -1).
- **RFC-0006 하나가 ADC 2건(`ADC-0005-structure-v1-migration-
  decisions.md`, `ADC-0006-baseline-relocation-decision.md`)과 ADR
  2건(`ADR-0006-structure-v1-migration.md`,
  `ADR-0007-baseline-relocation.md`)으로 분기(fan-out)한다** — 이는
  §5의 "1:1 강제 renumbering 불가" 판단의 핵심 근거다.
- `docs/decisions/adr/ADR-0001`은 `ADC-0003`(governance 트리)의
  결과이며 `docs/decisions/adr/ADR-0006`은 `ADC-0005`(decisions 트리)
  + `RFC-0006`의 결과다.

## 5. 통합(Unification) 가능성 판정

### 5.1 판정 기준 (Issue #206 §3.1 적용)

각 후보 쌍에 대해 5개 판단 기준(동일 문제/Decision Question, 동일
Architecture 범위, 명시적 Related Document 연결, RFC→ADC→ADR 흐름,
제목·본문 동일 대상 여부)을 적용했다.

### 5.2 근거 요약 (트리별)

| 트리 | RFC=ADC 번호 일치 | RFC/ADC=ADR 번호 일치 | 구조적 장애 |
|---|---|---|---|
| Kernel | 0001~0020 구간만 부분 일치, 0021+ 불일치 | 전 구간 불일치(ADR은 독립 순차 채번) | ADR이 여러 ADC를 순서대로 소비 — 1:1 강제 시 기존 ADR 40여 건 재번호 필요 |
| Execution Layer | 0001~0005 전부 일치 | 불일치(ADR 2건만 존재, 오프셋 -1/-2) | ADC 5건 중 2건만 ADR로 귀결 — "ADR 없음"인 ADC에 번호를 맞출 대상이 없음 |
| Development HQ | 0001~0004만 일치, 이후 불일치 | 불일치 + **1 RFC → 2 ADC → 2 ADR 분기 사례 확인**(RFC-0006) | 분기 사례는 애초에 "RFC-06=ADC-06=ADR-06" 단일 번호로 표현 불가능 |

### 5.3 결론: **전면적 식별자 통일은 근거 미충족으로 실행하지 않는다**

- **구조적 이유**: ADR 채번은 3개 트리 전부에서 "해당 ADC/RFC와 같은
  번호"가 아니라 "ADR이 작성된 순서"로 독립 증가하도록 이미 설계되어
  있다(Kernel 트리 40여 건, Execution Layer 2건, Dev HQ 11건 모두
  일관되게 이 패턴을 보임 — 예외 없음). 이는 우연한 실수가 아니라
  일관된 컨벤션이다.
- **1:N 분기 사례**: Development HQ RFC-0006이 ADC 2건·ADR 2건으로
  분기하는 것이 확인됐다(§4.3). 하나의 RFC가 여러 ADC/ADR로 나뉘는
  구조에서는 "RFC-XX = ADC-XX = ADR-XX" 형태의 단일 번호 매핑이 정의상
  불가능하다 — 강제로 번호를 맞추려면 ADC/ADR 중 하나를 골라 나머지를
  포기해야 하며, 이는 Issue #206 §3.1 "최소한 하나의 근거만으로
  통합하지 않는다"는 원칙과 §7 "근거 없는 식별자 변경 금지"에 저촉된다.
- **선행 Governance 결론과의 정합성**: `DEV-HQ-V2.0-GOVERNANCE-TREE-
  INVESTIGATION-0001.md` §8은 이미 이 상태를 "Architecture 영향 없음,
  Index/Traceability 문제"(B. Migration Residue)로 판정했고, §10
  권고는 renumbering이 아니라 README 범위 한정 문구/위치 열 추가였다.
  본 조사는 이 판정을 재확인했고 이를 뒤집을 새 Evidence를 찾지
  못했다.
- **파일명 변경 대안(4.2절 조건) 검토**: Issue #206 4.2절은 "파일명
  변경이 위험하거나 근거가 부족하면 파일명은 유지하고 제목과 문서 내
  ID만 수정하는 대안"을 요구한다. 그러나 §3에서 확인했듯 제목과 파일명
  ID는 이미 100% 일치하므로 이 대안조차 적용할 대상이 없다 — "제목만
  고치는" 최소 조치도 필요하지 않다.

**따라서 이번 조사에서는 어떤 RFC/ADC/ADR 파일의 번호·파일명·제목도
변경하지 않는다.**

## 6. 번호 충돌(동일 숫자·다른 의사결정 건) 기록 (Issue #206 §3.2)

다음은 "번호는 같지만 다른 결정을 가리키는" 확인된 충돌이다. 이미
저장소 자신이 각 파일 내부에 disambiguation 문구로 인지하고 있다 —
신규 발견이 아니라 기존 상태의 재확인이다.

| 충돌 ID | 위치 A | 위치 B | 위치 C | 비고 |
|---|---|---|---|---|
| RFC-0002 | `docs/decisions/rfc/` Task Dispatcher Boundary | `docs/architecture/core/` Kernel Definition | `docs/core/execution-layer/` Execution Result Contract | 서로 다른 도메인, 내용 중복 아님 |
| ADC-0002 | `docs/governance/adc/` Task Dispatcher 승격 | `docs/architecture/core/` Kernel Definition | `docs/core/execution-layer/` Execution Result Contract | 상동 |
| ADR-0002 | `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md` | `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md` | — | 두 파일 모두 서로를 "네임스페이스로 구분"한다고 본문에 명시 — 이미 self-disambiguated, 추가 조치 불필요 |

리포지토리 전체에서 리터럴 문자열 `RFC-0002`/`ADC-0002`/`ADR-0002`를
참조하는 파일은 각각 40건 이상이며, 대부분 "이전 결정을 인용"하는
정상적 citation chain이다(archive 제외). 위 표에 없는 추가적인
동일번호·동일도메인 충돌(=진짜 오류)은 발견되지 않았다.

## 7. Open Decision Register와의 관계

Issue #206 §5는 Open Decision(OD-XX)이 RFC/ADC/ADR과 별도 식별자
체계를 유지해야 한다고 명시한다. 현재 저장소에는 `OD-XXXX` 형식 문서가
아직 존재하지 않으므로(§2), 이번 조사에서 Open Decision 관련 변경
대상은 없다. `docs/decisions/adc/ADC.md`(ADC-01~12, Jarvis OS/Kernel
Open Decision 목록)는 명칭은 "ADC"이지만 실질적으로 Open Decision
Register 역할을 하는 기존 문서이며, 이번 통합 논의와 번호 체계가
겹치지 않는다(자체 독립 번호 ADC-01~12, 두 자리, 다른 트리의
`ADC-000X`(네 자리)와 형식부터 다르다 — 혼동 가능성 낮음, 별도 조치
불필요로 판단).

## 8. 검증

- **링크 검증**: 이번 조사는 어떤 파일도 이동/수정하지 않았으므로 기존
  링크는 전부 그대로 유효하다(변경 전 상태 = 변경 후 상태).
- **식별자 충돌 검증**: §6에서 확인한 충돌은 모두 기존 파일이 자체
  disambiguation 문구를 이미 보유하고 있음을 확인했다(신규 충돌 없음).
- **제목/파일명 일치 검증**: §3, 전수 검사 스크립트로 불일치 0건 확인.
- **변경 범위 검증**: `git status`/`git diff` 상 본 조사 문서 1개 신규
  추가 외 기존 문서 변경 없음(§9 커밋 참조).
- **테스트**: 코드 변경이 없으므로 해당 없음(N/A).

## 9. 최종 판단

| 항목 | 판단 |
|---|---|
| RFC=ADC=ADR 전면 통일 | **실행하지 않음** — 구조적으로 최소 1건(RFC-0006) 이상이 1:N 분기이며, ADR 채번이 3개 트리 전부에서 독립 순차 채번으로 설계되어 있어 강제 통일 시 근거 없는 대량 재번호(Kernel 40여 건 포함)가 필요 |
| 제목·파일명 수정 | **불필요** — 불일치 없음(전수 확인) |
| 파일명 변경(`git mv`) | **수행하지 않음** — 통합 ID가 확정되지 않아 4.2절 선행 조건 미충족 |
| 번호 충돌 기록 | **완료**(§6) — 기존에 이미 각 파일이 self-disambiguate 중, 추가 조치 불필요 |
| Open Decision 연계 | **해당 없음** — OD 문서 미존재 |
| Architecture/Contract 내용 | **변경 없음** |

## Architecture / Public Contract 영향

- Architecture 변경: 없음
- Public Contract 변경: 없음
- 본 조사로 인한 기존 문서 수정: 없음(신규 조사 문서 1건만 추가)

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Investigation | `docs/architecture/core/STABILITY-0001-core-architecture.md` §1.2, V-8 | 선행 조사 — 번호 재사용 최초 지적 |
| Investigation | `docs/architecture/core/DOC-TRIAGE-0001.md` D-6a/D-7 | 선행 조사 — Index/Traceability 분류, README 최소 수정 권고 |
| Investigation | `docs/research/DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001.md` §6~§10 | 선행 조사 — "B. Migration Residue" 최종 판정, renumbering 비권고 |
| Issue | #206 | 본 조사가 응답하는 요청 |
| PR | #207 | RFC/ADC/ADR/Open Decision 템플릿 구조 통합(별도 작업, 병합 대기 중) |

## Open Issues (해결하지 않음, 기록만)

1. Kernel 트리 RFC-0021 이후 RFC↔ADC 번호 오프셋이 왜 발생했는지(의도적
   재편인지 단순 누락인지)는 이번 조사 범위 밖 — 근거 문서를 찾지
   못해 Undetermined로 남긴다.
2. `docs/decisions/rfc/README.md`가 이미 3개 트리 전체(24건)를 위치
   열과 함께 등록한 것과 달리, `docs/decisions/adr/README.md`·
   `docs/decisions/adc/README.md`는 같은 수준의 전수 등록 표를 갖고
   있지 않다 — 필요성이 있다면 별도 문서 전용 작업(이번 Issue #206
   범위 밖, renumbering이 아닌 순수 추가 편집)으로 검토 가능.
