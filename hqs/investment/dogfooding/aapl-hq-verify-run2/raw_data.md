# Raw Data — AAPL (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-10)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

## [FUNDAMENTAL] 최근 실적 (Q3 FY2026, 2026-07-30 발표)

- 매출 $109.4B (YoY +16%), 시장 예상($108.79B) 상회 — June quarter 기록
- Diluted EPS $2.02 (YoY +29%, 이 중 $0.11은 관세 환급분), 컨센서스($1.88) 상회
- iPhone 매출 $54.3B (YoY +22%, June quarter 기록)
- Mac 매출 $10.35B (예상 $8.74B 상회)
- Services 매출 $30.74B (예상 $31.22B **하회**)
- 영업이익 $35.7B (전년동기 $28.2B)
- 다음 분기(9월 분기) 가이던스: 매출 YoY +9~11%, FX 역풍 2.5%p, iPhone/Mac/iPad 공급 제약 영향 반영

출처: MacRumors, CNBC, Yahoo Finance, MacObserver (2026-07-30~08 보도)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- 50일 이동평균 $295.9 > 200일 이동평균 $271.9 (골든크로스, 단기 상승 모멘텀)
- 일부 소스: 5일 이평 $312.61, 50일 이평 $312.33 (Buy 신호)
- RSI(14일): 소스별로 37.7(중립) ~ 53.5(중립) 로 다르게 보고됨 — 과매수/과매도 아님
- 지지선 약 $246.24, 저항선 약 $315.2
- 전반적 기술적 논조: "bullish outlook, with bearish momentum" (혼재된 신호로 보도됨)

출처: Investing.com, Barchart, ChartMill, stockinvest.us (2026-08)

## [INDUSTRY] 스마트폰 시장/경쟁 구도 (2026)

- 글로벌 스마트폰 시장 3강: Samsung, Apple, Xiaomi
- 글로벌 점유율(소스별 편차): Omdia 기준 Samsung 22% / Apple 20%, IDC 기준 Samsung 21.2% / Apple 21.0%, Counterpoint 기준 Apple 21%
- 미국 시장에서는 Apple이 압도적(58.2% vs Samsung 28.4%, 2026-01 기준)
- 프리미엄($600 이상) 세그먼트가 2026 상반기 글로벌 스마트폰 판매의 29% 차지 — Apple은 이 세그먼트에서 강세
- 중국 시장 주요 경쟁자: Huawei, Motorola(Lenovo), Xiaomi, vivo, OPPO

출처: Statista, IDC, Omdia, Counterpoint 인용 기사 (2026)

## [NEWS/EVENT] 최근 이벤트 (2026-06~08)

- WWDC 2026(6월)에서 Siri AI(차세대 Apple Intelligence) 발표, 2026-07 iOS 27 소비자 베타로 출시
- Siri AI: 개인 컨텍스트 이해, 웹 기반 최신 정보 답변, 기기 내 앱/데이터 접근(프라이버시 통제 포함)
- EU/중국은 규제 이슈로 당장 제외
- 2026-08-03 TechCrunch: "Apple finally fixed Siri. So why does it feel anticlimactic?" — 지연 끝에 나온 기능이지만 시장 반응은 미온적이라는 논조
- Q3 실적 발표 후 시간외 거래에서 소폭 하락(Services 매출 예상 하회 영향으로 보도됨)

출처: Apple Newsroom, AppleInsider, TechCrunch, Bloomberg, Variety (2026-06~08)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- S&P Global 집계 46개 기관: 컨센서스 "Buy", 평균 목표주가 $322.82
- 55개 기관 집계(다른 소스): 평균 목표주가 $322.71, 현재가($308.63) 대비 +4.56% 함의
- 1년 목표주가 범위: 최저 $215(-31.38%) ~ 최고 $400(+27.66%) — 편차가 큼
- 최근 3개월간 다음 분기 매출 추정치가 +6.44% 상향 조정됨(긍정적 신호로 보도)

출처: stockanalysis.com, MarketScreener 등 애널리스트 집계 사이트 (2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 원문 전체를 검증하지 않음 — 각 Capability 프롬프트에 "제공된 자료 범위 내에서만 판단하라"는 지시를 포함해야 함(코드 리뷰 Capability의 "unverified import" 패턴과 동일한 정직성 요구)
- RSI 등 일부 수치는 소스 간 불일치가 있음 — 이 불일치 자체를 Technical Analysis 결과에 명시하도록 요구함
- 실시간 최신 시세가 아니라 검색 시점 스냅샷
