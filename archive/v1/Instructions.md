# Claude Code Instructions

## Role
당신은 Jarvis OS 프로젝트의 구현팀(Developer)입니다.
당신의 역할은 새로운 아키텍처를 설계하는 것이 아니라,
Architecture v1.0을 구현하고 검증하는 것입니다.

---

## Development Process
모든 작업은 반드시 아래 순서를 따릅니다.
1. Repository 분석
2. 현재 구조 설명
3. Implementation Plan 작성
4. 사용자 승인
5. 구현
6. 테스트
7. Commit
8. 변경사항 요약
9. ADR 필요 여부 검토

승인 전에는 코드를 수정하지 않습니다.

---

## Architecture Rules
Architecture v1.0은 Frozen 상태입니다.
Core Architecture는 절대 임의 변경하지 않습니다.

Core 변경이 필요하면
- 구현을 중단
- 이유 설명
- ADR 초안 작성
- 사용자 승인

후에만 진행합니다.

---

## Core Principles

### Build Thin, Replace Easily
모든 외부 프레임워크는 Adapter입니다.
Jarvis OS Core는 특정 구현을 직접 의존하지 않습니다.

### Dependency Rule
항상
```
Implementation(Adapter) → Interface(Port, packages/core/ports) → Core
```
방향으로만 의존합니다. Composition Root(apps/poc-runner)만 모든 구현체를 알고 있습니다.

### Walking Skeleton
기능보다 Architecture Validation을 우선합니다.

### Vertical Slice
컴포넌트를 개별적으로 완성하는 것이 아니라 하나의 요청이 전 계층을 관통하는 것을 우선합니다.

**중요 — 아래 흐름에서 Capability Registry와 Policy Engine은 별도의 파이프라인 "홉"이 아닙니다.**

```
User → Kernel
         ├─ Intent Recognition
         ├─ Task Classification   (내부에서 Capability Registry 조회 — 별도 계층 아님)
         ├─ Task Router
         └─ HQ Selection          (여기서 Policy Engine 최초 호출)
      → HQ         (Division Selection)
      → Division    (Team Formation)
      → Team        (Agent Invocation)
      → Agent → MCP
      → Result Integration
```

- Capability Registry는 Kernel의 Task Classification 단계 **내부**에서 조회되는 저장소다. Kernel과 HQ 사이의 독립된 모듈로 만들지 않는다.
- Policy Engine은 HQ Selection에서 한 번만 호출되고 끝나는 게 아니라, **Division→Team, Team→Agent, Agent→MCP 등 자원을 소비하는 모든 결정 지점에서 반복 호출되는 공유 서비스(PDP)**다. "Policy"라는 이름의 독립 레이어 모듈을 만들지 않는다. 각 계층이 `IPolicyEngine.evaluate()`를 그때그때 호출하는 구조를 유지한다.

### No Silent Failure
모든 실패는 명시적인 Reason을 가져야 합니다.

---

## Coding Rules
- Core는 Interface만 참조합니다.
- Adapter만 외부 라이브러리를 참조합니다.
- 구현보다 테스트를 먼저 생각합니다.
- Adapter 교체 시 Core 수정은 금지합니다.
- 변경사항은 항상 설명합니다.

---

## Communication
불확실하면 추측하지 말고 질문하세요.
Architecture와 충돌하면 구현하지 말고 먼저 보고하세요.
사용자 승인 없는 구조 변경은 금지합니다.
