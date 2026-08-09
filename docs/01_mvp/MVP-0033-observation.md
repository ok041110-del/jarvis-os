# MVP-0033 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** —
2단계 모두 정상 동작해 수정할 문제가 없었다.

## 목적

`workflow_project_intelligence.py`(MVP-0006)의 `run_issue_to_design()`을
MVP-0028의 cwd 수정 이후 처음으로 실제 Engine으로 실행한다. 이 함수는
`run_issue_to_implementation`(MVP-0007, `workflow_artifact_flow.py`)과
달리 **같은 Relevant Context를 Design에도 그대로 재사용**하는 것을
관찰 대상으로 삼는다(MVP-0006의 명시적 목적: "`collect_relevant_context()`를
Stage마다 다시 호출하지 않고 재사용하는지를 관찰"). 코드성 Issue에서
이 별도 경로도 정상 동작하는지 확인한다.

## 실행 (실제 Engine, 56.5초)

MVP-0032와 동일한 `CODE_ISSUE`: "Add a clamp() helper function".

| Stage | 길이(문자) | 내용 |
|---|---|---|
| planning | 3350 | Goal/Scope/Risks — `clamp()` 요구사항을 정확히 서술, 중복 확인 필요성 언급 |
| design | 3353 | `max(low, min(value, high))` 형태의 구현 방식 채택, "ready to implement" 선언 |

## 관찰 결과

### 2단계 모두 정상 동작했는가?

**예.** MVP-0030에서 관찰된 코드 생성 거부/무의미한 산출물 현상은
나타나지 않았다 — Design이 "No open design questions — this is ready
to implement as a two-line pure function"로 명확히 마무리됐다.

### Relevant Context가 Design에도 재사용되는가?

**예, 그리고 의도된 대로다.** `design` 출력이 "the `development-hq/mvp`
source and workflow files named in context", "governance documents
(MVP/OBS/RFC/ADC/ADR/RT) listed as context"를 명시적으로 언급했다 —
`context`가 실제로 수집한 카테고리(source_code/mvp_documents/
rfc_documents 등)와 일치한다. 이는 버그가 아니라 `run_issue_to_design`
자신의 명시된 계약이다 — `workflow_artifact_flow.run_issue_to_implementation`
(MVP-0007, Design에는 원본 Issue만 전달)과 의도적으로 다른 동작이며,
MVP-0032가 확인한 "Design에 Context가 전달되지 않음"과 이번
"Design에 Context가 그대로 전달됨"이 서로 다른 함수의 서로 다른
계약이라는 점이 실측으로 대조됐다.

### 두 경로의 실제 산출물 품질 차이는?

두 실행(MVP-0032: Context 격리, MVP-0033: Context 공유) 모두 최종
Design은 실행 가능한 구현으로 수렴했다("ready to implement on your
go-ahead" vs "ready to implement as a two-line pure function") — 이번
Issue(작은 leaf 함수) 규모에서는 Context 공유 여부가 Design 품질에
관찰 가능한 차이를 만들지 않았다. 더 큰 Issue에서 차이가 나는지는
이번 관찰 범위 밖이다.

## 왜 수정하지 않았는가

2단계 모두 의미 있고 일관된 산출물을 냈고, 함수 자신이 명시한 계약
(Context 재사용)이 실측으로 그대로 확인됐다 — 고칠 문제가 없었다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `run_issue_to_design(CODE_ISSUE)`
  전체(2단계)를 실제 `claude -p` 호출로 1회 실행(mock 없음).
- Context 재사용을 버그로 오인해 "고칠 문제"로 보고했는가 —
  **아니오**. `workflow_project_intelligence.py`의 docstring에 명시된
  의도된 동작임을 확인하고 그렇게 기록했다.
