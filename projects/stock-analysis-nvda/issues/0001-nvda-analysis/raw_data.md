# Raw Data — NVDA (수집: 이 세션이 WebSearch로 직접 수집, 2026-08-10)

이 문서는 Engine(call_engine)에 전달되는 실제 Context 원본이다. `stock-analysis-aapl`
1차 실행에서 회사/티커명 누락 문제가 발견됐으므로, 여기서는 처음부터 각 섹션에
회사명을 명시한다(재현 방지, `runner.py`의 `_COMPANY_HEADER`와 별개로 원본
데이터 자체에도 포함).

## [FUNDAMENTAL] NVIDIA(NVDA) 최근 실적 (Q1 FY2027, 2026-05-20 발표) 및 Q2 가이던스

- Q1 FY2027(2026-04-26 마감 분기) 매출 $81.6B, 전분기 대비 +20%, 전년동기 대비 +85%
- Data Center 매출 $75.2B (전분기 대비 +21%, 전년동기 대비 +92%) — 사상 최고
- GAAP EPS $2.39, Non-GAAP EPS $1.87
- GAAP 매출총이익률 74.9%, Non-GAAP 매출총이익률 75.0%
- Q2 FY2027 가이던스: 매출 $91.0B ±2%, 매출총이익률 GAAP/Non-GAAP 각 74.9%/75.0% ±50bp
- 가이던스는 **중국向 Data Center 컴퓨트 매출을 전혀 반영하지 않음**(회사 명시)

출처: NVIDIA Newsroom(nvidianews.nvidia.com) 공식 발표, 2026-05-20 보도 기반 요약

## [TECHNICAL] NVDA 주가/기술적 지표 (2026-08 기준)

- 현재가 $223.96
- 50일 이동평균 $210.00, 200일 이동평균 $204.44 — 둘 다 현재가 아래(상승 배열, Buy 신호)
- RSI(14일) 66.686 — Buy 신호 구간이나 과매수(70 이상) 아님
- 이동평균 기반 신호 12개 Buy/0 Sell, 기술 지표 7개 Buy/0 Sell — "Strong Buy" 종합
- 가격 흐름: 2025년 중반 약 120 → 2026년 4월말~5월초 240 부근 고점 → 6월 큰 폭 조정 →
  7월~8월초 좁은 밴드에서 횡보

출처: vantagemarkets.com, AltIndex, Investing.com, Barchart, stockinvest.us (2026-08)

## [INDUSTRY] AI 반도체 시장/경쟁 구도 (2026)

- NVIDIA의 AI 가속기(데이터센터) 시장 점유율: 소스별 70~92%로 편차가 큼(매출 기준
  70~75% 추정이 다수, 일부 소스는 80~90%대 언급)
- AMD는 데이터센터 AI 가속기 시장의 약 6~10% 점유(소스별 편차), MI300X/MI325X가
  NVIDIA 대비 30~40% 낮은 가격에 유사 성능이라는 주장 있음
- 하이퍼스케일러 자체 개발 커스텀 실리콘(Google TPU, AWS Trainium, Microsoft Maia,
  Meta MTIA)이 합산 약 15~20% 차지 — 애널리스트들은 2028~2030년경 이 비중이
  구조적으로 커질 것으로 전망(2030년 약 50%까지 언급되나 이는 예측치)
- NVIDIA의 구조적 우위 요인으로 CUDA 소프트웨어 생태계, NVLink/InfiniBand
  칩투칩 네트워킹이 반복적으로 언급됨(락인 효과)

출처: Medium, companieshistory.com, Hakia, Presenc AI, Silicon Analysts 등 집계
기사 (2026)

## [NEWS/EVENT] 최근 이벤트 (2026-05~08, 중국 수출 규제 중심)

- 2026-05-31 미국 상무부가 "Blackwell Loophole"(중국 본사를 둔 기업이 말레이시아/
  싱가포르/UAE 소재 자회사를 통해 수출 규제를 우회하던 경로)를 막는 가이던스 발표 —
  구매 주체의 최종 모회사가 중국에 있으면 소재지 무관하게 라이선스 요건 적용
- NVIDIA는 이미 명확화된 규정에 맞춰 운영 중이었다고 밝힘
- 2026-07-14 상무부 관계자가 의회에서 H200 칩 대중국 출하량이 "trivial"(승인된
  라이선스 $10B 규모 대비)하다고 증언
- Blackwell 시스템(GB200 NVL72/NVL36, B200)은 중국 및 일부 Country Group(D1/D4/D5,
  이스라엘 제외)에 대해 라이선스 필요 — 2026-08 기준 NVIDIA는 아직 중국向 출하
  라이선스를 받지 못한 상태로 보도됨
- Q2 FY2027 가이던스($91.0B)는 이 중국 매출을 아예 배제하고 산정됨(FUNDAMENTAL
  섹션과 연결되는 사실)

출처: TechTimes, IFP, Al Jazeera, Taipei Times, CNBC, DigiTimes, Supply Chain
Digital (2026-05~08)

## [SENTIMENT] 애널리스트 컨센서스 (2026-08-08 기준)

- S&P Global 집계 61개 기관: 컨센서스 "Strong Buy", 평균 목표주가 $302.83
- 별도 소스(79개 커버 기관, 2026-08-08 기준): 평균 목표주가 $319.48, 현재가
  ($223.96) 대비 +42.7% 상승 여력
- 세부 분포: Buy/Strong Buy 60명, Hold 16명, Sell/Strong Sell 3명
- 1년 목표주가 범위: 최저 $180(-19.63%) ~ 최고 $500(+123.25%) — 편차가 매우 큼
- "평균 1년 예상 주가가 현재가 대비 +35.22% 높다"는 요약도 별도 소스에 존재(위
  +42.7%와 다른 수치 — 집계 시점·모집단 차이로 추정되나 데이터에 명시되지 않음)

출처: stockanalysis.com, VCP Scanner, ChartMill 등 애널리스트 집계 사이트
(2026-08)

## 데이터 한계 (있는 그대로 기록)

- WebSearch 결과 요약이며 원문 전체를 검증하지 않음 — 각 Capability 프롬프트에
  "제공된 자료 범위 내에서만 판단하라"는 지시를 포함해야 함
- AI 반도체 시장 점유율 수치는 소스 간 편차가 AAPL 사례보다 훨씬 큼(70~92%) —
  이 불일치 자체를 Industry Analysis 결과에 명시하도록 요구함
- 목표주가 상승률 수치가 소스마다 다름(+42.7% vs +35.22%) — Sentiment Analysis에서
  명시해야 함
- 실시간 최신 시세가 아니라 검색 시점 스냅샷
