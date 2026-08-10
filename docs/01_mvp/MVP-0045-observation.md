# MVP-0045 Observation

**문서 성격**: 실제 실행 기록(Evidence). 단일 Issue 검증을 넘어,
**실제 개발 프로젝트 하나**(`projects/textkit/`)를 Development HQ의
기존 Capability만으로 요구사항 분석 → 계획 → 설계 → 다단계 구현 →
Review → Test → 수정 → 최종 검증까지 처음부터 끝까지 수행했다.
`development-hq/mvp/`는 한 줄도 수정하지 않았다.

## 목적

`MVP-0001~0044`는 모두 단일 Issue(코드 한 덩어리, 또는 조사 1건)를
Development HQ Pipeline에 넣고 관찰하는 패턴이었다. 이번 세션은 그
경계를 넘어, **여러 Issue가 실제로 연결된 프로젝트**를 만들어 여러
파일·여러 Task·Task 간 Context 전달·조건 분기·Review 이후 실제 수정
사이클이 자연스럽게 필요할 때 Development HQ가 그것을 그대로
처리하는지 관찰했다.

## 선정한 실제 프로젝트

`projects/textkit/` — 작고 실제로 동작하는 텍스트 유틸리티 라이브러리.
`projects/development-hq-devkit`(기존 Dogfooding 프로젝트, Design/
Validation까지만 다룸)와 같은 성격(검증 목적, Production caller 후보
아님, `core/execution_layer` 미참조 — `grep -rn "execution_layer"
projects/textkit` 확인됨)의 **두 번째** Dogfooding 프로젝트로 별도
생성했다. 기존 devkit은 수정하지 않았다(ADC-0010/ADC-0011/RFC-0011이
devkit을 C5 후보 Evidence로 인용하고 있어, 그 근거를 바꾸지 않기
위함).

Issue 3개:

1. `slugify(text) -> str` — URL-safe 슬러그 생성
2. `truncate(text, max_len, suffix="...") -> str` — 말줄임 자르기
3. `cli.py` — 위 두 함수를 실제로 import해서 쓰는 argparse 기반 CLI

`runner.py`는 `development-hq/mvp`의 기존 함수
(`requirements_agent_requirement_analysis`, `design_agent_design`,
`backend_agent_code_generation`, `workflow_0002.run_mvp_0002`)만
하드코딩된 순서로 호출한다 — 새 Capability/Dispatcher/Runtime을
만들지 않았다.

## 1. 여러 Task, 여러 파일, Context 전달 — 실제 실행

3개 Issue 모두 real Engine으로 Planning → Design →
Implementation(`backend_agent_code_generation`) → Validation
(`run_mvp_0002`)을 완주했다(mock 없음). Issue 2·3은 앞선 Issue가
실제로 `src/textkit/`에 써 놓은 소스 코드를 Issue description에
`[Existing Code]` 블록으로 그대로 붙여 전달했다(`_enrich_issue`가
쓰는 것과 같은 패턴, 새 메커니즘 아님) — 실제로 Issue 3의 Design/
Implementation은 `from textkit.slugify import slugify` /
`from textkit.truncate import truncate`를 정확히 그 두 함수의 실제
시그니처로 생성했다. 이는 OBS-0003("Context 전달 메커니즘")이
관찰해 온 것과 같은 종류의 전달이 실제 다중 Task 프로젝트에서도
그대로 작동함을 보여준다.

## 2. 조건 분기 — 실제 관찰

각 Issue의 Validation은 기존 `workflow_0002.run_mvp_0002()`를 그대로
재사용했다 — `NO_ISSUES_MARKER` 조건 분기(이슈 없으면 test_execution
생략)를 새로 만들지 않고 그대로 노출시켰다. 3개 Issue 모두 real
Review가 실제 개선점을 찾아 분기가 "생략" 쪽으로 가지 않았다(항상
test_execution 실행) — 이는 강제로 만든 분기가 아니라 실제 코드
품질에 따라 자연스럽게 결정된 결과다.

## 3. Review가 실제로 찾아낸 결함과 2라운드 Fix Cycle (`truncate`)

Issue 2(`truncate`)의 첫 real Review는 실제 결함을 지적했다:
`max_len < len(suffix)` 검증이 `len(text) <= max_len` 조기 반환
**뒤에** 있어, 텍스트가 이미 `max_len` 안에 들어가면 검증이
건너뛰어진다. 이를 pytest로 직접 재현(`DID NOT RAISE ValueError`)한
뒤, 원본 코드 + 실제 pytest 실패 메시지를 기존
`backend_agent_code_generation()`에 그대로 입력해 재호출했다(새
Capability 아님, 기존 Capability의 반복 호출).

수정된 코드를 다시 real Review에 넣자, **정반대 방향의 실제 결함**을
새로 찾아냈다: 검증을 조기 반환보다 앞으로 옮기자 이번엔 정상적으로
"이미 fit하는" 짧은 입력(`truncate("ok", 2)`)까지 부당하게
`ValueError`를 던지게 됐다. 두 라운드는 서로 모순이 아니라, Issue
description이 "언제" 검증해야 하는지를 명시하지 않은 데서 온 자연스러운
명세 모호성이었다 — 최종 판단은 코드를 원래 순서로 되돌리고
docstring의 "Raises" 절만 실제 동작("truncation이 실제로 필요할
때만 검증")에 맞게 정정하는 것이었다. Round 1이 잘못된 가정(무조건
raise)을 인코딩했던 pytest 테스트도 함께 고쳤다. 세 번째 real
Review(최종 코드 재확인)는 "핵심 로직이 문서화된 계약과 일치한다"고
확인했다. 전체 기록: `projects/textkit/issues/0002-truncate/fix-cycle.md`.

## 4. 실제 검증 (mock 없음)

```
$ python3 -m pytest projects/textkit/tests -v
...
============================== 32 passed in 0.05s ==============================
```

`test_slugify.py`(12건), `test_truncate.py`(12건, Fix Cycle 이후 최종
계약 반영), `test_cli.py`(8건) 전부 실제 생성된 코드에 대해 실행해
통과했다. CLI도 실제로 실행해 확인했다:

```
$ python3 -m textkit.cli slugify "Hello, World! Café"
hello-world-caf
$ python3 -m textkit.cli truncate "This is a longer sentence that needs truncating" --max-len 20
This is a longer ...
```

### Development HQ 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
...                                                                      [100%]
3 passed in 61.29s (0:01:01)
```

`development-hq/mvp/` 어떤 파일도 수정하지 않았다(`git status
--porcelain`에 `development-hq/` 변경 없음, `projects/textkit/`만
신규 추가).

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — `runner.py`는 하드코딩된 순차 호출만 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 |
| 새 Capability/Agent/Engine 추가 | 미발동 — 기존 4개 함수만 재사용 |
| Kernel Component/Runtime/Production caller/Prompt Cache 착수 | 미발동 — `core/execution_layer` 미참조 확인됨, `projects/development-hq-devkit`와 동일한 검증 전용 성격 유지 |
| 새 Architecture/Concept/Component 필요 | 미발동 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `projects/development-hq-devkit` 수정 — 하지 않았다(별도 프로젝트로
  분리).
- 남은 스타일/견고성 지적(Unicode grapheme 경계, `suffix=None`
  `TypeError`, 에러 메시지 우선순위) — 이번 세션에서 실제로 재현되지
  않은 이론적 확장이라 반영하지 않았다.
- 새 RFC/ADC/ADR — 만들지 않았다.
- `development-hq/mvp/` 수정 — 전혀 하지 않았다.

## Self Review

- 코드를 변경했는가 — **예**, 새 프로젝트 디렉토리
  (`projects/textkit/`) 하나를 추가했다. `development-hq/mvp/`는
  변경하지 않았다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `projects/development-hq-devkit`와 같은 패턴(검증용 별도
  프로젝트)을 재사용했다.
- 실제 Engine으로 확인했는가 — **예**. 3개 Issue × (Planning/Design/
  Implementation/Review, 조건부 Test) + Fix Cycle 2라운드(Review 2회,
  code_generation 1회 추가) — 전부 real `claude -p` 호출, mock 없음.
  실제 pytest 32건, 실제 CLI 실행 2회, development-hq 기존 pytest
  3건도 재실행.
- 같은 종류의 작은 결함을 여러 MVP로 쪼갰는가 — **아니오**. 3개
  Issue의 전체 SDLC와 Fix Cycle을 이 세션 하나에서 연속으로 처리했다.
- 구조적 Architecture 결정이 필요한 문제를 만났는가 — **아니오**.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  Round 1 pytest 테스트 자체가 잘못된 가정을 인코딩했던 사실도 그대로
  기록했다.
- 불필요한 변경을 확인했는가 — **예**. `development-hq/`,
  `projects/development-hq-devkit/` 어디에도 손대지 않았다
  (`git status --porcelain` 확인).
