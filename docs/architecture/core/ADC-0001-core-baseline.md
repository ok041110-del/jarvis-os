# ADC-0001: Kernel Baseline Module 채택 판단 (RFC-0001 후속)

## 목적

`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`가 정리한 5개
Kernel Module 후보 — Governance, Workflow, Memory, Execution Layer, Event Bus
— 를 **개별적으로** 판단한다. Kernel 전체를 일괄 승인하지 않는다.

이 문서는 구현 방법이나 설계를 제안하지 않는다. 근거는 Development HQ가
Phase 1(MVP-0001~0013) 동안 **실제로 반복 관찰한 사실**과, RFC-0001이
인용한 Frozen 문서(`BASELINE.md`)의 실제 문구로만 한정한다. "필요할 것
같다"는 추측은 근거로 사용하지 않는다.

각 Module의 Decision은 다음 4개 중 하나다: **Accept / Defer / Reject / Out
of Authority**.

---

## Module 1. Governance

### Evidence

- `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`가 정의한 `RFC → ADC →
  ADR → Baseline Update` 절차가, Development HQ 수준에서 **실제로 5회
  완결**되었다: RFC-0001→ADC-0001, RFC-0002→(ADC-0002), RFC-0003→ADC-0003→
  ADR-0001(Baseline 반영까지 완료), RFC-0004→ADC-0004, RFC-0005(후속 ADC
  대기 중).
- Jarvis OS 수준에서도 동일한 절차가 `docs/03_adc/ADC.md`에 12개 Open
  Decision(ADC-01~12)으로 이미 운영되고 있다.
- RFC-0004는 이 절차 위에 "Rule A(RT Trigger 충족 → RFC 자동 개시)"라는
  규칙을 추가로 실측 적용했다 — 새 코드 실행 없이 기존 OBS 문서만으로
  RFC가 열렸다.
- 이 절차가 실행되는 동안 한 번도 절차 자체가 실패하거나 우회된 사례는
  없다(`ARCHITECTURE_GOVERNANCE.md`: "이 절차를 우회한 변경은 Baseline에
  반영되지 않는다"는 원칙이 실제로 지켜졌다).

### Decision

**Accept**

### Decision Rationale

Governance는 "필요할 것 같은" 미래 기능이 아니라, 이미 Jarvis OS 수준과
Development HQ 수준 양쪽에서 반복 실행되어 실패 없이 동작한 절차 그
자체다. Kernel Module로 채택하는 것은 새 메커니즘을 만드는 것이 아니라,
이미 검증된 절차를 Kernel Baseline 문서에 명시적으로 기록하는 것이다.

### Risks

Governance를 Kernel Module로 명시해도, 그 실행 주체(누가/무엇이 RFC/ADC/ADR
문서의 등록과 상태를 물리적으로 관리하는가)는 여전히 미정이다. 이 Accept는
"이 절차가 Kernel 수준 공통 기능이어야 한다"는 판단일 뿐, 그 구현 방식을
결정하지 않는다.

### Next Step

ADR Required

---

## Module 2. Workflow

### Evidence

- `docs/governance/adc/ADC-0001.md` Candidate 1(Task Dispatcher):
  MVP-0001의 하드코딩된 순차 호출에 대해 **Keep in MVP** 결정. "승격을
  정당화할 반복 사용 사례나 일반화 압력이 MVP 안에서 관찰되지 않았다."
- `docs/governance/adc/ADC-0004.md`: MVP-0001→0002→0004로 체인이 3개까지
  늘어난 뒤 재평가했음에도 다시 **Keep in MVP**. Q1(실패 사례 있는가) —
  없음. Q2(다음 MVP를 막았는가) — 없음. Q3(일반화가 필요한 문제인가) —
  "단순한 형태 반복에 가깝다."
- `docs/research/EVIDENCE-REVIEW-0001.md`: MVP-0005~0008 4건에서도 동일한
  패턴(새 하드코딩된 순차 호출 파일 반복 추가)이 재확인되었고, 이 문서의
  Unknowns 절은 "추가된 체인 수가 RT-0001 Trigger를 새로 발동시키는지
  판단 불가"라고 명시했다 — 즉 Trigger 재충족 여부조차 확정되지 않았다.
- Development HQ Phase 1 전 구간(MVP-0001~0013)에서 Workflow 실행 실패,
  동적 분기 선택, 실행 시점 결정이 필요했던 사례는 한 번도 보고되지
  않았다.

### Decision

**Defer**

### Decision Rationale

Development HQ가 반복적으로(ADC-0001, ADC-0004 두 차례) 동일한 근거 —
실패 없음, 진행 차단 없음, 동적 일반화 필요성 미관찰 — 로 **Keep in
MVP**를 유지했다는 사실 자체가 이 Module에 대한 가장 직접적인 Evidence다.
`BASELINE.md` §6 Concept Model이 Workflow를 이미 정의해 두었다는 사실은
Module의 "존재 근거"는 되지만 "지금 Kernel Module로 확정할 근거"는 되지
못한다. 지금 Accept하면 "언젠가 필요할 것"이라는 추측에 근거하게 되며,
이는 이번 판단 기준이 명시적으로 금지한 방식이다. `docs/03_adc/ADC.md`의
ADC-02(Runtime 개념의 존폐)가 여전히 Open(우선순위 NOW)인 것도 같은
결론을 가리킨다.

### Risks

Defer를 유지하는 동안 RT-0001의 Trigger가 실제로 재충족되었는지(체인
수·분기·재시도 발생)를 판단할 별도 절차가 없다면, 재평가 시점 자체가
계속 불명확한 채로 남을 위험이 있다.

### Next Step

No ADR Required

---

## Module 3. Memory

### Evidence

- `docs/governance/adc/ADC-0001.md` Candidate 4(Context 전달 메커니즘):
  MVP-0001의 지역 변수 전달에 대해 **Keep in MVP** 결정. "승격을
  정당화할 전달 실패 사례가 MVP 안에서 관찰되지 않았다."
- `docs/research/EVIDENCE-REVIEW-0001.md` "Context 전달 방식" 절:
  MVP-0005/0006/0007/0008 네 건 모두 동일한 단일 경로(기존
  `issue["description"]` 문자열에 텍스트로 덧붙임)만 사용했고, 함수
  시그니처는 네 건 모두 변경되지 않았다. 별도 저장소나 영속화는 한 번도
  도입되지 않았다.
- 같은 문서의 Existing Governance Mapping 절: "MVP-0005~0008은 모두
  지역 변수/문자열 덧붙이기라는 동일한 단일 경로만 사용했으므로, 이
  Trigger(RT-0001 "Context 전달 경로 ≥ 2") 자체가 발동했는지는 이
  문서가 판단하지 않는다" — 즉 재평가 조건 충족 여부조차 아직
  확인되지 않았다.
- RFC-0001은 실행 실패·재시도 시나리오를 "관찰된 사실이 아니라 가설적
  시나리오"라고 명시적으로 표시했고, Phase 1 종료 시점까지 이 시나리오는
  실제로 관찰되지 않았다.

### Decision

**Defer**

### Decision Rationale

Memory도 Workflow와 동일한 구조의 Evidence를 가진다: 단일 전달 경로가
Phase 1 전 구간(MVP-0001, 0005~0008)에서 한 번도 실패하지 않았고, 승격을
정당화할 두 번째 경로나 영속화 필요 사례가 관찰된 적이 없다. `BASELINE.md`
§6이 Memory를 Service로 이미 정의해 둔 것은 Concept의 존재 근거일 뿐,
지금 Kernel Module로 확정할 근거가 아니다. 이번 판단 기준이 요구하는 "실제
반복 관찰"은 오히려 "아직 필요하지 않았다"는 방향으로 일관되게 나타난다.

### Risks

Defer를 유지하는 동안, Memory 부재로 인한 실패(실행 실패 후 재시도,
Context 유실)가 실제로 발생해도 이를 감지할 기준이 아직 없다. 이 공백은
RT-0001의 재평가 Trigger가 재정의되기 전까지 그대로 남는다.

### Next Step

No ADR Required

---

## Module 4. Execution Layer

### Evidence

- `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md` §1: Phase 1
  전 구간(MVP-0005~0013)에서 Development HQ의 모든 Capability는 문자열
  마커 매칭만으로 구현되었고, LLM/ML 호출은 **한 번도 추가되지
  않았다**(각 MVP Observation이 명시).
- 같은 RFC §2: Development HQ의 유일한 Engine 호출 지점(`call_engine()`)은
  MVP-0005~0013 전 구간에서 항상 규칙 기반 응답만 반환했고, 실제 LLM
  Engine으로 교체된 적이 없다.
- `development-hq/BOUNDARY.md`: "Engine 호출 — Kernel Engine
  Port/Adapter의 책임"이 Phase 1 시작 이전부터 이미 명시되어 있었고,
  `IMPLEMENTATION_RULES.md`: "Engine Gateway 구현 금지"가 Phase 1 내내
  지켜졌다.
- `BASELINE.md` §7: "Engine 호출의 표준 인터페이스 제공(Port/Adapter)"이
  Jarvis OS 책임으로 v1.0부터 Frozen 상태로 확정되어 있다.
- `docs/governance/adc/ADC-0003.md` 판단 4: Execution Layer의 Multi-Model
  지원을 Development HQ ADC 권한 밖(**Out of Authority**)으로 이미
  분리해 두었다 — 즉 Development HQ 수준에서는 이 판단을 내릴 수 없다는
  사실이 이미 별도로 확정되어 있다.

### Decision

**Accept**

### Decision Rationale

Execution Layer는 Workflow·Memory와 근본적으로 다른 종류의 Evidence를
가진다. Workflow/Memory는 "HQ 내부에서 하드코딩이 아직 무너지지 않았다"는
증거인 반면, Execution Layer는 "HQ가 Phase 1 전체 동안 이 기능을 단
한 번도 수행하지 않았다"는 증거다 — Development HQ 9개 MVP
(MVP-0005~0013) 전부가 일관되게 "규칙 기반 응답만 반환, LLM/ML 호출
없음"을 재확인했고, 이는 반복 관찰의 방향이 흔들린 적이 없다. 또한 이
경계는 Phase 1 시작 이전부터(`BOUNDARY.md`, `BASELINE.md` §7) 이미
Frozen 상태로 확정되어 있었으므로, 이번 Accept는 새 경계를 만드는 것이
아니라 이미 확정되고 반복 재확인된 경계를 Kernel Module로 명명하는 것이다.
ADC-0003 판단 4가 이 사안을 이미 "Development HQ 권한 밖"으로 분리해
Jarvis OS 수준으로 넘겨 두었다는 사실도, 지금 이 ADC(Kernel Baseline
수준)가 그 판단을 내릴 정당한 권한 소재라는 것을 뒷받침한다.

### Risks

이 Accept는 Execution Layer가 Kernel Module로서 "존재해야 한다"는 것만
확정한다. 내부 구조(Prompt 구성, Model 선택, 재시도 정책, Multi-Model
Routing)는 `docs/03_adc/ADC.md`의 ADC-01·ADC-02가 여전히 Open으로
남겨 두었으므로, 이 Accept를 "Execution Layer의 설계가 결정되었다"는
의미로 확장 해석하면 안 된다.

### Next Step

ADR Required

---

## Module 5. Event Bus (별도 검토)

### Evidence

- `docs/02_rfc/RFC-0001-kernel-boundary.md`: "MVP-0001은 실행 실패·재시도
  상황을 직접 관찰하지 않았다(Fault 전파 인프라는 MVP Out of Scope). 이
  질문은 관찰된 사실이 아니라 가설적 시나리오다."
- Development HQ Phase 1 전 구간(MVP-0001~0013)의 어떤 Observation
  문서에도 Event 발생, Fault 전파, HQ 경계를 가로지르는 통지가 실행된
  기록이 없다. `docs/research/EVIDENCE-REVIEW-0001.md`도 Event/Fault를
  Repeated Patterns·Non-Repeated Findings 어느 절에도 포함하지 않았다.
- `docs/03_adc/ADC.md`의 ADC-05(Fault Event 배달 보장 수준)는 여전히
  Open(NEXT)이며, 이 결정에 실증 근거로 쓰일 Development HQ Observation은
  존재하지 않는다.
- Event Bus의 유일한 근거는 `BASELINE.md` §6 Concept Model이 이미
  Frozen 상태로 정의해 둔 것뿐이다: "Task는 실패 시 Fault를 발생시키고,
  Fault는 Event로 전파된다", "Event는 HQ 경계를 가로질러 전파된다."

### Decision

**Defer**

### Decision Rationale

Event Bus는 이번 5개 Module 중 유일하게 Development HQ에서 **단 한 건의
반복 관찰도 없는** Module이다. Governance(5회 반복 실행), Execution
Layer(9개 MVP 일관 재확인), Workflow·Memory(각각 2회 이상의 Keep in MVP
재평가)와 달리, Event Bus는 Phase 1 전체를 통틀어 단 한 번도 실행된 적이
없다. `BASELINE.md`가 이미 이 Concept을 Frozen 상태로 정의해 두었다는
사실만으로 지금 Accept하는 것은, 이번 판단 기준이 명시적으로 금지한
"필요할 것 같다"는 추측과 정확히 같은 형태의 판단이 된다. Reject하지
않는 이유는, Concept 자체는 이미 Frozen Baseline v1.0의 일부이며 이
ADC가 Frozen Concept의 존재 자체를 부정할 권한을 갖지 않기 때문이다 —
이 ADC는 "지금 Kernel Module로 확정할 근거가 있는가"만 판단하며, 그
근거가 없다는 결론이 Defer다.

### Risks

Fault/Event 전파가 실제로 필요한 상황(어떤 HQ에서든 Task 실패가 HQ
경계를 가로질러 통지되어야 하는 사례)이 실제로 발생하기 전까지, Event
Bus는 Kernel Baseline에서 이름만 있고 근거는 없는 상태로 남는다. 이는
`ARCHITECTURE_GOVERNANCE.md`의 Freeze 원칙("미결정 사항이 정직하게
드러나 추적되는 것이 목표")과 일치하는 상태이지, 결함이 아니다.

### Next Step

No ADR Required

---

## 종합

| Module | Decision | Evidence 성격 | Next Step |
|---|---|---|---|
| Governance | **Accept** | 5회 반복 실행, 실패 없음 | ADR Required |
| Workflow | **Defer** | 2회 반복 재평가(ADC-0001, ADC-0004) 모두 Keep in MVP | No ADR Required |
| Memory | **Defer** | 1회 재평가(ADC-0001) + 4개 MVP 재확인, 모두 단일 경로로 충분 | No ADR Required |
| Execution Layer | **Accept** | 9개 MVP 전부 일관, Phase 1 시작 이전부터 Frozen 경계 | ADR Required |
| Event Bus | **Defer** | Development HQ 반복 관찰 0건, Concept Model에만 근거 | No ADR Required |

Kernel 전체는 일괄 승인되지 않았다. 5개 Module 중 2개(Governance, Execution
Layer)만 Accept되었고, 3개(Workflow, Memory, Event Bus)는 Defer되었다.
Reject되거나 Out of Authority로 분류된 Module은 없다 — 5개 모두 Jarvis OS
Kernel Baseline 수준의 판단 권한 안에 있었고, 어떤 Module도 명시적으로
"틀렸다"고 볼 근거는 없었기 때문이다.

## Self Review

- Observation만 사용했는가 — **Pass**. 5개 Module 모두 실제 ADC/RFC/
  Evidence Review 문서에 기록된 사실만 인용했다. 추측성 근거는
  사용하지 않았다.
- "필요할 것 같다"는 이유로 Accept했는가 — **아니오**. Workflow·Memory는
  Concept Model에 이미 정의되어 있었음에도, 반복 관찰된 Evidence(Keep in
  MVP)가 정반대 방향을 가리켰기 때문에 Defer했다.
- Event Bus를 별도로 검토했는가 — **Pass**. 다른 4개와 분리된 절에서
  "Development HQ 관찰 0건"이라는 사실을 명시적으로 대조했다.
- Kernel 전체를 일괄 승인했는가 — **아니오**. 5개 Module을 개별적으로
  판단했고 결과가 2 Accept / 3 Defer로 갈렸다.
- Architecture를 추가로 설계했는가 — **아니오**. 각 Module의 내부 구조,
  API, 자료구조는 이 문서에서 다루지 않았다.
- Decision 어휘가 4개(Accept/Defer/Reject/Out of Authority) 중에서만
  선택되었는가 — **Pass**.
- RFC-0001과 모순되지 않는가 — **Pass**. RFC-0001이 §4.5에서 이미
  명시한 "Event Bus는 실증 Observation이 없다"는 사실을 그대로 이어받아
  Decision의 근거로 사용했을 뿐, 새로운 전제를 추가하지 않았다.
