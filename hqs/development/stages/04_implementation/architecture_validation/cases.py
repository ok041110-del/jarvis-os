"""Stage 04 Architecture Validation — Test Cases(RFC 요청 §12). 5개 대표
Case를 고정된 `build_input`(Design 역할), `target`, `expose_target`으로
정의한다 — 전부 합성 데이터라 실제 repository 파일을 참조하거나
변경하지 않는다. `target`/`expose_target`을 Case에 고정해 A/B/C 전부
동일한 값을 쓰게 한다(Controlled Variables — Target Resolver 최적화는
별도 후속 실험).

`allowed_function_names`(정의해도 되는 최대 범위)와
`required_function_names`(반드시 정의해야 하는 최소 범위)를 구분한다 —
`case_c_helper_reuse`처럼 "이미 존재하는 helper는 재사용만 하고 다시
정의하지 않아야 한다"는 요구를 표현하려면 둘이 달라야 한다."""

CASES = [
    {
        "case_id": "case_a_simple_function",
        "description": "단순 함수 — 문자열을 뒤집는 함수 1개.",
        "build_input": (
            "Design: implement a function `reverse_text(text: str) -> str` "
            "that returns the input string reversed."
        ),
        "target": ("case_a_module", "reverse_text"),
        "expose_target": False,
        "allowed_function_names": ("reverse_text",),
        "required_function_names": ("reverse_text",),
    },
    {
        "case_id": "case_b_moderate_modification",
        "description": "중간 복잡도의 기존 코드 수정 — 기존 함수에 파라미터 추가.",
        "build_input": (
            "Design: extend the existing function `format_amount(value: float) -> str` "
            "to accept an optional `currency: str = 'USD'` parameter and prefix the "
            "formatted amount with the currency code."
        ),
        "target": ("case_b_module", "format_amount"),
        "expose_target": False,
        "allowed_function_names": ("format_amount",),
        "required_function_names": ("format_amount",),
    },
    {
        "case_id": "case_c_helper_reuse",
        "description": "기존 helper 재사용이 중요한 작업 — `_truncate`는 재사용 대상일 뿐 재정의 대상이 아니다.",
        "build_input": (
            "Design: implement `summarize_lines(lines: list) -> str` that must reuse "
            "the existing helper `_truncate(text: str, limit: int) -> str` (already "
            "defined elsewhere) to cap each line at 80 characters before joining them."
        ),
        "target": ("case_c_module", "summarize_lines"),
        "expose_target": False,
        "allowed_function_names": ("summarize_lines", "_truncate"),
        "required_function_names": ("summarize_lines",),
    },
    {
        "case_id": "case_d_overcompression_risk",
        "description": "LLM이 지나치게 압축된 코드를 작성하기 쉬운 작업(다중 조건 분기).",
        "build_input": (
            "Design: implement `classify_score(score: int) -> str` that returns "
            "'fail' for score < 50, 'pass' for 50 <= score < 75, and 'excellent' "
            "for score >= 75. Prefer explicit, readable control flow."
        ),
        "target": ("case_d_module", "classify_score"),
        "expose_target": False,
        "allowed_function_names": ("classify_score",),
        "required_function_names": ("classify_score",),
    },
    {
        "case_id": "case_e_comment_prone",
        "description": "Comment/Docstring이 생성될 가능성이 높은 작업(비직관적 제약 포함).",
        "build_input": (
            "Design: implement `retry_with_backoff(attempts: int) -> list` returning "
            "the delay in seconds before each attempt, doubling each time starting at "
            "1 second, capped at 30 seconds due to an external rate-limit constraint."
        ),
        "target": ("case_e_module", "retry_with_backoff"),
        "expose_target": False,
        "allowed_function_names": ("retry_with_backoff",),
        "required_function_names": ("retry_with_backoff",),
    },
]
