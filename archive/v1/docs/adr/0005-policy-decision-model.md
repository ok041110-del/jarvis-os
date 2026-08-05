# ADR-0005: Policy Decision Model

- 날짜: 2026-08-03
- 상태: **Accepted**

---

## 배경 (Context)

Phase 3(Policy Adapter — Casbin)에 착수하기 전, `docs/architecture/v1.0/04-policy-engine.md`가
정의한 PDP/PEP 모델과 Tier 모델을 실제 코드(`packages/core/src/jarvis_core/policy/models.py`,
`ports/i_policy_engine.py`, `kernel/hq_selection.py`)와 대조했다.

현재 코드 상태:

1. `IPolicyEngine.evaluate(request) -> PolicyDecision`이 이미 Port로 존재하고,
   `kernel/hq_selection.py`가 유일한 PEP 호출 지점으로 이를 사용 중이다.
2. `PolicyTier`(TIER1_ABSOLUTE/TIER2_RESOURCE/TIER3_OPTIMIZE)가 이미 Core Domain
   Model로 정의되어 있으나, 실제로 구현되고 평가되는 것은 Permission Policy(Tier 1)
   하나뿐이다. Budget/Wake-up/Priority 등 04-policy-engine.md가 설계한 나머지 정책
   종류는 아직 코드로 존재하지 않는다.
3. `adapters/policy-casbin/.../casbin_policy_engine.py`는 docstring만 있고 구현이
   비어 있다 — Phase 3가 채워야 할 대상.
4. Policy Engine 호출이 실패(어댑터 예외, 설정 누락 등)했을 때 무엇을 해야 하는지는
   어디에도 정의되어 있지 않다 — 04-policy-engine.md는 "거부(Deny)"와 "정책이 없어서
   평가 자체가 안 되는 상황"을 구분하지 않았다.

이 ADR은 위 격차 중 **Phase 3에 실제로 영향을 주는 부분**(Policy Engine 책임 범위,
PDP/PEP 경계, Tier 모델의 PoC 적용 범위, Failure Policy, Policy/Domain 경계,
Casbin의 위치)을 코드 수준 결정으로 확정한다. 04-policy-engine.md 전체(9종 정책,
5단계 체크포인트)를 지금 전부 구현하는 것은 아니다 — 그건 v1.1 이후 범위다.

## 결정 (Decision)

### 결정 1 — Policy Engine(PDP)의 책임은 "허용/거부 판단"으로 한정한다

Policy Engine은 `PolicyRequest`를 받아 `PolicyDecision`을 반환하는 것 외에 아무것도
하지 않는다. Policy Engine은:

- 대상을 라우팅하지 않는다 (Kernel의 책임, ADR 대상 아님 — 04-policy-engine.md §3-1)
- 실행하지 않는다 (Organization Layer의 책임)
- 상태를 변경하지 않는다 (HQ Lifecycle, Capability Registry 어느 쪽도 쓰지 않음 —
  Query만 존재, Command 없음)

PoC(Phase 3) 범위는 04-policy-engine.md 1장의 9종 정책 중 **Permission Policy(Tier 1)
하나만** 구현한다. Security/Budget/Wake-up/Retry/Priority/Escalation/Isolation/Audit은
`PolicyTier` enum과 `docs/architecture/v1.0/04-policy-engine.md`에 설계만 존재하는
상태를 유지하며, v1.1 이후 OPA 전환 시점에 확장한다(ADR-0001의 ADR-003 재확인).

### 결정 2 — PEP는 판단을 재구현하지 않고, 판단을 요청하고 그 결과만 집행한다

PDP(Policy Engine)와 PEP(호출 지점)의 경계는 다음과 같이 고정한다.

- **PDP**: `IPolicyEngine` 구현체 단 하나의 권위. "허용되는가"의 유일한 판단 주체.
- **PEP**: `IPolicyEngine.evaluate()`를 호출하고 반환된 `PolicyDecision.allow`만
  보고 진행/중단을 결정하는 지점. PEP는 **자체적으로 권한 규칙을 다시 판단하지
  않는다** — Guard Rule을 Core(`hq_state`)에 두고 Adapter는 실행만 하는 ADR-0003
  결정 3과 동일한 원리다.

현재 유일한 PEP는 `kernel/hq_selection.py`이다. 04-policy-engine.md가 설계한
"Division→Team", "Team→Agent", "Agent→MCP" 지점의 PEP는 아직 코드에 존재하지
않으므로 이번 ADR의 구현 범위에 포함하지 않는다 — 다만 그 지점들이 생길 때도
"자체 규칙을 만들지 않고 동일한 `IPolicyEngine`을 호출한다"는 원칙은 지금
이 ADR로 고정해 둔다.

### 결정 3 — Tier 1/2/3 모델은 Core Domain Model로 유지하되, PoC는 Tier 1만 평가한다

`PolicyTier`(`packages/core/.../policy/models.py`)는 이미 Core에 있고 변경하지
않는다. 이 ADR은 다음을 명시적으로 확정한다.

- Tier는 **Adapter가 정하는 것이 아니라 Core가 정의한 분류**다. Casbin이든 OPA든
  "이 정책이 몇 티어인지"를 스스로 판단하지 않는다 — 호출하는 PEP(현재는
  `hq_selection.py`)가 어떤 종류의 정책을 묻는지 알고 있고, 그 정책 종류에 대응하는
  Tier는 Core 상수로 고정된다. PoC 범위(Permission Policy)는 항상 `TIER1_ABSOLUTE`다.
- Tier 1 거부는 하드 게이트다 — 즉시 중단, 대안 없음(04-policy-engine.md 4-1).
  `hq_selection.py`는 이미 이 규칙대로 동작한다(Tier 1 거부 시 해당 후보를 즉시
  포기하고 하위 후보로 넘어감). 이번 ADR로 이 동작이 "구현 우연"이 아니라
  "확정된 결정"임을 문서화한다.
- Tier 2/3(Budget/Wake-up/Priority 등)은 PoC 범위 밖이며, 이번 Phase에서
  `PolicyRequest`/`PolicyDecision` 스키마를 확장하지 않는다.

### 결정 4 — Failure Policy: Policy Engine Adapter는 예외를 던지지 않는다 (Fail-Closed)

지금까지 정의되지 않았던 부분이다. Policy Engine 호출이 내부적으로 실패할 수 있는
경우(정책 파일 파싱 실패, 백엔드 연결 불가 등)를 아래처럼 확정한다.

- **`IPolicyEngine.evaluate()`는 예외를 던지지 않는다.** 이것은 Domain Interface의
  계약(Contract)이다. Adapter 내부에서 어떤 예외가 발생하든, Adapter는 이를 잡아서
  `PolicyDecision(allow=False, tier=TIER1_ABSOLUTE, reason="policy engine internal
  error: ...")`로 변환해 반환해야 한다.
- **이유**: PEP(`hq_selection.py`)가 매 호출마다 `try/except`로 Policy Engine 오류를
  방어하게 만들면, Core가 "Adapter가 예외를 던질 수 있다"는 구현 디테일을 알아야
  한다. 이는 ADR-0003 결정 4(Core는 Adapter의 존재나 구현 방식을 추론/분기하지
  않는다) 위반이다. 대신 계약 자체를 "항상 값을 반환한다"로 고정하면 PEP 코드는
  그대로 유지된다.
- **Fail-Closed을 선택한 이유**: Fail-Open(오류 시 허용)은 Permission Policy의
  존재 목적 자체를 무력화한다. 정책 판단이 불가능한 상황은 "판단 안 함"이 아니라
  "가장 엄격한 판단(거부)"으로 취급한다 — No Silent Failure 원칙(Request Processing
  Kernel v1)의 연장선이다. 거부 사유(`reason`)에 내부 오류임을 명시해 사용자에게
  "권한이 없어서"가 아니라 "정책 엔진 오류로 판단 불가"임이 감사 로그에 구분되어
  남도록 한다.
- 이 계약은 `IPolicyEngine`의 docstring에 명시하고, 모든 구현체(Casbin/InMemory/
  향후 OPA)가 이를 따르는지 계약 테스트(Contract Test)로 검증한다.

### 결정 5 — Policy와 Domain의 경계

- **Core에 속하는 것**: `PolicyRequest`, `PolicyDecision`, `PolicyTier` — 이 세
  타입과 Tier 분류 규칙(어떤 정책 종류가 몇 티어인지)은 Core Domain Model이다.
  어떤 정책 엔진 구현체를 쓰든 이 스키마는 바뀌지 않는다.
- **Adapter에 속하는 것**: 정책을 어떻게 저장하고 어떻게 매칭 규칙을 평가하는지의
  전부. Casbin이라면 RBAC 모델 정의(`model.conf`)와 정책 데이터(`policy.csv` 또는
  동등한 소스)가 여기 속한다. Core는 이 파일들의 존재도, 문법도 모른다.
- **PoC에서 의도적으로 남겨둔 단순화**: `PolicyRequest`에는 아직 `tier` 필드가 없다
  (PDP가 반환하는 `PolicyDecision`에만 `tier`가 있다). 이는 PoC가 Permission Policy
  하나만 다루므로 "이 요청이 어떤 정책 종류를 묻는지"를 구분할 필요가 아직 없기
  때문이다. Tier 2/3 정책이 추가되는 시점(v1.1)에는 `PolicyRequest`에 정책 종류를
  구분하는 필드가 필요해질 수 있으며, 이는 그 시점의 별도 ADR 대상이다 — 지금
  미리 설계하지 않는다(YAGNI, Capability Registry Phase 2에서 확인된 "Division/Agent
  YAML화는 별도 Phase" 원칙과 동일).

### 결정 6 — Casbin의 위치: Policy 구현체이지 Architecture가 아니다

- Casbin은 `IPolicyEngine`의 구현체 중 하나다. Architecture v1.0과 04-policy-engine.md
  어디에도 "Casbin"이라는 단어는 Architecture 결정으로 등장하지 않는다 — PDP/PEP
  모델, Tier 모델, Failure Policy가 Architecture이고, Casbin은 그 Architecture를
  PoC 단계에서 만족시키는 하나의 선택(ADR-0001의 ADR-003)일 뿐이다.
- 이 ADR로 확정하는 Adapter Reversibility 조건(ADR-0003 결정 5 재적용): Casbin
  Adapter를 제거하고 `adapters/policy-inmemory`(또는 향후 `adapters/policy-opa`)로
  교체해도 `packages/core`와 `packages/core/.../kernel/hq_selection.py`는 단 한 줄도
  수정하지 않는다. 교체는 `apps/poc-runner`(Composition Root)의 import 한 줄과
  `pyproject.toml`의 의존성 한 줄로 끝나야 한다.
- Casbin의 RBAC 모델(`model.conf`)이 표현하는 "subject가 resource에 대해 action을
  할 수 있는가"라는 문법은 Casbin의 언어이지 Jarvis OS의 Domain Language가 아니다.
  Adapter 내부에서만 사용하고, `PolicyRequest`/`PolicyDecision`으로 변환하는 지점
  (Adapter의 `evaluate()` 메서드)이 Casbin 문법과 Domain Language의 유일한 경계다.

## 근거 (Rationale)

ADR-0003(Domain Port / Dependency Inversion / Adapter Reversibility)과 ADR-0004
(Capability Registration — Registry/Provider 책임 분리, Composition Root는 연결만
한다)의 원칙을 Policy Engine에 동일하게 적용한 것이다. Failure Policy(결정 4)는
이번 ADR에서 새로 확정하는 원칙으로, 향후 모든 Port(특히 외부 시스템에 의존하는
Adapter — MCP Connector, Workflow Engine)에도 "Adapter는 예외를 삼키고 Domain
값으로 변환해 반환한다"는 동일 패턴을 적용할 근거가 된다.

## 기각된 대안 (Rejected Alternatives)

- **대안 A**: 04-policy-engine.md의 9종 정책과 5단계 체크포인트를 Phase 3에서 전부
  구현한다. 기각 — PoC의 Architecture Validation 목표는 "Casbin을 교체해도 Core가
  안 바뀐다"는 것이지 "9종 정책을 다 만든다"가 아니다. 범위 과다는 검증을 오히려
  지연시킨다(ADR-0004 대안 C와 동일한 논리 — Division/Agent YAML화를 Phase 2에서
  기각한 것과 같은 이유).
- **대안 B**: Policy Engine 오류 시 Fail-Open(허용). 기각 — Permission Policy의
  존재 이유를 무력화하고, No Silent Failure 원칙과 정면 충돌.
- **대안 C**: PEP(`hq_selection.py`)가 `try/except`로 Adapter 예외를 방어한다.
  기각 — Core가 "Adapter는 예외를 던질 수 있다"는 구현 디테일을 알아야 하므로
  ADR-0003 결정 4 위반. 계약(예외 없음)을 Adapter 쪽에 고정하는 것이 Core를
  더 얇게 유지한다.
- **대안 D**: `PolicyRequest`에 지금 `tier` 필드를 미리 추가해 둔다. 기각 —
  PoC 범위(Permission만)에서는 쓰이지 않는 필드이며, Tier 2/3 설계가 확정되지
  않은 채 스키마를 먼저 넓히면 잘못된 형태로 고정될 위험이 있다(YAGNI).

## 영향 범위 (Impact)

- 무수정: `packages/core/.../policy/models.py`, `packages/core/.../kernel/hq_selection.py`
  (이번 ADR은 기존 동작을 재확인/문서화하는 것이지 스키마나 로직을 바꾸지 않는다)
- 수정 예정(Phase 3 구현 대상): `packages/core/.../ports/i_policy_engine.py`
  docstring에 Fail-Closed 계약 명시, `adapters/policy-casbin`(신규 구현),
  `apps/poc-runner`(Composition Root 배선 교체)
- 신규 테스트: Policy Adapter 계약 테스트(예외 미던짐 + Fail-Closed 검증을
  Casbin/InMemory 양쪽에 동일하게 적용) + Adapter Reversibility 통합 테스트

## Definition of Done

ADR-0003 공통 DoD에 더해 다음을 모두 만족한다.

- Casbin Adapter가 `hq_selection.py`의 기존 Permission 시나리오(시나리오 D — 낮은
  권한 세션이 restricted Capability를 요청 시 거부)를 InMemory Adapter와 동일하게
  판정한다.
- Casbin Adapter를 제거하고 InMemory Adapter로 되돌렸을 때 Core/Kernel 무수정으로
  즉시 복구 가능함을 통합 테스트로 증명한다(Adapter Reversibility).
- Policy Engine 내부 오류를 강제로 유발했을 때 `IPolicyEngine.evaluate()`가 예외를
  던지지 않고 `PolicyDecision(allow=False, ...)`을 반환함을 계약 테스트로 증명한다.

## 향후 적용

본 ADR은 Jarvis OS의 Policy Decision Model(PDP/PEP 경계, Tier 분류, Failure Policy)의
기준 문서다. v1.1에서 OPA로 전환하거나 Tier 2/3(Budget/Wake-up/Priority 등) 정책을
추가할 때, 그리고 향후 Division→Team/Team→Agent/Agent→MCP 지점에 새로운 PEP를
추가할 때 모두 본 ADR을 상위 원칙으로 인용한다.
