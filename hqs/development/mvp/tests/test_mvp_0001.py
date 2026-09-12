"""MVP-0001 Exit Criteria 검증.

MVP.md Exit Criteria: 입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와
Test Case 제안이 순서대로 반환되어야 한다.

## 실제 Engine 호출 opt-in Gate(`RUN_REAL_ENGINE_TESTS`, 2026-09-07 도입)

아래 두 테스트는 `call_engine()`을 mock하지 않거나(첫 번째) 원본을
그대로 감싸는 spy만 쓴다(두 번째) — 즉 **실제로 `call_engine()`의
현재 backend를 호출한다.**
`docs/architecture/core/EVIDENCE-0007-omniroute-call-site-conversion-hold.md`
§3.1이 이 사실을 OmniRoute Call-Site Conversion의 차단 사유로
기록했다 — `call_engine()`의 backend가 무엇이든 기본 `pytest`
실행에서 게이트 없이 실제 Engine을 호출하면, backend가 실제 외부
provider egress를 일으킬 수 있는 것으로 바뀌었을 때 그 위험을
그대로 물려받는다.

`docs/architecture/core/EVIDENCE-0008-test-mvp-0001-real-engine-gate.md`
가 이 위험을 해소한 재설계다 — 이 두 테스트는 이제 기본적으로
**SKIP**되며, `RUN_REAL_ENGINE_TESTS=1`을 명시적으로 설정해야
실제 Engine을 호출한다.

    RUN_REAL_ENGINE_TESTS=1 pytest hqs/development/mvp/tests/test_mvp_0001.py -v

이 Gate는 `call_engine()`이 무엇을 호출하는지 판단·분기하지
않는다 — 단순히 "실제 Engine을 호출할지 말지"만 결정하는 단일
환경변수 스위치이며, Routing/Fallback/Budget/Policy 로직을 전혀
포함하지 않는다.

## Backend 변경(`docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`, Multi-Engine Architecture)

`ADR-0024` Stage Mapping 이후 `agents/backend.py::backend_agent_code_review`는
ChatGPT Engine(`OPENAI_API_KEY`/`CHATGPT_BASE_URL` 필요)을,
`agents/qa.py::qa_agent_test_execution`은 Claude Code Engine(`claude`
CLI subprocess, 로컬 실행)을 호출한다 — 두 Engine이 서로 다르므로 Gate
활성화 시 각 호출이 실패하는 조건도 서로 다르다: ChatGPT 쪽은
`OPENAI_API_KEY` 미설정/네트워크 불가 시, Claude Code 쪽은 `claude`
CLI 부재 시 각각 안전하게(egress 확산 없이) FAIL한다.
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
    """`workflow.py`의 context 전달(`review` → `payload`) 메커니즘만 검증한다 —
    Engine 출력 문구에 대한 exact-substring assertion은 쓰지 않는다.

    Agent Package Refactoring 이전에는 Backend/QA Agent가 같은 `agents.py`
    모듈 하나를 공유해 `agents.call_engine` 단일 지점을 patch하면 충분했다.
    분리 이후 각 Agent 모듈이 자신만의 `call_engine` local reference를
    가지므로(`agents/backend.py`, `agents/qa.py`), 실제로 호출되는 두 지점을
    각각 patch해야 한다(ADC-0006 Condition 6 — 실제 module boundary 변경에
    따른 필연적 테스트 조정, monkeypatch target 변경일 뿐 검증 의도는 동일).

    Multi-Engine Architecture(`ADR-0024`) 이후 `backend.py`는 `code_review`용
    `call_engine_review`(ChatGPT Engine)와 `code_generation`용
    `call_engine_generation`(Claude Code Engine) 두 이름으로 분리됐다 —
    `run_mvp_0001()`이 실제로 호출하는 것은 `backend_agent_code_review`
    (→ `call_engine_review`)뿐이므로 이 테스트는 그 이름만 patch한다."""
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
