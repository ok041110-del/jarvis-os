# Stage 03: Capabilities

2개 Capability로 9개 관점(Architecture Definition/Component
Identification/Responsibility Allocation/Interface·Contract
Identification/Data Flow/Dependency·Boundary Definition/Implementation
Strategy/Design Constraints/Design Risks)을 모두 다룬다 — 신규
Capability나 신규 Engine 호출을 추가하지 않는다(`RESPONSIBILITY.md`
참고).

## 1. Design Skeleton 추출 (Engine 미호출)

| 항목 | 내용 |
|---|---|
| Input | `issue: dict`, Stage 01 Output(`run_stage_01()` 반환 dict, 특히 `candidate_index`), Stage 02 Output(`run_stage_02()` 반환 dict, 특히 `skeleton`) |
| Analysis | `stage_03._structure_from_specification()` — Stage 01의 `candidate_index`(함수/클래스 시그니처 색인)를 Component Candidates로, Stage 02 `skeleton`의 `scope_candidates`를 Dependency/Boundary 후보로, `constraints`/`risks`를 그대로 Design Constraints/Risks 입력으로 재배치한다. 새 AST 분석/Requirement 재해석을 하지 않는다 — Stage 01/02가 이미 만든 결과만 재배치 |
| Output | `dict`(`component_candidates`, `scope_candidates`, `constraints`, `risks` 4개 키) |
| Validation | 순수 함수 — `test_stage_03.py`에서 결정적 입출력을 직접 단위 테스트 |

## 2. Architecture / Design 생성 (Engine 재사용)

| 항목 | 내용 |
|---|---|
| Input | `issue: dict`, Stage 02 `specification`, Capability 1의 골격 `dict` |
| Analysis | 골격을 텍스트로 직렬화(`_skeleton_to_text`)해 Stage 02 `specification`에 덧붙이고(Stage 02가 Stage 01 Context를 Issue description에 붙인 것과 동일한 "결합 후 기존 Capability에 전달" 패턴), Architecture Definition/Component Identification/Responsibility Allocation/Interface·Contract Identification/Data Flow/Implementation Strategy를 추가로 서술하라는 지시문을 함께 붙여 **기존** `agents.design.design_agent_design(issue, requirement)`를 그대로 호출한다(`specification` + 골격을 `requirement` 인자로 전달). Capability 자체나 그 내부 지시문(`agents/design.py`)은 수정하지 않는다 |
| Output | `str`(Component/Dependency/Constraints/Risks 골격을 반영하고 나머지 6개 관점을 포함한 Design 프로즈) |
| Validation | Stage 02와 동일하게 mock 기반 단위 테스트로 (a) 골격과 Specification이 실제로 `design_agent_design`의 `requirement` 인자에 포함되는지, (b) Engine 실패 시 기존 오류 포맷(`_engine_failure_message`)을 유지하는지 확인. 추가로 real Engine E2E 1건으로 Stage 01/02 Context가 실제로 Design에 반영되는지 확인(`VALIDATION.md`) |
