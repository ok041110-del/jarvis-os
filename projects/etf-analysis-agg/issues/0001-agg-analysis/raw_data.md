# Raw Data — AGG (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-13)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

세 번째 ETF Dogfooding 대상으로 iShares Core U.S. Aggregate Bond ETF
(AGG, Bloomberg US Aggregate Bond Index 추적)를 선정했다 — QQQ(기술
성장주 주식형)·SCHD(배당 가치주 주식형)와 달리 **채권형 ETF**로 자산군
자체가 다르다. 이번 실행은 사용자 지시에 따라 QQQ/SCHD의 7개 분석
축을 6개로 재구성한다: Composition/Index, Holdings·Exposure(통합),
Cost·Tracking(통합), Performance·Risk(통합), Distribution, Macro.

## [COMPOSITION] 구성/추적지수

- 추적 지수: Bloomberg U.S. Aggregate Bond Index — 미국 투자등급
  채권시장 전체를 대표하는 지수
- 운용 방식: 전체 지수 편입 채권을 다 담지 않고 **표본추출(Sampling)
  전략**을 사용한다 — 유동성이 낮은 채권을 피하기 위한 방식이나, 이
  방식 자체가 추적오차를 유발할 수 있다고 자료가 명시함(주식형 QQQ/
  SCHD의 완전복제 방식과 다른 구조)
- 총 보유 채권 수: 13,224개(2026-06-30 기준), 순자산(AUM)
  $138,847.46백만
- 유사 상품(BND, LAG 등)이 같은 벤치마크를 추종하되 더 낮은 보수율을
  제시한다는 언급 있음(구체적 비교 수치는 자료에 없음)

출처: iShares Fact Sheet(2026-06-30), etfdb.com, mutualfunds.com (2026)

## [HOLDINGS_EXPOSURE] 보유종목/섹터·신용등급·만기 노출

- 섹터 구성: Treasury(국채) 46.26%, MBS Pass-Through(모기지담보부증권)
  23.43%, Industrial(산업 회사채) 14.28%, Financial Institutions(금융
  회사채) 7.90%, Utility(유틸리티) 2.53%, CMBS(상업용 모기지담보부증권)
  1.39%, 기타 소규모 배분
- 국채+정부기관 MBS 합산 약 70% — 나머지 30%는 회사채·비회사 신용·
  지방채 등에 분산
- 신용등급 구성: AAA 2.21%, AA 73.60%, A 11.85%, BBB 11.63%, BB 이하
  없음 — 투자등급 채권에 집중된 보수적 프로필
- 만기 구성: 7~10년 23.23%(최대 비중), 3~5년 21.11%, 5~7년 13.93%,
  1~2년 11.98%
- QQQ의 "상위 10개 종목 47.3%" 같은 단일 종목 집중도 개념 자체가
  존재하지 않음 — 13,224개 채권에 분산되어 있어 이번 ETF는 "종목
  집중도"가 아니라 "섹터·신용등급·만기 구조"가 실질적인 노출 지표임

출처: iShares Fact Sheet, 247wallst.com, Morningstar(간접 인용) (2026)

## [COST_TRACKING] 비용/추적오차

- 총보수율(Expense Ratio): 0.03% — QQQ(0.18%)·SCHD(0.06%)보다도 낮음
- 추적오차: 구체적 수치는 자료에 없음. 다만 원인 메커니즘에 대한 설명은
  있음 — "표본추출 전략이 유동성 낮은 채권을 회피하지만, 이 방식 자체가
  추적오차로 이어질 수 있다"고 자료가 명시. 이는 QQQ/SCHD의 정성적
  설명(유동성·스프레드, 증권대여 수익)과는 다른 유형의 원인 — 채권
  ETF 고유의 "완전복제 불가능성"이 이유로 제시됨
- 경쟁 상품(BND, LAG) 대비 낮은 보수율이라는 서술은 있으나 구체적
  비교 수치는 없음

출처: ishares.com, cbonds.com, aaii.com (2026-08-10)

## [PERFORMANCE_RISK] 성과/변동성·듀레이션 리스크

- YTD 수익률: -0.47%(소스에 따라 절단 시점 차이로 다소 다를 수 있음)
- 1년 수익률(배당 포함): +2.36%
- 30일 SEC Yield: 4.51%(2026-06-30 기준)
- 만기수익률(Yield to Maturity): 4.38%
- 유효 듀레이션(Effective Duration): 5.80년
- 가중평균만기(Weighted Average Maturity): 8.11년
- 금리 1%p 변동 시 가격이 반대 방향으로 약 5.85% 변동할 수 있다고
  보도됨(듀레이션 기반 추정)
- 3년 표준편차: 5.51%
- 3년 주식 베타(Equity Beta): 0.23 — 주식시장과의 상관관계가 낮음을
  시사
- QQQ(변동성 정성적 서술만 존재)·SCHD(연환산 변동성 11.10%, 베타
  0.56)와 달리, AGG는 **듀레이션이라는 채권 고유의 정량적 금리
  민감도 지표**를 제공함 — 이는 Stock/주식형 ETF 어디에도 없던 지표

출처: stockanalysis.com, ytdreturn.com, portfolioslab.com (2026-08)

## [DISTRIBUTION] 분배금/배당

- 배당수익률: 소스별로 3.85%(2026-08-04 기준)/4.04%(연환산, 연간
  예상 $3.94/주)/4.07%(최근 배당 기준) — 세 수치가 서로 다르게
  보도됨
- 최근 배당: 주당 $0.330(2026-05-06 지급), 다음 배당락일 2026-08-03,
  예상 다음 배당 $0.3307
- **지급 주기: 월간(Monthly)** — QQQ·SCHD(둘 다 분기 지급)와 다른
  주기. 채권형 ETF 고유의 지급 구조로 보임
- QQQ(0.42%)·SCHD(~3%)·AGG(~4%) 순으로 배당수익률이 가장 높음

출처: financecharts.com, macrotrends.net, stockinvest.us,
marketchameleon.com (2026)

## [MACRO] 시장·거시환경

- 10년물 국채금리: 2026년 3월 이후 대체로 4%~4.5% 범위에서 유지,
  연말까지 4.25%~4.50% 범위로 전망됨(상방 리스크 존재)
- Fed 정책: 동결 유지가 우세하나, 시장 참가자들 사이에서 연내 금리
  인상 가능성이 부각되고 있다고 보도됨 — 이는 SCHD Macro 자료의
  "금리 인하 기대 vs 인상 가능성 혼재" 서술과 방향은 유사하나 시점과
  출처가 다름(교차 검증되지 않음)
- 인플레이션 고착화, 재정 우려, 글로벌 채권금리 상승, 유가 등이 장기
  국채금리에 상방 압력 요인으로 거론됨
- 투자 관점 조언(정성적 보도): "듀레이션을 벤치마크보다 짧게 가져가는
  것이 현재 선호되는 전략"이라는 서술 존재 — 이는 AGG 자체(유효
  듀레이션 5.80년)에 대한 언급이 아니라 채권 투자 전반에 대한 일반론

출처: fidelity.com, nuveen.com, schwab.com, federalreserve.gov,
tradingeconomics.com (2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 iShares 공식 Fact Sheet(PDF) 원문 전체나
  Bloomberg 지수 방법론 문서를 직접 대조 검증하지 않음
- 배당수익률이 3.85%/4.04%/4.07%로 소스마다 다르게 보도됨 — 이
  불일치를 명시하도록 요구함
- 추적오차의 구체적 수치를 찾지 못함(QQQ/SCHD와 동일한 공백)
- YTD 수익률(-0.47%)의 정확한 산정 기준일이 자료에 명시되지 않음
- Macro 섹션의 "인상 가능성 부각" 서술과 SCHD Macro 자료의 서술이
  유사해 보이나 서로 다른 출처·시점이며 교차검증되지 않았음
- 실시간 최신 시세가 아니라 검색 시점(2026-08-13) 기준 가장 최근 보도
  스냅샷이며, Fact Sheet 자체도 2026-06-30 기준으로 다소 시차가 있음
