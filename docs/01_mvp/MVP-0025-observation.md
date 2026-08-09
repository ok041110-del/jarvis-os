# MVP-0025 Observation

## 목적

MVP-0001 Exit Criteria("입력 코드가 주어지면, 수동 개입 없이 Code
Review 결과와 Test Case 제안이 순서대로 반환된다")를 `run_mvp_0001()`로
실제 Engine을 호출해 직접 실행·검증하던 중, `qa_agent_test_execution`이
실제로는 테스트 케이스를 제안하지 않고 코드를 다시 리뷰하거나(재현
1), 입력을 애매한 요청으로 오인해 명확화를 요구하는(재현 2) False
Negative를 실제 실행으로 확인했다. 최소 수정으로 해소했다.

## 발견한 문제 (실제 Engine 실행으로 확인)

`agents.py`의 5개 Agent 함수 중 `requirements_agent_requirement_analysis`
/ `design_agent_design` / `backend_agent_code_generation` 3개는 이미
"리터럴 마커(`REQUIREMENT_ANALYSIS:` 등) 단독으로는 실제 Engine이
Capability 의도를 놓친다"는 이유로 지시 문장이 붙어 있었다(각 함수
docstring, 2026-08-08 관찰 기록). 그러나 `backend_agent_code_review`와
`qa_agent_test_execution`은 지시 문장 없이 `CODE_REVIEW:`/
`TEST_EXECUTION:` 리터럴 마커만 붙여 호출하고 있었다 — 동일한 문제가
남아 있을 가능성을 실제 실행으로 재현했다.

### 재현 1 — `test_mvp_0001.py`의 `SAMPLE_CODE`로 `run_mvp_0001()` 직접 실행

```
code_review: (정상 — bare except, mutable default 지적)
test_execution: 코드를 다시 리뷰함("Bugs/risks, ranked" + fix 제안) —
  테스트 케이스 목록이 아니다.
```

### 재현 2 — `workflow_hello_sdlc.run_hello_sdlc()`를 새 Issue로 직접 실행

Issue: "Add input validation to divide()" (b==0일 때 ValueError를
던지도록 요구).

```
test_execution: "I see a pasted block labeled TEST_EXECUTION ... but
there's no actual request attached ... Could you clarify what you'd
like me to do?" — 테스트 케이스 대신 명확화 요청을 반환.
```

두 재현 모두 `payload`(code + `---REVIEW---` + review)는 정상적으로
구성되어 있었다 — 문제는 payload 내용이 아니라, 그 payload가 무엇을
위한 것인지 알려주는 지시 문장이 없다는 점이었다. 이는 다른 3개
Agent에서 이미 한 번 관찰·해소된 것과 동일한 종류의 문제다.

## 변경 파일

- `development-hq/mvp/agents.py`
  - `backend_agent_code_review(code)` — `CODE_REVIEW:{code}`를
    `CODE_REVIEW:{instruction}\n\n{code}`로 바꿨다. 지시 문장:
    "Review the following code and describe issues in prose (bugs,
    risks, style) — do not rewrite or restate the code as your
    answer."
  - `qa_agent_test_execution(code, review)` — `TEST_EXECUTION:{payload}`를
    `TEST_EXECUTION:{instruction}\n\n{payload}`로 바꿨다. 지시 문장:
    "Based on the following code and its review, propose a list of
    test cases to add — do not review the code again."
  - 다른 3개 Agent 함수, `AGENT_CAPABILITY_MAP`,
    `HELLO_SDLC_CAPABILITY_MAP`은 손대지 않았다. `engine.py`(Engine
    호출 함수 자체), `workflow*.py`(Task 순서 하드코딩)도 손대지
    않았다 — 이번 변경은 두 함수가 Engine에 넘기는 prompt 문자열
    내용뿐이다. 새 Capability/Agent/Output Contract를 만들지 않았다.

## 관찰 결과 (실제 재실행으로 확인)

### 재현 1 재실행 — `run_mvp_0001(SAMPLE_CODE)`

```
code_review: 정상 (변경 전과 동일한 종류의 지적 — bare except, mutable default)
test_execution: "## Proposed Test Cases for `add`" — happy path/mutable
  default/type mismatch 범주로 나뉜 9개 이상의 구체적 테스트 케이스
  목록을 반환. 코드 재리뷰가 아니다.
```

### Regression 확인

- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 모두
  통과 (`code_review`/`test_execution` 두 Task가 순서대로 반환되는지,
  review 내용이 test_execution prompt에 포함되는지, `AGENT_CAPABILITY_MAP`이
  정확히 2개 항목인지 — 세 assertion 모두 실제 Engine 호출로 확인됨).

### 범위 밖으로 남겨둔 추가 관찰 (수정하지 않음)

재현 2를 이번 수정 이후 다시 실행했을 때, `test_execution` 자체는
더 이상 명확화를 요구하지 않았지만, 그 앞 단계인 `implementation`
(`backend_agent_code_generation`)이 이번 실행에서는 실제 코드 대신
"design을 받지 못해 구현할 수 없다"는 취지의 placeholder 텍스트를
반환했고, 그 결과 `code_review`/`test_execution`이 placeholder를
그대로 리뷰하는 연쇄가 관찰됐다. 이는 이번 수정(`code_review`/
`test_execution`의 지시 문장 누락)과는 다른 원인이며, 같은 Issue로
반복 실행했을 때 항상 재현되는지 아직 확인하지 않았다(실제 Engine의
비결정성 가능성 포함) — 새로운 별도 관찰 대상으로만 기록하고, 이번
MVP 범위에서 추가 수정은 하지 않는다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Capability/Agent/Contract를 만들었는가 — **아니오**. 기존
  Agent 함수 2개의 prompt 문자열만 바꿨다 — 나머지 3개 Agent가 이미
  쓰던 것과 같은 패턴(지시 문장 추가)을 그대로 적용했을 뿐이다.
- 실제 Engine으로 확인했는가 — **예**. 수정 전/후 모두 실제 `claude
  -p` 호출로 재현·검증했다(mock 없음).
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**. 수정 범위 밖의 별도
  현상(implementation 단계 placeholder)을 발견한 그대로 기록했고,
  이번 수정이 그 현상을 고쳤다고 주장하지 않았다.
