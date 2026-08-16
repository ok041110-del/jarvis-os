# Raw Data — Nestlé S.A. (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-16)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

Dividend Stock Team의 **비미국 종목 경계 검증**을 위해 Nestlé S.A.
(스위스, SIX 1차 상장 NESN.SW / ADR NSRGY)를 선정했다 — 16년 연속
배당 증액을 기록한 실제 배당주이며, 기존 Dividend Stock Dogfooding
3사(JNJ/KO/PG, 전부 미국 상장·USD·분기배당)와 대비되는 국가/시장 구조
(스위스 1차 상장, CHF 표시, **연 1회 배당**, 스위스 35% 원천징수세,
ADR 환전 구조)를 가진다. 산업은 소비재(식품/음료)로 KO/PG와 겹치나,
선정 기준은 산업이 아니라 국가/시장 구조 차이다.

## [FUNDAMENTAL] 최근 실적 (H1 2026, 2026-07-23 발표)

- 상반기(H1-26) 매출 CHF 43.1B, 유기적 성장(Organic Growth) +3.6%
  (실질내부성장 RIG +1.5%, 가격 효과 +2.1%). Q2-26 단독 유기적 성장
  +3.7%(RIG +1.8%, 가격 +1.9%)
- 신흥시장(중국 제외) 유기적 성장 +7.1%(RIG +3.9%)로 선진시장(유기적
  성장 +2.3%, RIG +0.6%) 대비 견조
- **순이익 CHF 3.5B — 전년동기(CHF 5.1B) 대비 -31.4%** 급감. 다만
  조정(Underlying) 순이익은 CHF 5.7B로 -2.4%(불변환율 기준 +3.4%)에
  그침 — GAAP 순이익과 조정 순이익 사이 방향성 자체가 다르게 보도됨
  (조정 기준은 개선, GAAP 기준은 급감)
- 2026년 연간 가이던스: 유기적 성장 3~4%로 유지(범위 좁힘), UTOP
  마진 2025년 대비 개선 전망, 잉여현금흐름(FCF) CHF 9B 이상 전망
- 잉여현금흐름 H1 CHF 3.4B(전년동기 CHF 2.3B 대비 개선), 비용절감
  프로그램(Fuel for Growth) 누적 CHF 1.7B(2026년 목표 CHF 2B)
- 이 자료는 순이익 급감(-31.4%)의 구체적 원인(일회성 항목 등)을
  명시하지 않음

출처: [Nestlé H1 2026: Organic growth up but net profit falls 31.4%](https://www.foodnavigator.com/Article/2026/07/23/nestle-h1-2026-organic-growth-up-but-net-profit-falls-314/),
[Half-year results 2026 — Nestlé Global](https://www.nestle.com/media/pressreleases/allpressreleases/half-year-results-2026),
[Nestle SA (NSRGF) H1 2026 Earnings Call Highlights — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/nestle-sa-nsrgf-half-2026-150207317.html)
(2026-07)

## [DIVIDEND_QUALITY] 배당 지속가능성/성장/지급여력 — 비미국 시장 특성 포함

- **16년 연속 배당 증액** — 전년 대비 배당 +4.09% 성장
- 연간 배당 $3.29/주(ADR 기준), 배당수익률 3.32%
- **배당성향(Payout Ratio) 약 86.9%** — JNJ(46.19%)·미국 배당주 대비
  현저히 높은 수준으로 보도됨(구체적 산정 기준의 GAAP/조정 여부는
  자료에 명시되지 않음)
- **지급 주기: 연 1회(Annual)** — JNJ/KO/PG(전부 분기 지급)와 구조적으로
  다름. 다음 배당락일(ADR 기준) 2026-04-20(과거 기록, 참고용)
- **스위스 원천징수세(Withholding Tax) 35%** — 비거주 주주 대상 표준
  세율. 미국 거주자는 ADR 예탁은행(Citibank)과 스위스 과세당국 간
  절차를 통해 우대세율 15%로 조정되나, 이는 자동이 아니라 별도 절차를
  거친다고 보도됨. 조세조약 미체결국 거주자는 이 35% 전액을 원천에서
  차감당할 수 있음
- 배당은 스위스 상장회사 관행상 **주주총회(AGM) 승인**을 거쳐 확정되는
  구조(자료에 일반 원칙으로 언급, Nestlé 개별 AGM 세부 절차는 이
  자료에 없음)
- 이 자료는 배당성향 86.9%의 회계적 근거(일회성 항목, GAAP vs 조정
  이익 중 어느 기준인지)를 명시하지 않음 — Fundamental 섹션의 순이익
  급감(-31.4%)과의 관계도 이 자료에서 직접 연결되지 않음

출처: [Nestle Stock Dividend History — Investing.com](https://www.investing.com/equities/nestle-ag-dividends),
[Nestlé (NSRGY) Dividend History — stockanalysis.com](https://stockanalysis.com/quote/otc/NSRGY/dividend/),
[Swiss dividend withholding tax for US investors explained](https://www.taxesforexpats.com/country-guides/switzerland/how-swiss-dividends-are-taxed-in-the-us.html),
[Nestlé SA Dividend Tax Withholding Tax Recovery](https://globaltaxrecovery.com/nestle/)
(2026)

## [VALUATION] 밸류에이션 — 통화 표시 불일치 포함

- Trailing P/E 28.53, Forward P/E 17.62~17.72(2026-05~07 기준) — 소비재
  업종(Consumer Packaged Goods) 중위 Forward P/E(14.32) 대비 +23.1%
  높은 수준으로 보도됨
- DCF(현금흐름할인) 내재가치 추정이 소스마다 크게 다름: 한 소스는
  공정가치 $113.62(현재가 $77.76 대비 +46.1% 상승여력), 다른 소스는
  $179.01(비교 시장가 $102 대비 +43% 저평가) — **두 소스의 "현재가"
  자체가 $77.76 vs $102로 서로 다르며, 이 차이가 ADR/원주(NESN.SW)
  가격 혼용 또는 산정 시점 차이 중 무엇 때문인지 자료가 설명하지 않음**
- 동종업계 비교: Unilever P/E(TTM) 12.93(10년 중위값 대비 -28%, 가장
  낮음) — Danone P/E(TTM) 22.54(10년 중위값과 유사, 가장 높음) —
  Nestlé Forward P/E 17.62~17.72로 두 경쟁사 사이 중간값
- 이 자료는 Nestlé 자체의 Trailing(28.53)과 Forward(17.62) P/E 사이
  큰 격차의 원인(이익 급감 -31.4% 반영 여부 등)을 명시하지 않음

출처: [NESTLE Forward PE Ratio — GuruFocus](https://www.gurufocus.com/term/forward-pe-ratio/NSRGY),
[NESTLE Intrinsic Value: DCF — GuruFocus](https://www.gurufocus.com/term/iv_dcf/NSRGY/Intrinsic-Value:-DCF-(FCF-Based)/Nestle%20SA),
[NESN DCF Valuation — Alpha Spread](https://www.alphaspread.com/security/six/nesn/dcf-valuation/base-case),
[UNILEVER PE Ratio — GuruFocus](https://www.gurufocus.com/term/pettm/UL),
[DANONE PE Ratio — GuruFocus](https://www.gurufocus.com/term/pettm/DANOY)
(2026)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준) — 통화 표시 혼재

- 현재가(NESN.SW, CHF 표시) 79.06 — 소스에 따라 스위스프랑/USD 혼용
  표시된다고 자료가 명시함
- 5일 이동평균 72.04(매수 신호), 50일 이동평균 71.85(매수 신호),
  200일 이동평균 74.52(매도 신호) — **단기/중기는 매수, 장기는 매도로
  방향이 갈림**(JNJ의 "전 구간 매수 일치"와 대조)
- RSI(14일) 50.830 — 중립
- 종합 기술 신호: 매수 4건, 매도 8건으로 매도 우세 — 이동평균만 따로
  보면 "Sell" 전망
- 지지선 78.99, 저항선 81.65
- 별도 예측성 기사: "2026년 8월 중순까지 약 23% 상승, $71에서 반등해
  $87 목표"라는 서술 존재 — 위 이동평균 기반 매도 신호와 방향이
  상반됨. 자료는 이 두 전망이 왜 다른지 설명하지 않음

출처: [NESN Technical Analysis — Investing.com](https://www.investing.com/equities/nestle-ag-technical),
[NSRGY Stock Price Chart Technical Analysis — Financhill](https://financhill.com/stock-price-chart/nsrgy-technical-analysis),
[NESN.S Technical Analysis — ChartMill](https://www.chartmill.com/stock/quote/NESN.S/technical-analysis)
(2026-08)

## [INDUSTRY] 산업/경쟁 구도

- 시가총액 소스 간 큰 차이: 한 소스는 $258.56B, 다른 소스는 $385B로
  보도(약 1.5배 차이, 원인은 자료에 없음 — 원주/ADR 환산 또는 집계
  시점 차이로 추정되나 확인 불가)
- 연매출 약 $89.88B~$92B(소스 간 소폭 차이)
- 주요 경쟁사: Unilever(연매출 약 $60B로 매출 기준 2위), PepsiCo,
  Coca-Cola, Danone(시가총액 $53B, 2025년 매출 €27.283B), Mondelez,
  Mars — 식품/음료 부문에서 Nestlé가 매출 기준 1위로 보도됨
- 전략적 포트폴리오 재편: 커피(Coffee)·반려동물사료(Petcare)·
  영양(Nutrition)·식품/스낵(Food & Snacks) 4개 핵심 사업에 집중한다고
  신임 CEO가 발표 — Blue Bottle Coffee 매각(중국계 사모펀드
  Centurium Capital 대상) 등 비핵심 자산 정리 진행 중
- 신규 위협: 플랫폼/AI 기반 프리미엄 영양 스타트업이 프리미엄 세그먼트
  점유율 12%를 확보했다는 서술 존재(구체적 브랜드명은 자료에 없음)

출처: [Top 8 Nestlé Competitors — FourWeekMBA](https://fourweekmba.com/nestle-competitors/),
[Nestlé — Market capitalization — companiesmarketcap.com](https://companiesmarketcap.com/nestle/marketcap/),
[Nestlé's 5-point turnaround plan — foodnavigator-usa.com](https://www.foodnavigator-usa.com/Article/2026/04/21/nestle-ceo-unveils-overhaul-strategy/)
(2026)

## [NEWS/EVENT] 최근 이벤트 (2025-10~2026-07)

- **CEO 전격 해임**: 전임 CEO Laurent Freixe가 내부 조사 후 해임됐고,
  회장(Chairman) Paul Bulcke도 조기 퇴진 — Philipp Navratil이 신임
  CEO로 선임됨(해임 사유의 구체적 내용은 이 자료에 없음)
- **대규모 인력 구조조정**: 향후 2년간 전 세계 16,000명 감원 발표
  (화이트칼라 약 12,000명, 제조/공급망 약 4,000명). 목표 비용절감
  규모를 기존 CHF 3.13B에서 CHF 3.76B로 상향
- **Blue Bottle Coffee 매각**: 스페셜티 커피 소매 사업에서 철수하는
  전략의 일환으로 중국계 사모펀드 Centurium Capital에 매각(구체적
  매각가는 비공개로 보도됨)
- 이 자료는 CEO 해임 사유, 16,000명 감원과 Fundamental 섹션의 순이익
  급감(-31.4%) 사이의 직접적 인과관계를 명시하지 않음 — 시점상
  구조조정 발표(2025-10)가 순이익 급감이 보도된 H1-26 실적(2026-07)
  이전이라는 점만 확인됨

출처: [Nestlé to cut 16,000 jobs — Euronews](https://www.euronews.com/2025/10/16/nestle-to-cut-16000-jobs-worldwide-in-major-restructuring-move),
[Nestlé's 5-point turnaround plan — foodnavigator-usa.com](https://www.foodnavigator-usa.com/Article/2026/04/21/nestle-ceo-unveils-overhaul-strategy/),
[Nestlé ramps up restructuring with Blue Bottle Coffee sale — foodingredientsfirst.com](https://www.foodingredientsfirst.com/news/nestle-restructuring-blue-bottle-job-cuts-coffee.html)
(2025-10~2026-07)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- 5개 기관 집계(ADR 기준): 매수 3건, 매도 1건, 보유 1건 — 종합 등급
  "Buy"
- 평균 목표주가 $113.68(범위 $97.00~$127.40) — 현재가 대비 +18.91%
  상승여력 시사
- 다른 소스(같은 조사기관, 2025-08 시점)는 "Hold"(보유) 평균 등급으로
  보도 — 두 소스의 등급 자체가 Buy/Hold로 다름. 시점 차이(2025-08 vs
  2026-08) 또는 조사기관 커버리지 차이 중 무엇이 원인인지 자료가
  설명하지 않음
- Technical 섹션의 저항선($81.65, CHF 표시로 추정)과 Sentiment
  섹션의 목표주가 범위($97~127.4, USD ADR 기준)가 서로 다른 통화
  단위로 보도돼 있어 직접 비교가 어려움 — 이 통화 단위 혼재 자체가
  자료에 명시적으로 정리되어 있지 않음

출처: [Nestle ADR (NSRGY) Stock Forecast — Investing.com](https://www.investing.com/equities/nestle-sa-pk-consensus-estimates),
[Nestlé (NSRGY) Stock Forecast & Price Targets — stockanalysis.com](https://stockanalysis.com/quote/otc/NSRGY/forecast/),
[Nestlé S.A. — Average Recommendation of Hold — MarketBeat](https://www.marketbeat.com/instant-alerts/nestle-sa-otcmktsnsrgy-receives-average-recommendation-of-hold-from-brokerages-2025-08-01)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 Nestlé 반기보고서(Half-year Report) 원문,
  스위스 거래소(SIX) 공시 전체를 직접 대조 검증하지 않음
- **통화 표시가 소스마다 다름**(CHF 원주가 vs USD ADR가) — 이 자료
  자체가 그 혼재를 정리하지 못했으며, Technical/Valuation/Sentiment
  섹션의 가격 수치를 직접 비교하려면 통화 환산이 필요하나 이 자료에는
  환율 정보가 없음
- 시가총액이 $258.56B/$385B로 소스 간 약 1.5배 차이 — 원인 불명
- DCF 공정가치 추정이 소스 간 $113.62/$179.01로 크게 다르고, 기준
  "현재가"도 $77.76/$102로 서로 다름 — 통화/시점 혼재로 추정되나
  확인 불가
- 배당성향(86.9%) 산정 기준(GAAP/조정)과 순이익 -31.4% 급감의 관계가
  자료에 명시되지 않음
- 스위스 원천징수세 35%→15% 우대세율 전환 절차의 세부 사항(자동 여부,
  소요 기간)은 이 자료에 없음
- 실시간 최신 시세가 아니라 검색 시점(2026-08-16) 기준 가장 최근 보도
  스냅샷
