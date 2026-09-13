"""OpenRouter Experimental Validation Adapter — **Production Stage Engine
Routing과 무관하다.** `domain/review.py`의 `engine_call: Callable[[str],
str]` Contract(기존 `mvp/chatgpt_engine.py`/`mvp/engine.py`와 동일한
`str -> str`, 단일 예외)를 그대로 만족하는 어댑터 하나만 제공한다 — 새
Gateway/Router/Provider Architecture를 만들지 않는다.

API Key/Credential은 이 파일이 탐색하거나 다루지 않는다 — 이 세션의
Egress Proxy가 `openrouter.ai` 요청에 자동으로 유효한 Credential을
주입한다(이전 세션 `OPENROUTER-VALIDATION-0001.md` §8.2가 이미 실측
확인한 메커니즘 — 클라이언트가 보낸 Authorization 헤더 값과 무관하게
동일하게 인증됨). 이 파일은 Authorization 헤더를 설정하지 않는다."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterCallError(RuntimeError):
    """OpenRouter 호출 실패(HTTP 오류, timeout, 응답 형태 불일치 등) — 단일
    예외 타입만 노출한다(기존 Engine Adapter Contract와 동일 패턴)."""


def make_openrouter_engine_call(model: str, *, max_tokens: int = 1500, timeout: int = 90):
    """`str -> str` Contract를 만족하는 callable을 반환한다. `model`은
    호출자가 명시적으로 고정한다(자동 `openrouter/free` 라우팅을 쓰지
    않는다, 이전 세션 관례와 동일)."""

    def call(prompt: str) -> str:
        body = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.2,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            OPENROUTER_CHAT_COMPLETIONS_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler())
            with opener.open(request, timeout=timeout) as response:
                raw = response.read()
                status = response.status
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            status = exc.code
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise OpenRouterCallError(f"OpenRouter connection failed: {exc}") from exc

        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise OpenRouterCallError(f"OpenRouter response is not valid JSON (status {status}): {exc}") from exc

        if status != 200:
            error_message = parsed.get("error", {}).get("message", str(parsed)[:200])
            raise OpenRouterCallError(f"OpenRouter call error (HTTP {status}): {error_message}")

        try:
            return parsed["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterCallError(f"OpenRouter unexpected response shape: {parsed}") from exc

    return call


def timed_call(engine_call, prompt: str) -> tuple[str, float]:
    """`engine_call(prompt)`의 실제 API latency(ms)를 함께 반환한다 — Review
    Validator 자체의 `latency_ms`(prompt 조립 포함)와 API 호출만의 latency를
    구분하기 위함."""
    start = time.perf_counter()
    result = engine_call(prompt)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms
