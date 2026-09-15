"""MVP-0001 Exit Criteria 검증 — 입력 코드가 주어지면 수동 개입 없이 Code Review와 Test Case가 순서대로 반환돼야 한다.

아래 두 테스트는 `call_engine()`을 mock하지 않고 실제 backend(ChatGPT/Claude Code, `ADR-0024`)를 호출하므로
기본적으로 SKIP되며, 아래처럼 opt-in 해야 실행된다(위험 배경: `EVIDENCE-0007`/`EVIDENCE-0008`).

    RUN_REAL_ENGINE_TESTS=1 pytest hqs/development/mvp/tests/test_mvp_0001.py -v
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp.agents import AGENT_CAPABILITY_MAP, backend, qa
from mvp.workflow import run_mvp_0001

SAMPLE_CODE = """
def add(a, b=[]):
    try:
        return a + b
    except:
        pass
"""

RUN_REAL_ENGINE_FLAG = "RUN_REAL_ENGINE_TESTS"
_skip_unless_real_engine_gate = pytest.mark.skipif(
    os.environ.get(RUN_REAL_ENGINE_FLAG) != "1",
    reason=(
        f"실제 Engine 호출(현재 backend: ChatGPT+Claude Code, `ADR-0024`) — "
        f"opt-in 전용, {RUN_REAL_ENGINE_FLAG}=1 로 명시적으로 실행해야 한다"
    ),
)


@_skip_unless_real_engine_gate
def test_returns_review_then_test_cases_without_manual_intervention():
    result = run_mvp_0001(SAMPLE_CODE)

    assert list(result.keys()) == ["code_review", "test_execution"]
    assert result["code_review"]
    assert result["test_execution"]


@_skip_unless_real_engine_gate
def test_review_content_reaches_test_execution_as_context(monkeypatch):
    """`workflow.py`의 context 전달(`review` → `payload`) 메커니즘만 검증한다(exact-substring assertion은 쓰지 않음) —
    Agent Package Refactoring 이후 Backend/QA 각 모듈이 별도 `call_engine` reference를 가지므로 둘 다 개별 patch가 필요하다."""
    engine_prompts = []
    original_backend_call_engine = backend.call_engine_review
    original_qa_call_engine = qa.call_engine

    def spy_backend_call_engine(prompt):
        engine_prompts.append(prompt)
        return original_backend_call_engine(prompt)

    def spy_qa_call_engine(prompt):
        engine_prompts.append(prompt)
        return original_qa_call_engine(prompt)

    monkeypatch.setattr(backend, "call_engine_review", spy_backend_call_engine)
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
