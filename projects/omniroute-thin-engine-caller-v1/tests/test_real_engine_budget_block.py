"""실제(격리된) OmniRoute 서버를 상대로 한 `domain_budgets` 사전 차단
lifecycle 검증.

**2026-09-07 방법론 갱신(`EVIDENCE-0004`/`EVIDENCE-0005` 참조)** — 이전
버전은 "서버 정지 → DB 삽입 → 재기동" 순서를 사용했고, 그 방식이 이
빌드에서는 실제 예산 차단을 트리거하지 못해 의도치 않은 실제 egress를
유발했다(`EVIDENCE.md` §안전 경계 참조, 2026-09-07 이전 기록). 근본
원인은 OmniRoute standalone 서버가 **동일 `DATA_DIR`로 두 번째 이후
기동할 때마다** `domain_budgets`/`domain_cost_history`/
`provider_connections`/`api_keys`를 초기화하는 "health-check-repair"
동작이었다(`EVIDENCE-0004` §3, 4회 독립 재현으로 확정).

이 버전은 그 근본 원인을 반영해 **서버를 단 한 번만 기동하고 절대
재기동하지 않는다.** 테스트 데이터는 서버가 계속 실행 중인 상태에서
별도 `sqlite3` CLI 연결로 직접 삽입한다 — 이 방식은 `EVIDENCE-0004`
§3.3에서 실제로 HTTP 429(`rate_limit_exceeded`, egress 흔적 0건)를
재현해 검증했다.

## 안전 경계(중요 — 이 파일이 검증하는 경로만 실제 서버로 확인한다)

`model:"auto"`로 provider connection이 전혀 없는 상태에서 요청을
보내면, OmniRoute 내장 no-auth provider(`opencode`/`felo-web`)로 실제
egress가 발생할 수 있다(`EVIDENCE.md` §안전 경계, `EVIDENCE-0003` §3).
이 파일은 두 겹의 방어로 이를 차단한다.

1. **1차 방어(주 대상)**: `domain_budgets` 초과 삽입 —
   `enforceApiKeyPolicy()`의 `validateBudget()`이 Auto-Combo 후보
   구성보다 먼저 실행되므로(`EVIDENCE-0002`가 소스 레벨로 확인,
   `EVIDENCE-0004` §3.3이 실행으로 재확인) egress가 발생하지 않는다.
2. **2차 방어(defense-in-depth)**: `blockedProviders`에 non-video
   NOAUTH provider 전체를 등록 — 혹시 1차 방어가 실패하더라도
   plain `"auto"` 후보 풀이 비어 있도록 만든다(`EVIDENCE-0004` §4가
   read-only endpoint로 검증한 것과 동일한 설정).

두 방어 중 하나라도 실패해 dispatch 흔적(`ProxyEgress`/`Auto
selection:`)이 로그에 나타나면 이 테스트는 **FAIL** 처리된다(안전
가정이 깨졌다는 뜻 — 재시도하지 않고 즉시 보고해야 한다).

- 완전히 새로운 임시 `DATA_DIR` — 사용자의 실제 `~/.omniroute`는
  건드리지 않는다(테스트 종료 시 mtime/size 대조로 재확인).
- test-only fake API key(`OMNIROUTE_API_KEY` env var, 실제 계정 아님).
- provider connection을 아예 만들지 않는다.
- 서버는 이 테스트 전체에서 **정확히 한 번**만 기동되고, 절대
  재기동되지 않는다(health-check-repair 회피).

## opt-in 게이팅(이중, 기존과 동일하게 유지)

기본 `pytest`로는 SKIP된다. 실행하려면:

    RUN_REAL_OMNIROUTE_TESTS=1 I_UNDERSTAND_REAL_EGRESS_RISK=1 \\
        OMNIROUTE_PKG_DIR=<omniroute 패키지 경로> \\
        pytest tests/test_real_engine_budget_block.py -v
"""

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import caller as omniroute_caller  # noqa: E402

RUN_FLAG = "RUN_REAL_OMNIROUTE_TESTS"
SECOND_GATE_FLAG = "I_UNDERSTAND_REAL_EGRESS_RISK"
DEFAULT_PKG_DIR = (
    "/private/tmp/claude-501/-Users-chan-Developer-jarvis-os/"
    "5ce390ee-d07e-47e5-ae03-ef17b00078ff/scratchpad/npm-cache-omniroute/"
    "_npx/44b85dff014d9ceb/node_modules/omniroute"
)
FAKE_API_KEY = "thin-caller-test-only-key-0002"
PORT = 20242

# `EVIDENCE-0003` §4가 규명한 전체 non-video NOAUTH provider id(2차 방어).
NOAUTH_BLOCKLIST = [
    "opencode", "duckduckgo-web", "cloudflare-playground", "felo-web",
    "theoldllm", "chipotle", "devin-cli-agentic", "auggie", "zcode",
    "codex-app-server", "uncloseai", "aihorde",
]

pytestmark = [
    pytest.mark.skipif(
        os.environ.get(RUN_FLAG) != "1",
        reason=f"opt-in 전용 — {RUN_FLAG}=1 로 명시적으로 실행해야 한다(비용/지연 발생 가능)",
    ),
    pytest.mark.skipif(
        os.environ.get(SECOND_GATE_FLAG) != "1",
        reason=(
            f"실제 격리 OmniRoute 서버로 egress 위험이 있는 경로를 검증한다 — "
            f"{SECOND_GATE_FLAG}=1 로 위험을 이해했음을 명시해야 한다"
        ),
    ),
]


def _pkg_dir():
    return os.environ.get("OMNIROUTE_PKG_DIR", DEFAULT_PKG_DIR)


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
def real_omniroute_env(tmp_path):
    pkg_dir = _pkg_dir()
    if not Path(pkg_dir, "dist", "server.js").is_file():
        pytest.skip(f"OmniRoute 패키지를 찾을 수 없다: {pkg_dir} (환경 가용성 문제, FAIL 아님)")

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
    # 이 fixture는 서버를 **정확히 한 번**만 기동한다 — 테스트 본문은
    # 이 프로세스를 절대 재기동하지 않는다(health-check-repair 회피,
    # `EVIDENCE-0004` §3.2/§3.3).
    proc = subprocess.Popen(
        ["node", "dist/server.js"], cwd=pkg_dir, env=env,
        stdout=log_file, stderr=subprocess.STDOUT,
    )
    try:
        if not _wait_for_health(base_url):
            proc.kill()
            proc.wait(timeout=5)
            pytest.skip("OmniRoute 서버가 health check에 응답하지 않음(환경 문제, FAIL 아님)")

        yield {
            "base_url": base_url,
            "data_dir": data_dir,
            "log_path": log_path,
        }
    finally:
        proc.kill()
        proc.wait(timeout=10)
        log_file.close()

    real_stat_after = real_data_dir.stat() if real_data_dir.exists() else None
    if real_stat_before is not None:
        assert real_stat_after is not None
        assert real_stat_before.st_mtime == real_stat_after.st_mtime, (
            "실제 ~/.omniroute/storage.sqlite mtime이 변경됐다 — 격리 실패"
        )
        assert real_stat_before.st_size == real_stat_after.st_size, (
            "실제 ~/.omniroute/storage.sqlite size가 변경됐다 — 격리 실패"
        )


def _sqlite_exec(db_path, statements):
    """서버가 실행 중인 채로 별도 연결을 열어 statement를 실행한다.

    서버 프로세스를 멈추거나 재기동하지 않는다 — 이것이
    `EVIDENCE-0004`가 확정한 안전한 방법론의 핵심이다.
    """
    conn = sqlite3.connect(str(db_path), timeout=10)
    try:
        for sql, params in statements:
            conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def _apply_blocked_providers(data_dir):
    import json as _json
    db_path = data_dir / "storage.sqlite"
    _sqlite_exec(db_path, [
        (
            "INSERT OR REPLACE INTO key_value (namespace, key, value) "
            "VALUES ('settings', 'blockedProviders', ?)",
            (_json.dumps(NOAUTH_BLOCKLIST),),
        ),
    ])


def _insert_exceeded_budget(data_dir, api_key_id):
    db_path = data_dir / "storage.sqlite"
    _sqlite_exec(db_path, [
        (
            "INSERT INTO domain_budgets "
            "(api_key_id, daily_limit_usd, weekly_limit_usd, monthly_limit_usd, "
            " warning_threshold, reset_interval, reset_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (api_key_id, 0.01, 100.0, 1000.0, 0.8, "daily", "00:00"),
        ),
        (
            "INSERT INTO domain_cost_history (api_key_id, cost, timestamp) VALUES (?, ?, ?)",
            (api_key_id, 999.0, int(time.time() * 1000)),
        ),
    ])


def _fetch_noauth_candidate_count(base_url):
    with urllib.request.urlopen(
        f"{base_url}/api/v1/auto-combo/auto/candidates", timeout=5
    ) as resp:
        import json as _json
        return len(_json.loads(resp.read().decode("utf-8")).get("candidates", []))


def test_budget_exceeded_blocks_before_dispatch(real_omniroute_env):
    env = real_omniroute_env

    # 2차 방어: blockedProviders를 먼저 적용하고, dispatch를 유발하지
    # 않는 read-only endpoint로 실제로 적용됐는지 확인한다(재기동 없음).
    _apply_blocked_providers(env["data_dir"])
    candidate_count = _fetch_noauth_candidate_count(env["base_url"])
    assert candidate_count == 0, (
        f"blockedProviders 적용 후에도 no-auth candidate가 {candidate_count}개 남음 — "
        "2차 방어가 적용되지 않았다. 실제 요청을 보내지 않고 여기서 중단한다"
    )

    # 1차 방어: budget 초과 행 삽입(같은 프로세스, 재기동 없음).
    _insert_exceeded_budget(env["data_dir"], api_key_id="env-key")

    with pytest.raises(omniroute_caller.OmniRouteBudgetExceededError) as excinfo:
        omniroute_caller.call_omniroute(
            "hello", base_url=env["base_url"], api_key=FAKE_API_KEY, timeout=15,
        )
    assert "429" in str(excinfo.value)

    log_text = env["log_path"].read_text(encoding="utf-8", errors="replace")
    assert "ProxyEgress" not in log_text, (
        "budget 차단 경로에서 egress 흔적이 발견됐다 — 안전 가정이 깨졌다"
    )
    assert "Auto selection:" not in log_text, (
        "budget 차단 경로에서 Auto-Combo dispatch 흔적이 발견됐다 — 안전 가정이 깨졌다"
    )
