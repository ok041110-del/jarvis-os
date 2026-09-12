# ADC-0032: Agent Domain & Lifecycle Contract — Governance Review (RFC-0024 후속)

## 목적

`docs/architecture/core/RFC-0024-agent-domain-and-lifecycle-contract.md`
§4(Agent Domain Model)·§5(Agent Lifecycle State Model)·§6(Agent ↔ Agent
Manager 책임 경계)·§8(귀속처 Open Question) 각각이 **지금 Baseline에
반영할 만큼 확정할 수 있는지**를 판단한다.

근거는 RFC-0024 원문과 그것이 인용한 Evidence, 그리고 이 Review가 추가로
확인한 다음 문서로 한정한다: `docs/architecture/baseline/BASELINE.md`
§3·§6·§7·§11·§14.6 N-3, `docs/00_governance/GLOSSARY.md`(Agent/Runtime/
Execution Unit 행), `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`("ADC
채택 기준"·"Architecture Need"), `hqs/development/IMPLEMENTATION_RULES.md`
(Registry/Scheduler/Event Bus 금지 표), `hqs/development/BASELINE.md`
(Frozen, "Development HQ는 Architecture Decision을 소유하지 않는다"),
`docs/decisions/adc/ADC.md`(Kernel 수준 Open Decision 등록부, ADC-01~12),
`archive/v1/docs/adr/0007-workflow-execution-model.md` 결정 3,
`docs/architecture/core/ADR-0011-*`(§16.6 Execution Unit 반영 선례 —
Kernel은 여전히 HQ Lifecycle만 안다는 확인), `docs/architecture/core/ADC-0008-*`
(Not Accepted 판정의 서술 형식 선례), `docs/research/DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`,
`hqs/investment/teams/stock_team.py`(`ThreadPoolExecutor` 관찰 — 유일한
"동시 실행" 실증 사례). **새로운 실험·프로토타입·측정은 수행하지 않는다.**

### 이 ADC가 판단하지 않는 것

- Agent Manager의 **구현·상세 설계** — 사용자 지시에 따라 이 Review는
  "현재 Governance가 허용하는 책임 범위"만 확인하고(§4), 그 이상을
  설계하지 않는다.
- Event Bus·Multi-Agent Workflow·Runtime 존폐(ADC-02, Open)·LangGraph
  채택 — RFC-0024 §7이 이미 Out of Scope로 둔 것을 이 ADC도 다루지
  않는다.
- `hqs/development/BASELINE.md`·`GLOSSARY.md`·`BASELINE.md`의 실제 문서
  수정 — 이 ADC는 **문서(ADC) 1건만 신설**하며, Baseline/Public
  Contract/Runtime 어느 것도 변경하지 않는다(사용자 지시).

---

## Q1. RFC-0024 §4 Agent Domain Model(Identity/Role/Capabilities/Input/Output/State/Result)은 Kernel Public Contract(§14)에 속하는가?

### Evidence

- `BASELINE.md` §7 HQ 책임: "Agent 구성 및 역할 결정." §14.6 N-3(Kernel
  Non-Goal): "Agent 관리 — Agent의 생성·구성·실행"을 제공하지 않으며,
  "닫지 않는 질문: 없음 — §7이 이미 HQ 책임으로 확정"이라고 **이미
  종결**되어 있다.
- §13.1 CM-4: "Kernel은 Content와 Source를 해석하지 않는다." §13.5:
  "HQ는 **무엇이** Context에 들어가야 하는가를 정한다." 이 원칙은 Context
  영역 한정 서술이지만, `ADR-0011` §2.4가 동일 원칙을 Workflow 실행
  State("종료 disposition의 내용·어휘는 HQ 도메인 책임")에도 적용한
  선례가 있다 — Domain 내용(Role/Capabilities가 무엇을 의미하는지)은
  일관되게 HQ 소관으로 판정되어 왔다.
- §14.1 계약 범위 표: 8개 Kernel 책임 후보 중 "Task 전달 책임"·"Capability
  탐색 책임"은 **미결**로 명시되어 있고, Agent Domain Model은 이 8개
  후보 어디에도 해당하지 않는다 — 신설 후보가 필요하다.

### Q1 결론

**아니다.** §7·N-3이 이미 "Agent 관리"를 HQ 책임으로 **확정**했고,
N-3의 "닫지 않는 질문" 열이 "없음"이라고 명시했으므로 이 질문은 이미
Baseline이 답한 질문을 다시 여는 것이 아니라, 그 답을 재확인하는
것이다. Agent Domain Model의 **내용**(각 필드가 무엇을 의미하는지)이
Kernel Public Contract(§14)에 속할 근거는 없다. §14에 PR-*/G-*/X-* 항목을
신설하는 것은 **Reject**한다.

## Q2. 그렇다면 HQ-level Domain Contract로 지금 Baseline(또는 HQ Baseline)에 반영해야 하는가?

### Evidence

- `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준": 새 ADC는 "①지금
  결정하지 않으면 상위 Architecture를 진행할 수 없다" 또는 "②결정이
  늦어질수록 되돌리는 비용이 매우 커진다" 중 하나를 반드시 만족해야
  한다.
- ① 검토: 현재 Development HQ는 `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`의
  비공식 표(Responsibility/Capability/Input/Output)만으로 v2.0 Freeze를
  통과했다(`DEV-HQ-V2.0-AGENT-LAYER-REFACTORING-AUDIT-0001.md` §6 "가능").
  즉 **지금 Domain Model이 없어서 막힌 상위 Architecture 진행이
  없다.** Investment HQ는 애초에 "Agent"라는 이름의 단위 자체를 쓰지
  않고 `stock_team.py`류 함수 모듈 + `ThreadPoolExecutor`로 구성된다
  (`RFC-0021` §1 관찰). 두 HQ가 이미 다른 어휘를 써 왔고 그로 인한
  실패 사례가 보고된 바 없다.
- ② 검토: "되돌리는 비용"이 커지려면 여러 HQ가 서로 다른 Domain Model을
  독립적으로 굳혀 나중에 통합 비용이 드는 상황이 관찰돼야 한다. 현재
  HQ는 Development 1개뿐이고, 그 문서(`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`)
  자체가 "새 Agent·새 Capability를 도입하지 않는다"고 못박은 Audit
  성격 문서라 굳어질 대상이 확장되고 있지도 않다. Investment HQ는
  애초에 이 어휘를 채택하지 않았으므로 "되돌릴 결정"이 존재하지 않는다.
- `BASELINE.md` §4 "Good Architecture Principle": "필요한 것만 적절한
  시점에 결정한 Architecture." 지금 결정을 내리면 이 원칙과 충돌한다 —
  실제 사용처가 하나(Development HQ, 그것도 비공식 형태로 이미 충분)뿐인
  상태에서 일반화된 Contract를 미리 만드는 것은 §4의 반례에 해당한다.

### Q2 결론

**아니다, 지금은 아니다(Not Accept — Defer).** ①·② 어느 기준도 충족하지
않는다. HQ-level Domain Contract로도 **지금 확정하지 않는다.** RFC-0024
§4는 **Reference로만 남긴다** — 향후 실제로 2번째 HQ가 "Agent"라는
동일 어휘를 채택하며 서로 다른 필드 구조를 굳히기 시작하는 시점, 또는
Development HQ의 비공식 표가 실제 유지보수 비용(불일치·재작업)을
일으키는 시점이 재검토 Trigger다(§Follow-up).

## Q3. RFC-0024 §5 Agent Lifecycle(REGISTERED→ASSIGNED→EXECUTING→{COMPLETED|FAILED}, RETIRED)은 기존 Agent 정의와 충돌하는가?

### Evidence

- `GLOSSARY.md` 12행: "Agent | 실제 업무를 수행하는 단위." `BASELINE.md`
  §7: Agent 책임 2문장(§4.1 Q1 인용). 이 두 곳 어디에도 State/Lifecycle
  개념이 존재하지 않는다 — **충돌할 기존 정의 자체가 없다.**
- v1 `archive/v1/docs/adr/0007-workflow-execution-model.md` 결정 3은
  Agent Lifecycle을 명시적으로 범위 밖에 두면서 재검토 시점을 "여러
  Agent가 장시간·비동기로 협업하는 Multi-Agent 운영 단계"로 지정했다.
  이 트리거가 v2에서 실제로 관찰됐는지 확인한 결과: Development HQ
  Stage 01~05는 고정 순서 **단일 패스**만 수행하고(`IMPLEMENTATION_RULES.md`
  "Stage 재진입 금지"), Investment HQ의 유일한 동시 실행 사례
  (`hqs/investment/teams/stock_team.py:164,190`)는 `with ThreadPoolExecutor(...)`
  블록 내부의 **짧은 수명 병렬 실행**이며 `Multi-Task`(§16.4, `ADC-0016`
  Scoped·Conditional)로 이미 다뤄지는 범위다 — "장시간·비동기 협업"에
  해당하지 않는다. **결정 3의 재검토 조건은 아직 충족되지 않았다.**

### Q3 결론

**충돌하지 않는다.** 대조할 기존 Lifecycle 정의 자체가 없으므로
형식적 충돌은 없다. 그러나 v1 결정 3이 지정한 재개설 조건(Multi-Agent
운영 단계 도래)이 v2에서 아직 관찰되지 않았으므로, 이 State Model을
**지금 확정할 근거도 없다** — Q2와 동일한 ADC 채택 기준 미충족.
**Not Accept — Defer.** RFC-0024 §5는 Reference로 남긴다.

## Q4. Agent Manager가 현재 Governance에서 가질 수 있는 책임 범위는 얼마인가?

> 사용자 지시에 따라 Agent Manager의 구현·설계는 하지 않는다. 이
> 질문은 "지금 무엇이 허용되는가"만 확인한다.

### Evidence

- `IMPLEMENTATION_RULES.md` 금지 표: Registry 구현 금지·Registry 일반화
  금지·Scheduler 구현 금지·Workflow orchestration/Dynamic Routing 금지·
  Event Bus 구현 금지 — 전부 현재도 유효(무변경, `RFC-0024` §12가 이미
  확인).
- `ADC-0006` §판단 대상에서 제외: "Agent class, Agent Runtime, Agent
  Registry, Agent Manager" 도입 자체가 그 ADC로 **승인된 적이 없다.**
- RFC-0024 §6 표의 "Candidate 영역"(복수 Agent 배분 결정, Agent 존재
  열거·조회, Agent 간 협업 순서 조정)은 각각 Scheduler 금지·Registry
  금지·Runtime 미결(ADC-02)에 해당한다.

### Q4 결론

**현재 허용 범위는 없다(전무).** "Agent Manager"라는 이름은 `ADC-0006`·
`RFC-0018`에 언급만 됐을 뿐 어떤 구현도 승인받은 적이 없고, 그 이름이
가질 만한 모든 후보 책임(배분 결정=Scheduler, 열거·조회=Registry, 협업
순서 조정=Runtime 미결)이 이미 개별적으로 금지·미결 상태다. RFC-0024
§6이 제안한 "Agent Manager가 Agent 자신의 전이 규칙을 재구현하지
않는다"는 예방적 원칙은 **현재 규제 대상이 존재하지 않으므로 공허하다**
(vacuously true) — Baseline에 지금 추가해도 실질적으로 막는 것이 없다.
**Baseline 반영 Not Accept** — Agent Manager가 실제로 제안되는 시점에
그 제안 자체의 RFC가 이 경계를 함께 정의하는 것이 더 실질적이다
(§Follow-up).

## Q5. RFC-0024 §8 귀속처 Open Question(Kernel-level vs HQ-level)을 이 ADC가 확정하는가?

### Q5 결론

**아니다 — Open Decision으로 유지한다.** Q2가 "지금은 어느 쪽도
아니다(Defer)"라고 판단했으나, 이는 "영원히 필요 없다"는 뜻이 아니다.
실제 Architecture Need가 관찰되는 시점에 Kernel-level(§6 Concept Model
확장, "실행 단위"처럼 §16 유사 설명 용어)과 HQ-level(Development HQ
Stage Data Contract처럼 개별 HQ Baseline에 등재) 중 무엇이 맞는지는
**그 시점의 Evidence로 후속 ADC가 판단**해야 한다. 이 ADC는 그 판단을
대신 내리지 않는다(§Out of Scope, 사용자 지시 "권한 밖의 판단은 임의로
확정하지 말고 Open Decision으로 남겨라").

---

## Decision

**Q1 — Reject**(Kernel Public Contract 신설 근거 없음, §7/N-3로 이미
종결).
**Q2 — Not Accept, Defer**(HQ-level Contract로도 지금 확정하지 않음 —
ADC 채택 기준 ①·② 모두 미충족).
**Q3 — 충돌 없음, 그러나 Not Accept, Defer**(v1 결정 3의 재개설 조건
미충족).
**Q4 — 확인만 함, 결정 아님**(현재 허용 책임 범위 = 없음).
**Q5 — Open Decision으로 유지**(이 ADC가 대신 판단하지 않음).

**RFC-0024는 Proposed 상태를 유지한다.** 이 ADC로 Accepted/Rejected 중
어느 쪽으로도 전환하지 않는다 — RFC-0024의 Candidate들이 "틀렸다"는
것이 아니라 "지금 결정할 근거가 부족하다"는 판단이며, 이는 §Follow-up의
재개설 조건이 충족되면 다시 열릴 수 있는 상태이지 폐기가 아니다.

## Status

**Decided — No Baseline/Contract/Runtime Change**

## Rationale

Q1~Q4가 공통으로 확인한 것은, RFC-0024의 세 Candidate(Domain Model,
Lifecycle, Agent Manager 경계) 중 어느 것도 이 저장소의 ADC 채택
기준("①지금 결정하지 않으면 진행 불가" 또는 "②되돌리는 비용이 커짐")을
충족할 만한 실제 압박이 없다는 점이다. Development HQ는 이미 비공식
형태로 충분히 동작하고 있고, Investment HQ는 애초에 이 어휘를 쓰지
않으며, v1이 지정한 "Multi-Agent 운영 단계" 재개설 조건은 두 HQ 어디서도
관찰되지 않았다. `BASELINE.md` §4 "필요한 것만 적절한 시점에 결정한
Architecture"·`ARCHITECTURE_GOVERNANCE.md`의 Architecture Need 정의("단순한
아이디어나 선호는 Architecture Need가 아니다")에 비추어, 지금 이
Contract를 Baseline에 편입하는 것은 실제 Need가 아니라 예상되는 미래
Need를 앞서 설계하는 것이 된다 — 이는 `ADR-0007` 결정 3이 원래 경계했던
바로 그 실수(아직 존재하지 않는 요구를 위해 설계하는 것)를 반복하는
것이다.

동시에, RFC-0024가 제기한 질문 자체(Gap이 실재한다는 §1~§3의 관찰)는
유효하며 폐기 대상이 아니다. 따라서 이 ADC는 Candidate를 "틀렸다"고
Reject하는 대신, Q2/Q3/Q4를 **"지금은 아니다(Not Accept, Defer)"**로
판정하고 명시적 재검토 Trigger를 남긴다.

## Conditions (재검토 Trigger)

아래 중 하나가 실제로 관찰되면 RFC-0024 §4/§5를 후속 ADC로 재상정할 수
있다. 관찰되지 않는 한 재상정하지 않는다.

1. **2번째 HQ의 실제 Agent 어휘 채택** — Development HQ 외의 HQ가 실제로
   "Agent" 단위 코드를 작성하며 `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`와
   다른 필드 구조를 쓰기 시작하는 시점(중복·불일치 비용이 실제로 발생).
2. **Multi-Agent 운영 단계의 실제 도래** — 어느 HQ든 Agent 단위가
   장시간·비동기로 협업하는 실제 구현 시도가 관찰되는 시점(v1 `ADR-0007`
   결정 3의 원 조건, `Multi-Task` §16.4 Scoped 범위를 넘어서는 사례).
3. **Agent Manager의 실제 제안** — Registry/Scheduler 금지의 Scoped
   해제가 논의되며 "Agent Manager"라는 이름의 구현이 실제로 제안되는
   시점 — 그 제안의 RFC가 Q4의 예방적 경계를 함께 정의해야 한다.
4. **`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`의 비공식 표가 실제 유지보수
   문제를 일으키는 시점** — 예: 필드 누락으로 인한 회귀, Stage 간
   불일치가 실제 버그로 관찰되는 경우.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **없음.** `BASELINE.md` §6·§7·§14·§14.6 N-3
  어느 것도 재해석되거나 수정되지 않는다 — 이미 확정된 내용을
  재확인했을 뿐이다(Q1).
- **Contract Impact**: **없음.** §14에 PR-*/G-*/X-* 항목이 추가되지
  않는다(Q1). HQ-level Contract도 신설되지 않는다(Q2).
- **Kernel Impact**: **없음.** 새 Kernel Concept·Layer·Component·enum·
  타입이 추가되지 않는다. `GLOSSARY.md`의 Agent 행("실제 업무를 수행하는
  단위")은 무변경.
- **Governance Impact**: `docs/decisions/adc/ADC.md`(Kernel 수준
  ADC-01~12 등록부)에 신규 항목을 추가하지 않는다 — 그 목록은 이
  Review보다 이전 세대의 Open Decision을 다루는 별도 트랙이며(§0 각주),
  이 ADC의 Q5 Open 상태는 `docs/architecture/core/`의 RFC-0024↔ADC-0032
  Governance Chain 자체로 추적된다.

## Governance Chain 검증

`RFC-0024`(Proposed — Domain Model·Lifecycle·경계를 Candidate로 개설,
판단은 위임) → 이 `ADC-0032`(Decided — Q1 Reject, Q2·Q3·Q4 Not
Accept/Defer, Q5 Open 유지) → **ADR 없음**(Baseline 변경 대상이 없으므로
Migration Strategy 자체가 존재하지 않는다 — `ADR-0008`~`ADR-0011`과 달리
이 트랙은 Accept가 아니므로 ADR 단계로 진행하지 않는다).

- `RFC-0024` §9 Out of Scope·§10 Non-goals가 이 ADC의 판단 범위를
  벗어나지 않았는지 확인 — Agent Manager 구현·Event Bus·Multi-Agent
  Workflow·LangGraph 어느 것도 이 ADC가 설계하지 않았다(위반 없음).
- `ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준" 두 조건을 Q2·Q3에서
  명시적으로 대조했다 — 자의적 판단이 아니라 절차가 정한 기준을 그대로
  적용했다.
- `hqs/development/BASELINE.md`("Development HQ는 Architecture Decision을
  소유하지 않는다")와 모순되지 않는다 — 이 ADC는 Jarvis OS
  Architecture Governance(`docs/architecture/core/`)트랙에서 진행됐고,
  Development HQ 자체의 Open Decision을 만들지 않았다.

## Validation — 문서 간 일관성 확인 (정적 검증)

- `git status --porcelain` — 이 ADC 파일 1건 추가 외 무변경 확인.
  `BASELINE.md`·`GLOSSARY.md`·`IMPLEMENTATION_RULES.md`·
  `hqs/development/BASELINE.md`·`docs/decisions/adc/ADC.md`·Production
  Code(`core/`, `hqs/`, `dashboard/`) **0줄 diff**.
- `grep -n "Agent" docs/00_governance/GLOSSARY.md` — Agent 정의("실제
  업무를 수행하는 단위")가 이 ADC의 §Q3 인용과 문자 그대로 일치함을
  확인(재인용 오류 없음).
- `grep -n "ThreadPoolExecutor" hqs/investment/teams/stock_team.py` —
  §Q3이 인용한 "짧은 수명 병렬 실행" 관찰(line 164, 190)이 실제 코드와
  일치함을 확인.
- `hqs/development/IMPLEMENTATION_RULES.md`의 Registry/Scheduler/Event
  Bus 금지 문구가 RFC-0024 §7·§9가 인용한 문구와 여전히 동일한지
  재확인(diff 없음 — RFC-0024 이후 이 파일이 변경되지 않았으므로 당연한
  결과이나, §Q4가 인용에 의존하므로 명시적으로 재확인했다).
- 이 ADC는 코드를 변경하지 않았으므로 Production 회귀 테스트 대상이
  아니다. 이번 세션 환경에는 `pytest` 모듈이 설치되어 있지 않아(이전
  RFC-0024 세션에서 이미 확인) 직접 재실행하지 않았다 — 코드 diff가
  0줄이므로 결과가 달라질 여지가 없다.

## Self Review

- Baseline/GLOSSARY/`IMPLEMENTATION_RULES.md`/`hqs/development/BASELINE.md`/
  Production Code를 변경했는가 — **아니오**(§Validation, `git status`
  0 diff).
- RFC-0024의 Candidate를 설계·확장했는가 — **아니오** — 오직 Accept
  여부만 판단했다(Q1~Q4).
- Agent Manager를 구현·설계했는가 — **아니오**(Q4) — "현재 허용 범위 =
  없음"만 확인했다.
- §14 Kernel Public Contract에 새 항목을 추가했는가 — **아니오**(Q1,
  §Architecture/Contract 영향).
- 권한 밖의 판단(귀속처 확정)을 임의로 내렸는가 — **아니오**(Q5) — Open
  Decision으로 명시적으로 남겼다.
- ADC 채택 기준을 자의적으로 적용했는가 — **아니오**(Q2, Q3) —
  `ARCHITECTURE_GOVERNANCE.md`의 두 조건을 그대로 인용해 대조했다.
- Q3 결론("충돌 없음")이 "채택 가능"을 의미하도록 흐렸는가 — **아니오** —
  같은 절에서 "충돌 없음"과 "Not Accept, Defer"를 분리해 명시했다.
- 재검토 Trigger를 관찰 가능한 형태로 남겼는가 — **예**(§Conditions
  1~4) — 추상적 "필요해지면"이 아니라 구체적 관찰 대상을 적었다.
- `docs/decisions/adc/ADC.md`(ADC-01~12 등록부)에 새 항목을 추가했는가 —
  **아니오**(§Architecture/Contract 영향 "Governance Impact") — 그
  목록은 별도 트랙이며 이 Review는 `docs/architecture/core/` 트랙(RFC↔ADC
  1:1 짝)을 따랐다.
- ADR을 작성했는가 — **아니오** — Accept된 것이 없으므로 Migration
  Strategy 대상이 없다(§Governance Chain 검증).
- Production Code·다른 문서를 이 ADC 작성 중 실수로 건드렸는가 —
  **아니오**(`git status --porcelain` 확인).
