"""Stage 04: Implementation 실행 진입점 (Architecture Owner 승인,
ADR-0008 §4).

Stage 03의 Output(`run_stage_03()` 반환 dict)을 그대로 Input으로
받는다 — Stage 01~03을 다시 호출하지 않는다. 새 Agent/Capability를
추가하지 않고, ADC-0005 §8에서 이미 검증된 `workflow_ast_context.py`의
`identify_target`/`build_dependency_closure`/`module_source_path`/
`_EXPOSURE_POLICY_INSTRUCTION`과 `agents.backend_agent_code_generation`
을 재사용한다(`CAPABILITIES.md`). `workflow_ast_context.run_pipeline_
with_ast_context()`의 조립 순서를 그대로 재현하되, Planning/Design을
다시 만들지 않고 Stage 03의 `design`을 바로 사용한다는 점만 다르다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import backend_agent_code_generation
from mvp.ast_context import build_dependency_closure, module_source_path
from mvp.workflow import _engine_failure_message
from mvp.workflow_ast_context import _EXPOSURE_POLICY_INSTRUCTION, identify_target


def _assemble_build_input(design: str, target, expose_target: bool) -> str:
    """target 유무 + exposure 켬/끔 4가지 조합을 결정적으로 조립한다
    (Engine 호출 없음) — `run_pipeline_with_ast_context()`와 동일한
    조립 순서(ADC-0005 §7/§8)를 재현한다."""
    if target is None:
        return design

    module_name, function_name = target
    closure = build_dependency_closure(module_name, function_name)
    build_input = f"{design}\n\n---RELEVANT CODE (AST closure)---\n{closure}"

    if expose_target:
        target_source = module_source_path(module_name).read_text(encoding="utf-8")
        policy = _EXPOSURE_POLICY_INSTRUCTION.format(function_name=function_name)
        build_input = (
            f"{build_input}\n\n---TARGET FILE ({module_name}.py, full content)---\n"
            f"{target_source}\n\n---INSTRUCTION---\n{policy}"
        )

    return build_input


def run_stage_04(issue: dict, stage_03_output: dict, expose_target: bool = False) -> dict:
    """Target Identification -> Closure/Exposure 조립 -> Code Generation.

    `issue`는 현재 조립에 쓰이지 않지만, 다른 Stage 진입점과 동일한
    시그니처(issue를 첫 인자로)를 유지해 Stage 05/향후 workflow.py
    작성 시 호출 패턴을 통일한다."""
    design = stage_03_output["design"]

    try:
        target = identify_target(design)
        build_input = _assemble_build_input(design, target, expose_target)
        implementation = backend_agent_code_generation(build_input)
    except Exception as exc:
        return {
            "target": None,
            "implementation": _engine_failure_message(exc),
            "expose_target": expose_target,
        }

    return {
        "target": target,
        "implementation": implementation,
        "expose_target": expose_target,
    }
