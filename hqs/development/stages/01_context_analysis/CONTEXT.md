# Stage 01: Context 산출물 스키마

`run_stage_01(issue, target=None)`이 반환하는 `dict`의 키 5개.
후속 Stage(특히 02 Planning & Specification)는 이 구조를 그대로
입력으로 사용할 수 있다 — 새 Contract를 만들지 않고, 기존
`build_context_bundle()`/`build_function_candidate_index()`의 반환
형태를 그대로 재노출한다.

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `directory_structure` | `list[str]` | Repository Structure Analysis | 예 |
| `context_bundle` | `dict`(8개 키) | Relevant File/Document Discovery + Project Context Analysis | 예 |
| `candidate_index` | `str` | AST Function Candidate Index | 예(저장소 고정 경로 기반, `issue`와 무관) |
| `target` | `tuple[str, str] \| None` | 호출자가 전달한 시작점을 그대로 echo | 호출자가 `target`을 넘겼을 때만 |
| `dependency_closure` | `str \| None` | AST Dependency Closure | `target`이 주어졌을 때만, 없으면 `None` |

`directory_structure`는 `collect_relevant_context()`가 반환하는 키지만,
`build_context_bundle()`은 이 키를 그대로 버리고 8개 필드로만
재배치한다. 그래서 `run_stage_01()`은 `collect_relevant_context()`를
`directory_structure`를 얻기 위해 한 번 더 호출한다(파일 시스템 조회만
중복되고 Engine 호출은 없음) — 기존 `build_context_bundle()` 시그니처는
바꾸지 않는다.

## 왜 `target`을 Stage 01이 자동으로 채우지 않는가

AST Dependency Closure의 시작점 식별(`identify_target`,
`workflow_ast_context.py`)은 Design 산출물을 입력으로 요구한다 —
Design은 Stage 03(Architecture & Design)의 산출물이므로, Stage 01
시점에는 아직 존재하지 않는다. 그래서 `dependency_closure`는
Stage 01 혼자서는 항상 계산할 수 없는 optional 필드다 —
`RESPONSIBILITY.md`가 이를 명시적으로 책임 밖으로 규정한 이유다.
