# Command Contract — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`에 구현하지 않는다.

**목적**: "Global Jarvis Chat이 HQ에 작업을 전달하기 위해 Command →
Task → Context라는 별도 계층을 실제로 필요로 하는가?"를 검증한다.
Production Command API를 완성하는 것이 목적이 아니다.

**의존**: `projects/unified-dashboard/`의 읽기 전용 Snapshot
Builder를 재사용한다(두 Experimental Prototype 간 연결, Production
External Interface 아님) — 이 Prototype은 `claude/unified-dashboard-
prototype` 브랜치 위에서 작업됐다.

## 실행

```
python3 projects/command-contract/demo.py
```

## 테스트

```
python3 -m pytest projects/command-contract/tests/ -q
```

## 구조

| 파일 | 책임 |
|---|---|
| `command.py` | `Command`/`CommandResult` — Experimental Prototype Contract(필드는 Evidence 기반 최소만) |
| `resolver.py` | Case A: User -> Command -> HQ Target -> Snapshot(Task 없음) |
| `task_case.py` | Case B: User -> Command -> Task -> HQ(Case A와 비교용) |
| `demo.py` | 수동 실행 데모 |
| `tests/test_command_contract.py` | Functional + Boundary Validation(HQ Isolation, Task 필요성, Command ID 필요성 포함) |

## Boundary

- Engine/Agent를 직접 호출하지 않는다.
- `hqs/*`, `core/*` Python 코드를 import하지 않는다 — `unified-
  dashboard` Prototype의 읽기 전용 Snapshot Builder만 재사용한다.
- Command Layer는 HQ 의미를 해석하지 않는다 — "어떤 HQ로 보낼지"만
  결정하고, 상태 해석은 전부 Snapshot Builder(HQ View 책임)에 있다.
- `Command`/`CommandResult`/`Task`는 Experimental Prototype Contract다
  — Production Contract로 문서화하지 않는다.

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001.md`
참조.
