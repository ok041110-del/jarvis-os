"""MVP-0004: Hello SDLC — 가장 작은 End-to-End Pipeline.

목적은 각 Stage의 완성도가 아니라 Pipeline이 Issue 하나를 끝까지
통과시키는 것이다 — `workflow.py`/`workflow_0002.py`와 별개의 순차
호출 체인이며 수정하지 않는다. Issue는 `title`/`description`/`status`만
가지는 단순 dict다 — 새 Domain Model을 만들지 않는다.

Kernel Extraction Candidate: 이 하드코딩된 순차 호출이 조건문/설정
파일/파서로 대체되려는 순간이 Task Dispatcher 추출 신호(Stop
Trigger, RFC로 넘긴다).
"""

from .agents import (
    backend_agent_code_generation,
    backend_agent_code_review,
    design_agent_design,
    qa_agent_test_execution,
    requirements_agent_requirement_analysis,
)


def run_hello_sdlc(issue: dict) -> dict:
    try:
        requirement = requirements_agent_requirement_analysis(issue)
        design = design_agent_design(issue, requirement)
        code = backend_agent_code_generation(design)
        review = backend_agent_code_review(code)
        test_cases = qa_agent_test_execution(code, review)
    except Exception as exc:
        return {
            "planning": None,
            "design": None,
            "implementation": None,
            "validation": None,
            "status": "Failed",
            "error": str(exc),
        }

    return {
        "planning": requirement,
        "design": design,
        "implementation": code,
        "validation": {"code_review": review, "test_execution": test_cases},
        "status": "Complete",
    }
