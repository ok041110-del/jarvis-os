# ADC-0017: Multi-Task Result Store/Checkpointer Integrity Boundary 존재 여부 판단 (RFC-0017 후속)

## 목적

`docs/architecture/core/RFC-0017-multi-task-checkpointer-integrity-boundary.md`
§5 Boundary Question — **"Multi-Task가 공유하는 Result Store
(Checkpointer)에, 저장되는 결과의 유효성·무결성을 보장하는 책임을
Execution Host(§16.3)·Multi-Task(§16.4)와 별개의 Kernel Concept 또는
그 두 책임에 속한 하위 의무로 Accept하는가?"** — 에 대해 판단한다.

근거는 RFC-0017과 그것이 인용한 Evidence(`hqs/investment/checkpoint.py`,
세 Team 파일, `hqs/investment/tests/test_checkpoint.py`,
`hqs/investment/dogfooding/pg-hq-verify/EVIDENCE.md`,
`hqs/investment/dogfooding/efa-2026-08/EVIDENCE.md`)로만 한정하되,
RFC-0017 §3이 요구한 "Engine 호출 계층 문제 가능성의 독립 검토"를 위해
`hqs/investment/engine_client.py`, `hqs/development/mvp/engine.py`,
`docs/research/PHASE4-HQ-CROSS-VALIDATION-0001.md`를 추가로 확인한다.
새로운 실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- 저장 전 검증·Resume 재검증의 구체적 구현 방법(시그니처 목록 확장,
  스키마 검증 등) — RFC-0017 §6이 이미 질문 후보로만 남겼다.
- `call_engine()`(`hqs/development/mvp/engine.py`) 자체의 수정 —
  Dev HQ 개선 후보 트랙(`efa-2026-08/EVIDENCE.md` §DEV_HQ_FEEDBACK)의
  몫이며, 이 ADC는 그 트랙을 대체하지 않는다.
- Execution Host(§16.3)·Multi-Task(§16.4)의 존재·명칭·범위 재론.
- Scheduler, 우선순위, Workflow orchestration, §6 넓은 Runtime.
- 새 Component/Interface 확정.
- Retry/Resume의 자동화 정책(재시도 횟수, backoff, 알림) 설계.
- Production Code(`hqs/`, `core/`, `dashboard/`) 수정.

이 ADC가 판단하는 것은 여섯이다: **(1) RFC-0017 §5가 좁힌 범위 —
저장 결과의 유효성·무결성 보장 책임의 존재 여부, (2) 그 근본 원인이
Result Store 설계 문제인지 Engine 호출 계층 문제인지, (3) 저장 전
검증과 Resume 재검증의 우선순위, (4) Retry/Resume 책임 경계를 과도하지
않은 범위에서 어디까지 명시할지, (5) Execution Host·Multi-Task와의
경계, (6) 이 Accept가 Investment HQ에 국한된 관찰이라는 것의 의미.**

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가

### Evidence

- `BASELINE.md` §16.4(Multi-Task, Accept Scoped·Conditional)는
  Data/Artifact Isolation을 최소 안전조건으로만 요구했을 뿐, "저장된
  결과의 유효성"이라는 하위 질문을 스스로 예견하지 않았다.
- RFC-0016 §4가 나열한 5개 위험 중 어디에도 "저장 판정 로직 자체의
  정합성"이라는 항목은 없다.

### Q0 결론

Intent는 "동시 실행 결과의 저장에 관한 무언가가 더 필요할 수 있다"는
신호조차 없었다 — 이 질문은 순수하게 사후 관찰(§Q1)에서 나왔다.
**Architecture Intent만으로는 지금 판단할 수 없다.**

---

## Q1. 실제 필요성 — `pg-hq-verify`가 보여주는 것

### Evidence

`hqs/investment/dogfooding/pg-hq-verify/EVIDENCE.md`의 CONTENT_FAILURE·
FAILURE_CAUSE 절이 실제 Production 실행(이미 `main`에 존재)으로 다음을
보여준다.

1. Synthesis 호출이 콘텐츠 레벨 실패(`"API Error: ..."`, 118자)를
   반환했으나 `_is_known_content_failure()`를 통과해 `synthesis.md`에
   정상 산출물처럼 저장됐다.
2. 손상된 Synthesis가 Final Report Writer 입력으로 그대로 전파돼
   최종 산출물 품질이 저하됐다(목표 단어 수 초과, 핵심 수치 2건 누락 —
   `EVIDENCE.md` §QUALITY).
3. 재실행(Resume)은 `manifest.json["completed_steps"]`에 이미 기록된
   `"synthesis"`를 신뢰해 손상된 값을 그대로 반환했다 — Engine을 다시
   호출하지 않았다.
4. 복구는 사람이 `manifest.json`을 수동 편집(`completed_steps`에서
   `synthesis`/`final_report` 제거)하고 해당 `.md` 파일을 삭제해야만
   가능했다.

### Q1 결론

이 관찰이 답하는 질문은 RFC-0017 §5가 좁힌 그대로다: **"저장 전에
결과를 판별하지 않으면, 그 판별 실패가 Resume을 거쳐 하위 Task까지
전파되고 사람의 수동 개입 없이는 복구되지 않는다."** 이 좁은 질문에
한해서는, 실제 Production 실행 1건(재구성하면 §Q2의 4건)이 필요성을
직접 보여준다.

---

## Q2. Evidence 수량 — Rule B 충족 여부

### 검토

`ADC-0016`(RFC-0016 후속)은 관찰이 1건뿐이어서 Governance v2 Rule B(3건
이상 독립 관찰) 기준에 크게 못 미쳤음에도, 범위를 좁히고 조건을
이월하는 방식으로 Accept까지 나아갔다. 이 ADC의 상황은 다르다 — 같은
실패 시그니처(`"API Error: Unable to connect to API: Self-signed
certificate detected..."`)가 **서로 다른 4개 실행 맥락**에서 재현됐다.

| 회차 | 맥락 | Investment HQ Multi-Task 경로인가 |
|---|---|---|
| 1회(PR #80, Nestlé) | project-local Dogfooding(Investment HQ 이전) | 아니오 |
| 2회(PR #81, Realty Income) | 동일(원인은 세션 한도, 시그니처는 다름) | 아니오 |
| 3회(`efa-2026-08`, ETF Team) | `run.py` 경유, Investment HQ MVP | 예(Wave3 Synthesis, 순차 구간) |
| 4회(`pg-hq-verify`, Dividend Stock Team) | `run.py` 경유, Investment HQ MVP | 예(Wave3 Synthesis, 순차 구간) |

### Q2 결론

**Rule B(3건 이상 독립 관찰)를 형식적으로 충족한다** — 4회 재현, 그중
2회는 Investment HQ MVP 경로 자체에서, 2회는 그 이전 project-local
경로에서 나왔다. 사용자 지시(작업 지시 §9)가 명시한 대로, 필요성이
Evidence로 충분히 뒷받침되는 이 상황에서 Evidence 부족을 이유로 Defer할
근거가 없다 — 오히려 ADC-0016보다 더 많은 독립 관찰을 갖고 있다. 다만
4건 전부가 **동일한 근본 원인**(아래 §Q3)에서 비롯됐다는 것은 "서로
다른 원인의 독립 관찰 다수"와는 성격이 다르다는 점을 Decision에 반영해야
한다.

---

## Q3. 근본 원인 — Result Store 문제인가, Engine 호출 계층 문제인가 (독립 검토)

### 검토

RFC-0017 §Out of Scope는 이 판단을 후속 ADC(이 ADC)로 명시적으로
위임했다. 두 계층을 분리해서 본다.

**Engine 호출 계층(`call_engine()`)의 구조**:

```python
def call_engine(prompt: str) -> str:
    result = subprocess.run([...], capture_output=True, text=True,
                             timeout=ENGINE_TIMEOUT_SECONDS, cwd=...)
    return result.stdout
```

`hqs/development/mvp/engine.py:23-38`이 정의하고,
`hqs/investment/engine_client.py`가 새 Adapter 없이 그대로 재사용하는
이 함수는 `result.returncode`나 `result.stderr`를 전혀 확인하지 않고
`stdout`을 무조건 반환한다 — CLI 프로세스 수준에서 이미 성공/실패를
구분할 수 있는 정보가 있음에도, `call_engine()`은 그 구분을 호출자에게
넘기지 않고 폐기한다.

**4건의 재현이 가리키는 공통점**: `docs/research/
PHASE4-HQ-CROSS-VALIDATION-0001.md`가 확인한 대로 `Checkpointer`는
`hqs/development/mvp/`에 존재한 적이 없다 — Investment HQ가
`projects/dev-hq-timeout-recovery-prototype`(PR #76 기원)에서 그대로
가져온 Investment HQ 전용 컴포넌트다. 그런데 1·2회차(PR #80/#81)는
Investment HQ도 `Checkpointer`도 없던 시점의 project-local
Dogfooding에서 **이미** 관찰됐다. 즉 콘텐츠 레벨 실패가 감지되지 않는
근본 원인은 `Checkpointer`가 존재하기 전부터 `call_engine()` 자체에
있었다 — `efa-2026-08/EVIDENCE.md`의 DEV_HQ_ISSUES 절이 이를 명시적으로
"Dev HQ 문제 — Invest HQ가 새로 만든 문제가 아니다"로 이미 판정했고,
같은 문서의 REPRODUCTION_COUNT/DEV_HQ_FEEDBACK 절은 이 시점(3회째)에
이미 "Failure Detection을 Dev HQ 개선 후보로 격상, Prototype 필요"로
판단을 내려놓았다.

**그러나 이 ADC가 다루는 질문은 원인 규명이 아니라 봉쇄(containment)
책임이다**: `call_engine()`이 실패를 구분해 반환하지 않는다는 사실은
그대로 두더라도, **그 반환값을 디스크에 영구히 남길지 결정하는 지점은
Result Store(Checkpointer) 하나뿐**이다 — `run_step()`이 `cp.save()`를
호출하기 전이 유일한 게이트다. Engine 호출 계층의 결함이 해소되기
전까지, Result Store가 이 게이트 역할을 하지 않으면 결함이 그대로
영속화되고 Resume을 통해 계속 전파된다.

### Q3 결론

**근본 원인(Root Cause)은 Engine 호출 계층(`call_engine()`)에 있다 —
이는 Result Store 설계의 결함이 아니며, 이미 Dev HQ 개선 후보로
공식 격상돼 있다(`efa-2026-08/EVIDENCE.md` §DEV_HQ_FEEDBACK).** 이 ADC는
그 판단을 재확인할 뿐 새로 결정하지 않는다. 다만 근본 원인의 소재와
별개로, **저장 여부를 결정하는 게이트 책임은 구조적으로 Result Store
쪽에만 위치한다** — 이 게이트 책임의 존재 여부가 §Q1이 확인한 실제
필요성의 대상이며, Decision은 이 좁은 게이트 책임에만 한정한다(§Decision).

---

## Q4. Execution Host·Multi-Task와의 경계

### 검토

§Q3이 확인한 대로, 4회 재현 중 2건(PR #80/#81)은 Multi-Task가 존재하기
전에 발생했고, Investment HQ 안에서 재현된 2건(EFA, PG)도 모두 **Wave3
(Synthesis)** — `run_step()` 단독 호출, `ThreadPoolExecutor`가 관여하지
않는 순차 구간 — 에서 일어났다. Wave1(5~7개 동시 분석)·Wave2(Bull/Bear
동시)에서는 이 실패가 한 번도 재현되지 않았다.

### Q4 결론

**이 책임은 Multi-Task 전용이 아니다.** 동시 실행(Coordination) 여부와
무관하게 Result Store가 어떤 호출 방식(순차·동시)으로든 결과를 저장하는
모든 지점에 적용되는 더 일반적인 책임이다. 따라서:

- Execution Host(§16.3)의 Execution Isolation 책임은 전혀 관련이 없다
  (변경하지 않는다).
- Multi-Task(§16.4)의 Coordination·실패 격리 책임도 변경하지 않는다 —
  `pg-hq-verify`에서도 실패 격리는 정상 동작했다(다른 Task들은 영향받지
  않고 정상 완료됨). 손상된 것은 저장 판정 로직이지 Task 간 격리가
  아니다.
- 이 Accept가 성립한다면, 그 대상은 Multi-Task가 아니라 **Multi-Task와
  Wave3/Wave4 순차 구간이 공유하는 Result Store(Checkpointer)** 그
  자체다 — Multi-Task는 이 Result Store를 사용하는 여러 호출자 중
  하나일 뿐이다.

---

## Q5. 저장 전 검증과 Resume 재검증의 우선순위

### 검토

RFC-0017 §6이 질문 후보로만 남긴 두 지점을, 이 ADC는 구현 방법이 아니라
**우선순위**만 판단한다.

- **저장 전 검증**: `run_step()`이 `cp.save()`를 호출하기 **전** 결과의
  유효성을 판단하는 지점. 판단 대상은 항상 방금 생성된 단일 결과 하나뿐
  이며, 실패 시 저장 자체를 막으므로 손상이 디스크에 전혀 남지 않는다 —
  `pg-hq-verify`의 실제 피해(하위 Task로의 전파, 수동 복구 필요)가
  발생할 원천 자체를 차단한다.
- **Resume 재검증**: `Checkpointer.has(step)`이 재개 시점에 **이미
  저장된** 콘텐츠를 다시 검사하는 지점. 판단 대상이 임의 시점에 임의
  경로로 쌓인 과거 데이터 전체이며, "무엇을 무효로 볼지"의 기준이 저장
  전 검증과 달라질 수 있다(당시엔 유효했던 것이 이후 기준으로 무효가
  될 수 있는가 등 새로운 질문을 만든다). 저장 전 검증이 실제로 동작하면
  Resume 시점에 무효한 콘텐츠가 존재할 여지 자체가 줄어든다.

### Q5 결론

**저장 전 검증이 우선순위가 높다.** 손상을 원천 차단하는 지점이 손상을
사후 발견하는 지점보다 구조적으로 더 적은 범위(단일 결과)만 판단하면
되고, `pg-hq-verify` 피해의 실제 발생 경로(저장 실패 → Resume이 그대로
재사용)를 직접 차단한다. **Resume 재검증은 이번 Accept에 포함하지
않는다** — 저장 전 검증이 실제로 동작한 이후에도 잔여 위험(예: 검증
로직 배포 이전에 이미 저장된 과거 손상 데이터)이 확인되면 그때 별도
Evidence로 재론한다.

---

## Q6. Retry/Resume 책임 경계 — 과도한 확장 없이

### 검토

`pg-hq-verify`의 실제 복구는 사람이 수행했다. 이것이 제기하는 질문(RFC-
0017 §7)은 "감지된 실패를 누가 고칠 책임을 지는가"이며, §Q5의 "무엇을
검증할지"와는 다른 층위다. 이 ADC는 이 경계를 최소한으로만 명시한다 —
새로운 자동화 정책을 설계하지 않는다.

- Result Store(Checkpointer)의 책임은 **판정 결과에 따라 저장을
  막는 것**까지다 — `ContentFailureError`를 발생시켜 `cp.save()`를
  건너뛰는 지금의 패턴(`_is_known_content_failure` → 예외)이 이미 이
  경계를 보여준다.
- 그 예외를 받은 뒤 **자동으로 재시도할지, 몇 번, 어떤 backoff로,
  누구에게 알릴지**는 Result Store의 책임이 아니다 — 호출자(Team
  `run()`) 또는 그 바깥(사용자 운용)의 몫이며, 이 ADC는 그 몫을
  누구에게 배정할지 결정하지 않는다.
- `efa-2026-08/EVIDENCE.md`가 이미 이 구분과 같은 방향의 Prototype
  범위(감지 → 자동 재시도 실측 → Checkpointing 통합)를 제안해뒀다 —
  이 ADC는 그 제안을 재확인만 하고, 그 Prototype의 설계·채택 여부는
  Dev HQ 개선 트랙(§Q3)과 후속 ADR/구현 단계로 넘긴다.

### Q6 결론

**Result Store의 책임은 "저장 게이트"로 한정한다 — 실패 이후의
재시도·알림·자동 복구 정책은 이 Accept에 포함하지 않는다.** 이는
RFC-0017 §7이 요구한 "책임 경계 판단"에 대한 답이면서 동시에, 그
경계를 재시도 정책 설계로 확장하지 않는 것이기도 하다.

---

## Q7. 새로운 Component/Interface를 확정하는가

### 검토

이 Accept가 요구하는 것은 기존 `run_step()`이 이미 수행하는 "저장 전
판정 → 실패 시 예외, 성공 시 저장"이라는 흐름의 **존재를 책임으로
인정**하는 것이지, 새 클래스·함수·시그니처를 도입하는 것이 아니다.
`Checkpointer`/`run_step`/`ContentFailureError`는 이미 `main`에 존재하는
Production Code이며, 이 ADC는 그 코드를 대체하거나 확장할 새 Interface를
설계하지 않는다.

### Q7 결론

**새 Component/Interface를 확정하지 않는다.** 저장 전 검증 판정 기준을
어떻게 넓힐지(시그니처 목록 확장, 다른 판단 방식 추가 등)는 여전히
구현 단계의 선택이며, 이 ADC는 "그런 판정이 있어야 한다는 책임의 존재"
만 Accept할 뿐 그 판정 로직의 형태를 정하지 않는다.

---

## Decision

**A. Accept (Scoped, Narrow — 저장 전 검증 게이트로 한정)**

RFC-0017 §5의 좁은 Boundary Question — "Multi-Task가 공유하는 Result
Store(Checkpointer)에 저장 결과의 유효성·무결성을 보장하는 책임" — 의
**존재**를, 다음 조건 위에서만 Accept한다.

1. **범위**: 이 책임은 "`run_step()`이 결과를 저장하기 전에 그 결과의
   유효성을 판정하고, 무효로 판정되면 저장을 막는다"는 게이트
   역할로만 한정한다(§Q5) — 이미 존재하는 `Checkpointer`/`run_step`/
   `ContentFailureError` 패턴이 이 게이트의 실증 사례다. Resume 시점의
   재검증은 포함하지 않는다(§Q5).
2. **Multi-Task 전용이 아니다**: 이 책임은 Execution Host(§16.3)·
   Multi-Task(§16.4)의 확장이 아니며, 그 두 책임도 전혀 변경되지
   않는다(§Q4) — 동시 실행 여부와 무관하게 Result Store가 존재하는
   모든 호출 경로(순차 포함)에 적용되는 더 일반적인 책임이다.
3. **근본 원인과 분리**: 이 Accept는 콘텐츠 레벨 실패가 발생하는 근본
   원인(Engine 호출 계층, `call_engine()`의 성공/실패 미판별)을
   해결하지 않는다(§Q3) — 그 문제는 이미 Dev HQ 개선 후보로 격상돼
   있으며, 이 ADC는 그 트랙을 대체하지 않는다. 이 Accept가 다루는
   것은 그 문제가 해결되기 전까지 손상을 영속화하지 않을 봉쇄
   (containment) 책임뿐이다.
4. **재시도 정책은 포함하지 않는다**: 판정된 실패 이후의 자동
   재시도·알림·복구 정책은 이 Accept에 포함하지 않는다(§Q6) — Result
   Store의 책임은 저장 게이트까지다.
5. **판정 로직의 구체적 형태를 확정하지 않는다**: 시그니처 목록을
   어떻게 넓힐지 등 구현 방법은 결정하지 않는다(§Q7) — 새 Component/
   Interface도 도입하지 않는다.
6. **Investment HQ 관찰에 한정**: 이 Accept의 근거인 4회 재현 중
   Investment HQ MVP 경로에서 나온 것은 2건(EFA, PG)뿐이며, `Checkpointer`
   자체가 `hqs/development/mvp/`에 존재한 적 없는 Investment HQ 전용
   컴포넌트다(§Q2, §Q3) — 이 Accept는 "Result Store가 존재하는 곳
   에서는 이런 게이트 책임이 필요하다"는 일반 원칙으로 Accept하는
   것이며, Development HQ에 동일한 컴포넌트를 새로 만들 것을 요구하지
   않는다.

### Reason

- Q0 — Architecture Intent는 이 질문을 예견하지 못했지만, 그것이
  Accept를 막지 않는다(ADC-0016과 동일한 판단 구조).
- Q1 — `pg-hq-verify`가 실제 피해(품질 저하, 수동 복구 필요)를 직접
  보여준다.
- Q2 — 4회 재현으로 Rule B(3건 이상)를 형식적으로 충족한다 —
  Evidence 부족을 이유로 Defer할 근거가 없다(작업 지시 §9).
- Q3 — 근본 원인은 Engine 호출 계층에 있다고 독립적으로 확인했다 —
  그러나 저장 게이트 책임은 원인의 소재와 무관하게 Result Store에만
  구조적으로 위치한다는 것도 함께 확인했다.
- Q4 — 4건 중 2건이 Multi-Task 도입 이전에 발생했고, Investment HQ
  안의 2건도 모두 순차 구간(Wave3)에서 발생해, 이 책임이 Multi-Task
  전용이 아님을 확인했다 — Execution Host·Multi-Task의 기존 Accept는
  흔들리지 않는다.
- Q5 — 저장 전 검증이 손상을 원천 차단하므로 Resume 재검증보다
  우선순위가 높다 — 이번 Accept는 저장 전 검증에만 한정한다.
- Q6 — 재시도·알림 정책까지 책임을 확장하지 않음으로써, 과도한 범위
  확장 없이 경계를 명시했다(작업 지시 §6).
- Q7 — 새 Component/Interface를 도입하지 않고 기존 패턴의 존재를
  책임으로 인정하는 데 그쳤다(작업 지시 §8).

### Decision Rationale

이 Decision은 `ADC-0016`(Multi-Task 존재, Accept Scoped·Conditional)을
전혀 재론하지 않는다 — Multi-Task의 Coordination·실패 격리 책임은
그대로 유지된다. 이 Decision이 새로 Accept하는 것은 Multi-Task가
의존하는 Result Store 컴포넌트의 저장 게이트 책임 하나이며, 그 근거는
Multi-Task 여부와 무관하게 성립한다(§Q4). `ADC-0013`~`ADC-0016`/
`ADR-0003`~`ADR-0006`(Execution Host·Multi-Task 존재·명칭·전략) 중
어느 것도 이 Decision으로 흔들리지 않는다.

---

## Implementation Boundary (다음 Production 구현을 위한 최소 책임 범위)

이 Accept는 Production 구현을 지금 승인하지 않는다 — 아래는 향후
ADR·구현 단계가 이 책임을 반영할 때 참고할 **최소 책임 경계**다.

**포함(이번에 존재를 Accept한 것)**:

- Result Store(예: `Checkpointer`)가 결과를 저장하기 전에 그 결과의
  유효성을 판정하는 게이트 책임.
- 무효로 판정된 결과는 저장하지 않고, 저장하지 않았다는 것을 호출자가
  알 수 있는 방식(현재는 예외)으로 알리는 책임.
- 이 게이트가 Multi-Task(동시 실행) 구간과 순차 실행 구간 모두에
  동일하게 적용된다는 것.

**제외(이번 Accept가 결정하지 않는 것 — 후속 절차로 위임)**:

- 판정 기준의 구체적 형태(시그니처 목록 확장, 다른 검증 방식 등) —
  `call_engine()` 개선(Dev HQ 트랙, §Q3)과의 관계를 포함해 후속 ADR/
  구현 단계가 정한다.
- Resume 시점 재검증 여부 — 이번엔 Not Accepted, 저장 전 검증 실효성이
  확인된 후 별도 Evidence로 재론(§Q5).
- 실패 감지 이후의 재시도·알림·자동 복구 정책(§Q6).
- Engine 호출 계층(`call_engine()`) 자체의 수정 — Dev HQ 개선 후보
  트랙이 별도로 진행한다(§Q3).
- 새 Component/Interface 신설(§Q7).
- Execution Host(§16.3)·Multi-Task(§16.4)의 범위 확장 — 전혀 넓어지지
  않는다(§Q4).
- Development HQ에 동일 Result Store 컴포넌트를 새로 만들 것을
  요구하는 것 — 이 Accept는 원칙 차원이며, 각 HQ가 실제로 Result
  Store를 갖는지는 각 HQ의 설계 선택으로 남는다.

---

## Risks

- 근거 4건 전부가 동일한 근본 원인(프록시/자체 서명 인증서로 인한
  Engine 호출 실패)에서 비롯됐다 — "서로 다른 계기의 독립 관찰"이라는
  Rule B의 취지와는 다소 다른 성격이다. 근본 원인이 Dev HQ 개선으로
  해소되면, 이 저장 게이트가 실제로 얼마나 자주 발동하는지는 재검증이
  필요할 수 있다.
- `Checkpointer`가 Investment HQ 전용이라는 것(§Q3)은, 이 Accept가
  Kernel 수준 원칙으로는 유효하더라도 Development HQ를 포함한 실제
  적용 사례가 아직 하나뿐(Investment HQ)이라는 뜻이다 — 다른 HQ에
  유사한 Result Store가 생기면 그 사례에서도 이 원칙이 유지되는지
  재확인이 필요하다.
- "저장 게이트 책임을 Accept했다"는 것이 "지금 바로 구현을 확장해야
  한다"로 오독될 위험이 있다 — 그런 뜻이 아니다. 이 Accept는 이미
  존재하는 패턴(`ContentFailureError`)의 책임을 인정한 것이며, 판정
  기준 확장은 별도 구현 단계의 선택이다.
- Resume 재검증을 이번에 Not Accepted로 남긴 것이, 저장 전 검증만으로
  충분하다는 것을 증명하지는 않는다 — 저장 전 검증이 실제로 배포된
  이후에도 과거에 이미 저장된 손상 데이터가 남아있을 수 있다는 잔여
  위험은 그대로 있다.

**재검토 조건**: 이 Decision 이후 다음 중 하나가 확인되면 재검토
대상이 된다 — (a) 저장 전 검증이 실제로 구현된 이후에도 손상된 결과가
저장되는 사례가 재현되는 관찰, (b) Development HQ 등 다른 HQ에 Result
Store가 새로 생기고 거기서도 유사한 저장 판정 공백이 관찰되는 사례,
(c) Engine 호출 계층 개선(Dev HQ 트랙)이 완료된 이후에도 이 저장
게이트가 여전히 필요하다고 판단되는 관찰(또는 반대로 완전히
불필요해졌다는 관찰).

## Next Step

**ADR Required** — 이 Decision은 Boundary를 이동시킨다(Open → Accept,
좁은 범위). 따라서 Baseline Update가 필요하다.

1. ADR을 작성해 `BASELINE.md`를 갱신한다 — §16.4(Multi-Task) 옆에
   또는 그 하위에, Result Store 저장 게이트 책임을 좁게 등재하되,
   §Implementation Boundary의 제외 항목(판정 기준 형태, Resume 재검증,
   재시도 정책, `call_engine()` 수정, 새 Component)은 계속 Open으로
   명시한다.
2. `call_engine()` 개선은 별도 Dev HQ 개선 트랙(`efa-2026-08/
   EVIDENCE.md` §DEV_HQ_FEEDBACK이 이미 제안한 Prototype 범위)으로
   독립적으로 진행한다 — 이 ADR/ADC 체인이 그 트랙을 대체하지 않는다.
3. Production 구현 착수는 이 ADC와 후속 ADR이 완료된 이후에만
   가능하다 — 착수 시 Investment HQ `Checkpointer`/`run_step`을 최소
   범위 후보로 남긴다. 구현 전, 판정 기준의 구체적 형태를 정하는 것은
   별도 판단(가능하면 §Q3의 Dev HQ 트랙과 조율)이 필요하다.
4. Resume 재검증 여부, Retry/Resume 자동화 정책은 각각 후속 RFC로
   다룬다(§Risks 재검토 조건 충족 시).

## Governance Chain 검증

`RFC-0017`(Proposed, `pg-hq-verify` 4회 재현 Evidence로 Boundary
Question만 열고 Decision 아님) → 이 ADC(Accept, Scoped·Narrow — 저장
전 검증 게이트로 한정, Resume 재검증 Not Accepted, 재시도 정책 제외,
근본 원인은 Engine 호출 계층으로 별도 확인, Multi-Task 전용 아님)
→ 후속 ADR(예정 — Baseline 반영). RFC-0017이 후속 ADC(이 ADC)에
위임한 항목(§5 Boundary Question, §6 저장 전/Resume 검증 우선순위,
§7 Retry/Resume 책임 경계, §Next Step 1~4) 중 1~3을 이 ADC가 답했다.
RFC-0017의 Out of Scope(구현 방법, Retry/Resume 책임 경계 확정,
Engine 호출 계층 근본 원인 해결, Execution Host/Multi-Task 범위 재론,
Scheduler/Workflow orchestration, §6 넓은 Runtime, 새 Component,
ADC.md 수정)를 이 ADC도 하나도 건드리지 않았음을 각 Q절에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **좁은 범위에서 그렇다**:
  Result Store 저장 게이트 책임의 "존재"만 Accept했다. 실제 Baseline
  반영은 ADR을 거쳐야 한다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오** —
  기존 `Checkpointer`/`run_step` 패턴의 책임을 인정했을 뿐, 명칭·
  Interface를 신설하지 않았다(§Q7).
- Contract Change — **없음** — 공개 Interface를 정의하지 않았다.
- Baseline 문서(`BASELINE.md`, `docs/decisions/adc/ADC.md`)를
  변경했는가 — **아니오** — 이 ADC 자신은 인용만 했다. 변경은 ADR의
  몫이다.
- Execution Host(§16.3)·Multi-Task(§16.4)의 범위를 넓혔는가 —
  **아니오**(§Q4, §Decision 조건 2).
- ADR이 필요한가 — **예**(§Next Step).

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0017과 그것이 인용한
  `checkpoint.py`, 세 Team 파일, `test_checkpoint.py`, `pg-hq-verify`/
  `efa-2026-08` EVIDENCE.md에, RFC-0017 §3이 요구한 독립 검토를 위해
  `engine_client.py`, `engine.py`, `PHASE4-HQ-CROSS-VALIDATION-0001.md`
  만 추가로 인용했다. 새 실험은 하지 않았다.
- `pg-hq-verify` 4회 재현을 핵심 Evidence로 검토했는가 — **Pass**(Q1,
  Q2).
- Result Store/Checkpointer의 무결성 책임을 Accept할지 판단했는가 —
  **Pass**(§Decision, Accept Scoped·Narrow).
- Engine 호출 계층 문제 가능성을 독립적으로 검토했는가 — **Pass**
  (Q3 — 근본 원인은 Engine 호출 계층으로 별도 확인, Dev HQ 트랙과의
  관계를 명시).
- 미관찰 위험(파일 덮어쓰기, Git 충돌)을 근거로 사용했는가 —
  **아니오** — RFC-0017 §2의 구분을 그대로 유지했다.
- 저장 전 검증과 Resume 재검증의 우선순위를 판단했는가 — **Pass**
  (Q5, 저장 전 검증 우선·Resume 재검증 Not Accepted).
- Retry/Resume 책임 경계를 과도하게 확장하지 않고 판단했는가 —
  **Pass**(Q6 — 저장 게이트까지만, 재시도 정책은 제외).
- Execution Host·Multi-Task 책임을 변경했는가 — **아니오**(Q4, §Decision
  조건 2).
- 새 Component/Interface를 임의로 확정했는가 — **아니오**(Q7,
  §Decision 조건 5).
- Evidence 부족을 이유로 불필요하게 Defer했는가 — **아니오**(Q2 —
  Rule B를 형식적으로 충족해 Accept까지 나아갔다).
- Production Code를 수정했는가 — **아니오**.
- Baseline을 직접 수정했는가 — **아니오** — 방향만 제시하고 ADR로
  위임했다.
