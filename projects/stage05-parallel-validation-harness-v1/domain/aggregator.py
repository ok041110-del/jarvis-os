"""Aggregator — validation logic을 새로 발명하지 않는다(사용자 지시
Part 4). 5개 blocking Validator(Structure/Scope/AST/Dependency/Test)의
FAIL/ERROR만 Verdict를 FAIL로 만든다. Review는 항상 advisory —
Review가 PASS여도 deterministic FAIL을 뒤집지 않고, Review가 FAIL/ERROR
여도 deterministic PASS를 자동으로 FAIL로 바꾸지 않는다."""

from __future__ import annotations

from dataclasses import dataclass, field

from .results import (
    ADVISORY_VALIDATOR_IDS,
    BLOCKING_VALIDATOR_IDS,
    VALIDATOR_ID_ORDER,
    ValidatorResult,
    sort_by_fixed_id_order,
)


@dataclass
class AggregationResult:
    verdict: str  # "PASS" | "FAIL" | "PARTIAL"
    results_by_id: dict = field(default_factory=dict)
    ordered_results: list = field(default_factory=list)
    missing_validator_ids: list = field(default_factory=list)


def aggregate(results: list[ValidatorResult]) -> AggregationResult:
    """1. 모든 Validator 결과 수집, 2. ID 정규화, 3. deterministic blocking
    집계, 4. Review 결과 별도 보존, 5. Final Verdict 계산 — 순서 그대로
    구현한다. 이 함수는 어떤 Validator도 직접 실행하지 않는다(이미 끝난
    결과만 받는다)."""
    # 1~2. 수집 + ID 정규화(고정 순서로 정렬, 실행/완료 순서와 분리)
    ordered = sort_by_fixed_id_order(results)
    results_by_id = {r.validator_id: r for r in ordered}

    missing = [vid for vid in VALIDATOR_ID_ORDER if vid not in results_by_id]

    # 3. deterministic blocking 집계 — Structure/Scope/AST/Dependency/Test만.
    blocking_results = [r for r in ordered if r.validator_id in BLOCKING_VALIDATOR_IDS]
    any_blocking_fail = any(r.status in ("FAIL", "ERROR") for r in blocking_results)
    any_blocking_missing = any(vid in missing for vid in BLOCKING_VALIDATOR_IDS)

    # 4. Review는 여기서 별도로만 보존한다 — verdict 계산에 참여시키지 않는다
    #    (아래 5번이 이를 그대로 반영, Review 유무와 무관하게 verdict 불변).
    _ = [r for r in ordered if r.validator_id in ADVISORY_VALIDATOR_IDS]  # 보존 목적 확인용, 계산에 미사용

    # 5. Final Verdict — Review는 절대 참여하지 않는다.
    if any_blocking_fail:
        verdict = "FAIL"
    elif any_blocking_missing:
        verdict = "PARTIAL"
    else:
        verdict = "PASS"

    return AggregationResult(
        verdict=verdict,
        results_by_id=results_by_id,
        ordered_results=ordered,
        missing_validator_ids=missing,
    )
