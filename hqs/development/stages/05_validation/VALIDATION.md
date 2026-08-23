# Stage 05: Validation Output 스키마 / 검증 방법

## Output 스키마

`run_stage_05(issue, stage_02_output, stage_03_output, stage_04_output)`
이 반환하는 `dict`의 키 6개. 이전 Stage처럼 새 Contract를 만들지 않고,
각 Capability의 결과를 그대로 재노출한다.

| 키 | 타입 | 생성 Capability |
|---|---|---|
| `structural_check` | `dict`(`valid: bool`, `engine_failed: bool`) | Implementation Result Validation |
| `specification_check` | `dict`(`target_in_scope: bool \| None`) | Requirement/Specification Validation |
| `design_scope_check` | `dict`(`scope_ok: bool \| None`, `changed_names: list[str]`) | Design/Scope Validation |
| `test_execution` | `dict`(`executed: bool`, `returncode: int \| None`, `output: str`) | Test Execution/Regression Detection |
| `code_review` | `str` | Code Review Evidence(Engine 재사용, 보조 Evidence) |
| `verdict` | `"PASS" \| "FAIL" \| "PARTIAL"` | Validation Result |

이 dict 전체가 Evidence다 — 각 하위 키가 Evidence Collection
Capability의 산출물이며, 별도의 "evidence" 래퍼 키를 추가하지 않았다
(Stage 01~04와 동일하게 새 Contract를 만들지 않는 원칙).

## Stage 03 Design을 이 Stage가 직접 소비하지 않는 이유

`stage_03_output`은 함수 시그니처에는 있지만(향후 `workflow.py`가 5개
Stage를 동일 패턴으로 연결하기 위함), 6개 Capability는 Stage 03
`design` 텍스트를 읽지 않는다 — AST Scope 검증은 실제 코드(Stage 04
`implementation`)와 변경 전 파일만 비교하면 충분하며, Design 프로즈를
Engine으로 재해석하지 않는 이유는 Policy 구현 금지 근거와 같다.

## 검증 원칙

Capability 1~4, 6은 순수 함수/subprocess라 mock 없이 결정적으로 단위
테스트한다. Capability 5는 기존 `backend_agent_code_review()`를
재사용하므로 그 자체 동작은 기존 테스트가 이미 검증했다 — 여기서는
`implementation`이 실제로 전달되는지, Engine 실패 시 기존 오류 포맷을
유지하는지만 mock으로 확인한다.

## 테스트 위치

`hqs/development/mvp/tests/test_stage_05.py` — 이전 Stage와 동일하게
Stage 폴더 하위가 아닌 기존 공통 `tests/` 위치를 쓴다(ADR-0008 §1).

## 검증 항목

| 항목 | 방법 |
|---|---|
| 구조 검사가 Engine 실패를 정확히 탐지 | `implementation`이 오류 포맷일 때/아닐 때 단위 테스트 |
| Specification Scope Membership이 정확히 판정 | `scope_candidates`에 포함/불포함/target 없음 3가지 단위 테스트 |
| AST Scope 검사가 Target 외 변경을 정확히 탐지 | `tmp_path`에 원본/변경본을 만들어 Scope 준수·위반 2가지 단위 테스트 |
| pytest 실행이 반드시 원상복구되는지 | 테스트 실행 도중 예외가 나도(`finally`) 원본 파일 내용이 보존되는지 확인 |
| Code Review가 실제 `implementation`을 받는지 | mock으로 전달 인자 확인 |
| 6가지 PASS/FAIL/PARTIAL 판정 경로 | `_determine_verdict()`를 각 조합(Engine 실패/pytest 실패/Scope 위반/일부 미실행/전부 통과)으로 단위 테스트 |
| Stage 04 Output이 Stage 05 Input으로 정상 소비 | `run_stage_05()` 통합 테스트(mock) |

## real Engine E2E (real pytest 실행 포함)

Stage 04 real Engine E2E(`DEV-HQ-V2.0-STAGE-04-E2E-0001.md`)에서 만든
실제 `target`/`implementation`을 그대로 Stage 05 Input으로 사용해:

1. Stage 01 → 02 → 03 → 04를 실제 실행(`expose_target=True`)한 뒤,
   그 Output으로 `run_stage_05()`를 실제 실행한다.
2. `specification_check.target_in_scope`가 `True`인지 확인한다(Stage
   02가 실제로 그 파일을 Scope 후보로 잡았는지).
3. `design_scope_check.scope_ok`가 `True`이고 `changed_names`가
   Target 함수 하나뿐인지 확인한다.
4. `test_execution.executed`가 `True`이고 `returncode == 0`인지
   확인한다(저장소 전체 테스트 스위트가 실제로 통과하는지).
5. 실행 후 `git status --short`로 대상 파일이 원상복구됐는지 확인한다.
6. `verdict`가 `PASS`인지 확인한다.
7. 결과를 이 Stage의 최종 보고(세션 기록)에 남긴다 — 이 문서는
   방법론만 고정하고 특정 시점의 결과를 반복 기록하지 않는다.
