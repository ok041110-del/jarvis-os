# Raw Data — KO (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-14)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

Dividend Stock Dogfooding 2번째 실행 대상으로 Coca-Cola(KO)를 선정했다 —
`docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` §7이 권고한
"다른 산업의 배당주"(KO/PG 예시) 중 하나이며, 54년 연속 배당 성장
(Dividend King)을 기록한 실제 배당주다. 첫 실행(JNJ, 헬스케어/제약)과
다른 산업(소비재/음료)이다. JNJ와 동일하게 Stock Team의 5개 분석에
"Dividend Quality"와 "Valuation"을 추가해 7개 분석으로 구성한다.

## [FUNDAMENTAL] 최근 실적 (Q2 2026, 2026-07 발표)

- 순영업매출 $13.4B(YoY +7%, 전년 $12.5B) — 유기적 매출 성장 +6%
- 비교 기준 EPS $0.97(YoY +11%)
- 단위 케이스 판매량 +5%(YoY) — 전년 비교 기준 완화, 우호적 날씨,
  FIFA 월드컵 활성화 효과. Trademark Coca-Cola 판매량 +5%(COVID
  회복기 제외 17년 만의 최고 성장률로 보도), POWERADE 글로벌 +8%
- 비교 기준 매출총이익률 120bp 확대(60.5%), 비교 기준 영업이익률
  90bp 확대(31.2%)
- 2026년 가이던스 상향: 유기적 매출 성장 약 5%, 비교 기준(환율중립)
  EPS 성장 7~8%, 비교 기준 EPS 성장 9~10%(2025년 $3.00 대비).
  2026년 환율 영향 순매출 +1p, EPS +3p(우호적). 2026년 잉여현금흐름
  목표 $12.4B

출처: Yahoo Finance(실적 콜 하이라이트), TipRanks, StockTitan(8-K),
ChartMill (2026-07~08)

## [DIVIDEND_QUALITY] 배당 지속가능성/성장/지급여력

- **54년 연속 배당 증액** — Dividend King 지위(다른 소스는 "60년
  이상"으로 보도해 정확한 연속 연수 자체가 소스 간 불일치)
- 연간 배당 $2.12/주, 분기 지급. 다음 배당 지급 예정일 2026-10-01
- 배당수익률 약 2.5%(밸류에이션 섹션 소스 기준)
- **배당성향(Payout Ratio)**: 소스별로 77.24%~80.1%로 보도 — JNJ
  (46.19%)보다 현저히 높은 수준. 80.1%를 "높음"(75% 초과 구간)으로
  분류하는 소스 존재
- 배당 성장률은 최근 3~5% 구간으로 둔화(성숙기 기업 특성으로 서술).
  다만 "인플레이션을 충분히 상회한다"는 서술이 함께 존재
- 이 자료에는 배당 인상 수준을 FCF 전망치에 명시적으로 연동한다는
  서술이 없음(JNJ는 있었음 — 차이점으로 기록)

출처: Koyfin, MacroTrends(54년 배당 이력), Dividend.com, dividendhistory.net,
tikr.com (2026)

## [VALUATION] 밸류에이션

- P/E(TTM, 2026-07-23 기준) 25.45배, Forward P/E 25.61배(다른 소스는
  Forward P/E 24.59배로 약간 다르게 보도)
- Consumer Defensive 섹터 평균(22.53배) 대비 13% 높음
- Forward 12개월 P/E 25.22배 — Zacks Beverages-Soft Drinks 업종 평균
  19.33배, S&P500 평균 20.81배 모두 상회
- 피어 비교: PepsiCo 약 16배, Diageo 약 15배, Keurig Dr Pepper 약
  12배(모두 NTM P/E) — KO(25.6배)가 음료 피어 대비 뚜렷한 프리미엄
- 프리미엄 근거로 LTM 매출총이익률 61.9%, 자본수익률 우위가 거론됨 —
  다만 이는 "프리미엄이 정당화될 수 있다"는 정성적 주장이며, 프리미엄
  자체의 적정 폭을 계산하는 근거는 자료에 없음
- JNJ와 달리 이번 자료에는 DCF 내재가치 추정치가 없어 "이익 배수 vs
  DCF"의 상반된 신호("valuation tug of war")를 재확인할 수 없음 —
  Valuation 분석은 이 자료 공백을 명시해야 함

출처: fullratio.com, gurufocus.com, tikr.com, Yahoo Finance(CA),
stockanalysis.com, simplywall.st, barchart.com (2026-07)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- 일간 RSI 76(과매수 구간)으로 보도한 소스와, 주간 RSI 61.23("healthy"
  구간)으로 보도한 다른 소스가 공존 — 같은 종목에 대해 기간(일간/주간)
  이 다른 RSI 수치를 병기, 직접 비교 불가
- 50일 이동평균 $72, 200일 이동평균 $69.4 — 50일선이 200일선 상회(강세
  구조로 해석)
- 주간 차트 기준 MA-20 $79.12, MA-50 $74.04, MA-200 $65.89 — 이
  수치들은 위 50일($72)/200일($69.4) 수치와 서로 다른 값이며, 두
  소스가 다른 산정 시점 또는 산정 방식을 사용한 것으로 추정되나
  확인 불가(JNJ 자료에서 관찰된 것과 동일한 유형의 소스 간 불일치)
- 이동평균 종합 "Strong Buy"(12개 매수 신호, 0개 매도 신호)
- 종합 기술적 판단: "강세이나 과매수" — 모멘텀 지표는 추가 상승을
  지지하나 단기 오실레이터는 과매수·단기 조정 가능성을 시사. 금주
  예상 거래 범위 $80.00~$86.30으로 보도(구체적 가격대, JNJ 자료에는
  없던 형태의 예측성 수치)

출처: altindex.com, investing.com, tradersunion.com, investtech.com
(2026-08)

## [INDUSTRY] 산업/경쟁 구도

- 시가총액 약 $360B(2026-06-10 기준) — 최대 경쟁사 PepsiCo($211B)를
  크게 상회
- 글로벌 비알코올 음료 시장 점유율: KO 40%대, PepsiCo 약 30%
- 미국 탄산음료(CSD) 시장 점유율: KO 47.1%, PepsiCo 미국 액상음료
  부문 16%(비교 대상 카테고리가 다르게 정의되어 있어 직접 비교에
  주의 필요 — 자료가 이 정의 차이를 명시하지 않음)
- 지역별: 인도에서 KO 계열(Thumbs Up, Sprite 포함) 약 60%, PepsiCo
  30~35%. 유럽 선진시장 탄산음료 부문 KO 45~50%
- 산업 전망: 청량음료 시장이 2026년 $283.8B에서 2031년 $340.8B로
  CAGR 3.7% 성장 전망. 건강 지향 포뮬레이션, 향미 혁신, 프리바이오틱
  탄산음료 등 신규 카테고리 부상이 트렌드로 거론됨

출처: accio.com, companieshistory.com, SEC 8-K(coca-colacompany.com),
thedishbloom.com (2026)

## [NEWS/EVENT] 최근 이벤트 (2026 상반기~하반기)

- **IRS와 $20B 규모 세금 분쟁**: 2007~2009 과세연도 해외 이전가격
  (제조 계열사의 상표·제조법 사용료 산정)을 둘러싼 분쟁. 2026-06-25
  연방 항소법원(마이애미)에서 구두변론 진행 — 미결 상태로 보도
- **집단소송**: Fanta·Sprite의 "100% 천연향료" 표기가 오인 소지가
  있다는 주장으로 집단소송 제기
- 트럼프 행정부의 관세(알루미늄 등 금속 수입 관세 포함)로 인한 시장
  압력이 언급되나, 주가는 이런 압력에도 견조했다고 보도됨
- 이 자료에는 설탕세(sugar tax) 관련 2026년 구체적 진전 정보가 없음
  (검색되지 않음 — 자료 공백으로 명시)
- $20B 세금 분쟁이 실적/현금흐름 가이던스에 어떻게 반영되어 있는지
  (또는 반영되지 않았는지)에 대한 연결 정보가 이 자료에 없음(JNJ의
  탈크 소송-가이던스 연결 공백과 동일한 유형)

출처: gurufocus.com, thestreet.com, Yahoo Finance, foxbusiness.com,
coca-colacompany.com(투자자 뉴스), seekingalpha.com, tipranks.com
(2026)

## [SENTIMENT] 애널리스트 컨센서스 (2026 기준)

- 25개 기관 집계: Strong Buy 19건, Moderate Buy 2건, Hold 4건 —
  종합 등급 "Strong Buy"
- S&P Global 24개 기관 평균 목표주가 $94.7, 등급 "Buy"
- 다른 소스(27개 기관) 중위값 목표주가 $85.00(범위 $71.38~$89.00)
- Barchart 컨센서스 12개월 목표주가 약 $80.83(당시 거래가 대비 약
  +9.9%), 최고 목표주가 $87
- 또 다른 소스는 평균 목표주가 $95.40(현재가 대비 +9.9% 함의),
  Street-high $104(+19.8% 함의)
- 목표주가가 $80.83~$95.40까지 소스 간 약 $15 차이 — JNJ(중위값/평균
  간 약 $28 차이)와 유사한 유형의 목표주가 불일치가 이번에도 반복
  관찰됨

출처: capital.com, Yahoo Finance, tickernerd.com, stockanalysis.com,
marketscreener.com, benzinga.com, marketbeat.com (2026)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 KO 10-Q/실적 발표 전문, SEC 제출 서류 전체를
  직접 대조 검증하지 않음
- 배당 연속 증액 연수 자체가 소스마다 54년/60년 이상으로 다르게 보도됨
- Technical 섹션의 RSI(일간 76 vs 주간 61.23)와 이동평균(50일/200일
  수치 vs MA-20/50/200 수치)이 서로 다른 기간·산정 기준을 쓰는 것으로
  보이나 자료가 이를 설명하지 않음
- 목표주가가 $80.83(Barchart)~$95.40(다른 소스)까지 소스 간 편차가 큼
- $20B IRS 세금 분쟁, 관세 압력이 가이던스에 미치는 구체적 정량 영향은
  자료에 없음
- 이번 자료에는 DCF 기반 내재가치 추정치가 없어(JNJ와 달리), "이익
  배수 vs DCF"의 상반된 신호를 이번 실행에서 재확인할 수 없다는 공백
  자체를 Valuation 분석이 명시해야 함
- 설탕세(sugar tax) 관련 2026년 진전 정보는 검색되지 않음(공백)
- 실시간 최신 시세가 아니라 검색 시점(2026-08-14) 기준 가장 최근 보도
  스냅샷
