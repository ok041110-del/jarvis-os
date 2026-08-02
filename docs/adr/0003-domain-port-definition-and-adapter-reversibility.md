# ADR-0003: Domain Port Definition & Adapter Reversibility Principles

날짜: 2026-08-02
상태: Accepted

## 배경 (Context)
Phase 1(Lifecycle Adapter, python-statemachine)을 시작하려면 현재 완전히 비어있는
`packages/core/src/jarvis_core/ports/i_lifecycle_runtime.py`(docstring뿐, ABC 없음)
에 최초의 실제 인터페이스를 정의해야 한다.

Architecture v1.0은 현재 Frozen 상태이며, "Core와 Interface는 임의로 변경하지 않는다"는
원칙을 가지고 있다. 따라서 빈 Port 파일에 최초로 코드를 작성하는 행위가 Architecture
변경인지, 아니면 설계상 예정된 확장인지 먼저 정의할 필요가 있다.

또한 이 인터페이스를 (a) python-statemachine 전용 인터페이스로 설계할 것인지, 아니면
(b) Lifecycle이라는 도메인 자체의 인터페이스로 설계할 것인지 결정해야 한다. 후자의
방식이어야 향후 다른 FSM 구현체나 분산 Runtime으로 교체하더라도 Core를 수정하지 않을
수 있다.

이 ADR은 Lifecycle뿐 아니라 앞으로 생성될 모든 Port에 적용되는 공통 원칙을 정의한다.

## 결정 (Decision)

### 결정 1 — 빈 Port에 최초 ABC를 정의하는 것은 Core 변경이 아니라 설계도상 예정된 확장으로 취급한다.
`i_lifecycle_runtime.py`는 docstring에서 이미 "Adapter가 구현할 Port"임을 명시하고
있었다. 따라서 최초의 ABC를 정의하는 것은 새로운 기능을 추가하는 것이 아니라 이미
존재하던 설계 계약을 코드로 명시하는 작업이다. 이 원칙은 앞으로 `i_workflow_engine.py`,
`i_capability_store.py`, 기타 Port에도 동일하게 적용한다.

### 결정 2 — Port는 특정 라이브러리의 인터페이스가 아니라 Domain Interface이다.
`LifecycleRuntime`은 python-statemachine을 위한 인터페이스가 아니다. Lifecycle이라는
도메인을 표현하는 인터페이스이다. 따라서 메서드 이름, 반환 타입, 예외 모두 Domain
Language만 사용한다.

- 사용 가능: `HQState`, `TransitionDenied`
- 사용 불가: `StateMachine`, `State`, `Transition` 데코레이터 등 특정 라이브러리 타입

```python
from abc import ABC, abstractmethod
from jarvis_core.lifecycle.hq_state import HQState

class LifecycleRuntime(ABC):
    @property
    @abstractmethod
    def current_state(self) -> HQState:
        ...

    @abstractmethod
    def transition(
        self,
        target: HQState,
        *,
        triggered_by_human: bool = False,
    ) -> HQState:
        ...

    @abstractmethod
    def is_discoverable(self) -> bool:
        ...
```

### 결정 3 — Guard Rule은 Core가 단일 진실 공급원(Single Source of Truth)이다.
Adapter는 Guard를 재구현하지 않는다. Adapter는 `jarvis_core.lifecycle.hq_state.transition()`
을 호출하여 Core가 판단한 결과를 그대로 사용한다. 따라서 허용된 Transition, Disabled →
Idle 재활성화 조건, Discoverable 여부는 모두 Core가 유일하게 판단한다. Adapter는 실행
엔진(FSM Runtime) 역할만 수행한다.

### 결정 4 — Core는 Adapter의 존재를 추론하거나 구현체에 따라 분기해서는 안 된다.
Core는 `LifecycleRuntime`이라는 Port만 안다. 현재 연결된 구현체가 python-statemachine,
Mock Runtime, InMemory Runtime, Distributed Runtime, Cloud Runtime 중 무엇인지 절대로
판단하거나 분기해서는 안 된다. Adapter 선택은 Composition Root(`apps/`)에서만 이루어진다.
Core는 Dependency Injection으로 전달받은 Port만 사용한다. 이는 Jarvis OS 전체의
Hexagonal Architecture 원칙이다.

### 결정 5 — 모든 Adapter는 가역적(Replaceable)이어야 한다.
새 Adapter를 제거하고 기존 Adapter를 연결했을 때, Core를 수정하지 않고 원래 상태로
즉시 복구 가능해야 한다. 이 조건을 만족하지 못하면 Adapter가 아니라 Core Extension으로
간주한다. 이 원칙은 Lifecycle, Policy, Workflow, MCP, Memory, Scheduler 등 모든 Adapter에
동일하게 적용한다.

## Definition of Done 추가 (모든 Adapter Phase 공통)
모든 Adapter Phase는 아래 조건을 반드시 만족해야 한다.

- Adapter 설치 성공
- 기존 테스트 통과
- 신규 Integration Test 통과
- Core 수정 없음
- Repository Health Report 제출
- ADR 업데이트 완료

그리고 반드시 아래 항목을 추가한다.

**Architecture Validation**: 새 Adapter를 제거하고 기존 Adapter를 연결했을 때, Core
수정 없이 즉시 원상 복구 가능함을 증명한다.

## 근거 (Rationale)
Jarvis OS는 Hexagonal Architecture를 기반으로 한다. Hexagonal Architecture의 핵심은
Core가 외부 기술을 모르는 것이다. 또한 Composition Root Pattern을 적용하여 구현체
선택은 `apps/`에서만 수행한다. Core는 Port만 알고 Adapter를 모른다. Adapter는 Port를
구현할 뿐이다.

또한 Guard Rule을 Core 하나에만 두면 중복 구현, Drift, 버그를 방지할 수 있다. Adapter는
실행 엔진만 담당하는 얇은 Layer("Build Thin")가 된다.

## 기각된 대안 (Rejected Alternatives)

**대안 A** — `LifecycleRuntime`을 python-statemachine 인터페이스 그대로 정의.
기각 이유: Core가 특정 라이브러리에 의존하게 된다. Hexagonal Architecture 위반.

**대안 B** — Guard Rule을 Adapter가 직접 구현.
기각 이유: Core와 Adapter에 동일한 Rule이 존재하게 되어 Rule Drift가 발생한다.

**대안 C** — Core가 Adapter 종류를 확인하여 분기(예: `if runtime is PythonStateMachine:`).
기각 이유: Core가 구현체를 알게 되어 Dependency Inversion 원칙 위반.

## 영향 범위 (Impact)
이번 Phase에서는 `i_lifecycle_runtime.py`와 `lifecycle-statemachine` adapter에 직접
적용한다.

또한 앞으로 생성되는 모든 Port의 기본 원칙으로 사용한다: `IPolicyEngine`,
`IWorkflowEngine`, `IConnector`, `IMemoryStore`, `IScheduler`, `ICapabilityProvider`,
향후 추가되는 모든 Domain Port.

Phase 5(Workflow Engine)에서도 별도 ADR 없이 본 ADR을 근거로 동일 원칙을 적용한다.

## 향후 적용
본 ADR은 Jarvis OS 전체의 Port / Adapter 설계 기준 문서이다. 향후 모든 Adapter ADR은
본 문서를 상위 ADR로 인용한다.
