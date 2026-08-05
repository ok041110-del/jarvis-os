# Observation: Development HQ DevKit Issue 0001

**Issue**: "Development HQ DevKit 최소 기능" (`runner.py`의
`DEVKIT_ISSUE_0001`)

**실행**: `projects/development-hq-devkit/runner.py`가 Development
HQ(`development-hq/mvp`)의 기존 함수만 그대로 호출해, 사람 개입 없이
Issue → Project Intelligence → Planning → Design → Validation을
끝까지 통과시켰다. Development HQ 코드는 한 줄도 수정하지 않았다.

> 이 문서는 사실만 기록한다. 판단, 설계, Architecture 제안, Decision을
> 하지 않는다.

## Success Criteria 충족 여부

**충족.** 예외 없이 Planning → Design → Validation까지 끝까지
실행되었고, `planning.md`, `design.md`, `validation.md` 세 Markdown
파일이 실제로 생성되었다.

## Project Intelligence 정확도

`collect_relevant_context()`가 8개 카테고리 중
`directory_structure`를 제외한 7개 전부에서 실제로 파일을 찾았다 —
`source_code`/`existing_workflow`에서는 최근 워크플로우 파일
(`workflow_0008.py`, `workflow_artifact_flow.py`,
`workflow_hello_sdlc.py`)이, `mvp_documents`/`obs_documents`/
`rfc_documents`/`adc_documents`/`adr_documents`/`rt_documents`에서는
Development HQ SDLC/Capability/Governance 관련 기존 문서가 반환되었다.
Issue 본문이 "Development HQ", "Capability", "Planning", "Design",
"Validation" 등 이 저장소에서 반복적으로 쓰인 용어를 그대로 포함하고
있었기 때문으로 보인다(원인 분석은 이 문서 범위 밖).

## Planning 품질

`requirements_agent_requirement_analysis()`의 반환값은 Issue의
`title`/`description`을 정해진 템플릿(`요구사항: '{title}' 기능이
필요하다. 상세: {description}`)에 그대로 끼워넣은 문자열이었다. Issue
본문에 없던 새로운 정보(예: 우선순위, 제약조건, 수용 기준)는 추가되지
않았다.

## Design 품질

`design_agent_design()`은 Issue `title`에서 만든 slug
(`development_hq_devkit`)로 함수 이름 하나를 제시하고, 나머지는
`requirement` 텍스트를 그대로 이어붙였다. Design 산출물에 실제 `def `
토큰(함수 정의)은 없었다 — `` `development_hq_devkit(*args, **kwargs)` ``
처럼 백틱으로 감싼 텍스트 언급만 있었다(직접 확인:
`"def " in design` == False).

## Validation 품질

- `backend_agent_code_review(design)`은 Design 텍스트(코드 아님)를
  그대로 입력받아 8건의 findings를 반환했다. 그중 1건("docstring이
  없습니다")은 Design 텍스트에 `"""`/`'''`가 없다는 규칙이 문자 그대로
  적용된 것이었고, 나머지 7건은 모두 "N번째 줄이 100자를 초과합니다"
  였는데 실제로는 `[Relevant Context]` 절의 카테고리별 파일 목록 줄이
  100자를 넘긴 것이었다(MVP-0008에서 관찰된 패턴과 동일).
- `qa_agent_test_execution(design, review)`은 Design 텍스트에서
  `"def "`로 시작하는 줄을 찾지 못해(`func_names` 비어있음), 기본
  분기인 "스크립트 최상위 로직에 대한 실행 결과 검증" 1건만
  반환했다. `review`에 "bare except"나 "mutable default argument"
  문자열이 없었으므로 조건부 추가 케이스도 붙지 않았다.
- 두 Validation 함수 모두 원래 코드(Python source)를 입력으로
  가정하고 만들어졌다는 점은 바뀌지 않았다. 이번 실행은 Design
  텍스트(비-코드)를 그대로 입력했을 때 두 함수가 실제로 무엇을
  반환하는지를 관찰한 것이다.

## Artifact Flow

- `requirement in design` == True — Planning 산출물 전체가 Design
  산출물에 부분 문자열로 그대로 포함되었다.
- `design in` (validation 입력) — Validation의 두 함수 모두 `design`
  문자열 전체를 그대로 입력받았다(Implementation 단계가 없으므로
  Design이 Validation의 직접 입력이 되었다 — MVP-0007/0008의
  Requirement→Design→Implementation 경로와 한 단계 짧은 경로).

## Information Flow

- `[Relevant Context] in design` == True — Design에는 Context가 없는
  원본 `issue`를 인자로 넘겼음에도(`design_agent_design(issue, requirement)`),
  `requirement` 문자열에 이미 섞여 있던 Context가 Design 산출물에
  그대로 나타났다. MVP-0007/0008과 동일한 경로(인자 전달이 아니라
  상위 Artifact 텍스트를 통한 전달)였다.
- Validation 두 함수는 Issue나 `context` dict를 인자로 전혀 받지
  않았다 — Validation이 접근할 수 있는 유일한 정보는 `design` 문자열
  (그 안에 이미 섞여 있는 Context 포함)뿐이었다.

## 범위 밖 (이번 실행에서 하지 않은 것)

- Implementation(Code Generation). Design 산출물을 그대로 Validation에
  입력했다.
- Development HQ(`development-hq/mvp`, `development-hq/stages`) 코드
  수정. `runner.py`는 새 디렉토리(`projects/development-hq-devkit/`)에
  작성되었고, 기존 함수를 import해서 호출만 했다.
- 새 Capability, Task Dispatcher 일반화, Runtime, Stage Runner,
  Pipeline Runner 구현.
- Validation 품질 문제(코드 아닌 입력에 대한 오탐)를 고치는 것.
  사실만 기록했다.
