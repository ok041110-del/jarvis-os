# PHASE11-PROMPT-CACHE-AUDIT-0001: Prompt Cache 필요성 검증

이 문서는 사용 후기가 아니다. 실제로 수행한 조사 + 실험 하나의 기록이다.
Phase 10 종료(`PHASE10-CLOSURE-0001.md`) 직후, "Prompt Cache가 실제로
필요한가"를 Cache 도입을 전제하지 않고 조사한다. `call_engine()`은
전혀 수정하지 않았다. Architecture/Contract를 설계하지 않았다.

## 1. 저장소에 "Prompt Cache" 개념이 이미 있는가

없다. `docs/`, `development-hq/` 전수 검색(`cache`/`캐시`) 결과
`__pycache__`/`.pytest_cache` 같은 도구 산출물 제외 디렉터리 언급만
있고, Prompt/Model 응답 Cache를 다루는 문서·코드는 없다.
`IMPLEMENTATION_RULES.md`도 Memory Service(영속화 계층)는 명시적으로
금지하지만 "Cache"라는 이름의 별도 항목은 없다 — Cache는 지금까지
논의된 적 없는 완전히 새로운 질문이다.

## 2. 현재 구조에서 "캐시할 대상"이 실제로 존재하는가

`call_engine()`이 매 호출마다 실제로 보내는 것 3가지를 그대로 확인했다:

1. `--append-system-prompt STATELESS_CALL_NOTICE` — **모든 호출에서
   글자 그대로 동일**(317자, 약 79 토큰 추정 — `len//4` 근사).
2. `prompt` 인자(`f"{MARKER}:{instruction}\n\n{payload}"`) — Capability마다
   다르고, 같은 Capability라도 `code`/`review` 등 payload가 Task마다
   다르다. 실제 워크플로(`run_mvp_0001`)에서 Task 1→Task 2가 같은
   `code`를 공유하긴 하지만, 두 호출의 앞부분이 `CODE_REVIEW:`/
   `TEST_EXECUTION:`로 서로 달라 **문자열 prefix가 겹치지 않는다** —
   Prompt Cache가 이득을 보려면 두 호출이 앞부분부터 동일해야 하는데,
   현재 프롬프트 조립 방식은 그 조건을 만들지 않는다.
3. `--disallowedTools` — CLI 플래그이지 프롬프트 텍스트가 아니다.

**결론**: 매 호출 공통으로 반복되는 유일한 고정 텍스트는
`STATELESS_CALL_NOTICE`(≈79 토큰) 하나뿐이다.

## 3. 그 반복 텍스트가 캐시할 만큼 큰가 — 실측

Anthropic Prompt Caching은 일반적으로 캐시 가능한 최소 블록 크기
기준(모델에 따라 1024~2048 토큰 내외)이 있다. `STATELESS_CALL_NOTICE`는
약 79 토큰으로 **그 최소 기준에 크게 못 미친다.** 설령 `claude -p`
내부가 시스템 프롬프트에 캐시를 자동 적용하더라도, 이 크기의 텍스트는
캐시 임계값 미만이라 실질적 이득이 구조적으로 발생하지 않는다 — 이는
추정이 아니라 텍스트 길이를 직접 측정한 결과다(`len(STATELESS_CALL_NOTICE)
== 317`).

## 4. 실험 — 동일 프롬프트 반복 호출의 실제 시간

동일한 짧은 prompt를 `call_engine()`으로 3회 연속 호출해 반복 시
유의미한 단축이 있는지 관찰했다(실제 Engine 3회 호출):

| 실행 | 소요 시간 |
|---|---|
| 1회 | 7.21s |
| 2회 | 5.77s |
| 3회 | 5.38s |

완만한 하락 추세가 있으나, `ENGINE-USECASE-0002`가 이미 확인한 동일
조건 반복 실행 간 자연 변동폭(예: 4-way 병렬이 53.60s → 17.20s로
3배 차이)에 비하면 이 정도 편차는 특이치로 보기 어렵다 — **이 실험
단독으로는 caching 효과를 주장할 근거가 되지 않는다**(억지로 확대
해석하지 않음). §3의 토큰 크기 논거가 훨씬 결정적이다.

## 5. 비용 관측 — 이번에도 구조적으로 불가

`ENGINE-USECASE-0001`이 이미 기록한 대로 `call_engine()`은 raw text만
반환해 캐시 적중 여부·토큰 절감을 직접 관측할 수 없다. 이번 조사도
같은 한계를 다시 확인했을 뿐, 새로 극복하지 않았다(`--output-format
json` 전환은 Contract 변경이므로 시도하지 않음).

## 6. 판정

**현재 구조로 캐시가 필요하다는 근거를 확보하지 못했다.**

- 반복되는 고정 텍스트가 하나뿐이고(§2), 그 텍스트가 캐시 최소
  기준보다 훨씬 작다(§3) — 캐시를 붙여도 이득이 발생할 물리적 대상이
  없다.
- 실제 워크플로의 연속 호출(Task 1→Task 2)도 prefix가 겹치지 않아
  캐시 이득 조건을 만들지 않는다(§2).
- Cache를 전제로 한 설계를 하지 않았다 — 이번 결론은 "필요 없다"는
  실측 근거이지, Cache Contract를 만들기 위한 사전 조사가 아니다.

## Adapter/Contract 필요성

없음.

## Governance

RFC/ADC/ADR 불필요. Prompt Cache는 **NEED-DRIVEN DEFER** — 다음 조건이
실제로 관찰될 때만 재조사한다(지금 선제적으로 설계하지 않는다):

1. 반복되는 고정 텍스트가 실제로 1000토큰 이상으로 커질 때(예: 여러
   파일을 한 번에 넘기는 새 Capability가 실제로 필요해질 때 — 지금은
   `code: str` 단일 파일 입력만 존재).
2. 동일하거나 prefix가 겹치는 프롬프트가 실제로 반복 호출되는 실제
   Use Case가 나타날 때(지금은 없음).

## Evidence

- 실험 스크립트: 세션 scratchpad(tracked 브랜치 미포함).
- 실측값: `STATELESS_CALL_NOTICE` 317자(≈79 토큰), 동일 프롬프트
  3회 반복 7.21s/5.77s/5.38s.

## Next

- 이번 문서는 초기 조사다 — Cache가 필요해지는 조건(§Governance)이
  실제로 발생하기 전까지는 후속 실험을 선제적으로 설계하지 않는다.
