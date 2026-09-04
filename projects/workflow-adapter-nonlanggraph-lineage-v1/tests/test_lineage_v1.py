"""E5 (B-1 / C(ii)) — 비-LangGraph 독립 계보 검증 — IN-1 ~ IN-6.

검증 대상 = §16.6 A-IN 5항목(State·Node·Conditional Edge·Loop·값 기반
Checkpoint/Resume) + Reversibility 필수 불변조건이, LangGraph 아닌 독립
실행 계보(L-A = worklist 인터프리터)에서도 성립하는가. LangGraph(L-LG)는
3-way 동치 대조로 유지한다.

범위 밖(mid-node resume, 성능, 실제 엔진, Public Port, Q-E-2, (c) 규범화)은
assert하지 않는다 — E4 Test Design 0001 §2.2·§2.3 계승.
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
from adapters import worklist as wl_adapter  # noqa: E402
from domain.state import json_roundtrip_ok, new_state, only_plain_types  # noqa: E402

SCENARIOS = ["clean", "data_gap", "node_error"]
RESUME_SCENARIOS = ["clean", "data_gap"]
ADAPTERS = {"worklist": wl_adapter, "langgraph": lg_adapter}
REPO = ROOT.parent.parent
KERNEL_HQ_FILES = [
    "caller.py",
    "domain/state.py",
    "domain/nodes.py",
    "domain/fixtures.py",
    "domain/graph_spec.py",
]


def _inputs(scenario: str) -> dict:
    return new_state("TESTCO", scenario)


def _imports(src: str, module_prefix: str) -> bool:
    return (
        f"import {module_prefix}" in src
        or f"from {module_prefix}" in src
        or f"import_module('{module_prefix}" in src
        or f'import_module("{module_prefix}' in src
    )


# ---------------------------------------------------------------- IN-1
# A-IN (a)(b)(c)(d) + State 동치: 독립 계보(worklist)의 최종 State가
# LangGraph 계보와 dict deep-equal.
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN1_final_state_equivalence_worklist_vs_langgraph(scenario):
    wl_state = caller.run_full(wl_adapter, _inputs(scenario))
    lg_state = caller.run_full(lg_adapter, _inputs(scenario))
    assert wl_state == lg_state


@pytest.mark.parametrize(
    "scenario,expected_outcome",
    [("clean", "COMPLETED"), ("data_gap", "ESCALATED_DATA_GAP"), ("node_error", "COMPLETED")],
)
def test_IN1_worklist_actually_walks_conditional_and_loop(scenario, expected_outcome):
    """동치 검증의 전제 — worklist 계보가 실제로 Conditional 분기·수렴 Loop를 밟는지."""
    state = caller.run_full(wl_adapter, _inputs(scenario))
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


# ---------------------------------------------------------------- IN-2
# 실행 결과의 값 표현 — 예외 비전파.
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN2_result_as_value_no_exception(adapter_name, scenario):
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


# ---------------------------------------------------------------- IN-3
# A-IN(e) 값 기반 Checkpoint/Resume — caller-owned, 별도 프로세스 재개.
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
@pytest.mark.parametrize("scenario", RESUME_SCENARIOS)
def test_IN3_caller_owned_checkpoint_resume(tmp_path, adapter_name, scenario):
    adapter = ADAPTERS[adapter_name]
    inputs = _inputs(scenario)

    checkpoint_path = tmp_path / "checkpoint.json"
    value = caller.phase1_and_save(adapter, inputs, str(checkpoint_path))

    assert json_roundtrip_ok(value), "checkpoint 값이 JSON round-trip 불가"
    assert only_plain_types(value), "checkpoint 값에 라이브러리 타입 누출"
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


def test_IN3_adapter_does_no_persistence_io():
    for rel in ["adapters/worklist.py", "adapters/langgraph.py"]:
        src = (ROOT / rel).read_text()
        for banned in ("open(", "json.dump", "json.load", "pathlib", "os.path.join", "pickle"):
            assert banned not in src, f"{rel}: 어댑터가 영속화({banned})를 수행함"


# ---------------------------------------------------------------- IN-4
# 계보 교체가 Kernel/HQ(=caller/domain) 코드 0 변경.
def test_IN4_swap_zero_kernel_hq_change():
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


def test_IN4_hashes_identical_across_lineages(tmp_path):
    import hashlib

    def snapshot():
        return {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in KERNEL_HQ_FILES}

    before = snapshot()
    caller.run_full(wl_adapter, _inputs("clean"))
    caller.run_full(lg_adapter, _inputs("clean"))
    caller.phase1_and_save(wl_adapter, _inputs("data_gap"), str(tmp_path / "a.json"))
    caller.phase1_and_save(lg_adapter, _inputs("data_gap"), str(tmp_path / "b.json"))
    assert snapshot() == before


# ---------------------------------------------------------------- IN-5
# 라이브러리 경계 격리.
def test_IN5_langgraph_import_single_module():
    non_importers = ["adapters/worklist.py", *KERNEL_HQ_FILES]
    for rel in non_importers:
        assert not _imports((ROOT / rel).read_text(), "langgraph"), rel
    assert _imports((ROOT / "adapters/langgraph.py").read_text(), "langgraph")


def test_IN5_domain_and_worklist_import_without_langgraph():
    code = (
        "import sys; sys.modules['langgraph'] = None;"
        "import importlib;"
        "mods = ['domain.state','domain.nodes','domain.fixtures','domain.graph_spec',"
        "'adapters.worklist','caller'];"
        "[importlib.import_module(m) for m in mods];"
        "import caller; from adapters import worklist;"
        "from domain.state import new_state;"
        "s = caller.run_full(worklist, new_state('X','clean'));"
        "assert s['outcome'] == 'COMPLETED';"
        "print('OK')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True
    )
    assert completed.stdout.strip() == "OK", completed.stderr


def test_IN5_no_library_types_in_state():
    for adapter in ADAPTERS.values():
        state = caller.run_full(adapter, _inputs("clean"))
        assert only_plain_types(state)


# ---------------------------------------------------------------- IN-6 (신규)
# 계보 독립성 — L-A 가 서드파티·LangGraph 무의존이고, 자체 실행 모델을
# 문서화하며, LangGraph 계보와 코드를 공유하지 않는다.
def test_IN6_worklist_stdlib_and_domain_only():
    src = (ROOT / "adapters/worklist.py").read_text()
    assert not _imports(src, "langgraph"), "worklist 가 langgraph 를 import"
    assert not _imports(src, "langchain"), "worklist 가 langchain 을 import"
    # 서드파티 import 금지 — 허용: 표준 라이브러리 + domain.*
    tree = ast.parse(src)
    allowed_roots = {"__future__", "copy", "collections", "domain"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root in allowed_roots, f"worklist import 위반: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in allowed_roots, f"worklist from-import 위반: {node.module}"


def test_IN6_worklist_documents_independent_execution_model():
    src = (ROOT / "adapters/worklist.py").read_text()
    doc = ast.get_docstring(ast.parse(src)) or ""
    assert "실행 모델" in doc, "worklist docstring 에 실행 모델 명문화 없음"
    # E4 sequential / LangGraph 두 계보와의 구분을 명시
    assert "sequential.py" in doc and "langgraph.py" in doc, "두 대조 계보와의 구분 서술 없음"


def test_IN6_lineages_do_not_share_code():
    wl = (ROOT / "adapters/worklist.py").read_text()
    lg = (ROOT / "adapters/langgraph.py").read_text()
    assert not _imports(wl, "adapters.langgraph")
    assert not _imports(lg, "adapters.worklist")
    # 공유는 domain.* 한 곳
    assert _imports(wl, "domain") and _imports(lg, "domain")
