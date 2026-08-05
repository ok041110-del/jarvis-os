# Development HQ DevKit

Development HQ를 검증하기 위한 첫 번째 Dogfooding 프로젝트(Testbed)다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용해 만든 첫 번째 결과물이다.** 이 디렉토리는 Development
HQ 코드(`development-hq/mvp`, `development-hq/stages` 등)를 한 줄도
수정하지 않는다 — `runner.py`가 그 안의 기존 함수를 import해서 그대로
호출할 뿐이다.

## 무엇을 하는가

Issue 하나를 입력하면:

```
Issue -> Project Intelligence -> Planning -> Design -> Validation
```

까지 사람 개입 없이 실행하고, 그 결과를 Issue별로
`issues/<issue-id>/planning.md`, `design.md`, `validation.md` 세
Markdown 파일로 저장한다.

## Out of Scope (이번 단계)

- Implementation(Code Generation) — Design 산출물을 그대로 Validation
  Capability(`code_review`, `test_execution`)에 입력해 관찰만 한다.
  실제 코드를 생성하지 않는다.
- 새 Capability, Task Dispatcher 일반화, Runtime, Stage Runner,
  Pipeline Runner, Event Bus, Scheduler, Multi-Agent, Engine Adapter,
  Model Routing — 모두 이번 프로젝트 범위 밖이다.
- Git 자동 Commit, Pull Request 자동 생성.

## Development HQ Update Policy

이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는 근거로
쓰지 않는다. `docs/governance/observations/`에 OBS로 기록하고,
반복 관찰된 뒤에만 Evidence Review → Governance(RFC/ADC/ADR) 절차로
넘긴다. Observe First, Decide Later. Accumulate Before Escalate.
