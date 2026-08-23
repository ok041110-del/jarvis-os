# DEV-HQ-V2.0 — Stage 03 Architecture / Design real Engine E2E

## 목적

`stages/03_architecture_design/VALIDATION.md`가 요구하는 real Engine
E2E: Stage 01 Context와 Stage 02 Specification이 Stage 03의 Design
생성에 실제로 반영되는지, `design`이 9개 관점을 실제로 포함하는지 확인한다.

## 방법

Blind Issue(실제 파일명/함수명을 언급하지 않음)로 `run_stage_01()` →
`run_stage_02()` → `run_stage_03()`을 순서대로 실행했다(Stage 02 E2E
`DEV-HQ-V2.0-STAGE-02-E2E-0001.md`와 동일한 Issue — Stage 02 산출물이
Stage 03 Input으로 실제 소비되는 흐름을 그대로 이어서 검증).

```text
Title: Limit dependency closure recursion depth
Description: The static-analysis dependency closure walker currently
recurses through relative imports without a configurable limit. Add a
way to cap how deep the closure recursion goes so it cannot run away on
deeply nested modules.
```

## 결과

`skeleton`(Engine 미호출, Stage 01/02 Output 결정적 재배치):

- `component_candidates`: Stage 01 `candidate_index`(저장소 전체 함수/
  클래스 색인) 그대로
- `scope_candidates`: `ast_context.py`, `agents.py`,
  `workflow_ast_context.py`(Stage 02 `skeleton`과 동일 — 재사용 확인)
- `constraints`: 없음, `risks`: RFC-0012 Open Question 5건(Stage 02
  `skeleton`과 동일)

`design`(Engine 산출, 위 골격 + Stage 02 `specification` + 9개 관점
지시 반영) — 9개 관점 전부 실제로 포함됨을 확인:

| 관점 | 확인 |
|---|---|
| Architecture Definition | "## Architecture Definition" 절 존재, 3개 컴포넌트의 역할 분리(단일 enforcement point, 2개 propagation point) 서술 |
| Component Identification | "## Component Identification" 절, `scope_candidates`의 3개 파일을 정확히 그대로 나열하고 각각의 책임 서술 |
| Responsibility Allocation | "## Responsibility Allocation" 절, 표 형태로 7개 관심사 대 소유 컴포넌트 매핑 |
| Interface / Contract Identification | "## Interface / Contract Identification" 절, 기존 `build_dependency_closure(module, function) -> str` 시그니처를 실제로 인용하며 확장안(`max_depth` 파라미터) 제시 |
| Data Flow | "## Data Flow" 절, 5단계 순서 서술 |
| Dependency / Boundary Definition | Component Identification/Interface 절에 통합 서술(3개 파일 간 호출 경계) |
| Implementation Strategy | "## Implementation Strategy" 절, 8단계 구현 순서 |
| Design Constraints | Skeleton의 빈 `constraints`를 반영해 별도 제약 서술 없음(정상 — 이 Issue와 무관) |
| Design Risks | "## Risks Carried Forward" 절, Skeleton의 RFC-0012 Risk를 실제로 해석해 "RFC-0012 경계 질문을 별도로 소유자에게 전달하라"는 구체적 후속 조치로 서술 |

`design`은 `str` 타입이며, 기존
`workflow_ast_context.identify_target(design: str)`의 Input 타입과
그대로 일치함을 확인했다(호출 자체는 이번 E2E 범위 밖 — Stage 04
검증 대상).

## 판정

**PASS(1건)** — Stage 01/02 Context가 Stage 03 Design에 실제로
반영됐고, 9개 관점 전부 확인 가능한 형태로 포함됐다. 결정적 골격
(`component_candidates`/`scope_candidates`/`constraints`/`risks`)이
Design에 정확히 재현됐고, 비결정적 관점(Architecture Definition 등
5개)도 원문을 단순 복붙하지 않고 실제로 해석·구조화했다.

## Open Issues

- 표본 1건 — 추가 재현은 필요시 후속 세션에서 수행
- `identify_target(design)` 실호출 여부(Design 텍스트에서 실제로
  올바른 target을 식별하는지)는 Stage 04 범위 — 이번 E2E는 타입
  정합성만 확인했다
- Interface/Contract 절이 실제 시그니처 변경(`max_depth` 파라미터
  추가)을 제안했는데, 이는 Design 산출물 내 제안일 뿐 — Stage 03이
  실제 Contract를 변경한 것은 아니다(코드 미수정, 텍스트 산출물)
