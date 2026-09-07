# EVIDENCE-0011: 실제 운영 OmniRoute 인스턴스 — 기동·안전조건 구성 상태 검증

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0007`·`EVIDENCE-0009`·`EVIDENCE-0010`이 확정한
HOLD 상태를 그대로 전제하고, 이번 검토(실제 운영 인스턴스의
안전조건 구성 상태 확인)의 결과만 기록한다. **코드/설정 변경
없음.** 실제 Provider 호출 없음(§6). Credential/provider connection
값 노출 없음(§2).

## 1. 검토 목적

`EVIDENCE-0007` §6.2 선행조건 #1 — "사용자(운영자)가 실제 로컬
환경에서 OmniRoute를 기동하고, `blockedProviders`/`REQUIRE_API_KEY`를
구성했음을 **직접 확인**한다" — 를 이 세션이 read-only로 직접
검증한다. `EVIDENCE-0009`가 이미 명확히 한 "환경 구조가
가능함"(macOS PASS)과 이번 문서가 다루는 "실제 운영 인스턴스가
안전하게 구성돼 있음"은 **서로 다른 질문**이다(사용자 지침 6) —
이번 문서는 후자만 답한다.

## 2. 방법론 — Credential 비노출 read-only 검사

실제 `~/.omniroute/storage.sqlite`를 `sqlite3 -readonly` 모드로만
열었다(쓰기 불가능한 연결) — 서버 프로세스를 새로 기동하지
않았고, 파일에 어떤 변경도 가하지 않았다(§9가 전후 mtime/size
동일함을 확인). 조회는 다음 두 종류로 엄격히 제한했다.

- **정책/설정 값**(credential이 아님, 안전하게 열람 가능): `key_value`
  테이블의 `settings` namespace 키/값, `db_meta`, `_omniroute_migrations`
  개수·최근 항목.
- **존재/개수/식별자만**(credential 컬럼은 SELECT하지 않음):
  `provider_connections`에서 `provider`·`is_active` 컬럼만 조회
  (`access_token`/`refresh_token`/`api_key`/`id_token` 등 credential
  컬럼은 **한 번도 SELECT하지 않았다**), `api_keys`/`domain_budgets`는
  `COUNT(*)`만 조회. `.env` 파일은 변수 **이름만** `grep -oE
  "^[A-Za-z_]+="`로 추출했고 값은 어디서도 출력하지 않았다.

## 3. 실제 운영 인스턴스 — 기동 상태(item 1, 4)

| 항목 | 확인 결과 |
|---|---|
| `~/.omniroute` 존재 여부 | **존재**(`.env`, `call_logs/`, `db_backups/`, `logs/`, `oauth/`, `server/`, `supervisor/`, `storage.sqlite` 등) — `setupComplete=true`(§4)로 실제 설정 완료된 인스턴스임을 확인 |
| `storage.sqlite` | 존재, `mtime=1788605986`, `size=2547712`(세션 전체의 기준 스냅샷과 동일) |
| 현재 리스닝 포트(기본 20128 및 인접) | **없음** — `lsof`로 확인, 현재 실행 중인 리스너 없음 |
| OmniRoute 관련 프로세스 | **없음** — `ps aux` 확인, 현재 실행 중인 프로세스 없음 |
| `supervisor/.pid`, `server/.pid` | 각각 `36674`, `36678` 기록돼 있으나 **둘 다 stale**(해당 PID로 실행 중인 프로세스 없음) |
| 마지막 활동 시각(추정) | `_omniroute_migrations` 최신 항목 `2026-09-05 03:28:16`, `storage.sqlite` mtime과 대략 일치 — 가장 최근 실행이 이 시점 부근이었던 것으로 보인다 |
| 실행 방식(추정) | 전역(global) npm 설치가 발견되지 않음(`npm root -g`에 `omniroute` 없음, `which omniroute` 없음) — `npx omniroute`(버전 `3.8.50`, 세션 전체에서 사용한 캐시된 버전과 동일) 방식의 **on-demand 실행**으로 추정. `supervisor`/`server` 두 개의 `.pid`를 관리하는 구조로 보아 supervisor가 실제 서버 프로세스를 감독하는 형태로 최근 실행됐던 것으로 보인다 |

**판정 — 기동 상태**: 현재 시점 기준 **실행 중이 아니다.** 사용자
지침 7에 따라, 확인 권한이 없거나 실행 중이 아닌 항목을 임의로
기동·구성하지 않았다 — **직접 기동하지 않았다.** `/api/health`,
`/api/v1/auto-combo/*/candidates` 등 live endpoint 확인(item 4)은
**UNVERIFIED**(실행 중이 아니므로 수행 대상 자체가 없음, 강행
기동하지 않음).

## 4. `blockedProviders` / `REQUIRE_API_KEY` 실제 구성 상태(item 2, 3)

`key_value` 테이블 전체 namespace(`apiKeySelfService`, `compression`,
`databaseSettings`, `gamification:streaks`, `lkgp`, `modelAliases`,
`pricing_sync_status`, `pricing_synced`, `providerLimitsCache`,
`scheduler`, `settings`, `syncedAvailableModels`)를 대상으로
`block`/`provider`/`require`/`api_key` 문자열을 포함하는 키를 전수
검색했다.

| 검사 항목 | 실제 값/존재 여부 | 판정 |
|---|---|---|
| `blockedProviders` 키 자체 | **어떤 namespace에도 존재하지 않음** | **FAIL** — 설정된 적이 없다 |
| `REQUIRE_API_KEY` 키 자체 | **존재하지 않음**(`EVIDENCE-0003`이 확인한 `featureFlagDefinitions.ts`의 `defaultValue: "false"`가 그대로 적용되는 상태로 추정 — 명시적으로 변경된 적이 없다는 의미) | **FAIL** — 기본값(비활성)에서 변경되지 않았다 |
| `requireLogin`(관련 인접 플래그, 실제 존재) | `false` | 참고 — `REQUIRE_API_KEY`와 별개 축이지만(`EVIDENCE-0003` §1), 이 역시 비활성 |
| `setupComplete` | `true` | 참고 — 인스턴스 자체는 설정 완료 상태(빈 설치가 아님) |

**판정 — 안전조건 구성**: `blockedProviders`, `REQUIRE_API_KEY` 둘 다
**FAIL** — 이 값들은 UNVERIFIED가 아니라, 직접 조회로 확인된 실제
persisted 상태다(§2의 read-only 조회가 확정적 증거).

## 5. Provider Connection 실재 여부(egress 잠재력 확인, credential 비노출)

```
SELECT provider, is_active FROM provider_connections;
```

```
claude       | 1
codex        | 1
moonshot     | 1
kimi-coding  | 1
```

- 4개의 **실제 활성(`is_active=1`) Provider Connection**이 존재한다
  — 이 인스턴스는 빈 설치가 아니라 실제 provider credential이
  등록된, 실사용 이력이 있는 인스턴스다.
- `api_keys` 테이블 1행 존재(개수만 확인, 값 미조회).
- `domain_budgets` 0행 — budget 기반 방어도 현재 구성돼 있지 않다
  (참고 사항, item 3의 직접 대상은 아니지만 §7의 위험 판단에
  포함).
- **이 4개 provider 자체는 `blockedProviders`가 막는 대상
  (`opencode`/`felo-web` 등 built-in NOAUTH provider)과 다르다** —
  이 4개는 사용자가 스스로 등록한 정식 provider connection이므로
  이번 검토의 FAIL 판정과 별개다. 다만 `blockedProviders` 미설정은
  이 4개와 무관하게 **built-in NOAUTH 경로(`opencode`/`felo-web`)를
  통한 zero-config egress를 막지 못하는 상태**를 의미한다
  (`EVIDENCE-0003`/`0004`가 규명한 경로 그대로).

## 6. 실제 Provider 호출 금지 준수(item 5)

- 실제 서버를 기동하지 않았다(§3).
- `npx omniroute --version`을 `--no-install` 플래그로 시도했으나
  캐시에 해당 정확한 invocation이 없어 **실행 자체가 취소됐다**
  (`npm error npx canceled due to missing packages`) — 실제 실행이
  일어나지 않았다.
- `model:"auto"` dispatch, `/api/v1/auto-combo/*/candidates` 등 어떤
  HTTP 요청도 실제 인스턴스에 보내지 않았다 — 서버가 기동돼 있지
  않으므로애초에 대상이 없었다.
- 모든 조회는 SQLite 파일에 대한 `-readonly` 연결로만 이뤄졌다.

## 7. Isolated 검증과 실제 운영 설정의 명확한 구분(item 6)

| 구분 | 결과 |
|---|---|
| **환경 구조가 가능한가**(`EVIDENCE-0009`) | **PASS** — macOS에서 Claude Code+Jarvis+OmniRoute가 격리 환경으로 실행·연결 가능함을 실동 확인 |
| **실제 운영 인스턴스가 안전하게 구성됐는가**(이 문서) | **FAIL** — 실제 `~/.omniroute`의 `blockedProviders`/`REQUIRE_API_KEY`가 둘 다 미구성(기본값) 상태로 확인됨 |

이 둘은 서로 다른 질문이며, 하나의 PASS가 다른 하나의 FAIL을
상쇄하지 않는다 — `EVIDENCE-0009`의 PASS는 "가능함"만 의미했고,
이번 문서가 "실제로 안전하게 그렇게 돼 있음"을 처음으로 직접
검증했다.

## 8. Gate/Boundary 무변경 확인(item 8)

- `RUN_REAL_ENGINE_TESTS`, `RUN_REAL_OMNIROUTE_TESTS`,
  `I_UNDERSTAND_REAL_EGRESS_RISK`: 이번 검토에서 설정하지도,
  코드를 수정하지도 않았다.
- Case A Boundary 관련 코드(`omniroute_engine.py`, 5개 호출부,
  Experimental prototype `caller.py`): **무수정**(`git status`로
  확인, §9).
- 실제 `~/.omniroute`의 설정을 **수정하지 않았다** — 이번 발견
  (`blockedProviders`/`REQUIRE_API_KEY` 미구성)에 대해 이 세션이
  직접 구성을 추가하거나 고치는 어떤 시도도 하지 않았다(사용자
  지침 7 — 임의 구성·수정 금지, 발견만 기록).

## 9. Provenance / Reproducibility

- 기동 상태 확인: `lsof -nP -iTCP -sTCP:LISTEN | grep -E
  ":(20128|20127|20129)"`(결과 없음), `ps aux | grep -i
  "omniroute\|dist/server.js"`(결과 없음), `cat ~/.omniroute/
  supervisor/.pid`(`36674`) · `~/.omniroute/server/.pid`(`36678`),
  `ps -p 36674`/`ps -p 36678`(둘 다 실행 중 아님).
- 설정 확인: `sqlite3 -readonly ~/.omniroute/storage.sqlite
  "SELECT namespace, key FROM key_value WHERE
  namespace='settings';"`(8개 키, `blockedProviders`/
  `REQUIRE_API_KEY` 없음 확인), 전체 namespace 대상
  `block`/`provider`/`require`/`api_key` 문자열 전수 검색(위 8개
  외 매칭 없음), `SELECT key, value FROM key_value WHERE
  namespace='settings' AND key IN ('requireLogin',
  'REQUIRE_API_KEY','setupComplete');` → `requireLogin=false`,
  `setupComplete=true`(`REQUIRE_API_KEY` 행 자체가 없음).
- Provider connection 확인: `SELECT provider, is_active FROM
  provider_connections;` → 4행(`claude`/`codex`/`moonshot`/
  `kimi-coding`, 전부 `is_active=1`) — credential 컬럼(`access_token`,
  `refresh_token`, `api_key`, `id_token` 등)은 스키마 컬럼명만
  확인했을 뿐(`PRAGMA table_info`) 값을 조회한 적 없음.
- `.env` 변수 이름만 확인: `grep -oE "^[A-Za-z_]+=" ~/.omniroute/.env`
  → `STORAGE_ENCRYPTION_KEY=`(이름만, 값 미출력).
- 무결성 확인: 조회 전후 `stat -f "mtime=%m size=%z"
  ~/.omniroute/storage.sqlite` → `mtime=1788605986 size=2547712`
  (완전 동일, 세션 전체 기준값과 일치), `storage.sqlite-wal`
  → `size=0`(변경 없음).
- 코드 변경: `git status --short` — 이 Evidence 문서 1개만 추가.
- 실제 Provider 호출: 없음(§6).
- commit/push/PR: 수행하지 않음.

## 10. `EVIDENCE-0007`~`0010` 대조 — 선행조건 #1 최종 판정

`EVIDENCE-0007` §6.2 선행조건 4개 중 이번 문서가 다루는 것은 #1이다.
`EVIDENCE-0009`·`EVIDENCE-0010`이 이미 정리한 표에 이번 결과를
반영한다.

| # | 선행조건 | 상태(이번 갱신 반영) |
|---|---|---|
| 1 | 사용자가 실제 로컬 환경에서 OmniRoute를 기동·`blockedProviders`/`REQUIRE_API_KEY` 구성을 직접 확인 | **미충족 — FAIL로 확정(이번 문서).** UNVERIFIED가 아니다: 실제 인스턴스가 현재 미기동 상태임을 확인했고, 그 인스턴스의 persisted 설정을 직접 read-only로 조회한 결과 `blockedProviders`/`REQUIRE_API_KEY` 둘 다 구성되지 않은(기본/비활성) 상태임을 확정적으로 확인했다. 동시에 4개의 실제 활성 provider connection이 등록돼 있어(§5) 이 인스턴스가 실사용 이력이 있는 진짜 운영 인스턴스임도 확인됐다 — "빈 설치라 판단 불가"가 아니라 "실사용 인스턴스인데 이 두 안전조건이 비어 있다"는 더 구체적이고 강한 부정적 결과다 |
| 2 | `test_mvp_0001.py` 게이트 재설계 | **충족**(`EVIDENCE-0008`, 무변경) |
| 3 | Python 3.10+ 환경 확보 | **충족**(`EVIDENCE-0010`, 무변경) |
| 4 | Governance 절차 재확인 여부 사용자 선택 | **미충족, 무변경** |

**결론**: 4개 중 2개(#2, #3)만 충족된 상태가 그대로 유지되며, #1은
이번 검토로 "미검증"에서 "명시적 FAIL"로 **더 명확해졌다** — 단순히
확인이 불가능했던 것이 아니라, 확인해 본 결과 현재 실제로 안전하게
구성돼 있지 않다는 사실이 드러났다. **Call-Site Conversion은 계속
HOLD**이며, 이번 발견은 HOLD 해제 근거가 되지 못할 뿐 아니라 —
Jarvis 코드와 무관하게 — 운영자가 실제 인스턴스를 사용하기 전에
직접 조치해야 할 별도의 실무 사항(`blockedProviders`/
`REQUIRE_API_KEY` 구성)이 있음을 명확히 보여준다. 이 조치 자체는
OmniRoute 자신의 설정 영역이며(`ADR-0017` §2.3, Policy 소재는
OmniRoute 쪽), 이 세션이 대신 수행하지 않는다(사용자 지침 7).

## Self Review

- 실제 운영 인스턴스의 Node.js/OmniRoute 버전·실행 방식·DATA_DIR·
  provider connection·model 설정을 read-only로 확인했는가 —
  **Pass**(§3, §5).
- `~/.omniroute`의 credential/provider connection 값을 노출했는가 —
  **아니오**(§2, §9 — credential 컬럼은 스키마명만 확인, 값 미조회).
- 존재 여부와 충족 여부만 PASS/FAIL로 판정했는가 — **Pass**(§4).
- `blockedProviders`(opencode/felo-web 차단)와 `REQUIRE_API_KEY`
  실제 적용 상태를 확인했는가 — **Pass**(§4 — 둘 다 FAIL로 확정).
- 실제 인스턴스가 실행 중이면 `/api/health`/candidates를
  확인했는가 — **해당 없음**(§3 — 실행 중이 아님을 먼저 확인,
  강행 기동하지 않음).
- 실제 Provider 호출이나 `model:auto` dispatch를 유발했는가 —
  **아니오**(§6).
- Isolated 검증 결과와 실제 운영 설정을 혼동했는가 — **아니오**
  (§7 — 명확히 분리해 표로 정리).
- 실행 중이 아니거나 권한이 없을 때 임의로 구성·수정했는가 —
  **아니오**(§3, §8 — 발견만 기록, 수정 시도 없음).
- 기존 Gate(`RUN_REAL_ENGINE_TESTS` 등)와 Case A Boundary를
  변경했는가 — **아니오**(§8).
- `EVIDENCE-0007`~`0010`과 대조해 선행조건 #1의 실제 충족 여부를
  명확히 판정했는가 — **Pass**(§10 — FAIL로 확정, HOLD 유지).
- 코드/Architecture/Contract를 변경했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**.
