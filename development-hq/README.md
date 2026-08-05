# Development HQ

## 소개

Development HQ는 Jarvis OS 위에서 동작하는 첫 번째 HQ다.

## 목적

Development HQ의 목적은 소프트웨어를 만드는 것이 아니라, Jarvis OS Architecture Baseline v1.0을 현실의 도메인에서 검증하는 것이다.

## Jarvis OS와의 관계

Development HQ는 Jarvis OS Architecture Baseline v1.0을 변경하지 않는다. Development HQ는 Baseline이 정의한 Concept Model과 System Boundary를 그대로 준수하며 동작하는 하나의 HQ 인스턴스다.

Architecture를 Development HQ에 맞추지 않는다. Development HQ를 통해 Architecture를 검증한다.

## Reference HQ인 이유

Development HQ는 Research HQ, Personal HQ, Investment HQ, Automation HQ, Communication HQ 등 향후 모든 HQ가 참고할 첫 번째 구현 사례다.

Reference로서 재사용되는 것은 Development HQ의 도메인 내용(소프트웨어 개발 프로세스)이 아니라, Mission·Responsibility·Boundary·Structure를 정의하는 **패턴**이다.

## 문서 구성

| 문서 | 내용 |
|---|---|
| `MISSION.md` | 존재 이유와 검증 대상 |
| `RESPONSIBILITY.md` | 책임 범위와 Kernel/Architecture/Infrastructure/Implementation과의 경계 |
| `BOUNDARY.md` | Jarvis OS → Development HQ → Agent → Connector 계층에서의 책임 분계 |
| `STRUCTURE.md` | 내부 구조, Capability 예시, Workflow 관계 |
| `BASELINE.md` | Development HQ Baseline v1.0 선언 |
| `MVP.md` | 승인된 첫 번째 MVP 정의 |
| `IMPLEMENTATION_RULES.md` | Claude Code가 구현 시 지켜야 하는 규칙 |
| `HANDOVER.md` | Claude Code 인수인계 문서 |
