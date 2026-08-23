# Stage: Implementation

## 목적

명세를 코드로 구현한다.

## Responsibility

- Coding
- Refactoring
- Git
- Documentation

## Reference

- Claude Code
- OpenHands

## 참고 구현 예시 (기존 코드, 이동하지 않음)

이 Stage의 Coding Responsibility는 MVP-0004(Hello SDLC)에서
`backend_agent_code_generation()`으로 실제 구현되었다(`design`을 입력받아
코드를 생성). 아래는 참조 링크일 뿐이며, 이 문서 작성으로 코드가
이동되거나 수정되지 않았다.

- `hqs/development/mvp/agents.py` — `backend_agent_code_generation()`
  (Coding), `backend_agent_code_review()`(MVP-0001 시점 예시, Stage
  05/Validation Responsibility에 더 가까움)
- `hqs/development/mvp/engine.py` — `call_engine()`
- `hqs/development/mvp/workflow.py`, `workflow_0002.py`,
  `workflow_hello_sdlc.py`, `workflow_0008.py`, `workflow_artifact_flow.py`

Refactoring/Git 작업/Documentation Responsibility에 대응하는 코드는 아직
없다(`docs/research/DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001.md` §8
참조).

## 상태

Capability 배정(`code_generation` 등 기존 목록과의 정식 매핑)은 아직
결정되지 않았다(`docs/governance/adc/ADC-0003.md` 판단 2: Defer). 관련
MVP 계획은 `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md` §11의
MVP-0004 후보를 참조한다.
