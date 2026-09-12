"""ParallelRunner 검증 — 정상 병렬 실행/timeout/retry/partial failure/invalid
output/concurrent task isolation을 확인한다(`mvp/parallel_runner.py`)."""

import time

from ..parallel_runner import ParallelRunner, ParallelTask, RetryPolicy, TaskStatus


class _CustomInvalidError(ValueError):
    pass


def test_tasks_run_concurrently_not_sequentially():
    def sleep_task(_):
        time.sleep(0.2)
        return "ok"

    tasks = [ParallelTask(task_id=f"t{i}", executor=sleep_task) for i in range(5)]

    started = time.monotonic()
    batch = ParallelRunner(max_workers=5).run(tasks)
    elapsed = time.monotonic() - started

    assert elapsed < 0.6  # 순차 실행이었다면 5 * 0.2s = 1.0s 이상 걸린다
    assert all(r.status == TaskStatus.SUCCESS for r in batch.results)
    assert batch.summary["SUCCESS"] == 5


def test_task_timeout_produces_timeout_status_without_blocking_others():
    def slow(_):
        time.sleep(0.5)
        return "too-slow"

    def fast(_):
        return "fast"

    tasks = [
        ParallelTask(task_id="slow", executor=slow, timeout=0.05),
        ParallelTask(task_id="fast", executor=fast, timeout=5),
    ]
    batch = ParallelRunner(max_workers=2).run(tasks)

    assert batch.by_id("slow").status == TaskStatus.TIMEOUT
    assert batch.by_id("fast").status == TaskStatus.SUCCESS
    assert batch.by_id("fast").output == "fast"


def test_retry_policy_retries_only_declared_exception_and_then_succeeds():
    attempts = {"count": 0}

    def flaky(_):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient")
        return "recovered"

    task = ParallelTask(
        task_id="flaky", executor=flaky,
        retry_policy=RetryPolicy(max_attempts=3, retry_on=(RuntimeError,)),
    )
    batch = ParallelRunner().run([task])

    result = batch.by_id("flaky")
    assert result.status == TaskStatus.SUCCESS
    assert result.output == "recovered"
    assert result.attempts == 3


def test_retry_exhausted_produces_failed_not_infinite_retry():
    def always_fails(_):
        raise RuntimeError("permanent")

    task = ParallelTask(
        task_id="dead", executor=always_fails,
        retry_policy=RetryPolicy(max_attempts=2, retry_on=(RuntimeError,)),
    )
    batch = ParallelRunner().run([task])

    result = batch.by_id("dead")
    assert result.status == TaskStatus.FAILED
    assert result.attempts == 2
    assert "permanent" in result.error


def test_invalid_output_error_is_not_retried():
    attempts = {"count": 0}

    def bad_schema(_):
        attempts["count"] += 1
        raise _CustomInvalidError("schema mismatch")

    task = ParallelTask(
        task_id="schema", executor=bad_schema,
        retry_policy=RetryPolicy(max_attempts=5, retry_on=(RuntimeError,)),
        invalid_output_errors=(_CustomInvalidError,),
    )
    batch = ParallelRunner().run([task])

    result = batch.by_id("schema")
    assert result.status == TaskStatus.INVALID_OUTPUT
    assert attempts["count"] == 1  # invalid_output_errors는 재시도하지 않는다


def test_deterministic_error_not_in_retry_on_fails_immediately():
    def deterministic_bug(_):
        raise ValueError("boom")

    task = ParallelTask(
        task_id="bug", executor=deterministic_bug,
        retry_policy=RetryPolicy(max_attempts=3, retry_on=(RuntimeError,)),
    )
    batch = ParallelRunner().run([task])

    result = batch.by_id("bug")
    assert result.status == TaskStatus.FAILED
    assert result.attempts == 1


def test_partial_failure_returns_all_results_runner_does_not_decide_progress():
    def ok(_):
        return "ok"

    def fail(_):
        raise RuntimeError("nope")

    tasks = [
        ParallelTask(task_id="a", executor=ok),
        ParallelTask(task_id="b", executor=fail),
        ParallelTask(task_id="c", executor=ok),
    ]
    batch = ParallelRunner().run(tasks)

    assert len(batch.results) == 3
    assert batch.by_id("a").status == TaskStatus.SUCCESS
    assert batch.by_id("b").status == TaskStatus.FAILED
    assert batch.by_id("c").status == TaskStatus.SUCCESS
    assert batch.summary == {
        "PENDING": 0, "RUNNING": 0, "SUCCESS": 2, "TIMEOUT": 0, "FAILED": 1, "INVALID_OUTPUT": 0,
    }


def test_concurrent_tasks_do_not_share_mutable_state_across_isolation_boundary():
    """각 Task의 `input`이 서로 다른 dict를 참조하면 실행 도중 서로의 값을
    간섭하지 않아야 한다(concurrent task isolation)."""

    def mutate_and_return(payload):
        payload["seen"] = payload["id"]
        time.sleep(0.05)
        return payload["seen"]

    tasks = [
        ParallelTask(task_id=str(i), executor=mutate_and_return, input={"id": i})
        for i in range(10)
    ]
    batch = ParallelRunner(max_workers=10).run(tasks)

    for i in range(10):
        result = batch.by_id(str(i))
        assert result.status == TaskStatus.SUCCESS
        assert result.output == i
