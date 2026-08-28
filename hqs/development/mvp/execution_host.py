"""Execution Host — 단일 실행 단위 dispatch·격리(`docs/architecture/baseline/BASELINE.md`
§16.3, `docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`
Conditional Accept).

구현 전략: Process(`ProcessPoolExecutor`) 1차 — Thread는 사용하지
않는다(`ADC-0015` §Q0, 동일 Target 동시 실행 오염 반복 관찰).
`동기(블로킹) 호출`만 제공한다 — 비동기 lifecycle(PENDING/RUNNING
상태 조회)은 `hqs/development/MVP.md` Out of Scope("Background
Execution / Distributed Execution")를 넘지 않기 위해 구현하지
않는다. Scheduler/Task Registry/Multi-Task orchestration도 포함하지
않는다 — 단일 호출을 격리된 Worker Process에서 실행하고 결과를
반환할 뿐이다.

`func`는 `ProcessPoolExecutor`로 전달 가능해야 한다(모듈 최상위에서
importable 해야 함 — 클로저·람다·인스턴스 메서드 불가).
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
