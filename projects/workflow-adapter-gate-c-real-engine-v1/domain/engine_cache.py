"""Record-once-replay 캐시 — 실제 Engine 비결정성과 어댑터 정합성 검증을
분리하기 위한 장치. Reversibility 검증 자체가 아니다.

`hqs/development/mvp/engine.py::call_engine()`(ENGINE-CONNECT-0001)을
**read-only import**한다 — 이 파일도, `hqs/development/`·`hqs/investment/`
어느 것도 수정하지 않는다.

설계:
- 시나리오당 실제 Engine 호출은 `capture_once()`로 **정확히 1회**만
  발생한다. 그 뒤 4개 어댑터(sequential/worklist/recursive/langgraph)는
  모두 `get_captured()`로 **동일한 캡처값**을 읽는다 — "LLM이 매번 같은
  말을 하는가"가 아니라 "같은 값을 4개 어댑터가 동일하게 처리하는가"를
  묻기 위함.
- 실패 주입(`capture_exception_once`)도 동일 원칙 — 진짜 예외를 1회만
  발생시켜 캡처하고, 이후 재사용은 그 예외 인스턴스를 재발생시킨다
  (추가 실제 호출 없음).
- `counted_call_engine()`이 이 프로젝트 안에서 실제 Engine을 호출하는
  **유일한 경유 지점**이다 — 총 호출 횟수를 `real_call_count()`로
  계측해 예산(≤10회)을 테스트 스위트 자체가 assert한다.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from hqs.investment.engine_client import call_engine  # noqa: E402 — 유일한 실제 Engine 경유 지점, read-only

_CAPTURED_TEXT: dict[str, str] = {}
_CAPTURED_EXC: dict[str, BaseException] = {}
_REAL_CALL_COUNT = 0


def counted_call_engine(prompt: str) -> str:
    """실제 Engine 호출 총량을 계측하는, 이 프로젝트 안의 유일한 경유 지점."""
    global _REAL_CALL_COUNT
    _REAL_CALL_COUNT += 1
    return call_engine(prompt)


def capture_once(scenario: str, prompt: str) -> str:
    """시나리오당 정확히 1회만 실제 Engine을 호출해 캡처한다."""
    if scenario not in _CAPTURED_TEXT:
        _CAPTURED_TEXT[scenario] = counted_call_engine(prompt)
    return _CAPTURED_TEXT[scenario]


def get_captured(scenario: str) -> str:
    if scenario not in _CAPTURED_TEXT:
        raise RuntimeError(f"'{scenario}' 미캡처 — capture_once()가 선행돼야 한다")
    return _CAPTURED_TEXT[scenario]


def capture_exception_once(scenario: str, trigger: Callable[[], None]) -> BaseException:
    """`trigger()`를 실행해 실제로 발생하는 예외를 캡처한다(시나리오당 1회).

    `trigger`가 내부에서 `counted_call_engine`을 쓰면 진짜 실제 호출로
    카운트된다(예: 실제 timeout). `trigger`가 `call_engine`을 직접
    monkeypatch된 조건 하에 호출하면(예: RuntimeError 재현) 이 함수는
    그 사실을 통제하지 않는다 — 호출 카운트 여부는 호출부의 설계에 달림.
    """
    if scenario not in _CAPTURED_EXC:
        try:
            trigger()
        except BaseException as exc:  # noqa: BLE001 — 예외 캡처가 목적
            _CAPTURED_EXC[scenario] = exc
        else:
            raise AssertionError(f"'{scenario}': trigger()가 예외를 내지 않음 — 실패 주입 실패")
    return _CAPTURED_EXC[scenario]


def get_captured_exception(scenario: str) -> BaseException:
    if scenario not in _CAPTURED_EXC:
        raise RuntimeError(f"'{scenario}' 예외 미캡처 — capture_exception_once()가 선행돼야 한다")
    return _CAPTURED_EXC[scenario]


def real_call_count() -> int:
    return _REAL_CALL_COUNT


def reset() -> None:
    """테스트 격리용. 정상 스위트 실행 중에는 호출하지 않는다(캡처 재사용이 핵심)."""
    global _REAL_CALL_COUNT
    _CAPTURED_TEXT.clear()
    _CAPTURED_EXC.clear()
    _REAL_CALL_COUNT = 0
