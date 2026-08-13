# Design: Add edit subcommand to notekeeper CLI

## 설계: `edit` 서브커맨드 추가

### 접근 방식

기존 서브커맨드(`show`, `delete`)가 따르는 3단 구조를 그대로 복제한다: (1) `build_parser()`에 서브파서 등록, (2) `_cmd_edit(args, store)` 핸들러 함수, (3) `store.update()` 위임. 새 코드는 이 세 지점에만 삽입되고, 그 외 어떤 기존 블록도 건드리지 않는다.

**파서 등록**: `edit_parser = subparsers.add_parser("edit", parents=[sub_store_parent], ...)` 형태로, `delete_parser`나 `show_parser` 정의 바로 옆(예: `show_parser` 다음, `search_parser` 이전)에 위치시켜 diff를 최소화한다. 인자는 `note_id`(positional, `show`/`delete`와 동일), `--title`(default=None), `--body`(default=None), `--tags`(default=None) 네 개. `set_defaults(func=_cmd_edit)`로 마무리하는 것도 기존 패턴 그대로다. `parents`에 `sub_store_parent`(서브커맨드 뒤 `--store` 허용)를 반드시 포함시켜야 하며, 이는 다른 서브파서와 한 글자도 다르지 않게 순서·인자를 맞추는 것이 핵심 리스크 완화책이다.

**핸들러 로직**: `_cmd_edit`는 세 줄 내외의 얇은 래퍼로 구성한다.
1. 태그 분기: `tags = None if args.tags is None else _parse_tags(args.tags)`. 이 한 줄이 이 기능 전체에서 유일하게 "새로운 판단"이 들어가는 지점이다 — `_parse_tags`를 무조건 호출하면 미지정 시에도 빈 리스트가 되어 "태그 미변경" 시맨틱이 깨지므로, `args.tags is None` 체크를 `_parse_tags` 호출보다 먼저 수행해야 한다.
2. `note = store.update(args.note_id, title=args.title, body=args.body, tags=tags)` 호출. `--title`/`--body` 미지정 시 argparse 기본값 `None`이 그대로 전달되며, "미지정=None, 필드 유지"라는 해석은 `NoteStore.update()`가 이미 구현한 계약이므로 CLI는 그 계약을 신뢰하고 그대로 값을 통과시키기만 하면 된다(별도의 `if args.title is not None:` 같은 재해석 로직 불필요 — update 시그니처가 이미 그렇게 설계되어 있다는 전제).
3. `None` 반환 시 `show`/`delete`와 동일한 문구·스트림·종료코드로 "Note not found: {id}"를 stderr에 출력하고 실패를 알린다. 성공 시에는 `add`와 동일하게 `note.id`만 stdout에 출력한다.

예외 처리는 별도로 하지 않는다. `NoteStoreError` 등은 `main()`의 기존 try/except가 이미 모든 `_cmd_*` 호출을 감싸고 있으므로, `_cmd_edit`도 그 우산 안에 자연스럽게 들어간다.

### 책임 분리

- **CLI 계층(`_cmd_edit`)**: 인자 해석, `None` vs 빈 문자열/빈 리스트 구분, not-found 시 사용자 메시지 포맷, 종료 코드 결정, 성공 출력 포맷. 이 함수는 "번역기"일 뿐 판단 로직을 갖지 않는다.
- **`NoteStore.update()`**: 실제 필드 병합 규칙(부분 업데이트 시맨틱), 존재 여부 확인, 영속화. 여기는 손대지 않고 시그니처만 신뢰한다.
- **`build_parser()`/`main()`**: 구조는 그대로 유지, `edit` 서브파서 한 블록만 추가되는 "삽입 지점" 역할.

### 리스크

1. **태그 분기 누락**이 가장 유력한 버그 지점 — 리뷰 시 이 한 줄을 최우선으로 검증해야 한다.
2. **parents 순서/누락**으로 인한 `--store` 위치 회귀 — 반드시 인접한 기존 서브파서 정의를 복사-수정하는 방식으로 작성해 구조적 diff를 0에 가깝게 만든다.
3. **not-found 메시지·종료코드 불일치** — 하드코딩하지 말고 `delete`/`show`가 실제로 쓰는 문자열 포맷·exit code 값을 그대로 재사용(상수/함수가 있다면 그것을 호출)해야 문구가 어긋나지 않는다.
4. **update() 시그니처 오해** — `title`/`body`/`tags` 세 키워드 인자의 이름과 "None=미변경" 계약이 실제 구현과 일치하는지 사전 확인이 필요하며, 이 부분은 코드를 보지 않고는 확정할 수 없으므로 구현 단계에서 반드시 `NoteStore.update()` 정의를 먼저 읽고 시작해야 한다.
5. **테스트 매트릭스**: 존재하는 id / 존재하지 않는 id, `--tags` 생략(보존) / 빈 문자열(초기화) / 값 지정(교체), `--title`만 단독 지정, `--store`가 `edit` 앞·뒤 각각 위치하는 경우 — 총 조합을 기존 서브커맨드 테스트 스타일 그대로 추가한다.

