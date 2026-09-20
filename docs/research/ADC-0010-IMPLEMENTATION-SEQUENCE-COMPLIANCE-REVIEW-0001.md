# ADC-0010 후속 구현 순서 준수 여부 검토 (Issue #206 후속)

**문서 성격**: READ-ONLY 검토. `docs/governance/adc/ADC-0010-decision-
group-identifier-scheme.md`, `docs/governance/DECISION-GROUP-REGISTRY.md`
원문은 이 문서가 수정하지 않는다. ADC-0010의 Decision(Scoped Accept)과
Architecture/Public Contract 판단(둘 다 No)도 소급 변경하지 않는다 —
이 문서는 그 결정의 **실행 순서**만 별도로 기록한다.

## 1. 배경

`ADC-0010` §"종합 Decision"(원문 181행)은 `docs/governance/
DECISION-GROUP-REGISTRY.md` 신규 생성을 "이 ADC는 수행하지 않음 —
후속 구현 작업(아래)으로 지정"이라고 명시하고, §"후속 구현 작업
목록"(원문 199~214행)은 4개 항목을 나열한 뒤 다음과 같이 못박는다.

> "이 4개 항목 중 어느 것도 이번 ADC가 직접 실행하지 않는다 —
> Governance 승인 이후 별도 구현 세션에서 순서대로 진행한다."

## 2. 실제 실행 순서 (Git 이력 직접 확인)

PR #208(`claude/rfc-adc-adr-id-unification` → `main`)의 커밋 이력을
`git log --oneline`으로 확인한 결과:

| 순서 | Commit | 시각(UTC) | 내용 |
|---|---|---|---|
| 1 | `83cddb5` | — | RFC/ADC/ADR 식별자 통일 가능성 조사 |
| 2 | `2b13de9` | 2026-09-20 02:57:40 | **ADC-0010 작성**(Scoped Accept, 후속 구현 작업 목록 확정) |
| 3 | `8481d81` | 2026-09-20 03:04:09 | **Decision Group Registry 최초 구현 및 2개 그룹 등록**(후속 구현 작업 1·2번) |
| 4 | `2ac472b` | — | Registry 커버리지 검증 보고서 |
| 5 | `6b00856` | — | RFC-0008/ADC-0006 재검증 보고서 |

PR #208은 위 5개 커밋을 **하나의 PR로 묶어** `2026-09-20 03:43:12
(UTC, PR API 기준 `merged_at`)`에 저장소 소유자(`ok041110-del`)가
병합했다.

**확인된 사실**:

- Commit 2(ADC-0010 작성)와 Commit 3(Registry 구현) 사이의 시간 간격은
  **약 6분 29초**다.
- 이 6분 29초 동안 별도의 Governance 승인 이벤트(예: PR 리뷰 코멘트,
  Merge, 사용자의 명시적 승인 메시지)가 기록된 근거는 찾지 못했다 —
  PR 자체의 Merge는 이보다 약 39분 뒤(`03:43:12`)에 일어났다.
- Commit 2와 Commit 3은 **동일 세션, 동일 PR, 동일 브랜치**에서
  이어졌다 — ADC-0010이 예고한 "별도 구현 세션"이 아니다.

**결론**: ADC-0010 원문이 스스로 정한 절차("Governance 승인 이후
별도 구현 세션에서 진행")와 실제 실행 순서(같은 세션에서 6분 29초
뒤 즉시 구현, PR 병합보다도 먼저 구현 완료)는 **일치하지 않는다**.
이는 이번 검증에서 새로 발견된 사실이며, 이전 Main Branch Full
Validation 세션에서 이미 medium 심각도로 보고된 항목이다.

## 3. 이 불일치가 Architecture/Baseline 판단에 영향을 주는가

**영향 없음 — 아래 근거로 판단을 유지한다.**

1. ADC-0010이 승인한 대상(Decision Group 개념, Registry 문서 신설)은
   **문서 색인 추가일 뿐 Kernel/Execution Layer의 구조나 Contract를
   전혀 변경하지 않는다** — ADC-0010 §"Architecture 및 Public Contract
   영향"의 "Architecture 변경: No, Public Contract 변경: No" 판단은
   Registry 구현 이후 실제 diff(`docs/governance/DECISION-GROUP-
   REGISTRY.md` 등 문서 5개 신규 추가만, 기존 파일 0개 수정 — 이전
   Main Branch Full Validation 세션에서 `git diff --name-status`로
   직접 확인됨)와 여전히 일치한다.
2. Registry 자체가 "기존 RFC/ADC/ADR 파일은 전혀 수정하지 않는다"는
   원칙을 지켰음을 이전 검증(문서 링크·ID 전수 재확인)이 이미
   확인했다 — 순서 위반이 내용상 위험한 결과(예: 근거 없는 재번호,
   Baseline 소급 수정)로 이어지지는 않았다.
3. PR #208은 저장소 소유자가 5개 커밋 전체를 하나의 단위로 검토·병합
   했다 — 즉 "ADC 작성"과 "구현"이 사람의 최종 승인(Merge) 시점
   기준으로는 결과적으로 함께 승인되었다. 다만 이것이 ADC-0010 원문이
   명시한 "승인 → 별도 세션" **순서**를 사후에 소급 정당화하지는
   않는다 — 그 문구 자체는 실행 당시 지켜지지 않았다는 사실은
   변하지 않는다(§2).

## 4. 판단

**문서 수정 여부**: ADC-0010 원문(Decision, 후속 구현 작업 목록,
Architecture 판단)은 **수정하지 않는다.** 근거:

- 사용자 지시("기존 Architecture 결론과 문서 이력을 소급 변경하지
  말 것")에 따라, 이미 병합되어 Governance 기록으로 확정된 ADC의
  결정문·서술을 사후에 고쳐 쓰는 것은 "결정 당시 실제로 그렇게
  기술했다"는 이력 자체를 지우는 결과가 되어 오히려 추적성을
  해친다.
- ADC-0010의 **결론**(Scoped Accept, Architecture/Contract 영향 No)은
  §3에서 확인했듯 여전히 유효하다 — 정정이 필요한 것은 "실행 순서
  서술"이지 "결정 내용"이 아니다.

**별도 Governance 기록 필요 여부**: **필요 — 이 문서로 기록한다.**
근거:

- Issue #206 §7("근거 없는 임의 수정 금지")과 CLAUDE.md의 "실패한
  검증을 성공으로 표현하지 않음" 원칙에 따라, 발견된 절차 불일치를
  기록 없이 넘어가는 것은 다음에 동일한 패턴(ADC 작성 직후 같은
  세션에서 "후속 작업"이라 부른 일을 즉시 실행)이 반복될 위험을
  방치하는 것과 같다.
- 이 문서는 `docs/research/`에 Issue #206 후속 조사·검증 문서들
  (`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`,
  `DECISION-GROUP-REGISTRY-COVERAGE-VERIFICATION-0001.md`,
  `RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001.md`)와 같은 위치·
  형식으로 추가되어, 기존 Governance 문서 계층 구조를 그대로
  따른다.

## 5. 권고 (실행하지 않음 — 기록만)

1. 향후 ADC가 "후속 구현은 별도 세션/승인 이후에 진행한다"와 같은
   구체적 절차를 스스로 명시할 경우, 같은 작업 세션 내에서 그
   "후속 구현"을 이어서 수행하지 않는다 — 부득이하게 같은 세션에서
   진행해야 한다면 ADC 본문의 해당 문구를 사실에 맞게(예: "이 ADC와
   동일 세션에서 이어서 구현한다") 함께 수정한 뒤 진행한다.
2. Architecture/Baseline에 영향이 없는 순수 문서 색인 성격의 ADC라도,
   "승인 이후 진행"을 명시했다면 그 승인은 최소한 PR Merge 시점
   이후로 미루는 것을 권고한다(이번 사례처럼 Merge보다 구현이 먼저
   끝나는 순서를 피한다).
3. 이 권고는 새로운 규칙 제정이 아니라 기존 CLAUDE.md Branch
   Strategy/Completion Standard의 적용 사례 기록이므로, 별도 RFC/ADC를
   요구하지 않는다.

## Architecture / Public Contract 영향

- Architecture 변경: **No** — 이 문서 자체는 아무 파일도 수정하지
  않으며, §3에서 확인한 ADC-0010의 기존 판단(No/No)도 유지된다.
- Public Contract 변경: **No**.

## 검증 방법

- `git log --oneline <base>..<PR#208 head>`로 커밋 순서 확인.
- `git show -s --format="%H %ai"`로 커밋 2·3의 정확한 타임스탬프 확인
  (간격 6분 29초).
- GitHub PR #208 API 응답의 `merged_at`(`2026-09-20T03:43:18Z`,
  Registry 구현 커밋보다 약 39분 뒤)과 비교.
- `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`,
  `docs/governance/DECISION-GROUP-REGISTRY.md` 원문 직접 대조.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| ADC | `docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md` | 검토 대상(원문 미수정) |
| Implementation | `docs/governance/DECISION-GROUP-REGISTRY.md` | ADC-0010 후속 구현 작업 1·2번 산출물 |
| Issue | #206 | 이 검토가 응답하는 상위 요청 |
| PR | #208 | 검토 대상 실행 순서가 발생한 PR |
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 같은 PR의 선행 조사 문서 |
