# MVP-0019 Observation

## 목적

MVP-0018 Observation의 "범위 밖"에 남긴 항목("RISK_MARKERS('문제'가
'문제없다' 안에서 걸릴 가능성 등)... 이번에 실측으로 관찰하지 않은
사례는 다루지 않았다")을 실제로 재현·확인한 뒤 동일한 최소 수정
방식(MVP-0018의 `NEGATED_MARKER_EXCEPTIONS`/`_contains_marker`)으로
해소했다.

## 발견한 문제 (실제 실행으로 확인)

```python
sentences = ['이 기능은 문제없다.', '정상 동작한다.']
_extract_marked_sentences(sentences, RISK_MARKERS, 'none')
# → '- 이 기능은 문제없다.'  (틀림 — "문제없다"는 문제가 없다는
#    뜻인데 RISK_MARKERS의 "문제"가 부분 문자열로 걸려 Risk로
#    잘못 뽑혔다)
```

MVP-0018과 정확히 같은 유형의 버그다 — 마커가 정반대 의미의 부정형
단어 안에 부분 문자열로 걸린다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `NEGATED_MARKER_EXCEPTIONS`에 `"문제": ("문제없다",)` 1건만
    추가했다. 새 메커니즘을 만들지 않고 MVP-0018이 만든 기존
    `_contains_marker()`/`NEGATED_MARKER_EXCEPTIONS` 구조를 그대로
    재사용했다.

## 관찰 결과

### 버그가 고쳐지는가?

**예.** 위 재현 케이스가 이제 `- none`(빈 결과에 대한 fallback
문구)을 반환한다 — "문제없다" 문장이 더 이상 Risk로 잘못 뽑히지
않는다.

### Regression 확인 (직접 실행)

- 순수 긍정형(`"이 부분에 문제가 있다."`) — 여전히 정상적으로 Risk로
  매칭됨.
- 부정형과 긍정형이 한 Issue 안에 같이 있는 경우(`"이 기능은
  문제없다. 하지만 다른 부분에 문제가 있다."`) — 부정형 문장은
  제외되고 실제 긍정형 문장만 Risk로 정확히 선택됨.
- MVP-0018의 기존 수정(`"필요하다"` ← `"불필요하다"`) — 그대로 유지됨,
  재실행으로 재확인.
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`REQUIREMENT_ANALYSIS:test`).
MVP-0014~0018에서 이미 기록한 것과 동일하게, 실제 Claude CLI가 자유
형식 응답을 반환하고 `_extract_marked_sentences()`를 포함한 rule-based
Capability Logic 경로는 호출되지 않는다. 이번 변경으로 새로 달라진
사실은 없다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- RISK_MARKERS의 나머지 항목(`"실패"`/`"오류"`/`"위험"`/`"왜곡"`/
  `"결함"`/`"누락"`)이 각자의 부정형(`"실패하지 않는다"`,
  `"오류 없다"` 등) 안에서 걸릴 가능성 — 이번에 실측으로 재현하지
  않았으므로 다루지 않았다. 다음 미해결 항목으로 남긴다.
- OUT_OF_SCOPE_MARKERS의 부정형 점검 — 이번에 실측하지 않았다.
- 마커 매칭을 형태소 분석기 등 실제 NLP 파이프라인으로 교체 — 하지
  않았다.
- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. MVP-0018이 만든 기존 구조에
  실제 관찰된 사례 1건만 추가했다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
