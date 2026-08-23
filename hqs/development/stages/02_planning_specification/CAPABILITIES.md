# Stage 02: Capabilities

2개 Capability로 7개 관점(Problem Definition/Requirement Analysis/Task
Decomposition/Constraints/Risk/Acceptance Criteria/Implementation Scope)을
모두 다룬다 — 신규 Capability나 신규 Engine 호출을 추가하지 않는다
(`RESPONSIBILITY.md` 참고).

## 1. Specification Skeleton 추출 (Engine 미호출)

| 항목 | 내용 |
|---|---|
| Input | `issue: dict`, Stage 01 Output(`run_stage_01()` 반환 dict, 특히 `context_bundle`) |
| Analysis | `stage_02._structure_from_context()` — `context_bundle["known_constraints"]`를 Constraints로, `context_bundle["open_questions"]`를 Risk로, `context_bundle["relevant_code"]`를 Implementation Scope 후보로, `issue`를 Problem Definition으로 그대로 재배치한다. 새 파일 탐색/AST 분석을 하지 않는다 — Stage 01이 이미 만든 결과만 재배치 |
| Output | `dict`(`problem_definition`, `constraints`, `risks`, `scope_candidates` 4개 키) |
| Validation | 순수 함수 — `test_stage_02.py`에서 결정적 입출력을 직접 단위 테스트 |

## 2. Requirement & Specification 생성 (Engine 재사용)

| 항목 | 내용 |
|---|---|
| Input | `issue: dict`, Capability 1의 골격 `dict` |
| Analysis | 골격을 텍스트로 직렬화(`_skeleton_to_text`)해 Issue `description`에 덧붙이고(`workflow_project_intelligence._enrich_issue`와 동일한 "Issue description에 concatenate" 패턴), Task Decomposition/Acceptance Criteria를 추가로 서술하라는 지시문을 함께 붙여 **기존** `agents.requirements_agent_requirement_analysis(issue)`를 그대로 호출한다. Capability 자체나 그 내부 지시문(`agents.py`)은 수정하지 않는다 |
| Output | `str`(Problem Definition/Constraints/Risk/Implementation Scope 골격을 반영하고 Task Decomposition/Acceptance Criteria를 포함한 Specification 프로즈) |
| Validation | 기존 패턴(`workflow_project_intelligence.py`)과 동일하게 mock 기반 단위 테스트로 (a) 골격이 Issue description에 실제로 포함되는지, (b) Engine 실패 시 기존 오류 포맷(`_engine_failure_message`)을 유지하는지 확인. 추가로 real Engine E2E 1건으로 Stage 01 Context가 실제로 Specification에 반영되는지 확인(`VALIDATION.md`) |
