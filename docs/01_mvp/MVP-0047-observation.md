# MVP-0047 Observation

**문서 성격**: 실제 실행 기록(Evidence). `MVP-0046`(notekeeper)이 발견한
Validation 한계 — `code_review` Capability가 존재하지 않는 모듈을
가리키는 import를 아무 언급 없이 통과시킨 것 — 를 기존 구조 안에서
해결할 수 있는지 직접 실험으로 검증했다. **단순 프롬프트 보강만으로
해결 가능함을 확인했고**, `development-hq/mvp/agents.py`
`backend_agent_code_review()`의 지시 문장 1개만 최소 수정했다.
Architecture/Contract는 전혀 바꾸지 않았다.

## 목적

`MVP-0046`(`projects/notekeeper/issues/0002-store`)에서 real
`code_review`가 `from .note import Note`(존재하지 않는 모듈)를 전혀
지적하지 못한 것을 관찰했었다. 이번 세션은 그 원인을 규명하고, 이
지시가 준 지시대로 (1) 결함을 재현 → (2) 단순 프롬프트 보강으로
해결되는지 먼저 확인 → (3) 해결되면 최소 수정 후 실제 Engine으로
재검증 → (4) Architecture 변경이 필요하면 중단 — 순서로 실행했다.

## 1. 원인 규명 — `code_review`의 입력 Contract 자체가 이 정보를 갖지 않는다

`development-hq/mvp/agents.py`/`engine.py`를 직접 읽어 확인: 
`backend_agent_code_review(code: str) -> str`은 파일 하나의 텍스트만
받는다. 다른 프로젝트 파일을 함께 넘기는 경로가 없고, `call_engine()`은
`--disallowedTools`로 `Read`/`Bash`/`Glob`/`Grep` 등을 전부 막아
Engine이 스스로 다른 파일을 열어보는 것도 불가능하다(`engine.py`
`DISALLOWED_TOOLS` 상수). 즉 "이 import가 가리키는 모듈이 실제로
존재하는가"라는 질문에 답할 정보 자체가 이 Capability의 입력에
없다 — 이는 프롬프트를 아무리 정교하게 써도 채울 수 없는 정보
공백이며, 먼저 이 사실을 확인한 뒤 "그렇다면 최소한 그 사실 자체를
명시적으로 말하게 할 수 있는가"로 질문을 좁혔다.

## 2. 결함 재현 — 실제 real Engine 호출

`MVP-0046`이 실제로 만든 버그 코드(`from .note import Note`, 실재하지
않는 모듈)를 그대로 **수정 전** `backend_agent_code_review()`에
입력했다:

```
$ python3 -c "... backend_agent_code_review(buggy_code) ..."
```

반환된 real Review는 8개 항목(상태 불일치, 동시성, 임시 파일 정리
등)을 지적했지만 `.note` import는 **한 번도 언급하지 않았다** —
결함 재현 성공.

## 3. 단순 프롬프트 보강 테스트 — 기존 `call_engine()` 그대로, 지시 문장만 변경

기존 함수를 수정하지 않고, 별도 스크립트에서 `call_engine()`(변경
없는 기존 단일 함수)에 지시 문장 한 줄만 추가한 프롬프트로 같은
버그 코드를 다시 리뷰했다:

> "For every `from .module import Name`-style relative import, you
> cannot verify that `module` actually exists as a sibling file or
> that `Name` is actually defined there — explicitly call out each
> such import as an unverified assumption that must be checked
> against the real project files, and say so even if the import looks
> syntactically fine."

결과(2회 반복 실행, mock 없음):

```
**Unverified import:** `from .note import Note` cannot be checked
from this file alone — I can't confirm `note.py` exists as a sibling
module...
```

두 번 모두 동일하게 정확한 import를 지목했다 — **재현 가능**.

### 오탐(False Positive) 확인 — 올바른 import에도 같은 프롬프트 적용

같은 프롬프트를 `MVP-0046`이 실제로 수정한 **올바른**
`store.py`(`from .models import Note`, 실재하는 모듈)에 적용:

```
**Unverified import.** `from .models import Note` cannot be checked
here — I have no visibility into whether `models.py` exists...
```

"검증할 수 없다"고만 말할 뿐 "틀렸다"고 오탐하지 않았다 — 사실
그대로(둘 다 실제로는 검증 불가능하다)를 정확히 반영한다.

## 4. 실제 코드베이스 구현 — 최소화

`development-hq/mvp/agents.py`의 `backend_agent_code_review()`
지시 문장에 위 실험으로 검증한 한 문장을 그대로 추가했다. 함수
시그니처(`code: str) -> str`), 호출 방식(`call_engine()` 1회 호출),
`NO_ISSUES_MARKER` 계약은 전혀 바꾸지 않았다 — 새 입력 파라미터나
Context 전달 경로를 추가하지 않았다(그러면 Contract 변경이 된다).
이미 참인 사실(자신이 볼 수 있는 범위의 한계)을 명시적으로 말하게
할 뿐이다.

## 5. 재검증 (실제 실행, mock 없음)

### 수정된 실제 함수로 재확인

```
$ python3 -c "... backend_agent_code_review(buggy_code) ..."  # 수정 후
**Unverified import:** `from .note import Note` is a relative import
into a sibling module I cannot see. ...
```

### 정상 경로 회귀 확인 — 상대 import가 없는 코드

```python
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
```

리뷰: "This file contains no relative imports ..., so there's nothing
to flag on that front for this particular snippet." — 불필요한
boilerplate 없이 정상적으로 코드 자체를 리뷰했다.

### End-to-End 재확인 — notekeeper가 실제로 썼던 것과 동일한 호출 경로

```
$ python3 -c "... workflow_0002.run_mvp_0002(buggy_code) ..."
**Unverified import (per instructions):** `from .note import Note`
cannot be confirmed against this file alone ...
```

`projects/notekeeper/runner.py`가 실제로 호출했던 것과 정확히 같은
함수(`workflow_0002.run_mvp_0002`)로 재확인 — `notekeeper` 프로젝트
자체는 전혀 건드리지 않았다.

### 기존 테스트 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
...                                                                      [100%]
3 passed in 81.32s (0:01:21)
```

real Engine 호출 포함 3건 모두 통과(mock 없음).

## 6. `test_execution` Capability도 실제 실행을 하지 않는다는 사실 확인

`qa_agent_test_execution()`도 `code_review`와 마찬가지로
`call_engine()` 1회 호출(텍스트 생성)일 뿐, 어떤 코드도 실제로
실행하지 않는다 — `DISALLOWED_TOOLS`가 Bash를 포함해 모든 도구를
막으므로 이는 우연이 아니라 Contract상 보장된 사실이다. 즉 "실제
실행 검증"은 어떤 Development HQ Capability의 책임도 아니며, 항상
호출하는 쪽(프로젝트의 `runner.py`/사람이 실제로 pytest를 돌리는
것, `MVP-0045`/`MVP-0046`이 실제로 한 것)의 책임이다 — 이번 지시의
"실제 실행 검증이 필요한 경우 기존 Test/Execution 경로를 활용한다"는
조건은 이미 `MVP-0045`/`MVP-0046`에서 실제로 활용되고 있었고, 이번
세션은 그 사실을 명시적으로 재확인했을 뿐 새로 만들지 않았다.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — 건드리지 않음 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — 건드리지 않음 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 `code_review` 지시 문장만 확장 |
| Architecture/Contract 변경 필요 | 미발동 — 함수 시그니처·호출 방식·반환 계약 전부 유지 |
| Kernel Component/Runtime/Production caller/Prompt Cache 착수 | 미발동 — 전혀 건드리지 않았다 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `code_review`에 다른 프로젝트 파일을 함께 넘기는 새 입력
  Context — 하지 않았다(Contract 변경이 되므로). 실험에서도
  "정보 공백 자체를 채우는 것"이 아니라 "정보 공백이 있다는 사실을
  명시하게 하는 것"만 검증했다.
- `qa_agent_test_execution`이나 다른 Capability의 지시 문장 —
  건드리지 않았다. 이번 결함은 `code_review`에서만 재현·검증했다.
- 새 RFC/ADC/ADR — 만들지 않았다. Architecture 결정이 필요한 지점을
  만나지 않았다.
- `projects/notekeeper`, `projects/textkit`,
  `projects/development-hq-devkit` — 전혀 수정하지 않았다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`agents.py`)**. 실제로 재현하고
  실제로 검증한 지시 문장 한 줄만 추가했다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `backend_agent_code_review()`의 시그니처와 호출 방식을 그대로
  유지했다.
- 실제 Engine으로 확인했는가 — **예**. 결함 재현 1회, 프롬프트 보강
  실험(버그 코드 2회 반복 + 유효 코드 1회 + 상대 import 없는 코드
  1회) 4회, 수정된 실제 함수 재확인 2회, End-to-End 재확인 1회
  (`run_mvp_0002` 동일 경로), 기존 pytest 3건 재실행 — 전부 real
  `claude -p` 호출, mock 없음.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 재현 →
  프롬프트 실험 → 최소 수정 → 재검증을 이 세션 하나에서 연속으로
  처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
  만났다면 중단하고 보고했을 것이다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  오탐 여부를 실제로 테스트해 "틀렸다고 주장하지 않고 검증 불가만
  말한다"는 사실을 그대로 기록했다.
- 불필요한 변경을 확인했는가 — **예**. `engine.py`, `workflow*.py`,
  `project_intelligence.py`, `cli.py`, 세 Dogfooding 프로젝트
  어디에도 손대지 않았다(`git status --porcelain` 확인).
