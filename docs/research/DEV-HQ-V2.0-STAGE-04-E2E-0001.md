# DEV-HQ-V2.0 — Stage 04 Implementation real Engine E2E

## 목적

`stages/04_implementation/VALIDATION.md`가 요구하는 real Engine E2E:
Stage 03 Design이 Stage 04 Input으로 정상 소비되는지, Target
Identification이 실제 Repository 기준으로 정확한지, 생성된 Code가
실제 Production Code에 적용 가능하고 Scope를 벗어나지 않는지, 기존
테스트를 깨지 않는지 확인한다.

## 방법

Blind Issue(실제 파일명/함수명을 언급하지 않음, "기존 함수 1개 확장"
유형)로 `run_stage_01()` → `run_stage_02()` → `run_stage_03()` →
`run_stage_04(expose_target=True)`를 순서대로 실행했다.

```text
Title: Cap the number of listed files per category in context summaries
Description: When summarizing collected context for the requirement-
analysis prompt, each category's file list is currently included in
full, which can make the prompt very long for categories with many
matches. Limit each category's summary line to at most 2 file names,
with an indicator of how many more were omitted.
```

## 결과

- `target`: `("workflow_0009", "_render_context_bundle")` — 실제
  저장소 파일(`hqs/development/mvp/workflow_0009.py`)의 실제 함수.
  Issue 어디에도 파일명/함수명을 언급하지 않았음에도 정확히 식별됨
- `expose_target`: `True`
- `implementation`: 3,224자, `workflow_0009.py` 전체 내용(수정 포함)

### 실제 파일 적용 → pytest → diff → 원상복구

1. `workflow_0009.py` 원본을 백업
2. `implementation`을 그대로 덮어씀
3. `pytest hqs/development/mvp/tests/ -q` → **75 passed**(기존 테스트
   전부 통과 — `_render_context_bundle`을 사용하는 기존 호출부와
   호환)
4. 원본과 diff — 변경은 정확히 `_render_context_bundle` 함수 내부
   (내부 헬퍼 `_capped_list_or_none` 추가 + 5개 호출 지점을 새 헬퍼로
   치환)로 국한됨. 다른 함수(`_enrich_issue_with_bundle`,
   `run_issue_to_planning_with_bundle`, `run_comparison`)와 import는
   변경 없음. 파일 끝 개행 문자 유무만 부가적으로 달라짐(내용
   변경 아님)
5. 백업본으로 원상복구, `git status --short`로 저장소에 잔여 변경이
   `workflow_0009.py` 관련해서는 없음을 확인(Stage 04 문서/코드
   파일만 남음)

## 판정

**PASS(1건)** — Stage 03 Design이 Stage 04 Input으로 정상 소비됐고,
Target Identification이 실제 존재하는 함수를 정확히 가리켰으며, 생성된
Code가 실제 Production Code에 적용 가능했고(pytest 75 passed), Scope를
벗어나지 않았다(대상 함수 1개만 변경). ADC-0005 §8 E2E(1건)에 이어
누적 Scope 준수 4/4.

## Open Issues

- 표본 1건(이 Stage 기준) — 누적으로는 T06~T19 + ADC-0005 §8 + 이번
  건까지 4/4
- `expose_target=False` 경로(부분 코드만 반환하는 모드)는 이번 E2E에서
  실행하지 않음 — 단위 테스트(mock)로만 조립 로직을 확인함
- `target`이 `None`인 경우(식별 실패 폴백)의 real Engine 동작도 이번
  E2E에서는 실행하지 않음(mock으로만 확인)
