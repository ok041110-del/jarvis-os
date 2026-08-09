# MVP-0042 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — `development-hq/mvp/cli.py`(MVP-0001 실행 진입점)를 실제로
실행해 발견한 실제 결함(잘못된 CLI 인자에서 raw traceback으로 죽음)을
그 자리에서 고치고 재검증했다.

## 목적

이번 세션은 `MVP-0041`처럼 `workflow_0008.run_pipeline()` 전체를 다시
Dogfooding하는 대신, 실제 사용자가 만지는 진입점(`cli.py`)을 직접
실행해 실제 개발 업무를 찾았다 — Development HQ MVP-0001의 유일한
CLI 진입점이므로, 이 지점의 결함은 이 저장소를 실제로 쓰는 모든
사람에게 그대로 노출된다.

## 선정한 실제 업무 — 직접 실행으로 재현

```
$ python3 development-hq/mvp/cli.py /tmp/doesnotexist.py
Traceback (most recent call last):
  File ".../cli.py", line 32, in <module>
    main()
  File ".../cli.py", line 17, in main
    with open(sys.argv[1], "r", encoding="utf-8") as f:
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/doesnotexist.py'

$ python3 development-hq/mvp/cli.py /tmp
Traceback (most recent call last):
  File ".../cli.py", line 32, in <module>
    main()
  File ".../cli.py", line 17, in main
    with open(sys.argv[1], "r", encoding="utf-8") as f:
IsADirectoryError: [Errno 21] Is a directory: '/tmp'
```

`cli.py`는 `sys.argv[1]`을 `open()`할 때 예외를 전혀 잡지 않는다.
존재하지 않는 경로, 디렉터리 경로 등 흔한 사용자 실수가 그대로 Python
raw traceback으로 나타난다 — MVP.md Exit Criteria("입력 코드가 주어지면,
수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환된다")가
말하는 "정상 입력"의 경우가 아니라, 그 이전 단계(입력을 읽는 단계)에서
사용자에게 아무 맥락 없는 traceback만 보여주는 문제다.

## 실제 코드베이스 구현 — 최소화

`development-hq/mvp/cli.py`의 `main()`에서 파일을 여는 부분만
`try/except OSError`로 감쌌다:

- 파일을 열 수 없으면(`FileNotFoundError`, `IsADirectoryError`,
  `PermissionError` 등 `OSError`의 하위 클래스 전부) 어떤 경로가
  왜 문제인지(`exc.strerror`) 한 줄로 stderr에 출력하고 `exit(1)`한다.
- 파일을 정상적으로 열 수 있는 경우의 동작(코드 읽기 → `run_mvp_0001`
  실행 → 출력)은 한 글자도 바꾸지 않았다.
- stdin 입력 경로(`sys.argv`가 없을 때)는 건드리지 않았다 — 이
  결함과 무관하다.

새 Capability/Agent/Component를 추가하지 않았다 — 기존 함수
(`main()`) 안의 예외 처리 범위만 넓혔다.

## 검증 (실제 실행)

### 결함 재현 케이스 2개 — 수정 후

```
$ python3 development-hq/mvp/cli.py /tmp/doesnotexist.py; echo "exit:$?"
Cannot read '/tmp/doesnotexist.py': No such file or directory
exit:1

$ python3 development-hq/mvp/cli.py /tmp; echo "exit:$?"
Cannot read '/tmp': Is a directory
exit:1
```

raw traceback 대신 원인이 명확한 한 줄 메시지와 비정상 종료 코드(1)를
반환한다.

### 정상 경로 회귀 확인 — 실제 Engine으로 재확인 (mock 없음)

유효한 파일(`mutable default` + `bare except`가 있는 실제 Python
코드)로 `cli.py`를 실제 Engine을 통해 재실행해, 기존과 동일한 형식
(`## Code Review` / `## Test Case Suggestions`)으로 정상 출력됨을
확인했다 — 파일을 여는 부분에 추가한 `try/except`가 정상 경로에 아무
영향을 주지 않았다.

### 기존 테스트 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
...                                                                      [100%]
3 passed in 80.62s (0:01:20)
```

real Engine 호출 포함 3건 모두 통과(mock 없음).

### 불필요한 변경 확인

```
$ git status --porcelain
 M development-hq/mvp/cli.py
```

`development-hq/mvp/cli.py` 1개 파일만 변경했다.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — 건드리지 않음 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — 건드리지 않음 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 `main()`의 예외 처리 범위만 넓힘 |
| 새 Architecture/Concept/Component 필요 | 미발동 |
| Production caller/Kernel Component/Runtime/Prompt Cache 착수 | 미발동 — 전혀 건드리지 않았다 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- stdin 입력 경로 — 이 결함과 무관해 건드리지 않았다.
- `run_mvp_0001()` 내부 로직 — 건드리지 않았다(MVP-0036/0037이 이미
  Engine 호출 실패를 처리한다).
- 새 RFC/ADC/ADR — 만들지 않았다. Architecture 결정이 필요한 지점을
  만나지 않았다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`cli.py`)**. 실제 실행으로
  재현한 실제 결함(잘못된 CLI 인자에서 raw traceback)만 고쳤다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `main()`의 시그니처와 정상 경로 동작을 그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. 결함 재현 2건(수정 전/후),
  정상 경로 재확인 1회(real `claude -p` 호출 2회, mock 없음), 기존
  pytest 3건(real Engine 포함) 재실행.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 발견 →
  수정 → 검증을 이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
  만났다면 중단하고 보고했을 것이다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `engine.py`,
  `workflow*.py`, `project_intelligence.py` 어디에도 손대지 않았다
  (`git status --porcelain` 확인).
