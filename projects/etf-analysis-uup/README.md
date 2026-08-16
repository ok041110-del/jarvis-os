# ETF Analysis — UUP

Investment HQ의 여섯 번째 ETF Dogfooding이자 첫 통화형(Currency) ETF
실행이다. 목적은 UUP(Invesco DB US Dollar Index Bullish Fund, 달러
강세 베팅 선물 기반 ETF) 분석 자체가 아니라, **QQQ(주식)·SCHD(주식)·
AGG(채권)·GLD(원자재)·VNQ(리츠)에서 확인된 ETF Team 6개 역할 구조가
여섯 번째 자산군(통화, 선물 기반)에서도 반복되는지 검증**하는 것이다.
이는 `docs/research/ETF-TEAM-DEFINITION-0001.md`의 재평가 조건("원자재/
리츠/통화 등 다른 자산군에서도 이 범위가 반복되는지")의 **마지막 남은
항목("통화")**을 다룬다 — GLD가 "원자재", VNQ가 "리츠"를 이미 검증함.
ETF Team이나 Agent를 이 실행에서 선행 설계하지 않는다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/etf-analysis-{qqq,schd,agg,gld,vnq}`
와 코드를 공유하지 않는 별도의 project-local 구현이다. AGG/GLD/VNQ와
동일한 6개 역할 구조(Composition/Index, Holdings/Exposure, Cost/
Tracking, Performance/Risk, Distribution, Macro → Bull Case/Bear
Case → Synthesis → Final Report, 총 10회 `call_engine()` 호출)를
그대로 유지했다 — 역할을 통화형 자산에 맞춰 미리 재구성하지 않았다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## QQQ/SCHD/AGG/GLD/VNQ와의 차이

- 보유 구조가 다섯 ETF 중 처음으로 **파생상품(선물) 기반**이다 —
  지분증권(QQQ/SCHD/AGG/VNQ)도, 실물자산(GLD)도 아닌 세 번째 보유
  구조 유형. Holdings/Exposure Analyst가 이를 스스로 구분했다.
- 원본 데이터 자체에 **추적 대상 설명이 서로 다른 근본적 불일치**가
  있었다(단일 USDX 선물 지수 vs 6개 통화 개별 선물 포지션) —
  Composition Analyst가 이를 "사소한 표현 차이가 아니라 트래킹
  메커니즘 자체에 대한 서술 불일치"로 정확히 짚었다.
- 법적 구조가 Limited Partnership(커머디티 풀)이라 세금 보고가
  K-1/K-3라는, 다른 5개 ETF에 없던 구조적 특성을 Distribution
  Analyst가 소득 프로필의 일부로 다뤘다.
- 지급주기가 **연 1회**(QQQ/SCHD/AGG/VNQ는 분기, GLD는 없음)로 다섯
  ETF 모두와 다른 세 번째 패턴.
- Final Report 호출이 `development-hq/mvp/engine.py`의
  `ENGINE_TIMEOUT_SECONDS`(180초) 근처(174.1초)까지 소요된 첫 사례 —
  6개 ETF 중 가장 큰 출력(25,538자)과 관련된 것으로 보이나, 최초
  시도는 실제로 180초를 초과해 타임아웃됐다(재실행으로 해결).

## 구조

`projects/etf-analysis-agg/README.md`·`etf-analysis-gld/README.md`·
`etf-analysis-vnq/README.md`와 동일한 구조, 6개 분석 Capability.

## Out of Scope

`projects/etf-analysis-{qqq,schd,agg,gld,vnq}/README.md`의 Out of
Scope와 동일. 여러 ETF의 동시/배치 처리도 이번 범위 밖이다.

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-{qqq,schd,agg,gld,vnq}`
와 동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는
근거로 쓰지 않는다. Observe First, Decide Later. Final Report 타임아웃
1회 관찰도 마찬가지로 즉시 `ENGINE_TIMEOUT_SECONDS`를 수정하지 않고
Evidence로만 기록한다.
