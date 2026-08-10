# Fix Cycle: cli.py — 잘못된 속성명 + argparse 순서 결함(2라운드)

## 결함 1 — `note.created` (실제 재현, AttributeError)

`_cmd_show`가 `note.created`를 참조하지만, `Note`의 실제 필드명은
`created_at`이다(`models.py`가 Context로 넘겨졌음에도 다시 발생한
Context-following 실패 — `store.py`의 `from .note import Note` 사례와
같은 종류).

```
$ cli.main(['--store', PATH, 'show', note_id])
AttributeError: 'Note' object has no attribute 'created'. Did you mean: 'created_at'?
```

## 결함 2 — `--store PATH`가 서브커맨드 앞에 오면 인식되지 않음(실제 재현)

```
$ cli.main(['add', 'Hello', 'World', '--store', PATH])
notekeeper: error: unrecognized arguments: --store PATH
```
(자연스러운 어순 — `notekeeper add ... --store PATH` — 이 실패한다.
`--store PATH add ...` 순서만 동작했다.)

## Fix Round 1 — 두 결함을 실제 traceback과 함께 재수정 요청

`backend_agent_code_generation()`에 원본 코드 + 두 실제 실패를 함께
입력해 재호출. 결과: `note.created` → `note.created_at` 정정,
`--store`를 top-level parser와 각 subparser 모두에 `parents=[...]`로
공유(같은 `store_parent`, 같은 `default="notes.json"`)해 두 위치
모두에서 인식되도록 함.

## Round 1 Fix가 만든 새로운 실제 결함 — 반대 방향 순서가 조용히 깨짐

Round 1 fix를 실제로 실행해 검증하는 과정에서 발견:

```python
parser.parse_args(['add', 'Hello', 'World', '--store', PATH]).store
# -> PATH (정상)
parser.parse_args(['--store', PATH, 'add', 'Hello', 'World']).store
# -> "notes.json" (기본값으로 조용히 되돌아감 — PATH가 무시됨!)
```

원인: subparser에 `parents=[store_parent]`로 **같은 default 값을 가진
`--store`를 복제**하면, argparse가 subparser 단계에서 그 default를
다시 적용해 top-level에서 이미 파싱된 값을 덮어쓴다(`--store`가
subcommand 뒤에 명시적으로 다시 주어지지 않는 한). 이는 real Review가
찾은 것이 아니라 **Fix를 real pytest/직접 실행으로 재검증하는 과정에서
직접 재현한** 결함이다 — Round 1 결함(순서 하나가 안 됨)을 고치려다
정반대 방향(다른 순서가 조용히 무시됨)을 만든 사례.

### Fix Round 2 — 직접 수정(SUPPRESS 패턴)

이 결함은 잘 알려진 argparse 관용구(subparser 쪽 복제본의 default를
`argparse.SUPPRESS`로 설정해, 명시적으로 다시 주어지지 않는 한
이미 파싱된 상위 값을 덮어쓰지 않게 함)로 해결된다. Engine을 다시
호출하지 않고 직접 수정했다(정답 패턴이 명확했고, 실제 실행으로
즉시 재검증 가능했기 때문 — `store.py`의 부모 디렉토리 결함과 같은
판단 기준).

### 최종 검증(실제 실행, 세 가지 어순 모두)

```python
parser.parse_args(['add', 'x', 'y']).store            # -> "notes.json" (기본값)
parser.parse_args(['--store', 'a.json', 'list']).store  # -> "a.json"
parser.parse_args(['list', '--store', 'b.json']).store  # -> "b.json"
```

세 경우 모두 정확히 기대한 값을 반환한다. 네 번째 real Review는 이
결함들을 더 이상 지적하지 않았다 — 대신 "SUPPRESS 트릭이 argparse의
문서화된 안정 계약이 아니라 내부 구현에 의존한다"는 스타일 지적을
새로 했는데, 이는 실제로 재현된 실패가 아니라 이론적 우려이므로
반영하지 않았다(README의 "이론적 문제는 만들지 않는다" 원칙).

## 회귀 확인

`python3 -m pytest projects/notekeeper/tests -v` — **40건 모두 통과**,
그중 `test_store_option_works_before_subcommand`/
`test_store_option_works_after_subcommand`/
`test_show_prints_created_at_without_crashing`가 이번 Fix Cycle의
회귀 테스트다.
