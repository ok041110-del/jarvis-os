"""OpenRouter Free Model Pool — 존재하는 `:free` 모델 전체를 조회해 `models` 배열에 넘길 Pool을 만든다.
Capability scoring/ranking은 하지 않는다 — 실측으로 plain chat completion 불가가 확인된 모델만 제외한다."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# 실측 확인된, plain chat completion이 구조적으로 불가능한 모델 — OpenRouter
# 자체 403 응답을 받음(추정 아님, `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §2).
_KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT = frozenset(
    {
        "thinkingmachines/inkling:free",
        "thinkingmachines/inkling-small:free",
    }
)


class ModelPoolFetchError(RuntimeError):
    pass


# 실측 확인: `models` 배열 4개 이상이면 OpenRouter가 즉시 400을 반환한다
# (공식 문서 미명시, Anthropic 호환 엔드포인트 각주만 확인 — 추정 아닌 실측 값).
MAX_MODELS_PER_REQUEST = 3


@dataclass
class ModelPool:
    model_ids: tuple[str, ...]
    excluded_known_nonfunctional: tuple[str, ...]
    fetched_from: str


def fetch_free_model_pool(*, timeout: int = 20, limit: int = MAX_MODELS_PER_REQUEST) -> ModelPool:
    """OpenRouter 응답 순서 그대로(재정렬 없음) `_KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT`만 제외한 뒤 `limit`개로 자른다."""
    request = urllib.request.Request(OPENROUTER_MODELS_URL, method="GET")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
    except OSError as exc:
        raise ModelPoolFetchError(f"OpenRouter model pool 조회 실패: {exc}") from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ModelPoolFetchError(f"OpenRouter model pool 응답이 JSON이 아니다: {exc}") from exc

    all_ids = [m["id"] for m in parsed.get("data", []) if m.get("id", "").endswith(":free")]
    excluded = [mid for mid in all_ids if mid in _KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT]
    kept = [mid for mid in all_ids if mid not in _KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT]

    return ModelPool(
        model_ids=tuple(kept[:limit]),
        excluded_known_nonfunctional=tuple(excluded),
        fetched_from=OPENROUTER_MODELS_URL,
    )
