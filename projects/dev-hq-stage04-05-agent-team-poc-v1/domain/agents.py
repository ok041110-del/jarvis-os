"""Stage 04/05 Agent 역할의 격리된 재현 — 순수 함수, 프레임워크 없음.

이 모듈은 `hqs/development/` 어떤 코드도 import하지 않는다. 실제
`call_engine_via_omniroute`를 호출하지 않고 그 자리를 결정적 mock으로
대체한다 — Production Engine 연결이나 새 Engine 계약을 만들지 않는다
(`RFC-0030`이 확인한 5개 실제 Engine 호출 지점의 **구조**만 재현).

Target Identification / Implementation / Review / QA 4개는
`docs/architecture/core/RFC-0030` §2가 코드에서 재확인한 4개의 서로
다른 LLM 판단 지점과 1:1 대응한다. Verdict/Aggregator는 이 모듈에
없다 — `caller.py`가 결정적 함수로 소유한다(Agent 아님, Phase F-2
확장 §6의 경계 재확인).
"""
from __future__ import annotations

import time


def target_identification_agent(design: str, candidate_index: str, *, fail: bool = False) -> dict:
    """Stage 04 — 어디를 고칠지 식별(`identify_target`의 판단 재현)."""
    if fail:
        return {"status": "error", "agent": "target_identification", "error": "no matching target"}
    return {
        "status": "ok",
        "agent": "target_identification",
        "target": {"module": "mock_module", "function": "mock_function"},
    }


def implementation_agent(design: str, target: dict, *, fail: bool = False) -> dict:
    """Stage 04 — 코드 작성(`backend_agent_code_generation`의 판단 재현)."""
    if fail:
        return {"status": "error", "agent": "implementation", "error": "code generation failed"}
    return {
        "status": "ok",
        "agent": "implementation",
        "code": f"def {target['function']}(): return '{design}'",
    }


def review_agent(implementation: str, *, fail: bool = False, delay: float = 0.0) -> dict:
    """Stage 05 — 코드 결함 지적(`backend_agent_code_review`의 판단 재현).
    `delay`는 병렬성 측정 테스트 전용 — 기본 0이라 일반 흐름에 영향 없음."""
    if delay:
        time.sleep(delay)
    if fail:
        return {"status": "error", "agent": "review", "error": "review engine failure"}
    return {"status": "ok", "agent": "review", "issues": []}


def qa_agent(implementation: str, *, fail: bool = False, delay: float = 0.0) -> dict:
    """Stage 05 — 테스트 케이스 제안(`qa_agent_test_execution`의 판단 재현,
    Production에서는 미호출이지만 이 PoC는 활성화된 경로를 검증한다).
    `delay`는 병렬성 측정 테스트 전용."""
    if delay:
        time.sleep(delay)
    if fail:
        return {"status": "error", "agent": "qa", "error": "qa engine failure"}
    return {"status": "ok", "agent": "qa", "proposed_tests": ["test_mock_function_returns_design"]}
