"""`omniroute_engine.py`가 Case A(Thin Engine Caller) 경계를 지키고,
`engine.py::call_engine()`(RT-0001 Candidate 2의 대상) 자체는 전혀
수정되지 않았음을 정적으로 확인한다 — Experimental Thin Caller
프로토타입(`projects/` 아래)의 동명 boundary 테스트와 같은 목적을
실제 production 모듈(`hqs/development/mvp/`)에 대해 수행한다.

`docs/architecture/core/EVIDENCE-0013-call-site-conversion-governance-final-review.md`
§5·§10의 Governance PASS 조건에 따라 5개 기존 호출부 전부가
`call_engine_via_omniroute`로 **동기화 전환**됐다(부분 전환 아님).
이 파일의 RT-0001 관련 검사는 그 전환 이후 상태를 검증한다 —
"`call_engine()`이 5개 호출부 중 어디에서도 더 이상 import되지
않는다(호출 지점 0개 = Engine 교체, 추가 아님)"와 "5개 전부가
예외 없이 `omniroute_engine`을 import한다(부분 전환 배제)"를 함께
확인해야 RT-0001 Candidate 2 Trigger("두 번째 Engine이 실제로
추가되어 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로 하게
됨")가 성립하지 않음을 실증할 수 있다(`EVIDENCE-0013` §5.1·§5.2)."""

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MVP_DIR = REPO_ROOT / "hqs" / "development" / "mvp"
ENGINE_PY = MVP_DIR / "engine.py"
OMNIROUTE_ENGINE_PY = MVP_DIR / "omniroute_engine.py"

# `call_engine()`의 기존(변경 전) 호출 지점 전체 — RT-0001 Candidate 2가
# "call_engine() 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로
# 하게 됨"으로 좁힌 그 대상들이다.
EXISTING_CALL_ENGINE_CALL_SITES = [
    MVP_DIR / "agents" / "backend.py",
    MVP_DIR / "agents" / "design.py",
    MVP_DIR / "agents" / "qa.py",
    MVP_DIR / "agents" / "requirements.py",
    MVP_DIR / "workflow_ast_context.py",
]


def test_engine_py_still_defines_only_call_engine():
    """`engine.py`가 이번 Integration으로 수정되지 않았음을 구조로
    재확인한다 — `call_engine` 하나만 정의하고 OmniRoute를 참조하지
    않는다."""
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


def test_no_existing_call_site_imports_engine_call_engine():
    """RT-0001 Candidate 2 non-trigger의 핵심 증거(전환 후) —
    `engine.py::call_engine`은 5개 기존 호출부 중 어디에서도 더 이상
    import되지 않는다(호출 지점 0개). Trigger 원문("호출 지점이
    둘 이상의 서로 다른 Engine을 대상으로 하게 됨")은 애초에 대상
    호출 지점이 0개이므로 성립할 수 없다 — 이것은 Engine이 추가된
    것이 아니라 교체된 것이다(`EVIDENCE-0013` §5.1)."""
    tree_by_path = {
        path: ast.parse(path.read_text(encoding="utf-8"))
        for path in EXISTING_CALL_ENGINE_CALL_SITES
    }
    for path, tree in tree_by_path.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in ("engine", "mvp.engine", ".engine"):
                names = {alias.name for alias in node.names}
                assert "call_engine" not in names, (
                    f"{path}가 여전히 engine.py::call_engine을 import한다"
                )


def test_all_five_existing_call_sites_import_omniroute_engine():
    """`EVIDENCE-0013` §5.2(부분 전환 금지) 준수 확인 — 5개 기존
    호출부 **전부**가 예외 없이 `omniroute_engine`을 import해야 한다.
    하나라도 빠지면 Claude CLI/OmniRoute 두 Engine이 production
    파이프라인에 동시에 실재하게 되어 RT-0001 Candidate 2 Trigger의
    취지("Engine 수 ≥2")를 충족시킬 위험이 생긴다 — 동기화된 전부
    전환만 이 Governance PASS의 적용 대상이다."""
    for path in EXISTING_CALL_ENGINE_CALL_SITES:
        source = path.read_text(encoding="utf-8")
        assert "omniroute_engine" in source, (
            f"{path}가 omniroute_engine을 import하지 않는다 — 부분 전환 상태로 의심된다"
        )


def test_production_call_site_import_count_matches_synchronized_conversion():
    """`--include=*.py`로 `.py` 소스만 검색한다 — Python 3.10+ venv처럼
    `sys.pycache_prefix`가 소스 트리 밖으로 우회되지 않는 표준
    인터프리터는 `__pycache__/*.pyc` 파일명에도 "omniroute_engine"이
    포함되어(예: `omniroute_engine.cpython-312.pyc`) 컴파일 캐시가
    소스 참조로 오검출되기 때문이다(`EVIDENCE-0010` §4).

    `hqs/development/mvp/` 전체에서 `omniroute_engine`을 참조하는
    파일이, 모듈 자신·이 테스트 파일들·5개 기존 호출부 외에는
    없어야 한다 — 전환 범위가 정확히 5개로 동기화됐음을 확인한다."""
    result = subprocess.run(
        ["grep", "-rl", "--include=*.py", "omniroute_engine", str(MVP_DIR)],
        capture_output=True, text=True,
    )
    expected_names = {
        "omniroute_engine.py", "test_omniroute_engine.py",
        "test_omniroute_engine_boundary.py", "test_omniroute_engine_real.py",
        "backend.py", "design.py", "qa.py", "requirements.py",
        "workflow_ast_context.py",
        # 전환 후 실제 의존 관계를 검증하는 테스트(문자열로 "omniroute_engine"을
        # 언급) — production 참조가 아니라 그 참조를 검증하는 테스트 자체다.
        "test_ast_context.py",
        # Stage 01~04 OmniRoute 통합 Call Boundary Verification — 5개
        # 호출부 + Stage 01/02 신규 모듈(reasoning.py/task_dependency_agent.py)
        # 전부가 실제로 이 모듈을 가리키는지 identity로 검사하는 테스트.
        "test_stage01_04_omniroute_call_boundary.py",
    }
    matches = [
        line for line in result.stdout.splitlines()
        if Path(line).name not in expected_names
    ]
    assert matches == [], f"omniroute_engine을 참조하는 예상 밖 파일: {matches}"


def test_no_provider_or_routing_selection_logic():
    """`caller.py`/`test_case_a_boundary.py`와 동일한 금지 식별자
    부재 확인 — provider 목록·priority·scoring·fallback을 코드
    (실행 가능한 statement)로 다루지 않는다. docstring 안에서
    "운영자가 OmniRoute 쪽에 blockedProviders를 설정해야 한다"는
    안내 문장(코드가 아니라 Policy 소재를 명시하는 설명, `ADR-0017`
    §2.3)은 이 검사 대상이 아니다 — 그래서 코드 statement만 검사한다."""
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
