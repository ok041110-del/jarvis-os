# MVP-0032 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** —
3단계 모두 정상 동작해 수정할 문제가 없었다.

## 목적

`workflow_artifact_flow.py`(MVP-0007)의 `run_issue_to_implementation()`을
MVP-0028의 cwd 수정 이후 처음으로 실제 Engine으로 실행한다. 이
함수는 `collect_relevant_context`(Project Intelligence)를 Planning
에서만 사용하고, Design에는 Context가 섞이지 않은 원본 Issue를 그대로
넘기는 것을 관찰하기 위한 것(MVP-0007의 목적)이다. MVP-0031이 확인한
"코드성 Issue에서는 파이프라인이 정상 동작한다"는 결론이 이 별도
경로(`run_issue_to_implementation`, Planning→Design→Implementation
3단계, Validation 없음)에서도 성립하는지 확인한다.

## 실행 (실제 Engine, 51.4초)

`CODE_ISSUE`(신규, 이 실행 전용): "Add a clamp() helper function" —
`clamp(value, low, high)`를 구현해 달라는 명확한 코드성 Issue.

| Stage | 길이(문자) | 내용 |
|---|---|---|
| planning | 3369 | Goal/Scope/Risks — `clamp()` 요구사항을 정확히 서술, `low > high` 미검증·NaN 처리·중복 가능성 등 실제로 유효한 위험을 지적 |
| design | 2216 | 구체적 구현 순서(`low` 먼저 검사)를 규정하고, 그 순서를 고른 이유를 명시 |
| implementation | 487 | **실제 동작하는 코드** — `clamp()` 구현 + docstring(전제조건과 NaN 처리 명시) |

## 관찰 결과

### 3단계 모두 정상 동작했는가?

**예.** MVP-0030에서 관찰된 "Implementation이 코드 작성을 거부"하는
현상은 나타나지 않았다 — Design이 "That's the full design; ready to
implement on your go-ahead"로 명확히 구현 준비 완료를 선언했고,
Implementation은 실제로 동작하는 코드를 반환했다. Planning → Design →
Implementation 각 단계가 이전 단계의 판단(예: `low` 우선 검사 순서,
NaN 미가드)을 다음 단계로 일관되게 전달했다.

### Project Intelligence는 Design에 전달되지 않는다는 계약이 지켜졌는가?

`context`가 수집한 파일 목록(`engine.py`/`agents.py`/
`workflow_artifact_flow.py`, MVP-0025/0014/0027 관찰 문서 등)이
`design` 출력 안에 그대로 나타나지 않았다 — `design`은 `clamp()`
자체의 설계에만 집중했고, 저장소의 다른 파일이나 거버넌스 문서를
인용하지 않았다. `workflow_artifact_flow.py`의 명시적 계약("Design에는
Context가 섞이지 않은 원본 Issue를 그대로 넘긴다")과 일치하는
관찰이다.

### 부수 관찰 — 모델의 일반 엔지니어링 판단과 저장소 컨벤션의 우연한 일치

`planning`/`design`이 "don't validate conditions that can't happen"
류의 판단을 자체적으로 언급했는데, 이는 이 저장소의 `CLAUDE.md`를
인용한 것이 아니라(`cwd`가 이미 격리되어 있어 이 저장소의 `CLAUDE.md`를
읽을 수 없다, MVP-0028) Claude 자체의 일반 엔지니어링 원칙과
우연히 일치한 것으로 보인다 — Issue 설명이나 지시 문장 어디에도 그런
표현이 없었다. 새로운 문제는 아니며, 참고로만 기록한다.

## 왜 수정하지 않았는가

3단계 모두 의미 있고 일관된 산출물을 냈고, Design→Implementation
Context 격리 계약도 실측으로 확인됐다 — 고칠 문제가 없었다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `run_issue_to_implementation(CODE_ISSUE)`
  전체(3단계)를 실제 `claude -p` 호출로 1회 실행(mock 없음).
- 문제가 없는데 있다고 표현했는가 — **아니오**.
- MVP-0031의 결론이 이 별도 경로에서도 성립하는지 확인했는가 —
  **예**, 같은 코드성 Issue 유형으로 별도 workflow 파일의 정상 동작을
  재확인했다.
