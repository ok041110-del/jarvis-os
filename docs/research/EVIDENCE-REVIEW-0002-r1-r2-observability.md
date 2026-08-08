# EVIDENCE-REVIEW-0002: R-1 / R-2 관찰 가능성 검토

**문서 성격**: **Research 문서. Governance 문서가 아니다.**
**목적**: 미관찰 상태인 R-1·R-2를 **기존 Architecture와 Governance
범위 안에서 관찰할 수 있는지**만 검토한다.

이 문서는 Execution Result Contract를 설계하지 않는다. 세 후보 중
어느 것도 선택하지 않는다. Artifact schema·Component·Layer·Gateway·
Adapter·Registry·Scheduler·Runtime·Routing을 만들지 않는다.
Development HQ를 수정하지 않는다. **실제 Engine을 실행하지 않는다.**
RFC·ADC·ADR을 작성하지 않는다. Baseline을 수정하지 않는다. 새
Governance Trigger를 만들지 않는다.

**관점은 하나다 — "무엇으로 결정할 것인가"가 아니라 "무엇을 관찰해야
하는가".**

---

# 1. Evidence Correction

**앞으로 이 세 값을 구분해 쓴다.**

| 항목 | 값 | 출처 |
|---|---|---|
| **실제 Engine 실험** | **3회** | `GOVERNANCE-REVIEW-0001` 133행: *"(ENGINE-INTEGRATION-0001~0003, **실제 Claude Code Engine 3회 실험**)"* |
| **코드 경로의 실제 Engine 호출** | **0회** | `development-hq/mvp/engine.py:15-17` — `call_engine()`은 규칙 기반 응답을 반환한다 |
| **Execution Result 결합 방식 관찰** | **Unknown** | ENGINE-INTEGRATION-0001·0002·0003 각각의 Unknowns |

> **"Engine 호출 0회"는 코드 경로에 대한 진술이며, 실험 횟수가
> 아니다.**

---

# 2. R-1 Observation Gap

**R-1을 Engine Input / Engine Execution / Engine Output 세 축으로
분리한다. 새 필드나 Model을 정의하지 않는다** — 이 세 축은
ENGINE-INTEGRATION 문서들이 이미 사용한 절 구분(`Inputs` /
`Timeline`·`Repository Interaction` / `Outputs`)을 그대로 쓴 것이다.

## 2.1 Engine Input

| | 내용 |
|---|---|
| **이미 관찰된 것** | Prompt Specification 전체 텍스트가 **별도 변환·재구성 없이 그대로** Engine 입력으로 사용됨. 세 실험이 **동일한 텍스트**를 사용했고 *"입력 텍스트는 세 실험 내내 한 글자도 바꾸지 않았다"*(0003 Experiment) |
| | Engine이 입력 텍스트만으로 작업하지 않고 **저장소를 능동 탐색**함(0001 Inputs) |
| **미관찰인 것** | **Model Request / Execution Handle / Execution State를 입력으로 준 경우.** 0001이 명시: *"Model Request나 Execution Handle/Execution State가 실제로 Claude Code에 입력된 적은 없다 — 이번 실험은 **Prompt Specification 한 단계만** 시험했다"* |

## 2.2 Engine Execution

| | 내용 |
|---|---|
| **이미 관찰된 것** | Timeline(3회), Repository Interaction — Grep/탐색적 검색 2/3회, 실패 범주 5종(Spec-Repository Staleness Mismatch 3/3, 모듈·상대 import 경로 오류 1, Self-Referential Recursion 1, Spec Internal Duplication 1), 시스템 수준 실패(Timeout/Permission/Tool Error/Context Limit) **0회** |
| **미관찰인 것** | 뒤 세 Artifact를 입력으로 했을 때의 실행 양상 — §2.1의 미관찰에 종속된다 |

## 2.3 Engine Output

| | 내용 |
|---|---|
| **이미 관찰된 것** | 신규 파일 생성 1/3, 다중 파일 수정(2개 이상) 1/3, **Diff/Patch 관찰 가능 2/3**, 진단 로그, pytest 결과, git status 확인, 구조화된 텍스트 보고 (0001 Outputs, 0003 Pattern Check) |
| | 즉 **출력은 이질적 복수 산출물이었다** |
| **미관찰인 것** | 뒤 세 Artifact 입력 시의 출력 형태 |

## 2.4 R-1의 정확한 정의

> **R-1 = "Prompt Specification 이후의 세 Artifact(Model Request /
> Execution Handle / Execution State)를 Engine 입력으로 주었을 때의
> 입력·실행·출력 형태."**
>
> 세 실험은 체인의 **한 단계**만 시험했고, 나머지 세 단계는 시험된
> 적이 없다. 이는 실험이 미흡했던 것이 아니라 **0001이 스스로
> 범위로 선언하고 Unknowns에 남긴 것**이다.

---

# 3. R-2 Observation Gap

## 3.1 현황

| | 내용 |
|---|---|
| **이미 관찰된 것** | 출력이 **여러 개별 산출물**이라는 사실(§2.3). 세 실험에서 산출물 **구성이 서로 달랐다**는 사실 — 0001은 신규 파일, 0002·0003은 파일 수정·diff·진단 로그·텍스트 보고 |
| | 그 차이가 **입력 조건 차이**(기존 파일 유무)에서 왔다는 사실 — 0003이 seed 파일을 미리 만들어 다중 파일 리팩터링을 유도했다 |
| **미관찰인 것** | *"여러 개별 산출물을 하나의 Execution Result로 묶는 방식"* — 세 실험 모두 Unknown |

## 3.2 R-2의 문언 성격 — 반드시 구분해야 한다

세 문서의 원문은 다음과 같다.

> *"여러 개별 산출물을 하나의 Execution Result로 묶는 방식이
> **무엇이어야 하는지** — Unknown이며 이 문서는 답하지 않는다."*

**"무엇이어야 하는지"는 규범적 질문이다.** 관찰은 그것을 **닫지
못한다.**

> **관찰이 할 수 있는 것은 후보를 좁히는 것뿐이며, 마지막 선택은
> 관찰이 아니라 판단(ADC)의 몫이다.**

이 구분이 없으면 "관찰만 더 하면 Contract가 나온다"는 잘못된 기대가
생긴다.

---

# 4. Observation Feasibility

## 4.1 기존 실험 조건 — 세 실험이 실제로 사용한 것

**0001·0003의 `Experiment` 절에서 그대로 추출했다. 새로 만들지
않았다.**

| # | 조건 | 원문 근거 |
|---|---|---|
| C-1 | **입력은 기존 Dogfooding 산출물의 전체 텍스트를 그대로 사용한다 — 새로 만들지 않는다** | 0001: *"…이미 생성되어 있던 Artifact를 그대로 사용했다 — **새로 만들지 않았다**"* |
| C-2 | Claude Code Agent 도구, **fresh session**(부모 맥락 미상속), 1회 실행 | 0001 실행 환경 |
| C-3 | **isolation worktree**에서 실행하고, 메인 저장소가 변경되지 않았음을 `git status --porcelain`으로 사후 확인 | 0001·0003 Repository 상태 |
| C-4 | 기록 항목: Timeline / Inputs / Outputs / Observable State / Failure / Artifact Mapping / Unknowns (+0002·0003: Repository Interaction / Comparison / Pattern Check) | 세 문서의 절 구조 |

## 4.2 R-1이 요구하는 변경 — **입력 Artifact 교체 하나뿐**

그리고 **그 입력이 이미 존재한다.**

| R-1의 미관찰 입력 | 저장소 내 실물 |
|---|---|
| Model Request | `core/execution_layer/mvp_0003/dogfooding/output/real_issue.model_request.md` |
| Execution Handle | `core/execution_layer/mvp_0004/dogfooding/output/real_issue.execution_handle.md` |
| Execution State | `core/execution_layer/mvp_0005/dogfooding/output/real_issue.execution_state.md` |

**세 파일 모두 세 실험이 사용한 Prompt Specification과 동일한
`real_issue` 체인의 Dogfooding 산출물이며, 이미 커밋되어 있다.**

> **따라서 C-1이 그대로 적용된다** — *"이미 생성되어 있던 Artifact를
> 그대로 사용한다"*는 조건이 세 입력에 대해서도 성립한다.

## 4.3 판정

| 질문 | 판정 |
|---|---|
| **기존 조건으로 관찰 가능한가** | **가능하다.** C-1~C-4를 그대로 쓰고 입력만 교체한다 |
| **추가 조건이 필요한가** | **불필요하다.** 새 실험 조건을 발명할 필요가 없다 |
| **Architecture 변경이 필요한가** | **불필요하다.** 기존 Artifact를 입력으로 주고 관찰만 하는 데 어떤 결정도 필요하지 않다 |
| **Development HQ 수정이 필요한가** | **불필요하다.** C-3이 worktree 격리와 메인 저장소 불변을 3회 실증했다 |

## 4.4 질문 4의 다섯 후보 — 각각 판정

| 후보 | 판정 | 근거 |
|---|---|---|
| 새로운 Architecture 결정 | **불필요** | §4.3 |
| 기존 Implementation 수정 | **불필요** | §4.3. 입력이 이미 존재하고 실험은 격리된다 |
| **기존 Engine 실험의 재실행** | **불충분** | 같은 입력(Prompt Specification)을 네 번째로 반복해도 R-1은 관찰되지 않는다. 세 실험 모두 같은 텍스트를 썼다 |
| **새로운 Research Experiment** | **필요** | 단 **새 조건 발명이 아니라 C-1~C-4 + 입력 교체**다 |
| 아무것도 하지 않고 대기 | **불가** | 대기로는 관찰이 생기지 않는다. 세 실험이 이미 그 사실을 세 번 기록했다 |

---

# 5. R-1 → R-2 관계 (질문 3)

## 5.1 R-1이 관찰되면 R-2를 판단할 수 있는가

> ## **아니다.**

두 가지 이유가 각각 독립적으로 성립한다.

1. **R-2는 규범적 질문이다**(§3.2). 관찰이 닫을 수 있는 종류가 아니다.
2. **R-1은 "출력이 무엇인가"를 늘리지만, 세 후보가 요구하는 관찰에
   직접 답하지 않는다.** `GOVERNANCE-REVIEW-0002` §2.1이 정리한
   요구 관찰과 대조하면 다음과 같다.

| 후보 | 요구되는 관찰 | R-1이 직접 답하는가 |
|---|---|---|
| 단일 불투명 결과 | 산출물이 하나의 텍스트로 환원 가능한가 | **아니다** — 출력을 더 볼 뿐 환원 가능성은 별개다 |
| 산출물 목록 | 항목의 종류·경계가 안정적인가 | **아니다** — 안정성은 **반복** 관찰의 성질이다 |
| 결과 Reference | 참조 대상을 어디에 두는가 | **아니다** — 저장 위치는 Memory 영역이며 **Defer** 상태다 |

## 5.2 R-2를 좁히려면 어떤 기존 Evidence가 더 필요한가

**후보를 선택하지 않는다. 필요한 Evidence의 종류만 기록한다.**

| 후보 | 좁히는 데 필요한 것 | 기존 문서에 방법이 있는가 |
|---|---|---|
| 산출물 목록 | 동일 조건 반복 시 출력 구성이 몇 회 중 몇 회 동일한가 | **있다** — ENGINE-INTEGRATION-0003의 **Pattern Check**(Observation Count 표)가 이미 그 형식을 제공한다 |
| 단일 불투명 결과 | 이질적 산출물이 손실 없이 한 텍스트로 표현 가능한지 | 기존 문서에 방법이 기록되어 있지 않다 |
| 결과 Reference | Memory Defer의 해소 | **관찰로 해소되지 않는다** — ADC 판단 사항이다 |

> **세 후보 중 하나(Reference)는 관찰이 아니라 Defer 해소가 선행되어야
> 하며, 이 문서는 그것을 요청하지 않는다.**

---

# 6. Rule A / Rule B 확인

**기존 Rule만 확인한다. 새 Trigger를 만들지 않는다.**

| Rule | 상태 |
|---|---|
| **Rule A** (RT Trigger 충족 → RFC) | **미충족.** RT-0001의 4개 Trigger 중 Engine 수 ≥ 2 / HQ 수 ≥ 2 / Context 경로 ≥ 2 전부 미충족. Task Dispatcher는 ADC-0004에서 재판단 완료 |
| **Rule B** (동일 Tag OBS 3회 → RFC) | **Execution Result 주제에 대해 미충족.** ENGINE-INTEGRATION 세 건은 `docs/research/` 소재이며 `Tag` 필드가 없다 |

## 6.1 별건 사실 — 기록만 한다

**Tag `Other`를 가진 OBS 3건(OBS-0004·0005·0006, 전부 Status
`Open`)이 존재하여 Rule B의 수치 조건이 문언상 충족된다.**

그러나 그 셋의 주제는 Validation Capability(0004·0005)와 Planning/
Design Capability 구조화(0006)이며 **Execution Result와 무관하다.**

> **따라서 이 사실을 Architecture Re-entry의 근거로 사용하지
> 않는다.** 기록만 한다.

---

# 7. Governance State

> ## **Hold for Evidence**

| 후보 | 판정 |
|---|---|
| Continue Implementation | **아니다** — Contract를 결정할 수 없으므로 코드를 이어 쓰면 후보 하나를 암묵 선택하게 된다(`IMPL-STOP-0001`) |
| **Hold for Evidence** | **그렇다** |
| Re-enter Architecture Governance | **아니다** — Rule A·B 미충족(§6), ADC 채택 기준 미충족(`GOVERNANCE-REVIEW-0002` §3) |

## 7.1 다만 Hold의 성격을 정정한다

**이번 검토가 바꾼 것은 Hold의 내용이다.**

| 이전 이해 | 이번 검토 결과 |
|---|---|
| 관찰이 생기려면 무언가가 구현·실행되어야 한다 | **필요한 관찰은 기존 실험 조건으로 가능하다**(§4.3) |
| Development HQ 수정 가부가 선행 결정이다 | **R-1 관찰에는 Development HQ 수정이 불필요하다**(§4.3) |
| Hold = 대기 | **Hold ≠ 대기.** 대기로는 관찰이 생기지 않는다(§4.4) |

---

# 8. Final Recommendation — 다음 단계의 **최소 작업**

**Architecture를 미리 설계하지 않는다. 실험을 실행하지 않는다.**

## 8.1 최소 작업

> **ENGINE-INTEGRATION 시리즈의 네 번째 실험 — 기존 조건 C-1~C-4를
> 그대로 사용하고 입력 Artifact만 교체하는 관찰 1회.**

## 8.2 질문 5가 요구한 항목

| 항목 | 내용 |
|---|---|
| **실험이 필요한 이유** | R-1은 세 실험이 스스로 범위 밖으로 선언한 영역이며(§2.1), 반복 재실행으로는 관찰되지 않는다(§4.4). 대기로도 생기지 않는다 |
| **관찰 대상** | Model Request / Execution Handle / Execution State 세 Artifact를 Engine 입력으로 주었을 때의 **Input·Execution·Output 형태**. **어느 것을 먼저 시험할지는 이 문서가 정하지 않는다** — 체인 순서는 Prompt Specification → Model Request → Execution Handle → Execution State이며, 기존 실험 형식은 실험 1회당 입력 1개를 다뤘다 |
| **기존 조건** | C-1(기존 Dogfooding 산출물 그대로) / C-2(fresh session) / C-3(worktree 격리 + 메인 저장소 불변 사후 확인) / C-4(기록 항목). **입력 파일 3개가 이미 커밋되어 존재한다**(§4.2) |
| **좁혀지는 Open Question** | (a) **R-1 자체.** (b) `ADC-0003` 판단 4의 재검토 조건 중 **뒤 절** — *"그 호출에서 '매번 동일하게 앞에 놓이는 Context 구간'이 실측으로 확인되면"*. 앞 절은 이미 충족되었고 뒤 절이 미충족이다(`GOVERNANCE-REVIEW-0002` §4.4). **좁힌다이지 해소한다가 아니다** |

## 8.3 이 권고가 하지 않는 것

- 실험을 실행하지 않는다.
- 실험 설계를 확정하지 않는다 — 어느 입력을 먼저 쓸지, 몇 회 반복할지
  정하지 않았다.
- 실험 결과를 예측하지 않는다.
- R-2의 후보를 선택하지 않는다.
- Development HQ 수정 가부를 판단하지 않는다 — **R-1 관찰에는
  불필요하다는 사실만 확인했다**(§4.3).

---

## Self Review

- Execution Result Contract를 설계했는가 — **아니오**. §5.2는 후보별로
  **필요한 Evidence의 종류**만 적었고 어느 것도 선택하지 않았다.
- 단일 문자열 / 산출물 목록 / Reference 중 하나를 골랐는가 —
  **아니오**.
- 새 Artifact schema·Component·Layer를 만들었는가 — **아니오**.
- 새 필드나 Model을 정의했는가 — **아니오**. §2의 세 축은
  ENGINE-INTEGRATION 문서의 기존 절 구분을 그대로 사용했다.
- 새로운 실험 조건을 발명했는가 — **아니오**. C-1~C-4는 0001·0003의
  `Experiment` 절에서 추출했고, 필요한 입력 3개가 이미 저장소에
  존재함을 확인했다.
- 실제 Engine을 실행했는가 — **아니오**.
- Development HQ를 수정했는가 — **아니오**. 코드 변경 0건.
- RFC·ADC·ADR·Baseline·Governance Trigger를 만들거나 바꿨는가 —
  **아니오**.
- Rule B의 형식적 충족을 재진입 근거로 썼는가 — **아니오**. §6.1이
  주제 무관함을 명시하고 사용하지 않았다.
- "관찰하면 Contract가 나온다"고 기대하게 썼는가 — **아니오**. §3.2와
  §5.1이 R-2가 규범적 질문이며 관찰로 닫히지 않음을 명시했다.
- 결론을 미리 가정했는가 — **아니오**. §4.4의 다섯 후보를 개별
  판정했고, 그중 둘(재실행·대기)을 명시적으로 배제했다.
