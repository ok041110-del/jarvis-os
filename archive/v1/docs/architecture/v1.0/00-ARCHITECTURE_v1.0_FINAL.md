# Jarvis OS — Architecture v1.0 (Final Frozen Baseline)
> Architecture v1.0(초안) + Capability Registry v1을 통합한 최종 동결판.
> 이 시점 이후 순수 설계 문서는 작성하지 않는다. 변경은 ADR + v1.1 형태로만 반영한다.

---

## 1. v1.0 초안 대비 변경 사항

**추가 확정: Capability Registry**

- Kernel은 이름이 아니라 Capability로 HQ를 탐색한다 — Reference Architecture v1의 "레지스트리 등록만으로 확장" 원칙을 실제로 구현하는 메커니즘
- 등록 계층은 **HQ, Division, Agent Role** 3단계로 확정 (요청하신 "Team 등록"은 Team의 Ephemeral 특성과 모순되어 조정 — Team은 Division이 Agent Capability Catalog에서 즉석 조립하는 결과물로 재정의)
- `HQRegistry`/`DivisionRegistry`(기존 엔티티)의 내부 스키마를 Capability 기반으로 구체화, 새 컴포넌트는 Agent Capability Catalog(Division 소유) 하나만 추가
- Capability 매칭은 Kernel Stage 3~5(Task Classification, Task Router, HQ Selection)의 기존 판단 근거를 하드코딩에서 Registry 조회로 대체할 뿐, 새 Stage를 만들지 않음
- Capability 가시성은 HQ Lifecycle State Machine에 그대로 편승 (Disabled 배제, Sleeping은 노출하되 Wake-up 트리거 포함)

이 외 나머지 항목(6-Layer 구조, HQ Communication A→C 전환, Lifecycle State Machine, Request Processing Kernel, Policy Engine PDP/PEP·3-Tier 위계)은 이전 Architecture v1.0 초안과 동일하게 유지한다.

**여전히 의도적 미정 (동일하게 유지)**: Direct Channel 승인 임계치, Wake-up Budget 수치, Archived Division 복귀 규칙, Event Bus 기술, Capability 매칭 알고리즘 구현.

---

## 2. PoC 범위 (개정)

**변경 사유**: Development HQ 단일 구성으로는 이 아키텍처의 핵심 가치 — HQ 간 라우팅, Policy 적용, Lifecycle 전이 — 가 애초에 검증되지 않는다. HQ가 하나면 Task Classification의 매칭도, HQ Selection의 후보 비교도 의미가 없다. 최소 2개 HQ가 있어야 "Kernel이 실제로 선택을 한다"는 것 자체가 테스트된다.

### 2-1. 구성

| 항목 | 범위 |
|---|---|
| HQ | Development HQ, Investment HQ (2개) |
| Division | 각 HQ당 1개 |
| Team | 각 Division당 1개 (Ephemeral 특성 확인용, Task 종료 시 소멸까지 관찰) |
| Agent | 각 Team당 1개 |
| MCP Connector | 검증된 것 1~2개만 연결 (기능 자체보다 Agent→MCP 통신 경로 확인 목적) |

### 2-2. PoC로 검증할 것 (기능이 아니라 아키텍처)

1. **Capability 매칭**: 두 HQ가 서로 다른 Capability를 등록했을 때, Kernel Stage 3~5가 사용자 요청을 올바른 HQ로 정확히 라우팅하는가
2. **HQ Lifecycle 전이**: `Idle → Running → Idle` 기본 사이클이 실제로 동작하는가. 가능하면 `Sleeping` 진입과 Wake-up 트리거 시나리오도 1건 포함
3. **Policy Engine 최소 적용**: Tier 1(Permission)만 우선 구현해, 권한 없는 요청이 실제로 Stage 5 이전에 차단되는지 확인
4. **No Silent Failure**: 의도적으로 실패 케이스(예: 존재하지 않는 Capability 요청, Disabled HQ로의 요청)를 1건 이상 포함해, 실패가 사용자에게 투명하게 전달되는지 확인
5. **계층 경계 준수**: Kernel이 Division/Team 선택에 관여하지 않고, HQ가 자기 Division 선택을 스스로 하는지 (설계상 원칙이 실제 구현에서도 지켜지는지)

**PoC에서 검증하지 않는 것 (v1.1 이후로 명시적으로 미룸)**: Budget/Priority Tier, Direct Channel, Event Bus, 실제 업무 품질(코드 리뷰가 잘 되는지, 투자 분석이 정확한지 등 — 이건 기능 검증이지 아키텍처 검증이 아님)

---

## 3. ADR(Architecture Decision Record) 프로세스

PoC 진행 중 아키텍처 변경이 필요하다고 판단되면, 아래 형식으로 ADR을 먼저 작성한 뒤에만 Architecture v1.1 문서에 반영한다. **구현 중 발견한 문제가 자동으로 아키텍처 변경이 되지 않는다** — 반드시 이 절차를 거친다.

```
ADR-XXX: [변경 제목]

날짜:
상태: Proposed / Accepted / Rejected

배경 (Context)
- PoC 중 어떤 문제가 관찰되었는가
- 왜 이것이 "구현 디테일"이 아니라 "아키텍처 원칙 위반"인가

결정 (Decision)
- Architecture v1.0의 어느 조항을 어떻게 바꾸는가

근거 (Rationale)
- 왜 이 대안이 다른 대안보다 나은가

기각된 대안 (Rejected Alternatives)
- 무엇을 고려했다가 왜 버렸는가

영향 범위 (Impact)
- 어느 계층/문서가 함께 수정되어야 하는가
```

ADR이 Accepted되면, 해당 ADR 번호를 근거로 명시하며 v1.1 문서를 갱신한다. ADR 없이 이루어지는 설계 변경은 없다.

---

## 4. 다음 단계

Architecture v1.0을 여기서 동결합니다. 이후 순서는 Vision.md의 개발 원칙(Research → Evaluate → Integrate → Customize → Build)을 따라:

1. 위 PoC 구성(Development HQ + Investment HQ, 각 최소 구성)에 필요한 오픈소스 후보를 GitHub에서 조사
2. 이전 Blueprint v1에서 조사했던 LangGraph/Mem0/MCP 등을 이번 최소 구성 관점에서 재검토 (전체 스택이 아니라 "2-HQ 라우팅 PoC 하나"에 필요한 최소 조합으로 좁혀서)

바로 오픈소스 조사를 시작할까요, 아니면 PoC 구성에 대해 먼저 더 확인하고 싶은 부분이 있으신가요?
