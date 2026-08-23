"""Agent 패키지 — Requirements/Design/Backend/QA Agent(Agent Definition 0001)를 파일별로 분리하고,
기존 `from .agents import ...` 외부 Contract를 re-export로 유지한다(ADC-0006)."""

from .backend import (
    NO_ISSUES_MARKER,
    backend_agent_code_generation,
    backend_agent_code_review,
)
from .design import design_agent_design
from .qa import qa_agent_test_execution
from .requirements import requirements_agent_requirement_analysis

AGENT_CAPABILITY_MAP = {
    "code_review": "Backend Agent",
    "test_execution": "QA Agent",
}

# Hello SDLC 전용 별도 딕셔너리 — AGENT_CAPABILITY_MAP을 2개 항목으로
# 고정 검증하는 test_mvp_0001.py를 깨지 않기 위해 확장하지 않는다.
HELLO_SDLC_CAPABILITY_MAP = {
    "requirement_analysis": "Requirements Agent",
    "design": "Design Agent",
    "code_generation": "Backend Agent",
}

__all__ = [
    "NO_ISSUES_MARKER",
    "backend_agent_code_generation",
    "backend_agent_code_review",
    "design_agent_design",
    "qa_agent_test_execution",
    "requirements_agent_requirement_analysis",
    "AGENT_CAPABILITY_MAP",
    "HELLO_SDLC_CAPABILITY_MAP",
]
