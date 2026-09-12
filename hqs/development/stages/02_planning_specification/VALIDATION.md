# Stage 02: Validation

**RFC-0035/ADC-0038/ADR-0023으로 Stage 02는 PRD Passthrough + Task &
Dependency Agent(Engine 1회) + Deterministic Layer로 구성된다.** 검증은
관심사별로 세 위치에 나뉜다.

## 검증 원칙

- PRD Passthrough(`skeleton`/`specification`)는 순수 dict 통과이므로
  mock 없이 결정적으로 단위 테스트한다.
- Task & Dependency Agent는 Engine 호출을 mock해 JSON 추출/파싱 동작만
  검증한다 — `tasks`/`dependencies`의 구조 검증은 검사하지 않는다(Schema
  Validation은 Deterministic Layer 책임).
- Deterministic Layer(Schema/Graph Validation, Cycle Detection,
  Topological Ordering, Plan Assembly)는 LLM 호출이 없으므로 순수 Python
  데이터로 각 단계를 독립적으로 단위 테스트한다.
- `run_stage_02()` 통합 테스트는 Task & Dependency Agent만 mock하고,
  Deterministic Layer는 실제로 실행해 전체 DAG의 배선을 확인한다.

## 테스트 위치

| 파일 | 대상 |
|---|---|
| `hqs/development/mvp/tests/test_stage_02.py` | `run_stage_02()` 통합 — PRD passthrough, 정상 Task/Dependency 처리, Agent 실패/Cycle 발견 시 fallback |
| `hqs/development/mvp/tests/test_task_dependency_agent.py` | Task & Dependency Agent — JSON 파싱, markdown fence 제거, 파싱 실패 시 `AgentOutputError` |
| `hqs/development/mvp/tests/test_planning_pipeline.py` | Deterministic Layer 각 단계 — Schema Validation, 참조 무결성, self-dependency, 직접/간접 Cycle Detection, Topological Ordering, Plan Assembly, 전체 파이프라인 |
| `hqs/development/mvp/tests/test_stage_contracts.py` | `SpecificationResult` 5-key Contract(`SPECIFICATION_REQUIRED_KEYS`) |
| `hqs/development/mvp/tests/test_stage01_stage02_prd_handoff.py` | Stage 01→02 E2E(mock) — PRD가 재생성 없이 그대로 전달되고 Contract를 통과하는지 |

## 검증 항목

| 항목 | 방법 |
|---|---|
| `skeleton`/`specification`이 Stage 01 PRD와 동일하게 전달 | `test_stage_02.py` passthrough 테스트 |
| 원본 PRD가 변형되지 않음 | `test_stage_02.py` mutate 테스트 |
| Task & Dependency Agent 출력이 정상 파싱됨 | `test_task_dependency_agent.py` |
| 잘못된 참조(존재하지 않는 task id) 거부 | `test_planning_pipeline.py::test_validate_dependency_graph_rejects_unknown_reference` |
| Self-dependency 거부 | `test_planning_pipeline.py::test_validate_dependency_graph_rejects_self_dependency` |
| 직접/간접 Cycle 탐지 | `test_planning_pipeline.py::test_detect_cycles_raises_on_*` |
| Topological Ordering이 선행 Task를 먼저 배치 | `test_planning_pipeline.py::test_topological_order_places_prerequisites_first` |
| Cycle/Agent 실패 시 안전한 빈 값으로 fallback | `test_stage_02.py::test_run_stage_02_falls_back_to_empty_planning_on_*` |
| `SpecificationResult` 5-key Contract | `test_stage_contracts.py` |

## real Engine E2E

Task & Dependency Agent는 Engine을 1회 호출하므로, "PRD가 실제로 Task/
Dependency 판단에 활용되는가"는 mock만으로 완전히 증명되지 않는다.
`test_omniroute_engine_real.py`와 동일한 opt-in 이중 게이팅
(`RUN_REAL_OMNIROUTE_TESTS=1 I_UNDERSTAND_REAL_EGRESS_RISK=1`) + 격리된
로컬 OmniRoute 서버로 실행하는 방법론을 그대로 따를 수 있다. 이번
구현에서는 실행 환경에 OmniRoute 패키지가 없어 real Engine E2E를 실제로
수행하지 못했다 — 방법론만 기록하고, Evidence는 남기지 않는다(가능한
환경에서 후속으로 수행).
