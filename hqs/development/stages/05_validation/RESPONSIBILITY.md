# Stage 05: Responsibility

## 책임진다

- Stage 04 Output이 Contract(`IMPLEMENTATION.md`)를 satisfy하는지 구조적
  확인(Implementation Result Validation)
- Target 함수가 Stage 02 `scope_candidates`(Implementation Scope 후보)에
  포함되는지 확인(Requirement/Specification Validation)
- Target File Exposure가 적용된 경우, 변경이 대상 함수 1개로 국한되는지
  AST 비교로 확인(Design/Scope Validation)
- 실제 `pytest`를 실행해 회귀 여부를 확인 — 대상 파일에 Implementation을
  임시로 적용하고, 실행 후 반드시 원상복구한다(Test Execution /
  Regression Detection)
- 위 4가지 검증 결과 + 기존 `backend_agent_code_review()` 재사용
  결과를 구조화된 Evidence로 반환(Evidence Collection)
- 위 Evidence로부터 PASS/FAIL/PARTIAL 판정을 결정적 규칙으로
  산출(Validation Result)

## 책임지지 않는다

- 발견된 문제를 직접 수정 — Stage 04 Implementation이나 대상 파일을
  영구적으로 변경하지 않는다. 검증 중 임시로 적용한 변경은 검증 직후
  반드시 원상복구한다(`try`/`finally`로 보장)
- Context 수집, Specification/Design/Implementation 생성(→ Stage
  01~04. 이 Stage는 그 Output들을 그대로 Input으로 받을 뿐, 다시
  생성하지 않는다)
- Specification/Design과의 의미적(semantic) 일치를 Engine에 판정시키는
  것 — `IMPLEMENTATION_RULES.md` "Policy 구현 금지" 원칙에 따라, 결정적
  대리 지표(Scope 후보 포함 여부, AST 변경 범위)로만 검증한다.
  `backend_agent_code_review()` 결과는 보조 Evidence일 뿐 판정에 직접
  반영하지 않는다
- 신규 Capability/Agent 추가 — 6개 중 Engine을 호출하는 것은
  `backend_agent_code_review()` 1개뿐이며 기존 Capability(MVP-0001)를
  그대로 재사용한다(`IMPLEMENTATION_RULES.md`, ADR-0008 §4 충족)
- 01→05 통합 Workflow 작성 — 이번 단계에서는 Stage 05 자체만 완성한다

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음, 새 Interface/Contract 미추가, `agents/`/`engine.py`/
`ast_context.py` 무수정.
