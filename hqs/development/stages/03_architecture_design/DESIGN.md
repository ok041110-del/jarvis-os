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

Architecture Definition/Responsibility Allocation/Interface·Contract
Identification/Data Flow/Implementation Strategy는 Stage 01/02 Context
만으로는 결정적으로 도출할 수 없다(Requirement/Specification 해석에
의존) — 그래서 이 다섯은 골격(`skeleton`)에 없고, Engine 호출의
지시문으로만 요청한다. 이는 Stage 02의 Task Decomposition/Acceptance
Criteria와 동일한 패턴이다.

## Stage 04가 이 Design을 어떻게 소비하는가

`design`(`str`)은 이미 존재하는 `workflow_ast_context.identify_target
(design: str)`의 Input 타입과 그대로 일치한다 — Stage 04가
`run_stage_03()`의 `design` 값을 그 함수에 직접 전달하면 AST 시작점을
식별할 수 있다(Stage 03은 이 호출을 스스로 하지 않는다,
`RESPONSIBILITY.md` 참고). 이는 새 Contract를 만든 것이 아니라, 기존
함수 시그니처(`design: str`)에 이 Stage의 Output 타입을 맞춘 것이다.

## 왜 Stage 01/02의 Output 전체가 아니라 일부만 쓰는가

Stage 01의 `directory_structure`/`context_bundle`은 이미 Stage 02
Specification에 반영됐으므로 Stage 03에서 다시 쓰지 않는다(중복 방지
— `candidate_index`만 새로 필요한 이유는 Stage 02가 이를 쓰지 않았기
때문). Stage 02의 `specification`은 그대로 전달하고, `skeleton`의
결정적 필드(`scope_candidates`/`constraints`/`risks`)만 재사용해
Design 골격에 편입한다.
