"""MVP-0001 Exit Criteria 검증.

MVP.md Exit Criteria: 입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와
Test Case 제안이 순서대로 반환되어야 한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import agents
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


def test_review_content_reaches_test_execution_as_context(monkeypatch):
    """Task 1(code_review)의 실제 출력이 Task 2(test_execution) 호출의
    입력 payload에 verbatim으로 포함되는지를 검증한다 — Engine이 반환하는
    문구가 아니라 `workflow.py`의 context 전달 메커니즘(`review` 지역
    변수 → `payload`) 자체를 검증한다. rule-based 응답의 정확한 문구에
    결합된 exact-substring assertion(ENGINE-CONNECT-0001에서 실제 Engine과
    불일치가 관찰됨)을 쓰지 않는다."""
    engine_prompts = []
    original_call_engine = agents.call_engine

    def spy_call_engine(prompt):
        engine_prompts.append(prompt)
        return original_call_engine(prompt)

    monkeypatch.setattr(agents, "call_engine", spy_call_engine)

    result = run_mvp_0001(SAMPLE_CODE)

    assert len(engine_prompts) == 2
    review = result["code_review"]
    test_execution_prompt = engine_prompts[1]
    assert review in test_execution_prompt
    assert "except" in review.lower()


def test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope():
    assert AGENT_CAPABILITY_MAP == {
        "code_review": "Backend Agent",
        "test_execution": "QA Agent",
    }
