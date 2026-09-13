"""Development HQ Adapter — 기존 Production Contract/Workflow/Engine을 변경하지 않고 연결한다.

hqs/development/를 직접 import하지 않는다 — pytest.main() 실행은 runtime-boundary/process-runtime-strategy가 이미 검증한 안전한 방식이다.
"""

ACTIONS = {
    "ast_context": "hqs/development/mvp/tests/test_ast_context.py",
    "stage_01": "hqs/development/mvp/tests/test_stage_01.py",
    "mvp_0001": "hqs/development/mvp/tests/test_mvp_0001.py",
}

EXPECTED_PASSED = {
    "ast_context": 8,
    "stage_01": 5,
    "mvp_0001": 3,
}


def resolve_target(action: str) -> str:
    if action not in ACTIONS:
        raise ValueError(f"unknown_action: {action}")
    return ACTIONS[action]
