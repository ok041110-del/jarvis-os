"""ADR-0026 Architecture Experiment Harness 테스트. 실제 네트워크 호출
없이 검증 가능한 것만 Fixture/Mock으로 확인한다(§11 원칙과 동일 —
외부 서비스를 실제로 공격/rate-limit 유발하지 않는다)."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from domain.candidate_selection import MAX_CANDIDATES, select_candidates  # noqa: E402
from domain.deterministic_filter import CheckResult, ModelFilterResult, apply_deterministic_filter  # noqa: E402
from domain.free_pool import FreeModelMetadata, FreePool  # noqa: E402
from domain.stage_requirements import StageRequirement, build_stage_requirements  # noqa: E402


def _mk_result(model_id: str, overall: str) -> ModelFilterResult:
    return ModelFilterResult(model_id=model_id, checks=(), overall=overall, exclusion_reasons=())


# ---- 1. Candidate Selection — 5개 case ---------------------------------------


def test_zero_candidates_case():
    r = select_candidates("stage01", ())
    assert r.case == "0_candidates"
    assert r.final_candidates == ()


def test_one_candidate_case():
    results = (_mk_result("a:free", "KEPT"),)
    r = select_candidates("stage01", results)
    assert r.case == "1_candidate"
    assert r.final_candidates == ("a:free",)


def test_two_candidates_case():
    results = (_mk_result("a:free", "KEPT"), _mk_result("b:free", "EXCLUDED"), _mk_result("c:free", "KEPT"))
    r = select_candidates("stage01", results)
    assert r.case == "2_candidates"
    assert r.final_candidates == ("a:free", "c:free")


def test_three_candidates_case_no_tie_break():
    results = tuple(_mk_result(f"m{i}:free", "KEPT") for i in range(3))
    r = select_candidates("stage01", results)
    assert r.case == "3_candidates"
    assert r.tie_break_applied is False
    assert len(r.final_candidates) == 3


def test_more_than_three_candidates_applies_deterministic_tie_break():
    """5개 KEPT -> pool 순서대로 앞 3개만 남아야 한다(재정렬 없음)."""
    results = tuple(_mk_result(f"m{i}:free", "KEPT") for i in range(5))
    r = select_candidates("stage01", results)
    assert r.case == ">3_candidates"
    assert r.kept_count == 5
    assert r.tie_break_applied is True
    assert r.final_candidates == ("m0:free", "m1:free", "m2:free")  # 순서 보존 확인
    assert len(r.final_candidates) == MAX_CANDIDATES


def test_selection_never_exceeds_max_candidates_regardless_of_pool_size():
    results = tuple(_mk_result(f"m{i}:free", "KEPT") for i in range(19))  # 실측 free pool 크기(19)와 동일 규모
    r = select_candidates("stage04", results)
    assert len(r.final_candidates) <= MAX_CANDIDATES


# ---- 2. Deterministic Filter — NOT_DETERMINED 처리 ---------------------------


def _mk_requirement(min_context: int = 1000) -> StageRequirement:
    return StageRequirement(
        stage="test_stage",
        prompt="hello",
        required_input_modalities=("text",),
        required_output_modalities=("text",),
        min_context_tokens=min_context,
        min_context_tokens_basis="test fixture",
        output_contract=lambda content: None,
        token_budget=100,
    )


def test_missing_context_length_is_not_determined_not_excluded():
    """context_length 메타데이터가 없으면 NOT_DETERMINED로만 기록하고,
    이것만으로 후보를 제외하지 않는다(다른 체크가 전부 PASS라면 KEPT)."""
    model = FreeModelMetadata(
        id="mystery/model:free",
        context_length=None,
        input_modalities=("text",),
        output_modalities=("text",),
        supported_parameters=(),
        raw={},
    )
    pool = FreePool(models=(model,), fetched_from="test", fetched_count_total=1)
    requirement = _mk_requirement()
    results = apply_deterministic_filter(pool, requirement)
    assert len(results) == 1
    context_check = next(c for c in results[0].checks if c.check_name == "context")
    assert context_check.verdict == "NOT_DETERMINED"
    assert results[0].overall == "KEPT"  # NOT_DETERMINED가 탈락 사유가 아님을 확인


def test_contract_compatibility_is_always_not_determined_at_filter_stage():
    """사전 메타데이터로 Contract 준수 여부를 판정할 수 없다는 원칙 —
    모든 모델에 대해 이 체크는 항상 NOT_DETERMINED여야 한다."""
    model = FreeModelMetadata(
        id="any/model:free",
        context_length=999999,
        input_modalities=("text",),
        output_modalities=("text",),
        supported_parameters=(),
        raw={},
    )
    pool = FreePool(models=(model,), fetched_from="test", fetched_count_total=1)
    results = apply_deterministic_filter(pool, _mk_requirement())
    contract_check = next(c for c in results[0].checks if c.check_name == "contract_compatibility")
    assert contract_check.verdict == "NOT_DETERMINED"


def test_insufficient_context_length_excludes_model():
    model = FreeModelMetadata(
        id="small/model:free",
        context_length=500,
        input_modalities=("text",),
        output_modalities=("text",),
        supported_parameters=(),
        raw={},
    )
    pool = FreePool(models=(model,), fetched_from="test", fetched_count_total=1)
    results = apply_deterministic_filter(pool, _mk_requirement(min_context=1000))
    assert results[0].overall == "EXCLUDED"
    assert any("context" in reason.lower() or "1000" in reason for reason in results[0].exclusion_reasons)


def test_missing_output_modality_excludes_model():
    model = FreeModelMetadata(
        id="image-only/model:free",
        context_length=999999,
        input_modalities=("text", "image"),
        output_modalities=("image",),  # text 출력 불가
        supported_parameters=(),
        raw={},
    )
    pool = FreePool(models=(model,), fetched_from="test", fetched_count_total=1)
    results = apply_deterministic_filter(pool, _mk_requirement())
    assert results[0].overall == "EXCLUDED"


def test_filter_preserves_pool_order_no_reordering():
    ids = ["z:free", "a:free", "m:free"]
    models = tuple(
        FreeModelMetadata(id=i, context_length=999999, input_modalities=("text",), output_modalities=("text",), supported_parameters=(), raw={})
        for i in ids
    )
    pool = FreePool(models=models, fetched_from="test", fetched_count_total=3)
    results = apply_deterministic_filter(pool, _mk_requirement())
    assert [r.model_id for r in results] == ids  # 입력 순서 그대로


# ---- 3. Stage Requirement — 모델명 없음 확인 ----------------------------------


def test_stage_requirements_have_no_model_name_field():
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(StageRequirement)}
    forbidden = {"model", "model_name", "model_id", "fixed_model"}
    assert not (field_names & forbidden)


def test_all_five_stage_requirements_built():
    requirements = build_stage_requirements()
    assert set(requirements.keys()) == {"stage01", "stage02", "stage03", "stage04", "stage05_review"}
    for req in requirements.values():
        assert req.min_context_tokens > 0
        assert req.min_context_tokens_basis  # 추정 근거가 항상 기록됨


# ---- 4. Production 미변경 정적 검사 -------------------------------------------


def test_harness_does_not_import_or_modify_production_engine_modules():
    harness_files = list(HARNESS_ROOT.rglob("*.py"))
    forbidden_imports = ("chatgpt_engine", "mvp.engine", "omniroute_engine")
    for path in harness_files:
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            assert forbidden not in text, f"{path}가 Production Engine 모듈({forbidden})을 참조한다"
