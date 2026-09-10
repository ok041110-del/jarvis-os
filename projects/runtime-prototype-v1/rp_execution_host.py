"""Runtime Prototype 전용 Execution Host stand-in.

Production `hqs/development/mvp/execution_host.py`의 Accepted Contract
(Process 1차, 블로킹 `run_isolated`, `ADC-0015-execution-host-implementation-
strategy.md` Conditional Accept)를 격리 환경에서 동일하게 재현한다.
Production 모듈은 import하지 않는다 — `docs/00_governance/
ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation"의 HQ production
path 무단 연결 금지, `runtime-boundary`/`process-runtime-strategy`
Prototype이 지켜온 격리 관행(Production import 대신 동일 Contract를
Prototype 내부에 재구현)을 그대로 따른다.

이 모듈 자체는 이번 Prototype의 검증 대상이 아니다 — Execution Host의
"단일 실행 단위 dispatch·격리" 책임은 이미 `ADC-0013`/`ADC-0015`로
Accept됐다. 이번 실험은 그 위에 Runtime 계층을 얹었을 때 어떤 차이가
생기는지만 검증한다.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")

_EXECUTOR = ProcessPoolExecutor(max_workers=4)


def run_isolated(func: Callable[..., T], *args, **kwargs) -> T:
    """`func(*args, **kwargs)`를 격리된 Worker Process에서 실행하고
    완료까지 블로킹해 결과(또는 예외)를 그대로 반환한다."""
    future = _EXECUTOR.submit(func, *args, **kwargs)
    return future.result()
