# DEV-HQ-V2.0 — Stage 05 Validation real Engine / real pytest E2E

## 목적

`stages/05_validation/VALIDATION.md`가 요구하는 real Engine/실제 pytest
E2E: Stage 04 Output이 Stage 05 Input으로 정상 소비되는지, Specification
Scope/Design Scope/Regression 검증이 실제로 동작하는지, PASS/FAIL/PARTIAL
판정이 명확한지 확인한다. 이번이 Stage 01→05 전체를 실제로 이어서
실행한 첫 사례다(Blind Issue 1건, 실제 파일명/함수명 미언급).

## 방법

```text
Title: Cap the number of listed files per category in context summaries
Description: When summarizing collected context for the requirement-
analysis prompt, each category's file list is currently included in
full, which can make the prompt very long for categories with many
matches. Limit each category's summary line to at most 2 file names,
with an indicator of how many more were omitted.
```

`run_stage_01()` → `run_stage_02()` → `run_stage_03()` →
`run_stage_04(expose_target=True)` → `run_stage_05()`을 순서대로
실제 실행했다(Stage 04 E2E와 동일한 Issue — 재현성 확인 겸용).

## 결과

- `target`: `("workflow_project_intelligence", "_summarize_context")` —
  실제 저장소 파일의 실제 함수(Stage 04 단독 E2E 때는 같은 Issue로
  `workflow_0009._render_context_bundle`이 식별됨 — Engine 응답의
  비결정성으로 다른 유효한 대상이 나올 수 있음을 확인, 둘 다 "context
  요약을 렌더링하는 함수"라는 점에서 Issue와 실제로 부합)
- `structural_check`: `{"valid": True, "engine_failed": False}`
- `specification_check`: `{"target_in_scope": True}` — Stage 02가 실제로
  이 파일을 Implementation Scope 후보로 잡았음을 확인
- `design_scope_check`: `{"scope_ok": True, "changed_names": []}` —
  AST 비교 결과 대상 함수 외 변경 없음
- `test_execution`: `{"executed": True, "returncode": 0}` — 대상 파일에
  실제로 적용한 뒤 저장소 전체 테스트 스위트 실행 → **98 passed**
  (기존 회귀 없음)
- `verdict`: **PASS**
- 실행 후 `git status --short` — Stage 05 신규 파일만 남고, 대상
  파일(`workflow_project_intelligence.py`)은 원상복구되어 변경 없음
  확인(`try`/`finally`가 실제로 동작함을 실증)

## 판정

**PASS(1건)** — Stage 04 Output이 Stage 05 Input으로 정상 소비됐고,
4개 결정적 검증(구조/Specification Scope/Design Scope/Test Execution)
전부 실행되어 전부 통과했으며, 판정 규칙이 정확히 `PASS`를 산출했다.
실제 파일 적용 → pytest 실행(98 passed) → 원상복구까지 전 과정이 코드로
자동화되어 동작함을 확인했다(이전까지는 이 절차를 세션 스크립트로
수동 수행했음 — 이번에 `stage_05.py`의 Capability로 formalize됨).

## Open Issues

- 표본 1건(Stage 01→05 전체 연쇄로는 이번이 처음) — 추가 재현은
  필요시 후속 세션에서 수행
- `code_review`(Capability 5) 내용 자체는 판정에 반영되지 않으므로
  이번 E2E 판정과 무관하게 별도 파일(`e2e_stage_05_code_review.txt`,
  세션 scratchpad)로만 보관
- FAIL/PARTIAL 경로의 real E2E는 아직 수행하지 않음(mock 단위
  테스트로만 확인) — 의도적으로 실패하는 Issue를 만들어 재현하는 것은
  이번 범위 밖
