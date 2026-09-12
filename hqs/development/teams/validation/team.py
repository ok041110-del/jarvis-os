"""Validation Team — 기존 Stage 05(Validation) 책임을 그대로 수행한다
(Stage → Team Migration, Kernel/Contract 변경 없음). `stages/05_validation/
stage_05.py`(Backend Agent code_review 재사용 포함, PASS/FAIL/PARTIAL
결정적 판정 로직 포함)를 그대로 호출한다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_PATH = Path(__file__).resolve().parents[2] / "stages" / "05_validation" / "stage_05.py"
_spec = importlib.util.spec_from_file_location("stage_05", _STAGE_PATH)
stage_05 = importlib.util.module_from_spec(_spec)
sys.modules["stage_05"] = stage_05
_spec.loader.exec_module(stage_05)


def run_validation_team(stage_02_output: dict, stage_04_output: dict) -> dict:
    """Validation Team 진입점 — 현재는 Stage 05 capability 호출로만
    구성된다(기존 `workflow.py`와 동일하게 `required_checks` 없이 호출,
    Stage 05 기본값 4개 전체 사용). PASS/FAIL/PARTIAL 판정 로직은 LLM
    Agent 판단으로 바꾸지 않는다(기존 결정적 판정 그대로 유지)."""
    return stage_05.run_stage_05(stage_02_output, stage_04_output)
