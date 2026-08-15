# PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001: Automation Workflow 필요성 재검토

이 문서는 사용 후기가 아니다. `PHASE12-RUNTIME-AUTOMATION-AUDIT-0001`의
"Runtime 필요 없음" 판단은 그대로 유지한 채, "Automation Workflow
필요성 없음" 판단만 분리해 재검토한 READ-ONLY 조사 기록이다(코드
무수정). Runtime/Scheduler/Event Bus를 전제하지 않는다. 5개 후보
Workflow를 실제 이번 세션(Phase 9~12)에서 반복 수행한 1차 경험 +
저장소 기존 문서를 근거로 평가한다.

## 후보 1: GitHub 변경 → /sync → Verified Project State → Artifact Dashboard 갱신

- **현재 수동 단계**: 사람이 `/sync`를 트리거 → Claude Code가 저장소
  상태 재조사 → Dashboard 갱신.
- **반복 빈도**: 이번 세션에서는 발생하지 않음(이 Workflow는 이번
  Phase 9~12 범위 밖). `ARTIFACT-DASHBOARD-TRIAL-0001.md` 기준 1회
  Trial만 확인됨 — 반복 빈도를 "실제로 자주"라고 주장할 근거가 아직
  약하다.
- **사람이 개입해야 하는 이유**: 그 문서 §7이 이미 "자동 트리거는
  실제 필요가 확인된 뒤 검토"라고 명시 — 지금은 의도적으로 수동.
- **자동화 이점**: Dashboard가 항상 최신 상태로 유지됨. 다만 반복
  빈도 증거가 약해 이점의 크기를 추정으로 부풀리지 않는다.
- **현재 도구만으로 가능한가**: 가능할 것으로 보이나(GitHub push
  이벤트 + 기존 `/sync`), 실제 필요 Evidence가 아직 없다.
- **판단**: 기존 문서의 DEFER를 재확인. 이번 조사로 새 근거가
  나오지 않았다.

## 후보 2: 작업 branch → main 병합 → branch 정리 — **가장 강한 후보**

- **현재 수동 단계(이번 세션에서 실제로 반복 수행)**: (1) 완료된
  branch에 대해 PR 생성(`create_pull_request`), (2) `mergeable_state`
  확인, (3) 병합(`merge_pull_request`), (4) `git fetch --prune`로
  원격 삭제 확인, (5) 로컬 stale branch 정리(`git branch -D`), (6)
  `git checkout -b <new-branch> origin/main`으로 다음 작업 시작.
- **반복 빈도**: 이번 세션에서만 Phase 9 종료 시 2회(PR #60, #61)
  전 과정을 실제로 수행했고, Phase 10~12에서도 매번 (2)·(6) 단계
  (Baseline 확인, 새 branch 생성)를 반복했다 — **세션당 5회 이상,
  Branch Strategy(CLAUDE.md)가 매 작업 단위마다 요구하는 고정
  패턴**이다.
- **사람이 개입해야 하는 이유**: PR 병합은 공유 상태를 바꾸는
  hard-to-reverse 행동이라 실제로는 매번 "병합해도 되는가"에 대한
  최소한의 확인(테스트 통과, 문서 변경만인지)이 들어간다 — 이 판단
  자체는 사람/Claude Code 개입이 필요하지만, 그 앞뒤의 기계적 단계
  (fetch/prune/branch 생성/이름 규칙 적용)는 판단이 필요 없다.
- **자동화 이점**: 매 Phase마다 반복되는 6단계 중 판단이 필요 없는
  단계(1, 4, 5, 6)를 한 번의 호출로 묶으면 반복 실수(예: origin/main
  최신화 누락, stale branch 방치) 위험이 줄어든다. 이미 이번 세션에서
  실제로 확인된 사실: GitHub 저장소의 "병합 시 head branch 자동 삭제"
  설정이 **이미 켜져 있다**(Phase 9 종료 시 `git push origin --delete`가
  "remote ref does not exist"로 실패 → `fetch --prune`으로 이미
  삭제됨을 확인) — 이는 새로 만들 필요 없이 **기존 GitHub 저장소
  설정이 이미 이 Workflow의 절반(원격 정리)을 자동화하고 있다**는
  뜻이다.
- **현재 도구만으로 자동화 가능한가**: **가능하다.** GitHub MCP
  tools(`create_pull_request`/`merge_pull_request`)와 `git` CLI만으로
  전 과정이 이미 수행 가능함을 이번 세션이 직접 증명했다 — 새 도구,
  새 Runtime, 새 Scheduler가 전혀 필요 없다.
- **Prototype 방향(설계만, 구현하지 않음)**: "branch 정리 + 새 branch
  생성"을 한 데 묶는 **Claude Code Skill 또는 slash-command 후보**
  (예: 기존 `.claude/skills/`에 있는 `handover`/`task-observer`와
  같은 성격) — 사람이 여전히 "지금 병합해도 되는가"만 판단하고, 그
  이후 기계적 단계는 한 번의 트리거로 실행. 이번 문서는 그 Skill을
  실제로 만들지 않는다 — Prototype **방향**만 식별한다(사용자가
  명시적으로 구현을 요청하지 않았다).

## 후보 3: Dogfooding → Evidence 기록 → Validation

- **현재 수동 단계**: 실험 스크립트 작성 → 실제 Engine 실행 →
  BEFORE/AFTER 표 작성 → 회귀 테스트 → Self Review 체크리스트 작성 →
  commit.
- **반복 빈도**: 저장소 전체 기준 매우 높음(`docs/01_mvp/` 52개
  문서, 이번 세션만 `MVP-0050/0051/0052` 3건). 구조가 거의 동일
  (문서 성격 → 목적 → BEFORE → 변경 → AFTER → 비교 → 회귀 확인 →
  판정 → Architecture 여부 → Governance → Self Review)하게 반복된다.
- **사람이 개입해야 하는 이유**: 실제 판정(Success/Failure/Inconclusive)과
  "억지로 성공 판정하지 않기"는 매번 실제 실행 결과를 보고 사람 수준의
  판단이 필요하다 — 이 부분은 자동화 대상이 아니다.
- **자동화 이점**: 문서 골격(성격 표기, Self Review 체크리스트 항목)을
  매번 손으로 새로 구성하는 대신 템플릿화하면 형식 누락(예: Self
  Review 항목 빠뜨림)을 줄일 수 있다.
- **현재 도구만으로 가능한가**: **이미 부분적으로 가능하다.**
  `CLAUDE.md`가 이미 `md-writer`(Markdown 문서 형식), `validation`
  (Acceptance Criteria 충족 여부 검증) Skill을 선언해 뒀고,
  `.claude/skills/md-writer/SKILL.md`·`.claude/skills/validation/SKILL.md`가
  실제로 저장소에 존재한다 — **새로 만들 필요 없이 이미 선언된
  도구가 있다.** 다만 이번 세션의 MVP-0050~0052 작성 과정에서 이
  두 Skill을 명시적으로 호출하지는 않았다 — "선언은 있으나 실제
  활용은 매번 되지 않는다"는 것이 이번에 새로 확인된 사실이다.
- **판단**: 새 Runtime/Automation이 아니라 **이미 있는 Skill을 실제로
  더 활용하는 것**이 다음 단계다 — 이는 이번 문서의 구현 범위 밖이다
  (사용자 요청 없이 임의로 Skill 사용 방식을 바꾸지 않는다).

## 후보 4: Claude Code 작업 완료 → 결과 검증 → 후속 작업

- **현재 수동 단계**: 매 작업 끝에 `pytest` 재실행, Self Review
  체크리스트, 최대 10줄 보고 형식.
- **반복 빈도**: 이번 세션 전 Phase에서 매번 발생 — 그러나 이는
  이미 "한 대화 턴 안에서" 자연스럽게 수행되고 있어 별도로 자동화할
  간극이 관찰되지 않았다.
- **판단**: 자동화 가치가 낮다 — 이미 사실상 매번 실행되고 있다.

## 후보 5: 기타 반복 작업

이번 조사 범위(Phase 9~12 세션 Evidence)에서 후보 1~4 외에 반복성이
확인된 새 Workflow는 찾지 못했다. 추측으로 새 후보를 만들지 않는다.

---

## 종합 판정

- **후보 2(branch → main 병합 → branch 정리)가 유일하게 "실제 반복
  빈도 + 판단 불필요한 기계적 단계 + 기존 도구만으로 가능"이라는
  세 조건을 모두 충족한다.**
- 나머지 후보(1, 3, 4, 5)는 반복 빈도 증거가 약하거나(1), 이미 다른
  형태로 부분 자동화 수단이 존재하거나(3), 자동화 간극이 없다(4, 5).

## Runtime Need

**변경 없음 — 여전히 불필요.** `PHASE12-RUNTIME-AUTOMATION-AUDIT-0001`의
판단(A: 현재 구조로 충분, Runtime DEFER)을 유지한다. 후보 2의 Prototype도
Scheduler/Event Bus 없이 매번 사람/Claude Code가 명시적으로 트리거하는
방식으로 충분하다 — Background 실행이나 정기 실행이 필요한 지점이
없다.

## Architecture/Governance

RFC/ADC/ADR 작성 없음. 새 Component/Layer/Concept 설계 없음. 이번
문서는 Prototype **방향**만 식별했고, 실제 Skill/Script를 만들지
않았다 — 구현은 별도 요청·판단 대상이다.

## Evidence

- 이번 세션 Phase 9 종료 시 PR #60/#61 생성·병합·자동 branch 삭제
  확인(이 대화의 실제 tool 호출 기록).
- `docs/research/ARTIFACT-DASHBOARD-TRIAL-0001.md` §7.
- `.claude/skills/md-writer/SKILL.md`, `.claude/skills/validation/SKILL.md`
  존재 확인(`find` 실행 결과).
- `docs/01_mvp/MVP-0050~0052-observation.md` 반복 구조 대조.

## Next

- 후보 2의 Prototype(Skill 또는 slash-command)을 실제로 만들지
  여부는 별도 사용자 지시가 있을 때 진행한다 — 이번 문서는 방향만
  기록했다.
- 후보 3(Skill 실활용도)도 마찬가지로, 실제로 `md-writer`/`validation`
  Skill을 다음 Evidence 문서 작성부터 명시적으로 호출할지는 별도
  판단 대상이다.
