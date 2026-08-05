# Stage: Validation

## 목적

구현 결과를 검증한다.

## Responsibility

- Unit Test
- Integration Test
- Review
- Lint
- Security
- Performance

## Reference

- OpenHands
- Claude Code

## 참고 구현 예시 (기존 코드, 이동하지 않음)

이 Stage의 Unit Test/Review Responsibility는 이미 Development HQ
MVP-0001·MVP-0002에서 `test_execution`, `code_review` Capability로
관찰되었다. 아래는 참조 링크일 뿐이며, 이 문서 작성으로 코드가 이동되거나
수정되지 않았다.

- `development-hq/mvp/agents.py` — `qa_agent_test_execution()`
- `development-hq/mvp/workflow.py`, `workflow_0002.py`
- `development-hq/mvp/tests/test_mvp_0001.py`

## 상태

Capability 배정(Lint/Security/Performance 세분화 여부 등)은 아직
결정되지 않았다(`docs/governance/adc/ADC-0003.md` 판단 2: Defer). 관련
MVP 계획은 `docs/02_rfc/RFC-0003-development-hq-sdlc-pivot.md` §11의
MVP-0005 후보를 참조한다.
