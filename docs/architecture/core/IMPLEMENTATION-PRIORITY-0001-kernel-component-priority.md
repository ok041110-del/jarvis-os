# IMPLEMENTATION-PRIORITY-0001: Kernel Component Implementation Priority (Phase 8)

**문서 성격**: Priority/Planning 문서. **RFC/ADC/ADR이 아니다.** 새
Component를 확정하거나 구현하지 않는다. `docs/03_adc/ADC.md`의 어떤
항목도 상태를 바꾸지 않는다. `docs/01_architecture/BASELINE.md` §10
(Kernel Component Architecture, Out of Scope)을 우회하지 않는다.
**이번 작업에서 코드는 한 줄도 작성하지 않는다.**

**선행 문서**: `VALIDATION-0002`(Phase 6 — Baseline 경계가 실제
코드/Evidence에서 지켜지는지 검증), `COMPONENT-CANDIDATE-0001`(Phase 7
— 8개 Component 후보의 Evidence 상태를 개별 판정, 전부 ADC 채택 기준
미충족으로 결론). 이 문서는 그 두 문서의 결론을 **재조사하지 않고
그대로 인용**하며, "지금 설계할 근거가 없다"는 Phase 7의 결론 위에서
**"조건이 충족될 때 어떤 순서로 다뤄야 하는가"**만 정리한다.

**입력 자료**: `VALIDATION-0002`, `COMPONENT-CANDIDATE-0001`,
`docs/01_architecture/BASELINE.md` §7·§10~§16, `docs/03_adc/ADC.md`
(ADC-01~12 전체), `core/execution_layer/**`(테스트).

---

## 0. 실행한 검증

```
python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q
```

이 문서는 새 코드를 만들지 않으므로 새 테스트도 만들지 않는다. 위
명령은 Phase 6·7이 이미 확인한 회귀 없음 상태를 재확인하기 위해서만
재실행한다.

---

## 1. 전제 — Phase 7이 이미 답한 것은 다시 묻지 않는다

`COMPONENT-CANDIDATE-0001` §3(ADC 채택 기준 대조)이 8개 후보 전부
"두 조건(지금 결정 안 하면 진행 불가 / 지연 비용 매우 큼) 미충족 →
RFC 불필요"로 이미 결론 냈다. 이 문서는 그 결론을 뒤집지 않는다 —
**"지금 Component를 만들어야 하는가"는 이미 "아니오"로 답해졌다.**

이번 작업이 새로 답하는 질문은 다르다: **"만약 각 후보가 나중에
실제로 다뤄진다면, 그 순서와 각 후보에 필요한 선행 작업(Contract
정의 vs 그냥 대기)은 무엇인가."** 이는 실행이 아니라 계획이다.

### 사용자 지시 원칙과 기존 판정의 대응

| 원칙 | 기존 판정과의 대응 |
|---|---|
| Execution은 재설계하지 않는다 | `COMPONENT-CANDIDATE-0001` C-4: 이미 Accept·구현·검증 완료 — 이 문서의 후보 목록에서 제외 |
| Agent/Capability는 Kernel Component로 만들지 않는다 | `COMPONENT-CANDIDATE-0001` C-3: §7이 이미 HQ 책임으로 확정 — Kernel Component 후보 자체가 아님, 이 문서의 우선순위 목록에서 제외(N/A) |
| Memory는 Non-Goal이므로 구현하지 않는다 | `BASELINE.md` §14.6 N-4(Non-Goal 확정) — Defer(C) |
| External Data/Acquisition은 Concept 미확정이므로 바로 구현하지 않는다 | `COMPONENT-CANDIDATE-0001` C-8: Concept Model에 분류 위치 자체가 없음 — Defer(C), Contract 단계에도 못 미침 |
| Registry/Lifecycle은 성급히 구현하지 않는다 | `VALIDATION-0002` §Q4: 책임 귀속은 확정, 구현은 ADC-01·02 해소 전까지 미착수 — Defer(C) |
| Kernel Context/Task-Workflow/Event-State 선후관계는 Evidence로 판단 | §2에서 판단 |

---

## 2. Component별 판단 (사용자 제시 7개 후보 + Execution 제외 사유)

| # | Component | Architecture 책임 확정? | 실제 구현 필요성 발생? | 다른 Component를 Block하는가? | Contract 선(先) 확정 필요? | Evidence 충분? | 지금 구현 시 Drift 위험 |
|---|---|---|---|---|---|---|---|
| 1 | Kernel Context | **예**(§13~15, ADR-0003~0005) | 아니오 — Execution Layer가 독자 `str` 파이프라인으로 완결(§2-A) | 아니오(어떤 후보도 C-1 완성을 기다리지 않는다) | **아니오 — 이미 완료됨**(PR-1~4, G-1~7) | 충분(Governance 절차로 확정) | **있음** — §10이 아직 Out of Scope이므로, 지금 구현하면 그 자체가 §10 위반(Drift) |
| 2 | Task/Workflow | 부분(Task Flow만 §6) | 아니오 — 하드코딩 순차 호출로 MVP-0001~0048·Investment 14건 전부 완주, Stop Trigger 0회 | 아니오 | **예** — ADC-09(Workflow 그래프 의미론) 해소 전엔 Contract 자체를 쓸 수 없음 | 불충분 — ADC-09 미해소 | 있음 — ADC-09 답 없이 구현하면 도메인 지식(SDLC 등)을 OS가 흡수할 위험(ADC-09 본문 그대로) |
| 3 | Registry/Lifecycle | **예**(§7, Kernel 책임) | 아니오 — Development HQ·Investment HQ 둘 다 비-live로 정상 동작(`INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001` §2-3) | 아니오(직접 Block 사례 없음 — 두 HQ 모두 등록 없이 동작) | **예, 그러나 ADC-01·02 해소가 선행**이라 지금은 Contract 자체를 쓸 근거가 없음 | 불충분 — ADC-01(Model↔Component)·ADC-02(Runtime 존폐) 둘 다 Open | 있음 — Runtime 존재 여부(ADC-02) 없이 Lifecycle 전환 모델을 설계하면 나중에 뒤집힐 위험 큼 |
| 4 | Event/State | 부분(Event Flow만 §6) | 아니오 — Multi-HQ 시나리오 자체가 한 번도 실행된 적 없음(모든 Dogfooding이 단일 HQ 내부) | 아니오 | **예, 그러나 3개 ADC 동시 해소 필요**(ADC-04·05·08) | 가장 불충분 — 8개 후보 중 미결 ADC 최다 | 있음 — 배달 보장 수준(ADC-05·08) 없이 설계하면 재작업 확률 최고 |
| 5 | External Data/Acquisition | **아니오** — Concept Model(§6) 10개 분류 어디에도 없음 | 실제 책임 경계로 4회 관찰됐으나(`AGG-DATA-BOUNDARY-REPRODUCTION-0001`) 1개 project 계열에 국한 | 아니오 | **Contract 이전 — Concept 자체가 없어 무엇을 계약할지 정의 불가** | 매우 불충분 — 표본 1개 계열, 표준화 시도 없음 | 있음 — 미정의 Concept 위에 Contract를 쓰면 그 Concept 자체를 이 문서가 사실상 새로 만드는 것(권한 밖) |
| 6 | Memory | Non-Goal로 **확정**(§14.6 N-4) | 아니오 — in-memory 변수 하나로 14건+10건(MVP+Investment) 전부 충분 | 아니오 | 불필요(Non-Goal, 재검토 조건 자체가 없음) | N/A(구현 안 하는 것이 Architecture 준수) | 있음 — 만들 이유가 없는데 만들면 그 자체가 Drift |
| 7 | Agent/Capability | **예**(§7, HQ 책임 — Kernel Component 아님) | **N/A — Kernel Component 후보가 아니므로 우선순위 대상 자체가 아님** | — | — | — | — |
| — | Execution | **예**(§16.2, ADR-0002) | **N/A — 이미 구현·검증 완료, 재설계 대상 아님** | — | — | — | — |

---

## 3. 결과

### A. 지금 구현해야 하는 Component

**없음.**

이유: (1) 사용자 지시 자체가 이번 작업에서 코드를 구현하지 않는다고
명시했고, (2) 그와 무관하게 §10(Kernel Component Architecture, Out of
Scope)이 여전히 유효하며 어떤 후보도 이를 뒤집을 ADC 채택 기준(§1)을
충족하지 못했다(`COMPONENT-CANDIDATE-0001` §3 재확인). Kernel Context
조차 Contract는 완료됐지만 **구현 착수 조건은 §10 해제**이지 Contract
완성이 아니다 — 두 조건을 혼동하지 않는다.

### B. Contract부터 정의해야 하는 Component

**Task/Workflow.** 단, "지금 Contract를 쓴다"가 아니라 **"이 후보가
다뤄질 차례가 오면, 구현보다 Contract(ADC-09 해소 결과 반영)가
먼저"**라는 순서를 의미한다. 근거:
- 8개 후보 중 유일하게 **이미 NOW 우선순위로 등재된 단일 ADC**
  (ADC-09)만 해소되면 Contract 작업이 열리는 구조다 — Registry(2개
  ADC), Event/State(3개 ADC)보다 선행조건이 적다.
- Task Flow의 절반(§6 Concept 관계)은 이미 정의돼 있어, ADC-09가
  풀리면 나머지 절반(그래프 의미론)만 채우면 된다 — 가장 적은 추가
  Governance로 Contract에 도달하는 경로다.

Registry/Lifecycle과 Event/State도 궁극적으로 "Contract-first"
대상이지만, 그 전에 해소해야 할 ADC가 각각 2개·3개로 더 많고, 그중
ADC-02(Runtime 존폐)는 `ADC-0008`이 이미 "결정할 재료 자체가 없다"고
판정한 항목이라 Task/Workflow보다 훨씬 멀다 — 그래서 이 둘은 B가
아니라 C로 분류한다(§C).

### C. Defer해야 하는 Component

| Component | Defer 사유 | 재검토 조건 |
|---|---|---|
| Registry/Lifecycle | ADC-01·ADC-02 동시 미해소, 두 HQ 모두 비-live로 정상 동작 중이라 압력 없음 | ADC-01·ADC-02 **둘 다** 해소될 때(`VALIDATION-0002` §Q4) |
| Event/State | ADC-04·05·08 3개 미해소, Multi-HQ 시나리오 자체가 아직 실행된 적 없음 | 실제 Multi-HQ 실행이 관찰되거나 위 3개 ADC 중 다수가 해소될 때 |
| External Data/Acquisition | Concept Model에 분류 위치가 아예 없음(ADC-03 선행 필요), Evidence가 1개 project 계열(ETF/Dividend Stock)뿐 | ADC-03 해소 **및** 다른 project 계열(예: Investment HQ 4번째 Dogfooding, 다른 HQ)에서 재현될 때 |
| Memory | Non-Goal로 이미 확정(§14.6 N-4), 재검토 트리거 자체가 정의돼 있지 않음 | 정의된 조건 없음 — in-memory 방식이 실패하는 실제 사례가 나타나야 함(지금까지 0건) |

### D. 구현 순서 (조건이 충족됐을 때만, 지금 착수하지 않음)

```
1순위: Kernel Context
   — Contract 이미 완료(PR-1~4, G-1~7). 유일한 선행조건은
     §10(Kernel Component Architecture Out of Scope) 해제뿐.
     해제 자체가 별도 RFC 대상(ADC 채택 기준 미충족으로 지금 열리지
     않음, §1).

2순위: Task/Workflow
   — ADC-09(NOW, 이미 추적 중) 해소 → Contract 정의 → 구현 검토.
     Kernel Context 다음으로 선행조건이 적다(ADC 1개).

3순위: Registry/Lifecycle
   — ADC-01 + ADC-02(둘 다 NEXT/NOW이나 ADC-02는 `ADC-0008`이 "결정
     재료 없음"으로 판정한 상태) 둘 다 해소 → Contract 정의 → 구현
     검토.

4순위: Event/State
   — ADC-04(LATER)·05(NEXT)·08(NEXT) 다수 해소 + 실제 Multi-HQ
     시나리오 실증 → Contract 정의 → 구현 검토. 선행조건이 가장 많다.

순위 밖(트리거 없이는 재검토 자체를 하지 않음): External Data/
Acquisition(ADC-03 해소 + Evidence 확장이 둘 다 필요 — 순수 ADC 해소
만으로는 부족), Memory(Non-Goal, 정의된 트리거 없음).

대상 아님: Agent/Capability(HQ 책임, Kernel Component 후보 아님),
Execution(이미 구현·검증 완료).
```

이 순서는 **"먼저 결정될 가능성이 높은 순"**이지 **"먼저 만들라"**는
지시가 아니다 — 4개 모두 지금 그 어떤 착수도 하지 않는다.

---

## 4. Architecture/Contract 변경 여부

**없음.** `BASELINE.md`, `docs/03_adc/ADC.md`, `core/`,
`development-hq/` 어느 것도 수정하지 않았다. 새 Component/Contract를
확정하지 않았다 — Kernel Context의 Contract는 이미 §13~15에 존재하는
것을 인용했을 뿐 이 문서가 새로 쓰지 않았다.

## 5. Governance 영향

**없음.** 새 RFC/ADC/ADR을 열지 않는다. `docs/03_adc/ADC.md`의
ADC-01~12는 전부 기존 상태(Open, 각자의 기존 우선순위) 그대로
유지한다. 이 문서는 어느 것도 재조사하지 않았다 — 우선순위 판단에
필요한 만큼만 기존 상태를 인용했다.

이 문서가 향후 실제로 여는 것을 권고하는 유일한 트랙은 **"어떤 ADC가
먼저 해소되면 어떤 Component 작업이 열리는가"**라는 **순서 정보**뿐이며,
그 자체로 새 Governance 행위를 유발하지 않는다.

## 6. 다음 Implementation 작업

**없음 — 이번 Phase의 결론은 "지금은 없다"이다.** 다음 실제 작업은
아래 중 하나가 **실제로** 발생했을 때만 시작된다(선제적으로 만들지
않는다):

1. ADC-09가 Governance 절차(RFC → ADC → ADR)로 실제 해소됨 →
   Task/Workflow Contract 정의 작업 시작.
2. §10(Kernel Component Architecture)을 여는 새 RFC가 실제로
   승인됨 → Kernel Context Component 구현 착수(1순위).
3. ADC-01·ADC-02가 함께 해소됨 → Registry/Lifecycle Contract 정의
   작업 시작.
4. Investment HQ 4번째 Dogfooding 또는 다른 HQ에서 External Data/
   Acquisition 재현이 관찰됨 → ADC-03 우선순위 재검토를 사용자에게
   건의(이 문서가 직접 건의를 실행하지 않는다).

## 7. Evidence / Tests

새 Evidence 생성 없음 — `VALIDATION-0002`, `COMPONENT-CANDIDATE-0001`,
`docs/03_adc/ADC.md`(ADC-01~12)만 인용했다.

```
python3 -m pytest development-hq/mvp/tests/ core/execution_layer -q
```
(회귀 재확인용, 결과는 §Tests 실행 로그에 기록)

## Files

`docs/architecture/core/IMPLEMENTATION-PRIORITY-0001-kernel-component-priority.md`
(이 문서, 신규). 그 외 어떤 파일도 수정하지 않았다.

## Commit / Branch

Branch: `claude/jarvis-os-documentation-drift-9lymtn`. 이 문서만 커밋
대상이다.

---

## Architecture Governance Review

- 새로운 Architecture/Layer/Component/Concept이 추가되었는가 —
  **아니오**. 우선순위만 정리했다.
- Baseline 문서를 변경했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**.
- ADR이 필요한가 — **아니오**.
- 코드를 작성했는가 — **아니오**.

## Self Review

- §10 Out of Scope를 우회했는가 — **아니오**. "지금 만들어야 하는
  Component"는 명시적으로 "없음"으로 답했다(§3-A).
- ADC-01~12를 재조사했는가 — **아니오**. 우선순위·Defer 사유에 필요한
  만큼만 기존 상태(Open/우선순위)를 인용했다.
- Registry/Lifecycle을 "성급히" 구현 대상으로 올렸는가 — **아니오**.
  ADC-01·02 동시 해소를 선행조건으로 명시하고 C(Defer)로 분류했다.
- Memory/External Data를 구현 대상으로 올렸는가 — **아니오**. 둘 다
  Defer, 순위 밖으로 명시했다.
- Agent/Capability를 Kernel Component 후보로 다뤘는가 — **아니오**.
  N/A로 명시하고 우선순위 목록에서 제외했다.
- Kernel Context/Task-Workflow/Event-State의 선후관계를 Evidence로
  근거지었는가 — **예**(§3-D, 선행조건 개수·기존 ADC 우선순위·`ADC-0008`
  판정을 근거로 순서 확정).
