# Stage 01: Responsibility

## 책임진다

- Repository 구조(디렉토리/파일 트리) 분석
- Issue와 관련된 파일/문서 탐색(코드, RFC/ADC/ADR/OBS/RT 문서 포함)
- 탐색 결과를 후속 Stage가 바로 쓸 수 있는 구조(Context Bundle)로 재배치
- 저장소 함수 후보를 이름+시그니처+docstring 첫 줄로 색인화(AST Function
  Candidate Index)
- 특정 함수의 직접·간접 의존성만 추출(AST Dependency Closure)

## 책임지지 않는다

- Requirement 분석, Design 산출(→ Stage 02 Planning & Specification,
  Stage 03 Architecture & Design)
- 코드 생성/수정(→ Stage 04 Implementation)
- 코드 리뷰/테스트 실행(→ Stage 05 Validation)
- AST 폐쇄 시작점(target module/function) 자동 식별 — Design 산출물이
  필요해 Stage 03 이후에만 가능(`workflow_ast_context.identify_target`
  이미 구현). Stage 01은 시작점이 **주어졌을 때**만 폐쇄를 계산한다.
- Engine 호출 — 5개 Capability 전부 순수 정적 분석/파일 탐색이며
  Engine을 호출하지 않는다(결정적 Input→Output의 근거).

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음(ADC-0005 Architecture Impact: NONE 그대로 적용, 5개 Capability
모두 ADC-0005 Accept 범위 + 기존 MVP-0005 재배치).
