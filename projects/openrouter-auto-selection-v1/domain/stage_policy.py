"""Stage Policy — 모델 이름을 갖지 않는다(사용자 지시 §4). 각 Stage가
필요로 하는 것(무료 여부/Contract/예산/timeout/재시도 정책)만 선언한다.
Capability scoring/model ranking은 v1에서 구현하지 않는다."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import STAGE_CONTRACTS


@dataclass
class RetryPolicy:
    """최대 1회 bounded retry(사용자 지시 §6). 실패 유형별로 재시도
    가능 여부가 다르다 — `classify_failure()`(auto_selection_client.py)가
    이 표를 그대로 따른다."""

    max_retries: int = 1
    exclude_failed_model_from_retry_pool: bool = True  # Contract/malformed 실패 시, 재시도에서 같은 모델을 다시 뽑지 않도록


@dataclass
class StagePolicy:
    stage: str
    free_only: bool
    output_contract: Callable  # str -> ContractResult, 재사용 가능한 기존 parser/validator
    token_budget: int  # 참고 값(이전 Evidence 인용) — 이 값이 "최적값"이라고 주장하지 않는다
    timeout_seconds: int
    retry_policy: RetryPolicy
    token_budget_source: str  # 이 예산 값의 출처(Evidence 인용, 추정 아님을 명시)


# 각 token_budget은 이전 세션 실측 Evidence를 그대로 인용한 값이다 — 이
# 정책이 "최적값"을 선언하지 않는다(사용자 지시 §4 마지막 문단).
STAGE_POLICIES: dict[str, StagePolicy] = {
    "stage01": StagePolicy(
        stage="stage01",
        free_only=True,
        output_contract=STAGE_CONTRACTS["stage01"],
        token_budget=1200,
        timeout_seconds=90,
        retry_policy=RetryPolicy(),
        token_budget_source="OPENROUTER-STAGE-MODEL-SELECTION-0001.md §3.1(stage01_prompt.txt max_tokens)",
    ),
    "stage02": StagePolicy(
        stage="stage02",
        free_only=True,
        output_contract=STAGE_CONTRACTS["stage02"],
        token_budget=1200,
        timeout_seconds=90,
        retry_policy=RetryPolicy(),
        token_budget_source="OPENROUTER-STAGE-MODEL-SELECTION-0001.md §3.2 초기값(일부 모델은 3000까지 필요했던 사례 있음, §3.2 재확인 — 이 정책은 1200을 baseline으로만 사용)",
    ),
    "stage03": StagePolicy(
        stage="stage03",
        free_only=True,
        output_contract=STAGE_CONTRACTS["stage03"],
        token_budget=1800,
        timeout_seconds=120,
        retry_policy=RetryPolicy(),
        token_budget_source="OPENROUTER-STAGE-MODEL-SELECTION-0001.md §3.3(stage03_prompt.txt max_tokens)",
    ),
    "stage04": StagePolicy(
        stage="stage04",
        free_only=True,
        output_contract=STAGE_CONTRACTS["stage04"],
        token_budget=2200,
        timeout_seconds=120,
        retry_policy=RetryPolicy(),
        token_budget_source="OPENROUTER-STAGE-MODEL-SELECTION-0001.md §3.4(nex-n2.5-mini 반복 실행 max_tokens)",
    ),
    "stage05_review": StagePolicy(
        stage="stage05_review",
        free_only=True,
        output_contract=STAGE_CONTRACTS["stage05_review"],
        token_budget=1800,
        timeout_seconds=90,
        retry_policy=RetryPolicy(),
        token_budget_source="STAGE05-REVIEW-LLM-REAL-EXECUTION-EVIDENCE-0001.md §2(공식 3회 실행 설정) — 그 Evidence 자체가 1800에서 2/3 실패를 관찰했음을 이 정책도 알고 있다(§9 그대로 인용, 최적값이라고 주장하지 않음)",
    ),
}
