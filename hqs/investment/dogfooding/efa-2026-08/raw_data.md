# Raw Data — iShares MSCI EAFE ETF (EFA) (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-17)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로, 여기 적힌 것 외의 데이터는
Engine이 알 수 없다.

이 실행의 목적은 EFA 분석 자체가 아니라 **Investment HQ MVP(`investment-hq/
run.py`)의 최소 E2E 경로가 실제로 동작하는지 검증**하는 것이다. 대상은
기존 18건 Dogfooding(Stock 5·ETF 6·Dividend Stock 7)과 겹치지 않는
**국제 선진국 주식 ETF(EFA)** — 기존 ETF 6건(QQQ/SCHD/AGG/GLD/VNQ/UUP)
이 전부 미국 시장/자산이었던 것과 달리, 처음으로 미국 외 지역(일본/
유럽) 주식에 노출되는 펀드다. ETF Team의 6개 역할은 변경 없이 그대로
재사용한다.

## [COMPOSITION] 추적 지수/구성 방법론

- MSCI EAFE Index(선진국 대형/중형주, 미국·캐나다 제외)를 추종
- **대표추출법(representative sampling)**으로 지수를 추종 — 완전
  복제(full replication)가 아님
- 자산의 최소 80%를 지수 구성종목 또는 경제적으로 실질적으로 동일한
  투자자산에 투자
- 보유 종목 수 700개, 성장주/가치주 혼합, 다양한 시가총액 구성

출처: [iShares MSCI EAFE ETF | EFA — iShares](https://www.ishares.com/us/products/239623/ishares-msci-eafe-etf),
[EFA Fact Sheet — iShares](https://www.ishares.com/us/literature/fact-sheet/efa-ishares-msci-eafe-etf-fund-fact-sheet-en-us.pdf)
(2026-06-30 기준)

## [HOLDINGS_EXPOSURE] 보유종목/노출 구조

- 국가 비중: 일본 약 24%, 영국 15%, 프랑스 9%, 스위스 9%, 독일이
  상위 5개국에 포함
- 상위 보유종목: ASML Holding 3.22%, HSBC Holdings 1.62%, Roche
  Holding AG 1.39%, Novartis AG 1.32%, AstraZeneca 1.18%
- 섹터 배분 상세 수치는 자료에 없음 — "섹터/종목 집중도를 최소화하되
  일본·영국·프랑스·독일에 무겁게 편중"이라는 정성적 서술만 존재
- **700개 종목 분산에도 불구하고 상위 5개국이 60%를 넘는 지리적
  집중**이 있음 — 이 자료는 "분산"과 "지리적 집중"이라는 두 서술을
  모두 담고 있으나 둘의 관계를 직접 설명하지 않음

출처: [EFA Holdings List — stockanalysis.com](https://stockanalysis.com/etf/efa/holdings/),
[One Low-Cost ETF For Europe, Japan — 247wallst.com](https://247wallst.com/investing/2026/05/17/one-low-cost-etf-for-europe-japan-and-a-lot-of-stocks-americans-ignore/)
(2026)

## [COST_TRACKING] 비용/추적

- 총보수율(Expense Ratio) 0.32%
- **경쟁 펀드(Vanguard VEA)가 동일한 지수를 더 낮은 보수율로, 일반적
  으로 더 낮은 추적오차로 복제한다**고 명시적으로 비교됨 — EFA
  자체의 추적오차 수치는 이 자료에 없음(경쟁사 대비 상대적으로만
  언급됨)
- 대표추출법 사용이 완전복제 대비 추적오차의 잠재 원인일 수 있으나,
  이 자료가 그 인과관계를 직접 명시하지는 않음

출처: [iShares MSCI EAFE ETF | EFA — iShares](https://www.ishares.com/us/products/239623/ishares-msci-eafe-etf),
[EFA - iShares MSCI EAFE ETF — etfdb.com](https://etfdb.com/etf/EFA/)
(2026)

## [PERFORMANCE_RISK] 성과/리스크

- 최근 1년 총수익률 20.06%(배당 포함)
- 설정 이후(2001년~) 연평균 수익률 6.55%, 다른 소스는 "2001-08-17~
  2026-08-14 기준 연복리 6.649%, 누적 396.995%"로 약간 다른 수치
  제시
- 연환산 표준편차(변동성) 20.8%(2026-08-14 기준)
- **설정 이후 최대낙폭(Max Drawdown) 61.0%** — 상당히 큰 낙폭
- Morningstar Silver 등급(2026-07-31 기준, Foreign Large Blend
  카테고리 645개 펀드 대비 위험조정수익률 기준)
- **통화/환율 리스크가 이 펀드의 핵심 리스크 요인**(미국 외 자산,
  현지통화 노출)이나, 이 자료는 환헤지 여부나 구체적 환율 민감도
  수치를 제공하지 않음

출처: [EFA iShares MSCI EAFE ETF Quote — MyPlanIQ](https://www.myplaniq.com/invest/quote/EFA/),
[EFA ETF Stock Price & Overview — stockanalysis.com](https://stockanalysis.com/etf/efa/)
(2026-08)

## [DISTRIBUTION] 분배금

- **배당수익률(TTM) 3.36%** — 다른 소스는 "2.75%"로 다르게 보도,
  **두 수치 간 약 0.6%p 차이**가 있고 자료는 원인(산정 시점/방식
  차이)을 설명하지 않음
- 지급 주기: **반기(semiannual)** — 기존 ETF Team 실행에서 분기
  (QQQ/SCHD/AGG/VNQ)·연 1회(GLD는 무배당)·월 1회(UUP는 K-1 파트너십)
  와 또 다른 패턴

출처: [ISHARES MSCI EAFE ETF (EFA) Dividend History — stockinvest.us](https://stockinvest.us/dividends/EFA),
[EFA: Dividend Date & History — Dividend.com](https://www.dividend.com/etfs/efa-ishares-msci-eafe-etf/)
(2026)

## [MACRO] 거시경제/시장 환경

- 2026-08-05 기준 주간 장기 뮤추얼펀드+ETF 순유입 $27.28B, 그 중
  ETF 부문 순발행(순유입에 해당) $43.70B, 뮤추얼펀드는 순유출
  $16.42B — 다만 이는 전체 장기펀드 시장 통계이며 EFA 개별 자금
  흐름 수치는 이 자료에 없음
- EFA 고유의 유럽/일본 거시경제 전망(금리, 성장률 등)에 대한 구체적
  수치는 이번 검색에서 확보되지 않음 — 이 공백 자체를 데이터 한계로
  기록

출처: [Release: Combined Estimated Long-Term Flows and ETF Net Issuance — ICI](https://www.ici.org/research/stats/combined_flows),
[iShares MSCI EAFE ETF (EFA) News Flow — moomoo](https://www.moomoo.com/etfs/EFA-US/news)
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 EFA 공식 Fact Sheet(2026-06-30) 전문,
  MSCI EAFE Index 방법론 문서를 직접 대조 검증하지 않음
- 배당수익률이 3.36%/2.75%로 소스 간 약 0.6%p 차이
- 평균 연수익률이 6.55%/6.649%로 소스 간 소폭 차이(연산 기준일 차이로
  추정되나 불명확)
- EFA 자체의 정확한 추적오차 수치가 없음(경쟁 펀드 VEA와의 상대
  비교만 존재)
- 섹터 배분 상세 수치 없음(국가 비중만 존재)
- 환헤지 여부, 구체적 환율 민감도 수치 없음
- EFA 고유의 자금 유출입 수치, 유럽/일본 거시경제 전망 수치 없음
  (전체 시장 통계만 존재)
- 실시간 최신 시세가 아니라 검색 시점(2026-08-17) 기준 가장 최근
  보도 스냅샷
