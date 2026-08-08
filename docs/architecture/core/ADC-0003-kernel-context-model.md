# ADC-0003: Kernel Context Model 채택 판단 (RFC-0003 후속)

## 목적

`docs/architecture/core/RFC-0003-kernel-context-model.md`가 제안한
Phase K-1 ~ K-5를 **개별적으로** 판단한다. 일괄 승인하지 않는다.

근거는 RFC-0003, 그리고 그 RFC가 인용한 기존 문서·코드
(`docs/01_architecture/BASELINE.md` v1.1,
`docs/architecture/core/RFC-0002`·`ADC-0002`,
`docs/04_adr/ADR-0002`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`docs/core/execution-layer/MVP-0001~0005-*`,
`core/execution_layer/mvp_0001~0005/**`,
`docs/research/EVIDENCE-REVIEW-0001.md`,
`docs/01_mvp/MVP-0009-observation.md`,
`development-hq/mvp/project_intelligence.py`,
`development-hq/BOUNDARY.md`)에 실제로 기록된 사실로만 한정한다.
새로운 Evidence를 만들지 않는다. 실험을 추가하지 않는다.

각 판단의 Decision은 **Accept / Defer / Reject / Out of Authority**
중 하나다.

**판단의 기준선**: ADC-0002 판단 2b(4-Layer Context Model, **Defer**)는
이 ADC에서도 해제되지 않는다. 어떤 판단도 그 Defer를 우회하는 형태로
taxonomy를 확정해서는 안 된다 — 이 점을 각 판단에서 개별 확인한다.

---

## 판단 1. K-1 Context Domain Model 5개 요소 (RFC-0003 §2)

Kernel ADC-0001이 5개 Module을 개별 판단한 선례에 따라, 5개 요소의
근거를 개별 확인한 뒤 하나의 Decision을 낸다.

### Evidence (요소별)

| 요소 | 근거 확인 결과 |
|---|---|
| Context Segment | **기존 사실의 일반화.** Execution Layer 5개 Builder 전부가 입력 텍스트를 한 글자도 바꾸지 않고 고정 절만 덧붙였다(`ARTIFACT-STANDARD-v1.md` 공통 패턴 "Wrap, not rewrite"). MVP-0002는 9개 절의 **본문을 그대로 옮겨** 5개 절로 재배치했고(`_extract_section_body` → `RENDERING_MAP`), 그 보존을 `test_every_source_section_body_survives_verbatim`으로 검증했다(연구자가 소스에서 직접 확인). MVP-0009 `build_context_bundle()`은 8개 항목을 각각 독립적으로 만들었다. "이름 붙은 복수의 조각을 내용 변경 없이 다룬다"는 실천이 이미 존재한다. |
| Context Source | **기존 사실의 일반화.** `build_context_bundle()`의 `relevant_code`는 `context["source_code"]`와 `context["existing_workflow"]` 두 출처의 합집합이다(`project_intelligence.py:143-144`, 연구자가 소스에서 직접 확인). 출처가 복수라는 사실은 코드에 있다. 다만 Kernel이 Source를 **해석하지 않는다**는 제약은 신규이며, 그 근거는 `BASELINE.md` §7(도메인 내용은 Jarvis OS 책임 아님)과 `BOUNDARY.md`(Workflow 내용은 HQ 책임)다. |
| Context Identifier | **기존 사실의 재진술.** `request_id`/`created_at`(MVP-0003), `handle_id`/`submitted_at`(MVP-0004), `handle_id`/`state`/`changed_at`(MVP-0005)이 전부 호출자 주입이고, 5개 MVP 전체에서 `uuid.uuid4`/`datetime.now`/`time.time` 부재가 테스트로 확인되었다. "Kernel이 식별자를 스스로 만들지 않는다"는 KP-6의 재진술이다. |
| Context Metadata | **신규.** 다만 commitment가 거의 없다 — 이 Phase에서 필수 키를 하나도 정의하지 않았고, 제약 2(계층 분류 금지)·제약 3(Engine 종속 키 금지)은 각각 ADC-0002 판단 2b와 KP-5의 재확인일 뿐이다. |
| Context | **기존 사실의 일반화.** 5개 Artifact 전부가 생성 후 하류에서 변경되지 않음이 4건의 테스트로 확인되었다(`test_execution_request_itself_is_unchanged_by_rendering`, `test_prompt_specification_itself_is_unchanged_by_wrapping`, `test_model_request_itself_is_unchanged_by_wrapping`, `test_execution_handle_itself_is_unchanged_by_state_creation` — 연구자가 소스에서 직접 확인). MVP-0005는 상태 변화 시 기존 Artifact를 수정하지 않고 **새 Artifact를 만들었다.** "Context는 값이다"는 이 실천의 일반화다. |

### 검토한 반론 (기록)

- **"5개 요소를 정의하는 것 자체가 관찰되지 않은 구조를 미리 만드는
  것 아닌가"(ADC-0002 판단 2b가 Defer한 것과 같은 상황 아닌가)** —
  같지 않다. 판단 2b가 Defer한 것은 **특정 값의 분류 체계**
  (Immutable/Stable/Working/Ephemeral 4개)였고, 그것은 이 저장소에서
  한 번도 관찰된 적이 없었다. K-1의 5개 요소는 분류가 아니라
  **이미 코드에 존재하는 것들에 이름을 붙이는 것**이다 — 조각
  (MVP-0002·MVP-0009), 출처(MVP-0009), 식별자(MVP-0003~0005), 불변
  값(MVP-0001~0005)은 전부 실물이 있다. 새 taxonomy를 만들지 않는다.
- **Order Key를 Metadata에서 분리한 것이 과설계인가** — 아니다.
  분리하지 않으면 "무엇을 바꾸면 Context가 바뀌는가"를 말할 수 없고,
  그것은 KP-2(결정론)를 테스트 불가능하게 만든다. 분리 비용은 필드
  하나이며, 그 필드는 이미 MVP-0002에 `SOURCE_SECTIONS_IN_ORDER`라는
  고정 튜플 형태로 존재한다.
- **`BASELINE.md` §6 Context와의 용어 충돌** — 실재하는 문제이며
  RFC-0003 §2.8이 이를 기록했다. 그러나 §6의 Context는 "Task 실행 중에만
  유효한 State"라는 **한 줄 정의**이고 구성 요소를 말하지 않았다.
  K-1은 그 자리를 채우는 구체화이며 §6을 재정의하지 않는다. 이
  ADC는 §6의 문장을 바꾸지 않는다.

### Decision

**Accept** (5개 요소 전부. 단 아래 제약을 조건으로 한다.)

1. Segment에 **계층·안정성 분류 필드를 두지 않는다** — ADC-0002 판단
   2b Defer 유지.
2. Model에 **Engine 종속 요소를 두지 않는다**(role, token 수, cache
   key 등) — KP-5.
3. Kernel은 **Identifier·시각을 스스로 생성하지 않는다** — KP-6.
4. Kernel은 Content와 Source를 **해석하지 않는다** — `BASELINE.md`
   §7, `BOUNDARY.md`.

### Decision Rationale

5개 중 4개(Segment, Source, Identifier, Context)는 이미 구현·테스트로
존재하는 사실의 일반화이며, 채택해도 새로운 commitment가 발생하지
않는다. 유일한 신규 항목(Metadata)은 필수 키를 하나도 정의하지 않아
commitment가 사실상 비어 있다.

이 Accept는 Component를 만들지 않는다(KP-1). Model은 어휘이며, 그
어휘가 없으면 ADC-0002 판단 2a가 Accept한 4개 책임을 판단할 대상
자체가 존재하지 않는다 — 판단 2b의 Risks가 이미 기록한 공백이다.

### Risks

Model은 실제 Engine 호출 없이 채택된다. 실제 호출이 시작된 뒤
"Segment 단위가 너무 크다/작다", "Metadata에 필수 키가 필요하다"는
관찰이 나오면 이 Model은 확장 대상이 된다. 이 Accept는 "이 5개가
영구히 충분하다"가 아니라 "지금 있는 사실을 표현하는 데 이보다 적은
어휘로는 부족하다"는 판단이다.

### Next Step

**ADR Required** — Kernel이 관리하는 대상의 정의이므로 Baseline에
기록되어야 한다.

---

## 판단 1b. Context Identifier 파생 규칙 확정 (RFC-0003 §2.4 미결 항목)

### Evidence

- RFC-0003 §2.4는 파생 규칙(호출자 주입 / 내용 해시 / 그 외)을
  결정하지 않고 미결로 남겼다.
- 관찰된 사실은 **호출자 주입 하나뿐이다**(MVP-0003~0005). 내용
  해시로 식별자를 만든 사례는 이 저장소에 존재하지 않는다.
- 어떤 규칙이 필요한지는 Context를 재사용·비교하는 사례가 있어야
  드러나며, 그런 사례는 아직 없다.

### Decision

**Defer**

단, **"Kernel이 스스로 생성하지 않는다"는 제약만은 판단 1에서 이미
Accept되었다**(KP-6). Defer되는 것은 "그 값을 어떻게 만드는가"뿐이다.

### Decision Rationale

두 후보(주입/해시) 중 하나를 지금 고르면, 근거 없이 한쪽을 고정하는
것이 된다. 반면 고르지 않아도 상위 설계가 막히지 않는다 — 판단 1의
Model은 Identifier를 "값 하나"로만 규정하므로 어느 규칙이든 나중에
들어올 수 있다. `ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준 2개
("지금 결정하지 않으면 진행 불가" / "늦어질수록 되돌리는 비용이
커진다") 중 어느 것도 만족하지 않는다.

### Next Step

No ADR Required

---

## 판단 2. K-2 Context Builder의 4개 책임 (RFC-0003 §3)

4개 책임을 개별 확인한다.

### Evidence (책임별)

| 책임 | 근거 확인 결과 | 판정 |
|---|---|---|
| 수집(Collect) | **기존 사실.** MVP-0005~0008 네 건 모두 `collect_relevant_context()`가 정확히 1회, 항상 Planning 직전에 호출되었다(EVIDENCE-REVIEW-0001 "Context 전달 방식"). 수집이 한 지점에서 일어난다는 사실이 4회 반복 관찰되었다. "Source를 발견하지 않는다"는 제약은 Registry 책임을 침범하지 않기 위한 것으로, Kernel ADC-0001의 Registry Defer와 정합적이다. | Accept |
| 검증(Validate) | **기존 사실의 일반화.** MVP-0005는 `state`가 허용값 5개 중 하나인지만 검증하고 전이 규칙은 검증하지 않았으며, 두 사실이 각각 테스트로 고정되어 있다(`test_state_validation_does_not_check_transition_rules`, `test_unknown_state_is_rejected` — 연구자가 소스에서 직접 확인). "구조만 최소로 검증하되 어긋나면 거부한다"는 선례가 실물로 존재한다. No Silent Failure는 `GLOSSARY.md`에 이미 등재된 원칙이다. | Accept |
| 병합(Merge) | **기존 사실.** `project_intelligence.py:143-144`가 `source_code`와 `existing_workflow`를 **중복 제거 합집합**으로 병합한다(연구자가 소스에서 직접 확인). 관찰된 유일한 병합 사례이며, 그 사례도 내용을 합치지 않고 항목 단위로만 합쳤다 — RFC-0003의 규칙("Content를 합치거나 요약하지 않는다")과 일치한다. | Accept |
| 정렬(Order) | **부분적 근거 있음 + 신규.** MVP-0002가 순서를 계산하지 않고 고정 선언(`SOURCE_SECTIONS_IN_ORDER`, `PROMPT_SECTIONS_IN_ORDER`, `RENDERING_MAP`)으로 두었고, 그 결과 서로 다른 두 Case에서 구조 오버헤드가 정확히 동일(77자)했다(MVP-0002 Artifact Mapping). 여기까지는 기존 사실이다. **신규인 부분은 그 선언을 코드 상수에서 Builder의 입력(Ordering Policy)으로 꺼내는 것이다.** | Accept (조건부, 아래) |

### 검토한 반론 (기록)

- **병합 규칙 2(같은 Identifier + 다른 Content → 오류)가 과한가** —
  아니다. 대안은 조용한 덮어쓰기인데, 그러면 같은 입력에서 다른
  Context가 나오는 경로가 생겨 KP-2를 직접 위반한다. 또한 `GLOSSARY.md`
  의 No Silent Failure와 충돌한다.
- **Ordering Policy 외부화가 새 Component를 만드는가** — 만들지
  않는다. Policy는 Builder의 **입력값**이며, 그것을 무엇이 제공하는지는
  이 ADC가 결정하지 않는다(KP-1 유지).
- **Ordering Policy가 4-Layer Defer를 우회하는가** — 반대다. 이
  ADC가 정렬을 Accept할 수 있는 이유가 바로 이 외부화다. 순서 규칙이
  Model 안에 박히면 그것이 곧 분류가 되어 판단 2b를 우회하게 된다.
  Policy를 입력으로 두면 Model은 분류를 갖지 않은 채 남고, 훗날
  4-Layer가 확정되면 **하나의 Policy로** 들어온다.

### Decision

**Accept** (4개 책임 전부. 정렬에는 아래 조건을 붙인다.)

- 정렬은 **전순서**여야 하며, 유일한 Identifier를 최종 tie-break로
  사용한다.
- **구체적인 Ordering Policy의 내용은 이 ADC가 확정하지 않는다.**
  Accept되는 것은 "정렬 규칙은 Policy로 외부에서 주어지며 자료구조의
  성질에서 나오지 않는다"는 형태뿐이다.

### Decision Rationale

4개 중 3개(수집·검증·병합)는 실제 코드에서 관찰된 동작의 일반화이며,
Development HQ가 이미 수행하고 있는 일에 이름을 붙이는 것이다. 정렬은
실천(고정 선언)이 이미 검증되었고, 신규인 부분(정책 외부화)은 새
구조를 추가하는 것이 아니라 이미 있는 상수를 인자로 옮기는 형태다.

이 Accept는 Builder라는 **Component를 채택하지 않는다.** 4개 책임이
Kernel에 속한다는 판단이며, 무엇이 그것을 구현할지는 미결이다(KP-1).

### Risks

수집·병합·정렬은 현재 Development HQ 안에서 수행되고 있다(RFC-0003
§6.2). 이 책임들을 Kernel 책임으로 판단한다는 것은 장기적으로 그
코드가 이동 대상이 된다는 뜻이지만, **이 ADC는 그 이동을 지시하지
않으며 시점도 정하지 않는다.** Development HQ Phase 1 문서·코드는
그대로 둔다.

### Next Step

**ADR Required**

---

## 판단 3. K-3 Deterministic Assembly + Stable Ordering (RFC-0003 §4.2~§4.4)

### Evidence

- 결정론 테스트가 5개 Builder 전부에 존재하고 통과한다
  (`test_transformation_is_deterministic` 4건 — MVP-0001·0003·0004·
  0005, `test_rendering_is_deterministic` 1건 — MVP-0002. 연구자가
  소스에서 직접 확인). `ARTIFACT-STANDARD-v1.md`가 이를 5개 Artifact
  전부의 Contract로 이미 고정했다.
- 시계·난수 부재가 5개 MVP 전체에서 테스트로 확인되었다
  (`test_no_ai_or_model_call_symbols_present_in_module` 4건 +
  `test_no_ai_or_runtime_symbols_present_in_module` 1건).
- 정본 불변 보장이 4건의 테스트로 확인되었다(판단 1 Evidence 참조).
- 고정 구조 오버헤드가 4개 변환 단계에서 입력과 무관하게 일정했다
  (77/183/199/197자, 각 Artifact Mapping 문서에서 두 Case로 실측).
- ADC-0002 판단 1은 KP-3에 대해 *"단일 Artifact 내부의 절 순서는
  검증되었으나 계층화된 Context 간 순서 보장은 관찰된 적이 없다"*
  고 명시했다. RFC-0003 §4.4는 **계층을 도입하지 않고** 그 공백을
  채운다(전순서 + Identifier tie-break).

### 검토한 반론 (기록)

- **A-1~A-5 불변식 5개를 Baseline에 넣는 것이 과한가** — 5개 중
  4개(A-1·A-3·A-4·A-5)는 이미 통과하는 테스트가 존재하는 성질이다.
  A-2("Segment가 조용히 추가·삭제되지 않는다")만 신규이며, 이는
  A-1의 자연스러운 짝이고 No Silent Failure와 같은 방향이다.
- **O-3(순서는 자료구조 성질에서 나오지 않는다)이 기존 코드를
  위반으로 만드는가** — `build_context_bundle()`은 dict를 반환하고
  삽입 순서에 의존한다. 그 코드가 틀렸다고 판단하지 않는다 — 당시
  Kernel이 없었고, 파이썬 dict는 삽입 순서를 보존하므로 실제 오류도
  발생하지 않았다. O-3은 **Kernel의 보장 방식**에 대한 요구이며,
  Development HQ 코드에 대한 판정이 아니다. 이 ADC는 그 코드의 수정을
  지시하지 않는다.

### Decision

**Accept**

### Decision Rationale

이 판단은 이 RFC 전체에서 근거가 가장 강한 부분이다 — 결정론과 정본
불변은 이미 42개 테스트 안에 실물로 존재하며, `ARTIFACT-STANDARD-v1.md`
가 Contract로 고정해 둔 성질이다. RFC-0003이 추가하는 것은 "무엇이
입력인가"(Segment 집합 + Ordering Policy 둘뿐)를 명시해 KP-2를
**테스트 가능한 진술로 만드는 것**이며, 이는 새 구조가 아니라 기존
테스트 관행의 명문화다.

Stable Ordering의 전순서 요구는 ADC-0002 판단 1이 KP-3의 미검증
부분으로 남긴 자리를 계층 없이 채운다 — 판단 2b의 Defer를 우회하지
않는다.

### Risks

전순서·tie-break 규칙은 실제 모델 호출 없이 채택된다. 순서가 실측상
무의미하다는 관찰이 나오면 재검토 대상이다(ADC-0002 판단 1의 Risks가
KP-3·KP-4에 대해 이미 같은 조건을 기록했다).

### Next Step

**ADR Required**

---

## 판단 4. K-3 Context Boundary (RFC-0003 §4.5)

### Evidence

- RFC-0003 §4.5 자신이 *"이 절은 이 RFC에서 근거가 가장 약한
  부분이다"*, *"직접 Observation 없음"*으로 표시했다.
- 이 저장소에서 Context Boundary가 관찰된 적이 없다. 현재 유일한
  구분자는 `[Relevant Context]` 마커 하나이며(EVIDENCE-REVIEW-0001,
  MVP-0005~0008), 그것은 경계가 아니라 문자열 분리점이다.
- Boundary가 필요해지는 활용 사례(Prompt Cache, Conversation Resume,
  Context Snapshot, Memory Restore)는 **네 건 모두 관찰된 적이
  없으며**, 실제 Engine 호출이 한 번도 없었다(RFC-0005 §1).
- `docs/governance/rt/RT-0001.md` Candidate 4의 재평가 Trigger
  ("Context 전달 경로 ≥ 2")는 EVIDENCE-REVIEW-0001 기준으로 발동
  여부조차 확인되지 않은 상태다.
- ADC-0002 판단 2a는 Context Boundary를 이미 Kernel 책임 **후보**로
  Accept했다 — 후보 지위는 이 판단과 무관하게 유지된다.

### Decision

**Defer**

Context Boundary는 ADC-0002 판단 2a가 부여한 **책임 후보 지위를 그대로
유지**하되, RFC-0003 §4.5가 제안한 형태(위치 기반 Boundary,
Boundary Policy에 의한 파생)를 **확정하지 않는다.**

### Decision Rationale

이것은 ADC-0002 판단 2b가 4-Layer Context Model을 Defer한 것과 정확히
같은 상황이다 — 관찰된 적 없는 구조를, 그것이 필요해지는 사례가 한
번도 발생하지 않은 시점에 확정하려는 것이다. Kernel ADC-0001이 Memory
Module을 Defer한 근거("단일 경로가 한 번도 실패하지 않았고, 승격을
정당화할 두 번째 경로가 관찰된 적이 없다")도 그대로 적용된다.

Defer해도 상위 설계가 막히지 않는다는 점이 중요하다 — 판단 1(Model)과
판단 3(Assembly)은 Boundary 없이 성립한다. Boundary는 그 위에 나중에
얹을 수 있는 파생 개념이며, RFC-0003 §4.5 자신이 Boundary를 Segment의
속성이 아니라 **위치**로 설계해 그 나중 추가가 Model 변경 없이
가능하도록 만들어 두었다.

### Risks

Defer를 유지하는 동안 KP-4(Stable Context by Design)는 Baseline에
있으나 그 안정 구간의 경계를 말할 어휘는 없는 상태가 지속된다. 이는
ADC-0002 판단 2b의 Risks와 같은 종류의 공백이며, 이 ADC는 그것을
해소하지 않고 기록만 한다.

**재검토 조건을 명시한다**: 실제 Engine 호출이 최소 1회 관찰되고,
그 호출에서 "매번 동일하게 앞에 놓이는 Context 구간"이 실측으로
확인되면 이 Defer는 재검토된다.

### Next Step

No ADR Required

---

## 판단 5. K-4 Prompt는 Kernel Context의 Output Format이다 (RFC-0003 §5)

### Evidence

- **이 명제는 이미 구현되어 테스트로 검증되어 있다.** MVP-0002
  모듈 docstring: *"Execution Request는 Canonical Artifact다. 이
  모듈은 그 정보를 재배치(Rendering)할 뿐, Execution Request를
  대체하거나 변경하지 않는다."* (연구자가 소스에서 직접 확인)
- 정본 불변: `test_execution_request_itself_is_unchanged_by_rendering`
  (통과). 결정론: `test_rendering_is_deterministic`(통과).
- Engine 비종속: MVP-0003이 `target_engine`을 고정 placeholder
  `"unresolved"`로 두고 실제 모델명 부재를 테스트로 검증
  (`test_target_engine_is_a_placeholder_not_a_real_model_name`, 통과).
- 내용 무생성: `test_no_new_information_beyond_headers_is_added`
  (MVP-0002, 통과) — R-4("Renderer는 Context에 없는 내용을 만들지
  않는다")와 정확히 대응한다.
- `BASELINE.md` §3·§4 "Engine Independent", "Everything is
  Replaceable"이 v1.0부터 Frozen이며, KP-5가 v1.1에서 이를 Kernel
  원칙으로 고정했다.

### 검토한 반론 (기록)

- **R-3(Renderer는 순서를 재배치하지 않는다)이 기존 구현과
  충돌한다** — 실제로 충돌한다. MVP-0002 `RENDERING_MAP`은 9개 절을
  5개 절로 **재배치한다.** RFC-0003 §5.3이 이 충돌을 스스로
  기록하고 "기존 구현에 대한 서술이 아니라 변경 제안"으로 표시했다.
  따라서 R-3은 이번 Accept 범위에서 **제외한다** — 정렬 책임을
  Renderer에서 Assembly로 옮기는 것은 Execution Layer 코드 변경을
  수반하며, 그것은 이 ADC의 권한 밖이다(문서 판단이 코드 재설계를
  지시하지 않는다).
- **Claude/GPT/Gemini Renderer를 지금 만들 수 있는가** — 없다.
  실제 Engine 호출이 한 번도 없었으므로 각 Engine이 무엇을 요구하는지
  관찰된 바가 없다.

### Decision

**Accept** (원칙과 방향에 한정)

Accept되는 것:

1. Kernel Context가 **정본**이고 Prompt는 그 **표현(Output Format)**
   이라는 방향. 역방향(Prompt → Context)은 정의하지 않는다.
2. Claude / GPT / Gemini Prompt는 **동일한 Kernel Context의 서로 다른
   표현**으로 취급한다.
3. Renderer 계약 중 **R-1(순수·결정론), R-2(정본 불변), R-4(내용
   무생성), R-5(Engine 고유 개념은 Renderer 안에만 존재)**.

Accept하지 않는 것:

- **R-3(Renderer는 순서를 재배치하지 않는다)** — 기존 구현과 충돌하며
  코드 변경을 수반한다. 별도 판단 대상으로 남긴다.

### Decision Rationale

이 판단은 새 Architecture를 채택하는 것이 아니라, **이미 구현되어
통과하고 있는 테스트들이 무엇을 보장하고 있었는지를 Kernel 수준의
원칙으로 올리는 것**이다. MVP-0002·MVP-0003은 "정본과 표현의 분리"를
이름 없이 이미 실천했고, 이 Accept는 그 이름을 부여한다.

Prompt를 Output Format으로 위치시키는 것은 KP-5(Implementation
Agnostic)의 직접적 귀결이기도 하다 — Prompt가 정본이 되면 Engine이
Model의 형태를 결정하게 되어 KP-5가 무너진다.

### Risks

세 Engine(Claude/GPT/Gemini)이 실제로 동일한 Context의 표현으로
충분히 다뤄질 수 있는지는 검증된 바 없다. 어떤 Engine이 Context
구조 자체를 다르게 요구한다는 관찰이 나오면 이 원칙은 재검토
대상이다.

### Next Step

**ADR Required**

---

## 판단 5b. Engine별 Renderer 설계 (Claude / GPT / Gemini)

### Evidence

- 실제 Engine 호출이 이 저장소에서 한 번도 일어난 적이 없다
  (RFC-0005 §1).
- MVP-0003은 `target_engine`을 의도적으로 `"unresolved"`로 두었고,
  실제 모델명이 들어가지 않았음을 테스트로 고정했다.
- RFC-0002 §13은 "Prompt Assembly Engine이 필요한가"를 미결로 남겼다.

### Decision

**Defer**

### Decision Rationale

각 Engine이 무엇을 요구하는지 관찰된 바가 없으므로, 지금 Renderer를
설계하면 추측으로 구조를 만드는 것이 된다. 판단 5가 Accept한 방향
(Prompt = 표현)은 Renderer를 하나도 만들지 않아도 성립한다.

### Next Step

No ADR Required

---

## 판단 6. K-5 Development HQ Integration (RFC-0003 §6)

성격이 다른 두 내용을 분리해 판단한다.

- **6a**: 책임 배치 방향(HQ = Context 생산자, Kernel = Context 소유자)
- **6b**: 실제 통합 및 활용 사례(Prompt Cache / Conversation Resume /
  Context Snapshot / Memory Restore)

### 6a. 책임 배치 방향

#### Evidence

- `development-hq/BOUNDARY.md`(Frozen)는 이미 이 배치를 갖고 있다 —
  HQ는 "Workflow 내용"·"도메인 규칙"을 책임지고, "Task 실행
  메커니즘"·"Engine 호출"은 Kernel 책임이며, *"Development HQ는 이
  인프라를 대체하거나 우회하는 자체 메커니즘을 만들지 않는다."*
- `BASELINE.md` §7이 같은 경계를 Jarvis OS 수준에서 이미 고정했다 —
  "Workflow의 도메인 내용", "Agent가 수행하는 업무의 Prompt 및 로직
  내용"은 Jarvis OS 책임이 아니다.
- RFC-0003 §6.2가 기록한 현재 상태(HQ가 수집·병합·정렬·표현을 전부
  수행)는 EVIDENCE-REVIEW-0001과 `project_intelligence.py`에 이미
  기록·존재하는 사실이다.

#### Decision

**Accept** (방향에 한정)

#### Decision Rationale

이 배치는 새로 만드는 것이 아니라 Frozen 상태인 `BOUNDARY.md`를 Context
영역에 그대로 적용한 것이다. 새 Boundary를 만들지 않는다.

RFC-0003 §6.2가 현재 상태를 "위반"으로 판정하지 않은 것도 타당하다 —
Kernel이 없는 상태에서 HQ가 Context를 스스로 다룬 것은 다른 선택지가
없었기 때문이며, `BOUNDARY.md`가 금지한 것은 "Kernel을 대체하는 자체
실행 메커니즘의 구축"이지 "Kernel 부재 시 임시 문자열 조립"이 아니다.
이 구분을 명시적으로 기록한다.

#### Risks

이 Accept는 장기적으로 `project_intelligence.py`의 Context 관련
코드가 Kernel로 이동할 대상임을 함의한다. **이 ADC는 그 이동을
지시하지 않고 시점도 정하지 않는다.** Development HQ Phase 1
문서·코드는 수정되지 않는다.

### 6b. 실제 통합 및 활용 사례

#### Evidence

- 활용 사례 4건(Prompt Cache / Conversation Resume / Context Snapshot
  / Memory Restore) 중 **어느 것도 이 저장소에서 관찰된 적이 없다.**
  RFC-0003 §6.4의 표가 4건 전부를 "관찰된 적 없음"으로 표시했다.
- 실제 Engine 호출이 0회다(RFC-0005 §1).
- Memory Module은 Kernel ADC-0001에서 이미 Defer되었다.
- 판단 4에서 Context Boundary가 Defer되었으므로, Boundary에 의존하는
  Prompt Cache·Conversation Resume은 근거가 되는 개념 자체가 아직
  확정되지 않았다.

#### Decision

**Defer**

#### Decision Rationale

활용 사례는 KP-4가 명시한 대로 **결과이지 목적이 아니다.** 결과를
지금 확정하면 인과 방향이 뒤집혀 KP-4를 직접 위반한다. 또한 근거가
되는 Boundary가 판단 4에서 Defer되었으므로, 6b를 Accept하면 Defer된
개념 위에 확정을 쌓게 된다.

실제 통합 역시 Defer한다 — Development HQ Phase 1은 종료되었고
(ADR-0001·ADR-0002 선례), 통합을 판단할 근거(실제 Engine 호출 관찰)가
아직 없다.

#### Risks

Kernel Context Model이 Baseline에 들어가되 그것을 실제로 사용하는
경로는 없는 상태가 지속된다. 이는 `GOVERNANCE-REVIEW-0001-post-adc-0001.md`
§1이 기록한 "ADC는 통과했으나 후속이 없는" 패턴과 같은 종류의 절차
부채가 될 수 있다. 이 ADC는 그것을 해소하지 않고 기록한다.

**재검토 조건**: 실제 Engine 호출이 최소 1회 관찰되면 6b와 판단 4를
함께 재검토한다.

#### Next Step

No ADR Required

---

## 판단 7. Baseline 반영 범위

### Evidence

- `docs/01_architecture/BASELINE.md` **§Version 절**(판단 당시 §13):
  Version v1.1, Status Active, Architecture State **Frozen**.
- 같은 문서 §10 Out of Scope: **Kernel Architecture**, Component
  Design이 명시되어 있다. v1.1이 §11에서 이를 그대로 유지한다고
  다시 못박았다.
- RFC-0003은 Kernel Architecture를 설계하지 않는다 — §7이 Component
  필요 여부, 직렬화 형식, Policy 내용, Boundary 개수를 전부 미결로
  남겼고, Builder·Assembly·Renderer를 전부 **책임**으로만 기술했다.
- `ARCHITECTURE_GOVERNANCE.md` Freeze 원칙: Baseline은 "지금 결정할
  것과 나중에 결정할 것이 명확히 구분되고 추적되는 상태"를 뜻한다.
- ADR-0002 선례: Frozen 상태의 Baseline을 RFC → ADC → ADR 절차를
  거쳐 v1.0 → v1.1로 갱신했다.

### Decision

**Accept** (반영 범위를 한정하는 조건부)

Baseline에 반영할 범위:

1. Kernel Context Model 5개 요소(판단 1, 4개 제약 포함)
2. Context Builder의 4개 책임(판단 2, 정렬의 Policy 외부화 조건 포함)
3. Deterministic Assembly + Stable Ordering(판단 3)
4. Prompt = Kernel Context의 Output Format(판단 5, R-3 제외)
5. Development HQ = Context 생산자 / Kernel = Context 소유자(판단 6a)

Baseline에 반영하지 **않는** 것:

- 4-Layer Context Model — ADC-0002 판단 2b Defer **유지**.
- Context Identifier 파생 규칙 — 판단 1b Defer.
- Context Boundary의 확정 형태 — 판단 4 Defer(후보 지위는 유지).
- Engine별 Renderer — 판단 5b Defer.
- R-3(Renderer 순서 재배치 금지) — 판단 5에서 Accept 범위 제외.
- 활용 사례 4건 및 실제 통합 — 판단 6b Defer.
- Kernel Architecture 및 Component Design — §10 Out of Scope **그대로
  유지**.

### Decision Rationale

RFC-0003이 Baseline에 추가하려는 것은 "Kernel이 무엇을 관리하는가
(Model)"와 "그것을 다룰 때 지켜야 할 제약(책임·불변식)"이며,
"어떤 Component가 어떻게 생겼는가"가 아니다. §10이 막는 것은 후자다.

이 반영은 오히려 §10이 무엇을 Out of Scope로 두고 있는지를 더
분명하게 만든다 — 7개 항목이 명시적으로 Defer/제외로 기록되어
추적된다. Freeze 원칙이 요구하는 상태와 부합한다.

### Risks

- Baseline 버전 갱신(v1.1 → v1.2)이 필요하다. 절 번호 정책과 인용
  갱신 범위는 이 ADC가 정하지 않고 ADR에 위임한다.
- 이번 판단이 다시 4건의 "ADR Required"를 발생시킨다. ADC-0002가
  기록한 절차 부채(Kernel ADC-0001의 미작성 ADR 2건)는 이 ADC가
  해소하지 않는다 — 사실로만 기록한다.

### Next Step

**ADR Required**

---

## 종합

| 판단 항목 | Decision | Next Step |
|---|---|---|
| 1. K-1 Context Domain Model 5개 요소 | **Accept** (4개 제약 조건부) | ADR Required |
| 1b. Context Identifier 파생 규칙 | **Defer** | No ADR Required |
| 2. K-2 Builder 4개 책임(수집·검증·병합·정렬) | **Accept** (정렬은 Policy 외부화 조건부) | ADR Required |
| 3. K-3 Deterministic Assembly + Stable Ordering | **Accept** | ADR Required |
| 4. K-3 Context Boundary | **Defer** (책임 후보 지위 유지) | No ADR Required |
| 5. K-4 Prompt = Output Format | **Accept** (R-3 제외) | ADR Required |
| 5b. Engine별 Renderer 설계 | **Defer** | No ADR Required |
| 6a. K-5 책임 배치 방향 | **Accept** (방향 한정) | ADR Required |
| 6b. K-5 실제 통합 및 활용 사례 4건 | **Defer** | No ADR Required |
| 7. Baseline 반영 범위 | **Accept** (범위 한정) | ADR Required |

RFC-0003 전체를 일괄 승인하지 않았다. 10개 판단 중 6개 Accept, 4개
Defer이며, Accept 중 4개는 조건·제외 항목을 붙였다.

Reject나 Out of Authority로 분류된 항목은 없다. 다만 판단 5의 R-3은
**Accept 범위에서 제외**했다 — 그것은 문서 판단이 아니라 Execution
Layer 코드 재설계를 요구하므로 이 ADC의 권한을 넘는다.

**Defer 4건이 공유하는 단일 재검토 조건**: 실제 Engine 호출이 최소
1회 관찰되는 것. 판단 4·5b·6b는 이 조건에 직접 걸려 있고, 판단 1b는
Context를 비교·재사용하는 사례가 나타나야 판단 가능하다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0003과 그것이 인용한 기존
  문서·소스에 실제로 기록된 사실만 사용했다. 인용한 테스트 이름
  13건과 `project_intelligence.py:143-144`는 소스에서 직접 확인했다.
  새 실험을 하지 않았다.
- 일괄 승인했는가 — **아니오**. 5개 Phase를 10개 판단으로 분리했고,
  그중 4개가 Defer다.
- ADC-0002 판단 2b(4-Layer Defer)를 우회했는가 — **아니오**. 판단
  1은 Segment에 분류 필드를 두지 않는 것을 Accept 조건으로 명시했고,
  판단 2는 정렬 규칙을 Model 밖(Policy)에 두는 형태만 Accept했으며,
  판단 4는 Boundary 자체를 Defer했다. 세 지점에서 개별 확인했다.
- "필요할 것 같다"는 이유로 Accept했는가 — **아니오**. 판단 4·5b·6b가
  바로 그 이유로 Defer되었다(관찰된 적 없는 것을 확정하지 않았다).
- 반론을 검토했는가 — **Pass**. 판단 1에 3건, 판단 2에 3건, 판단 3에
  2건, 판단 5에 2건을 기록했다. 그중 하나(R-3)는 실제로 Accept 범위
  축소로 이어졌다.
- Architecture Drift가 없는가 — **없음**. 새 Layer/Component를 만들지
  않았다. 판단 7이 `BASELINE.md` §10 Out of Scope를 그대로 유지하도록
  범위를 한정했다.
- Kernel Leak가 없는가 — **없음**. Scheduler/Registry/Runtime/Memory/
  Event Bus/Prompt Assembly Engine 어느 것도 설계하거나 필요 여부를
  판단하지 않았다.
- 구현을 제안했는가 — **아니오**. 판단 2·6a의 Risks에 "코드 이동을
  지시하지 않는다"를 명시했고, 판단 5는 코드 변경을 수반하는 R-3을
  범위에서 제외했다.
- Development HQ를 수정 대상으로 삼았는가 — **아니오**. 판단 3의
  반론 검토와 판단 6a의 Risks 두 곳에서 명시적으로 배제했다.
- ADR을 작성했는가 — **아니오**. 이 ADC는 ADR이 필요하다는 판정만
  내렸다.
