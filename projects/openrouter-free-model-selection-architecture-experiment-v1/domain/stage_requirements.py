"""Stage 01~05의 "현재 요구조건"을 Deterministic Filter가 판정할 수
있는 형태로 정리한다. 모델명은 어디에도 없다(ADR-0026 §5 Stage
Requirement 소유자 = Stage, 모델명 없음).

기존 `openrouter-auto-selection-v1` 프로젝트의 `STAGE_POLICIES`
(token_budget/output_contract)와 `fixtures`(실제 프롬프트)를
**읽기 전용으로 재사용**한다 — 이 실험을 위해 새로 발명하지 않는다."""

from __future__ import annotations

from dataclasses import dataclass

from ._sibling_import import load_sibling_domain

_sibling = load_sibling_domain()
REPO_ROOT = _sibling.fixtures.REPO_ROOT
STAGE01_PROMPT = _sibling.fixtures.STAGE01_PROMPT
STAGE02_PROMPT = _sibling.fixtures.STAGE02_PROMPT
STAGE03_PROMPT = _sibling.fixtures.STAGE03_PROMPT
TARGET_FUNCTION_NAME = _sibling.fixtures.TARGET_FUNCTION_NAME
build_stage04_prompt = _sibling.fixtures.build_stage04_prompt
build_stage05_review_prompt = _sibling.fixtures.build_stage05_review_prompt
STAGE_POLICIES = _sibling.stage_policy.STAGE_POLICIES


@dataclass
class StageRequirement:
    stage: str
    prompt: str
    required_input_modalities: tuple[str, ...]  # 모델의 input_modalities가 이 집합을 모두 포함해야 함
    required_output_modalities: tuple[str, ...]
    min_context_tokens: int  # 추정치(아래 설명) — Hard Filter가 판정 가능한 유일한 "capability" 대용치
    min_context_tokens_basis: str  # 추정 근거를 항상 기록(추측 은폐 금지)
    output_contract: object  # str -> ContractResult (STAGE_CONTRACTS 재사용)
    token_budget: int
    target_function_name: str | None = None


def _estimate_prompt_tokens(prompt: str) -> int:
    """정확한 tokenizer 없이(모델마다 tokenizer가 다름, 사전에 알 수
    없음) **문자 수 / 4를 보수적 근사치**로 쓴다 — 이는 영어 텍스트의
    일반적인 근사 비율이며, 실제 tokenizer와 다를 수 있다는 한계를
    Evidence에 명시한다(추측을 감추지 않는다)."""
    return len(prompt) // 4


def build_stage_requirements() -> dict[str, StageRequirement]:
    stage04_prompt = build_stage04_prompt(REPO_ROOT)
    stage05_prompt = build_stage05_review_prompt(REPO_ROOT)

    prompts = {
        "stage01": STAGE01_PROMPT,
        "stage02": STAGE02_PROMPT,
        "stage03": STAGE03_PROMPT,
        "stage04": stage04_prompt,
        "stage05_review": stage05_prompt,
    }

    requirements: dict[str, StageRequirement] = {}
    for stage_key, prompt in prompts.items():
        policy = STAGE_POLICIES[stage_key]
        input_tokens_estimate = _estimate_prompt_tokens(prompt)
        # 안전 여유 20%를 더한다(추정치이므로 경계선에서 오탐 감소 목적) — "최적값"이 아니라 보수적 임계값임을 명시.
        min_context = int((input_tokens_estimate + policy.token_budget) * 1.2)
        requirements[stage_key] = StageRequirement(
            stage=stage_key,
            prompt=prompt,
            required_input_modalities=("text",),
            required_output_modalities=("text",),
            min_context_tokens=min_context,
            min_context_tokens_basis=(
                f"len(prompt)//4={input_tokens_estimate} + token_budget={policy.token_budget}, "
                f"x1.2 안전 여유 (출처: 이 실험의 문자수 근사, 정확한 tokenizer 미사용 — 추정치임을 명시)"
            ),
            output_contract=policy.output_contract,
            token_budget=policy.token_budget,
            target_function_name=TARGET_FUNCTION_NAME if stage_key == "stage04" else None,
        )
    return requirements
