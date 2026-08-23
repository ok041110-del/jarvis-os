# DEV-HQ-V2.0 — Stage 02 Planning & Specification real Engine E2E

## 목적

`stages/02_planning_specification/VALIDATION.md`가 요구하는 real Engine
E2E: Stage 01 Context(특히 `scope_candidates`/`risks`)가 Stage 02의
Specification 생성에 실제로 반영되는지 확인한다.

## 방법

Blind Issue(실제 파일명/함수명을 언급하지 않음)로 `run_stage_01()` →
`run_stage_02()`를 순서대로 실행했다.

```text
Title: Limit dependency closure recursion depth
Description: The static-analysis dependency closure walker currently
recurses through relative imports without a configurable limit. Add a
way to cap how deep the closure recursion goes so it cannot run away on
deeply nested modules.
```

## 결과

`skeleton`(Engine 미호출, Stage 01 Context 결정적 재배치):

- `scope_candidates`: `hqs/development/mvp/ast_context.py`,
  `hqs/development/mvp/agents.py`, `hqs/development/mvp/workflow_ast_context.py`
- `risks`: `docs/architecture/core/RFC-0012-dispatch-component-boundary.md`의
  Open Question 5건
- `constraints`: 없음(매칭되는 RT 문서 없음 — 정상, 이 Issue와 무관)

`specification`(Engine 산출, 위 골격 + Task Decomposition/Acceptance
Criteria 지시 반영):

- Implementation Scope Candidates 절이 `skeleton["scope_candidates"]`의
  3개 파일을 정확히 그대로 나열
- Risks 절이 `skeleton["risks"]`의 RFC-0012 Open Question 내용을 실제로
  해석해 서술(단순 복사가 아니라 "depth-limit 배치가 ADC-0008~0011과
  충돌할 수 있다"는 식으로 문맥화)
- Task Decomposition 7단계, Acceptance Criteria 6개 항목을 지시대로
  추가 생성(골격에는 없던 항목 — Engine이 새로 도출)

## 판정

**PASS(1건)** — Stage 01 Context가 Stage 02 Specification에 실제로
반영됨을 확인했다. Skeleton의 결정적 필드(`scope_candidates`)가
Specification에 정확히 재현됐고, 비결정적 필드(`risks`)도 원문을
그대로 복붙하지 않고 실제로 해석·서술했다.

## Open Issues

- 표본 1건 — 추가 재현은 필요시 후속 세션에서 수행
- `constraints`가 매칭되지 않는 경우의 Specification 품질(빈 값일 때
  Engine이 이를 어떻게 서술하는지)은 이번 E2E에서 확인하지 못함(이번
  Issue는 우연히 빈 값이었음)
- 코드 파일을 수정하지 않는 산출물이라 backup/apply/revert 절차 불필요
  (Stage 04 E2E와의 차이점, `VALIDATION.md`에 이미 기록)
