# RFC-0003 — Development HQ를 AI Native SDLC Platform으로 재정의

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | RFC-0003 |
| Status | Resolved — `docs/governance/adc/ADC-0003.md` → `ADR-0001`(판단 1에 한해)로 종결됨(STABILITY-0001 §1.2). 이 라벨은 절차 진행 상태만 반영하며, RFC 자체는 결정 문서가 아니다 |
| Owner / Scope | Development HQ 내부 구조(Workflow 내용, 내부 조직 구조, Agent 구성, Capability 목록) — Jarvis OS Architecture Baseline/Meta Architecture/Concept Model/System Boundary는 대상이 아니다 |

## 2. Problem & Context

| Item | Description |
|---|---|
| Problem | 사용자가 제시한 "AI Native SDLC Platform" 방향 전환 요청 — Development HQ를 "Agent Platform"이 아니라 SDLC 전체(Planning → Design → Implementation → Validation → Release)를 AI 중심으로 오케스트레이션하는 플랫폼으로 재정의할지 |
| Context | Development HQ MVP-0001~0003 및 기존 Governance(RFC-0001/0002, ADC-0001/0002, RT-0001) 진행 중 OpenHands/Aider/LangGraph/CrewAI/OpenAI Agents SDK/AWS AI Native SDLC/Claude Code Workflow를 조사한 결과, "SDLC 전체 오케스트레이션"이 Development HQ Mission("Jarvis OS Architecture Baseline v1.0이 실제 도메인에서 성립하는지 검증")에 더 부합한다는 판단이 제기됨. Jarvis OS Architecture Baseline §7 System Boundary는 "Workflow의 도메인 내용", "HQ 내부 조직 구조", "Agent 구성 및 역할 결정"을 이미 HQ 책임으로 명시 — 즉 이 방향 전환의 상당 부분은 Architecture Drift가 아니다 |
| Motivation | Stage(Repository Intelligence → Planning & Specification → Architecture & Design → Implementation → Validation → DevOps & Release) 조직화를 Jarvis OS Architecture Baseline 변경 없이 Development HQ Baseline 갱신만으로 반영 가능함을 확인 |
| Scope | Development HQ 내부 구조 10개 산출물: Architecture, Directory Structure, Domain Model, Interface, Stage Definition, Responsibility Catalog, Capability Catalog, MVP 재구성 계획, 재사용 코드, 제거 코드 |
| Non-Goals | Development HQ Baseline v1.0(BASELINE/MISSION/BOUNDARY/RESPONSIBILITY/STRUCTURE) 즉시 수정 안 함(Frozen 유지). Jarvis OS Architecture Baseline 수정 안 함. Execution Layer의 Multi-Model 지원(§4.2, §14 Boundary Risk)은 Jarvis OS Kernel 책임 영역이라 이 RFC의 결정 범위 밖(`development-hq/BOUNDARY.md`: "Engine 호출 | Kernel Engine Port/Adapter의 책임") |

## 3. Questions & Alternatives

### Questions for Review

| ID | Question | Reason |
|---|---|---|
| Q-1 | Stage 기반 내부 조직화(§4.1 신규 Architecture, Directory, Domain Model, Stage Definition)를 Development HQ Baseline 갱신 대상으로 채택할지 | 새 조직 구조 도입 여부 확정 필요 |
| Q-2 | Capability Catalog 확장(신규 12건 제안)을 채택할지, 기존 7개로 유지할지 | 기존 7개 중 6개가 이미 6개 Stage 전부에 최소 1개씩 대응돼 세분화 필요성이 불명확 |
| Q-3 | MVP-0004 이후 계획(Implementation/Validation/Repository Intelligence Stage 검증)을 승인할지 | 순차 검증 로드맵 확정 필요 |
| Q-4 | Execution Layer의 Multi-Model 지원은 Development HQ ADC 범위가 아니라 Jarvis OS 수준 RFC로 별도 상정할지 | Engine 교체 가능성은 HQ 권한 밖(Kernel 책임) |

### Alternatives to Consider

| ID | Alternative | Description |
|---|---|---|
| A-1 | 새 Architecture(HQ 내부 구조) | Stage → Responsibility → Capability → Agent 계층을 Division/Team의 선택적 대체로 도입. 기존 `Workflow → Task → Capability → Agent`는 유지 |
| A-2 | Execution Layer는 이번 RFC 범위 밖으로 유지 | Multi-Model 지원 구조를 설계하지 않고, §7(MVP 재구성)에서 "관찰을 얻기 위한 별도 MVP"로만 다룸 — ADC-0001의 "Keep in MVP" 판단과 RT-0001의 재평가 Trigger(Engine 수 ≥ 2)를 그대로 존중 |

## 4. Proposed Direction

> 검토를 위한 제안이며 최종 결정이 아님.

- **Directory Structure**: 기존 디렉토리를 삭제하지 않고 `stages/01_repository_intelligence/` ~ `06_devops_release/` 6개(Responsibility/Capability 문서만, 실행 코드 없음)를 추가하는 최소 변경안. `stages/`는 이 RFC에서 실제로 생성하지 않는다 — ADC 승인 후 별도로 만든다.
- **Domain Model**: Stage/Responsibility는 새 Jarvis OS Concept이 아니라 기존 Task/Capability를 조직화하는 명명법. Interface는 기존 `call_engine(prompt) -> str` 단일 함수 형태를 그대로 재사용(Model 교체 가능 Interface는 Kernel Engine Port/Adapter 영역이라 이 RFC가 설계하지 않음).
- **Stage Definition / Responsibility Catalog**: 6개 Stage와 각 Responsibility 목록을 요청 그대로 채택(Reference: Aider Repository Map, AWS AI Native SDLC, LangGraph, CrewAI, OpenHands 등).
- **Capability Catalog 확장(제안)**: 기존 7개(`code_generation`/`code_review`/`deployment`/`design`/`incident_response`/`requirement_analysis`/`test_execution`)를 대체하지 않고 12개 신규 후보(`repository_analysis`/`file_discovery`/`symbol_search`/`dependency_analysis`/`context_optimization`/`user_story_authoring`/`spec_authoring`/`task_decomposition`/`prototyping`/`git_operations`/`documentation`/세분화 후보)로 확장하는 안. 기존 7개 중 6개가 이미 6 Stage 전부에 최소 1개씩 대응 — 세분화 필요 여부는 Q-2로 ADC에 위임.
- **MVP 재구성 계획**: MVP-0004(Implementation, `backend_agent_code_review` 재해석) → MVP-0005(Validation, `qa_agent_test_execution` + MVP-0003 관찰 재사용) → MVP-0006(Repository Intelligence, 신규 Capability 필요 — 별도 ADC 대상). 각 MVP는 기존 규율(최소 구현, Architecture Drift 금지, Observation 우선, Stop Trigger → RFC 에스컬레이션)을 따른다.
- **재사용/제거 코드**: 기존 MVP-0001~0003 코드(`AGENT_CAPABILITY_MAP`, `backend_agent_code_review`, `qa_agent_test_execution`, `engine.py::call_engine()`, `workflow.py`/`workflow_0002.py`, `test_mvp_0001.py`)는 전부 재사용하고, 제거 대상은 **없다**(리터럴 딕셔너리·단일 함수 호출·하드코딩 조건 분기 수준이라 삭제 이유 없음). RFC-0001/0002·ADC-0001/0002·RT-0001의 Governance 흐름도 그대로 재사용.

## 5. Requested Review

| Review Item | Description |
|---|---|
| Required Review | ADC-0003이 Q-1~Q-4를 개별 판단 |
| Expected Feedback | Stage 조직화 채택 여부, Capability 확장 범위, MVP-0004 이후 로드맵 승인 여부 |

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | — | 없음(선행 RFC 없음) |
| ADC | `docs/governance/adc/ADC-0003.md` | 이 RFC의 Q-1~Q-4를 판단, 판단 1을 Accept |
| ADR | `docs/decisions/adr/ADR-0001-development-hq-stage-baseline-update.md` | ADC-0003 판단 1을 Baseline 반영으로 구현 |
| Open Decision | — | Model Routing/Engine Adapter/Multi Model(Q-4)은 Jarvis OS 수준 ADC-01/03·`RFC_CANDIDATES.md` Candidate 3·4의 정식 RFC 승격 대상으로 기록만 함(직접 해결하지 않음) |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | 사용자 요청에 따른 방향 전환 제안 정리 |
