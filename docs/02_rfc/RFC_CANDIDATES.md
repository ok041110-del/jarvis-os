# RFC Candidates

이 문서는 "언젠가 검토할 아이디어" 목록이 아니다. **이미 논의가 이루어졌고, MVP-0001 검증 이후 Baseline에 반영될 가능성이 높은 Architecture 후보**를 관리한다.

각 항목은 정식 RFC로 상정되기 전 단계이며, 다음 조건이 충족되면 RFC로 승격된다.

- Development HQ MVP-0001 구현이 완료된다.
- 아래 각 항목이 실제 구현 과정에서 필요성이 재확인된다(또는 Kernel Extraction Candidate 관찰과 결합된다).

RFC로 승격되면 이 문서에서 제거되고 `docs/02_rfc/RFC-XXXX.md`로 정식 등록되며, 이후 통상 절차(RFC → ADC → ADR → Baseline Update)를 따른다.

---

## Candidate 1. Capability의 재분류 (Metadata → Contract)

**Status**: Pending RFC · **Adoption Likelihood**: High (post-MVP)

**현재 Baseline 상태**: Concept Model은 Capability를 `Metadata`로 분류한다 (`docs/01_architecture/BASELINE.md` 6장).

**후보 내용**: Capability를 "Contract"라는 개념으로 재정의.

**RFC 승격 시 다뤄야 할 것**: "Contract"가 기존 10개 분류 중 하나의 재명명인지, 새로운 분류 축인지 확정.

---

## Candidate 2. Agent의 재정의 ("Logical Worker")

**Status**: Pending RFC · **Adoption Likelihood**: High (post-MVP)

**현재 Baseline 상태**: Concept Model은 Agent를 `Entity`로 분류하고 "Task를 실행하는 단위, HQ에 소속"으로 정의한다.

**후보 내용**: Agent를 "Logical Worker"로 명명.

**RFC 승격 시 다뤄야 할 것**: 이 명명이 Concept Model 표를 대체하는지, 보조 설명으로 추가되는지 확정.

---

## Candidate 3. Engine의 재정의 ("Execution Resource") 및 Agent와의 분리

**Status**: Pending RFC · **Adoption Likelihood**: High (post-MVP)

**현재 Baseline 상태**: Concept Model은 Engine을 `Interface`(Engine Port/Adapter)로 분류한다.

**후보 내용**: Engine을 "Execution Resource"로 재정의하고, Agent(Logical Worker)와 개념적으로 분리.

**RFC 승격 시 다뤄야 할 것**: Interface 분류와 "Resource" 성격의 관계 정리.

---

## Candidate 4. Engine의 다대다 공유 관계

**Status**: Pending RFC · **Adoption Likelihood**: Medium-High (ADC-01, ADC-07과 연동 필요)

**후보 내용**: 동일한 Engine을 여러 Agent가 사용할 수 있다.

**RFC 승격 시 다뤄야 할 것**: Kernel 수준 Engine Gateway/Routing 설계에 직접 영향. 여러 Agent가 동일 Engine을 두고 경합할 때의 자원 배분·우선순위 문제는 `docs/03_adc/ADC.md`의 ADC-07(Token 예산 이중 소속)과 결합하여 다뤄야 한다.

---

## Candidate 5. Capability의 다대다 제공 관계

**Status**: Pending RFC · **Adoption Likelihood**: Medium-High (ADC-01과 연동 필요)

**후보 내용**: 하나의 Capability를 하나 이상의 Agent가 제공할 수 있다.

**RFC 승격 시 다뤄야 할 것**: 여러 Agent가 동일 Capability를 제공할 때 선택 기준은 Registry/Scheduler의 책임 영역이며, `docs/03_adc/ADC.md`의 ADC-01(Model↔Component 대응 관계)이 먼저 해결되어야 답할 수 있다.

---

## 현재 단계에서의 취급

MVP-0001 구현에는 위 5개 후보를 반영하지 않는다. `development-hq/STRUCTURE.md`, `development-hq/IMPLEMENTATION_RULES.md`는 현재 Baseline 정의(Capability=Metadata, Agent=Entity, Engine=Interface)만 사용한다.

Claude Code는 이 문서를 참고용으로만 취급하며, 이 문서의 어떤 내용도 구현에 반영하지 않는다.
