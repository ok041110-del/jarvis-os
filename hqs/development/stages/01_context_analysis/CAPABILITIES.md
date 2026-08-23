# Stage 01: Capabilities

5개 모두 기존 `hqs/development/mvp/` 함수를 그대로 재사용한다 — 신규
구현이나 신규 Capability 등록(`AGENT_CAPABILITY_MAP`)이 아니다
(ADR-0008 §4, 이 Stage는 필요성이 확인되지 않아 신규 Capability를
추가하지 않았다).

## 1. Repository Structure Analysis

| 항목 | 내용 |
|---|---|
| Input | 없음(저장소 고정 경로: `hqs/development`, `docs`) |
| Analysis | `project_intelligence._directory_structure()` — `max_depth=2`까지 디렉토리/파일 트리를 나열, `__pycache__` 등 noise 제외 |
| Output | 상대 경로 문자열 목록 |
| Validation | `project_intelligence.collect_relevant_context()`의 `"directory_structure"` 키를 통해 기존 36개 테스트(mock 기반)가 간접 검증. 실제 파일시스템 동작 자체는 `DEV-HQ-V2.0-CATEGORY-PATHS-BLIND-SPOT-REVIEW-0001.md`(T07)가 수동 확인 |

## 2. Relevant File / Document Discovery

| 항목 | 내용 |
|---|---|
| Input | `issue: dict`(`title`, `description` 필수) |
| Analysis | `project_intelligence.collect_relevant_context()` — 키워드 추출 → 8개 카테고리(`source_code`, `existing_workflow`, `mvp_documents`, `obs_documents`, `rfc_documents`, `adc_documents`, `adr_documents`, `rt_documents`) 각각 단어 경계 매칭 점수로 상위 3개 파일 선정 |
| Output | `dict`(카테고리별 상대 경로 목록 + `directory_structure`) |
| Validation | `validate_issue()`가 입력을 선검증. 기존 `test_workflow_0008.py` 등 다수 테스트가 mock으로 계약(반환 키 집합)을 고정 |

## 3. Project Context Analysis

| 항목 | 내용 |
|---|---|
| Input | `issue: dict` |
| Analysis | `project_intelligence.build_context_bundle()` — Discovery(2번) 결과를 Planning이 바로 쓸 8개 필드(`relevant_documents`, `relevant_code`, `relevant_observations`, `relevant_decisions`, `known_constraints`, `open_questions` 등)로 재배치, `_extract_open_questions()`로 "미해결"/"검토가 필요" 마커 최대 5개 추출 |
| Output | `dict`(8개 키, Planning Capability 입력 형태) |
| Validation | 기존 `test_workflow_project_intelligence.py`가 `_summarize_context`/`_enrich_issue` 경로를 검증 |

## 4. AST Function Candidate Index

| 항목 | 내용 |
|---|---|
| Input | 없음(저장소 고정 경로 `hqs/development/mvp/*.py`) |
| Analysis | `ast_context.build_function_candidate_index()` — 각 파일의 top-level 함수/클래스를 `ast.parse`로 순회, 시그니처(본문 제외) + docstring 첫 줄만 추출 |
| Output | `"FILE: ...\nFUNCTION/CLASS: ..."` 형태의 문자열(본문 없음) |
| Validation | `test_ast_context.py::test_candidate_index_*` 3건 — 알려진 함수/클래스 존재, 본문 미포함, 실제 시그니처 일치를 확인. Evidence: `DEV-HQ-V2.0-AST-CANDIDATE-INDEX-REPRODUCTION-0001.md`(시작점 식별 3/3) |

## 5. AST Dependency Closure

| 항목 | 내용 |
|---|---|
| Input | `module: str`, `function: str`(시작점 — Stage 01은 이 값을 스스로 식별하지 않는다, `RESPONSIBILITY.md` 참고) |
| Analysis | `ast_context.build_dependency_closure()` — Load-context 이름 추적 + 상대 import 재귀로 직접·간접 의존 함수/클래스만 폐쇄로 수집 |
| Output | 모듈별로 그룹화된 소스 코드 발췌 문자열(`# module: <name>` 헤더) |
| Validation | `test_ast_context.py::test_closure_*` 5건 — 단일/다중 모듈 폐쇄, T18 Evidence의 5-모듈 재현, 미존재 대상 예외. 실제 Build E2E: `DEV-HQ-V2.0-ADC-0005-WORKFLOW-INTEGRATION-E2E-0001.md`(real Engine, Scope 준수 3/3 누적) |
