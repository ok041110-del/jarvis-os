# Planning: Add edit subcommand to notekeeper CLI

## 요구사항 분석: `edit` 서브커맨드 추가

### 목표 (Goal)
notekeeper CLI에 기존 메모를 수정할 수 있는 `edit` 서브커맨드를 추가한다. 이미 `NoteStore`에 구현된 `update()` 메서드를 CLI 계층에서 노출시키는 것이 핵심이며, 새로운 비즈니스 로직을 만드는 것이 아니라 기존 로직을 얇게 감싸는 래퍼를 추가하는 작업이다.

### 범위 (Scope)

**포함:**
- `edit NOTE_ID [--title T] [--body B] [--tags t1,t2]` 형태의 신규 서브커맨드
- `_cmd_edit(args, store)` 함수 신설: `_parse_tags()`로 `--tags`를 파싱하고, `--tags` 미지정 시 `tags=None`을 그대로 `store.update()`에 전달해 태그 미변경 시맨틱 유지
- `store.update()`가 `None`을 반환하면(존재하지 않는 id) `show`/`delete`와 동일한 패턴으로 `"Note not found: {id}"`를 stderr에 출력하고 0이 아닌 종료 코드 반환
- 성공 시 갱신된 Note의 id를 stdout에 출력 (add와 동일한 출력 스타일)
- `build_parser()`에 `sub_store_parent`를 parents로 사용하는 `edit_parser` 추가 — 다른 서브커맨드와 동일하게 `--store`가 서브커맨드 앞/뒤 어느 위치에서도 동작해야 함

**제외 (명시적으로 손대면 안 되는 부분):**
- 기존 서브커맨드(add/list/show/search/delete)의 코드, 동작, 출력 형식은 단 한 글자도 변경 금지
- `build_parser()`/`main()`의 기존 구조(예: `store_parent`/`sub_store_parent` 분리 설계, `argparse.SUPPRESS` 트릭, 예외 처리 흐름) 변경 금지 — 오직 `edit` 서브파서 블록을 새로 추가하는 것만 허용
- `NoteStore.update()` 자체의 재구현/수정 — CLI는 이를 그대로 호출만 함

### 리스크 및 유의점 (Risks)

1. **`--tags` 미지정과 빈 문자열 지정의 구분**: `_parse_tags(None)`은 `[]`를 반환하므로, "태그를 변경하지 않음(`tags=None` 전달)"과 "태그를 빈 목록으로 지움(`--tags ""` 등)"을 CLI 레이어에서 명확히 구분해야 한다. 즉 `args.tags is None`일 때만 `update()`에 `tags=None`을 넘기고, 그 외에는 `_parse_tags(args.tags)` 결과를 넘기는 조건 분기가 필요하다 — 이를 놓치면 `--tags` 파싱 결과를 무조건 넘겨버려 "태그 미변경" 시맨틱이 깨진다.
2. **`--title`/`--body` 미지정 시 동작**: `update()`가 `None`(미지정)과 빈 문자열을 어떻게 구분하는지 `NoteStore.update()` 시그니처를 확인해야 하며, argparse 기본값을 `None`으로 두어 "지정 안 함"을 자연스럽게 표현해야 한다.
3. **에러 처리 일관성**: `NoteStoreError` 등 저장소 예외는 `main()`의 기존 try/except가 처리하므로 `_cmd_edit`에서 별도로 잡을 필요는 없으나, "not found" 케이스는 예외가 아니라 `update()`의 `None` 반환으로 구분된다는 기존 패턴(`delete`)을 그대로 따라야 한다.
4. **회귀 위험**: `sub_store_parent`를 parents로 잘못 누락하거나 순서를 바꾸면 `--store` 위치 무관 동작이 깨질 수 있다 — 이는 다른 서브커맨드 정의 순서를 그대로 복사해 최소 diff로 추가하는 것이 안전하다.
5. **테스트 범위**: id 없음/있음, `--tags` 생략 시 태그 보존, `--title`만 지정, `--store` 전/후 위치 등 기존 서브커맨드 테스트 패턴과 동일한 매트릭스로 검증이 필요하다.

