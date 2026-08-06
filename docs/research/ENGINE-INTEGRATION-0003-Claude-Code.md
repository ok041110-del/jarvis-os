# Engine Integration Research 0003: Claude Code — Execution Protocol Observation (다중 파일 수정)

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. ENGINE-INTEGRATION-0001·0002의 세 번째
Observation이며, 목적은 Spec-Repository Staleness Mismatch가 Pattern인지
우연인지 검증하는 것이다. Architecture 판단, Execution Result 설계,
Execution Layer 수정, RFC/ADC/ADR 작성은 하지 않는다. 실험에서 실제로
관찰된 사실만 기록한다. 관찰되지 않은 것은 모두 Unknown으로 남긴다.

## Experiment

- **Prompt Specification**: ENGINE-INTEGRATION-0001·0002와 **동일한**
  Artifact — `core/execution_layer/mvp_0002/dogfooding/output/real_issue.prompt_specification.md`
  전체 텍스트를 세 번째로 재사용했다. 입력 텍스트는 세 실험 내내
  한 글자도 바꾸지 않았다.
- **Repository 상태**: 메인 저장소는 커밋 `77bef0c`(Execution Layer
  MVP-0005) 위에서 변경 없이 유지되었다(실험 종료 후 `git
  status --porcelain`으로 확인). 실험은 `git worktree add`로 `77bef0c`
  에서 새로 만든 별도 worktree
  (`/home/user/jarvis-os/.claude/worktrees/experiment-0003-manual`,
  브랜치 `experiment-0003-seed`)에서 진행했다.
- **수정 대상 파일 목록(실험 시작 전 연구자가 미리 만들어 둔 상태)**:
  이번에는 다중 파일 리팩터링을 유도하기 위해, 서로 의존하는 3개
  파일을 **낡은 이름**(`review_project_intelligence`, Prompt
  Specification이 요구하는 실제 Public Interface `project_intelligence`
  와 다른 이름)으로 미리 만들고 커밋(`0ca3852`, "seed: pre-existing
  outdated multi-file package for experiment-0003")해 두었다.
  - `development-hq/mvp/generated/project_intelligence.py` —
    `review_project_intelligence(*args, **kwargs): raise
    NotImplementedError` 스텁.
  - `development-hq/mvp/generated/__init__.py` — 위 스텁을 낡은
    이름으로 재노출(`from .project_intelligence import
    review_project_intelligence`).
  - `development-hq/mvp/generated/tests/test_project_intelligence.py`
    — 낡은 이름을 import해서 `NotImplementedError`가 발생하는지만
    확인하는 스모크 테스트(실험 시작 전 실행 시 통과함을 직접
    확인했다 — 낡은 이름 기준으로는 내부적으로 일관된 상태였다).

  세 파일 모두 "새 파일"이 아니라 "이미 존재하고 서로 의존하는 낡은
  파일"이라는 조건을 만족한다.

## Timeline

관찰 가능한 순서만 기록한다. 시간은 추정하지 않는다. subagent가 스스로
보고한 실제 호출 순서를 그대로 옮겼다.

- **T0** — Prompt Specification 텍스트 + "이 패키지는 이미 존재하는
  낡은 초안이며, 이를 리팩터링하되 새 파일을 만드는 것이 목적이
  아니다"라는 지시 + 지정된 작업 디렉토리 제약을 Agent 도구 호출
  1회로 전달.
- **T1** — Bash: `ls` + `git status`로 `development-hq/mvp/generated/`
  상태 확인.
- **T2** — Read: `project_intelligence.py`(낡은 스텁).
- **T3** — Read: `__init__.py`(낡은 재노출).
- **T4** — Bash: `find development-hq/mvp/generated/tests -type f`.
- **T5** — Read: `test_project_intelligence.py`(낡은 테스트).
- **T6** — Read: `tests/__init__.py`.
- **T7** — Bash: `wc -l`로 Prompt Specification의 Dependencies 절에
  나열된 4개 파일 줄 수 확인.
- **T8** — Read: `workflow_0008.py`.
- **T9** — Read: `workflow_artifact_flow.py`.
- **T10** — Read: `workflow_project_intelligence.py`.
- **T11** — Grep: `collect_relevant_context|class ProjectIntelligence|def project_intelligence` 패턴으로 `development-hq/mvp` 전체 검색.
- **T12** — Bash: `grep -n "^def \|^class \|import"`로 `engine.py`의
  함수/클래스/import 목록 확인.
- **T13** — Bash: 다른 `generated` 패키지나 유사 관례가 있는지 저장소
  안에서 탐색(발견되지 않음).
- **T14** — Bash: `sed -n '1,120p' agents.py`.
- **T15** — Bash: `sed -n '385,460p' engine.py`(`_design_from_requirement`).
- **T16** — Bash: `sed -n '517,610p' engine.py`(`_generate_code`).
- **T17** — Bash: `sed -n '256,335p' engine.py`(`_analyze_requirement`).
- **T18** — Bash: 임시 python 스크립트로
  `collect_relevant_context(REAL_ISSUE)` / `_summarize_context` /
  `_enrich_issue` 실제 반환값을 직접 조사.
- **T19** — Bash: `pytest development-hq/mvp/generated/tests/test_project_intelligence.py -v`
  (반복 실행하며 구현을 다듬음, RecursionError 발견·수정 포함).
- **T20** — Bash: `pytest development-hq/mvp -q`(패키지 전체 회귀 확인).
- **T21** — Bash: `git status && git diff`(최종 검증).
- **Tn(종료)** — 연구자가 요청한 6개 항목 형식 그대로 구조화된 텍스트
  보고를 반환.

## Repository Interaction

실제로 관찰된 행동만 기록한다.

| 상호작용 종류 | 관찰 결과 |
|---|---|
| File Open(읽기) | 있음 — 총 9개 이상: 낡은 3개 파일(스텁, `__init__.py`, 테스트) + Dependencies 4개 파일(`workflow_0008.py`, `workflow_artifact_flow.py`, `workflow_project_intelligence.py`, `engine.py` 발췌) + `agents.py`. |
| Search(grep 등 패턴 검색) | **있음 — 이번 실험에서 처음으로 명시적 `Grep` 도구 사용이 보고되었다**(T11: `collect_relevant_context\|class ProjectIntelligence\|def project_intelligence` 패턴으로 저장소 전체 검색). 별도로 "다른 generated 패키지 관례가 있는지" 탐색(T13)도 수행했다(결과: 없음). |
| Directory Scan | 있음 — `development-hq/mvp/generated/`, `tests/` 디렉토리 확인. |
| Git Status | 있음 — 시작 시(T1) 1회, 종료 직전(T21) 1회. |
| Git Diff | 있음 — 종료 직전(T21) 1회, 연구자도 별도로 직접 재확인함(아래 Output 절). |
| 실행 테스트(모듈을 직접 import/실행) | 있음 — 임시 스크립트로 실제 함수 반환값 조사(T18) + pytest 반복 실행(T19, 여러 번) + 패키지 전체 pytest(T20). |

## Output

실제로 생성된 결과만 기록한다.

| 항목 | 관찰 결과 |
|---|---|
| Modified Files | 있음 — **3개 기존 파일 모두 수정됨**(요구 조건 "최소 2개 이상" 충족): `development-hq/mvp/generated/project_intelligence.py`, `development-hq/mvp/generated/__init__.py`, `development-hq/mvp/generated/tests/test_project_intelligence.py`. |
| New Files Created | 없음 — subagent 스스로도 "None"이라 보고했고, 연구자가 `git status --porcelain`으로 직접 확인한 결과도 세 파일 모두 `M`(Modified)이었다(`A`로 표시된 새 파일 없음). |
| Unified Diff | 있음 — 연구자가 직접 `git diff --stat`로 확인: `__init__.py` +8/-2, `project_intelligence.py` +170/-14(신규 함수 5개: `_resolve_issue`, `_observe`, `project_intelligence`, `check_1~4`), `test_project_intelligence.py` +59/-20. 세 파일 합계 `219 insertions(+), 18 deletions(-)`. |
| Patch | Diff와 별도로 관찰되지 않음. |
| Commit | 없음 — 지시대로 커밋을 만들지 않았다. |
| Diagnostics | 있음 — `pytest development-hq/mvp/generated/tests/test_project_intelligence.py`(패키지 전용, 7개 테스트 통과) + `pytest development-hq/mvp`(전체 10개 테스트 통과, 연구자가 직접 재실행해 확인). |
| Tool Output | 있음 — 33회의 Bash/Read/Grep/Write/Edit 호출 각각의 결과가 다음 판단에 사용되었다(0001: 25회, 0002: 19회, 0003: 33회). |

## Failure

실제 실패만 기록한다.

### Spec-Repository Staleness Mismatch — 재현 여부: **재현됨**

ENGINE-INTEGRATION-0001, 0002와 **동일한 근본 원인**이 세 번째로도
그대로 나타났다: Prompt Specification에 나오는 문자열은 아니지만
동일 계열의 문제로, `_enrich_issue`가 실제로 Issue description에
붙이는 헤더 문자열(`"[Relevant Context]"`)이 `engine._analyze_requirement`
에서 partition되어 사라지므로, 그 헤더 문자열 자체로 leak 여부를
판정하려 하면 항상 실패한다는 사실을 subagent가 T18(직접 실행 조사)
에서 다시 발견했다. 이번에는 subagent가 사전에(구현을 마치기 전에)
`collect_relevant_context`/`_summarize_context`/`_enrich_issue`의
실제 반환값을 코드 작성 전에 먼저 조사해, **이 문제를 사후 수정이
아니라 사전 예방으로 처리**했다는 점이 0001·0002와 다르다(Comparison
절 참조). 즉 마커 문제 자체는 세 번째로 재현되었으나, 이번에는
subagent가 그 문제를 코드 작성 전 조사 단계에서 미리 회피했다.

### 새로 관찰된 실패 범주 1 — Self-Referential Recursion (RecursionError)

subagent가 최초 구현에서 `project_intelligence()`가 각
`project_intelligence_check_N()`을 호출하고, 그 `check_N()` 함수들이
다시 `project_intelligence()`를 호출하는 순환 구조를 만들어
`RecursionError`가 발생했다. subagent는 이를 pytest 실행(T19)으로
직접 발견했고, 공유 헬퍼 `_observe()`를 별도로 두어 `project_intelligence()`
와 `check_N()` 함수들이 서로를 호출하지 않고 `_observe()`만 각자
호출하도록 구조를 바꿔 해결했다. 이 범주는 ENGINE-INTEGRATION-0001,
0002에서는 나타나지 않았다 — 다중 파일 간 함수 재사용 관계가 늘어난
이번 실험(3개 파일, 5개 함수)에서 처음 관찰되었다.

### 새로 관찰된 실패 범주 2 — Spec Internal Duplication

Prompt Specification의 Interfaces 절에서 `project_intelligence_check_1`
과 `project_intelligence_check_4`의 설명 문구가 실질적으로 동일한
문장("Project Intelligence(collect_relevant_context)가 이 문제를
완화할 수 있는 방향으로 개선될 수 있는지 검토가 필요하다")을 그대로
포함하고 있다는 사실을 subagent가 직접 지적했다(ERRORS_OR_FAILURES에
명시적으로 기록). subagent는 이를 "spec-vs-repo mismatch"가 아니라
"원본 텍스트 자체의 중복"이라고 구분해서 보고했고, `check_4`를
`check_1`과 동일한 로직으로 위임 구현했다.

**주의(사실 확인)**: 이 중복 자체는 세 실험 모두 동일한 입력 텍스트
안에 처음부터 있었다 — 새로 생긴 것이 아니다. 그러나 0001·0002의
subagent는 `check_1`과 `check_4`에 **서로 다른 로직**을 구현했다
(둘 다 "mitigation_directions 존재 여부" 계열의 조건을 썼지만, 정확한
검증 내용은 달랐다) — 두 실험 모두 이 중복을 명시적으로 언급하지
않았다. 0003의 subagent만 이 중복을 명시적으로 인지하고 두 함수를
사실상 동일하게 만들었다. 즉 "중복된 문구의 존재"는 세 실험 모두에서
동일했지만, "그 중복을 명시적으로 인지·보고했는가"는 0003에서만
관찰되었다.

### 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)

관찰되지 않았다(Unknown) — subagent 스스로도 "no permission or tool
errors" 외에는 없다고 보고했다.

## Comparison

세 실험(ENGINE-INTEGRATION-0001, 0002, 0003)을 비교한다. Repository
Interaction, Output 형태, Failure 형태 3가지만 비교한다. 판단하지
않는다.

### Repository Interaction

| | 0001(신규 파일 생성) | 0002(기존 파일 1개 수정) | 0003(기존 파일 3개 수정) |
|---|---|---|---|
| Tool Use 총 횟수(보고 기준) | 25 | 19 | 33 |
| 명시적 Search/Grep | 있음(1회, 저장소 전체에서 유사 예시 검색) | 없음 | 있음(2회 — Grep 패턴 검색 + 유사 관례 탐색) |
| Directory Scan | 있음(3회) | 있음(3회) | 있음(2회 이상) |
| Git Status | 있음(1회, 종료 직전) | 있음(2회, 시작+종료) | 있음(2회, 시작+종료) |
| 사전 조사(코드 작성 전 실제 반환값 검사) | 관찰되지 않음(사후 발견) | 관찰되지 않음(사후 발견) | **있음(T18, 코드 작성 전 실제 반환값을 미리 조사)** |
| **공통점** | 세 실험 모두 프롬프트 텍스트만으로 작업하지 않고 저장소를 능동적으로 읽었다. 세 실험 모두 `agents.py`/`engine.py`/`workflow_*.py` 계열 파일을 필수로 참조했다. 세 실험 모두 최소 1회 이상 Directory Scan과 Git Status를 수행했다. | | |
| **차이점** | Tool Use 총 횟수는 수정 대상 파일 수와 함께 늘어났다(1개→19, 3개→33) — 단, 0001(신규 파일, 25회)은 0002(기존 파일 1개, 19회)보다 많아, 파일 수와 Tool Use 횟수가 단순 비례하지는 않았다. 명시적 Search/Grep은 0001·0003에서만 관찰되고 0002에서는 관찰되지 않았다. "코드 작성 전 사전 조사"는 0003에서만 관찰되었다. | | |

### Output 형태

| | 0001 | 0002 | 0003 |
|---|---|---|---|
| 수정된 기존 파일 수 | 0(전부 신규) | 1 | 3 |
| 신규 생성 파일 수 | 2 | 0 | 0 |
| Unified Diff 관찰 여부 | 관찰되지 않음(신규 파일) | 관찰됨(`+216/-7`) | 관찰됨(3개 파일 합계 `+219/-18`) |
| Commit | 없음 | 없음 | 없음 |
| **공통점** | 세 실험 모두 Commit은 생성하지 않았다. 기존 파일이 있는 경우(0002, 0003) 모두 실제 Unified Diff가 관찰되었다. | | |
| **차이점** | 0001만 diff가 없는 유일한 실험이었다(대상이 전부 신규 파일이었기 때문). 0003만 3개 파일에 걸친 diff가 나타났다 — 다중 파일 수정이 실제로 다중 diff로 이어짐이 확인되었다. | | |

### Failure 형태

| | 0001 | 0002 | 0003 |
|---|---|---|---|
| Spec-Repository Staleness Mismatch | 관찰됨(사후 발견·수정) | 관찰됨(사후 발견·수정) | 관찰됨(사전 조사로 회피) |
| 모듈/상대 import 경로 오류 | 없음 | 있음(2건) | 없음 |
| Self-Referential Recursion | 없음 | 없음 | **있음(1건, 신규 범주)** |
| Spec Internal Duplication(명시적 인지) | 없음(다른 로직으로 구현, 언급 없음) | 없음(다른 로직으로 구현, 언급 없음) | **있음(1건, 신규 범주 — 명시적으로 인지·보고)** |
| 시스템 수준 실패 | 없음 | 없음 | 없음 |
| **공통점** | Spec-Repository Staleness Mismatch는 세 실험 모두에서 나타났다 — 실험 조건(신규 생성/단일 수정/다중 수정)과 무관하게 반복되었다. 세 실험 모두 시스템 수준 실패는 없었다. | | |
| **차이점** | 모듈 경로 오류는 0002에서만, Self-Referential Recursion과 Spec Internal Duplication(명시적 인지)은 0003에서만 관찰되었다 — 각각 1개 실험에서만 나타난 범주다. | | |

## Pattern Check

Pattern 여부는 판단하지 않는다. 3개 실험 중 몇 개에서 관찰되었는지
횟수만 기록한다.

| 현상 | Observation Count(3개 실험 중) |
|---|---|
| Spec-Repository Staleness Mismatch | 3 |
| Repository Search(Grep/탐색적 검색) | 2 |
| Diff/Patch 관찰 가능(기존 파일 존재) | 2 |
| 모듈/상대 import 경로 오류 | 1 |
| Self-Referential Recursion | 1 |
| Spec Internal Duplication(명시적 인지) | 1 |
| 신규 파일 생성 | 1 |
| 다중 파일 수정(2개 이상) | 1 |
| 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) | 0 |

## Unknowns

관찰되지 않은 것을 모두 기록한다. 추측하지 않는다.

- 이번에도 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지
  확인하지 않았다.
- Model Request, Execution Handle, Execution State를 Claude Code에
  직접 입력했을 때 어떤 입력/출력이 관찰될지 — 세 실험 모두 Prompt
  Specification만 시험했다.
- Tool Use 총 횟수가 수정 대상 파일 수와 정확히 어떤 관계인지(0001이
  0002보다 많았던 이유) — 이 문서는 판단하지 않는다.
- "코드 작성 전 사전 조사"가 다중 파일 리팩터링에서 일반적으로
  나타나는 특성인지, 이번 1회의 우연인지 — 추가 실험 없이는 판단 불가.
- Self-Referential Recursion이 함수/파일 수가 일정 이상 늘어날 때
  일반적으로 나타나는 현상인지, 이번 특정 구현 방식에서만 나타난
  우연인지 — 판단 불가(1회 관찰).
- Spec Internal Duplication을 명시적으로 인지하는 것이 무엇에 따라
  달라지는지(모델의 우연한 선택인지, 다른 요인이 있는지) — 판단 불가.
- 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)가
  실제로 어떤 형태로 반환되는지 — 세 실험 모두 발생하지 않았다.
- 여러 개별 산출물(파일 수정, diff, 진단 로그, 텍스트 보고)을 하나의
  Execution Result로 묶는 방식 — 여전히 Unknown.

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result를 설계하지
않는다. Execution Layer를 수정하지 않는다. RFC/ADC/ADR을 생성하지
않는다.

실험 3건(ENGINE-INTEGRATION-0001, 0002, 0003)에 걸쳐 다음 사실만
기록한다: 동일한 Prompt Specification 입력을 세 가지 다른 Repository
조건(신규 생성/단일 파일 수정/다중 파일 수정)에서 실행한 결과, Spec-
Repository Staleness Mismatch는 3/3 실험 모두에서 재현되었다. Repository
Search와 Diff 관찰 가능 여부는 각각 2/3 실험에서 나타났다. 모듈 경로
오류, Self-Referential Recursion, Spec Internal Duplication(명시적
인지)은 각각 1/3 실험에서만 나타났다. 이 수치가 Pattern을 확정하는지는
이 문서가 판단하지 않는다 — 관찰된 횟수만 기록했다.
