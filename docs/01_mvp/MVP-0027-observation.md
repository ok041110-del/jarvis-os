# MVP-0027 Observation

## 목적

`workflow_0002.py`(MVP-0002, RT-0001 Task Dispatcher Trigger 관찰용 1개
분기: "code_review 결과에 이슈가 없으면 test_execution을 건너뛴다")를
실제 Engine으로 직접 실행해, 그 분기가 실제로 동작하는지 검증했다.
동작하지 않음을 확인하고 최소 수정으로 해소했다.

## 발견한 문제 (실제 Engine 실행으로 확인)

`workflow_0002.py`의 분기 판단은 `NO_ISSUE_MARKER = "뚜렷한 이슈가
발견되지 않았습니다."`(rule-based Engine 시절 `_review_python_code`가
이슈 없을 때 반환하던 고정 문자열)를 `review` 안에서 찾는 방식이었다.
ENGINE-CONNECT-0001 이후 `call_engine()`은 실제 Claude CLI를 호출하며
(MVP-0023~0026에서 반복 확인된 사실과 동일), 실제 Engine은 이 한국어
고정 문자열을 그대로 반환하지 않는다.

명백히 이슈가 없는 코드로 직접 실행해 재현했다:

```python
CLEAN_CODE = '''def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''
run_mvp_0002(CLEAN_CODE)
```

`code_review`는 실제로 "No bugs here ... Nothing else stands out; it's
a correct, minimal implementation for its apparent scope."처럼 이슈
없음을 서술했지만, `NO_ISSUE_MARKER`가 그 안에 없으므로 분기는 항상
`test_execution`을 실행하는 쪽으로 빠졌다 — MVP-0002가 명시한 "이슈가
없으면 건너뛴다"는 계약이 실제로는 한 번도 발동하지 못하고 있었다.

## 변경 파일

- `development-hq/mvp/agents.py`
  - `NO_ISSUES_MARKER = "NO_ISSUES_FOUND"` (신규 모듈 상수).
  - `backend_agent_code_review()`의 지시 문장에 "이슈가 없을 때만
    응답 마지막 줄에 정확히 `NO_ISSUES_FOUND`를 적으라"는 한 문장을
    추가했다. 특정 응답 구조(섹션/헤더 전체)를 요구하는 것이
    아니라, MVP-0002가 이미 필요로 하던 단일 신호 하나만 명시적으로
    요청한다 — MVP-0025가 이미 쓴 "지시 문장 보강" 패턴과 같은
    종류다.
- `development-hq/mvp/workflow_0002.py`
  - `NO_ISSUE_MARKER`(로컬 상수, 고정 한국어 문자열) 정의를
    제거하고, `agents.NO_ISSUES_MARKER`를 import해서 그대로
    사용하도록 바꿨다. 분기 로직(`if ... in review`) 자체는
    바꾸지 않았다 — 비교 대상 마커만 바뀌었다.

## 관찰 결과 (실제 재실행으로 확인)

### 분기가 실제로 동작하는가?

**예.**

- 이슈 없는 코드(`CLEAN_CODE`) — `code_review`가 마지막 줄에
  `NO_ISSUES_FOUND`를 포함해 반환했고, `test_execution`은
  `"(생략됨: code_review에서 이슈가 발견되지 않아 test_execution을
  건너뜀)"`로 실제로 건너뛰었다(`qa_agent_test_execution` 호출
  없음).
- 이슈 있는 코드(bare except + mutable default) — `code_review`에
  `NO_ISSUES_FOUND`가 없었고, `test_execution`이 실제로 실행되어
  구체적인 테스트 케이스 목록을 반환했다.

두 경우 모두 실제 `claude -p` 호출로 확인했다(mock 없음).

### Regression 확인

- `development-hq/mvp/tests/test_mvp_0001.py` 3건 모두 통과. 이
  테스트는 `run_mvp_0001`(`workflow.py`, 분기 없음)만 검증하므로
  `backend_agent_code_review`의 지시 문장 변경 영향을 받지 않는다 —
  `SAMPLE_CODE`는 실제 이슈(bare except, mutable default)를 포함해
  `NO_ISSUES_FOUND` 마커가 나타나지 않을 입력이고, 기존 assertion
  (review truthy, "except" 포함 등)도 마커 추가와 무관하다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- `workflow.py`(MVP-0001, 분기 없음) — 손대지 않았다. MVP-0002
  Observation의 기존 원칙("MVP-0001의 workflow.py는 수정하지
  않는다")을 그대로 지켰다.
- `qa_agent_test_execution`이나 다른 3개 Agent 함수의 지시 문장 —
  손대지 않았다.
- `NO_ISSUES_FOUND`가 아닌 다른 형태의 구조화된 출력(JSON, 헤더
  등) 요구 — 하지 않았다. MVP-0002가 필요로 하는 신호 하나만
  최소로 추가했다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Capability/Agent/Engine을 추가했는가 — **아니오**. 기존
  `backend_agent_code_review`의 prompt 문자열과, 기존 분기 로직이
  참조하는 상수 값만 바꿨다.
- 실제 Engine으로 확인했는가 — **예**. 수정 전(재현)·후(검증) 모두
  실제 `claude -p` 호출(mock 없음).
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
