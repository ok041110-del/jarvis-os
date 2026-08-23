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

Task Decomposition/Acceptance Criteria는 Requirement 해석에 의존해
Stage 01 Context만으로 결정적 도출이 불가능하다 — 골격에 넣지 않고
Engine 지시문으로만 요청한다("새 Capability 금지" 제약 내 가능한 범위,
Stage 03 이후 더 정교화 가능, Open Issue: `VALIDATION.md`).

## 왜 `context_bundle`만 쓰는가

`run_stage_01()`의 나머지 키(`directory_structure`, `candidate_index`,
`target`, `dependency_closure`)는 AST/파일 구조 정보로 "어떻게
구현할지"(Stage 03 Design)에 더 적합하다 — Specification("무엇을
만들지")에는 `context_bundle`(Requirement Analysis용 8개 필드)만 쓴다.
