# Stage 01: Responsibility

## 책임진다

- Repository 구조(디렉토리/파일 트리) 분석
- Issue와 관련된 파일/문서 탐색(코드, RFC/ADC/ADR/OBS/RT 문서 포함)
- 탐색 결과를 후속 Stage가 바로 쓸 수 있는 구조(Context Bundle)로 재배치
- 저장소 함수 후보를 이름+시그니처+docstring 첫 줄로 색인화(AST Function
  Candidate Index)
- 특정 함수의 직접·간접 의존성만 추출(AST Dependency Closure)
- PRD/Specification 생성 — Structured Understanding(Multi-Agent
  Reasoning 결과)과 Repository Context(Code Analysis 결과)를 종합해
  기존 Requirement Agent를 재사용, PRD/Specification을 산출한다
  (`prd_synthesis.py`, RFC-0034/ADC-0037/ADR-0022 — 이전에는 Stage 02
  책임이었다)

## 책임지지 않는다

- Design 산출(→ Stage 03 Architecture & Design)
- Task Decomposition/Dependency Ordering/Acceptance Criteria 정교화/
  Implementation Planning(→ Stage 02 Planning — PRD/Specification
  생성만 Stage 01로 이동했고, 이 책임들은 여전히 Stage 02 소관이다)
- 코드 생성/수정(→ Stage 04 Implementation)
- 코드 리뷰/테스트 실행(→ Stage 05 Validation)
- AST 폐쇄 시작점(target module/function) 자동 식별 — Design 산출물이
  필요해 Stage 03 이후에만 가능(`workflow_ast_context.identify_target`
  이미 구현). Stage 01은 시작점이 **주어졌을 때**만 폐쇄를 계산한다.
- Engine 호출의 routing·provider 선택·policy 판정 — Stage 01은 Multi-Agent
  Reasoning(Intent/Goal/Requirement/Ambiguity Agent)을 orchestrate하지만,
  각 Agent의 실제 LLM 실행은 다른 Stage의 Agent와 동일하게 기존 Engine
  Adapter 경계(`mvp/omniroute_engine.py::call_engine_via_omniroute`)를
  그대로 따른다 — 새 Engine Gateway/Routing/Policy를 두지 않는다
  (`RFC-0033`/`ADC-0036`/`ADR-0021`). Repository Structure/Relevant
  Discovery/AST Candidate Index/Dependency Closure 4개 Code Analysis
  Capability는 계속 Engine을 호출하지 않는 결정적 분석으로 남는다.

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음. Multi-Agent Reasoning 도입(`RFC-0033`/`ADC-0036`/`ADR-0021`)은
Development HQ 내부 Scoped 결정이며, Kernel Public Contract·Development
HQ Baseline v1.0(Stage Data Contract)을 변경하지 않는다. `ADC-0005`의
"Architecture Impact: NONE"은 4개 결정적 Code Analysis Capability에는
그대로 적용되고, Reasoning 단계는 위 3개 문서가 별도로 판단했다.
