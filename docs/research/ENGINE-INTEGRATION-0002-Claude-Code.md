# Engine Integration Research 0002: Claude Code — Execution Protocol Observation (기존 파일 수정)

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. ENGINE-INTEGRATION-0001의 두 번째 Observation
이며, 이번 실험은 "새 파일 생성"이 아니라 "이미 존재하는 파일 수정"
작업을 다룬다. Architecture 판단, Execution Result 설계, Execution
Layer 수정은 하지 않는다. 실험에서 실제로 관찰된 사실만 기록한다.
관찰되지 않은 것은 모두 Unknown으로 남긴다.

## Experiment

- **Prompt Specification**: ENGINE-INTEGRATION-0001과 **동일한**
  Artifact — `core/execution_layer/mvp_0002/dogfooding/output/real_issue.prompt_specification.md`
  전체 텍스트를 그대로 재사용했다. Prompt Specification 자체는 이번
  실험을 위해 새로 만들지 않았다 — 입력을 고정하고 Repository 상태만
  바꿔서, "같은 입력이 다른 시작 상태에서 어떻게 처리되는가"를 비교할
  수 있게 했다.
- **Repository 상태**: ENGINE-INTEGRATION-0001과 마찬가지로 메인
  저장소는 커밋 `77bef0c`(Execution Layer MVP-0005) 위에 있었고 변경
  없이 유지되었다(`git status --porcelain`으로 실험 종료 후 확인,
  메인 저장소에는 어떤 변경도 없었다). 실험은 메인 저장소가 아니라,
  `git worktree add`로 `77bef0c`에서 새로 만든 별도 worktree
  (`/home/user/jarvis-os/.claude/worktrees/experiment-0002-manual`,
  브랜치 `experiment-0002-seed`)에서 진행했다.
- **기존 파일 존재 여부**: 실험 시작 전, 연구자(나)가 그 worktree
  안에 `development-hq/mvp/generated/project_intelligence.py`를
  다음 스텁 내용으로 직접 만들고 커밋(`46fdb2d`, "seed: pre-existing
  stub for experiment-0002")해 두었다 — 이는 subagent의 작업이
  아니라 실험 준비 단계다.

  ```python
  """Stub scaffold — earlier, incomplete implementation attempt.

  TODO: implement project_intelligence per the Implementation
  Specification (Target File / Public Interface / Functions / Classes /
  Dependencies / Algorithm Outline / Edge Cases / Validation Notes).
  Only the Public Interface signature has been stubbed out so far; the
  body is unimplemented and the four check functions are missing.
  """


  def project_intelligence(*args, **kwargs):
      raise NotImplementedError
  ```

  subagent에게는 "이 파일이 이미 존재하며 이 스텁 내용을 담고 있다"는
  사실을 프롬프트에 그대로 알려주고, 이를 새로 쓰지 말고 수정하라고
  지시했다.

## Timeline

관찰 가능한 순서만 기록한다. 시간은 추정하지 않는다. subagent가 스스로
보고한 실제 호출 순서를 그대로 옮겼다.

- **T0** — Prompt Specification 텍스트 + "이 파일은 이미 존재하니
  새로 쓰지 말고 수정하라"는 지시 + 지정된 작업 디렉토리(격리된
  worktree 경로) 제약을 Agent 도구 호출 1회로 전달.
- **T1** — Bash: `git status` 확인 + `cat`으로 기존 스텁 파일 내용 확인.
- **T2** — Bash: `development-hq/mvp/` 목록 확인;
  `workflow_project_intelligence.py`를 `sed -n`으로 읽음.
- **T3** — Bash: `development-hq/mvp/project_intelligence.py`
  (Development HQ 자신의 기존 모듈) 전체를 `sed -n`으로 읽음.
- **T4** — Bash: `development-hq/mvp/agents.py` 전체를 `sed -n`으로 읽음.
- **T5** — Bash: `workflow_0008.py`, `engine.py`,
  `workflow_artifact_flow.py` 세 파일을 한 번의 명령으로 읽음.
- **T6** — Bash: `development-hq/mvp/generated/` 목록 확인
  (`__init__.py` 존재 여부 확인).
- **T7** — Bash: python import 스모크 테스트 — 실패(모듈 경로 문제,
  Failure 절 참조).
- **T8** — Bash: `mvp/tests` 목록 확인 + 테스트 파일 일부 확인 +
  `__init__.py` 내용 확인(기존 import 관례 파악).
- **T9** — Bash: python import/실행 테스트 — 실패(상대 import 오류,
  Failure 절 참조).
- **T10** — Bash: python import/실행 테스트 — 통과(수정 후).
- **T11** — Bash: python으로 `run_pipeline` 출력 텍스트를 직접 검사해
  올바른 leak 마커 문자열을 확인.
- **T12** — Bash: 마커 수정 후 재검증 — 모든 check 통과.
- **T13** — Bash: `py_compile`, `pytest development-hq/mvp/tests`,
  `git status`, `git diff` 실행(최종 검증).
- **Tn(종료)** — 연구자가 요청한 6개 항목 형식 그대로 구조화된 텍스트
  보고를 반환.

파일 수정 자체는 T1~T13 사이에 다음 순서로 일어났다(REPOSITORY_
INTERACTIONS와 별도로 FILE_MODIFICATION_METHOD 절에서 보고됨):
스텁을 읽음(T1) → `Write`로 전체 내용을 새 코드로 교체 → `Edit`로
상대 import 경로 수정(`.agents` → `..agents` 등) → `Edit`로 leak 마커
상수 수정(`"[Relevant Context]"` → `"## Reference Context"`).

## Repository Interaction

Claude Code(subagent)가 실제로 Repository에서 무엇을 읽었는지만
기록한다.

| 상호작용 종류 | 관찰 결과 |
|---|---|
| File Open(읽기) | 있음 — `project_intelligence.py`(스텁, 수정 대상), `development-hq/mvp/project_intelligence.py`(Development HQ 자신의 기존 모듈, 전체), `agents.py`(전체), `workflow_project_intelligence.py`, `workflow_0008.py`, `engine.py`, `workflow_artifact_flow.py`, `development-hq/mvp/tests/` 안의 테스트 파일 일부, `generated/__init__.py`. |
| Directory Scan | 있음 — `development-hq/mvp/` 목록, `development-hq/mvp/generated/` 목록, `development-hq/mvp/tests` 목록을 각각 확인. |
| Search(코드베이스 전체 검색, grep 등) | 관찰되지 않음 — ENGINE-INTEGRATION-0001과 달리, 이번 실험에서는 저장소 전체를 검색하는 별도 Search 호출이 보고되지 않았다. 필요한 파일을 이미 알고 있었던 것처럼 File Open으로 바로 접근했다(Comparison 절 참조). |
| Git Status | 있음 — 시작 시(T1) 1회, 종료 직전(T13) 1회, 총 2회 확인. |
| 실행 테스트(모듈을 직접 import/실행) | 있음 — 3회(T7 실패, T9 실패, T10 성공) + 최종 `pytest` 1회(T13). ENGINE-INTEGRATION-0001에서도 관찰된 패턴이다. |

## Output

실제로 생성된 결과만 기록한다.

| 항목 | 관찰 결과 |
|---|---|
| File Modification | 있음 — `development-hq/mvp/generated/project_intelligence.py` **1개 파일만** 수정됨(기존 파일이 그 자리에서 바뀜, 새 파일이 추가되지 않음). |
| Diff | 있음 — 실험 종료 후 연구자가 직접 `git diff -- development-hq/mvp/generated/project_intelligence.py`를 실행해 확인한 실제 결과: 7줄(스텁)에서 223줄로 변경, `+216 -7`. 스텁의 docstring과 `raise NotImplementedError` 본문이 완전히 대체되었고, `project_intelligence()` 함수 본문 + `project_intelligence_check_1~4()` 4개 함수 + 보조 함수(`_leaks_into`, `_review_mitigation_directions`) + 모듈 상수(`_CONTEXT_MARKER`)가 추가되었다. |
| Patch | Diff와 별도로 관찰되지 않음(Git diff 형식 하나로만 확인됨). |
| Commit | 없음 — 지시대로 커밋을 만들지 않았다(`git status --porcelain` 결과가 `M development-hq/mvp/generated/project_intelligence.py` 하나뿐이었고, 새 커밋은 생성되지 않았다). |
| Diagnostics | 있음 — `py_compile` 통과, `pytest development-hq/mvp/tests`(기존 3개 테스트) 통과, 수동 실행으로 얻은 4개 check 함수 결과(모두 `True`) 및 `leaks` dict(`planning`/`design`/`implementation` 모두 `True`). |
| Tool Output | 있음 — 19회의 Bash/Read/Write/Edit 호출 각각의 결과가 다음 판단에 사용되었다(ENGINE-INTEGRATION-0001은 25회였다 — Comparison 절 참조). |

## Observable State

실제로 관찰된 상태만 기록한다.

| 상태 | 관찰 결과 |
|---|---|
| Tool Execution | 있음 — 19회의 개별 tool_use(Bash/Write/Edit)가 순차적으로 관찰되었다. |
| Running | 간접적으로만 관찰됨 — ENGINE-INTEGRATION-0001과 동일하게, 상위 세션은 Agent 호출 직후 launch 확인만 받았고 중간 진행 상황은 실시간으로 노출되지 않았다. |
| Waiting | 관찰되지 않음 — ENGINE-INTEGRATION-0001과 동일. |
| Finished | 있음 — `<status>completed</status>` 라벨이 task-notification에 실제로 포함되어 있었다(ENGINE-INTEGRATION-0001과 동일한 형태). |
| Failed / Cancelled | 이번 실험의 최종 결과로는 관찰되지 않음(최종적으로 완료됨). 단, 중간에 실패한 개별 tool 실행이 2건 있었다(Failure 절 참조) — 이는 전체 작업의 "Failed" 상태가 아니라, 개별 실행 단계의 실패였고 이어지는 단계에서 회복되었다. |

## Failure

실제 원인만 기록한다. 새 범주가 나타나면 Unknown으로 두지 않고
Observation으로 남긴다.

- **실패 1 — 모듈 경로 오류(T7)**: 최초 python import 스모크 테스트가
  `ModuleNotFoundError: No module named 'development_hq'`로 실패했다.
  subagent는 `development-hq`(하이픈 포함 디렉토리명)를 그대로
  import하려 했던 것으로 보이며, 기존 테스트 관례
  (`development-hq/mvp/tests/test_mvp_0001.py`가 `development-hq`를
  `sys.path`에 추가한 뒤 `mvp` 패키지로 import하는 방식)를 확인한 뒤
  같은 방식으로 고쳐 재시도했다(T8→T9).
- **실패 2 — 상대 import 오류(T9)**: 수정 후에도
  `ModuleNotFoundError: No module named 'mvp.generated.agents'`가
  발생했다. 원인은 `project_intelligence.py`가 `mvp.generated`
  서브패키지 안에 위치하는데, `.agents`(한 단계 상대 import)를 써서
  `mvp.generated.agents`를 찾으려 했기 때문이었다 — 올바른 경로는
  `mvp.agents`이므로 `..agents`(두 단계 상대 import)로 고쳐야 했다.
  이 오류는 파일의 실제 디렉토리 위치(패키지 depth)를 subagent가
  처음에 잘못 계산했다는 것을 보여준다. `Edit`으로 `.agents` →
  `..agents` 등으로 수정 후 재검증(T10)에서 통과했다.
- **실패 3(범주는 실패이나 시스템 오류 아님) — Spec-Repository
  Staleness Mismatch(T11)**: ENGINE-INTEGRATION-0001에서 관찰된 것과
  **동일한 현상이 이번에도 재현되었다.** Prompt Specification 문서
  안의 리터럴 마커(`"[Relevant Context]"`)를 그대로 코드에 사용했으나,
  실제 저장소의 현재 파이프라인(`_analyze_requirement`, `engine.py`)이
  그 텍스트를 `"## Reference Context"` 섹션으로 재구성한다는 사실과
  달랐다. `project_intelligence_check_3`이 처음에 `False`를 반환하는
  형태로만 드러났고(시스템 에러 아님), subagent가 `run_pipeline`
  출력을 직접 검사(T11)해 올바른 마커를 재도출하고 `Edit`으로 수정해
  해결했다.
- **Timeout / Permission / Context Limit**: Unknown — 이번 실험에서도
  발생하지 않았다.

## Comparison

ENGINE-INTEGRATION-0001과 비교한다. Repository Scan, Output 형태,
Failure 형태 3가지만 비교한다. 판단하지 않는다.

### Repository Scan

| | 0001(신규 파일 생성) | 0002(기존 파일 수정) |
|---|---|---|
| 읽은 파일 수(보고 기준) | 8개(`project_intelligence.py`, `workflow_project_intelligence.py`, `workflow_0008.py`, `engine.py`, `workflow_artifact_flow.py`, `test_mvp_0001.py`, `mvp/__init__.py`, `MVP-0007-observation.md`) | 7개(`project_intelligence.py`(스텁), Development HQ의 `project_intelligence.py`, `agents.py`, `workflow_project_intelligence.py`, `workflow_0008.py`, `engine.py`, `workflow_artifact_flow.py`) |
| 저장소 전체 검색(Search) | 있음 — "다른 `generated/*.py` 예시를 저장소에서 검색"(T3) | 관찰되지 않음 |
| Directory Scan 횟수 | 3회(`mvp/`, `tests/`, `generated/`) | 3회(`mvp/`, `generated/`, `tests/`) |
| **공통점** | 두 실험 모두 프롬프트 텍스트만으로 작업하지 않고 저장소를 능동적으로 읽었다. 두 실험 모두 `agents.py`/`engine.py`/`workflow_*.py` 계열 파일을 필수로 참조했다. | |
| **차이점** | 0001은 "새 generated/*.py 예시가 있는가"를 저장소 전체에서 찾는 탐색적 Search를 1회 수행했다. 0002는 그런 탐색적 Search 없이 곧바로 필요한 파일들을 열었다 — 기존 파일(스텁)이 이미 무엇을 구현해야 하는지 실마리(함수 시그니처, docstring)를 담고 있어 별도 탐색이 덜 필요했을 가능성이 있으나, 이는 관찰된 사실이 아니라 이 문서가 판단하지 않는 해석이다. | |

### Output 형태

| | 0001 | 0002 |
|---|---|---|
| 산출물 형태 | 신규 파일 2개(`__init__.py`, `project_intelligence.py` 전체) | 기존 파일 1개 수정(`project_intelligence.py`) |
| Diff 관찰 여부 | 관찰되지 않음(신규 파일이라 diff 개념 자체가 적용되지 않음 — subagent 스스로도 "Patch/Diff 아님"이라고 보고) | 관찰됨 — `git diff`로 `+216 -7`의 실제 unified diff 확인 |
| 수정 방법 | `Write`(신규 파일 작성) 후 `Edit` 2회(자체 오류 수정) | `Write`(전체 교체) 후 `Edit` 2회(import 경로 수정, 마커 수정) |
| **공통점** | 두 실험 모두 최초 산출물 작성에는 `Write`를 사용했고, 이후 자체 오류 수정에는 `Edit`을 사용했다 — 최초 작성과 사후 수정에 다른 도구를 쓰는 패턴이 동일하게 나타났다. | |
| **차이점** | 0001은 Git 관점에서 완전히 새 파일(추적되지 않던 경로)이라 diff 개념이 없었다. 0002는 이미 추적되던 파일이라 실제 unified diff가 생성되어 관찰 가능했다 — Execution Layer의 "Output" 개념 중 "Diff/Patch"는 대상 파일이 이미 존재할 때만 관찰 가능한 형태라는 것이 이번 비교로 확인되었다. | |

### Failure 형태

| | 0001 | 0002 |
|---|---|---|
| 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) | 없음(Unknown) | 없음(Unknown) — 단, "ModuleNotFoundError" 2건이 발생했으나 이는 subagent 자신의 코드 실행 실패이지, Claude Code 도구 자체의 오류(Tool Error)는 아니었다 |
| Spec-Repository Staleness Mismatch | 관찰됨(`leak_reproduced` 항상 `False`, 마커 불일치) | **동일하게 다시 관찰됨**(`project_intelligence_check_3` 항상 `False`, 동일한 마커 불일치: `"[Relevant Context]"` vs `"## Reference Context"`) |
| 그 외 실패 | 없음 | 모듈 경로/상대 import 오류 2건(신규 관찰 — 0001에서는 나타나지 않았다. 0001은 새 파일이라 패키지 depth 계산 실수가 발생할 여지가 `generated/` 바로 아래 1단계뿐이었고, 실제로 이 오류가 보고되지 않았다) |
| **공통점** | 두 실험 모두 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)는 발생하지 않았다. 두 실험 모두 동일한 Spec-Repository Staleness Mismatch(마커 불일치)가 재현되었다 — **이 시점에서 2회 반복 관찰되어 Pattern 후보가 되었다.** | |
| **차이점** | 0002에서만 모듈 경로 관련 오류(ModuleNotFoundError) 2건이 나타났다. 이는 "기존 파일을 수정"하는 작업이 "새 파일을 만드는" 작업보다 패키지 구조(상대 import 깊이)에 대한 가정을 더 많이 요구했기 때문일 수 있으나, 이는 해석이며 이 문서는 판단하지 않는다. | |

## Unknowns

관찰되지 않은 것을 모두 기록한다. 추측하지 않는다.

- 이번 실험도 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지
  확인하지 않았다.
- Model Request, Execution Handle, Execution State를 Claude Code에
  직접 입력했을 때 어떤 입력/출력이 관찰될지 — 여전히 시험되지 않았다.
- "Running"/"Waiting" 상태가 실제로 이름 붙어 존재하는지.
- Search(저장소 전체 검색)가 이번 실험에서 관찰되지 않은 것이,
  "기존 파일 수정" 작업의 일반적 특성인지 아니면 이번 1회 실험의
  우연인지 — Pattern으로 확정하지 않는다(실험 1회만으로는 판단 불가).
- 모듈 경로/상대 import 오류가 "기존 파일 수정" 작업에서 반복적으로
  나타나는 실패 형태인지, 이번 1회의 우연(이 저장소의 특정 패키지
  구조 때문)인지 — 추가 실험 없이는 판단 불가.
- 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)가
  실제로 어떤 형태로 반환되는지 — 두 실험 모두 발생하지 않았다.
- 여러 개별 산출물(파일 수정, diff, 진단 로그, 텍스트 보고)을 하나의
  Execution Result로 묶는 방식 — 여전히 Unknown이며 이 문서는 답하지
  않는다.

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result를 설계하지
않는다. Execution Layer를 수정하지 않는다. RFC/ADC/ADR을 생성하지
않는다.

실험 2건(ENGINE-INTEGRATION-0001, 0002)에 걸쳐 다음 사실만 기록한다:
Spec-Repository Staleness Mismatch(Prompt Specification의 문자열이
저장소의 실제 최신 상태와 어긋나는 현상)가 서로 다른 두 실험(신규 파일
생성, 기존 파일 수정) 모두에서 동일하게 재현되었다 — 2회 반복 관찰되어
Pattern 후보가 되었다. 그 외 나머지(모듈 경로 오류, Search 유무 차이
등)는 아직 1회씩만 관찰되어 Pattern인지 우연인지 이 문서가 판단하지
않는다.
