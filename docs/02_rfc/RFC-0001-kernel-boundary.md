# RFC-0001: Kernel Boundary

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (Development HQ MVP-0001 구현 세션)
**관련 Baseline**: `docs/01_architecture/BASELINE.md` §6 Concept Model, §7 System Boundary
**관련 ADC**: ADC-01, ADC-02, ADC-07, ADC-09, ADC-10 (`docs/03_adc/ADC.md`)

> 본 RFC는 Kernel의 구현 방법을 제안하지 않는다.
> 본 RFC는 MVP에서 관찰된 Kernel Extraction Candidate의 Boundary만 논의한다.

## 배경

Architecture Baseline v1.0 §10은 "Kernel Architecture"와 "Component Design(Scheduler,
Engine Gateway, Registry, Communication, Memory, Policy 등)"을 명시적으로
Out of Scope로 두었다. Development HQ MVP-0001은 이 Kernel을 미리 설계하지 않고,
그 자리를 최소한의 하드코딩(리터럴 딕셔너리, 단일 함수 호출, in-memory 변수)으로
메운 채 Architecture Baseline이 실제 도메인에서 성립하는지 검증했다.

MVP-0001은 승인(Accepted)되었고, Architecture/Development HQ Baseline을 위반하지
않았다. 이 RFC는 그 구현 과정에서 실제로 관찰된 4개 지점 — Kernel Extraction
Candidate — 을 근거로, Kernel Boundary를 지금 논의할 시점이 되었는지를 검토 대상으로
제기한다. 이 RFC 자체는 어떤 것도 결정하지 않는다.

## MVP-0001에서 관찰된 Kernel Extraction Candidate

| 후보 | MVP-0001에서의 형태 | 코드 위치 |
|---|---|---|
| Task Dispatcher | `review = backend_agent_code_review(code)` → `test_cases = qa_agent_test_execution(code, review)` 두 줄의 하드코딩된 순차 호출 | `development-hq/mvp/workflow.py` |
| Engine Gateway | 단일 함수 `call_engine(prompt)`. Port/Adapter 없음, Engine Routing 없음 | `development-hq/mvp/engine.py` |
| Registry | `AGENT_CAPABILITY_MAP = {"code_review": "Backend Agent", "test_execution": "QA Agent"}` 리터럴 딕셔너리. 조회 함수·클래스·동적 등록 없음 | `development-hq/mvp/agents.py` |
| Context 전달 메커니즘 | Task 간 데이터를 지역 변수 `review`로 전달. 영속화 없음 | `development-hq/mvp/workflow.py` |

MVP 구현 중 Implementation Stop Trigger(딕셔너리 → 클래스/서비스로 일반화,
직접 호출 → 조건문/설정 파일/파서로 대체)는 발생하지 않았다. 즉 2-Task/2-Agent
규모에서는 4개 후보 모두 하드코딩으로 충분했다.

## 이 RFC가 제기하는 질문

이 RFC는 답을 제시하지 않는다. 다음 질문에 대한 검토를 요청한다.

1. **Task Dispatcher**: Task 수·Agent 수·Workflow 분기가 늘어날 때, 몇 개 이상의
   Task부터 하드코딩된 순차 호출이 무너지는가? 이 임계값을 정의할 수 있는가,
   아니면 정의 자체가 Kernel Boundary를 흐리는가?
2. **Engine Gateway**: 여러 Agent가 서로 다른 Engine을 쓰거나 하나의 Engine을
   공유해야 하는 시점에 Port/Adapter 추상화가 필요해지는가? (`RFC_CANDIDATES.md`
   Candidate 4 — Engine의 다대다 공유 관계 — 와 연동)
3. **Registry**: Agent-Capability 매핑이 여러 HQ에 걸쳐 조회되어야 하는 시점부터
   Registry가 필요한가, 아니면 단일 HQ 내부에서도 Agent 수가 늘면 필요해지는가?
4. **Context 전달 메커니즘**: in-memory 변수 전달은 어느 시점부터 불충분해지는가
   (예: 실행 실패 후 재시도가 필요해지는 시점)? 이 시점 판단은 Memory
   Service(영속화)의 필요 시점 판단과 같은 질문인가, 다른 질문인가?

   > 참고: MVP-0001은 실행 실패·재시도 상황을 직접 관찰하지 않았다(Fault 전파
   > 인프라는 MVP Out of Scope). 이 질문은 관찰된 사실이 아니라 가설적
   > 시나리오이며, 답을 전제하지 않는다.

## 관련 Open Decision과의 연결

이 4개 질문은 개별 ADC가 아니라 `docs/03_adc/ADC.md`에 이미 등록된 다음 Open
Decision들과 겹친다. 이 RFC는 새 ADC를 만들자는 것이 아니라, 아래 항목들을
"Kernel Boundary"라는 하나의 논의 축으로 묶어 검토할 필요가 있는지를 묻는다.

- ADC-01 (Model 축과 Component 축의 대응 관계) — Task Dispatcher/Registry의
  경계 정의에 선행 필요
- ADC-02 (Runtime 개념의 존폐) — Task Dispatcher가 곧 Runtime/Scheduler인지
- ADC-07 (Resource 예산의 이중 소속) — Engine Gateway가 예산 배분까지
  책임지는지
- ADC-09 (Workflow 그래프의 의미론적 경계) — MVP-0001의 2-Task 선형 Workflow가
  이 결정의 최소 실증 사례로 이미 참고됨
- ADC-10 (Policy 규칙의 출처 분리) — MVP-0001은 Policy 판정 자체를 생략했으므로
  이 RFC의 직접 증거는 아니나, Kernel Boundary 논의에서 함께 다뤄질 가능성

## Non-goals

- 이 RFC는 Kernel을 설계하지 않는다.
- 이 RFC는 위 질문에 답하지 않는다.
- 이 RFC는 Architecture Baseline이나 Development HQ Baseline을 변경하지 않는다.

## 다음 절차

이 RFC는 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 절차를 따른다.

```
RFC-0001 (본 문서)
↓
docs/03_adc/ADC.md에 결정 필요 항목으로 등록 (또는 기존 ADC-01/02/07/09/10에 흡수)
↓
ADR
↓
Architecture Baseline Update
```

이 RFC가 ADC로 승격될지, 기존 ADC 항목에 실증 자료로 흡수될지는 이 문서가
결정하지 않는다. Architecture Governance 절차를 통해 별도로 판단한다.
