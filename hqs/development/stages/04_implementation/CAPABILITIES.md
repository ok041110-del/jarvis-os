# Stage 04: Capabilities

3개 Capability 전부 `workflow_ast_context.py`/`agents/`의 기존 함수를
그대로 재사용한다 — 신규 Capability나 신규 Engine 호출을 추가하지
않는다(`RESPONSIBILITY.md` 참고). Stage 04 고유 코드는 이 3개를
Stage 03 Design에 연결하는 조립 로직뿐이다.

## 1. Target Identification (Engine 재사용)

| 항목 | 내용 |
|---|---|
| Input | Stage 03 `design: str` |
| Analysis | `workflow_ast_context.identify_target(design)` — AST Function Candidate Index + Design으로 시작점(module, function)을 식별한다. T17~T19에서 3/3 재현된 기존 구현(RFC-0007 §2) |
| Output | `tuple[str, str] \| None`(식별 실패 시 `None`) |
| Validation | 기존 `test_workflow_ast_context.py`가 `identify_target` 자체를 이미 검증(정상 파싱 2건, UNKNOWN → `None` 1건). Stage 04에서는 Stage 03 `design`을 실제로 이 함수에 넘기는지만 mock으로 추가 확인 |

## 2. Dependency Closure & Exposure 조립 (Engine 미호출)

| 항목 | 내용 |
|---|---|
| Input | Capability 1의 `target`, `expose_target: bool` |
| Analysis | `ast_context.build_dependency_closure(module, function)`로 폐쇄를 계산해 `design`에 concatenate하고, `expose_target=True`이면 `ast_context.module_source_path(module)`로 대상 파일 전체를 읽어 `workflow_ast_context._EXPOSURE_POLICY_INSTRUCTION`(Target 함수만 확장, 그 외 변경 금지)과 함께 추가한다 — `workflow_ast_context.run_pipeline_with_ast_context()`의 조립 로직(ADC-0005 §7/§8)과 동일한 순서를 그대로 재현한다. 이미 검증된 그 함수 자체는 수정하지 않고, Stage 04가 별도로 동일 조립을 수행한다(RESPONSIBILITY.md: `workflow_ast_context.py`를 건드리지 않기 위한 선택) |
| Output | `str`(Build Capability에 넘길 최종 입력) |
| Validation | 순수 함수 조립 — `test_stage_04.py`에서 target 있음/없음, exposure 켬/끔 4가지 조합을 결정적으로 단위 테스트 |

## 3. Code Generation (Engine 재사용)

| 항목 | 내용 |
|---|---|
| Input | Capability 2의 Build 입력 `str` |
| Analysis | `agents.backend.backend_agent_code_generation(build_input)` — 기존 Backend Agent code_generation Capability를 그대로 호출(코드만 반환하도록 지시, 마크다운 fence 제거 포함) |
| Output | `str`(생성/수정된 코드 — Exposure 시 파일 전체, 아니면 부분 코드) |
| Validation | 기존 테스트가 `backend_agent_code_generation` 자체를 이미 검증. Stage 04에서는 (a) Engine 실패 시 기존 오류 포맷 유지, (b) real Engine E2E로 실제 파일에 적용 → pytest 실행 → Scope 준수(대상 함수만 변경) 확인 → 원상복구(`VALIDATION.md` 참고) |
