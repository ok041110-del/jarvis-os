# BASELINE-V1.6-DEV-HQ-V2.0-ALIGNMENT-0001: BASELINE v1.6 ↔ Development HQ v2.0 Architecture Alignment Audit

**문서 성격**: READ-ONLY Architecture Alignment Audit. Production
Code·Architecture·Contract·`BASELINE.md`을 변경하지 않는다. BASELINE
버전을 승격하지 않는다. 신규 Kernel Component를 설계하지 않는다.
Phase 7을 구현하지 않는다. 신규 RFC/ADC/ADR을 작성하지 않는다.
Historical Evidence를 소급 수정하지 않는다.

**질문**: "BASELINE을 v2.0으로 올릴 것인가?"가 아니라 "현재 BASELINE
v1.6이 실제 Jarvis OS Architecture를 아직 정확하게 설명하고 있는가?"

---

## 1. Audit Scope

`docs/architecture/baseline/BASELINE.md`(v1.6) 원문 전체(§1~§17)와
Development HQ v2.0 관련 실제 Evidence(`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`,
`RFC-0007`, `RFC-0008`, `docs/governance/adc/ADC-0005.md`,
`docs/governance/adc/ADC-0006.md`, `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`,
Agent Package Refactoring Evidence, Stage 01~05/Integrated
Workflow/CLI E2E 문서)를 대조. 필요한 범위에서 `docs/decisions/**`,
`RFC-0012`, `ADC-0012`, `PHASE7-RESUME-REVIEW-0001.md`(직전 세션
Review)도 참조.

---

## 2. BASELINE v1.6 Summary

- §10 Out of Scope: **Kernel Component Architecture, Component
  Design(Scheduler/Engine Gateway/Registry/Communication/Memory/Policy),
  Workflow Runtime 내부 구조, `Development HQ 내부 설계`,
  Implementation** — "Development HQ 내부 설계"가 명시적으로
  Jarvis OS Baseline의 Out of Scope 항목이다.
- §11~§16: Kernel은 책임(Responsibility)으로만 정의되고 Component로
  구현되지 않는다(KP-1). §13 Kernel Context Model은 Segment/Ordering
  Policy/Renderer로 구성된 **논리적 계약**이며 실제 구현체가 아니다
  (Context Boundary·Engine별 Renderer·활용 사례는 §13.6에서 여전히
  Defer). §16 Kernel Modules는 Governance·Execution Layer 2건만
  Accept, Workflow/Memory/Event Bus 3건은 Defer 상태 유지.
- §17 Version 변경 이력(v1.0→v1.6)은 **매 버전 증가가 실제 신설
  §절 또는 ADR로 확정된 Architecture 내용 변경과 1:1 대응**한다(v1.1
  Kernel 정의 추가/ADR-0002, v1.2 §13 추가/ADR-0003, v1.3 §14 추가/ADR-0004,
  v1.4 §15 추가/ADR-0005, v1.5 §16 추가/ADR-0001, v1.6 §16.2 Execution
  Layer 내용 반영/ADR-0002-execution-layer). **다른 HQ의 버전 번호에
  맞춰 증가한 사례는 이력 전체에 없다.**

---

## 3. Development HQ v2.0 Evidence

- `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`(1~7행, 96~115행)가 스스로
  선언: *"새 Architecture/Component/Concept을 설계하지 않는다.
  Frozen Architecture와 Development HQ Baseline v1.0을 직접
  수정하지 않는다."* Architecture/Governance Review 항목 *"새로운
  Architecture/Component/Concept을 추가했는가 — 아니오"*.
- `RFC-0007`(AST Context Production Build 통합): *"본 RFC는
  Workflow/Agent/Model을 변경하지 않는다. Production Code도 변경하지
  않는다."* 대상은 `backend_agent_code_generation` Capability 하나.
- `RFC-0008`(Agent Package 물리 배치): *"이번 Task는 코드를
  변경하지 않는다... ADR도 작성하지 않는다."* 대상은
  `hqs/development/mvp/ast_context.py`의 module discovery 확장 하나.
- `docs/governance/adc/ADC-0006.md`(RFC-0008 후속, Conditional
  Accept): *"이 ADC는 ADC-0004/ADC-0005와 성격이 같다 — **Kernel
  승격 여부가 아니라** Development HQ MVP Implementation 범위 내에서
  기존 검증된 정적 분석 함수의 동작 조건을 확장할지 여부를 묻는다."*
  §Architecture Impact: *"확장 대상은 이미 Kernel 범위 밖(MVP
  Implementation, `BASELINE.md`...)"*. §Self Review: *"Kernel
  Leak가 없는가 — 없음."*
- `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md`: *"Runtime: 변경 없음.
  Runtime 자체가 Kernel 범위 Open Decision..."*
- Stage 01~05 / Integrated Workflow / CLI E2E 문서(`DEV-HQ-V2.0-STAGE-02~05-E2E-0001.md`,
  `DEV-HQ-V2.0-INTEGRATED-WORKFLOW-E2E-0001.md`,
  `DEV-HQ-V2.0-CLI-INTEGRATION-E2E-0001.md`)는 Architecture/Baseline/Kernel
  언급이 **0건** — 순수 Dev HQ 내부 실행 Evidence(pytest, real
  Engine E2E)로만 구성됨.

---

## 4. Architecture Alignment Matrix

| 변경 | Dev HQ 내부 변화 | 상위 Architecture 영향 | Kernel 영향 | 판정 |
|---|---|---|---|---|
| Stage 01~05 | `hqs/development/mvp/stages/` 구현·E2E 검증 | 없음(문서에 Architecture 언급 0건) | 없음 | INTERNAL ONLY |
| Integrated Workflow | `workflow.py` — Stage 1→5 호출 순서 | 없음 | 없음(하드코딩 호출, Workflow Runtime 미도입) | INTERNAL ONLY |
| CLI | `cli.py` — 실행 진입점 | 없음 | 없음 | INTERNAL ONLY |
| Agent Definition 0001 | Requirements/Design/Backend/QA 4개 Agent 역할 확정 | §7 "Agent 구성 및 역할 결정"은 원래 HQ 책임 — 그 범위 내 실행 | 없음(Runtime 변경 없음, 자체 명시) | ARCHITECTURE-COMPATIBLE |
| Agent Package Refactoring | `agents.py` → `agents/{requirements,design,backend,qa}.py` 물리 분리 | 없음(파일 배치만) | 없음(ADC-0006 §Architecture Impact가 명시) | INTERNAL ONLY |
| AST Context extension (dotted package path) | `ast_context.py` module discovery 확장 | §13.5(HQ가 Context 내용을 정한다)와 원칙적으로 정합하나, Kernel Context Model(§13)의 Segment/Ordering Policy/Renderer 계약을 구현한 것은 아님 — 별개의 HQ-local 메커니즘 | 없음(ADC-0006 Self Review "Kernel Leak 없음") | ARCHITECTURE-COMPATIBLE |

근거 없는 KERNEL IMPACT/CONFLICT 판정 없음 — 모든 행이 원문 Self
Review·Architecture Impact 서술로 뒷받침됨.

---

## 5. Kernel Boundary Impact

- **HQ-specific**: Stage 01~05, Integrated Workflow, CLI, Agent
  Package 물리 배치 — 전부 `hqs/development/mvp/` 내부에서만
  의미를 가지며 다른 HQ가 그대로 재사용할 수 있는 형태로
  일반화되지 않았다(Registry/Scheduler화 시도 없음, Implementation
  Stop Trigger 미발동).
- **Cross-HQ Architecture 후보(승격 아님)**: AST Context 기반 Build
  Capability 강화는 개념적으로 다른 HQ(Investment HQ 등)의 유사
  Capability에도 적용 가능해 보이지만, 이번 Evidence는 **Development
  HQ 하나에서만** 검증됐다 — "다른 HQ에서도 쓸 수 있다"는 가능성만으로
  Kernel-level로 승격하지 않는다(작업 지시 §7 원칙 그대로 적용).
- **Kernel-level**: 없음. §13 Kernel Context Model(Segment/Ordering
  Policy/Renderer)을 실제로 구현·확장한 사례가 Dev HQ v2.0 어디에도
  없다 — `ast_context.py`는 그 계약의 구현체가 아니라 Backend Agent
  Capability 하나를 위한 별도의 AST 정적 분석 도구다.
- **용어 중복 주의(Conflict 아님)**: BASELINE §13이 정의하는 "Kernel
  Context"와 Dev HQ v2.0의 "AST Context"는 같은 "Context"라는 단어를
  쓰지만 서로 다른 대상이다 — 전자는 Jarvis OS 수준의 미구현 논리
  계약, 후자는 Dev HQ 내부의 실제 구현된 정적 분석 도구. 두 문서
  집합 어디에도 이 둘을 동일시하는 서술은 없으나, 향후 독자가
  혼동할 위험은 §9에 기록한다.

---

## 6. Versioning Assessment

**Q1. 기존 BASELINE Architecture Boundary를 변경했는가?** — 아니오.
`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`가 §6 Architecture/Governance
Review에서 명시적으로 "아니오"로 자체 확인했고, `BASELINE.md` §7
System Boundary·§10 Out of Scope 문언 자체가 변경된 사실이 없다
(§17 변경 이력에 해당 항목 없음).

**Q2. Jarvis OS 전체 수준 Layer/Component/Interface/Contract가
추가됐는가?** — 아니오. 모든 RFC-0007/RFC-0008/ADC-0006 변경은
`hqs/development/mvp/` 범위로 스스로 한정되며, Jarvis OS 수준
Interface/Contract(§14)를 참조·확장한 문서가 없다(grep 결과 §14
PR-*/G-*/X-* ID 인용 0건).

**Q3. Kernel Responsibility가 변경됐는가?** — 아니오. §11~§16 어느
Kernel 책임 정의도 이 기간 수정되지 않았다(§17 변경 이력 v1.6이
마지막이며 그 내용은 Execution Layer Accept 반영, Dev HQ v2.0 이전
결정). ADC-0006(governance)도 "Kernel 승격 여부가 아니다"로 명시.

**Q4. 기존 Out of Scope 항목이 실제 Production Architecture에
들어왔는가?** — 아니오. §10이 "Development HQ 내부 설계"를 이미
명시적으로 Out of Scope로 지정해 두었으므로, Dev HQ v2.0의 모든
변경은 애초에 BASELINE이 다루지 않기로 한 영역 안에 있다 — "들어온"
것이 아니라 "처음부터 그 영역"이다.

**Q5. 기존 Baseline을 유지하면 현재 실제 Architecture를 잘못
설명하게 되는가?** — 아니오. BASELINE은 애초에 Development HQ 내부
설계를 설명 대상으로 삼지 않았다(§10). 설명하지 않기로 한 것을
설명하지 않는 것은 오류가 아니라 설계다.

**Q6. BASELINE v1.6 유지가 향후 Phase 7 이후 작업에 혼란을
일으키는가?** — 실질적 혼란 근거는 발견되지 않았다. 다만 문서
탐색 편의성 측면에서 사소한 위험이 있다: `ADC-0006`이라는 동일
번호가 서로 다른 namespace 3곳(`docs/decisions/adc/`,
`docs/governance/adc/`, `docs/architecture/core/`)에 각각 다른
내용으로 존재한다(§9 참조) — Architecture 정합성 문제는 아니며
Baseline 변경 사유가 아니다.

**결론**: Q1~Q5 전부 "아니오/영향 없음", Q6은 "Architecture
혼란 아님, 문서 탐색 편의성 문제"로 판정. BASELINE Versioning
Policy(§17 변경 이력이 실증하는 규칙)상 이번 Dev HQ v2.0 완료는
버전 증가 조건(신규 §절 또는 ADR로 확정된 Architecture 내용 변경)을
충족하지 않는다.

---

## 7. Phase 7 Impact

**Blocker unchanged.**

직전 세션 `PHASE7-RESUME-REVIEW-0001.md`가 확인한 `GOVERNANCE-REVIEW-0001`
§5의 6개 재개 근거(Kernel Module Defer 3건, ADC-02 Open, 승격 대상
없음, Engine 수 ≥2 미충족, §10 절차 유지, Execution Result PASS)를
이번 Audit에서 Dev HQ v2.0 Evidence로 재검증한 결과 — 어느 근거도
Dev HQ v2.0에 의해 변경되지 않았다. 특히:

- Engine 수: Dev HQ v2.0도 여전히 단일 Engine(`claude`) 사용 —
  Agent Definition 0001의 4개 Agent는 Capability 분리이지 Engine
  분리가 아니다(§4 Agent Definition 행 참조).
- Kernel Module Defer 3건(Workflow/Memory/Event Bus): Dev HQ v2.0의
  Integrated Workflow는 하드코딩 함수 호출이며 Workflow Runtime을
  구현하지 않았다 — Defer 상태에 영향 없음.
- ADC-02(Runtime 존폐): Dev HQ v2.0 Evidence 어디에도 재검토 시도
  없음(§3 Agent Definition 0001 "Runtime 변경 없음" 인용).

---

## 8. Final Verdict

**B. BASELINE v1.6 VALID WITH DOCUMENTATION GAP**

Architecture 자체는 완전히 정합한다(모든 Alignment Matrix 행이
INTERNAL ONLY 또는 ARCHITECTURE-COMPATIBLE, KERNEL IMPACT·CONFLICT
0건). BASELINE.md 내용 수정은 불필요하다. 다만 §9에 기록한
Documentation 편의성 이슈(ADC-0006 번호 중복, Phase 9~12 번호
중복 — 직전 세션에서도 확인)는 실제 Architecture 문제가 아니라
문서 탐색 편의성 문제이며, Baseline 변경 대상이 아니다.

---

## 9. Required Follow-up

- **BASELINE.md 수정 불필요** — 이번 Audit에서 발견된 Architecture
  Gap 없음.
- **Documentation 개선 후보(Governance 절차 대상 아님, 기록만)**:
  - `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md`,
    `docs/governance/adc/ADC-0006.md`,
    `docs/architecture/core/ADC-0006-kernel-context-ownership.md` —
    동일 번호("ADC-0006")가 서로 다른 namespace에서 서로 다른
    결정을 가리킨다. 각 문서 자체는 스스로의 범위를 명확히
    선언하고 있어 실질적 오독 사례는 없었으나, 향후 인용 시
    전체 경로(namespace) 표기를 권장한다.
  - `HANDOVER.md`의 "Phase 9~12"(Engine Adapter/Prompt Cache 등)와
    `roadmap.md`의 "Phase 9~12"(HQ Migration/Runtime/Dashboard)
    번호 중복은 `PHASE7-RESUME-REVIEW-0001.md` §8에서 이미 기록됨 —
    재기록만.
  - 위 두 항목 모두 **신규 RFC/ADC/ADR 대상이 아니다** — 필요하면
    별도 세션에서 명명 정리만(Architecture 결정 아님).
- Phase 7은 이번 Audit으로도 재개되지 않는다(§7).

---

## 최종 보고 (8~10개 항목)

1. 무엇을 비교했는가: `BASELINE.md`(v1.6) §7~§17 Kernel/Boundary
   조항과 Development HQ v2.0 실제 Evidence(Freeze 문서, RFC-0007/0008,
   ADC-0005/0006, Agent Definition, Stage/Workflow/CLI E2E)를 원문
   대조.
2. Dev HQ v2.0에서 확인된 주요 변화: Stage 01~05, Integrated
   Workflow, CLI, Agent Definition 0001(4개 Agent), Agent Package
   물리 분리, AST Context dotted package path 확장 — 전부
   `hqs/development/mvp/` 범위 내부.
3. BASELINE v1.6과 정합한 부분: 전체(6개 항목 전부 INTERNAL ONLY
   또는 ARCHITECTURE-COMPATIBLE). `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`,
   `ADC-0006`(governance) 모두 스스로 "Kernel/Architecture 변경
   없음"을 확인.
4. BASELINE에 영향을 줄 수 있는 부분: 없음. §10이 "Development HQ
   내부 설계"를 이미 Out of Scope로 지정해 둔 것이 이번 Freeze
   전체를 사전에 포섭한다.
5. Kernel 영향: 없음. §13 Kernel Context Model(계약)과 Dev HQ의
   AST Context(구현)는 이름만 겹칠 뿐 서로 다른 대상 — Kernel Leak
   없음(ADC-0006 Self Review).
6. Phase 7 영향: Blocker unchanged — §5의 6개 재개 근거 중 어느
   것도 Dev HQ v2.0으로 변경되지 않음(Engine 수 여전히 1, Kernel
   Module Defer 3건 그대로, ADC-02 그대로 Open).
7. Version Update 필요 여부: 불필요. §17 변경 이력이 보여주는
   Versioning 규칙(신규 §절/ADR 확정 내용만 버전 증가)에 이번
   Freeze가 해당하지 않음.
8. 최종 Verdict: **B. BASELINE v1.6 VALID WITH DOCUMENTATION GAP**.
9. 남은 작업: BASELINE 수정 없음. ADC 번호 중복(3곳 ADC-0006)·Phase
   번호 중복(HANDOVER vs roadmap Phase 9~12) 문서 탐색 편의성
   이슈만 기록, Governance 절차 불필요.
10. 다음 단계: Phase 7 재개 아님(여전히 BLOCKED, 직전 Review와
    동일). `HANDOVER.md` §Next Step이 지정한 Kernel Boundary/Component
    책임 검증을 계속 진행하는 것이 다음으로 유효한 작업.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 미실행(Production Code 변경 없어 불필요)
E2E: 미실행
RFC: 없음(신규 작성 안 함)
ADC: 없음(신규 작성 안 함)
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 문서 커밋 예정)
Branch: `claude/baseline-v1.6-devhq-v2.0-alignment-audit`
Next Implementation Candidate: 없음(Kernel Boundary/Component 책임
검증 관찰 활동만 유효, 신규 구현 대상 아님)
