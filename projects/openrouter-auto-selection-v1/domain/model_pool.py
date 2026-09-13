"""OpenRouter Free Model Pool — Stage Policy는 모델 이름을 갖지 않는다 (사용자 지시). 이 모듈이 "지금 존재하는 `:free` 모델 전체"를 조회해 `models`(OpenRouter 공식 fallback 배열 파라미터, `docs/guides/routing/ model-fallbacks.md` 실측 확인)에 그대로 넘길 Pool을 만든다.

**Capability scoring/model ranking을 하지 않는다** — 이 모듈이 하는 유일한 판단은 "이 모델이 plain chat completion 자체를 구조적으로 지원하지 않는다는 실측 Evidence가 있는가"뿐이다(순위/품질 판단 아님). 그 실측 Evidence가 없는 모델은 전부 그대로 Pool에 남긴다 — 추정하지 않는다(사용자 지시).
"""

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
    """`/api/v1/models` 조회 자체가 실패했을 때(단일 예외, 기존 Adapter
    Contract와 동일 패턴)."""


# 실측 확인: `models` 배열 4개 이상이면 OpenRouter가 즉시 400을 반환한다
# (공식 문서 미명시, Anthropic 호환 엔드포인트 각주만 확인 — 추정 아닌 실측 값).
MAX_MODELS_PER_REQUEST = 3


@dataclass
class ModelPool:
    model_ids: tuple[str, ...]
    excluded_known_nonfunctional: tuple[str, ...]
    fetched_from: str


def fetch_free_model_pool(*, timeout: int = 20, limit: int = MAX_MODELS_PER_REQUEST) -> ModelPool:
    """`:free`로 끝나는 모델 id를 OpenRouter가 반환한 순서 그대로 가져와, 앞에서부터 `limit`개만 자른다(재정렬·순위화 없음 — OpenRouter 자신의 응답 순서를 그대로 따를 뿐이다) — `_KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT` 만 먼저 제외한 뒤 자른다. `limit`의 기본값(`MAX_MODELS_PER_REQUEST=3`)은 OpenRouter `models` 배열의 실측 상한이다(추정 아님)."""
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
