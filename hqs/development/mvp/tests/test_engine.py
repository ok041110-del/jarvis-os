"""`call_engine()` 실패 전파 회귀 테스트 — subprocess의 returncode/stderr가
유실되지 않고 예외로 전파되는지 검증(정상 경로의 반환 계약은 그대로)."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp.engine import call_engine


def _completed_process(returncode, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=["claude"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def test_success_returns_stdout():
    with patch("mvp.engine.subprocess.run", return_value=_completed_process(0, stdout="ok")):
        assert call_engine("prompt") == "ok"


def test_nonzero_returncode_raises_with_returncode_and_stderr():
    with patch(
        "mvp.engine.subprocess.run",
        return_value=_completed_process(1, stdout="", stderr="auth error"),
    ):
        with pytest.raises(Exception) as exc_info:
            call_engine("prompt")

    message = str(exc_info.value)
    assert "1" in message
    assert "auth error" in message


def test_timeout_still_propagates():
    with patch(
        "mvp.engine.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["claude"], timeout=180),
    ):
        with pytest.raises(subprocess.TimeoutExpired):
            call_engine("prompt")
