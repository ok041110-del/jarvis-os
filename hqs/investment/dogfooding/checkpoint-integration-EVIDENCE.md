# Evidence — `checkpoint.py` Content Failure Detection 최소 통합

`projects/investment-hq-checkpoint-detection-prototype/`에서 PASS 판정된
Detection Prototype을 `hqs/investment/checkpoint.py`에 최소 통합했다.
목표는 "`run_step()`의 결과가 알려진 콘텐츠 실패 시그니처일 경우
checkpoint 저장을 차단하는 것" 하나로 제한했다.

## INPUT

- `hqs/investment/checkpoint.py`(통합 전 원본), Detection Prototype
  (`is_content_failure`, 접두어 `"API Error:"` 검사, True Positive
  1/1·False Positive 0/30으로 이미 PASS)
- 기존 3개 Team HQ Dogfooding 산출물(`aapl-hq-verify`, `pg-hq-verify`,
  `efa-2026-08`) — Resume 회귀 확인용

## EXECUTION

1. `checkpoint.py`에 `ContentFailureError`(RuntimeError 상속)와
   `_is_known_content_failure()`를 추가(Prototype 로직을 그대로 인라인,
   `projects/`를 production import로 끌어오지 않음).
2. `run_step()`에서 `fn(*args)` 호출 직후, `cp.save()` 호출 **직전**에
   시그니처 검사를 삽입 — 감지되면 저장하지 않고 예외를 발생시킨다.
3. `Checkpointer` 클래스(`has`/`load`/`save`) 자체는 한 글자도 수정하지
   않았다 — Resume 판정(`has()`)과 저장 로직은 기존 그대로다.
4. `hqs/investment/tests/test_checkpoint.py` 신규 작성(5개 케이스):
   실패 감지·저장 차단, 정상 저장, Resume(2번째 Engine 미호출), 실패 후
   재시도로 정상 복구, "capital" 같은 부분 문자열 오탐 없음.
5. `pytest --ignore=archive` 전체 실행.
6. 기존 3개 Team의 완료된 `run.py` 실행을 **동일 인자로 재실행**해
   Resume이 여전히 0.0초(재호출 없음)로 동작하는지 확인(회귀 검증 후
   `call_log.json`의 시간 필드만 재기록되는 부작용은 원상복구했다 —
   `git checkout`으로 되돌림, 실제 Evidence 수치 보존).

## OUTPUT

```
hqs/investment/tests/test_checkpoint.py::test_known_failure_blocks_save PASSED
hqs/investment/tests/test_checkpoint.py::test_success_path_saves_normally PASSED
hqs/investment/tests/test_checkpoint.py::test_resume_skips_second_engine_call PASSED
hqs/investment/tests/test_checkpoint.py::test_failed_step_is_retried_on_resume PASSED
hqs/investment/tests/test_checkpoint.py::test_partial_api_mention_is_not_false_positive PASSED
5 passed in 0.07s
```

- `pytest --ignore=archive`: **187 passed**(기존 182 + 신규 5, 실패 0)
- 기존 3개 Team 재실행(Resume 확인): `aapl-hq-verify`/`pg-hq-verify`/
  `efa-2026-08` 전부 `wave1~4_elapsed_sec: 0.0`, `pipeline_total_elapsed_sec:
  0.0` — Engine 재호출 없이 저장된 산출물을 그대로 로드함을 확인. 실행
  중 생성된 `call_log.json`의 시간 필드 갱신은 diff 확인 후 원복
  (`git status`로 `checkpoint.py` 변경분 외 아무것도 남지 않음을 확인).

## VALIDATION

- **실패 감지·저장 차단**: 알려진 시그니처 응답 시 `ContentFailureError`
  발생, `checkpoints/<step>.md` 파일 미생성, `manifest.json`의
  `completed_steps`/`call_log` 모두 변화 없음 — 직접 assert로 확인.
- **정상 저장**: 시그니처가 아닌 응답은 기존과 동일하게 저장·완료
  표시됨.
- **Resume**: 저장된 단계는 `fn`을 다시 호출하지 않고 디스크에서
  로드됨(2번째 호출에서 예외를 던지는 `fn`을 넣어 직접 증명).
- **실패 후 재시도**: 실패해 저장되지 않은 단계는 `has()`가 여전히
  False이므로, 다음 실행에서 자동으로 재시도되고 정상 응답이면
  저장된다 — 새 재시도 로직을 추가한 게 아니라 기존 Resume 동작이
  실패 케이스에도 그대로 적용됨을 확인한 것.
- **False Positive 회귀**: "capital" 같은 정상 콘텐츠는 오탐하지 않음.

## ANOMALY

없음. 통합은 Prototype이 검증한 로직 그대로였고 예상과 다른 동작은
관찰되지 않았다.

## CONCLUSION

**PASS.** `run_step()`이 알려진 콘텐츠 실패 시그니처를 저장 전에
차단하도록 최소 통합했다. `Checkpointer` 클래스, `has()`/`load()`/
`save()`, `run.py`/`teams/*.py`의 호출부는 전혀 수정하지 않았다 —
변경은 `run_step()` 함수 본문 4줄 추가와 모듈 상단 헬퍼 2개(`+26/-1`
라인)뿐이다. 재시도/알림/동시성은 설계하지 않았다(지시 범위 밖) —
실패 시 상태는 "저장되지 않고 예외가 호출자까지 전파되어 프로세스가
중단되며, 다음 실행에서 자동으로 재시도 대상이 된다"로 최소 정의했다
— 이는 기존에 이미 존재하던(예: subprocess 타임아웃 등 다른 예외의)
동작과 동일한 경로다, 새 예외 처리 프레임워크를 만들지 않았다.

### Investment HQ Freeze Blocker 해소 여부: **해소**

Freeze Review가 지목한 Blocker("`checkpoint.py`가 콘텐츠 실패를 감지해
저장을 막지 못한다")는 이번 통합으로 **동작 자체가 바뀌었다** —
이전에는 오류 텍스트가 정상 산출물처럼 저장되고 완료 처리됐지만, 이제
저장 자체가 차단되고 예외로 승격된다. `run.py`를 통해 실행하는 사용자가
수동으로 `manifest.json`을 편집해 복구할 필요가 없어졌다(재실행만
하면 됨 — 실패한 단계는 `has()`가 False이므로 자동 재시도된다).

**단, 아래는 이번 통합 범위에 포함되지 않으며 별도 Open Issue로
남는다**:
- 재시도 자동화(현재는 예외로 프로세스가 중단되고, 사용자가 수동으로
  `run.py`를 다시 실행해야 한다 — 이는 기존에도 콘텐츠 실패가 아닌
  다른 예외에서 동일했던 동작이라 새로운 제약이 아니다)
- 알림(실패했다는 사실을 사용자가 콘솔 출력/예외 메시지 외의 방법으로
  알 수단은 없다)
- 동시성 세부 조정(`ThreadPoolExecutor`로 병렬 실행 중 한 단계가
  실패하면 해당 Wave의 다른 단계들과의 상호작용은 이번에 재검토하지
  않았다 — 기존 병렬화 구조에 이미 내재된 특성이며 이번 변경으로 새로
  생긴 문제가 아니다)
- Realty Income류(세션 한도 초과) 등 원문 미보존 실패 유형은 여전히
  감지 대상이 아니다(추측 시그니처 배제 원칙 유지)

## 관찰되지 않은 것 (명시적으로 기록)

- 실제 새 콘텐츠 실패가 재현되는 상황에서 이 통합이 실전 동작하는
  모습(이번엔 단위 테스트로만 검증, 실제 `call_engine()` 오류 재현을
  기다리지 않았다 — 인위적으로 재현을 유도하지 않는다는 기존 원칙 유지)
- 병렬 Wave 안에서 한 단계가 `ContentFailureError`로 실패할 때 같은
  Wave의 나머지 `ThreadPoolExecutor` 작업이 어떻게 종료되는지(Python
  기본 동작에 위임, 별도 처리 추가하지 않음 — 검증하지 않음)

---

# Architecture/Contract 변경 여부

**없음.** `hqs/development/`, Structure v1.0, Architecture Baseline,
Development HQ Freeze, `hqs/investment/STRUCTURE.md`의 금지 사항
(Registry/Scheduler/Runtime/Engine Gateway 미구현) 어느 것도 위반하지
않았다. `Checkpointer`는 여전히 "단계 이름 → 파일 하나"라는 고정 매핑만
다루며, 동적 등록 API나 일반화된 조회 인터페이스를 추가하지 않았다.
새 RFC/ADC/ADR을 작성하지 않았다. Kernel 개념을 도입하지 않았다.
