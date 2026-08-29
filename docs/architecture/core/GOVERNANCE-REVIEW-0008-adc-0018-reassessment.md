# GOVERNANCE-REVIEW-0008: ADC-0018 재검토 — Investment HQ Wave1/2 Multi-Task Dogfooding·Failure Isolation 테스트 대조

**문서 성격**: Governance Review. **Decision 문서가 아니다.** 새 RFC/ADC/ADR을
작성하지 않는다. `ADC-0018-natural-language-request-multi-hq-task-decomposition.md`의
Decision(Defer)을 이 문서가 직접 바꾸지 않는다 — 그 ADC 자체의 재검토
조건(Re-review Trigger)에 이번 신규 Evidence가 부합하는지만 대조한다. 새
Architecture/Concept을 설계하지 않는다. **이번 검토에서 Production 코드는
한 줄도 작성하지 않았다.**

## 목적

이번 세션에서 수행된 두 건의 실제 검증 —

1. Investment HQ Wave1/2 Multi-Task 병렬 실행 안정성 검증(main 최신 기준)
2. `hqs/investment/tests/test_wave_failure_isolation.py` 신규 추가 —
   Wave1/2 내부에서 1개 Task가 `ContentFailureError`로 실패해도 나머지
   Task는 정상 완료·저장되고, Resume 시 실패한 Task만 재실행됨을
   `stock_team.run()` 실제 호출로 검증

이 두 Evidence가 `ADC-0018`(자연어 요청 → Multi-HQ Task 분해 공통 책임,
Decision: Defer (Scoped))의 재검토 조건을 충족하는지, 그리고 ADC-0018의
Decision을 바꿀 근거가 되는지 독립적으로 판단한다.

---

## 1. ADC-0018의 기존 Defer 판단과 재검토 조건 확인

`ADC-0018`은 다음을 Decision으로 확정했다:

> **C. Defer (Scoped) — 실제 Multi-HQ 자연어 요청 처리 필요가 관찰될 때까지
> 보류**

근거(§Q1·Q2): RFC-0018 §5의 Evidence("자연어 → Multi-HQ → Task 공통 계층
부재")는 사실이나 "부재 증명"일 뿐 "필요 증명"이 아니며, 실제 Multi-HQ
자연어 요청 처리 시도가 Repository 어디에도 관찰되지 않았다(관찰 0건,
Governance v2 Rule B 미충족).

ADC-0018이 명시한 **재검토를 촉발하는 조건**(§Implementation Boundary)은
다음 중 하나다:

- (A) 실제 dogfooding 또는 Production 사용 중, 하나의 자연어 요청이 복수
  HQ에 걸친 의도를 담고 있어 사람이 수작업으로 나눠 처리해야 했던 사례가
  **3건 이상** 독립적으로 관찰될 것(Rule B), 또는
- (B) ADC-0016 수준의 명확한 단일 실제 구현 사례(사람이 직접 만든 실험적
  코드가 이미 존재하고 유효성이 검증된 경우)가 나타날 것.

이 문서는 이번 세션의 두 Evidence가 (A) 또는 (B) 중 어느 하나라도
충족하는지만 판단한다.

---

## 2. 이번 Evidence를 ADC-0018의 재검토 조건과 대조

### 2.1 무엇을 검증했는가 (사실 확인)

- Wave1/2 안정성 검증: `stock_team.py`의 `run()`이 Wave1(5개 독립 분석
  Task, `ThreadPoolExecutor`)·Wave2(Bull/Bear 2개 분기, 별도
  `ThreadPoolExecutor`)를 병렬 실행하고, `Checkpointer`가 각 Step의 결과를
  개별 저장하는 실제 흐름을 main 최신 코드로 재확인했다.
- Failure Isolation 테스트(`test_wave_failure_isolation.py`, 4건 전부
  Pass): Wave1에서 `TECHNICAL_ANALYSIS` 1개만 `"API Error:"` 접두사로
  실패시켜도 나머지 4개 Task가 정상 완료·저장됨을 검증. Wave2에서도
  `BEAR_CASE` 1개 실패 시 `BULL_CASE`는 정상 저장됨을 검증. 새
  `Checkpointer`로 Resume 시 성공한 Task는 재호출되지 않고 실패한
  Task만 재호출됨을 `call_engine` 호출 횟수로 직접 검증. `manifest.json`의
  `completed_steps`/`call_log`에 중복·누락이 없음을 검증.

이 모든 대상은 **하나의 HQ(Investment HQ) 내부, 하나의 Team
(`stock_team`) 내부**에서 이미 코드/설계에 고정된 여러 Task가 병렬
실행되고 개별적으로 격리·재개되는 동작이다.

### 2.2 조건 (A) — 실제 Multi-HQ 자연어 요청 처리 필요 3건 이상 대조

**이번 두 검증 중 어느 것도 하나의 자연어 요청이 복수 HQ(Investment HQ +
Development HQ)에 걸친 의도를 담았던 사례가 아니다.** `stock_team.run()`은
호출자가 이미 `TESTCO`라는 종목 코드와 `raw_data_path`를 명시적으로
지정해 호출하는 구조이며, Investment HQ 단일 범위를 벗어나지 않는다.
Development HQ와의 경계를 넘나든 요청은 이번 세션에 전혀 없었다.

`hqs/investment/dogfooding/` 전체(`aapl-hq-verify`, `pg-hq-verify`,
`checkpoint-integration`, `conditional-freeze-round2`, `efa-2026-08`)의
"Development HQ" 언급을 재확인한 결과, 전부 "Investment HQ가 Development
HQ의 Reference Architecture를 재사용했다" 또는 "Development HQ Freeze를
수정하지 않았다"는 **구조적 비교/불변 확인** 문구였고, 하나의 자연어
요청이 두 HQ에 걸쳐 실제로 처리된 사례는 하나도 없었다.

**판단: 조건 (A) 미충족.** 관찰 수량은 이번 세션 이후에도 여전히
**0건**이다.

### 2.3 조건 (B) — ADC-0016 수준의 단일 실제 구현 사례 대조

ADC-0016이 예외적으로 Accept 근거로 삼았던 것은 "`workflow_0009.py`의
`run_comparison`이 이미 merge된 Production Code로 존재했다"는, **Task가
이미 여러 개로 고정되어 병렬 실행되는 실제 코드 자체**였다. 이번
Failure Isolation 테스트는 그 반대 방향의 Evidence다 — Task를 여러 개로
분해하는 게 아니라, **이미 분해되어 고정된 Task(§16.4 Multi-Task 범위)가
장애 상황에서도 올바르게 격리·재개된다**는 것을 검증했을 뿐이다.

자연어 요청에서 Task를 만들어내는 로직(Request Interpretation/HQ
Routing/Task Decomposition)이나 HQ 간 요청 라우팅에 해당하는 실험적
코드는 이번 검증에 전혀 등장하지 않았다.

**판단: 조건 (B) 미충족.**

---

## 3. Execution Host / Multi-Task / Result Store 검증 결과와 RFC-0018 Evidence의 구분

`ADC-0018` §Q5는 Execution Host(§16.3)·Multi-Task(§16.4)·Dev HQ Context
Analysis·§6 Runtime(ADC-02)과의 경계를 이미 명확히 분리해 두었다. 이번
Evidence를 그 경계에 맞춰 다시 분류하면:

| 이번 검증 내용 | 해당하는 기존 Governance 범위 | RFC-0018/ADC-0018과의 관계 |
|---|---|---|
| Wave1/2 `ThreadPoolExecutor` 병렬 실행, 실패 격리 | Multi-Task(§16.4, ADC-0016) | **무관** — 이미 Accept된 "고정된 Task 병렬 실행" 범위의 신뢰도를 보강할 뿐, "자연어 → Task 분해" 필요성과는 층위가 다르다 |
| `Checkpointer` 저장 경계, `ContentFailureError` 차단 | Result Store Integrity(§16.5, ADC-0017) | **무관** — 저장 무결성 검증이며, HQ 간 라우팅과 무관 |
| `stock_team.run()`이 호출자로부터 이미 구조화된 인자(`ticker`, `raw_data_path`)를 받는 구조 | Q1의 "이미 구조화된 입력을 전제"라는 기존 관찰과 동일 패턴 재확인 | RFC-0018 §5의 기존 관찰(자연어 → 구조화 변환 계층 부재)을 **강화**하되, 새로운 사실을 추가하지 않는다 |

즉 이번 검증은 **Multi-Task(§16.4)와 Result Store(§16.5)가 이미 Accept된
범위 안에서 잘 작동함을 재확인**한 것이지, RFC-0018/ADC-0018이 다루는
"자연어 요청 → Multi-HQ Task 분해 공통 책임"의 필요성을 입증하는
Evidence가 아니다. 이 둘을 같은 것으로 취급하면 §Q5가 이미 분리해 둔
경계(§16.4 자체와 "§16.4에 전달될 입력을 만드는 단계"의 구분)를 무너뜨리게
된다 — 이 문서는 그 혼동을 피한다.

---

## 4. 실제 Multi-HQ 자연어 요청 사례 재확인

`docs/research/`, 양 HQ의 `dogfooding/`, 그리고 이번 세션에서 새로 추가된
`hqs/investment/tests/test_wave_failure_isolation.py`를 포함한 전체 변경
범위를 다시 확인했다. **하나의 자연어 요청이 Investment HQ와 Development
HQ에 걸쳐 실제로 처리된 사례는 이번에도 없다.** ADC-0018 작성 시점의
관찰(0건)과 비교해 변화가 없다.

---

## 5. Decision — Defer 유지 여부 독립 판단

### 검토

- 조건 (A)·(B) 모두 미충족(§2).
- 이번 Evidence는 Multi-Task(§16.4)·Result Store(§16.5)의 **기존 Accept
  범위**를 보강하는 것이지, RFC-0018/ADC-0018이 다루는 **Multi-HQ 자연어
  요청 분해**라는 별개 책임의 필요성과는 무관하다(§3).
- ADC-0018이 "부재 증명"과 "필요 증명"을 구분했던 논리(§Q1)가 이번에도
  그대로 유지된다 — Investment HQ 내부에서 Task가 잘 격리·재개된다는
  사실은 "HQ 간 자연어 요청 분해가 필요하다"는 사실을 전혀 함의하지
  않는다.

### 판단

**ADC-0018의 Decision(Defer (Scoped))을 그대로 유지한다.** 이번
Investment HQ Dogfooding·Failure Isolation 검증은 재검토를 촉발할 만한
새로운 Evidence가 아니다 — 무관한 범위(§16.4/§16.5)의 신뢰도 보강일 뿐,
RFC-0018/ADC-0018의 Boundary Question에 대해서는 여전히 관찰 **0건**이다.

이 판단은 ADC-0018의 결론을 단순 반복한 것이 아니라, 이번에 실제로
수행된 두 검증을 재검토 조건(A)·(B)에 개별 대조해 **독립적으로 재확인**한
결과다.

---

## 6. Decision 불변에 따른 조치

Decision이 바뀌지 않았으므로:

- `BASELINE.md`·`IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`
  어느 것도 갱신하지 않는다.
- 새 ADR을 작성하지 않는다.
- `ADC-0018` 문서 자체를 수정하지 않는다 — 이 재검토는 별도 Governance
  Review 문서로 남기고, ADC-0018 원문은 그대로 둔다(재검토 이력은 이
  문서가 담당).
- Production Code는 이번에도 수정하지 않는다.

---

## 7. 다음 단계

1. 이번 재검토 결과(Defer 유지)를 사용자에게 보고한다.
2. 향후 Investment HQ 또는 Development HQ에서 실제로 하나의 자연어
   요청이 두 HQ에 걸친 의도를 담아 사람이 수작업으로 나눠 처리해야 했던
   사례가 발생하면, ADC-0018의 재검토 조건(A)에 따라 그 사례를 명시적으로
   기록하고 누적한다.
3. RFC-0018 브랜치(`claude/rfc-0018-multi-hq-task-decomposition`)는 아직
   main에 병합되지 않았다 — 이 재검토 문서는 그 브랜치 위에서 이어지는
   동일 작업 단위로 취급하며, 별도 신규 브랜치를 만들지 않는다.
4. PR 생성은 이번 단계에서 수행하지 않는다(사용자 지시).

---

## Self Review

- ADC-0018의 기존 Decision을 반복 서술만 하지 않고, 재검토 조건(A)·(B)에
  이번 신규 Evidence를 개별 대조했는가 — **Pass**(§2).
- Execution Host/Multi-Task/Result Store 검증 결과를 RFC-0018/ADC-0018의
  Evidence와 혼동하지 않았는가 — **Pass**, §3에서 표로 명시적으로 분리.
- 실제 Multi-HQ 자연어 요청 사례가 있었는지 재확인하고, 없으면 없다고
  명시했는가 — **Pass**(§4, 관찰 0건).
- Accept/Defer/Reject 중 하나를 독립적으로 판단했는가 — **Pass**(§5,
  Defer 유지).
- Decision이 바뀌지 않았으므로 Baseline/ADR을 변경하지 않았는가 —
  **Pass**(§6).
- Production Code를 수정했는가 — **아니오**.
- 새로운 Architecture/Concept을 설계했는가 — **아니오**.
