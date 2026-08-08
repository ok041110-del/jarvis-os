# Engine Integration Research 0005: Claude Code — Execution Protocol Observation (결과 포맷 요구 제거)

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 Execution
Protocol Observation이다. ENGINE-INTEGRATION-0001~0004의 다섯 번째
Observation이며, 목적은 R-2의 **미관찰 원인을 좁히는 것** 하나다:
"ENGINE-INTEGRATION-0004에서 여러 산출물이 하나의 Execution Result로
묶이지 않은 것은, 실험자가 6개 항목 보고 형식을 지정했기 때문인가?"

Architecture 판단, Execution Result 설계, Contract/Schema 결정,
String/Artifact List/Reference 선택, 새 Artifact/Component/Layer 정의,
Execution Layer 수정, RFC/ADC/ADR 작성, Baseline 수정은 하지 않는다.
관찰된 사실만 기록한다. 관찰되지 않은 것은 모두 Unknown으로 남긴다.

## Experiment

**단 하나만 바꿨다.** ENGINE-INTEGRATION-0004의 프롬프트에서
`===== 보고 형식 (이 6개 항목만) =====` 블록 전체를 삭제했다. 결과
포맷에 대한 어떤 요구도 남기지 않았다. 그 외 모든 조건은 0004와
동일하다.

| 조건 | 0004 | 0005 |
|---|---|---|
| 입력 Artifact | Model Request + Execution Handle + Execution State 전문 | **동일(한 글자도 바꾸지 않음)** |
| 결과 포맷 요구 | 6개 항목 지정 | **없음(블록 삭제)** |
| 실행 환경 | Claude Code Agent 도구, fresh session 1회 | 동일 |
| Worktree | isolated, base `77bef0c`, seed 없음 | 동일(`experiment-0005-manual`, 브랜치 `experiment-0005-seed`) |
| 작업 디렉토리 제약 / 커밋 금지 / "질문하지 말라" | 있음 | 동일 |
| 시작 상태 | clean, `generated/` 부재 | 동일(실험자가 `git status --porcelain`으로 직접 확인) |

- **Repository 상태**: 메인 저장소는 커밋 `22ccdbb` 위에서 변경 없이
  유지되었다(실행 전후 `git status --porcelain` 모두 빈 출력).
- **중단된 1차 시도(사실 기록)**: 첫 실행은 tool use 11회 시점
  (Dependencies 파일 읽기 단계)에서 **환경 요인**(Claude 세션 사용량
  한도, 04:00 UTC 리셋)으로 중단되었다. Engine 자체의 실패가 아니다.
  중단 시점 worktree는 완전히 clean이었고 `generated/`는 생성되지
  않았다 — 부분 산출물이 없었으므로 동일 worktree에서 오염 없이
  재실행했다. 아래 기록은 모두 완주한 2차 실행의 관찰이다.
- 하위 subagent가 실제로 어떤 모델(버전)로 실행되었는지는 이번에도
  확인하지 않았다 — Unknown.

## 1. Engine이 실제로 수행한 행동

subagent가 스스로 보고한 범위와 실험자가 산출물로 확인한 범위만
기록한다. 총 tool use 19회(0001: 25, 0002: 19, 0003: 33, 0004: 19,
0005: 19).

- 세 Artifact의 중첩 구조(State ⊃ Handle ⊃ Model Request)를 **명시적으로
  인지하고 보고했다** — "세 Artifact는 하나의 Model Request로 귀결된다"고
  스스로 서술했다. 0004에서는 이 인지가 보고에 나타나지 않았다.
- `engine.py`의 3개 함수(`_analyze_requirement`, `_design_from_requirement`,
  `_generate_code`)를 읽고 Requirement→Design→Implementation 연쇄
  경로를 추적했다.
- `_extract_dependencies`가 `source_code`/`existing_workflow` 두 줄만
  읽는다는 사실을 확인하고, 이를 근거로 카테고리를 "downstream이 실제로
  소비하는 것"과 "Planning 전용"으로 나눴다.
- 구현 도중 **자신의 첫 구현에 있던 측정 오류를 스스로 발견해 수정했다**
  — leak 측정에 단순 부분문자열 매칭을 써서 `development-hq/mvp/`가
  `development-hq/mvp/engine.py`의 접두사라는 이유만으로 leak으로
  집계되었고, 그 때문에 check_4가 실패했다. 이를 "긴 경로부터 제거 후
  검색"으로 바꿨다고 보고했다.
- 기존 파일은 하나도 수정하지 않았다.

## 2. 생성·수정된 파일

실험자가 worktree에서 직접 확인한 값이다.

| 항목 | 관찰 결과 |
|---|---|
| New Files | 2개 — `development-hq/mvp/generated/project_intelligence.py`(369줄), `development-hq/mvp/generated/__init__.py`(**0줄, 빈 파일**) |
| Modified Files | **0개** — `git diff --stat` 빈 출력 |
| Commit | 없음 — worktree HEAD `77bef0c` 그대로 |
| `git status --porcelain`(worktree) | `?? development-hq/mvp/generated/` 1줄 |
| `git status --porcelain`(main) | 빈 출력(실행 전후 동일) |
| Artifact 식별자 인용 | `request_id 099012e5add6bcb1`가 파일 첫 줄 docstring에 1회. `handle_id`는 **인용되지 않았다**(0004에서는 두 식별자 모두 인용되었다). |
| 입력 Artifact 갱신 | 없음 — `state: PENDING` 그대로, 어떤 상태 전이 산출물도 생성되지 않았다. |

## 3. stdout / stderr 등 관찰 가능한 결과

실험자가 직접 실행해 확인했다.

| 실행 방식 | 관찰 결과 |
|---|---|
| 스크립트 실행 `python3 .../generated/project_intelligence.py` | **실패**. exit code 1, stdout 0줄, stderr 276 bytes: `ImportError: attempted relative import with no known parent package`(line 44, `from ..agents import (`). |
| import 모드 실행(`development-hq`를 cwd로, `from mvp.generated.project_intelligence import ...`) | **성공**. exit 0. `project_intelligence()`의 반환 타입은 `dict`, 키 7개: `issue`, `stage`, `context`, `propagating`, `planning_only`, `scoped`, `enriched_issue`. `check_1~4` 모두 `True`. |

0004와의 차이(사실만): 0004의 생성 모듈은 스크립트 실행이 성공했고
5개 절로 이루어진 측정 리포트를 stdout으로 출력했다. 0005의 생성
모듈은 스크립트 실행이 ImportError로 실패하며, stdout 리포트 자체가
없다. 대신 0005는 **함수 반환값이 7키 dict**다. 0004의 반환값 형태는
이 문서가 관찰하지 않았다.

## 4. 테스트·진단 결과

| 항목 | 관찰 결과 |
|---|---|
| Engine이 스스로 실행한 테스트 범위 | subagent는 "기존 테스트 3개 통과"라고 보고했다 — 0004의 subagent는 42개 범위를 실행했다. 동일 저장소·동일 커밋인데 **Engine이 선택한 진단 범위가 달랐다**. |
| 실험자가 0004와 같은 범위로 재실행 | `python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q` → **42 passed**. |
| check 함수 | `check_1~4` 모두 `True`(실험자가 import 모드로 직접 확인). |
| Engine이 보고한 측정치 | Planning 전용 경로 leak: Design 12 → 0, Implementation 12 → 0. `## Dependencies` 출력은 byte-identical 유지(대조군). 실험자는 이 수치를 재현하지 않았다 — Engine 보고값으로만 기록한다. |

## 5. Engine이 여러 산출물을 스스로 하나의 결과로 묶는 행동의 존재 여부

이번 실험의 핵심 관찰 지점이다.

**관찰 결과: 그런 행동은 관찰되지 않았다.**

결과 포맷 요구를 완전히 제거했음에도 Engine이 반환한 것은 다음
형태였다.

- 자유 서술형 산문 + Engine이 **그 자리에서 임의로 정한 굵은 글씨
  소제목**("What I executed", "The substantive finding", "One bug I
  found in my own first pass", "Files written")
- 그 산문 안에 파일 경로 2개가 bullet list로 인라인 나열됨
- 별도로 한 문장짜리 요약(`result`) 1줄

즉 관찰된 것은 **자연어 산문**이며, 다음 중 어느 것도 관찰되지 않았다.

- 이름 붙은 단일 결과 객체 / 봉투(Envelope)
- 안정적인 필드 집합(파일·diff·진단·로그를 구분해 담는 고정 슬롯)
- 기계가 파싱 가능한 형식(JSON/YAML/구분자 있는 구조)
- 산출물 전체를 가리키는 단일 참조(Reference)
- 상태(state) 전이나 완료 표식

0004와 0005를 나란히 두면 관찰되는 사실은 이렇다.

| | 0004(포맷 요구 있음) | 0005(포맷 요구 없음) |
|---|---|---|
| 반환 형태 | 실험자가 지정한 6개 항목 | Engine이 즉석에서 정한 산문 소제목 |
| 항목 구성의 출처 | 실험자 | Engine(단, 매 실행마다 새로 정해짐 — 0004와 겹치는 고정 형식 아님) |
| 파일 목록 | 별도 항목으로 분리됨 | 산문 안에 인라인 나열 |
| 진단 결과 | 별도 항목으로 분리됨 | 산문 안에 문장으로 서술 |
| 단일 Execution Result 객체 | 없음 | **없음** |

따라서 이번 실험이 좁힌 것은 다음 한 가지다: **0004에서 결합이
관찰되지 않은 원인은 "실험자가 포맷을 지정했기 때문"이 아니다.**
포맷 요구를 제거해도 Engine은 자기 정의의 결합된 Execution Result를
내놓지 않았다.

이 관찰이 "Engine에 그런 능력이 없다"를 뜻하는지, "이 입력 형태에서
그런 행동이 유도되지 않는다"를 뜻하는지는 **이 문서가 판단하지
않는다**. 두 실험 모두 Engine에게 결합을 요구한 적이 없다.

## 6. Artifact Mapping

기존 Artifact와 산출물 사이에서 **관찰된** 대응만 기록한다.

| 기존 Artifact 요소 | 관찰된 대응 |
|---|---|
| Prompt Specification `Target File` | 그 경로에 파일 생성됨. |
| Prompt Specification `Public Interface` | 해당 시그니처 함수 존재, 호출 시 `dict` 반환. |
| Prompt Specification `Interfaces`(check_1~4) | 4개 함수 모두 존재, 모두 `True`. |
| Prompt Specification `Dependencies`(4개 파일) | 모두 읽힘(subagent 보고 + `engine.py` 3개 함수 추적으로 확인). |
| Model Request `request_id` | 생성 파일 docstring에 문자열 1회 인용. |
| Execution Handle `handle_id` | **인용되지 않음**(0004와 다름). |
| Execution Handle `status: PENDING` / Execution State `state: PENDING` | 대응 행동 관찰되지 않음. 상태 전이 산출물 없음. |
| `created_at`/`submitted_at`/`changed_at`/`target_engine`(모두 `unresolved`) | 실행을 막지 않았고 질문도 유발하지 않았다(0004와 동일). |

## 7. Pattern Check

Pattern 여부는 판단하지 않는다. 5개 실험 중 관찰 횟수만 기록한다.

| 현상 | Observation Count(5개 실험 중) |
|---|---|
| 신규 파일 생성 | 3 |
| 코드 작성 전/중 실측 조사 | 3 |
| Spec-Repository Staleness Mismatch(보고 기준) | 3 |
| Diff/Patch 관찰 가능(기존 파일 존재) | 2 |
| 실행 중 자기 구현 오류를 스스로 발견·수정 | 2 (0003 RecursionError, 0005 부분문자열 측정 오류) |
| 생성 모듈의 스크립트 실행 성공 | 1 (0004) |
| 생성 모듈의 스크립트 실행 실패(ImportError) | 1 (0005) |
| stdout 측정 리포트 산출 | 1 (0004) |
| 반환값이 구조화된 자료형(dict) | 1 (0005 — 단, 0004는 미관찰) |
| 입력 Artifact의 상태 갱신(state 전이) | 0 |
| Commit 생성 | 0 |
| **Engine 자체 정의의 단일 Execution Result** | **0** |
| 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) | 0 |

## 8. Unknowns

- **Engine에게 "여러 산출물을 하나로 묶어 반환하라"고 요구했을 때
  무엇을 내놓는지** — 다섯 실험 모두 요구한 적이 없다. 이번 실험은
  "요구를 제거"했을 뿐, "결합을 요구"하지는 않았다.
- 0004 생성 모듈의 `project_intelligence()` 반환값 형태 — 관찰하지
  않았다. 따라서 "반환값이 dict"가 0005 고유인지 공통인지 판단 불가.
- 두 실행에서 Engine이 선택한 진단 범위가 다른 이유(3개 vs 42개) —
  관찰되지 않았다.
- 생성 모듈의 스크립트 실행 가능 여부가 갈린 이유(0004 성공, 0005
  ImportError) — 관찰되지 않았다.
- 하위 subagent의 실제 모델(버전) — 다섯 실험 모두 확인하지 않았다.
- `state`가 `PENDING`이 아닌 다른 값일 때의 행동 — 시험하지 않았다.
- 시스템 수준 실패가 반환되는 형태 — 다섯 실험 모두 발생하지 않았다
  (0005 1차 시도의 중단은 Engine 실패가 아니라 실험 환경의 사용량
  한도였다).

## Conclusion

이 문서는 Architecture를 판단하지 않는다. Execution Result Contract /
Schema를 결정하지 않는다. String / Artifact List / Reference 중 어느
것도 선택하지 않는다. 새 Artifact / Component / Layer를 정의하지
않는다. RFC / ADC / ADR을 생성하지 않는다. Baseline을 수정하지 않는다.

기록하는 사실은 하나다: 결과 포맷 요구를 완전히 제거한 조건에서도
Engine은 여러 산출물(파일 2개, 함수 반환 dict, 진단 결과, 자유 서술
보고)을 자기 정의의 단일 Execution Result로 묶어 반환하지 않았다.
따라서 ENGINE-INTEGRATION-0004에서 결합이 관찰되지 않은 원인은
실험자의 포맷 지정이 아니다. Engine에게 결합을 **요구**했을 때의
행동은 다섯 실험 모두에서 여전히 미관찰이다.
