# ADR-0001: Development HQ Baseline에 Stage 기반 구조 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0001 |
| 제목 | Development HQ Baseline을 Stage 기반 AI Native SDLC 구조로 갱신하기 위한 구현 결정 |
| 상태 | Accepted |
| Context | `docs/governance/adc/ADC-0003.md` 판단 1(Stage 기반 내부 조직화, Decision: Accept, Next Step: ADR Required) |
| 관련 ADC | `docs/governance/adc/ADC-0003.md` 판단 1 |

이 ADR은 ADC-0003이 이미 내린 결정(Accept)을 다시 논의하지 않는다. 새로운
철학을 제안하지도 않는다. ADC-0003 판단 1을 실제 Baseline 문서 변경으로
옮기기 위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

- Model Routing, Engine Adapter, Multi Model — ADC-0003 판단 4(Out of
  Authority / Escalate)에 따라 Jarvis OS 수준의 별도 절차 대상이며, 이
  ADR의 범위가 아니다.
- Jarvis OS Layer(Concept Model, Meta Architecture, System Boundary) —
  변경하지 않는다.
- 새로운 Capability 추가 — ADC-0003 판단 2(Defer)에 따라 이 ADR에서
  다루지 않는다.

## Decision

### 1. Baseline 문서 변경 방법

변경 대상 문서는 `development-hq/STRUCTURE.md` **하나뿐**이다.

- `STRUCTURE.md`의 "내부 계층" 절만 수정한다. 현재 문구:

  ```
  HQ
  ↓
  (선택적) Division
  ↓
  (선택적) Team
  ↓
  Agent
  ```

  다음 문장을 추가한다: "Stage는 Development HQ가 선택적으로 사용할 수
  있는 또 다른 내부 조직 구조이며, Division/Team과 마찬가지로 Jarvis OS
  Meta Architecture의 필수 계층이 아니다. Development HQ는 Division/Team,
  Stage, 또는 둘 다 사용하지 않는 방식 중 선택할 수 있다." Division/Team
  표기는 삭제하지 않는다 — Stage는 대체가 아니라 동위의 선택지로
  추가된다.
- `MISSION.md`, `BOUNDARY.md`, `RESPONSIBILITY.md`,
  `development-hq/BASELINE.md`는 수정하지 않는다. 이 문서들은 이미
  "Workflow 내용", "Agent 구성", "내부 조직 구조 결정"을 특정 구조
  (Division/Team 등)에 못박지 않고 HQ의 책임으로만 서술하고 있어, Stage
  도입과 충돌하지 않는다.
- `development-hq/STRUCTURE.md`의 Capability 목록(예시)은 그대로
  유지한다. 확장하지 않는다(ADC-0003 판단 2).

### 2. Directory Structure 변경

코드 디렉토리(`development-hq/mvp/`)는 변경하지 않는다(§5 참조). 문서
디렉토리에 Stage별 설명 문서만 신설한다.

```
development-hq/
├── STRUCTURE.md            (§1 문구만 갱신)
├── stages/                 (신규 — 문서 전용, 코드 없음)
│   ├── 01_repository_intelligence/README.md
│   ├── 02_planning_specification/README.md
│   ├── 03_architecture_design/README.md
│   ├── 04_implementation/README.md
│   ├── 05_validation/README.md
│   └── 06_devops_release/README.md
└── mvp/                    (기존 그대로, 이동 없음)
```

각 `stages/<n>/README.md`는 §4(Stage 정의)의 목적·Responsibility·
Reference만 담는다. Capability 배정이나 실행 코드 배치는 규정하지 않는다
(ADC-0003 판단 2·4의 범위이며 이 ADR이 결정하지 않는다).

### 3. Domain Model 변경

변경은 다음 한 가지로 한정한다: **Stage를 Division/Team과 동일한 지위의
Development HQ 내부 개념으로 추가한다.** 그 외 Concept Model
(`Workflow → Task → Capability → Agent`)은 그대로 유지한다.

| 개념 | 상태 |
|---|---|
| Stage | 신규 — Division/Team과 동위의 HQ 내부 선택적 조직 개념 |
| Workflow, Task, Capability, Agent | 변경 없음 |

### 4. Stage 정의

RFC-0003 §8에서 제시된 6개 Stage 명칭과 목적을 그대로 채택한다(내용
재논의 없음).

| Stage | 목적 |
|---|---|
| Repository Intelligence | 프로젝트를 이해한다 |
| Planning & Specification | Intent를 실행 가능한 명세로 변환한다 |
| Architecture & Design | 구현 전에 구조를 설계한다 |
| Implementation | 명세를 코드로 구현한다 |
| Validation | 구현 결과를 검증한다 |
| DevOps & Release | 배포와 운영을 자동화한다 |

### 5. 기존 MVP-0001~0003 재사용 방식

기존 코드는 이동하거나 수정하지 않는다.

- `development-hq/mvp/agents.py`, `engine.py`, `workflow.py`,
  `workflow_0002.py`, `tests/`는 현재 위치에 그대로 둔다.
- `stages/04_implementation/README.md`와 `stages/05_validation/README.md`
  는 이 기존 코드를 "참고 구현 예시"로 **링크만** 건다(파일 이동이나
  복제 없음).
- MVP-0003(Task Lifecycle 관찰)은 아직 계획(Plan) 상태이며 구현된 코드가
  없으므로, 이 ADR이 이동시킬 대상이 없다.

### 6. Migration Strategy

한 번에 모두 바꾸지 않고 순서대로 적용한다.

1. `development-hq/STRUCTURE.md`에 §1의 Stage 문단을 추가한다.
2. `development-hq/stages/<n>/README.md` 6개를 생성한다(§2, §4 내용만).
3. `stages/04_implementation/README.md`, `stages/05_validation/README.md`
   에서 기존 `mvp/` 코드로의 참조 링크만 추가한다. 코드 자체는 옮기지
   않는다.
4. 이 Migration은 문서 변경으로만 구성되므로, 기존 MVP-0001/0002 테스트
   (`development-hq/mvp/tests/`)는 영향을 받지 않는다. 각 Step 이후
   기존 테스트가 여전히 통과하는지 확인한다.
5. MVP-0004 이후 로드맵(ADC-0003 판단 3, Accept)은 이 Migration이 끝난
   뒤 별도 작업으로 진행한다. 이 ADR의 범위가 아니다.

## Consequences

- `development-hq/STRUCTURE.md`와 신규 `development-hq/stages/` 문서에
  Stage 개념이 명시적으로 도입된다. Jarvis OS Architecture Baseline과
  Development HQ의 다른 문서(MISSION/BOUNDARY/RESPONSIBILITY/BASELINE)는
  변경되지 않는다.
- 이 ADR은 결정만 기록한다. §6에 정의된 실제 파일 변경(Baseline Update
  단계)은 별도 실행을 필요로 하며, 이 문서 자체가 그 변경을 수행하지
  않는다.
- 이후 계획되는 MVP(MVP-0004~0006, ADC-0003 판단 3)는 이 Stage 구조를
  전제로 진행될 수 있다.
- Model Routing/Engine Adapter/Multi Model/신규 Capability에 대한 결정은
  여전히 미해결 상태로 남으며, 각각 ADC-0003 판단 2·4가 지정한 별도
  절차(Defer 재관찰, Jarvis OS 수준 RFC)를 따른다.
