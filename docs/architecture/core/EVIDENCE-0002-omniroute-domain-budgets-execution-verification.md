# EVIDENCE-0002: `domain_budgets` 실제 Blocking Execution 검증 (ADC-0027 후속)

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0001-omniroute-precondition-verification.md`은
자신을 "이 문서 작성 시점 이후 새 Observation을 추가하지 않는"
frozen snapshot으로 선언했다 — 이 문서는 그 원칙을 지키기 위해
`EVIDENCE-0001`을 수정하지 않고, 이번에 새로 수행한 검증 결과만
**독립된 문서**로 기록한다.

## 1. 검증 목적

`ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
§Decision "구현 착수 선행조건" 3번("`domain_budgets` 검증: UNVERIFIED
상태를 PASS/FAIL 중 하나로 확정한다")에 대해, `EVIDENCE-0001` §3.5가
"enforcement 로직의 존재와 배선은 검증됐으나, 한도를 넘었을 때 실제로
차단하는가"라는 핵심 동작은 검증되지 않았다"고 남긴 공백을, **실제
execution level에서 PASS 가능한지** 검증한다. 이 문서는 그 검증
결과만 기록하며, `ADC-0027`의 Decision이나 다른 선행조건을 재론하지
않는다.

## 2. 격리 조건

| 항목 | 값 |
|---|---|
| `DATA_DIR` | 완전히 새로운 temporary directory(jarvis-os repository 밖, 실제 `~/.omniroute`와 분리된 scratchpad 하위 경로) |
| OmniRoute 버전 | `3.8.50` standalone server(`dist/server.js`, 컴파일된 Next.js standalone 빌드) |
| 인증 방식 | `OMNIROUTE_API_KEY` env var를 통한 test-only fake key(`isConfiguredEnvApiKey()` 경로, 합성 `id: "env-key"`) — 실제 DB-backed API key를 생성하지 않았다 |
| Provider 자격증명 | 사용하지 않음 — 실제 provider connection·API key를 전혀 구성하지 않았다 |
| 테스트 종료 후 처리 | 프로세스 전부 종료 확인(`lsof`로 포트 미점유 재확인), temporary DATA_DIR 전체 삭제(`rm -rf`) |
| 실제 `~/.omniroute` 영향 관찰 | 검증 전후 `~/.omniroute/storage.sqlite`의 mtime·파일 크기 불변 확인(모두 `Sep 5 19:59`, `2547712`바이트로 동일), `domain_budgets`/`domain_cost_history` row count 검증 전후 모두 `0`으로 불변 확인 |

**분류**: 위 표 전체는 **Observation**(직접 실행·명령 출력으로 확인)이다.

## 3. Source-level 근거

아래 다섯 지점을 실제 소스에서 확인했다 — 각 근거가 정확히 무엇을
입증하는지와 무엇을 입증하지 않는지를 구분한다.

- **`src/lib/dataPaths.ts::resolveDataDir()`(64행)**: `process.env.DATA_DIR`이
  설정되면 그 값을 최우선으로 반환한다. **입증하는 것**: DATA_DIR
  override가 실제로 존재하는 공식 메커니즘이며, 이를 통해 실제
  `~/.omniroute`를 전혀 참조하지 않는 완전한 격리 인스턴스를 구성할
  수 있다. **입증하지 않는 것**: 이 함수 자체는 budget 로직과 무관하다
  — 격리 방법의 근거일 뿐이다.
- **`src/lib/db/apiKeys.ts::isConfiguredEnvApiKey()`(264행)`/`getApiKeyMetadata()`(1310행)**:
  `OMNIROUTE_API_KEY`(또는 `ROUTER_API_KEY`)와 일치하는 키가 오면
  DB 조회 없이 합성 `ApiKeyMetadata`(`id: "env-key"`)를 반환한다.
  **입증하는 것**: 실제 DB-backed API key를 생성하지 않고도
  `enforceApiKeyPolicy()` 경로에 진입할 수 있는 공식적인 테스트/운영
  경로가 존재한다. **입증하지 않는 것**: 이 경로가 실제 사용자가
  만드는 일반 API key의 budget 처리와 완전히 동일한 코드 경로를
  타는지는, 이 문서가 확인한 범위(§4 Process A/B) 안에서는 동일하게
  관찰됐다는 것 이상을 주장하지 않는다 — `checkBudget(apiKeyInfo.id)`
  호출에서 `apiKeyInfo.id`는 env-key 경로든 DB-backed 경로든 동일하게
  문자열 id 하나를 넘길 뿐이다.
- **`src/lib/db/domainState.ts`**: `domain_budgets`
  (`api_key_id, daily_limit_usd, weekly_limit_usd, monthly_limit_usd,
  warning_threshold, reset_interval, reset_time, budget_reset_at,
  last_budget_reset_at, warning_emitted_at, warning_period_start`,
  `saveBudget()` 199행/`loadBudget()` 237행)와 `domain_cost_history`
  (`api_key_id, cost, timestamp`, INSERT 376·391행)의 정확한 스키마를
  확인했다. **입증하는 것**: 이 문서 §4의 SQL INSERT가 실제 앱이
  기대하는 컬럼 형식과 일치한다는 것. **입증하지 않는 것**: 스키마
  존재 자체는 `EVIDENCE-0001` §3.5가 이미 확인했다 — 이 문서의 기여는
  스키마가 아니라 그 스키마 위에서 일어나는 실제 실행 동작이다.
- **`src/domain/costRules.ts::checkBudget()`(437행)`, `getBudgetWindowTotal()`(239행),
  차단 분기(485행 `if (activeLimitUsd > 0 && projectedTotal > activeLimitUsd)`)**:
  `periodUsed`(`domain_cost_history` 누적 합)와 `additionalCost`의 합이
  `activeLimitUsd`를 넘으면 `{ allowed: false, reason: "...budget
  exceeded: $X / $Y" }`를 반환한다. **입증하는 것**: §4 Process A의
  응답 메시지 포맷이 이 코드의 정확한 출력과 일치한다는 것. **입증하지
  않는 것**: 이 함수 자체는 `additionalCost`를 받을 수 있게 설계돼
  있다 — 그러나 실제로 그 값이 전달되는지는 호출부(아래) 확인이
  필요하다.
- **`src/shared/utils/apiKeyPolicy.ts::validateBudget()`(582행,
  `checkBudget(apiKeyInfo.id)` 호출은 586행)`/`enforceApiKeyPolicy()`(667행)**:
  **결정적 확인** — 586행의 호출은 `checkBudget(apiKeyInfo.id)`이며
  두 번째 인자(`additionalCost`)를 전달하지 않는다. `checkBudget()`
  시그니처(437행)의 기본값 `additionalCost = 0`이 그대로 적용된다.
  **입증하는 것**: 이 pre-flight 차단이 "이번 요청의 예상 비용"이
  아니라 **이미 기록된 과거 누적 spend(`domain_cost_history`)만으로**
  판단된다는 것 — §5 Final Judgment의 범위 제한이 이 확인에서
  직접 도출된다.

## 4. Execution Evidence

두 개의 독립된 fresh process에서 각각 정확히 한 번의 요청을 관찰했다.
(재현 시 두 번째 프로세스를 반드시 완전히 새 PID로 기동해야 한다 —
검증 중 기존 프로세스가 완전히 종료되지 않은 상태에서 DB만 갱신한
중간 시도는 이전 프로세스의 in-memory budget 캐시(`costRules.ts`
`budgets` Map)로 인해 갱신 전 값을 계속 반환했다 — 이는 프로세스를
PID 기준으로 강제 종료 후 재시도해 해소했다. 이 캐시 동작 자체는
이 문서의 검증 대상이 아니므로 판정에 반영하지 않는다.)

### Process A — budget 초과 상태

| 항목 | 값 |
|---|---|
| 상태 | fresh process(신규 기동 직후 첫 요청) |
| `daily_limit_usd` | `0.01` |
| 기존 spend(`domain_cost_history`) | `999.0` |
| 요청 대상 | 존재하지 않는 provider/model 문자열(fake) |
| HTTP 상태 | `429` |
| `error.type` | `rate_limit_error` |
| `error.code` | `rate_limit_exceeded` |
| `error.message` | `Daily budget exceeded: $999.0000 / $0.01` |

메시지 포맷이 `checkBudget()`(485~501행)의 실제 반환값 형식과 정확히
일치한다 — **provider 자격증명 조회·provider execution 단계에
도달하기 전에** 차단이 발생했다(§3 근거와의 정합).

### Process B — budget 충분 상태(대조군)

| 항목 | 값 |
|---|---|
| 상태 | Process A와 완전히 별도의 fresh process(신규 기동 직후 첫 요청) |
| `daily_limit_usd` | `10000` |
| 기존 spend(`domain_cost_history`) | `999.0`(Process A와 동일) |
| 요청 대상 | Process A와 동일한 fake provider/model 문자열 |
| HTTP 상태 | `401` |
| `error.type` | `authentication_error` |
| `error.code` | `invalid_api_key` |
| `error.message` | `No active credentials for provider: doesnotexist-provider.` |

budget 검사를 통과해 **다음 단계(provider 자격증명 조회)까지 진행**한
뒤, 그 단계에서 예상대로 실패했다 — budget이 원인이 아닌, 완전히
별개의 오류 타입·코드·상태다.

**A/B 대조의 의미**: 두 프로세스는 fake provider/model·인증 방식·기존
spend가 동일하고 **오직 `daily_limit_usd` 하나만 다르다.** 그 결과로
나온 오류의 종류(rate_limit_error/429 vs authentication_error/401)가
서로 다르다는 것은, 관찰된 차단이 budget 로직 자체에서 발생했다는
것을 가리키는 대조 Evidence다 — 이 요청이 provider 미존재 때문에
우연히 429를 받았거나, budget 로직과 무관한 다른 이유로 차단됐을
가능성을 배제한다.

## 5. Final Judgment

**PASS.**

- **PASS가 의미하는 것**: 기존 누적 spend(`domain_cost_history`)가
  `daily_limit_usd`를 초과한 상태에서, `enforceApiKeyPolicy()` →
  `validateBudget()` → `checkBudget()` 경로가 실제로 provider 호출
  이전 단계에서 요청을 차단하는 것이 격리 환경의 실제 실행으로
  확인됐다.
- **PASS가 의미하지 않는 것**: 이번 요청 자체의 예상 비용
  (additional cost)을 pre-flight에서 계산해 차단한다는 뜻이 아니다.
  §3 근거에서 확인했듯 `validateBudget()`(586행)은 `checkBudget()`을
  `additionalCost` 없이(기본값 0) 호출한다 — 즉 이번 검증이 확인한
  것은 **"이미 초과된 누적 spend 기준의 차단"**이며, "이번 요청
  비용까지 반영한 사전 계산형 차단"은 검증되지 않았고 현재 호출부
  구조상 애초에 그렇게 동작하지 않는다.
- 이 결과를 "budget system 전체가 검증됐다"고 확대 해석하지 않는다
  — `warningReached`/`warning threshold`/기간 리셋(`resetInterval`/
  `resetTime`) 로직, 여러 API key 동시 사용 시나리오, 실제 사용자
  생성 API key(DB-backed, env-key 아님) 경로의 완전한 재현은 이 문서
  범위 밖이다.

## 6. ADC-0027 영향

- `domain_budgets`: **UNVERIFIED → PASS**(이번 §4 Execution Evidence
  기준).
- `ADC-0027` §Decision "구현 착수 선행조건" 3번은 이번 실행 Evidence로
  해소 가능한 상태가 됐다.
- **`ADC-0027` 자체는 이 문서가 수정하지 않는다** — 문서 반영은
  별도 지시가 있을 때 진행한다.

## 7. 다른 조건(이번 Evidence로 변경되지 않음)

- `routing_decisions`: FAIL / BLOCKING(무변경).
- `priority` differential selection: UNVERIFIED(무변경).
- `IMPLEMENTATION_RULES.md`: 판단보류(무변경).
- `domain_fallback_chains`: `ADC-0028`이 이미 별도로 처리한 상태 그대로
  (무변경).
- OmniRoute integration: 미착수.
- ADR: 미작성.

## 8. Governance / Architecture

- Architecture 변경: **없음**.
- Contract 변경: **없음**.
- Freeze 변경: **없음**.
- Governance 문서(`CONSTITUTION.md`/`BASELINE.md`/
  `IMPLEMENTATION_RULES.md`/`ARCHITECTURE_GOVERNANCE.md`) 변경:
  **없음**.
- OmniRoute 실제 소스 수정: **없음**(캐시된 소스를 읽고 격리된 임시
  DB만 조작했다).

## 9. Evidence limitations

- 이 검증은 이전 세션의 임시 scratchpad에 남아 있던 OmniRoute
  `3.8.50` standalone 소스/컴파일 산출물을 대상으로 수행했다 —
  `EVIDENCE-0001` §1.1이 이미 지적한 것과 동일한 재현성 한계(휘발성
  경로, 라이브 서버 버전과의 완전한 동일성 미보증)가 이 문서에도
  동일하게 적용된다.
- 실제 provider 호출은 의도적으로 하지 않았다 — fake provider
  문자열을 사용해 budget 차단 여부만 관찰했다.
- 이 Evidence가 입증하는 것은 **`domain_budgets` pre-flight blocking
  behavior의 실제 동작**이지, 전체 OmniRoute routing system의
  production readiness가 아니다. `routing_decisions`·`priority`
  차등 selection 등 다른 미결 조건은 이 문서로 전혀 해소되지 않는다.
- env-key(합성 메타데이터) 경로로 얻은 결과이며, 일반 사용자가 대시보드로
  생성하는 DB-backed API key의 budget 처리 경로를 별도로 재현하지는
  않았다(§3 참조).

## 10. Provenance / Reproducibility

재현에 필요한 전체 조건을 기록한다.

- **검증 환경**: macOS(darwin arm64), Node.js `v24.18.0`, OmniRoute
  `3.8.50`(standalone 컴파일 빌드, `dist/server.js` + `dist/.build/next`),
  `better-sqlite3` prebuild `darwin-arm64.node` 사용.
- **격리 DATA_DIR**: scratchpad 하위 신규 temporary 디렉터리(테스트
  종료 후 `rm -rf`로 완전 삭제, 재현 불가 — 필요 시 동일 절차로
  새 디렉터리를 다시 생성해야 한다).
- **기동 커맨드 형태**: `DATA_DIR=<isolated> NODE_ENV=test
  OMNIROUTE_ALLOW_DEFAULT_DATA_DIR=0
  OMNIROUTE_API_KEY=<test-only-fake-key> PORT=<free-port>
  HOSTNAME=127.0.0.1 node dist/server.js`.
- **테스트 데이터 삽입(SQL)**: 서버를 정지한 상태에서
  `domain_budgets`에 `api_key_id='env-key'` 행을 `daily_limit_usd`만
  다르게(Process A: `0.01`, Process B: `10000`) 삽입, `domain_cost_history`에
  `api_key_id='env-key', cost=999.0, timestamp=<현재 시각 ms>` 행을
  삽입한 뒤 서버를 재기동.
- **요청**: `POST /api/v1/chat/completions`,
  `Authorization: Bearer <test-only-fake-key>`,
  body `{"model":"<존재하지 않는 provider>/<존재하지 않는 model>",
  "messages":[...]}`.
- **관찰된 HTTP 응답**: §4 표 참조(Process A/B 각각 1건씩, 총 2건).
- **cleanup 결과**: 두 프로세스 모두 PID 기준 강제 종료, `lsof`로
  포트 미점유 재확인, 격리 DATA_DIR `rm -rf` 완료, 실제
  `~/.omniroute/storage.sqlite` mtime·크기 불변 및 `domain_budgets`/
  `domain_cost_history` row count `0`/`0` 불변 재확인(검증 전후 동일).

## Self Review

- 실행 결과와 문서 내용이 정확히 일치하는가 — **Pass**. §4의 HTTP
  상태·`error.type`·`error.code`·`error.message`는 실제 관찰된 응답을
  그대로 옮겼다.
- PASS 범위를 과장했는가 — **아니오**. §5에서 "의미하는 것"과
  "의미하지 않는 것"을 명시적으로 분리했고, §9에서 전체 routing
  system의 production readiness가 아님을 재확인했다.
- `additionalCost` 미전달 사실이 정확히 표현됐는가 — **Pass**(§3
  마지막 항목, §5 두 번째 불릿에서 각각 명시).
- 실제 provider/credential 접근이 없었다는 표현이 검증 범위를 넘어가는가 —
  **아니오**. §2·§9에서 "fake provider 문자열을 사용해 provider
  자격증명 조회 단계에서 즉시 실패했다"는 관찰 수준으로만 서술했고,
  "provider 호출이 전혀 발생하지 않는다"는 일반화된 주장을 하지
  않았다.
- `ADC-0027`의 다른 Blocking 조건을 잘못 해소했는가 — **아니오**(§7에서
  전부 무변경으로 명시).
- `EVIDENCE-0001`과 충돌하는가 — **아니오**. `EVIDENCE-0001` §3.5의
  "배선은 확인, 실동작은 미확인"이라는 판정을 뒤집은 것이 아니라
  그 미확인 부분을 이번에 실제로 확인해 보완했다 — `EVIDENCE-0001`
  파일 자체는 수정하지 않았다.
- Architecture/Contract/Freeze 변경이 있는가 — **아니오**(§8).
- `ADC-0027`/`ADC-0028`을 수정했는가 — **아니오**.
- OmniRoute integration을 시작했는가 — **아니오**.
- ADR을 작성했는가 — **아니오**.
- 새로운 테스트 코드나 production code를 추가했는가 — **아니오** —
  격리 환경에서의 1회성 수동 검증이었고, 어떤 코드도 저장소에
  추가하지 않았다.
- commit/push/PR을 수행했는가 — **아니오**.
