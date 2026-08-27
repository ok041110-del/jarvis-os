# Runtime Boundary — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`, 기존 Runtime/Engine/Workflow를 수정하지 않는다.

**목적**: `in-process-async-command` Prototype이 발견한 문제(동일
실제 대상을 Thread에서 동시 실행하면 `monkeypatch` 상태가 섞여
실제 테스트 실패가 재현됨,
`docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`
§8/§12)를 최소 재현하고, Sequential / Thread / Process 세 실행
전략을 실제로 비교해 Runtime(scheduling/isolation)과 Task(lifecycle/
identity)의 책임 경계를 검증한다.

## 실행 전략 비교(실측)

동일 대상(`hqs/investment/tests/test_stock_team_integration.py`,
baseline 2 passed)을 두 번 동시 실행:

| 전략 | 즉시 반환(비동기)? | 동일 대상 동시 실행 결과 | 비고 |
|---|---|---|---|
| Sequential | 아니오(블로킹) | 항상 정확(4/4) | 동시성 자체가 없음 — 비교 baseline |
| Thread | 예 | **불안정 — 오염되거나(combined≠4), 대상 코드 자체의 내부 ThreadPoolExecutor(`stock_team.py`)와 중첩되어 심각하게 느려짐(0.03초 → 최대 16~37초 관찰)** | 프로세스 메모리 공유 |
| Process | 예 | 항상 정확(4/4), 속도도 안정적(~0.7초) | OS 프로세스 경계로 격리 |

## 의존

`hqs/investment/tests/test_stock_team_integration.py`를 재사용
(직접 import 없음, `pytest.main()`으로만 호출). Command Contract/
Dashboard Prototype의 `resolver`/`snapshot`은 이번에는 필요하지
않았다(이 Prototype은 Command 라우팅이 아니라 Task/Runtime 경계만
다룬다). `claude/inprocess-async-command-prototype` 브랜치 위에서
작업했다(Evidence 연속성 — 새 코드 의존은 없음).

## 실행

```
python3 projects/runtime-boundary/demo.py
```

## 테스트

```
python3 -m pytest projects/runtime-boundary/tests/ -q
```

`test_thread_execution_on_identical_target_can_produce_contaminated_results`
는 최대 5회 재시도 안에 오염 재현을 확인한다(확률적 현상이므로 —
Evidence 문서 §8 참조). Thread 전략을 쓰는 테스트는 대상 코드의
중첩 ThreadPoolExecutor 때문에 실행 시간이 실행마다 크게 달라질 수
있다(위 표 참조) — Process 전략 테스트는 항상 안정적이다.

## 구조

| 파일 | 책임 |
|---|---|
| `rtb_runtime.py` | Scheduling/Isolation — Sequential/Thread/Process 세 전략으로 실제 pytest 실행 |
| `rtb_task.py` | Identity/Lifecycle — Executor를 직접 참조하지 않음(rtb_runtime만 호출) |
| `rtb_dashboard_view.py` | 읽기 전용 Task Registry 관찰(전략과 무관) |
| `demo.py` | 세 전략 비교 데모 |
| `tests/test_runtime_boundary.py` | Functional + Boundary Validation |

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md`
참조.
