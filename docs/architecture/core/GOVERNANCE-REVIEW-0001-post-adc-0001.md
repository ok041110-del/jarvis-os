# Kernel Governance Review 0001 — ADC-0001(Artifact Drift Boundary) Merge 이후 상태 정리

이 문서는 새 Architecture를 설계하지 않는다. Kernel을 구현하거나
설계하지 않는다. Baseline을 변경하지 않는다. 오직 지금까지 실제로
일어난 Governance 절차와 그 결과를, 있는 그대로 정리한다.

## 근거 문서

- `docs/01_architecture/BASELINE.md`(Architecture Baseline v1.0, Frozen)
- `docs/03_adc/ADC.md`(Jarvis OS 수준 Open Decision, ADC-01~12)
- `docs/02_rfc/RFC-0001~0005`, `docs/governance/adc/ADC-0001~0004`,
  `docs/04_adr/ADR-0001`, `docs/governance/rt/RT-0001`,
  `docs/governance/observations/OBS-0001~0006`,
  `docs/research/EVIDENCE-REVIEW-0001.md`(Development HQ 수준)
- `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`,
  `docs/architecture/core/ADC-0001-core-baseline.md`(Kernel 수준)
- `core/execution_layer/mvp_0001~0005`, `docs/core/execution-layer/MVP-0001~0005-*`
  (Execution Layer 구현)
- `docs/research/ENGINE-INTEGRATION-0001~0003-Claude-Code.md`(Execution
  Protocol Research)
- `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md`,
  `docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md`
  (이번 Review의 직접 계기)

---

## 1. Kernel Governance Review — RFC → ADC → ADR 절차가 실제 사례와 일치하는가

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`가 정의한 절차는
`RFC → ADC → ADR → Baseline Update`다. 지금까지 실제로 일어난 사례를
그대로 대조한다.

| RFC | ADC | ADR | 실제 결과 |
|---|---|---|---|
| Dev HQ RFC-0001(Kernel Boundary) | ADC-0001(4개 Candidate 모두 Keep in MVP) | 없음 | 절차 완결(ADC가 "No ADR Required"로 스스로 종료) |
| Dev HQ RFC-0002(Task Dispatcher 재평가) | ADC-0002 | 없음 | 절차 완결 |
| Dev HQ RFC-0003(SDLC Pivot) | ADC-0003(판단 4개: Accept/Defer/Accept/Out of Authority) | ADR-0001(판단 1, Stage 구조에 한해서만) | **판단 4개 중 1개만 ADR로 이어짐** — 나머지 3개는 ADC에서 종료(Defer/Accept-No ADR/Out of Authority) |
| Dev HQ RFC-0004(Task Dispatcher→Runtime 승격) | ADC-0004(Keep in MVP) | 없음 | 절차 완결 |
| Dev HQ RFC-0005(Development HQ↔Execution Layer Boundary) | **없음** | 없음 | **RFC에서 절차가 멈췄다** — 후속 ADC가 열리기 전에 Development HQ Phase 1이 종료 선언되었다 |
| Kernel RFC-0001(Jarvis OS Kernel Baseline) | Kernel ADC-0001(5개 Module: Governance/Execution Layer Accept, Workflow/Memory/Event Bus Defer) | **Governance·Execution Layer 2개 Module이 "ADR Required"로 표시되었으나, 이 Review 시점까지 실제 ADR은 아직 작성되지 않았다** | 절차 진행 중 |
| Execution Layer RFC-0001(Artifact Drift Boundary) | Execution Layer ADC-0001(Not Accepted, based on current evidence) | 없음(No ADR Required로 스스로 명시) | 절차 완결 |

**일치 여부(사실 확인)**: 절차의 큰 틀(RFC → ADC → ADR)은 지금까지
위반된 적이 없다 — 어떤 사례도 ADC나 ADR을 건너뛰고 Baseline을 직접
바꾼 적이 없다. 다만 절차가 **항상 끝까지 진행되는 것은 아니라는
사실**이 실제 사례로 두 가지 형태로 확인된다.

1. RFC가 ADC로 이어지지 않고 멈춘 사례가 있다(Dev HQ RFC-0005).
2. ADC가 "ADR Required"로 판정했지만 그 ADR이 아직 실제로 작성되지
   않은 채 남아 있는 사례가 있다(Kernel ADC-0001의 Governance·Execution
   Layer 2개 Module).

이 문서는 이 두 사실을 지적만 한다 — 지금 그 공백을 메우지 않는다
(새 ADR을 작성하지 않는다, 새 ADC를 열지 않는다).

---

## 2. 운영 경험(Operational Experience) — Baseline에는 추가하지 않음

이번 Execution Layer ADC-0001을 포함해, 지금까지 실제로 관찰된
Governance 운영 경험만 기록한다. 이 절의 내용은 Architecture
Baseline이나 Kernel Baseline 문서에 반영하지 않는다 — 운영 경험으로만
남긴다.

- **ADC는 항상 ADR로 이어지지 않는다.** 지금까지 6건의 ADC(Dev HQ
  ADC-0001·0002·0003·0004, Kernel ADC-0001, Execution Layer ADC-0001)
  중, 실제로 ADR이 뒤따른 것은 ADC-0003의 판단 1(Stage 구조) 단
  1건뿐이다. 나머지는 모두 "Keep in MVP", "Defer", "Not Accepted",
  "Out of Authority" 같은 결과로 ADC 단계에서 종료되었다.
- **Evidence가 부족하면 ADC에서 종료될 수 있다.** Execution Layer
  ADC-0001("Not Accepted (based on current evidence)")이 그 실제
  사례다 — 3회의 독립 실험(ENGINE-INTEGRATION-0001~0003)이라는 상당한
  분량의 Evidence가 있었음에도, 그 Evidence가 "Boundary를 Kernel로
  옮길 근거"까지는 되지 못한다고 판단되어 ADR 없이 종료되었다.
- **RFC도 항상 ADC로 이어지지 않는다.** Dev HQ RFC-0005는 Development
  HQ Phase 1 종료 선언과 함께 후속 ADC 없이 절차가 멈췄다 — RFC 자체가
  "경계를 정리하는 것"으로 목적을 다한 경우, 반드시 ADC가 뒤따라야
  하는 것은 아니라는 사실이 확인되었다.
- **"ADR Required" 판정과 실제 ADR 작성 사이에는 시차가 있을 수
  있다.** Kernel ADC-0001은 두 Module(Governance, Execution Layer)에
  대해 ADR이 필요하다고 판정했지만, 그 판정 이후 실제 구현(Execution
  Layer MVP-0001~0005)과 후속 연구(Execution Protocol Research)가
  먼저 진행되었고, 이 Review 시점까지도 그 ADR 자체는 작성되지 않은
  채 남아 있다.
- **RFC/ADC 절차는 Governance v2의 자동 개시 규칙(Rule A, Rule B)과
  함께 실제로 작동했다.** Dev HQ RFC-0004는 Rule A(RT Trigger 충족 →
  RFC)로, Execution Layer RFC-0001은 Rule B(Observation Count ≥ 3 →
  RFC)로 각각 새 실험 없이 기존 Evidence만으로 열렸다 — 두 Rule 모두
  실제 사례에서 최소 1회 이상 적용되었다.

---

## 3. Architecture Timeline

관찰된 실제 순서를 그대로 나열한다. 추정하지 않는다.

```
Architecture Baseline v1.0 (Frozen)
↓
Development HQ Baseline v1.0 (Frozen, ADR-0001로 Stage 구조 반영)
↓
Development HQ MVP-0001 (Task Dispatcher/Engine Gateway/Registry/
                          Context 4개 Candidate 하드코딩으로 검증)
↓
Dev HQ RFC-0001(Kernel Boundary) → ADC-0001(4개 Candidate Keep in MVP)
                                  → RT-0001(재평가 Trigger 정의)
↓
Development HQ MVP-0002~0004 (Workflow Branch, Stage 구조 도입)
→ Dev HQ RFC-0002 → ADC-0002
→ Dev HQ RFC-0003(SDLC Pivot) → ADC-0003(판단 4개) → ADR-0001(판단 1만)
↓
Development HQ MVP-0005~0013 (Capability Loop 5개 Capability 반복 성숙:
  Project Intelligence/Planning/Design/Validation/Implementation Spec)
→ OBS-0001~0006 → Dev HQ RFC-0004(Rule A로 개시) → ADC-0004(Keep in MVP)
→ Evidence Review 0001
↓
Dev HQ RFC-0005(Development HQ ↔ Execution Layer Boundary)
— Development HQ Phase 1 종료 선언, 후속 ADC 없이 절차 종결
↓
Jarvis OS Kernel RFC-0001(Kernel Baseline: Governance/Workflow/Memory/
                        Execution Layer/Event Bus 5개 Module 정의)
↓
Jarvis OS Kernel ADC-0001(Module별 개별 판단:
  Governance Accept, Execution Layer Accept,
  Workflow/Memory/Event Bus Defer)
↓
Execution Layer MVP-0001~0005
(Execution Request → Prompt Specification → Model Request →
 Execution Handle → Execution State, Artifact Chain 구축)
→ Kernel Artifact Standard v1
↓
Execution Protocol Research
(ENGINE-INTEGRATION-0001~0003, 실제 Claude Code Engine 3회 실험)
→ Spec-Repository Artifact Drift Pattern 관찰(Observation Count = 3)
↓
Execution Layer RFC-0001(Artifact Drift Boundary, Rule B로 개시)
→ Execution Layer ADC-0001(Not Accepted, based on current evidence)
↓
No ADR
↓
Baseline 유지 (Architecture Baseline v1.0, Kernel Baseline 모두 불변)
```

---

## 4. Open Decision Status

`docs/03_adc/ADC.md`(Jarvis OS 수준 Single Source of Truth)의 12개
Open Decision(ADC-01~12) 중, 이번 Execution Layer RFC-0001/ADC-0001과
직접 연결되는 항목을 점검한다. **새 Decision을 내리지 않는다. 상태만
점검한다.**

| ADC 항목 | 현재 상태 | 이번 RFC-0001과의 관계(사실 확인) |
|---|---|---|
| ADC-02(Runtime 개념의 존폐) | Open, NOW | Workflow Module과 연결되지만, 이번 Artifact Drift 논의는 Workflow가 아니라 Execution Layer/HQ 경계를 다뤘다 — 직접 연결되지 않는다. 상태 변화 없음. |
| ADC-09(Workflow 그래프의 의미론적 경계) | Open, NOW | "OS가 도메인 내용을 몰라야 한다"는 원칙이 이번 ADC-0001의 Decision Rationale(§Q1)에 그대로 재사용되었다 — 근거로 인용되었을 뿐, ADC-09 자체의 상태를 바꾸지는 않는다. |
| ADC-11(Capability 선언의 신뢰 검증 책임) | Open, LATER | "HQ가 선언한 내용을 OS가 검증해야 하는가"라는 질문과 결이 비슷하다(이번 사례는 Capability가 아니라 Artifact 내용의 신선도 문제이긴 하다). 직접적인 동일 항목은 아니다. 상태 변화 없음. |
| 나머지 9개(ADC-01,03~08,10,12) | Open, 각각의 우선순위 유지 | 이번 RFC-0001/ADC-0001 사례와 직접 연결되는 근거를 찾지 못했다. |

**점검 결과(사실 확인)**: 이번 RFC-0001(Spec-Repository Artifact
Drift)이 다룬 주제는 `docs/03_adc/ADC.md`의 기존 12개 Open Decision
어디에도 정확히 대응하지 않는다. ADC-09의 원칙은 근거로 재사용되었을
뿐, 새 항목으로 등록되지는 않았다. ADC.md의 Single Source of Truth
원칙("모든 Open Decision은 ADC.md에서 관리한다")에 따르면 이 Boundary
Question이 Jarvis OS 수준에서 계속 추적되려면 별도 등록이 필요할 수
있으나, 이 문서는 그 등록 여부를 판단하지 않는다 — 상태만 점검했다.

---

## 5. Kernel Readiness Assessment

**질문**: Kernel을 설계할 충분한 Evidence가 있는가?

**평가: 아직 없다.**

Kernel Architecture 제안은 하지 않는다. 다음은 그렇게 판단하는 근거
(Evidence 기반)만 정리한다.

- `docs/01_architecture/BASELINE.md` §10은 Kernel Architecture와
  Component Design(Scheduler, Engine Gateway, Registry 등)을 v1.0
  시점부터 명시적으로 Out of Scope로 남겨 두었다 — 이 결정은 아직
  뒤집힌 적이 없다.
- Kernel의 5개 Module 후보 중 2개(Governance, Execution Layer)만
  Accept되었고, 3개(Workflow, Memory, Event Bus)는 여전히 Defer
  상태다(Kernel ADC-0001). Kernel은 통상 이 Module들이 상호작용하는
  전체 구조를 전제하는데, 절반 이상이 아직 Accept되지 않았다.
- ADC-02(Runtime 개념의 존폐)는 Architecture Baseline v1.0 이후
  지금까지 계속 Open(우선순위 NOW) 상태다 — Kernel의 핵심 개념 중
  하나가 아직 결정되지 않았다.
- 지금까지 Governance v2의 자동 개시 규칙(Rule A, Rule B)으로 실제
  RFC까지 이어진 Pattern은 극소수다: Dev HQ RFC-0004(Rule A, Task
  Dispatcher 체인 수 ≥ 2)와 Execution Layer RFC-0001(Rule B,
  Observation Count = 3, Spec-Repository Artifact Drift)뿐이다. 이
  둘 중 하나(RFC-0004→ADC-0004)는 "Keep in MVP"로, 다른 하나
  (RFC-0001→ADC-0001)는 "Not Accepted"로 끝났다 — **지금까지 충분한
  반복 Evidence를 확보해 실제로 RFC까지 이른 두 사례 모두, Kernel
  방향으로 무언가를 승격하거나 확정하는 결과로 이어지지 않았다.**
  이는 "아직 Kernel을 설계할 만큼 반복적으로 승격 압력이 관찰된 대상이
  없다"는 사실을 보여준다.
- Engine Gateway 관련 Trigger("Engine 수 ≥ 2", ADC-0001 Candidate 2,
  RT-0001)는 아직 충족되지 않았다 — Execution Protocol Research
  (ENGINE-INTEGRATION-0001~0003) 세 실험 모두 Claude Code 하나만
  사용했다. 여러 Engine을 실제로 오가며 관찰한 사례가 아직 없다.
- Execution Layer 자체도 5개 MVP로 Artifact Chain(Request → Prompt
  Specification → Model Request → Handle → State)만 구축했을 뿐,
  Execution Result(6번째 Artifact)조차 아직 설계되지 않았다 — Kernel의
  전제가 되는 Execution Layer 자체가 아직 완결되지 않은 상태다.

**결론**: 지금까지 축적된 Evidence는 "무엇이 아직 Open인가", "무엇이
아직 Defer 상태인가"를 정직하게 드러내는 데는 충분했지만, 그 Open
항목들을 실제로 Kernel 수준에서 통합할 근거는 아직 만들어지지 않았다.
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 Good Architecture
Principle("필요한 것만 적절한 시점에 결정한 Architecture")에 따르면,
지금 시점은 아직 그 시점이 아니다.

---

## 6. Architecture Governance Review

이 문서 자신에 대한 자기 점검이다.

- **Architecture Drift** — 없음. 새 Architecture를 제안하지 않았다.
- **Kernel Leak** — 없음. Kernel, Scheduler, Registry, Runtime 중
  어느 것도 설계하거나 구현하지 않았다. "아직 설계할 근거가 없다"는
  판단만 기록했을 뿐, 그 판단의 근거로 구현 방법을 논의하지 않았다.
- **Baseline 변경 여부** — 없음. Architecture Baseline v1.0, Kernel
  Baseline(RFC-0001/ADC-0001) 어느 것도 수정하지 않았다.
- **새로운 Layer** — 없음.
- **새로운 Component** — 없음.
- **새로운 Concept** — 없음. 이 문서가 사용한 모든 개념(Governance,
  Workflow, Memory, Execution Layer, Event Bus, Kernel, RFC/ADC/ADR)
  은 기존 문서에서 이미 정의된 것을 그대로 인용했다.
- **ADR 작성 여부** — 없음. §1에서 발견한 절차 공백(Dev HQ RFC-0005의
  미완결, Kernel ADC-0001의 미작성 ADR 2건)을 지적만 했을 뿐, 이 문서가
  그 공백을 메우는 ADR을 작성하지 않았다.

---

## 최종 산출물 요약

1. **Kernel Governance Review** — §1. RFC→ADC→ADR 절차의 큰 틀은
   지금까지 위반되지 않았으나, 절차가 항상 끝까지 완결되지는 않는다는
   사실(RFC가 ADC로 이어지지 않은 사례 1건, ADC가 ADR Required라고
   판정했지만 아직 작성되지 않은 사례 2건)이 확인되었다.
2. **Architecture Timeline** — §3. Architecture Baseline v1.0부터
   이번 Execution Layer ADC-0001(Not Accepted)까지의 실제 순서를
   정리했다.
3. **Open Decision Status** — §4. 이번 RFC-0001과 정확히 대응하는
   기존 Jarvis OS Open Decision은 없다(ADC-09의 원칙만 근거로
   재사용됨). 새 Decision은 내리지 않았다.
4. **Kernel Readiness Assessment** — §5. 아직 준비되지 않았다 — Kernel
   Module 절반 이상이 Defer 상태, ADC-02(Runtime)가 여전히 Open,
   Engine Gateway Trigger 미충족, Execution Layer 자체도 미완결
   (Execution Result 부재)이라는 사실에 근거한다.
5. **다음 RFC가 시작될 조건** — Governance v2의 기존 두 자동 개시
   규칙을 그대로 따른다: (a) Rule A — 기존에 정의된 RT Trigger(예:
   RT-0001의 "Engine 수 ≥ 2")가 실제로 충족되는 사건이 관찰될 때,
   또는 (b) Rule B — 새로운 Pattern이 서로 다른 조건에서 최소 3회
   독립적으로 반복 관찰될 때(이번 Execution Layer RFC-0001이 실제로
   그렇게 열렸다). 이 문서는 그 외의 새 개시 조건을 만들지 않는다.
