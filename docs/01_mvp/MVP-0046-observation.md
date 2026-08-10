# MVP-0046 Observation

**문서 성격**: 실제 실행 기록(Evidence). `MVP-0045`(`projects/textkit`,
상태 없는 순수 함수 3개)보다 실제로 더 복잡한 과제 —
**데이터 모델 + 파일 기반 영속 저장소 + 검색 + CLI**로 이어지는 4개의
실제로 연결된 Issue — 를 Development HQ의 기존 Capability만으로
요구사항 분석부터 최종 검증까지 처음부터 끝까지 실행했다.
`development-hq/mvp/`는 한 줄도 수정하지 않았다.

## 목적

`textkit`은 세 함수 모두 상태가 없고, 서로 거의 독립적이었다(cli.py만
둘에 의존). 이번에는 실제 개발에서 훨씬 흔한 패턴 — 모델 → 그
모델에 의존하는 영속 저장소 → 그 저장소에 의존하는 검색 → 셋 모두에
의존하는 CLI — 로 이어지는 진짜 의존 사슬을 만들어, Context가
사슬을 따라 여러 단계 전달될 때, 그리고 파일 I/O·"찾음/못 찾음"류
조건이 실제로 있을 때 무엇이 관찰되는지 확인했다.

## 선정한 실제 프로젝트

`projects/notekeeper/` — 로컬 파일 기반 메모 관리 라이브러리+CLI.
`projects/textkit`·`projects/development-hq-devkit`과 같은 성격(검증
목적, Production caller 후보 아님, `core/execution_layer` 미참조 —
`grep -rn "execution_layer" projects/notekeeper` 확인됨)의 세 번째
Dogfooding 프로젝트로 별도 생성했다. 기존 두 프로젝트는 수정하지
않았다.

Issue 4개, 각각 앞선 Issue의 실제 코드를 `[Existing Code]` Context로
전달받으며 순서대로 실행:

1. `models.py` — `Note` dataclass, `Note.new()`/`to_dict()`/`from_dict()`
2. `store.py` — `NoteStore`(JSON 파일 영속 저장소): add/get/delete/list/save/load
3. `search.py` — `search_notes()`(제목/본문 부분 일치 + 태그 AND 결합)
4. `cli.py` — 위 세 모듈을 실제로 import해서 쓰는 argparse CLI

## 1. 실제로 발견된 결함 4건 — 전부 real Engine + 실제 실행으로 확인

### 결함 1 (Issue 1, `models.py`) — dataclass 필드 순서, **모듈이 아예 import되지 않음**

`tags: list = field(default_factory=list)`가 `created_at: str`보다
앞에 있어 "기본값 없는 필드가 기본값 있는 필드 뒤에 온다"는
dataclass 규칙을 어겼다. 첫 real Review가 지적했고, 직접 import해
재현했다: `TypeError: non-default argument 'created_at' follows
default argument`. `backend_agent_code_generation()`(기존
Capability)에 실제 traceback을 넣어 재호출 — 필드 순서 정정으로
해소. 상세: `issues/0001-models/fix-cycle.md`.

### 결함 2 (Issue 2, `store.py`) — **Context로 넘긴 실제 파일명을 따르지 않음**

`models.py`(정확한 경로 포함)가 Context로 전달됐음에도, 생성된
코드는 `from .note import Note`(단수형, 존재하지 않는 파일)를
import했다. **첫 real `code_review`는 이 결함을 지적하지
못했다** — Validation Capability는 텍스트만 검토하고 실제로 import를
실행하지 않으므로, 존재하지 않는 모듈을 가리키는 import 한 줄은
텍스트만으로는 완전히 정상으로 보인다. `import notekeeper.store`를
실제로 실행해서만 드러났다(`ModuleNotFoundError: No module named
'notekeeper.note'`). 이는 이번 프로젝트 전체에서 가장 중요한
관찰이다 — **텍스트 기반 Review Capability가 놓치는 결함의 종류를
실제로 확인**했다. Fix: 실제 traceback을 다시 `code_generation`에
입력해 `from .models import Note`로 정정.

두 번째 real Review는 별도로 "save()가 부모 디렉토리를 만들지
않는다"는 결함을 지적했고, 직접 재현(`FileNotFoundError`)한 뒤
`self.path.parent.mkdir(parents=True, exist_ok=True)` 한 줄로 직접
수정했다(자명한 한 줄 수정이라 Engine을 다시 부르지 않았다 — 그
판단 기준 자체를 Evidence로 남김). 상세: `issues/0002-store/fix-cycle.md`.

### 결함 3·4 (Issue 4, `cli.py`) — 잘못된 속성명 + argparse 순서, **2라운드 Fix Cycle**

첫 real Review·직접 실행이 두 실제 결함을 확인: (1) `_cmd_show`가
`note.created`를 참조(`AttributeError`, 실제 필드명은 `created_at` —
결함 2와 같은 종류의 Context-following 실패), (2)
`notekeeper add ... --store PATH`(자연스러운 어순)가
`unrecognized arguments`로 실패(`--store PATH add ...` 순서만 동작).

두 실제 실패를 함께 `code_generation`에 입력해 재호출한 결과 (1)은
해소됐지만, **재수정된 코드를 실제로 재검증하는 과정에서 새로운
실제 결함을 발견**했다: 이번엔 정반대 방향의 어순
(`--store PATH add ...`)이 조용히 기본값("notes.json")으로
되돌아가 사용자가 지정한 경로가 무시됐다 — subparser에 같은
`--store`(같은 default)를 복제하면 argparse가 subparser 단계에서
그 default를 다시 적용해 이미 파싱된 top-level 값을 덮어쓰기
때문이다. 이는 real Review가 찾은 게 아니라 **Fix를 실제 실행으로
재검증하는 과정에서 직접 재현**했다. 잘 알려진 argparse 관용구
(subparser 쪽 복제본만 `default=argparse.SUPPRESS`)로 직접
수정했다(패턴이 명확하고 즉시 실행 검증 가능했으므로 Engine을 다시
부르지 않았다). 세 어순(`add x y`/`--store a add`/`add --store b`)
전부 실제 실행으로 재확인했다. 상세: `issues/0004-cli/fix-cycle.md`.

## 2. Context 전달 — 4단계 사슬에서 관찰

3개 Issue(2·3·4)가 각각 선행 Issue의 실제 코드를 `[Existing Code]`
블록으로 전달받았다. 결과는 섞여 있었다: Issue 3(`search.py`)은
`from notekeeper.store import NoteStore`를 정확한 패키지 경로로
올바르게 생성했지만, Issue 2·4는 각각 파일명(`note` vs `models`)과
속성명(`created` vs `created_at`)에서 Context를 실제로 따르지 않는
결함을 만들었다. **Context가 프롬프트에 포함된다고 해서 항상
정확히 반영되는 것은 아니라는 사실을 4단계 사슬에서 2회(결함
2·3) 실제로 관찰**했다 — `OBS-0003`(Context 전달 메커니즘)이
관찰해 온 것과 같은 주제의 새로운 실제 사례다.

## 3. 조건 분기 — 실제 관찰

각 Issue의 Validation은 `workflow_0002.run_mvp_0002()`를 그대로
재사용했다. 4개 Issue 모두 real Review가 실제 개선점을 찾아
`NO_ISSUES_MARKER` 분기가 "생략" 쪽으로 가지 않았다 — 강제로 만든
분기가 아니라 실제 코드 품질에 따른 자연스러운 결과다. `store.py`의
실제 코드(`get()`이 `None` 반환, `delete()`가 `bool` 반환,
`load()`가 손상된 JSON에 `NoteStoreError`를 던지는 것)와 `cli.py`의
"찾음/못 찾음" 분기(`show`/`delete`가 없는 id에 stderr 메시지 +
exit code 1)는 이번 프로젝트가 자연스럽게 요구한 실제 조건 분기다.

## 4. 실제 검증 (mock 없음)

```
$ python3 -m pytest projects/notekeeper/tests -v
...
============================== 40 passed in 0.12s ==============================
```

`test_models.py`(10건), `test_store.py`(11건, 부모 디렉토리 결함
포함), `test_search.py`(9건), `test_cli.py`(10건, 두 argparse
어순·`created_at` 회귀 테스트 포함) 전부 최종 코드에 대해 실행해
통과했다. CLI도 실제로 실행해 확인:

```
$ python3 -m notekeeper.cli add "Groceries" "Milk, eggs, bread" --tags food,errand --store /tmp/nk_smoke.json
764145da-...
$ python3 -m notekeeper.cli search milk --store /tmp/nk_smoke.json
764145da-...    Groceries
```

### 회귀 확인

```
$ python3 -m pytest projects/textkit/tests -q      # 32 passed
$ python3 -m pytest development-hq/mvp/tests -q    # 3 passed (61.3s, real Engine)
```

`development-hq/`, `projects/textkit/`, `projects/development-hq-devkit/`
어디에도 변경 없음(`git status --porcelain`에 `projects/notekeeper/`와
이 문서만 신규).

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — `runner.py`는 하드코딩된 순차 호출만 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 4개 함수만 재사용 |
| Kernel Component/Runtime/Production caller/Prompt Cache 착수 | 미발동 — `core/execution_layer` 미참조 확인됨, 기존 검증용 프로젝트와 동일한 성격 유지 |
| 새 Architecture/Concept/Component 필요 | 미발동 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- 동시성/파일 잠금 — README가 명시적으로 Out of Scope로 둔 항목이며
  실제로 재현되지 않았다.
- `--store` SUPPRESS 트릭이 argparse 내부 구현에 의존한다는 네 번째
  Review의 지적 — 실제로 재현된 실패가 아니라 이론적 우려라 반영하지
  않았다.
- `projects/textkit`, `projects/development-hq-devkit` 수정 — 하지
  않았다.
- 새 RFC/ADC/ADR — 만들지 않았다.
- `development-hq/mvp/` 수정 — 전혀 하지 않았다.

## Self Review

- 코드를 변경했는가 — **예**, 새 프로젝트 디렉토리
  (`projects/notekeeper/`) 하나를 추가했다. `development-hq/mvp/`는
  변경하지 않았다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. 기존 두 Dogfooding 프로젝트와 같은 패턴을 재사용했다.
- 실제 Engine으로 확인했는가 — **예**. 4개 Issue × (Planning/Design/
  Implementation/Review, 조건부 Test) + Fix Cycle 3라운드(real
  Engine 재호출 2회, 직접 수정 2회 — 각각 실제 실행으로 근거를
  확인한 뒤에만 직접 수정했다) — 전부 real `claude -p` 호출, mock
  없음. 실제 pytest 40건, 실제 CLI 실행, textkit·development-hq 기존
  테스트도 재실행.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 4개
  Issue의 전체 SDLC와 3라운드 Fix Cycle을 이 세션 하나에서 연속으로
  처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  Engine 재호출 없이 직접 고친 두 지점(부모 디렉토리 생성, argparse
  SUPPRESS)도 "왜 Engine을 다시 부르지 않았는지" 판단 근거를 그대로
  기록했다.
- 불필요한 변경을 확인했는가 — **예**. `development-hq/`,
  `projects/textkit/`, `projects/development-hq-devkit/` 어디에도
  손대지 않았다(`git status --porcelain` 확인).
