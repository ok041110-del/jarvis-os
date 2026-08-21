# Raw Data — PG (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-14)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

Dividend Stock Dogfooding 3번째 실행 대상으로 Procter & Gamble(PG)을
선정했다 — `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` §7이
요구한 반복 Evidence 확보를 위해, JNJ(헬스케어/제약)·KO(음료)와 또 다른
산업(생활용품/필수소비재)의 배당주다. 70년 연속 배당 증액(Dividend
King)을 기록한 실제 배당주다. JNJ/KO와 동일하게 Stock Team의 5개 분석에
"Dividend Quality"와 "Valuation"을 추가해 7개 분석으로 구성한다.

## [FUNDAMENTAL] 최근 실적 (FY2026 Q4, 2026-07-29 발표)

- FY2026(2026-06-30 종료) 연간 순매출 $87.0B(+3%), 유기적 매출 성장
  +1%. GAAP 희석 EPS $6.62(+2%), Core EPS $6.89(+1%)
- Q4 FY2026 순매출 $21.2B(+2%), GAAP 희석 EPS $1.26(**-15%**, YoY
  큰 폭 하락), Core EPS $1.43(-3%)
- FY2027 가이던스: 매출(all-in/유기적 모두) +1~3%, Core EPS 성장
  0~3%(FY2026 Core EPS $6.89 대비, $6.89~$7.11 범위)
- 주요 역풍: FY2027 원자재/에너지/운송비 세후 비용 부담 약 $1B 예상.
  FY2027 1분기 EPS가 전년 대비 5% 이상 감소할 수 있다고 자료가 명시
- Q4 GAAP EPS -15%와 연간 GAAP EPS +2%가 동시에 보도됨 — 두 수치의
  방향이 반대(연간은 성장, 최근 분기는 급락)라는 점을 자료가 명시적
  으로 구분하지 않은 채 병기하고 있음

출처: theglobedandmail.com, Yahoo Finance, gurufocus.com,
stocktitan.net(8-K), pginvestor.com(IR), cnbc.com (2026-07~08)

## [DIVIDEND_QUALITY] 배당 지속가능성/성장/지급여력

- **1890년 이래 136년 연속 배당 지급, 1956년 이래 70년 연속 배당
  증액** — Dividend King 지위(다른 배당주 자료들과 달리 이번 자료는
  "지급 연속"과 "증액 연속" 두 수치를 모두 명시적으로 구분해 제공)
- 연간 배당 $4.35/주(다른 소스는 $4.36/주로 근소하게 다르게 보도).
  최근 배당 $1.09/주, 배당락일 2026-07-24, 지급일 2026-08-17
- **배당성향(Payout Ratio) 63.77%** — JNJ(46.19%)보다는 높고
  KO(77.24~80.1%)보다는 낮은, 세 종목 중 중간 수준
- 배당수익률 약 3.02%(연간 배당 $4.36/주 기준)
- 최근 10년간 배당 연평균 성장률(CAGR) 5% — KO(3~5%)와 비슷한 구간,
  JNJ(자료상 별도 CAGR 수치 없음)와는 직접 비교 불가
- 이 자료에는 FCF 커버리지 비율이 명시되어 있지 않다(JNJ/KO와 동일한
  공백 반복). 다만 Q4 GAAP EPS가 -15% 급락한 시점의 배당성향 63.77%
  라는 점에서, 이 수치가 연간 기준인지 최근 분기 기준인지 자료가
  명확히 구분하지 않고 있다는 점을 추가로 기록해 둔다.
- 지급 주기: 분기별

출처: MacroTrends(70년 배당 이력), fullratio.com, Koyfin,
stockanalysis.com, SEC 10-K(FY2026), dividendhistory.org (2026)

## [VALUATION] 밸류에이션

- P/E(TTM) 21.66배(한 소스), Forward P/E는 소스별로 25.4배/21.1배로
  **크게 다르게** 보도됨(같은 지표인지, 산정 기준이 다른지 자료가
  설명하지 않음)
- 피어 비교(Forward P/E): Unilever 17.3배, Colgate-Palmolive
  25.9배(다른 소스는 Colgate-Palmolive 22.1배, Kimberly-Clark
  17.7배로 또 다르게 보도) — Colgate-Palmolive 수치 자체가 소스 간
  25.9배/22.1배로 불일치
  - 자료 원문 그대로: "PG's forward P/E of 21.1x is slightly above
    the peer average of 20.5x"라는 서술과, 앞의 "25.4배 vs Unilever
    17.3배" 서술이 PG 자체의 Forward P/E 수치부터 서로 다름(21.1배
    vs 25.4배) — Valuation 분석이 이 내부 불일치를 반드시 지적해야 함
- Price-to-FCF: PG 29.0배 vs Unilever 16.9배
- 프리미엄 근거로 영업이익률 우위(PG ~24%, 다른 소스는 26.3%로 약간
  다르게 보도 vs Unilever ~17%)가 거론됨 — KO 자료의 "매출총이익률
  61.9%" 근거와 같은 유형(정성적 정당화, 프리미엄 크기 계산 근거는
  없음)
- **이번 자료에도 DCF 내재가치 추정치가 없다** — JNJ 이후 KO·PG
  2연속으로 DCF 공백이 반복됨(JNJ만 예외적으로 DCF 추정치 보유)

출처: tradingview.com(gurufocus 인용), kavout.com, wisesheets.io,
Yahoo Finance, simplywall.st (2026)

## [TECHNICAL] 주가/기술적 지표 (2026-08 기준)

- 2026-08-03 종가 $144.49 — SMA20($148.06), SMA50($147.33) **모두
  하회**(약세 구조, JNJ·KO의 "이동평균 전부 상회"와 정반대 패턴)
- RSI(일간) 42.4 — 중립 구간("과매도로 반등을 시사할 만큼 낮지도,
  상승을 확인할 만큼 강하지도 않다"고 자료가 직접 서술)
- 종합 신호: Neutral(매수 신호 2개, 매도 신호 2개로 균형) — JNJ·KO의
  "Strong Buy(12 매수/0 매도)"와 뚜렷이 다른 패턴
- 지지선 $138, 저항선 $150으로 보도됨 — JNJ/KO 자료에는 없던 명시적
  지지/저항 수치가 이번에는 제공됨
- 이 자료에는 현재가($144.49)가 실제로 명시되어 있어, KO 자료에서
  Synthesis가 "현재가가 없어 이동평균을 해석할 수 없다"고 지적했던
  공백이 이번에는 없음 — 3회 중 처음으로 현재가 포함

출처: financhill.com, investing.com, barchart.com, journalarta.com,
investtech.com (2026-08-03)

## [INDUSTRY] 산업/경쟁 구도

- 시가총액 약 $357B(2026년 가정용품 부문 1위로 보도), 연매출
  $85.26B(다른 소스는 $87.0B로 보도 — Fundamental 섹션의 FY 매출과
  약간 다름, 회계연도 기준 차이로 추정되나 자료가 설명하지 않음)
- 매출총이익률 51.2%, 영업이익률 26.3%(Valuation 섹션의 24% 서술과
  약간 다름 — 소스 간 산정 시점/기준 차이로 추정)
- YoY 매출 성장 +1.5%(다른 소스 서술)
- 주요 경쟁사: Unilever, Johnson & Johnson(JNJ), Nestlé,
  Colgate-Palmolive, Kimberly-Clark, Reckitt Benckiser, Henkel
- Unilever가 개인관리·가정용품 부문 글로벌 점유율에서 강세로 보도되나
  구체적 점유율 수치는 자료에 없음(정성적 서술만 존재)
- "Church & Dwight, Kimberly-Clark, Colgate-Palmolive와 일부 영역에서
  경쟁하나, PG의 규모·브랜드력·혁신 파이프라인이 차별점"이라는 정성적
  서술 존재, 구체적 시장점유율 수치는 없음

출처: businessmodelanalyst.com, csimarket.com, hudson-labs.com,
pitchgrade.com (2026)

## [NEWS/EVENT] 최근 이벤트 (2025 하반기~2026)

- **대규모 구조조정**: 비제조 인력의 약 15%(약 7,000명) 감원을 포함한
  2년 구조조정 프로그램 진행 중. 2026-06 기준 1년 경과 시점에
  3,500명 이상 이미 감원 완료로 보도
- 포트폴리오 재평가, 공급망 재구조화, 조직 슬림화를 포함하는 광범위한
  구조조정으로 보도됨. 세전 비경상 비용 $1.0B~$1.6B 예상
- **관세 영향**: FY2026 기준 세전 관세 역풍 약 $600M으로 예상됐으나,
  다른 보도는 "트럼프 시대 관세로 세전 $1B 타격"으로 다르게 보도 —
  두 수치($600M vs $1B) 자체가 불일치
- 관세 비용 상쇄를 위해 2026-08부터 미국 제품의 25%에 중간 한 자릿수
  가격 인상 시행
- CEO 교체: 2026-01-01부로 Shailesh Jejurikar가 신임 CEO로 취임(보도
  시점 기준)
- 이 자료에는 구조조정 비용·관세 비용이 앞서 [FUNDAMENTAL] 섹션의
  FY2027 가이던스($6.89~$7.11 Core EPS)에 이미 반영된 것인지, 별도
  추가 부담인지에 대한 연결 정보가 없음

출처: cnbc.com, simplywall.st, mirrorreview.com, Yahoo Finance,
legis1.com, popsmokemedia.com, benzinga.com (2025-06~2026-07)

## [SENTIMENT] 애널리스트 컨센서스 (2026 기준)

- S&P Global 25개 기관 집계: 종합 등급 "Buy", 평균 목표주가 $163.3
- 다른 소스(33개 기관): 중위값 목표주가 $166.50
- 또 다른 소스(25개 기관): 평균 목표주가 $178.63 — 위 두 수치와
  자릿수부터 다르게 나타남(같은 "25개 기관" 표본이라고 서술하는
  소스가 두 개인데 평균값이 $163.3과 $178.63로 상이 — 표본이 실제로
  다른지, 집계 오류인지 자료가 설명하지 않음)
- 목표주가 범위: 최저 $145(-0.85%), 최고 $186(+27.19%)
- 평균 1년 전망 상승여력 +11.67%
- 종합 컨센서스는 "Buy" 우세로 일관되나, 목표주가 절대값 자체는
  $163.3~$178.63까지 소스 간 상당한 편차가 있음(JNJ $210/$238,
  KO $80.83/$95.40에 이어 3연속으로 목표주가 소스 간 불일치가 반복)

출처: stockanalysis.com, tickernerd.com, Yahoo Finance,
marketscreener.com, chartmill.com, marketbeat.com, benzinga.com (2026)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 PG 10-K/실적 발표 전문, SEC 제출 서류 전체를
  직접 대조 검증하지 않음
- Forward P/E 자체가 소스에 따라 21.1배/25.4배로 크게 다르게 보도됨 —
  Colgate-Palmolive 피어 수치도 22.1배/25.9배로 이중 불일치
- 매출 수치가 섹션 간(Fundamental $87.0B vs Industry $85.26B) 약간
  다르게 보도됨 — 회계연도 기준 차이 가능성이 있으나 자료에 명시 없음
- 관세 비용 추정이 $600M/$1B로 소스 간 불일치
- 목표주가 평균값이 $163.3/$178.63로 같은 기관 수(25개)를 인용하면서도
  크게 다르게 보도됨 — 원인 불명
- 구조조정·관세 비용이 FY2027 가이던스에 이미 반영됐는지 불명
- FCF 기준 배당 커버리지 비율 없음(JNJ/KO와 동일한 공백)
- 이번 자료에도 DCF 기반 내재가치 추정치가 없음(JNJ 이후 2연속 공백)
- 실시간 최신 시세가 아니라 검색 시점(2026-08-14) 기준 가장 최근 보도
  스냅샷(단, Technical 섹션의 종가 자체는 2026-08-03 기준으로, 다른
  섹션의 보도 시점과 최대 약 11일의 시차가 있을 수 있음)
