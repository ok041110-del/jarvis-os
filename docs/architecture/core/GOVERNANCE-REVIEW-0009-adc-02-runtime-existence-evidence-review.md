# GOVERNANCE-REVIEW-0009: ADC-02 Runtime Architecture Decision Evidence Review

**문서 성격**: READ-ONLY Governance Review. **Decision 문서가 아니다.**
새 RFC/ADC/ADR을 작성하지 않는다. `docs/decisions/adc/ADC.md`의 ADC-02
상태를 이 문서가 직접 바꾸지 않는다. Production 코드는 한 줄도
수정하지 않았다. ADC-09/ADC-10 등 다른 항목을 재판단하지 않는다.

**질문**: "Jarvis OS에서 Runtime이라는 독립적인 Architecture 개념/구현
책임이 실제로 필요한가?" — ADC-02(`docs/decisions/adc/ADC.md`) 결정을
위한 근거 자료로만 사용한다. 최종 ADR이 아니다.

---

## 1. 무엇을 조사했는가

1. main 전체에서 Runtime 관련 코드/문서/Architecture 정의 검색
   (`grep -rn Runtime docs/ core/ hqs/ dashboard/`, `ADC.md` 전체 재조회).
2. `BASELINE.md` §6(Concept Model)·§16.3(Kernel Modules)의 Runtime/
   Execution Host 정의.
3. Runtime 관련 기존 ADC/RFC/ADR 계보 전체:
   `RFC-0008`/`ADC-0008`, `RFC-0004`(Dev HQ), `RFC-0013`/`ADC-0013`,
   `RFC-0014`/`ADC-0014`/`ADR-0004`, `ADC-0011`, `ADC-0012`,
   `RFC-0024~0027`(Agent Domain/Lifecycle/State/Multi-Agent Workflow/
   Runtime Contract Candidate), `RFC-0028`(Phase E, Minimal Runtime MVP
   실행 Evidence), `GOVERNANCE-REVIEW-0001`, `GOVERNANCE-REVIEW-0006`.
4. Execution Host(`ADC-0013` Scoped Accept, `ADR-0003`/`ADR-0004`/
   `ADR-0005`)와 Runtime 책임 경계.
5. Scheduler / Workflow Adapter / Engine Adapter / Multi-Task 현재
   책임과 Runtime 중복 여부(`ADC-0016~0023`, `ADC-0027`, `ADC-0031`,
   `ADC-0034`/`ADC-0035`).
6. 실제 구현(`core/`, `hqs/`, `dashboard/`)에서 Runtime이라는 독립
   Component가 존재했거나 필요했던 사례.
7. Validation: `pytest hqs/development/mvp/tests/`,
   `pytest projects/multi-agent-handoff-mvp-v1/tests/`, 정적 grep.

---

## 2. Evidence

### 2.1 ADC-02 현재 상태 (Single Source of Truth)

`docs/decisions/adc/ADC.md` ADC-02: **상태 Open · 우선순위 NOW**
(최근 수정 2026-08-28, 이 문서로 변경하지 않음). 원문 충돌 내용: "Concept
Model은 Runtime을 Service로 유지하나, Core Component 검토에서는
Runtime을 폐기하고 Scheduler + Engine Gateway로 대체할 것을 권고함."

### 2.2 "넓은 범위" Runtime — 반복적으로 Not Accepted / Defer

| 문서 | 판단 | 근거 |
|---|---|---|
| `ADC-0008-runtime-existence-boundary.md` | Not Accepted (양쪽 후보 모두) | "유지" 근거(BASELINE §6)는 원문이 스스로 미결정을 선언, "대체" 근거("Core Component 검토")는 추론 과정이 저장소에 없음 |
| `ADC-0011-standalone-execution-location-boundary.md` | Not Accepted | (ADC.md·RFC-0028 §1 표에서 재인용, 미해소로 재확인) |
| `ADC-0012-dispatch-component-boundary.md` | Defer | Kernel Component Architecture 전체 착수 판단 — Rule B(3건 이상 독립 관찰) 미충족 |
| `GOVERNANCE-REVIEW-0006` | Open 유지 권고 | MVP-0038~0048, Stock/ETF/Dividend Stock Team Dogfooding 9건 전부 `runner.py`의 하드코딩 순차 함수 호출로 완주 — Runtime(Workflow 참조 Task 배분) 필요성 사례 없음. ADC 채택 기준(①지금 결정 안 하면 진행 불가, ②지연 시 되돌리는 비용 급증) 둘 다 미충족 |

### 2.3 "좁은 범위" 책임 — Accept된 것은 Runtime이 아니라 별개 Concept("Execution Host")

- `RFC-0013`/`ADC-0013`: "Command·Task로 환원되지 않는, 단일 실행
  단위의 dispatch·격리 책임"만 좁게 떼어 **Accept(Scoped)**. 근거는
  7개 Prototype/Vertical Slice(Command 불변성 보호, Task가 Executor를
  참조하지 않고도 동작, Thread 동시 실행 시 실제 정확성 결함 재현,
  Process 격리가 이를 해소).
- `RFC-0014`/`ADC-0014`/`ADR-0004`: 이 책임의 **명칭을 "Execution
  Host"로 확정** — `ADC-0014` §Q2가 "§6 Concept Model의 'Runtime'
  항목을 재명명한 것이 아니라 그와 별개의, 더 좁은 범위의 Concept"이라고
  명시적으로 판정. `ADR-0004`는 §6 "Runtime" 행을 손대지 않았고,
  `ADC.md`의 ADC-02도 변경하지 않았다(§Out of Scope 표에 명시).
- `BASELINE.md` §16.3: "Execution Host — 단일 실행 단위 Dispatch·격리
  (Accept, Scoped)". 본문이 직접 "§6의 'Runtime' 항목(Service 분류,
  Workflow 참조·Multi-Task 배분을 포함하는 넓은 정의)은 이 명칭
  반영으로 전혀 변경되지 않으며, ADC-02도 Open 상태 그대로 유지된다"고
  명시.
- `hqs/development/IMPLEMENTATION_RULES.md`: "Scheduler/우선순위/
  Workflow orchestration/Dynamic Routing 및 §6 넓은 Runtime(Workflow
  참조 전체) 구현 금지" 조항이 **현재도 유효** — 사유란이 "Runtime
  존폐 자체가 여전히 결론 없다 — ADC-02(Open, NOW), ADC-0008(Not
  Accepted), ADC-0011(Not Accepted), ADC-0012(Defer) 중 어느 것도
  Accept가 아니다"라고 명시.

### 2.4 최신 실행 Evidence — Multi-Agent 맥락에서도 필요성 미관찰 (Phase E)

`RFC-0027`(Multi-Agent Runtime Contract Candidate Boundary)의 문서
조사 결론을 `RFC-0028`(Minimal Runtime MVP 필요성 검증, main 병합
완료, commit `eb0b317`)이 실행 Evidence로 재검증:

- `projects/multi-agent-handoff-mvp-v1/`(Experimental, 격리): Agent
  역할 2개(순수 함수, Kernel/HQ import 없음), 순차 전달, 값 기반
  실패/종료, `ThreadPoolExecutor` 기반 독립 병렬 실행을 **기존
  Contract(직접 함수 호출 + 표준 라이브러리)만으로** 마찰 없이 재현.
- IN-6(정적 검사): LangGraph·Kernel/HQ production·Runtime/Scheduler/
  Registry/Agent Manager/Event Bus 어휘 의존 **0건**.
- 결론(§5): "충분하다 — 사용자가 요구한 최소 조건이 기존 Contract만으로
  마찰 없이 재현됐다." §6: "Runtime Candidate 발생하지 않았다 — 오히려
  '새 Runtime 없이도 충분하다'는 반대 방향 Evidence를 추가했다."
- 이 RFC는 ADC-02를 대신 판정하지 않고 Open 상태를 그대로 유지했다
  (§9, §Self Review).

### 2.5 실제 구현 검색 결과

`grep -rn "class.*Runtime" core/ hqs/ dashboard/`: `RuntimeError`
서브클래스 1건(`hqs/investment/checkpoint.py:12`, Python 표준
예외 상속 — Architecture Concept과 무관) 외 **Runtime이라는 이름의
독립 Component/Service 구현 없음**. `RuntimeService`·Runtime import
등도 0건.

### 2.6 Scheduler/Workflow/Engine Adapter/Multi-Task — 현재 각자 책임과 Runtime 중복 여부

| Component | Accept 여부·근거 | Runtime(넓은 정의)과의 관계 |
|---|---|---|
| Execution Host(§16.3) | Accept(Scoped), `ADC-0013`/`ADR-0003`/`ADR-0004` | 단일 실행 단위 dispatch·격리만 — Workflow 참조·Multi-Task 배분 없음(별개 Concept, §2.3) |
| Multi-Task(§16.4) | Accept(Scoped, Minimal), `ADC-0016`/`ADR-0006` | 독립 동시 실행만 — Agent 동적 배분 없음 |
| Workflow Adapter | Accept(Scoped), `ADC-0019~0023`/`ADR-0008`/`ADR-0009` | 고정 그래프 진행만 — Dynamic Routing 없음(§2.3 표 인용 원문) |
| Engine Adapter(OmniRoute) | Accept, `ADC-0027`/`ADC-0031`/`ADR-0015`/`ADR-0017` | LLM 호출 경계만 |
| LangGraph/Graphify | 비강제 구현 기술로 Accept, `ADC-0034`/`ADC-0035`/`ADR-0019`/`ADR-0020` | 구현 기술 채택이지 ADC-02 재판정 아님(두 문서 모두 Runtime 언급 없음) |

`RFC-0028` §1이 이 네 갈래(Execution Host·Multi-Task·Workflow
Adapter·Engine Adapter)를 "4갈래 모두 Accept(Scoped), 'Agent 동적
배분'만 미제공"으로 정리했다 — 이 요약을 이 문서가 재확인했다.

### 2.7 Validation 실행 결과

- `pytest hqs/development/mvp/tests/ -q` → **186 passed, 6 skipped**
  (RFC-0028 인용값과 동일, 이 문서가 새로 실행해 재확인).
- `pytest projects/multi-agent-handoff-mvp-v1/tests/ -q` → **7 passed**.
- 정적 grep: Production 코드에 Runtime 독립 Component 없음(§2.5).

---

## 3. 무엇이 확인되지 않았는가

- **"Core Component 검토" 원문**: ADC-02 원문이 언급하는 "대체" 후보의
  근거 문서가 저장소 어디에도 없다(`ADC-0008` 재검토 조건 1번,
  `GOVERNANCE-REVIEW-0006`도 동일하게 미충족 확인) — **Evidence 없음**.
- **넓은 정의(Workflow 참조·Multi-Task를 Agent에게 배분)의 실제 필요
  사례**: Dev HQ Dogfooding 9건, Multi-Agent Handoff Experimental
  1건 등 모든 실행 Evidence가 이 넓은 책임 없이 완주됐다 — 필요했던
  사례 **없음**(Evidence 없음, 반대 방향으로는 확인됨).
- **서로 다른 독립 계기의 반복 관찰(Rule B, 3건 이상)**: `ADC-0013`
  Q2가 스스로 인정했듯, 좁은 범위 Accept의 근거 5개 Prototype은 "같은
  저자·같은 세션"이라는 하나의 계기다. `RFC-0028`(Phase E)을 더하면
  서로 다른 시점의 계기가 늘었으나, 이는 "필요"가 아니라 "불필요"
  방향의 반복 관찰이다 — 여전히 "Runtime 필요"를 뒷받침하는 형식적
  3건 독립 관찰은 **확인되지 않음**.
- **ADC-09(Workflow 그래프 의미론)·ADC-10(Policy 출처 분리)과의 교차
  영향**: 이번 조사 범위 밖(작업 지시 명시) — 언급만 하고 재판단하지
  않았다.

---

## 4. A/B/C 비교 — Outcome → Invariant → Implementation Freedom 관점

**A. Runtime을 독립 Architecture Component/Service로 유지**

- 지지 Evidence: `BASELINE.md` §6이 Runtime을 Service로 이미 분류해
  둔 Architecture Intent(`ADC-0013` Q0) 뿐 — Q0 자체가 "단독으로는
  Accept 근거 부족"이라고 판정된 상태(§2.3).
- 반대 Evidence: 넓은 정의(Workflow 참조·Multi-Task 배분)를 필요로 한
  실제 Outcome 사례가 하나도 없다(§2.2, §2.4). Invariant(지켜야 할
  불변 제약)가 아직 식별되지 않은 상태에서 Component를 먼저 확정하면
  Outcome-Invariant-Implementation Freedom 원칙("Outcome이 먼저,
  Implementation은 자유")을 거스른다.
- **판정**: Evidence 부족. 현재 채택 시 근거 없는 선제적 Architecture
  확정이 된다.

**B. Runtime 개념 자체를 제거**

- 지지 Evidence: `ADC-0008`·`ADC-0011`(Not Accepted), `ADC-0012`
  (Defer) — "유지" 방향 근거가 부족한 것은 확인됐으나, 이 판정들
  자체가 "폐기"를 Accept한 것도 아니다(`ADC-0008`은 "대체" 후보도
  Not Accepted). `BASELINE.md` §16.3·`ADR-0004`는 "§6 Runtime
  항목을 재명명·삭제하지 않는다"는 판단을 반복해 왔다 — 제거를
  적극적으로 뒷받침한 Decision은 없다.
- 반대 Evidence: 제거는 "다시는 필요 없다"는 영구 결론인데,
  `RFC-0028` §8(Non-goals)이 스스로 "Multi-Agent Runtime이 필요
  없다고 영구적으로 주장하지 않는다 — 실제 Architecture Need가
  나중에 관찰되면 재검토는 언제든 가능하다"고 명시한다. 완전 제거는
  이 문서들이 유지해 온 신중한 태도보다 더 강한 주장이다.
- **판정**: 현재 Evidence는 "지금 채택할 근거 없음"을 반복 확인할
  뿐, "영구히 불필요함을 확정"하는 수준까지는 가지 않는다.

**C. Runtime은 상위 실행환경 개념으로 유지하되 독립 구현 Component로 확정하지 않음**

- 지지 Evidence: 지금까지의 모든 Decision Chain이 사실상 이 노선을
  걸어왔다 — `BASELINE.md` §6(Concept으로서 Runtime을 Service 분류로
  유지, 각주로 "세부 구조는 Open Decision"이라 유보), `ADC-0013`/
  `ADC-0014`(넓은 Runtime과 명시적으로 분리된, 더 좁은 "Execution
  Host"만 별도 구현 책임으로 Accept), `ADR-0004`(§6 Runtime 항목
  불변, §6에 Execution Host도 추가하지 않음 — 좁은 책임을 §6 상위
  개념과 섞지 않음), `IMPLEMENTATION_RULES.md`(넓은 Runtime 구현은
  계속 금지, 좁은 Execution Host만 Scoped 허용), `RFC-0028`(Multi-Agent
  맥락에서도 기존 4갈래 Scoped Component로 충분함을 실행 Evidence로
  재확인, 새 Runtime Candidate 열지 않음).
- 이 Evidence가 확인하는 것은 정확히 C의 정의와 일치한다: "Runtime"
  이라는 이름/Concept 자체는 Kernel Design Principles(KP-1, "Kernel은
  Component가 아니라 Responsibility") 하에서 미래에 그런 책임이
  실제로 관찰될 때를 대비한 **상위 어휘로만** 남아 있고, 지금까지
  관찰된 실제 실행 책임은 전부 더 좁은 이름(Execution Host,
  Multi-Task, Workflow Adapter, Engine Adapter)으로 이미 개별
  Accept됐다.
- **판정**: 지금까지의 실제 Decision Chain 및 실행 Evidence와 가장
  정합적이다.

---

## 5. ADC-02 Recommendation

**이 문서는 ADC-02를 결정하지 않는다.** 아래는 §4 비교에 근거한
권고이며, 실제 상태 변경은 별도 RFC → ADC → ADR 절차를 통해서만
유효하다.

- 현재까지 축적된 모든 Evidence(문서 조사 `GOVERNANCE-REVIEW-0006`,
  실행 Evidence `RFC-0028`/`ADC-0013`, 실제 구현 부재 `§2.5`)는 **C
  (상위 개념으로만 유지, 독립 구현 Component로 미확정)** 방향을
  일관되게 가리킨다.
- **A(독립 Component로 확정)**는 Evidence 부족으로 권고하지 않는다 —
  넓은 정의(Workflow 참조·Multi-Task 배분)를 필요로 한 사례가 여전히
  없다.
- **B(개념 자체 제거)**는 "영구히 불필요"를 확정할 만큼 강한 근거가
  없고, `RFC-0028` 스스로 미래 재검토 가능성을 열어 뒀으므로 지금
  권고하지 않는다.
- **재검토 조건**(변경 없음, `ADC-0008`이 이미 정의): (1) "Core
  Component 검토" 원문 확보, 또는 (2) 넓은 정의의 Runtime 미결정으로
  인한 반복 관찰(서로 다른 독립 계기 3건 이상) 축적 — 이번 조사에서도
  둘 다 충족되지 않았다(§3).
- **이 조사 자체가 ADC-02 상태를 바꿀 근거를 새로 만들지 않는다** —
  `GOVERNANCE-REVIEW-0006`의 결론("Open 유지가 타당하다")과 방향이
  같다.

---

## 6. Architecture/Contract 변경 여부

- **Architecture Change**: 없음 — `docs/decisions/adc/ADC.md`의
  ADC-02 상태(Open, NOW)를 이 문서가 변경하지 않는다.
- **Contract Change**: 없음.
- **Kernel Impact**: 없음(직접) — 기존 Decision Chain(`ADC-0008`,
  `ADC-0013`, `ADC-0014`, `ADR-0004`, `RFC-0028`)을 재인용해
  대조했을 뿐, 새 Concept·Component를 제안하지 않았다.
- **Production Code**: 무수정(READ-ONLY Review).

---

## 7. Branch/PR 상태

- **Branch**: `claude/jarvis-governance-v2-sqqg8w` (origin/main과
  fast-forward 상태로 병합 확인, 이 문서 추가 외 diff 없음).
- **PR**: 미생성 — `CLAUDE.md` PR Creation Criteria "PR 불필요:
  READ-ONLY Audit, main에 반영할 diff가 없는 브랜치"에 해당하지
  않는다(이 문서 자체가 신규 파일이므로 diff는 있음)만, 성격상
  READ-ONLY Governance Review이며 Architecture/Contract를 변경하지
  않으므로 PR 필수 기준에는 해당하지 않는다. 사용자 승인 시 커밋만
  진행하고 PR 생성 여부는 별도 확인한다.
- **Validation**: `pytest hqs/development/mvp/tests/ -q` → 186
  passed, 6 skipped. `pytest projects/multi-agent-handoff-mvp-v1/tests/ -q`
  → 7 passed. 정적 grep으로 Production 내 Runtime 독립 구현 부재 확인.

## Self Review

- Evidence만 사용했는가 — **Pass**. 기존 ADC/RFC/ADR/Governance
  Review 문서와 실제 코드 grep, pytest 실행 결과만 인용했다. 새
  실험을 만들지 않았다.
- 새로운 Architecture를 설계했는가 — **아니오**.
- 미래 기능을 가정해 필요성을 만들어냈는가 — **아니오**(§3, §4 B/C
  판정이 모두 "지금 관찰된 것"에만 근거).
- Evidence 없는 주장을 명시했는가 — **Pass**(§3, "Evidence 없음"
  명시).
- ADC-02의 범위를 넘어 ADC-09/ADC-10 등을 결정했는가 — **아니오**
  (§3에서 범위 밖으로 명시, 재판단하지 않음).
- `docs/decisions/adc/ADC.md`를 수정했는가 — **아니오**.
- Production Code를 변경했는가 — **아니오**.
- 결과를 Evidence → Evaluation → Recommendation 순서로 작성했는가 —
  **Pass**(§2 → §4 → §5).

---

Architecture Change: 없음(ADC-02 상태 Open·NOW 유지, 이 문서가 변경하지 않음)
Contract Change: 없음
Production Code Change: 없음
Tests: `pytest hqs/development/mvp/tests/ -q` — 186 passed, 6 skipped. `pytest projects/multi-agent-handoff-mvp-v1/tests/ -q` — 7 passed.
E2E: 해당 없음(신규 실행 없음, 기존 Evidence 문서 인용)
RFC: 없음(이 문서가 개설하지 않음, §5에서 기존 재검토 조건만 재확인)
ADC: 없음(ADC-02는 Open·NOW 그대로, 이 문서가 갱신하지 않음)
ADR: 없음
PR: 미생성(사용자 승인 대기)
Next Implementation Candidate: 없음 — 재검토 조건(§5) 미충족 확인이 이번 결론
