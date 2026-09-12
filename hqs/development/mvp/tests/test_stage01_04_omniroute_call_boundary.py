"""Stage 01~04 OmniRoute Thin Caller 통합 — Call Boundary Verification.

투자 조사 결과, Stage 01~04의 모든 Production Engine 호출 지점은 이미
`mvp/omniroute_engine.py::call_engine_via_omniroute`로 연결돼 있었다
(`agents/backend.py`·`agents/design.py`·`agents/qa.py`·
`agents/requirements.py`·`workflow_ast_context.py`는 EVIDENCE-0013에서,
`reasoning.py`·`task_dependency_agent.py`는 각각 작성 당시부터). 이
파일은 그 사실을 코드 읽기가 아니라 **실행 가능한 identity 검사**로
고정한다 — 각 모듈의 `call_engine` 이름이 정확히 같은 함수 객체를
가리키는지 확인해, 향후 누군가 로컬 alias를 다른 구현으로 바꾸면 이
테스트가 즉시 깨지게 한다."""

import importlib.util
import sys
from pathlib import Path

_DEV_DIR = Path(__file__).resolve().parents[2]
_STAGE_DIR = _DEV_DIR / "stages"

sys.path.insert(0, str(_DEV_DIR))

from mvp import omniroute_engine  # noqa: E402
from mvp.agents import backend, design, qa, requirements  # noqa: E402
from mvp import workflow_ast_context  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reasoning = _load(
    "omniroute_boundary_reasoning", _STAGE_DIR / "01_context_analysis" / "reasoning.py"
)
task_dependency_agent = _load(
    "omniroute_boundary_task_dependency_agent",
    _STAGE_DIR / "02_planning_specification" / "task_dependency_agent.py",
)

_MODULES_UNDER_TEST = {
    "agents.backend (Stage 04 Code Generation)": backend,
    "agents.design (Stage 03 Design)": design,
    "agents.qa (QA Agent)": qa,
    "agents.requirements (Stage 01 PRD Synthesis)": requirements,
    "workflow_ast_context (Stage 04 Target Identification)": workflow_ast_context,
    "stage01 reasoning.py (Stage 01 Multi-Agent Reasoning)": reasoning,
    "stage02 task_dependency_agent.py (Stage 02 Task & Dependency Agent)": task_dependency_agent,
}


def test_every_stage_01_to_04_call_site_is_bound_to_omniroute_thin_caller():
    for label, module in _MODULES_UNDER_TEST.items():
        assert hasattr(module, "call_engine"), f"{label} has no call_engine name"
        assert module.call_engine is omniroute_engine.call_engine_via_omniroute, (
            f"{label}'s call_engine is not omniroute_engine.call_engine_via_omniroute"
        )


def test_omniroute_thin_caller_contract_is_a_plain_str_to_str_function():
    """§2 "기존 Stage가 알고 있는 것은 계속 call_engine이어야 한다" —
    Thin Caller가 여전히 `str -> str` 계약만 노출하는지(신규 파라미터로
    Contract를 넓히지 않았는지) 시그니처로 확인한다."""
    import inspect

    signature = inspect.signature(omniroute_engine.call_engine_via_omniroute)
    assert list(signature.parameters) == ["prompt"]


def test_no_production_call_site_imports_raw_engine_module():
    """`mvp/engine.py`(레거시)가 Stage 01~04 Production 경로 어디에서도
    직접 import되지 않는지 확인한다 — 있다면 OmniRoute를 우회하는
    지점이다."""
    production_files = [
        _DEV_DIR / "mvp" / "agents" / "backend.py",
        _DEV_DIR / "mvp" / "agents" / "design.py",
        _DEV_DIR / "mvp" / "agents" / "qa.py",
        _DEV_DIR / "mvp" / "agents" / "requirements.py",
        _DEV_DIR / "mvp" / "workflow_ast_context.py",
        _STAGE_DIR / "01_context_analysis" / "reasoning.py",
        _STAGE_DIR / "01_context_analysis" / "prd_synthesis.py",
        _STAGE_DIR / "01_context_analysis" / "code_analysis.py",
        _STAGE_DIR / "02_planning_specification" / "task_dependency_agent.py",
        _STAGE_DIR / "02_planning_specification" / "planning_pipeline.py",
        _STAGE_DIR / "02_planning_specification" / "stage_02.py",
        _STAGE_DIR / "03_architecture_design" / "stage_03.py",
        _STAGE_DIR / "04_implementation" / "stage_04.py",
    ]
    for path in production_files:
        text = path.read_text(encoding="utf-8")
        assert "from ..engine import" not in text, f"{path} imports raw engine.py directly"
        assert "from mvp.engine import" not in text, f"{path} imports raw engine.py directly"
        assert "from .engine import" not in text, f"{path} imports raw engine.py directly"
