"""Stage 04 Architecture Validation — Cost Instrumentation(§7). Production의 `call_engine_via_omniroute()`가 `usage`를 버리는 것은 Thin Caller Contract (ADC-0031/ADR-0017)를 지키기 위한 의도된 설계이지 버그가 아니다."""

import http.client
import json
import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from mvp.omniroute_engine import (  # noqa: E402
    OMNIROUTE_CHAT_COMPLETIONS_PATH,
    OMNIROUTE_DEFAULT_BASE_URL,
    OMNIROUTE_DEFAULT_MODEL,
    OMNIROUTE_DEFAULT_TIMEOUT_SECONDS,
)


def call_with_usage(prompt: str) -> tuple:
    """Production 함수를 감싸거나 대체하지 않는다 — 완전히 별도 경로다
    (§7: Thin Caller Contract 임의 변경 금지)."""
    base_url = os.environ.get("OMNIROUTE_BASE_URL", OMNIROUTE_DEFAULT_BASE_URL)
    api_key = os.environ.get("OMNIROUTE_API_KEY", "")
    model = os.environ.get("OMNIROUTE_MODEL", OMNIROUTE_DEFAULT_MODEL)
    timeout = float(os.environ.get("OMNIROUTE_TIMEOUT_SECONDS", OMNIROUTE_DEFAULT_TIMEOUT_SECONDS))

    parsed_url = urllib.parse.urlparse(base_url)
    conn_cls = http.client.HTTPSConnection if parsed_url.scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(parsed_url.hostname, parsed_url.port, timeout=timeout)
    try:
        body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        path = (parsed_url.path.rstrip("/") or "") + OMNIROUTE_CHAT_COMPLETIONS_PATH
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()
        parsed = json.loads(response.read().decode("utf-8"))
        if response.status >= 400:
            raise RuntimeError(f"OmniRoute call error (HTTP {response.status}): {parsed}")
        text = parsed["choices"][0]["message"]["content"]
        usage = parsed.get("usage")
        return text, usage
    finally:
        conn.close()


def usage_to_result_fields(usage: dict) -> dict:
    """`usage`가 `None`이면 전부 `None`(미확보)을 유지한다 — 0으로 치환하지 않는다."""
    if not usage:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    return {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
