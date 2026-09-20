# RFC Role 경계 검토 — `## Decision` 절 사용 실태 (Issue #206 후속)

**문서 성격**: READ-ONLY 검토. 이 문서는 `RFC-0007`,
`RFC-0009`/`RFC-0010`/`RFC-0011`, `RFC-0031`/`RFC-0032` 중 어느
파일도 수정하지 않는다. 발견된 문제의 수정 여부는 이 문서가 결정하지
않고 §4 "판단"에서 후속 작업으로 분리한다(사용자 지시).

## 1. 배경

Issue #206 §4는 RFC가 "problem, context, questions, scope, requested
review; no final decision"만 다뤄야 한다고 요구한다. 저장소 전수
검토(이전 Main Branch Full Validation 세션) 결과, `## Decision`이라는
제목을 본문에 직접 포함한 RFC 6건이 발견되었다 — 이 문서는 각 건이
실제로 "RFC 스스로 최종 결정을 내리는" 역할 위반인지, 아니면 "후속
ADC/ADR 판정을 인용만 하는" 상태 기록인지 원문을 직접 대조해
재확인한다.

## 2. 개별 확인 결과

### 2.1 `RFC-0007-ast-context-build-integration.md`(원문 175~189행)

- 문서 헤더: `**Status**: Proposed (검토 대상, 결정 아님)`(원문 3행).
- 그러나 175행의 `## Decision` 절은 다음과 같이 **RFC 자신이** 최종
  판정을 내린다: `"**B. CONDITIONAL** — Production 통합의 방향성...
  Evidence로 충분히 뒷받침된다. 그러나 다음 두 선행조건이 해결되지
  않은 상태에서 통합을 진행하는 것은 권장하지 않는다"`(176~178행).
- 이 절 어디에도 "후속 ADC의 판정을 인용한다"는 문구가 없다 — 오히려
  RFC 자신의 근거(Evidence 충분성 평가)와 자신의 조건(선행조건 2개)을
  직접 제시한다.
- **사실 관계 확인**: `docs/governance/adc/ADC-0005.md`("RFC-0007
  후속")가 실제로 존재하며, RFC-0007의 재평가 문서(`docs/research/
  DEV-HQ-V2.0-RFC-0007-REVALIDATION-0001.md`)가 제시한 결정 후보
  4건을 ADC-0005가 개별적으로 Accept/Reject/Defer 판정했다(ADC-0005
  원문 1~20행 확인). 즉 **실제 최종 결정은 ADC-0005 경로로 정상
  진행**됐으나, RFC-0007 파일 자체에는 여전히 "RFC가 스스로 내린
  것처럼 보이는" `## Decision` 절이 남아 있다.
- **결론**: RFC-0007의 `## Decision` 절은 (a) 후속 ADC 판정을
  인용하지 않고, (b) 자신의 Status 필드("결정 아님")와 문면상
  충돌하며, (c) 실제 Governance 흐름(ADC-0005가 최종 판단)과도
  어긋나는 서술이다. **RFC 역할 원칙과 충돌 — 확인됨.**

### 2.2 `RFC-0009-stage-data-contract.md`(원문 230~234행)

`## Decision`은 `"후보 C — 분리 승격... 채택한다. B-1/B-2/B-3
Decision과 §3의 Public/Hidden 경계를 **후속 ADC의 판정 대상으로
제출한다** — 결과는 docs/governance/adc/ADC-0007.md(Scoped Accept),
후속 반영은 docs/decisions/adr/ADR-0009-...md"`로 명시한다. RFC가
스스로 결정을 내리지 않고 ADC/ADR 경로로 **제출·인용**하는 형태 —
**역할 위반 아님**, 제목("Decision")만 봤을 때 오인 가능성이 있는
naming 이슈로 한정.

### 2.3 `RFC-0010-outcome-oriented-governance-model.md`(원문 141~150행)

`## Decision`은 `"Scoped Accept — docs/governance/adc/ADC-0008.md
판정을 그대로 따른다"`로 시작한다. ADC 판정을 그대로 인용 — **역할
위반 아님**, 동일한 naming 이슈.

### 2.4 `RFC-0011-implementation-freedom-principle.md`(원문 139~148행)

`## Decision`은 `"Scoped Accept — docs/governance/adc/ADC-0009.md
판정을 그대로 따른다"`로 시작한다. 동일 패턴 — **역할 위반 아님**,
동일한 naming 이슈.

### 2.5 `docs/architecture/core/RFC-0031-langgraph-implementation-technology-adoption.md`(원문 137~144행)

`## Decision`은 `"Accept (Conditional·Non-Mandatory) —
docs/architecture/core/ADC-0034-...md 판정을 그대로 따른다"`로
시작한다. 동일 패턴 — **역할 위반 아님**.

### 2.6 `docs/architecture/core/RFC-0032-graphify-implementation-technology-adoption.md`(원문 115~123행)

`## Decision`은 `"Accept (Conditional·Non-Mandatory, Architecture
무연동) — docs/architecture/core/ADC-0035-...md 판정을 그대로
따른다"`로 시작한다. 동일 패턴 — **역할 위반 아님**.

## 3. 요약

| RFC | `## Decision` 내용 | ADC 판정 인용 여부 | 역할 위반 |
|---|---|---|---|
| RFC-0007 | RFC 자신의 Evidence 평가 + 선행조건 2개 직접 제시 | **없음** | **예 — 확인됨** |
| RFC-0009 | ADC-0007 제출/인용 | 있음 | 아니오(naming만) |
| RFC-0010 | ADC-0008 판정 인용 | 있음 | 아니오(naming만) |
| RFC-0011 | ADC-0009 판정 인용 | 있음 | 아니오(naming만) |
| RFC-0031 | ADC-0034 판정 인용 | 있음 | 아니오(naming만) |
| RFC-0032 | ADC-0035 판정 인용 | 있음 | 아니오(naming만) |

RFC-0009/0010/0011/0031/0032의 `## Decision`은 실질적으로 "ADC/ADR이
이미 내린 결정을 RFC 파일에 사후 인용·기록"하는 상태 업데이트이며,
Issue #206이 금지하는 "RFC가 최종 결정을 포함"하는 경우에 해당하지
않는다 — 제목 표기("Decision")가 RFC-TEMPLATE.md(PR #207)이 권장하는
중립적 표현과 다를 뿐, 내용은 원칙을 지킨다. **RFC-0007만 유일하게
실질적 역할 위반이다.**

## 4. 판단 — 수정 여부

**이번 세션에서 RFC-0007을 포함한 어떤 파일도 직접 수정하지 않는다.**
근거:

1. 사용자 지시("기존 문서 직접 수정은 근거와 영향 범위를 먼저
   확인하고, 필요하면 별도 후속 작업으로 분리")에 따라, 이 문서는
   근거(§2.1)와 영향 범위(§3)를 확인하는 단계까지만 수행한다.
2. RFC-0007은 이미 ADC-0005로 최종 판정이 내려진 **Resolved 상태의
   과거 기록**이다. Issue #206 §7("근거 없는 임의 수정 금지")과
   CLAUDE.md의 "실패한 검증을 성공으로 표현하지 않음"을 함께
   고려하면, "역할 위반이 확인됐다"는 사실은 기록해야 하지만, 실제
   파일 수정(`## Decision` 절을 삭제하거나 "## Status(ADC-0005 인용)"
   등으로 재작성)은 **다음 두 가지를 먼저 확정해야 안전하다**:
   - (a) RFC-0007의 `## Decision` 절이 다른 문서(ADC-0005, HANDOVER.md
     등)에서 근거로 재인용되고 있는지 전수 확인(현재 문서는 §2.1에서
     ADC-0005 존재만 확인했고, 인용 관계의 전수 조사는 하지 않음).
   - (b) 수정 방식을 "삭제"로 할지 "ADC-0005 인용으로 재작성"할지는
     RFC-TEMPLATE.md(PR #207)이 정한 신규 형식과의 정합성을 별도로
     검토해야 한다 — 과거 문서를 신규 템플릿에 맞춰 고치는 것은
     PR #207 자체가 "이번 범위에 포함하지 않음"이라고 명시한 "기존
     문서 마이그레이션"에 해당할 수 있다.
3. 따라서 **후속 작업으로 분리한다**: "RFC-0007 `## Decision` 절을
   ADC-0005 인용 형태로 재작성할지 여부"를 별도 Task/Issue로 열어
   사용자 승인을 받은 뒤 진행할 것을 권고한다. 이 문서는 그 판단에
   필요한 근거(§2, §3)를 제공하는 것으로 역할을 한정한다.
4. RFC-0009/0010/0011/0031/0032는 역할 위반이 아니므로 수정 대상이
   아니다 — naming 통일(예: "## Decision" → "## Status (ADC 판정
   인용)")은 선택 사항으로만 기록하고 실행하지 않는다.

## Architecture / Public Contract 영향

- Architecture 변경: **No** — 이 문서는 어떤 파일도 수정하지 않는다.
- Public Contract 변경: **No**.

## 검증 방법

- `grep -n "^## Decision"`으로 6개 RFC 파일 전수 확인.
- 각 파일의 `## Decision` 절 본문을 직접 열람해 "ADC/ADR 판정 인용"
  문구 유무를 확인.
- `docs/governance/adc/ADC-0005.md` 원문을 열람해 RFC-0007과의 실제
  후속 관계(Accept/Reject/Defer 4건 판정)를 확인.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0007-ast-context-build-integration.md` | 역할 위반 확인 대상(원문 미수정) |
| ADC | `docs/governance/adc/ADC-0005.md` | RFC-0007의 실제 최종 판정 문서 |
| Issue | #206 | 이 검토가 응답하는 상위 요청 |
| Template | `docs/decisions/rfc/RFC-TEMPLATE.md` | 신규 RFC의 역할 경계 기준(PR #207) |
