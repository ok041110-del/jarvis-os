# Jarvis OS — Request Processing Kernel v1
> Reference Architecture v1 + Core Design Principles v1의 후속. "User 자연어 → Organization 실행"을 잇는 Jarvis OS의 커널 계층 설계.

---

## 0. 이 계층이 왜 "Kernel"인가

지금까지 설계한 Organization Layer(HQ~Agent)는 **일단 Task Dispatch가 도착한 이후**의 구조입니다. 하지만 그 Task Dispatch 자체가 어떻게 만들어지는지는 아직 정의하지 않았습니다.

일반 OS로 비유하면, Organization Layer는 "프로세스가 실행되는 방식"이고, 지금 설계할 이 계층은 **"어떤 프로세스를 실행할지 결정하는 스케줄러"**입니다. 이 결정이 틀리면 그 아래 모든 계층(HQ, Division, Team, Agent)이 아무리 잘 설계돼 있어도 소용없습니다. 그래서 이 계층의 실패 처리와 Fallback이 다른 어떤 계층보다 중요합니다 — **여기서 실패하면 사용자는 Jarvis OS가 "이해를 못 했다"고 느낍니다.**

**중요한 구조적 사실 하나를 먼저 명시합니다**: 아래 9단계 중 1~5단계(User~HQ Selection)만 순수하게 새로 정의되는 **Jarvis OS Kernel 고유 영역**입니다. 6~9단계(Division Selection~Result Integration)는 사실 지난 두 문서에서 이미 HQ/Division/Team의 책임으로 정의해둔 것을 이 파이프라인 관점에서 다시 확인하는 것입니다. 이 경계를 명확히 해야 "Kernel이 모든 걸 다 하려는" 설계 오류를 피할 수 있습니다.

---

## 1. 단계별 설계

### Stage 1 — User

파이프라인의 시작점. 별도 처리 로직 없음. Raw request(텍스트/음성)와 세션 컨텍스트만 다음 단계로 전달합니다.

---

### Stage 2 — Intent Recognition

| 항목 | 정의 |
|---|---|
| **Responsibility** | 자연어 요청에서 "사용자가 진짜 원하는 것"을 구조화된 형태로 추출. 아직 어떤 HQ 문제인지는 판단하지 않음 — 순수하게 의도만 파악 |
| **Input** | Raw Request(텍스트) + Session Context(직전 대화 맥락) |
| **Output** | `Intent { primary_intent, entities[], ambiguity_score, confidence }` |
| **Lifecycle** | 요청 1건당 1회 실행, **stateless**. 단, 대화 맥락 파악을 위해 최근 세션 히스토리를 참조는 하되 자체 상태를 유지하진 않음 |
| **실패 처리** | `confidence`가 임계치 미만이면 "명확화 필요" 상태로 마킹하고 다음 단계로 넘기지 않음 |
| **Fallback** | 의도가 모호하면 **Jarvis OS가 직접** 사용자에게 되묻습니다 (HQ까지 내려가지 않음 — 이게 중요합니다. 이해 못 한 요청을 조직 전체에 흘려보내지 않는 것 자체가 이 계층의 존재 이유입니다). 재질문이 N회 반복돼도 해소 안 되면 사람 상담 채널로 에스컬레이션 |

---

### Stage 3 — Task Classification

| 항목 | 정의 |
|---|---|
| **Responsibility** | Intent를 "실행 가능한 작업 유형"으로 분류. 어떤 전문 영역(들)에 속하는지, 단일 HQ로 충분한지 여러 HQ 협업이 필요한지, 긴급도·예상 복잡도 판단 |
| **Input** | `Intent` |
| **Output** | `TaskClassification { domain_candidates[], requires_multi_hq: bool, urgency, complexity_tier }` |
| **Lifecycle** | 요청 1건당 1회, stateless |
| **실패 처리** | `domain_candidates`가 하나도 안 잡히면(=어떤 HQ와도 매칭 안 됨) `unclassified` 상태 |
| **Fallback** | `unclassified` Task는 즉시 실패시키지 않고, 조직 내 **범용 처리 경로**(General/Default HQ 또는 인간 에스컬레이션 큐)로 보냄 — "매칭되는 HQ가 없다"는 것 자체가 Jarvis OS의 정상적인 안전망 동작이어야 함 |

---

### Stage 4 — Task Router

| 항목 | 정의 |
|---|---|
| **Responsibility** | Classification 결과를 바탕으로 **실행 전략**을 세움 — 단일 HQ 직행 / 여러 HQ 병렬 / 여러 HQ 순차 협업 중 무엇인지 결정. HQ 간 조율이 필요하면 그 흐름이 Gateway를 거칠지(A) Direct 채널을 쓸지(C, 후속 논의 예정)가 여기서 결정됨 |
| **Input** | `TaskClassification` |
| **Output** | `ExecutionPlan { target_hqs[], execution_mode(단일/병렬/순차), estimated_cost }` |
| **Lifecycle** | 요청 1건당 1회, stateless (단, 복잡한 멀티턴 계획은 짧게 유지되는 planning context를 가질 수 있음) |
| **실패 처리** | 계획 자체가 성립하지 않는 경우(모순된 요구, 순환 의존 등) 오류 |
| **Fallback** | 계획 실패 시 가장 단순한 형태(단일 HQ, 단일 스텝)로 축소 재시도. 그마저 안 되면 사용자에게 "요청을 더 구체적으로 알려달라"고 되돌림 |

---

### Stage 5 — HQ Selection

| 항목 | 정의 |
|---|---|
| **Responsibility** | `ExecutionPlan`의 후보 HQ 중 실제로 Task Dispatch를 보낼 대상을 최종 확정. 이때 **HQ의 현재 State(Core Design Principles v1의 State Machine)를 확인** — `Disabled`면 후보에서 배제, `Sleeping`이면 Wake-up 트리거를 Dispatch에 포함 |
| **Input** | `ExecutionPlan` |
| **Output** | **`Task Dispatch`** — Reference Architecture v1에서 정의한 "Jarvis OS → HQ" 통신 메시지 그 자체 |
| **Lifecycle** | 요청 1건. **이 단계를 끝으로 Kernel의 역할이 종료**되고 제어권이 Organization Layer(HQ)로 넘어감 — Kernel과 Organization Layer의 실제 경계선이 여기 |
| **실패 처리** | 선택된 HQ가 `Disabled` 상태면 Dispatch 자체가 즉시 거부됨 (Disabled는 자동 wake 불가 — Core Design Principles v1 2-2 규칙과 일치) |
| **Fallback** | 1차 후보 HQ가 불가 상태면 `ExecutionPlan`에 정의된 차선책 HQ로 대체. 대체 후보도 없으면 사용자에게 "현재 처리 불가"를 명시적으로 응답 + 사람 에스컬레이션 (침묵 실패 금지) |

---

### Stage 6 — Division Selection *(HQ의 기존 책임 재확인)*

| 항목 | 정의 |
|---|---|
| **Responsibility** | *(새로 정의하지 않음)* Reference Architecture v1에서 이미 HQ의 책임으로 정의됨 — "Division 간 리소스/우선순위 배분". Task Dispatch를 받은 HQ가 내부적으로 어느 Division에 위임할지 결정 |
| **Input** | `Task Dispatch` |
| **Output** | `Objective Delegation` (HQ→Division) |
| **Lifecycle** | HQ가 `Running` 상태로 전이된 이후, HQ의 활성 기간 내에서 실행 |
| **실패 처리** | 적합한 Division이 없으면 HQ가 정책에 따라 임시 Division을 구성하거나, Kernel(Jarvis OS)에 "처리 불가"를 반환 |
| **Fallback** | HQ 내 기본(General/Default) Division으로 라우팅 |

---

### Stage 7 — Team Formation *(Division의 기존 책임 재확인)*

| 항목 | 정의 |
|---|---|
| **Responsibility** | *(새로 정의하지 않음)* Division이 Task를 실제로 수행할 Team을 소집. 여기서 **Team의 생명주기가 실제로 시작**됨 (`Forming` 상태 진입) |
| **Input** | `Objective Delegation` |
| **Output** | `Task Assignment` (Division→Team) + 새 Team 인스턴스 생성 |
| **Lifecycle** | Team은 Ephemeral — Formation 성공 시점부터 Task 종료까지만 존재 |
| **실패 처리** | 필요한 Agent 조합(role)을 구성할 수 없으면 Formation 자체가 실패 |
| **Fallback** | 최소 구성(단일 범용 Agent)으로 축소 시도. 그마저 실패하면 Division이 상위(HQ)로 실패를 보고 |

---

### Stage 8 — Agent Invocation *(Team의 기존 책임 재확인)*

| 항목 | 정의 |
|---|---|
| **Responsibility** | *(새로 정의하지 않음)* Team이 개별 Agent에게 Instruction을 전달하고 실행 결과를 받음 |
| **Input** | `Instruction` |
| **Output** | `AgentOutput` |
| **Lifecycle** | 가장 짧음 — 호출 1회 단위 |
| **실패 처리** | 모델 오류, Tool 실패, timeout 등 — 재시도 정책 필요 |
| **Fallback** | N회 재시도 실패 시 대체 모델/Agent 인스턴스로 전환. 그마저 실패하면 Team이 **부분 실패**로 상위에 보고 (전체 실패로 뭉뚱그리지 않음) |

---

### Stage 9 — Result Integration

| 항목 | 정의 |
|---|---|
| **Responsibility** | **이 단계는 단일 계층의 책임이 아니라, 상향 경로 전체에 걸친 책임입니다.** Team이 Agent 결과를 취합 → Division이 Team 결과를 취합 → HQ가 Division 결과를 취합 → (멀티 HQ인 경우) Kernel이 여러 HQ의 결과를 최종 취합해 User Response로 변환 |
| **Input** | 각 단계 하위 계층의 `Result` 묶음 |
| **Output** | 각 단계에서 상위로 전달되는 통합 Result → 최종적으로 `User Response` |
| **Lifecycle** | 하향 흐름(Task Dispatch)이 종료된 시점에 대응해 소멸 — Task 완료와 함께 사라짐 |
| **실패 처리** | 일부 Agent/Team/HQ가 실패한 **부분 실패** 상황을 어떻게 다룰지가 핵심 — "나머지 결과만으로 응답할지" "전체를 재시도할지"는 `complexity_tier`와 `urgency`(Stage 3 산출물)에 따라 정책적으로 결정 |
| **Fallback** | 부분 성공 시 **"일부만 완료됐다"는 사실을 사용자에게 투명하게 전달**합니다. 실패한 부분을 숨기고 완료된 것만 보여주는 건 침묵 실패(silent failure)이며, 이는 Jarvis OS 전체에 대한 신뢰를 깎는 가장 나쁜 형태의 실패입니다 |

---

## 2. 전체 파이프라인과 계층 경계

```
User
  │
  ▼
┌─────────────────────────────────────────────┐
│  JARVIS OS KERNEL  (신규 정의 영역)            │
│                                               │
│  Intent Recognition                          │
│        │  (모호하면 → 사용자에게 즉시 반문)      │
│        ▼                                     │
│  Task Classification                         │
│        │  (매칭 HQ 없으면 → General 경로)       │
│        ▼                                     │
│  Task Router                                 │
│        │  (계획 불가 → 단순화 재시도)            │
│        ▼                                     │
│  HQ Selection                                │
│        │  (HQ Disabled → 차선책 HQ / 에스컬레이션)│
└────────┼──────────────────────────────────────┘
         │  ══ Task Dispatch ══  (Kernel ↔ Organization 경계)
         ▼
┌─────────────────────────────────────────────┐
│  ORGANIZATION LAYER  (기존 정의 재확인)          │
│                                               │
│  Division Selection (HQ 책임)                 │
│        ▼                                     │
│  Team Formation (Division 책임)                │
│        ▼                                     │
│  Agent Invocation (Team 책임)                  │
└─────────────────────────────────────────────┘
         │
         ▼
   Result Integration  (Team→Division→HQ→Kernel, 상향 전 구간)
         │
         ▼
      User Response
```

**이 그림에서 확인해야 할 것**: Kernel 4단계 각각에 실패 시 **즉시 사용자에게 돌아갈 수 있는 탈출구**가 있습니다. 이게 의도적인 설계입니다 — Organization Layer까지 내려간 뒤에 실패하면 비용(토큰, 시간)이 이미 소모된 뒤이므로, 최대한 Kernel 단계에서 걸러내는 것이 Core Design Principles v1의 "Token 비용" 원칙과 일치합니다.

---

## 3. 이 설계에서 확정된 것

1. **Kernel의 범위는 Stage 1~5까지입니다.** Division Selection 이하는 이미 정의된 Organization Layer 책임을 재확인한 것이지, Kernel이 새로 관여하는 영역이 아닙니다. Kernel이 하위 계층의 결정까지 대신하려 들면 "인접 계층만 통신한다"는 원칙(Reference Architecture v1, 2장)이 깨집니다.
2. **모호함은 최대한 빨리, 가장 위 계층에서 해소합니다.** Intent Recognition 단계의 실패가 조직 전체로 전파되지 않고 Jarvis OS가 직접 사용자와 재대화하는 구조는, 실제 회사에서 비서실이 애매한 지시를 본부까지 내려보내지 않고 먼저 되묻는 것과 같은 원리입니다.
3. **침묵 실패를 금지합니다.** Result Integration 단계에서 부분 실패를 사용자에게 숨기지 않는다는 원칙을 명시했습니다. 이건 이후 Direct Channel Policy나 Audit 설계에도 계속 적용될 원칙입니다.

---

## 4. 다음 논의로 넘어가기 전 남은 질문

- Intent Recognition의 재질문 루프가 **몇 번까지** 허용되는지 (무한 반문은 나쁜 UX)
- `ExecutionPlan`의 `estimated_cost`가 실제로 어느 시점에 사용자에게 노출되는지 (특히 `requires_multi_hq: true`인 고비용 요청)
- Task Classification의 `unclassified` 비율이 실제로는 "General HQ 하나로 계속 흡수"되는 게 맞는지, 아니면 이 비율 자체를 모니터링해서 **새 HQ 신설의 신호**로 쓸지 (Vision.md의 "향후 새로운 HQ는 자유롭게 추가 가능"과 연결되는 지점)

이제 예정하신 대로 Direct Channel Policy, Wake-up Budget, Archived Division 순서로 이어가면 될까요?
