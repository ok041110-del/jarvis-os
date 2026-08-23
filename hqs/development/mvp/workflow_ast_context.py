"""ADC-0005 §8 — AST Context를 Build Capability에 최소 배선(기존 Workflow
무수정, 새 진입점 추가). `expose_target`은 자동 판별하지 않고 호출자가 명시적으로 지정한다(RFC-0007 Open Issues)."""

import re
from pathlib import PurePosixPath

from .agents.backend import backend_agent_code_generation
from .agents.design import design_agent_design
from .agents.requirements import requirements_agent_requirement_analysis
from .ast_context import build_dependency_closure, build_function_candidate_index, module_source_path
from .engine import call_engine
from .project_intelligence import collect_relevant_context
from .workflow import _engine_failure_message
from .workflow_project_intelligence import _enrich_issue

_IDENTIFY_INSTRUCTION = (
    "Below is a design description, followed by an index of candidate "
    "functions in the target repository (name, signature, and first line of "
    "docstring only — no function bodies). Identify exactly one file and one "
    "function from the index that this design is most likely about to "
    "implement or modify. Respond with exactly two lines, nothing else:\n"
    "FILE: <filename>\n"
    "FUNCTION: <function_name>\n"
    "If you cannot determine this with confidence, respond with:\n"
    "FILE: UNKNOWN\n"
    "FUNCTION: UNKNOWN"
)

_FILE_LINE_RE = re.compile(r"FILE:\s*(\S+)")
_FUNCTION_LINE_RE = re.compile(r"FUNCTION:\s*(\S+)")

_EXPOSURE_POLICY_INSTRUCTION = (
    "You are extending exactly one existing function, `{function_name}`, in "
    "the file below. Add code only inside that function's existing body — do "
    "not create a new function, and do not change any other function, "
    "import, or whitespace in this file for any reason. Return the complete "
    "file content with only that one change applied."
)


def identify_target(design: str):
    """AST 함수 후보 인덱스 + Design으로 시작점(module, function)을 식별
    (T17~T19 3/3 재현, `call_engine` 직접 호출)."""
    index = build_function_candidate_index()
    prompt = f"{_IDENTIFY_INSTRUCTION}\n\n---DESIGN---\n{design}\n\n---CANDIDATE INDEX---\n{index}"
    response = call_engine(prompt)

    file_match = _FILE_LINE_RE.search(response)
    function_match = _FUNCTION_LINE_RE.search(response)
    if not file_match or not function_match:
        return None

    file_name, function_name = file_match.group(1), function_match.group(1)
    if file_name == "UNKNOWN" or function_name == "UNKNOWN":
        return None

    # FILE이 저장소 상대 경로로 올 수 있어 basename만 쓴다.
    module_name = PurePosixPath(file_name).stem
    return module_name, function_name


def run_pipeline_with_ast_context(issue: dict, expose_target: bool = False) -> dict:
    """Planning -> Design -> (AST 시작점 식별 -> 폐쇄 [-> Exposure]) -> Build.
    Engine 실패 시 `workflow_0008.run_pipeline`과 동일한 형태로 흡수(RFC-0007 §5)."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
        design = design_agent_design(issue, requirement)

        target = identify_target(design)
        if target is None:
            build_input = design
        else:
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

        code = backend_agent_code_generation(build_input)
    except Exception as exc:
        error_message = _engine_failure_message(exc)
        return {
            "context": context,
            "planning": error_message,
            "design": error_message,
            "target": None,
            "implementation": error_message,
        }

    return {
        "context": context,
        "planning": requirement,
        "design": design,
        "target": target,
        "implementation": code,
    }
