# ETF Analysis — GLD

Investment HQ의 네 번째 ETF Dogfooding이자 첫 원자재형(Commodity) ETF
실행이다. 목적은 GLD(SPDR Gold Shares, 실물 금 담보 Grantor Trust) 분석
자체가 아니라, **QQQ(기술 성장주)·SCHD(배당 가치주)·AGG(채권)에서 확인된
ETF Team 6개 역할 구조가 지수도 배당도 없는 완전히 다른 자산군(실물
상품)에서도 반복되는지 검증**하는 것이다. 이는
`docs/research/ETF-TEAM-DEFINITION-0001.md`가 명시적으로 미검증 상태로
남겨둔 재평가 조건("원자재/리츠/통화 등 다른 자산군에서도 이 범위가
반복되는지")을 이번 실행에서 처음 다룬다. ETF Team이나 Agent를 이
실행에서 선행 설계하지 않는다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/etf-analysis-{qqq,schd,agg}`와 코드를
공유하지 않는 별도의 project-local 구현이다. AGG와 동일한 6개 역할
(Composition/Index, Holdings/Exposure, Cost/Tracking, Performance/Risk,
Distribution, Macro → Bull Case/Bear Case → Synthesis → Final Report,
총 10회 `call_engine()` 호출)을 그대로 유지한다 — 역할 이름/개수를
GLD에 맞춰 미리 바꾸지 않고, "이 역할이 GLD에 그대로 적용되는가"를
Engine 스스로 판단하게 뒀다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## QQQ/SCHD/AGG와의 차이

- 지수 자체가 없다 — GLD는 지수를 추적하지 않고 금 현물 가격을 그대로
  반영하는 Grantor Trust다. Composition Analyst가 이를 스스로 명시했다.
- 보유 구조가 다르다 — 100%가 단일 실물 상품(금괴)이며, 개별 종목/
  섹터/신용등급/만기 구조가 전부 개념적으로 적용되지 않는다(AGG는
  "종목 집중도만 무의미", GLD는 "종목이라는 개념 자체가 없음" — 정도가
  다르다).
- 분배금이 전혀 없다 — QQQ/SCHD/AGG는 모두 배당/이자 분배가 있었으나
  GLD는 구조적으로 분배할 소득 자체가 없다. Distribution Analyst가
  "None — 구조적 특징"이라고 명시했다.
- 리스크 지표 자체가 다르다 — 베타(주식)·듀레이션(채권) 같은 표준
  지표가 개념적으로 적용되지 않을 수 있음을 Performance/Risk Analyst가
  스스로 지적했다.

## 구조

`projects/etf-analysis-agg/README.md`와 동일한 구조, 6개 분석 Capability.

## Out of Scope

`projects/etf-analysis-{qqq,schd,agg}/README.md`의 Out of Scope와 동일.
여러 ETF의 동시/배치 처리도 이번 범위 밖이다.

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-{qqq,schd,agg}`와
동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는
근거로 쓰지 않는다. Observe First, Decide Later.
