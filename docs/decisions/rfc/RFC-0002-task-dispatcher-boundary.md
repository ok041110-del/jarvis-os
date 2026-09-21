# RFC-0002 — Task Dispatcher Boundary (재평가)

> 본 RFC는 Kernel의 구현 방법을 제안하지 않는다. MVP에서 관찰된 Kernel
> Extraction Candidate의 Boundary만 논의한다.

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | RFC-0002 |
| Status | Resolved — `docs/governance/adc/ADC-0002.md`로 종결됨(ADR 불필요, STABILITY-0001 §1.2). 이 라벨은 절차 진행 상태만 반영한다 |
| Owner / Scope | Task Dispatcher(단 하나) — Engine Gateway, Registry, Context 전달 메커니즘은 대상이 아니다 |

## 2. Problem & Context

| Item | Description |
|---|---|
| Problem | MVP-0002에서 새롭게 관찰된 Workflow Branch를 근거로, Task Dispatcher의 Kernel Boundary를 다시 질문 |
| Context | ADC-0001은 Task Dispatcher를 "Keep in MVP"로 판단했다 — 근거는 "MVP-0001에서 실제로 관찰된 유일한 사례(단일 선형 2-Task Workflow)에서 하드코딩된 순차 호출은 끝까지 무너지지 않았다"는 관찰. RT-0001은 Re-evaluation Trigger를 "Workflow Branch 발생, 또는 하드코딩된 Task 호출 체인 수 ≥ 2"로 정의했다. `MVP-0002-plan.md`는 이 Trigger 중 "Workflow Branch 발생"을 의도적으로 발생시키기로 계획했고, `MVP-0002-observation.md`는 그 계획이 실행되어 Trigger가 충족됐다고 기록했다 |
| Motivation | 이 RFC는 그 Observation을 근거로, ADC-0001의 Decision Rationale이 의존했던 전제("단일 선형 Workflow에서만 관찰됨")가 지금도 성립하는지를 질문한다 |
| Non-Goals | Task Dispatcher의 구현 방법, API/Interface/Parser/DSL/Config, Runtime/Scheduler/Registry/Memory/Event Bus, Engine Gateway/Registry/Context 전달 메커니즘(각각 별도 Candidate), Architecture Baseline/Development HQ Baseline 변경 — 어느 것도 논의하지 않는다. 아래 Boundary Question에 답하지도 않는다 |

## 3. Questions & Alternatives

### Questions for Review

| ID | Question | Reason |
|---|---|---|
| Q-1 | Workflow Branch가 실제로 발생한 지금, Task Dispatcher는 계속 MVP 범위(하드코딩된 직접 호출)에 남아 있어야 하는가, 아니면 이번 Observation이 승격 재검토 시점임을 의미하는가? | RT-0001 Trigger 충족 사실의 해석 |
| Q-2 | RT-0001이 정의한 Trigger("Workflow Branch 발생")가 충족된 사실과, ADC-0001의 Decision Rationale이 의존했던 전제(단일 선형 Workflow)가 깨진 것은 같은 의미인가, 다른 의미인가? | Trigger 충족과 전제 붕괴의 관계 확정 필요 |
| Q-3 | 이번 Observation은 분기 1개, `if`/`else` 하나에 대한 것이다. 분기가 몇 개부터 하드코딩된 호출 방식이 무너지는가 — 이 임계값은 정의 가능한 값인가, 아니면 정의 자체가 Task Dispatcher의 Boundary를 흐리는가? | 임계값 존재 여부 자체가 열린 질문 |
| Q-4 | MVP-0002가 관찰한 분기는, MVP-0001이 이미 Out of Scope로 선언한 "분기"(`development-hq/MVP.md`: "분기·재시도·병렬 실행 없음")와 같은 개념인가? 같다면 MVP-0002의 Observation은 MVP-0001 Baseline의 Out of Scope 선언과 어떤 관계에 있는가 — 범위를 넘어선 새 실험인가, 그 선언 자체의 재검토 대상인가? | MVP-0001 Out of Scope 선언과의 정합성 확인 필요 |

### Alternatives to Consider

이 RFC는 해결책(Alternative)을 제시하지 않는다 — Task Dispatcher의 승격 여부(Promote to Kernel / Keep in MVP / Defer) 판단은 ADC-0002로 전적으로 위임한다.

## 4. Proposed Direction

> 검토를 위한 제안이며 최종 결정이 아님. 이 RFC는 위 4개 질문에 답을
> 제시하지 않는다.

`MVP-0002-observation.md`에서 실제로 기록된 내용만 인용해 Observation을 구성한다.

- `development-hq/mvp/workflow_0002.py`에 조건 분기 1개가 추가되었다: `code_review` 결과에 "뚜렷한 이슈가 발견되지 않았습니다"라는 문자열이 포함되는지에 따라 `test_execution` 호출 여부가 갈린다.
- 분기 A(이슈 있음): `test_execution`이 정상 실행되어 테스트 케이스 제안을 반환. 분기 B(이슈 없음): `test_execution` 호출이 건너뛰어지고 생략 메시지가 반환.
- 두 경로 모두 하드코딩된 `if`/`else`로 표현되었으며, 별도 설정 파일이나 파서는 도입되지 않았다.
- 분기 추가 후에도 Implementation Stop Trigger(조건문이 파서/설정 파일로 대체되려는 순간)는 발생하지 않았다 — 단, "분기 1개" 규모에 한정된 관찰이라고 `MVP-0002-observation.md`는 명시한다.
- 기존 MVP-0001 테스트 3건은 그대로 통과했다(회귀 없음). 재시도·병렬 실행은 관찰하지 않았다.

## 5. Requested Review

| Review Item | Description |
|---|---|
| Required Review | ADC-0002에서 Task Dispatcher의 승격 여부(Promote to Kernel / Keep in MVP / Defer)를 판단 |
| Expected Feedback | Q-1~Q-4에 대한 판단, RT-0001 Trigger 재해석 여부 |

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0001-kernel-boundary.md` | Task Dispatcher에 대해 남긴 질문("몇 개 이상의 Task부터 하드코딩된 순차 호출이 무너지는가")을 이어받아 구체화 |
| ADC | `docs/governance/adc/ADC-0002.md` | 이 RFC를 종결(ADR 불필요) |
| Evidence | `docs/01_mvp/MVP-0002-observation.md`, `docs/01_mvp/MVP-0002-plan.md`, `development-hq/MVP.md`, `docs/governance/adc/ADC-0001.md`, `docs/governance/rt/RT-0001.md` | 근거 문서(`docs/01_mvp/MVP-0001.md`는 존재하지 않아 `development-hq/MVP.md`로 대체 인용) |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | MVP-0002 구현 세션 중 Task Dispatcher 재평가 |

---

## 부록: Self Review

- Candidate가 하나뿐인가 — Pass. Task Dispatcher만 다뤘고, Engine Gateway/Registry/Context 전달은 언급하지 않았다.
- Observation만 사용했는가 — Pass. `MVP-0002-observation.md`에 실제로 기록된 내용만 인용했다.
- Boundary만 질문했는가 — Pass. 4개 질문 모두 "언제/무엇을 의미하는가" 형태이며, 구현 방법·API·Parser를 묻지 않았다.
- Architecture Drift가 없는가 — Pass. 새 Layer/Component/Service/Baseline 없음.
- Kernel Leak가 없는가 — Pass. Runtime/Scheduler/Registry/Memory/EventBus/Parser/DSL/Config/API/Interface를 논의하지 않았다.
- RFC-0001과 모순되지 않는가 — Pass. RFC-0001이 남긴 질문을 이어받아 MVP-0002에서 실제로 관찰된 분기 사실로 구체화했을 뿐 새로운 전제를 추가하지 않았다.
