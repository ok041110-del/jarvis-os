"""서로 다른 실제 Dev HQ Validation 대상 — 정확성/격리/실행시간 반복 검증용.

`hqs/development/`를 직접 import하지 않는다 — `rtb_runtime`이
`pytest.main()`으로만 호출한다(Boundary 유지). 세 대상은 실행
시간대가 다르다(0.1초 / 0.6초 / ~69초) — Process 전략이 짧은
작업에만 우연히 맞는 게 아니라는 것을 실제 시간대 다양성으로
확인하기 위함(작업 지시 §2)."""

DEV_HQ_TARGETS = {
    "ast_context": "hqs/development/mvp/tests/test_ast_context.py",
    "stage_01": "hqs/development/mvp/tests/test_stage_01.py",
    "mvp_0001": "hqs/development/mvp/tests/test_mvp_0001.py",
}

EXPECTED_PASSED = {
    "ast_context": 8,
    "stage_01": 5,
    "mvp_0001": 3,
}
