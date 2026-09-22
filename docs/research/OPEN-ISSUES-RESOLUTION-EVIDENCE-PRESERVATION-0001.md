# OPEN-ISSUES-RESOLUTION-EVIDENCE-PRESERVATION-0001

## 0. 범위

PR #214 병합 이후 남은 4개 Open Issue를 처리한다. 기준: base
`origin/main`(`7485611e89a1827961485e4e22dcde9caf5fb850`), 작업 브랜치
`claude/open-issues-resolution-evidence-preservation`.

1. RFC-0003 내용 압축/삭제
2. ADC-0010 대규모 diff 검토
3. 고위험 문서(RFC-0020/RFC-0043/ADR-0011) 편집의 사용자 승인 근거 불확실성
4. Archive cleanup branch(`claude/jarvis-archive-cleanup-snro5w`) 처리

이 문서는 판단 근거와 조치 결과의 기록이며, 조치 자체(파일 수정)는
`docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md`,
`docs/research/RFC-0003-PRE-NORMALIZATION-SNAPSHOT-0001.md`,
`docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`
3개 파일에 대해서만 수행했다.

---

## 1. Issue 1 — RFC-0003 Evidence Preservation

### 1.1 방법

`git show 94c47762:docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md`
(원문, 321줄)과 `origin/main` 현재본(압축본, 70줄)을 절 단위로 전수
대조했다.

### 1.2 제거/압축된 항목 인벤토리 및 분류

| 원문 절 | 내용 | 분류 |
|---|---|---|
| Status/Author/범위 preamble | Identity & Status 표로 이동 | Meaning-preserving structural relocation |
| §0 (읽기 전 안내) | Problem&Context §Non-Goals로 압축, 문서명 5개는 그대로 보존 | Meaning-preserving summarization |
| §1 Background(조사 대상 7개 플랫폼) | Context 행으로 압축, 플랫폼명 전부 보존 | Meaning-preserving summarization |
| **§2 New Philosophy(사용자 요청 원문 인용구)** | **완전 삭제** — "요청 그대로 인용"이라고 스스로 명시한 verbatim 인용문이 어디에도 재수록되지 않음 | **Evidence loss** |
| **§3 Baseline 정합성 검토(STRUCTURE.md 직접 인용 포함)** | 결론 한 문장만 남고 STRUCTURE.md 원문 인용·근거 문단 삭제 | **Decision rationale loss** |
| §4.1 Architecture 다이어그램 2개 | 텍스트 1문장으로 압축(관계는 보존, 다이어그램 소실) | Meaning-preserving summarization |
| §4.2 Execution Layer 근거(ADC-0001/RT-0001) | Non-Goals/Alternative A-2로 이동, 핵심 사실 보존 | Meaning-preserving structural relocation |
| §5 Directory Structure(ASCII 트리) | 1문장 요약(트리 자체 소실, 핵심 사실은 보존) | Meaning-preserving summarization |
| **§6 Domain Model 표(4행, 개념 대응표)** | **표 전체 삭제**, 요약 1문장만 잔존 | **Decision rationale loss** |
| §7 Interface | Domain Model 서술에 흡수, 내용 보존 | Meaning-preserving structural relocation |
| **§8 Stage Definition 표(6행, Stage-Reference 매핑)** | **표 전체 삭제**(Stage-Reference 1:1 매핑 소실, Reference만 나열) | **Evidence loss** |
| **§9 Responsibility Catalog 표(6행)** | **표 전체 삭제**, "요청 그대로 채택"이라는 무근거 문장만 잔존 | **Evidence loss** |
| **§10 Capability Catalog 표(20행 매핑 + 관찰 문단)** | **표 전체 삭제**, Capability 명칭 12개만 나열(Responsibility 대응 관계 소실) | **Evidence loss** |
| §11 MVP 재구성 계획 표 | 1문장으로 압축, MVP 순서·재사용 대상은 보존 | Meaning-preserving summarization |
| §12 재사용 코드 표(6행) | 1문장 나열로 압축, 코드 식별자는 보존, "재사용 방식" 설명 개별 소실 | Meaning-preserving summarization |
| §13 제거 코드("없음" + 근거) | 거의 verbatim 보존 | Meaning-preserving structural relocation |
| §14 Boundary Risk | Non-Goals/Related Documents로 이동, 핵심 사실(ADC-01/03, Candidate 3·4) 보존 | Meaning-preserving structural relocation |
| Non-goals, 다음 절차 | Non-Goals 행 + Q-1~Q-4로 재라벨링(개선) | Meaning-preserving structural relocation |

### 1.3 후속 구현에 필요한 내용 식별

`docs/governance/adc/ADC-0003.md` "판단 2. Capability Catalog 확장 채택
여부"가 원문 §10의 개별 Capability 후보명(`repository_analysis`,
`symbol_search`, `git_operations`, `documentation`,
`user_story_authoring` 등)을 직접 인용해 Defer 판단의 근거로 삼고 있음을
확인했다(`grep -n` 재확인, §4 참조). 즉 §6/§8/§9/§10의 표는 단순
장식이 아니라 **차기 Development HQ Capability 확장 논의(Q-2 재상정
시)에 실제로 필요한 근거 자료**다.

### 1.4 조치

- **Both를 적용**: (1) 캐노니컬 문서 `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md`를
  구조 보존형으로 재작성 — PR #214가 도입한 6-섹션 틀(Identity & Status,
  Q-1~Q-4 라벨)은 유지하면서, 위 표에서 **Evidence loss/Decision
  rationale loss로 분류된 모든 절**(New Philosophy 인용, Baseline 정합성
  근거, Domain Model 표, Stage Definition 표, Responsibility Catalog 표,
  Capability Catalog 표, Directory 구조도)을 원문 그대로 재통합했다.
  Meaning-preserving summarization으로 분류된 항목은 굳이 원상복구하지
  않고 압축본을 유지했다(정보 손실이 없다고 판단했으므로).
- (2) 원문 전체(94c47762 시점, byte-for-byte)를
  `docs/research/RFC-0003-PRE-NORMALIZATION-SNAPSHOT-0001.md`에 Provenance
  포함해 별도 보존 — 캐노니컬 문서와 경쟁하는 두 번째 권위 버전이
  아니라, 감사용 이력 자료로만 존재한다(캐노니컬 문서의 Related
  Documents가 이 스냅샷을 가리키도록 링크 추가).
- Document ID(`RFC-0003`)·Status(`Resolved`)·Related Documents(ADC-0003,
  ADR-0001)는 변경하지 않았다. Change History에 이번 조치를 기록했다.
- 부수 발견: Non-Goals 행의 `development-hq/BOUNDARY.md` 인용문 안에
  이스케이프되지 않은 리터럴 `|` 문자가 있어 표가 4열로 잘못 파싱되는
  결함을 발견했다(PR #214 압축본에 이미 존재하던 결함, 이번 작업이
  새로 만든 것이 아님). `\|`로 이스케이프해 수정했다 — 의미 변경 없음.

---

## 2. Issue 2 — ADC-0010 대규모 diff 검토

### 2.1 방법

`git show 94c47762:docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`
(원문 225줄)과 현재본(92줄)을 절 단위로 대조했다. Kernel 트리 4건
고위험 문서 검토와 동일한 카테고리를 적용했다 — "GovAdc/Governance
Hold 목록에 없다"는 이유로 안전을 가정하지 않았다(지시사항 준수).

### 2.2 발견

| 원문 항목 | 현재본 상태 | 분류 |
|---|---|---|
| §판단 1 Options 비교표(8개 평가 기준 × 3후보) | §4 Evaluation에 **3개 기준만 잔존**(가시성/분기 결정 지원/Open Decision 지원/파일명·링크 변경 범위/장기 유지보수성 **5개 삭제**) | **Decision rationale loss** |
| 각 셀의 구체적 근거 문장(예: "Open Decision 지원 — Group ID를 OD에도 선택적 부여 가능") | 삭제, "높음/낮음" 단어만 잔존 | **Decision rationale loss** |
| §종합 Decision의 후보 A/B 명시적 **Reject** 판정 + 이유 | 삭제(Evaluation의 Risk 열에서 간접 추정만 가능) | **Decision rationale loss** |
| **§Architecture 및 Public Contract 영향(Architecture 변경: No / Public Contract 변경: No / Baseline 반영: 없음)** | **섹션 전체 삭제** — 현재본 어디에도 "Public Contract"라는 단어 자체가 없음 | **Evidence loss** |
| 판단 2~5(분기 규칙/마이그레이션 전략/신규 문서 규칙/OD 처리) | "Decision 세부 내용" 절로 이동, 핵심 규칙 전부 보존 | Meaning-preserving structural relocation |
| 후속 구현 작업 목록 4건 | 거의 verbatim 보존 | Meaning-preserving structural relocation |

**커밋 자체 보고와의 불일치**: commit `34b82b6`("RFC/ADC/ADR 샘플 6건 신
템플릿 적용 및 압축")는 "결정/Evidence/Trade-off 내용 삭제 없음"이라고
기록했으나, 이번 재검증 결과 ADC-0010에서 최소 2건(Evaluation 5개 기준
삭제, Architecture/Public Contract 영향 섹션 삭제)의 실질적 손실이
확인됐다. Decision 자체(Scoped Accept, 후보 C 채택)는 바뀌지 않았다.

### 2.3 조치

`docs/governance/adc/ADC-0010-decision-group-identifier-scheme.md`를
직접 수정했다(신규 파일 생성 없음 — 이 문서는 이미 Resolved 상태의
단일 캐노니컬 문서이므로 RFC-0003과 달리 별도 스냅샷 보존은 불필요하다고
판단, §1의 "Both, if necessary" 조건에서 "if necessary"에 해당하지
않음 — 손실 규모가 RFC-0003보다 작고 원문이 이 문서의 git 이력에
그대로 남아 있어 필요 시 `git show 94c47762`로 언제든 재확인 가능하기
때문).

- §4 Evaluation 표에 삭제됐던 5개 기준(가시성/분기 결정 지원/Open
  Decision 지원/파일명·링크 변경 범위/장기 유지보수성)을 원문 그대로 복원.
- §5에 "Rejected Alternatives" 행을 추가해 후보 A/B의 명시적 Reject
  판정과 이유를 복원.
- "Architecture 및 Public Contract 영향" 섹션을 원문 그대로 복원.
- Decision 자체(Scoped Accept, 후보 C 채택, Registry 설계)는 전혀
  변경하지 않았다. Status/Document ID도 무변경.
- Change History에 압축(2026-09-20)과 복원(2026-09-22) 이력을 모두
  기록했다.

---

## 3. Issue 3 — 고위험 문서 3건 편집 승인 근거

### 3.1 방법

`git log`로 `241cec7`(HIGH-RISK 검토 보고서 작성) → `afe92ed`(RFC-0020/
RFC-0043/ADR-0011 실제 편집) 두 커밋의 순서와 커밋 메시지 전문을
확인했다. 두 커밋 사이에 별도의 승인 커밋·PR 코멘트·머지 등 git
이력상 확인 가능한 승인 기록은 없다.

### 3.2 결과

**분류: Not verifiable from repository evidence.**

- `241cec7`은 "편집 전 사용자 승인을 받은 뒤 진행할 것을 권장"이라고
  명시했다.
- `afe92ed`은 "HIGH-RISK...REVIEW-0001.md의 권고에 따라... 정렬했다"고만
  기록했을 뿐, 승인이 실제로 이루어졌다는 근거(승인자, 승인 시각, 승인
  문구)를 커밋 메시지·PR 메타데이터 어디에도 남기지 않았다.
- git 이력은 대화(세션) 수준의 사용자 승인을 기록하지 않으므로, 이
  결과는 "승인이 없었다"는 증거가 아니라 **"git만으로는 확인할 수
  없다"**는 뜻이다(지시사항 §C "Important" 준수).

### 3.3 조치

- 이 3개 문서(RFC-0020/RFC-0043/ADR-0011)는 **수정하지 않았다** —
  편집 내용 자체는 별도 검증(2026-09-21 Stability Review, 본 문서
  §3.4 재확인)에서 Q-A~Q-J·Option 라벨 등이 전부 verbatim 보존된
  구조 보존형 재배치임을 이미 확인했으므로, 승인 근거 불확실성을
  이유로 되돌리지 않는다(지시사항 명시 사항).
- 이 불확실성은 "역사적 절차 한계"로만 기록하며, 승인이 없었다는
  주장으로 취급하지 않는다.

### 3.4 재확인(내용 안전성, 참고)

`grep -c "Q-A\|Q-B\|...` 로 RFC-0020의 Q-A~Q-J 라벨이 현재본에 23회
매치되어 삭제 없이 잔존함을 재확인했다(2026-09-21 검토와 동일 결과).
이 재확인은 "승인 여부"와 무관하며, 순수 내용 무결성 확인이다.

---

## 4. Issue 4 — Archive Cleanup Branch 처리

### 4.1 확인된 사실

| 항목 | 결과 |
|---|---|
| 브랜치 존재 | `origin/claude/jarvis-archive-cleanup-snro5w` 존재 확인(`git ls-remote`) |
| 커밋 `e54e27f` | 존재 확인(`git cat-file -t` → `commit`) |
| Merge-base | `9984408e0dd0431318da9c1e3bf4edd7700323b2`(현재 `origin/main`의 오래된 조상) |
| 브랜치 고유 커밋 | 1개(`e54e27f`)만 — 파일 1개(`docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`, 208줄) 추가, 코드/Architecture 변경 없음 |
| PR 존재 여부 | `list_pull_requests(head=claude/jarvis-archive-cleanup-snro5w)` 결과 **0건** — 이 브랜치로 열린 PR은 과거에도 현재도 없다 |
| main의 참조 여부 | **다수 확인** — `docs/architecture/core/RFC-0042`, `ADC-0045`, `ADR-0028`(§3.4, Accepted 상태) 3개 문서가 이 파일을 Evidence로 직접 인용 |

### 4.2 RFC-0042 의존성 재확인

`OPEN-ISSUES-PR214-VERIFICATION-0001.md` §2.2가 이미 확인한 대로,
RFC-0042의 해당 citation은 "미병합 상태" 각주와 함께 그대로
유지되어 있다. 이번 조사에서 추가로 확인한 것은 이 의존성이 RFC-0042
하나에 그치지 않는다는 점이다 — **`ADR-0028`(Accepted, 이미 Baseline에
가까운 구속력을 갖는 Python 감사/리팩토링 거버넌스 결정)이 §3.4에서
"이 문서가 KEEP으로 확정한 파일은 SIMPLIFY/REFACTOR 대상이 될 수
없다"는 **운영 중인 제약의 근거**로 이 미병합 문서를 직접 인용한다.
즉 main에는 현재 존재하지 않는 문서가, main에 있는 Accepted ADR의
실제 판정 기준으로 쓰이고 있다.

### 4.3 처분

**분류: Evidence Reference Requires Follow-up.**

`Separate Workstream / Not Blocking`이 아니라 이 분류를 선택한 이유는,
단순히 "언젠가 병합할지 결정이 필요한 별개 작업"이 아니라 **현재 main의
Accepted 거버넌스 문서(ADR-0028)가 이미 이 미병합 문서에 실제로 의존하고
있어 지금 당장의 Evidence 무결성 문제**이기 때문이다(`Requires User
Decision`에 가깝지만, 문서 자체를 지금 고칠 필요는 없고 "병합 여부"라는
단일 결정만 필요하므로 별도 분류를 유지한다).

- 이 브랜치를 병합·삭제·수정하지 않았다(지시사항 준수).
- RFC-0042를 자동으로 재작성하지 않았다.
- 존재하지 않는 PR을 만들어내지 않았다(확인 결과 그대로 기록).

### 4.4 사용자 결정이 필요한 사항

1. `origin/claude/jarvis-archive-cleanup-snro5w`(커밋 `e54e27f`)를 정식
   PR로 열어 main에 병합할지, 아니면 그 내용(archive 이동 보류 확정)을
   별도 신규 문서로 재작성해 main에만 반영할지.
2. 위 결정 전까지 RFC-0042/ADC-0045/ADR-0028의 해당 citation은 "미병합
   상태" 각주가 붙은 채로 유지하는 것이 최선이라고 판단한다(존재하는
   근거를 삭제하거나 조작하지 않는 편이 안전).

---

## 5. Repository Integrity 검증

```
git status --short
```
→ 3개 파일만 변경(신규 1 + 수정 2), 그 외 unintended change 없음(§6
참조).

```
git diff --check
```
→ 결과: (아래 §6 Validation Evidence에 실행 결과 기록)

- ADC-0019: 이번 작업에서 접촉하지 않음(zero-diff 유지).
- `docs/architecture/baseline/BASELINE.md`,
  `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`: 접촉하지 않음.
- Kernel Public Contract 문서(`ADC-0004`/`RFC-0004` in
  `docs/architecture/core/`): 접촉하지 않음.
- 원장 3종(`docs/decisions/{rfc,adc,adr}.md`)의 RFC-0003/ADC-0010 등록
  행: Document ID·Status·Source Path 값 자체는 변경하지 않았으므로
  원장과의 정합성은 유지된다(원장은 파일의 존재·Status만 참조하며 본문
  내용을 복제하지 않음).

## 완료 조건 확인

- Commit: 이 세션에서는 수행하지 않음(사용자 검토 후 별도 승인 필요 —
  §8 커밋/푸시/머지 권한 규칙 준수).
- Push/PR/Merge: 수행하지 않음.
- Architecture Baseline/Kernel Public Contract/ADC-0019: 무변경.
