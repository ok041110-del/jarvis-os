"""ADR-0026 §6 Deterministic Filter — "명백히 판정 가능한 사실"만으로
후보를 거른다. 판정 불가능한 metadata는 절대 추측하지 않고
`NOT_DETERMINED`로 기록한다(사용자 지시 §3) — `NOT_DETERMINED`는
탈락(FAIL)이 아니다: 판정 불가능한 항목 때문에 후보를 임의로
제외하면 그 자체가 추측이 되기 때문이다."""

from __future__ import annotations

from dataclasses import dataclass

from ._sibling_import import load_sibling_domain
from .free_pool import FreePool
from .stage_requirements import StageRequirement

_KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT = load_sibling_domain().model_pool._KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT

Verdict = str  # "PASS" | "FAIL" | "NOT_DETERMINED"


@dataclass
class CheckResult:
    check_name: str
    verdict: Verdict
    detail: str


@dataclass
class ModelFilterResult:
    model_id: str
    checks: tuple[CheckResult, ...]
    overall: str  # "KEPT" | "EXCLUDED"
    exclusion_reasons: tuple[str, ...]


def _check_free(model_id: str) -> CheckResult:
    # Free Pool 조회 단계(free_pool.py)가 이미 `:free` 접미사만 반환하므로,
    # 이 시점에는 항상 PASS다 — 그래도 ADR-0026이 "free 여부"를 필터의
    # 첫 항목으로 명시했으므로 검사 자체는 명시적으로 남긴다.
    verdict = "PASS" if model_id.endswith(":free") else "FAIL"
    return CheckResult("free", verdict, f"model id={model_id!r}")


def _check_required_capability(model_id: str) -> CheckResult:
    if model_id in _KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT:
        return CheckResult(
            "required_capability",
            "FAIL",
            "실측 확인된 plain chat completion 비기능 모델(agentic harness 전용, "
            "OPENROUTER-STAGE-MODEL-SELECTION-0001.md §2 실측 근거 승계)",
        )
    return CheckResult(
        "required_capability",
        "PASS",
        "알려진 비기능 모델 목록에 없음(양성 증명 아님 — 실제 성공 여부는 §5 OpenRouter 호출에서 별도 확인)",
    )


def _check_context(context_length: int | None, min_context_tokens: int, basis: str) -> CheckResult:
    if context_length is None:
        return CheckResult("context", "NOT_DETERMINED", "context_length 메타데이터가 OpenRouter 응답에 없음")
    if context_length >= min_context_tokens:
        return CheckResult("context", "PASS", f"context_length={context_length} >= 요구 추정치={min_context_tokens} ({basis})")
    return CheckResult("context", "FAIL", f"context_length={context_length} < 요구 추정치={min_context_tokens} ({basis})")


def _check_modality(
    input_modalities: tuple[str, ...],
    output_modalities: tuple[str, ...],
    required_input: tuple[str, ...],
    required_output: tuple[str, ...],
) -> CheckResult:
    if not input_modalities and not output_modalities:
        return CheckResult("modality", "NOT_DETERMINED", "input/output modality 메타데이터가 OpenRouter 응답에 없음")
    missing_input = set(required_input) - set(input_modalities)
    missing_output = set(required_output) - set(output_modalities)
    if missing_input or missing_output:
        return CheckResult(
            "modality", "FAIL", f"부족한 input={sorted(missing_input)} output={sorted(missing_output)}"
        )
    return CheckResult("modality", "PASS", f"input={input_modalities} output={output_modalities}")


def _check_contract_compatibility() -> CheckResult:
    # ADR-0026 §6 Contract compatibility는 "명백히 판정 가능한 사실"에
    # 해당하지 않는다 — 구조적 출력 준수 여부는 모델 메타데이터에
    # 존재하지 않고, 실제 호출 결과(§6 Contract Validation)로만 확인
    # 가능하다. 사전 단계에서 이를 추측(예: "supported_parameters에
    # response_format이 있으니 통과할 것이다")하지 않는다 — 사용자 지시.
    return CheckResult(
        "contract_compatibility",
        "NOT_DETERMINED",
        "사전 메타데이터로 구조적 출력 준수 여부를 판정할 수 없다 — 실제 호출 후 "
        "Contract Validation(§6)에서만 확인 가능. 이 필터 단계는 이를 추측하지 않는다",
    )


def apply_deterministic_filter(pool: FreePool, requirement: StageRequirement) -> tuple[ModelFilterResult, ...]:
    """OpenRouter 응답 순서를 그대로 보존한 채(재정렬 없음) 각 모델에
    5개 체크를 적용한다. `FAIL`이 하나라도 있으면 `EXCLUDED`,
    `NOT_DETERMINED`만 있으면 그 항목은 판정을 보류할 뿐 제외 사유가
    되지 않는다(§Verdict — 추측 배제 원칙)."""
    results: list[ModelFilterResult] = []
    for model in pool.models:
        checks = (
            _check_free(model.id),
            _check_required_capability(model.id),
            _check_context(model.context_length, requirement.min_context_tokens, requirement.min_context_tokens_basis),
            _check_modality(
                model.input_modalities,
                model.output_modalities,
                requirement.required_input_modalities,
                requirement.required_output_modalities,
            ),
            _check_contract_compatibility(),
        )
        fail_checks = tuple(c.detail for c in checks if c.verdict == "FAIL")
        overall = "EXCLUDED" if fail_checks else "KEPT"
        results.append(ModelFilterResult(model_id=model.id, checks=checks, overall=overall, exclusion_reasons=fail_checks))
    return tuple(results)
