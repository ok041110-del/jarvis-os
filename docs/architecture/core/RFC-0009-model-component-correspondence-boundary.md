# RFC-0009: Model 축과 Component 축의 대응 관계 — Boundary (ADC-01 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (ADC-01 Governance 우선순위 재평가 후속)
**대상**: `docs/03_adc/ADC.md` ADC-01("Model 축과 Component 축의 대응
관계") — Kernel Baseline에 등재된 이래 전용 RFC가 작성된 적 없는 항목
**Evidence**: `docs/03_adc/ADC.md` ADC-01,
`docs/01_architecture/BASELINE.md` §10,
`docs/02_rfc/RFC-0001-kernel-boundary.md`,
`docs/core/execution-layer/ADC-0004-execution-result-consumer.md`,
`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`,
`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`

> 본 RFC는 Model 축과 Component 축의 대응 관계를 결정하지 않는다.
> 새 Architecture를 설계하지 않는다. 새 실험을 하지 않는다. 이 RFC는
> ADC-01이 지금까지 저장소 안에서 실제로 판단된 적이 있는지 확인하고,
> 판단에 필요한 양측 근거를 있는 그대로 정리하며, 그 근거가 지금
> 판단을 가능하게 하는지만 질문한다. ADC-02(Runtime 존폐)는 재조사
> 하지 않는다 — `RFC-0008`·`ADC-0008`의 결론(Not Accepted)을 기존
> 결정으로만 인용한다.

## 0. 이 RFC가 열린 이유

ADC-01(Model 축과 Component 축의 대응 관계)은 `docs/03_adc/ADC.md`에
Open·우선순위 NEXT로 등재되어 있으나, 전용 RFC가 한 번도 작성된
적이 없다. 이 항목은 저장소 안에서 반복적으로 **인용만** 되어왔다 —
`docs/02_rfc/RFC-0001-kernel-boundary.md`는 "Task Dispatcher/Registry의
경계 정의에 선행 필요"라고 언급했고,
`docs/core/execution-layer/ADC-0004-execution-result-consumer.md`
Q3은 Execution Result Consumer Candidate C(Execution Layer 자신의
내부 처리)가 "ADC-01·ADC-02가 여전히 Open"에 막혀 있다고 확인했다.
`docs/architecture/core/RFC-0008-runtime-existence-boundary.md`는 이
공동 Blocking Evidence를 인지했으나, 우선순위(ADC-02=NOW, ADC-01=NEXT)
를 근거로 ADC-02만 다루고 ADC-01은 범위 밖에 남겼다
(`RFC-0008` §Out of Scope). `ADC-0008-runtime-existence-boundary.md`도
같은 제약을 명시했다.

ADC-02가 `RFC-0008` → `ADC-0008`로 이미 조사를 마쳤고(Not Accepted,
재조사하지 않음), Execution Result Consumer를 막고 있는 두 원인 중
아직 한 번도 다뤄지지 않은 나머지 하나가 ADC-01이다. 이 RFC는 그
다음 절차로서, 같은 종류의 Boundary Question을 연다.

## 1. Problem Statement

Kernel Boundary 설계는 "책임을 Model로 분류하는 축"과 "그 책임을
구현하는 Component로 분류하는 축" 두 가지 서로 다른 분류 체계를
동시에 언급해 왔으나, 이 둘이 정확히 어떻게 대응하는지는 결정된 바
없다. `ADC.md`는 이를 "Execution/Communication/Memory 3개 Model 축"과
"Scheduler/Engine Gateway/Registry/Communication/Memory/Policy 6개
Component 축"으로 표현한다.

## 2. Evidence Summary

| 축 | 근거 | 원문 실재 여부 |
|---|---|---|
| **Component 축 6개**(Scheduler/Engine Gateway/Registry/Communication/Memory/Policy) | `BASELINE.md` §10 Out of Scope: *"Component Design (Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)"* — Frozen Baseline 원문에 정확히 이 6개 이름이 그대로 존재하며, `ADC-0002-kernel-definition.md`·`RFC-0005-kernel-logical-reference-architecture.md`·`ADC-0005-kernel-logical-reference-architecture.md`·`ADR-0002-core-to-kernel-terminology-unification.md` 등 최소 5개 문서가 동일한 목록을 반복 인용한다 | **실재** — Frozen Baseline 원문, 반복 인용됨 |
| **Model 축 3개**(Execution/Communication/Memory) | `docs/03_adc/ADC.md` ADC-01 한 줄 진술: *"Execution/Communication/Memory 3개 Model 축 제안"*이 유일한 출처다. 전수 검색(`docs/`, `development-hq/`, `archive/`, git 이력 포함) 결과 이 3개를 "Model 축"으로 명명하거나 정의·근거를 부연한 문서는 이 한 줄 외에 **없다**. `docs/02_rfc/RFC-0001-kernel-boundary.md`와 `docs/governance/adc/ADC-0001.md`도 ADC-01을 이름으로만 인용할 뿐, "Model 축"의 정의를 부연하지 않는다 | **원문 부재** — 결론 문구 하나만 존재 |
| ADC-01의 Blocking 사실 | `ADC-0004-execution-result-consumer.md` Q3: *"Execution Layer 자신의 내부 처리... Kernel Module 4는... 내부 구조... ADC-01·ADC-02가 여전히 Open"* — Execution Result Consumer 판단이 실제로 막힌 최초 관찰 사례(ADC-02와 공동 원인) | 관찰 1건(반복 아님) |
| ADC-02와의 선례 | `RFC-0008-runtime-existence-boundary.md`·`ADC-0008-runtime-existence-boundary.md`: Runtime 존폐(ADC-02)는 "유지" 근거(원문 실재, 그러나 스스로 유보 명시)와 "대체" 근거("Core Component 검토", 결론만 남고 원문 부재)의 비대칭 때문에 **Not Accepted**로 종결됐다 — 새 Evidence·반복 관찰 없이는 재판단하지 않는다(기존 결정으로만 인용, 이 RFC는 재조사하지 않는다) | 기존 결정 인용만 |

## 3. Pattern

인용된 문서에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- Component 축 6개는 Frozen Baseline §10에 원문이 실재하고, 5개 이상
  문서가 동일한 목록을 그대로 재인용해 왔다 — 저장소 안에서 가장
  안정적으로 반복된 목록 중 하나다.
- Model 축 3개는 `ADC.md`의 결론 문구 하나만 존재하며, 그 문구가
  무엇을 근거로 "Execution/Communication/Memory"라는 3개 항목을
  선택했는지 설명하는 문서가 어디에도 없다.
- 이 비대칭은 `RFC-0008`이 ADC-02(Runtime 존폐)에서 발견한 것과
  **같은 종류의 구조**다 — 한쪽은 원문이 실재하고, 다른 쪽은 결론만
  남아 있다. 다만 이번엔 방향이 다르다: ADC-02에서는 "유지"(원문
  실재, 유보 명시) 대 "대체"(원문 부재)였고, ADC-01에서는 "Component
  축"(원문 실재, Frozen)이 한쪽이고 "Model 축"(원문 부재)이 다른
  쪽이며, 게다가 이 둘은 서로 대립하는 두 후보가 아니라 **대응
  관계가 요구되는 두 분류 체계**라는 점에서 질문의 형태 자체가
  ADC-02와 다르다.
- ADC-01은 `ADC-0004-execution-result-consumer.md`가 남긴 관찰 1건
  외에 반복 관찰이 없다 — ADC-02가 Not Accepted로 종결될 때 근거로
  쓴 "부족한 Evidence" 기준(`ADC-0008` §부족한 Evidence)과 같은 수준의
  공백이 ADC-01에도 존재한다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Kernel Concept Model의 Model 축 3개(Execution/Communication/Memory)와
Component 축 6개(Scheduler/Engine Gateway/Registry/Communication/
Memory/Policy)는 어떻게 대응하는가?

이 질문은 ADC-02와 달리 "둘 중 하나를 고르는" 형태가 아니라 "관계를
정의하는" 형태다. 현재 확보된 근거로 알 수 있는 것은 다음뿐이다.

| 관찰 | 근거 |
|---|---|
| "Communication"과 "Memory"는 두 축 모두에 동일한 이름으로 등장한다 | ADC-01 원문(§2 표) — 대응이 1:1일 가능성을 시사하나, 확정 근거는 아니다 |
| Component 축의 나머지 4개(Scheduler/Engine Gateway/Registry/Policy)는 Model 축 3개 어디에도 이름이 겹치지 않는다 | 동일 |
| "Execution"이 Model 축에만 있고 Component 축엔 이름이 없다 | 동일 — Kernel Module "Execution Layer"(`ADC-0001-core-baseline.md` Module 4, Accept)와 같은 단어이나, 동일 개념인지는 확인된 바 없다 |

이 RFC는 위 관찰이 실제 대응 관계를 뜻하는지 판단하지 않는다 —
이름이 같다는 사실과 개념이 같다는 것은 다르다(`RFC-0008`이 "유지"
근거를 "현상 유지 기술"과 "확정 근거"로 구분했던 것과 같은 종류의
경계).

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Model 축과 Component 축의 실제 대응 관계 결정.
- "Model 축"이라는 분류 자체를 재정의하거나 대체하는 것.
- ADC-02(Runtime 존폐)의 재조사 — `RFC-0008`·`ADC-0008`의 Not
  Accepted 결정은 기존 결정으로만 인용한다.
- Kernel Component Architecture의 실제 설계(Scheduler/Engine
  Gateway/Registry/Memory/Policy 등) — `BASELINE.md` §10 Out of
  Scope 그대로.
- Execution Result Consumer의 재판단 —
  `ADC-0004-execution-result-consumer.md`의 Not Accepted 상태는 이
  RFC의 결과가 나오기 전까지 그대로 유지된다.
- "Execution"(Model 축)과 "Execution Layer"(Kernel Module,
  `ADC-0001-core-baseline.md` Module 4 Accept)가 같은 개념인지 여부 —
  이 RFC는 이름이 같다는 관찰만 기록하고 동일성을 판단하지 않는다.
- 새로운 실험.

## Non-goals

- 이 RFC는 ADC-01을 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `ADC.md`, `BASELINE.md` §10,
  `RFC-0001-kernel-boundary.md`, `ADC-0004`(execution-layer),
  `RFC-0008`·`ADC-0008`에 이미 기록된 내용만 인용했다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 Model 축이나 Component 축을 설계·재정의하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.
- 이 RFC는 ADC-02를 재조사하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §2의 비대칭(Component 축은 원문 실재, Model 축은 원문 부재)을
   근거로 지금 판단이 가능한지, 아니면 "Model 축" 3개 항목의 원래
   근거를 확인할 방법이 없는 한 판단할 수 없는지 — `ADC-0008`이
   ADC-02에 적용한 것과 같은 방식의 판단.
2. 판단이 가능하다면 §4의 관찰(이름이 겹치는 "Communication"·
   "Memory", 겹치지 않는 나머지) 중 무엇을 실제 대응 관계의 근거로
   채택할지.
3. 판단이 불가능하다면, 부족한 Evidence가 무엇인지만 기록하고
   억지로 결론을 내리지 않는다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC.md`, `BASELINE.md` §10,
  `RFC-0001-kernel-boundary.md`, `ADC-0004`(execution-layer),
  `RFC-0008`·`ADC-0008`에 실제로 기록된 내용만 인용했다. 새 실험은
  하지 않았다.
- ADC-02를 재조사했는가 — **아니오**. `RFC-0008`·`ADC-0008`의 Not
  Accepted 결론을 기존 결정으로만 인용했다(§0, §Out of Scope).
- Model 축과 Component 축의 대응 관계를 임의로 결정했는가 —
  **아니오**. §4는 관찰(이름이 겹치는 항목)만 나열했고, 그것이
  실제 대응을 뜻하는지는 판단하지 않았다.
- 새 Architecture를 설계했는가 — **아니오**.
- "Execution"과 "Execution Layer"가 같다고 단정했는가 — **아니오**.
  이름이 같다는 관찰만 기록했다(§4, §Out of Scope).
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(대응 관계 결정, Model 축 재정의, ADC-02 재조사,
  Kernel Component Architecture 설계, Consumer 재판단, Execution
  동일성 판단, 새 실험)을 다뤘는가 — **아니오**.
