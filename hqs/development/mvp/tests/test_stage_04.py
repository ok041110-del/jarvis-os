"""Stage 04(Implementation) `run_stage_04()` 검증 (ADR-0008,
`stages/04_implementation/VALIDATION.md`).

`identify_target`/`build_dependency_closure`/`backend_agent_code_
generation`은 재구현하지 않았으므로 여기서는 (a) Stage 04가 이 함수들에
올바른 입력(Stage 03 design)을 넘기는지, (b) 조립 로직이 target 유무/
exposure 켬끔 4가지 조합에서 결정적으로 맞는지, (c) 기존 오류 포맷
유지 여부만 mock/실제 파일로 검증한다. `("agents.backend", "_strip_code_
fence")`는 Agent Package Refactoring 이후 실제 파일 경로 반영(ADC-0006
Condition 6) — `identify_target`은 mock이지만 조립 로직은 실제
`build_dependency_closure`를 호출한다.
"""

import importlib.util
import sys
from pathlib import Path

_STAGE_04_PATH = Path(__file__).resolve().parents[2] / "stages" / "04_implementation" / "stage_04.py"
_spec = importlib.util.spec_from_file_location("stage_04", _STAGE_04_PATH)
stage_04 = importlib.util.module_from_spec(_spec)
sys.modules["stage_04"] = stage_04
_spec.loader.exec_module(stage_04)

SAMPLE_STAGE_01_CONTEXT = {"candidate_index": "FILE: hqs/development/mvp/agents.py\n..."}
SAMPLE_STAGE_03_OUTPUT = {
    "skeleton": {
        "component_candidates": "FILE: hqs/development/mvp/agents.py\n...",
        "scope_candidates": ["hqs/development/mvp/agents.py"],
        "constraints": [],
        "risks": [],
    },
    "design": "DESIGN TEXT",
}


# --- _assemble_build_input(Capability 2) ------------------------------------


def test_assemble_without_target_returns_design_unchanged():
    build_input = stage_04._assemble_build_input("DESIGN TEXT", None, expose_target=True)
    assert build_input == "DESIGN TEXT"


def test_assemble_with_target_no_exposure_includes_closure_only():
    build_input = stage_04._assemble_build_input(
        "DESIGN TEXT", ("agents.backend", "_strip_code_fence"), expose_target=False
    )
    assert "DESIGN TEXT" in build_input
    assert "---RELEVANT CODE (AST closure)---" in build_input
    assert "def _strip_code_fence(text: str) -> str:" in build_input
    assert "---TARGET FILE" not in build_input


def test_assemble_with_target_and_exposure_includes_full_file_and_policy(tmp_path, monkeypatch):
    fake_mvp_dir = tmp_path / "mvp"
    fake_mvp_dir.mkdir()
    fake_module = fake_mvp_dir / "sample_module.py"
    fake_module.write_text("def target_fn():\n    pass\n")

    monkeypatch.setattr(stage_04, "module_source_path", lambda module: fake_module)
    monkeypatch.setattr(
        stage_04, "build_dependency_closure", lambda module, function: "def target_fn():\n    pass\n"
    )

    build_input = stage_04._assemble_build_input(
        "DESIGN TEXT", ("sample_module", "target_fn"), expose_target=True
    )

    assert "---TARGET FILE (sample_module.py, full content)---" in build_input
    assert "def target_fn():" in build_input
    assert "extending exactly one existing function, `target_fn`" in build_input
    # Phase 2.5 Case C 회귀: Exposure Policy 충돌 시 자유 텍스트 질문 대신
    # 결정적 마커로 응답하도록 지시하는 프로토콜이 포함돼야 한다.
    assert "EXPOSURE_POLICY_CONFLICT: <one-sentence reason>" in build_input


# --- run_stage_04(Capability 1+2+3 통합) ------------------------------------


def test_run_stage_04_happy_path_no_target(monkeypatch):
    monkeypatch.setattr(stage_04, "identify_target", lambda design, candidate_index: None)
    monkeypatch.setattr(stage_04, "backend_agent_code_generation", lambda build_input: "CODE")

    result = stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT)

    assert result == {"target": None, "implementation": "CODE", "expose_target": False}


def test_run_stage_04_happy_path_with_target(monkeypatch):
    monkeypatch.setattr(
        stage_04, "identify_target", lambda design, candidate_index: ("agents.backend", "_strip_code_fence")
    )
    monkeypatch.setattr(stage_04, "backend_agent_code_generation", lambda build_input: "CODE")

    result = stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT, expose_target=True)

    assert result["target"] == ("agents.backend", "_strip_code_fence")
    assert result["implementation"] == "CODE"
    assert result["expose_target"] is True


def test_identify_target_receives_stage_03_design(monkeypatch):
    seen = {}

    def fake_identify(design, candidate_index):
        seen["design"] = design
        return None

    monkeypatch.setattr(stage_04, "identify_target", fake_identify)
    monkeypatch.setattr(stage_04, "backend_agent_code_generation", lambda build_input: "CODE")

    stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT)

    assert seen["design"] == "DESIGN TEXT"


def test_identify_target_reuses_stage_01_candidate_index_without_recomputing(monkeypatch):
    """중복 계산 제거 회귀 테스트: Stage 04는 Stage 01이 이미 계산한
    candidate_index를 그대로 넘겨야 하며, 자체적으로 다시 계산하지
    않는다(CandidateIndex Contract, Producer: Stage 01)."""
    seen = {}

    def fake_identify(design, candidate_index):
        seen["candidate_index"] = candidate_index
        return None

    monkeypatch.setattr(stage_04, "identify_target", fake_identify)
    monkeypatch.setattr(stage_04, "backend_agent_code_generation", lambda build_input: "CODE")

    stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT)

    assert seen["candidate_index"] == SAMPLE_STAGE_01_CONTEXT["candidate_index"]


def test_engine_failure_in_code_generation_returns_error_message(monkeypatch):
    monkeypatch.setattr(
        stage_04, "identify_target", lambda design, candidate_index: ("agents.backend", "_strip_code_fence")
    )

    def raising_generation(build_input):
        raise RuntimeError("boom")

    monkeypatch.setattr(stage_04, "backend_agent_code_generation", raising_generation)

    result = stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT)

    assert result == {"target": None, "implementation": "Engine call failed: boom", "expose_target": False}


def test_engine_failure_in_identify_target_returns_error_message(monkeypatch):
    def raising_identify(design, candidate_index):
        raise TimeoutError("timed out")

    monkeypatch.setattr(stage_04, "identify_target", raising_identify)

    result = stage_04.run_stage_04(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_03_OUTPUT)

    assert result == {
        "target": None,
        "implementation": "Engine call failed: timed out",
        "expose_target": False,
    }
