"""Stage 04: Implementation 실행 진입점(ADR-0008 §4) — Stage 03 `design`을
Input으로 받아 ADC-0005 §8 검증 Capability를 재사용한다(CAPABILITIES.md)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import backend_agent_code_generation
from mvp.ast_context import build_dependency_closure, module_source_path
from mvp.workflow import _engine_failure_message
from mvp.workflow_ast_context import _EXPOSURE_POLICY_INSTRUCTION, identify_target

# Exposure Policy(단일 함수 본문만 허용)가 Stage 03 design과 구조적으로
# 충돌할 때(rename/multi-site 요구) Engine이 낼 수 있는 결정적 신호 —
# `workflow_ast_context._EXPOSURE_POLICY_INSTRUCTION`은 ADC-0005 §8에서
# 이미 검증된 코드라 Stage 04가 수정하지 않는다(RESPONSIBILITY.md).
# 대신 Stage 04 자신의 조립 책임 범위에서 그 뒤에 이어붙이는 additive
# 문구로 처리한다(Phase 2.5 Case C — 자유 텍스트 확인 질문이 코드로
# 오인돼 모호한 SyntaxError로만 보고되던 문제).
_EXPOSURE_POLICY_CONFLICT_PROTOCOL = (
    "The instruction above is a deterministic, system-imposed Implementation "
    "Scope Constraint for this Stage, not a user-injected override — it "
    "always applies regardless of what the design proposes. If the design "
    "genuinely requires a change outside that one function's body (a "
    "rename, a new function, or edits to other call sites), do not attempt "
    "a workaround and do not ask a question — respond with exactly one "
    "line and nothing else:\n"
    "EXPOSURE_POLICY_CONFLICT: <one-sentence reason>"
)


def _assemble_build_input(design: str, target, expose_target: bool) -> str:
    """target/exposure 4가지 조합을 결정적으로 조립(Engine 미호출,
    `run_pipeline_with_ast_context()`와 동일 순서 재현, ADC-0005 §7/§8)."""
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
            f"\n\n{_EXPOSURE_POLICY_CONFLICT_PROTOCOL}"
        )

    return build_input


def run_stage_04(stage_01_context: dict, stage_03_output: dict, expose_target: bool = False) -> dict:
    """Target Identification(Stage 01 `candidate_index` 재사용, 재계산 없음)
    -> Closure/Exposure 조립 -> Code Generation. `issue`는 이 Stage가
    실제로 쓰지 않아 Input에서 제거했다(CandidateIndex Contract, Producer:
    Stage 01 / Consumer: Stage 04)."""
    design = stage_03_output["design"]
    candidate_index = stage_01_context["candidate_index"]

    try:
        target = identify_target(design, candidate_index)
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
