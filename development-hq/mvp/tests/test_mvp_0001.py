"""MVP-0001 Exit Criteria 검증.

MVP.md Exit Criteria: 입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와
Test Case 제안이 순서대로 반환되어야 한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.agents import AGENT_CAPABILITY_MAP
from mvp.workflow import run_mvp_0001

SAMPLE_CODE = """
def add(a, b=[]):
    try:
        return a + b
    except:
        pass
"""


def test_returns_review_then_test_cases_without_manual_intervention():
    result = run_mvp_0001(SAMPLE_CODE)

    assert list(result.keys()) == ["code_review", "test_execution"]
    assert result["code_review"]
    assert result["test_execution"]


def test_review_content_reaches_test_execution_as_context():
    result = run_mvp_0001(SAMPLE_CODE)

    assert "bare except" in result["code_review"]
    assert "예외 처리 동작을 검증" in result["test_execution"]


def test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope():
    assert AGENT_CAPABILITY_MAP == {
        "code_review": "Backend Agent",
        "test_execution": "QA Agent",
    }
