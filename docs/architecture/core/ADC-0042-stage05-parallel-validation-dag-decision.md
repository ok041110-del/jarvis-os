# ADC-0042: Stage 05 Parallel Validation DAG — Decision (RFC-0039 후속)

## 목적

`RFC-0039-stage05-parallel-validation-dag.md`의 조사를 근거로, Stage 05를
6개 책임(Structure/Scope/AST/Dependency/Test/Review)의 Parallel
Validation DAG로 재설계하는 것을 Production Architecture로 채택할지
공식 Decision을 내린다. `ADC-0040`/`ADC-0041`과 동일한 판정 구조를
따른다.

---

## Q1. Independence 판정은 충분히 근거가 있는가

**예, 구조적 근거는 충분하다.** `RFC-0039`가 6개 책임 각각에 대해
8개 기준(Input/Output Dependency, Shared State, Mutation, Ordering,
Failure Dependency, 상호 결과 필요 여부, Race Condition)을 "책임의
본질" 기준으로 전수 조사했고, 특히 Review는 5개 타 책임 각각에 대해
개별적으로 의존성을 부정하는 근거를 제시했다(§2.6.1). 이 판정은
**추론/문서 기반으로 완결 가능한 질문**(A/B/C/D 분류)이며, 실제 Engine
실행 없이도 답할 수 있다는 점에서 `ADC-0040`/`ADC-0041`이 판정 불가
사유로 삼은 "Real Engine Evidence 필요"와는 **다른 종류의 질문**이다.

## Q2. 독립성 확인 ≠ Production 채택 — 이 구분이 유지되는가

**예.** `RFC-0039` §9.3이 스스로 이 구분을 명시했다 — "구조 자체는
채택(Accept)"과 "Production 구현 승인"은 다르다. 6개 책임이 논리적으로
독립적이라는 것을 안다고 해서, 실제로 그렇게 구현했을 때의 latency/
cost/failure rate/Isolation 메커니즘의 실제 정확성까지 보장되지 않는다
— 이 Gap은 Real Execution Evidence로만 메워진다.

## Q3. Case A(현재 순차 구조) 유지가 여전히 안전한 선택인가

**예.** Stage 05는 현재 순차 구조(4개 결정적 검사 + Code Review)로
Production에서 정상 동작 중이며(`stage_05.py`, `test_stage_05.py`),
이 ADC가 Case A를 유지하는 데 드는 추가 비용은 없다.

---

## Decision

**PARTIAL — Independence CONFIRMED, Production Adoption NOT
DETERMINED.**

이 Decision은 `ADC-0040`/`ADC-0041`의 순수 NOT DETERMINED와 다르게,
두 개의 서로 다른 질문에 서로 다른 확정도로 답한다 — 이를 뭉뚱그려
하나의 판정으로 표현하지 않는다(과장 방지).

### 확정하는 것 — Independence 판정(구조적 근거로 확정 가능)

| Responsibility | Parallel Verdict |
|---|---|
| Structure | **A(Fully Independent)** |
| Scope | **A(Fully Independent)** |
| AST | **A\*(Fully Independent, Context 선-스냅샷 전제)** |
| Dependency | **A(Fully Independent)** |
| Test | **B(Independent with Isolation/Coordination)** |
| Review | **A\*(Fully Independent, Context 선-스냅샷 전제, 5개 전부 개별 확인)** |

`RFC-0039` §9.1의 표와 근거를 그대로 확정한다 — 재론하지 않는다.

### 확정하지 않는 것 — Production 채택(Real Execution Evidence 필요)

`ADOPT`(6-way Parallel DAG를 그대로 Production 구현)/`KEEP`(현재
순차 구조 Freeze)/`REJECT` 어느 것도 이번 세션에서 근거를 갖추지
못했다:

- 실제로 6개 Node를 동시 실행했을 때의 실측 latency 개선 폭 — 0건.
- Test의 격리 실행 메커니즘(Process/Subprocess)이 실제로 Context
  선-스냅샷과 함께 Race Condition을 제거하는지의 실측 검증 — 0건.
- `VerificationResult` Contract 재설계가 상위 Workflow(`workflow.py`
  등)와의 연결성을 깨지 않는지의 실제 확인 — 0건.
- Review를 Deterministic/LLM/Hybrid 중 무엇으로 구현할 때 실제
  결함 탐지율이 어떻게 달라지는지 — 0건(`RFC-0039` §8).

### 이 Decision이 하는 것

- `RFC-0039`의 Independence 판정표(§9.1)를 공식 기록으로 확정한다 —
  향후 어떤 세션도 이 6개 책임의 독립성을 처음부터 재조사할 필요
  없이 이 표를 인용할 수 있다.
- Test가 유일하게 A가 아닌 이유(공유 파일 mutation)와 그 해소 방법
  (Context 선-스냅샷 + 격리 실행)을 공식 기록으로 확정한다.
- Case A(현재 순차 구조)를 **잠정 유지**한다.
- `RFC-0039` §5가 제시한 목표 DAG 수정안(Context 노드에 원본 스냅샷
  확보 책임 명시)을 **향후 재설계 시 채택해야 할 방향**으로
  기록한다 — 지금 그 방향으로 구현하라는 뜻은 아니다.

### 이 Decision이 하지 않는 것

- Stage 05의 실제 재구현(`stage_05.py` 변경, 6개 Node 함수 분리,
  Aggregator 구현) — 전부 미착수.
- `VerificationResult`/`stages/contracts.py` Contract 변경 — 전부
  무변경.
- `stages/05_validation/RESPONSIBILITY.md`/`CAPABILITIES.md`/
  `VALIDATION.md` 변경 — 전부 무변경(단, `RFC-0039`가 참고자료로
  인용했을 뿐 원문은 무수정).
- Test 격리 실행의 구체적 메커니즘 설계 — 미착수.
- Review 구현 방식(Deterministic/LLM/Hybrid) 확정 — 미착수.

---

## Validation Requirements — Production Adoption을 재판정하려면 필요한 것

1. **Context 선-스냅샷 + Test 격리 실행의 실제 구현 및 검증**: 실제로
   원본 파일 스냅샷을 Fan-out 이전에 확보하고, Test가 격리된 사본에서
   동작하는 최소 PoC를 만들어 Race Condition이 실제로 발생하지 않음을
   확인한다(`IMPLEMENTATION_RULES.md` Execution Host §16.3/ADC-0015
   범위 안에서, Thread 미사용).
2. **실제 Engine 실행**: 6개 Node를 실제로(최소 Structure/Scope/AST/
   Dependency/Test는 Engine 미호출이므로 즉시 가능, Review는 실제
   Engine 확보 후) 동시 실행해 latency 개선 폭을 실측한다.
3. **Contract 재설계안 확정**: `VerificationResult`를 6-Node Result +
   Aggregator 병합 구조로 바꾸는 구체적 스키마를 별도 RFC로 설계하고,
   상위 Workflow(`workflow.py`/`teams/validation/team.py`)와의 연결이
   깨지지 않음을 확인한다 — `ADR-0009` Public Scope 변경 절차(RFC →
   ADC → ADR)를 따른다.
4. **Review 구현 방식 결정**: Deterministic/LLM/Hybrid 중 무엇을 쓸지
   별도 Evidence 기반으로 결정한다(`RFC-0039` §8이 선택지만 제시).
5. **Multi-Task 허용 범위(ADC-0016) 사전 확인 요건 충족**: "동시
   실행되는 각 Task가 서로 다른 파일/Artifact 이름공간에 쓰거나
   아무것도 쓰지 않는다"는 조건이 **구현 착수 전에** 실제로 확인돼야
   한다(ADC-0016 §Q4) — 1번의 결과가 이 조건을 충족하는지 별도로
   재확인한다.

## Open Questions

- `ParallelRunner`(ThreadPoolExecutor, Stage 01 선례)를 Structure/
  Scope/AST/Dependency/Review(LLM일 경우)의 병렬 실행에 재사용할 수
  있는가 — 이는 I/O-bound Engine 호출 병렬화이므로 유력하나, Test는
  파일 mutation이 있어 별도 메커니즘(Process/Subprocess)이 필요할
  가능성이 높다 — 두 메커니즘을 하나의 Aggregator가 함께 조율하는
  방법은 Not Determined.
- `RFC-0038`/`ADC-0041`(QA Agent 활성화)과 이 ADC(6개 책임 Parallel
  DAG)는 서로 다른 축의 조사다 — QA Agent가 실제로 활성화되면 이는
  "Review와 별개의 7번째 책임"이 되는지, 혹은 Review 범위 안에
  흡수되는지는 이 ADC가 답하지 않는다(Not Determined, 별도 조사
  필요).

## ADR 여부

**이번 세션에서 ADR을 작성하지 않는다.** Production Adoption이
TRANSITION이 아니라 NOT DETERMINED이므로, `ADC-0040`/`ADC-0041`이
세운 것과 동일한 원칙을 따른다. Independence 판정 자체(Q1)는 확정됐지만,
이는 ADR이 다루는 "Production Architecture 채택"이 아니라 이 ADC
자신이 다루는 "구조적 사실 확인"이다.

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: `stage_05.py` 변경, 6-Node 분리 구현,
Aggregator 구현, Contract 변경, `RESPONSIBILITY.md`/`CAPABILITIES.md`/
`VALIDATION.md` 변경. 문서 2건(이 ADC + `RFC-0039`)만 추가했다.

## Self Review

- Independence 판정과 Production 채택 판정을 하나로 뭉뚱그렸는가 —
  **아니오**(§Decision이 명시적으로 두 축으로 분리).
- Real Engine Evidence 없이 Production Architecture를 승인했는가 —
  **아니오**(NOT DETERMINED로 명시, Independence 판정만 확정).
- `RFC-0039`가 제시한 목표 DAG 수정안(Context 선-스냅샷)을 확정된
  Production 설계처럼 서술했는가 — **아니오**("향후 재설계 시 채택해야
  할 방향"으로만 기록).
- Stage 04/05 선행 ADC(`ADC-0040`/`ADC-0041`)와 동일한 판정 구조·
  엄밀성을 적용했는가 — **Pass**(Q1~Q3, Decision, Validation
  Requirements 형식 동일, 단 Q1의 성격 차이를 명시적으로 구분).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다
  (PR은 사용자 지시에 따라 생성하지 않는다).

## Related

- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`
- `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`,
  `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md`(동일
  판정 구조 선례)
- `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md`(`ParallelRunner` 선례)
- `hqs/development/IMPLEMENTATION_RULES.md`(Execution Host §16.3
  ADC-0015, Multi-Task §16.4 ADC-0016)
- `hqs/development/stages/05_validation/`
