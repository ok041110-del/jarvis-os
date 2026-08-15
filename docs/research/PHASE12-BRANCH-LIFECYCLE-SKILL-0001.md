# PHASE12-BRANCH-LIFECYCLE-SKILL-0001: branch-lifecycle Skill 구현 및 실제 검증

이 문서는 사용 후기가 아니다. `PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001`이
식별한 유일한 강한 후보("작업 branch → main 병합 → branch 정리")를
`.claude/skills/branch-lifecycle/SKILL.md`로 실제 구현하고, 현재
저장소의 실제 branch 상태에 대해 1회 실행 검증한 기록이다. Runtime/
Scheduler/반복 Trigger를 구현하지 않았다. Architecture/Contract/
Governance 문서를 수정하지 않았다.

## 1. 구현

`.claude/skills/branch-lifecycle/SKILL.md` — 기존 Skill들(`handover`,
`validation` 등)과 동일하게 순수 지시문 기반(스크립트/Runtime 없음)이며,
Claude Code가 매번 명시적으로 호출할 때만 실행된다.

자동화 범위: `git fetch --all --prune`(1) → main 상태 확인(2) → branch별
흡수 여부 판별(3) → 삭제 후보/금지 분류 보고(4) → **사람 승인 후**
로컬 삭제(5) → **별도 승인 후** 원격 삭제(6) → 이름 승인 후 새 branch
생성(7).

Human-in-the-loop 게이트: merge 여부, 삭제 최종 승인, 원격 삭제/push
전부 — SKILL.md에 "이 Skill이 절대 대신하지 않는 것"으로 명시.

`CLAUDE.md` Skills 목록에 `branch-lifecycle`을 추가했다(Maintenance
규칙 "변경된 Skill 목록을 반영" 준수).

## 2. 실제 검증 (1회, 현재 프로젝트 workflow)

### Step 1~3 (기계적, 실제 실행)

```
$ git status --porcelain        # 최초 실행: 이 Skill 자신의 미커밋 변경 감지 → 중단(설계대로 동작)
$ git commit ...                # (커밋 후 재실행)
$ git status --porcelain        # clean
$ git fetch --all --prune
$ git log origin/main -1 --oneline
a514492 ENGINE-USECASE-0002: N-way(3/4) 병렬 실행 Runtime Evidence (#61)
```

**첫 실행에서 Step 1이 실제로 멈췄다** — 이 Skill 파일 자신을 커밋하기
전 상태였기 때문이다. 설계된 안전장치("커밋되지 않은 변경이 있으면
즉시 중단")가 실제로 작동함을 그 자리에서 확인했다(의도적으로 재현한
것이 아니라, 실행 중 실제로 발생함).

### Step 4 (흡수 여부 판별, 실제 6개 branch 대상)

`git log origin/main..origin/<branch> --oneline`로 전수 확인:

| branch | unmerged commits | PR 상태 | 분류 |
|---|---|---|---|
| `claude/jarvis-phase10-boundary-validation` | 4 | PR 없음 | **삭제 금지** |
| `claude/jarvis-phase10-nomarker-capability-prototype` | 1 | PR 없음 | **삭제 금지** |
| `claude/jarvis-phase10-nomarker-prototype-2` | 1 | PR 없음 | **삭제 금지** |
| `claude/jarvis-phase10-prompt-specification-audit` | 1 | PR 없음 | **삭제 금지** |
| `claude/jarvis-phase12-runtime-automation-audit` | 2 | PR 없음 | **삭제 금지** |
| `claude/jarvis-os-hq-mvp-0001-2fcqvd` | 3 | 최신 PR #58 merged, 그러나 그 **이후** 3개 커밋(PG Dividend Stock Dogfooding, `WIP` 포함)이 어떤 PR에도 없음 | **삭제 금지** |

**결과: 6개 전부 삭제 금지.** 실제로 지금 안전하게 삭제 가능한
branch는 하나도 없었다 — 이는 실패가 아니라 정확한 판별이다:
`claude/jarvis-os-hq-mvp-0001-2fcqvd`는 겉보기엔 "옛날 branch"지만
실제로는 마지막 merge 이후 미완료 Dogfooding(PG, 8/11단계까지만
완료된 `WIP` 커밋 포함)이 얹혀 있었다 — 이 Skill이 없었다면
"오래됐으니 지워도 되겠지"라고 착각하기 쉬운 사례를, 실제 commit 로그
대조로 정확히 걸러냈다.

### 부수 발견 — `list_pull_requests`의 `merged` 필드는 신뢰 불가

Step 4에서 GitHub PR 상태를 교차 확인하려고 `list_pull_requests`를
먼저 썼는데, 실제로 병합된 PR #58을 `merged: false`로 잘못 반환했다.
같은 PR을 `pull_request_read`(method: `get`)로 다시 조회하니
`merged: true`가 정확히 나왔다 — **`list_pull_requests`의 `merged`
필드를 흡수 여부 판별에 쓰면 안 된다**는 것을 이번 실제 실행으로
확인했다. SKILL.md는 이미 "PR 상태(`pull_request_read` 등)"로
표현해 뒀으나, 이번 발견으로 그 선택이 정확했음이 실증됐다 — SKILL.md
문구는 수정하지 않는다(이미 올바른 방법을 가리키고 있었다).

### Step 5~7 (삭제/생성)

- **삭제 실행**: 없음 — 삭제 후보가 하나도 없었으므로 사람 승인
  요청 자체가 발생하지 않았다(설계대로: 근거 없이는 후보에 올리지
  않는다).
- **새 branch 생성(Step 7)**: 이번 작업 자체가 이미 `git checkout -b
  claude/jarvis-branch-lifecycle-skill origin/main`으로 이 과정을
  실행했다 — 사용자가 "최신 main 기준으로 새 claude/* branch에서
  수행하라"고 지시했고, `origin/main`이 최신인지(Step 3) 확인 후
  생성했다.

## 3. 판정

**실제 프로젝트 workflow에서 1회 검증 완료.** 안전장치(미커밋 변경
차단, 흡수 여부 오판 방지, GitHub API 필드 신뢰성 문제 회피)가 전부
실제로 작동했다. 자동 merge, 무조건 삭제, force push는 이번 실행에서
시도되지 않았다(설계상 애초에 그런 경로가 없다).

## Architecture/Contract 변경 여부

**없음.** Runtime/Scheduler/Event Bus/반복 Trigger를 구현하지 않았다.
이 Skill은 사람이 Skill 도구로 명시적으로 호출할 때만 실행된다 —
백그라운드나 예약 실행 경로가 없다. `docs/01_architecture/BASELINE.md`,
`development-hq/BASELINE.md` 무수정.

## Governance

RFC/ADC/ADR 불필요 — Skill은 Claude Code 실행 도구이지 Jarvis OS
Architecture Component가 아니다. `PHASE12-RUNTIME-AUTOMATION-AUDIT-0001`의
Runtime DEFER 판단과 무관하게 이 Skill은 Runtime 없이 완결된다.

## Evidence

- `.claude/skills/branch-lifecycle/SKILL.md`(신규).
- 이번 문서 §2의 실제 실행 로그 표(6개 branch 전수 확인, PR #58
  `list` vs `get` 불일치 재현).

## Next

- 실제로 삭제 가능한 branch가 생기는 시점(예: 이번 Phase 12 관련
  branch들이 병합될 때)에 이 Skill로 다시 실행해, 삭제 경로(Step
  5~6)까지 포함한 전체 흐름을 검증하는 것이 후속 과제다 — 이번
  문서는 그 재검증을 선제적으로 예약하지 않는다.
