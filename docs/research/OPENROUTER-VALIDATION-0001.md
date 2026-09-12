# OpenRouter Validation 0001 — 현재 세션 실환경 검증 및 Stage 01~05 전환 판단

## Summary

- **[Session 2 갱신, 2026-09-12T07:43Z] 새 세션에서는 OpenRouter가 실제로
  연결·인증·무료 모델 호출까지 전부 성공했다** — `openrouter.ai`가 이번
  세션의 Egress Proxy에서 차단되지 않았고(§1 원래 기록과 다름, §8 참조),
  Credential이 Proxy 단계에서 자동 주입되며(client가 보낸 Authorization
  헤더 유무·값과 무관하게 동일하게 인증됨, §8.2), 무료 모델
  (`nvidia/nemotron-3.5-lightning:free`) 실제 호출에서 `200 OK` + 실제
  생성 텍스트를 받았다(§8.4). **§1~§7(아래)은 이전 세션의 기록이며, 세션마다
  Egress 정책이 달라질 수 있다는 것 자체가 이번 검증의 핵심 발견이다 —
  기존 서술을 지우지 않고 §8로 이어 붙인다.**
- (이하는 §8 이전, 최초 검증 세션의 원래 Summary — 그대로 보존)
- **핵심 결과: 이 세션(원격 Claude Code 실행 환경)에서 OpenRouter는 네트워크
  정책 단계에서 즉시 차단된다** — `openrouter.ai:443`에 대한 Egress Proxy
  CONNECT 요청이 `403(policy denial)`로 거부됨(재현 완료, §1). DNS/TLS/인증
  중 어느 단계까지도 도달하지 못했다 — 인증(API Key) 문제가 아니라 그 이전
  단계의 차단이다.
- 이 차단 때문에 검증 항목 2~4(무료 모델 호출, OpenRouter 경유 Claude 호출,
  Anthropic BYOK 적용 확인)는 **이 세션에서 실행 자체가 불가능**했다 —
  실패가 아니라 미실행이며, 이 문서는 그 차이를 숨기지 않는다.
- 비교 대상으로 `api.openai.com`(현재 ADR-0024 ChatGPT Engine이 실제 사용
  중인 host)은 같은 세션에서 `200 OK`로 정상 응답했다(§1) — 즉 이 환경의
  Egress 정책은 "모든 외부 API 차단"이 아니라 **host 단위 allowlist**이며,
  OpenRouter가 그 목록에 없다는 것이 원인이다.
- **사용자가 말한 "현재 작업환경(iPhone + Claude Code 앱 세션)"과 이 검증을
  수행한 세션은 서로 다른 실행 환경일 수 있다** — 이 문서는 이 세션의
  네트워크 정책만 실측했고, iPhone 앱 세션의 정책이 동일한지는 별도 확인이
  필요하다(§6 한계).
- Architecture 판단: ADR-0024는 이미 "Central Router는 만들지 않는다"를
  Option D로 명시적으로 배제하고 Option C(정적 import, 파일 단위 Engine
  고정)를 채택했다(§5). OpenRouter를 새 Central Router/Gateway로 도입하는
  것은 이 배제와 직접 충돌한다 — RFC 없이 진행할 수 없다.
- **Production 코드는 변경하지 않았다.** 이 문서는 Evidence 문서이며, 실제
  전환 여부는 RFC → ADC → ADR 절차를 거쳐야 한다(§7).

---

## 1. 검증 1: OpenRouter API 연결(DNS/TLS/인증) 확인 — FAIL(정책 차단)

Egress Proxy 상태(`$HTTPS_PROXY/__agentproxy/status`)의 `recentRelayFailures`가
이 세션에서 실제로 기록한 원문:

```json
{
  "ts": "2026-09-12T07:24:46.649Z",
  "kind": "connect_rejected",
  "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
  "host": "openrouter.ai:443"
}
```

직접 호출 결과:

```
$ curl -sS -m 15 https://openrouter.ai/api/v1/models
curl: (56) CONNECT tunnel failed, response 403
HTTP_STATUS:000
```

비교(같은 세션, 같은 방식):

```
$ curl -sS -m 15 -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models
200   (1.12s)
```

**해석**: `CONNECT tunnel failed, response 403`은 TCP/TLS handshake 이전에
Proxy Gateway가 요청을 거부했다는 뜻이다 — API Key 인증 단계(HTTP 401/403
with body)와는 다른 실패다. 이 세션은 OpenRouter에 도달할 수조차 없다.
API Key 유무와 무관하게 실패가 고정된다.

## 2~4. 검증 2~4: 무료 모델 호출 / OpenRouter 경유 Claude 호출 / Anthropic BYOK — 미실행(NOT EXECUTED)

§1의 차단으로 인해 이 세 항목은 **실행되지 않았다** — "실패"로 기록하지
않는다(실행 자체가 불가능했으므로 결과 자체가 없다). 추가로, 이 세션의
환경 변수에는 `OPENROUTER_API_KEY`가 존재하지 않았다(확인만 하고 값은
출력하지 않음, §5 규칙 준수) — 네트워크 차단이 없었더라도 인증 단계에서
추가 정보(API Key)가 필요했을 것이다. Anthropic BYOK 검증(항목 4)은
사용자 본인의 Anthropic API Key를 OpenRouter 계정에 연결하는 절차이므로,
이 세션 밖에서 사용자가 직접 수행해야 하는 단계도 포함되어 있다 — 세션
Evidence만으로는 애초에 완결할 수 없는 검증이다.

## 5. 검증 5: API Key/Credential 값 미출력 — 준수

이 문서와 세션 내 모든 명령은 `env | grep`류 조회 시 `sed`로 값을 마스킹
했고, 어떤 API Key/Credential 원문도 출력·기록하지 않았다.

## 6. 검증 6: 현재 세션에서 재현 가능한가 — 재현 가능(차단이 재현됨)

"재현 가능"의 의미를 명확히 한다: **OpenRouter 호출 성공이 재현 가능한 것이
아니라, OpenRouter 차단이 재현 가능하다.** 같은 명령을 다시 실행해도 같은
`403 policy denial`이 나올 것으로 판단한다(Proxy allowlist는 세션 설정이
아니라 환경 정책이므로 이 세션 내에서 변하지 않는다).

**한계(정직하게 명시)**: 이 판단은 **이 세션**(원격 실행 환경)에 대해서만
유효하다. 사용자가 언급한 "iPhone + Claude Code 앱 세션"이 동일한 Egress
Proxy 정책을 쓰는지는 이 세션에서 직접 확인할 수 없다 — 클라이언트/환경마다
Proxy 정책이 다를 수 있다(`api.openai.com`이 `허용 + API 주입` 대상으로
명시적으로 구성된 것과 달리, `openrouter.ai`는 이번 세션 구성에 없다). 이
문서는 이 세션 밖의 환경에 대한 결과를 추정하지 않는다.

---

## 7. Architecture/Governance 판단

### 7.1 OpenRouter 실환경 사용 가능 여부

**이 세션에서는 사용 불가(정책 차단).** 다른 환경(iPhone 앱 세션 등)에서의
가능 여부는 Not Determined — 별도 실측 필요(§6).

### 7.2 무료 모델 적합성

검증 미실행으로 **Not Determined.** latency/응답 품질 어느 것도 이 세션에서
실측하지 못했다.

### 7.3 Stage 04 Claude/BYOK 적합성

검증 미실행으로 **Not Determined.** 추가로 BYOK 검증은 사용자의 계정 설정
행위를 전제하므로, 세션 Evidence만으로 완결되는 항목이 애초에 아니다.

### 7.4 비용/품질/Latency

측정 불가(호출 자체가 없었음) — **Not Determined.**

### 7.5 OpenRouter를 Central Router로 볼 것인가, External Provider Gateway로 볼 것인가

이 판단은 Governance상 이미 절반 결정되어 있다. ADR-0024 §Decision은
Option D("Central Engine Router")를 다음 근거로 명시적으로 배제했다:

> Central Engine Router: complexity 높음, readability 낮음(추상화 계층),
> testability 낮음(Router 자체 테스트 필요), **15행(Gateway) 위반 확정**

OpenRouter는 그 자체가 "여러 Provider/Model 중 무엇을 호출할지 OpenRouter가
대신 판단"하는 서비스다 — Jarvis 코드 입장에서 이를 도입하면 기능적으로
Central Router를 도입하는 것과 동일한 효과를 갖는다(Jarvis가 Provider를
직접 고르지 않고 OpenRouter가 고른다는 점에서 `omniroute_engine.py`의
"Thin Engine Caller"와 유사한 외형이지만, 목표 후보 Architecture 자체가
"Stage 01~03,05는 Free Model, Stage 04는 Claude"처럼 **Jarvis 쪽에서 목적별
모델 선택 기준을 이미 갖고 있다** — 이는 `omniroute_engine.py`가 Provider
선택을 전적으로 위임하는 것과 다르다).

**판단**: 목표 Architecture 후보(Stage별 모델 차등 지정)를 그대로 구현하면
"External Provider Gateway"가 아니라 **Jarvis 코드 또는 OpenRouter 설정
어느 쪽에 Engine Routing 책임이 있는지"가 불분명한 회색지대**가 된다 —
`IMPLEMENTATION_RULES.md` 16행(Engine Routing 구현 금지)과 정면으로 맞닿는
질문이며, 이 문서(Evidence)가 답을 대신 내리지 않는다. RFC 단계에서
명시적으로 다뤄야 할 질문이다.

### 7.6 기존 ADR-0024와의 충돌

**충돌 있음, RFC 필요.** ADR-0024는 다음을 이미 확정했다:

- 2-Engine(ChatGPT/Claude Code) 구조를 Production Adoption했고, Stage
  01~03/05는 ChatGPT, Stage 04 code generation/QA는 Claude Code Engine으로
  이미 Stage Mapping이 확정되어 있다(§Stage Mapping, 위 ADR 본문 인용).
- Option C(정적 import, 파일 단위 Engine 고정)를 선택하고 Option D(Central
  Router)를 명시적으로 배제했다 — `test_engine_boundary.py::
  test_no_central_router_or_gateway_module_created`로 회귀까지 고정했다.
- "세 번째 Engine이 필요해지면 다시 RFC → ADC → ADR 절차를 밟아야 한다"고
  스스로 명시했다(§Consequences).

사용자가 제시한 목표 후보(OpenRouter를 세 번째 Engine 또는 기존 두 Engine의
대체 경로로 도입)는 이 세 가지 확정 사항 모두와 겹친다 — 즉 ADR-0024가
스스로 예고한 "다음 RFC가 필요한 시점"에 정확히 해당한다.

### 7.7 필요한 RFC/ADC/ADR 변경

- **RFC 필요**: "OpenRouter를 세 번째 Engine으로 추가할 것인가, 또는 기존
  ChatGPT/Claude Code Engine 중 하나(들)를 OpenRouter 경유로 대체할 것인가"
  를 조사 대상으로 하는 RFC. 최소한 다음을 다뤄야 한다:
  - OpenRouter 도입이 §7.5의 Central Router 회색지대를 실제로 어떻게
    피하는지(또는 피하지 못해 Option D로 재분류되는지)
  - 이 세션이 실측하지 못한 §7.2~7.4(무료 모델 품질/비용/latency, BYOK
    적용)의 실제 Evidence — 이 RFC 이전에 별도 세션(사용자 자신의 iPhone
    앱 세션 등 OpenRouter가 실제로 reachable한 환경)에서 재검증 필요
  - `test_engine_boundary.py`가 고정한 회귀 조건(Central Router/Gateway
    미생성)을 깨지 않는 구현 형태가 존재하는지
- RFC가 Accept되지 않는 한 ADC/ADR 단계로 진행하지 않는다(Frozen
  Architecture, Governance Impact 없음— 이 문서는 그 상태를 바꾸지 않는다).

### 7.8 Stage 01~05 Production 전환 가능 여부

**지금 단계에서는 불가.** 근거:

1. §7.1: 이 세션에서 OpenRouter 자체가 도달 불가 — 최소한의 실환경 Evidence가
   없다.
2. §7.6: ADR-0024가 이미 확정한 Stage Mapping/Option C 선택과 충돌하며,
   RFC 없이 바꿀 수 없다(Frozen Architecture, `CLAUDE.md` Core Rules).
3. §7.2~7.4: 비용/품질/latency 등 전환 여부를 판단할 최소 근거 자체가
   Not Determined다.

---

## Evidence 원문

- Proxy 상태/차단 로그: `$HTTPS_PROXY/__agentproxy/status` 응답 원문(§1,
  세션 실행 당시 상태, 재실행 시 `recentRelayFailures` 항목은 시간에 따라
  갱신될 수 있음 — 이 문서는 갱신 이전 스냅샷을 인용한 것으로 표기한다)
- `curl` 직접 호출 결과(§1)
- `env | grep -iE "openrouter|anthropic|openai"`(값 미출력, 존재 여부만
  확인, §2)

## 검증 환경

- 세션: 원격 Claude Code 실행 환경(이 세션), 2026-09-12
- 이 문서는 사용자가 언급한 "iPhone + Claude Code 앱 세션"과 동일 환경임을
  전제하지 않는다(§6 한계 참조)

---

## 8. Session 2 — 재검증(2026-09-12T07:43Z, 새 세션) — 실제 연결/Credential/무료 모델 호출

**전제 정정**: 이 재검증은 사용자가 요청한 "방금 등록한 OpenRouter
Credential"을 이 세션이 직접 등록하지 않았다 — 이 세션은 그 Credential이
이미 Egress Proxy에 구성되어 있는 상태에서 시작됐다. 아래는 그 상태를
있는 그대로 실측한 결과다. §1~§7과 다른 세션이므로, Egress 정책이 세션마다
달라질 수 있다는 §6의 우려가 실제로 확인된 것이기도 하다(이번엔 반대
방향 — 이전엔 차단, 이번엔 허용).

### 8.1 OpenRouter 연결 — PASS

```
$ curl -sS -m 20 https://openrouter.ai/api/v1/models
HTTP_STATUS:200 TIME:0.706855s
```

`$HTTPS_PROXY/__agentproxy/status`의 `recentRelayFailures`도 이번 세션에서는
빈 배열(`[]`) — OpenRouter에 대한 차단 기록이 없다.

### 8.2 Credential 주입 — PASS

- 이 세션의 환경변수에는 `OPENROUTER_API_KEY` 등 OpenRouter 관련 변수가
  **존재하지 않았다**(`env | grep -iE "openrouter"` → 매치 0건, 값 확인이
  아니라 존재 여부만 확인). 즉 이 세션의 코드/쉘 레벨에서 직접 Key를 넣지
  않았다.
- 그런데도 `Authorization` 헤더를 아예 보내지 않은 요청과, **의도적으로
  잘못된** `Authorization: Bearer sk-or-v1-invalid-test-...`를 보낸 요청
  **둘 다 동일하게 `200 OK` + 정상 인증된 응답**을 받았다 — 즉 client가
  보낸 Authorization 값이 실제로 사용되지 않고, Proxy가 실제 유효한
  Credential로 항상 교체/주입하고 있다는 뜻이다(이전 세션 시스템 안내의
  "`api.openai.com` — 허용 + OpenAI API 주입" 패턴과 동일한 메커니즘이
  OpenRouter에도 적용된 것으로 판단).
- `GET https://openrouter.ai/api/v1/key`(OpenRouter의 "현재 인증된 Key
  정보 확인" 공식 endpoint) 응답으로 인증 상태를 직접 확인했다 —
  **Key 원문/label 문자열은 이 문서에 옮기지 않는다**(규칙 6 준수, OpenRouter
  자체가 일부 마스킹해 반환한 값이라도 출력하지 않음). 확인한 사실만 기록:
  - `is_management_key: false`, `is_provisioning_key: false` — 일반 API Key
  - `is_free_tier: true` — 무료 티어 Key로 인증됨
  - `creator_user_id` 필드에 실제 계정 식별자가 채워져 있음(값 자체는
    비밀정보가 아니므로 "존재함"만 기록, 이 문서에 원문 옮기지 않음)
  - `usage: 0`, `byok_usage: 0` — 이 Key는 지금까지 BYOK 경로를 사용한
    이력이 없음(§8.5 참조)
  - HTTP 200, 인증 실패(401) 없음

### 8.3 OpenRouter API 인증 성공 여부 — PASS

§8.1(연결)과 §8.2(Credential 자동 주입 + `/api/v1/key` 200 응답)로 인증
성공을 확인했다. 이 세션은 OpenRouter 계정에 유효하게 인증된 상태다.

### 8.4 무료 모델 실제 호출 — PASS

전체 무료 모델 목록(`/api/v1/models`에서 id가 `:free`로 끝나는 것) 19개
확인, 그중 2개를 실제 호출:

| 시도 | 모델 | HTTP | 응답 시간 | 결과 |
|---|---|---|---|---|
| 1차 | `liquid/lfm-2.5-2.6b:free` | 200 | 1.007s | `finish_reason: length`, `content: null`(reasoning만 소비, `max_tokens=20`이 너무 작아 최종 답 생성 전에 잘림 — 호출 자체는 성공, 파라미터 문제) |
| 2차(동일 모델, `max_tokens=100`) | `liquid/lfm-2.5-2.6b:free` | 200 | 1.482s | 여전히 reasoning만 소비, 모델 특성상 reasoning이 김 |
| 3차(모델 교체) | `nvidia/nemotron-3.5-lightning:free` | 200 | 1.839s | **`content`에 실제 생성 텍스트 존재**("Here's a thinking process: ... Must" 등, `max_tokens=60`으로 컷) — 정상 LLM 응답 확인 |
| 4차(잘못된 Auth 헤더로 동일 모델 재확인) | `nvidia/nemotron-3.5-lightning:free` | 200 | 2.135s | 동일하게 정상 응답(§8.2 Credential 주입 증거) |

- 4회 호출 전부 `"cost": 0`, `"is_byok": false` — 과금 없는 순수 무료 티어
  호출로 확인됨.
- 1~2차의 `content: null`은 OpenRouter/모델 실패가 아니라 **요청 파라미터
  (`max_tokens`가 모델의 reasoning 소비량보다 작음)** 문제였음을 3차가
  증명한다 — 실패 원인을 "연결/인증 실패"와 섞지 않는다(규칙 8).

### 8.5 Latency 기록

| 항목 | 값 |
|---|---|
| `/api/v1/models` (목록 조회) | 0.707s |
| `/api/v1/chat/completions` (무료 모델, 성공 4회 평균) | 약 1.62s (1.007 / 1.482 / 1.839 / 2.135s) |
| `/api/v1/key` (인증 상태 조회) | 0.170s |

### 8.6 실패 원인 구분 — 해당 없음(연결/인증 실패 없음)

이번 세션에서는 연결·인증 실패가 없었다. 유일한 비정상 응답은 §8.4 1차
시도 전 `meta-llama/llama-3.2-3b-instruct:free`라는 **존재하지 않는 무료
slug**를 호출했을 때의 `404`였다 — OpenRouter가 반환한 메시지("This model
is unavailable for free... use this slug instead: ...")로 **연결/인증
문제가 아니라 모델 slug 선택 실수**임이 명확했다. 이후 실제 존재하는
`:free` slug로 재시도해 해결했다(§8.4).

### 8.7 이전 세션(§1~§7)과의 관계 — 세션별 Egress 정책 차이 확정

이 §8 자체가 §6의 한계 서술("Proxy allowlist는 세션 설정이 아니라 환경
정책"이라는 가정)이 **틀렸음을 실측으로 정정한다** — 최소한 두 세션 사이에
동일한 host(`openrouter.ai`)에 대한 정책이 `차단(403)` → `허용+인증
Credential 주입`으로 바뀌었다. 원인(세션 종류 차이, 사용자가 언급한
"방금 등록한 Credential"이 이 세션의 정책 자체를 바꿨을 가능성, 또는 단순
세션 간 정책 비일관성)은 이 문서가 규명하지 않는다 — Evidence만 기록한다.

### 8.8 Production/Architecture/Governance 영향

- Production 코드, Architecture/Contract/Governance 문서는 이 재검증에서도
  **전혀 변경하지 않았다.**
- §7(Architecture 판단)의 결론(ADR-0024 Option D 배제와의 충돌, RFC 필요,
  Stage 01~05 Production 전환 지금 단계 불가)은 이 §8로 **번복되지
  않는다** — §8은 "OpenRouter가 최소한 어떤 환경에서는 실제로 동작한다"는
  실행 가능성(feasibility) Evidence를 추가했을 뿐, Central Router 충돌
  문제(§7.5)·Engine Routing 금지(`IMPLEMENTATION_RULES.md` 16행) 문제는
  그대로 남아 있다. 오히려 "실제로 동작한다"가 확인됐으므로, RFC 착수의
  실행 가능성 전제 하나(§7.7이 요구한 "OpenRouter가 reachable한 환경에서의
  재검증")는 이번 §8로 충족됐다고 기록한다.

### 8.9 다음 단계

1. §8이 확인하지 못한 것: **OpenRouter 경유 Claude 모델 호출**과 **사용자
   본인 Anthropic API Key의 BYOK 연결**(원 요청 항목 3·4)은 이번 재검증
   범위에도 포함되지 않았다(이번 요청은 "무료 모델 1개 이상 호출"까지만
   범위로 명시함) — 별도 후속 검증 필요.
2. §8.7의 세션 간 정책 차이 원인 확인 — 특히 사용자의 실제 "iPhone +
   Claude Code 앱 세션"이 이번 §8과 같은(허용) 정책인지, §1~§7과 같은(차단)
   정책인지 그 세션에서 직접 재확인 필요(이 문서는 대신 답할 수 없음).
3. 위 1·2가 채워진 뒤에도, Stage 01~05 Production 전환 자체는 §7.6~7.7이
   요구한 RFC 없이는 여전히 진행할 수 없다(무변경).
