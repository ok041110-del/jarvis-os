# Stage → Team OpenRouter Real Call Validation (6) — Models/Chat 비대칭 실측 + 사용자 보고 성공 사례 분리 기록

## Summary

- 이 세션이 격리된 테스트 환경에서 `call_engine_via_openrouter()`를 1회
  실행한 결과, **같은 호출 내부에서 `GET /api/v1/models`는 성공(요청
  1회, 예외 없음)했고 `POST /api/v1/chat/completions`는 bounded
  retry 2회 attempt 전부 `http_status=401, category=malformed_
  response`로 실패**했다 — Evidence-0005와 수치·분류가 동일하다.
- 두 요청 모두 코드상 동일한 `_auth_headers()`를 사용함을 재확인했다
  (§3). Chat 요청 본문 구조(`models` 배열/`messages`)는 OpenRouter
  공식 문서와 구조적으로 일치하며, Request Contract 결함은 발견되지
  않았다(§4).
- **별도로, 사용자가 오늘 Dashboard(`projects/dashboard-shell-mvp`)
  환경에서 Chat Completion이 정상 작동하는 것을 직접 목격했다고
  보고했다.** 이 사실은 **이 세션이 독립적으로 검증한 것이 아니며**,
  사용자 보고로만 기록한다(§5) — 격리된 테스트 환경의 401 실측과
  혼동하지 않는다.
- **401의 근본 원인은 이번에도 확정하지 않는다.** 격리된 테스트
  환경에서 재현된 401과, 사용자가 보고한 Dashboard 환경의 성공이
  동일한 자격 증명/설정 상태였는지는 확인할 방법이 없다.
- 코드 변경 없음, Contract/Retry Policy/Architecture 무변경,
  API Key/Authorization/prompt/response body 미기록.

---

## 1. 목적 및 범위

**목적**: Evidence-0005 이후 이 세션에서 추가로 실측한 사실(models/
chat 비대칭)과, 이 세션 밖에서 사용자가 보고한 성공 사례를 하나의
문서에 담되, **검증 주체와 확실성 수준이 다른 두 사실을 절대 섞지
않고** 분리해서 기록한다.

**범위**:
- §2~§4: 이 세션이 코드 실행·정적 분석으로 **직접 확인**한 사실
- §5: 사용자가 **보고**했고 이 세션이 **검증하지 않은** 사실
- §6: 위 두 부류를 연결할 수 없는 이유

---

## 2. 격리된 테스트 환경 — 실측 결과

| 항목 | 값 |
|---|---|
| 실행 방식 | `mvp.openrouter_engine.call_engine_via_openrouter()` 프로덕션 코드 1회 논리 호출(재구현/우회 없음) |
| `OPENROUTER_API_KEY` | 존재함, 비어있지 않음, 길이 73자(값 미기록) |
| models 요청(GET) | 1회, 예외 없음 |
| chat 요청(POST) | 2회(최초 1회 + bounded retry 1회) |
| chat attempt 1 | `http_status=401`, `category=malformed_response`, `connection_error=False` |
| chat attempt 2 | `http_status=401`, `category=malformed_response`, `connection_error=False` |
| GitHub 요청 | 0회 |
| 파일 쓰기 | 0회 |
| 실행 전/후 `git status --short` | 둘 다 clean |

**관측 사실**: 같은 실행 안에서 models 요청은 통과했고 chat 요청만
401로 실패했다. 이 비대칭은 이번에 처음 같은 실행 단위 안에서
직접 재현되었다(이전에는 별도 세션에서 models 200만 단독 확인한
바 있음).

---

## 3. 인증 경로 재확인 (정적 분석)

- `_fetch_free_model_pool()`(models 요청)과 `_single_chat_call()`
  (chat 요청) **모두 동일한 `_auth_headers()` 함수를 호출**함을
  소스 코드로 재확인 — 두 요청 간 인증 설정 분기 없음.
- `_auth_headers()`는 `OPENROUTER_API_KEY`가 비어있을 때만
  `Authorization` 헤더를 생략하도록 설계되어 있음(기존 확인 사실,
  `OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`
  §3). 이번 실행에서는 키가 존재하므로 `_auth_headers()` 결과에
  `Authorization` 키가 포함됨을 실행 시점에 확인했다(값은 미기록).

---

## 4. Request Contract 대조 (OpenRouter 공식 문서 기준)

| 확인 항목 | 결과 |
|---|---|
| Chat URL/Method | `/api/v1/chat/completions`, `POST` — 공식 endpoint와 일치 |
| Models URL/Method | `/api/v1/models`, `GET` — 공식 endpoint와 일치 |
| `model`(단수) vs `models`(배열) | 코드는 `models` 배열만 사용 — 공식 문서상 "Either model OR models is required (not both)"로 **유효한 방식** |
| `messages` 필드 | 존재함(`role`/`content` 구조) — 공식 문서 필수 조건 충족 |
| Content-Type | `application/json` 포함, body는 `json.dumps()`로 인코딩 |
| 401 공식 정의 | "Missing Authentication header" 또는 invalid credentials |
| 402 공식 정의 | 크레딧 부족 — 이번 실패는 402가 아닌 401이므로 크레딧 부족으로 단정하지 않음 |

**결론**: Request Contract 결함은 발견되지 않았다. 코드가 문서와
다르게 요청을 구성하고 있다는 근거는 없다.

---

## 5. 사용자 보고 — Dashboard 환경 성공 (이 세션이 검증하지 않음)

| 항목 | 값 |
|---|---|
| 보고 내용 | Chat Completion이 정상 작동하는 것을 직접 목격 |
| 관찰 환경 | Dashboard(`projects/dashboard-shell-mvp`) |
| 관찰 시점 | 오늘(이 세션과 같은 날) |
| 검증 주체 | **사용자 본인** — 이 세션은 이 성공을 재현하거나 로그로 확인하지 않았음 |
| 이 세션의 관련 근거 | 없음(응답 본문/상태 코드/로그를 이 세션이 직접 관측하지 못함) |

이 항목은 **사실로 기록하되 "사용자 보고"라는 출처를 명시**한다.
이 세션이 독립적으로 재현·검증한 성공이 아니므로, §2의 401 실측과
같은 수준의 확실성으로 취급하지 않는다.

---

## 6. §2와 §5를 연결할 수 없는 이유

- 두 관찰은 **서로 다른 실행 환경**(격리된 테스트 스크립트 vs
  Dashboard 서비스)에서 나왔다.
- 두 환경이 동일한 `OPENROUTER_API_KEY` 값을 썼는지, 동일한 네트워크/
  프록시 경로를 거쳤는지 확인할 방법이 이 세션에는 없다.
- 따라서 "Dashboard에서는 되는데 격리된 테스트에서는 안 된다"는
  사실 자체는 기록하되, **왜** 그런지(환경별 키 차이/프록시 차이/
  기타)는 추측하지 않는다.

---

## 7. 명시적으로 미확인/미확정인 것

- 격리된 테스트 환경 401의 근본 원인 — 미확정(기존과 동일)
- Dashboard 환경 성공의 재현 가능성 — 이 세션에서 검증되지 않음
- 두 환경의 자격 증명/설정이 동일한지 여부 — 미확인
- models 200이 chat 인증 유효성을 보장하지 않는다는 사실의 **이유**
  (OpenRouter 서버 측 정책 등) — 공식 문서에 명시되지 않아 추측하지
  않음

---

## 8. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- `stages/contracts.py` 5개 Contract — **무변경**
- `openrouter_engine.py`의 bounded retry, `mvp/parallel_runner.
  RetryPolicy` — **무변경**
- 이번 문서 작성을 포함해 **코드를 전혀 수정하지 않음**
- Stop Trigger 미발동

---

## Governance Review

- 새로운 Architecture/Layer/Component/Concept 추가 — **아니오**
- Baseline 문서 변경 — **아니오**
- `docs/decisions/adc/ADC.md` 변경 — **아니오**
- ADR 필요 여부 — **아니오**
- 코드 작성·수정 — **아니오**
- RFC → ADC → ADR 절차 생략 — **아니오**

## Self Review

- 401의 원인을 추측했는가 — **아니오**(§6/§7에서 명시적으로 미확정 처리)
- 사용자 보고 성공을 이 세션이 검증한 것처럼 표현했는가 — **아니오**,
  §5에서 출처를 "사용자 보고"로 명시하고 이 세션의 독립 검증 여부를
  별도로 표기
- 성공을 과장했는가 — **아니오**, 격리된 테스트 환경 결과(§2)는
  실패(401)로 정확히 기록
- API Key/Authorization/prompt/response body를 출력·저장했는가 —
  **아니오**
- 기존 Evidence 원문을 수정했는가 — **아니오**, 신규 문서만 작성
- Stop Trigger가 발동했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0006.md`
(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `claude/api-key-exposure-security-ns754x`. 이 문서만 작성했으며,
커밋 여부는 아래 완료 보고에서 확인한다.
