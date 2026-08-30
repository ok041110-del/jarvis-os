"""`hqs/development/stages/contracts.py` — Stage 01~05 Data Contract 검증
(ADR-0008 Stage 구조 위에 추가된 Handover 시점 필수 키 검사). Contract는
Stage 고정 연결이 아니라 데이터 자체의 필수 형태만 검사하므로, 여기서는
(a) 각 `validate_*`가 필수 키 부재를 정확히 잡아내는지, (b) 값이 있으면
통과하는지, (c) `ContractViolation` 메시지가 어떤 키가 빠졌는지 명확히
알려주는지만 검증한다."""

import importlib.util
import sys
from pathlib import Path

import pytest

_CONTRACTS_PATH = Path(__file__).resolve().parents[2] / "stages" / "contracts.py"
_spec = importlib.util.spec_from_file_location("contracts", _CONTRACTS_PATH)
contracts = importlib.util.module_from_spec(_spec)
sys.modules["contracts"] = contracts
_spec.loader.exec_module(contracts)


VALID_CONTEXT_ANALYSIS_RESULT = {
    "directory_structure": "...",
    "context_bundle": {},
    "candidate_index": "INDEX",
    "target": None,
    "dependency_closure": None,
}
VALID_SPECIFICATION_RESULT = {"skeleton": {}, "specification": "SPEC"}
VALID_DESIGN_RESULT = {"skeleton": {}, "design": "DESIGN"}
VALID_IMPLEMENTATION_RESULT = {"target": None, "implementation": "CODE", "expose_target": False}
VALID_VERIFICATION_RESULT = {"required_checks": (), "check_results": [], "verdict": "PASS"}


@pytest.mark.parametrize(
    "validate, valid_data",
    [
        (contracts.validate_context_analysis_result, VALID_CONTEXT_ANALYSIS_RESULT),
        (contracts.validate_specification_result, VALID_SPECIFICATION_RESULT),
        (contracts.validate_design_result, VALID_DESIGN_RESULT),
        (contracts.validate_implementation_result, VALID_IMPLEMENTATION_RESULT),
        (contracts.validate_verification_result, VALID_VERIFICATION_RESULT),
    ],
)
def test_validate_passes_when_all_required_keys_present(validate, valid_data):
    validate(dict(valid_data))  # 예외 없이 통과해야 한다


@pytest.mark.parametrize(
    "validate, valid_data",
    [
        (contracts.validate_context_analysis_result, VALID_CONTEXT_ANALYSIS_RESULT),
        (contracts.validate_specification_result, VALID_SPECIFICATION_RESULT),
        (contracts.validate_design_result, VALID_DESIGN_RESULT),
        (contracts.validate_implementation_result, VALID_IMPLEMENTATION_RESULT),
        (contracts.validate_verification_result, VALID_VERIFICATION_RESULT),
    ],
)
def test_validate_raises_when_any_required_key_missing(validate, valid_data):
    for missing_key in valid_data:
        incomplete = dict(valid_data)
        del incomplete[missing_key]

        with pytest.raises(contracts.ContractViolation) as exc_info:
            validate(incomplete)
        assert missing_key in str(exc_info.value)


def test_require_keys_reports_all_missing_keys_at_once():
    with pytest.raises(contracts.ContractViolation) as exc_info:
        contracts.require_keys({"a": 1}, ("a", "b", "c"), "SampleContract")

    message = str(exc_info.value)
    assert "SampleContract" in message
    assert "b" in message and "c" in message
