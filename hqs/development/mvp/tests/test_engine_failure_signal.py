"""`_engine_failure_message()`/`is_engine_failure()` 왕복 검증 — 생산자와
판정자가 같은 접두사 소스(`mvp.workflow._ENGINE_FAILURE_PREFIX`)를 쓰는지
확인한다(Stage 05가 리터럴을 직접 중복 보유하지 않도록 하는 회귀 테스트)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.workflow import _engine_failure_message, is_engine_failure


def test_engine_failure_message_is_recognized_by_is_engine_failure():
    message = _engine_failure_message(RuntimeError("boom"))
    assert is_engine_failure(message) is True


def test_unrelated_text_is_not_engine_failure():
    assert is_engine_failure("CODE") is False
    assert is_engine_failure("") is False
