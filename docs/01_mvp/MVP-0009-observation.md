# MVP-0009 Observation: Project Intelligence를 Context Bundle로 발전시킨다

## 목적

`collect_relevant_context()`(MVP-0005, 카테고리별 파일 목록 flat dict)를
확장해, Planning이 입력으로 사용할 수 있는 구조화된 Context
Bundle(`build_context_bundle()`)을 만든다. Capability 추가가 목적이
아니다 — Context 품질(flat 파일 목록 vs. 구조화된 8개 항목)이 Planning
결과에 어떤 영향을 주는지 관찰하는 것이 이번 MVP의 목적이다.
Architecture 판단은 하지 않는다.

## 변경 파일

- `development-hq/mvp/project_intelligence.py` — `build_context_bundle(issue) -> dict`
  추가. 기존 `collect_relevant_context()`는 수정하지 않고 그대로
  호출·재사용한다. 새 카테고리 디렉토리나 파일 검색 로직을 추가하지
  않는다 — 이미 수집된 8개 카테고리 파일 목록을 다음 8개 항목으로
  재배치·재분류할 뿐이다.
  - `issue`, `goal` — Issue 원본과 (없으면 `title`을 그대로 쓰는) Goal.
  - `relevant_documents` — `mvp_documents` + `rfc_documents`.
  - `relevant_code` — `source_code` + `existing_workflow`(중복 제거).
  - `relevant_observations` — `obs_documents`.
  - `relevant_decisions` — `adc_documents` + `adr_documents`.
  - `known_constraints` — `rt_documents`(Re-evaluation Trigger 문서는
    "언제 이 결정이 재검토되는가"를 정의하므로 그 자체가 제약 조건이다).
  - `open_questions` — `relevant_documents` + `relevant_decisions` +
    `relevant_observations`에 속한 파일들의 본문에서, "Open"(단어
    경계 매칭) 또는 "미해결"/"검토가 필요"가 포함된 줄만 규칙 기반으로
    추출(최대 5개).
- `development-hq/mvp/workflow_0009.py` (신규) —
  `_render_context_bundle(bundle) -> str`(8개 항목을 텍스트로 렌더링),
  `run_issue_to_planning_with_bundle(issue) -> dict`(Context Bundle을
  렌더링한 내용만 Planning에 전달), `run_comparison(issue) -> dict`
  (같은 Issue로 MVP-0005 방식과 MVP-0009 방식의 Planning을 각각 실행해
  나란히 반환). Planning Capability(`requirements_agent_requirement_analysis`,
  MVP-0004)와 `engine.py`의 내부 로직은 수정하지 않았다 — `engine.py`가
  이미 갖고 있던 계약(`description`에서 `[Relevant Context]` 마커 이후를
  통째로 `Reference Context`로 취급, MVP-0005)을 그대로 재사용하고, 그
  마커 뒤에 들어가는 텍스트의 **구조만** 바꿨다.
- 기존 파일(`agents.py`, `engine.py`, `workflow.py`, `workflow_0002.py`,
  `workflow_hello_sdlc.py`, `workflow_project_intelligence.py`,
  `workflow_artifact_flow.py`, `workflow_0008.py`)은 **수정하지
  않았다**. 새 Runtime, Task Dispatcher, Stage Runner, Pipeline Runner,
  Capability는 추가하지 않았다.

## 사용한 실제 Issue

MVP-0008과 동일한 Issue(`workflow_0008.REAL_ISSUE`, "Project
Intelligence 개선")를 그대로 재사용했다 — 같은 입력에 대해 Context만
바꿨을 때의 차이를 관찰하기 위함이다.

## 관찰 결과 (사실만 기록)

`run_comparison(REAL_ISSUE)`를 실제 실행한 결과:

- **Planning의 구조적 출력(Goal/Description/In Scope/Out of
  Scope/Acceptance Criteria (Draft))은 두 방식에서 완전히 동일했다.**
  `flat_context_planning`과 `context_bundle_planning`을 `## Reference
  Context`(구 `Relevant Context` 절) 앞부분까지 잘라 비교하면 문자열이
  정확히 일치했다(`==` True). `_analyze_requirement`(`engine.py`)는
  `description`을 `[Relevant Context]` 마커로 분리한 뒤 마커 앞부분
  (`narrative`)만 문장 분리·In/Out Scope 분류에 사용하고, 마커 뒤는
  파싱 없이 그대로 이어붙이기 때문이다 — Context Bundle이 아무리
  구조화되어도, Planning의 필수 섹션 판단 자체는 Context 품질의
  영향을 받지 않았다.
- **차이는 오직 `Reference Context` 절의 길이와 구조에서만 나타났다.**
  `flat_context_planning`은 2,181자, `context_bundle_planning`은
  2,726자였다. flat 방식은 8개 카테고리를 `카테고리명: 파일1, 파일2`
  형태로 한 줄씩만 나열했고, Bundle 방식은 `## Goal` / `## Relevant
  Documents` 등 8개 마크다운 섹션 제목과 각 파일을 `- ` 불릿으로
  나열해 사람이 읽을 때 어느 항목이 Known Constraints인지 Open
  Questions인지 구분 가능했다. flat 방식에는 이 구분이 없었다(카테고리
  이름이 `rt_documents`, `adc_documents`처럼 내부 변수명 그대로였다).
- **`open_questions` 추출 규칙에서 실제 오탐을 관찰하고 수정했다.**
  최초 구현은 "open"을 부분 문자열로 매칭해, `docs/02_rfc/RFC-0003-development-hq-sdlc-pivot.md`의
  "OpenHands", "OpenAI Agents SDK" 같은 고유명사가 "Open Decision"과
  동일하게 걸렸다 — 실제로 이 Issue에 대해 `open_questions`에
  "조사했다: OpenHands, Aider, LangGraph, CrewAI, OpenAI Agents SDK..."
  같은, 열린 질문이 아닌 문장이 포함되는 것을 실측으로 확인했다.
  `\bopen\b`(단어 경계) 매칭으로 바꾼 뒤 재실행하자, 같은 Issue에서
  `open_questions`는 `RFC-0004-task-dispatcher-runtime-boundary.md`의
  실제 "Open Decision"/"미해결" 문장 3건과 관련 없는 옛 Observation
  문서의 부분 인용 2건, 총 5건으로 바뀌었고 고유명사 오탐은
  사라졌다. 즉 이번 MVP 자체가 "Context 수집 규칙의 사소한 차이가
  Context 품질에 관찰 가능한 영향을 준다"는 사례 하나를 만들어냈다.
- **`known_constraints`는 이번 Issue에서 정확히 1건
  (`docs/governance/rt/RT-0001.md`)이었다.** `collect_relevant_context()`가
  이미 이 Issue에서 RT 카테고리로 찾아낸 파일이 하나뿐이었기 때문이며,
  Bundle 재구성 단계에서 추가로 걸러지거나 늘어나지 않았다(그대로
  전달).
- **`relevant_code`(source_code + existing_workflow 중복 제거)는 4개
  파일로, 원래 두 카테고리(source_code 3개, existing_workflow 3개,
  둘 다 `workflow_0008.py`를 포함해 합치면 5개 중 1개가 중복)를 합친
  뒤 중복을 제거한 결과와 정확히 일치했다 — `workflow_0008.py`가 두
  카테고리 모두에서 나타났지만 Bundle에는 한 번만 나타났다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새 Capability, Runtime, Task Dispatcher, Stage Runner, Pipeline
  Runner 추가.
- Planning/Design/Validation Capability(`agents.py`, `engine.py`)의
  내부 로직 수정. `[Relevant Context]` 마커 계약(MVP-0005)을 그대로
  재사용했다.
- Design/Implementation/Validation Stage에 Context Bundle을 전달하는
  것. 이번 MVP는 Planning 입력만 다룬다 — MVP-0007이 관찰한 "Context가
  하위 Stage로 의도치 않게 누적되는 문제"를 해결하는 것은 이번 범위가
  아니다.
- flat Context와 Context Bundle 중 어느 쪽이 "더 나은 Context"인지
  판단. 구조적 출력이 동일했다는 사실과, 사람이 읽을 때의 가독성
  차이, 그리고 추출 규칙의 오탐 사례만 기록했다.
- `open_questions`/`known_constraints` 추출 규칙을 일반화된 NLP
  파이프라인으로 발전시키는 것. 여전히 문자열 마커 매칭뿐이다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 — 회귀 없음.
- `run_comparison(REAL_ISSUE)`를 수동 실행해 위 관찰 내용(구조적 출력
  동일 여부, 길이 차이, `open_questions` 오탐 수정 전/후 차이)을 직접
  확인했다. 별도 자동화 테스트는 추가하지 않았다.
