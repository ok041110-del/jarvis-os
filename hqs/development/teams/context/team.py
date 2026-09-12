"""Context Team — Stage 01(Context Analysis) 책임을 수행한다(Stage → Team
Migration + Multi-Agent Reasoning 도입, RFC-0033/ADC-0036/ADR-0021).

`run_context_team()`은 신규 Multi-Agent 진입점(`stage_01_multi_agent.py`)을
호출한다 — Intent/Goal/Requirement/Ambiguity Agent Reasoning이 먼저 전체
완료된 뒤, GitHub Repository 기준 Code Analysis(Structure/Relevant
Discovery/AST Candidate, 병렬)로 이어진다. 기존 결정적 `stage_01.py`는
무변경으로 남겨 `mvp/tests/test_stage_01.py`가 계속 그 경로를 직접
검증한다 — `stage_01` 속성으로 계속 노출해 하위 호환을 유지한다."""

import importlib.util
import sys
from pathlib import Path

_TEAM_DIR = Path(__file__).resolve().parent
_STAGE_DIR = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis"


def _load(folder: Path, module_name: str, filename: str):
    path = folder / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


stage_01 = _load(_STAGE_DIR, "stage_01", "stage_01.py")
stage_01_multi_agent = _load(_STAGE_DIR, "stage_01_multi_agent", "stage_01_multi_agent.py")


def run_context_team(issue: dict) -> dict:
    """Context Team 진입점 — Multi-Agent Reasoning + GitHub 기반 Code
    Analysis로 Stage 01 Output(기존 5-key Contract, 무변경)을 만든다."""
    return stage_01_multi_agent.run_stage_01_multi_agent(issue)
