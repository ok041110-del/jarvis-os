# PR #214 Open Issues 검증 — Issue 1·2 (읽기 전용 감사 + 안전 수정)

## 0. 목적과 범위

기준 커밋: 브랜치 `claude/decision-ledger-registration-74a9a1` HEAD
(`358fc36`), base `origin/main`(`94c47762`).

PR #214("RFC/ADC/ADR 통합 원장 및 결정 문서 구조 정규화")의 남은 후속
검토 항목 중 다음 두 건을 검증한다.

1. RFC/ADC/ADR 통합 원장(`docs/decisions/rfc.md`/`adc.md`/`adr.md`) 전체
   행의 Source Path 단위 중복·오류 검증.
2. `RFC-0042`(`docs/architecture/core/RFC-0042-repository-wide-python-
   audit-and-refactoring-governance.md`)에 남은 미확인 경로 2건 재조사.

교차 트리 ADR-0002~0005 물리 배치 문제(원래의 세 번째 항목)는 별도
문서(`docs/research/ADR-0002-0005-CROSS-TREE-PLACEMENT-DECISION-
PROPOSAL-0001.md`)로 분리해 다룬다 — 이 문서는 그 문제를 인용만 한다.

이 문서는 검증 기록이며, 기존 결정·Status·Evidence·내부 label을
변경하지 않는다. RFC-0042 본문에 가한 유일한 수정(§2.2)은 원문이
이미 인용한 경로 중 확인 결과가 명확한 경로 오류를 정정한 것으로,
RFC-0042의 결론·Evidence·section label은 변경하지 않았다.

## 1. Issue 1 — 원장 3종 Source Path 행 단위 검증

### 1.1 방법

`docs/decisions/rfc.md`/`adc.md`/`adr.md`의 "§6(또는 §5) 등록 현황"
표만 파싱했다(각 문서의 "§5 작성 예시" 절은 실제 등록이 아니라
문서 자신이 명시한 illustrative 예시이므로 검증 대상에서 제외 — 이
구분 없이 기계적으로 스캔하면 RFC-0007/ADR-0006이 "중복 등록"으로
오탐지된다는 것을 먼저 확인했다). 검증 항목:

1. Source Path 중복 등록(동일 Source Path가 두 번 이상 등록됐는가)
2. Document ID + Target Domain은 같지만 Source Path가 다른 행(교차
   트리 패턴 — 오류가 아니라 정상 패턴인지 확인)
3. Source Path가 가리키는 파일이 실제로 존재하는가
4. Document ID와 Source Path 파일명이 실제로 일치하는가
5. Parent/Related Documents 셀에 포함된 개별 경로가 실제로 존재하는가

### 1.2 결과

| 항목 | RFC 원장 | ADC 원장 | ADR 원장 |
|---|---|---|---|
| 등록 행 수(§5 예시 제외) | 60 | 61 | 41 |
| Source Path 중복 등록(진짜 오류) | **0건** | **0건** | **0건** |
| ID+Domain 동일·Source Path 상이(교차 트리) | 0건 | 0건 | **4건**(ADR-0002~0005, Kernel) |
| Source Path 파일 미존재 | **0건**(162행 전부 실존 확인) | | |
| Document ID·파일명 불일치 | **0건** | | |

**Source Path 중복 등록은 세 원장 어디에도 없다.** 처음 스캔에서
RFC-0007(`rfc.md`)과 ADR-0006(`adr.md`)이 동일 Source Path로 두 번
등장하는 것으로 보였으나, 대조 결과 하나는 "§5 작성 예시" 절의
illustrative 예시 행(각 원장 §5가 "다음은 이미 존재하는 RFC-0007을
이 원장 형식으로 표현한 예시다"라고 스스로 명시)이고 다른 하나는
"§6 등록 현황"의 실제 등록 행이다 — 두 행의 Status/Parent Documents
문구도 서로 달라(예시는 단순화된 형태) 실제 중복 등록이 아니라
문서 구조상 예정된 재사용임을 확인했다.

`adr.md`의 ADR-0002~0005(Kernel Target Domain)는 Document ID +
Target Domain은 같지만 Source Path가 서로 다른 두 개의 물리적으로
분리된 문서 쌍이다(예: `docs/architecture/core/ADR-0002-execution-
layer-module-baseline.md` vs `docs/decisions/adr/ADR-0002-core-to-
kernel-terminology-unification.md`). 이는 `adr.md` 자신이 §Note와
각 행의 Status 셀에서 "교차 트리"로 이미 명시적으로 구분해 등록한
**정상적인 참조 분리 패턴**(위 분류 기준 b)이며, 새로 발견된 오류가
아니다 — `docs/decisions/REGISTRATION-CANDIDATES-0001.md` §"교차 트리
ADR 배치 문제"가 이미 동일 결론에 도달해 있었고, 이번 재검증으로
확인 결과가 변경되지 않았다. 근본적인 물리 배치 문제 자체(파일을
옮길지 여부)는 별도 Decision Proposal 문서로 넘긴다(§Issue 3 참조).

Parent/Related Documents 셀에서 발견된 것은 전부 정상 축약 표기였다
— 예: `adr.md`의 여러 행에 등장하는 `GLOSSARY.md`(정식 경로
`docs/00_governance/GLOSSARY.md`, 같은 셀 안에서 `BASELINE.md` 전체
경로 뒤에 이어지는 축약형), ADR-0021 행의 `CONTEXT.md`(`RESPONSIBILITY.md`와
같은 디렉터리를 가리키는 축약형), ADR-0026 행의
`tests/test_openrouter_engine.py`(직전에 언급된
`hqs/development/mvp/openrouter_engine.py`의 형제 경로) — 전부 실제
파일이 존재하며, 문장 안에서 이미 전체 경로가 함께 언급된 뒤의 구어체
축약이다. 별도 수정을 하지 않았다(원문 표현 변경은 최소 범위 수정
원칙에 위배되며, 의미가 명확한 축약 표기를 "오류"로 취급해 임의로
바꾸는 것이 오히려 더 큰 리스크다).

### 1.3 결론

**Issue 1 상태: Verified — 결함 없음.** 세 원장 전체 162행에 대해
Source Path 중복 등록, 파일 부재, ID·파일명 불일치를 전수 검증했고
어느 것도 발견하지 못했다. 원장 파일 자체에는 수정을 가하지 않았다
(수정할 오류가 없었기 때문).

## 2. Issue 2 — RFC-0042 미확인 경로 2건 재조사

### 2.1 대상

`RFC-0042`의 "### Related Documents" 절(Batch 5 소배치 E 구조 보존
작업 당시, 원문 "## Related" 목록을 그대로 이관하면서 다음 두 경로를
존재 확인 실패로 인해 미수정 상태로 남겼음):

1. `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`
2. `docs/architecture/core/ADR-0006-structure-v1-migration.md`

### 2.2 조사 방법과 결과

`git log --all --diff-filter=A`로 저장소 전체 히스토리(모든 브랜치
포함)에서 두 파일명을 검색했다.

**(1) `ARCHIVE-CLEANUP-REVALIDATION-0001.md`** — 커밋
`e54e27f`("docs(research): Archive Cleanup DEFER 재검증")에서
`docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`로 실제 생성된
것을 확인했다. 그러나 이 커밋은 `origin/main`의 조상이 아니며, 이
PR의 브랜치(`claude/decision-ledger-registration-74a9a1`)에도 없다
— `git branch -a --contains e54e27f` 결과 유일하게 포함하는 브랜치는
`origin/claude/jarvis-archive-cleanup-snro5w`(별도의, 이 PR과
무관한 미병합 브랜치)뿐이다. 해당 브랜치의 파일 내용을 직접 읽어
확인한 결과, RFC-0042가 인용하려는 맥락(archive/projects 파일 보존
판단 선례)과 실제로 일치하는 문서다 — `STAGE-TO-TEAM-MIGRATION-
ARCHIVE-CLEANUP-INVESTIGATION-0001.md`의 DEFER 2건을 재검증해 "정리
불가, KEEP 유지"로 확정한 문서였다.

**결론**: 이 경로가 가리키는 문서는 실존하며 RFC-0042의 인용 의도와
정확히 일치하지만, main과 이 PR의 어느 시점에도 병합된 적이 없다.
그 브랜치를 병합할지 여부는 RFC-0042 또는 이 검증 작업의 판단 범위
밖이다(별도 Governance/사용자 결정 대상). RFC-0042 원문의 해당
citation은 **수정하지 않고 그대로 유지**했다(대응 파일이 실제로
"이 저장소의 main/현재 브랜치"에는 없으므로, 있지도 않은 경로로
바꿔치기하는 것이 오히려 fabrication이 된다) — 대신 미병합 상태임을
명시하는 각주를 추가했다(RFC-0042 §Related Documents 참조).

**상태 요약**:

| 항목 | 값 |
|---|---|
| Current repository presence | Not present(main/이 브랜치 어디에도 없음) |
| Historical/alternate branch presence | Verified(`origin/claude/jarvis-archive-cleanup-snro5w`, 커밋 `e54e27f`) |
| Merge status | Not merged |
| Required action | Separate decision(이 브랜치를 병합할지 여부는 별도 사용자/Governance 판단) |

**(2) `ADR-0006-structure-v1-migration.md`** — Batch 5 소배치 E
작업 당시 `docs/architecture/core/ADR-0006-structure-v1-migration.md`
경로로 존재 확인을 시도해 실패(`MISSING`)로 기록했었다. 이번
재조사에서 `git rev-list --all | xargs git ls-tree -r --name-only`로
전체 히스토리의 모든 파일 경로를 스캔한 결과, 이 파일은
**`docs/decisions/adr/ADR-0006-structure-v1-migration.md`**로 존재하며,
**현재 main과 이 PR 브랜치 working tree에 실제로 존재한다**(`ls -la`로
직접 확인). 이전 조사가 실패한 원인은 파일이 없어서가 아니라 잘못된
디렉터리(`docs/architecture/core/`)를 검색했기 때문이었다 — 실제
Kernel Structure v1.0 Migration을 확정한 이 ADR-0006은 `docs/decisions/
adr/` 트리(당시 `docs/04_adr/`에서 Structure v1.0 Migration으로
재배치된 경로)에 물리적으로 위치한다.

**결론**: 원문 citation의 오류(디렉터리 오기재)가 이번 재조사로
확정 확인됐다. RFC-0042 본문의 이 한 줄만 실제 경로로 정정했다
— "(원문은 `docs/architecture/core/ADR-0006-structure-v1-migration.md`로
인용 — 후속 검증으로 실제 경로 확인)" 주석을 남겨, 원문이 원래
무엇을 썼는지와 무엇으로 정정됐는지를 모두 추적 가능하게 했다(이번
세션 전체에서 일관되게 적용한 경로 정정 패턴과 동일).

### 2.3 RFC-0042 본문 변경 사항 (diff 요약)

| 위치 | 변경 전 | 변경 후 | 근거 |
|---|---|---|---|
| §Related Documents, `ADR-0006` 행 | `docs/architecture/core/ADR-0006-structure-v1-migration.md`(archive/ 제외 근거) | `docs/decisions/adr/ADR-0006-structure-v1-migration.md`(원문은 ...로 인용 — 후속 검증으로 실제 경로 확인, archive/ 제외 근거) | 실제 파일 위치 확인(§2.2-2) |
| §Related Documents, `ARCHIVE-CLEANUP-REVALIDATION-0001.md` 행 | 각주 없음 | 미병합 브랜치 존재 확인 각주 추가 | 존재는 확인되나 main/현재 브랜치에 없음(§2.2-1) |

RFC-0042의 Identity/Status/Decision/Evidence/section 번호·label은
전혀 변경하지 않았다. Content-lossless 재검증 결과, 이번 수정으로
"손실"된 내용은 정확히 위 표의 두 원문 문구뿐이며(그 문구를 대체한
것이 이번 수정의 목적이므로 예정된 변경), 그 외 어떤 문장도
삭제·압축되지 않았다.

### 2.4 결론

**Issue 2 상태: 부분 Resolved.**

- `ADR-0006-structure-v1-migration.md` — **Resolved**: 실제 경로
  확인 후 RFC-0042 citation 정정 완료.
- `ARCHIVE-CLEANUP-REVALIDATION-0001.md` — **Verified-Unresolved**:
  문서 실존은 확인했으나 병합 여부는 별도 결정 사항으로 남는다.
  이 파일을 만들어내거나 경로를 추측해 대체하지 않았다(지시사항
  준수).

## 3. Issue 3 참조 — ADR-0002~0005 교차 트리 배치

Issue 3(ADR-0002~0005 교차 트리 물리 배치)에 대한 조사·대안 비교·
Governance Decision은 별도 문서 `docs/research/ADR-0002-0005-CROSS-
TREE-PLACEMENT-DECISION-PROPOSAL-0001.md`에 전체 기록했다. 결정
요지: **현상 유지(Maintain Current Placement)** — 파일을 이동하지
않고, Document ID + Target Domain + Source Path 조합으로 계속
식별한다. 이 문서에서는 그 결론만 인용하며, 상세 근거는 중복
기술하지 않는다.

## 4. Architecture / Code 변경 여부

이번 검증·수정 작업(Issue 1·2·3 전체)은 다음 중 어느 것도 변경하지
않았다.

- 코드(`hqs/`, `mvp/`, `core/` 등) — 무변경
- Architecture Baseline(`docs/architecture/baseline/BASELINE.md`) — 무변경
- Kernel Public Contract — 무변경
- 기존 RFC/ADC/ADR의 Document ID/Status/Decision/Evidence/내부
  section label — 무변경(RFC-0042의 Related Documents 경로 문구
  2곳만 정정, §2.3 diff 요약 참조)
- ADC-0019 — 무변경(zero-diff, §5 재확인)

## 5. 검증 기준 재확인

- [x] 원장 3종 전체 행(162개) Source Path 실존 확인
- [x] 원장 3종 전체 행 Source Path 중복 등록 여부 확인(0건)
- [x] Document ID·파일명 불일치 확인(0건)
- [x] RFC-0042 미확인 경로 2건 전체 히스토리 검색(모든 브랜치 포함)
- [x] 확인된 경로만 정정, 미확인 상태는 추측하지 않고 그대로 기록
- [x] ADC-0019 무변경 확인(이 검증/수정 작업으로 diff 없음)

## 6. 후속 결정이 필요한 조건

- `ARCHIVE-CLEANUP-REVALIDATION-0001.md`가 있는
  `origin/claude/jarvis-archive-cleanup-snro5w` 브랜치를 main에
  병합할지 여부 — 별도 사용자/Governance 판단 필요.
- ADR-0002~0005 교차 트리 배치의 재검토 조건은
  `ADR-0002-0005-CROSS-TREE-PLACEMENT-DECISION-PROPOSAL-0001.md`
  §8(Reconsideration Conditions)에 기록했다.
