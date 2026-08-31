# Stage 01: Context 산출물 스키마

`run_stage_01(issue, target=None)`이 반환하는 `dict`의 키 5개.
후속 Stage(특히 02 Planning & Specification)는 이 구조를 그대로
입력으로 사용할 수 있다 — 기존 `build_context_bundle()`/
`build_function_candidate_index()`의 반환 형태를 그대로 재노출하며,
이 형태는 `ADR-0009`가 정의하는 Stage Data Contract의 Public
Scope다(`hqs/development/BASELINE.md` "Stage Data Contract" 절).

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `directory_structure` | `list[str]` | Repository Structure Analysis | 예 |
| `context_bundle` | `dict`(8개 키) | Relevant File/Document Discovery + Project Context Analysis | 예 |
| `candidate_index` | `str` | AST Function Candidate Index | 예(저장소 고정 경로 기반, `issue`와 무관) |
| `target` | `tuple[str, str] \| None` | 호출자가 전달한 시작점을 그대로 echo | 호출자가 `target`을 넘겼을 때만 |
| `dependency_closure` | `str \| None` | AST Dependency Closure | `target`이 주어졌을 때만, 없으면 `None` |

`build_context_bundle()`이 `directory_structure` 키를 버리므로,
`run_stage_01()`은 이를 얻기 위해 `collect_relevant_context()`를 한 번
더 호출한다(파일 시스템 조회만 중복, Engine 호출 없음, 기존 시그니처
불변).

## 왜 `target`을 자동으로 채우지 않는가

시작점 식별(`identify_target`)은 Design(Stage 03 산출물)을 입력으로
요구해 Stage 01 시점엔 존재하지 않는다 — `dependency_closure`가 항상
optional인 이유(`RESPONSIBILITY.md`).
