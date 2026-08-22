# ADC-0012: RFC-0012(Dispatch Component)의 Governance 진행 가능 여부 — DEFER

## 목적

`docs/architecture/core/RFC-0012-dispatch-component-boundary.md`(커밋
`9ff6a36` 기준)가 연 Boundary Question 자체를 판단하기 전에, **이
RFC를 지금 Architecture Governance 대상으로 진행할 수 있는가**를
먼저 판단한다. RFC-0012 §15-1이 이미 이 판단을 후속 ADC로 명시적으로
위임했다.

근거는 RFC-0012, `RFC-0010`/`ADC-0010`, `RFC-0011`/`ADC-0011`,
`COMPONENT-CANDIDATE-0001-kernel-component-architecture-review.md`,
`CLOSURE-0001-architecture-research.md`, `PHASE9-CLOSURE-0001.md`,
`PHASE5-KERNEL-CANDIDATE-0001.md`, `PHASE6`(`projects/kernel-parallel-execution-prototype/EVIDENCE.md`),
`PHASE7-KERNEL-COMPONENT-ARCHITECTURE-0001.md`로만 한정한다. 새로운
Evidence·실험·Trigger를 만들지 않는다.

### 이 ADC가 답하지 않는 것

- RFC-0012의 Boundary Question("Dispatch 책임을 지금 설계 착수
  대상으로 삼을 수 있는가") 그 자체 — 이 ADC가 A(ACCEPT)로 판단하지
  않는 한 다루지 않는다.
- Dispatch Component의 Architecture 내용(책임/Interface/위치) — RFC-0012
  §3~§13의 어떤 제안도 이 ADC는 확정하지 않는다.
- `ADC-0010`의 C1~C6, `ADC-0011`의 Boundary Question 재조사 — 상태만
  인용한다.
- `COMPONENT-CANDIDATE-0001`의 8개 후보 재조사.
- `PHASE9-CLOSURE-0001`의 Engine Adapter Defer 재론.
- `CLOSURE-0001` 자체의 수정 — 이 문서는 `CLOSURE-0001`을 수정하지
  않는다.
- 새 RFC/Trigger 생성.

이 ADC가 판단하는 것은 오직 하나다: **RFC-0012를 지금 Governance
절차(ADC → ADR)로 진행할 수 있는가, 아니면 대기해야 하는가?**

---

## 1. `CLOSURE-0001`이 실제로 규정한 Closure 범위와 재개 Trigger

**Closure 범위**: `CLOSURE-0001` §7.3은 "Architecture Research
종료 선언 **가능** 여부: 가능하다"고 판정했으나, 그 직전 문장에서
명시한다 — *"이 문서는 종료를 선언하지 않는다 — 가능 여부만
판정한다. 선언 자체는 이 문서의 권한 밖이다."* 즉 `CLOSURE-0001`은
Closure를 **선언한 적이 없다** — "선언 가능하다"는 판정만 남겼다.
같은 §7.3 표는 그 선언이 뜻하지 않는 것을 명시한다: *"미결 항목이
없다(Architecture 16 / Documentation 9 / 관찰 대기 11+)"*, *"앞으로
열리지 않는다"*.

**재개 Trigger**(§5, 새로 만들지 않고 인용):
- Rule A(RT Trigger, 후보별): *"2. Engine Gateway | Trigger: Engine
  수 ≥ 2 | 현재: 미충족"*.
- Rule B: *"동일 Tag Observation 3회 → RFC"* — `docs/01_mvp/MVP-00XX-observation.md`
  계열의 **Tag 부여 Observation**을 전제로 한다(§4.3의 5개 구간 분류가
  이 체계를 그대로 사용).
- Kernel Component Architecture(§10) 전체 재개 조건: §5.3 표 *"§5의
  6개 근거 해소 → Kernel Component Architecture (§10)"* — 이 6개
  근거는 `GOVERNANCE-REVIEW-0001` §5 원문이며, `CLOSURE-0001` §4.1이
  6개 중 4개(2·4·5·6번)를 **관찰 부족**으로, 그중 5번을 정확히
  *"Engine Gateway Trigger(Engine 수 ≥ 2) 미충족"*으로 분류했다.
- §5.4 결론: *"위 조건 전부가 '관찰'이다. 문서 작업만으로 충족되는
  Architecture Trigger는 하나도 없다."*

**`ADC-0010` C1 자신의 재검토 조건**(RFC-0012의 직접 근거): *"C1(Kernel
Engine Port/Adapter): Kernel Component Architecture 설계 착수(현재
§10 Out of Scope) — 이 자체가 여러 선행 조건(Kernel Module Defer
3건, ADC-01·02, Engine 수 ≥2 등)에 걸려 있다."* — "Engine 수 ≥2"는
이 목록의 **한 항목("등"으로 목록이 닫히지 않음)**이며, 다른 항목
(Kernel Module 3건 Defer, ADC-01·02 Open)도 함께 나열되어 있다.

**확인**: 세 문서(`CLOSURE-0001` §5, `GOVERNANCE-REVIEW-0001` §5,
`ADC-0010` C1)가 서로 다른 층위에서 각각 "Engine 수 ≥2"를 언급하지만,
어느 문서도 이를 유일한 조건으로 지정하지 않았다 — 항상 다른 관찰
조건과 병기된다.

---

## 2. RFC-0012가 `RFC-0010`/`RFC-0011`의 종료된 질문을 재개하는지

**문자 그대로는 아니다.** RFC-0012는 `ADC-0010`의 C1~C6 중 어느 것도
다시 선택하지 않고(§0, §13에서 확인), `ADC-0011`의 Boundary
Question("별도 실행 위치를 공식 Concept으로 둘 수 있는가")에도 답하지
않는다 — RFC-0012가 제안하는 Dispatch Component는 애초에 "Kernel/HQ
밖의 제3 위치"(`RFC-0011`의 대상)가 아니라 **C1(Kernel Engine
Port/Adapter)의 부분집합**으로 스스로를 위치시킨다(RFC-0012 §0).

**그러나 실질적으로는 같은 활동을 시작하려 한다.** `ADC-0010`이 C1을
Not Accepted로 판단한 이유는 *"지금 이 후보를 caller로 Accept하면,
§10이 Out of Scope로 명시한 Component(Engine Gateway)의 설계에
착수하는 것과 같은 효과를 가진다"*는 것이었다. RFC-0012 §1
Motivation은 스스로 *"`ADC-0010` C1이 '설계 선행 필요'라고 남긴
지점을... 좁은 범위(Dispatch)로 한정해 여는 것"*이라고 명시한다 —
이는 범위만 좁힌 **Kernel Component 설계 착수**이며, `ADC-0010`이
경계로 삼은 바로 그 활동("§10 Component 설계 착수와 같은 효과")과
같은 종류다.

**판정**: 질문(Boundary Question)은 새롭지만, 그 질문을 여는 행위
자체가 `ADC-0010`이 미룬 활동을 재개하는 것과 같은 범주에 속한다.

---

## 3. Phase 6 Evidence가 기존 Trigger와 동일한 의미인지, 별개의 새로운 Evidence인지

**별개의 새로운 Evidence이지만, 기존에 명시된 어떤 Trigger에도
해당하지 않는다.**

- `PHASE6` `EVIDENCE.md`의 `engine_caller.py`는 `ENGINE_CLI = "claude"`를
  그대로 사용한다 — Dev HQ·Investment HQ·Phase 6 Prototype 3개
  맥락 전부 **동일한 단일 Engine(Claude Code)**을 호출했다. Engine의
  **수**는 3개 맥락 전부 1로 동일하다 — "Engine 수 ≥2" Trigger가
  요구하는 사실(서로 다른 두 번째 Engine의 실제 등장)과 무관하다.
- Phase 6 Evidence의 실체는 "동일 기법(`ThreadPoolExecutor`+`call_engine()`)의
  3번째 독립 재현"이다(`PHASE5-KERNEL-CANDIDATE-0001.md` "반복성"·"재사용성"
  기준, `PHASE6` `EVIDENCE.md` Conclusion). 이것은 Rule B(*"동일 Tag
  Observation 3회 → RFC"*)와 표면적으로 유사해 보이지만, Rule B는
  `docs/01_mvp/MVP-00XX-observation.md` 계열의 **Tag가 부여된
  Observation**을 전제로 한다 — 실측 결과 `docs/research/` 하위
  Phase 문서 어디에도 `"Tag:"` 필드가 없다(grep 0건). Phase 4~7 문서는
  이 Tag 체계에 등록된 적이 없으므로, Rule B가 요구하는 형식적 조건을
  충족하지 못한다.
- `CLOSURE-0001` §5.3의 다른 재개 조건("실제 Engine 호출 1회 관찰")도
  살펴봤으나, 이는 Kernel Context Model 영역(Context Boundary/Engine별
  Renderer/HQ 통합)의 재검토 조건이지 Kernel Component Architecture(§10)
  또는 C1의 재검토 조건이 아니다 — 적용 대상이 다르다.

**결론**: Phase 6 Evidence는 실재하는 새 Observation이지만,
`CLOSURE-0001`이나 `ADC-0010`이 C1/§10 재개를 위해 명시한 **어떤
기존 Trigger 문구와도 일치하지 않는다.** 이 Evidence를 근거로 새
Trigger를 만들어 대응시키는 것은 이 ADC의 권한 밖이다(제약: "새로운
Trigger를 임의로 만들지 않는다").

---

## 4. Trigger 미충족 상태에서 RFC-0012를 여는 것이 기존 Governance와 충돌하는가

**RFC를 "여는 것"(Proposed 상태로 존재하는 것) 자체는 충돌하지
않는다.** `RFC-0010`·`RFC-0011` 자신도 Runtime Observation Trigger
없이 열렸다 — 두 RFC 모두 "선행 문서(`ADC-0005` Next Step, `ADC-0010`
§부족한 Evidence 6번)가 이미 후속 절차를 요구했다"는 절차적 근거로
열렸을 뿐, "Engine 수 ≥2" 같은 관찰 Trigger를 충족한 적이 없다.
`docs/decisions/rfc/README.md`도 RFC를 "결정이 아니라 검토 대상"으로
정의한다 — RFC 자체가 Baseline을 바꾸지 않는 한, 개설 자체를 위해
Runtime Trigger가 항상 필요한 것은 아니라는 것이 기존 선례다.

**그러나 RFC-0012가 실제로 하려는 것(Governance 절차를 통해 Dispatch
Component 설계에 착수)까지 "지금 진행 가능"으로 판단하는 것은
충돌한다.** `CLOSURE-0001` §5.4가 *"문서 작업만으로 충족되는
Architecture Trigger는 하나도 없다"*고 명시했고, §6.2는 현재 위치를
*"Implementation 미착수"*로, §6.3은 다음 순서를 *"Documentation
정리(병행 가능) → Implementation → Observation 축적 → Trigger 충족 시
Architecture 재개 → §5의 6개 근거 해소 시 Kernel Component
Architecture"*로 명시적으로 정리했다. RFC-0012가 목표하는
"Dispatch Component 설계 착수"는 이 순서의 마지막 두 단계(Trigger
충족 → Kernel Component Architecture)에 해당하며, 그 사이 단계
(Observation 축적)를 건너뛰는 것이 된다.

**판정**: RFC 문서의 **존재**(이미 작성·커밋된 상태)는 선례와
충돌하지 않는다. 그러나 이를 근거로 **ADC가 Dispatch Component
설계를 Accept**하는 것은 `CLOSURE-0001`이 정리한 절차 순서와
직접 충돌한다.

---

## 5. RFC-0012를 진행할 경우 기존 Closure를 우회하는 것인지

**우회 여지가 있다.** `CLOSURE-0001`은 Closure를 공식 선언하지
않았으므로(§1) "우회"라는 표현이 문자 그대로 성립하려면 먼저
선언된 것이 있어야 하지만, `CLOSURE-0001`이 정리한 **절차 순서**(§6.3)와
**Trigger 원칙**(§5.4: 관찰만 인정)은 실질적인 Governance 규범으로
이미 기록되어 있다. RFC-0012를 근거로 곧바로 ADC에서 Dispatch
Component Accept를 시도한다면, 이는 그 순서와 원칙을 **건너뛰는
효과**를 가진다 — `CLOSURE-0001`을 명시적으로 수정하거나 반박하지
않으면서 그 결론과 다른 실질적 결과에 도달하는 것이므로, "우회"에
해당한다고 판단한다.

**대비**: RFC-0012 자체(Proposed 상태로 질문만 여는 것)는 §4에서
확인했듯 우회가 아니다. 우회가 발생하는 지점은 "RFC의 존재"가 아니라
"그 RFC를 근거로 한 ADC의 Accept 시도"다.

---

## Decision

**B. DEFER**

RFC-0012의 Governance 진행(Boundary Question에 대한 ADC Accept,
그에 따른 Dispatch Component 설계 착수)을 **지금 진행하지 않는다.**
RFC-0012 문서 자체(Proposed, 이미 커밋된 상태)는 유지한다 — 삭제·수정
대상이 아니다.

### 근거(요약)

1. `CLOSURE-0001`이 명시한 Kernel Component Architecture(§10) 재개
   조건("§5의 6개 근거 해소", 그중 4개가 관찰 부족)이 여전히
   미충족이다(§1).
2. `ADC-0010` C1이 명시한 선행 조건(Kernel Module Defer 3건 여전히
   Defer, ADC-01·02 여전히 Open, Engine 수 ≥2 여전히 미충족) 중
   어느 것도 이번 판단 시점에 새로 충족되지 않았다(§1, §3).
3. Phase 6 Evidence는 실재하는 새 Observation이지만, 그 성격(동일
   Engine의 3번째 독립 재현)이 기존에 명시된 어느 Trigger 문구와도
   일치하지 않는다 — Rule B는 Tag 체계 미등록으로 형식 요건
   미충족, "Engine 수 ≥2"는 Engine이 여전히 1개이므로 미충족(§3).
4. RFC를 여는 것 자체는 `RFC-0010`/`RFC-0011` 선례와 일치하지만,
   이를 근거로 ADC가 Accept까지 나아가는 것은 `CLOSURE-0001`이 정리한
   절차 순서(Observation 축적 → Trigger 충족 → Architecture 재개)를
   건너뛰는 것이다(§4, §5).

### 필요한 향후 Trigger/Evidence(새로 만들지 않고, 기존 문서가 이미
명시한 것만 나열)

- `ADC-0010` C1의 선행 조건 3종 중 최소 하나의 실제 충족: (a) 두
  번째 실제 Engine 등장, (b) `ADC-0008`(ADC-02, Runtime 존폐)의
  재검토 조건 충족, (c) Kernel Module 3건(Workflow/Memory/Event
  Bus) Defer 사유("반복 관찰 없음") 해소.
- 또는 `CLOSURE-0001` §5의 6개 근거 중 나머지(2·4·6번, 전부 "관찰
  부족"으로 분류됨) 중 하나 이상의 실제 충족.
- Rule B를 원용하려면, Phase 4~7 Evidence를 `docs/01_mvp/` Tag
  체계에 정식으로 등록하는 것이 선행되어야 한다(이 ADC는 그 등록을
  제안하지 않는다 — 별도 판단 대상).

이 조건들은 전부 **관찰**이다 — 추가 문서 작성만으로는 충족되지
않는다(`CLOSURE-0001` §5.4).

---

## Risks

- DEFER는 "Dispatch Component가 영원히 불가능하다"는 뜻이 아니다 —
  `ADC-0008`·`ADC-0009`·`ADC-0010`·`ADC-0011`과 동일한 구분이다.
  위 Trigger가 실제로 충족되면 재검토 대상이 된다.
- `CLOSURE-0001` 자신이 "Engine 수 ≥2" 같은 Trigger를 오래된
  RT-0001 Candidate 목록(Task Dispatcher/Engine Gateway/Agent
  Registry/Context 전달)에서 가져온 것이며, 이 목록이 Dispatch
  Component처럼 이후 새로 식별된 후보에도 그대로 적용되는 것이
  최선인지는 이 ADC가 재론하지 않는다 — 기존 문서가 정의한 대로만
  적용했다.
- RFC-0012가 이미 커밋·push된 상태로 남는 것은, 향후 이 문서를
  아무 맥락 없이 발견한 사람이 "Proposed 상태의 미결 질문"과
  "Governance가 실제로 진행 중인 절차"를 혼동할 위험이 있다 — 이
  Decision 문서가 그 상태를 명시적으로 기록해 둔다.

**재검토 조건**: 위 "필요한 향후 Trigger/Evidence" 중 하나라도 실제로
충족되면, 이 Decision은 기존 Governance 절차(RFC → ADC → ADR)를
통해 재검토 대상이 된다.

## Next Step

**No ADR Required** — "DEFER"는 Boundary를 이동시키지 않으며 Baseline
Update를 전제하지 않는다. RFC-0012는 Proposed 상태로 유지되며,
`ADC-0010`/`ADC-0011`/`CLOSURE-0001`의 기존 판정은 갱신하지 않는다.
RFC-0012 §15의 나머지 항목(§14 Open Question, Engine Adapter 관계
등)은 이 DEFER 판정으로 인해 현재 판단 대상에서 제외된다 — Trigger
충족 후 재개 시 함께 다룬다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**. Dispatch
  Component는 이 ADC로 Accept되지 않았다.
- Baseline 문서를 변경했는가 — **아니오**.
- `CLOSURE-0001`을 수정했는가 — **아니오**. 절차 순서와 Trigger
  정의를 그대로 인용만 했다.
- ADR이 필요한가 — **아니오**.
- 코드/`core/`/Migration을 수행했는가 — **아니오**.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0012, `RFC-0010`/`ADC-0010`,
  `RFC-0011`/`ADC-0011`, `COMPONENT-CANDIDATE-0001`, `CLOSURE-0001`,
  `PHASE9-CLOSURE-0001`, Phase 5/6/7 문서에 실제로 기록된 내용만
  인용했다. Tag 체계 미등록 확인은 `grep -rl "Tag:" docs/research/`
  실측(0건)이다.
- "Phase 6 Evidence = Trigger 충족"으로 간주했는가 — **아니오**.
  §3에서 명시적으로 구분했다: 새 Observation이지만 기존 Trigger
  문구와 불일치.
- "Engine 수 ≥2"를 임의로 재해석했는가 — **아니오**. Engine 수가
  3개 맥락 전부 1(Claude Code)임을 코드(`ENGINE_CLI = "claude"`)로
  확인했을 뿐, 기준 자체를 바꾸지 않았다.
- 기존 Closure를 수정했는가 — **아니오**. `CLOSURE-0001` 파일 자체는
  건드리지 않았다.
- 새로운 Trigger를 임의로 만들었는가 — **아니오**. §Decision "필요한
  향후 Trigger/Evidence"는 전부 `ADC-0010`·`CLOSURE-0001`이 이미
  명시한 조건을 나열한 것이다.
- 기술적 Architecture 타당성과 Governance 진행 가능성을 분리했는가 —
  **Pass**. 이 ADC는 Dispatch Component의 기술적 타당성(RFC-0012
  §1~§13)을 전혀 판단하지 않았다 — Governance 절차 진행 가능 여부만
  판단했다.
- RFC-0012의 Architecture 내용을 확정했는가 — **아니오**.
- 억지로 결론을 내렸는가 — **아니오**. DEFER는 Not Accepted 계열
  판정과 동일한 형식(재검토 조건 명시, 영구 배제 아님)이다.
- ADR을 작성했는가 — **아니오**.
