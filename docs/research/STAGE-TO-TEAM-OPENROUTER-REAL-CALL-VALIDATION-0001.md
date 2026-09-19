# Stage → Team OpenRouter Real Call Validation

## Summary

- 목적: `STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md`가
  명시적으로 범위 밖에 남긴 부분("오늘 어떤 실제 OpenRouter API 호출도
  시도하지 않았다")을 메운다 — Team Migration 이후 `call_engine_via_
  openrouter()` 경로에 대한 **최초의 실측 real 외부 호출 검증**이다.
- 범위는 의도적으로 최소다: `call_engine_via_openrouter()` 단일 함수를
  고정 프롬프트로 1회 호출한 것뿐이며, **전체 `run_workflow()`나
  Team 01~05 통합 실행은 이 문서의 범위가 아니다.** GitHub 접근과
  파일 쓰기는 처음부터 배제했다.
- 실측 결과: 모델 목록 조회(GET)는 성공, Chat Completion(POST)은
  bounded retry 1회를 포함해 2회 모두 실패(`RuntimeError`,
  `category=malformed_response`, `candidates_tried=3`). **성공
  응답은 이번 표본에서 확보하지 못했다.**
- 실패 원인은 코드 레벨 동작(4xx 분류 로직, 후보 미축소, status
  code/response body 폐기)까지는 확정했으나, **실제 어떤 모델·어떤
  HTTP status였는지는 코드 자체가 그 정보를 보존하지 않아 확인
  불가능**하다(추가 API 호출 없이는 원천적으로 판별 불가).
- Architecture/Public Contract/Retry Policy/Team·Stage 책임 — 전부
  무변경. Stop Trigger 미발동.
- **이번 결과를 Team 경로의 real Engine E2E "PASS"로 해석하지
  않는다** — Chat Completion 성공 여부는 미확립(NOT ESTABLISHED)
  상태로 남는다.

---

## 1. 목적과 범위

### 1.1 목적

`hqs/development/HANDOVER.md` Next Step이 요구한 "Kernel Boundary
Validation에 필요한 최신 Evidence" 확보 작업의 일부로, Development HQ
Team 실행 경로(T1~T3에서 구조적으로 검증 완료)가 실제 외부 Engine
호출에서도 동작하는지 최소 표본으로 확인한다.

### 1.2 범위에 포함된 것

- `hqs/development/mvp/openrouter_engine.py::call_engine_via_openrouter()`
  단일 함수 1회 호출(고정 프롬프트 `"Reply with exactly the single
  word: PONG"`)
- 이 함수 내부에서 실제로 발생하는 외부 HTTP 요청의 실측(횟수·대상·
  성공/실패)

### 1.3 범위에서 명시적으로 제외한 것

- 전체 `run_workflow()`(Team 01→05 통합) 실행 — 별도 트랙(T5 이후)
- GitHub Repository 접근(`GitHubRepositoryAdapter`) — 이번 실행 경로에
  전혀 포함하지 않음
- 로컬 파일 쓰기 — `expose_target=True` 경로를 아예 사용하지 않아
  발생 여지 자체가 없음
- 저장소 코드/테스트 수정, 커밋, PR 생성

---

## 2. 실행 조건

| 조건 | 값 |
|---|---|
| 승인된 최대 외부 HTTP 요청 | 3회(모델 목록 GET 1회 + Chat Completion POST 최대 2회) |
| 실행 위치 | 세션 스크래치패드(`/tmp/.../scratchpad/t4s1_min_engine_call.py`) — 저장소 밖, 저장소 코드 무수정 |
| 실행 방식 | `importlib.util`로 `mvp/openrouter_engine.py`를 동적 로드 후 `call_engine_via_openrouter()` 직접 호출 |
| 계측 방법 | `urllib.request.OpenerDirector.open`을 wrapping해 실제 발생한 HTTP method/URL만 기록(요청/응답 내용 변형 없음) |
| 저장소 코드 변경 | 없음 — 실행 전후 `git status --short` 둘 다 출력 없음(clean) |

---

## 3. 실측 결과

```
HTTP 요청 횟수: 3
  - GET  https://openrouter.ai/api/v1/models
  - POST https://openrouter.ai/api/v1/chat/completions
  - POST https://openrouter.ai/api/v1/chat/completions
content_received: False
exception_type: RuntimeError
exception_message: OpenRouter call failed after retry (category=malformed_response, candidates_tried=3)
```

- **모델 목록 조회(GET `/api/v1/models`)**: 성공 — 실패했다면 이후
  단계(필터링·후보 선정) 진입 전에 `OpenRouterEngineConfigError`로
  즉시 중단됐을 것이나, 실제로는 후보 선정 이후 Chat 단계까지
  도달했으므로 Pool 조회는 정상 완료된 것으로 판단한다.
- **Chat Completion(POST `/api/v1/chat/completions`)**: 최초 1회 +
  bounded retry 1회, **2회 모두 실패**.
- **반환값**: 단일 `RuntimeError`(`call_engine_via_openrouter()`의
  외부 계약대로 — Stage/Team 계층에 새 예외 타입을 노출하지 않음).
- **`category=malformed_response`의 의미**: `_classify_failure()`
  기준으로 "순수 HTTP 4xx(429 제외)" — `docs/research/ADR-0027-
  VALIDATION-GATE-9-10-RESOLUTION-0001.md`가 이미 정정을 마친 정의와
  정확히 일치한다(§6 참조).
- **`candidates_tried=3`의 의미**: "실제로 3개 모델에 순차 시도했다"가
  아니라 **"끝까지 제외되지 않은 후보 개수"**다 — 4xx 응답은
  `_parse_chat_response()`가 `selected_model`을 추출하기 전에 즉시
  반환하므로, bounded retry가 실패 모델을 후보에서 제외하지 못하고
  1차·2차 시도 모두 **동일한 3개 후보**로 재요청했다(코드 레벨로
  확정, `test_http_4xx_retry_does_not_narrow_candidates`가 이미
  이 동작을 통합 테스트로 고정해 둠).
- **GitHub 요청**: 0건 — 계측된 3개 요청 전부 `openrouter.ai` 대상,
  GitHub 관련 요청 없음.
- **파일 변경**: 없음 — 실행 전후 `git status --short` clean.
- **API 키 노출**: 없음 — 계측 로그는 요청 method/URL만 기록했고,
  `Authorization` 헤더 값·응답 원문·프롬프트 내용 모두 출력하지 않았다.

---

## 4. 원인 조사 결과 (코드/테스트/기존 Evidence 기반, 추가 API 호출 없음)

| 확인 항목 | 확인 방법 | 결과 |
|---|---|---|
| 4xx 분류 로직 | 코드(`_classify_failure`) | `status>=400`이고 `429`/`5xx`가 아닐 때만 `malformed_response` — 429/5xx와 배타적 |
| 4xx 시 후보 목록 미축소 | 코드(`_parse_chat_response`, `call_engine_via_openrouter`) + 기존 테스트(`test_http_4xx_retry_does_not_narrow_candidates`) | 4xx 경로는 `selected_model`이 항상 `None`이라 후보가 좁혀지지 않고 동일 후보로 재시도 |
| bounded retry 동작 | 코드(`for attempt in range(2)`) | 최초 1회 + 최대 1회 추가, 카테고리 구분 없이 모든 실패에 동일 적용 |
| status code/response body 보존 여부 | 코드(`raise RuntimeError(f"... category=..., candidates_tried=...")`) | **보존되지 않음** — 최종 예외 메시지에 원본 HTTP status 숫자도, 응답 body도 포함되지 않는다. 이는 결함이 아니라 `RFC-0041`/`ADR-0027`이 요구한 범위("quota를 모델 품질 실패와 분리")를 그대로 반영한 의도된 설계 한계다 |
| 원인 확정 가능 여부 | 위 전부 종합 | **확정 불가** — 어떤 모델이 응답했는지, 실제 status 숫자가 무엇인지 코드가 애초에 기록하지 않으므로 이번 실행 로그만으로는 원천적으로 판별할 수 없다 |

가능한 원인 범주(불확실성 명시, 순위 없음):
1. 특정 free 모델의 정책적 거부(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`에 기록된 403 사례와 유사한 패턴 — 단 그 두 모델은 이미 블록리스트에 등재되어 있어 **다른 모델**일 가능성)
2. OpenRouter 계정/무료 모델 정책 응답(429가 아닌 4xx)
3. 무료 모델의 일시적 비가용
4. 요청 형식 자체의 문제(기존 다수의 real Engine E2E 성공 기록이 있어 가능성은 낮다고 추정)

**어느 쪽도 확정하지 않는다** — 확정하려면 실제 응답 body/모델명을 로깅해야 하는데, 이는 이번 문서의 범위(추가 API 호출 금지)를 벗어난다.

---

## 5. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- Public Contract(`stages/contracts.py` 5개 Contract) — **무변경**
- Retry Policy(`call_engine_via_openrouter()`의 bounded retry) — **무변경**(그대로 사용, 관찰만 함)
- Team/Stage 책임 경계 — **무변경**
- RFC/ADC/ADR — 신규 항목 없음
- **Stop Trigger 미발동**: Registry/Scheduler/Runtime 일반화, 신규 Kernel Component 필요성, Architecture/Public Contract 변경 필요성, Team/Stage 책임 확장 — 어느 것도 관찰되지 않았다

---

## 6. 기존 Evidence와의 관계

- `STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md`: Team → Stage → Agent → `openrouter_engine.py`까지 call path가 코드로 연결되어 있음을 확인했으나 "오늘 어떤 실제 OpenRouter API 호출도 시도하지 않았다"고 명시 — **이 문서가 그 공백을 메우는 최초의 실측 후속 문서**다.
- `ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md`: `malformed_response` 카테고리의 정확한 정의(순수 HTTP 4xx, 429 제외)를 이미 정정해 두었다 — 이번 실측 결과(`category=malformed_response`)는 **그 정정된 정의와 정확히 일치**하며, 과거의 이름-의미 혼동 문제와는 무관한 정상 분류다. 이번 문서는 그 정정 문서의 원문을 수정하지 않았다.
- `DEV-HQ-V2.0-INTEGRATED-WORKFLOW-E2E-0001.md`(옛 Stage 직접 호출 `workflow.py` 대상 real Engine E2E, Team Migration 이전 커밋): 이번 문서와 **대체 관계가 아니다** — 그 문서는 전체 01→05 통합 실행을, 이 문서는 단일 함수 최소 호출만 다루며, Team 경로에 대한 전체 통합 real E2E는 여전히 미수행 상태로 남아 있다.
- `OPENROUTER-STAGE-MODEL-SELECTION-0001.md`: 특정 free 모델의 403 정책 거부 실사례를 기록 — 이번 실패가 같은 패턴인지는 **미확인**(§4).

---

## 7. Evidence 한계

- **실제 성공 응답을 확보하지 못했다** — 이번 표본은 실패 1건뿐이며, Chat Completion가 실제로 정상 동작하는지는 이 문서만으로는 확인할 수 없다.
- 실제 응답한 모델 ID, 실제 HTTP status 숫자(400/403/404 등 중 무엇인지) — **미확인**(코드가 폐기, 로그에도 기록하지 않음).
- 계정 정책 문제인지 모델별 거부인지 요청 형식 문제인지 — **미확정**.
- **이번 결과를 Team 01~05 전체 E2E의 PASS로 해석하지 않는다.** 검증한 것은 오직 "단일 `call_engine_via_openrouter()` 호출이 예상된 방식(모델 목록 조회 → Chat 시도 → bounded retry → 단일 RuntimeError)으로 동작한다"는 것뿐이며, 이는 실패 경로의 안전성(예외 타입 고정, 후보 관리 동작)을 확인한 것이지 기능적 성공을 확인한 것이 아니다.

---

## 8. 판정

| 항목 | 판정 |
|---|---|
| T4-S1 안전 실행(조건 준수: 요청 ≤3회, GitHub 0건, 파일 변경 0건, 키 비노출) | **PASS** |
| T4-S2 제한적 원인 조사(추가 API 호출 없이 코드/테스트/Evidence 기반 조사) | **PASS**(단, 결론은 "원인 미확정"으로 확정) |
| Chat Completion 성공 여부 | **NOT ESTABLISHED** — 이번 표본은 100% 실패(2/2) |
| T4(Team 경로 real Engine E2E) 전체 성공 여부 | **NOT ESTABLISHED** — 최소 함수 호출 검증만 완료, 통합 실행·성공 응답 둘 다 미확보 |
| T5(성공·실패 경로 검증) 진행 가능 여부 | **조건부 가능** — "실패 시 단일 RuntimeError로 안전하게 종결되고 새 예외 타입을 노출하지 않는다"는 Architecture 요건(RFC-0041 §Failure Boundary)은 이번 실측으로 뒷받침되어 그 부분은 진행 가능하다. 다만 "성공 경로"의 실측 확인은 여전히 미확보 상태이므로, T5에서 성공 경로를 다루려면 별도의 성공 표본 확보가 선행되어야 한다 |

---

## 9. Governance Review

- 새로운 Architecture/Layer/Component/Concept이 추가되었는가 — **아니오**
- Baseline 문서를 변경했는가 — **아니오**
- `docs/decisions/adc/ADC.md`를 변경했는가 — **아니오**
- ADR이 필요한가 — **아니오**
- 코드를 작성·수정했는가 — **아니오**(스크래치패드 임시 스크립트만 사용, 저장소 밖)
- RFC → ADC → ADR 절차를 생략했는가 — **아니오**(이번 발견은 절차 생략이 필요한 성격이 아님)

## Self Review

- Registry/Scheduler/Runtime을 구현했는가 — **아니오**
- 신규 Agent/Capability를 추가했는가 — **아니오**
- 실패를 성공으로 과장했는가 — **아니오**, §8에서 Chat Completion 성공을 명시적으로 NOT ESTABLISHED로 판정
- 기존 Evidence 원문을 수정했는가 — **아니오**, 신규 문서만 작성
- Stop Trigger가 발동했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001.md`(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `main`. 이 문서만 작성했으며, 커밋·PR은 수행하지 않았다(사용자 지시).
