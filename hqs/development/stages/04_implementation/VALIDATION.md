# Stage 04: Validation

## 검증 원칙

3개 Capability 모두 기존에 검증된 함수를 재사용한다(`identify_target`/
`build_dependency_closure`/`backend_agent_code_generation`은
`test_workflow_ast_context.py`와 ADC-0005 §8 real Engine E2E가 이미
검증). 여기서는 (a) Stage 03 `design`이 올바르게 전달되는지, (b)
조립 로직이 target 유무/exposure 켬끔 4가지 조합에서 결정적으로
맞는지, (c) Engine 실패 시 기존 오류 포맷 유지 여부를 mock으로 확인
하고, (d) 실제 Engine 호출 + 파일 적용으로 "생성된 Code가 실제
Production Code를 대상으로 Scope를 벗어나지 않고 Stage 05가 검증
가능한 형태인가"를 확인한다.

## 테스트 위치

`hqs/development/mvp/tests/test_stage_04.py` — 이전 Stage와 동일하게
Stage 폴더 하위가 아닌 기존 공통 `tests/` 위치를 쓴다(ADR-0008 §1).

## 검증 항목

| 항목 | 방법 |
|---|---|
| `identify_target`이 Stage 03 `design`을 실제로 받는지 | mock으로 전달 인자 확인 |
| target 없음일 때 build 입력이 design 그대로인지 | 결정적 단위 테스트 |
| target 있음 + exposure 끔일 때 closure만 concatenate되는지 | 결정적 단위 테스트 |
| target 있음 + exposure 켬일 때 대상 파일 전체 + 정책 지시문이 포함되는지 | 결정적 단위 테스트(`tmp_path`에 쓴 가짜 모듈 사용, Stage 02/03 테스트 관례와 동일) |
| Engine 실패 시 오류 포맷 유지, `target`은 실패 시점 값 유지 | mock이 예외를 던질 때 확인 |
| Stage 05가 소비 가능한 형태(Contract 준수) | `IMPLEMENTATION.md` 스키마와 실제 반환 값 일치를 단위 테스트로 고정 |

## real Engine E2E (실제 파일 적용 포함)

Stage 04의 Output은 "실제로 적용 가능한 Code Change"여야 하므로, mock만
으로는 이 요구사항을 증명할 수 없다. T06~T19/ADC-0005 §8과 동일한
방법론으로 실제 파일에 적용해 검증한다:

1. Stage 01 → 02 → 03 → 04를 순서대로 실제 실행한다(Blind Issue —
   실제 파일명/함수명을 언급하지 않음), `expose_target=True`로 호출한다.
2. `target`이 식별됐는지, 대상 파일이 실제 저장소 파일인지 확인한다.
3. 대상 파일을 백업한 뒤 `implementation`을 그대로 덮어쓴다.
4. `pytest`를 실행해 기존 테스트가 깨지지 않는지 확인한다.
5. 원본과 diff를 떠 Scope 준수(대상 함수 내부만 변경, 다른 함수·
   import·공백 불변)를 확인한다.
6. 파일을 백업본으로 원상복구하고 `git status`로 저장소에 잔여
   변경이 없는지 확인한다.
7. 결과와 판정(PASS/PARTIAL/FAIL)을 이 Stage의 최종 보고(세션 기록)에
   남긴다 — 이 문서는 방법론만 고정하고 특정 시점의 결과를 반복
   기록하지 않는다.

이 절차는 Stage 04 자체의 Production 경로가 아니라 **검증 절차**다
(`IMPLEMENTATION.md`: Stage 04는 파일을 직접 쓰지 않는다) — Stage 05
가 실제로 이 절차를 반복 수행할 수 있음을 보여주는 것이 목적이다.
