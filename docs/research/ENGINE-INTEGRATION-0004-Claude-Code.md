# Engine Integration Research 0004: Claude Code — Execution Protocol Observation (Model Request / Execution Handle / Execution State 입력)

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. ENGINE-INTEGRATION-0001·0002·0003의 네 번째
Observation이며, 목적은 R-1 — "Model Request + Execution Handle +
Execution State를 실제 Engine 입력으로 주었을 때의 Input / Execution /
Output" — 을 관찰하는 것이다. Architecture 판단, Execution Result 설계,
Execution Result Contract/Schema 결정, Execution Layer 수정, RFC/ADC/ADR
작성은 하지 않는다. 실험에서 실제로 관찰된 사실만 기록한다. 관찰되지
않은 것은 모두 Unknown으로 남긴다.

## Experiment

- **바뀐 것은 입력뿐이다.** ENGINE-INTEGRATION-0001·0002·0003은 세 번
  모두 Prompt Specification 단독(`core/execution_layer/mvp_0002/dogfooding/output/real_issue.prompt_specification.md`)
  을 입력으로 썼다. 0004는 그 자리에 다음 3개 Artifact의 **전체 텍스트**를
  원문 그대로 넣었다. 새 입력을 만들지 않았다 — 저장소에 이미 존재하는
  Artifact를 그대로 읽어 붙였다.
  - `core/execution_layer/mvp_0003/dogfooding/output/real_issue.model_request.md`
  - `core/execution_layer/mvp_0004/dogfooding/output/real_issue.execution_handle.md`
  - `core/execution_layer/mvp_0005/dogfooding/output/real_issue.execution_state.md`
- **입력의 중첩 구조(관찰된 사실)**: 세 Artifact는 서로 독립이 아니라
  포함 관계다. Execution State는 Execution Handle 전문을 포함하고,
  Execution Handle은 Model Request 전문을 포함하며, Model Request는
  Prompt Specification 전문을 포함한다. 그 결과 **동일한 Prompt
  Specification 본문이 한 입력 안에 3회 반복**되었고, Metadata 계층은
  1회(Model Request) / 2회(Handle) / 3회(State) 반복되었다. 실험자는
  이 중복을 제거하지 않았다 — Artifact 전체 텍스트를 그대로 쓴다는
  기존 조건을 유지했다.
- **Repository 상태**: 메인 저장소는 커밋 `c263c1a` 위에서 변경 없이
  유지되었다(실험 전후 `git status --porcelain` 모두 빈 출력). 실험은
  `git worktree add`로 `77bef0c`(Execution Layer MVP-0005 — 0002·0003과
  동일한 base commit)에서 새로 만든 별도 worktree
  (`/home/user/jarvis-os/.claude/worktrees/experiment-0004-manual`,
  브랜치 `experiment-0004-seed`)에서 진행했다.
- **시작 조건**: worktree는 clean이었고 `development-hq/mvp/generated/`
  디렉토리는 존재하지 않았다 — 즉 사전 seed 없이 0001과 동일한 시작
  상태다(0002는 낡은 파일 1개, 0003은 낡은 파일 3개를 미리 커밋해
  두었다). 0004에서는 새 seed를 만들지 않았다.
- **실행 환경**: Claude Code Agent 도구(`subagent_type: "claude"`)로
  fresh session(부모 대화의 맥락을 전혀 물려받지 않음 — 전달한 프롬프트
  텍스트만 입력) 1회 실행. 커밋 금지와 worktree 디렉토리 제약을
  프롬프트에 명시했다. 하위 subagent가 실제로 어떤 모델(버전)로
  실행되었는지는 이번에도 확인하지 않았다 — Unknown.
- **보고 형식**: 0001~0003과 동일한 6개 항목(TOOL_CALLS_IN_ORDER /
  FILES_CREATED / FILES_MODIFIED / DIAGNOSTICS_RUN / ERRORS_OR_FAILURES /
  FINAL_STATE)을 그대로 요구했다.

## Timeline

관찰 가능한 순서만 기록한다. 시간은 추정하지 않는다. subagent가 스스로
보고한 실제 호출 순서를 그대로 옮겼다(총 19회).

- **T0** — Model Request / Execution Handle / Execution State 3개
  Artifact 전체 텍스트 + 작업 디렉토리 제약 + 보고 형식을 Agent 도구
  호출 1회로 전달.
- **T1** — Bash: worktree 루트 `ls -la`.
- **T2** — Bash: `ls -R development-hq` + `cat README.md`.
- **T3** — Bash: `wc -l`로 Dependencies 4개 파일 + `project_intelligence.py`,
  `agents.py` 줄 수 확인.
- **T4** — Read: `development-hq/mvp/project_intelligence.py`(기존 PI 구현).
- **T5** — Read: `development-hq/mvp/workflow_project_intelligence.py`.
- **T6** — Read: `development-hq/mvp/workflow_artifact_flow.py`.
- **T7** — Read: `development-hq/mvp/workflow_0008.py`.
- **T8** — Bash: `grep -rn "generated"` + `cat workflow_0009.py`.
- **T9** — Bash: `mvp/__init__.py`, `tests/test_mvp_0001.py`, `mvp/README.md`
  확인(import 관례 조사).
- **T10** — Bash: `sed -n 1,120p docs/01_mvp/MVP-0013-observation.md`.
- **T11** — Read: `development-hq/mvp/agents.py`.
- **T12** — Bash: 코드 작성 **전** 인라인 `python3 -c`로
  `run_pipeline(REAL_ISSUE)` 실행해 실제 leak 여부를 실측.
- **T13** — Bash: `mkdir -p development-hq/mvp/generated`.
- **T14** — Write: `development-hq/mvp/generated/__init__.py` 생성.
- **T15** — Write: `development-hq/mvp/generated/project_intelligence.py` 생성.
- **T16** — Bash: 생성한 Target File을 스크립트로 직접 실행.
- **T17** — Bash: import 모드 실행 + 무관한 toy issue 실행 + `pytest`.
- **T18** — Bash: `git status --short`, `git log -1`.
- **Tn(종료)** — 요청한 6개 항목 형식 그대로 구조화된 텍스트 보고를 반환.

## Input Handling — Model Request / Handle / State 계층이 실제로 어떻게 다뤄졌는가

R-1의 핵심 관찰 지점이다. 관찰된 것만 기록한다.

| 입력 계층 | 관찰 결과 |
|---|---|
| Prompt Specification 본문(Mission/Input/Constraints/Expected Output/Validation Notes) | **작업 지시로 소비되었다** — Target File 경로, Public Interface, 4개 check 함수, Dependencies 4개 파일 읽기가 모두 실제 행동으로 나타났다(T3~T7, T14~T15). 0001~0003과 동일하다. |
| Model Request Metadata(`request_id`, `artifact_version`, `created_at: unresolved`, `target_engine: unresolved`) | **실행을 막지 않았다** — `created_at`/`target_engine`이 `unresolved`인 채로도 subagent는 질문 없이 실행했다. `request_id`는 생성 파일 첫 줄 docstring에 문자열로 인용되었다(실험자가 `grep`으로 직접 확인). 그 외 기능적 사용은 관찰되지 않았다. |
| Execution Handle(`handle_id`, `status: PENDING`, `submitted_at: unresolved`) | **`handle_id`가 생성 파일 docstring에 문자열로 인용되었다**(1곳). `status: PENDING`에 대한 어떤 행동(대기, 폴링, 상태 조회, 상태 갱신)도 관찰되지 않았다. |
| Execution State(`state: PENDING`, `changed_at: unresolved`) | **어떤 관찰 가능한 행동도 유발하지 않았다.** state 전이(PENDING→RUNNING→…)를 나타내는 산출물, 파일, 반환 필드는 생성되지 않았다. 입력 Artifact 3개 중 어느 것도 수정되지 않았다. |
| 동일 Prompt Specification 본문 3회 반복 | **중복에 대한 언급이 보고에 없었다.** 중복을 지적하거나, 세 사본의 차이를 확인하거나, 어느 사본을 기준으로 삼았는지 밝히는 행동은 관찰되지 않았다. 실행은 정상 종료했다(Context Limit 오류 없음). |

즉 이번 실험에서 관찰된 범위 안에서, 3계층 봉투(Envelope)는 **식별자
2개가 생성 산출물의 docstring에 인용된 것 외에는 Prompt Specification
단독 입력과 구분되는 행동 차이를 만들지 않았다**. 이것이 봉투 계층의
일반적 성질인지 이번 1회의 결과인지는 이 문서가 판단하지 않는다.

## Repository Interaction

실제로 관찰된 행동만 기록한다.

| 상호작용 종류 | 관찰 결과 |
|---|---|
| File Open(읽기) | 있음 — Read 도구 5회(`project_intelligence.py`, `workflow_project_intelligence.py`, `workflow_artifact_flow.py`, `workflow_0008.py`, `agents.py`) + Bash `cat`/`sed`로 읽은 파일 다수(`README.md` 2종, `mvp/__init__.py`, `test_mvp_0001.py`, `workflow_0009.py`, `MVP-0013-observation.md`). |
| Search(grep 등 패턴 검색) | 있음 — `grep -rn "generated"`(T8) 1회. |
| Directory Scan | 있음 — `ls -la`(T1), `ls -R development-hq`(T2). |
| Git Status | 있음 — 종료 직전(T18) 1회. 시작 시에는 관찰되지 않았다. |
| Git Diff | **관찰되지 않았다** — `git status --short`와 `git log -1`만 수행했다(수정된 추적 파일이 0개였으므로 diff 대상이 없었다). |
| 실행 테스트(모듈을 직접 import/실행) | 있음 — 코드 작성 전 실측 probe(T12) + 스크립트 실행(T16) + import 모드 실행 + toy issue 실행 + pytest(T17). |
| 지시된 디렉토리 경계 준수 | 있음 — 실험자가 `git status --porcelain`으로 메인 저장소에 변경이 없음을 직접 확인했다. |

## Output

실제로 생성된 결과만 기록한다. 아래 수치는 실험자가 worktree에서 직접
재확인한 값이다.

| 항목 | 관찰 결과 |
|---|---|
| New Files Created | 있음 — 2개: `development-hq/mvp/generated/project_intelligence.py`(479줄, 20,095 bytes), `development-hq/mvp/generated/__init__.py`(7줄). `git status --porcelain`은 `?? development-hq/mvp/generated/` 1줄만 출력했다. |
| Modified Files | **없음 — 0개.** `git diff --stat`이 빈 출력이었다(추적 파일 중 수정된 것 없음). |
| Unified Diff | 관찰되지 않음 — 대상이 전부 신규 파일이라 diff가 존재하지 않는다(0001과 동일). |
| Patch | 관찰되지 않음. |
| Commit | 없음 — worktree HEAD는 `77bef0c` 그대로였다. |
| 표준 출력(stdout) 산출물 | **있음** — 생성 모듈을 실행하면 Verdict / Injected Relevant Context / Propagation / Finding / Checks 5개 절로 이루어진 측정 리포트가 stdout으로 출력된다(실험자가 직접 재실행해 확인). 이는 파일도 diff도 아닌 세 번째 형태의 산출물이다. |
| Diagnostics | 있음 — 코드 작성 전 leak probe(baseline 실측), 생성 모듈 스크립트 실행, import 모드 실행, 무관한 toy issue 실행, `python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q` → **42 passed**(실험자가 직접 재실행해 42 passed 확인). |
| 구조화된 최종 보고 | 있음 — 요청한 6개 항목 형식을 그대로 따른 텍스트 보고가 반환되었다. |
| Tool Output | 있음 — 19회 호출 각각의 결과가 다음 판단에 사용되었다(0001: 25회, 0002: 19회, 0003: 33회, 0004: 19회). |

### 생성물의 실측 결과(실험자 직접 재실행)

```
Verdict: mitigable
Injected Relevant Context: baseline 966자 → candidate 524자
design         : 966 -> 524 chars | paths 19 -> 0 | leak 0.2163 -> 0.1303
implementation : 966 -> 524 chars | paths 19 -> 1 | leak 0.1449 -> 0.0862
check_1 ~ check_4: 모두 True
```

## Failure

실제 실패만 기록한다.

### Spec-Repository Staleness Mismatch — 재현 여부: **보고되지 않음**

0001·0002·0003에서 3회 연속 나타났던 마커 계열 실패가 이번 보고에는
나타나지 않았다. subagent는 0003과 마찬가지로 **코드 작성 전에**
`run_pipeline(REAL_ISSUE)`를 직접 실행해 실제 전파 여부를 실측했고
(T12), 그 실측값을 기준으로 구현했다. 즉 이번에도 사전 조사 단계가
관찰되었고, 마커 불일치를 사후 수정한 흔적은 보고되지 않았다.

**주의(사실 확인)**: "실패가 보고되지 않았다"와 "그 조건이 저장소에
존재하지 않는다"는 다른 진술이다. 이 문서는 전자만 기록한다.

### 새로 관찰된 범주 — Generated Artifact Self-Inclusion (수정하지 않고 보고만 함)

subagent는 Model Request가 지정한 Target File 경로
(`development-hq/mvp/generated/project_intelligence.py`)가 기존 Project
Intelligence의 `CATEGORY_PATHS["source_code"]` 스캔 범위 **안**에 있기
때문에, 새로 생성된 파일 자신이 `source_code` 목록에 최고 점수로
진입해 `workflow_artifact_flow.py`를 밀어낸다는 사실을 발견해
ERRORS_OR_FAILURES에 기록했다. 그리고 이를 **고치지 않았다** — 수정하려면
Model Request의 Target File 밖인 기존 `project_intelligence.py`를
건드려야 하므로 범위를 벗어난다고 명시적으로 판단하고, 측정과 보고만
했다.

이 범주는 0001~0003에서는 나타나지 않았다. "Target File 범위를 근거로
관찰된 문제의 수정을 스스로 보류하고 보고만 한 행동"이 관찰된 것은
이번이 처음이다. 이것이 Model Request 계층 입력 때문인지, 이번 구현
방식의 우연인지 — 이 문서는 판단하지 않는다.

### 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)

관찰되지 않았다 — subagent 스스로도 "No errors"라고 보고했다. 입력
길이가 0001~0003보다 크게 늘었음에도(Prompt Specification 본문 3회 반복)
Context Limit 관련 실패는 관찰되지 않았다.

## Comparison

네 실험을 비교한다. Repository Interaction, Output 형태, Failure 형태만
비교한다. 판단하지 않는다.

### 입력과 시작 조건

| | 0001 | 0002 | 0003 | 0004 |
|---|---|---|---|---|
| 입력 Artifact | Prompt Specification | 동일 | 동일 | **Model Request + Execution Handle + Execution State** |
| Prompt Specification 본문 반복 횟수 | 1 | 1 | 1 | **3(중첩 구조 때문)** |
| 시작 시 대상 파일 | 없음 | 낡은 파일 1개 | 낡은 파일 3개 | 없음 |

### Repository Interaction

| | 0001 | 0002 | 0003 | 0004 |
|---|---|---|---|---|
| Tool Use 총 횟수(보고 기준) | 25 | 19 | 33 | 19 |
| 명시적 Search/Grep | 있음(1) | 없음 | 있음(2) | 있음(1) |
| Directory Scan | 있음 | 있음 | 있음 | 있음 |
| Git Status | 있음(종료) | 있음(시작+종료) | 있음(시작+종료) | 있음(종료 1회) |
| 코드 작성 전 사전 실측 | 관찰되지 않음 | 관찰되지 않음 | 있음 | **있음** |
| **공통점** | 네 실험 모두 프롬프트 텍스트만으로 작업하지 않고 저장소를 능동적으로 읽었다. 네 실험 모두 `agents.py`/`engine.py`/`workflow_*.py` 계열을 참조했고, 최소 1회 이상 Directory Scan과 Git Status를 수행했으며, 커밋은 만들지 않았다. | | | |

### Output 형태

| | 0001 | 0002 | 0003 | 0004 |
|---|---|---|---|---|
| 수정된 기존 파일 수 | 0 | 1 | 3 | 0 |
| 신규 생성 파일 수 | 2 | 0 | 0 | 2 |
| Unified Diff 관찰 여부 | 관찰되지 않음 | 관찰됨(`+216/-7`) | 관찰됨(`+219/-18`) | 관찰되지 않음 |
| stdout 측정 리포트 | 관찰되지 않음(수동 확인만) | 관찰되지 않음 | 관찰되지 않음 | **관찰됨(모듈 실행 시 5개 절 리포트)** |
| Commit | 없음 | 없음 | 없음 | 없음 |
| 입력 Artifact 자체의 갱신 | 해당 없음 | 해당 없음 | 해당 없음 | **없음(state는 PENDING 그대로)** |

### Failure 형태

| | 0001 | 0002 | 0003 | 0004 |
|---|---|---|---|---|
| Spec-Repository Staleness Mismatch | 관찰됨(사후 수정) | 관찰됨(사후 수정) | 관찰됨(사전 회피) | 보고되지 않음 |
| 모듈/상대 import 경로 오류 | 없음 | 있음(2건) | 없음 | 없음 |
| Self-Referential Recursion | 없음 | 없음 | 있음(1건) | 없음 |
| Spec Internal Duplication(명시적 인지) | 없음 | 없음 | 있음(1건) | 없음 |
| Generated Artifact Self-Inclusion(보고만) | 없음 | 없음 | 없음 | **있음(1건, 신규 범주)** |
| 시스템 수준 실패 | 없음 | 없음 | 없음 | 없음 |

## Pattern Check

Pattern 여부는 판단하지 않는다. 4개 실험 중 몇 개에서 관찰되었는지
횟수만 기록한다.

| 현상 | Observation Count(4개 실험 중) |
|---|---|
| Repository Search(Grep/탐색적 검색) | 3 |
| Spec-Repository Staleness Mismatch(보고 기준) | 3 |
| 신규 파일 생성 | 2 |
| Diff/Patch 관찰 가능(기존 파일 존재) | 2 |
| 코드 작성 전 사전 실측 | 2 |
| 모듈/상대 import 경로 오류 | 1 |
| Self-Referential Recursion | 1 |
| Spec Internal Duplication(명시적 인지) | 1 |
| 다중 파일 수정(2개 이상) | 1 |
| Generated Artifact Self-Inclusion(보고만) | 1 |
| stdout 측정 리포트 산출 | 1 |
| Commit 생성 | 0 |
| 입력 Artifact의 상태 갱신(state 전이) | 0 |
| 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) | 0 |

## Artifact Mapping

기존 Artifact와 실제 산출물 사이에서 **관찰된** 대응만 기록한다.

| 기존 Artifact 요소 | 관찰된 대응 |
|---|---|
| Prompt Specification `Target File` | 그 경로에 실제 파일이 생성됨. |
| Prompt Specification `Public Interface` | 해당 시그니처 함수가 생성 파일에 존재하고 실행됨. |
| Prompt Specification `Interfaces`(check_1~4) | 4개 함수 모두 생성되었고 실행 시 모두 `True` 반환. |
| Prompt Specification `Dependencies`(4개 파일) | 4개 모두 실제로 읽힘(T4~T7). |
| Model Request `request_id` | 생성 파일 docstring에 문자열로 인용됨. 다른 사용 없음. |
| Execution Handle `handle_id` | 생성 파일 docstring에 문자열로 인용됨. 다른 사용 없음. |
| Execution Handle `status: PENDING` | 대응 행동 관찰되지 않음. |
| Execution State `state: PENDING` | 대응 행동 관찰되지 않음. state 전이 산출물 없음. |
| `created_at` / `submitted_at` / `changed_at` / `target_engine`(모두 `unresolved`) | 실행을 막지 않았고, 질문도 유발하지 않았다. |

## Unknowns

관찰되지 않은 것을 모두 기록한다. 추측하지 않는다.

- 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지 — 네 실험 모두
  확인하지 않았다.
- 봉투 계층(Model Request / Handle / State)이 **필요한지** — 이 실험은
  "봉투를 넣어도 실행이 성립한다"만 관찰했다. 봉투를 제거했을 때와의
  대조 실험은 하지 않았다.
- `state: PENDING`이 아닌 다른 state 값(RUNNING/SUCCEEDED/FAILED 등)을
  입력했을 때 행동이 달라지는지 — 관찰하지 않았다.
- Prompt Specification 본문 3회 중복이 결과에 영향을 주었는지 — 중복
  없는 입력과의 대조 실험을 하지 않아 판단 불가.
- 여러 개별 산출물(신규 파일 2개, stdout 측정 리포트, pytest 결과,
  6개 항목 텍스트 보고)을 **하나의 Execution Result로 묶는 방식** —
  여전히 Unknown. 이번 실험에서 Engine은 그 묶음을 자기 형식으로
  반환하지 않았다. 실험자가 요구한 6개 항목 형식이 산출물을 나열했을
  뿐이다.
- Engine이 스스로 정의하는 Execution Result 형태가 있는지 — 관찰되지
  않았다(요구 형식 없이 실행했을 때 무엇을 반환하는지는 네 실험 모두
  시험하지 않았다).
- 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit)가 실제로
  어떤 형태로 반환되는지 — 네 실험 모두 발생하지 않았다.
- Generated Artifact Self-Inclusion이 일반적 현상인지 이번 1회의
  우연인지 — 1회 관찰로는 판단 불가.

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result를 설계하지
않는다. Execution Result Contract/Schema를 결정하지 않는다. Execution
Layer를 수정하지 않는다. RFC/ADC/ADR을 생성하지 않는다.

실험 4건에 걸쳐 다음 사실만 기록한다: Model Request + Execution Handle +
Execution State 3계층을 그대로 Engine 입력으로 주었을 때 실행은 정상
종료했고, 봉투 계층에서 관찰된 유일한 효과는 `request_id`와 `handle_id`
두 식별자가 생성 산출물의 docstring에 문자열로 인용된 것이었다.
`status`/`state`의 `PENDING` 값과 `unresolved` 타임스탬프들은 실행을
막지도, 어떤 상태 전이 산출물도 만들지도 않았다. 산출물은 신규 파일
2개 + stdout 측정 리포트 + pytest 결과 + 텍스트 보고 4가지 형태로
나타났고, 이들을 하나로 묶는 Engine 자신의 형식은 관찰되지 않았다.
