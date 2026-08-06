# ADC-0001: Spec-Repository Artifact Drift — Kernel 책임 여부 판단 (RFC-0001 후속)

## 목적

`docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md`가 제기한
Boundary Question — "Spec-Repository Artifact Drift를 Development HQ /
Execution Layer / Engine / Other 중 누가 책임지는가" — 중, 이번 ADC는
그 전체를 판단하지 않는다. 오직 하나만 판단한다: **이 Boundary를
Kernel가 책임지는가?**

해결책은 판단하지 않는다. 근거는 RFC-0001과
`docs/research/ENGINE-INTEGRATION-0001~0003-Claude-Code.md`에 실제로
기록된 사실로만 한정한다. 새로운 Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

이 ADC는 다음을 판단하지 않는다.

- Development HQ가 이 Boundary를 책임지는지 여부
- Kernel이 이 Boundary를 책임지는지 여부
- Drift에 대한 해결 방법
- 해결의 구현 방법

이 ADC가 판단하는 것은 오직 하나다: **현재 확보된 Evidence로 Kernel
Boundary를 이동할 수 있는가?**

---

## Q0. Artifact Drift는 Execution Layer 내부 문제인가, 밖에서 발생한 문제인가?

### Evidence

- Kernel Artifact Standard v1과 MVP-0001~0005 각 테스트 스위트는 5개
  Execution Layer Builder(`ExecutionRequestBuilder`,
  `PromptSpecificationBuilder`, `ModelRequestBuilder`,
  `ExecutionHandleBuilder`, `ExecutionStateBuilder`) 모두가 입력
  Artifact를 한 글자도 바꾸지 않고(Transformation만, Interpretation
  없음), Deterministic하게 동작한다는 사실을 이미 확정해 두었다. 세
  실험(ENGINE-INTEGRATION-0001~0003) 중 어디에서도 이 5개 Builder
  자체가 Drift를 만들어내거나 악화시켰다는 관찰은 없다.
- ENGINE-INTEGRATION-0001~0003 세 실험 모두에서 Drift의 실체는
  동일했다: `_enrich_issue()`가 실제로 붙이는 헤더 문자열
  (`"[Relevant Context]"`)이 `engine._analyze_requirement`에서
  partition되어 사라지고, 그 결과가 `"## Reference Context"` 절로
  재구성된다는 사실과, Prompt Specification 문서 안에 남아 있는
  서술(Requirement/Design 절의 문장)이 서로 어긋난 것이었다. 이
  서술은 Execution Layer가 만든 것이 아니라, Development HQ의
  Requirement/Design/Implementation Specification 생성 로직
  (`engine.py`)이 이미 만들어 Execution Layer에 **입력으로 건네준**
  텍스트다.
- ENGINE-INTEGRATION-0001의 Failure 절: subagent가 스스로 "이는 Spec
  텍스트 자체의 결함이지, Validation Logic의 결함이 아니다"라고
  판단한 것과 동일한 구조 — 세 실험 모두 Drift가 텍스트(Spec) 자체의
  내용 문제로 나타났을 뿐, Execution Layer의 어느 Builder가 잘못
  변환한 결과로 나타난 적은 없다.
- ENGINE-INTEGRATION-0003 Evidence Summary: 이번 실험에서만 subagent가
  코드 작성 전에 실제 반환값을 사전 조사해 Drift를 회피했다 — 이
  회피는 Execution Layer의 어떤 Builder도 관여하지 않은, Engine
  자신의 조사 행동이었다.

### Q0 결론(Evidence 기반)

세 실험 모두에서, Drift는 Execution Layer의 5개 Builder 내부에서
발생하지 않았다. Drift의 실체(마커 문자열 불일치)는 Execution Layer가
Artifact를 만들기 이전, 즉 Development HQ가 생성한 Implementation
Specification 텍스트 안에 이미 존재했다. **Execution Layer 밖에서
발생한 문제다.**

---

## Q1. Execution Layer 밖이라면, 그 "밖"은 Kernel 문제인가, 아니면 Kernel도 아닌 문제인가?

Q0가 "Execution Layer 밖"으로 판단했으므로, 이 질문은 그 "밖"이 (a)
다른 Kernel Module의 책임 범위인지, 아니면 (b) Kernel 전체의 책임 범위를
벗어난 것(Development HQ의 domain 문제)인지를 구분해야 한다. 원 질문
("만약 Kernel 문제라면 Execution Layer가 책임지는가, 다른 Kernel Module
책임인가")은 "밖 = Kernel 문제"라는 전제를 깔고 있으나, 이 전제 자체가
Evidence로 성립하는지부터 확인한다.

### Evidence

- Drift의 실체는 Development HQ의 Requirement/Design/Implementation
  Specification 문서 **내용**이 Development HQ 자신의 파이프라인
  코드(`engine.py`)가 이후 버전에서 바뀐 것과 어긋난 것이다 — 세
  실험의 Evidence Summary가 공통으로 지목한 원인이다.
- Kernel의 Boundary는 이미 확정되어 있다(`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`
  §3): "Kernel는 Specification, Context, Execution Result, Event 같은
  공통 Artifact만 다룬다... Kernel는 도메인을 모른다. HQ는 도메인을
  안다." Requirement/Design 문서가 실제로 서술하는 내용(어떤 마커
  문자열을 쓰는지, 어떤 함수가 무엇을 하는지)은 Development HQ의
  도메인 내용이지, Kernel가 다루는 공통 Artifact의 형식/전달 문제가
  아니다.
- 세 실험 어디에서도, Kernel의 다른 Module(Governance, Workflow,
  Memory, Event Bus — 어느 것도 Accept되지 않았거나 Execution Layer
  외에는 Defer 상태다, `docs/architecture/core/ADC-0001-core-baseline.md`
  참조)이 이 Drift와 관련해 어떤 역할을 했다는 관찰은 없다. Drift를
  실제로 발견하고 대응한 것은 매번 Engine(Claude Code) 자신이었다 —
  Kernel Module이 아니다.

### Q1 결론(Evidence 기반)

"밖 = Kernel 문제"라는 전제 자체가 Evidence로 뒷받침되지 않는다. 세
실험에서 관찰된 Drift의 원인은 Development HQ가 생성한 Artifact
**내용**(도메인 서술)이 Development HQ 자신의 코드 변경과 어긋난
것이었다. 이는 Kernel RFC-0001 §3이 이미 확정해 둔 System Boundary
("Kernel는 도메인을 모른다")에 따라 Development HQ의 domain 문제이지,
Kernel Module(Execution Layer를 포함한 어느 Module) 문제로 재분류될
근거가 Evidence에 없다. 따라서 Q1이 전제한 "Execution Layer 대 다른
Kernel Module" 사이의 선택 자체가 이번 Evidence로는 성립하지 않는다.

---

## Decision

**Not Accepted (based on current evidence)**

Kernel는 이 Boundary(Spec-Repository Artifact Drift에 대한 책임)를
지금 관찰된 Evidence를 근거로는 떠맡지 않는다.

### Reason

Current evidence does not support moving the Artifact Drift Boundary
into Kernel. (지금까지 관찰된 Evidence는 Artifact Drift Boundary를
Kernel 쪽으로 이동시킬 근거를 제공하지 않는다.)

## Decision Rationale

Q0는 Drift가 Execution Layer의 5개 Builder 내부에서 발생하지 않았다는
것을 실측(Kernel Artifact Standard v1의 Deterministic/Immutable 검증,
세 실험의 Failure 절)으로 확인했다. Q1은 그 "밖"이 다른 Kernel Module의
책임으로 재분류될 근거도 Evidence에 없다는 것을 확인했다 — Drift의
실체는 Development HQ가 생성한 Artifact의 도메인 내용(Requirement/
Design 서술)이 Development HQ 자신의 코드 변경과 어긋난 것이었고, 이는
Kernel RFC-0001 §3이 이미 확정한 System Boundary("Kernel는 도메인을
모른다")에 따라 Development HQ의 domain 문제다. 세 실험 모두에서 Drift
를 실제로 발견하고 대응한 주체는 Kernel Module이 아니라 Engine
(Claude Code) 자신이었다는 사실도 이 결론과 일치한다.

## Risks

이 Decision은 오직 3회 관찰(모두 동일한 하나의 Prompt Specification
Artifact를 근거로 함)에 근거한다. 세 실험 모두 같은 근본 원인(같은
마커 문자열 불일치)을 공유했으므로, 이는 "Drift 일반"에 대한 결론이
아니라 "지금까지 관찰된 이 특정 형태의 Drift"에 대한 결론이다.

**이 Decision이 의미하지 않는 것**: "Kernel가 영원히 이 Boundary를
책임지지 않는다"는 뜻이 아니다. 이 Decision이 실제로 의미하는 것은
"현재 확보된 Evidence만으로는 Boundary를 Kernel 쪽으로 이동시킬 이유가
없다"는 것뿐이다 — Boundary의 영구적 배정을 확정한 것이 아니라, 지금
시점의 Evidence 상태에 대한 판단이다.

**재검토 조건**: 다른 근본 원인을 가진 Drift(예: Execution Layer
Builder 자체의 결함으로 생기는 Drift)가 향후 관찰되거나, 새로운
Evidence가 확보되면, 이 Decision은 기존 Governance 절차
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`: RFC → ADC → ADR →
Baseline Update)를 통해 재검토 대상이 된다 — 이 문서를 직접 고쳐
뒤집는 것이 아니라, 새 RFC가 새 Evidence를 근거로 열리는 절차를
따른다.

## Next Step

No ADR Required — "Not Accepted (based on current evidence)"는
Boundary를 이동시키지 않으므로 Baseline 변경을 전제하지 않는다.

RFC-0001의 원래 Boundary Question(Development HQ / Execution Layer /
Engine / Other)에 대한 전체 판단은 이 ADC가 내리지 않는다. 이 ADC는
"Kernel가 책임지는가"만 판단했다. Development HQ가 이 Boundary를
책임질지 여부는 Development HQ 수준의 별도 판단이 필요하며, 이 ADC의
권한 범위가 아니다(Development HQ는 Phase 1 완료 후 더 이상 수정되지
않는 상태다 — 이 판단을 누가, 언제 내릴지는 이 ADC가 결정하지 않는다).

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer가 추가되었는가 — **아니오**.
- 새로운 Component가 추가되었는가 — **아니오**.
- 새로운 Concept이 추가되었는가 — **아니오**.
- Baseline 문서(Kernel RFC-0001, Kernel ADC-0001)를 변경했는가 —
  **아니오**. 이 ADC는 기존 Baseline을 그대로 인용만 했다.
- ADR이 필요한가 — **아니오**. "Not Accepted (based on current
  evidence)"는 Boundary를 이동시키지 않으므로 Baseline Update를
  전제하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0001과
  ENGINE-INTEGRATION-0001~0003에 실제로 기록된 내용, 그리고 이미
  Frozen된 Kernel RFC-0001/ADC-0001(Kernel Baseline)의 기존 결정만
  인용했다. 새 실험은 하지 않았다.
- 해결책을 판단했는가 — **아니오**. Repository Snapshot, Git Hook,
  Runtime, Prompt 수정, Engine 수정, Claude 개선 어느 것도 다루지
  않았다.
- Q0 → Q1 순서를 지켰는가 — **Pass**. Q0(Execution Layer 내부/외부)를
  먼저 판단한 뒤에만 Q1(Kernel Module 간 배분)을 다뤘다.
- Decision 표현이 "이 Boundary를 Kernel가 지금 확보된 Evidence로
  떠맡을 수 없다"는 의미를 정확히 전달하는가 — **Pass**. "Not
  Accepted (based on current evidence)"로 표현했다.
- ADR을 작성했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- Kernel을 설계했는가 — **아니오**.
- Development HQ를 수정했는가 — **아니오**.
- Kernel Architecture를 수정했는가 — **아니오**.
- RFC-0001과 모순되지 않는가 — **Pass**. RFC-0001이 답하지 않기로 한
  Boundary Question 전체를 이 ADC가 대신 답하지 않았다 — "Kernel가
  책임지는가" 하나만 판단했다.
