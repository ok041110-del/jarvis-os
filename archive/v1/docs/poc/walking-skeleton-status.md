# Walking Skeleton — 현재 상태

## 실행 방법 (네트워크 없는 환경 포함)
```
./scripts/run_walking_skeleton.sh   # 4개 시나리오 실행, 로그로 전 계층 흐름 확인
./scripts/run_tests.sh              # Must 11개 항목과 대응되는 10개 자동 테스트
```

## 구현 완료 (실제 동작 확인됨)
- packages/core: Kernel Stage 2~5(Intent Recognition~HQ Selection), Capability Registry,
  HQ Lifecycle State Machine(Guard 포함), Organization 엔티티(HQ/Division/Team/Agent) —
  전부 외부 의존성 없는 순수 Python으로 실동작.
- Must #1,2,3,4,5,6,7,8,9,10,11 — 4개 시나리오 + 10개 unittest로 검증 완료.

## 의도적으로 Walking Skeleton 수준으로 남긴 부분
- **Policy Engine**: adapters/policy-inmemory (임시). ADR-003에 따라 다음 증분에서
  adapters/policy-casbin(이미 스켈레톤 존재)으로 교체 예정. IPolicyEngine Port만
  맞으면 Core/Kernel 코드는 무변경.
- **MCP Connector**: adapters/connector-mock (임시). ADR-004에 따라
  adapters/connector-mcp(공식 filesystem/fetch 레퍼런스 서버)로 교체 예정.
- **Orchestration**: 지금은 apps/poc-runner가 Kernel~Organization 흐름을 직접
  순차 호출한다. ADR-001에 따라 LangGraph 코어로 교체 예정이나, Walking Skeleton
  철학상 "가장 단순한 기술로 먼저 전체 배선을 검증한 뒤 교체"가 맞는 순서라
  지금 단계에서는 의도적으로 보류.
- **CapabilityRegistry.match()**: 키워드 겹침 기반의 최소 구현. 매칭 알고리즘
  고도화는 기술 스택 논의 대상이며 Must 항목이 아님.

## 실행 환경 제약 (투명하게 기록)
이 저장소는 네트워크가 차단된 샌드박스에서 스캐폴딩·구현되었기 때문에
`uv sync`로 Casbin/LangGraph/python-statemachine/MCP SDK를 실제로 설치해
테스트하지 못했다. adapters/policy-casbin, adapters/workflow-langgraph,
adapters/lifecycle-statemachine, adapters/connector-mcp는 ADR에 근거한
스텁 상태로 남아 있으며, 네트워크가 있는 실제 개발 환경에서 `uv sync` 이후
다음 증분으로 채워야 한다.
