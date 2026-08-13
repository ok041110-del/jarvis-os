# MVP-0048 Observation

**문서 성격**: 실제 실행 기록(Evidence). `MVP-0047`(code_review의
"unverified import" 지시 보강)이 잘 일반화되는지 재확인하는 과정에서
더 심각한 실제 결함(파일을 확장하는 Issue에서 `code_generation`이
새로 추가되는 부분만 반환해 **기존 코드 전체가 파괴됨**)을 새로
재현·수정했다. `projects/notekeeper/runner.py` 1개 파일만 수정했고,
`development-hq/mvp/`는 전혀 건드리지 않았다.

## 목적

`MVP-0047`의 fix가 다른 실제 결함 유형(속성 접근, import 대상이
아닌)에도 일반화되는지 real Engine으로 재확인하려 했다. 이 확인
자체는 성공했지만, 그 과정에서 `notekeeper`에 다섯 번째 실제 Issue
(`NoteStore.update()` 추가 — 새 파일이 아니라 **기존 파일 확장**)를
실행하다가 훨씬 심각한 실제 결함을 발견해, 이번 세션의 주제가 그
결함의 재현·해결로 옮겨갔다.

## 1. MVP-0047 fix의 일반화 확인 — 성공

`notekeeper`의 실제 버그 CLI 코드(`note.created`, 존재하지 않는
속성)를 현재(수정된) `backend_agent_code_review()`에 다시 입력했다.
지시문은 "relative import"만 언급했음에도, 실제 Review는 import
검증 불가 이유를 설명하면서 그 import로 얻는 객체의 속성까지
자연스럽게 나열했다:

> "...instances exposing `.id`, `.title`, `.body`, `.tags`, **`.created`**
> (used in `_format_note_line` and `_cmd_show`)..."

`.created`(실제로는 잘못된 속성명)가 정확히 지목됐다 — 추가 프롬프트
수정 없이 일반화됨을 확인했다.

## 2. 새로 발견한 결함 — 기존 파일을 확장하는 Issue에서 `code_generation`이 파일 전체를 파괴함

실제로 다섯 번째 Issue(`NoteStore.update()` 추가, 기존 store.py의
`__init__`/`add`/`get`/`delete`/`list`/`save`/`load`는 "단 한 줄도
바꾸지 않는다"고 Issue에 명시)를 `run_issue()`로 실행한 결과:

```
$ cat src/notekeeper/store.py
def update(self, note_id, title=None, body=None, tags=None):
    note = self._notes.get(note_id)
    ...
```

**파일 전체가 이 메서드 하나로 대체됐다** — `class NoteStore`,
`NoteStoreError`, 나머지 6개 메서드, 모든 import가 사라졌다.

```
$ python3 -c "import notekeeper.store as s; print(hasattr(s, 'NoteStore'))"
False
```

### 원인 규명

`design_agent_design()`의 지시는 "describe a design in prose ... do
not write code yet"다 — 실제로 생성된 `design.md`(34줄)를 확인한
결과, 기존 `store.py`의 실제 소스는 한 줄도 포함돼 있지 않았고
"following the exact pattern add/delete already use"처럼 산문으로만
언급됐다. 즉 **`backend_agent_code_generation(design: str)`은애초에
기존 파일의 실제 바이트를 한 번도 받은 적이 없다** — Design
Capability의 계약(산문만 반환, 코드 작성 금지) 자체가 소스 코드를
무손실로 전달할 수 없게 만든다. Design 텍스트가 "메서드 하나만
추가"라고 설명하자, 실제 Engine은 "새로 추가되는 부분만 반환"으로
해석했다 — `code_generation`의 기존 지시("Return only the code")가
"새 파일을 만드는 경우"와 "기존 파일에 추가하는 경우"를 구분하지
않기 때문이다.

## 3. 해결 시도 순서 — 지시에 따라 단순 프롬프트 보강부터 확인

### 시도 1 (실패) — "복사본을 반환하라"는 지시만 추가

`code_generation`의 지시문에 "설계가 기존 코드에 추가하는 것을
설명하더라도 항상 완전한 파일을 반환하라"는 문장만 추가해 같은
`design.md`로 재호출 — 결과: 완전한 파일 형태는 갖췄지만(모든
메서드 이름 존재), **기존 메서드의 실제 구현을 처음부터
재발명(hallucinate)**했다(`add()`의 시그니처가 `add(title, body,
tags)`로 바뀌고, `Note` 필드 정의까지 다르게 재구성됨). 원인은
동일하다 — `code_generation`은애초에 보존해야 할 기존 코드의 실제
바이트를 받은 적이 없으므로, "완전한 파일을 반환하라"고만 지시해도
그 완전한 파일을 프롬프트만으로는 정확히 재구성할 수 없다. **단순
프롬프트 보강만으로는 해결되지 않음을 확인했다.**

### 시도 2 (성공) — 실제 대상 파일을 verbatim으로 함께 넘김

`code_generation()`의 입력(`design: str`)에 **실제 대상 파일의 현재
내용을 그대로(verbatim) 덧붙이고**, "이 내용을 한 글자도 바꾸지 말고
설명된 변경 사항만 추가해 전체 파일을 반환하라"고 지시했다. 결과:
기존 7개 메서드 전부가 **byte 단위로 원본과 동일하게** 보존됐고(직접
비교로 확인), 새 `update()`만 정확히 추가됐다.

## 4. 실제 코드베이스 구현 — 최소화, `development-hq/mvp/` 변경 없음

`backend_agent_code_generation()`(development-hq/mvp/agents.py)의
Contract(`design: str -> code: str`)는 전혀 바꾸지 않았다. 대신
**호출하는 쪽**(`projects/notekeeper/runner.py`)에
`_augment_design_with_target_source()` 헬퍼를 추가했다: 대상 모듈
파일이 이미 존재하면(= 새 파일이 아니라 기존 파일을 확장하는
Issue라면) 그 파일의 실제 내용을 verbatim으로 Design 텍스트 뒤에
덧붙여서 `code_generation()`에 넘긴다. 파일이 아직 없으면
(Issue 1~4처럼 새 파일을 만드는 경우) 이 함수는 아무것도 하지 않고
기존 동작을 그대로 유지한다 — `_enrich_with_existing_code()`가 이미
쓰는 것과 같은 기법(실제 파일 내용을 프롬프트 문자열에 그대로
포함)을 Design → Implementation 경계에도 적용했을 뿐이다.

## 5. 재검증 (실제 실행, mock 없음)

### Issue 5a — `NoteStore.update()`를 수정된 `run_issue()`로 정식 재실행

```
$ python3 -c "... run_issue('0005a-store-update', ...) ..."
```

생성된 `store.py`: 8개 메서드(`__init__`, `add`, `get`, `delete`,
`list`, `save`, `load`, `update`) 전부 존재, 기존 메서드는 그대로,
`update()`만 새로 추가됨을 실제로 확인.

### Issue 5b — CLI `edit` 서브커맨드도 같은 패턴으로 정식 실행

기존 서브커맨드(`add`/`list`/`show`/`search`/`delete`) 전부 보존,
`MVP-0046`이 고친 `--store` `SUPPRESS` 패턴도 그대로 유지된 채 새
`edit` 서브커맨드가 정확히 `store.update()`를 재사용하도록 생성됨을
확인.

### 실제 실행 검증

```
$ python3 -m notekeeper.cli add "Original" "Original body" --tags a,b --store /tmp/nk_edit_smoke.json
$ python3 -m notekeeper.cli edit <id> --title "Edited Title" --store /tmp/nk_edit_smoke.json
$ python3 -m notekeeper.cli show <id> --store /tmp/nk_edit_smoke.json
Title: Edited Title
Body: Original body
Tags: a, b
$ python3 -m notekeeper.cli edit does-not-exist --title x --store ...
Note not found: does-not-exist  # exit 1
```

### 기존 테스트 회귀 확인 + 신규 테스트

```
$ python3 -m pytest projects/notekeeper/tests -v
...
============================== 52 passed in 0.17s ==============================
```

기존 40건 + `update()`/`edit` 신규 12건(누락 id, 부분 갱신 3종, 무갱신,
id/created_at 불변성, 디스크 반영, CLI 성공/실패/태그 유지/태그 교체/
`--store` 순서 2종) 모두 통과.

```
$ python3 -m pytest projects/textkit/tests -q      # 32 passed
$ python3 -m pytest development-hq/mvp/tests -q    # 3 passed (real Engine)
```

`development-hq/`, `projects/textkit/`,
`projects/development-hq-devkit/` 무변경(`git status --porcelain`).

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 `code_generation` 호출 인자를 caller가 더 풍부하게 구성했을 뿐 |
| Architecture/Contract 변경 필요 | 미발동 — `development-hq/mvp/`는 한 줄도 바꾸지 않았다 |
| Kernel Component/Runtime/Production caller/Prompt Cache 착수 | 미발동 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `development-hq/mvp/agents.py`의 `backend_agent_code_generation()`
  자체를 수정 — 하지 않았다. 시도 1(프롬프트만 보강)이 실패했으므로,
  Development HQ Capability 수준에서 이 문제를 해결할 수 없다는
  것이 실제로 확인된 결론이다. 호출자(`runner.py`) 수준에서만
  해결했다.
- `projects/textkit/runner.py`에 같은 패턴 적용 — 하지 않았다(이번
  세션에서 textkit에 기존 파일을 확장하는 Issue가 실제로 발생하지
  않았다 — 재현되지 않은 것을 미리 고치지 않는다).
- 새 RFC/ADC/ADR — 만들지 않았다.

## Self Review

- 코드를 변경했는가 — **예**. `projects/notekeeper/runner.py` 1개
  파일(헬퍼 함수 추가)과 `tests/`에 신규 테스트만 추가했다.
  `development-hq/mvp/`는 전혀 수정하지 않았다.
- Architecture를 설계했는가 — **아니오**. `code_generation()`의
  시그니처/Contract를 그대로 유지했다. 호출자가 입력 문자열을 더
  풍부하게 구성했을 뿐이다.
- 실제 Engine으로 확인했는가 — **예**. 결함 재현 1회, 실패한 시도
  1회(프롬프트만 보강), 성공한 시도 1회(verbatim 소스 포함), 정식
  Issue 5a·5b 재실행 각 1회(Planning/Design/Implementation/Validation
  전부 real Engine) — 전부 mock 없음. 실제 CLI 실행, 실제 pytest
  52건 + textkit 32건 + development-hq 3건 재확인.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 발견 →
  원인 규명 → 실패한 시도 → 성공한 시도 → 정식 재실행 → 회귀 검증을
  이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
  Development HQ 수준 수정이 필요했다면(시도 1이 성공했다면 몰라도)
  중단하고 보고했을 것이나, 캐릭터 수준 fix로 충분함을 실제로
  확인했다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  시도 1이 실패했다는 사실(프롬프트만으로는 부족했다)을 숨기지 않고
  그대로 기록했다.
- 불필요한 변경을 확인했는가 — **예**. `development-hq/`,
  `projects/textkit/`, `projects/development-hq-devkit/` 어디에도
  손대지 않았다(`git status --porcelain` 확인).
