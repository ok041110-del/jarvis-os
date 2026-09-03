"""(C) Reversibility v2 in-repo 통합 테스트 — IN-1 ~ IN-5.

검증 대상 = §16.6 Reversibility 필수 불변조건 + Adapter Contract 부속 명세
(a)(b)(d). 범위 밖(mid-node resume, 성능, 실제 엔진, Public Port, Q-E-2,
(c) 규범화)은 assert하지 않는다 — Test Design 0001 §2.2·§2.3.
"""
from __future__ import annotations

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
from adapters import sequential  # noqa: E402
from domain.state import json_roundtrip_ok, new_state, only_plain_types  # noqa: E402

SCENARIOS = ["clean", "data_gap", "node_error"]
RESUME_SCENARIOS = ["clean", "data_gap"]
ADAPTERS = {"sequential": sequential, "langgraph": lg_adapter}
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


# ---------------------------------------------------------------- IN-1
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN1_final_state_equivalence(scenario):
    seq_state = caller.run_full(sequential, _inputs(scenario))
    lg_state = caller.run_full(lg_adapter, _inputs(scenario))
    assert seq_state == lg_state


@pytest.mark.parametrize(
    "scenario,expected_outcome",
    [("clean", "COMPLETED"), ("data_gap", "ESCALATED_DATA_GAP"), ("node_error", "COMPLETED")],
)
def test_IN1_behavior_record(scenario, expected_outcome):
    """동치 검증의 전제 — 시나리오가 실제로 Conditional·Loop를 밟는지 기록."""
    state = caller.run_full(sequential, _inputs(scenario))
    assert state["outcome"] == expected_outcome
    assert [x for x in state["debate_log"] if x.startswith("BULL")] == ["BULL r0", "BULL r1", "BULL r2"]
    if scenario == "data_gap":
        assert any(str(f).startswith("INCONSISTENT") for f in state["data_flags"])
        assert state["decision"]["action"] == "HOLD"
    if scenario == "node_error":
        assert any(str(f).startswith("NODE_ERROR:analyst_fundamental") for f in state["data_flags"])
        assert "fundamental" not in state


# ---------------------------------------------------------------- IN-2
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_IN2_result_as_value_no_exception(adapter_name, scenario):
    adapter = ADAPTERS[adapter_name]
    try:
        state = caller.run_full(adapter, _inputs(scenario))
        state_p1 = adapter.run_phase1(_inputs(scenario))
        adapter.run_phase2(state_p1)
    except Exception as exc:  # noqa: BLE001 - 경계 밖 예외 전파 = 실패
        pytest.fail(f"{adapter_name}/{scenario}: 예외가 어댑터 경계 밖으로 전파됨: {exc!r}")
    assert state["outcome"] in {"COMPLETED", "ESCALATED_DATA_GAP"}
    if scenario == "node_error":
        assert any(str(f).startswith("NODE_ERROR:") for f in state["data_flags"])


# ---------------------------------------------------------------- IN-3
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
    """어댑터 소스에 파일 영속화 호출이 없어야 한다(값 생산만)."""
    for rel in ["adapters/sequential.py", "adapters/langgraph.py"]:
        src = (ROOT / rel).read_text()
        for banned in ("open(", "json.dump", "json.load", "pathlib", "os.path.join", "pickle"):
            assert banned not in src, f"{rel}: 어댑터가 영속화({banned})를 수행함"


# ---------------------------------------------------------------- IN-4
def _imports(src: str, module_prefix: str) -> bool:
    return (
        f"import {module_prefix}" in src
        or f"from {module_prefix}" in src
        or f"import_module('{module_prefix}" in src
        or f'import_module("{module_prefix}' in src
    )


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


def test_IN4_hashes_identical_across_adapters(tmp_path):
    """두 어댑터로 각각 실행해도 caller/domain 파일 해시가 불변."""
    import hashlib

    def snapshot():
        return {
            rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in KERNEL_HQ_FILES
        }

    before = snapshot()
    caller.run_full(sequential, _inputs("clean"))
    caller.run_full(lg_adapter, _inputs("clean"))
    caller.phase1_and_save(sequential, _inputs("data_gap"), str(tmp_path / "a.json"))
    caller.phase1_and_save(lg_adapter, _inputs("data_gap"), str(tmp_path / "b.json"))
    assert snapshot() == before


# ---------------------------------------------------------------- IN-5
def test_IN5_langgraph_import_single_module():
    non_importers = ["adapters/sequential.py", *KERNEL_HQ_FILES]
    for rel in non_importers:
        assert not _imports((ROOT / rel).read_text(), "langgraph"), rel
    assert _imports((ROOT / "adapters/langgraph.py").read_text(), "langgraph")


def test_IN5_domain_imports_without_langgraph():
    code = (
        "import sys; sys.modules['langgraph'] = None;"
        "import importlib;"
        "mods = ['domain.state','domain.nodes','domain.fixtures','domain.graph_spec',"
        "'adapters.sequential','caller'];"
        "[importlib.import_module(m) for m in mods];"
        "import caller; from adapters import sequential;"
        "from domain.state import new_state;"
        "s = caller.run_full(sequential, new_state('X','clean'));"
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
