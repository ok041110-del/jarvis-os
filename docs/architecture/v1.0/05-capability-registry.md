# Jarvis OS — Capability Registry v1
> Architecture v1.0의 확장 논의. Policy Engine v1 다음, Direct Channel Policy 이전에 삽입.

---

## 0. 방향에 동의하며, 범위를 하나 조정합니다

"Kernel이 HQ 이름이 아니라 Capability로 HQ를 찾는다"는 방향에 전적으로 동의합니다. 이건 사실 Reference Architecture v1에서 이미 선언해둔 원칙 — *"새 HQ를 레지스트리에 등록하는 것만으로 확장"* — 을 실제로 가능하게 만드는 **구체적 메커니즘**입니다. 이름 기반 탐색이었다면 Kernel 코드 어딘가에 `if domain == "investment"` 같은 분기가 생길 수밖에 없고, 그건 새 HQ가 생길 때마다 Kernel을 고쳐야 한다는 뜻이라 Vision.md의 확장성 원칙과 정면으로 어긋납니다.

다만 요청하신 범위 — "HQ, Division, Team이 각각 Capability를 등록" — 중 **Team 부분은 그대로 채택하지 않고 조정을 제안**합니다. 이유는 3장에서 설명합니다.

---

## 1. Capability의 정의

Capability는 "이 조직 단위가 무엇을 할 수 있는가"를 **Kernel이나 상위 계층이 코드 수정 없이 읽고 판단할 수 있는 구조화된 선언**입니다.

```
Capability {
  capability_id          # 고유 식별자
  domain                 # 능력의 범주 (예: "investment.equity_research")
  description            # 이 능력이 무엇을 하는지 (매칭 판단의 핵심 근거)
  input_profile          # 어떤 종류의 요청을 받을 수 있는지
  output_profile         # 어떤 종류의 결과를 내놓는지
  constraints {
    cost_tier             # 예상 비용 등급 (Policy Engine의 Budget Tier와 연동)
    latency_tier          # 예상 처리 시간 등급
    required_permission   # 이 능력을 쓰려면 필요한 권한 수준 (Permission Tier와 연동)
  }
  owner                  # 이 Capability를 소유한 조직 단위(HQ/Division)의 식별자
  version                # Capability 명세 자체의 버전 (하위 호환 관리용)
  status                 # active / deprecated
}
```

**설계 근거**: `constraints` 필드가 Policy Engine v1의 Tier 1(Permission)·Tier 2(Budget)와 직접 연결됩니다. Capability를 "찾는 것"과 "써도 되는지 판단하는 것"이 서로 다른 컴포넌트(Capability Registry vs Policy Engine)의 책임이라는 걸 명확히 하기 위해, Capability 선언 자체에는 제약 조건의 "선언"만 담고 "판단"은 담지 않습니다. Registry는 후보를 찾아줄 뿐이고, 그 후보를 실제로 써도 되는지는 여전히 Policy Engine이 결정합니다.

---

## 2. 계층별 등록 구조

기존 Reference Architecture v1에서 이미 각 계층이 하위 레지스트리를 관리한다고 선언했습니다 (`HQRegistry`는 Jarvis OS 소유, `DivisionRegistry`는 HQ 소유, `TeamRegistry`는 Division 소유). 이번 설계는 그 레지스트리들을 **이름 목록에서 Capability 기반 카탈로그로 구체화**하는 작업입니다. 새 컴포넌트를 추가하는 게 아니라, 이미 선언된 것의 내부 구조를 정의하는 것입니다.

| 소유 계층 | 레지스트리 | 등록 주체 | 조회 주체 | 조회 시점 |
|---|---|---|---|---|
| Jarvis OS | `HQRegistry` (Capability 기반) | 각 HQ (Provisioning 완료 시) | Kernel | Task Classification, HQ Selection |
| HQ | `DivisionRegistry` (Capability 기반) | 각 Division | 소속 HQ | Division Selection |
| Division | Agent Capability Catalog *(3장에서 설명)* | 각 Agent Role 정의 | 소속 Division | Team Formation |

---

## 3. Team은 Capability를 등록하지 않습니다 — 조정 제안

**반론**: Team은 Ephemeral합니다 (Core Design Principles v1 확정 사항 — Forming부터 Terminated까지 Task 하나의 수명만 가지며, Idle 상태 자체를 의도적으로 두지 않았습니다). "등록"이라는 행위는 본질적으로 **등록 시점에 그 대상이 이미 존재하고, 나중에 발견되기를 기다리는 것**을 전제합니다. Team은 발견되기를 기다리는 대상이 아니라 **필요할 때 그 자리에서 조립되는** 대상입니다. Team이 Capability를 등록한다는 건, "아직 존재하지 않는 것이 자기 능력을 미리 선언한다"는 모순이 됩니다.

**대안**: Team이 조립되기 위해 필요한 재료 — 개별 **Agent Role의 Capability** — 를 Division이 카탈로그로 들고 있고, Division이 Team Formation(Request Processing Kernel v1, Stage 7) 시점에 이 카탈로그에서 필요한 조합을 골라 즉석에서 Team을 구성합니다.

```
Agent Capability Catalog (Division 소유) {
  agent_role_id
  role_capability          # 이 Role이 수행할 수 있는 작업 유형
  required_tools[]         # 이 Role이 필요로 하는 MCP Connector 목록
  ...
}
```

이렇게 하면:
- Team 자체는 여전히 순수하게 "생성-소멸"만 하는 임시 작업반이라는 철학이 깨지지 않습니다
- "Capability로 탐색한다"는 원칙은 한 단계 아래(Agent Role 수준)에서 동일하게 적용됩니다 — Division이 Team을 조립할 때도 여전히 이름이 아니라 능력으로 필요한 Agent Role을 찾습니다

**정리하면**: 요청하신 "HQ/Division/Team 각각의 Capability 등록"은 정확히는 **"HQ, Division, Agent Role" 3단계의 Capability 등록**으로 조정하는 것을 제안합니다. Team은 그 결과물(조립된 산출물)이지, 등록 주체가 아닙니다.

---

## 4. Kernel의 활용 방식

Request Processing Kernel v1의 기존 단계에 Capability Registry 조회를 끼워 넣습니다. **새 Stage를 추가하지 않습니다** — 기존 Stage 3, 4, 5가 이미 하던 판단의 "근거"가 하드코딩된 도메인 이름에서 Capability Registry 조회 결과로 바뀔 뿐입니다.

| Kernel Stage | 기존 정의 | Capability Registry 도입 후 |
|---|---|---|
| Stage 3 Task Classification | Intent를 도메인 후보로 분류 | Intent에서 추출한 요구사항 프로파일을 `HQRegistry`의 Capability `description`/`input_profile`과 매칭해 `domain_candidates`를 산출. 하드코딩된 분류 규칙이 아니라 **매칭 결과**가 산출물이 됨 |
| Stage 4 Task Router | 실행 전략(단일/병렬/순차) 수립 | 매칭된 각 Capability의 `constraints.cost_tier`/`latency_tier`를 참고해 `ExecutionPlan.estimated_cost` 산정 근거로 사용 |
| Stage 5 HQ Selection | 최종 HQ 확정, State 확인 | 매칭 점수 순으로 후보를 정렬한 뒤, **1순위 후보의 HQ Lifecycle State가 Disabled면 배제하고 2순위로 자동 이동** — 기존 Fallback 규칙(Request Processing Kernel v1)이 이제 "차선책"이 아니라 "매칭 순위상 다음 후보"로 구체화됨 |

**Permission Tier와의 연결**: Capability의 `constraints.required_permission`은 Stage 5에서 Policy Engine의 Permission Policy(Tier 1)를 호출할 때 그대로 입력값이 됩니다. Capability Registry는 "이 요청을 처리할 수 있는 후보가 누구인지"만 답하고, "이 사용자가 그 후보를 쓸 자격이 있는지"는 여전히 Policy Engine이 답합니다 — 두 컴포넌트의 책임이 섞이지 않습니다.

---

## 5. Lifecycle과의 연동

Capability의 가시성은 소유 조직의 State Machine(Core Design Principles v1)을 그대로 따릅니다. 별도 규칙을 새로 만들지 않고 기존 상태기계에 편승합니다.

| HQ State | Capability Registry에서 보이는가 |
|---|---|
| Provisioning | 아니오 — 헬스체크 통과 전에는 탐색 대상이 아님 |
| Running / Idle | 예 — 정상 후보 |
| Sleeping | **예, 단 선택 시 Wake-up 트리거 포함** — Sleeping이라고 후보에서 빠지면 "쓰지도 않는데 항상 깨어있는 HQ"만 발견되는 구조가 되어버려 Sleeping을 둔 의미가 없어짐 |
| Disabled | 아니오 — Stage 5에서 이미 확정한 규칙과 동일 |
| Updating / Error | 조건부 — 진행 중인 Task는 유지하되 신규 매칭 후보에서는 제외 (Updating/Error 중 새 일을 더 받으면 안 됨) |
| Decommissioned | 레지스트리에서 완전히 제거 |

---

## 6. 확장 시나리오로 검증

새 HQ(예: "Legal HQ")를 추가하는 경우를 그려보면 이 설계의 의도가 맞는지 확인할 수 있습니다.

1. Legal HQ가 `Provisioning` 상태로 생성되며 자신의 Capability를 `HQRegistry`에 선언 (`domain: "legal.contract_review"`, `constraints.required_permission: "standard"` 등)
2. 헬스체크 통과 → `Idle`로 전이, 이제 Registry에서 탐색 가능
3. **Kernel 코드는 단 한 줄도 바뀌지 않습니다.** 사용자가 "이 계약서 검토해줘"라고 말하면 Stage 3에서 이 새 Capability가 자연스럽게 매칭 후보에 오릅니다

이게 바로 "이름이 아니라 능력으로 찾는다"가 실제로 의미하는 바입니다 — **새 HQ 추가가 Registry에 데이터 하나 넣는 일이지, Kernel을 재배포하는 일이 아니게 됩니다.**

---

## 7. 기존 문서와의 관계 정리

| 항목 | 상태 |
|---|---|
| `HQRegistry`, `DivisionRegistry` (Reference Architecture v1) | 재사용 — 내부 스키마만 Capability 기반으로 구체화 |
| Agent Capability Catalog | **신규 추가** — Team Formation을 위해 필요했으나 이전 문서에 없던 개념. Division 소유로 배치 |
| Request Processing Kernel v1 Stage 3/4/5 | 재사용 — 로직 자체는 안 바뀌고, 판단 근거만 하드코딩에서 Registry 조회로 교체 |
| Policy Engine v1 Permission/Budget Tier | 재사용 — Capability의 `constraints`가 그 입력값이 됨 |
| HQ Lifecycle State Machine | 재사용 — Capability 가시성 규칙이 그대로 편승 |

이번 설계에서 새로 생긴 컴포넌트는 **Agent Capability Catalog 단 하나**입니다. 나머지는 전부 기존에 이미 선언했던 엔티티의 내부를 구체화한 것입니다 — 이게 지금까지 이 프로젝트가 지켜온 "새 박스를 함부로 늘리지 않는다"는 태도와 일치합니다.

---

## 8. 남은 질문

- 매칭 점수를 어떻게 계산할지(정확 일치 vs 의미 기반 매칭)는 **기술 스택 논의**이므로 여기서 다루지 않았습니다. 지금은 "매칭 결과가 순위 있는 후보 목록을 반환한다"는 인터페이스만 확정한 상태입니다
- Capability의 `version`이 올라갈 때(예: HQ가 기능을 확장) 기존에 매칭되던 요청들과의 하위 호환을 어떻게 다룰지는 아직 미정
- 여러 HQ가 **겹치는 Capability**를 등록하는 경우(예: Research HQ와 Investment HQ가 둘 다 "시장 동향 분석"을 선언) 우선순위를 어떻게 정할지 — 이건 Direct Channel Policy와도 맞닿아 있어 다음 논의에서 자연스럽게 다뤄질 수 있습니다

다음으로 Direct Channel Policy로 넘어가면 될까요, 아니면 위 남은 질문 중 먼저 정리하고 싶은 게 있으신가요?
