"""Context→Planning→Architecture→Implementation→Validation Team Workflow —
Team을 순서대로 호출·연결한다(ADR-0008 §4 Stage 순서·Handover 의미 유지,
Stage → Team Migration). `mvp/workflow.py`(MVP-0001)와는 다른 파일이며 그
파일을 수정하지 않는다.

각 Team은 `stages/0N_*/stage_0N.py`의 기존 capability를 그대로 호출한다
(재구현 없음, `hqs/development/teams/README.md` 참조). Handover와 함께, 각
Team Output이 `stages/contracts.py`가 정의한 필수 키를 갖췄는지 명시적으로
검증한다(계약 위반이 다음 Team으로 조용히 전파되지 않도록 함 — 값의
재해석은 하지 않고 키 존재만 확인)."""

import importlib.util
import sys
from pathlib import Path

_STAGES_DIR = Path(__file__).resolve().parent / "stages"
_TEAMS_DIR = Path(__file__).resolve().parent / "teams"


# Stage/Team 폴더는 패키지가 아니므로(`__init__.py` 없음) importlib로 동적 로드.
def _load_stage(folder: str, module_name: str):
    path = _STAGES_DIR / folder / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_team(folder: str, module_name: str):
    path = _TEAMS_DIR / folder / "team.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


context_team = _load_team("context", "context_team")
planning_team = _load_team("planning", "planning_team")
architecture_team = _load_team("architecture", "architecture_team")
implementation_team = _load_team("implementation", "implementation_team")
validation_team = _load_team("validation", "validation_team")

# 기존 화이트박스 테스트(`mvp/tests/test_workflow_integrated.py`)가
# `workflow.stage_0N.run_stage_0N`을 monkeypatch하므로, Team이 내부에서
# 로드한 것과 동일한 Stage 모듈 객체를 그대로 노출한다(Team 도입으로 Stage
# 재사용 capability의 정체성이 바뀌지 않았음을 보장).
stage_01 = context_team.stage_01
stage_02 = planning_team.stage_02
stage_03 = architecture_team.stage_03
stage_04 = implementation_team.stage_04
stage_05 = validation_team.stage_05
contracts = _load_stage("", "contracts")


def run_workflow(issue: dict, expose_target: bool = False) -> dict:
    """Stage 01→05를 순서대로 실행하며 Output을 다음 Stage Input으로 그대로
    전달한다(재해석 없음). 중간 Stage 예외 시 `failed_at`/`error`만 채워 즉시 반환."""
    result = {
        "stage_01": None,
        "stage_02": None,
        "stage_03": None,
        "stage_04": None,
        "stage_05": None,
        "failed_at": None,
        "error": None,
    }

    try:
        result["stage_01"] = context_team.run_context_team(issue)
        contracts.validate_context_analysis_result(result["stage_01"])
    except Exception as exc:
        result["failed_at"] = "stage_01"
        result["error"] = str(exc)
        return result

    try:
        result["stage_02"] = planning_team.run_planning_team(issue, result["stage_01"])
        contracts.validate_specification_result(result["stage_02"])
    except Exception as exc:
        result["failed_at"] = "stage_02"
        result["error"] = str(exc)
        return result

    try:
        result["stage_03"] = architecture_team.run_architecture_team(issue, result["stage_01"], result["stage_02"])
        contracts.validate_design_result(result["stage_03"])
    except Exception as exc:
        result["failed_at"] = "stage_03"
        result["error"] = str(exc)
        return result

    try:
        result["stage_04"] = implementation_team.run_implementation_team(
            result["stage_01"], result["stage_03"], expose_target=expose_target
        )
        contracts.validate_implementation_result(result["stage_04"])
    except Exception as exc:
        result["failed_at"] = "stage_04"
        result["error"] = str(exc)
        return result

    try:
        result["stage_05"] = validation_team.run_validation_team(result["stage_02"], result["stage_04"])
        contracts.validate_verification_result(result["stage_05"])
    except Exception as exc:
        result["failed_at"] = "stage_05"
        result["error"] = str(exc)
        return result

    return result
