---
name: branch-lifecycle
description: Closes out a completed claude/* work branch and starts the next one — checks merge/absorption status against latest origin/main, separates branches that are safe to delete from those that are not, and creates the next claude/* branch. Use when a work branch's PR has merged (or is confirmed absorbed into main) and it is time to clean up per CLAUDE.md Branch Strategy, or when starting a new work unit. Every irreversible step (delete, push) requires explicit human approval first — this skill never merges, never force-pushes, and never deletes a branch without that approval.
---

# branch-lifecycle

## 책임

반복되는 "작업 branch → main 반영 → 완료 branch 삭제 → 새 branch 생성"
과정에서, 판단이 필요 없는 기계적 단계만 자동화한다. merge 여부, 삭제
승인, push는 항상 사람이 명시적으로 승인한다. 이 Skill 자신은 Scheduler가
아니다 — 매번 사람/Claude Code가 명시적으로 호출할 때만 실행된다.

## 순서 (자동화)

1. **작업 트리 확인**: `git status --porcelain`. 커밋되지 않은 변경이
   있으면 즉시 중단하고 보고한다 — 임의로 stash/commit하지 않는다.
2. **원격 최신화**: `git fetch --all --prune` — 이미 삭제된 원격
   branch(예: PR 병합 시 GitHub의 head branch 자동삭제로 이미 없어진
   경우)를 로컬 tracking에서 정리한다. 이 단계는 삭제가 아니라 조회
   갱신이다.
3. **main 상태 확인**: `git log origin/main -1 --oneline`으로 최신
   commit을 확인한다.
4. **흡수 여부 판별**(대상 branch 각각에 대해):
   - `git log origin/main..<branch> --oneline` — 비어 있으면 해당
     branch의 모든 커밋이 이미 main에 있다(direct merge든 동일 내용
     이든).
   - 비어 있지 않으면(예: squash merge로 커밋 해시가 달라짐) GitHub
     PR 상태(`pull_request_read` 등, `merged: true`/`state: closed`)로
     추가 확인한다 — 커밋 로그 비교만으로 판단하지 않는다.
   - 두 확인 모두 실패하면(미병합, PR 없음, 확인 불가) **삭제 후보에서
     제외**한다.
5. **분류 보고 (삭제 실행 전)**: 사람에게 표로 보고한다 — 아직 아무것도
   삭제하지 않는다.

   | branch | 흡수 여부 근거 | 분류 |
   |---|---|---|
   | ... | main..branch 비어있음 / PR #N merged | 삭제 후보 |
   | ... | main..branch 비어있지 않음, PR 없음/미병합 | **삭제 금지** |

6. **로컬 삭제**(사람이 승인한 항목만): `git branch -D <branch>` —
   승인되지 않은 항목은 건드리지 않는다.
7. **원격 삭제**(사람이 별도로 승인한 항목만, 있는 경우만): 이미
   GitHub 자동삭제로 없어진 경우가 많으므로 `git ls-remote`로 실제
   존재를 재확인한 뒤, 존재하고 승인된 것만 `git push origin --delete
   <branch>` — 여기 도달하기 전에 반드시 6과 별도로 명시적 승인을
   받는다.
8. **새 branch 생성**: 이름을 사람이 확인/승인한 뒤
   `git checkout -b <new-branch-name> origin/main`.

## Human-in-the-loop (이 Skill이 절대 대신하지 않는 것)

- **merge 여부 판단** — 이 Skill은 PR을 생성하거나 병합하지 않는다.
  병합은 이 Skill 호출 이전에 이미 끝나 있어야 한다.
- **5번 표에서 어떤 branch를 삭제할지 최종 승인.**
- **원격 branch 삭제, 그리고 모든 push — 실행 전 명시적 승인 필수.**
  로컬 삭제 승인이 원격 삭제 승인을 자동으로 포함하지 않는다(7번은
  6번과 별도 승인).
- **미병합·미완료·Evidence 보존이 필요한 branch는 삭제 후보에 아예
  올리지 않는다**(4~5번에서 이미 제외, 6~7번에서 다시 확인).

## 금지

- 자동 merge, 자동 승인, "판단 없이" 진행.
- "오래됐다"/"안 쓰는 것 같다" 등 근거 없는 무조건적 branch 삭제 —
  흡수 여부 Evidence(4번) 없이는 삭제 후보에 올리지 않는다.
- Force push, force delete류 우회.
- Runtime, Scheduler, cron/Event Trigger 구현 — 이 Skill은 실행
  메커니즘을 새로 만들지 않는다. 사람이 호출해야 실행된다.
- `docs/architecture/baseline/BASELINE.md`, `hqs/development/BASELINE.md`
  등 Architecture/Contract/Governance 문서 수정.

## Pre-Flight

- 삭제 후보 목록과 그 근거(4번의 흡수 여부 Evidence)를 사람이 실제로
  확인했는가?
- 미병합 branch가 삭제 후보 표에 없는가?
- 로컬 삭제와 원격 삭제/push를 각각 별도로 승인받았는가?
- 이 Skill이 merge를 대신 수행하지 않았는가?
