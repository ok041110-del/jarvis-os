# Process Runtime Strategy — Experimental Validation

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`, 기존 Runtime/Engine/Workflow를 수정하지 않는다.

**목적**: `runtime-boundary` Prototype이 남긴 결론(Runtime =
CANDIDATE, Process가 Thread보다 정확·안정적)을 두 방향으로 넓혀
검증한다.

1. Process 전략을 **Investment HQ 한 파일**이 아니라 **서로 다른
   실제 Dev HQ Validation 작업 여러 개**에 반복 적용해도 정확성·
   격리·실행시간이 안정적인지.
2. **"동일 Target 동시 실행"에서만 Process가 필요한가, 아니면
   "다른 Target 동시 실행"에서도 필요한가**를 실제로 구분한다 —
   Dev HQ 내부의 서로 다른 두 실제 테스트 파일(모두 monkeypatch를
   쓰지 않음)을 Thread로 동시 실행해도 안전한지 실측했다.

**의존**: `projects/runtime-boundary/`의 `rtb_runtime.py`(Sequential/
Thread/Process Dispatcher)와 `rtb_task.py`(Task identity/lifecycle)
를 그대로 재사용한다 — 중복 구현하지 않는다. `claude/runtime-
boundary-prototype` 브랜치(→ `claude/inprocess-async-command-
prototype` → `claude/async-command-prototype` → `claude/command-
contract-prototype` → `claude/unified-dashboard-prototype`) 위에서
작업했다.

## 실측 결론 요약

| 조건 | Thread | Process |
|---|---|---|
| Sequential(비교 baseline) | 해당 없음 — 동시성 없음 | 해당 없음 |
| 동일 Target 동시 실행(Investment, monkeypatch 있음) | **불안정**(결과 오염, 지연 폭증 — `runtime-boundary` Evidence 재확인) | 항상 정확·안정 |
| 서로 다른 Target 동시 실행(Dev HQ 내부, monkeypatch 없음) | **정상**(5/5 반복 정확) | 정상(추가 비용만 있음, §본문) |
| 서로 다른 실제 Dev HQ Validation 3종 반복(Process만) | 해당 없음 | 정확성 100%, 실행시간은 baseline과 대체로 일치 |

**Process가 필요한 조건은 "동일 Target을 동시 실행할 가능성이 있는가"
로 좁혀진다** — 서로 다른 대상이라면 Thread로도 실제 문제가 없었다
(§본문, Dev HQ 내부/Cross-HQ 양쪽에서 재확인). `subprocess` 방식
(`async-command` Prototype)은 이 조건과 무관하게 항상 안전했지만
프로세스 생성 비용이 더 크다(비교는 본문 참조).

## 실행

```
python3 projects/process-runtime-strategy/demo.py
```

## 테스트

```
python3 -m pytest projects/process-runtime-strategy/tests/ -q
```

## 구조

| 파일 | 책임 |
|---|---|
| `prs_dev_validation.py` | 서로 다른 실제 Dev HQ Validation 3종에 Process 전략을 반복 적용 |
| `demo.py` | Sequential/Thread/Process × 동일/다른 Target 비교 데모 |
| `tests/test_process_runtime_strategy.py` | Functional + Boundary Validation |

`rtb_runtime.py`/`rtb_task.py`는 그대로 재사용(이 디렉터리에 복사
하지 않음, `sys.path`로 `../runtime-boundary/` 참조).

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001.md`
참조.
