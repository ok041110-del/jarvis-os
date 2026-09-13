# ADR-0027 §10 Validation Gate 실측 검증 — Evidence

**Date**: 2026-09-13
**Branch**: `claude/jarvis-openrouter-validation-bin9aj`
**Base commit(검증 시작 시점)**: `865d41adacd0c2c23c58a206113df4c17bd77185`
**작업 성격**: 검증(Validation)만 수행 — Production 코드/Architecture/Contract/Governance 문서는 변경하지 않았다.

## Summary

- ADR-0027 §10의 12개 항목 중 **실제로 PASS로 확정할 수 있는 항목은 6개(1/2/3/6/7/8)**,
  **BLOCKED 2개(9/10 — 실사용 실패 조건 재현 불가, 코드 레벨만 검증됨)**,
  **FAIL 3개(4/11/12 — Stage 04 진입점의 실제 defect로 차단)**,
  **PASS(구조적) 1개(5 — Contract 형태는 유지되나 내용 검증은 4/11에 종속)**다.
- **핵심 발견(신규 defect)**: Stage 04 Production 진입점(`stage_04.py::run_stage_04`)이
  모든 실행에서 무조건 호출하는 `identify_target()`
  (`mvp/workflow_ast_context.py`)이 여전히 `chatgpt_engine.py`를 사용한다.
  이 저장소에 연결된 ChatGPT/OpenAI 자격증명은 quota가 0이라
  **Stage 04는 OpenRouter Migration과 무관하게 첫 단계(Target
  Identification)에서 항상 실패**한다. `backend_agent_code_generation`
  (OpenRouter로 이미 전환됨)에는 도달조차 하지 못한다.
- 따라서 **Gate는 PASS로 판정하지 않는다 — OPEN/BLOCKED 유지**. Stage
  01~03은 실제 OpenRouter 호출로 정상 동작을 확인했으나, Stage 04~05는
  이 defect 때문에 실제 구현 흐름을 검증할 수 없었다.
- Production 코드는 이번 세션에서 전혀 수정하지 않았다(defect는 보고만
  하고 수정하지 않음 — 사용자 명시적 지시).

## 0. 사전 확인

- `git status --short` → 검증 시작 시점 clean, 로컬 HEAD == 원격 HEAD(`865d41a`).
- `OPENROUTER_API_KEY` 환경변수: **미설정**. `OPENAI`류 자격증명도 세션
  환경변수에 직접 존재하지 않는다(egress는 CCR Agent Proxy 경유).
- `openrouter_engine.py::_auth_headers()`를 직접 호출해 실제로
  `{}`(Authorization 헤더 없음)를 반환함을 코드로 재확인 — API key
  하드코딩/유출 없음.

## A. 12개 Validation Gate 항목별 판정표

| # | 항목 | 판정 | 근거 |
|---|---|---|---|
| 1 | Stage 01 Contract 회귀 없음(실제 응답) | **PASS** | 실제 E2E 실행에서 `stage_01` 6개 Contract 키 전부 생성, 내용이 이슈에 특정된 실제 한국어 응답(placeholder 아님) |
| 2 | Stage 02 Contract 회귀 없음 | **PASS** | `stage_02` 5개 키 전부 생성, 실제 `task_dependency_agent.py`(OpenRouter 경유) 응답 |
| 3 | Stage 03 Contract 회귀 없음 | **PASS** | `stage_03` 2개 키 생성, `design.py`(OpenRouter 경유) 실제 설계 문서 응답(3180자) |
| 4 | Stage 04 Contract 회귀 없음 | **FAIL** | Contract 키(`target`/`implementation`/`expose_target`)는 존재하나 `implementation` 값이 `"Engine call failed: ChatGPT rate limit exceeded..."` — 실제 코드 생성 실패. 아래 §신규 defect 참조 |
| 5 | Stage 05 Contract 회귀 없음 | **PASS(구조적)** | 8개 Contract 키 전부 생성(`verdict` 포함) — 그러나 입력이 #4의 오류 문자열이라 **내용 검증은 무의미**, 구조만 PASS |
| 6 | Free Pool availability(실행 시점 재조회) | **PASS** | `_fetch_free_model_pool()` 실측: 19개 free 모델 실시간 조회 성공 |
| 7 | Candidate ≤3 적용(Production 경로) | **PASS** | 19개 → Filter 후 17개 → `_select_candidates()` 결과 정확히 3개(`MAX_CANDIDATES` 준수) |
| 8 | `models[]` 요청 구성 정확성 | **PASS** | 실제 POST body `{"models":[...3개...], "messages":[...], "max_tokens":...}`로 OpenRouter가 200 OK + 실제 모델(`inclusionai/ling-3.0-flash-vl:free`, provider `Novita`) 응답 반환 확인 |
| 9 | Retry 정상 동작(bounded, 최대 1회) | **BLOCKED** | 코드 레벨 24개 unit test(fake server)로는 이미 검증됨. 실제 OpenRouter 호출은 이번 세션에서 전부 1차 성공 — 실패를 인위로 유발하는 것은 실 자원 낭비/남용 소지가 있어 지양함. **실사용 조건 재현 안 됨** |
| 10 | Failure classification(quota ≠ 모델 품질 실패) | **BLOCKED** | 위와 동일 사유 — OpenRouter 자체의 실패(429/5xx)는 재현하지 못함. 다만 **ChatGPT 쪽 429 quota 실패는 실측**됐고(§신규 defect), 이는 `chatgpt_engine.py`의 기존 분류 로직이지 OpenRouter Migration 대상이 아니다 |
| 11 | Stage 05가 실제 Stage 04 Implementation으로 Review 수행 | **FAIL** | `--expose-target` 포함 재실행에도 Stage 04가 #4에서 이미 실패해 실제 구현 코드가 존재하지 않음 → Stage 05의 `structural`(FAIL, blocking)/`design_scope`/`test_execution`(둘 다 INCONCLUSIVE, blocking) 전부 실제 코드 Review를 수행하지 못함. **과거 "placeholder implementation" 문제가 다른 형태(Engine 실패)로 재발** |
| 12 | Stage 01→05 전체 E2E 1회 이상 실제 통과 | **FAIL** | 2회 실행(플래그 유무 각 1회) 모두 `verdict: FAIL`. 프로세스는 exit 0으로 "완주"했지만 Stage 04 실패가 top-level `failed_at`으로 승격되지 않고 문자열로 삼켜진 채 Stage 05로 전파됨(§관찰 사항 참조) — **진짜 E2E 성공이 아니다** |

## B. 실제 OpenRouter 호출 결과

- Free Pool 조회: `GET /api/v1/models` → HTTP 200, 19개 free 모델(`:free` suffix) 실시간 확인.
- Chat Completions: `POST /api/v1/chat/completions`(`models` 배열 3개) → HTTP 200, 실제 생성 응답 수신(중략 로그는 §신뢰성 참고).
- 인증: Authorization 헤더 없이 호출됐음에도 200 응답을 받음 — 이는 사용자 개인 OpenRouter 계정/과금과 무관한 **환경(CCR Agent Proxy) 경유 경로**로 보인다(TLS 인증서 발급자가 `CCR Upstream Proxy CA`로 확인됨, `api.openai.com` 자동 자격증명 주입과 유사한 메커니즘으로 추정). **사용자 소유의 실제 Production OpenRouter 계정으로 실측한 것은 아니다** — quota/과금 관점의 "진짜 Production 준비도"는 여전히 미검증으로 남는다.

## C. 실제 선택/사용된 free model

- Stage 01~03 실행 및 별도 확인 호출에서 후보 3개(`inclusionai/ling-3.0-flash-vl:free`, `nex-agi/nex-n2.5-mini:free`, `nex-agi/nex-n2.5-pro:free`) 중 **OpenRouter가 자체적으로 `inclusionai/ling-3.0-flash-vl:free`(provider: Novita)를 선택**해 실제로 사용함을 확인 — Jarvis 코드는 특정 모델을 지정하지 않았고 delegation이 실제로 동작했다(ADR-0027 §Engine Boundary와 일치).

## D. Stage 01~05 실제 실행 결과

- 이슈: "간단한 두 정수 합산 유틸 함수 추가"(작은 범위, 안전).
- 1차 실행(`cli.py issue.json`, `--expose-target` 없음): exit 0, `failed_at: None`, Stage 05 `verdict` 미확인(경고: blocking 체크 INCONCLUSIVE로 스킵됨).
- 2차 실행(`cli.py --expose-target issue.json`): exit 0, `failed_at: None`, Stage 05 `verdict: FAIL`(§A 표 #11/#12 근거).
- 두 실행 모두 종료 후 `git status --short` clean 확인 — Stage 05의 실제 소스 mutate→restore(`finally`) 로직이 정상 동작했다(이번 세션에서는 실제 코드 생성이 실패해 애초에 유의미한 mutate가 없었을 가능성이 높지만, 최소한 잔여 변경은 없었다).

## E. Stage 05 실제 implementation Review 검증 결과

- **검증 불가(BLOCKED by defect)**. Stage 04가 `identify_target()` 단계에서 실패해 `implementation` 필드에 실제 코드 대신 오류 문자열이 담겼고, Stage 05는 이를 대상으로 `structural_check`만 겨우 판정(FAIL, `engine_failed: true`)했을 뿐 `design_scope`/`test_execution`은 전부 `INCONCLUSIVE`로 남았다. **"실제 Stage 04 Implementation → Stage 05 Review" 흐름은 이번 세션에서 한 번도 실제로 검증되지 못했다.**

## F. quota / retry / failure 관련 Evidence

- **ChatGPT quota(실측, 신규 defect의 원인 중 하나)**: `identify_target()` 호출 시 실제로 `RuntimeError: ChatGPT rate limit exceeded (HTTP 429): {'error': {'message': 'You have no credits remaining...', 'type': 'insufficient_quota', 'code': 'credit_balance_exhausted'}}` 수신 — 이 저장소 환경에 연결된 ChatGPT 자격증명은 현재 크레딧이 0이다.
- **OpenRouter retry/failure(실사용 조건)**: 이번 세션에서 발생하지 않음(모든 실제 OpenRouter 호출이 1차 시도에서 200 성공) — §A #9/#10 BLOCKED 사유와 동일.
- **API Key 노출**: 없음 — `OPENROUTER_API_KEY` 자체가 미설정이었고, 어떤 로그/본 문서에도 key 문자열을 기록하지 않았다.

## G. 전체 regression test 결과

```
352 passed, 6 skipped in 35.15s   (pytest, hqs/development/)
```

기존 baseline(352 passed / 6 skipped)과 완전히 동일 — 이번 세션에서 회귀 없음. 단, **기존 test suite는 `identify_target()`의 실제 ChatGPT quota 실패를 전혀 잡아내지 못한다**(모두 mock/fake 기반) — 이는 테스트 커버리지 자체의 공백이며, 이번 실측 Gate 실행이 아니었다면 발견되지 않았을 것이다.

## H. 새 Evidence 문서 경로

`docs/research/ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(본 문서)

## I. Gate 최종 판정

**OPEN / BLOCKED** — PASS로 승격하지 않는다.

- PASS 확정: #1, #2, #3, #6, #7, #8 (6/12)
- BLOCKED(환경상 실사용 조건 재현 불가, 코드 레벨만 검증): #9, #10 (2/12)
- FAIL(신규 defect로 차단): #4, #11, #12 (3/12)
- 구조적 PASS(내용은 상위 defect에 종속): #5 (1/12)

**12개 전부 통과하지 못했으므로 §11 규정에 따라 Gate는 PASS가 아니다.**

## J. Architecture / Contract / Governance 변경 여부

- Architecture: 변경 없음.
- Contract: 변경 없음(Stage 01~03/05 Contract 키 형태는 실측으로도 그대로 유지됨을 재확인).
- Governance: RFC-0041/ADC-0044/ADR-0027 및 다른 어떤 RFC/ADC/ADR도 수정하지 않았다.
- Production Code: **변경 없음**(발견된 defect는 보고만 하고 임의 수정하지 않음 — 사용자 명시적 지시). 실행 중 발생한 Stage 05의 실제 파일 mutate는 `finally`로 복원됐고, 세션 종료 시점 `git status --short`가 clean임을 재확인했다.
- 새 Agent/Routing/Scoring 로직: 추가하지 않음.

## K. branch / commit / PR 상태

- Branch: `claude/jarvis-openrouter-validation-bin9aj`
- Commit(본 문서 커밋 예정) 기준 이전 HEAD: `865d41adacd0c2c23c58a206113df4c17bd77185`
- PR: 없음(사용자가 명시적으로 요청하지 않음, 이번 세션은 Validation 전용)

## 발견된 defect(수정하지 않음, 보고만 함)

**Defect**: `hqs/development/stages/04_implementation/stage_04.py`의 Production
진입점 `run_stage_04()`이 모든 호출에서 무조건 실행하는 Target
Identification 단계(`mvp/workflow_ast_context.py::identify_target`)가
`ADR-0027` Migration 이후에도 여전히 `chatgpt_engine.py`(3번째 Engine
도입 이전의 기존 Engine)를 사용한다. 이 파일은 과거 Migration
Evidence(`OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`)와
`test_engine_boundary.py`에서 "실제 Stage 01~05 파이프라인 호출부가
아니다 · Migration 범위 밖"으로 명시적으로 분류됐으나, 이는 **정적
import 확인만으로 내린 판단이었고 실제 E2E 실행으로 검증되지 않았다** —
실측 결과 `stage_04.py`가 이 함수를 직접, 무조건 호출하는 것으로 확인돼
그 분류가 틀렸음이 실증됐다.

이 defect의 실제 영향: 이 저장소의 ChatGPT 자격증명 quota가 0인 현재
상태에서는 **Stage 04(Team04)가 어떤 이슈를 넣어도 항상 첫 단계에서
실패**하며, OpenRouter로 이미 전환된 `backend_agent_code_generation`에는
전혀 도달하지 못한다. 이는 OpenRouter Migration 자체의 결함이 아니라
**Migration이 놓친 호출 경로(scope 판단 오류)**다.

이 defect는 이번 세션에서 수정하지 않았다 — 별도 세션/승인 하에
(a) `identify_target()`도 OpenRouter로 전환할지, 아니면 (b) 이 함수를
Migration Scope 자체에 정식으로 재포함시키는 절차(RFC-0041/ADC-0044/
ADR-0027 범위 내 단순 보완인지, 별도 Governance 판단이 필요한지)를
사용자가 먼저 결정해야 한다.

## 관찰 사항(defect는 아니나 기록)

`run_stage_04()`의 `try/except`가 Engine 실패를 `implementation` 필드에
문자열로 담아 반환하고 `raise`하지 않아, `workflow.py`의 top-level
`failed_at`이 설정되지 않고 파이프라인이 "완주"한 것처럼 보인다(exit
0). 이는 `MVP-0001`(`mvp/workflow.py::run_mvp_0001`)이 처음부터 채택한
기존 계약(Engine 실패도 2-키 Contract를 유지한 채 오류 메시지로
반환)을 Stage 04가 그대로 재사용한 것으로, **이번 Migration이 만든
새로운 문제가 아니다**. 다만 이 계약 때문에 "E2E가 끝까지 실행됐다"와
"E2E가 실제로 성공했다"가 육안으로 구분되지 않는다는 점은, Gate
판정 작업 자체의 난이도를 높이는 요인으로 기록해 둔다.
