# Stage 05: Capabilities

6개 Capability. Engine을 호출하는 것은 5번(Code Review Evidence)
1개뿐이며 기존 Capability를 그대로 재사용한다 — 신규 Capability/Agent를
추가하지 않는다(`RESPONSIBILITY.md` 참고).

## 1. Implementation Result Validation (Structural Check)

| 항목 | 내용 |
|---|---|
| Input | Stage 04 Output(`run_stage_04()` 반환 dict) |
| Validation | `stage_05._check_structural()` — `target`/`implementation`/`expose_target` 3개 키가 모두 존재하는지, `implementation`이 `workflow._engine_failure_message()` 형식("Engine call failed: ...")으로 시작하는지 확인 |
| Output | `dict`(`valid: bool`, `engine_failed: bool`) |
| Evidence | 검사 자체가 결정적이므로 반환 값 자체가 Evidence — `test_stage_05.py`에서 정상/Engine 실패 2가지 케이스로 단위 테스트 |

## 2. Requirement / Specification Validation (Scope Membership)

| 항목 | 내용 |
|---|---|
| Input | Stage 04 `target`, Stage 02 Output(`skeleton.scope_candidates`) |
| Validation | `stage_05._check_specification_scope()` — `target`이 있으면 `ast_context.module_source_path(module)`로 실제 파일 경로를 구해, 그 경로가 Stage 02 `scope_candidates`(Implementation Scope 후보 목록)에 포함되는지 확인. Target이 없으면 판정 보류(`None`) |
| Output | `dict`(`target_in_scope: bool \| None`) |
| Evidence | 비교에 사용한 경로 문자열 자체가 Evidence — `test_stage_05.py`에서 포함/불포함/target 없음 3가지 케이스로 단위 테스트 |

## 3. Design / Scope Validation (AST Diff)

| 항목 | 내용 |
|---|---|
| Input | Stage 04 `target`, `expose_target`, `implementation` |
| Validation | `stage_05._check_design_scope()` — `target`이 있고 `expose_target=True`일 때만 실행. 대상 파일의 **현재(변경 전) 내용**과 `implementation`을 각각 `ast.parse`해 top-level 함수/클래스 이름 집합과 `ast.get_source_segment()`를 비교, Target 함수를 제외한 나머지가 전부 동일한 소스인지 확인(`ast_context.py`의 기존 AST 비교 패턴 재사용, 새 알고리즘 도입 아님). Target이 없거나 `expose_target=False`이면 판정 보류(`None`) — 부분 코드만으로는 비교 기준(전체 파일)이 없기 때문 |
| Output | `dict`(`scope_ok: bool \| None`, `changed_names: list[str]`) |
| Evidence | `changed_names`(Target 외에 실제로 달라진 함수/클래스 이름 목록)가 Evidence — `test_stage_05.py`에서 Scope 준수/위반/판정 보류 3가지 케이스로 단위 테스트 |

## 4. Test Execution / Regression Detection

| 항목 | 내용 |
|---|---|
| Input | Stage 04 `target`, `expose_target`, `implementation` |
| Validation | `stage_05._run_pytest_with_applied_implementation()` — `target`이 있고 `expose_target=True`일 때만 실행. 대상 파일을 백업 → `implementation`으로 덮어씀 → `pytest hqs/development/mvp/tests/ -q`를 subprocess로 실행 → **`try`/`finally`로 반드시 원상복구**(Stage 04 real Engine E2E, `DEV-HQ-V2.0-STAGE-04-E2E-0001.md`가 수동으로 수행한 절차를 코드로 formalize). Target이 없거나 `expose_target=False`이면 실행하지 않음(`executed: False`) |
| Output | `dict`(`executed: bool`, `returncode: int \| None`, `output: str`) |
| Evidence | `output`(pytest 표준 출력) 전체가 Evidence — `test_stage_05.py`에서 `tmp_path` 기반 가짜 모듈로 실행/미실행 케이스를 단위 테스트, real Engine E2E에서 실제 저장소 테스트 스위트로 재확인 |

## 5. Code Review Evidence (Engine 재사용)

| 항목 | 내용 |
|---|---|
| Input | Stage 04 `implementation` |
| Validation | `agents.backend_agent_code_review(implementation)` — 기존 Backend Agent code_review Capability(MVP-0001)를 그대로 호출. 판정에는 반영하지 않고 사람이 읽는 보조 Evidence로만 반환(`RESPONSIBILITY.md`) |
| Output | `str`(리뷰 프로즈) |
| Evidence | 반환 값 자체가 Evidence — Engine 실패 시 기존 오류 포맷 유지 여부를 mock으로 확인 |

## 6. Validation Result (PASS / FAIL / PARTIAL)

| 항목 | 내용 |
|---|---|
| Input | Capability 1~4의 결과 |
| Validation | `stage_05._determine_verdict()` — 결정적 규칙(Engine 미호출, Policy 구현 금지 준수): Engine 실패/pytest 실패/AST Scope 위반 확정 → `FAIL`. 일부 검증 미실행/미확정 → `PARTIAL`. 전부 실행·통과 → `PASS` |
| Output | `"PASS" \| "FAIL" \| "PARTIAL"` |
| Evidence | 판정 자체가 Capability 1~4 Evidence의 함수이므로 별도 Evidence 없음 — `test_stage_05.py`에서 PASS/FAIL/PARTIAL 각 경로를 명시적으로 단위 테스트 |
