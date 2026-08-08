# ENGINE-CONNECT-0001: `call_engine()` 실제 Engine 배선 — Runtime Evidence

이 문서는 사용 후기가 아니다. Implementation-First Mode(Evidence → Execute →
Observe → Judge) 지시에 따라 실제로 수행한 배선 실험 하나의 기록이다.
Execution Result Contract를 설계하지 않는다. Engine Gateway/Adapter를
만들지 않는다. Baseline을 수정하지 않는다. RFC/ADC/ADR을 작성하지 않는다.
**이 문서 자체가 코드 변경이 아니다** — 코드 변경은 격리된 worktree에만
존재했고 tracked 브랜치에는 반영되지 않았다.

## Experiment

- **대상**: `development-hq/mvp/engine.py`의 `call_engine(prompt: str) -> str`.
- **바뀐 것**: 함수 본문만. `_rule_based_response(prompt)` 호출을
  `subprocess.run(["claude", "-p", prompt, "--output-format", "text"], ...)`
  로 교체했다. 함수 시그니처, 파일 구조, 호출부(`agents.py`)는 그대로다.
  새 Gateway/Adapter/Registry/Scheduler/Runtime/Routing을 만들지 않았다 —
  여전히 단일 함수가 유일한 호출 지점이다.
- **격리**: `git worktree add`로 별도 worktree(`experiment-engine-connect-0001`
  브랜치, base `7982b85`)를 만들어 그 안에서만 수정했다. tracked 브랜치
  (`claude/jarvis-os-hq-mvp-0001-2fcqvd`)는 실험 전후 `git status --porcelain`
  모두 빈 출력 — 변경 없음.
- **실행 경로**: 별도 스크립트가 아니라 **기존 `run_mvp_0001()` 그대로** —
  `backend_agent_code_review()` → `qa_agent_test_execution()` → 내부에서
  `call_engine()` 2회 호출.

## Input (실제)

```python
SAMPLE_CODE = """
def add(a, b=[]):
    try:
        return a + b
    except:
        pass
"""
```

`call_engine()`에 전달된 실제 프롬프트는 기존 포맷 그대로다 —
`f"CODE_REVIEW:{code}"`, `f"TEST_EXECUTION:{code}\n---REVIEW---\n{review}"`.
새 프롬프트 포맷을 만들지 않았다.

## Output (실제 Raw Output)

`run_mvp_0001(SAMPLE_CODE)` 전체 소요 43.7초(2회 실제 Engine 호출 포함).

- `result["code_review"]`: 자연어 산문. Mutable default argument, bare
  `except`, silent failure, "Inconsistent contract" 4개 항목 + 수정 코드
  제안을 포함.
- `result["test_execution"]`: 자연어 산문. 동일 코드를 독립적으로 재검토한
  뒤 Bug/Fix 목록 + 수정 코드 제안.

두 반환값 모두 **기존 rule-based 응답과 형태가 다르다** — 항목이 고정된
불릿 목록(`- {finding}`)이 아니라 자유 서술형 산문 + 코드 블록이다. 이것이
관찰된 **Raw Output**이며, 이 문서는 이를 Execution Result Contract로
승격하지 않는다.

## Test 결과 (기존 `mvp/tests/test_mvp_0001.py`, worktree에서 실행)

```
mvp/tests/test_mvp_0001.py::test_returns_review_then_test_cases_without_manual_intervention PASSED
mvp/tests/test_mvp_0001.py::test_review_content_reaches_test_execution_as_context FAILED
mvp/tests/test_mvp_0001.py::test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope PASSED
```

**2 passed, 1 failed.**

| 테스트 | 결과 | 이유 |
|---|---|---|
| 키 순서·비어있지 않음 | PASS | 구조적 계약(dict 키, non-empty)은 실제 Engine 응답에서도 유지됨 |
| Agent-Capability 딕셔너리 리터럴 | PASS | `call_engine` 교체와 무관 — 영향 없음 확인 |
| 리뷰 내용 → 테스트 내용 exact substring(`"bare except"`, `"예외 처리 동작을 검증"`) | **FAIL** | 실제 Engine이 **"Bare `` `except: pass` ``"**로 표현 — 문자열이 다르다. 실패는 **구조적 결함이 아니라 문구 불일치**다 |

**사실 확인**: 실패한 테스트는 기존 rule-based 응답의 정확한 문구에 결합된
assertion이며, 이는 원래 `MVP.md` Exit Criteria가 rule-based Engine을
전제로 작성됐기 때문이다. 이 실패는 Execution Result Contract 미결정과
같은 사안이 **아니다** — 반환 타입(`str`)과 dict 구조는 그대로 유지됐다.

## Stop Trigger 대조

| Trigger(이번 작업 지시) | 발동 여부 |
|---|---|
| 새 Component/Layer/Service 필요 | 미발동 |
| Engine Gateway/Adapter 필요 | 미발동 — 단일 함수 유지 |
| Registry/Scheduler/Runtime 필요 | 미발동 |
| Engine Routing 필요 | 미발동 — Engine 선택 로직 없음 |
| Execution Result Contract 선결 필요 | 미발동 — Contract 없이 실행·관찰 완료 |
| Baseline 변경 필요 | 미발동 |
| Dev HQ Boundary 변경 필요 | 미발동 |
| Agent-Capability 매핑 일반화 | 미발동 |
| Task 호출 일반화 | 미발동 |

**하나도 발동하지 않았다.**

## 이 문서가 하지 않는 것

- `test_review_content_reaches_test_execution_as_context`를 고치지 않았다
  — 그 테스트를 어떻게 바꿀지는 Exit Criteria 재정의이며 이 문서의 범위가
  아니다.
- tracked 브랜치의 `engine.py`를 바꾸지 않았다 — 실제 배선은 worktree에만
  존재했고, 병합 여부는 이 문서가 판단하지 않는다.
- `subprocess.run(["claude", "-p", ...])`을 정식 Contract로 확정하지
  않았다 — 이번 배선이 유일하게 검증된 방법이라는 뜻이 아니다.

## Unknowns

- 반복 실행 시 Raw Output 형태가 얼마나 안정적인지 — 1회만 관찰했다.
- 기존 3개 테스트 중 실패한 1개를 제외한 나머지 케이스(다른 입력 코드)에서도
  같은 양상(구조 유지·문구 불일치)이 재현되는지 — 관찰하지 않았다.
- `subprocess.run` 방식이 유일하게 가능한 실제 배선 방법인지 — 대안(다른
  호출 방식)과의 비교는 하지 않았다.

## Conclusion

`call_engine()`은 구조(단일 함수, `str -> str`) 변경 없이 실제 Engine에
연결될 수 있다는 사실이 1회 관찰됐다. 이번 배선으로 어떤 Stop Trigger도
발동하지 않았다. 유일하게 관찰된 부작용은 기존 rule-based 문구에 결합된
테스트 1건의 실패이며, 이는 Architecture 문제가 아니라 Exit Criteria가
rule-based Engine의 정확한 문구를 전제했다는 사실을 드러낸다. 이 배선을
tracked 브랜치에 반영할지, 테스트를 구조적 assertion으로 바꿀지는 판단
사항으로 남긴다 — 이 문서는 그 판단을 하지 않는다.
