# Implementation Rules

이 문서는 Claude Code가 Development HQ MVP-0001을 구현할 때 반드시 지켜야 하는 규칙만 정리한다. 모두 이미 승인된 내용이며, 새로운 규칙을 추가하지 않는다.

## 금지 사항

| 금지 항목 | 이유 |
|---|---|
| Workflow Parser 구현 금지 | Task 1→Task 2는 직접 함수 호출로 충분. 파서는 Scheduler를 미리 만드는 것과 동일 |
| Scheduler 구현 금지 | MVP는 Task 순서를 스크립트에 하드코딩한다 |
| Registry 구현 금지 | Agent-Capability 매핑은 리터럴 딕셔너리 이상으로 발전시키지 않는다 |
| Registry 일반화 금지 | 정적 딕셔너리를 조회 함수, 클래스, 동적 등록 API 등 어떤 형태로도 일반화하지 않는다 |
| Scheduler/우선순위/Workflow orchestration/Dynamic Routing(조건부 목적지 선택·Agent 동적 배분) 및 §6 넓은 Runtime(Workflow 참조 전체) 구현 금지 | Runtime 존폐 자체가 여전히 결론 없다 — `docs/decisions/adc/ADC.md`의 ADC-02(Open, NOW), `docs/architecture/core/ADC-0008`(Runtime 존폐, Not Accepted)·`ADC-0011`(Standalone Execution Location Boundary, Not Accepted)·`ADC-0012`(Dispatch Component Boundary, Defer) 중 어느 것도 Accept가 아니다. Execution Host(§16.3)와 Multi-Task(§16.4)의 Scoped 허용 범위는 각각 아래 절 참조 — 두 절 모두 이 표의 나머지 금지를 해제하지 않는다 |
| Stage 재진입(Retry/Re-entry)·조건부 Stage 실행 구현 금지 | Development HQ v2.0 Stage 01→05(`workflow.py`)는 고정 순서 단일 패스만 수행한다. Stage 05 Verdict/실패를 보고 특정 Stage로 자동으로 되돌아가거나 다른 구현 경로를 자동 선택하는 로직은 Workflow Parser/Scheduler(위 금지)를 실질적으로 재도입하는 것과 같다. 재검토 조건은 아래 "Dynamic Workflow 재검토 Trigger" 참조 |
| Engine Gateway(Port/Adapter 추상화) 구현 금지 | 단일 함수로 Engine을 호출하는 것으로 충분하다 |
| Engine Routing 구현 금지 | 여러 Agent 또는 여러 Engine 중 무엇을 선택할지 결정하는 로직을 만들지 않는다. MVP는 Engine을 호출하는 함수 하나만 가진다 |
| Policy 구현 금지 | MVP는 Policy 판정 호출 자체를 생략한다 (스텁도 만들지 않는다) |
| Memory Service(영속화 계층) 구현 금지 | Context는 in-memory 변수로만 다룬다 |
| Event Bus 구현 금지 | MVP는 단일 선형 Task Flow만 다루며 Event Flow를 쓰지 않는다 |
| Multi-HQ 지원 코드 작성 금지 | MVP는 Development HQ 단독 시나리오만 다룬다. `docs/architecture/core/ADC-0018-natural-language-request-multi-hq-task-decomposition.md`가 자연어→Multi-HQ Task 분해 책임을 Defer(Scoped, 실제 필요 사례 관찰 전까지)했다 — 이 금지는 그 상태와 충돌하지 않는다 |
| Multi Engine 지원 코드 작성 금지 | 단일 Engine 호출로 충분하다 |
| Architecture Baseline 및 Development HQ Baseline 수정 금지 | 두 Baseline은 Frozen 상태다. Architecture 수준 문제 발견 시 아래 "Architecture 문제 발견 시 절차"를 따른다 |

## Execution Host 구현 허용 범위 (Scoped, ADC-0015)

`docs/architecture/core/ADC-0015-execution-host-implementation-strategy.md`
가 Conditional Accept한 범위에 한해, 아래 조건을 모두 지키는 경우
Execution Host 구현을 허용한다.

- 적용 대상: "동일 Target(프로세스 전역 상태를 공유하는 대상)을
  동시 실행할 가능성이 있는 경로"에서 격리를 제공하는 최소 구현만
  허용한다.
- 구현 전략: Process를 1차로, Subprocess를 대안으로 사용한다.
  **Thread는 이 경로에서 사용하지 않는다**(`ADC-0015` §Q0·§Q1).
- 이 허용은 Scheduler, Multi-Task/Workflow orchestration,
  `BASELINE.md` §6의 넓은 "Runtime"(Workflow 참조, Multi-Task를
  Agent에게 배분) 구현을 포함하지 않는다 — 이들은 여전히 금지
  상태다(위 표).
- 이 허용은 **Conditional**이다 — 비용 또는 운영 중 새로 관찰되는
  Evidence에 따라 `ADC-0015`의 재검토 대상이며, 재검토 결과에 따라
  이 절도 함께 갱신되어야 한다.
- 새 Public Interface/Contract를 정의하지 않는다 — Kernel Public
  Contract(§14)는 이 허용과 무관하게 무변경이다.

## Multi-Task 구현 허용 범위 (Scoped, Conditional, ADC-0016)

`docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`
가 Accept(Scoped, Conditional)한 범위에 한해, 아래 조건을 모두
지키는 경우 Multi-Task 구현을 허용한다.

- 적용 대상: 서로 입력 독립·출력 비의존인, 이미 코드/설계에 고정된
  소수의 실행 단위를 동시에 시작하고 결과를 수집하는 최소 구현만
  허용한다. 우선순위 판단, 조건부 분기, Workflow 그래프 해석, Agent
  동적 선택은 포함하지 않는다.
- Data/Artifact Isolation 사전 확인 필수: 적용 대상 Task 조합에서
  동시 실행되는 각 Task가 서로 다른 파일/Artifact 이름공간에 쓰거나
  아무것도 쓰지 않는다는 것이 **구현 착수 전에** 확인되어야 한다
  (`ADC-0016` §Q4·§Decision 조건 3). 이 조건이 확인되지 않으면 이
  허용 범위 밖이다 — 확인 방법(정적 분석, 코드 리뷰 체크리스트 등)의
  구체화는 이 절이 정하지 않는다.
- Task→Agent 할당: 기존 Agent 재사용만 허용한다. 새 Agent·Capability
  도입, 동적 Task→Agent 할당 로직은 이 허용에 포함되지 않는다(아래
  "구현 중 새 Capability/Agent 추가 금지" 절과 함께 적용).
- 이 허용은 Scheduler, 우선순위, Workflow orchestration,
  `BASELINE.md` §6의 넓은 "Runtime"(Workflow 참조, Agent 동적 배분)
  구현을 포함하지 않는다 — 이들은 여전히 금지 상태다(위 표).
- 이 허용은 Execution Host(§16.3)의 범위를 넓히지 않는다 — 별개
  책임이다(`ADC-0016` §Q3).
- 새 Public Interface/Contract를 정의하지 않는다 — Kernel Public
  Contract(§14)는 이 허용과 무관하게 무변경이다.

## Multi-Task Result Store 관련 확인 (ADC-0017)

`docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md`
가 Accept(Scoped, Narrow)한 "저장 전 검증 게이트" 책임(`BASELINE.md`
§16.5)의 실증 사례는 `hqs/investment/checkpoint.py`의
Checkpointer/`run_step`/`ContentFailureError` 패턴 하나뿐이며, 이
컴포넌트는 Development HQ(`hqs/development/mvp/`)에 존재한 적이
없다(`ADC-0017` §Q3). 이 Accept는 Development HQ에 새 Result
Store/Checkpointer 구현을 요구하거나 허용하지 않는다 — Development
HQ에는 적용 대상 자체가 없으므로, 위 금지 표(특히 Memory Service·
Registry 금지)는 이 Accept로 전혀 해제되지 않는다. Development
HQ에서 유사한 저장 전 검증 필요가 실제로 관찰되면 별도 RFC 대상이다.

## Stage Data Contract (ADR-0009) — Public/Hidden 구분

Development HQ v2.0 Stage 01~05가 주고받는 데이터는
`hqs/development/BASELINE.md`의 "Stage Data Contract(ADR-0009)"
절이 정의하는 HQ-level Public Contract를 따른다(Kernel Public
Contract §14와는 별개 — 이 문서는 그 내용을 다시 정의하지 않고
구현 규칙만 확인한다).

- **Public**(변경 시 예외 없이 RFC → ADC → ADR 필요): 5개 Stage
  Contract(`ContextAnalysisResult`/`SpecificationResult`/
  `DesignResult`/`ImplementationResult`/`VerificationResult`)의
  필수 키 집합, `KNOWN_CHECK_NAMES`(`structural`/`specification_scope`/
  `design_scope`/`test_execution` 4개 고정 — 이름 추가·삭제는 Security/
  Data-API 등 새 검사 종류 포함 예외 없이 이 절차 대상), `required_checks`
  (부분집합 파라미터, 빈 값·미지 이름은 즉시 `ContractViolation`),
  `check_results` 스키마(`{name, status, blocking, detail}`), `status`
  집합(`PASS`/`FAIL`/`INCONCLUSIVE`/`SKIPPED`), `blocking` 규칙
  (`structural`/`design_scope`/`test_execution`은 blocking,
  `specification_scope`는 non-blocking).
- **Hidden**(Public 의미를 바꾸지 않는 범위에서 절차 없이 자유 변경):
  각 검사의 내부 판정 로직(Stage 05 `_check_*`/`_CHECK_EVALUATORS`
  개별 함수 본문), `code_review` 필드 생성 방식. `stage_05.py`의
  malformed 입력 방어(`_check_design_scope`의 `ast.parse()` 예외 처리,
  `_check_specification_scope`의 nested 필드 결측 방어)는 이 Hidden
  범위 안의 수정이었다 — Public Contract는 변경되지 않았다.
- `workflow.py`의 Stage 순서·호출 배선은 이 Contract가 규정하지
  않는다(Contract는 Stage 간 "무엇을 주고받는가"만 정의) — Stage
  순서 변경은 이 Contract 절차가 아니라 아래 "Architecture 문제
  발견 시 절차" 대상이다.

## Dynamic Workflow 재검토 Trigger

Workflow Parser/Scheduler/Registry/Event Bus/Memory Service/Dynamic
Routing/Stage 재진입 구현 금지(위 표)는 현재 Evidence 기준으로
유지된다. Development HQ Dogfooding에서 실제 Claude Engine으로 복합
변경 요청 2건(기존 계약과 충돌하는 회귀 유발, design_scope 위반
유도)을 Stage 01→05에 실행해 Stage 05 실패를 관찰한 결과, 두 사례
모두 **Static Stage 01→05 고정 실행만으로 해결**됐다 — 회귀 사례는
issue를 수정해 Static Workflow를 처음부터 다시 실행하는 것으로,
scope 위반 유도 사례는 Stage 04 프롬프트 정책(`_EXPOSURE_POLICY_INSTRUCTION`)
자체가 이미 위반을 억제하는 것으로 해결됐다. Stage 05의 실패 결과를
Stage 03/04에 자동으로 되먹이는 내부 재진입은 어느 사례에서도
필요하지 않았다.

**재검토 Trigger**: 다음이 실제 코드/실행에서 반복적으로(1회 관찰은
Evidence로 인정하지 않음 — 다른 Accept 판단과 동일 기준) 관찰되면,
Dynamic Workflow/Retry/Re-entry/조건부 Stage 실행 금지를 RFC → ADC
→ ADR 절차로 재검토한다. 직접 구현으로 해결하지 않는다.

1. Stage 05 실패가 "issue를 고쳐 Static Workflow를 처음부터
   재실행"하는 방식으로 **해결되지 않는** 사례(예: 실패 원인이 Stage
   03/04의 중간 산출물에만 있어 처음부터 재실행해도 동일하게 실패)
2. 동일 Stage를 서로 다른 구현 경로로 여러 번 시도하고 그중 하나를
   선택해야 하는 필요가 실제 작업에서 관찰되는 경우

## 구현 중 새 Capability/Agent 추가 금지

MVP는 `STRUCTURE.md`에 이미 예시로 등재된 Capability(`code_review`, `test_execution`)와 Agent(Backend Agent, QA Agent)만 사용한다. 구현 편의를 위해 새 Capability나 Agent를 추가하지 않는다.

실제로 기존 Capability로 해결할 수 없는 작업이 반복적으로 관찰되면,
새 Capability/Agent를 직접 추가하지 않고 RFC → ADC → ADR 절차로
전환한다(`KNOWN_CHECK_NAMES` 확장도 위 "Stage Data Contract" 절이
정의하는 동일 절차 대상). Security/Data-API 검사 부재는 이미 이런
사례로 식별돼 있다(`ADR-0009` §4, `docs/research/DEV-HQ-V2.0-STAGE-DATA-CONTRACT-0002.md`).

## 구현 중단 트리거

다음 두 현상 중 하나라도 실제 코드에서 나타나면, 구현을 즉시 중단하고 `docs/decisions/rfc` → `docs/decisions/adc` → `docs/decisions/adr` 절차로 넘긴다. 직접 고치지 않는다.

1. Agent-Capability 매핑이 리터럴 딕셔너리를 넘어서는 클래스/서비스로 발전하려는 순간
2. Task 1→Task 2 호출이 조건문·설정 파일·파서로 대체되려는 순간

이는 새로운 Architecture, Component, Layer, Concept를 만드는 것이 아니라, Kernel Extraction이 예상보다 이르게 필요해졌다는 관찰을 ADC 후보로 기록하기 위한 절차다.

## Architecture 문제 발견 시 절차

**Architecture 변경은 구현으로 해결하지 않는다.** 구현 중 Architecture 결함이 발견되었다고 해서 그 결함을 코드로 메우거나 우회하지 않는다.

Development HQ 구현 중 Architecture 수준의 문제(Concept 누락, Boundary 모순 등)를 발견하면:

1. 직접 수정하지 않는다.
2. `docs/decisions/rfc`에 문제를 기록한다.
3. `docs/decisions/adc/ADC.md`에 Decision Candidate로 등록한다.
4. NOW로 분류되지 않는 한, 구현은 현재 MVP 범위 내에서 계속 진행한다.

## Exit Criteria 재확인

구현 완료 판단 기준은 `MVP.md`의 Exit Criteria를 그대로 따른다: 입력 코드가 주어지면 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환되고, 이 과정에서 Registry/Scheduler/Policy에 해당하는 범용 서비스 코드가 생성되지 않아야 한다.
