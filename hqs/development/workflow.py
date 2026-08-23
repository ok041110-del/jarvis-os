"""01→05 Integrated Workflow — Stage 01~05를 순서대로 호출·연결한다(ADR-0008
§4). `mvp/workflow.py`(MVP-0001)와는 다른 파일이며 그 파일을 수정하지 않는다."""

import importlib.util
import sys
from pathlib import Path

_STAGES_DIR = Path(__file__).resolve().parent / "stages"


# Stage 폴더는 패키지가 아니므로(`__init__.py` 없음) importlib로 동적 로드.
def _load_stage(folder: str, module_name: str):
    path = _STAGES_DIR / folder / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


stage_01 = _load_stage("01_context_analysis", "stage_01")
stage_02 = _load_stage("02_planning_specification", "stage_02")
stage_03 = _load_stage("03_architecture_design", "stage_03")
stage_04 = _load_stage("04_implementation", "stage_04")
stage_05 = _load_stage("05_validation", "stage_05")


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
        result["stage_01"] = stage_01.run_stage_01(issue)
    except Exception as exc:
        result["failed_at"] = "stage_01"
        result["error"] = str(exc)
        return result

    try:
        result["stage_02"] = stage_02.run_stage_02(issue, result["stage_01"])
    except Exception as exc:
        result["failed_at"] = "stage_02"
        result["error"] = str(exc)
        return result

    try:
        result["stage_03"] = stage_03.run_stage_03(issue, result["stage_01"], result["stage_02"])
    except Exception as exc:
        result["failed_at"] = "stage_03"
        result["error"] = str(exc)
        return result

    try:
        result["stage_04"] = stage_04.run_stage_04(issue, result["stage_03"], expose_target=expose_target)
    except Exception as exc:
        result["failed_at"] = "stage_04"
        result["error"] = str(exc)
        return result

    try:
        result["stage_05"] = stage_05.run_stage_05(
            issue, result["stage_02"], result["stage_03"], result["stage_04"]
        )
    except Exception as exc:
        result["failed_at"] = "stage_05"
        result["error"] = str(exc)
        return result

    return result
