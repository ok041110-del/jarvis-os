# Development HQ Boundary

## 계층 관계

```
Jarvis OS
↓
Development HQ
↓
Agent
↓
Connector (MCP)
```

## Development HQ가 책임지는 것

| 항목 | 설명 |
|---|---|
| Workflow 내용 | 어떤 업무를, 어떤 순서로 수행할지 정의 |
| Agent 구성 | 어떤 역할의 Agent를 둘지 결정 |
| Capability 선언 | 무엇을 할 수 있는지 Registry에 등록할 내용 작성 |
| 도메인 규칙 | 코드 리뷰 기준, 배포 승인 조건 등 내용 정의 |
| 내부 조직 구조 사용 여부 | Division/Team 관례를 쓸지 말지 결정 |

## Development HQ가 절대 책임지지 않는 것

| 항목 | 설명 |
|---|---|
| Task 실행 메커니즘 | Kernel Scheduler의 책임 |
| Agent 간 메시지 배달 | Kernel Communication의 책임 |
| Engine 호출 | Kernel Engine Port/Adapter의 책임 |
| Capability 색인·탐색 | Kernel Registry의 책임 |
| Policy 판정 | Kernel Policy Engine의 책임 |
| HQ 생명주기 상태 관리 | Kernel Registry/Governance의 책임 |
| 물리 자원·실행 예산 배분 | Kernel의 책임 |

## 원칙

Development HQ는 Jarvis OS가 제공하는 인프라를 소비하는 입장이며, 이 인프라를 대체하거나 우회하는 자체 메커니즘을 만들지 않는다.

Kernel이 아직 확정되지 않은 시점이라 하더라도, Development HQ가 이를 대신할 임시 실행 메커니즘을 자체적으로 만드는 것은 금지된다. 구체적 구현 규칙은 `IMPLEMENTATION_RULES.md` 참조.
