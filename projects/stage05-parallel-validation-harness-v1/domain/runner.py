"""Single Sequential Validation vs 6-way Parallel Validation — Experiment A.

Dispatch 정책(Governance 근거, `STAGE05-TEST-ISOLATION-VALIDATION-0001.md`
§1.5/§3.2 재확인):
- Structure/Scope/AST/Dependency/Review(5개, 파일 mutation 없음) —
  `ThreadPoolExecutor`(Stage 01 `ParallelRunner` 선례와 동일 계열, I/O-bound
  Engine 호출·경량 CPU 작업).
- Test(파일 mutation 있음, 유일한 공유 가변 자원 후보) — `ProcessPoolExecutor`
  (`ADC-0015` Thread 금지·Process 1차 원칙, `execution_host.py::run_isolated`와
  동일 전략 — 단, Test 자신은 이미 Workspace로 격리돼 있으므로 이 Process
  격리는 이중 안전장치다).
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass

from .results import ValidatorResult, sort_by_fixed_id_order
from .review import ReviewConfig, review_validator
from .test_node import TestNodeConfig, run_test_validator
from .validators import (
    ValidationContext,
    ast_validator,
    dependency_validator,
    scope_validator,
    structure_validator,
)

_THREAD_VALIDATOR_IDS = ("structure", "scope", "ast", "dependency", "review")


@dataclass
class RunResult:
    mode: str  # "single" | "parallel"
    ordered_results: list
    total_wall_clock_ms: float
    process_count: int
    thread_count: int


def _run_structure(ctx: ValidationContext) -> ValidatorResult:
    return structure_validator(ctx)


def _run_scope(ctx: ValidationContext) -> ValidatorResult:
    return scope_validator(ctx)


def _run_ast(ctx: ValidationContext) -> ValidatorResult:
    return ast_validator(ctx)


def _run_dependency(ctx: ValidationContext) -> ValidatorResult:
    return dependency_validator(ctx)


def _run_review(ctx: ValidationContext, review_config: ReviewConfig) -> ValidatorResult:
    return review_validator(ctx, review_config)


def _run_test(ctx: ValidationContext, test_config: TestNodeConfig) -> ValidatorResult:
    return run_test_validator(ctx.implementation, test_config)


def run_single(ctx: ValidationContext, review_config: ReviewConfig, test_config: TestNodeConfig) -> RunResult:
    """Structure -> Scope -> AST -> Dependency -> Test -> Review, 순서대로
    1개씩. 각 Validator가 다른 Validator의 결과를 실제로 쓰지 않는다는
    것(RFC-0039 §2)을 확인하기 위해 순서를 지켜도 각 함수는 `ctx`만
    받는다 — 이전 Validator의 출력이 다음 Validator의 입력에 섞이지
    않는다."""
    start = time.perf_counter()
    results = [
        _run_structure(ctx),
        _run_scope(ctx),
        _run_ast(ctx),
        _run_dependency(ctx),
        _run_test(ctx, test_config),
        _run_review(ctx, review_config),
    ]
    total_ms = (time.perf_counter() - start) * 1000
    return RunResult(
        mode="single",
        ordered_results=sort_by_fixed_id_order(results),
        total_wall_clock_ms=total_ms,
        process_count=1,  # Test 내부 pytest subprocess는 별도로 계산하지 않음(Dispatch 축 기준)
        thread_count=1,
    )


def run_parallel(ctx: ValidationContext, review_config: ReviewConfig, test_config: TestNodeConfig) -> RunResult:
    """6개 Validator를 동시에 시작한다. Test만 별도 Process에서, 나머지
    5개는 Thread Pool에서 — 실행 완료 순서와 무관하게 결과는 항상 고정
    ID 순서로 정렬한다(사용자 지시)."""
    start = time.perf_counter()
    results: list[ValidatorResult] = []

    with ThreadPoolExecutor(max_workers=5) as thread_pool, ProcessPoolExecutor(max_workers=1) as process_pool:
        thread_futures = {
            "structure": thread_pool.submit(_run_structure, ctx),
            "scope": thread_pool.submit(_run_scope, ctx),
            "ast": thread_pool.submit(_run_ast, ctx),
            "dependency": thread_pool.submit(_run_dependency, ctx),
            "review": thread_pool.submit(_run_review, ctx, review_config),
        }
        process_future = process_pool.submit(_run_test, ctx, test_config)

        for vid, future in thread_futures.items():
            results.append(future.result())
        results.append(process_future.result())

    total_ms = (time.perf_counter() - start) * 1000
    return RunResult(
        mode="parallel",
        ordered_results=sort_by_fixed_id_order(results),
        total_wall_clock_ms=total_ms,
        process_count=1,
        thread_count=5,
    )
