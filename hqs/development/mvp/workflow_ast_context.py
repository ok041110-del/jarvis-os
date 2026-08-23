"""ADC-0005 §8 — AST Context를 Build Capability에 최소 배선한다.

기존 Workflow(`workflow_0008.py` 등)는 수정하지 않는다 — Frozen
순차 호출 구조를 그대로 두고, 새 진입점 하나를 추가하는 방식이다
(`workflow_project_intelligence.py`가 `run_issue_to_planning` 곁에
`run_issue_to_design`을 추가한 선례와 동일). `backend_agent_code_
generation(design: str) -> str` 시그니처는 변경하지 않는다 — Context는
입력 문자열에 concatenate하는 기존 패턴(RFC-0007 §2, §7)만 확장한다.

초기 적용 범위는 "기존 함수 1개 확장" Task로 제한한다(ADC-0005 §7 —
Target File Exposure 정책의 Evidence가 1개 Task뿐이라는 Risk를 반영).
"Design 출력에서 노출 여부/수정 의도를 자동 판별"하는 것은 검증된
적이 없으므로(RFC-0007 Open Issues), `expose_target`은 호출자가
명시적으로 지정한다 — T17~T19 Research와 동일한 방법론이다.
"""

import re
from pathlib import PurePosixPath

from .agents import backend_agent_code_generation, design_agent_design, requirements_agent_requirement_analysis
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
    """AST 함수 후보 인덱스 + Design으로 시작점(module, function)을
    식별한다(T17~T19에서 3/3 재현). 새 Capability로 등록하지 않는다 —
    T17~T19와 동일하게 `call_engine`을 직접 호출한다."""
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

    # 후보 인덱스는 FILE을 저장소 상대 경로(예: hqs/development/mvp/x.py)로
    # 표기한다 — Engine이 그 경로를 그대로 돌려줄 수 있으므로 basename만 쓴다.
    module_name = PurePosixPath(file_name).stem
    return module_name, function_name


def run_pipeline_with_ast_context(issue: dict, expose_target: bool = False) -> dict:
    """Planning -> Design -> (AST 시작점 식별 -> AST 폐쇄 [-> Target File
    노출 + Exposure 정책]) -> Build.

    Engine 호출 실패 시에도 `workflow_0008.run_pipeline`과 같은 형태로
    실패를 흡수한다(기존 예외 처리 경로 재사용, RFC-0007 §5)."""
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
