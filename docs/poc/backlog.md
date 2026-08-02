# Jarvis OS — PoC Backlog & Open Source Survey v1
> Architecture v1.0 (Final) 동결 이후 첫 실행 문서. Backlog 확정 → 그 Backlog에만 근거한 오픈소스 조사.

---

## Part A. PoC Backlog

### Must — 이번 PoC의 성공 조건

| # | 항목 | Architecture v1.0 근거 |
|---|---|---|
| 1 | Kernel Routing (Intent Recognition~HQ Selection, 최소 규칙 기반) | Request Processing Kernel v1 |
| 2 | Capability Registry 기반 HQ 매칭 (Kernel이 이름이 아닌 Capability로 HQ 선택) | Capability Registry v1 |
| 3 | Development HQ (Division 1, Team 1, Agent 1) | Reference Architecture v1 |
| 4 | Investment HQ (Division 1, Team 1, Agent 1) | Reference Architecture v1 |
| 5 | HQ 간 Routing 정확성 (요청이 올바른 HQ로 가는지, Gateway 경유 구조 A) | Core Design Principles v1 §1 |
| 6 | Policy Engine — Permission Tier(Tier 1)만 | Policy Engine v1 |
| 7 | HQ Lifecycle: `Idle → Running → Idle` 기본 사이클 + `Sleeping → Wake-up` 1회 이상 | Core Design Principles v1 §2 |
| 8 | Team Ephemeral 확인: `Forming → Active → Completing → Terminated` 소멸까지 관찰 | Core Design Principles v1 §3 |
| 9 | MCP Connector 1~2개 (Agent→MCP 통신 경로 확인) | Reference Architecture v1 |
| 10 | No Silent Failure 시나리오 1건 이상 (예: Disabled HQ 요청, 존재하지 않는 Capability 요청) | Request Processing Kernel v1 |
| 11 | 계층 경계 준수 확인 (Kernel이 Division/Team 선택에 관여하지 않는지) | Reference Architecture v1 §0 원칙 |

### Should — 가능하면 검증

| # | 항목 | 비고 |
|---|---|---|
| 1 | 최소 Event Flow 시연 (Task Flow와 분리되어 있다는 것만 증명 — 실서비스 규모 아님) | Sleeping→Wake-up(Must #7) 트리거로 자연스럽게 겸사겸사 검증 가능 |
| 2 | 구조화된 로그(Audit 원칙 최소 확인 — "판단이 실시간 기록되는가") | Full Audit 인프라 아님, 콘솔/파일 로그 수준 |
| 3 | 상태 전이를 눈으로 보는 간단한 CLI/대시보드 | Lifecycle 관찰용 보조 도구일 뿐, 제품 UI 아님 |

### Won't — 이번 PoC에서는 하지 않음

| # | 항목 | 왜 안 하는지 |
|---|---|---|
| 1 | Voice 인터페이스 | Client 계층 자체가 v1.0 설계 범위 밖 |
| 2 | Memory 최적화 (Mem0/Graphiti 등 장기 기억) | Agent 계층이 위임하는 인터페이스만 있을 뿐, 이번 PoC는 위임 자체를 안 함 |
| 3 | Learning / 자기 개선 | 아키텍처 검증과 무관 |
| 4 | Token Optimization | Budget Tier 자체가 Won't (Architecture v1.0 Final §2-2) |
| 5 | Trading 성능, 코드 생성 품질 등 기능 품질 | 이번 PoC의 목적이 아님 — 명시적으로 배제 |
| 6 | Direct Channel Policy 실제 구현 | 의도적 미정 항목, v1.1 대상 |
| 7 | Event Bus 실서비스 구현(Kafka/NATS 등) | Should #1 수준의 최소 시연으로 충분, 실제 기술 선정은 v1.1 이후 |
| 8 | Budget/Priority Tier 실제 적용 | Architecture v1.0 Final §2-2에서 이미 제외 확정 |
| 9 | 인증/멀티테넌시 | v1.0 설계 범위 밖으로 명시됨 (Architecture v1.0 §6) |

---

## Part B. Backlog 기준 오픈소스 조사

**조사 원칙**: 가장 유명하거나 스타가 많은 프로젝트가 아니라, **Must 11개 항목을 가장 빠르고 안정적으로 증명할 수 있는 프로젝트**를 고릅니다. 이번 PoC 규모(HQ 2개, 각 Division/Team/Agent 1개)에는 대형 프레임워크의 고급 기능 대부분이 오히려 불필요한 복잡도입니다.

### B-1. Orchestration Engine — Kernel~Organization Layer 실행

Must #1, #3, #4, #5, #11 관련.

| 후보 | 이번 PoC 관점 평가 |
|---|---|
| **LangGraph** | <cite index="9-1">그래프의 각 노드가 자기 상태를 유지하는 방향 그래프 구조로, 조건부 로직과 다중 팀 조정, 계층적 제어를 지원하며 supervisor 노드로 확장 가능한 오케스트레이션을 만들 수 있습니다</cite>. HQ 2개를 supervisor 아래 두 개의 branch로 두는 최소 그래프로 정확히 표현 가능 — Must #5(HQ 간 Routing)를 가장 직접적으로 검증할 수 있는 구조 |
| CrewAI | <cite index="15-1">역할·목표·배경으로 에이전트를 정의하고 20줄 안에 멀티에이전트를 구성할 수 있을 만큼 빠르지만</cite>, 내부 상태 접근이 추상화에 가려져 있어 Must #11(계층 경계 준수를 코드 레벨에서 확인)을 검증하기 어려움 |
| Google ADK | <cite index="15-1">루트 에이전트가 하위 에이전트에 위임하는 계층적 트리 구조</cite>라 개념은 잘 맞지만, 특정 클라우드 생태계 종속성이 이번처럼 순수 아키텍처 검증에는 불필요한 제약 |

**추천: LangGraph.** 이유는 "멋져서"가 아니라, 우리가 이미 정의한 State Machine·Kernel 5단계·Capability 매칭 로직을 **그래프의 노드/엣지/조건부 분기로 거의 그대로 옮겨 적을 수 있기 때문**입니다. 즉 프레임워크가 우리 설계를 강요해서 바꾸게 만들지 않습니다. 이게 "빠르고 안정적으로 구현"의 실제 의미입니다.

### B-2. Lifecycle State Machine — HQ/Team 상태 전이

Must #7, #8 관련.

| 후보 | 평가 |
|---|---|
| **python-statemachine** | <cite index="53-1">계층적 상태와 병렬 리전, 히스토리 상태를 지원하는 선언적 API의 프로덕션 준비된 라이브러리로, 동기·비동기 코드베이스 모두에서 동작</cite>합니다. <cite index="52-1">Guard와 Validator로 조건부 전이를 구현할 수 있고, 커맨드라인이나 런타임에서 상태 다이어그램을 바로 생성</cite>할 수 있습니다 |
| pytransitions/transitions | <cite index="57-1">가볍고 객체지향적인 유한 상태 기계 구현체</cite>로 검증된 선택지지만, Guard 기반 조건부 전이(Disabled는 자동 wake 불가 같은 규칙)의 표현력이 python-statemachine보다 약함 |
| 직접 구현 | 문서에서 소개된 <cite index="60-1">전이 맵을 외부에서 주입받는 방식의 간단한 StateMachine 클래스</cite>처럼 손으로 짜는 것도 가능하지만, 다이어그램 자동 생성 기능을 포기해야 함 |

**추천: python-statemachine.** 결정적 이유는 **Guard 기능**입니다 — "Sleeping은 누구나 깨울 수 있지만 Disabled는 사람만 깨울 수 있다"는 Core Design Principles v1의 핵심 규칙이 정확히 Guard로 표현됩니다. 그리고 다이어그램 자동 생성 기능은 이번 문서들에서 그린 상태기계 다이어그램과 실제 구현이 일치하는지 육안으로 바로 대조할 수 있게 해줘서, PoC 검증(Must #7)에 그대로 쓸모가 있습니다.

### B-3. Policy Engine — Permission Tier

Must #6 관련. 여기서는 속도와 미래 확장성 사이에 실제 트레이드오프가 있어 구분해서 추천합니다.

| 후보 | 평가 |
|---|---|
| **Casbin** | <cite index="44-1">ACL, RBAC, ABAC, ReBAC 등 여러 접근 제어 모델을 Go, Java, Node.js, Python 등 여러 언어로 지원하는 오픈소스 인가 라이브러리</cite>이며, <cite index="46-1">정책 모델을 PERM(Policy, Effect, Request, Matcher) 파일로 정의해 별도 서버 없이 애플리케이션에 임베드</cite>할 수 있습니다 |
| **Open Policy Agent (OPA)** | <cite index="43-1">권한 부여 로직을 애플리케이션 코드에서 완전히 분리해 중앙에서 정책을 정의하고 런타임에 평가</cite>하는 범용 정책 엔진으로, <cite index="47-1">인프라와 애플리케이션 전체에 걸쳐 하나의 엔진을 쓰고 싶을 때의 표준</cite>입니다. 다만 <cite index="46-1">Rego라는 별도 정책 언어를 배워야 하고</cite>, <cite index="50-1">데몬으로 별도 실행되는 컴포넌트</cite>라 이번 최소 PoC엔 인프라가 하나 더 늘어남 |
| Cerbos | <cite index="47-1">가장 단순한 무상태(stateless) 정책 결정 서비스</cite>로 OPA보다 가볍지만, 여전히 별도 서비스로 띄워야 함 |

**추천: 이번 PoC는 Casbin, v1.1부터 OPA 전환을 전제로 설계.** Permission Tier 하나만 검증하는 지금 단계에서 별도 데몬을 띄우는 건 과합니다. 다만 Budget/Priority Tier가 추가되고 여러 PEP(HQ, Division, Team 등)가 분산된 환경에서 하나의 중앙 PDP를 참조해야 하는 v1.1 시점에는, 애플리케이션 코드와 정책이 완전히 분리되는 OPA 모델(정확히 우리가 정의한 PDP/PEP 개념 그 자체입니다)이 맞습니다. 지금은 Casbin으로 "허용/거부" 로직만 빠르게 증명하고, Policy Engine의 인터페이스(입력: 주체+행동+대상, 출력: allow/deny)를 OPA로 교체해도 위 계층 코드가 안 바뀌게 설계해두는 것을 권장합니다.

### B-4. Capability Registry — 매칭 로직

Must #2 관련. **이 항목은 조사 결과 추천할 기성 오픈소스가 없습니다.** Capability Registry v1에서 이미 이 컴포넌트를 "새 박스를 늘리지 않고 기존 엔티티를 구체화한 것"으로 설계했듯, 실제로도 이건 프레임워크가 아니라 **얇은 커스텀 계층**입니다 — Capability 스키마를 담는 저장소(PoC 규모라면 SQLite/JSON 파일로 충분)와, Intent와 Capability description을 비교하는 매칭 함수 하나가 전부입니다. 여기에 무거운 기술을 끌어오면 오히려 "빠르고 안정적"이라는 기준에 어긋납니다.

참고할 만한 유사 패턴: MCP의 도구 스키마 기반 발견 메커니즘 자체가 "능력을 이름이 아니라 구조화된 설명으로 찾는다"는 우리 원칙과 같은 발상입니다. 다만 그건 Agent→MCP(도구 레벨)에서 이미 검증된 패턴이고, 우리가 필요한 건 Kernel→HQ(조직 레벨)이므로 직접 재사용은 안 되지만, "Description 필드를 어떻게 구조화하면 매칭이 잘 되는지"는 MCP 도구 스키마 설계를 참고할 가치가 있습니다.

### B-5. MCP Connector

Must #9 관련. <cite index="30-1">2026년 5월 기준 공식 MCP 레지스트리에만 9,652개의 최신 서버 기록이 등록</cite>되어 있어 후보는 차고 넘칩니다. 이번 PoC는 **기능 품질이 목적이 아니므로**(Won't #5) 가장 검증되고 유지보수가 활발한 레퍼런스 서버 2개만 고릅니다.

**추천**: Anthropic 공식 레퍼런스 서버 저장소의 **filesystem 서버**(로컬 파일 접근, Development HQ의 Agent가 도구를 호출하는 가장 단순한 경로 증명용)와 **fetch 서버**(웹 요청, Investment HQ의 Agent가 외부 데이터에 접근하는 경로 증명용) 두 개면 Must #9 검증에 충분합니다. 둘 다 공식 SDK로 유지보수되어 PoC 단계에서 도구 자체의 안정성 문제로 시간을 뺏길 위험이 가장 낮습니다.

---

## Part C. PoC 기술 스택 요약

| 계층 | 선정 | 이번 PoC 한정 이유 |
|---|---|---|
| Orchestration (Kernel~Organization) | LangGraph | 우리 설계(State Machine, 조건부 라우팅)를 그대로 그래프로 옮길 수 있음 |
| Lifecycle State Machine | python-statemachine | Guard 기반 조건부 전이가 Sleeping/Disabled 구분 규칙과 정확히 일치, 다이어그램 자동 생성으로 설계-구현 대조 가능 |
| Policy Engine (Permission Tier) | Casbin (v1.1에서 OPA 전환 전제) | 별도 인프라 없이 최소 허용/거부 로직만 빠르게 증명 |
| Capability Registry | 커스텀 (SQLite/JSON + 매칭 함수) | 기성 프레임워크가 필요 없는 얇은 계층 |
| MCP Connector | filesystem, fetch (공식 레퍼런스 서버) | 가장 안정적으로 검증된 최소 구성 |

**의도적으로 제외한 것**: 이전 Blueprint v1에서 조사했던 Mem0/Graphiti(메모리), Temporal/Celery(내구성 실행), Tauri(클라이언트)는 이번 Must 목록 어디에도 해당하지 않으므로 이번 PoC 스택에서 전부 제외합니다. 이건 조사가 부족해서가 아니라, Backlog가 그것들을 요구하지 않기 때문입니다.

---

## Part D. 다음 단계

이 조사 결과로 실제 PoC 구현에 들어갈지, 아니면 특정 후보(특히 Policy Engine의 Casbin↔OPA 트레이드오프처럼 의견이 갈릴 수 있는 지점)를 더 검토하고 싶은지 알려주세요.
