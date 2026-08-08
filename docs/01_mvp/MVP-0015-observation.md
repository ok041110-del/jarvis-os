# MVP-0015 Observation

## 목적

`MVP-0012-observation.md`의 "범위 밖"에 남아 있던 항목(`_detect_artifact_stage`가
`unknown`을 반환하는 입력에 대한 별도 처리)을 Stage-Aware Validation
범위 안에서 최소 수정으로 해소한다. 새 Architecture/Contract는 만들지
않는다.

## 발견한 문제 (실제 실행으로 확인)

`unknown` 입력을 기존 코드로 실행하면 Design fallback이 적용되어,
실제로는 존재하지도 않는 Design 구조(Component/Responsibility/
Interfaces/Constraints/Open Questions/Reference Requirement)의 "누락"을
6건 보고했다:

```
- '## Component' 섹션이 없습니다. Architecture Draft에 포함되어야 합니다.
- '## Responsibility' 섹션이 없습니다. Architecture Draft에 포함되어야 합니다.
... (총 6건)
```

입력이 Design이 아니라는 것은 이미 알고 있음에도(그래서 `unknown`이 나온
것), Design 전용 Finding을 지어내는 것은 False Positive다 — MVP-0012가
Requirement 입력에 대해 이미 한 번 고친 것과 같은 종류의 문제다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `_review_unknown(text)`, `_suggest_unknown_checks(text)` 추가 —
    Stage를 판단할 수 없다는 사실 자체를 정직하게 반환하고, 존재하지
    않는 Design 섹션이나 검증 항목을 지어내지 않는다.
  - `_review_code()`, `_suggest_tests()`의 fallback을
    `_review_design()`/`_suggest_design_checks()`에서
    `_review_unknown()`/`_suggest_unknown_checks()`로 교체. `code`/
    `requirement`/`implementation`/`design` 4개 분기는 순서·조건
    변경 없이 그대로 유지.

## 관찰 결과

### False Positive가 해소되는가?

**예.** `unknown` 입력에 대해 `_review_code()`가 이제
"입력이 Requirement/Design/Implementation Specification/Code 중 어느
구조와도 일치하지 않아 Stage를 판단할 수 없습니다"를 반환한다(1건,
사실과 일치). `_suggest_tests()`도 동일하게 "구조 기반 검증 항목을
생성할 수 없습니다"를 반환한다.

### Regression 확인

- `code`/`design`/`requirement`/`implementation` 4개 stage 판정과
  각각의 review/suggest 출력 — 모두 변경 전과 동일(직접 실행으로
  재확인).
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 통과.

### 실제 Engine 실행

MVP-0014에서 이미 확인·기록한 사실(`call_engine()`이 ENGINE-CONNECT-0001
이후 실제 Claude CLI를 직접 호출하며, `_rule_based_response()` 경로
전체 — 이번 변경 포함 — 를 거치지 않음)이 이번 변경에도 동일하게
적용된다. 새로 확인할 내용이 없어 재검증만 하고 반복 서술하지 않는다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- `call_engine()`의 dispatch 방식 변경 — 하지 않았다(MVP-0014와 동일한
  이유로 Architecture 결정 사안이라 손대지 않음).
- 새 Stage, 새 Capability, 새 Engine 함수 추가 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. 기존 Stage-Aware Validation
  4-way 분기 구조를 그대로 따르고, fallback 분기의 내용만 정직하게
  바꿨다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
