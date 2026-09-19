# Stage → Team OpenRouter Real Call Validation (4) — T5-B-1 Contract 구조 검증(코드 근거)

## Summary

- T5-B(Contract 재검증)의 첫 단계로, **추가 real Engine 호출·GitHub
  접근·코드 변경 없이** `stages/contracts.py`와 Stage 03/04/05 코드를
  재검토해 "Contract의 구조적 준수가 Engine 성공/실패와 무관한가"를
  **코드 근거**로 확인했다.
- 결론: **무관하다.** `require_keys()`는 dict의 **키 존재 여부만**
  검사하며 값의 타입·의미·성공/실패 여부를 검사하지 않는다. Stage
  03/04/05는 성공 경로와 실패(`try/except`) 경로에서 **정확히 동일한
  키 집합**을 반환하도록 코드가 짜여 있다 — 값(문자열 내용)만 다를 뿐
  dict 형태는 달라지지 않는다.
- `-0001`/`-0002`/`-0003`의 **실측**(실패 경로에서 Contract 3종 전부
  위반 없음, 누적 5건)과 이번의 **코드 근거**(성공/실패 무관하게 형태가
  동일함이 소스 자체에 있음)를 결합하면, "성공 경로에서도 Contract
  형태 위반이 없을 것"이라는 **논리적 결론**에 도달한다.
- **이것은 실측이 아니다.** 실제 성공 응답이 발생했을 때 그 content가
  Stage 05의 개별 판정 로직(`target != None` 경로)에 미치는 영향은
  여전히 **미검증**이며, 이 문서는 "성공 경로 실측 검증 완료"라고
  표현하지 않는다.
- `candidate_index`/`target` 식별 경로(GitHub 기반 실제 후보를 사용해
  `identify_target()`이 non-None target을 반환하는 시나리오)는 별도
  트랙(**T5-C**)으로 이관한다.

---

## 1. 목적 및 범위

**목적**: T5-A까지 누적 성공 표본이 0/5인 상태에서, "Contract가 성공
경로에서도 지켜지는가"라는 질문에 **추가 real Engine 호출 없이** 답할
수 있는 부분과 답할 수 없는 부분을 명확히 구분해 기록한다.

**범위에 포함**: `stages/contracts.py`(`require_keys`,
`validate_design_result`, `validate_implementation_result`,
`validate_verification_result`), `stage_03.py`/`stage_04.py`/
`stage_05.py`의 정상/예외 반환문 재검토, `-0001`~`-0003`의 기존 실측
결과 재인용.

**범위에서 제외**: 신규 real Engine 호출, GitHub 접근, 코드 변경,
Architecture/Contract 변경. 이번 문서는 **읽기 전용 코드 분석**이다.

---

## 2. 코드 근거 (1) — `require_keys()`는 키 존재만 검사한다

`stages/contracts.py`:

```python
def require_keys(data: dict, keys: tuple, contract_name: str) -> None:
    """`data`에 `keys`가 전부 있는지만 확인한다(값의 타입/의미는 검사하지
    않음 — Stage 내부 로직의 재해석이 아니라 Handover 시점 존재 확인)."""
    missing = [key for key in keys if key not in data]
    if missing:
        raise ContractViolation(f"{contract_name} contract violated — missing keys: {missing}")
```

`validate_design_result`/`validate_implementation_result`는 이
`require_keys()`를 그대로 호출할 뿐이다. 즉 **키가 존재하기만 하면
값이 무엇이든(성공 텍스트든 엔진 실패 메시지든) 통과한다** — 이는
docstring이 이미 명시한 대로 "값의 타입/의미는 검사하지 않음"이며,
이번 재검토로 재확인한 사실이다.

`validate_verification_result`만 예외적으로 값 내용을 일부 검사한다
(`required_checks`가 `check_results`에 실제로 반영됐는지, SKIPPED가
아닌지) — 그러나 이 검사도 **"성공/실패"가 아니라 "선언된 항목이
실행됐는지"**를 보는 것이며, Engine 호출의 성공 여부 자체는 검사
대상이 아니다.

---

## 3. 코드 근거 (2) — Stage 03/04/05의 성공·실패 반환 구조가 동일하다

| Stage | 정상 반환 | 예외 반환(`except`) | 키 집합 동일 여부 |
|---|---|---|---|
| 03(`stage_03.py::run_stage_03`) | `{"skeleton": skeleton, "design": design}` (design은 `design_agent_design()` 성공 결과) | 동일 함수, `design = _engine_failure_message(exc)`로 값만 교체 후 **같은 `return {"skeleton": skeleton, "design": design}`** 한 줄을 그대로 사용 | **동일** |
| 04(`stage_04.py::run_stage_04`) | `{"target": target, "implementation": implementation, "expose_target": expose_target}` | `except Exception as exc: return {"target": None, "implementation": _engine_failure_message(exc), "expose_target": expose_target}` | **동일**(3개 키 완전 일치) |
| 05(`stage_05.py::run_stage_05`) | `{"structural_check":..., "specification_check":..., "design_scope_check":..., "test_execution":..., "code_review":..., "required_checks":..., "check_results":..., "verdict":...}` (8키, `_build_check_results()`가 `KNOWN_CHECK_NAMES` 4개를 **항상** 순회) | 별도 예외 분기 없음 — `is_engine_failure(implementation)`로 `code_review` 값만 스킵 메시지로 교체, 나머지 로직·반환 키 구조는 **정상 경로와 동일 코드 경로**를 그대로 통과 | **동일** |

**핵심 사실**: Stage 03/04는 `try/except`가 반환 키 구조 자체를
바꾸지 않고 **값만 교체**하도록 설계돼 있고(코드가 정상 경로와
예외 경로에서 동일한 `return` 딕셔너리 리터럴을 사용), Stage 05는
애초에 예외 분기 없이 단일 코드 경로로 8개 키를 항상 채운다. 이는
"Contract가 성공/실패와 무관하게 같은 형태를 반환하도록" 설계된
것이 **우연이 아니라 코드 구조 자체의 성질**임을 보여준다.

---

## 4. 실측 근거 — `-0001`~`-0003`의 기존 Evidence 재인용

| 문서 | 실행 건수 | Engine 결과 | Contract 3종 검증 결과(실측) |
|---|---|---|---|
| `-0001` | 1(단일 함수 호출) | 실패 | 해당 없음(Team/Stage 경로 아님, 단일 함수만 검증) |
| `-0002` | 2(Stage 03/04) | 전부 실패 | `validate_design_result`/`validate_implementation_result`/`validate_verification_result` **3종 전부 위반 없음(실측)** |
| `-0003`(T5-A) | 2(Stage 03/04) | 전부 실패 | 위와 동일하게 **3종 전부 위반 없음(실측)** |

**누적**: Engine 호출 5건(모두 실패, 성공 0/5) 동안 Contract 위반은
**0건** — 이는 §2/§3의 코드 근거가 예측하는 바와 정확히 일치한다.

---

## 5. 논리적 결론 (실측이 아님을 명시)

§2(검증 로직이 값이 아니라 키만 본다)와 §3(코드가 성공/실패 무관하게
동일한 키 구조를 반환하도록 짜여 있다)을 결합하면:

> **Contract의 구조적 준수(키 존재)는 Engine 호출의 성공/실패
> 여부와 무관하다 — 성공 응답이 오더라도 반환되는 dict의 키 집합은
> 지금까지 실측된 실패 경로와 동일할 수밖에 없다.**

이는 **코드가 그렇게 짜여 있다는 사실에서 도출한 논리적 추론**이며,
**실제 성공 응답을 관찰해서 확인한 실측 결과가 아니다.** 이 문서는
이 결론을 "성공 경로 실측 검증 완료"로 표현하지 않는다 — 정확한
표현은 "성공 경로에서도 Contract 키 구조가 위반될 코드 경로 자체가
존재하지 않는다"이다.

---

## 6. 명시적으로 미검증인 것

- **실제 성공 응답의 content**(design/implementation/code_review 텍스트가 실제로 무엇을 담는지)는 관찰된 적이 없다(누적 0/5).
- **`target != None` 경로**: `identify_target()`이 실제로 non-UNKNOWN 응답을 받아 `(module_name, function_name)`을 반환하는 시나리오는 지금까지 전부 배제됐다(빈 `candidate_index`로 UNKNOWN 유도). 이 경로가 열리면 Stage 05의 `_check_specification_scope`/`_check_design_scope`/`_run_pytest_with_applied_implementation`이 **로컬 파일을 실제로 읽는 non-trivial 판정 로직**을 타게 되는데, 이 판정 결과가 Contract의 `CheckResult` 스키마(`{name, status, blocking, detail}`)를 벗어나지 않는지는 **코드 구조상 벗어날 수 없어 보이나(각 `_check_*` 함수의 반환 형태가 고정 dict), 실측된 적이 없다.**
- 따라서 "Contract가 성공 경로에서도 지켜진다"는 주장은 **키 구조 차원에서는 강한 논리적 근거**가 있지만, **`target != None`을 포함한 전체 시나리오까지 실측으로 닫힌 것은 아니다.**

---

## 7. T5-C로 이관되는 범위

다음은 이번 문서가 다루지 않으며, 별도 트랙(T5-C)에서 GitHub 접근을
포함한 확장된 안전 조건 검토 후 다뤄야 한다:

1. 실제(비어 있지 않은) `candidate_index`를 사용해 `identify_target()`이 실제로 `target != None`을 반환하는 시나리오 관찰
2. 그 경로에서 `module_source_path()`/`build_dependency_closure()`가 실제로 로컬 파일을 읽고, 그 결과가 Stage 05의 `CheckResult` Contract를 벗어나지 않는지 확인
3. 성공 응답의 실제 content(코드/리뷰 텍스트)가 Stage 05 판정(`design_scope`, `test_execution`)에 미치는 영향 관찰

---

## 8. Architecture 및 Contract 영향

- Architecture Baseline, Development HQ Baseline — **무변경**
- `stages/contracts.py` 5개 Contract — **무변경**(이번 문서는 읽기만 함)
- Team/Stage 책임 경계 — **무변경**
- Stop Trigger 미발동(Registry/Scheduler/Runtime 일반화, 신규 Kernel Component, Architecture/Contract 변경 필요성, Team/Stage 책임 확장 — 어느 것도 관찰되지 않음)

---

## Governance Review

- 새로운 Architecture/Layer/Component/Concept 추가 — **아니오**
- Baseline 문서 변경 — **아니오**
- `docs/decisions/adc/ADC.md` 변경 — **아니오**
- ADR 필요 여부 — **아니오**
- 코드 작성·수정 — **아니오**(코드 읽기만 수행)
- RFC → ADC → ADR 절차 생략 — **아니오**

## Self Review

- 성공 경로가 "실측 검증 완료"라고 표현했는가 — **아니오**, §5/§6에서 명시적으로 "논리적 결론"과 "미검증"을 구분
- 코드 근거와 실측 근거를 구분했는가 — **예**(§2/§3은 코드 근거, §4는 실측 근거, §5가 이를 결합한 논리적 결론임을 명시)
- 기존 Evidence(`-0001`~`-0003`) 수치와 모순되는 서술이 있는가 — **아니오**, 누적 5건/성공 0건 수치를 그대로 인용
- 기존 Evidence 원문을 수정했는가 — **아니오**, 신규 문서만 작성
- 새 real Engine 호출·GitHub 접근을 시도했는가 — **아니오**
- Stop Trigger가 발동했는가 — **아니오**

## Files

`docs/research/STAGE-TO-TEAM-OPENROUTER-REAL-CALL-VALIDATION-0004.md`(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

새 작업 브랜치에서 이 문서만 커밋한다(아래 완료 보고 참조). PR 생성 여부는 별도 보고한다.
