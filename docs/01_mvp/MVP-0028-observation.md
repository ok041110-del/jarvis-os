# MVP-0028 Observation

## 목적

MVP-0009의 `run_comparison()`(같은 Issue로 flat Context Planning과
Context Bundle Planning을 각각 실제 Engine으로 실행해 나란히 비교)을
처음으로 실제 Engine으로 실행했다. 그 과정에서 `call_engine()`이
`STATELESS_CALL_NOTICE` 계약과 다르게 동작하는 실제 Blocking급 문제를
발견해 최소 수정으로 해소했고, 재실행으로 검증했다.

## 실행 1 — 문제 발견 (수정 전)

`run_comparison(REAL_ISSUE)`(MVP-0008의 실제 Issue "Project Intelligence
개선")를 실행했다(234.8초, 실제 Engine 2회 호출). 두 결과
(`flat_context_planning`, `context_bundle_planning`) 모두 요구된
"Requirement를 prose로 서술"이 아니라, 다음과 같은 이상 동작을 보였다:

- "이번 세션에는 파일시스템 조회 도구가 없어 ... 첨부된 거버넌스 문서를
  직접 열람하지 못했습니다(하위 조사 에이전트도 동일하게 도구 접근이
  차단됨)"처럼 이 저장소 고유의 개념(하위 조사 에이전트)을 언급.
- "**다음 단계 제안:** ... `context-loader` → `task-intake` 순서로
  ... 확인" — 이 저장소의 `.claude` Skill 이름을 그대로 인용.
- `context_bundle_planning`은 아예 이 저장소 `task-intake` Skill의
  출력 형식(`## Task`, `## Type`, `## Scope`, `## Non-goals`,
  `## Acceptance Criteria`, `## Required Context`, `## Boundary /
  Risk`, `## Next Skill`)을 그대로 흉내 냈다 — `REQUIREMENT_ANALYSIS:`
  프롬프트가 요구한 것과 다른 산출물 형식이다.

### 원인

`engine.py`의 `call_engine()`은 `subprocess.run()`에 `cwd`를 지정하지
않았다 — 호출한 Python 프로세스의 작업 디렉터리(이 저장소 안,
`development-hq/`)를 그대로 물려받았다. `claude -p`는 실행 디렉터리의
`CLAUDE.md`와 `.claude/skills`를 자동으로 읽으므로, "Engine으로
호출된 것"이 실제로는 **이 저장소 자신의 project-level 지시사항을
따르는 또 다른 대화형 Claude Code 세션**처럼 동작했다. Issue 내용이
이 저장소의 Development HQ/MVP 용어와 겹칠수록(REAL_ISSUE가 바로 그런
사례) 이 오염이 더 뚜렷하게 나타났다 — 이전 MVP-0025~0027에서 쓴
`divide()`/`add()` 같은 범용 Issue에서는 상대적으로 덜 두드러졌던
이유이기도 하다.

이는 이미 `engine.py`가 명시한 `STATELESS_CALL_NOTICE` 계약("You are
being invoked as a stateless text-in/text-out function call, not an
interactive coding session")을 실제 Engine 레벨에서 위반하는 사례다 —
Capability Logic이 아니라 Engine 호출 함수 자체의 문제이므로, 기존
Contract("단일 함수로 Engine을 호출") 안에서 그 함수의 호출 인자만
바꿔 해소 가능한지부터 확인했다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `import tempfile` 추가.
  - `subprocess.run()`에 `cwd=tempfile.gettempdir()`를 추가했다 —
    Engine 프로세스가 이 저장소의 `CLAUDE.md`/Skill을 더 이상 읽지
    않도록 저장소 밖 중립 디렉터리에서 실행한다. `call_engine()`이
    유일한 Engine 호출 지점이라는 사실, 함수 시그니처, 인자(`prompt`
    하나)는 그대로다 — 새 Gateway/Adapter가 아니라 기존 단일 함수
    호출의 `subprocess.run` 인자 하나(`cwd`)만 추가했다.

## 실행 2 — 수정 검증 (재실행)

### 격리 재현 (수정 확인용, `run_comparison()`과 별도)

같은 REQUIREMENT_ANALYSIS 프롬프트를 `cwd`만 바꿔 직접
`subprocess.run()`으로 두 번 비교했다: 수정 전 cwd(저장소 안)는 위와
동일한 오염된 출력을, 수정 후 cwd(`tempfile.gettempdir()`)는 Skill/
하위 에이전트 언급 없이 "## Project Intelligence 개선 — 요구사항
분석"으로 시작하는 순수한 prose Requirement 분석을 반환했다.

### `run_comparison()` 재실행 (실제 프로덕션 경로)

수정된 `engine.py`로 `run_comparison(REAL_ISSUE)`를 다시 실행했다
(92.5초). 두 결과 모두 더 이상 Skill/하위 에이전트/도구 부재를
언급하지 않았고, `REQUIREMENT_ANALYSIS:` 지시대로 Goal/Scope/Risks를
prose로 서술하는 산출물을 반환했다.

## flat vs Context Bundle 비교 (수정 후, run_comparison의 원래 목적)

| 항목 | flat_context_planning | context_bundle_planning |
|---|---|---|
| 길이 | 2299자 | 2358자 |
| 절 구성 | Goal/범위/리스크 3절 | Goal/Scope/Risks 3절 + 말미에 Open Question 1개 |
| MVP-0007 원인 인용 | 정확히 인용 | 정확히 인용 |
| 관련 RFC/ADR 인용 | RFC-0003/0004/0005, ADR-0003 | RFC-0003/0004/0005, ADR-0001~0003 |
| 회귀·경계 리스크 언급 | 있음 | 있음 |

이번 Issue에서는 flat Context와 Context Bundle 두 방식이 만들어낸
Planning 품질에 관찰 가능한 뚜렷한 차이가 없었다 — 둘 다 Issue의 핵심
원인(Artifact 이어붙이기로 인한 Context 누수)을 정확히 파악했고, 관련
Governance 문서를 유사한 폭으로 인용했다. `run_comparison()`의 원래
설계 의도(`workflow_0009.py` docstring: "어느 쪽이 더 나은지는 이
코드가 판단하지 않는다")대로, 이 관찰은 우열을 판단하지 않고 사실만
기록한다.

## Regression 확인

- `development-hq/mvp/tests/test_mvp_0001.py` 3건 모두 통과 — `cwd`
  변경이 `call_engine()`의 반환값 형태(코드 리뷰/테스트 케이스
  텍스트)에 영향을 주지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**. `call_engine()`은 여전히
  Engine을 호출하는 유일한 단일 함수다.
- 새 Capability/Agent/Gateway를 만들었는가 — **아니오**.
  `subprocess.run`의 기존 호출에 표준 라이브러리 인자(`cwd`) 하나만
  추가했다.
- 실제 Engine으로 확인했는가 — **예**. 격리 재현과 `run_comparison()`
  프로덕션 경로 양쪽 모두 수정 전/후를 실제 `claude -p` 호출(mock
  없음)로 비교했다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- flat vs bundle 우열을 판단했는가 — **아니오**. `run_comparison()`의
  설계 의도대로 관찰된 사실만 기록했다.
- 실패를 성공으로 표현했는가 — **아니오**.
