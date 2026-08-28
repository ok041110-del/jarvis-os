# RFC-0015: Execution Host 구현 전략 — Process/Thread/Subprocess 비교 (ADC-0014/ADR-0004 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §16.3("Execution
Host — 단일 실행 단위 Dispatch·격리, Accept Scoped")가 "이 Accept가
결정하지 않는 것"으로 명시적으로 남긴 항목 중 **구현 전략
(Process/Thread/Subprocess)** 만.
**Evidence**: `docs/research/JARVIS-OS-V2.0-RUNTIME-BOUNDARY-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-PROCESS-RUNTIME-STRATEGY-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-ASYNC-COMMAND-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-INPROCESS-ASYNC-COMMAND-PROTOTYPE-0001.md`,
`docs/research/JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md`,
`docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`,
`docs/architecture/core/ADC-0013-runtime-existence-scoped-reconsideration.md`,
`docs/architecture/core/ADC-0014-execution-responsibility-naming.md`,
`docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`,
`docs/architecture/baseline/BASELINE.md` §16.3,
`hqs/development/IMPLEMENTATION_RULES.md`. 새로운 실험·Evidence를
만들지 않는다 — 이미 병합/기록된 5개 Prototype Evidence만 재구성·
비교한다.

> 본 RFC는 Process/Thread/Subprocess 중 무엇을 최종 채택할지
> **확정하지 않는다** — 비교와 권고까지만 하고, 최종 채택은 후속
> ADC로 위임한다. Scheduler/Engine Gateway 등 대체 구조, Multi-Task/
> Workflow orchestration, `BASELINE.md` §6 "Runtime" 항목과의 관계는
> 이 RFC의 범위 밖이다(이미 `ADC-0014` §Q2가 별개 Concept으로
> 판정했고 이 RFC는 그 판정을 재론하지 않는다). Production
> Code(`core/`, `hqs/`, `dashboard/`)와 Kernel Public Contract(§14)는
> 수정하지 않는다.

## 0. 이 RFC가 열린 이유

`ADC-0014`/`ADR-0004`는 §16.3이 Accept한 "단일 실행 단위 dispatch·
격리" 책임에 **명칭**(Execution Host)만 부여했다. 두 문서 모두
"명칭 결정만으로는 구현 전략을 결정하지 않는다"고 명시적으로
못박았고(`ADC-0014` §Out of Scope, `ADR-0004` §Out of Scope),
`hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
조항도 그대로 유효하다.

그 사이 5개 Experimental Prototype
(`runtime-boundary` → `process-runtime-strategy`, 그리고 선행한
`async-command` → `inprocess-async-command` → `dev-hq-vertical-
slice`)이 이미 Process/Thread/Subprocess 세 전략을 실제 코드로
반복 비교한 Evidence를 남겼다. 이 RFC는 그 Evidence를 정확성·
격리·동시성·실패/Retry·비용·복잡도 여섯 기준으로 재구성해, "다음
Governance 절차가 구현 전략을 판단할 때 무엇을 근거로 삼을 수
있는가"를 정리한다. 새 실험은 하지 않는다.

## 1. Boundary Question

**Execution Host(§16.3)가 이미 Accept한 "단일 실행 단위 dispatch·
격리" 책임을, Process/Thread/Subprocess 중 어떤 구현 전략으로
실현할 것을 다음 절차(ADC)에 권고할 것인가?**

이 질문은 다음을 전제로 한다 — 전제 자체는 이 RFC가 다시 열지 않는다.

- 책임의 **존재**는 이미 Accept됐다(`ADC-0013`, `ADR-0003`). 이 RFC는
  존재 여부를 재론하지 않는다.
- 책임의 **명칭**은 이미 확정됐다(`ADC-0014`, `ADR-0004` — Execution
  Host). 이 RFC는 명칭을 재론하지 않는다.
- 책임의 **범위**(§16.3, Multi-Task/Workflow 제외)는 이미 좁게
  확정됐다. 이 RFC는 그 범위를 넓히거나 좁히지 않는다.
- Execution Host와 §6 Concept Model "Runtime" 항목의 관계(별개
  Concept)는 이미 `ADC-0014` §Q2가 판정했다. 이 RFC는 재론하지
  않는다.

## 2. Evidence Summary — 이미 기록된 것만 인용

아래는 5개 Prototype Evidence 문서에서 **이미 관찰·기록된 사실만**
발췌해 전략별로 재구성한 것이다. 각 항목 끝의 괄호가 원 출처다.
이 절 자체는 새로운 실험을 수행하지 않는다 — 다만 여러 문서에
흩어진 관찰을 하나의 표로 **재구성**하는 것은 이 RFC가 처음 하는
일이며, 그렇게 재구성해야만 보이는 결론(§3 비교표, §4 권고)이 있다.
이 재구성 자체를 "새로운 사실"로 오인하지 않도록, 원 출처 없이
서술되는 문장은 이 절에 없다.

### 2.1 Process (`ProcessPoolExecutor`, in-process 재사용 Worker Pool)

- 동일 Target 동시 실행: 4/4 정확(`runtime-boundary`), 3회 반복
  전부 정확(`process-runtime-strategy`) — 오염 0건.
- 다른 Target(Dev HQ 내부 서로 다른 실제 파일 2종, 실행 시간
  0.1초~69초) 반복 적용: 9/9 정확(`process-runtime-strategy` §3).
- Sequential Baseline과 결과 완전 일치(`(8,0)`==`(8,0)`,
  `process-runtime-strategy` §5).
- 실행 시간 안정성: 반복 실행 전부 ~0.7초로 일정, Thread처럼
  급격한 지연이 없음(`runtime-boundary` §5·§8).
- Failure/Retry: 잘못된 경로 → `FAILED`, `error` 보존, `retry()`가
  새 `task_id`로 재사용해 재실패(정상), 이후 올바른 경로로 재시도
  시 성공까지 확인(`runtime-boundary` §6, `process-runtime-strategy`
  §6).
- Dashboard Observe: Process Task도 Registry로 동일하게 관찰됨
  (`process-runtime-strategy` §6).
- Task/Runtime 책임 분리: `rtb_task.py`가 `ThreadPoolExecutor`/
  `ProcessPoolExecutor` 클래스를 이름조차 참조하지 않고도 세
  전략(sequential/thread/process) 모두에서 정상 동작
  (`runtime-boundary` §3, AST 기반 자동 검증).
- 비용: **정량 측정되지 않음** — Worker 기동 비용, 직렬화
  오버헤드는 두 Prototype 모두 명시적으로 "실측하지 않음, Next
  Step"으로 남겼다(`process-runtime-strategy` §1, §8; `runtime-
  boundary` §13).

### 2.2 Thread (`ThreadPoolExecutor`, in-process 공유 메모리)

- 동일 Target 동시 실행: 5회 반복 전부 오염
  (`runtime-boundary` §4, 재현), 3회 반복 전부 오염(`inprocess-
  async-command` §8) — `monkeypatch`로 설정한 fake 상태가 스레드
  간에 실제로 섞여 진짜 assertion 실패(`assert 2 == 1` 등)까지
  재현됨(`inprocess-async-command` §8).
- 다른 Target 동시 실행: **안전했다** — Cross-HQ(`inprocess-async-
  command` §8)뿐 아니라 같은 HQ(Dev HQ) 내부의 서로 다른 두 실제
  파일에서도 3회 반복 전부 정확(`process-runtime-strategy` §4).
- 예측 불가능한 지연: 대상 코드 자체의 내부 `ThreadPoolExecutor`
  (`stock_team.py`)와 중첩되어 baseline 0.03초가 최대 16~37초까지,
  자동 테스트 실측에서는 pytest 보고 6.33초인데 실제 프로세스
  종료까지 43초가 걸리는 현상까지 관찰됨(`runtime-boundary` §8).
  별도 1회성 재현에서 `RuntimeError: cannot schedule new futures
  after interpreter shutdown`까지 관찰됨(같은 절).
- 취소 불가능성: 실행 중인 Thread를 강제 종료하는 표준 방법이
  없음 — 함수 자체는 1.31초 만에 반환했지만 백그라운드 Thread가
  끝날 때까지 프로세스 종료에 실제로 59초가 걸림(`inprocess-async-
  command` §12).
- Failure/Retry: 이 조건(Thread 전략)에 대해 별도로 실측되지
  않았다 — 두 Prototype 모두 Failure/Retry 검증은 Process 전략
  기준으로 수행됐다(`runtime-boundary` §6, `process-runtime-
  strategy` §6). Thread 전략의 Failure/Retry 안전성은 **Evidence
  없음**(§4에서 Gap으로 명시).
- 비용: 정량 측정되지 않았다. 다만 Worker Process 기동이 없다는
  점에서 이론적으로 Process보다 가볍다고 예상되나, 이 예상 자체는
  어느 Prototype도 실측하지 않았다 — **추정일 뿐 Evidence 아님**.

### 2.3 Subprocess (`subprocess.Popen`, 매 실행마다 새 인터프리터)

- 동일/다른 Target 여부와 무관하게 항상 안전 — OS 프로세스 경계가
  애초에 공유 메모리 문제를 만들지 않음(`process-runtime-strategy`
  §1이 `async-command` 결과를 인용해 재확인. `async-command` 자체는
  동일 Target 동시 실행을 직접 재현하지는 않았으나, 서로 다른 HQ
  2종(Dev HQ 70초+, Investment HQ 0.1초)을 실제로 동시 RUNNING
  상태로 관찰함, `async-command` §4·§7).
- 실측 동시 실행 비용: Dev HQ 단독 69.99초 vs Investment HQ와 동시
  실행 시 88초(+18초, CPU 경합으로 인한 실측 지연) — 실제로 관찰된
  부작용이며 조작하지 않음(`async-command` §4).
- Failure/Retry: 실제 pytest 실패(exit code 4, 잘못된 경로)와
  재시도 성공 모두 실측 검증(`async-command` §9).
- Dashboard Observe: Task Registry 기반으로 2개 HQ의 동시 RUNNING
  상태를 정확히 관찰(`async-command` §10).
- 비용: 매 실행마다 완전히 새 Python 인터프리터를 기동하는 비용이
  있다고 판단되나(`process-runtime-strategy` §1), **정량 실측은
  없다** — `ProcessPoolExecutor`의 재사용 가능한 Worker Process
  대비 기동 비용이 클 것이라는 것은 일반적 추정이지 이 저장소의
  실측 Evidence가 아니다(`process-runtime-strategy` §1이 명시적으로
  "실측하지 않았으나 일반적으로"라고 한정).
- Command 불변성: Case A(Command만)는 동작했으나 `frozen=True`를
  유지할 수 없었다 — 이는 Subprocess/Thread/Process 전략과
  무관하게 Task 분리 필요성(이미 확정된 §16.3 존재 Accept의 근거)
  자체를 가리키며, 이 RFC가 다시 판단하지 않는다(`async-command`
  §12, `ADC-0013`가 이미 종합).

## 3. 비교 — 정확성·격리·동시성·실패/Retry·비용·복잡도

| 기준 | Process | Thread | Subprocess |
|---|---|---|---|
| **정확성**(동일 Target 동시 실행) | 항상 정확(4/4 + 3/3, §2.1) | 항상 오염(5/5 + 3/3, §2.2) | 오염 조건 자체가 원천적으로 없음(§2.3, OS 경계) |
| **정확성**(다른 Target 동시 실행) | 정확(§2.1) | 정확(§2.2) — Process와 동일 | 정확(§2.3, 실측은 Cross-HQ 한정) |
| **격리** | OS Worker Process 경계(재사용 Pool) | 없음 — 공유 프로세스 메모리(§2.2) | OS 프로세스 경계(매 실행 신규 인터프리터, §2.3) |
| **동시성 안정성**(실행 시간 예측 가능성) | 안정적(반복 실행 편차 거의 없음, §2.1) | 불안정 — 중첩 Thread Pool로 최대 16~37초 편차, 예외 발생 사례까지 관찰(§2.2) | 안정적이나 CPU 경합으로 인한 지연은 실측됨(+18초, §2.3) |
| **취소/종료** | 별도 실측 없음(Evidence Gap) | 표준 강제 종료 수단 없음 — 실제 지연 사례 관찰(59초, §2.2) | `operation.terminate()` 존재(`async-command`의 구현 요소로 `inprocess-async-command` §12가 대조 인용) — 이 RFC는 그 메커니즘 자체를 재검증하지 않는다 |
| **Failure/Retry** | 실측 검증 완료(§2.1) | **Evidence 없음**(§2.2, Gap) | 실측 검증 완료(§2.3) |
| **비용**(정량) | **미측정**(§2.1) | **미측정**(§2.2, 이론적 추정만) | **미측정**(§2.3, 이론적 추정만) |
| **복잡도**(구현) | 낮음 — `rtb_task.py`가 Executor를 몰라도 동작, 기존 `ProcessPoolExecutor(max_workers=4)`로 충분(§2.1) | 낮음(표준 primitive) — 그러나 대상 코드의 기존 Thread Pool과의 중첩을 고려해야 하는 숨은 복잡도가 실제로 발견됨(§2.2) | 가장 낮음 — 별도 Task/Runtime 분리 없이도 비동기성 자체는 stdlib만으로 확보(§2.3). 단, Command 불변성 보호를 위한 Task 분리 필요성은 세 전략 공통(§2.3 마지막 항목) |

**정확성·격리·동시성 안정성**은 세 Prototype에 걸쳐 반복 관찰된
결과가 일관된다 — Process와 Subprocess는 두 조건(동일/다른
Target) 모두에서 정확했고, Thread는 동일 Target에서만 실패했다.
**Failure/Retry**는 Process·Subprocess 양쪽에서 실측됐지만 Thread
전략에 대해서는 어느 Prototype도 직접 검증하지 않았다 — 이는 이
RFC가 새로 발견한 사실이 아니라, 기존 Evidence의 **공백**을 이
비교표가 처음으로 명시적으로 드러낸 것이다. **비용**은 세 전략
모두 정량 Evidence가 없다 — "Process/Subprocess가 Thread보다
무겁다"는 것은 이 저장소 어디에도 실측되지 않은 일반적 추정이며,
`process-runtime-strategy` §1 스스로 이 추정을 Evidence와
구분해서 표시했다. 이 RFC도 그 구분을 그대로 유지한다.

## 4. Decision Candidate (권고, 확정 아님)

**권고 방향: Process(정확성·격리·동시성 안정성 세 기준에서 가장
일관된 Evidence를 가짐)가 유력하지만, 이 RFC는 이를 확정하지
않는다.**

권고의 근거:

- 정확성·격리·동시성 안정성 세 기준에서 Process는 반복 관찰
  전부(4/4, 3/3, 9/9)에서 문제가 없었고, Subprocess도 동등하게
  안전했다(원천적 프로세스 경계). Thread만 유일하게 동일 Target
  조건에서 반복적으로 실패했다.
- Subprocess 대비 Process(`ProcessPoolExecutor`)가 가진 유일한
  구조적 이점은 "재사용 가능한 Worker Pool"이라는 점이나, 이
  이점을 뒷받침할 정량 비용 Evidence가 없다 — **권고가 Process를
  Subprocess보다 우선시할 근거는 아직 약하다는 것을 그대로
  인정한다.**

**이 권고를 이번 RFC에서 확정하지 않는 이유** — 사용자 지시 §4를
그대로 따른다:

1. **비용이 미측정이다**(§3). Process와 Subprocess 중 어느 것을
   "기본"으로 삼을지는 비용 실측 없이는 근거가 불완전하다.
2. **Thread의 Failure/Retry Evidence가 없다**(§3). "Thread를
   후보에서 제외한다"는 결론 자체는 정확성 근거만으로 이미
   충분히 강하지만(§3 첫 행), 그 제외가 Failure/Retry 관점에서도
   똑같이 확고한지는 검증되지 않았다.
3. **"동일 Target" 자동 판별 방법이 없다**(`process-runtime-
   strategy` §11). Process가 필요한 조건이 "동일 Target 동시
   실행"으로 좁혀졌지만, 실행 전에 이를 자동으로 판별하는 방법은
   어느 Prototype도 검증하지 않았다 — 이 판별 없이 "Process를
   기본 전략으로 삼는다"와 "필요할 때만 Process로 전환한다" 중
   무엇이 타당한지 이 RFC는 답할 수 없다.
4. Trading HQ 등장 시 3-HQ 재검증이 모든 5개 Prototype에서
   공통으로 보류된 항목이다 — 지금까지의 Evidence는 Dev HQ ·
   Investment HQ 2-HQ 범위로 한정된다.

**최종 채택은 후속 ADC로 위임한다.** 후속 ADC가 판단해야 할 것:

- Process를 Execution Host의 기본/유일 구현 전략으로 확정할지,
  아니면 조건부 전략(예: "동일 Target 감지 시에만 Process, 그 외
  Thread/Subprocess 허용")으로 남길지.
- Thread를 후보에서 완전히 배제할지, 아니면 "다른 Target 한정"
  조건부로 허용할지(§3의 Failure/Retry Evidence 공백을 어떻게
  처리할지 포함).
- 비용 실측이 확정에 필수적인 선행 조건인지, 아니면 정확성·격리
  Evidence만으로 잠정 확정하고 비용은 후속 검증으로 남길지.

## 5. Execution Host의 책임과 구현 전략의 분리

`BASELINE.md` §16.3(Execution Host)의 "**책임**"은 "실행을 시작하고
... 격리를 제공하는 책임"이라고 **행동의 결과**로 정의되어 있으며,
Process/Thread/Subprocess 중 무엇으로 그 결과를 만드는지는 애초에
그 문장의 범위 밖이다. `runtime-boundary` Prototype이 코드 수준에서
이미 이 분리를 증명했다 — `rtb_task.py`(identity/lifecycle)는
`ThreadPoolExecutor`/`ProcessPoolExecutor` 클래스 이름조차 참조하지
않고도 세 전략 전부에서 정상 동작했다(§2.1 인용, AST 기반 자동
검증). 즉:

- **책임**(무엇을 보장하는가 — dispatch·격리)은 `ADC-0013`/
  `ADR-0003`이 이미 확정했고, 이 RFC는 그 확정을 그대로 유지한다.
- **구현 전략**(어떻게 보장하는가 — Process/Thread/Subprocess)은
  책임과 독립적으로 선택 가능하다는 것이 코드 구조로 실증됐다 —
  이는 §4의 권고를 지금 확정하지 않아도 "책임의 존재·명칭"이라는
  이미 Accept된 결정이 흔들리지 않는다는 근거이기도 하다.

이 분리는 향후 ADC가 구현 전략을 "선택"이 아니라 "복수 지원"으로
판단하더라도(예: 조건에 따라 Process/Thread를 전환), Task 계층은
전혀 변경할 필요가 없다는 것을 시사한다 — 다만 이 시사점을 Decision
으로 확정하는 것은 이 RFC의 권한 밖이다(§Out of Scope).

## Out of Scope

- Process/Thread/Subprocess 중 최종 채택 확정 — 권고까지만(§4).
- Scheduler/Engine Gateway 등 대체 구조 설계.
- Multi-Task/Workflow orchestration 결정.
- `BASELINE.md` §6 Concept Model의 "Runtime" 항목과의 관계 재론 —
  `ADC-0014` §Q2가 이미 별개 Concept으로 판정했고 이 RFC는 그
  판정을 전제로 삼는다(§1).
- `docs/decisions/adc/ADC.md`의 ADC-02(Jarvis OS 수준, Runtime
  존폐) 항목 수정.
- `ADC-0008`(넓은 범위 Runtime 존폐, Not Accepted)의 재판단.
- `RFC-0012`/`ADC-0012`(Dispatch Component, DEFER)의 재개.
- 새로운 실험 — 이 RFC는 이미 병합된 5개 Prototype Evidence만
  재구성·비교한다(§2).
- 비용(Worker 기동, 직렬화 오버헤드) 실측 — 이 RFC는 Evidence
  공백을 명시할 뿐(§3), 새 측정을 수행하지 않는다.
- "동일 Target" 자동 판별 방법 설계.
- `hqs/development/IMPLEMENTATION_RULES.md`의 "Runtime 구현 금지"
  조항 해제 — 구현 전략이 이 RFC로 확정되지 않으므로 여전히
  유효하다.
- Production Code(`core/`, `hqs/`, `dashboard/`), Kernel Public
  Contract(§14) 수정.

## Non-goals

- 이 RFC는 Process/Thread/Subprocess 중 하나를 확정하지 않는다 —
  비교와 권고만 한다(§4).
- 이 RFC는 §16.3이 이미 확정한 책임의 존재·범위·명칭을 재론하지
  않는다(§1).
- 이 RFC는 §6 "Runtime"과 Execution Host의 관계를 재론하지
  않는다.
- 이 RFC는 Scheduler나 Multi-Task/Workflow를 설계하지 않는다.
- 이 RFC는 새로운 실험이나 비용 실측을 수행하지 않는다.
- 이 RFC는 Architecture Baseline을 직접 변경하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §4의 권고(Process 유력, 확정 아님)를 그대로 Accept할지, 조건부
   전략(동일 Target 감지 시에만 Process)으로 좁힐지, 아니면 비용
   실측을 선행 조건으로 요구하며 이번엔 DEFER할지.
2. Thread를 후보에서 완전히 배제할지, 배제한다면 그 근거로 §3의
   Failure/Retry Evidence 공백을 어떻게 다룰지(공백을 이유로
   배제 판단을 유보할지, 아니면 정확성 Evidence만으로 충분하다고
   판단할지).
3. 구현 전략이 확정된다면, `hqs/development/IMPLEMENTATION_RULES.md`
   의 "Runtime 구현 금지" 조항을 해제할지(또는 이유 문구만
   갱신할지) — `ADR-0003` §5, `ADR-0004` §5가 이미 이 타이밍을
   제안했다.
4. "동일 Target" 자동 판별 방법 검증을 이 ADC의 선행 조건으로
   요구할지, 별도 후속 Prototype으로 분리할지.
5. 비용 실측(Worker 기동, 직렬화 오버헤드)을 이 ADC 이전에
   요구할지, ADC 이후 별도 검증으로 남길지.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. 5개 Prototype Evidence 문서와
  `ADC-0013`/`ADR-0003`/`ADC-0014`/`ADR-0004`/`BASELINE.md` §16.3만
  인용했다. 새 실험은 하지 않았다(§2).
- 기존 관찰과 이 RFC의 재구성을 구분해 표시했는가 — **Pass**(§2
  머리말, §3 "이 RFC가 처음으로 드러낸 것"을 "새로 발견한 사실"이
  아니라 "기존 Evidence의 공백"으로 명확히 구분).
- 책임의 존재·명칭·범위를 재론했는가 — **아니오**(§1, 전제로만
  인용).
- Process/Thread/Subprocess를 최종 확정했는가 — **아니오**(§4,
  권고까지만).
- 정확성·격리·동시성·실패/Retry·비용·복잡도 여섯 기준 모두
  비교했는가 — **Pass**(§3 표).
- 비용 Evidence가 없다는 사실을 숨기거나 추정으로 대체했는가 —
  **아니오** — 세 전략 모두 "미측정"으로 명시했다(§2.1, §2.2,
  §2.3, §3).
- §6 "Runtime"과의 관계를 재론했는가 — **아니오**(`ADC-0014` §Q2
  전제 유지).
- `docs/decisions/adc/ADC.md`(ADC-02)를 다뤘는가 — **아니오**.
- `ADC-0008`·`ADC-0012`를 재론했는가 — **아니오**.
- Scheduler/Multi-Task/Workflow를 설계했는가 — **아니오**(§Out of
  Scope).
- Production Code를 수정했는가 — **아니오**.
- ADC, ADR 문서를 작성했는가 — **아니오**.
