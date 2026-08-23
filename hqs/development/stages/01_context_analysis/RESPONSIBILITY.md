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
- "AST 폐쇄의 시작점(target module/function)을 Design으로부터
  자동 식별"하는 것 — 이는 Design 산출물을 입력으로 요구하므로
  Stage 03 이후에만 가능하다. Stage 01은 시작점이 **주어졌을 때**
  AST Dependency Closure를 계산하는 능력만 제공한다
  (`workflow_ast_context.identify_target`이 이미 이 식별을 수행하며,
  Stage 01은 그 식별 로직 자체를 담당하지 않는다).
- Engine 호출 — Stage 01의 5개 Capability는 전부 순수 정적 분석/파일
  탐색이며 Engine을 호출하지 않는다(`RESPONSIBILITY.md`가 이 Stage의
  결정적 Input→Output 특성을 보장하는 근거).

## Kernel/Architecture 경계

Stage 01은 Development HQ MVP Implementation 범위이며, Jarvis OS
Kernel Architecture나 Development HQ Baseline을 변경하지 않는다
(ADC-0005 §Architecture Impact: NONE이 이 Stage에도 그대로 적용됨 —
Stage 01의 5개 Capability는 ADC-0005가 이미 Accept한 것과 기존
MVP-0005 범위의 재배치일 뿐이다).
