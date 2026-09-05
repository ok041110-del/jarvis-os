"""호출자 역할 (HQ 자리). adapter 모듈을 인자로 받으며 adapter 종류를 모른다.

caller-owned checkpoint: adapter는 값을 '생산'만 하고, 그 값의 영속화·복원은
caller의 몫이다(BASELINE §15.2·§16.6 A-IN(e), ADC-0020 §Q-D (a)).

이 모듈은 adapters를 import하지 않는다 — 어댑터 교체 시 이 파일은 바이트
단위로 불변이며, 교체점은 `adapter` 인자 한 곳이다(ADC-0021 §D4).
"""
from __future__ import annotations

import copy
import json


def run_full(adapter, inputs: dict) -> dict:
    return adapter.run_full(copy.deepcopy(inputs))


def phase1_and_save(adapter, inputs: dict, checkpoint_path: str) -> dict:
    value = adapter.run_phase1(copy.deepcopy(inputs))
    with open(checkpoint_path, "w", encoding="utf-8") as handle:  # 영속화는 caller의 몫
        json.dump(value, handle)
    return value


def load_and_phase2(adapter, checkpoint_path: str) -> dict:
    with open(checkpoint_path, encoding="utf-8") as handle:
        restored = json.load(handle)
    return adapter.run_phase2(restored)
