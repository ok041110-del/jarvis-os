# Jarvis OS — Reference Architecture v1
> 기술 스택 없이, 순수하게 조직/계층 구조만 정의한 문서. 기술 매핑은 문서 마지막 섹션에서 별도로 다룸.

---

## 0. 설계 원칙

이 문서 전체에서 지키는 규칙 3가지:

1. **각 계층은 자기 바로 아래 계층만 직접 지휘한다.** (Jarvis OS가 Agent에게 직접 명령하지 않음 — 사장이 말단 직원에게 직접 업무 지시를 안 하듯이)
2. **위로 올라갈수록 오래 살고(lifecycle이 길고), 아래로 내려갈수록 짧게 산다.** (본부는 몇 년을 가고, 실제 작업 지시는 그때그때 생겼다 사라짐)
3. **모든 계층은 "요청을 받는 통로"와 "이벤트를 흘려보내는 통로"를 둘 다 가진다.** 이유는 4장에서 설명.

---

## 1. 계층 정의

### 1-1. Layer 1 — Jarvis OS

> 비유: 회사 전체를 대표하는 **비서실 겸 대표이사실**. 회사 자체가 아니라, 회사가 돌아가게 만드는 "운영체제".

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① 사용자 요청을 어느 HQ로 보낼지 판단(라우팅) ② 여러 HQ가 동시에 필요한 요청을 조율(cross-HQ orchestration) ③ 전사 정책·권한 관리 (누가 무엇에 접근 가능한지) ④ HQ의 생성/등록/해제 관리 ⑤ 시스템 전역 상태 모니터링 |
| **Entity (관리 객체)** | `UserSession`, `Request`, `HQRegistry`, `GlobalPolicy`, `SystemEventLog` |
| **상위 통신** | User ↔ Jarvis OS: 사용자 인터페이스(앱/웹)를 통한 요청·응답. 유일하게 "사람"과 직접 대화하는 계층 |
| **하위 통신** | Jarvis OS → HQ: `Task Dispatch` (무엇을, 어떤 우선순위로, 어떤 제약 안에서 하라) HQ → Jarvis OS: `Result` + `StatusEvent` |
| **Lifecycle** | **상시 실행(always-on).** 서버처럼 절대 꺼지지 않음. 개별 요청은 트랜잭션처럼 생성·종료됨 |
| **확장 방식** | 새 HQ를 레지스트리에 등록하는 것만으로 확장 (코드 재배포 최소화가 목표) |

---

### 1-2. Layer 2 — HQ

> 비유: **본부장이 이끄는 사업부.** "우리는 투자를 다룬다", "우리는 개발을 다룬다" 처럼 정체성이 뚜렷한 단위.

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① 자기 전문 영역의 목표·전략 수립 ② Division 간 리소스/우선순위 배분 ③ 도메인 지식/정책 보유 ④ 다른 HQ와의 협업이 필요하면 Jarvis OS에 협업 요청 (HQ끼리 직접 명령하지 않음 — 대표이사를 거쳐야 함) |
| **Entity** | `DivisionRegistry`, `HQGoal`, `HQPolicy`, `DomainKnowledgeBase`, `HQBudget`(토큰/시간 예산) |
| **상위 통신** | Jarvis OS로부터 Task 수신, Result/Event 보고 |
| **하위 통신** | HQ → Division: `Objective Delegation` (이 목표를 이 안에서 달성하라) Division → HQ: `ProgressReport`, `Result` |
| **Lifecycle** | **반영구적(persistent).** 회사 조직처럼 한번 만들어지면 계속 존재. 안 쓰일 때는 활성 프로세스 없이 정의(config)로만 존재하다가 요청이 오면 깨어남(cold start 가능) |
| **확장 방식** | ① 기존 HQ 안에 Division 추가 ② Vision.md 원칙대로 완전히 새로운 HQ 자체를 자유롭게 추가 |

---

### 1-3. Layer 3 — Division

> 비유: 본부 안의 **팀들을 묶은 실(室)**. 예: 투자 HQ 안의 "주식 리서치 Division", "포트폴리오 관리 Division".

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① HQ가 준 목표를 Team 단위 작업으로 쪼갬 ② 여러 Team의 산출물을 하나로 합침 ③ Division 내부 우선순위 조정 |
| **Entity** | `TeamRegistry`, `DivisionTaskQueue`, `DivisionPolicy` |
| **상위 통신** | HQ로부터 Objective 수신, ProgressReport/Result 보고 |
| **하위 통신** | Division → Team: `Task Assignment` Team → Division: `TaskResult` |
| **Lifecycle** | HQ보다 **유동적(semi-dynamic)**. 필요에 따라 동적으로 생성되거나 통폐합 가능 (HQ는 잘 안 없어지지만 Division은 프로젝트 성격에 따라 생겼다 없어질 수 있음) |
| **확장 방식** | 새 Team 추가. Division 자체도 HQ 정책 안에서 자유롭게 신설 가능 |

---

### 1-4. Layer 4 — Team

> 비유: **실제로 손발을 맞춰 일하는 소규모 팀.** "이번 주 보고서 작성 팀" 처럼 하나의 구체적 Task를 위해 모임.

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① 여러 Agent를 실제로 오케스트레이션(누가 먼저, 누가 검증하는지) ② Task 완수까지 책임 ③ Agent 간 산출물 취합·검증 |
| **Entity** | `AgentPool`, `Task`, `WorkingMemory`(이 Task 한정 단기 기억), `ExecutionState` |
| **상위 통신** | Division으로부터 Task 수신, TaskResult 보고 |
| **하위 통신** | Team → Agent: `Instruction`(구체적 지시 + 필요한 Tool 접근 권한) Agent → Team: `AgentOutput` |
| **Lifecycle** | **Ephemeral(일시적).** Task 하나를 위해 생성되고, Task가 끝나면 소멸. 이게 상위 3개 계층과 가장 다른 점 — Team은 "조직"이 아니라 "그때그때 소집되는 작업반"에 가까움 |
| **확장 방식** | 동시에 여러 Team 인스턴스를 병렬 생성(동시 다중 요청 처리), 필요한 Agent 조합을 자유롭게 구성 |

---

### 1-5. Layer 5 — Agent

> 비유: **실제로 일하는 직원 한 명.** 정확히 한 가지 역할("리서처", "작성자", "검증자")만 가짐.

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① 단일 역할 수행(추론 1회 또는 짧은 루프) ② 필요하면 MCP를 통해 외부 도구 호출 ③ 자기 작업 결과만 책임 (다른 Agent 조율은 하지 않음 — 그건 Team의 역할) |
| **Entity** | `RoleDefinition`(프롬프트/시스템 지시), `ToolBinding`, `AgentMemory`(개인화된 장기 기억, Layer 6 메모리 서비스 참조), `ExecutionLog` |
| **상위 통신** | Team으로부터 Instruction 수신, AgentOutput 반환 |
| **하위 통신** | Agent → MCP/External Services: `ToolCall` MCP → Agent: `ToolResult` |
| **Lifecycle** | **가장 짧음.** 기본은 단일 invocation(호출 1번) 단위로 stateless. 사용자 개인화가 필요한 경우에만 별도 메모리 서비스에 상태를 영속화 |
| **확장 방식** | 새 Role 정의 추가, 모델 교체, 동일 역할의 여러 인스턴스 병렬 실행 |

---

### 1-6. Layer 6 — MCP / External Services

> 비유: 직원이 손에 쥐는 **전화기, 이메일, 회사 데이터베이스 열쇠**. 이 계층 자체는 "생각"하지 않고 "연결"만 함.

| 항목 | 정의 |
|---|---|
| **Responsibility** | ① 외부 시스템(API, DB, SaaS)과의 표준화된 인터페이스 제공 ② 인증/속도 제한 관리 ③ Agent 요청을 실제 외부 동작으로 변환 |
| **Entity** | `ToolSchema`, `Credential`, `RateLimitState`, `ConnectorRegistry` |
| **상위 통신** | Agent로부터 ToolCall 수신 → ToolResult 반환 (Layer 5와만 통신, 그 위 계층은 이 계층의 존재를 몰라도 됨) |
| **하위 통신 (외부)** | 실제 외부 API/서비스와 통신 |
| **Lifecycle** | **인프라형(independent).** Jarvis OS의 요청 흐름과 무관하게 독립적으로 상시 존재. 개별 Agent나 Task의 생사와 관계없이 계속 떠 있음 |
| **확장 방식** | 새 MCP 서버를 레지스트리에 등록만 하면 모든 상위 계층에서 즉시 사용 가능 (Vision.md의 "검증된 오픈소스 통합" 원칙이 실제로 구현되는 지점) |

---

## 2. 계층 간 통신 요약표

| From → To | 메시지 이름 | 방향 | 성격 |
|---|---|---|---|
| User → Jarvis OS | Request | 하향 | 동기(사람이 기다림) |
| Jarvis OS → HQ | Task Dispatch | 하향 | 비동기 가능 |
| HQ → Division | Objective Delegation | 하향 | 비동기 |
| Division → Team | Task Assignment | 하향 | 비동기 |
| Team → Agent | Instruction | 하향 | 동기/비동기 혼합 |
| Agent → MCP | Tool Call | 하향 | 동기 |
| (역방향 전체) | Result / ProgressReport | 상향 | 각 단계 완료 시 |

**규칙**: 메시지는 항상 인접 계층으로만 이동한다. Jarvis OS가 Team이나 Agent에 직접 개입해야 하는 상황(예: 긴급 중단)은 "명령"이 아니라 아래 3장의 **Event**로 처리한다.

---

## 3. 왜 "요청 흐름"과 "이벤트 흐름"을 분리하는가

Vision.md는 "사용자 명령 없이 백그라운드에서 분석·모니터링·자동화"를 요구합니다. 그런데 지금까지 정의한 통신은 전부 **위에서 아래로 내려가는 Task 흐름**입니다. 이것만으로는 다음이 불가능합니다:

- Personal HQ가 "새벽 3시에 알아서 이메일을 확인"하는 것 (User Request가 없음)
- Investment HQ Agent가 "주가 급락"을 감지해서 스스로 Team을 소집하는 것 (상위 계층 지시가 없음)

그래서 모든 계층에는 Task 흐름과 별개로 **Event Bus**를 둡니다.

- 어느 계층에서든 이벤트를 발행(publish)할 수 있음 (예: Agent가 "이상 징후 감지" 이벤트 발행)
- 어느 계층이든 관심 있는 이벤트를 구독(subscribe)할 수 있음 (예: HQ가 "자기 Division의 특정 이벤트"를 구독했다가 새 Task Dispatch를 스스로 생성)
- 이벤트는 계층을 건너뛸 수 있음 (Task 흐름과의 유일한 차이) — 말단 Agent가 감지한 이상 신호가 곧바로 Jarvis OS 모니터링 로그에도 찍힐 수 있어야 하기 때문

즉 Jarvis OS의 진짜 골격은 **Task 흐름(수직, 계층 준수) + Event 흐름(수평/전역, 계층 무관)** 두 겹입니다.

---

## 4. 생명주기 한눈에 보기

```
Jarvis OS   ████████████████████████████████████████  (상시)
HQ          ████████████████████████████░░░░░░░░░░░░  (반영구, sleep 가능)
Division    ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  (프로젝트 단위)
Team        ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (Task 단위, ephemeral)
Agent       ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (호출 1회)
MCP/외부     ████████████████████████████████████████  (인프라, 독립적 상시)
```

위로 갈수록 "회사 그 자체"에 가깝고, 아래로 갈수록 "오늘 할 일"에 가깝습니다. MCP만 예외적으로 상시 존재하는 이유는, 그것이 조직의 일부가 아니라 조직이 쓰는 **인프라**이기 때문입니다.

---

## 5. 기술 매핑 (아키텍처 → 오픈소스)

여기부터는 지난 블루프린트에서 조사한 후보들을 이 계층 구조에 배치합니다. 배치 기준은 "이 기술이 어느 계층의 Responsibility를 실제로 구현해주는가"입니다.

| 계층 | 기술 | 매핑 근거 |
|---|---|---|
| **Jarvis OS** | (자체 구현 — Gateway/Router) | 전역 라우팅·정책은 범용 프레임워크가 대신해주지 않는 Jarvis OS 고유 로직. LangGraph 등은 이 계층의 "도구"일 뿐, 이 계층 자체를 대체하지 않음 |
| **HQ ~ Team** | **LangGraph** | 그래프의 노드=Agent, 서브그래프=Team, supervisor 노드=Division/HQ의 위임 로직으로 그대로 대응. 즉 LangGraph 하나가 Layer 2~4의 "오케스트레이션 실행 엔진" 역할을 함. 계층 개념 자체는 Jarvis OS가 정의하고, LangGraph는 그 계층을 코드로 실행하는 런타임 |
| **Team (WorkingMemory)** | Team 내부 상태 (LangGraph의 State/Checkpoint) | Task 단위로 사라지는 단기 기억이므로 별도 영속 메모리 서비스 불필요, 그래프 실행 상태로 충분 |
| **Agent (AgentMemory, 장기)** | **Mem0 / Graphiti** | Agent 계층에 정의된 "장기 기억"은 개별 호출을 넘어서는 정보이므로, Agent가 자신의 프로세스 밖(외부 서비스)으로 위임해야 함. Mem0/Graphiti가 정확히 이 위임을 받는 자리 |
| **Agent → MCP 사이 (Tool Call)** | **MCP (프로토콜 자체)** | Layer 6과의 통신 규격 자체가 MCP. 계층도의 "Agent→MCP 화살표"가 곧 MCP 프로토콜 |
| **MCP / External Services** | **MCP 서버들 (파일시스템, GitHub, Slack 등)** | 정의 그대로, 이 계층의 실체 |
| **Jarvis OS ↔ HQ, HQ ↔ Division (비동기·장기 Task)** | **Temporal** | "정전 나도 이어서 한다"는 durable execution 요구는 상위 계층 간(오래 걸리는 크로스-HQ Task) 통신에서 발생. 짧게 끝나는 Team 내부 실행에는 과함 |
| **Division ↔ Team (일반 큐잉)** | **Celery** | Team은 ephemeral하고 비교적 짧게 실행되므로, 무거운 durable execution보다 가벼운 작업 큐가 적합. Temporal은 "오래 걸리는 소수의 흐름"에, Celery는 "짧고 빈번한 다수의 작업"에 배치 |
| **모든 계층 — Event Bus** | (별도 조사 필요: Redis Streams, Kafka, NATS 등) | 3장에서 정의한 이벤트 흐름 전용 인프라. 아직 미조사 — 다음 블루프린트 후보 |

**중요한 정정**: 이전 블루프린트에서는 LangGraph를 "오케스트레이션 코어" 전체로 표현했지만, 이번 아키텍처 설계로 보면 더 정확히는 **HQ~Team 사이의 실행 엔진**입니다. Jarvis OS 계층(전역 라우팅·정책·HQ 레지스트리)은 LangGraph가 대신해주지 않는, Jarvis OS가 직접 구현해야 하는 부분입니다. 이 구분이 이전 문서에서는 흐릿했습니다.

---

## 6. 다음으로 결정해야 할 것

1. **Event Bus 후보 조사** (Redis Streams vs Kafka vs NATS) — 3장에서 정의한 수평 이벤트 흐름의 실제 구현체
2. **HQ 간 협업이 "Jarvis OS를 반드시 거쳐야 하는지"** 재검토 — 지금은 원칙 1로 강제했지만, 두 HQ가 자주 협업한다면(예: Research HQ ↔ Investment HQ) 매번 대표이사를 거치는 게 비효율일 수 있음. "직속 채널"을 허용할지 결정 필요
3. **HQ의 "Sleep" 상태를 어떻게 구현할지** — cold start 비용과 상시 대기 비용의 트레이드오프

이 중 어느 걸 먼저 다룰지 알려주세요.
