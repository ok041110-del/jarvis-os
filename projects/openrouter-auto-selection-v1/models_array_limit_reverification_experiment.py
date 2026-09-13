"""`models` 배열 상한(3개) 재검증 — 사용자 지시.

기록 대상: HTTP status, error body만(사용자 지시 §5·§6). API Key/ Authorization 값은 절대 출력하지 않는다(사용자 지시 §6, 이 파일은 Authorization 헤더 자체를 설정하지 않는다 — Egress Proxy 자동 주입만 사용).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.model_pool import fetch_free_model_pool  # noqa: E402

CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
MINIMAL_PROMPT = "Reply with the single word: ok"


def _raw_models_call(model_ids: list[str], *, use_fallbacks_field: bool = False) -> dict:
    """`models` 필드(또는 대조군으로 `fallbacks` 필드)만 넣은 최소 request body로 1회 호출한다. 재시도/Contract 판정 없음 — 순수 HTTP status/error body 관찰만이 목적이다."""
    field_name = "fallbacks" if use_fallbacks_field else "models"
    payload = {
        field_name: model_ids,
        "messages": [{"role": "user", "content": MINIMAL_PROMPT}],
        "max_tokens": 10,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        CHAT_COMPLETIONS_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    try:
        with opener.open(request, timeout=30) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "request_field": field_name,
            "request_model_count": len(model_ids),
            "http_status": None,
            "connection_error": str(exc),
            "error_body": None,
        }

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        parsed = None

    error_body = None
    if parsed is not None and "error" in parsed:
        error_body = parsed["error"]
    elif status is not None and status >= 400:
        error_body = raw.decode("utf-8", errors="replace")[:500]

    return {
        "request_field": field_name,
        "request_model_count": len(model_ids),
        "http_status": status,
        "connection_error": None,
        "error_body": error_body,
    }


def main() -> dict:
    pool = fetch_free_model_pool(limit=10)  # 5개 실험을 위해 이번만 상한을 넉넉히 조회(:free 목록 자체 조회 — 요청 상한과 무관)
    if len(pool.model_ids) < 5:
        raise RuntimeError(f"실험에 5개 모델이 필요하지만 Pool에 {len(pool.model_ids)}개뿐이다 — 재실행 필요")

    results = {"models_field": [], "fallbacks_field_control": []}

    for n in (1, 2, 3, 4, 5):
        subset = list(pool.model_ids[:n])
        result = _raw_models_call(subset, use_fallbacks_field=False)
        print(f"[models n={n}] http_status={result['http_status']} error={result['error_body']}", file=sys.stderr)
        results["models_field"].append(result)

    # 대조군: 공식 문서상 `fallbacks`는 Chat Completions 엔드포인트 파라미터가
    # 아니다 — 이 엔드포인트에 `fallbacks`를 보내면 어떻게 되는지 1회만 관찰
    # (models와 fallbacks가 서로 다른 필드임을 실측으로도 구분하기 위함).
    control = _raw_models_call(list(pool.model_ids[:2]), use_fallbacks_field=True)
    print(f"[fallbacks(control) n=2] http_status={control['http_status']} error={control['error_body']}", file=sys.stderr)
    results["fallbacks_field_control"].append(control)

    results["pool_model_ids_used"] = list(pool.model_ids[:5])
    return results


if __name__ == "__main__":
    output = main()
    with open("/tmp/models_array_limit_reverification_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))
