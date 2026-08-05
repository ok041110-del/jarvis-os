# Jarvis OS — Policy Engine v1
> Request Processing Kernel v1의 후속. 요청하신 대로, 제안하신 계층 구조를 그대로 채택하지 않고 먼저 반론부터 정리합니다.

---

## 0. 결론부터 — 제안하신 선형 구조에 반대합니다

제안하신 구조는 이렇습니다.

```
User → Kernel → Policy Engine → Scheduler → Organization Layer → HQ → Division → Team → Agent
```

"Kernel은 무엇인지 판단, Policy Engine은 허용 여부 판단, Organization Layer는 누가 수행할지 결정"이라는 3분할 원칙 자체는 정확하고, 그대로 채택합니다. 문제는 **이걸 하나의 순차 파이프라인으로 그렸다는 점**입니다.

**반론의 핵심**: Policy Engine을 Kernel과 Scheduler 사이의 "한 번 거치는 검문소"로 두면, Organization Layer 내부(HQ→Division, Division→Team, Team→Agent, Agent→MCP)에서 일어나는 모든 후속 결정에는 정책 검증이 적용되지 않습니다. 그런데 실제로 정책이 필요한 순간은 최초 라우팅 때뿐만이 아닙니다.

구체적 예:
- Team이 특정 Agent를 호출하려는 순간에도 Permission 검사가 필요합니다 (이 Team이 이 Agent의 Tool 접근 권한을 가졌는가?)
- Agent가 MCP를 호출하는 순간에도 Permission/Security 검사가 필요합니다 (이 도구가 이 데이터에 접근해도 되는가?)
- Division이 Team을 여러 개 동시에 소집하려는 순간에도 Token Budget 검사가 필요합니다

Policy Engine을 최상단 한 지점에만 두면, 이 모든 하위 지점들이 **각자 알아서 정책을 구현**해야 하는데 — 이건 지난 문서(HQ Communication Policy, 구조 B)에서 이미 "각 애플리케이션이 접근 제어를 개별 구현하면 정책이 어긋난다"고 명시적으로 배제했던 실패 패턴을 여기서 그대로 반복하는 것입니다.

**대안**: Policy Engine은 파이프라인의 한 "단계(stage)"가 아니라, **모든 계층이 각자의 결정 순간에 호출하는 공유 서비스**로 설계합니다. 실제 OS에서 커널의 각 시스템 콜이 권한 서브시스템(예: Linux의 LSM/capability 체크)을 그때그때 호출하지, "권한 검사"라는 별도의 거대한 파이프라인 단계를 한 번만 거치고 끝내지 않는 것과 같은 이유입니다.

이 구조를 **PDP/PEP 모델**이라고 부르겠습니다.
- **PDP (Policy Decision Point)**: Policy Engine 자신. "허용되는가?"를 판단하는 단 하나의 권위 있는 주체
- **PEP (Policy Enforcement Point)**: 실제로 판단을 요청하고 그 결과를 집행하는 지점들. Kernel, Scheduler, HQ, Division, Team, Agent, MCP Connector — **모든 계층이 각자 자기 결정 순간마다 PEP가 됨**

이렇게 하면 "정책의 내용과 판단 로직은 한 곳(Policy Engine)에만 존재"하면서도 "정책이 실제로 적용되는 지점은 시스템 전체에 분산"됩니다. 정책 일관성과 실제 적용 커버리지를 동시에 확보하는 방법은 이것뿐입니다.

---

## 1. Policy Engine의 Responsibility

Policy Engine이 PDP로서 관리하는 정책 종류를 아래처럼 재정리합니다. 제안하신 목록에 두 가지(Escalation Policy, Isolation Policy)를 추가했고, 이유는 각 항목에 적었습니다.

| Policy 종류 | 판단 내용 | 주로 호출하는 PEP |
|---|---|---|
| **Permission Policy** | 이 주체(User/HQ/Division/Team/Agent)가 이 리소스/도구/데이터에 접근해도 되는가 | 모든 계층, 특히 Agent→MCP |
| **Security Policy** | 이 요청/응답이 보안 위협 패턴에 해당하는가 (이상 징후 탐지, 자동 Disable 트리거 등) | Kernel, MCP Connector, HQ Lifecycle |
| **Direct Channel Policy** | 이 HQ 쌍이 Gateway를 거치지 않고 직접 통신해도 되는가 | HQ Selection, HQ↔HQ 통신 시점 |
| **Wake-up Policy** | Sleeping 상태의 HQ를 지금 깨워도 되는가 (빈도 제한, 승인 필요 여부) | HQ Selection, Scheduler |
| **Token/Resource Budget Policy** | 이 요청에 지금 리소스(토큰, 시간, 비용)를 배정해도 되는가 | Scheduler, Division(Team 소집 시), Team(Agent 호출 시) |
| **Retry Policy** | 실패 시 몇 번, 어떤 간격으로 재시도할 것인가 | Team(Agent 재시도), HQ(Division 재시도) |
| **Priority Policy** | 여러 요청이 자원을 두고 경쟁할 때 무엇을 먼저 처리할 것인가 | Scheduler |
| **Escalation Policy** *(신규)* | 자동화로 해결이 안 될 때 몇 번의 시도 후 사람에게 넘길 것인가 | Kernel(Intent 재질문 횟수), Team(Agent 대체 실패) |
| **Isolation Policy** *(신규)* | 한 주체(HQ/Team)의 오작동·폭주가 다른 주체에 전파되지 않도록 어떻게 격리할 것인가 | Event Bus 사용 지점(이미 Reference Architecture v1 4장에서 "격리는 책임"이라 명시했으나 그 책임의 규칙 출처가 정의 안 돼 있었음 — 여기서 Policy Engine이 그 출처가 됨 |
| **Audit Policy** | 무엇을, 얼마나 상세히, 얼마나 오래 기록할 것인가 | 모든 PEP (예외 없이 전부) |

**Escalation Policy를 추가한 이유**: Request Processing Kernel v1에서 "N회 재질문 후 에스컬레이션", "N회 재시도 후 대체"처럼 **숫자를 Kernel 단계 설명에 직접 하드코딩**했습니다. Policy Engine이 생긴 지금, 이 숫자들은 Kernel의 로직이 아니라 정책이어야 합니다. 이건 5장에서 다시 다룹니다.

---

## 2. 계층 관계 — 재설계

### 2-1. 제안하신 구조에서 고친 두 가지

1. **Policy Engine을 파이프라인에서 빼고 옆에 놓습니다** (0장 근거)
2. **"Organization Layer"라는 이름을 별도의 계층처럼 나열하지 않습니다.** Organization Layer는 HQ~Agent를 묶어 부르는 **집합 명칭**이지, HQ 위에 존재하는 또 하나의 실제 계층이 아닙니다. `Scheduler → Organization Layer → HQ`처럼 쓰면 마치 Organization Layer가 HQ와 별개의 홉(hop)인 것처럼 보이는데, 이는 표기상 착시입니다.

### 2-2. Scheduler의 역할을 좁게 재정의

Scheduler를 그대로 유지하되, **Kernel의 HQ Selection과 겹치지 않도록 역할을 명확히 분리**해야 합니다.

- **Kernel (HQ Selection)**: "이 작업은 **어느 HQ**가 맡아야 하는가" — 대상 선정
- **Scheduler**: "지금 시스템 전체에 걸려 있는 작업들 중, 이 작업을 **지금 실행에 들어가게 할지, 대기시킬지**" — 동시성/자원 배분 결정

즉 Kernel은 "누가"를 정하고, Scheduler는 "언제/얼마나 동시에"를 정합니다. 실제 OS에서 이 둘이 분리되어 있는 이유와 같습니다 — 프로세스가 어떤 CPU 코어에 갈지(할당)와 지금 당장 실행될지 대기열에서 기다릴지(스케줄링)는 다른 문제입니다.

### 2-3. 재설계된 구조

```
                         User
                          │
                          ▼
                    ┌───────────┐
                    │  Kernel   │──────┐
                    │(무엇/누구 후보)│      │  매 결정 순간마다
                    └─────┬─────┘      │  Policy Engine에 조회
                          │            │
                          ▼            │
                    ┌───────────┐      │
                    │ Scheduler │──────┤
                    │(언제/동시성)│      │
                    └─────┬─────┘      │      ┌──────────────────┐
                          │            ├─────▶│   Policy Engine   │
                          ▼            │      │       (PDP)       │
              ┌─────────────────────┐  │      │                   │
              │  Organization Layer │──┤      │ Permission /       │
              │  (집합 명칭)          │  │      │ Security /         │
              │                     │  │      │ Budget / Priority / │
              │   HQ                │  │      │ Wake-up / Retry /   │
              │    ↓ (PEP)          │──┤      │ Escalation /        │
              │   Division          │  │      │ Isolation / Audit   │
              │    ↓ (PEP)          │──┤      └──────────────────┘
              │   Team              │  │
              │    ↓ (PEP)          │──┤
              │   Agent             │  │
              │    ↓ (PEP)          │──┘
              │   MCP/External      │
              └─────────────────────┘
```

**핵심**: 오른쪽의 Policy Engine은 파이프라인의 한 단계가 아니라, 왼쪽 모든 계층에서 화살표가 뻗어 나오는 **공유 서비스**입니다. Event Bus(Reference Architecture v1)와 마찬가지로 "수직 파이프라인이 아닌 수평/전역 인프라"라는 점에서 사실 Policy Engine과 Event Bus는 같은 부류의 컴포넌트입니다 — 하나는 "될까?"를 답하고, 하나는 "일어났다"를 퍼뜨립니다.

---

## 3. Policy 적용 순서 — 재설계

제안하신 순서는 다음과 같았습니다.

```
Intent Recognition → Routing → Permission → Budget → Priority → Execution → Audit
```

### 3-1. 두 가지 문제

**문제 1 — "Routing"은 Policy Engine의 일이 아닙니다.** Routing(경로 계획)은 Kernel의 Task Router(Request Processing Kernel v1, Stage 4)가 하는 일입니다. Policy Engine은 그 경로가 "허용되는가"만 검증합니다. 이 둘을 나란히 나열하면 책임이 다시 섞입니다. → `Routing`은 이 순서표에서 빠지고, Kernel의 산출물(`ExecutionPlan`)이 Policy Engine 입력으로 들어오는 것으로 정정합니다.

**문제 2 — Audit을 맨 마지막 단계로 두면 "No Silent Failure" 원칙과 충돌합니다.** Audit이 Execution 다음의 마지막 스텝이면, Execution 도중 뭔가 실패해서 파이프라인이 중간에 끊기는 경우 **감사 로그 자체가 안 남습니다.** 이는 Request Processing Kernel v1에서 확정한 침묵 실패 금지 원칙에 정면으로 위배됩니다. → Audit은 "마지막 단계"가 아니라 **모든 단계를 감싸는 상시 기록 채널**이어야 합니다. 매 판단(허용이든 거부든)이 내려지는 즉시 기록됩니다.

### 3-2. 재설계된 순서 (계층 경계 하나를 통과할 때마다 반복되는 체크포인트)

```
[어떤 계층이 다음 계층으로 무언가를 넘기려는 시점]
        │
        ▼
  1. Permission   ── 하드 게이트. 거부되면 즉시 중단 (하위 정책 평가 자체를 생략)
        │ (통과)
        ▼
  2. Security     ── 하드 게이트. 이상 패턴 감지 시 즉시 중단 + Isolation 트리거
        │ (통과)
        ▼
  3. Budget       ── 소프트 게이트. 부족하면 즉시 거부하지 않고 축소안(Fallback) 우선 시도
        │ (통과 또는 축소 승인)
        ▼
  4. Wake-up      ── 조건부 게이트. 대상이 Sleeping일 때만 평가
        │ (통과)
        ▼
  5. Priority     ── 논블로킹. 통과/거부를 정하지 않고, 실행 순서/자원 배분만 조정
        │
        ▼
     Execution 진행

  ※ Audit은 위 1~5 각 단계의 "판단 결과"를 그 즉시 기록하는 병렬 채널.
     Execution 이후에도 "결과"를 기록. 즉 Audit은 6번째 단계가 아니라
     1~5 전체와 동시에 흐름.
```

이 체크포인트는 **파이프라인 전체에서 딱 한 번** 일어나는 게 아니라, User→Kernel 진입 시, Scheduler 진입 시, HQ→Division, Division→Team, Team→Agent, Agent→MCP — **PEP가 있는 모든 지점에서 반복**됩니다. 다만 매번 9개 정책을 전부 재평가하는 건 낭비이므로, 상위 계층에서 이미 통과한 Permission/Security 판단 결과는 하위로 전파되는 컨텍스트에 캐싱되어, 하위 계층은 "자기 지점에서 새로 발생하는 결정"에 대해서만 재평가하는 것이 합리적입니다 (예: Division→Team 단계에서는 "이 Division이 이 Task를 다룰 권한"은 이미 검증됐으므로 재검사하지 않고, "이 Team이 이 특정 Agent를 쓸 권한"만 새로 검사).

---

## 4. Policy 충돌 해결

### 4-1. 정책 간 우선순위 티어

모든 정책을 동등하게 취급하면 충돌을 해결할 기준이 없습니다. 3단계 위계를 둡니다.

| Tier | 포함 정책 | 성격 | 충돌 시 동작 |
|---|---|---|---|
| **Tier 1 — 절대 게이트** | Permission, Security | 협상 불가. 둘 중 하나라도 거부하면 나머지는 평가할 필요조차 없음 | 즉시 중단, 대안 없음 |
| **Tier 2 — 자원 게이트** | Budget, Wake-up, Isolation | 거부되어도 즉시 끝내지 않고 축소/대체안(Fallback)을 먼저 시도. 대안이 없을 때만 최종 거부 | 축소 실행 또는 거부 (단, 반드시 사용자에게 고지 — 4-3 참고) |
| **Tier 3 — 최적화** | Priority, Retry | 애초에 "허용/거부"를 결정하지 않음. 이미 허용된 것들 사이의 순서·자원 배분만 조정 | 절대 상위 티어 결과를 뒤집지 못함 |
| **(티어 밖) 상시 채널** | Audit | 위 세 티어의 모든 판단을 예외 없이 기록. 그 자체로는 실행 여부에 영향 없음 | 항상 기록 |

**규칙**: 상위 티어가 하위 티어를 항상 이깁니다. Tier 3(Priority)이 아무리 "지금 당장 실행하라"고 해도 Tier 1(Permission)이 거부하면 그걸로 끝입니다. 이게 "직급이 높은 사람이 우선순위를 정할 순 있어도, 애초에 권한이 없는 일을 하게 만들 순 없다"는 조직 원리와 동일합니다.

### 4-2. 제시하신 예시로 검증

> Priority는 실행하라고 하지만, Token Budget은 막고, Permission은 허용하고, Wake-up Policy는 Sleeping HQ를 깨워야 하는 상황

평가 순서(3장 순서 그대로 적용):

1. **Permission (Tier 1)**: 허용 → 통과, 다음 단계로
2. **Security (Tier 1)**: (언급 안 됐으므로 통과 가정) → 통과
3. **Budget (Tier 2)**: 막힘 → 여기서 **즉시 거부하지 않고**, Kernel의 `ExecutionPlan` 축소 옵션을 먼저 조회 (예: 여러 HQ 병렬 실행 대신 단일 HQ로 축소하면 예산 내에 들어오는지)
   - 축소안이 예산 내에 들어오면 → 축소된 형태로 4번으로 진행
   - 축소안도 예산을 초과하면 → 여기서 최종 거부, **5번(Priority)은 평가되지 않음**
4. **Wake-up (Tier 2, 조건부)**: 3번을 통과했다는 전제하에 평가. Sleeping HQ를 깨우는 것 자체도 비용이므로, 이 비용이 3번에서 이미 통과한 예산 안에 포함되는지 재확인. 포함되면 통과
5. **Priority (Tier 3)**: 여기 와서야 처음으로 의미를 가짐. 이미 "실행 가능"이 확정된 상태에서, "지금 당장 할지 조금 대기시킬지"만 결정

**결론**: Priority의 "실행하라"는 지시는 **Budget이 막았다면 애초에 발언권이 없습니다.** Tier 3는 Tier 2를 이길 수 없습니다. 다만 Budget이 완전한 거부가 아니라 축소를 통해 실행 가능한 경로를 찾을 수도 있으므로, "Budget이 막았다"가 곧바로 "전체 실패"를 뜻하진 않습니다.

### 4-3. 축소/거부 시 고지 의무

Tier 2에서 축소나 거부가 발생하면, 이는 Request Processing Kernel v1의 **No Silent Failure 원칙**에 따라 반드시 사용자에게 전달되어야 합니다 — "Priority상 급하게 처리하려 했으나 예산 제약으로 축소된 방식으로 처리했습니다"처럼요. 정책이 사용자 몰래 결과의 품질이나 범위를 바꾸는 것 자체가 침묵 실패의 한 형태입니다.

---

## 5. 기존 문서와의 충돌 지점 (요청하신 대로 반드시 지적)

| 충돌 | 기존 문서 | 문제 | 수정 방향 |
|---|---|---|---|
| **재시도/에스컬레이션 임계값의 하드코딩** | Request Processing Kernel v1: "N회 재질문 후 에스컬레이션", "N회 재시도 후 대체"가 각 Stage 설명에 직접 명시됨 | 이 숫자들이 Kernel 로직에 박혀 있으면, 나중에 "재시도 횟수를 3회에서 5회로 바꾸자"는 결정이 **Kernel 코드 변경**이 되어버립니다. 정책은 코드가 아니라 데이터여야 합니다 | 해당 숫자들을 Retry Policy / Escalation Policy 소유로 이관. Kernel은 "실패했다"는 사실과 "재시도 여부를 Policy Engine에 물어본다"는 절차만 가짐 |
| **Wake-up 판단 주체의 이중화** | Core Design Principles v1: HQ의 State Machine 자체가 Wake-up 트리거와 latency budget을 정의 | 이번 문서에서 Wake-up Policy를 Policy Engine 소유로 새로 정의하면서, "누가 Wake-up을 최종 승인하는가"가 State Machine과 Policy Engine 양쪽에 걸쳐 있는 것처럼 보일 수 있음 | **명확히 분리합니다**: State Machine은 Wake-up이 **기계적으로 어떻게 일어나는지**(어떤 상태에서 어떤 상태로, cold start 절차)를 정의하고, Policy Engine의 Wake-up Policy는 **그 기계적 절차를 지금 실행해도 되는지**(빈도 제한, 비용 승인)를 판단합니다. State Machine = 메커니즘, Policy = 그 메커니즘을 쓸지 말지의 거버넌스 |
| **Isolation 책임의 출처 미정의** | Reference Architecture v1, 4장: Event Bus의 책임으로 "격리(Isolation)"가 언급되었으나, 그 격리 규칙이 어디서 오는지는 정의되지 않았음 | "격리되어야 한다"는 요구사항만 있고 "얼마나, 어떤 기준으로"가 없었음 | Isolation Policy를 Policy Engine의 정식 정책 종류로 추가해 이 공백을 메움 (1장에 반영 완료) |

---

## 6. 다음 단계

이 설계로 Policy Engine의 뼈대가 잡혔으니, 예정하신 대로 아래 순서로 하위 정책을 상세 설계하면 됩니다. 다만 이제는 각 하위 정책이 "몇 번째 티어에 속하는지", "어느 PEP에서 주로 호출되는지"를 먼저 확정하고 들어가는 게 이번 설계와 일관됩니다.

1. **Direct Channel Policy** (Tier 1: Security와 맞닿아 있음 — HQ 간 신뢰 경계 문제이므로)
2. **Wake-up Policy** (Tier 2 — 자원/비용 게이트)
3. **Archived Division Policy** (아직 티어 미정 — Division의 Archived→Active 복귀는 Permission 문제인지 Budget 문제인지부터 정해야 함, 이 자체가 논의거리)

어느 것부터 진행할까요?
