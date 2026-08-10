# Raw Data — MSFT (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-10)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. AAPL/NVDA와
동일하게 각 섹션에 회사명을 직접 명시한다(AAPL에서 검증된 수정을 재사용).

## [FUNDAMENTAL] Microsoft(MSFT) 최근 실적 (Q4 FY2026, 2026-07-29 발표)

- Q4 FY2026(회계연도 4분기) 매출 $90.01B, 전년동기($76.44B) 대비 +18%, 컨센서스
  ($87.62B) 상회
- GAAP EPS $4.81, Non-GAAP EPS $4.74, 컨센서스(약 $4.24) 큰 폭 상회
- Azure 연환산 매출(run rate)이 $100B 돌파, Q4 Azure 매출 성장률 YoY +43% 이상
- Microsoft Cloud 매출 $59.3B (YoY +27%)
- 부문별: Productivity and Business Processes $37.8B(+14%), Intelligent Cloud
  $39.3B(+32%)
- 실적 발표 후 시간외 거래에서 주가 약 +3% 상승, CFO가 실적콜에서 2026
  캘린더연도 capex 전망 유지를 언급한 이후 상승폭이 최대 +8%까지 확대
- Microsoft 365 Copilot 유료 시트 3천만 개 이상 언급됨

출처: Tickeron, Yahoo Finance, CNBC, TradingKey, Microsoft 공식 IR (2026-07-29)

## [TECHNICAL] MSFT 주가/기술적 지표 (2026-08-07 기준)

- 현재가 $499.86 (2026-08-06 기준, 3개월 신고가 $501.56에 근접)
- RSI 78.1 — **과매수 구간**(70 이상)
- 50일 이동평균 $420.87, 200일 이동평균 $393.27 — 둘 다 현재가 아래(상승 배열,
  Buy 신호)
- 최근 모멘텀: 당일 +2.54%, 5일 +10.81%, 1개월 +30.05% — 단중기 이평선 대비
  현저히 높은 수준(모멘텀이 과열권으로 진입 중이라는 논조)
- 지지선 $381.58, 저항선 $499.86(=현재가 자체가 최근 저항선으로 언급됨)
- 종합 논조: 강한 상승 추세이나 RSI 과매수로 조정 가능성 언급

출처: AltIndex, Investing.com, JournalArta, Barchart, stockinvest.us (2026-08)

## [INDUSTRY] 클라우드 시장/경쟁 구도 (2026, Q1 2026 기준 다수)

- 글로벌 클라우드 인프라 시장 3강: AWS, Azure, Google Cloud(GCP)
- 점유율(소스별 편차): 한 소스는 AWS 31% / Azure 23~25% / GCP 11~12%, 다른
  소스(Synergy Research 인용)는 AWS 28% / Azure 21% / GCP 14%
- Azure 점유율은 "2024년 20% → 2026년 23%"로 성장 중이라는 서술 존재
- 성장률(YoY) 비교: GCP +63%(2026 Q1 기준 가장 빠른 공시 성장률) > Azure +40%
  > AWS +28% — 점유율은 AWS가 가장 크지만 성장률은 GCP가 가장 빠름
- AWS/Azure/GCP 3사 합산 글로벌 클라우드 인프라 시장의 약 68% 차지, 나머지는
  Oracle Cloud/IBM Cloud/Alibaba Cloud 등
- Azure의 경쟁 우위 요인으로 Microsoft 365/Dynamics 365와의 깊은 통합이
  반복적으로 언급됨

출처: LinkedIn(Synergy Research 인용), Programming Helper Tech, CommandLinux,
CloudZero, TechRadar (2026)

## [NEWS/EVENT] 최근 이벤트 (2026-07~08, 규제·Copilot 중심)

- 2026-07-29 Bloomberg: 영국 소비자·반독점 규제당국(CMA)이 Microsoft가 Copilot AI를
  구독 상품에 끼워 넣으며 가격을 인상해 소비자를 오도했는지 조사 중
- FTC가 기존 2년 전부터 진행 중이던 반독점 조사를 클라우드 컴퓨팅, AI, 소프트웨어
  번들링(Entra ID, Copilot 포함)까지 확대, 최소 6개 경쟁사에 질의 — 라이선스 조건,
  상호운용성 장벽, 제품 번들링을 조사 중
- OpenAI와의 전략적 제휴 관련 별도 반독점 소송(집단소송)도 제기됨
- Microsoft Copilot이 소비자용/기업용을 하나의 통합 앱으로 합치는 작업이
  2026년 8월 목표로 진행 중
- **채택률 관련 상반된 신호**: 유료 Copilot 시트가 3천만 개 이상(FUNDAMENTAL
  섹션)이라고 발표됐으나, 별도 보도는 Microsoft 365 시트 4.5억 개 중 유료 AI로
  전환한 비율이 4.5% 미만이라고 지적 — 절대 규모(3천만)와 전환율(4.5% 미만)이
  같은 사안을 다른 각도에서 보도한 것으로 보이나 두 수치가 정확히 어떻게
  연결되는지는 자료에 명시되지 않음
- OpenAI 모델(GPT-5.6 계열)이 Microsoft 365 Copilot 내에서 OpenAI를
  subprocessor로 두고 구동되는 구조로 변경, 관리자 토글이 2026-07-24 자동
  활성화(이미 "No users"로 설정된 경우 제외) — 기존에 AWS/Google Cloud 배포
  애플리케이션이 접근할 수 없던 동일 모델에 대한 구조적 장벽이 사라졌다는 서술

출처: Bloomberg, InfoWorld, TechTimes, ad-hoc-news, tech-insider.org, VaaSBlock
(2026-07~08)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08 기준)

- S&P Global 집계 56개 기관: 컨센서스 "Strong Buy", 평균 목표주가 $563.16
- 별도 소스(약 97개 기관): 대다수 "Strong Buy"/"Buy", 평균 목표주가 $589~592
- 1년 목표주가 범위: 최저 $400(-20.00%) ~ 최고 $870(+74.00%) — 편차가 매우 큼
- 개별 애널리스트: Wedbush(Dan Ives) Outperform, 목표주가 $625; Morgan Stanley
  목표주가 $650으로 상향, "top pick"으로 지칭
- 장기 컨센서스 논조: Azure 성장 재가속과 데이터센터 용량 확장이 이어지면
  밸류에이션 배수가 확장될 것이라는 낙관적 전망

출처: Forbes, stockanalysis.com, ChartMill, primefinancelab.com, Yahoo Finance
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 원문 전체를 검증하지 않음 — 각 Capability 프롬프트에
  "제공된 자료 범위 내에서만 판단하라"는 지시를 포함해야 함
- 클라우드 시장 점유율 수치가 소스마다 다름(AWS 28~31%, Azure 21~25%, GCP
  11~14%) — 이 불일치를 Industry Analysis에서 명시해야 함
- Copilot 채택률과 관련해 "3천만 유료 시트"와 "4.5% 미만 전환율" 두 수치가
  함께 제공되나 모집단이 다를 수 있어(전체 M365 시트 vs Copilot 대상 시트)
  직접 비교가 가능한지 자료만으로 확정할 수 없음
- 목표주가 범위($400~$870)와 평균치가 소스마다 다름(563 vs 589~592) —
  Sentiment Analysis에서 명시해야 함
- 실시간 최신 시세가 아니라 검색 시점 스냅샷(RSI 78.1은 특정 일자 기준)
