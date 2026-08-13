# Raw Data — SCHD (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-13)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. Engine은
WebFetch/WebSearch가 차단되어 있으므로(`development-hq/mvp/engine.py`
DISALLOWED_TOOLS), 여기 적힌 것 외의 데이터는 Engine이 알 수 없다. 각
Capability 함수는 이 문서에서 자신에게 필요한 섹션만 프롬프트에 포함한다.

두 번째 ETF Dogfooding 대상으로 Schwab U.S. Dividend Equity ETF(SCHD,
Dow Jones U.S. Dividend 100 Index 추적)를 선정했다 — QQQ(기술 성장주
집중, 낮은 배당수익률 0.42%)와 의도적으로 대조되는 배당/가치주 ETF(헬스
케어·필수소비재·에너지 중심, 배당수익률 ~3%)다. QQQ와 상위 보유종목이
거의 겹치지 않아(QQQ 상위: NVIDIA/Apple/Microsoft, SCHD 상위: Abbott/
UnitedHealth/Merck), ETF 업무 구조가 성격이 다른 ETF에서도 반복되는지
검증하기 좋은 대조군이다.

## [COMPOSITION] 구성/추적지수

- 추적 지수: Dow Jones U.S. Dividend 100 Index(S&P Dow Jones Indices
  산출)
- 선정 방법론: Dow Jones U.S. Broad Market Index(약 2,500개 기업)에서
  출발해 4단계 순차 스크리닝 적용. 1단계는 최소 10년 연속 배당 지급
  이력 — 배당을 거른 적이 있거나 이력이 짧은 기업, 무배당 성장주를
  전부 제외
- 매년 3월 과거 10년 배당 이력, 과거 5년 배당 성장률, 현재 재무비율을
  스크리닝. 잉여현금흐름 대비 총부채, 자기자본이익률(ROE), 배당수익률,
  5년 배당성장률 등 지표로 상대 순위를 매겨 재구성
- 2026년 reconstitution(연 1회 구성종목 재편성): 2026-03-23 효력 발생,
  25개 신규 종목 편입·22개 종목 제외. 원자재(에너지) 비중 축소, 헬스케어·
  기술 비중 확대 방향으로 조정됐다고 보도됨

출처: techtimes.com, S&P Global(spglobal.com), topdividendetfs.com,
schdtools.com (2026)

## [HOLDINGS] 보유종목/집중도

- 상위 3개 종목(2026-07 기준): Abbott Laboratories 4.42%(1위),
  UnitedHealth 4.38%(2위), Merck 4.34%(3위)
- 다른 시점(더 이전) 자료: Chevron(CVX) 4.6%, ConocoPhillips(COP) 4.3%,
  Merck(MRK) 4.1% 등이 상위권으로 보도됨 — 2026-03 reconstitution
  전후로 상위 종목 구성 자체가 바뀐 것으로 추정되나, 정확한 변경
  시점과 사유가 자료에 명시적으로 연결되어 있지는 않음
- 상위 10개 종목 합산 비중: 41.61%(다른 소스에서는 "42%"로 반올림
  보도)
- 총 보유종목 수: 103개(2026-07-16 기준)
- 총 운용자산(AUM): $104.31B

출처: tipranks.com, topdividendetfs.com, Yahoo Finance, marketxls.com
(2026-07~08)

## [COST] 비용/추적오차

- 총보수율(Expense Ratio): 0.06%
- 추적오차: 자료에 구체적 수치는 없음. 다만 정성적 설명이 있음 —
  Schwab이 증권대여(securities lending) 프로그램을 운용해 헬스케어·
  반도체 우량주 대여 이자 수익 전액을 펀드 순자산가치(NAV)에 반영,
  이것이 "실질 추적오차를 낮추는 요인"이라고 보도됨(정성적 주장이며
  수치 근거는 제공되지 않음)
- 2026년 3월 reconstitution이 펀드 역사상 가장 큰 종목 교체 규모 중
  하나였다고 보도됨 — 대규모 매매가 발생했다는 사실 자체는 확인되나,
  이것이 실제 추적오차에 미친 정량적 영향은 자료에 없음
- 별도 보도: "0.06%라는 낮은 보수율 이면에, 3월 reconstitution이
  주당 $0.8241의 예상치 못한 분배금(자본이득 등)을 발생시켰다"는
  기사 제목이 존재 — 표면적 비용(보수율)과 별개로 reconstitution
  자체가 실질 비용/세금 효과를 유발할 수 있음을 시사하나, 구체적
  메커니즘은 이 자료만으로는 확인되지 않음

출처: bestetf.net, trackinsight.com, 247wallst.com, investsnips.com
(2026)

## [PERFORMANCE] 성과/변동성

- YTD 수익률(배당 재투자 기준, 2026-08-10 기준): +26.70%
- 1년 수익률(배당 재투자): +31.87%
- 연환산 변동성(Annualized Volatility): 11.10%
- 5년 월간 베타(Beta): 0.56 — 시장 전체 대비 변동성이 낮음을 시사
- 샤프비율(Sharpe Ratio): 2.89
- 별도 보도: "SCHD가 52주 신고가를 기록하며 올해 S&P 500 대비 사상
  최대 격차로 아웃퍼폼했다"는 기사 제목 존재 — 다만 이 "기록적 격차"의
  구체적 수치(몇 %p)는 자료에 명시되지 않음

출처: financecharts.com, portfolioslab.com, techtimes.com (2026-08)

## [SECTOR] 섹터·산업·지역 노출

- 헬스케어+필수소비재(Consumer Staples) 합산: 41.1%(2026-07 기준)
- 에너지: 14.1%
- 정보기술(IT): 9.2%
- 다른 소스 기준: 헬스케어+필수소비재+에너지 합산 55.17% (S&P 500의
  동일 3개 섹터 합산 17.53% 대비 훨씬 높음), 기술 비중 9.23%(S&P 500은
  36.32%) — SCHD가 S&P 500과 정반대의 섹터 프로필(경기방어·가치주
  중심, 기술 저비중)을 가짐을 보여줌
- 2026-03 reconstitution에 따른 섹터 변화: 에너지 비중 약 -8%p 축소,
  헬스케어 +4%p, 기술 +3%p 확대
- 지역 노출: 자료에 명시적 수치 없음("U.S. Dividend" 지수이므로 미국
  상장·미국 기업 중심으로 추정되나 검증 자료 없음)

출처: kavout.com, ts2.tech, seekingalpha.com, topdividendetfs.com (2026)

## [DISTRIBUTION] 분배금/배당

- 배당수익률: 3.06%(연간 배당 $1.05 기준), 다른 소스는 2026-08-11
  기준 forward yield 2.95%로 보도
- TTM(최근 12개월) 배당수익률: 약 3.30%, 최근 5년 배당수익률 범위는
  3.02%~3.85%로 보도됨
- 2026년 2분기 배당: 주당 $0.2525, 배당락일 2026-06-24, 지급일
  2026-06-29
- 다음 배당락일: 2026-09-23(예정)
- 지급 주기: 분기별
- 역사적 맥락: 2011년 설정 당시 분기 배당 $0.05 미만에서 2026-06
  기준 $0.2525로 성장했다고 보도됨(장기 배당성장 트랙레코드를 강조하는
  맥락)
- QQQ(배당수익률 0.42%) 대비 SCHD의 배당수익률(약 3%)이 약 7배 높음 —
  두 ETF의 성격 차이를 보여주는 수치

출처: stockanalysis.com, digrin.com, marketchameleon.com,
schddividend.com (2026)

## [MACRO] 시장·거시환경

- 2026-08-07 시장 상황: 예상보다 부드러운 고용지표(jobs report)가
  나오며 Fed의 추가 금리 인상 우려가 완화, 3대 지수 모두 상승 마감
- 금리 인하 기대 변화: Fed가 2025년 9월말~12월 중순 사이 이미 75bp
  인하(4.5%→3.75%)를 단행했다고 보도됨. Goldman Sachs Asset
  Management는 2026년 중 추가 2회 인하 가능성을 고객에게 안내했다고
  보도
- 다만 동시에 에너지 비용과 인플레이션 지속으로 "금리 인하 기대에서
  금리 인상 가능성 고려로 투자자들의 시각이 옮겨갔다"는 상반된 보도도
  존재 — 인하와 인상 전망이 같은 시기에 혼재해서 보도되고 있음(이는
  QQQ의 Macro 자료에서 나온 2026-06-17 FOMC 동결·매파적 dot plot
  정보와 시점이 다르고 상호 정합성이 검증되지 않음)
- 배당주 관점: 배당/가치주는 금리 인하 국면에서 상대적으로 유리하다는
  일반론이 보도되며, Duke Energy·Realty Income 등 개별 배당주가
  금리 인하 수혜주로 거론됨(SCHD 자체에 대한 언급은 아님)

출처: investing.com, 247wallst.com, blackrock.com (2026-06~08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 Schwab 공식 Fact Sheet 원문이나 S&P Dow
  Jones Indices 방법론 문서 전체를 직접 대조 검증하지 않음
- 보유종목 상위권 수치가 두 시점(이전 vs 2026-07)에서 서로 다른
  종목·비중으로 보도되어 있으나, 정확히 언제 바뀌었는지 자료에 명시적
  연결이 없음 — 이 불일치를 그대로 기록함
- 추적오차의 구체적 수치를 찾지 못함 — 정성적 설명(증권대여 수익)만
  존재
- Macro 섹션은 "금리 인하 기대"와 "금리 인상 가능성 고려로 전환"이라는
  상반된 보도가 공존 — 두 보도의 시점·근거가 자료상 명확히 구분되지
  않음
- 실시간 최신 시세가 아니라 검색 시점(2026-08-13) 기준 가장 최근 보도
  스냅샷
