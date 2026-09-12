"""Architecture Team — 기존 Stage 03(Architecture/Design) 책임을 그대로
수행한다(Stage → Team Migration, Kernel/Contract 변경 없음). `stages/
03_architecture_design/stage_03.py`(Design Agent 재사용 포함)를 그대로
호출한다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_PATH = Path(__file__).resolve().parents[2] / "stages" / "03_architecture_design" / "stage_03.py"
_spec = importlib.util.spec_from_file_location("stage_03", _STAGE_PATH)
stage_03 = importlib.util.module_from_spec(_spec)
sys.modules["stage_03"] = stage_03
_spec.loader.exec_module(stage_03)


def run_architecture_team(issue: dict, stage_01_context: dict, stage_02_output: dict) -> dict:
    """Architecture Team 진입점 — 현재는 Stage 03 capability 호출로만
    구성된다. Contract/Security/Trade-off Agent는 아직 도입하지 않는다."""
    return stage_03.run_stage_03(issue, stage_01_context, stage_02_output)
