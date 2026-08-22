# Experimental Evidence 0001 — Parallel Execution Scaling & ExecutionResult 결합

**문서 성격**: Governance v2 "Experimental Implementation" 원칙
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`)에 따른 Experimental
Observation이다. **RFC/ADC/ADR이 아니다.** 이 문서는 어떤 Architecture도
확정하지 않는다. `core/`, `hqs/`, Structure v1.0, Architecture Baseline,
Formal Component Contract 어느 것도 수정하지 않았다. `RFC-0012`는
Proposed, `ADC-0012`는 DEFER 그대로 유지되며, **이 문서의 어떤 결과도
그 상태를 자동으로 바꾸지 않는다.**

## 실험 목적

기존 `EVIDENCE.md`(Phase 6 Prototype)가 "관찰되지 않은 것"으로 명시한
세 가지 공백 — (1) 4-way 이상 병렬, (2) 장시간 Task, (3) `ExecutionResult`와의
결합 — 을 채운다. 대상 기법은 동일하다: `ThreadPoolExecutor.submit()`+`.result()`로
독립 Task를 동시에 `call_engine()` 호출하는 원시 기법(Phase 5 Kernel
Candidate).

## 환경

- `projects/kernel-parallel-execution-prototype/`(기존 디렉터리 확장,
  Phase 6 파일은 무수정) — 신규 파일 `run_experimental_scaling.py`,
  `execution_result_bridge.py`, 이 문서.
- Engine 호출: 기존 `engine_caller.py`(변경 없음) 재사용 — `hqs/`/`core/`
  실행 경로 의존 0건(정적 검사 재확인, 아래 §의존성 검사).
- Python 3.11.15, 실제 `claude` CLI subprocess 호출(모의/mock 아님).

## Task 구성

제3의 중립 도메인(자연 현상, Phase 6과 동일 계열)을 3개 → 6개로 확장:
tides, autumn_leaves, bread_rising, rainbow, ice_floats, thunder_delay.
각 프롬프트는 응답을 자기 주제의 고정 태그로 시작하도록 요구한다 —
결과 수집이 올바른 Task에 정확히 귀속되는지(교차 배정 없음)를 텍스트
내용으로 프로그램적으로 검증하기 위함이며, LLM 출력 자체의 결정론을
주장하는 것이 아니다.

## Sequential 결과

전체 6개 Task 순차 실행: **30.2s**(6건 전부 정상 응답 수신, 태그 일치).

## Parallel 결과 (A/B/C/D)

| 조건 | Task 수 | 소요 시간 | 비고 |
|---|---|---|---|
| A. Sequential(전체) | 6 | 30.2s | 기준선 |
| B. Parallel 2-way | 2 | 5.8s | 정상 |
| C. Parallel 3-way | 3 | 6.3s | 정상 |
| D. Parallel 4-way(1차) | 4 | 3.1s | **4/4 전부 콘텐츠 레벨 실패**(아래 §관찰된 이상 참조) — 시간값 무효 |
| D. Parallel 4-way(재실행) | 4 | 7.1s | 정상, 태그 일치 4/4 |
| Parallel 6-way(동일 Task 집합) | 6 | 9.3s | 정상, Sequential(30.2s) 대비 **3.25배** |

동일 Task 집합(6개 전부)으로 Sequential과 Parallel을 직접 비교했다 —
30.2s → 9.3s, 3.25배 단축. 이는 실제 동시 실행 없이는 불가능한 단축률이다.

## 관찰된 이상 — Parallel 4-way 1차 실행의 콘텐츠 레벨 실패

**실험 결과를 과장하지 않기 위해 있는 그대로 기록한다.** Parallel
4-way 1차 실행에서 4개 Task **전부**가 `"API Error: Unable to connect
to API: Self-signed certificate..."`로 응답했다 — `ThreadPoolExecutor`
자체는 정상 동작했으나(4개 모두 `.result()`가 즉시 반환), 그 내용이
실패였다. 이는 인위적으로 만든 실패가 아니라 실제 네트워크/프록시
계층에서 발생한 콘텐츠 레벨 실패이며, `hqs/investment/checkpoint.py`의
`_KNOWN_CONTENT_FAILURE_PREFIXES = ("API Error:",)`가 이미 알려진
시그니처로 다루고 있는 것과 **동일한 계열의 실패**다(Investment HQ
`pg-hq-verify` 등에서 4회 재현된 것과 같은 패턴).

`engine_caller.py`(이 Prototype 전용 최소 구현, `call_engine()`)는 —
Phase 6 원안 그대로 — 이 콘텐츠 레벨 실패를 감지하지 않고 문자열을
그대로 반환한다. **이것이 이 실험이 관찰한 Dispatch 자체의 한계다**:
`ThreadPoolExecutor`/`.result()` 메커니즘은 프로세스 레벨 예외(`FileNotFoundError`
등, 아래 §예외 전파 참조)는 정상 전파하지만, "프로세스는 성공 종료했으나
내용이 실패"인 경우는 Dispatch 계층에서 구분하지 않는다 — 이는 Investment
HQ의 `Checkpointer`/`ContentFailureError`가 이미 별도 계층에서 처리하고
있는 것과 동일한 책임이며, 이 실험이 새로 발견한 문제가 아니라 **기존
관찰의 재확인**이다.

같은 4-way 조합을 즉시 재실행하자 4/4 전부 정상 응답했다(태그 일치,
교차 없음) — 일시적 네트워크 상태였다는 것을 시사하지만, 재현 표본이
1건뿐이라 이를 "일시적"이라고 확정하지 않는다.

## 장시간 Task 시나리오

400~600단어를 요구하는 장문 Task(`long_water_cycle`) 1개를 짧은 Task
2개(tides, ice_floats)와 같은 Pool에 동시 제출:

- 총 소요 16.7s(180s Timeout 내 정상 종료).
- 완료 순서: `ice_floats` → `tides` → `long_water_cycle` — **장시간
  Task가 가장 나중에 완료됐다**(`long_task_finished_last: true`),
  즉 짧은 Task가 장시간 Task에 의해 지연되지 않았다.
- 3개 결과 전부 자기 태그와 일치, 교차 없음.

## 예외 전파

정상 Task 2개(rainbow, thunder_delay) + 존재하지 않는 바이너리를
호출하는 강제 실패 Task 1개(`forced_failure`, 실제 `subprocess`
예외)를 같은 Pool에 제출: 정상 2개는 `status: ok`로 정상 수신, 강제
실패는 `.result()` 호출 시 `FileNotFoundError`가 그대로 재발생했고
다른 두 Task는 오염되지 않았다 — Phase 6과 동일한 결론을 재확인했다.

## 결과 수집의 정확성(Deterministic Collection)

7개 배치(Sequential·2/3/4-way(1차 제외, API Error로 태그 검증 대상에서
자연 제외됨)·4-way 재실행·6-way·장시간 시나리오) 전체에서 태그-Task
귀속을 검사한 결과: **정상 응답을 받은 모든 케이스에서 mismatch
0건.** (1차 4-way의 "mismatch"로 잡힌 4건은 콘텐츠 자체가 API 실패
문자열이었기 때문이며 — 라우팅 오류가 아니다 — 재실행에서 4/4 전부
일치를 확인해 이 구분을 재확인했다.)

## ExecutionResult 결합 실험

`core/execution/pipeline.py`·`core/execution/mvp_0006/execution_result_builder.py`를
**읽기 전용으로 import**했다(수정 없음, `execution_result_bridge.py`).
Parallel 6-way 결과(`{task_name: text}`)를 `f"{task_name}: {text}"`
형태의 `list[str]`로 변환해 `build_execution_result(execution_state,
handle_id=..., produced_at=..., results=[...])`에 그대로 전달한 결과:

- **형식적으로 결합 가능함을 확인했다** — `combinable: true`, `## Results`
  절이 포함된 유효한 Execution Result Artifact가 생성됨(1170자, 데모
  기준).
- **이것이 확정하는 것은 그뿐이다.** Dispatch(Parallel Execution)와
  Execution Layer(`pipeline.py`)가 Architecture상 같은 Component라는
  뜻이 아니다 — `PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md` §3·§4가
  이미 코드·계약 수준에서 두 책임이 겹치지 않음을 확인했고(`pipeline.py`는
  `call_engine`/`subprocess` 심볼을 계약으로 금지), 이 실험은 그 판단을
  재조사하지 않는다.

## 의존성 검사

`run_experimental_scaling.py`, `engine_caller.py`(무수정) — `hqs`/`core`
import 정적 검사 **0건**. `execution_result_bridge.py`는 §목적 그대로
`core/execution`을 의도적으로 import하는 별도 파일이며, 이는 Dispatch
자체의 의존성이 아니라 이번 실험 한정의 결합 시험 코드다.

## 회귀 확인

`pytest --ignore=archive`: **187 passed**(기존과 동일, 변화 없음).
신규 실험 파일은 `test_` 접두어를 쓰지 않아 수집 대상이 아님(`--collect-only`로
확인).

## 한계

- 콘텐츠 레벨 실패(API Error)의 재현 표본이 1건뿐 — 이 실험의 목적
  (Dispatch 자체의 병렬성/예외 전파 검증)과 별개의 문제이므로 이 문서가
  그 원인을 추가로 조사하지 않는다.
- 8-way 이상, 또는 180s에 근접하는 실제 Timeout 경계는 이번에도
  검증하지 않았다.
- Checkpointing과의 결합은 이번에도 의도적으로 배제했다(`PHASE5-KERNEL-CANDIDATE-0001.md`
  판정 유지).
- `execution_result_bridge.py`의 결합 실험은 데모 수준(2개 결과)이며,
  6-way 전체 결과로도 형식은 동일하므로 별도로 반복하지 않았다.

## 8개 실험 질문에 대한 답

1. 재사용 가능한가 — **그렇다**, 3번째(Phase 6) 이후 이번이 4번째
   독립 실행이며 매번 동일 기법으로 성공.
2. Task 수 증가에도 동작하는가 — **그렇다**, 2/3/4/6-way 전부 정상
   동작(4-way는 재실행 포함).
3. 장시간 Task에서 안정적인가 — **그렇다**, 16.7s 내 정상 종료, 짧은
   Task를 지연시키지 않음.
4. 한 Task의 실패가 다른 Task에 영향을 주는가 — **아니오**(프로세스
   레벨 예외 기준). 단, **콘텐츠 레벨 실패는 Dispatch가 감지하지
   못한다**(이미 알려진 계열의 한계, 새로 발견한 것 아님).
5. 결과 수집이 deterministic한가 — **그렇다**(정상 응답 기준 mismatch
   0건).
6. `ExecutionResult`와 결합했을 때 책임 경계가 유지되는가 — **형식적
   결합은 가능하나, 책임 경계는 별개 문제로 유지된다** — 결합
   가능성이 책임 병합을 의미하지 않는다.
7. `pipeline.py`와 결합하지 않고도 독립적인 Dispatch 실험이 가능한가
   — **그렇다**, Dispatch 자체(`run_experimental_scaling.py`)는
   `core/`에 의존하지 않는다.
8. Formal Core Component로 승격할 만큼 추가 가치가 관찰됐는가 — **이
   문서는 그 판단을 내리지 않는다.** §Experimental 판정 참조.

## Experimental Evidence와 ADC-0012의 관계

이 문서가 만든 Evidence(4번째 독립 재현, 4/6/장시간 확장 검증)는 실재
하지만, `ADC-0012`가 명시한 재개 Trigger(Engine 수 ≥ 2 등, `docs/research/GOVERNANCE-TRIGGER-OBSERVATION-0001.md`
참조) 중 어느 것도 충족시키지 않는다 — 이번 실험도 여전히 Engine 1개
(Claude Code)만 사용했다. **`ADC-0012`의 DEFER는 이 문서로 자동
해제되지 않는다.** Formal Promotion을 시도하려면 여전히 기존
RFC → ADC → ADR 절차(및 그 재개 Trigger 충족)가 필요하다
(`docs/decisions/adc/README.md` "Experimental Implementation과의 관계"
원칙 그대로).

## Architecture/Contract 변경 여부

**없음.** `hqs/`, `core/`, Structure v1.0, Architecture Baseline,
Formal Component Contract, `roadmap.md`, RFC/ADC/ADR 어느 것도
수정하지 않았다. `core/execution/pipeline.py`는 읽기 전용으로
import만 했다. Registry/Scheduler/Runtime/Engine Gateway/Adapter를
만들지 않았다. `core/` Migration을 수행하지 않았다.
