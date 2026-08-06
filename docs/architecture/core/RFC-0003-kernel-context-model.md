# RFC-0003: Kernel Context Model — Context, Builder, Assembly, Prompt Projection

**Status**: Proposed (검토 대상, 결정 아님)
**Version**: Draft
**Author**: Claude Code (Phase K-1 ~ K-5 요청 → RFC 전환)
**상위 근거**: `docs/01_architecture/BASELINE.md` v1.1 §11(Kernel 정의)·§12(KP-1~KP-6)
**관련 문서**: `docs/architecture/core/RFC-0002-kernel-definition.md`(§12·§14·§15),
`docs/architecture/core/ADC-0002-kernel-definition.md`(판단 2a Accept, 판단 2b Defer),
`docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`,
`docs/core/execution-layer/MVP-0001~0005-*`,
`docs/research/EVIDENCE-REVIEW-0001.md`,
`docs/01_mvp/MVP-0009-observation.md`,
`development-hq/BOUNDARY.md`

> 이 RFC는 Kernel Context **Model**을 제안한다. Prompt를 만들지 않는다.
> Component를 만들지 않는다. 구현하지 않는다.
> Kernel은 Prompt 이전에 존재하는 개념이며, Prompt는 그 결과물 중
> 하나다.

---

## 0. 이 RFC의 위치와 절차적 제약

`docs/architecture/core/ADC-0002-kernel-definition.md`는 두 가지를
동시에 남겼다.

- **판단 2a — Accept**: Stable Prefix / Context Boundary / Context
  Assembly / Context Ordering 4개를 Kernel 책임 **후보**로 채택했다.
- **판단 2b — Defer**: 그 책임들이 다룰 Context가 **무엇으로
  구성되는가**(4-Layer Context Model)는 확정하지 않았다.

같은 문서 판단 2b의 Risks가 이 공백을 이미 기록했다: *"4개 책임은
채택되었으나 그 책임이 다룰 Context의 구조는 미정인 상태가 지속된다."*
이 RFC는 그 공백을 여는 단계이며, RFC-0002 §14 Roadmap의 "Kernel
Context Model" 단계에 해당한다.

### 0.1 이 RFC가 지켜야 하는 제약

| 제약 | 출처 |
|---|---|
| 4-Layer(Immutable/Stable/Working/Ephemeral) 분류를 확정하지 않는다 | ADC-0002 판단 2b (Defer) |
| Kernel Architecture·Component Design을 하지 않는다 | `BASELINE.md` §10 Out of Scope (v1.1에서 유지 확인) |
| 책임으로 정의하고 구현으로 정의하지 않는다 | `BASELINE.md` §12 KP-1 |
| 특정 모델·벤더에 종속되는 요소를 Model에 넣지 않는다 | `BASELINE.md` §12 KP-5 |
| Kernel이 시계·난수·내부 상태를 갖지 않는다 | `BASELINE.md` §12 KP-6 |
| Development HQ의 문서·코드를 수정하지 않는다 | ADR-0001·ADR-0002 선례(Phase 1 종료 후 불변) |

### 0.2 Evidence의 한계를 먼저 밝힌다

이 프로젝트는 **아직 실제 모델을 한 번도 호출한 적이 없다**
(`docs/02_rfc/RFC-0005-development-hq-execution-boundary.md` §1:
MVP-0005~0013 전 구간 LLM/ML 호출 없음). 따라서 Prompt Cache,
Conversation Resume, Context Snapshot에 대한 직접 Observation은
존재하지 않는다.

이 RFC는 각 절마다 근거의 성격을 **관찰된 사실 / 관찰된 사실의 일반화 /
신규**로 구분해 표시한다. 신규 항목을 관찰된 사실처럼 서술하지 않는다.

---

## 1. 문제

지금까지 이 저장소에서 "Context"는 두 가지 서로 다른 것을 가리켰고,
어느 쪽도 Model로 정의된 적이 없다.

1. `BASELINE.md` §6 Concept Model의 **Context** — "Task 실행 중에만
   유효한 State".
2. Development HQ MVP-0005~0009의 **실제 Context** —
   `collect_relevant_context()`가 수집하고 `build_context_bundle()`이
   재배치한 8개 항목. 전달 방식은 `issue["description"]` 문자열에
   덧붙이기 하나뿐이었다(EVIDENCE-REVIEW-0001, 4건 반복 확인).

그 결과 다음을 말할 수 있는 어휘가 없다.

- "이 Context의 어느 조각이 어디에서 왔는가"
- "같은 입력에서 같은 Context가 나왔는가"
- "Context의 어느 지점까지가 안정 영역인가"
- "이 Prompt는 어떤 Context의 표현인가"

Kernel 책임 4개(ADC-0002 판단 2a)는 전부 이 어휘를 전제로 한다.
어휘가 없으면 책임을 판단할 대상도 없다.

---

## 2. Phase K-1 — Kernel Context Model (최소 Domain Model)

**이 절의 목표**: Kernel이 실제로 무엇을 관리하는지를 표현할 수 있는
**최소 어휘**를 정의한다. 계층 분류는 하지 않는다.

### 2.1 Model 개요

```
Context
├── Context Identifier          (이 Context를 무엇이라 부르는가)
├── Context Metadata            (이 Context에 대한 서술)
└── Context Segment  [ordered]  (Context를 이루는 최소 단위)
    ├── Context Identifier      (이 Segment를 무엇이라 부르는가)
    ├── Context Source          (이 Segment가 어디에서 왔는가)
    ├── Content                 (Kernel이 해석하지 않는 불투명한 값)
    ├── Context Metadata        (이 Segment에 대한 서술)
    └── Order Key               (이 Segment가 어디에 놓이는가)
```

5개 개념 외에 어떤 요소도 이 Model에 추가하지 않는다.

### 2.2 Context Segment

| 항목 | 내용 |
|---|---|
| 정의 | Kernel이 **독립적으로 식별·정렬·포함/제외할 수 있는 Context의 최소 단위**. |
| 구성 | Identifier, Source, Content, Metadata, Order Key |
| Content | Kernel에게 **불투명한 값**이다. Kernel은 Content를 파싱·요약·재해석·검열하지 않는다. |
| 근거 성격 | **관찰된 사실의 일반화** |

**근거**: Execution Layer 5개 Builder 전부가 "Wrap, not rewrite" —
입력 Artifact의 텍스트를 한 글자도 바꾸지 않고 고정 절만 덧붙였다
(`ARTIFACT-STANDARD-v1.md` 공통 패턴). MVP-0002
`PromptSpecificationBuilder`는 9개 절의 **본문을 그대로 옮기기만**
하고 재배치했다(`_extract_section_body` → `RENDERING_MAP`). 즉 "이름이
붙은 여러 조각을 내용 변경 없이 다룬다"는 실천은 이미 코드로
존재한다. 이 RFC는 그 조각에 **Context Segment**라는 이름을 붙일 뿐이다.

MVP-0009 `build_context_bundle()`도 같은 형태였다 — 8개 항목(issue,
goal, relevant_documents, relevant_code, relevant_observations,
relevant_decisions, known_constraints, open_questions)을 각각
독립적으로 만들고 `_render_context_bundle()`이 8개 마크다운 절로
렌더링했다.

### 2.3 Context Source

| 항목 | 내용 |
|---|---|
| 정의 | Segment가 **어디에서 왔는가**를 식별하는 값. |
| 구성 | `source_id` (비교 가능한 불투명 식별자) 하나. |
| Kernel의 취급 | Kernel은 Source를 **비교**할 뿐 **해석하지 않는다.** 어떤 Source가 존재하는지는 HQ가 정한다. |
| 근거 성격 | **관찰된 사실의 일반화** |

**근거**: MVP-0009는 서로 다른 출처(파일 목록, Issue 원문, 규칙 기반
추출 결과)에서 온 항목들을 하나의 Bundle로 묶었고, `relevant_code`는
`source_code`와 `existing_workflow` **두 출처의 합집합(중복 제거)**
이었다. 출처가 복수라는 사실은 이미 코드에 있다.

**Kernel이 Source 목록을 정하지 않는 이유**: `development-hq/BOUNDARY.md`
가 "Workflow 내용", "도메인 규칙"을 HQ 책임으로 고정했다. 8개 카테고리
이름은 Development HQ의 도메인 내용이므로 Kernel Model에 들어가면
`BASELINE.md` §7("Jarvis OS는 Workflow의 도메인 내용을 책임지지
않는다")을 위반한다.

### 2.4 Context Identifier

| 항목 | 내용 |
|---|---|
| 정의 | Context 또는 Segment의 동일성 판정 기준. |
| 구성 | 값 하나(문자열). |
| 제약 | **Kernel은 Identifier를 스스로 생성하지 않는다.** 호출자가 주입하거나, Context 내용으로부터 결정론적으로 파생한다. 시계·난수를 사용하지 않는다. |
| 미결 | 파생 규칙(호출자 주입 / 내용 해시 / 그 외)은 이 RFC가 결정하지 않는다. |
| 근거 성격 | **관찰된 사실의 재진술** |

**근거**: `request_id`·`created_at`(MVP-0003), `handle_id`·
`submitted_at`(MVP-0004), `handle_id`·`state`·`changed_at`(MVP-0005)은
전부 호출자 주입이며, 5개 MVP 전체에서 `uuid.uuid4`, `datetime.now`,
`time.time`이 소스에 없음이 테스트로 확인되었다
(`ARTIFACT-STANDARD-v1.md`). 이 제약은 KP-6과 정확히 같은 것을
말한다.

### 2.5 Context Metadata

| 항목 | 내용 |
|---|---|
| 정의 | Segment 또는 Context **에 대한** 서술. Content **의** 내용이 아니다. |
| 구성 | 문자열 키-값의 순서 없는 집합. |
| 제약 1 | Kernel은 필수 키를 정의하지 않는다(이 Phase 기준). |
| 제약 2 | **계층 분류(Immutable/Stable/Working/Ephemeral)를 담지 않는다** — ADC-0002 판단 2b Defer 유지. |
| 제약 3 | **특정 Engine에만 의미가 있는 키를 담지 않는다**(role, cache_control, token count 등) — KP-5. |
| 근거 성격 | **신규** (다만 제약 2·3은 기존 결정의 재확인) |

**Metadata와 Order Key를 분리하는 이유**: Order Key는 조립 결과를
결정하므로 결정론(KP-2)의 일부다. Metadata는 그렇지 않다. 결정론에
영향을 주는 값과 주지 않는 값을 같은 자리에 두면, "무엇을 바꾸면
Context가 바뀌는가"를 말할 수 없게 된다.

### 2.6 Context

| 항목 | 내용 |
|---|---|
| 정의 | **순서가 정해진 유한한 Context Segment 열**과 그 Identifier·Metadata. |
| 성질 1 | Context는 **값(Value)이지 서비스가 아니다.** 조립된 뒤 변경되지 않는다. |
| 성질 2 | Context는 저장 방식·직렬화 형식을 규정하지 않는다. |
| 근거 성격 | **관찰된 사실의 일반화** |

**근거(성질 1)**: 5개 Artifact 전부가 생성 후 하류에서 변경되지 않음이
테스트로 확인되었다(`test_execution_request_itself_is_unchanged_by_rendering`
등 4건). MVP-0005는 상태가 바뀔 때 Execution Handle을 **수정하지 않고
새 Artifact(Execution State)를 만들었다** — 값 의미론이 이미 실천되고
있다.

### 2.7 이 Model에 **넣지 않는 것**과 그 이유

| 제외 항목 | 이유 |
|---|---|
| Layer / 안정성 분류 필드 | ADC-0002 판단 2b Defer. 관찰된 적 없는 taxonomy를 Model에 박지 않는다. |
| Token 수 / 예산 | 토크나이저는 Engine 종속이다(KP-5). 관찰된 적 없다. |
| Role (system/user/assistant) | Engine의 표현 형식 개념이다. K-4의 Output Format에 속하지, Model에 속하지 않는다. |
| TTL / Cache Key / Invalidation | Prompt Cache는 결과이지 목적이 아니다(KP-4). |
| 영속화·저장소 | Memory Module은 Kernel ADC-0001에서 Defer되었다. |
| 생성 시각 / 순번 자동 발급 | KP-6. Kernel은 시계·난수를 갖지 않는다. |
| 품질·신뢰도 점수 | 관찰된 적 없고, 판단은 Kernel 책임이 아니다(`BASELINE.md` §7: "개별 작업 결과의 품질 및 정확성"은 Jarvis OS 책임이 아니다). |

### 2.8 기존 Concept Model과의 관계 (용어 충돌 주의)

`BASELINE.md` §6은 이미 **Context**를 "Task 실행 중에만 유효한 임시
State"로 정의했고, `Memory는 Context를 HQ 네임스페이스 안에
영속화한다`고 기록했다.

이 RFC의 **Kernel Context는 새 개념이 아니라 그 Concept의
구체화(refinement)**다. §6의 Context가 "무엇인가"만 말했다면, 이
RFC는 "무엇으로 구성되는가"를 말한다. 영속화(Memory)는 이 RFC의
범위 밖이며 Defer 상태 그대로다.

**용어 위험을 기록한다**: 두 문서가 같은 단어를 서로 다른 상세도로
쓰게 된다. 이 RFC는 "Kernel Context"라는 한정 표현을 쓰고, §6의
Context를 재정의하지 않는다.

---

## 3. Phase K-2 — Kernel Context Builder

**이 절의 목표**: Context를 만드는 책임을 정의한다. Prompt는 만들지
않는다.

### 3.1 Builder의 형태

Kernel Context Builder는 **순수 함수의 책임**이다.

```
(Segment 입력들, Ordering Policy) → Context
```

- 시계·난수·I/O를 쓰지 않는다(KP-6).
- 같은 입력은 항상 같은 Context를 만든다(KP-2).
- 어떤 Component가 이 책임을 구현할지는 결정하지 않는다(KP-1).

### 3.2 4개 책임

#### (1) Context 수집 (Collect)

| 항목 | 내용 |
|---|---|
| 책임 | 하나 이상의 Context Source로부터 Segment를 모은다. |
| 하지 않는 것 | Source를 **발견**하지 않는다. 어떤 Source를 볼지는 호출자(HQ)가 정해 넘긴다. |
| 근거 성격 | **관찰된 사실** |

**근거**: MVP-0005~0008 네 건 모두 `collect_relevant_context()`가
정확히 1회 호출되었고 호출 위치는 항상 Planning 직전이었다
(EVIDENCE-REVIEW-0001). 수집이 한 지점에서 일어난다는 사실은
반복 관찰되었다.

#### (2) Context 검증 (Validate)

| 항목 | 내용 |
|---|---|
| 책임 | **구조 불변식만** 검사한다. |
| 검사 대상 | 모든 Segment에 Identifier가 있는가 / Identifier가 Context 안에서 유일한가 / Source가 있는가 / Order Key가 비교 가능한가 |
| 하지 않는 것 | 내용의 사실 여부, 관련성, 품질, 길이·토큰 예산 검사 |
| 실패 처리 | 조용히 통과시키지 않는다(No Silent Failure). |
| 근거 성격 | **관찰된 사실의 일반화** |

**근거**: MVP-0005 `ExecutionStateBuilder`는 `state`가 허용된 5개 값
중 하나인지만 검증하고 **전이 규칙은 검증하지 않았다** — 그것을
명시적으로 확인하는 테스트가 존재한다
(`test_state_validation_does_not_check_transition_rules`, 그리고
거부 경로는 `test_unknown_state_is_rejected`). "구조만 최소로
검증하되, 어긋나면 거부한다"는 선례가 이미 코드에 있다. No Silent Failure는 `GLOSSARY.md`에 이미 등재된
원칙이다.

#### (3) Context 병합 (Merge)

| 항목 | 내용 |
|---|---|
| 책임 | 복수 Source에서 온 Segment 집합을 하나의 집합으로 합친다. |
| 규칙 1 | 같은 Identifier + 같은 Content → 하나로 취급(중복 제거). |
| 규칙 2 | 같은 Identifier + 다른 Content → **오류**. 어느 쪽을 남길지 Kernel이 임의로 정하지 않는다. |
| 하지 않는 것 | Content를 합치거나 요약하지 않는다. Segment 경계를 무너뜨리지 않는다. |
| 근거 성격 | **관찰된 사실의 일반화** |

**근거**: MVP-0009 `build_context_bundle()`의 `relevant_code`는
`source_code + existing_workflow`의 **중복 제거 합집합**이었다
(MVP-0009 Observation). 실제로 관찰된 유일한 병합 사례이며, 그 사례도
내용을 합치지 않고 항목 단위로만 합쳤다.

**규칙 2가 오류인 이유**: 조용한 덮어쓰기는 같은 입력에서 다른 Context가
나올 수 있는 경로를 만든다 — KP-2 위반이다.

#### (4) Context 정렬 (Order)

| 항목 | 내용 |
|---|---|
| 책임 | Segment 집합에 **전순서(total order)**를 부여한다. |
| 규칙 | `(Order Key, Identifier)` 사전식 정렬. Identifier는 유일하므로(검증 (2)) 동률이 남지 않는다. |
| 핵심 | **Ordering Policy는 Builder의 입력이지, Model에 박힌 분류가 아니다.** |
| 근거 성격 | **관찰된 사실의 일반화 + 신규(정책 외부화)** |

**근거**: MVP-0002는 순서를 계산하지 않고 **고정 선언**으로 두었다 —
`SOURCE_SECTIONS_IN_ORDER`(9개), `PROMPT_SECTIONS_IN_ORDER`(5개),
`RENDERING_MAP`. 그 결과 서로 다른 두 Case에서 구조 오버헤드가 정확히
동일(77자)했다(MVP-0002 Artifact Mapping). "순서를 선언으로 고정한다"는
실천은 검증되었다.

**신규인 부분**: 그 선언을 코드 상수에서 **Builder의 입력(Ordering
Policy)**으로 꺼낸다는 점이다. 이 외부화가 판단 2b와의 관계에서
중요하다 — 훗날 4-Layer 분류가 확정되면 그것은 **하나의 Ordering
Policy**로 들어올 뿐, Model(§2)은 바뀌지 않는다. 지금 taxonomy를
확정하지 않고도 KP-3을 만족시키는 방법이다.

### 3.3 Builder가 하지 않는 것

- Prompt 생성 (K-4의 책임)
- 잘라내기·요약·압축 (Compaction — RFC-0002 §14의 별도 단계)
- 영속화·복원 (Memory — Defer)
- Source 발견·탐색 (Registry 책임 후보, 미결)

---

## 4. Phase K-3 — Kernel Context Assembly

**이 절의 목표**: Builder가 만든 것을 하나의 Kernel Context로 조립하는
과정에 KP-2·KP-3·Context Boundary가 실제로 어떻게 적용되는지 정의한다.

### 4.1 Assembly의 정의

Assembly는 **검증되고 정렬된 Segment 열을 하나의 Kernel Context 값으로
확정하는 단계**다. Builder(수집·검증·병합·정렬)의 결과를 받아,
그것을 더 이상 변하지 않는 값으로 만든다.

### 4.2 Assembly 불변식 (제안)

| ID | 불변식 | 근거 성격 |
|---|---|---|
| A-1 | Segment Content는 조립 과정에서 한 글자도 바뀌지 않는다. | 관찰된 사실 (5/5 Builder "Wrap, not rewrite") |
| A-2 | Segment가 조용히 추가되거나 사라지지 않는다. | 신규(A-1의 자연스러운 짝) |
| A-3 | 입력 Segment는 조립 후에도 변경되지 않는다. 결과는 새 값이다. | 관찰된 사실 (`test_*_itself_is_unchanged_by_*` 4건) |
| A-4 | 조립은 시계·난수·외부 I/O를 읽지 않는다. | 관찰된 사실 (5개 MVP 전체 소스에 `datetime.now`/`uuid4`/`time.time` 부재, 테스트로 확인) |
| A-5 | 같은 입력 + 같은 Policy → 같은 Context. | 관찰된 사실 (결정론 테스트 5건 통과) |

### 4.3 Deterministic Assembly (KP-2의 구체화)

KP-2는 "동일한 입력은 항상 동일한 Context를 구성해야 한다"고만
말한다. 이 RFC는 **"입력"이 무엇인지**를 확정한다.

> Assembly의 입력은 **(Segment 집합, Ordering Policy)** 둘뿐이다.
> 이 둘이 같으면 결과는 같아야 한다. 그 밖의 어떤 것(호출 시각, 호출
> 순서, 프로세스 상태, 환경 변수)도 결과에 영향을 주어서는 안 된다.

이 진술이 있어야 KP-2를 **테스트할 수 있다.** Execution Layer가 이미
같은 형태의 테스트를 5건 갖고 있다.

### 4.4 Stable Ordering (KP-3의 구체화)

KP-3은 "Context는 항상 동일한 순서로 조립되어야 한다"고만 말한다.
ADC-0002 판단 1은 이 원칙에 대해 *"단일 Artifact 내부의 절 순서는
검증되었으나, 계층화된 Context 간의 순서 보장은 관찰된 적이 없다"*
고 명시했다. 이 RFC는 그 미검증 부분을 **계층 없이** 채운다.

| 요구 | 내용 |
|---|---|
| O-1 | 순서는 **전순서**여야 한다. 부분 순서는 KP-3을 만족하지 않는다. |
| O-2 | 동률(tie)이 존재하면 결정론이 깨진다. 따라서 유일한 Identifier를 최종 tie-break로 사용한다. |
| O-3 | 순서는 Segment의 **선언된 Order Key**에서 나오며, 수집 순서·해시 순회 순서·삽입 순서에서 나오지 않는다. |
| O-4 | 순서 규칙은 Policy로 명시되며, 코드에 암묵적으로 흩어지지 않는다. |

**O-3이 중요한 이유**: MVP-0009 `build_context_bundle()`은 파이썬
`dict`를 반환했고, 렌더링 순서는 함수가 항목을 만든 순서에 의존했다.
그 코드에서는 문제가 없었지만(삽입 순서 보존), "순서가 자료구조의
성질에서 나온다"는 상태는 KP-3을 **보장하지 못한다** — 보장은 선언에서
나와야 한다.

### 4.5 Context Boundary

**근거 성격: 신규. 직접 Observation 없음.**

| 항목 | 내용 |
|---|---|
| 정의 | 조립된 Segment 열 위의 **위치(position)**. "여기까지는 다음 호출에서도 같다"와 "여기부터는 매번 바뀐다"를 가르는 지점. |
| 형태 | Segment의 속성이 아니라 **열 위의 인덱스/표식**이다. |
| 산출 방법 | Boundary Policy(Assembly의 입력)가 계산한다. Kernel은 그 계산이 결정론적임만 보장한다. |
| Kernel이 보장하는 것 | (a) Boundary는 **파생값**이며 손으로 유지되지 않는다. (b) Boundary 앞 구간은 같은 입력에 대해 바이트 단위로 동일하다. |
| Kernel이 보장하지 않는 것 | Boundary가 몇 개인가. 각 Boundary의 의미가 무엇인가. 무엇이 Boundary 앞에 놓여야 하는가. |

**왜 Segment의 속성이 아니라 위치인가**: "이 Segment는 안정적이다"를
Segment에 적는 순간, 그것은 곧 안정성 분류가 되고 ADC-0002 판단
2b가 Defer한 taxonomy를 다른 이름으로 확정하는 것이 된다. 위치로
두면 분류 없이도 경계를 말할 수 있고, 훗날 4-Layer가 확정되면 그것은
**하나의 Boundary Policy**로 들어온다.

**정직한 표시**: 이 절은 이 RFC에서 근거가 가장 약한 부분이다.
Boundary가 실제로 필요한지는 실제 Engine 호출이 한 번이라도 일어난
뒤에야 관찰될 수 있다. 이 RFC는 Boundary를 **책임의 형태로만** 제안하며,
확정을 요구하지 않는다.

---

## 5. Phase K-4 — Prompt Assembly (Output Format)

**이 절의 핵심 명제**:

> Prompt는 Kernel의 본질이 아니다. Prompt는 Kernel Context의 **하나의
> 표현(Output Format)**이다. Claude Prompt, GPT Prompt, Gemini Prompt는
> 모두 **동일한 Kernel Context의 서로 다른 표현**이다.

### 5.1 방향은 한쪽으로만 성립한다

```
Kernel Context   (Canonical — 정본)
        │
        ├── Renderer A ──▶ Claude Prompt      (표현)
        ├── Renderer B ──▶ GPT Prompt         (표현)
        └── Renderer C ──▶ Gemini Prompt      (표현)
```

- Kernel Context는 정본이다. Prompt는 파생물이다.
- **역방향은 정의하지 않는다** — Prompt를 다시 읽어 Context를 복원하는
  경로는 이 RFC의 범위가 아니다.
- Prompt가 Model의 형태를 바꾸지 않는다. 어떤 Engine이 무엇을
  요구하든, 그것은 Renderer가 흡수한다(KP-5).

### 5.2 이것은 신규 발상이 아니다 — 이미 구현되어 검증되었다

**근거 성격: 관찰된 사실의 일반화.**

Execution Layer MVP-0002가 정확히 이 구조를 이미 구현했다.

| 이 RFC의 개념 | MVP-0002의 실제 구현 |
|---|---|
| Canonical Context | Execution Request — "Execution Request는 Canonical Artifact다. 이 모듈은 그 정보를 재배치(Rendering)할 뿐, 대체하거나 변경하지 않는다"(모듈 docstring) |
| Renderer | `build_prompt_specification()` |
| 표현(Output Format) | Prompt Specification |
| 정본 불변 보장 | `test_execution_request_itself_is_unchanged_by_rendering` (통과) |
| 결정론 보장 | `test_rendering_is_deterministic` (통과) |
| Engine 비종속 | MVP-0003 `target_engine = "unresolved"` + `test_target_engine_is_a_placeholder_not_a_real_model_name` (통과) |

즉 "정본이 있고 Prompt는 그 표현일 뿐이며, 표현을 만들어도 정본은
바뀌지 않는다"는 명제는 **이미 코드와 테스트로 존재한다.** 이 RFC가
하는 일은 그것을 Kernel 수준의 원칙으로 올리는 것이다.

### 5.3 Renderer가 지켜야 할 계약 (제안)

| ID | 계약 | 근거 성격 |
|---|---|---|
| R-1 | Renderer는 순수하며 결정론적이다. | 관찰된 사실 (MVP-0002) |
| R-2 | Renderer는 Kernel Context를 변경하지 않는다. | 관찰된 사실 (MVP-0002) |
| R-3 | Renderer는 Segment 순서를 재배치하지 않는다 — 순서는 Assembly가 이미 확정했다. | 신규 |
| R-4 | Renderer가 덧붙이는 것은 **고정된 구조 틀**뿐이며, Context에 없는 내용을 만들어내지 않는다. | 관찰된 사실 (구조 오버헤드가 입력과 무관하게 항상 동일: 77/183/199/197자) |
| R-5 | Engine 고유 개념(role, 메시지 배열, 캐시 지시자 등)은 Renderer 안에서만 존재한다. Model에 새지 않는다. | 신규 (KP-5의 구체화) |

**R-3에 대한 주의**: MVP-0002의 `RENDERING_MAP`은 실제로 절을
재배치했다(9개 → 5개). 이것이 R-3과 충돌하는 것처럼 보이므로 구분을
명시한다 — MVP-0002 시점에는 Assembly 단계가 존재하지 않았고 정렬
책임이 Renderer 안에 있었다. 이 RFC는 그 책임을 Assembly(K-3)로
옮기자고 제안한다. 즉 R-3은 기존 구현에 대한 서술이 아니라 **변경
제안**이며, 그렇게 표시한다.

### 5.4 이 절이 결정하지 않는 것

- Prompt Assembly Engine이라는 Component가 필요한지 (RFC-0002 §13에서
  미결로 남은 그대로)
- 어떤 Engine의 Renderer를 먼저 만들 것인지
- 메시지 role 매핑, 토큰 예산, 캐시 지시자 사용 방법
- Prompt 문구의 효과성(Prompt Engineering) — 이 프로젝트의 범위가 아니다

---

## 6. Phase K-5 — Development HQ Integration

**이 절의 목표**: Development HQ가 Kernel Context를 어떻게 생성하고
전달하는지의 **방향**을 정의한다. 실제 통합을 수행하지 않는다.

### 6.1 책임 배치

| 주체 | 책임 |
|---|---|
| Development HQ | **무엇이 Context에 들어가야 하는가**를 정한다. Source를 선언하고 Segment의 Content를 제공한다. |
| Kernel | **그것이 어떻게 식별·검증·병합·정렬·조립·표현되는가**를 담당한다. |

이 배치는 새로 만드는 것이 아니라 `development-hq/BOUNDARY.md`
(Frozen)를 그대로 따른 것이다 — HQ는 "Workflow 내용"과 "도메인 규칙"을
책임지고, "실행 메커니즘"은 Kernel 책임이며, HQ는 *"이 인프라를
대체하거나 우회하는 자체 메커니즘을 만들지 않는다."*

### 6.2 현재 상태를 정직하게 기록한다

**관찰된 사실**: 현재 Development HQ는 Kernel이 존재하지 않기 때문에
Context 책임을 **스스로 전부 수행하고 있다.**

| Kernel 책임 (제안) | 현재 Development HQ에서 수행하는 위치 |
|---|---|
| 수집 | `project_intelligence.collect_relevant_context()` |
| 병합 | `build_context_bundle()`의 `source_code + existing_workflow` 중복 제거 |
| 정렬 | `_render_context_bundle()`의 8개 항목 렌더링 순서 |
| 표현(Prompt) | `_render_context_bundle()`이 만든 문자열을 `issue["description"]`에 덧붙임 |
| 경계 | 없음 — `[Relevant Context]` 마커 하나가 유일한 구분자 |

이것이 `BOUNDARY.md` 원칙 위반이었다고 이 RFC는 판단하지 않는다.
Kernel이 아직 없었으므로 다른 방법이 없었고, 그 사실은 EVIDENCE-REVIEW-0001에
이미 기록되어 있다. **이 RFC는 Development HQ의 코드·문서를 수정하지
않는다.**

### 6.3 통합의 방향 (제안이며 계획이 아니다)

```
Development HQ                    Kernel
──────────────                    ──────
Source 선언        ─────────────▶ Context Builder
Segment Content    ─────────────▶   (수집 → 검증 → 병합 → 정렬)
Ordering Policy 선택 ───────────▶ Context Assembly
                                     │
                                     ▼
                                  Kernel Context  (정본)
                                     │
                                     ▼  Renderer
                                  Prompt         (표현)
```

Development HQ는 Prompt를 만들지 않는다. Context에 무엇을 넣을지만
정한다.

### 6.4 활용 사례 — 목적이 아니라 결과 (KP-4)

RFC-0002 §12.1이 이미 고정한 인과 방향을 그대로 유지한다. 아래는
**설계 목표가 아니라, 위 구조가 성립하면 뒤따르는 결과**다. 이 RFC는
어느 것도 설계하지 않는다.

| 활용 사례 | 위 구조의 무엇을 쓰는가 | 관찰 여부 |
|---|---|---|
| Prompt Cache | Boundary 앞 구간이 호출 간 바이트 동일(4.5) | **관찰된 적 없음** |
| Conversation Resume | Boundary가 "재구성 가능 구간 / 복원 필요 구간"을 가름 | **관찰된 적 없음** |
| Context Snapshot | Context가 Identifier를 가진 불변 값(2.6) → 스냅샷 = 그 값을 보관 | **관찰된 적 없음** |
| Memory Restore | 복원 단위가 Segment로 이미 나뉘어 있음 | **관찰된 적 없음** (Memory Module은 Defer) |

**전제 조건을 명시한다**: 위 4개 중 어느 것도 이 저장소에서 관찰된
적이 없으며, 실제 Engine 호출이 한 번도 없었다. 따라서 K-5는 **방향
제안**이고, 실제 통합은 최소한 한 번의 실제 Engine 호출이 관찰된
뒤에 판단되어야 한다.

---

## 7. 아직 결정하지 않는 것

- 4-Layer Context Model(Immutable/Stable/Working/Ephemeral) —
  ADC-0002 판단 2b Defer **그대로 유지**한다.
- Context Identifier의 파생 규칙(호출자 주입 / 내용 해시 / 그 외).
- Boundary의 개수와 의미.
- Ordering Policy의 구체적 내용(어떤 Order Key 체계를 쓸 것인가).
- Context Builder / Context Assembly가 별도 Component인지, 같은
  Component의 두 단계인지.
- 직렬화 형식(JSON, 텍스트, 그 외).
- Compaction, 영속화, Memory.
- 어떤 Engine의 Renderer를 만들 것인지.
- Prompt Assembly Engine이라는 Component의 필요 여부.

---

## Out of Scope

- 구현. 이 RFC는 코드를 만들지 않고, 어떤 코드도 수정하지 않는다.
- Kernel Architecture 및 Component Design — `BASELINE.md` §10 Out of
  Scope 그대로.
- Development HQ의 문서·코드 수정.
- Execution Layer의 5개 Builder 수정 — 이 RFC는 그것을 **근거로만**
  인용하며, 재설계를 제안하지 않는다(단 §5.3 R-3은 향후 변경 제안으로
  표시했다).
- Prompt Engineering, 모델별 캐싱 메커니즘, TTL·Invalidation 정책.
- Memory / Compaction / Execution API — RFC-0002 §14의 이후 단계.

## Non-goals

- 이 RFC는 Prompt를 만들지 않는다.
- 이 RFC는 Kernel을 설계하지 않는다 — Model과 책임만 정의한다.
- 이 RFC는 §7 목록에 답하지 않는다.
- 이 RFC는 Baseline을 변경하지 않는다 — 반영 여부는 후속 ADC·ADR의
  몫이다.
- 이 RFC는 4-Layer Context Model의 Defer를 해제하지 않는다.

## Self Review

- Prompt를 만들었는가 — **아니오**. K-4는 Prompt를 Kernel Context의
  표현으로 **위치시켰을 뿐** 어떤 Prompt도 작성하지 않았다.
- 4-Layer Context Model을 확정했는가 — **아니오**. §2.5 제약 2, §2.7,
  §4.5, §7에서 네 번에 걸쳐 Defer 유지를 명시했다. 정렬(§3.2-4)과
  경계(§4.5)를 **계층 없이** 표현하는 방법(Policy 외부화, 위치 기반
  Boundary)을 택해 taxonomy 확정을 우회했다.
- 근거와 신규 제안을 구분했는가 — **Pass**. §2~§5의 각 항목에 "근거
  성격"(관찰된 사실 / 관찰된 사실의 일반화 / 신규)을 개별 표시했고,
  §4.5와 §5.3 R-3에는 근거가 약하거나 기존 구현과 다르다는 점을
  본문에 명시했다.
- Component를 만들었는가 — **아니오**. Builder·Assembly·Renderer는
  전부 **책임**으로만 기술했고, 어떤 Component가 구현할지는 §7에
  미결로 남겼다(KP-1).
- Engine 종속 요소가 Model에 들어갔는가 — **아니오**. §2.7이 role /
  token / cache key를 명시적으로 제외했고, §5.3 R-5가 그것들을
  Renderer 안에 가뒀다(KP-5).
- Kernel에 상태·시계·난수를 두었는가 — **아니오**. §2.4와 §4.2 A-4가
  KP-6을 그대로 따랐다.
- 기존 용어와 충돌하는가 — **부분적으로 그렇다. 기록했다.**
  `BASELINE.md` §6의 Context와 이름이 겹치므로, §2.8에서 "새 개념이
  아니라 구체화"임을 명시하고 용어 위험으로 기록했다.
- Development HQ를 수정했는가 — **아니오**. §6.2는 현재 상태를
  관찰로만 기록했다.
- Baseline을 변경했는가 — **아니오**.
