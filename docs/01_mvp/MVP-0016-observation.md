# MVP-0016 Observation

## 목적

`MVP-0012-observation.md`의 "범위 밖"에 남아 있던 항목("Implementation
산출물의 docstring에 누적된 Context/Artifact 텍스트로 인한 line-length
finding 증가 현상(MVP-0008/0011에서 이미 관찰) 완화")을 기존
`_review_python_code` 범위 내 최소 수정으로 해소한다. 새
Architecture/Contract는 만들지 않는다.

## 발견한 문제 (실제 실행으로 재현)

MVP-0008/0011이 관찰한 축적 현상을 직접 재현했다. docstring 안에
참고 텍스트(Reference Context)가 그대로 인용되어 100자를 넘는 줄이
생기면, 기존 `_review_python_code`는 이를 실제 코드 줄과 구분하지
않고 각각 "N번째 줄이 100자를 초과합니다" Finding으로 보고했다:

```
- 3번째 줄이 100자를 초과합니다. 가독성을 위해 줄바꿈하세요.
- 4번째 줄이 100자를 초과합니다. 가독성을 위해 줄바꿈하세요.
```

두 줄 모두 docstring 안의 인용 텍스트였고 실제 코드 줄이 아니었다.
코드 가독성 규칙을 문서 인용문에 적용하는 것은 False Positive다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `_line_is_inside_triple_quoted_string(lines, index)` 추가 — 각 줄의
    `"""`/`'''` 등장 횟수 누적 홀짝으로 삼중 따옴표 문자열(주로
    docstring) 내부 여부를 판단하는 단순 스캐너.
  - `_review_python_code()`의 line-length 검사에 이 함수를 조건으로
    추가 — docstring 내부 줄은 100자 초과 여부와 무관하게 검사하지
    않는다. bare except/TODO/docstring 존재/mutable default 등 다른
    4개 규칙은 손대지 않았다.

## 관찰 결과

### False Positive가 해소되는가?

**예.** 위 재현 케이스가 이제 "뚜렷한 이슈가 발견되지 않았습니다.
전체적으로 양호합니다"를 반환한다(직접 실행으로 확인).

### 실제 코드 줄의 100자 규칙은 유지되는가?

**예.** docstring 밖의 실제 코드 줄(105자 함수 호출)은 변경 후에도
그대로 "3번째 줄이 100자를 초과합니다"를 보고한다(직접 실행으로 확인).
한 줄짜리 docstring(여는/닫는 삼중 따옴표가 같은 줄에 있는 경우)은
그 줄 자체는 여전히 검사 대상이다 — 스캐너가 "그 줄 이전"의 상태만
보므로, 열고 닫는 줄 자체는 100자 규칙에서 면제되지 않는다(의도된
동작: 한 줄짜리 지나치게 긴 docstring도 여전히 스타일 피드백을 받는다).

### Regression 확인

- `SAMPLE_CODE`(bare except, mutable default, docstring 없음)에 대한
  기존 3개 Finding(bare except/docstring 없음/mutable default) —
  변경 전과 동일하게 3건 그대로 보고됨(line-length는 원래도 해당 없는
  케이스).
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`CODE_REVIEW:def add(a,b):
return a+b`). MVP-0014/0015에서 이미 기록한 것과 동일하게, 실제
Claude CLI가 자유 형식 응답을 반환하고 `_review_python_code()`를
포함한 rule-based Validation Logic 경로는 호출되지 않는다. 이번
변경으로 새로 달라진 사실은 없다 — 기존에 기록된 pre-existing 상태를
재확인만 했다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.
- bare except/TODO/docstring 존재/mutable default 등 line-length 이외의
  규칙 변경 — 하지 않았다.
- 실제 Python 파서(AST) 기반 문자열 리터럴 판정으로 교체 — 하지
  않았다. 기존 `'"""' not in code` 등 문자열 매칭 스타일과 일치시킨
  근사치 스캐너를 그대로 썼다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. 기존 line-length 규칙의
  적용 범위만 좁혔다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
