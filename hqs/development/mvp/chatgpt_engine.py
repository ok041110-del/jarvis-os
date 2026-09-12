"""ChatGPT를 통한 단일 Engine 호출 함수 — Multi-Engine Architecture의
Reasoning/Review 측 Engine(`docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`).

`omniroute_engine.py::call_engine_via_omniroute()`와 동일한 형태(단일
함수, `str -> str`, 실패 시 단일 예외 `RuntimeError`)를 그대로 따른다 —
`ADR-0024` §Contract Impact가 확정한 대로 새 Request/Result 객체를
만들지 않는다. Provider/Model 선택, Retry, Fallback, Policy 판정은
이 모듈에 없다 — 이 모듈은 OpenAI Chat Completions 호환 endpoint
하나를 호출하는 단일 함수일 뿐이다(`IMPLEMENTATION_RULES.md` 15·16·
17·21행 Multi-Engine Scoped 예외 범위 안, 동일 Case A 두 조건 유지).

API Key는 `OPENAI_API_KEY` 환경변수에서만 읽는다 — 코드에 하드코딩하지
않는다."""

import http.client
import json
import os
import socket
import urllib.parse

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
    """ChatGPT 응답을 응답 텍스트 또는 `RuntimeError`로 옮긴다 —
    `call_engine_via_omniroute._parse_response`와 동일 구조. 재시도·
    fallback·provider 재선택은 하지 않는다."""
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
    """단일 ChatGPT 호출 지점(ENGINE-CONNECT-CHATGPT-0001). `call_engine()`/
    `call_engine_via_omniroute()`와 동일한 외부 계약(`str -> str`, 실패 시
    `RuntimeError`)을 따른다 — 호출부가 이미 `except Exception`으로 잡아
    `Engine call failed: {exc}`로 구조화하므로 여기서 실패를 삼키지 않는다."""
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
        path = (parsed_url.path.rstrip("/") or "") + CHATGPT_CHAT_COMPLETIONS_PATH
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()
        response_body = response.read()
        return _parse_response(response.status, response_body)
    except RuntimeError:
        raise
    except socket.timeout as exc:
        raise RuntimeError(f"ChatGPT call timed out after {timeout}s: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"ChatGPT connection failed: {exc}") from exc
    finally:
        conn.close()
