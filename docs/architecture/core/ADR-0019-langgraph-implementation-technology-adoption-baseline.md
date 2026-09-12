# ADR-0019: LangGraph — 승인된 비강제 Implementation Technology 확정 (Workflow Adapter 구현 전략, `ADR-0018` Supersede)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0019` |
| 제목 | RFC-0031(Boundary Question) → ADC-0034(Q-1 Final Judgment)의 판단을 실제 Baseline 반영 결정으로 확정한다 — LangGraph를 Workflow Adapter(§16.6) Production 구현의 승인된 비강제 구현 전략 후보로 등재한다 |
| 상태 | **Accepted.** |
| Context | `docs/architecture/core/RFC-0031-langgraph-implementation-technology-adoption.md`(Q-1 Boundary Question) + `docs/architecture/core/ADC-0034-langgraph-implementation-technology-adoption.md`(Accept, Conditional·Non-Mandatory) |
| 관련 RFC | `RFC-0031` |
| 관련 ADC | `ADC-0034` |
| Supersede 대상 | `ADR-0018`(LangGraph Adoption Final Review, Deferred/Not Adopted) — §1 참고, 본문은 보존·재작성하지 않음 |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0013`/`ADC-0014`/`ADC-0015`(Execution Host 존재→명명→구현전략 3단계 선례), `ADC-0019`/`ADC-0020`(Workflow Adapter 존재·명칭), `ADR-0011`(Implementation Freedom) |
| 신규 Evidence | `projects/langgraph-conditional-routing-poc-v1/`(PR #173) — 실제 프로덕션 Capability + 실제 Engine 호출 기반 Conditional Routing Prototype, `EVIDENCE.md` |

이 ADR은 `ADC-0034`가 이미 내린 Q-1 Final Judgment를 다시 논의하지
않는다. 이 ADR이 하는 일은 그 판단을 실제 문서에 무엇을, 어디에,
어떤 문구로 반영할 것인지로 구체화하는 것뿐이다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| Workflow Adapter Production 구현 착수 승인 | `ADC-0034` 판단 — 별도 Scoped 해제 ADR 대상, §16.6이 이미 명시한 경계 |
| `IMPLEMENTATION_RULES.md`의 Workflow Parser/Scheduler/Dynamic Routing/Event Bus 구현 금지 해제 | 무변경 |
| `ADC-02`(Runtime 존폐)·`ADC-09`(Workflow 그래프 의미 경계) 재개설 | 하지 않는다 |
| Workflow Adapter의 존재(`ADC-0019`)·명칭(`ADC-0020`) 재론 | 무변경 |
| `ADR-0018` 본문 재작성 | 삭제·왜곡 금지 — Status 필드에 Supersede 표시만 추가(§1 이미 반영) |
| 코드/Development HQ/Investment HQ 실제 배선 | 대상 아님 |

---

## Decision

### 1. `ADR-0018` Supersede 처리 (완료)

`ADR-0018`의 Status 필드에 "2026-09-08, `ADR-0019`가 이 판정을
Supersede함" 문구를 추가했다(본문·Gate 표·근거는 원문 그대로
보존 — Governance v2 P7 "새 Evidence는 새 Decision으로 기존 Decision을
supersede하되, Accepted Decision은 역사로 보존한다"). `ADR-0018`이
내린 "Production 구현 미승인" 결론은 이 Supersede로도 **무변경**이다
— Supersede되는 것은 "LangGraph를 승인 후보로 사전 확정할 수 있는가"
라는 이 ADR이 새로 답한 질문뿐이다.

### 2. LangGraph Adoption 확정 (ADC-0034 Q-1 Final Judgment 반영)

**LangGraph는 Workflow Adapter(§16.6) Production 구현이 별도
절차로 승인되는 시점의, 승인된(비강제) 구현 전략 후보로 확정된다.**

- **범위**: State 기반 Agent workflow, Conditional routing 이상의
  복잡도(다중 Loop, 값 기반 Checkpoint/Resume, Agent orchestration,
  Workflow composition 등)가 실제로 필요해지는 경우에 한해 선택
  가능한 후보 중 하나다.
- **비강제(Non-Mandatory)**: "모든 Workflow를 LangGraph로 전환"하거나
  강제하지 않는다. 단순한 조건부 분기 등 기존 plain 구현(예:
  `workflow_0002.py`의 `if/else`)이 더 단순하고 적절한 경우, 기존
  방식을 계속 사용할 수 있다 — `projects/
  langgraph-conditional-routing-poc-v1/EVIDENCE.md`가 정확히 이
  경우를 실측했다(2/2 케이스에서 LangGraph가 이점을 만들지 못함).
- **Implementation Technology이지 Architecture가 아니다**: 이 확정은
  §16.6이 이미 정의한 Workflow Adapter 책임(State/Node/Conditional
  Edge/Loop/값 기반 Checkpoint-Resume)의 구현체 선택 문제이며, 그
  책임 자체의 경계·A-IN/A-OUT을 재정의하지 않는다. Kernel Module
  정의(§6 Concept Model), Kernel Public Contract(§14)는 이 ADR로
  변경되지 않는다.
- **Production 구현 착수는 이 Decision으로 승인되지 않는다**(위 Out
  of Scope 표).

### 3. 실제 반영 범위

| 대상 파일 | 반영 내용 |
|---|---|
| `docs/architecture/core/ADR-0018-langgraph-adoption-final-review.md` | Status 필드에 Supersede 표시 추가(완료, §1) — 본문 무변경 |
| `docs/architecture/baseline/BASELINE.md` §16.6 | "이 Accept가 결정하지 않는 것" 문단 중 "구현체 선택(LangGraph 채택 여부 포함)... 별도 절차(RFC → ADC → ADR)로 남는다" 문장 다음에, 그 별도 절차가 이 ADR로 완료됐다는 한 문장만 추가(§4 실제 diff). §16.6의 나머지 본문(A-IN/A-OUT/Production 구현 관계 등)은 무변경 |
| `docs/architecture/baseline/BASELINE.md` §17 Version | v1.19 행 추가(§4 실제 diff) |
| `.claude/docs/integrations/langgraph.md` | "도입 판단" 절 말미에 이 ADR을 인용하는 갱신 노트만 추가 — 기존 PoC 기록(2026-08-30/09-02)은 무변경 |
| 그 외 | 없음 — 코드, `IMPLEMENTATION_RULES.md`, `ADC.md`, Kernel Public Contract(§14)는 대상이 아니다 |

### 4. `BASELINE.md` 실제 diff

§16.6 "이 Accept가 결정하지 않는 것" 문단 뒤에 추가:

> **2026-09-08 갱신(`ADR-0019`)**: 위 문단이 별도 절차로 남긴
> "구현체 선택(LangGraph 채택 여부 포함)"에 대해, `RFC-0031` →
> `ADC-0034` → `ADR-0019`가 LangGraph를 **승인된 비강제 구현 전략
> 후보**로 확정했다(Execution Host의 `ADC-0015`와 같은 지위). 이
> 확정은 위 "Production 구현과의 관계" 문단(Production 구현 착수
> 미승인, `IMPLEMENTATION_RULES.md` 금지 조항 무변경)을 변경하지
> 않는다 — LangGraph는 그 별도 승인이 이뤄질 때 선택 가능한 후보
> 목록에 포함될 뿐이다. `ADC-02`/`ADC-09`는 이 갱신으로 재개설되지
> 않는다.

§17 Version 표에 다음 행 추가(맨 위, 최신):

> | v1.19 | §16.6 "이 Accept가 결정하지 않는 것" 문단에 LangGraph
> 구현 전략 확정 갱신 노트 추가(`ADR-0019`) — Workflow Adapter의
> 존재·경계·A-IN/A-OUT·Production 구현 미승인 상태는 무변경. `ADC-02`/
> `ADC-09`는 재개설되지 않음. 근거: `docs/architecture/core/
> ADR-0019-langgraph-implementation-technology-adoption-baseline.md` |

## 5. Architecture/Contract 불변 확인

- Kernel Module 정의(§6), Kernel Public Contract(§14), Workflow
  Adapter의 A-IN/A-OUT(§16.6 본문)은 한 글자도 변경하지 않는다 —
  §16.6에 상태 갱신 노트 한 문단만 추가한다.
- `IMPLEMENTATION_RULES.md`는 무변경 — Workflow Parser/Scheduler/
  Dynamic Routing/Event Bus 구현 금지 유지.
- `ADC.md`(ADC-02/ADC-09/ADC-10)는 무변경 — 재개설하지 않는다.
- 코드 파일은 이 ADR로 일절 수정하지 않는다.

## 6. 기존 RFC/ADC/ADR/Freeze와의 충돌 확인

- **`ADR-0018`**: 충돌 없음 — Supersede는 Status 필드 표시로만
  이뤄지고 본문·Gate 표·근거는 그대로 보존된다. "Production 구현
  미승인" 결론은 이 ADR에서도 동일하게 유지된다.
- **`BASELINE.md` §16.6**: 충돌 없음 — 그 문단이 스스로 예정해 둔
  "별도 절차"를 이 ADR이 완료했을 뿐이며, A-IN/A-OUT/Production
  구현 관계 문단은 그대로다.
- **`ADC-0013`/`ADC-0014`/`ADC-0015`(Execution Host 선례)**: 충돌
  없음 — 동일한 3단계(존재→명명→구현전략) 패턴을 Workflow Adapter에
  재사용했을 뿐이다.
- **`ADR-0011`(Implementation Freedom)**: 충돌 없음 — 이 ADR은 그
  원칙("Evidence 부재가 사전 금지 조건이 아님")을 실제로 적용한
  사례다.
- **`ADC-02`/`ADC-09`(`docs/decisions/adc/ADC.md`)**: 충돌 없음 —
  재개설하지 않았고, Workflow Adapter가 "Runtime" 정의의 부분
  집합이라는 기존 경계(`ADC-0019` §Q8)도 무변경.
- **`IMPLEMENTATION_RULES.md`**: 충돌 없음 — 무변경.

---

## Consequences

- LangGraph는 이제 "Deferred/Not Adopted"라는 단일 상태 대신,
  **"Production 구현은 미승인이나, 그 구현이 승인되면 즉시 쓸 수
  있는 승인된 비강제 후보"**라는 더 정확한 상태로 문서화된다.
- 향후 Workflow Adapter Production 구현이 별도 절차로 승인되는
  시점에, LangGraph 채택 여부를 처음부터 다시 RFC로 여는 비용이
  사라진다 — 이 ADR이 그 평가를 대신 완료해 두었다.
- 단순한 조건부 분기·순차 호출 같은 저복잡도 사례에는 이 ADR이
  LangGraph 사용을 권장하거나 강제하지 않는다 — `projects/
  langgraph-conditional-routing-poc-v1/EVIDENCE.md`가 그 경우
  기존 방식이 최소한 동등하거나 더 낫다는 것을 실측했다.
- `ADR-0018`은 역사적 기록으로 그대로 남고, 그 판단(Production 구현
  미승인)도 무변경이다 — 이 ADR은 그 위에 새 질문의 답만 얹었다.
- 남는 절차: Workflow Adapter Production 구현 자체의 Scoped 해제
  여부는 여전히 별도 ADR 대상이며, 이 ADR은 그 절차를 대신하거나
  앞당기지 않는다.
