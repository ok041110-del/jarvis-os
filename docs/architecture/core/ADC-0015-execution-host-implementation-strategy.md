# ADC-0015: Execution Host 구현 전략(Process/Thread/Subprocess) 판단 (RFC-0015 후속)

## 목적

`docs/architecture/core/RFC-0015-execution-host-implementation-strategy.md`
§1 Boundary Question — **"Execution Host(§16.3)가 이미 Accept한
'단일 실행 단위 dispatch·격리' 책임을, Process/Thread/Subprocess 중
어떤 구현 전략으로 실현할 것을 다음 절차(ADC)에 권고할 것인가?"** —
에 대해 판단한다.

근거는 RFC-0015와 그것이 인용한 Evidence(`docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md`,
`ADC-0013`/`ADR-0003`, `ADC-0014`/`ADR-0004`, `BASELINE.md` §16.3,
`hqs/development/IMPLEMENTATION_RULES.md`)로만 한정한다. 새로운
실험·Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration 결정.
- `BASELINE.md` §6 Concept Model "Runtime" 항목과 Execution Host의
  관계 — `ADC-0014` §Q2가 이미 별개 Concept으로 판정했고, 이 ADC는
  그 판정을 전제로 삼는다.
- `docs/decisions/adc/ADC.md`의 ADC-02(Jarvis OS 수준, Runtime
  존폐) 재판단 — 그 Decision은 이 ADC와 무관하게 유지된다.
- `ADC-0008`(넓은 범위 Runtime 존폐, Not Accepted)의 재판단.
- `RFC-0012`/`ADC-0012`(Dispatch Component, DEFER)의 재개.
- Execution Host의 **존재**·**명칭**·**범위**(`ADC-0013`/`ADR-0003`,
  `ADC-0014`/`ADR-0004`가 이미 확정) 재론 — 이 ADC는 그 확정을
  넓히거나 좁히지 않는다.
- "동일 Target" 자동 판별 메커니즘 설계.
- 구현 전략의 비용(Worker 기동, 직렬화 오버헤드) 실측 — RFC-0015가
  이미 명시한 Evidence 공백을 이 ADC가 새로 메우지 않는다.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.

이 ADC가 판단하는 것은 셋이다: **(1) Process/Thread/Subprocess 중
Execution Host의 격리 책임을 충족하는 전략은 무엇인가, (2) RFC-0015가
남긴 권고(Process 유력)를 Accept/Conditional Accept/Defer 중 무엇으로
확정할 것인가, (3) `IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
조항을 이 시점에 해제할 것인가.**

---

## Q0. Process/Thread/Subprocess를 기존 Evidence 기준으로 독립 판단

### 검토

RFC-0015 §2·§3이 재구성한 Evidence를 이 ADC가 다시 독립적으로
대조한다 — RFC의 권고를 그대로 베끼지 않는다.

**정확성·격리** — Execution Host §16.3 "책임" 문언 자체("동일 대상에
대한 동시 실행에서 상태가 오염되지 않도록 격리를 제공하는 책임")가
판단 기준이다.

- **Process**: 동일 Target 동시 실행 4/4(`runtime-boundary`) + 3회
  반복 전부 정확(`process-runtime-strategy`) — 두 개의 독립적인
  Prototype이 각각 반복 관찰로 수렴했다. 다른 Target 조건에서도
  9/9(`process-runtime-strategy` §3) 정확.
- **Subprocess**: 원천적으로 공유 메모리가 없어 오염 조건 자체가
  성립하지 않는다(`async-command`, OS 프로세스 경계). 별도의 "동일
  Target 반복 재현" 실험은 없었으나, 이는 반증이 아니라 애초에 그
  실험이 필요 없는 구조적 이유(OS 경계)가 이미 다른 방식으로
  뒷받침된다.
- **Thread**: 동일 Target 동시 실행 5/5(`runtime-boundary`) + 3/3
  (`inprocess-async-command`) **전부 오염** — 마찬가지로 두 개의
  독립적인 Prototype이 반복 관찰로 수렴했다. 다른 Target 조건에서는
  Process·Subprocess와 동등하게 안전했다(`process-runtime-strategy`
  §4, `inprocess-async-command` §8).

**동시성 안정성**(실행 시간 예측 가능성) — Process·Subprocess는
반복 실행 편차가 거의 없었던 반면, Thread는 대상 코드 내부
`ThreadPoolExecutor`와 중첩되어 baseline 대비 최대 100배 이상의
지연(0.03초 → 최대 16~37초, 별도 사례 43초)과 인터프리터 종료 시점
경합 예외까지 재현됐다(`runtime-boundary` §8).

### Q0 결론

**Process와 Subprocess는 Execution Host의 격리 책임(§16.3)을
독립적으로, 반복적으로 충족한다. Thread는 동일한 반복 관찰 기준으로
그 책임을 충족하지 못한다.** 이 결론은 RFC-0015의 권고(§4)를 그대로
받아들인 것이 아니라, RFC가 재구성한 원 Evidence(Prototype 문서
5건)를 이 ADC가 다시 독립적으로 대조해 얻은 것이다 — 특히 "정확성"과
"격리"를 §16.3의 실제 책임 문언에 직접 대응시켜 재확인했다는 점에서
RFC-0015 §3의 일반적 비교표보다 더 좁게, 판단 기준에 밀착시켰다.

---

## Q1. Thread의 동일 Target 오염과 Failure/Retry Gap을 결정 근거에 어떻게 반영하는가

### 검토

RFC-0015 §3이 명시한 두 가지 Thread 관련 사실을 구분해서 다룬다.

1. **동일 Target 오염** — 두 개의 독립 Prototype에서 반복 관찰된
   **부정적 Evidence**다(Thread가 실패한다는 것을 실제로 보여주는
   증거). 이는 Q0 결론의 핵심 근거이며, 그 자체로 Thread를
   Execution Host의 격리 전략에서 배제하기에 충분하다.
2. **Failure/Retry Gap** — 반대로 "Thread 전략에서 Failure/Retry가
   실패한다는 증거"가 아니라 **"검증 자체가 없다"는 증거 부재**다.
   이 둘을 같은 무게로 취급하면 안 된다 — 증거 부재를 "Thread는
   Failure/Retry에서도 위험하다"는 결론의 근거로 삼는 것은 실제로
   관찰되지 않은 것을 관찰된 것처럼 원용하는 오류다.

### Q1 결론

**동일 Target 오염만으로 Thread 배제는 이미 충분히 정당화된다
(Q0).** Failure/Retry Gap은 Thread 배제의 **추가 근거로 사용하지
않는다** — 대신 "Thread를 향후 어떤 형태로든 재검토할 경우 반드시
먼저 메워야 할 공백"으로 §Risks에 기록한다. 이렇게 구분함으로써
Thread 배제 결정이 실제 반복 관찰(오염)에만 근거하고, 증거가 없는
영역(Failure/Retry)을 부당하게 원용하지 않았음을 명시적으로 남긴다.

---

## Q2. 비용 미측정에도 구현을 시작할 가치가 있는가 — Architecture 필요성과 구현 가능성

### 검토

작업 지시가 명시한 대로, Evidence 부족(비용 미측정)만을 이유로
자동 Defer하지 않는다. 대신 두 축을 독립적으로 판단한다.

**Architecture 필요성**: `BASELINE.md` §16.3 "책임" 문언은 "실행을
시작하고... 격리를 제공하는 책임"이라고 정의한다 — **정확성과
격리**가 책임의 핵심이며, 실행 비용(속도·자원 효율)은 그 문언
어디에도 없다. 즉 §16.3이 요구하는 최소 조건은 Q0에서 이미
충족됐다(Process/Subprocess). 비용은 책임 충족의 **필요조건이
아니라 최적화 기준**이다 — 이 구분이 "비용 미측정 = Accept 불가"라는
자동 판단을 막는다.

**구현 가능성**: `runtime-boundary`/`process-runtime-strategy`
Prototype이 이미 다음을 코드 수준에서 실증했다.

- `rtb_task.py`(identity/lifecycle)가 Executor를 몰라도 동작 —
  Task 계층 재설계가 필요 없다(RFC-0015 §5 인용).
- `rtb_runtime.py`의 기존 `ProcessPoolExecutor(max_workers=4)`만으로
  모든 검증(정확성·Failure/Retry·Dashboard Observe)이 충분했다 —
  추가 인프라(Scheduler, 커스텀 Worker 관리)가 필요하다는 신호가
  없다.
- Failure/Retry, Dashboard Observe 모두 Process 전략에서 실측
  검증을 마쳤다(`process-runtime-strategy` §6, `runtime-boundary`
  §6).

**판단**: 비용 정보가 없다고 구현을 미루는 것과, 비용 정보 없이
정확성이 보장된 구현을 시작한 뒤 비용을 병행 실측하며 조정하는 것,
두 경로 중 후자의 위험이 더 낮다 — 전자를 택하면 "정확성이 검증된
구현조차 시작하지 못하는 상태"가 무기한 지속되는 반면, 후자는
Q0에서 이미 충족된 정확성·격리를 담보로 구현하면서 비용은 후속
검증 대상으로 명시적으로 남기면 된다. 이는 §16.3이 정의한 책임의
우선순위(정확성·격리가 핵심, 비용은 최적화)와도 일치한다.

**단, 이것이 "Process를 유일·영구 전략으로 Freeze"할 근거는 아니다**
— 비용 Evidence가 나중에 Subprocess나 다른 전략의 우위를 보이면
재검토할 수 있어야 한다. 이 비대칭(구현은 지금 시작하되, 전략은
영구 고정하지 않음)이 Q2의 핵심 결론이며, 뒤의 Decision 형태
(Conditional Accept)를 직접 결정짓는다.

### Q2 결론

**비용 미측정은 Accept 자체를 막지 않는다.** 다만 "Process를
Execution Host의 유일하고 영구적인 전략으로 Freeze"하는 것은
정당화하지 않는다 — Accept는 조건부(Conditional)여야 한다.

---

## Q3. Process vs Subprocess — 무엇을 1차 구현 전략으로 권고하는가

### 검토

Q0에서 Process와 Subprocess 둘 다 격리 책임을 충족한다고 판단했다.
어느 쪽을 Execution Host의 1차 구현 전략으로 삼을지는 구조적
적합성으로 판단한다(비용 비교는 Evidence가 없으므로 사용하지 않는다
— Q2에서 이미 확인).

- **Process**(`ProcessPoolExecutor`): Task/Runtime 책임 분리가 이미
  코드 구조로 검증됐다(`rtb_task.py`가 Executor를 참조하지 않고도
  세 전략 모두에서 동작, RFC-0015 §5). 재사용 가능한 Worker Pool
  기반으로 Failure/Retry·Dashboard Observe·Command 불변성 보호가
  전부 실측 검증됐다(`process-runtime-strategy` §6).
- **Subprocess**(`subprocess.Popen`): 원천적 OS 프로세스 경계로
  동일하게 안전하고, Failure/Retry·Dashboard Observe도 검증됐다
  (`async-command` §9·§10). 다만 매 실행마다 새 인터프리터를
  기동한다는 구조적 차이가 있고(비용 미측정), Task 분리가 필요했던
  이유(Command 불변성 보호)는 확인됐지만 Process 대비 재사용 가능한
  Worker 개념을 실증한 Prototype은 없다.

### Q3 결론

**Process를 1차 구현 전략으로 권고한다.** Task/Runtime 분리가 이미
Process 기반 코드로 실증되어 있어 추가 설계 없이 구현을 시작할 수
있다는 점(Q2 "구현 가능성")이 결정적이다. **Subprocess를 배제하지
않는다** — Q0가 이미 Subprocess도 격리 책임을 충족한다고 판단했으므로,
향후 특정 조건(예: in-process 실행이 부적절한 대상)에서 대안으로
남긴다.

---

## Decision

**A. Conditional Accept — Process를 Execution Host의 1차 구현
전략으로, Thread는 명시적으로 배제, Subprocess는 유효한 대안으로
병기**

`BASELINE.md` §16.3이 정의한 Execution Host의 격리 책임을 실현하는
구현 전략으로 **Process**(`ProcessPoolExecutor` 기반)를 1차로
Accept한다. 이 Accept는 다음 조건에 한정된다.

1. **적용 범위**: "동일 Target(또는 프로세스 전역 상태를 공유하는
   대상)을 동시 실행할 가능성이 있는 경로" — 이는 §16.3 "격리"
   책임이 실제로 요구되는 조건이며, `process-runtime-strategy`
   Evidence가 구체화한 조건 그대로다. 이 조건 밖(서로 다른 Target만
   실행하는 경로)까지 Process를 강제하지 않는다 — Thread도 그
   조건에서는 안전했다는 Evidence(Q0)를 이 ADC는 무시하지 않는다.
2. **Thread 배제**: 위 조건이 성립할 수 있는 모든 경로에서 Thread를
   격리 전략으로 사용하지 않는다(Q0·Q1).
3. **Subprocess 병기**: Process를 대체할 수 없는 것은 아니다 —
   Subprocess도 동일한 격리 책임을 충족하는 것으로 Accept한다(Q3).
   어느 쪽을 실제로 선택할지는 후속 구현 단계의 재량으로 남긴다.
4. **비용 재검토 조건**: 비용이 실측되어 Subprocess 또는 다른
   전략이 명백히 우위를 보이면, 이 Decision(1차 전략 = Process)은
   재검토 대상이다(Q2) — 그러나 지금 그 실측이 없다는 것이 Accept
   자체를 막지 않는다.

### Reason

- Q0 — Process·Subprocess는 두 개의 독립적인 Prototype에서 반복
  관찰로 격리 책임을 충족했고, Thread는 동일한 기준으로 충족하지
  못했다.
- Q1 — Thread 배제는 오염 Evidence(반복 관찰)에만 근거하며,
  증거가 없는 Failure/Retry Gap을 부당하게 원용하지 않았다.
- Q2 — 비용 미측정은 §16.3 책임 문언의 핵심(정확성·격리)과 무관한
  최적화 기준의 공백이며, Accept를 막을 근거가 아니다. 다만 영구
  고정(Freeze)은 정당화하지 않으므로 Conditional로 남긴다.
- Q3 — Process가 이미 코드 수준에서 Task/Runtime 분리를 실증했다는
  구현 가능성 우위로 1차 전략을 권고하되, Subprocess를 배제하지
  않는다.

### Decision Rationale

이 Decision은 `ADC-0013`/`ADR-0003`(존재), `ADC-0014`/`ADR-0004`
(명칭)이 이미 확정한 것을 전혀 건드리지 않는다 — §16.3의 책임
범위(단일 실행 단위, Multi-Task 제외)도 그대로 유지된다. 이 Decision은
"무엇으로 그 책임을 실현하는가"만 판단했다. `ADC-0008`(넓은 범위
Runtime 존폐, Not Accepted), `docs/decisions/adc/ADC.md` ADC-02(Open),
`RFC-0012`/`ADC-0012`(DEFER)도 전혀 영향받지 않는다 — 이 Decision은
좁은 구현 전략 질문에만 답했다.

---

## Q4. `IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지" 조항을 해제할 것인가

### 검토

기존 조항 문언: `| Runtime 구현 금지 | Runtime 개념 자체가 Open
Decision(ADC-02)이다 |`. 이 이유 문구는 이제 정확하지 않다 —
Execution Host는 ADC-02가 다루는 §6 넓은 "Runtime"과 별개
Concept(`ADC-0014` §Q2)이며, 그 존재·명칭은 이미 확정됐고, 이제
구현 전략까지 이 ADC가 Conditional Accept했다. `ADR-0003` §5와
`ADR-0004` §5가 공통으로 "구현 전략이 확정되는 시점에 함께 정리하는
것이 이중 수정을 피하는 길"이라고 예고한 바로 그 시점이 지금이다.

**그러나 전면 해제는 아니다.** 조항이 원래 금지한 범위(Dev HQ MVP
Production 코드에서 Runtime류 개념 구현)에는 여전히 두 가지가
포함된다.

- Scheduler/Multi-Task/Workflow orchestration — 이 ADC의 §Out of
  Scope이며 §16.3 책임 범위 밖이다. 이 부분의 금지는 유지되어야
  한다.
- §6 넓은 "Runtime"(Workflow 참조, Multi-Task 배분) 자체의 구현 —
  `ADC-0008`이 Not Accepted로 남긴 영역이며, `docs/decisions/adc/ADC.md`
  ADC-02가 여전히 Open이다. 이 부분의 금지도 유지되어야 한다.

### Q4 결론

**부분 해제(Scoped)한다.** Execution Host의 좁은 범위(§16.3 책임,
Process 1차·Subprocess 대안, "동일 Target 동시 실행" 조건, Thread
배제)에 한해 "Runtime 구현 금지"를 해제하도록 다음 ADR에 위임한다.
Scheduler/Multi-Task/Workflow, §6 넓은 Runtime 구현은 계속 금지
상태로 남긴다 — 조항을 완전히 삭제하지 않고, 범위를 좁힌 새 문구로
교체하는 것을 다음 ADR에 제안한다(§Baseline/Rules 반영 범위).

---

## Baseline / IMPLEMENTATION_RULES.md 반영 범위 (다음 ADR을 위한 지침, 이 ADC가 직접 반영하지 않음)

### `BASELINE.md` §16.3 반영 범위

절 제목·"책임"·"근거"·"명칭" 문단은 변경하지 않는다(`ADC-0013`/
`ADC-0014`가 이미 확정). "**이 Accept가 결정하지 않는 것**" 문단의
"구현 전략(Process/Thread/Subprocess)... 은 모두 별도 절차(RFC →
ADC → ADR)로 남는다" 문구를, 이제 그 절차가 이 ADC로 일부 완료됐음을
반영해 "구현 전략은 Process(1차)/Subprocess(대안)로 Conditional
Accept됐다(`ADC-0015`), Thread는 배제됐다. Scheduler/Multi-Task/
Workflow 확장은 여전히 별도 절차로 남는다"로 대체하는 것을 제안한다
(최종 문구는 후속 ADR이 확정).

### `hqs/development/IMPLEMENTATION_RULES.md` 반영 범위

금지 항목 문구를 다음 방향으로 좁히는 것을 제안한다(최종 문구는
ADR이 확정).

- 기존: `Runtime 구현 금지 | Runtime 개념 자체가 Open Decision(ADC-02)이다`
- 제안 방향: Execution Host(Process 1차, "동일 Target 동시 실행"
  조건, Thread 배제)의 최소 구현은 허용하되, Scheduler/Multi-Task/
  Workflow 및 §6 넓은 Runtime(ADC-02, Open) 구현은 계속 금지한다는
  것을 명시하는 두 항목으로 분리.

이 반영은 이 ADC가 직접 수행하지 않는다 — 다음 ADR의 몫이다.

---

## Out of Scope

- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration 결정.
- `BASELINE.md` §6 Concept Model "Runtime" 항목과 Execution Host의
  관계 재론(`ADC-0014` §Q2 유지).
- `docs/decisions/adc/ADC.md`의 ADC-02(Open) 항목 수정.
- `ADC-0008`(Not Accepted, 넓은 범위)의 재판단.
- `RFC-0012`/`ADC-0012`(DEFER)의 재개.
- Execution Host의 존재·명칭·범위 재론(`ADC-0013`/`ADR-0003`,
  `ADC-0014`/`ADR-0004` 유지).
- "동일 Target" 자동 판별 메커니즘 설계 — 이 Decision은 그 판별이
  구현자의 재량/후속 검증 대상임을 전제로 조건부 형태를 취했을
  뿐, 판별 방법 자체를 설계하지 않는다.
- 구현 전략의 비용 실측.
- `BASELINE.md`, `hqs/development/IMPLEMENTATION_RULES.md`의 실제
  파일 수정 — 방향만 제시했다(§Baseline/Rules 반영 범위), 실행은
  다음 ADR.
- Production Code(`core/`, `hqs/`, `dashboard/`) 수정.

## Risks

- Thread Failure/Retry Gap을 이 ADC가 배제 근거로 쓰지 않았다는
  것은, 향후 Thread를 어떤 형태로든(예: "다른 Target 전용 경량
  전략") 재고려할 경우 그 Gap을 반드시 먼저 메워야 한다는 뜻이다 —
  지금 이 Decision이 그 Gap을 대신 해소한 것으로 오독되어서는
  안 된다.
- 비용 미측정 상태로 구현을 시작하도록 Q2가 판단했으므로, 실제
  구현이 진행된 뒤 비용이 예상보다 크다는 것이 밝혀지면 이미 투입된
  구현에 대한 재작업 비용(sunk cost)이 발생할 수 있다 — 다음 ADR/
  구현 단계에서 비용 실측을 가능한 한 조기에 병행할 것을 권고한다.
- "동일 Target 동시 실행"이라는 조건이 자동으로 판별되지 않는 채로
  Conditional Accept가 이뤄졌으므로, 실제 구현자가 이 조건을 수동
  으로 판단해야 하는 실무 부담이 남는다 — 판별 실패(오탐/누락) 시
  Thread급 위험이 재현될 수 있다는 것을 다음 ADR/구현 지침에
  명시해야 한다.
- `IMPLEMENTATION_RULES.md`의 부분 해제가 "Runtime 개념 전체 구현
  허용"으로 오독될 위험 — 다음 ADR이 범위(Execution Host, Process/
  Subprocess, 동일 Target 조건)를 문구에 명확히 남겨야 한다.
- Subprocess를 "유효한 대안"으로 병기했지만 실제로 언제 Process
  대신 Subprocess를 선택해야 하는지의 기준은 이 ADC가 제공하지
  않는다 — 후속 구현에서 임의 선택에 따른 비일관성이 생길 수 있다.

**재검토 조건**: 비용 실측이 이뤄져 Subprocess 또는 다른 전략이
Process보다 명백히 우위라는 결과가 나오면, 이 Decision(Process를
1차 전략으로)은 재검토 대상이다. Trading HQ 등장 시 3-HQ 재검증도
5개 Prototype 전체에서 공통으로 보류된 조건이며, 이 ADC도 동일하게
유지한다.

## Next Step

**ADR Required** — 이 Decision은 `BASELINE.md` §16.3과
`hqs/development/IMPLEMENTATION_RULES.md`에 반영돼야 한다.

1. ADR을 작성해 `BASELINE.md` §16.3 "이 Accept가 결정하지 않는 것"
   문단에 구현 전략 Conditional Accept 결과를 반영한다(§Baseline/
   Rules 반영 범위 참고, 최종 문구는 ADR이 확정).
2. 같은 ADR 또는 별도 절차로 `hqs/development/IMPLEMENTATION_RULES.md`
   의 "Runtime 구현 금지" 조항을 Scoped 해제 방향으로 갱신한다(§Q4).
3. Production 구현 착수는 이 ADC와 후속 ADR이 완료된 이후에만
   가능하다 — 이 ADC 자체는 구현을 승인하지 않는다. 착수 시
   `rtb_task.py`/`rtb_runtime.py`(Process 전략) 계보를 최소 범위로
   Dev HQ MVP에 반영하는 것을 후보로 남긴다(우선순위는 사용자 결정).
4. 비용 실측을 구현과 최대한 병행하는 것을 권고한다(§Risks).
5. "동일 Target" 자동 판별 메커니즘은 이 ADC·ADR과 별도로 후속
   Prototype 검증 대상으로 남긴다.
6. Scheduler/Multi-Task/Workflow 구현은 계속 금지 상태로 유지한다 —
   이번 ADR도 이 범위를 건드리지 않는다.

## Governance Chain 검증

`RFC-0015`(Proposed, 5개 Prototype Evidence 비교와 권고만 — Decision
아님) → 이 ADC(Conditional Accept — Process 1차·Subprocess 대안·
Thread 배제, `IMPLEMENTATION_RULES.md` Scoped 해제 결정) → 후속
ADR(예정 — Baseline·Rules 반영). RFC-0015가 명시적으로 후속 ADC에
위임한 세 질문(§4 최종 채택 방향, Thread 배제 근거 처리, 구현 금지
해제 여부 — RFC-0015 §Next Step 1·2·3) 전부를 이 ADC가 답했다.
RFC-0015의 Out of Scope(Scheduler·Multi-Task/Workflow·§6 Runtime
관계·ADC-02·ADC-0012 재론·비용 실측·자동 판별 설계)를 이 ADC도
하나도 건드리지 않았음을 §Out of Scope에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오** — 이미 Accept된
  책임(§16.3)을 실현하는 구현 전략을 판단했을 뿐, 새 책임을 추가
  하지 않았다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오** —
  Execution Host라는 기존 Concept의 구현 방식만 판단했다.
- Contract Change — **없음** — 공개 Interface를 정의하지 않았다.
  Kernel Public Contract(§14)는 무변경.
- Baseline 문서(`BASELINE.md`)·`IMPLEMENTATION_RULES.md`를 이 ADC가
  변경했는가 — **아니오** — 방향·제안만 했다. 실제 변경은 ADR의
  몫이다(§Baseline/Rules 반영 범위).
- `docs/decisions/adc/ADC.md`(ADC-02)를 변경했는가 — **아니오**.
- Production 구현을 승인했는가 — **아니오** — Conditional Accept는
  구현을 위한 전략 판단이지 구현 승인 자체가 아니다. Production
  구현은 후속 ADR 이후에만 가능하다(§Next Step 3).
- ADR이 필요한가 — **예**(§Next Step).

## Self Review

- Evidence만 사용했는가 — **Pass**. `RFC-0015`와 그것이 인용한
  5개 Prototype 문서, `ADC-0013`/`ADR-0003`, `ADC-0014`/`ADR-0004`,
  `BASELINE.md` §16.3, `IMPLEMENTATION_RULES.md`만 인용했다. 새
  실험은 하지 않았다.
- Process/Thread/Subprocess를 기존 Evidence 기준으로 독립 재판단
  했는가 — **Pass**(§Q0) — RFC-0015의 비교표를 그대로 베끼지 않고
  §16.3 책임 문언에 직접 대응시켜 재확인했다.
- Process 권고를 Accept/Conditional Accept/Defer 중 하나로
  결정했는가 — **Pass**(§Decision — Conditional Accept).
- Evidence 부족(비용)만을 이유로 자동 Defer했는가 — **아니오**
  (§Q2 — Architecture 필요성과 구현 가능성을 독립적으로 판단한 뒤
  Accept 방향을 택했고, Defer가 아니라 Conditional로 남긴 이유를
  명시했다).
- Thread의 동일 Target 오염과 Failure/Retry Gap을 결정 근거에
  반영했는가 — **Pass**(§Q1) — 오염은 배제 근거로, Gap은 배제
  근거로 쓰지 않고 Risk로만 분리해 기록했다.
- 비용 실측이 없어도 구현을 시작할 가치가 있는지 명시적으로
  판단했는가 — **Pass**(§Q2 — "예"로 판단하고 그 근거를 §16.3
  책임 문언과 구현 가능성 Evidence로 뒷받침했다).
- `IMPLEMENTATION_RULES.md`의 Runtime 구현 금지 해제 여부를
  판단했는가 — **Pass**(§Q4 — 전면 해제가 아니라 Scoped 해제로
  결정).
- Execution Host의 책임 범위를 확대했는가 — **아니오** — §16.3의
  범위(단일 실행 단위, Multi-Task 제외)를 그대로 유지했고,
  Scheduler/Multi-Task/Workflow는 명시적으로 Out of Scope에
  남겼다(§Out of Scope, §Q4).
- Production Code를 변경했는가 — **아니오**.
- Baseline·`IMPLEMENTATION_RULES.md`를 직접 수정했는가 —
  **아니오** — 방향만 제시하고 ADR로 위임했다(§Baseline/Rules
  반영 범위).
- `ADC-0008`·`ADC-0012`·`docs/decisions/adc/ADC.md`(ADC-02)를
  재론했는가 — **아니오**.
- §6 "Runtime"과의 관계를 재론했는가 — **아니오**(`ADC-0014` §Q2
  전제 유지).
