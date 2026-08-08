# Engine Integration Research 0006: Claude Code — Execution Protocol Observation (결합 명시 요구)

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. ENGINE-INTEGRATION-0001~0005의 여섯 번째
Observation이며, 목적은 R-2의 마지막 Observation Gap 하나를 확인하는
것이다:

"Engine에게 여러 실행 산출물을 하나의 결과로 묶어 반환하도록
**명시적으로 요청하면** 무엇이 관찰되는가?"

Architecture 판단, Execution Result 설계, Contract/Schema 결정,
String/Artifact List/Reference 선택, 새 Artifact/Component/Layer 정의,
Gateway/Adapter/Registry/Scheduler/Runtime 도입, Execution Layer 수정,
RFC/ADC/ADR 작성, Baseline 수정은 하지 않는다. 관찰된 사실만 기록한다.

## Experiment

**추가한 것은 문장 하나뿐이다.** ENGINE-INTEGRATION-0005의 프롬프트에
다음 한 줄만 추가했다.

> 실행 과정에서 발생한 산출물을 하나의 결과로 묶어서 반환하라.

반환 형식은 **지정하지 않았다** — 항목 목록, 자료형, 구조, 필드 이름,
파일 여부 중 어느 것도 주지 않았다.

| 조건 | 0004 | 0005 | 0006 |
|---|---|---|---|
| 입력 Artifact | 3개 전문 | 동일 | **동일(한 글자도 바꾸지 않음)** |
| 결과 포맷 요구 | 6개 항목 지정 | 없음 | 없음 |
| 결합 요구 | 없음 | 없음 | **있음(형식 미지정)** |
| 실행 환경 | fresh session 1회 | 동일 | 동일 |
| Worktree | isolated, base `77bef0c`, seed 없음 | 동일 | 동일(`experiment-0006-manual`, 브랜치 `experiment-0006-seed`) |
| 작업 디렉토리 제약 / 커밋 금지 / "질문하지 말라" | 있음 | 동일 | 동일 |
| 시작 상태 | clean, `generated/` 부재 | 동일 | 동일(실험자 직접 확인) |

- **Repository 상태**: 메인 저장소는 커밋 `07b726a` 위에서 변경 없이
  유지되었다(실행 전후 `git status --porcelain` 모두 빈 출력).
- 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지는 이번에도
  확인하지 않았다 — Unknown.

## 1. Engine이 실제로 수행한 행동

tool use 24회(0001: 25, 0002: 19, 0003: 33, 0004: 19, 0005: 19,
0006: 24).

- 세 Artifact를 "하나의 구현 요청"으로 취급했다고 스스로 보고했다.
- `engine.py`의 아티팩트 연쇄를 읽고, Stage별로 어떤 Context 카테고리가
  하류에서 실제로 소비되는지 조사했다.
- 기존 `collect_relevant_context()`는 수정하지 않고, 소비 측에 규칙
  기반 완화 2종(Stage Projection, Artifact Scrub)을 새 파일 안에 두었다.
- **실행 도중 자기 구현의 결함을 스스로 발견해 고쳤다** — 최초 scrub가
  `## Reference Context` 본문을 통째로 삭제해 leak은 막았지만
  `engine.py::_extract_dependencies`가 그 블록에서 파싱하는
  `source_code:`/`existing_workflow:` 줄까지 사라져 Implementation
  Specification의 Dependencies가 비었다. 삭제를 투영(projection)으로
  바꾸고 그 회귀를 `check_1`에 넣었다고 보고했다. (자기 결함의
  실행 중 자체 발견·수정은 0003, 0005에 이어 세 번째 관찰이다.)
- 기존 파일은 하나도 수정하지 않았다.

## 2. 생성·수정된 파일

실험자가 worktree에서 직접 확인한 값이다.

| 항목 | 관찰 결과 |
|---|---|
| New Files | 2개 — `development-hq/mvp/generated/project_intelligence.py`(430줄), `development-hq/mvp/generated/__init__.py`(7줄) |
| Modified Files | **0개** — `git diff --stat` 빈 출력 |
| **결합 결과를 담은 별도 파일** | **없음.** `find development-hq/mvp/generated -type f`로 확인한 결과 파일은 위 2개뿐이다. 결합 요구를 받았음에도 result/summary/manifest 성격의 파일은 생성되지 않았다. |
| Commit | 없음 — worktree HEAD `77bef0c` 그대로 |
| `git status --porcelain`(worktree) | `?? development-hq/mvp/generated/` 1줄 |
| `git status --porcelain`(main) | 빈 출력(실행 전후 동일) |
| Artifact 식별자 인용 | `request 099012e5add6bcb1`가 파일 첫 줄 docstring에 1회. `handle_id`는 인용되지 않았다(0005와 동일, 0004와 다름). |
| 입력 Artifact 갱신 | 없음 — `state: PENDING` 그대로, 상태 전이 산출물 없음 |

## 3. 반환된 결과

### 3-1. Engine이 반환한 것(실행 결과 자체)

자유 서술형 산문 1개. Engine이 그 자리에서 정한 굵은 글씨 소제목으로
구성되었다.

- 첫 문장: "I executed the three artifacts as an implementation request
  and produced the target file."
- **Sanity check run** — 4개 acceptance check, 기존 테스트 스위트,
  `git status`, 커밋 생성 여부를 **한 문장 안에 함께** 서술
- **Files created** — 파일 경로 2개를 bullet list로 인라인 나열
- **What it does** — 구현 내용 서술
- **Measured result** — 측정치 서술
- **One real defect I found and fixed mid-task** — 자기 결함 서술
- 마지막에 한 문장짜리 요약 1줄(`result`)

### 3-2. 생성된 코드의 반환값(실험자가 직접 실행해 확인)

이것은 Engine의 실행 결과가 아니라 **생성된 Artifact 자신의 동작**이다.
둘을 구분해 기록한다.

| 실행 | 관찰 결과 |
|---|---|
| `python3 -m mvp.generated.project_intelligence` | exit 0. stdout 4줄: `check_1: PASS` ~ `check_4: PASS`. stderr 0 bytes. |
| `project_intelligence()` (인자 없음) | **TypeError** — "Issue dict 또는 Artifact 문자열을 필요로 한다". 0004·0005의 생성 모듈은 인자 없이 호출이 가능했다. |
| `project_intelligence(REAL_ISSUE, mode="pipeline")` | `dict`, 키 5개: `context`, `stage_context`, `planning`, `design`, `implementation` |
| `project_intelligence(mode="selfcheck")` | `dict`, 키 4개: `check_1`~`check_4`, 모두 `True` |

### 3-3. 진단

| 항목 | 관찰 결과 |
|---|---|
| Engine이 스스로 실행한 테스트 범위 | "기존 스위트 3 passed"라고 보고(0005와 동일, 0004는 42개 범위). |
| 실험자가 0004와 같은 범위로 재실행 | `python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q` → **42 passed**. |
| Engine이 보고한 측정치 | Planning 전용 경로 leak 6건 → 0건. Design 4465 → 3605자, Implementation 6665 → 5617자. 실험자는 이 수치를 재현하지 않았다 — Engine 보고값으로만 기록한다. |

## 4. 여러 산출물을 묶었는지 여부

**부분적으로 묶었다. 단, 묶인 것은 "설명"이지 "결과 객체"가 아니다.**

관찰된 것과 관찰되지 않은 것을 나눠 기록한다.

**관찰된 것**

- 산출물 전부(파일 2개, check 4개, 테스트 결과, git 상태, 커밋 여부,
  측정치, 자기 결함)를 **하나의 자연어 메시지 안에** 담아 반환했다.
- 그중 상태성 항목 4가지(check 결과 / 테스트 통과 / `git status` /
  커밋 없음)는 **한 문장으로 합쳐서** 제시되었다 — 0005에서는 이
  항목들이 산문 여러 곳에 흩어져 있었다.
- 파일 목록은 bullet list로 한곳에 모였다.

**관찰되지 않은 것**

- 이름 붙은 단일 결과 객체 / 봉투(Envelope)
- 안정적인 필드 집합(파일·diff·진단·로그를 담는 고정 슬롯)
- 기계가 파싱 가능한 형식(JSON/YAML/구분자 있는 구조)
- 산출물 전체를 가리키는 단일 참조(Reference)
- 결합 결과를 담은 **파일**(위 2절 — 생성 파일은 2개뿐)
- 입력 Artifact의 식별자(`request_id`/`handle_id`)를 반환 결과에
  붙이는 행동 — 반환 메시지에는 두 ID 모두 나타나지 않았다
- 상태(state) 전이나 완료 표식

## 5. 묶었다면 실제 관찰된 형태

**형태: 자연어 산문 1개 + 그 안의 인라인 열거.**

구체적으로 관찰된 구성 요소는 다음 4가지이며, 이들은 Engine이 이번
실행에서 즉석으로 정한 것이다(0004의 6개 항목과도, 0005의 소제목과도
일치하지 않는다).

1. 한 문장 상태 roll-up(check + 테스트 + git 상태 + 커밋 여부)
2. 파일 경로 bullet list(절대 경로 2개)
3. 서술형 본문(구현 내용 / 측정치 / 자기 결함)
4. 한 문장 최종 요약

세 실험을 나란히 두면 다음이 관찰된다.

| | 0004(포맷 지정) | 0005(요구 없음) | 0006(결합 요구) |
|---|---|---|---|
| 반환 매체 | 텍스트 | 텍스트 | 텍스트 |
| 항목 구성의 출처 | 실험자 | Engine(즉석) | Engine(즉석) |
| 실행마다 동일한 형식인가 | 해당 없음 | 아니오 | **아니오** |
| 상태 항목의 집약 | 항목별 분리 | 산문에 분산 | **한 문장으로 집약** |
| 단일 결과 **객체** | 없음 | 없음 | **없음** |
| 결합 결과 **파일** | 없음 | 없음 | **없음** |
| 결과에 request/handle ID 부착 | 없음 | 없음 | **없음** |

## 6. Pattern Check

Pattern 여부는 판단하지 않는다. 6개 실험 중 관찰 횟수만 기록한다.

| 현상 | Observation Count(6개 실험 중) |
|---|---|
| 신규 파일 생성 | 4 |
| 실행 중 자기 구현 결함을 스스로 발견·수정 | 3 (0003, 0005, 0006) |
| Spec-Repository Staleness Mismatch(보고 기준) | 3 |
| 코드 작성 전/중 실측 조사 | 4 |
| Diff/Patch 관찰 가능(기존 파일 존재) | 2 |
| 반환값이 구조화된 자료형(dict) | 2 (0005, 0006) |
| 생성 모듈의 무인자 호출 가능 | 2 (0004, 0005) |
| 생성 모듈의 무인자 호출이 TypeError | 1 (0006) |
| 입력 Artifact의 상태 갱신(state 전이) | 0 |
| Commit 생성 | 0 |
| **Engine 자체 정의의 단일 Execution Result 객체** | **0** |
| **결합 결과를 담은 파일 산출** | **0** |
| 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) | 0 |

## 7. Unknowns

- Engine이 즉석으로 만드는 산문 구성이 실행마다 달라지는 폭 —
  세 실행(0004·0005·0006)에서 매번 달랐다는 사실만 관찰했다. 무엇이
  그 차이를 만드는지는 관찰되지 않았다.
- **특정 형식**(예: JSON, 고정 필드, 파일 산출)을 지정해 결합을
  요구했을 때의 행동 — 이 실험은 형식을 지정하지 않았으므로 미관찰.
- 0004 생성 모듈의 반환값 형태 — 여전히 미관찰(0005·0006만 확인).
- Engine이 선택한 테스트 범위가 실행마다 다른 이유(42 vs 3 vs 3).
- 생성 모듈의 호출 규약이 실행마다 다른 이유(무인자 호출 가능 vs
  TypeError).
- Engine이 보고한 측정치의 재현성 — 실험자는 0005·0006 모두
  재현하지 않았다.
- 하위 subagent의 실제 모델(버전) — 여섯 실험 모두 확인하지 않았다.
- `state`가 `PENDING`이 아닐 때의 행동 — 시험하지 않았다.
- 시스템 수준 실패의 반환 형태 — 여섯 실험 모두 발생하지 않았다.

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result Contract /
Schema를 결정하지 않는다. String / Artifact List / Reference 중 어느
것도 선택하지 않는다. 새 Artifact / Component / Layer / Gateway /
Adapter / Registry / Scheduler / Runtime을 정의하지 않는다. RFC / ADC /
ADR을 생성하지 않는다. Baseline을 수정하지 않는다.

기록하는 사실은 하나다: 형식을 지정하지 않고 "산출물을 하나의 결과로
묶어 반환하라"고 명시적으로 요구했을 때, Engine은 모든 산출물을 하나의
**자연어 산문 메시지** 안에 담아 반환했고, 상태성 항목들을 한 문장으로
집약했다. 그러나 이름 붙은 결과 객체, 고정 필드, 기계 파싱 가능 형식,
단일 참조, 결합 결과 파일, 결과에 부착된 request/handle 식별자는
여섯 실험 모두에서 한 번도 관찰되지 않았다.
