# Evidence — Investment HQ `checkpoint.py` 콘텐츠 검증 격차: 최소 Detection Prototype

Investment HQ v1.0 Freeze Review에서 확인된 Freeze Blocker(`hqs/investment/
checkpoint.py`가 "완료"와 "성공"을 구분하지 못함)에 대해, **"콘텐츠 실패를
Checkpoint 저장 전에 감지할 수 있는가"** 하나만 검증하는 최소 Prototype이다.
`checkpoint.py` 자체는 수정하지 않았다 — 이 Prototype을 실제 저장 경로에
연결(wiring)할지, `checkpoint.py`의 본 구현을 어떻게 바꿀지는 별도 판단
대상으로 남긴다.

## INPUT

- `hqs/investment/checkpoint.py` 원문 확인: `Checkpointer.has(step)`은
  `manifest["completed_steps"]`에 `step` 이름이 있는지만 확인하고,
  `run_step()`은 `fn(*args)`(사실상 `call_engine()`)의 반환값을 내용
  검증 없이 그대로 `cp.save()`에 전달한다. `call_engine()`
  (`hqs/development/mvp/engine.py`)은 `subprocess.run()`의 `stdout`을
  예외 없이 그대로 반환하므로, API 오류 텍스트도 "정상 응답"과 동일한
  경로로 저장·완료 처리된다.
- 실제 관찰된 실패 시그니처 확인: `pg-hq-verify` 1차 시도에서 이 세션이
  `cat synthesis.md`로 직접 확인한 문자열과, `efa-2026-08/EVIDENCE.md`에
  인용된 문자열이 토씨 하나 다르지 않게 동일함 —
  `"API Error: Unable to connect to API: Self-signed certificate detected.
  Check your proxy or corporate SSL certificates"`. 다른 실패 유형
  (Realty Income의 "세션 사용 한도 초과")은 EVIDENCE.md에 요약 문장으로만
  남아 있고 원문이 보존되지 않아 이번 감지 대상에서 제외했다(추측 기반
  시그니처를 추가하지 않는다는 지시를 따름).

## EXECUTION

- `projects/investment-hq-checkpoint-detection-prototype/`에 독립 모듈
  생성(`hqs/investment/`, `hqs/development/`는 건드리지 않음):
  - `detect_content_failure.py`: `is_content_failure(output)` 함수 하나.
    관찰된 시그니처의 **접두어**(`"API Error:"`)로 시작하는지만 검사한다
    (부분 문자열 검사가 아닌 이유: 기존 checkpoint 파일 중 일부가 본문에
    "capital" 등 "api"를 부분 문자열로 포함하고 있어, 부분 문자열 검사는
    오탐 가능성이 있었다 — 아래 VALIDATION 참조).
  - `test_detection.py`: (1) 재구성된 실제 관찰 텍스트에 대해 True
    Positive를 확인하고, (2) 기존 3개 Team HQ Dogfooding(`aapl-hq-verify`,
    `pg-hq-verify`, `efa-2026-08`)의 실제 checkpoint 파일 30개 전부에
    대해 False Positive가 없는지 확인한다.
- `python3 projects/investment-hq-checkpoint-detection-prototype/test_detection.py` 실행.
- Prototype 추가 전/후 `pytest --ignore=archive` 실행해 회귀 확인.

## OUTPUT

```
checked 30 real checkpoint files across 3 dirs
PASS — true positive 1/1, false positive 0/30
```

- `pytest --ignore=archive`: Prototype 추가 전 182 passed → 추가 후 182
  passed(변화 없음, 기존 코드를 전혀 수정하지 않았으므로 당연한 결과).

## VALIDATION

- **True Positive**: 실제 2회 재현(EFA, PG)에서 동일하게 관찰된 시그니처를
  100% 감지.
- **False Positive**: 기존 검증된 정상 산출물(3개 Team, 30개 checkpoint
  파일, `bear_case.md`/`macro_analysis.md`/`performance_risk_analysis.md`
  등 본문에 "API"라는 단어가 포함된 파일 5건 포함) 전부에서 오탐 0건.
  사전 점검(`grep -rli api`)으로 "capital" 같은 단어가 "api"를 부분
  문자열로 포함함을 확인했고, 이 때문에 부분 문자열 검사 대신 접두어
  검사를 채택했다 — 이 설계 결정 자체가 실제 데이터로 검증됨.

## ANOMALY

없음. 감지 로직은 단순 문자열 접두어 비교이며, 예상대로 동작했다.

## CONCLUSION

**PASS.** "콘텐츠 실패를 Checkpoint 저장 전에 감지할 수 있는가"라는 좁은
질문에 한해, 최소 구현(문자열 접두어 검사)으로 실제 관찰된 실패 유형을
안정적으로 감지할 수 있고, 실제 정상 산출물 30건에 대해 오탐이 없음을
확인했다. **탐지의 기술적 실현 가능성(Feasibility)은 확인됐다.**

### Freeze Blocker 해소 여부 — 부분 해소, 완전 해소 아님

이 Prototype은 "감지가 가능한가"라는 **불확실성**만 해소했다. Investment
HQ v1.0 Freeze Review가 지목한 Blocker는 "`checkpoint.py`가 실제로
콘텐츠 실패를 감지해 저장을 막지 못한다"는 **현재 동작**이었고, 이
Prototype은 `checkpoint.py`를 수정하지 않았으므로 **그 동작 자체는
아직 바뀌지 않았다** — 지시(#6)에 따라 본 구현 연결은 이번 범위 밖으로
남긴다. 즉:

- 해소됨: "감지가 기술적으로 가능한가"에 대한 불확실성.
- 해소되지 않음: `checkpoint.py`/`run_step()`에 실제로 연결해 저장을
  차단하는 본 구현 여부 — 이는 별도 판단·별도 세션 대상이다.

## 관찰되지 않은 것 (명시적으로 기록)

- 감지 후 실제 동작(예외로 승격 vs 재시도 vs 사용자 알림) — 이번
  Prototype은 감지 여부만 확인했고 사후 처리 정책은 설계하지 않았다.
- Realty Income류(세션 한도 초과) 등 원문이 보존되지 않은 다른 실패
  유형에 대한 감지 가능성 — 이번엔 검증하지 않았다(추측 시그니처
  배제 원칙).
- `checkpoint.py` 실제 연결 시 동시성(Lock)·재시도 횟수 등 본 구현
  범위의 설계 — 다루지 않았다.

---

# Architecture/Contract 변경 여부

**없음.** `hqs/investment/checkpoint.py`, `hqs/development/`, Structure
v1.0, Architecture Baseline, Development HQ Freeze 어느 것도 수정하지
않았다. 새 RFC/ADC/ADR을 작성하지 않았다. Kernel 개념을 도입하지
않았다. 이 Prototype은 `projects/` 아래 독립 모듈 2개(`detect_content_
failure.py`, `test_detection.py`)와 이 EVIDENCE.md만 추가했다.
