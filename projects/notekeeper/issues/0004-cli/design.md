# Design: Add a CLI to notekeeper

# notekeeper CLI 설계

## 접근 방식

`cli.py`는 로직을 갖지 않는 얇은 어댑터로 설계한다. `argparse.ArgumentParser` + `add_subparsers(dest="command", required=True)` 구조로 5개 서브커맨드를 등록하고, 각 서브커맨드는 `set_defaults(func=...)`로 개별 핸들러 함수(`_cmd_add`, `_cmd_list`, `_cmd_show`, `_cmd_search`, `_cmd_delete`)에 매핑한다. `main(argv=None)`은 다음 역할만 수행한다:

1. 파서 생성 및 `parse_args(argv)`
2. `NoteStore(args.store)` 생성
3. `args.func(args, store)` 호출, 반환값(int)을 그대로 리턴

핸들러 함수는 각각 "인자 해석 → 라이브러리 호출 1회 → 결과를 stdout/stderr에 출력 → 종료 코드 반환"의 4단계만 수행하고, 그 이상의 판단(필터링, 정렬, 검증)은 하지 않는다. 이렇게 하면 `search`가 `search_notes()`를 재구현할 여지 자체를 구조적으로 차단할 수 있다.

## 컴포넌트별 책임

- **`build_parser() -> argparse.ArgumentParser`**: 파서 구성만 전담하는 별도 함수로 분리한다. `main()`에서 분리해두면 `--help` 출력이나 인자 파싱만 검증하는 테스트가 `NoteStore` 생성 없이 가능해진다.
- **전역 `--store`**: 최상위 파서에 정의하고 하위 파서 각각이 아닌 **부모 파서(`parents=[]`)를 통해 공유**하거나, 단순히 최상위 파서에 한 번만 정의해 `parse_args` 이후 모든 서브커맨드 핸들러가 동일한 `args.store` 값을 참조하게 한다. 서브커맨드마다 반복 정의하지 않는다.
- **각 핸들러**:
  - `_cmd_add`: `--tags` 원문 문자열을 파싱하는 헬퍼(`_parse_tags`)를 거쳐 `Note.new(title, body, tags)` 생성, `store.add(note)`, `print(note.id)`, `return 0`.
  - `_cmd_list`: `store.list()` 순회, 공통 포맷 헬퍼(`_format_note_line`)로 출력, `return 0`.
  - `_cmd_show`: `store.get(note_id)`가 `None`이면 stderr 메시지 후 `return 1`; 존재하면 상세 필드 출력 후 `return 0`.
  - `_cmd_search`: `search_notes(store, args.query, args.tag)` 결과를 `_format_note_line`으로 순회 출력만 하고 `return 0`. 필터링 조건문 자체를 이 함수 안에 두지 않는다.
  - `_cmd_delete`: `store.delete(note_id)`의 bool 반환값으로 분기, 실패 시 stderr + `return 1`.
- **공용 포맷 헬퍼 `_format_note_line(note) -> str`**: `list`와 `search`가 동일 함수를 호출하도록 강제해 "포맷 일관성" 요구를 코드 구조로 보장한다.

## 모호했던 지점에 대한 구체적 결정

- **태그 파싱**: `--tags` 값을 `,`로 split 후 각 항목 `.strip()`, 빈 문자열 제거, **순서를 유지한 채 중복 제거**(먼저 나온 것 우선). 미지정 시 `[]`. 이 규칙을 `_parse_tags` 단일 함수에 캡슐화해 정책 변경 시 한 곳만 고치면 되게 한다.
- **종료 코드**: 애플리케이션 레벨 실패(존재하지 않는 id 등)는 `1`로 통일한다. argparse 자체의 사용법 오류(필수 인자 누락 등)는 argparse 기본 동작(`SystemExit(2)`)에 맡기고 별도로 가로채지 않는다 — 이 둘을 구분해 코드값 자체에 의미를 부여한다(1=애플리케이션 오류, 2=CLI 사용법 오류).
- **`NoteStoreError`(파일 손상 등) 처리**: `main()` 최상위에서 `try/except NoteStoreError as e` 한 곳으로 잡아 stderr 출력 + `return 1`. 개별 핸들러 안에서 잡지 않는다 — store 생성 시점과 `save()` 시점 양쪽에서 터질 수 있으므로 가장 바깥에서 한 번에 처리하는 게 중복을 없앤다. traceback은 노출하지 않는다(요구사항의 "깔끔한 에러 메시지" 원칙을 개별 id 실패뿐 아니라 store 레벨 실패에도 동일하게 적용).
- **출력 포맷**: `list`/`search` 라인은 `f"{note.id}\t{note.title}"` 형태(탭 구분, 라벨 없음)로 통일해 스크립팅 시 `cut`/`awk` 등으로 파싱하기 쉽게 한다. `show`는 라벨을 붙인 여러 줄(`Title: ...`, `Body: ...`, `Tags: ...`, `Created: ...`) — 사람이 읽는 상세 뷰이므로 `list`와 다른 포맷이어도 요구사항 위반이 아니다(요구사항은 "list와 search 간" 일관성만 요구).
- **`list`/`search` 정렬**: 요구사항에 명시 없으므로 `store.list()`/`search_notes()`가 반환하는 순서를 그대로 사용하고 CLI에서 재정렬하지 않는다(재구현 금지 원칙의 연장).

## 리스크와 대응

- **로직 중복**: 위 구조(핸들러는 호출 1회 + 출력만)로 구조적으로 방지하지만, 코드 리뷰 시 `_cmd_search` 안에 `if`/`for`로 필터 조건이 들어가지 않았는지 명시적으로 확인해야 한다.
- **예외 노출**: `show`/`delete`는 `None`/`False` 반환값 분기만으로 처리되므로 애초에 예외가 발생하지 않는 경로다. 문제는 `NoteStore(args.store)` 생성 시점과 `store.add/list/search` 내부에서 발생 가능한 `NoteStoreError`인데, 이를 `main()` 최상위 `try/except`로 감싸는 것이 유일하게 빠지기 쉬운 지점이므로 테스트에서 손상된 JSON 파일을 `--store`로 지정하는 케이스를 반드시 검증한다.
- **테스트 용이성**: `main(argv=None)`이 리스트를 받아 int를 반환하는 순수 함수 형태이므로, `capsys`로 stdout/stderr을 캡처하고 반환값을 assert하는 방식으로 서브프로세스 없이 전체 커맨드를 테스트 가능 — 이 계약이 깨지지 않도록 `main()` 내부에서 `sys.exit()`를 직접 호출하지 않는다(그건 `if __name__ == "__main__"` 블록의 책임).
- **`--tags`의 빈 문자열/공백 케이스**: `--tags ""` 또는 `--tags " , "` 같은 입력이 빈 태그 리스트로 정규화되는지 별도 단위 테스트로 `_parse_tags`를 직접 검증해 CLI 레벨 통합 테스트에 숨지 않게 한다.

이 설계는 요구사항 문서가 이미 지적한 두 핵심 제약(검색 로직 재구현 금지, 실패 경로의 traceback 없는 처리)을 함수 분리와 최상위 예외 처리 지점 하나로 구조적으로 강제하는 데 초점을 맞췄다.

