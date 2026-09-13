"""ADR-0026 §Free Pool — OpenRouter가 실제 제공하는 `:free` 모델
목록을 메타데이터와 함께 그대로 조회한다. 재정렬·필터링을 하지
않는다(필터링은 `deterministic_filter.py`의 책임, 이 모듈은 §1
Free Pool 단계까지만 담당). API Key/Authorization 값은 이 모듈이
설정하지 않는다 — Egress Proxy 자동 인증만 사용."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


class FreePoolFetchError(RuntimeError):
    """`/api/v1/models` 조회 자체가 실패했을 때(단일 예외)."""


@dataclass
class FreeModelMetadata:
    """Deterministic Filter가 판정에 쓰는 필드만 추출한다 — 전체 원본
    JSON도 `raw`에 보존해 NOT DETERMINED 판단의 근거를 남긴다."""

    id: str
    context_length: int | None
    input_modalities: tuple[str, ...]
    output_modalities: tuple[str, ...]
    supported_parameters: tuple[str, ...]
    raw: dict = field(repr=False)


@dataclass
class FreePool:
    models: tuple[FreeModelMetadata, ...]  # OpenRouter 응답 순서 그대로(재정렬 없음)
    fetched_from: str
    fetched_count_total: int  # `:free` 여부와 무관한 전체 모델 수(참고용)


def fetch_free_pool(*, timeout: int = 30) -> FreePool:
    """`:free`로 끝나는 모델을 OpenRouter가 반환한 순서 그대로 가져온다.
    재정렬·품질 판단 없음 — Free 여부만으로 거른다(이것이 ADR-0026의
    "Free Pool" 단계 그 자체다, Deterministic Filter는 별도 단계)."""
    request = urllib.request.Request(OPENROUTER_MODELS_URL, method="GET")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
    except OSError as exc:
        raise FreePoolFetchError(f"OpenRouter free pool 조회 실패: {exc}") from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise FreePoolFetchError(f"OpenRouter free pool 응답이 JSON이 아니다: {exc}") from exc

    all_models = parsed.get("data", [])
    free_models = [m for m in all_models if m.get("id", "").endswith(":free")]

    metadata = tuple(
        FreeModelMetadata(
            id=m["id"],
            context_length=m.get("context_length"),
            input_modalities=tuple((m.get("architecture") or {}).get("input_modalities") or ()),
            output_modalities=tuple((m.get("architecture") or {}).get("output_modalities") or ()),
            supported_parameters=tuple(m.get("supported_parameters") or ()),
            raw=m,
        )
        for m in free_models
    )

    return FreePool(models=metadata, fetched_from=OPENROUTER_MODELS_URL, fetched_count_total=len(all_models))
