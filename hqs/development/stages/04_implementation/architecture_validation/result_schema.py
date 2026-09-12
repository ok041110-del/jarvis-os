"""Stage 04 Architecture Validation — Result Schema(RFC 요청 §13). 실행
1건의 측정값을 구조화된 dict로 담는다. 이 모듈 자체는 LLM을 호출하지
않는다."""

VARIANTS = ("single", "multi", "multi_ponytail")


def new_result(case_id: str, variant: str) -> dict:
    """빈 Result Schema를 만든다. `variant`는 `VARIANTS` 중 하나여야
    한다 — 값 채우기는 호출자(`variants.py`)가 실행 중 수행한다."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant!r}, expected one of {VARIANTS}")

    return {
        "case_id": case_id,
        "variant": variant,
        "llm_calls": 0,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "latency_ms": {
            "total": 0.0,
            "generation": 0.0,
            "validation": 0.0,
            "ponytail": 0.0,
        },
        "correctness": {
            "syntax": None,
            "contract": None,
            "scope": None,
            "pytest": None,
        },
        "quality": {
            "readability": None,
            "explicitness": None,
            "cognitive_load": None,
            "simplicity": None,
        },
        "comments": {
            "count": 0,
            "docstring_count": 0,
            "over_two_lines": 0,
            "compressed": 0,
            "code_changed_for_comment": False,
        },
    }
