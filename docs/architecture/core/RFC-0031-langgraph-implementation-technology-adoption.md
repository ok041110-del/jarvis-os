# RFC-0031: Workflow Adapter(§16.6) 구현 전략 — LangGraph를 승인된 비강제 Implementation Technology로 확정할 것인가

**Status**: Resolved — `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md`로
종결됨(Accept, Conditional·Non-Mandatory). 후속
`docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md`
참고.
**Author**: Claude Code (실제 Jarvis Prototype Evidence, `projects/
langgraph-conditional-routing-poc-v1/`, PR #173)에 대한 Governance
절차 적용)
**대상**: §16.6 Workflow Adapter의 **구현 전략(Implementation
Strategy)** 단계 — Execution Host가 존재(`ADC-0013`) → 명명(`ADC-0014`)
→ 구현 전략(`ADC-0015`)으로 이어진 3단계 선례를 Workflow Adapter에
적용하는 세 번째 단계다. Workflow Adapter는 이미 존재(`ADC-0019`,
Accept Scoped Conditional) → 명명(`ADC-0020`, "Workflow Adapter")까지
끝났고, "구현체 선택(LangGraph 채택 여부 포함)"만 `BASELINE.md`
§16.6이 명시적으로 "별도 절차(RFC → ADC → ADR)"로 남겨뒀다(§16.6
"이 Accept가 결정하지 않는 것" 문단).
**Evidence 범위**: `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md`
(기존 최종 판정)과 그것이 인용하는 전체 Evidence 계보(v1 `archive`,
E2/E3 PoC, Phase A~F), 그리고 이번에 **새로 추가된**
`projects/langgraph-conditional-routing-poc-v1/EVIDENCE.md`(PR #173,
실제 프로덕션 Capability + 실제 Engine 호출 기반 Conditional Routing
Prototype)만 근거로 삼는다. 기존 Evidence를 재조사하지 않는다.

> 본 RFC는 LangGraph를 Architecture Kernel Module로 재정의하지 않고,
> Production 구현 착수를 승인하지 않는다. `BASELINE.md` §16.6이 이미
> 명시한 대로 "이 Accept는 A-IN 범위의 존재만 등재하며 Production
> 구현 착수를 승인하지 않는다"는 경계는 이 RFC로도 변경되지 않는다
> — `IMPLEMENTATION_RULES.md`의 Workflow Parser/Scheduler/Dynamic
> Routing/Event Bus 구현 금지는 이 RFC의 범위 밖이며 별도 Scoped
> 해제 ADR 대상으로 남는다(§16.6 "Production 구현과의 관계" 문단).
> 이 RFC는 오직 "**만약** Workflow Adapter의 Production 구현이 별도
> 절차로 승인된다면, 그때 LangGraph가 승인된(비강제) 구현 후보
> 목록에 포함되는가"만 다룬다.

## 0. 이 RFC가 열린 이유

`ADR-0018`은 2026-09-02 이전 Evidence(v1 archive, E2/E3 toy·Domain
PoC, Phase A~F Multi-Agent Handoff/Failure Isolation)를 종합해
"LangGraph는 Deferred / Not Adopted"로 최종 판정했다. 그 재검토
조건은 다음 둘 다다.

> (1) ADC-02(Runtime 존폐)가 Accept로 판정되고, (2) 실제 Multi-Task/
> Workflow orchestration 구현 근거(Implementation Stop Trigger 또는
> Kernel Extraction Candidate)가 발생하면, 그때 RFC → ADC → ADR
> 절차로 LangGraph를 Workflow Engine 구현 후보 중 하나로 정식
> 평가한다.

이번에 사용자가 요청한 결정은 이 재검토 조건이 **실제로 충족됐다는
주장이 아니다** — (1) ADC-02는 여전히 Open이고(재개설하지 않음,
사용자 지시 7번), (2) Development HQ에 실제 Workflow orchestration
구현 근거(Stop Trigger)가 발생하지도 않았다. 대신 사용자는 별도
질문을 제기한다: **"Production 구현을 지금 승인하는 것과 무관하게,
LangGraph를 승인된(비강제) Implementation Technology 후보로
미리 확정해 둘 수 있는가"** — 이는 Execution Host가 이미 겪은 것과
같은 종류의 분리다: 책임의 존재(ADC-0013)·명칭(ADC-0014)·구현
전략(ADC-0015)이 서로 다른 절차이듯, Workflow Adapter의 존재
(`ADC-0019`)·명칭(`ADC-0020`)·구현 전략(이 RFC)도 분리된 질문이다.

## 1. Observation — 새로 추가된 Evidence

`projects/langgraph-conditional-routing-poc-v1/`(PR #173)은 `ADR-0018`
이후 처음으로 **실제 프로덕션 Capability**(`backend_agent_code_review`/
`qa_agent_test_execution`, `hqs/development/mvp/agents/`)와 **실제
Engine 호출**(Claude CLI, 4회) 위에서 LangGraph를 실행했다. 결과:

- baseline(`workflow_0002.py::run_mvp_0002`, plain `if/else`)과
  LangGraph 구현의 분기 판정이 **2/2 케이스 100% 일치**.
- LangGraph가 이 단순 2지 분기 시나리오에서 얻은 이점은 **없음**
  (정확성 동일, 속도 차이는 Engine 응답 변동성 범위, State/Graph
  정의로 코드량만 증가).
- LangGraph 자체의 실행(설치, State/Node/Conditional Edge 조립,
  `compile()`, `invoke()`)은 **결함 없이 정상 동작**했다 — 이번
  Prototype이 실패시킨 것은 "가치"이지 "동작 여부"가 아니다.
- `hqs/`, `core/`, `docs/architecture/`, `docs/decisions/` 어떤
  파일도 이 Prototype으로 변경되지 않았다(EVIDENCE.md §0 확인).

이 Evidence는 `ADR-0018`의 결론(단순 분기에는 LangGraph가 불필요)을
**뒤집지 않는다** — 오히려 강화한다. 그러나 이 Evidence가 답하는
질문은 `ADR-0018`이 답한 질문("지금 Production에 필요한가")과
다르다: 이번 Prototype은 "LangGraph가 이 저장소의 실제 코드베이스
위에서 기술적으로 문제없이 동작하고, 기존 방식과 결과가 어긋나지
않는다"는 **기술적 적합성(compatibility)**을 실측했다.

## 2. Boundary Question

### Q-1. LangGraph를 승인된 비강제 Implementation Technology로 확정할 것인가

- **Question**: Workflow Adapter의 Production 구현이 (별도 절차로)
  승인되는 시점이 왔을 때, LangGraph가 그 구현 후보 목록에 **이미
  검토를 마친 승인된 선택지**로 포함되는가, 아니면 그 시점에 처음부터
  다시 RFC를 열어야 하는가?
- **Evidence**: 위 §1 + 기존 Evidence 계보 전체(v1 Adapter
  Reversibility 증명, E2/E3, Phase E/F 7/7·26/26 PASS, 이번 4/4 real
  Engine PASS) — LangGraph가 Kernel 경계(§7 System Boundary, KP-1/
  KP-5)를 지키며 배선 가능하다는 사실은 이미 여러 독립 Evidence로
  반복 확인됐다. 남은 것은 "가치가 있는가"이지 "가능한가"가 아니다.
- **Constraint**: `ADR-0011`(Implementation Freedom) — "Evidence의
  부재 자체는 구현 기술 선택을 금지하는 사전 허가 조건이 아니다."
  이 RFC가 확인해야 하는 것은 "LangGraph를 금지할 근거가 있는가"가
  아니라 "승인 목록에 명시적으로 올릴 실익이 있는가"다.
- **Options**:
  - (a) 승인된 비강제 후보로 명시 확정 — Production 구현이 별도로
    승인될 때, LangGraph 재평가를 처음부터 다시 하지 않아도 된다.
    복잡한 State/Loop/Checkpoint/Agent orchestration/Workflow
    composition이 실제로 필요해지는 시점에 선택지 중 하나로 즉시
    쓸 수 있다.
  - (b) `ADR-0018`의 Deferred/Not Adopted를 그대로 유지 — Production
    구현이 승인되는 시점에 다시 RFC를 열어 처음부터 평가한다.
  - (c) 어느 쪽도 아닌 상태 유지(판단 보류) — 사용자 지시가 명확히
    (a)를 요청했으므로 이 RFC의 채택 후보에서 제외한다.
- **ADC에서 결정할 사항**: (a)와 (b) 중 채택안, (a) 채택 시 "비강제"
  범위(단순 사례는 기존 방식 계속 허용)와 소급 미적용 여부.

## 3. Architecture Impact

- **없음(NONE의 범위 한정)** — 이 RFC는 §16.6이 이미 Accept한
  Workflow Adapter 책임의 존재·경계·A-IN/A-OUT을 재정의하지 않는다.
  `ADC-02`/`ADC-09`를 재개설하지 않는다(사용자 지시 7번). Kernel
  Public Contract(§14)는 변경 대상이 아니다.
- **Production 구현 금지는 무변경** — `IMPLEMENTATION_RULES.md`의
  Workflow Parser/Scheduler/Dynamic Routing/Event Bus 구현 금지
  조항은 이 RFC로 해제되지 않는다.

## 4. Contract Impact

- 없음 — Public Contract를 변경하지 않는다.

## 5. 이 RFC가 정의하지 않는 것 (경계)

- Workflow Adapter Production 구현의 실제 착수 여부·시점 — 별도
  Scoped 해제 ADR 대상(§16.6이 이미 명시).
- LangGraph를 Development HQ/Investment HQ의 특정 기존 코드에
  실제로 배선하는 것 — 이 RFC는 승인 목록 등재 여부만 다룬다.
- ADC-02(Runtime 존폐)·ADC-09(Workflow 그래프 의미 경계)의 재개설.

## Decision

**Accept (Conditional·Non-Mandatory)** — `docs/architecture/core/
ADC-0034-langgraph-implementation-technology-adoption.md` 판정을
그대로 따른다. LangGraph는 Workflow Adapter(§16.6) Production
구현이 별도 절차로 승인되는 시점의 구현 전략 후보로 확정되며, 사용은
강제되지 않는다(단순 사례는 기존 방식 유지 가능). Production 구현
착수 자체는 이 Decision으로 승인되지 않는다.
