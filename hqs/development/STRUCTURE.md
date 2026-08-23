# Development HQ Structure

## 내부 계층

```
HQ
↓
(선택적) Division
↓
(선택적) Team
↓
Agent
```

Division과 Team은 Development HQ 내부의 선택적 관례이며, Jarvis OS Meta Architecture의 필수 계층이 아니다. Jarvis OS Kernel은 Division/Team의 존재 여부를 알지 못하며, 이 계층은 Registry에 등록되지 않는다.

Stage는 Development HQ가 선택적으로 사용할 수 있는 또 다른 내부 조직 구조이며, Division/Team과 마찬가지로 Jarvis OS Meta Architecture의 필수 계층이 아니다. Development HQ는 Division/Team, Stage, 또는 둘 다 사용하지 않는 방식 중 선택할 수 있다. Stage 정의는 `hqs/development/stages/`를 참조한다(ADR-0001, ADR-0008).
ADR-0008은 ADR-0001 §2/§6("stages/는 문서 전용, 코드 없음")을
Supersede했다 — Stage 폴더는 이제 문서와 실행 코드를 함께 관리할 수
있다.

## Capability (예시)

아래는 Development HQ가 Registry에 등록할 수 있는 Capability의 예시일 뿐이며, Reference Architecture로 확정하는 목록이 아니다. 다른 HQ는 전혀 다른 Capability 집합을 가질 수 있다.

나열 순서는 알파벳순이며, **Capability의 나열 순서는 Workflow 실행 순서나 어떤 프로세스 단계도 의미하지 않는다.** Capability는 각각 독립적인 능력 단위이며, 이들이 실제로 어떤 순서로 조합되어 쓰이는지는 Workflow가 별도로 정의한다.

- `code_generation`
- `code_review`
- `deployment`
- `design`
- `incident_response`
- `requirement_analysis`
- `test_execution`

## Agent (예시)

- Backend Agent
- Design Agent
- Frontend Agent
- Ops Agent
- QA Agent
- Release Agent
- Requirements Agent

각 Agent는 Development HQ에 소속되며 하나 이상의 Capability를 가진다.

## Workflow 관계

```
Workflow
↓
Task
↓
Capability
↓
Agent
```

Workflow는 Task들의 실행 순서를 정의하고, 각 Task는 필요한 Capability를 요구하며, 그 Capability를 가진 Agent가 Task를 수행한다.

이 관계는 항상 Capability를 경유한다.

- Workflow는 Agent를 직접 참조하지 않는다. Workflow는 Task의 순서만 정의한다.
- Task는 Agent를 직접 호출하지 않는다. Task는 필요한 Capability만 요구한다. Task를 어느 Agent에게 배분할지는 Runtime의 책임이다 (Concept Model: "Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다").

Task의 실행 스키마(task_type, input, output 등)는 Kernel 설계 범위이며 이 문서에서 정의하지 않는다.

## Engine과의 관계

Engine 호출은 Development HQ의 책임이 아니라 Kernel(Engine Port/Adapter)의 책임이다 (`BOUNDARY.md` 참조). Development HQ는 Agent가 실제로 어떤 Engine을 사용하는지 정의하거나 통제하지 않는다.

> Capability, Agent, Engine 사이의 세부 관계(예: 하나의 Capability를 여러 Agent가 제공할 수 있는지, 하나의 Engine을 여러 Agent가 공유할 수 있는지 등)는 이미 논의되었으나 아직 정식 RFC로 승격되지 않은 Architecture 후보다. 이 Starter Kit에는 반영하지 않는다. → `docs/decisions/rfc/RFC_CANDIDATES.md` 참조.
