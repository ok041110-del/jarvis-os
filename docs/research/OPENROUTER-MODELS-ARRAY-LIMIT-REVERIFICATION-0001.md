# OpenRouter `models` 배열 상한(3개) 재검증

## Summary

- 목적: `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`가 기록한
  "`models` 배열은 4개 이상이면 HTTP 400"이 API 자체의 제한인지, 이
  세션이 만든 Harness 구현/SDK의 문제인지 독립적으로 재검증한다.
- 방법: 기존 `domain/auto_selection_client.py`를 **재사용하지 않고**,
  새 독립 스크립트(`models_array_limit_reverification_experiment.py`)를
  raw `urllib`(SDK 미사용)로 작성해 `models` 1~5개 요청을 각각 보냈다.
- 결과: `models` 4개·5개 요청 모두 동일한 API 오류 메시지
  (`"'models' array must have 3 items or fewer."`, HTTP 400)를
  반환했다 — 독립 구현·독립 요청에서도 재현됨.
- 판정: **API-level limit** (아래 §6 근거).
- `fallbacks`는 `models`와 다른 파라미터임을 실측으로 별도 확인했다
  (§4) — 공식 문서와 일치, 두 필드는 상호 배타적.
- 기존 Evidence 문서는 수정하지 않았다. Production 코드 변경 없음.

## 1. 현재 구현이 실제로 사용한 JSON request body

`domain/auto_selection_client.py::_single_call()`(기존 구현, 코드
읽기로 확인, 수정 없음):

```python
body = json.dumps(
    {
        "models": list(models_offered),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
).encode("utf-8")
```

- `"models"` 필드만 사용한다. request body를 구성하는 코드
  어디에도 `"fallbacks"` JSON 필드는 없다(grep 확인 — 파일 내
  유일한 `fallbacks` 문자열은 모듈 docstring의 문서 URL
  `model-fallbacks.md` 언급뿐이며, 실제 request body 키가 아니다).
- SDK(openai-python, openrouter 공식 SDK 등)를 쓰지 않는다 — 표준
  라이브러리 `urllib.request`로 직접 HTTP POST한다.
- Authorization 헤더를 직접 설정하지 않는다 — 이 세션 Egress Proxy의
  자동 인증 주입에만 의존한다.

**결론**: 기존 구현은 처음부터 raw HTTP였다 — "SDK냐 raw HTTP냐"를
분리하는 재실험 자체가 이미 raw HTTP 대 raw HTTP 비교가 됐지만, 요청
본문 구성 코드를 완전히 독립적으로 새로 작성해(§3) 첫 구현의 우연한
버그 가능성까지 배제했다.

## 2. `models` vs `fallbacks` 공식 문서 확인

공식 문서(`openrouter.ai/docs/guides/routing/model-fallbacks`) 인용
(WebFetch로 재확인, 이번 세션):

- `models` — 표준 Chat Completions 요청(`/api/v1/chat/completions`)
  파라미터. 예: `"models": ["~anthropic/claude-sonnet-latest", ...]`.
  **배열 크기 제한이 문서에 명시되어 있지 않다.**
- `fallbacks` — Anthropic Messages 호환 엔드포인트(`/api/v1/messages`)
  전용 파라미터. 예: `"fallbacks": [{ model: "anthropic/claude-opus-4.1" }]`.
  문서 원문: `"fallbacks accepts at most 3 entries; longer lists return a
  400 error."` — **3개 상한이 명시된 것은 `fallbacks`뿐이다.**
- 문서 원문: `"fallbacks cannot be combined with the models parameter;
  sending both returns a 400 error."` — 두 필드는 상호 배타적.

**중요한 불일치**: 공식 문서는 "3개 상한"을 `fallbacks`(다른 엔드
포인트)에만 명시하고, 이 Harness가 실제 쓰는 `models`(Chat
Completions)에는 크기 제한을 문서화하지 않았다. 즉 이전 세션이 관찰한
"`models` 배열도 3개 상한"은 **문서화되지 않은 실제 API 동작**이다
(문서 부재 ≠ 제한 부재임을 이번 재검증이 실측으로 확인했다).

## 3. 재검증 실험 설계

파일: `projects/openrouter-auto-selection-v1/models_array_limit_reverification_experiment.py`
(신규, 기존 `domain/auto_selection_client.py`를 import하지 않음 —
독립 재구현).

- `_raw_models_call(model_ids, use_fallbacks_field=False)` — 최소
  request body(`models` 또는 대조군 `fallbacks` 필드 + `messages` +
  `max_tokens=10`)로 1회 POST. 재시도·Contract 판정 없음(순수 관찰).
- 기록 필드: `request_field`, `request_model_count`, `http_status`,
  `error_body`만. **API Key/Authorization 값은 코드 어디에도 없고
  출력도 하지 않는다**(Authorization 헤더 자체를 설정하지 않음 —
  Egress Proxy 자동 주입).
- `models` 배열 크기 1, 2, 3, 4, 5 각각 1회.
- 대조군: 동일 엔드포인트(`/chat/completions`)에 `fallbacks` 필드로
  2개 모델을 보내 실제로 다른 필드인지 확인.
- Pool은 `domain/model_pool.py::fetch_free_model_pool(limit=10)`으로
  조회(재정렬·필터링 없음, 기존 모듈 읽기 전용 재사용 — 요청 크기
  실험과는 무관한 "모델 id 목록 획득" 용도로만 사용).

## 4. 실행 결과(원문 그대로, API Key 값 없음)

| n(models 배열 크기) | HTTP status | error message |
|---|---|---|
| 1 | 429 | `Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day` |
| 2 | 429 | 위와 동일(`previous_errors` 누적) |
| 3 | 429 | 위와 동일(`previous_errors` 누적) |
| 4 | **400** | **`'models' array must have 3 items or fewer.`** |
| 5 | **400** | **`'models' array must have 3 items or fewer.`** |
| (대조군) `fallbacks`, n=2 | 400 | `No models provided` |

- n=1~3이 429인 이유: 이 세션이 이전 여러 Task에서 OpenRouter 무료
  모델을 대량 호출해 **일일 무료 요청 한도(50/day)를 이미 소진**했기
  때문이다(`X-RateLimit-Remaining: 0`) — 이번 재검증과 무관한, 이전
  세션 누적 사용량에 의한 별도 제약이다. 배열 크기 실험 자체와는
  독립적인 원인임을 응답 메시지(`free-models-per-day`)로 명확히
  구분할 수 있다.
- n=4, n=5는 **일일 한도 소진 상태에서도** 429가 아니라 400을 받았다
  — 즉 OpenRouter가 배열 크기 검증을 요청 한도 검사보다 먼저(또는
  독립적으로) 수행해, 크기 위반 요청은 quota 소모 여부와 무관하게
  즉시 거부한다는 뜻이다. 이는 이 제한이 "우연히 매번 rate limit에
  걸린 것"이 아니라 **입력 자체에 대한 구조적 검증**이라는 근거가
  된다.
- 원문 오류 메시지(`'models' array must have 3 items or freewer.` —
  실제로는 `fewer`, 오타 아님, 원문 그대로 인용: `"'models' array must
  have 3 items or fewer."`)는 이전 세션이 기록한 메시지와 **완전히
  동일**하다 — 독립 재구현·재실행에서도 재현됨.
- `fallbacks` 필드를 Chat Completions 엔드포인트로 보내면 OpenRouter는
  그 필드를 아예 인식하지 않고 `"models"` 필드가 비어있는 것으로
  처리한다(`No models provided`) — `models`와 `fallbacks`가 이
  엔드포인트에서 서로 다른, 상호 대체 불가능한 파라미터임을 실측으로
  확인(공식 문서 §2와 일치).

## 5. SDK 제한인지 API 제한인지 분리

- 기존 구현(`auto_selection_client.py`)도, 이번 재검증 스크립트도
  **동일하게 SDK를 쓰지 않는다** — 둘 다 `urllib.request` raw HTTP다.
  따라서 "SDK가 별도로 배열을 자르는가"라는 가설은 애초에 성립하지
  않는다(SDK 자체가 요청 경로에 없음).
- 재검증 스크립트는 `domain/auto_selection_client.py`의 `_single_call`
  함수를 전혀 import하지 않고, request body 구성 로직을 처음부터
  새로 작성했다. 그런데도 n=4/n=5에서 완전히 동일한 오류 메시지가
  나왔다 — 이는 **이 Harness 코드 자체의 버그(예: 잘못된 직렬화, 잘못된
  필드명)일 가능성을 배제**한다. 코드가 다른데 결과가 같다는 것은
  원인이 코드가 아니라 서버(OpenRouter API) 쪽에 있다는 뜻이다.

## 6. 결론(사용자 지시 — 4가지 중 하나로 판정)

**판정: API-level limit**

근거:
1. 독립적으로 재구현한 raw HTTP 요청(기존 Harness 코드 미재사용)에서
   동일한 배열 크기(4개 이상)로 동일한 오류 메시지가 재현됐다(§4,§5).
2. 이 제한은 SDK가 아니라 서버 응답(HTTP 400 + 구조화된 JSON error
   body)으로 온다 — 클라이언트 측에서 사전에 자르거나 막지 않았다
   (재검증 스크립트는 4개·5개를 그대로 전송했다).
3. 이 제한은 요청 한도(quota) 소진 여부와 무관하게 발동한다(§4) —
   "우연히 매번 rate limit이었다"는 대안 설명을 배제한다.
4. 공식 문서는 이 제한을 `models`(Chat Completions)가 아니라
   `fallbacks`(Anthropic Messages)에만 명시하지만, 실제 서버 동작은
   `models`에도 동일한 "3개 초과 거부"를 적용한다 — **문서화되지
   않은 API 동작**이며, SDK/클라이언트 구현 문제가 아니다.

**Implementation bug 여부**: 아니다. 기존
`domain/auto_selection_client.py`와 `domain/model_pool.py`의
`MAX_MODELS_PER_REQUEST = 3` 제약은 이번 재검증으로 **정당성이
재확인**됐다 — 코드/주석 수정 불필요.

## 7. NOT DETERMINED

- n=1, n=2, n=3이 quota 소진 없이 실제로 성공(HTTP 200)하는지는 이번
  재검증에서 확인하지 못했다(일일 한도 소진 상태였기 때문) — 다음
  UTC 일일 리셋 이후 재확인이 필요하면 별도 세션에서 수행한다.
- `fallbacks` 필드의 3개 상한이 실제로 정확히 3인지는 이번 재검증에서
  직접 확인하지 않았다(대조군은 필드 인식 여부만 확인, 크기 스윕은
  하지 않음) — Anthropic Messages 엔드포인트 자체를 이번 재검증이
  호출하지 않았기 때문.
- 이 3개 상한이 OpenRouter 쪽 향후 변경(API 버전업 등)으로 바뀔 수
  있는지는 알 수 없다 — 이 문서는 2026-09-12 시점의 실측만 기록한다.

## 8. Governance / Production 영향

- RFC/ADC/ADR 변경 없음. `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`
  포함 기존 Evidence 문서는 수정하지 않았다(사용자 지시 §9) — 이
  문서가 별도 재검증 기록이다.
- Production 코드(`hqs/development/`) 변경 없음.
- 신규 파일: 이 문서와
  `projects/openrouter-auto-selection-v1/models_array_limit_reverification_experiment.py`
  뿐이다.
- API Key/Credential 값은 이 재검증의 어떤 산출물에도 포함되지 않았다.
