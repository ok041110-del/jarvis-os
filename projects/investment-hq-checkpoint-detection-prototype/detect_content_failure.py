"""최소 Detection Prototype — "콘텐츠 실패를 Checkpoint 저장 전에 감지할 수 있는가" 하나만 검증한다.

`hqs/investment/checkpoint.py`는 수정하지 않는다. 이 모듈은 독립 함수 하나만 제공하며, `run_step`/`Checkpointer.save()`에 실제로 연결하지 않는다(연결 여부는 별도 판단 대상 — Freeze Blocker Review 지시 범위 밖).
"""

KNOWN_FAILURE_PREFIXES = ("API Error:",)


def is_content_failure(output: str) -> bool:
    """실제 관찰된 시그니처로 시작하는지만 확인한다 — 부분 문자열이 아니라 접두어 검사인 이유: 정상 분석 콘텐츠가 본문 중간에 "API"라는 단어를 포함하는 사례가 이미 실제 checkpoint 파일들에서 관찰됐다(예: "capital"에 "api"가 부분 문자열로 포함됨). 접두어 검사는 이런 경우를 오탐하지 않는다."""
    stripped = output.strip()
    return any(stripped.startswith(prefix) for prefix in KNOWN_FAILURE_PREFIXES)
