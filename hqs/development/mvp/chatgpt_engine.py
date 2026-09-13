"""ChatGPT를 통한 단일 Engine 호출 함수 — Multi-Engine Architecture의 Reasoning/Review 측 Engine
(`ADR-0024`). `omniroute_engine.py::call_engine_via_omniroute()`와 동일한 외부 계약(`str -> str`,
실패 시 `RuntimeError`)을 따른다."""

import json
import os
import socket
import urllib.error
import urllib.request

CHATGPT_DEFAULT_BASE_URL = "https://api.openai.com"
CHATGPT_DEFAULT_MODEL = "gpt-4o"
CHATGPT_DEFAULT_TIMEOUT_SECONDS = 180
CHATGPT_CHAT_COMPLETIONS_PATH = "/v1/chat/completions"


def _resolve_config():
    base_url = os.environ.get("CHATGPT_BASE_URL", CHATGPT_DEFAULT_BASE_URL)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("CHATGPT_MODEL", CHATGPT_DEFAULT_MODEL)
    timeout = float(os.environ.get("CHATGPT_TIMEOUT_SECONDS", CHATGPT_DEFAULT_TIMEOUT_SECONDS))
    return base_url, api_key, model, timeout


def _parse_response(status, body_bytes):
    try:
        parsed = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except (ValueError, UnicodeDecodeError):
        parsed = None
    detail = parsed if parsed is not None else body_bytes[:200]

    if status in (401, 403):
        raise RuntimeError(f"ChatGPT auth error (HTTP {status}): {detail}")
    if status == 429:
        raise RuntimeError(f"ChatGPT rate limit exceeded (HTTP {status}): {detail}")
    if status >= 500:
        raise RuntimeError(f"ChatGPT provider error (HTTP {status}): {detail}")
    if status >= 400:
        raise RuntimeError(f"ChatGPT call error (HTTP {status}): {detail}")

    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"ChatGPT unexpected response shape: {detail}") from exc


def call_engine_via_chatgpt(prompt: str) -> str:
    """단일 ChatGPT 호출 지점(ENGINE-CONNECT-CHATGPT-0001).
    `urllib.request`를 사용한다 — Claude Environment의 `HTTPS_PROXY`를 자동으로 경유하기 위함이다
    (`http.client.HTTPSConnection`은 이 환경변수를 읽지 않아 Agent Egress Proxy를 우회해 버린다)."""
    base_url, api_key, model, timeout = _resolve_config()
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    url = base_url.rstrip("/") + CHATGPT_CHAT_COMPLETIONS_PATH
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    # 매 호출마다 opener를 새로 만든다 — 전역 opener는 최초 호출 시점의
    # getproxies()를 캐싱해, 이후 HTTPS_PROXY 변경을 반영하지 못하기 때문이다.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            return _parse_response(response.status, response.read())
    except RuntimeError:
        raise
    except urllib.error.HTTPError as exc:
        return _parse_response(exc.code, exc.read())
    except socket.timeout as exc:
        raise RuntimeError(f"ChatGPT call timed out after {timeout}s: {exc}") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, socket.timeout):
            raise RuntimeError(f"ChatGPT call timed out after {timeout}s: {exc.reason}") from exc
        raise RuntimeError(f"ChatGPT connection failed: {exc.reason}") from exc
    except OSError as exc:
        raise RuntimeError(f"ChatGPT connection failed: {exc}") from exc
