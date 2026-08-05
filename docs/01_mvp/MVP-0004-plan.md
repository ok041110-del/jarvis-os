# MVP-0004 Plan: Hello SDLC

## 목적

Development HQ의 다음 MVP는 Stage를 개별적으로 완성하는 것이 아니라,
Issue 하나가 다음 흐름을 끝까지 통과하는 **가장 작은 End-to-End
Pipeline**을 구현하는 것이다.

```
Planning
  ↓
Design
  ↓
Implementation
  ↓
Validation
  ↓
Complete
```

Hello World가 프로그램의 최소 실행이라면, Hello SDLC는 AI Native
Development Pipeline의 최소 실행이다. 중요한 것은 각 Stage의 완성도가
아니라 **Pipeline이 끝까지 연결되는 것**이다.

이 문서는 계획 문서다. 이번 작업에서는 구현하지 않는다.

## Background — RFC-0003 §11 로드맵과의 관계

RFC-0003 §11과 ADC-0003 판단 3(Accept)은 MVP-0004를 "Implementation
Stage 검증"으로, MVP-0005를 "Validation Stage 검증"으로 순서를 제안했다.
이번 요청은 그 Stage-by-Stage 순서 대신 **하나의 얇은 파이프라인을 5개
Stage 전체에 먼저 관통시키는 방식**으로 MVP-0004의 범위를 재정의한다.

ADC-0003은 이 순서를 "구속력 있는 계획이 아니라 방향 제안"이라고 이미
명시했으므로, 이 재정의는 새 RFC/ADC 없이 MVP 기획 단계에서 그대로
반영할 수 있다.

## 현재 상태 (변경하지 않음)

- MVP-0001, MVP-0002(plan/observation), MVP-0003(plan), RFC-0001~0003,
  ADC-0001~0003, RT-0001, ADR-0001, Governance README, Development HQ
  Baseline(§Stage 반영 완료)은 확정되어 있다.
- 이 문서는 위 문서 중 어떤 것도 수정하지 않는다.

## 시나리오

Issue 하나(예: "문자열을 뒤집는 함수를 추가해 달라")가 5단계를 순서대로
통과한다.

1. **Planning** — Issue를 요구사항으로 정리한다.
2. **Design** — 요구사항을 최소한의 설계(함수 시그니처 등)로 변환한다.
3. **Implementation** — 설계를 코드로 만든다.
4. **Validation** — 만들어진 코드를 검증한다(MVP-0001의 `code_review`,
   `test_execution` 패턴 재사용).
5. **Complete** — 파이프라인이 끝까지 통과했음을 나타내는 종료 상태.

각 단계는 최소 기능만 구현한다. 병렬 실행, 재시도, 여러 Issue 동시 처리는
다루지 않는다.

## Stage ↔ 기존 Capability/Agent 매핑 (신규 Capability 없음)

`development-hq/STRUCTURE.md`의 기존 예시 목록(Capability 7개, Agent
7개)만으로 5단계 전부를 커버할 수 있다. **새 Capability/Agent 이름을
추가하지 않는다** — ADC-0003 판단 2(Capability Catalog 확장, Defer)와
그대로 일치한다.

| Stage | Capability(기존 예시) | Agent(기존 예시) | 코드 구현 여부 |
|---|---|---|---|
| Planning | `requirement_analysis` | Requirements Agent | 없음 → 신규 함수 필요 |
| Design | `design` | Design Agent | 없음 → 신규 함수 필요 |
| Implementation | `code_generation` | Backend Agent | 없음 → 신규 함수 필요 |
| Validation | `code_review`, `test_execution` | Backend Agent, QA Agent | **이미 있음** (MVP-0001) |
| Complete | (Capability 아님 — Pipeline 종료 상태) | 해당 없음 | 없음 → 최소 표기 필요 |

Backend Agent가 `code_generation`(Implementation)과 `code_review`
(Validation) 두 Capability를 모두 갖는 것은 STRUCTURE.md 문구("각
Agent는 하나 이상의 Capability를 가진다")와 그대로 일치하며 새 Agent를
만들 필요가 없다.

## 최소 구현 범위 (Minimum Observation Product) — 계획만, 구현하지 않음

- `development-hq/mvp/engine.py`의 `_rule_based_response()`에 3개
  prefix 분기(`REQUIREMENT_ANALYSIS:`, `DESIGN:`, `CODE_GENERATION:`)를
  추가한다. 이는 새 함수가 아니라 기존 단일 함수(`call_engine()`) 안의
  분기 추가이며, 지금 이미 있는 `CODE_REVIEW:`/`TEST_EXECUTION:` 분기와
  동일한 패턴이다(ADC-0001: Engine Gateway는 Keep in MVP로 이미 승인).
- `development-hq/mvp/agents.py`에 3개 함수를 추가한다:
  `requirements_agent_requirement_analysis()`,
  `design_agent_design()`, `backend_agent_code_generation()`. 각각
  `call_engine()`을 호출하는 한 줄짜리 래퍼이며, 기존
  `backend_agent_code_review()`와 동일한 형태다.
- `AGENT_CAPABILITY_MAP`에 3개 항목을 추가한다: `requirement_analysis
  → Requirements Agent`, `design → Design Agent`, `code_generation →
  Backend Agent`. 딕셔너리 형태 그대로 유지한다(Registry 일반화 금지,
  ADC-0001과 동일 원칙).
- 신규 파일 `development-hq/mvp/workflow_hello_sdlc.py`에
  `run_hello_sdlc(issue: str) -> dict`를 만든다. Planning →
  Design → Implementation → Validation(code_review → test_execution)
  → Complete 순서로 하드코딩된 함수 호출 5개(Validation은 2개 호출로
  기존과 동일)를 그대로 나열한다. 조건 분기·설정 파일·파서는 두지
  않는다.
- 반환값의 마지막 키는 `"status"`이며, 값은 `"Complete"`(예외 없이 전
  단계 통과) 또는 `"Failed"`(어느 단계에서든 예외 발생)로 고정한다.
  Task 상태를 별도 클래스나 상태 머신으로 일반화하지 않는다.
- 기존 `development-hq/mvp/workflow.py`, `workflow_0002.py`,
  `tests/test_mvp_0001.py`는 수정하지 않는다.

## Non-goals

- Scheduler, Queue, Runtime, Registry, Memory, Event Bus, Workflow
  Parser를 만들지 않는다.
- 병렬 실행, Retry, Priority, 여러 Issue 동시 처리를 구현하지 않는다.
- STRUCTURE.md의 기존 7개 Capability, 7개 Agent 목록을 벗어나는 이름을
  추가하지 않는다(ADC-0003 판단 2와 일치).
- 실제 Git 조작, 실제 CI/CD 호출, 외부 도구 연동을 구현하지 않는다. 각
  Stage의 "실행"은 MVP-0001과 동일하게 규칙 기반 `call_engine()` 응답으로
  대체한다.
- Model Routing/Engine Adapter/Multi Model을 구현하지 않는다(ADC-0003
  판단 4, Development HQ 권한 밖).
- 각 Stage의 완성도(정교한 Planning/Design 로직 등)를 높이지 않는다.
  목표는 연결(End-to-End)이지 품질이 아니다.
- `development-hq/stages/*/README.md`, `STRUCTURE.md`,
  RFC-0001~0003, ADC-0001~0003, RT-0001, ADR-0001을 수정하지 않는다.
- 이번 작업에서는 구현하지 않는다. 계획만 작성한다.

## Self Review

- Pipeline이 Planning→Design→Implementation→Validation→Complete를
  모두 거치는가 → **Pass(계획 수준)**. 5단계 각각에 대응하는 최소
  구현 항목을 빠짐없이 정의했다.
- 새로운 Capability/Agent를 추가했는가 → **아니오**. 5단계 모두
  STRUCTURE.md에 이미 예시로 등재된 이름만 사용한다.
- Architecture Drift가 없는가 → **Pass**. Scheduler/Registry/Runtime/
  Memory/EventBus/Parser를 포함하지 않았다.
- Kernel Leak가 없는가 → **Pass**. Engine 분기는 기존 패턴을 반복할
  뿐 새로운 추상화를 만들지 않는다.
- Stage의 완성도가 아니라 연결이 목표인가 → **Pass**. 각 Stage 구현은
  기존 `call_engine()` 규칙 기반 응답 수준으로 의도적으로 얕게
  유지했다.
