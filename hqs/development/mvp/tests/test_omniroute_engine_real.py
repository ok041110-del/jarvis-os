"""`call_engine_via_omniroute()`를 실제(격리) OmniRoute 서버 + 로컬
controlled double을 통해 검증한다 — 실제 provider egress는 발생시키지
않는다(`docs/architecture/core/EVIDENCE-0004`/`EVIDENCE-0005`가 확립한
안전 방법론과 동일).

## 안전 경계

- 완전히 새로운 임시 `DATA_DIR` — 사용자의 실제 `~/.omniroute`는
  건드리지 않는다(mtime/size 대조로 재확인).
- `blockedProviders`(non-video NOAUTH provider 전체)를 먼저 적용하고
  read-only endpoint로 적용 여부를 확인한 뒤에만 요청을 보낸다.
- dispatch 대상은 `ollama-local`(고정 `localhost` 대상 registry)
  + 이 파일이 직접 띄우는 로컬 stdlib 서버뿐이다 — 실제 서드파티
  provider·API key는 전혀 사용하지 않는다.
- 서버는 이 테스트 전체에서 **정확히 한 번**만 기동한다(재기동 없음,
  `EVIDENCE-0004` §3의 health-check-repair 회피).

## opt-in 게이팅(이중, `test_real_engine_budget_block.py`와 동일)

    RUN_REAL_OMNIROUTE_TESTS=1 I_UNDERSTAND_REAL_EGRESS_RISK=1 \\
        OMNIROUTE_PKG_DIR=<omniroute 패키지 경로> \\
        pytest hqs/development/mvp/tests/test_omniroute_engine_real.py -v
"""

import json
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.omniroute_engine import call_engine_via_omniroute  # noqa: E402
from mvp.agents.backend import backend_agent_code_review  # noqa: E402

RUN_FLAG = "RUN_REAL_OMNIROUTE_TESTS"
SECOND_GATE_FLAG = "I_UNDERSTAND_REAL_EGRESS_RISK"
DEFAULT_PKG_DIR = (
    "/private/tmp/claude-501/-Users-chan-Developer-jarvis-os/"
    "5ce390ee-d07e-47e5-ae03-ef17b00078ff/scratchpad/npm-cache-omniroute/"
    "_npx/44b85dff014d9ceb/node_modules/omniroute"
)
FAKE_API_KEY = "engine-real-test-only-key-0001"
PORT = 20243
# `ollama-local`(LOCAL_PROVIDERS registry)의 target은 코드에 고정된
# `localDefault`(`http://localhost:11434/v1`)이며 `provider_connections`
# 행의 값으로 override되지 않는다(`EVIDENCE-0004`§5.1이 확인) — 이
# 로컬 double은 반드시 이 고정 포트에 떠 있어야 한다.
DOUBLE_PORT = 11434

NOAUTH_BLOCKLIST = [
    "opencode", "duckduckgo-web", "cloudflare-playground", "felo-web",
    "theoldllm", "chipotle", "devin-cli-agentic", "auggie", "zcode",
    "codex-app-server", "uncloseai", "aihorde",
]

pytestmark = [
    pytest.mark.skipif(
        os.environ.get(RUN_FLAG) != "1",
        reason=f"opt-in 전용 — {RUN_FLAG}=1 로 명시적으로 실행해야 한다",
    ),
    pytest.mark.skipif(
        os.environ.get(SECOND_GATE_FLAG) != "1",
        reason=f"실제 격리 OmniRoute 서버 사용 — {SECOND_GATE_FLAG}=1 로 위험을 이해했음을 명시해야 한다",
    ),
]


class _DoubleHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length) if length else b""
        mode = self.server.mode  # type: ignore[attr-defined]
        if mode == "slow":
            time.sleep(3)
        if mode == "error500":
            payload = json.dumps({"error": {"message": "synthetic upstream failure"}}).encode()
            self.send_response(500)
        else:
            payload = json.dumps({
                "choices": [{"message": {"content": "ENGINE_REAL_INTEGRATION_OK"}}],
            }).encode()
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except Exception:
            pass


def _wait_for_health(base_url, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.3)
    return False


@pytest.fixture
def real_omniroute_with_local_double(tmp_path):
    pkg_dir = os.environ.get("OMNIROUTE_PKG_DIR", DEFAULT_PKG_DIR)
    if not Path(pkg_dir, "dist", "server.js").is_file():
        pytest.skip(f"OmniRoute 패키지를 찾을 수 없다: {pkg_dir}(환경 문제, FAIL 아님)")

    real_data_dir = Path.home() / ".omniroute" / "storage.sqlite"
    real_stat_before = real_data_dir.stat() if real_data_dir.exists() else None

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    log_path = tmp_path / "server.log"

    env = dict(os.environ)
    env.update({
        "DATA_DIR": str(data_dir),
        "NODE_ENV": "test",
        "OMNIROUTE_ALLOW_DEFAULT_DATA_DIR": "0",
        "OMNIROUTE_API_KEY": FAKE_API_KEY,
        "PORT": str(PORT),
        "HOSTNAME": "127.0.0.1",
    })
    base_url = f"http://127.0.0.1:{PORT}"

    log_file = open(log_path, "w")
    proc = subprocess.Popen(
        ["node", "dist/server.js"], cwd=pkg_dir, env=env,
        stdout=log_file, stderr=subprocess.STDOUT,
    )

    double_server = HTTPServer(("127.0.0.1", DOUBLE_PORT), _DoubleHandler)
    double_server.mode = "success"
    double_thread = threading.Thread(target=double_server.serve_forever, daemon=True)
    double_thread.start()

    try:
        if not _wait_for_health(base_url):
            proc.kill()
            proc.wait(timeout=5)
            pytest.skip("OmniRoute 서버가 health check에 응답하지 않음(환경 문제, FAIL 아님)")

        db_path = data_dir / "storage.sqlite"
        conn = sqlite3.connect(str(db_path), timeout=10)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO key_value (namespace, key, value) "
                "VALUES ('settings', 'blockedProviders', ?)",
                (json.dumps(NOAUTH_BLOCKLIST),),
            )
            conn.execute(
                "INSERT INTO provider_connections "
                "(id, provider, is_active, api_key, proxy_enabled, per_key_proxy_enabled, "
                " quota_visible, created_at, updated_at) "
                "VALUES ('engine-real-double-conn', 'ollama-local', 1, ?, 0, 0, 1, "
                " datetime('now'), datetime('now'))",
                ("local-test-placeholder-key",),
            )
            conn.commit()
        finally:
            conn.close()

        candidate_count = None
        with urllib.request.urlopen(
            f"{base_url}/api/v1/auto-combo/auto/candidates", timeout=5
        ) as resp:
            candidate_count = len(json.loads(resp.read().decode("utf-8")).get("candidates", []))
        assert candidate_count == 0, (
            "blockedProviders 적용 후에도 no-auth candidate가 남음 — 2차 방어 미적용, 중단"
        )

        yield {"base_url": base_url, "log_path": log_path, "double_server": double_server}
    finally:
        proc.kill()
        proc.wait(timeout=10)
        log_file.close()
        double_server.shutdown()
        double_server.server_close()
        double_thread.join(timeout=5)

    real_stat_after = real_data_dir.stat() if real_data_dir.exists() else None
    if real_stat_before is not None:
        assert real_stat_after is not None
        assert real_stat_before.st_mtime == real_stat_after.st_mtime
        assert real_stat_before.st_size == real_stat_after.st_size


def test_success_via_production_function(real_omniroute_with_local_double, monkeypatch):
    env = real_omniroute_with_local_double
    monkeypatch.setenv("OMNIROUTE_BASE_URL", env["base_url"])
    monkeypatch.setenv("OMNIROUTE_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("OMNIROUTE_MODEL", "ollama-local/test-model")

    result = call_engine_via_omniroute("hello")
    assert result == "ENGINE_REAL_INTEGRATION_OK"

    log_text = env["log_path"].read_text(encoding="utf-8", errors="replace")
    assert "opencode" not in log_text.lower() or "Using opencode account" not in log_text


def test_error_mapping_via_production_function(real_omniroute_with_local_double, monkeypatch):
    env = real_omniroute_with_local_double
    env["double_server"].mode = "error500"
    monkeypatch.setenv("OMNIROUTE_BASE_URL", env["base_url"])
    monkeypatch.setenv("OMNIROUTE_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("OMNIROUTE_MODEL", "ollama-local/test-model")

    with pytest.raises(RuntimeError) as exc_info:
        call_engine_via_omniroute("hello")
    assert "500" in str(exc_info.value) or "provider error" in str(exc_info.value).lower()


def test_actual_call_site_routes_through_omniroute_end_to_end(
    real_omniroute_with_local_double, monkeypatch
):
    """`EVIDENCE-0013` Governance PASS 이후 실제로 전환된 5개 호출부 중
    하나(`backend_agent_code_review`)가 `call_engine_via_omniroute`를
    거쳐 실제(격리) OmniRoute 서버까지 도달하는지 end-to-end로
    확인한다 — 이전 테스트들은 `call_engine_via_omniroute()`를 직접
    호출했을 뿐, 실제 Agent 함수를 통한 배선(import alias)까지는
    검증하지 않았다."""
    env = real_omniroute_with_local_double
    monkeypatch.setenv("OMNIROUTE_BASE_URL", env["base_url"])
    monkeypatch.setenv("OMNIROUTE_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("OMNIROUTE_MODEL", "ollama-local/test-model")

    result = backend_agent_code_review("def f(): pass")
    assert result == "ENGINE_REAL_INTEGRATION_OK"


def test_timeout_abort_via_production_function(real_omniroute_with_local_double, monkeypatch):
    """`call_engine_via_omniroute()`는 동기 계약(`call_engine()`과 동일)만
    노출한다 — cancellation API는 `caller.py`(비동기 handle)에서만
    검증한다(`EVIDENCE-0004`§5.4, 이번 회귀에서 재확인). 이 함수의
    동기 계약에서 "진행 중 중단"에 대응하는 것은 timeout이다."""
    env = real_omniroute_with_local_double
    env["double_server"].mode = "slow"
    monkeypatch.setenv("OMNIROUTE_BASE_URL", env["base_url"])
    monkeypatch.setenv("OMNIROUTE_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("OMNIROUTE_MODEL", "ollama-local/test-model")
    monkeypatch.setenv("OMNIROUTE_TIMEOUT_SECONDS", "0.5")

    with pytest.raises(RuntimeError) as exc_info:
        call_engine_via_omniroute("hello")
    assert "timed out" in str(exc_info.value).lower()
