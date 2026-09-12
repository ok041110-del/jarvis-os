# ADR-0026: OpenRouter Free Model Selection — Architecture Boundary

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0026` |
| 상태 | **Accepted (Scoped) — Architecture Independence/Boundary 확정. Concrete API 구현(`openrouter/free`류 조합 등) 및 Stage 01~05 Production Routing 실통합은 이 ADR이 결정하지 않는다 — 둘 다 `NOT YET DETERMINED`로 명시적으로 유보한다(§9, §10).** |
| Context | `RFC-0040-openrouter-free-model-selection-architecture.md` → `ADC-0043-openrouter-free-model-selection-decision.md` → 이 ADR |
| 관련 RFC | `RFC-0040`(8단계 파이프라인·책임 경계 제안) |
| 관련 ADC | `ADC-0043`(Boundary 확정, Concrete API Adoption NOT DETERMINED) |
| 관련 Evidence | `docs/research/OPENROUTER-VALIDATION-0001.md`, `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md`, `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`, `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` |
| Governance Status 확인 | `ADR-0025`가 이미 확인한 대로, 이 저장소의 모든 ADR Status는 "Accepted"(Scoped 등 수식어 동반) 계열뿐이며 "Proposed"/"NOT DETERMINED" 상태의 ADR 선례는 없다. 이 ADR도 `ADR-0025`와 동일한 패턴을 따른다 — **부분적으로 확정된 사실(책임 경계/Boundary)** 만 Scoped Accept로 기록하고, 나머지(Concrete API 구현, Production Routing 통합)는 ADC 수준의 NOT YET DETERMINED로 유지한다. 새 상태명을 만들지 않는다. |

---

## 1. Context

Stage 01~05는 지금까지 검증 세션마다 특정 OpenRouter free 모델명을
하드코딩해 테스트해왔다(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`).
이 방식은 무료 모델의 가용성 변동에 취약함이 실측으로 이미 드러났다
(Stage01 최초 후보였던 Gemma가 33% 가용성만 보여 재선정이 필요했던
사례). `RFC-0040`은 이 문제를 "Stage 코드에 모델명을 고정하지 않고,
후보 축소까지만 Jarvis가 담당하고 최종 선택은 OpenRouter에 위임한다"는
책임 경계로 재구성했다. `ADC-0043`이 이 경계를 확정했으나 Concrete
API 구현·Production 통합은 Real Adoption Evidence 부재로 NOT
DETERMINED로 유보했다. 이 ADR은 그 위에서 무엇이 지금 확정 가능하고
무엇이 여전히 유보돼야 하는지를 공식화한다.

## 2. Problem

OpenRouter Free Model을 Stage가 쓰도록 만들려면 최소한 다음 질문에
답해야 한다: (1) 후보를 누가 어떻게 좁히는가, (2) 최종 선택 권한을
누가 갖는가, (3) 이것이 `ADR-0024`가 이미 거부한 Central Router
패턴이 되지 않는가, (4) 실제로 이 경로가 Production에서 신뢰성 있게
동작하는가. (1)~(3)은 추론으로 답할 수 있는 책임 경계 질문이지만,
(4)는 실제 API 조합과 반복 실행 결과가 있어야만 답할 수 있는 질문
이다 — 이 둘을 섞으면 근거 없는 (4)의 답이 근거 있는 (1)~(3)의 답까지
오염시킨다.

## 3. Existing Evidence

| 출처 | 확인한 것 |
|---|---|
| `OPENROUTER-VALIDATION-0001.md` | OpenRouter 연결·Egress Proxy 자동 인증 자체의 실측 검증 |
| `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` | Stage별 고정 모델 선정의 가용성 취약점(Stage01 재선정 사례) |
| `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` §6 | `models[]` 3개 상한이 **API-level limit**임을 독립 재구현(SDK 미사용, 기존 harness 코드 미재사용)으로 재현·확정. quota 소진 상태에서도 4개 이상 요청이 즉시 400으로 거부돼 "우연한 rate limit"이 아님을 확인 |
| `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` | Stage 01~05에 대해 `models[]` 기반 실행을 15회 실측 — 파이프라인이 구조적으로 동작 가능함을 보여준 참고 사례. 단 Stage05 Review는 Fixture 결함으로 Decision이 B(PARTIAL)에 그침 — 이 ADR은 이 실험을 "채택 근거"로 재사용하지 않는다(§9) |
| `ADR-0024` §Alternatives Option D | Central Engine Router를 명시적으로 거부한 선례 — 이 ADR이 제안하는 Candidate Selection이 이 패턴과 다름을 증명해야 하는 기준선 |

## 4. Architectural Options

### A. Stage별 고정 모델명(현행 검증 방식의 연장)

장점: 지금까지 Evidence 축적에 실제로 쓰임. 단점: 무료 모델 가용성
변동에 취약함이 실측으로 확인됨(§3).

### B. `openrouter/auto` 사용

무료 티어에서 지원되지 않는다(HTTP 402, `OPENROUTER-AUTO-SELECTION-
V1-VALIDATION-0001.md` §5) — 애초에 선택지가 아니다.

### C. Free Pool → Deterministic Filter → ≤3 Candidate → OpenRouter Delegation(채택안)

Jarvis 책임을 "명백히 판정 가능한 후보 축소"까지로 제한하고, 실제
선택은 OpenRouter의 실측 지원 메커니즘(`models[]`)에 위임한다. 장점:
모델명 고정 없음, Jarvis 쪽 Scoring Engine 불필요, 최대 3개 제한이
실측 Evidence에 근거. 단점: Concrete API 조합·Production 통합 검증이
아직 없음(§9, §10).

### D. Jarvis 자체 Scoring/Ranking Engine(참고, 배제)

`RFC-0040` §Rejected Alternatives가 이미 배제 — 복잡한 자체 Router,
품질 추정 로직 필요 — 채택하지 않는다.

## 5. Responsibility Boundary Decision

**확정한다(Scoped Accept)**: `RFC-0040`/`ADC-0043`의 책임 경계표를
이 ADR의 Architecture Boundary로 그대로 채택한다.

| 단계 | 소유자 |
|---|---|
| Stage Requirement | Stage(capability/context/input-output/Contract 선언, 모델명 없음) |
| Free Model Pool | Jarvis Candidate Selection(OpenRouter `:free` 목록 조회) |
| Deterministic Candidate Filter | Jarvis Candidate Selection(명백히 판정 가능한 compatibility만) |
| Candidate Selection (≤ 3) | Jarvis Candidate Selection(순위화 없이 상한 이하로 축소) |
| OpenRouter `models[]` | Jarvis 호출부(후보 목록 전달만) |
| OpenRouter Model Selection / Fallback | **OpenRouter**(실제 선택·availability·failover 전권) |
| Stage Execution | Stage/Engine 호출부 |
| Contract Validation | Contract Validation(모델 선택과 독립, 품질 추측 없음) |

## 6. Free Pool / Deterministic Filtering / Maximum 3 Decision

**확정한다**:

- **Free Pool 기반**: 후보는 OpenRouter가 실제로 제공하는 `:free`
  목록에서만 나온다 — Jarvis가 임의로 모델을 추가하거나 가정하지
  않는다.
- **Deterministic filtering**: 후보 축소는 Free 여부, Stage hard
  requirement, Contract compatibility, context/modality 등 명백히
  판정 가능한 사실만으로 이뤄진다 — 품질/성능 추정 기준은 이 경계에
  속하지 않는다.
- **Maximum 3 candidates**: `OPENROUTER-MODELS-ARRAY-LIMIT-
  REVERIFICATION-0001.md` §6이 확정한 API-level limit을 Architecture
  불변조건으로 그대로 승격한다 — Jarvis가 임의로 정한 값이 아니다.

## 7. OpenRouter Delegation Decision

**확정한다**: 전달받은 후보 중 실제로 어떤 모델을 쓸지, provider
가용성 문제가 있을 때 어떻게 failover할지는 전적으로 OpenRouter의
책임이다. Jarvis는 이 내부 알고리즘을 알 필요가 없고, 이를 재현하는
로직을 만들지 않는다.

## 8. Central Router 오독 방지 — 명시적 구분

**확정한다**: 이 Architecture의 Candidate Selection은 `ADR-0024`
§Alternatives Option D(Central Engine Router, 명시적으로 배제됨)와
**다르다**. 근거:

- 최종 선택 권한을 갖지 않는다(그 권한은 OpenRouter에 있다) — Router는
  최종 선택 권한을 갖는 계층이다.
- 여러 Engine(ChatGPT/Claude Code/OpenRouter) 사이의 런타임 선택을
  하지 않는다 — `ADR-0024`가 확정한 2-Engine 정적 구조(Option C)를
  그대로 유지하며, 이 ADR은 그 구조를 바꾸지 않는다. 이 Architecture는
  **OpenRouter라는 하나의 실험적 Engine 내부**에서 free 모델 후보를
  줄이는 필터일 뿐이다.
- 단순 결정적 필터링만 수행하며, 조건부 fallback·재선택 같은 런타임
  provider 재선택 계층을 신설하지 않는다(`IMPLEMENTATION_RULES.md`
  16·21행 Gateway 금지 조항과 충돌하지 않음).

## 9. Concrete API Implementation Decision Status

**NOT YET DETERMINED.**

- `openrouter/free`류 구체적 파라미터 조합의 실제 채택 여부는 이
  ADR이 확정하지 않는다(`RFC-0040` §Non-Goals 원칙 5, 6을 그대로
  승계) — 별도 Experiment에서 검증한다.
- `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`가 `models[]`
  기반 실행을 15회 실측했으나, Stage05 Review 부분은 Fixture 결함
  (placeholder 텍스트가 실제 Stage04 산출물을 대체)으로 Decision이
  B(PARTIAL)에 그쳤다 — 이 ADR은 이 실험 결과를 "Concrete API 구현이
  검증됐다"는 근거로 소급 인용하지 않는다(`ADC-0043` §Validation
  Requirements 2번과 동일 원칙).
- Deterministic Candidate Filter의 구체적 판정 규칙 전체 목록(어떤
  메타데이터 필드를 어떤 기준으로 볼지)도 이 ADR이 확정하지 않는다.

## 10. Production Routing Integration Decision Status

**NOT YET DETERMINED.**

- 이 ADR이 확정한 것은 "이런 책임 경계로 설계해야 한다"는 구조뿐이다
  — Stage 01~05의 실제 코드가 이 경로로 OpenRouter를 호출하도록
  바꾸는 것은 별개의 결정이다.
- OpenRouter는 지금까지 Production Stage Engine Routing에 편입된
  적이 없고, "실험적 검증 endpoint"로만 다뤄져 왔다(`ADR-0024`가
  확정한 ChatGPT/Claude Code 2-Engine 구조가 Production을 담당) — 이
  ADR은 이 구분을 바꾸지 않는다.
- 설령 §9의 Concrete API 구현이 검증되더라도, 이를 실제 Production
  Routing에 편입할지는 `ADR-0024`와의 관계를 포함한 별도 Governance
  판단이 필요하다(`ADC-0043` §Validation Requirements 5번).

## 11. Consequences

- OpenRouter Free Model Selection의 책임 경계(Free Pool/Deterministic
  Filter/≤3 Candidate/OpenRouter Delegation/Contract Validation 독립성)
  판단은 이제 이 ADR을 Single Source of Truth로 인용할 수 있다 —
  향후 세션이 이 경계를 처음부터 재조사할 필요가 없다.
- Concrete API 구현과 Production Routing 통합은 여전히 열려 있다 —
  이 ADR을 "OpenRouter가 Stage 01~05에 실제로 연결됐다"는 근거로
  인용해서는 안 된다.
- `projects/openrouter-auto-selection-v1/`이 §9의 후속 Concrete API
  실험을 위한 재사용 가능한 도구로 남는다.
- Production `hqs/development/stages/`, `ADR-0024`가 확정한 2-Engine
  Routing은 전부 무변경 — 이 ADR은 그 자체로 어떤 Production 동작도
  바꾸지 않는다.

## 12. Non-Goals

- Stage 01~05 Production 코드/routing을 변경하는 것 — 하지 않음.
- Jarvis 자체 Model Router/Scoring Engine을 만드는 것 — 하지 않음
  (§8에서 Central Router와의 구분을 명시적으로 확정).
- 특정 모델명, 특정 Stage-모델 매핑을 확정하는 것 — 하지 않음.
- `openrouter/free`류 구체적 API 조합을 확정하는 것 — 하지 않음
  (§9, 별도 Experiment 영역).
- Contract를 변경하는 것 — 하지 않음(모델 선택 경로와 독립적으로
  유지).
- `ADR-0024`가 확정한 ChatGPT/Claude Code 2-Engine 정적 구조를
  재론하거나 수정하는 것 — 하지 않음.
- 기존 RFC(`RFC-0040`)/ADC(`ADC-0043`)를 수정하거나 완료 처리하지
  않는다 — 그대로 Related로만 인용한다.

---

## Self Review

- 현재 검증 방식(고정 모델명)을 Architecture 기준으로 삼았는가 —
  **아니오**(`RFC-0040`의 책임 경계 제안을 그대로 인용, 이 ADR도
  재론하지 않음).
- Concrete API 구현을 확정했는가 — **아니오**(§9, NOT YET DETERMINED로
  명시, Stage05 Fixture 결함을 숨기지 않고 재확인).
- Production Routing 통합을 확정했는가 — **아니오**(§10, NOT YET
  DETERMINED — `ADR-0024`의 2-Engine 구조가 여전히 Production을
  담당함을 명시).
- Central Router로 해석될 여지를 남겼는가 — **아니오**(§8, `ADR-0024`
  Option D와의 구조적 차이를 항목별로 명시).
- "Auto Selection이 더 안정적이다/빠르다/모델을 더 잘 고른다"를
  주장했는가 — **아니오**(§9 — 오히려 기존 실험의 Fixture 결함을
  그대로 재인용해 과장을 방지).
- 임의의 ADR 상태명을 만들었는가 — **아니오**(§Governance Status
  확인 — `ADR-0025`와 동일하게 기존 "Accepted(Scoped)" 어휘만 재사용).
- 기존 RFC/ADC/ADR을 임의로 수정하거나 완료 처리했는가 — **아니오**
  (`RFC-0040`/`ADC-0043` 본문 무수정, Related로만 인용).
- API Key/Credential을 탐색하거나 출력했는가 — **아니오**(이 ADR
  자체가 어떤 실행도 수행하지 않는다 — 순수 문서 작업).
- Production 코드를 변경했는가 — **아니오**(변경 범위는 이 ADR +
  `RFC-0040` + `ADC-0043` 문서 3건뿐).

## Related

- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`
- `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`(Central
  Router 명시적 거부 선례, Option D — §8이 직접 대조)
- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`(Boundary
  Accepted / Production Adoption NOT YET DETERMINED 분리 기록 선례,
  동일 패턴)
- `docs/research/OPENROUTER-VALIDATION-0001.md`
- `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md`
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`
- `projects/openrouter-auto-selection-v1/`(이 ADR이 인용하는 실측 Harness)
