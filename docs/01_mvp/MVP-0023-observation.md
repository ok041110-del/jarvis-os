# MVP-0023 Observation

## 목적

`_review_python_code`(MVP-0005~0011)의 TODO 주석 탐지 규칙이,
MVP-0016이 line-length 규칙에서 이미 고친 것과 같은 종류의 False
Positive를 갖고 있음을 발견하고 최소 수정으로 해소했다. 새 메커니즘
없이 MVP-0016이 만든 `_line_is_inside_triple_quoted_string()`을
그대로 재사용했다.

## 발견한 문제 (실제 실행으로 확인)

```python
code = '''def f():
    """
    Reference: 이 프로젝트는 TODO 관리 도구를 사용한다.
    """
    return 1
'''
_review_python_code(code)
# → "- TODO 주석이 남아있습니다. 구현을 완료하거나 이슈로 분리하세요."
#   (틀림 — docstring 안에 인용된 참고 텍스트에 "TODO"라는 단어가
#   나타났을 뿐, 실제로 남겨진 TODO 주석이 아니다)
```

기존 검사는 `"def " in code and "TODO" in code`로 코드 전체 문자열에
대해 한 번만 검사했다 — TODO가 실제 주석(`# TODO: ...`)인지, 아니면
docstring에 그대로 인용된 참고 텍스트(MVP-0008/0011에서 관찰된 Artifact
누적 이어붙이기, MVP-0016이 line-length에서 이미 고친 것과 같은
자리)인지 구분하지 않았다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `_review_python_code()`의 TODO 검사를 코드 전체 문자열 검사에서
    줄 단위 검사로 바꾸고, MVP-0016의
    `_line_is_inside_triple_quoted_string()`으로 docstring 내부 줄을
    제외했다. 새 헬퍼를 추가하지 않고 기존 것을 그대로 재사용했다.
    ```python
    if "def " in code and any(
        "TODO" in line and not _line_is_inside_triple_quoted_string(lines, i)
        for i, line in enumerate(lines)
    ):
    ```
  - bare except/docstring 존재/line-length/mutable default 등 다른
    4개 규칙은 손대지 않았다.

## 관찰 결과

### False Positive가 해소되는가?

**예.** 위 재현 케이스가 이제 "뚜렷한 이슈가 발견되지 않았습니다.
전체적으로 양호합니다"를 반환한다.

### 실제 TODO 주석은 여전히 탐지되는가?

**예.** docstring 밖에 실제로 남겨진 `# TODO: implement this
properly` 주석은 변경 후에도 그대로 "TODO 주석이 남아있습니다"를
보고한다(직접 실행으로 확인).

### Regression 확인

- `SAMPLE_CODE`(bare except, mutable default, docstring 없음)에 대한
  기존 3개 Finding — 변경 전과 동일하게 그대로 보고됨.
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`CODE_REVIEW:def
add(a,b): return a+b`). MVP-0014~0021에서 이미 기록한 것과 동일하게,
실제 Claude CLI가 자유 형식 응답을 반환하고 `_review_python_code()`를
포함한 rule-based Capability Logic 경로는 호출되지 않는다. 이번
변경으로 새로 달라진 사실은 없다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- bare except/docstring 존재/line-length/mutable default 등
  TODO 이외의 규칙 변경 — 하지 않았다.
- 실제 Python 파서(AST/tokenize) 기반 주석·문자열 판정으로 교체 —
  하지 않았다. MVP-0016과 동일한 근사치 스캐너를 그대로 재사용했다.
- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract나 새 메커니즘을 만들었는가 — **아니오**. MVP-0016이
  만든 `_line_is_inside_triple_quoted_string()`을 그대로 재사용했다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
