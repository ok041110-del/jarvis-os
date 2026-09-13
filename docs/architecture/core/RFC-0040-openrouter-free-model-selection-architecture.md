# RFC-0040: OpenRouter Free Model Selection Architecture

**Status**: Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0043`/`ADR-0026`가 담당)
**Author**: Claude Code(사용자 요청에 따른 Architecture 공식화)
**대상**: Stage 01~05가 OpenRouter Free Model을 사용할 때 따라야 할
**선택(Selection) 책임 경계**. 특정 모델명, 특정 Stage-모델 매핑,
실제 Production 통합 여부는 이 RFC의 대상이 아니다(§Non-Goals).

---

## Summary

- Stage 코드에 모델명을 고정하지 않고, "Free Model Pool → 결정적
  후보 필터 → 최대 3개 후보 선정 → OpenRouter에 실제 선택 위임"이라는
  책임 경계를 제안한다.
- Jarvis 쪽 책임은 **후보를 3개 이하로 좁히는 것**까지이며, 그 이후
  "실제로 어떤 모델이 쓰이는가"는 전적으로 OpenRouter가 결정한다 —
  Jarvis가 모델 품질/성능을 추정하는 Scoring Engine을 만들지 않는다.
  최대 3개 제한은 추정이 아니라 실측 Evidence
  (`OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`)에 근거한다.
- 이 RFC는 실제 API 조합 방식(`openrouter/free` 등 구체적 파라미터
  조합)과 Production 통합 여부를 확정하지 않는다 — 그건 Architecture
  확정 이후의 별도 Experiment 영역이다(§Open Questions).
- 이 제안은 `ADR-0024`가 이미 거부한 "Central Engine Router"(Option D)
  와 다르다 — 이 RFC가 다루는 범위는 ChatGPT/Claude Code 2-Engine
  선택이 아니라, OpenRouter라는 **하나의 실험적 Engine 내부에서
  Free Model 후보를 고르는 방식**뿐이다(§Responsibility Boundary,
  §Rejected Alternatives에서 명시적으로 구분한다).

---

## Problem

이전 세션들이 실측으로 확인한 사실들이 서로 흩어져 있다:

1. Stage 01~05는 지금까지 검증 과정에서 특정 free 모델명을 하드코딩해
   테스트해왔다(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`) — 그러나
   무료 모델의 가용성(availability)은 시간에 따라 변한다(Stage01의
   최초 후보였던 Gemma가 33% 가용성만 보여 재선정이 필요했던 사례).
2. `model="openrouter/auto"`는 무료 티어에서 사용할 수 없다(HTTP 402,
   `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` §5).
3. `models[]` 배열은 free 호환이지만 최대 3개로 제한된다 — 이 제한이
   API 자체의 것임을 독립 재검증으로 확정했다
   (`OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`).
4. 지금까지 이 사실들은 각 Evidence 문서에만 흩어져 있었고, "Stage가
   실제로 어떻게 모델을 고를 것인가"에 대한 **Architecture 차원의
   책임 경계**가 어디에도 공식화되어 있지 않았다.

이 RFC는 이 흩어진 사실들을 근거로 삼아(§Evidence References), Stage가
모델을 어떻게 선택해야 하는지의 책임 경계만 공식화한다.

## Context

- 관련 선행 RFC: 없음(OpenRouter 기반 모델 선택은 이번이 첫 Architecture
  제안) — 단, `RFC-0036`(ChatGPT/Claude Code Dual Engine)과 `ADR-0024`
  (Multi-Engine 채택, Central Router 명시적 거부)는 "새 Engine
  선택/라우팅 계층을 만들 때의 Governance 제약"으로 이 RFC가 그대로
  따른다(§Responsibility Boundary).
- OpenRouter는 현재 Production Stage Engine Routing에 편입되어 있지
  않다 — ChatGPT/Claude Code 2-Engine 구조(`ADR-0024`)가 Production을
  담당하고, OpenRouter는 지금까지 "실험적 검증 endpoint"로만 사용됐다
  (`OPENROUTER-VALIDATION-0001.md`). 이 RFC는 이 구분을 바꾸지 않는다.
- 이 RFC가 참조하는 실측 Evidence는 모두 이전 세션들이 이미 생성한
  것이며, 이 RFC를 위해 새로 만들지 않는다(§Evidence References,
  원칙 9 — 소급 작성 금지).

## Goals

1. Stage 01~05가 OpenRouter Free Model을 쓸 때, "어떤 후보를 누가
   좁히고, 최종 선택을 누가 하는가"의 책임 경계를 명확히 한다.
2. 후보 축소(Candidate Selection) 로직이 **deterministic-first**임을
   Architecture 차원에서 확정한다 — 품질/성능 추정 기반 Scoring을
   금지한다.
3. `models[]` 최대 3개 제한이라는 실측 Evidence를 Architecture
   자체의 불변조건으로 승격한다(§Candidate Selection Boundary).
4. Stage Contract(입출력 계약)와 모델 선택 방식이 서로 독립적임을
   명시한다 — Contract Validation은 어떤 모델이 선택됐는지와 무관하게
   동일하게 동작해야 한다.

## Non-Goals

- 특정 Stage에 특정 모델명을 매핑하지 않는다.
- OpenRouter 내부 Selection Algorithm(어떤 기준으로 실제 모델을
  고르는지)을 설계하지 않는다 — 이는 OpenRouter의 책임이며 Jarvis가
  알 필요도, 재현할 필요도 없다.
- `openrouter/free`(또는 이와 유사한 구체적 파라미터 조합)의 실제
  사용 여부를 이 RFC에서 확정하지 않는다(원칙 5, 6) — 별도 Experiment
  영역.
- Production Stage 01~05 routing에 OpenRouter를 실제로 편입하지
  않는다(원칙 7, 8).
- Jarvis 자체 Model Router/Scoring Engine을 만들지 않는다(원칙 2).
- 이 RFC는 latency-based/quality-based 우선순위를 다루지 않는다.

## Proposed Architecture

```
Stage Requirement
    ↓
Free Model Pool
    ↓
Deterministic Candidate Filter
    ↓
Candidate Selection (≤ 3)
    ↓
OpenRouter models[]
    ↓
OpenRouter Model Selection / Fallback
    ↓
Stage Execution
    ↓
Contract Validation
```

각 단계는 §Responsibility Boundary에서 소유자를 명시한다. 이 파이프
라인은 순수하게 **선택(Selection) 경로**를 기술하며, Stage 실행
자체(Engine 호출, 응답 처리)의 세부 구현을 규정하지 않는다.

## Responsibility Boundary

| 단계 | 소유자 | 책임 |
|---|---|---|
| Stage Requirement | Stage | 필요한 capability, context requirement, input/output requirement, Stage Contract를 선언한다 — 모델명을 포함하지 않는다 |
| Free Model Pool | Jarvis Candidate Selection | OpenRouter가 실제로 제공하는 `:free` 모델 목록을 조회한다(가공 없이 있는 그대로) |
| Deterministic Candidate Filter | Jarvis Candidate Selection | Free 여부, Stage hard requirement 충족 여부, Contract compatibility, context/modality 등 **명백히 판정 가능한** compatibility만으로 후보를 줄인다 — 품질 추정 없음 |
| Candidate Selection (≤ 3) | Jarvis Candidate Selection | 필터를 통과한 후보를 실측 상한(3개) 이하로 축소한다 — 순위화/점수화 없이, 필터 결과 순서를 그대로 따른다 |
| OpenRouter `models[]` | Jarvis(호출부) | 후보 목록을 OpenRouter API 계약 형태로 전달한다 — 이 이상의 가공 없음 |
| OpenRouter Model Selection / Fallback | **OpenRouter** | 전달받은 후보 중 실제 모델을 선택하고, provider/model availability와 failover를 처리한다 — Jarvis는 이 내부 로직을 알지도, 재현하지도 않는다 |
| Stage Execution | Stage/Engine 호출부 | 선택된 모델로 실제 호출을 수행한다 |
| Contract Validation | Contract Validation | Stage 결과가 Stage Contract를 만족하는지만 검증한다 — 모델 품질을 추측하지 않는다(어떤 모델이 선택됐는지와 무관하게 동일 기준 적용) |

## Candidate Selection Boundary

- Jarvis Candidate Selection의 유일한 산출물은 **"OpenRouter에 넘길
  후보 id 목록(최대 3개)"**이다 — 최종 모델을 확정하지 않는다.
- 필터 기준은 전부 **명백히 판정 가능한 사실**이어야 한다(예: 모델
  id가 `:free`로 끝나는가, Stage가 요구하는 최소 context window를
  모델 메타데이터가 만족하는가, 과거 실측으로 확인된 "plain chat
  completion 자체가 구조적으로 불가능한 모델"인가). "이 모델이 더
  똑똑할 것 같다" 류의 추정 기준은 이 경계에 속하지 않는다.
- 최대 3개 제한은 `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
  §6이 확정한 **API-level limit**을 그대로 따른 것이며, Jarvis가
  임의로 정한 값이 아니다 — 이 Evidence가 바뀌면(예: OpenRouter가
  향후 상한을 변경하면) 이 숫자도 재검증 대상이 된다(§Open Questions).
- 필터를 통과한 후보가 3개를 초과하면, **추가 순위화 로직 없이** 조회
  순서(OpenRouter `/models` 응답 순서)대로 앞에서부터 자른다 — 이는
  `Deterministic Candidate Filter`가 이미 "명백한 compatibility"만
  판정했다는 전제와 일관된다(순위화가 필요하다면 그 자체가 Scoring
  Engine이 되므로 원칙 2 위반).

## OpenRouter Boundary

- OpenRouter는 전달받은 후보 중 실제로 어떤 모델을 쓸지, provider
  가용성 문제가 있을 때 어떻게 failover할지를 **자체적으로** 결정한다.
- Jarvis는 이 내부 알고리즘을 알 필요가 없고, 이를 흉내 내는 로직을
  만들지 않는다(원칙 2 — 복잡한 자체 Model Router/Scoring Engine
  금지).
- `openrouter/free`류의 구체적 파라미터 조합, `models[]` 이외의 대안
  메커니즘(있다면)의 채택 여부는 이 RFC가 확정하지 않는다(원칙 5) —
  Architecture가 요구하는 것은 "OpenRouter가 실제 선택을 담당한다"는
  경계뿐이며, 그 경계를 만족하는 구체적 API 조합은 별도 Experiment
  에서 검증한다(원칙 6, §Open Questions).

## Contract Boundary

- Stage Contract(입출력 계약)는 이 Architecture로 인해 변경되지
  않는다 — 어떤 모델이 선택됐든 Stage 결과는 동일한 Contract
  Validation을 통과해야 한다.
- Contract Validation은 모델 선택 단계의 존재를 몰라도 동작해야
  한다 — 즉 Contract Validation 코드는 `models[]`/Candidate Selection
  로직에 의존성을 가지면 안 된다(단방향 의존: Selection → Execution
  → Contract Validation, 역방향 없음).
- Contract Validation은 "이 모델이 더 나은 결과를 냈는가"를 판단하지
  않는다 — Structure/형식 계약 충족 여부만 본다(모델 품질 추측 금지,
  §책임 경계 원문 그대로).

## Failure Boundary

- Free Model Pool 조회 자체가 실패하면(네트워크/API 오류), Stage는
  이 Architecture 경로를 사용할 수 없다 — 이 RFC는 그 경우의 Fallback
  전략(예: 고정 모델로 되돌아갈지, 실패로 처리할지)을 확정하지
  않는다(§Open Questions, NOT YET DETERMINED).
- Deterministic Candidate Filter를 통과하는 후보가 0개인 경우(모든
  Free 모델이 Stage hard requirement를 만족하지 못하는 경우)의 처리
  방식도 이 RFC의 범위 밖이다(§Open Questions).
- OpenRouter가 전달받은 후보 모두에서 실패를 반환하는 경우(예: 모든
  후보가 rate limit)의 재시도/에스컬레이션 정책은 이 RFC가 확정하지
  않는다 — `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`가 이미
  실측한 bounded retry(§실험 결과)는 **Architecture 채택의 근거가
  아니라 참고 사례**로만 인용한다(원칙 9 — 소급 확정 금지).

## Alternatives

1. **Stage별 고정 모델명 하드코딩(현행 검증 방식의 연장)** — 지금까지
   Evidence 축적에는 유용했으나, 무료 모델 가용성 변동에 취약함이
   이미 실측으로 확인됐다(Stage01 Gemma 재선정 사례).
2. **`openrouter/auto` 사용** — 무료 티어 미지원(HTTP 402, 실측 확정)
   으로 애초에 선택지가 아니다.
3. **Jarvis 자체 Scoring/Ranking Engine으로 최선의 모델을 미리 계산**
   — 원칙 2/4 위반(복잡한 자체 Router, OpenRouter의 실제 selection
   책임을 Jarvis가 흉내 냄) — 채택하지 않는다.
4. **제안한 Architecture(Free Pool → Deterministic Filter → ≤3
   Candidate → OpenRouter delegation)** — 채택안. Jarvis 책임을
   "명백히 판정 가능한 후보 축소"까지로 제한하고, 실제 선택은
   OpenRouter의 실측 지원 메커니즘에 위임한다.

## Rejected Alternatives

- **Central Model Router/Gateway를 Jarvis 내부에 신설** — `ADR-0024`
  §Alternatives Option D(Central Engine Router)가 이미 명시적으로
  배제한 패턴과 동일한 구조적 위험(`IMPLEMENTATION_RULES.md` Gateway
  금지 조항 위반, 런타임 provider 재선택 계층 신설)을 갖는다. 이
  RFC가 제안하는 Candidate Selection은 **Router가 아니다** — 최종
  선택 권한을 갖지 않고(그 권한은 OpenRouter에 있다), 단순 결정적
  필터링만 수행하며, 여러 Engine(ChatGPT/Claude Code/OpenRouter) 사이의
  런타임 선택을 하지 않는다(OpenRouter 내부에서의 free 모델 후보
  축소일 뿐). 이 구분을 명확히 하기 위해 `ADC-0043`/`ADR-0026`에서
  "Central Router 아님"을 별도 항목으로 재확인한다.
- **Latency/Quality 기반 동적 우선순위 재정렬** — 원칙 2, 4 위반
  (Scoring Engine 필요) — 배제.
- **Stage Contract를 모델별로 분기** — Contract는 모델 선택과
  독립적이어야 한다는 §Contract Boundary와 정면으로 충돌 — 배제.

## Open Questions

- `openrouter/free`류 구체적 API 조합 방식의 실제 채택 여부 —
  NOT YET DETERMINED(원칙 5, 6).
- Free Model Pool 조회 실패/후보 0개 상황의 Fallback 정책 —
  NOT YET DETERMINED(§Failure Boundary).
- `models[]` 3개 상한이 OpenRouter 측 변경으로 달라질 경우의 재검증
  주기/트리거 — NOT YET DETERMINED.
- Stage 01~05 각각의 실제 Free Model Pool 통합(Production Adoption)
  여부와 시점 — NOT YET DETERMINED(`ADC-0043`/`ADR-0026`에서 명시적
  보류).
- Deterministic Candidate Filter의 구체적 판정 규칙 집합(어떤
  메타데이터 필드를 어떤 기준으로 볼지)의 전체 목록 — 이 RFC는 원칙
  (명백히 판정 가능한 사실만)만 확정하고, 규칙 집합 자체는 구현
  단계(향후 Experiment)에서 정한다 — NOT YET DETERMINED.

## Evidence References

이 RFC는 아래 기존 Evidence를 **참고자료로만** 인용한다 — 이 Evidence들이
"이 Architecture가 Production에 적합하다"를 입증하는 것으로 확대
해석하지 않는다(원칙 9, 아래 각 항목에 과도한 확정을 피하기 위한
주석을 남긴다).

- `docs/research/OPENROUTER-VALIDATION-0001.md` — OpenRouter 연결
  자체의 실측 검증(Egress Proxy 자동 인증 포함). 이 RFC의 "OpenRouter를
  실험적 endpoint로 쓸 수 있다"는 전제의 근거.
- `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md` — Stage별
  고정 모델 선정 시도와 가용성 문제(Stage01 재선정 사례) — 이 RFC가
  "고정 모델명 방식의 한계"를 주장하는 근거(§Problem 1). **이 문서가
  제안한 특정 모델명 자체는 이 RFC의 Architecture와 무관하다** —
  이 RFC는 어떤 모델명도 고정하지 않는다.
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
  — `models[]` 3개 상한이 API-level limit임을 독립 재검증으로 확정한
  문서. 이 RFC의 §Candidate Selection Boundary "최대 3개" 수치의
  **직접 근거**. 이 문서가 확정한 것은 "3개 상한이 API 제한이라는
  사실"뿐이며, "Deterministic Filter가 이렇게 구현되어야 한다"는
  세부 설계까지 정하지 않는다 — 그 세부 설계는 이 RFC가 별도로
  Open Question으로 남긴다.
- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md` —
  Stage 01~05 각각에 대해 `models[]` 기반 실행을 15회 실측한 문서.
  이 RFC의 파이프라인 도식(Free Model Pool → `models[]` → OpenRouter
  Selection → Stage Execution → Contract Validation)이 **실행
  가능함을 보여준 참고 사례**로만 인용한다 — 단, 그 문서 자체가
  "Decision = B(PARTIAL)"로 이미 명시했듯 Stage05 Review 부분은
  Fixture 결함이 있었다(그 문서 §13/§19). 이 RFC는 그 결함이 있는
  실행 결과를 근거로 "Stage05 통합이 검증됐다"고 주장하지 않는다 —
  Architecture 책임 경계 확정에만 이 문서의 구조적 관찰(파이프라인이
  end-to-end로 동작은 했다는 사실)을 인용한다.

---

이 RFC는 결정 문서가 아니다. 실제 채택/보류 판정은 `ADC-0043`이,
Architecture Boundary 확정은 `ADR-0026`이 담당한다.
