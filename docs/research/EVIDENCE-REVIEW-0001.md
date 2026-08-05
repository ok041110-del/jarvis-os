# Evidence Review 0001

## 문서 성격

이 문서는 **Research 문서다. Governance 문서가 아니다.**

Architecture Decision을 포함하지 않는다. 결론을 내리지 않는다. 새 코드,
새 Capability, 새 Dispatcher, 새 Runtime, 새 Stage Runner, 새
Pipeline을 구현하지 않는다. RFC/ADC/ADR/RT를 수정하지 않는다. 이
문서는 MVP-0005~0008 Observation 4건을 읽고 그 내용을 구조화해
정리하는 것만을 목적으로 한다.

## 범위

- `docs/01_mvp/MVP-0005-observation.md`
- `docs/01_mvp/MVP-0006-observation.md`
- `docs/01_mvp/MVP-0007-observation.md`
- `docs/01_mvp/MVP-0008-observation.md`

---

# Evidence Summary

## MVP-0005: Project Intelligence 최소 구현

- `collect_relevant_context(issue)`가 신규 작성되었다. Project 내 8개
  카테고리(source_code, existing_workflow, mvp/obs/rfc/adc/adr/rt
  documents)와 directory_structure 1개를 규칙 기반(키워드 겹침)으로
  수집하는 일반 함수 하나다. 어떤 Capability-Agent 매핑에도 등록되지
  않았다.
- `run_issue_to_planning(issue)`가 이 함수를 호출한 뒤 결과를 Issue의
  `description`에 문자열로 덧붙여 기존 Planning 함수
  (`requirements_agent_requirement_analysis`)에 그대로 전달했다. 함수
  시그니처는 바뀌지 않았다.
- 관련 Issue(Task Dispatcher)와 무관한 Issue(reverse string)를 각각
  실행해, 카테고리별로 실제로 다른 파일 집합이 반환됨을 확인했다.
- 구현 중 실제 토큰화 버그(`\w+`가 한글 조사를 라틴 단어에 붙임)를
  발견하고 수정했다 — Architecture Decision이 아니라 코드 결함
  수정으로 기록됨.
- `collect_relevant_context()`가 기존 7개 Capability 중 어느 것과도
  정확히 대응하지 않는다는 사실을 관찰만 하고 판단하지 않았다(ADC-0003
  판단 2, Capability Catalog 확장 Defer와 연결 가능하다고만 기록).

## MVP-0006: Project Intelligence를 Design Stage까지 전달

- `run_issue_to_design(issue)`가 신규 작성되어 `collect_relevant_context()`
  를 1회만 호출하고, 그 결과를 Planning과 Design 양쪽 호출에 재사용했다.
- 재사용이 실제로 일어난 경로가 예상과 달랐다: `design_agent_design(issue, requirement)`
  은 인자로 받은 `issue`의 `title`만 사용하고 `description`은 읽지
  않는다. 따라서 Context가 담긴 `enriched_issue`를 Design에 그대로
  넘겨도 그 자체로는 효과가 없었다 — Context가 Design 출력에 도달한
  유일한 경로는 이미 Context가 섞여 있는 `requirement` 문자열이었다.
- 직접 비교 실험(`enriched_issue` vs 원본 `issue`, 동일한 `requirement`
  고정)으로 두 Design 출력이 완전히 동일함을 확인했다.

## MVP-0007: Artifact Flow 관찰 (PI는 Planning에서만 사용)

- `run_issue_to_implementation(issue)`가 신규 작성되어 Planning ->
  Design -> Implementation을 통과시켰다. Design에는 Context가 섞이지
  않은 원본 Issue를 넘겼다(MVP-0006과 달리).
- `requirement in design`, `design in implementation`이 실제 실행에서
  모두 True로 확인되었다 — 상위 Stage의 산출물 전체가 하위 Stage의
  산출물에 부분 문자열로 그대로 포함된다(`engine.py`의
  `_design_from_requirement`, `_generate_code`가 상위 텍스트를 그대로
  이어붙이기 때문).
- Design에 원본(Context 없는) `issue`를 넘겼음에도, `[Relevant
  Context]` 절이 `design`과 `implementation` 텍스트 양쪽에 그대로
  나타남을 확인했다. 원인은 워크플로우가 인자로 무엇을 넘기는가가
  아니라, 각 Stage 함수가 상위 Artifact 텍스트 전체를 verbatim으로
  이어붙이는 `engine.py`의 동작이었다.
- 각 Stage가 상위 Artifact에서 구조적으로 실제 사용하는 부분은
  `title`(→slug) 하나뿐이었고, 나머지 텍스트는 파싱 없이 그대로
  이어붙여졌다는 사실도 함께 관찰되었다.

## MVP-0008: Development HQ가 실제 Issue 하나를 처리

- 토이 예시가 아니라 이 저장소 자신의 실제 산출물(MVP-0007에서
  발견된 문제를 다루는 "Project Intelligence 개선" Issue)을 입력으로
  사용했다.
- `run_pipeline(issue)`가 Planning -> Design -> Implementation ->
  Validation(code_review -> test_execution) 4단계를 유지했다. PI는
  Planning에서만 사용했다(MVP-0007과 동일한 방식).
- MVP-0007에서 관찰된 verbatim 이어붙이기가 재현되었다(Requirement가
  Design에, Design이 Implementation에 그대로 포함).
- `code_review`가 반환한 findings 8건 중 7건이 실제 코드 문제가 아니라
  docstring에 새어들어간 Context 목록 줄이 100자를 넘겨서 발생한
  것이었다 — Information Flow가 Validation 결과 자체를 실측으로
  왜곡시키는 사례가 처음으로 관찰되었다.
- Validation 두 함수(`code_review`, `test_execution`)는 Issue 원문이나
  `context` dict를 인자로 전혀 받지 않는다는 사실이 확인되었다 — 이
  시점부터 유일한 정보 전달 경로는 누적된 `code` 문자열 자체였다.

---

# Repeated Patterns

아래는 MVP-0005~0008 중 2회 이상 반복적으로 관찰된 사실만 정리한다.
판단은 하지 않는다.

## Context 전달 방식

- MVP-0005, 0006, 0007, 0008 네 건 모두 동일한 방식을 사용했다:
  `collect_relevant_context()` 결과를 별도 인자나 새 필드로 전달하지
  않고, 기존 `issue["description"]` 문자열에 텍스트로 덧붙인다. 함수
  시그니처는 네 건 모두 변경되지 않았다.
- MVP-0006, 0007, 0008 세 건 모두에서 `collect_relevant_context()`는
  정확히 1회만 호출되었다(호출 위치는 항상 Planning 직전).

## Artifact 전달 방식

- MVP-0006, 0007, 0008 세 건 모두에서 하위 Stage 함수가 상위 Stage
  산출물 텍스트 전체를 요약·파싱 없이 그대로 이어붙이는 동작이
  확인되었다(`_design_from_requirement`, `_generate_code`).
- MVP-0007, 0008 두 건 모두에서 `requirement in design`,
  `design in implementation`이 True로 확인되었다(직접 substring
  검증).
- MVP-0006, 0007, 0008 세 건 모두에서 각 Stage 함수가 상위 Artifact
  에서 구조적으로 실제 사용하는 부분은 `title`(또는 그로부터 만든
  slug) 하나뿐이라는 사실이 반복 확인되었다.

## Information Flow (의도한 경로와 실제 도달 경로의 불일치)

- MVP-0006, 0007 두 건 모두에서, 워크플로우가 어떤 Stage 함수에
  Context를 인자로 넘기는지와, Context가 실제로 그 Stage의 산출물에
  도달하는지가 서로 다른 질문이었다는 사실이 반복 확인되었다.
  - MVP-0006: `enriched_issue`를 Design에 넘겼지만 Design이
    `description`을 읽지 않아 인자 전달 자체는 무의미했고, 대신
    `requirement` 문자열을 통해 Context가 전달되었다.
  - MVP-0007: 원본 `issue`(Context 없음)를 Design에 넘겼음에도
    `requirement` 문자열에 이미 섞여 있던 Context가 Design과
    Implementation까지 도달했다.

## Validation 입력 구조

- MVP-0008에서만 Validation까지 실행되었으므로 반복 관찰은 아니지만,
  MVP-0004(`workflow_hello_sdlc.py`, 이번 범위 밖)에서 이미 확립된
  것과 동일한 구조 — `backend_agent_code_review(code)`와
  `qa_agent_test_execution(code, review)`는 Issue나 context dict를
  인자로 받지 않는다 — 가 MVP-0008에서도 그대로 재확인되었다.

## Task Dispatcher 패턴 재사용 (하드코딩된 순차 호출)

- MVP-0005, 0006, 0007, 0008 네 건 모두 새로운 Dispatcher/Runtime/
  Stage Runner/Pipeline Runner를 만들지 않고, 기존과 동일한
  하드코딩된 순차 함수 호출 체인을 각각 새 워크플로우 파일/함수로
  반복 추가했다(`workflow_project_intelligence.py`의 2개 함수,
  `workflow_artifact_flow.py`, `workflow_0008.py`).

---

# Non-Repeated Findings

한 번만 나타난 Observation.

- MVP-0005: 키워드 토큰화 버그(한글 조사가 라틴 단어에 붙는 문제)를
  구현 중 발견하고 수정한 것 — 다른 3개 MVP에서는 유사한 코드 결함
  발견·수정 사례가 보고되지 않았다.
- MVP-0006: `design_agent_design`이 `issue['description']`을 전혀
  읽지 않는다는 사실 자체는 MVP-0006에서 처음 발견되었다(이후
  MVP-0007/0008에서는 이 사실을 전제로 원본 issue를 Design에
  넘기는 설계를 그대로 따랐을 뿐, 새로 발견한 것은 아니다).
- MVP-0007: 무관한 Issue(reverse string)에 대해서도 동일한 verbatim
  이어붙이기 패턴이 재현되는지 별도로 검증한 것 — MVP-0008은 실제
  Issue 1건만 실행했다.
- MVP-0008: `code_review`의 findings 8건 중 7건이 실제 코드 문제가
  아니라 이어붙은 Context 텍스트의 줄 길이 때문에 발생했다는 관찰 —
  Validation 결과가 Information Flow에 의해 실측으로 왜곡된 유일한
  사례다.
- MVP-0008: 이번 MVP에서 사용한 Issue 자체가 이전 MVP(MVP-0007)의
  Observation에서 나온 실제 발견이라는 점 — MVP-0005~0007 중에는
  이런 자기참조적 Issue 사용 사례가 없었다.

---

# Existing Governance Mapping

각 Observation을 기존 RT/RFC/ADC 문서와 연결만 한다. 새 Governance를
만들지 않는다.

| Observation | 연결되는 기존 문서 | 연결 근거 |
|---|---|---|
| Context 전달 방식(issue["description"]에 텍스트로 덧붙임, 별도 저장소·필드 없음) | RT-0001 Candidate 4(Context 전달 메커니즘), ADC-0001 Candidate 4 | RT-0001은 "Context 전달 경로 ≥ 2"를 Re-evaluation Trigger로 정의했다. MVP-0005~0008은 모두 지역 변수/문자열 덧붙이기라는 동일한 단일 경로만 사용했으므로, 이 Trigger 자체가 발동했는지는 이 문서가 판단하지 않는다. |
| Task Dispatcher 패턴이 워크플로우 파일마다 반복 추가됨(MVP-0005~0008에서 5개 이상의 새 하드코딩된 함수) | RT-0001 Candidate 1(Task Dispatcher), RFC-0004, ADC-0004 | RT-0001 Candidate 1의 Trigger는 "하드코딩된 Task 호출 체인 수 ≥ 2"다. ADC-0004는 이미 MVP-0001/0002/0004의 3개 체인을 근거로 Task Dispatcher 재판단(Keep)을 다뤘다. MVP-0005~0008이 추가한 체인 수가 이 재판단에 새로운 근거가 되는지는 이 문서가 판단하지 않는다. |
| `collect_relevant_context()`가 기존 7개 Capability 중 어느 것과도 대응하지 않음 | ADC-0003 판단 2(Capability Catalog 확장, Defer) | ADC-0003 판단 2는 "신규 Capability 후보가 어떤 MVP에서도 실제로 실행·관찰된 적이 없다"는 이유로 Defer했다. MVP-0005~0008은 `collect_relevant_context()`를 4개 MVP에 걸쳐 반복 실행하고도 여전히 Capability로 등록하지 않았다는 사실만 연결한다. |
| Design/Implementation이 상위 Artifact를 verbatim으로 이어붙임(Artifact Flow) | 해당 없음 | MVP-0005~0008 범위 안에서는 이 관찰과 직접 연결되는 기존 RT/RFC/ADC 문서를 찾지 못했다. RFC-0001·RFC-0004는 Task Dispatcher/Engine Gateway/Context 전달 메커니즘을 다루지만, "Stage 간 Artifact 내용이 어떻게 합성되는가"를 별도로 다룬 문서는 없다. |
| Validation이 Issue/context dict를 인자로 받지 않음 | 해당 없음 | 위와 동일한 이유로, 이 관찰과 직접 연결되는 기존 RT/RFC/ADC 문서를 찾지 못했다. |

---

# Candidate Topics

향후 RFC 후보가 될 수 있는 주제를 나열만 한다. RFC를 만들지 않는다.
승격 여부를 판단하지 않는다.

- Task Dispatcher (후보)
- Capability Catalog (후보)
- Artifact Flow (후보)
- Project Intelligence (후보)
- Context 전달 메커니즘 (후보)

---

# Unknowns

현재 Observation만으로는 판단할 수 없는 것.

- Artifact Flow(상위 Stage 산출물이 하위 Stage 산출물에 verbatim으로
  포함되는 현상)가 Development HQ Boundary에 해당하는 사안인지, 아니면
  현재 `engine.py` 구현의 세부사항(규칙 기반 응답이 입력 텍스트를
  그대로 에코하는 방식)에 불과한지 판단 불가.
- `collect_relevant_context()`가 4개 MVP에 걸쳐 반복 실행된 사실이
  ADC-0003 판단 2(Capability Catalog 확장, Defer)의 재판단 조건("MVP가
  실행되어 기존 Capability로 부족하다는 사실이 실제로 관찰된 뒤")을
  충족했는지 판단 불가 — 이 문서는 사실을 연결만 했을 뿐, 조건 충족
  여부는 판단하지 않는다.
- MVP-0005~0008에서 추가된 하드코딩된 순차 호출 체인의 수가 RT-0001
  Candidate 1의 "하드코딩된 Task 호출 체인 수 ≥ 2" Trigger를 (ADC-0004
  이후 시점 기준으로) 새로 발동시키는지 판단 불가.
- Validation 함수가 Issue/context를 인자로 받지 않는 구조가 의도된
  Boundary(Validation은 Code만 보아야 한다)인지, 아니면 단순히 아직
  다뤄지지 않은 설계 공백인지 판단 불가.
- MVP-0008에서 관찰된 "Information Flow가 Validation 결과를 실측으로
  왜곡시킨 사례"(line-length findings 7건)가 일반적으로 재현되는
  패턴인지, 이번 Issue의 우연한 텍스트 길이 때문에 나타난 1회성
  현상인지 판단 불가 — 이번 문서 범위(MVP-0005~0008) 안에서는 반복
  관찰이 없었다.
