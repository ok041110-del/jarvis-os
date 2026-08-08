# MVP-0018 Observation

## 목적

`_extract_goal()`/`_extract_marked_sentences()`(MVP-0010)의 마커
매칭이 부분 문자열 방식이라, 부정형 단어 안에서 오탐이 발생하는
사례를 실제 실행으로 발견하고 최소 수정으로 고쳤다. MVP-0009가 이미
같은 종류의 문제("open"이 "OpenHands" 안에서 걸림)를 고친 적이 있는
것과 동일한 유형이다.

## 발견한 문제 (실제 실행으로 확인)

```python
sentences = ['이 기능은 불필요하다.', '로그인 기능을 추가한다.']
_extract_goal(sentences, 'title')
# → '이 기능은 불필요하다.'  (틀림 — "불필요"는 "필요 없음"을 뜻하는데
#    GOAL_MARKERS의 "필요하다"가 "불필요하다" 안에서 부분 문자열로
#    걸려 Goal로 잘못 뽑혔다)
```

`GOAL_MARKERS = ("필요하다", "해야 한다", "검토가 필요", "확인이
필요")`의 `"필요하다"`가 `"불필요하다"`(정반대 의미) 안에 포함되어
있어 생기는 문제였다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `NEGATED_MARKER_EXCEPTIONS` 딕셔너리 추가 — `"필요하다"` 마커가
    `"불필요하다"` 안에서 걸리는, 실제로 관찰된 사례 1건만 등록했다.
    다른 마커의 부정형 전수 처리는 하지 않았다(RISK_MARKERS의 "문제"가
    "문제없다" 안에서 걸리는 등 다른 잠재 사례는 이번에 실측하지
    않았으므로 손대지 않았다).
  - `_contains_marker(sentence, marker)` 추가 — `marker in sentence`와
    같되, 등록된 부정형 안에서만 걸리는 경우는 매칭에서 제외한다.
    부정형을 지운 나머지 문장에 marker가 별도로 남아 있으면(다른
    위치에서 실제로 쓰였다면) 여전히 매칭으로 인정한다.
  - `_extract_goal()`, `_extract_marked_sentences()`의 `marker in
    sentence`를 `_contains_marker(sentence, marker)`로 교체.

## 관찰 결과

### 버그가 고쳐지는가?

**예.** 위 재현 케이스가 이제 `'title' 기능을 추가한다.`(고정
fallback 템플릿)를 반환한다 — "불필요하다" 문장이 더 이상 Goal로
잘못 뽑히지 않는다.

### Regression 확인 (직접 실행)

- 순수 긍정형(`"이 기능이 필요하다."`) — 여전히 정상 매칭됨.
- MVP-0010이 의도적으로 허용하기로 결정한 중복(Goal이자 Open
  Question인 문장, 예: "...검토가 필요하다")— 여전히 두 절 모두에
  나타남. 이번 수정은 그 의도적 중복 결정을 건드리지 않았다.
- 부정형과 긍정형이 한 Issue 안에 같이 있는 경우("불필요하다"와
  "필요하다"가 각각 다른 문장에 등장) — 부정형 문장은 제외되고 실제
  긍정형 문장이 Goal로 정확히 선택됨.
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`REQUIREMENT_ANALYSIS:test`).
MVP-0014~0017에서 이미 기록한 것과 동일하게, 실제 Claude CLI가 자유
형식 응답을 반환하고 `_extract_goal()`을 포함한 rule-based Capability
Logic 경로는 호출되지 않는다. 이번 변경으로 새로 달라진 사실은 없다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- RISK_MARKERS("문제"가 "문제없다" 안에서 걸릴 가능성 등)나
  OUT_OF_SCOPE_MARKERS의 부정형 전수 점검 — 이번에 실측으로 관찰하지
  않은 사례는 다루지 않았다.
- 마커 매칭을 형태소 분석기 등 실제 NLP 파이프라인으로 교체 — 하지
  않았다. 문자열 매칭 방식은 그대로 유지했다.
- MVP-0010이 의도적으로 허용한 Goal/Open Question 중복 자체를
  제거하는 것 — 하지 않았다(이번 수정과 무관한, 이미 결정된 사안).
- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. 기존 마커 매칭 방식(문자열
  부분 매칭)을 유지하고, 실제 관찰된 오탐 1건만 제외했다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
