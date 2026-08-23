# Stage 02: Specification 산출물 스키마

`run_stage_02(issue, stage_01_context)`이 반환하는 `dict`의 키 2개.
Stage 01처럼 새 Contract를 만들지 않고, 기존 Capability의 반환 형태를
그대로 재노출한다.

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `skeleton` | `dict`(4개 키: `problem_definition`, `constraints`, `risks`, `scope_candidates`) | Specification Skeleton 추출 | 예(Stage 01 Context가 비어 있어도 빈 값으로 채워짐) |
| `specification` | `str` | Requirement & Specification 생성 | 예(Engine 실패 시에도 `_engine_failure_message()` 문자열로 채워짐 — Stage 01의 5개 필드와 달리 이 Stage는 Engine을 호출하므로 실패 가능성이 있다) |

## 7개 관점이 어디서 채워지는가

| 관점 | 위치 |
|---|---|
| Problem Definition | `skeleton["problem_definition"]`(결정적) + `specification` 서두 |
| Constraints | `skeleton["constraints"]`(결정적) + `specification`에 반영 |
| Risk | `skeleton["risks"]`(결정적) + `specification`에 반영 |
| Implementation Scope | `skeleton["scope_candidates"]`(결정적) + `specification`에 반영 |
| Requirement Analysis | `specification` 전체(기존 Requirement Analysis Capability의 본래 책임) |
| Task Decomposition | `specification` 내(지시문으로 요청, Engine 산출 — 결정적 골격 없음) |
| Acceptance Criteria | `specification` 내(지시문으로 요청, Engine 산출 — 결정적 골격 없음) |

Task Decomposition과 Acceptance Criteria는 Stage 01 Context만으로는
결정적으로 도출할 수 없다(각 Task/기준은 Requirement 해석에 의존) —
그래서 이 둘은 골격(`skeleton`)에 없고, Engine 호출의 지시문으로만
요청한다. 이는 "새 Capability를 만들지 않는다"는 제약 아래 가능한
범위이며, Stage 03 이후 Design 산출물로 더 정교화될 수 있다(Open
Issue로 `VALIDATION.md`에 기록).

## 왜 Stage 01의 Output 전체가 아니라 `context_bundle`만 쓰는가

`run_stage_01()`의 다른 키(`directory_structure`, `candidate_index`,
`target`, `dependency_closure`)는 AST/파일 구조 정보로, Specification
(무엇을 만들지)보다 Stage 03 Design(어떻게 구현할지)에 더 적합하다
— Stage 02는 `context_bundle`(Requirement Analysis가 이미 소비하도록
설계된 8개 필드)만 골격 추출에 사용한다.
