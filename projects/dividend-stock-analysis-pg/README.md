# Dividend Stock Analysis — PG

Investment HQ의 3번째 Dividend Stock Dogfooding이다(1차: JNJ, 2차: KO).
목적은 PG(The Procter & Gamble Company) 분석 자체가 아니라,
`docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` §7이 요구한
"최소 1~2회 추가 배당주 실행"을 완성해 **Stock/ETF Team과 동일한 3회
반복 기준으로 Promotion 판단 재료를 확보**하는 것이다. Dividend Stock
Team이나 Agent를 이 실행에서 승격하지 않는다.

70년 연속 배당 증액(Dividend King, 136년 연속 배당 지급)을 기록한 실제
배당주이며, JNJ(헬스케어)·KO(음료)와 다른 산업(생활용품/필수소비재)이다.

## 무엇을 하는가

`agents.py`/`runner.py`는 JNJ/KO/`projects/stock-analysis-*`와 코드를
공유하지 않는 별도의 project-local 구현이다(지시문 패턴만 동일하게
유지 — 공정한 반복 관찰을 위해). Stock의 5개 분석 + Dividend
Quality/Valuation 2개 = 7개 분석 → Bull Case/Bear Case → Synthesis →
Final Report(총 11회 `call_engine()` 호출) 구조를 쓴다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## JNJ/KO와의 차이

- 배당성향 63.77% — JNJ(46.19%)와 KO(77.24~80.1%) 사이의 중간값.
- Technical 섹션이 처음으로 명시적인 현재가/지지선/저항선을 포함하고
  (KO는 현재가 자체가 없었음), 기술적 신호도 처음으로 약세/중립
  (JNJ·KO는 둘 다 강세 "Strong Buy") — 3회 중 처음으로 기술적으로
  다른 방향의 데이터.
- FY2027 가이던스 대비 최근 분기(Q4 FY2026) GAAP EPS -15% 급락이라는,
  JNJ/KO에는 없던 유형의 단기 실적 악화 신호가 존재.
- DCF 부재가 KO에 이어 2연속 반복(JNJ만 예외적으로 보유).
- Valuation 섹션 내부에 Forward P/E 수치 자체의 소스 간 불일치
  (21.1배 vs 25.4배)를 의도적으로 남겨 두어, 자기인정 패턴의 반복
  여부를 다시 관찰했다.

## 구조

`projects/dividend-stock-analysis-jnj/README.md`,
`projects/dividend-stock-analysis-ko/README.md`와 동일한 구조.

## Out of Scope

- Dividend Stock Team/Agent 실제 생성/등록, Investment HQ Architecture
  확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-*`·
`projects/dividend-stock-analysis-{jnj,ko}`와 동일: 이 프로젝트에서
발견되는 문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다.
Observe First, Decide Later.
