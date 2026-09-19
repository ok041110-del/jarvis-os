# Stage → Team OpenRouter Real Call Validation (5) — Observability 적용 후 T5-C 재실행, 최초 HTTP Status 관측

## Summary

- PR #204(Failure Observability, `RuntimeError.attempts`)가 `main`에
  병합된 뒤, `-0003`/`-0004`와 동일한 안전 가드로 T5-C(Team→Stage
  03→04→05, real 로컬 candidate_index)를 재실행했다.
- **이번이 누적 9회 Engine 호출 중 최초로 실제 HTTP status를 관측한
  실행이다 — 두 번의 실패(Stage 03 `design_agent_design`, Stage 04
  `identify_target`) 전부, 매 attempt마다 `http_status: 401`이
  관측됐다.**
- 후보 모델 3개(`inclusionai/ling-3.0-flash-vl:free`,
  `nex-agi/nex-n2.5-mini:free`, `nex-agi/nex-n2.5-pro:free`)는 두
  attempt 모두 동일했고(`selected_model`이 매번 `None`이라 후보가
  좁혀지지 않음 — 기존 코드 동작과 일치), `category`는 이전과 동일한
  `malformed_response`로 분류됐다(401은 429/5xx가 아닌 4xx이므로
  분류 정의와 정확히 일치).
- GitHub 요청 0건, 파일 변경 0건(`git status --short` clean),
  `DesignResult`/`ImplementationResult`/`VerificationResult` Contract
  3종 전부 위반 없음 — 구조적 결과는 `-0002`/`-0003`과 동일.
- **원인은 이번에도 추측하지 않는다.** 401이라는 숫자 자체는 관측된
  사실이며, 이 숫자가 왜 발생했는지(자격 증명 문제/프록시 문제/기타)는
  이 문서의 범위 밖이다.
- 코드 변경 없음 — Observability 기능이 설계대로 정확히 동작함을
  실측으로 확인한 것이 이번 실행의 핵심 성과다.

---

## 1. 목적 및 범위

**목적**: PR #204로 병합된 `attempts` 진단 속성이 실제 Team→Stage
경로의 real Engine 실패에서 의도대로 동작하는지 확인하고, 이번에
새로 관측 가능해진 정보(HTTP status 등)를 기록한다.

**범위**: `-0003`(T5-A)/`-0004`(T5-C 최초 실행)와 동일한 실행 경로 —
`architecture_team.run_architecture_team()` → `implementation_team.
run_implementation_team(expose_target=False)` → `validation_team.
run_validation_team()`, real 로컬 `candidate_index`(`ast_context.
build_function_candidate_index()`), GitHub 접근 없음, 파일 쓰기 없음.

**이번 실행에서 추가된 것**: `mvp.openrouter_engine.call_engine_via_
openrouter`를 Stage/Agent 코드가 import하기 전에 얇게 wrapping해,
Stage 03/04가 내부적으로 흡수하는 `RuntimeError`가 Stage에 도달하기
직전 시점의 `.attempts` 속성을 안전한 6개 필드만 복사해 두었다(원본
함수의 동작·반환값·예외는 전혀 변경하지 않음 — 그대로 재발생).

---

## 2. 실행 환경과 안전장치(기존과 동일, 재확인)

| 항목 | 값 |
|---|---|
| 기준 커밋 | `main` `ca5b209`(PR #204 병합 반영 확인 후 실행) |
| GitHub 차단 | `urllib.request.OpenerDirector.open` 계측, `github.com` 감지 시 `AssertionError`(미발동 — 시도 없음) |
| 파일 쓰기 차단 | `pathlib.Path.write_text` 예외 발생 함수로 임시 교체(미발동 — 시도 없음) |
| `expose_target` | `False` 고정 |
| attempts 캡처 방식 | `call_engine_via_openrouter`를 얇게 wrapping, `RuntimeError` 발생 시 `.attempts`의 6개 허용 필드(`attempt`/`http_status`/`requested_candidates`/`selected_model`/`category`/`connection_error`)만 복사 후 원본 예외 재발생 |
| 저장소 변경 | 실행 전/후 `git status --short` 둘 다 clean |

---

## 3. 실측 결과 — 최초 관측된 HTTP Status

```
=== HTTP 요청 로그 ===
총 요청 횟수: 6 (GET 모델목록 2 + Chat POST 4, 이전과 동일 패턴)

[RuntimeError #1] (Stage 03 design_agent_design)
  attempt 1: http_status=401, category=malformed_response, connection_error=False,
             selected_model=None,
             requested_candidates=('inclusionai/ling-3.0-flash-vl:free',
                                    'nex-agi/nex-n2.5-mini:free',
                                    'nex-agi/nex-n2.5-pro:free')
  attempt 2: http_status=401, category=malformed_response, connection_error=False,
             selected_model=None,
             requested_candidates=(동일 3개, 미축소)

[RuntimeError #2] (Stage 04 identify_target)
  attempt 1: http_status=401, category=malformed_response, connection_error=False,
             selected_model=None,
             requested_candidates=(동일 3개)
  attempt 2: http_status=401, category=malformed_response, connection_error=False,
             selected_model=None,
             requested_candidates=(동일 3개)
```

- **관측된 사실**: 이번 실행에서 발생한 2건의 `RuntimeError`, 총 4개
  attempt **전부 `http_status=401`**로 동일했다.
- **HTTP 401(Unauthorized)의 표준 의미**: HTTP 사양상 401은 일반적으로
  "요청에 유효한 인증 자격 증명이 없음"을 의미하는 표준 상태 코드다.
  이는 HTTP 스펙 자체의 정의를 인용한 것이며, **이 세션/환경에서 실제
  원인이 자격 증명 문제였는지는 확정하지 않는다** — 추가 조사 없이는
  "왜 401인지"(API Key 미주입/만료/프록시 처리 방식 등)를 알 수 없다.
- `selected_model`이 매 attempt마다 `None`인 것은 기존에 이미 확인된
  코드 동작(4xx 경로는 `_parse_chat_response`가 model 필드를 추출하기
  전에 조기 반환) 그대로다 — 401도 4xx이므로 이 동작이 그대로 적용됨.
- `requested_candidates`가 두 attempt에서 동일한 것도 기존 확인
  사실과 일치(4xx는 `selected_model=None`이라 후보가 좁혀지지 않음).

---

## 4. Team → Stage 위임, 구조적 결과 (기존과 동일)

- Stage 03: `design_agent_design()` 실패 → `run_stage_03`이 흡수 →
  `design`을 엔진 실패 메시지로 반환
- Stage 04: `identify_target()` 실패 → `run_stage_04`가 흡수 →
  `target=None`, `implementation`을 동일 형식 실패 메시지로 반환.
  `backend_agent_code_generation()`은 호출되지 않음
- Stage 05: `is_engine_failure()` 감지 → `code_review` 건너뜀,
  `verdict: FAIL`(`structural` blocking FAIL + `design_scope`/
  `test_execution` blocking INCONCLUSIVE)
- `validate_design_result`/`validate_implementation_result`/
  `validate_verification_result` **3종 전부 위반 없음**

---

## 5. Observability 기능 자체의 검증 결과

**PASS.** PR #204에서 구현한 `attempts` 속성이:
1. 실제 Team→Stage 경로의 real Engine 실패에서 **정상적으로 채워짐**
2. 기존 예외 타입(`RuntimeError` 단일)과 메시지 형식을 **전혀 바꾸지 않음**(Stage 03/04의 흡수 로직이 여전히 `_engine_failure_message(exc)`로 동일하게 동작 — `str(exc)` 포맷 불변 확인)
3. API Key/Authorization/prompt/response body — **이번 실행 스크립트도 이 값들을 전혀 캡처·출력하지 않았고**, `attempts`의 6개 필드 자체도 이런 값을 담지 않음(코드 설계상 원천적으로 불포함)

이는 PR #204의 설계 의도가 실제 real Engine 실패 상황에서 정확히 작동함을 처음으로 실측 확인한 것이다.

---

## 6. 명시적으로 미확인/미확정인 것

- **401의 실제 원인** — 확정하지 않는다(자격 증명 미주입/만료, 프록시 처리 방식, OpenRouter 계정 상태 등 여러 가능성이 있으나 이 문서는 추측하지 않는다)
- **성공 응답** — 여전히 미확보(누적 9회 전부 실패: T4-S1 1 + T4 2 + T5-A 2 + T5-C(최초) 2 + T5-C(재실행) 2 = 9회, 성공 0/9)
- **다른 status 코드가 나올 수 있는지** — 이번 관측은 단일 세션·단일 실행의 표본이며, 다른 시점/조건에서 다른 status가 나올 가능성을 배제하지 않는다

---

## 7. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- `stages/contracts.py` 5개 Contract — **무변경**
- `openrouter_engine.py`의 bounded retry, `mvp/parallel_runner.RetryPolicy` — **무변경**
- Team/Stage 책임 경계 — **무변경**
- 이번 실행 자체는 **코드를 전혀 수정하지 않음**(스크래치패드 임시 스크립트만 사용, 저장소 밖) — PR #204는 이미 병합된 상태를 그대로 사용했을 뿐
- Stop Trigger 미발동

---

## 8. 판정

| 항목 | 판정 |
|---|---|
| Team→Stage 03→04→05 non-mock 위임 재확인 | **PASS** |
| GitHub 접근 0건, 파일 쓰기 0건 | **PASS** |
| Contract 3종 검증 | **PASS** |
| Observability(`attempts`) 실측 동작 확인 | **PASS** — 최초로 HTTP status(401) 관측 성공 |
| 민감정보(API Key/Authorization/prompt/body) 비노출 | **PASS** |
| Chat Completion 성공 여부 | **NOT ESTABLISHED**(누적 0/9) |
| 401의 근본 원인 확정 | **NOT ESTABLISHED — 이 문서는 추측하지 않음** |

---

## 9. 기존 Evidence와의 관계

- `-0001`~`-0004`: 전부 `category=malformed_response`만 확인했고 실제 status 숫자는 몰랐다 — 이 문서가 **최초로 그 숫자(401)를 실측으로 채운 문서**다.
- PR #204(`e64addc`, `ca5b209`로 병합): 이 문서가 검증하는 대상 기능 자체.
- 원문 어디도 수정하지 않았다.

---

## Governance Review

- 새로운 Architecture/Layer/Component/Concept 추가 — **아니오**
- Baseline 문서 변경 — **아니오**
- `docs/decisions/adc/ADC.md` 변경 — **아니오**
- ADR 필요 여부 — **아니오**
- 코드 작성·수정 — **아니오**(스크래치패드 임시 스크립트만 사용, 저장소 밖)
- RFC → ADC → ADR 절차 생략 — **아니오**

## Self Review

- 401의 원인을 추측했는가 — **아니오**, §3/§6에서 "표준 HTTP 정의 인용"과 "이 환경에서의 실제 원인 미확정"을 명확히 구분
- 성공을 과장했는가 — **아니오**, §8에서 NOT ESTABLISHED로 명시
- API Key/Authorization/prompt/response body를 출력·저장했는가 — **아니오**
- 기존 Evidence 원문을 수정했는가 — **아니오**, 신규 문서만 작성
- Stop Trigger가 발동했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0005.md`(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `claude/dev-hq-t5c-observability-rerun`(신규). 이 문서만 작성했으며, 커밋 여부는 아래 완료 보고에서 확인한다.
