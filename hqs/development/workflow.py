"""01→05 Integrated Workflow — Stage 01~05(`stages/0N_*/stage_0N.py`)를
순서대로 호출·연결한다(ADR-0008 §4). Handover와 실행 순서/중단 관리만
담당하고, 각 Stage의 내부 로직은 복제하지 않는다.

Stage 폴더는 패키지가 아니므로(`__init__.py` 없음) `test_stage_0N.py`와
동일하게 `importlib`로 동적 로드한다.

`hqs/development/mvp/workflow.py`(MVP-0001, Task1→Task2 파이프라인)와는
다른 파일이며 그 파일을 수정하지 않는다.
"""

import importlib.util
import sys
from pathlib import Path

_STAGES_DIR = Path(__file__).resolve().parent / "stages"


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
    """Stage 01→05를 순서대로 실행하며 각 Output을 다음 Stage의 명시된
    Input으로 그대로 전달한다(재해석 없음):

    - Stage 01 Output -> Stage 02 Input
    - Stage 01 Output + Stage 02 Output -> Stage 03 Input
    - Stage 03 Output -> Stage 04 Input
    - Stage 02 Output + Stage 03 Output + Stage 04 Output -> Stage 05 Input

    중간 Stage가 예외를 던지면 즉시 중단하고 `failed_at`/`error`를
    채워 반환한다(이후 Stage 미호출). Stage 05 `verdict`는 그대로
    반환한다."""
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
