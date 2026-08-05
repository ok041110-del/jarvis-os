# Jarvis OS Platform — Architecture Freeze v1.0

날짜: 2026-08-03
근거: `docs/architecture-review/architecture-review-v1.md` (Repository Architecture Review, 사용자 공식 승인)
main 기준 commit: `6d957e5`

---

## 목적 (왜 Freeze를 하는가)

Phase 1~5가 Jarvis OS Platform의 핵심 Architecture Claim — "Core는 구체 기술을 모르고,
어떤 Adapter든 교체 가능하다" — 을 5개 Domain(Lifecycle/Capability/Policy/Connector/
Workflow) 전부에서 코드와 테스트로 반복 실증했다. Repository Architecture Review가
ADR 일관성, Layer Dependency, Dependency Rule, Core 순수성, Adapter Reversibility에
위반 사항이 없음을 확인했고, 사용자가 이 결과를 근거로 v1.0을 공식 승인했다.

이 시점부터 실제 업무 조직(Development HQ, Investment HQ, Personal HQ, Research HQ 등)의
비즈니스 로직 개발이 시작된다. Application Layer 개발은 Platform Architecture를 계속
재검증하는 작업이 아니라 그 위에 짓는 작업이어야 한다 — 그러려면 "지금 검증된 구조가
Application 개발 중에 조용히 무너지지 않는다"는 보장이 필요하다. Freeze는 그 보장의
형식이다: **Application Layer 개발 중에는 Platform Architecture를 손대지 않는다.**

Freeze는 "더 이상 개선하지 않는다"는 뜻이 아니라 "임의로 바꾸지 않는다"는 뜻이다.
정당한 변경 경로(§Freeze 해제 조건)는 여전히 열려 있다.

---

## Freeze 대상

다음 항목은 v1.0 시점의 상태로 고정되며, 통상적인 Application 개발 과정에서 수정되지
않는다.

- **Layer**: `packages/` (Core) → `adapters/` (Adapter) → `hqs/` + `apps/` (Composition
  Root/HQ) 3단 구조.
- **Package**: 현재 14개 workspace 패키지(`packages/core`, `packages/shared`, adapter
  10개, `hqs/development-hq`, `hqs/investment-hq`, `apps/poc-runner`)의 존재와 경계.
  새 HQ/Adapter *패키지*를 추가하는 것은 Freeze 대상이 아니다(§변경 가능한 영역) —
  Freeze 대상은 기존 패키지의 책임 경계다.
- **Dependency Rule**: `Adapter/HQ/App → Core → Shared` 단방향 의존. Core가 어떤
  외부 프레임워크도 직접 import하지 않는다는 규칙.
- **ADR-0003~ADR-0007**: Domain Port Definition & Adapter Reversibility Principles,
  Capability Registration Model, Policy Decision Model, Connector Execution Model,
  Workflow Execution Model. 이 5개 ADR이 규정한 결정 사항(Registry 분리 원칙, Fail-Closed
  계약, Workflow Registry 미도입 등)은 그대로 유지된다.
- **Core Ports**: `i_lifecycle_runtime.py`, `i_capability_provider.py`,
  `i_capability_store.py`, `i_policy_engine.py`, `i_connector.py`,
  `i_connector_discovery.py`, `i_workflow_engine.py`의 현재 시그니처와 계약(Fail-Closed,
  반환 타입).
- **Registry 구조**: HQ Capability Registry(`capability_registry/`)와 Connector
  Registry(`connector_registry/`)가 서로 완전히 분리된 별도 Domain이라는 원칙. Workflow는
  Registry/Discovery를 갖지 않는다는 원칙(ADR-0007 결정 12).
- **Adapter 구조**: 각 Domain이 최소 1개의 실사용 Adapter + Adapter Reversibility 증명용
  대조 Adapter를 갖는 패턴, Composition Root(`apps/poc-runner`)만 구체 Adapter를 아는
  구조.

---

## 변경 가능한 영역

Application Layer 개발은 아래 영역에서 자유롭게 이루어진다 — 이는 Platform Architecture를
바꾸는 것이 아니라 그 위에서 실제 조직을 짓는 것이다.

- **HQ 구현**: `hqs/development-hq`, `hqs/investment-hq`의 실제 Capability 목록, Division
  구성, Capability YAML 내용. 새로운 HQ(Personal HQ, Research HQ 등) 패키지를 추가하는 것.
- **Agent 구현**: 각 Division의 `agent_catalog`, Agent의 `required_tools` 내용(단,
  `Agent.required_tools`를 실제로 채우는 *메커니즘* 자체 — HQProvisioner의 절차 —
  는 Application 개발이 아니라 별도 ADR이 필요한 Platform 변경이다. 이미 채워진 필드에
  실제 값을 넣는 것은 Application 작업, 그 필드를 채우는 로직 자체를 새로 만드는 것은
  Architecture 작업이라는 구분에 유의).
- **Tool 구현**: 새 Connector Adapter를 추가하는 것(entry point로 자동 Discovery됨),
  기존 Connector의 실제 Tool 목록/동작.
- **Workflow 내용**: 특정 HQ/Division이 어떤 순서로 Agent를 실행할지의 실제 데이터
  (`Team.agents` 구성 등). `IWorkflowEngine`의 계약 자체는 Freeze 대상이지만, 그 계약
  위에서 실행되는 실제 Team 구성은 자유롭다.

---

## 변경 불가능한 영역

아래는 Application 개발 중 어떤 이유로도 그냥 수정하지 않는다 — §Freeze 해제 조건을
반드시 거쳐야 한다.

- **Layer 구조**: Core/Adapter/HQ/Composition Root 4단 구분 자체.
- **Dependency Rule**: 의존 방향의 역전(Core가 Adapter나 HQ를 아는 것), Core의
  외부 프레임워크 직접 의존.
- **Hexagonal Architecture**: Port 없이 Adapter를 직접 호출하는 구조, Composition Root
  외의 위치에서 구체 Adapter를 조립하는 것.
- **Core Port 계약**: 기존 Port의 메서드 시그니처 변경, 반환 타입 변경, Fail-Closed
  계약 파기(예외를 던지도록 바꾸는 것).

---

## Freeze 해제 조건

다음 중 하나가 충족되어야만 v1.1 이상에서 위 "변경 불가능한 영역"을 수정할 수 있다.

1. **Architecture Review** — Repository 전체 관점의 재평가를 수행하고 그 결과를 문서로
   남긴 뒤 사용자 승인을 받는다 (이번 `architecture-review-v1.md`와 동일한 형식).
2. **ADR 승인** — 변경하려는 범위에 대한 ADR을 작성하고(배경/결정/근거/기각 대안/영향
   범위/DoD 포함), 사용자 승인을 받는다.
3. **Breaking Change 승인** — 위 두 절차를 생략해야 할 만큼 긴급한 상황이라면, 무엇이
   왜 깨지는지와 대안이 없는 이유를 명시적으로 보고하고 사용자의 개별 승인을 받는다.

셋 중 어느 경로든, **먼저 구현을 멈추고 문서를 작성한 뒤에만 진행한다** — 이는 Phase
1~5 전체에서 이미 지켜진 원칙("Architecture 변경이 필요한 상황이 발생하면 즉시 구현을
중단하고 ADR을 먼저 작성한다")의 연장이다.
