# Raw Data — Toyota Motor Corporation (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-16)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

이 실행의 목적은 종목 분석 자체가 아니라 **Nestlé 실행에서 5~6회
연속 재현된 Final Report `ENGINE_TIMEOUT_SECONDS`(180초) 타임아웃이
다른 비미국 배당주에서도 재현되는지 검증**하는 것이다. 대상으로
Toyota Motor Corporation(일본, 1차 상장 7203.T / ADR TM)을 선정했다
— Nestlé(스위스, 식음료, 연 1회 배당)와 국가·산업·배당주기·통화가
전부 다르며(일본, 자동차, 반기 배당, JPY), 기존 Investment Dogfooding
(Stock 4종·ETF 6종·Dividend Stock 4종[JNJ/KO/PG/Nestlé])과 중복되지
않는다. Dividend Stock Team의 7개 역할 구조는 신규 설계 없이 그대로
재사용한다.

## [FUNDAMENTAL] 최근 실적 (FY2026 연간, 2026년 3월 결산, 2026-08-04 1분기 발표 포함)

- FY2026(2025-04~2026-03) 연간 매출 ¥50.68조(YoY +5.5%), 판매대수
  959.5만대(YoY +2.5%)
- 영업이익 ¥3,766.216B로 YoY -21.5%(전년 ¥4,795.586B) — 미국 관세
  영향 ¥1.38조, R&D/인건비 증가, 환율 효과가 주요 원인으로 보도됨
  (마케팅 노력·원가절감으로 일부 상쇄)
- 순이익 ¥3,848.098B로 YoY -19.2%, 기본 EPS ¥295.25(전년 ¥359.56)
- FY2027(2026-04~2027-03) 가이던스: 영업이익 ¥3.4조로 상향(기존
  전망 ¥3.0조에서 상향), 매출 ¥51.0조, 순이익 ¥3.0조 전망
- 별도 보도: 2026-08-04 발표된 1분기(4~6월) 이익이 전년 대비 +76%
  (¥1.48조)로 급증했다는 기사 존재 — **연간 영업이익 -21.5%(악화)와
  1분기 +76%(개선)라는 시점이 다른 두 수치가 방향성부터 상반**되며,
  자료는 이 두 수치가 다른 회계 기간(FY2026 연간 vs FY2026 1분기)을
  가리킨다는 것 외에 추가 설명을 제공하지 않음
- 관세 비용: 회계연도 기준 최대 $9B로 주요 자동차 업체 중 최대치로
  보도됨

출처: [Toyota FY2026 results — StockTitan](https://www.stocktitan.net/sec-filings/TM/6-k-toyota-motor-corp-current-report-foreign-issuer-36f41dfd6880.html),
[TMC Announces April Through March 2026 Financial Results — Toyota USA Newsroom](https://pressroom.toyota.com/tmc-announces-april-through-march-2026-financial-results/),
[Toyota boosts guidance — Yahoo Finance](https://finance.yahoo.com/markets/stocks/article/toyota-boosts-guidance-announces-6-billion-share-buyback-as-fiscal-q1-results-shine-170431398.html),
[Toyota's (TM) Profit Soared 76% — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/toyota-tm-profit-soared-76-190728633.html)
(2026-08)

## [DIVIDEND_QUALITY] 배당 지속가능성/성장/지급여력 — 비미국 시장 특성 포함

- **지급 주기: 반기(연 2회, 중간배당+기말배당)** — Nestlé(연 1회),
  JNJ/KO/PG(분기)와 또 다른 세 번째 지급 주기 패턴
- FY2026 배당: 중간배당 ¥45/주 + 기말배당 ¥50/주 = 연간 ¥95/주.
  보통주 총배당액 ¥1,238.2B
- **배당성향(Payout Ratio) 32.2~33.2%** — Nestlé(86.9%)보다 훨씬
  낮고 JNJ(46.19%)보다도 낮음. 최근 5년 배당 성장률 평균 약 16%로
  보도됨
- **일본 원천징수세**: 배당 원천징수세율 국세 15%(소득할증 2.1%
  포함 시 15.315%) + 지방세 5% = 총 20.315~20.42%. 조세조약 체결국
  (미국 포함) 거주자는 통상 5~10%로 우대되나, 구체적 미국-일본
  조약 우대세율 수치는 이 자료에 없음(IRS 조약 문서 링크만 확인,
  세부 %는 미확인)
- 이 자료는 배당성향 32.2%와 33.2%(두 소스 간 소폭 차이)의 산정
  시점/기준이 FY2026 연간 실적 중 어느 시점 데이터인지 명시하지
  않음 — Fundamental 섹션의 연간(-19.2%)/1분기(+76%) 순이익 방향
  불일치와 마찬가지로 시점 정합성 문제가 존재할 수 있으나 자료가
  이를 직접 연결하지 않음

출처: [Toyota Motor (TM) Dividend Analysis — Tickeron](https://tickeron.com/dividends/TM/),
[Dividends — Toyota Motor Corporation Official Global Website](https://global.toyota/en/ir/stock/dividend/),
[TOYOTA MOTOR Dividend Payout Ratio — GuruFocus](https://www.gurufocus.com/term/payout/TM),
[Withholding Tax in Japan — AQ Partners](https://www.aqpartners.jp/blog/withholding-tax-japan-employment-dividends-royalties),
[Japan - Corporate - Withholding taxes — PwC Tax Summaries](https://taxsummaries.pwc.com/japan/corporate/withholding-taxes)
(2026)

## [VALUATION] 밸류에이션

- Trailing P/E 8.53(2026-06-30 기준), Forward P/E 10.31. 다른
  소스는 TTM P/E 10.07(2026-07-29 기준, 10년 중위값 10.04 대비
  거의 동일)로 보도 — Trailing 수치가 8.53/10.07로 소스 간 차이
  있음(원인 불명)
- 동종업계 비교: General Motors P/E 8.82(Toyota와 유사), Honda
  P/E 10.82(Toyota보다 높음), Volkswagen P/E 6.84(Toyota보다
  낮음), GM 41.32(다른 소스, 위 8.82와 크게 다름 — 어느 GM
  수치가 맞는지 자료가 설명하지 않음), Tesla P/E 265.28(极단적
  고평가)
- Toyota의 현재 P/E(8.53)는 3년 평균(11.13)·5년 평균(11.36)보다
  낮음 — "업종 내 상위 10% 저평가 구간"으로 서술됨
- 이 자료는 Trailing P/E 두 수치(8.53/10.07)의 차이나 GM P/E 두
  수치(8.82/41.32)의 차이의 산정 기준을 설명하지 않음 — Nestlé의
  DCF 공정가치 불일치와 유사한 유형의 소스 간 미해소 모순

출처: [Toyota (TM) — P/E ratio — companiesmarketcap.com](https://companiesmarketcap.com/toyota/pe-ratio/),
[TOYOTA MOTOR PE Ratio (TTM) — GuruFocus](https://www.gurufocus.com/term/pettm/TM),
[Toyota Motor (TM) PE Ratio — financecharts.com](https://www.financecharts.com/stocks/TM/value/pe-ratio)
(2026)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- 2026-08-13 종가 $188.71(전일 대비 +0.260%, $188.22→$188.71)
- 단기/장기 이동평균은 매수 신호(단기가 장기 위에 위치)로 보도되는
  한편, 다른 소스는 MA5~MA200 기준 매수 2건·매도 10건으로 "Strong
  Sell"이라고 상반되게 보도 — **두 기술적 요약 자체가 방향부터
  반대**(Nestlé의 "단기/중기 매수, 장기 매도"보다 더 극단적인
  소스 간 불일치)
- RSI(14일) 43.04 — 중립(과매수·과매도 아님)
- 3개월 MACD는 매수 신호. $193.09 상단 추세선 돌파 시 강한 매수
  신호가 될 수 있다는 조건부 서술 존재(2026-08-13 기준 아직 미돌파)
- 종합 기술 점수(StockInvest.us): 0.00, "Hold/Accumulate" 등급

출처: [Toyota Motor Ord Stock Price Forecast — StockInvest.us](https://stockinvest.us/stock/TM),
[TM Technical Analysis — Investing.com](https://www.investing.com/equities/toyota-technical),
[TM Technical Analysis — Barchart.com](https://www.barchart.com/stocks/quotes/TM/technical-analysis)
(2026-08)

## [INDUSTRY] 산업/경쟁 구도

- 시가총액 $226.29B(2026-08 기준) — 글로벌 자동차 제조사 중 시가총액
  2위(1위 Tesla), 판매대수 기준으로는 2025년 1,130만대+로 6년
  연속 세계 1위
- Tesla가 Toyota보다 시가총액이 훨씬 높은 이유로 "EV/AI/자율주행/
  에너지 기술의 리더로 평가받기 때문"이라고 자료가 설명 — 판매량과
  시가총액 순위가 반대로 나타나는 구조를 자료가 스스로 지적
- 경쟁사: BYD, Hyundai, GM, Ford, Volkswagen, Honda, Mercedes-Benz,
  Porsche, Ferrari 등이 시가총액 상위권으로 언급됨
- 전동화 전략: "Multi-pathway"(HEV 중심, 순수 EV는 제한적 투자)
  전략을 견지 — 전동화 차량이 전체 판매의 약 47% 차지(대부분 HEV로
  추정되나 자료가 HEV/BEV 비중을 명확히 구분하지 않음)
- EV 목표를 기존 150만대(2026년)에서 80만대로 하향 조정했다는 서술과,
  2027년까지 EV 라인업을 5종에서 15종으로 3배 확대한다는 서술이
  동시에 존재 — "생산량 목표는 낮추면서 모델 수는 늘린다"는 얼핏
  상충되는 전략으로 보이나, 자료는 이 둘의 관계(모델당 생산량 감소
  등)를 설명하지 않음

출처: [Toyota (TM) - Market capitalization — companiesmarketcap.com](https://companiesmarketcap.com/toyota/marketcap/),
[World's Largest Automakers by Market Capitalization — autopunditz.com](https://www.autopunditz.com/post/world-s-largest-automakers-by-market-capitalization-tesla-leads-toyota-follows-byd-strengthens-it),
[Toyota Sat Out the EV Boom—Now It's Winning — Autoblog](https://www.autoblog.com/news/toyota-sat-out-the-ev-boom-now-its-winning),
[Toyota Defies EV Trends, Surges Ahead — MarketScreener](https://www.marketscreener.com/news/toyota-defies-ev-trends-surges-ahead-ce7e5dddd98eff2d)
(2026-08)

## [NEWS/EVENT] 최근 이벤트 (2026-06~08)

- **대규모 리콜**: 2026-08-11, 계기판 결함(비상등/방향지시등 무력화
  가능성)으로 미국 내 508,354대(2025~2026년형 Camry Hybrid 포함)
  리콜 발표. 2026-06에는 별도로 2026년형 bZ·Lexus RZ 약 16,200대
  리콜
- **관세 비용**: 회계연도 기준 관세 비용이 최대 $9B에 달할 것으로
  전망 — 주요 자동차업체 중 최대 규모로 보도됨. 이것이 Fundamental
  섹션의 영업이익 -21.5%(¥1.38조 관세 영향 포함)와 직접 연결됨을
  자료가 명시
- **미국 생산 투자**: 켄터키·인디애나 공장에 $1B 투자 발표(2026-03),
  2번째 EV 생산 및 Camry/RAV4 하이브리드·Grand Highlander SUV 생산
  능력 확대 목적
- **신차**: 2027년형 C-HR 발표(2026-08-06), bZ Woodland(BEV) 연내
  출시 예정
- 이 자료는 리콜 508,354대의 재무적 영향(충당금 등)이 실적에
  반영됐는지 여부를 명시하지 않음 — JNJ의 탈크 소송, Nestlé의
  CEO 해임과 동일한 구조("이벤트는 다루되 재무 영향은 자료 범위
  밖으로 명시")

출처: [Toyota (TM) Recalls Thousands of EVs — Yahoo Finance](https://finance.yahoo.com/technology/articles/toyota-tm-recalls-thousands-evs-013426742.html),
[Toyota Shares Lifted as Camry Recall Expands — ts2.tech](https://ts2.tech/en/toyota-stock-nysetm-edges-higher-camry-recall-reaches-508354-vehicles/),
[US tariffs erase all of Toyota's North America profits in FY2026 — WardsAuto](https://www.wardsauto.com/news/us-tariffs-erase-all-of-toyotas-north-america-profits-in-fy2026/819825/),
[Toyota bets big on EVs and US manufacturing — Yahoo Finance](https://finance.yahoo.com/markets/article/toyota-bets-big-on-evs-and-us-manufacturing-as-tariff-costs-mount-192446874.html)
(2026-06~08)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- 4개 기관 집계: 전부 매수(Strong Buy), 매도/보유 0건 — 평균
  목표주가 $256.52(범위 $230~$290)
- 다른 소스(26개 기관): 평균 목표주가 $237.83(+23.97% 상승여력)
- 또 다른 소스: 12개월 목표주가 $231.58(+21.57% 상승여력)
- **동일 "애널리스트 컨센서스"를 표방하는 세 소스의 평균 목표주가가
  $231.58/$237.83/$256.52로 전부 다르고**, 커버리지 기관 수도
  4개/12개월 소스 불명/26개로 제각각 — Nestlé(Buy/Hold 소스 간
  등급 자체가 다름)보다 더 심한 수치 자체의 불일치
- 현재가($188.71, Technical 섹션 기준) 대비 세 목표주가 모두
  20%대 이상 상승여력을 시사한다는 방향성은 일치

출처: [Toyota Motor (TM) Stock Forecast — stockanalysis.com](https://stockanalysis.com/stocks/tm/forecast/),
[Toyota Stock Target Price and Analyst Consensus — macroaxis.com](https://www.macroaxis.com/target-price/TM),
[TM Forecast, Price Target & Analyst Ratings — ChartMill.com](https://www.chartmill.com/stock/quote/TM/analyst-ratings)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 Toyota FY2026 有価証券報告書(유가증권보고서)
  원문, 도쿄증권거래소 공시 전체를 직접 대조 검증하지 않음
- **연간 영업이익(-21.5%)과 1분기 순이익(+76%)의 방향성이 정반대** —
  서로 다른 회계 기간을 가리키는 것으로 추정되나 자료가 명시적으로
  연결하지 않음(Fundamental 섹션)
- Trailing P/E(8.53/10.07)와 GM P/E(8.82/41.32) 모두 소스 간 수치
  자체가 다름 — 산정 기준(TTM 시점, GAAP/조정 등) 불명
- 애널리스트 목표주가 평균이 $231.58/$237.83/$256.52로 세 소스 모두
  다르고 커버리지 기관 수도 불일치
- 배당성향(32.2%/33.2%) 산정 시점이 연간 실적의 어느 시점 기준인지
  불명
- EV 생산 목표(80만대 하향)와 EV 모델 수 확대(5→15종)가 동시에
  보도되나 관계가 설명되지 않음
- 실시간 최신 시세가 아니라 검색 시점(2026-08-16) 기준 가장 최근 보도
  스냅샷
