# EVIDENCE-0004: `domain_budgets` 차단 경로 근본 원인 확정과 실제 Engine Dispatch Lifecycle 검증

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0001`/`EVIDENCE-0002`/`EVIDENCE-0003`을 수정하지
않고, 이번에 새로 수행한 검증 결과만 **독립된 문서**로 기록한다.

## 1. 검증 목적

`EVIDENCE-0003` §5(`domain_budgets`)와 §6(Thin Caller v1 실제 Engine
lifecycle)이 남긴 두 개의 핵심 UNVERIFIED 항목을 한 번의 작업으로
해소한다.

1. `domain_budgets` 초과 시 실제 dispatch 이전 차단이 재현되지 않은
   원인을 확정한다(`EVIDENCE.md` §Open Issues 1, `EVIDENCE-0003` §5).
2. Thin Caller(`caller.py`)의 성공 응답·오류 매핑·cancellation
   lifecycle을 **실제(격리) OmniRoute 서버**를 통해 검증한다(기존
   `EVIDENCE.md` §Final Judgment의 "시도 안 함"/"UNVERIFIED" 두 행).

이 문서는 이 두 항목만 다룬다. `RT-0001`/`ADC-0010` 판단, Production
Adoption 여부는 기존 결론(무변경, 아래 §8)을 그대로 따른다.

## 2. 격리 조건

| 항목 | 값 |
|---|---|
| 실행 환경 | macOS(darwin), Python 3.9.6 stdlib, Node.js(OmniRoute 3.8.50 standalone `dist/server.js`) |
| `DATA_DIR` | 매 서버 인스턴스마다 완전히 새로운 scratchpad 하위 temporary directory(jarvis-os repository 밖, 실제 `~/.omniroute`와 분리) |
| 인증 | `OMNIROUTE_API_KEY` env var를 통한 test-only fake key만 사용(`env-key` 합성 메타데이터 경로, `EVIDENCE-0002`와 동일 방식) |
| Provider 자격증명 | 실제 provider connection·API key 없음. `ollama-local`(로컬 전용 registry, 고정 `localhost:11434` 기본 대상)에 대한 test-only placeholder row만 삽입 |
| 실제 provider egress | **0건**. 모든 "실제 dispatch" 검증은 필자가 직접 작성한 로컬 stdlib HTTP 서버(`local_double_server.py`, `127.0.0.1:11434`)를 대상으로 수행했다 — 외부 네트워크 호출 없음 |
| `blockedProviders` | 검증 시작 전 `key_value` 설정으로 12개 non-video NOAUTH provider id를 명시적으로 차단(§4) |
| 테스트 종료 후 처리 | 모든 프로세스 PID 기준 강제 종료 확인, `lsof`로 포트 미점유 재확인, temporary DATA_DIR 전체 삭제(`rm -rf`) |
| 실제 `~/.omniroute` 영향 관찰 | 검증 전후 `~/.omniroute/storage.sqlite` mtime(`1788605986`)·size(`2547712`바이트) 완전 동일 재확인 |

**분류**: 위 표 전체는 **Observation**(직접 실행·명령 출력으로 확인)이다.

## 3. `domain_budgets` 근본 원인 확정

### 3.1 이전 두 번의 실패(`EVIDENCE.md` 프로브 2, `EVIDENCE-0003` §5)의 재확인

`EVIDENCE-0003` §5는 timestamp 포맷(`datetime('now')` TEXT vs
epoch-ms INTEGER) 불일치를 유력 가설로 남기고 UNVERIFIED로
종결했다. 이번 검증에서 그 가설부터 실행으로 확인했다.

- epoch-ms 정수로 정확히 수정해 `EVIDENCE-0002`와 동일한 삽입 SQL을
  재현한 뒤 재기동 → **여전히 401**(429 아님). **timestamp 포맷 가설은
  기각됐다.**
- `PRAGMA wal_checkpoint(FULL)`로 WAL 파일을 완전히 메인 DB에 병합한
  뒤(`0-byte -wal` 확인) 재기동 → **여전히 wipe됨.** WAL 체크포인트
  타이밍 가설도 기각.
- graceful shutdown(`SIGTERM`, 정상 종료 대기)으로 재기동 → **여전히
  wipe됨.** ungraceful shutdown(`kill -9`) 가설도 기각.

### 3.2 확정된 원인: "health-check-repair"

새 `DATA_DIR`로 서버를 **처음** 기동하면 아무 repair도 실행되지
않는다. 그러나 **동일 `DATA_DIR`로 두 번째 이후 기동할 때마다**
서버 로그에 다음이 출력되며:

```
[DB] Backup created (health-check-repair): <DATA_DIR>/db_backups/db_<timestamp>_health-check-repair.sqlite
```

이 시점에 `domain_budgets`, `domain_cost_history`, `provider_connections`,
`api_keys` 네 테이블이 **전부 빈 테이블로 재설정**된다(`SELECT
COUNT(*)`로 재기동 직후 4개 테이블 모두 `0` 확인, 백업 파일에는
재기동 직전 삽입한 행이 그대로 남아 있음을 대조 확인). `key_value`
(설정)는 이 repair의 영향을 받지 않는다 — `blockedProviders` 등
설정값은 재기동 후에도 유지된다.

이 동작은 **timestamp 포맷·모델 문자열·WAL 상태·종료 방식과
무관하게** 100% 결정론적으로 재현됐다(§3.1의 네 가지 통제 변인을
모두 배제한 뒤에도 동일). 이 repair를 구현하는 실제 소스는 배포된
npm 패키지에 포함되지 않는다(컴파일된 `dist/server.js`에만 존재) —
따라서 이 확정은 **실행 관찰**이며 소스 레벨 확인은 아니다.

### 3.3 확정된 해결 방법과 실제 재현

**서버를 재기동하지 않고, 별도의 `sqlite3` CLI 연결로 서버가 실행
중인 상태에서 직접 행을 삽입**하면 health-check-repair가 전혀
실행되지 않는다(재기동 자체가 없으므로). 이 방법으로:

| 항목 | 값 |
|---|---|
| 상태 | 이미 기동 중인 프로세스(재기동 없음), 별도 `sqlite3` 연결로 `domain_budgets`(`daily_limit_usd=0.01`)·`domain_cost_history`(`cost=999.0`, epoch-ms timestamp) 행을 `api_key_id='env-key'`로 live insert |
| 요청 | `POST /api/v1/chat/completions`, fake API key |
| HTTP 상태 | **429** |
| `error.type` | `rate_limit_error` |
| `error.code` | `rate_limit_exceeded` |
| `error.message` | `Daily budget exceeded: $999.0000 / $0.01` |
| 서버 로그 | `[BudgetWarning]`/`POLICY: API key policy rejected` 계열만 출력. `[AUTO]`/`[COMBO]`/`[ROUTING]`/`[ProxyEgress]` **0건** |

`EVIDENCE-0002`가 확인한 차단 로직(`enforceApiKeyPolicy()` →
`validateBudget()` → `checkBudget()`, provider dispatch 이전 실행)이
그대로, 그리고 egress 없이 재현됐다 — `EVIDENCE-0002`의 PASS 판정과
정확히 같은 형태의 결과다.

### 3.4 남은 잔여 한계(미해결, 주 검증 대상 아님)

같은 API key에 대해 "budget 충분(대조군)" 케이스를 같은 프로세스
안에서 live `UPDATE`로 재현하려는 시도는 실패했다 — `getBudget()`이
첫 번째 초과-체크의 warning-emission 경로에서 채워 넣은 in-memory
`budgets` Map 캐시를 그대로 반환하기 때문에(직접 DB 갱신이 캐시를
무효화하지 않음), 재기동 없이는 대조군을 얻을 수 없다. 이 잔여 항목은
이번 작업의 두 UNVERIFIED 항목(§1) 중 어디에도 해당하지 않으므로
추가로 재현하지 않았다 — `EVIDENCE-0002`의 Process B(별도 fresh
프로세스로 대조군을 얻은 방식)가 이미 이 형태의 대조를 PASS로
확인해 두었다.

## 4. `blockedProviders`/NOAUTH 안전장치 재확인

실제 dispatch 검증(§5)에 앞서, `model:"auto"`의 zero-config egress
경로가 실제로 차단됐음을 **dispatch를 발생시키지 않는 read-only
endpoint**로 먼저 확인했다.

- `GET /api/v1/auto-combo/auto/candidates`(routing state를 변경하지
  않는 조회 전용 endpoint, `virtualFactory.createVirtualAutoCombo`와
  동일한 candidate pool 생성 로직을 공유)를 사용.
- `blockedProviders` 삽입 **전**: 13개 candidate, provider id 집합
  `{'opencode', 'felo-web'}`(= `AUTO_COMBO_NOAUTH_ALLOWLIST` 전체).
- 12개 non-video NOAUTH provider id(`opencode`, `felo-web` 포함, 비디오
  전용 `veoaifree-web` 제외)를 `key_value`에 `blockedProviders`로
  live 삽입 **후**: candidate **0개**, provider id 집합 `set()`.

이 확인은 실제 `chat/completions` 요청을 전혀 보내지 않고 이루어졌다
— egress 위험 없이 "plain-auto가 더 이상 NOAUTH provider를 후보로
포함하지 않는다"는 것을 직접 관찰로 확정했다. `REQUIRE_API_KEY`는
별도 역할(OmniRoute 자신에 대한 클라이언트 인증)이라는 `EVIDENCE-0003`
§1의 판단은 이번 검증에서 재확인 대상이 아니었고(소스 재확인 없이
기존 판단을 그대로 유지), 이번 §4·§5는 순수하게 `blockedProviders`의
효과만 다룬다.

## 5. 실제 Engine Dispatch Lifecycle 검증(local/controlled endpoint)

### 5.1 안전 설계

실제 서드파티 provider 대신, `LOCAL_PROVIDERS` registry의
`ollama-local`(고정 기본 대상 `http://localhost:11434/v1`, 이 저장소
소스에서 확인된 값)을 이용했다. 필자가 직접 작성한 stdlib
`http.server` 기반 로컬 서버(`local_double_server.py`)를 정확히 그
포트(`127.0.0.1:11434`)에 띄워, OmniRoute의 **실제 dispatch 코드
경로**(인증 확인 → connection 조회 → HTTP client 구성 → 요청 전달 →
응답 파싱)를 그대로 실행시키되, 그 목적지는 처음부터 끝까지
`localhost` 범위를 벗어나지 않는다. `provider_connections`에
`ollama-local`용 test-only placeholder row(`is_active=1`,
`api_key='local-test-placeholder-key'`) 하나만 삽입했다 — 이 row가
있어야 `hasUsableConnectionCredential()`이 통과해 dispatch가
진행된다.

`openai-compatible-*`/`anthropic-compatible-*` 동적 connection
방식은 그 base-URL 저장 메커니즘이 배포 소스에 존재하지 않아(compiled
전용) 의도적으로 사용하지 않았다 — `LOCAL_PROVIDERS`는 설계상
목적지가 항상 `localhost`로 고정되므로 이쪽이 더 낮은 위험의 선택이다.

### 5.2 성공 응답(success)

Thin Caller 자신의 코드(`caller.call_omniroute()`, curl이 아님)로
직접 호출했다.

```python
caller.call_omniroute(
    "hello", base_url="http://127.0.0.1:20320", api_key="dispatch-key-0001",
    model="ollama-local/test-model", timeout=10,
)
```

결과: `'REAL_OMNIROUTE_DISPATCH_TO_LOCAL_DOUBLE_OK'` — 로컬 서버가
반환하도록 지정해 둔 고유 문자열이 그대로 파싱되어 돌아왔고, 로컬
서버 자체 로그에서도 요청을 실제로 수신했음을 확인했다
(`received path=/v1/chat/completions body={'model': 'test-model', ...}`).
**PASS** — OmniRoute의 실제 dispatch·프록시 코드가 동작했고, Thin
Caller의 응답 파싱 로직이 실제(격리) 서버의 실제 응답 형태와
end-to-end로 맞물렸다.

### 5.3 오류 전달(error mapping)

로컬 서버를 `error500` 모드로 전환(업스트림이 HTTP 500 + synthetic
error JSON을 반환하도록)한 뒤 동일한 호출을 반복했다.

```
CAUGHT: OmniRouteProviderError - HTTP 500: {'error': {'message': '[500]: synthetic upstream failure', ...}}
```

**PASS** — 실제 OmniRoute가 업스트림 5xx를 그대로 전달했고, Thin
Caller의 `_parse_response_body()`가 이를 `OmniRouteProviderError`로
정확히 매핑했다. 이 오류 매핑은 이전까지 로컬 test double(`fake_server.py`)
로만 검증됐던 것으로, 이번이 **실제 OmniRoute 서버를 경유한 최초의
오류 매핑 확인**이다.

### 5.4 Cancellation/Status

로컬 서버를 `slow` 모드(응답 전 5초 지연)로 전환한 뒤,
`call_omniroute_async()`로 실제 서버에 요청을 보내고 즉시 취소했다.

```
status before cancel: pending
cancel() returned: True
status after cancel: cancelled
CAUGHT expected OmniRouteCancelledError: call was cancelled
```

**PASS** — 실제 네트워크 연결(`http.client` connection, 실제 OmniRoute
서버로의 실 TCP 연결)에 대해 `.cancel()`이 연결을 종료시키고 상태를
`cancelled`로 전이시켰으며, `.result()`가 `OmniRouteCancelledError`를
발생시켰다. 이 항목 역시 이전까지 로컬 test double로만 검증됐던
것으로, 이번이 **실제 OmniRoute 서버를 경유한 최초의 cancellation
확인**이다.

### 5.5 Case A 경계 재확인

로컬 test double 기반 26개 테스트(`test_caller_unit.py` 13개,
`test_caller_lifecycle.py` 5개, `test_case_a_boundary.py` 8개)를
이번 검증 종료 직전 재실행했다: **26 passed**(코드 변경 없음,
`EVIDENCE-0003` §6과 동일 결과). `test_case_a_boundary.py`가 정적으로
재확인하는 항목(단일 파일 구성, 두 번째 Engine hardcode 없음,
provider/routing 선택 로직 없음, `call_engine()` 미참조, `hqs/`
production path 무연결) 전부 이번 실제 dispatch 검증 동안에도 코드
수준에서 그대로 유지됐다 — §5.2~§5.4의 실제 서버 호출은 `caller.py`에
어떤 Routing/Fallback/Gateway 로직도 추가하지 않고 기존 함수를
그대로 호출한 것이다.

## 6. Final Judgment

| UNVERIFIED 항목(EVIDENCE-0003 기준) | 이번 판정 | 근거 |
|---|---|---|
| `domain_budgets` 차단 경로 | **PASS**(원인 확정 포함) | §3.2 근본 원인 확정, §3.3 실제 재현(429, egress 0건) |
| 실제 Engine 성공 응답 lifecycle | **PASS** | §5.2 |
| 실제 Engine 오류 전달 lifecycle | **PASS** | §5.3 |
| 실제 Engine cancellation/status lifecycle | **PASS** | §5.4 |
| Case A 경계(Thin Caller 코드 구조) | **PASS**(재확인, 무변경) | §5.5, 26/26 |

**두 UNVERIFIED 항목 모두 이번 작업으로 PASS로 확정한다.** 어느 것도
FAIL이나 잔여 UNVERIFIED로 남지 않았다(§3.4의 잔여 한계는 이번 두
항목의 범위 밖이다).

### 과장 방지

- `domain_budgets` PASS는 "OmniRoute standalone 서버가 재기동될 때마다
  운영 데이터를 초기화하는 health-check-repair 동작을 가진다"는
  **별도의, 이번에 새로 발견한 운영상 특성**을 동반한다 — 이것은
  budget 로직의 결함이 아니라 **테스트/재현 방법론이 반드시 고려해야
  할 서버 운영 특성**이다. Jarvis가 향후 실제 OmniRoute 인스턴스를
  운영/재기동할 경우, 이 repair가 실제 provider connection·budget
  설정까지 초기화할 위험이 있다는 것은 Production 운용 관점에서
  **별도로 다뤄야 할 사실**이며, 이 문서는 그 대응 방안을 제안하지
  않는다(§9).
- 실제 dispatch 검증(§5)은 **로컬/통제된 endpoint**를 대상으로
  했다 — 실제 서드파티 provider(OpenAI, Anthropic 등)와의 dispatch가
  동일하게 동작한다고 확대 해석하지 않는다. 이번 검증이 입증하는
  것은 OmniRoute의 **dispatch 파이프라인 자체**(인증 확인 → connection
  조회 → HTTP 전달 → 응답/오류 파싱)가 Thin Caller와 end-to-end로
  맞물린다는 것이지, 특정 실제 provider와의 호환성이 아니다.

## 7. `EVIDENCE-0002`/`EVIDENCE-0003`과의 차이

| 항목 | EVIDENCE-0002 | EVIDENCE-0003 | EVIDENCE-0004(이 문서) |
|---|---|---|---|
| `domain_budgets` 차단 재현 | PASS(정지→삽입→재기동 방식) | UNVERIFIED(timestamp 가설, 미실행) | **PASS**(근본 원인 확정 + 재기동 없이 재현) |
| 재현 방법론 | 정지→삽입→재기동 | (미실행) | **재기동 없이 live 삽입**(EVIDENCE-0002 방식은 이번 환경에서 health-check-repair로 인해 더 이상 신뢰할 수 없음이 확인됨) |
| 실제 Engine 성공 lifecycle | 대상 아님(별도 주제) | "시도 안 함"(test double로 대체) | **PASS**(실제 서버 + `caller.py` 직접 호출) |
| 실제 Engine 오류 lifecycle | budget 차단 오류만 확인 | UNVERIFIED | **PASS**(업스트림 5xx 매핑, 실제 서버) |
| cancellation lifecycle | 대상 아님 | test double로만 확인 | **PASS**(실제 서버) |
| `blockedProviders` 검증 방법 | 대상 아님 | 정적 분석만 | **실행 확인**(read-only endpoint, 13→0) |

이 문서는 `EVIDENCE-0002`의 정지→삽입→재기동 방법론이 **틀렸다**고
주장하지 않는다 — `EVIDENCE-0002` 실행 당시의 환경/빌드에서는 그
방식이 실제로 작동했을 수 있다(그 문서 자체가 실제 PASS 결과를
기록하고 있다). 이번 문서가 확정하는 것은 **이번 세션이 사용한
동일한 캐시된 3.8.50 standalone 빌드에서, 이번 검증 시점 기준으로는**
재기동이 health-check-repair를 트리거해 재현을 방해한다는 것이며,
그 회피 방법(재기동 없는 live 삽입)을 확립했다는 것이다.

## 8. `RT-0001`/`ADC-0010`/Architecture 영향

- `RT-0001`("Engine 수 ≥ 2") 재판단: **무변경**. 이번 문서가 새로
  발견한 health-check-repair 동작과 NOAUTH-egress 재확인은 모두
  OmniRoute 자체의 **운영 특성 확인**이며, Jarvis 쪽에 새로운 Engine이
  추가되거나 Thin Caller의 Case A 범위가 넓어진 사실이 아니다.
  `EVIDENCE-0003` §8의 판단(이 프로토타입은 여전히 단일 Engine, RT-0001
  트리거 아님)을 그대로 유지한다.
- `ADC-0010` C1 재판단: **무변경**. 이번 검증은 기존 Thin Caller
  코드에 어떤 줄도 추가·수정하지 않았다(§5.5) — Case A 경계 판단을
  바꿀 근거가 새로 생기지 않았다.
- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**. Governance 문서(`CONSTITUTION.md`/`BASELINE.md`/
  `IMPLEMENTATION_RULES.md`/`ARCHITECTURE_GOVERNANCE.md`) 변경: **없음**.
- 새로운 Jarvis측 Routing/Fallback/Gateway: **구현하지 않았다**. 이번
  작업 전체에서 수정된 Jarvis 저장소 파일은 **0개**다(§10).
- 이번에 발견한 health-check-repair 동작이 Architecture 재검토를
  요구하는지: **아니다로 판단한다** — 이것은 OmniRoute(외부
  Implementation Engine)의 내부 운영 동작이며, Jarvis의 Thin Caller
  코드·Case A 경계·Kernel Architecture 어디에도 영향을 주지 않는다.
  다만 향후 실제 Production 배포 시 이 특성을 운영 절차에서 고려해야
  한다는 점은 §9 Open Issues에 남긴다.

## 9. Evidence limitations / Open Issues

- health-check-repair의 정확한 트리거 조건(예: 특정 시간 간격, 특정
  파일 존재 여부 등)은 소스가 배포되지 않아 완전히 규명하지
  못했다 — "두 번째 이후 기동마다 발생한다"는 것은 4회의 독립
  재현으로 확인된 **관찰**이지, 소스 레벨 **증명**은 아니다.
- §3.4의 대조군(budget 충분) 잔여 한계는 미해결로 남긴다 —
  `EVIDENCE-0002`의 별도 fresh 프로세스 방식이 이미 이 형태의 대조를
  PASS로 확인해 두었으므로, 이번 두 UNVERIFIED 항목의 판정에는
  영향을 주지 않는다.
- `test_real_engine_budget_block.py`(기존 파일)는 여전히 구식(정지→
  삽입→재기동) 방법론과 이중 opt-in 게이트를 그대로 유지한다 — 이번
  검증은 그 파일을 실행하거나 수정하지 않았고, 대신 scratchpad에서의
  ad-hoc 재현으로 대체했다(§10 Provenance가 그 재현 절차의 유일한
  기록이다). 이 파일을 새 방법론으로 갱신할지, 폐기할지는 이 문서의
  권한 밖이며 별도 판단이 필요하다.
- 실제 서드파티 provider(OpenAI/Anthropic 등)와의 dispatch는 이번에도
  검증하지 않았다(의도적 — §6 과장 방지 참조).
- Production Adoption 여부는 이 문서의 범위 밖이다 — 이 문서는
  Experimental 프로토타입의 두 UNVERIFIED 항목만 해소한다.

## 10. Provenance / Reproducibility

- **검증 환경**: macOS(darwin), Python 3.9.6, OmniRoute 3.8.50
  standalone(`dist/server.js`, 이전 세션이 캐시해 둔 npm 패키지,
  volatile scratchpad 경로 — `EVIDENCE-0001` §1.1과 동일한 재현성
  한계).
- **domain_budgets 재현(§3.3)**: `DATA_DIR=<isolated> NODE_ENV=test
  OMNIROUTE_ALLOW_DEFAULT_DATA_DIR=0 OMNIROUTE_API_KEY=<fake> PORT=<free>
  HOSTNAME=127.0.0.1 node dist/server.js`로 기동(최초 1회만, 이후
  재기동 없음) → 별도 `sqlite3 <DATA_DIR>/storage.sqlite` 연결로
  `domain_budgets`/`domain_cost_history` INSERT(서버는 계속 실행
  상태) → 동일 서버에 `POST /api/v1/chat/completions` 요청.
- **`blockedProviders` 확인(§4)**: 동일 방식으로 `key_value` 테이블에
  `blockedProviders` JSON 배열 삽입(서버 재기동 없음, `key_value`는
  repair 영향 없음이 이미 확인됨) → `GET
  /api/v1/auto-combo/auto/candidates` 전후 비교.
- **실제 dispatch lifecycle(§5)**: 별도 격리 인스턴스(`DATA_DIR` 별도,
  `blockedProviders` 동일 적용) + `provider_connections`에
  `ollama-local` test-only row 삽입(서버 재기동 없음) + 로컬
  `python3 http.server` 기반 더블 서버(`127.0.0.1:11434`, success/
  error500/slow 세 모드)를 순서대로 기동/전환하며 `caller.py`의
  `call_omniroute()`/`call_omniroute_async()`를 직접 호출.
- **cleanup 결과**: 이번 작업에서 기동한 모든 프로세스(OmniRoute
  standalone 서버 2개 인스턴스, 로컬 더블 서버 1개) PID 기준 강제
  종료 확인, 모든 임시 `DATA_DIR`·scratchpad 스크립트 `rm -rf`로
  완전 삭제, `lsof`로 관련 포트 전부 미점유 재확인, 실제
  `~/.omniroute/storage.sqlite` mtime(`1788605986`)·size(`2547712`)가
  검증 시작 전과 완전히 동일함을 최종 재확인.
- **Jarvis 저장소 변경**: 이 문서(`EVIDENCE-0004`) 추가 1건 외
  **없음**. `caller.py`·`tests/`·`README.md`·`EVIDENCE.md`·
  Governance 문서 어느 것도 수정하지 않았다.

## Self Review

- 실행 결과와 문서 내용이 정확히 일치하는가 — **Pass**. §3·§4·§5의
  모든 관찰값(HTTP 상태·오류 메시지·candidate 개수·문자열 결과)은
  실제 실행에서 얻은 값을 그대로 옮겼다.
- 두 UNVERIFIED 항목 모두 실제로 PASS로 확정할 근거가 있는가 —
  **있다**(§3.3 실제 429 재현 + 원인 확정, §5.2~5.4 실제 서버 경유
  성공/오류/취소 3종 모두 확인).
- PASS 범위를 과장했는가 — **아니오**. §6에서 health-check-repair가
  budget 로직 결함이 아니라는 것, §5가 실제 서드파티 provider가 아닌
  local/controlled endpoint 대상이라는 것을 명시적으로 분리했다.
- 실제 provider/실제 비용 발생이 있었는가 — **없다**. 모든 dispatch
  대상은 필자가 직접 작성한 `127.0.0.1:11434` 로컬 서버였다(§5.1).
- 실제 `~/.omniroute` 데이터·credential을 건드렸는가 — **아니다**
  (§10 cleanup 결과, mtime/size 완전 동일).
- 새 Routing/Fallback/Gateway를 Jarvis에 구현했는가 — **아니오**
  (§8, §10 — 저장소 변경은 이 문서 추가 1건뿐).
- Case A 경계가 계속 유지되는가 — **그렇다**(§5.5, 26/26 재확인,
  코드 변경 없음).
- Architecture/Contract/Freeze 변경이 있는가 — **아니오**(§8).
- `RT-0001`/`ADC-0010` 판단을 변경했는가 — **아니오**, 무변경으로
  재확인했다(§8).
- `EVIDENCE-0001`/`0002`/`0003`을 수정했는가 — **아니오**. 이 문서는
  그것들과 독립된 새 문서다.
- Production Adoption을 선언했는가 — **아니오**(§9에서 범위 밖임을
  명시).
- 새로운 테스트 코드나 production code를 추가했는가 — **아니오** —
  격리 환경에서의 1회성 수동 검증이었고, `caller.py`나 `tests/`에
  어떤 파일도 추가·수정하지 않았다. `test_real_engine_budget_block.py`
  는 구식 상태로 남아 있으며 이번에 실행·수정하지 않았다(§9에 명시).
- commit/push/PR을 수행했는가 — **아니오**.
