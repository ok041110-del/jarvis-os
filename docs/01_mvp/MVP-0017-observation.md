# MVP-0017 Observation

## 목적

`MVP-0013-observation.md`의 "범위 밖"에 남아 있던 항목("Classes 절을
실제로 여러 Class로 분해하는 로직")을 기존 Architecture/Contract를
유지한 채 최소 수정으로 해소한다.

## 왜 Design을 바꾸지 않았는가

MVP-0013 Observation은 이 항목이 막힌 이유를 "Design이 항상 단일
함수형 Component만 제안하므로(MVP-0011)"라고 적었다. Design(`_design_from_requirement`,
MVP-0011)이 실제로 여러 Component를 제안하도록 바꾸는 것도 한 방법이지만,
그러려면 Design의 `## Component` 절 구조(현재는 명시적으로 "단일
Component"라고 서술하는 고정 문구 포함)와, 그 절을 읽는
`_extract_slug()`(backtick 안 첫 함수 시그니처 하나만 읽음) 등 여러
지점을 함께 바꿔야 해 "최소 수정" 범위를 벗어난다.

대신 Design은 전혀 건드리지 않고, Implementation Specification이 이미
가진 정보만으로 분해했다: `## Functions` 절은 이미 두 역할(Public
Interface 함수 1개, Interfaces 절의 검증 함수 `{slug}_check_N` N개,
MVP-0011)을 구분해 나열하고 있었다. 이 구분을 그대로 `## Classes`
절에 반영했을 뿐, 새 Contract·새 Design 능력을 추가하지 않았다.

## 변경 파일

- `development-hq/mvp/engine.py`
  - `_slug_to_class_name(slug)` 추가 — 기존 `slug` 값(Design Component
    함수 시그니처에서 이미 추출되던 값)을 PascalCase Class 이름
    표기로만 바꾼다. 새 명명 규칙을 만들지 않는다.
  - `_generate_code()`의 `classes_lines`를 고정 문구에서 조건부
    생성으로 교체:
    - 검증 함수(`check_entries`, 기존에 이미 계산되던
      `_parse_interface_lines(interfaces_body)` 결과)가 1개 이상이면
      `{ClassName}`(Public Interface 담당)과
      `{ClassName}Validator`(검증 함수 담당) 2개 Class를 제안한다.
    - 검증 함수가 0개면 기존과 동일하게 "필요 없음"을 유지한다(나눌
      근거가 없으므로).

## 관찰 결과

### 실제로 다중 Class로 분해되는가?

**예.** 검증 함수 2개를 가진 Design 텍스트(Component: `login`,
Interfaces: `login_check_1`, `login_check_2`)를 직접 입력해 확인했다:

```
- `class Login`: Public Interface(`login`)를 구현하는 Component 본체.
- `class LoginValidator`: Interfaces 절의 검증 함수(`login_check_1`, `login_check_2`)를 모아 구현하는 Class.
```

### 검증 함수가 없는 경우 회귀는 없는가?

**예.** 같은 Design에서 `## Interfaces` 절을 placeholder
("Acceptance Criteria가 없어 Interfaces를 도출할 수 없음")로 바꾸면
`## Classes`는 변경 전과 동일하게 "필요 없음: ..."을 반환한다(문구는
"Design이 단일 함수형 Component만 제안했다"에서 "Interfaces에 검증
함수가 없어 Public Interface 하나로 충분하다"로 더 정확하게
바뀌었다 — 사실 자체는 동일).

### 다른 절/다른 Stage 판정에 영향이 있는가?

**아니오.** 새로 생성된 Implementation Specification을
`_detect_artifact_stage()`에 넣으면 여전히 `implementation`으로
정확히 분류되고(MVP-0014), `_review_code()`도 9개 필수 섹션이 모두
포함됨을 정상 확인한다. Target File/Public Interface/Functions/
Dependencies/Algorithm Outline/Edge Cases/Validation Notes/Reference
Design — Classes 외 다른 절의 생성 로직은 손대지 않았다.

### 기존 테스트

`development-hq/mvp/tests/test_mvp_0001.py` 3건 통과, 회귀 없음.

### 실제 Engine 실행

`call_engine()`을 직접 실행해 재확인했다(`CODE_GENERATION:test
prompt`). MVP-0014/0015/0016에서 이미 기록한 것과 동일하게, 실제
Claude CLI가 자유 형식 응답을 반환하고 `_generate_code()`를 포함한
rule-based Capability Logic 경로는 호출되지 않는다. 이번 변경으로
새로 달라진 사실은 없다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- Design Logic(`_design_from_requirement`)이 실제로 복수 Component를
  제안하도록 바꾸는 것 — 하지 않았다. 위 "왜 Design을 바꾸지 않았는가"
  참고.
- `call_engine()`의 dispatch 방식 변경 — 하지 않았다.
- Classes 분해 기준을 검증 함수 개수 이외의 다른 신호(예: Constraints
  개수, Responsibility 개수)로 확장하는 것 — 하지 않았다. Functions
  절이 이미 구분해 놓은 두 역할만 그대로 반영했다.

## Self Review

- Architecture를 변경했는가 — **아니오**.
- 새 Contract를 만들었는가 — **아니오**. `## Classes` 절은
  MVP-0013부터 이미 있던 절이며, 그 안의 내용 생성 로직만 바꿨다.
- Design을 수정했는가 — **아니오**.
- 기존 테스트가 통과하는가 — **예**, 3건 모두 통과, 회귀 없음.
- 실패를 성공으로 표현했는가 — **아니오**.
