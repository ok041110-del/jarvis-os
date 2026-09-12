# ADC-0043: OpenRouter Free Model Selection — Decision (RFC-0040 후속)

## 목적

`RFC-0040-openrouter-free-model-selection-architecture.md`가 제안한
"Free Pool → Deterministic Filter → ≤3 Candidate → OpenRouter
delegation" 책임 경계를 Architecture로 확정할지 공식 Decision을
내린다. `ADC-0042`(Independence 확정 / Production 채택 보류)와 동일한
분리 판정 구조를 따른다.

---

## Q1. 책임 경계 자체는 충분히 근거가 있는가

**예.** `RFC-0040`의 8단계 파이프라인은 코드 실행 결과가 아니라
"누가 어떤 판단을 내리는가"라는 책임의 본질로 도출됐고, 각 단계의
소유자(Stage/Jarvis Candidate Selection/OpenRouter/Contract
Validation)가 서로 중첩되지 않는다(§Responsibility Boundary). 이는
추론만으로 완결 가능한 질문이며, 실제 Production 통합 없이도 답할
수 있다.

## Q2. 최대 3개 제한은 추정이 아니라 실측 근거를 갖는가

**예.** `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` §6이
독립 재구현(기존 harness 코드 미재사용, raw HTTP)으로 재현한 **API-level
limit** 판정을 그대로 인용한다 — quota 소진 상태에서도 4개 이상
요청이 즉시 400으로 거부됐다는 사실이 "우연한 rate limit"이 아니라
"입력 자체에 대한 구조적 검증"이라는 근거였다. 이 ADC는 그 판정을
재론하지 않고 그대로 승계한다.

## Q3. Central Router로 오독될 위험은 실제로 배제되는가

**예, 조건부로.** `RFC-0040` §Rejected Alternatives가 `ADR-0024`
Option D(Central Engine Router)와의 구조적 차이(최종 선택 권한 없음,
여러 Engine 간 런타임 선택 아님, 단순 결정적 필터링만 수행)를 명시
했다. 이 ADC는 이 구분을 **Architecture 확정의 필수 조건**으로
다시 못박는다 — 아래 Decision이 "Central Router 아님"을 별도 항목으로
명시하는 이유다.

## Q4. 책임 경계 확정 ≠ Production API 통합 — 이 구분이 유지되는가

**예.** 책임 경계(누가 무엇을 결정하는가)가 명확하다는 것과, 실제로
Stage 01~05 코드가 이 경로로 OpenRouter를 호출하도록 바꾸는 것은
다른 질문이다. 후자는 구체적 API 조합 실험, Production Routing 변경,
Contract 재검증을 필요로 하며 이 ADC의 범위 밖이다.

---

## Decision

**PARTIAL — Architecture Boundary CONFIRMED, Concrete API Adoption
NOT YET DETERMINED.**

### 확정하는 것 — 책임 경계(구조적 근거로 확정 가능)

- **Free Pool 기반**: 모델 후보는 OpenRouter가 실제로 제공하는
  `:free` 목록에서만 나온다 — Jarvis가 임의로 모델을 추가/가정하지
  않는다.
- **Deterministic filtering**: 후보 축소는 명백히 판정 가능한 사실
  (Free 여부, Stage hard requirement, Contract compatibility,
  context/modality)만으로 이뤄진다 — 품질/성능 추정 없음.
- **Maximum 3 candidates**: `models[]` 상한 3개를 Architecture
  불변조건으로 확정한다(Q2 근거).
- **OpenRouter delegation**: 후보 중 실제 모델 선택, provider
  availability, failover는 전적으로 OpenRouter 책임이다 — Jarvis는
  이를 재현하지 않는다.
- **Contract Validation 유지**: 모델 선택 경로와 무관하게 기존 Stage
  Contract 검증 방식을 그대로 유지한다 — Contract는 이 Architecture로
  인해 변경되지 않는다.

### 확정하지 않는 것 — 아래는 이 ADC가 명시적으로 보류한다

- **특정 모델명** — 어떤 Stage도 특정 free 모델 id를 Architecture
  수준에서 고정하지 않는다.
- **특정 Stage별 모델** — Stage-모델 매핑표를 만들지 않는다.
- **scoring algorithm** — Jarvis 쪽 후보 순위화/점수화 로직을 설계
  하지 않는다(Deterministic Filter는 순위화가 아니라 필터링이다).
- **latency-based routing** — 응답 속도 기반 우선순위를 두지 않는다.
- **quality-based routing** — 품질 추정 기반 우선순위를 두지 않는다.
- **OpenRouter 내부 selection algorithm** — OpenRouter가 후보 중
  실제로 무엇을 어떻게 고르는지는 Jarvis가 설계·가정하지 않는다.

### 이 Decision이 하는 것

- `RFC-0040`의 8단계 파이프라인과 책임 경계표를 공식 기록으로
  확정한다 — 향후 어떤 세션도 이 경계를 처음부터 재조사할 필요 없이
  이 문서를 인용할 수 있다.
- 최대 3개 제한을 Architecture 불변조건으로 승격한다(실측 Evidence
  근거, 추정 아님).
- "이 Candidate Selection은 Central Router가 아니다"라는 구분을
  공식 기록으로 확정한다(Q3).

### 이 Decision이 하지 않는 것

- Stage 01~05 Production 코드/routing 변경 — 전부 미착수.
- `openrouter/free`류 구체적 API 조합 방식의 채택 — 미확정.
- Deterministic Candidate Filter의 구체적 판정 규칙 목록(필드/기준
  전체 목록) 구현 — 미착수.
- Contract 재설계 — 무변경(원래부터 이 Architecture가 요구하지 않음).
- Failure Boundary(Pool 조회 실패, 후보 0개, 전체 후보 실패 시
  재시도/에스컬레이션 정책)의 구체적 구현 — 미착수(`RFC-0040`
  §Failure Boundary가 이미 Open Question으로 명시).

---

## Validation Requirements — Concrete API Adoption을 재판정하려면 필요한 것

1. **Deterministic Candidate Filter 실제 구현 및 규칙 목록 확정**:
   "명백히 판정 가능한 사실"의 전체 기준 목록(예: context window
   최소값, 알려진 비기능 모델 제외 목록)을 구체화하고, 이 규칙만으로
   Scoring 없이 후보가 정상적으로 좁혀지는지 실측한다.
2. **Stage 01~05 각각에 대한 실제 통합 실험**: Free Pool 조회 →
   Filter → ≤3 후보 → `models[]` 호출 → Contract Validation까지
   전체 경로를 각 Stage에서 실제로 실행하고, 실패율/latency/선택된
   모델 분포를 실측한다(이미 `OPENROUTER-AUTO-SELECTION-V1-
   VALIDATION-0001.md`가 유사 실험을 했으나, 그 결과는 Stage05
   Fixture 결함으로 "PARTIAL" 판정을 받았다 — 이 ADC는 그 실험을
   "충분한 근거"로 재사용하지 않는다, 원칙 9).
3. **Failure Boundary 정책 확정**: Pool 조회 실패/후보 0개/전체 후보
   실패 각각에 대해 구체적 처리 방식을 별도 RFC 또는 이 ADC의 후속
   Amendment로 정한다.
4. **`openrouter/free`류 구체적 API 조합 방식 검증**: 별도 Experiment로
   실제 지원 여부를 확인한다(추정 금지, 원칙 6).
5. **Production Routing 편입 여부의 별도 Governance 판단**: 설령 위
   1~4이 전부 충족되더라도, 이 경로를 실제 Stage 01~05 Production
   Routing에 편입할지는 `ADR-0024`가 확정한 2-Engine 구조와의 관계를
   포함해 별도로 판단해야 한다(OpenRouter는 지금까지 "실험적 검증
   endpoint"로만 다뤄져 왔다는 전제를 그대로 유지, `RFC-0040` §Context).

## Open Questions

- Deterministic Filter가 판정할 "명백한 compatibility" 기준의 전체
  목록은 이 ADC가 확정하지 않는다 — 구현 단계에서 별도로 정한다.
- 이 Architecture가 Stage 01~04(deterministic 결과 확인 가능)와
  Stage05 Review(LLM 품질 판단 개입)에 동일하게 적용 가능한지는
  이 ADC가 판단하지 않는다 — `OPENROUTER-AUTO-SELECTION-V1-
  VALIDATION-0001.md`가 이미 Stage05에서 Fixture 결함을 겪었다는
  점만 참고로 남긴다.
- `models[]` 3개 상한이 OpenRouter 측 변경으로 달라질 경우 이 ADC를
  Amendment할지, 새 ADC를 만들지는 Not Determined.

## ADR 여부

**이번 세션에서 ADR을 작성한다(`ADR-0026`).** `ADC-0042`와 달리, 이
ADC는 "책임 경계(구조) 확정"이 명확한 Yes이며 Production API
Adoption만 NOT YET DETERMINED다 — 이는 `ADR-0025`(Stage05 Parallel
Validation Architecture Boundary)가 이미 세운 선례("Independence/
Boundary는 Accepted, Production Adoption은 NOT YET DETERMINED로
분리해 ADR에 기록")와 동일한 패턴이다. Boundary 확정 자체는 ADR
수준의 기록 가치가 있다고 판단한다.

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: Stage 01~05 코드 변경, OpenRouter
Production Routing 편입, `domain/model_pool.py` 등 기존 실험 harness
코드 변경, Contract 변경. 문서 3건(이 ADC + `RFC-0040` + 후속
`ADR-0026`)만 추가한다.

## Self Review

- 책임 경계 확정과 Production API 채택 판정을 하나로 뭉뚱그렸는가 —
  **아니오**(§Decision이 명시적으로 두 축으로 분리).
- 실측 Evidence 없이 "3개 제한"을 임의로 정했는가 — **아니오**
  (Q2, `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` §6
  직접 인용).
- Central Router로 해석될 여지를 남겼는가 — **아니오**(Q3, `RFC-0040`
  §Rejected Alternatives와 함께 명시적으로 배제).
- `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`의 PARTIAL 실험
  결과를 "충분한 채택 근거"로 소급 인용했는가 — **아니오**
  (§Validation Requirements 2번에서 명시적으로 "충분한 근거로
  재사용하지 않는다"고 기록).
- 특정 모델명/Stage 매핑/scoring/latency-routing/quality-routing을
  확정했는가 — **아니오**(§Decision "확정하지 않는 것" 전부 명시).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다
  (PR은 사용자 지시에 따라 생성하지 않는다).

## Related

- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`
- `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`(동일
  분리 판정 구조 선례)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`(Central
  Router 명시적 거부 선례, Option D)
- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`(Boundary
  Accepted / Production Adoption NOT YET DETERMINED 분리 기록 선례)
- `docs/research/OPENROUTER-VALIDATION-0001.md`
- `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md`
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`
