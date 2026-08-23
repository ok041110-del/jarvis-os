"""MVP-0001 Exit Criteria 검증.

MVP.md Exit Criteria: 입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와
Test Case 제안이 순서대로 반환되어야 한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.agents import AGENT_CAPABILITY_MAP, backend, qa
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
    """`workflow.py`의 context 전달(`review` → `payload`) 메커니즘만 검증한다 —
    Engine 출력 문구에 대한 exact-substring assertion은 쓰지 않는다.

    Agent Package Refactoring 이전에는 Backend/QA Agent가 같은 `agents.py`
    모듈 하나를 공유해 `agents.call_engine` 단일 지점을 patch하면 충분했다.
    분리 이후 각 Agent 모듈이 자신만의 `call_engine` local reference를
    가지므로(`agents/backend.py`, `agents/qa.py`), 실제로 호출되는 두 지점을
    각각 patch해야 한다(ADC-0006 Condition 6 — 실제 module boundary 변경에
    따른 필연적 테스트 조정, monkeypatch target 변경일 뿐 검증 의도는 동일)."""
    engine_prompts = []
    original_backend_call_engine = backend.call_engine
    original_qa_call_engine = qa.call_engine

    def spy_backend_call_engine(prompt):
        engine_prompts.append(prompt)
        return original_backend_call_engine(prompt)

    def spy_qa_call_engine(prompt):
        engine_prompts.append(prompt)
        return original_qa_call_engine(prompt)

    monkeypatch.setattr(backend, "call_engine", spy_backend_call_engine)
    monkeypatch.setattr(qa, "call_engine", spy_qa_call_engine)

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
