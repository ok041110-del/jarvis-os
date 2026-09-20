# ADC-0010: RFC·ADC·ADR 통합 식별자 체계 도입 여부 판단 (Issue #206 후속)

## 목적

Issue #206이 요청한 "RFC·ADC·ADR을 의사결정 단위로 추적 가능하게 하는
통합 식별자 체계" 설계를 판단한다. 선행 근거는
`docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`
(PR #208, 병합 대기 중)이며, 이 ADC는 그 조사 결과를 그대로 인용하고
새로 재조사하지 않는다.

이 ADC는 별도 선행 RFC 없이 Issue #206의 직접 요청으로 연다 —
`ADR-0008`(Architecture Owner 직접 지시, ADC 경유 없음)과 같은 성격의
선례이며, 대상이 Kernel Boundary가 아니라 **문서 식별자 체계라는
Governance 절차 자체**이므로 RFC의 전통적 대상(Boundary Question)에
해당하지 않는다.

**판단 대상에서 제외**: 기존 RFC/ADC/ADR 파일의 재번호화·이름
변경·내용 수정, Architecture Baseline 소급 수정, PR #207 템플릿의
임의 변경, ADR 신규 생성(이 ADC는 규칙만 확정하며 Baseline 반영은
후속 ADR 대상).

---

## 사전 조사 요약 (전체 근거는 investigation 문서 참조)

| 항목 | 결과 |
|---|---|
| RFC/ADC/ADR 전체 문서·파일명 | 3개 트리(Dev HQ/Kernel/Execution Layer), 약 141개 파일, 제목-파일명 불일치 0건 |
| 명시적 링크 | 각 파일이 "RFC-000X 후속" 등 본문 인용으로 연결 — 파일명 유사도 추정 아님 |
| **1 RFC → 다수 ADC/ADR 분기(fan-out)** | 확인됨 — Dev HQ RFC-0006 → ADC-0005+ADC-0006 → ADR-0006+ADR-0007 |
| **다수 RFC → 1 ADC 집약(fan-in)** | 확인됨 — Kernel RFC-0024~0030 → ADC-0032/ADC-0033 |
| **1 ADC 내 부분 종결(partial closure)** | 확인됨 — `docs/decisions/adr/ADR-0001`은 `docs/governance/adc/ADC-0003.md`의 "판단 1"만 종결(ADC-0003의 다른 판단 항목은 별도) |
| 이미 결정된 문서 / 미결정 문서 | Kernel RFC-0005(Dev HQ 트리), Execution Layer RFC-0005/ADC-0005가 Open. 나머지는 Resolved(Not Accepted 포함) |
| ADR의 채번 방식 | 3개 트리 전부에서 RFC/ADC 번호와 무관하게 **작성 순서로 독립 증가** — 우연이 아니라 일관된 컨벤션(예외 없음) |
| 기존 번호·링크 의존성 | `docs/decisions/{rfc,adc,adr}/README.md`, `docs/decisions/adc/ADC.md`, 다수 ADR의 "관련 ADC/RFC" 필드, `hqs/development/mvp/project_intelligence.py`(실행 코드)가 현재 경로·번호를 실제로 참조 |
| 관련 Governance 문서 | `docs/governance/README.md`("번호는 문서 종류별로 독립적으로 증가한다"), `STABILITY-0001` V-8, `DOC-TRIAGE-0001` D-6a/D-7, `DEV-HQ-V2.0-GOVERNANCE-TREE-INVESTIGATION-0001` §6~§10(B. Migration Residue, renumbering 비권고) |

**핵심 결론(재확인)**: RFC=ADC=ADR 단일 번호 강제는 fan-out·fan-in·
partial-closure 세 가지 실제 관측 패턴과 구조적으로 양립 불가능하다.
따라서 "번호를 맞추는" 접근이 아니라 "관계를 명시적으로 기록하는"
접근이 필요하다 — 이것이 아래 판단의 전제다.

---

## 판단 1. 식별자 체계 후보 비교

### Evidence

위 표의 fan-out/fan-in/partial-closure 3개 실증 사례. 세 후보 모두
이 사례들을 표현할 수 있어야 실전에서 유효하다.

### Options

| 기준 | 후보 A: 단순 공통 번호 (`RFC-006`/`ADC-006`/`ADR-006`) | 후보 B: 분기 접미사 (`ADC-006-A`/`ADR-006-A`) | 후보 C: Decision Group + 점 표기 (`D-006`/`ADC-006.1`/`ADR-006.1`) |
|---|---|---|---|
| 가시성 | 높음(번호만 봐도 연결 인지) | 중간(접미사 의미 학습 필요) | 중간(Group ID 별도 조회 필요하나 명시적) |
| 추적성 | 낮음 — fan-out/fan-in 발생 시 번호 하나로 표현 불가 | 중간 — 분기는 표현되나 fan-in(다수 RFC→1 ADC)의 접미사 소속이 모호 | 높음 — Group이 N:M 관계를 그대로 수용 |
| 분기 결정 지원 | 지원 안 됨(구조적 불가) | 부분 지원(1:N만, N:1은 불명확) | 지원(1:N, N:1, partial-closure 모두 Group 하위 항목으로 표현 가능) |
| Open Decision 지원 | 없음(RFC/ADC/ADR과 별도 체계 요구 — Issue #206 §5) | 없음(동일) | Group ID를 Open Decision에도 선택적으로 부여 가능(단, OD 고유 번호는 유지 — Issue #206 §5 "OD ID를 RFC·ADC·ADR 번호와 동일하게 변경하지 않는다"와 합치) |
| 기존 문서와의 호환성 | **불가** — 기존 141개 문서 전체 재번호 필요, 근거 없는 대량 변경(Issue #206 §7 금지 사항 위반) | 낮음 — 기존 파일에 접미사를 소급 부여하려면 파일명 변경 필요 | **높음** — 기존 파일명·ID 변경 없이 신규 Registry 문서로 병기 가능 |
| 파일명·링크 변경 범위 | 전체(141개 파일 + 모든 참조) | 부분적이나 여전히 광범위(분기 이력이 있는 모든 문서) | **0**(신규 Registry 1개 문서 추가만, 기존 파일 무변경) |
| 장기 유지보수성 | 낮음(신규 fan-out 발생 시마다 재번호 반복 필요) | 중간(접미사 조합 폭발 가능성 — `-A-1` 등 중첩) | 높음(Group Registry에 행 추가만으로 확장) |
| Governance 적용 난이도 | 매우 높음(전면 재번호 = 사실상 새 RFC→ADC→ADR 대량 재작업) | 높음(소급 적용 시 링크 전수 갱신 필요) | 낮음(추가 전용, 기존 절차와 충돌 없음) |

### Constraint / Boundary

- Issue #206 §7: 사전 승인 없는 전체 재번호화, 기존 링크 일괄 변경,
  Architecture Baseline 소급 수정 금지.
- Issue #206 §4: "기존 번호를 보존하면서 통합 식별자를 병기할 수
  있는가?"를 반드시 검토해야 한다 — 이는 후보 A/B가 구조적으로 만족
  못 하는 조건이다.

### Recommendation

**후보 C를 기반으로 하되, 파일명에 점(`.`) 표기를 소급 적용하지 않고
별도 Registry 문서로 구현한다** (아래 "권장안" 참조). 후보 A는 실제
관측된 fan-out/fan-in을 표현할 수 없어 채택 불가. 후보 B는 fan-in과
중첩 분기(분기의 분기) 표현이 불명확하고, 소급 적용 시 파일명 변경이
불가피해 Issue #206 §7 위반 위험이 크다.

### Final Judgment

**Scoped Accept — 후보 C의 "논리적 그룹" 개념만 채택하고, 표기법은
기존 파일에 직접 반영하지 않는다.** 상세는 아래 "권장안"에 기술한다.

---

## 권장안: Decision Group Registry (추가 전용, 비파괴적)

### 설계

- **Decision Group ID**: `DG-NNNN` 형식의 새로운 전역 순차 번호.
  RFC/ADC/ADR/OD 어느 것과도 번호 체계를 공유하지 않는 완전히 독립된
  네임스페이스다 — 기존 141개 문서의 어떤 번호와도 충돌하지 않는다.
- **Decision Group Registry**: 신규 문서 1개
  (`docs/governance/DECISION-GROUP-REGISTRY.md`, 이번 ADC는 이 문서를
  생성하지 않고 후속 구현 작업으로만 지정한다 — §"후속 구현 작업"
  참조)가 각 `DG-NNNN`에 대해 다음을 기록한다.

  | Field | 설명 |
  |---|---|
  | DG ID | `DG-0001` 등 |
  | Title | 의사결정 주제 |
  | Domain | Development HQ / Kernel / Execution Layer |
  | Member RFCs | 기존 RFC 파일 경로 목록(0개 이상, 변경 없이 그대로 인용) |
  | Member ADCs | 기존 ADC 파일 경로 + 해당 시 "판단 N" 하위 식별 |
  | Member ADRs | 기존 ADR 파일 경로 + 해당 시 "판단 N" 하위 식별 |
  | Status | Open / Partially Resolved / Resolved / Superseded |
  | Evidence | 그룹으로 묶는 근거(명시적 본문 인용) |

- **기존 파일은 전혀 수정하지 않는다.** Registry는 순수 색인이며,
  기존 RFC/ADC/ADR 파일의 제목·ID·본문·링크는 그대로 둔다.
- 신규 문서(향후 새로 작성되는 RFC/ADC/ADR)는 **선택적으로** Identity
  & Status 표 또는 Related Documents 표(PR #207 템플릿 기준)에
  `Decision Group: DG-NNNN` 필드를 추가할 수 있다 — 필수는 아니며,
  fan-out/fan-in이 실제로 발생하는 경우에만 부여한다.

### 판단 2. 분기·보류·대체·폐기 규칙

| 상황 | 규칙 |
|---|---|
| RFC 1건 → ADC 여러 건 분기 | 동일 `DG-NNNN`에 모든 ADC를 Member로 등록. ADC 번호는 각자의 트리 규칙(독립 순차 증가)을 그대로 따른다 |
| ADC 1건 → ADR 여러 건(부분 종결) | Member ADR 목록에 "ADC-XXXX 판단 N"처럼 어느 판단 항목을 종결하는지 명시. ADC 전체가 아니라 판단 단위로 Status를 관리한다 |
| ADR 미작성(예약) | Registry의 Member ADR 칸에 "Reserved — 번호 미정"으로 표기하고, 실제 ADR 번호는 그 트리의 독립 채번 규칙에 따라 작성 시점에 확정한다. **번호를 미리 예약하여 확정하지 않는다** — 예약 번호가 다른 결정에 재사용되는 것을 막는 것으로 충분하며(Issue #206 §3.2), 사전 확정은 후속 채번 순서를 왜곡할 수 있다 |
| Deferred/Not Accepted | Status를 "Resolved(Not Accepted)"로 기록. 식별자는 유지 — Issue #206 §7, `docs/governance/README.md`의 Outcome-Oriented Governance Model(Deferred ≠ 영구 금지) 원칙과 합치 |
| 결정 대체(Superseded) | 기존 문서·번호를 삭제하지 않고 Status를 "Superseded by DG-MMMM"으로 갱신. 새 결정은 새 `DG-MMMM`을 발급하며 이전 Group을 재사용하지 않는다 |

### 판단 3. 기존 문서 마이그레이션 전략

**전면 마이그레이션은 수행하지 않는다.** 근거: (1) Issue #206 §7이
사전 승인 없는 전체 재번호화를 명시적으로 금지, (2) 141개 문서 전체를
한 번에 매핑하는 것은 근거 검증 비용이 매우 크고 오류 위험이 큼(1건의
Kernel RFC-0021 이후 오프셋 원인조차 Undetermined로 남아 있음 —
investigation 문서 Open Issues 참조).

대신 **점진적·근거 기반 등록**을 권장한다.

1. 이미 명시적 근거로 확인된 fan-out/fan-in 사례부터 Registry에
   등록한다(예: Dev HQ RFC-0006 그룹, Kernel RFC-0024~0030 그룹) —
   각각 `DG-0001`, `DG-0002`로 시작 가능(정확한 번호는 후속 구현
   작업에서 확정).
2. 나머지 문서는 "Registry 미등록 = 여전히 독립 문서"로 남기며, 강제
   등록 기한을 두지 않는다.
3. 신규 RFC/ADC/ADR을 작성할 때만 필요 시 Decision Group을 새로
   발급한다(아래 판단 4).

### 판단 4. 신규 문서 작성 규칙

- 신규 RFC 작성 시 후속 ADC/ADR이 여러 건으로 분기할 가능성이 미리
  예상되면(예: 하나의 RFC가 여러 독립적인 Boundary Question을 포함),
  작성자는 RFC 본문에 그 사실을 명시하고 Decision Group 발급을
  고려할 수 있다 — 의무는 아니다.
- ADC가 여러 "판단" 항목을 포함하는 기존 관행(예: ADC-0009의 판단
  1·2)은 그대로 유지한다 — 이 ADC는 그 관행을 바꾸지 않는다.
- 신규 ADR 작성 시, 자신이 종결하는 ADC/RFC의 정확한 판단 번호를
  본문에 명시하는 기존 관행(예: `ADR-0001`의 "ADC-0003 판단 1")을
  계속 따른다 — 이것이 이미 사실상 최소한의 추적성 도구로 기능하고
  있음을 investigation 문서가 확인했다.

### 판단 5. Open Decision 처리 방식

Issue #206 §5 원칙을 그대로 수용한다 — Open Decision은 `OD-XX`
독자 번호 체계를 유지하며 RFC/ADC/ADR 번호로 변경하지 않는다.
Decision Group과의 관계는 **선택적 연결**로 한정한다: 어떤 Open
Decision이 특정 `DG-NNNN`에 속한 RFC/ADC와 관련되면 OD 문서의
Related Documents 표(PR #207 Open Decision Register 템플릿 기준)에
`DG-NNNN`을 기재할 수 있으나, OD 자체의 번호나 Architecture Baseline
포함 여부에는 영향을 주지 않는다(Issue #206 §5 제한사항 준수).

---

## 종합 Decision

**Scoped Accept.** 다음 범위로 한정하여 승인한다.

| 대상 | 승인 여부 | 처리 |
|---|---|---|
| 후보 C(Decision Group) 개념 채택 | Accept | 이 ADC로 확정 |
| Decision Group을 파일명 접미사로 소급 반영(후보 B 요소) | Reject | 기존 파일 무변경 원칙 위반 |
| 전면 재번호화(후보 A) | Reject | fan-out/fan-in 구조와 양립 불가, Issue #206 §7 위반 |
| `docs/governance/DECISION-GROUP-REGISTRY.md` 신규 생성 | 이 ADC는 수행하지 않음 | 후속 구현 작업(아래)으로 지정 — 이 ADC는 규칙만 확정 |
| 기존 RFC/ADC/ADR 파일 수정 | 없음 | 이번 작업 범위 밖 |
| Architecture Baseline 반영 | 불필요 | 이 결정은 Governance 절차(문서 색인) 변경이며 Architecture Decision이 아님 — ADR 대상이 아니다(§Architecture 영향 참조) |

이 ADC는 **ADR을 생성하지 않는다** — Registry 신설은 Baseline
변경이 아니라 순수 추가 문서 작업이므로 `docs/governance/README.md`의
"ADR은 ADC에서 Accept/Promote로 판단된 사항을 Baseline 문서 변경
결정으로 기록"하는 정의에 해당하지 않는다. 다만 이 ADC의 결정 자체가
장차 Registry 도입의 근거 문서 역할을 한다.

## Architecture 및 Public Contract 영향

- Architecture 변경: **No** — Kernel/Execution Layer의 어떤 구조·
  Contract도 변경하지 않는다. Decision Group Registry는 순수 문서
  색인이다.
- Public Contract 변경: **No**.
- 이 판단으로 Baseline 문서(BASELINE.md 등) 반영이 필요한 항목: 없음.

## 후속 구현 작업 목록

1. `docs/governance/DECISION-GROUP-REGISTRY.md` 신규 생성(빈 표 +
   위 Field 정의) — 파일 1개, 기존 문서 무변경.
2. 이미 근거가 확인된 2개 그룹(Dev HQ RFC-0006 계열, Kernel
   RFC-0024~0030 계열)을 Registry에 최초 등록.
3. `docs/decisions/{rfc,adc,adr}/README.md`, `docs/governance/README.md`
   "Document Numbering" 절에 Decision Group 존재를 알리는 한 문단
   추가(선택, 이 ADC는 지금 수행하지 않음 — 별도 최소 편집 작업으로
   분리 권장, renumbering 아님).
4. Registry 생성 이후, 신규 RFC/ADC/ADR 작성 가이드(`md-writer`,
   `context-loader` 스킬 또는 관련 SKILL.md)에 "Decision Group 선택적
   기재" 안내를 추가할지 검토(선택).

이 4개 항목 중 어느 것도 이번 ADC가 직접 실행하지 않는다 — Governance
승인 이후 별도 구현 세션에서 순서대로 진행한다.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 이 ADC의 조사 근거(PR #208) |
| Issue | #206 | 이 ADC가 응답하는 요청 |
| PR | #207 | Open Decision Register 템플릿(§판단 5에서 인용, 병합 대기 중) |
| PR | #208 | Investigation 문서(병합 대기 중) |
| Precedent | `ADR-0008-stage-folder-code-and-docs.md` | "Architecture Owner 직접 지시, ADC 경유 없음" 선례 인용 |
| Precedent | `docs/governance/adc/ADC-0009.md` | ADC 문서 형식(판단/Evidence/Options/Recommendation) 참조 |
