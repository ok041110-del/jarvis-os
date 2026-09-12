"""공통 Validator Result 스키마 — 6개 Validator·Aggregator가 전부 이
형태만 주고받는다(RFC-0039/ADC-0042의 "완결된 Result 객체만 수집"
원칙). 고정 ID 순서를 여기 한 곳에서만 정의해 Single/Parallel 양쪽이
동일한 정렬 기준을 공유한다."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 고정 ID 순서(사용자 지시) — 실행/완료 순서와 무관하게 항상 이 순서로 정렬한다.
VALIDATOR_ID_ORDER = ("structure", "scope", "ast", "dependency", "test", "review")

BLOCKING_VALIDATOR_IDS = frozenset({"structure", "scope", "ast", "dependency", "test"})
ADVISORY_VALIDATOR_IDS = frozenset({"review"})


@dataclass
class ValidatorResult:
    validator_id: str
    status: str  # "PASS" | "FAIL" | "ERROR" | "SKIPPED"
    latency_ms: float
    detail: dict = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self) -> None:
        if self.validator_id not in VALIDATOR_ID_ORDER:
            raise ValueError(f"unknown validator_id: {self.validator_id!r}")
        if self.status not in ("PASS", "FAIL", "ERROR", "SKIPPED"):
            raise ValueError(f"unknown status: {self.status!r}")

    @property
    def is_blocking(self) -> bool:
        return self.validator_id in BLOCKING_VALIDATOR_IDS


def sort_by_fixed_id_order(results: list[ValidatorResult]) -> list[ValidatorResult]:
    """실행 완료 순서와 무관하게 항상 `VALIDATOR_ID_ORDER`로 정렬한다
    (사용자 지시 — 실행/완료 순서가 결과 순서를 결정해서는 안 된다)."""
    order_index = {vid: i for i, vid in enumerate(VALIDATOR_ID_ORDER)}
    return sorted(results, key=lambda r: order_index[r.validator_id])
