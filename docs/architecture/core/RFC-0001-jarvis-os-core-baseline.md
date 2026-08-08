# RFC-0001: Jarvis OS Kernel Baseline

**Status**: Resolved — `ADC-0001-core-baseline.md`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (Development HQ Phase 1 종료 → Kernel 설계 단계 진입 시점 요청에 대한 RFC)
**대상**: Jarvis OS Kernel의 Mission, Boundary, Kernel Module, Kernel API, Design Principle (Baseline 정의만)
**전제**: Development HQ는 Phase 1(Capability Foundation)을 완료한 것으로 간주하며, 더 이상 수정하지 않는다.
**Evidence 범위**: `docs/01_architecture/BASELINE.md`, `docs/03_adc/ADC.md`, Development HQ RFC
(`docs/02_rfc/RFC-0001~0005`), ADC(`docs/governance/adc/ADC-0001~0004`), ADR
(`docs/04_adr/ADR-0001`), Observation(`docs/governance/observations/OBS-0001~0006`,
`docs/01_mvp/MVP-0001~0013`), Evidence Review(`docs/research/EVIDENCE-REVIEW-0001.md`).
새로운 실험은 하지 않았다.

> 본 RFC는 Execution Layer를 설계하지 않는다. 본 RFC는 Runtime, Multi-Agent,
> Scheduler, Cost Optimization, Retry, Parallel Execution, Git, Deployment,
> Prompt Engineering, Model Routing을 다루지 않는다. 본 RFC는 새 Architecture를
> 발명하지 않는다. Development HQ에서 반복적으로 검증된 사실과, 이미 Frozen인
> Architecture Baseline v1.0의 Concept Model만 Kernel 수준으로 일반화한다.

## 0. 이 RFC가 열린 이유

Jarvis OS는 HQ 구현(Development HQ MVP-0001~0013) 단계에서 Kernel 설계 단계로
진입한다. Development HQ는 Phase 1을 완료한 것으로 간주하고 더 이상 수정하지
않는다. 이 RFC의 목적은 Execution Layer를 포함한 새 Architecture를 설계하는
것이 아니라, Development HQ가 한 HQ의 전체 Capability Loop를 반복하는 동안
실제로 관찰·결정된 사실들을 Jarvis OS Kernel의 Baseline으로 일반화하는 것이다.

## 1. Kernel Mission

Jarvis OS Kernel는 모든 HQ가 공통으로 사용하는 Shared Infrastructure다.

- Kernel는 도메인 로직을 갖지 않는다.
- Kernel는 공통 서비스를 제공한다.
- HQ는 Kernel를 사용한다.
- Kernel는 HQ를 알지 못한다.

**근거**: 이 Mission은 새 진술이 아니라 `BASELINE.md` §7 System Boundary가
이미 "Jarvis OS의 책임"과 "Jarvis OS가 책임지지 않는 것"으로 확정해 둔
내용을 그대로 재진술한 것이다. Development HQ는 한 Phase 전체(MVP-0001~0013)
동안 이 경계를 위반하지 않았다는 사실이 실측으로 확인되어 있다.
`development-hq/BOUNDARY.md`는 "Development HQ가 절대 책임지지 않는 것"으로
Task 실행 메커니즘·Agent 간 메시지 배달·Engine 호출·Capability 색인·Policy
판정·HQ 생명주기 상태 관리·물리 자원 배분을 명시했고, RFC-0005 §4는 Phase 1
종료 시점까지 이 경계가 실제로 지켜졌음을 사실 근거로 재확인했다("Development
HQ의 모든 Capability는 문자열 마커 매칭만으로 구현되어 있다. LLM/ML 호출은
한 번도 추가되지 않았다").

## 2. Position

```
Jarvis OS

├── Kernel
│
│   ├── Governance
│   ├── Workflow
│   ├── Memory
│   ├── Execution Layer
│   ├── Event Bus
│   └── ...
│
└── HQ
    ├── Development HQ
    ├── Research HQ
    ├── Writing HQ
    ├── Math HQ
    └── ...
```

Kernel는 HQ 위에 존재하지 않는다. Kernel는 HQ 아래에도 존재하지 않는다. Kernel는
모든 HQ가 공유하는 공통 계층이다.

**근거**: `BASELINE.md` §5 Meta Architecture(`Jarvis OS → HQ → Agent →
Connector`)와 `development-hq/BOUNDARY.md`의 계층 관계(`Jarvis OS →
Development HQ → Agent → Connector`)는 이미 이 수직 관계를 확정해 두었다.
이 RFC는 그 계층의 "Jarvis OS" 위치를 "Kernel"로 명명하고, 지금까지 이름 없이
Out of Scope로 남아 있던 자리(`BASELINE.md` §10: Kernel Architecture,
Component Design)를 Kernel라는 하나의 층으로 일반화할 뿐, 계층 구조 자체를
새로 발명하지 않는다.

## 3. Boundary

Kernel는 Service를 제공한다. HQ는 Capability를 제공한다.

Kernel는 도메인을 모른다. HQ는 도메인을 안다.

Kernel는 Specification, Context, Execution Result, Event 같은 공통 Artifact만
다룬다.

**근거**: `BASELINE.md` §7의 "Jarvis OS 책임" 목록(Registry, 생명주기 관리,
Task/Event 전달, Engine 호출 표준 인터페이스, Context/Artifact 저장 인프라,
Policy 판정 메커니즘, 자원/예산 배분, 실패 관측 가능성)과 "HQ 책임" 목록
(Workflow 내용, 내부 조직 구조, Agent 구성, 도메인 규칙, Capability 내용)의
구분을 그대로 채택한다. 이 구분이 실제로 성립했다는 근거는 RFC-0005 §1·§4다:
Development HQ는 Phase 1 전체 동안 Implementation Specification이라는
Artifact를 생성하는 지점까지만 책임졌고, 그 Specification으로부터 실제 코드를
만드는 것(Execution) — 도메인이 아니라 공통 메커니즘인 Engine 호출 — 은 한
번도 자체적으로 만들지 않았다.

## 4. Kernel Modules

이번 RFC에서는 모듈 이름과 책임만 정의한다. 구현은 하지 않는다.

### 4.1 Governance

**책임**: Architecture Decision 관리.

**근거**: 이 책임은 발명이 아니라, 지금까지 실제로 5회(RFC-0001~0005) 이상
반복 실행되어 검증된 절차 그 자체다. `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`
가 정의한 `RFC → ADC → ADR → Baseline Update` 절차는 Jarvis OS 수준
(`docs/03_adc/ADC.md`의 ADC-01~12)과 Development HQ 수준(`docs/governance/adc/ADC-0001~0004`,
`docs/04_adr/ADR-0001`) 양쪽에서 동일한 형태로 반복 사용되었다. RFC-0004는
여기에 더해 "Rule A(RT Trigger 충족 → RFC)"라는 절차 규칙까지 실측으로
검증했다. 이 반복된 절차가 Governance 모듈의 근거다.

### 4.2 Workflow

**책임**: 공통 Workflow 실행.

**근거**: `BASELINE.md` §6 Concept Model은 이미 Workflow를 "Task들의 실행
순서(그래프)를 정의하는 선언적 정의"로 등록해 두었다. Development HQ는
Phase 1 동안 이 개념에 해당하는 자리(Task Dispatcher)를 MVP-0001부터
MVP-0013까지 반복해서 하드코딩된 순차 호출로 채웠고, `docs/governance/adc/ADC-0004`는
이 패턴이 실패한 적이 없다는 사실(Q1)과 다음 MVP 진행을 막은 적이 없다는
사실(Q2)에 근거해 Development HQ 범위에서는 "Keep in MVP"로 판단했다.
`docs/research/EVIDENCE-REVIEW-0001.md`는 MVP-0005~0008 4건 모두에서 동일한
패턴(새 하드코딩된 순차 호출 파일 반복 추가)이 다시 확인되었다고 기록한다.
Workflow 실행이라는 공통 필요 자체는 모든 MVP에서 반복 관찰되었으나, 그
실행 메커니즘을 지금 Kernel/Kernel 수준에서 어떻게 일반화할지는 여전히
Open이다(`docs/03_adc/ADC.md` ADC-02 "Runtime 개념의 존폐", 우선순위 NOW).
이 RFC는 Workflow가 Kernel Module이라는 위치만 확인하고, 그 내부 구조(Runtime
명칭 포함)는 결정하지 않는다.

### 4.3 Memory

**책임**: 공통 Context 저장 및 조회.

**근거**: `BASELINE.md` §6은 Memory를 이미 "Context를 HQ 네임스페이스 안에
영속화하는 서비스"로 등록해 두었다. Development HQ는 Phase 1 전체
(MVP-0005~0008, `EVIDENCE-REVIEW-0001.md` "Context 전달 방식" 절)에서
Context를 자체 저장소 없이 기존 `issue["description"]` 문자열에 이어붙이는
단일 경로로만 다뤘고, 별도의 영속화 메커니즘을 스스로 만든 적이 없다. 이는
Memory가 HQ 내부에서 자체 구현되지 않고 Kernel 수준의 공통 서비스 자리로
남아 있었다는 사실을 보여준다. `docs/02_rfc/RFC-0001-kernel-boundary.md`
§Context 전달 메커니즘 질문과 RT-0001 Candidate 4는 이 자리를 언제
Memory Service로 승격할지를 이미 Open Question으로 남겨 두었다 — 이 RFC는
그 질문에 답하지 않고, Memory가 Kernel Module이라는 위치만 확인한다.

### 4.4 Execution Layer

**책임**: Specification 기반 AI 실행.

**근거**: 이 모듈의 경계는 이번 RFC 중 가장 직접적인 근거를 가진다.
`docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`는 Development HQ가
Implementation Specification(Target File / Public Interface / Functions /
Classes / Dependencies / Algorithm Outline / Edge Cases / Validation Notes
8개 항목)을 생성하고 그 구조적 완전성만 검증하는 지점에서 끝난다는 것과,
그 Specification으로부터 실제 코드를 생성·실행·테스트하고 Model/Engine을
선택·호출하는 지점부터 Execution Layer가 시작된다는 것을 사실 근거로 이미
정리했다. `development-hq/BOUNDARY.md`("Engine 호출 — Kernel Engine
Port/Adapter의 책임")와 `BASELINE.md` §7("Engine 호출의 표준 인터페이스
제공(Port/Adapter)")은 이 경계를 Jarvis OS 수준에서 이미 확정해 두었다.
따라서 Execution Layer를 Kernel의 일부로 정의하는 것은 새 결정이 아니라, 이미
확정된 System Boundary와 RFC-0005의 관찰을 하나의 Kernel Module로 명명하는
것이다. Execution Layer의 내부 구조(Prompt 구성, Model 선택, 재시도 정책)는
`docs/03_adc/ADC.md`의 ADC-01(Model↔Component 대응)·ADC-02(Runtime 존폐)와
`docs/governance/adc/ADC-0003.md` 판단 4(Multi-Model, Out of Authority)가
여전히 Open으로 남겨 둔 영역이며, 이 RFC는 그 내부를 설계하지 않는다.

### 4.5 Event Bus

**책임**: Kernel 내부 Event 전달.

**근거**: 다른 4개 Module과 달리, Event Bus는 Development HQ Phase 1 동안
직접 관찰된 실증 근거를 갖지 않는다. `docs/02_rfc/RFC-0001-kernel-boundary.md`
는 이미 "MVP-0001은 실행 실패·재시도 상황을 직접 관찰하지 않았다(Fault
전파 인프라는 MVP Out of Scope)"고 명시했고, Phase 1 전체(MVP-0001~0013)
에서도 Fault 전파나 Event Flow를 실제로 실행한 Observation은 없다. 이
Module의 근거는 오직 `BASELINE.md` §6 Concept Model이 이미 Frozen 상태로
정의해 둔 것뿐이다: "Task는 실패 시 Fault를 발생시키고, Fault는 Event로
전파된다", "Event는 HQ 경계를 가로질러(Event Flow) 전파된다." `docs/03_adc/ADC.md`
의 ADC-05(Fault Event 배달 보장 수준)는 이 Module의 배달 보장 수준을 여전히
Open으로 남겨 두었다. 이 사실을 정직하게 기록한다 — Event Bus는 Concept
Model에 이미 존재했던 자리를 Kernel Module로 재확인한 것이지, Development
HQ Observation으로 새로 검증된 것이 아니다.

## 5. Kernel API Principle

Kernel는 구체 구현이 아니라 Service Interface만 노출한다.

| Module | Interface (예) |
|---|---|
| Memory | `store()`, `retrieve()` |
| Execution | `submit()`, `status()`, `result()`, `cancel()` |
| Workflow | `start()`, `stop()`, `resume()` |
| Governance | `propose()`, `review()`, `approve()` |

**근거**: 위 Interface는 함수 시그니처나 자료구조를 새로 설계한 것이 아니라,
지금까지 각 Module의 근거가 된 행위 자체를 동사로만 명명한 것이다. 예를 들어
`propose()`/`review()`/`approve()`는 RFC 제출 → ADC 판정 → ADR 승격이라는,
이미 5회 이상 실행된 절차의 세 단계를 그대로 옮긴 것이다. `submit()`/`status()`/
`result()`/`cancel()`은 RFC-0005가 정리한 "Specification을 넘기면 Execution
Layer가 실행하고 결과를 돌려준다"는 관찰된 흐름을 넘어서지 않는다. 이 표는
구현 방법(자료구조, 프로토콜, 저장소)을 규정하지 않으며, `BASELINE.md` §10이
Component Design을 Out of Scope로 유지한 원칙을 그대로 따른다.

## 6. Design Principles

Kernel는 다음을 유지한다.

- **HQ Independent** — Kernel는 HQ를 알지 못한다(§1, §3 근거와 동일).
- **Model Independent** — `BASELINE.md` §3 "Engine Independent" 원칙과 동일.
  RFC-0005 §4는 Development HQ가 Phase 1 전체 동안 어떤 Model도 직접
  호출하지 않았다는 사실로 이 원칙이 실제로 지켜졌음을 보여준다.
- **Artifact Driven** — RFC-0005 §3이 정리한 것처럼, Kernel Module 사이의
  전달 단위는 항상 명세된 Artifact(Implementation Specification 8개 항목
  같은)였지, 코드나 프로세스가 아니었다.
- **Service Oriented** — §5의 Kernel API Principle과 동일. Kernel는 Interface만
  노출한다.
- **Stateless Interface** — `BASELINE.md` §6 Concept Model은 Context를
  "Task 실행 중에만 유효한 State"로, Memory를 그 영속화 지점으로 이미
  분리해 두었다. Interface 자체는 상태를 갖지 않고, 상태는 Memory Module이
  전담한다.

## 7. Out of Scope

이번 RFC에서는 다루지 않는다.

- Runtime
- Multi-Agent
- Scheduler
- Cost Optimization
- Retry
- Parallel Execution
- Git
- Deployment
- Prompt Engineering
- Model Routing

## Non-goals

- 이 RFC는 Kernel Module을 어떻게 구현할지 논의하지 않는다.
- 이 RFC는 Execution Layer, Workflow, Memory, Event Bus, Governance의 내부
  구조(자료구조, 프로토콜, 저장소, Runtime 명칭)를 설계하지 않는다.
- 이 RFC는 ADC-01, ADC-02, ADC-03, ADC-05, ADC-09, ADC-10을 비롯한 기존
  Open Decision을 대신 해결하지 않는다.
- 이 RFC는 Architecture Baseline v1.0(Frozen)이나 Development HQ Baseline을
  변경하지 않는다. Development HQ는 이 RFC로 인해 수정되지 않는다.
- 이 RFC는 새 Architecture, 새 Layer, 새 Component를 발명하지 않는다 — §1~6
  각 절의 "근거" 문단이 인용한 기존 문서만을 일반화했다.
- 이 RFC는 ADC, ADR, MVP 문서를 작성하지 않는다.
- 이 RFC는 코드를 구현하지 않으며 커밋되지 않는다.

## Evidence 목록

- `docs/01_architecture/BASELINE.md` (Frozen Architecture Baseline v1.0)
- `docs/03_adc/ADC.md` (Jarvis OS 수준 Open Decision, ADC-01~12)
- `docs/02_rfc/RFC-0001-kernel-boundary.md`
- `docs/02_rfc/RFC-0002-task-dispatcher-boundary.md`
- `docs/02_rfc/RFC-0004-task-dispatcher-runtime-boundary.md`
- `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md`
- `docs/governance/adc/ADC-0001~0004.md`
- `docs/governance/rt/RT-0001.md`
- `docs/governance/observations/OBS-0001~0006.md`
- `docs/04_adr/ADR-0001-development-hq-stage-baseline-update.md`
- `docs/research/EVIDENCE-REVIEW-0001.md`
- `docs/01_mvp/MVP-0001~0013` 관련 Observation/Plan 문서
- `development-hq/BOUNDARY.md`, `development-hq/MISSION.md`

새 실험은 하지 않았다. 새 구조는 발명하지 않았다.

## 다음 절차

이 RFC는 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 절차를 따른다.

```
RFC-0001 (본 문서)
↓
docs/03_adc/ADC.md에 결정 필요 항목으로 등록 (또는 기존 ADC-01/02/03/05/09/10에 흡수)
↓
ADR
↓
Architecture Baseline Update (Kernel 절 신설)
```

이 RFC 자체는 §4~6에서 제시한 Module 이름·책임·API Interface·Design
Principle을 채택할지 여부를 결정하지 않는다. Architecture Governance
절차를 통해 별도로 판단한다.

## Self Review

- Execution Layer를 설계했는가 — **아니오**. §4.4는 경계와 근거만
  기록했고 내부 구조를 다루지 않았다.
- ADC/ADR/MVP를 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- 새 Architecture를 발명했는가 — **아니오**. 각 절의 "근거" 문단이 인용한
  기존 Baseline/RFC/ADC/ADR/Observation/Evidence Review 문서 범위를
  벗어난 진술은 없다.
- Development HQ를 수정했는가 — **아니오**. Development HQ 문서·코드는
  읽기만 했다.
- Out of Scope 항목(Runtime 세부 구조, Multi-Agent, Scheduler, Cost
  Optimization, Retry, Parallel Execution, Git, Deployment, Prompt
  Engineering, Model Routing)을 다뤘는가 — **아니오**.
- 미해결 사실을 정직하게 남겼는가 — **Pass**. Event Bus(§4.5)는 실증
  Observation이 없다는 사실을 숨기지 않고 명시했다.
