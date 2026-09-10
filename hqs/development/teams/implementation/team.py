"""Implementation Team — 기존 Stage 04(Implementation) 책임을 그대로
수행한다(Stage → Team Migration, Kernel/Contract 변경 없음). `stages/
04_implementation/stage_04.py`(Backend Agent 재사용 포함, target
identification/dependency closure/exposure policy/implementation input
assembly/scope constraint는 기존 그대로 deterministic 처리)를 그대로
호출한다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_PATH = Path(__file__).resolve().parents[2] / "stages" / "04_implementation" / "stage_04.py"
_spec = importlib.util.spec_from_file_location("stage_04", _STAGE_PATH)
stage_04 = importlib.util.module_from_spec(_spec)
sys.modules["stage_04"] = stage_04
_spec.loader.exec_module(stage_04)


def run_implementation_team(stage_01_context: dict, stage_03_output: dict, expose_target: bool = False) -> dict:
    """Implementation Team 진입점 — 현재는 Stage 04 capability 호출로만
    구성된다. Coding/Test/Debugging/Refactoring Agent는 아직 도입하지
    않으며, 기존 deterministic 책임을 Agent로 이관하지 않는다."""
    return stage_04.run_stage_04(stage_01_context, stage_03_output, expose_target=expose_target)
