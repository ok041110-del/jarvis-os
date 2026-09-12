"""Planning Team — 기존 Stage 02(Planning/Specification) 책임을 그대로
수행한다(Stage → Team Migration, Kernel/Contract 변경 없음). `stages/
02_planning_specification/stage_02.py`(Requirements Agent 재사용 포함)를
그대로 호출한다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_PATH = Path(__file__).resolve().parents[2] / "stages" / "02_planning_specification" / "stage_02.py"
_spec = importlib.util.spec_from_file_location("stage_02", _STAGE_PATH)
stage_02 = importlib.util.module_from_spec(_spec)
sys.modules["stage_02"] = stage_02
_spec.loader.exec_module(stage_02)


def run_planning_team(issue: dict, stage_01_context: dict) -> dict:
    """Planning Team 진입점 — 현재는 Stage 02 capability 호출로만 구성된다.
    Decomposition/Dependency/Risk Agent는 아직 도입하지 않는다."""
    return stage_02.run_stage_02(issue, stage_01_context)
