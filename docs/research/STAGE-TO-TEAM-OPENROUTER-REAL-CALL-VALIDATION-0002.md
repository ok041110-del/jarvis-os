# Stage → Team OpenRouter Real Call Validation (2) — 축소형 E2E와 실패 전파 검증

## Summary

- `STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001.md`(단일
  `call_engine_via_openrouter()` 호출 1건)에 이어, 이번에는 **Team
  (Architecture/Implementation/Validation) → Stage 03→04→05 실제
  non-mock 위임 경로 전체**를 GitHub 접근·파일 쓰기 없이 최소 고정
  입력으로 실행했다.
- 실제 HTTP 요청 6회(전부 `openrouter.ai`), GitHub 요청 0회, 파일
  변경 0회(`git status --short` 실행 전후 모두 clean)를 실측했다.
- 논리적 Engine 호출은 2건(Stage 03 `design_agent_design()`, Stage 04
  `identify_target()`) 시도됐고 **둘 다 실패**(`category=
  malformed_response`, `candidates_tried=3`) — Stage 04의 `backend_
  agent_code_generation()`과 Stage 05의 `backend_agent_code_review()`는
  선행 실패로 인해 **호출 자체가 발생하지 않았다.**
- 실패는 Stage/Team 계층에서 설계된 대로 안전하게 흡수됐다: Stage 04가
  예외를 잡아 `target=None` + 엔진 실패 메시지로 반환했고, Stage 05가
  `is_engine_failure()`로 이를 감지해 `code_review`를 건너뛰었으며,
  `DesignResult`/`ImplementationResult`/`VerificationResult` Contract
  3종 전부 위반 없이 통과했다.
- 실패 원인(실제 HTTP status 숫자, 실패한 모델 ID, 응답 body)은
  **코드가 구조적으로 폐기하기 때문에 확인 불가**하며, 이번 문서도
  추측으로 원인을 확정하지 않는다.
- **이번 결과를 정상 성공 경로의 검증으로 해석하지 않는다** — 성공
  응답은 이번까지 누적 0/3(T4-S1 1건 + 이번 2건)으로 여전히 미확보다.

---

## 1. 목적과 범위

`STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001.md`는 단일 함수
호출만 다뤘다. 이 문서는 그 다음 단계로, **Team → Stage 03→04→05의
실제 위임·Handover·Contract 검증**을 GitHub 접근과 파일 쓰기 없이
최소 범위로 실행한 결과를 기록한다.

범위에 포함: `architecture_team.run_architecture_team()` →
`implementation_team.run_implementation_team(expose_target=False)` →
`validation_team.run_validation_team()`, 고정 stub 입력(`candidate_index`를
"후보 없음, UNKNOWN으로 응답" 유도 문구로 고정해 `identify_target()`이
`target=None`을 반환하도록 유도).

범위에서 제외: 전체 `run_workflow()`(Team 01~05 전체), GitHub
Repository 접근, `expose_target=True`, Production 코드/테스트 수정.

---

## 2. 실행 조건 및 안전장치

| 조건 | 값 |
|---|---|
| 실행 위치 | 세션 스크래치패드(저장소 밖), 저장소 코드 무수정, `importlib`로 Team 모듈 동적 로드 |
| GitHub 차단 | `urllib.request.OpenerDirector.open`을 계측해 `github.com`/`api.github.com` URL이 감지되면 즉시 `AssertionError`로 중단(발동되지 않음 — 시도 자체가 없었음) |
| 파일 쓰기 차단 | `pathlib.Path.write_text`를 호출 시 `AssertionError`를 던지도록 임시 교체(발동되지 않음 — 시도 자체가 없었음) |
| `expose_target` | `False` 고정 |
| 저장소 변경 | 실행 전/후 `git status --short` 둘 다 clean |

---

## 3. 실측 결과

```
GET  https://openrouter.ai/api/v1/models
POST https://openrouter.ai/api/v1/chat/completions
POST https://openrouter.ai/api/v1/chat/completions
GET  https://openrouter.ai/api/v1/models
POST https://openrouter.ai/api/v1/chat/completions
POST https://openrouter.ai/api/v1/chat/completions
```

- **총 6회**: 모델 목록 GET 2회(Stage 03/Stage 04 각 1회) + Chat POST
  4회(각 호출당 최초 1 + bounded retry 1) = 2개의 논리적 Engine 호출이
  각각 실패로 종결됨을 정확히 설명한다.
- **Stage 03**(`design_agent_design`): 실패 → `run_stage_03`의
  `try/except`가 흡수 → `design = "Engine call failed: OpenRouter call
  failed after retry (category=malformed_response, candidates_tried=3)"`
  (104자)
- **Stage 04**(`identify_target`): 자체 `call_engine()` 호출이 동일하게
  실패 → 예외가 `run_stage_04`의 최상위 `try/except`로 전파 → `target=
  None`, `implementation`이 동일 형식의 엔진 실패 메시지(104자)로 반환.
  **`backend_agent_code_generation()`은 호출되지 않았다**(도달 전에
  이미 예외 발생).
- **Stage 05**: `is_engine_failure(implementation) == True`를 정확히
  감지해 `code_review = "(Stage 04 Engine 실패로 Code Review를
  건너뜀)"` — **`backend_agent_code_review()` 호출 없음.**
  `verdict = "FAIL"`(`structural` blocking FAIL + `design_scope`/
  `test_execution` blocking INCONCLUSIVE).
- **GitHub 요청**: 0건. **파일 변경**: 0건(`git status --short` clean).
- **API 키 노출**: 없음(요청 URL/method만 계측, 헤더·본문·응답 내용
  미출력).

---

## 4. Contract 검증 결과

| Contract | 검증 함수 | 결과 |
|---|---|---|
| `DesignResult` | `contracts.validate_design_result(stage_03_output)` | **위반 없음**(`skeleton`/`design` 2/2 키 보존, 실패 시에도 형태 유지) |
| `ImplementationResult` | `contracts.validate_implementation_result(stage_04_output)` | **위반 없음**(`target`/`implementation`/`expose_target` 3/3 키 보존) |
| `VerificationResult` | `contracts.validate_verification_result(stage_05_output)` | **위반 없음**(`required_checks` 4개 전부가 `check_results`에 반영되고 SKIPPED 없이 판정에 실제 반영됨) |

Stage 03→04, 03+04→05 Handover는 재해석 없이 그대로 전달됨을 실측
확인했다 — **실패 경로에서도 Contract·Handover가 mock 테스트가
보장한 것과 동일하게 동작함을 non-mock으로 처음 확인**했다.

---

## 5. 실패 패턴 조사 (추측 배제, 확인/미확인 구분)

| 항목 | 상태 | 근거 |
|---|---|---|
| 실제 HTTP status 숫자(400/403/404 등) | **미확인 — 확인 불가능** | `_single_chat_call()`이 status를 `_classify_failure()`에만 넘기고 최종 예외 메시지에는 포함하지 않음(코드 구조상 폐기) |
| Content-Type/JSON 여부 | **미확인** | `_parse_chat_response()`는 `status>=400`일 때 파싱 결과를 보기 전에 즉시 `return None, None` — Content-Type 자체를 읽지 않음 |
| 실패한 모델 ID·후보 3개 목록 | **미확인** | 4xx 경로는 `selected_model` 추출 전에 조기 반환되므로 코드 자체가 알 수 없음. 이번 실행 계측도 후보 목록을 로깅하지 않음(민감정보 최소화 목적) |
| `malformed_response` 분류 조건 | **확인됨(코드)** | `status>=400`이고 `429`/`5xx`가 아닐 때만 반환, 배타적 |
| `candidates_tried=3`의 의미 | **확인됨(코드)** | "시도 횟수"가 아니라 "끝까지 제외 안 된 후보 개수"(4xx는 `selected_model=None`이라 후보가 절대 좁혀지지 않음) |
| RetryPolicy(`mvp/parallel_runner.py`) 관련 여부 | **확인됨 — 무관** | 이 클래스는 Stage 01 Multi-Agent Reasoning에서만 사용되며, Stage 03/04의 OpenRouter 실패는 `openrouter_engine.py` 내부의 별도 인라인 `for attempt in range(2)` 루프(최초 1 + retry 1)만 거쳤다 |
| T4-S1(단일 호출 1건)과의 공통점 | **확인됨** | 이번 2건 + T4-S1 1건, 총 3건 전부 `category=malformed_response`, `candidates_tried=3`으로 동일 — 코드 구조상 예정된 동일 메시지 형식일 뿐, "3건이 실제로 같은 원인이었다"는 것까지 확정하지는 않는다 |
| PR #199(`068267e`)·PR #200(`0cf39e5`)와의 관계 | **확인됨** | 두 PR은 `malformed_response`가 "순수 HTTP 4xx(429 제외)"임을 fake server 기반으로 정의·정정했다(§`ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md`). 이번 실측 분류는 그 정의와 정확히 일치하며 이름-의미 혼동과는 무관하다. 다만 두 PR 모두 "실제 운영 환경에서 왜 4xx가 발생하는가"는 다루지 않았다(fake server 대상 단위/통합 테스트였을 뿐, 실제 OpenRouter 대상 실행이 아니었음) |

**원인 결론**: 미확정. 추가 로깅(응답 status/본문 보존) 없이는 코드
구조상 원천적으로 확정할 수 없으며, 이는 이번 조사가 다다를 수 있는
한계다.

---

## 6. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- `stages/contracts.py` 5개 Contract — **무변경**
- `call_engine_via_openrouter()`의 bounded retry, `mvp/parallel_runner.RetryPolicy` — **무변경**(관찰만 함, 코드 수정 없음)
- Team/Stage 책임 경계 — **무변경**
- Stop Trigger 미발동(Registry/Scheduler/Runtime 일반화, 신규 Kernel Component, Architecture/Contract 변경 필요성, Team/Stage 책임 확장 — 어느 것도 관찰되지 않음)

---

## 7. Evidence 한계

- 정상 성공 응답 누적 확보 건수: **0/3**(T4-S1 1건 + 이번 2건 전부 실패)
- 실제 실패 모델·HTTP status 숫자 — 미확인, 확인 불가능한 코드 구조
- Stage 04의 `backend_agent_code_generation()`, Stage 05의 `backend_agent_code_review()` — 선행 실패로 인해 이번에도 실측하지 못함
- **이번 결과를 Team 01~05 전체 E2E의 PASS/성공으로 해석하지 않는다** — 검증한 것은 "실패가 안전하게 흡수·전파되고 Contract가 지켜진다"는 것이지, "정상 기능이 동작한다"는 것이 아니다

---

## 8. 판정

| 항목 | 판정 |
|---|---|
| Team→Stage 03→04→05 non-mock 위임 | **PASS** |
| GitHub 접근 0건, 파일 쓰기 0건 | **PASS** |
| Contract 3종(Design/Implementation/Verification) 검증 | **PASS** |
| 실패 흡수·전파(Stage 04 흡수, Stage 05 code_review 스킵) | **PASS** |
| Chat Completion 성공 여부 | **NOT ESTABLISHED**(누적 0/3) |
| 실패 원인 확정 | **NOT ESTABLISHED — 코드 구조상 확인 불가** |
| T4(Team 경로 real Engine E2E) 전체 성공 | **NOT ESTABLISHED** |

---

## 9. 기존 Evidence와의 관계

- `STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0001.md`: 이 문서의
  선행 문서(단일 함수 호출 1건). 이번 문서는 그 결과를 대체하지 않고
  Team→Stage 통합 경로로 범위를 확장한 후속 문서다.
- `ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md`: `malformed_response`
  정의의 근거로 인용만 함, 원문 무수정.
- `STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md`:
  Team→Stage→Agent→`openrouter_engine.py` call path가 코드로 연결돼
  있음을 확인했으나 실제 API 호출은 시도하지 않았던 문서 — 이번 문서가
  그 경로의 **실패 처리 부분**을 최초로 non-mock 실측했다.

---

## Governance Review

- 새로운 Architecture/Layer/Component/Concept 추가 — **아니오**
- Baseline 문서 변경 — **아니오**
- `docs/decisions/adc/ADC.md` 변경 — **아니오**
- ADR 필요 여부 — **아니오**
- 코드 작성·수정 — **아니오**(스크래치패드 임시 스크립트만 사용, 저장소 밖)
- RFC → ADC → ADR 절차 생략 — **아니오**(이번 발견은 절차 생략이 필요한 성격이 아님)

## Self Review

- 실패를 성공으로 과장했는가 — **아니오**, §8에서 명시적으로 NOT ESTABLISHED 판정
- 기존 Evidence 원문(`-0001`, PR #199/#200 관련 문서)을 수정했는가 — **아니오**, 신규 문서만 작성
- 원인을 추측으로 확정했는가 — **아니오**, §5에서 확인/미확인을 구분
- Stop Trigger가 발동했는가 — **아니오**
- RetryPolicy/Contract/Architecture를 변경했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0002.md`(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `claude/dev-hq-team-validation-evidence`(기존 `-0001` 문서와 동일 작업 단위). 이 문서만 작성했으며, 커밋·PR은 수행하지 않았다(사용자 지시).
