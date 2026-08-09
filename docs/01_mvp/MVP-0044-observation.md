# MVP-0044 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — `project_intelligence.py`의 `_directory_structure()`가
`__pycache__`만 걸러내고 다른 도구 캐시 디렉토리는 그대로 통과시켜
Planning에 전달되는 Context Bundle을 오염시키던 실제 결함을 재현해
고쳤다.

## 목적

`MVP-0043`(engine.py 죽은 코드 삭제)에 이어, 이번에는 실제로 살아있는
Live Path인 `project_intelligence.collect_relevant_context()` →
`_directory_structure()`를 직접 실행해 결과를 눈으로 확인했다. 이
함수의 반환값은 `build_context_bundle()`을 거쳐 실제 Planning
Engine 호출(`requirements_agent_requirement_analysis`)의 입력에 그대로
포함된다 — Project Intelligence가 실제 Engine에게 "이 프로젝트의
구조가 이렇다"고 알려주는 신호다.

## 선정한 실제 업무 — 직접 실행으로 재현

```python
>>> from mvp.project_intelligence import _directory_structure
>>> [d for d in _directory_structure() if 'cache' in d.lower()]
['development-hq/.pytest_cache/']
```

`_directory_structure()`는 `__pycache__`만 명시적으로 제외한다
(`"__pycache__" in rel.parts`). 하지만 이 저장소의 `.gitignore`에는
`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`도 함께 등록돼 있다 —
즉 이들도 `__pycache__`와 같은 부류(생성된 빌드/테스트 산출물, 프로젝트
구조가 아님)로 이미 분류돼 있다. 하지만 코드는 `__pycache__`만
걸러낸다. 이 저장소에서 pytest를 한 번이라도 실행하면(이번
Dogfooding 세션에서도 매번 실행함) `development-hq/.pytest_cache/`가
생기고, 그 즉시 `_directory_structure()`의 출력에 나타난다 — 실제로
재현했다(위 코드 그대로 실행한 raw 출력).

같은 클래스의 문제가 `.mypy_cache`/`.ruff_cache`에도 적용됨을
디렉터리를 실제로 만들어 확인했다:

```python
# development-hq/.mypy_cache/, docs/.ruff_cache/ 실제로 생성 후
>>> [d for d in _directory_structure() if 'cache' in d.lower()]
['development-hq/.mypy_cache/', 'development-hq/.pytest_cache/', 'docs/.ruff_cache/']
```

## 실제 코드베이스 구현 — 최소화

`development-hq/mvp/project_intelligence.py`의 `_directory_structure()`
직전에 `_NOISE_DIR_NAMES` frozenset(`__pycache__`/`.pytest_cache`/
`.mypy_cache`/`.ruff_cache`)을 추가하고, 기존 단일 이름 비교
(`"__pycache__" in rel.parts`)를 집합 교집합(`_NOISE_DIR_NAMES &
set(rel.parts)`)으로 바꿨다 — `__pycache__` 제외가 이미 쓰던 것과
같은 기법(디렉터리 이름 리터럴 비교)을 그대로 확장했을 뿐, `.gitignore`
파서나 일반화된 "무시 규칙" 개념을 새로 만들지 않았다. `max_depth`
비교, 반환 형식(`str(rel) + "/"` 등)은 손대지 않았다.

새 Capability/Agent/Component를 추가하지 않았다 — 기존 함수 하나의
제외 목록만 넓혔다.

## 검증 (실제 실행, mock 없음)

### 결함 재현 케이스 — 수정 후

```
$ mkdir -p development-hq/.mypy_cache docs/.ruff_cache && touch .../dummy.txt
$ python3 -c "... noise = [d for d in _directory_structure() if 'cache' in d.lower()]; print(noise)"
noise entries: []
```

`.pytest_cache`/`.mypy_cache`/`.ruff_cache` 모두 더 이상 나타나지
않는다.

### 실제 pytest 실행 후에도 깨끗함

```
$ python3 -m pytest development-hq/mvp/tests -q
...                                                                      [100%]
3 passed in 82.01s (0:01:22)
$ python3 -c "... noise entries after real pytest run: []"
```

이 저장소에서 실제로 pytest를 돌려 `.pytest_cache/`가 다시 생성된
뒤에도(수정 전이라면 이 시점에 결함이 재현됐다) `_directory_structure()`
출력은 깨끗했다.

### 정상 경로 회귀 확인

수정한 `_directory_structure()`는 `collect_relevant_context()` →
`build_context_bundle()`의 유일한 `directory_structure` 소스이며, 위
pytest 3건(실제 Engine 호출 포함, real Issue로 Planning까지 실행하는
케이스 포함)이 모두 그대로 통과해 정상 경로에 회귀가 없음을 확인했다.

### 불필요한 변경 확인

```
$ git status --porcelain
 M development-hq/mvp/project_intelligence.py
```

`development-hq/mvp/project_intelligence.py` 1개 파일만 변경했다.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — 건드리지 않음 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — 건드리지 않음 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 헬퍼 함수의 제외 목록만 넓힘 |
| 새 Architecture/Concept/Component 필요 | 미발동 — `.gitignore` 파서 등 일반화 메커니즘을 만들지 않았다 |
| Production caller/Kernel Component/Runtime/Prompt Cache 착수 | 미발동 — 전혀 건드리지 않았다 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `.gitignore` 내용을 실제로 파싱해 제외 목록을 자동 생성하는 것 —
  하지 않았다. `__pycache__`가 이미 쓰던 것과 같은 리터럴 이름 방식만
  확장했다. 새 일반화 메커니즘(설정 파일 읽기 등)은 Kernel Extraction
  후보이지 지금 만들 대상이 아니다.
- `.gitignore`의 다른 항목(`.venv/`, `.DS_Store`, `.vscode/`,
  `.idea/`) — 이 저장소의 `development-hq/`나 `docs/` 아래에서 실제로
  생성되는 것을 관찰하지 못해 추가하지 않았다(재현하지 못한 항목을
  등록하지 않는다는 이 파일의 기존 원칙, `NEGATED_MARKER_EXCEPTIONS`
  주석 참고).
- `CATEGORY_PATHS`(`_relevant_files`)의 `exclude_dirs` — 해당 glob
  패턴(`*.py`, `*.md`, `RFC-*.md` 등)이 캐시 디렉토리 안의 파일과
  실제로 매치되는지 확인했으나(캐시 디렉토리는 `.py`/`.md` 산출물을
  만들지 않음) 재현되지 않아 손대지 않았다.
- 새 RFC/ADC/ADR — 만들지 않았다. Architecture 결정이 필요한 지점을
  만나지 않았다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`project_intelligence.py`)**.
  실제 실행으로 재현한 실제 결함(캐시 디렉토리가 Context Bundle에
  노출됨)만 고쳤다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `_directory_structure()`의 시그니처와 반환 형식을 그대로
  유지했다.
- 실제 Engine으로 확인했는가 — **예**. 결함 재현(수정 전/후), 실제
  pytest 실행으로 `.pytest_cache/` 재생성 후에도 깨끗함 확인, 기존
  pytest 3건(real Engine 호출 포함, mock 없음) 재실행.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 발견 →
  수정 → 검증을 이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `engine.py`,
  `workflow*.py`, `cli.py` 어디에도 손대지 않았다(`git status
  --porcelain` 확인).
