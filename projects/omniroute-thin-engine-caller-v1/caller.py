"""OmniRoute Thin Engine Caller — 단일 OmniRoute endpoint 호출 함수.

Case A(Thin Engine Caller) 경계를 지킨다(`ADC-0031`, `ADR-0016`) — Provider/Model 선택·Routing·Fallback 판단을 하지 않는다.
"""

import http.client
import json
import os
import socket
import threading
import urllib.parse

DEFAULT_BASE_URL = "http://127.0.0.1:20128"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MODEL = "auto"
CHAT_COMPLETIONS_PATH = "/api/v1/chat/completions"


class OmniRouteCallError(Exception):
    """OmniRoute 호출 실패의 기본 예외."""


class OmniRouteAuthError(OmniRouteCallError):
    """API Key 인증 실패(HTTP 401/403)."""


class OmniRouteBudgetExceededError(OmniRouteCallError):
    """비용/요청 한도 초과(HTTP 429)."""


class OmniRouteProviderError(OmniRouteCallError):
    """OmniRoute가 Provider 호출에 실패했다고 보고함(HTTP 5xx)."""


class OmniRouteTimeoutError(OmniRouteCallError):
    """응답 시간 초과."""


class OmniRouteConnectionError(OmniRouteCallError):
    """OmniRoute endpoint에 연결할 수 없음."""


class OmniRouteCancelledError(OmniRouteCallError):
    """호출이 취소됨."""


def _build_request_body(prompt, *, model):
    """model 문자열을 그대로 옮길 뿐, 어떤 provider/model을 쓸지는 판단하지 않는다(OmniRoute의 책임)."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    return json.dumps(payload).encode("utf-8")


def _parse_response_body(status, body_bytes):
    """상태 코드를 타입이 있는 예외로 옮길 뿐 — 재시도·fallback·provider 재선택은 하지 않는다."""
    try:
        parsed = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except (ValueError, UnicodeDecodeError):
        parsed = None

    detail = parsed if parsed is not None else body_bytes[:200]

    if status in (401, 403):
        raise OmniRouteAuthError(f"HTTP {status}: {detail}")
    if status == 429:
        raise OmniRouteBudgetExceededError(f"HTTP {status}: {detail}")
    if status >= 500:
        raise OmniRouteProviderError(f"HTTP {status}: {detail}")
    if status >= 400:
        raise OmniRouteCallError(f"HTTP {status}: {detail}")

    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OmniRouteCallError(f"unexpected response shape: {detail}") from exc


def _resolve_config(base_url, api_key, model, timeout):
    return (
        base_url or os.environ.get("OMNIROUTE_BASE_URL", DEFAULT_BASE_URL),
        api_key if api_key is not None else os.environ.get("OMNIROUTE_API_KEY", ""),
        model or DEFAULT_MODEL,
        timeout or DEFAULT_TIMEOUT_SECONDS,
    )


def _do_call(prompt, *, base_url, api_key, model, timeout, handle=None):
    """`handle`이 주어지면 연결 객체를 등록해 다른 스레드가 취소할 수 있게 한다(lifecycle 지원, 라우팅 판단 아님)."""
    base_url, api_key, model, timeout = _resolve_config(base_url, api_key, model, timeout)

    parsed_url = urllib.parse.urlparse(base_url)
    conn_cls = (
        http.client.HTTPSConnection
        if parsed_url.scheme == "https"
        else http.client.HTTPConnection
    )
    conn = conn_cls(parsed_url.hostname, parsed_url.port, timeout=timeout)

    if handle is not None:
        with handle._lock:
            if handle._cancel_requested:
                conn.close()
                raise OmniRouteCancelledError("cancelled before send")
            handle._conn = conn

    try:
        body = _build_request_body(prompt, model=model)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        path = (parsed_url.path.rstrip("/") or "") + CHAT_COMPLETIONS_PATH
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()
        response_body = response.read()
        return _parse_response_body(response.status, response_body)
    except OmniRouteCallError:
        raise
    except socket.timeout as exc:
        raise OmniRouteTimeoutError(str(exc)) from exc
    except OSError as exc:
        if handle is not None and handle._cancel_requested:
            raise OmniRouteCancelledError(str(exc)) from exc
        raise OmniRouteConnectionError(str(exc)) from exc
    finally:
        conn.close()


def call_omniroute(prompt, *, base_url=None, api_key=None, model=None, timeout=None):
    """동기 호출 — Provider/Model 선택·Routing·Fallback은 전부 OmniRoute가 수행하며 이 함수는 판단하지 않는다."""
    return _do_call(prompt, base_url=base_url, api_key=api_key, model=model, timeout=timeout)


class OmniRouteCallHandle:
    """비동기 호출 하나의 lifecycle(상태 조회·취소)만 다룬다 — Provider/Model 후보를 나열·비교하지 않는다."""

    def __init__(self):
        self._lock = threading.Lock()
        self._status = "pending"
        self._result = None
        self._error = None
        self._conn = None
        self._cancel_requested = False
        self._done_event = threading.Event()
        self._thread = None

    def status(self):
        with self._lock:
            return self._status

    def cancel(self):
        """진행 중인 호출을 취소한다. 이미 끝난 호출은 취소할 수
        없다(False 반환)."""
        with self._lock:
            if self._status != "pending":
                return False
            self._cancel_requested = True
            self._status = "cancelled"
            conn = self._conn
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        self._done_event.set()
        return True

    def result(self, timeout=None):
        if not self._done_event.wait(timeout=timeout):
            raise OmniRouteTimeoutError("result() timed out waiting for completion")
        with self._lock:
            if self._status == "succeeded":
                return self._result
            if self._status == "cancelled":
                raise OmniRouteCancelledError("call was cancelled")
            raise self._error


def call_omniroute_async(prompt, *, base_url=None, api_key=None, model=None, timeout=None):
    """`call_omniroute`를 별도 스레드에서 실행하고 handle을 즉시 반환한다 — 감싸는 대상은 여전히 `call_omniroute` 하나뿐이다."""
    handle = OmniRouteCallHandle()

    def _worker():
        try:
            result = _do_call(
                prompt, base_url=base_url, api_key=api_key, model=model,
                timeout=timeout, handle=handle,
            )
            with handle._lock:
                if handle._status == "cancelled":
                    return
                handle._result = result
                handle._status = "succeeded"
        except Exception as exc:  # noqa: BLE001 - 의도적으로 모든 예외를 handle에 위임
            with handle._lock:
                if handle._status == "cancelled":
                    return
                handle._error = exc
                handle._status = "failed"
        finally:
            handle._done_event.set()

    handle._thread = threading.Thread(target=_worker, daemon=True)
    handle._thread.start()
    return handle
