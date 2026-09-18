# ADR-0027 §10 Gate #9(Retry) / #10(Failure Classification) 최종 판정 — Evidence

**Date**: 2026-09-13
**Branch**: `claude/jarvis-openrouter-validation-bin9aj`
**연결 Evidence(전부 보존, 수정하지 않음)**:
`ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(`c39eb26`),
`OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`(`40300a4`),
`OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md`(`8678327`),
`ADR-0027-VALIDATION-GATE-12-RESOLUTION-0001.md`(`568e736`)
**작업 성격**: 테스트 추가/실행만 수행. Production 코드(`openrouter_engine.py`
포함) / Architecture / Contract / Governance 문서는 전혀 수정하지 않았다.
실제 OpenRouter API에 대한 egress는 이번 세션에서 0회.

## Summary

- 기존 테스트 infrastructure(`mvp/tests/fake_openrouter_server.py` —
  로컬 stdlib `http.server` 기반 결정론적 test double)가 이미
  `quota`/`server_error`/`malformed`/`empty_content`/
  `recover_on_retry` 모드를 전부 갖추고 있어 **실제 OpenRouter quota를
  전혀 소모하지 않고** retryable/terminal failure를 결정론적으로
  재현할 수 있었다. 새 Production logic 없이 이 기존 인프라만으로
  Gate #9/#10을 검증했다.
- 유일하게 부족했던 것은 "retry 횟수/종료 조건"을 직접 세는 장치였다
  — 기존 fake server는 `recover_on_retry` 모드에서만 호출 횟수를
  셌다. 이를 **모든 POST 모드에 대해 무조건 카운트**하도록
  최소 확장(테스트 인프라 파일 3줄 추가, Production 코드 아님)한 뒤,
  4개의 신규 focused test로 정확한 호출 횟수(1회 성공 시 1번,
  지속 실패 시 정확히 2번 — 무한 재시도 아님)를 실측했다.
- **Gate #9: PASS(실측 확정)**. **Gate #10: PASS(실측 확정)**.
- 전체 `mvp/tests`는 352 → **356 passed**(신규 4개 테스트 추가분),
  **6 skipped 그대로** — 기존 baseline 대비 회귀 없음.

## 1. Retry / Failure Handling 구현 추적

`mvp/openrouter_engine.py::call_engine_via_openrouter()`(무변경, 코드
재확인만 함):

```python
for attempt in range(2):  # 최초 1회 + bounded retry 최대 1회
    result = _single_chat_call(candidates, prompt, timeout)
    if result["content"]:
        return result["content"]

    last_failure_category = _classify_failure(result["http_status"], result["connection_error"])

    failed_model = result.get("selected_model")
    if failed_model and failed_model in candidates:
        candidates = tuple(c for c in candidates if c != failed_model)
    if not candidates:
        break

raise RuntimeError(
    f"OpenRouter call failed after retry (category={last_failure_category}, ...)"
)
```

- **Retry**: `for attempt in range(2)`로 구조적으로 상한이 2회(최초 +
  재시도 1회)로 고정돼 있다 — 실패 카테고리와 무관하게 동일하게
  적용된다(카테고리별 "재시도 skip" 분기 없음).
- **Failure Classification**(`_classify_failure`): `connection_error`
  → `"connection_error"`, `status==429` → `"429_quota"`,
  `status>=500` → `"5xx"`, `status>=400` → `"malformed_response"`,
  그 외(200인데 content 없음 등) → `"empty_response"`. 5개 카테고리
  전부 분류되며, quota는 다른 카테고리와 절대 섞이지 않는다(코드
  구조상 `if`/`elif` 순서로 배타적).
- **Terminal failure**: 재시도까지 소진(루프 종료 또는 candidates
  exhausted로 조기 `break`)하면 단일 `RuntimeError` 하나만 발생 —
  분류 결과(`category=...`)는 예외 메시지에 문자열로만 포함되고,
  예외 타입 자체는 항상 `RuntimeError` 하나로 고정된다(Stage/Agent
  계층에 새 예외 타입을 노출하지 않음, `RFC-0041` §Failure Boundary).
- **중요한 사실 확인**: Architecture(`RFC-0041` §Retry Boundary)가
  요구하는 분류는 "quota를 모델 품질 실패와 분리"뿐이다 —
  "retryable vs non-retryable"이라는 **별도의 카테고리 축은 코드에도
  Architecture에도 존재하지 않는다**. 모든 실패 카테고리(quota
  포함)가 동일하게 최대 1회 재시도를 받는다 — quota라고 재시도를
  건너뛰는 특별 취급이 없다(`openrouter_engine.py` 자체
  docstring: "quota 실패는... 그래도 재시도 자체는 수행한다").
  이번 검증은 이 사실 그대로를 실측했고, 존재하지 않는
  "non-retryable 전용 코드 경로"를 억지로 만들어 테스트하지
  않았다.

## 2. Fault Injection 방식 조사 — 기존 인프라로 충분함을 확인

`mvp/tests/fake_openrouter_server.py`(로컬 127.0.0.1 stdlib
`http.server`, 실제 OpenRouter egress 전혀 없음)가 이미 제공하는 모드:

| 모드 | 재현하는 상황 | Gate 대응 |
|---|---|---|
| `success` | 정상 응답 | 재시도 불필요 확인(#9) |
| `quota` | HTTP 429 | quota 분류(#10), quota도 재시도됨(#9/#10 경계) |
| `server_error` | HTTP 500 | 5xx 분류(#10), 지속 실패 시 bounded 종료(#9) |
| `malformed` | JSON 파싱 불가 응답 | malformed_response 분류(#10) |
| `empty_content` | 200이나 content 없음 | empty_response 분류(#10) |
| `recover_on_retry` | 1차 500 → 2차 성공 | retry가 실제로 회복시키는지(#9) |
| (연결 자체 거부, `127.0.0.1:1`) | connection refused | connection_error 분류(#10) |

이 모든 모드가 **이미 기존 테스트(`c39eb26` 이전부터 존재)에서
개별적으로 검증돼 있었다** — 이번 세션이 새로 발명한 것이 아니다.
부족했던 것은 "정확한 호출 횟수"를 세는 부분뿐이었다.

## 3. 최소 확장(테스트 인프라만, Production 코드 아님)

`fake_openrouter_server.py`의 `do_POST()` 최상단에
`self.server.call_count += 1`을 모드와 무관하게 무조건 추가(3줄) —
기존에는 `recover_on_retry` 모드에서만 카운트했다. 다른 Production
로직/Contract/Engine 변경 없음. 이 파일은 테스트 전용 fixture이며
`mvp/openrouter_engine.py`(Production)와 무관하다.

## 4. Gate #9 검증(Retry)

신규 테스트(`mvp/tests/test_openrouter_engine.py`):

| 테스트 | 확인 내용 | 결과 |
|---|---|---|
| `test_transient_failure_recovers_on_bounded_retry`(기존, 이번에 call_count 단언 추가) | 1차 500 → 2차 성공 → 응답 회복, `call_count == 2` | **PASS** |
| `test_successful_first_attempt_does_not_retry`(신규) | 1차 성공 시 재시도 없음, `call_count == 1` | **PASS** |
| `test_persistent_failure_stops_after_exactly_two_attempts`(신규) | 매번 500이어도 무한 재시도 없이 정확히 2회 후 `RuntimeError` | **PASS** |
| `test_quota_failure_still_attempts_bounded_retry`(신규) | quota(429)도 2회 시도(재시도 skip 없음), `429_quota` 메시지 확인 | **PASS** |

→ retryable failure 발생 확인 / retry 수행 확인 / retry 횟수(정확히
2회, bounded)·종료 조건(candidates 소진 또는 attempt 상한) 확인 /
성공(회복) 또는 terminal failure(`RuntimeError`)까지 정상 종료 확인
— **4개 항목 전부 실측 Evidence로 충족**.

## 5. Gate #10 검증(Failure Classification)

기존 테스트(변경 없음, 재확인만):

- `test_quota_failure_raises_single_runtime_error_after_retry` → `429_quota`
- `test_server_error_raises_runtime_error` → `5xx`
- `test_malformed_response_raises_runtime_error` → malformed 분류 경로
- `test_empty_content_raises_runtime_error` → empty_response 분류 경로
- `test_connection_refused_raises_runtime_error` → connection_error 분류 경로
- `test_classify_failure_separates_quota_from_other_categories` /
  `test_classify_failure_never_conflates_quota_with_malformed` →
  단위 레벨로 5개 카테고리 배타성 확인

신규 추가(`mvp/tests/test_workflow_ast_context.py`):

- `test_identify_target_real_openrouter_failure_surfaces_as_single_runtime_error`
  — `call_engine`을 mock하지 않고 **실제 `openrouter_engine` 경로를
  fake server로 통과**시켜, `identify_target()`(Stage 04 실제 Production
  진입점, `8678327`로 이미 OpenRouter 전환 완료)에서 발생한 quota
  분류(`429_quota`)가 **단일 `RuntimeError`로, 다른 예외 타입으로
  바뀌지 않고 그대로** 전달됨을 실측. → **PASS**
- 기존 `test_stage_04.py::test_engine_failure_in_identify_target_returns_error_message`
  (변경 없음)가 이미 "Engine 실패 메시지가 무엇이든 Stage 04의 3키
  Contract(`target`/`implementation`/`expose_target`)는 그대로
  유지된다"를 일반적으로 증명한다 — 위 신규 테스트가 만든 실제
  `429_quota` 메시지도 이 Contract 보존 경로를 그대로 통과한다
  (두 테스트를 조합하면 "실제 OpenRouter 분류 결과 → 실제
  `identify_target()` → Stage 04 Contract 무결"까지 체인이 실측으로
  연결된다).

→ retryable failure 분류(5xx/malformed/empty/connection) 확인 /
quota 분류가 별도로 존재함 확인 / "non-retryable" 전용 분기는
Architecture·코드 어디에도 없음을 §1에서 명시적으로 확인(억지로
만들지 않음) / terminal failure가 단일 `RuntimeError`로 처리됨
확인 / classification 결과가 Stage Contract를 깨뜨리지 않음을
실제 Production 호출 경로(`identify_target`)로 실측 확인 —
**Gate #10 요건 전부 실측 Evidence로 충족**.

## 사용한 fault injection / mock 방식

- **로컬 stdlib HTTP 서버**(`fake_openrouter_server.py`,
  `http.server.HTTPServer`를 `127.0.0.1`의 임의 포트에 기동) — 실제
  네트워크 스택은 타지만 목적지가 로컬호스트라 외부(OpenRouter) egress
  가 전혀 발생하지 않는다.
- `OPENROUTER_BASE_URL` 환경변수를 `monkeypatch.setenv()`로 이
  로컬 서버 주소로 바꿔치기 — Production 코드(`_resolve_base_url()`)는
  원래부터 이 환경변수를 지원하도록 설계돼 있어 별도 개조가
  필요 없었다(기존 인프라 그대로 사용).
- connection_error 재현은 `127.0.0.1:1`(어떤 서비스도 listen하지
  않는 포트)로 연결을 시도해 OS 레벨에서 즉시 거부되게 함 — 이 역시
  실제 egress 없음.

## 실제 OpenRouter quota 사용 여부

**0회.** 이번 세션에서 `openrouter.ai`로 나가는 요청은 단 한 번도
발생하지 않았다(모든 신규/기존 관련 테스트가 `127.0.0.1` 로컬 서버
또는 즉시 거부되는 로컬 포트만 사용). `grep`으로 관련 테스트 파일에
`openrouter.ai` 리터럴이 없음을 확인했다.

## 관련 테스트 결과

```
mvp/tests/test_openrouter_engine.py ...........................  (27 passed)
mvp/tests/test_workflow_ast_context.py .........                  (9 passed)
36 passed in 5.25s
```

## 전체 regression 결과

```
mvp/tests/  356 passed, 6 skipped in 40.26s
```

기존 baseline(352 passed, 6 skipped, `c39eb26`~`568e736`) 대비 **+4
신규 테스트만 추가, skip 6건 동일, 기존 테스트 전부 그대로 PASS** —
회귀 없음.

`py_compile`: `fake_openrouter_server.py`/`test_openrouter_engine.py`/
`test_workflow_ast_context.py` 전부 문법 오류 없음.

## Gate #9 / #10 최종 판정

- **Gate #9(Retry): PASS.**
- **Gate #10(Failure Classification): PASS.**

두 판정 모두 §4/§5의 실측 테스트 결과(로컬 fake server 기반, 실제
OpenRouter quota 미사용)에 근거하며, 추측이나 코드 미검토 상태의
낙관적 판단이 아니다.

## Architecture / Contract / Governance 변경 여부

- Architecture: 무변경.
- Contract: 무변경.
- Governance: RFC-0041/ADC-0044/ADR-0027 및 다른 어떤 문서도 수정하지 않음.
- Production Code: **무변경** — `mvp/openrouter_engine.py`를 포함해
  어떤 Production 파일도 이번 세션에서 diff가 없다. 변경된 파일은
  전부 `mvp/tests/` 아래 테스트 코드/fixture뿐이다.

## Branch / Commit / PR 상태

- Branch: `claude/jarvis-openrouter-validation-bin9aj`
- 이전 HEAD: `568e736`
- 본 Evidence 커밋 예정
- PR: 없음(사용자 명시적 요청 없음)

## ADR-0027 §10 Validation Gate 전체 현황(참고, 최신화)

`c39eb26` → `40300a4` → `8678327` → `568e736` → 본 문서를 종합하면:

| # | 항목 | 최종 판정 |
|---|---|---|
| 1~3 | Stage 01~03 Contract 회귀 없음 | PASS |
| 4 | Stage 04 Contract 회귀 없음 | PASS |
| 5 | Stage 05 Contract 회귀 없음 | PASS |
| 6 | Free Pool availability | PASS |
| 7 | Candidate ≤3 | PASS |
| 8 | `models[]` 구성 정확성 | PASS |
| 9 | Retry 정상 동작 | **PASS(본 문서)** |
| 10 | Failure classification | **PASS(본 문서, 아래 Post-Hoc Amendment 참조)** |
| 11 | Stage 05 실제 Implementation Review | PASS |
| 12 | 전체 E2E 1회 이상 실제 통과 | PASS |

## Post-Hoc Amendment (2026-09-18, PR #199 기반)

이 절은 본 문서 §2("Fault Injection 방식 조사")·§5("Gate #10 검증")의
기존 서술 중 부정확했던 부분을 사후에 정정한다. 아래 원문(§2 표,
§5, §"ADR-0027 §10 Validation Gate 전체 현황")은 삭제·수정하지
않고 그대로 보존하며, 이 절이 그 서술의 정확한 실제 의미를
덧붙인다 — `ADR-0027` §16이 이미 사용한 것과 동일한 Post-Hoc
Amendment 방식이다.

**정정 대상 서술**:

- §2 표의 `malformed` 행: "`malformed` | JSON 파싱 불가 응답 |
  malformed_response 분류(#10)"
- §5의 "`test_malformed_response_raises_runtime_error` → malformed
  분류 경로"
- §"관련 사실"의 "retryable failure 분류(5xx/malformed/empty/
  connection) 확인"

**실제 확인된 사실(PR #199, `068267e`)**:

1. `fake_openrouter_server.py`의 `mode="malformed"`는 실제로
   **HTTP 200 상태 + non-JSON 본문**(`b"not json"`)을 반환한다 —
   4xx 응답이 아니다.
2. `openrouter_engine.py::_classify_failure(status, connection_error)`
   는 `status >= 400`일 때만 `"malformed_response"`를 반환한다.
   HTTP 200은 이 조건을 만족하지 않으므로, `mode="malformed"`가
   실제로 만들어내는 분류 결과는 **`"malformed_response"`가 아니라
   `"empty_response"`다.**
3. 위 §2/§5의 세 서술은 `mode="malformed"`라는 fixture 이름과
   코드의 카테고리 이름 `"malformed_response"`가 같은 단어를
   공유해 생긴 혼동으로, **실제 코드 동작과 어긋난 부정확한
   서술이었다.**
4. `test_malformed_response_raises_runtime_error` 자신은
   `pytest.raises(RuntimeError)`만 확인할 뿐 `category` 문자열을
   검사하지 않으므로, "malformed 분류 경로를 확인했다"는 §5의
   서술은 이 테스트가 실제로 보장하는 것보다 강하게 서술되어 있었다.
5. **진짜 `malformed_response`(순수 HTTP 4xx, 429 제외) 경로**는
   이 문서가 작성된 시점까지 통합 테스트로 검증된 적이 없었다 —
   `mvp/tests/test_openrouter_engine.py`(PR #199, `068267e`)가
   `client_error_4xx`라는 신규 fixture mode(HTTP 400)와 4개 신규
   테스트(`test_2xx_body_that_is_not_json_classified_as_empty_
   response_not_malformed`, `test_http_4xx_response_classified_
   as_malformed_response`, `test_http_4xx_retry_does_not_narrow_
   candidates`, `test_http_4xx_error_message_candidates_tried_
   reflects_untouched_pool`)로 **처음 이 경로를 실측 검증했다.**

**Gate #10 PASS 판정에 대한 영향**: **판정을 뒤집지 않는다.**
Gate #10의 요건("quota를 모델 품질 실패와 분리")은 이 문서 §1이
이미 인용한 `test_classify_failure_separates_quota_from_other_
categories`/`test_classify_failure_never_conflates_quota_with_
malformed`(둘 다 `_classify_failure()`를 직접 호출하는 단위
테스트, 이번 정정과 무관하게 처음부터 정확했다)로 독립적으로
충족되어 있었다. 이번에 정정하는 것은 §2/§5가 **어떤 테스트가
무엇을 확인했는지에 대한 서술**이지, quota 분리라는 판정의
근거 자체가 아니다.

**변경 범위**: 이 절 추가만. §2/§5/"ADR-0027 §10 Validation Gate
전체 현황" 표의 기존 원문은 무수정(추적성 보존). Production 코드,
테스트 코드, Architecture, Contract, 다른 Governance 문서는
이 정정과 무관하며 수정하지 않았다.

**Evidence**: PR #199(`068267e9e88d505226df0e38995f57819885be90`,
squash merge), 본 세션의 "OpenRouter malformed_response 원인 조사"
및 "PR #199 병합 확인 및 Gate #10 Evidence 문서 정확성 검토" 작업.

**12개 항목 전부 PASS.**
