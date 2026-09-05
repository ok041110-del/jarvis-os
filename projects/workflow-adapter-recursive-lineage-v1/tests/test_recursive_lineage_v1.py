"""L-B (Gate B 완전 완화 후속조건 (i) / `ADC-0024` §D-B4) — 재귀 조합자
독립 계보 검증 — IN-1' ~ IN-6'.

검증 대상 = §16.6 A-IN 5항목(State·Node·Conditional Edge·Loop·값 기반
Checkpoint/Resume) + Reversibility 필수 불변조건이, L-A(worklist)와도
LangGraph와도 다른 두 번째 독립 실행 계보(L-B = 재귀 조합자)에서도
성립하는가. LangGraph(L-LG)는 동치 대조로 유지한다.

IN-6'은 E5 IN-6(정적 import 검사만)의 기계적 복제가 아니다 — 자료구조
부재(클래스/큐 없음)와 실행 메커니즘 자체(재귀 vs 반복)를 정적 검사 +
런타임 계측으로 실증한다(승인된 Test Design §2 IN-6'-1/2/3).

범위 밖(mid-node resume, 성능, 실제 엔진, Public Port, Q-E-2, (c) 규범화,
Gate B/C 판정 선언)은 assert하지 않는다 — E4/E5 Test Design 계승.
"""
from __future__ import annotations

import ast
import copy
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import caller  # noqa: E402
from adapters import langgraph as lg_adapter  # noqa: E402
from adapters import recursive as rc_adapter  # noqa: E402
from domain.state import json_roundtrip_ok, new_state, only_plain_types  # noqa: E402

SCENARIOS = ["clean", "data_gap", "node_error"]
RESUME_SCENARIOS = ["clean", "data_gap"]
ADAPTERS = {"recursive": rc_adapter, "langgraph": lg_adapter}
REPO = ROOT.parent.parent
KERNEL_HQ_FILES = [
    "caller.py",
    "domain/state.py",
    "domain/nodes.py",
    "domain/fixtures.py",
    "domain/graph_spec.py",
]
# sibling Experimental 프로젝트(E5) — 있으면 대조에 쓰고, 없으면(폐기됐으면) 스킵한다.
# import는 하지 않는다(런타임 결합 없음) — 소스 텍스트만 읽어 정적 대조한다.
SIBLING_WORKLIST = REPO / "projects" / "workflow-adapter-nonlanggraph-lineage-v1" / "adapters" / "worklist.py"


def _inputs(scenario: str) -> dict:
    return new_state("TESTCO", scenario)


def _imports(src: str, module_prefix: str) -> bool:
    return (
        f"import {module_prefix}" in src
        or f"from {module_prefix}" in src
        or f"import_module('{module_prefix}" in src
        or f'import_module("{module_prefix}' in src
    )


def _import_roots(src: str) -> set[str]:
    tree = ast.parse(src)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            roots.add((node.module or "").split(".")[0])
    return roots


def _defines_self_recursive_function(src: str, func_name: str) -> bool:
    """`func_name` 함수 정의의 바디 안에 자기 자신을 호출하는 Call 노드가 있는가."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == func_name:
                    return True
    return False


# ---------------------------------------------------------------- IN-1'
# A-IN (a)(b)(c)(d) + State 동치: 독립 계보(recursive)의 최종 State가
# LangGraph 계보와 dict deep-equal.
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN1p_final_state_equivalence_recursive_vs_langgraph(scenario):
    rc_state = caller.run_full(rc_adapter, _inputs(scenario))
    lg_state = caller.run_full(lg_adapter, _inputs(scenario))
    assert rc_state == lg_state


@pytest.mark.parametrize(
    "scenario,expected_outcome",
    [("clean", "COMPLETED"), ("data_gap", "ESCALATED_DATA_GAP"), ("node_error", "COMPLETED")],
)
def test_IN1p_recursive_actually_walks_conditional_and_loop(scenario, expected_outcome):
    """동치 검증의 전제 — recursive 계보가 실제로 Conditional 분기·수렴 Loop를 밟는지."""
    state = caller.run_full(rc_adapter, _inputs(scenario))
    assert state["outcome"] == expected_outcome
    # A-IN(d) Loop: 토론 본문이 정확히 3회 반복
    assert [x for x in state["debate_log"] if x.startswith("BULL")] == ["BULL r0", "BULL r1", "BULL r2"]
    assert state["debate_round"] == 3
    if scenario == "data_gap":
        # A-IN(c) 조건부 분기: route_after_decision -> escalate
        assert any(str(f).startswith("INCONSISTENT") for f in state["data_flags"])
        assert state["decision"]["action"] == "HOLD"
        assert "escalation" in state and "final_report" not in state
    if scenario == "clean":
        # A-IN(c) 조건부 분기: route_after_decision -> report
        assert "final_report" in state and "escalation" not in state
    if scenario == "node_error":
        assert any(str(f).startswith("NODE_ERROR:analyst_fundamental") for f in state["data_flags"])
        assert "fundamental" not in state


# ---------------------------------------------------------------- IN-2'
# 실행 결과의 값 표현 — 예외 비전파. 재귀 구조는 예외가 상위 프레임으로
# 새기 쉬운 구조이므로, 매 프레임(각 _advance 호출)에서 catch됨을 확인한다.
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN2p_result_as_value_no_exception(adapter_name, scenario):
    adapter = ADAPTERS[adapter_name]
    try:
        state = caller.run_full(adapter, _inputs(scenario))
        state_p1 = adapter.run_phase1(_inputs(scenario))
        adapter.run_phase2(state_p1)
    except Exception as exc:  # noqa: BLE001 — 경계 밖 예외 전파 = 실패
        pytest.fail(f"{adapter_name}/{scenario}: 예외가 어댑터 경계 밖으로 전파됨: {exc!r}")
    assert state["outcome"] in {"COMPLETED", "ESCALATED_DATA_GAP"}
    if scenario == "node_error":
        assert any(str(f).startswith("NODE_ERROR:") for f in state["data_flags"])


# ---------------------------------------------------------------- IN-3'
# A-IN(e) 값 기반 Checkpoint/Resume — caller-owned, 별도 프로세스 재개.
# recursive 계보는 "이전 재귀 호출 스택을 복원하지 않고 완전히 새 재귀로
# 재개한다"는 것이 검증 포인트다 — checkpoint 값 자체에 visited/frozenset
# 등 실행기 내부 상태가 전혀 없어야 한다(순수 도메인 State만).
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
@pytest.mark.parametrize("scenario", RESUME_SCENARIOS)
def test_IN3p_caller_owned_checkpoint_resume(tmp_path, adapter_name, scenario):
    adapter = ADAPTERS[adapter_name]
    inputs = _inputs(scenario)

    checkpoint_path = tmp_path / "checkpoint.json"
    value = caller.phase1_and_save(adapter, inputs, str(checkpoint_path))

    assert json_roundtrip_ok(value), "checkpoint 값이 JSON round-trip 불가"
    assert only_plain_types(value), "checkpoint 값에 라이브러리 타입 누출"
    # recursive 전용 — 실행기 내부 표현(frozenset/visited/depth)이 checkpoint 값에
    # 누출되지 않았는지 키 이름으로 재확인(구조적 누출 방지, only_plain_types의 보강).
    assert "visited" not in value and "depth" not in value
    assert checkpoint_path.exists(), "caller가 checkpoint 파일을 쓰지 않음"

    completed = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "_resume_subprocess.py"), adapter_name, str(checkpoint_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    resumed_state = json.loads(completed.stdout)

    single_shot = caller.run_full(adapter, copy.deepcopy(inputs))
    assert resumed_state == single_shot, "fresh 프로세스 재개 결과 != 단발 실행 결과"


def test_IN3p_adapter_does_no_persistence_io():
    for rel in ["adapters/recursive.py", "adapters/langgraph.py"]:
        src = (ROOT / rel).read_text()
        for banned in ("open(", "json.dump", "json.load", "pathlib", "os.path.join", "pickle"):
            assert banned not in src, f"{rel}: 어댑터가 영속화({banned})를 수행함"


# ---------------------------------------------------------------- IN-4'
# 계보 교체가 Kernel/HQ(=caller/domain) 코드 0 변경.
def test_IN4p_swap_zero_kernel_hq_change():
    for rel in KERNEL_HQ_FILES:
        src = (ROOT / rel).read_text()
        assert not _imports(src, "adapters"), rel
        assert not _imports(src, "langgraph"), rel
        assert not _imports(src, "langchain"), rel

    assert "adapter" in inspect.signature(caller.run_full).parameters
    assert "adapter" in inspect.signature(caller.phase1_and_save).parameters
    assert "adapter" in inspect.signature(caller.load_and_phase2).parameters

    grep = subprocess.run(
        ["git", "grep", "-nE", "langgraph|langchain", "--", "core/", "hqs/"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert grep.stdout.strip() == "", f"production 경로 오염:\n{grep.stdout}"


def test_IN4p_hashes_identical_across_lineages(tmp_path):
    import hashlib

    def snapshot():
        return {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in KERNEL_HQ_FILES}

    before = snapshot()
    caller.run_full(rc_adapter, _inputs("clean"))
    caller.run_full(lg_adapter, _inputs("clean"))
    caller.phase1_and_save(rc_adapter, _inputs("data_gap"), str(tmp_path / "a.json"))
    caller.phase1_and_save(lg_adapter, _inputs("data_gap"), str(tmp_path / "b.json"))
    assert snapshot() == before


# ---------------------------------------------------------------- IN-5'
# 라이브러리 경계 격리 + 계보 간 코드 비공유.
def test_IN5p_langgraph_import_single_module():
    non_importers = ["adapters/recursive.py", *KERNEL_HQ_FILES]
    for rel in non_importers:
        assert not _imports((ROOT / rel).read_text(), "langgraph"), rel
    assert _imports((ROOT / "adapters/langgraph.py").read_text(), "langgraph")


def test_IN5p_domain_and_recursive_import_without_langgraph():
    code = (
        "import sys; sys.modules['langgraph'] = None;"
        "import importlib;"
        "mods = ['domain.state','domain.nodes','domain.fixtures','domain.graph_spec',"
        "'adapters.recursive','caller'];"
        "[importlib.import_module(m) for m in mods];"
        "import caller; from adapters import recursive;"
        "from domain.state import new_state;"
        "s = caller.run_full(recursive, new_state('X','clean'));"
        "assert s['outcome'] == 'COMPLETED';"
        "print('OK')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True
    )
    assert completed.stdout.strip() == "OK", completed.stderr


def test_IN5p_no_library_types_in_state():
    for adapter in ADAPTERS.values():
        state = caller.run_full(adapter, _inputs("clean"))
        assert only_plain_types(state)


def test_IN5p_recursive_and_langgraph_do_not_share_code():
    rc = (ROOT / "adapters/recursive.py").read_text()
    lg = (ROOT / "adapters/langgraph.py").read_text()
    assert not _imports(rc, "adapters.langgraph")
    assert not _imports(lg, "adapters.recursive")
    assert _imports(rc, "domain") and _imports(lg, "domain")  # 공유는 domain.* 한 곳


# ---------------------------------------------------------------- IN-6' (재설계 — 기계적 복제 아님)
# 계보 독립성을 "정적 import 목록"만이 아니라 (1) 자료구조 부재,
# (2) 실행 메커니즘 자체(재귀 self-call + 실측 재귀 깊이)로 증명한다.

# IN-6'-1 — 정적 의존성 (필요조건, E5 IN-6 계승 — 이것만으로는 불충분함을
# IN-6'-2/3이 보강한다).
def test_IN6p_1_recursive_stdlib_and_domain_only():
    src = (ROOT / "adapters/recursive.py").read_text()
    assert not _imports(src, "langgraph")
    assert not _imports(src, "langchain")
    assert not _imports(src, "worklist")
    assert not _imports(src, "sequential")
    allowed_roots = {"__future__", "copy", "domain"}
    assert _import_roots(src) <= allowed_roots, f"recursive import 위반: {_import_roots(src) - allowed_roots}"


# IN-6'-2 — 구조 부재 검사(신설): L-A류 "인터프리터 인스턴스 + 큐"가
# 이름만 바뀐 재구현이 아님을 소스 구조로 강제한다.
def test_IN6p_2_recursive_has_no_class_or_queue():
    src = (ROOT / "adapters/recursive.py").read_text()
    tree = ast.parse(src)
    assert not any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)), "recursive.py에 class 정의 존재"
    assert "collections" not in _import_roots(src), "recursive.py가 collections(deque 등)를 import"
    # 코드 바디(문서 docstring 제외)에 큐 자료구조 사용 흔적이 없는지 확인.
    # 모듈 docstring은 L-A와의 대조 설명을 위해 "deque"라는 단어를 인용하므로
    # 텍스트 전체가 아니라 AST 바디(모듈 docstring을 제외한 구문 트리)만 본다.
    body_without_docstring = tree.body[1:] if ast.get_docstring(tree) else tree.body
    body_src = "\n".join(ast.unparse(n) for n in body_without_docstring)
    assert "deque" not in body_src, "recursive.py 코드 바디에 deque 사용 흔적"


@pytest.mark.skipif(not SIBLING_WORKLIST.exists(), reason="sibling E5 프로젝트(L-A)가 없음 — 폐기된 경우 스킵")
def test_IN6p_2_worklist_sibling_has_class_and_queue_for_contrast():
    """대조 확인 — L-A(worklist.py)는 실제로 class+deque를 쓴다(정적 텍스트 읽기, import 없음)."""
    src = SIBLING_WORKLIST.read_text()
    tree = ast.parse(src)
    assert any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)), "worklist.py에 class 정의 없음(전제 무효)"
    assert "collections" in _import_roots(src) or "deque" in src


# IN-6'-3 — 실행 메커니즘 실측(신설): "재귀냐 반복이냐"를 주장이 아니라
# (a) 자기 재귀 호출의 정적 검출, (b) 실행 중 재귀 깊이 실측으로 증명한다.
def test_IN6p_3_advance_is_self_recursive_by_source():
    src = (ROOT / "adapters/recursive.py").read_text()
    assert _defines_self_recursive_function(src, "_advance"), "_advance가 자기 자신을 재귀 호출하지 않음"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN6p_3_recursion_depth_is_deep_not_constant(scenario):
    """L-B의 콜스택 깊이가 그래프 실행 경로 길이에 비례하는 다층 재귀임을 실측한다.

    도메인 경로: dispatch -> analyst(5번째) -> collect -> (bull->bear->judge)x3
    -> trader -> terminal = 최소 13단 이상의 중첩. 상수(예: 2~3)에 머무르는
    반복문 기반 스케줄러라면 이 깊이가 나올 수 없다.
    """
    _, max_depth = rc_adapter.run_full_with_depth(_inputs(scenario))
    assert max_depth >= 12, f"재귀 깊이가 얕음(max_depth={max_depth}) — 재귀 기반이라는 주장과 불일치"


@pytest.mark.skipif(not SIBLING_WORKLIST.exists(), reason="sibling E5 프로젝트(L-A)가 없음 — 폐기된 경우 스킵")
def test_IN6p_3_worklist_run_is_iterative_not_self_recursive():
    """대조 확인 — L-A의 진행 메서드(run)는 while 루프 기반이며 자기 자신을
    재귀 호출하지 않는다(정적 텍스트 읽기, import 없음 — 런타임 결합 없음)."""
    src = SIBLING_WORKLIST.read_text()
    tree = ast.parse(src)
    run_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "run"]
    assert run_defs, "worklist.py에 run 메서드 없음(전제 무효)"
    run_node = run_defs[0]
    assert any(isinstance(n, ast.While) for n in ast.walk(run_node)), "worklist.run에 while 루프 없음(전제 무효)"
    assert not any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "run"
        for n in ast.walk(run_node)
    ), "worklist.run이 자기 자신을 재귀 호출함 — L-A/L-B 대조 전제 무효"
