"""ADR-0026 §Candidate Selection(≤3) — Deterministic Filter를 통과한
후보(`KEPT`)를 OpenRouter `models[]`에 넘길 최종 목록(최대 3개)으로
좁힌다. 순위화 없음 — 3개를 초과하면 RFC-0040 §Candidate Selection
Boundary가 정한 tie-break(OpenRouter 조회 순서, 앞에서부터 자름)만
적용한다."""

from __future__ import annotations

from dataclasses import dataclass

from .deterministic_filter import ModelFilterResult

MAX_CANDIDATES = 3  # ADR-0026 §6, API-level limit(OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md §6) 그대로 승계


@dataclass
class CandidateSelectionResult:
    stage: str
    case: str  # "0_candidates" | "1_candidate" | "2_candidates" | "3_candidates" | ">3_candidates"
    kept_count: int
    kept_model_ids: tuple[str, ...]  # Filter 통과 전체(재정렬 없음, pool 순서 그대로)
    final_candidates: tuple[str, ...]  # OpenRouter models[]에 실제 전달될 목록(<=3)
    tie_break_applied: bool
    tie_break_rule: str | None


def select_candidates(stage: str, filter_results: tuple[ModelFilterResult, ...]) -> CandidateSelectionResult:
    # `filter_results`는 `free_pool.fetch_free_pool()`이 반환한 OpenRouter 응답
    # 순서를 그대로 보존한다(deterministic_filter.py가 재정렬하지 않음) — 이
    # 순서 자체가 tie-break의 근거(RFC-0040 §Candidate Selection Boundary)다.
    kept_ids = tuple(r.model_id for r in filter_results if r.overall == "KEPT")
    kept_count = len(kept_ids)

    if kept_count == 0:
        case = "0_candidates"
    elif kept_count == 1:
        case = "1_candidate"
    elif kept_count == 2:
        case = "2_candidates"
    elif kept_count == 3:
        case = "3_candidates"
    else:
        case = ">3_candidates"

    if kept_count > MAX_CANDIDATES:
        final = kept_ids[:MAX_CANDIDATES]
        tie_break_applied = True
        tie_break_rule = (
            "RFC-0040 §Candidate Selection Boundary: 추가 순위화 로직 없이 "
            "OpenRouter `/models` 응답 순서대로 앞에서부터 자름(재정렬 없음)"
        )
    else:
        final = kept_ids
        tie_break_applied = False
        tie_break_rule = None

    return CandidateSelectionResult(
        stage=stage,
        case=case,
        kept_count=kept_count,
        kept_model_ids=kept_ids,
        final_candidates=final,
        tie_break_applied=tie_break_applied,
        tie_break_rule=tie_break_rule,
    )
