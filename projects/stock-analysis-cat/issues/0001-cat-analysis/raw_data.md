# Raw Data — Caterpillar Inc. (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-17)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

Stock Team의 기존 4건(AAPL=소비자 하드웨어, NVDA=AI 반도체, MSFT=
기업용 SW/클라우드, JPM=금융)이 기술주 3건+금융주 1건으로 편중돼
있어, 이를 보완할 **산업재/중장비 제조업** 종목으로 **Caterpillar
Inc.(NYSE: CAT)**를 선정했다 — 경기순환 산업, 백로그(수주잔고)
지표, 관세 노출도 등 기술/금융과 완전히 다른 펀더멘털 구조를 가진다.
Stock Team의 5개 역할(Fundamental/Technical/Industry-Competition/
News-Event/Sentiment)은 지시문 변경 없이 재사용한다.

## [FUNDAMENTAL] 최근 실적 (Q2 2026, 2026-08 발표)

- 매출 $20.543B(YoY +24%, $16.569B에서 증가) — **사상 최초로 분기
  매출 $20B 돌파**
- 주당순이익(EPS) $7.77(전년동기 $4.62), 조정 EPS $8.17(전년동기
  $4.72, YoY +73%)
- 영업이익률 20.9%(전년동기 17.3%), 조정 영업이익률 21.9%(전년동기
  17.6%, +430bp)
- 부문별: Construction Industries 매출 +35%, Power & Energy +17%,
  Resource Industries +20%($4.648B, 부문이익 $693M, +23%),
  Financial Products 매출 +10%($1.145B, 부문이익 $328M, +32%)
- 2026년 연간 가이던스: 매출 "mid to high teens"(중~고두자리수)
  성장 전망으로 상향 — **다른 자료는 2026년 매출 성장을 "low
  double-digit"(낮은 두자리수)로 서술** — 두 표현이 서로 다른 시점
  (Q2 실적 발표 전/후)의 가이던스인지 자료가 명확히 구분하지 않음
- **백로그(수주잔고) $72B**(전분기 대비 +$9B, 전년동기 대비 약 +92%)
  — 사상 최대

출처: [Caterpillar stock extends 2026 rally — ad-hoc-news.de](https://www.ad-hoc-news.de/boerse/news/corporate-news/caterpillar-stock-extends-2026-rally-as-record-q2-backlog-and-earnings/69943793),
[Caterpillar Q2 2026 slides: record $20.5B revenue, backlog soars — Investing.com](https://www.investing.com/news/company-news/caterpillar-q2-2026-slides-record-205b-revenue-backlog-soars-93CH-4835057),
[Caterpillar's Q2 Earnings Cross $20 Billion — TIKR](https://www.tikr.com/blog/caterpillars-q2-earnings-cross-20-billion-for-the-first-time)
(2026-08)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- **기술적 신호 자체가 소스 간 정면으로 상충**:
  - 한 소스: "이동평균 기준 Neutral(중립), 매수 6건·매도 6건"
  - 같은 소스 내 다른 서술: "주가가 5·20·50일 지수이동평균보다
    낮아 'strongly bearish'(강한 약세) 추세"
  - 또 다른 서술: "일간 기준 Neutral, 매수 3건·매도 3건"
  - **"중립"과 "강한 약세"가 동시에 서술되는 등, 방향성 자체가
    자료 안에서 일관되지 않음**
- RSI(14일) 40.55 — "과매도(oversold)"로 해석
- 자료 최신성 주의: "가장 최근 데이터는 2026년 7월 말 기준으로
  보이며, 8월 상황은 달라졌을 수 있다"고 자료 자체가 명시

출처: [CAT Technical Analysis, RSI and Moving Averages — Investing.com](https://www.investing.com/equities/caterpillar-technical),
[Caterpillar, Inc. (CAT) Technical Analysis — Financhill](https://financhill.com/stock-price-chart/cat-technical-analysis),
[CAT RSI: Caterpillar Relative Strength Index Chart — stockrsi.com](https://www.stockrsi.com/cat/)
(2026-07~08)

## [INDUSTRY] 산업/경쟁 구도

- **시가총액이 소스 간 다름**: 한 소스는 "2026년 8월 기준
  $392.49B(세계 38위)", 다른 소스는 "2026년 초 약 $409B" — 시점
  차이로 추정되나 자료가 명확히 정리하지 않음
- 주요 경쟁사: Deere & Company, Komatsu(일본), Terex, Oshkosh,
  Wabtec, XCMG(중국), Epiroc(스웨덴)
- **관세 영향**: 2026년 1분기에만 약 $600M 관세 타격, 2026년 전체
  기준 약 $2.2~2.4B 관세 역풍 전망(Deere는 2026년 $1.2B로 다소 적음)
- 밸류에이션 프리미엄: Forward P/E 38.51배(업종 평균 35.13배 대비
  프리미엄) — 다른 자료는 "43.7배로 Deere(33.1배) 대비 상당한
  프리미엄"으로 서술, **38.51배와 43.7배 두 수치가 공존**
- Komatsu(14.73배)·Terex(13.65배)는 훨씬 저렴하나, "ROE 48.21%
  (Komatsu 10.83%, Terex 13.43%)로 CAT의 수익성이 프리미엄을
  정당화한다"고 서술
- 매출 성장(11.8%)은 Terex(17.0%)보다 낮고, 영업마진(16.5%)은
  Deere(17.4%)보다 낮음 — **이 "11.8%/16.5%" 수치는 Fundamental
  섹션의 Q2 매출성장 +24%·영업이익률 20.9~21.9%와 다른 기준(연간
  vs 분기, 조정 전 vs 후 등)으로 추정되나 자료가 설명하지 않음**

출처: [Should You Buy, Sell or Hold Caterpillar Stock Post Q2 Earnings — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/buy-sell-hold-caterpillar-stock-145100162.html),
[CAT Earns Its Premium Over Peers — Trefis](https://www.trefis.com/stock/cat/articles-v3/608363/cat-earns-its-premium-over-peers-now-what/2026-07-22),
[Caterpillar (CAT) - Market capitalization — companiesmarketcap.com](https://companiesmarketcap.com/caterpillar/marketcap/),
[Caterpillar vs. Komatsu — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/caterpillar-vs-komatsu-heavy-equipment-154600195.html)
(2026)

## [NEWS/EVENT] 최근 이벤트 (2026)

- **관세**: 2026년 전체 관세 역풍이 $2.2~2.4B로 전망(위 INDUSTRY
  섹션과 중복 언급되나 News/Event 관점에서는 "지속되는 정책 리스크"
  로 다뤄짐)
- **수요 동인**: 2026년 매출 성장의 배경으로 미국 인프라 지출,
  에너지 전환 관련 광산 수요, 자동화 도입, 데이터센터·지속가능성
  관련 투자 증가가 거론됨
- 이 자료는 관세 역풍($2.2~2.4B)과 매출 가이던스 상향(mid-high
  teens)이 어떻게 동시에 성립하는지(관세 비용이 이미 가이던스에
  반영됐는지) 설명하지 않음

출처: [Caterpillar Lifts 2026 Outlook After Record Quarter — TipRanks](https://www.tipranks.com/news/company-announcements/caterpillar-lifts-2026-outlook-after-record-quarter),
[Caterpillar Competitors: CAT Top Rivals in 2026 — Hudson Labs](https://www.hudson-labs.com/research/caterpillar-competitors-cat-top-rivals-in-2026)
(2026)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- **28개 기관(S&P Global) 집계**: 매수 15건, 보유 11건, 매도 2건 —
  종합 등급 "Buy"
- **목표주가가 세 소스에서 전부 다름**: S&P Global 28개 기관 평균
  $972.95, 다른 소스(26개 기관) 평균 $970.37(범위 $575~$1,218),
  또 다른 소스(34개 기관) 평균 $900.78 — **기관 수(28/26/34)와
  평균값이 전부 다름**
- 별도 컨센서스(16개 기관): 2026년 매출 $78.9B 전망, 주당순이익
  13% 성장한 $26.71 전망
- 이 자료는 세 목표주가 소스 간 차이(집계 시점, 포함 기관 차이 등)
  의 원인을 설명하지 않음

출처: [CAT Forecast, Price Target & Analyst Ratings — ChartMill](https://www.chartmill.com/stock/quote/CAT/analyst-ratings),
[Caterpillar Inc. Just Beat Earnings Expectations — Sahm Capital](https://www.sahmcapital.com/news/content/caterpillar-inc-just-beat-earnings-expectations-heres-what-analysts-think-will-happen-next-2026-08-08),
[Caterpillar (CAT) Stock Forecast & Analyst Price Targets — stockanalysis.com](https://stockanalysis.com/stocks/cat/forecast/)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 Caterpillar 10-Q(2026-06-30), Q2 2026
  Earnings Release 원문을 직접 대조 검증하지 않음
- 2026년 매출 가이던스가 "mid to high teens"와 "low double-digit"
  으로 다르게 보도됨
- 시가총액이 $392.49B/$409B로 소스 간 차이(시점 차이로 추정되나
  불명확)
- Forward P/E가 38.51배/43.7배로 같은 지표에 대해 다른 수치
- 기술적 신호가 "중립"과 "강한 약세"로 자료 내부에서도 상충
- 목표주가가 $972.95/$970.37/$900.78로 세 소스 모두 다름, 집계
  기관 수(28/26/34)도 다름
- 업종 비교 수치(매출성장 11.8%, 영업마진 16.5%)와 Fundamental
  섹션의 Q2 실측치(+24%, 20.9~21.9%) 간 기준 차이가 설명되지 않음
- 관세 역풍($2.2~2.4B)이 매출 가이던스 상향에 이미 반영됐는지 불명
- 실시간 최신 시세가 아니라 검색 시점(2026-08-17) 기준 가장 최근
  보도 스냅샷, 기술적 지표는 자료 자체가 "7월 말 기준일 수 있다"고
  명시
