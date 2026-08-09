# MVP-0041 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — Development HQ 전체 SDLC(Planning → Design →
Implementation → Review → Test)를 real Engine으로 1회 Dogfooding하고,
그 결과(특히 Review가 지적한 실제 결함)를 반영해 실제 코드베이스에
구현했다.

## 목적

`MVP-0038`~`0040`이 개별 Capability(`project_intelligence`,
`code_generation`, `workflow_0002`)를 하나씩 점검·수정한 것과 달리,
이번에는 **실제 개발 업무 하나를 선정해 Development HQ 전체 흐름을
처음부터 끝까지 Dogfooding**한다 — `workflow_0008.run_pipeline()`
(Project Intelligence → Planning → Design → Implementation →
Validation(Review+Test))을 real Issue 하나로 완주시키고, 그 과정에서
드러난 문제를 이 한 세션 안에서 연속으로 고친다. 문제를 작은 단위로
쪼개 별도 MVP로 나누지 않는다(지시).

## 선정한 실제 업무

기존 코드를 직접 실행해 확인한 실제 결함을 Issue로 그대로 썼다:

```
title: "Validate Issue dict before Project Intelligence processing"
description: collect_relevant_context(issue)가 issue dict에
  title/description 키가 없으면 KeyError만 던진다
  (collect_relevant_context({'title': 'x'}) → KeyError('description'),
  무엇이 왜 잘못됐는지 아무 맥락이 없음). Project Intelligence가 issue를
  참조하기 전에, 어떤 필수 필드가 문제인지 명확히 알려주는 검증
  단계를 추가해야 한다. 이미 유효한 issue(title/description이 있는
  경우)의 동작은 바뀌면 안 된다.
```

이 결함은 이 MVP를 시작하기 전 직접 실행으로 먼저 재현해 확인했다:
`collect_relevant_context({'title': 'x'})` → `KeyError: 'description'`,
`collect_relevant_context({})` → `KeyError: 'title'` — 어느 쪽도 어떤
Issue가 문제였는지, 무엇이 기대되는지 알려주지 않는다.

## 1. Planning → Design → Implementation → Review → Test 전체 실행 (real Engine, 187.0초)

`workflow_0008.run_pipeline(issue)`를 1회 실행해 5단계 전부를 완주했다
(mock 없음, 실제 `claude -p` 호출 5회).

| Stage | 길이(문자) |
|---|---|
| planning | 5,835 |
| design | 5,383 |
| implementation | 2,808 |
| code_review | 2,495 |
| test_execution | 4,686 |

5단계 모두 예외 없이 완주했다 — Engine이 작성을 거부하거나
(`MVP-0030` 현상) 코드 대신 산문을 반환하는 일이 없었다. Design은
`IssueValidationError`라는 전용 예외 타입과, `title`/`description`을
필수 필드로 검사하는 `validate_issue()` 함수를 제안했고,
Implementation은 그 Design을 그대로 구현한 코드를 반환했다.

## 2. Review가 실제로 찾아낸 문제 (Engine이 스스로 낸 Implementation을 real Engine이 리뷰)

`backend_agent_code_review()`가 Engine 자신이 만든 Implementation을
검토해 실제로 유효한 결함 3가지를 지적했다:

1. **비-dict 입력에서 처리되지 않은 crash**: `issue`가 `None`이거나
   dict가 아니면 `"title" not in None`이 `TypeError`를 던져,
   `IssueValidationError`로 잡을 수 있어야 할 caller가 다른 예외
   타입을 받게 된다 — 애초에 이 모듈이 막으려던 "malformed input"의
   가장 흔한 형태를 오히려 놓친다.
2. **`None`/빈 문자열 외의 잘못된 값(falsy/wrong-typed)을 통과시킴**:
   `title=0`, `title=[]`, `title=False` 등이 검증을 그대로 통과해
   버린다.
3. **`_resolve_identifier`가 그 자체로 예외를 던질 수 있음**: 이 Design이
   제안한 다중 식별자 우선순위 로직(`id`/`issue_id`/`key`)의 부수적
   결함.

이 3가지 중 1·2는 실제 결함이었고(아래 "실제 코드베이스 구현"에서
고쳤다), 3은 애초에 이 저장소가 쓰지 않는 기능(아래 참고)이라 그
기능 자체를 들이지 않는 방식으로 해소했다.

## 3. 실제 코드베이스 구현 — Review 결과를 반영해 최소화

Engine이 제안한 Implementation을 그대로 복사하지 않고, Review가
찾아낸 실제 결함(1·2)만 고치면서 이 저장소에 존재하지 않는 개념은
들이지 않았다: `_IDENTIFIER_FIELDS = ("id", "issue_id", "key")`와
그 우선순위 해석 로직(`_resolve_identifier`)은 이 저장소의 실제
Issue fixture 전부(`REAL_ISSUE`/`CODE_ISSUE`, `MVP-0007~0032`)가
`title`/`description`/`status`만 쓸 뿐 `id` 계열 필드를 쓴 적이
없어 제외했다 — Review의 결함 3은 애초에 이 기능을 만들지 않는
것으로 해소된다(고치는 것이 아니라 만들지 않는 것).

- `development-hq/mvp/project_intelligence.py`
  - `IssueValidationError(ValueError)`(신규): `issue`가 dict가
    아니거나 필수 필드가 없거나 빈 값일 때 발생.
  - `validate_issue(issue)`(신규): (1) `isinstance(issue, dict)`를
    먼저 확인해 Review 결함 1(비-dict crash)을 해소하고, (2)
    `title`/`description` 각각을 `isinstance(value, str)`과
    비어있지-않음을 함께 확인해 Review 결함 2(falsy/wrong-typed
    통과)를 해소한다 — 문자열이 아니면 그 값이 무엇이든(0/[]/False
    포함) 실패로 처리되므로 별도 타입별 분기가 필요 없다.
  - `collect_relevant_context(issue)`: 맨 앞에 `validate_issue(issue)`
    호출을 추가했다. 그 뒤 로직(`issue['title']`/`issue['description']`
    참조, 카테고리별 파일 수집)은 한 글자도 바꾸지 않았다 — 유효한
    Issue의 동작은 그대로다.

## 4. 검증 (실제 실행, mock 없음)

### 4.1 결함 재현 케이스 7개 + 정상 케이스 1개

```
{'title': 'x'}                        -> OK: issue is missing required non-empty string field(s): description
{}                                     -> OK: issue is missing required non-empty string field(s): title, description
None                                   -> OK: issue must be a dict, got NoneType
['not', 'a', 'dict']                   -> OK: issue must be a dict, got list
{'title': 0, 'description': 'y'}       -> OK: issue is missing required non-empty string field(s): title
{'title': '   ', 'description': 'y'}   -> OK: issue is missing required non-empty string field(s): title
{'title': False, 'description': 'y'}   -> OK: issue is missing required non-empty string field(s): title
{'title': 'Fix bug', 'description': 'Something broke.'} -> 정상 처리, 기존과 동일한 8개 카테고리 키 반환
```

Review가 지적한 결함 1(비-dict)과 2(falsy/wrong-typed)가 모두
`IssueValidationError`로 명확하게 처리됨을 확인했다 — `TypeError`나
`KeyError`가 새지 않는다.

### 4.2 `build_context_bundle()`에도 자동으로 적용됨

`build_context_bundle()`은 내부에서 `collect_relevant_context()`를
호출하므로 별도 수정 없이 같은 검증을 상속받는다 — 실제 실행으로
확인: 유효한 Issue는 기존과 동일한 8개 키를 반환했고, `{'title': 'x'}`는
동일한 `IssueValidationError`를 그대로 전파했다.

### 4.3 실제 workflow 진입점에서 깨끗하게 전파되는지 확인

`workflow_project_intelligence.run_issue_to_planning({'title': 'x'})`를
직접 호출한 결과, `IssueValidationError`가 그대로 전파됐다(bare
`KeyError`가 아님). `collect_relevant_context(issue)` 호출은 각
workflow 함수의 `try/except`(MVP-0037, Engine 호출 실패 전용) **밖**에
있으므로 — 이는 의도된 배치다: 잘못된 Issue는 caller의 프로그래밍
오류이지 Engine의 일시적 실패가 아니므로, "Engine call failed"로
감싸 조용히 삼키지 않고 그대로 올라가 즉시 드러나야 한다.

### 4.4 실제 Engine으로 정상 경로 재확인 (회귀 없음)

유효한 Issue("Add caching to `_score()`")로
`run_issue_to_planning()`을 real Engine으로 재실행했다(40.1초) —
`context`가 기존과 동일한 8개 키를 반환했고, `planning`도 4,114자로
정상 반환됨을 확인했다. `collect_relevant_context()` 앞에 검증을
추가한 것이 정상 경로에 아무 영향을 주지 않았다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음, 77.3초).
- `git status --porcelain` — `development-hq/mvp/project_intelligence.py`
  1개 파일만 변경.

## 이번 세션에서 발견했으나 구조적이지 않다고 판단해 만들지 않은 것

Review가 지적한 결함 3(`_resolve_identifier`의 다중 식별자 우선순위
로직)은 이 저장소가 실제로 쓰지 않는 개념(`id`/`issue_id`/`key`
필드)을 전제로 한다 — 그 기능 자체를 만들지 않았으므로 "고칠 결함"이
아니라 "애초에 들이지 않은 기능"이다. 이는 Architecture 결정이
아니라(새 Concept/Component가 아니다), 기존 Issue Contract(`title`/
`description`/`status`만 쓴다는 이 저장소의 일관된 실제 사용
패턴, `MVP-0007~0032` 전수)를 그대로 따른 최소화 판단이다. 별도
보고나 중단이 필요한 구조적 문제가 아니었다.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 |
| 새 Capability/Agent/Engine 추가 | 미발동 — `validate_issue()`는 `collect_relevant_context()`의 기존 계약(입력 검증) 안의 헬퍼일 뿐, 새 Capability가 아니다 |
| 새 Architecture/Concept/Component 필요 | 미발동 |
| Production caller/Kernel Component/Runtime/Prompt Cache 착수 | 미발동 — 전혀 건드리지 않았다 |

**하나도 발동하지 않았다.** 구조적 Architecture 결정이 필요한 문제를
만나지 않아 중단·보고할 대상이 없었다 — 발견한 유일한 "더 큰" 결함
(Review 결함 3)도 새 기능을 만들지 않는 방식으로 이미 해소됐다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- Production caller, Kernel Component, Runtime, Prompt Cache —
  건드리지 않았다.
- `_IDENTIFIER_FIELDS`류 다중 식별자 기능 — 위 이유로 만들지 않았다.
- 새 RFC/ADC/ADR — 만들지 않았다. Architecture 결정이 필요한 지점을
  만나지 않았다.
- 같은 결함을 여러 MVP로 쪼개는 것 — 이번 세션 하나에서 Planning부터
  실제 코드 수정·검증까지 연속으로 완료했다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`project_intelligence.py`)**.
  실제 Dogfooding(전체 SDLC 1회 완주)이 드러낸 실제 결함을, Engine
  자신의 Review가 찾아낸 것 중 실제로 유효한 부분만 반영해 최소
  구현했다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `collect_relevant_context()`의 시그니처와 반환 Contract도
  그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. 전체 SDLC 1회(187.0초),
  정상 경로 재확인 1회(40.1초), 워크플로우 진입점 전파 확인 1회 —
  모두 real `claude -p` 호출(mock 없음). 기존 pytest 3건도 real
  Engine 포함 재실행해 회귀 없음을 확인했다.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. Planning
  → Design → Implementation → Review → Test 실행부터 Review가 찾은
  결함의 실제 수정·검증까지 이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
  만났다면 중단하고 보고했을 것이다(지시 4번) — 유일하게 "더 큰"
  후보(다중 식별자 필드)는 새 기능을 만들지 않는 것으로 해소되어
  중단·보고 대상이 아니었다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  Engine의 Implementation 제안을 그대로 채택하지 않고 Review 결과 중
  실제로 유효한 부분만 구분해 반영했음을 그대로 기록했다.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `engine.py`,
  `workflow*.py`, `cli.py` 어디에도 손대지 않았다(`git status
  --porcelain` 확인).
