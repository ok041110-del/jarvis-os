# EVIDENCE-0003: OmniRoute Zero-Config Egress 메커니즘 및 `domain_budgets` 재현 실패 정적 분석

자립 Evidence 문서 — Governance 문서가 아니다. 실제 소스 대조 결과를
있는 그대로 기록한다. 이 문서는 어떤 Architecture Decision도 내리지
않으며, Production Adoption 여부를 판단하지 않는다.

## 문서 성격 / 검증 목적

직전 Governance Review(2026-09-07, Read-only)가 남긴 두 개의
UNVERIFIED/설명 필요 항목 — (1) `model:"auto"`가 provider connection
0개에서도 실제 egress를 발생시키는 정확한 메커니즘과 그 차단에 필요한
최소 설정, (2) `domain_budgets` 실제 차단 재현 실패 원인 — 을 **순수
정적 소스 분석만으로** 추가로 좁힌다. 서버 실행·실제 provider 호출·
`model:"auto"` dispatch는 이 문서 작성 과정에서 전혀 재현하지
않았다.

---

## 1. `REQUIRE_API_KEY` — 실제 설정 경로와 적용 범위

**소스**: `src/shared/utils/featureFlags.ts::resolveFeatureFlag()`

```
우선순위: DB override(getFeatureFlagOverride) > process.env[key] > definition.defaultValue
```

`src/shared/constants/featureFlagDefinitions.ts`:

```
{ key: "REQUIRE_API_KEY", category: "security", defaultValue: "false", warningLevel: "caution" }
```

**적용 범위**: `src/server/authz/policies/clientApi.ts` — client(호출자)가
OmniRoute에 요청을 보낼 때의 인증 요구 여부만 결정한다. `false`(기본값)
이면 잘못되거나 없는 Bearer도 "anonymous"로 falling through한다
(`clientApi.ts:83-92`, 이전 리뷰에서 로그로 실측 확인: `invalid bearer
presented ... but REQUIRE_API_KEY=false — falling through to anonymous`).

**이 설정이 하지 않는 것**: OmniRoute가 어떤 upstream provider로
dispatch할지는 전혀 결정하지 않는다 — 완전히 별개 계층(§2).

**최소 Production 설정(식별만, 미적용)**: `REQUIRE_API_KEY=true`
(env var 또는 DB feature flag override). 이 값이 켜져 있어도 §2의
문제는 별도로 막아야 한다.

## 2. `blockedProviders` — 실제 설정 경로와 적용 범위

**소스**: `open-sse/services/autoCombo/virtualFactory.ts::getNoAuthCandidates()`

```js
if (blockedProviders.has(providerId) ||
    (typeof providerDef.alias === "string" && blockedProviders.has(providerDef.alias)))
  continue;
```

`blockedProviders`는 `settings.blockedProviders`(OmniRoute 자체
설정값, `getSettings()`로 로드 — 대시보드/설정 API를 통해 관리되는
기존 OmniRoute 자체 메커니즘)에서 온다. **Jarvis 코드나 새 설정
파일이 필요 없다.**

같은 로직이 `provider_connections` 기반 credentialed candidate에도
독립적으로 적용되며(`disabledNoAuthProviders` 별도 체크,
`virtualFactory.ts:503`), no-auth 후보 경로(§3)에도 동일하게
적용된다는 것을 소스로 확인했다.

## 3. `model:"auto"` zero-config egress의 정확한 메커니즘 (완전히 규명)

### 3.1 왜 provider_connections 0개에서도 후보가 생기는가

`src/shared/constants/providers/noauth.ts`가 정의하는
`NOAUTH_PROVIDERS`(13개 항목, §4 전체 목록)는 `provider_connections`
테이블과 무관하게 `getNoAuthCandidates()`(`virtualFactory.ts:243`)가
직접 순회해 후보를 만든다 — `validConnections =
connections.filter(hasUsableConnectionCredential)` 경로(DB
connection 기반)와는 **완전히 분리된 별도 경로**다.

### 3.2 왜 plain `"auto"`에서 정확히 `opencode`(alias `oc`)가 선택됐는가

**새로 발견한 핵심 사실**: 13개 `NOAUTH_PROVIDERS` 전부가 plain
`"auto"`에서 후보가 되는 것이 아니다. `virtualFactory.ts:230`:

```js
const AUTO_COMBO_NOAUTH_ALLOWLIST = new Set<string>(["opencode", "felo-web"]);
```

`isChatAutoComboNoAuthProvider()`(`virtualFactory.ts:232-241`)는
`bypassAllowlist`가 `false`일 때 이 allowlist에 없는 provider를
전부 제외한다. `buildPreparedPool(false)`(`virtualFactory.ts:656`,
`regularCandidates` — **plain `"auto"`가 실제로 쓰는 pool**)는
`bypassNoAuthAllowlist=false`로 호출된다. 따라서 **plain
`"auto"`에서 no-auth 후보로 나올 수 있는 것은 `opencode`/`felo-web`
단 2개뿐이다.**

반대로 `buildPreparedPool(true)`(`familyCandidates`,
`virtualFactory.ts:658`, 주석: "family selectors bypass the
reliability-curated no-auth allowlist")는 `auto/coding:pro`·
`auto/vision:pro` 같은 "family selector" 변형에 쓰이며, 이 경로는
allowlist를 우회해 §4의 LLM 서비스 no-auth provider 전부(12개,
video 전용 `veoaifree-web` 제외)에 노출된다.

### 3.3 왜 완전히 틀린 API Key로도 성공했는가

§1(`REQUIRE_API_KEY`)과 §3의 no-auth 경로는 서로 다른 축이다 —
client 인증 실패가 anonymous로 falling through해도, `model:"auto"`
요청은 §3.1·§3.2 경로를 그대로 타서 `opencode`에 도달한다. 인증
설정과 zero-config egress는 **독립적으로 각각 막아야 하는 두
문제**다.

---

## 4. NOAUTH_PROVIDERS 전체 목록과 `auto` 노출 범위

| id | alias | serviceKinds | plain `"auto"` 노출(allowlist) | family selector(`auto/*:pro`) 노출 |
|---|---|---|---|---|
| `devin-cli-agentic` | `dva` | llm | 아니오 | 예(local CLI 필요, 미설치 시 실패) |
| `opencode` | `oc` | llm | **예**(egress 실측 확인) | 예 |
| `duckduckgo-web` | `ddgw` | llm | 아니오 | 예 |
| `cloudflare-playground` | `cfp` | llm | 아니오 | 예 |
| `felo-web` | `felo` | llm | **예**(allowlist 포함, egress 미실측) | 예 |
| `theoldllm` | `tllm` | llm | 아니오 | 예 |
| `chipotle` | `pepper` | llm | 아니오 | 예 |
| `veoaifree-web` | `veo-free` | video | 아니오(llm 아님) | 아니오(llm 아님) |
| `auggie` | `aug` | llm | 아니오 | 예(local CLI 필요) |
| `zcode` | `zc` | llm | 아니오 | 예(local CLI 필요) |
| `codex-app-server` | `cxa` | llm | 아니오 | 예(local app-server 필요) |
| `uncloseai` | `unc` | llm | 아니오 | 예 |
| `aihorde` | `horde` | llm | 아니오 | 예 |

**최소 Production `blockedProviders` 권고(식별만, 미적용)**:

- **plain `"auto"`만 쓸 경우 최소 필요 집합**: `opencode`(`oc`),
  `felo-web`(`felo`) — 2개.
- **family selector(`auto/*:pro`) 사용 가능성까지 방어하려면**: 위
  표의 llm 계열 11개(`devin-cli-agentic`/`duckduckgo-web`/
  `cloudflare-playground`/`theoldllm`/`chipotle`/`auggie`/`zcode`/
  `codex-app-server`/`uncloseai`/`aihorde` + `opencode`/`felo-web`)
  전부를 `blockedProviders`에 등록하는 것을 권고한다(id 또는 alias
  중 하나만 등록해도 필터가 양쪽 다 검사하므로 충분 — §2).
- `veoaifree-web`는 `serviceKinds:["video"]`라 chat completions
  경로에는 애초에 노출되지 않는다 — 이 목록에서 제외해도 무방하다.

**이 표는 식별 결과일 뿐이다 — 이번 작업에서 실제로 어떤 설정도
변경하지 않았다.**

---

## 5. `domain_budgets` 재현 실패 원인 — 재정밀화(여전히 UNVERIFIED)

기존 `EVIDENCE-0002` §10 Provenance와 직전 시도의 정확한 차이를
대조했다.

| 항목 | `EVIDENCE-0002`(성공, 429 관찰) | 직전 실패 시도 |
|---|---|---|
| `domain_cost_history.timestamp` | 현재 시각 **ms(epoch 정수)** | `datetime('now')`(SQLite TEXT) |
| 요청 `model` 필드 | `<존재하지 않는 provider>/<존재하지 않는 model>` | `"auto"` |
| `domain_budgets` 스키마 | 동일 | 동일(대조 결과 컬럼 구성 일치) |
| 인증 경로(`api_key_id`) | `env-key` | `env-key`(로그로 실측 일치 확인) |

두 차이 각각을 소스로 재검증했다.

**(a) `model` 필드 차이는 원인이 아니다(소스로 배제)**: `src/sse/
handlers/chat.ts:603`의 `enforceApiKeyPolicy(request, modelStr)`
호출은 `modelStr` 값과 무관하게 무조건 실행되며, Auto-Combo/
`virtualFactory` 관련 코드(`chat.ts:895` 부근)보다 **항상 먼저**
실행된다(같은 파일 내 라인 순서로 확인). `apiKeyPolicy.ts:580-592`의
`validateBudget()`도 `checkBudget(apiKeyInfo.id)`만 호출할 뿐 `model`
파라미터를 전혀 받지 않는다 — model 값에 따른 우회 분기가 코드에
없다는 것을 직접 확인했다.

**(b) `timestamp` 타입 차이는 유력하지만 소스만으로 확정할 수
없다**: `domain_cost_history.timestamp`는 `INTEGER NOT NULL`
(`src/lib/db/core.ts:462`)이고 `loadCostTotal()`의 쿼리(`domainState.ts:409`,
`WHERE api_key_id = ? AND timestamp >= ?`)는 `periodStartAt`(JS
`Date.UTC(...)` 기반 ms 정수)과 비교한다. `datetime('now')`가 넣는
TEXT 값이 이 비교에서 실제로 어떻게 취급되는지(SQLite storage-class
비교 규칙상 TEXT는 항상 INTEGER보다 "크다"고 취급되어 오히려
포함됐을 수도 있다)는 문서 판독만으로 확정할 수 없다 — better-
sqlite3의 정확한 바인딩 동작까지 확인하려면 재실행이 필요하다.

**결론**: (a)는 소스 근거로 원인에서 **배제**했다. (b)는 가장 유력한
후보로 **좁혔으나 확정하지 않는다.** 사용자 지침(§4)에 따라 이번
작업에서는 재실행하지 않았으므로, `domain_budgets` pre-dispatch
차단이 `model:"auto"` 요청에도 동일하게 성립하는지는 **UNVERIFIED로
유지한다.**

---

## 6. Thin Caller v1 재검증 (로컬 test double만, 실제 서버 미사용)

```
python3 -m pytest projects/omniroute-thin-engine-caller-v1/tests/test_caller_unit.py \
  projects/omniroute-thin-engine-caller-v1/tests/test_caller_lifecycle.py \
  projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py -v
```

결과(2026-09-07 재실행): `26 passed in 10.82s` — 이전 EVIDENCE와
동일한 26개 항목 전부 재확인. 코드 변경 없음(`caller.py`는 이전
구현 세션 이후 무수정).

`test_real_engine_budget_block.py`(opt-in, 이중 게이트)는 **이번
작업에서 실행하지 않았다** — §7 참조.

## 7. 실제 서버 재실행을 하지 않기로 한 판단

§5가 유력한 가설(timestamp 타입)을 좁혔지만, 이전 세션에서 이미
동일한 종류의 시도가 2회 연속 의도치 않은 실제 egress(내장
`opencode` 무료 endpoint 호출)로 이어졌다. 가설이 틀렸을 경우 세
번째 실제 egress가 재발할 위험이 실질적으로 존재하므로, 이번
Validation에서는 **실제 서버를 다시 기동하지 않기로 판단했다.**
`test_real_engine_budget_block.py`에 걸어 둔 이중 opt-in 게이트
(`RUN_REAL_OMNIROUTE_TESTS=1` + `I_UNDERSTAND_REAL_EGRESS_RISK=1`)도
그대로 유지한다 — 이 판단 자체가 그 게이트의 설계 의도(사용자
지침 §6 "외부 egress 가능성이 있으면 즉시 중단")를 실제로
적용한 것이다.

**따라서 실제 Engine을 통한 성공 응답·`domain_budgets` 차단 재현은
이번에도 UNVERIFIED로 남는다** — §6의 test double 결과(PASS)와
혼동하지 않는다. test double은 Caller 코드의 request/response/
lifecycle 로직만 검증하며, OmniRoute 실제 서버의 동작을 대신
증명하지 않는다.

## 8. RT-0001 / ADC-0010 — 기존 판단 유지

직전 Governance Review(2026-09-07)가 원문 대조로 이미 확정한 판단을
그대로 유지한다 — 이 문서에서 재조사하지 않는다.

> RT-0001 Candidate 2의 Trigger는 "`call_engine()` 호출 지점이 둘
> 이상의 서로 다른 Engine을 대상으로 하게 됨"으로 명시적으로
> 좁혀져 있다. `omniroute-thin-engine-caller-v1`은 `call_engine()`을
> import/호출하지 않고 `hqs/development/` 어디에서도 참조되지
> 않는다 — Trigger를 충족하지 않는다. `ADC-0010` C1 재검토도
> 여러 미충족 선행조건(Kernel Module Defer 3건, ADC-01·02)이 이
> prototype과 무관하게 그대로 남아 있어 별도로 열리지 않는다.

이 판단을 뒤집을 새 근거는 이번 작업에서 발견되지 않았다 — 새
Architecture Decision을 제안하지 않는다.

---

## Final Judgment

| 항목 | 상태 |
|---|---|
| zero-config egress 메커니즘 규명 | **완전히 규명**(§3, 정적 분석만) |
| NOAUTH_PROVIDERS 전체 목록·`auto` 노출 범위 | **완전히 규명**(§4) |
| 최소 Production 설정 식별 | **식별 완료, 미적용**(§1·§2·§4) |
| `domain_budgets` 재현 실패 원인 | **UNVERIFIED**(유력 가설로 좁힘, §5) |
| Thin Caller v1 unit/lifecycle/boundary | **PASS**(26/26, 실제 재실행 확인, §6) |
| 실제 Engine 성공 응답 | **UNVERIFIED**(시도하지 않음, §7) |
| 실제 Engine 오류 전달(dispatch 이전 차단) | **UNVERIFIED**(시도하지 않음, §7) |
| RT-0001 / ADC-0010 Trigger | **미충족**(기존 판단 유지, §8) |
| Production Adoption | **선언하지 않음** |

## 이 Evidence가 답하지 않는 것

- `domain_budgets` 실패의 확정 원인(재실행 없이는 확정 불가).
- 실제 OmniRoute Engine을 통한 성공 응답·오류 전달 lifecycle(의도적
  으로 시도하지 않았다).
- `blockedProviders`/`REQUIRE_API_KEY`를 실제로 설정했을 때 §3의
  문제가 실제로 해소되는지(식별만 했을 뿐 적용·재검증하지 않았다).
- Production Adoption 가능 여부 — `ADR-0016` §9가 요구한 세 단계
  (Thin Caller 구현·Integration Validation·Final Adoption Review)
  중 어느 것도 이 Evidence로 완료되지 않는다.

## Provenance / Reproducibility

- 소스 대조 대상: `src/shared/utils/featureFlags.ts`,
  `src/shared/constants/featureFlagDefinitions.ts`,
  `src/server/authz/policies/clientApi.ts`,
  `open-sse/services/autoCombo/virtualFactory.ts`(198-320행, 600-660행),
  `src/shared/constants/providers/noauth.ts`(전체, 251행),
  `src/lib/db/core.ts`(432-465행),
  `src/lib/db/domainState.ts`(237-258행, 404-413행),
  `src/domain/costRules.ts`(175-177행, 219-260행, 429-510행),
  `src/sse/handlers/chat.ts`(560-610행),
  `src/shared/utils/apiKeyPolicy.ts`(560-593행) — 전부 이전 세션이
  캐시해 둔 OmniRoute 3.8.50 패키지(volatile scratchpad 경로,
  `EVIDENCE-0001` §한계와 동일 성격)에서 `grep`/`Read`로만 확인,
  실행 없음.
- Thin Caller 재검증: `python3 -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/test_caller_unit.py
  projects/omniroute-thin-engine-caller-v1/tests/test_caller_lifecycle.py
  projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py -v`
  (의존성 설치 불필요, stdlib만 사용, 2026-09-07 재실행).
- 실제 서버 실행: 없음(§7).

## Self Review

- 실제 서버를 실행했는가 — **아니오**(§7, 명시적으로 판단해 회피).
- `model:"auto"` dispatch를 재현했는가 — **아니오**.
- zero-config egress 원인을 코드 근거로 규명했는가 — **Pass**(§3,
  정확한 파일·라인·상수명 인용).
- `domain_budgets` 실패 원인을 근거 없이 확정했는가 — **아니오**
  (§5, UNVERIFIED 유지, model 차이는 배제 근거 제시).
- test double 결과와 실제 Engine 결과를 혼동했는가 — **아니오**(§6·
  §7에서 명시적으로 분리).
- RT-0001/ADC-0010을 재론했는가 — **아니오**(§8, 기존 판단 인용만).
- 기존 문서(`EVIDENCE-0001`/`0002`, `ADC-0027`~`0031`, `ADR-0015`/
  `0016`)를 수정했는가 — **아니오**(이 파일 하나만 신규 생성).
- Production Adoption PASS를 선언했는가 — **아니오**.
