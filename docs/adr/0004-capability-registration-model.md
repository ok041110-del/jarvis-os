# ADR-0004: Capability Registration Model

- 날짜: 2026-08-02
- 상태: **Accepted**

---

## 배경 (Context)

Phase 2(Capability YAML Loader)는 ADR-0002가 기록한 Known Gap인
"`capabilities.yaml`이 런타임에 로드되지 않고 `main.py`에 하드코딩되어 있다."
를 해결하는 것이 목적이다.

이번 Phase의 Architecture Validation 목표는

> 새로운 HQ를 코드 수정 없이 추가하거나 제거할 수 있는 구조를 증명하는 것

이다.

코드 조사 결과 다음 두 가지가 확인되었다.

1. `CapabilityRegistry`는 순수 Capability Catalog와 Matching Engine 역할만 수행한다.
   파일 시스템 / YAML / Lifecycle / HQ Discovery를 전혀 알지 않는다. 현재 책임
   분리는 올바르며 유지한다.
2. 현재 어떤 HQ도 실제 Provisioning 과정을 거치지 않는다. `main.py`가 이미 생성
   완료된 HQ를 직접 하드코딩하고 있다. Architecture 문서의 "HQ가 자신의
   Capability를 선언한다."는 설계는 아직 실제 코드에서 증명되지 않았다.

## 결정 (Decision)

### 결정 1 — Capability Registry의 책임

`CapabilityRegistry`는 Capability Catalog와 Matching Engine으로만 유지한다.
`CapabilityRegistry`는 YAML / File I/O / HQ Discovery / Lifecycle을 절대 알지
않는다. Phase 2에서도 `packages/core/.../capability_registry/`는 수정하지
않는다. Lifecycle 가시성 판단은 계속 Kernel(Stage 5)의 책임으로 유지한다.

### 결정 2 — Capability Provider는 Discovery와 Parsing만 담당한다

새로운 Domain Port를 정의한다.

```python
class ICapabilityProvider(ABC):
    @abstractmethod
    def load(self) -> list[Capability]:
        ...
```

Provider의 책임은 Capability를 발견하고 Capability 객체를 생성하는 것까지이다.
Registry 등록 / HQ 생성 / Lifecycle / Kernel은 담당하지 않는다.

Provider는 YAML / Database / Remote Registry / Marketplace 등 어떤 Source라도
구현 가능해야 한다. PoC에서는 YAML Provider를 기본 구현으로 사용한다.

### 결정 3 — HQ는 Provisioning 단계에서 자신의 Capability를 선언한다

Provisioning 단계에서 Provider가 반환한 Capability를 Registry에 등록한다.
등록 성공 시 `Provisioning → Idle`, 등록 실패 시 `Provisioning → Error`로
전이한다.

### 결정 4 — Provisioning → Idle 전환 조건

다음 조건을 모두 만족해야 한다.

- YAML Parsing 성공
- Capability ID 중복 없음
- Owner가 HQ ID와 일치

실패 시 `Provisioning → Error`로 전이한다. 잘못된 Capability는 절대 자동으로
무시하지 않는다. No Silent Failure 원칙을 따른다.

### 결정 5 — Registry와 Lifecycle은 서로 독립이다

Registry는 Lifecycle을 모른다. Lifecycle은 Registry를 모른다. 둘의 연결은
Composition Root에서만 수행한다. Registry와 Lifecycle 사이에 직접 참조 /
Callback / Observer를 만들지 않는다.

### 결정 6 — Composition Root의 책임

Composition Root는 다음 순서만 수행한다.

```
Capability Provider 호출
  → Capability 목록 획득
  → HQ Provisioning
  → Registry 등록
  → Idle 또는 Error 전이
```

Composition Root는 Capability 내용을 해석하지 않는다. 단순히 각 Domain을
연결하는 역할만 수행한다.

### 결정 7 — HQ Discovery는 구현 방식과 분리한다

Architecture가 요구하는 것은 "새 HQ를 코드 수정 없이 자동 발견할 수 있어야
한다."이다. Discovery 구현 방식은 Architecture의 일부가 아니다.

PoC에서는 Python Entry Point를 기본 Discovery 방식으로 사용한다. 하지만
향후 Filesystem / Manifest / Plugin Registry / Remote Registry 등 다른
Discovery 방식으로 교체 가능해야 한다. Discovery는 Adapter 책임이며 Core는
Discovery 방식을 알지 못한다.

## 근거 (Rationale)

ADR-0003의 Domain Port / Dependency Inversion / Adapter Reversibility 원칙을
그대로 따른다. 또한 Composition Root Pattern을 유지하여 구현체 선택은
`apps/`에서만 수행한다.

Capability Registry는 Capability를 저장하고 검색하는 Domain 역할만 수행한다.
Capability Discovery는 Provider가 담당한다. Registry와 Provider를 분리함으로써
파일 시스템 / DB / Remote / Plugin 등 Discovery 방식이 바뀌어도 Core는
변경되지 않는다.

## 기각된 대안 (Rejected Alternatives)

- **대안 A**: Registry가 직접 YAML을 읽는다. 기각 — Registry에 File I/O가
  포함된다. Hexagonal Architecture 위반.
- **대안 B**: Filesystem 경로를 직접 탐색한다. 기각 — Repository 구조에
  결합된다. PoC에서는 Entry Point를 사용하지만 Discovery 방식은 언제든
  교체 가능해야 한다.
- **대안 C**: Division과 Agent까지 이번 Phase에서 YAML화한다. 기각 — 이번
  Phase 목표는 HQ Discovery와 Capability Registration이다. Division과
  Agent는 별도 Phase에서 다룬다.

## 영향 범위 (Impact)

- 추가: `ICapabilityProvider` (신규 Port), `adapters/capability-provider-yaml`
  (신규 Adapter)
- 수정: `apps/poc-runner`
- 무수정: Capability Registry, Kernel
- 향후: Database Provider / Marketplace Provider / Remote Provider 등도 동일
  Port를 구현한다.

## Definition of Done

ADR-0003 공통 DoD에 더해 다음을 모두 만족한다.

- 새 HQ를 추가한다 → Core 수정 없음 → Kernel 수정 없음 → Registry 수정 없음
  → 자동 Discovery → 자동 Registration → Routing 성공
- HQ 하나를 제거한다 → Core 수정 없음 → Kernel 수정 없음 → Repository 정상
  실행 → 나머지 HQ 정상 Routing
- Provider 구현을 제거하고 기존 Mock Provider로 교체해도 Core 수정 없이
  동작한다 (Adapter Reversibility).

## 향후 적용

본 ADR은 Jarvis OS의 Capability Discovery / Capability Registration / Plugin
HQ 구조의 기준 문서이다. 향후 Database Provider / Marketplace Provider /
Remote Provider 등 모든 Capability Provider는 본 ADR을 상위 원칙으로 인용한다.
