# MVP-0039 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — 실제 Engine 3회 독립 호출로 재현한 실제 Contract 위반을
고쳤다.

## 목적

`MVP-0038`과 같은 이유(`GOVERNANCE-REVIEW-0004`·`0005`: Production
caller 위치 미결 동안 진행 가능한 트랙은 Development HQ Capability
Engineering뿐)로, 아직 개선 가치가 높은 Capability를 다시 선정한다.
이번에는 `docs/01_mvp/MVP-0026~0033` 등 최근 real-Engine 검증
문서들을 재검토해 이미 도달 가능한(dead code 아닌) 경로 중 아직
고쳐지지 않은 것을 찾았다.

### 후보 검토

`backend_agent_code_generation()`(`development-hq/mvp/agents.py`)의
지시 문장은 "Based on the following design, write the implementation
code. Return only the code, with no surrounding commentary."다 —
코드만 반환하라는 명시적 Contract다. 이 함수가 실제로 그 Contract를
지키는지 직접 실행으로 확인해 본 적이 이전 MVP 어디에도 없었다
(`grep -n "backend_agent_code_generation" docs/01_mvp/*.md`로 확인—
`MVP-0025/0030~0033`은 이 함수를 호출하는 workflow의 결과만 요약해서
기록했을 뿐, 반환값 자체의 형태(markdown fence 포함 여부)를 직접
검사한 적은 없었다).

## 발견한 문제 (실제 Engine 3회 독립 호출로 재현)

서로 다른 Issue/언어로 `design_agent_design()` → `backend_agent_code_generation()`을
3회 독립적으로 실행했다(mock 없음, 매회 새 `claude -p` 프로세스):

| 실행 | Issue | 반환값(발췌) |
|---|---|---|
| 1 | "Add divide() input validation" | ` ```python\ndef divide(dividend, divisor):\n    ...\n``` \n` |
| 2 | "Add clamp helper"(언어 미지정) | ` ```javascript\nfunction clamp(value, min, max) {\n  ...\n} \n``` \n` |
| 3 | "Add a slugify helper" | ` ```python\nimport re\nimport unicodedata\n\n\ndef slugify(...):\n    ...\n``` \n` |

**3회 모두** 실제 Engine이 지시("코드만, 부가 설명 없이")를 문자
그대로는 지키지 않고, 코드 전체를 markdown fence(` ```{언어}\n...\n``` `)로
감싸서 반환했다. 이 반환값은 그대로 `backend_agent_code_review(code)`/
`qa_agent_test_execution(code, review)`의 `code` 인자로 전달되므로,
이후 두 Capability가 "코드"로 받는 입력에 fence 마커가 섞여 있었다.

## 변경 파일

- `development-hq/mvp/agents.py`
  - `_strip_code_fence(text)`(신규 헬퍼): 반환값의 첫 줄이 ` ``` `로
    시작하고 마지막 줄이 정확히 ` ``` `인 경우에만 그 감싸는 두 줄을
    제거하고 안쪽 내용만 반환한다. 그 형태가 아니면(Engine이 fence
    없이 코드만 반환한 경우 등) 원문을 그대로 반환한다 — 새 파싱
    Capability가 아니라 기존 `backend_agent_code_generation` 하나의
    출력을 그 자신의 지시문 Contract에 맞게 정리하는 최소 후처리다.
  - `backend_agent_code_generation()`: `call_engine()` 반환값에
    `_strip_code_fence()`를 적용한 뒤 반환하도록 한 줄 추가했다.
    함수 시그니처(`str -> str`)와 지시 문장은 바꾸지 않았다.

## 관찰 결과 — 단위 검증

`_strip_code_fence()`를 위 3개 실제 반환값 그대로에 적용한 결과, 3개
전부 fence 없이 순수 코드만 남았다(예: `def divide(dividend, divisor):\n    ...`,
fence 마커 없음). fence가 없는 입력(`"def plain(): pass\n"`)과 빈
문자열은 그대로 반환됨을 확인했다 — 회귀 없음.

## 실제 Engine으로 End-to-End 검증 (mock 없음)

### 1) `run_issue_to_implementation()`(clamp 함수, 72.5초)

수정 후 `implementation` 필드가 fence 없이 순수 함수 정의 하나로
정확히 반환됨을 확인했다(`str.startswith("```")`/`endswith("```")`
모두 `False`).

### 2) `run_hello_sdlc()`(divide 함수, 100.7초) — 잔여 케이스 발견

이 실행에서 실제 Engine이 **하나의 응답 안에 fenced code block 2개**
(구현 함수 + 별도 테스트 파일)를 반환하는 경우를 처음 실측 확인했다.
`_strip_code_fence()`는 "전체가 하나의 fence로 감싸인 경우"만 벗기도록
설계했으므로(위 "변경 파일" 참고), 이 경우 가장 바깥쪽 fence 한 쌍만
제거되고, 두 코드 블록 사이의 내부 fence 마커(```` ```\n\n```python ````)는
그대로 `implementation` 문자열 중간에 남았다. 이후 `code_review`(2352자)/
`test_execution`(2073자)은 예외 없이 정상 반환됐고, `code_review`는 이
잔여 마커를 오류로 지어내지 않고 실제로 "두 번째 코드 블록이
`import pytest`만 하고 `divide`를 import하지 않는다"는 실질적인 문제로
정확히 지적했다 — 파이프라인이 깨지지는 않았다.

## 이 잔여 케이스를 고치지 않은 이유

"코드 생성 요청에 대해 Engine이 구현 코드 외에 테스트 코드까지 함께
반환하는 경우가 있다"는 사실은, 지금 고치려면 응답 안에서 fenced
block이 몇 개인지 세고 그중 "진짜 구현"에 해당하는 블록만 선택하는
조건부 파싱 로직이 필요하다 — `MVP-0030`이 이미 같은 이유로 수정을
보류한 것("입력 종류를 구분해 다르게 동작하게 만드는 것은 Capability
Logic에 조건 분기를 추가하는 것이며, `MVP-0002`의 RT-0001 관찰 대상과
같은 종류의 변화")과 정확히 같은 종류의 변화다. 이번 MVP가 고친
"단일 fence 감싸기"(항상 재현됨, 3/3)와 달리 이 "다중 블록" 현상은
이번 관찰에서 1회만 나타났고, 재현 조건도 특정하지 못했다 — 재현
비율을 확인하지 않은 채 조건 분기를 추가하는 것은 이번 지시("새
Architecture가 필요하면 임의 설계하지 말고 중단 후 보고")의 정신에
맞지 않는다. 고치지 않고 Evidence로만 기록한다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음, 68.0초).
- `git status --porcelain` — `development-hq/mvp/agents.py` 1개
  파일만 변경.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 |
| Capability Logic에 입력 종류별 조건 분기 추가 | 미발동 — "다중 fence 블록" 잔여 케이스를 의도적으로 고치지 않고 Evidence로만 남겼다(위 "고치지 않은 이유") |
| 새 Capability/Agent/Engine 추가 | 미발동 |
| 새 Architecture/Concept/Component 필요 | 미발동 |

**하나도 발동하지 않았다.** 잔여 케이스는 새 Architecture가 필요할
수 있는 지점으로 판단해 임의로 설계하지 않고 그대로 보고한다(위
"이 잔여 케이스를 고치지 않은 이유").

## 범위 밖 (이번 구현에서 하지 않은 것)

- Production caller, Kernel Component, Runtime, Prompt Cache — 건드리지
  않았다.
- 다중 fence 블록 파싱 로직 — 위 이유로 고치지 않았다.
- `backend_agent_code_review`/`qa_agent_test_execution`의 지시
  문장 — 건드리지 않았다.
- 새 RFC/ADC/ADR — 만들지 않았다. 이번 수정은 Architecture 결정이
  필요한 지점을 만들지 않았다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`agents.py`)**. 실제로 3회
  독립 재현한 실제 Contract 위반(fence 감싸기)을 최소 후처리
  헬퍼 하나로 고쳤다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `backend_agent_code_generation()`의 시그니처와 지시 문장도
  그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. 수정 전 재현 3회, 수정 후
  단위 검증(3개 실제 샘플) + End-to-End 2회(`run_issue_to_implementation`,
  `run_hello_sdlc`) 모두 실제 `claude -p` 호출(mock 없음). 기존
  pytest 3건도 real Engine 포함 재실행해 회귀 없음을 확인했다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  단일 fence 감싸기는 고쳤다고 정확히 기록했고, 다중 fence 블록
  잔여 케이스는 고치지 않았다는 사실과 그 이유를 숨기지 않았다.
- 새 Architecture가 필요한 지점을 만나 임의로 설계했는가 —
  **아니오**. 다중 fence 블록 케이스에서 멈추고 그 사실을 그대로
  기록했다(위 "고치지 않은 이유").
- 불필요한 변경을 확인했는가 — **예**. `engine.py`, `workflow*.py`,
  `cli.py`, `project_intelligence.py` 어디에도 손대지 않았다
  (`git status --porcelain` 확인).
