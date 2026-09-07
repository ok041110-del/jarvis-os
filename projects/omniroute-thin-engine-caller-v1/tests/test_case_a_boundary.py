"""Thin Caller가 Case A 범위(`ADC-0031` §Q1)를 지키고, Jarvis 자체
Routing/Gateway/Policy 로직이 존재하지 않음을 정적으로 검증한다.

이 테스트는 동작이 아니라 **구조**를 검증한다 — `caller.py` 소스와
저장소 전체를 대상으로, 금지된 패턴이 없는지, production 경로에서
import되지 않는지를 확인한다.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
CALLER_PATH = PROJECT_DIR / "caller.py"


def _caller_source():
    return CALLER_PATH.read_text(encoding="utf-8")


def _caller_ast():
    return ast.parse(_caller_source(), filename=str(CALLER_PATH))


def test_caller_module_exists_and_is_single_file():
    # Thin Caller는 단일 파일/단일 호출 지점이다 — 여러 모듈로 분산된
    # "Adapter 계층"을 만들지 않는다.
    assert CALLER_PATH.is_file()
    module_files = [p for p in PROJECT_DIR.iterdir() if p.suffix == ".py"]
    assert module_files == [CALLER_PATH], (
        f"caller.py 외 다른 .py 모듈이 프로젝트 루트에 있다: {module_files}"
    )


def test_no_second_engine_target_hardcoded():
    # 다른 Engine(예: OpenAI 직접 호출, Claude API 직접 호출 등)을
    # 가리키는 두 번째 호출 대상이 없어야 한다 — 단일 Engine만 호출.
    source = _caller_source().lower()
    forbidden_hosts = [
        "api.anthropic.com",
        "api.openai.com",
        "generativelanguage.googleapis.com",
    ]
    for host in forbidden_hosts:
        assert host not in source, f"두 번째 Engine 대상으로 보이는 host 발견: {host}"


def test_no_provider_or_routing_selection_logic():
    # Provider/Model 선택·우선순위·fallback·재랭킹 로직이 없어야 한다.
    # DEFAULT_MODEL="auto" 같은 상수 지정은 "선택"이 아니라 OmniRoute에
    # 그대로 위임하는 값이므로 별도로 허용한다.
    tree = _caller_ast()
    forbidden_identifiers = {
        "provider_connections", "priority", "fallback_chain",
        "select_provider", "score_candidate", "rank_candidates",
        "routing_policy",
    }
    found_names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    found_attrs = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    overlap = forbidden_identifiers & (found_names | found_attrs)
    assert not overlap, f"금지된 Routing/Policy 식별자 발견: {overlap}"

    # 후보 목록을 비교·정렬하는 것으로 보이는 sort/sorted 호출이 없어야
    # 한다 — Provider/Model 후보 재랭킹은 OmniRoute의 책임이다.
    sort_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("sort",)
    ]
    sort_calls += [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "sorted"
    ]
    assert not sort_calls, "candidate 정렬로 해석될 수 있는 sort/sorted 호출 발견"


def test_no_generalized_adapter_or_gateway_class():
    # "여러 Engine을 갈아 끼울 수 있는" 일반화된 추상화(Base class +
    # 복수 구현체)가 없어야 한다 — 이 모듈의 클래스는 전부 단일 호출
    # 하나의 lifecycle/오류 표현에 그친다.
    tree = _caller_ast()
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    forbidden_name_fragments = ["gateway", "engineadapter", "enginebase", "engineinterface"]
    for name in class_names:
        lowered = name.lower()
        for fragment in forbidden_name_fragments:
            assert fragment not in lowered, f"금지된 추상화로 보이는 클래스명: {name}"

    # 클래스 정의가 상속하는 추상 기반 클래스(ABC 등)가 없어야 한다 —
    # 여러 구현체를 전제하는 인터페이스 패턴을 짓지 않는다는 뜻이다.
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = getattr(base, "id", getattr(base, "attr", ""))
                assert base_name not in ("ABC", "Protocol"), (
                    f"{node.name}이 추상 인터페이스({base_name})를 상속 — "
                    "Engine Gateway 패턴 위험"
                )


def test_module_defines_exactly_one_network_call_entrypoint():
    # 실제로 OmniRoute에 네트워크 요청을 보내는 지점은 conn.request()
    # 호출 한 곳뿐이어야 한다.
    tree = _caller_ast()
    request_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "request"
    ]
    assert len(request_calls) == 1, (
        f"conn.request() 호출 지점이 1개가 아니다: {len(request_calls)}개 발견"
    )


def test_engine_py_not_imported_or_referenced():
    # Development HQ의 단일 Engine 호출 함수(call_engine)를 이 모듈이
    # import하거나 호출하지 않는다 — 완전히 별개 경로다. docstring이
    # 설명 목적으로 그 이름을 인용하는 것은(§목적 문단) 실제 import/
    # 호출이 아니므로 AST 기준(Import/Call)으로만 검사한다.
    tree = _caller_ast()
    import_targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_targets.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_targets.append(node.module)
    assert not any("hqs" in target for target in import_targets), (
        f"hqs.* 모듈을 import하는 지점 발견: {import_targets}"
    )

    call_names = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "call_engine" not in call_names


def test_not_imported_from_hqs_production_paths():
    # `hqs/development/`·`hqs/investment/` 어떤 파일도 이 프로젝트를
    # import하지 않아야 한다(Experimental이 production path에 직접
    # 연결되지 않아야 한다 — ARCHITECTURE_GOVERNANCE.md).
    result = subprocess.run(
        [
            "grep", "-rl",
            "-e", "omniroute_thin_engine_caller",
            "-e", "omniroute-thin-engine-caller-v1",
            str(REPO_ROOT / "hqs"),
        ],
        capture_output=True, text=True,
    )
    matches = [line for line in result.stdout.splitlines() if line.strip()]
    assert matches == [], f"hqs/ 아래에서 이 프로젝트를 참조하는 파일 발견: {matches}"


def test_caller_module_is_importable_standalone(monkeypatch):
    # 외부 의존성 없이(stdlib only) import 가능해야 한다.
    monkeypatch.syspath_prepend(str(PROJECT_DIR))
    result = subprocess.run(
        [sys.executable, "-c", "import caller"],
        cwd=str(PROJECT_DIR), capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
