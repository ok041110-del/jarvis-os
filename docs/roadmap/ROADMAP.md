# Jarvis OS — Roadmap
> 새로운 계획을 만드는 문서가 아니라, 지금까지의 모든 설계 문서에 흩어져 있던
> "의도적 미정" / "다음 단계" / "남은 질문"을 한곳에 모은 문서입니다.
> 항목마다 어느 문서에서 나왔는지 출처를 남깁니다.

---

## 진행 중 — Phase 1~5 (Architecture Validation 중심 어댑터 교체)

PROJECT_CONTEXT.md의 "Phase 실행 로그"가 최신 상태를 반영합니다. 이 로드맵에는 순서만 기록합니다.

1. **Lifecycle** → python-statemachine (Walking Skeleton의 자체 구현 State Machine 교체) — **완료** (ADR-0003)
2. **Capability YAML Loader** (ADR-0002 해소, 모델 설계는 ADR-0004로 Accepted) — `ICapabilityProvider` Port + YAML Adapter가 `hqs/*/capabilities.yaml`을 실제로 읽어 Provisioning 단계에서 Capability Registry에 등록하도록 변경. "레지스트리 등록만으로 HQ 확장"이라는 핵심 가치를 Phase 3~5보다 먼저 코드로 증명한다.
3. **Policy** → Casbin (Walking Skeleton의 In-Memory Policy Engine 교체)
4. **Connector** → MCP 공식 filesystem/fetch 서버 (Walking Skeleton의 Mock Connector 교체)
5. **Workflow** → LangGraph Core (현재 apps/poc-runner의 순차 호출 방식 교체)

각 Phase의 Definition of Done은 PROJECT_CONTEXT.md 및 ADR-0003(Port/Adapter 설계 기준 문서) 참고.
순서 기준은 "구현 난이도"가 아니라 "Architecture를 가장 많이 검증하는 순서" — Capability YAML
Loader가 Phase 2로 앞당겨진 이유도 동일하다: Jarvis OS의 핵심 Identity Claim("HQ를 코드
수정 없이 추가할 수 있다")이 아직 실증되지 않은 상태로 두지 않기 위함이다.

---

## v1.1 후보 — HQ Communication

- **Direct Channel Policy 승인 임계치·승인권자**: 어떤 트래픽량/레이턴시 기준을 넘으면 Gateway 경유(A)에서 Direct(C)로 전환할지, 누가 승인하는지 (출처: Core Design Principles v1 §5, Architecture v1.0 Final §2)
- **여러 HQ가 겹치는 Capability를 등록할 때의 우선순위** (출처: Capability Registry v1 §8) — Direct Channel Policy 논의와 자연스럽게 연결됨

## v1.1 후보 — Lifecycle

- **Wake-up latency budget의 실제 숫자** (몇 초 안에 Cold Start가 끝나야 정상인가) (출처: Core Design Principles v1 §2-3, Architecture v1.0 Final §2)
- **Division의 Archived → Active 복귀 가능 여부**, 가능하다면 그게 Permission 문제인지 Budget 문제인지 (출처: Architecture v1.0 Final §2, §6)

## v1.1 후보 — Capability Registry

- **매칭 알고리즘 고도화**: 현재 키워드 겹침 기반(PoC 최소 구현) → 의미 기반(임베딩 등)으로 교체할지 여부와 시점 (출처: Capability Registry v1 §8, PoC Backlog and OSS Survey v1 B-4)
- **Capability version 상승 시 하위 호환 처리** 방식 (출처: Capability Registry v1 §8)

## v1.1 후보 — Kernel

- **Intent Recognition 재질문 루프의 상한 횟수**: Policy Engine v1 §5에서 이미 "Kernel 로직이 아니라 Escalation Policy 소유"로 이관 결정됨 — 실제 숫자만 미정 (출처: Request Processing Kernel v1 §4, Policy Engine v1 §5)
- **`ExecutionPlan.estimated_cost`를 사용자에게 노출하는 시점** (특히 `requires_multi_hq=true`인 고비용 요청) (출처: Request Processing Kernel v1 §4)
- **`unclassified` 비율을 새 HQ 신설 신호로 모니터링할지 여부** (출처: Request Processing Kernel v1 §4, Vision.md "향후 새로운 HQ는 자유롭게 추가 가능")

## v1.1 후보 — Policy Engine

- **Event Bus 기술 선정** (Kafka / NATS / Redis Streams 등) — 책임 정의는 Reference Architecture v1 §4에서 이미 확정, 기술만 미정 (출처: Reference Architecture v1 §4, Architecture v1.0 Final §5)

---

## 아직 손도 대지 않은 영역 (v1.0 설계 범위 밖)

"미정"과는 다른 카테고리입니다 — 필요성이 아직 드러나지 않아 설계 자체를 시작하지 않은 영역입니다.

- **Memory Layer의 아키텍처적 위치**: Agent가 장기 기억을 어디에 위임하는지 인터페이스 자체가 없음
- **인증/사용자 신원 모델**: User가 누구인지, 세션을 어떻게 유지하는지
- **멀티테넌시/리소스 격리**: 사용자 A의 HQ 실행이 사용자 B에게 영향을 주지 않는 구조
- **Client(Layer 0) 아키텍처**: Tauri 등은 Blueprint 단계의 기술 후보였을 뿐 구조 설계는 없음

(출처: Architecture v1.0 Final §6)

---

## 장기 비전 (미검증 — 채택 시 ADR + docs/research 필요)

- Investment HQ가 참고할 만한 오픈소스로 "TradingAgents"류 프로젝트가 거론됨 (Vision.md) — 아직 GitHub 원본 검증 전. 실제 채택 논의 시 `docs/research/`에 원본 조사 근거를 먼저 남기고 ADR로 확정한다 (이번 프로젝트에서 LangGraph/Casbin/OPA에 적용한 것과 동일한 절차).
- Personal HQ, Finance HQ, Research HQ 등 추가 HQ (Vision.md) — Capability Registry 덕분에 Kernel 코드 변경 없이 추가 가능하다는 것이 설계 목표(§ Capability Registry v1 §6 확장 시나리오로 검증됨).

---

## 이 로드맵을 갱신하는 규칙

새 항목은 반드시 "출처 문서"를 남깁니다. 출처 없는 로드맵 항목은 추가하지 않습니다 —
이 문서는 새로운 계획을 세우는 곳이 아니라, 이미 결정 과정에서 언급된 것을 잃어버리지
않기 위한 목록이기 때문입니다.
