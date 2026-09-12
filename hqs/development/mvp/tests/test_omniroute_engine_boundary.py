"""`omniroute_engine.py` 자신의 Case A(Thin Engine Caller) 경계를 정적으로
확인한다.

**Superseded 안내**: 이 파일은 원래 "5개(이후 7개) 기존 호출부 전부가
`omniroute_engine`을 예외 없이 import한다"는 RT-0001 Candidate 2
non-trigger 실증까지 담당했다. `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`가
Multi-Engine Architecture로 전환하면서 그 특정 불변조건(Engine 수=1)은
더 이상 성립하지 않는다 — 이 파일은 그 부분(호출부 전수 검사)을
`test_engine_boundary.py`로 이관하고, `omniroute_engine.py` 자신의
Case A 경계(단일 함수, Policy 로직 0줄, `engine.py`와 독립)만 계속
검증한다. OmniRoute는 `ADR-0024` §Non-goal에 따라 필수 실행 경로가
아닌 선택적 Adapter로 코드에 그대로 남아 있으므로, 이 경계 자체는
여전히 유효하다."""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MVP_DIR = REPO_ROOT / "hqs" / "development" / "mvp"
ENGINE_PY = MVP_DIR / "engine.py"
OMNIROUTE_ENGINE_PY = MVP_DIR / "omniroute_engine.py"


def test_engine_py_still_defines_only_call_engine():
    """`engine.py`(Claude Code Engine)가 `call_engine` 하나만 정의하고
    OmniRoute를 참조하지 않는다."""
    tree = ast.parse(ENGINE_PY.read_text(encoding="utf-8"))
    top_level_funcs = [
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    ]
    assert top_level_funcs == ["call_engine"]
    source = ENGINE_PY.read_text(encoding="utf-8")
    assert "omniroute" not in source.lower()
    assert "OMNIROUTE" not in source


def test_omniroute_engine_does_not_import_call_engine():
    tree = ast.parse(OMNIROUTE_ENGINE_PY.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module != "engine"
            assert node.module != "mvp.engine"
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in ("engine", "mvp.engine")


def test_no_provider_or_routing_selection_logic():
    """`caller.py`/`test_case_a_boundary.py`와 동일한 금지 식별자
    부재 확인 — provider 목록·priority·scoring·fallback을 코드
    (실행 가능한 statement)로 다루지 않는다."""
    tree = ast.parse(OMNIROUTE_ENGINE_PY.read_text(encoding="utf-8"))
    code_only_source = "\n".join(
        ast.unparse(node) for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.Call, ast.Compare, ast.If, ast.For))
    ).lower()
    forbidden_terms = [
        "provider_connections", "priority", "fallback_chain",
        "score", "candidates", "blockedproviders",
    ]
    for term in forbidden_terms:
        assert term not in code_only_source, f"금지 식별자 '{term}'가 코드에서 발견됐다"


def test_module_defines_exactly_one_network_call_entrypoint():
    tree = ast.parse(OMNIROUTE_ENGINE_PY.read_text(encoding="utf-8"))
    public_funcs = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert public_funcs == ["call_engine_via_omniroute"]


def test_omniroute_engine_importable_standalone():
    sys.path.insert(0, str(MVP_DIR.parent))
    from mvp.omniroute_engine import call_engine_via_omniroute  # noqa: F401
