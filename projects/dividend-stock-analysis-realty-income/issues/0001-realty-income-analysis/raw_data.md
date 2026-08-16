# Raw Data — Realty Income Corporation (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-16)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

기존 13건 Dogfooding(Stock: AAPL/NVDA/MSFT/JPM, ETF: QQQ/SCHD/AGG/
GLD/VNQ/UUP, Dividend Stock: JNJ/KO/PG/Nestlé/Toyota)과 겹치지 않는
신규 대상으로 **Realty Income Corporation(NYSE: O)**을 선정했다 —
순임대(net lease) REIT 개별 종목으로, **월 배당(월 673회 연속 지급)**,
**FFO/AFFO 기준 밸류에이션**(EPS/P/E가 아님), **리츠 90% 의무배당
구조**라는 이전 5개 배당주(전부 일반 기업, 분기/반기/연 배당)와
구조적으로 다른 특성을 가진다. 이번 실행부터 **신규 표준 실행
패턴**(병렬화+출력최적화+Checkpointing+180초 Timeout, PR #80에서
검증·채택)을 적용한다. Dividend Stock Team의 7개 역할은 지시문
변경 없이 그대로 재사용한다.

## [FUNDAMENTAL] 최근 실적 (Q2 2026, 2026-08-05 발표)

- AFFO(조정 운영자금, REIT의 핵심 실적 지표 — 순이익보다 감가상각
  영향을 제거해 현금창출력을 반영) per share $1.09(YoY +3.8%).
  상반기 누적 AFFO per share $2.22(YoY +5.2%)
- 매출 $1.54B, 컨센서스($1.53B) 상회
- 2026년 AFFO per share 가이던스 상향: $4.44~$4.45(기존
  $4.41~$4.44에서 상향), 중간값 기준 약 +4% 성장
- 투자 목표 상향: $10B(기존 $9.5B에서 상향), 지분 기준 약 $9B 예상
- 2분기 글로벌 투자 약 $2.6B(지분 기준 $2.1B), 초기 가중평균
  현금수익률 7.3%. 산업용 부동산이 전체 투자의 약 65% 차지
- 점유율 98.8%, 임대 회수율(rent recapture) 102.7%(갱신 임대료
  104.6%). 투자등급 임차인 비중 34%(1분기 32%에서 상승)
- 이 자료는 AFFO(REIT 고유 지표)와 순이익(GAAP)의 관계를 별도로
  설명하지 않음 — 다른 배당주(JNJ 등)의 EPS 중심 서술과 구조적으로
  다른 지표 체계를 사용한다는 점 자체가 특징

출처: [Realty Income Q2 Earnings Call Raises 2026 Growth Targets — Yahoo Finance](https://finance.yahoo.com/real-estate/articles/realty-income-q2-earnings-call-175500005.html),
[Realty Income Corp (O) Q2 2026 Earnings Call Highlights — GuruFocus](https://www.gurufocus.com/news/9009561/realty-income-corp-o-q2-2026-earnings-call-highlights-affo-growth-and-strategic-expansion-into-data-centers),
[O Q2 2026 Earnings Call — BigGo Finance](https://finance.biggo.com/news/US_O_2026-08-05)
(2026-08-05)

## [DIVIDEND_QUALITY] 배당 지속가능성/성장/지급여력 — REIT 고유 구조 포함

- **31년 연속 배당 증액**, 1994년 NYSE 상장 이후 135회 배당 인상
- **지급 주기: 월 1회** — 2026년 6월 기준 **673회 연속 월 배당** 지급.
  JNJ/KO/PG(분기)·Nestlé(연 1회)·Toyota(반기)와 전부 다른 네 번째
  지급 주기 패턴
- 최근 월 배당 $0.2710/주로 인상
- **AFFO 기준 배당성향 73%**(2026년 상반기 실측), 2026년 연간
  예상 배당성향 74% — "합리적인 수준"으로 보도됨. **REIT는 세법상
  과세소득의 90% 이상을 배당해야 하는 의무 구조**를 가진다(이
  자료는 Realty Income이 이 최소 요건을 충족하는지 구체적 수치로
  확인해주지 않음 — 73~74%라는 AFFO payout ratio가 세법상 요구되는
  과세소득 기준 90%와 같은 개념인지 자료가 명시적으로 구분하지 않음)
- 연평균 배당 성장률 약 4.2%(1994년 상장 이후 평균)
- 이 자료는 "AFFO 배당성향 73~74%"와 "REIT 세법상 90% 의무배당"이
  서로 다른 분모(AFFO vs 과세소득)를 쓰는 별개의 개념인지, 아니면
  같은 것을 다르게 표현한 것인지 설명하지 않음 — Dividend Quality
  Analyst가 다뤄야 할 자료 자체의 공백

출처: [Realty Income Raised Its 2026 AFFO Guidance — Yahoo Finance](https://finance.yahoo.com/real-estate/articles/realty-income-raised-2026-affo-183001317.html),
[Monthly Dividend Stock In Focus: Realty Income — Sure Dividend](https://www.suredividend.com/monthly-dividend-stock-o/),
[Realty Income Raised Its 2026 AFFO Guidance — The Motley Fool](https://www.fool.com/investing/2026/08/06/realty-income-raised-its-2026-affo-guidance-heres-what-that-means-for-its-52-dividend/)
(2026)

## [VALUATION] 밸류에이션 — REIT 지표(P/FFO) vs 일반 지표(P/E) 불일치

- **Forward P/FFO(주가/운영자금) 13.62배** — 소매 REIT 업종 평균
  16.75배보다 낮고, 자사 3년 중위값 13.24배보다는 약간 높음(업종
  대비 저평가, 자체 역사 대비는 소폭 프리미엄)
- 동종업계 비교(P/FFO): Agree Realty 15.80배, Essential Properties
  Realty Trust 14.22배 — Realty Income이 가장 낮은(저평가) 수준
- **P/E(주가수익비율) 52.2배** — "공정 비율" 36.6배, 미국 소매
  REIT 업종 27.5배, 피어그룹 28.9배 대비 **현저히 높음(고평가로
  보임)**. **이는 P/FFO 기준 결론(저평가)과 정반대 방향** — 자료는
  이 두 지표(P/FFO 저평가 vs P/E 고평가)가 상반된 신호를 내는 이유를
  설명하지 않으며, REIT는 감가상각 때문에 P/E가 구조적으로 왜곡되기
  쉽다는 일반 지식이 있으나 이 자료 자체에는 그 설명이 없음
- 이 자료는 P/FFO와 P/E 중 어느 것이 이 업종에서 더 신뢰할 만한
  지표인지 판단 기준을 제공하지 않음

출처: [Is Realty Income Stock Worth Holding — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/realty-income-stock-worth-holding-152200256.html),
[Realty Income (O) Stock After Dividend Hike — Simply Wall St](https://simplywall.st/stocks/us/real-estate/nyse-o/realty-income/news/realty-income-o-stock-after-dividend-hike-and-higher-affo-gu),
[Assessing Realty Income (O) Valuation — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/assessing-realty-income-o-valuation-041606015.html)
(2026)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- RSI(14일) 약 52 — 중립(과매수·과매도 아님)
- 50일 이동평균 $63.57, 200일 이동평균 $62.83 — 주가가 두 이동평균
  위에서 장기 상승추세 유지 중이라고 보도됨
- 그러나 다른 소스는 이동평균 신호를 매수 6건·매도 6건(중립)으로
  보도하고, 또 다른 소스(일간 기준)는 매수 0건·매도 8건("Sell")
  으로 보도 — **세 소스가 각각 "상승추세 지속" vs "중립" vs "매도
  우세"로 전부 다른 결론**을 냄
- MACD는 양(+0.11)으로 단기 매수 신호
- 지지선 $61.79~$63.78, 저항선 $64~$65 부근
- 이 자료는 세 기술적 신호 소스 간 결론 불일치(상승세/중립/매도)의
  원인(산정 시점, 지표 조합 차이 등)을 설명하지 않음

출처: [Realty Income (O) Stock Analysis — Tickeron](https://tickeron.com/ticker/O/),
[O Technical Analysis, RSI and Moving Averages — Investing.com](https://www.investing.com/equities/realty-income-technical),
[Realty Income Corporation stock Analysis — Cryptonomist](https://en.cryptonomist.ch/2026/08/09/realty-income-corporation-stock-trades-below-key-levels-as-affo-rises-3-8/)
(2026-08)

## [INDUSTRY] 산업/경쟁 구도

- 시가총액 $58.6B — **순임대(net lease) REIT 중 최대 규모**
- 주요 경쟁사: W. P. Carey(시가총액 $15.9B, 산업/창고/소매 자산,
  미국·유럽), NNN REIT(**36년 연속 배당 증액 — Realty Income의
  31년보다 5년 더 김**), Agree Realty, STAG Industrial(산업용
  물류 특화)
- 순임대 REIT 섹터 전체: 시가총액 합계 $124B, 20개 REIT, 평균
  배당수익률 5.32%, Forward FFO 배수 13.5배
- Realty Income 포트폴리오: 가중평균 임대 잔여기간 8.7년, 높은
  다각화·점유율로 현금흐름 예측가능성이 강점으로 보도됨
- 이 자료는 NNN REIT가 배당 증액 연속기록에서 Realty Income을
  앞선다는 사실을 명시하면서도, Realty Income이 "업계 1위"로 자주
  불리는 이유(규모/다각화)와 이 배당 기록 열위가 어떻게 공존하는지
  설명하지 않음

출처: [Forget Realty Income: 4 Other REITs — 247wallst.com](https://247wallst.com/investing/2026/07/26/forget-realty-income-4-other-reits-built-for-dividend-investors/),
[The 7 Largest REIT Stocks in 2026 — Gainify](https://www.gainify.io/blog/reit-stocks),
[Better Dividend Stock: Realty Income vs. NNN REIT — The Motley Fool](https://www.fool.com/investing/2026/03/25/better-dividend-stock-realty-income-vs-nnn-reit/)
(2026)

## [NEWS/EVENT] 최근 이벤트 (2026-06~08)

- **데이터센터 진출**: 2026-06-30, Cloud Capital 및 글로벌 기관투자자와
  파트너십 발표 — 버지니아 북부 데이터센터 포트폴리오에 최대 $1.4B
  투자(45% 지분), 2·3분기 중 약 $700M 초기 투입 예정. 투자등급
  임차인 대상 장기 트리플넷 리스 구조. 기존 소매/산업 중심에서
  자산군 다각화를 시도하는 전략적 이벤트
- **Spirit Realty Capital 인수 완료**: 2023년 10월 발표된 $9.3B
  규모 인수가 2026년까지 완료됨(구체적 완료 시점은 이 자료에 명시
  안 됨)
- **테넌트 부도 리스크**: Dollar General, Seven & i Holdings(7-Eleven
  모회사), Wynn Resorts 등 주요 임차인이 동시다발적으로 부도날 경우
  배당 삭감 압력이 이론적으로 존재하나, "그런 시나리오가 발생할
  가능성은 낮다"고 보도됨(구체적 확률/근거 수치는 자료에 없음)
- 이 자료는 데이터센터 진출($1.4B)이 기존 AFFO 가이던스 상향
  ($4.44~$4.45)에 이미 반영된 것인지 별도 추가 요인인지 명시하지
  않음

출처: [Realty Income (O) Forms Joint Venture for Data Center Investments — GuruFocus](https://www.gurufocus.com/news/8939577/realty-income-o-forms-joint-venture-for-data-center-investments),
[Realty Income to Acquire Spirit Realty Capital — Realty Income IR](https://www.realtyincome.com/investors/press-releases/realty-income-acquire-spirit-realty-capital-93-billion-transaction),
[Prediction: Realty Income's Data Center Pivot — The Motley Fool](https://www.fool.com/investing/2026/07/02/prediction-realty-incomes-data-center-pivot-will-s/)
(2026-06~08)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- **한 소스(24개 기관, S&P Global 집계)**: 종합 등급 **"Hold"**
  (매수 6건, 보유 17건, 매도 0건)
- **다른 소스(23개 기관)**: 평균 등급 **"Buy"** — **두 소스의 종합
  등급 자체가 Hold/Buy로 다름**, 집계 기관 수도 24개/23개로 소폭
  다름
- 평균 목표주가 $67.91(범위 $61.50~$75.00), 현재가 대비 +6.38%
  상승여력. 다른 소스는 목표주가 $68.22(+8.73%)로 근사하지만 약간
  다른 수치
- 이 자료는 "Hold"와 "Buy"라는 종합 등급 자체의 불일치 원인(집계
  방법론, 커버리지 시점 차이 등)을 설명하지 않음

출처: [Realty Income Stock: Analyst Estimates & Ratings — Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/realty-income-stock-analyst-estimates-104323109.html),
[Realty Income (O) Stock Forecast & Analyst Price Targets — stockanalysis.com](https://stockanalysis.com/stocks/o/forecast/),
[O Technical Analysis — Investing.com](https://www.investing.com/equities/realty-income-technical)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 Realty Income 10-Q(2026-06-30), Q2 2026
  Earnings Supplemental 원문을 직접 대조 검증하지 않음
- **P/FFO(13.62배, 저평가 시사)와 P/E(52.2배, 고평가 시사)가 정반대
  결론을 낸다** — 이 자료는 원인을 설명하지 않음(REIT 감가상각 구조
  때문일 가능성이 있으나 자료 자체에는 없음)
- 기술적 신호가 세 소스에서 "상승추세/중립/매도 우세"로 전부 다름
- 애널리스트 종합 등급이 소스에 따라 Hold/Buy로 다름, 목표주가도
  $67.91/$68.22로 소폭 다름
- AFFO 배당성향(73~74%)과 REIT 세법상 90% 의무배당 요건의 관계가
  설명되지 않음
- 데이터센터 신규 투자($1.4B)가 기존 AFFO 가이던스에 반영됐는지
  불명
- NNN REIT가 배당 증액 연속기록(36년)에서 Realty Income(31년)을
  앞서는데도 Realty Income이 업계 최대 규모/1위로 서술되는 맥락이
  자료에서 충분히 연결되지 않음
- 실시간 최신 시세가 아니라 검색 시점(2026-08-16) 기준 가장 최근
  보도 스냅샷
