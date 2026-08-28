"""Development HQ Adapter — 기존 Production Contract/Workflow/Engine을
변경하지 않고 연결한다(작업 지시 §5).

Dev HQ의 실제 코드(`hqs/development/`)를 직접 import하지 않는다 —
`pytest.main()`으로 실제 Validation 대상을 실행하는 것은 이미
`runtime-boundary`/`process-runtime-strategy` Prototype이 검증한
안전한 방식이다(실제 Engine 호출·코드 생성 없음, read-only).

이 Adapter가 하는 일은 "action 이름 → 실제 대상 경로" 매핑뿐이다.
Dev HQ의 Workflow/Engine을 호출하거나 그 결과를 해석하지 않는다 —
그 실행은 전적으로 Runtime(`rtb_runtime`)의 책임이다.
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
