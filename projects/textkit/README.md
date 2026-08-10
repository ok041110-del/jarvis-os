# TextKit

Development HQ를 이용해 만든 두 번째 Dogfooding 프로젝트(Testbed)다.
`projects/development-hq-devkit`가 단일 Issue로 Design/Validation까지만
관찰했다면, TextKit은 **여러 개의 실제로 연결된 Issue를 Planning →
Design → Implementation → Validation까지 전부 실행**해, 실제 Task가
여러 개일 때 자연스럽게 필요한 것(Context 전달, 파일 간 의존, 조건
분기, Review 이후 수정)을 그대로 관찰한다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용해 만든 결과물이다.** 이 디렉토리는 Development HQ
코드(`development-hq/mvp`)를 한 줄도 수정하지 않는다 —
`runner.py`가 그 안의 기존 함수를 import해서 순서대로 호출할 뿐이다.

## 무엇을 하는가

작고 실제로 쓸 수 있는 텍스트 유틸리티 라이브러리(`src/textkit/`)를
Issue 3개로 나눠 만든다.

1. `slugify(text) -> str` — URL-safe 슬러그 생성
2. `truncate(text, max_len, suffix="...") -> str` — 말줄임 자르기
3. `cli.py` — 위 두 함수를 실제로 import해서 쓰는 커맨드라인 진입점

각 Issue는:

```
Issue -> Project Intelligence(선행 Issue 실제 코드를 Context로 포함) ->
Planning -> Design -> Implementation(code_generation) ->
src/textkit/<module>.py 저장 ->
Validation(workflow_0002.run_mvp_0002 그대로 재사용 — NO_ISSUES_MARKER
조건 분기 포함)
```

순서로 실행되고, 결과를 `issues/<issue-id>/planning.md`, `design.md`,
`validation.md`로 저장한다. Issue 2·3은 앞선 Issue가 실제로 만든
`src/textkit/*.py` 파일 내용을 Issue description에 `[Existing Code]`
블록으로 그대로 붙여 Context로 전달한다 — 새 Project Intelligence
메커니즘이 아니라, `workflow_project_intelligence._enrich_issue`가 이미
쓰는 것과 같은 패턴(Issue description에 텍스트를 덧붙이는 것)이다.

Validation이 실제 pytest로 이어지는 경로(`tests/`)는 사람이
`test_execution` 제안을 읽고 실제 테스트 코드로 옮겨 적은 뒤 실제로
실행한다 — Development HQ의 어떤 Capability도 파일을 쓰거나 테스트를
실행하지 않는다(Engine 호출은 여전히 상태 없는 text-in/text-out
함수다). pytest가 실제로 실패하면, 그 실패 메시지를 다시
`backend_agent_code_generation()`(기존 Capability, 새 Capability 아님)의
입력에 포함해 수정을 요청하고, 수정된 코드로 Review·pytest를
재실행해 확인한다.

## Out of Scope

- 새 Capability, Task Dispatcher 일반화, Runtime, Stage Runner,
  Pipeline Runner, Event Bus, Scheduler, Multi-Agent, Engine Adapter,
  Model Routing, Kernel Component, Production caller, Prompt Cache —
  모두 이번 프로젝트 범위 밖이다.
- 이 프로젝트는 Production caller 후보가 **아니다**. `runner.py`는
  `projects/development-hq-devkit/runner.py`와 정확히 같은 성격(검증
  목적 스크립트)이며, production 위치로 승격하려는 시도가 아니다
  (`ADC-0010` C5 조건: "승격 시도가 실제로 관찰되거나 명시적으로
  제안되어야 한다" — 이 프로젝트는 그런 시도를 하지 않는다).
- `core/execution_layer`를 참조하지 않는다(devkit과 동일).
- Git 자동 Commit, Pull Request 자동 생성 — Engine이나 runner가 하지
  않는다.

## Development HQ Update Policy

`projects/development-hq-devkit/README.md`와 동일: 이 프로젝트에서
발견되는 문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다.
반복 관찰된 뒤에만 Observation → Evidence Review → Governance 절차로
넘긴다. Observe First, Decide Later.
