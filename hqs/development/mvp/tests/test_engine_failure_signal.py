"""`_engine_failure_message()`/`is_engine_failure()` 왕복 검증 — 생산자와
판정자가 같은 접두사 소스(`mvp.workflow._ENGINE_FAILURE_PREFIX`)를 쓰는지
확인한다(Stage 05가 리터럴을 직접 중복 보유하지 않도록 하는 회귀 테스트)."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.workflow import _engine_failure_message, is_engine_failure, run_mvp_0001


def test_engine_failure_message_is_recognized_by_is_engine_failure():
    message = _engine_failure_message(RuntimeError("boom"))
    assert is_engine_failure(message) is True


def test_unrelated_text_is_not_engine_failure():
    assert is_engine_failure("CODE") is False
    assert is_engine_failure("") is False


def test_subprocess_timeout_expired_is_recognized_as_engine_failure_end_to_end():
    """`call_engine()`의 유일한 경계인 `subprocess.run()`이
    `TimeoutExpired`를 던지는 실제 상황을 그 지점에서만 흉내내고, 그 위의
    어떤 계층도 patch하지 않는다 — Stage가 `except Exception`으로 잡아
    `_engine_failure_message()`로 감싼 결과가 `is_engine_failure()`에서
    True로 판정되는 실제 경로(`subprocess.TimeoutExpired` -> `call_engine()`
    -> `backend_agent_code_review()` -> `run_mvp_0001()`의 `except Exception`
    -> `is_engine_failure()`) 전체를 고정한다."""
    with patch(
        "mvp.engine.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["claude"], timeout=180),
    ):
        result = run_mvp_0001("def f(): pass")

    assert is_engine_failure(result["code_review"]) is True
    assert is_engine_failure(result["test_execution"]) is True
