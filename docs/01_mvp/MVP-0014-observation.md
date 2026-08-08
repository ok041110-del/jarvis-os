# MVP-0014 Observation

## 목적

`MVP-0013-observation.md`의 "Regression 확인"이 남긴 관찰(Implementation
Specification이 Validation에서 "design"으로 오분류됨)을 Stage-Aware
Validation(MVP-0012) 범위 안에서 최소 수정으로 해소한다. 새
Architecture/Contract는 만들지 않는다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `_looks_like_implementation(text)` 추가 — `## Target File` +
    `## Public Interface`(Implementation Specification, MVP-0013
    `_generate_code`에만 있는 마커)로 판단.
  - `_detect_artifact_stage()`에 `implementation` 분기 추가 — 코드
    판정 다음, Design 판정보다 먼저 검사한다. Implementation
    Specification은 `## Reference Design`으로 Design 전체를 verbatim
    포함하므로, Design 판정을 먼저 하면 그 안에 중첩된 `##
    Interfaces`/`## Reference Requirement`에 걸려 Design으로 오판된다
    (MVP-0013이 실측한 문제).
  - `IMPLEMENTATION_REQUIRED_SECTIONS` 상수, `_review_implementation()`,
    `_suggest_implementation_checks()` 추가 — 기존 `_review_design`/
    `_suggest_design_checks`와 동일한 패턴(필수 섹션 존재 확인, 구조
    기반 검증 항목 도출)을 Implementation Specification 전용 섹션에
    적용한다.
  - `_review_code()`, `_suggest_tests()`에 `implementation` 분기를
    추가로 연결. 기존 code/requirement/design(fallback) 분기는
    순서·조건 변경 없이 그대로 유지.

## 관찰 결과

### Stage 오분류가 실제로 해소되는가?

**예.** `core/execution_layer/mvp_0002/dogfooding/output/real_issue.implementation_specification.md`
(MVP-0013이 생성 예시로 인용한 것과 동일한 구조의 Implementation
Specification)를 직접 입력해 확인했다.

- 변경 전(코드 미변경 상태 기준 재현): `_detect_artifact_stage()` →
  `"design"` (Reference Design 안의 `## Interfaces`/`## Reference
  Requirement`에 걸림)
- 변경 후: `_detect_artifact_stage()` → `"implementation"`,
  `_review_code()`는 Implementation Specification 전용 9개 섹션
  확인 결과를, `_suggest_tests()`는 Functions/Dependencies/Edge
  Cases/Validation Notes 기반 검증 항목 4건을 반환한다.

### Regression 확인

- Design 입력(`_design_from_requirement()` 산출물)의 stage 판정 —
  `"design"` 그대로 유지.
- Requirement 입력(`_analyze_requirement()` 산출물)의 stage 판정 —
  `"requirement"` 그대로 유지.
- Python 코드 입력의 stage 판정 — `"code"` 그대로 유지.
- 기존 테스트: `development-hq/mvp/tests/test_mvp_0001.py` 3건 모두
  통과.

### 실제 Engine 실행 — 중요한 발견 (해결하지 않음, 기록만)

`mvp.agents`의 모든 Capability 함수(`backend_agent_code_review`,
`qa_agent_test_execution` 등)는 `call_engine(prompt)`를 거친다.
`call_engine()`을 실제로 호출해 확인한 결과(`CODE_REVIEW:def
add(a,b): return a+b`), **실제 Claude CLI(`claude -p`)가 자유
형식 자연어 응답을 반환했다** — `CODE_REVIEW:` prefix는 무시되고,
`_rule_based_response()`/`_review_code()`/이번에 수정한
`_detect_artifact_stage()`는 전혀 호출되지 않았다.

이는 이번 변경으로 생긴 문제가 아니다. `engine.py` 27~31행 주석이
이미 이 사실을 기록하고 있다: `_rule_based_response` 경로는
`call_engine()`이 더 이상 호출하지 않는 "현재 미사용 코드"다
(ENGINE-CONNECT-0001에서 `call_engine()`이 prefix 기반 라우팅 대신
실제 Engine 직접 호출로 교체됨). 이번 관찰로 새로 확인된 것은, 그
"미사용 코드"에 **Stage-Aware Validation(MVP-0012)과 이번 MVP-0014
전체가 포함된다**는 사실의 명시적 연결이다 — 즉 실제 운영 파이프라인
(`call_engine()` 경유)에서는 Requirement/Design/Implementation/Code
Stage 구분이 전혀 일어나지 않는다.

**이 문서는 이 사실을 판단하지 않는다.** `_rule_based_response` 경로를
`call_engine()`에 다시 연결할지(Engine 호출 방식에 대한 결정이며,
ENGINE-CONNECT-0001이 이미 명시적으로 다른 방향을 택했다), 아니면 이
모듈을 별도 Capability Logic 계층으로 유지할지는 Architecture/Contract
결정이 필요한 사안이다. 이번 MVP는 그 결정을 하지 않았고, 기존
Validation Logic 모듈 내부의 최소 수정만 수행했다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.
- `_rule_based_response()`를 다시 연결하는 것 — 하지 않았다.
- 새 Stage, 새 Capability, 새 Engine 함수 추가 — 하지 않았다.
- Workflow(`workflow_0008.py` 등)가 Implementation Specification을
  다르게 라우팅하도록 바꾸는 것 — 하지 않았다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. 기존 Stage-Aware Validation
  패턴(MVP-0012)을 그대로 따랐다.
- `call_engine()`의 dispatch를 바꿨는가 — **아니오**.
- 실제 Engine을 실행해 검증했는가 — **예**(`call_engine()` 직접 호출,
  위 절 참고). 그 결과 발견한 "Validation Logic 미도달" 사실은
  숨기지 않고 그대로 기록했다.
- 실패를 성공으로 표현했는가 — **아니오**. 코드 변경 자체(Stage 분류
  정확도)는 검증대로 동작하지만, 그것이 실제 운영 파이프라인에
  연결되어 있지 않다는 사실을 그대로 밝혔다.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
