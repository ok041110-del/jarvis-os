# ADC-0033: Agent State / Message / Event Contract — Governance Review (RFC-0025 후속, Phase B)

## 목적

`docs/architecture/core/RFC-0025-agent-state-message-event-contract.md`
§4(Agent State 존재)·§5(State 소유권/변경 책임 매트릭스)·§6(Message vs
Event 구분, (a)/(b)/(c))·§7(최소 Envelope 후보)·§10(귀속처 Open
Question) 각각이 **지금 Baseline에 반영할 만큼 확정할 수 있는지**를
판단한다.

근거는 RFC-0025 원문과 그것이 인용한 Evidence, 그리고 이 Review가 추가로
직접 재확인한 다음 문서로 한정한다: `docs/architecture/baseline/BASELINE.md`
§6(Concept Model)·§11("Kernel은 Event Bus가 아니다")·§13.3(A-4, G-7 —
"조립은 시계·난수·외부 I/O를 읽지 않는다")·§14.1(Kernel 책임 후보 표 8개
항목 — Event/Message 미등재를 원문 대조로 재확인), `docs/00_governance/GLOSSARY.md`,
`docs/decisions/adc/ADC.md` ADC-05(Fault Event 배달 보장 수준, Open,
NEXT)·ADC-08(Task/Event Flow 배달 보장 차등화, Open, NEXT) 원문,
`hqs/development/IMPLEMENTATION_RULES.md`(Event Bus 구현 금지),
`docs/architecture/core/RFC-0024-*`·`ADC-0032-*`(Phase A — Agent
Domain/Lifecycle **Not Accept, Defer**, Agent Manager 현재 허용 범위 =
없음). **새로운 실험·프로토타입·측정은 수행하지 않는다.**

### 이 ADC가 판단하지 않는 것

- Agent State/Message/Event의 **자료구조·스키마·구현** — 사용자 지시에
  따라 이 Review는 Accept/Reject/Defer 판단만 하며 설계하지 않는다.
- Event Bus·Scheduler·Registry·Runtime(ADC-02, Open)·Workflow
  Engine·LangGraph — RFC-0025가 이미 Out of Scope로 둔 것을 이 ADC도
  다루지 않는다.
- ADC-05·ADC-08의 **해소**(배달 보장 수준 결정) — 이 ADC는 두 항목이
  RFC-0025로 인해 사실상 결정되어 버렸는지만 검증하고(Q5), 그 자체를
  이번 기회에 해소하지 않는다.
- `BASELINE.md`/`GLOSSARY.md`/`ADC.md` 문서 수정 — 이 ADC는 **문서 1건만
  신설**한다.

---

## Q1. RFC-0025 §4 Agent State(불투명 값 존재 후보)를 지금 Baseline Candidate로 확정해야 하는가?

### Evidence

- `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준": ①지금 결정하지 않으면
  상위 Architecture 진행 불가, 또는 ②결정이 늦어질수록 되돌리는 비용이
  매우 커짐 — 둘 중 하나 필요.
- Agent State의 유일한 잠재 소비자는 "Multi-Agent Runtime"인데, Runtime
  존폐 자체가 `ADC-02`(Open, 아직 미결)다. 소비자가 존재하지 않는
  상태에서 그 소비자가 읽을 대상의 존재 여부를 먼저 확정하는 것은 순서가
  거꾸로다.
- `RFC-0024`/`ADC-0032`가 이미 Agent Lifecycle State를 Defer했고, Agent
  State는 그와 별개 개념이라도 마찬가지로 "아직 관찰되지 않은 미래
  소비자를 위한 선제 설계"라는 동일한 성격을 갖는다.

### Q1 결론

**Not Accept — Defer.** ①·② 어느 기준도 충족하지 않는다(소비자 부재,
되돌릴 결정 자체가 아직 없음). §4는 Reference로만 남긴다 — RFC-0025가
스스로 "존재를 주장하지 않는다"고 명시한 것과 일치하는 판정이다.

## Q2. RFC-0025 §5 State 소유권/변경 책임 매트릭스를 Baseline에 반영해야 하는가?

### Evidence

- §5 표는 새 권한을 창설하지 않고 기존 확정·금지(`ADC-0032` §Q4 "Agent
  Manager 허용 범위 = 없음", `IMPLEMENTATION_RULES.md` Event Bus/Registry/
  Scheduler 금지, §11)를 State라는 아직 존재하지 않는 대상에 조건부로
  적용한 것이다.
- Q1이 Agent State 자체를 Defer했으므로, 그 State에 대한 소유권 규정은
  **대상이 없는 규정**이 된다 — `ADC-0032` §Q4가 Agent Manager 경계를
  "공허하다(vacuously true)"고 판정한 것과 동일한 구조.

### Q2 결론

**Not Accept — Defer(대상 부재로 인한 종속적 Defer).** §5는 독립적으로
Reject할 근거가 있어서가 아니라, Q1이 Defer된 이상 그 위에 세워진
소유권 규정도 함께 보류되는 것이 논리적으로 맞다. 다만 §5가 인용한
개별 사실(Agent Manager 허용 범위 없음, Event Bus 미존재)은 이미
`ADC-0032`·`IMPLEMENTATION_RULES.md`가 확정한 것이므로 그 부분은
**재확인**으로 유효하며 이 ADC가 뒤집지 않는다. Agent State가 실제로
Accept되는 시점에 §5를 함께 재상정한다.

## Q3. RFC-0025 §6의 Message vs Event (a)/(b)/(c) 중 하나를 지금 선택해야 하는가?

### Evidence

- §6 원문은 "HQ 경계를 가로질러" 전파되는 것으로만 Event를 정의하며,
  Agent 경계를 가로지르는 통신이 그 정의에 포함되는지는 미답이다.
- 세 후보 모두 §6 Concept Model 문언 확장을 전제한다 — (c)는 새 Flow
  개념 추가로 Architecture Impact가 가장 크다.
- 실제 Agent↔Agent 통신 사례가 v2에서 아직 관찰되지 않았다(`ADC-0032`
  §Q3 인용 — `stock_team.py`의 `ThreadPoolExecutor`는 단명 병렬 실행일
  뿐 Agent 간 통신이 아니다). 선택을 강제할 실증 사례가 없다.

### Q3 결론

**선택하지 않는다 — Open으로 유지.** ADC 채택 기준 ①·② 어느 것도
충족하지 않는다. 세 후보 중 하나를 지금 고르면 실제 사용 사례 없이
Concept Model을 앞서 확장하는 것이 되어 `BASELINE.md` §4 "필요한 것만
적절한 시점에 결정한 Architecture" 원칙과 충돌한다.

## Q4. RFC-0025 §7 Envelope(Identity/Type/Payload/Correlation/Time) 필드의 존재 여부를 지금 확정해야 하는가?

### Evidence

- §7은 스스로 "결정하는 것 — 없음"이라 명시하며 필드의 **존재 여부만**
  후보로 제안했다. 자료형·필수 여부·직렬화는 다루지 않는다.
- Time 필드는 §13.3 A-4("조립은 시계를 읽지 않는다")·G-7(Stateless
  Boundary)과 충돌하지 않도록 "호출자 주입"으로 한정되어 있다 — 이
  ADC가 원문을 재대조한 결과 §13.3 표(283행)·§13.6(437~448행)의 문언과
  정합적이며, Kernel이 스스로 시계를 읽는 새 예외를 만들지 않는다.
- 그러나 Envelope의 실제 소비자 역시 Event Bus(구현 금지, §11)·Runtime
  (ADC-02 Open)이며, Q1·Q3와 동일하게 아직 실체가 없다.

### Q4 결론

**Not Accept — Defer.** A-4/G-7과 충돌하지 않는다는 점은 확인했지만
(그래서 §13.3 자체를 다시 열 필요는 없다), 필드 존재 여부를 Baseline
Candidate로 승격할 만한 실제 압박(①·②)이 없다. Envelope는 Reference로
남긴다.

## Q5. RFC-0025가 ADC-05·ADC-08의 기존 Open Decision을 우회하거나 사실상 확정했는가?

### Evidence

- `docs/decisions/adc/ADC.md` 원문 재확인: ADC-05 "Fault가 Task Flow
  수준(at-least-once)으로 배달되는지, Event Flow 수준(best-effort)으로
  배달되는지 미정" — 상태 Open, 우선순위 NEXT. ADC-08 "Task Flow(순서·
  무유실)와 Event Flow(도달 범위)가 실제로 다른 배달 보장 수준으로
  구현되는지 미정" — 상태 Open, 우선순위 NEXT. 이 Review 시점 기준
  **두 항목 모두 RFC-0025 이전과 동일하게 Open**이며 수정 이력 없음.
- RFC-0025 §6~§7 어디에도 배달 보장 수준(at-least-once/best-effort),
  재시도 정책, 순서 보장 여부에 대한 서술이 없다 — Envelope 후보는
  "무엇을 담는가"만 다루고 "어떻게 배달되는가"는 전혀 다루지 않는다.
  Correlation 필드조차 "발신자가 정하고 Kernel은 비교만 한다"는
  존재-후보 서술에 그친다.
- §6의 (a)/(b)/(c) 중 하나를 선택하지 않은 것 자체가 ADC-05/08이
  전제하는 "Event Flow가 Agent 간에도 적용되는가"라는 선결 질문을 열어
  둔 채로 두었다는 뜻이다 — 배달 보장 수준을 논하려면 먼저 그 Flow의
  적용 범위가 확정돼야 하는데, RFC-0025는 그 범위조차 미확정으로
  남겼으므로 배달 보장을 사실상 결정할 방법이 구조적으로 없다.

### Q5 결론

**우회·사실상 확정 없음.** ADC-05·ADC-08은 이 Review로도 상태·내용
불변이다. RFC-0025는 배달 보장 수준의 **전제가 되는 상위 질문**(Flow
적용 범위, §6)조차 미해결로 남겨, 오히려 ADC-05/08을 조기에 답하지
못하게 만드는 구조를 스스로 확인했을 뿐이다.

## Q6. RFC-0025 §10 귀속처(Kernel-level 정련 가능성) Open Question을 이 ADC가 확정하는가?

### Evidence

- §10은 "Kernel-level 정련일 가능성이 더 높다"는 **관찰**과 Accept
  여부인 **결정**을 명시적으로 분리했다. `ADC-0032` §Q5도 Agent Domain
  귀속처를 Open으로 유지한 바 있다.
- Q1~Q4가 전부 Defer로 판정된 이상, "무엇에 귀속되는가"를 먼저 정할
  실익이 없다 — 귀속시킬 확정된 Contract 내용 자체가 아직 없다.

### Q6 결론

**확정하지 않는다 — Open으로 유지.** §10의 관찰은 유효한 기록으로
남기되(§Rationale에 인용), 이 ADC가 Kernel-level/HQ-level 중 하나로
귀속을 확정하지 않는다. 사용자 지시("권한 밖의 판단은 임의로 확정하지
말고 Open Decision으로 남겨라")와 일치한다.

---

## Decision

**Q1(Agent State 존재) — Not Accept, Defer.**
**Q2(State 소유권 매트릭스) — Not Accept, Defer(대상 부재에 따른
종속적 Defer; 개별 인용 사실 자체는 기존 확정 유지).**
**Q3(Message/Event (a)/(b)/(c) 선택) — 선택하지 않음, Open.**
**Q4(Envelope 필드 존재) — Not Accept, Defer.**
**Q5(ADC-05/08 우회 여부) — 우회·사실상 확정 없음, 두 항목 Open 그대로
유지.**
**Q6(귀속처 확정) — 확정하지 않음, Open Decision 유지.**

**RFC-0025는 Proposed 상태를 유지한다.** 이 ADC로 Accepted/Rejected 중
어느 쪽으로도 전환하지 않는다 — Candidate들이 틀렸다는 것이 아니라
지금 결정할 근거(실제 소비자·실제 Agent 간 통신 사례)가 없다는 판단이며,
§Conditions가 충족되면 다시 열릴 수 있다.

## Status

**Decided — No Baseline/Contract/Runtime Change**

## Rationale

Q1~Q4가 공통으로 확인한 것은, RFC-0025의 모든 Candidate(Agent State,
State 소유권, Message/Event 구분, Envelope)가 궁극적으로 같은 미해결
전제에 의존한다는 점이다 — **Multi-Agent Runtime의 실제 존재**(ADC-02,
여전히 Open)와 **실제 관찰된 Agent 간 통신 사례**(v2 어디에도 없음,
`ADC-0032` §Q3 재인용). 소비자와 실증 사례가 모두 없는 상태에서 그
소비자가 쓸 어휘를 먼저 Baseline에 새기는 것은 `BASELINE.md` §4 "필요한
것만 적절한 시점에 결정한 Architecture"·`ARCHITECTURE_GOVERNANCE.md`의
Architecture Need 정의("단순한 아이디어나 선호는 Architecture Need가
아니다")와 충돌한다. 이는 Phase A(`ADC-0032`)가 이미 확인한 것과 동일한
구조의 판단이며, Phase B 자체가 Phase A의 Defer를 전제로 열렸으므로
결론이 같은 방향으로 수렴하는 것은 일관성의 증거이지 반복적 회피가
아니다.

동시에, RFC-0025가 발견한 Gap 자체(§14.1이 Event/Message 전달 책임을
후보로도 등재한 적이 없다는 §2.2의 관찰, Message=Envelope/Event=내용물
구분이 (a)/(b)/(c) 선택과 무관하게 성립한다는 §6 관찰)는 유효한 기록으로
남긴다 — 이 ADC는 그 관찰을 Reject하지 않고, Accept하기에는 이르다고
판정할 뿐이다.

Q5는 이 Review에서 특히 신중히 다뤘다 — RFC-0025가 "배달 보장 수준을
논하지 않는다"고 스스로 선언한 것을 문면 그대로 신뢰하지 않고,
`ADC.md` 원문을 직접 재조회해 ADC-05·ADC-08의 상태·문구가 RFC-0025
이전과 완전히 동일함을 확인했다. 나아가 RFC-0025의 §6 미선택 상태가
오히려 ADC-05/08 해소의 **선결 조건**(Flow 적용 범위)조차 열어 두지
않았다는 구조적 이유까지 확인했다 — 이는 "언급하지 않았으니 우회가
아니다"는 소극적 판정이 아니라, "우회할 수 있는 구조 자체가 없다"는
적극적 확인이다.

## Conditions (재검토 Trigger)

아래 중 하나가 실제로 관찰되면 RFC-0025 §4~§7을 후속 ADC로 재상정할 수
있다. 관찰되지 않는 한 재상정하지 않는다.

1. **Multi-Agent Runtime의 실제 등장** — `ADC-02`(Runtime 존폐)가 Accept
   방향으로 해소되어 Runtime이 실제로 설계·구현되는 시점. 그 시점에
   Runtime이 소비할 State/Envelope 어휘가 비로소 실제 소비자를 갖는다.
2. **Agent↔Agent 통신의 실제 관찰** — 어느 HQ든 Agent 단위가 서로
   직접·간접으로 통신하는 실제 구현 시도가 관찰되는 시점(`Multi-Task`
   §16.4 Scoped 범위를 넘어서는 사례) — §6의 (a)/(b)/(c) 선택이 비로소
   실증 근거를 갖는다.
3. **ADC-05/08 해소 절차의 착수** — 두 항목이 별도로 해소 절차에
   들어가는 시점, RFC-0025 §7 Envelope 후보(Correlation/Time 등)가 그
   절차의 참고 자료로 재검토될 수 있다.
4. **RFC-0024/ADC-0032의 재상정** — Agent Domain/Lifecycle이 먼저
   Accept되면, Agent State(§4, Lifecycle State와는 다른 개념이지만
   같은 Runtime 소비 맥락을 공유)도 함께 재검토 대상이 된다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **없음.** `BASELINE.md` §6·§11·§13.3·§14.1
  어느 것도 재해석·수정되지 않는다 — 원문을 대조 재확인했을 뿐이다(Q1,
  Q4, Q5).
- **Contract Impact**: **없음.** §14에 Event/Message 관련 PR-*/G-*/X-*
  항목이 추가되지 않는다. HQ-level Contract도 신설되지 않는다.
- **Kernel Impact**: **없음.** 새 Concept·Layer·Component·enum·타입이
  추가되지 않는다. `GLOSSARY.md` 무변경.
- **Governance Impact**: `docs/decisions/adc/ADC.md`(ADC-01~12 등록부)의
  ADC-05·ADC-08 항목은 **문구·상태 모두 무변경**(Q5) — 이 ADC는 그
  목록에 신규 항목을 추가하지 않으며, `docs/architecture/core/` 트랙의
  RFC-0025↔ADC-0033 짝으로만 기록된다.

## Governance Chain 검증

`RFC-0025`(Proposed — State/Message/Event를 Candidate로 개설, 판단은
위임) → 이 `ADC-0033`(Decided — Q1·Q2·Q4 Not Accept/Defer, Q3·Q6 Open
유지, Q5 우회 없음 확인) → **ADR 없음**(Baseline 변경 대상이 없으므로
Migration Strategy 자체가 존재하지 않는다 — `ADC-0032`와 동일 구조).

- `RFC-0025` §11 Out of Scope·§12 Non-goals가 이 ADC의 판단 범위를
  벗어나지 않았는지 확인 — Event Bus 구현·Runtime 세부 구조·ADC-05/08
  해소 어느 것도 이 ADC가 설계·해소하지 않았다(위반 없음).
- `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준" 두 조건을 Q1·Q3·Q4에서
  명시적으로 대조했다.
- `RFC-0024`/`ADC-0032`의 Defer 판정과 모순되지 않는지 확인 — Q1이
  Agent State를 Lifecycle State와 별개로 다루면서도 동일한 Defer
  결론에 도달했으며, Lifecycle을 재확정하는 방식으로 우회하지 않았다
  (RFC-0025 §9 자체 점검을 이 ADC가 재확인).

## Validation — 문서 간 일관성 확인 (정적 검증)

- `git status --porcelain` — 이 ADC 파일 1건 추가 외 무변경 확인.
  `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·
  `docs/decisions/adc/ADC.md`·Production Code(`core/`, `hqs/`,
  `dashboard/`) **0줄 diff**.
- `grep -n "A-4\|조립은 시계" docs/architecture/baseline/BASELINE.md` —
  RFC-0025 §7 Time 필드 근거 인용("조립은 시계·난수·외부 I/O를 읽지
  않는다")이 §13.3 A-4·G-7 원문(283행, 437행)과 문자 그대로 일치함을
  확인.
- `docs/decisions/adc/ADC.md`에서 ADC-05·ADC-08 절 전체를 재조회 —
  RFC-0025 §2.1이 인용한 문구와 원문이 일치하며, 상태 모두 Open·
  우선순위 NEXT로 이 ADC 작성 전후 변화 없음을 확인(Q5).
- `BASELINE.md` §14.1 표(176~178행, 384~391행) 재조회 — Kernel 책임
  후보 8개(Task 전달/Capability 탐색/Engine 호출/Context 전달/Stable
  Prefix/Context Boundary/Context Assembly/Context Ordering) 목록에
  Event·Message 전달 책임이 여전히 없음을 재확인(RFC-0025 §2.2 인용과
  일치).
- 코드 변경이 없으므로 Production 회귀 테스트 대상이 아니다 — 이번
  세션 환경에는 `pytest` 모듈이 설치되어 있지 않으며(Phase A에서 이미
  확인), 코드 diff 0줄이므로 재실행 결과가 달라질 여지가 없다.

## Self Review

- Baseline/GLOSSARY/`IMPLEMENTATION_RULES.md`/`ADC.md`/Production
  Code를 변경했는가 — **아니오**(§Validation, `git status` 0 diff).
- RFC-0025의 Candidate를 설계·확장했는가 — **아니오** — Accept 여부만
  판단했다(Q1~Q4).
- Agent State를 Lifecycle State와 혼동해 Phase A를 재확정했는가 —
  **아니오**(Q1) — 별개 개념으로 다루면서도 독립적으로 동일한 Defer에
  도달했을 뿐이다.
- ADC-05·ADC-08을 이 김에 해소했는가 — **아니오**(Q5) — 상태·문구
  불변을 원문 재조회로 확인했을 뿐 판정을 내리지 않았다.
- Message/Event (a)/(b)/(c) 중 하나를 임의로 선택했는가 — **아니오**
  (Q3) — Open으로 유지했다.
- Envelope 자료구조·스키마를 확정했는가 — **아니오**(Q4) — 필드
  존재 여부 판단(Defer)만 내렸다.
- §10 귀속처를 확정했는가 — **아니오**(Q6) — 관찰과 결정을 분리해
  Open으로 유지했다.
- Agent Manager·Runtime·Event Bus에 새 권한을 부여했는가 — **아니오**
  (Q2) — 기존 확정·금지를 재인용했을 뿐이다.
- 권한 밖의 판단을 임의로 확정했는가 — **아니오**(Q3, Q5, Q6) — 전부
  Open 유지 또는 Defer로 판정했다.
- 재검토 Trigger를 관찰 가능한 형태로 남겼는가 — **예**(§Conditions
  1~4).
- `docs/decisions/adc/ADC.md`(ADC-01~12 등록부)에 새 항목을
  추가했는가 — **아니오** — 별도 트랙(`docs/architecture/core/`)을
  따랐다.
- ADR을 작성했는가 — **아니오** — Accept된 것이 없으므로 Migration
  Strategy 대상이 없다.
