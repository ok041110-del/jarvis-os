# Fix Cycle: NoteStore Context-following failure + missing parent dir

## 결함 1 — Context로 넘긴 파일 이름을 따르지 않음(실제 재현)

`store.py`의 `[Existing Code]` Context는 `models.py`(경로까지 정확히
명시)의 실제 코드를 그대로 포함하고 있었는데도, 생성된 코드는
`from .note import Note`(단수형 "note")를 import했다 — 실제 파일
이름은 `models.py`다.

```
$ python3 -c "import notekeeper.store"
ModuleNotFoundError: No module named 'notekeeper.note'
```

주목할 점: 첫 real `code_review`는 이 결함을 **지적하지 않았다** —
Validation Capability는 텍스트만 검토하고 실제로 import를 실행하지
않으므로, "존재하지 않는 모듈을 참조하는 import 한 줄"은 텍스트만
봐서는 완전히 정상적인 코드로 보인다. **실제 import 실행만이 이
결함을 드러냈다.**

### Fix

원본 코드 + 실제 traceback을 `backend_agent_code_generation()`에
입력해 재호출 — `from .models import Note`로 정정됨. 재확인:

```
$ python3 -c "import notekeeper.store"  # 성공
```

## 결함 2 — save()가 부모 디렉토리를 만들지 않음(real Review + 실제 재현)

두 번째 real Review가 지적: `save()`는 `self.path.parent`가 없을
때를 처리하지 않는다. 직접 재현:

```python
store = NoteStore(Path(d) / "sub" / "dir" / "notes.json")
store.add(Note.new("x", "y"))
# FileNotFoundError: [Errno 2] No such file or directory: '.../sub/dir/notes.json.tmp'
```

### Fix

`save()` 맨 앞에 `self.path.parent.mkdir(parents=True,
exist_ok=True)` 한 줄 추가 — Engine을 다시 호출하지 않고 직접
수정했다(한 줄짜리 명백한 수정이며, 다른 로직에 영향이 없음을 실제
실행으로 즉시 확인 가능했기 때문).

### 검증

```python
store = NoteStore(Path(d) / "sub" / "dir" / "notes.json")
store.add(Note.new("x", "y"))
print(p.exists())  # True
```

세 번째 real Review(최종 코드)는 두 결함 모두 더 이상 지적하지
않았다. 남은 지적(동시성 미보호, 임시 파일 이름 충돌 가능성, `fsync`
없음)은 이 프로젝트가 단일 프로세스 사용을 전제한다는 README의
명시적 Out of Scope와 일치해 반영하지 않았다.
