# MVP-0038 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — Project Intelligence Capability(`collect_relevant_context`,
MVP-0005/0006)의 관련 파일 선정 로직에서 실제로 관찰한 정밀도 결함을
고쳤다.

## 목적

`GOVERNANCE-REVIEW-0004`·`GOVERNANCE-REVIEW-0005`가 확인한 대로,
Production caller 위치(`ADC-0010`)가 미결인 동안 진행 가능한 트랙은
caller 위치가 필요 없는 **Development HQ Capability Engineering**뿐이다
(`development-hq/CONSTITUTION.md`: Architecture < Capability <
Dogfooding < Observation < Evidence). 이번 MVP는 기존 MVP/Evidence를
검토해 아직 구현 가치가 높은 Capability 하나를 선정하고, 기존
Architecture/Contract 안에서 실제로 구현·검증한다.

### 후보 검토 — 왜 이 Capability인가

- `docs/governance/observations/OBS-0003~0006`을 다시 확인한 결과,
  이 4개 관찰은 모두 `call_engine()`이 실제 Engine을 호출하기 **이전**
  (rule-based `_review_design`/`_analyze_requirement` 등이 응답을
  만들던 시절)의 `projects/development-hq-devkit` 실행에서 나온
  Fact였다 — devkit 관찰 문서(`observation.md`) 자신이 기록한 Planning
  출력("요구사항: '{title}' 기능이 필요하다...")이 `_analyze_requirement`의
  MVP-0010 이전 고정 템플릿과 정확히 일치한다. `ENGINE-CONNECT-0001`
  이후 `call_engine()`은 `_rule_based_response()`를 더 이상 호출하지
  않는다(`grep -rn "_rule_based_response" development-hq/ projects/`
  결과, 자기 자신의 주석 1건 외 호출부 0건 — 이번 조사에서 재확인).
  즉 OBS-0003~0006이 다루는 코드 경로는 현재 프로덕션 경로에서
  **도달 불가능**하다 — 그 경로를 더 개선하는 것은 구현 가치가 낮다.
- 대신 `development-hq/mvp/project_intelligence.py`의
  `collect_relevant_context()`는 지금도 모든 실제 workflow
  (`run_issue_to_planning`/`run_issue_to_design`/`run_pipeline`/
  `run_comparison`)가 실제 Engine 호출 **직전**에 호출하는, 도달
  가능한 실제 Capability다. 이 함수의 `_score()`가 관련 파일을
  선정하는 방식을 직접 실행해 확인한 결과, 실제 결함이 있었다(아래
  "발견한 문제").

## 발견한 문제 (직접 실행으로 확인)

`_keywords()`는 길이 2자 이상인 모든 토큰을 키워드로 쓰고,
`_score()`는 그 키워드가 파일 내용에 **부분 문자열로** 포함되는지만
확인했다. 실제 Issue로 직접 실행한 결과:

```python
issue = {
    "title": "Prompt instruction improvement for QA capability",
    "description": "When the qa agent proposes test cases, it does not "
        "always cover exception paths that were flagged by the reviewer, "
        "so the suggested tests should reference the review findings "
        "more directly.",
}
```

이 Issue는 명백히 `agents.py`(QA/Backend Agent의 Capability 지시
문장을 정의하는 파일)와 가장 관련이 크다. 그러나 수정 전 `_score()`는
`agents.py`에 7점을 준 반면, Issue와 무관한 `engine.py`에 10점을 줬다
— "of"/"not"/"an"/"the"/"in"/"so" 같은 순수 영문 관사/전치사/접속사가
`development-hq/mvp/`의 거의 모든 파일 주석·docstring에 등장해 실제
주제어(agent/capability/qa 등) 신호를 덮어버렸기 때문이다. `"so"`처럼
2자짜리 단어는 부분 문자열 매칭 때문에 `"also"`/`"reason"` 등 무관한
단어 안에서도 걸렸다 — `_extract_open_questions()`의 `_OPEN_WORD_RE`가
이미 "OpenHands"/"OpenAI" 오탐을 막기 위해 단어 경계 매칭을 쓰던 것과
같은 종류의 문제였다.

## 변경 파일

- `development-hq/mvp/project_intelligence.py`
  1. `_STOPWORDS`(신규 모듈 상수): 도메인과 무관하게 항상 의미가 없는
     영문 관사/전치사/접속사/대명사/조동사만 담는다(`a`/`an`/`the`/
     `in`/`of`/`not`/`is`/`can` 등). `_keywords()`가 이 집합에 속한
     토큰을 제외하도록 한 줄만 바꿨다 — `workflow`/`engine`/
     `exception`처럼 실제로 의미 있는 도메인 단어는 제외 대상에
     넣지 않았다(실측으로 신호가 있었음을 확인한 단어들, 위 "발견한
     문제" 참고).
  2. `_score()`: 부분 문자열 매칭(`kw in haystack`)을 단어 경계 매칭
     (`re.search(rf"\b{re.escape(kw)}\b", haystack)`)으로 바꿨다 —
     새 기법이 아니라 같은 파일의 `_extract_open_questions()`가 이미
     쓰던 `_OPEN_WORD_RE`(`\bopen\b`) 기법을 그대로 재사용한 것이다.
  - `collect_relevant_context()`/`build_context_bundle()`의 반환
    Contract(카테고리별 키, 각 카테고리가 파일 경로 `list[str]`)는
    바꾸지 않았다. 새 카테고리/새 Capability/새 파라미터를 추가하지
    않았다.

## 관찰 결과 — 수정 전/후 비교 (직접 실행)

같은 Issue(위 코드 블록)로 `_score()`가 매긴 각 파일의 점수:

| 파일 | 수정 전 | 수정 후 |
|---|---|---|
| `agents.py` | 7 | **7 (1위)** |
| `engine.py` | **10 (1위)** | 6 |
| `project_intelligence.py` | 4 | 4 |
| `workflow_0002.py` | 4 | 4 |

`collect_relevant_context(issue)["source_code"]`(top 3):

- 수정 전: 확인 안 함(이번 MVP에서 처음 발견해 바로 수정) — 위 표의
  점수만으로도 `engine.py`가 `agents.py`보다 먼저 선정될 것이 명확함.
- 수정 후: `['development-hq/mvp/agents.py', 'development-hq/mvp/engine.py', 'development-hq/mvp/project_intelligence.py']`
  — Issue와 가장 관련 있는 `agents.py`가 1위로 정확히 선정됨.

## 실제 Engine으로 검증 (mock 없음)

위와 동일한 Issue로 `run_issue_to_planning(issue)`를 실제 Engine으로
1회 실행했다(`development-hq/mvp/workflow_project_intelligence.py`,
Project Intelligence → `requirement_analysis` Capability 순서 그대로,
새 경로를 만들지 않았다).

- 소요 시간: 38.8초.
- `context["source_code"]`: `['development-hq/mvp/agents.py', 'development-hq/mvp/engine.py', 'development-hq/mvp/project_intelligence.py']`
  (위 결과와 일치, 수정된 로직이 실제 workflow 경로에서도 그대로
  적용됨을 확인).
- `planning`(`requirements_agent_requirement_analysis`의 실제 Engine
  응답): 예외 없이 3,861자 반환. "QA Agent — Exception-Path
  Traceability to Reviewer Findings"라는 제목으로 Issue의 실제 의도
  (QA agent의 테스트 케이스가 reviewer findings를 더 직접 반영해야
  한다는 것)를 정확히 파악한 Requirement Analysis를 반환했다 — Engine
  호출 자체는 정상 동작했고, 개선된 Context가 이 호출을 방해하지
  않았다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음, 69.4초).
- `git status --porcelain` — `development-hq/mvp/project_intelligence.py`
  1개 파일만 변경.
- `git diff development-hq/mvp/project_intelligence.py` — 위 "변경
  파일" 절의 내용과 일치, 그 외 변경 없음.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 — `AGENT_CAPABILITY_MAP`을 건드리지 않았다 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — `_score()`/`_keywords()` 내부 로직만 바꿨다, 호출 순서·분기 없음 |
| 새 Capability/Agent/Engine 추가 | 미발동 |
| 새 Architecture/Concept/Component 필요 | 미발동 — 기존 함수 시그니처와 반환 Contract를 그대로 유지했다 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `_STOPWORDS`에 한글 불용어(조사 등)를 추가하지 않았다 — 이번
  실측에서 한글 불용어로 인한 오염 사례를 관찰하지 못했다(이 저장소의
  기존 관례: "실제로 관찰된 것만 등록한다", `engine.py`
  `NEGATED_MARKER_EXCEPTIONS` 주석 참고). 필요성이 실측되면 별도
  관찰로 다룬다.
- `_score()`를 빈도 기반(단순 존재 여부가 아니라 등장 횟수)으로
  바꾸지 않았다 — 이번에 관찰한 결함(기능어의 "어디에나 있음" 신호)은
  존재 여부 판단 방식(단어 경계)만으로 해소됐고, 빈도 가중치가
  필요하다는 별도 증거는 없다.
- `OBS-0003~0006`이 다루는 rule-based 경로(`_review_design` 등)는
  건드리지 않았다 — 위 "후보 검토"에서 확인한 대로 현재 프로덕션
  경로에서 도달 불가능한 코드이며, 이번 MVP의 대상이 아니다. 이
  발견(4개 OBS가 사실상 도달 불가능한 경로를 다룬다는 것) 자체는
  새 Architecture 판단이 아니라 코드 도달 가능성에 대한 사실 확인이므로
  별도 Governance 절차 없이 이 문서에 기록한다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`project_intelligence.py`)**.
  실제로 재현한 실제 결함(관사/전치사가 관련성 신호를 덮어씀)을
  이 저장소가 이미 쓰던 기법(단어 경계 매칭, `_OPEN_WORD_RE`와 동일)
  재사용으로 최소 수정했다. 새 Registry/Scheduler/Policy/Engine
  Gateway를 만들지 않았다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. `collect_relevant_context()`/`build_context_bundle()`의 반환
  Contract도 그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. `run_issue_to_planning()`을
  실제 `claude -p` 호출로 1회 실행(mock 없음, 38.8초), 개선된 Context
  선정이 실제 workflow 경로에서 그대로 적용되고 Engine 호출도 정상
  동작함을 확인했다. 기존 pytest 3건도 real Engine 포함 재실행해
  회귀 없음을 확인했다.
- Production caller, Kernel Component, Runtime, Prompt Cache를
  건드렸는가 — **아니오**. `project_intelligence.py` 내부 함수 2개만
  수정했다.
- 새 RFC/ADC/ADR이 필요했는가 — **아니오**. 새 Architecture 결정이
  필요한 지점을 만나지 않았다 — 만났다면 중단하고 보고했을 것이다
  (지시 4번).
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  수정 전 실제 점수(engine.py 10점 > agents.py 7점)와 수정 후 점수를
  모두 그대로 기록했다.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `engine.py`,
  `workflow*.py`, `cli.py` 어디에도 손대지 않았다(`git status
  --porcelain` 확인).
