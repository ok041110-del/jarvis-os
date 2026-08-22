# RFC-0012: Dispatch Component의 Architecture Boundary (RFC-0010 C1 / RFC-0011 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Phase 7 Kernel Component Architecture 판단 후속)
**대상**: `PHASE5-KERNEL-CANDIDATE-0001.md`/Phase 6 Prototype이 도메인 독립성을 실증한 "Parallel Execution 원시 기법"(`ThreadPoolExecutor.submit()`+`.result()`로 독립 Task를 동시에 `call_engine()` 호출)을, 기존 `core/execution/pipeline.py`(Specification→Artifact 변환)와 별개의 **Dispatch 책임**으로 Kernel 안에 둘 수 있는지 — 그 최소 경계만 연다. **위치의 실제 선택, 설계, 구현은 다루지 않는다.**
**Evidence**: `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`(`core/execution/` 정의, 줄 55), `docs/architecture/baseline/BASELINE.md` §16.2(Execution Layer Accept), `docs/research/PHASE4-HQ-CROSS-VALIDATION-0001.md`, `docs/research/PHASE5-KERNEL-CANDIDATE-0001.md`, `docs/research/PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md`, `projects/kernel-parallel-execution-prototype/EVIDENCE.md`, `core/execution/pipeline.py`, `core/execution/tests/test_pipeline.py`, `docs/architecture/core/RFC-0010-engine-caller-location-boundary.md`, `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`, `docs/architecture/core/RFC-0011-standalone-execution-location-boundary.md`, `docs/architecture/core/ADC-0011-standalone-execution-location-boundary.md`, `docs/architecture/core/COMPONENT-CANDIDATE-0001-kernel-component-architecture-review.md`, `docs/architecture/core/CLOSURE-0001-architecture-research.md`, `docs/research/PHASE9-CLOSURE-0001.md`

> 본 RFC는 Dispatch Component의 실제 위치를 선택하지 않는다. Interface
> 시그니처를 확정하지 않는다. Engine Adapter/Gateway/Registry/Scheduler를
> 설계·구현하지 않는다. `core/execution/pipeline.py`를 수정하지 않는다.
> `hqs/` 코드를 수정하지 않는다. Checkpointing을 다루지 않는다.
> `RFC-0010`/`ADC-0010`의 C1~C6, `RFC-0011`/`ADC-0011`의 Boundary
> Question, `PHASE9-CLOSURE-0001`의 Engine Adapter Defer 판정을
> 재조사하지 않는다 — 기존 결정으로만 인용한다.

## 0. 이 RFC가 열린 이유와, 왜 기존 RFC-0010/0011을 재론하는 것이 아닌지

`ADC-0010`(Engine Caller 위치)은 caller 후보 6개(C1 Kernel Engine
Port/Adapter, C2 Runtime, C3 Session, C4 Development HQ, C5 Dogfooding
스크립트, C6 별도 스크립트/함수) 전부를 **Not Accepted (based on
current evidence)**로 종결했다. `RFC-0011`은 C6("별도 실행 위치")를
공식 Concept으로 인정할 수 있는지를 물었고, 그 후속 `ADC-0011`도
동일하게 Not Accepted로 종결했다. `COMPONENT-CANDIDATE-0001`(구
세션의 "Phase 7" — 이번 문서와 이름만 같고 계보상 무관한 별개
검토)은 Execution을 포함한 8개 Kernel Component 후보 전부를 "RFC
채택 기준 미충족"으로 판정했다. `CLOSURE-0001`은 Kernel Component
Architecture 재개의 주된 결여 요인을 **Runtime Observation 부족**으로
지목하고, 재개 Trigger를 전부 "관찰" 조건으로 명시했다(예: Engine
Gateway "Engine 수 ≥ 2", 현재도 미충족).

**이 RFC는 그 종결을 뒤집지 않는다.** C1~C6 중 어느 것도 다시
Accept하지 않는다. 대신 `ADC-0010`이 C1(Kernel Engine Port/Adapter)에
대해 남긴 두 문구를 근거로 삼는다 — 판단: *"실체가 없어 지금 caller
역할을 할 수 없다"*, 그리고 부족한 Evidence 1번: *"Kernel Component
Architecture 설계 착수(현재 §10 Out of Scope) — 이 자체가 여러 선행
조건(Kernel Module Defer 3건, ADC-01·02, Engine 수 ≥2 등)에 걸려
있다."* 이 RFC는 이 두 문구가 가리키는 **선행 설계 착수의 최소
단위**를 연다. 범위는 C1 전체(Engine 호출 일반)가
아니라, `PHASE5-KERNEL-CANDIDATE-0001.md`가 Kernel Candidate로 확정한
좁은 부분집합 — 동시성 Dispatch(Parallel Execution 원시 기법) —
로 한정한다.

**새 Observation의 성격**: `RFC-0010`/`RFC-0011`/`COMPONENT-CANDIDATE-0001`/`CLOSURE-0001`
작성 시점에는 존재하지 않았던 Evidence가 이후에 추가됐다 — Phase 6
Prototype이 제3의 중립 도메인에서 이 기법을 독립 재구현해 재현했다
(Dev HQ, Investment HQ에 이은 **세 번째 독립 맥락**, `PHASE5`/`PHASE6`
Evidence). 다만 이것이 `CLOSURE-0001`이 명시한 특정 Trigger("Engine
수 ≥ 2")를 충족한다고는 주장하지 않는다 — 그 Trigger는 여전히
미충족이다(§9에서 별도로 기록). 이 RFC는 그와 **다른 성격의
Observation**(동일 기법의 3회 독립 재현)이 선행 설계 착수의 근거가 될
수 있는지를 여는 것이며, 이 판단 자체도 후속 ADC로 위임한다.

---

## 1. 문제 정의 및 Motivation

`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md`가 코드·계약 수준
Evidence로 확인한 사실: `core/execution/pipeline.py`는 자신의 계약
테스트(`test_no_ai_or_runtime_symbols_present_in_module`)로 `call_engine`/`subprocess`
등 실제 호출 관련 심볼의 소스 존재 자체를 금지한다 — 즉 "실제 Engine
호출"은 이 모듈의 계약 밖에 있다. 그런데 `BASELINE.md` §16.2는 Execution
Layer Kernel Module의 책임을 "Model/Engine 선택·호출까지의 경계"로
이미 Accept했다 — **Accept된 책임의 일부가 현재 어느 Kernel 코드에도
실체화되어 있지 않다.**

Motivation은 이 공백을 메우는 것이 아니라(공백을 메우는 것은 이 RFC의
권한 밖 — Implementation), **그 공백을 메우려 할 때 지켜야 할 최소
경계를 먼저 정의**하는 것이다. `ADC-0010` C1이 "설계 선행 필요"라고
남긴 지점을, Kernel Component Architecture 전체가 아니라 Phase
5/6이 확정한 좁은 범위(Dispatch)로 한정해 여는 것이 이 RFC의
Motivation이다.

---

## 2. 기존 Execution Layer와 Dispatch의 책임 경계

`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` §1~§4를 그대로 인용한다
(재조사 아님).

| | Execution Layer(`pipeline.py`) | Dispatch(Candidate) |
|---|---|---|
| 책임 | Specification → Result Artifact 변환(6 Builder) | Artifact(또는 Prompt)를 실제 Engine에 전달하고 결과를 회수 |
| 실제 Engine 호출 | 계약으로 금지(`test_no_ai_or_runtime_symbols_present_in_module`) | 계약의 존재 이유 자체 |
| 상태/부작용 | 없음(순수 함수) | 있음(실제 프로세스 실행) |
| §16.2 Accept 범위 내 위치 | 경계 내부(Specification 변환 부분) | 경계 내부이나 "내부 구조"(Open)로 남은 부분 |

두 책임은 순서 관계(Specification 완료 → Dispatch 수행)로 잠정
관찰되며, 대체 관계가 아니다. 이 관찰은 Phase 7이 이미 코드
Evidence로 확인한 것이며, 이 RFC가 새로 만든 것이 아니다.

---

## 3. Dispatch Component의 책임/비책임(제안, 미확정)

**책임(제안)**: 완성된 Prompt(또는 Prompt에 준하는 Artifact)를 받아
실제 Engine 호출을 수행하고, 단일/동시 호출 여부와 무관하게 결과를
호출자에게 반환한다.

**비책임(제안)**: Specification/Artifact 구성(Execution Layer 책임),
Task 배분·Workflow 순서 결정(Task/Workflow 후보 영역, `COMPONENT-CANDIDATE-0001`
C-2가 이미 "독립 Component로 설계할 Evidence 없음"으로 판정, 재조사
안 함), Agent/Capability 판단(HQ 책임, §7 Frozen), 영속화(Checkpointing —
명시적으로 이 RFC 범위 밖).

이 항목들은 **제안일 뿐 확정이 아니다** — Interface 시그니처, 클래스
구조, 실제 채택 여부는 후속 ADC/구현 단계의 판단 대상이다.

---

## 4. 입력/출력 Contract(제안, 미확정)

- **입력(제안)**: 완성된 Prompt 문자열 1개 이상(단일 호출은 1개,
  Dispatch는 N개의 독립 Prompt 집합).
- **출력(제안)**: 각 입력에 대응하는 결과 문자열(또는 예외).
- Execution Layer의 `ExecutionResult`(`str`)를 그대로 입력으로 받을
  수 있는지, 아니면 별도 형식이 필요한지는 **미확정**이다 —
  `ExecutionResult`가 다단계 Markdown 텍스트(`## Results` 포함)이고
  Phase 6 Prototype의 입력은 단순 Prompt 문자열이었다는 차이가
  있다(Phase 6 Prototype은 `core/execution/`을 전혀 경유하지 않았다
  — `PHASE6` `EVIDENCE.md` "관찰되지 않은 것" 참조). 이 차이의 해소는
  이 RFC가 다루지 않는다.

---

## 5. Artifact → Dispatch → Engine/Provider Dependency 방향(제안)

`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` §5를 그대로 인용한다.
Artifact(Execution Layer 산출물) → Dispatch(입력으로 소비) → Engine/Provider(실제
호출 대상)의 단방향을 제안한다. 역방향(Dispatch가 Builder를 호출)은
책임 역전이므로 배제를 제안한다. **이 방향은 제안이며, 후속 ADC가
채택하지 않는 한 Contract가 아니다.**

---

## 6. Sequential / Parallel 실행 책임의 위치

Phase 5/6 Evidence가 확정한 것은 "독립 Task를 `ThreadPoolExecutor.submit()`+`.result()`로
동시 호출하는 원시 기법"뿐이다 — Sequential 호출(현재 두 HQ의
`call_engine()` 단일 호출)과 Parallel 호출(Wave/Prototype)이 **같은
Dispatch 책임의 두 가지 실행 모드**인지, 아니면 서로 다른 책임인지는
Evidence가 결정하지 않는다. 관찰된 사실만 기록한다: 두 HQ 모두 동일한
`call_engine()` 함수를 Sequential/Parallel 양쪽에서 재사용했다(`PHASE4`
Evidence) — 즉 최소한 **호출 대상 함수는 공유**된다. Dispatch가 이
공유를 Component 경계로 삼아야 하는지는 후속 ADC 판단 대상이다.

---

## 7. 성공/실패 및 Exception 전파 기본 원칙(Evidence 기반, 확정 아님)

Phase 6 Prototype이 실측한 것만 원칙 후보로 제안한다:

- 동시 제출된 Task 중 하나의 실패(`FileNotFoundError`)는 그 Task의
  `.result()` 호출 지점에서만 재발생하고, 같은 Pool의 다른 정상 Task
  결과에 영향을 주지 않았다(`PHASE6` `EVIDENCE.md` VALIDATION 항목 5).
- 이는 `ThreadPoolExecutor` 자체의 표준 동작이며, Dispatch Component가
  별도 예외 처리·재시도·Checkpointing 계층을 추가로 요구하지 않고도
  이 정도의 격리가 이미 확보됨을 보여준다(**Checkpointing과의 결합은
  이 RFC 범위 밖 — 이미 제약으로 명시**).

이 관찰이 Dispatch Component의 공식 계약(예: "한 Task의 실패가 다른
Task를 오염시키지 않아야 한다")으로 승격될지는 확정하지 않는다 —
Evidence는 3개 Task, 1개 인위적 실패 시나리오로 한정되어 있다(Phase
6 Evidence "관찰되지 않은 것": 4-way 이상 병렬, 장시간 Task 미검증).

---

## 8. 현재 `call_engine()`과의 관계

`hqs/development/mvp/engine.py`의 `call_engine()`은 Dispatch가 실제로
호출할 대상 함수의 **현재 유일한 실사용 구현**이다(`PHASE4` Evidence:
Investment HQ가 이 함수를 live import로 공유). Phase 6 Prototype의
`engine_caller.py`는 이 함수를 의도적으로 import하지 않고 독립
재구현했다 — 도메인 독립성 검증이 목적이었기 때문이다(`PHASE6`
`EVIDENCE.md` 참조). 이 RFC가 확인하는 것은 **두 사실 사이의 아직
풀리지 않은 질문**뿐이다: Dispatch Component가 실제로 채택된다면
HQ의 `call_engine()`을 그대로 호출 대상으로 삼을지, 아니면 별도
Interface를 그 위에 둘지 — 이 질문은 `ADC-0010`이 C1~C6를 판단할 때
답하지 않은 것과 같은 미결 영역이며, 이 RFC도 답하지 않는다.

---

## 9. 향후 Engine Adapter와의 관계

`BASELINE.md` §7이 "Engine 호출의 표준 인터페이스 제공(Port/Adapter)"을
Jarvis OS(Kernel) 책임으로 Frozen해 뒀고, `PHASE9-CLOSURE-0001`이
Engine Adapter 도입을 **NEED-DRIVEN DEFER**로 종결했다(재검토 조건:
"두 번째 실제 Engine이 추가될 때", 현재 Engine 수 1 — **이 RFC
작성 시점에도 미충족**). `RFC-0011` §5는 "별도 실행 위치가 도입된다면
그 위치가 하는 일이 Engine Adapter와 같은 것인지 다른 것인지가
반드시 구분되어야 한다"고 명시했다.

**이 RFC는 그 구분을 시도하지 않는다.** Dispatch Component(제안)는
"표준 인터페이스 제공"(Adapter의 정의)이 아니라 "기존 공개 함수(`call_engine()`)를
그대로 호출자로서 순서대로/동시에 호출하는 것"이라는 차이가 있어
보이지만(Phase 6 Prototype이 새 Interface를 만들지 않고 기존 함수
시그니처만 재사용했다는 사실이 이 차이의 근거 후보다), 이 차이가
Engine Adapter Defer 판정과 충돌하지 않는지는 **후속 ADC가 명시적으로
판단해야 한다** — 이 RFC가 임의로 "다르다"고 확정하지 않는다.

---

## 10. 기존 `core/execution/pipeline.py`와의 호환 관계

`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` §6·§8을 그대로 인용한다.
`pipeline.py`는 수정하지 않는다 — 자체 계약 테스트가 실제 호출을
명시적으로 배제하고 있으므로, 이 모듈을 확장해 Dispatch 책임을
넣는 것은 이 RFC가 승인하지 않는다. "이 모듈이 Dispatch 앞단
(Specification 전용)으로 남을지, 계약을 넓혀 Dispatch까지 포함할지"는
후속 ADC 대상이다.

---

## 11. HQ가 Dispatch를 어떻게 소비하는지의 방향(제안, 미확정)

현재 두 HQ(`hqs/development/`, `hqs/investment/`)는 각자의 코드 안에서
직접 `call_engine()`을 호출하고 직접 `ThreadPoolExecutor`를 구성한다
(`PHASE4` Evidence). Dispatch Component가 Kernel에 실제로 자리잡는다면,
HQ가 이를 소비하는 방향은 두 가지 후보가 있을 수 있다 — (a) HQ가
Dispatch를 직접 import해 호출, (b) 현행 유지(HQ가 각자
`ThreadPoolExecutor`를 구성). **이 RFC는 둘 중 하나를 선택하지 않는다.**
`RFC-0010` §3(Pattern)이 "Development HQ는 caller 후보로 검토된 적이 없는
정도가 아니라, Engine Adapter/Model Routing 관련 책임에서 명시적으로
제외됐다"고 확인한 사실은, HQ가 Dispatch의 **제공자**가 아니라
**소비자**일 가능성만 시사할 뿐, 소비 방식을 결정하지 않는다.

---

## 12. Migration 범위와 비범위

`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` §9를 그대로 인용한다.

**범위에 포함될 수 있는 것(제안, RFC 승인 이후에만)**: 신규 하위
구조(가칭 `core/execution/dispatch/` 또는 별도 Kernel 하위 Component)에
Parallel Execution 원시 기법을 이관.

**범위에서 명시적으로 제외되는 것**: `pipeline.py` 수정, HQ의 기존
`call_engine()`/`ThreadPoolExecutor` 코드 즉시 치환, Checkpointing
전부(Investment-specific 상태 유지, `PHASE5-KERNEL-CANDIDATE-0001.md`
판정 그대로), Engine Adapter/Gateway 신규 설계·구현, Registry/Scheduler/Runtime
신규 설계·구현.

---

## 13. Alternatives 및 Reject 이유

| 대안 | 내용 | Reject 이유 |
|---|---|---|
| A. 지금 바로 Migration 실행 | Phase 6 PASS를 근거로 즉시 `core/`에 Dispatch 코드 작성 | `ADC-0010` C1이 이미 "설계 선행 필요"로 Not Accepted 판정한 것을 절차 없이 우회하는 것 — Frozen Architecture 규칙 위반 |
| B. `pipeline.py`를 확장해 호출 로직 추가 | 별도 Component 없이 기존 모듈에 병합 | `pipeline.py` 자체의 계약 테스트가 실제 호출 심볼을 금지 — 기존 계약을 깨뜨림(§10) |
| C. 아무것도 하지 않고 Phase 6로 종료 | RFC를 열지 않고 Prototype Evidence만 남김 | `ADC-0010` C1이 명시한 "Kernel Component Architecture 설계 선행"이라는 전제 조건에 대해 아무 진전도 없음 — Phase 5/6이 확정한 유일한 Kernel Candidate가 영구히 미착수 상태로 남음 |
| D(채택 후보). 좁은 범위 RFC로 선행 설계 착수 | 이 문서 — Dispatch만 한정해 경계만 연다 | C1의 요구를 최소 단위로 충족하면서, `COMPONENT-CANDIDATE-0001`/`CLOSURE-0001`이 확인한 "관찰 부족" 문제를 새 Evidence(3회 독립 재현)로 부분적으로 메운다 |

---

## 14. Open Questions

1. §4의 입력/출력 형식 — `ExecutionResult`(Markdown 텍스트)와 Phase
   6 Prototype의 단순 Prompt 문자열 사이의 형식 차이를 어떻게 다룰지.
2. §6 — Sequential/Parallel이 하나의 Dispatch 책임인지 별개인지.
3. §8 — Dispatch가 HQ의 `call_engine()`을 직접 호출 대상으로 삼을지,
   별도 Interface를 그 위에 둘지.
4. §9 — Dispatch가 "Engine Adapter"와 같은 것인지 다른 것인지(`RFC-0011`
   §5가 이미 요구한 구분, 아직 아무도 답하지 않음).
5. §11 — HQ가 Dispatch를 소비하는 구체적 방식.
6. `CLOSURE-0001`이 명시한 "Engine 수 ≥ 2" Trigger가 여전히
   미충족인 상태에서, 이 RFC가 여는 좁은 선행 설계가 그 Trigger를
   우회하는 것은 아닌지 — 후속 ADC가 이 RFC 자체의 절차적 정당성도
   함께 판단해야 한다(§9 참조).

---

## 15. RFC 이후 ADC/ADR에서 확정해야 할 사항

후속 ADC(신설 예정)가 판단해야 할 것:

1. 이 RFC를 여는 것 자체가 절차적으로 정당한지 — `ADC-0010` C1의
   "설계 선행 필요"를 이 시점에 열 근거로 Phase 6 Evidence(3회 독립
   재현)가 충분한지, 아니면 `CLOSURE-0001`의 "Engine 수 ≥ 2" Trigger
   미충족을 이유로 Not Accepted(추가 관찰 대기)로 다시 남길지.
2. §14의 6개 Open Question 중 이번 ADC 사이클에서 결정 가능한 것과
   후속 RFC로 미룰 것의 구분.
3. Dispatch Component와 Engine Adapter의 관계(§9) — 같은 것으로
   판단되면 이 RFC 트랙 전체가 `PHASE9-CLOSURE-0001`의 Engine
   Adapter Defer 판정과 충돌하므로 재검토가 필요하다는 것도 함께
   기록해야 한다.
4. ADR 필요 여부 — `ADC-0010`/`ADC-0011`이 그랬듯 "Not Accepted
   (based on current evidence)"로 종결되면 **No ADR Required**(Boundary가
   이동하지 않으므로)와 동일한 논리가 적용될 가능성이 높다. Accept로
   판단될 경우에만 ADR이 필요하다.

---

## Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 연다.

**Phase 5/6이 확정한 Parallel Execution 원시 기법을 위한 "Dispatch"
책임을, `ADC-0010` C1(Kernel Engine Port/Adapter)의 좁은 부분집합으로서
지금 설계 착수 대상으로 삼을 수 있는가 — 아니면 `CLOSURE-0001`의
Trigger(Engine 수 ≥ 2, 여전히 미충족)가 채워질 때까지 계속 대기해야
하는가?**

---

## Out of Scope

- Dispatch Component의 실제 위치 선택.
- Interface 시그니처, 클래스/모듈 구조의 확정.
- `core/execution/pipeline.py`, `hqs/development/`, `hqs/investment/`
  코드 수정.
- Checkpointing 설계.
- Registry/Scheduler/Runtime/Engine Gateway 신규 설계·구현.
- `RFC-0010`/`ADC-0010`의 C1~C6, `RFC-0011`/`ADC-0011`의 Boundary
  Question, `PHASE9-CLOSURE-0001`의 Engine Adapter Defer 재조사.
- `COMPONENT-CANDIDATE-0001`의 8개 후보 재조사(Execution/C-4 포함).
- ADC-01(Model↔Component 대응)·ADC-02(Runtime 존폐) 재조사.
- 새로운 실험(Phase 6 Prototype 재실행 포함).

## Non-goals

- 이 RFC는 Dispatch 위치를 결정하지 않는다.
- 이 RFC는 새 Component/Interface를 설계하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — 이미 기록된 Phase 4/5/6/7
  Evidence와 기존 RFC-0010/0011/COMPONENT-CANDIDATE-0001/CLOSURE-0001/PHASE9-CLOSURE-0001만
  인용했다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 Boundary Question에 답하지 않는다.
- 이 RFC는 C1~C6, ADC-01·02, Execution Result Consumer, `COMPONENT-CANDIDATE-0001`의
  8개 후보를 재조사하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §15-1 — 이 RFC를 지금 여는 것의 절차적 정당성(Phase 6 Evidence
   vs `CLOSURE-0001` Trigger 미충족).
2. 정당성이 인정되면 §14 Open Question을 `ADC-0008`·`ADC-0009`·`ADC-0010`·`ADC-0011`과
   동일한 방식(Not Accepted 시 억지로 선택하지 않음)으로 하나씩 판단.
3. 정당성이 인정되지 않으면, Dispatch Component 논의를 `CLOSURE-0001`의
   Trigger 충족 시점까지 다시 대기 상태로 명시적으로 되돌린다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(RFC → ADC → ADR)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. Structure v1.0, `BASELINE.md`
  §16.2, Phase 4/5/6/7 문서, `core/execution/pipeline.py`와 그 테스트,
  기존 RFC-0010/ADC-0010/RFC-0011/ADC-0011/`COMPONENT-CANDIDATE-0001`/`CLOSURE-0001`/`PHASE9-CLOSURE-0001`에
  실제로 기록된 내용만 인용했다. 새 실험은 하지 않았다.
- Dispatch 위치를 선택했는가 — **아니오**. §13은 대안을 나열했을
  뿐 실제 위치를 정하지 않았고, §D(채택 후보)도 "RFC를 여는 것"까지만
  제안한다.
- `RFC-0010`/`ADC-0010`의 C1~C6, `RFC-0011`/`ADC-0011`의 Boundary
  Question을 재조사했는가 — **아니오**. §0·§9·§11에서 상태만 인용했다.
- `COMPONENT-CANDIDATE-0001`의 8개 후보를 재조사했는가 — **아니오**.
  §2·§3에서 Execution/C-4 관련 기존 판정만 인용했다.
- `PHASE9-CLOSURE-0001`의 Engine Adapter Defer를 재론했는가 —
  **아니오**. §9에서 그 결론을 그대로 인용하고, 구분 필요성만 Open
  Question(§14-4)으로 남겼다.
- Phase 6 Prototype 결과를 Architecture 확정 근거로 과도하게
  확대했는가 — **아니오**. §0에서 `CLOSURE-0001`의 특정 Trigger(Engine
  수 ≥ 2)는 여전히 미충족임을 명시했고, "3회 독립 재현"이라는 다른
  성격의 Observation이라고만 기록했다 — 이 Observation이 충분한지
  자체를 §15-1에서 후속 ADC로 위임했다.
- 새 Component/Interface를 설계했는가 — **아니오**. §3·§4는 "제안"과
  "미확정"으로 명시했고, 후속 ADC/구현 이전에는 Contract가 아니라고
  명시했다.
- `core/execution/pipeline.py`, HQ 코드를 수정했는가 — **아니오**.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- 기존 Governance 문서와의 충돌을 확인하고 보고했는가 — **Pass**.
  §0에서 RFC-0010/RFC-0011/`COMPONENT-CANDIDATE-0001`/`CLOSURE-0001`과의
  중첩을 명시적으로 인정하고, 재론이 아니라 그 결론이 남긴 좁은
  후속 지점(C1의 "설계 선행 필요")만 여는 것임을 밝혔다.

## Correction Log

- 최초 작성본은 §0에서 `ADC-0010` C1 판단을 "책임은 이미 귀속되어
  있으나(Frozen), 실체가 없어 지금 당장 caller 역할을 할 수 없다 —
  Kernel Component Architecture 설계가 선행되어야 한다"는 **하나의
  인용문**으로 제시했으나, 이는 `ADC-0010`의 C1 판단 문장과 "부족한
  Evidence" 1번 항목을 합성한 것으로 원문에 그 형태의 문장이
  존재하지 않았다. 대조 결과 확인된 오류로, 두 원문 문구를 각각
  따로 인용하도록 수정했다(§0). §11의 인용 출처도 "RFC-0010 §2"에서
  실제 위치인 "RFC-0010 §3(Pattern)"으로 정정했다. 두 수정 모두
  인용 정확성 교정이며, RFC의 결론(Boundary Question 미답변,
  Not Accepted 트랙 재론 안 함)은 변경되지 않았다.
