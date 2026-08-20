# Development HQ Responsibility

## In Scope

- Workflow의 내용 정의
- Agent의 역할 및 구성 결정
- Capability 내용 작성 및 Registry 등록
- 도메인 규칙의 내용 정의
- 내부 조직 구조(Division/Team 관례) 사용 여부 결정
- Development HQ 산출물(Artifact) 내용 관리

## Out of Scope

### Kernel과의 경계

- Task 생성·배분 메커니즘
- Agent 간 메시지 배달
- Engine 호출 (Engine Port/Adapter)
- Capability 색인·탐색 (Registry 내부 구현)
- Policy 판정 메커니즘 (PDP/PEP)
- 물리 자원 및 실행 예산 배분

### Architecture와의 경계

- Jarvis OS Concept Model 정의
- Jarvis OS System Boundary 정의
- Architecture Baseline 변경

Development HQ 설계·구현 과정에서 Architecture 문제가 발견되면, 직접 수정하지 않고 RFC → ADC → ADR 절차를 통해서만 제안한다.

### Infrastructure와의 경계

- Memory/Artifact 저장소의 물리적 구현
- Communication 프로토콜의 실제 구현
- Registry의 저장소 구현

### Implementation과의 경계

- 실제 코드 실행 환경
- CI/CD 파이프라인의 기술적 구현
- 특정 프로그래밍 언어·프레임워크 선택
