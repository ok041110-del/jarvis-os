# Stage 01: Context 산출물 스키마

Production 경로(`teams/context/team.py` → `stage_01_multi_agent.py`)가
반환하는 `dict`의 키 6개(RFC-0034/ADC-0037/ADR-0022로 `prd` 추가). 후속
Stage(특히 02 Planning & Specification)는 이 구조를 그대로 입력으로
사용할 수 있다 — 이 형태는 `ADR-0009`가 정의하는 Stage Data Contract의
Public Scope다(`hqs/development/BASELINE.md` "Stage Data Contract" 절).
Legacy 결정적 `stage_01.py`(ADR-0021 보존 대상)는 여전히 `prd` 없는
5키만 반환한다 — Production 경로가 아니므로 이 표는 6키 형태를
기준으로 한다.

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `directory_structure` | `list[str]` | Repository Structure Analysis | 예 |
| `context_bundle` | `dict`(8개 키) | Relevant File/Document Discovery + Project Context Analysis | 예 |
| `candidate_index` | `str` | AST Function Candidate Index | 예(저장소 고정 경로 기반, `issue`와 무관) |
| `target` | `tuple[str, str] \| None` | 호출자가 전달한 시작점을 그대로 echo | 호출자가 `target`을 넘겼을 때만 |
| `dependency_closure` | `str \| None` | AST Dependency Closure | `target`이 주어졌을 때만, 없으면 `None` |
| `prd` | `dict`(`skeleton`/`specification` 2개 키, `SpecificationResult`와 동일 형태) | PRD/Specification Synthesis(`prd_synthesis.py`) | 예(Structured Understanding + Repository Context 종합, Engine 실패 시에도 오류 포맷으로 채워짐) |

## PRD/Specification Synthesis (RFC-0034/ADC-0037/ADR-0022)

`prd`는 Structured Understanding(Reasoning Aggregator 결과, 재추론
없이 직렬화)과 Repository Context(`context_bundle`/`candidate_index`/
`directory_structure`)를 종합해 기존 Requirement Agent
(`requirements_agent_requirement_analysis`)를 정확히 1회 호출한 결과다
— 새 Agent/Capability가 아니라 기존 Stage 02 Capability의 호출 위치
이동이다. Stage 02는 이제 이 값을 재생성 없이 그대로 전달한다
(`stage_02.py`).

`build_context_bundle()`이 `directory_structure` 키를 버리므로,
`run_stage_01()`은 이를 얻기 위해 `collect_relevant_context()`를 한 번
더 호출한다(파일 시스템 조회만 중복, Engine 호출 없음, 기존 시그니처
불변).

## 왜 `target`을 자동으로 채우지 않는가

시작점 식별(`identify_target`)은 Design(Stage 03 산출물)을 입력으로
요구해 Stage 01 시점엔 존재하지 않는다 — `dependency_closure`가 항상
optional인 이유(`RESPONSIBILITY.md`).

## Multi-Agent Reasoning과 Public Contract의 관계

`RFC-0033`/`ADC-0036`/`ADR-0021`로 Stage 01 내부에 Multi-Agent
Reasoning(Intent/Goal/Requirement/Ambiguity Agent → Structured
Understanding)이 추가됐다. Structured Understanding은 **내부 중간
산출물**이며, 이 표가 정의하는 5개 키(Public Contract, `ADR-0009` Stage
Data Contract Scope)는 그대로 유지된다 — Stage 02 이후는 여전히 이
5개 키만 Input으로 받는다.
