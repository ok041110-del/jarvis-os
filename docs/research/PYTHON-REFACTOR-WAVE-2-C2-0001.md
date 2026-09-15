# Python Refactor Wave 2 — C2 Implementation: `auto_selection_client.py`

**Governance 근거**: `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`
§10.2/§12(C2)/§14 — Wave 2 Audit이 P1 `DUPLICATION`, `WAVE 2 IMPLEMENT`
1순위로 확정한 후보의 실제 구현 Evidence다. 이번 커밋은 **C2 하나만**
대상으로 하며, C1(`investment/teams/*.py`)은 건드리지 않는다.

## 1. Problem

`projects/openrouter-auto-selection-v1/domain/auto_selection_client.py::call_with_auto_selection`(133 LOC)은
전송 실패/빈 응답/Contract 실패/성공 4갈래 분기마다 `AutoSelectionAttempt`
(11개 필드) 생성 코드가 거의 그대로 반복돼, 함수의 실제 의도(재시도
정책)를 읽으려면 매번 같은 10줄짜리 dataclass 생성 코드를 건너뛰어야
했다(Wave 2 Audit §5/§10.2).

## 2. Before Structure

```
for attempt_number in 1..max_retries+1:
    call_result = _single_call(...)
    failure_class = classify_failure(call_result)

    if failure_class:                              # 분기 A: 전송/HTTP 실패
        attempts.append(AutoSelectionAttempt(...))  # 11필드 인라인 생성
        break-or-continue

    content = parsed에서 추출 시도

    if not content:                                 # 분기 B: 빈 응답
        attempts.append(AutoSelectionAttempt(...))  # 11필드 인라인 생성(A와 유사)
        current_pool = (인라인 pool 제외 로직)
        break-or-continue

    contract_result = output_contract(content)
    if not contract_result.passed:                  # 분기 C: Contract 실패
        attempts.append(AutoSelectionAttempt(...))  # 11필드 인라인 생성(B와 거의 동일)
        current_pool = (인라인 pool 제외 로직, B와 동일 코드)
        break-or-continue

    # 분기 D: 성공
    attempts.append(AutoSelectionAttempt(...))       # 11필드 인라인 생성
    return AutoSelectionResult(success=True, ...)

return AutoSelectionResult(success=False, ...)       # 루프 소진
```

각 분기의 semantic responsibility:

- **분기 A(전송/HTTP 실패)**: 재시도 가능 여부 판정 + 실패 기록.
- **분기 B(빈 응답)**: 실패 기록 + 실패 모델을 Pool에서 제외(정책적).
- **분기 C(Contract 실패)**: 실패 기록 + 실패 모델을 Pool에서 제외
  (B와 정책 동일, 실패 사유만 다름).
- **분기 D(성공)**: 성공 기록 + 즉시 반환.

반복 코드는 두 갈래였다: (1) `AutoSelectionAttempt` 생성(4곳 모두),
(2) Pool 제외 로직(B, C 2곳 완전히 동일한 3줄).

## 3. Refactoring Decision

- **`_record_attempt(...)`**: `attempts.append(AutoSelectionAttempt(...))`를
  대체하는 private helper. 4개 분기에서 달라지는 값(선택 모델/원문/
  failure_class/error_detail/contract 판정)만 키워드 인자로 받고,
  `call_result`에서 공통으로 뽑히는 `http_status`/`api_latency_ms`는
  helper 내부에서 한 번만 처리한다. 이름 자체가 "이번 시도 결과를
  기록한다"는 의미를 그대로 전달한다 — 단순 1줄 wrapper가 아니라
  11개 필드 조립이라는 실제 semantic unit이다.
- **`_exclude_model_if_configured(...)`**: B/C에서 완전히 동일하던
  3줄("설정이 켜져 있고 Pool에 있으면 제외")을 대체하는 순수 함수.
  반환값을 그대로 `current_pool`에 대입하는 방식으로 원래 로직과
  동일하게 유지했다.
- **채택하지 않은 방향**: 재시도 루프 자체를 여러 함수로 쪼개는 방향은
  시도하지 않았다 — `current_pool`/`attempts`/`overall_start` 등
  루프 상태를 여러 함수에 걸쳐 전달해야 해서 오히려 Cognitive Load가
  늘어난다고 판단했다(Wave 2 Audit §10.2의 재검토 결론과 일치). 함수
  분리가 아니라 반복되는 **결과 기록 코드의 통합**만 적용했다.

## 4. After Structure

```
def _record_attempt(attempts, *, attempt_number, models_offered, call_result,
                     selected_model=None, raw_content=None, usage=None,
                     failure_class=None, error_detail=None,
                     contract_passed=None, contract_detail=None) -> None:
    attempts.append(AutoSelectionAttempt(...))   # 공통 조립 1곳

def _exclude_model_if_configured(pool, model, exclude) -> tuple[str, ...]:
    ...                                          # 공통 Pool 제외 1곳

def call_with_auto_selection(...):
    for attempt_number in 1..max_retries+1:
        call_result = _single_call(...)
        failure_class = classify_failure(call_result)

        if failure_class:
            _record_attempt(attempts, ..., failure_class=failure_class, error_detail=...)
            break-or-continue

        ... content 추출 ...

        if not content:
            _record_attempt(attempts, ..., failure_class="empty_response", error_detail=...)
            current_pool = _exclude_model_if_configured(current_pool, selected_model, exclude_failed_model_from_retry_pool)
            break-or-continue

        contract_result = output_contract(content)
        if not contract_result.passed:
            _record_attempt(attempts, ..., failure_class="contract_failure", contract_passed=False, contract_detail=...)
            current_pool = _exclude_model_if_configured(current_pool, selected_model, exclude_failed_model_from_retry_pool)
            break-or-continue

        _record_attempt(attempts, ..., contract_passed=True, contract_detail=...)  # 성공
        return AutoSelectionResult(success=True, ...)

    return AutoSelectionResult(success=False, ...)
```

각 분기는 이제 "무엇이 실패/성공했는지 + 그에 따른 정책(재시도/제외
여부)"만 남고, 필드 조립 상세는 `_record_attempt`로 격리됐다.

## 5. Behavior Preservation

- **retry 횟수/순서**: `for attempt_number in range(1, max_retries + 2)`
  루프, `break`/`continue` 조건문 전부 원본 그대로 유지 — 텍스트
  변경 없음.
- **model selection/exclusion semantics**: `_exclude_model_if_configured`는
  원본의 `if exclude_failed_model_from_retry_pool and selected_model in current_pool: current_pool = tuple(...)`를
  그대로 함수로 옮긴 것이며, 조건·결과 값이 1:1 동일하다.
- **실패 분류 의미**: `classify_failure`, `_RETRYABLE_FAILURE_CLASSES`,
  `_NON_RETRYABLE_FAILURE_CLASSES`는 손대지 않았다.
- **필드 값**: `http_status`는 원본이 분기별로 `.get()`/`[...]`를
  혼용했으나 `_single_call`이 모든 경로에서 `"http_status"`/
  `"elapsed_ms"` 키를 항상 채워 반환하므로(§2 코드 확인) 두 접근
  방식은 동일한 값을 낸다 — 관측 가능한 차이 없음.
- **return schema**: `AutoSelectionResult`/`AutoSelectionAttempt`
  dataclass 정의는 1바이트도 변경하지 않았다.
- **exception semantics**: 새 `try`/`except` 없음, 기존 예외 경로
  무변경.
- **public function signature**: `call_with_auto_selection`의 인자
  목록·기본값·keyword-only 여부 무변경. `classify_failure`도 무변경.
- **외부 dependency/import**: 무변경(§7에서 diff로 재확인).

## 6. Tests

- 기존 전용 테스트(`projects/openrouter-auto-selection-v1/tests/test_auto_selection_harness.py`,
  15개)를 리팩터링 전/후 각각 실행 — **15 passed, 변화 없음**. 이
  테스트는 이미 성공/재시도 성공/최종 실패/Contract 실패 시 Pool
  제외/시간순 attempts 기록을 모두 커버한다(§9 항목 4, 6, 7).
- 리팩터링이 순수 내부 구조 변경(동일 입력 → 동일 출력)이고 기존
  테스트가 이미 success/retry-success/final-failure/pool-exclusion/
  attempt-ordering을 실제 위험 지점으로 커버하고 있어, **신규
  회귀 테스트는 추가하지 않았다** — 기존 테스트의 behavior도
  변경하지 않았다(assert 문 1개도 수정하지 않음, `git diff`로 확인).

## 7. Validation

| 항목 | 결과 |
|---|---|
| Targeted tests(`projects/openrouter-auto-selection-v1/tests/`) | **15 passed**(변경 전/후 동일) |
| `hqs/` 전체 pytest | **380 passed, 6 skipped**(Wave 2 Audit baseline과 동일, 회귀 없음) |
| `python3 -m py_compile`(대상 파일) | 오류 0건 |
| `ast.parse()`(대상 파일) | 오류 0건 |
| `git diff` 범위 | `auto_selection_client.py` **1개 파일만** 변경(§8에서 재확인) |
| Contract 검사 | `AutoSelectionAttempt`/`AutoSelectionResult` 필드, `call_with_auto_selection` 시그니처 무변경 |

실패 0건 — regression/기존 failure/environment failure 구분이 필요한
사례 자체가 발생하지 않았다.

## 8. Architecture/Contract Check

- **대상 파일 외 변경**: 0건(`git diff --stat` 결과 1 file changed).
- **public API 변경**: 0건 — `call_with_auto_selection`/`classify_failure`
  시그니처 무변경, 신규 함수(`_record_attempt`, `_exclude_model_if_configured`)는
  모두 `_` prefix로 module-private.
- **return schema 변경**: 0건 — 두 dataclass 정의 무변경.
- **exception behavior 변경**: 0건 — 신규/삭제된 `try`/`except` 없음.
- **retry behavior 변경**: 0건 — 루프 범위·`break`/`continue` 조건
  전부 원문 그대로.
- **dependency/import 변경**: 0건(`import json/time/urllib...` 등
  기존 import 목록 무변경, 신규 import 없음).
- **Architecture/Governance**: 무변경. Engine boundary/OpenRouter
  Contract/Stage-Team 책임에 영향 없음.

## 9. Conclusion

Wave 2 Audit이 C2로 확정한 "반복되는 결과 기록 코드"를
`_record_attempt`/`_exclude_model_if_configured` 두 개의 semantic
helper로 통합했다. `call_with_auto_selection`의 top-level 흐름은
이제 각 분기에서 "무엇이 실패/성공했는가 + 그에 따른 정책"만
드러내고, 11개 필드 dataclass 조립이라는 bookkeeping은 한 곳에
격리됐다. 인자 시그니처·반환 schema·재시도/제외 정책·예외 처리는
모두 동일하게 유지됐으며, 전용 테스트 15개와 `hqs/` 전체 380
passed/6 skipped로 무회귀를 확인했다. C1(`investment/teams`)은
이번 커밋에서 다루지 않았다.

## Related

- `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`(§10.2, §12 C2, §14)
- `projects/openrouter-auto-selection-v1/tests/test_auto_selection_harness.py`
