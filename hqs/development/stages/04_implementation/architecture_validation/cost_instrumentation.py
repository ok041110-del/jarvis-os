"""Stage 04 Architecture Validation — Cost Instrumentation(§7 조사 결과).

`mvp/omniroute_engine.py::call_engine_via_omniroute()`는 응답 텍스트만
반환하고 OpenAI-compatible 응답의 `usage`(prompt/completion/total
tokens) 필드를 그대로 버린다 — Thin Caller Contract(`str -> str`,
ADC-0031/ADR-0017)를 그대로 유지하기 위해 의도된 설계이지, 버그가
아니다. 이 Harness는 그 Production Contract를 바꾸지 않는다 — 대신 이
파일에 **별도의, Harness 전용** 계측 함수를 둔다. Production
`call_engine_via_omniroute()`의 요청 조립 로직을 그대로 재현하되,
`usage`를 버리지 않고 함께 반환한다.

실제 OmniRoute가 없는 이 세션 환경에서도 검증 가능하도록,
`test_stage04_arch_validation_harness.py`가 stdlib `http.server`로 만든
loopback double(`test_omniroute_engine_real.py`와 동일한 방법론)로 이
함수를 실제로 호출해 `usage` 파싱을 확인한다 — 네트워크/실제 OmniRoute
없이도 검증 가능하다."""

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
    """`call_engine_via_omniroute()`와 동일한 요청을 보내되, 응답 텍스트와
    `usage` dict(없으면 `None`)를 함께 반환한다. Production 함수를
    감싸거나 대체하지 않는다 — 완전히 별도 경로다(§7: Thin Caller
    Contract 임의 변경 금지)."""
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
    """OpenAI-compatible `usage` dict를 Result Schema 필드명으로 옮긴다.
    `usage`가 `None`이면 전부 `None`(미확보)을 유지한다 — 0으로
    치환하지 않는다."""
    if not usage:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    return {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
