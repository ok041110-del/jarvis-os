# `identify_target()` OpenRouter Migration 구현 + Gate #4/#11/#12 재검증 — Evidence

**Date**: 2026-09-13
**Branch**: `claude/jarvis-openrouter-validation-bin9aj`
**전제 Evidence**: `ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(`c39eb26`),
`OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`(`40300a4`) — 둘 다 보존, 수정하지 않음.

## Summary

- Scope Gap 분석(`40300a4`)의 결론대로 `identify_target()`의 Engine을
  `chatgpt_engine.py` → `openrouter_engine.py`로 전환했다 — **판단 로직은
  한 글자도 바꾸지 않음**(import 한 줄만 변경).
- `test_engine_boundary.py`의 Engine 분류를 실제 경로와 일치하도록
  갱신(파일 재분류 + 회귀 테스트 1개 교체).
- 실측 재검증 결과: **Gate #4/#11은 실제 Evidence로 PASS 확정**.
  **Gate #12는 여전히 FAIL** — 단, 원인은 이번에 고친 defect와
  무관한 별개의 환경 이슈(`sys.executable -m pytest`가 이 샌드박스의
  기본 `python3`에서 pytest 모듈을 찾지 못함, `ModuleNotFoundError`
  수준)로 확인됐다. **범위를 넘겨 이 pytest 환경 문제를 고치지 않았다.**
- Production 변경은 정확히 2개 파일, 각 파일 최소 diff로 제한됨(§변경
  파일 diff 참조). 다른 Production 파일은 전혀 건드리지 않았다.

## 변경 파일

1. `hqs/development/mvp/workflow_ast_context.py` — 11행 import 1줄만 변경:
   `from .chatgpt_engine import call_engine_via_chatgpt as call_engine`
   → `from .openrouter_engine import call_engine_via_openrouter as call_engine`
2. `hqs/development/mvp/tests/test_engine_boundary.py`:
   - `workflow_ast_context.py`를 `CHATGPT_ROUTED_FILES` → `OPENROUTER_ROUTED_FILES`로 재분류
   - `CHATGPT_ROUTED_FILES`가 빈 리스트가 됐음을 반영해
     `test_chatgpt_routed_files_import_chatgpt_engine_only` →
     `test_no_production_file_still_routed_to_chatgpt_engine`(빈 리스트
     유지 자체를 회귀 테스트로 고정)로 교체
   - 모듈 docstring/주석 갱신(어떤 RFC/ADC/ADR도 수정하지 않음 — 이
     테스트 파일 자체의 서술만 정정)

`identify_target()` 함수 본문, `_assemble_build_input`, Exposure Policy,
Stage 04 DAG, Contract, 다른 어떤 Production 파일도 변경하지 않았다.

## 해결된 문제

`c39eb26`이 실측으로 발견한 defect(Stage 04가 `identify_target()`
단계에서 `chatgpt_engine.py`의 quota 소진으로 항상 실패해
`backend_agent_code_generation`에 도달조차 못하던 문제)가 해소됐다 —
아래 §D/§E 실측으로 확인.

## 테스트 결과

### A. focused tests

```
mvp/tests/test_engine_boundary.py .............. (14 passed)
mvp/tests/test_workflow_ast_context.py ........  (8 passed)
mvp/tests/test_ast_context.py ........            (8 passed)
mvp/tests/test_openrouter_engine.py ....................... (24 passed)
mvp/tests/test_stage_04.py .........               (9 passed)
63 passed in 4.98s
```

### B. 전체 `mvp/tests`

```
352 passed, 6 skipped in 38.24s
```

baseline(`c39eb26` 시점 352 passed / 6 skipped)과 동일 — 회귀 없음.

### C. py_compile

```
python3 -m py_compile mvp/workflow_ast_context.py mvp/tests/test_engine_boundary.py stages/04_implementation/stage_04.py
→ OK(문법 오류 없음)
```

### G. 전체 regression(재확인)

```
352 passed, 6 skipped in 36.64s
```

## 실제 OpenRouter 호출 결과

- `identify_target()` 호출이 이제 `openrouter_engine.py` 경유로 실행되며,
  **ChatGPT quota 오류(`insufficient_quota`)가 더 이상 발생하지 않음**을
  2회의 실제 E2E 실행 모두에서 확인.
- **Credential 성격 재확인(오인 방지)**: 이번에도 `OPENROUTER_API_KEY`는
  이 환경에 설정돼 있지 않다(`_auth_headers()`가 `{}` 반환, 세션 환경변수
  확인 동일). 실제 200 응답은 여전히 **CCR Agent Proxy 경유 경로**로
  들어온 것이며, `api.openai.com` 자동 자격증명 주입과 유사한 인프라
  메커니즘으로 추정된다(TLS 인증서 발급자가 `CCR Upstream Proxy CA`).
  **이것은 사용자 개인/Production OpenRouter 계정의 quota 검증이
  아니다** — 코드 경로와 실제 응답 생성이 동작함을 확인한 것이지,
  사용자 소유 계정의 실사용 준비도를 검증한 것이 아니다. 이 구분을
  다시 한번 명시적으로 기록한다(사용자 지시 사항).

## Stage04 결과

두 issue로 각 1회씩, 총 2회 실제 실행(모두 `--expose-target`):

| Run | issue 성격 | `identify_target` 결과 | `implementation` |
|---|---|---|---|
| 1 | 완전 신규 모듈 추가 | `target: None`(정당한 결정적 판단 — 신규 모듈이라 기존 AST 대상 없음) | 실제 생성된 코드: `def add_two_numbers(a: int, b: int) -> int: return a + b` |
| 2 | 기존 함수(`workflow_hello_sdlc.py::run_hello_sdlc`) 수정 | `target: ['workflow_hello_sdlc', 'run_hello_sdlc']`(실제 AST 후보 색인에서 정확히 식별) | 실제 생성된 전체 파일 내용(주석 1줄만 추가하라는 지시를 반영) |

두 실행 모두 `identify_target()` 단계에서 **더 이상 오류가 발생하지
않았고**, `backend_agent_code_generation`(OpenRouter)까지 정상 도달해
실제 코드를 생성했다. 실행 후 `git status --short`는 두 번 다
의도한 변경 파일(`workflow_ast_context.py`/`test_engine_boundary.py`)
외에 잔여 변경이 없음을 확인(Stage 05의 mutate→`finally` 복원이
정상 동작).

## Stage05 Review 결과

| Run | structural | specification_scope | design_scope | test_execution | verdict |
|---|---|---|---|---|---|
| 1(target=None) | PASS(`engine_failed:false`) | INCONCLUSIVE | INCONCLUSIVE(blocking) | INCONCLUSIVE(blocking) | PARTIAL |
| 2(target 식별됨) | PASS | PASS(`target_in_scope:true`) | **PASS**(`scope_ok:true`) | **FAIL**(`returncode:1`) | FAIL |

Run 2에서 `code_review`/`structural`/`specification_scope`/`design_scope`가
전부 **실제 Stage 04 구현물을 대상으로 실측 PASS**했다 — placeholder가
아닌 진짜 코드에 대한 진짜 Review가 수행됐음을 실증한다(`ADR-0027`
§Contract Boundary "Stage 05는 반드시 실제 Stage 04 Implementation을
입력으로 받아야 한다" 요건 실측 충족).

`test_execution`만 FAIL했는데, 원인은:

```
/usr/local/bin/python3: No module named pytest
```

`stage_05.py`가 `subprocess.run([sys.executable, "-m", "pytest", ...])`로
호출하는데, 이 샌드박스의 `sys.executable`(`/usr/local/bin/python3`)에는
pytest가 모듈로 설치돼 있지 않다(이번 세션에서 pytest 실행에 실제 쓴
바이너리는 `/root/.local/bin/pytest`이며 이는 별도 경로다). **이는
OpenRouter Migration/`identify_target`과 완전히 무관한, 이 실행
환경만의 pytest 설치 경로 문제**다 — 코드 결함이 아니므로 수정하지
않았다(범위 확대 금지 지시에 따름).

## Gate #4 / #11 / #12 결과

- **#4(Stage 04 Contract 회귀 없음)**: **PASS**(실측 확정). 2회 실행
  모두 Contract 3키(`target`/`implementation`/`expose_target`) 정상
  생성, `implementation`에 실제 코드(오류 문자열 아님) 확인.
- **#11(Stage 05가 실제 Stage 04 Implementation으로 Review 수행)**:
  **PASS**(실측 확정). Run 2에서 실제 코드에 대해 `structural`/
  `specification_scope`/`design_scope`가 전부 실측 PASS, `code_review`도
  실제 내용 기반으로 응답함(placeholder 재발 없음).
- **#12(Stage 01→05 전체 E2E 1회 이상 실제 통과)**: **여전히 FAIL**.
  Run 2의 `verdict: FAIL`은 `test_execution`의 pytest 환경 문제
  때문이며, 이번에 고친 defect(ChatGPT quota/identify_target)와는
  무관하다. **Gate #12는 이 세션에서 PASS로 승격하지 않는다** — 별도
  환경 문제(이 샌드박스에 `sys.executable -m pytest` 실행 가능한
  pytest 설치)가 먼저 해결돼야 재검증 가능하다.

## Architecture / Contract / Governance 변경 여부

- Architecture: 무변경.
- Contract: 무변경(`identify_target`/Stage 04 반환 Contract 형태 동일).
- Governance: RFC-0041/ADC-0044/ADR-0027 및 다른 어떤 RFC/ADC/ADR도
  수정하지 않음 — `OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`
  §7 결론(신규 Governance 불필요)대로 진행.
- Production Code: `mvp/workflow_ast_context.py`(1줄) +
  `mvp/tests/test_engine_boundary.py`(분류/테스트 갱신) — 정확히
  이 2개 파일만 변경. Stage04 DAG, `identify_target()` 판단 로직,
  다른 Agent/Stage/Engine adapter는 전혀 변경하지 않음.

## Branch / Commit / PR 상태

- Branch: `claude/jarvis-openrouter-validation-bin9aj`
- 이전 HEAD: `40300a4`
- 본 Evidence 커밋 예정
- PR: 없음(사용자 명시적 요청 없음)

## Evidence 경로

`docs/research/OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md`(본 문서)

## 발견됐으나 이번 범위에서 고치지 않은 별개 문제(보고만 함)

`stages/05_validation/stage_05.py`의 `test_execution` 체크가
`sys.executable -m pytest`를 호출하는데, 이 샌드박스 환경의 기본
`python3`에는 pytest가 모듈로 설치돼 있지 않아 항상
`ModuleNotFoundError`로 실패한다. 이는 **OpenRouter Migration과 무관한
환경 구성 문제**이며, 임의로 범위를 넓혀 고치지 않았다(사용자 지시:
"문제가 발견되면 임의로 범위를 확대하지 말고 중단 후 보고한다"). 이
문제 때문에 Gate #12(전체 E2E 실제 통과)가 이 환경에서는 구조적으로
항상 FAIL로 나올 가능성이 있다 — 별도 세션에서 이 환경의 pytest 설치
경로를 사용자가 먼저 판단해야 한다.
