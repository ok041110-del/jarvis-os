"""Context Team — 기존 Stage 01(Context Analysis) 책임을 그대로 수행한다
(Stage → Team Migration, Kernel/Contract 변경 없음). `stages/01_context_analysis/
stage_01.py`의 결정적 capability를 재사용만 하고 재구현하지 않는다."""

import importlib.util
import sys
from pathlib import Path

_STAGE_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "stage_01.py"
_spec = importlib.util.spec_from_file_location("stage_01", _STAGE_PATH)
stage_01 = importlib.util.module_from_spec(_spec)
sys.modules["stage_01"] = stage_01
_spec.loader.exec_module(stage_01)


def run_context_team(issue: dict) -> dict:
    """Context Team 진입점 — 현재는 Stage 01 capability 호출로만 구성된다
    (기존 `workflow.py`와 동일하게 `target` 없이 호출). Intent/Requirement/
    Context Retrieval/Ambiguity Agent는 아직 도입하지 않는다(필요성이
    실제로 관찰되기 전까지 선행 구현하지 않음)."""
    return stage_01.run_stage_01(issue)
