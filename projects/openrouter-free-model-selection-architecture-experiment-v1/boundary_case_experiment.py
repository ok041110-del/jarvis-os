"""Candidate Selection의 5개 Case(0/1/2/3/>3)를 **실제 조회한 Free
Pool 메타데이터**로 전부 재현한다. Stage 01~05의 실제 Requirement는
이번 세션 기준 항상 `>3_candidates`로 귀결됐으므로(모든 Stage의
context 요구치가 대부분 free 모델의 context_length보다 훨씬 작음),
나머지 4개 case는 동일한 실측 Pool에 **합성 Requirement**(실제
메타데이터 분포를 근거로 역산한 임계값)를 적용해 Filter/Selection
로직 자체가 5개 case 모두에서 올바르게 동작하는지 확인한다.

이 스크립트는 OpenRouter Chat Completions를 호출하지 않는다(순수
Free Pool 조회 + Filter + Selection만) — quota를 소모하지 않는다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.candidate_selection import select_candidates  # noqa: E402
from domain.deterministic_filter import apply_deterministic_filter  # noqa: E402
from domain.free_pool import fetch_free_pool  # noqa: E402
from domain.stage_requirements import StageRequirement  # noqa: E402


def _mk_req(name: str, *, min_context: int, input_mod: tuple[str, ...], output_mod: tuple[str, ...], basis: str) -> StageRequirement:
    return StageRequirement(
        stage=name,
        prompt="(boundary-case-only — 실제 OpenRouter 호출 없음)",
        required_input_modalities=input_mod,
        required_output_modalities=output_mod,
        min_context_tokens=min_context,
        min_context_tokens_basis=basis,
        output_contract=lambda content: None,
        token_budget=0,
    )


def main() -> dict:
    pool = fetch_free_pool()
    print(f"Free Pool 실측 크기: {len(pool.models)}", file=sys.stderr)

    scenarios = {
        "0_candidates_target": _mk_req(
            "boundary_0",
            min_context=0,
            input_mod=("text",),
            output_mod=("audio",),  # 실측 Pool 어떤 모델도 output modality에 audio가 없음(§본문 확인)
            basis="output_modality=audio 요구 — 실측 Pool 19개 중 output에 audio를 포함하는 모델 0개(고의적 경계 조건, 추측 아님)",
        ),
        "1_candidate_target": _mk_req(
            "boundary_1",
            min_context=100000,
            input_mod=("text", "video", "audio"),
            output_mod=("text",),
            basis="input_modality=text+video+audio 동시 요구 — 실측 Pool 중 nemotron-3-nano-omni-30b-a3b-reasoning(256000, text+audio+image+video)만 유일하게 충족",
        ),
        "2_candidates_target": _mk_req(
            "boundary_2",
            min_context=600000,
            input_mod=("text",),
            output_mod=("text",),
            basis="min_context=600000 — 실측 Pool 중 nemotron-3.5-lightning/nemotron-3-ultra-550b(둘 다 1,000,000)만 충족, dots-studio(512000)는 미달",
        ),
        "3_candidates_target": _mk_req(
            "boundary_3",
            min_context=500000,
            input_mod=("text",),
            output_mod=("text",),
            basis="min_context=500000 — 실측 Pool 중 nemotron-3.5-lightning/nemotron-3-ultra-550b(1,000,000 x2)+dots-studio(512000) 3개 충족",
        ),
    }

    results = {}
    for name, requirement in scenarios.items():
        filter_results = apply_deterministic_filter(pool, requirement)
        selection = select_candidates(name, filter_results)
        results[name] = {
            "requirement_basis": requirement.min_context_tokens_basis,
            "kept_count": selection.kept_count,
            "kept_model_ids": list(selection.kept_model_ids),
            "case": selection.case,
            "final_candidates": list(selection.final_candidates),
            "tie_break_applied": selection.tie_break_applied,
        }
        print(f"{name}: case={selection.case} kept={selection.kept_count} final={selection.final_candidates}", file=sys.stderr)

    results["pool_size"] = len(pool.models)
    return results


if __name__ == "__main__":
    output = main()
    with open("/tmp/boundary_case_experiment_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))
