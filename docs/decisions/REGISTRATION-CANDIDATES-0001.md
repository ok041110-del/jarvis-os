---
document_id: REGISTRATION-CANDIDATES-0001
title: Core Document Ledger Registration — 검증·등록 라운드 기록
type: Research
target_domain: Governance
status: Complete
decision_group: LEDGER
parent_documents:
  - docs/decisions/rfc.md
  - docs/decisions/adc.md
  - docs/decisions/adr.md
  - docs/decisions/open_decision.md
related_documents:
  - docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md
  - docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md
  - docs/01_mvp/MVP-0049-observation.md
  - docs/01_mvp/MVP-0050-observation.md
  - docs/01_mvp/MVP-0051-observation.md
  - docs/01_mvp/MVP-0052-observation.md
evidence_references: []
source_path: docs/decisions/REGISTRATION-CANDIDATES-0001.md
last_verified: 2026-09-20
verification_confidence: Medium
---

# Core Document Ledger Registration — 검증·등록 라운드 기록

이 문서는 통합 원장(`docs/decisions/{rfc,adc,adr,open_decision}.md`)에
기존 문서를 소급 등록하며 확인한 근거를 라운드별로 기록한다. 라운드가
늘어나도 이전 라운드 기록은 삭제하지 않고 절을 추가한다.

## 1차 라운드 — Execution Layer (PR #214)

### 1. 목적과 범위 축소 사유

PR #213으로 통합 원장 4개와 Research Index가 main에 반영된 뒤, 우선순위
높은 기존 문서를 본문 검증 후 원장에 등록하는 첫 라운드다.

지시된 검토 우선순위 1~3(`docs/01_mvp/`, `docs/architecture/`,
`docs/core/execution-layer/`) 중, 1차 라운드는 **`docs/core/execution-layer/`**
트리(RFC-0001~0005, ADC-0001~0005, ADR-0001~0002, 총 12건)로 범위를
축소했다. `docs/architecture/core/`(Kernel, 118건 규모)는 이 라운드에서
전수 대조가 불가능해 보류하고 2차 라운드로 넘겼다(아래 참조).

### 2. 확정 등록 — Execution Layer (12건)

| Document ID | Type | Source Path | 등록 원장 |
|---|---|---|---|
| RFC-0001 | RFC | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` | `docs/decisions/rfc.md` §6 |
| RFC-0002 | RFC | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` | `docs/decisions/rfc.md` §6 |
| RFC-0003 | RFC | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` | `docs/decisions/rfc.md` §6 |
| RFC-0004 | RFC | `docs/core/execution-layer/RFC-0004-execution-result-consumer.md` | `docs/decisions/rfc.md` §6 |
| RFC-0005 | RFC | `docs/core/execution-layer/RFC-0005-engine-connection-boundary.md` | `docs/decisions/rfc.md` §6 |
| ADC-0001 | ADC | `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md` | `docs/decisions/adc.md` §6 |
| ADC-0002 | ADC | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` | `docs/decisions/adc.md` §6 |
| ADC-0003 | ADC | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` | `docs/decisions/adc.md` §6 |
| ADC-0004 | ADC | `docs/core/execution-layer/ADC-0004-execution-result-consumer.md` | `docs/decisions/adc.md` §6 |
| ADC-0005 | ADC | `docs/core/execution-layer/ADC-0005-engine-connection-boundary.md` | `docs/decisions/adc.md` §6 |
| ADR-0001 | ADR | `docs/core/execution-layer/ADR-0001-execution-result-contract.md` | `docs/decisions/adr.md` §6 |
| ADR-0002 | ADR | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md` | `docs/decisions/adr.md` §6 |

**특기 사항 — RFC-0005 헤더 불일치**: RFC-0005 헤더는 `Proposed`라고
적혀 있으나, `ADC-0005-engine-connection-boundary.md`를 직접 읽어
이미 Decision(§Q0 Accept / §Q1 Not Accepted, 양쪽 다 No ADR Required)이
내려져 있음을 확인했다. 원장에는 본문 확인 결과를 Status로 기록했고,
RFC-0005 원본 파일은 수정하지 않았다.

### 3. MVP 문서 — Evidence Reference 후보 (docs/01_mvp/)

MVP-0049~0052 4건은 각 파일 첫 문단에서 스스로 **"문서 성격: 실제
실행 기록(Evidence)"**라고 명시한다. Decision Register에는 등록하지
않고 Evidence Reference 후보로만 기록한다.

| Document ID | Title | 구분 | Status(본문 판정) | Source Path |
|---|---|---|---|---|
| MVP-0049 | MVP-0049 Observation | Evidence(Observation) | 완료 — Capability 지시문 최소 수정 Prototype, Architecture/Contract 불변 | `docs/01_mvp/MVP-0049-observation.md` |
| MVP-0050 | MVP-0050 Observation (Phase 10 Prototype #1) | Evidence(Observation) | 완료 — Failure로 판정(MVP-0051로 이어짐), Architecture/Contract 불변 | `docs/01_mvp/MVP-0050-observation.md` |
| MVP-0051 | MVP-0051 Observation (Phase 10 Prototype #2) | Evidence(Observation) | 완료 — Success로 판정, Architecture/Contract 불변 | `docs/01_mvp/MVP-0051-observation.md` |
| MVP-0052 | MVP-0052 Observation (Phase 10 Boundary Validation) | Evidence(Observation) | 완료 — Success(경계 검증), 단 "탐지 재현율 편차" 별도 관찰(§4) | `docs/01_mvp/MVP-0052-observation.md` |

MVP → RFC/ADC/ADR 관계는 임의로 생성하지 않았다 — 4건 모두 원문에
그런 연결을 주장하는 서술이 없다.

### 4. Open Issue 후보 — MVP-0052 탐지 재현율 편차

MVP-0052 §2(L60~83)는 "같은 잠재 결함을 Engine이 매번 알아채는 것은
아니다"라는 **탐지 재현율(detection recall) 편차**를 관찰로 기록했다.
같은 문서 §Governance(L99~104)는 이를 스스로 다음과 같이 판정한다:

> "RFC/ADC/ADR 불필요. 탐지 재현율 편차는 '단일 stochastic Engine
> 호출의 본질적 특성'으로 판단한다 — 지금 Specification/Contract를
> 설계할 근거로 쓰지 않는다(NEED-DRIVEN DEFER)."

이 판정은 문서 자신의 결론이다. Open Decision으로 승격할 본문 근거가
없으므로 `docs/decisions/open_decision.md`에는 등록하지 않고 Open
Issue 후보로만 남긴다. 재검토 조건은 MVP-0052 원문의 판정 그대로다.

---

## 2차 라운드 — Kernel (`docs/architecture/core/`) (PR #214 확장)

### 1. 범위와 접근 방법

1차 라운드에서 보류했던 Kernel 트리(RFC 44건·ADC 46건·ADR 28건, 총
118건)를 이번 라운드에서 본문 대조했다. 접근 방법:

- 모든 RFC 파일의 헤더 `Status` 라인을 추출했다. 이 트리는 Dev HQ
  트리와 달리 상당수 RFC가 헤더에 실제 종결 ADC/ADR을 직접 인용하고
  있어("Resolved — `ADC-000X`로 종결됨…") 신뢰도가 상대적으로 높았다.
  다만 여전히 다수(RFC-0009~0012, 0014~0017, 0019~0023 등)가 헤더에
  `Proposed`로 남아 있는데도 해당 번호의 ADC가 이미 Decision을 내린
  경우가 발견됐다 — 기존 `docs/decisions/rfc/README.md`가 지적한
  D-9 색인 부채가 이 트리에도 존재한다.
- 모든 ADC 파일의 `## Decision`(또는 `### Decision`, `## 5. Decision`
  등 문서마다 다른 헤딩 레벨)절과, 다중 판단 ADC(예: `ADC-0001`~
  `ADC-0007`)의 `## 종합` 요약 표를 직접 읽어 Decision을 확인했다.
- 모든 ADR 파일의 "필드/내용" 표(`ID`/`제목`/`상태`/`Context`/
  `관련 RFC`/`관련 ADC`) 또는 이에 준하는 헤더를 읽어 실제 Status와
  Parent Documents를 확인했다. 이 트리의 ADR은 대부분 이 표를 통해
  종결시킨 RFC/ADC를 스스로 명시하고 있어, RFC/ADC 본문의 상호 인용
  (`grep -o "RFC-[0-9]\{4\}"` 등)과 함께 대조했을 때 신뢰도가 높았다.
- 각 문서의 Related/Parent Documents로 적은 경로는 전부 `ls`/`Read`로
  실제 존재를 확인했다(§5 검증 결과 참조).

### 2. 확정 등록 — Kernel (106건: RFC 38 + ADC 40 + ADR 28)

`docs/decisions/rfc.md`/`adc.md`/`adr.md` §6에 Target Domain=`Kernel`로
등록했다. RFC/ADC 각 6건(RFC-0002~0007, ADC-0002~0007)은 아래 §3의
이유로 이번 라운드에서도 보류했다 — 그래서 RFC 44건 중 38건, ADC
46건 중 40건만 등록됐다. ADR은 28건 전부 등록했다(모두 Accepted며,
Parent Documents가 ADR 자신의 표에 명시되어 있어 대조 부담이 낮았다).

등록된 문서 중 다음은 특히 주의가 필요해 각 원장 행의 Status/비고에
그대로 반영했다:

- **RFC-0009~0012, 0014~0017, 0019~0023**: 헤더가 `Proposed`로
  남아 있지만, 같은 번호(또는 인접 번호)의 ADC가 이미 Decision을
  냈음을 본문 대조로 확인했다 — Status를 `Resolved(헤더 미갱신 — D-9)`
  로 기록했다. RFC 원본 파일은 수정하지 않았다.
- **RFC-0021 → ADC-0022, RFC-0022 → ADC-0023 (번호 불일치)**: RFC
  번호와 이를 종결시키는 ADC 번호가 어긋난다. 이는 추정이 아니라
  `ADR-0011`/`ADR-0012`의 "관련 RFC"/"관련 ADC" 표가 직접 명시한
  대응이다 — Verification Confidence를 `Medium`으로 낮추고 원장에
  불일치 사실 자체를 기록했다.
- **ADC-0021, ADC-0024, ADC-0025, ADC-0026**: 전용 RFC 없이 선행
  ADC(`ADC-0019`/`ADC-0020`/`ADC-0024`)의 재검토 조건에 따라 열린
  후속 판단이다. Parent Documents를 "없음(선행 ADC의 후속 판단)"으로
  명시하고, RFC를 추정해 채우지 않았다.
- **ADR-0015~0017 (OmniRoute)**: 하나의 RFC(RFC-0023)와 5개 ADC
  (ADC-0027~0031)를 순차적으로 소비하는 Consolidation형 ADR 3건이다.
  `ADR-0015`는 스스로 "Consolidation Only — Baseline/Rules 문구
  미반영"이라고 명시해, Related Documents에 "문구 반영은 후속 ADR로
  이월"이라고 그대로 옮겼다(임의로 반영 완료라고 기록하지 않았다).
- **ADR-0018 (LangGraph Adoption Final Review)**: RFC 10건·ADC 10건을
  한 번에 종합하는 Consolidation ADR이며, 스스로 "2026-09-08 ADR-0019가
  이 판정을 부분 Supersede함"이라고 명시한다. Parent/Related Documents
  칸에 "다수"로 요약하고 Verification Confidence를 `Medium`으로
  낮췄다 — 개별 RFC/ADC 10+10건 전부를 이 ADR 하나의 근거로 낱낱이
  대조하지는 않았기 때문이다.
- **ADC-0040, ADC-0041 (Stage04/05)**: 헤더 자체가 `NOT DETERMINED —
  Real Engine Evidence Required`다. 이 라운드가 임의로 Resolved로
  올리지 않고 **Status를 `Open`으로 그대로 등록**했다(`ADR-0028`이
  "ADC-0040은 여전히 NOT DETERMINED — Open"이라고 재확인한 것과 일치).
- **ADC-0039 (Multi-Engine Re-Evaluation)**: Decision이 `RE-EVALUATE`
  (KEEP도 TRANSITION도 아님)이라, Status를 `Resolved`로 표기하되
  괄호로 "추가 Evidence 필요"임을 명시했다 — Accept/Reject로
  단순화하지 않았다.
- **RFC-0043/0044, ADC-0046 (Execution History)**: RFC-0043(넓은
  범위)이 후속 RFC-0044(좁힌 범위)로 승계되고, ADC-0046이 RFC-0044를
  주 근거로 Not Accepted 판정했다 — RFC-0043은 "자체 ADC 없음, 후속
  RFC로 범위가 좁혀짐"으로만 기록하고 Resolved로 표기하지 않았다.

### 3. 보류 — RFC/ADC-0002~0007 (Kernel Baseline 상세 6건)

RFC-0002~0007(Kernel Definition, Context Model, Public Contract,
Logical Reference Architecture, Context Ownership, Context Identity)과
그 ADC-0002~0007은 이번 라운드에서도 등록하지 않았다. 사유:

- 이 RFC들의 헤더는 "Resolved — `ADC-000X.md` → `ADR-000X`로
  종결됨"이라고 명시하지만, 그 "ADR-000X"가 가리키는 실제 파일이
  **`docs/architecture/core/`가 아니라 `docs/decisions/adr/`
  (Development HQ 물리 경로) 트리에 위치**한다
  (`docs/decisions/adr/ADR-0002~0005-*.md`, 예:
  `ADR-0003-kernel-context-model-baseline.md`가 Kernel `ADC-0003`을
  종결시킨다). 즉 Kernel Architecture 내용을 다루는 문서가 Dev HQ
  경로에 물리적으로 위치한, 저장소 자체의 기존 배치 문제다.
- 이 교차 배치는 이번에 새로 발견한 것이 아니라, 기존
  `docs/decisions/rfc/README.md` "Open Issues"가 이미 "저장소에는
  같은 번호의 `ADR-0002`가 두 곳 존재해 대상을 특정할 수 없다 —
  `Undetermined`로 남긴다"고 기록해 둔 문제와 같은 종류다.
- 각 원장의 Target Domain 필드는 "Document ID + Target Domain"으로
  전역 유일성을 보장하도록 설계했지만, 이 경우는 그 설계가 상정하지
  않은 **Target Domain(내용상 Kernel)과 물리 경로(Dev HQ 트리)가
  불일치**하는 사례다. 등록 자체는 가능하겠으나, Source Path를
  Target Domain에 맞춰 임의로 재해석하면 "Status를 임의 추론하지
  않는다"는 제약과 충돌할 위험이 있다고 판단해, 이 6건만 보류하고
  다음 라운드에서 별도로(Source Path와 Target Domain 불일치를 어떻게
  표기할지 결정한 뒤) 등록하기로 한다. **이 문제는 원본 문서를 이동·
  수정하지 않고는 근본적으로 해소되지 않으며, 그런 이동은 이번 작업의
  제약사항(기존 문서 이동 금지)을 벗어난다** — 그래서 등록 방식을
  결정하는 것 자체가 별도 판단(가능하면 Open Decision 후보)이 필요할
  수 있다.

### 4. 보류 — RFC-0026~0030 (조사·분석 기록, 후속 ADC 없음)

RFC-0026~0030은 각 헤더가 스스로 "Proposed(조사·판단/분석 결과 기록,
Baseline 결정 아님)"이라고 명시하고, 대응하는 ADC가 존재하지 않는다.
`docs/decisions/rfc.md`에는 Status를 `Open(조사·분석 기록)`으로
등록했으나(Decision Register에 남기되 Resolved로 과장하지 않기
위해), Related/Parent Documents는 "없음"으로 두고 향후 이 RFC들을
근거로 삼는 ADC가 실제로 작성될 때 관계를 채우기로 한다.

### 5. 검증 결과

실행한 검증(전부 Python 스크립트로 직접 실행):

- **Front Matter 파싱**: 원장 4개 + 이 문서 + Research Index 총 6건
  전부 YAML 파싱 성공.
- **Document ID 중복 검사**: (Document ID, Target Domain) 조합 기준
  중복 0건 — `rfc.md`(43행), `adc.md`(45행), `adr.md`(30행),
  `open_decision.md`(1행, 신규 없음) 전부 확인.
- **Source Path 존재 검증**: 등록된 모든 행의 Source Path를 `ls`로
  대조 — 누락 0건.
- **참조 경로(Related/Evidence) 존재 검증**: 원장·이 문서에서 인용한
  `docs/*.md` 경로를 정규식으로 추출해 존재 여부 확인 — 총 148개 중
  4개가 "누락"으로 잡혔으나 전부 원본 문서에 이미 있던 glob 표기
  (`ADC-000X-*.md` 등)이거나 이 문서 자체의 예시 텍스트이며, 실제
  Broken Link는 0건이다.
- **Markdown 표 구조 검증**: 4개 원장 §6 표의 컬럼 수가 전부 12로
  일치(헤더 포함) — 불일치 0건.
- **기존 문서 비의도적 변경 여부**: `git status`/`git diff --stat`로
  이번 라운드에서 수정된 파일이 `docs/decisions/{rfc,adc,adr}.md`
  3개(§6 등록 현황·안내 문구만) + 이 문서 뿐임을 확인 — Kernel/Dev HQ/
  Execution Layer의 원본 RFC/ADC/ADR/MVP 파일은 전혀 건드리지 않았다.
- **Architecture Baseline / Public Contract 영향**: 없음 — 원장은
  기존 Baseline 반영 여부를 "확인 필요" 등으로 인용만 했을 뿐,
  `docs/architecture/baseline/BASELINE.md` 자체를 열람·수정하지
  않았다. ADR이 실제로 Baseline에 반영됐는지 여부(Related Documents
  칸의 "반영 확인 필요")는 다음 라운드의 잔여 작업으로 남긴다.
- **테스트 회귀**: 해당 없음(코드 변경 없음, 문서만 변경).

### 6. 잔여 Open Issue (완료로 표시하지 않음)

- **RFC/ADC-0002~0007 등록 방식 미결정**(§3) — Source Path와 Target
  Domain 불일치를 어떻게 표기할지 결정이 필요하다.
- **ADR의 실제 Baseline 반영 여부 미대조** — 이번 라운드는 ADR 파일
  자신의 "Accepted" 주장과 관련 RFC/ADC 인용만 확인했고,
  `docs/architecture/baseline/BASELINE.md`를 열어 실제로 그 절이
  존재하는지까지는 대조하지 않았다. Related Documents 칸에 "반영
  확인 필요"로 명시해 과장하지 않았다.
- **RFC-0026~0030의 향후 ADC 승격 여부** — 현재는 Open(조사 기록)으로
  남아 있으며, 후속 ADC가 작성되면 그때 관계를 채운다.
- **`docs/architecture/core/`의 EVIDENCE-*/GOVERNANCE-REVIEW-*/
  CLOSURE-*/VALIDATION-* 등 비-RFC/ADC/ADR 문서**는 이번 라운드
  대상에 포함하지 않았다 — Evidence Reference 후보 검토는 다음
  라운드 과제로 남긴다.
- **`docs/governance/adc/ADC-0001~000X.md`(별도 Dev HQ ADC 트리)**는
  이번 두 라운드 모두 대상으로 삼지 않았다 — 미착수.

### 7. Self Review

- 검증되지 않은 문서를 원장에 등록했는가 — **아니오**. 헤더/본문을
  직접 읽어 Status를 확인한 문서만 등록했고, 확인이 애매한 6건
  (RFC/ADC-0002~0007)은 보류했다.
- Status를 임의 추론했는가 — **아니오**. `Proposed` 헤더도 ADC/ADR의
  실제 Decision을 본문에서 직접 확인한 경우에만 `Resolved`로
  재기록했고, 그 근거(어느 ADC/ADR을 봤는지)를 원장 행 또는 이 문서에
  남겼다. NOT DETERMINED/RE-EVALUATE 상태는 Resolved로 승격하지
  않았다.
- 기존 ID·파일명·번호를 변경했는가 — **아니오**.
- 기존 RFC/ADC/ADR/MVP 본문을 수정했는가 — **아니오**(§5 `git diff`
  확인).
- Architecture Baseline/Public Contract를 수정했는가 — **아니오**.
- RFC↔ADC↔ADR 관계를 추정으로 생성했는가 — **아니오**. 번호가 어긋난
  경우(RFC-0021/0022)도 ADR 자신의 표를 근거로만 기록했다.
- 미해결 항목을 완료로 표시했는가 — **아니오**(§6에 잔여 항목 명시).

---

## 3차 라운드 — 잔여 Open Issue 처리 (PR #214 최종 정리)

2차 라운드가 남긴 잔여 Open Issue를 이번 라운드에서 전부 검토했다.
후속 PR로 미루지 않고, 처리 가능한 항목은 이번 PR에서 완료했다.

### 1. 교차 트리 ADR 배치 문제 — 처리 완료

RFC/ADC-0002~0007(Kernel Definition~Context Identity)의 실제 종결
ADR을 조사한 결과, 다음을 확인했다:

- `docs/architecture/core/RFC-0002~0005.md`/`ADC-0002~0005.md`를
  종결시키는 ADR-0002~0005는 **물리적으로 `docs/decisions/adr/`
  디렉터리**(`ADR-0002-core-to-kernel-terminology-unification.md`
  등)에 있다 — 각 ADR 파일 자신의 "관련 RFC"/"관련 ADC" 표가
  `docs/architecture/core/RFC-000X.md`/`ADC-000X.md`를 직접 인용해
  확인했다.
- 이 물리적 배치는 기존 `docs/decisions/rfc/README.md`의 "Open
  Issues"가 이미 지적한 "동일 번호 ADR-0002가 두 곳에 존재해 대상을
  특정할 수 없다"는 문제와 같은 뿌리다 — 이번 조사로 그 두 곳이
  정확히 무엇인지 확인했다: `docs/architecture/core/ADR-0002-
  execution-layer-module-baseline.md`(Kernel Execution Layer Module)
  와 `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-
  unification.md`(Kernel Definition/용어 통합) — **둘 다 내용상
  Target Domain이 `Kernel`이면서 물리적으로 다른 두 파일**이다.
  같은 패턴이 ADR-0003·0004·0005에도 반복된다(4건 전부).
- **원장 등록 방식 검증 결과 — 기존 방식이 부정확했다.** 이전
  라운드까지 "Document ID + Target Domain 조합이 전역적으로
  유일하다"고 문서화했으나, 이번 조사로 그 전제가 거짓임이 실측
  확인됐다(위 4건, 그리고 아래 §3에서 추가로 확인한
  `docs/governance/adc/ADC-0005.md` vs `docs/decisions/adc/ADC-0005-
  structure-v1-migration-decisions.md` 사례). **수정 방식**: 파일을
  이동·복사·재번호화하지 않고(제약사항 준수), 대신 원장 스키마의
  전역 유일 키 정의를 "Document ID + Target Domain"에서 "Document ID
  + Target Domain + Source Path"로 정정했다 — `rfc.md`/`adc.md`/
  `adr.md` §2 필드 설명과 §7 검증 기준에 이 사실과 구체적 충돌
  사례를 명시했다. 이것은 구조 변경(파일 이동)이 아니라 내가 작성한
  원장 문서 자신의 스키마 설명을 사실에 맞게 고친 것이다.
- 이 수정 후 RFC-0002~0007, ADC-0002~0007(Kernel, `docs/architecture/
  core/` 물리 경로), ADR-0002~0005(Kernel 내용, `docs/decisions/adr/`
  물리 경로, Source Path로 기존 Kernel ADR-0002~0005와 구분)를 원장에
  등록했다. 각 행에 교차 트리 관계를 명시적으로 기록했다.
- **구조 변경 제안(실행하지 않음)**: 근본 해소는 두 방법 중 하나다 —
  (a) `docs/decisions/adr/ADR-0002~0005-*.md` 4개 파일을
  `docs/architecture/core/`로 물리 이동(파일명·번호는 유지),
  (b) 현재 위치를 유지하고 각 파일 헤더에 "이 ADR은 Kernel Target
  Domain에 속하며 `docs/architecture/core/` 트리와 물리적으로
  분리되어 있다"는 한 문장을 추가. 두 방법 모두 이번 작업 범위 밖
  (파일 이동·본문 수정 금지)이라 실행하지 않고 근거만 남긴다 — 사용자
  판단이 필요하다.

### 2. Baseline 반영 여부 — 처리 완료 (대부분 확인됨)

`docs/architecture/baseline/BASELINE.md` §17 "Version" 절의 변경
이력 표를 직접 읽어, 이전 라운드에서 "반영 확인 필요"로 남겨뒀던
항목을 전부 대조했다:

| ADR | Baseline 절 | 버전 | 확인 결과 |
|---|---|---|---|
| ADR-0001(Kernel) | §16 | v1.5 | **확인됨** |
| ADR-0002(Kernel, execution-layer-module) | §16.2 | v1.6 | **확인됨** |
| ADR-0002(Kernel 내용, decisions/adr 물리 경로) | §11·§12 | v1.1 | **확인됨** |
| ADR-0003(Kernel, single-execution-unit) | §16.3 | v1.7 | **확인됨** |
| ADR-0003(Kernel 내용, decisions/adr 물리 경로) | §13 | v1.2 | **확인됨** |
| ADR-0004(Kernel, execution-host-naming) | §16.3 | v1.8 | **확인됨** |
| ADR-0004(Kernel 내용, decisions/adr 물리 경로) | §14 | v1.3 | **확인됨** |
| ADR-0005(Kernel, execution-host-implementation) | §16.3 | v1.9 | **확인됨** |
| ADR-0005(Kernel 내용, decisions/adr 물리 경로) | §15(및 §10 범위 한정) | v1.4 | **확인됨** |
| ADR-0006~0014, 0019(Kernel) | §16.4~§16.6 | v1.10~v1.19 | **확인됨**(1·2차 라운드에서 이미 인용, 이번에 버전 이력으로 재대조) |
| ADR-0021(Kernel, Stage01 Multi-Agent) | `RESPONSIBILITY.md`/`CONTEXT.md`(Baseline 아님) | — | **확인됨**(grep으로 실제 인용 확인) |
| ADR-0022(Kernel, Stage01 PRD) | `CONTEXT.md`/`RESPONSIBILITY.md`(Baseline 아님) | — | **확인됨** |
| ADR-0023(Kernel, Stage02 Planning) | `CAPABILITIES.md`/`README.md`(Baseline 아님) | — | **확인됨** |
| ADR-0010/0011(Development HQ, Governance) | `docs/governance/README.md`(Baseline 아님) | — | **확인됨**(해당 절 제목 grep으로 확인) |
| ADR-0015~0018, 0020, 0024~0028 | `hqs/development/IMPLEMENTATION_RULES.md` 등(Baseline 아님) | — | **부분 확인**(ADR-0015/OmniRoute만 spot-check, 나머지는 미대조 — 아래 §6 잔여 항목) |

**미반영 확인(Open Issue로 기록, 확정하지 않음)**: `ADR-0015`는
스스로 "Consolidation Only — Baseline/Rules 문구 미반영, 후속 ADR
대상"이라고 명시한다 — 이는 미반영을 **문서 자신이 인정**한 것이며,
Baseline은 수정하지 않았다(제약사항 준수). 이 ADR을 Accepted로
기록하되 Related Documents에 "문구 반영은 후속 ADR로 이월"이라고
그대로 남겨 과장하지 않았다.

Architecture Baseline 문서(`BASELINE.md`) 자체는 열람만 했고 한 글자도
수정하지 않았다(`git diff` 확인, 아래 §4).

### 3. 미검토 문서 영역 — 처리 완료 (등록 + 중요 발견)

**`docs/governance/adc/` 트리(10건)**: 전부 열람해 Decision을
확인했다 — Dev HQ RFC-0001~0011(`docs/decisions/rfc/`)을 종결시키는
ADC임을 확인하고 Target Domain=`Development HQ`로 원장에 등록했다
(ADC-0001~0010). 이 중 **`ADC-0010`(Issue #206 후속, RFC·ADC·ADR
통합 식별자 체계 도입 판단)은 이번 작업과 직접 관련된 중요한
선행 결정**이다 — 상세는 아래 "중요 발견" 참조.

**`docs/architecture/core/`의 비-RFC/ADC/ADR 문서(34건)**: 파일명
패턴과 2건(`DEVELOPMENT-HQ-V1.0-FREEZE-0001`, `DOC-TRIAGE-0001`)의
직접 대조로 분류했다. 34건 전부 각 문서 자신이 "Architecture 문서가
아니다"/"Governance 판단(Freeze 선언)"/"Documentation Review" 등으로
스스로를 RFC/ADC/ADR과 구분하고 있어, **Decision Register 대상이
아니다**로 판정했다.

| 패턴 | 건수 | 분류 | 근거 |
|---|---|---|---|
| `EVIDENCE-*`, `EVIDENCE-INVENTORY-*` | 14 | Research/Evidence | 실행 기록·검증 결과 문서(파일명 자체가 Evidence) |
| `GOVERNANCE-REVIEW-*` | 8 | Research(Governance 재검토) | 결정이 아니라 기존 결정의 재확인/재평가 기록 |
| `VALIDATION-*` | 2 | Research/Evidence | 검증 결과 기록 |
| `CLOSURE-*`, `REFACTORING-TRACK-CLOSURE-*` | 2 | Research(종결 보고) | 트랙 종료 보고, 새 결정 없음 |
| `*-FREEZE-0001`(Dev HQ v1.0/v2.0, Investment HQ v1.0) | 3 | Governance(Freeze 선언) | `DEVELOPMENT-HQ-V1.0-FREEZE-0001` 직접 대조 — "새 RFC/ADC/ADR 작성하지 않는다" 자기 선언 |
| `DOC-TRIAGE-0001` | 1 | Documentation Review | 직접 대조 — "Architecture 문서가 아니다" 자기 선언 |
| `COMPONENT-CANDIDATE-*`, `IMPLEMENTATION-PRIORITY-*`, `IMPL-ENTRY-*`, `EFFICIENCY-AUDIT-*`, `STABILITY-*` | 4 | Research/Audit | 조사·우선순위·감사 기록(RFC/ADC/ADR 형식 아님) |

이 34건은 물리적으로 `docs/research/` 바깥에 있어 Research Index
(`docs/research/README.md`)의 등록 대상도 아니다(그 Index는 §3에서
`docs/01_mvp/` Evidence 문서에 대해 이미 같은 원칙을 밝혔다 — 물리
경로가 `docs/research/`가 아니면 이 Index가 관리하지 않는다). 자동
추론·일괄 등록은 하지 않았다 — 34건 전부 Decision Register·Research
Index 어느 쪽에도 등록하지 않고, 이 분류표로만 존재를 기록했다.

**중요 발견 — `ADC-0010`과 이 통합 원장의 Decision Group 필드 충돌**:
`docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`
(Issue #206 후속)은 RFC/ADC/ADR의 fan-out/fan-in 관계를 추적하기
위해 **전역 단일 네임스페이스** `DG-NNNN`을 쓰는 별도 Registry
문서(`docs/governance/DECISION-GROUP-REGISTRY.md`)를 Scoped Accept로
승인했다 — 단, 그 문서 자체는 "후속 구현 작업"으로 지정됐을 뿐 아직
생성되지 않았다. 반면 이번 세 라운드에 걸쳐 만든
`docs/decisions/{rfc,adc,adr}.md` 원장은 이미 `DG-<도메인약어>-NNNN`
(예: `DG-KERNEL-0001`) 형식의 값을 독자적으로 채워 넣었다 — `ADC-0010`
이 정의한 공식 형식과 다르다. 이 불일치는 `docs/decisions/
open_decision.md`에 **`OD-0001`**로 정식 등록했다(Open Decision —
확정하지 않음, 다음 라운드에서 사용자 판단 필요).

### 4. 최종 검증 — 결과

전부 Python 스크립트로 직접 실행:

- **Front Matter YAML 파싱**: 원장 4개 + 이 문서 + Research Index
  총 6건 전부 성공.
- **Document ID / (Document ID, Target Domain) 중복**: (Document ID,
  Target Domain) 단독 기준으로는 5건 충돌이 실측 확인됐다
  (ADR-0002~0005 Kernel 4건 + ADC-0005 Development HQ 1건) — 이는
  버그가 아니라 저장소 자체의 실제 구조(같은 도메인 안에 물리적으로
  독립 채번된 여러 문서가 존재)를 정확히 반영한 것이다. **(Document
  ID, Target Domain, Source Path) 3중 키 기준으로는 원장 4개 전체
  (rfc.md 60행, adc.md 61행, adr.md 41행, open_decision.md 2행)에서
  중복 0건**임을 확인했다 — 원장 스키마를 이 3중 키로 정정했다(§1).
- **Source Path 존재 검증**: 등록된 모든 행의 Source Path를 `ls`로
  대조 — 누락 0건.
- **Related Documents/Evidence References 경로 존재 검증**: 4개
  원장 + 이 문서에서 인용한 `docs/*.md` 경로 정규식 추출 — 누락으로
  잡힌 항목은 전부 기존 glob 표기/예시 텍스트이며 실제 Broken Link는
  0건.
- **Markdown 표 컬럼 정합성**: 4개 원장 전체 컬럼 수 12로 일치 —
  불일치 0건.
- **원본 문서의 비의도적 변경 여부**: `git status`/`git diff
  --stat`으로 이번 라운드에서 수정된 파일이 `docs/decisions/
  {rfc,adc,adr,open_decision}.md` 4개(전부 §2/§6 필드 설명·등록
  현황만) + 이 문서 뿐임을 확인 — Kernel/Dev HQ/Execution Layer의
  원본 RFC/ADC/ADR/MVP 파일, `BASELINE.md`, `docs/governance/
  README.md`, `GLOSSARY.md`, `IMPLEMENTATION_RULES.md`,
  `RESPONSIBILITY.md`/`CONTEXT.md`/`CAPABILITIES.md` 등 Baseline
  반영 확인을 위해 **열람한** 모든 파일은 전혀 수정하지 않았다.
- **Architecture Baseline / Public Contract 변경 여부**: 없음 —
  `BASELINE.md`를 열람만 하고 수정하지 않았다.

### 5. 등록 현황 요약(누적)

| 구분 | 1차(Execution Layer) | 2차(Kernel) | 3차(Dev HQ + Kernel 잔여 + governance/adc) | 누적 |
|---|---|---|---|---|
| RFC | 5 | 38 | 17 | 60 |
| ADC | 5 | 40 | 16 | 61 |
| ADR | 2 | 28 | 11 | 41 |
| Open Decision | 0 | 0 | 1(OD-0001) | 1 |

### 6. 잔여 Open Issue (완료로 표시하지 않음)

- **OD-0001**(위 §3) — Decision Group Registry(공식 `DG-NNNN`)와 이
  원장의 `DG-<도메인>-NNNN` 형식 간 관계 미결정.
- **ADR-0002~0005 교차 트리 물리 배치**(§1) — 근본 해소(파일 이동
  또는 헤더 주석 추가)는 사용자 판단 필요, 이번 라운드는 등록 방식
  정정으로만 대응했다.
- **ADR-0015~0018, 0020, 0024~0028의 Baseline-외 반영처(§2)** —
  `IMPLEMENTATION_RULES.md` 등에서 ADR-0015 1건만 spot-check했고
  나머지는 미대조.
- **`docs/architecture/core/`의 34건 비-RFC/ADC/ADR 문서**는 분류만
  했고 Research Index 편입 여부(현재 설계상 `docs/research/` 물리
  경로만 관리)는 별도 판단이 필요하면 다음 라운드로 넘긴다.
- **Dev HQ `docs/decisions/rfc/`·`docs/decisions/adr/`의 나머지
  문서**(예: RFC-0006의 실제 Migration 실행 여부, Dev HQ 자체 Baseline
  문서 반영 여부)는 이번 라운드가 Parent/Related 필드 채우기 목적으로
  참조만 했을 뿐, 그 문서들의 Baseline 반영 여부까지 독립적으로
  재검증하지는 않았다.
- **`docs/governance/DECISION-GROUP-REGISTRY.md` 신규 생성**은
  `ADC-0010`이 이미 승인한 후속 구현 작업이지만, 이 PR의 범위(문서
  검증·등록)를 벗어난 별도 구현 작업이라 이번에 수행하지 않았다 —
  OD-0001이 이 결정을 추적한다.

### 7. Self Review

- 처리 가능한 항목을 후속 PR로 미뤘는가 — **아니오**. 지시된 4개
  영역(교차 트리 ADR, Baseline 반영, 미검토 문서, 최종 검증)을 모두
  이번 PR 브랜치에서 직접 처리했다. 처리 불가능한 항목(파일 이동,
  Registry 신규 생성)은 실행하지 않고 근거·제안만 남겼다.
- 기존 파일을 이동·복사·번호 변경했는가 — **아니오**.
- Architecture Baseline을 수정했는가 — **아니오**.
- 확인되지 않은 사항을 확정했는가 — **아니오**(ADR-0015~0028 미대조
  항목은 "확인 필요"로 남김, ADR-0015는 문서 자신의 미반영 인정을
  그대로 인용).
- 자동 추론·일괄 등록을 했는가 — **아니오**(34건 비결정 문서는 분류만,
  등록하지 않음).

## 4차 라운드 — PR #214 최종 잔여 항목 처리

3차 라운드가 §6에 남긴 "잔여 Open Issue" 중 실제로 확인 가능한
항목(Baseline-외 반영처 미대조 8건)을 직접 원문 대조로 마무리했다.

### 1. 교차 트리 ADR 배치 문제 — 재확인(변경 없음)

3차 라운드가 이미 원장 유일 키를 (Document ID, Target Domain,
Source Path)로 정정했고, 이번 라운드에서 그 스키마가 여전히
`rfc.md`/`adc.md`/`adr.md`/`open_decision.md` 전체에서 중복 0건을
유지함을 재확인했다(§4). ADR-0002~0005 교차 트리 물리 배치 자체의
근본 해소(파일 이동 또는 헤더 주석 추가)는 여전히 사용자 판단이
필요한 사안이며, 이번 라운드도 실행하지 않는다 — 제안만 유지한다.

### 2. Baseline 반영 여부 — 잔여 8건 원문 대조 완료

3차 라운드가 "미대조"로 남긴 항목을 전부 직접 열람해 대조했다.

| ADR | 확인 방법 | 결과 |
|---|---|---|
| ADR-0001(Development HQ) | `hqs/development/STRUCTURE.md`(17행) | **확인됨** — "Stage 정의는 hqs/development/stages/를 참조(ADR-0001, ADR-0008)" |
| ADR-0006(Development HQ, Structure v1 Migration) | `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`(255행) | **확인됨** — ADR 표 행에 명시 인용 |
| ADR-0007(Development HQ, Baseline Relocation) | 동일 파일(255행) | **확인됨** |
| ADR-0008(Development HQ, Stage 폴더 공존) | `hqs/development/STRUCTURE.md`(17~19행), `hqs/development/HANDOVER.md` | **확인됨** |
| ADR-0009(Development HQ, Stage Data Contract) | `hqs/development/BASELINE.md` §"Stage Data Contract (ADR-0009)"(40행) | **확인됨** |
| ADR-0016(Kernel, OmniRoute Freeze Relaxation) | `hqs/development/IMPLEMENTATION_RULES.md`(50행) | **확인됨** |
| ADR-0017(Kernel, OmniRoute Production Adoption) | `docs/architecture/baseline/BASELINE.md` §"Engine 호출 책임"(386·826·828행) | **확인됨** |
| ADR-0018(Kernel, LangGraph Final Review) | `docs/architecture/baseline/BASELINE.md`(1365행, 1회 인용) | **확인됨** — Not Adopted 판정이므로 신규 Baseline 절 자체가 없는 것이 정상 |
| ADR-0020(Kernel, Graphify Adoption) | `.claude/docs/integrations/graphify.md`(66·72행) | **확인됨** — 문서 자신이 "BASELINE.md는 전혀 수정되지 않았다"고 명시, 미반영이 설계대로임을 확인 |
| ADR-0024(Kernel, Multi-Engine Adoption) | `hqs/development/IMPLEMENTATION_RULES.md` §"Multi-Engine Architecture 허용 범위 (Scoped, ADR-0024)"(54~81행) | **확인됨** |
| ADR-0025(Kernel, Stage05 Parallel Validation) | `projects/stage05-parallel-validation-harness-v1/README.md`(5·60행) | **확인됨**(Scoped 범위 내 — Production Adoption 자체는 여전히 NOT YET DETERMINED, 그 부분은 확정하지 않음) |
| ADR-0026(Kernel, OpenRouter Free Model Selection) | `hqs/development/mvp/openrouter_engine.py`(실제 코드), `tests/test_openrouter_engine.py` | **확인됨**(Scoped 범위 내) |
| ADR-0027(Kernel, OpenRouter Production Migration) | 동일 코드 | **확인됨**(Scoped 범위 내) |
| ADR-0028(Kernel, Python Audit Governance) | `docs/research/PYTHON-AUDIT-WAVE-0~5-*.md`(6건), 대응 커밋 `793714a`·`ce71a46` 등 | **표기 최신성 불일치 발견** — ADR 상태 필드는 "Wave 실행 NOT YET AUTHORIZED"이나 실제로는 Wave 0~5 실행 기록이 존재. 개별 Wave 승인 여부는 파일만으로 확인 불가 — **확정하지 않고 `OD-0002`로 등록**(아래) |

`docs/decisions/adr.md`의 위 13개 행(ADR-0001·0006~0009·0016~0018·
0020·0024~0027)에 확인된 근거를 채워 넣었다. ADR-0028은 근거가
"확인됨"과 "불일치 발견"으로 나뉘어 행 자체는 수정하지 않고 Open
Decision(`OD-0002`)으로만 기록했다 — 확정하지 않는다는 원칙을
지켰다.

### 3. 미검토 문서 영역 — 재확인(변경 없음)

3차 라운드의 `docs/governance/adc/`(10건 등록) 및 `docs/architecture/
core/` 비-RFC/ADC/ADR 34건 분류는 이번 라운드에서 파일 존재와 분류
근거를 다시 대조했고, 변경할 사유를 찾지 못했다 — 그대로 유지한다.

### 4. 최종 검증 — 결과(4차, 누적)

Python 스크립트로 직접 재실행:

- **Front Matter YAML 파싱**: 원장 4개 전부 성공(변경 없음).
- **Document ID / (Document ID, Target Domain) 중복**: 3차와 동일 —
  단순 (ID, Domain) 기준 5건 충돌은 실제 구조 반영(버그 아님).
  **(Document ID, Target Domain, Source Path) 3중 키 기준 중복
  0건**(이번 라운드가 수정한 13개 행 포함 재검증 — `## 5. 작성 예시`
  섹션의 견본 행 1개는 실제 등록 표(`## 6. 등록 현황`)와 분리해
  집계에서 제외했다).
- **Source Path 존재 검증**: 변경된 13개 행 포함 전체 재확인 — 누락
  0건.
- **Related Documents/Evidence References 경로 존재 검증**: 이번
  라운드가 새로 추가한 인용 경로(`hqs/development/STRUCTURE.md`,
  `hqs/development/BASELINE.md`, `hqs/development/HANDOVER.md`,
  `hqs/development/IMPLEMENTATION_RULES.md`,
  `.claude/docs/integrations/graphify.md`,
  `hqs/development/mvp/openrouter_engine.py`,
  `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`,
  `projects/stage05-parallel-validation-harness-v1/README.md`,
  `docs/research/PYTHON-AUDIT-WAVE-*`·`PYTHON-REFACTOR-WAVE-*`
  6건) 전부 실제 존재 확인 — Broken Link 0건.
- **Markdown 표 컬럼 정합성**: `adr.md`·`open_decision.md` 변경된
  행 전부 12컬럼 유지 확인.
- **원본 문서의 비의도적 변경 여부**: `git status --short`/`git diff
  --stat` 확인 결과, 이번 라운드에서 수정된 파일은
  `docs/decisions/adr.md`, `docs/decisions/open_decision.md`,
  `docs/decisions/REGISTRATION-CANDIDATES-0001.md` 3개뿐 —
  Baseline 반영 확인을 위해 열람한 모든 파일(`BASELINE.md` 2종,
  `STRUCTURE.md`, `HANDOVER.md`, `IMPLEMENTATION_RULES.md`,
  `graphify.md`, `openrouter_engine.py`, `STRUCTURE-V1.0-FROZEN.md`,
  Wave 문서 6건)은 전혀 수정하지 않았다.
- **Architecture Baseline / Public Contract 변경 여부**: 없음 —
  Kernel `BASELINE.md`, Dev HQ `BASELINE.md` 둘 다 열람만 했다.

### 5. 등록 현황 요약(누적, 4차 기준)

| 구분 | 1차 | 2차 | 3차 | 4차 | 누적 |
|---|---|---|---|---|---|
| RFC | 5 | 38 | 17 | 0 | 60 |
| ADC | 5 | 40 | 16 | 0 | 61 |
| ADR | 2 | 28 | 11 | 0(13건 필드 보강만) | 41 |
| Open Decision | 0 | 0 | 1(OD-0001) | 1(OD-0002) | 2 |

### 6. 잔여 Open Issue (4차 기준, 완료로 표시하지 않음)

- **OD-0001** — Decision Group Registry(공식 `DG-NNNN`) 형식과 이
  원장의 `DG-<도메인>-NNNN` 형식 간 관계, 여전히 미결정.
- **OD-0002**(신규) — `ADR-0028` 상태 필드와 실제 Wave 0~5 실행
  기록의 표기 최신성 불일치, 개별 Wave 승인 근거는 파일 밖 확인
  필요.
- **ADR-0002~0005 교차 트리 물리 배치** — 근본 해소는 여전히 사용자
  판단 필요(제안만 유지, §1).
- **`docs/governance/DECISION-GROUP-REGISTRY.md` 신규 생성** —
  여전히 이 PR 범위 밖, OD-0001이 추적.
- 이번 라운드로 **"Baseline 반영 여부 미대조"로 분류됐던 8건은 전부
  해소**됐다(위 §2) — 남은 항목은 위 4개뿐이다.

### 7. Self Review(4차)

- 처리 가능한 항목을 후속 PR로 미뤘는가 — **아니오**. 3차가 명시적으로
  "미대조"라고 남긴 8건(ADR-0006~0009 Dev HQ, ADR-0016·0017·0020·
  0024~0027 Kernel)을 전부 이번 라운드에서 원문 대조로 마무리했다.
- 기존 파일을 이동·복사·번호 변경했는가 — **아니오**.
- Architecture Baseline을 수정했는가 — **아니오**(열람만).
- 확인되지 않은 사항을 확정했는가 — **아니오**(ADR-0028의 Wave 승인
  여부는 확정하지 않고 `OD-0002`로 남김).
- 자동 추론·일괄 등록을 했는가 — **아니오**(전부 개별 grep+원문
  열람으로 확인 후 반영, 나머지는 그대로 둠).
