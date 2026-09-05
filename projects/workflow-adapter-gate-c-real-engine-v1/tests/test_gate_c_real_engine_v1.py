"""E7 (Gate C(i) 잔여 한계 — 결정론적 stub) — 실제 Engine 호출 기반 검증.

승인된 Test Design(세션 2026-09-05)에 따른 IN-7-1 ~ IN-7-5.

- opt-in 게이팅: `RUN_REAL_ENGINE_TESTS=1` 없이는 이 파일 전체가 SKIP된다
  (실제 Engine 호출은 비용·지연이 있으므로 기본 `pytest tests/`에 섞지 않음).
- Record-once-replay: `clean`/`data_gap` 시나리오는 각각 정확히 1회만 실제
  Engine을 호출하고, 그 캡처값을 4개 어댑터(sequential/worklist/recursive/
  langgraph) 모두에 동일 주입한다 — "LLM이 매번 같은 말을 하는가"가 아니라
  "같은 값을 4개 어댑터가 동일하게 처리하는가"를 검증한다.
- 실제 Engine 호출 총량은 `engine_cache.real_call_count()`로 계측하고,
  이 스위트 자체가 예산(≤10회) 준수를 assert한다(IN-7-meta).
- 환경 문제(claude CLI 부재·미인증·네트워크 실패)는 FAIL이 아니라 SKIP으로
  구분한다.
- Gate C(i) discharge나 Gate C(iii) 해결을 이 파일은 선언하지 않는다 —
  결과 판정은 후속 ADR/ADC의 몫이다.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os  # noqa: E402

RUN_REAL = os.environ.get("RUN_REAL_ENGINE_TESTS") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="opt-in 게이팅 — RUN_REAL_ENGINE_TESTS=1 로만 실행(실제 Engine 호출 발생, 비용·지연 있음)",
)

import caller  # noqa: E402
from adapters import sequential as seq_adapter  # noqa: E402
from adapters import worklist as wl_adapter  # noqa: E402
from adapters import recursive as rc_adapter  # noqa: E402
from adapters import langgraph as lg_adapter  # noqa: E402
from domain import engine_cache  # noqa: E402 — import 시점에 hqs.investment.engine_client를 통해 sys.path에 hqs/development가 등록됨
from domain.state import json_roundtrip_ok, new_state, only_plain_types  # noqa: E402

import mvp.engine as engine_module  # noqa: E402 — ENGINE_TIMEOUT_SECONDS 로컬 monkeypatch 대상(파일 미수정)

REPO = ROOT.parent.parent
ADAPTERS = {"sequential": seq_adapter, "worklist": wl_adapter, "recursive": rc_adapter, "langgraph": lg_adapter}
REAL_SCENARIOS = ["clean", "data_gap"]
KERNEL_HQ_FILES = [
    "caller.py",
    "domain/state.py",
    "domain/nodes.py",
    "domain/fixtures.py",
    "domain/graph_spec.py",
    "domain/engine_cache.py",
]
CALL_BUDGET = 10

_PROMPTS = {
    "clean": (
        "이것은 소프트웨어 자동화 테스트입니다. 실제 기업이나 실제 시장 데이터를 "
        "언급하지 말고, 완전히 지어낸 가상 회사에 대한 감정 분석 노트를 한 문장으로만 "
        "작성하세요. 전반적으로 안정적이라는 취지로 써 주세요."
    ),
    "data_gap": (
        "이것은 소프트웨어 자동화 테스트입니다. 실제 기업이나 실제 시장 데이터를 "
        "언급하지 말고, 완전히 지어낸 가상 회사에 대한 감정 분석 노트를 한 문장으로만 "
        "작성하세요. 출처마다 결론이 엇갈린다는 취지로 써 주세요."
    ),
}


def _inputs(scenario: str) -> dict:
    return new_state("TESTCO", scenario)


def _imports(src: str, module_prefix: str) -> bool:
    return f"import {module_prefix}" in src or f"from {module_prefix}" in src


@pytest.fixture(scope="module", autouse=True)
def _capture_real_scenarios():
    """모듈 전체에서 재사용할 실제 Engine 캡처 — clean/data_gap 각 1회.

    환경 문제(claude CLI 부재·미인증·네트워크)로 실패하면 SKIP한다(FAIL 아님)
    — 어댑터 결함과 환경 가용성 문제를 구분하기 위함.
    """
    try:
        for scenario, prompt in _PROMPTS.items():
            engine_cache.capture_once(scenario, prompt)
    except Exception as exc:  # noqa: BLE001 — 환경 문제와 로직 결함을 구분
        pytest.skip(f"실제 Engine 호출 환경 사용 불가 — SKIP: {exc!r}")
    yield


@pytest.fixture(scope="module")
def _real_timeout_exception():
    """진짜 timeout 시도 1회로 `subprocess.TimeoutExpired`를 캡처한다(실제 호출 카운트 +1).

    `ENGINE_TIMEOUT_SECONDS`는 이 fixture 안에서만 일시적으로 줄였다가
    복원한다 — `hqs/development/mvp/engine.py` 파일 자체는 무수정.
    """

    def trigger():
        original_timeout = engine_module.ENGINE_TIMEOUT_SECONDS
        engine_module.ENGINE_TIMEOUT_SECONDS = 0.01
        try:
            engine_cache.counted_call_engine("자동화 timeout 테스트 — 아무 응답이나 좋습니다.")
        finally:
            engine_module.ENGINE_TIMEOUT_SECONDS = original_timeout

    try:
        return engine_cache.capture_exception_once("engine_error_real_timeout", trigger)
    except AssertionError:
        pytest.skip("실제 timeout이 0.01초 안에 발생하지 않음(환경이 예상보다 빠름) — SKIP")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"실제 timeout 유도 실패 — 환경 문제로 SKIP: {exc!r}")


@pytest.fixture(scope="module")
def _synthetic_runtime_error_exception():
    """`call_engine()`의 실제 RuntimeError 발생 코드 경로(비-zero exit 분기)를
    조건 통제 하에 재현한다 — `subprocess.run`을 로컬로 대체해 non-zero exit를
    강제할 뿐, 실제 `claude` CLI는 기동하지 않는다(합성, 실제 호출 카운트에
    포함되지 않음 — `EVIDENCE.md`에 그렇게 명시한다).
    """
    original_run = subprocess.run

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="synthetic non-zero exit (IN-7-3b)")

    def trigger():
        subprocess.run = _fake_run
        try:
            engine_module.call_engine("subprocess.run이 대체돼 실제로 나가지 않는 합성 호출")
        finally:
            subprocess.run = original_run

    return engine_cache.capture_exception_once("engine_error_runtime", trigger)


# ---------------------------------------------------------------- IN-7-1
def test_IN7_1_real_engine_actually_invoked_and_returns_text():
    """capture가 실제로 발생했고(카운터 증가), 고정 stub 값이 아닌 텍스트를 반환했는지."""
    for scenario in REAL_SCENARIOS:
        text = engine_cache.get_captured(scenario)
        assert isinstance(text, str) and text.strip() != "", f"{scenario}: 빈 응답"
    assert engine_cache.real_call_count() >= len(REAL_SCENARIOS), "실제 호출 카운터가 캡처 수만큼 증가하지 않음"


# ---------------------------------------------------------------- IN-7-2
@pytest.mark.parametrize("scenario", REAL_SCENARIOS)
def test_IN7_2_record_once_replay_equivalence_across_four_adapters(scenario):
    """동일 캡처값을 4개 어댑터에 주입 → 최종 State가 서로 dict 동치(고정 기대값과의 비교 아님)."""
    states = {name: caller.run_full(adapter, _inputs(scenario)) for name, adapter in ADAPTERS.items()}
    ref_name, ref_state = next(iter(states.items()))
    for name, state in states.items():
        assert state == ref_state, f"{name} != {ref_name} (scenario={scenario})"
    # 실제 Engine 텍스트가 실제로 State를 관통했는지(스텁 고정값이 아님)를 재확인
    assert ref_state["sentiment"]["engine_note"] == engine_cache.get_captured(scenario)


# ---------------------------------------------------------------- IN-7-3
@pytest.mark.parametrize(
    "scenario,fixture_name",
    [("engine_error_real_timeout", "_real_timeout_exception"), ("engine_error_runtime", "_synthetic_runtime_error_exception")],
)
def test_IN7_3_catch_and_encode_real_exceptions_across_four_adapters(scenario, fixture_name, request):
    exc = request.getfixturevalue(fixture_name)
    exc_type = type(exc).__name__
    for name, adapter in ADAPTERS.items():
        state = caller.run_full(adapter, _inputs(scenario))
        flags = state.get("data_flags", [])
        assert any(f.startswith(f"NODE_ERROR:analyst_sentiment:{exc_type}") for f in flags), (
            f"{name}: {scenario} 예외({exc_type})가 catch-and-encode 되지 않음: {flags}"
        )
        # 경계 밖 예외 전파가 없었다는 것 자체가 위 run_full()이 raise 없이 반환했다는 사실로 증명됨.


# ---------------------------------------------------------------- IN-7-4
@pytest.mark.parametrize("adapter_name", list(ADAPTERS))
def test_IN7_4_checkpoint_roundtrip_with_real_engine_payload(tmp_path, adapter_name):
    adapter = ADAPTERS[adapter_name]
    scenario = "clean"
    inputs = _inputs(scenario)

    checkpoint_path = tmp_path / "checkpoint.json"
    value = caller.phase1_and_save(adapter, inputs, str(checkpoint_path))

    assert json_roundtrip_ok(value), "checkpoint 값이 JSON round-trip 불가(실제 Engine 텍스트 포함)"
    assert only_plain_types(value), "checkpoint 값에 라이브러리 타입 누출"
    assert value["sentiment"]["engine_note"] == engine_cache.get_captured(scenario)

    completed = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "_resume_subprocess.py"), adapter_name, str(checkpoint_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    resumed_state = json.loads(completed.stdout)

    single_shot = caller.run_full(adapter, copy.deepcopy(inputs))
    assert resumed_state == single_shot, "fresh 프로세스 재개 결과 != 단발 실행 결과(실제 Engine 페이로드 포함)"


# ---------------------------------------------------------------- IN-7-5
def test_IN7_5_swap_zero_kernel_hq_change():
    for rel in KERNEL_HQ_FILES:
        src = (ROOT / rel).read_text()
        assert not _imports(src, "adapters"), rel
        assert not _imports(src, "langgraph"), rel
        assert not _imports(src, "langchain"), rel

    diff = subprocess.run(
        ["git", "diff", "--stat", "--", "core/", "hqs/", "dashboard/"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert diff.stdout.strip() == "", f"core/hqs/dashboard 변경 감지:\n{diff.stdout}"


def test_IN7_5_hashes_identical_across_adapters():
    import hashlib

    def snapshot():
        return {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in KERNEL_HQ_FILES}

    before = snapshot()
    for adapter in ADAPTERS.values():
        caller.run_full(adapter, _inputs("clean"))
    assert snapshot() == before


# ---------------------------------------------------------------- 예산 메타 검증
def test_IN7_meta_real_call_budget_within_limit():
    """이 스위트 전체의 실제 Engine 호출 총량이 승인된 예산(≤10회) 이내인지."""
    count = engine_cache.real_call_count()
    assert count <= CALL_BUDGET, f"실제 Engine 호출 총량 {count}회 — 예산 {CALL_BUDGET}회 초과"
