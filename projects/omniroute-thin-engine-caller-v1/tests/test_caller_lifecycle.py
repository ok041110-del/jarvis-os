"""Adapter 수준 lifecycle(비동기 상태 조회·취소) 테스트.

로컬 test double만 사용한다 — 지연 응답으로 "아직 진행 중" 구간을
결정론적으로 만들어 취소 시점을 재현한다.
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import caller as omniroute_caller  # noqa: E402
from fake_server import FakeOmniRouteServer, success_body  # noqa: E402


def test_async_success_transitions_pending_to_succeeded():
    with FakeOmniRouteServer(status=200, body=success_body("비동기 성공")) as server:
        handle = omniroute_caller.call_omniroute_async(
            "hello", base_url=server.base_url, api_key="k",
        )
        assert handle.status() == "pending"
        result = handle.result(timeout=10)
    assert result == "비동기 성공"
    assert handle.status() == "succeeded"


def test_async_failure_transitions_to_failed():
    with FakeOmniRouteServer(status=401, body={"error": "bad key"}) as server:
        handle = omniroute_caller.call_omniroute_async(
            "hello", base_url=server.base_url, api_key="wrong",
        )
        with pytest.raises(omniroute_caller.OmniRouteAuthError):
            handle.result(timeout=10)
    assert handle.status() == "failed"


def test_cancel_before_completion_sets_cancelled_status():
    with FakeOmniRouteServer(status=200, delay_seconds=3.0) as server:
        handle = omniroute_caller.call_omniroute_async(
            "hello", base_url=server.base_url, api_key="k", timeout=10,
        )
        time.sleep(0.1)  # 요청이 실제로 전송될 시간을 준다
        assert handle.status() == "pending"

        cancelled = handle.cancel()

        assert cancelled is True
        assert handle.status() == "cancelled"
        with pytest.raises(omniroute_caller.OmniRouteCancelledError):
            handle.result(timeout=10)


def test_cancel_after_completion_returns_false():
    with FakeOmniRouteServer(status=200, body=success_body("이미 끝남")) as server:
        handle = omniroute_caller.call_omniroute_async(
            "hello", base_url=server.base_url, api_key="k",
        )
        handle.result(timeout=10)
        assert handle.status() == "succeeded"

        cancelled_again = handle.cancel()

    assert cancelled_again is False
    assert handle.status() == "succeeded"


def test_result_timeout_raises_without_cancelling_status():
    with FakeOmniRouteServer(status=200, delay_seconds=2.0) as server:
        handle = omniroute_caller.call_omniroute_async(
            "hello", base_url=server.base_url, api_key="k", timeout=10,
        )
        with pytest.raises(omniroute_caller.OmniRouteTimeoutError):
            handle.result(timeout=0.2)
        # result() 자체의 대기 시간 초과일 뿐 — 실제 호출은 계속 진행 중이어야 한다.
        assert handle.status() == "pending"
        handle.result(timeout=10)  # 정리: 실제 완료까지 기다려 스레드 누수 방지
