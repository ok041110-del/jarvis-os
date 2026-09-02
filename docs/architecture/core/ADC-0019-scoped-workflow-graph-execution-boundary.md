# ADC-0019: §16.3~16.5 너머 Scoped Workflow Graph Execution Boundary — 존재 판단 (RFC-0019 후속)

## 목적

`docs/architecture/core/RFC-0019-langgraph-scoped-workflow-adapter-runtime-existence-boundary.md`
§8이 연 Boundary Question을 판단한다.

> §16.3~16.5가 이미 Accept한 범위를 넘어서는 Workflow 그래프 해석·실행
> 책임(조건부 분기·Loop·Checkpoint/Resume 포함)이, LangGraph라는
> 구체적으로 검증된 Adapter Evidence(v1 `ADR-0007` Accepted + 이번 세션
> 최신 버전 재확인)를 근거로, 지금 재검토 대상이 될 수 있는가?

이 ADC는 그 질문을 승격 여부를 가를 수 있는 형태로 조여서 판단한다:
**Jarvis OS는 §16.3(Execution Host)·§16.4(Multi-Task)·§16.5(Multi-Task
Result Store)가 Accept한 범위를 넘어서는, HQ가 정의한 Workflow 그래프의
조건부 분기·Loop·실행 상태 pause/resume을 포함하는 실행 순서 조립·진행
책임의 존재를, 그 셋과 별개의 Scoped Kernel Concept으로 지금 Accept하는가?**
판단 대상은 특정 구현체(LangGraph)가 아니라 **§16.3~16.5 너머의 Scoped
Workflow Graph Execution Boundary**다.

근거는 RFC-0019와 그것이 인용한 Evidence(v1
`archive/v1/docs/adr/0007-workflow-execution-model.md`(Accepted),
`archive/v1/adapters/workflow-langgraph/`,
`.claude/docs/integrations/langgraph.md`(이번 세션 PoC),
`docs/architecture/baseline/BASELINE.md` §6·§7·§15.2·§16.1~16.6,
`docs/decisions/adc/ADC.md` ADC-02,
`docs/architecture/core/RFC-0008`/`ADC-0008`,
`docs/architecture/core/RFC-0013`/`ADC-0013`,
`docs/architecture/core/RFC-0016`/`ADC-0016`,
`docs/architecture/core/RFC-0017`/`ADC-0017`,
`hqs/investment/checkpoint.py`,
`docs/core/execution-layer/MVP-0001-plan.md`,
`hqs/development/IMPLEMENTATION_RULES.md`)로만 한정한다. 새로운
Evidence·실험·Architecture를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- 구현체 선택 — LangGraph를 채택할지, v1처럼 순차 함수 호출을 유지할지.
- 명칭 — 이 책임을 Workflow Adapter / Workflow Engine 중 무엇으로 부를지
  (Execution Host가 `ADC-0014`로 별도 명명 절차를 거친 것과 같은 절차는
  후속 ADC가 담당).
- Public Port / Interface 정의 — §14.1이 "Task 전달 책임"을 여전히 계약
  범위 밖으로 두는 한, 새 Public Contract를 만들 근거가 없다.
- 구현 전략 — Adapter 래핑 방식, Checkpointer 백엔드 선택 등.
- v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계 자체 — 조건으로 이월할 뿐
  이 ADC가 설계하지 않는다(Q7).
- `docs/decisions/adc/ADC.md` ADC-02(Runtime 개념의 존폐)의 재판단 —
  이 ADC는 §6 넓은 정의의 부분집합 하나만 판단한다(Q8).
- `docs/architecture/core/ADC-0008`의 Not Accepted 전복 — 서로 다른
  범위의 별개 질문이다(Q8).
- Production 구현 착수 승인 — `hqs/development/IMPLEMENTATION_RULES.md`의
  "Workflow Parser/Scheduler/Runtime orchestration/Event Bus 구현 금지"는
  이 ADC로 해제되지 않는다(Q7).
- `hqs/investment/checkpoint.py`(§16.5)의 책임 재판단 또는 대체(Q5).
- Model/LLM Provider 호출을 다루는 Engine Adapter(§16.2)의 내부 구조(Q5).
- Multi-HQ, 자연어 요청 분해(`ADC-0018`, Defer) 범위로의 확장(Q4).

---

## Evidence 요약 (RFC-0019 인용 — 새 실험 없음)

**승격을 지지하는 쪽**

- **E1 — v1 `ADR-0007`(Accepted)**: LangGraph를 `IWorkflowEngine` Port의
  구현체로 실사용 검증했다. Team 생명주기 전이 규칙은 Core에 남기고
  (결정 2), LangGraph는 호출 순서만 조립하며(결정 1), 병렬 fan-out/fan-in을
  실제로 구성했고(결정 7), **Adapter Reversibility**를 통합 테스트로
  증명했다(결정 4 — LangGraph를 `SequentialWorkflowEngine`으로 교체해도
  Core/Organization Layer 무수정, `test_workflow_adapter_reversibility.py`).
- **E2 — 이번 세션 PoC**(`.claude/docs/integrations/langgraph.md`): 저장소
  밖 임시 디렉터리에서 langgraph 1.2.11을 설치해 State→Node→Conditional
  Edge→Loop→종료를 실행했고(4회 반복 후 정상 종료), `MemorySaver`
  Checkpointer로 중단 후 동일 `thread_id` 재개가 동작함을 확인했다
  (checkpoint 히스토리 6건). `langgraph`는 `langchain-core`에만 의존한다.
- **E3 — Architecture Intent**: `BASELINE.md` §6은 Workflow를 Definition으로
  이미 등재하고 "Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다"고
  기술한다. §7은 "Workflow의 도메인 내용"을 처음부터 Kernel 책임에서
  제외한다 — 이 ADC가 다루는 것은 내용이 아니라 그 내용을 실행하는 그래프
  해석·조립 책임의 소재다.
- **E4 — §3 Core Principle "Build < Integrate"**: 직접 구현보다 검증된
  오픈소스 통합을 우선한다(보조 근거).

**승격을 막는 쪽 (RFC-0019 §2.3이 스스로 명시한 공백)**

- **G1 — Rule B 미충족**: 독립 관찰은 사실상 2건(E1+E2)이며, 둘 다 동일
  계보(LangGraph)이고 프로덕션 트래픽이 아닌 PoC/Phase 검증이다. Governance
  v2 Rule B(3건 이상 독립 관찰)를 형식적으로 충족하지 못한다.
- **G2 — v1 ≠ v2 Architecture**: v1은 Team/Division을 Core Domain Model로
  가졌으나 v2 §5는 "Jarvis OS는 Team/Division의 존재를 알지 못한다"고
  명시한다. v1 `ADR-0007`의 Team 중심 결정(2·5·11)은 v2로 직접 이식할 수
  없다 — E1의 강도가 v2에 대해서는 부분 할인된다.
- **G3 — Port 공백의 상위 원인**: v1 결정 9(`IWorkflowEngine` Port)의 v2
  공백은 Team 부재가 아니라 §14.1이 "Task 전달 책임"을 계약 범위 밖으로
  두는 데서 온다 — 이 ADC 범위보다 상위의, 별도로 이미 Open인 질문이다.
- **G4 — `checkpoint.py`(§16.5)와의 관계 미정리**: 같은 "Checkpoint" 단어를
  쓰지만 계층이 다르다(저장 전 검증 게이트 대 그래프 실행 상태 pause/resume).
- **G5 — Evidence 성격**: RFC-0019가 가져온 것은 "외부 Adapter가 §16.4가
  제외한 영역을 Core 무수정으로 채울 수 있다"는 능력 증거이지, "Runtime
  세부 구조가 문제를 일으켰다"는 문제 재발 관찰(`ADC-0008` 재검토 조건 2번의
  문언)에 정확히 일치하지는 않는다 — 인접하되 동일하지 않다.

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가

### 검토

`BASELINE.md` §6은 Workflow를 Concept Model의 Definition으로 이미 두었고,
"Runtime은 Workflow를 참조하여 Task를 Agent에게 배분한다"는 문장으로
그래프 실행과 관련된 책임이 있을 수 있다는 신호를 남겼다. 그러나 같은 절이
"세부 구조는 Open Decision(ADC-02)"이라고 스스로 유보한다. §7은 Workflow의
도메인 내용을 Kernel 책임에서 제외하지만, 그 내용을 실행하는 **그래프
해석·조립 책임의 소재**는 명시하지 않는다.

### Q0 결론

`ADC-0008`/`ADC-0013`/`ADC-0016` Q0과 동일하게, 이 Intent는 단독으로
Accept 근거가 되지 못한다 — 원문 스스로 미결정임을 명시하기 때문이다.
Intent는 "조건부·반복 조율과 관련된 무언가가 필요할 수 있다"는 신호만
줄 뿐, 그 정체나 범위를 판단하지 못한다. §2 Evidence와 결합해야 한다.

---

## Q1. 실제 필요성 — E1(v1 `ADR-0007`) + E2(이번 세션 PoC)가 보여주는 것

### 검토

§16.3~16.5의 세 차례 Accept를 합쳐도 "이미 고정된 소수의 독립 실행 단위를
동시에 시작하고 결과를 모으는 것"까지만 가능하다(§16.4: "우선순위 판단,
조건부 분기, Workflow 그래프 해석, Agent 동적 선택은 포함하지 않는다").
실행 중 상태에 따라 다음 단계가 갈라지는 것(Conditional Edge), 조건을
만족할 때까지 반복하는 것(Loop), 그 중간 상태를 저장했다 이어서 실행하는
것(Checkpoint/Resume)은 세 Accept 모두가 명시적으로 제외한 영역이다.

이 저장소의 `archive/v1`은 바로 이 미검토 영역의 실행을 LangGraph로
실사용 검증한 이력이 있다(E1, `ADR-0007`, Accepted). E1은 그 실행을
**Core를 전혀 수정하지 않고** Adapter로 담을 수 있음을 통합 테스트로
증명했다(Reversibility, 결정 4). E2는 그 능력이 v2 시점(langgraph 1.2.11)에도
API 수준에서 유효함 — `StateGraph`/`add_conditional_edges`/`compile()` 및
Checkpointer가 하위 호환을 유지함 — 을 별도 PoC로 재확인했다.

두 Evidence를 합치면: "조건부 분기·Loop이 있는 Workflow 실행"이라는 §16.4가
제외한 영역에서, 실제로 동작하는 구체적 구현체가 Core 무수정으로 그 영역을
채울 수 있다는 것이 한 번(E1) 실증되고 최신 버전에서 한 번(E2) 더
확인되었다.

### Q1 결론

이 관찰이 답하는 질문은 "Runtime이라는 이름의 Concept이 필요한가"가 아니라
RFC-0019 §8이 좁힌 그대로다 — "§16.3~16.5 너머의 조건부 분기·Loop·Checkpoint
실행 책임이 실제로 채워질 수 있는가." **이 좁은 능력에 한해서는 Evidence가
존재를 지지한다.**

---

## Q2. Evidence 2건·동일 계보·Rule B 미충족이 Accept를 막는가 (핵심 판단)

### 검토

RFC-0019는 Rule B 충족을 주장하지 않는다(§Non-goals). 독립 관찰은
사실상 2건(E1+E2), 둘 다 LangGraph 계보이며 v2 프로덕션 트래픽이 아니다
(G1). 관건은 선례가 세운 원칙 — **Rule B 형식 미충족은, 판단 범위가 충분히
좁아 Rule B가 겨냥하는 위험(넓고 되돌리기 어려운 결정을 우연한 관찰로
성급히 확정)이 실재하지 않을 때에만 Accept를 막지 못한다**(`ADC-0013` Q2) —
을 이 대상에 적용했을 때 어떻게 되는가이다.

| 기준 | `ADC-0013` (Accept) | `ADC-0016` (Accept) | 이 ADC 대상 |
|---|---|---|---|
| 관찰 건수 | 5건(+1) | 1건 | 2건 |
| 다양성 | 서로 다른 실행 대상·전략, 부재 시 정확성 결함 재현 | 단일 사례 | 동일 계보 반복 — 다양성 없음 |
| Evidence 현재성 | 현행 v2 프로토타입 | 이미 `main` 병합된 Production Code | v1(교차 Architecture) + 저장소 밖 PoC |
| 형식 미충족 대체 요소 | 관찰 다양성 | "이미 존재하는 것" | 없음 |
| 판단 범위 폭 | 단일 실행 단위 격리 (좁음) | 고정된 소수 독립 호출 동시 시작 (좁음) | 조건부 분기 + Loop + Checkpoint (더 넓고 되돌리기 어려움) |

정직하게 보면 이 대상은 `ADC-0013`이 형식 미충족을 넘어선 경로(관찰
다양성)도, `ADC-0016`이 넘어선 경로(현행 프로덕션 코드)도 갖지 못한다.
동시에 판단 범위는 두 선례보다 넓다 — RFC-0019 §5가 재설계 필요한 진짜
공백 4개(v1 결정 2/5/9/11)를 스스로 식별한 것이 그 폭의 증거다. 따라서
"범위가 좁아서 형식 미충족이 결정적이지 않다"는 `ADC-0013` Q2의 논거를
그대로 끌어오기는 어렵다.

그러나 그것이 Accept를 봉쇄하지는 않는다. 남은 길은 **Accept의 범위를
RFC-0019 §7 Pseudo-Contract 수준으로 극소화하고**(Q3의 A-IN 다섯 항목만,
Q4의 A-OUT 전부 제외), **검증되지 않은 v2 공백을 명시적 조건으로 이월하며**
(Q7), **Reversibility를 필수 불변조건으로 못박는 것**(Q6)이다. 이는
`ADC-0013`의 방법(범위 좁힘)과 `ADC-0016`의 방법(조건부 이월)을 **함께**
적용하는 것이며, 두 방법을 동시에 쓰는 이유는 이 대상의 범위 폭이 어느
한쪽만으로는 부족하기 때문이다.

- 극소화된 A-IN은 "무엇을 실행할지"를 결정하지 않고(도메인 내용은 HQ),
  Domain Lifecycle·Policy·Registry·Event Bus·Result Store 게이트를
  건드리지 않는다(Q4). 이 상태에서 이 책임을 순차 함수 호출로 교체해도
  Kernel/HQ 코드가 바뀌지 않는다는 Reversibility(Q6)가 성립하면, "성급히
  확정해 되돌릴 수 없게 되는" 위험 자체가 계약 수준에서 차단된다.
- v1 결정 2/5/9/11 공백은 "Accept의 미해결 조건"으로 이월되어, 후속
  Architecture 절차가 이를 다루기 전에는 Public Contract 승격·구현 착수가
  불가능하다(Q7) — Evidence 부족이 무시되지 않는다.

### Q2 결론

**Rule B 형식 미충족(Evidence 2건·동일 계보)은 명백한 사실이며, 이 대상에서는
`ADC-0013`/`ADC-0016`보다 무겁게 작용한다.** 그럼에도 Accept가 가능한 것은,
범위를 §7 Pseudo-Contract 수준으로 극소화하고(Q3·Q4) 검증되지 않은 공백을
조건으로 이월하며(Q7) Reversibility를 필수 불변조건으로 요구할(Q6) 때에
한해서다. 이 세 장치가 모두 성립하지 않으면 이 Accept는 성립하지 않는다.
§6 전체(Workflow 참조 전체 + Agent 동적 배분)에는 Rule B를 그대로 적용해
미충족으로 남긴다.

---

## Q3. A-IN — 인정되는 책임 범위의 확정

### 검토

RFC-0019 §7의 책임·불변조건·경계를 이 ADC가 Decision으로 확정한다. 인정되는
범위는 HQ가 이미 정의한 Workflow 그래프와 이미 구성된 실행 단위를 입력으로
받아, 그 그래프가 기술하는 다음 다섯을 진행시키는 것으로 한정한다.

1. **State** — 공유 실행 상태의 보유.
2. **Node** — 단일 실행 단계의 진행.
3. **Conditional Edge** — 실행 중 상태에 따른 조건부 분기.
4. **Loop** — 조건 만족까지의 반복.
5. **값 기반 Checkpoint/Resume** — 진행 상태(어느 Node에 있는지, 무엇을
   반복 중인지)를 값으로 표현하고, 호출자가 그 값을 보관했다 반환하면
   이어서 진행하는 것.

5번은 Adapter가 영속화 계층을 소유한다는 뜻이 아니다. `BASELINE.md` §15.2가
Kernel Context Assembly에 이미 적용한 패턴 — "이 흐름에는 영속화 지점이
없다... 호출자가 그 값을 들고 있는 것이지 Kernel이 저장하는 것이 아니다" —
와 동일하게, 이 책임은 Checkpoint 값을 **생산**할 뿐 그 값의 영속화·복원은
호출자(및 실제 Checkpointer 백엔드 선택)의 몫으로 남는다.

경계: 이 책임이 개입하는 구간은 "HQ가 실행 단위를 이미 구성한 이후 ~ 그
실행이 모두 끝나는 시점까지"로 한정된다. 출력은 성공/실패/취소에 준하는
상태를 **값으로** 표현하며 예외를 던지지 않는다(§14.3 G-6 No Silent Failure와
동일 원칙).

### Q3 결론

**A-IN을 위 다섯 항목 + 값 기반 표현 + 한정된 개입 구간으로 확정한다.**
이보다 넓은 어떤 책임도 이 Accept에 포함되지 않는다.

---

## Q4. A-OUT — 명시적으로 제외되는 범위

### 검토

RFC-0019 §4·§7이 "Core가 계속 소유해야 하는 책임"으로 나열한 것과 §Out of
Scope를 이 ADC가 Decision으로 확정한다. 다음은 이 책임에 포함되지 않으며,
이 책임의 어떤 구현체도 이를 소유·재구현·대체하지 않는다.

- **HQ Routing / Registry** — 어떤 HQ가 선택되는가. (§7 System Boundary가
  이미 확정한 "HQ/Agent의 등록과 발견"에 속한다.)
- **Policy 판정(PDP/PEP)** — Agent가 이 Capability를 써도 되는지.
- **Capability / Connector Discovery** — 어떤 Agent가 어떤 Capability로
  발견되는가.
- **Domain Lifecycle 전이 규칙** — HQ/Agent의 상태 전이 자체(HQ가 소유하는
  Domain 로직을 Adapter가 재구현하지 않는다, v1 `ADR-0007` 결정 2·대안 B
  기각과 동일 원칙).
- **Event Bus** — Event 발행은 할 수 있으나 구독·라우팅은 소유하지 않는다
  (§16.6 Defer 유지, v1 결정 8).
- **§16.5 Multi-Task Result Store 저장 전 검증 게이트** — 겹치는 저장 검증
  로직을 새로 만들지 않는다.
- **Multi-HQ 및 자연어 요청 분해**(`ADC-0018` 범위) — 이 Accept는 단일 HQ
  안에서의 Workflow 그래프 실행만 다룬다.
- **Registry / Discovery 일반화** — 여러 Workflow 구현체가 동시에 존재하고
  런타임에 선택되는 구조를 만들지 않는다(v1 결정 12,
  `IMPLEMENTATION_RULES.md` "Registry 일반화 금지").

### Q4 결론

**A-OUT을 위 목록으로 확정한다.** 이 항목들은 이 Accept 이후에도 각자의
기존 상태(Open / Defer / 별도 Accept)를 그대로 유지한다.

---

## Q5. §16.3~16.5 기존 Accept 및 `checkpoint.py`·Engine Adapter와의 경계

### 검토

- **Execution Host(§16.3)와 겹치지 않는다.** Execution Host는 "이미 dispatch가
  결정된 단일 실행 단위"의 실행 격리(Execution Isolation)만 다룬다. 이 책임은
  그 반대편 질문 — "무엇을, 어떤 순서로, 어떤 조건으로" dispatch할지 — 를
  다룬다. `ADC-0016` §Q3 구도(Execution Host=Isolation, Multi-Task=Coordination)를
  연장하면, 이 책임은 **Coordination의 조건부·반복 확장**이다.
- **Multi-Task(§16.4)를 넓히지 않는다.** §16.4는 "이미 고정된 소수의 독립
  실행 단위"만 다룬다. 이 책임은 그 "고정" 자체가 실행 중 조건에 따라
  달라지는 경우(Conditional Edge)와 같은 단계가 반복되는 경우(Loop)를
  다룬다 — §16.4가 명시적으로 제외한 바로 그 영역이며, §16.4의 범위를
  수정하는 것이 아니라 그 옆의 빈자리를 여는 것이다.
- **Multi-Task Result Store(§16.5)를 대체하지 않는다.** §16.5는 저장 **직전**
  결과의 유효성 검증 게이트이고, LangGraph류 Checkpointer는 그래프 실행
  **전체 상태**의 pause/resume이다. 계층이 다르며 하나가 다른 하나를 함의하지
  않는다. `hqs/investment/checkpoint.py`의 저장 전 검증 책임은 §16.5 그대로
  유지되고 별도 절차 없이 자동으로 대체되지 않는다(G4).
- **Engine Adapter(§16.2)와 혼동하지 않는다.** Engine Adapter는 Model/LLM
  Provider 호출 어댑터다. 이 책임(Workflow Adapter 계층)이 "어떤 Agent를
  어떤 순서로 실행할지"를 조립하면, 그 Agent 실행 **내부**에서 필요하면
  Engine Adapter가 별도로 Model을 호출한다. 이 책임은 Engine Adapter를
  대체하거나 흡수하지 않는다(RFC-0019 §3).

### Q5 결론

**§16.3·§16.4·§16.5의 범위는 이 Accept로 전혀 넓어지거나 좁아지지 않으며,
`checkpoint.py`와 Engine Adapter(§16.2)도 건드리지 않는다.** 이 책임은
§6 Runtime 정의 중 "조건부·반복 조율"에 해당하는 별개의, 더 좁은 Concept
후보다.

---

## Q6. Reversibility를 필수 불변조건으로 — v1 `ADR-0007` 기반 후속 검증 요구

### 검토

이 Accept가 "존재는 인정하되 구현체·명칭·Port는 미확정"으로 안전하게
성립하려면, 구현체 선택의 오판이 Kernel/HQ로 번지지 않고 되돌릴 수 있음이
계약 수준에서 보장돼야 한다. RFC-0019 §7 Reversibility 조건을 이 ADC가
**필수 불변조건**으로 확정한다.

- 이 책임의 어떤 구현체(LangGraph 포함)를 제거하고 다른 구현체(최소한으로는
  순차 함수 호출)로 교체해도, Kernel과 HQ가 정의하는 코드는 한 줄도 수정되지
  않아야 한다.
- 구현체 고유 문법(`StateGraph`/`START`/`END`/Checkpointer API 등)은 이
  책임의 경계 안에서만 쓰여야 한다 — HQ나 Kernel이 이 문법을 알게 되면
  Reversibility가 깨진다.

이 조건은 새로 만드는 규칙이 아니다. v1 `ADR-0007` 결정 4와
`test_workflow_adapter_reversibility.py`가 LangGraph를 `SequentialWorkflowEngine`으로
교체해도 Core/Organization Layer 무수정임을 통합 테스트로 이미 증명한
선례가 있다. 다만 v1↔v2 Architecture 불일치(G2)로 그 증명의 강도는 v2에
대해 부분 할인되므로, 이 조건은 후속 ADR이 Baseline에 반영할 때 **v2 맥락의
통합 테스트 수준 검증 요구사항**으로 명문화되어야 한다.

### Q6 결론

**Reversibility를 이 책임의 필수 불변조건으로 확정하고, v1
`test_workflow_adapter_reversibility.py`를 선례로 하여 후속 ADR/구현 지침이
v2 통합 테스트로 이를 재현하는 것을 선행 요구사항으로 정의한다.**

---

## Q7. v1 `ADR-0007` 결정 2/5/9/11의 v2 공백 — 조건 이월

### 검토

RFC-0019 §5는 v1의 12개 결정 중 대부분(1, 3, 4, 6, 8, 10, 12)은 v2로 옮길
수 있으나 4개(2, 5, 9, 11)는 재설계가 필요한 진짜 공백이라고 정리했다.

- **결정 2·5·11**의 공백 원인은 **Team/Division 부재**다 — v2 §5 Meta
  Architecture에 대응물이 없어, Core가 소비할 생명주기(결정 2)·경계(결정 5)·
  State Model(결정 11)을 그대로 옮길 수 없다.
- **결정 9**(`IWorkflowEngine` Port)의 공백 원인은 Team 부재가 아니라 §14.1이
  "Task 전달 책임"을 계약 범위 밖으로 두는 것이다(G3) — 이 RFC/ADC 범위보다
  상위의, 별도로 이미 Open인 Kernel Public Contract 확장 질문이다.

이 ADC는 이 4개 공백을 침묵하지 않고 **Accept의 미해결 조건**으로 명시
이월한다. 즉:

- 이 4개 공백이 후속 Architecture 절차(ADR 또는 필요 시 별도 RFC)로 다뤄지기
  전에는, 이 책임을 v2 Kernel Public Contract(§14)로 승격하거나 Production
  구현에 착수할 수 없다.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Workflow Parser/Scheduler/Runtime
  orchestration/Event Bus 구현 금지" 조항은 이 ADC로 해제되지 않는다 —
  §16.3이 Execution Host 범위에서만 해제됐던 것과 동일한 원칙이며, 이 책임의
  범위는 아직 Baseline에 반영조차 되지 않았다.

이는 `ADC-0016`이 관찰 1건으로 존재를 Accept하되 Data/Artifact Isolation을
최소 안전조건으로 이월한 것과 동일한 구조다 — "존재는 Accept하되, 검증되지
않은 부분은 조건으로 남긴다."

### Q7 결론

**v1 결정 2/5/9/11의 v2 재설계는 이 ADC가 설계하지 않고 후속 Architecture/ADR
조건으로 이월한다. 그 완료 전에는 Public Contract 승격·구현 착수를 허용하지
않으며, `IMPLEMENTATION_RULES.md` 금지 조항도 유효하게 유지된다.**

---

## Q8. ADC-02·ADC-0008 불변 / LangGraph 채택·명칭·Port·구현 전략 미확정

### 검토

- **`docs/decisions/adc/ADC.md` ADC-02(Open·NOW)를 갱신하지 않는다.** ADC-02가
  다루는 §6 넓은 정의(Workflow 참조 **전체** + Agent 동적 배분)는 이 ADC
  판단 후에도 여전히 미결이다. 이 ADC는 그중 "조건부·반복 조율"이라는 좁은
  조각 하나만 판단했다. `ADC-0013`/`0016`/`0017`이 각자 슬라이스를 Accept하고도
  ADC-02 항목을 건드리지 않고 ADR+Baseline Update로 위임한 것과 동일하다.
- **`docs/architecture/core/ADC-0008`의 Not Accepted를 전복하지 않는다.**
  `ADC-0008`은 §6 넓은 "유지 대 대체"를 판단 대상으로 삼았고, 그 범위에서는
  지금도 Evidence가 부족하다. 이 ADC는 RFC-0019가 새로 연 좁은 질문만
  판단했다 — 서로 다른 범위의 질문이므로 별개 Decision이며 모순이 아니다
  (`ADC-0013` §Decision Rationale와 동일 논리).
- **LangGraph 채택·명칭·Public Port·구현 전략을 확정하지 않는다.** LangGraph는
  §Evidence(E1·E2)에서 근거로만 등장하며, JQ의 어휘는 구현 중립적이다.
  Execution Host가 존재(`ADC-0013`) → 명명(`ADC-0014`) → 구현 전략(`ADC-0015`)
  3단계로 분리한 선례를 그대로 따라, 명칭과 구현체 선택은 각각 별도 ADC로
  넘긴다.

### Q8 결론

**ADC.md의 ADC-02 항목과 `ADC-0008`의 Not Accepted는 이 ADC로 갱신·전복되지
않는다. LangGraph 채택 여부·명칭·Public Port·구현 전략은 이번 ADC에서
확정하지 않는다.**

---

## Decision

**A. Accept (Scoped, Conditional)**

RFC-0019 §8의 좁은 Boundary Question — §16.3~16.5가 Accept한 범위를 넘어서는,
HQ가 정의한 Workflow 그래프의 조건부 분기·Loop·실행 상태 pause/resume을
포함하는 실행 순서 조립·진행 책임 — 의 **존재**를 Accept한다. 판단 대상은
특정 구현체(LangGraph)가 아니라 **§16.3~16.5 너머의 Scoped Workflow Graph
Execution Boundary**다. 이 Accept는 아래 여섯 조건 위에서만 유효하다.

1. **범위 (A-IN)** — HQ가 이미 정의한 Workflow 그래프와 이미 구성된 실행
   단위를 입력으로 받아, 그 그래프가 기술하는 다음 다섯을 진행시키는
   책임으로 한정한다: (a) 공유 실행 상태(State)의 보유, (b) 단일 실행
   단계(Node)의 진행, (c) 실행 중 상태에 따른 조건부 분기(Conditional Edge),
   (d) 조건 만족까지의 반복(Loop), (e) 진행 상태를 값으로 표현하고, 호출자가
   그 값을 보관했다 반환하면 이어서 진행하는 것(값 기반 Checkpoint/Resume).
   이 책임은 영속화 계층을 소유하지 않는다 — Checkpoint 값을 **생산**할 뿐,
   그 값의 저장·복원은 호출자의 몫이다(`BASELINE.md` §15.2 패턴과 동일).
   실행 결과는 예외가 아닌 값으로 표현한다(§14.3 G-6).

2. **명시적 제외 (A-OUT)** — HQ Routing/Registry, Policy 판정(PDP/PEP),
   Capability/Connector Discovery, Domain Lifecycle 전이 규칙, Event Bus
   구독·라우팅, §16.5 Result Store 저장 게이트, Multi-HQ 및 자연어 요청
   분해(`ADC-0018` 범위), Registry/Discovery 일반화는 이 책임에 포함되지
   않으며, 이 책임의 어떤 구현체도 이를 소유·재구현·대체하지 않는다.

3. **§16.3~16.5 불가침** — 이 Accept는 Execution Host(§16.3)·Multi-Task(§16.4)·
   Multi-Task Result Store(§16.5)의 범위를 넓히거나 좁히지 않는다. 이 책임은
   그 셋의 확장이 아니라, §6 Runtime 정의 중 "조건부·반복 조율"에 해당하는
   별개의, 더 좁은 Concept 후보다. `hqs/investment/checkpoint.py`와 LangGraph류
   Checkpointer는 계층이 다르며(저장 게이트 대 그래프 실행 상태 pause/resume),
   하나가 다른 하나를 함의하지 않는다.

4. **Reversibility 필수 불변조건** — 이 책임의 어떤 구현체(LangGraph 포함)를
   제거하고 다른 구현체(최소한으로는 순차 함수 호출)로 교체해도, Kernel과
   HQ가 정의하는 코드는 한 줄도 수정되지 않아야 한다. 구현체 고유 문법은
   이 책임의 경계 안에서만 쓰인다. 이 조건은 v1 `ADR-0007` 결정 4와
   `test_workflow_adapter_reversibility.py`가 이미 실증한 선례를 근거로,
   후속 ADR이 Baseline 반영 시 **v2 맥락의 통합 테스트 수준 검증 요구사항**으로
   명문화한다.

5. **조건 이월 (Conditional)** — RFC-0019 §5가 식별한 v2 재설계 공백, 즉
   v1 `ADR-0007` 결정 2(Core 소유 Lifecycle 소비)·5(Team/Division 경계)·
   9(`IWorkflowEngine` Port)·11(State Model)의 v2 대응 부재는 이 Accept로
   해소되지 않는다. 이 네 공백이 후속 Architecture 절차(ADR 또는 필요 시
   별도 RFC)로 다뤄지기 전에는, 이 책임을 v2 Kernel Public Contract(§14)로
   승격하거나 Production 구현에 착수할 수 없다.
   `hqs/development/IMPLEMENTATION_RULES.md`의 "Workflow Parser/Scheduler/Runtime
   orchestration/Event Bus 구현 금지" 조항은 이 ADC로 해제되지 않는다.

6. **미확정 항목** — 이 Accept는 구현체 선택(LangGraph 채택 여부 포함),
   명칭(Workflow Adapter/Workflow Engine 등), Public Port 정의, 구현 전략을
   확정하지 않는다. Execution Host가 존재(`ADC-0013`) → 명명(`ADC-0014`) →
   구현 전략(`ADC-0015`) 3단계로 분리한 선례를 그대로 따른다.

### Reason

- **Q0** — Architecture Intent는 단독 근거가 되지 못하지만, Workflow가
  §6 Definition으로 이미 존재하고 §7이 "도메인 내용은 HQ, 그래프 해석·조립
  책임의 소재는 미결"로 남긴 신호는 일관됐다.
- **Q1** — E1(v1 `ADR-0007`, Accepted)이 조건부 분기·Loop 실행을 Core
  무수정으로 채울 수 있음을 프로덕션에서 검증했고(Reversibility 통합 테스트
  포함), E2가 그 능력이 최신 버전에서도 API 수준으로 유지됨을 재확인했다 —
  이 좁은 능력에 한해 Evidence가 존재를 지지한다.
- **Q2** — Evidence 2건·동일 계보로 Rule B 형식은 미충족이며, 이 대상에서는
  `ADC-0013`/`ADC-0016`보다 무겁게 작용한다. 그럼에도 Accept가 가능한 것은,
  범위를 §7 Pseudo-Contract 수준으로 극소화하고(조건 1·2), 검증되지 않은
  v2 공백을 조건으로 이월하며(조건 5), Reversibility를 필수 불변조건으로
  요구할(조건 4) 때에 한해서다 — `ADC-0013`의 범위 좁힘과 `ADC-0016`의
  조건부 이월을 **함께** 적용한다.
- **Q3·Q4** — A-IN 다섯 항목과 A-OUT 전 항목을 Decision으로 확정함으로써,
  이 책임이 커질 여지를 문서 수준에서 봉쇄한다.
- **Q5** — §16.3~16.5·`checkpoint.py`·Engine Adapter와의 경계가 명확히
  분리되므로, 이 Accept가 기존 Accept를 흔들 위험이 없다.
- **Q6** — Reversibility를 필수 불변조건으로 못박음으로써, 구현체 선택의
  오판이 Kernel/HQ로 번지지 않고 되돌릴 수 있음이 계약 수준에서 보장된다.
- **Q7** — v1 결정 2/5/9/11의 v2 공백을 침묵하지 않고 조건으로 명시 이월하며,
  Public Contract 승격·구현 착수를 차단한다 — Evidence 부족을 무시하지
  않으면서 불필요한 Defer를 피하는 방법이다.

### Decision Rationale

이 Decision은 `ADC-02`(Open)를 갱신하지 않는다 — `ADC-02`가 다루는 §6 넓은
정의(Workflow 참조 전체 + Agent 동적 배분)는 여전히 미결이며, 이 ADC는
그중 "조건부·반복 조율"이라는 좁은 조각 하나만 판단했다. `ADC-0008`의
Not Accepted도 뒤집지 않는다 — `ADC-0008`은 넓은 "유지 대 대체"를 판단
대상으로 삼았고, 이 ADC는 RFC-0019가 새로 연 좁은 질문만 판단했다. 서로
다른 범위의 질문이므로 별개 Decision이며 모순이 아니다(`ADC-0013` §Decision
Rationale와 동일 논리). `ADC-0013`/`0014`/`0015`(Execution Host)·`ADC-0016`
(Multi-Task)·`ADC-0017`(Result Store 게이트)의 Accept 범위도 이 Decision으로
전혀 넓어지지 않는다 — 이 Decision은 그와 분리된 새 책임 하나를 좁게
Accept했을 뿐이다. "Rule B를 범위 좁히기로 우회했다"는 비판이 가능하나,
그 범위 좁히기는 이 ADC가 아니라 RFC-0019 §7·§8이 이미 수행했고, 이 ADC는
그 좁힌 범위와 조건 이월에 대해서만 판단했다 — §6 전체에는 Rule B를 그대로
적용해 미충족으로 남긴다.

---

## Implementation Boundary (다음 Production 구현을 위한 최소 책임 범위)

이 Accept는 Production 구현을 지금 승인하지 않는다 — 아래는 향후 ADR·Baseline
Update가 이 책임을 등재할 때 참고할 **최소 책임 경계**다.

**포함(이번에 존재를 Accept한 것)**:

- HQ가 정의한 Workflow 그래프 + 이미 구성된 실행 단위를 입력으로 받아,
  State 보유 / Node 진행 / Conditional Edge 분기 / Loop 반복 / 값 기반
  Checkpoint·Resume을 진행시키는 책임.
- 실행 결과(성공/실패/취소에 준하는 상태)를 예외가 아닌 값으로 표현하는
  책임(No Silent Failure, G-6과 동일 원칙).
- 개입 구간을 "HQ가 실행 단위를 구성한 이후 ~ 그 실행이 모두 끝나는
  시점까지"로 한정 — Kernel Routing, Policy 판정, Capability/Connector 탐색은
  이 구간 이전에 끝나 있어야 한다.
- Reversibility(조건 4)가 v2 통합 테스트로 검증된 구현에 한해 적용된다는
  전제.

**제외(이번 Accept가 결정하지 않는 것 — 후속 절차로 위임)**:

- 구현체 선택(LangGraph 채택 여부 포함), 명칭, Public Port(§14) 정의, 구현
  전략.
- v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계 — 후속 Architecture/ADR 조건,
  완료 전 Public Contract 승격·구현 착수 불가.
- A-OUT 전 항목(Routing/Registry, Policy, Discovery, Domain Lifecycle,
  Event Bus, Result Store 게이트, Multi-HQ decomposition).
- `BASELINE.md` §6의 넓은 정의(Workflow 참조 전체 + Agent 동적 배분) — 이
  Accept로 검증되지 않는다.
- `IMPLEMENTATION_RULES.md`의 관련 금지 조항 — 이 좁은 범위에 한한 Scoped
  해제는 후속 ADR의 몫이며, Scheduler/우선순위/Workflow orchestration/Event
  Bus/§6 넓은 Runtime 구현은 계속 금지.

---

## Risks

| 위험 | 설명 | 완화 |
|---|---|---|
| Evidence 2건·동일 계보 | E1+E2가 모두 LangGraph 계보이고 v2 프로덕션 트래픽이 아니라는 사실은 그대로 남는다 | 재검토 시 다른 계보 또는 v2 프로덕션 맥락의 독립 관찰 추가가 이 Decision을 견고하게 만든다(재검토 조건 c) |
| "존재 Accept"의 오독 | "구현 착수 가능"으로 읽힐 수 있다 | 조건 5, `IMPLEMENTATION_RULES.md` 금지 조항이 Baseline 갱신 전까지 유효하다 |
| v1 결정 2/5/9/11이 "빈 상자"로 남을 위험 | 후속 ADR이 네 공백을 다루기 전에 Public Contract로 나아가면 근거 없는 계약이 된다 | 다음 ADR 문구가 "네 공백 해소 전 Public Contract 승격 불가"를 명시(조건 5) |
| v1↔v2 Architecture 불일치(G2) | E1의 강도가 v2에 대해 부분 할인된다 | Reversibility 검증(조건 4)이 v2 통합 테스트로 재현되어야 이 근거가 완성된다(Q6, Next Step 4) |
| Rule B 우회 비판 | "범위를 좁혀 형식 미충족을 우회했다"는 비판이 가능하다 | 범위 좁힘은 RFC-0019 §7·§8이 수행했고, 이 ADC는 그 좁힌 범위 + 조건 이월에 대해서만 판단했다. §6 전체에는 Rule B를 그대로 적용해 미충족으로 남긴다(Q2, Decision Rationale) |

**재검토 조건**: 이 Decision 이후 다음 중 하나가 확인되면 재검토 대상이
된다 — (a) 이 Accept가 실제 Production 맥락에서 부적절했다는 반증 관찰,
(b) A-IN 경계로는 실제 필요를 충족하지 못한다는 관찰(예: A-OUT 항목 중
하나가 실제로 이 책임에 필요해지는 사례), (c) LangGraph와 다른 계보 또는
v2 프로덕션 맥락의 조건부 분기·Loop 실행 관찰이 추가되어 독립 관찰 3건에
도달 — 이 경우 Conditional 성격을 완화하는 방향의 재판단이 가능하다.
재검토는 기존 Governance 절차(RFC → ADC → ADR → Baseline Update)를 따른다 —
이 문서를 직접 고쳐 뒤집는 것이 아니다.

---

## Next Step

**ADR Required** — 이 Decision은 Boundary를 이동시킨다(Open → Accept, 좁은
범위). 따라서 Baseline Update가 필요하다.

1. ADR을 작성해 `BASELINE.md`를 갱신한다 — §16에 새 절(예: §16.7 Scoped
   Workflow Graph Execution)을 추가해 A-IN의 존재를 등재하되, A-OUT·조건
   이월(v1 결정 2/5/9/11)·Reversibility 검증 요구는 계속 Open/조건으로
   명시한다.
2. 같은 ADR 또는 별도 절차로 `hqs/development/IMPLEMENTATION_RULES.md`에
   이 좁은 범위(A-IN, Reversibility 검증 완료)에 한해 금지 조항을 Scoped
   해제하는 방향을 반영한다 — Scheduler/우선순위/Workflow orchestration/Event
   Bus/§6 넓은 Runtime 구현은 계속 금지(`ADC-0013` Q4·`ADC-0016` §Next Step
   2와 동일 패턴).
3. `docs/decisions/adc/ADC.md`의 ADC-02 항목은 ADR 승인 이후에만 이 Decision을
   반영해 갱신을 검토한다 — 이 ADC 자신은 그 문서를 수정하지 않는다.
4. Reversibility 검증(조건 4)을 v2 맥락의 통합 테스트로 재현하는 것을 후속
   ADR/구현 지침의 선행 요구사항으로 명시한다(v1
   `test_workflow_adapter_reversibility.py`가 선례).
5. v1 `ADR-0007` 결정 2/5/9/11의 v2 재설계는 후속 ADR 또는 별도 RFC로 순서를
   정해 다룬다 — 완료 전 Public Contract 승격·구현 착수 불가.
6. 명칭, 구현체 선택(LangGraph 포함), 구현 전략은 각각 별도 ADC로 분리해
   판단한다(Execution Host 존재→명명→구현 전략 3단계 선례).

이 ADC 자체는 위 판단을 내리지 않는다. Architecture Governance 절차(RFC →
ADC → ADR → Baseline Update)를 통해 별도로 진행한다.

---

## Governance Chain 검증

| 문서 | 관계 | 정합성 |
|---|---|---|
| RFC-0019 | 이 ADC가 판단하는 Boundary Question의 출처 | RFC의 Evidence(E1·E2)와 §4~§7 재해석을 인용하되, §8 Boundary Question에 대해 RFC가 후속 ADC로 위임한 판단을 이 ADC가 완료함(RFC-0019 §Next Step 1~4 중 1·2·3에 답, 4는 Accept로 판단했으므로 해당 없음) |
| RFC-0013→ADC-0013→ADR-0003 (Execution Host) | §16.3 경계 | 변경 없음(Q5) |
| RFC-0014→ADC-0014→ADR-0004 (명칭) | 명명 절차 선례 | 변경 없음 — 이 ADC도 명칭을 확정하지 않고 별도 ADC로 위임(Q8) |
| RFC-0015→ADC-0015→ADR-0005 (구현 전략) | 구현 전략 분리 선례 | 변경 없음 — 이 ADC도 구현 전략을 확정하지 않음(Q8) |
| RFC-0016→ADC-0016→ADR-0006 (Multi-Task) | §16.4 경계, "이미 고정된 Task" 전제 | 변경 없음(Q5) — 이 책임은 §16.4가 제외한 조건부·반복 영역을 다룸 |
| RFC-0017→ADC-0017→ADR-0007 (Result Store) | §16.5 경계 | 변경 없음(Q5) — Checkpointer와 저장 게이트는 계층이 다름 |
| `docs/decisions/adc/ADC.md` ADC-02 | Runtime 개념의 존폐, Open·NOW | 변경 없음(Q8) — 이 ADC는 §6 넓은 정의의 좁은 조각만 판단 |
| `docs/architecture/core/ADC-0008` | 넓은 "유지 대 대체" Not Accepted | 변경 없음(Q8) — 서로 다른 범위의 별개 질문 |
| `docs/architecture/core/ADC-0018` | Multi-HQ 자연어 요청 분해, Defer | 변경 없음(Q4) — 이 Accept는 단일 HQ 안의 Workflow 그래프 실행만 다룸 |
| `BASELINE.md` §6 Concept Model | Runtime 정의 | 변경 없음 — 인용만 |
| `hqs/investment/checkpoint.py` | §16.5 저장 전 검증 | 변경 없음(Q5) — 대체 제안 없음 |
| `hqs/development/IMPLEMENTATION_RULES.md` | Workflow Parser/Scheduler/orchestration 구현 금지 | 변경 없음(Q7) — 이 ADC로 해제되지 않음 |

---

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **좁은 범위에서 그렇다**: Scoped
  Workflow Graph Execution 책임의 "존재"만 Accept했다. 실제 Baseline 반영은
  ADR을 거쳐야 한다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오** — Concept의
  명칭·위치·Interface는 확정하지 않았다(Q8).
- Contract Change — **없음** — 공개 Interface를 정의하지 않았고, §14.1을
  확장하지 않았다(Q7 G3).
- Baseline 문서(`BASELINE.md`, `docs/decisions/adc/ADC.md`)를 변경했는가 —
  **아니오** — 이 ADC 자신은 인용만 했다. 변경은 ADR의 몫이다.
- §16.3~16.5의 범위를 넓혔는가 — **아니오**(Q5, §Decision 조건 3).
- `ADC-08`(넓은 범위 Not Accepted)·`ADC-02`(Open)를 갱신·전복했는가 —
  **아니오**(Q8, §Decision Rationale).
- ADR이 필요한가 — **예**(§Next Step).

---

## Self Review

- [x] 판단 대상을 특정 구현체(LangGraph)가 아니라 §16.3~16.5 너머의 Scoped
      Workflow Graph Execution Boundary로 유지했다(목적, Q8).
- [x] Rule B 미충족(Evidence 2건·동일 계보)을 명시하고, 이 대상에서
      선례보다 무겁게 작용함을 인정한 뒤, 극도의 범위 제한 + 조건부 이월 +
      Reversibility 필수화로 Accept가 성립하는 구조를 설계했다(Q2).
- [x] A-IN을 State/Node/Conditional Edge/Loop + 값 기반 Checkpoint/Resume
      다섯으로 한정했다(Q3, §Decision 조건 1).
- [x] A-OUT으로 Routing/Registry, Policy, Discovery, Domain Lifecycle,
      Event Bus, Result Store 게이트, Multi-HQ decomposition을 명시 제외했다
      (Q4, §Decision 조건 2).
- [x] LangGraph 채택, 명칭, Public Port, 구현 전략을 확정하지 않았다(Q8,
      §Decision 조건 6).
- [x] Reversibility를 필수 불변조건으로 포함하고, v1
      `test_workflow_adapter_reversibility.py`를 근거로 후속 v2 검증
      요구사항으로 정의했다(Q6, §Decision 조건 4, §Next Step 4).
- [x] v1 `ADR-0007` 결정 2/5/9/11의 v2 공백을 후속 Architecture/ADR 조건으로
      이월하고, Public Contract 승격·구현 착수를 허용하지 않았다(Q7,
      §Decision 조건 5).
- [x] `docs/decisions/adc/ADC.md` ADC-02와 `docs/architecture/core/ADC-0008`을
      갱신·전복하지 않았다(Q8, §Decision Rationale).
- [x] `BASELINE.md`·`ADC.md`·`IMPLEMENTATION_RULES.md`·ADR·CLAUDE.md·Production
      Code·RFC-0019 어느 것도 수정하지 않았다 — 이 ADC 파일 하나만 신규
      작성했다.
- [x] Evidence만 사용했는가 — **Pass**. RFC-0019와 그것이 인용한 v1
      `ADR-0007`, 이번 세션 PoC 기록, `BASELINE.md`, `ADC.md`, 기존 RFC/ADC
      체인만 인용했다. 새 실험은 수행하지 않았다.
- [x] ADR 필요를 §Next Step에 명시했다(Boundary 이동 — Open → Accept Scoped).
