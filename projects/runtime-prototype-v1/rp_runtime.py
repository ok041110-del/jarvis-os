"""Runtime Prototype — 최소 실행 조정 계층.

담당(작업 지시 "Prototype 범위"):

1. Execution Unit 생성/등록 (`create_unit`)
2. Execution Unit 실행 요청 (`start`)
3. Execution Unit 상태 조회 (`status`)
4. Execution Unit 종료/정리 (`cleanup`)
5. Execution 결과 수집 (`result`)

Execution Host(`rp_execution_host.run_isolated`)를 대체하지 않는다 —
단일 실행의 dispatch·격리는 여전히 Execution Host가 수행한다. Runtime은
여러 Execution Unit의 lifecycle과 "제출 후 폴링" 형태의 비동기
호출만 조정한다.

포함하지 않는 것(작업 지시 "Prototype에서 하지 말 것"): Scheduler,
Workflow Engine/Parser, Policy Engine, Agent Manager, Event Bus, Model
Routing, Engine Gateway, Multi-Agent orchestration, 새 Public
Contract, 새 Kernel Module.
"""

from __future__ import annotations

import itertools
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

import rp_execution_host

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_DONE = "DONE"
STATUS_FAILED = "FAILED"

_id_counter = itertools.count(1)
_id_lock = threading.Lock()


@dataclass
class ExecutionUnit:
    unit_id: int
    func: Callable[..., Any]
    args: tuple
    kwargs: dict
    status: str = STATUS_PENDING
    result: Any = None
    error: str | None = None
    future: Future | None = field(default=None, repr=False)


class UnknownExecutionUnitError(KeyError):
    """등록되지 않았거나 이미 정리된 unit_id를 참조했을 때."""


class Runtime:
    """단일 Runtime 인스턴스 — 여러 Execution Unit의 lifecycle을
    등록·조정한다. Execution Unit identity(§16.3 Task/Command와 동형의
    관계)는 Runtime이 소유하고, 실제 dispatch·격리는 매번
    `rp_execution_host.run_isolated`에 위임한다(Execution Host를
    감싸지 직접 대체하지 않는다)."""

    def __init__(self, max_concurrency: int = 4) -> None:
        self._units: dict[int, ExecutionUnit] = {}
        self._pool = ThreadPoolExecutor(max_workers=max_concurrency)

    def create_unit(self, func: Callable[..., Any], *args, **kwargs) -> int:
        with _id_lock:
            unit_id = next(_id_counter)
        self._units[unit_id] = ExecutionUnit(unit_id=unit_id, func=func, args=args, kwargs=kwargs)
        return unit_id

    def _get(self, unit_id: int) -> ExecutionUnit:
        try:
            return self._units[unit_id]
        except KeyError as exc:
            raise UnknownExecutionUnitError(unit_id) from exc

    def start(self, unit_id: int) -> None:
        unit = self._get(unit_id)
        if unit.status != STATUS_PENDING:
            raise ValueError(f"unit {unit_id} already started (status={unit.status})")
        unit.status = STATUS_RUNNING

        def _run() -> None:
            try:
                value = rp_execution_host.run_isolated(unit.func, *unit.args, **unit.kwargs)
                unit.result = value
                unit.status = STATUS_DONE
            except Exception as exc:  # noqa: BLE001 - Execution Host 예외를 상태로 보존
                unit.error = str(exc)
                unit.status = STATUS_FAILED

        unit.future = self._pool.submit(_run)

    def status(self, unit_id: int) -> str:
        return self._get(unit_id).status

    def result(self, unit_id: int, wait: bool = True) -> Any:
        unit = self._get(unit_id)
        if wait and unit.future is not None:
            unit.future.result()
        if unit.status == STATUS_FAILED:
            raise RuntimeError(unit.error)
        return unit.result

    def cleanup(self, unit_id: int) -> None:
        unit = self._units.pop(unit_id, None)
        if unit is not None and unit.future is not None:
            unit.future.cancel()

    def shutdown(self) -> None:
        self._pool.shutdown(wait=True)
