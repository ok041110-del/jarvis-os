"""최소 Detection Prototype — "콘텐츠 실패를 Checkpoint 저장 전에 감지할 수 있는가" 하나만 검증한다.

`hqs/investment/checkpoint.py`는 수정하지 않는다. 이 모듈은 독립 함수 하나만
제공하며, `run_step`/`Checkpointer.save()`에 실제로 연결하지 않는다(연결
여부는 별도 판단 대상 — Freeze Blocker Review 지시 범위 밖).

감지 기준은 실제로 관찰된 실패 시그니처 하나뿐이다: `efa-2026-08`,
`pg-hq-verify` 두 실행에서 Synthesis 호출이 반환한 텍스트가 토씨 하나
틀리지 않고 동일했다 —

    "API Error: Unable to connect to API: Self-signed certificate detected.
    Check your proxy or corporate SSL certificates"

이 문자열은 `pg-hq-verify` 실행 중 이 세션이 `cat synthesis.md`로 직접
확인했고, `efa-2026-08/EVIDENCE.md`에 동일한 문장이 인용되어 있어 재현이
확인된 실제 관찰 값이다. 다른 실패 유형(예: Realty Income의 "세션 사용
한도 초과")은 EVIDENCE.md에 문장으로만 요약되어 있을 뿐 원문이 보존되지
않았으므로, 이번 Prototype의 감지 대상에 포함하지 않는다(추측 기반 시그니처
추가 금지).
"""

KNOWN_FAILURE_PREFIXES = ("API Error:",)


def is_content_failure(output: str) -> bool:
    """실제 관찰된 시그니처로 시작하는지만 확인한다 — 부분 문자열이 아니라
    접두어 검사인 이유: 정상 분석 콘텐츠가 본문 중간에 "API"라는 단어를
    포함하는 사례가 이미 실제 checkpoint 파일들에서 관찰됐다(예:
    "capital"에 "api"가 부분 문자열로 포함됨). 접두어 검사는 이런 경우를
    오탐하지 않는다."""
    stripped = output.strip()
    return any(stripped.startswith(prefix) for prefix in KNOWN_FAILURE_PREFIXES)
