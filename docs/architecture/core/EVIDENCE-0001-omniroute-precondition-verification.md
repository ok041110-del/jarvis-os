# EVIDENCE-0001: OmniRoute 구현 착수 선행조건 검증 (ADC-0027 후속)

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. 새 Observation을 이 문서 작성 시점 이후로 추가하지 않는다 —
아래 검증 시점에 실제로 확인한 것만 기록한다.

**목적**: `docs/architecture/core/ADC-0027-omniroute-model-routing-engine-adapter-conditional-adoption.md`
"구현 착수 선행조건" 1~4의 현재 충족 여부를, 이전 세션 보고(§3.1 PASS
4/FAIL 3/UNVERIFIED 1)를 재인용하지 않고 **실제 코드·DB·로그를
직접 대조**해 재확인한 결과를 저장소에 재현 가능한 형태로 보존한다.
이 문서가 존재하는 이유 자체가 `ADC-0027` §Q6·§Risks("Audit 영속성")가
지적한 공백 — "5라운드 검증 결과가 저장소에 재현 가능한 형태로
영속화되지 않았다" — 을 메우는 것이다.

**ADC-0027과의 관계**: 이 문서는 `ADC-0027`의 Decision을 변경하지
않는다. `ADC-0027` "구현 착수 선행조건" 1(Evidence 영속화)을
**충족시키는 산출물**이며, 나머지 선행조건 2~4(FAIL 재해소,
`domain_budgets` 확정, `IMPLEMENTATION_RULES.md` Scoped 완화)의
충족 여부에 대한 **최신 재확인 결과**를 기록한다 — 그 판단이
`ADC-0027`을 재론하거나 확정하지 않는다는 것은 동일하다.

## 분류 규칙

| 분류 | 기준 |
|---|---|
| **Observation (OB)** | 파일 경로·라인·명령 출력에서 **직접 읽어 확인**할 수 있는 것. 유한 범위 전수 검색으로 확인된 부재도 Observation이다 |
| **Interpretation (IN)** | 그 사실로부터의 추론·평가·연결 |

---

## 1. 검증 환경

| 항목 | 내용 |
|---|---|
| OmniRoute 소스 버전 (읽은 코드) | `3.8.50`(`package.json` `"version"` 필드, OB-1) |
| OmniRoute 라이브 서버 버전 | **미확인** — `~/.omniroute/server/`에는 `.pid` 파일 하나만 있고 버전 기록 파일이 없다(OB-2). `.claude/docs/SMOKE_TEST-2026-08-08.md`는 2026-08-08 시점 `3.8.49`를 기록했다 — 이 문서의 검증 시점(아래)과는 다른 세션·다른 날짜의 기록이다 |
| 검증 시점 | 2026-09-06 (이 문서 작성 시점). 대조에 사용한 라이브 데이터는 그 이전 시점(call_logs·app.log 타임스탬프 2026-09-05T03:35~10:33Z, OB-3)에 생성된 것이다 |
| SQLite DB 위치 | `~/.omniroute/storage.sqlite` (사용자 로컬 머신, jarvis-os repo 밖) |
| 로그 위치 | `~/.omniroute/logs/application/app.log` (2201줄, OB-4) |
| 소스 코드 위치 | `/private/tmp/claude-501/-Users-chan-Developer-jarvis-os/5ce390ee-d07e-47e5-ae03-ef17b00078ff/scratchpad/npm-cache-omniroute/_npx/44b85dff014d9ceb/node_modules/omniroute` — **이전(다른) 세션의 임시 scratchpad에 남은 `npx omniroute` 설치 캐시** |
| OmniRoute 서버 프로세스 | 검증 시점 기준 미기동 — `.pid` 파일의 PID(36678)에 해당하는 프로세스 없음, `lsof` 상 리스닝 포트 없음(OB-5). **이 문서의 모든 확인은 정적 코드 분석 + 과거 실행이 남긴 DB/로그이지, 이번 세션이 새로 실행한 live request가 아니다** |

### 1.1 source artifact의 출처와 한계 (반드시 읽을 것)

- **§8 "임시 scratchpad 경로를 영구 Evidence source처럼 표현하지 않는다"에 대한 명시적 답**: 위 소스 코드 경로는 세션 ID `5ce390ee-d07e-47e5-ae03-ef17b00078ff`의 `/private/tmp/claude-501/...` 임시 디렉터리다. `/private/tmp`는 **컨테이너/세션 재시작 시 소거될 수 있는 휘발성 경로**이며, 이 문서가 인용하는 라인 번호·인용문은 **이 문서 작성 시점에 그 경로가 우연히 아직 존재했기 때문에** 읽을 수 있었던 것이다. 이 경로는 jarvis-os repo의 일부가 아니고, 이 문서가 그 경로를 향후에도 다시 읽을 수 있다고 보장하지 않는다.
- **재현성 문제(§9)**: 따라서 이 문서에 인용된 코드 스니펫 자체가 **1차 원본이 아니라 이 문서가 대신 보존하는 사본**이다. 원본(`/private/tmp/.../node_modules/omniroute/src/...`)이 사라지면, 이 문서에 인용된 코드 블록만이 남는 유일한 기록이 된다 — 이는 이상적인 Evidence 관리가 아니라 **차선책**이다. 진짜 해결책은 검증용 OmniRoute 소스 사본(또는 최소한 관련 파일)을 별도 프로세스로 jarvis-os repo 밖의 안정적인 위치(또는 `projects/` 격리 환경)에 고정하는 것이며, 이 문서는 그 작업을 대신하지 않는다.
- **버전 동일성 미보증**: `~/.omniroute/storage.sqlite`를 만든 실제 서버 바이너리가 정확히 이 `3.8.50` 소스와 동일한 빌드였다는 직접 증거는 없다(위 표 참조) — 버전 근접성(3.8.49 → 3.8.50)과 같은 사용자 환경(`~/.omniroute` 단일 데이터 디렉터리)이라는 정황 증거만 있다. 이는 **Interpretation**이며 Observation이 아니다.
- **Live execution 미수행**: 이 문서를 작성하며 OmniRoute 서버를 새로 기동하거나 실제 Provider에 새 요청을 보내지 않았다(지시 "OmniRoute 통합 구현도 수행하지 않는다" 준수). 아래 모든 "live execution 여부" 항목은 **과거에 실제로 발생한 요청의 흔적(`call_logs` 78건, `app.log`)**을 근거로 하며, 이 세션이 직접 관찰한 실시간 실행이 아니다.

---

## 2. Evidence Matrix

| 조건 | 판정 | 구현 착수 영향 |
|---|---|---|
| Evidence 영속화 | **FAIL**(이 문서 작성 이전 기준) → 이 문서가 부분 해소 | 이 문서 자체가 조치 |
| `provider_connections.priority` | **PASS** | Blocking 아님(단, 차등 데이터 재검증 권장) |
| `domain_fallback_chains` | **FAIL** | BLOCKING |
| `routing_decisions` | **FAIL** | BLOCKING |
| `domain_budgets` | **UNVERIFIED** | BLOCKING(실동작 미확인) |
| `IMPLEMENTATION_RULES.md` Scoped 완화 필요 여부 | **UNVERIFIED**(판단 보류) | 별도 설계 결정 선행 필요 |

이 판정은 이전 턴(Evidence Review)의 결론을 **그대로 유지**한다 — 이
문서 작성 과정에서 새로 발견한 사실(§3.3 caller chain 등)로 판정을
뒤집지 않았다.

---

## 3. 상세 결과

### 3.1 Evidence 영속화

- **판정**: FAIL(이 문서 작성 전) — jarvis-os repo 안에 5라운드 검증
  결과나 이번 재검증 결과를 재현 가능한 형태로 기록한 문서가
  이전에는 없었다.
- **이 문서가 하는 것**: 이번 재검증에서 실제로 확인한 코드 경로·
  caller chain·DB row count·로그 발췌를 §1·§3.2~§3.6에 원문 인용
  형태로 고정한다.
- **이 문서가 하지 않는 것**: 원본 소스 코드 자체를 repo에 복사하지
  않는다(라이선스·용량·"OmniRoute 구현 금지" 지시와 충돌 가능성).
  `~/.omniroute/storage.sqlite`도 복사하지 않는다(개인 계정 데이터
  포함 가능). 따라서 이 문서 자체도 **완전한 재현성**을 제공하지
  않는다 — §1.1 참조.

### 3.2 `provider_connections.priority`

- **판정**: **PASS**
- **DB 상태(OB-6)**: `provider_connections` 4 rows. 전부
  `priority = 1`, `global_priority`는 전부 NULL(빈 문자열로 표시).
  Provider: `kimi-coding`, `moonshot`, `codex`, `claude` — 각 Provider당
  connection이 1개뿐이다.
  ```
  9d57b506-...|kimi-coding|1||1|2026-09-05T03:39:39.288Z
  65144ab9-...|moonshot   |1||1|2026-09-05T03:38:33.610Z
  fa71079b-...|codex      |1||1|2026-09-05T03:36:26.632Z
  0714594b-...|claude     |1||1|2026-09-05T03:35:34.704Z
  ```
- **Source/code path(OB-7)**: `src/lib/db/providers.ts` 함수
  `getRawProviderConnections()`(244행 정의) 내부 283행 SQL:
  ```
  sql += " ORDER BY priority ASC, updated_at DESC";
  ```
  같은 함수 docstring 237행: *"Used by the lazy-decryption
  path in auth selection (auth.ts) where 10k+ connections are
  filtered in JS but only 1 needs its apiKey decrypted."*
- **Caller chain(OB-8, 3-hop 확인)**:
  `src/sse/handlers/chat.ts`(실 SSE chat 요청 핸들러, `enforceApiKeyPolicy`
  호출부와 동일 파일) → `src/lib/db/readCache.ts`(`dbCache`, 요청마다
  호출되는 5초 TTL 캐시, 파일 헤더: *"some functions (getSettings,
  getPricing, getProviderConnections) are called on every request by
  multiple callers"*) → `src/lib/db/providers.ts::getRawProviderConnections()`.
  `src/sse/services/auth.ts`도 `readCache.ts`를 import한다(OB-9,
  `grep -rln "from.*db/readCache" src` 결과에 `sse/services/auth.ts`,
  `sse/handlers/chat.ts` 포함).
- **Live execution 여부**: **경로는 실행됐다(call_logs 78건이 실제
  connection을 통해 처리됐으므로 이 코드 경로 자체는 매 요청 통과).
  그러나 "priority 값 차이가 실제로 선택 결과를 바꾼다"는 것은
  관찰되지 않았다** — 현재 DB에 Provider당 connection이 1개씩뿐이고
  priority가 전부 동일(1)하기 때문에, `ORDER BY priority`가 있으나
  없으나 정렬 결과가 달라질 수 없는 상태다(OB-6과 OB-7의 논리적 결합,
  Interpretation).
- **구현 착수 영향**: Blocking 아님. 다만 "priority가 실제 후보
  선정에 영향을 준다"는 것을 **행동으로** 확인하려면, 동일 Provider에
  서로 다른 priority 값을 가진 connection 2개 이상을 등록하고 실제
  선택 결과를 재검증해야 한다(§4 권고).

### 3.3 `domain_fallback_chains`

- **판정**: **FAIL**
- **DB 상태(OB-10)**: 0 rows.
- **Schema(OB-11)**: `CREATE TABLE domain_fallback_chains (model TEXT
  PRIMARY KEY, chain TEXT NOT NULL)`.
- **저장 계층(OB-12)**: `src/lib/db/domainState.ts` — 파일 헤더 주석:
  *"Tables: domain_fallback_chains, domain_budgets, domain_cost_history,
  domain_lockout_state, domain_circuit_breakers"*. 함수
  `saveFallbackChain(model, chain)`(135행)이 실제
  `INSERT OR REPLACE INTO domain_fallback_chains (model, chain) VALUES (?, ?)`를
  실행하고, `loadFallbackChain`(148행)·`loadAllFallbackChains`(159행)이
  `SELECT`를 실행한다 — **이 계층은 스텁이 아니라 실제로 SQL을
  실행하는 코드다.**
- **1차 caller(OB-13)**: `src/domain/fallbackPolicy.ts` — 파일 헤더
  주석: *"State is persisted in SQLite via domainState.js."*
  `registerFallback`(56행)이 `saveFallbackChain`을 호출하고,
  `resolveFallbackChain`(82행)이 내부 캐시(`ensureLoaded()`→
  `loadAllFallbackChains()`)를 통해 값을 읽는다.
- **2차(유일한) caller(OB-14)**: `src/domain/policyEngine.ts` 12~13행이
  `costRules`의 `checkBudget`과 `fallbackPolicy`의
  `resolveFallbackChain`을 함께 import하고, 47행 `evaluateRequest()`가
  77행에서 `resolveFallbackChain(model)`을 호출한다.
- **3차 caller 부재(OB-15, 결정적)**: `grep -rln "from.*domain/policyEngine\|require.*domain/policyEngine" src` 결과
  **`src/lib/container.ts` 단 1개 파일**만 나온다. `container.ts`
  18행이 `evaluateRequest`/`evaluateFirstAllowed`를 import하고
  110~111행에서
  ```
  container.register("policyEngine", () => {
    return { evaluateRequest, evaluateFirstAllowed, PolicyEngine };
  });
  ```
  로 DI 컨테이너에 **등록만** 한다. `src` 전체에서 이 컨테이너의
  `"policyEngine"` 바인딩을 실제로 resolve해서 쓰는 코드는
  **발견되지 않았다**(전수 검색, `container.ts` 자기 자신 제외).
- **결론(Interpretation)**: 저장 계층(SQL)과 1차 소비자
  (`fallbackPolicy.ts`)는 실재하지만, 그 값을 실제 요청 처리에
  반영할 유일한 경로(`policyEngine.evaluateRequest`)가 등록만 되고
  아무도 호출하지 않는 **dead code**다. `domain_fallback_chains`가
  0 rows인 것은 "설정한 적이 없어서"가 아니라 "설정해도 반영할
  실행 경로가 없어서"에 더 가깝다 — `registerFallback()` 자체도
  이 전수 검색에서 호출자가 발견되지 않았다(OB-16, `grep -rln
  "registerFallback" src` 결과 정의 파일 자신 뿐).
- **구현 착수 영향**: BLOCKING.

### 3.4 `routing_decisions`

- **판정**: **FAIL**
- **DB 상태(OB-17)**: 0 rows.
- **Schema**: `routing_decisions(id, request_id, task_type, combo_id,
  provider_selected, model_selected, score, factors_json,
  fallbacks_triggered, success, latency_ms, cost, source, created_at)` —
  4개 인덱스 포함, 매우 완성된 형태의 스키마.
- **Source(OB-18, 결정적)**: `src/lib/a2a/routingLogger.ts`.
  파일 헤더 주석(1~7행): *"A2A Routing Decision Logger / Records every
  routing decision to the `routing_decisions` SQLite table. / Used by
  `omniroute_explain_route` (T03) and future learning router."*
  그러나 38행 코드 주석은 다음과 같다:
  ```
  // In-memory log (production would use SQLite via routing_decisions table)
  const decisions: RoutingDecision[] = [];
  ```
  즉 **파일 헤더의 주장("SQLite table에 기록한다")과 실제 구현
  (in-memory 배열만 사용)이 이 파일 자체 안에서 서로 모순된다.**
  46행 `logRoutingDecision()`은 `decisions.push(decision)`만 수행하고
  (55행), `db.prepare(...INSERT...)` 호출은 파일 전체에 **없다**.
  최대 1000건, TTL 7일(39~41행)로 프로세스 재시작 시 소실되는 순수
  휘발성 로그다.
- **Caller 부재(OB-19)**: `grep -rln "logRoutingDecision" src` 결과
  **정의 파일(`routingLogger.ts`) 자기 자신 한 곳**뿐이다 — 이 함수를
  호출하는 코드가 `src` 전체에 없다.
- **Live execution 여부**: 확인 불가 — 애초에 이 write path가
  구현되지 않았으므로(SQL INSERT 부재) "실행됐는지"를 물을 대상
  자체가 없다. `routing/decisions/[requestId]/route.js`(컴파일된
  Next.js API route, `dist/.build/next/server/app/api/routing/decisions/[requestId]/route.js`,
  OB-20)는 **조회(GET)용 API 엔드포인트**로 보이며, 채워질 데이터가
  없으므로 실제 조회해도 빈 결과만 반환할 것이다(Interpretation,
  직접 호출해 확인하지는 않음 — 서버 미기동).
- **구현 착수 영향**: BLOCKING. 이 항목은 "설정-실동작 불일치"가
  아니라 **"기능 자체가 미구현 상태"**임이 소스 수준에서 확정됐다.

### 3.5 `domain_budgets`

- **판정**: **UNVERIFIED**
- **DB 상태(OB-21)**: 0 rows. `domain_budget_reset_logs`도 0 rows,
  `domain_cost_history`도 0 rows.
- **저장 계층**: `domainState.ts`의 `saveBudget`(199행)·
  `loadBudget`(237행)·`loadAllBudgets`(264행)이 실제 SQL을 실행한다
  (`ensureBudgetSchema()`로 컬럼 마이그레이션까지 수행 — 74~126행).
- **정책 계층(OB-22)**: `src/domain/costRules.ts`. `checkBudget(apiKeyId,
  additionalCost)`(437행)이 `getBudget()`→`loadBudget()`을 거쳐 예산을
  계산하고, 초과 시(485~501행)
  ```
  return {
    allowed: false,
    reason: `... budget exceeded: $... / $...`,
    ...
  };
  ```
  를 반환한다 — **이 함수 자체는 완성도 높게 구현돼 있다.**
- **Caller chain(OB-23, 5-hop 확인, 결정적)**: `src/sse/handlers/chat.ts`
  603행 `const policy = await enforceApiKeyPolicy(request, modelStr);`
  → `src/shared/utils/apiKeyPolicy.ts` 667행에서 시작하는
  `enforceApiKeyPolicy()` 본문 717행
  `const budgetRejection = validateBudget(context);` → 같은 파일
  582행 `function validateBudget(context)` 내부 586행
  `const budgetOk = checkBudget(apiKeyInfo.id);` → `costRules.ts`
  `checkBudget()` → `domainState.ts` `loadBudget()`(SQL SELECT).
  **이 경로는 실제 라이브 chat 요청 핸들러(`chat.ts`)에서 매 요청
  거치는 경로다** — `domain_fallback_chains`(§3.3)와 달리 dead code가
  아니다.
- **Live execution 여부**: 경로 자체는 78건의 실제 call_logs 각각에서
  통과했을 것이다(호출 시점이 같은 요청 처리 흐름 안에 있으므로,
  Interpretation). **그러나 `setBudget()`이 한 번도 호출되지 않아
  (0 rows) `getBudget()`이 항상 `null`을 반환했을 것이고, 그 경우
  `checkBudget`은 437~454행에서 즉시
  `{ allowed: true, ... }`를 반환한다** — 즉 이번 78건의 실제 트래픽
  중 어느 것도 예산 한도를 실제로 시험한 적이 없다. **enforcement
  로직의 존재와 배선은 검증됐으나, "한도를 넘었을 때 실제로 차단
  하는가"라는 핵심 동작은 검증되지 않았다.**
- **구현 착수 영향**: BLOCKING(실동작 미확인). §3.3·§3.4와 달리
  코드가 dead이거나 미구현인 것이 아니라, **설정이 존재한 적이
  없어 유일하게 남은 미지수가 "실제 차단이 작동하는가" 하나뿐**이라는
  점에서 성격이 다르다.

### 3.6 `IMPLEMENTATION_RULES.md` Scoped 완화 필요 여부

- **판정**: **UNVERIFIED**(판단 보류)
- **Observation(OB-24)**: §3.2~§3.5에서 확인한 4개 메커니즘
  (`priority` 기반 connection 선택, `domain_fallback_chains`,
  `routing_decisions`, `domain_budgets`)은 **전부 OmniRoute 자신의
  내부 코드**이며, 이 저장소(jarvis-os)의 `hqs/`·`core/` 어디에도
  대응하는 코드가 없다(§목적에서 인용한 이전 세션 grep 결과 재확인 —
  이 문서 작성 중 별도 재검색은 수행하지 않음, 이전 턴 결과 인용).
- **Interpretation**: `hqs/development/IMPLEMENTATION_RULES.md`의
  "Engine Gateway 구현 금지"·"Engine Routing 구현 금지"·"Multi Engine
  지원 코드 작성 금지"는 **Jarvis OS 자신의 코드가 그런 책임을
  떠맡는 것**을 금지하는 조항이다. 만약 Jarvis OS 쪽 caller가
  OmniRoute를 "단일 OpenAI-호환 엔드포인트 하나"로만 호출한다면 —
  즉 Jarvis OS 코드 안에 Provider 선택·fallback 체인·예산 판단
  로직을 두지 않고 그 판단 전부를 OmniRoute 내부에 위임한다면 —
  Jarvis OS 코드는 여전히 "Engine을 호출하는 함수 하나"(현재도
  허용된 형태)만 갖게 되어 금지 조항과 애초에 충돌하지 않을 가능성이
  있다.
- **판단을 보류하는 이유**: 이는 Jarvis OS 쪽 caller의 **설계**가
  먼저 정해져야 답할 수 있는 질문이며, 그 설계는 이 Evidence Review의
  범위가 아니다. 또한 §3.3·§3.4가 보여준 대로 OmniRoute 내부의
  `domain_fallback_chains`·`routing_decisions` 메커니즘 자체가
  아직 신뢰할 수 없는 상태이므로, "OmniRoute에 위임하면 된다"는
  전제 자체도 지금은 검증되지 않았다.
- **구현 착수 영향**: 별도 설계 결정(Jarvis caller가 무엇을
  호출·소유할 것인가)이 먼저 필요하다 — 이 문서는 그 결정을 내리지
  않는다.

---

## 4. 재검증 권고 (이 문서가 직접 수행하지 않음)

- `provider_connections`에 동일 Provider·서로 다른 priority 값을
  가진 connection 2개 이상을 실제로 등록하고, 실제 요청이 낮은
  priority 값을 우선 선택하는지 관찰한다.
- `registerFallback()`을 실제로 호출하는 임시 스크립트(옵션 B,
  `projects/` 격리 환경)로 `domain_fallback_chains`에 값을 쓴 뒤,
  현재 dead code 경로(`policyEngine.evaluateRequest`)가 아니라 실제
  chat 요청 흐름 어딘가에 연결하는 코드 변경이 있어야만 관찰이
  가능하다는 것을 재확인한다 — 즉 재검증 전에 **OmniRoute 자체의
  코드 변경(업스트림 이슈/PR)**이 선행돼야 할 수 있다.
- `logRoutingDecision()`을 실제 SQL INSERT로 연결하는 것도 마찬가지로
  **OmniRoute 업스트림의 수정 사항**이다 — jarvis-os 쪽에서 해결할
  수 있는 공백이 아니다.
- `setBudget()`으로 실제 한도를 설정한 뒤 그 한도를 넘는 실제 요청을
  보내 `allowed:false` 응답이 실제로 오는지 확인한다.

---

## Self Review

- 실제 검증 결과와 문서가 정확히 일치하는가 — **Pass**. §2 Evidence
  Matrix 판정은 이전 Evidence Review 턴의 결론을 그대로 유지했고,
  §3의 코드 인용은 이번에 직접 읽은 파일·라인을 그대로 옮겼다.
- Evidence를 과장했는가 — **아니오**. `priority`의 PASS 판정에도
  "차등 선택은 관찰되지 않았다"는 한계를 §3.2에 명시했고,
  `domain_budgets`는 "배선은 확인, 실동작은 미확인"으로 분리해
  UNVERIFIED를 유지했다. FAIL 두 건(`domain_fallback_chains`,
  `routing_decisions`)을 PASS로 바꾸지 않았다.
- source artifact의 한계를 명확히 표시했는가 — **Pass**(§1.1) —
  임시 scratchpad 경로임을 명시하고, 그 경로가 사라질 수 있다는 것,
  버전 동일성이 보증되지 않는다는 것, live execution을 새로 수행하지
  않았다는 것을 모두 기록했다.
- `ADC-0027`과 판정이 일치하는가 — **Pass**. `ADC-0027` §Q4 표의
  PASS 4/FAIL 3/UNVERIFIED 1 구도, §Decision "구현 착수 선행조건"
  1~4 구조를 그대로 유지했다. `ADC-0027`의 Decision(Conditional
  Accept) 자체를 재론하거나 변경하지 않았다.
- 기존 Architecture/Contract/Constitution/`IMPLEMENTATION_RULES.md`를
  변경했는가 — **아니오**. 이 문서 파일 외 어떤 파일도 생성·수정하지
  않았다.
- OmniRoute 구현을 수행했는가 — **아니오**. 서버를 기동하거나 새
  코드를 작성하지 않았다 — 기존 소스를 읽고 기존 DB를 조회했을
  뿐이다.
- ADR을 작성했는가 — **아니오**.
