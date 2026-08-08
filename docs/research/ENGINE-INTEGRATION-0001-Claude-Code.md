# Engine Integration Research 0001: Claude Code — Execution Protocol Observation

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. Architecture 판단, Execution Result 설계,
Runtime 논의는 하지 않는다. 실험에서 실제로 관찰된 사실만 기록한다.
관찰되지 않은 것은 모두 Unknown으로 남긴다.

## Experiment

- **사용한 Prompt Specification**: Execution Layer MVP-0002 Dogfooding
  산출물 `core/execution_layer/mvp_0002/dogfooding/output/real_issue.prompt_specification.md`
  전체 텍스트. Development HQ MVP-0008의 실제 Issue("Project
  Intelligence 개선")로부터 Implementation Specification → Execution
  Request → Prompt Specification 체인을 거쳐 이미 생성되어 있던
  Artifact를 그대로 사용했다 — 새로 만들지 않았다.
- **Repository 상태**: 실험 시작 시점 기준 메인 저장소는 직전 커밋
  `77bef0c`(Execution Layer MVP-0005) 위에 있었고, 추적되지 않는
  파일은 `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`
  1개뿐이었다(별도 지시로 커밋하지 않기로 한 문서).
- **Worktree 여부**: 있음. Claude Code Agent 도구를
  `isolation: "worktree"`로 호출해, 메인 작업 디렉토리와 분리된 별도
  git worktree(`/home/user/jarvis-os/.claude/worktrees/agent-a545da4cebaf3bf22`,
  브랜치 `worktree-agent-a545da4cebaf3bf22`, 실험 종료 시점 커밋
  `47a1f3a`)에서 실행되었다. 실험 종료 후 `git status --porcelain`으로
  메인 저장소의 추적 파일이 이 실험으로 전혀 변경되지 않았음을
  확인했다(`.claude/` 아래 worktree 디렉토리 자체만 추적되지 않는
  항목으로 나타남).
- **실행 환경**: Claude Code Agent 도구(`subagent_type: "claude"`)로
  fresh session(부모 대화의 맥락을 전혀 물려받지 않음 — 전달한 프롬프트
  텍스트만 입력) 1회 실행. 하위 subagent가 실제로 어떤 모델로
  실행되었는지는 이번 실험에서 별도로 확인하지 않았다 — Unknown.

## Timeline

관찰 가능한 순서만 기록한다. 시간은 추정하지 않는다. 아래 T번호는
subagent가 스스로 보고한 실제 호출 순서를 그대로 옮긴 것이다.

- **T0** — Prompt Specification 텍스트(+ "이것을 작업 지시로 취급해
  실제로 수행하고, 질문하지 말고, 정해진 형식으로 보고하라"는 연구자
  지시)를 Agent 도구 호출 1회로 전달.
- **T1** — Bash: `development-hq/mvp/` 목록 확인, `generated/` 디렉토리
  존재 여부 확인.
- **T2** — Bash(병렬 배치): `project_intelligence.py`,
  `workflow_project_intelligence.py`, `workflow_0008.py` 읽기.
- **T3** — Bash(병렬 배치): `engine.py`(전체), `workflow_artifact_flow.py`
  읽기; 저장소 안에서 다른 `generated/*.py` 예시 검색.
- **T4** — Read: 이전 단계에서 저장된 대용량 출력 파일(engine.py 전체
  내용)을 다시 열람.
- **T5** — Bash(병렬 배치): `mvp/tests/` 목록 확인;
  `docs/01_mvp/MVP-0007-observation.md` 앞부분 읽기.
- **T6** — Bash(병렬 배치): `test_mvp_0001.py` 읽기, pyproject/conftest
  존재 여부 확인, `mvp/__init__.py` 읽기.
- **T7** — Bash: `mkdir -p development-hq/mvp/generated`.
- **T8** — Write: `development-hq/mvp/generated/__init__.py` 생성.
- **T9** — Write: `development-hq/mvp/generated/project_intelligence.py`
  생성(신규 코드 전체).
- **T10** — Bash: 새로 만든 모듈을 수동으로 실행해 `check_1~4`,
  `leak_reproduced`, `mitigation_reduces_size` 값 확인.
- **T11** — Edit ×2: `_CONTEXT_MARKER`를 Spec 문서 안의 문자열
  (`"[Relevant Context]"`)에서 저장소 현재 상태의 실제 마커
  (`"## Reference Context"`)로 수정, 부수적으로 남은 placeholder 줄 정리.
- **T12** — Edit: `leak_reproduced` 함수의 docstring을 마커 불일치
  사실을 설명하도록 수정.
- **T13** — Bash: 수동 검증 재실행(기본 Issue, positional 인자,
  keyword 인자 3가지 호출 방식 모두 확인).
- **T14** — Bash: `python3 -m pytest mvp/tests/ -q` 실행.
- **T15** — Bash: `git status --short` 실행.
- **Tn(종료)** — 연구자가 요청한 6개 항목(TOOL_CALLS_IN_ORDER 등) 형식
  그대로 구조화된 텍스트 보고를 반환.

## Inputs

Claude Code(subagent)가 실제로 참조한 입력만 기록한다.

| 항목 | 관찰 결과 |
|---|---|
| Prompt | 있음 — Prompt Specification 5개 절 전체 텍스트 + 연구자가 앞뒤로 붙인 작업 지시 문구. |
| Repository | 있음 — subagent가 스스로 `development-hq/mvp/` 하위 여러 파일을 능동적으로 조회했다(프롬프트 텍스트만으로 작업하지 않았다). |
| Files | 있음 — `project_intelligence.py`, `workflow_project_intelligence.py`, `workflow_0008.py`, `engine.py`(전체), `workflow_artifact_flow.py`, `test_mvp_0001.py`, `mvp/__init__.py`, `docs/01_mvp/MVP-0007-observation.md`. |
| Git Status | 있음 — 종료 직전 `git status --short` 1회 실행해 확인(T15). 시작 시점에 Git 이력이나 diff를 사전 입력으로 받은 흔적은 없음. |
| 이전 대화 맥락 | 없음(Unknown이 아니라 명시적으로 없음) — fresh session이므로 이 문서를 작성 중인 세션의 이전 대화, Execution Layer MVP-0001~0005 구현 이력 등은 전혀 전달되지 않았다. |

## Outputs

실제로 생성된 것만 기록한다.

| 항목 | 관찰 결과 |
|---|---|
| Files | 있음 — `development-hq/mvp/generated/__init__.py`, `development-hq/mvp/generated/project_intelligence.py`(신규 파일 전체). |
| Patch/Diff | 관찰되지 않음(신규 파일 생성이라 diff 형태로 나타나지 않았다). 기존 초안을 스스로 고칠 때는 Edit(old_string/new_string 치환) 방식이 관찰되었다 — 별도의 unified diff 텍스트 형태는 아니었다. |
| Commit | 없음 — 연구자 지시대로 커밋을 만들지 않았다(관찰된 사실: 지시가 있으면 커밋을 생성하지 않는다는 것 자체가 확인됨). |
| Diagnostics | 있음 — `python3 -m pytest mvp/tests/ -q` 실행 결과("3개 테스트 통과"), 수동 실행으로 얻은 `check_1~4`/`leak_reproduced`/`mitigation_reduces_size` 값. |
| Tool Output | 있음 — 25회의 Bash/Read/Write/Edit 호출 각각의 결과가 subagent 자신의 다음 판단에 그대로 사용되었다. |
| 로그(별도 스트림) | 관찰되지 않음 — Bash stdout/stderr 외의 독립된 로그 스트림은 없었다. |
| 구조화된 최종 보고 | 있음 — 연구자가 요청한 6개 항목 형식을 그대로 따른 텍스트 보고가 반환되었다. |

## Observable State

실행 중 실제로 관찰된 상태만 기록한다.

| 상태 | 관찰 결과 |
|---|---|
| Tool Execution | 있음 — 25회의 개별 tool_use(Bash/Read/Write/Edit)가 순차적으로, 일부는 동시에("병렬 배치")로 관찰되었다. |
| Running | 간접적으로만 관찰됨 — 상위 세션(연구자) 기준으로는 Agent 호출 직후 "Async agent launched successfully"라는 launch 확인만 받았고, 그 이후 하위 25개 tool call이 진행되는 동안의 중간 상태는 상위 세션에 실시간으로 노출되지 않았다. |
| Waiting | 관찰되지 않음 — "Waiting"이라는 이름이 붙은 상태 신호를 받은 적이 없다. 완료 알림이 올 때까지 상위 세션은 그냥 다른 작업을 계속했을 뿐이다. |
| Finished | 있음 — 완료 시점에 `<status>completed</status>`라는 명시적 라벨이 task-notification에 실제로 포함되어 있었다. |
| Failed / Cancelled | Unknown — 이번 실험에서는 발생하지 않았다. |

## Failure

이번 실험은 시스템 수준 실패(Timeout/Permission/Tool Error/Context
Limit) 없이 종료되었다 — subagent 스스로도 "ERRORS_OR_FAILURES: None
blocking"이라고 보고했고, 25개 tool call 모두 성공적으로 반환되었다.

- **Timeout**: Unknown — 발생하지 않았고 관찰되지 않았다.
- **Permission**: Unknown — 실험 중 권한 거부가 발생한 흔적이 없다.
- **Tool Error**: Unknown — 25개 tool call 모두 오류 없이 반환되었다.
- **Context Limit**: Unknown — 관찰되지 않았다.
- **실제로 관찰된, 위 4개 범주에 속하지 않는 실패 형태 1건**: subagent가
  최초 구현에서 Prompt Specification 문서 안의 문자열
  (`"[Relevant Context]"`)을 그대로 코드에 사용했으나, 이는 실제
  저장소의 현재 `engine.py`가 이미 다른 마커(`"## Reference Context"`)
  로 바뀐 뒤였던 것과 불일치했다. 이 불일치는 Tool Error나 시스템
  실패로 드러나지 않았다 — `leak_reproduced`가 항상 `False`를 반환하는
  논리적 결과로만 나타났고, subagent가 자신의 수동 테스트 실행(T10)으로
  이를 발견해 Edit(T11~T12)으로 스스로 수정했다. 이 문서는 이를
  "Spec-Repository Staleness Mismatch"라고만 이름 붙여 사실로 기록한다
  — Timeout/Permission/Tool Error/Context Limit 중 어디에도 해당하지
  않는, 이번 실험에서 실제로 관찰된 별도 현상이다.

## Artifact Mapping

```
Prompt Specification (Execution Layer MVP-0002 Artifact, real_issue)
            │
            ▼  Observed Claude Input
프롬프트 텍스트 그대로 + Repository 능동 탐색(8개 파일 열람, Git Status 확인)
            │
            ▼  Observed Claude Output
신규 파일 2개(project_intelligence.py, __init__.py, diff 아닌 전체 코드)
+ 수동 검증 로그 + pytest 결과 + git status 확인 + 구조화된 텍스트 보고
            │
            ▼  Candidate Execution Result
Unknown
```

- **Prompt Specification → Observed Claude Input**: 이번 실험에서는
  별도 변환·재구성 없이 Prompt Specification 텍스트 그대로가 Claude
  Code의 입력(작업 지시)으로 사용되었다. Claude Code는 이 텍스트만으로
  작업하지 않고, 스스로 저장소를 능동적으로 탐색해 참고 자료를 추가로
  확보했다(Inputs 절 참조). Model Request나 Execution Handle/Execution
  State가 실제로 Claude Code에 입력된 적은 없다 — 이번 실험은 Prompt
  Specification 한 단계만 시험했다. 그 세 Artifact와 Claude Code 입력
  사이의 대응은 Unknown이다.
- **Observed Claude Input → Observed Claude Output**: 관찰됨(Outputs
  절 전체).
- **Observed Claude Output → Candidate Execution Result**: Unknown.
  이번 실험은 "여러 개별 산출물"(신규 파일, 로그, 텍스트 보고)만
  만들었을 뿐, 그것을 하나의 단일 Execution Result Artifact로 묶는
  방식은 관찰되지 않았다. Execution Result는 Execution Layer에
  아직 존재하지 않는 Artifact이며, 이 문서는 그것을 설계하지 않는다.

## Unknowns

관찰되지 않은 것을 모두 기록한다. 추측하지 않는다.

- 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지.
- Model Request, Execution Handle, Execution State를 Claude Code에
  직접 입력했을 때 어떤 입력/출력이 관찰될지 — 이번 실험은 Prompt
  Specification만 시험했다.
- "Running"이라는 이름이 붙은 상태가 실제로 존재하는지, 아니면
  상위 세션에 그 이름으로 노출되지 않을 뿐인지.
- "Waiting" 상태가 실제로 존재하는지.
- Timeout, Permission 거부, Tool Error, Context Limit이 실제로 어떤
  형태로 반환되는지 — 이번 실험에서는 하나도 발생하지 않았다.
- 기존 파일을 수정하는 작업이었다면 Output이 Patch/Diff 형태로
  나타났을지 — 이번 실험은 신규 파일 생성만 관찰했다.
- 여러 개별 산출물(파일, 로그, 텍스트 보고)을 하나의 Execution Result로
  묶는 방식이 무엇이어야 하는지 — Unknown이며 이 문서는 답하지 않는다.
- 실패가 실제로 Tool Error/Timeout/Permission/Context Limit 형태로
  반환될 때 그 형식이 무엇인지 — 이번 실험에서 그 경로가 실행되지
  않았다.

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result를 설계하지
않는다. 실험 1건에서 실제로 관찰된 사실(Timeline, Input, Output,
Observable State, Failure, Artifact Mapping의 일부)만 기록했으며,
관찰되지 않은 나머지는 모두 Unknowns 절에 정직하게 남겼다.
