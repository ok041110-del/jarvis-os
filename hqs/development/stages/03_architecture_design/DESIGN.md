# Stage 03: Design 산출물 스키마

`run_stage_03(issue, stage_01_context, stage_02_output)`이 반환하는
`dict`의 키 2개. Stage 01/02처럼 새 Contract를 만들지 않고, 기존
Capability의 반환 형태를 그대로 재노출한다.

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `skeleton` | `dict`(4개 키: `component_candidates`, `scope_candidates`, `constraints`, `risks`) | Design Skeleton 추출 | 예(Stage 01/02 Context가 비어 있어도 빈 값으로 채워짐) |
| `design` | `str` | Architecture / Design 생성 | 예(Engine 실패 시에도 `_engine_failure_message()` 문자열로 채워짐) |

## 9개 관점이 어디서 채워지는가

| 관점 | 위치 |
|---|---|
| Component Identification | `skeleton["component_candidates"]`(결정적, Stage 01 `candidate_index` 재사용) + `design`에 반영 |
| Dependency / Boundary Definition | `skeleton["scope_candidates"]`(결정적, Stage 02 `skeleton` 재사용) + `design`에 반영 |
| Design Constraints | `skeleton["constraints"]`(결정적, Stage 02 `skeleton` 재사용) + `design`에 반영 |
| Design Risks | `skeleton["risks"]`(결정적, Stage 02 `skeleton` 재사용) + `design`에 반영 |
| Architecture Definition | `design` 내(지시문으로 요청, Engine 산출 — 결정적 골격 없음) |
| Responsibility Allocation | `design` 내(지시문으로 요청, Engine 산출) |
| Interface / Contract Identification | `design` 내(지시문으로 요청, Engine 산출) |
| Data Flow | `design` 내(지시문으로 요청, Engine 산출) |
| Implementation Strategy | `design` 내(지시문으로 요청, Engine 산출 — Task Decomposition(Stage 02)을 "어떻게 구현할지" 관점으로 재해석) |

나머지 다섯(Architecture Definition/Responsibility Allocation/
Interface·Contract Identification/Data Flow/Implementation Strategy)은
Requirement/Specification 해석에 의존해 Stage 01/02 Context만으로
결정적 도출이 불가능하다 — Engine 지시문으로만 요청한다(Stage 02의
Task Decomposition/Acceptance Criteria와 동일한 패턴).

## Stage 04가 이 Design을 어떻게 소비하는가

`design`(`str`)은 기존 `workflow_ast_context.identify_target(design:
str)`의 Input 타입과 그대로 일치한다 — Stage 04가 이 값을 직접 전달해
AST 시작점을 식별할 수 있다(호출 자체는 Stage 04 책임,
`RESPONSIBILITY.md`). 새 Contract가 아니라 기존 시그니처에 Output
타입을 맞춘 것이다.

## 왜 일부만 쓰는가

Stage 01의 `directory_structure`/`context_bundle`은 이미 Stage 02
Specification에 반영돼 재사용하지 않는다(`candidate_index`만 Stage 02가
쓰지 않아 새로 필요). Stage 02 `specification`은 그대로 전달하고,
`skeleton`의 결정적 필드(`scope_candidates`/`constraints`/`risks`)만
Design 골격에 편입한다.
