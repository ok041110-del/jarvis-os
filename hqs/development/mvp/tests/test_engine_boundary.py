"""Multi-Engine Architecture(`docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`,
`docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md`)
경계 확인 — 정확히 세 Engine(ChatGPT/Claude Code/OpenRouter)만 존재하고,
각 호출부가 정확히 하나의 Engine 모듈을 참조하며, Central Router/
Gateway가 생기지 않았음을 정적으로 검증한다.

`ADR-0027` Migration으로 기존 ChatGPT-routed 호출부(Stage 01/02
Reasoning, Stage 03 Design, Stage 05 Review)와 requirements.py는
3번째 Engine(OpenRouter)으로 전환됐다 — `chatgpt_engine.py`/`engine.py`
자체는 무변경(Rollback 가능성 유지, `RFC-0041` §Rollback Strategy)."""

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MVP_DIR = REPO_ROOT / "hqs" / "development" / "mvp"
STAGES_DIR = REPO_ROOT / "hqs" / "development" / "stages"

CHATGPT_ENGINE_PY = MVP_DIR / "chatgpt_engine.py"
CLAUDE_CODE_ENGINE_PY = MVP_DIR / "engine.py"
OPENROUTER_ENGINE_PY = MVP_DIR / "openrouter_engine.py"

# Stage Mapping(`ADR-0027` Migration 이후) — 호출부 파일과 그 안에서
# 어떤 Engine 모듈을 import해야 하는지 고정한다. `backend.py`는 두
# Capability를 별도로 검사한다(아래
# test_backend_py_uses_openrouter_engine_for_both_capabilities).
OPENROUTER_ROUTED_FILES = [
    MVP_DIR / "agents" / "requirements.py",
    MVP_DIR / "agents" / "design.py",
    STAGES_DIR / "01_context_analysis" / "reasoning.py",
    STAGES_DIR / "02_planning_specification" / "task_dependency_agent.py",
]

# `workflow_ast_context.py`는 실제 Stage 01~05 파이프라인 호출부가
# 아니다(AST Context 유틸리티의 과거 예제 모듈, T18 Evidence 당시
# 스냅샷) — 이번 Migration 범위(RFC-0041 §Migration Scope) 밖이므로
# ChatGPT 라우팅을 그대로 유지한다.
CHATGPT_ROUTED_FILES = [
    MVP_DIR / "workflow_ast_context.py",
]

CLAUDE_CODE_ROUTED_FILES = [
    MVP_DIR / "agents" / "qa.py",
]


def test_openrouter_routed_files_import_openrouter_engine_only():
    for path in OPENROUTER_ROUTED_FILES:
        source = path.read_text(encoding="utf-8")
        assert "openrouter_engine" in source, f"{path}가 openrouter_engine을 import하지 않는다"
        assert "omniroute_engine" not in source, f"{path}가 여전히 omniroute_engine을 참조한다"
        assert "chatgpt_engine" not in source, f"{path}가 여전히 chatgpt_engine을 참조한다(Migration 미완료)"


def test_chatgpt_routed_files_import_chatgpt_engine_only():
    for path in CHATGPT_ROUTED_FILES:
        source = path.read_text(encoding="utf-8")
        assert "chatgpt_engine" in source, f"{path}가 chatgpt_engine을 import하지 않는다"
        assert "omniroute_engine" not in source, f"{path}가 여전히 omniroute_engine을 참조한다"


def test_claude_code_routed_files_import_engine_only():
    for path in CLAUDE_CODE_ROUTED_FILES:
        source = path.read_text(encoding="utf-8")
        assert "from ..engine import call_engine" in source or "from .engine import call_engine" in source, (
            f"{path}가 Claude Code Engine(engine.py)을 import하지 않는다"
        )
        assert "omniroute_engine" not in source, f"{path}가 여전히 omniroute_engine을 참조한다"


def test_backend_py_uses_openrouter_engine_for_both_capabilities():
    """`agents/backend.py`는 `code_review`/`code_generation` 둘 다
    `ADR-0027` Migration으로 3번째 Engine(OpenRouter)을 쓴다 — 두
    Capability가 서로 다른 함수 이름(`call_engine_review`/
    `call_engine_generation`)으로 남아있는 구조(`RFC-0036` §1.4가
    지적한 module-level 이름 공유 문제의 해소)는 그대로 유지된다."""
    source = (MVP_DIR / "agents" / "backend.py").read_text(encoding="utf-8")
    assert "from ..openrouter_engine import call_engine_via_openrouter as call_engine_review" in source
    assert "from ..openrouter_engine import call_engine_via_openrouter as call_engine_generation" in source
    assert "omniroute_engine" not in source
    assert "chatgpt_engine" not in source
    assert "from ..engine import" not in source


def test_no_provider_specific_function_names_in_stage_or_agent_code():
    """Stage/Agent 코드에 `call_chatgpt(...)`/`call_claude_code(...)`처럼
    Provider-specific 이름을 흩뿌리지 않는다(`ADR-0024` §Decision — 모든
    호출부는 `call_engine`/`call_engine_review`/`call_engine_generation`
    같은 목적 기반 이름만 쓴다) — 이 함수를 호출부에서 재정의하지 않는지
    확인한다."""
    forbidden = ("call_chatgpt", "call_claude_code", "call_openrouter")
    for path in [*OPENROUTER_ROUTED_FILES, *CHATGPT_ROUTED_FILES, *CLAUDE_CODE_ROUTED_FILES,
                 MVP_DIR / "agents" / "backend.py"]:
        source = path.read_text(encoding="utf-8")
        for term in forbidden:
            assert f"def {term}" not in source, f"{path}에 Provider-specific 함수 {term}가 정의됐다"


def test_no_central_router_or_gateway_module_created():
    """`IMPLEMENTATION_RULES.md` 15행(Engine Gateway 금지)이 Multi-Engine
    전환 이후에도 유지되는지 확인 — Router/Gateway 이름의 신규 모듈이
    `mvp/` 아래 생기지 않았다."""
    forbidden_names = {"engine_router.py", "engine_gateway.py", "router.py", "gateway.py"}
    existing = {p.name for p in MVP_DIR.glob("*.py")}
    assert existing.isdisjoint(forbidden_names), f"금지된 Router/Gateway 모듈 발견: {existing & forbidden_names}"


def test_chatgpt_engine_defines_exactly_one_public_function():
    tree = ast.parse(CHATGPT_ENGINE_PY.read_text(encoding="utf-8"))
    public_funcs = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert public_funcs == ["call_engine_via_chatgpt"]


_FOREIGN_ENGINE_MODULE_NAMES = (
    "engine", "mvp.engine", "omniroute_engine", "mvp.omniroute_engine",
    "chatgpt_engine", "mvp.chatgpt_engine", "openrouter_engine", "mvp.openrouter_engine",
)


def _assert_module_does_not_import_other_engines(engine_py: Path, own_names: tuple[str, ...]):
    """어떤 Engine 모듈도 다른 Engine 모듈을 import하지 않는지 확인한다
    (`ADR-0024` §Rollback이 요구하는 Reversibility 조건 — 3개로 늘어난
    지금도 그대로 지켜야 한다)."""
    tree = ast.parse(engine_py.read_text(encoding="utf-8"))
    forbidden = tuple(n for n in _FOREIGN_ENGINE_MODULE_NAMES if n not in own_names)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden, f"{engine_py}가 다른 Engine 모듈({node.module})을 import한다"
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden, f"{engine_py}가 다른 Engine 모듈({alias.name})을 import한다"


def test_chatgpt_engine_does_not_import_claude_code_or_omniroute_engine():
    _assert_module_does_not_import_other_engines(CHATGPT_ENGINE_PY, ("chatgpt_engine", "mvp.chatgpt_engine"))


def test_openrouter_engine_does_not_import_other_engine_modules():
    _assert_module_does_not_import_other_engines(OPENROUTER_ENGINE_PY, ("openrouter_engine", "mvp.openrouter_engine"))


def test_claude_code_engine_importable_standalone():
    import sys
    sys.path.insert(0, str(MVP_DIR.parent))
    from mvp.engine import call_engine  # noqa: F401


def test_chatgpt_engine_importable_standalone():
    import sys
    sys.path.insert(0, str(MVP_DIR.parent))
    from mvp.chatgpt_engine import call_engine_via_chatgpt  # noqa: F401


def test_openrouter_engine_importable_standalone():
    import sys
    sys.path.insert(0, str(MVP_DIR.parent))
    from mvp.openrouter_engine import call_engine_via_openrouter  # noqa: F401


def test_openrouter_engine_defines_exactly_one_public_function():
    """`call_engine_via_openrouter` 하나만 공개 — Free Pool 조회/Filter/
    Candidate Selection/Retry 헬퍼는 전부 `_`-prefixed 내부 함수다."""
    tree = ast.parse(OPENROUTER_ENGINE_PY.read_text(encoding="utf-8"))
    public_funcs = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert public_funcs == ["call_engine_via_openrouter"]


def test_no_api_key_hardcoded_in_any_engine_module():
    for path in (CHATGPT_ENGINE_PY, CLAUDE_CODE_ENGINE_PY, MVP_DIR / "omniroute_engine.py", OPENROUTER_ENGINE_PY):
        source = path.read_text(encoding="utf-8")
        assert "sk-" not in source
