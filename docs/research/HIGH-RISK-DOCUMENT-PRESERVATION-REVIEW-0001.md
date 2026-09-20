# HIGH-RISK-DOCUMENT-PRESERVATION-REVIEW-0001

## 0. 목적 및 범위

RFC/ADC/ADR 템플릿 정합성 작업(PR #214)에서 정보 손실 위험 때문에
편집을 보류한 4개 문서에 대해, 실제로 편집을 시작하기 전에 안전한
압축·템플릿 정렬 방법을 설계한다. **이 문서는 검토 보고서이며, 대상
4개 문서 중 어느 것도 수정하지 않는다.**

대상:

1. `docs/architecture/core/RFC-0020-workflow-adapter-contract-and-implementation-boundary.md`
2. `docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md`
3. `docs/architecture/core/ADC-0019-scoped-workflow-graph-execution-boundary.md`
4. `docs/architecture/core/ADR-0011-gate-a-decisions-2-5-11-resolution-baseline.md`

이 검토를 위해 4개 문서 원문 전체를 재확인했고, 각 문서의 Q-번호·절
번호가 **외부에서 실제로 인용되는지**를 `grep`으로 저장소 전체에서
재확인했다(결과는 §4 및 부록에 원본 그대로 인용).

---

## 1. `RFC-0020` — Workflow Adapter Contract와 구현체 경계

### 1.1 현재 구조 및 주요 섹션

213행. `##` 최상위 헤더가 **0개**다 — Status/Author/대상/Evidence를
문서 최상단 볼드체 문단으로 서술한 뒤, 전부 `###` 이하로만 구성된다.

- `### 0.` 이 RFC가 열린 이유
- `### 1.` Context
- `### 2.` Problem(4개 항목)
- `### 3.` Evidence — E1/E2/E3 비교 표
- `### 4.` Alternatives — 4.1 명칭·구현체 경계(N-0~N-3 표), 4.2 Checkpoint 입도(C1~C3 표)
- `### 5.` Proposal — 5.1~5.5(권고안, 결정 아님)
- `### 6.` Consequences
- `### 7.` 명시적으로 범위 밖(표)
- `### 8.` Open Questions — 8.1 ADC-0020 필수 결정 항목(Q-A~Q-F 표), 8.2 이연 항목(Q-G~Q-J 표)
- `### 9.` Traceability — 기존 Governance와의 관계(20행 표)
- `### 10.` Self Review(18개 체크리스트)

### 1.2 안전하게 압축 가능한 내용

- §0("이 RFC가 열린 이유")과 §1(Context)의 서술 일부는 중복 — 둘 다
  "RFC-0019 → ADC-0019 → ADR-0008이 존재만 Accept했다"는 같은 사실을
  반복 서술한다. §1로 통합 가능.
- 최상단 볼드체 Status/Author/대상/Evidence 문단은 표(Identity &
  Status)로 옮길 수 있다 — 내용 손실 없음, 형식만 변경.
- §6(Consequences)의 "명명·계약과 구현 금지는 공존한다"는 설명은
  §7(범위 밖 표)의 두 번째 행과 논지가 겹친다 — 완전히 삭제하지 않고
  요약문 한 줄 + §7 표 참조로 축약 가능.

### 1.3 반드시 verbatim 또는 구조 그대로 유지해야 하는 내용

- **§3 Evidence 표(E1/E2/E3 vs 증명하는 것/증명하지 못하는 것)**:
  후속 ADC-0020·ADC-0021·ADC-0022가 "E1/E2/E3" 명칭과 그 증명 범위를
  그대로 인용한다(§4 근거 참조). 표를 산문으로 풀면 "증명 못하는 것"
  칸의 부정 진술(예: "v2 Reversibility 미검증")이 긍정 진술처럼
  오독될 위험이 있다.
- **§4.1 Alternatives 표(N-0~N-3)와 §4.2(C1~C3)**: `ADC-0020`이 이
  RFC의 N-1/C1 "권고"를 그대로 이어받아 판단했다(§4 근거의
  `RFC-0020` 인용 목록 참조). 후보 식별자(N-1, C1 등) 자체가 외부
  인용 대상이므로 표 구조·라벨을 변경할 수 없다.
- **§8 Open Questions의 Q-A~Q-J**: `ADC-0019` 자신도 §Q-표기 관행을
  쓰고 있고, 이 RFC의 Q-A~Q-F는 ADC-0020이 실제로 하나씩 답한
  질문이다(Governance Chain 재확인 완료 사항, 아래 §4 grep 결과에서
  `ADC-0020`이 이 RFC를 22회 이상 인용). Q-번호를 재부여하거나
  순서를 바꾸면 ADC-0020~0023의 인용이 무엇을 가리키는지 알 수
  없어진다.
- **§9 Traceability 표(20행)**: 이 표 자체가 "어떤 기존 문서를
  이 RFC가 건드리지 않았는지"의 감사 기록이다 — 표를 없애면 그
  감사 기록이 사라진다.
- **§10 Self Review(18개 체크)**: 각 체크 항목이 특정 절(§1·§6·
  §7·§8.1 등)을 인용한다 — 위 섹션들의 절 번호가 하나라도 바뀌면
  이 체크리스트의 절 참조가 깨진다.

### 1.4 외부에서 절/Q-번호를 실제로 인용하는 참조

`grep -rn "RFC-0020"` 결과, 다음 16개 문서가 이 RFC를 인용한다(파일
목록):

```
docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md
docs/research/DOCUMENT-INVENTORY-0001.md
docs/decisions/rfc.md, docs/decisions/adc.md
docs/architecture/core/ADC-0020~0026(다수), ADR-0009, ADR-0010, ADR-0018,
docs/architecture/core/RFC-0021, RFC-0022
```

이 중 `ADC-0020`(명칭/Adapter Contract Q-C·Q-D·Q-E 판단),
`ADC-0021`(구현 전략 Gate), `ADC-0022`(A-IN(a) State/Lifecycle
Resolution), `ADR-0009`(Adapter Contract (a)(b)(d) Baseline 반영)는
이 RFC의 **§5.3 후보 절 (a)~(d) 라벨**과 **§8.1 Q-번호**를 직접
가리키며 판단을 내렸다 — 이미 확정된 Baseline 텍스트가 그 라벨
체계를 전제로 작성돼 있다. 이는 §Q-번호/절 라벨이 단순 내부 조직화
도구가 아니라 **저장소 전체 Governance Chain의 좌표계**로
기능한다는 뜻이다.

### 1.5 제안 6-섹션 매핑

| 6-섹션 | 매핑 대상 |
|---|---|
| Identity & Status | 최상단 Status/Author/대상 문단 → 표로 변환 |
| Problem & Context | §0+§1(통합, 중복만 제거) + §2(Problem, 4항목 유지) |
| Questions & Alternatives | §3(Evidence 표, verbatim) + §4.1/§4.2(Alternatives 표, N/C 라벨 유지) + §8(Open Questions, Q-A~Q-J 표 verbatim, 8.1/8.2 구분 유지) |
| Proposed Direction | §5(Proposal 5.1~5.5) — 압축 없이 그대로, "결정 아님" 명시 유지 |
| Requested Review | §7(범위 밖 표) + §9(Traceability 표, verbatim) — 이 템플릿에 없는 두 표는 "Requested Review" 아래 하위 표로 추가 배치(섹션 신설 아님, 기존 섹션 안에 표만 추가) |
| Related Documents / Change History | §9 Traceability 표의 문서 목록을 Related Documents 형식으로도 중복 등재(원문 표는 유지) |

**주의**: §6(Consequences)과 §10(Self Review)은 RFC-TEMPLATE.md에
대응 섹션이 없다 — RFC 템플릿 자체가 "최종 결정이 아니다"라는 전제라
Consequences/Self Review 섹션을 두지 않는다. 이 둘을 강제로 템플릿에
끼워 넣기보다 "Requested Review" 섹션 뒤에 원래 번호를 유지한 부록
성격 섹션(`## 부록: Consequences`, `## 부록: Self Review`)으로
남기는 편이 템플릿 위반을 정직하게 표시하면서도 정보를 보존한다.

### 1.6 추적성/감사 기록 손실 위험

**높음.** 이 RFC는 §16.6 Boundary Question이 "명명" 단계로 넘어가는
지점 전체(Q-A~Q-F)를 정의했고, 그 정의를 `ADC-0020`이 그대로 받아
판단했다. Q-번호나 후보 라벨(N-1, C1, (a)~(d))을 조금이라도 바꾸면
`ADC-0020`/`ADC-0021`/`ADC-0022`/`ADR-0009`/`ADR-0010`/`ADR-0011`
(총 5개 이상의 후속 Baseline 반영 ADR) 본문의 인용이 무엇을
가리키는지 알 수 없어진다 — 이는 이미 **Frozen Architecture
Baseline**(`docs/architecture/baseline/BASELINE.md`)에 반영된
내용의 근거 사슬을 훼손하는 것과 같다.

### 1.7 권장 구현 방법

**구조 보존형 재배치만 수행한다** — 표·Q-번호·후보 라벨을 전부
verbatim으로 유지하고, 산문 연결 문장만 다듬어 6-섹션 틀 안에
재배치한다. 실제 텍스트 압축률은 낮을 것으로 예상(추정 10~15%)되며,
이는 원본이 이미 표 중심으로 밀도가 높기 때문이다. 편집 전 별도로
"이 RFC를 인용하는 16개 문서의 Q-번호/라벨 인용문"을 스냅샷으로
저장해 두고, 편집 후 그 스냅샷과 재대조하는 회귀 검증 스크립트를
먼저 준비할 것을 권장한다.

---

## 2. `RFC-0043` — Execution History & Evidence Persistence Architecture

### 2.1 현재 구조 및 주요 섹션

544행, `##` 22개 최상위 섹션(§1 Status ~ §23 Risks + Open Questions +
Required ADC/ADR Follow-up). 섹션 대부분이 원 지시사항(사용자
요청서)의 번호를 그대로 따른 것으로 보인다 — 예: "§9 요구사항",
"§10 요구사항", "§11 요구사항"처럼 각 섹션 제목이 스스로 대응하는
요구사항 번호를 명시한다.

### 2.2 안전하게 압축 가능한 내용

- §4(Current Architecture)의 4.1/4.2/4.3/4.4 서술 중, 같은 결론
  ("§16.6 Workflow Adapter는 존재하지만 영속화는 caller-owned")을
  §14(Progress/Time)·§19(Cancel/Retry/Resume)에서 다시 설명하는
  부분은 참조로 축약 가능.
- §21(Security/Integrity)은 "Concern만 기록"이라고 스스로 명시한
  나열형 리스트 — 산문을 bullet 그대로 유지하되 도입 문장만 압축
  가능.

### 2.3 반드시 verbatim 또는 구조 그대로 유지해야 하는 내용

- **§4.2 Kernel 측 Scoped Accept 표**(§16.1~§16.7 상태 요약) —
  이 표는 저장소 전체 Kernel Governance 상태의 스냅샷이며, 이후
  `ADC-0046`/`RFC-0044`가 이 표의 결론(§16.6 caller-owned 제약)을
  전제로 이어받았다.
- **§12 Option Comparison 표, §22 Architecture Principles 기준
  평가 표**: A/B/C/D Option 라벨이 §8~§11(Option 서술)과 §Recommendation에서
  반복 참조된다 — 표를 없애면 Option 비교의 근거가 산문 속에
  흩어져 추적 불가능해진다.
- **§15 Persistence 표, §19 Cancel/Retry/Resume 표**: "무엇이
  저장 안 되어 있는가"의 감사 기록 — 이 RFC의 핵심 발견(Evidence
  개념 자체의 부재, §4.3)을 뒷받침하는 유일한 근거.
- **Recommendation / Decision Candidate, Required ADC/ADR
  Follow-up 섹션**: 후속 ADC가 "Option B의 좁은 부분집합만 열어야
  한다"는 이 RFC의 결론을 그대로 승계했다(§4 근거: `RFC-0044`가
  이 RFC의 직접 후속으로 존재).

### 2.4 외부에서 절/요구사항 번호를 실제로 인용하는 참조

`grep -rln "RFC-0043"` 결과 6개 문서가 인용하며, 그중
`docs/architecture/core/ADC-0046-workflow-execution-history-verification-persistence-ownership-boundary.md`와
`docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md`는
이 RFC의 **직접 후속 문서**로서 Option B 부분집합·Boundary Question
범위를 이어받았다. 이 두 문서가 존재한다는 사실 자체가, `RFC-0043`
Recommendation 절의 "다음 단계는 Boundary Question 하나짜리 후속
RFC를 여는 것"이라는 제안이 실제로 실행됐음을 보여준다 — 즉 이
문서는 단순 분석 메모가 아니라 **실제로 후속 절차를 만들어낸
근거 문서**다.

### 2.5 제안 6-섹션 매핑

| 6-섹션 | 매핑 대상 |
|---|---|
| Identity & Status | §1(Status), 최상단 Status/Author/대상/Evidence 범위 문단 |
| Problem & Context | §2(Context) + §3(Problem Statement) + §4(Current Architecture, 표 3개 verbatim) + §5(Current Limitations) |
| Questions & Alternatives | §6(Requirements) + §7(Architecture Constraints) + §8~§11(Option A~D) + §12(Option Comparison 표) + Open Questions(4개, 원문 번호 유지) |
| Proposed Direction | §13~§22(Execution Identity/State/Persistence/Evidence/Task↔Execution/Progress/Cancel-Retry-Resume/Boundary/Security/Principles) — 분석 섹션이므로 "제안이며 결정 아님" 명시하에 그대로 배치. 22개 하위 절 번호는 유지(§13~§22라는 번호 자체가 각 절 제목에 새겨져 있어 재배열이 위험) |
| Requested Review | Recommendation/Decision Candidate + Risks(§23) + Open Questions + Required ADC/ADR Follow-up |
| Related Documents / Change History | 신규 추가 |

### 2.6 추적성/감사 기록 손실 위험

**높음.** §13~§22의 절 번호가 "지시사항 §N 요구사항"이라는 외부
프레임과 1:1 대응되어 있어(예: "§9 요구사항", 원 사용자 지시서의
번호로 추정), 이를 6-섹션 템플릿 논리에 맞춰 재배열하면 "어느
섹션이 원래 어떤 요구사항에 답한 것인지"의 매핑이 깨진다. 또한
`ADC-0046`/`RFC-0044`가 이 문서의 결론(Option B 부분집합)을
계승했으므로, Option 라벨(A/B/C/D)을 바꾸는 것은 후속 문서의
근거를 소급 훼손하는 것과 같다.

### 2.7 권장 구현 방법

**구조 보존형 재배치 + 섹션 그룹핑만 수행한다.** §13~§22는 번호를
그대로 두고 "Proposed Direction" 상위 섹션 아래 하위 절로 묶는다
(번호 재부여 없음). 압축은 §4의 반복 서술 정리 정도로 제한하고
(추정 압축률 5~10%), Option 비교표·Persistence 표·Cancel/Retry/
Resume 표는 전부 verbatim 유지한다.

---

## 3. `ADC-0019` — Scoped Workflow Graph Execution Boundary

### 3.1 현재 구조 및 주요 섹션

655행, 163개 문서 전체 중 최장. `##` 최상위 구조:

- 목적, "이 ADC가 답하지 않는 것"(리스트)
- Evidence 요약(승격 지지/막는 쪽, E1~E4·G1~G5)
- **Q0~Q8** 순차 분석 섹션(각각 "검토"→"결론" 하위 구조)
- Decision(6개 조건, A. Accept Scoped Conditional)
- Implementation Boundary(포함/제외 표)
- Risks(표) + 재검토 조건
- Next Step(6항목)
- Governance Chain 검증(12행 표)
- Architecture Governance Review(7문항)
- Self Review(11개 체크)

### 3.2 안전하게 압축 가능한 내용

- Q0~Q8 각 절의 "검토" 산문 중, 이미 §Evidence 요약에서 서술한
  E1~E4/G1~G5 내용을 다시 풀어 쓰는 부분(특히 Q1, Q2 서두)은
  Evidence 요약을 참조하는 한 문장으로 축약 가능.
- Decision 섹션의 "Reason" 하위 문단은 Q0~Q8 결론을 요약 재서술한
  것 — Q-번호 참조로 압축 가능하나, 이는 Decision 자체의 근거
  진술이므로 **삭제는 불가**, 문장 길이만 축약 가능.

### 3.3 반드시 verbatim 또는 구조 그대로 유지해야 하는 내용

- **Q0~Q8 섹션 구조 전체** — 아래 §3.4에서 확인하듯, 이 Q-번호는
  `BASELINE.md`(Frozen Architecture Baseline 원문) 자신이 8곳에서
  직접 인용하고 있다. Q-번호를 하나라도 재배열·재번호하면 **이미
  병합된 Architecture Baseline 문서의 각주가 깨진다** — 이는 이
  4개 문서 중 가장 심각한 단일 리스크다.
- **Decision 섹션의 6개 조건**(A-IN/A-OUT/§16.3~16.5 불가침/
  Reversibility/조건 이월/미확정 항목) — `ADR-0011` §Out of Scope
  표가 "`ADC-0019` §Decision 조건 1~6"을 항목별로 직접 인용한다.
- **Governance Chain 검증 표(12행)** — RFC-0019/RFC-0013~0018/
  ADC.md ADC-02/ADC-0008/ADC-0018과의 관계를 기록한 유일한 감사
  기록.
- **Self Review(11개 체크)** — 각 체크가 Q-번호·Decision 조건
  번호를 인용(예: "Q2", "§Decision 조건 4").

### 3.4 외부에서 Q-번호를 실제로 인용하는 참조 (가장 중요한 발견)

`grep -n "ADC-0019.*§Q"` 결과, **`docs/architecture/baseline/BASELINE.md`
자신이 8곳에서 `ADC-0019 §Q2`, `§Q3·§Decision 조건 1`, `§Q4·§Decision
조건 2`, `§Q5`(2곳), `§Q7·§Decision 조건 5`, `§Q8`을 직접 인용한다**
(§16.6 본문 문단들). 이는 CLAUDE.md의 Frozen Architecture 원칙상
직접 수정할 수 없는 문서가 이 ADC의 Q-번호 체계를 그 본문의
일부로 이미 흡수했다는 뜻이다.

추가로 다음 문서들이 `ADC-0019`의 Q-번호·Decision 조건을 인용한다:
`ADC-0020`~`ADC-0026`(6건), `ADR-0008`~`ADR-0011`, `ADR-0014`,
`RFC-0021`~`RFC-0027`(다수), `docs/governance/DECISION-GROUP-REGISTRY.md`,
`docs/00_governance/GLOSSARY.md`, `docs/decisions/{rfc,adc,adr}.md`
(통합 원장), `DOCUMENT-INVENTORY-0001.md`. 총 30개 이상의 문서가
이 ADC를 인용하며, 그중 다수가 Q-번호 또는 Decision 조건 번호를
구체적으로 지목한다.

### 3.5 제안 6-섹션 매핑

| 6-섹션 | 매핑 대상 |
|---|---|
| Identity & Status | 목적 문단 → 표 변환, "이 ADC가 답하지 않는 것" 리스트 유지 |
| Decision Scope & Context | Evidence 요약(승격 지지/막는 쪽) verbatim |
| Candidates / Options | **매핑하지 않는다** — 이 문서는 후보 비교형이 아니라 순차 판단형(Q0~Q8)이다. 대신 아래 "Evaluation"에 Q-섹션 전체를 배치 |
| Evaluation | **Q0~Q8 전체를 이 섹션의 하위 절(`### Q0`~`### Q8`)로 번호·내용 모두 verbatim 유지하며 그대로 이동**. 이것이 이 문서 압축의 핵심 원칙: "표를 만들어 압축"하지 않고 "섹션을 그대로 하위 절로 강등"한다 |
| Recommendation & Decision Boundary | Decision(6개 조건) + Implementation Boundary(포함/제외 표) + Next Step |
| Open Questions | 재검토 조건(Risks 표 하단) |
| Related Documents | Governance Chain 검증 표(12행) — 형식을 표준 Related Documents 표로 변환하되 "정합성" 열 내용은 verbatim 보존 |
| Change History | 신규 추가(원 문서에 없음) |

**§Architecture Governance Review·§Self Review**는 ADC-TEMPLATE.md에
대응 섹션이 없다 — RFC-0020과 동일하게 "부록" 섹션으로 원 번호를
유지한 채 보존을 권장한다.

### 3.6 추적성/감사 기록 손실 위험

**매우 높음 — 4개 문서 중 최고 위험도.** `BASELINE.md`(Frozen,
CLAUDE.md 원칙상 직접 수정 불가)가 이 문서의 Q-번호를 8곳에서
인용하는 것이 확인된 이상, Q-번호를 조금이라도 바꾸면:

1. `BASELINE.md` 본문의 각주 참조가 깨진 링크가 된다(문서를
   고치지 않고는 고칠 수 없음 — Frozen).
2. 이를 되돌리려면 별도 RFC → ADC → ADR 절차를 거쳐 `BASELINE.md`
   자체를 다시 고쳐야 하는 순환이 발생한다.
3. 30개 이상의 다른 Governance 문서의 인용도 함께 깨진다.

**따라서 이 문서의 Q-번호와 Decision 조건 번호는 어떤 상황에서도
변경 대상이 아니다.**

### 3.7 권장 구현 방법

**섹션 강등(demotion)만 수행, 재배열·재번호·표 변환 금지.** Q0~Q8을
`## 4. Evaluation`의 하위 `### Q0`~`### Q8`로 그대로 옮기고, 각
절 내부의 "검토"/"결론" 소제목과 문장도 그대로 유지한다. 압축은
Decision 섹션의 Reason 문단에서 이미 Q-요약과 중복되는 문장 정리
정도로 제한(추정 압축률 5% 미만). **이 문서는 편집하더라도 원문
대비 실질 압축 효과가 거의 없을 것으로 예상되며, 템플릿 형식
정합성만 얻고 정보량은 그대로 유지하는 것이 유일하게 안전한
목표다.**

---

## 4. `ADR-0011` — Gate (A) 결정 2·5·11 Resolution의 Baseline 반영

### 4.1 현재 구조 및 주요 섹션

596행. 이 문서는 **이미 실행 완료된(Accepted, 2026-09-04 사용자
승인)** `BASELINE.md`·`GLOSSARY.md` 편집의 감사 기록이다.

- Identity 표 + Status(Accepted, 실행 내역 요약)
- Out of Scope(12행 표)
- Decision — §1(변경 대상 파일 표) + **§2.1~§2.7**(BASELINE.md §16.6
  갱신 내용 — 각 하위 절이 "기존 텍스트" 코드 블록과 "교체 후"
  코드 블록을 나란히 제시) + §3((c) 처리) + §4(§6 Concept Model
  표 갱신 여부) + §5(GLOSSARY.md 갱신, 5.1/5.2) + §6
  (IMPLEMENTATION_RULES.md 갱신 여부) + §7(Version 정책) +
  §8(Migration Strategy, 이미 실행됨 — 4단계 체크리스트)
- Consequences, Architecture/Contract/Kernel 영향
- Governance Chain 검증
- Self Review(13개 체크)

### 4.2 안전하게 압축 가능한 내용

- Out of Scope 표의 각 행에 딸린 "근거" 열 설명 중 일부는 여러 행이
  같은 근거(`ADC-0022` §6 조건 6 등)를 반복 인용 — 표 자체는
  유지하되 중복 인용 문구를 축약 가능.
- §7(Version 정책)의 "Frozen 유지 근거"/"Minor 증가 근거" 서술은
  다소 장황하나 정보 손실 없이 문장 압축 가능.

### 4.3 반드시 verbatim 또는 구조 그대로 유지해야 하는 내용

- **§2.1~§2.7의 "기존" / "교체 후" 코드 블록 전체** — 이것은
  일반적인 "결정 설명"이 아니라 **실제로 BASELINE.md에 적용된
  편집의 diff 기록**이다. "기존" 블록은 편집 전 원문, "교체 후"
  블록은 실제로 삽입된 문장이다. 이 코드 블록을 압축·재서술하면
  실제 Baseline 반영 내용과 이 ADR의 기록이 어긋나게 되어 **문서가
  스스로의 감사 목적을 상실**한다.
- **§8 Migration Strategy의 4개 검증 체크리스트** — "이미 실행된"
  절차의 검증 기준이며, 향후 `git diff`로 재검증할 때 쓰는 유일한
  체크리스트다.
- **Governance Chain 검증**(`RFC-0021`→`ADC-0022`→이 ADR) 및
  **Self Review 13개 항목** — 각 항목이 "결정 9 / Gate (B) / Gate
  (C)를 바꾸지 않았는가" 등 정확히 무엇을 확인했는지의 기록.
- **Out of Scope 표 전체** — 어떤 항목을 의도적으로 건드리지
  않았는지의 유일한 명시적 목록.

### 4.4 외부에서 절/결정 번호를 실제로 인용하는 참조

`grep -rln "ADR-0011"` 결과 32개 파일에서 매치되나, 대다수는
`docs/decisions/adr/ADR-0011-implementation-freedom-principle-baseline.md`
(Dev HQ 트리, **이름이 같은 별개 문서** — 8절 "교차 트리 ID 충돌"
선례와 동일 패턴, 착오 주의)에 대한 참조다. **Kernel 트리
`docs/architecture/core/ADR-0011`을 실제로 인용하는 문서**는
`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`,
`DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md`,
`DOCUMENT-INVENTORY-0001.md`, `REGISTRATION-CANDIDATES-0001.md`,
그리고 4개 통합 원장(`docs/decisions/{rfc,adc,adr}.md`)이다 — 이들은
전부 이번 PR #214 계열 작업이 만든 등록/인벤토리 문서로, **문서
존재 여부와 상태(Accepted)만 참조**할 뿐 내부 절 번호를 인용하지
않는다. 즉 이 ADR은 앞의 3개 문서와 달리 **외부의 다른 Governance
결정 문서로부터 §2.x 절 번호 자체를 인용받는 경우는 확인되지
않았다.**

그러나 이 사실이 리스크를 낮추지는 않는다 — §4.3에서 확인했듯
이 문서의 위험은 "다른 문서가 절 번호를 인용해서"가 아니라 **이
문서 자체가 실제로 실행된 BASELINE.md 편집의 유일한 기록**이라는
데 있다. `BASELINE.md` §16.6은 이미 이 ADR이 지시한 대로 편집되어
있으므로(§Migration Strategy가 "실행되었다"고 명시), 이 ADR의
"기존"/"교체 후" 블록을 재서술하면 **실제 Baseline 현재 텍스트와
이 ADR이 주장하는 "무엇을 왜 바꿨는지"가 어긋날 위험**이 생긴다.

### 4.5 제안 6-섹션 매핑

| 6-섹션 | 매핑 대상 |
|---|---|
| Identity & Status | Identity 표 + Status(Accepted, 실행 요약) |
| Context & Decision Drivers | Out of Scope 표(verbatim) + 선행 ADR/ADC 체인 |
| Decision | §1(변경 대상 파일) + §2.1~§2.7(코드 블록 전부 verbatim, 절 번호 유지) + §3~§7 |
| Rationale & Alternatives | Rationale = §2 도입부의 "ADC-0022가 이미 내린 Decision을 옮기는 구현 결정" 서술. Rejected Alternatives = 해당 없음(이 ADR은 대안 비교형이 아니라 이미 결정된 사항의 반영 기록이므로 "해당 없음"을 명시) |
| Consequences & Impact | Consequences + Architecture/Contract/Kernel 영향(verbatim) |
| Architecture Baseline & Implementation | §8 Migration Strategy(체크리스트 verbatim, "실행되었다" 상태 명시 유지) |
| Related Documents | Governance Chain 검증 표를 표준 형식으로 |
| Change History | Self Review 13개 항목은 부록으로 보존(템플릿 대응 섹션 없음) |

### 4.6 추적성/감사 기록 손실 위험

**높음, 단 위험의 성격이 다르다.** 다른 3개 문서는 "외부 문서의
인용이 깨지는" 위험이 중심이지만, 이 ADR은 **자기 자신이 유일한
1차 사료(the only primary record)인 diff 기록**이라는 점에서
위험하다. 코드 블록 하나만 잘못 요약해도 "실제로 BASELINE.md에
무엇이 삽입됐는가"를 확인할 방법이 이 문서 하나뿐이므로 복구가
불가능하다(git 히스토리로 재구성 가능하긴 하나, 이 ADR의 존재
목적 자체가 "git diff를 다시 파지 않고도 확인 가능하게" 하는
것이다).

### 4.7 권장 구현 방법

**코드 블록 절대 불가침 원칙으로 재배치만 수행.** §2.1~§2.7의
"기존"/"교체 후" 코드 블록은 문자 단위로 원문 그대로 복사하고,
그 앞뒤 설명 문장만 다듬는다. 편집 후 반드시 `BASELINE.md` §16.6의
현재 텍스트와 이 ADR의 "교체 후" 블록들을 `diff`로 대조해 실제
Baseline 상태와 일치하는지 재확인하는 것을 편집의 필수 완료
조건으로 둔다(예: 각 "교체 후" 블록이 여전히 `BASELINE.md`
§16.6에 문자 그대로 존재하는지 grep 확인).

---

## 5. 4개 문서 종합 비교

| 문서 | 위험도 | 위험의 성격 | 권장 방법 |
|---|---|---|---|
| RFC-0020 | 높음 | 5개 이상 후속 ADC/ADR이 Q-번호·후보 라벨을 인용 | 구조 보존형 재배치, 표/라벨 verbatim |
| RFC-0043 | 높음 | 절 번호가 원 요구사항 번호와 1:1, 후속 RFC-0044/ADC-0046이 결론 승계 | 구조 보존형 재배치, Option 라벨 verbatim |
| ADC-0019 | **매우 높음(최고)** | **Frozen `BASELINE.md` 본문이 Q-번호를 8곳에서 직접 인용** | Q0~Q8 섹션을 그대로 하위 절로 강등, 번호 절대 불변 |
| ADR-0011 | 높음(성격 다름) | 자기 자신이 실행 완료된 Baseline 편집의 유일한 diff 기록 | 코드 블록 문자 단위 보존 + 편집 후 BASELINE.md 대조 검증 필수 |

공통 권장 사항: 4개 문서 모두 **"산문을 표로 압축"하는 방식이
아니라 "기존 표·번호 구조를 그대로 템플릿 섹션 아래로 재배치"하는
방식**이 유일하게 안전하다. 이는 지난 라운드에서 압축이 성공적으로
적용된 6개 샘플(반복 서술형 문서)과 근본적으로 다른 문서
유형이라는 뜻이다 — 6개 샘플은 "같은 내용을 산문으로 여러 번
반복 서술"한 것이 압축 대상이었지만, 이 4개 문서는 처음부터
표·번호 체계로 정보 밀도를 이미 최대화해 두었다.

---

## 6. 검증 방법 (편집 착수 시 반드시 선행)

1. 편집 전, 4개 문서 각각을 인용하는 모든 외부 문서의 인용 문자열을
   `grep -n "<ID>.*§"` 패턴으로 스냅샷 저장한다(이 보고서 §1.4·
   §2.4·§3.4·§4.4가 그 스냅샷의 1차본).
2. 편집 후, 동일 grep을 재실행해 인용 대상 절 번호·Q-번호·라벨이
   편집된 문서 안에 여전히 동일한 이름으로 존재하는지 대조한다.
3. `ADC-0019`는 특히 `docs/architecture/baseline/BASELINE.md`의
   8개 인용 지점(§16.6 문단들)을 개별적으로 재확인한다 — 이 파일은
   Frozen이므로 이 문서가 깨지면 되돌릴 수 없는 순환 문제가 된다.
4. `ADR-0011`은 §2.1~§2.7 "교체 후" 블록 7건 전부를 `BASELINE.md`
   §16.6 현재 텍스트와 `diff`로 대조해 문자 단위 일치를 확인한다.
5. 4개 문서 모두 YAML Front Matter를 추가하지 않았는지, Document
   ID·Status가 원문과 동일한지 재확인한다.

---

## 7. 문서별 권장 다음 조치

- **RFC-0020**: 구조 보존형 재배치 편집을 진행할 수 있다 — 단,
  편집 전 §6 검증 방법 1을 먼저 수행하고 사용자 승인을 받은 뒤
  진행할 것을 권장한다.
- **RFC-0043**: 구조 보존형 재배치 편집을 진행할 수 있다 — §13~§22
  절 번호를 그대로 보존하는 것을 편집 승인 조건으로 명시할 것을
  권장한다.
- **ADC-0019**: **편집을 보류하고 별도로 재논의할 것을 권장한다.**
  `BASELINE.md`(Frozen)가 Q-번호를 직접 인용하는 것이 확인된 이상,
  이 문서의 편집은 이 PR의 "문서 재정비"라는 낮은 리스크 범위를
  넘어선다 — 최소한 "Q0~Q8 섹션을 그대로 하위 절로 강등하고 번호는
  일절 변경하지 않는다"는 제약을 사용자가 명시적으로 재확인한
  뒤에만 진행해야 한다.
- **ADR-0011**: 편집을 진행할 수 있으나, 편집 직후 반드시 §6
  검증 방법 4(코드 블록 대 실제 BASELINE.md 대조)를 실행하고 그
  결과를 편집 보고서에 포함할 것을 완료 조건으로 삼을 것을
  권장한다.

---

## 완료 조건 확인

- 문서 수정: 없음(대상 4개 문서 전부 미수정).
- Architecture/Contract 변경: 없음.
- Commit/Push: 수행하지 않음.
- 이 보고서 자체(`docs/research/HIGH-RISK-DOCUMENT-PRESERVATION-REVIEW-0001.md`)만
  신규 작성.
