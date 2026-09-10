# Runtime Prototype v1 (Experimental Implementation)

**목적**: ADC-02(`docs/decisions/adc/ADC.md`, Open · NOW)의 최종
Architecture Decision을 내리기 전에, Runtime이라는 추상화가 실제
Jarvis OS 실행 구조에서 유용한지 실행 Evidence로 검증한다. **이
Prototype은 Runtime 채택을 결정하지 않는다.**

전체 Evidence·Q1~Q5 평가·최종 판정(USEFUL/NEUTRAL/NOT_USEFUL)은
`EVIDENCE.md` 참조.

## 구조

```
Caller
  │
  ▼
Runtime (rp_runtime.py)          ← 이번 Prototype이 검증하는 대상
  │  create_unit / start / status / result / cleanup
  ▼
Execution Host (rp_execution_host.py)  ← Production Contract 재현(Accept, Scoped)
  │  run_isolated(func, *args, **kwargs)
  ▼
Engine (rp_target.py → 실제 pytest 스위트)
```

Runtime은 Execution Host를 대체하지 않는다 — 단일 실행의 dispatch·
격리는 여전히 Execution Host(`rp_execution_host.run_isolated`)가
수행한다. Runtime은 여러 Execution Unit의 lifecycle과 "제출 후 폴링"
형태의 비동기 호출만 조정한다.

## 파일

| 파일 | 역할 |
|---|---|
| `rp_execution_host.py` | Production `hqs/development/mvp/execution_host.py`의 Accepted Contract를 격리 환경에서 재현(Production import 없음) |
| `rp_runtime.py` | 이번 실험이 검증하는 Runtime Prototype 본체 |
| `rp_target.py` | 실제 Engine 실행 대상 — 저장소의 실제 pytest 스위트를 Worker Process에서 실행 |
| `tests/test_baseline_direct_execution_host.py` | Baseline 시나리오(Caller → Execution Host, Runtime 없음) |
| `tests/test_runtime_prototype.py` | Runtime Prototype 시나리오(Caller → Runtime → Execution Host) |
| `tests/test_isolation_guardrails.py` | Experimental Implementation 격리 검증(AST + `git diff`) |
| `EVIDENCE.md` | 전체 Evidence·비교·Q1~Q5 평가·최종 판정 |

## 격리

`hqs/`, `core/`를 import하거나 수정하지 않는다(`test_isolation_guardrails.py`로
자동 검증). Scheduler/Workflow Engine/Policy Engine/Agent Manager/
Event Bus/Model Routing/Engine Gateway/Multi-Agent orchestration은
포함하지 않는다. 새 Public Contract·새 Kernel Module을 만들지
않는다.

## 실행

```
pytest projects/runtime-prototype-v1/tests/ -v
```
