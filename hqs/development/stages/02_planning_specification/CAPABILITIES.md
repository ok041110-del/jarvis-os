# Stage 02: Capabilities

**RFC-0035/ADC-0038/ADR-0023으로 Stage 02는 PRD Passthrough에 더해 Task &
Dependency Agent + Deterministic Layer를 실행한다.** 신규 Capability는
정확히 1개(Task & Dependency Agent, Engine 1회 호출)만 추가됐다 — 별도
Task Agent/Dependency Agent/Acceptance Criteria Agent는 만들지 않는다
(`RESPONSIBILITY.md` 참고).

## 1. PRD/Specification Passthrough (Engine 미호출)

| 항목 | 내용 |
|---|---|
| Input | Stage 01 Output(`stage_01_context["prd"]`, `{skeleton, specification}` 형태) |
| Analysis | `stage_02.run_stage_02()` — `prd["skeleton"]`/`prd["specification"]`을 재해석·재생성 없이 그대로 반환한다 |
| Output | `skeleton`(`dict`), `specification`(`str`) — Stage 01의 `prd`와 동일 값 |
| Validation | `test_stage_02.py`에서 passthrough 동작(입력 변형 없음, 원본 불변)을 직접 단위 테스트 |

## 2. Task & Dependency Agent (Engine 1회 호출)

| 항목 | 내용 |
|---|---|
| Input | `prd["specification"]`(prose) |
| Analysis | `task_dependency_agent.decompose_tasks_and_dependencies()` — 단일 Engine 호출로 Task Decomposition과 Dependency Judgment를 함께 수행. `reasoning.py`의 `parse_structured_output()`/`AgentOutputError` 패턴을 재사용해 JSON 추출만 담당하고, 키/타입 검증은 하지 않는다(Deterministic Layer 책임) |
| Output | `{"tasks": [...], "dependencies": [...]}` 형태의 raw dict(구조 미검증) |
| Validation | `test_task_dependency_agent.py` — Engine 호출을 mock해 JSON 파싱/markdown fence 제거/파싱 실패 시 `AgentOutputError`를 확인 |

## 3. Deterministic Layer (LLM 호출 없음)

| 항목 | 내용 |
|---|---|
| Input | Task & Dependency Agent의 raw 출력(`{tasks, dependencies}`) |
| Analysis | `planning_pipeline.run_planning_pipeline()` — Schema Validation → Dependency Graph Validation(참조 무결성/self-dependency) → Cycle Detection(DFS white/gray/black) → Topological Ordering(Kahn's algorithm) → Implementation Plan Assembly → Final Aggregation을 순서대로 실행. 전 구간 순수 코드, Engine 호출 없음 |
| Output | `{"tasks": [...], "dependencies": [...], "plan": {"execution_order": [...]}}` |
| Validation | `test_planning_pipeline.py` — 정상 Task/Dependency, 잘못된 참조, self-dependency, 직접/간접 Cycle, Topological Ordering, 전체 파이프라인 통합을 순수 Python 데이터로 단위 테스트(mock 불필요) |
| 한계 | Cycle Detection은 구조적 무결성만 보장하며, 순환이 아닌 의미적으로 잘못된 의존관계는 걸러내지 못한다(ADR-0023, 의도적으로 받아들인 위험) |

## 실패 처리

`run_stage_02()`는 Task & Dependency Agent 호출 또는 Deterministic Layer
검증(예: Cycle 발견) 중 어느 단계에서 실패하더라도 `skeleton`/
`specification`은 영향받지 않고, `tasks=[]`/`dependencies=[]`/
`plan={"execution_order": []}`로 안전하게 채워 Contract의 5-key를 항상
만족시킨다(`test_stage_02.py`의 fallback 테스트 참고).
