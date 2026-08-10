# Planning: Add a CLI to notekeeper

## 요구사항 분석: notekeeper CLI 추가

### 목표 (Goal)
기존 `notekeeper` 패키지(`models.Note`, `store.NoteStore`, `search.search_notes`)에 대한 커맨드라인 인터페이스(`src/notekeeper/cli.py`)를 신규로 제공한다. 목적은 라이브러리 계층의 기능(노트 생성/조회/검색/삭제)을 별도 프로세스에서 스크립팅 가능한 형태로 노출하는 것이며, 비즈니스 로직 재구현이 아니라 기존 계층(`NoteStore`, `search_notes`)에 대한 얇은 프레젠테이션 레이어를 만드는 것이다.

### 범위 (Scope)
- **구현 대상**: `cli.py` 단일 파일, `argparse`(표준 라이브러리)만 사용, 외부 의존성 없음.
- **전역 옵션**: `--store PATH` (기본값 `"notes.json"`) — 모든 서브커맨드 공통. 이 옵션으로 `NoteStore` 인스턴스를 생성해 각 서브커맨드 핸들러에 전달해야 한다.
- **서브커맨드 5종**과 각각의 정확한 동작:
  1. `add TITLE BODY [--tags t1,t2,t3]` — `Note.new()`로 생성, `store.add()`로 영속화, 생성된 `note.id`를 stdout에 출력. `--tags` 미지정 시 빈 리스트. 쉼표 분리 파싱 로직이 필요(트리밍 여부 등 세부 규칙은 명시 안 됨 — 아래 리스크 참고).
  2. `list` — `store.list()`의 전체 노트를 한 줄에 `id`와 `title` 형식으로 출력. 정렬 순서 미지정.
  3. `show NOTE_ID` — `store.get()`으로 조회, 존재하면 title/body/tags/created_at 출력. 존재하지 않으면 **stderr**에 에러 메시지 + **0이 아닌 종료 코드**로 종료(예외 traceback 노출 금지 → try/except로 명시적 처리 필요).
  4. `search [--query Q] [--tag T]` — `search_notes(store, query, tag)`를 그대로 호출(필터링 로직 재구현 금지), 결과를 `list`와 동일한 출력 포맷으로 표시. 두 옵션 모두 선택적(둘 다 생략 가능해 보임 — 이 경우 전체 반환).
  5. `delete NOTE_ID` — `store.delete()` 호출. 성공(`True`) 시 성공 메시지, 실패(`False`, 존재하지 않는 id) 시 stderr 에러 메시지 + 0이 아닌 종료 코드, traceback 없이.
- **진입점**: `main(argv=None) -> int`(관례상), `if __name__ == "__main__": sys.exit(main())`.

### 설계상 필요한 결정 사항 (구현 시 판단 필요, 요구사항에 명시 안 됨)
- `show`/`delete`에서 "없는 id"는 예외가 아니라 `store.get()`이 `None`을 반환하거나 `store.delete()`가 `False`를 반환하는 정상 흐름이므로, `NoteStoreError`(파일 손상 등 별도 예외)와 혼동하지 않고 조건 분기로 처리해야 함 — 다만 `NoteStoreError`(store 파일 자체가 손상된 경우)에 대한 처리 방침은 요구사항에 없음. 이것도 traceback 없이 처리할지, 그대로 노출할지 확인 필요.
- `--tags` 파싱 시 빈 문자열("")이나 공백 처리, 중복 태그 처리 방식은 불명확.
- 종료 코드의 구체적 숫자값(예: 1 vs 2)은 지정되지 않음 — "0이 아닌" 정도만 요구됨.
- `show`/`search`/`list`의 정확한 출력 텍스트 포맷(구분자, 라벨 유무 등)은 예시가 없어 자유도가 있음. 다만 "list와 같은 형식"이라는 제약으로 `list`와 `search`의 포맷 일관성은 명확히 요구됨.
- `add`에서 `TITLE`/`BODY`가 positional argument인데 공백 포함 값 처리(쉘 quoting)는 argparse 기본 동작에 의존.

### 리스크 (Risks)
- **로직 중복 위험**: `search` 서브커맨드가 `search_notes()`를 감싸기만 해야 하는데, 실수로 필터링을 CLI 레벨에서 재구현하면 요구사항 위반(명시적으로 금지됨).
- **에러 처리 누락**: `show`/`delete`에서 예외를 잡지 않고 그대로 흘려보내면 traceback이 노출되어 요구사항(깔끔한 에러 메시지) 위반. `NoteStore` 생성 자체가 실패하는 경우(예: 손상된 JSON, `NoteStoreError`)도 전역적으로 처리할지 결정 필요 — 현재 요구사항은 개별 id 조회 실패만 언급.
- **종료 코드 일관성**: 성공 경로는 0, 실패 경로는 명확히 0이 아닌 값을 반환하도록 모든 분기에서 일관되게 처리해야 함(argparse 자체 에러와 애플리케이션 에러를 구분).
- **--store 경로와 파일 생성**: `NoteStore.__init__`은 파일이 없으면 빈 상태로 시작하고, `save()` 시점에 디렉터리를 생성하므로 이 동작에 의존해도 무방하나, 상위 디렉터리가 없는 경로를 `--store`로 지정한 경우의 동작은 `NoteStore` 구현에 위임됨(CLI에서 별도 처리 불필요).
- **테스트 가능성**: `main(argv=None)`으로 argv를 주입 가능하게 만들어야 자동화 테스트(서브프로세스 대신 함수 직접 호출)가 용이함 — 요구사항에 이미 반영되어 있음.

### 결론
요구사항 자체는 명확하고 실행 가능한 수준으로 구체적이다(옵션명, 기본값, 출력 대상, 에러 처리 방식까지 명시). 모호한 부분은 대부분 "출력 포맷의 세부 텍스트"와 "태그 파싱의 엣지 케이스" 수준이며, 구현을 막을 정도의 불확실성은 없다. 가장 중요한 제약은 (1) `search` 로직을 재구현하지 않고 `search_notes()`를 그대로 호출할 것, (2) `show`/`delete`의 실패 경로에서 traceback 없이 stderr + 0이 아닌 종료 코드로 마무리할 것, 두 가지다.

