# ADC-0034: LangGraph 승인된 비강제 Implementation Technology 확정 판단 (RFC-0031 후속)

## 목적

RFC-0031이 제기한 Q-1 Boundary Question을 판단한다. 근거는 RFC-0031
원문과 그것이 인용하는 `ADR-0018`, `projects/
langgraph-conditional-routing-poc-v1/EVIDENCE.md`(PR #173),
`docs/architecture/baseline/BASELINE.md` §16.6, `ADC-0013`/`ADC-0014`/
`ADC-0015`(Execution Host 3단계 선례), `ADR-0011`(Implementation
Freedom)로 한정한다. 이 문서 자체는 새로운 조사를 하지 않는다.

이 ADC는 ADC-0015와 같은 성격이다 — 책임의 존재나 명칭이 아니라
**이미 존재·명명이 끝난 책임의 구현 전략**을 판단한다.

## 판단 대상에서 제외

- Workflow Adapter의 존재(`ADC-0019`)·명칭(`ADC-0020`) 재론 — 무변경.
- Production 구현 착수 승인 — 별도 Scoped 해제 ADR 대상, 이 ADC의
  범위 밖(§16.6이 이미 이 경계를 명시).
- `IMPLEMENTATION_RULES.md`의 Workflow Parser/Scheduler/Dynamic
  Routing/Event Bus 구현 금지 해제 — 다루지 않는다.
- `ADC-02`(Runtime 존폐)·`ADC-09`(Workflow 그래프 의미 경계) 재개설
  — 하지 않는다(사용자 지시 7번).
- LangGraph를 특정 기존 코드(Development HQ/Investment HQ)에 실제로
  배선하는 것 — 이 ADC는 승인 목록 등재 여부만 판단한다.

---

## 판단 (Q-1). LangGraph를 승인된 비강제 Implementation Technology로 확정할 것인가

### Evidence

- **기존 계보(재확인만, 재조사 아님)**: v1 `archive`에서 LangGraph가
  `IWorkflowEngine` Adapter로 실사용 검증되고 Reversibility(순차
  함수로 교체해도 Core 무수정)까지 증명됨(ADR-0007). v2 E2(toy PoC,
  API 호환), E3(Domain PoC, Investment HQ Stock Team 의미 반영,
  26/26 PASS), Phase E(RFC-0028, 실제 Handoff/실패격리/병렬 7/7
  PASS, "Scheduler/Runtime 필요 마찰 0회 관찰"), Phase F(Stage 04/05
  Agent 분리 불필요 결론) — 전부 "LangGraph는 기술적으로 동작하고
  Kernel 경계를 지킬 수 있다"는 결론에 반복 도달했다.
- **신규 Evidence(PR #173)**: 실제 프로덕션 Capability
  (`backend_agent_code_review`/`qa_agent_test_execution`)와 실제
  Engine 호출(Claude CLI, 4회) 기반 Conditional Routing Prototype.
  baseline과 LangGraph 구현의 분기 판정이 **2/2 케이스 100% 일치**,
  LangGraph 자체는 결함 없이 정상 동작. `git status`로 `hqs/`,
  `core/`, `docs/architecture/`, `docs/decisions/` 무변경 확인됨.
- **`ADR-0011`(Implementation Freedom)**: "Evidence의 부재 자체는
  구현 기술 선택을 금지하는 사전 허가 조건이 아니다... Goal과
  Invariant를 만족하는 범위에서 개발자·사용자·AI는 구현 기술을
  자유롭게 선택할 수 있다."
- **`BASELINE.md` §16.6 자체가 이미 지정한 절차**: "구현체 선택
  (LangGraph 채택 여부 포함)... 별도 절차(RFC → ADC → ADR)로
  남는다 — Execution Host가 존재 → 명명 → 구현 전략 3단계로 분리한
  선례를 그대로 따른다." 이 ADC가 정확히 그 절차다.

### Constraint / Boundary

- 이 ADC가 "Accept"하더라도 §16.6 "Production 구현과의 관계" 문단
  (`IMPLEMENTATION_RULES.md` 금지 조항 무변경)은 이 ADC로 해제되지
  않는다 — 그 해제는 별도 ADR("Reversibility의 v2 완전 검증 이후"
  조건, §16.6 명시)이 판단한다.
- `ADC-02`/`ADC-09`는 이 ADC로 재개설되지 않는다 — Workflow Adapter는
  "Runtime" 정의 중 "조건부·반복 조율" 조각 하나일 뿐이라는 기존
  경계(`ADC-0019` §Q8)를 그대로 유지한다.
- PR #173의 결과 자체(단순 분기에는 이점 없음)는 뒤집지 않는다 —
  "승인 목록에 올린다"와 "이 시나리오에 쓰라고 권고한다"는 다른
  질문이다.

### Options

- (a) **승인된 비강제 후보로 확정** — LangGraph를 Workflow Adapter
  구현 전략의 승인된 후보 중 하나로 등재. Production 구현이 별도로
  승인되는 시점에 처음부터 재평가하지 않아도 됨. 단순 사례(조건부
  분기 등)에는 기존 방식이 여전히 기본값.
- (b) `ADR-0018`의 Deferred/Not Adopted 유지 — Production 구현
  승인 시점에 처음부터 재평가.
- (c) 판단 보류.

### Recommendation

(a). Evidence(§Evidence)는 "가능한가"라는 질문에는 이미 여러 차례
반복 답했고, 이번 PR #173은 "실제 프로덕션 코드 위에서도 문제없이
동작한다"는 마지막 남은 유형의 Evidence(toy/Domain PoC를 벗어난
실제 Capability + 실제 Engine)를 채웠다. `ADR-0011`(Implementation
Freedom) 기준으로 "가치가 제한적으로 보인다"는 사실(§16.6이 다루는
단순 사례) 자체가 승인을 막을 근거는 아니다 — 오히려 그 가치 판단을
"필요할 때 다시 논의"가 아니라 "지금 기록해 두고 필요할 때 즉시 쓸 수
있게"하는 것이 Evidence 축적 원칙(P12, Evidence over Authority)에
부합한다. (b)는 이미 충분히 쌓인 Evidence를 무시하고 매번 같은 질문을
반복하게 만든다 — Governance v2 P17(반복되는 비용은 상위 절차 재검토
신호)과 배치된다.

### Final Judgment

**Accept (a), Conditional·Non-Mandatory.**

1. LangGraph는 Workflow Adapter(§16.6) Production 구현이 **별도
   절차로 승인되는 시점에**, 그 구현 전략의 **승인된 후보** 중
   하나로 확정된다 — Execution Host의 Process/Subprocess(`ADC-0015`)
   와 같은 지위다.
2. **비강제(Non-Mandatory)**: 이 Accept는 LangGraph 사용을 강제하지
   않는다. 단순한 조건부 분기 등 기존 plain 구현이 더 단순하고
   충분한 경우, 기존 방식을 계속 사용할 수 있다(PR #173 Evidence가
   바로 이 경우를 실측했다) — "모든 Workflow를 LangGraph로 전환"
   하거나 강제 적용하지 않는다.
3. **Production 구현 착수는 이 Accept로 승인되지 않는다** —
   §16.6 "Production 구현과의 관계" 문단, `IMPLEMENTATION_RULES.md`의
   금지 조항은 무변경. 이 Accept는 오직 "구현 후보 목록"에 대한
   것이다.
4. **소급 미적용** — 이 Accept는 이후 Workflow Adapter Production
   구현이 승인될 때 적용되는 사전 등재이며, 기존 완료된 Evidence
   문서(`ADR-0018` 포함)의 과거 판정을 다시 쓰지 않는다. `ADR-0018`은
   역사적 기록으로 보존하고, 이 판단은 새 ADR(ADR-0019)로 그것을
   **Supersede**한다(Governance v2 P7 — 새 Evidence는 새 Decision으로
   기존 Decision을 supersede).
5. `ADC-02`/`ADC-09`는 재개설하지 않는다 — 무관.

---

## 종합 Decision

**Accept (Conditional·Non-Mandatory).**

| 대상 | Governance 변경 필요 | 처리 |
|---|---|---|
| LangGraph 승인된 비강제 구현 후보 확정 | 필요 | 후속 ADR(ADR-0019)에서 `ADR-0018` Supersede + `BASELINE.md` §16.6 최소 상태 갱신 |
| Production 구현 착수 승인 | 불필요(이 ADC 범위 아님) | 별도 Scoped 해제 ADR 대상, 무변경 |
| `IMPLEMENTATION_RULES.md` 금지 조항 해제 | 불필요 | 무변경 |
| `ADC-02`/`ADC-09` 재개설 | 불필요 | 무변경 |
| `ADR-0018` 원문 수정 | 불필요(삭제·왜곡 금지) | Supersede 표시만 추가, 본문 보존 |

Baseline 반영 정확한 문구·배치는 후속 ADR 단계에서 확정한다(이 ADC가
결정하지 않음). RFC-0031의 Status/Decision 절은 이 ADC의 결과를
반영해 Resolved로 갱신한다.

**후속 ADR**: `docs/architecture/core/ADR-0019-langgraph-implementation-technology-adoption-baseline.md`.
