"""최소 2-Agent 역할 — 순수 함수, 프레임워크 의존 없음.

이 모듈은 Kernel/HQ 어느 코드도 import하지 않는다. 표준 라이브러리만
쓴다. `RFC-0024`(Agent Domain, Defer)의 Identity/Role/Capabilities 필드를
이 실험이 확정하는 것이 아니다 — 각 함수는 그 필드들과 닮은 매개변수를
받을 뿐, Kernel/HQ에 등록되는 Domain 객체가 아니다.

실패는 예외가 아닌 값으로 표현한다(`BASELINE.md` §14.3 G-6과 동형 원칙 —
이 실험이 그 원칙을 재확정하는 것은 아니며, 관찰상 자연스러운 선택일
뿐이다).
"""
from __future__ import annotations


def run_drafter(topic: str, *, fail: bool = False) -> dict:
    """Agent 역할 1 — 초안을 만든다."""
    if fail:
        return {"status": "error", "agent": "drafter", "error": f"draft failed: {topic}"}
    if not topic:
        return {"status": "error", "agent": "drafter", "error": "empty topic"}
    return {"status": "ok", "agent": "drafter", "draft": f"draft({topic})"}


def run_reviewer(draft_result: dict, *, fail: bool = False) -> dict:
    """Agent 역할 2 — Agent 1의 결과를 입력으로 받아 검토한다."""
    if draft_result.get("status") != "ok":
        return {"status": "error", "agent": "reviewer", "error": "no valid draft to review"}
    if fail:
        return {"status": "error", "agent": "reviewer", "error": "review failed"}
    draft = draft_result["draft"]
    return {"status": "ok", "agent": "reviewer", "review": f"reviewed({draft})"}
