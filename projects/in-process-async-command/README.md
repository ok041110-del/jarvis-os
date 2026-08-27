# In-Process Async Command — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`, 기존 Runtime/Engine/Workflow를 수정하지 않는다.

**목적**: `async-command` Prototype(subprocess 기반)에서 "Runtime =
NOT REQUIRED"로 결론 내린 뒤, 같은 질문을 **in-process**(subprocess
없이 `concurrent.futures.ThreadPoolExecutor`) 실행에서 반복 검증한다.
subprocess는 OS 프로세스 경계로 격리를 공짜로 얻지만, in-process
실행은 그 격리가 없다 — 이 차이가 Task/Runtime 경계를 바꾸는지 확인
한다.

**Long-running Operation**: `hqs/development/mvp/tests/test_mvp_0001.py`
(실측 ~69초, 3 passed)를 `pytest.main()`으로 Worker Thread에서 직접
실행한다 — `sleep()`이 아닌 실제 MVP 워크플로 테스트, subprocess
대신 in-process 호출이라는 점만 이전 Prototype과 다르다.

**의존**: `projects/command-contract/`의 `resolver._detect_hq`를
재사용한다. `claude/async-command-prototype` 브랜치(→
`claude/command-contract-prototype` → `claude/unified-dashboard-prototype`)
위에서 작업했다.

**모듈 이름에 `inproc_` 접두어를 붙인 이유**: 처음에는
`async-command`와 동일하게 `operation.py`/`case_a_command_only.py`
등으로 만들었는데, 전체 회귀 테스트(`pytest --ignore=archive`)에서
두 Prototype이 같은 프로세스 안에서 함께 수집되며 **Python
`sys.modules` 이름 충돌**이 실제로 발생했다 — 나중에 import되는
쪽이 먼저 import된 동일 이름 모듈을 그대로 재사용해, 이 Prototype의
테스트가 `async-command`의 `operation.py` 결과 형식(문자열)을 받아
전부 실패했다. 서로 다른 이름으로 분리해 해결했다 — 이 자체가 §Q4에
대한 실제 Evidence다(Task/Command 설계와 무관하게, 이름이 겹치는
두 격리 Prototype도 같은 프로세스에서는 격리되지 않는다).

## 실행

```
python3 projects/in-process-async-command/demo.py
```

Part 1은 Dev HQ 완료(~54~69초)까지 실제로 기다린다. Part 2는 동일
대상(Investment HQ tests)을 두 Thread에서 동시에 실행했을 때 실제로
무슨 일이 일어나는지 관찰한다(§12 Runtime Evaluation 참조 — 결과가
매번 다르다).

## 테스트

```
python3 -m pytest projects/in-process-async-command/tests/ -q
```

Dev HQ 전체 완료(~54~69초) 대기는 테스트 함수 자체에는 없지만, 이
Thread는 in-process라 `terminate()`할 수 없다 — 프로세스 종료 시
`ThreadPoolExecutor`가 자연히 완료를 기다리므로 테스트 자체는
1초대에 끝나도 프로세스 종료까지 ~1분이 걸린다(이 자체가 Evidence,
Evidence 문서 §12 참조).

## 구조

| 파일 | 책임 |
|---|---|
| `inproc_operation.py` | in-process Long-running Operation(ThreadPoolExecutor + pytest.main + hook 기반 결과 수집) |
| `inproc_case_a.py` | Case A — Command에 실행 상태를 직접 담음(mutable, frozen 불가) |
| `inproc_case_b.py` | Case B — Command는 불변, Task가 실행 상태 소유 |
| `inproc_dashboard_view.py` | 읽기 전용 Task Registry 관찰 |
| `demo.py` | 전체 lifecycle 데모 + 동일 대상 동시 실행 탐색 |
| `tests/test_inprocess_async_command.py` | Functional + Boundary Validation |

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`
참조.
