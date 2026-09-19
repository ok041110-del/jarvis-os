# Stage → Team OpenRouter Real Call Validation (3) — T5-A 성공 표본 확보 시도

## Summary

- T5 Kernel Boundary Validation의 첫 실행 단위인 **T5-A**(성공 표본
  확보 시도)의 결과를 기록한다. `-0002`와 동일한 Team→Stage 03→04→05
  경로·동일 안전장치·동일 고정 입력으로, "이번에는 성공 응답이
  나오는지"만 다시 관찰했다.
- 결과는 **다시 실패**다. Stage 03(`design_agent_design`), Stage 04
  (`identify_target`) 두 논리적 Engine 호출 모두 실패했고, Stage 04의
  `backend_agent_code_generation()`·Stage 05의 `backend_agent_code_
  review()`는 선행 실패로 호출되지 않았다.
- 이번에도 GitHub 요청 0건, 파일 변경 0건(`git status --short`
  clean), `DesignResult`/`ImplementationResult`/`VerificationResult`
  Contract 3종 전부 위반 없이 통과했다.
- **성공 경로는 여전히 검증되지 않았다.** `-0001`(1건) + `-0002`(2건)
  + 이번(2건)을 합쳐 **누적 성공 0/5, 실패 5/5**다.
- 실패 원인(HTTP status 숫자, 실패 모델 ID, 응답 본문)은 이번에도
  확인하지 않았다 — 코드가 그 정보를 구조적으로 보존하지 않기
  때문이며, 이 문서도 원인을 추측으로 확정하지 않는다.

---

## 1. 목적 및 검증 범위

**목적**: `STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0002.md`가
Team→Stage 03→04→05 경로에서 실패 처리(예외 흡수, Contract 준수)를
확인했으나 성공 표본을 확보하지 못한 채 끝났다 — T5-A는 그 이후
**"이번에는 성공 응답이 나오는가"**만 관찰하기 위해, 동일 경로를
재시도(강제 없음, 자연스러운 1회 실행)한 것이다.

**범위에 포함**: `architecture_team.run_architecture_team()` →
`implementation_team.run_implementation_team(expose_target=False)` →
`validation_team.run_validation_team()`, `-0002`와 동일한 고정 stub
입력(`candidate_index`를 "후보 없음, UNKNOWN 응답 유도" 문구로 고정).

**범위에서 제외**: 전체 `run_workflow()`, GitHub Repository 접근,
`expose_target=True`, 성공을 유도하기 위한 입력 조작이나 재시도
강제, Production 코드/테스트 수정.

---

## 2. 실행 환경과 안전장치

| 항목 | 값 |
|---|---|
| 기준 커밋 | `main` `5a486eb`(사전 확인 완료, `-0001`/`-0002` Evidence 포함) |
| 실행 위치 | 세션 스크래치패드(저장소 밖), `importlib`로 Team 모듈 동적 로드, 저장소 코드 무수정 |
| GitHub 차단 | `urllib.request.OpenerDirector.open` 계측 — `github.com` 포함 URL 감지 시 즉시 `AssertionError`(발동 안 됨 — 시도 자체 없음) |
| 파일 쓰기 차단 | `pathlib.Path.write_text`를 예외 발생 함수로 임시 교체(발동 안 됨 — 시도 자체 없음) |
| `expose_target` | `False` 고정 |
| RetryPolicy | 우회하지 않음 — `call_engine_via_openrouter()` 내장 bounded retry(최초 1 + 재시도 1, 최대 2회)만 그대로 소진. 성공을 위한 추가 재시도·입력 조작 없음 |
| 저장소 변경 | 실행 전/후 `git status --short` 둘 다 clean |

---

## 3. Team → Stage 03→04→05 실제 위임 결과

`-0002`와 동일하게, 3개 Team이 실제 Stage 함수를 정확한 인자로
호출하는 위임 경로가 이번에도 그대로 재현됐다(코드 변경이 없었으므로
당연한 결과이나, **실행으로 재확인**한 것 자체가 이번 표본의 의미다).

---

## 4. Engine 호출 결과와 실패 상태

| 호출 | 결과 |
|---|---|
| Stage 03 `design_agent_design()` | **실패** — `design_is_engine_failure: True`, `design_length: 104` |
| Stage 04 `identify_target()` | **실패** — `implementation_is_engine_failure: True`, `implementation_length: 104`, `target: None` |
| Stage 04 `backend_agent_code_generation()` | **호출되지 않음**(`identify_target()` 실패로 도달 전 예외 발생) |
| Stage 05 `backend_agent_code_review()` | **호출되지 않음**(`code_review_skipped: True`) |

실패 형식은 `-0001`/`-0002`와 동일한 시그니처("Engine call failed:
OpenRouter call failed after retry (category=malformed_response,
candidates_tried=3)")로 재현됐다.

---

## 5. Contract validator 3종 결과

| Contract | 결과 |
|---|---|
| `validate_design_result(stage_03_output)` | **위반 없음** |
| `validate_implementation_result(stage_04_output)` | **위반 없음** |
| `validate_verification_result(stage_05_output)` | **위반 없음**(`required_checks` 4개 전부 `check_results`에 반영, SKIPPED 없이 판정 반영) |

`Contract Violations: 없음` — 실패 상태에서도 Contract가 지켜짐을
재확인.

---

## 6. Stage 03/04 예외 흡수 및 Stage 05 처리

- **Stage 03**: `design_agent_design()` 실패 → `run_stage_03`의
  `try/except`가 흡수 → `design`을 엔진 실패 메시지로 반환(예외
  전파 없음)
- **Stage 04**: `identify_target()` 실패가 `run_stage_04`의 최상위
  `try/except`로 전파 → `target=None`, `implementation`을 동일 형식
  실패 메시지로 반환
- **Stage 05**: `is_engine_failure(implementation) == True`를 정확히
  감지 → `code_review`를 "(Stage 04 Engine 실패로 Code Review를
  건너뜀)"으로 대체, **실제 호출 없음** → `verdict: FAIL`(`structural`
  blocking FAIL + `design_scope`/`test_execution` blocking
  INCONCLUSIVE)
- 세션 스크립트 최상위 `failed_at`/`error`는 둘 다 `None` — 즉
  Team/Stage 계층에서 예외가 바깥으로 새어나가지 않고 전부 흡수됨을
  다시 확인

---

## 7. HTTP 요청 실측

```
GET  https://openrouter.ai/api/v1/models
POST https://openrouter.ai/api/v1/chat/completions
POST https://openrouter.ai/api/v1/chat/completions
GET  https://openrouter.ai/api/v1/models
POST https://openrouter.ai/api/v1/chat/completions
POST https://openrouter.ai/api/v1/chat/completions
```

- **총 6회, 고유 host 1개(`openrouter.ai`)** — `-0002`와 정확히
  동일한 횟수·패턴(모델 목록 GET 2 + Chat POST 4, 2개 논리 호출 ×
  각 bounded retry 소진)
- **GitHub 요청 0건**

---

## 8. 파일 변경 및 Working Tree 상태

- 실행 전/후 `git status --short`: **둘 다 clean**
- `Path.write_text` 차단 장치: **미발동**(시도 자체 없음 — `target=None`이라 관련 코드 경로 미도달)

---

## 9. 성공 경로 미검증 — 누적 결과

**성공 경로는 이번에도 검증되지 않았다.** 강제로 성공을 유도하지
않았고(입력 조작·추가 재시도 없음), 자연스러운 1회 실행 결과가
실패였다는 사실을 그대로 기록한다.

| 문서 | Engine 호출 건수 | 성공 | 실패 |
|---|---|---|---|
| `-0001`(단일 함수 호출) | 1 | 0 | 1 |
| `-0002`(Team→Stage 03→04→05, 축소형 E2E) | 2 | 0 | 2 |
| `-0003`(이 문서, T5-A) | 2 | 0 | 2 |
| **누적** | **5** | **0** | **5** |

**누적 성공 0/5, 실패 5/5.**

---

## 10. 확인된 사실과 미확인 사항 (추측 배제)

| 항목 | 상태 |
|---|---|
| Team→Stage 위임이 실제로 동작하는가 | **확인됨**(실행 사실) |
| 실패 시 Contract가 지켜지는가 | **확인됨**(실행 사실, 3종 전부) |
| 실패가 Stage/Team 경계 밖으로 새지 않는가 | **확인됨**(실행 사실) |
| GitHub 접근·파일 쓰기가 발생했는가 | **확인됨 — 발생하지 않음**(실행 사실) |
| 성공 응답이 확보됐는가 | **확인됨 — 확보되지 않음**(실행 사실, 0/5) |
| 실제 HTTP status 숫자 | **미확인 — 확인 불가능**(코드가 폐기, `-0001`/`-0002`와 동일한 한계) |
| 실패한 모델 ID·후보 목록 | **미확인**(코드가 4xx 경로에서 `selected_model`을 추출하지 않음) |
| 실패 원인(계정 정책/모델별 거부/일시적 비가용 등) | **미확정** — 추측하지 않는다 |

---

## 11. 기존 Evidence와의 관계 및 구분

- `-0001`: 단일 함수 호출 1건 검증. 이 문서와 **범위가 다름**(Team 위임 없음).
- `-0002`: 이 문서와 **동일한 실행 경로·동일 안전장치**를 사용한 선행 문서. `-0002`가 이미 확인한 사실(위임/Contract/실패 흡수)을 이 문서가 **독립적으로 재현**했다는 것이 이번 표본의 의미이며, `-0002`의 결론을 대체하지 않는다.
- **이 문서는 `-0002`와 별개의 독립 실행 표본이다** — 같은 코드에 대한 반복 관찰이지, `-0002`의 결과를 다시 쓰는 것이 아니다.
- 세 문서 모두 "성공 미확보"라는 점에서 **모순 없이 일관**된다.

---

## 12. 제한사항 및 후속 검증 항목

**이번 문서가 다루지 않은 것(제한사항)**:
- 새로운 실행이나 네트워크 요청 없음(사전 조건대로 T5-A의 기존 실행 결과만 인용)
- 코드, Architecture, Contract 변경 없음
- 실패 원인 확정 시도 없음

**후속 검증 항목**:
- 성공 표본 확보를 위한 추가 시도(입력 조작이나 강제 재시도가 아닌, 동일 조건의 반복 관찰)
- `identify_target()`이 실제로 target을 식별하는 경로(로컬 파일 읽기 포함)의 실측 — 성공 표본이 나와야 관찰 가능
- `expose_target=True` 경로의 Team 기반 non-mock 실측(안전 승인 필요)
- HTTP status/응답 본문을 보존하는 관측 강화가 필요한지에 대한 판단(코드 변경이 필요하므로 별도 RFC 검토 대상일 수 있음 — 이 문서는 그 판단을 내리지 않는다)

---

## 13. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- `stages/contracts.py` 5개 Contract — **무변경**
- `call_engine_via_openrouter()`의 bounded retry, `mvp/parallel_runner.RetryPolicy` — **무변경**, 우회 없음
- Team/Stage 책임 경계 — **무변경**
- Stop Trigger 미발동(Registry/Scheduler/Runtime 일반화, 신규 Kernel Component, Architecture/Contract 변경 필요성, Team/Stage 책임 확장 — 어느 것도 관찰되지 않음)

---

## Governance Review

- 새로운 Architecture/Layer/Component/Concept 추가 — **아니오**
- Baseline 문서 변경 — **아니오**
- `docs/decisions/adc/ADC.md` 변경 — **아니오**
- ADR 필요 여부 — **아니오**
- 코드 작성·수정 — **아니오**(스크래치패드 임시 스크립트만 사용, 저장소 밖)
- RFC → ADC → ADR 절차 생략 — **아니오**

## Self Review

- 성공 경로가 검증됐다고 표현했는가 — **아니오**, §9/§10에서 명시적으로 미검증·0/5 판정
- HTTP status나 실제 원인을 추측했는가 — **아니오**, §10에서 확인/미확인 명확히 구분
- `-0001`/`-0002`와 모순되는 서술이 있는가 — **아니오**, §11에서 관계와 구분을 명시
- 기존 Evidence 원문을 수정했는가 — **아니오**, 신규 문서만 작성
- Stop Trigger가 발동했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0003.md`(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `main`(작성 시점 기준). 이 문서만 작성했으며, 커밋·push·PR은 수행하지 않았다(사용자 지시).
