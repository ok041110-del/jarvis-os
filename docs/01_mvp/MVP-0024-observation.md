# MVP-0024 Observation

## 목적

`_review_python_code`(MVP-0005~0011)의 나머지 두 규칙(bare except,
mutable default)도 MVP-0016(line-length)/MVP-0023(TODO)와 같은
종류의 False Positive를 갖고 있음을 확인하고 최소 수정으로 해소했다.
새 메커니즘 없이 MVP-0016의 `_line_is_inside_triple_quoted_string()`을
그대로 재사용했다. 이로써 `_review_python_code`의 5개 규칙 중 코드
문자열 전체를 검사하던 4개(line-length/TODO/bare except/mutable
default) 모두 docstring 내부를 제외하게 되었다. docstring 존재
여부(`'"""' not in code`) 규칙은 애초에 docstring 유무 자체를 묻는
것이라 이 문제와 무관하다.

## 발견한 문제 (실제 실행으로 확인)

```python
code1 = '''def f():
    """
    Reference: 예전 코드는 except: pass 형태의 bare except를 썼다.
    """
    return 1
'''
_review_python_code(code1)
# → "- bare except 절이 있습니다..." (틀림 — docstring 안의 인용
#   텍스트일 뿐 실제 bare except가 아니다)

code2 = '''def f():
    """
    Reference: 매개변수 기본값을 def g(a=[]): 처럼 쓰면 안 된다.
    """
    return 1
'''
_review_python_code(code2)
# → "- mutable default argument(빈 리스트)가 있습니다..." (틀림 —
#   docstring 안의 인용 텍스트일 뿐 실제 mutable default가 아니다)
```

## 변경 파일

- `development-hq/mvp/engine.py`
  - bare except 검사: `"except:" in code or "except :" in code`
    (코드 전체 문자열 검사)를 줄 단위 검사로 바꾸고 docstring 내부
    줄을 제외했다. **`"def " in code` 조건은 추가하지 않았다** —
    원래 이 규칙은 `def` 유무와 무관하게(module-level bare except도)
    적용됐으므로, docstring 제외만 추가하고 그 조건은 그대로
    유지했다.
  - mutable default 검사: `"def " in code and "=[]" in
    code.replace(" ", "")`(코드 전체에서 공백을 지운 뒤 검사)를 줄
    단위 검사(각 줄에서 공백을 지운 뒤 검사)로 바꾸고 docstring 내부
    줄을 제외했다. `"def " in code` 조건은 원래대로 유지했다.
  - TODO/line-length와 동일하게 새 헬퍼를 추가하지 않고
    `_line_is_inside_triple_quoted_string()`을 재사용했다.

## 관찰 결과

### False Positive가 해소되는가?

**예.** 위 두 재현 케이스 모두 이제 "뚜렷한 이슈가 발견되지
않았습니다. 전체적으로 양호합니다"를 반환한다.

### 실제 위반은 여전히 탐지되는가?

**예.** docstring 밖의 실제 `except:`(try/except 안)와 실제
`def f(a=[]):`(함수 시그니처의 mutable default)는 변경 후에도
그대로 탐지된다(직접 실행으로 확인).

### `def` 없는 module-level bare except도 여전히 탐지되는가?

**예.** bare except 규칙은 원래 `"def "` 유무와 무관하게 적용되던
규칙이므로, docstring 제외만 추가하고 그 조건은 손대지 않았다.
`def` 없이 `try/except:`만 있는 코드도 변경 후 그대로 탐지됨을 직접
실행으로 확인했다.

### Regression 확인

- `SAMPLE_CODE`(bare except, mutable default, docstring 없음)에 대한
  기존 3개 Finding — 변경 전과 동일하게 그대로 보고됨.
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`CODE_REVIEW:def
add(a,b): return a+b`). MVP-0014~0023에서 이미 기록한 것과 동일하게,
실제 Claude CLI가 자유 형식 응답을 반환하고 `_review_python_code()`를
포함한 rule-based Capability Logic 경로는 호출되지 않는다. 이번
변경으로 새로 달라진 사실은 없다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- docstring 존재 여부 규칙(`'"""' not in code and "'''" not in
  code`) 변경 — 하지 않았다. 이 규칙은 docstring 유무 자체를 묻는
  것이라 "docstring 안의 인용 텍스트" 문제와 무관하다.
- 실제 Python 파서(AST/tokenize) 기반 판정으로 교체 — 하지 않았다.
  MVP-0016/0023과 동일한 근사치 스캐너를 그대로 재사용했다.
- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract나 새 메커니즘을 만들었는가 — **아니오**. MVP-0016이
  만든 `_line_is_inside_triple_quoted_string()`을 그대로 재사용했다.
- 원래 규칙의 적용 조건(`"def "` 유무)을 바꿨는가 — **아니오**.
  bare except는 원래대로 `def` 무관, mutable default는 원래대로
  `def` 필요 — docstring 제외만 추가했다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
