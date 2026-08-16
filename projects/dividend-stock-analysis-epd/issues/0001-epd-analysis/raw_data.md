# Raw Data — Enterprise Products Partners L.P. (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-16)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

기존 14건 Dogfooding(Stock: AAPL/NVDA/MSFT/JPM, ETF: QQQ/SCHD/AGG/
GLD/VNQ/UUP, Dividend Stock: JNJ/KO/PG/Nestlé/Toyota/Realty Income)과
중복되지 않는 신규 대상으로 **Enterprise Products Partners L.P.
(NYSE: EPD)**를 선정했다 — **MLP(Master Limited Partnership,
합자회사) 구조**로, 이전 6개 배당주(전부 일반 법인 corporation) 및
Realty Income(REIT, 그래도 법인)과 다르게 **법적 형태 자체가
파트너십**이다. "배당(dividend)"이 아니라 "**분배금(distribution)**",
표준 1099-DIV가 아니라 **Schedule K-1** 세금 서류, 배당성향 대신
**분배 커버리지 비율(Distribution Coverage Ratio, DCR)** 지표를
쓴다. 이번 실행도 신규 표준 실행 패턴(병렬화+출력최적화+Checkpointing
+180초 Timeout)을 그대로 적용한다. Dividend Stock Team 7개 역할은
지시문 변경 없이 재사용한다.

## [FUNDAMENTAL] 최근 실적 (Q2 2026, 2026-07-30 발표)

- 매출 $18.27B, 보통 유닛 보유자(common unitholder) 귀속 순이익
  $1.84B(주당[유닛당] $0.84, 희석 기준)
- **영업 분배가능현금흐름(Operational DCF) $2.3B(YoY +21%)** —
  분기 사상 최대치, 파트너십 분배금 대비 **1.9배 커버리지**
- 등가 파이프라인 물동량 14.7 MMBPD(YoY +8%), 해상터미널 물동량
  2.8 MMBPD(YoY +33%)
- 2026년 성장 자본지출(CapEx) 가이던스 $2.9B~$3.4B — 다른 자료는
  2026년 CapEx가 $2.2B~$2.5B로 "상당히 감소할 것"이라고 서술 —
  **두 CapEx 범위가 서로 다름**(시점/버전 차이로 추정되나 자료가
  설명하지 않음)
- 시장 컨센서스는 조정 주당순이익 $0.77(YoY +22%) 전망 — 실제 Q2
  결과($0.84)와 어느 정도 관련되는지 자료가 명시하지 않음(분기
  vs 연간 컨센서스 비교 여부 불명)
- 1분기(Q1 2026) 실적은 "EPS 예상 미달, 매출은 예상 상회"로 보도돼
  Q2(매출·이익 모두 컨센서스 상회로 보도)와 다른 패턴

출처: [Enterprise Reports Second Quarter 2026 Earnings — Businesswire](https://www.businesswire.com/news/home/20260730758757/en/Enterprise-Reports-Second-Quarter-2026-Earnings),
[Enterprise Products Partners LP (EPD) Q2 2026 Earnings Call Highlights — GuruFocus](https://www.gurufocus.com/news/8992351/enterprise-products-partners-lp-epd-q2-2026-earnings-call-highlights-record-ebitda-and-strong-volume-growth-amid-market-volatility),
[Enterprise Products Partners (EPD) Builds On Growth Projects — Simply Wall St](https://simplywall.st/stocks/us/energy/nyse-epd/enterprise-products-partners/news/enterprise-products-partners-epd-builds-on-growth-projects-i)
(2026-07~08)

## [DIVIDEND_QUALITY] 분배금 지속가능성/성장/커버리지 — MLP 고유 구조 포함

- **28년 연속 분배금 증액**("distribution growth"로 표현, 배당
  아님)
- 2026년 1분기 분배금 $0.55/유닛, 이후 연환산 기준 $0.56/유닛
  (YoY +2.8%)
- **분배 커버리지 비율(DCR)이 소스마다 다름**: Q1 2026 기준
  "Operational DCF가 분배금의 1.8배 커버", 다른 자료는 "1.85배",
  Q2 2026 실적 발표는 "1.9배", 2025년 전체는 "1.7배" — **네
  소스가 전부 다른 배율**을 보도(기간이 다르다는 점을 감안해도
  일관된 추세인지 자료가 명확히 정리하지 않음)
- **배당성향(payout ratio) 관련 정면 모순**: 한 기사 제목이
  "Payout Ratio Hits 80% Even as Management Cites Just 57%"라고
  명시 — **경영진이 밝힌 수치(57%, 조정 CFFO 기준, 2026-03
  종료 12개월)와 언론이 계산한 수치(80%)가 정면으로 다름**. 또
  다른 자료는 "2분기 페이아웃 비율(분배금+자사주 매입 합산)이
  조정 CFFO의 56%"라고 서술 — 57%/80%/56% 세 수치가 혼재
- **Schedule K-1 세금 서류**: 배당소득(1099-DIV)이 아니라 파트너십
  지분 세금서류(K-1)를 발급 — "세제상 이연 혜택이 있으나 IRA보다
  일반 과세계좌 보유가 권장된다"고 서술. 2025년 귀속분 K-1이
  2026-03-03부터 온라인 제공됨
- 2026년 유닛 자사주매입 $159M(2분기 기준)도 "분배 정책"의 일부로
  다뤄짐 — 순수 분배금 증액과 자사주매입을 분배 여력 계산에 함께
  넣을지 자료가 일관되게 다루지 않음

출처: [Enterprise Products Partners Stock's Payout Ratio Hits 80% Even as Management Cites Just 57% — TIKR](https://www.tikr.com/blog/enterprise-products-partners-stocks-payout-ratio-hits-80-even-as-management-cites-just-57),
[Enterprise Products: 1.85x Distribution Coverage Ratio — Benzinga](https://www.benzinga.com/Opinion/26/04/51980374/enterprise-products-solid-distribution-coverage-ratio-but-growth-capex-is-changing-what-that-buffer-actually-means),
[Enterprise Products Partners Has Had 28 Consecutive Annual Dividend Increases — The Motley Fool](https://www.fool.com/investing/2026/07/11/enterprise-products-partners-has-had-28-consecutiv/),
[Enterprise 2025 Schedule K-1 Tax Packages — Enterprise Products IR](https://ir.enterpriseproducts.com/news-releases/news-release-details/enterprise-2025-schedule-k-1-tax-packages-be-available-march-3),
[How Investors Are Reacting To EPD Record Q1 Volumes — Simply Wall St](https://simplywall.st/stocks/us/energy/nyse-epd/enterprise-products-partners/news/how-investors-are-reacting-to-enterprise-products-partners-e)
(2026)

## [VALUATION] 밸류에이션 — MLP 지표(EV/EBITDA·분배수익률) 중심

- **P/E 13.5배**(업종 평균 12.6배보다 약간 높음, 피어그룹 평균
  19.6배보다는 낮음) — 다른 소스는 P/E 13.6배(피어 평균 20.3배
  대비 저평가)로 근사하지만 소폭 다른 수치
- **EV/EBITDA 11.31배**(업종 평균과 "거의 동일"로 서술) — 그러나
  Energy Transfer(10.04배)보다 높고, Enbridge(9.82배 — 이 수치
  자체가 EPD의 것인지 다른 문맥인지 자료 서술이 혼란스러움, 원문은
  "EPD가 ENB의 15.53배보다 훨씬 낮은 9.82배"라고 서술해 **9.82배가
  EPD의 EV/EBITDA를 가리킴** — 그런데 앞서 11.31배라고도 함,
  **같은 지표(EV/EBITDA)에 대해 11.31배/9.82배 두 수치가 공존**)
- Forward EV/EBITDA는 9.0~9.5배로 서술(Energy Transfer 약 8.0배,
  Enbridge 약 11.5배 대비 "중간" 포지션)
- **분배수익률(distribution yield) 5.66%**(ENB 5.03%보다 높고,
  Energy Transfer 7.21%보다 낮음)
- 이 자료는 EV/EBITDA 두 상반 수치(11.31배 vs 9.82배)의 근거
  차이(TTM vs Forward, 산정 시점 등)를 설명하지 않는다

출처: [Enterprise Products Partners (EPD) Stock Still Looks Like A Bargain — Simply Wall St](https://simplywall.st/stocks/us/energy/nyse-epd/enterprise-products-partners/news/enterprise-products-partners-epd-stock-still-looks-like-a-ba/amp),
[MPLX vs ENB, EPD - EV to EBITDA Ratio — financecharts.com](https://www.financecharts.com/compare/MPLX,ENB,EPD/value/ev-to-ebitda),
[Enterprise Products vs. Enbridge — Yahoo Finance](https://finance.yahoo.com/news/enterprise-products-vs-enbridge-midstream-134200719.html),
[ET, EPD, or ENB: Which High-Yield Dividend Stock — Nasdaq](https://www.nasdaq.com/articles/et-epd-or-enb:-which-high-yield-dividend-stock-will-deliver-the-best-returns)
(2026)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- 이동평균: **매수 12건, 매도 0건("Strong Buy")**, 골든크로스
  발생, 모든 주요 이동평균 위에서 거래 중
- **RSI 자체가 타임프레임마다 극단적으로 다름**: 일간 RSI(14)
  60.48("건전한 매수세, 과매수 아님")인데 반해, **1시간/15분봉
  RSI는 각각 76·79 이상으로 과매수** — "단기 과열 vs 장기 상승
  추세 지속" 긴장 관계로 서술됨. 다른 기사 제목은 "장중 RSI 80
  도달, 과매수 신호"라고 표현
- ROE 20.9%("우수한 지표"로 서술)
- 종합 기술 전망: **"Strong Buy"**(JNJ/Nestlé/Toyota/Realty
  Income 등 이전 배당주들의 "신호 자체가 상충" 패턴과 달리, 이번엔
  방향성 자체는 일치하되 **타임프레임별 과매수 여부만** 상충)

출처: [EPD Technical Analysis, RSI and Moving Averages — Investing.com](https://www.investing.com/equities/enterprise-products-partners-lp-technical),
[Enterprise Products Partners L. stock Analysis — Cryptonomist](https://en.cryptonomist.ch/2026/08/15/enterprise-products-partners-l-stock-stays-bullish-as-intraday-rsi-hits-80/),
[EPD Technical Analysis — ChartMill](https://www.chartmill.com/stock/quote/EPD/technical-analysis)
(2026-08)

## [INDUSTRY] 산업/경쟁 구도

- **시가총액 약 $84.1B**(다른 자료는 EPD의 "기업가치(enterprise
  value)"가 "약 $1.8B에서 거의 $120B로 성장"했다고 서술 — 시가총액
  $84.1B와 기업가치 ~$120B는 다른 개념[EV=시가총액+순부채]이므로
  모순은 아니나, 자료가 이 둘의 관계를 명시적으로 연결하지 않아
  독자가 혼동할 수 있음)
- 연매출 $51.6B, 파이프라인 총연장 50,000마일 이상
- 4개 사업부문: NGL 파이프라인/서비스, 원유 파이프라인/서비스,
  천연가스 파이프라인/서비스, 석유화학/정제제품 서비스
- 경쟁 우위: Mont Belvieu 가격결정 지점(미국 NGL 생산의 95% 이상에
  영향)에서의 지위, LPG 수출 부문 브라운필드 경제성
- 경쟁사: Energy Transfer(레버리지 높음, EV/EBITDA 더 낮음),
  Enbridge(C-corp, EV/EBITDA 더 높음), MPLX
- 2026년 성장 CapEx는 Fundamental 섹션에서 이미 지적했듯 두 자료가
  $2.9~3.4B / $2.2~2.5B로 다르게 보도

출처: [I'm Calling It: Enterprise Products Partners Will Crush the S&P 500 — The Motley Fool](https://www.fool.com/investing/2026/07/25/im-calling-it-enterprise-products-partners-will-cr/),
[Enterprise Products Partners (EPD) Stock Price, Market Cap — Datainsightsmarket](https://www.datainsightsmarket.com/companies/EPD),
[Enterprise Products — 공식 사이트](https://www.enterpriseproducts.com/)
(2026)

## [NEWS/EVENT] 최근 이벤트 (2026)

- **CEO 승계 발표**: 공동 CEO A.J. "Jim" Teague가 2027-01-04
  은퇴 예정, 현재 공동 CEO인 W. Randall "Randy" Fowler가 단독
  CEO로 승계. General Partner의 "Office of the Chairman"을
  CEO·최고상업책임자·CFO까지 포함하도록 확대해 "연속성"을 강조
  하는 조직개편 동반
- Teague는 "웰헤드-투-워터(wellhead-to-water) NGL 서비스"를
  개척하고 기업가치를 "$1.8B에서 거의 $120B로" 성장시킨 인물로
  서술됨(위 INDUSTRY 섹션의 시가총액 $84.1B와 별개 지표[기업가치]
  — 자료가 명확히 구분하지 않음)
- CFO 신규 선임(Executive VP 겸 신임 CFO) 발표도 별도로 있었음
  (구체적 인물명/시점은 이 자료에 없음)
- 애널리스트 반응: JPMorgan 목표주가 $41→$42 상향(Neutral 유지),
  Raymond James $40→$42 상향(Outperform 유지), Scotiabank $39→$40
  상향(Sector Perform 유지) — **상향 조정이 이어지나 등급 자체는
  Neutral/Outperform/Sector Perform으로 기관마다 다름**
- 이 자료는 CEO 승계가 주가/실적에 미칠 구체적 영향을 제시하지
  않음("연속성 강조"라는 정성적 서술만 있음)

출처: [Enterprise Products announces CEO succession plan — Investing.com](https://www.investing.com/news/company-news/enterprise-products-announces-ceo-succession-plan-93CH-4770409),
[Enterprise Products Announces CEO Succession and Leadership Transition — TipRanks](https://www.tipranks.com/news/company-announcements/enterprise-products-announces-ceo-succession-and-leadership-transition),
[Enterprise Products Partners (EPD) On CEO Succession And Permian Growth — Simply Wall St](https://simplywall.st/stocks/us/energy/nyse-epd/enterprise-products-partners/news/enterprise-products-partners-epd-on-ceo-succession-and-permi)
(2026)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- **21개 기관 집계**: 매수 13건, 보유 6건, 매도 0건 — 종합 등급
  "Buy"
- 목표주가: 한 소스 평균 $41.15(+6.61% 상승여력), 다른 소스는
  $42.10(+15.11% 상승여력, 현재가 $36.57 기준) — **두 소스의
  "현재가" 자체가 다르게 암시됨**($41.15의 +6.61% 역산 시 현재가
  약 $38.6, $42.10의 +15.11% 역산 시 현재가 $36.57 — 서로 다른
  기준가)
- 최근 개별 조정: JPMorgan $41→$42(Neutral), Raymond James
  $40→$42(Outperform), Scotiabank $39→$40(Sector Perform), TD
  Cowen $39→$38로 **하향**(Hold), Morgan Stanley $43→$40으로
  **하향**(Underweight) — **상향/하향이 동시에 존재**하며 등급도
  Neutral/Outperform/Sector Perform/Hold/Underweight로 5개 기관이
  전부 다른 표현을 씀
- 이 자료는 "Buy" 종합 등급(13/6/0)과, 개별 기관의 목표주가 하향
  조정(TD Cowen, Morgan Stanley)이 어떻게 공존하는지 설명하지 않음

출처: [Enterprise Products Partners (EPD) Stock Price & Overview — stockanalysis.com](https://stockanalysis.com/stocks/epd/),
[EPD Forecast, Price Target & Analyst Ratings — ChartMill](https://www.chartmill.com/stock/quote/EPD/analyst-ratings),
[Enterprise products price target raised to 38 from 37 at BofA — TipRanks](https://www.tipranks.com/news/the-fly/enterprise-products-price-target-raised-to-38-from-37-at-bofa)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 EPD 10-Q(2026-06-30), Q2 2026 Earnings
  Release 원문을 직접 대조 검증하지 않음
- **분배 커버리지 비율이 소스마다 1.7배/1.8배/1.85배/1.9배로 전부
  다름**(기간 차이를 감안해도 정리되지 않음)
- **배당성향(payout ratio)이 56%/57%/80%로 소스마다 크게 다름** —
  경영진 발표치(57%)와 언론 계산치(80%) 사이 정면 모순이 기사
  제목 자체에 명시됨
- **EV/EBITDA가 11.31배와 9.82배로 같은 지표에 대해 다른 수치**
  제시
- 2026년 성장 CapEx가 $2.9~3.4B와 $2.2~2.5B로 다르게 보도
- 목표주가 산정 기준가($38.6 역산 vs $36.57)가 소스마다 다름,
  개별 기관 등급도 5개 전부 다른 표현(Neutral/Outperform/Sector
  Perform/Hold/Underweight)
- 기업가치(~$120B, CEO 재임 기간 성장분으로 서술)와 시가총액
  ($84.1B)의 관계가 명시적으로 연결되지 않음
- RSI가 타임프레임(일간 vs 시간/분봉)에 따라 60대(중립)~80(과매수)
  으로 다름 — 이는 다른 이전 배당주들의 "소스 간 불일치"와 달리
  "같은 지표의 시간축 차이"라는 다른 유형의 데이터 특성
- 실시간 최신 시세가 아니라 검색 시점(2026-08-16) 기준 가장 최근
  보도 스냅샷
