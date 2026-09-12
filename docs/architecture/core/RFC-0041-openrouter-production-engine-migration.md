# RFC-0041: OpenRouter Production Engine Migration — Stage 01~05 Free Model Selection Architecture 편입

**Status**: Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0044`/`ADR-0027`가 담당)
**Author**: Claude Code(사용자 요청에 따른 Architecture 공식화)
**대상**: `ADR-0026`이 §10에서 NOT YET DETERMINED로 유보한 "Production
Routing Integration"을 실제로 승인할지 판단하기 위한 제안. 이 RFC는
**Governance 문서만** 다룬다 — Production 코드 변경은 이 RFC의 범위가
아니다(구현은 이 RFC 승인 이후, 별도 작업으로 진행).

---

## Summary

- 질문: **"OpenRouter를 Jarvis OS의 Production LLM Engine으로
  편입하고, Stage 01~05의 LLM routing을 Free Model Selection
  Architecture로 Migration할 것인가?"**
- 제안 Architecture는 `ADR-0026`이 이미 Boundary 수준에서 Accept한
  8단계 경로(Free Pool → Deterministic Filter → ≤3 Candidate →
  `models[]` → OpenRouter 실제 선택 → Stage Execution → Contract
  Validation)를 그대로 Production에 적용하는 것이다 — 새 Architecture
  발명이 아니라 기존 결정의 적용 범위 확장이다.
- `ADR-0024`의 2-Engine(ChatGPT/Claude Code) 정적 구조는 그대로 두고,
  OpenRouter를 **3번째 Engine**으로 추가한다 — `IMPLEMENTATION_
  RULES.md`가 "3번째 Engine은 별도 RFC → ADC → ADR 대상"이라고 명시한
  절차를 이 RFC가 충족한다.
- Jarvis Engine selection(어떤 Engine 모듈을 쓸지, 파일 단위 정적
  import)과 OpenRouter 내부 Free Model selection(그 Engine 안에서
  어떤 모델이 쓰일지)은 **서로 다른 층위**다 — 이 RFC는 전자에
  OpenRouter라는 선택지 하나를 추가할 뿐, Central Engine Router를
  부활시키지 않는다(§Engine Boundary).
- 기존 Stage 01~05의 책임/Contract/Agent/Capability는 전부 보존한다
  — 이 Migration은 "모델을 누가/어떻게 고르는가"만 바꾼다.

---

## Problem

Stage 01~05는 현재 ChatGPT/Claude Code 2개 Engine에 완전히 의존한다
(`ADR-0024`). 두 Engine 모두 특정 모델(`gpt-4o` 등)을 Engine 모듈
내부에 고정하고 있어, 무료 대안 모델 Pool을 활용할 방법이 없다.
`ADR-0026`은 OpenRouter Free Model Pool을 실험적으로 검증해 Architecture
Boundary(Free Pool/Filter/Candidate Selection)를 Accept했지만,
**Production에 실제로 적용할지는 의도적으로 유보**했다 — 그 유보를
지금 해소할지 판단하는 것이 이 RFC의 목적이다.

## Context

- `ADR-0024` — ChatGPT/Claude Code 2-Engine 정적 구조 채택(Option C),
  Central Router 명시적 거부(Option D).
- `RFC-0040` → `ADC-0043` → `ADR-0026` — OpenRouter Free Model
  Selection Architecture Boundary Accept(Scoped). §9(Concrete API
  구현)·§10(Production Routing Integration) 둘 다 NOT YET DETERMINED.
- `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
  `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` — 8단계 경로의
  앞부분(Free Pool/Filter/Candidate Selection)을 실제 Pool 데이터로
  실측 확정. 뒷부분(OpenRouter 실제 선택/Contract)은 이 세션 내내
  quota 소진으로 미확인(NOT DETERMINED로 남음, §Evidence References
  에서 그대로 인용).
- `OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` —
  Production Migration을 코드로 직접 시도했을 때 이 RFC 없이는
  Governance 위반임을 확인하고 STOP한 선행 작업. 이 RFC가 바로 그
  STOP이 요구한 "별도 RFC"다.
- `hqs/development/IMPLEMENTATION_RULES.md` "Multi-Engine 허용 범위
  확인" 절 — "3번째 이상의 Engine 추가... 별도 RFC → ADC → ADR 대상".

## Motivation

- 무료 모델 Pool을 실제로 활용하면 Stage 01~05 실행 비용을 낮출 수
  있는 **가능성**이 있다(단, 이 RFC는 비용 절감을 확정된 사실로
  주장하지 않는다 — §Cost Boundary).
- `ADR-0026`이 실험으로 이미 확인한 Boundary(Free Pool/Filter/
  Candidate Selection)를 Production에서 썩히지 않고, 승인된 절차
  (RFC→ADC→ADR)를 거쳐 실제로 쓸 수 있게 만든다.
- Stage별 모델 고정을 시도했던 이전 세션들(`OPENROUTER-STAGE-MODEL-
  SELECTION-0001.md`)이 겪은 가용성 변동 문제를, "Jarvis가 모델을
  고정하지 않고 OpenRouter에 위임"하는 구조로 원천 해결한다.

## Goals

1. OpenRouter를 Jarvis Production의 3번째 LLM Engine으로 Governance
   상 정식 승인한다.
2. Stage 01~05가 OpenRouter Free Model Selection Architecture로
   Migration할 수 있는 **Governance 근거**를 만든다(실제 코드
   Migration은 이 RFC 승인 이후 별도 구현 작업).
3. `IMPLEMENTATION_RULES.md`의 3번째 Engine 절차 요건을 충족한다.
4. 기존 Stage Contract/Agent/Capability를 조금도 흔들지 않는다.

## Non-Goals

- 이번 RFC는 Production Code를 변경하지 않는다(§13 Production 항목,
  사용자 지시).
- 특정 Stage에 특정 free 모델명을 고정하지 않는다.
- Jarvis-side Scoring/Ranking/Quality Judge/Latency Routing을
  도입하지 않는다(`ADR-0026`이 이미 배제한 것을 재확인할 뿐).
- OpenRouter 내부 selection algorithm을 설계하지 않는다.
- `openrouter/free`류 구체적 API 조합 방식의 확정 — 이 RFC의 범위
  밖(`ADR-0026` §9와 동일하게 유보, §Open Questions).
- Central Engine Router/Gateway를 신설하지 않는다(§Engine Boundary).
- Stage DAG/Team 구조 검증 — 별도 "Stage 01~05 Team Architecture
  Review" 작업(사용자 지시, 이 RFC 다음 단계).

## Current Architecture

```
Stage 01/02 ─┐
Stage 03/05 ─┼─(정적 import)─→ chatgpt_engine.call_engine_via_chatgpt ─→ str
Stage 04    ─┘─(정적 import)─→ engine.call_engine(Claude Code)       ─→ str
```

`ADR-0024` Option C — 파일 단위 정적 import, 런타임 분기 없음. 각
Engine 모듈이 모델을 내부에 고정(`chatgpt_engine.py`의
`CHATGPT_DEFAULT_MODEL = "gpt-4o"` 등). Stage/Agent 코드는 모델명을
모른다(`OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` §1,
§8이 이미 실측 확인).

## Proposed Architecture

```
Stage
  ↓
Stage Requirement
  ↓
Free Model Pool
  ↓
Deterministic Candidate Filter
  ↓
Candidate Selection ≤ 3
  ↓
OpenRouter models[]
  ↓
OpenRouter actual model selection/failover
  ↓
Stage Execution
  ↓
Contract Validation
```

이는 `RFC-0040`/`ADR-0026`이 이미 Accept한 8단계 경로와 동일하다 —
이 RFC는 새 Architecture를 발명하지 않고, 그 경로의 **Production
적용 여부**만 다룬다. Stage는 여전히 모델명을 모른다 — 대신 이제는
"어떤 Engine을 쓸지"도 Stage 코드가 알 필요가 없어지고(Migration
대상이 되는 경우), Engine Adapter 계층이 Free Pool 조회부터
Contract Validation 호출까지를 캡슐화한다(§Migration Scope).

## Migration Scope

이 RFC가 "Migration 가능"으로 판단하는 범위는 다음으로 한정된다
(§9 Migration Boundary와 동일, 여기서는 Architecture 관점으로 기술):

- **바뀌는 것**: Stage가 LLM 응답을 얻는 경로 — 기존에는 정적으로
  고정된 Engine 함수 하나를 호출했다면, Migration 후에는 OpenRouter
  Free Model Selection Layer(Free Pool→Filter→Candidate→`models[]`)
  를 거쳐 호출한다.
- **안 바뀌는 것**: Stage가 그 응답을 어떻게 검증하는지(Contract),
  Stage가 무엇을 책임지는지(Responsibility), Stage 실행 순서(DAG).

Stage별로 Migration을 적용할지는 이 RFC가 일괄 강제하지 않는다 —
Stage마다 독립적으로 Migration 여부를 판단할 수 있다(예: Stage 04는
Claude Code Engine을 유지하고 Stage 01/02만 먼저 Migration하는 것도
이 RFC의 범위 안이다). 이 RFC는 **경로 자체의 Governance 승인**만
다룬다.

## Stage 01~05 영향

| Stage | 현재 책임 | Contract | 이번 RFC가 바꾸는 것 |
|---|---|---|---|
| 01 | Context | 4개 reasoning agent, JSON 필수 키 검사(`parse_structured_output`) | 모델 선택 경로만(Contract 무변경) |
| 02 | Specification | `tasks`/`dependencies` JSON, 세부 스키마는 `planning_pipeline.py` | 〃 |
| 03 | Architecture Design | 6개 섹션 포함 prose | 〃 |
| 04 | Implementation | AST 기반 Target 함수 존재 확인, `EXPOSURE_POLICY_CONFLICT` sentinel | 〃 |
| 05 | Validation | Review는 advisory prose, 실제 Contract는 `contracts.py`가 별도 집행 | 〃, **실제 Stage 04 Implementation이 Review에 전달되는 구조는 그대로 유지**(placeholder 금지, `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`가 이미 확인한 구조를 승계) |

## Engine Boundary

`ADR-0024`와의 관계를 명확히 구분한다:

- **A. Jarvis Engine selection**: 어떤 Engine 모듈(`chatgpt_engine.py`
  / `engine.py` / 이번에 추가될 OpenRouter Adapter)을 쓸지 — 이는
  여전히 **파일 단위 정적 선택**이다. `IMPLEMENTATION_RULES.md`의
  "허용" 조건(정확히 하나의 Engine 모듈을 import 시점에 정적으로
  선택)을 그대로 따른다. 이번 RFC는 이 층위에 **3번째 선택지
  (OpenRouter Adapter)**를 추가할 뿐, 런타임 조건 분기나 자동 fallback
  로직을 이 층위에 추가하지 않는다.
- **B. OpenRouter 내부 Free Model selection**: OpenRouter Adapter가
  일단 선택되면, 그 Adapter 내부에서 Free Pool 후보 중 실제로 어떤
  모델이 쓰일지는 OpenRouter 자신이 결정한다(`ADR-0026` §7 OpenRouter
  Delegation Decision을 그대로 승계).
- 이 RFC의 목적은 **B를 사용하는 하나의 Production Engine(OpenRouter
  Adapter)을 A의 선택지에 추가하는 것**이다 — A 층위에 Central
  Router를 만드는 것이 아니다. A는 여전히 "정확히 하나의 모듈을
  정적으로 고른다"는 원칙을 유지하며, 이번에 고를 수 있는 모듈이
  2개에서 3개로 늘어날 뿐이다.
- `IMPLEMENTATION_RULES.md`의 "3번째 이상의 Engine 추가... 별도 RFC →
  ADC → ADR 대상" 규칙은 이 RFC → 후속 `ADC-0044` → `ADR-0027`로
  충족된다.
- `ADR-0024`의 Central Router 거부(Option D)는 이 RFC로 재론되지
  않는다 — Option D가 거부했던 것은 "런타임 조건으로 Engine을 선택하는
  별도 Router 모듈"이었고, 이 RFC는 그런 Router를 제안하지 않는다
  (§Rejected Alternatives에서 명시적으로 구분).

## Candidate Selection Boundary

`ADR-0026` §6이 이미 확정한 것을 그대로 승계한다 — 이 RFC가 새로
결정하지 않는다:

- Free Pool 기반, deterministic filtering(free 여부/capability/
  context/modality/Contract compatibility), 최대 3개, tie-break는
  OpenRouter 응답 순서 그대로 앞에서부터 자름.
- 판정 불가능한 metadata는 추측하지 않고 `NOT_DETERMINED`로만
  기록한다(제외 사유로 쓰지 않음) — `OPENROUTER-FREE-MODEL-SELECTION-
  ARCHITECTURE-EXPERIMENT-0001.md` §2가 이미 실제 Pool 데이터로 이
  원칙의 실제 동작을 확인했다.

## OpenRouter Boundary

`ADR-0026` §7을 그대로 승계 — OpenRouter가 후보 중 실제 모델 선택,
provider availability, failover를 전담한다. Jarvis는 이 내부
알고리즘을 재현하지 않는다.

## Contract Boundary

- Stage Contract는 이 Migration으로 **전혀 변경되지 않는다** — Stage
  01~05 각각의 기존 Input/Output Contract(§Stage 01~05 영향 표)를
  그대로 유지한다.
- Contract Validation은 어떤 Engine(ChatGPT/Claude Code/OpenRouter)이
  선택됐는지 몰라도 동작해야 한다 — `ADR-0026` §Contract Boundary의
  단방향 의존(Selection → Execution → Contract Validation) 원칙을
  그대로 승계한다.
- Stage 05 Review는 반드시 **실제 Stage 04 Implementation**을
  입력으로 받아야 한다 — placeholder/dummy 금지
  (`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`가 이미 실제로
  검증한 구조를 그대로 Production 요건으로 승격한다).

## Failure Boundary

- 개별 Stage 실행의 실패 semantics(예외 타입, sentinel 문자열 반환
  방식 등)는 이 Migration으로 바뀌지 않는다(§9 Migration Boundary —
  "deterministic validation semantics"는 변경 대상이 아님).
- OpenRouter Adapter 자체의 실패(quota/5xx/timeout/malformed/
  connection)는 기존 Engine 모듈과 동일하게 **단일 예외 타입
  (`RuntimeError`)**으로 Stage/Agent 계층에 전달되어야 한다 — 기존
  `chatgpt_engine.py`/`engine.py`의 `str -> str`, 단일 `RuntimeError`
  Contract를 OpenRouter Adapter도 그대로 지켜야 한다(새 예외 타입
  체계를 Stage 계층에 노출하지 않는다).
- Free Pool 조회 실패, 후보 0개, 전체 후보 실패의 세부 처리는
  `ADR-0026` §Failure Boundary가 이미 유보한 대로 이 RFC도 유보한다
  (§Open Questions).

## Retry Boundary

- `ADR-0026` Experiment가 검증한 bounded retry(최대 1회, 실패 모델을
  재시도 Pool에서 제외)를 그대로 승계한다 — 재시도 횟수를 임의로
  늘리지 않는다.
- **Quota/rate-limit 실패는 모델 품질 실패와 분리해서 분류한다**
  (`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` §5가 이미
  실측으로 구현·검증한 `429_quota` 분류를 Production 요건으로
  승격한다) — quota 실패를 "이 모델이 나쁘다"는 신호로 오인해 그
  모델을 영구 배제하는 로직을 만들지 않는다.
- 기존 Stage의 failure semantics(예: Stage 03/04/05의 "실패 시
  sentinel 문자열로 치환, re-raise 없음")를 훼손하는 범위까지 retry를
  확장하지 않는다.

## Free Model Policy

- Free Pool은 OpenRouter가 실제로 제공하는 `:free` 모델 목록에서만
  구성한다 — Jarvis가 임의로 모델을 추가/가정하지 않는다.
- 특정 free 모델을 Stage에 영구 고정하지 않는다 — Pool은 매 실행마다
  다시 조회될 수 있다(`OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-
  EXPERIMENT-0001.md` §4가 실측한 대로, 짧은 시간 안에서는 Pool
  순서가 안정적이었으나 이를 "영구히 고정됨"으로 확대 해석하지
  않는다).
- 이미 실측으로 확인된 "plain chat completion 비기능 모델"(예:
  `thinkingmachines/inkling:free`류) 제외 목록은 그대로 승계한다 —
  이는 품질 판단이 아니라 구조적 비기능성의 실측 기록이다.

## Security / Credential Boundary

- API Key/Authorization 값은 Production 코드 어디에서도 명시적으로
  설정하지 않는다 — 기존 실험 세션 전체가 따른 것과 동일하게, 이
  Migration도 환경의 자동 인증 주입 방식(현재 세션의 Egress Proxy와
  동일한 원리 — Production 배포 환경에서는 별도의 Credential
  주입/관리 방식이 필요할 수 있으며, 이는 이 RFC가 확정하지 않는다,
  §Open Questions)에 의존한다.
- API Key 값은 로그/Evidence/커밋 메시지 어디에도 출력하지 않는다
  (이 세션 전체가 지켜온 원칙을 Production 요건으로 승격).
- OpenRouter Adapter가 Key를 별도로 저장·캐시하지 않는다 — 기존
  Engine 모듈(`chatgpt_engine.py`가 `OPENAI_API_KEY` 환경변수를 읽는
  방식과 유사한 원리)과 동일한 수준의 최소 노출을 유지한다.

## Cost Boundary

- Free Model Pool만 사용하므로 명목상 실행 비용은 0이다 — 단, 이는
  OpenRouter의 무료 티어 정책이 유지되는 동안만 유효하며, 이 RFC는
  OpenRouter의 요금 정책 변경 가능성을 통제하지 않는다.
- 일일 무료 요청 한도(실측 50/day, `OPENROUTER-MODELS-ARRAY-LIMIT-
  REVERIFICATION-0001.md`)는 Jarvis 전체 사용량이 공유하는 계정 단위
  제약이다 — Stage 01~05가 실제 Production 트래픽에서 이 한도를
  초과할 가능성은 **이번 RFC가 확정할 수 없다**(§Open Questions,
  §Risks).
- "비용이 절감된다"는 이 RFC의 확정 사실이 아니다 — 무료 요청 한도를
  초과하면 유료 대안(고정 모델 Engine으로의 재선택 등) 또는 실행
  차단 중 무엇을 택할지는 별도 정책 결정이 필요하다(§Open Questions).

## Latency Considerations

- `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`가 실측한 바로는
  Stage 01~03에서는 Auto Selection이 기존 Fixed Model보다 빨랐고
  (4~5배), Stage 04에서는 오히려 더 느렸다 — **"OpenRouter가 항상
  빠르다"는 주장을 하지 않는다**.
- Stage 05의 실제 latency는 quota 소진으로 이번 세션까지 미확정이다
  (`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` §NOT
  DETERMINED).
- 이 RFC는 Latency를 Migration 승인의 조건으로 삼지 않는다 — Latency
  실측은 Migration 이후 Validation Gate(§11, `ADR-0027`)의 대상이다.

## Alternatives

1. **현행 유지(2-Engine 고정)** — 무료 모델 Pool을 전혀 활용하지
   못한다. 채택하지 않는 이유가 되지는 않으나(이 RFC의 Motivation),
   이 RFC가 실패할 경우의 기본값이다.
2. **Stage별 특정 free 모델 하드코딩** — 이전 세션이 가용성 변동
   문제를 이미 실측으로 확인(Stage01 Gemma 재선정 사례) — 배제.
3. **OpenRouter를 3번째 Engine으로 추가, Free Model Selection Layer
   경유(채택안)** — Jarvis 책임을 후보 축소까지로 제한, 실제 선택은
   OpenRouter에 위임.
4. **Jarvis 자체 Multi-Provider Router 구축(모든 Provider를 하나의
   Router로 통합)** — `ADR-0024` Option D와 동일한 구조적 위험(Central
   Router, Gateway 금지 위반) — 배제.

## Rejected Alternatives

- **Central Engine Router 신설**(A 층위에 런타임 조건 분기 Router를
  두는 것) — `ADR-0024` §Alternatives Option D가 이미 명시적으로
  거부한 패턴과 동일 — 이 RFC는 재론하지 않고 그대로 배제 상태를
  유지한다.
- **ChatGPT/Claude Code를 OpenRouter로 완전히 대체** — 이 RFC는
  OpenRouter를 **추가**하는 것이지 기존 2-Engine을 **대체**하는 것이
  아니다 — `ADR-0024`의 Reasoning/Implementation 목적별 Engine 분리
  원칙을 훼손하지 않는다(대체는 별도 RFC 대상, 이 RFC의 범위 밖).
- **Quality/Latency 기반 동적 Engine 선택**(3개 Engine 중 상황에 따라
  자동으로 고르는 것) — 이는 A 층위에 Router를 도입하는 것과 동일한
  위험이므로 배제.

## Risks

- **Quota 소진 리스크**: 계정 단위 일일 한도(50/day)가 Production
  트래픽에서 조기 소진될 수 있다 — 이 경우 해당 Stage 실행이
  실패한다(§Failure Boundary가 이를 quota 실패로 정확히 분류하는
  것까지만 보장하며, 그 이후의 정책 — 유료 전환/기존 Engine 대체
  실행 등 — 은 이 RFC가 결정하지 않는다).
- **Free 모델 가용성 변동 리스크**: Pool 구성 자체가 OpenRouter 측
  사정으로 바뀔 수 있다(모델 deprecate, 신규 추가) — Deterministic
  Filter가 이를 자동으로 흡수하도록 설계됐으나(§Candidate Selection
  Boundary), 실제 장기 안정성은 검증된 바 없다(§Validation Plan).
- **Stage 05 Review 품질 미검증 리스크**: `STAGE05-ACTUAL-
  IMPLEMENTATION-REVALIDATION-0001.md`가 확인한 대로, 실제 LLM
  Review 결과 자체는 이 세션까지 한 번도 관찰되지 못했다 — Migration
  후에도 이 공백이 즉시 메워진다는 보장이 없다.
- **Governance 해석 리스크**: "3번째 Engine"이라는 이 RFC의 프레이밍
  자체가 향후 4번째, 5번째 Provider 추가 요구로 이어질 수 있다 — 이
  RFC는 그런 확장을 사전 승인하지 않으며, 추가 Provider는 각각 별도
  RFC → ADC → ADR을 다시 거쳐야 한다(`IMPLEMENTATION_RULES.md` 규칙
  그대로).

## Rollback Strategy

- Migration 실패 시: OpenRouter Selection Layer(Adapter)를 제거/
  비활성화하고 해당 Stage의 import를 기존 Engine 모듈(`chatgpt_
  engine.py` 또는 `engine.py`)로 되돌린다 — `ADR-0024` Option C가
  이미 각 호출부를 "정확히 하나의 Engine 모듈 정적 import"로
  유지하도록 설계했으므로, Rollback은 import 한 줄을 되돌리는 것과
  동등하다(Central Router가 없으므로 Rollback 경로가 단순함,
  `ADR-0024` §Rollback과 동일 원리).
- Rollback은 Stage Contract를 변경하지 않는다 — Contract Validation
  로직은 어떤 Engine을 쓰는지와 무관하게 동작하므로(§Contract
  Boundary), Rollback 시 Contract 재작업이 필요 없다.
- Rollback 판단 기준(구체적 임계값 — 예: quota 소진율, Contract 실패율)
  은 이 RFC가 확정하지 않는다 — `ADR-0027` §Validation Gate의 결과에
  따라 정한다(§Open Questions).

## Validation Plan

Migration 이후 Production 적용 전/후에 반드시 확인해야 할 항목(상세는
`ADR-0027` §Validation Gate):

- Stage 01~05 각각의 기존 Contract 회귀 없음
- Free Pool availability(실행 시점마다 재확인)
- Candidate ≤3 적용 확인
- `models[]` 요청 구성 정확성
- Retry/Failure classification(quota 별도 분류 포함)
- Stage 05가 실제 Stage 04 Implementation으로 Review를 수행하는지
- Stage 01→05 전체 E2E 실행

## Open Questions

- Quota 초과 시 Production 정책(유료 전환/기존 Engine으로 자동
  복귀/실행 실패 처리 중 무엇을 택할지) — NOT YET DETERMINED.
- Production 배포 환경의 실제 Credential 주입 방식(현재 세션의
  Egress Proxy와 동일한 방식이 Production에도 있는지) — NOT YET
  DETERMINED, 이 RFC의 조사 범위 밖.
- `openrouter/free`류 구체적 API 조합 방식 — `ADR-0026` §9와 동일하게
  이 RFC도 유보.
- Stage별로 Migration을 개별 적용할지 일괄 적용할지의 순서/우선순위
  — NOT YET DETERMINED(§Migration Scope가 개별 적용 가능성만 열어둠).
- Free Pool 조회 실패/후보 0개 시의 구체적 Fallback 정책(기존 Engine
  으로 자동 전환할지, 실행을 실패로 처리할지) — NOT YET DETERMINED.

## Evidence References

이 RFC는 아래 Evidence를 참고자료로 인용한다 — 각 Evidence의 한계를
숨기지 않는다(사용자 지시):

- `OPENROUTER-VALIDATION-0001.md` — OpenRouter 연결 자체의 실측 검증.
- `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` — Stage별 고정 모델
  선정의 가용성 한계(참고자료일 뿐, 이 RFC가 제안하는 Architecture와
  무관 — 어떤 모델명도 이 RFC는 고정하지 않는다).
- `OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md` — `models[]`
  3개 상한이 **API-level Evidence**(독립 재구현으로 재현)임을 명시.
- `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` —
  **Free Pool + deterministic filtering + ≤3 candidate는 실제 Pool
  데이터로 검증됐다**(5개 Case 전부 재현). 단, OpenRouter 실제 선택/
  Contract Validation/Retry 회복 효과는 **quota 소진으로 이번
  세션에서 확인하지 못했다**(NOT DETERMINED) — 이 한계를 숨기지 않는다.
- `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` — Stage 05
  Review에 실제 Stage 04 Implementation이 전달되는 구조는 확정했으나,
  **실제 Stage 05 LLM Review 결과 자체는 quota로 인해 여전히
  미확인**이다 — 이 RFC가 §Contract Boundary에서 "구조 유지"만
  요구하고 "품질 보증"을 주장하지 않는 이유.
- `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`("OpenRouter Auto
  Selection v1 Evidence") — 15/15 API 성공, Contract 100% 통과라는
  강한 근거가 있으나, **Decision은 PASS가 아니라 PARTIAL(B)**이다 —
  Stage05 Review 프롬프트에 placeholder가 쓰인 결함 때문이다. 이 RFC는
  이 PARTIAL 판정을 그대로 인용하며 PASS로 과장하지 않는다.
- `OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` — 이 RFC의
  직접 계기가 된 STOP 기록(Governance 승인 없이 코드 Migration을
  시도할 수 없음을 확인).

---

이 RFC는 결정 문서가 아니다. 실제 채택/보류 판정은 `ADC-0044`가,
Architecture Boundary 확정은 `ADR-0027`이 담당한다.
