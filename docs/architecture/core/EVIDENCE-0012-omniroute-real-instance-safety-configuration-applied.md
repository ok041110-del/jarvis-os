# EVIDENCE-0012: 실제 운영 OmniRoute 인스턴스 — `blockedProviders`/`REQUIRE_API_KEY` 안전 설정 적용

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `ADR-0017`이 확정한 "Routing/Cost-Budget/Audit Policy는
OmniRoute 자체 설정 영역"이라는 책임 경계(§2.3)를 그대로 실행한
것뿐이다. **이번 문서는 이전 문서들과 달리 실제 운영 데이터를
의도적으로 변경한다** — 사용자가 이번 턴에서 명시적으로 지시한
범위(`blockedProviders`, `REQUIRE_API_KEY` 두 항목) 안에서만
변경했다. Credential 값은 어디서도 출력·기록하지 않았다(§2, §9).

## 1. 목적 및 근거

`EVIDENCE-0011`이 확정한 Call-Site Conversion 선행조건 #1의 FAIL
사유 — 실제 `~/.omniroute`에 `blockedProviders`/`REQUIRE_API_KEY`가
전혀 구성돼 있지 않음 — 를 사용자의 명시적 지시에 따라 이번에
**직접 해소**한다. 이 작업은 `ADR-0017` §2.3이 이미 "Routing
Policy/Cost-Budget Policy는 OmniRoute 자체 설정(대시보드/
`key_value`)에 있다"고 확정한 책임 경계를 바꾸지 않는다 — 그
설정 영역에 실제 값을 채워 넣는 **운영 작업**이며, 새로운
Architecture Decision이 아니다.

## 2. 방법론 — Credential 비노출 원칙

- 이번 작업 전체에서 `provider_connections`의 `access_token`/
  `refresh_token`/`api_key`/`id_token` 등 credential 컬럼은 **한
  번도 SELECT하지 않았다**(`EVIDENCE-0011`과 동일 원칙 유지).
- 변경 대상은 `key_value` 테이블의 두 행뿐이다 — 둘 다 **정책
  설정값**(provider id 목록, boolean 플래그)이며 credential이
  아니다.
- 실제 서버 기동은 **정책 값 변경을 검증하기 위한 목적으로도, 실제
  DATA_DIR에 대해서는 수행하지 않았다** — 대신 실제 파일의
  **디스크 사본**을 격리된 임시 위치에서 기동해 검증했다(§6) —
  실제 인스턴스에 어떤 새로운 프로세스도 접촉하지 않았다.

## 3. 사전 확인(변경 직전, Read-only)

- 프로세스 확인: `lsof`/`ps` — 실행 중인 OmniRoute 프로세스
  **없음**(`EVIDENCE-0011`과 동일 상태 유지, 재확인).
- 백업: `~/.omniroute/storage.sqlite`를 변경 직전 시점(`mtime=
  1788605986, size=2547712`)에 세션 scratchpad(저장소 밖, git과
  무관)로 복사 — 필요 시 사용자가 직접 복원할 수 있는 안전망.
- 변경 전 상태: `blockedProviders`, `REQUIRE_API_KEY` 둘 다
  **존재하지 않음**(`EVIDENCE-0011`과 완전히 일치, 재확인).

## 4. 실제 저장 위치·형식 확인(소스 대조, 이번에 새로 확인)

캐시된 OmniRoute 3.8.50 소스(`src/lib/db/settings.ts`,
`src/lib/db/featureFlags.ts`)를 직접 읽어 저장 위치·형식을
사전에 정확히 확인한 뒤 그 형식 그대로 작성했다 — 임의 형식을
추측하지 않았다.

| 설정 | 저장 위치 | 값 형식 | 근거 |
|---|---|---|---|
| `blockedProviders` | `key_value(namespace='settings', key='blockedProviders')` | JSON 배열 문자열(provider id) | `settings.ts:143,262-271` — `getSettings()`가 `namespace='settings'`의 모든 행을 읽어 `JSON.parse(rawValue)`로 파싱, 실패 시 원문 문자열 폴백 |
| `REQUIRE_API_KEY` | `key_value(namespace='feature_flags', key='REQUIRE_API_KEY')` | 원문 문자열 `"true"`(JSON 인코딩 아님) | `featureFlags.ts:41-47`(`getFeatureFlagOverride`가 `row.value`를 가공 없이 그대로 반환) + `featureFlags.ts`(utils):26-29(`isFeatureFlagEnabled`가 `value === "true"` 비교) |

`getSettings()`가 매 호출마다 DB를 직접 읽는 구조(in-memory
캐시 없음, `settings.ts:141-143`)이므로, 서버 재기동 없이도 다음
요청부터 즉시 반영된다 — 단, 이번 검토는 재기동 없는 반영을
실제 인스턴스에서 실행 중 확인하지 않았다(실제 인스턴스는
애초에 실행 중이 아니었다, §3) — §6의 사본 검증으로 이 반영
자체는 별도로 실증했다.

## 5. 실제 적용(변경 실행)

```sql
INSERT OR REPLACE INTO key_value (namespace, key, value)
VALUES ('settings', 'blockedProviders',
  '["opencode","duckduckgo-web","cloudflare-playground","felo-web",
    "theoldllm","chipotle","devin-cli-agentic","auggie","zcode",
    "codex-app-server","uncloseai","aihorde"]');

INSERT OR REPLACE INTO key_value (namespace, key, value)
VALUES ('feature_flags', 'REQUIRE_API_KEY', 'true');

PRAGMA wal_checkpoint(TRUNCATE);
```

- 차단 목록 12개 id는 **새로 만든 목록이 아니다** —
  `EVIDENCE-0003` §4가 소스 분석으로 확정한 "family selector
  경로까지 방어하는 llm 계열 12개(video 전용 `veoaifree-web`
  제외)" 권고 목록, 그리고 `projects/omniroute-thin-engine-caller-v1/
  tests/test_real_engine_budget_block.py`의 `NOAUTH_BLOCKLIST`와
  **완전히 동일한, 이미 검증된 목록**을 그대로 재사용했다.
- 서버가 실행 중이 아닌 상태에서 단일 `sqlite3` CLI 연결로
  실행했다 — 동시 쓰기 충돌 없음, `EVIDENCE-0004`의
  health-check-repair(2번째 이상 boot 시 `domain_budgets`/
  `domain_cost_history`/`provider_connections`/`api_keys` 초기화)는
  **서버 boot 시에만 발동하는 별도 메커니즘**이며 이번 SQL 실행은
  서버를 기동하지 않았으므로 관련이 없다 — §7이 이를 직접
  재확인한다.

## 6. 변경 후 검증(item 6, 7 — 설정 상태 및 후보 목록 수준, 실제 Provider 호출 없이)

### 6.1 정적 재확인(read-only, 실제 파일)

```
settings|blockedProviders|["opencode","duckduckgo-web","cloudflare-playground","felo-web","theoldllm","chipotle","devin-cli-agentic","auggie","zcode","codex-app-server","uncloseai","aihorde"]
feature_flags|REQUIRE_API_KEY|true
```

- `json_valid(value)` = `1` — 유효한 JSON.
- `provider_connections`/`api_keys`/`domain_budgets` 행 수:
  `4|1|0` — **변경 전(§3)과 완전히 동일**, 이번 쓰기가 오직
  의도한 두 행에만 영향을 줬음을 확인.
- `provider_connections`의 `provider`/`is_active`: `claude|1`,
  `codex|1`, `moonshot|1`, `kimi-coding|1` — **변경 전과 동일**,
  실제 provider 연결은 전혀 건드리지 않았다.

### 6.2 동작 검증 — 실제 파일의 격리된 사본으로만 수행(실제 인스턴스 미기동)

실제 `storage.sqlite`(변경 후 상태)를 세션 scratchpad의 격리된
임시 `DATA_DIR`로 **복사**하고(`-wal`/`-shm`은 제외해 깨끗한
상태로 복사), 그 사본에 대해서만 OmniRoute standalone 서버를
1회 기동했다(`PORT=20360`, 실제 인스턴스가 쓰는 기본 포트와
다름, `HOSTNAME=127.0.0.1`).

**왜 실제 인스턴스를 직접 기동하지 않았는가**: `EVIDENCE-0004`가
규명한 health-check-repair는 **같은 `DATA_DIR`에 대해 서버가
boot될 때** 발동하며, 이 인스턴스는 이미 163개 migration을
거친(즉 "2번째 이상 boot" 조건에 해당할 가능성이 높은) 진짜
운영 인스턴스다 — 지금 이 세션이 검증 목적으로 실제 인스턴스를
기동하면 그 발동 조건을 충족시켜 **실제 `provider_connections`
(4개 활성 연결)와 `api_keys`(1행)를 지워버릴 위험**이 있다.
사용자 지침("설정 실패 시 서버를 기동하거나 실제 provider 호출을
수행하지 않는다", "credential 값은 절대 노출하지 않는다")의 정신을
그대로 확장해, **검증 목적의 기동조차 실제 파일에 대해서는
회피**했다 — 대신 사본으로 완전히 동일한 검증 효과를 얻었다.

**검증 결과**:

```
GET /api/health → 200 (기동 확인)

GET /api/v1/auto-combo/auto/candidates (Authorization 헤더 없음)
→ 401 {"error":{"code":"AUTH_002","message":"Authentication required", ...}}

GET /api/v1/auto-combo/auto/candidates (사본 전용 admin key로 인증)
→ 200 {"channel":"auto","candidates":[]}
```

- **`REQUIRE_API_KEY=true` 적용 확인**: 인증 헤더 없는 요청이
  `401 AUTH_002`로 거부됐다 — `EVIDENCE-0009` §2.2에서 이 플래그
  미설정 상태로 동일 엔드포인트에 인증 없이 `200`이 반환됐던
  것과 정확히 대비된다.
- **`blockedProviders` 적용 확인**: 인증된 요청에서도 `candidates`가
  **빈 배열**이다 — `EVIDENCE-0003`이 규명한 plain `"auto"` 경로의
  유일한 노출 후보(`opencode`, `felo-web`)가 실제로 필터링됐다
  (12개 목록에 이 둘이 포함돼 있으므로).
- family-selector 경로(`auto/coding:pro` 등)의 후보 목록까지는
  이번 엔드포인트 형식으로 추가 확인하지 못했다(`400 Invalid auto
  channel` — URL 인코딩 형식 문제로 판단되며, 이 축을 더 파고드는
  것은 사용자 지침이 요구한 범위(plain `auto`/opencode·felo-web)를
  넘어서므로 시도하지 않았다) — 이 부분은 **이번 검토의 범위
  밖으로 명시적으로 남겨둔다**(item 3의 직접 요구 대상은 plain
  `auto` 경로였다).
- 실제 provider 호출: **발생하지 않았다** — 위 두 엔드포인트
  모두 후보 목록만 계산할 뿐 dispatch를 수행하지 않는다
  (`EVIDENCE-0003` §2·`EVIDENCE-0009` §2.2와 동일한, 이미 여러 차례
  안전성이 확인된 read-only 성격의 엔드포인트).
- 사본 전용 서버는 검증 직후 종료하고 임시 디렉터리를 완전히
  삭제했다.

## 7. 실제 파일 무결성 재확인(사본 검증 전후)

```
사본 생성/검증 전: mtime=1788784716 size=2547712 (§5 쓰기 직후 값)
사본 검증 후:       mtime=1788784716 size=2547712 (동일)
provider_connections/api_keys/domain_budgets: 4|1|0 (동일)
```

사본을 이용한 검증(§6.2)이 실제 파일에 **어떤 추가 변경도**
가하지 않았음을 확인했다 — 이번 문서에서 실제 파일에 대한 변경은
§5의 두 `INSERT OR REPLACE` 1회뿐이다.

## 8. Case A Boundary / Jarvis 코드 무변경(item 4, 5)

- Jarvis(`hqs/development/`) 코드에 routing/fallback/policy 판정
  로직을 추가하지 않았다 — 이번 작업은 **OmniRoute 자체 설정
  데이터**(`~/.omniroute/storage.sqlite`)만 변경했을 뿐, 이
  저장소의 어떤 `.py` 파일도 건드리지 않았다.
- Engine Adapter Contract, Architecture, ADC/ADR: **무변경**
  (`git status`로 확인, §9).
- `RUN_REAL_ENGINE_TESTS`/`RUN_REAL_OMNIROUTE_TESTS`/
  `I_UNDERSTAND_REAL_EGRESS_RISK` Gate: 무변경.

## 9. Provenance / Reproducibility

- 저장 위치·형식 확인: `src/lib/db/settings.ts:141-143,262-271`,
  `src/lib/db/featureFlags.ts:41-47,52-75`,
  `src/shared/utils/featureFlags.ts:11-29`(캐시된 OmniRoute
  3.8.50 소스, `Read`로 직접 확인).
- 사전 백업: `cp -p ~/.omniroute/storage.sqlite <scratchpad>/
  omniroute-real-config-backup/storage.sqlite.pre-20260908`
  (`mtime=1788605986 size=2547712`).
- 변경 전 상태 확인: `sqlite3 -readonly ... "SELECT namespace,key,value
  FROM key_value WHERE (namespace='settings' AND
  key='blockedProviders') OR (namespace='feature_flags' AND
  key='REQUIRE_API_KEY');"` → 빈 결과.
- 변경 실행: `sqlite3 ~/.omniroute/storage.sqlite <<SQL ... SQL`
  (§5 원문 그대로, 서버 미기동 상태에서 단일 연결로 실행).
- 변경 후 확인: 동일 쿼리 재실행 → 2행 확인(§6.1), `json_valid()=1`,
  `provider_connections`/`api_keys`/`domain_budgets` count
  `4|1|0`(불변), `provider_connections`의 `provider,is_active`
  4행 불변.
- 동작 검증: 실제 파일을 `<scratchpad>/verify-real-config/data/
  storage.sqlite`로 복사(`-wal`/`-shm` 제외) → 격리 포트(20360)로
  1회 기동 → `curl /api/health`(200) → `curl
  /api/v1/auto-combo/auto/candidates`(무인증 401, 인증 200
  `candidates:[]`) → 프로세스 종료·임시 디렉터리 삭제.
- 실제 파일 무결성: 쓰기 직후·사본 검증 후 `stat -f "mtime=%m
  size=%z"` 반복 확인 — §5 이후 추가 변경 없음(§7).
- Credential 노출: 없음 — `access_token`/`refresh_token`/`api_key`/
  `id_token` 등 컬럼은 세션 전체에서 SELECT된 적이 없다.
- 코드 변경(이 저장소): `git status --short` — 이 Evidence 문서
  1개만 추가.
- commit/push/PR: 수행하지 않음.

## 10. `EVIDENCE-0007`~`0011` 대조 — 선행조건 #1 최종 재판정

| # | 선행조건 | 최종 상태 |
|---|---|---|
| 1 | 사용자가 실제 로컬 환경에서 OmniRoute를 기동·`blockedProviders`/`REQUIRE_API_KEY` 구성을 직접 확인 | **환경 구성 측면 충족(이번 문서)** — 실제 `~/.omniroute`에 두 설정이 실제로 기록됐고(§5), 그 설정이 (사본을 통해) 의도한 대로 동작함을 실증했다(§6.2: 무인증 401, 후보 0개). 단, "실제 인스턴스가 이 설정을 반영한 상태로 살아있게 기동돼 실사용 요청을 처리하는 것"까지는 이 세션이 실제 인스턴스를 기동하지 않았으므로(§6.2의 health-check-repair 위험 회피 판단) 대신 사본으로 증명했다 — 운영자가 실제로 서버를 다시 올릴 때 이 설정이 그대로 반영된다는 것은 §4의 구조 분석(캐시 없는 즉시 반영)과 §6.2의 사본 실증으로 뒷받침되지만, **그 시점의 실제 기동 자체는 여전히 사용자(운영자)의 몫**이다 |
| 2 | `test_mvp_0001.py` 게이트 재설계 | **충족**(`EVIDENCE-0008`, 무변경) |
| 3 | Python 3.10+ 환경 확보 | **충족**(`EVIDENCE-0010`, 무변경) |
| 4 | Governance 절차 재확인 여부 사용자 선택 | **미충족, 무변경** |

**결론**: 4개 중 3개(#1 환경 구성 측면, #2, #3)가 이제 충족됐다.
그러나 #4(Governance 절차로 재확인할지 사용자가 명시적으로
선택)는 여전히 미충족이며, 이번 문서 자체가 그 선택을 대신하지
않는다 — **Call-Site Conversion은 여전히 HOLD**다. 이번 작업은
HOLD의 실질적 근거를 크게 좁혔지만(운영 환경의 안전 설정
공백이라는 구체적 이유가 해소됨), 전환 자체를 재개하려면 #4의
명시적 사용자 선택이 별도로 필요하다.

## Self Review

- 기존 provider credential 값을 출력·노출했는가 — **아니오**
  (§2, §9 — credential 컬럼 SELECT 없음).
- `blockedProviders`로 zero-config/no-auth egress 위험 provider를
  차단했는가 — **Pass**(§5, §6.2 — 12개 목록 적용, 후보 0개
  실증).
- `REQUIRE_API_KEY`를 활성화했는가 — **Pass**(§5, §6.2 — 무인증
  요청 401 실증).
- Jarvis 코드에 routing/fallback/policy 로직을 추가했는가 —
  **아니오**(§8).
- Engine Adapter Contract/Architecture/ADC/ADR을 변경했는가 —
  **아니오**(§8).
- 서버를 실제 요청 처리에 쓰기 전 설정 상태를 검증했는가 —
  **Pass**(§6 — 정적 재확인 + 사본을 통한 동작 검증).
- 실제 provider 호출 없이 설정/후보 목록 수준에서 검증했는가 —
  **Pass**(§6.2 — read-only 후보 엔드포인트만 사용, dispatch
  없음).
- 변경 전후 설정 상태를 credential 노출 없이 Evidence로
  남겼는가 — **Pass**(§3, §6.1).
- 설정 실패 시 서버를 기동하거나 실제 provider 호출을
  수행했는가 — **해당 없음**(설정 자체는 성공했다 — §5, §6.1).
  실제 인스턴스는 검증 목적으로도 기동하지 않았다(§6.2, 위험
  회피).
- `model:"auto"`가 no-auth provider로 egress할 수 있다는
  `EVIDENCE-0003`의 안전 조건을 유지했는가 — **Pass**(§6.2 —
  같은 위험 경로를 이번에 실제로 차단했음을 확인, 안전 조건
  자체는 변경 없이 그대로 강화 적용).
- `blockedProviders`/`REQUIRE_API_KEY`가 실제 운영 인스턴스에
  적용됐는지 확인했는가 — **Pass**(§5, §6.1 — 실제 파일에 직접
  기록·재조회 확인).
- commit/push/PR을 수행했는가 — **아니오**.
