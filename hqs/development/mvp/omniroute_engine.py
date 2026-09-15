"""OmniRoute를 통한 단일 Engine 호출 함수 — Thin Engine Caller(Case A, `ADC-0031` §Decision, `ADR-0017` §2·§6): 단일 함수가 OmniRoute OpenAI-compatible endpoint 하나만 호출하고, Provider/Model 선택·Retry·Fallback은 OmniRoute에 위임한다."""

import http.client
import json
import os
import socket
import urllib.parse

OMNIROUTE_DEFAULT_BASE_URL = "http://127.0.0.1:20128"
OMNIROUTE_DEFAULT_MODEL = "auto"
OMNIROUTE_DEFAULT_TIMEOUT_SECONDS = 180
OMNIROUTE_CHAT_COMPLETIONS_PATH = "/api/v1/chat/completions"


def _resolve_config():
    base_url = os.environ.get("OMNIROUTE_BASE_URL", OMNIROUTE_DEFAULT_BASE_URL)
    api_key = os.environ.get("OMNIROUTE_API_KEY", "")
    model = os.environ.get("OMNIROUTE_MODEL", OMNIROUTE_DEFAULT_MODEL)
    timeout = float(os.environ.get("OMNIROUTE_TIMEOUT_SECONDS", OMNIROUTE_DEFAULT_TIMEOUT_SECONDS))
    return base_url, api_key, model, timeout


def _parse_response(status, body_bytes):
    try:
        parsed = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except (ValueError, UnicodeDecodeError):
        parsed = None
    detail = parsed if parsed is not None else body_bytes[:200]

    if status in (401, 403):
        raise RuntimeError(f"OmniRoute auth error (HTTP {status}): {detail}")
    if status == 429:
        raise RuntimeError(f"OmniRoute budget/rate limit exceeded (HTTP {status}): {detail}")
    if status >= 500:
        raise RuntimeError(f"OmniRoute provider error (HTTP {status}): {detail}")
    if status >= 400:
        raise RuntimeError(f"OmniRoute call error (HTTP {status}): {detail}")

    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"OmniRoute unexpected response shape: {detail}") from exc


def call_engine_via_omniroute(prompt: str) -> str:
    """단일 OmniRoute 호출 지점(ENGINE-CONNECT-OMNIROUTE-0001). Production에서 쓰려면 운영자가 해당 OmniRoute 인스턴스에 `blockedProviders`/`REQUIRE_API_KEY`를 사전 구성해야 한다(`EVIDENCE-0003`~`EVIDENCE-0005`의 zero-config egress 방어 — 이 함수는 대신하지 않는다)."""
    base_url, api_key, model, timeout = _resolve_config()
    parsed_url = urllib.parse.urlparse(base_url)
    conn_cls = (
        http.client.HTTPSConnection
        if parsed_url.scheme == "https"
        else http.client.HTTPConnection
    )
    conn = conn_cls(parsed_url.hostname, parsed_url.port, timeout=timeout)
    try:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        path = (parsed_url.path.rstrip("/") or "") + OMNIROUTE_CHAT_COMPLETIONS_PATH
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()
        response_body = response.read()
        return _parse_response(response.status, response_body)
    except RuntimeError:
        raise
    except socket.timeout as exc:
        raise RuntimeError(f"OmniRoute call timed out after {timeout}s: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"OmniRoute connection failed: {exc}") from exc
    finally:
        conn.close()
