# Async / Long-running Command — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`, 기존 Runtime/Engine/Workflow를 수정하지 않는다.

**목적**: "실행이 즉시 끝나지 않는 순간, Command만으로는 무엇을
표현할 수 없게 되는가?"를 실제 장시간 작업으로 검증한다.

**Long-running Operation**: `sleep()`이 아니라 저장소의 실제 테스트
스위트를 subprocess로 실행한다(`pytest hqs/development/mvp/tests -q`,
실측 ~70~90초, 120 passed / `pytest hqs/investment/tests -q`, 실측
<1초, 16 passed) — Dashboard Prototype이 이미 "Latest Validation"
으로 인용한 바로 그 작업.

**의존**: `projects/command-contract/`의 `resolver._detect_hq`를
재사용한다(중복 구현 금지). `claude/command-contract-prototype`
브랜치(→ `claude/unified-dashboard-prototype`) 위에서 작업했다.

## 실행

```
python3 projects/async-command/demo.py
```

## 테스트

```
python3 -m pytest projects/async-command/tests/ -q
```

Dev HQ 전체 완료(~70~90초) 대기는 자동 테스트에 포함하지 않는다 —
`operation.terminate()`로 RUNNING 상태 확인 후 즉시 정리한다. 전체
완료 관찰은 `demo.py` 수동 실행 결과로 Evidence 문서에 기록한다.

## 구조

| 파일 | 책임 |
|---|---|
| `operation.py` | 실제 Long-running Operation(subprocess) 시작/폴링/캐싱된 완료 상태 |
| `case_a_command_only.py` | Case A — Command 하나에 실행 상태를 직접 담음(mutable, frozen 불가) |
| `case_b_command_task.py` | Case B — Command는 불변, Task가 실행 상태 소유(Registry 조회 가능) |
| `dashboard_view.py` | 읽기 전용 Task Registry 관찰(Dashboard = Observe 원칙 검증) |
| `demo.py` | 전체 lifecycle 수동 실행 데모 |
| `tests/test_async_command.py` | Functional + Boundary Validation |

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`
참조.
