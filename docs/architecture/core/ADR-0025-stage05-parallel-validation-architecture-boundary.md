# ADR-0025: Stage 05 Parallel Validation Architecture — Boundary

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0025` |
| 상태 | **Accepted — Architecture Independence/Isolation/Aggregation Boundary 확정(Scoped). Parallel Production Adoption 및 Review Validator LLM Adoption은 이 ADR이 결정하지 않는다 — 둘 다 `NOT YET DETERMINED`로 명시적으로 유보한다(§11, §12).** |
| Context | `RFC-0039-stage05-parallel-validation-dag.md` → `ADC-0042-stage05-parallel-validation-dag-decision.md` → `STAGE05-TEST-ISOLATION-VALIDATION-0001.md`(Test Isolation 실측) → 이 ADR |
| 관련 RFC | `RFC-0039`(6개 Validator 독립성 분석), `RFC-0038`(QA Agent Multi-Agent 경계, 별개 축) |
| 관련 ADC | `ADC-0042`(Independence 판정 확정, Production Adoption NOT DETERMINED) |
| 관련 Evidence | `docs/research/STAGE05-TEST-ISOLATION-VALIDATION-0001.md`(Test Workspace 실측), `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`(이 ADR과 함께 제출하는 실측 Harness 결과) |
| Governance Status 확인 | 이 저장소의 `docs/architecture/core/ADR-0001`~`ADR-0024` 전수 조사 결과, **모든 ADR의 Status는 "Accepted"(Scoped/Consolidation Only 등 수식어 동반) 계열뿐이다** — "Proposed"나 "NOT DETERMINED" 상태의 ADR 선례는 없다(NOT DETERMINED 판정은 전부 RFC/ADC 단계에서 멈추고 ADR을 작성하지 않았다 — `ADC-0040`/`ADC-0041` 자체가 이를 명시). 이 ADR은 그 관례와 다르게, **부분적으로 확정된 사실(Independence/Isolation/Aggregation)** 이 이미 존재하므로 그 부분만 Scoped Accept로 기록하고, 나머지(Production/LLM Adoption)는 여전히 ADC 수준의 NOT DETERMINED로 유지한다 — 임의의 새 상태명을 만들지 않고 기존 "Accepted(Scoped)" 어휘(`ADR-0015`/`ADR-0017` 선례)를 그대로 재사용한다. |

---

## 1. Context

Stage 05(Validation)는 현재 main에서 순차 구조(4개 결정적 검사 + Code
Review 1개, `hqs/development/stages/05_validation/stage_05.py`)로
Production에서 동작 중이다. `RFC-0039`가 사용자 요청에 따라 현재
구현을 Architecture 기준으로 삼지 않고, Stage 05의 책임을 6개
(Structure/Scope/AST/Dependency/Test/Review)로 재정의해 "책임의
본질" 기준으로 Parallel Validation DAG 채택 가능성을 조사했다.
`ADC-0042`가 그 결과(6개 중 5개 Fully Independent, Test만 Isolation
필요)를 확정했으나 Production 채택은 Real Execution Evidence 부재로
NOT DETERMINED로 유보했다. `STAGE05-TEST-ISOLATION-VALIDATION-0001.md`
가 Test Isolation 메커니즘(Workspace 복제 방식)을 실측으로 구체화했다.
이 ADR은 그 위에서 — 이번 세션이 만든 실측 Harness(`projects/
stage05-parallel-validation-harness-v1/`) 결과까지 반영해 — 무엇이
지금 확정 가능하고 무엇이 여전히 유보돼야 하는지를 공식화한다.

## 2. Problem

Stage 05를 6-way Parallel DAG로 재설계할지 결정하려면 최소한 다음
질문에 답해야 한다: (1) 6개 책임이 실제로 구조적으로 독립적인가,
(2) Test의 파일 mutation을 어떻게 격리하는가, (3) 병렬화가 실제로
latency 이득을 주는가, (4) Review에 LLM이 필요한가. (1)·(2)는
추론과 실측으로 답할 수 있는 질문이지만, (3)·(4)는 실제 실행
결과(비용·latency·품질)가 있어야만 답할 수 있는 질문이다 — 이 둘을
섞어서 하나의 "채택/비채택" 결정으로 뭉뚱그리면, 근거 없는 (3)·(4)의
답이 근거 있는 (1)·(2)의 답까지 오염시킨다.

## 3. Existing Evidence

| 출처 | 확인한 것 |
|---|---|
| `RFC-0039` §2, §9.1 | 6개 책임을 8개 기준으로 전수 분석 — Structure/Scope/Dependency는 조건 없이 A(Fully Independent), AST/Review는 원본 스냅샷을 Context 단계에서 선확보하면 A, Test는 공유 파일 mutation 때문에 B(Isolation 필요) |
| `RFC-0039` §2.6.1 | Review가 Structure/Scope/AST/Dependency/Test 5개 각각의 결과를 필요로 하지 않음을 개별적으로 확인 |
| `ADC-0042` | 위 Independence 판정을 공식 확정. Production Adoption은 NOT DETERMINED로 유보 |
| `STAGE05-TEST-ISOLATION-VALIDATION-0001.md` §1.3~§1.4 | "test/만 복제"는 실측으로 기각(FileNotFoundError 재현) — `.git` 제외 전체 working tree 복사가 251ms에 원본과 동일 결과(324 passed/6 skipped) 산출 |
| `STAGE05-TEST-ISOLATION-VALIDATION-0001.md` §1.5 | `execution_host.py::run_isolated()`(`ADC-0015` 기 채택)가 Process 격리 축을 이미 제공, Workspace 복제가 파일 시스템 격리 축을 제공 — 둘은 별개 메커니즘 |
| `projects/stage05-parallel-validation-harness-v1/`(이 세션 신규) | Single/Parallel 3회 반복 실측, Review 3-Case 실측, 7개 Failure Isolation 시나리오 실측 — 상세는 `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md` |

## 4. Architectural Options

### A. Single Sequential Validation(현재 Production 형태)

Structure → Scope → AST → Dependency → Test → Review, 순차 1개씩.
장점: 이미 Production에서 검증됨, 추가 복잡도 없음. 단점: Test의
~30초가 전체 latency를 그대로 지배.

### B. 6-way Parallel Validation

Structure/Scope/AST/Dependency/Test/Review를 동시에 시작하고
Aggregator가 종합. 장점: 이론상 `max(6개 latency)`에 근접 가능.
단점: Test가 다른 5개 대비 압도적으로 느리므로(§6 실측), 이론적
이득이 실제로 실현되는지는 **이 세션의 실측으로 확인되지 않았다**
(§6).

### C. Hybrid

Test만 별도 트랙(Isolation 필요)으로 분리하고, 나머지 5개(Structure/
Scope/AST/Dependency/Review)만 병렬화하거나, Test를 여전히 순차
마지막에 두는 형태 등 — 이 ADR은 특정 Hybrid 형태를 확정하지 않는다
(§12 Validation Required).

## 5. Independence Decision

**확정한다(Scoped Accept)**: `RFC-0039`/`ADC-0042`의 Independence
판정표를 이 ADR의 Architecture Boundary로 그대로 채택한다.

- Structure/Scope/Dependency: **A(Fully Independent)** — 다른 5개
  Validator의 결과를 어떤 형태로도 입력받지 않는다.
- AST/Review: **A(Fully Independent), 단 원본 코드는 반드시 Context
  Snapshot 단계에서 Fan-out 이전에 확보된 읽기 전용 값이어야 한다**
  (Test Workspace를 참조하지 않는다).
- Test: **B(Independent with Isolation)** — 유일하게 파일 시스템에
  쓰기를 하므로, 원본이 아니라 격리된 Test Workspace 안에서만
  실행되어야 한다.
- Review는 Structure/Scope/AST/Dependency/Test 5개 중 **어느 것의
  결과도 입력으로 사용하지 않는다**(`RFC-0039` §2.6.1, 이 ADR §9에서
  재확인).

## 6. Test Isolation Decision

**확정한다**: Test Validator는 **repository working tree 전체 복사
(`.git` 제외)**로 만든 격리 Workspace 안에서만 실행한다.

- `STAGE05-TEST-ISOLATION-VALIDATION-0001.md` §1.3이 "손으로 고른
  최소 소스 집합"(test/만, 또는 test/+짐작한 일부 source)이 실제로는
  부족함을 실측(`FileNotFoundError` 재현, 테스트가 `hqs/investment/`
  까지 참조하는 것을 발견)으로 확인했다.
- 같은 문서 §1.4가 `.git` 제외 전체 복사가 251ms에 끝나고 원본과
  동일한 결과(324 passed/6 skipped)를 냄을 실측했다.
- Worktree/Container는 **불필요**하다 — Git 의존성 0건, 권한/네트워크
  격리 필요 근거 0건(같은 문서 §1.1, §3.1).
- 이 세션의 Harness(`domain/workspace.py`)가 이 방식을 실제로
  구현·테스트했다(§10, `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`
  §2).

## 7. Aggregation Boundary

**확정한다**: Aggregator는 다음 5단계만 수행하며, 새 validation
logic을 발명하지 않는다(`RFC-0039` §6, 사용자 지시 Part 4와 동일):

1. 모든 Validator 결과 수집(완결된 `ValidatorResult` 객체만, 재판단
   없음).
2. Validator ID를 고정 순서(`structure, scope, ast, dependency, test,
   review`)로 정규화 — 실행/완료 순서와 결과 순서를 분리한다.
3. Structure/Scope/AST/Dependency/Test(5개, blocking)의 FAIL/ERROR만
   집계해 Verdict 후보를 정한다.
4. Review 결과는 별도로 보존하되 3번의 집계에 참여시키지 않는다.
5. Final Verdict를 계산한다(§8).

## 8. Failure Isolation Policy

**확정한다**: 한 Validator의 failure(FAIL/ERROR/Timeout/Workspace
생성 실패/Implementation 적용 실패/pytest 실행 실패/cleanup 실패
어느 것이든)는 다른 Validator의 실행을 막지 않는다. Aggregator는
가능한 모든 결과를 수집한 뒤에만 Verdict를 산출한다 — 하나가
누락되면 그 항목만 결과 집합에서 빠지고(Aggregator는 "missing"으로
인지), 나머지는 정상적으로 기록된다.

이 정책은 이 세션의 실측(§10, `docs/research/
STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md` §4)으로 6개 시나리오
(6/6 success ~ all failure)에서 확인됐다.

## 9. Review Validator Boundary

**확정한다**(`RFC-0039` §2.6.1의 5-way 개별 검증을 그대로 채택):

- Review ← Structure Result: 불필요.
- Review ← Scope Result: 불필요(단, Scope **Context**는 입력으로 허용 — Result와 Context를 구분).
- Review ← AST Result: 불필요.
- Review ← Dependency Result: 불필요.
- Review ← Test Result: 불필요.
- Review Input은 `Stage 04 Implementation / Architecture·Design Context / Contract / Scope Context(정의) / 필요한 원본 코드·메타데이터(읽기 전용 Context Snapshot)`로 제한된다.
- Review는 **항상 advisory**다 — Aggregator의 Verdict 계산(§7·§8)에
  참여하지 않는다. Review가 PASS여도 deterministic FAIL을 뒤집지
  못하고, Review가 FAIL/ERROR여도 deterministic PASS를 자동으로
  FAIL로 바꾸지 않는다.

## 10. LLM Review Decision Status

**NOT YET DETERMINED.**

- Review의 구현 방식(Deterministic/LLM/Hybrid)은 §9의 독립성 판정과
  무관한 별개 질문이다(`RFC-0039` §8).
- 이 세션의 Harness(`domain/review.py`)가 3-Mode 구조(disabled/
  deterministic/llm)를 **실제로 구현**했고, LLM Mode는 기존 Engine
  Contract(`str -> str`)와 동일한 형태의 `engine_call`을 주입받는
  Adapter 형태로 만들었다(§13 Non-Goals — 새 Gateway/Router를
  만들지 않았다).
- Experiment B(§11, `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`
  §5)는 Case A(disabled)/B(deterministic)를 실제로 실행했으나, Case
  C(llm)는 **실제 Engine을 호출하지 않았다**(`engine_call` 미주입 —
  OpenRouter 등 실제 호출은 이번 작업의 필수 조건이 아니라는 사용자
  지시를 그대로 따름). 따라서 LLM Review가 실제로 새로운 결함을
  찾는지, Deterministic Review와 결과가 겹치는지, false positive/
  negative가 있는지는 **전부 NOT DETERMINED**다 — 추정하지 않는다.

## 11. Parallel Production Adoption Decision Status

**NOT YET DETERMINED.**

- Experiment A(§10, `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`
  §3)가 실제로 Single vs Parallel을 3회씩 반복 실행해 실측했다.
- **실측 결과, 이 3회 반복에서 Parallel이 Single보다 명확히 빠르다는
  근거는 나타나지 않았다** — Test Validator(약 30초)가 전체
  latency를 압도적으로 지배하고, 나머지 5개(Structure/Scope/AST/
  Dependency/Review)는 전부 10ms 미만이라 병렬화로 절약되는 절대
  시간이 무시할 만한 수준이었다. 오히려 한 반복(Parallel run 1)은
  Single의 어떤 반복보다도 느렸다(Thread/Process Pool 생성 오버헤드로
  추정 — 원인은 이 문서가 확정하지 않는다, Not Determined).
- **"Parallel이 더 빠르다"/"Parallel이 비용 효율적이다"는 이 ADR이
  주장하지 않는다** — 사용자 지시가 명시적으로 금지한 바로 그
  주장이며, 실측 결과 자체가 그런 결론을 뒷받침하지 않는다.
- 6-way Parallel DAG를 Production Architecture로 채택할지는 §12의
  조건이 충족된 뒤에만 재검토한다.

## 12. Validation Required Before Final Adoption

`ADC-0042` Validation Requirements를 그대로 유지하며, 이번 세션의
실측으로 일부(1번의 메커니즘 구체화)만 진전시켰다:

1. **(진전됨)** Context 선-스냅샷 + Test 격리 실행의 실제 메커니즘 —
   Workspace 복제 방식으로 구체화·구현·테스트 완료(§6, §10). 단,
   Production `stage_05.py`에 실제로 배선하지는 않았다.
2. Real Engine 실행 결과(latency/cost/품질)를 워크로드가 더 균형
   잡힌 조건(예: Review가 실제 LLM 호출을 포함하는 경우)에서 반복
   측정 — 이번 3회는 Test가 압도적으로 느린 조건에서만 측정됐다.
3. LLM Review를 실제로 최소 1회 이상 실행해 Deterministic Review와의
   중복/false positive/false negative를 실측.
4. `VerificationResult` Contract를 6-Node 구조로 재설계하는 별도
   RFC(§13 Non-Goals — 이 ADR은 착수하지 않음).
5. Multi-Task 허용 범위(`ADC-0016` §Q4)의 "구현 착수 전 Data/Artifact
   Isolation 확인" 요건이 실제 Production 배선 시점에도 충족되는지
   재확인.

## 13. Consequences

- Stage 05의 6개 책임에 대한 Independence/Isolation/Aggregation/
  Failure Isolation/Review Boundary 판단은 이제 이 ADR을 Single
  Source of Truth로 인용할 수 있다 — 향후 세션이 이 5가지를 처음부터
  재조사할 필요가 없다.
- Parallel Production Adoption과 LLM Review Adoption은 여전히 열려
  있다 — 이 ADR을 "Stage 05가 병렬로 전환됐다"는 근거로 인용해서는
  안 된다.
- `projects/stage05-parallel-validation-harness-v1/`가 §12의 후속
  실험을 위한 재사용 가능한 도구로 남는다(Stage 04의 `architecture_
  validation/` Harness가 `ADC-0040`을 위해 재사용된 것과 동일한
  패턴).
- Production `stage_05.py`/`RESPONSIBILITY.md`/`VerificationResult`
  Contract는 전부 무변경 — 이 ADR은 그 자체로 어떤 Production
  동작도 바꾸지 않는다.

## 14. Non-Goals

- Production `stage_05.py`를 6-Node 구조로 재구현하는 것 — 하지 않음.
- `VerificationResult`/`stages/contracts.py` Contract를 변경하는 것 —
  하지 않음(변경하려면 별도 RFC → ADC → ADR, §12 항목 4).
- LLM Review를 위한 새 Engine Gateway/Router/Provider Architecture를
  만드는 것 — 하지 않음(`domain/review.py`는 기존 `str -> str`
  Contract의 Adapter일 뿐).
- OpenRouter를 Production Stage Engine Routing에 연결하는 것 — 하지
  않음. 이 ADR·Harness가 OpenRouter를 쓰더라도 그것은 Experimental
  Validation endpoint일 뿐이다(이번 세션은 실제로 호출하지도
  않았다, §10).
- `RFC-0038`/`ADC-0041`(QA Agent 활성화, 별개 축)을 이 ADR로
  재론하거나 병합하지 않는다.
- 기존 RFC(`RFC-0039`)/ADC(`ADC-0042`)를 수정하거나 완료 처리하지
  않는다 — 그대로 Related로만 인용한다.

---

## Self Review

- 현재 구현을 Architecture 기준으로 삼았는가 — **아니오**(`RFC-0039`의
  "책임의 본질" 기준을 그대로 인용, 이 ADR도 재론하지 않음).
- Parallel Production Adoption을 확정했는가 — **아니오**(§11, NOT YET
  DETERMINED로 명시, 실측 결과가 오히려 이를 뒷받침하지 않음을
  정직하게 기록).
- Review LLM Adoption을 확정했는가 — **아니오**(§10, NOT YET
  DETERMINED — LLM을 실제로 호출하지 않았다는 사실을 숨기지 않음).
- "Parallel이 더 빠르다/비용 효율적이다/LLM Review가 필요하다/품질을
  향상시킨다"를 주장했는가 — **아니오**(§11, §10 — 오히려 실측이
  반대 방향(눈에 띄는 이득 없음)을 보여줬음을 그대로 기록).
- 임의의 ADR 상태명을 만들었는가 — **아니오**(§Governance Status
  확인 — 기존 "Accepted(Scoped)" 어휘만 재사용, 번호도 다음 순번
  `0025` 그대로 사용).
- 기존 RFC/ADC/ADR을 임의로 수정하거나 완료 처리했는가 — **아니오**
  (`RFC-0039`/`ADC-0042` 본문 무수정, Related로만 인용).
- API Key/Credential을 탐색하거나 출력했는가 — **아니오**(이 ADR도,
  §10이 인용하는 Harness도 `engine_call`을 주입하지 않은 채로만
  실행했다).
- Production 코드를 변경했는가 — **아니오**(변경 범위는 이 ADR +
  Evidence 문서 + `projects/` 신규 Harness뿐, §Validation에서 재확인).

## Related

- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`
- `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`
- `docs/research/STAGE05-TEST-ISOLATION-VALIDATION-0001.md`
- `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`(이 ADR과 함께 제출)
- `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md`,
  `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md`(별개 축, QA Agent 활성화)
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`(동일 방법론 선례)
- `hqs/development/mvp/execution_host.py`(`ADC-0015` Process 격리 선례)
- `projects/stage05-parallel-validation-harness-v1/`(이 ADR이 인용하는 실측 Harness)
