# Stage 02: Specification 산출물 스키마

**RFC-0035/ADC-0038/ADR-0023으로 `SpecificationResult`가 5-key로
확장됐다.** `skeleton`/`specification`은 Stage 01의 `prd`를 재생성 없이
그대로 반환하고(ADR-0022 유지), `tasks`/`dependencies`/`plan`은 Stage
02의 Task & Dependency Agent + Deterministic Layer가 새로 산출한다.

`dict`의 키 5개. 이 형태는 `ADR-0009`가 정의하는 Stage Data Contract의
Public Scope다(`hqs/development/BASELINE.md` "Stage Data Contract" 절,
`stages/contracts.py::SPECIFICATION_REQUIRED_KEYS`).

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `skeleton` | `dict`(4개 키: `problem_definition`, `constraints`, `risks`, `scope_candidates`) | Stage 01 PRD Synthesis(Passthrough) | 예 |
| `specification` | `str` | Stage 01 PRD Synthesis(Passthrough) | 예 |
| `tasks` | `list[dict]`(각 `id`/`title`/`description`) | Task & Dependency Agent + Deterministic Layer | 예(Agent/Deterministic Layer 실패 시 빈 리스트) |
| `dependencies` | `list[dict]`(각 `task`/`depends_on`) | Task & Dependency Agent + Deterministic Layer | 예(실패 시 빈 리스트) |
| `plan` | `dict`(`execution_order`: `list[str]`, Task id를 실행 순서대로 나열) | Deterministic Layer(Topological Ordering + Implementation Plan Assembly) | 예(실패 시 `{"execution_order": []}`) |

## Task/Dependency 구조

- `tasks`의 각 항목: `{"id": str, "title": str, "description": str}` —
  `id`는 `dependencies` 참조에 쓰이는 고유 식별자다.
- `dependencies`의 각 항목: `{"task": str, "depends_on": str}` — `task`
  (후행)가 `depends_on`(선행)의 완료를 전제로 한다는 의미다.
- `plan.execution_order`: Topological Ordering(Kahn's algorithm) 결과로,
  선행 Task가 항상 후행 Task보다 먼저 나온다.

## 7개 관점이 어디서 채워지는가

| 관점 | 위치 |
|---|---|
| Problem Definition | `skeleton["problem_definition"]`(결정적) + `specification` 서두 |
| Constraints | `skeleton["constraints"]`(결정적) + `specification`에 반영 |
| Risk | `skeleton["risks"]`(결정적) + `specification`에 반영 |
| Implementation Scope | `skeleton["scope_candidates"]`(결정적) + `specification`에 반영 |
| Requirement Analysis | `specification` 전체(Stage 01에서 이미 생성) |
| Task Decomposition | `tasks`(Task & Dependency Agent 산출, 구조화됨) |
| Dependency Judgment | `dependencies`(Task & Dependency Agent 산출, 구조화됨) |
| Dependency Ordering | `plan.execution_order`(Deterministic, Topological Sort) |
| Acceptance Criteria | `specification` 내(Stage 01 PRD Synthesis 지시문으로 이미 포함, 재생성하지 않음 — Decision 4) |

## 실패 시 값

Task & Dependency Agent 호출 실패(`AgentOutputError` 등) 또는
Deterministic Layer 검증 실패(`PlanningPipelineError` — 참조 무결성 위반,
Cycle 등)가 발생하면 `tasks=[]`, `dependencies=[]`,
`plan={"execution_order": []}`로 안전하게 채워진다. `skeleton`/
`specification`은 Stage 01 값을 그대로 전달하는 별개 경로이므로 이 실패의
영향을 받지 않는다.
