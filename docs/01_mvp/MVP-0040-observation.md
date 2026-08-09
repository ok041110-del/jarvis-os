# MVP-0040 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 1개 파일에서 최소
수정했다** — 실제 Engine으로 재현한 실제 Contract 오염(내부 분기
신호가 사람이 읽는 결과에 노출됨)을 고쳤다.

## 목적

`MVP-0038`(Project Intelligence)·`MVP-0039`(code_generation)와 같은
이유(`GOVERNANCE-REVIEW-0004`·`0005`: Production caller 위치 미결
동안 진행 가능한 트랙은 Development HQ Capability Engineering뿐)로
다음 개선 대상을 선정한다.

### 후보 검토 (실제 실행으로 확인, 문제 없던 것들)

- `requirements_agent_requirement_analysis()`/`design_agent_design()`
  — "코드를 작성하지 말라"는 지시를 실제 Engine이 지키는지 새 Issue로
  직접 실행해 확인했다. 반환값 어디에도 markdown 코드 fence가
  없었다(`"```" in text` → `False` 둘 다) — 문제 없음.
- `backend_agent_code_review()`의 "실제 이슈가 있으면 놓치지 않는가"
  — 눈에 잘 안 띄는 off-by-one 버그(`moving_average`)를 담은 코드로
  직접 실행해 확인했다. 실제 Engine이 버그를 정확히 지적했고
  `NO_ISSUES_MARKER`도 정확히 부재했다 — 문제 없음.
- `qa_agent_test_execution()` — 반환값에 markdown fence가 없음을
  확인했다 — 문제 없음(애초에 "코드가 아니라 목록을 제안하라"는
  지시라 `MVP-0039`의 fence 문제와 다른 종류).

### 발견한 문제 (실제 Engine으로 확인)

`workflow_0002.run_mvp_0002()`는 `backend_agent_code_review()`가
반환한 `review`에서 `NO_ISSUES_MARKER`("NO_ISSUES_FOUND")를 찾아
test_execution 생략 여부를 판단한다(`MVP-0027`). 그러나 이 마커를
찾은 뒤 `review` 자체를 정리하지 않고 **그대로** `code_review`
반환값에 담았다 — 마커는 이 파일이 분기를 판단하기 위한 내부 신호일
뿐인데, 사람이 읽는 `code_review` 결과의 일부로 그대로 노출됐다.

실제 Engine으로 확인(수정 전, 이슈 없는 코드):

```python
run_mvp_0002('''def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
''')
```

`code_review`가 실제로 다음과 같이 끝났다(발췌):

```
... 이지만, ... 것은 의도적인 트레이드오프로 볼 수 있다.

NO_ISSUES_FOUND
```

기계 신호(`NO_ISSUES_FOUND`)가 사람이 읽는 리뷰 텍스트 마지막 줄에
그대로 노출됐다 — `MVP.md` Expected Result("코드 리뷰 코멘트")가
기대하는 것은 리뷰 내용이지 내부 분기 신호가 아니다.

## 변경 파일

- `development-hq/mvp/workflow_0002.py`
  - `_strip_trailing_marker(review, marker)`(신규 헬퍼): `review`의
    마지막 줄이 정확히 `marker`이면 그 줄(과 그 앞 공백 줄)만
    제거한다. 마커가 다른 위치에 있거나 없으면 원문을 그대로
    반환한다 — `backend_agent_code_review`의 지시("이슈가 없을
    때만 응답 마지막 줄에 정확히 NO_ISSUES_FOUND를 적으라",
    MVP-0027)가 요구하는 정확한 형태만 제거 대상으로 삼는다.
    `agents.py`의 `_strip_code_fence`(MVP-0039)와 같은 종류의
    "Capability 출력에서 그 결과의 일부가 아닌 신호만 제거하는"
    후처리다.
  - `run_mvp_0002()`: `NO_ISSUES_MARKER in review` 분기가 참일 때만
    `review = _strip_trailing_marker(review, NO_ISSUES_MARKER)`를
    한 줄 추가했다. 분기 판단 자체(`if NO_ISSUES_MARKER in review`)는
    바꾸지 않았다 — 정리 전 원문으로 먼저 판단한 뒤에만 정리한다.
    반환 계약(`{"code_review": ..., "test_execution": ...}`, 정확히
    2개 키)은 그대로 유지했다.

## 관찰 결과 — 단위 검증

`_strip_trailing_marker()`를 4개 케이스에 적용했다: (1) 마커가
마지막 줄인 경우(개행 있음/없음 2가지) → 마커 줄 제거, 앞 텍스트만
남음. (2) 마커가 본문 중간에 언급된 경우 → 원문 그대로(오제거 없음).
(3) 마커가 아예 없는 경우 → 원문 그대로. 4개 전부 기대한 대로
동작했다.

## 실제 Engine으로 End-to-End 검증 (mock 없음)

같은 "이슈 없는" 코드(`add()`)로 `run_mvp_0002()`를 반복 실행한 결과,
한 번은 분기가 실제로 발동했다(`test_execution`이
"(생략됨: ...)"으로 반환됨, 15.7초). 그 실행에서 `code_review`의
마지막 부분을 확인한 결과:

```
... No correctness bugs, no risky patterns, nothing to fix.
```

수정 전(위 "발견한 문제")과 달리 `NO_ISSUES_FOUND`가 결과에 전혀
없었다(`"NO_ISSUES_FOUND" in result["code_review"]` → `False`) —
분기 판단은 그대로 정확히 동작(test_execution 생략)하면서, 사람이
읽는 `code_review`에서는 내부 신호가 사라졌다.

같은 세션에서 이슈가 있는 코드(bare except + mutable default)로도
재실행해, 분기가 정상적으로 test_execution을 실행하는 쪽으로
동작함을 재확인했다(`code_review`에 마커 없음, `test_execution`
1979자 반환) — 이슈가 있을 때의 경로는 이번 수정으로 건드리지
않았으므로 회귀가 없어야 하고, 실측으로도 회귀가 없었다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과
  (real Engine 호출 포함, mock 없음, 81.4초). 이 테스트는
  `run_mvp_0001`(`workflow.py`, 분기 없음)만 검증하므로 이번 수정과
  무관하지만, `workflow_0002.py`의 import 오류나 사이드 이펙트가
  없음을 함께 확인한다.
- `git status --porcelain` — `development-hq/mvp/workflow_0002.py`
  1개 파일만 변경.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| Agent-Capability 매핑이 Registry처럼 일반화 | 미발동 |
| Task 호출이 Workflow Parser/Scheduler로 일반화 | 미발동 — 기존 `if/else` 분기 구조를 그대로 유지, 반환 전 정리 한 줄만 추가 |
| 새 Capability/Agent/Engine 추가 | 미발동 |
| 새 Architecture/Concept/Component 필요 | 미발동 |

**하나도 발동하지 않았다.**

## 범위 밖 (이번 구현에서 하지 않은 것)

- `workflow.py`(MVP-0001, 분기 없음) — 애초에 `NO_ISSUES_MARKER` 분기
  자체가 없으므로 이 문제가 발생하지 않는다. 손대지 않았다.
- `backend_agent_code_review`/`qa_agent_test_execution`의 지시 문장 —
  건드리지 않았다.
- Production caller, Kernel Component, Runtime, Prompt Cache —
  건드리지 않았다.
- 새 RFC/ADC/ADR — 만들지 않았다. 이번 수정은 Architecture 결정이
  필요한 지점을 만들지 않았다.

## Self Review

- 코드를 변경했는가 — **예, 1개 파일(`workflow_0002.py`)**. 실제로
  재현한 실제 Contract 오염(분기 신호가 사람이 읽는 결과에 누출)을
  최소 후처리 헬퍼 하나로 고쳤다.
- Architecture를 설계했는가 — **아니오**. 새 Concept/Layer/Component
  없음. 분기 로직 자체와 반환 Contract(2개 키)를 그대로 유지했다.
- 실제 Engine으로 확인했는가 — **예**. 수정 전 재현 1회, 수정 후
  End-to-End 반복 실행으로 분기가 실제로 발동한 케이스를 확보해
  검증(mock 없음). 기존 pytest 3건도 real Engine 포함 재실행해
  회귀 없음을 확인했다.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  다른 3개 Capability(requirement_analysis/design/test_execution)는
  직접 실행으로 확인한 뒤 "문제 없음"으로 정확히 구분해 기록했다.
- 새 Architecture가 필요한 지점을 만났는가 — **아니오**. 이번
  수정은 기존 분기 판단 로직 뒤에 정리 한 줄을 추가하는 것으로
  충분했다.
- 불필요한 변경을 확인했는가 — **예**. `agents.py`, `engine.py`,
  `workflow.py`, 다른 `workflow_*.py`, `cli.py`,
  `project_intelligence.py` 어디에도 손대지 않았다(`git status
  --porcelain` 확인).
