# RFC-0002: Kernel Definition — Responsibility, Not Component

**Status**: Resolved — `ADC-0002.md` → `ADR-0002`로 종결됨(STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Version**: Draft
**Author**: Claude Code (Kernel Definition Discussion → RFC 전환)
**관련 문서**: `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`,
`docs/architecture/core/ADC-0001-core-baseline.md`,
`docs/governance/adc/ADC-0001.md`(Dev HQ, Kernel Extraction Candidate),
`docs/governance/adc/ADC-0004.md`(Dev HQ, Task Dispatcher 재판단),
`development-hq/BOUNDARY.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md`
(Kernel Readiness Assessment)

> 본 RFC는 Kernel의 구현을 정의하지 않는다. Kernel의 책임만 정의한다.
> Scheduler/Registry/Runtime/Memory/Event Bus/Engine Gateway가
> 필요한지는 이 RFC의 범위가 아니다. 이 RFC는 Kernel을 설계하지
> 않는다.

---

## 0. Terminology — "Kernel"과 "Core"의 통합 (Proposal)

이 RFC는 지금까지 두 갈래로 쓰여온 용어를 하나로 통합할 것을
**제안**한다.

- Development HQ 수준 문서(`development-hq/BOUNDARY.md`,
  Dev HQ `RFC-0001`~`RFC-0004`, `docs/governance/adc/ADC-0001`~`0004`)
  는 처음부터 **"Kernel"**을 사용해 왔다 — `BOUNDARY.md`는 Task 실행
  메커니즘, Engine 호출, Capability 색인·탐색, Policy 판정, HQ
  생명주기 관리, 자원·예산 배분을 모두 "Kernel Scheduler",
  "Kernel Engine Port/Adapter", "Kernel Registry" 등으로 이미 명시해
  두었다.
- 이번 Jarvis OS Core 수준 작업(`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`,
  `ADC-0001-core-baseline.md`)에서는 동일한 개념을 **"Core"**라는
  이름으로 다시 도입했다. 이는 새 개념이 아니라, `BOUNDARY.md`가 이미
  "Kernel"이라고 부른 것과 같은 자리(모든 HQ가 공유하는 공통 계층)를
  가리킨 것이었다.
- 따라서 이 RFC는 **"Kernel"을 공식 용어(Canonical Term)로 확정할
  것을 제안한다** — 이것은 새 병렬 개념을 만드는 것이 아니라, 원래
  `BOUNDARY.md`가 쓰던 용어로 되돌아가 하나로 정리하는 것이다.

**이 통합의 절차적 위치**: 이 RFC는 Proposal일 뿐, Decision이
아니다. 이미 커밋된 문서(`RFC-0001-jarvis-os-core-baseline.md`,
`ADC-0001-core-baseline.md` 등)의 실제 텍스트는 이 RFC가 직접
수정하지 않는다 — `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
절차(`RFC → ADC → ADR → Baseline Update`)에 따라, 이 용어 통합이
실제로 기존 문서에 반영되려면 후속 ADC와 ADR이 필요하다. 이 RFC는 그
절차의 첫 단계일 뿐이다.

이 RFC 승인 이후 작성되는 모든 신규 문서는 "Kernel"을 사용한다. 기존
문서의 "Core"는, 별도의 의미 차이가 명시되지 않는 한, 이 RFC가
정의하는 "Kernel"과 동일한 것으로 읽는다.

---

## 1. 목적

Kernel의 구현을 정의하지 않는다. Kernel의 책임을 정의한다.

## 2. 질문

Kernel은 무엇인가?

## 3. 잘못된 정의 (Non-Definitions)

- Kernel은 Scheduler이다.
- Kernel은 Registry이다.
- Kernel은 Runtime이다.
- Kernel은 Event Bus이다.
- Kernel은 Memory이다.
- Kernel은 Engine Gateway이다.

위 정의는 모두 구현(Component)을 Kernel과 동일시한다. **Kernel은
특정 Component가 아니다.**

## 4. Evidence — Development HQ MVP-0001 관찰

`docs/governance/adc/ADC-0001.md`(Kernel Extraction Candidate 승격
판단)는 MVP-0001이 다음 4개 후보를 모두 하드코딩·최소 구현으로 채운
채 끝까지 동작했다는 사실을 이미 기록해 두었다 — "승격을 정당화할
반복 사용 사례나 일반화 압력이 MVP 안에서 관찰되지 않았다"(4건 모두
Keep in MVP).

- Task Dispatcher(Scheduler에 해당) 없이 동작했다 — 두 줄의 하드코딩된
  순차 호출로 충분했다.
- Agent Registry 없이 동작했다 — 리터럴 딕셔너리로 충분했다.
- Engine Gateway 없이 동작했다 — 단일 함수 호출로 충분했다.
- Context 전달 메커니즘(Memory Service에 해당) 없이 동작했다 —
  지역 변수 전달로 충분했다.

`docs/governance/adc/ADC-0004.md`는 MVP-0004까지 세 번째 체인이
늘어난 뒤에도 동일한 결론(Keep in MVP)을 재확인했다. 즉, 위
Component들은 **Kernel의 정의가 아니다** — Kernel 없이도(그 Component
들 없이도) MVP는 실제로 동작했다.

## 5. MVP에서 반복 관찰된 책임

MVP는 다음 책임을 반복적으로 드러냈다(Dev HQ MVP-0001~0013,
`docs/research/EVIDENCE-REVIEW-0001.md`에 걸쳐 반복 관찰됨).

- Task를 다음 Task로 전달해야 한다.
- Capability를 찾아야 한다.
- Engine을 호출해야 한다.
- Context를 전달해야 한다.

그러나 `development-hq/BOUNDARY.md`는 이 책임들을 "Development HQ가
절대 책임지지 않는 것"으로 이미 명시했다 — Development HQ는 이 책임을
가져서는 안 된다. `docs/01_architecture/BASELINE.md` §3의 "Composable
HQ"("새로운 HQ는 기존 Architecture를 재사용하여 생성할 수 있어야
한다")와 §4의 "Reference Architecture"(첫 HQ가 이후 모든 HQ의 기준
구조가 되어야 한다) 원칙에 따르면, 아직 존재하지 않는 Personal HQ나
Research HQ에도 이 책임 배제는 동일하게 적용되어야 한다 — 이는 아직
관찰되지 않은 가설적 확장이며, 이 RFC는 그 확장 자체를 실증하지
않는다.

## 6. 공통점

모든 HQ는 동일한 종류의 책임을 반복한다. 도메인은 다르지만 책임은
동일하다.

## 7. 가설

Kernel은 모든 HQ가 공통으로 필요로 하지만 어느 HQ에도 속하지 않는
책임을 담당하는 계층이다.

## 8. Kernel의 정의

Kernel은 Component가 아니다.
Kernel은 Framework가 아니다.
Kernel은 Runtime이 아니다.
Kernel은 Scheduler가 아니다.
Kernel은 Registry가 아니다.
Kernel은 Event Bus가 아니다.

**Kernel은 공통 책임(Common Responsibility)을 담당하는 계층이다.**

## 9. Kernel과 Component

Kernel은 책임을 가진다. Component는 그 책임을 구현하는 방법이다.

| Kernel 책임 | 구현 후보(예시일 뿐, 채택 여부 결정 아님) |
|---|---|
| Task 전달 책임 | Scheduler |
| Capability 탐색 책임 | Registry |
| Engine 호출 책임 | Engine Gateway |
| Context 전달 책임 | Memory |

## 10. 중요한 원칙

Kernel은 구현으로 정의하지 않는다. 책임으로 정의한다.

---

## 11. Kernel Design Principles

Kernel의 상위 설계 원칙(KP-n)을 정의한다. 이 원칙들은 앞으로
Development HQ, Runtime, Memory, Agent 등 **모든 하위 설계가 공통으로
참조하는 최상위 설계 원칙**으로 사용할 것을 제안한다.

각 원칙마다 그 원칙이 (a) 이미 관찰·확정된 사실에서 도출된 것인지,
(b) 이번 RFC가 새로 도입하는 것인지를 표시한다 — 이 프로젝트가
지켜온 "관찰된 사실과 새 제안을 구분한다"는 원칙을 그대로 적용한다.

### KP-1. Responsibility over Component

Kernel은 구현 객체가 아니라 **책임 경계(Responsibility Boundary)**다.

*근거(기존 사실)*: §4의 MVP-0001 관찰 —
Scheduler/Registry/Runtime/Memory/Event Bus 없이도 MVP는 동작했다.
`docs/governance/adc/ADC-0001.md`·`ADC-0004.md`가 4개 Candidate를
모두 "Keep in MVP"로 판단한 것이 이 원칙의 실증이다. §10과 동일한
진술이며, KP-1은 그것을 원칙 번호로 승격한 것이다.

### KP-2. Deterministic Context Assembly

동일한 입력은 항상 동일한 Context를 구성해야 한다.

*근거(기존 사실)*: Execution Layer MVP-0001~0005의 5개 Builder 전부가
Deterministic Transformation을 만족함이 각 MVP의
`test_transformation_is_deterministic`/`test_rendering_is_deterministic`
으로 실측 확인되었고, `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`
가 이를 5개 Artifact 전부의 Contract로 이미 고정했다. KP-2는 그
성질을 Execution Layer에 국한하지 않고 Kernel 전체 원칙으로 일반화한
것이다.

### KP-3. Stable Context Ordering

Context는 항상 동일한 순서로 조립되어야 한다.

*근거(부분적 기존 사실) + 신규 일반화*: 고정된 순서로 조립한다는
실천 자체는 이미 존재하고 검증되었다 — Execution Layer MVP-0002는
고정 배치표(`RENDERING_MAP`)로 절 순서를 고정했고, 그 결과 서로 다른
두 Case에서 구조 오버헤드가 정확히 동일(77 글자)했음이 실측되었다
(`docs/core/execution-layer/MVP-0002-artifact-mapping.md`). 다만 그
실천은 단일 문자열 Artifact 안에서의 절 순서였을 뿐이며(`EVIDENCE-
REVIEW-0001.md` "Context 전달 방식": MVP-0005~0008 네 건 모두 단일
경로만 사용), **계층화된 Context 간의 순서 보장은 관찰된 적이 없다.**
KP-3에서 신규인 부분은 이 계층 간 순서로의 일반화다.

### KP-4. Stable Context by Design

> Kernel is designed to produce deterministic, stable, and reusable
> context structures. Optimizations such as prompt caching are
> consequences of this design, not its objective.

Kernel은 **결정론적이고 안정적이며 재사용 가능한 Context 구조를
만들어내도록** 설계된다. Prompt Caching과 같은 최적화는 그 설계의
**결과이지 목적이 아니다.**

*인과 방향(명시)*: 다음 방향만 성립한다.

```
안정적인 Context 구조를 설계한다   (목적)
            ↓  그 결과로
Prompt Cache 등 최적화가 가능해진다 (결과)
```

역방향 — "Prompt Cache를 쓰기 위해 Kernel을 이렇게 설계한다" — 은
성립하지 않는다. 특정 벤더의 캐싱 기능이 사라지거나 바뀌어도 이
원칙과 그로부터 나온 구조는 그대로 유효해야 한다(KP-5와 동일한
방향).

*성격(신규)*: 이번 RFC가 새로 도입하는 원칙이다. 다만 이 원칙이
요구하는 것은 "안정적인 Context 구조"뿐이며, 특정 최적화 기능을 위해
무언가를 구현할 것을 요구하지 않는다(§12 참조).

### KP-5. Implementation Agnostic

Kernel은 특정 모델(Claude, GPT, Gemini 등)이나 특정 Runtime에
종속되지 않는다.

*근거(기존 사실)*: `docs/01_architecture/BASELINE.md` §3의 "Engine
Independent"·"Everything is Replaceable" 원칙이 v1.0부터 Frozen
상태다. Execution Layer MVP-0003은 이를 실제 코드로 지켰다 —
`target_engine`을 고정 placeholder(`"unresolved"`)로 두고, 메타데이터
어디에도 실제 모델명이 나타나지 않음을 테스트로 검증했다.

### KP-6. Stateless Responsibility Boundary

Kernel은 책임을 정의하지만, 특정 구현체의 내부 상태를 강제하지 않는다.

*근거(기존 사실)*: `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`
§6이 이미 "Stateless Interface"를 Design Principle로 명시했다.
Execution Layer MVP-0003~0005는 이를 실제로 지켰다 — `request_id`,
`created_at`, `handle_id`, `submitted_at`, `state`, `changed_at`을
Builder 내부에서 생성하지 않고 전부 호출자 주입으로 남겨, 시계·난수·
상태 결정 로직을 Kernel 쪽 코드에 두지 않았다.

---

## 12. Kernel Context Architecture

**이 절은 §4~§9와 성격이 다르다.** §4~§9는 과거 MVP Observation에서
직접 도출된 결론이다. 이 절은 그렇지 않다 — 과거 MVP는 실제 Model을
한 번도 호출하지 않았으므로(RFC-0005 §1: "MVP-0005~0013 전 구간에서
LLM/ML 호출은 한 번도 추가되지 않았다"), Context 계층화에 대한 직접
Observation은 존재하지 않는다. 이 절은 이번 RFC가 **새로 도입하는
Architecture 원칙**이며, 그렇게 정직하게 표시한다.

### 12.1 이 Architecture가 무엇을 위한 것인가

Kernel Context Architecture는 **안정적인 Context를 구성하기 위한
일반적인 아키텍처 원칙**이다. 특정 벤더의 특정 최적화 기능을 위해
존재하지 않는다.

```
Kernel Context Architecture        (KP-4: Stable Context by Design)
        ↓
Stable Context Ordering            (KP-3)
        ↓
활용 사례
  ├─ Prompt Cache                  (첫 번째 사례)
  ├─ Conversation Resume
  ├─ Context Snapshot
  ├─ Memory Restore
  └─ Future Runtime Optimization
```

이 방향은 한쪽으로만 성립한다(KP-4). Architecture가 위에 있고 활용
사례가 아래에 있다 — 활용 사례가 Architecture의 형태를 결정하지
않는다.

Prompt Caching은 이 원칙을 활용하는 **첫 번째 사례일 뿐이다.**
동일한 구조 — Context가 계층으로 나뉘고, 계층 간 순서가 항상 같으며,
어디까지가 안정적이고 어디부터 매번 바뀌는지 경계가 명시된 구조 —
는 다음에도 그대로 활용된다.

| 활용 사례 | 이 구조를 어떻게 쓰는가 |
|---|---|
| Prompt Cache | 안정적인 앞부분(Immutable/Stable)이 매 호출 동일하므로 캐시 재사용이 가능해진다 |
| Conversation Resume | 어디까지가 재구성 가능한 안정 영역이고 어디부터 복원해야 하는지 구분된다 |
| Context Snapshot | 특정 시점의 Context를 계층 단위로 떠낼 수 있다 |
| Memory Restore | 어느 계층을 복원 대상으로 삼을지 경계가 이미 정의되어 있다 |
| Future Runtime Optimization | 아직 알려지지 않은 최적화도 "안정 영역/가변 영역" 구분 위에서 설계할 수 있다 |

**따라서 Kernel은 Claude의 Prompt Cache를 위해 존재하지 않는다.**
Kernel은 모델·벤더에 독립적인 Context 관리 계층이며(KP-5), Prompt
Cache는 그 계층이 제공하는 안정성 덕분에 가능해지는 여러 결과 중
하나다(KP-4).

### 12.2 Context Layer (4단계)

| Layer | 정의 |
|---|---|
| Immutable | 절대 바뀌지 않는 Context(예: System Prompt, Kernel/HQ 정의 자체) |
| Stable | 세션/Task 단위로는 바뀌지 않는 Context(예: HQ Capability 목록, 현재 Workflow 정의) |
| Working | Task 실행 중 누적되는 Context(예: 지금까지의 Tool 호출 결과) |
| Ephemeral | 이번 호출 한 번만 유효한 Context(예: 지금 이 순간의 사용자 입력) |

### 12.3 Kernel이 보장해야 할 책임(구현 방법은 규정하지 않음)

- **Stable Prefix** — Immutable/Stable Layer가 항상 앞쪽에서 동일한
  순서·내용으로 유지되도록 보장하는 책임.
- **Context Boundary** — 어느 지점까지가 안정 영역이고 어디부터
  매번 바뀌는 영역인지 경계를 명시적으로 구분하는 책임. (Prompt
  Cache 관점에서는 이것이 곧 Cache Boundary가 되지만, 경계 자체는
  캐시 전용 개념이 아니다 — Snapshot·Resume·Restore도 같은 경계를
  사용한다.)
- **Context Assembly** — Immutable/Stable/Working/Ephemeral 4개
  Layer를 실제 실행 입력으로 조립하는 책임. (모델 호출의 경우
  Prompt Assembly가 이 책임의 한 형태다.)
- **Context Ordering** — Layer 간 순서(Immutable → Stable → Working
  → Ephemeral)를 일관되게 유지하는 책임(KP-3).

이 4개는 §10·KP-1의 원칙을 그대로 따라 **책임으로만** 명시한다. 어떤
Component(예: Prompt Assembly Engine)가 이를 실제로 구현할지, 어떤
모델의 어떤 캐싱 메커니즘을 쓸지는 이 RFC가 결정하지 않는다.

---

## 13. 아직 결정하지 않는 것

- Scheduler가 필요한가?
- Registry가 필요한가?
- Runtime이 필요한가?
- Memory가 필요한가?
- Event Bus가 필요한가?
- Engine Gateway가 필요한가?
- Prompt Assembly Engine이 필요한가?
- Compaction 전략은 무엇인가?

이 질문들은 Kernel Definition의 범위가 아니다.

---

## 14. Roadmap (제안, 결정 아님)

Kernel 정의 단계 이후, 다음 순서를 제안한다. 순서 제안일 뿐이며, 각
단계 자체를 이 RFC가 미리 설계하지 않는다.

```
Kernel Definition (본 RFC)
↓
Kernel Core 정의
↓
Kernel Context Model
↓
Kernel Context Architecture (신규)
↓
Prompt Assembly Engine
↓
Memory / Compaction
↓
Execution API
```

각 단계가 다루는 범위(이름이 겹쳐 보이는 단계를 구분하기 위한
최소 설명이며, 각 단계의 내용을 여기서 미리 설계하지 않는다):

| 단계 | 다루는 범위 |
|---|---|
| Kernel Core 정의 | §15가 나열한 8개 책임이 각각 Kernel에 속하는지 하나씩 판단 |
| Kernel Context Model | Context가 **무엇으로 구성되는가**(§12.2의 4개 Layer를 실제 Model로 확정) |
| Kernel Context Architecture | Context가 **어떻게 조립·정렬·경계 지어지는가**(§12.1·§12.3, KP-3·KP-4를 Architecture로 확정). 특정 모델·벤더에 종속되지 않으며, Prompt Cache는 그 위에서 가능해지는 활용 사례 중 하나다(§12.1) |
| Prompt Assembly Engine | 위 책임을 실제로 수행할 Component(필요 여부 자체가 아직 미결) |
| Memory / Compaction | Working Layer가 무한히 커질 때의 처리 |
| Execution API | 위 전부가 외부에 노출되는 Interface |

각 단계는 §10·KP-1의 원칙("책임으로 정의, 구현으로 정의하지 않는다")을
그대로 따라 별도 RFC로 진행된다.

## 15. 다음 단계

Kernel Definition(본 RFC)이 승인되면, 다음 각 책임이 Kernel에
속하는지 아닌지를 RFC를 통해 하나씩 판단한다.

1. Task 전달 책임
2. Capability 탐색 책임
3. Engine 호출 책임
4. Context 전달 책임
5. Stable Prefix 책임(§12.3)
6. Context Boundary 책임(§12.3)
7. Context Assembly 책임(§12.3)
8. Context Ordering 책임(§12.3)

그리고 §11의 Kernel Design Principles(KP-1~KP-6)를 모든 하위 설계의
최상위 참조 원칙으로 채택할지 여부도 ADC 판단 대상이다 — 이 RFC는
그것을 제안만 한다.

그리고 §0의 Terminology Proposal("Kernel"을 공식 용어로 통합)이
실제로 기존 문서(`RFC-0001-jarvis-os-core-baseline.md`,
`ADC-0001-core-baseline.md` 등)에 반영되려면, 이 RFC에 대한 ADC 판단
이후 별도 ADR이 필요하다.

---

## Out of Scope

- Scheduler, Registry, Runtime, Memory, Event Bus, Engine Gateway,
  Prompt Assembly Engine의 구현 또는 상세 설계.
- Prompt Caching의 실제 구현 방법(특정 모델의 특정 캐싱 메커니즘,
  TTL, Invalidation 정책 등).
- §12.1이 나열한 다른 활용 사례(Conversation Resume, Context
  Snapshot, Memory Restore, Future Runtime Optimization)의 설계 —
  이 RFC는 그 사례들이 동일한 Context 구조를 활용할 수 있다는 점만
  기록하고, 각각을 설계하지 않는다.
- "Kernel"/"Core" 용어 통합의 최종 확정 — 이는 후속 ADC/ADR의 몫이다.
- Development HQ의 어떤 코드·문서 수정.

## Non-goals

- 이 RFC는 Kernel을 설계하지 않는다.
- 이 RFC는 위 "아직 결정하지 않는 것"(§13) 목록에 답하지 않는다.
- 이 RFC는 Architecture Baseline이나 Kernel Baseline 문서를 변경하지
  않는다 — 기존 문서의 실제 텍스트는 그대로 둔다.
- 이 RFC는 §12의 Context Architecture를 구현하지 않는다 — 책임만
  명시한다.
- 이 RFC는 KP-1~KP-6을 확정하지 않는다 — 최상위 원칙으로 채택할지는
  후속 ADC의 몫이다.
- 이 RFC는 Development HQ를 수정하지 않는다.

## Self Review

- Kernel을 구현/설계했는가 — **아니오**. 책임만 정의했다.
- Evidence와 신규 제안을 구분했는가 — **Pass**. §4~§10은 MVP
  Observation 근거임을 밝혔고, §11의 6개 원칙은 각각 "근거(기존
  사실)"/"성격(신규)"으로 개별 표시했으며, §12는 신규 도입 원칙임을
  절 서두에 명시했다.
- Component를 Kernel과 동일시했는가 — **아니오**. §9의 표는 "예시일
  뿐, 채택 여부 결정 아님"으로 명시했다.
- Context Architecture가 특정 벤더 기능에 종속되어 읽히는가 —
  **아니오**. §12.1이 Prompt Cache를 5개 활용 사례 중 하나로만
  배치했고, KP-4가 인과 방향(Cache가 목적이 아니라 결과)을 명시했다.
- Baseline을 변경했는가 — **아니오**. 기존 문서 텍스트를 수정하지
  않았다. 용어 통합은 Proposal로만 남겼다.
- Development HQ를 수정했는가 — **아니오**.
- "아직 결정하지 않는 것"에 답했는가 — **아니오**.
