"""OmniRoute를 통한 단일 Engine 호출 함수 — Thin Engine Caller(Case A).

`docs/architecture/core/ADC-0031-omniroute-thin-engine-caller-boundary.md`
§Q1·§Decision, `docs/architecture/core/ADR-0017-omniroute-production-adoption-final-review.md`
§2·§6이 확정한 범위 안에서만 존재한다: 단일 함수가 OmniRoute
OpenAI-compatible endpoint 하나만 호출하고, request/response 변환과
호출 실패의 단일 예외(`RuntimeError`) 전달만 담당한다. Provider/Model
선택, Routing, Fallback, Budget/Policy 판정은 전부 OmniRoute 책임이며
이 모듈에는 없다(`ADR-0017` §2.3 — 이 네 가지는 OmniRoute 자체 설정에
위치한다).

**`engine.py::call_engine()`과의 관계(중요, RT-0001 Candidate 2
관련)**: 이 모듈은 `engine.py`를 import하지 않고, `engine.py`도 이
모듈을 import하지 않는다 — 완전히 독립된 두 개의 단일-Engine 호출
지점이다. `call_engine()`의 시그니처·구현·호출부(`agents/*.py`,
`workflow_ast_context.py`)는 이 모듈 추가로 **한 글자도 바뀌지
않았다.** `docs/governance/rt/RT-0001.md` Candidate 2의 Trigger는
"`call_engine()` 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로
하게 됨"으로 명시적으로 좁혀져 있다 — `call_engine()`의 기존 호출
지점(`agents/backend.py`·`agents/design.py`·`agents/qa.py`·
`agents/requirements.py`·`workflow_ast_context.py`) 중 어느 것도 이
모듈을 참조하지 않으므로 그 Trigger는 발생하지 않는다.
"""

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
    """OmniRoute 응답을 응답 텍스트 또는 `RuntimeError`로 옮긴다 — 이
    함수는 어떤 재시도·fallback·provider 재선택도 수행하지 않는다.
    `call_engine()`과 동일하게 단일 예외 타입(`RuntimeError`)만
    externally 노출한다(호출부의 `except Exception` 구조화와 정합)."""
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
    """단일 OmniRoute 호출 지점(ENGINE-CONNECT-OMNIROUTE-0001). `call_engine()`과
    동일한 외부 계약(`str -> str`, 실패 시 `RuntimeError`)을 따른다 —
    호출부가 이미 `except Exception`으로 잡아 `Engine call failed:
    {exc}`로 구조화하므로 여기서 실패를 삼키지 않는다.

    Provider/Model 선택은 `model`(기본값 `"auto"`, `OMNIROUTE_MODEL`로
    override 가능)로 OmniRoute에 그대로 위임한다 — 이 함수는 어떤
    provider/model도 직접 고르지 않는다. Production에서 이 함수를
    실제로 사용하려면, 운영자가 그 OmniRoute 인스턴스에
    `blockedProviders`/`REQUIRE_API_KEY`를 사전에 구성해야 한다
    (`docs/architecture/core/EVIDENCE-0003`~`EVIDENCE-0005`가 식별한
    zero-config egress 방어 — 이 함수는 그 설정을 대신하지 않는다)."""
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
