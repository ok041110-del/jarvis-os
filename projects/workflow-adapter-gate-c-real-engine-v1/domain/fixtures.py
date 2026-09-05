"""시나리오 fixture — Gate C(i) 실험 전용.

- clean / data_gap: `analyst_sentiment` 한 노드만 실제 Engine 호출(engine_cache
  경유)로 대체된다. 조건부 분기(conflict 여부)는 여전히 이 설정이 결정한다 —
  업무 분기(control flow)의 재현성을 유지하기 위함이며, 실제 Engine 텍스트는
  State 값(`engine_note`)으로만 실려 파이프라인(merge/checkpoint/어댑터
  교체)을 관통한다.
- engine_error_real_timeout / engine_error_runtime: `analyst_sentiment`가
  engine_cache에 미리 캡처된 **실제** 예외(진짜 timeout 1회 시도로 얻은
  `subprocess.TimeoutExpired`, 또는 `call_engine()`의 실제 코드 경로를
  합성 조건으로 재현한 `RuntimeError`)를 재발생시킨다 — catch-and-encode
  검증용. E4/E5/E6의 `node_error`(fixture가 직접 raise)와 달리, 여기서는
  raise되는 예외 자체가 진짜 Engine 실행 결과다.
"""
from __future__ import annotations

SCENARIOS = {
    "clean": {"ticker": "TESTCO", "sentiment_conflict": False, "engine_mode": "real"},
    "data_gap": {"ticker": "TESTCO", "sentiment_conflict": True, "engine_mode": "real"},
    "engine_error_real_timeout": {"ticker": "TESTCO", "sentiment_conflict": False, "engine_mode": "raise"},
    "engine_error_runtime": {"ticker": "TESTCO", "sentiment_conflict": False, "engine_mode": "raise"},
}


def scenario_config(name: str) -> dict:
    return SCENARIOS[name]
